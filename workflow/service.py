"""Case transitions. All mutations acquire the store-wide lock."""

import hashlib
import json
from pathlib import Path
import uuid

from .store import Store, WorkflowError, digest, now
from .verify import RUNNER, commit_id, run_checks
from .acceptance_runner import POLICY_VERSION

REQUIRED_REPORT = ("policy", "summary", "steps", "expected", "actual")
MAX_ATTEMPTS = 2


class Service:
    def __init__(self, root=".proofdesk"):
        self.store = Store(root)

    def _state(self, case, *allowed):
        if case["state"] not in allowed:
            raise WorkflowError(f"Action requires {', '.join(allowed)}; case is {case['state']}")

    def create(self, request_key, report):
        if not request_key or not isinstance(report, dict):
            raise WorkflowError("A request key and JSON report object are required")
        if report.get("policy") and report["policy"] != POLICY_VERSION:
            raise WorkflowError("This MVP supports only the order-total-v1 policy")
        with self.store.lock():
            key = hashlib.sha256(request_key.encode()).hexdigest()
            payload_hash = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
            for path in (self.store.root / "cases").glob("*/case.json"):
                existing = json.loads(path.read_text(encoding="utf-8"))
                if existing["request_key_hash"] == key:
                    if existing["report_hash"] != payload_hash:
                        raise WorkflowError("Request key already used with a different report")
                    return existing
            timestamp = now()
            missing = [field for field in REQUIRED_REPORT if not isinstance(report.get(field), str) or not report[field].strip()]
            case = {
                "schema_version": 1, "id": "PD-" + uuid.uuid4().hex[:12],
                "request_key_hash": key, "report_hash": payload_hash, "report": report,
                "state": "CLARIFYING" if missing else "NEW", "missing_fields": missing,
                "created_at": timestamp, "updated_at": timestamp, "events": [],
                "baseline": None, "candidate": None, "verification": None,
                "approval": None, "response": None, "attempts": 0, "total_attempts": 0,
            }
            self.store.event(case, "created", missing_fields=missing)
            self.store.save(case)
            return case

    def context(self, case_id, room, thread, message):
        values = {"room": room, "thread": thread, "message": message}
        if any(not isinstance(value, str) or not value.strip() or len(value) > 2000 for value in values.values()):
            raise WorkflowError("Real room, thread and message references are required (up to 2000 characters each)")
        with self.store.lock():
            case = self.store.load(case_id)
            if case["state"] == "CLOSED":
                raise WorkflowError("Closed cases cannot change context")
            reference = self.store.evidence(case, "switch-context", {
                **values, "provenance": "Operator/agent supplied references; not independently authenticated",
            })
            self.store.event(case, "switch_context_recorded", evidence=reference)
            self.store.save(case)
            return case

    def clarify(self, case_id, report):
        with self.store.lock():
            case = self.store.load(case_id)
            self._state(case, "CLARIFYING")
            if not isinstance(report, dict):
                raise WorkflowError("Report must be an object")
            if report.get("policy") and report["policy"] != POLICY_VERSION:
                raise WorkflowError("This MVP supports only the order-total-v1 policy")
            case["report"].update(report)
            missing = [f for f in REQUIRED_REPORT if not isinstance(case["report"].get(f), str) or not case["report"][f].strip()]
            case["missing_fields"] = missing
            case["state"] = "CLARIFYING" if missing else "NEW"
            self.store.event(case, "clarified", missing_fields=missing)
            self.store.save(case)
            return case

    def reproduce(self, case_id, repo, revision):
        with self.store.lock():
            case = self.store.load(case_id)
            self._state(case, "NEW")
            repo = Path(repo).resolve()
            sha = commit_id(repo, revision)
            result = run_checks(repo, sha)
            reference = self.store.evidence(case, "baseline", result)
            case["baseline"] = {"repo": str(repo), "commit": sha, "evidence": reference}
            if result["reproduced"]:
                case["state"] = "REPRODUCED"
            self.store.event(case, "reproduction", commit=sha, reproduced=result["reproduced"], evidence=reference)
            self.store.save(case)
            return case

    def propose(self, case_id, revision):
        with self.store.lock():
            case = self.store.load(case_id)
            self._state(case, "REPRODUCED", "PATCH_READY", "VERIFIED", "APPROVED")
            sha = commit_id(case["baseline"]["repo"], revision)
            if sha == case["baseline"]["commit"]:
                raise WorkflowError("Candidate must differ from the failing baseline")
            if case["candidate"] and case["candidate"]["commit"] == sha:
                return case
            if case["attempts"] >= MAX_ATTEMPTS:
                raise WorkflowError("Repair budget exhausted; a human must grant a retry")
            case["candidate"] = {"commit": sha}
            case["attempts"] += 1
            case["total_attempts"] += 1
            case["verification"] = None
            case["approval"] = None
            case["response"] = None
            case["state"] = "PATCH_READY"
            self.store.event(case, "candidate_proposed", commit=sha, attempt=case["total_attempts"])
            self.store.save(case)
            return case

    def verify(self, case_id):
        with self.store.lock():
            case = self.store.load(case_id)
            self._state(case, "PATCH_READY", "VERIFIED", "APPROVED")
            # Never accept an arbitrary failing command as proof of reproduction.
            baseline = self.store.read_evidence(case, case["baseline"]["evidence"])
            if not baseline.get("reproduced") or baseline.get("commit") != case["baseline"]["commit"]:
                raise WorkflowError("Baseline reproduction evidence is invalid")
            result = run_checks(case["baseline"]["repo"], case["candidate"]["commit"])
            reference = self.store.evidence(case, "verification", result)
            case["verification"] = {"commit": result["commit"], "passed": result["passed"], "evidence": reference}
            case["approval"] = None
            case["response"] = None
            case["state"] = "VERIFIED" if result["passed"] else ("NEEDS_HUMAN" if case["attempts"] >= MAX_ATTEMPTS else "PATCH_READY")
            self.store.event(case, "verified" if result["passed"] else "verification_rejected", commit=result["commit"], evidence=reference)
            self.store.save(case)
            return case

    def _verified(self, case):
        baseline = self.store.read_evidence(case, case["baseline"]["evidence"])
        if not baseline.get("reproduced") or baseline.get("commit") != case["baseline"]["commit"]:
            raise WorkflowError("Baseline reproduction evidence is invalid")
        verification = case["verification"]
        if not verification or not verification["passed"] or verification["commit"] != case["candidate"]["commit"]:
            raise WorkflowError("Current candidate has no passing verification")
        evidence = self.store.read_evidence(case, verification["evidence"])
        if not evidence.get("passed") or evidence.get("commit") != case["candidate"]["commit"]:
            raise WorkflowError("Verification evidence does not match candidate")
        if evidence.get("runner_sha256") != digest(RUNNER):
            raise WorkflowError("Acceptance policy changed; reverify before review")

    def review(self, case_id, decision, reviewer, reason, expected_commit, expected_verification=None):
        if not reviewer.strip() or not reason.strip():
            raise WorkflowError("Reviewer and reason are required")
        with self.store.lock():
            case = self.store.load(case_id)
            if not case["candidate"] or expected_commit != case["candidate"]["commit"]:
                raise WorkflowError("Review commit does not match the current candidate")
            if expected_verification is not None and (
                not case["verification"] or
                case["verification"]["evidence"]["sha256"] != expected_verification
            ):
                raise WorkflowError("Verification changed since you opened the case. Refresh and review again.")
            if decision == "retry":
                self._state(case, "NEEDS_HUMAN", "PATCH_READY")
                case["attempts"] = 0
                case["state"] = "PATCH_READY"
                case["verification"] = None
                case["approval"] = None
                case["response"] = None
            else:
                self._state(case, "VERIFIED")
                self._verified(case)
                if decision == "approve":
                    case["approval"] = {"reviewer": reviewer, "reason": reason, "commit": expected_commit, "at": now(), "verification_sha256": case["verification"]["evidence"]["sha256"]}
                    case["state"] = "APPROVED"
                elif decision == "reject":
                    case["approval"] = None
                    case["state"] = "NEEDS_HUMAN"
                else:
                    raise WorkflowError("Unknown review decision")
            self.store.event(case, "human_" + decision, reviewer=reviewer, reason=reason, commit=expected_commit)
            self.store.save(case)
            return case

    def draft(self, case_id):
        with self.store.lock():
            case = self.store.load(case_id)
            self._state(case, "APPROVED")
            self._verified(case)
            if not case["approval"] or case["approval"]["commit"] != case["candidate"]["commit"]:
                raise WorkflowError("Approval is missing or stale")
            content = (
                f"DRAFT ONLY — case {case_id}\n\n"
                f"We reproduced your report: {case['report']['summary']}. "
                "We prepared a candidate patch and checked it against the documented "
                f"order-total acceptance policy. Candidate {case['candidate']['commit']} "
                f"was accepted for this local case by {case['approval']['reviewer']}. "
                "The patch has not been confirmed merged or deployed. "
                "We will confirm availability separately.\n"
            )
            reference = self.store.evidence(case, "response-draft", {"commit": case["candidate"]["commit"], "content": content, "sent": False})
            case["response"] = reference
            self.store.event(case, "response_drafted", evidence=reference)
            self.store.save(case)
            return case

    def close(self, case_id):
        with self.store.lock():
            case = self.store.load(case_id)
            self._state(case, "APPROVED")
            self._verified(case)
            approval = case["approval"]
            if not approval or approval["commit"] != case["candidate"]["commit"] or approval["verification_sha256"] != case["verification"]["evidence"]["sha256"]:
                raise WorkflowError("Approval is missing or stale")
            if not case.get("response"):
                raise WorkflowError("Prepare the customer reply draft before closing")
            response = self.store.read_evidence(case, case["response"])
            if response["commit"] != case["candidate"]["commit"]:
                raise WorkflowError("Customer draft is stale")
            case["state"] = "CLOSED"
            self.store.event(case, "closed", commit=case["candidate"]["commit"])
            self.store.save(case)
            return case

    def summary(self, case_id):
        with self.store.lock():
            case = self.store.load(case_id)
            if case["state"] in ("VERIFIED", "APPROVED", "CLOSED"):
                self._verified(case)
            checks = []
            if case["verification"]:
                checks = self.store.read_evidence(case, case["verification"]["evidence"])["checks"]
            return {"id": case_id, "state": case["state"], "summary": case["report"].get("summary"), "candidate": case["candidate"], "checks_passed": sum(c["passed"] for c in checks), "checks_total": len(checks), "repair_attempts": case["total_attempts"], "human_decisions": sum(e["action"].startswith("human_") for e in case["events"]), "approval": case["approval"], "response": case.get("response"), "note": "Acceptance of a local patch does not mean it was merged, deployed, or sent to a customer."}
