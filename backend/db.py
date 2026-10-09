"""
SQLite Database Layer for Generated App.
Zero external dependencies, fast, ACID compliant.
"""

import os
import sqlite3
import threading
from datetime import datetime

_DB_PATH = None
_LOCK = threading.Lock()


def get_db_path():
    global _DB_PATH
    if _DB_PATH:
        return _DB_PATH
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    storage_dir = os.path.join(base_dir, 'storage')
    os.makedirs(storage_dir, exist_ok=True)
    _DB_PATH = os.path.join(storage_dir, 'database.sqlite')
    return _DB_PATH


def set_db_path(path):
    global _DB_PATH
    _DB_PATH = path


def get_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path=None):
    if db_path:
        set_db_path(db_path)
    
    with _LOCK:
        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        password_salt TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'user',
                        created_at TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS apps (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        url TEXT NOT NULL,
                        package_name TEXT NOT NULL,
                        version TEXT NOT NULL DEFAULT '1.0.0',
                        version_code INTEGER NOT NULL DEFAULT 1,
                        icon_path TEXT,
                        apk_path TEXT,
                        aab_path TEXT,
                        apk_size INTEGER DEFAULT 0,
                        aab_size INTEGER DEFAULT 0,
                        status TEXT NOT NULL DEFAULT 'Queued',
                        build_log TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        token TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)

                # Indices for fast lookups
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_apps_user_id ON apps(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        finally:
            conn.close()


# ------------------------------------------------------------------------------
# User Operations
# ------------------------------------------------------------------------------

def create_user(user_id, name, email, password_hash, password_salt, role='user'):
    with _LOCK:
        conn = get_connection()
        try:
            now = datetime.utcnow().isoformat()
            with conn:
                conn.execute("""
                    INSERT INTO users (id, name, email, password_hash, password_salt, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, name, email.strip().lower(), password_hash, password_salt, role, now))
            return get_user_by_id(user_id)
        finally:
            conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_users():
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT u.id, u.name, u.email, u.role, u.created_at,
                   COUNT(a.id) as apps_count
            FROM users u
            LEFT JOIN apps a ON u.id = a.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def delete_user(user_id):
    with _LOCK:
        conn = get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return True
        finally:
            conn.close()


# ------------------------------------------------------------------------------
# Session Operations
# ------------------------------------------------------------------------------

def create_session(token, user_id, expires_at):
    with _LOCK:
        conn = get_connection()
        try:
            now = datetime.utcnow().isoformat()
            with conn:
                conn.execute("""
                    INSERT INTO sessions (token, user_id, expires_at, created_at)
                    VALUES (?, ?, ?, ?)
                """, (token, user_id, expires_at, now))
        finally:
            conn.close()


def get_session(token):
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT s.token, s.user_id, s.expires_at, u.name, u.email, u.role
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        """, (token,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_session(token):
    with _LOCK:
        conn = get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        finally:
            conn.close()


def clean_expired_sessions():
    with _LOCK:
        conn = get_connection()
        try:
            now = datetime.utcnow().isoformat()
            with conn:
                conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
        finally:
            conn.close()


# ------------------------------------------------------------------------------
# App Operations
# ------------------------------------------------------------------------------

def create_app(app_id, user_id, name, url, package_name, version='1.0.0', version_code=1, icon_path=None):
    with _LOCK:
        conn = get_connection()
        try:
            now = datetime.utcnow().isoformat()
            with conn:
                conn.execute("""
                    INSERT INTO apps (
                        id, user_id, name, url, package_name, version, version_code,
                        icon_path, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Queued', ?, ?)
                """, (app_id, user_id, name, url, package_name, version, version_code, icon_path, now, now))
            return get_app_by_id(app_id)
        finally:
            conn.close()


def get_app_by_id(app_id):
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT a.*, u.name as user_name, u.email as user_email
            FROM apps a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = ?
        """, (app_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_apps_by_user(user_id):
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT * FROM apps
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_all_apps():
    conn = get_connection()
    try:
        cur = conn.execute("""
            SELECT a.*, u.name as user_name, u.email as user_email
            FROM apps a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def update_app_build(app_id, status, apk_path=None, aab_path=None, apk_size=0, aab_size=0, build_log=None):
    with _LOCK:
        conn = get_connection()
        try:
            now = datetime.utcnow().isoformat()
            with conn:
                conn.execute("""
                    UPDATE apps
                    SET status = ?, apk_path = ?, aab_path = ?, apk_size = ?, aab_size = ?,
                        build_log = ?, updated_at = ?
                    WHERE id = ?
                """, (status, apk_path, aab_path, apk_size, aab_size, build_log, now, app_id))
            return get_app_by_id(app_id)
        finally:
            conn.close()


def delete_app(app_id):
    with _LOCK:
        conn = get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM apps WHERE id = ?", (app_id,))
            return True
        finally:
            conn.close()


# ------------------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------------------

def get_stats_for_admin():
    conn = get_connection()
    try:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_apps = conn.execute("SELECT COUNT(*) FROM apps").fetchone()[0]
        successful_builds = conn.execute("SELECT COUNT(*) FROM apps WHERE status = 'Success'").fetchone()[0]
        failed_builds = conn.execute("SELECT COUNT(*) FROM apps WHERE status = 'Failed'").fetchone()[0]
        total_builds = successful_builds + failed_builds
        return {
            'total_users': total_users,
            'total_apps': total_apps,
            'total_builds': total_builds,
            'successful_builds': successful_builds,
            'failed_builds': failed_builds,
        }
    finally:
        conn.close()


def get_stats_for_user(user_id):
    conn = get_connection()
    try:
        user_apps = conn.execute("SELECT COUNT(*) FROM apps WHERE user_id = ?", (user_id,)).fetchone()[0]
        successful_builds = conn.execute("SELECT COUNT(*) FROM apps WHERE user_id = ? AND status = 'Success'", (user_id,)).fetchone()[0]
        return {
            'your_apps': user_apps,
            'successful_builds': successful_builds,
        }
    finally:
        conn.close()
