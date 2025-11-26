import { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'

function MessageInput({ onSendMessage, disabled }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSendMessage(input)
      setInput('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Quick suggestions
  const suggestions = [
    "I need to schedule an appointment",
    "What insurance do you accept?",
    "Where are you located?",
    "What are your hours?"
  ]

  const handleSuggestionClick = (suggestion) => {
    if (!disabled) {
      onSendMessage(suggestion)
    }
  }

  return (
    <div className="border-t border-gray-200 bg-white flex-shrink-0">
      {/* Quick Suggestions (only show when input is empty) */}
      {!input && (
        <div className="px-3 sm:px-4 lg:px-6 py-2 sm:py-3 border-b border-gray-100">
          <p className="text-xs text-gray-500 mb-2">Quick suggestions:</p>
          <div className="flex overflow-x-auto gap-2 pb-1 scrollbar-thin">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={disabled}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap flex-shrink-0"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="px-3 sm:px-4 lg:px-6 py-3 sm:py-4">
        <div className="flex items-end space-x-2 sm:space-x-3">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={disabled ? "Connecting to server..." : "Type your message..."}
              disabled={disabled}
              rows={1}
              className="w-full px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>
          <button
            type="submit"
            disabled={disabled || !input.trim()}
            className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white p-2.5 sm:p-3 rounded-xl transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center justify-center flex-shrink-0"
          >
            {disabled && input ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-4 h-4 sm:w-5 sm:h-5" />
            )}
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2 hidden sm:block">
          Press Enter to send, Shift+Enter for new line
        </p>
      </form>
    </div>
  )
}

export default MessageInput

