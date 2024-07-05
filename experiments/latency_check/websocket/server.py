"""
FastAPI Server for Streaming Audio File Upload via WebSockets

This FastAPI server is designed to accept streaming audio files via WebSocket connections.
The audio files are uploaded as raw binary data, and the server responds with the size of the received file
when the client indicates that the streaming has stopped using a binary end-of-stream signal.

To run the server, execute the following command:
    python server_ws_stream.py
"""

from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/ws/upload-audio/")
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
    
    size = len(audio_data)
    response = {"message": "Last byte received", "size": size}
    await websocket.send_json(response)
    await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
