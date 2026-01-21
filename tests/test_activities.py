"""Tests for the activities API endpoints"""
import pytest


def test_get_activities(client, reset_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) == 9


def test_get_activities_structure(client, reset_activities):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    data = response.json()
    activity = data["Chess Club"]
    
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity_success(client, reset_activities):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_updates_participants(client, reset_activities):
    """Test that signup actually adds participant to the list"""
    email = "newstudent@mergington.edu"
    
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()["Chess Club"]["participants"])
    
    # Sign up
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Check updated count
    response = client.get("/activities")
    updated_count = len(response.json()["Chess Club"]["participants"])
    
    assert updated_count == initial_count + 1
    assert email in response.json()["Chess Club"]["participants"]


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signup for non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_registered(client, reset_activities):
    """Test signup for activity when already registered returns 400"""
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_success(client, reset_activities):
    """Test successful unregistration from an activity"""
    response = client.post(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "michael@mergington.edu" in data["message"]
    assert "Unregistered" in data["message"]


def test_unregister_removes_participant(client, reset_activities):
    """Test that unregister actually removes participant from the list"""
    email = "michael@mergington.edu"
    
    # Verify participant is there
    response = client.get("/activities")
    assert email in response.json()["Chess Club"]["participants"]
    
    # Unregister
    client.post(f"/activities/Chess Club/unregister?email={email}")
    
    # Check participant is removed
    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_nonexistent_activity(client, reset_activities):
    """Test unregister from non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_not_registered(client, reset_activities):
    """Test unregister when not registered returns 400"""
    response = client.post(
        "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_signup_and_unregister_flow(client, reset_activities):
    """Test the full signup and unregister flow"""
    email = "flowtest@mergington.edu"
    activity = "Programming Class"
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Verify participant was added
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]
    
    # Unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify participant was removed
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]


def test_multiple_signups_same_activity(client, reset_activities):
    """Test multiple students signing up for the same activity"""
    activity = "Art Club"
    students = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
    
    for email in students:
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    # Verify all were added
    response = client.get("/activities")
    participants = response.json()[activity]["participants"]
    for email in students:
        assert email in participants
