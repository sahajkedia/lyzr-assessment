import { User } from 'lucide-react'

function MessageList({ messages, isLoading, messagesEndRef }) {
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  // Function to render text with markdown formatting
  const renderFormattedText = (text) => {
    // Split by ** to find bold sections
    const parts = text.split(/(\*\*.*?\*\*)/g)
    
    return parts.map((part, index) => {
      // Check if this part is wrapped in **
      if (part.startsWith('**') && part.endsWith('**')) {
        const boldText = part.slice(2, -2)
        return <strong key={index} className="font-semibold">{boldText}</strong>
      }
      return <span key={index}>{part}</span>
    })
  }

  return (
    <div className="flex-1 overflow-y-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-4 space-y-3 sm:space-y-4 bg-gray-50">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex items-start space-x-2 sm:space-x-3 animate-slide-in ${
            message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
          }`}
        >
          {/* Avatar */}
          <div
            className={`flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center ${
              message.role === 'user'
                ? 'bg-primary-600'
                : message.isError
                ? 'bg-red-100'
                : 'bg-gradient-to-br from-purple-400 to-pink-400'
            }`}
          >
            {message.role === 'user' ? (
              <User className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            ) : (
              <span className="text-white font-semibold text-xs sm:text-sm">M</span>
            )}
          </div>

          {/* Message Content */}
          <div className={`flex-1 max-w-[85%] sm:max-w-[80%] lg:max-w-[75%] ${message.role === 'user' ? 'flex flex-col items-end' : ''}`}>
            {/* Agent Name Label */}
            {message.role === 'assistant' && (
              <p className="text-xs font-medium text-gray-500 mb-1 px-2">Meera</p>
            )}
            <div
              className={`message-bubble ${
                message.role === 'user'
                  ? 'user-message'
                  : message.isError
                  ? 'bg-red-50 text-red-900 border border-red-200'
                  : 'agent-message'
              }`}
            >
              <div className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">
                {renderFormattedText(message.content)}
              </div>
              
              {/* Metadata (for tool usage info) */}
              {message.metadata?.used_tools && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500 italic">
                    Tools used: {message.metadata.tool_calls?.join(', ')}
                  </p>
                </div>
              )}
            </div>
            
            {/* Timestamp */}
            <p className="text-xs text-gray-400 mt-1 px-2">
              {formatTime(message.timestamp)}
            </p>
          </div>
        </div>
      ))}

      {/* Typing Indicator */}
      {isLoading && (
        <div className="flex items-start space-x-2 sm:space-x-3 animate-slide-in">
          <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
            <span className="text-white font-semibold text-xs sm:text-sm">M</span>
          </div>
          <div className="flex flex-col">
            <p className="text-xs font-medium text-gray-500 mb-1 px-2">Meera</p>
            <div className="message-bubble agent-message">
              <div className="typing-indicator flex space-x-1">
                <span style={{ '--delay': 0 }}></span>
                <span style={{ '--delay': 1 }}></span>
                <span style={{ '--delay': 2 }}></span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList

