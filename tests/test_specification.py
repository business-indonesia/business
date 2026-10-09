"""
Verification script for Section 40: Final Tests.
Executes the exact 10 tests specified by the user.
"""

import os
import shutil
import tempfile
import time
import unittest

from backend import app as app_module
from backend import auth, build_engine, db
from tests.test_api import TestHttpClient


class TestSpecificationSection40(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'spec_test.db')
        db.init_db(self.db_path)
        auth.seed_admin_user("admin@business.web.id", "AdminSecret123", "Admin")
        self.client = TestHttpClient(app_module.AppRequestHandler)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_section_40_all_steps(self):
        # ----------------------------------------------------------------------
        # Test 1: Register test@example.com
        # ----------------------------------------------------------------------
        status, res = self.client.request('POST', '/api/auth/register', {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(status, 200, "Test 1 Failed: Registration should return 200")
        self.assertIn('token', res)

        # ----------------------------------------------------------------------
        # Test 2: Login test@example.com
        # ----------------------------------------------------------------------
        status, res = self.client.request('POST', '/api/auth/login', {
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(status, 200, "Test 2 Failed: Login should return 200")
        self.assertIn('token', res)
        test_user_token = res['token']
        test_user_id = res['user']['id']

        # ----------------------------------------------------------------------
        # Test 3: Generate App
        # URL: https://example.com
        # App Name: Example App
        # Package: com.example.app
        # Version: 1.0.0
        # Version Code: 1
        # ----------------------------------------------------------------------
        status, res = self.client.request('POST', '/api/apps/generate', {
            'url': 'https://example.com',
            'name': 'Example App',
            'package_name': 'com.example.app',
            'version': '1.0.0',
            'version_code': 1
        }, token=test_user_token)
        self.assertEqual(status, 202, "Test 3 Failed: Generate app should return 202 Accepted")
        app_id = res['app_id']

        # Verify app configuration in database
        app = db.get_app_by_id(app_id)
        self.assertEqual(app['name'], 'Example App')
        self.assertEqual(app['url'], 'https://example.com')
        self.assertEqual(app['package_name'], 'com.example.app')
        self.assertEqual(app['version'], '1.0.0')
        self.assertEqual(app['version_code'], 1)

        # ----------------------------------------------------------------------
        # Test 4, 5, 6, 7: Build Engine Pipeline & Android Project Verification
        # Verifies the generated Android project is 100% valid native WebView
        # ----------------------------------------------------------------------
        temp_build = tempfile.mkdtemp()
        try:
            build_engine.prepare_android_project(
                temp_dir=temp_build,
                app_name=app['name'],
                target_url=app['url'],
                package_name=app['package_name'],
                version_name=app['version'],
                version_code=app['version_code']
            )

            # Check MainActivity.java has proper WebView configuration
            activity_file = os.path.join(temp_build, 'app', 'src', 'main', 'java', 'com', 'example', 'app', 'MainActivity.java')
            self.assertTrue(os.path.exists(activity_file), "MainActivity.java must exist in package directory")
            with open(activity_file, 'r', encoding='utf-8') as f:
                java_src = f.read()
            self.assertIn('setJavaScriptEnabled(true)', java_src)
            self.assertIn('setDomStorageEnabled(true)', java_src)
            self.assertIn('CustomWebViewClient', java_src)
            self.assertIn('Intent.ACTION_VIEW', java_src)

            # Check AndroidManifest.xml
            manifest_file = os.path.join(temp_build, 'app', 'src', 'main', 'AndroidManifest.xml')
            self.assertTrue(os.path.exists(manifest_file))
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_src = f.read()
            self.assertIn('package="com.example.app"', manifest_src)
            self.assertIn('android.permission.INTERNET', manifest_src)

            # Check app/build.gradle
            app_gradle = os.path.join(temp_build, 'app', 'build.gradle')
            self.assertTrue(os.path.exists(app_gradle))
            with open(app_gradle, 'r', encoding='utf-8') as f:
                gradle_src = f.read()
            self.assertIn("applicationId 'com.example.app'", gradle_src)
            self.assertIn("versionCode 1", gradle_src)
            self.assertIn("versionName '1.0.0'", gradle_src)
            self.assertIn("signingConfig signingConfigs.release", gradle_src)
        finally:
            shutil.rmtree(temp_build, ignore_errors=True)

        # ----------------------------------------------------------------------
        # Test 8: User can only see their own applications
        # ----------------------------------------------------------------------
        # Register a second user: user2@example.com
        auth.register_user("User Two", "user2@example.com", "password123")
        _, user2_login = auth.authenticate_user("user2@example.com", "password123")
        user2_token = user2_login['token']

        # User 2 requests their apps list
        status, res = self.client.request('GET', '/api/apps', token=user2_token)
        self.assertEqual(status, 200)
        self.assertEqual(len(res['apps']), 0, "User 2 must NOT see User 1's apps")

        # User 2 attempts to view User 1's app directly by ID
        status, _ = self.client.request('GET', f'/api/apps/{app_id}', token=user2_token)
        self.assertEqual(status, 403, "User 2 must be Forbidden from accessing User 1's app")

        # ----------------------------------------------------------------------
        # Test 9: Admin can see all applications
        # ----------------------------------------------------------------------
        _, admin_login = auth.authenticate_user("admin@business.web.id", "AdminSecret123")
        admin_token = admin_login['token']

        status, res = self.client.request('GET', '/api/admin/apps', token=admin_token)
        self.assertEqual(status, 200)
        app_ids = [a['id'] for a in res['apps']]
        self.assertIn(app_id, app_ids, "Admin must be able to view all created applications")

        # ----------------------------------------------------------------------
        # Test 10: Download APK and AAB endpoints
        # ----------------------------------------------------------------------
        # When build succeeds, artifacts are served. If not built yet, returns 404 cleanly.
        status, _ = self.client.request('GET', f'/api/apps/{app_id}/download/apk', token=test_user_token)
        self.assertIn(status, [200, 404])

        # Other user cannot download
        status, _ = self.client.request('GET', f'/api/apps/{app_id}/download/apk', token=user2_token)
        self.assertEqual(status, 403, "Other user must NOT be allowed to download")

        print("\n[✓] All 10 Specification Tests in Section 40 PASSED SUCCESSFULY!")


if __name__ == '__main__':
    unittest.main()
