"""
Pytest configuration and fixtures for the Mergington High School API tests.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path


@pytest.fixture
def app():
    """Create a FastAPI app instance for testing with isolated data."""
    # Create a new FastAPI app
    test_app = FastAPI(
        title="Mergington High School API (Test)",
        description="API for viewing and signing up for extracurricular activities"
    )
    
    # Test data - isolated per test
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 1,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        },
    }
    
    @test_app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")
    
    @test_app.get("/activities")
    def get_activities():
        return test_activities
    
    @test_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        from fastapi import HTTPException
        
        # Validate activity exists
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        # Get the specific activity
        activity = test_activities[activity_name]
        
        # Validate student is not already signed up
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")
        
        # Check if activity is at capacity
        if len(activity["participants"]) >= activity["max_participants"]:
            raise HTTPException(status_code=400, detail="Activity is at maximum capacity")
        
        # Add student
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}
    
    @test_app.delete("/activities/{activity_name}/participants/{email}")
    def remove_participant(activity_name: str, email: str):
        """Remove a participant from an activity"""
        from fastapi import HTTPException
        
        # Validate activity exists
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        # Get the specific activity
        activity = test_activities[activity_name]
        
        # Check if participant exists
        if email not in activity["participants"]:
            raise HTTPException(status_code=404, detail="Participant not found in this activity")
        
        # Remove participant
        activity["participants"].remove(email)
        return {"message": f"Removed {email} from {activity_name}"}
    
    return test_app


@pytest.fixture
def client(app):
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)
