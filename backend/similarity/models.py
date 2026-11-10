from django.db import models
from earth_sites.models import CelluleTerrestre
from spatial_zones.models import SelectionZone


class Recherche(models.Model):
    class Objectif(models.TextChoices):
        ROVER = "rover", "Mobilité rover"
        HABITAT = "habitat", "Habitat"
        ISRU = "isru", "Ressources (ISRU)"

    selection = models.ForeignKey(SelectionZone, on_delete=models.CASCADE)
    objectif = models.CharField(max_length=20, choices=Objectif.choices)
    cree_le = models.DateTimeField(auto_now_add=True)


class Resultat(models.Model):
    recherche = models.ForeignKey(Recherche, related_name="resultats",
                                  on_delete=models.CASCADE)
    cellule = models.ForeignKey(CelluleTerrestre, on_delete=models.CASCADE)
    rang = models.PositiveIntegerField()
    score_global = models.FloatField()            # 0 à 100
    scores_criteres = models.JSONField()          # {"pente_moy": 0.93, ...}
    justification = models.TextField(blank=True)

    class Meta:
        ordering = ["rang"]