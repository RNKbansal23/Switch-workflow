# ProofDesk recording runbook — ClulessNerds

Target: approximately 4 minutes 30 seconds. This is our suggested presentation length, not a verified event requirement. Check the submission form for any actual limit.

Record a narrated walkthrough of the genuine completed run, not a claim that agents are executing again during the recording. Use the same case throughout: **PD-41b429bc34c2**. Its real candidate is **c10966e1b9bb3d58f644c6762eff89887ea144e3**.

## 1. Prepare before pressing Record

Use the screen recorder already available on your machine. Select a 1920×1080 capture if your screen supports it, approximately 30 fps, and microphone audio. Make a ten-second test to confirm readable text and audible narration. Webcam and music are optional; neither is needed to understand this project.

Close unrelated tabs/windows and enable Do Not Disturb. Keep Switch Console and its server terminal open. Avoid recording tokens, provider account/billing screens, email, or unrelated community conversations. Increase browser zoom until the report, diff and results are comfortably readable. Keep the cursor still while explaining a result.

### Prepare these five views

1. **ProofDesk dashboard** in the browser, with PD-41b429bc34c2 ready to open. This supplies the opening and final result.
2. **Switch Console → Your Agents**, showing all three ClulessNerds agents and their Codex provider. Use Your Rooms briefly if useful.
3. **Discord → clulessnerds-support → original 6:32 PM report thread**, scrolled to the original report. Then locate Concierge's case-created and Builder-handoff messages.
4. **Discord → clulessnerds-engineering → PD-41b429bc34c2 thread**, with Builder's candidate handoff and Verifier's final 11/11 result located in advance. It is fine to switch channels within the same Discord window instead of opening another tab.
5. **PowerShell**, already in the project root, ready to run the final read-only summary. Keep the narrator script on another screen or print it.

### Start the dashboard only if it is not already running

In a separate PowerShell window:

```powershell
cd "F:\open source projects\switchAiProject"
.\start-proofdesk.cmd
```

Open the complete private URL printed by the launcher. Let the page finish loading before recording: it removes the token from the address bar. Keep that terminal open but out of the capture. If the dashboard is already open and refreshing, reuse it; do not start another server on the same port.

### Run these checks before recording

In another PowerShell window:

```powershell
cd "F:\open source projects\switchAiProject"
python -m unittest discover -s tests -q
python -m workflow summary PD-41b429bc34c2
```

The test suite previously passed 26 tests. Use the actual current output rather than quoting a count if it changes. The summary should show CLOSED, 11 checks passed out of 11, one candidate attempt, one human decision and a response reference. If something differs, investigate before recording rather than editing state.

Do not run `workflow verify`, propose a candidate, grant another approval, reset the repository, or reopen the CLOSED case for the recording. Reverification clears approval/draft state; it is unnecessary here.

## 2. Exact recording script

### 0:00–0:25 — Outcome and problem

**Show:** dashboard case desk, then open PD-41b429bc34c2 with its CLOSED badge visible.

**Say:**

> Hi, I'm Rajat from ClulessNerds. This is ProofDesk: a support-to-engineering workflow built with Switch. It turns a bug report into a reproduced failure, a proposed patch, independent checks, and a human-reviewed reply draft. I'll walk through a real completed Switch run using a synthetic customer report.

**On-screen caption:** `ProofDesk | ClulessNerds | Business Workflow` and `Completed live run walkthrough · synthetic report`.

### 0:25–0:50 — Show why Switch matters

**Show:** Switch Console → Your Agents. Point briefly to Concierge, Builder and Verifier. If switching to Your Rooms is quick, show support and engineering too.

**Say:**

> Three Codex-powered agents have separate responsibilities. Concierge handles support intake. Builder reproduces and fixes the issue. Verifier checks the exact committed candidate. Switch connects them through our Discord support and engineering rooms and carries the handoffs and shared context. ProofDesk's local engine records the case and enforces the review sequence.

Do not spend this segment opening settings, showing provider credentials, or explaining installation problems.

### 0:50–1:20 — The actual report and first handoff

**Show:** original Discord support thread. Pause on the initial report, then scroll to Concierge's case creation and Builder's acknowledgement.

**Say:**

> The report is concrete: a 10.05 order with a ten-percent discount incorrectly returns 10.05. The documented result is 9.05, with the discount applied before final rounding. I supplied a broken baseline repository and its exact revision. Concierge created this case and handed it to Builder. These are the messages from the actual run.

**Visual check:** case ID matches the dashboard. No need to read a forty-character commit aloud.

### 1:20–1:55 — Reproduction and actual patch

**Show:** dashboard → case → Checks. Scroll to **Baseline reproduction**, where the reported example fails. Then choose **Patch** and point to the discount formula and the added test file.

**Say:**

