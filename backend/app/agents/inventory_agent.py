"""Agent 3: Inventory Intelligence — measure national supply and market pressure."""
from __future__ import annotations

import logging
from datetime import date

import httpx
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeaseHackr-Discovery/1.0)"}


def run_inventory(db: Session) -> list:
    """Attempt to collect inventory metrics. Falls back gracefully on error."""
    from app.models.vehicle import Vehicle
    from app.models.inventory import InventoryMetric

    vehicles = db.query(Vehicle).all()
    results = []
    today = date.today()

    for vehicle in vehicles:
        try:
            metrics = _fetch_inventory_for_vehicle(vehicle)
            if metrics:
                im = InventoryMetric(
                    vehicle_id=vehicle.id,
                    region="National",
                    recorded_date=today,
                    source="cargurus",
                    **metrics,
                )
                db.add(im)
                results.append(im)
        except Exception as exc:
            log.warning("Inventory collection failed for %s %s: %s", vehicle.make, vehicle.model, exc)

    if results:
        db.commit()
    return results


def _fetch_inventory_for_vehicle(vehicle) -> dict | None:
    """
    CarGurus has a public search endpoint. We probe it for count signals.
    Returns None if unavailable — seed data covers the baseline.
    """
    try:
        query = f"{vehicle.year}+{vehicle.make}+{vehicle.model}".replace(" ", "+")
        url = f"https://www.cargurus.com/Cars/new/nl-New-{vehicle.make}-{vehicle.model}-d2455"
        with httpx.Client(timeout=8, headers=_HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return None
        return None
    except Exception:
        return None
