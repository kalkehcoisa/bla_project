def _create_task(client, headers, **overrides):
    """Create a task using default fields and any supplied overrides."""
    payload = {"title": "Sample task", "description": "Do the thing"}
    payload.update(overrides)
    return client.post("/api/v1/tasks/", json=payload, headers=headers)


def test_create_task(client, auth_headers):
    """Verify that a task can be created with a pending status."""
    response = _create_task(client, auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Sample task"
    assert data["status"] == "pending"


def test_list_tasks_returns_paginated_page(client, auth_headers):
    """Verify that tasks are returned in a paginated response."""
    for i in range(3):
        _create_task(client, auth_headers, title=f"Task {i}")

    response = client.get("/api/v1/tasks/?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_filter_tasks_by_status(client, auth_headers):
    """Verify that tasks can be filtered by status."""
    created = _create_task(client, auth_headers, title="To finish").json()
    client.patch(
        f"/api/v1/tasks/{created['id']}",
        json={"status": "done"},
        headers=auth_headers,
    )
    _create_task(client, auth_headers, title="Still pending")

    response = client.get("/api/v1/tasks/?status=done", headers=auth_headers)
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "To finish"


def test_filter_tasks_by_due_date(client, auth_headers):
    """Verify that tasks can be filtered by due date."""
    _create_task(client, auth_headers, title="Due soon", due_date="2026-10-01")
    _create_task(client, auth_headers, title="Due later", due_date="2026-11-01")

    response = client.get("/api/v1/tasks/?due_date=2026-10-01", headers=auth_headers)
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Due soon"


def test_update_task(client, auth_headers):
    """Verify that an existing task can be updated."""
    created = _create_task(client, auth_headers).json()
    response = client.patch(
        f"/api/v1/tasks/{created['id']}",
        json={"title": "Updated title"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


def test_complete_task(client, auth_headers):
    """Verify that a task can be marked as complete."""
    created = _create_task(client, auth_headers).json()
    response = client.post(f"/api/v1/tasks/{created['id']}/complete", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_delete_task(client, auth_headers):
    """Verify that a deleted task is no longer available."""
    created = _create_task(client, auth_headers).json()
    response = client.delete(f"/api/v1/tasks/{created['id']}", headers=auth_headers)
    assert response.status_code == 204

    follow_up = client.get(f"/api/v1/tasks/{created['id']}", headers=auth_headers)
    assert follow_up.status_code == 404


def test_get_nonexistent_task_returns_404(client, auth_headers):
    """Verify that requesting a nonexistent task returns not found."""
    response = client.get("/api/v1/tasks/9999", headers=auth_headers)
    assert response.status_code == 404


def test_task_owner_can_assign_to_other_user(client, auth_headers):
    """Verify that a task owner can assign a task to another user."""
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "assignee@example.com", "full_name": "Assignee", "password": "pass1234"},
    ).json()

    response = _create_task(client, auth_headers, assignee_id=other["id"])
    assert response.status_code == 201
    assert response.json()["assignee_id"] == other["id"]
