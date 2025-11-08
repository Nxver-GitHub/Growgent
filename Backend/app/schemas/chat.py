"""
Pydantic schemas for chat functionality.

Request and response schemas for natural language chat with AI agents.
"""

from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Message content")


class ChatRequest(BaseModel):
    """Request schema for sending a chat message."""

    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for maintaining context"
    )
    field_id: Optional[UUID] = Field(
        None, description="Optional field ID to scope the conversation"
    )
    include_context: bool = Field(
        True, description="Whether to include field/recommendation context"
    )


class ChatResponse(BaseModel):
    """Response schema for chat messages."""

    message: str = Field(..., description="Assistant response message")
    conversation_id: str = Field(..., description="Conversation ID for context")
    sources: Optional[List[str]] = Field(
        None, description="Data sources referenced in the response"
    )
    suggested_actions: Optional[List[dict]] = Field(
        None, description="Suggested actions or follow-up questions"
    )

