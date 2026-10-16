"""
CivicFix AI — LangGraph Multi-Agent State
Defines the shared state passed across all agent nodes during civic action orchestration.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class CivicActionState(TypedDict, total=False):
    # Core complaint metadata
    complaint_id: str
    citizen_id: str
    title: str
    description: str
    category: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    landmark: Optional[str]
    media_urls: List[str]

    # Node outputs
    intake_result: Dict[str, Any]
    # {summary, detected_category, confidence_score, urgency_score, severity, extracted_entities, vision_analysis}

    validation_result: Dict[str, Any]
    # {is_valid: bool, spam_score: float, validity_reason: str, is_actionable: bool, flags: List[str]}

    deduplication_result: Dict[str, Any]
    # {is_duplicate: bool, duplicate_of_id: Optional[str], distance_meters: Optional[float], similarity_score: float, cluster_id: Optional[str]}

    routing_result: Dict[str, Any]
    # {department_id: str, department_name: str, department_code: str, priority: str, severity: int, sla_hours: int, routing_rationale: str}

    # Human-in-the-Loop (HITL) Gate
    requires_human_approval: bool
    approval_reason: str
    is_awaiting_approval: bool
    human_decision: Optional[Dict[str, Any]]
    # {approved: bool, officer_id: Optional[str], officer_notes: str, override_dept: Optional[str], override_priority: Optional[str], timestamp: str}

    # Final Action Execution
    action_result: Dict[str, Any]
    # {work_order_id: str, action_status: str, notifications_queued: bool, dispatched_to: str, timeline_note: str}

    # Workflow tracing
    current_step: str
    steps_completed: List[str]
    errors: List[str]
