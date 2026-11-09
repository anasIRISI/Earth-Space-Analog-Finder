from pyproj import Geod
from django.contrib.gis.geos import GEOSGeometry

RAYON_MARS_M = 3_396_190
GEOD_MARS = Geod(a=RAYON_MARS_M, b=RAYON_MARS_M)   # sphère de rayon Mars

SURFACE_MIN_KM2 = 50
SURFACE_MAX_KM2 = 50_000


def surface_km2(geom):
    """Surface sur la sphère de Mars (et non avec PostGIS, qui suppose la Terre)."""
    shp = geom.coords[0]
    lons, lats = zip(*[(p[0], p[1]) for p in shp])
    aire, _ = GEOD_MARS.polygon_area_perimeter(lons, lats)
    return abs(aire) / 1e6


class ErreurPolygone(ValueError):
    pass


def valider_polygone(geojson_str, zones_qs):
    """Renvoie (geom, zone_autorisee, surface_km2) ou lève ErreurPolygone."""
    try:
        geom = GEOSGeometry(geojson_str, srid=4326)
    except Exception:
        raise ErreurPolygone("Géométrie illisible.")
    if geom.geom_type != "Polygon":
        raise ErreurPolygone("Un seul polygone est attendu.")
    if not geom.valid:
        raise ErreurPolygone(f"Polygone invalide : {geom.valid_reason}")
    s = surface_km2(geom)
    if s < SURFACE_MIN_KM2:
        raise ErreurPolygone(f"Zone trop petite ({s:.0f} km², minimum {SURFACE_MIN_KM2}).")
    if s > SURFACE_MAX_KM2:
        raise ErreurPolygone(f"Zone trop grande ({s:.0f} km², maximum {SURFACE_MAX_KM2}).")
    zone = zones_qs.filter(geom__contains=geom).first()
    if zone is None:
        raise ErreurPolygone("Le polygone doit être entièrement dans une zone autorisée.")
    return geom, zone, s