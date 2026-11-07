"""Intentionally broken baseline for the ProofDesk demonstration.

This fixture ignores discounts. It is not the implementation to ship.
"""

from decimal import Decimal, ROUND_HALF_UP


def order_total(unit_price: str, quantity: int, discount_percent: str = "0") -> str:
    price, discount = Decimal(unit_price), Decimal(discount_percent)
    if not price.is_finite() or not discount.is_finite():
        raise ValueError("Values must be finite")
    if price < 0 or type(quantity) is not int or quantity < 0 or not 0 <= discount <= 100:
        raise ValueError("Invalid order")
    return str((price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
