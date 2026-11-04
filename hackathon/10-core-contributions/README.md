# Core contribution track

[Back to index](../../README.md)

## Event-specific requirements

Choose a hackathon-labelled issue; comment with your approach and tag `@petr-sandbox`. Wait for assignment. Only your assigned issues count; keep at most five PRs open. Inactivity after 48 hours can lose assignment. Avoid spam and superficial/unreviewed changes. Early work is allowed; open the PR by the event cutoff and include `Closes #number`. [Contribution track rules](https://www.wemakedevs.org/hackathons/switch).

The [filtered issue list](https://github.com/sandbox-quantum/switch/issues?q=is%3Aissue+state%3Aopen+label%3Ahackathon) could not be fetched during research. No particular issue is claimed to be available or assigned.

## Development setup

Read [CONTRIBUTING.md](https://github.com/sandbox-quantum/switch/blob/main/CONTRIBUTING.md) in the checkout/version you will modify. The reviewed guide requires Docker, `uv`, and `just` and shows:

```text
just init-env
uv sync
just gateway-install
just up
just run
```

Run `just gateway-dev` in another terminal for the frontend. Supporting services run in Docker; core runs locally on port 8000. Use the guide's actual recipes for checks relevant to your change. Commands here are documentation only; nothing was installed or started.

## Suggested PR workflow

1. Confirm assignment and expected behavior on the issue.
2. Reproduce the problem on the relevant checkout.
3. Make a focused implementation and verify the changed behavior.
4. Run the repository-required checks.
5. Explain the trigger, fix, validation, and remaining limits in the PR.
6. Respond to review and keep the issue active.

These workflow steps are practical advice, in addition to the event's assignment rules.

The project requires a one-time contributor license agreement on your first PR. Follow its code of conduct; report vulnerabilities privately using SECURITY.md. Provider integrations and messaging adapters have repository-specific contribution guides. [Contribution documentation](https://docs.switchagents.ai/switch-rooms/resources/contribute).

See [tracks and judging](../03-tracks-and-judging/README.md) for the inconsistent published winner counts.
