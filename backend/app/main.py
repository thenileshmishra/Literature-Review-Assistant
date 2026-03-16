"""
FastAPI main application
Wraps AutoGen multi-agent system with REST API and SSE streaming
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, health, reviews, stream
from app.config.settings import get_backend_settings
from app.db.database import engine
from app.db.models import Base


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_backend_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
)

# CORSMiddleware is a pure ASGI middleware — safe to use with asyncpg
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(reviews.router, prefix="/api/v1", tags=["Reviews"])
app.include_router(stream.router, prefix="/api/v1", tags=["Streaming"])


@app.on_event("startup")
async def startup_event():
    """Create DB tables and log config on startup."""
    from sqlalchemy import text

    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    async with engine.begin() as conn:
        # Create any tables that don't exist yet (no-op for existing tables)
        await conn.run_sync(Base.metadata.create_all)
        # Ensure user_id column exists on reviews table —
        # handles databases created before JWT auth was added
        try:
            await conn.execute(
                text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS user_id UUID")
            )
        except Exception:
            pass  # column already exists with correct type
    logger.info("Database connected and tables ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Dispose DB engine on shutdown."""
    logger.info("Shutting down Literature Review Assistant API")
    await engine.dispose()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"error": "Internal server error", "details": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
