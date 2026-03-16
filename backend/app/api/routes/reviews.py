"""Review management endpoints"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config.settings import get_settings
from app.db.database import get_db
from app.db.models import UserORM
from app.db.review_repository import ReviewRepository, orm_to_response
from app.models.requests import CreateReviewRequest
from app.models.responses import ReviewResponse

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    request: CreateReviewRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new literature review (auth required)."""
    repo = ReviewRepository(db)
    review = await repo.create_review(
        topic=request.topic,
        papers_limit=settings.papers_per_review,
        model=settings.default_model,
        user_id=str(current_user.id),
    )
    logger.info(f"User {current_user.email} created review {review.id}")
    return orm_to_response(review)


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific review (must belong to current user)."""
    repo = ReviewRepository(db)
    review = await repo.get_review(review_id, user_id=str(current_user.id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return orm_to_response(review)


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(
    review_id: str,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a review (must belong to current user)."""
    repo = ReviewRepository(db)
    deleted = await repo.delete_review(review_id, user_id=str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return None


@router.get("/reviews", response_model=list[ReviewResponse])
async def list_reviews(
    limit: int = 20,
    offset: int = 0,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List reviews belonging to the current user."""
    repo = ReviewRepository(db)
    reviews = await repo.list_reviews(user_id=str(current_user.id), limit=limit, offset=offset)
    return [orm_to_response(r) for r in reviews]
