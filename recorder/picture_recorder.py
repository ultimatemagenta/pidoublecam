# recording/picture_recorder.py

import os
import time
import subprocess
from datetime import datetime
from threading import Thread
from config.recorder_config import VIDEO_WIDTH, VIDEO_HEIGHT, FRAMERATE, TEMP_DIR, SEGMENT_DURATION_SEC
from state_manager import is_recording, get_event

def capture_raw_image(camera_id, cam_label, frame_num, output_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{cam_label}_{timestamp}_frame{frame_num:04d}.dng"
    filepath = os.path.join(output_dir, filename)

    cmd = [
        "libcamera-still",
        "--camera", str(camera_id),
        "--width", str(VIDEO_WIDTH),
        "--height", str(VIDEO_HEIGHT),
        "--raw",
        "--nopreview",
        "--timeout", "1",
        "-o", filepath
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_picture_capture(camera_id, cam_label, output_dir):
    print(f"📸 [{cam_label}] Capture d’images RAW démarrée")
    frame_delay = 1.0 / FRAMERATE
    frame_num = 0
    start_time = time.time()

    while time.time() - start_time < SEGMENT_DURATION_SEC:
        capture_raw_image(camera_id, cam_label, frame_num, output_dir)
        frame_num += 1
        time.sleep(frame_delay)

    print(f"🛑 [{cam_label}] Fin capture RAW")

def run():
    print("📷 Picture Recorder prêt, en attente de déclenchement...")
    event = get_event()

    while True:
        event.wait()
        session = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        session_dir = TEMP_DIR
        os.makedirs(session_dir, exist_ok=True)

        with open(os.path.join(TEMP_DIR, ".current_session"), "w") as f:
            f.write(session)

        print(f"🚀 Début session : {session}")

        t0 = Thread(target=start_picture_capture, args=(0, "CAM-RIGHT", session_dir))
        t1 = Thread(target=start_picture_capture, args=(1, "CAM-LEFT", session_dir))

        t0.start()
        t1.start()
        t0.join()
        t1.join()

        print("✅ Fin de session, en attente du prochain déclenchement...")
