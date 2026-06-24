"""
Seed database with 15 historical lease winners.
Idempotent: skips if vehicles already exist.
Includes realistic lease programs, inventory metrics, deal evidence, and pre-computed scores.
"""
from __future__ import annotations

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

# Each entry drives all five tables: Vehicle, LeaseProgram, InventoryMetric, DealEvidence, HackabilityScore
SEED_DATA = [
    {
        "vehicle": {"make": "Chevrolet", "model": "Equinox EV", "trim": "LT", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 62.0, "money_factor": 0.00050, "lease_cash": 7500.0,
            "loyalty_cash": 1000.0, "conquest_cash": 500.0, "term": 36, "mileage": 10000,
            "source": "GM Financial / Edmunds forums",
        },
        "inventory": {
            "inventory_count": 3200, "avg_days_on_market": 38.0,
            "price_reduction_count": 1100, "dealer_count": 2800,
        },
        "deals": [
            {"monthly_payment": 229.0, "msrp": 35300.0, "selling_price": 32400.0,
             "discount_percent": 8.2, "das": 2100.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.65},
            {"monthly_payment": 249.0, "msrp": 36200.0, "selling_price": 33100.0,
             "discount_percent": 8.6, "das": 1800.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.69},
            {"monthly_payment": 215.0, "msrp": 34800.0, "selling_price": 31900.0,
             "discount_percent": 8.3, "das": 2000.0, "term": 36, "mileage": 10000,
             "region": "FL", "leasehackr_score": 0.62},
            {"monthly_payment": 239.0, "msrp": 35500.0, "selling_price": 32500.0,
             "discount_percent": 8.5, "das": 1900.0, "term": 36, "mileage": 10000,
             "region": "NY", "leasehackr_score": 0.67},
        ],
        "signals": ["$7,500 EV lease credit", "High national inventory (3,200+ units)", "GM Financial 1.2% APR equiv MF", "38-day avg market time"],
    },
    {
        "vehicle": {"make": "Hyundai", "model": "Ioniq 5", "trim": "SE Standard Range", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 58.0, "money_factor": 0.00045, "lease_cash": 7500.0,
            "loyalty_cash": 750.0, "conquest_cash": 500.0, "term": 36, "mileage": 10000,
            "source": "Hyundai Motor Finance / Leasehackr forums",
        },
        "inventory": {
            "inventory_count": 2800, "avg_days_on_market": 42.0,
            "price_reduction_count": 980, "dealer_count": 820,
        },
        "deals": [
            {"monthly_payment": 299.0, "msrp": 44500.0, "selling_price": 40600.0,
             "discount_percent": 8.8, "das": 2500.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.67},
            {"monthly_payment": 319.0, "msrp": 45200.0, "selling_price": 41200.0,
             "discount_percent": 8.8, "das": 2200.0, "term": 36, "mileage": 10000,
             "region": "NJ", "leasehackr_score": 0.71},
            {"monthly_payment": 285.0, "msrp": 43800.0, "selling_price": 39900.0,
             "discount_percent": 8.9, "das": 2400.0, "term": 36, "mileage": 10000,
             "region": "WA", "leasehackr_score": 0.65},
        ],
        "signals": ["$7,500 EV lease credit", "Hyundai Motor Finance sub-1% APR MF", "Strong 58% residual", "Conquest cash available"],
    },
    {
        "vehicle": {"make": "Kia", "model": "EV6", "trim": "Wind", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 56.0, "money_factor": 0.00043, "lease_cash": 7500.0,
            "loyalty_cash": 750.0, "conquest_cash": 500.0, "term": 36, "mileage": 10000,
            "source": "Kia Motor Finance / Edmunds forums",
        },
        "inventory": {
            "inventory_count": 2600, "avg_days_on_market": 45.0,
            "price_reduction_count": 910, "dealer_count": 760,
        },
        "deals": [
            {"monthly_payment": 329.0, "msrp": 46800.0, "selling_price": 42600.0,
             "discount_percent": 9.0, "das": 2300.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.70},
            {"monthly_payment": 349.0, "msrp": 47500.0, "selling_price": 43200.0,
             "discount_percent": 9.1, "das": 2100.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.74},
            {"monthly_payment": 315.0, "msrp": 46200.0, "selling_price": 42000.0,
             "discount_percent": 9.1, "das": 2400.0, "term": 36, "mileage": 10000,
             "region": "IL", "leasehackr_score": 0.68},
        ],
        "signals": ["$7,500 EV lease credit", "Kia Motor Finance lowest MF in segment", "Sister program mirrors Ioniq 5"],
    },
    {
        "vehicle": {"make": "Nissan", "model": "Ariya", "trim": "Engage", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 54.0, "money_factor": 0.00041, "lease_cash": 8000.0,
            "loyalty_cash": 1000.0, "conquest_cash": 1000.0, "term": 36, "mileage": 10000,
            "source": "Nissan Motor Acceptance Corp / Leasehackr",
        },
        "inventory": {
            "inventory_count": 1800, "avg_days_on_market": 52.0,
            "price_reduction_count": 810, "dealer_count": 1100,
        },
        "deals": [
            {"monthly_payment": 269.0, "msrp": 43500.0, "selling_price": 39200.0,
             "discount_percent": 9.9, "das": 2500.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.62},
            {"monthly_payment": 289.0, "msrp": 44200.0, "selling_price": 39800.0,
             "discount_percent": 9.9, "das": 2200.0, "term": 36, "mileage": 10000,
             "region": "NJ", "leasehackr_score": 0.65},
        ],
        "signals": ["$8,000 lease cash from Nissan", "52-day avg DOM — dealers motivated", "Conquest + loyalty stackable", "Lowest volume = most motivated dealers"],
    },
    {
        "vehicle": {"make": "Honda", "model": "Prologue", "trim": "EX-L", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 60.0, "money_factor": 0.00046, "lease_cash": 7500.0,
            "loyalty_cash": 500.0, "conquest_cash": 0.0, "term": 36, "mileage": 10000,
            "source": "Honda Financial Services / Edmunds",
        },
        "inventory": {
            "inventory_count": 2100, "avg_days_on_market": 44.0,
            "price_reduction_count": 720, "dealer_count": 1050,
        },
        "deals": [
            {"monthly_payment": 349.0, "msrp": 51900.0, "selling_price": 47900.0,
             "discount_percent": 7.7, "das": 2500.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.67},
            {"monthly_payment": 369.0, "msrp": 53100.0, "selling_price": 49000.0,
             "discount_percent": 7.7, "das": 2300.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.70},
        ],
        "signals": ["$7,500 EV credit", "60% residual — exceptional for EV", "Honda pushing EV transition", "Clearing ahead of Honda-built EV lineup"],
    },
    {
        "vehicle": {"make": "Jeep", "model": "Wrangler 4xe", "trim": "Sahara", "year": 2025, "category": "SUV"},
        "lease_program": {
            "residual_percent": 55.0, "money_factor": 0.00062, "lease_cash": 5000.0,
            "loyalty_cash": 1500.0, "conquest_cash": 1500.0, "military_cash": 500.0,
            "term": 36, "mileage": 10000,
            "source": "Stellantis Financial / Leasehackr",
        },
        "inventory": {
            "inventory_count": 4500, "avg_days_on_market": 33.0,
            "price_reduction_count": 1350, "dealer_count": 2400,
        },
        "deals": [
            {"monthly_payment": 449.0, "msrp": 57900.0, "selling_price": 52500.0,
             "discount_percent": 9.3, "das": 3000.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.78},
            {"monthly_payment": 399.0, "msrp": 57200.0, "selling_price": 51800.0,
             "discount_percent": 9.4, "das": 2800.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.70},
            {"monthly_payment": 429.0, "msrp": 57500.0, "selling_price": 52000.0,
             "discount_percent": 9.6, "das": 3200.0, "term": 36, "mileage": 10000,
             "region": "FL", "leasehackr_score": 0.75},
        ],
        "signals": ["PHEV qualifies for state EV incentives", "Conquest + loyalty stackable ($3k)", "Historically repeating lease special", "55% residual strong for PHEV SUV"],
    },
    {
        "vehicle": {"make": "Chevrolet", "model": "Blazer EV", "trim": "LT", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 57.0, "money_factor": 0.00048, "lease_cash": 6000.0,
            "loyalty_cash": 1000.0, "conquest_cash": 500.0, "term": 36, "mileage": 10000,
            "source": "GM Financial / Edmunds forums",
        },
        "inventory": {
            "inventory_count": 2200, "avg_days_on_market": 40.0,
            "price_reduction_count": 770, "dealer_count": 2200,
        },
        "deals": [
            {"monthly_payment": 299.0, "msrp": 40600.0, "selling_price": 37400.0,
             "discount_percent": 7.9, "das": 2200.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.74},
            {"monthly_payment": 319.0, "msrp": 41200.0, "selling_price": 37900.0,
             "discount_percent": 8.0, "das": 2000.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.77},
        ],
        "signals": ["$6,000 EV lease cash", "57% residual on GM Electric", "Competing with Equinox EV keeps program sharp", "Established GM dealer network"],
    },
    {
        "vehicle": {"make": "Polestar", "model": "2", "trim": "Long Range Single Motor", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 53.0, "money_factor": 0.00039, "lease_cash": 6000.0,
            "loyalty_cash": 500.0, "conquest_cash": 1000.0, "term": 36, "mileage": 10000,
            "source": "Polestar Financial / Leasehackr",
        },
        "inventory": {
            "inventory_count": 1500, "avg_days_on_market": 55.0,
            "price_reduction_count": 750, "dealer_count": 280,
        },
        "deals": [
            {"monthly_payment": 299.0, "msrp": 45900.0, "selling_price": 40900.0,
             "discount_percent": 10.9, "das": 2500.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.65},
            {"monthly_payment": 279.0, "msrp": 45200.0, "selling_price": 40200.0,
             "discount_percent": 11.1, "das": 2300.0, "term": 36, "mileage": 10000,
             "region": "WA", "leasehackr_score": 0.62},
        ],
        "signals": ["0.94% APR equiv MF — exceptional", "$6k lease cash", "55-day DOM — dealers very motivated", "Polestar offering up to 11% off MSRP"],
    },
    {
        "vehicle": {"make": "Volvo", "model": "C40 Recharge", "trim": "Plus", "year": 2025, "category": "EV"},
        "lease_program": {
            "residual_percent": 55.0, "money_factor": 0.00040, "lease_cash": 5500.0,
            "loyalty_cash": 750.0, "conquest_cash": 750.0, "term": 36, "mileage": 10000,
            "source": "Volvo Car Financial / Edmunds",
        },
        "inventory": {
            "inventory_count": 1700, "avg_days_on_market": 50.0,
            "price_reduction_count": 680, "dealer_count": 320,
        },
        "deals": [
            {"monthly_payment": 369.0, "msrp": 54900.0, "selling_price": 49200.0,
             "discount_percent": 10.4, "das": 2800.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.67},
            {"monthly_payment": 389.0, "msrp": 55600.0, "selling_price": 49900.0,
             "discount_percent": 10.3, "das": 2600.0, "term": 36, "mileage": 10000,
             "region": "NY", "leasehackr_score": 0.70},
        ],
        "signals": ["0.96% APR equiv MF", "$5,500 lease cash", "50-day avg DOM", "Volvo pushing EV mix ahead of 2030 goal"],
    },
    {
        "vehicle": {"make": "BMW", "model": "iX", "trim": "xDrive50", "year": 2025, "category": "Luxury"},
        "lease_program": {
            "residual_percent": 52.0, "money_factor": 0.00085, "lease_cash": 5000.0,
            "loyalty_cash": 2000.0, "conquest_cash": 1000.0, "term": 36, "mileage": 10000,
            "source": "BMW Financial Services / Edmunds",
        },
        "inventory": {
            "inventory_count": 1200, "avg_days_on_market": 48.0,
            "price_reduction_count": 360, "dealer_count": 350,
        },
        "deals": [
            {"monthly_payment": 799.0, "msrp": 92500.0, "selling_price": 81300.0,
             "discount_percent": 12.1, "das": 4000.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.86},
            {"monthly_payment": 849.0, "msrp": 93200.0, "selling_price": 82000.0,
             "discount_percent": 12.0, "das": 3500.0, "term": 36, "mileage": 10000,
             "region": "NY", "leasehackr_score": 0.91},
        ],
        "signals": ["12%+ dealer discount common", "$5k EV lease cash + $3k loyalty/conquest", "BMW clearing iX ahead of next gen", "48-day avg DOM for luxury segment"],
    },
    {
        "vehicle": {"make": "Ford", "model": "F-150 Lightning", "trim": "XLT", "year": 2025, "category": "Truck"},
        "lease_program": {
            "residual_percent": 50.0, "money_factor": 0.00055, "lease_cash": 5000.0,
            "loyalty_cash": 1500.0, "conquest_cash": 1000.0, "term": 36, "mileage": 10000,
            "source": "Ford Motor Credit / Edmunds forums",
        },
        "inventory": {
            "inventory_count": 3800, "avg_days_on_market": 58.0,
            "price_reduction_count": 1900, "dealer_count": 3200,
        },
        "deals": [
            {"monthly_payment": 479.0, "msrp": 55400.0, "selling_price": 49100.0,
             "discount_percent": 11.4, "das": 3000.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.87},
            {"monthly_payment": 449.0, "msrp": 54800.0, "selling_price": 48500.0,
             "discount_percent": 11.5, "das": 2800.0, "term": 36, "mileage": 10000,
             "region": "MI", "leasehackr_score": 0.82},
            {"monthly_payment": 499.0, "msrp": 55900.0, "selling_price": 49400.0,
             "discount_percent": 11.6, "das": 3200.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.89},
        ],
        "signals": ["3,800+ units national inventory", "58-day avg DOM — 50% have been price-cut", "11%+ dealer discount achievable", "$5k EV lease cash + stackable loyalty"],
    },
    {
        "vehicle": {"make": "Mercedes-Benz", "model": "EQE", "trim": "350+", "year": 2025, "category": "Luxury"},
        "lease_program": {
            "residual_percent": 48.0, "money_factor": 0.00078, "lease_cash": 6000.0,
            "loyalty_cash": 2000.0, "conquest_cash": 1000.0, "term": 36, "mileage": 10000,
            "source": "Mercedes-Benz Financial / Leasehackr",
        },
        "inventory": {
            "inventory_count": 1100, "avg_days_on_market": 62.0,
            "price_reduction_count": 550, "dealer_count": 380,
        },
        "deals": [
            {"monthly_payment": 699.0, "msrp": 76800.0, "selling_price": 66900.0,
             "discount_percent": 12.9, "das": 4000.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.91},
            {"monthly_payment": 729.0, "msrp": 77500.0, "selling_price": 67500.0,
             "discount_percent": 12.9, "das": 3800.0, "term": 36, "mileage": 10000,
             "region": "FL", "leasehackr_score": 0.94},
        ],
        "signals": ["62-day avg DOM — high dealer urgency", "13%+ discount achievable", "$6k lease cash + $3k loyalty/conquest", "MBFS competing hard with BMW iX"],
    },
    {
        "vehicle": {"make": "Genesis", "model": "GV80e", "trim": "Advanced", "year": 2025, "category": "Luxury"},
        "lease_program": {
            "residual_percent": 56.0, "money_factor": 0.00058, "lease_cash": 5000.0,
            "loyalty_cash": 1500.0, "conquest_cash": 1500.0, "term": 36, "mileage": 10000,
            "source": "Genesis Financial / Edmunds forums",
        },
        "inventory": {
            "inventory_count": 900, "avg_days_on_market": 47.0,
            "price_reduction_count": 270, "dealer_count": 210,
        },
        "deals": [
            {"monthly_payment": 649.0, "msrp": 84500.0, "selling_price": 76800.0,
             "discount_percent": 9.1, "das": 3500.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.77},
            {"monthly_payment": 679.0, "msrp": 85200.0, "selling_price": 77500.0,
             "discount_percent": 9.0, "das": 3300.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.80},
        ],
        "signals": ["56% residual rare for EV luxury", "Genesis underdog pricing vs. BMW/MB", "$5k cash + $3k loyalty/conquest", "47-day DOM — dealers flexible"],
    },
    {
        "vehicle": {"make": "Chevrolet", "model": "Silverado EV", "trim": "WT", "year": 2025, "category": "Truck"},
        "lease_program": {
            "residual_percent": 51.0, "money_factor": 0.00052, "lease_cash": 5500.0,
            "loyalty_cash": 1500.0, "conquest_cash": 1000.0, "term": 36, "mileage": 10000,
            "source": "GM Financial / Edmunds forums",
        },
        "inventory": {
            "inventory_count": 2500, "avg_days_on_market": 55.0,
            "price_reduction_count": 1000, "dealer_count": 2400,
        },
        "deals": [
            {"monthly_payment": 549.0, "msrp": 72000.0, "selling_price": 64800.0,
             "discount_percent": 10.0, "das": 3500.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.76},
            {"monthly_payment": 579.0, "msrp": 72500.0, "selling_price": 65300.0,
             "discount_percent": 9.9, "das": 3200.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.80},
        ],
        "signals": ["$5.5k EV cash + stackable incentives", "55-day avg DOM, 40% price-reduced", "GM pushing work truck EV market share", "Competing with F-150 Lightning pricing"],
    },
    {
        "vehicle": {"make": "Cadillac", "model": "Lyriq", "trim": "Luxury", "year": 2025, "category": "Luxury"},
        "lease_program": {
            "residual_percent": 58.0, "money_factor": 0.00060, "lease_cash": 6000.0,
            "loyalty_cash": 2000.0, "conquest_cash": 1500.0, "term": 36, "mileage": 10000,
            "source": "GM Financial / Leasehackr forums",
        },
        "inventory": {
            "inventory_count": 1900, "avg_days_on_market": 44.0,
            "price_reduction_count": 570, "dealer_count": 900,
        },
        "deals": [
            {"monthly_payment": 499.0, "msrp": 65800.0, "selling_price": 59600.0,
             "discount_percent": 9.4, "das": 3200.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 0.76},
            {"monthly_payment": 529.0, "msrp": 66500.0, "selling_price": 60200.0,
             "discount_percent": 9.5, "das": 3000.0, "term": 36, "mileage": 10000,
             "region": "TX", "leasehackr_score": 0.80},
            {"monthly_payment": 479.0, "msrp": 65200.0, "selling_price": 59000.0,
             "discount_percent": 9.5, "das": 3400.0, "term": 36, "mileage": 10000,
             "region": "FL", "leasehackr_score": 0.73},
        ],
        "signals": ["58% residual — best in luxury EV class", "$6k cash + $3.5k loyalty/conquest", "Cadillac EV push subsidized by GM", "44-day DOM, 30% price-reduced"],
    },
]


