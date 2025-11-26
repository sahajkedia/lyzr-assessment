import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import { Calendar, Heart, Shield, Clock } from 'lucide-react'

function App() {
  const [showChat, setShowChat] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-medical-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Heart className="w-6 h-6 text-white" fill="white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">HealthCare Plus</h1>
                <p className="text-sm text-gray-500">Medical Appointment Scheduler</p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>24/7 Support</span>
              </div>
              <div className="flex items-center space-x-1">
                <Shield className="w-4 h-4" />
                <span>HIPAA Compliant</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className={`mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 ${showChat ? 'max-w-[95%] xl:max-w-[90%]' : 'max-w-7xl'}`}>
        <div className={`${showChat ? 'grid lg:grid-cols-[1fr_4fr] gap-4 lg:gap-6' : 'grid lg:grid-cols-2 gap-8'} items-start transition-all duration-500`}>
          {/* Left Side - Info */}
          <div className={`space-y-4 lg:space-y-6 animate-fade-in ${showChat ? 'hidden lg:block' : ''}`}>
            <div className="bg-white rounded-2xl shadow-lg p-4 lg:p-8 border border-gray-200">
              <div className="flex items-center space-x-3 mb-4">
                <Calendar className={`${showChat ? 'w-6 h-6' : 'w-8 h-8'} text-primary-600 transition-all`} />
                <h2 className={`${showChat ? 'text-xl' : 'text-3xl'} font-bold text-gray-900 transition-all`}>
                  {showChat ? 'Info' : 'Schedule Your Appointment'}
                </h2>
              </div>
              {!showChat && (
                <>
                  <p className="text-gray-600 text-lg mb-6">
                    Our intelligent AI assistant is here to help you book appointments, 
                    answer questions, and guide you through the process.
                  </p>

                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className="bg-medical-100 rounded-full p-2 mt-1">
                        <svg className="w-5 h-5 text-medical-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">Natural Conversation</h3>
                        <p className="text-gray-600">Just chat naturally - our AI understands your needs</p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <div className="bg-medical-100 rounded-full p-2 mt-1">
                        <svg className="w-5 h-5 text-medical-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">Real-Time Availability</h3>
                        <p className="text-gray-600">See available slots and book instantly</p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <div className="bg-medical-100 rounded-full p-2 mt-1">
                        <svg className="w-5 h-5 text-medical-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">Instant Answers</h3>
                        <p className="text-gray-600">Get answers about insurance, location, and policies</p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <div className="bg-medical-100 rounded-full p-2 mt-1">
                        <svg className="w-5 h-5 text-medical-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">Multiple Appointment Types</h3>
                        <p className="text-gray-600">Consultation, Follow-up, Physical Exam, or Specialist</p>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {!showChat && (
                <button
                  onClick={() => setShowChat(true)}
                  className="mt-8 w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-4 px-6 rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105 flex items-center justify-center space-x-2"
                >
                  <Calendar className="w-5 h-5" />
                  <span>Start Scheduling</span>
                </button>
              )}

              {showChat && (
                <div className="space-y-3 text-sm">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-primary-600" />
                    <span className="text-gray-700">15 min wait</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Heart className="w-4 h-4 text-medical-600" />
                    <span className="text-gray-700">98% satisfaction</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Shield className="w-4 h-4 text-primary-600" />
                    <span className="text-gray-700">HIPAA secure</span>
                  </div>
                </div>
              )}
            </div>

            {/* Quick Info Cards - Only show when chat is not active */}
            {!showChat && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-xl shadow p-4 border border-gray-200">
                  <div className="text-2xl font-bold text-primary-600 mb-1">15 min</div>
                  <div className="text-sm text-gray-600">Average Wait Time</div>
                </div>
                <div className="bg-white rounded-xl shadow p-4 border border-gray-200">
                  <div className="text-2xl font-bold text-medical-600 mb-1">98%</div>
                  <div className="text-sm text-gray-600">Patient Satisfaction</div>
                </div>
              </div>
            )}
          </div>

          {/* Right Side - Chat Interface */}
          <div className={`${showChat ? 'lg:col-span-1' : ''}`}>
            {showChat ? (
              <ChatInterface />
            ) : (
              <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200 text-center animate-pulse-slow lg:sticky lg:top-8">
                <div className="w-24 h-24 bg-gradient-to-br from-primary-100 to-medical-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <Calendar className="w-12 h-12 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Ready to Get Started?
                </h3>
                <p className="text-gray-600">
                  Click "Start Scheduling" to begin your appointment booking
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>© 2024 HealthCare Plus Clinic. All rights reserved.</p>
            <p className="mt-1">123 Medical Center Dr, Suite 100, New York, NY 10001 • +1-555-123-4567</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

