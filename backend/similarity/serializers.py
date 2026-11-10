import json
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geospatial.models import ProfilMixin
from spatial_zones.models import ZoneMartienneAutorisee
from .models import Recherche, Resultat

CHAMPS_PROFIL = list(ProfilMixin.CRITERES)


class ZoneMarsSerializer(serializers.ModelSerializer):
    geom = serializers.SerializerMethodField()

    class Meta:
        model = ZoneMartienneAutorisee
        fields = ("id", "nom", "description", "geom")

    @extend_schema_field(dict)  # Explicite à drf-spectacular que le GeoJSON est un dict/object
    def get_geom(self, obj):
        return obj.geom.geojson


class RechercheCreateSerializer(serializers.Serializer):
    polygone = serializers.JSONField(help_text="Géométrie GeoJSON de type Polygon (lon, lat)")
    objectif = serializers.ChoiceField(choices=Recherche.Objectif.choices)
    limite = serializers.IntegerField(min_value=1, max_value=50, default=10)


class ResultatSerializer(serializers.ModelSerializer):
    cellule = serializers.SerializerMethodField()

    class Meta:
        model = Resultat
        fields = ("id", "rang", "score_global", "scores_criteres", "justification", "cellule")

    @extend_schema_field(dict)
    def get_cellule(self, obj):
        c = obj.cellule
        centre = c.geom.centroid
        return {
            "id": c.id, "cell_id": c.cell_id, "pays": c.pays,
            "centre": {"lon": centre.x, "lat": centre.y},
            "geometry": json.loads(c.geom.geojson),
            "profil": {k: getattr(c, k) for k in CHAMPS_PROFIL},
            "homogeneite": c.homogeneite, "aridite": c.aridite,
        }


class RechercheDetailSerializer(serializers.ModelSerializer):
    selection = serializers.SerializerMethodField()
    resultats = ResultatSerializer(many=True, read_only=True)

    class Meta:
        model = Recherche
        fields = ("id", "objectif", "cree_le", "selection", "resultats")

    @extend_schema_field(dict)
    def get_selection(self, obj):
        s = obj.selection
        return {
            "id": s.id, "surface_km2": s.surface_km2,
            "geometry": json.loads(s.geom.geojson),
            "profil": {k: getattr(s, k) for k in CHAMPS_PROFIL},
        }