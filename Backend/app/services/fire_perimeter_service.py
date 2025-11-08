# backend/app/services/fire_perimeter_service.py

import logging
import httpx
from shapely.geometry import shape
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

from ..config import settings
from ..models.fire_perimeter import FirePerimeter
from ..schemas.fire_perimeter import FirePerimeterFeature

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_fire_perimeters(db: AsyncSession):
    """
    Fetches active fire perimeters from the configured FeatureServer,
    validates them, and upserts them into the database.
    """
    if not settings.fire_perimeters_feature_server_url:
        logger.warning("FIRE_PERIMETERS_FEATURE_SERVER_URL is not set. Skipping sync.")
        return

    logger.info("Starting fire perimeter synchronization...")
    
    try:
        # 1. Fetch data from the external API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.fire_perimeters_feature_server_url,
                timeout=30.0
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()

        features = data.get("features", [])
        if not features:
            logger.info("No fire perimeter features found in the source data.")
            return

        perimeters_to_upsert = []
        for feature_data in features:
            try:
                # 2. Validate each feature using the Pydantic schema
                feature = FirePerimeterFeature.model_validate(feature_data)

                # Use a stable unique identifier from the source
                source_id = str(feature.properties.poly_SourceOID)
                if not source_id:
                    continue # Skip features without a unique ID

                # 3. Convert GeoJSON geometry to WKT for GeoAlchemy2
                geom_shape = shape(feature.geometry.model_dump())
                geom_wkt = f"SRID=4326;{geom_shape.wkt}"

                perimeter_dict = {
                    "id": source_id,
                    "fire_name": feature.properties.poly_IncidentName,
                    "geom": geom_wkt,
                    # Store all original properties for future use
                    "properties": feature.properties.model_dump(by_alias=True),
                    "agency": "NIFC/FIRIS" # Placeholder, can be refined later
                }
                perimeters_to_upsert.append(perimeter_dict)
            except Exception as e:
                logger.error(f"Failed to process feature: {feature_data}. Error: {e}")

        if not perimeters_to_upsert:
            logger.info("No valid perimeters to upsert after processing.")
            return

        # 4. Perform an efficient "upsert" operation
        stmt = insert(FirePerimeter).values(perimeters_to_upsert)

        # On conflict (if 'id' already exists), update these fields
        on_conflict_stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_={
                "fire_name": stmt.excluded.fire_name,
                "geom": stmt.excluded.geom,
                "properties": stmt.excluded.properties,
                "updated_at": func.now() # Update the timestamp
            }
        )

        await db.execute(on_conflict_stmt)
        await db.commit()

        logger.info(f"Successfully synchronized {len(perimeters_to_upsert)} fire perimeters.")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred while fetching fire data: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during fire perimeter sync: {e}")
        await db.rollback()


async def get_active_fire_perimeters(db: AsyncSession):
    """
    Retrieves all active fire perimeters from the database.
    """
    result = await db.execute(
        select(FirePerimeter)
    )
    return result.scalars().all()
