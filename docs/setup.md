# Setup and observed environment

## Local prerequisites

Python 3.11+ and Git are enough for the local CLI, tests, and rehearsal. No pip install is required when commands are run from the project root. Optional package installation exposes `proofdesk` and `proofdesk-review`, but is not needed for the documented path.

```powershell
python --version
git --version
python -m unittest discover -s tests -v
python -m scripts.demo
```

State and generated fixture repositories live in `.proofdesk/`, which is ignored by Git. Rehearsal creates a new case and fixture repository on each invocation; existing cases are preserved.

## Observed November 4, 2026

| Component | Observation |
| --- | --- |
| Python | 3.11.9 |
| Git | 2.51.0.windows.1 |
| Codex CLI | 0.166.0 via `codex.cmd --version`; sign-in not verified |
| Docker executable | Installed; engine pipe unavailable during check; config access also restricted |
| Switch process | No running process found by the process-name check |
| Console/server version | Not verified locally |
| Live room exchange | Not performed |

PowerShell selected `codex.ps1`, which this environment's execution policy refuses. The installed `codex.cmd` reports its version without changing execution policy. This verifies the executable, not that a Switch runtime can launch or authenticate it.

## Switch setup sequence

1. Open/install the appropriate released Switch Console and record its actual version.
2. Choose the local setup supported by that release. For the bundled Mattermost path requiring Docker, start Docker Desktop and confirm its engine is available first. Newer releases also describe a Docker-free option; do not assume it bundles the same messaging stack.
3. Verify the selected agent provider is installed and signed in from Console's Agent providers page.
4. Add the server, connect or open the chosen messaging app, and link your personal messaging identity.
5. Import [proofdesk.template.yaml](../switch/proofdesk.template.yaml). Supply a unique prefix, existing absolute project directory, provider, run location, and connected bridge. This draft has not been validated by a running Switch server.
6. Confirm preview membership: Concierge/Builder in support; Builder/Verifier in engineering; owner in both.
7. Confirm owner-agents addressing works for each actual agent handoff. Additional human teammates need explicit permissions.
8. Read the actual role files on the agent machine and perform the [live demo sequence](demo.md).

The template assumes one machine and a common project/state directory. A managed remote machine must already have the repository, Python, Git, provider sign-in, and access to the demo repository. Do not claim cross-host synchronization from this shared-directory prototype.

Source contracts: [Switch quickstart](https://docs.switchagents.ai/switch-rooms/getting-started), [template language](https://github.com/sandbox-quantum/switch/blob/main/docs/TEMPLATES.md). Follow the installed release if the current development documentation differs.
