from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base

from app.routers import health, dashboard, ingest, metrics

app = FastAPI(title="Monitoring Platform")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(ingest.router)
app.include_router(metrics.router)
