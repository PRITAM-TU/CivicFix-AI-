"""
CivicFix AI — Deduplication Agent Node
Performs geospatial clustering and semantic text similarity matching to detect duplicate grievances.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from sqlalchemy import select

from app.agents.state import CivicActionState
from app.core.database import async_session_factory
from app.gis.service import haversine_distance_meters
from app.models.complaint import Complaint, ComplaintStatus

logger = logging.getLogger("civicfix.agent.deduplication")


def calculate_token_similarity(text1: str, text2: str) -> float:
    """Calculate token-level Jaccard similarity between two texts."""
    tokens1 = set(re.findall(r"\w+", text1.lower()))
    tokens2 = set(re.findall(r"\w+", text2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return len(intersection) / len(union)


async def deduplication_node(state: CivicActionState) -> Dict[str, Any]:
    """
    Deduplication node: Checks if a similar complaint exists within 100m of coordinates.
    """
    complaint_id = state.get("complaint_id")
    lat = state.get("latitude")
    lon = state.get("longitude")
    title = state.get("title", "")
    desc = state.get("description", "")
    full_text = f"{title} {desc}"

    logger.info(f"[DeduplicationAgent] Checking duplicates for complaint {complaint_id}")

    is_duplicate = False
    duplicate_of_id: Optional[str] = None
    min_dist_meters: Optional[float] = None
    max_similarity = 0.0

    # Only perform geospatial lookup if coordinates exist
    if lat is not None and lon is not None:
        try:
            async with async_session_factory() as session:
                # Query active complaints other than this one
                stmt = select(Complaint).where(
                    Complaint.id != complaint_id,
                    Complaint.status.in_([
                        ComplaintStatus.pending,
                        ComplaintStatus.analyzing,
                        ComplaintStatus.verified,
                        ComplaintStatus.assigned,
                        ComplaintStatus.in_progress,
                    ]),
                    Complaint.latitude.isnot(None),
                    Complaint.longitude.isnot(None),
                )
                res = await session.execute(stmt)
                candidates = res.scalars().all()

                for candidate in candidates:
                    if candidate.latitude is None or candidate.longitude is None:
                        continue

                    dist = haversine_distance_meters(lat, lon, candidate.latitude, candidate.longitude)
                    # If within 100 meters
                    if dist <= 100.0:
                        sim = calculate_token_similarity(full_text, f"{candidate.title} {candidate.description}")
                        # Match if same category or moderate token overlap
                        same_cat = candidate.category.value == state.get("category")
                        if (same_cat and sim >= 0.25) or sim >= 0.5:
                            is_duplicate = True
                            duplicate_of_id = candidate.id
                            min_dist_meters = round(dist, 1)
                            max_similarity = round(sim, 2)
                            break
        except Exception as exc:
            logger.warning(f"Error checking duplicate candidates in DB: {exc}")

    dedup_result = {
        "is_duplicate": is_duplicate,
        "duplicate_of_id": duplicate_of_id,
        "distance_meters": min_dist_meters,
        "similarity_score": max_similarity,
        "cluster_id": f"cluster-{duplicate_of_id[:8]}" if duplicate_of_id else None,
    }

    steps = list(state.get("steps_completed", []))
    if "deduplication" not in steps:
        steps.append("deduplication")

    return {
        "deduplication_result": dedup_result,
        "current_step": "routing",
        "steps_completed": steps,
    }
