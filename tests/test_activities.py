"""
Comprehensive test suite for Mergington High School API endpoints.
Tests cover all endpoints, edge cases, and error scenarios.
"""

import pytest


class TestGetActivities:
    """Test the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Verify activity structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_returns_correct_data_types(self, client):
        """Test that activity data types are correct."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Programming Class"]
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Programming%20Class/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Programming Class" in data["message"]
        
        # Verify student was added
        activities = client.get("/activities").json()
        assert "newstudent@mergington.edu" in activities["Programming Class"]["participants"]
    
    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up a student twice returns 400 error."""
        email = "newstudent@mergington.edu"
        activity = "Programming%20Class"
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404 error."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_at_capacity_returns_400(self, client):
        """Test that signup fails when activity is at maximum capacity."""
        activity = "Programming%20Class"  # max_participants: 1
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email=student1@mergington.edu")
        assert response1.status_code == 200
        
        # Second signup - should fail because activity is at capacity (max is 1)
        response2 = client.post(f"/activities/{activity}/signup?email=student2@mergington.edu")
        assert response2.status_code == 400
        data = response2.json()
        assert "capacity" in data["detail"].lower()
    
    def test_signup_with_url_encoded_email(self, client):
        """Test signup with special characters in email."""
        response = client.post(
            "/activities/Gym%20Class/signup?email=john%2Bdoe%40mergington.edu"
        )
        
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert "john+doe@mergington.edu" in activities["Gym Class"]["participants"]
    
    def test_signup_multiple_students_different_activities(self, client):
        """Test that multiple students can sign up for different activities."""
        # Student 1 signs up for Programming Class
        response1 = client.post(
            "/activities/Programming%20Class/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Student 2 signs up for Gym Class
        response2 = client.post(
            "/activities/Gym%20Class/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities = client.get("/activities").json()
        assert "student1@mergington.edu" in activities["Programming Class"]["participants"]
        assert "student2@mergington.edu" in activities["Gym Class"]["participants"]


class TestRemoveParticipant:
    """Test the DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_remove_participant_successful(self, client):
        """Test successful removal of a participant."""
        # Sign up first
        client.post("/activities/Chess%20Club/signup?email=student@mergington.edu")
        
        # Remove participant
        response = client.delete(
            "/activities/Chess%20Club/participants/student%40mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert "student@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing non-existent participant returns 404 error."""
        response = client.delete(
            "/activities/Gym%20Class/participants/nonexistent%40mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]
    
    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from non-existent activity returns 404 error."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/participants/student%40mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_remove_existing_participant(self, client):
        """Test removing a participant that was pre-populated in test data."""
        # Chess Club has michael@mergington.edu in test data
        response = client.delete(
            "/activities/Chess%20Club/participants/michael%40mergington.edu"
        )
        
        assert response.status_code == 200
        
        # Verify removal
        activities = client.get("/activities").json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_remove_and_signup_again(self, client):
        """Test that a student can be removed and sign up again."""
        email_encoded = "student%40mergington.edu"
        email_decoded = "student@mergington.edu"
        activity_encoded = "Programming%20Class"
        activity_decoded = "Programming Class"
        
        # Sign up
        response1 = client.post(f"/activities/{activity_encoded}/signup?email={email_encoded}")
        assert response1.status_code == 200
        
        # Remove
        response2 = client.delete(f"/activities/{activity_encoded}/participants/{email_encoded}")
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(f"/activities/{activity_encoded}/signup?email={email_encoded}")
        assert response3.status_code == 200
        
        # Verify final state
        activities = client.get("/activities").json()
        assert email_decoded in activities[activity_decoded]["participants"]


class TestCapacityManagement:
    """Test edge cases related to activity capacity."""
    
    def test_fill_activity_to_capacity(self, client):
        """Test that activity can be filled exactly to max_participants."""
        activity = "Chess%20Club"  # max_participants: 2, has 1 participant
        
        # Add one more to reach capacity
        response = client.post(f"/activities/{activity}/signup?email=student1@mergington.edu")
        assert response.status_code == 200
        
        # Verify capacity is reached
        activities = client.get("/activities").json()
        assert len(activities["Chess Club"]["participants"]) == 2
        
        # Try to add another - should fail
        response = client.post(f"/activities/{activity}/signup?email=student2@mergington.edu")
        assert response.status_code == 400
    
    def test_multiple_removes_and_signups(self, client):
        """Test multiple removal and signup cycles."""
        activity = "Programming%20Class"
        
        # Sign up, remove, sign up different student
        for i in range(3):
            email = f"student{i}%40mergington.edu"
            
            # Sign up
            response1 = client.post(f"/activities/{activity}/signup?email={email}")
            assert response1.status_code == 200
            
            # Remove
            response2 = client.delete(f"/activities/{activity}/participants/{email}")
            assert response2.status_code == 200
