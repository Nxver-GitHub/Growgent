"""
Service layer for chat message operations.

Handles business logic for storing and retrieving chat history.
"""

import logging
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """Service for managing chat history."""

    @staticmethod
    async def save_message(
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        field_id: Optional[str] = None,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None,
    ) -> ChatMessage:
        """
        Save a chat message to the database.

        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            field_id: Optional field ID
            tokens_used: Optional token count
            model_used: Optional model name

        Returns:
            Created ChatMessage instance
        """
        logger.debug(
            f"Saving chat message: conversation_id={conversation_id}, role={role}"
        )

        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            field_id=field_id,
            tokens_used=tokens_used,
            model_used=model_used,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        logger.info(f"Chat message saved: id={message.id}")
        return message

    @staticmethod
    async def get_conversation_history(
        db: AsyncSession,
        conversation_id: str,
        limit: Optional[int] = None,
    ) -> List[ChatMessage]:
        """
        Get conversation history.

        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Optional limit on number of messages

        Returns:
            List of ChatMessage instances ordered by created_at
        """
        logger.debug(f"Fetching conversation history: conversation_id={conversation_id}")

        query = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
        )

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        messages = list(result.scalars().all())

        logger.debug(f"Found {len(messages)} messages in conversation")
        return messages

    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        field_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[dict], int]:
        """
        List conversations with optional filtering.

        Args:
            db: Database session
            field_id: Optional field ID filter
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (conversation summaries list, total count)
        """
        logger.debug(
            f"Listing conversations: field_id={field_id}, page={page}, page_size={page_size}"
        )

        # Get unique conversation IDs with filters
        query = select(ChatMessage.conversation_id).distinct()

        if field_id:
            query = query.where(ChatMessage.field_id == field_id)

        # Get total count
        count_query = select(func.count(func.distinct(ChatMessage.conversation_id)))
        if field_id:
            count_query = count_query.where(ChatMessage.field_id == field_id)
        count_result = await db.execute(count_query)
        total = count_result.scalar_one() or 0

        # Apply pagination
        query = query.order_by(desc(ChatMessage.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        conversation_ids = [row[0] for row in result.fetchall()]

        # Get summary for each conversation
        conversations = []
        for conv_id in conversation_ids:
            # Get first and last message timestamps
            first_query = (
                select(ChatMessage.created_at)
                .where(ChatMessage.conversation_id == conv_id)
                .order_by(ChatMessage.created_at)
                .limit(1)
            )
            last_query = (
                select(ChatMessage.created_at)
                .where(ChatMessage.conversation_id == conv_id)
                .order_by(desc(ChatMessage.created_at))
                .limit(1)
            )

            first_result = await db.execute(first_query)
            last_result = await db.execute(last_query)

            first_at = first_result.scalar_one()
            last_at = last_result.scalar_one()

            # Get message count
            count_query = select(func.count()).where(
                ChatMessage.conversation_id == conv_id
            )
            count_result = await db.execute(count_query)
            message_count = count_result.scalar_one() or 0

            # Get field_id (from any message in conversation)
            field_query = (
                select(ChatMessage.field_id)
                .where(ChatMessage.conversation_id == conv_id)
                .limit(1)
            )
            field_result = await db.execute(field_query)
            conv_field_id = field_result.scalar_one()

            conversations.append(
                {
                    "conversation_id": conv_id,
                    "field_id": conv_field_id,
                    "message_count": message_count,
                    "last_message_at": last_at,
                    "first_message_at": first_at,
                }
            )

        logger.debug(f"Found {len(conversations)} conversations (total: {total})")
        return conversations, total

    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: str,
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        logger.debug(f"Deleting conversation: conversation_id={conversation_id}")

        query = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
        result = await db.execute(query)
        messages = list(result.scalars().all())

        if not messages:
            return False

        for message in messages:
            await db.delete(message)

        await db.commit()

        logger.info(f"Conversation deleted: conversation_id={conversation_id}, {len(messages)} messages")
        return True

