import { User, Calendar, CheckCircle, XCircle, Edit } from 'lucide-react'
import { useState } from 'react'
import AppointmentConfirmation from './AppointmentConfirmation'

function MessageList({ messages, isLoading, messagesEndRef }) {
  const [expandedConfirmation, setExpandedConfirmation] = useState(null)

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

  // Detect if message contains appointment confirmation
  const parseAppointmentData = (content) => {
    // Look for booking confirmation patterns
    const bookingIdMatch = content.match(/booking[_ ]id[:\s]*([A-Z]+-\d+-\d+)/i)
    const confirmationCodeMatch = content.match(/confirmation[_ ]code[:\s]*([A-Z0-9]{6})/i)
    const dateMatch = content.match(/date[:\s]*([A-Za-z]+,\s*[A-Za-z]+\s+\d+,\s+\d{4})/i)
    
    // Check for cancellation
    const isCancelled = /cancel(?:led|lation)/i.test(content) && /success/i.test(content)
    
    // Check for reschedule
    const isRescheduled = /reschedule[d]?/i.test(content) && /success/i.test(content)
    
    if (bookingIdMatch && confirmationCodeMatch) {
      // Try to extract all appointment details from the message
      const typeMatch = content.match(/(?:type of )?appointment[:\s]*\*\*([^*]+)\*\*/i)
      const timeMatch = content.match(/time[:\s]*([0-9:]+\s*(?:AM|PM))/i)
      const patientMatch = content.match(/patient[_ ]name[:\s]*\*\*([^*]+)\*\*/i)
      const phoneMatch = content.match(/phone[_ ]number[:\s]*\*\*([^*]+)\*\*/i)
      const emailMatch = content.match(/email[_ ]address[:\s]*\*\*([^*]+)\*\*/i)
      const reasonMatch = content.match(/reason for visit[:\s]*\*\*([^*]+)\*\*/i)
      
      return {
        hasAppointment: true,
        type: isCancelled ? 'cancelled' : isRescheduled ? 'rescheduled' : 'booked',
        booking_id: bookingIdMatch[1],
        confirmation_code: confirmationCodeMatch[1],
        appointment_type: typeMatch ? typeMatch[1].trim().toLowerCase().replace(' consultation', '').replace('consultation', 'consultation') : 'consultation',
        date: dateMatch ? dateMatch[1] : new Date().toISOString().split('T')[0],
        start_time: timeMatch ? timeMatch[1] : '09:00',
        patient: {
          name: patientMatch ? patientMatch[1] : 'Patient',
          email: emailMatch ? emailMatch[1] : '',
          phone: phoneMatch ? phoneMatch[1] : ''
        },
        reason: reasonMatch ? reasonMatch[1] : 'General consultation',
        status: isCancelled ? 'cancelled' : 'confirmed'
      }
    }
    
    return { hasAppointment: false }
  }

  const formatDateForAPI = (dateStr) => {
    try {
      const date = new Date(dateStr)
      return date.toISOString().split('T')[0]
    } catch {
      return dateStr
    }
  }

  const formatTimeForAPI = (timeStr) => {
    try {
      const match = timeStr.match(/(\d+):(\d+)\s*(AM|PM)/i)
      if (match) {
        let hours = parseInt(match[1])
        const minutes = match[2]
        const period = match[3].toUpperCase()
        
        if (period === 'PM' && hours !== 12) hours += 12
        if (period === 'AM' && hours === 12) hours = 0
        
        return `${hours.toString().padStart(2, '0')}:${minutes}`
      }
      return timeStr
    } catch {
      return timeStr
    }
  }

  return (
    <div className="flex-1 overflow-y-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-4 space-y-3 sm:space-y-4 bg-gray-50">
      {messages.map((message, index) => {
        const appointmentData = message.role === 'assistant' ? parseAppointmentData(message.content) : { hasAppointment: false }
        
        return (
          <div key={index}>
            <div
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

                  {/* Show Appointment Card Preview if confirmation detected */}
                  {appointmentData.hasAppointment && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <button
                        onClick={() => setExpandedConfirmation(expandedConfirmation === index ? null : index)}
                        className="w-full bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 border border-purple-200 rounded-lg p-3 transition-all flex items-center justify-between group"
                      >
                        <div className="flex items-center space-x-2">
                          {appointmentData.type === 'cancelled' ? (
                            <XCircle className="w-5 h-5 text-red-500" />
                          ) : appointmentData.type === 'rescheduled' ? (
                            <Edit className="w-5 h-5 text-purple-500" />
                          ) : (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          )}
                          <span className="text-sm font-medium text-gray-900">
                            {appointmentData.type === 'cancelled' 
                              ? 'View Cancellation Details' 
                              : appointmentData.type === 'rescheduled'
                              ? 'View Rescheduled Appointment'
                              : 'View Appointment Confirmation'}
                          </span>
                        </div>
                        <Calendar className="w-4 h-4 text-purple-600 group-hover:scale-110 transition-transform" />
                      </button>
                    </div>
                  )}
                </div>
                
                {/* Timestamp */}
                <p className="text-xs text-gray-400 mt-1 px-2">
                  {formatTime(message.timestamp)}
                </p>
              </div>
            </div>

            {/* Expanded Appointment Confirmation */}
            {appointmentData.hasAppointment && expandedConfirmation === index && (
              <div className="mt-3 ml-10 sm:ml-12 animate-slide-up">
                <div className="bg-white rounded-xl border border-purple-200 overflow-hidden shadow-lg max-w-2xl">
                  <AppointmentConfirmation
                    appointment={{
                      ...appointmentData,
                      date: formatDateForAPI(appointmentData.date),
                      start_time: formatTimeForAPI(appointmentData.start_time),
                      end_time: appointmentData.end_time || '10:00'
                    }}
                    type={appointmentData.type}
                    onClose={() => setExpandedConfirmation(null)}
                  />
                </div>
              </div>
            )}
          </div>
        )
      })}

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

