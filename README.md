# Medical Appointment Scheduling Agent

An intelligent conversational AI agent that helps patients schedule medical appointments through natural conversation, while seamlessly answering frequently asked questions using RAG (Retrieval Augmented Generation).

## 🌟 Features

### Core Capabilities

- **Natural Conversation Flow**: Warm, empathetic dialogue that feels human
- **Intelligent Scheduling**: Smart appointment booking with availability checking
- **RAG-Powered FAQ**: Accurate answers using clinic knowledge base
- **Seamless Context Switching**: Smoothly handles FAQ questions during booking
- **Multi-Appointment Types**: Supports 4 appointment types with different durations
- **Edge Case Handling**: Gracefully manages ambiguous inputs, conflicts, and errors

### Appointment Types

| Type                    | Duration | Use Case                                               |
| ----------------------- | -------- | ------------------------------------------------------ |
| General Consultation    | 30 min   | Common health concerns, illness, injuries              |
| Follow-up               | 15 min   | Review results, check progress, medication adjustments |
| Physical Exam           | 45 min   | Annual physicals, comprehensive examinations           |
| Specialist Consultation | 60 min   | Complex conditions, specialized care                   |

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User/Patient                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Chat Message
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Chat Endpoint (/api/chat)               │  │
│  └───────────────────────┬───────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Scheduling Agent                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              LLM (GPT-4 / Claude)                    │   │
│  │         - Conversation Management                     │   │
│  │         - Intent Understanding                        │   │
│  │         - Tool Selection                              │   │
│  └──────────────────┬──────────────┬────────────────────┘   │
└─────────────────────┼──────────────┼─────────────────────────┘
                      │              │
          ┌───────────┴──┐      ┌────┴──────────┐
          │              │      │                │
          ▼              ▼      ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   FAQ RAG    │  │ Availability │  │ Booking Tool     │
│              │  │    Tool      │  │                  │
│ ┌──────────┐ │  │              │  │ - Book Appt     │
│ │ Vector   │ │  │ - Check      │  │ - Cancel Appt   │
│ │ Store    │ │  │   Slots      │  │ - Get Details   │
│ │(ChromaDB)│ │  │ - Get Next   │  │                  │
│ └──────────┘ │  │   Available  │  │                  │
│              │  │              │  │                  │
│ ┌──────────┐ │  └──────┬───────┘  └────────┬─────────┘
│ │Embeddings│ │         │                   │
│ │ Model    │ │         │                   │
│ └──────────┘ │         ▼                   ▼
└──────┬───────┘  ┌─────────────────────────────────┐
       │          │   Mock Calendly API              │
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
│                                         │
│  - Clinic Details (location, hours)    │
│  - Insurance & Billing                 │
│  - Visit Preparation                   │
│  - Policies (cancellation, COVID)      │
│  - Appointment Types                   │
└─────────────────────────────────────────┘
```

### Conversation Flow

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

### Tool Calling Flow

```
User: "I need an appointment tomorrow afternoon"
    │
    ▼
LLM processes request
    │
    ├─► Identifies: appointment_type needed
    │   Identifies: "tomorrow afternoon" = date + time preference
    │
    ▼
LLM calls: get_next_available_slots(appointment_type="consultation")
    │
    ▼
Tool executes → Returns available slots
    │
    ▼
LLM receives results
    │
    ▼
LLM generates natural response with slot options
    │
    ▼
User selects slot
    │
    ▼
LLM calls: book_appointment(...all required params...)
    │
    ▼
Booking confirmed → Response with confirmation details
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (or Anthropic API key)
- Git

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd lyzr-assessment-1
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=your_actual_api_key_here
```

For Anthropic Claude:

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=your_actual_api_key_here
```

5. **Initialize the knowledge base**

The FAQ knowledge base will be automatically initialized on first run. The system will:

- Load clinic information from `data/clinic_info.json`
- Generate embeddings using Sentence Transformers
- Store in ChromaDB vector database

### Running the Application

**Option 1: Start Everything (Recommended)**

