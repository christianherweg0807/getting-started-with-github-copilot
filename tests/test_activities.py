"""
Unit tests for the FastAPI activities endpoints.
Tests the core functionality of the Mergington High School Activities API.
"""
import pytest
from fastapi import status


class TestActivitiesAPI:
    """Test suite for activities API endpoints."""
    
    def test_get_activities_success(self, client):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that we have the expected number of activities
        assert len(data) == 9
        
        # Check that Chess Club exists with correct structure
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2
        
    def test_get_activities_returns_correct_data_types(self, client):
        """Test that activities endpoint returns data in correct format."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that all participants are email strings
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupEndpoint:
    """Test suite for activity signup functionality."""
    
    def test_signup_success(self, client, sample_student_email, sample_activity_name):
        """Test successful signup for an activity."""
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_student_email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert sample_student_email in data["message"]
        assert sample_activity_name in data["message"]
        
        # Verify student was added to the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert sample_student_email in activities[sample_activity_name]["participants"]
        
    def test_signup_nonexistent_activity(self, client, sample_student_email):
        """Test signup for a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": sample_student_email}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_signup_duplicate_student(self, client):
        """Test that signing up the same student twice returns 400."""
        # Use an existing student
        existing_email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Student is already signed up for this activity"
        
    def test_signup_full_activity(self, client):
        """Test signup when activity is at max capacity."""
        activity_name = "Mathletes"
        
        # First, get current participants count
        activities_response = client.get("/activities")
        activities = activities_response.json()
        current_participants = len(activities[activity_name]["participants"])
        max_participants = activities[activity_name]["max_participants"]
        
        # Fill up the remaining spots
        for i in range(current_participants, max_participants):
            email = f"student{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
            
        # Now try to add one more student (should fail)
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Activity is full"
        
    def test_signup_invalid_email_format(self, client, sample_activity_name):
        """Test signup with various email formats."""
        # Note: FastAPI doesn't validate email format by default in query params
        # This test ensures the system accepts various formats
        test_emails = [
            "valid@example.com",
            "valid.email@mergington.edu",
            "student123@school.org"
        ]
        
        for email in test_emails:
            response = client.post(
                f"/activities/{sample_activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK


class TestUnregisterEndpoint:
    """Test suite for activity unregister functionality."""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity."""
        # Use an existing participant
        existing_email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert existing_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was removed from the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert existing_email not in activities[activity_name]["participants"]
        
    def test_unregister_nonexistent_activity(self, client, sample_student_email):
        """Test unregister from a non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": sample_student_email}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_unregister_student_not_enrolled(self, client, sample_student_email, sample_activity_name):
        """Test unregister student who is not enrolled returns 400."""
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_student_email}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"


class TestRootEndpoint:
    """Test suite for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestIntegrationScenarios:
    """Integration tests covering full user workflows."""
    
    def test_complete_signup_and_unregister_workflow(self, client):
        """Test complete workflow: signup -> verify -> unregister -> verify."""
        email = "integration.test@mergington.edu"
        activity_name = "Programming Class"
        
        # Step 1: Verify student is not initially enrolled
        activities_response = client.get("/activities")
        activities = activities_response.json()
        initial_participants = activities[activity_name]["participants"].copy()
        assert email not in initial_participants
        
        # Step 2: Sign up student
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Step 3: Verify student is now enrolled
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1
        
        # Step 4: Unregister student
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Step 5: Verify student is no longer enrolled
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(initial_participants)
        
    def test_multiple_students_same_activity(self, client):
        """Test multiple students can sign up for the same activity."""
        activity_name = "Art Workshop"
        test_emails = [
            "artist1@mergington.edu",
            "artist2@mergington.edu",
            "artist3@mergington.edu"
        ]
        
        # Get initial participant count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()[activity_name]["participants"])
        
        # Sign up multiple students
        for email in test_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
            
        # Verify all students are enrolled
        activities_response = client.get("/activities")
        activities = activities_response.json()
        final_participants = activities[activity_name]["participants"]
        
        for email in test_emails:
            assert email in final_participants
            
        assert len(final_participants) == initial_count + len(test_emails)
        
    def test_student_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities."""
        email = "multi.activity@mergington.edu"
        activities_to_join = ["Chess Club", "Science Club", "Drama Club"]
        
        # Sign up for multiple activities
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
            
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for activity_name in activities_to_join:
            assert email in activities[activity_name]["participants"]