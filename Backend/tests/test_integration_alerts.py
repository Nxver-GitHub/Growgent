"""
Integration tests for alert API endpoints and services.

Tests the full flow from API endpoints through AlertService to database.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.alert import AlertType, AlertSeverity, AgentType
from app.models.field import Field
from app.services.alert import AlertService

client = TestClient(app)


@pytest.mark.integration
class TestAlertIntegration:
    """Integration tests for alert endpoints and services."""

    @pytest.mark.asyncio
    async def test_create_alert_via_api(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test creating an alert via API endpoint."""
        alert_data = {
            "field_id": str(sample_field.id),
            "alert_type": AlertType.PSPS_WARNING.value,
            "severity": AlertSeverity.CRITICAL.value,
            "message": "Test PSPS warning alert",
            "agent_type": AgentType.PSPS_ANTICIPATION.value,
        }

        response = client.post("/api/alerts/create", json=alert_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"]["alert_type"] == AlertType.PSPS_WARNING.value
        assert data["data"]["severity"] == AlertSeverity.CRITICAL.value
        assert data["data"]["message"] == "Test PSPS warning alert"
        assert data["data"]["acknowledged"] is False

    @pytest.mark.asyncio
    async def test_list_alerts_with_filters(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test listing alerts with various filters."""
        # Create multiple alerts
        await AlertService.create_alert(
            db=db_session,
            field_id=sample_field.id,
            alert_type=AlertType.PSPS_WARNING,
            severity=AlertSeverity.CRITICAL,
            message="Critical PSPS alert",
            agent_type=AgentType.PSPS_ANTICIPATION,
        )

        await AlertService.create_alert(
            db=db_session,
            field_id=sample_field.id,
            alert_type=AlertType.WATER_SAVED_MILESTONE,
            severity=AlertSeverity.INFO,
            message="Water saved milestone",
            agent_type=AgentType.WATER_EFFICIENCY,
        )

        await db_session.commit()

        # Test filter by severity
        response = client.get(
            "/api/alerts",
            params={"severity": AlertSeverity.CRITICAL.value, "page": 1, "page_size": 20},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "alerts" in data["data"]
        assert len(data["data"]["alerts"]) >= 1
        assert all(
            alert["severity"] == AlertSeverity.CRITICAL.value
            for alert in data["data"]["alerts"]
        )

        # Test filter by alert_type
        response = client.get(
            "/api/alerts",
            params={
                "alert_type": AlertType.WATER_SAVED_MILESTONE.value,
                "page": 1,
                "page_size": 20,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["alerts"]) >= 1
        assert all(
            alert["alert_type"] == AlertType.WATER_SAVED_MILESTONE.value
            for alert in data["data"]["alerts"]
        )

    @pytest.mark.asyncio
    async def test_acknowledge_alert_via_api(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test acknowledging an alert via API endpoint."""
        # Create alert
        alert = await AlertService.create_alert(
            db=db_session,
            field_id=sample_field.id,
            alert_type=AlertType.PSPS_WARNING,
            severity=AlertSeverity.CRITICAL,
            message="Test alert to acknowledge",
            agent_type=AgentType.PSPS_ANTICIPATION,
        )
        await db_session.commit()

        # Acknowledge via API
        response = client.post(f"/api/alerts/{alert.id}/acknowledge")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["acknowledged"] is True
        assert data["data"]["acknowledged_at"] is not None

    @pytest.mark.asyncio
    async def test_get_critical_alerts(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test getting critical alerts endpoint."""
        # Create critical alert
        await AlertService.create_alert(
            db=db_session,
            field_id=sample_field.id,
            alert_type=AlertType.PSPS_WARNING,
            severity=AlertSeverity.CRITICAL,
            message="Critical alert",
            agent_type=AgentType.PSPS_ANTICIPATION,
        )
        await db_session.commit()

        response = client.get("/api/alerts/critical", params={"limit": 10})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "alerts" in data["data"]
        assert len(data["data"]["alerts"]) >= 1
        assert all(
            alert["severity"] == AlertSeverity.CRITICAL.value
            for alert in data["data"]["alerts"]
        )
        assert all(alert["acknowledged"] is False for alert in data["data"]["alerts"])

    @pytest.mark.asyncio
    async def test_alert_pagination(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test alert list pagination."""
        # Create multiple alerts
        for i in range(5):
            await AlertService.create_alert(
                db=db_session,
                field_id=sample_field.id,
                alert_type=AlertType.WATER_SAVED_MILESTONE,
                severity=AlertSeverity.INFO,
                message=f"Test alert {i}",
                agent_type=AgentType.WATER_EFFICIENCY,
            )
        await db_session.commit()

        # Test first page
        response = client.get("/api/alerts", params={"page": 1, "page_size": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["alerts"]) <= 2
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 2
        assert data["data"]["total"] >= 5

    @pytest.mark.asyncio
    async def test_create_alert_invalid_data(self) -> None:
        """Test creating alert with invalid data."""
        response = client.post(
            "/api/alerts/create",
            json={
                "alert_type": "invalid_type",
                "severity": AlertSeverity.CRITICAL.value,
                "message": "Test",
                "agent_type": AgentType.PSPS_ANTICIPATION.value,
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_acknowledge_nonexistent_alert(self) -> None:
        """Test acknowledging a non-existent alert."""
        fake_id = str(uuid4())
        response = client.post(f"/api/alerts/{fake_id}/acknowledge")

        assert response.status_code == 404

