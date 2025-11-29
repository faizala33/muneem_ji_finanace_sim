import os
from fastapi import FastAPI, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client # <--- NEW IMPORT
from dotenv import load_dotenv
from agent import process_user_message, load_db # Import load_db to get context

load_dotenv()
app = FastAPI()

# --- 🧠 IN-MEMORY STORAGE ---
CHAT_HISTORY = {} 

# --- 📤 NEW: OUTBOUND MESSAGE FUNCTION ---
def send_whatsapp_message(to_number, body_text):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Ensure number format is correct (whatsapp:+91...)
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:+91{to_number}" # Assuming India (+91)
            
        message = client.messages.create(
            from_=from_number,
            body=body_text,
            to=to_number
        )
        print(f"✅ Welcome Message Sent to {to_number}: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

# --- 🔗 NEW ENDPOINT FOR DASHBOARD ---
@app.post("/trigger-welcome")
async def trigger_welcome(request: Request):
    """Called by Streamlit when user registers"""
    data = await request.json()
    mobile = data.get("mobile")
    name = data.get("name")
    
    # Create a personalized welcome
    welcome_msg = f"👋 Namaste {name}! I am MuneemAI, your Financial Manager.\n\nI have noted your goal and current debt. You can now tell me 'I made 5000' or 'Invest 2000'.\n\nLet's start!"
    
    send_whatsapp_message(mobile, welcome_msg)
    return {"status": "sent"}

# --- 📥 EXISTING WEBHOOK ---
@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    user_id = form_data.get('From') 
    incoming_msg = form_data.get('Body', '').strip()
    print(f"📥 {user_id} SAID: {incoming_msg}")

    if user_id not in CHAT_HISTORY: CHAT_HISTORY[user_id] = []
    user_history = CHAT_HISTORY[user_id][-10:]

    ai_response_text = process_user_message(incoming_msg, user_history)
    print(f"📤 AGENT REPLIED: {ai_response_text}")

    CHAT_HISTORY[user_id].append({"role": "user", "content": incoming_msg})
    CHAT_HISTORY[user_id].append({"role": "ai", "content": ai_response_text})

    resp = MessagingResponse()
    resp.message(ai_response_text)
    return Response(content=str(resp), media_type="application/xml")