from fastapi import FastAPI, Form, Request, Response # <--- Added Response
from twilio.twiml.messaging_response import MessagingResponse
from agent import process_user_message

app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    # 1. Get the message
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').strip()
    
    print(f"📥 USER SAID: {incoming_msg}")

    # 2. Ask Agent
    ai_response_text = process_user_message(incoming_msg)

    print(f"📤 AGENT REPLIED: {ai_response_text}")

    # 3. Create Twilio XML Response
    resp = MessagingResponse()
    resp.message(ai_response_text)
    
    # 4. CRITICAL FIX: Explicitly set media_type to XML
    return Response(content=str(resp), media_type="application/xml")