"""
Tests for the main FastAPI application.

Tests cover health checks, root endpoint, and error handling.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint() -> None:
    """
    Test the root endpoint returns correct API information.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Growgent API"
    assert data["version"] == "0.1.0"


def test_health_endpoint() -> None:
    """
    Test the health check endpoint returns healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_health_endpoint_response_time() -> None:
    """
    Test health endpoint responds quickly.
    """
    import time
    
    start = time.time()
    response = client.get("/health")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 1.0  # Should respond in under 1 second

