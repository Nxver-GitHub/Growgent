"""
Quick smoke tests for Agent 2 components.

These tests verify basic functionality of Water Efficiency and PSPS agents
with minimal setup.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field import Field
from app.models.recommendation import Recommendation, AgentType, RecommendationAction
from app.models.sensor_reading import SensorReading
from app.agents.water_efficiency import WaterEfficiencyAgent, WaterEfficiencyAgentState
from app.agents.psps import PSPSAlertAgent, PSPSAgentState
from app.services.metrics import MetricsService
from app.services.alert import AlertService


@pytest.mark.asyncio
async def test_water_efficiency_agent_basic(db_session: AsyncSession, sample_field: Field):
    """Test Water Efficiency Agent can process a field."""
    # Create a recommendation
    recommendation = Recommendation(
        field_id=sample_field.id,
        agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
        action=RecommendationAction.IRRIGATE,
        title="Test recommendation",
        reason="Test reason",
        confidence=0.8,
    )
    db_session.add(recommendation)
    
    # Create sensor reading
    sensor = SensorReading(
        field_id=sample_field.id,
        sensor_id="sensor-001",
        moisture_percent=40.0,
        temperature=22.0,
        ph=6.5,
        reading_timestamp=datetime.now(timezone.utc),
    )
    db_session.add(sensor)
    await db_session.commit()
    
    # Run agent
    agent = WaterEfficiencyAgent()
    state = WaterEfficiencyAgentState(field_id=sample_field.id)
    state = await agent.process(state, db_session)
    
    # Verify
    assert state.error is None
    assert state.water_metrics is not None
    assert state.water_metrics['field_id'] == sample_field.id
    print(f"✅ Water Efficiency Agent: Calculated {state.water_metrics['water_saved_liters']}L saved")


@pytest.mark.asyncio
async def test_psps_agent_basic(db_session: AsyncSession, sample_field: Field):
    """Test PSPS Agent can process a field."""
    # Run agent
    agent = PSPSAlertAgent()
    state = PSPSAgentState(field_id=sample_field.id)
    state = await agent.process(state, db_session)
    
    # Verify
    assert state.error is None
    assert state.step == "completed"
    assert isinstance(state.affected_field_ids, list)
    print(f"✅ PSPS Agent: Found {len(state.affected_field_ids)} affected fields")


@pytest.mark.asyncio
async def test_metrics_service_basic(db_session: AsyncSession, sample_field: Field):
    """Test MetricsService can calculate water metrics."""
    # Create recommendation
    recommendation = Recommendation(
        field_id=sample_field.id,
        agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
        action=RecommendationAction.IRRIGATE,
        title="Test",
        reason="Test",
        confidence=0.8,
    )
    db_session.add(recommendation)
    
    # Create sensor
    sensor = SensorReading(
        field_id=sample_field.id,
        sensor_id="sensor-001",
        moisture_percent=35.0,
        temperature=22.0,
        ph=6.5,
        reading_timestamp=datetime.now(timezone.utc),
    )
    db_session.add(sensor)
    await db_session.commit()
    
    # Calculate metrics
    metrics = await MetricsService.calculate_water_saved(
        db=db_session,
        field_id=sample_field.id,
        period="season",
    )
    
    # Verify
    assert metrics.field_id == sample_field.id
    assert metrics.water_typical_liters > 0
    assert 0 <= metrics.efficiency_percent <= 100
    print(f"✅ Metrics Service: {metrics.efficiency_percent:.1f}% efficiency, {metrics.water_saved_liters}L saved")


@pytest.mark.asyncio
async def test_alert_service_basic(db_session: AsyncSession, sample_field: Field):
    """Test AlertService can create and retrieve alerts."""
    from app.models.alert import AlertType, AlertSeverity
    
    # Create alert
    alert = await AlertService.create_alert(
        db=db_session,
        field_id=sample_field.id,
        alert_type=AlertType.WATER_SAVED_MILESTONE,
        severity=AlertSeverity.INFO,
        message="Test milestone alert",
        agent_type=AgentType.WATER_EFFICIENCY,
    )
    
    # Retrieve alert
    retrieved = await AlertService.get_alert(db=db_session, alert_id=alert.id)
    
    # Verify
    assert retrieved is not None
    assert retrieved.id == alert.id
    assert retrieved.message == "Test milestone alert"
    print(f"✅ Alert Service: Created and retrieved alert {alert.id}")





