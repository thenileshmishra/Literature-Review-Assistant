
# 🔧 Microservice Refactoring Instruction

## Goal: Convert Monorepo Split-Source Backend into Production-Ready Microservice

You are a senior Python architect.
Refactor this repository to eliminate the root-level `src/` directory and consolidate all backend logic into `backend/app/`.

---

# 🎯 Target State (Non-Negotiable)

After refactoring:

* No `src/` directory exists.
* No imports use `src.*`
* No imports use `backend.app.*`
* All backend imports use `app.*`
* Backend builds independently with:

```
docker build ./backend
```

* No `PYTHONPATH` hacks
* Docker context is `./backend`
* Tests run from inside `backend/`

---

# 📁 Required Final Backend Structure

```
backend/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │
│   ├── services/
│   ├── orchestrator/
│   ├── agents/
│   ├── teams/
│   ├── tools/
│   ├── core/
│   ├── config/
│   ├── models/        # API DTOs (requests/responses)
│   └── schemas/       # Domain/business models (from old src/models)
│
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── pytest.ini
└── .dockerignore
```

Frontend remains unchanged.

---

# 🛠 REQUIRED REFACTOR STEPS

## Step 1 — Move Source Code

Move the following directories:

```
src/agents        → backend/app/agents
src/orchestrator  → backend/app/orchestrator
src/tools         → backend/app/tools
src/core          → backend/app/core
src/config        → backend/app/config
src/teams         → backend/app/teams
src/models        → backend/app/schemas
```

Delete the `src/` directory afterward.

---

## Step 2 — Fix All Imports

Replace all imports as follows:

| OLD                     | NEW                     |
| ----------------------- | ----------------------- |
| from src.agents.X       | from app.agents.X       |
| from src.orchestrator.X | from app.orchestrator.X |
| from src.tools.X        | from app.tools.X        |
| from src.core.X         | from app.core.X         |
| from src.config.X       | from app.config.X       |
| from src.teams.X        | from app.teams.X        |
| from src.models.X       | from app.schemas.X      |
| from backend.app.X      | from app.X              |

After changes:

* There must be ZERO occurrences of:

  * `src.`
  * `backend.app.`

---

## Step 3 — Update FastAPI Entrypoint

Ensure `backend/app/main.py` imports use:

```
from app.api.routes import ...
from app.config.settings import ...
```

Application must run via:

```
uvicorn app.main:app
```

---

## Step 4 — Clean Dockerfile

Create `backend/Dockerfile` with:

```
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Important:

* Do NOT set PYTHONPATH
* Do NOT copy root directory
* Only copy `app/`

---

## Step 5 — Fix docker-compose.yml

Backend service must use:

```
build:
  context: ./backend
```

NOT root context.

---

## Step 6 — Move Tests

Move:

```
tests/ → backend/tests/
```

Update all test imports to use:

```
from app.*
```

Create `backend/pytest.ini`:

```
[pytest]
testpaths = tests
pythonpath = .
```

---

## Step 7 — Requirements Consolidation

* Remove root `requirements.txt`
* Keep only `backend/requirements.txt`
* Ensure no duplicate dependency definitions

---

## Step 8 — Verification Checklist (Agent Must Validate)

After refactor, confirm:

1. `grep -r "src\." backend/` returns nothing
2. `grep -r "backend.app" backend/` returns nothing
3. `docker build ./backend` succeeds
4. `pytest backend/tests` passes
5. `uvicorn app.main:app` runs from inside backend directory

---

# 🚀 CI/CD Expectations

Backend CI must:

* Trigger only when `backend/**` changes
* Build using `context: ./backend`
* Push to ECR independently

Frontend CI must not build backend.

---

# 🧠 Architecture Constraints

Maintain clean layering:

API → Service → Orchestrator → Agent → Tool → Core

Rules:

* API must not directly call agents
* Agents must not import FastAPI
* Tools must not depend on API
* Config must be injectable

---

# 🧹 Remove the Following

* Root-level `src/`
* Root-level `requirements.txt`
* Any PYTHONPATH environment variable
* Any Docker COPY of entire repo
* Any import using relative traversal like `../../`

---

# 📌 Final Deliverable

A backend that:

* Is fully isolated
* Builds independently
* Has clean `app.*` imports
* Is microservice-ready
* Is production deployable to ECS/Kubernetes

---

If anything is ambiguous, choose the option that improves:

* Service isolation
* Docker independence
* Import clarity
* CI/CD modularity
