# ProofDesk: detailed workflow specification

## Product promise and limits

A support teammate supplies a bug report. Concierge clarifies it, Builder produces an evidenced reproduction and candidate commit, Verifier runs independent checks, and a human reviews the exact candidate before Concierge drafts the response. The first supported policy is **order-total-v1**, defined in [the sample application's contract](../demo-app/README.md).

This is a bounded prototype. It does not promise correctness for every possible input, arbitrary bug diagnosis, production deployment, or tamper-proof auditing. The local rehearsal executes prepared fixture revisions; the live Switch workflow must be demonstrated separately.

## Architecture and ownership

| Layer | Owns | Does not own |
| --- | --- | --- |
| Switch | Rooms, participant context, addressing, cross-room handoffs | ProofDesk state transitions or test verdicts |
| Coding-agent provider | Agent reasoning, tools, execution permissions | Human identity verification by ProofDesk |
| ProofDesk service | State machine, commit binding, evidence, retry budget | Messaging-platform authentication |
| External acceptance runner | Documented checks against an exported Git snapshot | General proof of correctness or an OS sandbox |
| Human reviewer | Acceptance/rejection of a named candidate | Automatic merge/deployment |

Agents use Python commands from the project directory and Switch tools supplied by their runtime. The local application needs no third-party Python runtime dependencies. A shared local state directory works for agents on one machine. Multiple hosts require a separately designed shared service; do not point separate local stores at the same case ID and assume synchronization.

## Rooms and participants

`proofdesk-support`: human, Concierge, Builder. Keep a customer-facing summary, current state, evidence references, and next actor in the case thread.

`proofdesk-engineering`: human, Builder, Verifier. Keep reproduction commands, candidate revisions, and verification verdicts in an engineering thread.

Link the rooms in both directions. Builder belongs to both and relays outcomes. Concierge does not need membership in engineering. A link alone does not grant access. The draft template uses one owner with owner-agents addressing; a second person's permissions need explicit configuration and validation. [Switch template](../switch/proofdesk.template.yaml).

## Input and case record

Reports contain `policy`, `summary`, `steps`, `expected`, and `actual` strings. Missing fields create CLARIFYING rather than starting work. Unsupported policies are refused. This version does not translate arbitrary natural-language reports into new acceptance suites.

Use a stable platform event/message ID as the request key, namespaced by platform/workspace when integrating. Repeated keys with the same report return the existing case; a different report under that key raises an error. A new conversation creates a new request key.

Each case has an opaque `PD-` ID, timestamps, the report, missing fields, baseline repository and full commit, candidate commit, verification/approval/draft references, repair counters, and an ordered event list. The whole record is replaced atomically while a store-wide exclusive lock prevents concurrent mutations through the CLI.

## State transitions

| From | Action and precondition | To |
| --- | --- | --- |
| Intake | Required fields missing | CLARIFYING |
| Intake | Complete supported report | NEW |
| CLARIFYING | Supply remaining fields | NEW |
| NEW | Named complaint assertion fails on baseline; runner output is valid | REPRODUCED |
| NEW | Baseline passes or has infrastructure error | NEW; evidence retained |
| REPRODUCED | Propose a different committed revision | PATCH_READY |
| PATCH_READY | All required external acceptance checks pass | VERIFIED |
| PATCH_READY | Candidate fails; budget remains | PATCH_READY |
| PATCH_READY | Candidate fails; budget exhausted | NEEDS_HUMAN |
| VERIFIED | Human accepts matching full SHA | APPROVED |
| VERIFIED | Human rejects matching full SHA | NEEDS_HUMAN |
| APPROVED | Generate response draft, validate evidence, close | CLOSED |
| NEEDS_HUMAN or PATCH_READY | Human grants retry for current SHA and gives reason | PATCH_READY, budget reset |
| PATCH_READY, VERIFIED, or APPROVED | Propose a different candidate within budget | PATCH_READY; prior verdict, approval, and draft cleared |
| VERIFIED or APPROVED | Re-run verification | VERIFIED or failure state; approval and draft cleared |

CLOSED cases are terminal. Opening follow-up work requires a new case. Reproposing the current SHA is idempotent, not a new attempt. Two distinct candidates are allowed per budget; the total counter survives human retry.

## Evidence contract

Export the **full committed repository revision** with Git archive to a fresh temporary directory. Uncommitted working-copy changes do not affect the result. Refuse unsafe archive paths, symlinks, oversized archives, and a candidate identical to its failing baseline.

Run the acceptance policy from the trusted workflow code outside the candidate tree. Record the full SHA, Python version, policy name, runner hash, timestamps, duration, exit status, stdout/stderr, expected/actual check results, and infrastructure status. A missing/import-broken module is not evidence of the reported business bug. Successful verification requires the complete expected check list and a successful process status.

Evidence files are separately written and hashed. Verify hashes before review/closure. This detects ordinary changes through the intended application path, but an account owner who can rewrite state and hashes can forge it. The candidate code runs with that user's privileges; a fresh directory is isolation of source state, not a hostile-code sandbox.

The present suite covers eleven contract examples: the reported rounding case, an ordinary discount, no discount, rounding down, full discount, empty order, negative price, negative quantity, fractional quantity, excess discount, and non-finite price. Broader monetary edge cases and fuzz/property testing are future work.

## Human review

`workflow.review` is deliberately separate from the agent-facing `workflow` CLI. Agents must not invoke it, impersonate a reviewer, or directly edit records. The human names the full candidate SHA and supplies their name and reason. Changed or reverified candidates lose earlier approval.

This is a local operator workflow, **not authenticated human identity enforcement**. All agents currently share an owner's account, so prompt instructions and a separate entry point do not stop an agent with unrestricted shell access. A stronger deployment requires separate OS/service identities and a reviewer-only authenticated endpoint. Merging and deployment remain manual.

## Response and closure

The deterministic draft identifies the case and reviewed candidate and explicitly says deployment is unconfirmed. It is stored as evidence with `sent: false`. Concierge can adapt the wording in chat while keeping those facts accurate. Closing requires an approved matching candidate, unchanged verification evidence, and a draft tied to that candidate. No external customer message is sent.

## Failures and recovery

- Offline agent: keep the case pending and post the next required actor. Resume by case ID rather than creating another case.
- Busy store: wait for the current operation to finish and retry. A stale lock after a crash requires the operator to confirm no process is running before removing it.
- Verifier timeout: record rejection evidence and request diagnosis; never mark a timeout as a passing test.
- Missing baseline repository: restore its recorded commit locally; never silently change the baseline.
- Tampered evidence: stop review/closure and rerun the needed check from trusted source.
- Exhausted budget: ask a human for a recorded retry; do not spawn additional repair loops.
- Policy changes: rerun verification and review; if the baseline contract changes, open a new case and reproduce it under the new contract.

## Definition of done

Local MVP: tests pass; rehearsal shows real reproduction/rejection/pass; human entry point is separate; draft and closure are exercised in tests; no fake live claims.

Hackathon-ready workflow: import the template on a recorded Switch version, prove each addressing boundary, complete a genuine baseline-only agent repair, preserve actual room/thread references and transcript, perform human review, verify fresh setup, and record an honest demo. Those live items remain pending until observed.
