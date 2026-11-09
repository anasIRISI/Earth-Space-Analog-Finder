from django.test import SimpleTestCase
from types import SimpleNamespace
from geospatial.models import ProfilMixin
from .services.scoring import calculer_score


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

    def test_objectif_change_le_score(self):
        p = {"pente_moy": 10, "ati_moy": 100}
        c = cellule(pente_moy=10, ati_moy=1900)
        s_rover, _ = calculer_score(p, c, "rover")
        s_habitat, _ = calculer_score(p, c, "habitat")
        self.assertGreater(s_rover, s_habitat)