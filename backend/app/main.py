from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import create_tables, SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    _seed_on_startup()
    _start_scheduler()
    yield


def _seed_on_startup():
    from app.seeds.historical_winners import run_seed
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


def _start_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from app.api.workflow import _run_workflow
        from app.models.score import WorkflowRun
        from datetime import datetime

        scheduler = BackgroundScheduler()

        def _scheduled_job():
            db = SessionLocal()
            try:
                run = WorkflowRun(started_at=datetime.utcnow(), status="running", steps_completed=0)
                db.add(run)
                db.commit()
                db.refresh(run)
                run_id = run.id
            finally:
                db.close()
            _run_workflow(run_id)

        scheduler.add_job(_scheduled_job, "cron", hour=2, minute=0)
        scheduler.start()
        log.info("APScheduler started — workflow fires nightly at 02:00 UTC")
    except Exception as exc:
        log.warning("APScheduler not available: %s", exc)


app = FastAPI(
    title="Lease Deal Discovery",
    description="Identifies and ranks the most hackable lease opportunities in the US.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.vehicles import router as vehicles_router  # noqa: E402
from app.api.scores import router as scores_router  # noqa: E402
from app.api.workflow import router as workflow_router  # noqa: E402

app.include_router(vehicles_router)
app.include_router(scores_router)
app.include_router(workflow_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve the frontend dashboard from /
try:
    import os
    _frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    _frontend_dir = os.path.abspath(_frontend_dir)
    _vendor_dir = os.path.join(_frontend_dir, "vendor")
    if os.path.isdir(_frontend_dir):
        if os.path.isdir(_vendor_dir):
            app.mount("/vendor", StaticFiles(directory=_vendor_dir), name="vendor")
        app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

        @app.get("/", include_in_schema=False)
        def serve_dashboard():
            return FileResponse(os.path.join(_frontend_dir, "index.html"))
except Exception as exc:
    log.warning("Could not mount frontend: %s", exc)
