"""
Service for synchronizing and retrieving PSPS (Public Safety Power Shutoff) events.

Fetches PSPS events from configured utility FeatureServer URLs and upserts them into the database.
"""

import logging
import httpx
from shapely.geometry import shape
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, select
import json
from typing import Optional, List # Added List

from app.config import settings
from app.models.psps_event import PspsEvent, PspsUtility, PspsStatus
from app.schemas.psps_event import PspsEventFeature, PspsEventProperties

logger = logging.getLogger(__name__)


async def sync_psps_events(db: AsyncSession):
    """
    Fetches PSPS events from configured FeatureServer URLs,
    validates them, and upserts them into the database.
    """
    if not settings.psps_feature_server_urls:
        logger.warning("PSPS_FEATURE_SERVER_URLS is not set. Skipping sync.")
        return

    feature_server_urls = [url.strip() for url in settings.psps_feature_server_urls.split(',') if url.strip()]
    if not feature_server_urls:
        logger.warning("No valid PSPS FeatureServer URLs found. Skipping sync.")
        return

    logger.info(f"Starting PSPS event synchronization from {len(feature_server_urls)} sources...")

    all_events_to_upsert = []
    for url in feature_server_urls:
        try:
            # 1. Fetch data from the external API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    timeout=30.0
                )
                response.raise_for_status()  # Raise an exception for bad status codes
                data = response.json()

            features = data.get("features", [])
            if not features:
                logger.info(f"No PSPS features found in source data from {url}.")
                continue

            for feature_data in features:
                try:
                    # 2. Validate each feature using the Pydantic schema
                    # Use PspsEventProperties to parse properties, allowing extra fields
                    properties_data = feature_data.get("properties", {})
                    geometry_data = feature_data.get("geometry", {})

                    # Attempt to extract known fields for PspsEvent model
                    utility_str = properties_data.get("utility_name") or properties_data.get("utility")
                    status_str = properties_data.get("event_status") or properties_data.get("status")
                    start_time_str = properties_data.get("start_time")
                    end_time_str = properties_data.get("end_time")
                    
                    # Determine utility enum
                    utility_enum = PspsUtility.OTHER
                    if utility_str:
                        for member in PspsUtility:
                            if member.value.lower() == utility_str.lower():
                                utility_enum = member
                                break
                    
                    # Determine status enum
                    status_enum = PspsStatus.PLANNED # Default to planned if unknown
                    if status_str:
                        for member in PspsStatus:
                            if member.value.lower() == status_str.lower():
                                status_enum = member
                                break

                    # Parse dates
                    starts_at = None
                    if start_time_str:
                        try:
                            starts_at = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                        except ValueError:
                            logger.warning(f"Could not parse start_time: {start_time_str}")

                    ends_at = None
                    if end_time_str:
                        try:
                            ends_at = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                        except ValueError:
                            logger.warning(f"Could not parse end_time: {end_time_str}")

                    # Use a stable unique identifier from the source
                    source_id = properties_data.get("utility_id") or properties_data.get("id")
                    if not source_id:
                        logger.warning(f"Skipping PSPS feature from {url} without a unique ID: {properties_data}")
                        continue

                    # 3. Convert GeoJSON geometry to WKT for GeoAlchemy2
                    geom_shape = shape(geometry_data)
                    geom_wkt = f"SRID=4326;{geom_shape.wkt}"

                    event_dict = {
                        "id": source_id,
                        "utility": utility_enum,
                        "status": status_enum,
                        "starts_at": starts_at,
                        "ends_at": ends_at,
                        "geom": geom_wkt,
                        "properties": properties_data, # Store all original properties
                    }
                    all_events_to_upsert.append(event_dict)
                except Exception as e:
                    logger.error(f"Failed to process PSPS feature from {url}: {feature_data}. Error: {e}")
        except httpx.HTTPStatusError as e: # Moved this except block to be inside the for loop's try
            logger.error(f"HTTP error occurred while fetching PSPS data from {url}: {e}")
        except Exception as e: # Moved this except block to be inside the for loop's try
            logger.error(f"An unexpected error occurred during PSPS sync from {url}: {e}")
            await db.rollback() # Rollback only for the current URL's processing

    if not all_events_to_upsert:
        logger.info("No valid PSPS events to upsert after processing all sources.")
        return

    # 4. Perform an efficient "upsert" operation
    stmt = insert(PspsEvent).values(all_events_to_upsert)

    # On conflict (if 'id' already exists), update these fields
    on_conflict_stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_={
            "utility": stmt.excluded.utility,
            "status": stmt.excluded.status,
            "starts_at": stmt.excluded.starts_at,
            "ends_at": stmt.excluded.ends_at,
            "geom": stmt.excluded.geom,
            "properties": stmt.excluded.properties,
            "updated_at": func.now() # Update the timestamp
        }
    )

    await db.execute(on_conflict_stmt)
    await db.commit()

    logger.info(f"Successfully synchronized {len(all_events_to_upsert)} PSPS events.")


async def get_active_psps_events(
    db: AsyncSession,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 0.1, # Small radius for point intersection
    status_filter: Optional[PspsStatus] = None,
) -> List[PspsEvent]:
    """
    Retrieves active PSPS events from the database, optionally filtered by location and status.
    """
    query = select(PspsEvent).where(PspsEvent.status != PspsStatus.COMPLETED) # Only active/planned/restoring

    if status_filter:
        query = query.where(PspsEvent.status == status_filter)

    if latitude is not None and longitude is not None:
        search_point = ST_GeomFromText(f"POINT({longitude} {latitude})", 4326)
        query = query.where(ST_DWithin(PspsEvent.geom, search_point, radius_km * 1000)) # radius in meters

    result = await db.execute(query)
    return list(result.scalars().all())

