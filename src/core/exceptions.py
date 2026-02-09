"""
exceptions.py
=============
Custom exception hierarchy for the literature review assistant.

Provides structured error handling with context preservation
for different failure modes across the application.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


# ===============================================================
# BASE EXCEPTION
# ===============================================================

class LitRevError(Exception):
    """
    Base exception for all literature review assistant errors.

    Attributes:
        message: Human-readable error description
        details: Additional context about the error
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# ===============================================================
# SPECIFIC EXCEPTIONS
# ===============================================================

class ConfigurationError(LitRevError):
    """
    Raised when application configuration is invalid or missing.

    Examples:
        - Missing API key
        - Invalid model name
        - Malformed environment variables
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details)


class AgentError(LitRevError):
    """
    Raised when an agent encounters an execution error.

    Examples:
        - Agent initialization failure
        - LLM API errors
        - Agent communication failures
    """

    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = details or {}
        if agent_name:
            details["agent_name"] = agent_name
        super().__init__(message, details)


class ToolError(LitRevError):
    """
    Raised when a tool execution fails.

    Examples:
        - arXiv API unavailable
        - Invalid search query
        - Rate limiting
    """

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = details or {}
        if tool_name:
            details["tool_name"] = tool_name
        super().__init__(message, details)


class TeamError(LitRevError):
    """
    Raised when team orchestration fails.

    Examples:
        - Team initialization failure
        - Agent coordination errors
        - Message passing failures
    """

    def __init__(
        self,
        message: str,
        team_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = details or {}
        if team_name:
            details["team_name"] = team_name
        super().__init__(message, details)


# ===============================================================
# CLI TESTING
# ===============================================================

if __name__ == "__main__":
    try:
        raise AgentError(
            "Failed to initialize agent",
            agent_name="search_agent",
            details={"model": "gpt-4o-mini"},
        )
    except LitRevError as e:
        print(f"Caught: {e}")
