# Getting Started - Quick Setup Guide

This guide will help you get the Medical Appointment Scheduling Agent up and running in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (or Anthropic API key)
- Terminal/Command line access

## Quick Start (5 Steps)

### Step 1: Set up Python environment

```bash
# Navigate to project directory
cd lyzr-assessment-1

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (API server)
- OpenAI/Anthropic SDKs (LLM)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- Other utilities

### Step 3: Configure API key

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` file and add your API key:

**For OpenAI (GPT-4):**
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**For Anthropic (Claude):**
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=your-actual-api-key-here
```

### Step 4: Start the server

```bash
cd backend
python main.py
```

You should see:
```
Initializing Medical Appointment Scheduling Agent...
LLM Provider: openai
LLM Model: gpt-4-turbo
Agent initialized successfully!
Server running on port 8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Test the agent

**Option A: Interactive CLI**

Open a new terminal and run:
```bash
python run.py
```

Then chat with the agent:
```
You: I need to schedule an appointment
Agent: I'd be happy to help! What brings you in today?
```

**Option B: Test via API**

In a new terminal:
```bash
python test_client.py
```

**Option C: Use curl**

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What insurance do you accept?",
    "conversation_history": []
  }'
```

**Option D: Swagger UI**

Open browser: http://localhost:8000/docs

## What to Test

### Test 1: FAQ Question
```
You: "What insurance do you accept?"

Expected: Agent lists accepted insurance providers from the knowledge base.
```

### Test 2: Schedule Appointment
```
You: "I need to schedule an appointment"
Agent: "I'd be happy to help! What brings you in today?"
You: "I've been having headaches"
Agent: "I recommend a General Consultation (30 minutes)..."

Expected: Agent guides you through booking process.
```

### Test 3: Context Switching
```
You: "I want to book an appointment"
Agent: "What brings you in?"
You: "Actually, where are you located?"
Agent: [Answers location question]
You: "Thanks. I need a checkup"

Expected: Agent seamlessly switches from FAQ back to scheduling.
```

## Project Structure Overview

```
lyzr-assessment-1/
├── backend/               # Core application
│   ├── agent/            # Conversational agent logic
│   ├── api/              # API endpoints & Calendly mock
│   ├── rag/              # RAG system for FAQs
│   ├── tools/            # Availability & booking tools
│   └── main.py           # FastAPI application
├── data/                 # Knowledge base & schedule
│   ├── clinic_info.json  # FAQ knowledge base
│   ├── doctor_schedule.json
│   └── vectordb/         # ChromaDB storage (auto-created)
├── tests/                # Test suite
├── run.py               # Interactive CLI client
├── test_client.py       # API test client
└── README.md            # Full documentation
```

## Common Issues & Solutions

### Issue 1: "No module named 'backend'"

**Solution:** Make sure you're in the project root directory:
```bash
cd lyzr-assessment-1
python run.py
```

### Issue 2: "API key not found"

**Solution:** Check your `.env` file:
```bash
cat .env | grep API_KEY
```

Make sure the key is set correctly (no quotes needed).

### Issue 3: Port 8000 already in use

**Solution:** Change port in `.env`:
```env
BACKEND_PORT=8001
```

Then restart the server.

### Issue 4: ChromaDB initialization issues

**Solution:** Delete the vector database and let it reinitialize:
```bash
rm -rf data/vectordb/
```

Restart the server - it will automatically recreate the knowledge base.

### Issue 5: Slow first response

**Normal behavior:** The first request loads the model (~5-10 seconds). Subsequent requests are fast.

## Next Steps

1. **Read the full documentation:** Check `README.md` for detailed architecture
2. **View example conversations:** See `tests/example_conversations.md`
3. **Run test suite:** `pytest tests/test_agent.py -v`
4. **Explore API docs:** http://localhost:8000/docs
5. **Customize clinic info:** Edit `data/clinic_info.json`
6. **Adjust schedule:** Edit `data/doctor_schedule.json`

## Testing Checklist

- [ ] Server starts without errors
- [ ] FAQ questions get accurate answers
- [ ] Can check appointment availability
- [ ] Can book an appointment
- [ ] Context switching works (FAQ during booking)
- [ ] Edge cases handled (past dates, no slots, etc.)
- [ ] Conversation feels natural and empathetic

## Sample Conversation Flow

Here's a complete booking conversation to test:

```
1. You: "Hello"
   Agent: [Greets warmly]

2. You: "I need to see the doctor"
   Agent: [Asks what brings you in]

3. You: "I've been having headaches"
   Agent: [Recommends appointment type]

4. You: "General consultation sounds good"
   Agent: [Asks for date/time preference]

5. You: "Tomorrow afternoon"
   Agent: [Shows available slots using tool]

6. You: "2:00 PM works"
   Agent: [Asks for patient information]

7. You: "John Doe"
   [Continue with phone, email...]

8. Agent: [Confirms and books using tool]
```

## Performance Expectations

- **First request:** 5-10 seconds (model loading)
- **Subsequent requests:** 1-3 seconds
- **FAQ lookup:** ~500ms
- **Tool calls:** ~1-2 seconds
- **Full booking flow:** 2-3 minutes (conversation time)

## Getting Help

1. Check `README.md` for detailed documentation
2. Review `architecture_diagram.md` for system design
3. See `tests/example_conversations.md` for examples
4. Check API logs in terminal for errors

## Production Checklist (Future)

For deploying to production, you'll need:

- [ ] Replace mock Calendly with real API
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for sessions
- [ ] Add authentication
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Add rate limiting
- [ ] Implement HIPAA compliance
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

---

**You're all set!** The agent is ready to help schedule appointments and answer questions. 🎉

For questions or issues, refer to the full README.md documentation.


