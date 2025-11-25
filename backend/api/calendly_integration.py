"""
Calendly API integration (Mock Implementation).
Provides endpoints for checking availability and booking appointments.
"""
import json
import os
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Any, Optional
import random
import string
from pathlib import Path

from backend.models.schemas import (
    TimeSlot, AvailabilityRequest, AvailabilityResponse,
    BookingRequest, BookingResponse, AppointmentDetails
)


class MockCalendlyAPI:
    """Mock implementation of Calendly API."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.schedule_file = self.data_dir / "doctor_schedule.json"
        self.appointments_file = self.data_dir / "appointments.json"
        
        # Load doctor schedule
        with open(self.schedule_file, 'r') as f:
            self.schedule = json.load(f)
        
        # Load or initialize appointments
        self.appointments = self._load_appointments()
    
    def _load_appointments(self) -> List[Dict[str, Any]]:
        """Load existing appointments from file."""
        if self.appointments_file.exists():
            with open(self.appointments_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_appointments(self):
        """Save appointments to file."""
        with open(self.appointments_file, 'w') as f:
            json.dump(self.appointments, f, indent=2, default=str)
    
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
    
    def _is_blocked_date(self, date_str: str) -> bool:
        """Check if date is blocked."""
        return date_str in self.schedule.get("blocked_dates", [])
    
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
        slot_duration = self.schedule["appointment_slot_duration"]
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
        slot_duration = self.schedule["appointment_slot_duration"]
        
        for i in range(slots_required):
            check_time = self._add_minutes_to_time(start_time, i * slot_duration)
            
            # Check against existing appointments
            for appt in self.appointments:
                if appt["date"] == date_str:
                    appt_start = appt["start_time"]
                    appt_end = appt["end_time"]
                    
                    if appt_start <= check_time < appt_end:
                        return False
        
        return True
    
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
        if self._is_blocked_date(date_str):
            return AvailabilityResponse(
                date=date_str,
                appointment_type=appt_type,
                available_slots=[],
                total_available=0
            )
        
        # Get working hours for the day
        working_hours = self._get_working_hours(date_str)
        if not working_hours:
            return AvailabilityResponse(
                date=date_str,
                appointment_type=appt_type,
                available_slots=[],
                total_available=0
            )
        
        # Get appointment type details
        appt_details = self.schedule["appointment_types"][appt_type]
        duration = appt_details["duration"]
        slots_required = appt_details["slots_required"]
        
        # Generate all time slots
        all_slots = self._generate_time_slots(date_str, working_hours)
        
        # Check availability for each slot
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
                "phone": request.patient.phone
            },
            "reason": request.reason,
            "confirmation_code": confirmation_code,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Save appointment
        self.appointments.append(appointment)
        self._save_appointments()
        
        # Return booking response
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            confirmation_code=confirmation_code,
            details=appointment
        )
    
    async def get_appointment(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by booking ID."""
        for appt in self.appointments:
            if appt["booking_id"] == booking_id:
                return appt
        return None
    
    async def cancel_appointment(self, booking_id: str) -> bool:
        """Cancel an appointment."""
        for i, appt in enumerate(self.appointments):
            if appt["booking_id"] == booking_id:
                self.appointments[i]["status"] = "cancelled"
                self._save_appointments()
                return True
        return False
    
    async def get_next_available_dates(self, appointment_type: str, num_days: int = 7) -> List[Dict[str, Any]]:
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
                # Get first 3 slots
                slots = [
                    {"start_time": slot.start_time, "end_time": slot.end_time}
                    for slot in availability.available_slots[:3]
                ]
                available_dates.append({
                    "date": date_str,
                    "day_name": check_date.strftime("%A"),
                    "total_slots": availability.total_available,
                    "sample_slots": slots
                })
        
        return available_dates


# Global instance
calendly_api = MockCalendlyAPI()

