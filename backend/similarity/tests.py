from django.test import SimpleTestCase
from types import SimpleNamespace
from geospatial.models import ProfilMixin
from .services.scoring import calculer_score
from similarity.services.scoring import _echelles_defaut, calculer_score


def cellule(**kw):
    base = {c: None for c in ProfilMixin.CRITERES}
    base.update(kw, homogeneite=1.0)
    return SimpleNamespace(**base)


class ScoringTests(SimpleTestCase):
    def test_profils_identiques(self):
        p = {"pente_moy": 10, "rugosite_moy": 50}
        s, _ = calculer_score(p, cellule(**p), "rover")
        self.assertEqual(s, 100.0)

    def test_profils_tres_differents(self):
        s, _ = calculer_score({"pente_moy": 0}, cellule(pente_moy=35), "rover")
        self.assertLess(s, 10)

    def test_critere_absent_ignore(self):
        s, d = calculer_score({"pente_moy": 10, "albedo_moy": None},
                              cellule(pente_moy=10, albedo_moy=0.3), "rover")
        self.assertNotIn("albedo_moy", d)
        self.assertEqual(s, 100.0)

    from similarity.services.scoring import _echelles_defaut, calculer_score

def test_objectif_change_le_score(self):
    profil_mars = {
        "pente_moy": 3.0,
        "rugosite_moy": 20.0,
        "relief_local": 150.0,
        "albedo_moy": 0.17,
        "ati_moy": 2.5,
        "amplitude_thermique": 30.0,
        "indice_fer": 0.1,
    }
    # Cellule avec des valeurs très proches pour que le score ne soit pas égal à 0.0
    cellule = SimpleNamespace(
        pente_moy=3.5,
        rugosite_moy=22.0,
        relief_local=160.0,
        albedo_moy=0.18,
        ati_moy=4.0,
        amplitude_thermique=15.0,
        indice_fer=0.2,
        homogeneite=0.8,
    )

    echelles = _echelles_defaut()
    s_rover, _ = calculer_score(profil_mars, cellule, "rover", echelles=echelles)
    s_habitat, _ = calculer_score(profil_mars, cellule, "habitat", echelles=echelles)

    self.assertNotEqual(s_rover, s_habitat)