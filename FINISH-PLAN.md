# ProofDesk: finish and submission plan

Prepared November 7, 2026 after reviewing the repository, research notes, workflow specification, agent contracts, template, and implementation. Current verification: `python -m unittest discover -s tests -q` passes all 18 tests.

## Approach

Choose **Track 1: Best Business Workflow** and finish ProofDesk. A support report becomes a reproduced failure, an agent-written patch, independent checks, a human decision, and a customer reply draft. The strongest achievable improvement is a real Switch conversation producing inspectable evidence; the local engine is already implemented.

Track 2 would be simpler for a new text-only project, but changing tracks here would discard useful work and require a new workflow, validation, and recording. This recommendation concerns the easiest credible completion of this repository, not a claim that business projects are inherently easier.

No plan guarantees a prize or eliminates setup failures. Each phase below has an observable exit condition and a time limit.

## Scope

- In: one synthetic order-discount report, one baseline-only repository, three agents, two rooms, an actual agent-written candidate, external acceptance checks, explicit human review, reply draft, transcript, reproducible instructions, video.
- Out: new product idea, general-purpose bug fixing, custom web application, production deployments, automatic merging, external customer messages, multiple messaging integrations, distributed agent machines, new authentication infrastructure.
- Optional after the live flow works: a portable static evidence report and a short build blog.

## Product story

**Pitch:** Support can see exactly why a proposed fix is ready for review, without chasing engineering or trusting an agent's unsupported claim.

**Example:** The demo order function returns `10.05` for a `10.05` item with a 10% discount. The documented result is `9.05`. Builder fixes the baseline; Verifier checks the committed candidate against the external eleven-example contract. A person reviews that exact revision before Concierge drafts a response.

The original defect ignores discounts. Rounding boundaries are additional checks, not a different description of the baseline defect.

| Actor | Where | Responsibility | Visible proof |
| --- | --- | --- | --- |
| Human | Support and engineering | Submit report; inspect and accept candidate | Original message and operator review event |
| Concierge | Support | Clarify, create case, hand off, draft response | Case ID, request reference, summary |
| Builder | Both rooms | Reproduce, edit baseline repository, commit, relay | Failing baseline, diff, full candidate SHA |
| Verifier | Engineering | Execute trusted checks on pinned snapshot | Actual check results and evidence path |

Switch is essential to the demonstrated collaboration: addressing participants, sharing room context, and carrying the handoffs. The Python engine remains runnable alone for testing; do not claim its unit tests require Switch.

## Existing work and remaining gaps

| Area | Evidence already present | Work needed |
| --- | --- | --- |
| Workflow engine | `workflow/`, 18 passing tests | Keep stable; fix only observed live blockers |
| Rehearsal | `scripts/demo.py`, prepared candidate fixtures | Keep labelled separately from live generation |
| Agent roles | `agents/*.md` | Confirm real runtime reads and obeys them |
| Switch setup | Draft `switch/proofdesk.template.yaml` | Validate on installed server; test mentions and handoffs |
| Human review | `workflow/review.py` | Person performs review during genuine run |
| Evidence | Local JSON events and hashed outputs | Preserve portable, sanitized evidence plus real chat references |
| Presentation | Setup and demo documentation | Add actual versions, recording, final results and links |

Previous Docker/Console observations are from November 4 and must be checked again. No live server, provider sign-in, template import, or current integration readiness has been established by this planning pass.

## Ordered action items

### 1. Prove the runtime — budget 45 minutes

- [ ] Open Switch Console and record installed Console/server versions in `docs/setup.md`.
- [ ] Confirm provider authentication through the Console and choose the provider that already works.
- [ ] Start a supported local server and use one available messaging bridge. Prefer an existing working connection; use bundled Mattermost only if that installation actually provides it.
- [ ] Link the human messaging identity and send one exact mention to a single agent.
- [ ] Confirm the agent can read this project and execute Python and Git from its working directory.

**Exit:** one actual room message produces a response containing a fact read from the local project.

