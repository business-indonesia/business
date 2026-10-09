"""
Tests for build engine template generation, parameter replacement, and diagnostics.
"""

import os
import shutil
import tempfile
import unittest
from backend import build_engine


class TestBuildEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_environment_detection(self):
        env = build_engine.detect_build_environment()
        self.assertIn('ready', env)
        self.assertIn('java_ready', env)
        self.assertIn('android_ready', env)
        self.assertIn('details', env)
        self.assertIsInstance(env['details'], list)

    def test_prepare_android_project(self):
        app_name = "My Test App"
        target_url = "https://example.com/portal"
        package_name = "com.test.myportal"
        version_name = "2.1.0"
        version_code = 5

        build_engine.prepare_android_project(
            temp_dir=self.temp_dir,
            app_name=app_name,
            target_url=target_url,
            package_name=package_name,
            version_name=version_name,
            version_code=version_code
        )

        # 1. Verify app/build.gradle contains package and version
        gradle_path = os.path.join(self.temp_dir, 'app', 'build.gradle')
        self.assertTrue(os.path.exists(gradle_path))
        with open(gradle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(f"namespace '{package_name}'", content)
        self.assertIn(f"applicationId '{package_name}'", content)
        self.assertIn(f"versionCode {version_code}", content)
        self.assertIn(f"versionName '{version_name}'", content)

        # 2. Verify AndroidManifest.xml
        manifest_path = os.path.join(self.temp_dir, 'app', 'src', 'main', 'AndroidManifest.xml')
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(f'package="{package_name}"', content)

        # 3. Verify strings.xml
        strings_path = os.path.join(self.temp_dir, 'app', 'src', 'main', 'res', 'values', 'strings.xml')
        self.assertTrue(os.path.exists(strings_path))
        with open(strings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(app_name, content)
        self.assertIn(target_url, content)

        # 4. Verify MainActivity.java moved to package hierarchy
        expected_java = os.path.join(self.temp_dir, 'app', 'src', 'main', 'java', 'com', 'test', 'myportal', 'MainActivity.java')
        self.assertTrue(os.path.exists(expected_java))
        with open(expected_java, 'r', encoding='utf-8') as f:
            java_code = f.read()
        self.assertIn(f"package {package_name};", java_code)


if __name__ == '__main__':
    unittest.main()
