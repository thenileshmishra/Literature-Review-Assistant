# Architecture Documentation

## System Overview

The Literature Review Assistant is built as a microservices architecture with two main services:

1. **Frontend Service**: Next.js 14 application providing the user interface
2. **Backend Service**: FastAPI application wrapping the AutoGen multi-agent system

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Browser Client                            │
└──────────────────────────────────────────────────────────────────┘
                               │
                               │ HTTP/SSE
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Frontend Service (Next.js)                     │
│ ─────────────────────────────────────────────────────────────── │
│  • Next.js 14 App Router                                         │
│  • TypeScript + Tailwind CSS                                     │
│  • Server Components & Client Components                         │
│  • TanStack Query for state management                           │
│  • EventSource for SSE streaming                                 │
│  • Port: 3000                                                    │
└──────────────────────────────────────────────────────────────────┘
                               │
                               │ REST API + SSE
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Backend Service (FastAPI)                      │
│ ─────────────────────────────────────────────────────────────── │
│  API Layer:                                                      │
│    • POST /api/v1/reviews - Create review                       │
│    • GET /api/v1/reviews/{id} - Get review                      │
│    • GET /api/v1/reviews/{id}/stream - SSE stream               │
│                                                                  │
│  Services Layer:                                                 │
│    • ReviewService - Wraps AutoGen orchestrator                 │
│    • SessionManager - In-memory session storage                 │
│                                                                  │
│  Port: 8000                                                     │
└──────────────────────────────────────────────────────────────────┘
                               │
                               │ Direct Python calls
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                  AutoGen Multi-Agent System                       │
│ ─────────────────────────────────────────────────────────────── │
│  LitRevOrchestrator                                              │
│         │                                                        │
│         ▼                                                        │
│  LitRevTeam (RoundRobinGroupChat)                               │
│         │                                                        │
│         ├──> SearchAgent                                        │
│         │      ├── ArxivSearchTool                              │
│         │      └── Crafts queries, filters papers               │
│         │                                                        │
│         └──> SummarizerAgent                                    │
│                └── Generates markdown reviews                    │
│                                                                  │
│  • AutoGen AgentChat 0.4+                                       │
│  • OpenAI GPT-4o-mini/GPT-4o                                    │
│  • arXiv API integration                                        │
└──────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (built on Radix UI)
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Real-time Updates**: EventSource (SSE)

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic v2
- **Streaming**: sse-starlette
- **Configuration**: pydantic-settings

### AI/ML
- **Agent Framework**: Microsoft AutoGen 0.4+
- **LLM Provider**: OpenAI
- **Models**: GPT-4o-mini (default), GPT-4o, GPT-4-turbo
- **Data Source**: arXiv API

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Networking**: Bridge network

## Data Flow

### 1. Create Review Flow

```
User → Frontend → Backend → AutoGen
 │         │          │         │
 │         │          │         ├─> SearchAgent
 │         │          │         │     └─> arXiv API
 │         │          │         │
 │         │          │         └─> SummarizerAgent
 │         │          │               └─> OpenAI GPT
 │         │          │
 │         │          └─> SessionManager (store)
 │         │
 │         └─> EventSource connection
 │
 └─> Display results
```

**Steps:**
1. User submits a search form with a topic
2. Frontend sends POST to `/api/v1/reviews`
3. Backend creates session and returns review ID
4. Frontend connects to SSE stream at `/api/v1/reviews/{id}/stream`
5. Backend starts AutoGen orchestrator
6. SearchAgent queries arXiv and returns 5 papers
7. SummarizerAgent generates literature review
8. Messages stream back to frontend via SSE
9. Session marked as completed

### 2. Message Streaming

The backend uses Server-Sent Events (SSE) to stream agent messages in real-time:

```python
# Backend (FastAPI)
async def review_event_generator(review_id: str):
    async for message in review_service.start_review(...):
        yield {
            "event": "message",
            "data": json.dumps(message)
        }
```

```typescript
// Frontend (Next.js)
const eventSource = new EventSource(`${API_URL}/reviews/${id}/stream`)
eventSource.addEventListener('message', (e) => {
    const msg = JSON.parse(e.data)
    setMessages(prev => [...prev, msg])
})
```

## Component Architecture

### Frontend Components

