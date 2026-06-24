"""
Seed database with Seattle-area lease targets.
Idempotent per vehicle and per (vehicle_id, term, program_month, program_year).

Incentive notes:
  lease_cash   — manufacturer lease support or EV federal credit pass-through; UNIVERSAL
  conquest_cash— requires owning a non-brand vehicle; conditional
  loyalty_cash — requires current/prior brand ownership; conditional
  military_cash— active duty, NG, reservists, or veterans within published window; conditional
  costco_cash  — Costco Auto Program pre-negotiated cap cost reduction; conditional
"""
from __future__ import annotations

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

WA_TAX_RATE = 10.4

_EV_NOTES_KIA = (
    "WA sales tax ~10.4%. Lease cash = federal $7,500 EV credit + Kia manufacturer support; "
    "total varies by trim ($12,600–$13,000). Source: Edmunds forums June 2026, zip 98033 (Kirkland WA). "
    "Conquest requires non-Kia/non-Hyundai ownership. "
    "Loyalty requires current/prior Kia ownership. "
    "Military requires active duty, NG/Reserves, or separation within 24 months. "
    "Costco Auto Program: ~$1,000 cap cost reduction at participating dealers."
)
_EV_NOTES_HYU = (
    "WA sales tax ~10.4%. Lease cash = federal $7,500 EV credit passed through by HMF. "
    "Conquest requires non-Kia/non-Hyundai ownership. "
    "Loyalty requires current/prior Hyundai ownership. "
    "Military requires active duty or separation within 12 months (stricter than Kia). "
    "Costco Auto Program: ~$500 cap cost reduction at participating dealers."
)
_MIN_NOTES = (
    "WA sales tax ~10.4%. No EV credit. Higher MF than EV programs. "
    "Conquest requires non-Kia ownership. Loyalty requires current/prior Kia. "
    "Military requires active duty, NG/Reserves, or separation within 24 months. "
    "Costco Auto Program: ~$750 cap cost reduction at participating dealers."
)
_MIN_HEV_NOTES = (
    "WA sales tax ~10.4%. No federal EV credit on standard lease. "
    "WA $2,500 clean vehicle rebate applies on purchase only. "
    "Conquest requires non-Kia ownership. Loyalty requires current/prior Kia. "
    "Military requires active duty, NG/Reserves, or separation within 24 months. "
    "Costco Auto Program: ~$750 cap cost reduction at participating dealers."
)

# incentive_config is merged into every lease_program for that vehicle.
# lease_program-specific keys (term, mileage, residual_percent, money_factor,
# lease_cash, loyalty_cash, conquest_cash, source, regional_notes) override config defaults.
# costco_cash and military_cash live here to avoid repeating across all term rows.

