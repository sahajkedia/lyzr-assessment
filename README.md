# Medical Appointment Scheduling Agent

An intelligent conversational AI agent that helps patients schedule medical appointments through natural conversation, while seamlessly answering frequently asked questions using RAG (Retrieval Augmented Generation).

## Overview

This project implements a complete medical appointment scheduling system with:

- **Natural Conversation Flow**: Warm, empathetic dialogue that understands patient needs
- **Intelligent Scheduling**: Smart appointment booking with real-time availability checking
- **RAG-Powered FAQ System**: Accurate answers from clinic knowledge base with no hallucinations
- **Seamless Context Switching**: Smoothly transitions between FAQ and scheduling contexts
- **Multi-Appointment Types**: Supports consultation (30min), follow-up (15min), physical exam (45min), specialist (60min)
- **Edge Case Handling**: Gracefully manages ambiguous inputs, conflicts, and errors
- **Full-Stack Implementation**: React frontend with FastAPI backend

## Tech Stack

**Backend:**

- FastAPI (Python 3.10+)
- LLM: OpenAI GPT-4 Turbo / Anthropic Claude 3 Sonnet
- Vector Database: ChromaDB (persistent)
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Calendar API: Mock Calendly Implementation

**Frontend:**

- React 18 with Vite
- Tailwind CSS
- Axios for API calls

**Testing:**

- Pytest with pytest-asyncio
- 70+ tests, fully mocked (no external dependencies)

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 16+ and npm (for frontend)
- OpenAI API key or Anthropic API key

### Installation

#### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd lyzr-assessment-1

# Backend setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (optional)
cd frontend
npm install
cd ..
```

#### 2. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required Configuration:**

```env
# LLM Configuration (REQUIRED)
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

**For Anthropic Claude instead of OpenAI:**

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### 3. Calendly API Setup (Optional)

**This system uses a Mock Calendly implementation by default** - no API key required.

The mock implementation:

- Stores appointments locally in `data/appointments.json`
- Uses doctor schedule from `data/doctor_schedule.json`
- Provides full booking, rescheduling, and cancellation support
- Works completely offline

If you want to use **Real Calendly API** instead:

1. Sign up at https://calendly.com
2. Get API token from https://calendly.com/integrations/api_webhooks
3. Add to `.env`:
   ```env
   CALENDLY_API_KEY=your_calendly_api_key
   CALENDLY_USER_URL=https://calendly.com/your-username
   ```

The system will automatically use real Calendly if configured, otherwise falls back to mock.

### Running the Application

#### Option 1: Start Everything (Recommended)

```bash
./start.sh
```

This starts:

- Backend API on http://localhost:8000
- Frontend UI on http://localhost:3000

#### Option 2: Backend Only

```bash
python backend/main.py
```

Or using uvicorn:

```bash
uvicorn backend.main:app --reload --port 8000
```

Access API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Option 3: Interactive CLI

```bash
python run.py
```

### Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agent.py -v
```

All tests are fully mocked - no API keys or external services needed.

---

## System Design

### Agent Conversation Flow

The agent follows a three-phase conversation flow:

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: Understanding Needs                            │
│ • Greet patient warmly                                  │
│ • Understand reason for visit                           │
│ • Determine appropriate appointment type                │
│ • Ask about date/time preferences                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: Slot Recommendation                            │
│ • Call availability tool                                │
│ • Show 3-5 available slots based on preferences         │
│ • Explain why slots are suggested                       │
│ • Handle "none of these work" gracefully                │
│ • Offer alternative dates/times                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: Booking Confirmation                           │
│ • Collect patient information (name, email, phone)      │
│ • Confirm all details before booking                    │
│ • Call booking tool                                     │
│ • Provide confirmation details                          │
└─────────────────────────────────────────────────────────┘
```

**Context Switching:** The agent can seamlessly switch between scheduling and FAQ answering:

```
User: "I want to book an appointment"
Agent: "What brings you in today?"
User: "What insurance do you accept?"  ← FAQ interruption
Agent: [Retrieves from knowledge base]
       "We accept Blue Cross, Aetna, Cigna..."
       "Now, what brings you in today?"  ← Resumes scheduling
```

### Calendly Integration Approach

**Mock Implementation (Default):**

The system uses a pure local implementation:

1. **Doctor Schedule** (`data/doctor_schedule.json`):

   - Working hours per day (e.g., 9:00 AM - 5:00 PM)
   - Lunch breaks
   - Blocked dates (holidays)

2. **Slot Calculation:**

   - Generate 15-minute intervals within working hours
   - Exclude lunch breaks
   - Check against existing appointments
   - Match appointment duration requirements

3. **Appointment Storage** (`data/appointments.json`):

   - JSON file stores all bookings
   - Includes booking ID, confirmation code, patient info
   - Checked for conflicts before booking

