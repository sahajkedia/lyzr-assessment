# 🔄 Appointment Reschedule & Cancel Guide

Complete end-to-end guide for the appointment management system including reschedule and cancel functionality.

---

## 🎯 Overview

The system now supports full appointment lifecycle management:
- ✅ **Book** appointments through conversational AI
- 🔍 **View** appointment details
- 📅 **Reschedule** to a new date/time
- ❌ **Cancel** appointments
- 💬 **Chat-based** and **UI-based** workflows

---

## 🌐 Backend API Endpoints

### Base URL: `/api/calendly`

### 1. **Get Appointment by Confirmation Code**
```bash
GET /api/calendly/appointment/confirmation/{confirmation_code}
```

**Example:**
```bash
curl http://localhost:8000/api/calendly/appointment/confirmation/1I6P5C
```

**Response:**
```json
{
  "success": true,
  "appointment": {
    "booking_id": "APPT-202511-0001",
    "appointment_type": "specialist",
    "date": "2025-11-26",
    "start_time": "10:00",
    "end_time": "11:00",
    "patient": { ... },
    "status": "confirmed",
    "confirmation_code": "1I6P5C"
  }
}
```

---

### 2. **Cancel Appointment**
```bash
DELETE /api/calendly/cancel/{booking_id}?reason=optional_reason
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/calendly/cancel/APPT-202511-0001?reason=Schedule+conflict"
```

**Response:**
```json
{
  "success": true,
  "message": "Appointment cancelled successfully",
  "booking_id": "APPT-202511-0001",
  "cancelled_at": "2025-11-26T10:30:00",
  "appointment": { ... }
}
```

**Effects:**
- Sets `status` to `"cancelled"`
- Adds `cancelled_at` timestamp
- Optionally stores `cancellation_reason`
- Frees up the time slot for new bookings

---

### 3. **Reschedule Appointment**
```bash
POST /api/calendly/reschedule/{booking_id}?new_date=YYYY-MM-DD&new_time=HH:MM
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/calendly/reschedule/APPT-202511-0001?new_date=2025-11-27&new_time=14:00"
```

**Response:**
```json
{
  "success": true,
  "message": "Appointment rescheduled successfully",
  "booking_id": "APPT-202511-0001",
  "old_date": "2025-11-26",
  "old_time": "10:00",
  "new_date": "2025-11-27",
  "new_time": "14:00",
  "appointment": { ... }
}
```

**Effects:**
- Updates `date`, `start_time`, and `end_time`
- Adds `rescheduled_at` timestamp
- Stores `previous_date` and `previous_time`
- Keeps the same `booking_id` and `confirmation_code`

---

### 4. **Check Availability**
```bash
POST /api/calendly/availability
Content-Type: application/json

{
  "date": "2025-11-27",
  "appointment_type": "consultation"
}
```

**Response:**
```json
{
  "date": "2025-11-27",
  "appointment_type": "consultation",
  "available_slots": [
    {
      "start_time": "09:00",
      "end_time": "09:30",
      "available": true
    },
    ...
  ],
  "total_available": 28
}
```

---

### 5. **Get Next Available Dates**
```bash
GET /api/calendly/availability/next-dates?appointment_type=consultation&days=7
```

**Response:**
```json
{
  "success": true,
  "appointment_type": "consultation",
  "available_dates": [
    {
      "date": "2025-11-27",
      "day_name": "Wednesday",
      "total_slots": 28,
      "sample_slots": [
        {"start_time": "09:00", "end_time": "09:30"},
        {"start_time": "09:15", "end_time": "09:45"},
        {"start_time": "09:30", "end_time": "10:00"}
      ]
    }
  ]
}
```

---

## 🤖 Agent / Chat Integration

### How Meera Handles Cancellations

**User:** "I want to cancel my appointment"

**Meera's Flow:**
1. Asks for confirmation code: *"Sure, I can help you with that. Could you please provide your confirmation code?"*
2. Retrieves appointment details using `get_appointment_by_confirmation` tool
3. Shows appointment details: *"I found your appointment: Specialist Consultation on November 26, 2025 at 10:00 AM..."*
4. Confirms cancellation: *"Would you like to proceed with cancelling this appointment?"*
5. Uses `cancel_appointment` tool after confirmation
6. Provides confirmation: *"Your appointment has been cancelled successfully..."*

