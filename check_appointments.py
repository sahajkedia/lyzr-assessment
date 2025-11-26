#!/usr/bin/env python3
"""
Helper script to check appointments.
Usage: python check_appointments.py [--date YYYY-MM-DD] [--email EMAIL] [--phone PHONE]
"""
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def load_appointments() -> List[Dict[str, Any]]:
    """Load appointments from JSON file."""
    appointments_file = Path(__file__).parent / "data" / "appointments.json"
    
    if not appointments_file.exists():
        return []
    
    with open(appointments_file, 'r') as f:
        return json.load(f)


def format_appointment(appt: Dict[str, Any]) -> str:
    """Format appointment for display."""
    status_emoji = "✅" if appt["status"] == "confirmed" else "❌"
    
    return f"""
{status_emoji} {appt['booking_id']} - {appt['status'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {appt['date']}
⏰ Time: {appt['start_time']} - {appt['end_time']}
🏥 Type: {appt['appointment_type'].title()}
👤 Patient: {appt['patient']['name']}
📧 Email: {appt['patient']['email']}
📱 Phone: {appt['patient']['phone']}
📝 Reason: {appt['reason']}
🎫 Confirmation Code: {appt['confirmation_code']}
📆 Booked At: {appt['created_at']}
"""


def filter_appointments(
    appointments: List[Dict[str, Any]],
    date: str = None,
    email: str = None,
    phone: str = None,
    status: str = None
) -> List[Dict[str, Any]]:
    """Filter appointments based on criteria."""
    filtered = appointments
    
    if date:
        filtered = [a for a in filtered if a["date"] == date]
    
    if email:
        filtered = [a for a in filtered if a["patient"]["email"].lower() == email.lower()]
    
    if phone:
        filtered = [a for a in filtered if a["patient"]["phone"] == phone]
    
    if status:
        filtered = [a for a in filtered if a["status"] == status]
    
    return filtered


def get_summary(appointments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get summary statistics."""
    total = len(appointments)
    confirmed = sum(1 for a in appointments if a["status"] == "confirmed")
    cancelled = sum(1 for a in appointments if a["status"] == "cancelled")
    
    today = datetime.now().date()
    upcoming = sum(
        1 for a in appointments 
        if datetime.strptime(a["date"], "%Y-%m-%d").date() >= today 
        and a["status"] == "confirmed"
    )
    
    by_type = {}
    for appt in appointments:
        appt_type = appt["appointment_type"]
        by_type[appt_type] = by_type.get(appt_type, 0) + 1
    
    return {
        "total": total,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "upcoming": upcoming,
        "by_type": by_type
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check booked appointments",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--date", help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--email", help="Filter by patient email")
    parser.add_argument("--phone", help="Filter by patient phone")
    parser.add_argument("--status", choices=["confirmed", "cancelled"], help="Filter by status")
    parser.add_argument("--summary", action="store_true", help="Show summary statistics only")
    parser.add_argument("--booking-id", help="Get specific appointment by booking ID")
    parser.add_argument("--confirmation", help="Get appointment by confirmation code")
    
    args = parser.parse_args()
    
    # Load appointments
    appointments = load_appointments()
    
    if not appointments:
        print("❌ No appointments found in the database.")
        return
    
    # Handle specific booking ID lookup
    if args.booking_id:
        appt = next((a for a in appointments if a["booking_id"] == args.booking_id), None)
        if appt:
            print(format_appointment(appt))
        else:
            print(f"❌ Appointment with booking ID '{args.booking_id}' not found.")
        return
    
    # Handle confirmation code lookup
    if args.confirmation:
        appt = next((a for a in appointments if a["confirmation_code"] == args.confirmation.upper()), None)
        if appt:
            print(format_appointment(appt))
        else:
            print(f"❌ Appointment with confirmation code '{args.confirmation}' not found.")
        return
    
    # Show summary if requested
    if args.summary:
        summary = get_summary(appointments)
        print("\n📊 APPOINTMENTS SUMMARY")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📋 Total Appointments: {summary['total']}")
        print(f"✅ Confirmed: {summary['confirmed']}")
        print(f"❌ Cancelled: {summary['cancelled']}")
        print(f"📅 Upcoming (Confirmed): {summary['upcoming']}")
        print("\n📊 By Type:")
        for appt_type, count in summary['by_type'].items():
            print(f"   • {appt_type.title()}: {count}")
        print()
        return
    
    # Filter appointments
    filtered = filter_appointments(
        appointments,
        date=args.date,
        email=args.email,
        phone=args.phone,
        status=args.status
    )
    
    if not filtered:
        print("❌ No appointments found matching the criteria.")
        return
    
    # Display results
    print(f"\n📋 Found {len(filtered)} appointment(s)")
    print("=" * 45)
    
    for appt in filtered:
        print(format_appointment(appt))


if __name__ == "__main__":
    main()

