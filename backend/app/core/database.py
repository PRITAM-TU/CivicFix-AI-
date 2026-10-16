"""
CivicFix AI — Database Layer
Abstraction over SQLite (dev) and PostgreSQL + PostGIS (prod).
"""
from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import AppEnv, settings


# ── Base class for all ORM models ────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Engine factory ───────────────────────────────────────────────────────────

def _build_engine():
    """
    Build an async SQLAlchemy engine from DATABASE_URL.

    SQLite:
        - Uses aiosqlite driver
        - Automatically adds check_same_thread=False
        - Returns synchronous-compatible async engine

    PostgreSQL:
        - Uses psycopg async driver
        - Supports PostGIS via geoalchemy2
    """
    url = settings.database_url

    is_vercel = os.environ.get("VERCEL") == "1"

    if settings.is_sqlite:
        # On Vercel / serverless, filesystem is read-only except /tmp
        if is_vercel and ("/tmp" not in url):
            url = "sqlite+aiosqlite:////tmp/civicfix.db"
        elif url.startswith("sqlite:///") and "+aiosqlite" not in url:
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///")

        engine = create_async_engine(
            url,
            echo=settings.debug,
            connect_args={"check_same_thread": False},
        )
    else:
        # PostgreSQL — ensure psycopg async driver
        if url.startswith("postgresql://") or url.startswith("postgresql+psycopg://"):
            if "+asyncpg" not in url and "+psycopg" not in url:
                url = url.replace("postgresql://", "postgresql+psycopg://")

        engine = create_async_engine(
            url,
            echo=settings.debug,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )

    return engine


engine = _build_engine()

# ── Session factory ──────────────────────────────────────────────────────────

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Convenience alias for background tasks and agent pipelines
async_session_factory = AsyncSessionLocal


# ── Dependency injection helper ───────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session.

    Usage:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Database initialisation ───────────────────────────────────────────────────

async def init_db() -> None:
    """
    Create missing tables and seed demo data outside production.
    Production schema changes are applied with Alembic.
    """
    async with engine.begin() as conn:
        # Import all models so Base.metadata knows about them
        from app.models import _import_all_models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

    is_vercel = os.environ.get("VERCEL") == "1"
    auto_seed = os.environ.get("AUTO_SEED", "").lower() in ("true", "1", "yes")

    if settings.app_env != AppEnv.production or (is_vercel and settings.is_sqlite) or auto_seed:
        async with AsyncSessionLocal() as session:
            try:
                from app.core.seed import seed_all
                await seed_all(session)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
