"""
Seed database with Seattle-area lease targets.
Idempotent per vehicle: checks for each by (make, model, trim, year) before inserting.
"""
from __future__ import annotations

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

# WA sales tax rate used for estimated monthly calculation
WA_TAX_RATE = 10.4

SEED_DATA = [
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "Wind RWD", "year": 2025, "category": "EV",
        },
        "lease_program": {
            "base_msrp": 63400.0,
            "residual_percent": 48.0,
            "money_factor": 0.00175,
            "lease_cash": 7500.0,
            "loyalty_cash": 1000.0,
            "conquest_cash": 500.0,
            "term": 36,
            "mileage": 10000,
            "source": "Kia Motor Finance / Edmunds forums",
            "regional_notes": "WA sales tax ~10.4%. No additional state EV lease rebate. "
                              "Federal $7,500 EV credit passed through by KMMAF.",
        },
        "inventory": {
            "inventory_count": 48,
            "avg_days_on_market": 34.0,
            "price_reduction_count": 16,
            "dealer_count": 6,
        },
        "deals": [
            {
                "monthly_payment": 765.0, "msrp": 64200.0, "selling_price": 59900.0,
                "discount_percent": 6.7, "das": 3000.0, "term": 36, "mileage": 10000,
                "region": "WA", "leasehackr_score": 1.19,
            },
            {
                "monthly_payment": 749.0, "msrp": 63400.0, "selling_price": 59000.0,
                "discount_percent": 6.9, "das": 3200.0, "term": 36, "mileage": 10000,
                "region": "WA", "leasehackr_score": 1.18,
            },
            {
                "monthly_payment": 780.0, "msrp": 65000.0, "selling_price": 60500.0,
                "discount_percent": 6.9, "das": 2800.0, "term": 36, "mileage": 10000,
                "region": "WA", "leasehackr_score": 1.20,
            },
        ],
        "signals": [
            "$7,500 federal EV credit passed through lease",
            "48 units within 100mi of Seattle",
            "MF 0.00175 = 4.2% APR equiv",
            "6–7% dealer discount achievable in PNW",
        ],
    },
    {
        "vehicle": {
            "make": "Hyundai", "model": "Ioniq 9", "trim": "SE Long Range", "year": 2025, "category": "EV",
        },
        "lease_program": {
            "base_msrp": 62995.0,
            "residual_percent": 52.0,
            "money_factor": 0.00115,
            "lease_cash": 7500.0,
            "loyalty_cash": 1000.0,
            "conquest_cash": 500.0,
            "term": 36,
            "mileage": 10000,
            "source": "Hyundai Motor Finance / Leasehackr",
            "regional_notes": "Brand-new model (2025 launch). Limited PNW inventory. "
                              "$7,500 federal EV credit via HMF. WA tax ~10.4%.",
        },
        "inventory": {
            "inventory_count": 22,
            "avg_days_on_market": 18.0,
            "price_reduction_count": 3,
            "dealer_count": 5,
        },
        "deals": [
            {
                "monthly_payment": 642.0, "msrp": 63400.0, "selling_price": 61500.0,
                "discount_percent": 3.0, "das": 3500.0, "term": 36, "mileage": 10000,
                "region": "WA", "leasehackr_score": 1.01,
            },
            {
                "monthly_payment": 658.0, "msrp": 64000.0, "selling_price": 62100.0,
                "discount_percent": 3.0, "das": 3200.0, "term": 36, "mileage": 10000,
                "region": "CA", "leasehackr_score": 1.03,
            },
        ],
        "signals": [
            "Brand-new 3-row EV — introductory MF 0.00115 = 2.76% APR",
            "$7,500 federal EV credit via HMF",
            "52% residual — best in class for new EV launch",
            "Limited inventory keeps pricing firm; low discount potential for now",
        ],
    },
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival", "trim": "EX", "year": 2025, "category": "Minivan",
        },
        "lease_program": {
            "base_msrp": 42495.0,
            "residual_percent": 53.0,
            "money_factor": 0.00230,
            "lease_cash": 1500.0,
            "loyalty_cash": 750.0,
            "conquest_cash": 0.0,
            "term": 36,
            "mileage": 12000,
            "source": "Kia Motor Finance / Edmunds forums",
            "regional_notes": "No EV credit. WA sales tax ~10.4%. "
                              "Higher MF relative to EV programs — consider buying if financing.",
        },
        "inventory": {
            "inventory_count": 87,
            "avg_days_on_market": 28.0,
            "price_reduction_count": 26,
            "dealer_count": 6,
        },
        "deals": [
            {
                "monthly_payment": 595.0, "msrp": 43200.0, "selling_price": 40900.0,
                "discount_percent": 5.3, "das": 2500.0, "term": 36, "mileage": 12000,
                "region": "WA", "leasehackr_score": 1.38,
            },
            {
                "monthly_payment": 580.0, "msrp": 42495.0, "selling_price": 40200.0,
                "discount_percent": 5.4, "das": 2800.0, "term": 36, "mileage": 12000,
                "region": "WA", "leasehackr_score": 1.37,
            },
            {
                "monthly_payment": 610.0, "msrp": 44100.0, "selling_price": 41700.0,
                "discount_percent": 5.4, "das": 2300.0, "term": 36, "mileage": 12000,
                "region": "WA", "leasehackr_score": 1.38,
            },
        ],
        "signals": [
            "87 units in Seattle metro — dealers motivated",
            "MF 0.00230 = 5.52% APR — high cost of money",
            "5–6% dealer discount achievable",
            "Minimal lease cash ($1,500) vs. EV alternatives",
        ],
    },
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival Hybrid", "trim": "EX HEV", "year": 2025, "category": "Minivan",
        },
        "lease_program": {
            "base_msrp": 46495.0,
            "residual_percent": 55.0,
            "money_factor": 0.00215,
            "lease_cash": 2000.0,
            "loyalty_cash": 750.0,
            "conquest_cash": 0.0,
            "term": 36,
            "mileage": 12000,
            "source": "Kia Motor Finance / Edmunds forums",
            "regional_notes": "Hybrid premium over gas Carnival. WA state $2,500 clean vehicle rebate "
                              "may apply on purchase — not available for standard leases in WA.",
        },
        "inventory": {
            "inventory_count": 54,
            "avg_days_on_market": 33.0,
            "price_reduction_count": 19,
            "dealer_count": 6,
        },
        "deals": [
            {
                "monthly_payment": 564.0, "msrp": 47200.0, "selling_price": 44600.0,
                "discount_percent": 5.5, "das": 2800.0, "term": 36, "mileage": 12000,
                "region": "WA", "leasehackr_score": 1.20,
            },
            {
                "monthly_payment": 578.0, "msrp": 47800.0, "selling_price": 45200.0,
                "discount_percent": 5.4, "das": 2600.0, "term": 36, "mileage": 12000,
                "region": "WA", "leasehackr_score": 1.21,
            },
        ],
        "signals": [
            "55% residual — 2 points better than gas Carnival",
            "MF 0.00215 = 5.16% APR — slightly better than gas trim",
            "$2,000 lease cash (vs. $1,500 on gas) plus loyalty",
            "54 Seattle-area units, 33-day avg DOM",
        ],
    },
]


