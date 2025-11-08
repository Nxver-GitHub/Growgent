"""
Simple tests for Fire-Adaptive Irrigation Agent logic.

Tests agent decision logic without requiring full database setup.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

# Test agent logic directly without importing database-dependent modules
from app.agents.irrigation import (
    FireAdaptiveIrrigationAgent,
    IrrigationAgentState,
)
from app.models.recommendation import RecommendationAction


@pytest.mark.asyncio
class TestFireAdaptiveIrrigationAgentSimple:
    """Simple test suite for Fire-Adaptive Irrigation Agent."""

    @pytest.fixture
    def agent(self) -> FireAdaptiveIrrigationAgent:
        """Create agent instance for testing."""
        return FireAdaptiveIrrigationAgent()

    async def test_agent_initialization(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test agent initializes correctly."""
        assert agent.agent_name == "FireAdaptiveIrrigationAgent"
        assert agent.SOIL_MOISTURE_LOW_THRESHOLD == 30.0
        assert agent.FIRE_RISK_HIGH_THRESHOLD == 0.7
        assert agent.PSPS_PRE_IRRIGATE_HOURS == 36

    async def test_calculate_water_need(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test water need calculation."""
        # Test with different crop stages
        need_seedling = agent._calculate_water_need("seedling", None)
        need_flowering = agent._calculate_water_need("flowering", None)
        
        assert 0.0 <= need_seedling <= 1.0
        assert 0.0 <= need_flowering <= 1.0
        assert need_flowering > need_seedling  # Flowering needs more water

    async def test_calculate_fire_risk_score(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test fire risk score calculation."""
        # Test with high risk data
        high_risk_data = {
            "zones": [{
                "risk_score": 0.85,
                "risk_level": "HIGH",
            }]
        }
        score = agent._calculate_fire_risk_score(high_risk_data)
        assert score == 0.85

        # Test with no data
        score_no_data = agent._calculate_fire_risk_score(None)
        assert score_no_data == 0.5  # Default moderate risk

    async def test_calculate_drought_risk_score(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test drought risk score calculation."""
        # Test with low moisture
        score_low = agent._calculate_drought_risk_score(25.0, None)
        assert score_low > 0.5  # Should be high risk

        # Test with sufficient moisture
        score_sufficient = agent._calculate_drought_risk_score(55.0, None)
        assert score_sufficient < 0.5  # Should be lower risk

    async def test_decision_logic_low_moisture(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test decision logic when moisture is low."""
        state = IrrigationAgentState(field_id=uuid4())
        state.current_soil_moisture = 25.0  # Low
        state.fire_risk_score = 0.5  # Moderate
        state.drought_risk_score = 0.7  # High
        state.field_location = {"latitude": 38.5, "longitude": -122.5}
        
        state = await agent._make_decision(state)
        
        assert state.recommended_action == RecommendationAction.IRRIGATE
        assert state.reasoning is not None
        assert "low" in state.reasoning.lower() or "moisture" in state.reasoning.lower()

    async def test_decision_logic_high_fire_risk(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test decision logic when fire risk is high and moisture is sufficient."""
        state = IrrigationAgentState(field_id=uuid4())
        state.current_soil_moisture = 55.0  # Sufficient
        state.fire_risk_score = 0.85  # High
        state.drought_risk_score = 0.3  # Low
        state.field_location = {"latitude": 38.5, "longitude": -122.5}
        
        # Make decision and calculate impact
        state = await agent._make_decision(state)
        state = await agent._calculate_impact(state)
        
        assert state.recommended_action == RecommendationAction.DELAY
        assert state.fire_risk_reduction_percent is not None
        assert state.water_saved_liters is not None

    async def test_decision_logic_psps_prediction(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test decision logic when PSPS is predicted."""
        state = IrrigationAgentState(field_id=uuid4())
        state.field_location = {"latitude": 38.5, "longitude": -122.5}
        
        # Mock PSPS prediction 36 hours ahead
        predicted_time = datetime.now() + timedelta(hours=36)
        state.psps_predictions = [{
            "id": "psps-pred-001",
            "predicted_start_time": predicted_time.isoformat(),
            "predicted_end_time": (predicted_time + timedelta(hours=24)).isoformat(),
            "status": "PREDICTED",
        }]
        
        state = await agent._make_decision(state)
        
        assert state.recommended_action == RecommendationAction.PRE_IRRIGATE
        assert state.psps_alert is True
        assert state.recommended_timing is not None

    async def test_confidence_calculation(self, agent: FireAdaptiveIrrigationAgent) -> None:
        """Test confidence score calculation."""
        state = IrrigationAgentState(field_id=uuid4())
        state.data_quality_score = 0.8
        state.fire_risk_score = 0.85
        state.current_soil_moisture = 55.0
        
        confidence = agent._calculate_confidence(state)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.5  # Should have reasonable confidence

