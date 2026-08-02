from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random
import os

from dotenv import load_dotenv

load_dotenv()


# ================= TWILIO CONFIG =================

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")
NGROK_URL = os.getenv("NGROK_URL")


try:
    from twilio.rest import Client
    client = Client(
        TWILIO_SID,
        TWILIO_AUTH
    )
except:
    client=None



app = FastAPI(
    title="AI Conversational IRCTC IVR",
    version="2.0"
)



# ================= CORS =================


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)



# ================= MODELS =================



class CallStart(BaseModel):

    caller_number:str

    call_id:Optional[str]=None



class DTMFInput(BaseModel):

    call_id:str

    digit:str

    current_menu:str



# NEW MODEL FOR NATURAL SPEECH

class VoiceInput(BaseModel):

    call_id:str

    text:str





# ================= MEMORY =================


active_calls={}

call_history=[]




# ================= IRCTC MENU =================


MENU={


"main":{

"prompt":
"Welcome to IRCTC Railway Services. "
"Press 1 Ticket Booking. "
"Press 2 PNR Status. "
"Press 3 Train Running Status. "
"Press 4 Ticket Cancellation. "
"Press 5 Refund Status. "
"Press 6 Seat Availability. "
"Press 9 Customer Support.",


"options":{

"1":{
"action":"goto",
"target":"booking",
"msg":"Ticket booking selected."
},

"2":{
"action":"goto",
"target":"pnr_status",
"msg":"PNR status selected."
},

"3":{
"action":"goto",
"target":"train_status",
"msg":"Train running status selected."
},

"4":{
"action":"goto",
"target":"cancel_ticket",
"msg":"Ticket cancellation selected."
},

"5":{
"action":"goto",
"target":"refunds",
"msg":"Refund option selected."
},

"6":{
"action":"goto",
"target":"seat",
"msg":"Seat availability selected."
},

"9":{
"action":"transfer",
"msg":"Connecting to customer support."
}

}

},



"booking":{

"prompt":
"Press 1 Sleeper booking. "
"Press 2 AC booking. "
"Press 3 Tatkal booking.",


"options":{

"1":{
"action":"end",
"msg":"Sleeper booking initiated."
},

"2":{
"action":"end",
"msg":"AC booking initiated."
},

"3":{
"action":"end",
"msg":"Tatkal booking initiated."
}

}

},



"pnr_status":{

"prompt":
"Please enter your 10 digit PNR number.",

"options":{}

},



"train_status":{

"prompt":
"Press 1 Today's running status. "
"Press 2 Tomorrow schedule.",


"options":{

"1":{
"action":"end",
"msg":"Your train is running on time."
},

"2":{
"action":"end",
"msg":"Tomorrow schedule available."
}

}

},



"cancel_ticket":{

"prompt":
"Press 1 Cancel ticket. "
"Press 2 Cancellation rules.",


"options":{

"1":{
"action":"end",
"msg":"Cancellation request received."
},

"2":{
"action":"end",
"msg":"Cancellation rules provided."
}

}

},



"refunds":{

"prompt":
"Press 1 Check refund status. "
"Press 2 Refund policy.",


"options":{

"1":{
"action":"end",
"msg":"Your refund status is being processed."
},

"2":{
"action":"end",
"msg":"Refund policy provided."
}

}

},



"seat":{

"prompt":
"Press 1 Sleeper seats. "
"Press 2 AC seats.",


"options":{

"1":{
"action":"end",
"msg":"Sleeper availability checked."
},

"2":{
"action":"end",
"msg":"AC availability checked."
}

}

}


}
