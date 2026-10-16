"""
CivicFix AI — Complaint & Media Models
Defines Complaint, ComplaintMedia, and ComplaintTimeline entities.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.department import Department  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.ai_analysis import AIAnalysis  # noqa: F401


# ── Enums ────────────────────────────────────────────────────────────────────

class ComplaintCategory(str, PyEnum):
    pothole = "pothole"
    garbage = "garbage"
    water_leakage = "water_leakage"
    street_light = "street_light"
    drainage = "drainage"
    traffic_signal = "traffic_signal"
    encroachment = "encroachment"
    other = "other"


class ComplaintStatus(str, PyEnum):
    pending = "pending"
    analyzing = "analyzing"
    verified = "verified"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"


class PriorityLevel(str, PyEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ComplaintSource(str, PyEnum):
    web = "web"
    mobile = "mobile"
    voice = "voice"
    whatsapp = "whatsapp"


class MediaType(str, PyEnum):
    image = "image"
    audio = "audio"
    video = "video"
    document = "document"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Models ───────────────────────────────────────────────────────────────────

class Complaint(Base):
    """
    Core civic issue report submitted by a citizen.
    """
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    citizen_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped[ComplaintCategory] = mapped_column(
        Enum(ComplaintCategory),
        nullable=False,
        default=ComplaintCategory.other,
        index=True,
    )
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus),
        nullable=False,
        default=ComplaintStatus.pending,
        index=True,
    )
    priority: Mapped[PriorityLevel] = mapped_column(
        Enum(PriorityLevel),
        nullable=False,
        default=PriorityLevel.medium,
        index=True,
    )
    severity: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # Scale 1-10

    # Geospatial data
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    landmark: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Department & Officer Routing
    department_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_officer_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    source: Mapped[ComplaintSource] = mapped_column(
        Enum(ComplaintSource), default=ComplaintSource.web, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    media: Mapped[List[ComplaintMedia]] = relationship(
        "ComplaintMedia", back_populates="complaint", cascade="all, delete-orphan", lazy="selectin"
    )
    timeline: Mapped[List[ComplaintTimeline]] = relationship(
        "ComplaintTimeline", back_populates="complaint", cascade="all, delete-orphan", lazy="selectin", order_by="ComplaintTimeline.created_at"
    )
    ai_analysis: Mapped[Optional["AIAnalysis"]] = relationship(
        "AIAnalysis", back_populates="complaint", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Complaint id={self.id} title={self.title[:20]} status={self.status}>"


class ComplaintMedia(Base):
    """
    Media attachments (photos, audio notes, docs) for a complaint.
    """
    __tablename__ = "complaint_media"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complaint_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True
    )

    media_type: Mapped[MediaType] = mapped_column(
        Enum(MediaType), default=MediaType.image, nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_resolution_evidence: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="media")

    def __repr__(self) -> str:
        return f"<ComplaintMedia id={self.id} type={self.media_type} url={self.file_url}>"


class ComplaintTimeline(Base):
    """
    Lifecycle status progression audit trail for a complaint.
    """
    __tablename__ = "complaint_timeline"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    complaint_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus), nullable=False
    )
    changed_by_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="timeline")

    def __repr__(self) -> str:
        return f"<ComplaintTimeline id={self.id} status={self.status}>"
