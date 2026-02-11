"""
base.py
=======
Abstract base class for all tools in the literature review system.

Provides common interface for tool implementations that can be
used by agents via AutoGen's FunctionTool.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable

from autogen_core.tools import FunctionTool

from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ===============================================================
# BASE TOOL CLASS
# ===============================================================

class BaseTool(ABC):
    """
    Abstract base class for literature review tools.

    Wraps functionality into AutoGen FunctionTool format with
    standardized interface and logging.

    Attributes:
        name: Unique identifier for the tool
        description: Human-readable tool description
    """

    def __init__(
        self,
        name: str,
        description: str,
    ) -> None:
        """
        Initialize the base tool.

        Args:
            name: Tool identifier
            description: Tool description for the LLM
        """
        self.name = name
        self.description = description
        self._function_tool: FunctionTool | None = None

        logger.debug(f"Initialized {self.__class__.__name__}: {name}")

    # ===============================================================
    # ABSTRACT METHODS
    # ===============================================================

    @abstractmethod
    def _get_tool_function(self) -> Callable[..., Any]:
        """
        Get the underlying function for this tool.

        Returns:
            Callable: The function to wrap as a tool
        """
        pass

    # ===============================================================
    # BUILD METHODS
    # ===============================================================

    def as_function_tool(self) -> FunctionTool:
        """
        Convert this tool to an AutoGen FunctionTool.

        Returns:
            FunctionTool: AutoGen-compatible tool wrapper
        """
        if self._function_tool is not None:
            return self._function_tool

        self._function_tool = FunctionTool(
            self._get_tool_function(),
            description=self.description,
        )

        logger.info(f"Built FunctionTool: {self.name}")
        return self._function_tool