```
src/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Home page
│   └── globals.css          # Global styles
│
├── components/
│   ├── ui/                  # Base UI components (shadcn)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── label.tsx
│   │
│   ├── layout/              # Layout components
│   │   └── Header.tsx
│   │
│   ├── search/              # Search-related
│   │   └── SearchForm.tsx
│   │
│   ├── chat/                # Message display
│   │   └── MessageDisplay.tsx
│   │
│   └── papers/              # Paper display
│       ├── PaperCard.tsx
│       └── PaperList.tsx
│
├── lib/
│   ├── api/                 # API client
│   │   ├── client.ts        # Axios instance
│   │   └── reviews.ts       # Review API functions
│   │
│   ├── hooks/               # Custom hooks
│   │   └── useReviewStream.ts  # SSE streaming hook
│   │
│   └── types/               # TypeScript types
│       └── api.ts
│
└── providers/
    └── QueryProvider.tsx    # React Query provider
```

### Backend Services

```
backend/
├── app/
│   ├── main.py              # FastAPI app & CORS
│   ├── config.py            # Settings
│   │
│   ├── api/routes/
│   │   ├── health.py        # Health checks
│   │   ├── reviews.py       # Review CRUD
│   │   └── stream.py        # SSE streaming
│   │
│   ├── models/
│   │   ├── requests.py      # Request models
│   │   └── responses.py     # Response models
│   │
│   └── services/
│       ├── review_service.py    # AutoGen wrapper
│       └── session_manager.py   # Session storage
```

## State Management

### Frontend State
- **Server State**: TanStack Query caches API responses
- **Local State**: React useState for UI state
- **Streaming State**: Custom useReviewStream hook

### Backend State
- **Sessions**: In-memory dictionary (could migrate to Redis)
- **Messages**: Stored in session objects
- **Papers**: Stored in session objects

## Security Considerations

### Current Implementation
- CORS configured for specific origins
- No authentication required (single-user mode)
- OpenAI API key stored server-side only
- Input validation via Pydantic

### Future Enhancements
- User authentication (JWT)
- API key rotation
- Rate limiting
- Request signing
- HTTPS enforcement

## Scalability

### Current Limitations
- In-memory session storage (lost on restart)
- Single instance only
- No load balancing

### Scaling Strategy
1. **Horizontal Scaling**:
   - Add Redis for session storage
   - Use message queue (RabbitMQ/Redis) for async processing
   - Deploy multiple backend instances behind load balancer

2. **Vertical Scaling**:
   - Increase compute resources for AutoGen agents
   - Use faster LLM models

3. **Caching**:
   - Cache arXiv search results
   - Cache LLM responses for common queries

## Deployment Architecture (AWS)

```
┌────────────────────────────────────────────────┐
│              Route 53 (DNS)                    │
└────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│         Application Load Balancer              │
└────────────────────────────────────────────────┘
          │                      │
          ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│  ECS Service     │   │  ECS Service     │
│  (Frontend)      │   │  (Backend)       │
│                  │   │                  │
│  Task Def:       │   │  Task Def:       │
│  - Next.js       │   │  - FastAPI       │
│  - Port 3000     │   │  - AutoGen       │
└──────────────────┘   │  - Port 8000     │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  ElastiCache     │
                       │  (Redis)         │
                       │  - Sessions      │
                       └──────────────────┘
```

## Monitoring & Observability

### Logging
- Backend: Python logging to stdout
- Frontend: Next.js logs
- Centralized: CloudWatch (AWS) or similar

### Metrics
- Request/response times
- Error rates
- Active sessions
- LLM token usage

### Health Checks
- `/health` - Basic health
- `/ready` - Readiness for traffic
- Docker healthcheck directives

## Development Workflow

1. **Local Development**: Run services locally with hot-reload
2. **Docker Development**: Use docker-compose.dev.yml
3. **Testing**: Pytest for backend, Jest for frontend
4. **CI/CD**: GitHub Actions (future)
5. **Deployment**: Docker Compose or AWS ECS

## Future Enhancements

1. **Features**:
   - User authentication
   - Save/export reviews
   - Multiple data sources (PubMed, Google Scholar)
   - Citation management

2. **Architecture**:
   - Migrate to Redis for sessions
   - Add message queue for async processing
   - Implement WebSocket fallback
   - Add database for persistence

3. **Performance**:
   - Response caching
   - CDN for frontend
   - Parallel agent execution
   - Streaming optimizations
