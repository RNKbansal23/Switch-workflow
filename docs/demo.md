# Demo runbook

Run commands from the ProofDesk project root. The local store defaults to `.proofdesk`; use `python -m workflow --root <directory> ...` to select another store. The review command has its own matching `--root` option.

## A. Labelled local fixture rehearsal

```powershell
$run = python -m scripts.demo | ConvertFrom-Json
$run
$caseId = $run.id
python -m workflow show $caseId
python -m workflow summary $caseId
```

Expected outcome: a real baseline reproduction, rejection of the incomplete fixture, then VERIFIED with 11/11 acceptance checks on the corrected fixture. Neither candidate is claimed to have been generated live. The rehearsal does not grant approval or close the case.

Open the case record and the evidence files it references under `.proofdesk/cases/<case-id>/`. Inspect the candidate in the printed fixture repository using Git. Temporary verification snapshots are removed after execution; command output, hashes, and verdicts remain in evidence.

After a person inspects that evidence, they can run:

```powershell
$reviewer = Read-Host 'Your reviewer name'
$reason = Read-Host 'What did you review and why do you accept this candidate?'
python -m workflow.review approve $caseId --commit $run.candidate.commit --reviewer $reviewer --reason $reason
python -m workflow draft $caseId
python -m workflow close $caseId
python -m workflow summary $caseId
```

The resulting draft is a JSON evidence file containing the reply text and `sent: false`. Closure means local patch acceptance only. If the person declines, use `reject` with the same required arguments instead; no draft or closure should follow rejection.

## B. Genuine live Switch run

First complete [Switch setup](setup.md). Prepare a separate repository containing only the broken baseline:

```powershell
$prep = python -m scripts.demo --prepare-only | ConvertFrom-Json
$prep
```

In the support room, send the following with the actual repository path and full baseline SHA from `$prep`, and the actual configured agent name:

> @proofdesk-concierge Open a synthetic order-total-v1 case. On the supplied baseline, order_total('10.05', 1, '10') returns 10.05; the documented result is 9.05. The baseline repository and full commit are shown below. Ask Builder to reproduce and prepare a patch, then have Verifier check the exact candidate. Return the evidence for my review. Do not use prepared candidate fixtures, approve on my behalf, merge, deploy, or send a real customer response.

The Concierge must collect the real message/thread references rather than inventing them. Follow the role contracts in [agents/](../agents/concierge.md).

Expected exchanges:

1. Concierge creates a case with the stable message ID, posts its ID, and addresses Builder.
2. Builder acknowledges, moves detailed work to engineering, and records baseline reproduction.
3. Builder edits/commits in the baseline-only demo repository and proposes that SHA.
4. Builder addresses Verifier; Verifier runs the trusted suite and reports its actual verdict.
5. Failed checks return to Builder within the repair budget; a pass returns to support.
6. A person reads the actual candidate/evidence and runs `workflow.review` for that full SHA.
7. Concierge drafts the accurate response, closes the local case, and posts the summary.

Do not force or fabricate a rejection if a live Builder fixes the issue on its first attempt. Demonstrate rejection separately using the labelled fixture rehearsal.

## Recovery commands

Inspect: `python -m workflow show <case-id>`.

Reverify: `python -m workflow verify <case-id>`; this clears any previous approval/draft.

Human-authorized retry: `python -m workflow.review retry <case-id> --commit <current-full-sha> --reviewer <name> --reason <reason>`.

Each new demo run uses fresh IDs. No recursive delete/reset command is needed. If a case is CLOSED, open a new case instead of editing its JSON.

## Presentation sequence

Suggested three-minute narrative: show the complaint and room participants; show actual reproduction and handoff; inspect candidate verification and human decision; open the final evidence and draft. State whether the recording is a fixture rehearsal or live Switch execution. Include setup instructions and limitations alongside the recording.
