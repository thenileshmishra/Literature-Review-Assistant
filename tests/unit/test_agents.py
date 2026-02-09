"""
test_agents.py
==============
Unit tests for agent classes.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from src.agents.search_agent import SearchAgent
from src.agents.summarizer_agent import SummarizerAgent


class TestSearchAgent:
    """Tests for SearchAgent class."""

    def test_initialization(self):
        """Test agent initializes with correct attributes."""
        agent = SearchAgent(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        assert agent.name == "search_agent"
        assert agent.model == "gpt-4o-mini"
        assert len(agent.tools) == 1
        assert agent.reflect_on_tool_use is True

    def test_system_message(self):
        """Test system message is set correctly."""
        agent = SearchAgent(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        system_msg = agent._get_system_message()

        assert "arXiv" in system_msg
        assert "query" in system_msg.lower()

    @patch("src.agents.base.OpenAIChatCompletionClient")
    def test_build_creates_assistant(self, mock_client):
        """Test build creates AssistantAgent."""
        agent = SearchAgent(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        built = agent.build()

        assert built is not None
        assert built.name == "search_agent"


class TestSummarizerAgent:
    """Tests for SummarizerAgent class."""

    def test_initialization(self):
        """Test agent initializes with correct attributes."""
        agent = SummarizerAgent(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        assert agent.name == "summarizer"
        assert agent.model == "gpt-4o-mini"
        assert len(agent.tools) == 0
        assert agent.reflect_on_tool_use is False

    def test_system_message(self):
        """Test system message is set correctly."""
        agent = SummarizerAgent(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        system_msg = agent._get_system_message()

        assert "literature" in system_msg.lower()
        assert "Markdown" in system_msg

    @patch("src.agents.base.OpenAIChatCompletionClient")
    def test_build_creates_assistant(self, mock_client):
        """Test build creates AssistantAgent."""
        agent = SummarizerAgent(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        built = agent.build()

        assert built is not None
        assert built.name == "summarizer"
