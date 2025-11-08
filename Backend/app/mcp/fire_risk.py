"""
Fire Risk MCP Server implementation.

Provides fire risk zones and evacuation areas from NOAA/Cal Fire APIs
with mock data fallback.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession
from geoalchemy2.functions import ST_DWithin, ST_GeomFromText, ST_AsGeoJSON # Import PostGIS functions
import json # Import json for GeoJSON conversion

from app.config import settings
from app.database import get_db # Import get_db to get a session
# Removed: from app.services.fire_perimeter_service import get_active_fire_perimeters, sync_fire_perimeters
from app.models.fire_perimeter import FirePerimeter # Import the model

logger = logging.getLogger(__name__)


class FireRiskMCP:
    """
    Fire Risk MCP Server.

    Fetches fire risk zones and evacuation areas from NOAA and Cal Fire APIs
    with graceful fallback to mock data.
    """

    def __init__(self) -> None:
        """Initialize Fire Risk MCP server."""
        self.noaa_api_key = settings.noaa_api_key or ""
        self.fire_perimeters_feature_server_url = settings.fire_perimeters_feature_server_url or ""
        self.use_mock = (
            not self.noaa_api_key
            and not self.fire_perimeters_feature_server_url
            or settings.environment == "development"
        )

    async def get_fire_risk_zones(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
    ) -> Dict[str, Any]:
        """
        Get fire risk zones for a location.

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            radius_km: Search radius in kilometers (default: 50.0)

        Returns:
            Dictionary containing fire risk zone data
        """
        if self.use_mock:
            logger.info("Using mock fire risk zone data")
            return self._get_mock_fire_risk_zones(latitude, longitude, radius_km)

        try:
            # Use get_db to get an async session
            async for db in get_db():
                return await self._get_real_fire_risk_zones(db, latitude, longitude, radius_km)
        except Exception as e:
            logger.warning(f"Failed to fetch real fire risk data: {e}, using mock")
            return self._get_mock_fire_risk_zones(latitude, longitude, radius_km)

    async def _get_real_fire_risk_zones(
        self,
        db: AsyncSession, # Pass db session
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> Dict[str, Any]:
        """
        Fetch fire risk zones from NOAA/Cal Fire APIs and active fire perimeters.

        Args:
            db: Database session
            latitude: Latitude
            longitude: Longitude
            radius_km: Radius in km

        Returns:
            Fire risk zone data
        """
        # Import here to avoid circular dependency
        from app.services.fire_perimeter_service import get_active_fire_perimeters, sync_fire_perimeters

        # First, sync fire perimeters from the external source to ensure data is fresh
        if self.fire_perimeters_feature_server_url:
            await sync_fire_perimeters(db)
            logger.info("Synchronized active fire perimeters.")

        # Query for fire perimeters within the radius
        # Convert radius_km to meters for ST_DWithin (1 km = 1000 meters)
        search_point = ST_GeomFromText(f"POINT({longitude} {latitude})", 4326)
        perimeters_query = (
            select(FirePerimeter)
            .where(ST_DWithin(FirePerimeter.geom, search_point, radius_km * 1000))
        )
        perimeters_result = await db.execute(perimeters_query)
        fire_perimeters = perimeters_result.scalars().all()

        zones_data = []
        for fp in fire_perimeters:
            # Convert PostGIS geometry to GeoJSON
            geojson_geom = json.loads(await db.scalar(ST_AsGeoJSON(fp.geom)))
            zones_data.append({
                "id": fp.id,
                "name": fp.fire_name or "Active Fire",
                "risk_level": "CRITICAL", # Active fires are critical
                "risk_score": 0.95, # High score for active fires
                "geometry": geojson_geom,
                "factors": {
                    "agency": fp.agency,
                    "updated_at": fp.updated_at.isoformat(),
                    **fp.properties # Include all original properties
                },
            })

        # Add other fire risk zones (e.g., from NOAA Fire Weather API) if integrated
        # For now, we'll just return the active fire perimeters as the primary "zones"
        # If NOAA integration is added, it would go here and merge with zones_data

        if not zones_data:
            logger.info("No active fire perimeters found within radius, falling back to mock fire risk zones.")
            return self._get_mock_fire_risk_zones(latitude, longitude, radius_km)

        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "zones": zones_data,
        }

    def _get_mock_fire_risk_zones(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> Dict[str, Any]:
        """
        Generate mock fire risk zone data.

        Args:
            latitude: Latitude
            longitude: Longitude
            radius_km: Radius in km

        Returns:
            Mock fire risk zone data
        """
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "zones": [
                {
                    "id": "zone-001",
                    "name": "High Fire Risk Zone A",
                    "risk_level": "HIGH",
                    "risk_score": 0.85,
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [longitude - 0.02, latitude - 0.02],
                            [longitude + 0.02, latitude - 0.02],
                            [longitude + 0.02, latitude + 0.02],
                            [longitude - 0.02, latitude + 0.02],
                            [longitude - 0.02, latitude - 0.02],
                        ]],
                    },
                    "factors": {
                        "fuel_moisture": "Very Dry",
                        "wind_speed": "High",
                        "temperature": "Above Average",
                    },
                },
                {
                    "id": "zone-002",
                    "name": "Moderate Fire Risk Zone B",
                    "risk_level": "MODERATE",
                    "risk_score": 0.55,
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [longitude - 0.01, latitude - 0.01],
                            [longitude + 0.01, latitude - 0.01],
                            [longitude + 0.01, latitude + 0.01],
                            [longitude - 0.01, latitude + 0.01],
                            [longitude - 0.01, latitude - 0.01],
                        ]],
                    },
                    "factors": {
                        "fuel_moisture": "Dry",
                        "wind_speed": "Moderate",
                        "temperature": "Average",
                    },
                },
            ],
        }

    async def get_evacuation_areas(
        self,
        latitude: float,
        longitude: float,
    ) -> List[Dict[str, Any]]:
        """
        Get evacuation areas near a location.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            List of evacuation areas
        """
        if self.use_mock:
            logger.info("Using mock evacuation area data")
            return self._get_mock_evacuation_areas(latitude, longitude)

        try:
            return await self._get_real_evacuation_areas(latitude, longitude)
        except Exception as e:
            logger.warning(f"Failed to fetch real evacuation data: {e}, using mock")
            return self._get_mock_evacuation_areas(latitude, longitude)

    async def _get_real_evacuation_areas(
        self,
        latitude: float,
        longitude: float,
    ) -> List[Dict[str, Any]]:
        """
        Fetch evacuation areas from Cal Fire API.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            List of evacuation areas
        """
        # Placeholder for real API integration
        return self._get_mock_evacuation_areas(latitude, longitude)

    def _get_mock_evacuation_areas(
        self,
        latitude: float,
        longitude: float,
    ) -> List[Dict[str, Any]]:
        """
        Generate mock evacuation area data.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            List of mock evacuation areas
        """
        return [
            {
                "id": "evac-001",
                "name": "Sonoma County Evacuation Zone",
                "status": "WARNING",  # WARNING, MANDATORY, CLEARED
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [longitude - 0.05, latitude - 0.05],
                        [longitude + 0.05, latitude - 0.05],
                        [longitude + 0.05, latitude + 0.05],
                        [longitude - 0.05, latitude + 0.05],
                        [longitude - 0.05, latitude - 0.05],
                    ]],
                },
                "issued_at": "2025-01-07T10:00:00Z",
            },
        ]


# Global instance
fire_risk_mcp = FireRiskMCP()

