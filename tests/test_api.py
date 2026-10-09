"""
End-to-end API integration tests.
Uses in-memory request simulation for fast, isolated, sandbox-safe testing.
"""

import io
import json
import os
import shutil
import tempfile
import unittest

from backend import app as app_module
from backend import auth, db


class DummyServer:
    server_name = 'test'
    server_port = 80


class TestHttpClient:
    def __init__(self, handler_cls):
        self.handler_cls = handler_cls

    def request(self, method, path, data=None, headers=None, token=None):
        headers = headers or {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        body = b''
        if data is not None:
            if isinstance(data, (dict, list)):
                body = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            elif isinstance(data, bytes):
                body = data

        headers_lines = [f'{method} {path} HTTP/1.1', 'Host: localhost']
        for k, v in headers.items():
            headers_lines.append(f'{k}: {v}')
        if body and 'Content-Length' not in headers:
            headers_lines.append(f'Content-Length: {len(body)}')
        headers_lines.append('')
        headers_lines.append('')

        req_bytes = '\r\n'.join(headers_lines).encode('utf-8') + body
        rfile = io.BytesIO(req_bytes)
        wfile = io.BytesIO()

        class DummySocket:
            def __init__(self, r, w):
                self.r = r
                self.w = w
            def makefile(self, mode, *args, **kwargs):
                if 'r' in mode:
                    return self.r
                return self.w
            def sendall(self, d):
                self.w.write(d)

        sock = DummySocket(rfile, wfile)
        self.handler_cls(sock, ('127.0.0.1', 12345), DummyServer())

        res_bytes = wfile.getvalue()
        parts = res_bytes.split(b'\r\n\r\n', 1)
        header_text = parts[0].decode('latin-1')
        body_resp = parts[1] if len(parts) > 1 else b''
        status_line = header_text.splitlines()[0]
        status_code = int(status_line.split()[1])

        parsed_json = {}
        if body_resp:
            try:
                parsed_json = json.loads(body_resp.decode('utf-8'))
            except Exception:
                parsed_json = {'raw': body_resp}

        return status_code, parsed_json


class TestApiIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_api.db')
        db.init_db(self.db_path)

        # Seed admin
        auth.seed_admin_user("admin@example.com", "AdminPassword123", "Super Admin")
        self.client = TestHttpClient(app_module.AppRequestHandler)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_auth_and_user_flow(self):
        # 1. Register Bob
        status, res = self.client.request('POST', '/api/auth/register', {
            'name': 'Bob Tester',
            'email': 'bob@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.assertEqual(status, 200)
        self.assertIn('token', res)
        bob_token = res['token']

        # 2. Get profile (/api/auth/me)
        status, res = self.client.request('GET', '/api/auth/me', token=bob_token)
        self.assertEqual(status, 200)
        self.assertEqual(res['user']['email'], 'bob@example.com')

        # 3. Request Bob's apps list (should be empty initially)
        status, res = self.client.request('GET', '/api/apps', token=bob_token)
        self.assertEqual(status, 200)
        self.assertEqual(len(res['apps']), 0)

        # 4. Generate app with invalid URL
        status, res = self.client.request('POST', '/api/apps/generate', {
            'url': 'javascript:alert(1)',
            'name': 'Bad App'
        }, token=bob_token)
        self.assertEqual(status, 400)
        self.assertIn('error', res)

        # 5. Generate app with valid URL
        status, res = self.client.request('POST', '/api/apps/generate', {
            'url': 'https://sangkala.business.web.id',
            'name': 'Sangkala App'
        }, token=bob_token)
        self.assertEqual(status, 202)
        self.assertIn('app_id', res)
        app_id = res['app_id']

        # Verify app in list and details
        status, res = self.client.request('GET', f'/api/apps/{app_id}', token=bob_token)
        self.assertEqual(status, 200)
        self.assertEqual(res['app']['name'], 'Sangkala App')
        self.assertEqual(res['app']['package_name'], 'id.web.business.sangkala')

        # 6. Admin login
        status, res = self.client.request('POST', '/api/auth/login', {
            'email': 'admin@example.com',
            'password': 'AdminPassword123'
        })
        self.assertEqual(status, 200)
        admin_token = res['token']

        # 7. Admin stats
        status, res = self.client.request('GET', '/api/admin/stats', token=admin_token)
        self.assertEqual(status, 200)
        self.assertGreaterEqual(res['stats']['total_users'], 2)
        self.assertIn('build_engine', res)

        # 8. User access to admin endpoints forbidden
        status, _ = self.client.request('GET', '/api/admin/stats', token=bob_token)
        self.assertEqual(status, 403)

        # 9. Other user cannot access Bob's app
        auth.register_user("Charlie", "charlie@example.com", "Password123")
        _, charlie_login = auth.authenticate_user("charlie@example.com", "Password123")
        status, _ = self.client.request('GET', f'/api/apps/{app_id}', token=charlie_login['token'])
        self.assertEqual(status, 403)


if __name__ == '__main__':
    unittest.main()
