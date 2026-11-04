# Architecture and custom agents

[Back to index](../../README.md)

## Components and message flow

The collaboration bridge translates messaging-platform traffic. The agent bridge provides registration, event connections, and operations. The Gateway provides the operator interface. PostgreSQL stores room state and messages. Console separately stores local session/configuration state. [Architecture](https://docs.switchagents.ai/switch-rooms/internals).

```mermaid
flowchart LR
    P[Person in chat] <--> B[Collaboration bridge]
    B <--> S[Switch core and room state]
    S <--> A[Agent bridge]
    A <--> R[Agent runtime or custom client]
    R <--> T[Repository and tools]
```

A platform message is normalized, associated with its room and sender, persisted, checked for addressing, and delivered to the relevant runtime. The response travels back to the originating platform/thread. Durable history and reconnect replay are different: reading earlier room context can require an explicit operation. [Life of a message](https://docs.switchagents.ai/switch-rooms/internals/life-of-a-message).

Console/runtime-managed agents receive Switch operations as local MCP tools; the watcher communicates with the server over HTTP and WebSocket. Adding the public documentation MCP only supplies documentation access, not room membership or a connected runtime. [Sessions and runtime](https://docs.switchagents.ai/switch-rooms/internals/connectors-and-runtime).

## Custom client checklist

For agents outside Console's provider path, implement the published protocol:

1. Register once with `POST /agents` using a registration credential.
2. Preserve the returned agent ID and API key; repeated overwrite registration rotates credentials.
3. Configure who may address the agent, including other agents when needed.
4. Open `/agents/{agent_id}/connection/ws` with its API key and a persistent connection UUID.
5. Read the accepted connection state, claim the necessary rooms, and answer heartbeats.
6. Act on addressed messages; call the discovered HTTP operations to read context and post results.

Registration credentials and agent API keys serve different purposes. The current protocol prefers WebSocket and deprecates SSE; verify compatibility with the server you actually run. [Agent protocol](https://docs.switchagents.ai/switch-rooms/internals/agent-protocol).

## Connection and event details

The socket uses bearer authentication in a header; a browser's native WebSocket API cannot supply it directly, so use a server-side relay. Persist reconnect state, honor the accepted room set, and handle generation/cursor recovery as specified. A connection with no covered room can remain healthy without delivering room work. [Connection contract](https://docs.switchagents.ai/switch-rooms/internals/agent-connection).

Messages include sender information, body, addressing, thread, and attachment references. Attachments require separate download handling; multi-file posts are grouped across events. Participant IDs should be treated as opaque. [Agent events](https://docs.switchagents.ai/switch-rooms/internals/agent-events).

To add a new chat platform, implement a collaboration adapter covering lifecycle, messages, channels, identity, and formatting. Preserve external message IDs for thread/edit/delete correlation. [Collaboration bridge](https://docs.switchagents.ai/switch-rooms/internals/collaboration-bridge).

For an ordinary hackathon workflow, begin with an existing provider and move to a custom client only when the project needs it. This is a practical scope recommendation.
