"""
litrev_team.py
==============
Literature review team using SelectorGroupChat for dynamic agent routing.

Uses AutoGen's SelectorGroupChat so the LLM dynamically picks which agent
speaks next, enabling iterative search-summarize-critique loops.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import SelectorGroupChat

from app.agents.critic_agent import CriticAgent
from app.agents.search_agent import SearchAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.core.exceptions import TeamError
from app.core.logging_config import get_logger
from app.teams.base import BaseTeam

logger = get_logger(__name__)


class LitRevTeam(BaseTeam):
    """
    Three-agent team using SelectorGroupChat for dynamic routing.

    Instead of fixed round-robin, an LLM selector picks the next agent
    based on context — allowing multiple search rounds before summarization,
    and routing back to search if the critic says coverage is lacking.
    """

    SELECTOR_PROMPT = (
        "You are the orchestrator of a research team. Given the conversation so far, "
        "pick the next agent to speak.\n\n"
        "Rules:\n"
        "- If no search has been done yet, pick search_agent.\n"
        "- If search results are available but no review has been written, pick summarizer.\n"
        "- If a review draft exists but hasn't been critiqued, pick critic.\n"
        "- If the critic says coverage is lacking or more sources are needed, pick search_agent.\n"
        "- If the critic gave revision feedback (not about missing sources), pick summarizer.\n"
        "- If the critic said APPROVED, stop.\n"
        "- Never pick the same agent twice in a row unless it's search_agent gathering more sources."
    )

    def __init__(
        self,
        model: str,
        api_key: str,
        tavily_api_key: str = "",
        max_turns: int = 12,
    ) -> None:
        super().__init__(
            name="litrev_team",
            max_turns=max_turns,
        )

        self.model = model
        self.api_key = api_key

        self._search_agent = SearchAgent(
            model=model, api_key=api_key, tavily_api_key=tavily_api_key,
        )
        self._summarizer_agent = SummarizerAgent(model=model, api_key=api_key)
        self._critic_agent = CriticAgent(model=model, api_key=api_key)
        self._team: SelectorGroupChat | None = None

        logger.debug(f"LitRevTeam initialized with model={model}")

    def _get_participants(self) -> list[AssistantAgent]:
        return [
            self._search_agent.build(),
            self._summarizer_agent.build(),
            self._critic_agent.build(),
        ]

    def build(self) -> SelectorGroupChat:
        if self._team is not None:
            return self._team

        participants = self._get_participants()

        termination = TextMentionTermination("APPROVED") | MaxMessageTermination(self.max_turns)

        self._team = SelectorGroupChat(
            participants=participants,
            termination_condition=termination,
            model_client=self._search_agent._build_llm_client(),
            selector_prompt=self.SELECTOR_PROMPT,
        )

        logger.info(f"Built LitRevTeam (SelectorGroupChat) with {len(participants)} agents")
        return self._team

    async def run_stream(
        self,
        task: str,
    ) -> AsyncGenerator[str, None]:
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
            ) from e
