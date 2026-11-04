# Official examples and possible project ideas

[Back to index](../../README.md)

## Official scenarios

These illustrate possible workflows; they are not guaranteed outcomes or ready-made implementations.

| Scenario | What to learn |
| --- | --- |
| [Cross-time-zone engineering](https://docs.switchagents.ai/switch-rooms/use-cases/across-time-zones) | An agent with access to another team's repository prepares a fix; a human reviews the merge |
| [Incident response](https://docs.switchagents.ai/switch-rooms/use-cases/incident-response) | Investigation, escalation, customer notice, and decisions stay in a thread |
| [Sensitive support data](https://docs.switchagents.ai/switch-rooms/use-cases/guardrails) | Configured Switch Trust redacts selected message text before agents receive it |
| [Product launch](https://docs.switchagents.ai/switch-rooms/use-cases/product-launch) | Engineering, copy, and brand review coordinate a release |
| [Meeting preparation](https://docs.switchagents.ai/switch-rooms/use-cases/meeting-prep) | Specialists gather sourced information and draft a presentation |
| [Customer onboarding](https://docs.switchagents.ai/switch-rooms/use-cases/customer-onboarding) | Room membership lets agents carry earlier requirements into onboarding |
| [Vendor review](https://docs.switchagents.ai/switch-rooms/use-cases/vendor-review) | Security, legal, and finance work from their own evidence |
| [Open-source review](https://docs.switchagents.ai/switch-rooms/use-cases/open-source-contribution) | Contributor and reviewer agents settle an edge case before maintainer review |

Important details: the incident example's instruction to wait does not itself block production credentials. In the support example, original text remains visible in Slack, messages with attachments bypass that described text check, and unavailable Trust checks are flagged. Do not describe these examples as universal enforcement. [Incident setup](https://docs.switchagents.ai/switch-rooms/use-cases/incident-response), [guardrail limitations](https://docs.switchagents.ai/switch-rooms/use-cases/guardrails).

## Worked setup and template

The [payments room walkthrough](https://docs.switchagents.ai/switch-rooms/building/payments-room) builds a channel around repository context, room instructions, a reviewer job, and a single release holder. It is a useful blueprint for assigning jobs while distinguishing instructions from access controls.

The repository's [triage pair template](https://github.com/sandbox-quantum/switch/blob/main/examples/agent-templates/triage-pair.template.yaml) creates a triager, reproducer, and shared room. Use the actual YAML as a starting point rather than copying the condensed snippet on the event page. Validate provider, location, directory, bridge, and addressing choices against your release.

## Suggested small builds

These are original suggestions, not organizer-endorsed entries:

| Idea | Minimal input | Agent work | Human decision | Deliverable |
| --- | --- | --- | --- | --- |
| Bug desk | Report plus sample repository | Clarify, reproduce, propose fix | Accept proposed change | Reproduction script and patch |
| Release desk | Sample commit history | Draft notes, check supporting evidence | Approve final wording | Release draft and checklist |
| Study room | A small folder of course notes | Create questions and evaluate answers | Choose weak topic to revisit | Study plan and progress record |
| Creative brief room | Brief plus sample brand guide | Draft and critique options | Select and revise | Finished copy with review trail |

Pick a real input you can safely show, and define a measurable outcome before adding agents or rooms.
