"""API request models"""

from pydantic import BaseModel, Field, field_validator


class CreateReviewRequest(BaseModel):
    """Request model for creating a new literature review"""

    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Research topic to review",
        examples=["quantum computing", "neural networks in medicine"]
    )
    num_papers: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of papers to include in the review"
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="LLM model to use for agents",
        examples=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
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
        json_schema_extra = {
            "example": {
                "topic": "machine learning in healthcare",
                "num_papers": 5,
                "model": "gpt-4o-mini"
            }
        }
