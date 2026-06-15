import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def build_activity_path(activity_name: str, suffix: str = "") -> str:
    return f"/activities/{quote(activity_name, safe='')}{suffix}"


def test_get_activities_returns_activity_list(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant(client):
    email = "student1@mergington.edu"
    response = client.post(build_activity_path("Chess Club", "/signup"), params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    email = "michael@mergington.edu"
    response = client.post(build_activity_path("Chess Club", "/signup"), params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant(client):
    email = "michael@mergington.edu"
    response = client.delete(build_activity_path("Chess Club", "/participants"), params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    email = "nobody@mergington.edu"
    response = client.delete(build_activity_path("Chess Club", "/participants"), params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
