"""Run browser QA against disposable fixture state, never the operator's cases.

Set PLAYWRIGHT_MODULE to an installed playwright-core directory and optionally
PLAYWRIGHT_CHROMIUM_EXECUTABLE to an existing Chromium executable.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading

from scripts.demo import run
from workflow.web import Workspace


def main():
    if not os.environ.get("PLAYWRIGHT_MODULE"):
        raise SystemExit("Set PLAYWRIGHT_MODULE to an installed playwright-core directory.")
    with tempfile.TemporaryDirectory(prefix="proofdesk-browser-") as temporary:
        try:
            summary = run(temporary)
            with Workspace(temporary, 0) as server:
                server.service.context(summary["id"], "QA fixture room", "QA fixture thread", "QA fixture message")
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                env = {**os.environ, "PROOFDESK_QA_URL": f"http://127.0.0.1:{server.server_port}/#token={server.token}",
                       "PROOFDESK_QA_CASE": summary["id"]}
                try:
                    result = subprocess.run([shutil.which("node"), str(Path(__file__).with_suffix(".cjs"))],
                                            env=env, timeout=120)
                    if result.returncode:
                        raise SystemExit(result.returncode)
                finally:
                    server.shutdown()
                    thread.join()
        finally:
            # Temporary fixture Git object files can be read-only on Windows.
            import stat
            for path in Path(temporary).rglob("*"):
                if path.is_file():
                    os.chmod(path, stat.S_IREAD | stat.S_IWRITE)


if __name__ == "__main__":
    main()
