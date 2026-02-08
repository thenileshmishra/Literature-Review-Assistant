# 📚 Literature Review Assistant

AI-powered literature review assistant that helps researchers discover and synthesize academic papers from arXiv using multi-agent collaboration.

## Features

- **Microservices Architecture**: Modern 2-service architecture with FastAPI backend and Next.js frontend
- **Multi-Agent System**: Uses AutoGen AgentChat with specialized search and summarizer agents
- **arXiv Integration**: Searches and retrieves papers directly from arXiv
- **Real-time Streaming**: SSE (Server-Sent Events) for live agent updates
- **Modern UI**: Beautiful dark-themed Next.js interface with Tailwind CSS
- **Docker Ready**: Production-ready containerization with Docker Compose

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│               FRONTEND SERVICE (Next.js)                         │
│  - Port 3000                                                     │
│  - TypeScript + Tailwind CSS                                    │
│  - Server-Sent Events (SSE) for streaming                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ HTTP/SSE
┌─────────────────────────────────────────────────────────────────┐
│               BACKEND SERVICE (FastAPI)                          │
│  - Port 8000                                                     │
│  - RESTful API + SSE endpoints                                  │
│  - Wraps AutoGen orchestrator                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOGEN MULTI-AGENT SYSTEM                    │
│                                                                  │
│              LitRevOrchestrator → LitRevTeam                    │
│                  ├── SearchAgent                                │
│                  └── SummarizerAgent                            │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 20+** (for frontend)
- **Docker & Docker Compose** (for containerized deployment)
- **OpenAI API Key**

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/nileshmishra/litrev-assistant.git
   cd litrev-assistant
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Install Python dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the backend**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

#### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local if needed (default: http://localhost:8000)
   ```

3. **Run the frontend**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## Environment Variables

### Backend (.env)
```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional (with defaults)
DEFAULT_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
DEBUG=false
MAX_PAPERS=10
DEFAULT_PAPERS=5
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Literature Review Assistant
```

## Project Structure

```
.
├── backend/                    # FastAPI Backend Service
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Backend configuration
│   │   ├── api/               # API routes
│   │   │   └── routes/
│   │   │       ├── health.py  # Health checks
│   │   │       ├── reviews.py # Review CRUD
│   │   │       └── stream.py  # SSE streaming
│   │   ├── models/            # Request/Response models
│   │   ├── services/          # Business logic
│   │   │   ├── review_service.py
│   │   │   └── session_manager.py
│   │   └── utils/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Next.js Frontend Service
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   ├── components/        # React components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── layout/
│   │   │   ├── search/
│   │   │   ├── chat/
│   │   │   └── papers/
│   │   ├── lib/
│   │   │   ├── api/           # API client
│   │   │   ├── hooks/         # Custom hooks
│   │   │   └── types/         # TypeScript types
│   │   └── providers/         # React providers
│   ├── Dockerfile
│   ├── package.json
│   └── next.config.js
│
├── src/                        # AutoGen Multi-Agent System
│   ├── orchestrator/           # (Unchanged)
│   ├── agents/                 # SearchAgent, SummarizerAgent
│   ├── teams/                  # LitRevTeam
│   ├── tools/                  # ArxivSearchTool
│   ├── models/                 # Data models
│   ├── config/                 # Settings
│   └── core/                   # Utilities
│
├── docker-compose.yml          # Multi-service orchestration
├── docker-compose.dev.yml      # Development overrides
├── Makefile                    # Build commands
└── README.md
```

## API Endpoints

### Health
- `GET /health` - Health check
- `GET /ready` - Readiness probe

### Reviews
- `POST /api/v1/reviews` - Create a new review
- `GET /api/v1/reviews/{id}` - Get review details
- `GET /api/v1/reviews/{id}/stream` - Stream review progress (SSE)
- `DELETE /api/v1/reviews/{id}` - Delete a review
- `GET /api/v1/reviews` - List reviews

For detailed API documentation, visit `/docs` after starting the backend.

## Development

### Using Makefile

```bash
# Install dependencies
make install

# Run development servers
make dev                 # Both services
make dev-backend         # Backend only
make dev-frontend        # Frontend only

# Docker commands
make build               # Build Docker images
make up                  # Start services
make down                # Stop services

# Testing
make test                # Run all tests
make test-backend        # Backend tests
make test-frontend       # Frontend tests
```

### Manual Commands

**Backend Development:**
```bash
uvicorn backend.app.main:app --reload --port 8000
```

**Frontend Development:**
```bash
cd frontend && npm run dev
```

**Run Tests:**
```bash
# Backend
PYTHONPATH=. pytest tests/backend -v

# Frontend
cd frontend && npm test
```

## Deployment

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run in production mode
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### AWS Deployment

For AWS deployment with ECS/EKS, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **AI**: AutoGen AgentChat 0.4+
- **LLM**: OpenAI GPT-4o-mini/GPT-4o
- **Data Source**: arXiv API
- **Validation**: Pydantic 2.0+
- **Streaming**: SSE-Starlette

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI)
- **State Management**: TanStack Query
- **HTTP Client**: Axios
- **Streaming**: EventSource (SSE)

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Deployment**: AWS ECS/EKS (future)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [AutoGen](https://github.com/microsoft/autogen) - Multi-agent framework
- [arXiv API](https://arxiv.org/help/api) - Academic paper database
- [OpenAI](https://openai.com/) - LLM provider
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

## Support

For issues and questions, please open an issue on GitHub.
