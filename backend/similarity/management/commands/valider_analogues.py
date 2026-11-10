import numpy as np
from django.contrib.gis.geos import Point, Polygon
from django.core.management.base import BaseCommand

from earth_sites.models import CelluleTerrestre
from geospatial.services.profil import profil_polygone
from similarity.services.scoring import calculer_score, candidats, echelles_terre

# Sites utilisés par des agences ou des équipes comme analogues de Mars (lon, lat).
ANALOGUES = {
    "Atacama (Yungay)": (-69.9, -24.1),
    "Death Valley / Mojave": (-116.9, 36.3),
    "Désert du Namib": (15.2, -24.7),
    "Désert de Lut": (59.0, 30.5),
    "Danakil": (40.3, 14.2),
    "Utah (Hanksville, MDRS)": (-110.8, 38.4),
    "Rio Tinto": (-6.55, 37.7),
    "Islande (Askja)": (-16.7, 65.0),
    "Vallées sèches (Antarctique)": (161.8, -77.5),
    "Cratère Haughton (Arctique)": (-89.7, 75.4),
}


class Command(BaseCommand):
    help = "Classe les analogues connus pour un polygone martien donné."

    def add_arguments(self, p):
        p.add_argument(
            "--bbox",
            nargs=4,
            type=float,
            default=[77.0, 18.0, 77.5, 18.5],
            metavar=("LON_MIN", "LAT_MIN", "LON_MAX", "LAT_MAX"),
        )
        p.add_argument("--objectif", default="rover")

    def handle(self, *a, **o):
        profil = profil_polygone(Polygon.from_bbox(tuple(o["bbox"])))
        self.stdout.write(f"Profil Mars : { {k: v for k, v in profil.items() if v is not None} }")

        echelles = echelles_terre()
        scores = {}
        for c in candidats(profil):
            s, _ = calculer_score(profil, c, o["objectif"], echelles=echelles)
            scores[c.pk] = s

        valeurs = np.array(list(scores.values()))
        if not len(valeurs):
            self.stdout.write("Aucune cellule candidate.")
            return

        self.stdout.write(
            f"\n{len(valeurs)} candidats – score min {valeurs.min():.1f} | médiane "
            f"{np.median(valeurs):.1f} | p90 {np.percentile(valeurs, 90):.1f} | "
            f"max {valeurs.max():.1f}"
        )
        if np.percentile(valeurs, 90) > 90:
            self.stdout.write(
                self.style.WARNING(
                    "p90 > 90 : les scores discriminent peu. Resserrez les plages de "
                    "ProfilMixin.CRITERES."
                )
            )

        ordre = sorted(scores.values(), reverse=True)
        self.stdout.write("\nAnalogues connus :")
        for nom, (lon, lat) in ANALOGUES.items():
            cel = CelluleTerrestre.objects.filter(
                geom__contains=Point(lon, lat, srid=4326)
            ).first()
            if cel is None:
                self.stdout.write(f"  {nom:32s} cellule absente de la base")
                continue
            if cel.pk not in scores:
                self.stdout.write(f"  {nom:32s} {cel.cell_id} : écartée par le pré-filtre")
                continue
            rang = ordre.index(scores[cel.pk]) + 1
            self.stdout.write(
                f"  {nom:32s} {cel.cell_id} : score {scores[cel.pk]:.1f}, "
                f"rang {rang}/{len(ordre)} (top {100 * rang / len(ordre):.0f} %)"
            )