"""
CivicFix AI — Complaints API Router
Endpoints for submitting, retrieving, updating, and attaching media to civic complaints.
"""
from __future__ import annotations

import os
import shutil
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from app.api.deps import CurrentUser, DBSession, OptionalUser
from app.core.config import settings
from app.core.logging import get_logger
from app.models.complaint import (
    ComplaintCategory,
    ComplaintStatus,
    MediaType,
    PriorityLevel,
)
from app.schemas.complaint import (
    ComplaintCreateRequest,
    ComplaintListResponse,
    ComplaintOut,
    ComplaintUpdateRequest,
    UploadMediaResponse,
)
from app.services.complaint_service import (
    ComplaintNotFoundError,
    ComplaintService,
    UnauthorizedComplaintActionError,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/complaints", tags=["complaints"])

# Ensure uploads directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


# ── File Upload ───────────────────────────────────────────────────────────────

ALLOWED_MIME_TYPES = {
    "image/jpeg": MediaType.image,
    "image/png": MediaType.image,
    "image/webp": MediaType.image,
    "image/gif": MediaType.image,
    "audio/mpeg": MediaType.audio,
    "audio/wav": MediaType.audio,
    "audio/webm": MediaType.audio,
    "audio/ogg": MediaType.audio,
    "audio/mp4": MediaType.audio,
    "application/pdf": MediaType.document,
}


@router.post(
    "/upload",
    response_model=UploadMediaResponse,
    summary="Upload media evidence (image or audio) for a complaint",
)
async def upload_media(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
) -> UploadMediaResponse:
    """
    Accepts multipart file upload, validates mime type and size,
    saves file to storage, and returns static URL and metadata.
    """
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported media type: {content_type}. Allowed: JPEG, PNG, WEBP, MP3, WAV, WEBM.",
        )

    # Generate unique filename to avoid collision
    ext = os.path.splitext(file.filename or "")[1].lower()
    if not ext:
        ext = ".jpg" if "image" in content_type else ".wav"

    unique_filename = f"{uuid.uuid4().hex[:12]}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        logger.error("File upload failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file.",
        )

    file_size = os.path.getsize(file_path)
    if file_size > settings.max_upload_bytes:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.max_upload_size_mb}MB.",
        )

    file_url = f"/uploads/{unique_filename}"
    media_type = ALLOWED_MIME_TYPES[content_type]

    logger.info(
        "Media uploaded",
        filename=unique_filename,
        size_bytes=file_size,
        type=media_type.value,
    )

    return UploadMediaResponse(
        file_url=file_url,
        file_name=file.filename or unique_filename,
        file_size=file_size,
        mime_type=content_type,
        media_type=media_type,
    )


# ── Create Complaint ──────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ComplaintOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new civic complaint",
)
async def create_complaint(
    body: ComplaintCreateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ComplaintOut:
    """
    Create a new complaint record with media and initial timeline audit entry.
    """
    svc = ComplaintService(db)
    complaint = await svc.create_complaint(body, citizen_id=current_user.id)
    return ComplaintOut.model_validate(complaint)


# ── List Complaints ───────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=ComplaintListResponse,
    summary="List complaints with optional filtering and pagination",
)
async def list_complaints(
    db: DBSession,
    current_user: OptionalUser = None,
    category: Optional[ComplaintCategory] = None,
    status: Optional[ComplaintStatus] = None,
    priority: Optional[PriorityLevel] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ComplaintListResponse:
    svc = ComplaintService(db)
    items, total, pages = await svc.list_complaints(
        category=category,
        status=status,
        priority=priority,
        page=page,
        limit=limit,
    )
    return ComplaintListResponse(
        items=[ComplaintOut.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


# ── My Complaints ─────────────────────────────────────────────────────────────

@router.get(
    "/my",
    response_model=ComplaintListResponse,
    summary="List complaints submitted by current authenticated user",
)
async def list_my_complaints(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ComplaintListResponse:
    svc = ComplaintService(db)
    items, total, pages = await svc.list_complaints(
        citizen_id=current_user.id,
        page=page,
        limit=limit,
    )
    return ComplaintListResponse(
        items=[ComplaintOut.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/my/summary",
    summary="Get count summary for citizen dashboard",
)
async def get_my_complaints_summary(
    current_user: CurrentUser,
    db: DBSession,
):
    svc = ComplaintService(db)
    return await svc.get_citizen_summary(citizen_id=current_user.id)


# ── Get Detail ────────────────────────────────────────────────────────────────

@router.get(
    "/{complaint_id}",
    response_model=ComplaintOut,
    summary="Get full complaint detail with media and timeline history",
)
async def get_complaint(
    complaint_id: str,
    db: DBSession,
    current_user: OptionalUser = None,
) -> ComplaintOut:
    svc = ComplaintService(db)
    try:
        complaint = await svc.get_by_id(complaint_id)
        return ComplaintOut.model_validate(complaint)
    except ComplaintNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ── Update Complaint ──────────────────────────────────────────────────────────

@router.patch(
    "/{complaint_id}",
    response_model=ComplaintOut,
    summary="Update complaint details or status (officer/admin or owner if pending)",
)
async def update_complaint(
    complaint_id: str,
    body: ComplaintUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ComplaintOut:
    svc = ComplaintService(db)
    try:
        updated = await svc.update_complaint(complaint_id, body, current_user)
        return ComplaintOut.model_validate(updated)
    except ComplaintNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except UnauthorizedComplaintActionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


# ── AI Analysis Endpoint ─────────────────────────────────────────────────────

@router.post(
    "/{complaint_id}/analyze",
    response_model=ComplaintOut,
    summary="Trigger autonomous AI triage & multimodal understanding for a complaint",
)
async def trigger_ai_triage(
    complaint_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> ComplaintOut:
    from app.services.ai_service import AIService
    record = await AIService.analyze_and_enrich_complaint(complaint_id, db, re_analyze=True)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Complaint {complaint_id} not found")
    svc = ComplaintService(db)
    complaint = await svc.get_by_id(complaint_id)
    return ComplaintOut.model_validate(complaint)
