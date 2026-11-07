# ProofDesk publishing pack

These are drafts for the user to publish. No post has been sent. The full article is in `docs/BLOG-PROOFDESK.md`. Publish it as a LinkedIn Article, then use the promotion post below. On X, publish the short post or the thread and attach actual project screenshots. Add your real article/video links only after they exist.

## LinkedIn article title

11 Green Checks. One Human Decision. Building ProofDesk with Switch.

## LinkedIn promotion post

My AI agent fixed the bug. The workflow still needed my decision.

I built ProofDesk with ClulessNerds for the Flip the Switch hackathon: a support-to-engineering workflow running through Switch and Discord.

The input was tiny: an order worth 10.05 with a 10% discount returned 10.05. It should have returned 9.05.

Three Codex-powered agents took it through the process:

→ Concierge collected the report and created a case.
→ Builder reproduced the failure, committed a fix, and added regression tests.
→ Verifier independently checked that exact revision.
→ I recorded approval in the dashboard.
→ Concierge saved an unsent reply draft and closed the case.

The completed live run: 11/11 acceptance checks passed. One candidate. One human approval. Nothing automatically merged, deployed, or sent to a customer.

Getting there also meant debugging conflicting provider status, permission prompts, Git ownership, and a server interruption. After recovery, we resumed the saved case and candidate.

I wrote up the architecture, setup, failures, and limits in the article attached to this post. It includes the steps to try the local workspace yourself.

Source: https://github.com/RNKbansal23/Switch-workflow

Where would you put the human checkpoint in an agent workflow: before the patch, after verification, or both?

#HowISwitch #BuildInPublic #AI #OpenSource

## X standalone post

3 AI agents. 2 Discord rooms. 1 human decision.

I built ProofDesk with Switch + Codex:
bug report → patch → 11/11 independent checks → my approval → unsent reply draft.

Real run. No auto-deploy.

https://github.com/RNKbansal23/Switch-workflow
#HowISwitch

## X thread

### Post 1

My AI agent fixed the bug. The workflow still needed my decision.

I built ProofDesk with Switch + Codex: 3 agents, 2 Discord rooms, and an actual support-to-review workflow.

11/11 independent checks passed. Here's how it worked. 🧵
#HowISwitch

### Post 2

The report was simple:

order_total('10.05', 1, '10')
Expected: 9.05
Actual: 10.05

The baseline ignored the discount. This was a synthetic report on a deliberately broken baseline; the agents had to generate the candidate live.

### Post 3

Concierge opened the case in support.
Builder reproduced the failure and committed a patch + regression tests.
Verifier checked that exact commit in engineering.

Switch carried the handoffs and context. Python enforced the case transitions and review requirements.

### Post 4

Verifier tested a fresh export of the candidate commit with checks maintained outside the candidate tree.

11/11 passed: the reported issue, discount boundaries, rounding examples and invalid inputs.

Then the workflow waited for my approval.

### Post 5

The build had plenty of friction: conflicting provider status, permission prompts, Windows Git ownership, and a local server interruption.

After restoring the server, we resumed the saved case and candidate. We didn't create replacement work.

### Post 6

I approved the exact candidate in the dashboard.

Concierge saved the reply draft and closed the case. The draft stayed unsent and said deployment was unconfirmed.

This run needed human help. I haven't measured unattended success or time savings.

### Post 7

What I'd improve in Switch:
• One approval inbox with complete commands
• Consistent provider detection
• Clear queued / blocked / disconnected states

The full build story covers the architecture, setup, recovery and limits.

### Post 8

ProofDesk by ClulessNerds.

The finished run: one candidate, 11/11 independent checks, one human approval, an unsent draft, and a CLOSED case.

Code: https://github.com/RNKbansal23/Switch-workflow

Where would you put the human checkpoint?
#HowISwitch

## Screenshots to attach

1. A dashboard case view showing CLOSED and the actual check results. Use a fresh capture of the completed case rather than a browser-QA fixture screenshot.
2. Switch's three running ClulessNerds agents (your Screenshot_3 is suitable after checking its crop).
3. The original report and Builder/Verifier handoff in Discord (crop to the relevant conversation).
4. The final VERIFIED result and unsent reply draft; keep full private paths or unrelated members out of the crop where practical.

For the article, insert three or four images near the relevant passages and add factual captions such as: “Verifier reported eleven passing acceptance checks for the pinned candidate.” The prose is publishable without images, but actual screenshots make the steps much easier to follow.

## Publishing order

1. Review the article's first-person statements and technical explanation.
2. Ensure the article, portable template, and other referenced files are pushed to the repository before sharing their links. A local file is not yet a published blog URL.
3. Publish the long article through LinkedIn's article editor. Retain the real article URL.
4. Share it using the LinkedIn promotion copy, attaching the article.
5. Publish the X standalone post or thread with project screenshots. Reply with the real article link if promoting the long article there.
6. Put the public article URL in the hackathon's Blog post field and the actual social post URL in its #HowISwitch field. If the form specifies a platform or other requirement, follow that instruction.

Do not tag an assumed @Switch account. Select the real organizer accounts through each platform's own search if you want to tag them. Do not claim prize eligibility or publication until the relevant links and form requirements are checked.
