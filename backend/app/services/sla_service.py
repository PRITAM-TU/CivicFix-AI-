"""
Autonomous SLA Monitoring & Auto-Escalation Engine
Tracks complaint resolution deadlines, predicts breach risks, and executes escalations.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.mcp.client import mcp_client
from app.models.complaint import Complaint, ComplaintStatus, ComplaintTimeline, PriorityLevel

logger = get_logger(__name__)


SLA_HOURS_MAP = {
    PriorityLevel.critical: 12,
    PriorityLevel.high: 24,
    PriorityLevel.medium: 48,
    PriorityLevel.low: 72,
}


class SLAService:
    """Computes SLA compliance metrics and executes automated escalations."""

    @staticmethod
    def calculate_sla(complaint: Complaint) -> Dict[str, Any]:
        """Compute SLA deadline, time left, and breach status for a complaint."""
        created_at = complaint.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        priority = complaint.priority or PriorityLevel.medium
        total_sla_hours = SLA_HOURS_MAP.get(priority, 48)
        deadline = created_at + timedelta(hours=total_sla_hours)

        now = datetime.now(timezone.utc)
        
        # If already resolved/rejected, use actual completion
        is_closed = complaint.status in (ComplaintStatus.resolved, ComplaintStatus.rejected)
        
        time_elapsed_seconds = max(0, (now - created_at).total_seconds())
        time_remaining_seconds = (deadline - now).total_seconds()
        total_sla_seconds = total_sla_hours * 3600

        percent_consumed = min(100.0, max(0.0, (time_elapsed_seconds / total_sla_seconds) * 100))
        hours_remaining = round(time_remaining_seconds / 3600, 1)

        if is_closed:
            sla_status = "RESOLVED"
            risk_level = "NONE"
        elif time_remaining_seconds <= 0:
            sla_status = "BREACHED"
            risk_level = "CRITICAL"
        elif percent_consumed >= 75.0 or hours_remaining <= (total_sla_hours * 0.25):
            sla_status = "AT_RISK"
            risk_level = "HIGH"
        else:
            sla_status = "ON_TRACK"
            risk_level = "LOW"

        return {
            "complaint_id": str(complaint.id),
            "priority": priority.value,
            "total_sla_hours": total_sla_hours,
            "created_at": created_at.isoformat(),
            "deadline": deadline.isoformat(),
            "hours_remaining": hours_remaining,
            "seconds_remaining": max(0, int(time_remaining_seconds)),
            "percent_consumed": round(percent_consumed, 1),
            "sla_status": sla_status,
            "risk_level": risk_level,
            "is_closed": is_closed,
        }

    @staticmethod
    async def escalate_complaint(
        session: AsyncSession,
        complaint: Complaint,
        reason: str = "Autonomous SLA Proximity Alert",
        tier: str = "TIER_1_SUPERVISOR"
    ) -> Dict[str, Any]:
        """Trigger formal escalation, log audit note, and dispatch officer emergency alert via MCP."""
        now = datetime.now(timezone.utc)
        
        # Disallow redundant escalations if already resolved
        if complaint.status in (ComplaintStatus.resolved, ComplaintStatus.rejected):
            return {"status": "SKIPPED", "message": "Complaint is already resolved/closed"}

        # Optional priority bump if medium
        if complaint.priority == PriorityLevel.medium:
            complaint.priority = PriorityLevel.high

        tracking_code = str(complaint.id)[:8].upper()
        escalation_note = (
            f"⚠️ AUTONOMOUS SLA ESCALATION ({tier}): {reason}. "
            f"Priority calibrated to {complaint.priority.value.upper()}. "
            f"Dispatched automated alert to municipal command staff."
        )

        timeline_entry = ComplaintTimeline(
            complaint_id=complaint.id,
            status=complaint.status,
            note=escalation_note,
        )
        session.add(timeline_entry)
        await session.commit()

        # Send alert via MCP
        mcp_alert = {}
        mcp_alert_error = None
        try:
            mcp_alert = await mcp_client.call_tool("notify_officer_emergency_alert", {
                "alert_title": f"SLA ESCALATION: Complaint {tracking_code}",
                "hazard_description": reason,
                "sla_hours_left": 1.5,
            })
        except Exception as exc:
            mcp_alert_error = str(exc)
            logger.exception(
                "Failed to dispatch SLA escalation alert",
                complaint_id=str(complaint.id),
                tier=tier,
            )

        return {
            "status": "ESCALATED",
            "tier": tier,
            "complaint_id": str(complaint.id),
            "tracking_id": tracking_code,
            "new_priority": complaint.priority.value,
            "escalated_at": now.isoformat(),
            "mcp_alert": mcp_alert,
            "mcp_alert_error": mcp_alert_error,
        }

    @staticmethod
    async def scan_and_auto_escalate(session: AsyncSession) -> Dict[str, Any]:
        """Scan all active complaints and automatically trigger escalations for AT_RISK or BREACHED cases."""
        stmt = (
            select(Complaint)
            .where(Complaint.status.in_([ComplaintStatus.pending, ComplaintStatus.in_progress, ComplaintStatus.assigned]))
            .options(selectinload(Complaint.timeline))
        )
        result = await session.execute(stmt)
        complaints = result.scalars().all()

        total_scanned = len(complaints)
        escalated_count = 0
        details = []
        recorded_escalations = session.info.setdefault("sla_escalations_recorded", set())

        for c in complaints:
            sla_info = SLAService.calculate_sla(c)
            if sla_info["sla_status"] in ("AT_RISK", "BREACHED"):
                tier = "TIER_2_DIRECTOR" if sla_info["sla_status"] == "BREACHED" else "TIER_1_SUPERVISOR"
                escalation_key = (str(c.id), tier)
                already_escalated = any(
                    event.note
                    and "AUTONOMOUS SLA ESCALATION" in event.note
                    and f"({tier})" in event.note
                    for event in c.timeline
                )
                if already_escalated or escalation_key in recorded_escalations:
                    continue

                reason = f"SLA {sla_info['sla_status']}: {sla_info['hours_remaining']}h remaining ({sla_info['percent_consumed']}% consumed)"
                result = await SLAService.escalate_complaint(session, c, reason=reason, tier=tier)
                if result["status"] != "ESCALATED":
                    continue

                recorded_escalations.add(escalation_key)
                escalated_count += 1
                details.append({
                    "tracking_id": str(c.id)[:8].upper(),
                    "status": sla_info["sla_status"],
                    "tier": tier,
                    "hours_remaining": sla_info["hours_remaining"]
                })

        return {
            "total_scanned": total_scanned,
            "escalated_count": escalated_count,
            "escalations": details,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    async def get_sla_overview(session: AsyncSession) -> Dict[str, Any]:
        """City-wide SLA performance summary."""
        stmt = select(Complaint).options(selectinload(Complaint.timeline))
        result = await session.execute(stmt)
        all_complaints = result.scalars().all()

        total = len(all_complaints)
        on_track = 0
        at_risk = 0
        breached = 0
        resolved_count = 0

        for c in all_complaints:
            sla = SLAService.calculate_sla(c)
            if sla["sla_status"] == "RESOLVED":
                resolved_count += 1
            elif sla["sla_status"] == "BREACHED":
                breached += 1
            elif sla["sla_status"] == "AT_RISK":
                at_risk += 1
            else:
                on_track += 1

        active_count = on_track + at_risk + breached
        compliance_rate = round(((on_track + resolved_count) / max(1, total)) * 100, 1)

        return {
            "total_complaints": total,
            "active_complaints": active_count,
            "on_track": on_track,
            "at_risk": at_risk,
            "breached": breached,
            "resolved": resolved_count,
            "sla_compliance_rate": compliance_rate,
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        }
