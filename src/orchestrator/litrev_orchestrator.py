"""
litrev_orchestrator.py
======================
Main orchestrator for literature review generation.

Provides the high-level API for running literature reviews,
coordinating the team, and managing the review workflow.
"""

from __future__ import annotations

from typing import AsyncGenerator

from src.teams.litrev_team import LitRevTeam
from src.config.settings import Settings, get_settings
from src.core.logging_config import get_logger, setup_logging
from src.core.exceptions import ConfigurationError

logger = get_logger(__name__)


# ===============================================================
# LITERATURE REVIEW ORCHESTRATOR
# ===============================================================

class LitRevOrchestrator:
    """
    Main orchestrator for literature review generation.

    Provides the primary interface for running literature reviews
    with configurable parameters and streaming output.

    Attributes:
        settings: Application settings
        model: LLM model to use
    """

    def __init__(
        self,
        model: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            model: Optional LLM model override
            settings: Optional settings override

        Raises:
            ConfigurationError: If API key is missing
        """
        self.settings = settings or get_settings()
        self.model = model or self.settings.default_model

        setup_logging(level=self.settings.log_level)

        if not self.settings.openai_api_key:
            raise ConfigurationError(
                "OpenAI API key is required",
                config_key="OPENAI_API_KEY",
            )

        logger.info(f"LitRevOrchestrator initialized with model={self.model}")

    # ===============================================================
    # MAIN API
    # ===============================================================

    async def run_review(
        self,
        topic: str,
        num_papers: int = 5,
    ) -> AsyncGenerator[str, None]:
        """
        Run a literature review on the given topic.

        Creates a new team instance and executes the review workflow,
        streaming messages as they are generated.

        Args:
            topic: Research topic to review
            num_papers: Number of papers to include

        Yields:
            str: Streaming message content as "source: content"

        Example:
            >>> orchestrator = LitRevOrchestrator()
            >>> async for msg in orchestrator.run_review("neural networks", 5):
            ...     print(msg)
        """
        logger.info(f"Starting review: topic='{topic}', papers={num_papers}")

        team = LitRevTeam(
            model=self.model,
            api_key=self.settings.openai_api_key,
        )

        task_prompt = (
            f"Conduct a literature review on '{topic}' "
            f"and return {num_papers} papers."
        )

        async for msg in team.run_stream(task=task_prompt):
            yield msg

        logger.info(f"Review completed for topic: {topic}")


# ===============================================================
# CONVENIENCE FUNCTION
# ===============================================================

async def run_litrev(
    topic: str,
    num_papers: int = 5,
    model: str = "gpt-4o-mini",
) -> AsyncGenerator[str, None]:
    """
    Convenience function to run a literature review.

    Provides backwards-compatible API matching the original
    implementation while using the new class-based architecture.

    Args:
        topic: Research topic to review
        num_papers: Number of papers to include
        model: LLM model to use

    Yields:
        str: Streaming message content

    Example:
        >>> async for msg in run_litrev("graph neural networks", 5):
        ...     print(msg)
    """
    orchestrator = LitRevOrchestrator(model=model)

    async for msg in orchestrator.run_review(topic, num_papers):
        yield msg


# ===============================================================
# CLI TESTING
# ===============================================================

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    async def _demo() -> None:
        async for line in run_litrev(
            "graph neural networks for chemistry",
            num_papers=3,
        ):
            print(line)
            print("-" * 50)

    asyncio.run(_demo())
