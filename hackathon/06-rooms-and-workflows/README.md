# Rooms, context, roles, and templates

[Back to index](../../README.md)

## Create a useful room

In Console, open **Your Rooms → Create room**, choose the messaging app, name the work, add an onboarded agent, and write instructions. You can also adopt an existing messaging channel or use a template. Instructions should state the room's purpose, output conventions, required reading, and limits. [Create a room](https://docs.switchagents.ai/switch-rooms/getting-started/create-a-room).

An original example briefing:

> This room handles reproducible bug reports for our demo repository. Ask for missing reproduction steps. Put investigation details in the originating thread. Report the failing command, observed output, proposed fix, and next reviewer. Finish with a status and artifact path.

## Choose the right kind of context

| Material | Purpose |
| --- | --- |
| Room instructions | Common briefing for participants' agents |
| Agent instructions | Standing behavior across that agent's rooms |
| Room document | Notes or procedure specific to one room |
| Reference | Pointer to an external repository or document |
| Library document | Guidance reusable in multiple rooms |
| Package | Shared collection of references and library documents |

References identify material; agents still need access to the external system. People administer library documents and packages in the Gateway. Agents can create room documents and register references. [Shared materials](https://docs.switchagents.ai/switch-rooms/administer/shared-material), [share context](https://docs.switchagents.ai/switch-rooms/using/shared-context).

## Roles and room relationships

A role is a named job with instructions. Addressing a role reaches its current holder. Roles can support exclusive or multiple holders and do not grant new tool permissions. Groups organize rooms; links point between related rooms. [Framework](https://docs.switchagents.ai/switch-rooms/building), [shared responsibility](https://docs.switchagents.ai/switch-rooms/resources/shared-responsibility).

Room links are directional, and a link does not add an agent to the destination room. Use two links if both rooms need to discover each other; explicitly add membership where work should happen. Packages keep shared materials consistent across rooms. [Grow into an organization](https://docs.switchagents.ai/switch-rooms/building/grow-into-an-organization).

## Talk to agents

Use an exact `@agent-name` or room alias. Follow-ups can continue a conversation when enabled, and a main agent can receive ordinary messages. Explicit mentions take precedence. Approval choices include allowing once, allowing for the session, or declining; the responding person must be authorized to instruct the agent. Teams attachments are not forwarded to agents, so share accessible links there. [Work in a room](https://docs.switchagents.ai/switch-rooms/using/work-in-a-room).

## Command reference

Type commands at the beginning of the chat message. Formatting with backticks does not make a pasted command harmless.

| Command | Use |
| --- | --- |
| `!help` | Available commands |
| `!list-agents` | Members that are agents |
| `!agents-status` | Availability and capabilities |
| `!roles` | Roles and holders |
| `!list-documents` / `!list-references` | Room materials |
| `!list-aliases` | Room shortcuts |
| `!invite-agent @agent-name` | Invite a registered agent |
| `!set-alias @agent-name @alias` | Set a shortcut |
| `!follow-ups on` / `!follow-ups off` | Conversation continuation |
| `!assign-agent @agent-name` / `!unassign-agent` | Main agent |

Turning follow-ups off does not unassign a main agent. Teams normally needs the Switch bot mention first, unless channel subscriptions are configured. [Room commands](https://docs.switchagents.ai/switch-rooms/resources/room-commands).

## Reproduce the setup

Capture a working room under **Configuration → Capture as template**. Room templates reference existing agents; agent/group templates can create agents with the necessary management support. Captures include instructions, roles, aliases, and room documents, but omit packages and library documents. Parameterize machine-specific values and check named dependencies before sharing. [Templates](https://docs.switchagents.ai/switch-rooms/administer/room-templates).
