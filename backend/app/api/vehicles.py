from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


class VehicleResponse(BaseModel):
    id: int
    make: str
    model: str
    trim: Optional[str]
    year: int
    category: Optional[str]
    latest_score: Optional[float] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[VehicleResponse])
def list_vehicles(db: Session = Depends(get_db)):
    from app.models.vehicle import Vehicle
    from app.models.score import HackabilityScore
    from sqlalchemy import func

    # Latest score per vehicle via subquery — avoids N+1
    latest_score_sq = (
        db.query(
            HackabilityScore.vehicle_id,
            func.max(
                HackabilityScore.score_year * 100 + HackabilityScore.score_month
            ).label("ym"),
        )
        .group_by(HackabilityScore.vehicle_id)
        .subquery()
    )
    rows = (
        db.query(Vehicle, HackabilityScore)
        .outerjoin(
            latest_score_sq,
            latest_score_sq.c.vehicle_id == Vehicle.id,
        )
        .outerjoin(
            HackabilityScore,
            (HackabilityScore.vehicle_id == Vehicle.id)
            & (
                HackabilityScore.score_year * 100 + HackabilityScore.score_month
                == latest_score_sq.c.ym
            ),
        )
        .order_by(Vehicle.year.desc(), Vehicle.make)
        .all()
    )
    return [
        VehicleResponse(
            id=v.id,
            make=v.make,
            model=v.model,
            trim=v.trim,
            year=v.year,
            category=v.category,
            latest_score=s.hackability_score if s else None,
        )
        for v, s in rows
    ]
