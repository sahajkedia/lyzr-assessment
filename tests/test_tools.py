"""
Tests for booking and availability tools with mocked dependencies.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from backend.tools import availability_tool, booking_tool
from backend.models.schemas import AvailabilityRequest, BookingRequest, PatientInfo


# ============================================================================
# Availability Tool Tests
# ============================================================================

@pytest.mark.asyncio
async def test_check_availability_success():
    """Test checking availability with mocked Calendly API."""
    with patch('backend.tools.availability_tool.calendly_api') as mock_api:
        # Mock the API response
        tomorrow = datetime.now() + timedelta(days=1)
        mock_api.get_availability = AsyncMock(return_value=MagicMock(
            date=tomorrow.strftime("%Y-%m-%d"),
            appointment_type="consultation",
            available_slots=[
                MagicMock(start_time="09:00", end_time="09:30", available=True),
                MagicMock(start_time="10:00", end_time="10:30", available=True)
            ],
            total_available=2
        ))
        
        result = await availability_tool.check_availability(
            date=tomorrow.strftime("%Y-%m-%d"),
            appointment_type="consultation"
        )
        
        assert result["success"] is True
        assert "available_slots" in result
        assert len(result["available_slots"]) >= 2


@pytest.mark.asyncio
async def test_check_availability_no_slots():
    """Test handling when no slots are available."""
    with patch('backend.tools.availability_tool.calendly_api') as mock_api:
        mock_api.get_availability = AsyncMock(return_value=MagicMock(
            date="2025-11-27",
            appointment_type="consultation",
            available_slots=[],
            total_available=0
        ))
        
        result = await availability_tool.check_availability(
            date="2025-11-27",
            appointment_type="consultation"
        )
        
        assert result["success"] is True
        assert result["available_slots"] == []


@pytest.mark.asyncio
async def test_get_next_available_slots():
    """Test getting next available slots across multiple days."""
    with patch('backend.tools.availability_tool.calendly_api') as mock_api:
        mock_api.get_next_available_dates = AsyncMock(return_value=[
            {
                "date": "2025-11-27",
                "day_name": "Wednesday",
                "total_slots": 5,
                "sample_slots": [
                    {"start_time": "09:00", "end_time": "09:30"}
                ]
            }
        ])
        
        result = await availability_tool.get_next_available_slots(
            appointment_type="consultation",
            days_ahead=7
        )
        
        assert result["success"] is True
        assert len(result["available_dates"]) >= 1


# ============================================================================
# Booking Tool Tests
# ============================================================================

@pytest.mark.asyncio
async def test_book_appointment_success():
    """Test successful appointment booking."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        mock_api.book_appointment = AsyncMock(return_value=MagicMock(
            booking_id="APPT-202511-0001",
            status="confirmed",
            confirmation_code="ABC123",
            details={
                "appointment_type": "consultation",
                "date": "2025-11-27",
                "start_time": "14:00",
                "patient": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "555-1234"
                }
            }
        ))
        
        result = await booking_tool.book_appointment(
            appointment_type="consultation",
            date="2025-11-27",
            start_time="14:00",
            patient_name="John Doe",
            patient_email="john@example.com",
            patient_phone="555-1234",
            reason="General checkup"
        )
        
        assert result["success"] is True
        assert result["booking_id"] == "APPT-202511-0001"
        assert result["confirmation_code"] == "ABC123"
        assert result["status"] == "confirmed"


@pytest.mark.asyncio
async def test_book_appointment_slot_taken():
    """Test booking when slot is already taken."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        mock_api.book_appointment = AsyncMock(
            side_effect=ValueError("The selected time slot is no longer available")
        )
        
        result = await booking_tool.book_appointment(
            appointment_type="consultation",
            date="2025-11-27",
            start_time="14:00",
            patient_name="John Doe",
            patient_email="john@example.com",
            patient_phone="555-1234",
            reason="General checkup"
        )
        
        assert result["success"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_cancel_appointment_success():
    """Test successful appointment cancellation."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        mock_api.cancel_appointment = AsyncMock(return_value=True)
        
        result = await booking_tool.cancel_appointment(
            booking_id="APPT-202511-0001"
        )
        
        assert result["success"] is True
        assert result["message"] == "Appointment cancelled successfully"


