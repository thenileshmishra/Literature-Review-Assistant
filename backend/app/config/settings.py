"""
settings.py
===========
Centralized application configuration using Pydantic Settings.

Loads configuration from environment variables with sensible defaults
for the literature review assistant application.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ===============================================================
# SETTINGS CLASS
# ===============================================================

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        openai_api_key: OpenAI API key for LLM access
        default_model: Default model to use for agents
        papers_per_review: Fixed number of papers per review
        log_level: Logging verbosity level
        app_name: Application display name
        app_version: Application version string
        debug: Enable debug mode
    """

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for model access",
    )

    default_model: str = Field(
        default="gpt-4o-mini",
        description="Default LLM model to use",
    )

    # Search Configuration
    papers_per_review: int = Field(
        default=5,
        ge=5,
        le=5,
        validation_alias="PAPERS_PER_REVIEW",
        description="Fixed number of papers per review",
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging verbosity level",
    )

    # Application Metadata
    app_name: str = Field(
        default="Literature Review Assistant",
        description="Application display name",
    )

    app_version: str = Field(
        default="1.0.0",
        description="Application version",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )


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
    session_ttl_seconds: int = Field(default=3600, validation_alias="SESSION_TTL")

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


# ===============================================================
# SETTINGS FACTORY
# ===============================================================

@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings instance.

    Uses LRU cache to ensure settings are only loaded once
    from environment variables during application lifecycle.

    Returns:
        Settings: Configured settings instance
    """
    return Settings()


@lru_cache()
def get_backend_settings() -> BackendSettings:
    """Get cached backend settings instance"""
    return BackendSettings()


