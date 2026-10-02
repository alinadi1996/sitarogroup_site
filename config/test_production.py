"""Production guardrails; all subprocess values are test-only, never real secrets."""
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase, SimpleTestCase, override_settings


class ProductionSettingsTests(SimpleTestCase):
    def run_settings(self, code, **overrides):
        test_env = os.environ.copy()
        test_env.update({
            'PYTHONDONTWRITEBYTECODE': '1', 'DJANGO_SETTINGS_MODULE': 'config.settings',
            'DJANGO_ENV': 'production', 'DJANGO_DEBUG': 'false',
            'DJANGO_SECRET_KEY': 'test-only-0123456789-abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'DJANGO_ALLOWED_HOSTS': 'sitarogroup.ir,www.sitarogroup.ir',
            'DJANGO_CSRF_TRUSTED_ORIGINS': 'https://sitarogroup.ir',
            'POSTGRES_PASSWORD': 'test-only-password',
            'EMAIL_HOST': 'smtp.example.com', 'DEFAULT_FROM_EMAIL': 'noreply@sitarogroup.ir',
            'EMAIL_USE_TLS': 'true', 'EMAIL_USE_SSL': 'false',
        })
        test_env.update(overrides)
        return subprocess.run([sys.executable, '-c', code], env=test_env,
                              cwd=Path(__file__).resolve().parent.parent,
                              capture_output=True, text=True)

    def test_production_bool_and_smtp_backend(self):
        result = self.run_settings(
            "import django; django.setup(); from django.conf import settings; "
            "from django.core.mail import mailers; "
            "assert settings.DEBUG is False; assert settings.SESSION_COOKIE_SECURE; "
            "assert settings.CSRF_COOKIE_SECURE; "
            "assert mailers['default'].host == 'smtp.example.com'; "
            "assert mailers['default'].use_tls is True"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_production_configuration_fails_closed(self):
        for values in ({'DJANGO_DEBUG': 'true'}, {'DJANGO_SECRET_KEY': ''},
                       {'POSTGRES_PASSWORD': ''}, {'POSTGRES_PASSWORD': 'replace-with-password'},
                       {'DJANGO_ALLOWED_HOSTS': '*'},
                       {'DJANGO_CSRF_TRUSTED_ORIGINS': 'http://sitarogroup.ir'},
                       {'EMAIL_HOST': ''}, {'EMAIL_USE_SSL': 'true'}):
            with self.subTest(values=values):
                result = self.run_settings('import config.settings', **values)
                self.assertNotEqual(result.returncode, 0)


@override_settings(SECURE_SSL_REDIRECT=True, SECURE_REDIRECT_EXEMPT=[r'^healthz/$'])
class ReadinessTests(TestCase):
    def test_database_is_checked_without_https_redirect(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertIn('no-store', response['Cache-Control'])

    @patch('config.health.connection.cursor', side_effect=OperationalError('private credentials'))
    def test_database_failure_returns_no_sensitive_details(self, _cursor):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unavailable'})
        self.assertNotContains(response, 'private credentials', status_code=503)

    def test_probe_is_get_only(self):
        self.assertEqual(self.client.post('/healthz/').status_code, 405)
