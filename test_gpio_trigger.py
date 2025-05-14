import os
import time
from datetime import datetime
from threading import Thread
import RPi.GPIO as GPIO
from state_manager import enable_recording, disable_recording, is_recording
import utils.ressource_monitor as monitor

# GPIO config
TEST_PIN = 22  # GPIO BCM
GPIO.setmode(GPIO.BCM)
GPIO.setup(TEST_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Dossier et pattern de log
LOG_DIR = "/mnt/ssd"
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_path():
    today = datetime.now().strftime("%Y%m%d")
    existing = [f for f in os.listdir(LOG_DIR) if f.startswith(f"test_{today}")]
    index = len(existing) + 1
    return os.path.join(LOG_DIR, f"test_{today}_#{index}.csv")

def monitor_thread_func(log_path):
    monitor.monitor(log_path=log_path)

def simulate_recording_loop():
    while GPIO.input(TEST_PIN) == GPIO.HIGH:
        print("🟢 Test GPIO HIGH - Enregistrement ON")
        enable_recording()
        time.sleep(5 * 60)

        print("🟡 Pause d’enregistrement")
        disable_recording()
        time.sleep(5 * 60)

    print("🔴 Test terminé, GPIO LOW")
    disable_recording()

def run_test_mode():
    print("⌛ En attente de GPIO test HIGH sur pin 22...")
    while True:
        if GPIO.input(TEST_PIN) == GPIO.HIGH:
            print("🚀 Début du test automatique")
            log_path = get_log_path()

            # Démarrage du monitor
            mon_thread = Thread(target=monitor_thread_func, args=(log_path,), daemon=True)
            mon_thread.start()

            # Démarrage du simulateur ON/OFF
            simulate_recording_loop()
            break

        time.sleep(0.5)

if __name__ == "__main__":
    try:
        run_test_mode()
    except KeyboardInterrupt:
        GPIO.cleanup()
