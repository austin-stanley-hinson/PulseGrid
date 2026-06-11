from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

class Metric(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    agent_id: str
    hostname: str

    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int 
    
    timestamp: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)