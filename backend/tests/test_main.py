def test_home_lists_endpoint_groups(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["docs"] == "/docs"
    assert "tasks" in data["endpoints"]
    assert "auth" in data["endpoints"]
