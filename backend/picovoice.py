from faster_whisper import WhisperModel
from pvrecorder import PvRecorder
from dotenv import load_dotenv
from TTS.api import TTS
from backend.testing import *
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
SILENCE_THRESHOLD = 30
MAX_SILENCE_DURATION = 3.0

# Initialize Porcupine, Whisper, and TTS Models
porcupine = pvporcupine.create(
    access_key=pico_key,
    keyword_paths=["backend/models/Hey-Talk-Pilot_en_mac_v3_0_0.ppn"],
    model_path="backend/models/porcupine_params.pv"
)
whisper_model = WhisperModel("base.en", compute_type="int8")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)


# Record user input until user stops talking
def record():
    print("Recording started.")

    buffer = []
    silence_start_time = None
    stream_closed = False

    def audio_callback(indata, frames, timing_info, status):
        nonlocal silence_start_time, stream_closed
        volume = np.linalg.norm(indata) * 10
        buffer.append(indata.copy())

        if volume < SILENCE_THRESHOLD:
            if silence_start_time is None:
                silence_start_time = time.time()
        else:
            silence_start_time = None

        if silence_start_time is not None and time.time() - silence_start_time > MAX_SILENCE_DURATION:
            print("Silence detected. Recording ended.")
            stream_closed = True

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback) as stream:
        # Delay to start mic
        sd.sleep(500)
        while not stream_closed:
            time.sleep(0.1)

        # Wait to process audio
        time.sleep(0.3)

    # Save file as .wav
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
    tts.tts_to_file(text=input, file_path="backend/output.wav")

# TTS method to play audio file
def play_audio(file_path):
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait() 
    
# # AI request routing agent
# def route_request(input):
    

# Method to start Talk Pilot wake word listen
def start_listening():
    global latest_transcription

    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
    recorder.start()
    print("Listening for 'Hey Talk Pilot'...")

    try:
        while True:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Trigger word detected")
                audio_path = record()
                print("\n \n \n \n  Hi1 \n \n \n \n \n")
                start = time.time()
                print("\n \n \n \n  Hi1.5 \n \n \n \n \n")
                latest_transcription = transcribe_audio(audio_path)
                print("\n \n \n \n  Hi2 \n \n \n \n \n")
                final_transcription = asyncio.run(run_agent(latest_transcription))
                print("\n \n \n \n  Hi3 \n \n \n \n \n")
                audio_tts(final_transcription)
                print(f"Took {time.time() - start:.2f} seconds")
                play_audio("backend/output.wav")

    except KeyboardInterrupt:
        print("Stopped by user")

    finally:
        recorder.stop()
        recorder.delete()
        porcupine.delete()
    