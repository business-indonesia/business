"""
Validation and sanitization utilities for Generated App.
Enforces strict security, URL safety, Android package naming, and file validation.
"""

import ipaddress
import re
from urllib.parse import urlparse

JAVA_RESERVED_KEYWORDS = {
    'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
    'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
    'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
    'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
    'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
    'volatile', 'while', 'true', 'false', 'null'
}


def validate_url(url_str):
    """
    Validates target URL according to strict rules.
    Rejects: javascript:, file:, data:, localhost, private/local IPs.
    Defaults to https:// if scheme is missing.
    """
    if not url_str or not isinstance(url_str, str):
        return False, "URL cannot be empty."
    
    url = url_str.strip()
    
    # Block dangerous URI schemes explicitly
    lower_url = url.lower()
    if lower_url.startswith(('javascript:', 'file:', 'data:', 'vbscript:', 'about:')):
        return False, "Invalid URL scheme."
    
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Malformed URL format."
    
    if parsed.scheme not in ('http', 'https'):
        return False, "Only HTTP and HTTPS protocols are supported."
    
    host = parsed.hostname
    if not host:
        return False, "URL must contain a valid domain hostname."
    
    host_lower = host.lower()
    
    # Block localhost and local hostnames
    if host_lower in ('localhost', 'localhost.localdomain', '127.0.0.1', '::1') or host_lower.endswith('.local'):
        return False, "Localhost addresses are not allowed."
    
    # Check IP addresses against private and loopback ranges
    try:
        ip = ipaddress.ip_address(host_lower)
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
            return False, "Private or local network IP addresses are not allowed."
    except ValueError:
        # Not an IP address, so it's a domain name
        pass

    # Basic hostname syntax check
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        return False, "Invalid characters in domain name."
    
    if '.' not in host:
        return False, "Domain must contain at least one dot (e.g. example.com)."
    
    return True, url


def generate_package_name_from_url(url_str):
    """
    Converts domain to reverse package name.
    e.g. https://sangkala.business.web.id -> id.web.business.sangkala
    https://example.com -> com.example.app
    """
    try:
        parsed = urlparse(url_str if '://' in url_str else 'https://' + url_str)
        host = parsed.hostname or ''
    except Exception:
        host = ''
    
    # Strip port, numbers, illegal characters
    parts = [p.lower() for p in host.split('.') if p]
    cleaned_parts = []
    for part in parts:
        cleaned = re.sub(r'[^a-z0-9_]', '', part)
        if cleaned:
            # Identifier segment cannot start with a digit
            if cleaned[0].isdigit():
                cleaned = 'app_' + cleaned
            if cleaned in JAVA_RESERVED_KEYWORDS:
                cleaned = cleaned + '_app'
            cleaned_parts.append(cleaned)
    
    if not cleaned_parts:
        return "com.example.app"
    
    # Reverse domain segments (e.g. web.id -> id.web)
    reversed_parts = list(reversed(cleaned_parts))
    if len(reversed_parts) == 1:
        reversed_parts.append('app')
    
    package_name = '.'.join(reversed_parts)
    is_valid, _ = validate_package_name(package_name)
    if is_valid:
        return package_name
    return "com.example.app"


def validate_package_name(pkg_str):
    """
    Validates Android package name rules:
    - At least two segments separated by dot
    - Each segment starts with letter, only letters/numbers/underscore
    - Segments cannot be Java keywords
    """
    if not pkg_str or not isinstance(pkg_str, str):
        return False, "Package name cannot be empty."
    
    pkg = pkg_str.strip()
    segments = pkg.split('.')
    if len(segments) < 2:
        return False, "Package name must contain at least two segments (e.g. com.example.app)."
    
    segment_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    for seg in segments:
        if not segment_pattern.match(seg):
            return False, f"Invalid segment '{seg}' in package name. Must start with a letter and contain only alphanumeric characters or underscores."
        if seg.lower() in JAVA_RESERVED_KEYWORDS:
            return False, f"Segment '{seg}' is a reserved Java keyword."
            
    return True, pkg


def validate_app_name(name_str):
    if not name_str or not isinstance(name_str, str):
        return False, "App name cannot be empty."
    name = name_str.strip()
    if len(name) < 1 or len(name) > 60:
        return False, "App name must be between 1 and 60 characters."
    if any(ord(c) < 32 for c in name):
        return False, "App name contains invalid control characters."
    return True, name


def sanitize_filename(name_str):
    """
    Sanitizes app name to safe filename:
    'Sangkala Bekerja' -> 'Sangkala-Bekerja'
    """
    clean = re.sub(r'[^\w\s-]', '', name_str).strip()
    clean = re.sub(r'[\s]+', '-', clean)
    return clean or 'Generated-App'


def validate_version(version_str):
    if not version_str or not isinstance(version_str, str):
        return False, "1.0.0"
    v = version_str.strip()
    if re.match(r'^\d+(\.\d+){1,3}$', v):
        return True, v
    return False, "Invalid version format (use e.g. 1.0.0)."


def validate_version_code(code_val):
    try:
        code = int(code_val)
        if 1 <= code <= 2100000000:
            return True, code
        return False, "Version code must be between 1 and 2100000000."
    except (ValueError, TypeError):
        return False, "Version code must be a valid positive integer."


def validate_icon_bytes(data, max_size=2097152):
    """
    Validates uploaded icon:
    - Must not exceed max_size (default 2MB)
    - Must be a valid PNG file (checks PNG magic header: \x89PNG\r\n\x1a\n)
    """
    if not data:
        return True, None  # Icon is optional
    
    if len(data) > max_size:
        return False, f"Icon file size exceeds maximum limit ({max_size // 1024 // 1024} MB)."
    
    png_signature = b'\x89PNG\r\n\x1a\n'
    if not data.startswith(png_signature):
        return False, "App icon must be a valid PNG image."
    
    return True, data