4. **Endpoints Provided:**
   - `GET /api/calendly/availability` - Check specific date
   - `GET /api/calendly/availability/next-dates` - Get upcoming availability
   - `POST /api/calendly/book` - Create appointment
   - `POST /api/calendly/reschedule` - Move appointment
   - `POST /api/calendly/cancel` - Cancel appointment

**Real Calendly Integration (Optional):**

If Calendly API key is provided in `.env`, the system uses:

- `GET /event_types` - Get appointment types
- `GET /event_types/{uuid}/available_times` - Get availability
- `POST /scheduled_events` - Create booking

The system automatically falls back to mock if real API fails.

### RAG Pipeline for FAQs

**Knowledge Base:**

Clinic information stored in `data/clinic_info.json`:

- Clinic details (location, hours, parking, directions)
- Insurance & billing (accepted providers, payment methods)
- Visit preparation (documents to bring, first visit procedures)
- Policies (cancellation, late arrival, COVID-19 protocols)

**RAG Process:**

1. **Embedding Generation:**

   - Uses Sentence Transformers (all-MiniLM-L6-v2)
   - 384-dimensional embeddings
   - Generated once at startup, stored in ChromaDB

2. **Query Processing:**

   - User question embedded using same model
   - Semantic search in vector store
   - Top 3-5 most relevant documents retrieved

3. **Answer Generation:**

   - Retrieved context provided to LLM
   - LLM generates natural language answer
   - Grounded in knowledge base (no hallucinations)

4. **Context Retention:**
   - Conversation history maintained
   - Can return to scheduling after FAQ
   - Handles multiple FAQs in sequence

**Example:**

```
User: "What insurance do you accept?"
    ↓
Semantic Search: Find insurance-related docs
    ↓
Retrieved: "Accepted insurance providers include..."
    ↓
LLM: "We accept Blue Cross Blue Shield, Aetna, Cigna,
      UnitedHealthcare, and Medicare..."
```

### Tool Calling Strategy

The system uses **native LLM function calling** (not ReAct prompting):

**Available Tools:**

1. **`check_availability(date, appointment_type)`**

   - Checks specific date for available slots
   - Returns list of time slots with availability status

2. **`get_next_available_slots(appointment_type, num_days=7)`**

   - Gets upcoming availability across multiple days
   - Returns dates with sample available slots

3. **`book_appointment(appointment_type, date, start_time, patient_name, patient_email, patient_phone, reason)`**

   - Books appointment after confirmation
   - Validates slot availability
   - Generates booking ID and confirmation code

4. **`cancel_appointment(booking_id)`**

   - Cancels existing appointment
   - Updates appointment status

5. **`reschedule_appointment(booking_id, new_date, new_start_time)`**
   - Moves appointment to new date/time
   - Preserves booking ID and confirmation code

**Tool Execution Flow:**

```
User: "I need an appointment tomorrow afternoon"
    ↓
LLM: Needs appointment_type, has date/time preference
    ↓
LLM: Asks "What brings you in today?"
    ↓
User: "Headaches"
    ↓
LLM: Calls get_next_available_slots(
        appointment_type="consultation",
        num_days=1
     )
    ↓
Tool: Returns afternoon slots for tomorrow
    ↓
LLM: "I have these afternoon slots: 2:00 PM, 3:30 PM..."
```

**Benefits over ReAct:**

- More reliable tool execution
- Automatic parameter validation
- Better multi-step reasoning
- Native error handling

---

## Scheduling Logic

### How Available Slots Are Determined

#### 1. Load Doctor's Schedule

From `data/doctor_schedule.json`:

```json
{
  "working_hours": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"},
    ...
  },
  "lunch_break": {"start": "12:00", "end": "13:00"},
  "blocked_dates": ["2024-12-25", "2024-01-01"]
}
```

#### 2. Validate Date

Check that requested date:

- ✓ Is not in the past
- ✓ Is not a weekend (unless configured)
- ✓ Is not a blocked date (holidays)
- ✓ Is within working hours

#### 3. Generate Time Slots

- Create 15-minute intervals from opening to closing
- Exclude lunch break periods
- Example: 9:00, 9:15, 9:30, 9:45, 10:00, 10:15...

#### 4. Check Existing Appointments

```python
# Load appointments from data/appointments.json
existing_appointments = load_appointments_for_date(target_date)

# Mark slots as unavailable if they conflict
for appointment in existing_appointments:
    mark_slots_unavailable(
        appointment.start_time,
        appointment.duration
    )
```

#### 5. Match Appointment Duration

Find contiguous available slots matching appointment type:

