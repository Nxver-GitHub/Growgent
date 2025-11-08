"""
Farm service for farm management.

Handles farm creation, updates, and relationship management with users and fields.
"""

import logging
from typing import Optional
from uuid import UUID

from geoalchemy2 import WKTElement
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.farm import Farm
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmUpdate

logger = logging.getLogger(__name__)


class FarmService:
    """Service for farm management."""

    @staticmethod
    def _create_location_geom(latitude: Optional[float], longitude: Optional[float]) -> Optional[WKTElement]:
        """
        Create PostGIS geometry from latitude/longitude.

        Args:
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)

        Returns:
            PostGIS WKTElement or None
        """
        if latitude is None or longitude is None:
            return None

        # PostGIS uses POINT(longitude latitude) format
        return WKTElement(f"POINT({longitude} {latitude})", srid=4326)

    @staticmethod
    async def create_farm(
        db: AsyncSession,
        farm_data: FarmCreate,
    ) -> Farm:
        """
        Create a new farm.

        Args:
            db: Database session
            farm_data: Farm creation data

        Returns:
            Created farm
        """
        # Verify owner exists
        owner = await db.get(User, farm_data.owner_id)
        if not owner:
            raise ValueError(f"User with id {farm_data.owner_id} not found")

        # Create location geometry if provided
        location_geom = FarmService._create_location_geom(
            farm_data.latitude,
            farm_data.longitude,
        )

        # Create farm
        farm = Farm(
            owner_id=farm_data.owner_id,
            name=farm_data.name,
            farm_id=farm_data.farm_id,
            address=farm_data.address,
            city=farm_data.city,
            state=farm_data.state,
            zip_code=farm_data.zip_code,
            country=farm_data.country or "USA",
            contact_email=farm_data.contact_email,
            contact_phone=farm_data.contact_phone,
            notes=farm_data.notes,
            location_geom=location_geom,
        )
        db.add(farm)
        await db.commit()
        await db.refresh(farm)

        logger.info(f"Created farm: {farm.name} (id: {farm.id}, farm_id: {farm.farm_id})")
        return farm

    @staticmethod
    async def get_farm(
        db: AsyncSession,
        farm_id: UUID,
        include_fields: bool = False,
    ) -> Optional[Farm]:
        """
        Get farm by ID.

        Args:
            db: Database session
            farm_id: Farm UUID
            include_fields: Whether to include fields

        Returns:
            Farm if found, None otherwise
        """
        query = select(Farm).where(Farm.id == farm_id)

        if include_fields:
            query = query.options(selectinload(Farm.fields))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_farm_by_farm_id(
        db: AsyncSession,
        farm_id_str: str,
        include_fields: bool = False,
    ) -> Optional[Farm]:
        """
        Get farm by farm_id string (legacy identifier).

        Args:
            db: Database session
            farm_id_str: Farm ID string
            include_fields: Whether to include fields

        Returns:
            Farm if found, None otherwise
        """
        query = select(Farm).where(Farm.farm_id == farm_id_str)

        if include_fields:
            query = query.options(selectinload(Farm.fields))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_farm(
        db: AsyncSession,
        farm_id: UUID,
        farm_data: FarmUpdate,
    ) -> Optional[Farm]:
        """
        Update farm information.

        Args:
            db: Database session
            farm_id: Farm UUID
            farm_data: Farm update data

        Returns:
            Updated farm if found, None otherwise
        """
        farm = await FarmService.get_farm(db, farm_id, include_fields=False)
        if not farm:
            return None

        # Update fields
        update_data = farm_data.model_dump(exclude_unset=True)

        # Handle location geometry
        if "latitude" in update_data or "longitude" in update_data:
            latitude = update_data.pop("latitude", None)
            longitude = update_data.pop("longitude", None)
            farm.location_geom = FarmService._create_location_geom(latitude, longitude)

        for field, value in update_data.items():
            setattr(farm, field, value)

        await db.commit()
        await db.refresh(farm)

        logger.info(f"Updated farm: {farm.name} (id: {farm.id})")
        return farm

    @staticmethod
    async def list_farms_by_owner(
        db: AsyncSession,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Farm]:
        """
        List farms owned by a user.

        Args:
            db: Database session
            owner_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of farms
        """
        query = (
            select(Farm)
            .where(Farm.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_farm_with_field_count(
        db: AsyncSession,
        farm_id: UUID,
    ) -> Optional[dict]:
        """
        Get farm with field count.

        Args:
            db: Database session
            farm_id: Farm UUID

        Returns:
            Farm data with field count, or None if not found
        """
        from app.models.field import Field

        result = await db.execute(
            select(
                Farm,
                func.count(Field.id).label("fields_count"),
            )
            .outerjoin(Field, Farm.id == Field.farm_uuid)
            .where(Farm.id == farm_id)
            .group_by(Farm.id)
        )
        row = result.first()
        if not row:
            return None

        farm, fields_count = row
        return {
            "farm": farm,
            "fields_count": fields_count or 0,
        }

