import logging
import platform

import django
from django.db import DatabaseError, connection
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.serializers import CapabilitiesSerializer, HealthSerializer, ReadinessSerializer

logger = logging.getLogger(__name__)


class PublicDiagnosticView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]


class HealthView(PublicDiagnosticView):
    @extend_schema(responses=HealthSerializer, tags=["Infrastructure"])
    def get(self, request):
        """Vérifie Django sans ouvrir de connexion à la base."""
        return Response({
            "status": "ok",
            "service": "earth-space-analog-finder",
            "phase": 1,
            "python_version": platform.python_version(),
            "django_version": django.get_version(),
        })


class ReadinessView(PublicDiagnosticView):
    @extend_schema(responses={200: ReadinessSerializer, 503: ReadinessSerializer}, tags=["Infrastructure"])
    def get(self, request):
        """Interroge réellement l'extension PostGIS, pas seulement le port TCP."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT PostGIS_Version()")
                postgis_version = cursor.fetchone()[0]
        except DatabaseError:
            logger.warning("PostgreSQL/PostGIS indisponible pendant le diagnostic.")
            return Response({
                "status": "unavailable",
                "database": "postgresql/postgis",
                "postgis_version": None,
                "message": "PostgreSQL ou PostGIS indisponible. Vérifiez Docker Compose et les migrations.",
            }, status=503)
        return Response({
            "status": "ready",
            "database": "postgresql/postgis",
            "postgis_version": postgis_version,
            "message": "Connexion PostgreSQL et extension PostGIS opérationnelles.",
        })


class CapabilitiesView(PublicDiagnosticView):
    @extend_schema(responses=CapabilitiesSerializer, tags=["Infrastructure"])
    def get(self, request):
        return Response({
            "phase": 1,
            "scientific_data_loaded": False,
            "modules": [
                {"name": "infrastructure", "phase": 1, "status": "available"},
                {"name": "spatial_zones", "phase": 2, "status": "planned"},
                {"name": "earth_sites", "phase": 2, "status": "planned"},
                {"name": "geospatial", "phase": 2, "status": "planned"},
                {"name": "similarity", "phase": 3, "status": "planned"},
                {"name": "comparison", "phase": 4, "status": "planned"},
                {"name": "reports", "phase": 5, "status": "planned"},
            ],
        })
