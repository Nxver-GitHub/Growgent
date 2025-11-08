"""
Pydantic schemas module.

This module contains all request/response validation schemas.
"""

from app.schemas.field import (
    FieldBase,
    FieldCreate,
    FieldUpdate,
    FieldResponse,
    FieldListResponse,
)
from app.schemas.sensor_reading import (
    SensorReadingBase,
    SensorReadingCreate,
    SensorReadingResponse,
    SensorReadingListResponse,
)
from app.schemas.recommendation import (
    RecommendationBase,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationListResponse,
    RecommendationRequest,
)
from app.schemas.alert import (
    AlertBase,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
)
from app.schemas.metrics import (
    WaterMetricsResponse,
    WaterMetricsSummaryResponse,
    FireRiskMetricsResponse,
)

__all__ = [
    # Field schemas
    "FieldBase",
    "FieldCreate",
    "FieldUpdate",
    "FieldResponse",
    "FieldListResponse",
    # Sensor reading schemas
    "SensorReadingBase",
    "SensorReadingCreate",
    "SensorReadingResponse",
    "SensorReadingListResponse",
    # Recommendation schemas
    "RecommendationBase",
    "RecommendationCreate",
    "RecommendationUpdate",
    "RecommendationResponse",
    "RecommendationListResponse",
    "RecommendationRequest",
    # Alert schemas
    "AlertBase",
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertListResponse",
    # Metrics schemas
    "WaterMetricsResponse",
    "WaterMetricsSummaryResponse",
    "FireRiskMetricsResponse",
]