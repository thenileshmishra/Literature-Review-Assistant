"""API request models"""

from pydantic import BaseModel, Field, field_validator


class CreateReviewRequest(BaseModel):
    """Request model for creating a new literature review"""

    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Research topic to review",
        examples=["graph neural networks", "renewable energy storage"],
    )

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate and clean topic"""
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Topic must be at least 3 characters long")
        return v

    class Config:
        json_schema_extra = {"example": {"topic": "graph neural networks"}}
