"""
semantic_scholar_tool.py
========================
Semantic Scholar search tool for fetching academic papers.

Uses the free Semantic Scholar Graph API (no key required) alongside
arXiv to broaden paper coverage. Semantic Scholar covers peer-reviewed
venues and provides richer citation context not available on arXiv.
"""

from __future__ import annotations

from typing import Callable, Dict, List

import httpx

from app.tools.base import BaseTool
from app.core.logging_config import get_logger
from app.core.exceptions import ToolError

logger = get_logger(__name__)

_SS_API = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS = "title,authors,year,abstract,openAccessPdf"


# ===============================================================
# SEMANTIC SCHOLAR SEARCH TOOL
# ===============================================================


class SemanticScholarTool(BaseTool):
    """
    Tool for searching Semantic Scholar papers.

    Uses the free Semantic Scholar Graph API to retrieve paper metadata.
    Complements arXiv by covering peer-reviewed conference and journal
    papers, and provides open-access PDF links where available.

    Attributes:
        default_max_results: Default number of results to return
    """

    def __init__(
        self,
        default_max_results: int = 5,
    ) -> None:
        """
        Initialize the Semantic Scholar search tool.

        Args:
            default_max_results: Default max results per search
        """
        super().__init__(
            name="semantic_scholar_search",
            description=(
                "Searches Semantic Scholar and returns up to max_results papers "
                "with title, authors, abstract, and PDF URL where available."
            ),
        )
        self.default_max_results = default_max_results

        logger.debug(
            f"SemanticScholarTool initialized with default_max={default_max_results}"
        )

    # ===============================================================
    # SEARCH IMPLEMENTATION
    # ===============================================================

    def semantic_scholar_search(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[Dict]:
        """
        Search Semantic Scholar for papers matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List[Dict]: List of paper metadata dicts with title, authors,
                        published, summary, and pdf_url keys

        Raises:
            ToolError: If the API request fails
        """
        capped = min(max_results, self.default_max_results)
        logger.info(f"Searching Semantic Scholar: query='{query}', max_results={capped}")

        try:
            response = httpx.get(
                _SS_API,
                params={"query": query, "fields": _FIELDS, "limit": capped},
                timeout=15,
            )
            response.raise_for_status()

            papers: List[Dict] = []
            for item in response.json().get("data", []):
                open_access = item.get("openAccessPdf") or {}
                pdf_url = open_access.get("url") or (
                    f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}"
                )

                year = item.get("year")
                published = f"{year}-01-01" if year else "Unknown"

                authors = [a["name"] for a in item.get("authors", [])]

                papers.append(
                    {
                        "title": item.get("title", ""),
                        "authors": authors,
                        "published": published,
                        "summary": item.get("abstract") or "No abstract available.",
                        "pdf_url": pdf_url,
                    }
                )

            logger.info(
                f"Found {len(papers)} papers on Semantic Scholar for: {query}"
            )
            return papers

        except httpx.HTTPStatusError as e:
            logger.error(f"Semantic Scholar API error: {e}")
            raise ToolError(
                f"Semantic Scholar request failed: {e}",
                tool_name=self.name,
                details={"query": query},
            )
        except Exception as e:
            logger.error(f"Semantic Scholar search failed: {e}")
            raise ToolError(
                f"Failed to search Semantic Scholar: {e}",
                tool_name=self.name,
                details={"query": query},
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
        return self.semantic_scholar_search
