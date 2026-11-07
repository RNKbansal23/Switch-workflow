"""Human-operated review entry point; do not expose to agent tools."""

import argparse
import json
import sys

from .service import Service
from .store import WorkflowError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Human review of an exact ProofDesk candidate")
    parser.add_argument("--root", default=".proofdesk")
    parser.add_argument("decision", choices=("approve", "reject", "retry"))
    parser.add_argument("case_id")
    parser.add_argument("--commit", required=True, help="Full candidate commit being reviewed")
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    try:
        result = Service(args.root).review(args.case_id, args.decision, args.reviewer, args.reason, args.commit)
        print(json.dumps(result, indent=2))
        return 0
    except (WorkflowError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
