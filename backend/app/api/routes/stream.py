"""SSE streaming endpoints"""

import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_current_user_from_query
from app.config.settings import get_settings
from app.db.database import async_session_factory
from app.db.models import UserORM
from app.db.review_repository import ReviewRepository
from app.services import ReviewService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


async def review_event_generator(review_id: str, user_id: str) -> AsyncGenerator:
    """
    Generate SSE events for a review.
    Opens its own DB session because SSE generators outlive the
    normal FastAPI request/response Depends lifecycle.
    """
    async with async_session_factory() as db:
        repo = ReviewRepository(db)

        # Enforce ownership — user can only stream their own reviews
        review = await repo.get_review(review_id, user_id=user_id)
        if not review:
            yield {
                "event": "error",
                "data": json.dumps({"error": "Review not found", "review_id": review_id}),
            }
            return

        topic = review.topic
        papers_limit = review.papers_limit or settings.papers_per_review
        model = review.model or settings.default_model

        logger.info(f"SSE stream started: review={review_id} user={user_id}")

        try:
            review_service = ReviewService(db)
            async for message_data in review_service.start_review(
                session_id=str(review.id),
                topic=topic,
                papers_limit=papers_limit,
                model=model,
            ):
                if message_data.get("type") == "complete":
                    yield {"event": "complete", "data": json.dumps(message_data)}
                    break
                elif message_data.get("type") == "error":
                    yield {"event": "error", "data": json.dumps(message_data)}
                    break
                else:
                    yield {"event": "message", "data": json.dumps(message_data)}

            logger.info(f"SSE stream completed: review={review_id}")

        except Exception as e:
            logger.error(f"SSE stream error review={review_id}: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e), "review_id": review_id}),
            }


@router.get("/reviews/{review_id}/stream")
async def stream_review(
    review_id: str,
    current_user: UserORM = Depends(get_current_user_from_query),
):
    """
    Stream review progress via SSE.
    Auth: pass JWT as ?token=<access_token> (EventSource cannot send headers).
    """
    return EventSourceResponse(
        review_event_generator(review_id, user_id=str(current_user.id))
    )
