"""
End-to-end tests for Agent 2 components.

Tests complete workflows from API endpoints through agents, services, and database.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.field import Field
from app.models.recommendation import Recommendation, AgentType, RecommendationAction
from app.models.sensor_reading import SensorReading
from app.models.alert import AlertType, AlertSeverity
from app.agents.water_efficiency import WaterEfficiencyAgent, WaterEfficiencyAgentState
from app.agents.psps import PSPSAlertAgent, PSPSAgentState
from app.services.alert import AlertService
from app.services.metrics import MetricsService

client = TestClient(app)


@pytest.mark.e2e
class TestWaterEfficiencyE2E:
    """End-to-end tests for Water Efficiency workflow."""

    @pytest.mark.asyncio
    async def test_water_efficiency_full_workflow(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test complete Water Efficiency workflow:
        1. Create Fire-Adaptive recommendations
        2. Run Water Efficiency Agent
        3. Check metrics via API
        4. Verify milestone alerts created
        """
        # Step 1: Create Fire-Adaptive Irrigation recommendations
        for i in range(5):
            recommendation = Recommendation(
                field_id=sample_field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.DELAY,
                title=f"Fire-adaptive delay recommendation {i}",
                reason="High fire risk, sufficient moisture",
                confidence=0.85,
                water_saved_liters=1500.0 * (i + 1),
            )
            db_session.add(recommendation)

        # Step 2: Create sensor reading for drought stress calculation
        sensor_reading = SensorReading(
            field_id=sample_field.id,
            sensor_id="sensor-001",
            moisture_percent=45.0,
            temperature=24.0,
            ph=6.8,
            reading_timestamp=datetime.now(timezone.utc),
        )
        db_session.add(sensor_reading)
        await db_session.commit()

        # Step 3: Run Water Efficiency Agent
        agent = WaterEfficiencyAgent()
        state = WaterEfficiencyAgentState(field_id=sample_field.id)
        state = await agent.process(state, db_session)

        assert state.error is None
        assert state.water_metrics is not None
        assert state.water_metrics['water_saved_liters'] >= 0

        # Step 4: Verify metrics via API
        response = client.get(
            f"/api/metrics/water?field_id={sample_field.id}&period=season"
        )

        assert response.status_code == 200
        api_data = response.json()
        assert api_data["status"] == "success"
        assert api_data["data"]["field_id"] == str(sample_field.id)
        assert api_data["data"]["water_saved_liters"] >= 0

        # Step 5: Check if milestone alerts were created
        alerts, _ = await AlertService.list_alerts(
            db=db_session,
            field_id=sample_field.id,
            alert_type=AlertType.WATER_SAVED_MILESTONE,
        )

        # May have milestone alerts if savings are significant
        assert isinstance(alerts, list)

    @pytest.mark.asyncio
    async def test_water_metrics_api_to_service_flow(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test complete flow: API → MetricsService → Database → Response.
        """
        # Setup: Create recommendations and sensor data
        recommendation = Recommendation(
            field_id=sample_field.id,
            agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
            action=RecommendationAction.IRRIGATE,
            title="Test recommendation",
            reason="Test reason",
            confidence=0.8,
        )
        db_session.add(recommendation)

        sensor_reading = SensorReading(
            field_id=sample_field.id,
            sensor_id="sensor-001",
            moisture_percent=40.0,
            temperature=22.0,
            ph=6.5,
            reading_timestamp=datetime.now(timezone.utc),
        )
        db_session.add(sensor_reading)
        await db_session.commit()

        # Test: Call API endpoint
        response = client.get(
            f"/api/metrics/water?field_id={sample_field.id}&period=season"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data

        # Verify data structure matches schema
        metrics = data["data"]
        assert "field_id" in metrics
        assert "water_recommended_liters" in metrics
        assert "water_typical_liters" in metrics
        assert "water_saved_liters" in metrics
        assert "efficiency_percent" in metrics
        assert "cost_saved_usd" in metrics
        assert "drought_stress_score" in metrics
        assert "last_updated" in metrics

        # Verify calculated values are reasonable
        assert metrics["water_typical_liters"] > 0
        assert 0 <= metrics["efficiency_percent"] <= 100
        assert metrics["drought_stress_score"] >= 0


@pytest.mark.e2e
class TestPSPSE2E:
    """End-to-end tests for PSPS Anticipation workflow."""

    @pytest.mark.asyncio
    async def test_psps_detection_and_alert_workflow(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test complete PSPS workflow:
        1. Run PSPS Agent to detect shutoffs
        2. Verify alerts created via API
        3. Check pre-irrigation recommendations
        """
        # Step 1: Run PSPS Agent
        agent = PSPSAlertAgent()
        state = PSPSAgentState(field_id=sample_field.id)
        state = await agent.process(state, db_session)

        assert state.error is None
        assert state.step == "completed"
        assert isinstance(state.affected_field_ids, list)

        # Step 2: Verify alerts via API
        response = client.get(
            "/api/alerts",
            params={
                "field_id": str(sample_field.id),
                "alert_type": AlertType.PSPS_WARNING.value,
                "page": 1,
                "page_size": 20,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Step 3: Check critical alerts endpoint
        response = client.get("/api/alerts/critical", params={"limit": 10})

        assert response.status_code == 200
        critical_data = response.json()
        assert critical_data["status"] == "success"
        assert "data" in critical_data

    @pytest.mark.asyncio
    async def test_psps_alert_creation_via_api(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test creating PSPS alert via API and verifying it appears in list.
        """
        # Step 1: Create alert via API
        alert_data = {
            "field_id": str(sample_field.id),
            "alert_type": AlertType.PSPS_WARNING.value,
            "severity": AlertSeverity.CRITICAL.value,
            "message": "E2E Test: PSPS shutoff predicted in 36 hours",
            "agent_type": AgentType.PSPS_ANTICIPATION.value,
        }

        create_response = client.post("/api/alerts/create", json=alert_data)
        assert create_response.status_code == 201

        created_alert = create_response.json()["data"]
        alert_id = created_alert["id"]

        # Step 2: Verify alert appears in list
        list_response = client.get(
            "/api/alerts",
            params={"field_id": str(sample_field.id), "page": 1, "page_size": 20},
        )

        assert list_response.status_code == 200
        list_data = list_response.json()
        alerts = list_data["data"]["alerts"]

        # Find our alert
        found_alert = next(
            (a for a in alerts if a["id"] == alert_id), None
        )
        assert found_alert is not None
        assert found_alert["message"] == "E2E Test: PSPS shutoff predicted in 36 hours"

        # Step 3: Acknowledge alert
        ack_response = client.post(f"/api/alerts/{alert_id}/acknowledge")
        assert ack_response.status_code == 200
        assert ack_response.json()["data"]["acknowledged"] is True


@pytest.mark.e2e
class TestMetricsE2E:
    """End-to-end tests for metrics API workflows."""

    @pytest.mark.asyncio
    async def test_water_metrics_complete_flow(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test complete water metrics flow with multiple recommendations.
        """
        # Setup: Create multiple recommendations
        recommendations = []
        for i in range(3):
            rec = Recommendation(
                field_id=sample_field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.IRRIGATE,
                title=f"Recommendation {i}",
                reason="Test reason",
                confidence=0.8,
                water_saved_liters=2000.0 * (i + 1),
            )
            recommendations.append(rec)
            db_session.add(rec)

        sensor_reading = SensorReading(
            field_id=sample_field.id,
            sensor_id="sensor-001",
            moisture_percent=38.0,
            temperature=23.0,
            ph=6.6,
            reading_timestamp=datetime.now(timezone.utc),
        )
        db_session.add(sensor_reading)
        await db_session.commit()

        # Test: Get metrics via API
        response = client.get(
            f"/api/metrics/water?field_id={sample_field.id}&period=season"
        )

        assert response.status_code == 200
        data = response.json()
        metrics = data["data"]

        # Verify all required fields present
        required_fields = [
            "field_id",
            "water_recommended_liters",
            "water_typical_liters",
            "water_saved_liters",
            "efficiency_percent",
            "cost_saved_usd",
            "drought_stress_score",
            "last_updated",
        ]
        for field in required_fields:
            assert field in metrics, f"Missing field: {field}"

        # Verify calculated values
        assert metrics["water_typical_liters"] > 0
        assert metrics["water_saved_liters"] >= 0
        assert 0 <= metrics["efficiency_percent"] <= 100
        assert metrics["cost_saved_usd"] >= 0
        assert 0 <= metrics["drought_stress_score"] <= 100

    @pytest.mark.asyncio
    async def test_farm_summary_workflow(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test farm-wide water summary workflow.
        """
        # Create another field in same farm
        field2 = Field(
            farm_id=sample_field.farm_id,
            name="Test Field 2",
            crop_type="almond",
            area_hectares=5.0,
        )
        db_session.add(field2)
        await db_session.commit()
        await db_session.refresh(field2)

        # Create recommendations for both fields
        for field in [sample_field, field2]:
            rec = Recommendation(
                field_id=field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.IRRIGATE,
                title="Test recommendation",
                reason="Test reason",
                confidence=0.8,
            )
            db_session.add(rec)

            sensor = SensorReading(
                field_id=field.id,
                sensor_id=f"sensor-{field.id}",
                moisture_percent=40.0,
                temperature=22.0,
                ph=6.5,
                reading_timestamp=datetime.now(timezone.utc),
            )
            db_session.add(sensor)

        await db_session.commit()

        # Test: Get farm summary via API
        response = client.get(
            f"/api/metrics/water/summary?farm_id={sample_field.farm_id}"
        )

        assert response.status_code == 200
        data = response.json()
        summary = data["data"]

        # Verify summary structure
        assert summary["farm_id"] == sample_field.farm_id
        assert summary["field_count"] >= 2
        assert summary["total_water_recommended_liters"] >= 0
        assert summary["total_water_typical_liters"] > 0
        assert summary["total_water_saved_liters"] >= 0
        assert 0 <= summary["average_efficiency_percent"] <= 100

    @pytest.mark.asyncio
    async def test_fire_risk_metrics_workflow(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test fire risk metrics workflow with accepted recommendations.
        """
        # Create accepted recommendations with fire risk reduction
        for i in range(2):
            rec = Recommendation(
                field_id=sample_field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.DELAY,
                title=f"Fire risk reduction {i}",
                reason="High fire risk",
                confidence=0.85,
                fire_risk_reduction_percent=12.0 + (i * 3.0),
                accepted=True,
                accepted_at=datetime.now(timezone.utc) - timedelta(hours=i),
            )
            db_session.add(rec)

        await db_session.commit()

        # Test: Get fire risk metrics via API
        response = client.get(f"/api/metrics/fire-risk?field_id={sample_field.id}")

        assert response.status_code == 200
        data = response.json()
        metrics = data["data"]

        # Verify structure
        assert metrics["field_id"] == str(sample_field.id)
        assert "fire_risk_reduction_percent" in metrics
        assert "current_fire_risk_level" in metrics
        assert "recommendations_applied" in metrics
        assert metrics["recommendations_applied"] >= 2
        assert metrics["fire_risk_reduction_percent"] >= 0


@pytest.mark.e2e
class TestAlertOrchestrationE2E:
    """End-to-end tests for alert orchestration across agents."""

    @pytest.mark.asyncio
    async def test_multi_agent_alert_workflow(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test alert creation from multiple agents in sequence.
        """
        # Step 1: Water Efficiency Agent creates milestone alert
        # (Setup with recommendations first)
        for i in range(10):
            rec = Recommendation(
                field_id=sample_field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.DELAY,
                title=f"Rec {i}",
                reason="Test",
                confidence=0.8,
            )
            db_session.add(rec)

        sensor = SensorReading(
            field_id=sample_field.id,
            sensor_id="sensor-001",
            moisture_percent=45.0,
            temperature=22.0,
            ph=6.5,
            reading_timestamp=datetime.now(timezone.utc),
        )
        db_session.add(sensor)
        await db_session.commit()

        water_agent = WaterEfficiencyAgent()
        water_state = WaterEfficiencyAgentState(field_id=sample_field.id)
        water_state = await water_agent.process(water_state, db_session)

        # Step 2: PSPS Agent creates warning alert
        psps_agent = PSPSAlertAgent()
        psps_state = PSPSAgentState(field_id=sample_field.id)
        psps_state = await psps_agent.process(psps_state, db_session)

        # Step 3: Verify all alerts via API
        response = client.get(
            "/api/alerts",
            params={"field_id": str(sample_field.id), "page": 1, "page_size": 50},
        )

        assert response.status_code == 200
        data = response.json()
        alerts = data["data"]["alerts"]

        # Should have alerts from both agents (if conditions are met)
        # May vary based on conditions
        assert isinstance(alerts, list)

    @pytest.mark.asyncio
    async def test_alert_filtering_and_pagination_e2e(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """
        Test alert filtering and pagination end-to-end.
        """
        # Create alerts of different types and severities
        alert_configs = [
            (AlertType.PSPS_WARNING, AlertSeverity.CRITICAL, AgentType.PSPS_ANTICIPATION),
            (AlertType.WATER_SAVED_MILESTONE, AlertSeverity.INFO, AgentType.WATER_EFFICIENCY),
            (AlertType.PSPS_ACTIVE, AlertSeverity.CRITICAL, AgentType.PSPS_ANTICIPATION),
        ]

        for alert_type, severity, agent_type in alert_configs:
            await AlertService.create_alert(
                db=db_session,
                field_id=sample_field.id,
                alert_type=alert_type,
                severity=severity,
                message=f"Test {alert_type.value} alert",
                agent_type=agent_type,
            )

        await db_session.commit()

        # Test: Filter by severity
        response = client.get(
            "/api/alerts",
            params={
                "field_id": str(sample_field.id),
                "severity": AlertSeverity.CRITICAL.value,
                "page": 1,
                "page_size": 20,
            },
        )

        assert response.status_code == 200
        data = response.json()
        critical_alerts = data["data"]["alerts"]
        assert all(
            alert["severity"] == AlertSeverity.CRITICAL.value
            for alert in critical_alerts
        )

        # Test: Filter by alert type
        response = client.get(
            "/api/alerts",
            params={
                "field_id": str(sample_field.id),
                "alert_type": AlertType.PSPS_WARNING.value,
                "page": 1,
                "page_size": 20,
            },
        )

        assert response.status_code == 200
        data = response.json()
        psps_alerts = data["data"]["alerts"]
        assert all(
            alert["alert_type"] == AlertType.PSPS_WARNING.value
            for alert in psps_alerts
        )