Use the convenience script to start both backend and frontend:

```bash
./start.sh
```

This will start:

- Backend API on `http://localhost:8000`
- Frontend UI on `http://localhost:3000`

**Option 2: Start Backend Only**

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

**Access the API documentation:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Option 3: Start Frontend Only**

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:3000`

### Testing the Agent

**Option 1: Web UI (Recommended)**

Open your browser and go to `http://localhost:3000`

This provides a beautiful, professional chat interface where you can:

- Have natural conversations with the AI
- Schedule appointments interactively
- Get instant answers to FAQs
- See real-time availability
- Complete full booking flow

**Option 2: Interactive CLI**

```bash
python run.py
```

**Option 3: API directly**

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to schedule an appointment",
    "conversation_history": []
  }'
```

**Option 4: Using Python**

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "I need to schedule an appointment",
        "conversation_history": []
    }
)

print(response.json()["message"])
```

**Option 5: Run test suite**

```bash
pytest tests/test_agent.py -v
```

Or run the example script:

```bash
python tests/test_agent.py
```

## 📋 API Endpoints

### POST /api/chat

Main chat endpoint for conversational interaction.

**Request:**

```json
{
	"message": "I need to see the doctor",
	"conversation_history": [
		{ "role": "user", "content": "Previous message" },
		{ "role": "assistant", "content": "Previous response" }
	],
	"session_id": "optional-session-id"
}
```

**Response:**

```json
{
  "message": "I'd be happy to help you schedule an appointment! What brings you in today?",
  "conversation_history": [...],
  "session_id": "generated-session-id",
  "metadata": {
    "iterations": 1,
    "used_tools": false
  }
}
```

### GET /api/chat/

Get session data.

### DELETE /api/chat/

Clear a chat session.

### GET /health

Health check endpoint.

## 🎯 Scheduling Logic

### How Available Slots Are Determined

1. **Load Doctor's Schedule**: Working hours and lunch breaks from `data/doctor_schedule.json`
2. **Check Date Validity**:
   - Not in the past
   - Not a blocked date (holidays)
   - Within working hours
3. **Calculate Time Slots**: Based on 15-minute intervals
4. **Check Existing Appointments**: Prevent double-booking
5. **Match Appointment Type**: Ensure sufficient contiguous slots

### Appointment Type Handling

Each appointment type requires a specific number of 15-minute slots:

- **General Consultation**: 2 slots (30 min)
- **Follow-up**: 1 slot (15 min)
- **Physical Exam**: 3 slots (45 min)
- **Specialist Consultation**: 4 slots (60 min)

The system ensures contiguous availability for the required duration.

### Conflict Prevention

- Real-time availability checking
- Slot reservation during booking
- Concurrent booking protection (would use database locks in production)
- Buffer time handling (configurable)

## 🧠 RAG Pipeline for FAQs

### Knowledge Base Structure

The clinic knowledge base (`data/clinic_info.json`) contains:

- **Clinic Details**: Location, hours, parking, directions
- **Insurance & Billing**: Accepted providers, payment methods, costs
- **Visit Preparation**: Required documents, what to bring
- **Policies**: Cancellation, late arrival, COVID-19 protocols
- **Appointment Types**: Descriptions and use cases

### RAG Process

1. **Document Preparation**:

   - Flatten nested JSON structure
   - Create text chunks with metadata
   - Generate embeddings using Sentence Transformers

2. **Vector Storage**:

   - Store in ChromaDB persistent database
   - Enable semantic search

3. **Query Process**:

   - User asks FAQ question
   - Generate query embedding
   - Semantic search for top-K relevant documents
   - Provide context to LLM

4. **Answer Generation**:

   - LLM generates answer using retrieved context
   - Ensures accuracy (no hallucination)
   - Returns to scheduling context if applicable

### Context Switching

The agent seamlessly switches between scheduling and FAQ:

