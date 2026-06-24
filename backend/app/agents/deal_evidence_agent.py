"""Agent 4: Deal Evidence — collect confirmed signed deals from Leasehackr and forums."""
from __future__ import annotations

import logging
import re
from datetime import date

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeaseHackr-Discovery/1.0)"}
_LH_SIGNED = "https://leasehackr.com/deals/signed"


def run_deal_evidence(db: Session) -> list:
    """Scrape Leasehackr signed deals page. Falls back gracefully on any error."""
    from app.models.vehicle import Vehicle
    from app.models.deal_evidence import DealEvidence

    vehicles = db.query(Vehicle).all()
    vehicle_map = {
        f"{v.year} {v.make} {v.model}".lower(): v for v in vehicles
    }

    results = []
    try:
        deals = _scrape_lh_signed_deals()
        today = date.today()
        for deal in deals:
            matched = _match_vehicle(deal.get("vehicle_name", ""), vehicle_map)
            if not matched:
                continue
            ev = DealEvidence(
                vehicle_id=matched.id,
                monthly_payment=deal.get("monthly"),
                msrp=deal.get("msrp"),
                discount_percent=deal.get("discount_percent"),
                das=deal.get("das"),
                term=deal.get("term"),
                mileage=deal.get("mileage"),
                region=deal.get("region"),
                source="leasehackr",
                deal_date=today,
            )
            db.add(ev)
            results.append(ev)
        if results:
            db.commit()
    except Exception as exc:
        log.warning("Deal evidence scrape failed: %s", exc)

    return results


def _scrape_lh_signed_deals() -> list[dict]:
    try:
        with httpx.Client(timeout=10, headers=_HEADERS, follow_redirects=True) as client:
            resp = client.get(_LH_SIGNED)
            if resp.status_code != 200:
                return []
        soup = BeautifulSoup(resp.text, "lxml")
        deals = []
        for row in soup.select(".deal-row, .deal-card, tr.deal")[:50]:
            deal = _parse_deal_row(row)
            if deal:
                deals.append(deal)
        return deals
    except Exception as exc:
        log.warning("LH scrape error: %s", exc)
        return []


def _parse_deal_row(element) -> dict | None:
    text = element.get_text(" ", strip=True)
    monthly_match = re.search(r"\$(\d{2,4})/mo", text)
    msrp_match = re.search(r"MSRP[:\s]+\$?([\d,]+)", text, re.IGNORECASE)
    return {
        "vehicle_name": text[:80],
        "monthly": float(monthly_match.group(1)) if monthly_match else None,
        "msrp": float(msrp_match.group(1).replace(",", "")) if msrp_match else None,
    } if monthly_match else None


def _match_vehicle(name: str, vehicle_map: dict):
    name_lower = name.lower()
    for key, vehicle in vehicle_map.items():
        parts = key.split()
        if all(p in name_lower for p in parts[1:]):  # skip year
            return vehicle
    return None
