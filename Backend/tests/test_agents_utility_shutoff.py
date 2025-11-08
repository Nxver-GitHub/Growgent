"""
Unit tests for the Utility Shutoff Anticipation Agent.
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.agents.utility_shutoff import UtilityShutoffAnticipationAgent, UtilityShutoffAgentState

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def agent() -> UtilityShutoffAnticipationAgent:
    """Fixture to provide a UtilityShutoffAnticipationAgent instance."""
    return UtilityShutoffAnticipationAgent()


async def test_agent_generates_alert_for_high_confidence_psps(agent: UtilityShutoffAnticipationAgent):
    """
    Test that the agent generates an alert for a high-confidence PSPS event.
    """
    field_id = uuid4()
    location = {"latitude": 38.5, "longitude": -122.5}
    
    mock_psps_predictions = [
        {
            "confidence": 0.8,
            "predicted_start_time": "2025-11-10T10:00:00Z",
        }
    ]

    with patch("app.agents.utility_shutoff.psps_mcp.get_predicted_shutoffs", new_callable=AsyncMock) as mock_get_shutoffs:
        mock_get_shutoffs.return_value = mock_psps_predictions

        initial_state = UtilityShutoffAgentState(field_id=field_id, location=location)
        updated_state = await agent.process(initial_state)

        assert updated_state.error is None
        assert updated_state.alert_generated is True
        assert "High confidence PSPS event predicted" in updated_state.alert_message


async def test_agent_no_alert_for_low_confidence_psps(agent: UtilityShutoffAnticipationAgent):
    """
    Test that the agent does not generate an alert for a low-confidence PSPS event.
    """
    field_id = uuid4()
    location = {"latitude": 38.5, "longitude": -122.5}
    
    mock_psps_predictions = [
        {
            "confidence": 0.5,
            "predicted_start_time": "2025-11-10T10:00:00Z",
        }
    ]

    with patch("app.agents.utility_shutoff.psps_mcp.get_predicted_shutoffs", new_callable=AsyncMock) as mock_get_shutoffs:
        mock_get_shutoffs.return_value = mock_psps_predictions

        initial_state = UtilityShutoffAgentState(field_id=field_id, location=location)
        updated_state = await agent.process(initial_state)

        assert updated_state.error is None
        assert updated_state.alert_generated is False
        assert updated_state.alert_message is None


async def test_agent_no_alert_for_no_psps_events(agent: UtilityShutoffAnticipationAgent):
    """
    Test that the agent does nothing when there are no predicted PSPS events.
    """
    field_id = uuid4()
    location = {"latitude": 38.5, "longitude": -122.5}
    
    with patch("app.agents.utility_shutoff.psps_mcp.get_predicted_shutoffs", new_callable=AsyncMock) as mock_get_shutoffs:
        mock_get_shutoffs.return_value = []

        initial_state = UtilityShutoffAgentState(field_id=field_id, location=location)
        updated_state = await agent.process(initial_state)

        assert updated_state.error is None
        assert updated_state.alert_generated is False
        assert updated_state.alert_message is None


async def test_agent_handles_mcp_error_gracefully(agent: UtilityShutoffAnticipationAgent):
    """
    Test that the agent handles an error from the PSPS MCP server gracefully.
    """
    field_id = uuid4()
    location = {"latitude": 38.5, "longitude": -122.5}
    
    with patch("app.agents.utility_shutoff.psps_mcp.get_predicted_shutoffs", new_callable=AsyncMock) as mock_get_shutoffs:
        mock_get_shutoffs.side_effect = Exception("MCP server is down")

        initial_state = UtilityShutoffAgentState(field_id=field_id, location=location)
        updated_state = await agent.process(initial_state)

        assert updated_state.error is not None
        assert "Failed to fetch PSPS data from MCP" in updated_state.error
        assert updated_state.alert_generated is False


async def test_check_shutoffs_api_endpoint():
    """
    Test the /api/agents/utility-shutoff/check endpoint.
    """
    field_id = uuid4()
    request_data = {
        "field_id": str(field_id),
        "latitude": 38.5,
        "longitude": -122.5,
    }

    mock_agent_state = UtilityShutoffAgentState(
        field_id=field_id,
        location={"latitude": request_data["latitude"], "longitude": request_data["longitude"]},
        alert_generated=True,
        alert_message="PSPS event predicted",
    )

    with patch("app.api.utility_shutoff.utility_shutoff_agent.check_for_shutoffs", new_callable=AsyncMock) as mock_check_shutoffs:
        mock_check_shutoffs.return_value = mock_agent_state

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/agents/utility-shutoff/check", json=request_data)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["status"] == "success"
        assert response_json["data"]["alert_generated"] is True
        assert "PSPS event predicted" in response_json["data"]["alert_message"]
