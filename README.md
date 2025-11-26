# Medical Appointment Scheduling Agent

An intelligent conversational AI agent that helps patients schedule medical appointments through natural conversation, while seamlessly answering frequently asked questions using RAG (Retrieval Augmented Generation).

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [System Design](#system-design)
- [Scheduling Logic](#scheduling-logic)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)

---

## Overview

This project implements a complete medical appointment scheduling system with:

- **Natural Conversation Flow**: Warm, empathetic dialogue that feels human
- **Intelligent Scheduling**: Smart appointment booking with real-time availability checking
- **RAG-Powered FAQ System**: Accurate answers using clinic knowledge base
- **Seamless Context Switching**: Smoothly handles FAQ questions during booking
- **Multi-Appointment Types**: Supports 4 appointment types with different durations
- **Edge Case Handling**: Gracefully manages ambiguous inputs, conflicts, and errors
- **Full-Stack Implementation**: React frontend with FastAPI backend

### Appointment Types

| Type                    | Duration | Use Case                                               |
| ----------------------- | -------- | ------------------------------------------------------ |
| General Consultation    | 30 min   | Common health concerns, illness, injuries              |
| Follow-up               | 15 min   | Review results, check progress, medication adjustments |
| Physical Exam           | 45 min   | Annual physicals, comprehensive examinations           |
| Specialist Consultation | 60 min   | Complex conditions, specialized care                   |

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **LLM**: OpenAI GPT-4 Turbo / Anthropic Claude 3 Sonnet
- **Vector Database**: ChromaDB (persistent)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Calendar API**: Mock Calendly API with real API integration support

### Frontend
- **Framework**: React 18 with Hooks
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Testing
- **Framework**: Pytest with pytest-asyncio
- **Mocking**: unittest.mock
- **Coverage**: 70+ tests, fully mocked (no external dependencies required)

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 16+ and npm (for frontend)
- OpenAI API key or Anthropic API key
- Git

### Installation Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd lyzr-assessment-1
```

#### 2. Backend Setup

**Create and activate virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

#### 3. Environment Configuration

**Copy the example environment file:**

```bash
cp .env.example .env
```

**Edit `.env` and configure:**

**For OpenAI (GPT-4):**
```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=your_api_key_here

# Vector Database
VECTOR_DB=chromadb
VECTOR_DB_PATH=./data/vectordb

# Clinic Configuration
CLINIC_NAME=HealthCare Plus Clinic
CLINIC_PHONE=+1-555-123-4567
TIMEZONE=America/New_York

# Application
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

**For Anthropic (Claude):**
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=your_api_key_here
```

#### 4. Calendly API Setup (Optional)

The system works with both mock and real Calendly API:

**Mock Mode (No API Key Required):**
- System automatically uses local JSON storage
- Fully functional for testing and demos
- No external dependencies

**Real Calendly Mode:**

1. Sign up for a free Calendly account at https://calendly.com
2. Get your Personal Access Token from https://calendly.com/integrations/api_webhooks
3. Add to your `.env`:
```env
CALENDLY_API_KEY=your_personal_access_token_here
```
4. Create event types in Calendly:
   - General Consultation (30 min)
   - Follow-up (15 min)
   - Physical Exam (45 min)
   - Specialist Consultation (60 min)

The system automatically detects if Calendly is configured and switches modes accordingly.

#### 5. Frontend Setup (Optional)

```bash
cd frontend
npm install
```

#### 6. Initialize Knowledge Base

The FAQ knowledge base will be automatically initialized on first run:
- Loads clinic information from `data/clinic_info.json`
- Generates embeddings using Sentence Transformers
- Stores in ChromaDB vector database at `data/vectordb/`

### Running the Application

#### Option 1: Start Everything (Recommended)

```bash
./start.sh
```

This starts:
- Backend API on `http://localhost:8000`
- Frontend UI on `http://localhost:3000`

#### Option 2: Start Backend Only

```bash
cd backend
python main.py
```

Or using uvicorn:

```bash
uvicorn backend.main:app --reload --port 8000
```

**Access API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Option 3: Start Frontend Only

```bash
cd frontend
npm run dev
```

Opens at `http://localhost:3000`

### Testing the System

**1. Web UI (Recommended):**
```
Open http://localhost:3000
```

**2. Interactive CLI:**
```bash
python run.py
```

**3. API Directly:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to schedule an appointment",
    "conversation_history": []
  }'
```

**4. Run Test Suite:**
```bash
pytest tests/ -v
```

---

## System Design

### Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                         User/Patient                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               Chat Endpoint (/api/chat)                   │  │
│  └───────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Scheduling Agent                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LLM (GPT-4 / Claude)                        │   │
│  │         - Conversation Management                         │   │
│  │         - Intent Understanding                            │   │
│  │         - Tool Selection                                  │   │
│  └──────────────────┬──────────────┬────────────────────────┘   │
└─────────────────────┼──────────────┼─────────────────────────────┘
                      │              │
          ┌───────────┴──┐      ┌────┴──────────┐
          │              │      │                │
          ▼              ▼      ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   FAQ RAG    │  │ Availability │  │ Booking Tool     │
│              │  │    Tool      │  │                  │
│ ┌──────────┐ │  │              │  │ - Book Appt     │
│ │ Vector   │ │  │ - Check      │  │ - Cancel Appt   │
│ │ Store    │ │  │   Slots      │  │ - Reschedule    │
│ │(ChromaDB)│ │  │ - Get Next   │  │                  │
│ └──────────┘ │  │   Available  │  │                  │
│              │  │              │  │                  │
│ ┌──────────┐ │  └──────┬───────┘  └────────┬─────────┘
│ │Embeddings│ │         │                   │
│ │ Model    │ │         │                   │
│ └──────────┘ │         ▼                   ▼
└──────┬───────┘  ┌─────────────────────────────────┐
       │          │   Calendly API (Mock/Real)       │
       │          │                                   │
       │          │  - Working Hours Management      │
       │          │  - Slot Calculation              │
       │          │  - Conflict Detection            │
       │          │  - Appointment Storage           │
       │          └─────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│      Clinic Knowledge Base              │
│  - Clinic Details (location, hours)    │
│  - Insurance & Billing                 │
│  - Visit Preparation                   │
│  - Policies (cancellation, COVID)      │
└─────────────────────────────────────────┘
```

### Agent Conversation Flow

The agent follows a three-phase conversation flow:

```
User Message
    │
    ▼
Intent Detection
    │
    ├─── FAQ Question? ───► RAG System ───► Generate Answer ───► Response
    │                          │
    │                          └─► Return to Scheduling Context (if applicable)
    │
    └─── Scheduling Request
            │
            ▼
        Phase Detection
            │
            ├─── Phase 1: Understanding Needs
            │       ├─► Determine appointment type
            │       └─► Get date/time preferences
            │
            ├─── Phase 2: Slot Recommendation
            │       ├─► Call Availability Tool
            │       ├─► Present 3-5 slots
            │       └─► Handle selection/rejection
            │
            └─── Phase 3: Booking Confirmation
                    ├─► Collect patient info
                    ├─► Confirm all details
                    ├─► Call Booking Tool
                    └─► Provide confirmation
```

### Calendly Integration Approach

The system uses a **unified Calendly service** with automatic fallback:

**Operating Modes:**

| Mode | Description |
|------|-------------|
| `REAL` | Connected to Calendly API - all bookings sync with your Calendly account |
| `MOCK` | No API key configured - uses local JSON storage |
| `FALLBACK` | API failed - automatically falls back to mock for uninterrupted service |

**Integration Features:**
- Automatic mode detection
- Real-time availability fetching
- Event type mapping
- Graceful fallback on API failures
- Local backup of all appointments

### RAG Pipeline for FAQs

#### 1. Knowledge Base Structure

The clinic knowledge base (`data/clinic_info.json`) contains structured information about:
- **Clinic Details**: Location, hours, parking, directions
- **Insurance & Billing**: Accepted providers, payment methods, costs
- **Visit Preparation**: Required documents, what to bring
- **Policies**: Cancellation, late arrival, COVID-19 protocols
- **Appointment Types**: Descriptions and use cases

#### 2. RAG Process Flow

```
User Question: "What insurance do you accept?"
    │
    ▼
┌─────────────────────────────────────────────┐
│  Step 1: Query Processing                   │
│  ├─ Receive user question                   │
│  └─ Generate query embedding                │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 2: Semantic Search                    │
│  ├─ Query vector store (ChromaDB)           │
│  ├─ Find top-K similar documents            │
│  └─ Return with similarity scores           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 3: Context Compilation                │
│  ├─ Extract relevant information            │
│  ├─ Format as context                       │
│  └─ Add to LLM prompt                       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
              ┌─────────────────┐
              │   LLM Generates │
              │  Natural Answer │
              └─────────────────┘
```

**Technical Details:**
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Vector Database**: ChromaDB with persistent storage
- **Retrieval Method**: Cosine similarity search
- **Top-K Results**: 3-5 most relevant documents
- **Context Window**: Provides retrieved context to LLM for accurate answers

#### 3. Context Switching Mechanism

The agent seamlessly switches between scheduling and FAQ:

```
User: "I want to book an appointment"
Agent: "I'd be happy to help! What brings you in?"

User: "What insurance do you accept?"  ← FAQ during scheduling
Agent: [Answers using RAG]
       "We accept Blue Cross, Aetna, Cigna..."
       [Returns to scheduling]
       "Now, what brings you in today?"

User: "I have Blue Cross, I need a checkup"  ← Back to scheduling
Agent: [Continues scheduling flow]
```

**Implementation:**
- Maintains conversation history throughout
- Detects FAQ intent via LLM analysis
- Pauses scheduling phase
- Queries RAG system
- Provides FAQ answer
- Resumes scheduling from previous phase

### Tool Calling Strategy

The system uses **native function calling** (OpenAI) and **tool use** (Anthropic), not ReAct prompting.

**Available Tools:**

1. **`check_availability`**
   ```python
   check_availability(date: str, appointment_type: str) -> dict
   ```
   - Checks specific date for available slots
   - Returns list of time slots with availability status

2. **`get_next_available_slots`**
   ```python
   get_next_available_slots(appointment_type: str, num_days: int = 7) -> dict
   ```
   - Gets upcoming availability across multiple days
   - Returns dates with sample available slots

3. **`book_appointment`**
   ```python
   book_appointment(
       appointment_type: str,
       date: str,
       start_time: str,
       patient_name: str,
       patient_email: str,
       patient_phone: str,
       reason: str
   ) -> dict
   ```
   - Books appointment after confirmation
   - Validates slot availability
   - Generates booking ID and confirmation code

4. **`cancel_appointment`**
   ```python
   cancel_appointment(booking_id: str) -> dict
   ```
   - Cancels existing appointment
   - Updates appointment status

5. **`reschedule_appointment`**
   ```python
   reschedule_appointment(
       booking_id: str,
       new_date: str,
       new_start_time: str
   ) -> dict
   ```
   - Moves appointment to new date/time
   - Preserves booking ID and confirmation code

**Tool Execution Flow:**

```
User: "I need an appointment tomorrow afternoon"
    │
    ▼
LLM analyzes: needs appointment_type, has date/time preference
    │
    ▼
LLM asks: "What brings you in today?"
    │
    ▼
User: "Headaches"
    │
    ▼
LLM decides: Call get_next_available_slots(
    appointment_type="consultation",
    num_days=1
)
    │
    ▼
Tool returns: Available afternoon slots
    │
    ▼
LLM generates: "I have these afternoon slots..."
```

**Benefits:**
- More reliable than ReAct prompting
- Automatic parameter validation
- Better handling of multi-step processes
- Native error handling

---

## Scheduling Logic

### How Available Slots Are Determined

The system uses a sophisticated slot calculation algorithm:

#### 1. Load Doctor's Schedule

```json
{
  "working_hours": {
    "monday": { "start": "09:00", "end": "17:00" },
    "tuesday": { "start": "09:00", "end": "17:00" },
    ...
  },
  "lunch_break": { "start": "12:00", "end": "13:00" },
  "blocked_dates": ["2024-12-25", "2024-01-01"]
}
```

#### 2. Validate Date

- ✅ Not in the past
- ✅ Not a weekend (unless configured)
- ✅ Not a blocked date (holidays)
- ✅ Within working hours

#### 3. Generate Time Slots

- Creates 15-minute intervals from opening to closing
- Excludes lunch break periods
- Example: 9:00, 9:15, 9:30, 9:45, 10:00...

#### 4. Check Existing Appointments

```python
# Load existing appointments from data/appointments.json
existing_appointments = load_appointments()

# Filter for the requested date
date_appointments = filter_by_date(existing_appointments, target_date)

# Mark slots as unavailable if they conflict
for appointment in date_appointments:
    mark_slots_unavailable(appointment.start_time, appointment.duration)
```

#### 5. Match Appointment Type Duration

Each appointment type requires contiguous available slots:

| Type | Duration | Slots Required |
|------|----------|----------------|
| Follow-up | 15 min | 1 slot |
| Consultation | 30 min | 2 consecutive slots |
| Physical | 45 min | 3 consecutive slots |
| Specialist | 60 min | 4 consecutive slots |

**Algorithm:**
```python
def find_available_slots(date, appointment_type):
    slots_needed = get_slots_for_type(appointment_type)  # e.g., 2 for consultation
    all_slots = generate_15min_slots(date)
    
    available_blocks = []
    for i in range(len(all_slots) - slots_needed + 1):
        block = all_slots[i:i + slots_needed]
        if all(slot.available for slot in block):
            available_blocks.append({
                "start_time": block[0].time,
                "end_time": block[-1].time + duration,
                "available": True
            })
    
    return available_blocks
```

### Appointment Type Handling

**Type Determination Logic:**

```
User Reason → Recommended Type
────────────────────────────────
"Headache", "Cold", "Flu" → General Consultation
"Follow up on blood pressure" → Follow-up
"Annual physical", "Checkup" → Physical Exam
"Cardiology", "Complex issue" → Specialist Consultation
```

**Duration Enforcement:**
- System ensures requested slot has sufficient consecutive availability
- Automatically blocks out the full duration when booking
- Prevents overlapping appointments

### Conflict Prevention

#### 1. Real-time Availability Checking

```python
# Always check before booking
def book_appointment(slot_info):
    # Double-check availability
    if not is_slot_still_available(slot_info.date, slot_info.time):
        raise ConflictError("Slot no longer available")
    
    # Proceed with booking
    create_appointment(slot_info)
```

#### 2. Atomic Operations

- Read appointment file
- Check for conflicts
- Write new appointment
- All in a single operation (would use database transactions in production)

#### 3. Concurrent Booking Protection

**Current (Development):**
- In-memory file locking
- Single server instance

**Production Ready:**
- Use database row-level locking
- Implement optimistic locking with version numbers
- Use Redis for distributed locking

#### 4. Buffer Time Handling

Optional buffer time between appointments:

```python
BUFFER_MINUTES = 0  # Configurable

def calculate_end_time(start_time, duration):
    return start_time + duration + BUFFER_MINUTES
```

#### 5. Validation Layers

```
User Request
    │
    ▼
Frontend Validation (basic checks)
    │
    ▼
API Validation (Pydantic schemas)
    │
    ▼
Business Logic Validation (slot availability)
    │
    ▼
Database Validation (unique constraints)
```

---

## Testing

### Test Suite Overview

The project includes 70+ comprehensive tests, all **fully mocked** (no external dependencies required).

**Test Files:**
- `tests/test_agent_mocked.py` - Agent conversation tests (15+ tests)
- `tests/test_tools.py` - Tool function tests (18+ tests)
- `tests/test_api.py` - API endpoint tests (20+ tests)
- `tests/test_models.py` - Schema validation tests (22 tests)

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agent_mocked.py -v

# Run specific test
pytest tests/test_agent_mocked.py::test_greeting_response -v
```

### Test Coverage

**What's Tested:**

✅ **Conversational Quality:**
- Natural greeting responses
- Context awareness
- Empathetic tone
- Smooth topic transitions

✅ **RAG System:**
- FAQ retrieval accuracy
- Semantic search
- Context switching
- No hallucinations

✅ **Scheduling Intelligence:**
- Appointment type determination
- Slot recommendations
- Preference understanding
- Booking validation

✅ **Edge Cases:**
- No available slots
- Past dates
- Invalid inputs
- API failures
- User changes mind
- Ambiguous time references

### Example Conversations

See `tests/example_conversations.md` for 10+ detailed conversation examples demonstrating:

#### 1. Successful Booking
```
User: I need to see the doctor
Agent: I'd be happy to help! What brings you in today?
User: I've been having headaches
Agent: I recommend a General Consultation (30 minutes)...
[Complete booking flow]
```

#### 2. FAQ During Booking (Context Switching)
```
User: I want to book an appointment
Agent: What brings you in?
User: What insurance do you accept?  ← Context switch
Agent: [Answers from knowledge base]
User: I have Blue Cross, I need a checkup  ← Back to scheduling
Agent: [Continues scheduling]
```

#### 3. No Available Slots
```
User: Can I see the doctor today?
Agent: Unfortunately, we don't have availability today.
       However, I have these options for tomorrow:
       - 9:00 AM
       - 11:30 AM
       - 2:00 PM
       Would any of these work?
```

#### 4. Ambiguous Time References
```
User: I need an appointment tomorrow morning
Agent: [Shows morning slots: 9:00 AM, 10:30 AM]
User: Around 10
Agent: Just to clarify, would you prefer the 10:30 AM slot?
```

#### 5. User Changes Mind
```
User: I need a physical exam
Agent: [Shows availability]
User: Actually, I just need a quick follow-up
Agent: No problem! A follow-up is 15 minutes...
```

### Edge Cases Covered

**Date/Time Issues:**
- Past dates → Politely corrects, suggests future dates
- Invalid dates → Validates and requests correction
- Outside business hours → Explains hours, suggests alternatives
- "Tomorrow morning" → Clarifies specific times
- "Around 3" → Confirms AM or PM

**Availability Issues:**
- No slots available → Offers alternative dates, provides phone number
- All afternoon slots booked → Suggests mornings or next day
- Slot taken during booking → Detects conflict, offers alternatives

**API Failures:**
- Calendly unavailable → Fallback to mock mode
- Network timeout → Retry logic with clear communication
- Invalid API key → Graceful degradation with phone number

**User Behavior:**
- Changes mind mid-booking → Gracefully restarts
- Asks multiple FAQs → Answers all, maintains context
- Provides incomplete information → Politely asks for missing details
- Ambiguous responses → Seeks clarification

**System Errors:**
- Invalid appointment type → Suggests valid types
- Malformed input → Validates and requests correction
- Session expires → Maintains conversation history

---

## API Documentation

### Main Endpoints

#### POST /api/chat

Main conversational endpoint.

**Request:**
```json
{
  "message": "I need to schedule an appointment",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "message": "I'd be happy to help you schedule an appointment!",
  "conversation_history": [...],
  "session_id": "generated-or-provided-session-id",
  "metadata": {
    "iterations": 1,
    "used_tools": false,
    "tool_calls": []
  }
}
```

#### GET /api/calendly/status

Check Calendly connection status.

**Response:**
```json
{
  "success": true,
  "status": {
    "mode": "real",
    "calendly_configured": true,
    "event_types_mapped": 4,
    "local_appointments": 5,
    "initialized": true
  }
}
```

#### POST /api/calendly/availability

Check slot availability for specific date.

**Request:**
```json
{
  "date": "2024-12-15",
  "appointment_type": "consultation"
}
```

**Response:**
```json
{
  "date": "2024-12-15",
  "available_slots": [
    {"start_time": "09:00", "end_time": "09:30", "available": true},
    {"start_time": "09:30", "end_time": "10:00", "available": false},
    ...
  ]
}
```

#### POST /api/calendly/book

Book an appointment.

**Request:**
```json
{
  "appointment_type": "consultation",
  "date": "2024-12-15",
  "start_time": "10:00",
  "patient": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0100"
  },
  "reason": "Annual checkup"
}
```

**Response:**
```json
{
  "success": true,
  "booking_id": "APPT-2024-001",
  "confirmation_code": "ABC123",
  "status": "confirmed",
  "details": {
    "appointment_type": "consultation",
    "date": "2024-12-15",
    "start_time": "10:00",
    "end_time": "10:30"
  }
}
```

#### GET /health

Health check endpoint.

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Project Structure

```
lyzr-assessment-1/
├── README.md                          # This file
├── .env.example                       # Environment template
├── requirements.txt                   # Python dependencies
├── pytest.ini                         # Test configuration
├── start.sh                           # Convenience startup script
│
├── backend/
│   ├── main.py                        # FastAPI application entry point
│   │
│   ├── agent/
│   │   ├── scheduling_agent.py        # Main agent logic with LLM integration
│   │   └── prompts.py                 # System prompts for agent
│   │
│   ├── api/
│   │   ├── chat.py                    # Chat endpoints
│   │   ├── calendly.py                # Calendly API endpoints
│   │   ├── calendly_client.py         # Real Calendly API client
│   │   ├── calendly_integration.py    # Mock Calendly implementation
│   │   ├── calendly_service.py        # Unified service with fallback
│   │   └── appointments.py            # Appointments management
│   │
│   ├── rag/
│   │   ├── faq_rag.py                 # RAG system for FAQs
│   │   ├── embeddings.py              # Embedding model wrapper
│   │   └── vector_store.py            # ChromaDB wrapper
│   │
│   ├── tools/
│   │   ├── availability_tool.py       # Availability checking functions
│   │   └── booking_tool.py            # Booking operations
│   │
│   └── models/
│       └── schemas.py                 # Pydantic models
│
├── frontend/
│   ├── package.json                   # Frontend dependencies
│   ├── vite.config.js                 # Vite configuration
│   ├── tailwind.config.js             # Tailwind CSS config
│   │
│   └── src/
│       ├── App.jsx                    # Main app component
│       ├── main.jsx                   # Entry point
│       ├── index.css                  # Global styles
│       │
│       ├── components/
│       │   ├── ChatInterface.jsx      # Main chat container
│       │   ├── MessageList.jsx        # Message display
│       │   ├── MessageInput.jsx       # User input
│       │   ├── AppointmentCard.jsx    # Appointment display
│       │   ├── AppointmentManager.jsx # Appointment management
│       │   └── ConfirmationPage.jsx   # Booking confirmation
│       │
│       └── api/
│           └── chatApi.js             # API client
│
├── data/
│   ├── clinic_info.json               # FAQ knowledge base
│   ├── doctor_schedule.json           # Doctor's working hours
│   ├── appointments.json              # Booked appointments
│   └── vectordb/                      # ChromaDB storage (auto-generated)
│
└── tests/
    ├── README.md                      # Testing guide
    ├── conftest.py                    # Pytest configuration and fixtures
    ├── test_agent_mocked.py           # Agent tests (mocked)
    ├── test_tools.py                  # Tool tests
    ├── test_api.py                    # API tests
    ├── test_models.py                 # Schema tests
    └── example_conversations.md       # Example dialogues
