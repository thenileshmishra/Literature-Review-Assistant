"""Health check endpoints"""

from fastapi import APIRouter

from app.config.settings import get_backend_settings
from app.models.responses import HealthResponse

router = APIRouter()
settings = get_backend_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version=settings.api_version)
