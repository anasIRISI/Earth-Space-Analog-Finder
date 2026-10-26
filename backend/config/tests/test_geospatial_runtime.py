import sys

from django.contrib.gis.gdal import GDAL_VERSION
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.test import SimpleTestCase, TestCase


class GeospatialRuntimeTests(SimpleTestCase):
    def test_required_libraries_import_on_python_312(self):
        import geopandas
        import numpy
        import pyproj
        import rasterio
        import reportlab
        import shapely
        import sklearn

        self.assertEqual(sys.version_info[:2], (3, 12))
        self.assertGreaterEqual(GDAL_VERSION, (3, 1))
        for module in (geopandas, numpy, pyproj, rasterio, reportlab, shapely, sklearn):
            self.assertTrue(module.__version__)

    def test_geos_is_available(self):
        # Géométrie de test technique ; aucune observation scientifique.
        point = GEOSGeometry('POINT (0 0)', srid=4326)
        self.assertTrue(point.valid)


class PostgisIntegrationTests(TestCase):
    def test_actual_postgis_spatial_operation_and_readiness(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT ST_AsText(ST_SetSRID(ST_MakePoint(0, 0), 4326)), PostGIS_Version()")
            geometry, version = cursor.fetchone()
        self.assertEqual(geometry, 'POINT(0 0)')
        self.assertTrue(version)
        response = self.client.get('/api/v1/ready/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ready')
