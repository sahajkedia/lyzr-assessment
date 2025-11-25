# 🚀 Quick Start - Run the Full Application

## Prerequisites Check

- ✅ Python 3.10+ installed
- ✅ Node.js 16+ installed
- ✅ OpenAI API key (or Anthropic)

## Start Everything in 3 Steps

### Step 1: Set API Key (If not done already)

```bash
# Edit .env file
cp .env.example .env
# Add your OpenAI API key: OPENAI_API_KEY=sk-your-key
```

### Step 2: Run the Startup Script

```bash
./start.sh
```

That's it! The script will:
- ✅ Check dependencies
- ✅ Start backend on port 8000
- ✅ Start frontend on port 3000
- ✅ Open both servers

### Step 3: Open Your Browser

Go to: **http://localhost:3000**

You'll see a beautiful, professional UI!

---

## Manual Start (Alternative)

If you prefer to run servers separately:

### Terminal 1 - Backend

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd backend
python main.py
```

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

---

## What You'll See

### 🏠 Landing Page

- **Left**: Information about the service
  - Feature list
  - Benefits
  - Statistics
  - "Start Scheduling" button

- **Right**: Chat preview
  - Click button to activate

### 💬 Chat Interface (After clicking "Start Scheduling")

Beautiful, professional chat with:

- **Quick Suggestions**: One-click questions
  - "I need to schedule an appointment"
  - "What insurance do you accept?"
  - "Where are you located?"
  - "What are your hours?"

- **Real-time Chat**:
  - Agent messages (white, left side)
  - Your messages (blue, right side)
  - Typing indicators
  - Timestamps

- **Status Indicators**:
  - Green dot = connected
  - Red dot = disconnected (with retry button)

---

## Try These Conversations

### 1. Schedule an Appointment

```
You: I need to schedule an appointment
Agent: I'd be happy to help! What brings you in today?
You: I've been having headaches
Agent: I recommend a General Consultation (30 minutes)...
[Continue conversation to book]
```

### 2. Ask About Insurance

```
You: What insurance do you accept?
Agent: [Lists all accepted insurance providers]
```

### 3. Get Location Info

```
You: Where are you located?
Agent: [Provides address and directions]
```

### 4. Mixed Conversation

```
You: I want to book an appointment
Agent: What brings you in?
You: Actually, what's your cancellation policy?
Agent: [Explains policy, then returns to booking]
You: Thanks! I need a checkup
[Continue booking]
```

---

## Features to Explore

### ✨ Chat Features

- ✅ Natural conversation flow
- ✅ Real-time responses
- ✅ Quick suggestion buttons
- ✅ Message timestamps
- ✅ Typing indicators
- ✅ Error handling with retry
- ✅ Clear chat option
- ✅ Session management

### 🎨 UI Features

- ✅ Modern, professional design
- ✅ Medical/healthcare themed colors
- ✅ Smooth animations
- ✅ Responsive layout
- ✅ Clean typography
- ✅ Intuitive navigation

### 🔧 Technical Features

- ✅ Connection status monitoring
- ✅ Automatic reconnection
- ✅ CORS-enabled API
- ✅ Session persistence
- ✅ Tool usage display

---

## Stopping the Servers

If you used `./start.sh`:

**Press Ctrl+C** in the terminal

This stops both servers gracefully.

If running manually:

**Press Ctrl+C** in each terminal window

---

## Troubleshooting

### ❌ "Cannot connect to backend"

**Problem**: Frontend shows red status indicator

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start backend:
cd backend && python main.py
```

### ❌ Port 3000 already in use

**Problem**: Frontend won't start

**Solution**:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or change port in frontend/vite.config.js
```

### ❌ "Module not found"

**Problem**: Frontend shows errors

**Solution**:
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### ❌ Styling looks broken

**Problem**: No colors/design

**Solution**:
1. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
2. Clear browser cache
3. Restart dev server

---

## API Endpoints (For Reference)

If you want to test the API directly:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## File Locations

### Backend
- Code: `backend/`
- Config: `.env`
- Data: `data/`

### Frontend
- Code: `frontend/src/`
- Config: `frontend/.env`
- Build: `frontend/dist/` (after `npm run build`)

---

## Next Steps

1. ✅ Start servers (you've done this!)
2. ✅ Open http://localhost:3000
3. ✅ Click "Start Scheduling"
4. ✅ Try the quick suggestions
5. ✅ Have a conversation
6. ✅ Schedule a test appointment
7. ✅ Check out the API docs at http://localhost:8000/docs

---

## Support

- **Main docs**: README.md
- **Frontend guide**: FRONTEND_GUIDE.md
- **Architecture**: architecture_diagram.md
- **Examples**: tests/example_conversations.md

---

## Development Mode

The servers run in development mode with:

- **Hot reload**: Changes update automatically
- **Detailed errors**: See full stack traces
- **Debug info**: Console logs enabled

---

**Enjoy your professional medical appointment scheduling interface!** 🎉

The combination of the intelligent AI backend and beautiful React frontend creates a seamless, professional experience for users.

