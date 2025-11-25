"""
Simple test client for the API.
"""
import requests
import json


def main():
    """Test the chat API."""
    base_url = "http://localhost:8000"
    
    print("=" * 80)
    print("Testing Medical Appointment Scheduling Agent API")
    print("=" * 80)
    print()
    
    # Check health
    print("1. Checking health...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✅ Health check passed")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        print()
        print("Make sure the server is running:")
        print("   cd backend && python main.py")
        return
    
    print()
    
    # Test conversation
    print("2. Testing conversation...")
    
    messages = [
        "Hello!",
        "What insurance do you accept?",
        "I need to schedule an appointment",
        "I've been having headaches",
        "General consultation sounds good"
    ]
    
    conversation_history = []
    session_id = None
    
    for msg in messages:
        print(f"\n   You: {msg}")
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": msg,
                    "conversation_history": conversation_history,
                    "session_id": session_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Agent: {data['message'][:200]}...")
                
                conversation_history = [
                    {"role": h["role"], "content": h["content"]}
                    for h in data["conversation_history"]
                ]
                session_id = data["session_id"]
                
                if data.get("metadata", {}).get("used_tools"):
                    print(f"   [Tools: {', '.join(data['metadata']['tool_calls'])}]")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   {response.text}")
        
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print()
    print("=" * 80)
    print("Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()

