"""
settings.py
===========
Centralized application configuration using Pydantic Settings.

Loads configuration from environment variables with sensible defaults
for the literature review assistant application.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

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
        env_file=".env",
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


