import os
import time
from datetime import datetime
from threading import Thread
from config.recorder_config import VIDEO_WIDTH, VIDEO_HEIGHT, FRAMERATE, SEGMENT_DURATION_SEC, BASE_OUTPUT_DIR, TEMP_DIR
from state_manager import is_recording, get_event

def start_segmented_recording(camera_id, cam_label, output_dir):
    import subprocess
    seg_num = 0
    while is_recording():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{cam_label}_{timestamp}_seg{seg_num:02d}.mjpeg"
        filepath = os.path.join(output_dir, filename)

        print(f"📹 [{cam_label}] Début segment {seg_num}")
        cmd = [
            "rpicam-vid",
            "--camera", str(camera_id),
            "-t", str(SEGMENT_DURATION_SEC * 1000),
            "--codec", "mjpeg",
            "--width", str(VIDEO_WIDTH),
            "--height", str(VIDEO_HEIGHT),
            "--framerate", str(FRAMERATE),
            "-o", filepath
        ]

        subprocess.run(cmd)
        seg_num += 1

    print(f"🛑 [{cam_label}] Fin d’enregistrement")

def run():
    print("🎥 Recorder prêt, en attente de déclenchement...")
    event = get_event()

    while True:
        event.wait()
        session = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        session_dir = TEMP_DIR
        os.makedirs(session_dir, exist_ok=True)

        # 🔖 Enregistre le nom de la session dans un fichier pour le segment mover
        with open(os.path.join(TEMP_DIR, ".current_session"), "w") as f:
            f.write(session)

        print(f"🚀 Début session : {session}")

        t0 = Thread(target=start_segmented_recording, args=(0, "CAM-RIGHT", session_dir))
        t1 = Thread(target=start_segmented_recording, args=(1, "CAM-LEFT", session_dir))
        
        t0.start()
        t1.start()
        t0.join()
        t1.join()

        print("✅ Fin de session, en attente du prochain déclenchement...")
