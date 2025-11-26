import { Calendar, Clock, User, Mail, Phone, FileText, CheckCircle, XCircle, Edit, Trash2 } from 'lucide-react'
import { useState } from 'react'

function AppointmentCard({ appointment, onCancel, onReschedule }) {
  const [isLoading, setIsLoading] = useState(false)
  const [showConfirmCancel, setShowConfirmCancel] = useState(false)

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  const formatTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':')
    const hour = parseInt(hours)
    const ampm = hour >= 12 ? 'PM' : 'AM'
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour
    return `${displayHour}:${minutes} ${ampm}`
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getTypeDisplay = (type) => {
    const types = {
      'consultation': 'General Consultation',
      'followup': 'Follow-up',
      'physical': 'Physical Exam',
      'specialist': 'Specialist Consultation'
    }
    return types[type] || type
  }

  const handleCancel = async () => {
    setIsLoading(true)
    try {
      await onCancel(appointment.booking_id)
      setShowConfirmCancel(false)
    } catch (error) {
      console.error('Failed to cancel:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReschedule = () => {
    onReschedule(appointment)
  }

  const isUpcoming = appointment.status === 'confirmed'

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden animate-slide-up">
      {/* Header */}
      <div className={`px-4 py-3 border-b ${isUpcoming ? 'bg-gradient-to-r from-purple-50 to-pink-50' : 'bg-gray-50'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">{getTypeDisplay(appointment.appointment_type)}</h3>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(appointment.status)}`}>
            {appointment.status === 'confirmed' ? (
              <span className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3" />
                <span>Confirmed</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1">
                <XCircle className="w-3 h-3" />
                <span>Cancelled</span>
              </span>
            )}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-3">
        {/* Date & Time */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="flex items-start space-x-2">
            <Calendar className="w-4 h-4 text-gray-400 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500">Date</p>
              <p className="text-sm font-medium text-gray-900">{formatDate(appointment.date)}</p>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <Clock className="w-4 h-4 text-gray-400 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500">Time</p>
              <p className="text-sm font-medium text-gray-900">
                {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
              </p>
            </div>
          </div>
        </div>

        {/* Patient Info */}
        <div className="space-y-2 pt-2 border-t border-gray-100">
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4 text-gray-400" />
            <p className="text-sm text-gray-700">{appointment.patient.name}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Mail className="w-4 h-4 text-gray-400" />
            <p className="text-sm text-gray-600">{appointment.patient.email}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Phone className="w-4 h-4 text-gray-400" />
            <p className="text-sm text-gray-600">{appointment.patient.phone}</p>
          </div>
        </div>

        {/* Reason */}
        <div className="flex items-start space-x-2 pt-2 border-t border-gray-100">
          <FileText className="w-4 h-4 text-gray-400 mt-0.5" />
          <div>
            <p className="text-xs text-gray-500">Reason for Visit</p>
            <p className="text-sm text-gray-700">{appointment.reason}</p>
          </div>
        </div>

        {/* Booking Info */}
        <div className="pt-2 border-t border-gray-100">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <p className="text-gray-500">Booking ID</p>
              <p className="font-mono font-medium text-gray-900">{appointment.booking_id}</p>
            </div>
            <div>
              <p className="text-gray-500">Confirmation Code</p>
              <p className="font-mono font-medium text-purple-600">{appointment.confirmation_code}</p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {isUpcoming && !showConfirmCancel && (
          <div className="flex gap-2 pt-3 border-t border-gray-100">
            <button
              onClick={handleReschedule}
              disabled={isLoading}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Edit className="w-4 h-4" />
              <span>Reschedule</span>
            </button>
            <button
              onClick={() => setShowConfirmCancel(true)}
              disabled={isLoading}
              className="flex-1 bg-red-50 hover:bg-red-100 text-red-600 py-2 px-4 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-2 border border-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="w-4 h-4" />
              <span>Cancel</span>
            </button>
          </div>
        )}

        {/* Confirm Cancellation */}
        {showConfirmCancel && (
          <div className="pt-3 border-t border-gray-100 bg-red-50 rounded-lg p-3 animate-slide-up">
            <p className="text-sm text-red-800 mb-3">
              Are you sure you want to cancel this appointment? This action cannot be undone.
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleCancel}
                disabled={isLoading}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Cancelling...' : 'Yes, Cancel'}
              </button>
              <button
                onClick={() => setShowConfirmCancel(false)}
                disabled={isLoading}
                className="flex-1 bg-white hover:bg-gray-50 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium transition-colors border border-gray-300"
              >
                No, Keep It
              </button>
            </div>
          </div>
        )}

        {/* Rescheduled Notice */}
        {appointment.rescheduled_at && (
          <div className="pt-2 border-t border-gray-100">
            <p className="text-xs text-gray-500">
              Rescheduled from {formatDate(appointment.previous_date)} at {formatTime(appointment.previous_time)}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AppointmentCard


