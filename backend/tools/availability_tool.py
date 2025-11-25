"""
Tool for checking appointment availability.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from backend.api.calendly_integration import calendly_api
from backend.models.schemas import AvailabilityRequest


async def check_availability(date: str, appointment_type: str) -> Dict[str, Any]:
    """
    Check availability for a specific date and appointment type.
    
    Args:
        date: Date in YYYY-MM-DD format
        appointment_type: Type (consultation, followup, physical, specialist)
        
    Returns:
        Dictionary with availability information
    """
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        
        # Create request
        request = AvailabilityRequest(
            date=date,
            appointment_type=appointment_type
        )
        
        # Get availability
        availability = await calendly_api.get_availability(request)
        
        # Format response
        return {
            "success": True,
            "date": availability.date,
            "appointment_type": availability.appointment_type,
            "total_available": availability.total_available,
            "available_slots": [
                {
                    "start_time": slot.start_time,
                    "end_time": slot.end_time
                }
                for slot in availability.available_slots
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_next_available_slots(
    appointment_type: str,
    num_days: int = 7,
    max_slots_per_day: int = 3
) -> Dict[str, Any]:
    """
    Get next available slots across multiple days.
    
    Args:
        appointment_type: Type of appointment
        num_days: Number of days to check
        max_slots_per_day: Maximum slots to return per day
        
    Returns:
        Dictionary with available dates and slots
    """
    try:
        available_dates = await calendly_api.get_next_available_dates(
            appointment_type=appointment_type,
            num_days=num_days
        )
        
        # Format response
        formatted_dates = []
        for date_info in available_dates[:5]:  # Return max 5 days
            formatted_dates.append({
                "date": date_info["date"],
                "day_name": date_info["day_name"],
                "total_slots": date_info["total_slots"],
                "sample_slots": date_info["sample_slots"][:max_slots_per_day]
            })
        
        return {
            "success": True,
            "appointment_type": appointment_type,
            "available_dates": formatted_dates
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_availability_for_date_range(
    start_date: str,
    end_date: str,
    appointment_type: str
) -> Dict[str, Any]:
    """
    Get availability for a date range.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        appointment_type: Type of appointment
        
    Returns:
        Dictionary with availability for each date
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        if end < start:
            raise ValueError("End date must be after start date")
        
        if (end - start).days > 14:
            raise ValueError("Date range cannot exceed 14 days")
        
        availability_by_date = []
        current = start
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            request = AvailabilityRequest(
                date=date_str,
                appointment_type=appointment_type
            )
            
            availability = await calendly_api.get_availability(request)
            
            if availability.total_available > 0:
                availability_by_date.append({
                    "date": date_str,
                    "day_name": current.strftime("%A"),
                    "total_slots": availability.total_available,
                    "sample_slots": [
                        {"start_time": slot.start_time, "end_time": slot.end_time}
                        for slot in availability.available_slots[:3]
                    ]
                })
            
            current += timedelta(days=1)
        
        return {
            "success": True,
            "start_date": start_date,
            "end_date": end_date,
            "appointment_type": appointment_type,
            "available_dates": availability_by_date
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Tool definitions for LLM
AVAILABILITY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available appointment slots for a specific date and appointment type. Use this when the user specifies a particular date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date to check in YYYY-MM-DD format"
                    },
                    "appointment_type": {
                        "type": "string",
                        "enum": ["consultation", "followup", "physical", "specialist"],
                        "description": "Type of appointment: consultation (30 min), followup (15 min), physical (45 min), or specialist (60 min)"
                    }
                },
                "required": ["date", "appointment_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_available_slots",
            "description": "Get the next available appointment slots across multiple days. Use this when the user doesn't specify a date or wants to see upcoming availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_type": {
                        "type": "string",
                        "enum": ["consultation", "followup", "physical", "specialist"],
                        "description": "Type of appointment"
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "Number of days to check (default 7)",
                        "default": 7
                    }
                },
                "required": ["appointment_type"]
            }
        }
    }
]