def run_seed(db: Session) -> None:
    from app.models.vehicle import Vehicle
    from app.models.lease_program import LeaseProgram
    from app.models.inventory import InventoryMetric
    from app.models.deal_evidence import DealEvidence
    from app.agents.hackability_ranking import compute_hackability_score

    now = datetime.utcnow()
    today = date.today()
    seeded = 0

    for entry in SEED_DATA:
        v_data = entry["vehicle"]

        existing = (
            db.query(Vehicle)
            .filter(
                Vehicle.make == v_data["make"],
                Vehicle.model == v_data["model"],
                Vehicle.trim == v_data["trim"],
                Vehicle.year == v_data["year"],
            )
            .first()
        )
        if existing:
            continue  # already seeded — idempotent per vehicle

        vehicle = Vehicle(**v_data)
        db.add(vehicle)
        db.flush()

        lp = LeaseProgram(
            vehicle_id=vehicle.id,
            program_month=now.month,
            program_year=now.year,
            **entry["lease_program"],
        )
        db.add(lp)

        im = InventoryMetric(
            vehicle_id=vehicle.id,
            region="Seattle Metro / Puget Sound",
            recorded_date=today,
            source="seed/market-research",
            **entry["inventory"],
        )
        db.add(im)

        for deal in entry.get("deals", []):
            de = DealEvidence(
                vehicle_id=vehicle.id,
                deal_date=today,
                source="leasehackr/seed",
                **deal,
            )
            db.add(de)

        db.commit()
        compute_hackability_score(vehicle.id, db)
        seeded += 1
        log.info("Seeded: %s %s %s", vehicle.year, vehicle.make, vehicle.model)

    if seeded:
        log.info("Seed complete — %d vehicles added.", seeded)
    else:
        log.info("Seed skipped — all target vehicles already present.")
