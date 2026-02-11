"""
base.py
=======
Abstract base class for all agents in the literature review system.

Provides common interface and functionality that all agent
implementations must follow.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from app.core.logging_config import get_logger

if TYPE_CHECKING:
    from autogen_core.tools import FunctionTool

logger = get_logger(__name__)


# ===============================================================
# BASE AGENT CLASS
# ===============================================================

class BaseAgent(ABC):
    """
    Abstract base class for literature review agents.

    Wraps AutoGen's AssistantAgent with standardized configuration
    and lifecycle management.

    Attributes:
        name: Unique identifier for the agent
        description: Human-readable agent description
        system_message: Agent's system prompt
        model: LLM model identifier
        api_key: API key for model access
    """

    def __init__(
        self,
        name: str,
        description: str,
        system_message: str,
        model: str,
        api_key: str,
        tools: Optional[List["FunctionTool"]] = None,
        reflect_on_tool_use: bool = False,
    ) -> None:
        """
        Initialize the base agent.

        Args:
            name: Agent identifier
            description: Agent description
            system_message: System prompt for the agent
            model: LLM model to use
            api_key: OpenAI API key
            tools: List of tools available to the agent
            reflect_on_tool_use: Whether agent reflects after tool use
        """
        self.name = name
        self.description = description
        self.system_message = system_message
        self.model = model
        self.api_key = api_key
        self.tools = tools or []
        self.reflect_on_tool_use = reflect_on_tool_use

        self._agent: Optional[AssistantAgent] = None
        self._llm_client: Optional[OpenAIChatCompletionClient] = None

        logger.debug(f"Initialized {self.__class__.__name__}: {name}")

    # ===============================================================
    # ABSTRACT METHODS
    # ===============================================================

    @abstractmethod
    def _get_system_message(self) -> str:
        """
        Get the system message for this agent.

        Returns:
            str: System prompt for the agent
        """
        pass

    # ===============================================================
    # BUILD METHODS
    # ===============================================================

    def _build_llm_client(self) -> OpenAIChatCompletionClient:
        """
        Build the LLM client for this agent.

        Returns:
            OpenAIChatCompletionClient: Configured LLM client
        """
        return OpenAIChatCompletionClient(
            model=self.model,
            api_key=self.api_key,
        )

    def build(self) -> AssistantAgent:
        """
        Build and return the AutoGen AssistantAgent.

        Creates the underlying AssistantAgent with all configured
        parameters and tools.

        Returns:
            AssistantAgent: Configured AutoGen agent
        """
        if self._agent is not None:
            return self._agent

        self._llm_client = self._build_llm_client()

        agent_kwargs = {
            "name": self.name,
            "description": self.description,
            "system_message": self._get_system_message(),
            "model_client": self._llm_client,
        }

        if self.tools:
            agent_kwargs["tools"] = self.tools
            agent_kwargs["reflect_on_tool_use"] = self.reflect_on_tool_use

        self._agent = AssistantAgent(**agent_kwargs)

        logger.info(f"Built agent: {self.name}")
        return self._agent

    # ===============================================================
    # PROPERTIES
    # ===============================================================

    @property
    def agent(self) -> AssistantAgent:
        """
        Get the built agent instance.

        Returns:
            AssistantAgent: The built agent

        Raises:
            RuntimeError: If agent hasn't been built yet
        """
        if self._agent is None:
            raise RuntimeError(
                f"Agent {self.name} not built. Call build() first."
            )
        return self._agent