```
User: "I want to book an appointment"
Agent: "I'd be happy to help! What brings you in?"

User: "What insurance do you accept?"  ← FAQ during scheduling
Agent: [Answers using RAG, then returns to scheduling]

User: "I have Blue Cross, I need a checkup"  ← Back to scheduling
Agent: [Continues scheduling flow]
```

## 🛡️ Edge Case Handling

### No Slots Available

```python
Response: "I don't have availability for [date], but I have these alternatives:
- [Alternative 1]
- [Alternative 2]
You can also call our office at [phone] for urgent matters."
```

### Ambiguous Time References

- "Tomorrow morning" → Clarifies specific times (9 AM - 12 PM)
- "Around 3" → Confirms AM or PM
- "Next week" → Asks for specific day

### Invalid Input

- Past dates → Politely corrects, asks for future date
- Non-existent dates → Validates and requests correction
- Outside business hours → Explains hours, suggests available times

### User Changes Mind

- Gracefully restarts conversation
- Maintains context where appropriate
- Never shows frustration

### API Failures

- Calendly unavailable → Fallback message with phone number
- Network timeout → Retry logic with clear communication
- Graceful degradation → Always provides helpful alternative

## 🧪 Testing

### Test Coverage

The test suite (`tests/test_agent.py`) covers:

1. **Basic Interactions**

   - Greeting
   - Intent understanding

2. **FAQ Handling**

   - Insurance questions
   - Parking information
   - Hours of operation
   - Policies

3. **Scheduling Flow**

   - Full booking process
   - Slot selection
   - Information collection
   - Confirmation

4. **Context Switching**

   - FAQ during booking
   - Return to scheduling
   - Multiple FAQs

5. **Edge Cases**

   - Past dates
   - Ambiguous times
   - No availability
   - User changes mind

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_agent.py::test_greeting -v

# Run with output
python tests/test_agent.py
```

### Example Conversations

See `tests/example_conversations.md` for 10+ detailed conversation examples demonstrating:

- Successful bookings
- FAQ handling
- Context switching
- Edge cases
- Error scenarios

## 📊 System Design Decisions

### LLM Provider Support

The system supports multiple LLM providers:

- **OpenAI**: GPT-4 Turbo (recommended), GPT-4, GPT-3.5-Turbo
- **Anthropic**: Claude 3 Sonnet, Claude 3 Opus

Switch providers by changing `.env`:

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
```

### Tool Calling Strategy

**Function Calling** (not ReAct):

- Uses native function calling (OpenAI) or tool use (Anthropic)
- More reliable than ReAct prompting
- Better handling of multi-step processes
- Automatic parameter validation

**Available Tools**:

1. `check_availability`: Check specific date
2. `get_next_available_slots`: Get upcoming slots
3. `book_appointment`: Book after confirmation

### Calendly Integration

The system now supports **real Calendly API integration** with automatic fallback to mock:

**Operating Modes:**
| Mode | Description |
|------|-------------|
| `REAL` | Connected to Calendly API - all bookings sync with your Calendly account |
| `MOCK` | No API key configured - uses local mock implementation |
| `FALLBACK` | API failed - automatically falls back to mock for uninterrupted service |

**Setup Real Calendly:**

