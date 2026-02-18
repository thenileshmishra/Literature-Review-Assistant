"""Review service wrapping AutoGen orchestrator"""

import json
import logging
import re
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from app.core.exceptions import LitRevError
from app.models.responses import ReviewStatus
from app.orchestrator.litrev_orchestrator import LitRevOrchestrator
from app.services.session_manager import SessionManager

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for managing literature reviews using AutoGen"""

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def start_review(
        self, session_id: str, topic: str, papers_limit: int, model: str = "gpt-4o-mini"
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Start a literature review and stream messages

        Args:
            session_id: Session ID for tracking
            topic: Research topic
            papers_limit: Number of papers to find
            model: LLM model to use

        Yields:
            Dictionary with message data
        """
        try:
            # Update status to in_progress
            self.session_manager.update_status(session_id, ReviewStatus.IN_PROGRESS)

            logger.info(
                f"Starting review {session_id}: topic='{topic}', papers={papers_limit}, model={model}"
            )

            # Run AutoGen orchestrator
            orchestrator = LitRevOrchestrator(model=model)
            async for message_str in orchestrator.run_review(
                topic=topic, num_papers=papers_limit
            ):
                # Parse message in "source: content" format
                parsed = self._parse_message(message_str)

                if parsed:
                    source = parsed["source"]
                    content = parsed["content"]

                    # Determine message type
                    message_type = self._determine_message_type(source, content)

                    # Store in session
                    self.session_manager.add_message(
                        session_id=session_id,
                        source=source,
                        content=content,
                        message_type=message_type,
                    )

                    # Extract papers if search agent message
                    if source == "search_agent":
                        self._extract_papers(session_id, content)

                    # Yield message for streaming
                    yield {
                        "source": source,
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat(),
                        "message_type": message_type,
                    }

            # Mark as completed
            self.session_manager.update_status(session_id, ReviewStatus.COMPLETED)
            logger.info(f"Completed review {session_id}")

            # Yield completion event
            yield {
                "type": "complete",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except LitRevError as e:
            logger.error(f"LitRevError in review {session_id}: {e}")
            self.session_manager.update_status(session_id, ReviewStatus.FAILED)
            self.session_manager.add_message(
                session_id=session_id,
                source="system",
                content=f"Error: {str(e)}",
                message_type="error",
            )
            yield {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Unexpected error in review {session_id}: {e}", exc_info=True)
            self.session_manager.update_status(session_id, ReviewStatus.FAILED)
            self.session_manager.add_message(
                session_id=session_id,
                source="system",
                content=f"Unexpected error: {str(e)}",
                message_type="error",
            )
            yield {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _parse_message(self, message_str: str) -> dict[str, str]:
        """Parse message in 'source: content' format"""
        # Match pattern: "source: content"
        match = re.match(r"^([^:]+):\s*(.*)$", message_str.strip())
        if match:
            return {"source": match.group(1).strip(), "content": match.group(2).strip()}
        # Fallback: treat as system message
        return {"source": "system", "content": message_str.strip()}

    def _determine_message_type(self, source: str, content: str) -> str:
        """Determine message type based on source and content"""
        if source == "search_agent":
            return "search"
        elif source == "summarizer":
            return "summary"
        elif source == "critic":
            return "critique"
        elif source == "planner":
            return "planning"
        elif "error" in content.lower():
            return "error"
        return "system"

    def _extract_papers(self, session_id: str, content: str) -> None:
        """Extract paper information from search agent message"""
        payload = self._parse_papers_payload(content)
        if not payload:
            return

        for paper in payload:
            if not isinstance(paper, dict):
                continue

            title = paper.get("title")
            authors = paper.get("authors")
            published = paper.get("published")
            summary = paper.get("summary")
            pdf_url = paper.get("pdf_url")

            if not all([title, authors, published, summary, pdf_url]):
                continue

            self.session_manager.add_paper(
                session_id=session_id,
                title=title,
                authors=authors,
                published=published,
                summary=summary,
                pdf_url=pdf_url,
            )

    def _parse_papers_payload(self, content: str) -> list | None:
        """Parse a JSON payload of papers from an agent message."""
        candidates = []

        fenced_match = re.search(r"```json\s*([\s\S]*?)\s*```", content, re.IGNORECASE)
        if fenced_match:
            candidates.append(fenced_match.group(1))

        candidates.append(content)

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue

            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and isinstance(parsed.get("papers"), list):
                return parsed["papers"]

        return None
