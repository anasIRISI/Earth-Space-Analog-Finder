import numpy as np
import rasterio
from rasterio import Affine
from rasterio.windows import from_bounds
from scipy import ndimage as ndi
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from rasterio.windows import Window, from_bounds

R_MARS = 3_396_190.0
NODATA = -9999.0


def lire_fenetre(chemin, bbox):
    """Lit l'emprise (lon/lat en degrés) et renvoie (tableau, transformation en degrés)."""
    lon_min, lat_min, lon_max, lat_max = bbox
    deg = 180.0 / (np.pi * R_MARS)
    with rasterio.open(chemin) as src:
        print(f"{chemin} : emprise native {src.bounds} | projeté : {src.crs.is_projected}")
        projete = bool(src.crs) and src.crs.is_projected
        decalage = 0.0
        if projete:                                   # mètres (équirectangulaire Mars)
            k = R_MARS * np.pi / 180
            b = (lon_min * k, lat_min * k, lon_max * k, lat_max * k)
        elif src.bounds.right > 180.5:                # degrés, longitudes 0..360
            if lon_min < 0 and lon_max > 0:
                raise CommandError("Emprise à cheval sur le méridien 0 : non gérée.")
            if lon_min < 0:
                b = (lon_min % 360, lat_min, lon_max % 360, lat_max)
                decalage = -360.0
            else:
                b = (lon_min, lat_min, lon_max, lat_max)
        else:
            b = (lon_min, lat_min, lon_max, lat_max)

        w = from_bounds(*b, transform=src.transform)
        col0, row0 = max(int(np.floor(w.col_off)), 0), max(int(np.floor(w.row_off)), 0)
        col1 = min(int(np.ceil(w.col_off + w.width)), src.width)
        row1 = min(int(np.ceil(w.row_off + w.height)), src.height)
        win = Window(col0, row0, col1 - col0, row1 - row0)

        z = src.read(1, window=win).astype("float64")
        tr = src.window_transform(win)
        if src.nodata is not None:
            z[z == src.nodata] = np.nan

    if projete:                                       # mètres -> degrés
        tr = Affine(tr.a * deg, tr.b * deg, tr.c * deg, tr.d * deg, tr.e * deg, tr.f * deg)
    elif decalage:
        tr = Affine(tr.a, tr.b, tr.c + decalage, tr.d, tr.e, tr.f)
    return z, tr
# def lire_fenetre(chemin, bbox):
#     """Lit l'emprise (lon/lat en degrés) en adaptant la bbox au CRS du raster (mètres ou degrés)."""
#     lon_min, lat_min, lon_max, lat_max = bbox
#     with rasterio.open(chemin) as src:
#         print(f"{chemin} : emprise native {src.bounds} | CRS: {src.crs}")
        
#         # Si le raster est en projection Equirectangulaire en mètres (ex: MOLA DEM)
#         if src.crs and src.crs.to_string() != "EPSG:4326":
#             # Conversion manuelle Degrés -> Mètres pour Mars Equirectangular
#             b_left = np.radians(lon_min) * R_MARS
#             b_right = np.radians(lon_max) * R_MARS
#             b_bottom = np.radians(lat_min) * R_MARS
#             b_top = np.radians(lat_max) * R_MARS
#         else:
#             src360 = src.bounds.right > 180.5
#             if src360:
#                 if lon_min < 0 and lon_max > 0:
#                     raise CommandError("Emprise à cheval sur le méridien 0 : non gérée.")
#                 b_left, b_right = (lon_min % 360, lon_max % 360) if lon_min < 0 else (lon_min, lon_max)
#             else:
#                 b_left, b_right = lon_min, lon_max
#             b_bottom, b_top = lat_min, lat_max

#         # Découper la fenêtre dans le raster
#         win = from_bounds(b_left, b_bottom, b_right, b_top, src.transform)
#         z = src.read(1, window=win, boundless=False).astype("float64")

#         # Générer la transformation spatiale EPSG:4326 en degrés pour les fichiers de sortie
#         h, w = z.shape
#         pixel_size_x = (lon_max - lon_min) / w if w > 0 else 0
#         pixel_size_y = (lat_max - lat_min) / h if h > 0 else 0
#         tr_out = Affine(pixel_size_x, 0.0, lon_min, 0.0, -pixel_size_y, lat_max)

#         if src.nodata is not None:
#             z[z == src.nodata] = np.nan

#     return z, tr_out


def ecrire(chemin, arr, tr):
    out = np.where(np.isfinite(arr), arr, NODATA).astype("float32")
    with rasterio.open(chemin, "w", driver="GTiff", height=out.shape[0],
                       width=out.shape[1], count=1, dtype="float32",
                       crs="EPSG:4326", transform=tr, nodata=NODATA) as dst:
        dst.write(out, 1)
    print("écrit :", chemin)


class Command(BaseCommand):
    help = "Calcule pente, rugosité, relief, altitude (et albédo) de Mars sur une emprise."

    def add_arguments(self, p):
        p.add_argument("--dem", required=True)
        p.add_argument("--albedo")
        p.add_argument("--bbox", nargs=4, type=float, required=True,
                       metavar=("LON_MIN", "LAT_MIN", "LON_MAX", "LAT_MAX"))

    def handle(self, *a, **o):
        sortie = settings.MARS_RASTER_DIR
        sortie.mkdir(parents=True, exist_ok=True)
        z, tr = lire_fenetre(o["dem"], o["bbox"])
        h, w = z.shape
        print(f"fenêtre MNT : {w} x {h} pixels")

        # taille des pixels en mètres (varie avec la latitude)
        lat = tr.f + (np.arange(h) + 0.5) * tr.e
        dy = abs(tr.e) * np.pi / 180 * R_MARS
        dx = abs(tr.a) * np.pi / 180 * R_MARS * np.cos(np.radians(lat))[:, None]

        gy = np.gradient(z, axis=0) / dy
        gx = np.gradient(z, axis=1) / dx
        pente = np.degrees(np.arctan(np.hypot(gx, gy)))

        m1, m2 = ndi.uniform_filter(z, 3), ndi.uniform_filter(z * z, 3)
        rugosite = np.sqrt(np.maximum(m2 - m1 ** 2, 0))     # écart-type 3x3
        relief = ndi.maximum_filter(z, 7) - ndi.minimum_filter(z, 7)

        ecrire(sortie / "mars_altitude.tif", z, tr)
        ecrire(sortie / "mars_pente.tif", pente, tr)
        ecrire(sortie / "mars_rugosite.tif", rugosite, tr)
        ecrire(sortie / "mars_relief.tif", relief, tr)

        if o["albedo"]:
            za, tra = lire_fenetre(o["albedo"], o["bbox"])
            ecrire(sortie / "mars_albedo.tif", za, tra)