from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import MessageORM, PaperORM, ReviewORM
from app.models.responses import (
    MessageResponse,
    PaperResponse,
    ReviewResponse,
    ReviewStatus,
)


def orm_to_response(review: ReviewORM) -> ReviewResponse:
    """Convert a ReviewORM object to the Pydantic ReviewResponse."""
    return ReviewResponse(
        id=str(review.id),
        status=ReviewStatus(review.status),
        request={
            "topic": review.topic,
            "papers_limit": review.papers_limit,
            "model": review.model,
        },
        messages=[
            MessageResponse(
                source=m.source,
                content=m.content,
                timestamp=m.timestamp,
                message_type=m.message_type,
            )
            for m in (review.messages or [])
        ],
        papers=[
            PaperResponse(
                title=p.title,
                authors=p.authors or [],
                published=p.published or "",
                summary=p.summary or "",
                pdf_url=p.pdf_url or "",
            )
            for p in (review.papers or [])
        ],
        created_at=review.created_at,
        completed_at=review.completed_at,
    )


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(self, topic: str, papers_limit: int, model: str, user_id: str) -> ReviewORM:
        review = ReviewORM(
            topic=topic,
            papers_limit=papers_limit,
            model=model,
            user_id=UUID(str(user_id)),
        )
        self.db.add(review)
        await self.db.commit()
        # Re-fetch with relationships eagerly loaded so orm_to_response can access them
        return await self.get_review(str(review.id))

    async def get_review(self, review_id: str, user_id: str | None = None) -> ReviewORM | None:
        """Fetch review by ID. If user_id is given, also enforce ownership."""
        try:
            uid = UUID(str(review_id))
        except ValueError:
            return None
        stmt = (
            select(ReviewORM)
            .options(selectinload(ReviewORM.messages), selectinload(ReviewORM.papers))
            .where(ReviewORM.id == uid)
        )
        if user_id:
            stmt = stmt.where(ReviewORM.user_id == UUID(str(user_id)))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, review_id: str, status: str) -> None:
        review = await self.get_review(review_id)
        if review:
            review.status = status
            if status in ("completed", "failed"):
                review.completed_at = datetime.utcnow()
            await self.db.commit()

    async def add_message(self, review_id: str, source: str, content: str, message_type: str = "system") -> None:
        msg = MessageORM(
            review_id=UUID(str(review_id)),
            source=source,
            content=content,
            message_type=message_type,
        )
        self.db.add(msg)
        await self.db.commit()

    async def add_paper(self, review_id: str, title: str, authors: list, published: str, summary: str, pdf_url: str) -> None:
        paper = PaperORM(
            review_id=UUID(str(review_id)),
            title=title,
            authors=authors,
            published=published,
            summary=summary,
            pdf_url=pdf_url,
        )
        self.db.add(paper)
        await self.db.commit()

    async def delete_review(self, review_id: str, user_id: str) -> bool:
        review = await self.get_review(review_id, user_id=user_id)
        if review:
            await self.db.delete(review)
            await self.db.commit()
            return True
        return False

    async def list_reviews(self, user_id: str, limit: int = 20, offset: int = 0) -> list[ReviewORM]:
        """List reviews for a specific user only."""
        stmt = (
            select(ReviewORM)
            .where(ReviewORM.user_id == UUID(str(user_id)))
            .order_by(ReviewORM.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
