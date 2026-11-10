import json
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from geospatial.services.profil import profil_polygone
from spatial_zones.models import ZoneMartienneAutorisee, SelectionZone
from spatial_zones.services import valider_polygone, ErreurPolygone
from .models import Recherche, Resultat
from .serializers import (RechercheCreateSerializer, RechercheDetailSerializer,
                          ResultatSerializer, ZoneMarsSerializer)
from .services.scoring import calculer_score, candidats   # adaptez si candidats() est ailleurs
from .services.justification import generer_justification
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import action
from reports.services import generer_pdf
from similarity.services.scoring import echelles_terre


class ZoneMarsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ZoneMartienneAutorisee.objects.all()
    serializer_class = ZoneMarsSerializer
    pagination_class = None


class ResultatViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Resultat.objects.select_related("cellule")
    serializer_class = ResultatSerializer


class RechercheViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Recherche.objects.select_related("selection").prefetch_related(
        "resultats__cellule"
    )
    serializer_class = RechercheDetailSerializer

    @extend_schema(
        request=RechercheCreateSerializer,
        responses={201: RechercheDetailSerializer},
    )
    def create(self, request):
        ser = RechercheCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        # 1. Validation du polygone dessiné
        try:
            geom, zone, surface = valider_polygone(
                json.dumps(d["polygone"]), ZoneMartienneAutorisee.objects.all()
            )
        except ErreurPolygone as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Profil de la zone martienne
        profil = profil_polygone(geom)
        if all(v is None for v in profil.values()):
            return Response(
                {"detail": "Aucune donnée raster sous ce polygone."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # 3. Score de chaque cellule candidate (avec pré-calcul des échelles)
        echelles = echelles_terre()
        scores = []
        for cellule in candidats(profil):
            s, detail = calculer_score(profil, cellule, d["objectif"], echelles=echelles)
            scores.append((s, detail, cellule))

        if not scores:
            return Response(
                {"detail": "Aucune cellule terrestre candidate."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        scores.sort(key=lambda t: t[0], reverse=True)

        # 4. Enregistrement du top N
        with transaction.atomic():
            selection = SelectionZone.objects.create(
                zone_autorisee=zone, geom=geom, surface_km2=surface, **profil
            )
            recherche = Recherche.objects.create(selection=selection, objectif=d["objectif"])
            Resultat.objects.bulk_create([
                Resultat(
                    recherche=recherche,
                    cellule=c,
                    rang=i + 1,
                    score_global=s,
                    scores_criteres=detail,
                    justification=generer_justification(profil, c, detail, s),
                )
                for i, (s, detail, c) in enumerate(scores[: d["limite"]])
            ])

        recherche = self.get_queryset().get(pk=recherche.pk)
        return Response(
            RechercheDetailSerializer(recherche).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(responses={200: OpenApiTypes.BINARY})
    @action(detail=True, methods=["get"], url_path="rapport")
    def rapport(self, request, pk=None):
        recherche = self.get_object()
        reponse = HttpResponse(generer_pdf(recherche), content_type="application/pdf")
        reponse["Content-Disposition"] = (
            f'attachment; filename="rapport_analogues_{recherche.pk}.pdf"'
        )
        return reponse