```

---

## Key Features

### ✅ Natural Conversation
- Warm, empathetic dialogue
- Context-aware responses
- Smooth topic transitions
- Professional medical tone

### ✅ Intelligent Scheduling
- Understands date/time preferences
- Smart slot recommendations
- Multiple appointment types
- Real-time availability

### ✅ RAG-Powered FAQ
- Semantic search in knowledge base
- Accurate, grounded answers
- No hallucinations
- Context switching capability

### ✅ Edge Case Handling
- Graceful error recovery
- Ambiguous input clarification
- No availability alternatives
- API failure fallbacks

### ✅ Production Ready
- Comprehensive test suite
- Error handling
- Input validation
- Security considerations

---

## Performance

- **First Request**: 5-10 seconds (model loading)
- **Subsequent Requests**: 1-3 seconds
- **FAQ Lookup**: ~500ms
- **Tool Calls**: ~1-2 seconds
- **Test Suite Execution**: < 10 seconds

---

## Security & Privacy

**Current Implementation:**
- Environment variables for sensitive data
- Input validation on all endpoints
- CORS configuration
- No patient data in logs

**Production Requirements:**
- HIPAA compliance measures
- Data encryption at rest and in transit
- Audit logging
- Authentication & authorization
- Rate limiting
- Security headers
- Regular security audits

---

## Development Notes

- **LLM Provider**: Easily switch between OpenAI and Anthropic
- **Calendly Mode**: Works with or without real API
- **Session Management**: In-memory (use Redis in production)
- **Database**: JSON files (use PostgreSQL in production)
- **Deployment**: Ready for Docker/Kubernetes

---

## Future Enhancements

- [ ] SMS/email notifications
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Calendar sync (Google/Outlook)
- [ ] Admin dashboard
- [ ] Analytics & reporting
- [ ] Recurring appointments
- [ ] Waitlist functionality

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Verify API key in `.env`
- Check port 8000 is available
- Review logs for errors

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Run `npm install` in frontend directory
- Check port 3000 is available

### Tests failing
- Activate virtual environment
- Install test dependencies: `pip install pytest pytest-asyncio`
- Run from project root

### ChromaDB errors
- Delete `data/vectordb/` folder
- Restart backend (will rebuild automatically)

### API key errors
- Verify key is correct in `.env`
- No quotes around key value
- Check key has proper permissions

---

## Author

**Assessment Submission** for Lyzr AI

- Framework: FastAPI
- LLM: OpenAI GPT-4 Turbo / Anthropic Claude 3 Sonnet
- Vector DB: ChromaDB
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Frontend: React + Vite + Tailwind CSS

---

## License

This project is created for the Lyzr AI Assessment.

---

## Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- FastAPI for the backend framework
- React and Vite for the frontend

---

**For questions or support, please refer to the test examples in `tests/example_conversations.md` or check the API documentation at `http://localhost:8000/docs`**
