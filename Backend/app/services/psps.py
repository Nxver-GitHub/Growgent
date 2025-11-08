"""
PSPS service for checking utility shutoff impact on fields.

This service polls PSPS data from MCP servers and determines which fields
are affected by active or predicted power shutoffs.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.field import Field
from app.mcp.psps import PSPSMCP
from app.services.geo import GeoService

logger = logging.getLogger(__name__)


class PSPSService:
    """Service for PSPS (Public Safety Power Shutoff) impact assessment."""

    def __init__(self, psps_mcp: Optional[PSPSMCP] = None) -> None:
        """
        Initialize PSPS service.

        Args:
            psps_mcp: Optional PSPS MCP instance (creates new one if not provided)
        """
        self.psps_mcp = psps_mcp or PSPSMCP()
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

    async def _fetch_shutoff_areas(self, field: Optional[Field] = None) -> list[dict]:
        """
        Fetch shutoff areas from PSPS MCP server.

        Args:
            field: Optional field to get location from

        Returns:
            List of shutoff area dictionaries
        """
        logger.debug("Fetching shutoff areas from PSPS MCP")

        try:
            # Extract lat/lon from field location if available
            # For now, we'll fetch all shutoffs and filter by geometry
            latitude = None
            longitude = None

            # TODO: Extract coordinates from field.location_geom if it's a POINT
            # For MVP, we'll fetch all shutoffs and use GeoService to filter

            # Get both active and predicted shutoffs
            active_shutoffs = await self.psps_mcp.get_active_shutoffs(latitude, longitude)
            predicted_shutoffs = await self.psps_mcp.get_predicted_shutoffs(
                latitude, longitude, hours_ahead=48
            )

            # Combine and format as shutoff areas
            all_shutoffs = active_shutoffs + predicted_shutoffs

            # Convert to shutoff area format (with geometry if available)
            shutoff_areas = []
            for shutoff in all_shutoffs:
                # For MVP, shutoff areas are represented by counties
                # In production, these would have actual GeoJSON geometries
                area = {
                    "id": shutoff.get("id", "unknown"),
                    "utility": shutoff.get("utility", "unknown"),
                    "status": shutoff.get("status", "UNKNOWN"),
                    "counties": shutoff.get("counties", []),
                    "start_time": shutoff.get("start_time") or shutoff.get("predicted_start_time"),
                    "end_time": shutoff.get("estimated_end_time") or shutoff.get("predicted_end_time"),
                    "geometry": None,  # Would contain GeoJSON in production
                }
                shutoff_areas.append(area)

            logger.debug(f"Fetched {len(shutoff_areas)} shutoff areas from PSPS MCP")
            return shutoff_areas

        except Exception as e:
            logger.error(f"Error fetching shutoff areas from PSPS MCP: {e}")
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

