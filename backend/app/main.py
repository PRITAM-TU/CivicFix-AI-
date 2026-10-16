"""
CivicFix AI — FastAPI Application Entry Point
"""
from __future__ import annotations

import contextlib
import asyncio
import os
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging, get_logger
from app.workers.sla_monitor import run_sla_monitor

logger = get_logger(__name__)


# ── Serverless / Vercel detection ───────────────────────────────────────────
IS_VERCEL = os.environ.get("VERCEL") == "1"


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown logic."""
    # ── Startup ──────────────────────────────────────────────
    configure_logging()
    logger.info(
        "CivicFix AI starting",
        version=settings.app_version,
        environment=settings.app_env.value,
        database_mode=settings.database_mode.value,
        ai_mode=settings.ai_mode.value,
        mcp_mode=settings.mcp_mode.value,
        serverless=IS_VERCEL,
    )

    # Initialise database (create tables if not exist)
    await init_db()
    logger.info("Database initialised", mode=settings.database_mode.value)

    # SLA background monitor — skip on Vercel (serverless has no persistent tasks)
    sla_monitor = None
    if not IS_VERCEL:
        sla_monitor = asyncio.create_task(
            run_sla_monitor(settings.sla_scan_interval_seconds),
            name="civicfix-sla-monitor",
        )
    else:
        logger.info("SLA monitor skipped — serverless environment detected")

    try:
        yield  # Application runs here
    finally:
        if sla_monitor is not None:
            sla_monitor.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await sla_monitor
        logger.info("CivicFix AI shutting down")


# ── FastAPI Application ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Factory function to create the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "CivicFix AI — Autonomous Civic Action Agent. "
            "From Citizen Report → Verified Action → Resolution."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────

    # CORS — in production allow the Vercel frontend domain
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted hosts — skip on Vercel (it manages domains internally)
    if not settings.debug and not IS_VERCEL:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.civicfix.ai", "localhost"],
        )

    # ── Routers ───────────────────────────────────────────────
    app.include_router(api_router)

    # ── Static uploads ────────────────────────────────────────
    # On Vercel, filesystem is read-only between invocations.
    # Use Cloudinary / S3 for production; local dir for dev only.
    if not IS_VERCEL:
        os.makedirs(settings.upload_dir, exist_ok=True)
        app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

    # ── Exception handlers ────────────────────────────────────

    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc: Exception):
        logger.error("Unhandled exception", error=str(exc), exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred.",
                "service": settings.app_name,
            },
        )

    return app


app = create_app()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
