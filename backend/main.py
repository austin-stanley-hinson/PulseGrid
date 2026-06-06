import time 
import socket 
from datetime import datetime
 
import psutil 
import requests

BACKEND_URL - "https://127.0.0.1:8000/metrics"
AGENT_ID = "austin-macbook"

def collect_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    return {
        "agent_id": AGENT_ID,
        "hostname": socket.gethostname(),
        "cpu_percent": cpu_percent,
        "memory_used": memory.used,
        "memory_total": memory.total, 
        "time_stamp": datetime.now().isoformat(),
    }

def send_metrics(metrics):
    response = requests.post(BACKEND_URL, json=metrics, timeout=5)

    if response.status_code == 200:
        print("Metric sent successfully: ")
        print(response.json())
    else:
        print("Failed to send metric: ")
        print(response.status_code)
        print(response.text)

def main():
    print("PulseGrid agent check started...")

    while True:
        metrics = collect_metrics()
        send_metrics(metrics)
        time.sleep(5)

if __name__ == "__main__":
    main()