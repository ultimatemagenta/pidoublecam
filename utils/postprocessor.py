import os
import time
import subprocess
from state_manager import is_recording
from config.recorder_config import BASE_OUTPUT_DIR

SLEEP_INTERVAL = 60  # secondes
VALID_EXT = ".mjpeg"

def convert_mjpeg_to_mp4(mjpeg_path):
    mp4_path = mjpeg_path.replace(".mjpeg", ".mp4")
    if os.path.exists(mp4_path):
        print(f"⏩ Déjà converti : {mp4_path}")
        return
    print(f"🎞️ Conversion : {os.path.basename(mjpeg_path)} → .mp4")
    try:
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", mjpeg_path,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            mp4_path
        ], check=True)
        os.remove(mjpeg_path)
        print(f"✅ Fichier converti et supprimé : {mjpeg_path}")
    except Exception as e:
        print(f"❌ Erreur conversion {mjpeg_path}: {e}")

def run():
    print("🧼 Post-processor actif")
    while True:
        if is_recording():
            time.sleep(SLEEP_INTERVAL)
            continue

        for session_dir in os.listdir(BASE_OUTPUT_DIR):
            full_path = os.path.join(BASE_OUTPUT_DIR, session_dir)
            if not os.path.isdir(full_path):
                continue

            mjpegs = [f for f in os.listdir(full_path) if f.endswith(VALID_EXT)]
            if not mjpegs:
                continue

            print(f"📂 Session à convertir : {session_dir}")
            for mjpeg in mjpegs:
                convert_mjpeg_to_mp4(os.path.join(full_path, mjpeg))

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    run()