@pytest.mark.asyncio
async def test_cancel_appointment_not_found():
    """Test cancelling non-existent appointment."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        mock_api.cancel_appointment = AsyncMock(return_value=False)
        
        result = await booking_tool.cancel_appointment(
            booking_id="APPT-INVALID"
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_reschedule_appointment_success():
    """Test successful appointment rescheduling."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        # Mock getting existing appointment
        mock_api.get_appointment = AsyncMock(return_value={
            "booking_id": "APPT-202511-0001",
            "appointment_type": "consultation",
            "date": "2025-11-27",
            "start_time": "14:00",
            "status": "confirmed"
        })
        
        # Mock availability check
        mock_api._is_slot_available = MagicMock(return_value=True)
        mock_api._add_minutes_to_time = MagicMock(return_value="15:00")
        mock_api.schedule = {
            "appointment_types": {
                "consultation": {
                    "duration": 30,
                    "slots_required": 2
                }
            }
        }
        
        # Mock the appointments list and save
        mock_api.appointments = [{
            "booking_id": "APPT-202511-0001",
            "appointment_type": "consultation",
            "date": "2025-11-27",
            "start_time": "14:00",
            "end_time": "14:30",
            "status": "confirmed"
        }]
        mock_api._save_appointments = MagicMock()
        
        result = await booking_tool.reschedule_appointment(
            booking_id="APPT-202511-0001",
            new_date="2025-11-28",
            new_start_time="10:00"
        )
        
        assert result["success"] is True
        assert result["new_date"] == "2025-11-28"
        assert result["new_time"] == "10:00"


@pytest.mark.asyncio
async def test_reschedule_cancelled_appointment():
    """Test rescheduling a cancelled appointment fails."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        mock_api.get_appointment = AsyncMock(return_value={
            "booking_id": "APPT-202511-0001",
            "status": "cancelled"
        })
        
        result = await booking_tool.reschedule_appointment(
            booking_id="APPT-202511-0001",
            new_date="2025-11-28",
            new_start_time="10:00"
        )
        
        assert result["success"] is False
        assert "cancelled" in result["error"].lower()


@pytest.mark.asyncio
async def test_get_appointment_by_confirmation():
    """Test retrieving appointment by confirmation code."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        mock_api.appointments = [{
            "booking_id": "APPT-202511-0001",
            "confirmation_code": "ABC123",
            "appointment_type": "consultation",
            "status": "confirmed"
        }]
        
        result = await booking_tool.get_appointment_by_confirmation(
            confirmation_code="ABC123"
        )
        
        assert result["success"] is True
        assert result["appointment"]["confirmation_code"] == "ABC123"


@pytest.mark.asyncio
async def test_get_appointment_by_confirmation_not_found():
    """Test retrieving non-existent appointment by confirmation code."""
    with patch('backend.tools.booking_tool.calendly_api') as mock_api:
        mock_api.appointments = []
        
        result = await booking_tool.get_appointment_by_confirmation(
            confirmation_code="INVALID"
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()


# ============================================================================
# Tool Definition Tests
# ============================================================================

def test_availability_tools_structure():
    """Test that availability tools are properly structured."""
    assert len(availability_tool.AVAILABILITY_TOOLS) > 0
    
    for tool in availability_tool.AVAILABILITY_TOOLS:
        assert "type" in tool
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]


def test_booking_tools_structure():
    """Test that booking tools are properly structured."""
    assert len(booking_tool.BOOKING_TOOLS) > 0
    
    for tool in booking_tool.BOOKING_TOOLS:
        assert "type" in tool
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]
    
    # Check specific tools exist
    tool_names = [t["function"]["name"] for t in booking_tool.BOOKING_TOOLS]
    assert "book_appointment" in tool_names
    assert "cancel_appointment" in tool_names
    assert "reschedule_appointment" in tool_names
    assert "get_appointment_by_confirmation" in tool_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

