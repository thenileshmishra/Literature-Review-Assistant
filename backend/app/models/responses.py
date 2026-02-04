"""API response models"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class ReviewStatus(str, Enum):
    """Review processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageResponse(BaseModel):
    """Agent message response"""
    source: str = Field(..., description="Agent name (search_agent, summarizer)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: Literal["search", "summary", "system", "error"] = Field(default="system")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "search_agent",
                "content": "Found 5 relevant papers on quantum computing",
                "timestamp": "2025-02-10T10:30:00Z",
                "message_type": "search"
            }
        }


class PaperResponse(BaseModel):
    """Paper metadata response"""
    title: str
    authors: List[str]
    published: str = Field(..., description="Publication date (YYYY-MM-DD)")
    summary: str = Field(..., description="Paper abstract")
    pdf_url: str = Field(..., description="URL to PDF")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Quantum Computing: A Gentle Introduction",
                "authors": ["John Doe", "Jane Smith"],
                "published": "2024-01-15",
                "summary": "This paper provides an overview of quantum computing...",
                "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf"
            }
        }


class ReviewResponse(BaseModel):
    """Literature review response"""
    id: str = Field(..., description="Unique review ID")
    status: ReviewStatus
    request: dict = Field(..., description="Original request parameters")
    messages: List[MessageResponse] = Field(default_factory=list)
    papers: List[PaperResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "request": {
                    "topic": "quantum computing",
                    "num_papers": 5,
                    "model": "gpt-4o-mini"
                },
                "messages": [],
                "papers": [],
                "created_at": "2025-02-10T10:00:00Z",
                "completed_at": "2025-02-10T10:05:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-02-10T10:00:00Z"
            }
        }
