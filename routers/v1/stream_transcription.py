# Filename: routers/v1/stream_transcription.py

import pyaudio
from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect
# from starlette.websockets import WebSocketDisconnect
from utils.whisper import transcribe

STREAM_FORMAT = pyaudio.paInt16

router = APIRouter()

@router.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handle WebSocket connections for real-time audio transcription.

    Args:
        websocket (WebSocket): The WebSocket connection.

    Returns:
        None
    """
    await websocket.accept()
    # print("Connection established")
    end_of_speech_signal = b'\x00\x00\x00\x00'

    try:
        while True:
            audio_data = bytearray()
            
            while True:
                try:
                    data = await websocket.receive_bytes()
                except WebSocketDisconnect as e:
                    print(f"WebSocket disconnected with code {e.code}, reason: {e.reason}")
                    return
                
                if data == end_of_speech_signal:
                    break
                audio_data.extend(data)
            
            # Save raw audio data to a file
            with open("temp_last_audio.raw", "wb") as f:
                f.write(audio_data)
            
            # Process the received audio data using the transcribe function
            print(f"Processing {len(audio_data)} bytes ≈ ({len(audio_data) / (16_000 * STREAM_FORMAT.bit_length())}s) of audio bytes")
            transcription, process_time = transcribe(audio_data)
            
            # Reset the audio data buffer
            audio_data.clear()
            
            # Send the transcription and processing time back to the client
            response = {"transcription": transcription, "process_time": process_time}
            await websocket.send_json(response)

    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected with code {e.code}, reason: {e.reason}")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.close()
    finally:
        pass
        # await websocket.close()
        # print("WebSocket connection closed")
