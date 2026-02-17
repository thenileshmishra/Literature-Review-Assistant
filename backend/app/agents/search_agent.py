"""
search_agent.py
===============
Search agent for crafting queries and fetching papers from multiple sources.

Responsible for interpreting planner sub-queries, calling both arXiv
and Semantic Scholar, deduplicating results, and selecting the most
relevant papers for the summarizer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.agents.base import BaseAgent
from app.tools.arxiv_tool import ArxivSearchTool
from app.tools.semantic_scholar_tool import SemanticScholarTool
from app.core.logging_config import get_logger

if TYPE_CHECKING:
    from autogen_core.tools import FunctionTool

logger = get_logger(__name__)


# ===============================================================
# SEARCH AGENT
# ===============================================================


class SearchAgent(BaseAgent):
    """
    Agent specialized in searching multiple academic sources for papers.

    Uses arXiv for preprints and cutting-edge research, and Semantic
    Scholar for broader peer-reviewed coverage. Deduplicates results
    by title before passing to the summarizer.

    Attributes:
        arxiv_tool: The arXiv search tool instance
        semantic_scholar_tool: The Semantic Scholar search tool instance
    """

    DEFAULT_SYSTEM_MESSAGE = (
        "You are an expert research assistant specialized in finding academic papers.\n\n"
        "You have two search tools: arxiv_search and semantic_scholar_search.\n"
        "When given a topic or a list of sub-queries:\n"
        "1. Use arxiv_search for preprints and recent cutting-edge research\n"
        "2. Use semantic_scholar_search for peer-reviewed papers and broader coverage\n"
        "Combine all results, remove duplicates by title, and pass the top papers "
        "as concise JSON to the summarizer.\n\n"
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
        semantic_scholar_tool: SemanticScholarTool | None = None,
    ) -> None:
        """
        Initialize the search agent.

        Args:
            model: LLM model to use
            api_key: OpenAI API key
            arxiv_tool: Optional pre-configured arXiv tool
            semantic_scholar_tool: Optional pre-configured Semantic Scholar tool
        """
        self.arxiv_tool = arxiv_tool or ArxivSearchTool()
        self.semantic_scholar_tool = semantic_scholar_tool or SemanticScholarTool()

        super().__init__(
            name="search_agent",
            description="Searches arXiv and Semantic Scholar, then returns deduplicated candidate papers.",
            system_message=self.DEFAULT_SYSTEM_MESSAGE,
            model=model,
            api_key=api_key,
            tools=[
                self.arxiv_tool.as_function_tool(),
                self.semantic_scholar_tool.as_function_tool(),
            ],
            reflect_on_tool_use=True,
        )

        logger.debug("SearchAgent initialized with arxiv + semantic_scholar tools")

    # ===============================================================
    # IMPLEMENTATION
    # ===============================================================

    def _get_system_message(self) -> str:
        """
        Get the system message for the search agent.

        Returns:
            str: System prompt for multi-source paper searching
        """
        return self.DEFAULT_SYSTEM_MESSAGE
