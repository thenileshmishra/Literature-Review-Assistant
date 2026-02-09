"""
test_tools.py
=============
Unit tests for tool classes.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.tools.arxiv_tool import ArxivSearchTool


class TestArxivSearchTool:
    """Tests for ArxivSearchTool class."""

    def test_initialization(self):
        """Test tool initializes with correct attributes."""
        tool = ArxivSearchTool(default_max_results=10)

        assert tool.name == "arxiv_search"
        assert tool.default_max_results == 10
        assert "arXiv" in tool.description

    def test_as_function_tool(self):
        """Test FunctionTool creation."""
        tool = ArxivSearchTool()
        func_tool = tool.as_function_tool()

        assert func_tool is not None
        # Should return same instance on subsequent calls
        assert tool.as_function_tool() is func_tool

    @patch("arxiv.Client")
    @patch("arxiv.Search")
    def test_search_returns_papers(self, mock_search, mock_client):
        """Test search returns formatted papers."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.title = "Test Paper"
        mock_result.authors = [MagicMock(name="Author 1")]
        mock_result.authors[0].name = "Author 1"
        mock_result.published = datetime(2024, 1, 15)
        mock_result.summary = "Test summary"
        mock_result.pdf_url = "https://arxiv.org/pdf/test.pdf"

        mock_client_instance = MagicMock()
        mock_client_instance.results.return_value = [mock_result]
        mock_client.return_value = mock_client_instance

        tool = ArxivSearchTool()
        tool._client = mock_client_instance

        results = tool.search("test query", max_results=1)

        assert len(results) == 1
        assert results[0]["title"] == "Test Paper"
        assert "Author 1" in results[0]["authors"]

    def test_search_empty_query(self):
        """Test search handles empty results."""
        tool = ArxivSearchTool()
        tool._client = MagicMock()
        tool._client.results.return_value = []

        results = tool.search("nonexistent topic")

        assert results == []
