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

# ================= SESSION =================


def create_session(caller_number):

    cid = f"CALL_{random.randint(100000,999999)}"


    active_calls[cid]={

        "call_id":cid,

        "caller_number":caller_number,

        "start_time":datetime.now().isoformat(),

        "current_menu":"main",

        "pnr_buffer":""

    }


    return cid





# ================= ROOT =================


@app.get("/")
def root():

    return {

        "status":"AI IRCTC IVR Running",

        "active_calls":len(active_calls),

        "total_calls":len(call_history)

    }





# ================= START CALL =================


@app.post("/ivr/start")
def ivr_start(payload:CallStart):


    cid=create_session(
        payload.caller_number
    )


    return {

        "call_id":cid,

        "status":"connected",

        "prompt":MENU["main"]["prompt"]

    }





# ================= AI INTENT RECOGNITION =================


def detect_intent(text):


    text=text.lower()



    if any(x in text for x in [

        "book",

        "booking",

        "reserve",

        "ticket"

    ]):

        return "booking"



    elif any(x in text for x in [

        "pnr",

        "ticket status",

        "status of my ticket"

    ]):

        return "pnr_status"



    elif any(x in text for x in [

        "train status",

        "running status",

        "where is my train",

        "train location"

    ]):

        return "train_status"



    elif any(x in text for x in [

        "cancel",

        "cancel ticket",

        "cancellation"

    ]):

        return "cancel_ticket"



    elif any(x in text for x in [

        "refund",

        "refund status",

        "money back"

    ]):

        return "refunds"



    elif any(x in text for x in [

        "seat",

        "availability",

        "available seat"

    ]):

        return "seat"



    elif any(x in text for x in [

        "customer care",

        "support",

        "agent"

    ]):

        return "support"



    return "unknown"






# ================= NATURAL VOICE API =================



@app.post("/ivr/voice")
def ivr_voice(data:VoiceInput):


    if data.call_id not in active_calls:

        raise HTTPException(

            status_code=404,

            detail="Call session not found"

        )


    session=active_calls[data.call_id]


    intent=detect_intent(data.text)



    if intent=="booking":


        session["current_menu"]="booking"


        return {

            "intent":"BOOK_TICKET",

            "prompt":

            "Sure. Ticket booking selected. "

            + MENU["booking"]["prompt"]

        }




    elif intent=="pnr_status":


        session["current_menu"]="pnr_status"


        return {

            "intent":"CHECK_PNR",

            "prompt":

            "Please enter your 10 digit PNR number."

        }




    elif intent=="train_status":


        session["current_menu"]="train_status"


        return {

            "intent":"TRAIN_STATUS",

            "prompt":

            MENU["train_status"]["prompt"]

        }





    elif intent=="cancel_ticket":


        session["current_menu"]="cancel_ticket"


        return {

            "intent":"CANCEL_TICKET",

            "prompt":

            MENU["cancel_ticket"]["prompt"]

        }




    elif intent=="refunds":


        session["current_menu"]="refunds"


        return {

            "intent":"REFUND_STATUS",

            "prompt":

            MENU["refunds"]["prompt"]

        }




    elif intent=="seat":


        session["current_menu"]="seat"


        return {

            "intent":"SEAT_AVAILABILITY",

            "prompt":

            MENU["seat"]["prompt"]

        }





    elif intent=="support":


        return {

            "intent":"TRANSFER",

            "prompt":

            "Connecting you to IRCTC customer support."

        }





    else:


        return {

            "intent":"UNKNOWN",

            "prompt":

            "Sorry, I did not understand. "
            "Please say booking, PNR, refund or cancellation."

        }







# ================= DTMF HANDLER =================


@app.post("/ivr/dtmf")
def ivr_dtmf(data:DTMFInput):


    call_id=data.call_id


    digit=data.digit



    if call_id not in active_calls:


        raise HTTPException(

            status_code=404,

            detail="session missing"

        )



    session=active_calls[call_id]


    menu_key=session["current_menu"]


    menu=MENU.get(menu_key)



    if digit not in menu["options"]:


        return {

            "prompt":

            "Invalid option. Please try again."

        }




    option=menu["options"][digit]


    action=option["action"]


    msg=option["msg"]




    if action=="goto":


        target=option["target"]


        session["current_menu"]=target


        return {


            "prompt":

            msg+" "+MENU[target]["prompt"]

        }




    elif action=="end":


        session["end_time"]=datetime.now().isoformat()


        call_history.append(session)


        del active_calls[call_id]



        return {

            "prompt":msg

        }





    elif action=="transfer":


        session["end_time"]=datetime.now().isoformat()


        call_history.append(session)


        del active_calls[call_id]



        return {

            "prompt":msg

        }






# ================= END CALL =================


@app.post("/ivr/end")
def ivr_end(call_id:str=Query(...)):


    if call_id in active_calls:


        session=active_calls[call_id]


        session["end_time"]=datetime.now().isoformat()


        call_history.append(session)


        del active_calls[call_id]


        return {

            "status":"ended"

        }



    return {


        "status":"not found"

    }
