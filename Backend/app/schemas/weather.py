# backend/app/schemas/weather.py

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from uuid import UUID
from ..models.weather import WeatherSource # Reuse the enum from the model

# --- Schemas for parsing the Open-Meteo API Response ---

class OpenMeteoHourlyData(BaseModel):
    """
    Parses the 'hourly' object from the Open-Meteo API response.
    Each field is an array of values corresponding to the 'time' array.
    """
    time: List[datetime]
    temperature_2m: List[float]
    relative_humidity_2m: List[int]
    precipitation: List[float] = Field(..., alias="precipitation")
    wind_speed_10m: List[float]
    et0_fao_evapotranspiration: List[float]

class OpenMeteoResponse(BaseModel):
    """
    The top-level schema for the Open-Meteo API response.
    """
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    hourly: OpenMeteoHourlyData

# --- Schemas for our internal application use ---

class HourlyWeatherBase(BaseModel):
    """
    Base schema containing the core fields for a weather record.
    """
    field_id: UUID
    timestamp: datetime
    temperature_2m: float
    relative_humidity_2m: float
    wind_speed_10m: float
    precipitation_mm: float
    et0_mm: float
    source: WeatherSource

class HourlyWeatherCreate(HourlyWeatherBase):
    """

    Schema used for creating a new hourly weather record in the database.
    """
    pass

class HourlyWeather(HourlyWeatherBase):
    """
    Schema for reading an hourly weather record from the database.
    Includes database-generated fields like 'id' and timestamps.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic v2 alias for orm_mode
