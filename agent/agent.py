import time
import socket
from datetime import datetime

import psutil
import requests


# Backend metrics ingestion endpoint.
BACKEND_URL = "http://127.0.0.1:8000/metrics"
# Human-readable identifier for this agent instance.
AGENT_ID = "austin-macbook"


def collect_metrics():
    """Collect one machine-metrics snapshot with metadata."""

    # `interval=1` waits one second to produce a stable CPU sample.
    cpu_percent = psutil.cpu_percent(interval=1)
    # `virtual_memory` provides both percentage and byte-level memory stats.
    memory = psutil.virtual_memory()

    # Include identity and timing fields so the backend can attribute data.
    return {
        "agent_id": AGENT_ID,
        # Hostname helps distinguish multiple machines using one backend.
        "hostname": socket.gethostname(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_used": memory.used,
        "memory_total": memory.total,
        # ISO format is easy to parse across services and languages.
        "timestamp": datetime.now().isoformat(),
    }


def send_metrics(metrics):
    """Send one metric payload to the backend via HTTP POST."""

    # Timeout prevents the loop from hanging if the backend is unavailable.
    response = requests.post(BACKEND_URL, json=metrics, timeout=5)

    if response.status_code == 200:
        # Success output confirms connectivity and accepted payload shape.
        print("Metric sent successfully:")
        print(response.json())
    else:
        # Failure output helps diagnose network or validation issues quickly.
        print("Failed to send metric:")
        print(response.status_code)
        print(response.text)


def main():
    """Run the continuous collection-and-send loop."""

    # Startup log confirms the agent process launched correctly.
    print("PulseGrid agent started...")

    while True:
        # Gather a fresh snapshot, send it, then pause before next cycle.
        metrics = collect_metrics()
        send_metrics(metrics)
        time.sleep(5)


if __name__ == "__main__":
    main()