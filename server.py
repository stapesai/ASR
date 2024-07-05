# Path: server.py

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # GPU-0

from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
from utils.whisper import transcribe

app = FastAPI()

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    transcription, process_time = transcribe(audio_file.file)
    return JSONResponse(
        content={"transcription": transcription, "process_time": process_time}
    )

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Connection established")
    audio_data = bytearray()
    end_of_stream_signal = b'\x00\x00\x00\x00'
    
    while True:
        data = await websocket.receive_bytes()
        if data == end_of_stream_signal:
            break
        else:
            audio_data.extend(data)
    
    # Process the received audio data using the transcribe function
    import io
    audio_file = io.BytesIO(audio_data)
    transcription, process_time = transcribe(audio_file)
    
    response = {"transcription": transcription, "process_time": process_time}
    await websocket.send_json(response)
    await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
