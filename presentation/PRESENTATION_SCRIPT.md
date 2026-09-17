# Presentation script — Task Manager API

Guide for presenting to the technical panel. Built for screen-sharing
(repo/IDE), alternating between talking and showing code.

Suggested total time: 15-20 min presentation + Q&A.

Companion files in this folder: [`ARCHITECTURE.md`](./ARCHITECTURE.md) (diagrams
referenced in section 3), [`DEMO_CHECKLIST.md`](./DEMO_CHECKLIST.md) (step-by-step
for section 5), and [`ANTICIPATED_QA.md`](./ANTICIPATED_QA.md) (prep for section 7
and general Q&A). See the main [`README.md`](../README.md) for full setup and
architecture details.

---

## 1. Opening and context (1-2 min)

"The exercise asked for a task management API with FastAPI/Django/Flask,
authentication, full CRUD, filtering, pagination, tests, Docker, and an
integrated frontend — plus documenting GenAI tool usage in the process. I
chose FastAPI for its strong typing via Pydantic and automatic OpenAPI
generation, and React with Vite on the frontend."

## 2. User story (1 min)

State the use case that drove the modeling decisions in one line:

> "A user creates tasks, can assign them to another user, and both — owner and assignee — can track and update status through to completion."

This justifies the permission rule (owner OR assignee can edit) implemented
in `_get_owned_task`.

## 3. Architecture (4-5 min)

Open [`ARCHITECTURE.md`](./ARCHITECTURE.md) or walk the folder tree directly
in the editor. Points to cover, in order:

1. **Layered separation**: `api/` (HTTP) → `crud/` (data access) → `models/` (ORM). Routes never touch SQLAlchemy directly — this is what gives you testability and is the core argument for the "Clean Architecture" criterion in the brief.
2. **Pydantic schemas split by operation** (`TaskCreate`, `TaskUpdate`, `TaskRead`): keeps `hashed_password` from ever being exposed, and keeps a `PATCH` from wiping fields the client didn't send (`exclude_unset=True`).
3. **Stateless JWT auth**: token carries the user's email as `sub`, expires after 24h. No server-side session — simpler to scale horizontally.
4. **Rate limiting with graceful fallback**: if the library isn't installed, the decorator becomes a no-op instead of crashing the app — shows attention to restricted execution environments.
5. **Celery + Redis for an async job**: completing a task fires a background notification. The `.delay()` call is wrapped in try/except — if Redis is down, the request still succeeds, only the notification is skipped. Frame this as a deliberate resilience decision, not an oversight.

## 4. Data model (2 min)

Show `app/models/user.py` and `app/models/task.py`. Highlight:
- `Task` has two distinct FKs to `User` — `owner_id` and `assignee_id` — so the creator and the assignee can be different people.
- `status` is an Enum (`pending`, `in_progress`, `done`), not a free string — prevents inconsistent values in the database.

## 5. Live demo (5-6 min)

Follow [`DEMO_CHECKLIST.md`](./DEMO_CHECKLIST.md) — it has the exact sequence of
steps (Swagger + frontend) so nothing gets missed during the presentation.

## 6. Tests and quality (2 min)

Run `pytest` live (or show the already-captured output) and mention:
- 14 tests, ~95% coverage.
- Covers: auth (register, login, duplicate email, wrong password), task CRUD, filtering by status and due_date, pagination, and permission rules (owner/assignee).
- Fixtures in `conftest.py` isolate each test with an in-memory SQLite database — tests don't interfere with each other or depend on external infrastructure.

## 7. GenAI usage (2-3 min)

This part is explicitly evaluated by the brief. Don't undersell it — show that
you validated and corrected the output, not just pasted generated code. Check
[`ANTICIPATED_QA.md`](./ANTICIPATED_QA.md) for likely follow-up questions, but the
short version is:

> "I used Claude as a pair-programming tool inside an environment with real code execution — every generated piece was actually run, not just read. That caught three real issues a visual review wouldn't: Pydantic's `EmailStr` needs the `email-validator` extra; `passlib` 1.7.4 breaks with `bcrypt` 4.1+ due to an internal API incompatibility; and `@app.on_event('startup')` is deprecated in favor of the `lifespan` pattern. None of these are things you'd catch reading a diff — only by running the code."

The full section is in the project's main [`README.md`](../README.md#use-of-genai-tools).

## 8. Closing and next steps (1 min)

Mention 2-3 items from the README's ["Possible next steps"](../README.md#possible-next-steps)
list (refresh tokens, Alembic migrations, frontend E2E tests) — shows you have
visibility into what's missing without it sounding like an excuse.

---

## General presentation tips

- Don't read this script on screen — use it as a reference before/during, but talk while looking at the code.
- If you get stuck on a technical question, "I'm not sure, but my hypothesis would be X, and I'd verify Y" beats making something up.
- Have your environment already set up BEFORE the call — don't burn presentation time installing dependencies.
