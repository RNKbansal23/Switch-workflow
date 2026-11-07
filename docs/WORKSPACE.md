# Operator workspace

Run from the repository root with Python 3.11+ and Git:

```powershell
python -m workflow.web
```

Open the complete URL printed in your terminal. It contains a private session token in the URL fragment; the browser removes it from the address bar and retains it in tab session storage. A server restart generates a new token, so reopen the new terminal URL. If `python` is unavailable in PowerShell, invoke your installed Python executable directly or use `py -3.11` where the launcher is installed.

The server binds only to `127.0.0.1`, checks the Host and Origin headers, requires the token for all case APIs, limits request bodies, and serves a fixed list of assets. No public deployment is configured. A hosted static copy cannot access these local Python/Git processes and is not a substitute for this workspace.

## What works

- List/search/filter actual case records, with counts derived from their current states.
- Create an order-total-v1 report, with a stable request reference for deduplication.
- Copy a handoff for an existing case into Switch; replace the default agent prefix when necessary.
- Read original facts, the actual baseline-to-candidate Git diff, independent check results, source-context evidence, and recorded events.
- Execute verification asynchronously and wait for its real result. A verification rejection remains a rejection.
- Accept/reject a verified candidate using the operator's name and reason. The request binds to both the full candidate revision and the verification evidence hash; stale review pages are refused.
- Generate an unsent reply draft after approval and close the local case explicitly.
- Download a standalone, escaped HTML report containing the case, timeline, diff, and evidence. Review local paths and any report content before sharing.
- Refresh every five seconds while visible. Updates do not replace a review form while it is focused; a stale submission is still rejected by the server.

The trusted acceptance contract is deliberately bounded to the sample order-total policy. User-facing records, diffs, states, counts, checks, and review decisions are dynamic; the product does not pretend to support arbitrary repositories or acceptance policies.

## Live versus rehearsal

`python -m scripts.live` prepares only the broken baseline and a concrete Switch message. It does not create a candidate, dispatch an agent, or fabricate a transcript. The live connected provider must perform the work.

`python -m scripts.demo` executes prepared fixture commits and stops before approval. It remains useful for demonstrating rejection and checking the local engine. Its cases are labelled synthetic fixture input.

The dashboard never marks Switch connected based on local HTTP health. The setup screen explicitly says live Switch is unverified. Actual source references can be attached by Concierge using:

```powershell
python -m workflow context <case-id> --room <real-room-reference> --thread <real-thread-reference> --message <real-message-reference>
```

Those values are recorded as operator/agent supplied, not independently authenticated by this application. Inspect them in the exported evidence report.

## Local trust limits

The browser token protects access from ordinary unauthenticated HTTP requests; it does not isolate unrestricted agents running as the same OS account. Such an agent can access files or launch its own process. Operator review remains an explicit local convention, not proof of authenticated human identity. Candidate execution is not a hostile-code sandbox. Keep merge/deployment/customer delivery manual.

## Design and verification

The interface uses a dark utilitarian workspace, mint/cyan emphasis, system sans typography, monospaced evidence labels, flat dividers, and a visible case-to-evidence hierarchy. It needs no remote fonts or images. Motion is limited to short control transitions and dialog entrance, disabled by reduced-motion preferences.

Browser QA exercised real local HTTP data at 390, 768, and 1440 pixels, including intake, text escaping, search, setup, patch/check inspection, keyboard tab navigation, asynchronous verification, review, draft, closure, and download. No horizontal document overflow was observed at those widths. Keyboard focus styles and semantic labels are implemented; a full screen-reader audit and exhaustive contrast audit have not been performed.

For repeatable browser QA, point `PLAYWRIGHT_MODULE` at an installed `playwright-core` directory and optionally `PLAYWRIGHT_CHROMIUM_EXECUTABLE` at Chromium, then run `python -m scripts.browser_qa`. This uses disposable prepared fixtures and stores screenshots under ignored `.proofdesk/qa/`. It never approves or closes your actual cases.
