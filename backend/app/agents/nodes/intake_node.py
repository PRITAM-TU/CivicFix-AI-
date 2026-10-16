"""
CivicFix AI — Intake Agent Node
Performs multimodal ingestion, category classification, entity extraction, and vision feature analysis.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from app.agents.state import CivicActionState
from app.core.ai.factory import get_ai_provider

logger = logging.getLogger("civicfix.agent.intake")


async def intake_node(state: CivicActionState) -> Dict[str, Any]:
    """
    Intake node: Combines complaint text, media attachments, and category hints into unified analysis.
    """
    logger.info(f"[IntakeAgent] Processing complaint: {state.get('complaint_id')}")

    full_text = f"{state.get('title', '')}\n{state.get('description', '')}"
    if state.get("landmark"):
        full_text += f"\nLandmark: {state.get('landmark')}"
    if state.get("address"):
        full_text += f"\nAddress: {state.get('address')}"

    media_urls = state.get("media_urls", [])
    first_image = media_urls[0] if media_urls else None

    provider = get_ai_provider()
    analysis = await provider.synthesize_multimodal_triage(
        text=full_text,
        image_url=first_image,
        category_hint=state.get("category"),
    )

    intake_result = {
        "summary": analysis.summary,
        "detected_category": analysis.detected_category,
        "confidence_score": analysis.confidence_score,
        "urgency_score": analysis.urgency_score,
        "severity": analysis.severity,
        "extracted_entities": analysis.extracted_entities,
        "vision_analysis": analysis.vision_analysis,
        "provider_name": analysis.provider_name,
        "model_name": analysis.model_name,
        "processing_time_ms": analysis.processing_time_ms,
    }

    steps = list(state.get("steps_completed", []))
    if "intake" not in steps:
        steps.append("intake")

    return {
        "intake_result": intake_result,
        "current_step": "validation",
        "steps_completed": steps,
    }
