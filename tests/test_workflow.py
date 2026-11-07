import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.demo import PROJECT, command, fixture_repo
from workflow.cli import main
from workflow.service import Service
from workflow.store import WorkflowError


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_temp = tempfile.TemporaryDirectory(prefix="proofdesk-test-repo-")
        cls.repo = Path(cls.repo_temp.name) / "repo"
        cls.revisions = fixture_repo(cls.repo)
        cls.report = json.loads((PROJECT / "fixtures/customer-report.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        # Git's object files can be read-only on Windows. Remove via native Python
        # within this known temporary directory, not a computed shell command.
        import os
        import stat
        for path in Path(cls.repo_temp.name).rglob("*"):
            if path.is_file():
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        cls.repo_temp.cleanup()

    def setUp(self):
        self.state = tempfile.TemporaryDirectory(prefix="proofdesk-test-state-")
        self.service = Service(self.state.name)
        self.case_id = self.service.create("request-1", self.report)["id"]

    def tearDown(self):
        self.state.cleanup()

    def reproduced(self):
        case = self.service.reproduce(self.case_id, self.repo, self.revisions["baseline"])
        self.assertEqual(case["state"], "REPRODUCED")
        return case

    def verified(self):
        self.reproduced()
        self.service.propose(self.case_id, self.revisions["corrected"])
        case = self.service.verify(self.case_id)
        self.assertEqual(case["state"], "VERIFIED")
        return case

    def approve(self):
        return self.service.review(self.case_id, "approve", "test-human", "Reviewed the candidate", self.revisions["corrected"])

    def test_full_rejection_revision_human_review_and_close(self):
        self.reproduced()
        self.service.propose(self.case_id, self.revisions["incomplete"])
        rejected = self.service.verify(self.case_id)
        self.assertFalse(rejected["verification"]["passed"])
        with self.assertRaises(WorkflowError):
            self.approve()
        self.service.propose(self.case_id, self.revisions["corrected"])
        verified = self.service.verify(self.case_id)
        self.assertEqual(verified["state"], "VERIFIED")
        with self.assertRaises(WorkflowError):
            self.service.close(self.case_id)
        self.approve()
        with self.assertRaises(WorkflowError):
            self.service.close(self.case_id)
        self.service.draft(self.case_id)
        self.assertEqual(self.service.close(self.case_id)["state"], "CLOSED")
        self.assertEqual(self.service.summary(self.case_id)["checks_passed"], 11)

    def test_deduplication_and_conflicting_payload(self):
        self.assertEqual(self.service.create("request-1", self.report)["id"], self.case_id)
        with self.assertRaises(WorkflowError):
            self.service.create("request-1", {**self.report, "summary": "Different report"})

    def test_unrelated_policy_is_not_claimed_as_verified(self):
        with self.assertRaises(WorkflowError):
            self.service.create("unrelated", {**self.report, "policy": "any-other-bug"})

    def test_clarification_blocks_reproduction(self):
        case = self.service.create("missing", {"summary": "Wrong price"})
        self.assertEqual(case["state"], "CLARIFYING")
        with self.assertRaises(WorkflowError):
            self.service.reproduce(case["id"], self.repo, self.revisions["baseline"])
        self.assertEqual(self.service.clarify(case["id"], self.report)["state"], "NEW")

    def test_passing_baseline_is_not_reproduction(self):
        case = self.service.reproduce(self.case_id, self.repo, self.revisions["corrected"])
        self.assertEqual(case["state"], "NEW")

    def test_changed_candidate_invalidates_approval(self):
        self.verified()
        self.approve()
        revised = self.service.propose(self.case_id, self.revisions["incomplete"])
        self.assertIsNone(revised["approval"])
        self.assertIsNone(revised["verification"])
        with self.assertRaises(WorkflowError):
            self.service.close(self.case_id)

    def test_review_must_name_current_full_commit(self):
        self.verified()
        with self.assertRaises(WorkflowError):
            self.service.review(self.case_id, "approve", "human", "Reviewed", self.revisions["incomplete"])

    def test_reverification_invalidates_approval_and_draft(self):
        self.verified()
        self.approve()
        self.service.draft(self.case_id)
        case = self.service.verify(self.case_id)
        self.assertEqual(case["state"], "VERIFIED")
        self.assertIsNone(case["approval"])
        self.assertIsNone(case["response"])

    def test_retry_cannot_target_a_stale_commit(self):
        self.reproduced()
        self.service.propose(self.case_id, self.revisions["incomplete"])
        with self.assertRaises(WorkflowError):
            self.service.review(self.case_id, "retry", "human", "Retry", self.revisions["corrected"])

    def test_syntax_error_is_not_proof_of_the_reported_bug(self):
        from workflow.verify import run_checks
        from unittest.mock import patch
        import subprocess
        failure = subprocess.CompletedProcess([], 1, stdout=json.dumps({"policy": "order-total-v1", "checks": [], "infrastructure_error": "SyntaxError"}), stderr="")
        archive = subprocess.run(["git", "-C", str(self.repo), "archive", "--format=zip", self.revisions["baseline"]], capture_output=True, check=True).stdout
        with patch("workflow.verify.git", return_value=archive), patch("workflow.verify.subprocess.run", return_value=failure):
            result = run_checks(self.repo, self.revisions["baseline"])
        self.assertFalse(result["passed"])
        self.assertFalse(result["reproduced"])

    def test_malformed_runner_report_fails_closed(self):
        from workflow.verify import run_checks
        from unittest.mock import patch
        import subprocess
        archive = subprocess.run(["git", "-C", str(self.repo), "archive", "--format=zip", self.revisions["baseline"]], capture_output=True, check=True).stdout
        malformed = subprocess.CompletedProcess([], 0, stdout='{"checks": null}', stderr="")
        with patch("workflow.verify.git", return_value=archive), patch("workflow.verify.subprocess.run", return_value=malformed):
            result = run_checks(self.repo, self.revisions["baseline"])
        self.assertFalse(result["passed"])
        self.assertFalse(result["reproduced"])

    def test_tampered_evidence_blocks_approval(self):
        case = self.verified()
        evidence = self.service.store.case_dir(self.case_id) / case["verification"]["evidence"]["path"]
        evidence.write_text("{}", encoding="utf-8")
        with self.assertRaises(WorkflowError):
            self.approve()

    def test_changed_baseline_evidence_blocks_closure(self):
        case = self.verified()
        self.approve()
        self.service.draft(self.case_id)
        evidence = self.service.store.case_dir(self.case_id) / case["baseline"]["evidence"]["path"]
        evidence.write_text("{}", encoding="utf-8")
        with self.assertRaises(WorkflowError):
            self.service.close(self.case_id)

    def test_budget_and_human_retry(self):
        self.reproduced()
        self.service.propose(self.case_id, self.revisions["incomplete"])
        self.service.verify(self.case_id)
        # Same revision is idempotent and does not consume another attempt.
        self.assertEqual(self.service.propose(self.case_id, self.revisions["incomplete"])["attempts"], 1)
        self.service.propose(self.case_id, self.revisions["corrected"])
        with self.assertRaises(WorkflowError):
            self.service.propose(self.case_id, self.revisions["incomplete"])
        self.service.review(self.case_id, "retry", "human", "One extra attempt", self.revisions["corrected"])
        self.assertEqual(self.service.propose(self.case_id, self.revisions["incomplete"])["attempts"], 1)

    def test_case_id_traversal_is_refused(self):
        with self.assertRaises(WorkflowError):
            self.service.store.load("../../outside")

    def test_store_lock_does_not_allow_concurrent_writer(self):
        with self.service.store.lock():
            with self.assertRaises(WorkflowError):
                self.service.create("another", self.report)

    def test_uncommitted_files_do_not_affect_verification(self):
        # The exported commit is used even if the working copy has a different file.
        source = self.repo / "demo-app/order_total.py"
        original = source.read_bytes()
        try:
            source.write_text("raise RuntimeError('uncommitted change')", encoding="utf-8")
            self.verified()
        finally:
            source.write_bytes(original)

    def test_cli_reports_failed_verification_exit_code(self):
        self.reproduced()
        self.service.propose(self.case_id, self.revisions["incomplete"])
        with contextlib.redirect_stdout(io.StringIO()):
            status = main(["--root", self.state.name, "verify", self.case_id])
        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
