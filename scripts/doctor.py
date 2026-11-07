"""Report local prerequisites without reading credentials or claiming connectivity."""
import json
import platform
import shutil
import subprocess
import sys


def probe(executable, arguments):
    path = shutil.which(executable)
    if not path:
        return {"installed": False, "ready": False}
    try:
        result = subprocess.run([path, *arguments], capture_output=True, text=True, timeout=12)
        return {"installed": True, "ready": result.returncode == 0,
                "detail": (result.stdout.strip() if result.returncode == 0 else "Command failed; check the application locally.")[:300]}
    except (OSError, subprocess.TimeoutExpired):
        return {"installed": True, "ready": False, "detail": "Command could not complete."}


def main():
    result = {"python": {"version": platform.python_version(), "executable": sys.executable},
              "git": probe("git", ["--version"]),
              "docker_engine": probe("docker", ["version", "--format", "{{.Server.Version}}"]),
              "providers": {name: {"installed": bool(shutil.which(name + ".cmd")) or bool(shutil.which(name)),
                                   "sign_in": "not_checked"}
                            for name in ("codex", "claude", "opencode", "agent", "antigravity")},
              "switch": {"connection": "not_verified", "action": "Open Switch Console; verify server, provider, and a real room reply."},
              "api_keys_required_for_dashboard": False}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