| Type                    | Duration | Slots Needed        |
| ----------------------- | -------- | ------------------- |
| Follow-up               | 15 min   | 1 slot              |
| General Consultation    | 30 min   | 2 consecutive slots |
| Physical Exam           | 45 min   | 3 consecutive slots |
| Specialist Consultation | 60 min   | 4 consecutive slots |

**Algorithm:**

```python
def find_available_slots(date, appointment_type):
    slots_needed = get_slots_for_type(appointment_type)
    all_slots = generate_15min_slots(date)

    available_blocks = []
    for i in range(len(all_slots) - slots_needed + 1):
        block = all_slots[i:i + slots_needed]
        if all(slot.available for slot in block):
            available_blocks.append(block[0].start_time)

    return available_blocks
```

### Appointment Type Handling

**Type Determination:**

The LLM determines appropriate appointment type based on patient's reason:

```
Reason                          → Recommended Type
─────────────────────────────────────────────────────
"Headache", "Cold", "Flu"       → General Consultation (30 min)
"Follow up on test results"     → Follow-up (15 min)
"Annual physical", "Checkup"    → Physical Exam (45 min)
"Heart specialist", "Complex"   → Specialist Consultation (60 min)
```

**Duration Enforcement:**

- System ensures slot has sufficient consecutive availability
- Automatically blocks out full duration when booking
- Prevents overlapping appointments

### Conflict Prevention

#### 1. Real-time Availability Checking

```python
def book_appointment(slot_info):
    # Double-check availability before booking
    if not is_slot_still_available(slot_info.date, slot_info.time):
        raise ConflictError("Slot no longer available")

    # Proceed with booking
    create_appointment(slot_info)
```

#### 2. Atomic Operations

- Read appointment file
- Check for conflicts
- Write new appointment
- All in single operation (would use database transactions in production)

#### 3. Validation Layers

```
User Request
    ↓
Frontend Validation (basic checks)
    ↓
API Validation (Pydantic schemas)
    ↓
Business Logic (slot availability check)
    ↓
Data Layer (consistency checks)
```

#### 4. Edge Cases Handled

- **Date in past**: Politely corrects, suggests future dates
- **Outside business hours**: Explains hours, suggests alternatives
- **Slot taken during booking**: Detects conflict, offers alternatives
- **No consecutive slots**: Finds next available block
- **Weekend booking**: Suggests weekday alternatives

---

## Testing

### Test Suite Overview

The project includes 70+ comprehensive tests covering all aspects:

- `tests/test_agent.py` - Agent conversation tests
- `tests/test_tools.py` - Tool function tests
- `tests/test_api.py` - API endpoint tests
- `tests/test_models.py` - Schema validation tests

All tests are **fully mocked** - no external API calls or services required.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agent.py -v

# Run specific test
pytest tests/test_agent.py::test_greeting -v
```

### Example Conversations

#### 1. Successful Booking

```
User: I need to see the doctor

Agent: I'd be happy to help you schedule an appointment! What's the main
reason for your visit today?

User: I've been having headaches

Agent: I understand. For persistent headaches, I'd recommend a general
consultation (30 minutes) where the doctor can assess your symptoms. Does
that sound appropriate?

User: Yes, that works

Agent: Perfect. When would you like to come in? Do you have a preference
for morning or afternoon appointments?

User: Afternoon if possible, sometime this week

Agent: Let me check our afternoon availability this week. I have these
options:
- Tomorrow (Nov 27) at 2:00 PM
- Wednesday (Nov 28) at 3:30 PM
- Thursday (Nov 29) at 1:00 PM

Which works best for you?

User: Wednesday at 3:30

Agent: Excellent! Wednesday, November 28th at 3:30 PM for a 30-minute
consultation. Before I confirm, I'll need:
- Your full name?
- Best phone number to reach you?
- Email address for confirmation?

User: John Doe, 555-123-4567, john@example.com

Agent: Perfect! I've confirmed your appointment for Wednesday, November
28th at 3:30 PM. You'll receive a confirmation email at john@example.com.
Your confirmation code is ABC123.

Is there anything else you'd like to know about your visit?
```

#### 2. FAQ During Booking (Context Switching)

```
User: I want to book an appointment

Agent: I'd be happy to help! What brings you in today?

User: Actually, first - what insurance do you accept?

Agent: Great question! We accept most major insurance providers including
Blue Cross Blue Shield, Aetna, Cigna, UnitedHealthcare, and Medicare. We
also accept self-pay patients. Do you have insurance with one of these
providers?

User: Yes, I have Blue Cross. I'd like to schedule a checkup

Agent: Perfect, we accept Blue Cross Blue Shield. For a checkup, I'd
recommend our Physical Exam (45 minutes) which includes a comprehensive
examination. Would you like to proceed with that?

[Continues with scheduling...]
```

#### 3. No Available Slots

```
User: Can I see the doctor today?

