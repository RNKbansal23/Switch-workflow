# Troubleshooting

[Back to index](../../README.md)

## An agent does not answer

| Symptom | First check |
| --- | --- |
| Nothing visible | Open the thread; check the exact `@name`; run `!agents-status` |
| Waiting for input | Find and answer the pending request |
| Agent refuses you | Link your messaging identity and check addressing policy |
| Managed machine offline | Check that machine and its agent controller |
| Local Console-run agent offline | Start Console on the owning computer |
| Agent works in another room | Check its active session/role and room membership |
| Approval has no effect | Confirm the approver may instruct this agent |

Follow [When an agent doesn't answer](https://docs.switchagents.ai/switch-rooms/using/agent-not-answering) for the specific status text. Membership does not prove the runtime is online.

## Setup or provider problems

- **CLI installed but undetected:** recheck provider status, then quit/reopen Console so it reloads PATH.
- **Provider unsigned-in:** sign in on the machine that actually runs the agent.
- **Tool works in a terminal but fails in Switch:** check the runtime's environment; Switch does not pass through every shell variable.
- **Bridge not running:** check the connection/server first. Re-linking your personal identity cannot repair a stopped bridge.
- **Schema or field error after updating Console:** compare the server version with Console's requirements; Console 0.40 needs server 0.31.0 for the documented functionality.
- **Wrong server address:** an older Gateway page URL may differ from the agent-facing server address.

Sources: [Troubleshooting](https://docs.switchagents.ai/switch-rooms/resources/troubleshooting), [agent onboarding](https://docs.switchagents.ai/switch-rooms/getting-started/onboard-your-agents).

## Platform-specific checks

| App | Common setup issue |
| --- | --- |
| Discord | Message Content Intent missing or permissions not saved |
| Telegram | Group Privacy changed after the bot already joined |
| Teams | Bot not mentioned, or Graph channel notifications missing |
| Slack | App credentials/scopes or channel installation incomplete |
| Mattermost | Wrong account/team details or bot creation disabled |

Use the linked official setup in [messaging integrations](../07-messaging-integrations/README.md) for repairs.

Do not delete a server or disconnect a chat connection as a first diagnostic step: the documented actions can remove stored rooms/history. Inspect status and repair credentials first. [Troubleshooting](https://docs.switchagents.ai/switch-rooms/resources/troubleshooting).
