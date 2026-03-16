import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("ReviewORM", back_populates="user", cascade="all, delete-orphan")


class ReviewORM(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending")
    topic = Column(String(500), nullable=False)
    papers_limit = Column(Integer, default=5)
    model = Column(String(50), default="gpt-4o-mini")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("UserORM", back_populates="reviews")
    messages = relationship("MessageORM", back_populates="review", cascade="all, delete-orphan")
    papers = relationship("PaperORM", back_populates="review", cascade="all, delete-orphan")


class MessageORM(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"))
    source = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="system")
    timestamp = Column(DateTime, default=datetime.utcnow)

    review = relationship("ReviewORM", back_populates="messages")


class PaperORM(Base):
    __tablename__ = "papers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"))
    title = Column(String(500), nullable=False)
    authors = Column(ARRAY(String), default=[])
    published = Column(String(20))
    summary = Column(Text)
    pdf_url = Column(String(500))

    review = relationship("ReviewORM", back_populates="papers")
