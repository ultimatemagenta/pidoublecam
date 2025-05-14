import os
import time
import subprocess
from threading import Thread
from state_manager import is_recording, get_event
from config.recorder_config import BASE_OUTPUT_DIR

CONVERT_EXT = ".mjpeg"
OUTPUT_EXT = ".mp4"
CHECK_INTERVAL = 60  # toutes les 60 sec
IDLE_REQUIRED_SEC = 15 * 60  # 15 minutes

def convert_file(input_path, output_path):
    try:
        print(f"🎬 Conversion : {input_path} ➜ {output_path}")
        proc = subprocess.Popen([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_path,
            "-c:v", "libx264", "-preset", "ultrafast", output_path
        ])
        while proc.poll() is None:
            if is_recording():
                print(f"⛔️ Interruption de la conversion de {input_path}")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                if os.path.exists(output_path):
                    os.remove(output_path)
                return
            time.sleep(2)
        if proc.returncode == 0:
            os.remove(input_path)
            print(f"✅ Terminé : {output_path}")
        else:
            print(f"❌ Erreur : {input_path}")
    except Exception as e:
        print(f"❌ Exception pendant la conversion : {e}")

def run():
    print("🧼 Postprocessor en attente de 15 min d’inactivité...")
    idle_timer = 0

    while True:
        if is_recording():
            idle_timer = 0
            time.sleep(CHECK_INTERVAL)
            continue

        idle_timer += CHECK_INTERVAL
        if idle_timer < IDLE_REQUIRED_SEC:
            print(f"⏳ En attente... {idle_timer // 60} min d’inactivité")
            time.sleep(CHECK_INTERVAL)
            continue

        # On scanne tous les dossiers de session
        for root, _, files in os.walk(BASE_OUTPUT_DIR):
            for f in sorted(files):
                if f.endswith(CONVERT_EXT):
                    input_path = os.path.join(root, f)
                    output_path = os.path.splitext(input_path)[0] + OUTPUT_EXT
                    if not os.path.exists(output_path):
                        convert_file(input_path, output_path)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
