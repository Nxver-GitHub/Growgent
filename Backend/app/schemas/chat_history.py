"""
Pydantic schemas for chat message history.

Request and response schemas for chat history operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    """Base schema for ChatMessage with common fields."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Message content")
    conversation_id: str = Field(..., description="Conversation ID")
    field_id: Optional[str] = Field(None, description="Optional field ID")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""

    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    model_used: Optional[str] = Field(None, description="LLM model used")


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response with all fields including metadata."""

    id: UUID
    tokens_used: Optional[int]
    model_used: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""

    conversation_id: str = Field(..., description="Conversation ID")
    messages: list[ChatMessageResponse] = Field(
        default_factory=list, description="List of messages in conversation"
    )
    total: int = Field(..., description="Total number of messages")
    field_id: Optional[str] = Field(None, description="Field ID if conversation is scoped")


class ChatConversationSummary(BaseModel):
    """Schema for conversation summary."""

    conversation_id: str
    field_id: Optional[str]
    message_count: int
    last_message_at: datetime
    first_message_at: datetime


class ChatConversationListResponse(BaseModel):
    """Schema for list of conversations."""

    conversations: list[ChatConversationSummary]
    total: int
    page: int = 1
    page_size: int = 20

