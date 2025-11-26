"""
Pytest configuration and fixtures for testing.
Provides mocked services so tests run without external dependencies.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.schemas import ChatMessage


# ============================================================================
# Mock LLM Responses
# ============================================================================

MOCK_LLM_RESPONSES = {
    "greeting": {
        "content": "Hello! I'm Meera, your HealthCare Plus virtual assistant. I'm here to help you schedule appointments and answer any questions you might have about our clinic. What brings you in today?",
        "tool_calls": []
    },
    "ask_reason": {
        "content": "I'd be happy to help you schedule an appointment. Could you tell me the reason for your visit?",
        "tool_calls": []
    },
    "suggest_slots": {
        "content": "",
        "tool_calls": [{
            "id": "call_123",
            "name": "check_availability",
            "arguments": {
                "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "appointment_type": "consultation"
            }
        }]
    },
    "confirm_booking": {
        "content": "",
        "tool_calls": [{
            "id": "call_456",
            "name": "book_appointment",
            "arguments": {
                "appointment_type": "consultation",
                "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "start_time": "14:00",
                "patient_name": "John Doe",
                "patient_email": "john@example.com",
                "patient_phone": "555-123-4567",
                "reason": "General checkup"
            }
        }]
    },
    "booking_success": {
        "content": "Perfect! Your appointment has been successfully booked.\n\n**Type of Appointment:** General Consultation\n**Date and Time:** Tomorrow at 2:00 PM\n**Patient Name:** John Doe\n**Phone Number:** 555-123-4567\n**Email Address:** john@example.com\n**Confirmation Code:** ABC123\n**Booking ID:** APPT-202511-0001",
        "tool_calls": []
    },
    "faq_insurance": {
        "content": "We accept most major insurance plans including Blue Cross Blue Shield, Aetna, Cigna, UnitedHealthcare, and Medicare. Please bring your insurance card to your appointment.",
        "tool_calls": []
    },
    "faq_parking": {
        "content": "We have free parking available in our building's parking garage. The entrance is on Medical Center Drive. You can also find street parking nearby.",
        "tool_calls": []
    },
    "faq_hours": {
        "content": "Our clinic is open Monday through Friday from 9:00 AM to 5:00 PM. We're closed on weekends and major holidays.",
        "tool_calls": []
    },
    "cancel_request": {
        "content": "",
        "tool_calls": [{
            "id": "call_789",
            "name": "get_appointment_by_confirmation",
            "arguments": {
                "confirmation_code": "ABC123"
            }
        }]
    },
    "cancel_confirm": {
        "content": "",
        "tool_calls": [{
            "id": "call_012",
            "name": "cancel_appointment",
            "arguments": {
                "booking_id": "APPT-202511-0001"
            }
        }]
    },
    "cancel_success": {
        "content": "Your appointment has been cancelled successfully. If you need to schedule a new appointment in the future, I'm here to help!",
        "tool_calls": []
    }
}


# ============================================================================
# Mock Tool Results
# ============================================================================

MOCK_TOOL_RESULTS = {
    "check_availability": {
        "success": True,
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "appointment_type": "consultation",
        "available_slots": [
            {"start_time": "09:00", "end_time": "09:30"},
            {"start_time": "10:00", "end_time": "10:30"},
            {"start_time": "14:00", "end_time": "14:30"},
            {"start_time": "15:00", "end_time": "15:30"},
        ]
    },
    "book_appointment": {
        "success": True,
        "booking_id": "APPT-202511-0001",
        "confirmation_code": "ABC123",
        "status": "confirmed",
        "details": {
            "appointment_type": "consultation",
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "start_time": "14:00",
            "end_time": "14:30",
            "patient": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "555-123-4567"
            },
            "reason": "General checkup"
        }
    },
    "get_appointment_by_confirmation": {
        "success": True,
        "appointment": {
            "booking_id": "APPT-202511-0001",
            "confirmation_code": "ABC123",
            "appointment_type": "consultation",
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "start_time": "14:00",
            "end_time": "14:30",
            "patient": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "555-123-4567"
            },
            "reason": "General checkup",
            "status": "confirmed"
        }
    },
    "cancel_appointment": {
        "success": True,
        "message": "Appointment cancelled successfully",
        "booking_id": "APPT-202511-0001"
    },
    "reschedule_appointment": {
        "success": True,
        "message": "Appointment rescheduled successfully",
        "booking_id": "APPT-202511-0001",
        "old_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "old_time": "14:00",
        "new_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "new_time": "10:00"
    }
}


# ============================================================================
# Mock LLM Client
# ============================================================================

class MockLLMResponse:
    """Mock LLM response object."""
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class MockLLMClient:
    """Mock LLM client that returns predefined responses."""
    
    def __init__(self, response_key="greeting"):
        self.response_key = response_key
        self.call_count = 0
    
    async def chat_completions_create(self, **kwargs):
        """Mock chat completions creation."""
        self.call_count += 1
        
        # Determine response based on message content
        messages = kwargs.get("messages", [])
        last_message = messages[-1]["content"] if messages else ""
        
        # Simple pattern matching to return appropriate mock response
        if "hello" in last_message.lower() or "hi" in last_message.lower():
            response_data = MOCK_LLM_RESPONSES["greeting"]
        elif "insurance" in last_message.lower():
            response_data = MOCK_LLM_RESPONSES["faq_insurance"]
        elif "park" in last_message.lower():
            response_data = MOCK_LLM_RESPONSES["faq_parking"]
        elif "hours" in last_message.lower() or "open" in last_message.lower():
            response_data = MOCK_LLM_RESPONSES["faq_hours"]
        elif "cancel" in last_message.lower():
            if "ABC123" in last_message or "confirmation" in last_message:
                response_data = MOCK_LLM_RESPONSES["cancel_confirm"]
            else:
                response_data = MOCK_LLM_RESPONSES["cancel_request"]
        elif "book" in last_message.lower() or "appointment" in last_message.lower():
            # Check if we have patient details
            if "john" in last_message.lower() or "555" in last_message:
                response_data = MOCK_LLM_RESPONSES["confirm_booking"]
            else:
                response_data = MOCK_LLM_RESPONSES["ask_reason"]
        else:
            response_data = MOCK_LLM_RESPONSES.get(self.response_key, MOCK_LLM_RESPONSES["greeting"])
        
        return {
            "content": response_data["content"],
            "tool_calls": response_data["tool_calls"]
        }


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_client():
    """Provide a mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock:
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content="Test response",
                    tool_calls=None
                )
            )]
        ))
        mock.return_value = client
        yield mock


