"""
Unified Calendly Service.
Uses real Calendly API when configured, falls back to mock implementation.
"""
import os
import json
import logging
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Any, Optional
import random
import string
from pathlib import Path
from enum import Enum

from backend.models.schemas import (
    TimeSlot, AvailabilityRequest, AvailabilityResponse,
    BookingRequest, BookingResponse, AppointmentDetails
)
from backend.api.calendly_client import CalendlyClient, CalendlyAPIError, calendly_client

logger = logging.getLogger(__name__)


class CalendlyMode(Enum):
    """Operating mode for Calendly service."""
    REAL = "real"       # Using real Calendly API
    MOCK = "mock"       # Using mock implementation
    FALLBACK = "fallback"  # Real API failed, using mock


class CalendlyService:
    """
    Unified Calendly service with real API and mock fallback.
    
    Priority:
    1. Try real Calendly API if configured
    2. Fall back to mock if API fails or is not configured
    3. Sync local appointments with Calendly when possible
    """
    
    def __init__(self):
        self.client = calendly_client
        self.mode = CalendlyMode.MOCK
        self._initialized = False
        
        # Local storage for mock/fallback
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.schedule_file = self.data_dir / "doctor_schedule.json"
        self.appointments_file = self.data_dir / "appointments.json"
        
        # Load schedule for mock mode
        self.schedule = self._load_schedule()
        self.appointments = self._load_appointments()
        
        # Event type mapping (local type -> Calendly event type URI)
        self._event_type_map: Dict[str, str] = {}
    
    def _load_schedule(self) -> Dict[str, Any]:
        """Load doctor schedule from file."""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                return json.load(f)
        return {
            "working_hours": {},
            "appointment_types": {},
            "blocked_dates": [],
            "appointment_slot_duration": 30
        }
    
    def _load_appointments(self) -> List[Dict[str, Any]]:
        """Load existing appointments from file."""
        if self.appointments_file.exists():
            with open(self.appointments_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_appointments(self):
        """Save appointments to file."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.appointments_file, 'w') as f:
            json.dump(self.appointments, f, indent=2, default=str)
    
    async def initialize(self) -> CalendlyMode:
        """
        Initialize the service and determine operating mode.
        
        Returns:
            The mode the service is operating in
        """
        if self._initialized:
            return self.mode
        
        # Check if Calendly is configured
        if self.client.is_configured:
            logger.info("Calendly API key found, attempting connection...")
            try:
                connected = await self.client.verify_connection()
                if connected:
                    self.mode = CalendlyMode.REAL
                    logger.info("✅ Connected to Calendly API - using REAL mode")
                    
                    # Map event types
                    await self._map_event_types()
                else:
                    self.mode = CalendlyMode.MOCK
                    logger.warning("❌ Calendly connection failed - using MOCK mode")
            except Exception as e:
                self.mode = CalendlyMode.MOCK
                logger.error(f"❌ Calendly initialization error: {e} - using MOCK mode")
        else:
            self.mode = CalendlyMode.MOCK
            logger.info("📋 No Calendly API key configured - using MOCK mode")
        
        self._initialized = True
        return self.mode
    
    async def _map_event_types(self):
        """Map local appointment types to Calendly event types."""
        try:
            event_types = await self.client.get_event_types()
            
            local_types = ["consultation", "followup", "physical", "specialist"]
            
            for local_type in local_types:
                for et in event_types:
                    name = et.get("name", "").lower()
                    slug = et.get("slug", "").lower()
                    
                    if local_type in name or local_type in slug:
                        self._event_type_map[local_type] = et.get("uri")
                        logger.info(f"Mapped '{local_type}' -> '{et.get('name')}'")
                        break
                
                # If no match found, use first event type as default
                if local_type not in self._event_type_map and event_types:
                    self._event_type_map[local_type] = event_types[0].get("uri")
            
            logger.info(f"Event type mapping complete: {len(self._event_type_map)} types mapped")
            
        except Exception as e:
            logger.error(f"Failed to map event types: {e}")
    
    # ==================== Availability ====================
    
    async def get_availability(self, request: AvailabilityRequest) -> AvailabilityResponse:
        """Get available time slots for a specific date and appointment type."""
        await self.initialize()
        
        if self.mode == CalendlyMode.REAL:
            try:
                return await self._get_availability_real(request)
            except CalendlyAPIError as e:
                logger.warning(f"Calendly API error: {e.message} - falling back to mock")
                self.mode = CalendlyMode.FALLBACK
        
        return await self._get_availability_mock(request)
    
    async def _get_availability_real(self, request: AvailabilityRequest) -> AvailabilityResponse:
        """Get availability from real Calendly API."""
        date_str = request.date
        appt_type = request.appointment_type
        
        # Get event type URI
        event_type_uri = self._event_type_map.get(appt_type)
        if not event_type_uri:
            raise CalendlyAPIError(f"Event type '{appt_type}' not mapped")
        
        # Format date range for API
        start_time = f"{date_str}T00:00:00Z"
        end_time = f"{date_str}T23:59:59Z"
        
        # Get available times from Calendly
        available_times = await self.client.get_available_times(
            event_type_uri=event_type_uri,
            start_time=start_time,
            end_time=end_time,
        )
        
        # Convert to our format
        slots = []
        for at in available_times:
            start = datetime.fromisoformat(at.get("start_time", "").replace("Z", "+00:00"))
            # Calculate end time based on event type duration
            end_str = at.get("end_time", "")
            if end_str:
                end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            else:
                end = start + timedelta(minutes=30)  # Default 30 min
            
            slots.append(TimeSlot(
                start_time=start.strftime("%H:%M"),
                end_time=end.strftime("%H:%M"),
                available=True,
            ))
        
        return AvailabilityResponse(
            date=date_str,
            appointment_type=appt_type,
            available_slots=slots,
            total_available=len(slots),
        )
    
    async def _get_availability_mock(self, request: AvailabilityRequest) -> AvailabilityResponse:
        """Get availability from mock implementation."""
        date_str = request.date
        appt_type = request.appointment_type
        
        # Validate appointment type
        if appt_type not in self.schedule["appointment_types"]:
            raise ValueError(f"Invalid appointment type: {appt_type}")
        
        # Check if date is in the past
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj < datetime.now().date():
            return AvailabilityResponse(
                date=date_str,
                appointment_type=appt_type,
                available_slots=[],
                total_available=0
            )
        
        # Check if date is blocked
        if date_str in self.schedule.get("blocked_dates", []):
            return AvailabilityResponse(
                date=date_str,
                appointment_type=appt_type,
                available_slots=[],
                total_available=0
            )
        
        # Get working hours
        working_hours = self._get_working_hours(date_str)
        if not working_hours:
            return AvailabilityResponse(
                date=date_str,
                appointment_type=appt_type,
                available_slots=[],
                total_available=0
            )
        
        # Get appointment details
        appt_details = self.schedule["appointment_types"][appt_type]
        duration = appt_details["duration"]
        slots_required = appt_details["slots_required"]
        
        # Generate time slots
        all_slots = self._generate_time_slots(date_str, working_hours)
        
        # Check availability
        available_slots = []
        for slot_time in all_slots:
            if self._is_slot_available(date_str, slot_time, slots_required):
                end_time = self._add_minutes_to_time(slot_time, duration)
                available_slots.append(TimeSlot(
                    start_time=slot_time,
                    end_time=end_time,
                    available=True
                ))
        
        return AvailabilityResponse(
            date=date_str,
            appointment_type=appt_type,
            available_slots=available_slots,
            total_available=len(available_slots)
        )
    
    # ==================== Booking ====================
    
    async def book_appointment(self, request: BookingRequest) -> BookingResponse:
        """Book an appointment."""
        await self.initialize()
        
        if self.mode == CalendlyMode.REAL:
            try:
                return await self._book_appointment_real(request)
            except CalendlyAPIError as e:
                logger.warning(f"Calendly API error: {e.message} - falling back to mock")
                self.mode = CalendlyMode.FALLBACK
        
        return await self._book_appointment_mock(request)
    
    async def _book_appointment_real(self, request: BookingRequest) -> BookingResponse:
        """Book appointment via real Calendly API."""
        # Get event type URI
        event_type_uri = self._event_type_map.get(request.appointment_type)
        if not event_type_uri:
            raise CalendlyAPIError(f"Event type '{request.appointment_type}' not mapped")
        
        # Format start time for API
        start_time = self.client.format_datetime_for_api(request.date, request.start_time)
        
        # Create the event via Scheduling API
        result = await self.client.create_scheduled_event(
            event_type_uri=event_type_uri,
            start_time=start_time,
            invitee_email=request.patient.email,
            invitee_name=request.patient.name,
            invitee_phone=request.patient.phone,
            custom_answers=[
                {"question": "Reason for visit", "answer": request.reason}
            ],
        )
        
        # Extract event details
        event_uri = result.get("uri", "")
        event_uuid = self.client._extract_uuid(event_uri)
        
        # Generate our own confirmation code for easy reference
        confirmation_code = self._generate_confirmation_code()
        booking_id = f"CAL-{event_uuid[:8].upper()}"
        
        # Calculate end time
        appt_details = self.schedule["appointment_types"].get(
            request.appointment_type,
            {"duration": 30}
        )
        duration = appt_details.get("duration", 30)
        end_time = self._add_minutes_to_time(request.start_time, duration)
        
        # Create local record for our system
        appointment = {
            "booking_id": booking_id,
            "calendly_event_uri": event_uri,
            "calendly_event_uuid": event_uuid,
            "appointment_type": request.appointment_type,
            "date": request.date,
            "start_time": request.start_time,
            "end_time": end_time,
            "patient": {
                "name": request.patient.name,
                "email": request.patient.email,
                "phone": request.patient.phone,
            },
            "reason": request.reason,
            "confirmation_code": confirmation_code,
            "status": "confirmed",
            "source": "calendly",
            "created_at": datetime.now().isoformat(),
        }
        
        # Save locally as well
        self.appointments.append(appointment)
        self._save_appointments()
        
        logger.info(f"✅ Appointment booked via Calendly: {booking_id}")
        
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            confirmation_code=confirmation_code,
            details=appointment,
        )
    
    async def _book_appointment_mock(self, request: BookingRequest) -> BookingResponse:
        """Book appointment via mock implementation."""
        date_str = request.date
        start_time = request.start_time
        appt_type = request.appointment_type
        
        # Validate appointment type
        if appt_type not in self.schedule["appointment_types"]:
            raise ValueError(f"Invalid appointment type: {appt_type}")
        
        # Get appointment details
        appt_details = self.schedule["appointment_types"][appt_type]
        duration = appt_details["duration"]
        slots_required = appt_details["slots_required"]
        
        # Check if slot is available
        if not self._is_slot_available(date_str, start_time, slots_required):
            raise ValueError("The selected time slot is no longer available")
        
        # Calculate end time
        end_time = self._add_minutes_to_time(start_time, duration)
        
        # Generate booking details
        booking_id = self._generate_booking_id()
        confirmation_code = self._generate_confirmation_code()
        
        # Create appointment record
        appointment = {
            "booking_id": booking_id,
            "appointment_type": appt_type,
            "date": date_str,
            "start_time": start_time,
            "end_time": end_time,
            "patient": {
                "name": request.patient.name,
                "email": request.patient.email,
                "phone": request.patient.phone,
            },
            "reason": request.reason,
            "confirmation_code": confirmation_code,
            "status": "confirmed",
            "source": "mock",
            "created_at": datetime.now().isoformat(),
        }
        
        # Save appointment
        self.appointments.append(appointment)
        self._save_appointments()
        
        logger.info(f"📋 Appointment booked via mock: {booking_id}")
        
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            confirmation_code=confirmation_code,
            details=appointment,
        )
    
    # ==================== Get/Cancel/Reschedule ====================
    
    async def get_appointment(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by booking ID."""
        for appt in self.appointments:
            if appt["booking_id"] == booking_id:
                return appt
        return None
    
    async def cancel_appointment(self, booking_id: str, reason: str = None) -> bool:
        """Cancel an appointment."""
        await self.initialize()
        
        for i, appt in enumerate(self.appointments):
            if appt["booking_id"] == booking_id:
                # If it's a Calendly appointment, cancel via API
                if self.mode == CalendlyMode.REAL and appt.get("calendly_event_uuid"):
                    try:
                        await self.client.cancel_scheduled_event(
                            event_uuid=appt["calendly_event_uuid"],
                            reason=reason,
                        )
                        logger.info(f"✅ Cancelled via Calendly: {booking_id}")
                    except CalendlyAPIError as e:
                        logger.warning(f"Calendly cancel failed: {e.message} - updating local only")
                
                # Update local record
                self.appointments[i]["status"] = "cancelled"
                self.appointments[i]["cancelled_at"] = datetime.now().isoformat()
                if reason:
                    self.appointments[i]["cancellation_reason"] = reason
                
                self._save_appointments()
                return True
        
        return False
    
    async def get_next_available_dates(
        self,
        appointment_type: str,
        num_days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get next available dates with slots for an appointment type."""
        available_dates = []
        current_date = datetime.now().date()
        
        for i in range(num_days):
            check_date = current_date + timedelta(days=i)
            date_str = check_date.strftime("%Y-%m-%d")
            
            # Skip weekends if not in schedule
            day_name = check_date.strftime("%A").lower()
            if self.schedule["working_hours"].get(day_name) == "closed":
                continue
            
            # Get availability
            request = AvailabilityRequest(date=date_str, appointment_type=appointment_type)
            availability = await self.get_availability(request)
            
            if availability.total_available > 0:
                slots = [
                    {"start_time": slot.start_time, "end_time": slot.end_time}
                    for slot in availability.available_slots[:3]
                ]
                available_dates.append({
                    "date": date_str,
                    "day_name": check_date.strftime("%A"),
                    "total_slots": availability.total_available,
                    "sample_slots": slots,
                })
        
        return available_dates
    
    # ==================== Helper Methods ====================
    
    def _generate_confirmation_code(self) -> str:
        """Generate a random confirmation code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def _generate_booking_id(self) -> str:
        """Generate a unique booking ID."""
        date_part = datetime.now().strftime("%Y%m")
        number_part = str(len(self.appointments) + 1).zfill(4)
        return f"APPT-{date_part}-{number_part}"
    
    def _parse_time(self, time_str: str) -> dt_time:
        """Parse time string (HH:MM) to time object."""
        return datetime.strptime(time_str, "%H:%M").time()
    
    def _time_to_str(self, time_obj: dt_time) -> str:
        """Convert time object to string (HH:MM)."""
        return time_obj.strftime("%H:%M")
    
    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string."""
        dt = datetime.strptime(time_str, "%H:%M")
        dt += timedelta(minutes=minutes)
        return dt.strftime("%H:%M")
    
    def _get_working_hours(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Get working hours for a specific date."""
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A").lower()
        
        working_hours = self.schedule["working_hours"].get(day_name)
        
        if not working_hours or working_hours == "closed":
            return None
        
        return working_hours
    
    def _generate_time_slots(self, date_str: str, working_hours: Dict[str, Any]) -> List[str]:
        """Generate all possible time slots for a day."""
        slot_duration = self.schedule.get("appointment_slot_duration", 30)
        slots = []
        
        start_time = self._parse_time(working_hours["start"])
        end_time = self._parse_time(working_hours["end"])
        
        # Handle lunch break
        lunch = working_hours.get("lunch")
        lunch_start = self._parse_time(lunch["start"]) if lunch else None
        lunch_end = self._parse_time(lunch["end"]) if lunch else None
        
        current_time = start_time
        
        while True:
            current_dt = datetime.combine(datetime.today(), current_time)
            next_dt = current_dt + timedelta(minutes=slot_duration)
            next_time = next_dt.time()
            
            if next_time > end_time:
                break
            
            # Skip lunch break
            if lunch_start and lunch_end:
                if not (current_time >= lunch_end or next_time <= lunch_start):
                    current_time = lunch_end
                    continue
            
            slots.append(self._time_to_str(current_time))
            current_time = next_time
        
        return slots
    
    def _is_slot_available(self, date_str: str, start_time: str, slots_required: int) -> bool:
        """Check if a slot (and required subsequent slots) is available."""
        slot_duration = self.schedule.get("appointment_slot_duration", 30)
        
        for i in range(slots_required):
            check_time = self._add_minutes_to_time(start_time, i * slot_duration)
            
            # Check against existing appointments
            for appt in self.appointments:
                if appt["date"] == date_str and appt.get("status") != "cancelled":
                    appt_start = appt["start_time"]
                    appt_end = appt["end_time"]
                    
                    if appt_start <= check_time < appt_end:
                        return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return {
            "mode": self.mode.value,
            "calendly_configured": self.client.is_configured,
            "event_types_mapped": len(self._event_type_map),
            "local_appointments": len(self.appointments),
            "initialized": self._initialized,
        }


# Global instance
calendly_service = CalendlyService()

