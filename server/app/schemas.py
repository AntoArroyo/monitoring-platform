from pydantic import BaseModel
from datetime import datetime
from typing import Dict


class SystemMetrics(BaseModel):
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    uptime_seconds: int


class RaspberryPiMetrics(BaseModel):
    cpu_temp_c: float | None = None


class IngestPayload(BaseModel):
    agent_id: str
    timestamp: datetime
    system: SystemMetrics
    raspberry_pi: RaspberryPiMetrics | None = None
