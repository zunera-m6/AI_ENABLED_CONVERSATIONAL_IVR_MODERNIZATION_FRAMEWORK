# irctc_ivr_backend_with_twilio.py
from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

app = FastAPI(title="IRCTC IVR Backend + Twilio", version="1.0")

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CONFIG ----------------

NGROK_HOST = ""


# ---------------- MODELS ----------------

class CallStart(BaseModel):
    caller_number: str
    call_id: Optional[str] = None


class DTMFInput(BaseModel):
    call_id: str
    digit: str
    current_menu: str


# ---------------- MEMORY ----------------

active_calls = {}
call_history = []

# ---------------- IRCTC MENU ----------------

MENU = {

"main":{
"prompt":"Welcome to IRCTC Railway Services. Press 1 Ticket Booking. Press 2 PNR Status. Press 3 Train Running Status. Press 4 Ticket Cancellation. Press 5 Refund Status. Press 6 Seat Availability. Press 7 Travel Advisory. Press 8 Feedback. Press 9 Talk to Customer Support.",
"options":{
"1":{"action":"goto","target":"booking","msg":"Ticket booking selected."},
"2":{"action":"goto","target":"pnr_status","msg":"PNR status selected."},
"3":{"action":"goto","target":"train_status","msg":"Train running status selected."},
"4":{"action":"goto","target":"cancel_ticket","msg":"Ticket cancellation selected."},
"5":{"action":"goto","target":"refunds","msg":"Refund options selected."},
"6":{"action":"goto","target":"seat","msg":"Seat availability options."},
"7":{"action":"goto","target":"advisory","msg":"Travel advisory options."},
"8":{"action":"goto","target":"feedback","msg":"Feedback options."},
"9":{"action":"transfer","msg":"Connecting to IRCTC customer support."}
}
},

"booking":{
"prompt":"Press 1 Sleeper Class Booking. Press 2 AC Class Booking. Press 3 Tatkal Booking. Press 0 Back to main menu.",
"options":{
"1":{"action":"end","msg":"Sleeper class booking request received."},
"2":{"action":"end","msg":"AC class booking request received."},
"3":{"action":"end","msg":"Tatkal booking initiated."},
"0":{"action":"goto","target":"main","msg":"Returning to main menu."}
}
},

"pnr_status":{
"prompt":"Please enter your 10 digit PNR number followed by hash.",
"options":{
"#":{"action":"lookup_pnr","msg":"Checking PNR status"}
}
},

"train_status":{
"prompt":"Press 1 Today's train running status. Press 2 Tomorrow schedule. Press 0 Back.",
"options":{
"1":{"action":"end","msg":"Your train is running on time."},
"2":{"action":"end","msg":"Tomorrow schedule available on IRCTC website."},
"0":{"action":"goto","target":"main","msg":"Back to main menu."}
}
},

"cancel_ticket":{
"prompt":"Press 1 Cancel booked ticket. Press 2 Cancellation rules. Press 0 Back.",
"options":{
"1":{"action":"end","msg":"Ticket cancellation request received."},
"2":{"action":"end","msg":"Cancellation rules sent to your email."},
"0":{"action":"goto","target":"main","msg":"Back to main menu."}
}
},

"refunds":{
"prompt":"Press 1 Check refund status. Press 2 Refund policy. Press 0 Back.",
"options":{
"1":{"action":"end","msg":"Refund status will be sent to your registered mobile number."},
"2":{"action":"end","msg":"Refund policy available on IRCTC website."},
"0":{"action":"goto","target":"main","msg":"Back to main."}
}
},

"seat":{
"prompt":"Press 1 Sleeper seat availability. Press 2 AC seat availability. Press 3 Tatkal seats. Press 0 Back.",
"options":{
"1":{"action":"end","msg":"Sleeper seat availability checked."},
"2":{"action":"end","msg":"AC seat availability checked."},
"3":{"action":"end","msg":"Tatkal seat availability checked."},
"0":{"action":"goto","target":"main","msg":"Back to main."}
}
},

"advisory":{
"prompt":"Press 1 Railway safety rules. Press 2 Luggage guidelines. Press 0 Back.",
"options":{
"1":{"action":"end","msg":"Railway safety rules available on official website."},
"2":{"action":"end","msg":"Luggage policy details provided."},
"0":{"action":"goto","target":"main","msg":"Back to main."}
}
},

"feedback":{
"prompt":"Press 1 Rate service 1 to 3. Press 2 Rate service 4 to 5. Press 0 Back.",
"options":{
"1":{"action":"end","msg":"Thanks for your feedback."},
"2":{"action":"end","msg":"Thank you for the positive feedback."},
"0":{"action":"goto","target":"main","msg":"Back to main."}
}
}

}

# ---------------- SESSION ----------------

def create_session(caller_number):

    cid=f"CALL_{random.randint(100000,999999)}"

    active_calls[cid]={
    "call_id":cid,
    "caller_number":caller_number,
    "start_time":datetime.now().isoformat(),
    "current_menu":"main",
    "pnr_buffer":""
    }

    return cid


# ---------------- ROOT ----------------

@app.get("/")
def root():
    return {
    "status":"IRCTC IVR Running",
    "active_calls":len(active_calls),
    "total_calls":len(call_history)
    }


# ---------------- START CALL ----------------

@app.post("/ivr/start")
def ivr_start(payload:CallStart):

    cid=create_session(payload.caller_number)

    return {
    "call_id":cid,
    "status":"connected",
    "prompt":MENU["main"]["prompt"]
    }


# ---------------- DTMF ----------------

@app.post("/ivr/dtmf")
def ivr_dtmf(data:DTMFInput):

    call_id=data.call_id
    digit=data.digit

    if call_id not in active_calls:
        raise HTTPException(status_code=404,detail="session missing")

    session=active_calls[call_id]
    menu_key=session["current_menu"]

    menu=MENU.get(menu_key)

    # PNR entry

    if menu_key=="pnr_status" and digit!="#":

        if digit.isdigit():

            session["pnr_buffer"]+=digit

            if len(session["pnr_buffer"])<10:
                return {"prompt":"Digit received. Please enter remaining PNR digits."}

            else:
                return {"prompt":"PNR entered. Press hash to confirm."}


    options=menu["options"]

    if digit not in options:
        return {"prompt":"Invalid option. Please try again."}

    opt=options[digit]
    action=opt["action"]
    msg=opt.get("msg","")

    if action=="goto":

        target=opt["target"]
        session["current_menu"]=target

        return {"prompt":msg+" "+MENU[target]["prompt"]}

    if action=="end":

        session["end_time"]=datetime.now().isoformat()

        call_history.append(session)

        del active_calls[call_id]

        return {"prompt":msg}

    if action=="transfer":

        session["end_time"]=datetime.now().isoformat()

        call_history.append(session)

        del active_calls[call_id]

        return {"prompt":msg}

    if action=="lookup_pnr":

        pnr=session["pnr_buffer"]

        if len(pnr)==10:

            session["end_time"]=datetime.now().isoformat()

            call_history.append(session)

            del active_calls[call_id]

            return {"prompt":f"PNR {pnr} confirmed. Train departs at 6 PM from Vijayawada."}

        else:

            session["pnr_buffer"]=""

            return {"prompt":"Invalid PNR number."}


# ---------------- END CALL ----------------

@app.post("/ivr/end")
def ivr_end(call_id:str=Query(...)):

    if call_id in active_calls:

        s=active_calls[call_id]

        s["end_time"]=datetime.now().isoformat()

        call_history.append(s)

        del active_calls[call_id]

        return {"status":"ended"}

    return {"status":"not found"}