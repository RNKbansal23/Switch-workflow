# Order-total demonstration contract

This deliberately broken baseline ignores the discount. The incomplete and corrected candidates in `fixtures/` are labelled rehearsal inputs.

`order_total(unit_price: str, quantity: int, discount_percent: str = "0") -> str` calculates the order subtotal and applies a percentage discount using exact decimal arithmetic. Round the final result once to two places with ROUND_HALF_UP. Reject negative prices, non-integer/negative quantities, non-finite inputs, and discounts outside 0–100 with ValueError.

Examples: `10.05 × 1` less `10%` is `9.05`; `10.04 × 1` less `10%` is `9.04`; `12.50 × 2` without discount is `25.00`. Tax, currencies, shipping, and line-item rounding are outside this sample contract.

The trusted acceptance runner lives outside the candidate repository. Changing candidate-owned tests cannot make its checks pass.
