"""
Core Application HTTP Server and API Router for Generated App.
Implemented with pure Python 3 standard library:
- 0 external dependencies
- Fast & lightweight
- Secure sessions & role-based access control
- Real build orchestration with live status tracking
"""

import http.cookies
import json
import mimetypes
import os
import shutil
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import auth, build_engine, db, multipart, validator

# ------------------------------------------------------------------------------
# In-Memory Rate Limiting
# ------------------------------------------------------------------------------
_RATE_LIMITS = {}  # {ip: [(timestamp)]}


def is_rate_limited(ip, max_requests=60, window_seconds=60):
    now = time.time()
    history = _RATE_LIMITS.setdefault(ip, [])
    # Filter expired timestamps
    _RATE_LIMITS[ip] = [ts for ts in history if now - ts < window_seconds]
    if len(_RATE_LIMITS[ip]) >= max_requests:
        return True
    _RATE_LIMITS[ip].append(now)
    return False


# ------------------------------------------------------------------------------
# Environment Variables Loader (Simple .env parser)
# ------------------------------------------------------------------------------
def load_env(env_path=None):
    if not env_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(base_dir, '.env')
    if not os.path.isfile(env_path):
        return
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"\'')
            if k not in os.environ:
                os.environ[k] = v


# ------------------------------------------------------------------------------
# Request Handler
# ------------------------------------------------------------------------------
class AppRequestHandler(BaseHTTPRequestHandler):
    server_version = "GeneratedApp/1.0"

    def log_message(self, format, *args):
        # Clean logging format
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} - {format % args}")

    def get_client_ip(self):
        xff = self.headers.get('X-Forwarded-For')
        if xff:
            return xff.split(',')[0].strip()
        return self.client_address[0]

    def send_json(self, data, status_code=200, headers=None):
        payload = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def send_file_response(self, file_path, download_filename=None, mime_type=None):
        if not os.path.isfile(file_path):
            self.send_error(404, "File not found")
            return
        
        file_size = os.path.getsize(file_path)
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.send_header('Content-Length', str(file_size))
        self.send_header('X-Content-Type-Options', 'nosniff')
        if download_filename:
            self.send_header('Content-Disposition', f'attachment; filename="{download_filename}"')
        self.end_headers()

        with open(file_path, 'rb') as f:
            shutil.copyfileobj(f, self.wfile)

    def get_session_token(self):
        # 1. Check Authorization header
        auth_header = self.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1].strip()

        # 2. Check Cookie header
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            c = http.cookies.SimpleCookie()
            try:
                c.load(cookie_header)
                if 'session_token' in c:
                    return c['session_token'].value
            except Exception:
                pass
        return None

    def get_current_user(self):
        token = self.get_session_token()
        return auth.get_current_user_from_token(token)

    # --------------------------------------------------------------------------
    # GET Handlers
    # --------------------------------------------------------------------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API Routes
        if path.startswith('/api/'):
            return self.handle_api_get(path, query)

        # 2. Static Asset Routes (/css/*, /js/*)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        frontend_dir = os.path.join(base_dir, 'frontend')

        if path.startswith('/css/') or path.startswith('/js/'):
            safe_rel_path = path.lstrip('/')
            file_path = os.path.join(frontend_dir, safe_rel_path)
            if os.path.isfile(file_path):
                return self.send_file_response(file_path)
            else:
                self.send_error(404, "Asset not found")
                return

        if path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return

        # 3. HTML Pages
        user = self.get_current_user()

        if path in ('/', ''):
            if user:
                self.send_redirect('/dashboard')
            else:
                self.send_redirect('/login')
            return

        page_map = {
            '/login': 'login.html',
            '/register': 'register.html',
            '/dashboard': 'dashboard.html',
            '/generate': 'generate.html',
            '/admin': 'admin.html',
        }

        if path in page_map:
            # Route authentication checks
            if path in ('/login', '/register') and user:
                return self.send_redirect('/dashboard')

            if path in ('/dashboard', '/generate') and not user:
                return self.send_redirect('/login')

            if path == '/admin':
                if not user:
                    return self.send_redirect('/login')
                if user.get('role') != 'admin':
                    return self.send_redirect('/dashboard')

            html_file = os.path.join(frontend_dir, page_map[path])
            if os.path.isfile(html_file):
                return self.send_file_response(html_file, mime_type='text/html; charset=utf-8')

        self.send_error(404, "Page not found")

    def send_redirect(self, target_url):
        self.send_response(302)
        self.send_header('Location', target_url)
        self.end_headers()

    # --------------------------------------------------------------------------
    # API GET Router
    # --------------------------------------------------------------------------
    def handle_api_get(self, path, query):
        user = self.get_current_user()

        if path == '/api/auth/me':
            if not user:
                return self.send_json({'error': 'Unauthorized'}, status_code=401)
            return self.send_json({'user': user})

        if path == '/api/apps':
            if not user:
                return self.send_json({'error': 'Unauthorized'}, status_code=401)
            apps = db.get_apps_by_user(user['id'])
            stats = db.get_stats_for_user(user['id'])
            return self.send_json({
                'apps': apps,
                'stats': stats,
                'user': user
            })

        if path.startswith('/api/apps/') and '/download/' in path:
            if not user:
                return self.send_json({'error': 'Unauthorized'}, status_code=401)
            
            # Format: /api/apps/<id>/download/<type>
            parts = path.strip('/').split('/')
            if len(parts) == 5:
                app_id = parts[2]
                download_type = parts[4].lower() # 'apk' or 'aab'
                
                app = db.get_app_by_id(app_id)
                if not app:
                    return self.send_json({'error': 'App not found'}, status_code=404)
                
                # Authorization: Owner or Admin only
                if app['user_id'] != user['id'] and user.get('role') != 'admin':
                    return self.send_json({'error': 'Forbidden'}, status_code=403)
                
                if download_type == 'apk':
                    file_path = app.get('apk_path')
                    ext = 'apk'
                    mime = 'application/vnd.android.package-archive'
                elif download_type == 'aab':
                    file_path = app.get('aab_path')
                    ext = 'aab'
                    mime = 'application/octet-stream'
                else:
                    return self.send_json({'error': 'Invalid download type'}, status_code=400)
                
                if not file_path or not os.path.exists(file_path):
                    return self.send_json({'error': f'{download_type.upper()} file is not available yet'}, status_code=404)
                
                clean_name = validator.sanitize_filename(app['name'])
                filename = f"{clean_name}.{ext}"
                return self.send_file_response(file_path, download_filename=filename, mime_type=mime)

        if path.startswith('/api/apps/'):
            if not user:
                return self.send_json({'error': 'Unauthorized'}, status_code=401)
            app_id = path.replace('/api/apps/', '').strip('/')
            app = db.get_app_by_id(app_id)
            if not app:
                return self.send_json({'error': 'App not found'}, status_code=404)
            if app['user_id'] != user['id'] and user.get('role') != 'admin':
                return self.send_json({'error': 'Forbidden'}, status_code=403)
            return self.send_json({'app': app})

        # Admin Routes
        if path.startswith('/api/admin/'):
            if not user:
                return self.send_json({'error': 'Unauthorized'}, status_code=401)
            if user.get('role') != 'admin':
                return self.send_json({'error': 'Admin access required'}, status_code=403)

            if path == '/api/admin/stats':
                stats = db.get_stats_for_admin()
                env_status = build_engine.detect_build_environment()
                return self.send_json({'stats': stats, 'build_engine': env_status})

            if path == '/api/admin/users':
                users = db.get_all_users()
                return self.send_json({'users': users})

            if path == '/api/admin/apps':
                apps = db.get_all_apps()
                return self.send_json({'apps': apps})

        if path == '/api/system/status':
            env_status = build_engine.detect_build_environment()
            return self.send_json({
                'status': 'ok',
                'app_name': os.environ.get('APP_NAME', 'Generated App'),
                'build_engine': env_status
            })

        return self.send_json({'error': 'Not found'}, status_code=404)

    # --------------------------------------------------------------------------
    # POST Handlers
    # --------------------------------------------------------------------------
    def do_POST(self):
        client_ip = self.get_client_ip()
        if is_rate_limited(client_ip, max_requests=100, window_seconds=60):
            return self.send_json({'error': 'Rate limit exceeded. Please try again shortly.'}, status_code=429)

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type', '')

        # Max payload size check
        max_size = int(os.environ.get('MAX_FILE_SIZE', 2097152)) + 1048576  # 2MB icon + buffer
        if content_length > max_size:
            return self.send_json({'error': 'Request payload too large.'}, status_code=413)

        body_bytes = self.rfile.read(content_length) if content_length > 0 else b''

        # Parse JSON or Multipart
        json_data = {}
        files_data = {}
        if 'application/json' in content_type:
            try:
                json_data = json.loads(body_bytes.decode('utf-8'))
            except Exception:
                return self.send_json({'error': 'Invalid JSON body.'}, status_code=400)
        elif 'multipart/form-data' in content_type:
            fields, files_data = multipart.parse_multipart(body_bytes, content_type)
            json_data = fields

        # Route POST
        if path == '/api/auth/register':
            return self.handle_register(json_data)

        if path == '/api/auth/login':
            return self.handle_login(json_data)

        if path == '/api/auth/logout':
            return self.handle_logout()

        if path == '/api/apps/generate':
            return self.handle_generate_app(json_data, files_data)

        return self.send_json({'error': 'Endpoint not found.'}, status_code=404)

    # --------------------------------------------------------------------------
    # DELETE Handlers
    # --------------------------------------------------------------------------
    def do_DELETE(self):
        user = self.get_current_user()
        if not user:
            return self.send_json({'error': 'Unauthorized'}, status_code=401)

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Delete App: /api/apps/<id> or /api/admin/apps/<id>
        if path.startswith('/api/apps/') or path.startswith('/api/admin/apps/'):
            parts = path.strip('/').split('/')
            app_id = parts[-1]
            app = db.get_app_by_id(app_id)
            if not app:
                return self.send_json({'error': 'App not found'}, status_code=404)

            # Owner or Admin
            if app['user_id'] != user['id'] and user.get('role') != 'admin':
                return self.send_json({'error': 'Forbidden'}, status_code=403)

            # Clean storage files
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            app_storage = os.path.join(base_dir, 'storage', 'users', app['user_id'], app_id)
            if os.path.exists(app_storage):
                shutil.rmtree(app_storage, ignore_errors=True)

            db.delete_app(app_id)
            return self.send_json({'success': True, 'message': 'App deleted successfully'})

        # Delete User (Admin only): /api/admin/users/<id>
        if path.startswith('/api/admin/users/'):
            if user.get('role') != 'admin':
                return self.send_json({'error': 'Admin access required'}, status_code=403)
            user_id = path.replace('/api/admin/users/', '').strip('/')
            
            # Prevent deleting self
            if user_id == user['id']:
                return self.send_json({'error': 'Cannot delete your own admin account.'}, status_code=400)

            # Clean storage
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            user_storage = os.path.join(base_dir, 'storage', 'users', user_id)
            if os.path.exists(user_storage):
                shutil.rmtree(user_storage, ignore_errors=True)

            db.delete_user(user_id)
            return self.send_json({'success': True, 'message': 'User deleted successfully'})

        return self.send_json({'error': 'Endpoint not found.'}, status_code=404)

    # --------------------------------------------------------------------------
    # Controller Action Implementations
    # --------------------------------------------------------------------------
    def handle_register(self, data):
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        confirm_password = data.get('confirm_password') or data.get('confirmPassword') or ''

        if not name:
            return self.send_json({'error': 'Name is required.'}, status_code=400)
        if not email or '@' not in email:
            return self.send_json({'error': 'Valid email is required.'}, status_code=400)
        if not password or len(password) < 6:
            return self.send_json({'error': 'Password must be at least 6 characters.'}, status_code=400)
        if password != confirm_password:
            return self.send_json({'error': 'Passwords do not match.'}, status_code=400)

        success, res = auth.register_user(name, email, password)
        if not success:
            return self.send_json({'error': res}, status_code=400)

        # Automatically log in after registration
        _, login_res = auth.authenticate_user(email, password)
        cookie = f"session_token={login_res['token']}; Path=/; HttpOnly; SameSite=Lax; Max-Age=604800"
        return self.send_json({
            'success': True,
            'message': 'Registration successful.',
            'user': login_res['user'],
            'token': login_res['token']
        }, headers={'Set-Cookie': cookie})

    def handle_login(self, data):
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''

        if not email or not password:
            return self.send_json({'error': 'Email and password are required.'}, status_code=400)

        success, res = auth.authenticate_user(email, password)
        if not success:
            return self.send_json({'error': res}, status_code=401)

        cookie = f"session_token={res['token']}; Path=/; HttpOnly; SameSite=Lax; Max-Age=604800"
        return self.send_json({
            'success': True,
            'message': 'Login successful.',
            'user': res['user'],
            'token': res['token']
        }, headers={'Set-Cookie': cookie})

    def handle_logout(self):
        token = self.get_session_token()
        if token:
            auth.logout_token(token)
        cookie = "session_token=; Path=/; HttpOnly; Max-Age=0"
        return self.send_json({'success': True, 'message': 'Logged out.'}, headers={'Set-Cookie': cookie})

    def handle_generate_app(self, fields, files):
        user = self.get_current_user()
        if not user:
            return self.send_json({'error': 'Unauthorized. Please login.'}, status_code=401)

        # 1. Validate Target Website URL
        raw_url = fields.get('url') or ''
        is_valid_url, url_or_err = validator.validate_url(raw_url)
        if not is_valid_url:
            return self.send_json({'error': url_or_err}, status_code=400)
        target_url = url_or_err

        # 2. Validate App Name
        raw_name = fields.get('name') or ''
        is_valid_name, name_or_err = validator.validate_app_name(raw_name)
        if not is_valid_name:
            return self.send_json({'error': name_or_err}, status_code=400)
        app_name = name_or_err

        # 3. Validate or Auto-Generate Package Name
        raw_pkg = (fields.get('package_name') or fields.get('packageName') or '').strip()
        if raw_pkg:
            is_valid_pkg, pkg_or_err = validator.validate_package_name(raw_pkg)
            if not is_valid_pkg:
                return self.send_json({'error': pkg_or_err}, status_code=400)
            package_name = pkg_or_err
        else:
            package_name = validator.generate_package_name_from_url(target_url)

        # 4. Validate Version & Version Code
        raw_version = fields.get('version') or '1.0.0'
        is_valid_ver, version = validator.validate_version(raw_version)
        if not is_valid_ver:
            version = '1.0.0'

        raw_version_code = fields.get('version_code') or fields.get('versionCode') or 1
        is_valid_code, version_code = validator.validate_version_code(raw_version_code)
        if not is_valid_code:
            version_code = 1

        # 5. Handle App Icon (Optional PNG upload)
        icon_path = None
        icon_file = files.get('icon')
        if icon_file and icon_file.get('data'):
            icon_bytes = icon_file['data']
            is_valid_icon, icon_res = validator.validate_icon_bytes(icon_bytes)
            if not is_valid_icon:
                return self.send_json({'error': icon_res}, status_code=400)
            
            # Save uploaded icon temporarily
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_dir = os.path.join(base_dir, 'storage', 'icons')
            os.makedirs(icon_dir, exist_ok=True)
            icon_path = os.path.join(icon_dir, f"icon-{int(time.time()*1000)}.png")
            with open(icon_path, 'wb') as f:
                f.write(icon_bytes)

        # 6. Create App Entry in Database
        import uuid
        app_id = str(uuid.uuid4())
        app_record = db.create_app(
            app_id=app_id,
            user_id=user['id'],
            name=app_name,
            url=target_url,
            package_name=package_name,
            version=version,
            version_code=version_code,
            icon_path=icon_path
        )

        # 7. Trigger Build Pipeline (Asynchronous, non-blocking)
        build_engine.build_app_async(app_id)

        return self.send_json({
            'success': True,
            'message': 'Build started.',
            'app_id': app_id,
            'app': app_record
        }, status_code=202)


def run_server(host='0.0.0.0', port=3000):
    load_env()
    
    # Configure database
    db.init_db()

    # Seed admin user
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'CHANGE_ME')
    admin_name = os.environ.get('ADMIN_NAME', 'Admin')
    auth.seed_admin_user(admin_email, admin_password, admin_name)

    env_status = build_engine.detect_build_environment()
    print("==================================================")
    print(f"[*] {os.environ.get('APP_NAME', 'Generated App')} starting...")
    print(f"[*] Listening on http://{host}:{port}")
    print(f"[*] Build Engine status: {'READY' if env_status['ready'] else 'DEPENDENCIES NEEDED'}")
    for d in env_status['details']:
        print(f"    - {d}")
    print("==================================================")

    server = ThreadingHTTPServer((host, port), AppRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
        server.server_close()
