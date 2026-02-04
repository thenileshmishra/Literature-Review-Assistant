"""Session management for review tracking"""

from typing import Dict, Optional
from datetime import datetime
import uuid
import logging
from backend.app.models.responses import ReviewResponse, ReviewStatus, MessageResponse, PaperResponse

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages in-memory sessions for literature reviews"""

    def __init__(self, max_sessions: int = 1000):
        self._sessions: Dict[str, ReviewResponse] = {}
        self._max_sessions = max_sessions
        logger.info(f"SessionManager initialized with max_sessions={max_sessions}")

    def create_session(
        self,
        topic: str,
        num_papers: int,
        model: str
    ) -> ReviewResponse:
        """Create a new review session"""
        # Generate unique ID
        session_id = str(uuid.uuid4())

        # Create review response
        review = ReviewResponse(
            id=session_id,
            status=ReviewStatus.PENDING,
            request={
                "topic": topic,
                "num_papers": num_papers,
                "model": model
            },
            messages=[],
            papers=[],
            created_at=datetime.utcnow(),
            completed_at=None
        )

        # Store session
        self._sessions[session_id] = review

        # Clean up old sessions if limit exceeded
        if len(self._sessions) > self._max_sessions:
            self._cleanup_oldest_sessions()

        logger.info(f"Created session {session_id} for topic: {topic}")
        return review

    def get_session(self, session_id: str) -> Optional[ReviewResponse]:
        """Get a review session by ID"""
        return self._sessions.get(session_id)

    def update_status(self, session_id: str, status: ReviewStatus) -> None:
        """Update session status"""
        if session_id in self._sessions:
            self._sessions[session_id].status = status
            if status == ReviewStatus.COMPLETED or status == ReviewStatus.FAILED:
                self._sessions[session_id].completed_at = datetime.utcnow()
            logger.debug(f"Updated session {session_id} status to {status}")

    def add_message(
        self,
        session_id: str,
        source: str,
        content: str,
        message_type: str = "system"
    ) -> None:
        """Add a message to a session"""
        if session_id in self._sessions:
            message = MessageResponse(
                source=source,
                content=content,
                timestamp=datetime.utcnow(),
                message_type=message_type
            )
            self._sessions[session_id].messages.append(message)
            logger.debug(f"Added message to session {session_id} from {source}")

    def add_paper(
        self,
        session_id: str,
        title: str,
        authors: list,
        published: str,
        summary: str,
        pdf_url: str
    ) -> None:
        """Add a paper to a session"""
        if session_id in self._sessions:
            paper = PaperResponse(
                title=title,
                authors=authors,
                published=published,
                summary=summary,
                pdf_url=pdf_url
            )
            self._sessions[session_id].papers.append(paper)
            logger.debug(f"Added paper to session {session_id}: {title}")

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True
        return False

    def list_sessions(self, limit: int = 20, offset: int = 0) -> list:
        """List recent sessions"""
        sessions = list(self._sessions.values())
        # Sort by created_at descending
        sessions.sort(key=lambda x: x.created_at, reverse=True)
        return sessions[offset:offset + limit]

    def _cleanup_oldest_sessions(self) -> None:
        """Remove oldest sessions when limit is exceeded"""
        if len(self._sessions) <= self._max_sessions:
            return

        # Sort by created_at
        sessions_by_age = sorted(
            self._sessions.items(),
            key=lambda x: x[1].created_at
        )

        # Remove oldest 10%
        num_to_remove = max(1, len(sessions_by_age) // 10)
        for session_id, _ in sessions_by_age[:num_to_remove]:
            del self._sessions[session_id]

        logger.info(f"Cleaned up {num_to_remove} old sessions")


# Singleton instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create SessionManager singleton"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
