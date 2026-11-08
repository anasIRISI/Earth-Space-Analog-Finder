from django.contrib.gis.db import models
from geospatial.models import ProfilMixin


class ZoneMartienneAutorisee(models.Model):
    nom = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    geom = models.PolygonField(srid=4326)  # convention : lon/lat de Mars

    def __str__(self):
        return self.nom


class SelectionZone(ProfilMixin):
    """Polygone dessiné par l'utilisateur, avec son profil calculé."""
    zone_autorisee = models.ForeignKey(ZoneMartienneAutorisee, on_delete=models.PROTECT)
    geom = models.PolygonField(srid=4326)
    surface_km2 = models.FloatField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)