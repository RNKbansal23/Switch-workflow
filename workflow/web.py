"""Loopback-only operator workspace. No third-party dependencies or AI keys."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
from urllib.parse import urlsplit
import uuid

from .presentation import case_view, environment, export_html, list_cases
from .service import Service
from .store import WorkflowError

ASSETS = Path(__file__).with_name("web_assets")
MAX_BODY = 64 * 1024


class Workspace(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, root, port=8765):
        self.service = Service(root)
        self.token = secrets.token_urlsafe(32)
        self.jobs = {}
        self.job_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="proofdesk-check")
        super().__init__(("127.0.0.1", port), Handler)

    def server_close(self):
        super().server_close()
        self.executor.shutdown(wait=True, cancel_futures=True)

    def submit(self, case_id, action):
        with self.job_lock:
            for job in self.jobs.values():
                if job["status"] in ("queued", "running"):
                    raise WorkflowError("A check is already running. Wait for its result.")
            job_id = uuid.uuid4().hex
            self.jobs[job_id] = {"id": job_id, "case_id": case_id, "status": "queued"}

        def run():
            with self.job_lock:
                self.jobs[job_id]["status"] = "running"
            try:
                case = action()
                update = {"status": "finished", "state": case["state"]}
            except Exception as exc:
                update = {"status": "failed", "error": str(exc)}
            with self.job_lock:
                self.jobs[job_id].update(update)
                # Bound memory while preserving the current result.
                while len(self.jobs) > 100:
                    del self.jobs[next(iter(self.jobs))]

        self.executor.submit(run)
        return self.jobs[job_id].copy()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Do not log URLs, case payloads, or authorization tokens.
        pass

    def send(self, status, body, content_type="application/json; charset=utf-8", download=None):
        raw = body.encode("utf-8") if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if download:
            self.send_header("Content-Disposition", f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(raw)

    def guard(self):
        allowed = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != allowed:
            self.send(403, {"error": "Use the printed 127.0.0.1 address."})
            return False
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{allowed}":
            self.send(403, {"error": "Cross-origin access is disabled."})
            return False
        return True

    def authorized(self):
        token = self.headers.get("Authorization", "")
        if not secrets.compare_digest(token.encode("utf-8"), ("Bearer " + self.server.token).encode("utf-8")):
            self.send(401, {"error": "Workspace locked. Open the full terminal URL to unlock it."})
            return False
        return True

    def do_GET(self):
        if not self.guard():
            return
        path = urlsplit(self.path).path
        assets = {"/": ("index.html", "text/html; charset=utf-8"),
                  "/app.css": ("app.css", "text/css; charset=utf-8"),
                  "/app.js": ("app.js", "text/javascript; charset=utf-8")}
        if path in assets:
            name, mime = assets[path]
            self.send(200, (ASSETS / name).read_text(encoding="utf-8"), mime)
            return
        if not self.authorized():
            return
        try:
            if path == "/api/health":
                self.send(200, environment())
            elif path == "/api/cases":
                self.send(200, list_cases(self.server.service))
            elif path.startswith("/api/jobs/"):
                with self.server.job_lock:
                    job = self.server.jobs.get(path.rsplit("/", 1)[1])
                    self.send(200 if job else 404, job or {"error": "Job not found"})
            elif path.startswith("/api/cases/"):
                parts = path.strip("/").split("/")
                if len(parts) not in (3, 4) or (len(parts) == 4 and parts[3] != "export"):
                    self.send(404, {"error": "Route not found"})
                    return
                view = case_view(self.server.service, parts[2])
                if len(parts) == 4:
                    self.send(200, export_html(view), "text/html; charset=utf-8", parts[2] + ".html")
                else:
                    self.send(200, view)
            else:
                self.send(404, {"error": "Route not found"})
        except (WorkflowError, OSError, ValueError, KeyError) as exc:
            self.send(409, {"error": str(exc)})

    def do_POST(self):
        if not self.guard() or not self.authorized():
            return
        try:
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                self.send(415, {"error": "Send application/json"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                self.send(413, {"error": "Request must contain 1–65536 bytes"})
                return
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object")
            path = urlsplit(self.path).path
            service = self.server.service
            if path == "/api/cases":
                report = payload.get("report")
                if not isinstance(report, dict) or any(not isinstance(v, str) for v in report.values()):
                    raise ValueError("Report fields must be text")
                key = payload.get("request_key")
                if not isinstance(key, str) or not key.strip():
                    raise ValueError("A stable request key is required")
                self.send(201, service.create(key, report))
                return
            parts = path.strip("/").split("/")
            if len(parts) != 4 or parts[:2] != ["api", "cases"]:
                self.send(404, {"error": "Route not found"})
                return
            case_id, action = parts[2:]
            service.store.case_dir(case_id)
            if action == "verify":
                self.send(202, self.server.submit(case_id, lambda: service.verify(case_id)))
            elif action == "review":
                for field in ("decision", "reviewer", "reason", "commit", "verification_sha256"):
                    if not isinstance(payload.get(field), str) or not payload[field].strip():
                        raise ValueError(f"{field} is required")
                if payload["decision"] not in ("approve", "reject"):
                    raise ValueError("Decision must be approve or reject")
                self.send(200, service.review(case_id, payload["decision"], payload["reviewer"],
                                             payload["reason"], payload["commit"],
                                             expected_verification=payload["verification_sha256"]))
            elif action == "draft":
                self.send(200, service.draft(case_id))
            elif action == "close":
                self.send(200, service.close(case_id))
            elif action == "clarify":
                report = payload.get("report")
                if not isinstance(report, dict) or any(not isinstance(v, str) for v in report.values()):
                    raise ValueError("Report fields must be text")
                self.send(200, service.clarify(case_id, report))
            else:
                self.send(404, {"error": "Unknown action"})
        except (WorkflowError, OSError, ValueError, KeyError, TypeError) as exc:
            self.send(409, {"error": str(exc)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".proofdesk")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with Workspace(args.root, args.port) as server:
        print(f"ProofDesk: http://127.0.0.1:{server.server_port}/#token={server.token}", flush=True)
        print("Local operator access. Keep this URL private. Ctrl+C stops the workspace.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
