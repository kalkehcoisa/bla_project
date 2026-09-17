# Live demo checklist

Set all of this up BEFORE joining the call. Steps below are referenced from
section 5 of [`PRESENTATION_SCRIPT.md`](./PRESENTATION_SCRIPT.md).

## Preparation (before the presentation)

- [ ] `docker compose up --build` already running and verified once (or local
      setup with `uvicorn` + `npm run dev` already validated)
- [ ] Browser open in two tabs: `http://localhost:8000/docs` (Swagger) and
      `http://localhost:5173` (frontend)
- [ ] Terminal open at the project root, venv activated, ready to run `pytest`
      live
- [ ] IDE open with the backend folder tree visible

## Demo sequence (in order)

1. **Show Swagger (`/docs`)**
   - Expand `POST /auth/register` and `POST /auth/login` — show the
     request/response schemas auto-generated from the Pydantic models.
   - Log in with `demo@example.com` / `demo1234`, copy the `access_token`.
   - Click "Authorize" at the top of Swagger and paste the token — protected
     endpoints become testable directly from the UI from here on.

2. **Task CRUD via Swagger**
   - `GET /tasks/` with no filter — show the paginated response (`items`,
     `total`, `page`, `page_size`).
   - `GET /tasks/?status=done` — show status filtering working.
   - `POST /tasks/` — create a new task live.
   - `PATCH /tasks/{id}` — update status to `done` and mention this triggers
     the Celery background job.

3. **Switch to the frontend**
   - Log in with the same demo user.
   - Show creating a task through the form, assigning it to another user.
   - Apply a status filter on the list.
   - Mark a task as complete and show the list updating.
   - Edit and then delete a task, showing the confirmation prompt.

4. **Tests**
   - In the terminal: `pytest` — let it run and show the coverage summary at
     the end (~95%).
   - Open `tests/test_tasks.py` and walk through 1-2 cases (e.g. the due_date
     filter test, or the 404-for-nonexistent-task test) to show the tests
     cover edge cases, not just the happy path.

5. **Docker (if the panel asks)**
   - Show `docker-compose.yml` and explain the 5 services: `db`, `redis`,
     `api`, `worker`, `frontend`.
   - No need to spin everything up live again if it's already running — just
     point at the active services (`docker compose ps`).