> Builder first reproduced the failure on the baseline. This check records the wrong result rather than relying on the agent's description. The candidate then changes the calculation to apply the percentage discount to the full order and round only once. Builder also added regression coverage, including a case that catches rounding each item too early. The patch is tied to this immutable commit.

The candidate test case `order_total('0.05', 3, '10') == '0.14'` is useful to point out if it is visible. Keep scrolling slow enough to follow.

### 1:55–2:30 — Independent verification

**Show:** engineering thread → Builder's handoff to Verifier → Verifier's final result. Then dashboard → Checks → independent candidate checks.

**Say:**

> Builder handed the candidate to Verifier through Switch. Verifier ran the independently maintained acceptance suite against a fresh export of that exact Git revision. All eleven documented checks passed, including the reported failure, discount boundaries, rounding examples and invalid inputs. The evidence records the revision, expected and actual results, command status and timing. This proves the documented contract examples, rather than every possible monetary input.

**Caption:** `11/11 independent acceptance checks passed`.

### 2:30–3:05 — Human decision and completed output

**Show:** dashboard → Overview → recorded review, then the unsent response draft. Choose Timeline to show approval followed by draft and closure.

**Say:**

> Passing checks did not automatically approve the patch. I recorded the human decision in the dashboard against that candidate and its verification evidence. Concierge then generated this customer reply draft and closed the local case. The draft explicitly says deployment has not been confirmed, and it remains unsent. Closing the case does not merge code, deploy it, or contact a customer.

The real recorded review reason is `for test`. Do not claim a stronger review reason than was entered. Do not try to click Accept again: the case is already closed.

### 3:05–3:30 — Traceability and portable evidence

**Show:** Timeline briefly, then click **Export report**. Open the downloaded HTML after reviewing its contents if you want a second shot; otherwise show the download completing.

**Say:**

> The timeline keeps the report, candidate, verification and review events together. Evidence hashes detect ordinary changes through the intended workflow. This read-only report makes the patch and supporting records easy to inspect outside the dashboard. The local prototype does not provide tamper-proof auditing or authenticated separation from unrestricted agents sharing the same operating-system account.

Do not show the private dashboard launch token in a terminal. The export contains local paths and reviewer details; inspect before sharing it separately.

### 3:30–4:00 — Reproducibility and final state

**Show:** PowerShell and run:

```powershell
python -m workflow summary PD-41b429bc34c2
```

Keep CLOSED, checks_passed/checks_total, repair_attempts and human_decisions readable. Briefly switch to README setup commands or the prepared successful test output if time remains.

**Say:**

> The final state is recorded by executable code: closed, eleven checks passed, one candidate attempt, and one human approval. The local application uses Python and Git with no third-party runtime dependencies. The repository includes the setup instructions, role contracts, Switch template, test suite, and live-run record.

Only mention 26 automated tests if the pre-recording test run still passed that count.

### 4:00–4:25 — Recovery and closing statement

**Show:** dashboard Overview with CLOSED visible; optionally briefly show the recovery notes in `docs/LIVE-RUN.md`.

**Say:**

> This run needed human permission handling and a server restart, so I am not presenting it as fully unattended. When Switch came back, the workflow resumed the saved case and candidate rather than creating replacement work. ProofDesk demonstrates a useful business workflow where agents collaborate through Switch, while evidence and a human decision determine what can be accepted. Thank you.

End on the product screen. If adding repository/video links in editing, use only real, accessible links after they exist.

## 3. Editing and export

- Cut window-switching delays, loading screens and long waits. If showing accelerated execution footage, label it with its actual speed.
- Keep the opening disclosure that this is a walkthrough of a completed live run. Do not splice prepared fixture results into this case.
- The live candidate passed on its first attempt. Do not claim Verifier rejected it first. Rejection behavior belongs to the separately labelled fixture rehearsal and is optional extra footage.
- Keep the main capture focused on your project rooms rather than unrelated server members or conversations. Blur private material that enters the capture.
- Make narration louder than any optional music. Use captions for case state and check counts, not paragraphs of duplicated text.
- Export a common MP4 format supported by your recorder/editor. Play the entire export once: check audio, text readability, transitions, privacy, and that all screens refer to the same case/revision.
- Upload the actual recording, confirm reviewer access, add its real link to README and the submission form, then submit personally. Check the form's current fields and length limit.

## 4. If you need a shorter edit

For approximately three minutes, keep the opening, agents/rooms, report/handoff, patch, Verifier's actual result, human review/draft and final state. Cut the export demonstration and reduce the recovery explanation to one sentence. Preserve the completed-run disclosure and deployment limitation.

## 5. If you want to film fresh execution instead

Use a new baseline-only preparation with `python -m scripts.live --prefix clulessnerds`, a new actual request and a new case. Record the genuine work, review and final output. Do not reuse this closed case as if it were new, and do not fabricate elapsed time. Leave time for permission prompts or outages. The completed-run walkthrough above is sufficient to show the existing genuine result without another execution.
