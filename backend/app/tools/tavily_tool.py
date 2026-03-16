"""
tavily_tool.py
==============
Web search tool using Tavily API for general internet search.
"""

from __future__ import annotations

from collections.abc import Callable

from tavily import TavilyClient

from app.core.exceptions import ToolError
from app.core.logging_config import get_logger
from app.tools.base import BaseTool

logger = get_logger(__name__)


class TavilySearchTool(BaseTool):
    """Tool for searching the web using Tavily API."""

    def __init__(self, api_key: str, max_results: int = 5) -> None:
        super().__init__(
            name="web_search",
            description=(
                "Searches the internet and returns relevant results with "
                "title, URL, and content snippet. Use for blogs, docs, news, and general web sources."
            ),
        )
        self.max_results = max_results
        self._client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search the web for the given query."""
        capped = min(max_results, self.max_results)
        logger.info(f"Tavily search: query='{query}', max_results={capped}")

        try:
            response = self._client.search(
                query=query,
                max_results=capped,
                include_answer=False,
            )

            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                })

            logger.info(f"Found {len(results)} web results for: {query}")
            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise ToolError(
                f"Web search failed: {e}",
                tool_name=self.name,
                details={"query": query},
            ) from e

    def _get_tool_function(self) -> Callable[..., list[dict]]:
        return self.search
