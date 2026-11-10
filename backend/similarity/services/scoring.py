import math
from django.db.models import Q, StdDev
from earth_sites.models import CelluleTerrestre
from geospatial.models import ProfilMixin

POIDS = {
    "rover": {"pente_moy": 3, "rugosite_moy": 3, "relief_local": 2, "albedo_moy": 1,
              "ati_moy": 1, "amplitude_thermique": 1, "indice_fer": 0.5},
    "habitat": {"pente_moy": 1, "rugosite_moy": 1, "relief_local": 1, "albedo_moy": 1,
                "ati_moy": 3, "amplitude_thermique": 3, "indice_fer": 1},
    "isru": {"pente_moy": 1, "rugosite_moy": 1, "relief_local": 1, "albedo_moy": 1,
             "ati_moy": 1, "amplitude_thermique": 1, "indice_fer": 3},
}


def _pool_terre():
    """Cellules terrestres utilisables (NDVI absent accepté : glace, désert)."""
    return CelluleTerrestre.objects.filter(
        Q(ndvi_moy__lt=0.25) | Q(ndvi_moy__isnull=True), part_valide__gt=0.7)


def echelles_terre():
    """Écart-type de chaque critère sur toutes les terres candidates (avec un plancher)."""
    stds = _pool_terre().aggregate(**{c: StdDev(c) for c in ProfilMixin.CRITERES})
    return {c: max(stds.get(c) or 0.0, (hi - lo) / 50)
            for c, (lo, hi) in ProfilMixin.CRITERES.items()}


def _echelles_defaut():
    return {c: (hi - lo) / 4 for c, (lo, hi) in ProfilMixin.CRITERES.items()}


def calculer_score(profil_mars, cellule, objectif, echelles=None):
    """Renvoie (score 0-100, détail par critère entre 0 et 1)."""
    echelles = echelles or _echelles_defaut()
    poids = POIDS[objectif]
    somme = total = 0.0
    detail = {}
    for champ in ProfilMixin.CRITERES:
        v_mars = (profil_mars.get(champ) if isinstance(profil_mars, dict)
                  else getattr(profil_mars, champ, None))
        v_terre = getattr(cellule, champ)
        if v_mars is None or v_terre is None:
            continue                          # critère absent : ignoré, pas pénalisé
        z = (v_mars - v_terre) / echelles[champ]
        detail[champ] = round(math.exp(-0.5 * z * z), 3)
        somme += poids[champ] * z * z
        total += poids[champ]
    if total == 0:
        return 0.0, detail
    base = math.exp(-0.5 * somme / total)
    homog = cellule.homogeneite if cellule.homogeneite is not None else 0.5
    return round(100 * base * (0.9 + 0.1 * homog), 1), detail


def candidats(profil_mars):
    qs = _pool_terre()
    pente = profil_mars.get("pente_moy")
    if pente is not None:
        qs = qs.filter(pente_moy__range=(pente - 10, pente + 10))
    return qs