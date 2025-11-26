"""
Calendly API router for scheduling operations.
Provides endpoints for availability, booking, rescheduling, and cancellation.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from backend.api.calendly_integration import calendly_api
from backend.models.schemas import (
    AvailabilityRequest, AvailabilityResponse,
    BookingRequest, BookingResponse
)

router = APIRouter()


@router.post("/availability", response_model=AvailabilityResponse)
async def check_availability(request: AvailabilityRequest) -> AvailabilityResponse:
    """
    Check available time slots for a specific date and appointment type.
    
    Args:
        request: Availability request with date and appointment type
        
    Returns:
        Available time slots
    """
    try:
        availability = await calendly_api.get_availability(request)
        return availability
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/availability/next-dates")
async def get_next_available_dates(
    appointment_type: str = Query(..., description="Type of appointment"),
    days: int = Query(7, description="Number of days to check", ge=1, le=30)
) -> Dict[str, Any]:
    """
    Get next available dates with time slots.
    
    Args:
        appointment_type: Type of appointment
        days: Number of days to check ahead
        
    Returns:
        List of available dates with sample time slots
    """
    try:
        dates = await calendly_api.get_next_available_dates(appointment_type, days)
        return {
            "success": True,
            "appointment_type": appointment_type,
            "available_dates": dates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book", response_model=BookingResponse)
async def book_appointment(request: BookingRequest) -> BookingResponse:
    """
    Book a new appointment.
    
    Args:
        request: Booking request with all appointment details
        
    Returns:
        Booking confirmation with booking ID and confirmation code
    """
    try:
        booking = await calendly_api.book_appointment(request)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointment/{booking_id}")
async def get_appointment(booking_id: str) -> Dict[str, Any]:
    """
    Get appointment details by booking ID.
    
    Args:
        booking_id: The booking ID
        
    Returns:
        Appointment details
    """
    try:
        appointment = await calendly_api.get_appointment(booking_id)
        
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with booking_id '{booking_id}' not found"
            )
        
        return {
            "success": True,
            "appointment": appointment
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reschedule/{booking_id}")
async def reschedule_appointment(
    booking_id: str,
    new_date: str = Query(..., description="New date in YYYY-MM-DD format"),
    new_time: str = Query(..., description="New start time in HH:MM format")
) -> Dict[str, Any]:
    """
    Reschedule an existing appointment to a new date/time.
    
    Args:
        booking_id: The booking ID to reschedule
        new_date: New date in YYYY-MM-DD format
        new_time: New start time in HH:MM format
        
    Returns:
        Updated appointment details
    """
    try:
        # Get existing appointment
        appointment = await calendly_api.get_appointment(booking_id)
        
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with booking_id '{booking_id}' not found"
            )
        
        if appointment["status"] == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Cannot reschedule a cancelled appointment"
            )
        
        # Get appointment type details
        appt_type = appointment["appointment_type"]
        appt_details = calendly_api.schedule["appointment_types"][appt_type]
        duration = appt_details["duration"]
        slots_required = appt_details["slots_required"]
        
        # Check if new slot is available
        if not calendly_api._is_slot_available(new_date, new_time, slots_required):
            raise HTTPException(
                status_code=400,
                detail="The selected time slot is not available"
            )
        
        # Update appointment
        new_end_time = calendly_api._add_minutes_to_time(new_time, duration)
        
        for appt in calendly_api.appointments:
            if appt["booking_id"] == booking_id:
                # Store old details for response
                old_date = appt["date"]
                old_time = appt["start_time"]
                
                # Update to new date/time
                appt["date"] = new_date
                appt["start_time"] = new_time
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
                    "new_time": new_time,
                    "appointment": appt
                }
        
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel/{booking_id}")
async def cancel_appointment(
    booking_id: str,
    reason: Optional[str] = Query(None, description="Reason for cancellation")
) -> Dict[str, Any]:
    """
    Cancel an appointment.
    
    Args:
        booking_id: The booking ID to cancel
        reason: Optional reason for cancellation
        
    Returns:
        Cancellation confirmation
    """
    try:
        # Get existing appointment
        appointment = await calendly_api.get_appointment(booking_id)
        
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with booking_id '{booking_id}' not found"
            )
        
        if appointment["status"] == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Appointment is already cancelled"
            )
        
        # Cancel the appointment
        for appt in calendly_api.appointments:
            if appt["booking_id"] == booking_id:
                appt["status"] = "cancelled"
                appt["cancelled_at"] = datetime.now().isoformat()
                if reason:
                    appt["cancellation_reason"] = reason
                
                calendly_api._save_appointments()
                
                return {
                    "success": True,
                    "message": "Appointment cancelled successfully",
                    "booking_id": booking_id,
                    "cancelled_at": appt["cancelled_at"],
                    "appointment": appt
                }
        
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointment/confirmation/{confirmation_code}")
async def get_appointment_by_confirmation(confirmation_code: str) -> Dict[str, Any]:
    """
    Get appointment by confirmation code.
    
    Args:
        confirmation_code: The 6-character confirmation code
        
    Returns:
        Appointment details
    """
    try:
        appointments = calendly_api.appointments
        
        for appt in appointments:
            if appt["confirmation_code"] == confirmation_code.upper():
                return {
                    "success": True,
                    "appointment": appt
                }
        
        raise HTTPException(
            status_code=404,
            detail=f"Appointment with confirmation code '{confirmation_code}' not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_appointment_types() -> Dict[str, Any]:
    """
    Get all available appointment types and their details.
    
    Returns:
        List of appointment types with durations and descriptions
    """
    try:
        types = calendly_api.schedule["appointment_types"]
        return {
            "success": True,
            "appointment_types": types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_calendly_status() -> Dict[str, Any]:
    """
    Get the current Calendly integration status.
    
    Returns:
        Status information including mode (real/mock/fallback)
    """
    try:
        status = calendly_api.get_status()
        return {
            "success": True,
            "status": status,
            "message": f"Calendly service running in {status['mode'].upper()} mode"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


