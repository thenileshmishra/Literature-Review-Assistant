"""
search_agent.py
===============
Search agent for crafting queries and fetching papers from arXiv.

Responsible for interpreting user topics, crafting effective
search queries, and selecting the most relevant papers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.agents.base import BaseAgent
from app.tools.arxiv_tool import ArxivSearchTool
from app.core.logging_config import get_logger

if TYPE_CHECKING:
    from autogen_core.tools import FunctionTool

logger = get_logger(__name__)


# ===============================================================
# SEARCH AGENT
# ===============================================================

class SearchAgent(BaseAgent):
    """
    Agent specialized in searching arXiv for relevant papers.

    Interprets user research topics, crafts optimized search
    queries, and filters results to the most relevant papers.

    Attributes:
        arxiv_tool: The arXiv search tool instance
    """

    DEFAULT_SYSTEM_MESSAGE = (
        "You are an expert research assistant specialized in finding academic papers.\n\n"
        "Given a user topic, craft the best arXiv query and call the tool. "
        "Fetch exactly the requested number of papers and pass them as concise JSON to the summarizer.\n\n"
        "When selecting papers:\n"
        "- Prioritize recent, high-impact papers\n"
        "- Ensure diversity in approaches and methodologies\n"
        "- Focus on papers directly relevant to the topic"
    )

    def __init__(
        self,
        model: str,
        api_key: str,
        arxiv_tool: ArxivSearchTool | None = None,
    ) -> None:
        """
        Initialize the search agent.

        Args:
            model: LLM model to use
            api_key: OpenAI API key
            arxiv_tool: Optional pre-configured arXiv tool
        """
        self.arxiv_tool = arxiv_tool or ArxivSearchTool()

        super().__init__(
            name="search_agent",
            description="Crafts arXiv queries and retrieves candidate papers.",
            system_message=self.DEFAULT_SYSTEM_MESSAGE,
            model=model,
            api_key=api_key,
            tools=[self.arxiv_tool.as_function_tool()],
            reflect_on_tool_use=True,
        )

        logger.debug("SearchAgent initialized")

    # ===============================================================
    # IMPLEMENTATION
    # ===============================================================

    def _get_system_message(self) -> str:
        """
        Get the system message for the search agent.

        Returns:
            str: System prompt for paper searching
        """
        return self.DEFAULT_SYSTEM_MESSAGE


