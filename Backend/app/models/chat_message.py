"""
Chat message model for storing chat history.

Stores conversation messages between users and AI agents for context
and history tracking.
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.field import Field


class ChatMessage(BaseModel):
    """
    Chat message model for storing conversation history.

    Stores individual messages in conversations between users and AI agents.
    """

    __tablename__ = "chat_messages"

    # Conversation tracking
    conversation_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Conversation ID for grouping messages"
    )

    # Message details
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Message role: 'user' or 'assistant'",
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Message content"
    )

    # Optional field context
    field_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Optional field ID this conversation is about",
    )

    # Metadata
    tokens_used: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of tokens used (for LLM responses)"
    )
    model_used: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="LLM model used (e.g., 'claude-3-5-sonnet-20241022')",
    )

    # Relationships
    # Note: Using string reference to avoid circular imports
    # field: Mapped[Optional["Field"]] = relationship("Field", back_populates="chat_messages")

    def __repr__(self) -> str:
        """String representation of the chat message."""
        return (
            f"<ChatMessage(id={self.id}, conversation_id={self.conversation_id}, "
            f"role={self.role}, created_at={self.created_at})>"
        )

