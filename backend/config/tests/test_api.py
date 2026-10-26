from unittest.mock import patch

from django.db import OperationalError, ProgrammingError
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient


class DiagnosticsTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_liveness_works_without_database(self):
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertTrue(response.json()['python_version'].startswith('3.12.'))

    def test_capabilities_do_not_claim_scientific_data(self):
        response = self.client.get('/api/v1/capabilities/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['scientific_data_loaded'])
        modules = response.json()['modules']
        self.assertTrue(all(m['status'] == 'planned' for m in modules if m['phase'] > 1))

    @patch('config.views.connection')
    def test_readiness_checks_postgis(self, db):
        db.cursor.return_value.__enter__.return_value.fetchone.return_value = ['3.4 TEST']
        response = self.client.get('/api/v1/ready/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['postgis_version'], '3.4 TEST')
        db.cursor.return_value.__enter__.return_value.execute.assert_called_once_with('SELECT PostGIS_Version()')

    @patch('config.views.connection')
    def test_database_failure_is_503_without_leaking_credentials(self, db):
        db.cursor.side_effect = OperationalError('password=private-host-secret')
        response = self.client.get('/api/v1/ready/')
        self.assertEqual(response.status_code, 503)
        self.assertIsNone(response.json()['postgis_version'])
        self.assertNotIn('private-host-secret', response.content.decode())

    @patch('config.views.connection')
    def test_missing_postgis_extension_is_503(self, db):
        db.cursor.return_value.__enter__.return_value.execute.side_effect = ProgrammingError('undefined function')
        self.assertEqual(self.client.get('/api/v1/ready/').status_code, 503)

    @override_settings(CORS_ALLOWED_ORIGINS=['http://localhost:5173'])
    def test_cors_allows_local_frontend(self):
        response = self.client.options('/api/v1/health/', HTTP_ORIGIN='http://localhost:5173', HTTP_ACCESS_CONTROL_REQUEST_METHOD='GET')
        self.assertEqual(response['Access-Control-Allow-Origin'], 'http://localhost:5173')

    def test_cors_rejects_unknown_origin(self):
        response = self.client.get('/api/v1/health/', HTTP_ORIGIN='https://example.invalid')
        self.assertNotIn('Access-Control-Allow-Origin', response)
