"""Agent 6: Hackability Ranking Engine."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

# Scoring weights as specified in the PRD
WEIGHTS = {
    "residual": 0.25,
    "incentive": 0.25,
    "discount": 0.20,
    "inventory": 0.15,
    "market_weakness": 0.10,
    "evidence": 0.05,
}


# ---------------------------------------------------------------------------
# Sub-score calculators (each returns 0–100)
# ---------------------------------------------------------------------------

def _residual_score(residual_percent: Optional[float]) -> float:
    """Higher residual = lower monthly payment = better lease. 60%+ = 100."""
    if residual_percent is None:
        return 40.0
    return min(100.0, max(0.0, (residual_percent - 40.0) * 5.0))


def _incentive_score(total_cash: float) -> float:
    """Total incentive cash (all rebates combined). $5k+ scores 100."""
    return min(100.0, total_cash / 50.0)


def _discount_score(avg_discount_percent: Optional[float]) -> float:
    """Dealer discount potential from deal evidence. 10%+ off MSRP = 100."""
    if avg_discount_percent is None:
        return 30.0
    return min(100.0, avg_discount_percent * 10.0)


def _inventory_score(inventory_count: Optional[int], avg_dom: Optional[float]) -> float:
    """High count + high DOM = buyer's market = high score."""
    count_score = min(100.0, (inventory_count or 0) / 50.0)
    dom_score = min(100.0, (avg_dom or 0) * 2.0)
    return round(count_score * 0.6 + dom_score * 0.4, 1)


def _market_weakness_score(
    price_reductions: Optional[int], inventory_count: Optional[int]
) -> float:
    """Fraction of inventory with price cuts signals a weak market for the vehicle."""
    if not inventory_count:
        return 35.0
    ratio = (price_reductions or 0) / inventory_count
    return min(100.0, ratio * 200.0)


def _evidence_score(deal_count: int) -> float:
    """Volume of confirmed real deals. 20+ deals = score 100."""
    return min(100.0, deal_count * 5.0)


# ---------------------------------------------------------------------------
# Composite scorer
# ---------------------------------------------------------------------------

