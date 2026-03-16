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

    async def create_review(self, topic, papers_limit, model) -> ReviewORM:
        review = ReviewORM(topic=topic, papers_limit=papers_limit, model=model)
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_review(self, review_id) -> ReviewORM | None:
        try:
            uid = UUID(str(review_id))
        except ValueError:
            return None
        stmt = (
            select(ReviewORM)
            .options(selectinload(ReviewORM.messages), selectinload(ReviewORM.papers))
            .where(ReviewORM.id == uid)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, review_id, status):
        review = await self.get_review(review_id)
        if review:
            review.status = status
            if status in ("completed", "failed"):
                review.completed_at = datetime.utcnow()
            await self.db.commit()

    async def add_message(self, review_id, source, content, message_type="system"):
        msg = MessageORM(
            review_id=UUID(str(review_id)), source=source, content=content, message_type=message_type
        )
        self.db.add(msg)
        await self.db.commit()

    async def add_paper(self, review_id, title, authors, published, summary, pdf_url):
        paper = PaperORM(
            review_id=UUID(str(review_id)), title=title, authors=authors,
            published=published, summary=summary, pdf_url=pdf_url
        )
        self.db.add(paper)
        await self.db.commit()

    async def delete_review(self, review_id) -> bool:
        review = await self.get_review(review_id)
        if review:
            await self.db.delete(review)
            await self.db.commit()
            return True
        return False

    async def list_reviews(self, limit=20, offset=0):
        stmt = (
            select(ReviewORM)
            .order_by(ReviewORM.created_at.desc())
            .offset(offset).limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()