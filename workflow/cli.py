"""Agent-facing workflow surface. Review decisions have a separate entry point."""

import argparse
import json
from pathlib import Path
import sys

from .service import Service
from .store import WorkflowError


def parser():
    cli = argparse.ArgumentParser(description="ProofDesk case workflow")
    cli.add_argument("--root", default=".proofdesk", help="Local state directory")
    commands = cli.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--request-key", required=True)
    create.add_argument("--report", required=True, type=Path)
    clarify = commands.add_parser("clarify")
    clarify.add_argument("case_id")
    clarify.add_argument("--report", required=True, type=Path)
    reproduce = commands.add_parser("reproduce")
    reproduce.add_argument("case_id")
    reproduce.add_argument("--repo", required=True, type=Path)
    reproduce.add_argument("--revision", required=True)
    propose = commands.add_parser("propose")
    propose.add_argument("case_id")
    propose.add_argument("--revision", required=True)
    context = commands.add_parser("context")
    context.add_argument("case_id")
    context.add_argument("--room", required=True)
    context.add_argument("--thread", required=True)
    context.add_argument("--message", required=True)
    for name in ("verify", "draft", "close", "show", "summary"):
        commands.add_parser(name).add_argument("case_id")
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        service = Service(args.root)
        if args.command == "create":
            result = service.create(args.request_key, json.loads(args.report.read_text(encoding="utf-8")))
        elif args.command == "clarify":
            result = service.clarify(args.case_id, json.loads(args.report.read_text(encoding="utf-8")))
        elif args.command == "reproduce":
            result = service.reproduce(args.case_id, args.repo, args.revision)
        elif args.command == "propose":
            result = service.propose(args.case_id, args.revision)
        elif args.command == "context":
            result = service.context(args.case_id, args.room, args.thread, args.message)
        elif args.command == "verify":
            result = service.verify(args.case_id)
        elif args.command == "close":
            result = service.close(args.case_id)
        elif args.command == "draft":
            result = service.draft(args.case_id)
        elif args.command == "summary":
            result = service.summary(args.case_id)
        else:
            with service.store.lock():
                result = service.store.load(args.case_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.command == "verify" and not result["verification"]["passed"]:
            return 1
        if args.command == "reproduce" and result["state"] != "REPRODUCED":
            return 1
        return 0
    except (WorkflowError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