---

### How Meera Handles Rescheduling

**User:** "I need to reschedule my appointment with confirmation code 1I6P5C"

**Meera's Flow:**
1. Retrieves current appointment using `get_appointment_by_confirmation` tool
2. Shows current appointment: *"Your current appointment is: Specialist Consultation on November 26, 2025 at 10:00 AM"*
3. Asks for preferences: *"When would you like to reschedule to?"*
4. Uses `check_availability` or `get_next_available_slots` to find options
5. Presents available slots: *"Here are some available times..."*
6. Confirms new selection: *"Great! I'll reschedule your appointment to November 27 at 2:00 PM. Is that correct?"*
7. Uses `reschedule_appointment` tool after confirmation
8. Provides updated details: *"Your appointment has been rescheduled successfully! Your confirmation code remains 1I6P5C"*

---

## 🎨 Frontend UI Components

### 1. **Appointment Manager Button**
- Located in the chat header (calendar icon)
- Opens a modal to manage appointments
- Always accessible during chat

### 2. **Appointment Manager Modal**
Components: `AppointmentManager.jsx`

**Features:**
- Search by confirmation code
- Displays full appointment details
- Shows appointment status (confirmed/cancelled)
- Provides action buttons

**Usage:**
1. Click calendar icon in chat header
2. Enter 6-character confirmation code
3. View appointment details
4. Choose to reschedule or cancel

### 3. **Appointment Card**
Component: `AppointmentCard.jsx`

**Displays:**
- Appointment type with icon
- Status badge (confirmed/cancelled)
- Date and time
- Patient information
- Reason for visit
- Booking ID and confirmation code
- Action buttons (if confirmed)

**Actions:**
- **Reschedule Button**: Closes modal and starts chat-based rescheduling
- **Cancel Button**: Shows confirmation dialog, then cancels appointment

---

## 🔄 User Workflows

### Workflow 1: Cancel via UI
1. Open chat interface
2. Click calendar icon in header
3. Enter confirmation code
4. View appointment details
5. Click "Cancel" button
6. Confirm cancellation
7. See updated status

### Workflow 2: Cancel via Chat
1. Say: "I want to cancel my appointment"
2. Provide confirmation code when asked
3. Confirm cancellation details
4. Receive confirmation message

### Workflow 3: Reschedule via UI
1. Open appointment manager
2. Enter confirmation code
3. Click "Reschedule" button
4. Continue conversation with Meera
5. Select new date/time
6. Confirm reschedule

### Workflow 4: Reschedule via Chat
1. Say: "I need to reschedule my appointment"
2. Provide confirmation code
3. View current appointment details
4. Select new date/time from available slots
5. Confirm reschedule
6. Receive updated confirmation

---

## 🧪 Testing Guide

### Test 1: View Appointment
```bash
# Via API
curl http://localhost:8000/api/calendly/appointment/confirmation/1I6P5C | python3 -m json.tool

# Via UI
1. Click calendar icon
2. Enter: 1I6P5C
3. Click "Find Appointment"
```

### Test 2: Cancel Appointment
```bash
# Via API
curl -X DELETE http://localhost:8000/api/calendly/cancel/APPT-202511-0001

# Via Chat
User: "I want to cancel my appointment with code 1I6P5C"
Meera will guide through cancellation

# Via UI
1. Open appointment manager
2. Search for appointment
3. Click "Cancel" button
4. Confirm cancellation
```

### Test 3: Reschedule Appointment
```bash
# Via API
curl -X POST "http://localhost:8000/api/calendly/reschedule/APPT-202511-0001?new_date=2025-11-27&new_time=14:00"

# Via Chat
User: "I need to reschedule my appointment with code 1I6P5C to tomorrow at 2 PM"
Meera will check availability and reschedule

# Via UI
1. Open appointment manager
2. Find appointment
3. Click "Reschedule"
4. Continue in chat to select new time
```

