"""
Calendly API integration.
Now uses real Calendly API with mock fallback via CalendlyService.
"""
import json
import os
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Any, Optional
import random
import string
from pathlib import Path
import logging

from backend.models.schemas import (
    TimeSlot, AvailabilityRequest, AvailabilityResponse,
    BookingRequest, BookingResponse, AppointmentDetails
)

# Import the new unified service
from backend.api.calendly_service import calendly_service, CalendlyMode

logger = logging.getLogger(__name__)


class CalendlyAPI:
    """
    Calendly API wrapper.
    
    This class now delegates to the unified CalendlyService which handles:
    - Real Calendly API integration when configured
    - Mock fallback when API is unavailable or not configured
    - Local appointment storage for consistency
    """
    
    def __init__(self):
        """Initialize the Calendly API wrapper."""
        self._service = calendly_service
        
        # For backwards compatibility - expose these properties
        self.data_dir = self._service.data_dir
        self.schedule_file = self._service.schedule_file
        self.appointments_file = self._service.appointments_file
    
    @property
    def schedule(self) -> Dict[str, Any]:
        """Get the doctor schedule (for backwards compatibility)."""
        return self._service.schedule
    
    @property
    def appointments(self) -> List[Dict[str, Any]]:
        """Get appointments list (for backwards compatibility)."""
        return self._service.appointments
    
    @property
    def mode(self) -> str:
        """Get current operating mode."""
        return self._service.mode.value
    
    @property
    def is_using_real_api(self) -> bool:
        """Check if using real Calendly API."""
        return self._service.mode == CalendlyMode.REAL
    
    def _load_appointments(self) -> List[Dict[str, Any]]:
        """Load existing appointments from file (backwards compatibility)."""
        return self._service._load_appointments()
    
    def _save_appointments(self):
        """Save appointments to file (backwards compatibility)."""
        self._service._save_appointments()
    
    def _generate_confirmation_code(self) -> str:
        """Generate a random confirmation code."""
        return self._service._generate_confirmation_code()
    
    def _generate_booking_id(self) -> str:
        """Generate a unique booking ID."""
        return self._service._generate_booking_id()
    
    def _parse_time(self, time_str: str) -> dt_time:
        """Parse time string (HH:MM) to time object."""
        return self._service._parse_time(time_str)
    
    def _time_to_str(self, time_obj: dt_time) -> str:
        """Convert time object to string (HH:MM)."""
        return self._service._time_to_str(time_obj)
    
    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string."""
        return self._service._add_minutes_to_time(time_str, minutes)
    
    def _is_blocked_date(self, date_str: str) -> bool:
        """Check if date is blocked."""
        return date_str in self._service.schedule.get("blocked_dates", [])
    
    def _get_working_hours(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Get working hours for a specific date."""
        return self._service._get_working_hours(date_str)
    
    def _generate_time_slots(self, date_str: str, working_hours: Dict[str, Any]) -> List[str]:
        """Generate all possible time slots for a day."""
        return self._service._generate_time_slots(date_str, working_hours)
    
    def _is_slot_available(self, date_str: str, start_time: str, slots_required: int) -> bool:
        """Check if a slot (and required subsequent slots) is available."""
        return self._service._is_slot_available(date_str, start_time, slots_required)
    
    async def get_availability(self, request: AvailabilityRequest) -> AvailabilityResponse:
        """
        Get available time slots for a specific date and appointment type.
        Uses real Calendly API if configured, otherwise falls back to mock.
        """
        return await self._service.get_availability(request)
    
    async def book_appointment(self, request: BookingRequest) -> BookingResponse:
        """
        Book an appointment.
        Uses real Calendly API if configured, otherwise falls back to mock.
        """
        return await self._service.book_appointment(request)
    
    async def get_appointment(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by booking ID."""
        return await self._service.get_appointment(booking_id)
    
    async def cancel_appointment(self, booking_id: str, reason: str = None) -> bool:
        """Cancel an appointment."""
        return await self._service.cancel_appointment(booking_id, reason)
    
    async def get_next_available_dates(self, appointment_type: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get next available dates with slots for an appointment type."""
        return await self._service.get_next_available_dates(appointment_type, num_days)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return self._service.get_status()


# Backwards-compatible aliases
MockCalendlyAPI = CalendlyAPI

# Global instance
calendly_api = CalendlyAPI()