@pytest.fixture
def mock_tools():
    """Mock all tool functions."""
    with patch('backend.tools.availability_tool.check_availability') as mock_avail, \
         patch('backend.tools.booking_tool.book_appointment') as mock_book, \
         patch('backend.tools.booking_tool.cancel_appointment') as mock_cancel, \
         patch('backend.tools.booking_tool.reschedule_appointment') as mock_reschedule, \
         patch('backend.tools.booking_tool.get_appointment_by_confirmation') as mock_get:
        
        mock_avail.return_value = MOCK_TOOL_RESULTS["check_availability"]
        mock_book.return_value = MOCK_TOOL_RESULTS["book_appointment"]
        mock_cancel.return_value = MOCK_TOOL_RESULTS["cancel_appointment"]
        mock_reschedule.return_value = MOCK_TOOL_RESULTS["reschedule_appointment"]
        mock_get.return_value = MOCK_TOOL_RESULTS["get_appointment_by_confirmation"]
        
        yield {
            "check_availability": mock_avail,
            "book_appointment": mock_book,
            "cancel_appointment": mock_cancel,
            "reschedule_appointment": mock_reschedule,
            "get_appointment_by_confirmation": mock_get
        }


@pytest.fixture
def mock_rag():
    """Mock RAG system."""
    with patch('backend.rag.faq_rag.faq_rag') as mock:
        mock.answer_question = MagicMock(return_value={
            "answer": "Mock FAQ answer",
            "context": "Mock FAQ context",
            "confidence": 0.95
        })
        yield mock


@pytest.fixture
def mock_agent_dependencies(mock_openai_client, mock_tools, mock_rag):
    """Mock all agent dependencies."""
    return {
        "llm_client": mock_openai_client,
        "tools": mock_tools,
        "rag": mock_rag
    }


@pytest.fixture
def sample_appointment():
    """Sample appointment data for testing."""
    return {
        "booking_id": "APPT-202511-0001",
        "confirmation_code": "ABC123",
        "appointment_type": "consultation",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "start_time": "14:00",
        "end_time": "14:30",
        "patient": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-123-4567"
        },
        "reason": "General checkup",
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_conversation():
    """Sample conversation history."""
    return [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hello! How can I help you?"),
        ChatMessage(role="user", content="I need an appointment"),
        ChatMessage(role="assistant", content="I'd be happy to help! What brings you in?")
    ]


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_llm_response(content, tool_calls=None):
    """Create a mock LLM response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = content
    mock_response.choices[0].message.tool_calls = tool_calls
    return mock_response


def create_mock_tool_call(tool_id, function_name, arguments):
    """Create a mock tool call."""
    mock_call = MagicMock()
    mock_call.id = tool_id
    mock_call.function = MagicMock()
    mock_call.function.name = function_name
    mock_call.function.arguments = str(arguments) if isinstance(arguments, dict) else arguments
    return mock_call

