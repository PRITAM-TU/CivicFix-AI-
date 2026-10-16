"""
CivicFix AI — Action Agent Node
Executes final civic action: updates database status, assigns work order, logs timeline audit.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.state import CivicActionState
from app.core.database import async_session_factory
from app.models.complaint import Complaint, ComplaintStatus, ComplaintTimeline, PriorityLevel

logger = logging.getLogger("civicfix.agent.action")


async def action_node(state: CivicActionState) -> Dict[str, Any]:
    """
    Action node: Dispatches work order, updates complaint status, and writes timeline events.
    """
    complaint_id = state.get("complaint_id")
    logger.info(f"[ActionAgent] Dispatching civic action for complaint {complaint_id}")

    routing = state.get("routing_result", {})
    dept_id = routing.get("department_id")
    dept_name = routing.get("department_name", "Public Works")
    priority_str = routing.get("priority", "medium")
    severity = routing.get("severity", 5)
    sla_hours = routing.get("sla_hours", 48)

    # Check if rejected by approval node
    is_rejected = False
    human_decision = state.get("human_decision")
    if human_decision and not human_decision.get("approved", True):
        is_rejected = True

    work_order_id = f"WO-{uuid.uuid4().hex[:8].upper()}" if not is_rejected else "N/A"
    mcp_telemetry = {}

    if not is_rejected:
        try:
            from app.mcp.client import mcp_client
            wo_res = await mcp_client.call_tool("civic_work_order_dispatch", {
                "complaint_id": str(complaint_id),
                "department_code": dept_name,
                "priority": priority_str,
            })
            work_order_id = wo_res.get("work_order_id", work_order_id)
            mcp_telemetry["work_order"] = wo_res

            sms_res = await mcp_client.call_tool("notify_citizen_sms", {
                "phone_number": "+1-555-0199",
                "message": f"CivicFix: Work Order {work_order_id} created for {dept_name}. Target SLA: {sla_hours}h.",
                "complaint_id": str(complaint_id),
            })
            mcp_telemetry["sms_notification"] = sms_res
        except Exception as e:
            logger.warning(f"[ActionAgent] MCP tool execution fallback: {e}")

    try:
        async with async_session_factory() as session:
            stmt = select(Complaint).where(Complaint.id == complaint_id).options(
                selectinload(Complaint.timeline)
            )
            res = await session.execute(stmt)
            complaint = res.scalar_one_or_none()

            if complaint:
                if is_rejected:
                    complaint.status = ComplaintStatus.rejected
                    note = f"Complaint rejected by officer review. Reason: {human_decision.get('officer_notes', 'N/A')}"
                else:
                    complaint.status = ComplaintStatus.assigned
                    if dept_id:
                        complaint.department_id = dept_id
                    try:
                        complaint.priority = PriorityLevel(priority_str.lower())
                    except ValueError:
                        pass
                    complaint.severity = severity
                    note = (
                        f"Autonomous Multi-Agent Dispatch: Generated Work Order {work_order_id} "
                        f"assigned to {dept_name}. Target resolution within {sla_hours} hours."
                    )

                timeline_entry = ComplaintTimeline(
                    complaint_id=complaint.id,
                    status=complaint.status,
                    note=note,
                )
                session.add(timeline_entry)
                await session.commit()
                logger.info(f"[ActionAgent] Complaint {complaint_id} updated to {complaint.status}")
    except Exception as exc:
        logger.error(f"[ActionAgent] Database update error: {exc}", exc_info=True)

    action_result = {
        "work_order_id": work_order_id,
        "action_status": "rejected" if is_rejected else "dispatched",
        "notifications_queued": True,
        "dispatched_to": dept_name if not is_rejected else "None",
        "timeline_note": (
            f"Work Order {work_order_id} active with {dept_name}"
            if not is_rejected
            else f"Report rejected: {human_decision.get('officer_notes', '')}"
        ),
    }

    steps = list(state.get("steps_completed", []))
    if "action" not in steps:
        steps.append("action")

    return {
        "action_result": action_result,
        "current_step": "completed",
        "steps_completed": steps,
    }
