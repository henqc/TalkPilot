from faster_whisper import WhisperModel
from pvrecorder import PvRecorder
from dotenv import load_dotenv
from TTS.api import TTS
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

# Initialize Porcupine with ppn and model
porcupine = pvporcupine.create(
    access_key=pico_key,
    keyword_paths=["backend/models/Hey-Talk-Pilot_en_mac_v3_0_0.ppn"],
    model_path="backend/models/porcupine_params.pv"
)

# Whisper model for transcription
whisper_model = WhisperModel("base.en", compute_type="int8")

def record_until_silence():
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

    
def transcribe_audio(path):
    segments, _ = whisper_model.transcribe(path)
    return " ".join(segment.text.strip() for segment in segments)

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

def audio_tts(response):
    tts.tts_to_file(text=response, file_path="backend/output.wav")

def play_audio(file_path):
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait() 

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
                print("🚀 Trigger word detected")
                audio_path = record_until_silence()
                start = time.time()
                latest_transcription = transcribe_audio(audio_path)
                print(f"Transcription: {latest_transcription}")
                audio_tts(latest_transcription)
                print(f"Took {time.time() - start:.2f} seconds")
                play_audio("backend/output.wav")

    except KeyboardInterrupt:
        print("🛑 Stopped by user")

    finally:
        recorder.stop()
        recorder.delete()
        porcupine.delete()