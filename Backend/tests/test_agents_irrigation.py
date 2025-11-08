"""
Tests for Fire-Adaptive Irrigation Agent.

Tests cover agent decision logic, MCP integration, and recommendation generation.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.agents.irrigation import (
    FireAdaptiveIrrigationAgent,
    IrrigationAgentState,
)
from app.models.recommendation import RecommendationAction


@pytest.mark.asyncio
class TestFireAdaptiveIrrigationAgent:
    """Test suite for Fire-Adaptive Irrigation Agent."""

    @pytest.fixture
    def agent(self) -> FireAdaptiveIrrigationAgent:
        """Create agent instance for testing."""
        return FireAdaptiveIrrigationAgent()

    @pytest.fixture
    def field_id(self) -> str:
        """Generate test field ID."""
        return uuid4()

    async def test_agent_initialization(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test agent initializes correctly."""
        assert agent.agent_name == "FireAdaptiveIrrigationAgent"
        assert agent.SOIL_MOISTURE_LOW_THRESHOLD == 30.0
        assert agent.FIRE_RISK_HIGH_THRESHOLD == 0.7

    async def test_recommend_with_low_moisture(self, agent: FireAdaptiveIrrigationAgent, field_id: str) -> None:
        """Test agent recommends IRRIGATE when soil moisture is low."""
        # Mock sensor reading with low moisture
        from app.mcp import sensor_mcp
        original_get_latest = sensor_mcp.get_latest_reading
        
        async def mock_get_latest(field_uuid, sensor_id=None):
            return {
                "sensor_id": "sensor-001",
                "field_id": str(field_uuid),
                "moisture_percent": 25.0,  # Low moisture
                "temperature": 22.0,
                "ph": 6.5,
                "reading_timestamp": datetime.now().isoformat(),
            }
        
        sensor_mcp.get_latest_reading = mock_get_latest
        
        try:
            state = await agent.recommend(field_id=field_id)
            
            assert state.recommended_action == RecommendationAction.IRRIGATE
            assert state.confidence is not None
            assert state.confidence > 0.5
            assert "low" in state.reasoning.lower() or "moisture" in state.reasoning.lower()
        finally:
            sensor_mcp.get_latest_reading = original_get_latest

    async def test_recommend_with_high_fire_risk_and_sufficient_moisture(
        self, agent: FireAdaptiveIrrigationAgent, field_id: str
    ) -> None:
        """Test agent recommends DELAY when fire risk is high and moisture is sufficient."""
        # Mock sensor reading with sufficient moisture
        from app.mcp import sensor_mcp, fire_risk_mcp
        original_get_latest = sensor_mcp.get_latest_reading
        original_get_fire_risk = fire_risk_mcp.get_fire_risk_zones
        
        async def mock_get_latest(field_uuid, sensor_id=None):
            return {
                "sensor_id": "sensor-001",
                "field_id": str(field_uuid),
                "moisture_percent": 55.0,  # Sufficient moisture
                "temperature": 22.0,
                "ph": 6.5,
                "reading_timestamp": datetime.now().isoformat(),
            }
        
        async def mock_get_fire_risk(lat, lon, radius_km=50.0):
            return {
                "location": {"latitude": lat, "longitude": lon},
                "radius_km": radius_km,
                "zones": [{
                    "id": "zone-001",
                    "name": "High Fire Risk Zone",
                    "risk_level": "HIGH",
                    "risk_score": 0.85,  # High fire risk
                    "geometry": {"type": "Polygon", "coordinates": []},
                    "factors": {},
                }],
            }
        
        sensor_mcp.get_latest_reading = mock_get_latest
        fire_risk_mcp.get_fire_risk_zones = mock_get_fire_risk
        
        try:
            state = await agent.recommend(field_id=field_id)
            
            assert state.recommended_action == RecommendationAction.DELAY
            assert state.fire_risk_reduction_percent is not None
            assert state.water_saved_liters is not None
            assert "fire" in state.reasoning.lower() or "delay" in state.reasoning.lower()
        finally:
            sensor_mcp.get_latest_reading = original_get_latest
            fire_risk_mcp.get_fire_risk_zones = original_get_fire_risk

    async def test_recommend_with_psps_prediction(
        self, agent: FireAdaptiveIrrigationAgent, field_id: str
    ) -> None:
        """Test agent recommends PRE_IRRIGATE when PSPS is predicted."""
        from app.mcp import psps_mcp
        original_get_predicted = psps_mcp.get_predicted_shutoffs
        
        async def mock_get_predicted(lat=None, lon=None, hours_ahead=48):
            # PSPS predicted in 36 hours (within PRE_IRRIGATE window)
            predicted_time = datetime.now() + timedelta(hours=36)
            return [{
                "id": "psps-pred-001",
                "utility": "PG&E",
                "predicted_start_time": predicted_time.isoformat(),
                "predicted_end_time": (predicted_time + timedelta(hours=24)).isoformat(),
                "estimated_affected_customers": 25000,
                "counties": ["Sonoma"],
                "status": "PREDICTED",
                "confidence": 0.85,
                "reason": "Forecasted high winds",
            }]
        
        psps_mcp.get_predicted_shutoffs = mock_get_predicted
        
        try:
            state = await agent.recommend(field_id=field_id)
            
            assert state.recommended_action == RecommendationAction.PRE_IRRIGATE
            assert state.psps_alert is True
            assert state.recommended_timing is not None
            assert "psps" in state.reasoning.lower() or "shutoff" in state.reasoning.lower()
        finally:
            psps_mcp.get_predicted_shutoffs = original_get_predicted

    async def test_recommend_monitor_when_balanced(
        self, agent: FireAdaptiveIrrigationAgent, field_id: str
    ) -> None:
        """Test agent recommends MONITOR when conditions are balanced."""
        from app.mcp import sensor_mcp, fire_risk_mcp
        original_get_latest = sensor_mcp.get_latest_reading
        original_get_fire_risk = fire_risk_mcp.get_fire_risk_zones
        
        async def mock_get_latest(field_uuid, sensor_id=None):
            return {
                "sensor_id": "sensor-001",
                "field_id": str(field_uuid),
                "moisture_percent": 45.0,  # Moderate moisture
                "temperature": 22.0,
                "ph": 6.5,
                "reading_timestamp": datetime.now().isoformat(),
            }
        
        async def mock_get_fire_risk(lat, lon, radius_km=50.0):
            return {
                "location": {"latitude": lat, "longitude": lon},
                "radius_km": radius_km,
                "zones": [{
                    "id": "zone-001",
                    "name": "Moderate Fire Risk Zone",
                    "risk_level": "MODERATE",
                    "risk_score": 0.5,  # Moderate fire risk
                    "geometry": {"type": "Polygon", "coordinates": []},
                    "factors": {},
                }],
            }
        
        sensor_mcp.get_latest_reading = mock_get_latest
        fire_risk_mcp.get_fire_risk_zones = mock_get_fire_risk
        
        try:
            state = await agent.recommend(field_id=field_id)
            
            assert state.recommended_action == RecommendationAction.MONITOR
            assert state.confidence is not None
        finally:
            sensor_mcp.get_latest_reading = original_get_latest
            fire_risk_mcp.get_fire_risk_zones = original_get_fire_risk

    async def test_confidence_calculation(self, agent: FireAdaptiveIrrigationAgent, field_id: str) -> None:
        """Test confidence score calculation."""
        state = await agent.recommend(field_id=field_id)
        
        assert state.confidence is not None
        assert 0.0 <= state.confidence <= 1.0
        assert state.data_quality_score is not None
        assert 0.0 <= state.data_quality_score <= 1.0

    async def test_impact_metrics_calculation(
        self, agent: FireAdaptiveIrrigationAgent, field_id: str
    ) -> None:
        """Test impact metrics are calculated correctly."""
        from app.mcp import sensor_mcp, fire_risk_mcp
        original_get_latest = sensor_mcp.get_latest_reading
        original_get_fire_risk = fire_risk_mcp.get_fire_risk_zones
        
        async def mock_get_latest(field_uuid, sensor_id=None):
            return {
                "sensor_id": "sensor-001",
                "field_id": str(field_uuid),
                "moisture_percent": 55.0,
                "temperature": 22.0,
                "ph": 6.5,
                "reading_timestamp": datetime.now().isoformat(),
            }
        
        async def mock_get_fire_risk(lat, lon, radius_km=50.0):
            return {
                "location": {"latitude": lat, "longitude": lon},
                "radius_km": radius_km,
                "zones": [{
                    "id": "zone-001",
                    "name": "High Fire Risk Zone",
                    "risk_level": "HIGH",
                    "risk_score": 0.85,
                    "geometry": {"type": "Polygon", "coordinates": []},
                    "factors": {},
                }],
            }
        
        sensor_mcp.get_latest_reading = mock_get_latest
        fire_risk_mcp.get_fire_risk_zones = mock_get_fire_risk
        
        try:
            state = await agent.recommend(field_id=field_id)
            
            if state.recommended_action == RecommendationAction.DELAY:
                assert state.fire_risk_reduction_percent is not None
                assert state.fire_risk_reduction_percent > 0.0
                assert state.water_saved_liters is not None
                assert state.water_saved_liters > 0.0
        finally:
            sensor_mcp.get_latest_reading = original_get_latest
            fire_risk_mcp.get_fire_risk_zones = original_get_fire_risk

