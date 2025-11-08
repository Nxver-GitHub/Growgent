"""
Geo service for PostGIS spatial queries.

This service handles geospatial operations like checking if fields intersect
with shutoff zones, fire risk areas, etc.
"""

import logging
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class GeoService:
    """Service for geospatial queries using PostGIS."""

    @staticmethod
    async def does_field_intersect_zone(
        db: AsyncSession,
        field_geom: Any,
        zone_data: dict[str, Any],
    ) -> bool:
        """
        Check if a field geometry intersects with a zone (shutoff area, fire zone, etc.).

        Args:
            db: Database session
            field_geom: Field geometry (PostGIS geometry type)
            zone_data: Zone data dictionary containing geometry or location info

        Returns:
            True if field intersects with zone, False otherwise
        """
        logger.debug(f"Checking field intersection with zone: {zone_data.get('id', 'unknown')}")

        # If zone has explicit geometry (GeoJSON), use PostGIS ST_Intersects
        if zone_data.get("geometry"):
            geometry = zone_data["geometry"]
            return await GeoService._intersects_geometry(db, field_geom, geometry)

        # If zone has counties, check if field is in those counties
        # For MVP, we'll use a simplified county-based check
        # In production, this would use actual county boundary geometries
        if zone_data.get("counties"):
            counties = zone_data["counties"]
            # For MVP, we'll do a simple check based on field location
            # This is a placeholder - in production, use actual county boundaries
            logger.debug(f"Zone has counties: {counties}, using simplified check")
            # TODO: Implement proper county boundary intersection
            # For now, return True if we have county info (simplified for MVP)
            return len(counties) > 0

        # If no geometry or county info, cannot determine intersection
        logger.warning("Zone has no geometry or county information, cannot check intersection")
        return False

    @staticmethod
    async def _intersects_geometry(
        db: AsyncSession,
        field_geom: Any,
        zone_geometry: dict[str, Any],
    ) -> bool:
        """
        Check if field geometry intersects with zone geometry using PostGIS.

        Args:
            db: Database session
            field_geom: Field geometry
            zone_geometry: Zone geometry as GeoJSON dict

        Returns:
            True if geometries intersect
        """
        try:
            # Convert GeoJSON to PostGIS geometry and check intersection
            # Format: ST_Intersects(field_geom, ST_GeomFromGeoJSON(zone_geometry))
            query = text(
                """
                SELECT ST_Intersects(
                    :field_geom,
                    ST_GeomFromGeoJSON(:zone_geometry)
                ) AS intersects
                """
            )

            # Convert zone_geometry dict to GeoJSON string
            import json
            zone_geojson = json.dumps(zone_geometry)

            result = await db.execute(
                query,
                {
                    "field_geom": field_geom,
                    "zone_geometry": zone_geojson,
                },
            )

            row = result.fetchone()
            if row:
                intersects = row[0]
                logger.debug(f"Geometry intersection result: {intersects}")
                return bool(intersects)

            return False

        except Exception as e:
            logger.error(f"Error checking geometry intersection: {e}")
            # On error, return False to be safe
            return False

    @staticmethod
    async def get_fields_in_radius(
        db: AsyncSession,
        center_latitude: float,
        center_longitude: float,
        radius_km: float,
    ) -> list[Any]:
        """
        Get all fields within a radius of a center point.

        Args:
            db: Database session
            center_latitude: Center point latitude
            center_longitude: Center point longitude
            radius_km: Radius in kilometers

        Returns:
            List of Field objects within radius
        """
        logger.debug(
            f"Finding fields within {radius_km}km of ({center_latitude}, {center_longitude})"
        )

        try:
            # Use PostGIS ST_DWithin to find fields within radius
            query = text(
                """
                SELECT f.*
                FROM fields f
                WHERE ST_DWithin(
                    f.location_geom::geography,
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                    :radius_meters
                )
                """
            )

            # Convert radius from km to meters
            radius_meters = radius_km * 1000.0

            result = await db.execute(
                query,
                {
                    "lat": center_latitude,
                    "lon": center_longitude,
                    "radius_meters": radius_meters,
                },
            )

            fields = result.fetchall()
            logger.debug(f"Found {len(fields)} fields within radius")
            return fields

        except Exception as e:
            logger.error(f"Error finding fields in radius: {e}")
            return []

    @staticmethod
    async def get_fields_in_polygon(
        db: AsyncSession,
        polygon_geojson: dict[str, Any],
    ) -> list[Any]:
        """
        Get all fields within a polygon (e.g., shutoff zone, fire risk area).

        Args:
            db: Database session
            polygon_geojson: Polygon as GeoJSON dictionary

        Returns:
            List of Field objects within polygon
        """
        logger.debug("Finding fields within polygon")

        try:
            import json

            # Convert GeoJSON to PostGIS geometry and find fields within
            query = text(
                """
                SELECT f.*
                FROM fields f
                WHERE ST_Within(
                    f.location_geom,
                    ST_GeomFromGeoJSON(:polygon_geojson)
                )
                """
            )

            polygon_json = json.dumps(polygon_geojson)

            result = await db.execute(
                query,
                {"polygon_geojson": polygon_json},
            )

            fields = result.fetchall()
            logger.debug(f"Found {len(fields)} fields within polygon")
            return fields

        except Exception as e:
            logger.error(f"Error finding fields in polygon: {e}")
            return []

