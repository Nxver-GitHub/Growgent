# backend/app/models/fire_perimeter.py

import uuid
from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from geoalchemy2 import Geometry
from ..database import Base  # Assuming your declarative base is in database.py

class FirePerimeter(Base):
    """
    SQLAlchemy model for storing active fire perimeters.
    """
    __tablename__ = "fire_perimeters"

    # Columns based on the data plan
    id: str = Column(String, primary_key=True, index=True) # From provider ID
    agency: str = Column(String, nullable=True)
    fire_name: str = Column(String, nullable=True, index=True)
    
    # Use timezone-aware datetime
    properties: dict = Column(JSONB, nullable=True)
    geom = Column(
        Geometry(geometry_type='MULTIPOLYGON', srid=4326),
        nullable=False
    )
    
    # Timestamps
    # The 'updated_at' from the source data is preserved in 'properties'
    # These are for our internal record-keeping
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

    def __repr__(self):
        return f"<FirePerimeter(id='{self.id}', name='{self.fire_name}')>"
