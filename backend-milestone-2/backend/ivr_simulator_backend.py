# ivr_backend_zunera.py
# IRCTC IVR Simulation Backend - Shaik Zunera

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import random

app = FastAPI(title="IRCTC IVR Simulator - Zunera", version="1.0")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATA MODELS ----------------

class StartCallRequest(BaseModel):
    caller_number: str
    call_id: Optional[str] = None


class KeypadInput(BaseModel):
    call_id: str
    digit: str
    current_menu: str


class CallArchive(BaseModel):
    call_id: str
    caller_number: str
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[int] = None
    menu_path: List[str] = []
    inputs: List[str] = []


# ---------------- MEMORY STORAGE ----------------

live_sessions = {}
call_logs = []


# ---------------- IVR MENU (IRCTC SERVICES) ----------------

IVR_MENU = {

    "main": {
        "prompt": """Welcome to IRCTC Railway Helpline.

Press 1 Ticket Booking
Press 2 PNR Status
Press 3 Train Running Status
Press 4 Ticket Cancellation
Press 5 Seat Availability
Press 6 Refund Status
Press 7 Travel Guidelines
Press 8 Feedback
Press 9 Talk to Customer Care""",

        "options": {
            "1": {"action": "goto", "target": "booking"},
            "2": {"action": "goto", "target": "pnr_status"},
            "3": {"action": "goto", "target": "train_status"},
            "4": {"action": "goto", "target": "cancel"},
            "5": {"action": "goto", "target": "seat"},
            "6": {"action": "goto", "target": "refund"},
            "7": {"action": "goto", "target": "guidelines"},
            "8": {"action": "goto", "target": "feedback"},
            "9": {"action": "transfer"}
        }
    },

    "booking": {
        "prompt": "Ticket Booking Menu: 1 New Ticket, 2 Modify Ticket, 3 Tatkal Booking, 0 Main Menu",
        "options": {
            "1": {"action": "end", "msg": "Please visit IRCTC website for new ticket booking."},
            "2": {"action": "end", "msg": "Ticket modification request submitted."},
            "3": {"action": "end", "msg": "Tatkal booking opens one day before travel."},
            "0": {"action": "goto", "target": "main"}
        }
    },

    "pnr_status": {
        "prompt": "Enter your 10 digit PNR number followed by #",
        "options": {
            "#": {"action": "lookup_pnr"}
        }
    },

    "train_status": {
        "prompt": "Train Running Status: 1 Live Status, 2 Train Schedule, 0 Back",
        "options": {
            "1": {"action": "end", "msg": "Live train status available on NTES website."},
            "2": {"action": "end", "msg": "Train schedule information sent to your phone."},
            "0": {"action": "goto", "target": "main"}
        }
    },

    "cancel": {
        "prompt": "Ticket Cancellation: 1 Cancel Ticket, 2 Cancellation Rules, 0 Back",
        "options": {
            "1": {"action": "end", "msg": "Ticket cancellation request received."},
            "2": {"action": "end", "msg": "Cancellation rules sent via SMS."},
            "0": {"action": "goto", "target": "main"}
        }
    },

    "seat": {
        "prompt": "Seat Availability: 1 Sleeper Class, 2 AC Class, 3 Tatkal Seats, 0 Back",
        "options": {
            "1": {"action": "end", "msg": "Sleeper seat availability can be checked online."},
            "2": {"action": "end", "msg": "AC class seat availability details sent."},
            "3": {"action": "end", "msg": "Tatkal seats open one day before travel."},
            "0": {"action": "goto", "target": "main"}
        }
    },

    "refund": {
        "prompt": "Refund Services: 1 Check Refund Status, 2 Refund Policy, 0 Back",
        "options": {
            "1": {"action": "end", "msg": "Refund status will be sent to your mobile."},
            "2": {"action": "end", "msg": "Refund policy shared via SMS."},
            "0": {"action": "goto", "target": "main"}
        }
    },

    "guidelines": {
        "prompt": "Travel Guidelines: 1 ID Proof Rules, 2 Luggage Rules, 0 Back",
        "options": {
            "1": {"action": "end", "msg": "Valid ID proof is mandatory during travel."},
            "2": {"action": "end", "msg": "Luggage limits depend on travel class."},
            "0": {"action": "goto", "target": "main"}
        }
    },

    "feedback": {
        "prompt": "Rate our service: 1 Average, 2 Excellent, 0 Back",
        "options": {
            "1": {"action": "end", "msg": "Thank you for your feedback."},
            "2": {"action": "end", "msg": "Thank you! We appreciate your support."},
            "0": {"action": "goto", "target": "main"}
        }
    }
}


