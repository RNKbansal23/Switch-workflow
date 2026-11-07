"""Atomic JSON case records and a single-writer store lock.

This prevents accidental races through this API, not edits by the account owner.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import uuid


class WorkflowError(Exception):
    """An expected workflow precondition failed."""


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class Store:
    def __init__(self, root=".proofdesk"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def lock(self):
        path = self.root / "store.lock"
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise WorkflowError(
                "Store is busy. If a process crashed, confirm it stopped before removing store.lock."
            ) from exc
        try:
            with os.fdopen(fd, "w") as stream:
                stream.write(str(os.getpid()))
            yield
        finally:
            path.unlink(missing_ok=True)

    def case_dir(self, case_id):
        if not re.fullmatch(r"PD-[a-f0-9]{12}", case_id):
            raise WorkflowError("Invalid case ID")
        path = (self.root / "cases" / case_id).resolve()
        if not path.is_relative_to(self.root):
            raise WorkflowError("Case path escapes store")
        return path

    def load(self, case_id):
        try:
            case = json.loads((self.case_dir(case_id) / "case.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise WorkflowError("Case does not exist or cannot be read") from exc
        if case.get("schema_version") != 1 or case.get("id") != case_id:
            raise WorkflowError("Unsupported or inconsistent case record")
        return case

    def save(self, case):
        atomic_json(self.case_dir(case["id"]) / "case.json", case)

    def event(self, case, action, **details):
        timestamp = now()
        case["updated_at"] = timestamp
        case["events"].append({"at": timestamp, "action": action, **details})

    def evidence(self, case, kind, data):
        relative = f"evidence/{kind}-{uuid.uuid4().hex}.json"
        path = self.case_dir(case["id"]) / relative
        atomic_json(path, data)
        return {"path": relative, "sha256": digest(path)}

    def read_evidence(self, case, reference):
        path = (self.case_dir(case["id"]) / reference["path"]).resolve()
        if not path.is_relative_to(self.case_dir(case["id"])):
            raise WorkflowError("Evidence path escapes case directory")
        if not path.is_file() or digest(path) != reference["sha256"]:
            raise WorkflowError("Evidence is missing or has changed")
        return json.loads(path.read_text(encoding="utf-8"))
