"""Trusted acceptance policy run outside the candidate snapshot.

Candidate code still runs with the local user's privileges; this is not a sandbox.
"""

from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import sys

POLICY_VERSION = "order-total-v1"

# Expected values are literal business examples, not a duplicate of the algorithm.
CHECKS = [
    ("reported-rounding", ("10.05", 1, "10"), "9.05"),
    ("ordinary-discount", ("100.00", 1, "10"), "90.00"),
    ("no-discount", ("12.50", 2, "0"), "25.00"),
    ("round-down", ("10.04", 1, "10"), "9.04"),
    ("full-discount", ("19.99", 3, "100"), "0.00"),
    ("empty-order", ("12.50", 0, "10"), "0.00"),
]
INVALID = [
    ("negative-price", ("-1.00", 1, "0")),
    ("negative-quantity", ("1.00", -1, "0")),
    ("fractional-quantity", ("1.00", 1.5, "0")),
    ("excess-discount", ("1.00", 1, "101")),
    ("nonfinite-price", ("NaN", 1, "0")),
]
EXPECTED_IDS = [row[0] for row in CHECKS + INVALID]


def evaluate(snapshot):
    module_path = Path(snapshot) / "demo-app" / "order_total.py"
    spec = importlib.util.spec_from_file_location("proofdesk_candidate", module_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        return {"policy": POLICY_VERSION, "infrastructure_error": f"{type(exc).__name__}: {exc}", "checks": []}
    checks = []
    for name, arguments, expected in CHECKS:
        try:
            actual = module.order_total(*arguments)
            valid = isinstance(actual, str) and actual == expected
            checks.append({"id": name, "passed": valid, "expected": expected, "actual": str(actual), "kind": "assertion"})
        except Exception as exc:
            checks.append({"id": name, "passed": False, "kind": "error", "error": f"{type(exc).__name__}: {exc}"})
    for name, arguments in INVALID:
        try:
            actual = module.order_total(*arguments)
            checks.append({"id": name, "passed": False, "kind": "assertion", "actual": str(actual), "expected": "ValueError"})
        except ValueError:
            checks.append({"id": name, "passed": True, "kind": "assertion", "expected": "ValueError"})
        except Exception as exc:
            checks.append({"id": name, "passed": False, "kind": "error", "error": f"{type(exc).__name__}: {exc}"})
    return {"policy": POLICY_VERSION, "checks": checks, "infrastructure_error": None}


if __name__ == "__main__":
    result = evaluate(sys.argv[1])
    print(json.dumps(result, allow_nan=False))
    raise SystemExit(0 if result["checks"] and all(c["passed"] for c in result["checks"]) else 1)
