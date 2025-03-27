import argparse
import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Stream
import uvicorn
from bot import run_bot

app = FastAPI()

# Enable CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of phone numbers to dial
#phone_numbers = ["+13322875843","+13322875766"]  # Replace with your list of numbers

# Counter to track which number is being dialed
#current_number_index = 0

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
    stream = Stream(url="wss://f452-34-82-42-179.ngrok-free.app/ws")
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

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipecat Twilio Chatbot Server")
    parser.add_argument(
        "-t", "--test", action="store_true", default=False, help="set the server in testing mode"
    )
    args, _ = parser.parse_known_args()

    app.state.testing = args.test

    uvicorn.run(app, host="0.0.0.0", port=8765)
