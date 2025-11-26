"""
Mocked tests for the scheduling agent.
These tests use mocks and don't require external API calls.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json

from backend.models.schemas import ChatMessage
from backend.agent.scheduling_agent import SchedulingAgent


# ============================================================================
# Basic Agent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent can be initialized without external services."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI'):
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        assert agent is not None
        assert agent.llm_provider == "openai"
        assert agent.model == "gpt-4-turbo"
        assert len(agent.tools) > 0
        assert "check_availability" in agent.tool_functions
        assert "book_appointment" in agent.tool_functions


@pytest.mark.asyncio
async def test_greeting_response():
    """Test agent responds to greeting without API calls."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai:
        # Mock the API response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock(
            content="Hello! I'm Meera, your HealthCare Plus virtual assistant.",
            tool_calls=None
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        result = await agent.process_message(
            user_message="Hello",
            conversation_history=[]
        )
        
        assert "response" in result
        assert len(result["response"]) > 0
        assert "metadata" in result


@pytest.mark.asyncio
async def test_system_prompt_includes_current_time():
    """Test that system prompt includes current date/time."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI'):
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        prompt = agent._get_system_prompt()
        
        assert "Current date and time:" in prompt
        assert "Meera" in prompt


# ============================================================================
# Tool Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_check_availability_tool():
    """Test availability checking tool execution."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai, \
         patch('backend.tools.availability_tool.check_availability') as mock_tool:
        
        # Mock tool response
        mock_tool.return_value = {
            "success": True,
            "date": "2025-11-27",
            "available_slots": [
                {"start_time": "09:00", "end_time": "09:30"},
                {"start_time": "10:00", "end_time": "10:30"}
            ]
        }
        
        # Mock LLM to request tool call
        mock_client = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function = MagicMock()
        mock_tool_call.function.name = "check_availability"
        mock_tool_call.function.arguments = json.dumps({
            "date": "2025-11-27",
            "appointment_type": "consultation"
        })
        
        # First call: request tool
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message = MagicMock(
            content="",
            tool_calls=[mock_tool_call]
        )
        
        # Second call: final response
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message = MagicMock(
            content="Here are the available slots for tomorrow.",
            tool_calls=None
        )
        
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[mock_response_1, mock_response_2]
        )
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        result = await agent.process_message(
            user_message="What times are available tomorrow?",
            conversation_history=[]
        )
        
        assert "response" in result
        assert mock_tool.called
        assert result["metadata"]["used_tools"] is True


@pytest.mark.asyncio
async def test_book_appointment_tool():
    """Test appointment booking tool execution."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai, \
         patch('backend.tools.booking_tool.book_appointment') as mock_book:
        
        # Mock booking response
        mock_book.return_value = {
            "success": True,
            "booking_id": "APPT-202511-0001",
            "confirmation_code": "ABC123",
            "status": "confirmed"
        }
        
        # Mock LLM to request booking
        mock_client = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_456"
        mock_tool_call.function = MagicMock()
        mock_tool_call.function.name = "book_appointment"
        mock_tool_call.function.arguments = json.dumps({
            "appointment_type": "consultation",
            "date": "2025-11-27",
            "start_time": "14:00",
            "patient_name": "John Doe",
            "patient_email": "john@example.com",
            "patient_phone": "555-123-4567",
            "reason": "General checkup"
        })
        
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message = MagicMock(
            content="",
            tool_calls=[mock_tool_call]
        )
        
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message = MagicMock(
            content="Your appointment has been confirmed! Confirmation code: ABC123",
            tool_calls=None
        )
        
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[mock_response_1, mock_response_2]
        )
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        result = await agent.process_message(
            user_message="Book for John Doe, 555-123-4567, john@example.com",
            conversation_history=[]
        )
        
        assert "response" in result
        assert mock_book.called
        assert "ABC123" in result["response"] or result["metadata"]["used_tools"]


@pytest.mark.asyncio
async def test_cancel_appointment_tool():
    """Test appointment cancellation tool execution."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai, \
         patch('backend.tools.booking_tool.cancel_appointment') as mock_cancel:
        
        # Mock cancellation response
        mock_cancel.return_value = {
            "success": True,
            "message": "Appointment cancelled successfully",
            "booking_id": "APPT-202511-0001"
        }
        
        mock_client = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_789"
        mock_tool_call.function = MagicMock()
        mock_tool_call.function.name = "cancel_appointment"
        mock_tool_call.function.arguments = json.dumps({
            "booking_id": "APPT-202511-0001"
        })
        
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message = MagicMock(
            content="",
            tool_calls=[mock_tool_call]
        )
        
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message = MagicMock(
            content="Your appointment has been cancelled successfully.",
            tool_calls=None
        )
        
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[mock_response_1, mock_response_2]
        )
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        result = await agent.process_message(
            user_message="Cancel appointment APPT-202511-0001",
            conversation_history=[]
        )
        
        assert "response" in result
        assert mock_cancel.called


