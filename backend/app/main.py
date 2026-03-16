"""
FastAPI main application
Wraps AutoGen multi-agent system with REST API and SSE streaming
"""

import logging
import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, health, reviews, stream
from app.config.settings import get_backend_settings
from app.db.database import engine
from app.db.models import Base

# -- Simple in-memory rate limiter --
_RATE_WINDOW = 60  # seconds
_RATE_LIMIT = 5  # max review creations per window per IP
_rate_store: dict[str, list[float]] = defaultdict(list)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_backend_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# -- Rate-limit middleware (only on POST /api/v1/reviews) --
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "POST" and request.url.path.rstrip("/") == "/api/v1/reviews":
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        # Prune old timestamps
        _rate_store[client_ip] = [t for t in _rate_store[client_ip] if now - t < _RATE_WINDOW]
        if len(_rate_store[client_ip]) >= _RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Too many requests. Please wait before creating another review. "
                    f"Limit: {_RATE_LIMIT} reviews per {_RATE_WINDOW}s."
                },
            )
        _rate_store[client_ip].append(now)
    return await call_next(request)


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(reviews.router, prefix="/api/v1", tags=["Reviews"])
app.include_router(stream.router, prefix="/api/v1", tags=["Streaming"])


@app.on_event("startup")
async def startup_event():
    """Application startup event — create DB tables and log config"""
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Debug mode: {settings.debug}")

    # Create database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database connected and tables ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event — dispose DB engine"""
    logger.info("Shutting down Literature Review Assistant API")
    await engine.dispose()
    logger.info("Database engine disposed")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
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
