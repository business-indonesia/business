"""
Zero-dependency lightweight multipart/form-data parser for Python standard library.
"""

import re


def parse_multipart(body_bytes, content_type_header):
    """
    Parses multipart/form-data into fields dict and files dict.
    Returns:
        fields: dict of {name: str_value}
        files: dict of {name: {'filename': str, 'content_type': str, 'data': bytes}}
    """
    fields = {}
    files = {}

    match = re.search(r'boundary=([^;]+)', content_type_header, re.IGNORECASE)
    if not match:
        return fields, files

    boundary_str = match.group(1).strip().strip('"')
    boundary = ('--' + boundary_str).encode('utf-8')
    boundary_end = ('--' + boundary_str + '--').encode('utf-8')

    parts = body_bytes.split(boundary)
    for part in parts:
        if not part or part.startswith(b'--') or part == b'\r\n':
            continue

        # Strip leading \r\n and trailing \r\n
        if part.startswith(b'\r\n'):
            part = part[2:]
        if part.endswith(b'\r\n'):
            part = part[:-2:]

        # Split headers and body at double CRLF
        subparts = part.split(b'\r\n\r\n', 1)
        if len(subparts) != 2:
            continue

        headers_raw, content_raw = subparts
        headers_str = headers_raw.decode('latin-1', errors='replace')

        cd_match = re.search(r'Content-Disposition:\s*form-data;\s*name="([^"]+)"(?:;\s*filename="([^"]*)")?', headers_str, re.IGNORECASE)
        if not cd_match:
            continue

        field_name = cd_match.group(1)
        filename = cd_match.group(2)

        ct_match = re.search(r'Content-Type:\s*([^\r\n;]+)', headers_str, re.IGNORECASE)
        content_type = ct_match.group(1).strip() if ct_match else 'application/octet-stream'

        if filename is not None and filename != '':
            files[field_name] = {
                'filename': filename,
                'content_type': content_type,
                'data': content_raw
            }
        else:
            fields[field_name] = content_raw.decode('utf-8', errors='replace')

    return fields, files
