"""
search_agent.py
===============
Search agent for crafting queries and fetching from multiple sources.

Searches academic papers (arXiv, Semantic Scholar) and the general web
(Tavily), with the ability to read full web pages for deeper context.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.agents.base import BaseAgent
from app.core.logging_config import get_logger
from app.tools.arxiv_tool import ArxivSearchTool
from app.tools.semantic_scholar_tool import SemanticScholarTool
from app.tools.tavily_tool import TavilySearchTool
from app.tools.web_reader_tool import WebReaderTool

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class SearchAgent(BaseAgent):
    """
    Agent specialized in searching multiple sources for research material.

    Uses arXiv and Semantic Scholar for academic papers, Tavily for
    general web search, and a web reader to extract full page content.
    """

    DEFAULT_SYSTEM_MESSAGE = (
        "You are an expert research assistant specialized in deep research.\n\n"
        "You have four tools:\n"
        "1. arxiv_search — for preprints and cutting-edge academic research\n"
        "2. semantic_scholar_search — for peer-reviewed papers and broader academic coverage\n"
        "3. web_search — for blogs, documentation, news articles, and general web sources\n"
        "4. read_webpage — to read the full content of a specific URL\n\n"
        "When given a topic or sub-queries:\n"
        "1. Search academic sources (arxiv + semantic scholar) for foundational papers\n"
        "2. Search the web for recent articles, blog posts, and documentation\n"
        "3. Use read_webpage on the most promising URLs to get deeper content\n"
        "4. Combine all results, remove duplicates, and return the top sources as JSON\n\n"
        "Each source should include: title, url/pdf_url, authors (if available), "
        "date (if available), and a brief summary of key findings.\n"
        "Prioritize recent, high-impact sources with diverse perspectives."
    )

    def __init__(
        self,
        model: str,
        api_key: str,
        tavily_api_key: str = "",
        arxiv_tool: ArxivSearchTool | None = None,
        semantic_scholar_tool: SemanticScholarTool | None = None,
    ) -> None:
        self.arxiv_tool = arxiv_tool or ArxivSearchTool()
        self.semantic_scholar_tool = semantic_scholar_tool or SemanticScholarTool()
        self.web_reader_tool = WebReaderTool()

        tools = [
            self.arxiv_tool.as_function_tool(),
            self.semantic_scholar_tool.as_function_tool(),
            self.web_reader_tool.as_function_tool(),
        ]

        # Only add Tavily if API key is provided
        if tavily_api_key:
            self.tavily_tool = TavilySearchTool(api_key=tavily_api_key)
            tools.append(self.tavily_tool.as_function_tool())

        super().__init__(
            name="search_agent",
            description="Searches academic and web sources, reads pages, and returns deduplicated results.",
            system_message=self.DEFAULT_SYSTEM_MESSAGE,
            model=model,
            api_key=api_key,
            tools=tools,
            reflect_on_tool_use=True,
        )

        logger.debug("SearchAgent initialized with academic + web tools")

    def _get_system_message(self) -> str:
        return self.DEFAULT_SYSTEM_MESSAGE
