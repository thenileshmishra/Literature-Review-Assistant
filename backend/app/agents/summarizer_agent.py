"""
summarizer_agent.py
===================
Summarizer agent for producing literature review content.

Responsible for analyzing paper metadata and producing
well-structured markdown literature reviews.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ===============================================================
# SUMMARIZER AGENT
# ===============================================================

class SummarizerAgent(BaseAgent):
    """
    Agent specialized in producing literature reviews.

    Takes paper metadata from the search agent and produces
    well-structured markdown summaries highlighting key
    contributions and themes.

    Attributes:
        None additional beyond BaseAgent
    """

    DEFAULT_SYSTEM_MESSAGE = (
        "You are an expert researcher specializing in literature reviews.\n\n"
        "When you receive a JSON list of papers:\n"
        "1. Write a short literature-review style introduction in Markdown.\n"
        "2. Include one bullet per paper with:\n"
        "   - Title (as Markdown link to PDF)\n"
        "   - Authors (first 3, then et al. if more)\n"
        "   - Publication date\n"
        "   - Specific problem tackled\n"
        "   - Key contributions and findings\n\n"
        "3. End with a brief synthesis paragraph connecting themes.\n\n"
        "Format your output as clean, readable Markdown suitable for "
        "academic or professional contexts."
    )

    def __init__(
        self,
        model: str,
        api_key: str,
    ) -> None:
        """
        Initialize the summarizer agent.

        Args:
            model: LLM model to use
            api_key: OpenAI API key
        """
        super().__init__(
            name="summarizer",
            description="Produces a short Markdown review from provided papers.",
            system_message=self.DEFAULT_SYSTEM_MESSAGE,
            model=model,
            api_key=api_key,
            tools=[],
            reflect_on_tool_use=False,
        )

        logger.debug("SummarizerAgent initialized")

    # ===============================================================
    # IMPLEMENTATION
    # ===============================================================

    def _get_system_message(self) -> str:
        """
        Get the system message for the summarizer agent.

        Returns:
            str: System prompt for literature review generation
        """
        return self.DEFAULT_SYSTEM_MESSAGE


