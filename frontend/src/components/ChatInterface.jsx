import { useState, useEffect, useRef } from 'react'
import { AlertCircle, RefreshCw, Trash2 } from 'lucide-react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { chatAPI } from '../api/chatApi'

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m Meera, your HealthCare Plus virtual assistant. I\'m here to help you schedule appointments and answer any questions you might have about our clinic. What brings you in today?',
      timestamp: new Date(),
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [isHealthy, setIsHealthy] = useState(true)
  const messagesEndRef = useRef(null)

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth()
  }, [])

  const checkBackendHealth = async () => {
    try {
      const health = await chatAPI.checkHealth()
      setIsHealthy(health.status === 'healthy')
      if (health.status !== 'healthy') {
        setError('Backend server is not responding. Please make sure it\'s running.')
      }
    } catch (err) {
      setIsHealthy(false)
      setError('Cannot connect to backend. Please start the server with: cd backend && python main.py')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (message) => {
    if (!message.trim()) return

    // Add user message
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      // Prepare conversation history
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Send to backend
      const response = await chatAPI.sendMessage(message, conversationHistory, sessionId)

      // Update session ID if new
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id)
      }

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        metadata: response.metadata
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setError(err.message)
      // Add error message
      const errorMessage = {
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble processing your request. Please try again or contact our office directly at +1-555-123-4567.',
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = async () => {
    if (sessionId) {
      await chatAPI.clearSession(sessionId)
    }
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m Meera, your HealthCare Plus virtual assistant. I\'m here to help you schedule appointments and answer any questions you might have about our clinic. What brings you in today?',
        timestamp: new Date(),
      }
    ])
    setSessionId(null)
    setError(null)
  }

  const handleRetry = () => {
    checkBackendHealth()
    setError(null)
  }

  return (
    <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden flex flex-col h-[calc(100vh-12rem)] sm:h-[calc(100vh-10rem)] lg:h-[calc(100vh-8rem)] min-h-[500px] max-h-[900px] animate-slide-up">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
            <span className="text-white font-bold text-lg">M</span>
          </div>
          <div>
            <h3 className="text-white font-semibold text-lg">Meera</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
              <p className="text-white/80 text-sm">
                {isHealthy ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {!isHealthy && (
            <button
              onClick={handleRetry}
              className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
              title="Retry connection"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          )}
          <button
            onClick={handleClearChat}
            className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
            title="Clear conversation"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-3 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-red-800">{error}</p>
            {!isHealthy && (
              <button
                onClick={handleRetry}
                className="text-sm text-red-600 hover:text-red-700 font-medium mt-1 underline"
              >
                Retry Connection
              </button>
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <MessageList
        messages={messages}
        isLoading={isLoading}
        messagesEndRef={messagesEndRef}
      />

      {/* Input */}
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading || !isHealthy}
      />
    </div>
  )
}

export default ChatInterface

