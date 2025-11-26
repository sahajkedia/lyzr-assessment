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
from backend.api.calendly import router as calendly_router
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
    print("\n" + "="*60)
    print("🏥 Medical Appointment Scheduling Agent")
    print("="*60)
    
    # Initialize the agent
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    print(f"\n📝 LLM Configuration:")
    print(f"   Provider: {llm_provider}")
    print(f"   Model: {llm_model}")
    
    initialize_agent(llm_provider=llm_provider, model=llm_model)
    print("   ✅ Agent initialized")
    
    # Initialize Mock Calendly service
    print(f"\n📅 Mock Calendly Service:")
    from backend.api.calendly_service import calendly_service
    await calendly_service.initialize()
    status = calendly_service.get_status()
    
    print(f"   📋 Mock mode active")
    print(f"   📊 Total appointments: {status['total_appointments']}")
    print(f"   ✅ Active appointments: {status['active_appointments']}")
    print(f"   🏥 Appointment types: {status['appointment_types']}")
    
    port = os.getenv('BACKEND_PORT', 8000)
    print(f"\n🚀 Server running on port {port}")
    print("="*60 + "\n")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Medical Appointment Scheduling Agent API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "appointments": "/api/appointments",
            "calendly": "/api/calendly",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    from backend.api.calendly_service import calendly_service
    
    calendly_status = calendly_service.get_status()
    
    return {
        "status": "healthy",
        "service": "appointment-scheduling-agent",
        "calendly": {
            "mode": calendly_status["mode"],
            "total_appointments": calendly_status["total_appointments"],
            "active_appointments": calendly_status["active_appointments"],
            "appointment_types": calendly_status["appointment_types"],
        }
    }


# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(appointments_router, prefix="/api", tags=["appointments"])
app.include_router(calendly_router, prefix="/api/calendly", tags=["calendly"])


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

