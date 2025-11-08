"""
PSPS service for checking utility shutoff impact on fields.

This service polls PSPS data from MCP servers and determines which fields
are affected by active or predicted power shutoffs.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List # Added List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.functions import ST_X, ST_Y # Added for extracting lat/lon

from app.models.field import Field
from app.models.psps_event import PspsStatus # Added
from app.services.geo import GeoService
from app.services.psps_event_service import get_active_psps_events # Added

logger = logging.getLogger(__name__)


class PSPSService:
    """Service for PSPS (Public Safety Power Shutoff) impact assessment."""

    def __init__(self) -> None: # Removed psps_mcp parameter
        """Initialize PSPS service."""
        # self.psps_mcp = psps_mcp or PSPSMCP() # Removed
        self._seen_event_ids: set[str] = set()  # Track seen PSPS events to avoid duplicates

    async def check_shutoff_impact(
        self,
        db: AsyncSession,
        field_id: UUID,
        shutoff_areas: Optional[list[dict]] = None,
    ) -> bool:
        """
        Check if a field is affected by PSPS shutoffs.

        Args:
            db: Database session
            field_id: Field ID to check
            shutoff_areas: Optional list of shutoff area geometries (if None, fetches from MCP)

        Returns:
            True if field is affected by any shutoff, False otherwise
        """
        logger.info(f"Checking PSPS impact for field: {field_id}")

        # Get field with location
        field_query = select(Field).where(Field.id == field_id)
        field_result = await db.execute(field_query)
        field = field_result.scalar_one_or_none()

        if not field:
            logger.warning(f"Field not found: {field_id}")
            return False

        if not field.location_geom:
            logger.warning(f"Field {field_id} has no location geometry, cannot check PSPS impact")
            return False

        # If shutoff areas not provided, fetch from MCP
        if shutoff_areas is None:
            shutoff_areas = await self._fetch_shutoff_areas(field)

        if not shutoff_areas:
            logger.debug(f"No shutoff areas found for field {field_id}")
            return False

        # Check if field intersects with any shutoff area
        for shutoff_area in shutoff_areas:
            if await GeoService.does_field_intersect_zone(
                db, field.location_geom, shutoff_area
            ):
                logger.info(
                    f"Field {field_id} is affected by shutoff: {shutoff_area.get('id', 'unknown')}"
                )
                return True

        logger.debug(f"Field {field_id} is not affected by any shutoffs")
        return False

    async def _fetch_shutoff_areas(self, db: AsyncSession, field: Optional[Field] = None) -> list[dict]: # Added db parameter
        """
        Fetch shutoff areas from the database (previously from PSPS MCP server).

        Args:
            db: Database session # Added
            field: Optional field to get location from

        Returns:
            List of shutoff area dictionaries
        """
        logger.debug("Fetching shutoff areas from DB via psps_event_service")

        latitude = None
        longitude = None
        if field and field.location_geom:
            # Extract lat/lon from field.location_geom
            # Assuming field.location_geom is a PostGIS POINT
            latitude = await db.scalar(ST_Y(field.location_geom))
            longitude = await db.scalar(ST_X(field.location_geom))

        try:
            # Get both active and predicted shutoffs from the database
            active_events = await get_active_psps_events(
                db,
                latitude=latitude,
                longitude=longitude,
                status_filter=PspsStatus.ACTIVE,
            )
            predicted_events = await get_active_psps_events(
                db,
                latitude=latitude,
                longitude=longitude,
                status_filter=PspsStatus.PLANNED,
            )

            # Combine and format as shutoff areas
            all_events = active_events + predicted_events

            shutoff_areas = []
            for event in all_events:
                area = {
                    "id": event.id,
                    "utility": event.utility.value,
                    "status": event.status.value,
                    "start_time": event.starts_at.isoformat(),
                    "end_time": event.ends_at.isoformat() if event.ends_at else None,
                    "reason": event.properties.get("reason", "No specific reason provided"),
                    "affected_customers": event.properties.get("affected_customers"),
                    "counties": event.properties.get("counties"),
                    "geometry": json.loads(await db.scalar(ST_AsGeoJSON(event.geom))), # Convert geom to GeoJSON
                }
                shutoff_areas.append(area)

            logger.debug(f"Fetched {len(shutoff_areas)} shutoff areas from DB")
            return shutoff_areas

        except Exception as e:
            logger.error(f"Error fetching shutoff areas from DB: {e}")
            return []

    async def get_affected_fields(
        self,
        db: AsyncSession,
        farm_id: Optional[str] = None,
    ) -> list[tuple[Field, dict]]:
        """
        Get all fields affected by PSPS shutoffs.

        Args:
            db: Database session
            farm_id: Optional farm ID to filter fields

        Returns:
            List of tuples (Field, shutoff_info) for affected fields
        """
        logger.info(f"Finding fields affected by PSPS shutoffs: farm_id={farm_id}")

        # Get all fields (or filter by farm_id)
        query = select(Field)
        if farm_id:
            query = query.where(Field.farm_id == farm_id)

        fields_result = await db.execute(query)
        fields = list(fields_result.scalars().all())

        affected_fields: list[tuple[Field, dict]] = []

        # Fetch shutoff areas once (use first field for location if available)
        reference_field = fields[0] if fields else None
        shutoff_areas = await self._fetch_shutoff_areas(reference_field) if fields else []

        # Check each field
        for field in fields:
            if not field.location_geom:
                continue

            # Check if field is affected
            for shutoff_area in shutoff_areas:
                if await GeoService.does_field_intersect_zone(
                    db, field.location_geom, shutoff_area
                ):
                    affected_fields.append((field, shutoff_area))
                    logger.info(
                        f"Field {field.id} ({field.name}) is affected by shutoff {shutoff_area.get('id')}"
                    )
                    break  # Only add once per field

        logger.info(f"Found {len(affected_fields)} fields affected by PSPS shutoffs")
        return affected_fields

    def is_new_event(self, event_id: str) -> bool:
        """
        Check if a PSPS event is new (not seen before).

        Args:
            event_id: PSPS event ID

        Returns:
            True if event is new, False if already seen
        """
        is_new = event_id not in self._seen_event_ids
        if is_new:
            self._seen_event_ids.add(event_id)
            logger.debug(f"New PSPS event detected: {event_id}")
        return is_new

    def clear_seen_events(self) -> None:
        """Clear the set of seen event IDs (useful for testing or periodic cleanup)."""
        self._seen_event_ids.clear()
        logger.debug("Cleared seen PSPS event IDs")

