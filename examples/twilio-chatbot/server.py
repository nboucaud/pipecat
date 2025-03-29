import argparse
import json
import asyncio
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Stream
import uvicorn
from bot import run_bot
import datetime
from call_logger import log_call
from transcript_store import transcript_store, transcript_lock
from pipecat.services.together import TogetherLLMService
import os
app = FastAPI()

# Enable CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
async def start_call():
    #global current_number_index

    # Check if there are more numbers to dial
    #if current_number_index >= len(phone_numbers):
        #return HTMLResponse(content="<Response></Response>", media_type="application/xml")

    # Get the current phone number
    #current_number = phone_numbers[current_number_index]

    # Generate TwiML for dialing the current number
    response = VoiceResponse()
    connect = response.connect()
    stream = Stream(url="wss://4e33-102-152-170-102.ngrok-free.app/ws")
    connect.append(stream)
    response.pause(length=40)

    print(f"TwiML Generated:")
    print(str(response))  # Log the generated TwiML
    #print(f"Dialing: {current_number}")
    #current_number_index += 1  # Move to the next number after this call

    # Return the TwiML as XML
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket connection requested")
    await websocket.accept()
    print("WebSocket connection accepted")
    start_data = websocket.iter_text()
    await start_data.__anext__()  # Ignore the first message (handshake)
    call_data = json.loads(await start_data.__anext__())
    print(f"Received call data: {call_data}", flush=True)
    stream_sid = call_data["start"]["streamSid"]
    print(f"Stream SID: {stream_sid}")
    print("Calling run_bot function...")
    await run_bot(websocket, stream_sid, app.state.testing)

@app.post("/call_status")
async def call_status(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid")
    call_status = form.get("CallStatus")
    call_duration = form.get("CallDuration", "")  # might be empty if call wasn’t answered
    target_number = form.get("To")
    source_number = form.get("From")
    timestamp_start = datetime.datetime.utcnow().isoformat()

    async with transcript_lock:
        transcript = transcript_store.get(call_sid, "")

    # Generate a summary using TogetherAI Deepseek if there is a transcript.
    call_summary = ""
    if transcript:
        llm = TogetherLLMService(
            api_key=os.getenv("TOGETHER_API_KEY"),
            model="deepseek-ai/DeepSeek-V3"
        )
        prompt = f"Please summarize the following conversation transcript concisely:\n\n{transcript}"
        response = await llm.chat([{"role": "system", "content": prompt}])
        call_summary = response["choices"][0]["message"]["content"]

    # Log call details (assuming log_call is defined in call_logger.py)
    log_call(timestamp_start, call_duration or call_status, call_summary, target_number, source_number)
    
    print(f"Logged call {call_sid}: {call_status}, from {source_number} to {target_number}")
    return "OK"


    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipecat Twilio Chatbot Server")
    parser.add_argument(
        "-t", "--test", action="store_true", default=False, help="set the server in testing mode"
    )
    args, _ = parser.parse_known_args()

    app.state.testing = args.test

    uvicorn.run(app, host="0.0.0.0", port=8765)
