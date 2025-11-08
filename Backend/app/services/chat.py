"""
Chat service for natural language interaction with AI agents.

Uses Anthropic Claude to answer questions about fields, recommendations,
alerts, and other platform data with context-aware responses.
"""

import logging
import json
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from anthropic import Anthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.field import Field
from app.models.recommendation import Recommendation
from app.models.alert import Alert
from app.services.field import FieldService
from app.services.recommendation import RecommendationService
from app.services.alert import AlertService
from app.services.chat_history import ChatHistoryService

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with AI agents."""

    def __init__(self) -> None:
        """Initialize chat service with Anthropic client."""
        if settings.anthropic_api_key:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.llm_enabled = True
        else:
            self.client = None
            self.llm_enabled = False
            logger.warning(
                "Anthropic API key not set. Chat will use rule-based responses."
            )

    async def process_message(
        self,
        db: AsyncSession,
        message: str,
        conversation_id: Optional[str] = None,
        field_id: Optional[UUID] = None,
        include_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate a response.

        Args:
            db: Database session
            message: User message
            conversation_id: Optional conversation ID for context
            field_id: Optional field ID to scope the conversation
            include_context: Whether to include field/recommendation context

        Returns:
            Dict with response message, conversation_id, and metadata
        """
        logger.info(f"Processing chat message: {message[:100]}...")

        # Generate or use conversation ID
        if not conversation_id:
            conversation_id = str(uuid4())

        # Load conversation history for context
        conversation_history = await ChatHistoryService.get_conversation_history(
            db=db, conversation_id=conversation_id, limit=10
        )

        # Save user message to database
        await ChatHistoryService.save_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=message,
            field_id=str(field_id) if field_id else None,
        )

        # Retrieve context if requested
        context = ""
        sources: List[str] = []
        if include_context:
            context = await self._build_context(db, field_id)
            if context:
                sources.append("Database")

        # Add conversation history to context
        if conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                history_context += f"{msg.role}: {msg.content}\n"
            context = history_context + "\n" + context if context else history_context

        # Generate response
        tokens_used = None
        model_used = None
        if self.llm_enabled:
            response, tokens_used, model_used = await self._generate_llm_response(
                message=message,
                context=context,
                conversation_id=conversation_id,
                conversation_history=conversation_history,
            )
        else:
            response = await self._generate_rule_based_response(
                db=db,
                message=message,
                context=context,
                field_id=field_id,
            )

        # Save assistant response to database
        await ChatHistoryService.save_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            field_id=str(field_id) if field_id else None,
            tokens_used=tokens_used,
            model_used=model_used,
        )

        # Extract suggested actions
        suggested_actions = self._extract_suggested_actions(response, field_id)

        return {
            "message": response,
            "conversation_id": conversation_id,
            "sources": sources if sources else None,
            "suggested_actions": suggested_actions if suggested_actions else None,
        }

    async def _build_context(
        self, db: AsyncSession, field_id: Optional[UUID]
    ) -> str:
        """
        Build context string from database for the conversation.

        Args:
            db: Database session
            field_id: Optional field ID to scope context

        Returns:
            Context string with relevant information
        """
        context_parts: List[str] = []

        try:
            # Get fields
            if field_id:
                field = await FieldService.get_field(db=db, field_id=field_id)
                if field:
                    context_parts.append(
                        f"Field: {field.name} (ID: {field.id})\n"
                        f"  Crop Type: {field.crop_type}\n"
                        f"  Area: {field.area_hectares} hectares\n"
                        f"  Farm ID: {field.farm_id}"
                    )
            else:
                fields, _ = await FieldService.list_fields(
                    db=db, page=1, page_size=10
                )
                if fields:
                    context_parts.append("Available Fields:")
                    for field in fields[:5]:  # Limit to 5 fields
                        context_parts.append(
                            f"  - {field.name} ({field.crop_type}, "
                            f"{field.area_hectares} ha)"
                        )

            # Get recent recommendations
            recommendations, _ = await RecommendationService.list_recommendations(
                db=db, field_id=field_id, page=1, page_size=5
            )
            if recommendations:
                context_parts.append("\nRecent Recommendations:")
                for rec in recommendations[:3]:  # Limit to 3
                    context_parts.append(
                        f"  - {rec.action.value}: {rec.title}\n"
                        f"    Reason: {rec.reason[:100]}\n"
                        f"    Confidence: {rec.confidence:.0%}"
                    )

            # Get recent alerts
            alerts, _ = await AlertService.list_alerts(
                db=db, field_id=field_id, page=1, page_size=5
            )
            if alerts:
                context_parts.append("\nRecent Alerts:")
                for alert in alerts[:3]:  # Limit to 3
                    context_parts.append(
                        f"  - {alert.severity.value.upper()}: {alert.message[:100]}"
                    )

        except Exception as e:
            logger.error(f"Error building context: {e}")
            return ""

        return "\n".join(context_parts)

    async def _generate_llm_response(
        self,
        message: str,
        context: str,
        conversation_id: str,
        conversation_history: List[Any] = None,
    ) -> tuple[str, Optional[int], Optional[str]]:
        """
        Generate response using Anthropic Claude.

        Args:
            message: User message
            context: Context string with relevant data
            conversation_id: Conversation ID
            conversation_history: Previous messages in conversation

        Returns:
            Tuple of (response message, tokens_used, model_used)
        """
        try:
            system_prompt = """You are a helpful AI assistant for Growgent, an agricultural platform for climate-adaptive irrigation and wildfire management.

Your role is to help farmers understand:
- Field conditions and sensor data
- Irrigation recommendations from AI agents
- Fire risk assessments
- PSPS (Public Safety Power Shutoff) predictions
- Water efficiency metrics
- Alerts and notifications

Be concise, helpful, and focus on actionable insights. If you reference specific data, mention where it comes from.
"""

            # Build messages list from conversation history
            messages = []
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    messages.append({"role": msg.role, "content": msg.content})

            # Add current user message
            user_prompt = message
            if context:
                user_prompt = f"""Context:
{context}

User Question: {message}

Please answer the user's question based on the context provided. If the context doesn't contain enough information, say so and suggest what information might be helpful."""

            messages.append({"role": "user", "content": user_prompt})

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
            )

            # Extract token usage if available
            tokens_used = None
            if hasattr(response, "usage") and hasattr(response.usage, "input_tokens"):
                tokens_used = response.usage.input_tokens + response.usage.output_tokens

            return response.content[0].text, tokens_used, "claude-3-5-sonnet-20241022"

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            fallback = await self._generate_fallback_response(message)
            return fallback, None, None

    async def _generate_rule_based_response(
        self,
        db: AsyncSession,
        message: str,
        context: str,
        field_id: Optional[UUID],
    ) -> str:
        """
        Generate rule-based response when LLM is not available.

        Args:
            db: Database session
            message: User message
            context: Context string
            field_id: Optional field ID

        Returns:
            Rule-based response
        """
        message_lower = message.lower()

        # Check for common queries
        if any(word in message_lower for word in ["irrigat", "water", "moisture"]):
            if field_id:
                recommendations, _ = await RecommendationService.list_recommendations(
                    db=db, field_id=field_id, page=1, page_size=1
                )
                if recommendations:
                    rec = recommendations[0]
                    return (
                        f"Based on current conditions, I recommend: {rec.action.value}. "
                        f"{rec.reason}"
                    )
                return "I don't have a recent irrigation recommendation for this field. Would you like me to generate one?"

        elif any(word in message_lower for word in ["fire", "risk", "wildfire"]):
            return (
                "Fire risk assessment considers weather conditions, fuel moisture, "
                "and regional fire danger ratings. Check the fire risk zones on the map "
                "for detailed information."
            )

        elif any(word in message_lower for word in ["alert", "warning", "critical"]):
            alerts, _ = await AlertService.list_alerts(
                db=db, field_id=field_id, page=1, page_size=3
            )
            if alerts:
                alert_list = "\n".join(
                    [f"- {alert.severity.value.upper()}: {alert.message}" for alert in alerts]
                )
                return f"Recent alerts:\n{alert_list}"
            return "No active alerts at this time."

        elif any(word in message_lower for word in ["field", "fields"]):
            if context:
                return f"Here's information about your fields:\n\n{context}"
            return "I can help you with information about your fields. Which field would you like to know about?"

        elif any(word in message_lower for word in ["help", "what can", "how"]):
            return (
                "I can help you with:\n"
                "- Irrigation recommendations and scheduling\n"
                "- Field conditions and sensor data\n"
                "- Fire risk assessments\n"
                "- PSPS (power shutoff) predictions\n"
                "- Water efficiency metrics\n"
                "- Alerts and notifications\n\n"
                'Try asking: "Should I irrigate today?" or "What\'s the fire risk for my fields?"'
            )

        # Default response
        return (
            "I'm here to help with your farm management questions. "
            "You can ask about irrigation, fire risk, field conditions, or alerts. "
            "What would you like to know?"
        )

    async def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response when LLM fails."""
        return (
            "I'm having trouble processing your request right now. "
            "Please try rephrasing your question or contact support if the issue persists."
        )

    def _extract_suggested_actions(
        self, response: str, field_id: Optional[UUID]
    ) -> Optional[List[dict]]:
        """
        Extract suggested actions from response.

        Args:
            response: Response message
            field_id: Optional field ID

        Returns:
            List of suggested actions or None
        """
        actions: List[dict] = []

        response_lower = response.lower()

        # Suggest viewing recommendations if irrigation is mentioned
        if "irrigat" in response_lower or "water" in response_lower:
            actions.append(
                {
                    "label": "View Recommendations",
                    "action": "view_recommendations",
                    "field_id": str(field_id) if field_id else None,
                }
            )

        # Suggest viewing alerts if alerts are mentioned
        if "alert" in response_lower or "warning" in response_lower:
            actions.append(
                {
                    "label": "View Alerts",
                    "action": "view_alerts",
                    "field_id": str(field_id) if field_id else None,
                }
            )

        # Suggest viewing fields if fields are mentioned
        if "field" in response_lower:
            actions.append(
                {
                    "label": "View Fields",
                    "action": "view_fields",
                }
            )

        return actions if actions else None

