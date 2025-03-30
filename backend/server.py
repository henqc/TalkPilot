# In server.py - Add a global variable to track the current thread
from fastapi import FastAPI
from threading import Thread
from pydantic import BaseModel
import time

from backend.picovoice import start_listening, stop_listening
from backend.testing import cleanup_resources

app = FastAPI()
listen_thread = None  # Add this global variable

class user_settings(BaseModel):
    sound_threshold: int
    silence_duration: int

@app.post("/listen")
def listen(data: user_settings):
    global listen_thread
    
    # If there's an existing thread, make sure it's stopped
    if listen_thread and listen_thread.is_alive():
        stop_listening()  # Add a way to signal the thread to stop
        listen_thread.join(timeout=2)  # Wait for it to finish
    
    def run():
        start_listening(data.sound_threshold, data.silence_duration)

    listen_thread = Thread(target=run)
    listen_thread.daemon = True  # Make it a daemon thread so it exits when main program exits
    listen_thread.start()
    return {"status": "Listening started"}

@app.get("/end")
def end():
    # return {"status": "Listening stopped"}
    global listen_thread
    
    # Signal the thread to stop
    stop_listening()
    
    # Wait for the thread to finish
    if listen_thread and listen_thread.is_alive():
        listen_thread.join(timeout=2)
    
    # Clean up resources
    cleanup_resources()
    
    stop_listening()
    
    return {"status": "Listening stopped"}