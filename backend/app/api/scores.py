from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db

router = APIRouter(prefix="/api/scores", tags=["scores"])


class SubScores(BaseModel):
    residual: float
    incentive: float
    discount: float
    inventory: float
    market_weakness: float
    evidence: float


class LeaseSnapshot(BaseModel):
    residual_percent: Optional[float]
    money_factor: Optional[float]
    lease_cash: Optional[float]
    total_incentives: Optional[float]
    term: Optional[int]
    mileage: Optional[int]


class ScoreResponse(BaseModel):
    vehicle_id: int
    make: str
    model: str
    trim: Optional[str]
    year: int
    category: Optional[str]
    hackability_score: float
    confidence_score: float
    sub_scores: SubScores
    explanation: Optional[str]
    score_month: int
    score_year: int
    last_updated: datetime
    lease_snapshot: Optional[LeaseSnapshot] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ScoreResponse])
def list_scores(
    category: Optional[str] = Query(None, description="Filter by category: EV, SUV, Luxury, Truck"),
    min_score: float = Query(0.0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    from app.models.vehicle import Vehicle
    from app.models.score import HackabilityScore
    from app.models.lease_program import LeaseProgram

    # Join scores with vehicles, get latest score per vehicle
    query = (
        db.query(HackabilityScore, Vehicle)
        .join(Vehicle, HackabilityScore.vehicle_id == Vehicle.id)
        .filter(HackabilityScore.hackability_score >= min_score)
    )
    if category:
        query = query.filter(Vehicle.category.ilike(f"%{category}%"))

    rows = (
        query.order_by(HackabilityScore.hackability_score.desc())
        .limit(limit * 3)  # over-fetch to deduplicate per vehicle
        .all()
    )

    # Keep only the highest-scoring row per vehicle
    seen = set()
    results = []
    for score, vehicle in rows:
        if vehicle.id in seen:
            continue
        seen.add(vehicle.id)

        lp = (
            db.query(LeaseProgram)
            .filter(LeaseProgram.vehicle_id == vehicle.id)
            .order_by(LeaseProgram.program_year.desc(), LeaseProgram.program_month.desc())
            .first()
        )
        lease_snap = None
        if lp:
            total = (lp.lease_cash or 0) + (lp.loyalty_cash or 0) + (lp.conquest_cash or 0)
            lease_snap = LeaseSnapshot(
                residual_percent=lp.residual_percent,
                money_factor=lp.money_factor,
                lease_cash=lp.lease_cash,
                total_incentives=total,
                term=lp.term,
                mileage=lp.mileage,
            )

        results.append(
            ScoreResponse(
                vehicle_id=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                trim=vehicle.trim,
                year=vehicle.year,
                category=vehicle.category,
                hackability_score=score.hackability_score,
                confidence_score=score.confidence_score,
                sub_scores=SubScores(
                    residual=score.residual_score or 0,
                    incentive=score.incentive_score or 0,
                    discount=score.discount_score or 0,
                    inventory=score.inventory_score or 0,
                    market_weakness=score.market_weakness_score or 0,
                    evidence=score.evidence_score or 0,
                ),
                explanation=score.explanation,
                score_month=score.score_month,
                score_year=score.score_year,
                last_updated=score.last_updated,
                lease_snapshot=lease_snap,
            )
        )
        if len(results) >= limit:
            break

    return results
