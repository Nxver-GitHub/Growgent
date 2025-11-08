"""
Utility PSPS (Public Safety Power Shutoff) MCP Server implementation.

Provides PSPS data from utility APIs (PG&E, SDG&E, SCE) with mock data fallback.
"""

import csv
import logging
from datetime import datetime, timedelta
from io import StringIO
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class PSPSMCP:
    """
    Utility PSPS MCP Server.

    Fetches active and predicted power shutoff events from utility APIs
    with graceful fallback to mock/CSV data.
    """

    def __init__(self) -> None:
        """Initialize PSPS MCP server."""
        self.use_mock = settings.environment == "development"

    async def get_active_shutoffs(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get currently active PSPS shutoffs.

        Args:
            latitude: Optional latitude to filter by location
            longitude: Optional longitude to filter by location

        Returns:
            List of active shutoff events
        """
        if self.use_mock:
            logger.info("Using mock PSPS data")
            return self._get_mock_active_shutoffs(latitude, longitude)

        try:
            # Try real utility APIs
            return await self._get_real_active_shutoffs(latitude, longitude)
        except Exception as e:
            logger.warning(f"Failed to fetch real PSPS data: {e}, using mock")
            return self._get_mock_active_shutoffs(latitude, longitude)

    async def _get_real_active_shutoffs(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
    ) -> List[Dict[str, Any]]:
        """
        Fetch active shutoffs from utility APIs.

        Args:
            latitude: Optional latitude
            longitude: Optional longitude

        Returns:
            List of shutoff events

        Note:
            This would integrate with PG&E, SDG&E, or SCE APIs
            For MVP, returns mock data
        """
        # Placeholder for real API integration
        # PG&E API: https://www.pge.com/pge_global/common/pages/safety/outage-center/psps.html
        # SDG&E API: https://www.sdge.com/safety/outages/psps
        # SCE API: https://www.sce.com/safety/outages/psps
        return self._get_mock_active_shutoffs(latitude, longitude)

    def _get_mock_active_shutoffs(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
    ) -> List[Dict[str, Any]]:
        """
        Generate mock active shutoff data.

        Args:
            latitude: Optional latitude
            longitude: Optional longitude

        Returns:
            List of mock shutoff events
        """
        now = datetime.now()
        return [
            {
                "id": "psps-001",
                "utility": "PG&E",
                "start_time": (now - timedelta(hours=2)).isoformat(),
                "estimated_end_time": (now + timedelta(hours=24)).isoformat(),
                "affected_customers": 15000,
                "counties": ["Sonoma", "Napa"],
                "status": "ACTIVE",
                "reason": "High fire risk conditions",
            },
        ]

    async def get_predicted_shutoffs(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        hours_ahead: int = 48,
    ) -> List[Dict[str, Any]]:
        """
        Get predicted PSPS shutoffs in the next N hours.

        Args:
            latitude: Optional latitude to filter by location
            longitude: Optional longitude to filter by location
            hours_ahead: Number of hours to look ahead (default: 48)

        Returns:
            List of predicted shutoff events
        """
        if self.use_mock:
            logger.info("Using mock predicted PSPS data")
            return self._get_mock_predicted_shutoffs(latitude, longitude, hours_ahead)

        try:
            return await self._get_real_predicted_shutoffs(
                latitude, longitude, hours_ahead
            )
        except Exception as e:
            logger.warning(f"Failed to fetch real predicted PSPS data: {e}, using mock")
            return self._get_mock_predicted_shutoffs(
                latitude, longitude, hours_ahead
            )

    async def _get_real_predicted_shutoffs(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
        hours_ahead: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetch predicted shutoffs from utility APIs.

        Args:
            latitude: Optional latitude
            longitude: Optional longitude
            hours_ahead: Hours ahead

        Returns:
            List of predicted shutoff events
        """
        # Placeholder for real API integration
        return self._get_mock_predicted_shutoffs(latitude, longitude, hours_ahead)

    def _get_mock_predicted_shutoffs(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
        hours_ahead: int,
    ) -> List[Dict[str, Any]]:
        """
        Generate mock predicted shutoff data.

        Args:
            latitude: Optional latitude
            longitude: Optional longitude
            hours_ahead: Hours ahead

        Returns:
            List of mock predicted shutoff events
        """
        now = datetime.now()
        predicted_time = now + timedelta(hours=36)  # 36 hours from now

        return [
            {
                "id": "psps-pred-001",
                "utility": "PG&E",
                "predicted_start_time": predicted_time.isoformat(),
                "predicted_end_time": (predicted_time + timedelta(hours=24)).isoformat(),
                "estimated_affected_customers": 25000,
                "counties": ["Sonoma", "Napa", "Marin"],
                "status": "PREDICTED",
                "confidence": 0.85,
                "reason": "Forecasted high winds and low humidity",
            },
        ]

    def _load_from_csv(self, csv_data: str) -> List[Dict[str, Any]]:
        """
        Load PSPS data from CSV string.

        Args:
            csv_data: CSV data as string

        Returns:
            List of PSPS events
        """
        reader = csv.DictReader(StringIO(csv_data))
        return list(reader)

