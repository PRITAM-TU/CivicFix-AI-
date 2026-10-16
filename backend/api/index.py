"""
CivicFix AI — Vercel Serverless Entry Point
Exports the FastAPI ASGI app for Vercel's Python runtime.
"""
from __future__ import annotations

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
_backend_dir = os.path.join(_parent_dir, "backend")

for _path in [_parent_dir, _backend_dir, _current_dir, "/var/task", "/var/task/backend"]:
    if os.path.exists(_path) and _path not in sys.path:
        sys.path.insert(0, _path)

from app.main import create_app

# Top-level ASGI entrypoint assignments explicitly recognized by Vercel
app = create_app()
application = app
handler = app
