import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Loader2, AlertCircle } from 'lucide-react'
import AppointmentConfirmation from './AppointmentConfirmation'
import { chatAPI } from '../api/chatApi'

function ConfirmationPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [appointment, setAppointment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const confirmationCode = searchParams.get('code')
  const bookingId = searchParams.get('booking_id')
  const type = searchParams.get('type') || 'booked'

  useEffect(() => {
    const fetchAppointment = async () => {
      if (!confirmationCode && !bookingId) {
        setError('No confirmation code or booking ID provided')
        setLoading(false)
        return
      }

      try {
        let result
        if (confirmationCode) {
          result = await chatAPI.getAppointmentByConfirmation(confirmationCode)
        } else {
          result = await chatAPI.getAppointmentById(bookingId)
        }

        if (result.success) {
          setAppointment(result.appointment)
        } else {
          setError('Appointment not found')
        }
      } catch (err) {
        setError(err.message || 'Failed to load appointment details')
      } finally {
        setLoading(false)
      }
    }

    fetchAppointment()
  }, [confirmationCode, bookingId])

  const handleClose = () => {
    navigate('/')
  }

  const handleNewAppointment = () => {
    navigate('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-purple-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading appointment details...</p>
        </div>
      </div>
    )
  }

  if (error || !appointment) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Appointment Not Found</h2>
          <p className="text-gray-600 mb-6">{error || 'Unable to load appointment details'}</p>
          <button
            onClick={handleClose}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 px-6 rounded-xl font-semibold transition-all"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <AppointmentConfirmation
      appointment={appointment}
      type={type}
      onClose={handleClose}
      onNewAppointment={handleNewAppointment}
    />
  )
}

export default ConfirmationPage

