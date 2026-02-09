"""
logging_config.py
=================
Structured logging configuration for the literature review assistant.

Provides consistent logging format across all modules with
support for different log levels and output formats.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


# ===============================================================
# LOGGING SETUP
# ===============================================================

def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom log format (optional)
    """
    if format_string is None:
        format_string = (
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# ===============================================================
# LOGGER FACTORY
# ===============================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


# ===============================================================
# CLI TESTING
# ===============================================================

if __name__ == "__main__":
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
