# Path: microservice.py

from utils.whisper import transcribe

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    transcription, process_time = transcribe(audio_file.file)
    return JSONResponse(
        content={"transcription": transcription, "process_time": process_time}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.253", port=8000)
