import os
import time
import subprocess
from datetime import datetime
from threading import Thread
from config.recorder_config import SEGMENT_DURATION_SEC, TEMP_DIR, FRAMERATE
from state_manager import get_event

def start_raw_capture(camera_id, cam_label, output_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename_pattern = f"{cam_label}_{timestamp}_%05d.raw"
    filepath = os.path.join(output_dir, filename_pattern)

    print(f"📸 [{cam_label}] Capture RAW segmentée avec rpicam-raw")
    cmd = [
        "rpicam-raw",
        "--camera", str(camera_id),
        "-t", str(SEGMENT_DURATION_SEC * 1000),
        "--segment", "1",
        "--framerate", str(FRAMERATE),
        "-o", filepath
    ]

    subprocess.run(cmd)
    print(f"🛑 [{cam_label}] Fin capture rpicam-raw")

def run():
    print("📷 Picture Recorder (RAW) prêt, en attente de déclenchement...")
    event = get_event()

    while True:
        event.wait()
        session = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        session_dir = TEMP_DIR
        os.makedirs(session_dir, exist_ok=True)

        with open(os.path.join(TEMP_DIR, ".current_session"), "w") as f:
            f.write(session)

        print(f"🚀 Début session : {session}")

        t0 = Thread(target=start_raw_capture, args=(0, "CAM-RIGHT", session_dir))
        t1 = Thread(target=start_raw_capture, args=(1, "CAM-LEFT", session_dir))

        t0.start()
        t1.start()
        t0.join()
        t1.join()

        print("✅ Fin de session, en attente du prochain déclenchement...")
