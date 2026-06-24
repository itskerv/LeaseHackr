"""Agent 1: Vehicle Discovery — identify lease candidates from market signals."""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

CANDIDATE_SIGNALS = [
    # ── Kia EV9 ─────────────────────────────────────────────────────────────
    {
        "make": "Kia", "model": "EV9", "trim": "Light Long Range", "year": 2025, "category": "EV",
        "reason": "$7,500 EV credit via KMMAF, entry trim with broadest buyer pool",
    },
    {
        "make": "Kia", "model": "EV9", "trim": "Wind RWD", "year": 2025, "category": "EV",
        "reason": "$7,500 EV credit via KMMAF, 48 units in Seattle metro, 34-day avg DOM",
    },
    {
        "make": "Kia", "model": "EV9", "trim": "Wind AWD", "year": 2025, "category": "EV",
        "reason": "AWD version of Wind, 47% residual at 36mo, similar incentive stack",
    },
    {
        "make": "Kia", "model": "EV9", "trim": "GT-Line RWD", "year": 2025, "category": "EV",
        "reason": "Top EV9 trim, 46% residual weakest in lineup, limited 24/36mo only",
    },
    # ── Hyundai Ioniq 9 ─────────────────────────────────────────────────────
    {
        "make": "Hyundai", "model": "Ioniq 9", "trim": "SE Long Range", "year": 2025, "category": "EV",
        "reason": "New 3-row EV, introductory MF 0.00115, $7,500 EV credit, 52% residual at 36mo",
    },
    {
        "make": "Hyundai", "model": "Ioniq 9", "trim": "SEL", "year": 2025, "category": "EV",
        "reason": "Mid-tier Ioniq 9, same low MF, 50% residual at 36mo",
    },
    {
        "make": "Hyundai", "model": "Ioniq 9", "trim": "Limited", "year": 2025, "category": "EV",
        "reason": "Top Ioniq 9, 48% residual at 36mo, very limited PNW inventory",
    },
    # ── Kia Carnival ────────────────────────────────────────────────────────
    {
        "make": "Kia", "model": "Carnival", "trim": "LX", "year": 2025, "category": "Minivan",
        "reason": "Entry Carnival, best residual in gas lineup at 55%, 75 Seattle-area units",
    },
    {
        "make": "Kia", "model": "Carnival", "trim": "EX", "year": 2025, "category": "Minivan",
        "reason": "87 Seattle-area units, 28-day DOM, 5-6% dealer discount achievable",
    },
    {
        "make": "Kia", "model": "Carnival", "trim": "SX", "year": 2025, "category": "Minivan",
        "reason": "Top gas Carnival, 52% residual, 62 Seattle-area units",
    },
    # ── Kia Carnival Hybrid ─────────────────────────────────────────────────
    {
        "make": "Kia", "model": "Carnival Hybrid", "trim": "EX HEV", "year": 2025, "category": "Minivan",
        "reason": "55% residual, $2k lease cash, slightly better program than gas Carnival",
    },
    {
        "make": "Kia", "model": "Carnival Hybrid", "trim": "SX HEV", "year": 2025, "category": "Minivan",
        "reason": "Top HEV trim, 53% residual at 36mo, $2k lease cash",
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
