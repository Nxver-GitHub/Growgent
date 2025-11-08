# backend/app/models/weather.py

import uuid
import enum
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

# Define an enum for the data source to ensure consistency
class WeatherSource(str, enum.Enum):
    OPEN_METEO = "open_meteo"
    NWS_GRID = "nws_grid"

class HourlyWeather(Base):
    """
    SQLAlchemy model for storing hourly weather forecast data.
    """
    __tablename__ = "weather_hourly"

    # Columns based on the data plan
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    field_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"), # Assumes a 'fields' table
        nullable=False,
        index=True,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Using Numeric for precision with measurements
    temperature_2m = Column(Numeric(precision=5, scale=2), nullable=False)
    relative_humidity_2m = Column(Numeric(precision=5, scale=2), nullable=False)
    wind_speed_10m = Column(Numeric(precision=5, scale=2), nullable=False)
    precipitation_mm = Column(Numeric(precision=5, scale=2), nullable=False)
    et0_mm = Column(Numeric(precision=5, scale=2), nullable=False)
    
    source = Column(SAEnum(WeatherSource), nullable=False)

    # Timestamps for our records
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Prevent duplicate entries for the same field, timestamp, and source
    __table_args__ = (
        UniqueConstraint(
            "field_id",
            "timestamp",
            "source",
            name="uq_field_timestamp_source"
        ),
    )

    def __repr__(self):
        return f"<HourlyWeather(field_id='{self.field_id}', timestamp='{self.timestamp}')>"
