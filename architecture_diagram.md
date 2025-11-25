# Architecture Diagram - Medical Appointment Scheduling Agent

## High-Level System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  • API Clients (cURL, Postman)                                   │  │
│  │  • Python CLI (run.py)                                           │  │
│  │  • Future: React Web UI                                          │  │
│  └────────────────────────────┬───────────────────────────────────────│  │
└─────────────────────────────────┼─────────────────────────────────────┘
                                  │
                    HTTP POST /api/chat
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI BACKEND                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                     API Layer (backend/api/)                      │  │
│  │                                                                   │  │
│  │  • chat.py - Chat endpoint                                       │  │
│  │  • Session management (in-memory dict)                           │  │
│  │  • Request/Response handling                                     │  │
│  │  • CORS middleware                                               │  │
│  └──────────────────────────────┬────────────────────────────────────┘  │
└─────────────────────────────────┼─────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SCHEDULING AGENT (Core)                            │
│                   backend/agent/scheduling_agent.py                     │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃                     CONVERSATION MANAGER                          ┃  │
│  ┃                                                                   ┃  │
│  ┃  1. Intent Detection                                             ┃  │
│  ┃     ├─ FAQ Question? → RAG System                                ┃  │
│  ┃     └─ Scheduling Request? → Tools                               ┃  │
│  ┃                                                                   ┃  │
│  ┃  2. Context Management                                           ┃  │
│  ┃     ├─ Conversation History                                      ┃  │
│  ┃     ├─ Current Phase Tracking                                    ┃  │
│  ┃     └─ Seamless Context Switching                                ┃  │
│  ┃                                                                   ┃  │
│  ┃  3. LLM Integration                                              ┃  │
│  ┃     ├─ OpenAI GPT-4 (Function Calling)                           ┃  │
│  ┃     └─ Anthropic Claude (Tool Use)                               ┃  │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
│                                                                         │
│                    ┌────────────┴────────────┐                          │
│                    │                         │                          │
│                    ▼                         ▼                          │
│    ┌────────────────────────┐   ┌──────────────────────────┐           │
│    │    Tool Dispatcher     │   │    Response Generator    │           │
│    └──────────┬─────────────┘   └──────────────────────────┘           │
└───────────────┼──────────────────────────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Tool 1 │ │  Tool 2 │ │  Tool 3 │
└─────────┘ └─────────┘ └─────────┘
```

## Component Details

### 1. RAG System (FAQ Handling)

```
User Question: "What insurance do you accept?"
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                  FAQ RAG System                              │
│               backend/rag/faq_rag.py                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Step 1: Query Processing                              │ │
│  │  ├─ Receive user question                              │ │
│  │  └─ Generate query embedding                           │ │
│  └──────────────────┬─────────────────────────────────────┘ │
│                     │                                        │
│                     ▼                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Step 2: Semantic Search                               │ │
│  │  ├─ Query vector store (ChromaDB)                      │ │
│  │  ├─ Find top-K similar documents                       │ │
│  │  └─ Return with similarity scores                      │ │
│  └──────────────────┬─────────────────────────────────────┘ │
│                     │                                        │
│                     ▼                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Step 3: Context Compilation                           │ │
│  │  ├─ Extract relevant information                       │ │
│  │  ├─ Format as context                                  │ │
│  │  └─ Add to LLM prompt                                  │ │
│  └──────────────────┬─────────────────────────────────────┘ │
└─────────────────────┼──────────────────────────────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │   LLM Generates │
              │  Natural Answer │
              └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Vector Store (ChromaDB)                         │
