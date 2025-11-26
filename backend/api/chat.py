"""
Chat API endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid

from backend.models.schemas import ChatRequest, ChatResponse, ChatMessage
from backend.agent import scheduling_agent

router = APIRouter()

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for conversational interaction.
    
    Args:
        request: Chat request with message and history
        
    Returns:
        Chat response with assistant's message
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions:
            sessions[session_id] = {
                "conversation_history": [],
                "context": {}
            }
        
        session = sessions[session_id]
        
        # Use conversation history from request or session
        if request.conversation_history:
            conversation_history = request.conversation_history
        else:
            conversation_history = [
                ChatMessage(**msg) for msg in session["conversation_history"]
            ]
        # Process message with agent
        agent = getattr(scheduling_agent, "agent", None)
        if agent is None:
            raise HTTPException(status_code=500, detail="Scheduling agent is not initialized.")
        if not hasattr(agent, "process_message") or not callable(getattr(agent, "process_message")):
            raise HTTPException(status_code=500, detail="Scheduling agent does not support message processing.")
        result = await agent.process_message(
            user_message=request.message,
            conversation_history=conversation_history
        )
        # Update conversation history
        updated_history = conversation_history + [
            ChatMessage(role="user", content=request.message),
            ChatMessage(role="assistant", content=result["response"])
        ]
        
        # Save to session
        session["conversation_history"] = [
            {"role": msg.role, "content": msg.content}
            for msg in updated_history
        ]
        
        # Return response
        return ChatResponse(
            message=result["response"],
            conversation_history=updated_history,
            session_id=session_id,
            metadata=result.get("metadata")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{session_id}")
async def clear_session(session_id: str) -> Dict[str, str]:
    """
    Clear a chat session.
    
    Args:
        session_id: Session ID to clear
        
    Returns:
        Success message
    """
    if session_id in sessions:
        del sessions[session_id]
    
    return {"message": "Session cleared successfully"}


@router.get("/chat/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get session data.
    
    Args:
        session_id: Session ID
        
    Returns:
        Session data
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]

