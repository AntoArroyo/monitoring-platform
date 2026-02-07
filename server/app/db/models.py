from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String, unique=True, index=True)
    hostname = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)

    metrics = relationship("Metric", back_populates="host")


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey("hosts.id"))
    metric_name = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    host = relationship("Host", back_populates="metrics")
