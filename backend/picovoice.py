import pvporcupine
import os
from dotenv import load_dotenv

load_dotenv()

pico_key = os.getenv("PICO_KEY")


porcupine = pvporcupine.create(
  access_key=pico_key,
  keywords=['Hey Talk Pilot']
)

def get_next_audio_frame():
  pass


while True:
    audio_frame = get_next_audio_frame()
    keyword_index = porcupine.process(audio_frame)
    if keyword_index == 0:
        # detected `porcupine`
        print("ts frickin broken")
    elif keyword_index == 1:
        # detected `bumblebee`
        print("ts frickin broken")

porcupine.delete()
