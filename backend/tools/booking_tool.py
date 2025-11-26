"""
Tool for booking appointments.
"""
from typing import Dict, Any
from datetime import datetime

from backend.api.calendly_integration import calendly_api
from backend.models.schemas import BookingRequest, PatientInfo


async def book_appointment(
    appointment_type: str,
    date: str,
    start_time: str,
    patient_name: str,
    patient_email: str,
    patient_phone: str,
    reason: str
) -> Dict[str, Any]:
    """
    Book an appointment.
    
    Args:
        appointment_type: Type of appointment
        date: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM format
        patient_name: Patient's full name
        patient_email: Patient's email
        patient_phone: Patient's phone number
        reason: Reason for visit
        
    Returns:
        Dictionary with booking confirmation
    """
    try:
        # Create patient info
        patient = PatientInfo(
            name=patient_name,
            email=patient_email,
            phone=patient_phone
        )
        
        # Create booking request
        request = BookingRequest(
            appointment_type=appointment_type,
            date=date,
            start_time=start_time,
            patient=patient,
            reason=reason
        )
        
        # Book appointment
        booking = await calendly_api.book_appointment(request)
        
        return {
            "success": True,
            "booking_id": booking.booking_id,
            "confirmation_code": booking.confirmation_code,
            "status": booking.status,
            "details": booking.details
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def cancel_appointment(booking_id: str) -> Dict[str, Any]:
    """
    Cancel an appointment.
    
    Args:
        booking_id: The booking ID to cancel
        
    Returns:
        Dictionary with cancellation status
    """
    try:
        success = await calendly_api.cancel_appointment(booking_id)
        
        if success:
            return {
                "success": True,
                "message": "Appointment cancelled successfully",
                "booking_id": booking_id
            }
        else:
            return {
                "success": False,
                "error": "Appointment not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_appointment_details(booking_id: str) -> Dict[str, Any]:
    """
    Get details of an appointment.
    
    Args:
        booking_id: The booking ID
        
    Returns:
        Dictionary with appointment details
    """
    try:
        appointment = await calendly_api.get_appointment(booking_id)
        
        if appointment:
            return {
                "success": True,
                "appointment": appointment
            }
        else:
            return {
                "success": False,
                "error": "Appointment not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def reschedule_appointment(
    booking_id: str,
    new_date: str,
    new_start_time: str
) -> Dict[str, Any]:
    """
    Reschedule an existing appointment to a new date/time.
    
    Args:
        booking_id: The booking ID to reschedule
        new_date: New date in YYYY-MM-DD format
        new_start_time: New start time in HH:MM format
        
    Returns:
        Dictionary with rescheduling confirmation
    """
    try:
        # Get existing appointment
        appointment = await calendly_api.get_appointment(booking_id)
        
        if not appointment:
            return {
                "success": False,
                "error": "Appointment not found"
            }
        
        if appointment["status"] == "cancelled":
            return {
                "success": False,
                "error": "Cannot reschedule a cancelled appointment"
            }
        
        # Get appointment type details
        appt_type = appointment["appointment_type"]
        appt_details = calendly_api.schedule["appointment_types"][appt_type]
        duration = appt_details["duration"]
        slots_required = appt_details["slots_required"]
        
        # Check if new slot is available
        if not calendly_api._is_slot_available(new_date, new_start_time, slots_required):
            return {
                "success": False,
                "error": "The selected time slot is not available"
            }
        
        # Update appointment
        new_end_time = calendly_api._add_minutes_to_time(new_start_time, duration)
        
        for appt in calendly_api.appointments:
            if appt["booking_id"] == booking_id:
                # Store old details
                old_date = appt["date"]
                old_time = appt["start_time"]
                
                # Update to new date/time
                appt["date"] = new_date
                appt["start_time"] = new_start_time
                appt["end_time"] = new_end_time
                appt["rescheduled_at"] = datetime.now().isoformat()
                appt["previous_date"] = old_date
                appt["previous_time"] = old_time
                
                calendly_api._save_appointments()
                
                return {
                    "success": True,
                    "message": "Appointment rescheduled successfully",
                    "booking_id": booking_id,
                    "old_date": old_date,
                    "old_time": old_time,
                    "new_date": new_date,
                    "new_time": new_start_time,
                    "confirmation_code": appt["confirmation_code"]
                }
        
        return {
            "success": False,
            "error": "Appointment not found"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_appointment_by_confirmation(confirmation_code: str) -> Dict[str, Any]:
    """
    Get appointment details by confirmation code.
    
    Args:
        confirmation_code: The 6-character confirmation code
        
    Returns:
        Dictionary with appointment details
    """
    try:
        for appt in calendly_api.appointments:
            if appt["confirmation_code"] == confirmation_code.upper():
                return {
                    "success": True,
                    "appointment": appt
                }
        
        return {
            "success": False,
            "error": "Appointment not found with this confirmation code"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Tool definitions for LLM
BOOKING_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment after collecting all required information from the patient. Only use this when you have confirmed all details with the patient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_type": {
                        "type": "string",
                        "enum": ["consultation", "followup", "physical", "specialist"],
                        "description": "Type of appointment"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in HH:MM format (24-hour)"
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Patient's full name"
                    },
                    "patient_email": {
                        "type": "string",
                        "description": "Patient's email address"
                    },
                    "patient_phone": {
                        "type": "string",
                        "description": "Patient's phone number"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for visit"
                    }
                },
                "required": [
                    "appointment_type",
                    "date",
                    "start_time",
                    "patient_name",
                    "patient_email",
                    "patient_phone",
                    "reason"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointment_by_confirmation",
            "description": "Retrieve appointment details using the confirmation code. Use this when a patient wants to view, cancel, or reschedule their appointment using their confirmation code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "confirmation_code": {
                        "type": "string",
                        "description": "The 6-character confirmation code (e.g., 1I6P5C)"
                    }
                },
                "required": ["confirmation_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment. Only use this after confirming with the patient that they want to cancel. Always retrieve the appointment details first to show what will be cancelled.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {
                        "type": "string",
                        "description": "The booking ID of the appointment to cancel"
                    }
                },
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_appointment",
            "description": "Reschedule an existing appointment to a new date and time. Check availability first, then confirm the new time with the patient before rescheduling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {
                        "type": "string",
                        "description": "The booking ID of the appointment to reschedule"
                    },
                    "new_date": {
                        "type": "string",
                        "description": "New date in YYYY-MM-DD format"
                    },
                    "new_start_time": {
                        "type": "string",
                        "description": "New start time in HH:MM format (24-hour)"
                    }
                },
                "required": ["booking_id", "new_date", "new_start_time"]
            }
        }
    }
]

