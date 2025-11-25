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
    }
]