def run_seed(db: Session) -> None:
    from app.models.vehicle import Vehicle
    from app.models.lease_program import LeaseProgram
    from app.models.inventory import InventoryMetric
    from app.models.deal_evidence import DealEvidence
    from app.models.score import HackabilityScore
    from app.agents.hackability_ranking import compute_hackability_score

    if db.query(Vehicle).count() > 0:
        log.info("Seed data already present — skipping.")
        return

    log.info("Seeding historical winners...")
    now = datetime.utcnow()
    today = date.today()

    for entry in SEED_DATA:
        v_data = entry["vehicle"]
        vehicle = Vehicle(**v_data)
        db.add(vehicle)
        db.flush()  # get vehicle.id

        lp_data = entry["lease_program"]
        lp = LeaseProgram(
            vehicle_id=vehicle.id,
            program_month=now.month,
            program_year=now.year,
            **lp_data,
        )
        db.add(lp)

        inv_data = entry["inventory"]
        im = InventoryMetric(
            vehicle_id=vehicle.id,
            region="National",
            recorded_date=today,
            source="seed/historical",
            **inv_data,
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

        # Compute and store hackability score using the live engine
        compute_hackability_score(vehicle.id, db)
        log.info("Seeded: %s %s %s", vehicle.year, vehicle.make, vehicle.model)

    log.info("Seeding complete — %d vehicles loaded.", len(SEED_DATA))
