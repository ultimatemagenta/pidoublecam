import os
import time
import subprocess
from datetime import datetime
from threading import Thread
from config.recorder_config import SEGMENT_DURATION_SEC, TEMP_DIR
from state_manager import is_recording, get_event

AUDIO_DEVICE = "plughw:0"  # À adapter si nécessaire
SAMPLE_RATE = 44100
CHANNELS = 1
FORMAT = "S16_LE"  # 16-bit little-endian PCM

def start_audio_recording(output_dir):
    seg_num = 0
    while is_recording():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"AUDIO_{timestamp}_seg{seg_num:02d}.wav"
        filepath = os.path.join(output_dir, filename)

        print(f"🎙️ Début audio segment {seg_num}")
        cmd = [
            "arecord",
            "-D", AUDIO_DEVICE,
            "-f", FORMAT,
            "-r", str(SAMPLE_RATE),
            "-c", str(CHANNELS),
            "-d", str(SEGMENT_DURATION_SEC),
            filepath
        ]
        subprocess.run(cmd)
        seg_num += 1

    print("🛑 Fin de l'enregistrement audio")

def run():
    print("🎙️ Audio Recorder prêt, en attente de déclenchement...")
    event = get_event()

    while True:
        event.wait()
        os.makedirs(TEMP_DIR, exist_ok=True)

        # 🔖 On lit la session déjà écrite par mjpeg_recorder
        try:
            with open(os.path.join(TEMP_DIR, ".current_session"), "r") as f:
                session = f.read().strip()
        except FileNotFoundError:
            session = datetime.now().strftime("session_%Y%m%d_%H%M%S")

        print(f"🎧 Début session audio : {session}")
        start_audio_recording(TEMP_DIR)
        print("✅ Fin session audio")
