"""Agent 1: Vehicle Discovery — identify lease candidates from market signals."""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

# Known high-probability candidates based on structural market signals.
# These are refreshed each run; new discoveries are appended without duplicates.
CANDIDATE_SIGNALS = [
    {"make": "Chevrolet", "model": "Equinox EV", "trim": "LT", "year": 2025, "category": "EV",
     "reason": "High inventory, EV lease credit, GM Financial aggressive program"},
    {"make": "Hyundai", "model": "Ioniq 5", "trim": "SE Standard Range", "year": 2025, "category": "EV",
     "reason": "EV lease credit, Hyundai Motor Finance competitive MF, strong residuals"},
    {"make": "Kia", "model": "EV6", "trim": "Wind", "year": 2025, "category": "EV",
     "reason": "EV lease credit, Kia Motor Finance support, sister program to Ioniq 5"},
    {"make": "Nissan", "model": "Ariya", "trim": "Engage", "year": 2025, "category": "EV",
     "reason": "Very high inventory, Nissan pushing to move units, 90+ days on market at many dealers"},
    {"make": "Honda", "model": "Prologue", "trim": "EX-L", "year": 2025, "category": "EV",
     "reason": "Honda EV launch push, EV lease credit, clearing inventory ahead of Honda-built EVs"},
    {"make": "Jeep", "model": "Wrangler 4xe", "trim": "Sahara", "year": 2025, "category": "SUV",
     "reason": "PHEV state credits + conquest cash, Jeep high residuals, historically repeating deal"},
    {"make": "Chevrolet", "model": "Blazer EV", "trim": "LT", "year": 2025, "category": "EV",
     "reason": "EV credit, competing with Equinox EV for inventory clearance"},
    {"make": "Polestar", "model": "2", "trim": "Long Range Single Motor", "year": 2025, "category": "EV",
     "reason": "Polestar aggressive incentives, high inventory, very low money factor"},
    {"make": "Volvo", "model": "C40 Recharge", "trim": "Plus", "year": 2025, "category": "EV",
     "reason": "EV credit, Volvo Car Financial competitive, inventory above days-on-market threshold"},
    {"make": "BMW", "model": "iX", "trim": "xDrive50", "year": 2025, "category": "Luxury",
     "reason": "EV lease credit on luxury segment, BMW Financial strong program"},
    {"make": "Ford", "model": "F-150 Lightning", "trim": "XLT", "year": 2025, "category": "Truck",
     "reason": "EV credit, high truck inventory, Ford Motor Credit incentivizing"},
    {"make": "Mercedes-Benz", "model": "EQE", "trim": "350+", "year": 2025, "category": "Luxury",
     "reason": "EV credit on luxury, MBFS aggressive to compete with BMW/Audi EV offerings"},
    {"make": "Genesis", "model": "GV80e", "trim": "Advanced", "year": 2025, "category": "Luxury",
     "reason": "Genesis underdog push, EV credit, higher discount potential vs. German brands"},
    {"make": "Chevrolet", "model": "Silverado EV", "trim": "WT", "year": 2025, "category": "Truck",
     "reason": "EV credit, GM pushing fleet + retail, high inventory, competing with F-150 Lightning"},
    {"make": "Cadillac", "model": "Lyriq", "trim": "Luxury", "year": 2025, "category": "Luxury",
     "reason": "EV credit, Cadillac pushing EV transition, strong residuals, GMFS support"},
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
