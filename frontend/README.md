# Medical Appointment Scheduler - Frontend

A beautiful, professional React frontend for the Medical Appointment Scheduling Agent.

## Features

- 🎨 Modern, professional UI with Tailwind CSS
- 💬 Real-time chat interface
- 🔄 Seamless backend integration
- 📱 Responsive design
- ✨ Smooth animations and transitions
- 🏥 Medical/healthcare themed styling
- 🎯 Quick suggestion buttons
- ⚡ Built with Vite for fast development

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

The default configuration connects to `http://localhost:8000`.

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Make Sure Backend is Running

The frontend needs the backend API to be running:

```bash
# In a separate terminal
cd backend
python main.py
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx    # Main chat container
│   │   ├── MessageList.jsx      # Message display
│   │   └── MessageInput.jsx     # User input
│   ├── api/
│   │   └── chatApi.js           # API client
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── public/                      # Static assets
├── index.html                   # HTML template
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind configuration
└── package.json                # Dependencies
```

## Features Explained

### Chat Interface
- Natural conversation flow
- User messages appear on the right (blue)
- AI responses appear on the left (white)
- Typing indicators during processing
- Timestamps for all messages

### Quick Suggestions
- Pre-defined questions for easy start
- One-click to send common queries
- Helps users get started quickly

### Error Handling
- Connection status indicator
- Clear error messages
- Retry button for failed connections
- Graceful degradation

### Backend Integration
- Automatic session management
- Conversation history tracking
- Tool usage metadata display
- Health check monitoring

## Customization

### Colors

Edit `tailwind.config.js` to customize the color scheme:

```javascript
colors: {
  primary: { ... },  // Main blue theme
  medical: { ... },  // Medical green theme
}
```

### API Endpoint

Edit `.env` to change the backend URL:

```env
VITE_API_URL=http://your-backend-url
```

### Quick Suggestions

Edit `MessageInput.jsx` to customize suggestions:

```javascript
const suggestions = [
  "Your custom suggestion",
  // ...
]
```

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Deploy

The `dist/` directory can be deployed to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- etc.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Backend Connection Failed

**Error:** "Cannot connect to backend"

**Solution:**
1. Make sure backend is running: `cd backend && python main.py`
2. Check backend is on port 8000
3. Verify CORS is enabled in backend
4. Check `.env` file has correct API URL

### Styling Issues

**Problem:** Tailwind classes not applying

**Solution:**
1. Make sure PostCSS is configured
2. Restart dev server
3. Clear browser cache

### Build Errors

**Problem:** Build fails with module errors

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Voice input
- [ ] File upload for documents
- [ ] Print appointment confirmation
- [ ] Calendar integration
- [ ] Email/SMS notifications
- [ ] Accessibility improvements (WCAG 2.1)

## Contributing

This frontend is part of the Medical Appointment Scheduling Agent assessment project.

## License

Created for Lyzr AI Assessment

