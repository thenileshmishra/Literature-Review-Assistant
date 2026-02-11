"""SSE streaming endpoints"""

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import logging
import json
from typing import AsyncGenerator

from app.services import get_session_manager, ReviewService
from app.config.settings import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


async def review_event_generator(review_id: str) -> AsyncGenerator:
    """
    Generate SSE events for a review

    Yields events in Server-Sent Events format
    """
    session_manager = get_session_manager()

    # Check if session exists
    session = session_manager.get_session(review_id)
    if not session:
        yield {
            "event": "error",
            "data": json.dumps({"error": "Review not found", "review_id": review_id})
        }
        return

    # Create review service
    review_service = ReviewService(session_manager)

    # Get request parameters from session
    request = session.request
    topic = request.get("topic")
    papers_limit = request.get("papers_limit", settings.papers_per_review)
    model = request.get("model", settings.default_model)

    logger.info(f"Starting SSE stream for review {review_id}")

    try:
        # Stream messages from review service
        async for message_data in review_service.start_review(
            session_id=review_id,
            topic=topic,
            papers_limit=papers_limit,
            model=model
        ):
            # Determine event type
            if message_data.get("type") == "complete":
                yield {
                    "event": "complete",
                    "data": json.dumps(message_data)
                }
                break
            elif message_data.get("type") == "error":
                yield {
                    "event": "error",
                    "data": json.dumps(message_data)
                }
                break
            else:
                # Regular message event
                yield {
                    "event": "message",
                    "data": json.dumps(message_data)
                }

        logger.info(f"Completed SSE stream for review {review_id}")

    except Exception as e:
        logger.error(f"Error in SSE stream for review {review_id}: {e}", exc_info=True)
        yield {
            "event": "error",
            "data": json.dumps({
                "error": str(e),
                "review_id": review_id
            })
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
