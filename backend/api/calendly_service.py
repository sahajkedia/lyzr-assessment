"""
Mock Calendly Service.
Pure mock implementation for appointment scheduling without real Calendly API.
"""
import json
import logging
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Any, Optional
import random
import string
from pathlib import Path

from backend.models.schemas import (
    TimeSlot, AvailabilityRequest, AvailabilityResponse,
    BookingRequest, BookingResponse, AppointmentDetails
)

logger = logging.getLogger(__name__)


class CalendlyService:
    """
    Mock Calendly service for appointment scheduling.
    
    Uses local JSON files for schedule and appointments.
    No external API dependencies.
    """
    
    def __init__(self):
        self.mode = "mock"
        self._initialized = False
        
        # Local storage
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.schedule_file = self.data_dir / "doctor_schedule.json"
        self.appointments_file = self.data_dir / "appointments.json"
        
        # Load schedule and appointments
        self.schedule = self._load_schedule()
        self.appointments = self._load_appointments()
    
    def _load_schedule(self) -> Dict[str, Any]:
        """Load doctor schedule from file."""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                return json.load(f)
        
        # Default schedule if file doesn't exist
        return {
            "working_hours": {
                "monday": {"start": "09:00", "end": "17:00", "lunch": {"start": "12:00", "end": "13:00"}},
                "tuesday": {"start": "09:00", "end": "17:00", "lunch": {"start": "12:00", "end": "13:00"}},
                "wednesday": {"start": "09:00", "end": "17:00", "lunch": {"start": "12:00", "end": "13:00"}},
                "thursday": {"start": "09:00", "end": "17:00", "lunch": {"start": "12:00", "end": "13:00"}},
                "friday": {"start": "09:00", "end": "17:00", "lunch": {"start": "12:00", "end": "13:00"}},
                "saturday": "closed",
                "sunday": "closed"
            },
            "appointment_types": {
                "consultation": {
                    "name": "General Consultation",
                    "duration": 30,
                    "slots_required": 1,
                    "description": "General medical consultation"
                },
                "followup": {
                    "name": "Follow-up",
                    "duration": 15,
                    "slots_required": 1,
                    "description": "Follow-up appointment"
                },
                "physical": {
                    "name": "Physical Exam",
                    "duration": 45,
                    "slots_required": 2,
                    "description": "Complete physical examination"
                },
                "specialist": {
                    "name": "Specialist Consultation",
                    "duration": 60,
                    "slots_required": 2,
                    "description": "Specialist consultation"
                }
            },
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
    
    async def initialize(self) -> str:
        """
        Initialize the service.
        
        Returns:
            The mode the service is operating in (always "mock")
        """
        if not self._initialized:
            logger.info("📋 Initializing Mock Calendly Service")
            logger.info(f"   Schedule file: {self.schedule_file}")
            logger.info(f"   Appointments file: {self.appointments_file}")
            logger.info(f"   Current appointments: {len(self.appointments)}")
            self._initialized = True
        
        return self.mode
    
    # ==================== Availability ====================
    
    async def get_availability(self, request: AvailabilityRequest) -> AvailabilityResponse:
        """Get available time slots for a specific date and appointment type."""
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
        
        logger.info(f"📋 Appointment booked (mock): {booking_id}")
        
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
        """Cancel an appointment (marks as cancelled but keeps in database)."""
        for i, appt in enumerate(self.appointments):
            if appt["booking_id"] == booking_id:
                # Update local record
                self.appointments[i]["status"] = "cancelled"
                self.appointments[i]["cancelled_at"] = datetime.now().isoformat()
                if reason:
                    self.appointments[i]["cancellation_reason"] = reason
                
                self._save_appointments()
                logger.info(f"📋 Appointment cancelled (mock): {booking_id}")
                return True
        
        return False
    
    async def delete_appointment(self, booking_id: str) -> bool:
        """Permanently delete an appointment from the database."""
        for i, appt in enumerate(self.appointments):
            if appt["booking_id"] == booking_id:
                # Permanently remove from list
                self.appointments.pop(i)
                self._save_appointments()
                logger.info(f"🗑️ Appointment permanently deleted (mock): {booking_id}")
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
        
        days_checked = 0
        days_with_availability = 0
        
        while days_with_availability < num_days and days_checked < 60:  # Check up to 60 days
            check_date = current_date + timedelta(days=days_checked)
            date_str = check_date.strftime("%Y-%m-%d")
            
            # Skip weekends if not in schedule
            day_name = check_date.strftime("%A").lower()
            if self.schedule["working_hours"].get(day_name) == "closed":
                days_checked += 1
                continue
            
            # Get availability
            request = AvailabilityRequest(date=date_str, appointment_type=appointment_type)
            availability = await self.get_availability(request)
            
            if availability.total_available > 0:
                slots = [
                    {"start_time": slot.start_time, "end_time": slot.end_time}
                    for slot in availability.available_slots[:3]  # First 3 slots
                ]
                available_dates.append({
                    "date": date_str,
                    "day_name": check_date.strftime("%A"),
                    "total_slots": availability.total_available,
                    "sample_slots": slots,
                })
                days_with_availability += 1
            
            days_checked += 1
        
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
            "mode": self.mode,
            "initialized": self._initialized,
            "total_appointments": len(self.appointments),
            "active_appointments": len([a for a in self.appointments if a.get("status") == "confirmed"]),
            "appointment_types": len(self.schedule.get("appointment_types", {})),
        }


# Global instance
calendly_service = CalendlyService()
