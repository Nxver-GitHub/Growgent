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
from app.schemas.zone import (
    ZoneBase,
    ZoneCreate,
    ZoneUpdate,
    ZoneResponse,
    ZoneListResponse,
)
from app.schemas.explanation import (
    AgentExplanation,
    DecisionFactor,
    DataSource,
    AlternativeScenario,
    ConfidenceBreakdown,
    ExplanationRequest,
)
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.schemas.chat_history import (
    ChatMessageResponse,
    ChatHistoryResponse,
    ChatConversationSummary,
    ChatConversationListResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfileResponse,
)
from app.schemas.farm import (
    FarmBase,
    FarmCreate,
    FarmUpdate,
    FarmResponse,
)
from app.schemas.user_preferences import (
    UserPreferencesBase,
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse,
)
from app.schemas.fire_perimeter import ( # Added
    FirePerimeterBase, # Added
    FirePerimeterCreate, # Added
    FirePerimeter, # Added
) # Added
from app.schemas.psps_event import ( # Added
    PspsEventBase, # Added
    PspsEventCreate, # Added
    PspsEventResponse, # Added
    PspsEventListResponse, # Added
) # Added

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
    # Zone schemas
    "ZoneBase",
    "ZoneCreate",
    "ZoneUpdate",
    "ZoneResponse",
    "ZoneListResponse",
    # Explanation schemas
    "AgentExplanation",
    "DecisionFactor",
    "DataSource",
    "AlternativeScenario",
    "ConfidenceBreakdown",
    "ExplanationRequest",
    # Chat schemas
    "ChatRequest",
    "ChatResponse",
    "ChatMessage",
    # Chat history schemas
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ChatConversationSummary",
    "ChatConversationListResponse",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfileResponse",
    # Farm schemas
    "FarmBase",
    "FarmCreate",
    "FarmUpdate",
    "FarmResponse",
    # User preferences schemas
    "UserPreferencesBase",
    "UserPreferencesCreate",
    "UserPreferencesUpdate",
    "UserPreferencesResponse",
    # Fire Perimeter schemas # Added
    "FirePerimeterBase", # Added
    "FirePerimeterCreate", # Added
    "FirePerimeter", # Added
    # PSPS Event schemas # Added
    "PspsEventBase", # Added
    "PspsEventCreate", # Added
    "PspsEventResponse", # Added
    "PspsEventListResponse", # Added
]