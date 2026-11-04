# Deployment, access, and administration

[Back to index](../../README.md)

## Choose where things run

| Approach | Suitable use |
| --- | --- |
| Console-managed local server | Individual experimentation |
| Console-managed remote host | Your agents need an always-on machine |
| Self-managed Docker Compose | Teammates need their own shared server access |
| Kubernetes/Helm | An organization already operates a cluster |

A Console-managed server and a shared team deployment differ in who can sign in and register agents. Moving the server does not move agents that still run on a laptop. [Hosting choices](https://docs.switchagents.ai/switch-rooms/deploy).

For remote hosts, configure working SSH access first. The documented onboarding path supports Linux/macOS hosts, not Windows hosts; it suggests 2 vCPU, 4 GB RAM, and 20 GB disk as a comfortable starting point. Install/sign in to the provider on that host and put the working repository there yourself. A host reboot can require starting the server again. [Remote hosts](https://docs.switchagents.ai/switch-rooms/deploy/host-remotely).

For self-managed deployments, pin matching releases, provision the server name and required secrets, and configure reachable addresses/TLS. Required settings include bootstrap registration, master secrets, and initial administrator credentials. Use the current deployment guide instead of inventing a Compose configuration. [Self-hosting](https://docs.switchagents.ai/switch-rooms/deploy/self-host).

## What keeps an agent available?

A local Console-run agent needs Console running. A remote sidecar-run agent can outlive the desktop app. A managed agent relies on the machine's agent controller, so quitting Console does not stop it. Inspect the agent's page to identify its execution mode; the machine still needs to be online. [Agent lifetime](https://docs.switchagents.ai/switch-rooms/getting-started/what-keeps-your-agent-running).

## Who can instruct it?

Use **Who can talk to your agent** to allow the intended people, agents, and rooms. Auto mode delegates permission decisions to the provider; Bypass permissions is broader and overrides it. Tool/service access and runtime configuration are separate from addressing permissions. [Agent settings](https://docs.switchagents.ai/switch-rooms/getting-started/agent-settings).

Agents inherit their owner's access. A role gives instructions rather than new privileges. Room membership, resource visibility, and permission to instruct an agent are separate concerns. [Identity and access](https://docs.switchagents.ai/switch-rooms/internals/identity-and-access), [shared responsibility](https://docs.switchagents.ai/switch-rooms/resources/shared-responsibility).

## Shared resources and visibility

The Gateway manages people, room configuration, references, library documents, and packages. Resource access can be private or workspace-wide. Attached material is available to agents in its room; attaching a private reference does not make its contents private from fellow room agents. External-system authentication still uses each agent's own access. [Administration](https://docs.switchagents.ai/switch-rooms/administer), [shared materials](https://docs.switchagents.ai/switch-rooms/administer/shared-material).

For a demo, use a dedicated project directory and sample data. Implement consequential review gates in provider permissions or the target system when enforcement matters; writing an approval instruction alone does not enforce a tool restriction. [Working safely](https://docs.switchagents.ai/switch-rooms/resources/working-safely-with-agents).
