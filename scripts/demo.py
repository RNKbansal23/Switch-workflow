"""Create real Git fixture commits and execute a labelled local rehearsal.

No Switch conversation, live agent decision, approval, merge, or deployment is simulated.
The rehearsal stops at VERIFIED for a person to review separately.
"""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import uuid

from workflow.service import Service

PROJECT = Path(__file__).resolve().parents[1]


def command(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def fixture_repo(destination, include_candidates=True):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    command(destination, "init", "--quiet")
    (destination / "demo-app").mkdir()
    revisions = {}
    sources = (
        ("baseline", PROJECT / "demo-app" / "order_total.py"),
        ("incomplete", PROJECT / "fixtures" / "incomplete" / "order_total.py"),
        ("corrected", PROJECT / "fixtures" / "corrected" / "order_total.py"),
    )
    for name, source in (sources if include_candidates else sources[:1]):
        shutil.copyfile(source, destination / "demo-app" / "order_total.py")
        command(destination, "add", "demo-app/order_total.py")
        command(destination, "-c", "user.name=ProofDesk fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Labelled demo fixture: " + name)
        revisions[name] = command(destination, "rev-parse", "HEAD")
    return revisions


def run(root):
    root = Path(root).resolve()
    run_id = uuid.uuid4().hex[:8]
    repo = root / "demo-repositories" / run_id
    revisions = fixture_repo(repo)
    service = Service(root)
    report = json.loads((PROJECT / "fixtures" / "customer-report.json").read_text(encoding="utf-8"))
    case = service.create("fixture-rehearsal-" + run_id, report)
    case_id = case["id"]
    case = service.reproduce(case_id, repo, revisions["baseline"])
    if case["state"] != "REPRODUCED":
        raise RuntimeError("Baseline did not reproduce the reported failure")
    service.propose(case_id, revisions["incomplete"])
    rejected = service.verify(case_id)
    if rejected["verification"]["passed"]:
        raise RuntimeError("Incomplete fixture unexpectedly passed")
    service.propose(case_id, revisions["corrected"])
    verified = service.verify(case_id)
    if verified["state"] != "VERIFIED":
        raise RuntimeError("Corrected fixture failed verification")
    summary = service.summary(case_id)
    summary.update({"mode": "LABELLED LOCAL FIXTURE REHEARSAL; no live Switch agents", "repository": str(repo), "revisions": revisions, "rejection_observed": True, "approval": "PENDING: run the human review command after inspecting evidence"})
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".proofdesk")
    parser.add_argument("--prepare-only", action="store_true", help="Create a baseline-only repository for a live agent run")
    args = parser.parse_args()
    if args.prepare_only:
        repo = Path(args.root).resolve() / "live-repositories" / uuid.uuid4().hex[:8]
        revisions = fixture_repo(repo, include_candidates=False)
        result = {"mode": "BASELINE ONLY: ready for a live Builder", "repository": str(repo), "revisions": revisions}
    else:
        result = run(args.root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