│            backend/rag/vector_store.py                       │
│                                                              │
│  Document Storage:                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Doc 1: "accepted_insurance: Blue Cross, Aetna..."    │ │
│  │  Embedding: [0.23, 0.45, -0.12, ...]                  │ │
│  │  Metadata: {category: "insurance", topic: "accepted"} │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  Doc 2: "parking_information: Free parking garage..." │ │
│  │  Embedding: [0.67, -0.34, 0.89, ...]                  │ │
│  │  Metadata: {category: "clinic", topic: "parking"}     │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  ... (100+ documents from clinic_info.json)           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Embedding Model (Sentence Transformers)              │
│            backend/rag/embeddings.py                         │
│                                                              │
│  Model: all-MiniLM-L6-v2                                    │
│  Dimension: 384                                             │
│  Purpose: Convert text to dense vectors                     │
└─────────────────────────────────────────────────────────────┘
```

### 2. Scheduling Tools

```
┌─────────────────────────────────────────────────────────────┐
│              Availability Tool                               │
│         backend/tools/availability_tool.py                   │
│                                                              │
│  Functions:                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  check_availability(date, appointment_type)            │ │
│  │  ├─ Input: "2024-12-05", "consultation"               │ │
│  │  ├─ Process: Query Calendly API                        │ │
│  │  └─ Output: List of available time slots              │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  get_next_available_slots(appointment_type, num_days) │ │
│  │  ├─ Input: "consultation", 7                           │ │
│  │  ├─ Process: Check next 7 days                         │ │
│  │  └─ Output: Available dates with sample slots         │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                Booking Tool                                  │
│           backend/tools/booking_tool.py                      │
│                                                              │
│  Functions:                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  book_appointment(...)                                 │ │
│  │  ├─ Input: All patient info + slot details            │ │
│  │  ├─ Validate: Slot still available                     │ │
│  │  ├─ Create: Appointment record                         │ │
│  │  └─ Output: Confirmation code + booking ID            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  cancel_appointment(booking_id)                        │ │
│  │  get_appointment_details(booking_id)                   │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Mock Calendly API                                  │
│       backend/api/calendly_integration.py                    │
│                                                              │
│  Core Logic:                                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Slot Calculation                                   │ │
│  │     ├─ Load working hours from schedule.json           │ │
│  │     ├─ Generate 15-min slots                           │ │
│  │     ├─ Exclude lunch breaks                            │ │
│  │     └─ Skip blocked dates                              │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  2. Availability Checking                              │ │
│  │     ├─ Load existing appointments                      │ │
│  │     ├─ Check for conflicts                             │ │
│  │     ├─ Ensure contiguous slots for duration            │ │
│  │     └─ Return available slots                          │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  3. Booking                                            │ │
│  │     ├─ Validate slot availability                      │ │
│  │     ├─ Generate booking ID & confirmation code         │ │
│  │     ├─ Save to appointments.json                       │ │
│  │     └─ Return confirmation                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3. Conversation Flow State Machine

```
┌──────────────────────────────────────────────────────────────┐
│                   Conversation Phases                         │
│                                                              │
│                      [START]                                 │
│                         │                                    │
│                         ▼                                    │
│              ┌───────────────────┐                           │
│              │  PHASE 1: GREETING│                           │
│              │  & UNDERSTANDING  │                           │
│              └─────────┬─────────┘                           │
│                        │                                     │
│              Ask: Reason for visit?                          │
│                        │                                     │
│                        ▼                                     │
│              ┌───────────────────┐                           │
│         ┌────│  Determine Appt   │────┐                      │
│         │    │      Type          │    │                     │
│         │    └───────────────────┘    │                      │
│         │                              │                     │
│    Consultation  Follow-up   Physical  Specialist            │
│         │                              │                     │
│         └──────────────┬───────────────┘                      │
│                        │                                     │
│              Ask: Date/Time preference?                      │
│                        │                                     │
│                        ▼                                     │
│              ┌───────────────────┐                           │
│              │ PHASE 2: SLOT     │                           │
│              │ RECOMMENDATION    │                           │
│              └─────────┬─────────┘                           │
│                        │                                     │
│         Call: check_availability() or                        │
│               get_next_available_slots()                     │
│                        │                                     │
│                        ▼                                     │
│              Present 3-5 slots                               │
│                        │                                     │
│              ┌─────────┴─────────┐                           │
│              │                   │                           │
│         Slot selected      No slots work                     │
│              │                   │                           │
│              │            Offer alternatives                 │
│              │                   │                           │
│              └─────────┬─────────┘                           │
│                        │                                     │
│                        ▼                                     │
│              ┌───────────────────┐                           │
│              │ PHASE 3: BOOKING  │                           │
│              │  CONFIRMATION     │                           │
│              └─────────┬─────────┘                           │
│                        │                                     │
│            Collect: Name, Phone, Email                       │
│                        │                                     │
│                        ▼                                     │
│              Summarize & Confirm                             │
│                        │                                     │
│                  User confirms?                              │
│                        │                                     │
│                 ┌──────┴──────┐                              │
│                 │             │                              │
│               Yes            No                              │
│                 │             │                              │
│         book_appointment()  Retry                            │
│                 │                                            │
│                 ▼                                            │
│         [BOOKING COMPLETE]                                   │
│                                                              │
│  ═══════════════════════════════════════════════════════    │
│                                                              │
│         Context Switching (Anytime):                         │
│                                                              │
│         FAQ Question Detected                                │
│                 │                                            │
│                 ▼                                            │
│         Pause current phase                                  │
│                 │                                            │
│                 ▼                                            │
│         Query RAG System                                     │
│                 │                                            │
│                 ▼                                            │
│         Provide Answer                                       │
│                 │                                            │
│                 ▼                                            │
│         Resume previous phase                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4. LLM Tool Calling Flow

```
┌─────────────────────────────────────────────────────────────┐
│          Tool Calling Mechanism                              │
│                                                              │
│  User Message:                                              │
│  "I need an appointment tomorrow afternoon"                 │
│                 │                                           │
│                 ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LLM Analysis                                        │  │
│  │  ├─ Intent: Schedule appointment                     │  │
│  │  ├─ Missing: appointment_type                        │  │
│  │  ├─ Has: date preference (tomorrow)                  │  │
│  │  └─ Has: time preference (afternoon)                 │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│              Ask clarifying question                        │
│              "What brings you in?"                          │
│                         │                                   │
│                         ▼                                   │
│  User: "Headaches"                                         │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LLM Decision: Call Tool                             │  │
│  │  Tool: get_next_available_slots                      │  │
│  │  Params: {                                           │  │
│  │    "appointment_type": "consultation",               │  │
│  │    "num_days": 1                                     │  │
│  │  }                                                   │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tool Execution                                      │  │
│  │  Returns: {                                          │  │
│  │    "available_dates": [                              │  │
│  │      {                                               │  │
│  │        "date": "2024-12-05",                         │  │
│  │        "sample_slots": [                             │  │
│  │          {"start_time": "14:00", ...},               │  │
│  │          {"start_time": "15:30", ...}                │  │
│  │        ]                                             │  │
│  │      }                                               │  │
│  │    ]                                                 │  │
│  │  }                                                   │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LLM Generates Natural Response                      │  │
│  │  "I have these afternoon slots available tomorrow:  │  │
│  │   - 2:00 PM                                          │  │
│  │   - 3:30 PM                                          │  │
│  │   Which works best for you?"                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 5. Data Flow

