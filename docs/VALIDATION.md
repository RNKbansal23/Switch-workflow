# Validation record

## November 7 operator workspace

- `python -m unittest discover -s tests -q`: **26 tests passed**, including eight HTTP/presentation/live-preparation regression tests.
- `node --check workflow/web_assets/app.js`: passed.
- Chromium browser QA at **390, 768, and 1440 pixels**: intake, escaping of script-like customer text, search, setup screen, actual diff/check rendering, keyboard tabs, real asynchronous verification, review, draft, closure, and HTML download passed. No page JavaScript errors or horizontal document overflow observed.
- Browser tests used disposable prepared fixture state. Their operator decisions are test events, not a human approval of an actual customer case and not proof of Switch integration.
- Evidence corruption is shown in the interface and blocks approval; a stale verification hash is refused even when the candidate SHA is unchanged.
- `python -m scripts.live`: created a baseline-only repository and a concrete request file, without candidate fixtures in its Git history.
- `python -m scripts.doctor`: Python/Git available; Docker engine not ready; provider sign-in and live Switch unverified.
- Official Switch Console Windows installer downloaded from the installation page's GitHub release link: version **0.40.1**, Windows Authenticode status **Valid**, signer **SandboxAQ**. Installer opened for user-operated installation. This does not establish installation completion or a running server.
- Follow-up after the user completed installation: Console **0.40.1** running; startup log reports **switch-core 0.31.0**; local runtime is **native**, using PostgreSQL 17; local API `/health` on port **65081** returned **200**. Provider sign-in, template import and genuine agent handoffs remain pending.

The screenshot/report artifacts are local under ignored `.proofdesk/qa/`. Full screen-reader and exhaustive contrast audits remain unperformed. Live template import, real provider-generated fixes, chat handoffs, and recording remain pending.

## Earlier engine checks

Observed locally on November 4, 2026, using Python 3.11.9 and Git 2.51.0.windows.1.

## Executed checks

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 18 tests passed |
| `python -m scripts.demo` | Baseline reproduced, incomplete fixture rejected, corrected fixture VERIFIED with 11/11 checks; zero human decisions |
| Markdown reference/fence check | 24 Markdown files checked at that point; local links resolved and fences balanced |
| YAML parsing and relationship check | Three agents, two private rooms, valid local membership/link references |
| `python -m compileall -q workflow scripts tests` | Passed |
| `git diff --check` | Passed for tracked changes; Git emitted its normal LF/CRLF notice |

The final added validation document is not included in the earlier Markdown count. The structural YAML check used an already installed parser only as a development check; the application does not depend on it.

## Rehearsal evidence

Case `PD-e2f3cd90f8b9` was left VERIFIED in the ignored local `.proofdesk/` store. It used two prepared candidate attempts and recorded no human approval. Its candidate fixture commit was `b1ac6985746ccca0e642091702a992b00bb6a318`. A fresh run creates its own local repository, commits, IDs, and evidence.

Tests exercise complete rejection/revision/review/draft/closure, stale SHA refusal, approval invalidation after changes/reverification, modified baseline and verification evidence, deduplication, clarification, unsupported policies, repair budget, stale retry, path traversal, writer locking, infrastructure errors, malformed runner output, uncommitted source changes, and CLI failure status.

## Not established by these checks

- A live Switch template import or room exchange.
- Authenticated human identity or protection from a malicious same-account agent.
- Arbitrary customer-bug support beyond the fixed order-total policy.
- Correctness for every numeric input or production monetary use.
- A real customer message, repository merge, production deployment, video recording, registration, or event submission.
- Windows Docker/Console/provider readiness beyond the observations in [setup](setup.md).

The next acceptance milestone is the genuine baseline-only run in [the demo runbook](demo.md), with actual Switch room/thread references and a person performing review.
