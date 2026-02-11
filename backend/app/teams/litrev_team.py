"""
litrev_team.py
==============
Literature review team coordinating search and summarizer agents.

Uses AutoGen's RoundRobinGroupChat to orchestrate the two-agent
workflow for producing literature reviews.
"""

from __future__ import annotations

from typing import AsyncGenerator, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat

from app.teams.base import BaseTeam
from app.agents.search_agent import SearchAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.core.logging_config import get_logger
from app.core.exceptions import TeamError

logger = get_logger(__name__)


# ===============================================================
# LITERATURE REVIEW TEAM
# ===============================================================

class LitRevTeam(BaseTeam):
    """
    Two-agent team for literature review generation.

    Coordinates a search agent and summarizer agent using
    RoundRobinGroupChat to produce literature reviews from
    arXiv papers.

    Attributes:
        search_agent: Agent for searching papers
        summarizer_agent: Agent for summarizing papers
        model: LLM model identifier
        api_key: API key for model access
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        max_turns: int = 2,
    ) -> None:
        """
        Initialize the literature review team.

        Args:
            model: LLM model to use for agents
            api_key: OpenAI API key
            max_turns: Maximum conversation turns
        """
        super().__init__(
            name="litrev_team",
            max_turns=max_turns,
        )

        self.model = model
        self.api_key = api_key

        self._search_agent = SearchAgent(model=model, api_key=api_key)
        self._summarizer_agent = SummarizerAgent(model=model, api_key=api_key)
        self._team: RoundRobinGroupChat | None = None

        logger.debug(f"LitRevTeam initialized with model={model}")

    # ===============================================================
    # IMPLEMENTATION
    # ===============================================================

    def _get_participants(self) -> List[AssistantAgent]:
        """
        Get the list of agent participants.

        Returns:
            List[AssistantAgent]: Built search and summarizer agents
        """
        return [
            self._search_agent.build(),
            self._summarizer_agent.build(),
        ]

    def build(self) -> RoundRobinGroupChat:
        """
        Build and return the RoundRobinGroupChat team.

        Returns:
            RoundRobinGroupChat: Configured team instance
        """
        if self._team is not None:
            return self._team

        participants = self._get_participants()

        self._team = RoundRobinGroupChat(
            participants=participants,
            max_turns=self.max_turns,
        )

        logger.info(f"Built LitRevTeam with {len(participants)} agents")
        return self._team

    async def run_stream(
        self,
        task: str,
    ) -> AsyncGenerator[str, None]:
        """
        Execute the team with streaming output.

        Args:
            task: The task prompt for the team

        Yields:
            str: Formatted message strings as "source: content"

        Raises:
            TeamError: If team execution fails
        """
        team = self.build()

        logger.info(f"Starting team execution: {task[:50]}...")

        try:
            async for msg in team.run_stream(task=task):
                if isinstance(msg, TextMessage):
                    yield f"{msg.source}: {msg.content}"

        except Exception as e:
            logger.error(f"Team execution failed: {e}")
            raise TeamError(
                f"Failed to execute literature review: {e}",
                team_name=self.name,
                details={"task": task},
            )