1. Get your Personal Access Token from [Calendly Integrations](https://calendly.com/integrations/api_webhooks)
2. Add to your `.env`:

```env
CALENDLY_API_KEY=your_personal_access_token_here
```

3. The system will automatically:
   - Connect to Calendly API on startup
   - Map your event types (Consultation, Follow-up, Physical, Specialist)
   - Sync appointments to your Calendly calendar
   - Fall back to mock if API is unavailable

**Check Status:**
```bash
curl http://localhost:8000/api/calendly/status
# Returns: { "mode": "real", "event_types_mapped": 4, ... }
```

**Features with Real Calendly:**
- ✅ Real-time availability from your Calendly calendar
- ✅ Bookings appear in your Calendly dashboard
- ✅ Automatic event type mapping
- ✅ Cancellation syncs to Calendly
- ✅ Local backup of all appointments

### Session Management

**Current**: In-memory dictionary (development)
**Production**: Use Redis or database with session expiration

## 🔒 Security & Privacy

- HIPAA considerations (would add encryption, audit logs in production)
- No patient data stored in logs
- Environment variables for sensitive data
- CORS configured (update for production domains)
- Input validation on all endpoints

## 🎨 Frontend Features

The React frontend provides a professional, user-friendly interface:

### ✨ Key Features

- **Modern UI/UX**: Beautiful, medical-themed design with Tailwind CSS
- **Real-time Chat**: Instant messaging with the AI assistant
- **Quick Suggestions**: One-click common questions
- **Typing Indicators**: Visual feedback during processing
- **Connection Status**: Health monitoring with auto-retry
- **Session Management**: Clear chat and restart conversations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Professional transitions and effects
- **Error Handling**: Graceful error messages and recovery

### 🎯 User Experience

- Clean, intuitive interface
- Medical/healthcare themed colors (blue & green)
- Clear visual distinction between user and agent messages
- Timestamps for all messages
- Tool usage metadata display
- Accessibility considerations

### 🚀 Technologies

- React 18 with Hooks
- Vite for fast development
- Tailwind CSS for styling
- Axios for API calls
- Lucide React for icons

## 🚧 Future Enhancements

- [ ] Dark mode toggle
- [ ] SMS/WhatsApp integration
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Calendar sync (Google Calendar, Apple Calendar)
- [ ] Email/SMS reminders
- [ ] Patient portal integration
- [ ] Analytics dashboard
- [ ] A/B testing framework
- [ ] Real-time availability webhooks

## 📝 Project Structure

```
appointment-scheduling-agent/
├── backend/
│   ├── agent/
│   │   ├── scheduling_agent.py    # Main agent logic
│   │   └── prompts.py             # System prompts
│   ├── api/
│   │   ├── chat.py                # Chat endpoints
│   │   └── calendly_integration.py # Calendly mock API
│   ├── rag/
│   │   ├── faq_rag.py             # RAG system
│   │   ├── embeddings.py          # Embedding model
│   │   └── vector_store.py        # ChromaDB wrapper
│   ├── tools/
│   │   ├── availability_tool.py   # Availability checking
│   │   └── booking_tool.py        # Booking operations
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── main.py                    # FastAPI app
├── frontend/                      # React UI (NEW!)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx  # Main chat container
│   │   │   ├── MessageList.jsx    # Message display
│   │   │   └── MessageInput.jsx   # User input
│   │   ├── api/
│   │   │   └── chatApi.js         # API client
│   │   ├── App.jsx                # Main app
│   │   ├── main.jsx               # Entry point
│   │   └── index.css              # Styles
│   ├── package.json               # Frontend dependencies
│   ├── vite.config.js             # Vite config
│   └── tailwind.config.js         # Tailwind config
├── data/
│   ├── clinic_info.json           # FAQ knowledge base
│   ├── doctor_schedule.json       # Doctor schedule
│   └── vectordb/                  # ChromaDB storage
├── tests/
│   ├── test_agent.py              # Test suite
│   └── example_conversations.md   # Example dialogues
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── start.sh                       # Convenience startup script
└── README.md                      # This file
```

## 🤝 Contributing

This is an assessment project, but suggestions are welcome!

## 📄 License

This project is created for the Lyzr AI Assessment.

## Author

**Assessment Submission**

- Framework: FastAPI
- LLM: OpenAI GPT-4 Turbo / Anthropic Claude 3
- Vector DB: ChromaDB
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)

## Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- FastAPI for the backend framework

---

**Note**: This project now includes **real Calendly API integration** with mock fallback. For full production use, also implement:

- Proper database (PostgreSQL)
- Redis for session management
- Authentication & authorization
- HIPAA compliance measures
- Comprehensive error handling
- Monitoring & logging
- CI/CD pipeline
- Comprehensive test coverage
- Webhooks for real-time Calendly sync

## Development Process

This project was developed with AI-assisted coding tools as part of a learning and rapid prototyping process. All code has been reviewed, tested, and thoroughly understood by the developer.
