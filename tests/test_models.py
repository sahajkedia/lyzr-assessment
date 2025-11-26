"""
Tests for data models and schemas.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

from backend.models.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    PatientInfo,
    TimeSlot,
    AvailabilityRequest,
    AvailabilityResponse,
    BookingRequest,
    BookingResponse,
    AppointmentDetails
)


# ============================================================================
# Chat Models Tests
# ============================================================================

def test_chat_message_creation():
    """Test creating a chat message."""
    message = ChatMessage(role="user", content="Hello")
    
    assert message.role == "user"
    assert message.content == "Hello"


def test_chat_message_validation():
    """Test chat message validation."""
    # Valid roles - schemas accept any string role
    ChatMessage(role="user", content="Test")
    ChatMessage(role="assistant", content="Test")
    ChatMessage(role="system", content="Test")
    
    # Empty content should still work (Pydantic allows it)
    message = ChatMessage(role="user", content="")
    assert message.content == ""


def test_chat_request_creation():
    """Test creating a chat request."""
    request = ChatRequest(
        message="I need an appointment",
        conversation_history=[
            ChatMessage(role="user", content="Hello")
        ],
        session_id="test-123"
    )
    
    assert request.message == "I need an appointment"
    assert len(request.conversation_history) == 1
    assert request.session_id == "test-123"


def test_chat_request_without_session():
    """Test chat request without session ID."""
    request = ChatRequest(
        message="Hello",
        conversation_history=[]
    )
    
    assert request.session_id is None


def test_chat_response_creation():
    """Test creating a chat response."""
    response = ChatResponse(
        message="Hello! How can I help?",
        conversation_history=[],
        session_id="test-123"
    )
    
    assert response.message == "Hello! How can I help?"
    assert response.session_id == "test-123"


# ============================================================================
# Patient & Appointment Models Tests
# ============================================================================

def test_patient_info_creation():
    """Test creating patient info."""
    patient = PatientInfo(
        name="John Doe",
        email="john@example.com",
        phone="555-123-4567"
    )
    
    assert patient.name == "John Doe"
    assert patient.email == "john@example.com"
    assert patient.phone == "555-123-4567"


def test_patient_info_email_validation():
    """Test patient email validation."""
    # Valid email
    PatientInfo(name="Test", email="test@example.com", phone="555-0000")
    
    # Invalid email should raise error
    with pytest.raises(ValidationError):
        PatientInfo(name="Test", email="invalid-email", phone="555-0000")


def test_time_slot_creation():
    """Test creating a time slot."""
    slot = TimeSlot(
        start_time="09:00",
        end_time="09:30",
        available=True
    )
    
    assert slot.start_time == "09:00"
    assert slot.end_time == "09:30"
    assert slot.available is True


# ============================================================================
# Availability Models Tests
# ============================================================================

def test_availability_request_creation():
    """Test creating an availability request."""
    request = AvailabilityRequest(
        date="2025-11-27",
        appointment_type="consultation"
    )
    
    assert request.date == "2025-11-27"
    assert request.appointment_type == "consultation"


def test_availability_request_validation():
    """Test availability request validation."""
    # Valid appointment types - schemas accept any string
    for appt_type in ["consultation", "followup", "physical", "specialist"]:
        request = AvailabilityRequest(date="2025-11-27", appointment_type=appt_type)
        assert request.appointment_type == appt_type
    
    # Schemas accept any string for appointment_type
    request = AvailabilityRequest(date="2025-11-27", appointment_type="custom")
    assert request.appointment_type == "custom"


def test_availability_response_creation():
    """Test creating an availability response."""
    response = AvailabilityResponse(
        date="2025-11-27",
        appointment_type="consultation",
        available_slots=[
            TimeSlot(start_time="09:00", end_time="09:30", available=True)
        ],
        total_available=1
    )
    
    assert response.date == "2025-11-27"
    assert len(response.available_slots) == 1
    assert response.total_available == 1


# ============================================================================
# Booking Models Tests
# ============================================================================

def test_booking_request_creation():
    """Test creating a booking request."""
    patient = PatientInfo(
        name="John Doe",
        email="john@example.com",
        phone="555-1234"
    )
    
    request = BookingRequest(
        appointment_type="consultation",
        date="2025-11-27",
        start_time="14:00",
        patient=patient,
        reason="General checkup"
    )
    
    assert request.appointment_type == "consultation"
    assert request.date == "2025-11-27"
    assert request.start_time == "14:00"
    assert request.patient.name == "John Doe"
    assert request.reason == "General checkup"


def test_booking_request_validation():
    """Test booking request validation."""
    patient = PatientInfo(
        name="Test",
        email="test@test.com",
        phone="555-0000"
    )
    
    # Valid request
    request = BookingRequest(
        appointment_type="consultation",
        date="2025-11-27",
        start_time="14:00",
        patient=patient,
        reason="Test"
    )
    assert request.appointment_type == "consultation"
    
    # Missing required field should raise error
    with pytest.raises(ValidationError):
        BookingRequest(
            appointment_type="consultation",
            date="2025-11-27",
            # Missing start_time
            patient=patient,
            reason="Test"
        )


def test_booking_response_creation():
    """Test creating a booking response."""
    response = BookingResponse(
        booking_id="APPT-202511-0001",
        status="confirmed",
        confirmation_code="ABC123",
        details={"appointment_type": "consultation"}
    )
    
    assert response.booking_id == "APPT-202511-0001"
    assert response.status == "confirmed"
    assert response.confirmation_code == "ABC123"
    assert "appointment_type" in response.details


def test_appointment_details_creation():
    """Test creating appointment details."""
    patient = PatientInfo(
        name="John Doe",
        email="john@example.com",
        phone="555-1234"
    )
    
    details = AppointmentDetails(
        booking_id="APPT-202511-0001",
        appointment_type="consultation",
        date="2025-11-27",
        start_time="14:00",
        end_time="14:30",
        patient=patient,
        reason="General checkup",
        confirmation_code="ABC123"
    )
    
    assert details.appointment_type == "consultation"
    assert details.patient.name == "John Doe"
    assert details.booking_id == "APPT-202511-0001"
    assert details.status == "confirmed"


# ============================================================================
# Serialization Tests
# ============================================================================

def test_chat_message_serialization():
    """Test chat message JSON serialization."""
    message = ChatMessage(role="user", content="Test message")
    
    json_data = message.model_dump()
    
    assert json_data["role"] == "user"
    assert json_data["content"] == "Test message"


def test_booking_request_serialization():
    """Test booking request JSON serialization."""
    patient = PatientInfo(
        name="John Doe",
        email="john@example.com",
        phone="555-1234"
    )
    
    request = BookingRequest(
        appointment_type="consultation",
        date="2025-11-27",
        start_time="14:00",
        patient=patient,
        reason="Test"
    )
    
    json_data = request.model_dump()
    
    assert json_data["appointment_type"] == "consultation"
    assert json_data["patient"]["name"] == "John Doe"


def test_deserialization_from_dict():
    """Test creating models from dictionaries."""
    data = {
        "role": "user",
        "content": "Hello"
    }
    
    message = ChatMessage(**data)
    
    assert message.role == "user"
    assert message.content == "Hello"


# ============================================================================
# Edge Cases Tests
# ============================================================================

def test_empty_conversation_history():
    """Test handling empty conversation history."""
    request = ChatRequest(
        message="Hello",
        conversation_history=[]
    )
    
    assert len(request.conversation_history) == 0


def test_long_message_content():
    """Test handling long message content."""
    long_content = "A" * 10000
    
    message = ChatMessage(role="user", content=long_content)
    
    assert len(message.content) == 10000


def test_special_characters_in_content():
    """Test handling special characters."""
    special_content = "Hello! 你好 🎉 @#$%^&*()"
    
    message = ChatMessage(role="user", content=special_content)
    
    assert message.content == special_content


def test_patient_info_with_various_phone_formats():
    """Test patient info with different phone number formats."""
    formats = [
        "555-123-4567",
        "(555) 123-4567",
        "555.123.4567",
        "5551234567",
        "+1-555-123-4567"
    ]
    
    for phone in formats:
        patient = PatientInfo(
            name="Test",
            email="test@test.com",
            phone=phone
        )
        assert patient.phone == phone


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

