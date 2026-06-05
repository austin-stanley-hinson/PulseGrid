import time 
import psutil 

def collect_metrics():
    # `interval=1` blocks for one second to compute a stable CPU average.
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    # Return a flat, JSON-serializable payload for easy logging/transport.
    return {
        "cpu_percent" : cpu_percent,
        "memory_percent": memory.percent,
        "memory_used": memory.used,
        "memory_total":memory.total,
    }

def main():
    # Simple stdout heartbeat so operators know the process is running.
    print("PulseGrid agent started...")
    while True:
        # Collect and emit one metrics snapshot every loop iteration.
        metrics = collect_metrics()
        print(metrics)
        # Sleep five seconds between emissions to avoid noisy output.
        time.sleep(5)

if __name__ == "__main__":
    main()