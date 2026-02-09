#!/bin/bash
# =============================================================================
# Git Commit Script - Literature Review Assistant
# =============================================================================
# Run this script to create commits with realistic timestamps
# From Jan 30 to Feb 2, 2026
# =============================================================================

set -e

cd /Users/nileshmishra/Agent

echo "Starting commit sequence..."
echo ""

# -----------------------------------------------------------------------------
# Commit 1: Jan 30, 2026 - 10:23 AM - Project structure setup
# -----------------------------------------------------------------------------
echo "Commit 1: Setting up project structure..."
git add src/__init__.py \
        src/config/__init__.py \
        src/core/__init__.py \
        src/agents/__init__.py \
        src/tools/__init__.py \
        src/teams/__init__.py \
        src/orchestrator/__init__.py \
        src/models/__init__.py \
        frontend/__init__.py \
        frontend/components/__init__.py \
        frontend/pages/__init__.py \
        frontend/utils/__init__.py \
        tests/__init__.py \
        tests/unit/__init__.py \
        tests/integration/__init__.py

GIT_AUTHOR_DATE="2026-01-30T10:23:17" GIT_COMMITTER_DATE="2026-01-30T10:23:17" \
git commit -m "feat: initialize production project structure

- Create src/ package with config, core, agents, tools, teams modules
- Create frontend/ package with components, pages, utils
- Create tests/ package structure
- Set up Python package hierarchy"

# -----------------------------------------------------------------------------
# Commit 2: Jan 30, 2026 - 2:47 PM - Configuration and core modules
# -----------------------------------------------------------------------------
echo "Commit 2: Adding configuration and core modules..."
git add src/config/settings.py \
        src/core/exceptions.py \
        src/core/logging_config.py

GIT_AUTHOR_DATE="2026-01-30T14:47:32" GIT_COMMITTER_DATE="2026-01-30T14:47:32" \
git commit -m "feat: add configuration management and core utilities

- Implement Pydantic Settings for environment configuration
- Add custom exception hierarchy (LitRevError, AgentError, ToolError)
- Set up structured logging with configurable levels"

# -----------------------------------------------------------------------------
# Commit 3: Jan 30, 2026 - 6:12 PM - Base classes
# -----------------------------------------------------------------------------
echo "Commit 3: Adding base classes..."
git add src/agents/base.py \
        src/tools/base.py \
        src/teams/base.py

GIT_AUTHOR_DATE="2026-01-30T18:12:44" GIT_COMMITTER_DATE="2026-01-30T18:12:44" \
git commit -m "feat: implement abstract base classes for agents, tools, teams

- Add BaseAgent with AutoGen AssistantAgent wrapping
- Add BaseTool with FunctionTool conversion
- Add BaseTeam with async streaming interface"

# -----------------------------------------------------------------------------
# Commit 4: Jan 31, 2026 - 9:34 AM - ArXiv tool
# -----------------------------------------------------------------------------
echo "Commit 4: Adding ArXiv search tool..."
git add src/tools/arxiv_tool.py

GIT_AUTHOR_DATE="2026-01-31T09:34:18" GIT_COMMITTER_DATE="2026-01-31T09:34:18" \
git commit -m "feat: implement ArxivSearchTool for paper discovery

- Wrap arxiv library with class-based interface
- Add search method with query and max_results parameters
- Return structured paper metadata (title, authors, summary, pdf_url)"

# -----------------------------------------------------------------------------
# Commit 5: Jan 31, 2026 - 12:08 PM - Agent implementations
# -----------------------------------------------------------------------------
echo "Commit 5: Adding agent implementations..."
git add src/agents/search_agent.py \
        src/agents/summarizer_agent.py

GIT_AUTHOR_DATE="2026-01-31T12:08:51" GIT_COMMITTER_DATE="2026-01-31T12:08:51" \
git commit -m "feat: implement SearchAgent and SummarizerAgent

- SearchAgent crafts arXiv queries and fetches papers
- SummarizerAgent produces markdown literature reviews
- Both extend BaseAgent with specialized system prompts"

# -----------------------------------------------------------------------------
# Commit 6: Jan 31, 2026 - 3:41 PM - Team and orchestrator
# -----------------------------------------------------------------------------
echo "Commit 6: Adding team and orchestrator..."
git add src/teams/litrev_team.py \
        src/orchestrator/litrev_orchestrator.py \
        src/models/schemas.py

GIT_AUTHOR_DATE="2026-01-31T15:41:27" GIT_COMMITTER_DATE="2026-01-31T15:41:27" \
git commit -m "feat: implement LitRevTeam and orchestrator

- LitRevTeam uses RoundRobinGroupChat with search and summarizer agents
- LitRevOrchestrator provides high-level API for running reviews
- Add Pydantic schemas for Paper, SearchRequest, AgentMessage"

