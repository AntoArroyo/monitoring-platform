from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import Host, Metric
from app.schemas import IngestPayload

app = FastAPI(title="Monitoring Platform")

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

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



@app.get("/metrics/timeseries")
def get_timeseries(
    metric_name: str,
    minutes: int = 60,
    db: Session = Depends(get_db),
):
    since = datetime.now() - timedelta(minutes=minutes)

    rows = (
        db.query(Metric)
        .filter(Metric.metric_name == metric_name)
        .filter(Metric.timestamp >= since)
        .order_by(Metric.timestamp.asc())
        .all()
    )

    return [
        {
            "timestamp": m.timestamp.isoformat(),
            "value": m.value,
        }
        for m in rows
    ]
    
@app.get("/metrics/latest-per-host")
def latest_per_host(db: Session = Depends(get_db)):
    subq = (
        db.query(
            Metric.host_id,
            Metric.metric_name,
            func.max(Metric.timestamp).label("max_ts"),
        )
        .group_by(Metric.host_id, Metric.metric_name)
        .subquery()
    )

    rows = (
        db.query(Metric)
        .join(
            subq,
            (Metric.host_id == subq.c.host_id)
            & (Metric.metric_name == subq.c.metric_name)
            & (Metric.timestamp == subq.c.max_ts),
        )
        .all()
    )

    return rows