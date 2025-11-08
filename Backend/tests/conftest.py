"""
Pytest configuration and fixtures.

Provides shared test fixtures for all tests.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.field import Field
from app.models.sensor_reading import SensorReading


@pytest.fixture
def sample_field_id() -> str:
    """Generate a sample field UUID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_field_data() -> dict:
    """Sample field data for testing."""
    return {
        "id": uuid4(),
        "farm_id": "farm-001",
        "name": "Test Field",
        "crop_type": "Tomatoes",
        "area_hectares": 10.0,
        "location_geom": None,
        "notes": "Test field for unit tests",
    }


@pytest.fixture
def mock_weather_forecast() -> dict:
    """Mock weather forecast data."""
    return {
        "location": {"latitude": 38.5, "longitude": -122.5},
        "current": {
            "temperature": 25.0,
            "humidity": 45.0,
            "wind_speed": 10.0,
            "precipitation": 0.0,
        },
        "forecast": [
            {
                "timestamp": "2025-01-07T12:00:00",
                "temperature": 25.0,
                "humidity": 45.0,
                "wind_speed": 10.0,
                "precipitation": 0.0,
                "description": "clear sky",
            }
        ],
    }


@pytest.fixture
def mock_fire_risk_data() -> dict:
    """Mock fire risk data."""
    return {
        "location": {"latitude": 38.5, "longitude": -122.5},
        "radius_km": 50.0,
        "zones": [
            {
                "id": "zone-001",
                "name": "High Fire Risk Zone",
                "risk_level": "HIGH",
                "risk_score": 0.85,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-122.52, 38.48], [-122.48, 38.48], [-122.48, 38.52], [-122.52, 38.52], [-122.52, 38.48]]],
                },
                "factors": {
                    "fuel_moisture": "Very Dry",
                    "wind_speed": "High",
                    "temperature": "Above Average",
                },
            }
        ],
    }


@pytest.fixture
def mock_psps_predictions() -> list:
    """Mock PSPS predictions."""
    return [
        {
            "id": "psps-pred-001",
            "utility": "PG&E",
            "predicted_start_time": "2025-01-09T10:00:00Z",
            "predicted_end_time": "2025-01-10T10:00:00Z",
            "estimated_affected_customers": 25000,
            "counties": ["Sonoma", "Napa"],
            "status": "PREDICTED",
            "confidence": 0.85,
            "reason": "Forecasted high winds and low humidity",
        }
    ]


@pytest.fixture
def mock_sensor_reading() -> dict:
    """Mock sensor reading data."""
    return {
        "sensor_id": "sensor-001",
        "field_id": str(uuid4()),
        "moisture_percent": 35.0,
        "temperature": 22.0,
        "ph": 6.5,
        "reading_timestamp": "2025-01-07T10:00:00Z",
        "battery_level": 85.0,
        "signal_strength": -90.0,
    }


# Database fixtures for integration tests
@pytest_asyncio.fixture
async def db_session():
    """
    Create a test database session using the actual PostgreSQL database.
    
    Uses the configured database from settings, which should be running via Docker.
    """
    from app.config import settings
    from app.database import AsyncSessionLocal
    
    # Use the actual database connection from app.database
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.rollback()  # Rollback test changes
        finally:
            await session.close()


@pytest_asyncio.fixture
async def sample_field(db_session: AsyncSession) -> Field:
    """Create a sample field for testing."""
    # Clean up any existing test fields first (optional, for test isolation)
    from sqlalchemy import select, delete
    from app.models.field import Field as FieldModel
    
    # Delete any existing test fields with this farm_id (optional)
    # await db_session.execute(delete(FieldModel).where(FieldModel.farm_id == "test-farm-001"))
    
    field = Field(
        farm_id="test-farm-001",
        name="Test Field",
        crop_type="tomato",
        area_hectares=10.0,
        location_geom=None,  # Can be enhanced with PostGIS geometry if needed
    )
    db_session.add(field)
    await db_session.commit()
    await db_session.refresh(field)
    return field
