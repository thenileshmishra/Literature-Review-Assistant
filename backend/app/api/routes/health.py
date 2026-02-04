"""Health check endpoints"""

from fastapi import APIRouter
from backend.app.models.responses import HealthResponse
from backend.app.config import get_backend_settings

router = APIRouter()
settings = get_backend_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness probe endpoint"""
    # TODO: Add checks for dependencies (OpenAI API, etc.)
    return HealthResponse(
        status="ready",
        version=settings.api_version
    )
