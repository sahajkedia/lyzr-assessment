"""
Simple script to run the scheduling agent interactively.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path so backend package can be imported
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from backend.agent.scheduling_agent import SchedulingAgent
from backend.models.schemas import ChatMessage

# Load environment
load_dotenv()


async def main():
    """Run interactive chat session."""
    print("=" * 80)
    print("Medical Appointment Scheduling Agent")
    print("=" * 80)
    print()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: No API key found!")
        print()
        print("Please set your API key in .env file:")
        print("  - For OpenAI: OPENAI_API_KEY=your_key")
        print("  - For Anthropic: ANTHROPIC_API_KEY=your_key")
        print()
        return
    
    # Initialize agent
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    print(f"🤖 Initializing agent...")
    print(f"   Provider: {llm_provider}")
    print(f"   Model: {llm_model}")
    print()
    
    try:
        agent = SchedulingAgent(llm_provider=llm_provider, model=llm_model)
        print("✅ Agent initialized successfully!")
        print()
        print("Type your message and press Enter. Type 'quit' to exit.")
        print("-" * 80)
        print()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return
    
    # Conversation history
    conversation_history = []
    
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nThank you for using the Medical Appointment Scheduling Agent!")
            print("Have a great day!")
            break
        
        # Process message
        try:
            result = await agent.process_message(
                user_message=user_input,
                conversation_history=conversation_history
            )
            
            # Update history
            conversation_history.append(ChatMessage(role="user", content=user_input))
            conversation_history.append(ChatMessage(role="assistant", content=result["response"]))
            
            # Print response
            print(f"\nAgent: {result['response']}\n")
            
            # Show metadata if available
            if result.get("metadata", {}).get("used_tools"):
                tools_used = result["metadata"].get("tool_calls", [])
                print(f"[Tools used: {', '.join(tools_used)}]\n")
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    asyncio.run(main())

