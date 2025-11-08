"""
Base agent class with common functionality.

All agents inherit from this base class to get common methods
and structure for agent orchestration.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AgentState(BaseModel):
    """
    Base agent state for LangGraph.

    All agent states should inherit from this or include these fields.
    """

    field_id: UUID
    step: str = "initialize"
    error: str | None = None
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """
    Base agent class.

    Provides common functionality for all agents including
    logging, error handling, and state management.
    """

    def __init__(self, agent_name: str) -> None:
        """
        Initialize base agent.

        Args:
            agent_name: Name of the agent for logging
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """
        Process agent logic.

        Args:
            state: Current agent state

        Returns:
            Updated agent state
        """
        pass

    def log_info(self, message: str, **kwargs: Any) -> None:
        """
        Log info message with agent context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.info(f"[{self.agent_name}] {message}", extra=kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """
        Log warning message with agent context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.warning(f"[{self.agent_name}] {message}", extra=kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """
        Log error message with agent context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.error(f"[{self.agent_name}] {message}", extra=kwargs)

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """
        Log debug message with agent context.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.debug(f"[{self.agent_name}] {message}", extra=kwargs)

