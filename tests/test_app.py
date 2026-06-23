"""
Tests for Mergington High School Activities API
Using Arrange-Act-Assert (AAA) testing pattern
"""
import pytest


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
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
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        for activity in expected_activities:
            assert activity in data

    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, details in activities.items():
            for field in required_fields:
                assert field in details, f"Missing '{field}' in {activity_name}"
            assert isinstance(details["participants"], list)
            assert isinstance(details["max_participants"], int)


class TestSignup:
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup returns 400 error"""
        # Arrange
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"

        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act - Try to signup again with same email
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds participant to activity list"""
        # Arrange
        activity_name = "Soccer Team"
        email = "participant@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email in activities[activity_name]["participants"]


class TestUnregister:
    def test_unregister_success(self, client):
        """Test successful unregistration from activity"""
        # Arrange
        activity_name = "Basketball Club"
        email = "unregister_test@mergington.edu"

        # First signup a participant
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregistering non-existent participant returns 404"""
        # Arrange
        activity_name = "Chess Club"
        email = "notaparticipant@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_removes_participant_from_activity(self, client):
        """Test that unregister actually removes participant from list"""
        # Arrange
        activity_name = "Art Club"
        email = "removal_test@mergington.edu"

        # Signup a participant
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Verify participant is registered
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]

        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert - Verify participant is removed
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]

    def test_unregister_then_signup_again_succeeds(self, client):
        """Test that a student can signup after unregistering"""
        # Arrange
        activity_name = "Drama Club"
        email = "rejoin_test@mergington.edu"

        # Signup
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Act - Try to signup again
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
