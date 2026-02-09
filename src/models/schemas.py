"""
schemas.py
==========
Pydantic models for data validation across the application.

Defines structured data types for papers, search requests,
agent messages, and review sessions.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


# ===============================================================
# PAPER MODEL
# ===============================================================

class Paper(BaseModel):
    """
    Represents a research paper from arXiv.

    Attributes:
        title: Paper title
        authors: List of author names
        published: Publication date string
        summary: Paper abstract
        pdf_url: URL to the PDF
    """

    title: str = Field(description="Paper title")
    authors: List[str] = Field(description="List of author names")
    published: str = Field(description="Publication date (YYYY-MM-DD)")
    summary: str = Field(description="Paper abstract/summary")
    pdf_url: str = Field(description="URL to PDF")

    @property
    def author_display(self) -> str:
        """Get formatted author string with et al. for >3 authors."""
        if len(self.authors) <= 3:
            return ", ".join(self.authors)
        return f"{', '.join(self.authors[:3])} et al."


# ===============================================================
# REQUEST MODELS
# ===============================================================

class SearchRequest(BaseModel):
    """
    Request model for literature review searches.

    Attributes:
        topic: Research topic to search
        num_papers: Number of papers to return
        model: LLM model to use
    """

    topic: str = Field(
        min_length=3,
        max_length=500,
        description="Research topic to search",
    )
    num_papers: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of papers to return",
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="LLM model to use",
    )


# ===============================================================
# MESSAGE MODELS
# ===============================================================

class AgentMessage(BaseModel):
    """
    Represents a message from an agent.

    Attributes:
        source: Agent name that sent the message
        content: Message content
        timestamp: When the message was created
        message_type: Type of message
    """

    source: str = Field(description="Agent name")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Message timestamp",
    )
    message_type: Literal["search", "summary", "system", "error"] = Field(
        default="system",
        description="Type of message",
    )

    @classmethod
    def from_stream(cls, raw: str) -> "AgentMessage":
        """
        Parse a message from stream format.

        Args:
            raw: Raw message string in "source: content" format

        Returns:
            AgentMessage: Parsed message instance
        """
        parts = raw.split(":", 1)
        source = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else ""

        msg_type: Literal["search", "summary", "system", "error"] = "system"
        if source == "search_agent":
            msg_type = "search"
        elif source == "summarizer":
            msg_type = "summary"

        return cls(
            source=source,
            content=content,
            message_type=msg_type,
        )


# ===============================================================
# SESSION MODELS
# ===============================================================

class ReviewSession(BaseModel):
    """
    Represents a complete review session.

    Attributes:
        id: Unique session identifier
        request: The original search request
        messages: List of agent messages
        papers: List of found papers
        created_at: Session creation time
        completed: Whether the session finished
    """

    id: str = Field(description="Session ID")
    request: SearchRequest = Field(description="Original request")
    messages: List[AgentMessage] = Field(
        default_factory=list,
        description="Agent messages",
    )
    papers: List[Paper] = Field(
        default_factory=list,
        description="Found papers",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )
    completed: bool = Field(
        default=False,
        description="Completion status",
    )

    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the session."""
        self.messages.append(message)

    def mark_completed(self) -> None:
        """Mark the session as completed."""
        self.completed = True


# ===============================================================
# CLI TESTING
# ===============================================================

if __name__ == "__main__":
    paper = Paper(
        title="Test Paper",
        authors=["Author 1", "Author 2", "Author 3", "Author 4"],
        published="2024-01-15",
        summary="This is a test summary.",
        pdf_url="https://arxiv.org/pdf/test.pdf",
    )
    print(f"Paper: {paper.title}")
    print(f"Authors: {paper.author_display}")

    msg = AgentMessage.from_stream("search_agent: Found 5 papers")
    print(f"\nMessage: {msg.source} ({msg.message_type})")
