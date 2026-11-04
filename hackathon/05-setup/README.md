# Install and get your first agent answering

[Back to index](../../README.md)

## Version note

During research, GitHub's latest stable release resolved to **Switch Console 0.40.1**, bundling **switch-core 0.31.0**. Record your actual installed versions, because Console and server releases differ. [Release](https://github.com/sandbox-quantum/switch/releases/tag/switch-console-v0.40.1).

The quickstart describes a Docker-based local stack and an older two-address server connection. Newer documentation describes one server address; the 0.40.0 changelog also announces a local option without Docker. Follow the UI available in your release, and retain Docker for the bundled Mattermost/development path when required. [Quickstart](https://docs.switchagents.ai/switch-rooms/getting-started), [add a server](https://docs.switchagents.ai/switch-rooms/getting-started/add-a-server), [changelog](https://docs.switchagents.ai/switch-rooms/resources/changelog).

## Windows starting point

1. Download the Windows x64 `.exe` or `.msi` from the [official installation page](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console). Windows and Linux builds are marked early access.
2. Run the installer and open Switch Console.
3. Install and sign in to an agent provider on the computer where the agent will run. In Console, check **Settings → Agent providers**. Recheck after signing in; fully restart Console if a newly installed CLI remains undetected. [Provider setup](https://docs.switchagents.ai/switch-rooms/getting-started/set-up-agent-providers).
4. Add a local server, onboard a remote host, or connect to an existing server. For a Docker-backed local setup, start Docker first. Existing-server access needs the correct server address and account. Link your messaging account so Switch recognizes you. [Server setup](https://docs.switchagents.ai/switch-rooms/getting-started/add-a-server).

## First room smoke check

In the documented quickstart, choose **Templates → Switch expert → Use**, enable **Start it in a room**, and create the agent and room. Open the resulting chat and address the agent by its exact name. If its repository download awaits approval, inspect the thread and respond there. A successful reply proves your first room exchange works. [Quickstart](https://docs.switchagents.ai/switch-rooms/getting-started).

Newer first-run UI may guide you through **switch-buddy** instead. This is a documented change in the [0.40.0 changelog](https://docs.switchagents.ai/switch-rooms/resources/changelog).

## Your project agent

Under **Your Agents**, add an agent with a descriptive name, provider, run location, and working directory. Registration is once per server, not once per room. Names use lowercase letters, digits, periods, underscores, and hyphens; start with a letter or digit. Check the directory on the selected machine. Name and run location are fixed after creation; directory mutability differs for managed agents. [Onboarding](https://docs.switchagents.ai/switch-rooms/getting-started/onboard-your-agents).

Then create a project room, add the agent, and test a small request against a sample file. See [rooms](../06-rooms-and-workflows/README.md).
