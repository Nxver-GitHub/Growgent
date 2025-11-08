# backend/app/services/weather_service.py

import logging
import httpx
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

from ..models.weather import HourlyWeather, WeatherSource
from ..schemas.weather import OpenMeteoResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the variables we want from the API
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "et0_fao_evapotranspiration",
]

async def sync_weather_for_field(
    db: AsyncSession, field_id: UUID, lat: float, lon: float
):
    """
    Fetches hourly weather forecast data from Open-Meteo for a specific
    field's location and upserts it into the database.
    """
    logger.info(f"Starting weather sync for field {field_id} at ({lat}, {lon})")
    
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": "UTC",
    }

    try:
        # 1. Fetch data from Open-Meteo API
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params, timeout=30.0)
            response.raise_for_status()
            
            # 2. Validate the response with Pydantic
            validated_data = OpenMeteoResponse.model_validate(response.json())
        
        hourly_data = validated_data.hourly
        records_to_upsert = []
        
        # 3. Transform columnar data into a list of row-based records
        for i, timestamp in enumerate(hourly_data.time):
            # To prevent db errors, skip records older than now
            if timestamp.replace(tzinfo=None) < datetime.utcnow():
                continue

            record = {
                "field_id": field_id,
                "timestamp": timestamp,
                "temperature_2m": hourly_data.temperature_2m[i],
                "relative_humidity_2m": hourly_data.relative_humidity_2m[i],
                "wind_speed_10m": hourly_data.wind_speed_10m[i],
                "precipitation_mm": hourly_data.precipitation[i],
                "et0_mm": hourly_data.et0_fao_evapotranspiration[i],
                "source": WeatherSource.OPEN_METEO,
            }
            records_to_upsert.append(record)

        if not records_to_upsert:
            logger.warning(f"No future weather data to sync for field {field_id}.")
            return
            
        # 4. Perform an efficient "upsert" operation
        stmt = insert(HourlyWeather).values(records_to_upsert)
        
        # On conflict on the unique constraint, update the weather values
        on_conflict_stmt = stmt.on_conflict_do_update(
            index_elements=["field_id", "timestamp", "source"],
            set_={
                "temperature_2m": stmt.excluded.temperature_2m,
                "relative_humidity_2m": stmt.excluded.relative_humidity_2m,
                "wind_speed_10m": stmt.excluded.wind_speed_10m,
                "precipitation_mm": stmt.excluded.precipitation_mm,
                "et0_mm": stmt.excluded.et0_mm,
                "updated_at": func.now(),
            }
        )
        
        await db.execute(on_conflict_stmt)
        await db.commit()
        
        logger.info(
            f"Successfully synchronized {len(records_to_upsert)} hourly "
            f"weather records for field {field_id}."
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching weather for field {field_id}: {e}")
    except Exception as e:
        logger.error(f"Error during weather sync for field {field_id}: {e}")
        await db.rollback()
