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
from app.database import get_db # Added
from app.models.psps_event import PspsEvent, PspsUtility, PspsStatus # Added
from app.services.psps_event_service import sync_psps_events, get_active_psps_events # Added
from sqlalchemy.ext.asyncio import AsyncSession # Added
from geoalchemy2.functions import ST_AsGeoJSON # Added
import json # Added

logger = logging.getLogger(__name__)


class PSPSMCP:
    """
    Utility PSPS MCP Server.

    Fetches active and predicted power shutoff events from utility APIs
    with graceful fallback to mock/CSV data.
    """

    def __init__(self) -> None:
        """Initialize PSPS MCP server."""
        self.psps_feature_server_urls = settings.psps_feature_server_urls or "" # Added
        self.use_mock = (
            not self.psps_feature_server_urls # Modified
            or settings.environment == "development"
        )

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
            async for db in get_db(): # Modified
                return await self._get_real_active_shutoffs(db, latitude, longitude) # Modified
        except Exception as e:
            logger.warning(f"Failed to fetch real PSPS data: {e}, using mock")
            return self._get_mock_active_shutoffs(latitude, longitude)

    async def _get_real_active_shutoffs(
        self,
        db: AsyncSession,
        latitude: Optional[float],
        longitude: Optional[float],
    ) -> List[Dict[str, Any]]:
        """
        Fetch active shutoffs from the database.

        Args:
            db: Database session
            latitude: Optional latitude
            longitude: Optional longitude

        Returns:
            List of shutoff events
        """
        # Query for active PSPS events from the database
        psps_events = await get_active_psps_events(
            db,
            latitude=latitude,
            longitude=longitude,
            status_filter=PspsStatus.ACTIVE # Filter for active events
        )

        if not psps_events:
            logger.info("No active PSPS events found in DB, falling back to mock.")
            return self._get_mock_active_shutoffs(latitude, longitude)

        # Convert PspsEvent objects to dictionary format
        active_shutoffs_data = []
        for event in psps_events:
            active_shutoffs_data.append({
                "id": event.id,
                "utility": event.utility.value,
                "start_time": event.starts_at.isoformat(),
                "estimated_end_time": event.ends_at.isoformat() if event.ends_at else None,
                "status": event.status.value.upper(),
                "reason": event.properties.get("reason", "No specific reason provided"),
                "affected_customers": event.properties.get("affected_customers"),
                "counties": event.properties.get("counties"),
                "geometry": json.loads(await db.scalar(ST_AsGeoJSON(event.geom))), # Convert geom to GeoJSON
            })
        return active_shutoffs_data

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
        db: AsyncSession,
        latitude: Optional[float],
        longitude: Optional[float],
        hours_ahead: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetch predicted shutoffs from the database.

        Args:
            db: Database session
            latitude: Optional latitude
            longitude: Optional longitude
            hours_ahead: Hours ahead

        Returns:
            List of predicted shutoff events
        """
        # Query for predicted PSPS events from the database
        psps_events = await get_active_psps_events(
            db,
            latitude=latitude,
            longitude=longitude,
            status_filter=PspsStatus.PLANNED # Filter for planned events
        )

        if not psps_events:
            logger.info("No predicted PSPS events found in DB, falling back to mock.")
            return self._get_mock_predicted_shutoffs(latitude, longitude, hours_ahead)

        # Convert PspsEvent objects to dictionary format
        predicted_shutoffs_data = []
        for event in psps_events:
            # Only include events that are within the hours_ahead window
            if event.starts_at and event.starts_at < datetime.now(event.starts_at.tzinfo) + timedelta(hours=hours_ahead):
                predicted_shutoffs_data.append({
                    "id": event.id,
                    "utility": event.utility.value,
                    "predicted_start_time": event.starts_at.isoformat(),
                    "predicted_end_time": event.ends_at.isoformat() if event.ends_at else None,
                    "status": event.status.value.upper(),
                    "confidence": event.properties.get("confidence", 0.7), # Default confidence
                    "reason": event.properties.get("reason", "Forecasted high winds and low humidity"),
                    "estimated_affected_customers": event.properties.get("affected_customers"),
                    "counties": event.properties.get("counties"),
                    "geometry": json.loads(await db.scalar(ST_AsGeoJSON(event.geom))), # Convert geom to GeoJSON
                })
        return predicted_shutoffs_data

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

