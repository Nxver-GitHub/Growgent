"""
Service layer for zone operations.

Handles business logic for CRUD operations on risk zones with PostGIS geometry.
"""

import json
import logging
from typing import Optional
from uuid import UUID

from shapely.geometry import shape as shapely_shape
from shapely import wkt
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.zone import Zone, ZoneType, RiskLevel

logger = logging.getLogger(__name__)


class ZoneService:
    """Service for zone management."""

    @staticmethod
    def _geojson_to_wkt(geojson: Optional[dict]) -> Optional[str]:
        """
        Convert GeoJSON geometry to PostGIS WKT format.

        Args:
            geojson: GeoJSON geometry dict

        Returns:
            PostGIS WKT string or None
        """
        if not geojson:
            return None

        try:
            # Use shapely to convert GeoJSON to WKT
            geom = shapely_shape(geojson)
            return wkt.dumps(geom)
        except Exception as e:
            logger.error(f"Error converting GeoJSON to WKT: {e}")
            raise ValueError(f"Invalid GeoJSON geometry: {e}")

    @staticmethod
    def _wkt_to_geojson(wkt_str: Optional[str]) -> Optional[dict]:
        """
        Convert PostGIS WKT geometry to GeoJSON format.

        Args:
            wkt_str: PostGIS WKT geometry string

        Returns:
            GeoJSON geometry dict or None
        """
        if not wkt_str:
            return None

        try:
            # Parse WKT to shapely geometry, then to GeoJSON
            geom = wkt.loads(wkt_str)
            return geom.__geo_interface__
        except Exception as e:
            logger.error(f"Error converting WKT to GeoJSON: {e}")
            return None

    @staticmethod
    async def create_zone(
        db: AsyncSession,
        name: str,
        zone_type: ZoneType,
        risk_level: RiskLevel,
        description: Optional[str] = None,
        geometry: Optional[dict] = None,
        field_id: Optional[str] = None,
        farm_id: Optional[str] = None,
        extra_metadata: Optional[dict] = None,
    ) -> Zone:
        """
        Create a new zone.

        Args:
            db: Database session
            name: Zone name
            zone_type: Zone type
            risk_level: Risk level
            description: Optional description
            geometry: GeoJSON geometry dict
            field_id: Optional field ID
            farm_id: Optional farm ID
            extra_metadata: Optional metadata dict

        Returns:
            Created Zone instance
        """
        logger.debug(f"Creating zone: name={name}, type={zone_type}, risk={risk_level}")

        # Convert GeoJSON to PostGIS WKT
        geometry_wkt = ZoneService._geojson_to_wkt(geometry) if geometry else None

        # Serialize metadata to JSON string
        metadata_str = json.dumps(extra_metadata) if extra_metadata else None

        zone = Zone(
            name=name,
            description=description,
            zone_type=zone_type,
            risk_level=risk_level,
            geometry=geometry_wkt,
            field_id=field_id,
            farm_id=farm_id,
            extra_metadata=metadata_str,
        )

        db.add(zone)
        await db.commit()
        await db.refresh(zone)

        logger.info(f"Zone created: id={zone.id}, name={name}")
        return zone

    @staticmethod
    async def get_zone(
        db: AsyncSession,
        zone_id: UUID,
    ) -> Optional[Zone]:
        """
        Get a single zone by ID.

        Args:
            db: Database session
            zone_id: Zone ID

        Returns:
            Zone instance or None if not found
        """
        logger.debug(f"Fetching zone: id={zone_id}")

        query = select(Zone).where(Zone.id == zone_id)
        result = await db.execute(query)
        zone = result.scalar_one_or_none()

        if zone:
            logger.debug(f"Zone found: id={zone_id}, name={zone.name}")
        else:
            logger.debug(f"Zone not found: id={zone_id}")

        return zone

    @staticmethod
    async def list_zones(
        db: AsyncSession,
        zone_type: Optional[ZoneType] = None,
        risk_level: Optional[RiskLevel] = None,
        field_id: Optional[str] = None,
        farm_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Zone], int]:
        """
        List zones with optional filtering and pagination.

        Args:
            db: Database session
            zone_type: Optional zone type filter
            risk_level: Optional risk level filter
            field_id: Optional field ID filter
            farm_id: Optional farm ID filter
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (zones list, total count)
        """
        logger.debug(
            f"Listing zones: type={zone_type}, risk={risk_level}, "
            f"field_id={field_id}, farm_id={farm_id}, page={page}, page_size={page_size}"
        )

        # Build query
        query = select(Zone)

        if zone_type:
            query = query.where(Zone.zone_type == zone_type)
        if risk_level:
            query = query.where(Zone.risk_level == risk_level)
        if field_id:
            query = query.where(Zone.field_id == field_id)
        if farm_id:
            query = query.where(Zone.farm_id == farm_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar_one() or 0

        # Apply pagination and ordering
        query = query.order_by(desc(Zone.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        zones = list(result.scalars().all())

        logger.debug(f"Found {len(zones)} zones (total: {total})")
        return zones, total

    @staticmethod
    def _zone_to_dict(zone: Zone) -> dict:
        """
        Convert a Zone model instance to a dict with GeoJSON geometry.

        Args:
            zone: Zone instance

        Returns:
            Dict with zone data and GeoJSON geometry
        """
        # Convert geometry to GeoJSON
        geometry_geojson = None
        if zone.geometry:
            try:
                # Try converting WKT to GeoJSON using shapely
                geom_str = str(zone.geometry)
                geometry_geojson = ZoneService._wkt_to_geojson(geom_str)
            except Exception as e:
                logger.warning(f"Error converting zone geometry to GeoJSON: {e}")
                geometry_geojson = None

        zone_dict = {
            "id": zone.id,
            "name": zone.name,
            "description": zone.description,
            "zone_type": zone.zone_type,
            "risk_level": zone.risk_level,
            "geometry": geometry_geojson,
            "field_id": zone.field_id,
            "farm_id": zone.farm_id,
            "extra_metadata": json.loads(zone.extra_metadata) if zone.extra_metadata else None,
            "created_at": zone.created_at,
            "updated_at": zone.updated_at,
        }
        return zone_dict

    @staticmethod
    async def update_zone(
        db: AsyncSession,
        zone_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        zone_type: Optional[ZoneType] = None,
        risk_level: Optional[RiskLevel] = None,
        geometry: Optional[dict] = None,
        field_id: Optional[str] = None,
        farm_id: Optional[str] = None,
        extra_metadata: Optional[dict] = None,
    ) -> Optional[Zone]:
        """
        Update a zone.

        Args:
            db: Database session
            zone_id: Zone ID
            name: Optional new name
            description: Optional new description
            zone_type: Optional new zone type
            risk_level: Optional new risk level
            geometry: Optional new GeoJSON geometry
            field_id: Optional new field ID
            farm_id: Optional new farm ID
            extra_metadata: Optional new metadata dict

        Returns:
            Updated Zone instance or None if not found
        """
        logger.debug(f"Updating zone: id={zone_id}")

        zone = await ZoneService.get_zone(db=db, zone_id=zone_id)
        if not zone:
            return None

        # Update fields if provided
        if name is not None:
            zone.name = name
        if description is not None:
            zone.description = description
        if zone_type is not None:
            zone.zone_type = zone_type
        if risk_level is not None:
            zone.risk_level = risk_level
        if geometry is not None:
            zone.geometry = ZoneService._geojson_to_wkt(geometry)
        if field_id is not None:
            zone.field_id = field_id
        if farm_id is not None:
            zone.farm_id = farm_id
        if extra_metadata is not None:
            zone.extra_metadata = json.dumps(extra_metadata)

        await db.commit()
        await db.refresh(zone)

        logger.info(f"Zone updated: id={zone_id}")
        return zone

    @staticmethod
    async def delete_zone(
        db: AsyncSession,
        zone_id: UUID,
    ) -> bool:
        """
        Delete a zone.

        Args:
            db: Database session
            zone_id: Zone ID

        Returns:
            True if deleted, False if not found
        """
        logger.debug(f"Deleting zone: id={zone_id}")

        zone = await ZoneService.get_zone(db=db, zone_id=zone_id)
        if not zone:
            return False

        await db.delete(zone)
        await db.commit()

        logger.info(f"Zone deleted: id={zone_id}")
        return True

