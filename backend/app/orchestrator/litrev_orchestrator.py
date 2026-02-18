"""
litrev_orchestrator.py
======================
Main orchestrator for literature review generation.

Provides the high-level API for running literature reviews,
coordinating the team, and managing the review workflow.
"""

from __future__ import annotations

from typing import AsyncGenerator

from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat

from app.agents.planner_agent import PlannerAgent
from app.teams.litrev_team import LitRevTeam
from app.config.settings import Settings, get_settings
from app.core.logging_config import get_logger, setup_logging
from app.core.exceptions import ConfigurationError

logger = get_logger(__name__)


# ===============================================================
# LITERATURE REVIEW ORCHESTRATOR
# ===============================================================


class LitRevOrchestrator:
    """
    Main orchestrator for literature review generation.

    Provides the primary interface for running literature reviews
    with configurable parameters and streaming output.

    Workflow:
        1. PlannerAgent decomposes the topic into sub-queries (pre-step).
        2. LitRevTeam (Search → Summarize → Critic) runs with the enriched task.

    Attributes:
        settings: Application settings
        model: LLM model to use
    """

    def __init__(
        self,
        model: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            model: Optional LLM model override
            settings: Optional settings override

        Raises:
            ConfigurationError: If API key is missing
        """
        self.settings = settings or get_settings()
        self.model = model or self.settings.default_model

        setup_logging(level=self.settings.log_level)

        if not self.settings.openai_api_key:
            raise ConfigurationError(
                "OpenAI API key is required",
                config_key="OPENAI_API_KEY",
            )

        logger.info(f"LitRevOrchestrator initialized with model={self.model}")

    # ===============================================================
    # MAIN API
    # ===============================================================

    async def run_review(
        self,
        topic: str,
        num_papers: int = 5,
    ) -> AsyncGenerator[str, None]:
        """
        Run a literature review on the given topic.

        First runs a PlannerAgent to decompose the topic into sub-queries,
        then passes the enriched task to the LitRevTeam (Search → Summarize
        → Critic). Streams all messages as they are generated.

        Args:
            topic: Research topic to review
            num_papers: Deprecated (fixed to settings.papers_per_review)

        Yields:
            str: Streaming message content as "source: content"

        Example:
            >>> orchestrator = LitRevOrchestrator()
            >>> async for msg in orchestrator.run_review("neural networks"):
            ...     print(msg)
        """
        papers_limit = self.settings.papers_per_review
        logger.info(f"Starting review: topic='{topic}', papers={papers_limit}")

        # Step 1: Decompose topic into sub-queries
        sub_queries_json = await self._plan_topic(topic)
        if sub_queries_json:
            yield f"planner: {sub_queries_json}"

        # Step 2: Build enriched task prompt
        if sub_queries_json:
            task_prompt = (
                f"Research topic: '{topic}'\n"
                f"Planned sub-queries: {sub_queries_json}\n"
                f"Search for papers on each sub-query using all available tools, "
                f"combine and deduplicate results, then return the {papers_limit} "
                f"most relevant papers."
            )
        else:
            task_prompt = (
                f"Conduct a literature review on '{topic}' "
                f"and return {papers_limit} papers."
            )

        # Step 3: Run the multi-agent team
        team = LitRevTeam(
            model=self.model,
            api_key=self.settings.openai_api_key,
        )

        async for msg in team.run_stream(task=task_prompt):
            yield msg

        logger.info(f"Review completed for topic: {topic}")

    # ===============================================================
    # INTERNAL HELPERS
    # ===============================================================

    async def _plan_topic(self, topic: str) -> str | None:
        """
        Run the PlannerAgent to decompose the topic into sub-queries.

        Args:
            topic: Research topic to decompose

        Returns:
            str | None: JSON array string of sub-queries, or None on failure
        """
        try:
            planner = PlannerAgent(
                model=self.model,
                api_key=self.settings.openai_api_key,
            )
            planner_team = RoundRobinGroupChat(
                participants=[planner.build()],
                termination_condition=MaxMessageTermination(2),
            )

            result: str | None = None
            async for msg in planner_team.run_stream(
                task=f"Decompose this research topic into sub-queries: {topic}"
            ):
                if isinstance(msg, TextMessage) and msg.source == "planner":
                    result = msg.content

            logger.info(f"Planner produced sub-queries for: {topic}")
            return result

        except Exception as e:
            logger.warning(f"Planner failed, falling back to direct topic: {e}")
            return None


# ===============================================================
# CONVENIENCE FUNCTION
# ===============================================================


async def run_litrev(
    topic: str,
    num_papers: int = 5,
    model: str = "gpt-4o-mini",
) -> AsyncGenerator[str, None]:
    """
    Convenience function to run a literature review.

    Provides backwards-compatible API matching the original
    implementation while using the new class-based architecture.

    Args:
        topic: Research topic to review
        num_papers: Deprecated (fixed to settings.papers_per_review)
        model: LLM model to use

    Yields:
        str: Streaming message content

    Example:
        >>> async for msg in run_litrev("graph neural networks", 5):
        ...     print(msg)
    """
    orchestrator = LitRevOrchestrator(model=model)

    async for msg in orchestrator.run_review(topic, num_papers):
        yield msg
