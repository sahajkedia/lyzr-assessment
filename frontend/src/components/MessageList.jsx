import { Bot, User } from 'lucide-react'

function MessageList({ messages, isLoading, messagesEndRef }) {
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex items-start space-x-3 animate-slide-in ${
            message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
          }`}
        >
          {/* Avatar */}
          <div
            className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
              message.role === 'user'
                ? 'bg-primary-600'
                : message.isError
                ? 'bg-red-100'
                : 'bg-medical-100'
            }`}
          >
            {message.role === 'user' ? (
              <User className="w-5 h-5 text-white" />
            ) : (
              <Bot className={`w-5 h-5 ${message.isError ? 'text-red-600' : 'text-medical-600'}`} />
            )}
          </div>

          {/* Message Content */}
          <div className={`flex-1 max-w-[75%] ${message.role === 'user' ? 'flex flex-col items-end' : ''}`}>
            <div
              className={`message-bubble ${
                message.role === 'user'
                  ? 'user-message'
                  : message.isError
                  ? 'bg-red-50 text-red-900 border border-red-200'
                  : 'agent-message'
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>
              
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
        <div className="flex items-start space-x-3 animate-slide-in">
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-medical-100 flex items-center justify-center">
            <Bot className="w-5 h-5 text-medical-600" />
          </div>
          <div className="message-bubble agent-message">
            <div className="typing-indicator flex space-x-1">
              <span style={{ '--delay': 0 }}></span>
              <span style={{ '--delay': 1 }}></span>
              <span style={{ '--delay': 2 }}></span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList

