"""
base.py
=======
Abstract base class for agent teams in the literature review system.

Provides common interface for team configurations that coordinate
multiple agents working together.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, TYPE_CHECKING

from src.core.logging_config import get_logger

if TYPE_CHECKING:
    from autogen_agentchat.agents import AssistantAgent

logger = get_logger(__name__)


# ===============================================================
# BASE TEAM CLASS
# ===============================================================

class BaseTeam(ABC):
    """
    Abstract base class for agent teams.

    Provides common interface for different team configurations
    (RoundRobin, Selector, etc.) with standardized build and
    execution methods.

    Attributes:
        name: Unique identifier for the team
        max_turns: Maximum conversation turns
    """

    def __init__(
        self,
        name: str,
        max_turns: int = 2,
    ) -> None:
        """
        Initialize the base team.

        Args:
            name: Team identifier
            max_turns: Maximum turns for team execution
        """
        self.name = name
        self.max_turns = max_turns

        logger.debug(f"Initialized {self.__class__.__name__}: {name}")

    # ===============================================================
    # ABSTRACT METHODS
    # ===============================================================

    @abstractmethod
    def _get_participants(self) -> List["AssistantAgent"]:
        """
        Get the list of agent participants for this team.

        Returns:
            List[AssistantAgent]: List of built agents
        """
        pass

    @abstractmethod
    def build(self) -> object:
        """
        Build and return the AutoGen team instance.

        Returns:
            The configured team object
        """
        pass

    @abstractmethod
    async def run_stream(
        self,
        task: str,
    ) -> AsyncGenerator[str, None]:
        """
        Execute the team with streaming output.

        Args:
            task: The task prompt for the team

        Yields:
            str: Streaming message content
        """
        pass
