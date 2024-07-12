# Path: app/routers/v1/file_transcription.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.utils.whisper import transcribe

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe an uploaded audio file.

    Args:
        audio_file (UploadFile): The audio file to be transcribed.

    Returns:
        JSONResponse: A JSON response containing the transcription and processing time.
    """
    transcription, process_time = transcribe(audio_file.file)
    return JSONResponse(content={"transcription": transcription, "process_time": process_time})
