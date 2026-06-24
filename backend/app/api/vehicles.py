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

    vehicles = db.query(Vehicle).order_by(Vehicle.year.desc(), Vehicle.make).all()
    results = []
    for v in vehicles:
        score = (
            db.query(HackabilityScore)
            .filter(HackabilityScore.vehicle_id == v.id)
            .order_by(HackabilityScore.score_year.desc(), HackabilityScore.score_month.desc())
            .first()
        )
        results.append(
            VehicleResponse(
                id=v.id,
                make=v.make,
                model=v.model,
                trim=v.trim,
                year=v.year,
                category=v.category,
                latest_score=score.hackability_score if score else None,
            )
        )
    return results
