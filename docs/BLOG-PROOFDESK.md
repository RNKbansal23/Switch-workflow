# 11 Green Checks. One Human Decision. Building ProofDesk with Switch.

*By Rajat Bansal · ClulessNerds · Flip the Switch hackathon*

The bug was small enough to explain in one line:

```python
order_total('10.05', 1, '10')
# Expected: '9.05'
# Actual:   '10.05'
```

An order calculation was ignoring the discount.

The interesting part came after an AI agent fixed it. Another agent needed to check the exact patch. A person needed to accept it. The response needed to say what had actually happened, including the fact that nothing had been deployed.

I built **ProofDesk** to connect those steps through Switch and Discord.

Our completed live run produced one candidate, passed all eleven independent acceptance checks, received one human approval, and closed with an unsent customer reply draft. Along the way, I encountered provider detection problems, permission prompts, Windows Git ownership checks, and a local server interruption.

That messy middle taught me as much as the green checks.

## Start with a support problem people can follow

A support teammate reports a bug. Engineering investigates. Someone proposes a fix. Someone else reviews it. Support eventually explains the outcome.

Each handoff needs enough context to answer a few concrete questions:

- What input caused the failure?
- Which code revision reproduced it?
- What changed?
- Who checked the candidate, and what did they execute?
- Has a person accepted it?
- Is the fix available to the customer yet?

For this prototype, I chose a synthetic order-discount report and a deliberately broken baseline repository. The narrow scope made the result understandable and testable. This version supports the documented order-total policy; it does not diagnose arbitrary customer bugs.

## Three agents, two rooms, one case

Switch connected three Codex-powered agents to our Discord server:

| Agent | Responsibility | Where it worked |
| --- | --- | --- |
| Concierge | Clarify the report, create the case, return the result | Support |
| Builder | Reproduce the failure, write the patch and regression tests | Support and engineering |
| Verifier | Execute independent checks on the exact candidate revision | Engineering |

The rooms were `clulessnerds-support` and `clulessnerds-engineering`.

The workflow looked like this:

```text
Discord report
  → Concierge creates the case
  → Builder reproduces and commits a candidate
  → Verifier checks that revision
  → Human reviews the evidence
  → Concierge saves a reply draft and closes the local case
```

Switch supplied the identities, addressing, shared room context, and message handoffs. ProofDesk's Python service supplied the case state, evidence records, retry budget, and review conditions. The CLI also runs independently for local testing.

Keeping those responsibilities clear made the demonstration easier to explain: the agents coordinate through Switch, and executable checks determine whether the case can advance.

## Give the agents contracts they can actually follow

Each role has its own instruction file in the repository. Concierge collects required facts before starting engineering. Builder must reproduce the reported failure and propose a committed candidate. Verifier must report executed checks rather than repeat Builder's confidence.

Handoffs include the case ID, repository, full commit, evidence references, and next actor. Actual room/thread references are recorded when available; the local application labels them as supplied references rather than pretending to authenticate Discord independently.

A case moves through states such as:

```text
NEW → REPRODUCED → PATCH_READY → VERIFIED → APPROVED → CLOSED
```

Missing details lead to clarification. Failed checks prevent verification. A changed candidate invalidates earlier verification, approval, and drafts. The repair budget limits automated candidate attempts before human help is needed.

These rules make an agent's next step more concrete than a broad instruction to “handle the ticket.”

## The patch was short. Its evidence mattered.

The baseline multiplied price by quantity and rounded the result. It never applied the supplied discount.

Builder changed the calculation to:

```python
total = price * quantity * (Decimal('100') - discount) / Decimal('100')
return str(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
```

Builder also added regression tests. One useful example was:

```python
order_total('0.05', 3, '10') == '0.14'
```

That example helps catch rounding each discounted item before calculating the full order. The documented contract requires one final rounding step.

The candidate was committed as:

```text
c10966e1b9bb3d58f644c6762eff89887ea144e3
```

Verifier checked a fresh Git export of that revision using the acceptance runner maintained outside the candidate tree. Uncommitted working-copy changes could not silently become the code under review.

The eleven acceptance examples covered the reported result, ordinary and boundary discounts, rounding, empty orders, and several invalid inputs. All eleven passed. That establishes the documented examples; it does not prove correctness for every numeric input or production financial use.

## Getting the first handoff working took real debugging

I used Switch Console **0.40.1**, switch-core **0.31.0**, a native Windows server setup, and PostgreSQL 17. Codex was already signed in. The dashboard itself required no AI API key; agent usage remained governed by the provider account.

Connecting Discord involved creating a bot application, enabling the documented member and message-content intents, inviting the bot with the required permissions, and entering its token and server ID in Switch. Linking my Discord identity let the agents recognize their owner.

