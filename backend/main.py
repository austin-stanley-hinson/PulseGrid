from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel


# FastAPI application setup for the PulseGrid backend service.
app = FastAPI(title="PulseGrid Backend")


class MetricPayload(BaseModel):
    """Schema for metrics sent by each PulseGrid agent."""

    # Stable identifier for the agent process or machine.
    agent_id: str
    # Hostname of the machine where the agent is running.
    hostname: str
    # CPU usage percentage sampled by the agent.
    cpu_percent: float
    # Memory usage percentage sampled by the agent.
    memory_percent: float
    # Absolute memory usage in bytes.
    memory_used: int
    # Total system memory in bytes.
    memory_total: int
    # ISO timestamp of when the metric snapshot was created.
    timestamp: datetime


# In-memory store used for local development and simple demos.
# Note: data resets whenever the backend process restarts.
received_metrics = []


@app.get("/")
def root():
    """Health check route that confirms the backend is running."""

    return {
        "message": "PulseGrid backend is running"
    }


@app.post("/metrics")
def receive_metrics(payload: MetricPayload):
    """Ingest a metric payload from an agent and store it in memory."""

    # Keep each payload so the dashboard and API can show recent activity.
    received_metrics.append(payload)

    # Console output makes it easy to verify ingestion during development.
    print("Received metric:")
    print(payload)

    return {
        "status": "received",
        "agent_id": payload.agent_id,
        "hostname": payload.hostname,
        "cpu_percent": payload.cpu_percent,
        "memory_percent": payload.memory_percent,
    }


@app.get("/metrics")
def get_metrics():
    """Return all received metrics and a total count."""

    return {
        "count": len(received_metrics),
        "metrics": received_metrics
    }