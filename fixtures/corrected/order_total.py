"""Labelled corrected rehearsal candidate, not a live agent-generated patch."""

from decimal import Decimal, ROUND_HALF_UP


def order_total(unit_price: str, quantity: int, discount_percent: str = "0") -> str:
    price, discount = Decimal(unit_price), Decimal(discount_percent)
    if not price.is_finite() or not discount.is_finite():
        raise ValueError("Values must be finite")
    if price < 0 or type(quantity) is not int or quantity < 0 or not 0 <= discount <= 100:
        raise ValueError("Invalid order")
    total = price * quantity * (1 - discount / 100)
    return str(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
