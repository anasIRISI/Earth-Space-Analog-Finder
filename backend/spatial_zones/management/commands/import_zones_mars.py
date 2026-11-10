import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry, Polygon
from spatial_zones.models import ZoneMartienneAutorisee


class Command(BaseCommand):
    help = "Importe les zones de démo de Mars depuis un GeoJSON (propriétés : nom, description)."

    def add_arguments(self, parser):
        parser.add_argument("chemin")
        parser.add_argument("--vider", action="store_true")

    def handle(self, *args, **opts):
        try:
            with open(opts["chemin"], encoding="utf-8") as f:
                data = json.load(f)
        except OSError as e:
            raise CommandError(e)

        if opts["vider"]:
            ZoneMartienneAutorisee.objects.all().delete()

        n = 0
        for feat in data["features"]:
            geom = GEOSGeometry(json.dumps(feat["geometry"]), srid=4326)
            if geom.geom_type == "MultiPolygon":
                geom = geom[0]                      # on garde le premier polygone
            if not isinstance(geom, Polygon):
                self.stderr.write(f"Ignoré (type {geom.geom_type})")
                continue
            props = feat.get("properties", {})
            ZoneMartienneAutorisee.objects.create(
                nom=props.get("nom", f"Zone {n + 1}"),
                description=props.get("description", ""),
                geom=geom,
            )
            n += 1
        self.stdout.write(self.style.SUCCESS(f"{n} zone(s) importée(s)"))