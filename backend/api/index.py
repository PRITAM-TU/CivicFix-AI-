"""
CivicFix AI — Vercel Serverless Entry Point
Exports the FastAPI ASGI app for Vercel's Python runtime.
"""
from __future__ import annotations

import os
import sys
import traceback

# Ensure all plausible backend root paths are on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

for candidate in [
    parent_dir,
    current_dir,
    os.path.join(parent_dir, "backend"),
    "/var/task",
    "/var/task/backend",
]:
    if os.path.exists(candidate) and candidate not in sys.path:
        sys.path.insert(0, candidate)

try:
    from app.main import app  # noqa: F401
except Exception as exc:
    # Diagnostic fallback: if importing app fails on Vercel, return detailed JSON error
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="CivicFix AI - Startup Diagnostics")
    _err_str = str(exc)
    _tb_lines = traceback.format_exc().splitlines()

    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def diagnostic_handler(path_name: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "FastAPI Startup Failed on Vercel",
                "detail": _err_str,
                "traceback": _tb_lines,
                "sys_path": sys.path,
                "cwd": os.getcwd(),
            },
        )
