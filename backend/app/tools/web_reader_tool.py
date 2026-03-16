"""
web_reader_tool.py
==================
Tool for reading and extracting text content from web pages.
"""

from __future__ import annotations

from collections.abc import Callable

import httpx
from bs4 import BeautifulSoup

from app.core.exceptions import ToolError
from app.core.logging_config import get_logger
from app.tools.base import BaseTool

logger = get_logger(__name__)


class WebReaderTool(BaseTool):
    """Tool for reading web page content."""

    def __init__(self, max_chars: int = 4000) -> None:
        super().__init__(
            name="read_webpage",
            description=(
                "Fetches a URL and extracts its main text content. "
                "Use this to read full articles, blog posts, or documentation pages."
            ),
        )
        self.max_chars = max_chars

    def read(self, url: str) -> str:
        """Fetch and extract text from a URL."""
        logger.info(f"Reading webpage: {url}")

        try:
            resp = httpx.get(url, timeout=15, follow_redirects=True, headers={
                "User-Agent": "Mozilla/5.0 (compatible; LitRevBot/1.0)"
            })
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)

            # Truncate to max_chars
            if len(text) > self.max_chars:
                text = text[: self.max_chars] + "\n...[truncated]"

            logger.info(f"Extracted {len(text)} chars from {url}")
            return text

        except Exception as e:
            logger.error(f"Failed to read {url}: {e}")
            raise ToolError(
                f"Failed to read webpage: {e}",
                tool_name=self.name,
                details={"url": url},
            ) from e

    def _get_tool_function(self) -> Callable[..., str]:
        return self.read