My first template attempt exposed a confusing mismatch: Settings showed Codex signed in, while the template form reported that no provider was ready. A managed-machine template with an explicit Codex provider let us create the agents and rooms.

Another easy-to-miss detail: our Discord server was named **IDLE NO MORE**, but the Switch connection was named **myDiscord**. The template needed the connection label.

Permission handling also needed attention. Short command requests could be approved in Discord. One oversized request directed me to Console, but the room view opened Discord again. Enabling Auto mode for Concierge changed its runtime definition; the blocked session needed to end before restarting under the new settings. Builder and Verifier still requested relevant command approvals. I kept the recommended bypass setting off.

Windows Git ownership checks supplied the next obstacle. The baseline had been created under a sandbox account, while the live workflow ran under my Windows account. Git refused the repository until I approved trusting that exact demo path. We did not disable ownership checks globally or trust every repository.

For a first-time user, my advice is to prove one mention, one file read, and one handoff before attempting the complete workflow. Confirm the actual provider, machine, working directory, and chat connection separately.

## Then the server became unreachable

Builder had already saved its candidate when the local server stopped responding. The controller logs showed repeated reconnect attempts, and the health endpoint refused connections.

The case still existed. So did the candidate revision.

After restoring the server, we resumed the existing case and sent the saved candidate to Verifier. There was no need to create replacement work or ask Builder to invent another fix.

This is why I wanted persistent case state alongside the conversation. A status message can become stale during an outage; a recorded revision and its evidence give the next participant something concrete to resume.

This run needed human intervention. I have not measured an unattended success rate or a time-savings percentage.

## Eleven passing checks still left a human decision

The local dashboard brings together the original report, actual Git diff, acceptance results, timeline, review controls, and reply draft.

Once the case reached VERIFIED, I entered my approval through that dashboard. The decision was tied to the candidate and its verification evidence. My recorded reason was simply `for test`, appropriate to this synthetic demonstration; it should not be mistaken for a production release review.

Concierge then saved the reply draft and closed the case. The response explicitly said the patch had not been confirmed merged or deployed. Its saved record contained:

```json
{"sent": false}
```

The final case, **PD-41b429bc34c2**, recorded:

- **CLOSED**
- **11/11 independent acceptance checks passed**
- **1 candidate attempt**
- **1 human approval**
- **An unsent reply draft**

The separate local implementation also passed 26 automated tests, plus browser checks at mobile, tablet, and desktop widths. Those browser tests use disposable prepared fixtures; they are distinct from the genuine Discord/Switch run described here.

## Try the local workspace

The repository includes the role contracts, acceptance policy, setup notes, candidate diff, and live-run record:

[ProofDesk repository](https://github.com/RNKbansal23/Switch-workflow)

With Python 3.11+ and Git installed, run these commands from the repository root:

```powershell
python -m unittest discover -s tests -q
python -m workflow.web
```

Open the private URL printed by the workspace server. The dashboard reads your actual local cases and starts empty when none exist.

To prepare a new baseline-only task for live agents, use a second terminal:

```powershell
python -m scripts.live --prefix clulessnerds
```

That command creates the broken baseline and a request file containing its actual repository path and commit. It does not generate the candidate or simulate agent messages. Follow the live setup guide to configure Switch, your signed-in provider, and a messaging connection. The portable managed-machine template is in `switch/clulessnerds.managed.template.yaml`; select your own machine, project directory, and connection.

Keep the local Switch server and dashboard processes running. If an interruption occurs, inspect the saved case before creating another one.

## What I would improve next

For Switch, I would value a central approval inbox, consistent provider detection across Settings and Templates, and a clearer distinction between queued, permission-blocked, disconnected, and actively working agents.

For ProofDesk, the next engineering steps would be stronger reviewer identity separation, safer candidate execution, and a deliberate mechanism for adding acceptance policies beyond this sample application.

The current hashes detect ordinary evidence changes through the intended workflow. They are not tamper-proof against an unrestricted account owner. Separate role instructions do not isolate agents sharing an operating-system account, and a fresh source snapshot is not a hostile-code sandbox.

Those boundaries matter because someone reading the final reply should know exactly what has been established.

The moment I would highlight from this build is the handoff after verification: a specific patch, eleven executed checks, and a decision waiting for the person responsible.

That is the workflow I wanted ProofDesk to make visible.

---

Built by **ClulessNerds** for the **Flip the Switch hackathon**, Business Workflow track. Codex assisted with implementation and documentation and powered the three agents in the live workflow.

Project: https://github.com/RNKbansal23/Switch-workflow

Switch setup reference: https://docs.switchagents.ai/switch-rooms/getting-started

Hackathon: https://www.wemakedevs.org/hackathons/switch

#HowISwitch #BuildInPublic #AI #OpenSource
