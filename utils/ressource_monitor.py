import psutil
import os
import time
from datetime import datetime
from state_manager import is_recording

LOG_PATH = "/mnt/ssd/resource_usage.csv"
DETAIL_LOG_PATH = "/mnt/ssd/resource_details.csv"
INTERVAL = 5  # secondes

def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read().strip()) / 1000, 1)
    except:
        return None

def get_disk_usage(path):
    usage = psutil.disk_usage(path)
    return usage.percent, round(usage.free / (1024**3), 2)

def write_headers():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            f.write("timestamp,recording,cpu_percent,mem_percent,temp_c,tmp_usage_pct,tmp_free_gb,ssd_usage_pct,ssd_free_gb\n")
    if not os.path.exists(DETAIL_LOG_PATH):
        with open(DETAIL_LOG_PATH, "w") as f:
            f.write("timestamp,pid,name,cpu_percent,mem_percent\n")

def log_top_processes(timestamp):
    top_cpu = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                     key=lambda p: p.info['cpu_percent'], reverse=True)[:10]
    top_mem = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                     key=lambda p: p.info['memory_percent'], reverse=True)[:10]
    seen = set()
    with open(DETAIL_LOG_PATH, "a") as f:
        for proc in top_cpu + top_mem:
            info = proc.info
            pid = info['pid']
            if pid in seen:
                continue
            seen.add(pid)
            f.write(f"{timestamp},{pid},{info['name']},{info['cpu_percent']},{info['memory_percent']}\n")

def monitor(log_path="/mnt/ssd/resource_usage.csv", interval=5):
    print("🩺 Resource monitor started")
    write_headers()

    while True:
        timestamp = datetime.now().isoformat()
        rec_state = "ON" if is_recording() else "OFF"
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        temp = get_temp()
        tmp_pct, tmp_free = get_disk_usage("/tmp")
        ssd_pct, ssd_free = get_disk_usage("/mnt/ssd")

        with open(log_path, "a") as f:
            f.write(f"{timestamp},{rec_state},{cpu},{mem},{temp},{tmp_pct},{tmp_free},{ssd_pct},{ssd_free}\n")

        log_top_processes(timestamp)
        time.sleep(interval)

if __name__ == "__main__":
    monitor()
