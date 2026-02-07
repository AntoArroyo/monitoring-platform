from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import Host, Metric
from app.schemas import IngestPayload

app = FastAPI(title="Monitoring Platform")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics/latest")
def get_latest_metrics(db: Session = Depends(get_db)):
    rows = (
        db.query(Metric)
        .order_by(Metric.timestamp.desc())
        .limit(50)
        .all()
    )
    return rows


@app.post("/api/v1/ingest")
def ingest_metrics(payload: IngestPayload, db: Session = Depends(get_db)):
    host = db.query(Host).filter_by(agent_id=payload.agent_id).first()

    if not host:
        host = Host(
            agent_id=payload.agent_id,
            hostname=payload.agent_id,
            last_seen=datetime.now(),
        )
        db.add(host)
        db.commit()
        db.refresh(host)

    host.last_seen = datetime.now()

    metrics = {
        "cpu_percent": payload.system.cpu_percent,
        "ram_percent": payload.system.ram_percent,
        "disk_percent": payload.system.disk_percent,
        "cpu_temp_c": payload.raspberry_pi.cpu_temp_c if payload.raspberry_pi else None,
    }

    for name, value in metrics.items():
        if value is None:
            continue
        db.add(
            Metric(
                host_id=host.id,
                metric_name=name,
                value=value,
                timestamp=payload.timestamp,
            )
        )

    db.commit()

    return {"status": "ingested"}
