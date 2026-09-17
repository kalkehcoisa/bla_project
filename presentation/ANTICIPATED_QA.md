# Anticipated panel questions

Likely questions based on the brief's evaluation criteria, with a base answer for each. Referenced from section 7 of [`PRESENTATION_SCRIPT.md`](./PRESENTATION_SCRIPT.md); architecture questions link back to [`ARCHITECTURE.md`](./ARCHITECTURE.md) and the main [`README.md`](../README.md).

## Architecture

**"Why separate api/crud/schemas/models instead of putting everything directly in the route, like a lot of FastAPI tutorials do?"**
Because a route tested in isolation gets coupled to HTTP; by separating data access into `crud/`, the business logic can be tested without assembling a full HTTP request, and the persistence layer can be swapped without touching the routes.

**"How would you make sure two users can't see each other's tasks?"**
That's already the current rule (see [`ARCHITECTURE.md`](./ARCHITECTURE.md#task-permission-rule)):
`_get_owned_task` checks `owner_id` and `assignee_id` against the authenticated user, returning 403/404. What's missing for production is the same filter on the list endpoint (`GET /tasks/`) — today it returns every task in the system, not just the user's own. [If asked, be upfront about this gap — it's a real improvement area, wasn't in the minimum scope, but worth naming.]

## Authentication

**"Why JWT instead of a cookie-based session?"**
Stateless: no server-side session storage needed, scales horizontally without sticky sessions. Trade-off: revoking a token before it expires isn't trivial without a blocklist — a known limitation, listed under "next steps" in the README.

**"The token expires in 24h — is that secure?"**
For this exercise's scope, yes. In production I'd shrink the access token window (e.g. 15-30 min) and add a longer-lived refresh token.

## Testing

**"Why in-memory SQLite for tests when production uses Postgres?"**
Speed and isolation — each test spins up/tears down the schema in memory, no external dependency. The risk is a Postgres-specific feature (e.g. some constraints) not being caught by the suite. For this scope the trade-off is worth it; on a larger project I'd also run the suite against a real Postgres instance in CI.

**"What was your TDD approach, if any?"**
Not everything was written test-first, but nothing was considered done until the tests actually passed — the suite ran for real after every meaningful change, not just at the end.

## GenAI usage

**"How did you validate what the AI generated?"**
By actually running it: installed dependencies into a clean venv and ran the test suite; built the frontend with `npm run build`. That caught 3 real dependency-version issues (detailed in the README) that a code read-through wouldn't catch.
Did a code read through, trying to catch problems and understand the code.
Used the system to see it working and did some fixes like adding a start button to make the Pending status. It made the system look more like users managing tasks and added filtering in list_tasks to only return the ones owned or assigned to the user requesting them.

**"Do you understand all the generated code, or did you just accept what came
out?"** [Answer honestly — if you reviewed and understand every decision, say so and be ready to walk through any specific piece asked about, like the pagination math in `crud/task.py` or the JWT decoding flow in `core/security.py`.]

## Scalability / production readiness

**"What would you change to run this in production for real?"**
Alembic migrations instead of `create_all`, refresh tokens, more granular rate limiting per user (currently per IP), structured logging, metrics (e.g. Prometheus), and filtering the task list by user (see the gap noted above).
