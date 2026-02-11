"""
test_teams.py
=============
Unit tests for team classes.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.teams.litrev_team import LitRevTeam


class TestLitRevTeam:
    """Tests for LitRevTeam class."""

    def test_initialization(self):
        """Test team initializes with correct attributes."""
        team = LitRevTeam(
            model="gpt-4o-mini",
            api_key="test-key",
            max_turns=3,
        )

        assert team.name == "litrev_team"
        assert team.model == "gpt-4o-mini"
        assert team.max_turns == 3

    @patch("app.agents.base.OpenAIChatCompletionClient")
    def test_get_participants(self, mock_client):
        """Test participants are created correctly."""
        team = LitRevTeam(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        participants = team._get_participants()

        assert len(participants) == 2
        names = [p.name for p in participants]
        assert "search_agent" in names
        assert "summarizer" in names

    @patch("app.agents.base.OpenAIChatCompletionClient")
    def test_build_creates_team(self, mock_client):
        """Test build creates RoundRobinGroupChat."""
        team = LitRevTeam(
            model="gpt-4o-mini",
            api_key="test-key",
        )

        built = team.build()

        assert built is not None
        # Should return same instance on subsequent calls
        assert team.build() is built
