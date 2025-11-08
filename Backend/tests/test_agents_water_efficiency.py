"""
Unit tests for the Water Efficiency Agent.
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock, MagicMock

from app.agents.water_efficiency import WaterEfficiencyAgent, WaterEfficiencyAgentState
from app.models.recommendation import Recommendation, RecommendationAction

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def agent() -> WaterEfficiencyAgent:
    """Fixture to provide a WaterEfficiencyAgent instance."""
    return WaterEfficiencyAgent()


async def test_water_efficiency_agent_calculates_metrics(agent: WaterEfficiencyAgent):
    """
    Test that the Water Efficiency Agent correctly calculates efficiency metrics.
    """
    field_id = uuid4()
    
    mock_recommendations = [
        Recommendation(id=uuid4(), field_id=field_id, action=RecommendationAction.IRRIGATE, water_saved_liters=0),
        Recommendation(id=uuid4(), field_id=field_id, action=RecommendationAction.DELAY, water_saved_liters=5000),
    ]

    with patch("app.agents.water_efficiency.RecommendationService.list_recommendations", new_callable=AsyncMock) as mock_list_recs:
        mock_list_recs.return_value = (mock_recommendations, len(mock_recommendations))

        mock_db_session = AsyncMock()
        
        state = await agent.analyze(db=mock_db_session, field_id=field_id)

        assert state.error is None
        assert len(state.recommendations) == 2
        assert len(state.actual_irrigation_data) == 2
        assert state.total_water_recommended > 0
        assert state.efficiency_score > 0