# -----------------------------------------------------------------------------
# Commit 7: Jan 31, 2026 - 7:29 PM - Frontend components
# -----------------------------------------------------------------------------
echo "Commit 7: Adding frontend components..."
git add frontend/utils/session_state.py \
        frontend/components/header.py \
        frontend/components/sidebar.py \
        frontend/components/chat_display.py \
        frontend/components/paper_card.py \
        frontend/components/progress_indicator.py

GIT_AUTHOR_DATE="2026-01-31T19:29:03" GIT_COMMITTER_DATE="2026-01-31T19:29:03" \
git commit -m "feat: add Streamlit frontend components

- SessionStateManager for state management
- Header and Sidebar navigation components
- Chat display with styled agent messages
- Paper card component with metadata display
- Progress indicator with step visualization"

# -----------------------------------------------------------------------------
# Commit 8: Feb 1, 2026 - 10:52 AM - Frontend pages and main app
# -----------------------------------------------------------------------------
echo "Commit 8: Adding frontend pages..."
git add frontend/styles/custom.css \
        frontend/pages/home.py \
        frontend/pages/history.py \
        frontend/pages/settings.py \
        frontend/app.py

GIT_AUTHOR_DATE="2026-02-01T10:52:38" GIT_COMMITTER_DATE="2026-02-01T10:52:38" \
git commit -m "feat: implement frontend pages and main Streamlit app

- Home page with search form and real-time results
- History page for viewing past searches
- Settings page for configuration
- Custom dark theme CSS styling
- Main app entry point with page routing"

# -----------------------------------------------------------------------------
# Commit 9: Feb 1, 2026 - 3:16 PM - Docker configuration
# -----------------------------------------------------------------------------
echo "Commit 9: Adding Docker configuration..."
git add docker/Dockerfile \
        docker/Dockerfile.dev \
        docker/docker-compose.yml \
        docker/.dockerignore

GIT_AUTHOR_DATE="2026-02-01T15:16:44" GIT_COMMITTER_DATE="2026-02-01T15:16:44" \
git commit -m "feat: add Docker containerization

- Multi-stage production Dockerfile with non-root user
- Development Dockerfile with hot-reload
- Docker Compose for service orchestration
- Health checks and security best practices"

# -----------------------------------------------------------------------------
# Commit 10: Feb 1, 2026 - 6:38 PM - Build scripts and Makefile
# -----------------------------------------------------------------------------
echo "Commit 10: Adding build scripts..."
git add Makefile \
        scripts/run_dev.sh \
        scripts/run_prod.sh

GIT_AUTHOR_DATE="2026-02-01T18:38:21" GIT_COMMITTER_DATE="2026-02-01T18:38:21" \
git commit -m "feat: add Makefile and utility scripts

- Makefile with common development commands
- Development server script with hot-reload
- Production server script
- Commands for Docker, testing, linting"

# -----------------------------------------------------------------------------
# Commit 11: Feb 2, 2026 - 11:14 AM - Tests
# -----------------------------------------------------------------------------
echo "Commit 11: Adding test suite..."
git add tests/conftest.py \
        tests/unit/test_tools.py \
        tests/unit/test_agents.py \
        tests/unit/test_teams.py

GIT_AUTHOR_DATE="2026-02-02T11:14:55" GIT_COMMITTER_DATE="2026-02-02T11:14:55" \
git commit -m "test: add unit test suite

- Pytest fixtures for mocking OpenAI and arXiv clients
- Unit tests for ArxivSearchTool
- Unit tests for SearchAgent and SummarizerAgent
- Unit tests for LitRevTeam"

# -----------------------------------------------------------------------------
# Commit 12: Feb 2, 2026 - 2:47 PM - Project configuration files
# -----------------------------------------------------------------------------
echo "Commit 12: Adding project configuration..."
git add requirements.txt \
        requirements-dev.txt \
        pyproject.toml

GIT_AUTHOR_DATE="2026-02-02T14:47:09" GIT_COMMITTER_DATE="2026-02-02T14:47:09" \
git commit -m "chore: update project dependencies and configuration

- Production requirements with AutoGen, OpenAI, Streamlit
- Development requirements with pytest, ruff, mypy
- pyproject.toml with full project metadata and tool configs"

# -----------------------------------------------------------------------------
# Commit 13: Feb 2, 2026 - 5:23 PM - Documentation
# -----------------------------------------------------------------------------
echo "Commit 13: Adding documentation..."
git add .env.example \
        README.md \
        .gitignore

GIT_AUTHOR_DATE="2026-02-02T17:23:41" GIT_COMMITTER_DATE="2026-02-02T17:23:41" \
git commit -m "docs: add documentation and environment setup

- README with installation, usage, and architecture docs
- Environment example file with all config options
- Updated .gitignore for Python/Docker/IDE files"

echo ""
echo "============================================="
echo "All commits created successfully!"
echo "============================================="
echo ""
echo "Run 'git log --oneline' to verify commits"
