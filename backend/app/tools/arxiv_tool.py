"""
arxiv_tool.py
=============
arXiv search tool for fetching academic papers.

Provides search functionality against the arXiv API with
result formatting suitable for literature review tasks.
"""

from __future__ import annotations

from typing import Callable, Dict, List

import arxiv

from app.tools.base import BaseTool
from app.core.logging_config import get_logger
from app.core.exceptions import ToolError

logger = get_logger(__name__)


# ===============================================================
# ARXIV SEARCH TOOL
# ===============================================================

class ArxivSearchTool(BaseTool):
    """
    Tool for searching arXiv papers.

    Wraps the arxiv Python library to provide paper search
    functionality that can be used by agents.

    Attributes:
        default_max_results: Default number of results to return
    """

    def __init__(
        self,
        default_max_results: int = 5,
    ) -> None:
        """
        Initialize the arXiv search tool.

        Args:
            default_max_results: Default max results per search
        """
        super().__init__(
            name="arxiv_search",
            description=(
                "Searches arXiv and returns up to max_results papers "
                "with metadata including title, authors, abstract, and PDF URL."
            ),
        )
        self.default_max_results = default_max_results
        self._client = arxiv.Client()

        logger.debug(f"ArxivSearchTool initialized with default_max={default_max_results}")

    # ===============================================================
    # SEARCH IMPLEMENTATION
    # ===============================================================

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[Dict]:
        """
        Search arXiv for papers matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List[Dict]: List of paper metadata dictionaries

        Raises:
            ToolError: If the search fails
        """
        capped_results = min(max_results, self.default_max_results)
        logger.info(f"Searching arXiv: query='{query}', max_results={capped_results}")

        try:
            search = arxiv.Search(
                query=query,
                max_results=capped_results,
                sort_by=arxiv.SortCriterion.Relevance,
            )

            papers: List[Dict] = []
            for result in self._client.results(search):
                papers.append(
                    {
                        "title": result.title,
                        "authors": [a.name for a in result.authors],
                        "published": result.published.strftime("%Y-%m-%d"),
                        "summary": result.summary,
                        "pdf_url": result.pdf_url,
                    }
                )

            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers

        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            raise ToolError(
                f"Failed to search arXiv: {e}",
                tool_name=self.name,
                details={"query": query, "max_results": capped_results},
            )

    # ===============================================================
    # TOOL INTERFACE
    # ===============================================================

    def _get_tool_function(self) -> Callable[..., List[Dict]]:
        """
        Get the search function for FunctionTool wrapping.

        Returns:
            Callable: The search method
        """
        return self.search


