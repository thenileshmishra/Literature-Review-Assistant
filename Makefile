# =============================================================================
# Makefile for Literature Review Assistant (Microservices)
# =============================================================================
# Commands for development and deployment
# =============================================================================

.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend build up down logs test lint format clean

# Default target
help:
	@echo "Literature Review Assistant - Available Commands"
	@echo "================================================"
	@echo ""
	@echo "Development:"
	@echo "  make install           - Install all dependencies"
	@echo "  make install-backend   - Install backend dependencies"
	@echo "  make install-frontend  - Install frontend dependencies"
	@echo "  make dev               - Run both services in development"
	@echo "  make dev-backend       - Run backend only"
	@echo "  make dev-frontend      - Run frontend only"
	@echo ""
	@echo "Docker:"
	@echo "  make build             - Build Docker images"
	@echo "  make up                - Start services with Docker Compose"
	@echo "  make up-dev            - Start development containers"
	@echo "  make down              - Stop Docker services"
	@echo "  make logs              - View container logs"
	@echo "  make logs-backend      - View backend logs"
	@echo "  make logs-frontend     - View frontend logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests"
	@echo "  make test-backend      - Run backend tests"
	@echo "  make test-frontend     - Run frontend tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              - Run linters"
	@echo "  make format            - Format code"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean             - Remove build artifacts"
	@echo "  make clean-all         - Remove all generated files"

# =============================================================================
# Installation
# =============================================================================

install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	pip install -r backend/requirements.txt
	pip install -r backend/requirements-dev.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# =============================================================================
# Development
# =============================================================================

dev:
	@echo "Starting both services in development mode..."
	docker-compose -f docker-compose.dev.yml up

dev-backend:
	@echo "Starting backend development server..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# =============================================================================
# Testing
# =============================================================================

test: test-backend

test-backend:
	@echo "Running backend tests..."
	cd backend && pytest tests -v --tb=short

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

test-cov:
	@echo "Running backend tests with coverage..."
	cd backend && pytest tests -v --cov=app --cov-report=html

# =============================================================================
# Code Quality
# =============================================================================

lint:
	@echo "Running linters..."
	ruff check backend/app backend/tests
	mypy backend/app --ignore-missing-imports

format:
	@echo "Formatting code..."
	ruff format backend/app backend/tests
	ruff check --fix backend/app backend/tests

# =============================================================================
# Docker
# =============================================================================

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting containers..."
	docker-compose up -d

up-dev:
	@echo "Starting development containers..."
	docker-compose -f docker-compose.dev.yml up

down:
	@echo "Stopping containers..."
	docker-compose down

logs:
	@echo "Viewing all logs..."
	docker-compose logs -f

logs-backend:
	@echo "Viewing backend logs..."
	docker-compose logs -f backend

logs-frontend:
	@echo "Viewing frontend logs..."
	docker-compose logs -f frontend

restart:
	@echo "Restarting containers..."
	docker-compose restart

# =============================================================================
# Cleanup
# =============================================================================

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	rm -rf frontend/.next frontend/node_modules 2>/dev/null || true

clean-all: clean
	@echo "Cleaning all generated files..."
	rm -rf venv/ .venv/ 2>/dev/null || true
	docker-compose down -v --rmi all 2>/dev/null || true
