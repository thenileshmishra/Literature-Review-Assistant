"""SSE streaming endpoints"""

import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.config.settings import get_settings
from app.db.database import async_session_factory
from app.db.review_repository import ReviewRepository
from app.services import ReviewService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


async def review_event_generator(review_id: str) -> AsyncGenerator:
    """
    Generate SSE events for a review

    Yields events in Server-Sent Events format.
    We open our own DB session here because SSE generators outlive
    the normal FastAPI request-response Depends lifecycle.
    """
    async with async_session_factory() as db:
        repo = ReviewRepository(db)

        # Check if session exists
        review = await repo.get_review(review_id)
        if not review:
            yield {
                "event": "error",
                "data": json.dumps({"error": "Review not found", "review_id": review_id}),
            }
            return

        # Get request parameters from the stored review
        topic = review.topic
        papers_limit = review.papers_limit or settings.papers_per_review
        model = review.model or settings.default_model

        logger.info(f"Starting SSE stream for review {review_id}")

        try:
            # Create review service with the same DB session
            review_service = ReviewService(db)

            # Stream messages from review service
            async for message_data in review_service.start_review(
                session_id=str(review.id),
                topic=topic,
                papers_limit=papers_limit,
                model=model,
            ):
                # Determine event type
                if message_data.get("type") == "complete":
                    yield {"event": "complete", "data": json.dumps(message_data)}
                    break
                elif message_data.get("type") == "error":
                    yield {"event": "error", "data": json.dumps(message_data)}
                    break
                else:
                    # Regular message event
                    yield {"event": "message", "data": json.dumps(message_data)}

            logger.info(f"Completed SSE stream for review {review_id}")

        except Exception as e:
            logger.error(f"Error in SSE stream for review {review_id}: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e), "review_id": review_id}),
            }


@router.get("/reviews/{review_id}/stream")
async def stream_review(review_id: str):
    """
    Stream review progress via Server-Sent Events (SSE)

    Connect to this endpoint to receive real-time updates about the review process.

    Events:
    - message: Agent message
    - complete: Review completed
    - error: Error occurred
    """
    return EventSourceResponse(review_event_generator(review_id))
