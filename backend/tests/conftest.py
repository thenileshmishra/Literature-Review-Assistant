"""
conftest.py
===========
Pytest configuration and shared fixtures.
"""

from __future__ import annotations

import os
import pytest
from unittest.mock import MagicMock, patch

# Set test environment
os.environ["OPENAI_API_KEY"] = "test-api-key-for-testing"
os.environ["DEBUG"] = "true"


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch("autogen_ext.models.openai.OpenAIChatCompletionClient") as mock:
        yield mock


@pytest.fixture
def mock_arxiv_client():
    """Mock arXiv client for testing."""
    with patch("arxiv.Client") as mock:
        yield mock


@pytest.fixture
def sample_papers():
    """Sample paper data for testing."""
    return [
        {
            "title": "Test Paper 1",
            "authors": ["Author A", "Author B"],
            "published": "2024-01-15",
            "summary": "This is a test summary for paper 1.",
            "pdf_url": "https://arxiv.org/pdf/test1.pdf",
        },
        {
            "title": "Test Paper 2",
            "authors": ["Author C", "Author D", "Author E"],
            "published": "2024-02-20",
            "summary": "This is a test summary for paper 2.",
            "pdf_url": "https://arxiv.org/pdf/test2.pdf",
        },
    ]
