"""
litrev_orchestrator.py
======================
Main orchestrator for literature review generation.

Coordinates planning, team execution, and progress streaming.
"""

from __future__ import annotations

import json
import re
from collections.abc import AsyncGenerator

from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat

from app.agents.planner_agent import PlannerAgent
from app.config.settings import Settings, get_settings
from app.core.exceptions import ConfigurationError
from app.core.logging_config import get_logger, setup_logging
from app.teams.litrev_team import LitRevTeam

logger = get_logger(__name__)


# ===============================================================
# OUTPUT GUARDRAIL
# ===============================================================


def validate_review_output(raw_message: str) -> str | None:
    """
    Guardrail that validates the summarizer's output.

    Returns an error string if the output is invalid, None if OK.
    """
    # Must have some minimum content
    if len(raw_message.strip()) < 100:
        return "Review is too short — must be at least 100 characters."

    # Must contain at least one markdown link (source citation)
    if not re.search(r"\[.+?\]\(.+?\)", raw_message):
        return "Review must include at least one source citation as a markdown link."

    return None


class LitRevOrchestrator:
    """
    Main orchestrator for literature review generation.

    Workflow:
        1. PlannerAgent decomposes the topic into sub-queries.
        2. LitRevTeam (SelectorGroupChat: Search → Summarize → Critic) runs.
        3. Output guardrails validate the final review.
    """

    def __init__(
        self,
        model: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.model = model or self.settings.default_model

        setup_logging(level=self.settings.log_level)

        if not self.settings.openai_api_key:
            raise ConfigurationError(
                "OpenAI API key is required",
                config_key="OPENAI_API_KEY",
            )

        logger.info(f"LitRevOrchestrator initialized with model={self.model}")

    async def run_review(
        self,
        topic: str,
        num_papers: int = 5,
    ) -> AsyncGenerator[str, None]:
        """
        Run a deep research review on the given topic with progress events.
        """
        papers_limit = self.settings.papers_per_review
        logger.info(f"Starting review: topic='{topic}', papers={papers_limit}")

        # Progress: planning
        yield "progress: Planning research strategy..."

        # Step 1: Plan
        sub_queries_json = await self._plan_topic(topic)
        if sub_queries_json:
            yield f"planner: {sub_queries_json}"
            # Parse for progress display
            try:
                queries = json.loads(sub_queries_json)
                yield f"progress: Researching {len(queries)} sub-topics across academic and web sources..."
            except (json.JSONDecodeError, TypeError):
                yield "progress: Searching academic and web sources..."
        else:
            yield "progress: Searching academic and web sources..."

        # Step 2: Build enriched task prompt
        if sub_queries_json:
            task_prompt = (
                f"Research topic: '{topic}'\n"
                f"Planned sub-queries: {sub_queries_json}\n"
                f"Search for sources on each sub-query using ALL available tools "
                f"(arxiv, semantic scholar, web search, and read key pages), "
                f"combine and deduplicate results, then return the {papers_limit} "
                f"most relevant sources."
            )
        else:
            task_prompt = (
                f"Conduct a deep research review on '{topic}'. "
                f"Use all search tools (academic and web) and read key pages. "
                f"Return {papers_limit} high-quality sources."
            )

        # Step 3: Run the multi-agent team
        team = LitRevTeam(
            model=self.model,
            api_key=self.settings.openai_api_key,
            tavily_api_key=self.settings.tavily_api_key,
        )

        last_summarizer_msg = ""
        async for msg in team.run_stream(task=task_prompt):
            # Track summarizer output for guardrail check
            if msg.startswith("summarizer:"):
                last_summarizer_msg = msg.split(": ", 1)[1] if ": " in msg else ""

            # Emit progress hints based on which agent is speaking
            if msg.startswith("search_agent:"):
                yield "progress: Searching and reading sources..."
            elif msg.startswith("summarizer:"):
                yield "progress: Writing research report..."
            elif msg.startswith("critic:"):
                yield "progress: Reviewing report quality..."

            yield msg

        # Step 4: Output guardrail — validate final review
        if last_summarizer_msg:
            guardrail_error = validate_review_output(last_summarizer_msg)
            if guardrail_error:
                logger.warning(f"Output guardrail failed: {guardrail_error}")
                yield f"guardrail: {guardrail_error}"

        logger.info(f"Review completed for topic: {topic}")

    async def _plan_topic(self, topic: str) -> str | None:
        """Run the PlannerAgent to decompose the topic into sub-queries."""
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
