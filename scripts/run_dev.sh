#!/bin/bash
# =============================================================================
# Development Server Script
# =============================================================================
# Starts the Streamlit development server with hot-reload
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please update .env with your API key."
fi

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set Python path
export PYTHONPATH="$PROJECT_ROOT"

# Start development server
echo "Starting development server..."
echo "Access the app at: http://localhost:8501"
echo ""

streamlit run frontend/app.py \
    --server.port=8501 \
    --server.runOnSave=true \
    --browser.gatherUsageStats=false
