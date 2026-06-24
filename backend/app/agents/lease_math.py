"""Agent 5: Lease Math Engine — pure arithmetic, no AI."""


def calculate_monthly_payment(
    msrp: float,
    selling_price: float,
    residual_percent: float,
    money_factor: float,
    term: int,
    das: float = 0.0,
    lease_cash: float = 0.0,
    tax_rate: float = 0.0,
) -> float:
    """Standard capitalized-cost lease payment formula."""
    residual_value = msrp * (residual_percent / 100.0)
    adjusted_cap_cost = selling_price - lease_cash
    # DAS reduces cap cost only if it's a cap reduction (not drive-off fees).
    # For simplicity treat DAS = cap reduction here.
    depreciation = (adjusted_cap_cost - residual_value) / term
    finance_charge = (adjusted_cap_cost + residual_value) * money_factor
    base = depreciation + finance_charge
    return round(base * (1 + tax_rate / 100.0), 2)


def calculate_lh_score(monthly_payment: float, msrp: float) -> float:
    """Leasehackr score: monthly / (MSRP / 1000). Lower is better; 0.8% is excellent."""
    if msrp <= 0:
        return 0.0
    return round(monthly_payment / (msrp / 1000.0), 2)


def calculate_effective_monthly(monthly_payment: float, das: float, term: int) -> float:
    """Amortize due-at-signing across the term to get true cost per month."""
    if term <= 0:
        return monthly_payment
    return round(monthly_payment + (das / term), 2)


def build_scenario(
    msrp: float,
    discount_percent: float,
    residual_percent: float,
    money_factor: float,
    term: int = 36,
    mileage: int = 10000,
    lease_cash: float = 0.0,
    das: float = 1500.0,
    tax_rate: float = 0.0,
) -> dict:
    selling_price = msrp * (1 - discount_percent / 100.0)
    monthly = calculate_monthly_payment(
        msrp, selling_price, residual_percent, money_factor, term, das, lease_cash, tax_rate
    )
    effective = calculate_effective_monthly(monthly, das, term)
    lh_score = calculate_lh_score(monthly, msrp)
    return {
        "msrp": msrp,
        "selling_price": round(selling_price, 2),
        "discount_percent": discount_percent,
        "residual_percent": residual_percent,
        "money_factor": money_factor,
        "term": term,
        "mileage": mileage,
        "lease_cash": lease_cash,
        "das": das,
        "monthly_payment": monthly,
        "effective_monthly": effective,
        "lh_score": lh_score,
    }
