from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal

router = APIRouter(prefix="/api/workflow", tags=["workflow"])
log = logging.getLogger(__name__)


class WorkflowStatusResponse(BaseModel):
    id: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    steps_completed: int
    error_message: Optional[str]

    class Config:
        from_attributes = True


@router.post("/run", status_code=202)
def trigger_workflow(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from app.models.score import WorkflowRun

    running = db.query(WorkflowRun).filter(WorkflowRun.status == "running").first()
    if running:
        raise HTTPException(status_code=409, detail="Workflow already running")

    run = WorkflowRun(started_at=datetime.utcnow(), status="running", steps_completed=0)
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(_run_workflow, run.id)
    return {"run_id": run.id, "status": "started"}


@router.get("/status", response_model=Optional[WorkflowStatusResponse])
def workflow_status(db: Session = Depends(get_db)):
    from app.models.score import WorkflowRun

    run = db.query(WorkflowRun).order_by(WorkflowRun.started_at.desc()).first()
    return run


def _run_workflow(run_id: int) -> None:
    db = SessionLocal()
    try:
        from app.models.score import WorkflowRun
        from app.models.vehicle import Vehicle
        from app.agents.vehicle_discovery import run_discovery
        from app.agents.lease_program_collector import run_collection
        from app.agents.inventory_agent import run_inventory
        from app.agents.deal_evidence_agent import run_deal_evidence
        from app.agents.hackability_ranking import compute_hackability_score

        run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()

        def _step(n: int):
            run.steps_completed = n
            db.commit()

        log.info("Workflow run %d: Step 1 — Vehicle Discovery", run_id)
        run_discovery(db)
        _step(1)

        log.info("Workflow run %d: Step 2 — Lease Program Collection", run_id)
        run_collection(db)
        _step(2)

        log.info("Workflow run %d: Step 3 — Inventory Intelligence", run_id)
        run_inventory(db)
        _step(3)

        log.info("Workflow run %d: Step 4 — Deal Evidence", run_id)
        run_deal_evidence(db)
        _step(4)

        log.info("Workflow run %d: Step 5 — Hackability Ranking", run_id)
        vehicles = db.query(Vehicle).all()
        for v in vehicles:
            try:
                compute_hackability_score(v.id, db)
            except Exception as exc:
                log.warning("Scoring failed for vehicle %d: %s", v.id, exc)
        _step(5)

        run.status = "completed"
        run.completed_at = datetime.utcnow()
        db.commit()
        log.info("Workflow run %d complete.", run_id)

    except Exception as exc:
        log.error("Workflow run %d failed: %s", run_id, exc, exc_info=True)
        from app.models.score import WorkflowRun
        run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
        if run:
            run.status = "failed"
            run.error_message = str(exc)
            run.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()
