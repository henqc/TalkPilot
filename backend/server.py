from fastapi import FastAPI
from threading import Thread
import time

from backend.picovoice import start_listening

# To run: uvicorn backend.server:app --reload

app = FastAPI()

@app.get("/listen")
def listen():
    def run():
        start_listening()

    thread = Thread(target=run)
    thread.start()
    return {"status": "Listening started"}