def compute_hackability_score(vehicle_id: int, db: Session) -> "HackabilityScore":
    from app.models.vehicle import Vehicle
    from app.models.lease_program import LeaseProgram
    from app.models.inventory import InventoryMetric
    from app.models.deal_evidence import DealEvidence
    from app.models.score import HackabilityScore

    now = datetime.utcnow()

    # Fetch all lease programs; use 36mo as canonical, fall back to most recent
    all_programs = (
        db.query(LeaseProgram)
        .filter(LeaseProgram.vehicle_id == vehicle_id)
        .order_by(LeaseProgram.program_year.desc(), LeaseProgram.program_month.desc())
        .all()
    )
    lp: Optional[LeaseProgram] = next(
        (p for p in all_programs if p.term == 36),
        all_programs[0] if all_programs else None,
    )

    # Fetch latest inventory snapshot
    inv: Optional[InventoryMetric] = (
        db.query(InventoryMetric)
        .filter(InventoryMetric.vehicle_id == vehicle_id)
        .order_by(InventoryMetric.recorded_date.desc())
        .first()
    )

    # Fetch all deal evidence for this vehicle
    deals = db.query(DealEvidence).filter(DealEvidence.vehicle_id == vehicle_id).all()
    deal_count = len(deals)
    avg_discount = (
        sum(d.discount_percent for d in deals if d.discount_percent) / deal_count
        if deal_count else None
    )

    # Compute individual sub-scores
    total_cash = 0.0
    if lp:
        total_cash = (
            (lp.lease_cash or 0)
            + (lp.loyalty_cash or 0)
            + (lp.conquest_cash or 0)
            + (lp.military_cash or 0)
            + (lp.college_cash or 0)
            + (lp.costco_cash or 0)
        )

    r_score = _residual_score(lp.residual_percent if lp else None)
    i_score = _incentive_score(total_cash)
    d_score = _discount_score(avg_discount)
    inv_score = _inventory_score(
        inv.inventory_count if inv else None,
        inv.avg_days_on_market if inv else None,
    )
    mw_score = _market_weakness_score(
        inv.price_reduction_count if inv else None,
        inv.inventory_count if inv else None,
    )
    ev_score = _evidence_score(deal_count)

    hackability = round(
        r_score * WEIGHTS["residual"]
        + i_score * WEIGHTS["incentive"]
        + d_score * WEIGHTS["discount"]
        + inv_score * WEIGHTS["inventory"]
        + mw_score * WEIGHTS["market_weakness"]
        + ev_score * WEIGHTS["evidence"],
        1,
    )

    # Confidence: baseline 30, +10 per populated data type, +10 if 5+ deals
    confidence = 30.0
    if lp:
        confidence += 20.0
    if inv:
        confidence += 20.0
    if deal_count > 0:
        confidence += 15.0
    if deal_count >= 5:
        confidence += 15.0
    confidence = min(100.0, confidence)

    explanation = _build_explanation(
        r_score, i_score, d_score, inv_score, mw_score, ev_score,
        lp, inv, deal_count, hackability
    )

    # Upsert: one score row per vehicle per (month, year)
    existing = (
        db.query(HackabilityScore)
        .filter(
            HackabilityScore.vehicle_id == vehicle_id,
            HackabilityScore.score_month == now.month,
            HackabilityScore.score_year == now.year,
        )
        .first()
    )
    if existing:
        score_row = existing
    else:
        score_row = HackabilityScore(
            vehicle_id=vehicle_id,
            score_month=now.month,
            score_year=now.year,
        )
        db.add(score_row)

    score_row.hackability_score = hackability
    score_row.confidence_score = round(confidence, 1)
    score_row.residual_score = round(r_score, 1)
    score_row.incentive_score = round(i_score, 1)
    score_row.discount_score = round(d_score, 1)
    score_row.inventory_score = round(inv_score, 1)
    score_row.market_weakness_score = round(mw_score, 1)
    score_row.evidence_score = round(ev_score, 1)
    score_row.explanation = explanation
    score_row.last_updated = now
    db.commit()
    db.refresh(score_row)
    return score_row


def _build_explanation(
    r, i, d, inv, mw, ev, lp, inventory, deal_count, hackability
) -> str:
    lines = []
    if lp and lp.residual_percent:
        lines.append(f"Residual {lp.residual_percent:.0f}% (36mo/10k) — {'above' if lp.residual_percent >= 56 else 'near'} market average.")
    if lp:
        total = (
            (lp.lease_cash or 0) + (lp.loyalty_cash or 0) + (lp.conquest_cash or 0)
            + (lp.military_cash or 0) + (lp.college_cash or 0) + (lp.costco_cash or 0)
        )
        if total > 0:
            lines.append(f"${total:,.0f} in combined incentives available.")
        if lp.money_factor and lp.money_factor < 0.001:
            apr_equiv = lp.money_factor * 2400
            lines.append(f"Money factor {lp.money_factor:.5f} ({apr_equiv:.1f}% APR equiv).")
    if inventory and inventory.inventory_count:
        lines.append(
            f"{inventory.inventory_count:,} units in national inventory"
            + (f", avg {inventory.avg_days_on_market:.0f} days on market." if inventory.avg_days_on_market else ".")
        )
    if deal_count > 0:
        lines.append(f"{deal_count} confirmed signed deal{'s' if deal_count != 1 else ''} on record.")
    if not lines:
        lines.append("Limited data available — score based on market signals.")
    category = "Elite" if hackability >= 85 else "Excellent" if hackability >= 70 else "Good" if hackability >= 55 else "Average"
    lines.insert(0, f"Hackability {hackability:.0f}/100 — {category}.")
    return " ".join(lines)
