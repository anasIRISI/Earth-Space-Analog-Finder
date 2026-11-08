from django.db import models


class ProfilMixin(models.Model):
    """Caractéristiques de surface, identiques pour Mars et la Terre."""
    # Topographie
    pente_moy = models.FloatField(null=True)          # degrés
    pente_std = models.FloatField(null=True)
    pente_p90 = models.FloatField(null=True)
    rugosite_moy = models.FloatField(null=True)       # TRI, mètres
    rugosite_std = models.FloatField(null=True)
    relief_local = models.FloatField(null=True)       # max - min en fenêtre, mètres
    altitude_moy = models.FloatField(null=True)       # mètres
    # Réflectance
    albedo_moy = models.FloatField(null=True)         # 0 à 1
    albedo_std = models.FloatField(null=True)
    # Thermique
    ati_moy = models.FloatField(null=True)            # inertie thermique apparente
    amplitude_thermique = models.FloatField(null=True)  # K, écart jour/nuit
    # Composition
    indice_fer = models.FloatField(null=True)         # oxydes de fer, sans unité

    class Meta:
        abstract = True

    # Les critères utilisés par le score, avec leur plage de normalisation.
    CRITERES = {
        "pente_moy":           (0, 35),
        "rugosite_moy":        (0, 200),
        "relief_local":        (0, 2000),
        "albedo_moy":          (0, 0.5),
        "ati_moy":             (0, 2000),
        "amplitude_thermique": (0, 80),
        "indice_fer":          (0, 1),
    }