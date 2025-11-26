import { useState } from 'react'
import { X, Search, Calendar, Loader2 } from 'lucide-react'
import { chatAPI } from '../api/chatApi'
import AppointmentCard from './AppointmentCard'

function AppointmentManager({ isOpen, onClose, onSendMessage }) {
  const [confirmationCode, setConfirmationCode] = useState('')
  const [appointment, setAppointment] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!confirmationCode.trim()) return

    setLoading(true)
    setError(null)
    setAppointment(null)

    try {
      const result = await chatAPI.getAppointmentByConfirmation(confirmationCode.toUpperCase())
      if (result.success) {
        setAppointment(result.appointment)
      }
    } catch (err) {
      setError(err.message || 'Appointment not found. Please check your confirmation code.')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (bookingId) => {
    setError(null)
    try {
      const result = await chatAPI.cancelAppointment(bookingId)
      if (result.success) {
        // Update the appointment to show cancelled status
        setAppointment({ 
          ...appointment, 
          status: 'cancelled',
          cancelled_at: result.cancelled_at || new Date().toISOString()
        })
        
        // Optionally notify via chat
        if (onSendMessage) {
          setTimeout(() => {
            onClose()
          }, 2000)
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to cancel appointment.')
      // Re-throw the error so AppointmentCard can also handle it
      throw err
    }
  }

  const handleReschedule = (appt) => {
    // Close the modal and send a message to start rescheduling flow
    onClose()
    if (onSendMessage) {
      onSendMessage(`I want to reschedule my appointment with confirmation code ${appt.confirmation_code}`)
    }
  }

  const handleReset = () => {
    setConfirmationCode('')
    setAppointment(null)
    setError(null)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-slide-up">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center space-x-3">
            <Calendar className="w-6 h-6 text-white" />
            <h2 className="text-xl font-semibold text-white">Manage Appointment</h2>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {!appointment ? (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <p className="text-gray-600">
                  Enter your confirmation code to view, cancel, or reschedule your appointment
                </p>
              </div>

              {/* Search Form */}
              <form onSubmit={handleSearch} className="space-y-4">
                <div>
                  <label htmlFor="confirmationCode" className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmation Code
                  </label>
                  <div className="relative">
                    <input
                      id="confirmationCode"
                      type="text"
                      value={confirmationCode}
                      onChange={(e) => setConfirmationCode(e.target.value.toUpperCase())}
                      placeholder="e.g., ABC123"
                      maxLength={6}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-center text-lg font-mono uppercase"
                      disabled={loading}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-2 text-center">
                    This is the 6-character code from your booking confirmation
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading || confirmationCode.length !== 6}
                  className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white py-3 px-6 rounded-xl font-semibold transition-colors flex items-center justify-center space-x-2 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Searching...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5" />
                      <span>Find Appointment</span>
                    </>
                  )}
                </button>
              </form>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 animate-slide-up">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {/* Help Text */}
              <div className="mt-8 p-4 bg-purple-50 rounded-xl border border-purple-200">
                <h3 className="font-semibold text-purple-900 mb-2">Don't have your confirmation code?</h3>
                <p className="text-sm text-purple-800">
                  You can ask Meera in the chat to help you find your appointment or create a new one.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Appointment Card */}
              <AppointmentCard
                appointment={appointment}
                onCancel={handleCancel}
                onReschedule={handleReschedule}
              />

              {/* Search Again Button */}
              <button
                onClick={handleReset}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium transition-colors"
              >
                Search Another Appointment
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AppointmentManager


