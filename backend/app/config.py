"""Backend configuration"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class BackendSettings(BaseSettings):
    """Backend-specific configuration settings"""

    # API Configuration
    api_title: str = "Literature Review Assistant API"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI backend for multi-agent literature review system"
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        validation_alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Session Configuration
    max_sessions: int = Field(default=1000, validation_alias="MAX_SESSIONS")
    session_ttl_seconds: int = Field(default=3600, validation_alias="SESSION_TTL")  # 1 hour

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    debug: bool = Field(default=False, validation_alias="DEBUG")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins


@lru_cache()
def get_backend_settings() -> BackendSettings:
    """Get cached backend settings instance"""
    return BackendSettings()
