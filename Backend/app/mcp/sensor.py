"""
Sensor MCP Server implementation.

Provides IoT sensor data (soil moisture, temperature, pH) with mock data fallback.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config import settings

logger = logging.getLogger(__name__)


class SensorMCP:
    """
    Sensor MCP Server.

    Fetches IoT sensor readings from LoRaWAN or simulated sources
    with graceful fallback to mock data.
    """

    def __init__(self) -> None:
        """Initialize Sensor MCP server."""
        self.use_mock = settings.environment == "development"
        # Track mock sensor state for realistic increments
        self._mock_sensor_state: Dict[str, Dict[str, float]] = {}

    async def get_sensor_readings(
        self,
        field_id: UUID,
        sensor_id: Optional[str] = None,
        hours_back: int = 24,
    ) -> List[Dict[str, Any]]:
        """
        Get sensor readings for a field.

        Args:
            field_id: Field UUID
            sensor_id: Optional specific sensor ID
            hours_back: Number of hours to look back (default: 24)

        Returns:
            List of sensor readings
        """
        if self.use_mock:
            logger.info(f"Using mock sensor data for field {field_id}")
            return self._get_mock_readings(field_id, sensor_id, hours_back)

        try:
            # Try real sensor API (LoRaWAN, etc.)
            return await self._get_real_readings(field_id, sensor_id, hours_back)
        except Exception as e:
            logger.warning(f"Failed to fetch real sensor data: {e}, using mock")
            return self._get_mock_readings(field_id, sensor_id, hours_back)

    async def _get_real_readings(
        self,
        field_id: UUID,
        sensor_id: Optional[str],
        hours_back: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetch sensor readings from real IoT system.

        Args:
            field_id: Field UUID
            sensor_id: Optional sensor ID
            hours_back: Hours back

        Returns:
            List of readings

        Note:
            This would integrate with LoRaWAN, MQTT, or other IoT protocols
            For MVP, returns mock data
        """
        # Placeholder for real IoT integration
        # Would connect to LoRaWAN network server, MQTT broker, etc.
        return self._get_mock_readings(field_id, sensor_id, hours_back)

    def _get_mock_readings(
        self,
        field_id: UUID,
        sensor_id: Optional[str],
        hours_back: int,
    ) -> List[Dict[str, Any]]:
        """
        Generate mock sensor readings with realistic increments.

        Args:
            field_id: Field UUID
            sensor_id: Optional sensor ID
            hours_back: Hours back

        Returns:
            List of mock readings
        """
        field_key = str(field_id)
        if field_key not in self._mock_sensor_state:
            # Initialize state for this field
            self._mock_sensor_state[field_key] = {
                "moisture": 45.0,  # Start at 45%
                "temperature": 20.0,
                "ph": 6.5,
            }

        state = self._mock_sensor_state[field_key]
        readings = []
        now = datetime.now()

        # Generate readings for the past N hours (one per hour)
        for hour in range(hours_back, 0, -1):
            timestamp = now - timedelta(hours=hour)

            # Simulate realistic changes
            # Moisture decreases slowly, temperature varies
            state["moisture"] = max(20.0, state["moisture"] - 0.5)
            state["temperature"] = 18.0 + (hour % 24) * 0.5
            state["ph"] = 6.5 + (hour % 10) * 0.1

            readings.append({
                "sensor_id": sensor_id or f"sensor-{field_key}-001",
                "field_id": str(field_id),
                "moisture_percent": round(state["moisture"], 2),
                "temperature": round(state["temperature"], 2),
                "ph": round(state["ph"], 2),
                "reading_timestamp": timestamp.isoformat(),
                "battery_level": 85.0 - (hour * 0.1),
                "signal_strength": -90.0 + (hour % 5),
            })

        return readings

    async def get_latest_reading(
        self,
        field_id: UUID,
        sensor_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent sensor reading for a field.

        Args:
            field_id: Field UUID
            sensor_id: Optional specific sensor ID

        Returns:
            Latest reading or None if no readings found
        """
        readings = await self.get_sensor_readings(field_id, sensor_id, hours_back=1)
        return readings[-1] if readings else None


# Global instance
sensor_mcp = SensorMCP()

