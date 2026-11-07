"""Export a pinned Git revision and execute an external acceptance policy."""

import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import time
import zipfile

from .acceptance_runner import EXPECTED_IDS, POLICY_VERSION
from .store import WorkflowError, digest, now

RUNNER = Path(__file__).with_name("acceptance_runner.py").resolve()


def git(repo, *args, binary=False):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkflowError(f"Git could not complete: {exc}") from exc
    if result.returncode:
        raise WorkflowError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def commit_id(repo, revision):
    sha = git(repo, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}")
    if not re.fullmatch(r"[a-f0-9]{40,64}", sha):
        raise WorkflowError("Revision did not resolve to a full commit ID")
    return sha


def run_checks(repo, sha):
    started = now()
    clock = time.monotonic()
    archive = git(repo, "archive", "--format=zip", sha, binary=True)
    if len(archive) > 20_000_000:
        raise WorkflowError("Demo repository archive exceeds 20 MB")
    with tempfile.TemporaryDirectory(prefix="proofdesk-") as temporary:
        snapshot = Path(temporary)
        with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
            if sum(entry.file_size for entry in zipped.infolist()) > 50_000_000:
                raise WorkflowError("Expanded repository exceeds 50 MB")
            for entry in zipped.infolist():
                name = PurePosixPath(entry.filename)
                target = (snapshot / entry.filename).resolve()
                if name.is_absolute() or ".." in name.parts or not target.is_relative_to(snapshot):
                    raise WorkflowError("Unsafe snapshot path")
                if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise WorkflowError("Symlinks are not supported in demo snapshots")
            zipped.extractall(snapshot)
        command = [sys.executable, "-I", str(RUNNER), str(snapshot)]
        try:
            process = subprocess.run(command, cwd=snapshot, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)
            stdout, stderr, code = process.stdout, process.stderr, process.returncode
            try:
                report = json.loads(stdout)
            except ValueError:
                report = {"checks": [], "infrastructure_error": "Runner did not return valid JSON"}
        except subprocess.TimeoutExpired:
            stdout, stderr, code = "", "Acceptance process exceeded 15 seconds", -1
            report = {"checks": [], "infrastructure_error": "timeout"}
    raw_checks = report.get("checks", []) if isinstance(report, dict) else []
    checks = raw_checks if isinstance(raw_checks, list) else []
    well_formed = (
        isinstance(report, dict) and report.get("policy") == POLICY_VERSION
        and isinstance(checks, list) and all(isinstance(c, dict) for c in checks)
        and [c.get("id") for c in checks] == EXPECTED_IDS
        and all(type(c.get("passed")) is bool for c in checks)
        and not report.get("infrastructure_error")
    )
    passed = well_formed and code == 0 and all(c["passed"] for c in checks)
    complaint = next((c for c in checks if isinstance(c, dict) and c.get("id") == "reported-rounding"), {})
    reproduced = well_formed and code == 1 and complaint.get("passed") is False and complaint.get("kind") == "assertion"
    return {
        "commit": sha, "started_at": started, "finished_at": now(),
        "duration_seconds": round(time.monotonic() - clock, 4),
        "python": sys.version.split()[0], "policy": POLICY_VERSION,
        "runner_sha256": digest(RUNNER),
        "command": [sys.executable, "-I", "<trusted acceptance runner>", "<temporary Git snapshot>"],
        "exit_code": code, "stdout": stdout[:100000], "stderr": stderr[:100000],
        "checks": checks, "infrastructure_error": report.get("infrastructure_error") if isinstance(report, dict) else "Invalid report",
        "well_formed": well_formed, "passed": passed, "reproduced": reproduced,
    }