# ============================================================================
# FAQ/RAG Tests
# ============================================================================

@pytest.mark.asyncio
async def test_faq_detection():
    """Test that FAQ questions are detected."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI'):
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        # Test various FAQ questions
        assert agent._check_if_faq_question("What insurance do you accept?")
        assert agent._check_if_faq_question("Where can I park?")
        assert agent._check_if_faq_question("What are your hours?")
        assert agent._check_if_faq_question("How do I get there?")
        
        # Non-FAQ questions
        assert not agent._check_if_faq_question("I need an appointment")
        assert not agent._check_if_faq_question("Book me for tomorrow")


@pytest.mark.asyncio
async def test_faq_with_rag():
    """Test FAQ handling with mocked RAG."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai, \
         patch('backend.rag.faq_rag.faq_rag') as mock_rag:
        
        # Mock RAG response
        mock_rag.answer_question.return_value = {
            "answer": "We accept Blue Cross, Aetna, and Cigna.",
            "context": "Insurance information...",
            "confidence": 0.95
        }
        
        # Mock LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock(
            content="We accept most major insurance plans including Blue Cross, Aetna, and Cigna.",
            tool_calls=None
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        result = await agent.process_message(
            user_message="What insurance do you accept?",
            conversation_history=[]
        )
        
        assert "response" in result
        assert mock_rag.answer_question.called


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_max_iterations_reached():
    """Test that max iterations prevents infinite loops."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai:
        # Mock to always request tools (infinite loop scenario)
        mock_client = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_loop"
        mock_tool_call.function = MagicMock()
        mock_tool_call.function.name = "check_availability"
        mock_tool_call.function.arguments = json.dumps({
            "date": "2025-11-27",
            "appointment_type": "consultation"
        })
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock(
            content="",
            tool_calls=[mock_tool_call]
        )
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        result = await agent.process_message(
            user_message="Test max iterations",
            conversation_history=[]
        )
        
        assert "response" in result
        assert result["metadata"]["error"] == "max_iterations_reached"


@pytest.mark.asyncio
async def test_tool_execution_error_handling():
    """Test graceful handling of tool execution errors."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai, \
         patch('backend.tools.booking_tool.book_appointment') as mock_book:
        
        # Mock tool to raise error
        mock_book.side_effect = Exception("Database connection failed")
        
        mock_client = MagicMock()
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_error"
        mock_tool_call.function = MagicMock()
        mock_tool_call.function.name = "book_appointment"
        mock_tool_call.function.arguments = json.dumps({
            "appointment_type": "consultation",
            "date": "2025-11-27",
            "start_time": "14:00",
            "patient_name": "Test",
            "patient_email": "test@test.com",
            "patient_phone": "555-0000",
            "reason": "Test"
        })
        
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message = MagicMock(
            content="",
            tool_calls=[mock_tool_call]
        )
        
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message = MagicMock(
            content="I apologize, but there was an error processing your request.",
            tool_calls=None
        )
        
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[mock_response_1, mock_response_2]
        )
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        result = await agent.process_message(
            user_message="Book appointment",
            conversation_history=[]
        )
        
        assert "response" in result
        # Tool should have been called despite error
        assert mock_book.called


# ============================================================================
# Integration Tests (Mocked)
# ============================================================================

@pytest.mark.asyncio
async def test_full_booking_flow_mocked():
    """Test complete booking flow with all mocks."""
    with patch('backend.agent.scheduling_agent.AsyncOpenAI') as mock_openai, \
         patch('backend.tools.availability_tool.check_availability') as mock_avail, \
         patch('backend.tools.booking_tool.book_appointment') as mock_book:
        
        # Setup mocks
        mock_avail.return_value = {
            "success": True,
            "available_slots": [{"start_time": "14:00", "end_time": "14:30"}]
        }
        
        mock_book.return_value = {
            "success": True,
            "booking_id": "APPT-TEST-001",
            "confirmation_code": "TEST123",
            "status": "confirmed"
        }
        
        mock_client = MagicMock()
        responses = [
            # Initial greeting
            MagicMock(choices=[MagicMock(message=MagicMock(
                content="I can help! What type of appointment?",
                tool_calls=None
            ))]),
            # Final confirmation
            MagicMock(choices=[MagicMock(message=MagicMock(
                content="Appointment confirmed! Code: TEST123",
                tool_calls=None
            ))])
        ]
        mock_client.chat.completions.create = AsyncMock(side_effect=responses)
        mock_openai.return_value = mock_client
        
        agent = SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")
        
        conversation = []
        
        # Step 1: Initial request
        result1 = await agent.process_message(
            user_message="I need an appointment",
            conversation_history=conversation
        )
        
        assert "response" in result1
        assert len(result1["response"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