```
                    ┌─────────────────┐
                    │  User Request   │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   FastAPI Endpoint       │
              │   Validates Request      │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │  Scheduling Agent        │
              │  - Parse intent          │
              │  - Check if FAQ          │
              └──────────┬───────────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
           ▼                           ▼
    ┌─────────────┐            ┌─────────────┐
    │  FAQ Query  │            │  Tool Call  │
    └──────┬──────┘            └──────┬──────┘
           │                          │
           ▼                          ▼
    ┌─────────────┐            ┌─────────────┐
    │ RAG System  │            │ Mock API    │
    │ ├─Query Vec │            │ ├─Check DB  │
    │ ├─Get Docs  │            │ ├─Calculate │
    │ └─Format    │            │ └─Return    │
    └──────┬──────┘            └──────┬──────┘
           │                          │
           └─────────────┬─────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │  LLM Generates Response  │
              │  - Natural language      │
              │  - Context-aware         │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────────┐
              │  FastAPI Response        │
              │  - Message               │
              │  - Updated History       │
              │  - Metadata              │
              └──────────┬───────────────┘
                         │
                         ▼
                    ┌─────────────────┐
                    │  User Receives  │
                    └─────────────────┘
```

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### LLM Integration
- **OpenAI GPT-4**: Function calling
- **Anthropic Claude**: Tool use
- **Async I/O**: Non-blocking requests

### RAG System
- **ChromaDB**: Vector database (persistent)
- **Sentence Transformers**: Embeddings (all-MiniLM-L6-v2)
- **Semantic search**: Cosine similarity

### Data Storage
- **JSON Files**: Clinic info, schedule, appointments
- **In-memory**: Session storage (dev)
- **Future**: PostgreSQL + Redis

### Testing
- **Pytest**: Test framework
- **Pytest-asyncio**: Async testing

## Deployment Architecture (Production)

```
                    ┌─────────────┐
                    │   Internet  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  CDN / WAF  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Load Balancer│
                    └──────┬──────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
  ┌─────────────┐                    ┌─────────────┐
  │  FastAPI    │                    │  FastAPI    │
  │  Instance 1 │                    │  Instance 2 │
  └──────┬──────┘                    └──────┬──────┘
         │                                   │
         └─────────────────┬─────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
  ┌───────────┐     ┌───────────┐    ┌───────────┐
  │PostgreSQL │     │   Redis   │    │  ChromaDB │
  │(Appts DB) │     │(Sessions) │    │(Vectors)  │
  └───────────┘     └───────────┘    └───────────┘
```

This architecture provides scalability, reliability, and performance for production use.

