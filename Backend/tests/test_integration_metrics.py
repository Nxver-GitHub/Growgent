"""
Integration tests for metrics API endpoints and services.

Tests the full flow from API endpoints through MetricsService to database.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.field import Field
from app.models.recommendation import Recommendation, AgentType, RecommendationAction
from app.models.sensor_reading import SensorReading
from app.services.metrics import MetricsService

client = TestClient(app)


@pytest.mark.integration
class TestMetricsIntegration:
    """Integration tests for metrics endpoints and services."""

    @pytest.mark.asyncio
    async def test_get_water_metrics_via_api(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test getting water metrics via API endpoint."""
        # Create a sensor reading for drought stress calculation
        sensor_reading = SensorReading(
            field_id=sample_field.id,
            sensor_id="sensor-001",
            moisture_percent=35.0,
            temperature=22.0,
            ph=6.5,
            reading_timestamp=datetime.now(timezone.utc),
        )
        db_session.add(sensor_reading)
        await db_session.commit()

        response = client.get(
            f"/api/metrics/water?field_id={sample_field.id}&period=season"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "field_id" in data["data"]
        assert "water_recommended_liters" in data["data"]
        assert "water_typical_liters" in data["data"]
        assert "water_saved_liters" in data["data"]
        assert "efficiency_percent" in data["data"]
        assert "cost_saved_usd" in data["data"]
        assert "drought_stress_score" in data["data"]
        assert "last_updated" in data["data"]

        # Validate data types and ranges
        assert isinstance(data["data"]["water_recommended_liters"], int)
        assert isinstance(data["data"]["water_typical_liters"], int)
        assert isinstance(data["data"]["water_saved_liters"], int)
        assert 0 <= data["data"]["efficiency_percent"] <= 100
        assert data["data"]["drought_stress_score"] >= 0

    @pytest.mark.asyncio
    async def test_get_water_metrics_different_periods(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test getting water metrics for different time periods."""
        periods = ["season", "month", "week", "all"]

        for period in periods:
            response = client.get(
                f"/api/metrics/water?field_id={sample_field.id}&period={period}"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_water_metrics_invalid_period(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test getting water metrics with invalid period."""
        response = client.get(
            f"/api/metrics/water?field_id={sample_field.id}&period=invalid"
        )

        assert response.status_code == 400
        assert "Period must be one of" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_water_metrics_nonexistent_field(self) -> None:
        """Test getting water metrics for non-existent field."""
        fake_id = str(uuid4())
        response = client.get(f"/api/metrics/water?field_id={fake_id}&period=season")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_water_summary_via_api(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test getting farm-wide water summary via API endpoint."""
        response = client.get(f"/api/metrics/water/summary?farm_id={sample_field.farm_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "farm_id" in data["data"]
        assert "total_water_recommended_liters" in data["data"]
        assert "total_water_typical_liters" in data["data"]
        assert "total_water_saved_liters" in data["data"]
        assert "average_efficiency_percent" in data["data"]
        assert "total_cost_saved_usd" in data["data"]
        assert "field_count" in data["data"]
        assert data["data"]["field_count"] >= 1

    @pytest.mark.asyncio
    async def test_get_water_summary_nonexistent_farm(self) -> None:
        """Test getting water summary for non-existent farm."""
        response = client.get("/api/metrics/water/summary?farm_id=nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_fire_risk_metrics_via_api(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test getting fire risk metrics via API endpoint."""
        # Create an accepted recommendation with fire risk reduction
        recommendation = Recommendation(
            field_id=sample_field.id,
            agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
            action=RecommendationAction.DELAY,
            title="Delay irrigation due to fire risk",
            reason="High fire risk detected",
            confidence=0.85,
            fire_risk_reduction_percent=15.0,
            accepted=True,
            accepted_at=datetime.now(timezone.utc),
        )
        db_session.add(recommendation)
        await db_session.commit()

        response = client.get(f"/api/metrics/fire-risk?field_id={sample_field.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "field_id" in data["data"]
        assert "fire_risk_reduction_percent" in data["data"]
        assert "current_fire_risk_level" in data["data"]
        assert "recommendations_applied" in data["data"]
        assert "last_updated" in data["data"]

        # Validate data
        assert data["data"]["recommendations_applied"] >= 1
        assert data["data"]["fire_risk_reduction_percent"] >= 0

    @pytest.mark.asyncio
    async def test_get_fire_risk_metrics_nonexistent_field(self) -> None:
        """Test getting fire risk metrics for non-existent field."""
        fake_id = str(uuid4())
        response = client.get(f"/api/metrics/fire-risk?field_id={fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_water_metrics_with_recommendations(
        self, db_session: AsyncSession, sample_field: Field
    ) -> None:
        """Test water metrics calculation with actual recommendations."""
        # Create Fire-Adaptive Irrigation recommendations
        for i in range(3):
            recommendation = Recommendation(
                field_id=sample_field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.IRRIGATE,
                title=f"Test recommendation {i}",
                reason="Test reason",
                confidence=0.8,
                water_saved_liters=1000.0 * (i + 1),
            )
            db_session.add(recommendation)

        # Create sensor reading
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

        # Get metrics
        response = client.get(
            f"/api/metrics/water?field_id={sample_field.id}&period=season"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["water_recommended_liters"] >= 0
        assert data["data"]["water_typical_liters"] > 0
        assert data["data"]["water_saved_liters"] >= 0

