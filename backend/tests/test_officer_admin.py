"""
Unit & Integration tests for Officer Tactical Command & Admin Control Modules
"""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import create_access_token
from app.main import app
from app.models.complaint import Complaint, ComplaintStatus, PriorityLevel
from app.models.department import Department
from app.models.user import User, UserRole
from app.services.admin_service import AdminService
from app.services.officer_service import OfficerService


@pytest.mark.asyncio
async def test_officer_service_queue_and_stats():
    """Verify officer queue sorting and workload calculations."""
    async with async_session_factory() as db:
        # Fetch or create officer
        res_officer = await db.execute(select(User).where(User.role == UserRole.officer).limit(1))
        officer = res_officer.scalar_one_or_none()
        if not officer:
            officer = User(
                email="officer_test@civicfix.ai",
                full_name="Officer Test",
                hashed_password="fake",
                role=UserRole.officer
            )
            db.add(officer)
            await db.commit()
            await db.refresh(officer)

        # Create a test complaint assigned to this officer
        comp = Complaint(
            citizen_id=officer.id,
            title="Broken Traffic Pole",
            description="Lying in street",
            category="traffic_signal",
            status=ComplaintStatus.assigned,
            priority=PriorityLevel.critical,
            assigned_officer_id=officer.id,
        )
        db.add(comp)
        await db.commit()

        queue = await OfficerService.get_officer_queue(session=db, officer_id=officer.id)
        assert len(queue) >= 1
        assert any(item["id"] == str(comp.id) for item in queue)
        assert "sla" in queue[0]

        stats = await OfficerService.get_officer_workload_stats(session=db, officer_id=officer.id)
        assert stats["total_cases"] >= 1
        assert "active_cases" in stats
        assert "compliance_rate" in stats


@pytest.mark.asyncio
async def test_admin_service_users_and_metrics():
    """Verify admin user listing, updating, and system telemetry."""
    async with async_session_factory() as db:
        users = await AdminService.list_users(session=db, limit=10)
        assert "total" in users
        assert len(users["items"]) >= 1

        # Test updating user status
        target_user = users["items"][0]
        updated = await AdminService.update_user(
            session=db,
            user_id=target_user["id"],
            role="officer"
        )
        assert updated["role"] == "officer"

        # System health metrics
        metrics = await AdminService.get_system_health_metrics(session=db)
        assert metrics["system_name"] == "CivicFix AI Autonomous Engine"
        assert metrics["mcp_server_status"] == "ONLINE"
        assert "metrics" in metrics


@pytest.mark.asyncio
async def test_officer_and_admin_api_endpoints_rbac():
    """Verify endpoint responses and RBAC security gates."""
    async with async_session_factory() as db:
        # Create or fetch officer, admin, and citizen
        res_admin = await db.execute(select(User).where(User.role == UserRole.admin).limit(1))
        admin_user = res_admin.scalar_one_or_none()
        if not admin_user:
            admin_user = User(email="super_admin@civicfix.ai", full_name="Admin", hashed_password="fake", role=UserRole.admin)
            db.add(admin_user)

        res_citizen = await db.execute(select(User).where(User.role == UserRole.citizen).limit(1))
        citizen_user = res_citizen.scalar_one_or_none()
        if not citizen_user:
            citizen_user = User(email="plain_citizen@civicfix.ai", full_name="Citizen", hashed_password="fake", role=UserRole.citizen)
            db.add(citizen_user)

        await db.commit()
        await db.refresh(admin_user)
        await db.refresh(citizen_user)

        admin_token = create_access_token(admin_user.id, role="admin")
        citizen_token = create_access_token(citizen_user.id, role="citizen")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Citizen should be blocked from /api/admin/users (403)
            r_forbidden = await ac.get("/api/admin/users", headers={"Authorization": f"Bearer {citizen_token}"})
            assert r_forbidden.status_code == 403

            # Admin should have full access to /api/admin/users (200)
            r_admin = await ac.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
            assert r_admin.status_code == 200
            assert "items" in r_admin.json()

            # Admin gets system metrics (200)
            r_sys = await ac.get("/api/admin/system/metrics", headers={"Authorization": f"Bearer {admin_token}"})
            assert r_sys.status_code == 200
            assert r_sys.json()["mcp_tools_active"] >= 8

            # Officer queue endpoint test with admin (admin has officer privilege)
            r_queue = await ac.get("/api/officer/queue", headers={"Authorization": f"Bearer {admin_token}"})
            assert r_queue.status_code == 200
            assert isinstance(r_queue.json(), list)
