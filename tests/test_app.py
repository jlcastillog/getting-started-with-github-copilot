"""Tests for the Mergington High School Activities API."""

from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities_returns_all_activities():
    """Test that GET /activities returns all available activities."""
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Art Club",
        "Drama Club",
        "Science Club",
        "Debate Team",
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    for activity_name in expected_activities:
        assert activity_name in activities
        assert "description" in activities[activity_name]
        assert "schedule" in activities[activity_name]
        assert "max_participants" in activities[activity_name]
        assert "participants" in activities[activity_name]


def test_signup_for_activity_adds_participant():
    """Test that signing up a new participant adds them to the activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "test.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]

    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_error():
    """Test that signing up a duplicate participant returns a 400 error."""
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_remove_participant_from_activity():
    """Test that removing a participant deletes them from the activity."""
    # Arrange
    activity_name = "Gym Class"
    email = "new.student@mergington.edu"

    # First, sign up the participant
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]

    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    """Test that removing a non-existent participant returns a 404 error."""
    # Arrange
    activity_name = "Art Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"]
