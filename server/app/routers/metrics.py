from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from app.core.deps import get_db
from app.db.models import Metric

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/latest")
def get_latest_metrics(db: Session = Depends(get_db)):
    rows = (
        db.query(Metric)
        .order_by(Metric.timestamp.desc())
        .limit(50)
        .all()
    )
    return rows


@router.get("/timeseries")
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


@router.get("/latest-per-host")
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
