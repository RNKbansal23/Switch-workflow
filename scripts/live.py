"""Prepare a baseline-only repository and a concrete Switch request. No simulated AI."""
import argparse
import json
from pathlib import Path
import uuid

from scripts.demo import PROJECT, fixture_repo
from workflow.store import atomic_json


def prepare(root, prefix="proofdesk"):
    if not prefix or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in prefix):
        raise ValueError("Use a lowercase agent prefix containing letters, digits and hyphens")
    run = Path(root).resolve() / "live-repositories" / uuid.uuid4().hex[:8]
    revisions = fixture_repo(run, include_candidates=False)
    prompt = (
        f"@{prefix}-concierge Open a new synthetic order-total-v1 case.\n"
        "The baseline order_total('10.05', 1, '10') returns '10.05'; the documented result is '9.05'.\n"
        "Apply the percentage discount to the complete order, then round once to two decimal places using ROUND_HALF_UP.\n"
        f"Baseline repository: {run}\nBaseline full commit: {revisions['baseline']}\n"
        f"ProofDesk project and shared state location: {PROJECT}\n"
        "Read docs/demo.md, docs/WORKFLOW-SPEC.md and your role contract under agents/. "
        "Create the case with the actual source message ID; record real room/thread references with the context command. "
        "Ask Builder to reproduce the failure, write a focused patch and regression test, and commit them in the baseline repository. "
        "Ask Verifier to execute independent checks against that exact candidate. Return the diff and evidence for my review. "
        "Do not inspect prepared candidate fixtures, approve for me, merge, deploy, or send a customer message. "
        "This is a live-agent run using a synthetic report."
    )
    # Preparation artifacts live beside the repository, never in its commit history.
    bundle = Path(root).resolve() / "live-requests" / run.name
    bundle.mkdir(parents=True)
    prompt_file = bundle / "START-IN-SWITCH.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    result = {"mode": "BASELINE ONLY — agents must generate the candidate live", "repository": str(run),
              "baseline_commit": revisions["baseline"], "prompt_file": str(prompt_file), "prompt": prompt}
    atomic_json(bundle / "live-run.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".proofdesk")
    parser.add_argument("--prefix", default="proofdesk")
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.prefix), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
