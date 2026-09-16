"""Shared pytest fixtures for the backend test suite."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=__import__("sqlalchemy").pool.StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _setup_db():
    """Create the test database schema before each test and remove it afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Provide a database session backed by the in-memory test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_user(client):
    """Register and return a test user's credentials."""
    payload = {
        "email": "jayme@example.com",
        "full_name": "Jayme Tosi",
        "password": "supersecret",
    }
    client.post("/api/v1/auth/register", json=payload)
    return payload


@pytest.fixture
def auth_headers(client, registered_user):
    """Return authorization headers for the registered test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
