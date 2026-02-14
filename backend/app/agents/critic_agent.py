"""
critic_agent.py
===============
Critic agent for reviewing and scoring literature review drafts.

Responsible for evaluating the quality of generated reviews
and providing actionable feedback for improvement.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ===============================================================
# CRITIC AGENT
# ===============================================================


class CriticAgent(BaseAgent):
    """
    Agent specialized in critiquing literature reviews.

    Evaluates the review produced by the SummarizerAgent on
    three dimensions and provides specific improvement feedback.
    Outputs APPROVED when the review meets quality standards.

    Attributes:
        None additional beyond BaseAgent
    """

    DEFAULT_SYSTEM_MESSAGE = (
        "You are a rigorous academic peer reviewer evaluating literature reviews.\n\n"
        "When you receive a literature review draft, score it on three dimensions (1-5 each):\n"
        "- **Coverage**: Are the most relevant papers included and well represented?\n"
        "- **Clarity**: Is the writing clear, structured, and easy to follow?\n"
        "- **Relevance**: Do the selected papers directly address the stated topic?\n\n"
        "After scoring, provide 2-3 specific, actionable bullet points for improvement.\n\n"
        "If all scores are 4 or above AND the review is well-written, end your message "
        "with the exact word APPROVED on its own line.\n\n"
        "If any score is below 4, do NOT include APPROVED — give feedback so the "
        "summarizer can revise."
    )

    def __init__(
        self,
        model: str,
        api_key: str,
    ) -> None:
        """
        Initialize the critic agent.

        Args:
            model: LLM model to use
            api_key: OpenAI API key
        """
        super().__init__(
            name="critic",
            description="Scores and critiques the literature review draft.",
            system_message=self.DEFAULT_SYSTEM_MESSAGE,
            model=model,
            api_key=api_key,
            tools=[],
            reflect_on_tool_use=False,
        )

        logger.debug("CriticAgent initialized")

    # ===============================================================
    # IMPLEMENTATION
    # ===============================================================

    def _get_system_message(self) -> str:
        """
        Get the system message for the critic agent.

        Returns:
            str: System prompt for literature review critique
        """
        return self.DEFAULT_SYSTEM_MESSAGE
