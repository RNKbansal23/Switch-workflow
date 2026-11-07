"""HTTP boundaries, real evidence rendering and stale browser review regression checks."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

from scripts.demo import PROJECT, fixture_repo
from workflow.presentation import case_view, export_html
from workflow.store import WorkflowError
from workflow.web import Workspace


class WorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_temp = tempfile.TemporaryDirectory(prefix="proofdesk-web-repo-")
        cls.repo = Path(cls.repo_temp.name) / "repo"
        cls.revisions = fixture_repo(cls.repo)
        cls.report = json.loads((PROJECT / "fixtures/customer-report.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        import os
        import stat
        for path in Path(cls.repo_temp.name).rglob("*"):
            if path.is_file():
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        cls.repo_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="proofdesk-web-store-")
        self.server = Workspace(self.temp.name, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.service = self.server.service

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path, payload=None, *, auth=True, origin=None, host=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=15)
        headers = {"Host": host or f"127.0.0.1:{self.server.server_port}"}
        if auth:
            headers["Authorization"] = "Bearer " + self.server.token
        if origin:
            headers["Origin"] = origin
        if payload is not None:
            headers["Content-Type"] = "application/json"
        connection.request("POST" if payload is not None else "GET", path,
                           json.dumps(payload) if payload is not None else None, headers)
        response = connection.getresponse()
        data = response.read().decode("utf-8")
        status, mime = response.status, response.getheader("Content-Type")
        connection.close()
        return status, json.loads(data) if mime.startswith("application/json") else data

    def candidate(self):
        case = self.service.create("web-regression", self.report)
        self.service.reproduce(case["id"], self.repo, self.revisions["baseline"])
        self.service.propose(case["id"], self.revisions["corrected"])
        return case["id"]

    def test_auth_origin_and_host_boundaries(self):
        self.assertEqual(self.request("/api/cases", auth=False)[0], 401)
        self.assertEqual(self.request("/api/cases", origin="https://attacker.invalid")[0], 403)
        self.assertEqual(self.request("/api/cases", host="attacker.invalid")[0], 403)
        self.assertEqual(self.request("/api/cases")[1]["cases"], [])
        self.assertEqual(self.request("/", auth=False)[0], 200)

    def test_create_deduplicates_and_validates_inputs(self):
        payload = {"request_key": "web-1", "report": self.report}
        status, case = self.request("/api/cases", payload)
        self.assertEqual(status, 201)
        self.assertEqual(self.request("/api/cases", payload)[1]["id"], case["id"])
        self.assertEqual(self.request("/api/cases", {"request_key": "bad", "report": {"summary": []}})[0], 409)
        self.assertEqual(self.request("/api/cases", {"request_key": "", "report": self.report})[0], 409)

    def test_real_verification_job_review_draft_and_close(self):
        case_id = self.candidate()
        status, job = self.request(f"/api/cases/{case_id}/verify", {})
        self.assertEqual(status, 202)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            _, result = self.request("/api/jobs/" + job["id"])
            if result["status"] in ("finished", "failed"):
                break
            time.sleep(.05)
        self.assertEqual(result["status"], "finished")
        self.assertEqual(result["state"], "VERIFIED")
        _, view = self.request(f"/api/cases/{case_id}")
        case = view["case"]
        self.assertIn("order_total", view["diff"])
        self.assertTrue(all(item["valid"] for item in view["evidence"]))
        status, approved = self.request(f"/api/cases/{case_id}/review", {
            "decision": "approve", "reviewer": "HTTP test operator", "reason": "Inspected diff and checks",
            "commit": case["candidate"]["commit"],
            "verification_sha256": case["verification"]["evidence"]["sha256"],
        })
        self.assertEqual(status, 200)
        self.assertEqual(approved["state"], "APPROVED")
        self.assertEqual(self.request(f"/api/cases/{case_id}/draft", {})[0], 200)
        self.assertEqual(self.request(f"/api/cases/{case_id}/close", {})[1]["state"], "CLOSED")
        exported = self.request(f"/api/cases/{case_id}/export")[1]
        self.assertIn("DRAFT ONLY", exported)
        self.assertIn('&quot;sent&quot;: false', exported)

    def test_stale_browser_review_refused_after_same_revision_reverification(self):
        case_id = self.candidate()
        old = self.service.verify(case_id)
        old_hash = old["verification"]["evidence"]["sha256"]
        self.service.verify(case_id)
        status, result = self.request(f"/api/cases/{case_id}/review", {
            "decision": "approve", "reviewer": "test", "reason": "old page",
            "commit": old["candidate"]["commit"], "verification_sha256": old_hash,
        })
        self.assertEqual(status, 409)
        self.assertIn("Verification changed", result["error"])

    def test_tampered_evidence_is_visible_and_cannot_be_approved(self):
        case_id = self.candidate()
        case = self.service.verify(case_id)
        ref = case["verification"]["evidence"]
        (self.service.store.case_dir(case_id) / ref["path"]).write_text('{}', encoding="utf-8")
        _, view = self.request(f"/api/cases/{case_id}")
        self.assertTrue(any(not item["valid"] for item in view["evidence"]))
        with self.assertRaises(WorkflowError):
            self.service.review(case_id, "approve", "test", "test", case["candidate"]["commit"])

    def test_report_escapes_content_and_preserves_context(self):
        case = self.service.create("xss-report", {**self.report, "summary": '<script>alert("x")</script>'})
        self.service.context(case["id"], "room-actual", "thread-actual", "message-actual")
        view = case_view(self.service, case["id"])
        document = export_html(view)
        self.assertNotIn('<script>', document)
        self.assertIn('&lt;script&gt;', document)
        self.assertIn('room-actual', document)
        self.assertIn('not independently authenticated', document)

    def test_unknown_routes_and_path_traversal_refused(self):
        self.assertEqual(self.request('/api/cases/../export')[0], 409)
        self.assertEqual(self.request('/api/unknown')[0], 404)
        self.assertEqual(self.request('/api/cases/PD-123456789abc/unknown', {})[0], 404)

    def test_live_preparation_has_no_candidate_answers_or_case(self):
        from scripts.live import prepare
        from scripts.demo import command
        prepared = prepare(self.temp.name, "test-team")
        repo = Path(prepared["repository"])
        self.assertEqual(command(repo, "rev-list", "--count", "HEAD"), "1")
        self.assertEqual(command(repo, "ls-files"), "demo-app/order_total.py")
        self.assertEqual(command(repo, "status", "--porcelain"), "")
        self.assertTrue(prepared["prompt"].startswith("@test-team-concierge"))
        self.assertTrue(Path(prepared["prompt_file"]).is_file())
        self.assertEqual(self.request('/api/cases')[1]['cases'], [])
        # Clean read-only fixture Git files before the temporary directory exits.
        import os
        import stat
        for path in repo.rglob('*'):
            if path.is_file():
                os.chmod(path, stat.S_IREAD | stat.S_IWRITE)


if __name__ == "__main__":
    unittest.main()