### Test 4: Check Availability Before Rescheduling
```bash
curl -X POST http://localhost:8000/api/calendly/availability \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-11-27","appointment_type":"specialist"}'
```

---

## 📋 Agent Tools Reference

### New Tools Added to Meera:

1. **`get_appointment_by_confirmation`**
   - Retrieves appointment by confirmation code
   - Used for: viewing, cancelling, rescheduling

2. **`cancel_appointment`**
   - Cancels an existing appointment
   - Requires: booking_id
   - Updates status to "cancelled"

3. **`reschedule_appointment`**
   - Moves appointment to new date/time
   - Requires: booking_id, new_date, new_start_time
   - Preserves booking_id and confirmation_code

---

## 🎯 Example Conversations

### Example 1: Simple Cancellation
```
User: Can I cancel my appointment?
Meera: Of course! I can help you cancel your appointment. Could you please 
       provide your confirmation code?
User: 1I6P5C
Meera: I found your appointment:
       - Specialist Consultation
       - November 26, 2025 at 10:00 AM
       - Patient: Sahaj
       
       Would you like to proceed with cancelling this appointment?
User: Yes
Meera: Your appointment has been cancelled successfully. If you need to 
       schedule a new appointment in the future, I'm here to help!
```

### Example 2: Reschedule with Availability Check
```
User: I need to reschedule my appointment with code 1I6P5C
Meera: I found your current appointment:
       - Specialist Consultation
       - November 26, 2025 at 10:00 AM
       
       When would you like to reschedule to?
User: Tomorrow afternoon
Meera: Let me check what's available tomorrow afternoon... I have these slots:
       - 1:00 PM - 2:00 PM
       - 2:00 PM - 3:00 PM
       - 3:00 PM - 4:00 PM
       
       Which time works best for you?
User: 2:00 PM
Meera: Perfect! I'll reschedule your Specialist Consultation to November 27, 
       2025 at 2:00 PM. Is that correct?
User: Yes
Meera: Your appointment has been rescheduled successfully!
       
       Updated Details:
       - Type: Specialist Consultation
       - Date: November 27, 2025
       - Time: 2:00 PM - 3:00 PM
       - Confirmation Code: 1I6P5C (same as before)
```

---

## 🔐 Security & Validation

### Backend Validations:
- ✅ Confirmation code exists
- ✅ Booking ID exists
- ✅ Cannot cancel already cancelled appointments
- ✅ Cannot reschedule cancelled appointments
- ✅ New time slot is available
- ✅ Date is not in the past
- ✅ Appointment type is valid

### Frontend Validations:
- ✅ Confirmation code is 6 characters
- ✅ Uppercase formatting
- ✅ Prevents double-clicks during API calls
- ✅ Shows loading states
- ✅ Displays error messages

---

## 📊 API Documentation

Visit the interactive API documentation:
```
http://localhost:8000/docs
```

Look for the **"calendly"** section with all endpoints!

---

## 🚀 Quick Start Testing

```bash
# 1. Start the servers (if not running)
./start.sh

# 2. View existing appointment
curl http://localhost:8000/api/calendly/appointment/confirmation/1I6P5C | python3 -m json.tool

# 3. Check availability for rescheduling
curl -X POST http://localhost:8000/api/calendly/availability \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-11-27","appointment_type":"specialist"}' | python3 -m json.tool

# 4. Test in frontend
# Open http://localhost:3000
# Click calendar icon
# Enter: 1I6P5C
# Try reschedule or cancel
```

---

## 💡 Tips

1. **Confirmation codes** are 6-character alphanumeric codes (e.g., 1I6P5C)
2. **Booking IDs** follow the format `APPT-YYYYMM-NNNN`
3. **Times** are in 24-hour format in the API (HH:MM)
4. **Meera** can handle both booking IDs and confirmation codes
5. **Chat flow** is recommended for rescheduling (more natural)
6. **UI flow** is quick for cancellations

---

## 🎉 Success!

You now have a complete appointment management system with:
- ✅ Conversational booking
- ✅ UI-based management
- ✅ Flexible rescheduling
- ✅ Easy cancellation
- ✅ Full API access
- ✅ End-to-end integration

All managed by Meera, your friendly AI assistant! 💜


