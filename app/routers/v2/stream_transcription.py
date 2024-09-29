# Path: app/routers/v2/stream_transcription.py

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

SAMPLE_RATE = 16000