SEED_DATA = [
    # ── Kia EV9 Light ───────────────────────────────────────────────────────
    # Base trim; program data estimated from Wind pattern (screenshot showed Wind/Land/GT-Line only)
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "Light", "year": 2026, "category": "EV",
        },
        "incentive_config": {
            "costco_cash": 1000.0,
            "military_cash": 500.0,   # active duty / NG / <24mo post-separation
        },
        "lease_programs": [
            {"term": 18, "mileage": 10000, "base_msrp": 57595.0,
             "residual_percent": 68.0, "money_factor": 0.00194,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Kia Motor Finance / Edmunds forums Jun 2026 zip 98033 (estimated from Wind)", "regional_notes": _EV_NOTES_KIA},
            {"term": 24, "mileage": 10000, "base_msrp": 57595.0,
             "residual_percent": 64.0, "money_factor": 0.00194,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Kia Motor Finance / Edmunds forums Jun 2026 zip 98033 (estimated from Wind)", "regional_notes": _EV_NOTES_KIA},
            {"term": 36, "mileage": 10000, "base_msrp": 57595.0,
             "residual_percent": 56.0, "money_factor": 0.00194,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Kia Motor Finance / Edmunds forums Jun 2026 zip 98033 (estimated from Wind)", "regional_notes": _EV_NOTES_KIA},
            {"term": 48, "mileage": 10000, "base_msrp": 57595.0,
             "residual_percent": 48.0, "money_factor": 0.00220,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Kia Motor Finance / Edmunds forums Jun 2026 zip 98033 (estimated from Wind)", "regional_notes": _EV_NOTES_KIA},
        ],
        "inventory": {
            "inventory_count": 35, "avg_days_on_market": 38.0,
            "price_reduction_count": 11, "dealer_count": 6,
        },
        "deals": [],
        "signals": [
            "$13,000 lease cash (estimated) + $500 conquest + $1,000 Costco = $14,500 best case",
            "Entry-level EV9 — broadest buyer pool",
            "68% residual on 18mo exceptional for short-term flip",
        ],
    },

    # ── Kia EV9 Wind ────────────────────────────────────────────────────────
    # Confirmed: MF 0.00194, RV 66% at 24/12mo, $13,000 lease cash (Edmunds zip 98033 Jun 2026)
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "Wind", "year": 2026, "category": "EV",
        },
        "incentive_config": {
            "costco_cash": 1000.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 10000, "base_msrp": 64895.0,
             "residual_percent": 70.0, "money_factor": 0.00194,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 24, "mileage": 10000, "base_msrp": 64895.0,
             "residual_percent": 66.0, "money_factor": 0.00194,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 36, "mileage": 10000, "base_msrp": 64895.0,
             "residual_percent": 58.0, "money_factor": 0.00194,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 48, "mileage": 10000, "base_msrp": 64895.0,
             "residual_percent": 50.0, "money_factor": 0.00220,
             "lease_cash": 13000.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
        ],
        "inventory": {
            "inventory_count": 48, "avg_days_on_market": 34.0,
            "price_reduction_count": 16, "dealer_count": 6,
        },
        "deals": [
            {"monthly_payment": 765.0, "msrp": 64200.0, "selling_price": 59900.0,
             "discount_percent": 6.7, "das": 3000.0, "term": 36, "mileage": 10000,
             "region": "WA", "leasehackr_score": 1.19},
            {"monthly_payment": 749.0, "msrp": 63400.0, "selling_price": 59000.0,
             "discount_percent": 6.9, "das": 3200.0, "term": 36, "mileage": 10000,
             "region": "WA", "leasehackr_score": 1.18},
        ],
        "signals": [
            "MF 0.00194 = 4.66% APR equiv; 66% RV at 24mo confirmed WA Jun 2026",
            "$13,000 lease cash + $500 conquest + $1,000 Costco = $14,500 best case",
            "6–7% dealer discount achievable in PNW",
        ],
    },

    # ── Kia EV9 Land (AWD) ──────────────────────────────────────────────────
    # Confirmed: MF 0.00192, RV 65% at 24/12mo, $12,700 lease cash (Edmunds zip 98033 Jun 2026)
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "Land", "year": 2026, "category": "EV",
        },
        "incentive_config": {
            "costco_cash": 1000.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 10000, "base_msrp": 67895.0,
             "residual_percent": 69.0, "money_factor": 0.00192,
             "lease_cash": 12700.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 24, "mileage": 10000, "base_msrp": 67895.0,
             "residual_percent": 65.0, "money_factor": 0.00192,
             "lease_cash": 12700.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 36, "mileage": 10000, "base_msrp": 67895.0,
             "residual_percent": 57.0, "money_factor": 0.00192,
             "lease_cash": 12700.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 48, "mileage": 10000, "base_msrp": 67895.0,
             "residual_percent": 49.0, "money_factor": 0.00220,
             "lease_cash": 12700.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
        ],
        "inventory": {
            "inventory_count": 28, "avg_days_on_market": 31.0,
            "price_reduction_count": 9, "dealer_count": 5,
        },
        "deals": [],
        "signals": [
            "AWD trim — 65% RV at 24mo confirmed WA Jun 2026; 1pt lower than Wind",
            "$12,700 lease cash + $500 conquest + $1,000 Costco = $14,200 best case",
        ],
    },

    # ── Kia EV9 GT-Line ─────────────────────────────────────────────────────
    # Confirmed: MF 0.00194, RV 66% at 24/12mo, $12,600 lease cash (Edmunds zip 98033 Jun 2026)
    {
        "vehicle": {
            "make": "Kia", "model": "EV9", "trim": "GT-Line", "year": 2026, "category": "EV",
        },
        "incentive_config": {
            "costco_cash": 1000.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 10000, "base_msrp": 69895.0,
             "residual_percent": 70.0, "money_factor": 0.00194,
             "lease_cash": 12600.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 24, "mileage": 10000, "base_msrp": 69895.0,
             "residual_percent": 66.0, "money_factor": 0.00194,
             "lease_cash": 12600.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
            {"term": 36, "mileage": 10000, "base_msrp": 69895.0,
             "residual_percent": 58.0, "money_factor": 0.00194,
             "lease_cash": 12600.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Edmunds forums Jun 2026 zip 98033 (Kirkland WA)", "regional_notes": _EV_NOTES_KIA},
        ],
        "inventory": {
            "inventory_count": 15, "avg_days_on_market": 24.0,
            "price_reduction_count": 4, "dealer_count": 4,
        },
        "deals": [],
        "signals": [
            "Top EV9 — 66% RV at 24mo matches Wind despite higher MSRP",
            "No 48mo program; limited PNW inventory",
            "$12,600 lease cash + $500 conquest + $1,000 Costco = $14,100 best case",
        ],
    },

    # ── Hyundai Ioniq 9 SE Long Range ───────────────────────────────────────
    {
        "vehicle": {
            "make": "Hyundai", "model": "Ioniq 9", "trim": "SE Long Range", "year": 2025, "category": "EV",
        },
        "incentive_config": {
            "costco_cash": 500.0,
            "military_cash": 500.0,   # Hyundai: active duty or <12mo post-separation
        },
        "lease_programs": [
            {"term": 18, "mileage": 10000, "base_msrp": 62995.0,
             "residual_percent": 64.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 24, "mileage": 10000, "base_msrp": 62995.0,
             "residual_percent": 60.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 36, "mileage": 10000, "base_msrp": 62995.0,
             "residual_percent": 52.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 48, "mileage": 10000, "base_msrp": 62995.0,
             "residual_percent": 44.0, "money_factor": 0.00135,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
        ],
        "inventory": {
            "inventory_count": 22, "avg_days_on_market": 18.0,
            "price_reduction_count": 3, "dealer_count": 5,
        },
        "deals": [
            {"monthly_payment": 642.0, "msrp": 63400.0, "selling_price": 61500.0,
             "discount_percent": 3.0, "das": 3500.0, "term": 36, "mileage": 10000,
             "region": "WA", "leasehackr_score": 1.01},
            {"monthly_payment": 658.0, "msrp": 64000.0, "selling_price": 62100.0,
             "discount_percent": 3.0, "das": 3200.0, "term": 36, "mileage": 10000,
             "region": "CA", "leasehackr_score": 1.03},
        ],
        "signals": [
            "MF 0.00115 = 2.76% APR — best money factor in the lineup",
            "$7,500 EV credit + $500 conquest + $500 Costco = $8,500 for conquest+Costco buyer",
            "52% residual at 36mo — best in class for new EV launch",
            "64% residual on 18mo = exceptional",
        ],
    },

    # ── Hyundai Ioniq 9 SEL ─────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Hyundai", "model": "Ioniq 9", "trim": "SEL", "year": 2025, "category": "EV",
        },
        "incentive_config": {
            "costco_cash": 500.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 10000, "base_msrp": 68995.0,
             "residual_percent": 62.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 24, "mileage": 10000, "base_msrp": 68995.0,
             "residual_percent": 58.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 36, "mileage": 10000, "base_msrp": 68995.0,
             "residual_percent": 50.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 48, "mileage": 10000, "base_msrp": 68995.0,
             "residual_percent": 42.0, "money_factor": 0.00135,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
        ],
        "inventory": {
            "inventory_count": 14, "avg_days_on_market": 16.0,
            "price_reduction_count": 2, "dealer_count": 4,
        },
        "deals": [],
        "signals": [
            "Mid-tier Ioniq 9 — same low MF as SE",
            "$7,500 EV credit + $500 conquest + $500 Costco = $8,500",
        ],
    },

    # ── Hyundai Ioniq 9 Limited ─────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Hyundai", "model": "Ioniq 9", "trim": "Limited", "year": 2025, "category": "EV",
        },
        "incentive_config": {
            "costco_cash": 500.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 10000, "base_msrp": 76995.0,
             "residual_percent": 60.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 24, "mileage": 10000, "base_msrp": 76995.0,
             "residual_percent": 56.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
            {"term": 36, "mileage": 10000, "base_msrp": 76995.0,
             "residual_percent": 48.0, "money_factor": 0.00115,
             "lease_cash": 7500.0, "loyalty_cash": 1000.0, "conquest_cash": 500.0,
             "source": "Hyundai Motor Finance / Leasehackr", "regional_notes": _EV_NOTES_HYU},
        ],
        "inventory": {
            "inventory_count": 8, "avg_days_on_market": 12.0,
            "price_reduction_count": 1, "dealer_count": 3,
        },
        "deals": [],
        "signals": [
            "Top-spec Ioniq 9 — 48% residual weakest in lineup",
            "No 48mo program available",
            "Very limited PNW inventory",
        ],
    },

    # ── Kia Carnival LX ─────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival", "trim": "LX", "year": 2025, "category": "Minivan",
        },
        "incentive_config": {
            "costco_cash": 750.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 12000, "base_msrp": 35995.0,
             "residual_percent": 63.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 24, "mileage": 12000, "base_msrp": 35995.0,
             "residual_percent": 59.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 36, "mileage": 12000, "base_msrp": 35995.0,
             "residual_percent": 55.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 48, "mileage": 12000, "base_msrp": 35995.0,
             "residual_percent": 47.0, "money_factor": 0.00250,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
        ],
        "inventory": {
            "inventory_count": 75, "avg_days_on_market": 32.0,
            "price_reduction_count": 22, "dealer_count": 6,
        },
        "deals": [],
        "signals": [
            "Entry Carnival — best residual at 55% (36mo)",
            "No conquest cash on Carnival; Costco $750 replaces it for Costco buyers",
            "75 Seattle-area units — strong dealer leverage",
        ],
    },

    # ── Kia Carnival EX ─────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival", "trim": "EX", "year": 2025, "category": "Minivan",
        },
        "incentive_config": {
            "costco_cash": 750.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 12000, "base_msrp": 42495.0,
             "residual_percent": 61.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 24, "mileage": 12000, "base_msrp": 42495.0,
             "residual_percent": 57.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 36, "mileage": 12000, "base_msrp": 42495.0,
             "residual_percent": 53.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 48, "mileage": 12000, "base_msrp": 42495.0,
             "residual_percent": 45.0, "money_factor": 0.00250,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
        ],
        "inventory": {
            "inventory_count": 87, "avg_days_on_market": 28.0,
            "price_reduction_count": 26, "dealer_count": 6,
        },
        "deals": [
            {"monthly_payment": 595.0, "msrp": 43200.0, "selling_price": 40900.0,
             "discount_percent": 5.3, "das": 2500.0, "term": 36, "mileage": 12000,
             "region": "WA", "leasehackr_score": 1.38},
            {"monthly_payment": 580.0, "msrp": 42495.0, "selling_price": 40200.0,
             "discount_percent": 5.4, "das": 2800.0, "term": 36, "mileage": 12000,
             "region": "WA", "leasehackr_score": 1.37},
            {"monthly_payment": 610.0, "msrp": 44100.0, "selling_price": 41700.0,
             "discount_percent": 5.4, "das": 2300.0, "term": 36, "mileage": 12000,
             "region": "WA", "leasehackr_score": 1.38},
        ],
        "signals": [
            "87 Seattle-area units — highest inventory in lineup",
            "No conquest cash; Costco $750 is primary conditional incentive",
            "5–6% dealer discount achievable beyond Costco price",
        ],
    },

    # ── Kia Carnival SX ─────────────────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival", "trim": "SX", "year": 2025, "category": "Minivan",
        },
        "incentive_config": {
            "costco_cash": 750.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 60.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 24, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 56.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 36, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 52.0, "money_factor": 0.00230,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
            {"term": 48, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 44.0, "money_factor": 0.00250,
             "lease_cash": 1500.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_NOTES},
        ],
        "inventory": {
            "inventory_count": 62, "avg_days_on_market": 25.0,
            "price_reduction_count": 18, "dealer_count": 6,
        },
        "deals": [],
        "signals": [
            "Top gas Carnival — 52% residual at 36mo",
            "No conquest cash on gas Carnival lineup",
        ],
    },

    # ── Kia Carnival Hybrid EX HEV ──────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival Hybrid", "trim": "EX HEV", "year": 2025, "category": "Minivan",
        },
        "incentive_config": {
            "costco_cash": 750.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 63.0, "money_factor": 0.00215,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
            {"term": 24, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 59.0, "money_factor": 0.00215,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
            {"term": 36, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 55.0, "money_factor": 0.00215,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
            {"term": 48, "mileage": 12000, "base_msrp": 46495.0,
             "residual_percent": 47.0, "money_factor": 0.00235,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
        ],
        "inventory": {
            "inventory_count": 54, "avg_days_on_market": 33.0,
            "price_reduction_count": 19, "dealer_count": 6,
        },
        "deals": [
            {"monthly_payment": 564.0, "msrp": 47200.0, "selling_price": 44600.0,
             "discount_percent": 5.5, "das": 2800.0, "term": 36, "mileage": 12000,
             "region": "WA", "leasehackr_score": 1.20},
            {"monthly_payment": 578.0, "msrp": 47800.0, "selling_price": 45200.0,
             "discount_percent": 5.4, "das": 2600.0, "term": 36, "mileage": 12000,
             "region": "WA", "leasehackr_score": 1.21},
        ],
        "signals": [
            "55% residual at 36mo — 2pts better than gas Carnival EX",
            "Costco $750 only conditional incentive for conquest buyers",
            "54 Seattle-area units, 33-day avg DOM",
        ],
    },

    # ── Kia Carnival Hybrid SX HEV ──────────────────────────────────────────
    {
        "vehicle": {
            "make": "Kia", "model": "Carnival Hybrid", "trim": "SX HEV", "year": 2025, "category": "Minivan",
        },
        "incentive_config": {
            "costco_cash": 750.0,
            "military_cash": 500.0,
        },
        "lease_programs": [
            {"term": 18, "mileage": 12000, "base_msrp": 50395.0,
             "residual_percent": 61.0, "money_factor": 0.00215,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
            {"term": 24, "mileage": 12000, "base_msrp": 50395.0,
             "residual_percent": 57.0, "money_factor": 0.00215,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
            {"term": 36, "mileage": 12000, "base_msrp": 50395.0,
             "residual_percent": 53.0, "money_factor": 0.00215,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
            {"term": 48, "mileage": 12000, "base_msrp": 50395.0,
             "residual_percent": 45.0, "money_factor": 0.00235,
             "lease_cash": 2000.0, "loyalty_cash": 750.0, "conquest_cash": 0.0,
             "source": "Kia Motor Finance / Edmunds forums", "regional_notes": _MIN_HEV_NOTES},
        ],
        "inventory": {
            "inventory_count": 38, "avg_days_on_market": 28.0,
            "price_reduction_count": 11, "dealer_count": 5,
        },
        "deals": [],
        "signals": [
            "Top Carnival Hybrid — $2,000 lease cash unchanged vs EX HEV",
            "53% residual at 36mo",
        ],
    },
]


def run_seed(db: Session) -> None:
    from app.models.vehicle import Vehicle
    from app.models.lease_program import LeaseProgram
    from app.models.inventory import InventoryMetric
    from app.models.deal_evidence import DealEvidence
    from app.models.score import HackabilityScore
    from app.agents.hackability_ranking import compute_hackability_score

    now = datetime.utcnow()
    today = date.today()
    vehicles_touched = []

    # Remove stale 2025 EV9 records superseded by 2026 model year data.
    # Also handles trim renames: "Wind RWD"→"Wind", "Wind AWD"→"Land", "GT-Line RWD"→"GT-Line".
    _stale_ev9 = [
        ("Kia", "EV9", "Light Long Range", 2025),
        ("Kia", "EV9", "Wind RWD", 2025),
        ("Kia", "EV9", "Wind AWD", 2025),
        ("Kia", "EV9", "GT-Line RWD", 2025),
    ]
    for make, model, trim, year in _stale_ev9:
        old_v = db.query(Vehicle).filter(
            Vehicle.make == make, Vehicle.model == model,
            Vehicle.trim == trim, Vehicle.year == year,
        ).first()
        if old_v:
            db.query(HackabilityScore).filter(HackabilityScore.vehicle_id == old_v.id).delete()
            db.query(LeaseProgram).filter(LeaseProgram.vehicle_id == old_v.id).delete()
            db.query(InventoryMetric).filter(InventoryMetric.vehicle_id == old_v.id).delete()
            db.query(DealEvidence).filter(DealEvidence.vehicle_id == old_v.id).delete()
            db.delete(old_v)
            log.info("Removed stale vehicle: %d %s %s %s", year, make, model, trim)
    db.commit()

    for entry in SEED_DATA:
        v_data = entry["vehicle"]
        incentive_cfg = entry.get("incentive_config", {})

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

        # Lease programs: idempotent per (vehicle, term, month, year).
        # Always update cash fields so new incentives (Costco, military) populate on re-run.
        for lp_data in entry.get("lease_programs", []):
            # Merge vehicle-level incentive_config, then program-specific keys override
            full_data = {**incentive_cfg, **lp_data}
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
                    **full_data,
                )
                db.add(lp)
            else:
                # Update incentive fields in case they've been added or changed
                for field in ("lease_cash", "loyalty_cash", "conquest_cash",
                              "military_cash", "costco_cash", "college_cash"):
                    if field in full_data:
                        setattr(existing_lp, field, full_data[field])

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

        # Insert deals only if none exist yet
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
