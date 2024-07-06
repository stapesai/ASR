# Filename: routers/v1/__init__.py

from fastapi import APIRouter
from routers.v1.file_transcription import router as file_transcription_router
from routers.v1.stream_transcription import router as stream_transcription_router

router = APIRouter()
router.include_router(file_transcription_router)
router.include_router(stream_transcription_router)
