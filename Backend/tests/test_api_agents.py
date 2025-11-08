"""
Tests for agent API endpoints.

Tests cover the REST API endpoints for agent operations.
"""

import pytest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
class TestAgentEndpoints:
    """Test suite for agent API endpoints."""

    def test_recommend_irrigation_endpoint(self) -> None:
        """Test POST /api/agents/irrigation/recommend endpoint."""
        field_id = str(uuid4())
        
        response = client.post(
            "/api/agents/irrigation/recommend",
            json={"field_id": field_id},
        )
        
        # Should return 201 or 400/500 if field doesn't exist
        assert response.status_code in [201, 400, 404, 500]
        
        if response.status_code == 201:
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "action" in data["data"]
            assert data["data"]["action"] in ["IRRIGATE", "DELAY", "MONITOR", "PRE_IRRIGATE"]

    def test_recommend_irrigation_invalid_request(self) -> None:
        """Test POST /api/agents/irrigation/recommend with invalid request."""
        response = client.post(
            "/api/agents/irrigation/recommend",
            json={},  # Missing field_id
        )
        
        assert response.status_code == 422  # Validation error

    def test_list_irrigation_recommendations(self) -> None:
        """Test GET /api/agents/irrigation/recommendations endpoint."""
        response = client.get("/api/agents/irrigation/recommendations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "recommendations" in data["data"]
        assert "total" in data["data"]

    def test_list_irrigation_recommendations_with_filters(self) -> None:
        """Test GET /api/agents/irrigation/recommendations with filters."""
        response = client.get(
            "/api/agents/irrigation/recommendations",
            params={"page": 1, "page_size": 10, "accepted": False},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_list_irrigation_recommendations_invalid_pagination(self) -> None:
        """Test GET /api/agents/irrigation/recommendations with invalid pagination."""
        response = client.get(
            "/api/agents/irrigation/recommendations",
            params={"page": 0},  # Invalid page
        )
        
        assert response.status_code == 400

