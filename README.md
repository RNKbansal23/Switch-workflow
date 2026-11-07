# ProofDesk

Customer bug report → reproduced failure → candidate patch → independent checks → human review → reply draft.

Built for the Flip the Switch hackathon's Business Workflow track. The local case engine and operator dashboard are implemented. A genuine Discord/Switch/Codex run completed on November 7: a synthetic report produced an agent-written candidate, 11/11 independent passing checks, one human approval, an unsent reply draft, and a CLOSED local case. See the [live-run record](docs/LIVE-RUN.md) and [actual candidate diff](evidence/live-run/candidate.patch).

## Open the workspace

```powershell
python -m workflow.web
```

Open the complete private URL printed in the terminal. The responsive dashboard reads actual case records, refreshes as agents work, shows committed patches and check evidence, and records operator review before drafting and closing a case. It starts with the cases in your local store; it does not invent activity. There are no third-party runtime dependencies or dashboard API keys.

On Windows you can also run `.\start-proofdesk.cmd`; it locates the installed Python without changing PowerShell's execution policy.

```powershell
python -m scripts.doctor
python -m scripts.live
```

The doctor reports local prerequisites without reading credentials. The live preparation command creates a fresh baseline-only repository and a concrete request to paste into your configured Switch room. Agents must generate the patch themselves. Follow [live connection setup](docs/LIVE-SETUP.md) and the [workspace guide](docs/WORKSPACE.md).

```powershell
python -m unittest discover -s tests -v
python -m scripts.demo
```

Requires Python 3.11+ and Git. The demo executes **labelled prepared fixtures**, rejects an incomplete patch, verifies the corrected commit, and stops before human approval. It is not a live agent recording. State stays in the ignored `.proofdesk/` directory.

| Build document | Purpose |
| --- | --- |
| [Operator workspace](docs/WORKSPACE.md) | Dashboard, review, export, and local access |
| [Live setup](docs/LIVE-SETUP.md) | Free-provider options and required connections |
| [Finish plan](FINISH-PLAN.md) | Ordered integration and submission checklist |
| [Video script](docs/VIDEO-SCRIPT.md) | Recording setup, exact narration, screens, and commands |
| [Implementation plan](WORKFLOW-PLAN.md) | Milestones, current status, remaining work |
| [Detailed workflow](docs/WORKFLOW-SPEC.md) | States, evidence, handoffs, recovery, limits |
| [Demo runbook](docs/demo.md) | Local rehearsal and genuine live-run steps |
| [Setup and environment](docs/setup.md) | Prerequisites and live setup gaps |
| [Validation record](docs/VALIDATION.md) | Executed checks and what remains unverified |
| [Rules checklist](docs/COMPLIANCE.md) | Requirement-to-evidence mapping |
| [Switch template](switch/proofdesk.template.yaml) | Three agents and two linked private rooms; server validation pending |

The CLI binds verification and human review to exact Git revisions, rejects stale approvals, limits repair attempts, and retains hashed evidence. A separate human review command records a local operator decision; it does not authenticate human identity against unrestricted agents sharing the same OS account. Candidate snapshots are not a hostile-code sandbox. No production deployment or customer messaging occurs.

## Hackathon research

Researched on **November 4, 2026**. Start with the [overview](hackathon/01-overview/README.md), then follow [how to proceed](hackathon/04-how-to-proceed/README.md).

Proposed build: [ProofDesk workflow implementation plan](WORKFLOW-PLAN.md), from customer bug report to independently verified fix and human-reviewed response.

These are original research notes with official source links. Published requirements, practical suggestions, and unresolved details are identified separately. This folder does not represent a registered or submitted entry.

| Guide | Contents |
| --- | --- |
| [Overview](hackathon/01-overview/README.md) | What Switch is and what the event involves |
| [Rules](hackathon/02-rules/README.md) | Eligibility, identity, ownership, prizes, conduct |
| [Tracks and judging](hackathon/03-tracks-and-judging/README.md) | Tracks, awards, judging, conflicting announcements |
| [How to proceed](hackathon/04-how-to-proceed/README.md) | Practical four-day build plan |
| [Setup](hackathon/05-setup/README.md) | Windows installation, providers, server, first agent |
| [Rooms and workflows](hackathon/06-rooms-and-workflows/README.md) | Instructions, context, roles, templates, commands |
| [Messaging integrations](hackathon/07-messaging-integrations/README.md) | Mattermost, Discord, Slack, Teams, Telegram |
| [Architecture and custom agents](hackathon/08-architecture-and-custom-agents/README.md) | Message flow, protocol, registration, events |
| [Deployment and administration](hackathon/09-deployment-and-administration/README.md) | Hosting choices, managed agents, resource access |
| [Core contributions](hackathon/10-core-contributions/README.md) | Assignment rules, development setup, PR process |
| [Ideas and examples](hackathon/11-ideas-and-examples/README.md) | Official scenarios and suggested small projects |
| [Submission](hackathon/12-submission/README.md) | Deliverables, demo outline, README contents |
| [Troubleshooting](hackathon/13-troubleshooting/README.md) | Common failures and diagnostic order |
| [Sources and open questions](hackathon/14-sources-and-open-questions/README.md) | Navigation coverage, source directory, access limits |

The public [schedule](https://www.wemakedevs.org/hackathons/switch/schedule) gives the submission cutoff as **November 7, 2026, 11:59 PM IST**. Read the [official rules](https://www.wemakedevs.org/hackathons/switch/rules) before entering.
