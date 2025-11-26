"""
Appointments API endpoints for viewing and managing booked appointments.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.api.calendly_service import calendly_service

router = APIRouter()


@router.get("/appointments")
async def list_appointments(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    patient_email: Optional[str] = Query(None, description="Filter by patient email"),
    patient_phone: Optional[str] = Query(None, description="Filter by patient phone"),
    status: Optional[str] = Query(None, description="Filter by status (confirmed, cancelled)")
) -> Dict[str, Any]:
    """
    List all appointments with optional filters.
    
    Query Parameters:
        - date: Filter by specific date
        - patient_email: Filter by patient email
        - patient_phone: Filter by patient phone
        - status: Filter by appointment status
        
    Returns:
        Dictionary with appointments list and count
    """
    try:
        appointments = calendly_service.appointments.copy()
        
        # Apply filters
        if date:
            appointments = [a for a in appointments if a["date"] == date]
        
        if patient_email:
            appointments = [a for a in appointments 
                          if a["patient"]["email"].lower() == patient_email.lower()]
        
        if patient_phone:
            appointments = [a for a in appointments 
                          if a["patient"]["phone"] == patient_phone]
        
        if status:
            appointments = [a for a in appointments if a["status"] == status]
        
        return {
            "success": True,
            "count": len(appointments),
            "appointments": appointments
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments/{booking_id}")
async def get_appointment(booking_id: str) -> Dict[str, Any]:
    """
    Get a specific appointment by booking ID.
    
    Args:
        booking_id: The booking ID (e.g., APPT-202511-0001)
        
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments/confirmation/{confirmation_code}")
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
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/appointments/{booking_id}")
async def delete_appointment(booking_id: str, 
                            permanent: bool = Query(False, description="Permanently delete instead of just cancelling")) -> Dict[str, Any]:
    """
    Delete or cancel an appointment.
    
    Args:
        booking_id: The booking ID to delete/cancel
        permanent: If True, permanently removes the appointment. If False (default), just cancels it.
        
    Returns:
        Deletion/cancellation confirmation
    """
    try:
        if permanent:
            # Permanently remove the appointment
            success = await calendly_service.delete_appointment(booking_id)
            message = "Appointment permanently deleted"
        else:
            # Just cancel it (keeps in database)
            success = await calendly_service.cancel_appointment(booking_id)
            message = "Appointment cancelled successfully"
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with booking_id '{booking_id}' not found"
            )
        
        return {
            "success": True,
            "message": message,
            "booking_id": booking_id,
            "permanent": permanent
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments/stats/summary")
async def get_appointments_summary() -> Dict[str, Any]:
    """
    Get summary statistics of all appointments.
    
    Returns:
        Summary with counts by status, type, and upcoming appointments
    """
    try:
        appointments = calendly_service.appointments
        
        # Count by status
        status_counts: Dict[str, int] = {}
        type_counts: Dict[str, int] = {}
        upcoming_count = 0
        past_count = 0
        today = datetime.now().date()
        
        for appt in appointments:
            # Status counts
            status = appt["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Type counts
            appt_type = appt["appointment_type"]
            type_counts[appt_type] = type_counts.get(appt_type, 0) + 1
            
            # Upcoming vs past
            appt_date = datetime.strptime(appt["date"], "%Y-%m-%d").date()
            if appt_date >= today and status == "confirmed":
                upcoming_count += 1
            elif appt_date < today:
                past_count += 1
        
        return {
            "success": True,
            "total_appointments": len(appointments),
            "by_status": status_counts,
            "by_type": type_counts,
            "upcoming_confirmed": upcoming_count,
            "past_appointments": past_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

