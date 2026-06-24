"""
Seed database with Seattle-area lease targets.
Idempotent per vehicle and per (vehicle_id, term, program_month, program_year).
"""
from __future__ import annotations

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

WA_TAX_RATE = 10.4

_EV_NOTES_KIA = (
    "WA sales tax ~10.4%. Federal $7,500 EV credit passed through by KMMAF. "
    "No additional WA state EV lease rebate."
)
_EV_NOTES_HYU = (
    "WA sales tax ~10.4%. Federal $7,500 EV credit passed through by HMF. "
    "No additional WA state EV lease rebate."
)
_MIN_NOTES = (
    "WA sales tax ~10.4%. No EV credit. "
    "Higher MF relative to EV programs — consider buying if financing."
)
_MIN_HEV_NOTES = (
    "WA sales tax ~10.4%. No federal EV credit on standard lease. "
    "WA state $2,500 clean vehicle rebate applies on purchase only."
)

SEED_DATA = [
    # ── Kia EV9 Light Long Range ─────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "Light Long Range", "year": 2025, "category": "EV",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 10000, "base_msrp": 56395.0,
                "residual_percent": 62.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 24, "mileage": 10000, "base_msrp": 56395.0,
                "residual_percent": 58.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 36, "mileage": 10000, "base_msrp": 56395.0,
                "residual_percent": 50.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 48, "mileage": 10000, "base_msrp": 56395.0,
                "residual_percent": 42.0, "money_factor": 0.00195,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
        ],
        "inventory": {
            "inventory_count": 35, "avg_days_on_market": 38.0,
            "price_reduction_count": 11, "dealer_count": 6,
        },
        "deals": [],
        "signals": [
            "$7,500 federal EV credit via KMMAF",
            "Entry-level EV9 — broadest buyer pool",
            "58% residual on 24mo is class-leading short term",
            "35 Seattle-area units, motivated dealers on lot age",
        ],
    },

    # ── Kia EV9 Wind RWD ────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "Wind RWD", "year": 2025, "category": "EV",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 10000, "base_msrp": 63400.0,
                "residual_percent": 60.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 24, "mileage": 10000, "base_msrp": 63400.0,
                "residual_percent": 56.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 36, "mileage": 10000, "base_msrp": 63400.0,
                "residual_percent": 48.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 48, "mileage": 10000, "base_msrp": 63400.0,
                "residual_percent": 40.0, "money_factor": 0.00195,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
        ],
        "inventory": {
            "inventory_count": 48, "avg_days_on_market": 34.0,
            "price_reduction_count": 16, "dealer_count": 6,
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
            "$7,500 federal EV credit via KMMAF",
            "48 units within 100mi of Seattle",
            "MF 0.00175 = 4.2% APR equiv",
            "6–7% dealer discount achievable in PNW",
        ],
    },

    # ── Kia EV9 Wind AWD ────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "Wind AWD", "year": 2025, "category": "EV",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 10000, "base_msrp": 65400.0,
                "residual_percent": 59.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 24, "mileage": 10000, "base_msrp": 65400.0,
                "residual_percent": 55.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 36, "mileage": 10000, "base_msrp": 65400.0,
                "residual_percent": 47.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 48, "mileage": 10000, "base_msrp": 65400.0,
                "residual_percent": 39.0, "money_factor": 0.00195,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
        ],
        "inventory": {
            "inventory_count": 28, "avg_days_on_market": 31.0,
            "price_reduction_count": 9, "dealer_count": 5,
        },
        "deals": [],
        "signals": [
            "AWD premium over Wind RWD — ~$2k higher MSRP",
            "1-point lower residual vs. RWD — slightly worse program",
            "$7,500 EV credit applies equally across all EV9 trims",
            "28 Seattle-area units",
        ],
    },

    # ── Kia EV9 GT-Line RWD ─────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "GT-Line RWD", "year": 2025, "category": "EV",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 10000, "base_msrp": 67400.0,
                "residual_percent": 58.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 24, "mileage": 10000, "base_msrp": 67400.0,
                "residual_percent": 54.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
            {
                "term": 36, "mileage": 10000, "base_msrp": 67400.0,
                "residual_percent": 46.0, "money_factor": 0.00175,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _EV_NOTES_KIA,
            },
        ],
        "inventory": {
            "inventory_count": 15, "avg_days_on_market": 24.0,
            "price_reduction_count": 4, "dealer_count": 4,
        },
        "deals": [],
        "signals": [
            "Top trim — residual falls to 46% at 36mo (worst in EV9 lineup)",
            "No 48mo program available",
            "Limited PNW inventory reduces discount leverage",
            "$7,500 EV credit still applies",
        ],
    },

    # ── Hyundai Ioniq 9 SE Long Range ───────────────────────────────────────
    {
        "vehicle": {
            "make": "Hyundai", "model": "Ioniq 9", "trim": "SE Long Range", "year": 2025, "category": "EV",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 10000, "base_msrp": 62995.0,
                "residual_percent": 64.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 24, "mileage": 10000, "base_msrp": 62995.0,
                "residual_percent": 60.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 36, "mileage": 10000, "base_msrp": 62995.0,
                "residual_percent": 52.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 48, "mileage": 10000, "base_msrp": 62995.0,
                "residual_percent": 44.0, "money_factor": 0.00135,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
        ],
        "inventory": {
            "inventory_count": 22, "avg_days_on_market": 18.0,
            "price_reduction_count": 3, "dealer_count": 5,
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
            "52% residual at 36mo — best in class for new EV launch",
            "60% residual on 24mo = exceptional short-term value",
        ],
    },

    # ── Hyundai Ioniq 9 SEL ─────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Hyundai", "model": "Ioniq 9", "trim": "SEL", "year": 2025, "category": "EV",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 10000, "base_msrp": 68995.0,
                "residual_percent": 62.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 24, "mileage": 10000, "base_msrp": 68995.0,
                "residual_percent": 58.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 36, "mileage": 10000, "base_msrp": 68995.0,
                "residual_percent": 50.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 48, "mileage": 10000, "base_msrp": 68995.0,
                "residual_percent": 42.0, "money_factor": 0.00135,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
        ],
        "inventory": {
            "inventory_count": 14, "avg_days_on_market": 16.0,
            "price_reduction_count": 2, "dealer_count": 4,
        },
        "deals": [],
        "signals": [
            "Mid-tier Ioniq 9 — more features, same lease program structure",
            "50% residual at 36mo — still competitive for the class",
            "MF 0.00115 = 2.76% APR — lowest money factor in segment",
            "Limited PNW inventory at launch",
        ],
    },

    # ── Hyundai Ioniq 9 Limited ─────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Hyundai", "model": "Ioniq 9", "trim": "Limited", "year": 2025, "category": "EV",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 10000, "base_msrp": 76995.0,
                "residual_percent": 60.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 24, "mileage": 10000, "base_msrp": 76995.0,
                "residual_percent": 56.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
            {
                "term": 36, "mileage": 10000, "base_msrp": 76995.0,
                "residual_percent": 48.0, "money_factor": 0.00115,
                "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
                "source": "Hyundai Motor Finance / Leasehackr",
                "regional_notes": _EV_NOTES_HYU,
            },
        ],
        "inventory": {
            "inventory_count": 8, "avg_days_on_market": 12.0,
            "price_reduction_count": 1, "dealer_count": 3,
        },
        "deals": [],
        "signals": [
            "Top-spec Ioniq 9 — highest MSRP reduces $/feature value",
            "48% residual at 36mo — weakest in Ioniq 9 lineup",
            "No 48mo program available on Limited",
            "Very limited PNW inventory — strong dealer price hold",
        ],
    },

    # ── Kia Carnival LX ─────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival", "trim": "LX", "year": 2025, "category": "Minivan",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 12000, "base_msrp": 35995.0,
                "residual_percent": 63.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 24, "mileage": 12000, "base_msrp": 35995.0,
                "residual_percent": 59.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 36, "mileage": 12000, "base_msrp": 35995.0,
                "residual_percent": 55.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 48, "mileage": 12000, "base_msrp": 35995.0,
                "residual_percent": 47.0, "money_factor": 0.00250,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
        ],
        "inventory": {
            "inventory_count": 75, "avg_days_on_market": 32.0,
            "price_reduction_count": 22, "dealer_count": 6,
        },
        "deals": [],
        "signals": [
            "Entry Carnival — best price/payment ratio in minivan segment",
            "55% residual at 36mo — highest in the Carnival gas lineup",
            "75 Seattle-area units — significant dealer leverage",
            "No 24mo program available",
        ],
    },

    # ── Kia Carnival EX ─────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival", "trim": "EX", "year": 2025, "category": "Minivan",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 12000, "base_msrp": 42495.0,
                "residual_percent": 61.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 24, "mileage": 12000, "base_msrp": 42495.0,
                "residual_percent": 57.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 36, "mileage": 12000, "base_msrp": 42495.0,
                "residual_percent": 53.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 48, "mileage": 12000, "base_msrp": 42495.0,
                "residual_percent": 45.0, "money_factor": 0.00250,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
        ],
        "inventory": {
            "inventory_count": 87, "avg_days_on_market": 28.0,
            "price_reduction_count": 26, "dealer_count": 6,
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

    # ── Kia Carnival SX ─────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival", "trim": "SX", "year": 2025, "category": "Minivan",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 60.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 24, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 56.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 36, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 52.0, "money_factor": 0.00230,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
            {
                "term": 48, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 44.0, "money_factor": 0.00250,
                "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_NOTES,
            },
        ],
        "inventory": {
            "inventory_count": 62, "avg_days_on_market": 25.0,
            "price_reduction_count": 18, "dealer_count": 6,
        },
        "deals": [],
        "signals": [
            "Top gas Carnival — MSRP similar to Carnival HEV EX",
            "52% residual at 36mo — slightly weaker than EX/LX",
            "62 Seattle-area units — moderate leverage",
        ],
    },

    # ── Kia Carnival Hybrid EX HEV ──────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival Hybrid", "trim": "EX HEV", "year": 2025, "category": "Minivan",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 63.0, "money_factor": 0.00215,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
            {
                "term": 24, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 59.0, "money_factor": 0.00215,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
            {
                "term": 36, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 55.0, "money_factor": 0.00215,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
            {
                "term": 48, "mileage": 12000, "base_msrp": 46495.0,
                "residual_percent": 47.0, "money_factor": 0.00235,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
        ],
        "inventory": {
            "inventory_count": 54, "avg_days_on_market": 33.0,
            "price_reduction_count": 19, "dealer_count": 6,
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
            "55% residual — 2 points better than gas Carnival EX",
            "MF 0.00215 = 5.16% APR — slightly better than gas trim",
            "$2,000 lease cash (vs. $1,500 on gas) plus loyalty",
            "54 Seattle-area units, 33-day avg DOM",
        ],
    },

    # ── Kia Carnival Hybrid SX HEV ──────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival Hybrid", "trim": "SX HEV", "year": 2025, "category": "Minivan",
        },
        "lease_programs": [
            {
                "term": 18, "mileage": 12000, "base_msrp": 50395.0,
                "residual_percent": 61.0, "money_factor": 0.00215,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
            {
                "term": 24, "mileage": 12000, "base_msrp": 50395.0,
                "residual_percent": 57.0, "money_factor": 0.00215,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
            {
                "term": 36, "mileage": 12000, "base_msrp": 50395.0,
                "residual_percent": 53.0, "money_factor": 0.00215,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
            {
                "term": 48, "mileage": 12000, "base_msrp": 50395.0,
                "residual_percent": 45.0, "money_factor": 0.00235,
                "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
                "source": "Kia Motor Finance / Edmunds forums",
                "regional_notes": _MIN_HEV_NOTES,
            },
        ],
        "inventory": {
            "inventory_count": 38, "avg_days_on_market": 28.0,
            "price_reduction_count": 11, "dealer_count": 5,
        },
        "deals": [],
        "signals": [
            "Top Carnival Hybrid — higher MSRP than EX HEV",
            "53% residual at 36mo — slightly lower than EX HEV",
            "$2,000 lease cash unchanged vs. EX HEV",
            "38 Seattle-area units",
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
    vehicles_touched = []

    for entry in SEED_DATA:
        v_data = entry["vehicle"]

        vehicle = (
            db.query(Vehicle)
            .filter(
                Vehicle.make == v_data["make"],
                Vehicle.model == v_data["model"],
                Vehicle.trim == v_data["trim"],
                Vehicle.year == v_data["year"],
            )
            .first()
        )
        if not vehicle:
            vehicle = Vehicle(**v_data)
            db.add(vehicle)
            db.flush()
            log.info("Created vehicle: %d %s %s %s", v_data["year"], v_data["make"], v_data["model"], v_data["trim"])

        # Insert any missing lease programs (idempotent per term + month/year)
        for lp_data in entry.get("lease_programs", []):
            existing_lp = (
                db.query(LeaseProgram)
                .filter(
                    LeaseProgram.vehicle_id == vehicle.id,
                    LeaseProgram.term == lp_data["term"],
                    LeaseProgram.program_month == now.month,
                    LeaseProgram.program_year == now.year,
                )
                .first()
            )
            if not existing_lp:
                lp = LeaseProgram(
                    vehicle_id=vehicle.id,
                    program_month=now.month,
                    program_year=now.year,
                    **lp_data,
                )
                db.add(lp)

        # Insert inventory if none exists for this vehicle
        if not db.query(InventoryMetric).filter(InventoryMetric.vehicle_id == vehicle.id).first():
            if entry.get("inventory"):
                im = InventoryMetric(
                    vehicle_id=vehicle.id,
                    region="Seattle Metro / Puget Sound",
                    recorded_date=today,
                    source="seed/market-research",
                    **entry["inventory"],
                )
                db.add(im)

        # Insert deals only if none exist yet for this vehicle
        if db.query(DealEvidence).filter(DealEvidence.vehicle_id == vehicle.id).count() == 0:
            for deal in entry.get("deals", []):
                de = DealEvidence(
                    vehicle_id=vehicle.id,
                    deal_date=today,
                    source="leasehackr/seed",
                    **deal,
                )
                db.add(de)

        db.commit()
        vehicles_touched.append(vehicle.id)

    for vid in vehicles_touched:
        compute_hackability_score(vid, db)

    log.info("Seed complete — %d vehicles processed.", len(vehicles_touched))
