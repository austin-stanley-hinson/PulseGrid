from datetime import datetime, timedelta

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Metric, Agent, Alert

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="PulseGrid Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CPU_WARNING_THRESHOLD = 75.0
CPU_CRITICAL_THRESHOLD = 90.0

MEMORY_WARNING_THRESHOLD = 75.0
MEMORY_CRITICAL_THRESHOLD = 90.0

OFFLINE_THRESHOLD_SECONDS = 30

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
    Receive metric data from an agent, validate it, store it,
    update agent health state, and create alerts if needed.
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

    agent = upsert_agent(payload, session)
    alerts = create_threshold_alerts(payload, session)

    session.commit()
    session.refresh(metric)
    session.refresh(agent)

    return {
        "status": "stored",
        "metric_id": metric.id,
        "agent_id": metric.agent_id,
        "hostname": metric.hostname,
        "cpu_percent": metric.cpu_percent,
        "memory_percent": metric.memory_percent,
        "agent_status": agent.status,
        "alerts_created": len(alerts),
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

def upsert_agent(payload: MetricPayload, session: Session) -> Agent:
    """
    Create or update an agent row whenever a metric is received.

    Each metric acts like a heartbeat.
    """

    statement = select(Agent).where(Agent.agent_id == payload.agent_id)
    agent = session.exec(statement).first()

    if agent is None:
        agent = Agent(
            agent_id=payload.agent_id,
            hostname=payload.hostname,
            status="online",
            last_seen_at=payload.timestamp,
        )
        session.add(agent)
    else:
        agent.hostname = payload.hostname
        agent.status = "online"
        agent.last_seen_at = payload.timestamp

    return agent


def create_threshold_alerts(payload: MetricPayload, session: Session) -> list[Alert]:
    """
    Create warning/critical alerts when CPU or memory crosses thresholds.
    """

    alerts = []

    if payload.cpu_percent >= CPU_CRITICAL_THRESHOLD:
        alerts.append(
            Alert(
                agent_id=payload.agent_id,
                hostname=payload.hostname,
                alert_type="cpu",
                severity="critical",
                message=f"CPU usage is critically high at {payload.cpu_percent:.1f}%",
                value=payload.cpu_percent,
                threshold=CPU_CRITICAL_THRESHOLD,
            )
        )
    elif payload.cpu_percent >= CPU_WARNING_THRESHOLD:
        alerts.append(
            Alert(
                agent_id=payload.agent_id,
                hostname=payload.hostname,
                alert_type="cpu",
                severity="warning",
                message=f"CPU usage is elevated at {payload.cpu_percent:.1f}%",
                value=payload.cpu_percent,
                threshold=CPU_WARNING_THRESHOLD,
            )
        )

    if payload.memory_percent >= MEMORY_CRITICAL_THRESHOLD:
        alerts.append(
            Alert(
                agent_id=payload.agent_id,
                hostname=payload.hostname,
                alert_type="memory",
                severity="critical",
                message=f"Memory usage is critically high at {payload.memory_percent:.1f}%",
                value=payload.memory_percent,
                threshold=MEMORY_CRITICAL_THRESHOLD,
            )
        )
    elif payload.memory_percent >= MEMORY_WARNING_THRESHOLD:
        alerts.append(
            Alert(
                agent_id=payload.agent_id,
                hostname=payload.hostname,
                alert_type="memory",
                severity="warning",
                message=f"Memory usage is elevated at {payload.memory_percent:.1f}%",
                value=payload.memory_percent,
                threshold=MEMORY_WARNING_THRESHOLD,
            )
        )

    for alert in alerts:
        session.add(alert)

    return alerts


@app.get("/agents")
def get_agents(session: Session = Depends(get_session)):
    """
    Return all agents with computed online/offline status.

    An agent is offline if it has not sent a metric recently.
    """

    statement = select(Agent).order_by(Agent.agent_id)
    agents = session.exec(statement).all()

    now = datetime.utcnow()
    results = []

    for agent in agents:
        seconds_since_seen = (now - agent.last_seen_at).total_seconds()

        computed_status = (
            "offline"
            if seconds_since_seen > OFFLINE_THRESHOLD_SECONDS
            else agent.status
        )

        results.append(
            {
                "id": agent.id,
                "agent_id": agent.agent_id,
                "hostname": agent.hostname,
                "status": computed_status,
                "registered_at": agent.registered_at,
                "last_seen_at": agent.last_seen_at,
                "seconds_since_seen": round(seconds_since_seen, 1),
            }
        )

    return {
        "count": len(results),
        "agents": results,
    }

@app.get("/alerts")
def get_alerts(session: Session = Depends(get_session)):
    """
    Return recent alerts.
    """

    statement = select(Alert).order_by(Alert.id.desc()).limit(50)
    alerts = session.exec(statement).all()

    return {
        "count": len(alerts),
        "alerts": alerts,
    }