**Decision:** if blocked after 30 minutes, diagnose the exact failed boundary: server, provider, bridge, identity, or permissions. Avoid spending the whole build window on optional Docker or chat infrastructure. Try a documented alternative supported by the installed release. If no agent can answer by the phase limit, prioritize resolving that blocker; a fixture recording alone does not establish a Switch workflow.

### 2. Prove handoffs — budget 35 minutes

- [ ] Import the draft template with an existing absolute directory, working provider, bridge, and unique prefix.
- [ ] Correct any template incompatibility using the installed version's accepted format; record the final working configuration.
- [ ] Confirm Concierge/Builder membership in support and Builder/Verifier membership in engineering, with the human in both.
- [ ] Test human-to-Concierge, Concierge-to-Builder, Builder-to-Verifier, and Builder-to-Concierge addressing individually using harmless acknowledgements.
- [ ] Save actual room and message references in `docs/live-run.md`; record any manual forwarding honestly.

**Exit:** each participant receives its expected handoff through Switch. Room links alone do not prove membership or addressing.

**Fallback:** if cross-room discovery alone fails, keep three roles in one working room, update instructions/template to match, and demonstrate the complete exchange there. Claim two-room coordination only if observed. If an individual handoff requires human forwarding, identify it as assisted and fix automatic routing before making an automation claim.

### 3. Complete one genuine case — budget 90 minutes

- [ ] Run `python -m scripts.demo --prepare-only` to create a fresh baseline-only repository; retain its path and full SHA.
- [ ] Send the live request from `docs/demo.md` with those actual values to Concierge.
- [ ] Have Concierge collect a complete report and create a case keyed by the real originating message ID.
- [ ] Have Builder record actual baseline reproduction, edit only the supplied demo repository, add useful regression coverage, and commit a focused candidate.
- [ ] Have Builder propose the full SHA and hand off through Switch to Verifier.
- [ ] Have Verifier execute `python -m workflow verify <case-id>` and post the actual verdict, check count, SHA, and evidence reference.
- [ ] Relay the result to support and let the person inspect the diff and verification evidence.
- [ ] Have the person run `python -m workflow.review approve ...` with the full candidate SHA, their name, and a review reason.
- [ ] Have Concierge generate the reply draft, show it in support, and close the local case when the owner requests closure.
- [ ] Preserve case events, diff, check output, draft, and real conversation references.

**Exit:** one genuine Switch-driven case reaches CLOSED with a live-generated candidate, matching passing checks, operator approval, and an unsent draft.

Do not force an agent to make a bad fix for drama. If it succeeds immediately, show the separately labelled incomplete fixture later. Existing agents share the same OS account: separate roles and a review command do not authenticate a human or prevent arbitrary shell misuse.

### 4. Make the result easy to inspect — budget 40 minutes

- [ ] Create a sanitized `evidence/live-run/` bundle containing a concise case summary, patch, relevant check results, reply draft, and transcript/screenshots.
- [ ] Preserve original revision/hash references where possible; explain any redaction. Copy reviewed evidence for publication without modifying the original local case store.
- [ ] Record elapsed case time from timestamps, checks passed/total, candidate attempts, and recorded human review decisions. Describe manual forwarding and other human help separately.
- [ ] If time remains, add `scripts/export_report.py` to produce a portable read-only HTML report from an existing case and referenced evidence.
- [ ] Show report, baseline result, diff, full candidate SHA, independent checks, review reason, timeline, and draft. Mark live versus fixture origin prominently.

**Exit:** someone can understand what failed, what changed, who checked it, and what the person accepted without searching raw JSON.

The report is optional presentation work. Skip it if the live workflow or recording is incomplete. It needs no web server, framework, database, or dashboard. Escape customer text and code when generating HTML, and do not expose approval controls.

### 5. Verify the delivery — budget 40 minutes

- [ ] Run `python -m unittest discover -s tests -q` after any code changes.
- [ ] Run `python -m scripts.demo` and confirm actual incomplete-fixture rejection and corrected-fixture acceptance, clearly labelled as rehearsal.
- [ ] Repeat the documented setup from a separate checkout/copy with a fresh state directory and new case ID; confirm required files are included.
- [ ] If time allows, repeat the genuine live case from a fresh baseline to establish that setup and handoffs are repeatable.
- [ ] Show clarification for missing input and rejection evidence for the incomplete candidate. Use existing automated tests to substantiate stale approval and deduplication behavior.
- [ ] Update `docs/VALIDATION.md` with commands, date, actual results, live case reference, versions, and remaining limits.

