"""
Tests for auth and database modules.
"""

import os
import tempfile
import unittest
from backend import auth, db


class TestAuth(unittest.TestCase):

    def setUp(self):
        # Use temporary SQLite database for tests
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        db.init_db(self.db_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_password_hashing(self):
        h1, s1 = auth.hash_password("SuperSecret123")
        h2, s2 = auth.hash_password("SuperSecret123")
        
        # Salts should be unique
        self.assertNotEqual(s1, s2)
        self.assertNotEqual(h1, h2)

        # Verification
        self.assertTrue(auth.verify_password("SuperSecret123", h1, s1))
        self.assertFalse(auth.verify_password("WrongPassword", h1, s1))

    def test_user_registration_and_login(self):
        success, user = auth.register_user("Test User", "test@example.com", "Password123")
        self.assertTrue(success)
        self.assertEqual(user['email'], "test@example.com")

        # Reject duplicate email
        success, err = auth.register_user("Another User", "test@example.com", "Password123")
        self.assertFalse(success)
        self.assertIn("already registered", err)

        # Login success
        ok, res = auth.authenticate_user("test@example.com", "Password123")
        self.assertTrue(ok)
        self.assertIn('token', res)
        self.assertEqual(res['user']['email'], "test@example.com")

        # Login failure
        ok, res = auth.authenticate_user("test@example.com", "WrongPassword")
        self.assertFalse(ok)

    def test_session_management(self):
        auth.register_user("Alice", "alice@example.com", "Password123")
        _, res = auth.authenticate_user("alice@example.com", "Password123")
        token = res['token']

        # Lookup session
        current = auth.get_current_user_from_token(token)
        self.assertIsNotNone(current)
        self.assertEqual(current['email'], "alice@example.com")

        # Logout
        auth.logout_token(token)
        self.assertIsNone(auth.get_current_user_from_token(token))


if __name__ == '__main__':
    unittest.main()
