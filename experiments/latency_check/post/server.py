"""
FastAPI Server for Audio File Upload

This FastAPI server is designed to accept audio files via a POST request.
The audio files are uploaded as raw binary data and the server responds
with the filename and size of the received file.

Dependencies:
- fastapi
- uvicorn

To run the server, execute the following command:
    python server.py
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    contents = await file.read()
    # You can add processing logic here if needed
    return JSONResponse(content={"filename": file.filename, "size": len(contents)}, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
