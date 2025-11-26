# 📋 Appointments Management Guide

This guide shows you all the ways to check and manage booked appointments in your Medical Appointment Scheduling system.

## 🎯 Quick Overview

Appointments are stored in: `/data/appointments.json`

Each appointment has:
- **booking_id**: Unique identifier (e.g., `APPT-202511-0001`)
- **confirmation_code**: 6-character code (e.g., `1I6P5C`)
- **patient**: Name, email, phone
- **date & time**: Appointment schedule
- **status**: `confirmed` or `cancelled`
- **appointment_type**: consultation, followup, physical, specialist

---

## 🔍 Method 1: Python Script (Easiest)

### Check All Appointments
```bash
python3 check_appointments.py
```

### Get Summary Statistics
```bash
python3 check_appointments.py --summary
```

### Filter by Date
```bash
python3 check_appointments.py --date 2025-11-26
```

### Filter by Patient Email
```bash
python3 check_appointments.py --email sahajkedia333@gmail.com
```

### Filter by Patient Phone
```bash
python3 check_appointments.py --phone 93046333363
```

### Find by Booking ID
```bash
python3 check_appointments.py --booking-id APPT-202511-0001
```

### Find by Confirmation Code
```bash
python3 check_appointments.py --confirmation 1I6P5C
```

### Filter by Status
```bash
python3 check_appointments.py --status confirmed
python3 check_appointments.py --status cancelled
```

---

## 🌐 Method 2: REST API (Best for Integration)

The backend server now has full appointments API endpoints!

### Base URL
```
http://localhost:8000/api/appointments
```

### 1. **List All Appointments**
```bash
curl http://localhost:8000/api/appointments
```

**Response:**
```json
{
  "success": true,
  "count": 1,
  "appointments": [...]
}
```

### 2. **Filter Appointments**

**By Date:**
```bash
curl "http://localhost:8000/api/appointments?date=2025-11-26"
```

**By Patient Email:**
```bash
curl "http://localhost:8000/api/appointments?patient_email=sahajkedia333@gmail.com"
```

**By Patient Phone:**
```bash
curl "http://localhost:8000/api/appointments?patient_phone=93046333363"
```

**By Status:**
```bash
curl "http://localhost:8000/api/appointments?status=confirmed"
```

**Combine Multiple Filters:**
```bash
curl "http://localhost:8000/api/appointments?date=2025-11-26&status=confirmed"
```

### 3. **Get Specific Appointment by Booking ID**
```bash
curl http://localhost:8000/api/appointments/APPT-202511-0001
```

### 4. **Get Appointment by Confirmation Code**
```bash
curl http://localhost:8000/api/appointments/confirmation/1I6P5C
```

### 5. **Get Summary Statistics**
```bash
curl http://localhost:8000/api/appointments/stats/summary
```

**Response:**
```json
{
  "success": true,
  "total_appointments": 1,
  "by_status": {
    "confirmed": 1
  },
  "by_type": {
    "specialist": 1
  },
  "upcoming_confirmed": 1,
  "past_appointments": 0
}
```

### 6. **Cancel an Appointment**
```bash
curl -X DELETE http://localhost:8000/api/appointments/APPT-202511-0001
```

---

## 📁 Method 3: Direct File Access

### View Raw JSON
```bash
cat data/appointments.json
```

### Pretty Print
```bash
cat data/appointments.json | python3 -m json.tool
```

### Count Appointments
```bash
cat data/appointments.json | python3 -c "import json, sys; print(f'Total: {len(json.load(sys.stdin))}')"
```

### Search by Pattern
```bash
grep -i "sahaj" data/appointments.json
```

---

## 🔧 Method 4: Python Code

```python
import json
from pathlib import Path

# Load appointments
appointments_file = Path("data/appointments.json")
with open(appointments_file, 'r') as f:
    appointments = json.load(f)

# Check if appointment exists by booking_id
def is_appointment_booked(booking_id: str) -> bool:
    return any(a["booking_id"] == booking_id for a in appointments)

# Get appointment by email
def get_appointments_by_email(email: str):
    return [a for a in appointments if a["patient"]["email"] == email]

# Get upcoming appointments
from datetime import datetime
def get_upcoming_appointments():
    today = datetime.now().date()
    return [
        a for a in appointments 
        if datetime.strptime(a["date"], "%Y-%m-%d").date() >= today
        and a["status"] == "confirmed"
    ]

# Usage
print(f"Booking exists: {is_appointment_booked('APPT-202511-0001')}")
print(f"Sahaj's appointments: {get_appointments_by_email('sahajkedia333@gmail.com')}")
print(f"Upcoming: {len(get_upcoming_appointments())}")
```

---

## 📊 Interactive API Documentation

Visit the Swagger UI to test all endpoints interactively:

```
http://localhost:8000/docs
```

Look for the **"appointments"** section with all the new endpoints!

---

## 🎯 Common Use Cases

### 1. **Check if today has any appointments**
```bash
python3 check_appointments.py --date $(date +%Y-%m-%d)
```

### 2. **Find all appointments for a patient**
```bash
python3 check_appointments.py --email patient@example.com
```

### 3. **Get appointment count**
```bash
python3 check_appointments.py --summary
```

### 4. **Verify booking after confirmation**
```bash
# By confirmation code
python3 check_appointments.py --confirmation ABC123

# By booking ID
python3 check_appointments.py --booking-id APPT-202511-0001
```

### 5. **Check for conflicts before booking** (In your code)
```python
from backend.api.calendly_integration import calendly_api

# Check if slot is available
availability = await calendly_api.get_availability(
    AvailabilityRequest(date="2025-11-26", appointment_type="specialist")
)

# Get all existing appointments for a date
existing = [a for a in calendly_api.appointments if a["date"] == "2025-11-26"]
```

---

## 🚨 Troubleshooting

### No appointments showing?
1. Check if file exists: `ls -la data/appointments.json`
2. Check file contents: `cat data/appointments.json`
3. Verify it's valid JSON: `python3 -m json.tool data/appointments.json`

### API returning 404?
1. Make sure backend is running: `curl http://localhost:8000/health`
2. Check if endpoints are registered: `curl http://localhost:8000/`
3. Restart the backend server

### Script not working?
1. Make sure you're in the project directory
2. Use `python3` instead of `python`
3. Check if file has correct permissions: `chmod +x check_appointments.py`

---

## 📝 Notes

- Appointments are automatically saved after each booking
- The system generates unique booking IDs and confirmation codes
- Past appointments remain in the database (status: confirmed/cancelled)
- The backend server must be running for API endpoints
- The script works directly with the JSON file (no server needed)

---

## 🔐 Security Considerations

For production:
- Add authentication to API endpoints
- Encrypt sensitive patient data
- Use a proper database (PostgreSQL, MongoDB)
- Add rate limiting
- Implement audit logging
- Add input validation and sanitization

---

## 🎉 Quick Test

Try this now:
```bash
# Get summary
python3 check_appointments.py --summary

# View all appointments
python3 check_appointments.py

# Test API (if server is running)
curl http://localhost:8000/api/appointments
```


