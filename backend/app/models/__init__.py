"""
CivicFix AI — Models package.
Import all models here so SQLAlchemy metadata is populated.
"""
from __future__ import annotations


def _import_all_models() -> None:
    """
    Lazy import of all ORM models.
    Called by database.init_db() to ensure all tables are registered
    with Base.metadata before create_all() is invoked.
    """
    from app.models.user import User  # noqa: F401 — Phase 2
    from app.models.department import Department  # noqa: F401 — Phase 3
    from app.models.complaint import (  # noqa: F401 — Phase 3
        Complaint,
        ComplaintMedia,
        ComplaintTimeline,
    )
    from app.models.ai_analysis import AIAnalysis  # noqa: F401 — Phase 4
