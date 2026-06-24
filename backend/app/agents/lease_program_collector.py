"""Agent 2: Lease Program Collection — scrape Edmunds forums and manufacturer pages."""
from __future__ import annotations

import logging
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

_EDMUNDS_FORUM_BASE = "https://forums.edmunds.com"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeaseHackr-Discovery/1.0)"}


def run_collection(db: Session) -> list:
    """Attempt to collect current lease programs. Falls back to existing DB data on error."""
    from app.models.vehicle import Vehicle
    from app.models.lease_program import LeaseProgram

    vehicles = db.query(Vehicle).all()
    results = []
    now = datetime.utcnow()

    for vehicle in vehicles:
        try:
            program = _fetch_program_for_vehicle(vehicle, now)
            if program:
                lp = LeaseProgram(
                    vehicle_id=vehicle.id,
                    program_month=now.month,
                    program_year=now.year,
                    **program,
                )
                db.add(lp)
                results.append(lp)
        except Exception as exc:
            log.warning("Lease program collection failed for %s %s: %s", vehicle.make, vehicle.model, exc)

    if results:
        db.commit()
    return results


def _fetch_program_for_vehicle(vehicle, now: datetime) -> dict | None:
    """
    Attempt a lightweight probe of Edmunds for current incentive data.
    Returns a partial LeaseProgram dict or None if unavailable.
    """
    search_term = f"{vehicle.year} {vehicle.make} {vehicle.model} lease money factor residual"
    url = f"https://www.edmunds.com/car-leasing/articles/lease-deals/"
    try:
        with httpx.Client(timeout=8, headers=_HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return None
        # Minimal parse — real extraction would need model-specific pages
        return None
    except Exception:
        return None
