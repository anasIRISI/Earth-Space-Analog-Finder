import csv, math
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon
from earth_sites.models import CelluleTerrestre

CELL = 1.0   # doit être égal à CELL dans le script Earth Engine

MAPPING = {
    "altitude_moy": "altitude_mean", "pente_moy": "pente_mean",
    "pente_std": "pente_stdDev", "pente_p90": "pente_p90",
    "rugosite_moy": "rugosite_mean", "rugosite_std": "rugosite_stdDev",
    "relief_local": "relief_mean", "albedo_moy": "albedo_mean",
    "albedo_std": "albedo_stdDev", "amplitude_thermique": "amplitude_mean",
    "ati_moy": "ati_mean", "ndvi_moy": "ndvi_mean",
    "aridite": "aridite_mean", "part_valide": "valide_mean",
}

def num(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


class Command(BaseCommand):
    help = "Importe un CSV Earth Engine dans CelluleTerrestre."

    def add_arguments(self, parser):
        parser.add_argument("csv")
        parser.add_argument("--vider-fake", action="store_true")

    def handle(self, *args, **o):
        if o["vider_fake"]:
            CelluleTerrestre.objects.filter(cell_id__startswith="FAKE-").delete()
        n = 0
        with open(o["csv"], encoding="utf-8") as f:
            for row in csv.DictReader(f):
                lon0, lat0 = num(row["lon0"]), num(row["lat0"])
                if lon0 is None or lat0 is None:
                    continue
                vals = {champ: num(row.get(col)) for champ, col in MAPPING.items()}
                # homogénéité : peu de variation de pente et d'albédo = proche de 1
                ps, als = vals["pente_std"], vals["albedo_std"]
                if ps is not None and als is not None:
                    vals["homogeneite"] = max(0.0, min(1.0,
                        1 - (ps / 15 + als / 0.15) / 2))
                lat_c = lat0 + CELL / 2
                surface = (111.32 * CELL) ** 2 * math.cos(math.radians(lat_c))
                CelluleTerrestre.objects.update_or_create(
                    cell_id=f"C_{lon0:.1f}_{lat0:.1f}",
                    defaults=dict(
                        geom=Polygon.from_bbox((lon0, lat0, lon0 + CELL, lat0 + CELL)),
                        surface_km2=surface, **vals),
                )
                n += 1
        self.stdout.write(self.style.SUCCESS(f"{n} cellules importées"))