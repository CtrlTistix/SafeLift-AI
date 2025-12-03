"""
Integration tests for Events API.
"""
import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_event_without_auth(client):
    """Test creating event without authentication fails."""
    response = client.post(
        "/api/events",
        json={
            "type": "person_near_forklift",
            "severity": 4,
            "source": "camera_1",
            "metadata": {}
        }
    )
    assert response.status_code == 403  # Forbidden without auth


def test_create_event_with_auth(client, auth_headers):
    """Test creating event with authentication."""
    response = client.post(
        "/api/events",
        json={
            "type": "person_near_forklift",
            "severity": 4,
            "source": "camera_1",
            "metadata": {"distance": 120.0}
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "person_near_forklift"
    assert data["severity"] == 4


def test_get_events(client, auth_headers):
    """Test getting events list."""
    # Create an event first
    client.post(
        "/api/events",
        json={
            "type": "test_event",
            "severity": 3,
            "source": "test_source",
            "metadata": {}
        },
        headers=auth_headers
    )
    
    # Get events
    response = client.get("/api/events", headers=auth_headers)
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) > 0


def test_get_critical_events(client, auth_headers):
    """Test getting critical events."""
    # Create a critical event
    client.post(
        "/api/events",
        json={
            "type": "critical_event",
            "severity": 5,
            "source": "camera_1",
            "metadata": {}
        },
        headers=auth_headers
    )
    
    # Get critical events
    response = client.get("/api/events/critical", headers=auth_headers)
    assert response.status_code == 200
    events = response.json()
    assert all(event["severity"] >= 4 for event in events)


def test_create_event_invalid_severity(client, auth_headers):
    """Test creating event with invalid severity."""
    response = client.post(
        "/api/events",
        json={
            "type": "test_event",
            "severity": 10,  # Invalid severity
            "source": "test_source",
            "metadata": {}
        },
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error
