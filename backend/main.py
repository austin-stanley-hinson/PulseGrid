from datetime import datetime

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Metric


app = FastAPI(title="PulseGrid Backend")


class MetricPayload(BaseModel):
    """
    Expected JSON structure for metrics sent by an agent.
    FastAPI uses this model to validate incoming request bodies.
    """

    agent_id: str
    hostname: str
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    timestamp: datetime


@app.on_event("startup")
def on_startup():
    """
    Runs when the backend starts.

    Creates database tables if they do not already exist.
    """
    create_db_and_tables()


@app.get("/")
def root():
    """
    Basic health check route to confirm the backend is running.
    """

    return {
        "message": "PulseGrid backend is running"
    }


@app.post("/metrics")
def receive_metrics(
    payload: MetricPayload,
    session: Session = Depends(get_session)
):
    """
    Receive metric data from an agent, validate it, and store it in PostgreSQL.
    """

    metric = Metric(
        agent_id=payload.agent_id,
        hostname=payload.hostname,
        cpu_percent=payload.cpu_percent,
        memory_percent=payload.memory_percent,
        memory_used=payload.memory_used,
        memory_total=payload.memory_total,
        timestamp=payload.timestamp,
    )

    session.add(metric)
    session.commit()
    session.refresh(metric)

    print("Stored metric in PostgreSQL:")
    print(metric)

    return {
        "status": "stored",
        "metric_id": metric.id,
        "agent_id": metric.agent_id,
        "hostname": metric.hostname,
        "cpu_percent": metric.cpu_percent,
        "memory_percent": metric.memory_percent,
    }


@app.get("/metrics")
def get_metrics(session: Session = Depends(get_session)):
    """
    Return recently stored metrics from PostgreSQL.
    """

    statement = select(Metric).order_by(Metric.id.desc()).limit(20)
    metrics = session.exec(statement).all()

    return {
        "count": len(metrics),
        "metrics": metrics,
    }