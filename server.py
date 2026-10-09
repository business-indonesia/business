#!/usr/bin/env python3
"""
Entry point for Generated App.
Run:
    python3 server.py
"""

import os
import sys

# Ensure backend package is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import run_server

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 3000))
    run_server(host=host, port=port)
