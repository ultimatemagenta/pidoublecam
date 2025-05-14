import os
import time
import subprocess
from threading import Thread
import rawpy
import imageio
from state_manager import is_recording, get_event
from config.recorder_config import BASE_OUTPUT_DIR

CONVERT_EXT = ".mjpeg"
DNG_EXT = ".dng"
PNG_EXT = ".png"
OUTPUT_EXT = ".mp4"
CHECK_INTERVAL = 60  # toutes les 60 sec
IDLE_REQUIRED_SEC = 5 * 60  # 15 minutes

def convert_mjpeg_to_mp4(input_path, output_path):
    try:
        print(f"🎬 Conversion MJPEG : {input_path} ➜ {output_path}")
        proc = subprocess.Popen([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_path,
            "-c:v", "libx264", "-preset", "ultrafast", output_path
        ])
        while proc.poll() is None:
            if is_recording():
                print(f"⛔️ Interruption conversion MJPEG {input_path}")
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
            print(f"❌ Erreur MJPEG : {input_path}")
    except Exception as e:
        print(f"❌ Exception MJPEG : {e}")

def convert_dng_to_png(dng_path):
    try:
        png_path = os.path.splitext(dng_path)[0] + PNG_EXT
        if os.path.exists(png_path):
            return  # déjà converti
        print(f"🖼️ Conversion DNG : {dng_path} ➜ {png_path}")
        with rawpy.imread(dng_path) as raw:
            rgb = raw.postprocess()
            imageio.imwrite(png_path, rgb)
        os.remove(dng_path)
    except Exception as e:
        print(f"❌ Erreur DNG : {dng_path} - {e}")

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
            print(f"⏳ Inactivité : {idle_timer // 60} min")
            time.sleep(CHECK_INTERVAL)
            continue

        # Parcours des fichiers de toutes les sessions
        for root, _, files in os.walk(BASE_OUTPUT_DIR):
            files.sort()

            for f in files:
                input_path = os.path.join(root, f)
                if f.endswith(CONVERT_EXT):
                    output_path = os.path.splitext(input_path)[0] + OUTPUT_EXT
                    if not os.path.exists(output_path):
                        convert_mjpeg_to_mp4(input_path, output_path)

                elif f.endswith(DNG_EXT):
                    convert_dng_to_png(input_path)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
