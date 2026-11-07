"""Read real case evidence for the operator interface and portable exports."""

from datetime import datetime
import html
import json
import platform
import shutil
from pathlib import Path

from .store import WorkflowError
from .verify import git


def case_view(service, case_id):
    with service.store.lock():
        case = service.store.load(case_id)
        evidence = []
        references = {}
        for event in case["events"]:
            ref = event.get("evidence")
            if ref:
                references[ref["path"]] = ref
        for key in ("baseline", "verification"):
            if case.get(key):
                ref = case[key]["evidence"]
                references[ref["path"]] = ref
        if case.get("response"):
            ref = case["response"]
            references[ref["path"]] = ref
        for ref in references.values():
            try:
                evidence.append({"reference": ref, "valid": True,
                                 "data": service.store.read_evidence(case, ref)})
            except (WorkflowError, OSError, ValueError) as exc:
                evidence.append({"reference": ref, "valid": False, "error": str(exc)})
        elapsed = (datetime.fromisoformat(case["updated_at"]) -
                   datetime.fromisoformat(case["created_at"])).total_seconds()
        result = {"case": case, "evidence": evidence,
                  "elapsed_seconds": max(0, round(elapsed)), "diff": "", "diff_error": None}
    if case.get("candidate") and case.get("baseline"):
        try:
            result["diff"] = git(case["baseline"]["repo"], "diff", "--no-ext-diff",
                                 "--no-textconv", case["baseline"]["commit"],
                                 case["candidate"]["commit"], "--")[:200000]
        except WorkflowError as exc:
            result["diff_error"] = str(exc)
    return result


def list_cases(service):
    cases, errors = [], []
    with service.store.lock():
        for path in (service.store.root / "cases").glob("*/case.json"):
            try:
                case = service.store.load(path.parent.name)
                cases.append({key: case[key] for key in
                              ("id", "state", "report", "created_at", "updated_at",
                               "attempts", "total_attempts", "candidate", "verification")})
            except (WorkflowError, OSError, ValueError, KeyError) as exc:
                errors.append({"case": path.parent.name, "error": str(exc)})
    return {"cases": sorted(cases, key=lambda item: item["updated_at"], reverse=True),
            "errors": errors}


def environment():
    return {"python": platform.python_version(), "git_available": bool(shutil.which("git")),
            "switch": "not_verified", "provider": "not_verified",
            "message": "Console, provider sign-in and room handoffs must be verified in Switch. "
                       "This dashboard does not impersonate a Switch connection."}


def export_html(view):
    """A self-contained read-only report; all customer/code content is escaped."""
    case = view["case"]
    esc = lambda value: html.escape(str(value), quote=True)
    sections = []
    for item in view["evidence"]:
        sections.append(f'<section><h2>{esc(item["reference"]["path"])}</h2>'
                        f'<p>Integrity: {"valid" if item["valid"] else "FAILED"}</p>'
                        f'<pre>{esc(json.dumps(item.get("data", item.get("error")), indent=2, ensure_ascii=False))}</pre></section>')
    return (f'<!doctype html><html lang="en"><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>ProofDesk / {esc(case["id"])}</title>'
            '<style>body{background:#101416;color:#e5eceb;font:16px/1.6 system-ui;max-width:1000px;margin:50px auto;padding:24px}'
            'h1{font-size:42px}h2{font-size:20px;color:#9eddd0}section{border-top:1px solid #36433f;padding:24px 0}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#191f21;padding:20px}p{overflow-wrap:anywhere}</style>'
            f'<p>PROOFDESK / EXPORTED CASE EVIDENCE</p><h1>{esc(case["report"].get("summary", case["id"]))}</h1>'
            f'<p>{esc(case["id"])} · {esc(case["state"])} · {view["elapsed_seconds"]} seconds between first and latest event</p>'
            '<p>This is a local case record. Chat references are operator/agent supplied; this export does not independently authenticate them. '
            'Local acceptance does not imply merge, deployment, or customer delivery.</p>'
            f'<section><h2>Patch</h2><pre>{esc(view["diff_error"] or view["diff"] or "No candidate patch")}</pre></section>'
            f'<section><h2>Case and timeline</h2><pre>{esc(json.dumps(case, indent=2, ensure_ascii=False))}</pre></section>'
            + ''.join(sections) + '</html>')
