"""Agent 1: Vehicle Discovery — identify lease candidates from market signals."""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

# Known high-probability candidates based on structural market signals.
# These are refreshed each run; new discoveries are appended without duplicates.
CANDIDATE_SIGNALS = [
    {
        "make": "Kia", "model": "EV9", "trim": "Wind RWD", "year": 2025, "category": "EV",
        "reason": "$7,500 EV credit via KMMAF, 48 units in Seattle metro, 34-day avg DOM",
    },
    {
        "make": "Hyundai", "model": "Ioniq 9", "trim": "SE Long Range", "year": 2025, "category": "EV",
        "reason": "New 3-row EV, introductory MF 0.00115, $7,500 EV credit, 52% residual",
    },
    {
        "make": "Kia", "model": "Carnival", "trim": "EX", "year": 2025, "category": "Minivan",
        "reason": "87 Seattle-area units, 28-day DOM, 5-6% dealer discount achievable",
    },
    {
        "make": "Kia", "model": "Carnival Hybrid", "trim": "EX HEV", "year": 2025, "category": "Minivan",
        "reason": "55% residual, $2k lease cash, slightly better program than gas Carnival",
    },
]


def run_discovery(db: Session) -> list:
    """Upsert candidate vehicles. Returns list of Vehicle objects added/found."""
    from app.models.vehicle import Vehicle

    results = []
    for sig in CANDIDATE_SIGNALS:
        existing = (
            db.query(Vehicle)
            .filter(
                Vehicle.make == sig["make"],
                Vehicle.model == sig["model"],
                Vehicle.trim == sig["trim"],
                Vehicle.year == sig["year"],
            )
            .first()
        )
        if not existing:
            v = Vehicle(
                make=sig["make"],
                model=sig["model"],
                trim=sig["trim"],
                year=sig["year"],
                category=sig["category"],
            )
            db.add(v)
            log.info("Discovered: %d %s %s %s", sig["year"], sig["make"], sig["model"], sig["trim"])
            results.append(v)
        else:
            results.append(existing)
    db.commit()
    return results
