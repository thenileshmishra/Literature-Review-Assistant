# Literature Review Assistant

An AI-powered research tool that automates literature reviews using a multi-agent system. Enter a topic, and a team of specialized AI agents searches academic databases, evaluates papers, and produces a structured literature review — all streamed in real time.

**Live:** [agent.nileshmishra.info](https://agent.nileshmishra.info)

## How It Works

1. **PlannerAgent** decomposes a broad topic into focused sub-queries
2. **SearchAgent** searches arXiv and Semantic Scholar, deduplicates results
3. **SummarizerAgent** writes a structured Markdown literature review
4. **CriticAgent** scores the draft on coverage, clarity, and relevance — if it doesn't pass, the review is revised and re-evaluated

All agent activity streams to the browser via SSE, so you see progress as it happens.

## Architecture

```
Browser → Next.js (React) → Nginx (reverse proxy) → FastAPI → AutoGen Multi-Agent System
                                                                  ├── PlannerAgent
                                                                  ├── SearchAgent (arXiv + Semantic Scholar)
                                                                  ├── SummarizerAgent
                                                                  └── CriticAgent (reflection loop)
```

**Backend:** FastAPI, AutoGen AgentChat, OpenAI GPT-4o, Pydantic, SSE-Starlette
**Frontend:** Next.js 14, TypeScript, Ant Design, Tailwind CSS, EventSource (SSE)
**Infra:** Docker, Nginx, AWS EC2 + ECR, GitHub Actions CI/CD, Let's Encrypt SSL

## Quick Start

### Prerequisites

- Python 3.10+, Node.js 20+, Docker
- OpenAI API key

### Run with Docker Compose

```bash
git clone https://github.com/thenileshmishra/Literature-Review-Assistant.git
cd Literature-Review-Assistant

cp .env.example .env
# Add your OPENAI_API_KEY to .env

docker-compose up --build
```

Open [localhost:3000](http://localhost:3000).

### Local Development

```bash
# Backend
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Project Structure

```
backend/
  app/
    agents/        # PlannerAgent, SearchAgent, SummarizerAgent, CriticAgent
    tools/         # ArxivSearchTool, SemanticScholarTool
    orchestrator/  # LitRevOrchestrator — wires agents into a team
    api/routes/    # REST + SSE streaming endpoints
    services/      # Business logic (review lifecycle)
    config/        # Pydantic settings

frontend/
  src/
    app/           # Next.js App Router (single-page app)
    components/    # SearchForm, MessageDisplay, PaperList, PaperCard
    lib/           # API client, hooks (useReviewStream), types
```

## Deployment

Pushes to `main` trigger a GitHub Actions pipeline that:

1. Builds and pushes Docker images to AWS ECR
2. SSHs into EC2, pulls new images, restarts containers
3. Nginx handles SSL termination with Let's Encrypt certs
