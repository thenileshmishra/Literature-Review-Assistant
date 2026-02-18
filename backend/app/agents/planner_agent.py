"""
planner_agent.py
================
Planner agent for decomposing research topics into focused sub-queries.

Responsible for breaking broad topics into 2-3 targeted sub-queries
that improve search coverage and recall across both arXiv and
Semantic Scholar.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ===============================================================
# PLANNER AGENT
# ===============================================================


class PlannerAgent(BaseAgent):
    """
    Agent specialized in decomposing research topics.

    Takes a broad research topic and produces 2-3 focused sub-queries
    that the search agent uses independently, improving coverage and
    reducing missed papers on adjacent subtopics.

    Attributes:
        None additional beyond BaseAgent
    """

    DEFAULT_SYSTEM_MESSAGE = (
        "You are a research planning expert.\n\n"
        "Given a research topic, decompose it into 2-3 focused sub-queries "
        "that together provide comprehensive coverage of the topic.\n\n"
        "Output ONLY a raw JSON array of strings. No markdown, no explanation:\n"
        '["sub-query 1", "sub-query 2", "sub-query 3"]\n\n'
        "Rules:\n"
        "- Each sub-query targets a distinct aspect or subtopic\n"
        "- Keep each sub-query concise and suitable for academic paper search\n"
        "- Return exactly the JSON array, nothing else"
    )

    def __init__(
        self,
        model: str,
        api_key: str,
    ) -> None:
        """
        Initialize the planner agent.

        Args:
            model: LLM model to use
            api_key: OpenAI API key
        """
        super().__init__(
            name="planner",
            description="Decomposes research topics into focused sub-queries.",
            system_message=self.DEFAULT_SYSTEM_MESSAGE,
            model=model,
            api_key=api_key,
            tools=[],
            reflect_on_tool_use=False,
        )

        logger.debug("PlannerAgent initialized")

    # ===============================================================
    # IMPLEMENTATION
    # ===============================================================

    def _get_system_message(self) -> str:
        """
        Get the system message for the planner agent.

        Returns:
            str: System prompt for topic decomposition
        """
        return self.DEFAULT_SYSTEM_MESSAGE
