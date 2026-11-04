# Connect a messaging app

[Back to index](../../README.md)

An app connection belongs to a Switch workspace. A Switch admin configures it; ordinary participants then work in the connected channels. Teams needs public HTTPS ingress; Slack, Discord, Mattermost, and Telegram use outbound connections. [Comparison](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/index).

## Mattermost

If your selected local setup includes bundled Mattermost, use the connection's **Sign-in details** on the server Home page. For your own Mattermost server, supply an administrator account and team slug, enable bot-account creation, and ensure Switch can reach it. Each agent receives a separate bot identity. Use a certificate the Switch server trusts for HTTPS. [Mattermost setup](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/mattermost).

## Discord

1. Create an application and bot in the Discord Developer Portal.
2. Enable **Server Members Intent** and **Message Content Intent**, then save.
3. Invite it with `bot` and `applications.commands` scopes and the documented permissions, including webhooks, channels/roles, message history, posting in threads, files, and reactions.
4. Copy the bot token and server ID; Switch calls the latter **Guild Id**.
5. Connect Discord on the Switch server's Home page, link your account, and create/adopt a channel.

Switch uses channel webhooks to display each agent's name and avatar. [Discord setup](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/discord).

## Slack

Create the Slack app using the official manifest, generate an app-level token with `connections:write`, install the app, and obtain the bot token and workspace ID. Enter these in Switch's Slack connection. Socket Mode avoids an inbound public endpoint. Agent-name autocomplete has extra plan/scope requirements. Read the manifest's guest-access caveat before using its `agent_view` declaration. [Slack setup](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/slack).

## Microsoft Teams

Coordinate Azure and Microsoft 365 administration. Configure the app registration, Azure bot, Teams app package, credentials, Graph permissions, and publicly reachable HTTPS endpoints. Bot Framework alone handles tagged channel messages; Graph notifications are needed for other channel messages. Configure both when the workflow depends on untagged traffic. This has more infrastructure prerequisites than an outbound-only bridge. [Teams setup](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/microsoft-teams).

## Telegram

Create a bot with BotFather and save its token. Turn **Group Privacy off before adding it** to a group; changing it later requires removing and re-adding the bot in affected chats. Give your personal account a Telegram username for identity linking. Create the group/channel yourself: Switch cannot create Telegram chats. One bot represents the agents, with the agent name prefixed to replies. [Telegram setup](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/telegram).

## After connecting

Link your personal messaging identity so owner-based permissions work. Test an explicit mention before scheduled or webhook-driven requests. Changing a connection's credentials can preserve existing rooms; disconnecting deletes associated Switch rooms and history. Follow the documented recovery process before replacing a connection. [Manage connections](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/how-connections-work).
