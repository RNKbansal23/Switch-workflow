# ProofDesk submission content

Prepared from the completed live workflow. The submission page's public text view remained at its loading message, so the headings below are an answer bank, not verified form-field labels. The participant must enter the submission personally under event rule 3(b).

## Project name

ProofDesk

## Team name

ClulessNerds

## Primary track

Best Business Workflow

## Tagline

From a support report to a verified patch and a human-reviewed reply, through Switch.

## Short description

ProofDesk connects three Codex-powered agents through Switch and Discord to reproduce a reported bug, prepare a committed fix, independently verify the exact revision, and return evidence for human review. A local dashboard displays the patch, checks, timeline, approval, and unsent reply draft.

## Project description

Support teams need more than an agent saying a bug is fixed. They need a reproducible failure, an inspectable patch, independent checks, and a clear review decision.

ProofDesk coordinates that process through Switch. Concierge collects the report in a Discord support room and creates a case. Builder reproduces the failure, writes a focused patch and regression tests, then hands the committed candidate to Verifier in an engineering room. Verifier executes a separate acceptance suite against a fresh export of that exact revision. A person reviews the evidence in the dashboard before Concierge drafts the response and closes the local case.

Our completed live run used a synthetic order-discount defect. The calculation returned 10.05 instead of 9.05. The agents produced one candidate, passed all 11 independent acceptance checks, obtained one human approval, and closed the case with an unsent reply draft. No merge, deployment, or customer delivery was automated.

## How Switch is used

Switch connects the Codex-powered Concierge, Builder, and Verifier to two Discord rooms. It provides agent identities, shared room context, addressing, human permission requests, and the support-to-engineering handoffs. The actual run includes Concierge handing work to Builder, Builder requesting independent verification, and the verified result returning to support.

ProofDesk's Python service separately enforces case transitions, candidate/evidence binding, retry limits, and review requirements. The CLI can run alone for testing; Switch is central to the demonstrated collaborative workflow rather than the local verification algorithm.

## What makes it useful

- Reviews use the exact committed candidate, not an agent's unsupported completion claim.
- Verification runs against a fresh Git snapshot using checks maintained outside the candidate tree.
- Changing a candidate or rerunning verification invalidates previous approval and drafts.
- The dashboard and portable report make the original report, patch, checks, and decision inspectable.
- The live case resumed its saved candidate after a local Switch server interruption.

## Technology

Switch Console 0.40.1, switch-core 0.31.0, Codex, Discord, Python 3.11, Git, native HTML/CSS/JavaScript, and a standard-library Python HTTP server. The observed local Switch setup used native Windows and PostgreSQL 17. The ProofDesk application has no third-party Python runtime dependencies.

## Validation

The completed live case is PD-41b429bc34c2. Its candidate is c10966e1b9bb3d58f644c6762eff89887ea144e3. Saved evidence confirms CLOSED, 11/11 independent passing checks, one candidate attempt, one human approval, and a response with sent=false.

The implementation also passed 26 automated tests and browser QA at 390, 768, and 1440 pixels. Browser tests use disposable fixtures and are distinguished from the genuine Discord/Switch run.

## Challenges and learning

The build exposed a mismatch between local provider detection and the managed agent controller. A managed-machine template resolved creation. We also handled Windows Git ownership differences, command approval prompts, and a local server interruption. The case state and candidate revision allowed the workflow to resume without replacing the case or silently changing its patch.

The lesson was to treat agent messages as coordination and executed evidence as the source of results. Human command permissions and acceptance of the final patch are distinct decisions.

## Limitations

This is a bounded prototype for the documented order-total acceptance policy and synthetic reports. It is not a general bug-fixing service. The live run required human permission handling and recovery, so it does not establish unattended operation or measured time savings. Local reviewer identity and evidence hashes are not a security boundary against unrestricted same-account agents. Candidate execution is not a hostile-code sandbox. Merge, deployment, and customer messaging remain manual.

## AI assistance disclosure

Codex assisted with implementation and documentation. The demonstrated workflow also used three Codex-powered agents coordinated through Switch. The synthetic input, prepared fixture rehearsal, automated tests, and genuine live candidate run are distinguished in the repository and demo.

## Links

- Repository configured as this checkout's origin: https://github.com/RNKbansal23/Switch-workflow
- README: https://github.com/RNKbansal23/Switch-workflow/blob/main/README.md — use the repository's actual default branch if different.
- Demo video: add your actual uploaded recording link. No video URL has been supplied or verified in this session.
- Hosted application: no public application URL has been established. The dashboard runs locally; do not submit its private loopback/token URL as a hosted demo.

Verify the latest source and documentation are pushed and accessible before entering repository links. Copy real participant/team information from your registration. Enter optional award evidence only if you actually have it.

## Submission handling

The user should complete the actual form, confirm eligibility/terms personally, enter real repository/video links, and click Submit themselves. Official rules prohibit automated registration/submission while allowing AI-assisted development: https://www.wemakedevs.org/hackathons/switch/rules.
