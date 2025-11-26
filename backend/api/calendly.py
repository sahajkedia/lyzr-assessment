"""
Mock Calendly API router for scheduling operations.
Provides endpoints for availability, booking, rescheduling, and cancellation.
Uses mock implementation only (no real Calendly API).
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from backend.api.calendly_service import calendly_service
from backend.models.schemas import (
    AvailabilityRequest, AvailabilityResponse,
    BookingRequest, BookingResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/availability", response_model=AvailabilityResponse)
async def check_availability(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    appointment_type: str = Query(..., description="Type of appointment: consultation, followup, physical, specialist")
) -> AvailabilityResponse:
    """
    Check available time slots for a specific date and appointment type.
    
    Args:
        date: Date in YYYY-MM-DD format (e.g., "2024-01-15")
        appointment_type: Type of appointment (consultation, followup, physical, specialist)
        
    Returns:
        Available time slots
        
    Example:
        GET /api/calendly/availability?date=2024-01-15&appointment_type=consultation
    """
    try:
        # Create request object from query params
        from backend.models.schemas import AvailabilityRequest
        request = AvailabilityRequest(date=date, appointment_type=appointment_type)
        availability = await calendly_service.get_availability(request)
        return availability
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Availability check failed: {e}")
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
        dates = await calendly_service.get_next_available_dates(appointment_type, days)
        return {
            "success": True,
            "appointment_type": appointment_type,
            "available_dates": dates
        }
    except Exception as e:
        logger.error(f"Get next dates failed: {e}")
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
        booking = await calendly_service.book_appointment(request)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Booking failed: {e}")
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
        appointment = await calendly_service.get_appointment(booking_id)
        
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
        logger.error(f"Get appointment failed: {e}")
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
        appointment = await calendly_service.get_appointment(booking_id)
        
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
        appt_details = calendly_service.schedule["appointment_types"][appt_type]
        duration = appt_details["duration"]
        slots_required = appt_details["slots_required"]
        
        # Check if new slot is available
        if not calendly_service._is_slot_available(new_date, new_time, slots_required):
            raise HTTPException(
                status_code=400,
                detail="The selected time slot is not available"
            )
        
        # Update appointment
        new_end_time = calendly_service._add_minutes_to_time(new_time, duration)
        
        for appt in calendly_service.appointments:
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
                
                calendly_service._save_appointments()
                
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
        logger.error(f"Reschedule failed: {e}")
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
        appointment = await calendly_service.get_appointment(booking_id)
        
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with booking_id '{booking_id}' not found"
            )
        
        if appointment["status"] == "cancelled":
            # Return success with a message indicating it was already cancelled
            return {
                "success": True,
                "message": "Appointment was already cancelled",
                "booking_id": booking_id,
                "cancelled_at": appointment.get("cancelled_at"),
                "appointment": appointment,
                "already_cancelled": True
            }
        
        # Cancel the appointment via service (handles both real and mock)
        success = await calendly_service.cancel_appointment(booking_id, reason)
        
        if success:
            # Get updated appointment
            updated_appt = await calendly_service.get_appointment(booking_id)
            return {
                "success": True,
                "message": "Appointment cancelled successfully",
                "booking_id": booking_id,
                "cancelled_at": updated_appt.get("cancelled_at"),
                "appointment": updated_appt
            }
        
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancellation failed: {e}")
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
        appointments = calendly_service.appointments
        
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
        logger.error(f"Get by confirmation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_appointment_types() -> Dict[str, Any]:
    """
    Get all available appointment types and their details.
    
    Returns:
        List of appointment types with durations and descriptions
    """
    try:
        types = calendly_service.schedule["appointment_types"]
        return {
            "success": True,
            "appointment_types": types
        }
    except Exception as e:
        logger.error(f"Get appointment types failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_calendly_status() -> Dict[str, Any]:
    """
    Get Calendly service status.
    Shows mock service configuration and statistics.
    
    Returns:
        Service status information (always mock mode)
    """
    try:
        await calendly_service.initialize()
        status = calendly_service.get_status()
        return {
            "success": True,
            "status": status,
            "message": "Mock Calendly service active"
        }
    except Exception as e:
        logger.error(f"Get status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


