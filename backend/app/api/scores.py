from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.agents.lease_math import calculate_monthly_payment

router = APIRouter(prefix="/api/scores", tags=["scores"])

# WA state sales tax for the estimated monthly shown on the Seattle dashboard
_WA_TAX_RATE = 10.4
# Conservative discount used for the "target monthly" estimate
_TARGET_DISCOUNT_PCT = 5.0


class SubScores(BaseModel):
    residual: float
    incentive: float
    discount: float
    inventory: float
    market_weakness: float
    evidence: float


class LeaseSnapshot(BaseModel):
    base_msrp: Optional[float]
    residual_percent: Optional[float]
    money_factor: Optional[float]
    apr_equivalent: Optional[float]        # money_factor * 2400
    lease_cash: Optional[float]
    total_incentives: Optional[float]
    term: Optional[int]
    mileage: Optional[int]
    estimated_monthly: Optional[float]     # at 5% disc + WA 10.4% tax, pre-DAS
    estimated_monthly_pretax: Optional[float]


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
    category: Optional[str] = Query(None, description="Filter by category: EV, Minivan"),
    min_score: float = Query(0.0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    from app.models.vehicle import Vehicle
    from app.models.score import HackabilityScore
    from app.models.lease_program import LeaseProgram

    query = (
        db.query(HackabilityScore, Vehicle)
        .join(Vehicle, HackabilityScore.vehicle_id == Vehicle.id)
        .filter(HackabilityScore.hackability_score >= min_score)
    )
    if category:
        query = query.filter(Vehicle.category.ilike(f"%{category}%"))

    rows = (
        query.order_by(HackabilityScore.hackability_score.desc())
        .limit(limit * 3)
        .all()
    )

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
            apr = round((lp.money_factor or 0) * 2400, 2) if lp.money_factor else None

            est_pretax = None
            est_with_tax = None
            if lp.base_msrp and lp.residual_percent and lp.money_factor and lp.term:
                est_pretax = calculate_monthly_payment(
                    msrp=lp.base_msrp,
                    selling_price=lp.base_msrp * (1 - _TARGET_DISCOUNT_PCT / 100),
                    residual_percent=lp.residual_percent,
                    money_factor=lp.money_factor,
                    term=lp.term,
                    lease_cash=lp.lease_cash or 0,
                    tax_rate=0,
                )
                est_with_tax = round(est_pretax * (1 + _WA_TAX_RATE / 100), 0)
                est_pretax = round(est_pretax, 0)

            lease_snap = LeaseSnapshot(
                base_msrp=lp.base_msrp,
                residual_percent=lp.residual_percent,
                money_factor=lp.money_factor,
                apr_equivalent=apr,
                lease_cash=lp.lease_cash,
                total_incentives=total,
                term=lp.term,
                mileage=lp.mileage,
                estimated_monthly=est_with_tax,
                estimated_monthly_pretax=est_pretax,
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
