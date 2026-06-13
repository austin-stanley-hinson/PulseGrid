from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel


class Metric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    agent_id: str
    hostname: str
    cpu_percent: float
    memory_percent: float

    memory_used: int = Field(sa_column=Column(BigInteger))
    memory_total: int = Field(sa_column=Column(BigInteger))

    timestamp: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Agent(SQLModel, table=True):
    """
    Tracks one monitored agent/machine.

    This table represents the latest known state of each agent.
    It is used for service health and offline detection.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    agent_id: str = Field(index=True, unique=True)
    hostname: str

    status: str = Field(default="online")

    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)


class Alert(SQLModel, table=True):
    """
    Stores alert events created when metrics cross unhealthy thresholds.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    agent_id: str = Field(index=True)
    hostname: str

    alert_type: str
    severity: str
    message: str

    value: float
    threshold: float

    created_at: datetime = Field(default_factory=datetime.utcnow)