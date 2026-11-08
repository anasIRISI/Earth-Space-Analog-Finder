from django.contrib.gis.db import models
from geospatial.models import ProfilMixin


class CelluleTerrestre(ProfilMixin):
    cell_id = models.CharField(max_length=40, unique=True)  # identifiant de la grille
    geom = models.PolygonField(srid=4326, spatial_index=True)
    pays = models.CharField(max_length=80, blank=True)
    surface_km2 = models.FloatField(null=True)
    # Spécifiques à la Terre
    aridite = models.FloatField(null=True)        # indice d'aridité
    homogeneite = models.FloatField(null=True)    # 0 à 1
    part_valide = models.FloatField(null=True)    # fraction de pixels valides
    ndvi_moy = models.FloatField(null=True)       # pour exclure la végétation