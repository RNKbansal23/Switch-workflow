# Completed live run: PD-41b429bc34c2

On November 7, 2026, the user submitted a synthetic report in Discord's `clulessnerds-support` room. Concierge created the case and recorded source references, Builder reproduced the bug and committed a patch with regression coverage, and Verifier independently checked the pinned candidate. The person then recorded approval through the local dashboard; Concierge generated an unsent draft and closed the case.

| Item | Observed result |
| --- | --- |
| Team | ClulessNerds |
| Console / core | 0.40.1 / 0.31.0 |
| Runtime | Native Windows, PostgreSQL 17 |
| Provider | Signed-in Codex; the project did not add API billing |
| Chat connection | Discord connection `myDiscord` |
| Agents | clulessnerds-concierge, clulessnerds-builder, clulessnerds-verifier |
| Case | PD-41b429bc34c2 |
| Baseline | 1c3cec4af9a753e0b4d5ed14b0ca8d4c4ac882a8 |
| Candidate | c10966e1b9bb3d58f644c6762eff89887ea144e3 |
| Candidate attempts | 1 |
| Independent acceptance checks | 11/11 passed |
| Human review decisions | 1 approval, entered through the dashboard |
| Review reason | `for test` |
| Final state | CLOSED |
| Customer delivery | None; saved reply has `sent: false` |

The patch applies the percentage discount to the full order before rounding once with ROUND_HALF_UP. It changes `demo-app/order_total.py` and adds `demo-app/test_order_total.py`. The reported input now produces `9.05` rather than `10.05`. The [candidate diff](../evidence/live-run/candidate.patch) is preserved without Git author metadata.

The original case and hashed evidence remain under ignored `.proofdesk/cases/PD-41b429bc34c2/`. A complete read-only HTML report is saved locally at `.proofdesk/exports/PD-41b429bc34c2.html`; it includes local paths and reviewer information, so inspect it before sharing. A post-closure read verified referenced evidence hashes and confirmed the response is unsent. The operator's Discord screenshots document the visible handoffs; this record is not a substitute for a final demo recording.

## Setup findings

- Templates using the older local provider selector reported Codex unsupported even while managed-machine provider settings reported Signed in. An explicit managed-machine template with literal `codex` allowed creation of the three agents and two private rooms.
- The connection was named `myDiscord`; the earlier default `IDLE NO MORE` did not match that label.
- Some short permission requests were approved in Discord. An oversized request could not be approved there, and the managed agent did not expose it through the legacy local-session view. Enabling Auto mode for Concierge required the existing blocked turn to end and restart under its updated definition. Bypass permissions remained off in the recommended setup.
- The baseline repository had been created by CodexSandboxOffline, while the live workflow ran as the user's Windows account. Git rejected ownership until the operator approved an exact-path safe.directory entry for that repository. No wildcard trust was added.
- The local Switch server stopped during the workflow; the controller reported repeated reconnect failures and the API health check refused connections. After the user restored the server, the agents resumed the saved candidate rather than opening a replacement case.

These interruptions mean this is not an unattended-throughput or time-savings benchmark. It establishes one completed live workflow with a synthetic input and a bounded acceptance policy. It does not establish arbitrary bug-fixing support, authenticated reviewer identity against same-account agents, hostile-code isolation, merge, production deployment, or real customer delivery.

## Remaining presentation work

- Record a concise demonstration and preserve the actual chat handoffs.
- Check final repository/video accessibility and reproduce setup from a fresh checkout.
- Complete the event submission personally; the project does not automate registration or submission.
