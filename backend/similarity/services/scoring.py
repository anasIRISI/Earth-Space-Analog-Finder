from geospatial.models import ProfilMixin

POIDS = {
    "rover": {"pente_moy": 3, "rugosite_moy": 3, "relief_local": 2, "albedo_moy": 1,
              "ati_moy": 1, "amplitude_thermique": 1, "indice_fer": 0.5},
    "habitat": {"pente_moy": 1, "rugosite_moy": 1, "relief_local": 1, "albedo_moy": 1,
                "ati_moy": 3, "amplitude_thermique": 3, "indice_fer": 1},
    "isru": {"pente_moy": 1, "rugosite_moy": 1, "relief_local": 1, "albedo_moy": 1,
             "ati_moy": 1, "amplitude_thermique": 1, "indice_fer": 3},
}


def score_critere(v_mars, v_terre, plage):
    """Similarité entre 0 et 1 ; None si une des valeurs manque."""
    if v_mars is None or v_terre is None:
        return None
    lo, hi = plage
    return max(0.0, 1.0 - abs(v_mars - v_terre) / (hi - lo))


def calculer_score(profil_mars, cellule, objectif):
    """profil_mars : dict ou objet avec les champs de ProfilMixin.
    Renvoie (score 0-100, détail par critère)."""
    poids = POIDS[objectif]
    somme = total = 0.0
    detail = {}
    for champ, plage in ProfilMixin.CRITERES.items():
        v_mars = profil_mars.get(champ) if isinstance(profil_mars, dict) \
            else getattr(profil_mars, champ, None)
        s = score_critere(v_mars, getattr(cellule, champ), plage)
        if s is None:
            continue                       # critère absent : ignoré, pas pénalisé
        detail[champ] = round(s, 3)
        somme += poids[champ] * s
        total += poids[champ]
    if total == 0:
        return 0.0, detail
    base = somme / total
    bonus = 0.9 + 0.1 * (cellule.homogeneite if cellule.homogeneite is not None else 0.5)
    return round(100 * base * bonus, 1), detail

from earth_sites.models import CelluleTerrestre

def candidats(profil_mars):
    qs = CelluleTerrestre.objects.filter(ndvi_moy__lt=0.25, part_valide__gt=0.7)
    pente = profil_mars.get("pente_moy")
    if pente is not None:
        qs = qs.filter(pente_moy__range=(pente - 10, pente + 10))
    return qs