"""
Tests for API endpoints with mocked dependencies.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

# Import after adding to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Mock the scheduling agent."""
    with patch('backend.api.chat.scheduling_agent') as mock:
        mock.agent = MagicMock()
        mock.agent.process_message = AsyncMock(return_value={
            "response": "Test response",
            "metadata": {"used_tools": False}
        })
        yield mock


@pytest.fixture
def mock_calendly():
    """Mock Calendly service."""
    with patch('backend.api.calendly.calendly_service') as mock:
        mock.get_availability = AsyncMock()
        mock.get_next_available_dates = AsyncMock(return_value=[])
        mock.book_appointment = AsyncMock()
        mock.get_appointment = AsyncMock()
        mock.cancel_appointment = AsyncMock(return_value=True)
        mock.appointments = []
        mock.schedule = {"appointment_types": {}}
        yield mock


# ============================================================================
# Health & Root Tests
# ============================================================================

def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data
    assert "chat" in data["endpoints"]
    assert "calendly" in data["endpoints"]


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ============================================================================
# Chat API Tests
# ============================================================================

def test_chat_endpoint_success(client, mock_agent):
    """Test successful chat message."""
    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_history": []
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "session_id" in data
    assert mock_agent.agent.process_message.called


def test_chat_endpoint_with_history(client, mock_agent):
    """Test chat with conversation history."""
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    
    response = client.post("/api/chat", json={
        "message": "I need an appointment",
        "conversation_history": history
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_chat_endpoint_with_session_id(client, mock_agent):
    """Test chat with existing session ID."""
    response = client.post("/api/chat", json={
        "message": "Continue conversation",
        "conversation_history": [],
        "session_id": "test-session-123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session-123"


def test_clear_session(client):
    """Test clearing a session."""
    response = client.delete("/api/chat/test-session-123")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


# ============================================================================
# Calendly API Tests
# ============================================================================

def test_check_availability_endpoint(client, mock_calendly):
    """Test availability checking endpoint."""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    mock_calendly.get_availability = AsyncMock(return_value=MagicMock(
        date=tomorrow,
        appointment_type="consultation",
        available_slots=[
            MagicMock(start_time="09:00", end_time="09:30", available=True)
        ],
        total_available=1
    ))
    
    response = client.get(
        f"/api/calendly/availability?date={tomorrow}&appointment_type=consultation"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert "available_slots" in data


def test_get_next_available_dates(client, mock_calendly):
    """Test getting next available dates."""
    mock_calendly.get_next_available_dates = AsyncMock(return_value=[
        {
            "date": "2025-11-27",
            "day_name": "Wednesday",
            "total_slots": 5
        }
    ])
    
    response = client.get(
        "/api/calendly/availability/next-dates",
        params={"appointment_type": "consultation", "days": 7}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "available_dates" in data


def test_get_appointment_by_confirmation(client, mock_calendly):
    """Test getting appointment by confirmation code."""
    mock_calendly.appointments = [{
        "booking_id": "APPT-TEST-001",
        "confirmation_code": "ABC123",
        "status": "confirmed"
    }]
    
    response = client.get("/api/calendly/appointment/confirmation/ABC123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["appointment"]["confirmation_code"] == "ABC123"


def test_cancel_appointment_endpoint(client, mock_calendly):
    """Test appointment cancellation endpoint."""
    mock_calendly.get_appointment = AsyncMock(return_value={
        "booking_id": "APPT-TEST-001",
        "status": "confirmed"
    })
    mock_calendly.appointments = [{
        "booking_id": "APPT-TEST-001",
        "status": "confirmed"
    }]
    mock_calendly._save_appointments = MagicMock()
    
    response = client.delete("/api/calendly/cancel/APPT-TEST-001")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_reschedule_appointment_endpoint(client, mock_calendly):
    """Test appointment rescheduling endpoint."""
    mock_calendly.get_appointment = AsyncMock(return_value={
        "booking_id": "APPT-TEST-001",
        "appointment_type": "consultation",
        "status": "confirmed"
    })
    mock_calendly._is_slot_available = MagicMock(return_value=True)
    mock_calendly._add_minutes_to_time = MagicMock(return_value="11:00")
    mock_calendly.schedule = {
        "appointment_types": {
            "consultation": {
                "duration": 30,
                "slots_required": 2
            }
        }
    }
    mock_calendly.appointments = [{
        "booking_id": "APPT-TEST-001",
        "date": "2025-11-27",
        "start_time": "10:00"
    }]
    mock_calendly._save_appointments = MagicMock()
    
    response = client.post(
        "/api/calendly/reschedule/APPT-TEST-001",
        params={"new_date": "2025-11-28", "new_time": "10:00"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ============================================================================
# Appointments API Tests
# ============================================================================

def test_list_appointments(client, mock_calendly):
    """Test listing all appointments."""
    mock_calendly.appointments = [
        {
            "booking_id": "APPT-001",
            "status": "confirmed",
            "date": "2025-11-27"
        }
    ]
    
    response = client.get("/api/appointments")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "appointments" in data
    assert data["count"] >= 0


def test_get_appointments_summary(client, mock_calendly):
    """Test getting appointments summary."""
    mock_calendly.appointments = [
        {
            "booking_id": "APPT-001",
            "status": "confirmed",
            "appointment_type": "consultation",
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        }
    ]
    
    response = client.get("/api/appointments/stats/summary")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_appointments" in data
    assert "by_status" in data


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_appointment_not_found(client, mock_calendly):
    """Test getting non-existent appointment."""
    mock_calendly.appointments = []
    
    response = client.get("/api/calendly/appointment/confirmation/INVALID")
    
    assert response.status_code == 404


def test_cancel_already_cancelled(client, mock_calendly):
    """Test cancelling already cancelled appointment."""
    mock_calendly.get_appointment = AsyncMock(return_value={
        "booking_id": "APPT-TEST-001",
        "status": "cancelled"
    })
    
    response = client.delete("/api/calendly/cancel/APPT-TEST-001")
    
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

