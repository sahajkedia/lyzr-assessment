# Frontend Setup and Usage Guide

## Quick Start

### 1. Install Dependencies (One Time)

```bash
cd frontend
npm install
```

### 2. Start Both Servers

From the project root:

```bash
./start.sh
```

Or manually:

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 3. Open in Browser

Navigate to: **http://localhost:3000**

## Features Overview

### Landing Page

When you first open the app, you'll see:
- **Left Side**: Information about the service, features, and benefits
- **Right Side**: Placeholder for chat (click "Start Scheduling" to begin)
- **Header**: Clinic branding with 24/7 support and HIPAA compliance badges
- **Footer**: Contact information

### Chat Interface

Once you click "Start Scheduling":

#### Header
- **Status Indicator**: Green dot = connected, Red = disconnected
- **Refresh Button**: Retry connection if offline
- **Clear Chat Button**: Start a new conversation

#### Message Area
- **Agent Messages** (left side):
  - White bubbles with bot avatar
  - Medical-green accent color
  - Tool usage metadata when agent uses functions
- **Your Messages** (right side):
  - Blue bubbles with user avatar
  - Timestamp below each message
- **Typing Indicator**: Animated dots while agent is thinking

#### Input Area
- **Quick Suggestions**: Pre-written questions you can click
  - "I need to schedule an appointment"
  - "What insurance do you accept?"
  - "Where are you located?"
  - "What are your hours?"
- **Text Input**: Type your own message
  - Press Enter to send
  - Shift+Enter for new line
- **Send Button**: Click or press Enter

## User Journey Examples

### Example 1: Schedule an Appointment

1. Click "Start Scheduling"
2. Chat interface appears
3. Agent greets you
4. Click "I need to schedule an appointment" or type your own message
5. Agent asks what brings you in
6. Describe your symptoms (e.g., "I've been having headaches")
7. Agent recommends appointment type and checks availability
8. Choose from available time slots
9. Provide your information (name, phone, email)
10. Confirm booking
11. Receive confirmation code

### Example 2: Ask About Insurance

1. Type "What insurance do you accept?"
2. Agent retrieves information from knowledge base
3. See list of accepted insurance providers
4. Continue with booking or ask more questions

### Example 3: Mixed Conversation

1. Start booking an appointment
2. Mid-conversation, ask "Where is your office?"
3. Agent answers location question
4. Smoothly returns to booking process
5. Complete appointment scheduling

## UI Components Explained

### Color Scheme

- **Primary Blue** (#0ea5e9): Main actions, user messages
- **Medical Green** (#22c55e): Agent avatar, success states
- **Gray Scale**: Text, backgrounds, borders
- **White**: Clean backgrounds for messages and cards

### Icons

- **Heart**: Clinic logo (header)
- **Calendar**: Scheduling actions
- **Bot**: Agent avatar
- **User**: Your avatar
- **Send**: Submit message
- **Trash**: Clear conversation
- **Refresh**: Retry connection
- **Clock**: Time-related info
- **Shield**: Security/HIPAA

### Responsive Design

- **Desktop**: Two-column layout (info + chat)
- **Tablet**: Stacked layout with adapted spacing
- **Mobile**: Single column, optimized for touch

## Customization

### Change Colors

Edit `frontend/tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        600: '#your-color',  // Main blue
      },
      medical: {
        600: '#your-color',  // Medical green
      }
    }
  }
}
```

### Change Quick Suggestions

Edit `frontend/src/components/MessageInput.jsx`:

```javascript
const suggestions = [
  "Your custom suggestion 1",
  "Your custom suggestion 2",
  // ...
]
```

### Change API Endpoint

Edit `frontend/.env`:

```env
VITE_API_URL=http://your-backend-url
```

### Modify Welcome Message

Edit `frontend/src/components/ChatInterface.jsx`:

```javascript
const [messages, setMessages] = useState([
  {
    role: 'assistant',
    content: 'Your custom welcome message',
    timestamp: new Date(),
  }
])
```

## Troubleshooting

### Issue: "Cannot connect to backend"

**Cause**: Backend server is not running

**Solution**:
```bash
cd backend
python main.py
```

Check terminal for errors.

### Issue: White screen / "Module not found"

**Cause**: Dependencies not installed

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Styling looks broken

**Cause**: Tailwind CSS not compiled

**Solution**:
1. Restart dev server
2. Clear browser cache
3. Check `tailwind.config.js` exists

### Issue: Messages not sending

**Cause**: CORS or API connection issue

**Solution**:
1. Check browser console for errors (F12)
2. Verify backend CORS settings allow `localhost:3000`
3. Check API URL in `.env` file

### Issue: Port 3000 already in use

**Solution**:
```bash
# Edit vite.config.js
server: {
  port: 3001,  // Change to different port
}
```

## Development Tips

### Hot Reload

Vite automatically reloads when you save changes:
- Component changes → Hot Module Replacement (instant)
- CSS changes → Instant update
- Config changes → Full reload

### Browser DevTools

- **F12** or **Cmd+Option+I**: Open developer tools
- **Console tab**: See errors and logs
- **Network tab**: Monitor API calls
- **React DevTools**: Install extension for component inspection

### Code Organization

```
src/
├── components/     # React components
│   ├── ChatInterface.jsx    # Main container
│   ├── MessageList.jsx      # Message display logic
│   └── MessageInput.jsx     # Input handling
├── api/           # API client
│   └── chatApi.js          # Backend communication
├── App.jsx        # Root component
└── index.css      # Global styles
```

## Performance

- **First Load**: ~1-2 seconds
- **Message Send**: ~1-3 seconds (depends on AI)
- **UI Updates**: Instant (React virtual DOM)
- **Build Size**: ~300KB (gzipped)

## Browser Support

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Deployment

### Build for Production

```bash
cd frontend
npm run build
```

Creates optimized build in `dist/` folder.

### Deploy to Vercel

```bash
npm install -g vercel
cd frontend
vercel
```

### Deploy to Netlify

```bash
npm install -g netlify-cli
cd frontend
netlify deploy --prod --dir=dist
```

### Environment Variables for Production

Set in your hosting platform:
```
VITE_API_URL=https://your-production-api.com
```

## Screenshots

### Landing Page
- Professional header with branding
- Feature list with checkmarks
- Call-to-action button
- Statistics cards

### Chat Interface
- Clean, modern design
- Clear message separation
- Professional medical theme
- Easy-to-use input

---

**Need help?** Check the main README.md or contact support.

