"""
CivicFix AI — Vercel Serverless Entry Point
This file exports the FastAPI ASGI app for Vercel's Python runtime.
"""
import sys
import os

# Ensure the backend directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: F401 — Vercel imports `app` from this module
