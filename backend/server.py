from fastapi import FastAPI
from threading import Thread
from pydantic import BaseModel
import time

from backend.picovoice import start_listening
from backend.testing import cleanup_resources

# To run: uvicorn backend.server:app --reload

app = FastAPI()

class user_settings(BaseModel):
    sound_threshold: int
    silence_duration: int

@app.post("/listen")
def listen(data: user_settings):
    def run():
        start_listening(data.sound_threshold, data.silence_duration)

    thread = Thread(target=run)
    thread.start()
    return {"status": "Listening started"}

@app.get("/end")
def end():
    cleanup_resources()
