"""
settings.py
===========
Centralized application configuration using Pydantic Settings.

Loads configuration from environment variables with sensible defaults
for the literature review assistant application.
"""

from __future__ import annotations

import os
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
        max_papers: Maximum number of papers allowed per search
        default_papers: Default number of papers to fetch
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
    max_papers: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum papers per search",
    )

    default_papers: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Default number of papers",
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


# ===============================================================
# CLI TESTING
# ===============================================================

if __name__ == "__main__":
    settings = get_settings()
    print(f"App: {settings.app_name} v{settings.app_version}")
    print(f"Model: {settings.default_model}")
    print(f"Debug: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
