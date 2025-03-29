import os
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder

# Load environment variables
load_dotenv()
pico_key = os.getenv("PICO_KEY")

# Initialize Porcupine with your custom PPN file and model
porcupine = pvporcupine.create(
    access_key=pico_key,
    keyword_paths=["backend/models/Hey-Talk-Pilot_en_mac_v3_0_0.ppn"],
    model_path="backend/models/porcupine_params.pv"
)

# Start recording from default mic
recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
recorder.start()

print("Listening for 'Hey Talk Pilot'")

try:
    while True:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Trigger word detected")

except KeyboardInterrupt:
    print("\nStopping")

finally:
    recorder.stop()
    recorder.delete()
    porcupine.delete()
