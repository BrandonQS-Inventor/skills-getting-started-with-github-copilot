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
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity_name in data
    assert data[expected_activity_name]["max_participants"] == 12
    assert isinstance(data[expected_activity_name]["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student1@mergington.edu"
    signup_url = build_activity_path(activity_name, "/signup")

    # Act
    response = client.post(signup_url, params={"email": email})
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert response_data["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    signup_url = build_activity_path(activity_name, "/signup")

    # Act
    response = client.post(signup_url, params={"email": email})
    response_data = response.json()

    # Assert
    assert response.status_code == 400
    assert response_data["detail"] == "Student is already signed up for this activity"


def test_remove_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    remove_url = build_activity_path(activity_name, "/participants")

    # Act
    response = client.delete(remove_url, params={"email": email})
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert response_data["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "nobody@mergington.edu"
    remove_url = build_activity_path(activity_name, "/participants")

    # Act
    response = client.delete(remove_url, params={"email": email})
    response_data = response.json()

    # Assert
    assert response.status_code == 404
    assert response_data["detail"] == "Participant not found"
