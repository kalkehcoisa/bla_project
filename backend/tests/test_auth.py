def test_register_new_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "full_name": "New User", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client, registered_user):
    response = client.post("/api/v1/auth/register", json=registered_user)
    assert response.status_code == 400


def test_login_success(client, registered_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_fails(client, registered_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": registered_user["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
