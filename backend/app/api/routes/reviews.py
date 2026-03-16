"""Review management endpoints"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.db.database import get_db
from app.db.review_repository import ReviewRepository, orm_to_response
from app.models.requests import CreateReviewRequest
from app.models.responses import ReviewResponse
from app.services import ReviewService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    request: CreateReviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new literature review

    Creates a review session and starts the AutoGen orchestrator in the background.
    Use the returned ID to connect to the streaming endpoint.
    """
    repo = ReviewRepository(db)

    papers_limit = settings.papers_per_review
    model = settings.default_model

    review = await repo.create_review(
        topic=request.topic,
        papers_limit=papers_limit,
        model=model,
    )

    logger.info(f"Created review session {review.id}")

    return orm_to_response(review)


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str, db: AsyncSession = Depends(get_db)):
    """Get a review by ID"""
    repo = ReviewRepository(db)
    review = await repo.get_review(review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return orm_to_response(review)


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(review_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a review"""
    repo = ReviewRepository(db)
    deleted = await repo.delete_review(review_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")

    return None


@router.get("/reviews", response_model=list[ReviewResponse])
async def list_reviews(
    limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    """List recent reviews"""
    repo = ReviewRepository(db)
    reviews = await repo.list_reviews(limit=limit, offset=offset)
    return [orm_to_response(r) for r in reviews]