**Exit:** the documented commands work and the presentation's claims match observed results. Additional changes receive checks proportional to their behavior; a documentation-only edit does not require new mirrored unit tests.

### 6. Record and package — budget 50 minutes

- [ ] Record a roughly three-minute demonstration using the sequence below; this is a suggested duration, not a verified event rule.
- [ ] Update `README.md` with the pitch, track, real outcome, architecture, actual Switch role, tested setup, demo link, reusable template, evidence link, and limitations.
- [ ] Preserve useful existing documentation and update `WORKFLOW-PLAN.md` checkboxes only when the corresponding work has actually been completed.
- [ ] Inspect the final changed-file list, exclude `.proofdesk/`, credentials, and private data, and include all needed source/configuration files.
- [ ] Verify repository and video access from a signed-out browser where appropriate.

**Exit:** a reviewer can open the video and repository and follow the setup without private files.

### 7. Submit personally — reserve at least 30 minutes

- [ ] Open the real submission dashboard and verify its actual required fields early; do not assume deployment or video-length requirements.
- [ ] Select Business Workflow and supply the requested repository, video, and README information.
- [ ] Submit personally before the cutoff and retain the confirmation.
- [ ] Write the optional blog only after the main entry is safely submitted; use real screenshots and explain the setup problem, solution, and limits.

Official rules prohibit automated registration/submission; AI-assisted development is allowed. Sources: [schedule](https://www.wemakedevs.org/hackathons/switch/schedule), [rules](https://www.wemakedevs.org/hackathons/switch/rules).

## Demo script

| Time | Show | Point |
| --- | --- | --- |
| 0:00–0:20 | Synthetic complaint and wrong total | A concrete support problem |
| 0:20–0:45 | Switch rooms, roles, Concierge intake | Where the workflow starts |
| 0:45–1:25 | Builder handoff, baseline failure, actual diff | Work produced by the connected agent |
| 1:25–1:55 | Verifier handoff and eleven executed checks | Evidence over unsupported claims |
| 1:55–2:25 | Person inspects and approves the exact SHA | Clear review responsibility |
| 2:25–2:45 | Reply draft and case summary | Useful business output |
| 2:45–3:00 | Setup command, template, limitations | Reproducibility |

Trim waits with disclosed edits. Do not splice fixture output into a purported live case. If showing fixture rejection, label it on screen and give it a separate short segment.

## Time and cut decisions

The official deadline is **November 7, 2026, 11:59 PM IST**. At planning time it was approximately **4:53 PM IST**, leaving about seven hours. The budgets total roughly 6 hours 10 minutes, leaving a small buffer; they are estimates, not measured task durations.

If behind schedule, cut the HTML report, blog, additional failure demonstrations, and visual polish in that order. Preserve the live case, verification, human review, honest evidence, recording, and submission buffer. If live integration remains incomplete, describe that limitation rather than presenting a prepared local rehearsal as a completed live integration.

## Final acceptance checklist

- [ ] One real request flows through Switch to a completed local case.
- [ ] The candidate is generated from a baseline-only repository during that run.
- [ ] Verification executes against the exact committed candidate and reports the actual result.
- [ ] A person reviews that revision; the draft does not claim deployment or delivery.
- [ ] A separately labelled rehearsal demonstrates rejection without invented agent behavior.
- [ ] Published instructions and artifacts reproduce the demonstrated scope.
- [ ] Repository, README, evidence, and video agree about what works.
- [ ] The person receives submission confirmation before the published cutoff.

Judging emphasizes Switch usage, technical execution, creativity/impact, and presentation. This plan maps those to visible handoffs, a repeatable case, reviewable evidence, and a concise demonstration rather than speculative feature count. [Official challenge and judging](https://www.wemakedevs.org/hackathons/switch).
