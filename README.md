# Task Manager

A small full-stack task management system: FastAPI backend + React (Vite) frontend, built as a technical interview exercise.

Users can register, log in, create tasks, assign them to other users, mark them as completed, and filter the list by status and due date.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.0, Pydantic v2, JWT auth (python-jose + passlib), Celery + Redis for background jobs, slowapi for rate limiting, pytest for tests.
- **Frontend:** React 18 + Vite, plain CSS (no UI framework), fetch-based API client.
- **Database:** PostgreSQL in Docker, SQLite for local dev/tests (no setup required).
- **Infra:** Docker Compose (API, worker, Postgres, Redis, frontend).

## Architecture & key decisions

The backend follows a simple layered structure to keep concerns separated:

```
app/
  api/v1/endpoints/   HTTP layer: request/response, status codes, auth checks
  crud/               Data access layer: pure SQLAlchemy queries, no HTTP concerns
  schemas/            Pydantic models for input validation and output shaping
  models/             SQLAlchemy ORM models
  core/               Config, security (JWT/hashing), Celery setup
  tasks/              Celery background jobs
```

Endpoints never touch the ORM directly — they call `crud/` functions, which makes the data-access logic independently testable and keeps route handlers thin. Pydantic schemas are split into `Create`/`Update`/`Read` variants so the API never accepts or leaks fields it shouldn't (e.g. `hashed_password` is never serialized back).

Other decisions:

- **JWT auth** with `python-jose`, tokens carry the user's email as `sub`. Passwords are hashed with bcrypt via `passlib`.
- **SQLite by default** for local development and tests (zero setup), **Postgres** in Docker Compose to match a production-like environment.
- **Rate limiting** via `slowapi` on the task-creation endpoint, degrading gracefully (no-op) if the library isn't installed, so the app still runs in restricted environments.
- **Celery + Redis** for a background notification job fired when a task is marked `done`. The `.delay()` call is wrapped so a missing broker never breaks a request — useful for running the API without spinning up Redis during a quick demo.
- **Ownership rules:** a task is visible/editable by its owner or its assignee; only those users can update, complete, or delete it.

## Running with Docker (recommended)

```bash
docker compose up --build
```

- API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173
- Postgres: localhost:5432, Redis: localhost:6379

Demo credentials (seeded automatically on first run):

| Email               | Password  |
|---------------------|-----------|
| demo@example.com    | demo1234  |
| alice@example.com   | alice1234 |

## Running locally without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

This uses SQLite (`taskmanager.db`) and seeds the same demo users on startup.
Background jobs need Redis running locally (`redis-server`) plus:

```bash
celery -A app.core.celery_app worker --loglevel=info
```

If Redis isn't available, the API still works — completing a task just skips the notification job instead of failing.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Tests

```bash
cd backend
pytest
```

14 tests covering auth (register/login/duplicate email/bad password), task CRUD, status/due-date filtering, pagination, and ownership permissions. Coverage is reported in the terminal and as HTML (`htmlcov/`); current coverage is ~92%.

## API documentation

Interactive Swagger UI is available at `/docs` (ReDoc at `/redoc`) once the API is running.

## Presentation materials

The [`presentation/`](../presentation) folder has the material prepared for the panel presentation and code review, kept separate from the project code:

- [`PRESENTATION_SCRIPT.md`](../presentation/PRESENTATION_SCRIPT.md) — section-by-section talking script (context, architecture, demo, tests, GenAI usage, closing).
- [`ARCHITECTURE.md`](../presentation/ARCHITECTURE.md) — component and auth-flow diagrams, plus the reasoning behind the layered structure.
- [`DEMO_CHECKLIST.md`](../presentation/DEMO_CHECKLIST.md) — exact step-by-step for the live demo (Swagger + frontend).
- [`ANTICIPATED_QA.md`](../presentation/ANTICIPATED_QA.md) — likely panel questions with prepared answers.

---

## Use of GenAI tools

This project was built with Claude (Anthropic) as the GenAI pair-programming tool, working iteratively inside a coding sandbox rather than a single one-shot generation.

### Prompt used to scaffold the project

The scaffolding prompt (paraphrased from the actual session) was:

> Build a FastAPI backend for a task management API: JWT auth, CRUD for tasks,
> assignment to users, filtering by status and due date, pagination, rate limiting,
> and a Celery+Redis background job triggered when a task is completed. Structure it
> with a clear separation between HTTP routes, data access, and schemas. Add pytest
> tests for the critical endpoints with coverage reporting. Then build a React (Vite)
> frontend that consumes it: login/register, a task list with filters and pagination,
> a create/edit form, and complete/delete actions. Finish with Dockerfiles, a
> docker-compose.yml wiring Postgres/Redis/API/worker/frontend together, and a README.

Follow-up prompts refined specific pieces (e.g. "make the Celery call fail silently if the broker is unreachable", "add ownership checks so only the owner or assignee can modify a task").

### Validating the output

Every generated piece was actually run, not just read:

- The backend was installed into a real virtualenv and the full pytest suite was executed (`14 passed`, ~92% coverage) before moving on.
- The frontend was installed with `npm install` and built with `npm run build` to catch import/syntax errors before treating it as done.

### Corrections made to the AI-generated code

Running the code surfaced three real issues that a "looks correct" read-through
would have missed:

1. **`pydantic.EmailStr` failed at import time** — Pydantic v2 requires the optional `email-validator` dependency. Fixed by adding `pydantic[email]` instead of bare `pydantic`.
2. **`passlib` + modern `bcrypt` incompatibility** — `passlib 1.7.4` calls a `bcrypt` internal attribute that was removed in `bcrypt>=4.1`, causing password hashing to raise at runtime. Pinned `bcrypt==4.0.1`, a known-compatible version, rather than patching around it.
3. **Deprecated `@app.on_event("startup")`** — still functional but flagged as deprecated by FastAPI; replaced with the `lifespan` context-manager pattern.

None of these were "hallucinated" APIs — they were real dependency-version interactions that only show up when the code is actually executed, which is why running the test suite (rather than just reading the diff) was part of the process.
(See also [`presentation/ANTICIPATED_QA.md`](../presentation/ANTICIPATED_QA.md#genai-usage) for the condensed talking-point version of this section.)

### Edge cases and validation handled

- Duplicate email registration returns `400` instead of a raw DB integrity error.
- Missing/invalid JWT returns `401` with a `WWW-Authenticate` header.
- Accessing or modifying a task you don't own/aren't assigned to returns `403`/`404` appropriately (404 for tasks that don't exist, 403 for ones that exist but aren't yours).
- `PATCH` uses `exclude_unset=True` so partial updates don't accidentally null out fields the client didn't send.
- The Celery call is defensively wrapped so a missing Redis broker degrades to "no notification" instead of a 500 error — important for demoing the app without the full Docker stack running.

### Assessment of the AI-generated code

The generated structure (routes/crud/schemas separation, Pydantic schema variants, dependency-injected DB sessions) matches idiomatic FastAPI patterns and needed no architectural rework. The gaps were entirely at the dependency-version level (bcrypt/passlib, email-validator) — the kind of issue that's invisible without actually running the code, which is the main practical lesson from this exercise:
  treat AI-generated code as a draft to execute and verify, not a finished artifact to read and trust.

## Possible next steps

- Refresh tokens / token revocation (current JWTs are stateless with a 24h expiry).
- Alembic migrations instead of `create_all` for schema evolution.
- WebSocket or polling-based live updates when a task is completed by someone else.
- E2E tests for the frontend (Playwright) alongside the backend pytest suite.