Agent: I understand you'd like to be seen today. Unfortunately, we don't
have any available appointments for today. However, I have several options
for tomorrow:
- 9:00 AM
- 11:30 AM
- 2:00 PM

Would any of these work? If you need urgent care, I can also provide
information about our walk-in clinic hours.

User: Is there a waitlist for today?

Agent: We don't have a formal waitlist, but I'd recommend calling our
office at (555) 123-4567 as they sometimes have last-minute cancellations.
For planned appointments, would you like me to book you for tomorrow?
```

#### 4. Ambiguous Time References

```
User: I need an appointment tomorrow morning

Agent: I can help with that! I have these morning slots available:
- 9:00 AM
- 10:30 AM
- 11:00 AM

Which time works best for you?

User: Around 10

Agent: Just to clarify, would you prefer the 10:30 AM slot?

User: Yes, 10:30 works

Agent: Great! Let me confirm...
```

#### 5. User Changes Mind

```
User: I need a physical exam

Agent: I can schedule a Physical Exam (45 minutes) for you. When would
you like to come in?

User: Actually, I just need a quick follow-up on my blood pressure

Agent: No problem! A follow-up appointment (15 minutes) is perfect for
that. This gives you time to check in with the doctor about your blood
pressure. When would you like to come in?

[Continues with new appointment type...]
```

### Edge Cases Covered

#### Date/Time Issues

- ✓ Past dates - Politely corrects, suggests future
- ✓ Invalid dates - Validates and requests correction
- ✓ Outside business hours - Explains hours, suggests alternatives
- ✓ "Tomorrow morning" - Clarifies specific times
- ✓ "Around 3" - Confirms AM or PM
- ✓ Weekend requests - Suggests weekday alternatives

#### Availability Issues

- ✓ No slots available - Offers alternative dates, provides phone number
- ✓ All afternoon slots booked - Suggests mornings or next day
- ✓ Slot taken during booking - Detects conflict, offers alternatives
- ✓ Only partial time available - Finds complete blocks

#### User Behavior

- ✓ Changes mind mid-booking - Gracefully restarts
- ✓ Asks multiple FAQs - Answers all, maintains context
- ✓ Provides incomplete information - Politely asks for missing details
- ✓ Ambiguous responses - Seeks clarification
- ✓ Interrupts booking with FAQ - Switches context, returns to booking

#### System Errors

- ✓ Invalid appointment type - Suggests valid types
- ✓ Malformed input - Validates and requests correction
- ✓ API failures - Fallback mechanisms with clear communication
- ✓ Network timeout - Retry logic with user notification

---

## Project Structure

```
lyzr-assessment-1/
├── README.md                          # This file
├── architecture_diagram.png           # System architecture visual
├── .env.example                       # Environment template
├── requirements.txt                   # Python dependencies
├── start.sh                           # Convenience startup script
│
├── backend/
│   ├── main.py                        # FastAPI application entry
│   ├── agent/
│   │   ├── scheduling_agent.py        # Main agent with LLM integration
│   │   └── prompts.py                 # System prompts
│   ├── api/
│   │   ├── chat.py                    # Chat endpoints
│   │   ├── calendly_integration.py    # Mock Calendly implementation
│   │   ├── calendly_service.py        # Calendly service layer
│   │   └── calendly.py                # Calendly API router
│   ├── rag/
│   │   ├── faq_rag.py                 # RAG system for FAQs
│   │   ├── embeddings.py              # Embedding model wrapper
│   │   └── vector_store.py            # ChromaDB wrapper
│   ├── tools/
│   │   ├── availability_tool.py       # Availability checking
│   │   └── booking_tool.py            # Booking operations
│   └── models/
│       └── schemas.py                 # Pydantic models
│
├── frontend/                          # React application
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   └── AppointmentConfirmation.jsx
│   │   └── api/
│   │       └── chatApi.js
│   └── package.json
│
├── data/
│   ├── clinic_info.json               # FAQ knowledge base
│   ├── doctor_schedule.json           # Doctor working hours
│   ├── appointments.json              # Booked appointments
│   └── vectordb/                      # ChromaDB storage
│
└── tests/
    ├── test_agent.py                  # Agent tests
    ├── test_tools.py                  # Tool tests
    ├── test_api.py                    # API tests
    └── test_models.py                 # Schema tests
```

---

## API Documentation

**Interactive Documentation:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Key Endpoints:**

- `POST /api/chat` - Main conversation endpoint
- `GET /api/calendly/availability` - Check slot availability
- `POST /api/calendly/book` - Book appointment
- `GET /api/health` - Health check

---

## License

This project is created for the Lyzr AI Assessment.

---

**For more detailed examples, see `tests/example_conversations.md`**
