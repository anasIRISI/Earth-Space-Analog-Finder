from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config.views import CapabilitiesView, HealthView, ReadinessView
from similarity.views import ZoneMarsViewSet, RechercheViewSet, ResultatViewSet

# Configuration du routeur DRF
router = DefaultRouter()
router.register("zones-mars", ZoneMarsViewSet, basename="zones-mars")
router.register("recherches", RechercheViewSet, basename="recherches")
router.register("resultats", ResultatViewSet, basename="resultats")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", HealthView.as_view(), name="health"),
    path("api/v1/ready/", ReadinessView.as_view(), name="readiness"),
    path("api/v1/capabilities/", CapabilitiesView.as_view(), name="capabilities"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="swagger-ui"), name="swagger-ui"),
    
    # Intégration des ViewSets sous api/v1/
    path("api/v1/", include(router.urls)),
]