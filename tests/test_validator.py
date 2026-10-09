"""
Tests for validator module.
"""

import unittest
from backend import validator


class TestValidator(unittest.TestCase):

    def test_url_valid(self):
        valid_urls = [
            'https://example.com',
            'http://example.com/page?query=1',
            'https://sangkala.business.web.id',
            'mywebsite.com'  # should auto-prefix https://
        ]
        for u in valid_urls:
            is_valid, res = validator.validate_url(u)
            self.assertTrue(is_valid, f"Failed for valid URL: {u}")
            self.assertTrue(res.startswith('http://') or res.startswith('https://'))

    def test_url_rejects_malicious(self):
        blocked = [
            'javascript:alert(1)',
            'file:///etc/passwd',
            'data:text/html;base64,PHNjcmlwdD4=',
            'http://localhost',
            'http://localhost:3000',
            'http://127.0.0.1:8080',
            'http://192.168.1.1',
            'http://10.0.0.1',
            'http://172.16.0.1'
        ]
        for u in blocked:
            is_valid, _ = validator.validate_url(u)
            self.assertFalse(is_valid, f"Expected reject for {u}")

    def test_package_name_validation(self):
        self.assertTrue(validator.validate_package_name('com.example.app')[0])
        self.assertTrue(validator.validate_package_name('id.web.business.sangkala')[0])
        self.assertTrue(validator.validate_package_name('com.my_company.my_app')[0])

        # Invalid cases
        self.assertFalse(validator.validate_package_name('com')[0])  # Needs at least 2 segments
        self.assertFalse(validator.validate_package_name('com.example.123app')[0])  # Segment starts with digit
        self.assertFalse(validator.validate_package_name('com.example.class')[0])  # Reserved keyword
        self.assertFalse(validator.validate_package_name('com.example.app-name')[0])  # Hyphen illegal in Java

    def test_package_name_generation(self):
        pkg = validator.generate_package_name_from_url('https://sangkala.business.web.id')
        self.assertEqual(pkg, 'id.web.business.sangkala')

        pkg2 = validator.generate_package_name_from_url('https://example.com')
        self.assertEqual(pkg2, 'com.example')

    def test_sanitize_filename(self):
        self.assertEqual(validator.sanitize_filename('Example App'), 'Example-App')
        self.assertEqual(validator.sanitize_filename('Sangkala Bekerja'), 'Sangkala-Bekerja')
        self.assertEqual(validator.sanitize_filename('App!@#$$%^&*()'), 'App')

    def test_icon_validation(self):
        valid_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 50
        is_valid, _ = validator.validate_icon_bytes(valid_png)
        self.assertTrue(is_valid)

        invalid_file = b'MZ\x90\x00\x03\x00' # EXE header
        is_valid, _ = validator.validate_icon_bytes(invalid_file)
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()
