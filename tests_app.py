import os

os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_generate_workout():
    response = client.post(
        "/generate-workout",
        data={
            "username": "Test User",
            "user_id": "TEST001",
            "age": "20",
            "weight": "65",
            "goal": "muscle gain",
            "intensity": "medium",
        },
    )

    assert response.status_code == 200
    assert "7-Day Workout Plan" in response.text


def test_api_users():
    response = client.get("/api/users")

    assert response.status_code == 200
    assert isinstance(response.json(), list)