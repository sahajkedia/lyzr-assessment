"""
Main FastAPI application.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path so backend package can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Load from .env.example as fallback (for demo)
    env_example_path = Path(__file__).parent.parent / ".env.example"
    if env_example_path.exists():
        load_dotenv(env_example_path)

from backend.api.chat import router as chat_router
from backend.api.appointments import router as appointments_router
from backend.agent.scheduling_agent import initialize_agent

# Initialize FastAPI app
app = FastAPI(
    title="Medical Appointment Scheduling Agent",
    description="Intelligent conversational agent for scheduling medical appointments",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("Initializing Medical Appointment Scheduling Agent...")
    
    # Initialize the agent
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    print(f"LLM Provider: {llm_provider}")
    print(f"LLM Model: {llm_model}")
    
    initialize_agent(llm_provider=llm_provider, model=llm_model)
    
    print("Agent initialized successfully!")
    print(f"Server running on port {os.getenv('BACKEND_PORT', 8000)}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Medical Appointment Scheduling Agent API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "appointments": "/api/appointments",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "appointment-scheduling-agent"
    }


# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(appointments_router, prefix="/api", tags=["appointments"])


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

