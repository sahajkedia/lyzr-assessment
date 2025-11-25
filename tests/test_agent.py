"""
Test cases for the scheduling agent.
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.schemas import ChatMessage
from backend.agent.scheduling_agent import SchedulingAgent


@pytest.fixture
async def agent():
    """Create agent instance for testing."""
    # Use a simple model for testing
    return SchedulingAgent(llm_provider="openai", model="gpt-4-turbo")


@pytest.mark.asyncio
async def test_greeting():
    """Test initial greeting."""
    agent = SchedulingAgent()
    
    result = await agent.process_message(
        user_message="Hello",
        conversation_history=[]
    )
    
    assert "response" in result
    assert len(result["response"]) > 0
    print(f"Greeting response: {result['response']}")


@pytest.mark.asyncio
async def test_appointment_booking_flow():
    """Test full appointment booking flow."""
    agent = SchedulingAgent()
    
    conversation = []
    
    # Step 1: User wants to book
    messages = [
        "I need to see the doctor",
        "I've been having headaches",
        "General consultation sounds good",
        "Tomorrow afternoon if possible",
        "2:00 PM works for me",
        "John Doe",
        "555-123-4567",
        "john@example.com",
        "Yes, please confirm"
    ]
    
    for msg in messages:
        result = await agent.process_message(
            user_message=msg,
            conversation_history=conversation
        )
        
        conversation.append(ChatMessage(role="user", content=msg))
        conversation.append(ChatMessage(role="assistant", content=result["response"]))
        
        print(f"\nUser: {msg}")
        print(f"Agent: {result['response']}")
        
        assert len(result["response"]) > 0


@pytest.mark.asyncio
async def test_faq_insurance():
    """Test FAQ about insurance."""
    agent = SchedulingAgent()
    
    result = await agent.process_message(
        user_message="What insurance do you accept?",
        conversation_history=[]
    )
    
    assert "response" in result
    response_lower = result["response"].lower()
    
    # Should mention some insurance providers
    assert any(insurance in response_lower for insurance in [
        "blue cross", "aetna", "cigna", "united", "medicare"
    ])
    
    print(f"Insurance FAQ response: {result['response']}")


@pytest.mark.asyncio
async def test_faq_parking():
    """Test FAQ about parking."""
    agent = SchedulingAgent()
    
    result = await agent.process_message(
        user_message="Where can I park?",
        conversation_history=[]
    )
    
    assert "response" in result
    response_lower = result["response"].lower()
    
    # Should mention parking information
    assert "park" in response_lower
    
    print(f"Parking FAQ response: {result['response']}")


@pytest.mark.asyncio
async def test_faq_hours():
    """Test FAQ about clinic hours."""
    agent = SchedulingAgent()
    
    result = await agent.process_message(
        user_message="What are your hours of operation?",
        conversation_history=[]
    )
    
    assert "response" in result
    response_lower = result["response"].lower()
    
    # Should mention hours
    assert any(term in response_lower for term in ["hour", "open", "close", "9", "5", "pm", "am"])
    
    print(f"Hours FAQ response: {result['response']}")


@pytest.mark.asyncio
async def test_context_switching():
    """Test switching from booking to FAQ and back."""
    agent = SchedulingAgent()
    
    conversation = []
    
    # Start booking
    result1 = await agent.process_message(
        user_message="I want to book an appointment",
        conversation_history=conversation
    )
    conversation.append(ChatMessage(role="user", content="I want to book an appointment"))
    conversation.append(ChatMessage(role="assistant", content=result1["response"]))
    
    # Ask FAQ
    result2 = await agent.process_message(
        user_message="Actually, what insurance do you accept?",
        conversation_history=conversation
    )
    conversation.append(ChatMessage(role="user", content="Actually, what insurance do you accept?"))
    conversation.append(ChatMessage(role="assistant", content=result2["response"]))
    
    # Continue booking
    result3 = await agent.process_message(
        user_message="Okay, I have Blue Cross. I'd like to schedule a checkup",
        conversation_history=conversation
    )
    
    print(f"\nStep 1 (Booking): {result1['response']}")
    print(f"\nStep 2 (FAQ): {result2['response']}")
    print(f"\nStep 3 (Back to booking): {result3['response']}")
    
    assert len(result3["response"]) > 0


@pytest.mark.asyncio
async def test_edge_case_past_date():
    """Test handling of past date."""
    agent = SchedulingAgent()
    
    result = await agent.process_message(
        user_message="Can I book an appointment for yesterday?",
        conversation_history=[]
    )
    
    assert "response" in result
    print(f"Past date response: {result['response']}")


@pytest.mark.asyncio
async def test_edge_case_ambiguous_time():
    """Test handling of ambiguous time."""
    agent = SchedulingAgent()
    
    conversation = [
        ChatMessage(role="user", content="I need an appointment"),
        ChatMessage(role="assistant", content="I'd be happy to help! What brings you in?")
    ]
    
    result = await agent.process_message(
        user_message="Tomorrow around 3",
        conversation_history=conversation
    )
    
    assert "response" in result
    print(f"Ambiguous time response: {result['response']}")


if __name__ == "__main__":
    # Run tests
    import asyncio
    
    print("=" * 80)
    print("TESTING GREETING")
    print("=" * 80)
    asyncio.run(test_greeting())
    
    print("\n" + "=" * 80)
    print("TESTING FAQ - INSURANCE")
    print("=" * 80)
    asyncio.run(test_faq_insurance())
    
    print("\n" + "=" * 80)
    print("TESTING FAQ - PARKING")
    print("=" * 80)
    asyncio.run(test_faq_parking())
    
    print("\n" + "=" * 80)
    print("TESTING FAQ - HOURS")
    print("=" * 80)
    asyncio.run(test_faq_hours())

