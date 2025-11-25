"""
Data models and schemas for the appointment scheduling system.
"""
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class PatientInfo(BaseModel):
    """Patient information for appointment booking."""
    name: str = Field(..., description="Patient's full name")
    email: EmailStr = Field(..., description="Patient's email address")
    phone: str = Field(..., description="Patient's phone number")


class TimeSlot(BaseModel):
    """Represents a time slot."""
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    available: bool = Field(..., description="Whether the slot is available")


class AvailabilityRequest(BaseModel):
    """Request for checking availability."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    appointment_type: str = Field(..., description="Type: consultation, followup, physical, specialist")


class AvailabilityResponse(BaseModel):
    """Response with available slots."""
    date: str
    appointment_type: str
    available_slots: List[TimeSlot]
    total_available: int


class BookingRequest(BaseModel):
    """Request to book an appointment."""
    appointment_type: str = Field(..., description="Type: consultation, followup, physical, specialist")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    start_time: str = Field(..., description="Start time in HH:MM format")
    patient: PatientInfo
    reason: str = Field(..., description="Reason for visit")


class BookingResponse(BaseModel):
    """Response after booking."""
    booking_id: str
    status: str
    confirmation_code: str
    details: Dict[str, Any]


class ChatMessage(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Role: user, assistant, system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str = Field(..., description="User's message")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    message: str = Field(..., description="Assistant's response")
    conversation_history: List[ChatMessage] = Field(..., description="Updated conversation history")
    session_id: str = Field(..., description="Session ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AppointmentDetails(BaseModel):
    """Details of an appointment."""
    booking_id: str
    appointment_type: str
    date: str
    start_time: str
    end_time: str
    patient: PatientInfo
    reason: str
    confirmation_code: str
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=datetime.now)


class ConversationState(BaseModel):
    """State of the conversation."""
    session_id: str
    current_phase: str = "greeting"  # greeting, understanding, suggesting, confirming, booking, faq
    appointment_type: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    patient_info: Optional[PatientInfo] = None
    reason: Optional[str] = None
    suggested_slots: List[Dict[str, str]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)

