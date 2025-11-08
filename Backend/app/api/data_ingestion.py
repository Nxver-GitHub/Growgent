# backend/app/api/routes/data_ingestion.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel, Field

from ...database import get_db
from ...services.fire_perimeter_service import sync_fire_perimeters
from ...services.weather_service import sync_weather_for_field

router = APIRouter()

class WeatherSyncRequest(BaseModel):
    field_id: UUID
    latitude: float = Field(..., gt=-90, lt=90)
    longitude: float = Field(..., gt=-180, lt=180)


@router.post(
    "/sync-fire-perimeters",
    summary="Synchronize Active Fire Perimeters",
    status_code=202, # Accepted
)
async def trigger_sync_fire_perimeters(db: AsyncSession = Depends(get_db)):
    """
    Triggers a background task to fetch the latest fire perimeter data from
    the configured source and update the database.
    """
    await sync_fire_perimeters(db)
    return {"message": "Fire perimeter synchronization process started."}


@router.post(
    "/sync-weather",
    summary="Synchronize Weather Forecast for a Field",
    status_code=202, # Accepted
)
async def trigger_sync_weather(
    request: WeatherSyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers a background task to fetch the latest weather forecast data
    for a specific field's location and update the database.
    """
    await sync_weather_for_field(
        db=db,
        field_id=request.field_id,
        lat=request.latitude,
        lon=request.longitude
    )
    return {"message": "Weather forecast synchronization process started."}
