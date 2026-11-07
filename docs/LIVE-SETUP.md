# Connect ProofDesk live

The local workspace needs Python, Git, and no AI API key. Switch and an agent provider are separate prerequisites. No paid provider or billing configuration is added by this project.

## Current observed state

November 7 checks found Python 3.11.9, Git 2.51.0.windows.1, and a Codex executable. Docker's executable is installed but its engine was unavailable. No running Switch process or Console installation in the checked standard application locations was found. Provider sign-in and free usage allowances were not established. Run `python -m scripts.doctor` to repeat executable/engine checks; it does not read secrets or validate sign-in.

The official Windows installer was subsequently downloaded to `.proofdesk/tools/switch-console-x64.exe` and opened for user-operated installation. Its product version is **0.40.1**; Windows verified its **SandboxAQ** Authenticode signature. SHA-256: `575262E7971CF2046CE04F968E33D6CD6C3FF795D695061C5A1443B6E79A2332`. Installation completion and server startup are still unverified.

Follow-up November 7: installation completed and Switch Console **0.40.1** is running. Its log records **switch-core 0.31.0** starting with the **native** runtime and installed PostgreSQL 17. The runtime file confirms `native`, and `http://127.0.0.1:65081/health` returned **HTTP 200**. Docker is not needed for this observed native setup. Provider sign-in, template import, and real agent exchanges are still unverified. Desktop capture was obscured by the terminal, so this confirmation comes from processes, runtime files, logs, and HTTP health rather than visual inspection of Console's current screen.

## Connection sequence

1. Install/open [Switch Console](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console).
2. Start a local server or join an existing one. Follow the installed release's actual choices. The official quickstart and the server guide currently describe different local setup details; do not assume Docker is optional or required for every release. If the chosen path needs Docker, start Docker Desktop and confirm its engine responds.
3. Open Settings → Agent providers. Set up a supported provider and confirm its status reads Signed in. Executable availability alone is insufficient.
4. Use built-in Switch rooms if your installed release supports them, a messaging connection supplied by the server, or one external chat app. For bridged rooms, link your personal identity. Discord needs a server you manage plus a bot token/Guild ID entered in Switch; Mattermost may be supplied by the selected local stack. Do not paste tokens into case reports or commit them.
5. Import `switch/proofdesk.template.yaml`. Supply the existing project directory, an explicitly selected provider, local location, and unique prefix. The bridge is optional: the current template language permits the server's default messaging app or Switch-only rooms when none is configured. Validate this draft against the installed server before relying on it.
6. Confirm support membership: human, Concierge, Builder. Confirm engineering membership: human, Builder, Verifier. Test each exact mention and each role-to-role handoff.
7. Start `python -m workflow.web` from this project and open the printed URL.
8. Run `python -m scripts.live --prefix proofdesk`. Open its `prompt_file` and paste the request into support. For another prefix, use the same value you configured in the template.
9. Let the live agents reproduce, edit, commit, verify and return evidence. Review the exact candidate in the dashboard and record your own decision.
10. Preserve the actual chat transcript and template version in addition to the exported local report.

Official references: [quickstart](https://docs.switchagents.ai/switch-rooms/getting-started), [server choices](https://docs.switchagents.ai/switch-rooms/getting-started/add-a-server), [provider setup](https://docs.switchagents.ai/switch-rooms/getting-started/set-up-agent-providers).

The template was checked against the current [official template language](https://github.com/sandbox-quantum/switch/blob/main/docs/TEMPLATES.md). That documentation check does not replace an import/run against the actual installed release.

## Free-only provider choice

Use a supported provider only after confirming the selected account/model is available without new payment. Existing paid subscriptions are not inherently free, even if they avoid a separate API key. This repository neither checks nor changes billing.

OpenCode is a Switch-supported provider. Its [official model documentation](https://opencode.ai/docs/console/models/) currently lists limited-time free models, including GLM-5.3-Flash Free and DeepSeek V4.1 Flash Free. Availability and limits can change. Select a model explicitly labelled free in the installed provider and confirm it works with Switch's tool/runtime integration. Free-tier chat models are documented as requiring OpenCode; do not substitute a generic HTTP API call and assume the same entitlement. Do not add credits, billing details, or auto-recharge to make a failed free setup work.

If you choose another provider, use its own current free allowance and sign-in flow. Model quality and successful tool handoffs must be measured during the live run; a free label alone does not establish reliability.

## If a handoff fails

Identify which boundary failed: server, provider launch/sign-in, chat bridge, human account link, room membership, agent addressing, working directory, or workflow command. Save the exact error without secrets. Fix that boundary and repeat the smallest failed exchange before running another case. Never replace an unavailable live result with a prepared fixture result.

The dashboard's Copy Switch handoff action prepares text for a person to paste; it does not itself send a message. All communication claims must be backed by the actual connected-room transcript.