# ---------------- CREATE SESSION ----------------

def create_session(caller_number: str):

    call_id = f"CALL_{random.randint(100000,999999)}"

    live_sessions[call_id] = {
        "call_id": call_id,
        "caller_number": caller_number,
        "start_time": datetime.now().isoformat(),
        "current_menu": "main",
        "menu_path": ["main"],
        "inputs": [],
        "pnr_buffer": ""
    }

    return call_id


# ---------------- API ROUTES ----------------

@app.get("/")
def server_status():
    return {
        "status": "IRCTC IVR Backend Running",
        "active_calls": len(live_sessions),
        "total_calls": len(call_logs)
    }


# Start Call
@app.post("/ivr/start")
def start_call(data: StartCallRequest):

    call_id = create_session(data.caller_number)

    return {
        "call_id": call_id,
        "status": "connected",
        "prompt": IVR_MENU["main"]["prompt"]
    }


# Process Keypad Input
@app.post("/ivr/dtmf")
def process_dtmf(data: KeypadInput):

    if data.call_id not in live_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = live_sessions[data.call_id]
    menu_name = session["current_menu"]

    # Handle PNR digit input
    if menu_name == "pnr_status" and data.digit.isdigit():
        session["pnr_buffer"] += data.digit

        if len(session["pnr_buffer"]) < 10:
            return {
                "status": "collecting_pnr",
                "message": f"Entered digits: {session['pnr_buffer']}"
            }

    menu = IVR_MENU.get(menu_name)
    options = menu.get("options", {})

    if data.digit not in options:
        return {"status": "invalid", "prompt": "Invalid option"}

    option = options[data.digit]
    action = option["action"]

    # Go to another menu
    if action == "goto":

        target = option["target"]

        session["current_menu"] = target
        session["menu_path"].append(target)

        return {
            "status": "processed",
            "prompt": IVR_MENU[target]["prompt"],
            "current_menu": target
        }

    # End Call
    if action == "end":

        session["end_time"] = datetime.now().isoformat()
        call_logs.append(session.copy())
        del live_sessions[data.call_id]

        return {"status": "call_ended", "message": option["msg"]}

    # Transfer to agent
    if action == "transfer":

        session["end_time"] = datetime.now().isoformat()
        call_logs.append(session.copy())
        del live_sessions[data.call_id]

        return {"status": "transferred", "message": "Connecting to customer care agent"}

    # PNR Lookup
    if action == "lookup_pnr":

        pnr = session["pnr_buffer"]

        if len(pnr) == 10:

            session["end_time"] = datetime.now().isoformat()
            call_logs.append(session.copy())
            del live_sessions[data.call_id]

            return {
                "status": "pnr_found",
                "message": f"PNR {pnr} confirmed. Train 12760 Charminar Express Hyderabad → Chennai."
            }

        return {"status": "invalid_pnr", "message": "Invalid PNR number"}

# End Call
@app.post("/ivr/end")
def end_call(call_id: str = Query(...)):

    if call_id in live_sessions:

        session = live_sessions[call_id]
        session["end_time"] = datetime.now().isoformat()

        call_logs.append(session.copy())
        del live_sessions[call_id]

        return {"status": "ended"}

    return {"status": "not_found"}
