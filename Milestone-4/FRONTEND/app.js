// =====================================================
// AI IRCTC IVR DASHBOARD JAVASCRIPT
// =====================================================


// Change this after deployment
const API_URL = "https://ai-enabled-conversational-ivr-ste4.onrender.com";




// =====================================================
// LOAD DASHBOARD DATA
// =====================================================


async function loadDashboard(){


    try{


        // ----------------------------
        // ACTIVE CALLS
        // ----------------------------


        const activeResponse =
            await fetch(
                `${API_URL}/active`
            );


        const activeData =
            await activeResponse.json();



        document.getElementById(
            "activeCalls"
        ).innerText =
            activeData.count;




        const table =
            document.getElementById(
                "callTable"
            );



        table.innerHTML = "";




        if(activeData.calls.length===0){


            table.innerHTML = `

            <tr>

            <td colspan="5">

            No active calls

            </td>

            </tr>

            `;


        }

        else{


            activeData.calls.forEach(
                call=>{


                table.innerHTML += `


                <tr>


                <td>

                📞 ${call.phone}

                </td>



                <td>

                ${call.intent || "Listening"}

                </td>



                <td>

                ⏱ ${call.duration}

                </td>



                <td>

                <span class="live">

                ${call.status}

                </span>

                </td>



                <td>


                <button onclick="hangup('${call.call_sid}')">

                Disconnect

                </button>


                </td>


                </tr>


                `;


                }

            );


        }





        // ----------------------------
        // ANALYTICS
        // ----------------------------


        const analyticsResponse =
            await fetch(
                `${API_URL}/analytics`
            );


        const analytics =
            await analyticsResponse.json();





        document.getElementById(
            "totalCalls"
        ).innerText =
            analytics.total_calls || 0;





        document.getElementById(
            "tickets"
        ).innerText =
            analytics.successful_bookings || 0;





        document.getElementById(
            "pnr"
        ).innerText =
            analytics.pnr_queries || 0;




        document.getElementById(
            "refund"
        ).innerText =
            analytics.refund_requests || 0;



        document.getElementById(
            "success"
        ).innerText =
            analytics.total_calls || 0;



    }

    catch(error){


        console.log(
            "Dashboard Error:",
            error
        );


    }


}









// =====================================================
// HANGUP BUTTON
// =====================================================


async function hangup(callSid){



    try{


        await fetch(

            `${API_URL}/hangup/${callSid}`,

            {

                method:"POST"

            }

        );



        alert(
            "Call disconnected successfully"
        );



        loadDashboard();


    }

    catch(error){


        console.log(error);


    }


}









// =====================================================
// LOAD CONVERSATION HISTORY
// =====================================================


async function loadConversation(){


    try{


        const response =
            await fetch(
                `${API_URL}/history`
            );



        const data =
            await response.json();



        const chat =
            document.getElementById(
                "conversation"
            );



        chat.innerHTML="";




        if(
            data.history &&
            data.history.length>0
        ){



            let latest =
            data.history[
                data.history.length-1
            ];



            latest.conversation.forEach(
                msg=>{


                    chat.innerHTML += `


                    <div class="user-message">

                    👤 ${msg.user}

                    </div>



                    <div class="ai-message">

                    🤖 ${msg.bot}

                    </div>


                    `;


                }

            );



        }


        else{


            chat.innerHTML = `


            <div class="ai-message">

            🤖 Waiting for customer interaction...

            </div>


            `;


        }



    }

    catch(error){


        console.log(error);


    }


}









// =====================================================
// AUTO REFRESH
// =====================================================



setInterval(

    ()=>{


        loadDashboard();

        loadConversation();


    },

    3000

);







// INITIAL LOAD


loadDashboard();

loadConversation();
