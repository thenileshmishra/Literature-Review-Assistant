from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import get_backend_settings

settings = get_backend_settings()

engine = create_async_engine(settings.database_url, echo=False, pool_size=10, max_overflow=20)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a DB session."""
    async with async_session_factory() as session:
        yield session
