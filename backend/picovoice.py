from faster_whisper import WhisperModel
from pvrecorder import PvRecorder
from dotenv import load_dotenv
from TTS.api import TTS
from backend.testing import *
from pathlib import Path
from openai import OpenAI
import asyncio
import pvporcupine
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import time
import os

# Load environment variables
load_dotenv()
pico_key = os.getenv("PICO_KEY")

# Mic threshold settings
SAMPLE_RATE = 16000
CHANNELS = 1
# SILENCE_THRESHOLD = 5
# MAX_SILENCE_DURATION = 3

# Initialize Porcupine, Whisper, OpenAI Models
porcupine = pvporcupine.create(
    access_key=pico_key,
    keyword_paths=["backend/models/Hey-Talk-Pilot_en_mac_v3_0_0.ppn"],
    model_path="backend/models/porcupine_params.pv"
)
whisper_model = WhisperModel("base.en", compute_type="int8")
# tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
openai_agent = OpenAI()

# Record user input until user stops talking
def record(sound_threshold, silence_duration):
    play_audio("backend/audio/uh_huh.wav")
    print("Recording started.")

    buffer = []
    silence_start_time = None
    stream_closed = False
    grace_counter = 0

    # Sensitivity tuning
    grace_limit = 25

    def audio_callback(indata, frames, timing_info, status):
        nonlocal silence_start_time, stream_closed, grace_counter

        volume = np.linalg.norm(indata) * 10
        buffer.append(indata.copy())

        if volume < sound_threshold:
            grace_counter += 1

            # Only start the timer if grace has been exceeded AND the timer hasn't already started
            if grace_counter > grace_limit and silence_start_time is None:
                silence_start_time = time.time()
        else:
            # Reset grace + timer on any sound detected
            if grace_counter > 0 or silence_start_time is not None:
                print("Voice detected again. Resetting grace and silence timer.")
            grace_counter = 0
            silence_start_time = None

        # Final silence check — if timer has been running too long, stop
        if silence_start_time and time.time() - silence_start_time > silence_duration:
            print("Silence detected. Recording ended.")
            stream_closed = True

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback):
        sd.sleep(500)
        while not stream_closed:
            time.sleep(0.1)
        time.sleep(0.3) 

    # Save audio to temp file
    audio_data = np.concatenate(buffer, axis=0)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        sf.write(tmpfile.name, audio_data, SAMPLE_RATE)
        print(f"Saved audio to {tmpfile.name}")
        return tmpfile.name

# Transcribe audio file from path to text
def transcribe_audio(path):
    segments, _ = whisper_model.transcribe(path)
    return " ".join(segment.text.strip() for segment in segments)

# TTS method to create audio file
def audio_tts(input):
    # tts.tts_to_file(text=input, file_path="backend/output.wav")
    with openai_agent.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=input,
        instructions="Speak in a kind warm tone.",
    ) as response:
        response.stream_to_file("backend/output.wav")

# TTS method to play audio file
def play_audio(file_path):
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait() 
    
# AI request routing agent
def route_request(input):
    play_audio("backend/audio/on_it.wav")
    completion = openai_agent.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You're an intent router. Your job is to classify the user's message into one of two categories:\n"
                    "- 'request' if the user wants to take an action, like opening a website, searching something, or controlling an app.\n"
                    "- 'query' if the user is just asking a question or having a conversation.\n\n"
                    "Respond with only one word: 'request' or 'query'. No explanation."
                )
            },
            {
                "role": "user",
                "content": input
            }
        ]
    )

    result = completion.choices[0].message.content.strip().lower()
    return result
    

# Initialize resources at startup
def initialize_resources():
    from backend.testing import init_browser
    init_browser()

# Method to start Talk Pilot wake word listen
def start_listening(sound_threshold, silence_duration):
    global transcription
    
    # Initialize resources
    initialize_resources()
    
    from backend.testing import loop
    
    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
    recorder.start()
    print("Listening for 'Hey Talk Pilot'...")

    try:
        while True:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Trigger word detected")
                audio_path = record(sound_threshold, silence_duration)
                start = time.time()
                transcription = transcribe_audio(audio_path)
                
                # route request
                route_res = route_request(transcription)
                
                if route_res == "request":
                    final_transcription = loop.run_until_complete(run_agent(transcription))
                elif route_res == "query":
                    completion = openai_agent.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a nice assistant. Answer the following prompt in a nice tone. Keep your answer short."
                                )
                            },
                            {
                                "role": "user",
                                "content": transcription
                            }
                        ],
                        max_tokens=250
                    )

                    final_transcription = completion.choices[0].message.content.strip().lower()
                else:
                    final_transcription = "Error fulfilling request."
                    
                audio_tts(final_transcription)
                print(f"Took {time.time() - start:.2f} seconds")
                play_audio("backend/output.wav")
                
                # Add a small small delay to make sure everything is processed
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("Stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        recorder.stop()
        recorder.delete()
        porcupine.delete()
        
        # Clean up browser resources
        from backend.testing import cleanup_resources
        cleanup_resources()