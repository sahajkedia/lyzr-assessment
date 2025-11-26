# System Architecture

## Overview

The Medical Appointment Scheduling Agent is built with a modern, scalable architecture that seamlessly integrates LLM-powered conversation with appointment booking and FAQ answering capabilities.

## Component Descriptions

### 1. **API Layer (FastAPI)**

- **Chat Endpoint**: Receives user messages, manages sessions
- **Calendly Endpoints**: Availability checking, booking, cancellation
- **Appointments**: Management and retrieval endpoints

### 2. **Scheduling Agent**

Core orchestration component that:

- Manages conversation flow through 3 phases (Understanding → Recommendation → Confirmation)
- Detects intent (scheduling vs FAQ)
- Calls appropriate tools based on context
- Maintains conversation state
- Switches between FAQ and scheduling seamlessly

### 3. **RAG System (FAQ)**

Retrieval Augmented Generation for answering clinic questions:

- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: ChromaDB with persistent storage
- **Knowledge Base**: Structured clinic information (insurance, parking, policies, etc.)
- **Semantic Search**: Finds relevant information based on query meaning

### 4. **Tools System**

LLM-callable functions for appointment operations:

**Availability Tools:**

- `check_availability(date, type)`: Check slots for specific date
- `get_next_available_slots(type, days)`: Get upcoming availability

**Booking Tools:**

- `book_appointment(...)`: Create new appointment
- `cancel_appointment(booking_id)`: Cancel existing appointment
- `reschedule_appointment(booking_id, new_date, new_time)`: Move appointment
- `get_appointment_by_confirmation(code)`: Retrieve by confirmation code

### 5. **Calendly Service**

Unified service with intelligent fallback:

- **Real Mode**: Connects to Calendly API when configured
- **Mock Mode**: Uses local JSON storage when no API key provided
- **Fallback Mode**: Automatically switches to mock if API fails
- Handles slot calculation, conflict detection, and appointment management

### 6. **Data Models**

Pydantic schemas for type safety:

- Request/Response validation
- Serialization/Deserialization
- Input validation with detailed error messages

## Data Flow

### Scheduling Flow

```
1. User: "I need an appointment"
   ↓
2. Agent detects scheduling intent
   ↓
3. Agent asks for reason/preferences
   ↓
4. Agent calls get_next_available_slots()
   ↓
5. Calendly Service calculates available slots
   ↓
6. Agent presents options to user
   ↓
7. User selects slot + provides info
   ↓
8. Agent confirms details
   ↓
9. Agent calls book_appointment()
   ↓
10. Booking confirmation returned
```

### FAQ Flow

```
1. User: "What insurance do you accept?"
   ↓
2. Agent detects FAQ question
   ↓
3. Query sent to RAG system
   ↓
4. Semantic search in vector store
   ↓
5. Relevant documents retrieved
   ↓
6. Context compiled and sent to LLM
   ↓
7. LLM generates natural answer
   ↓
8. Answer returned to user
   ↓
9. Agent returns to previous context (if scheduling)
```

### Context Switching Flow

```
User: "I want to book an appointment"
Agent: "What brings you in?"
User: "Actually, what insurance do you accept?" ← CONTEXT SWITCH
Agent: [Answers from RAG] "We accept Blue Cross..." ← FAQ RESPONSE
       "Now, what brings you in today?" ← BACK TO SCHEDULING
User: "I have Blue Cross, I need a checkup"
Agent: [Continues booking process]
```

## Technology Stack

### Backend

- **Framework**: FastAPI (async Python)
- **LLM**: OpenAI GPT-4 Turbo / Anthropic Claude 3 Sonnet
- **Vector DB**: ChromaDB (persistent)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Validation**: Pydantic v2

### Frontend (Optional)

- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Data Storage

- **Vector Store**: ChromaDB (./data/vectordb/)
- **Appointments**: JSON (./data/appointments.json)
- **Schedule**: JSON (./data/doctor_schedule.json)
- **Knowledge Base**: JSON (./data/clinic_info.json)

## Key Design Decisions

### 1. **Unified Calendly Service**

Instead of separate real/mock implementations, we use a single service that:

- Detects available mode at initialization
- Automatically falls back on failure
- Provides consistent interface regardless of mode

**Benefits**: Seamless development, no code changes for production, graceful degradation

### 2. **Native Function Calling**

Uses OpenAI's native function calling (not ReAct prompting):

- More reliable tool execution
- Automatic parameter validation
- Better multi-step reasoning

### 3. **RAG for FAQs**

Instead of fine-tuning or prompt stuffing:

- Dynamic knowledge retrieval
- Easy to update information
- No hallucinations (grounded in knowledge base)
- Semantic search vs keyword matching

### 4. **Stateless Agent**

No session storage required:

- Conversation history passed with each request
- Scales horizontally
- Simple deployment
- (Optional: Add Redis for production session management)

### 5. **Layered Architecture**

Clear separation of concerns:

- **API Layer**: Request handling, validation
- **Business Logic**: Agent orchestration
- **Data Layer**: Storage and retrieval
- **External Services**: LLM, Calendly

## Error Handling

### Graceful Degradation

1. **Calendly API Failure**: Falls back to mock mode
2. **LLM Timeout**: Returns helpful error message with phone number
3. **Vector Store Error**: Continues scheduling without FAQ
4. **Tool Execution Error**: Returns error info to LLM for handling

### Validation Layers

1. **Frontend**: Basic input validation
2. **API**: Pydantic schema validation
3. **Business Logic**: Slot availability, date validation
4. **Data Layer**: Consistency checks

## Scalability Considerations

### Current (Development)

- In-memory session management
- File-based storage
- Single server instance

### Production Ready

- **Database**: PostgreSQL for appointments
- **Cache**: Redis for sessions
- **Queue**: Celery for async tasks
- **Load Balancer**: Multiple API instances
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with ELK stack

## Security

### Current

- Environment variables for secrets
- Input validation on all endpoints
- CORS configuration
- No sensitive data in logs

### Production Requirements

- HIPAA compliance
- Data encryption (at rest and in transit)
- Authentication & authorization (OAuth 2.0)
- Rate limiting
- Audit logging
- Security headers
- Regular security audits

## Testing Strategy

### Unit Tests

- Model validation
- Tool functions
- RAG retrieval
- Utility functions

### Integration Tests

- API endpoints
- Agent conversation flows
- Tool orchestration
- Database operations

### Mocked Tests

- No external API calls required
- Fast execution
- Repeatable results
- CI/CD friendly

## Deployment

### Docker

```yaml
services:
  backend:
    - FastAPI application
    - Uvicorn server
    - Vector store volume

  frontend:
    - Nginx for static files
    - React SPA
```

### Environment Variables

- See .env.example for full configuration
- Minimum required: LLM API key
- Optional: Calendly API key

## Monitoring & Observability

### Metrics to Track

- **Performance**: Response times, token usage
- **Usage**: API calls, booking success rate
- **Errors**: Failed bookings, API errors
- **User Experience**: Conversation length, completion rate

### Logging

- Structured JSON logging
- Request/response logging (sanitized)
- Error tracking with stack traces
- Performance profiling
