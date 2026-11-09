import numpy as np
import rasterio
from rasterio.mask import mask
from django.conf import settings

# champ du profil -> (fichier raster, statistique)
SOURCES = {
    "pente_moy":           ("mars_pente.tif", "mean"),
    "pente_std":           ("mars_pente.tif", "std"),
    "pente_p90":           ("mars_pente.tif", "p90"),
    "rugosite_moy":        ("mars_rugosite.tif", "mean"),
    "rugosite_std":        ("mars_rugosite.tif", "std"),
    "relief_local":        ("mars_relief.tif", "mean"),
    "altitude_moy":        ("mars_altitude.tif", "mean"),
    "albedo_moy":          ("mars_albedo.tif", "mean"),
    "albedo_std":          ("mars_albedo.tif", "std"),
    "ati_moy":             ("mars_thermique.tif", "mean"),
    "amplitude_thermique": ("mars_amplitude.tif", "mean"),
    "indice_fer":          ("mars_fer.tif", "mean"),
}

STATS = {
    "mean": np.nanmean,
    "std": np.nanstd,
    "p90": lambda a: np.nanpercentile(a, 90),
}


def _valeurs_raster(chemin, geom):
    """Valeurs du raster sous le polygone, sans les nodata. None si impossible."""
    if not chemin.exists():
        return None
    with rasterio.open(chemin) as src:
        try:
            data, _ = mask(src, [geom.geojson_dict()], crop=True, filled=False)
        except ValueError:                        # polygone hors du raster
            return None
        band = data[0]
        valeurs = band.compressed().astype("float64")
    valeurs = valeurs[np.isfinite(valeurs)]
    return valeurs if valeurs.size else None


def profil_polygone(geom):
    """geom : polygone GEOS en lon/lat. Renvoie un dict aux noms de ProfilMixin."""
    import json
    geom_json = json.loads(geom.geojson)
    cache, profil = {}, {}
    for champ, (fichier, stat) in SOURCES.items():
        if fichier not in cache:
            chemin = settings.MARS_RASTER_DIR / fichier
            cache[fichier] = _valeurs_raster_json(chemin, geom_json)
        v = cache[fichier]
        profil[champ] = float(STATS[stat](v)) if v is not None else None
    return profil


def _valeurs_raster_json(chemin, geom_json):
    if not chemin.exists():
        return None
    with rasterio.open(chemin) as src:
        try:
            data, _ = mask(src, [geom_json], crop=True, filled=False, all_touched=True) # mask(src, [geom_json], crop=True, filled=False)
        except ValueError:
            return None
        valeurs = data[0].compressed().astype("float64")
    valeurs = valeurs[np.isfinite(valeurs)]
    return valeurs if valeurs.size else None