import { CheckCircle, XCircle, Calendar, Clock, User, Mail, Phone, FileText, MapPin, Download, Share2, Edit } from 'lucide-react'
import { useState } from 'react'

function AppointmentConfirmation({ appointment, type = 'booked', onClose, onNewAppointment }) {
  const [copied, setCopied] = useState(false)

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

  const getTypeDisplay = (appointmentType) => {
    const types = {
      'consultation': 'General Consultation',
      'followup': 'Follow-up',
      'physical': 'Physical Exam',
      'specialist': 'Specialist Consultation'
    }
    return types[appointmentType] || appointmentType
  }

  const copyConfirmationCode = () => {
    navigator.clipboard.writeText(appointment.confirmation_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadDetails = () => {
    const details = `
HealthCare Plus Clinic - Appointment Confirmation

Confirmation Code: ${appointment.confirmation_code}
Booking ID: ${appointment.booking_id}

Appointment Details:
Type: ${getTypeDisplay(appointment.appointment_type)}
Date: ${formatDate(appointment.date)}
Time: ${formatTime(appointment.start_time)} - ${formatTime(appointment.end_time)}

Patient Information:
Name: ${appointment.patient.name}
Email: ${appointment.patient.email}
Phone: ${appointment.patient.phone}

Reason for Visit:
${appointment.reason}

Location:
HealthCare Plus Clinic
123 Medical Center Dr, Suite 100
New York, NY 10001

What to Bring:
- Photo ID
- Insurance card
- List of current medications
- Medical records (if first visit)

Contact Us:
Phone: +1-555-123-4567
Email: appointments@healthcareplus.com

Cancellation Policy:
Please notify us at least 24 hours in advance if you need to cancel or reschedule.

${type === 'rescheduled' ? `\nNote: This appointment was rescheduled from ${formatDate(appointment.previous_date)} at ${formatTime(appointment.previous_time)}` : ''}
    `.trim()

    const blob = new Blob([details], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `appointment-${appointment.confirmation_code}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const shareDetails = async () => {
    const text = `Appointment Confirmed! 
${getTypeDisplay(appointment.appointment_type)}
${formatDate(appointment.date)} at ${formatTime(appointment.start_time)}
Confirmation: ${appointment.confirmation_code}`

    if (navigator.share) {
      try {
        await navigator.share({ text })
      } catch (err) {
        copyConfirmationCode()
      }
    } else {
      copyConfirmationCode()
    }
  }

  // Determine the header content based on type
  const getHeaderContent = () => {
    switch (type) {
      case 'booked':
        return {
          icon: <CheckCircle className="w-16 h-16 text-green-500" />,
          title: 'Appointment Confirmed!',
          subtitle: 'Your appointment has been successfully scheduled',
          bgColor: 'from-green-500 to-emerald-500'
        }
      case 'rescheduled':
        return {
          icon: <Edit className="w-16 h-16 text-purple-500" />,
          title: 'Appointment Rescheduled!',
          subtitle: 'Your appointment has been moved to a new time',
          bgColor: 'from-purple-500 to-pink-500'
        }
      case 'cancelled':
        return {
          icon: <XCircle className="w-16 h-16 text-red-500" />,
          title: 'Appointment Cancelled',
          subtitle: 'Your appointment has been cancelled successfully',
          bgColor: 'from-red-500 to-orange-500'
        }
      default:
        return {
          icon: <CheckCircle className="w-16 h-16 text-green-500" />,
          title: 'Success!',
          subtitle: 'Action completed successfully',
          bgColor: 'from-green-500 to-emerald-500'
        }
    }
  }

  const header = getHeaderContent()

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Success Header */}
        <div className={`bg-gradient-to-r ${header.bgColor} rounded-2xl shadow-2xl p-8 mb-6 text-white text-center animate-slide-up`}>
          <div className="flex justify-center mb-4 animate-bounce">
            {header.icon}
          </div>
          <h1 className="text-3xl font-bold mb-2">{header.title}</h1>
          <p className="text-white/90">{header.subtitle}</p>
        </div>

        {/* Only show details if not cancelled */}
        {type !== 'cancelled' && (
          <>
            {/* Confirmation Code Highlight */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border-2 border-purple-200 animate-slide-up" style={{ animationDelay: '0.1s' }}>
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-2">Your Confirmation Code</p>
                <div className="flex items-center justify-center space-x-3">
                  <p className="text-4xl font-bold font-mono text-purple-600 tracking-wider">
                    {appointment.confirmation_code}
                  </p>
                  <button
                    onClick={copyConfirmationCode}
                    className="bg-purple-100 hover:bg-purple-200 text-purple-600 p-2 rounded-lg transition-colors"
                    title="Copy code"
                  >
                    {copied ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Share2 className="w-5 h-5" />
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Save this code to view, cancel, or reschedule your appointment
                </p>
              </div>
            </div>

            {/* Appointment Details */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <Calendar className="w-5 h-5 text-purple-600" />
                <span>Appointment Details</span>
              </h2>

              <div className="space-y-4">
                {/* Type */}
                <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
                  <FileText className="w-5 h-5 text-purple-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-500">Appointment Type</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {getTypeDisplay(appointment.appointment_type)}
                    </p>
                  </div>
                </div>

                {/* Date & Time */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <Calendar className="w-5 h-5 text-gray-600 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-500">Date</p>
                      <p className="font-semibold text-gray-900">{formatDate(appointment.date)}</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <Clock className="w-5 h-5 text-gray-600 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-500">Time</p>
                      <p className="font-semibold text-gray-900">
                        {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Rescheduled Notice */}
                {type === 'rescheduled' && appointment.previous_date && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">
                      <strong>Note:</strong> Rescheduled from {formatDate(appointment.previous_date)} at {formatTime(appointment.previous_time)}
                    </p>
                  </div>
                )}

                {/* Reason */}
                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <FileText className="w-5 h-5 text-gray-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-500">Reason for Visit</p>
                    <p className="text-gray-900">{appointment.reason}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Patient Information */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 animate-slide-up" style={{ animationDelay: '0.3s' }}>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <User className="w-5 h-5 text-purple-600" />
                <span>Patient Information</span>
              </h2>

              <div className="space-y-3">
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <User className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-500">Name</p>
                    <p className="font-medium text-gray-900">{appointment.patient.name}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Mail className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-500">Email</p>
                    <p className="font-medium text-gray-900">{appointment.patient.email}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Phone className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="text-sm text-gray-500">Phone</p>
                    <p className="font-medium text-gray-900">{appointment.patient.phone}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Location & What to Bring */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 animate-slide-up" style={{ animationDelay: '0.4s' }}>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <MapPin className="w-5 h-5 text-purple-600" />
                <span>Location & Preparation</span>
              </h2>

              <div className="space-y-4">
                {/* Location */}
                <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                  <p className="font-semibold text-gray-900 mb-1">HealthCare Plus Clinic</p>
                  <p className="text-gray-700 text-sm">123 Medical Center Dr, Suite 100</p>
                  <p className="text-gray-700 text-sm">New York, NY 10001</p>
                  <p className="text-purple-600 text-sm mt-2">+1-555-123-4567</p>
                </div>

                {/* What to Bring */}
                <div>
                  <p className="font-semibold text-gray-900 mb-2">What to Bring:</p>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 bg-purple-600 rounded-full"></span>
                      <span>Photo ID (Driver's License, Passport, etc.)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 bg-purple-600 rounded-full"></span>
                      <span>Insurance card</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 bg-purple-600 rounded-full"></span>
                      <span>List of current medications</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 bg-purple-600 rounded-full"></span>
                      <span>Medical records (if first visit)</span>
                    </li>
                  </ul>
                </div>

                {/* Important Note */}
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>Please arrive 15 minutes early</strong> to complete any necessary paperwork.
                  </p>
                </div>
              </div>
            </div>

            {/* Cancellation Policy */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 mb-6 border border-gray-200 animate-slide-up" style={{ animationDelay: '0.5s' }}>
              <h3 className="font-semibold text-gray-900 mb-2">Cancellation Policy</h3>
              <p className="text-sm text-gray-700">
                If you need to cancel or reschedule your appointment, please notify us at least 24 hours in advance. 
                You can manage your appointment anytime using your confirmation code: <span className="font-mono font-semibold text-purple-600">{appointment.confirmation_code}</span>
              </p>
            </div>
          </>
        )}

        {/* Cancelled State Message */}
        {type === 'cancelled' && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6 text-center animate-slide-up">
            <p className="text-gray-700 mb-4">
              Your appointment for <strong>{getTypeDisplay(appointment.appointment_type)}</strong> on {formatDate(appointment.date)} has been cancelled.
            </p>
            <p className="text-sm text-gray-500">
              If you cancelled by mistake or would like to schedule a new appointment, we're here to help!
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6 animate-slide-up" style={{ animationDelay: '0.6s' }}>
          {type !== 'cancelled' && (
            <>
              <button
                onClick={downloadDetails}
                className="flex-1 bg-white hover:bg-gray-50 text-gray-700 py-3 px-6 rounded-xl font-medium transition-colors border border-gray-300 flex items-center justify-center space-x-2"
              >
                <Download className="w-5 h-5" />
                <span>Download Details</span>
              </button>
              <button
                onClick={shareDetails}
                className="flex-1 bg-white hover:bg-gray-50 text-gray-700 py-3 px-6 rounded-xl font-medium transition-colors border border-gray-300 flex items-center justify-center space-x-2"
              >
                <Share2 className="w-5 h-5" />
                <span>Share</span>
              </button>
            </>
          )}
        </div>

        {/* Primary Action Button */}
        <div className="flex flex-col gap-3 animate-slide-up" style={{ animationDelay: '0.7s' }}>
          {type === 'cancelled' && onNewAppointment && (
            <button
              onClick={onNewAppointment}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-4 px-6 rounded-xl font-semibold transition-all transform hover:scale-105 flex items-center justify-center space-x-2"
            >
              <Calendar className="w-5 h-5" />
              <span>Schedule New Appointment</span>
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className={`w-full ${type === 'cancelled' ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'} py-4 px-6 rounded-xl font-semibold transition-all`}
            >
              {type === 'cancelled' ? 'Close' : 'Done'}
            </button>
          )}
        </div>

        {/* Additional Help */}
        <div className="text-center mt-8 text-sm text-gray-500 animate-slide-up" style={{ animationDelay: '0.8s' }}>
          <p>Need help? Contact us at <a href="tel:+15551234567" className="text-purple-600 hover:underline">+1-555-123-4567</a></p>
          <p>or email <a href="mailto:appointments@healthcareplus.com" className="text-purple-600 hover:underline">appointments@healthcareplus.com</a></p>
        </div>
      </div>
    </div>
  )
}

export default AppointmentConfirmation

