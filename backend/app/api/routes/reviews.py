"""Review management endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging
import asyncio

from backend.app.models.requests import CreateReviewRequest
from backend.app.models.responses import ReviewResponse, ReviewStatus
from backend.app.services import get_session_manager, ReviewService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    request: CreateReviewRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new literature review

    Creates a review session and starts the AutoGen orchestrator in the background.
    Use the returned ID to connect to the streaming endpoint.
    """
    session_manager = get_session_manager()

    # Create session
    session = session_manager.create_session(
        topic=request.topic,
        num_papers=request.num_papers,
        model=request.model
    )

    logger.info(f"Created review session {session.id}")

    # Start review in background
    async def run_review_background():
        """Run review processing in background"""
        try:
            review_service = ReviewService(session_manager)
            # Consume the generator without yielding (background task)
            async for _ in review_service.start_review(
                session_id=session.id,
                topic=request.topic,
                num_papers=request.num_papers,
                model=request.model
            ):
                pass  # Messages are stored in session manager
        except Exception as e:
            logger.error(f"Error in background review {session.id}: {e}", exc_info=True)

    # Schedule background task
    background_tasks.add_task(run_review_background)

    return session


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str):
    """Get a review by ID"""
    session_manager = get_session_manager()
    session = session_manager.get_session(review_id)

    if not session:
        raise HTTPException(status_code=404, detail="Review not found")

    return session


@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(review_id: str):
    """Delete a review"""
    session_manager = get_session_manager()
    deleted = session_manager.delete_session(review_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")

    return None


@router.get("/reviews", response_model=List[ReviewResponse])
async def list_reviews(limit: int = 20, offset: int = 0):
    """List recent reviews"""
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions(limit=limit, offset=offset)
    return sessions
