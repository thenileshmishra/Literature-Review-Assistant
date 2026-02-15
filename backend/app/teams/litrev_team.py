"""
litrev_team.py
==============
Literature review team coordinating search, summarizer, and critic agents.

Uses AutoGen's RoundRobinGroupChat to orchestrate the three-agent
workflow for producing and refining literature reviews.
"""

from __future__ import annotations

from typing import AsyncGenerator, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat

from app.agents.critic_agent import CriticAgent
from app.agents.search_agent import SearchAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.core.exceptions import TeamError
from app.core.logging_config import get_logger
from app.teams.base import BaseTeam

logger = get_logger(__name__)


# ===============================================================
# LITERATURE REVIEW TEAM
# ===============================================================


class LitRevTeam(BaseTeam):
    """
    Three-agent team for literature review generation with reflection.

    Coordinates a search agent, summarizer agent, and critic agent using
    RoundRobinGroupChat. The critic reviews the draft and provides
    feedback; the summarizer revises once before critic approves.

    Attributes:
        search_agent: Agent for searching papers
        summarizer_agent: Agent for summarizing papers
        critic_agent: Agent for reviewing and scoring the draft
        model: LLM model identifier
        api_key: API key for model access
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        max_turns: int = 6,
    ) -> None:
        """
        Initialize the literature review team.

        Args:
            model: LLM model to use for agents
            api_key: OpenAI API key
            max_turns: Maximum conversation turns (default 6 for one reflection cycle)
        """
        super().__init__(
            name="litrev_team",
            max_turns=max_turns,
        )

        self.model = model
        self.api_key = api_key

        self._search_agent = SearchAgent(model=model, api_key=api_key)
        self._summarizer_agent = SummarizerAgent(model=model, api_key=api_key)
        self._critic_agent = CriticAgent(model=model, api_key=api_key)
        self._team: RoundRobinGroupChat | None = None

        logger.debug(f"LitRevTeam initialized with model={model}")

    # ===============================================================
    # IMPLEMENTATION
    # ===============================================================

    def _get_participants(self) -> List[AssistantAgent]:
        """
        Get the list of agent participants.

        Returns:
            List[AssistantAgent]: Built search, summarizer, and critic agents
        """
        return [
            self._search_agent.build(),
            self._summarizer_agent.build(),
            self._critic_agent.build(),
        ]

    def build(self) -> RoundRobinGroupChat:
        """
        Build and return the RoundRobinGroupChat team.

        Termination: stops when critic says APPROVED or after max_turns.

        Returns:
            RoundRobinGroupChat: Configured team instance
        """
        if self._team is not None:
            return self._team

        participants = self._get_participants()

        termination = TextMentionTermination("APPROVED") | MaxMessageTermination(self.max_turns)

        self._team = RoundRobinGroupChat(
            participants=participants,
            termination_condition=termination,
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
