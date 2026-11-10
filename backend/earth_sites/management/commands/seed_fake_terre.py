import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon
from earth_sites.models import CelluleTerrestre
from geospatial.models import ProfilMixin


class Command(BaseCommand):
    help = "Génère des cellules terrestres FACTICES pour développer le backend."

    def add_arguments(self, parser):
        parser.add_argument("--n", type=int, default=300)

    def handle(self, *args, **opts):
        random.seed(42)
        CelluleTerrestre.objects.filter(cell_id__startswith="FAKE-").delete()
        cellules = []
        for i in range(opts["n"]):
            lon = random.uniform(-170, 170)
            lat = random.uniform(-55, 60)
            demi = 0.25
            vals = {c: random.uniform(*plage) for c, plage in ProfilMixin.CRITERES.items()}
            cellules.append(CelluleTerrestre(
                cell_id=f"FAKE-{i:05d}",
                geom=Polygon.from_bbox((lon - demi, lat - demi, lon + demi, lat + demi)),
                pays="FICTIF",
                surface_km2=2500,
                aridite=random.uniform(0, 1),
                homogeneite=random.uniform(0.3, 1),
                part_valide=random.uniform(0.8, 1),
                ndvi_moy=random.uniform(0, 0.4),
                **vals,
            ))
        CelluleTerrestre.objects.bulk_create(cellules)
        self.stdout.write(self.style.SUCCESS(f"{len(cellules)} cellules factices créées"))