"""
Authentication, Password Hashing and Session Management.
Uses standard PBKDF2-HMAC-SHA256 with cryptographically secure random salts.
"""

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta
import uuid

from . import db


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex(), salt


def verify_password(password, stored_hash, salt):
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return hmac.compare_digest(key.hex(), stored_hash)


def register_user(name, email, password, role='user'):
    existing = db.get_user_by_email(email)
    if existing:
        return False, "Email already registered."
    
    user_id = str(uuid.uuid4())
    pw_hash, pw_salt = hash_password(password)
    user = db.create_user(user_id, name, email, pw_hash, pw_salt, role=role)
    return True, user


def authenticate_user(email, password):
    user = db.get_user_by_email(email)
    if not user:
        return False, "Invalid email or password."
    
    if not verify_password(password, user['password_hash'], user['password_salt']):
        return False, "Invalid email or password."
    
    # Create session token
    token = secrets.token_hex(32)
    expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
    db.create_session(token, user['id'], expires_at)
    
    user_info = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role']
    }
    return True, {'user': user_info, 'token': token, 'expires_at': expires_at}


def get_current_user_from_token(token):
    if not token:
        return None
    session = db.get_session(token)
    if not session:
        return None
    
    # Check expiry
    expires_at = datetime.fromisoformat(session['expires_at'])
    if datetime.utcnow() > expires_at:
        db.delete_session(token)
        return None
    
    return {
        'id': session['user_id'],
        'name': session['name'],
        'email': session['email'],
        'role': session['role'],
        'token': session['token']
    }


def logout_token(token):
    if token:
        db.delete_session(token)
        return True
    return False


def seed_admin_user(admin_email, admin_password, admin_name="Admin"):
    """
    Ensures default admin account exists based on environment variables.
    """
    if not admin_email or not admin_password:
        return
    existing = db.get_user_by_email(admin_email)
    if not existing:
        user_id = str(uuid.uuid4())
        pw_hash, pw_salt = hash_password(admin_password)
        db.create_user(user_id, admin_name, admin_email, pw_hash, pw_salt, role='admin')
        print(f"[*] Admin user initialized: {admin_email}")
    else:
        # If user exists but is not admin, upgrade to admin
        if existing['role'] != 'admin':
            # Update role in database
            conn = db.get_connection()
            try:
                with conn:
                    conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (existing['id'],))
            finally:
                conn.close()
