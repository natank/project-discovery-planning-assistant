# Milestone M3 — CrewAI Integration Kickoff

**Status:** Draft  
**Milestone:** M3 — CrewAI integration  
**Source:** [`04-delivery-plan.md`](../04-delivery-plan.md)  
**Kickoff branch:** `docs/M3-kickoff`  
**Implementation branch:** `feat/M3-crewai-runner`

## Objective

Replace the deterministic runner with a real, sequential CrewAI adapter without
changing the product-facing runner contract. M3 proves that configured model
calls can produce the same validated discovery package shape while preserving
stage visibility, safe failures, traceability, and the human review boundary.

## Expected outcome

At the end of M3:

- six CrewAI roles and ordered tasks map to the existing `DiscoveryRunner`
  protocol;
- every task result is converted to a Pydantic domain model before the next
  task consumes it;
- model configuration is created through the typed settings boundary;
- provider, task, and schema failures stop the affected workflow with safe
  diagnostics;
- the default test suite remains provider-free;
- a manually initiated smoke run with a non-sensitive fixture produces a
  reviewable draft; and
- no agent has search, external-write, or unrestricted tool capability.

## Scope

### In scope

- DP-08: the sequential CrewAI runner;
- clarification, discovery, scope, requirements, delivery planning, and quality
  reviewer agents;
- sequential task definitions and typed output conversion;
- model-factory configuration through `Settings`;
- mocked adapter contract tests and failure-path tests;
- narrow retries for documented transient provider failures;
- safe stage events and redacted diagnostics; and
- an opt-in provider smoke command and inspection checklist.

### Out of scope

- review, correction, regeneration, acceptance, and export commands from M4;
- web UI, authentication, external research, or delivery-tool integrations;
- agent tools that write files or make uncontrolled network requests;
- asynchronous or hierarchical CrewAI execution;
- changing domain models or the product-facing `DiscoveryRunner` protocol
  without updating this kickoff and the delivery plan; and
- making provider credentials mandatory for ordinary tests or CLI intake.

## Linked requirements and design

| Source | Link |
| --- | --- |
| Delivery story | DP-08 |
| PRD backlog | B-03 through B-08, B-13 |
| Milestone exit criterion | The real sequential CrewAI runner satisfies the fake runner contract and an opt-in smoke run produces a reviewable draft. |
| Functional requirements | FR-03 through FR-08, FR-14, FR-16 |
| Quality requirements | NFR-01, NFR-03, NFR-05 through NFR-09 |
| Technical design | CrewAI sequential process, typed handoffs, model configuration, safe failures, and event logging |

## Tailored detailed-design decision

**Decision: required for M3.**

The approved technical design establishes the topology but does not define the
application-level CrewAI construction details. This kickoff fixes the adapter
boundary, role/task mapping, output conversion, configuration behavior, retry
policy, smoke command, and security restrictions before implementation.

### Adapter boundary

`CrewAIRunner` implements the existing `DiscoveryRunner` protocol. Each public
stage method:

1. receives validated domain models;
2. constructs or invokes the corresponding CrewAI task;
3. reads the task's structured result;
4. converts it into the exact Pydantic domain model;
5. raises a typed runner error when conversion or execution fails; and
6. returns only validated data to the orchestrator.

The runner must not persist files, render Markdown, mutate project state, or
expose raw provider responses to the CLI.

### Agent and task mapping

| Order | Agent role | Task output | Inputs |
| --- | --- | --- | --- |
| 1 | Clarification analyst | `ClarificationQuestion[]` | `ProjectContext` |
| 2 | Discovery analyst | `DiscoverySummary` | `ProjectContext` and clarification state |
| 3 | Scope planner | `ScopeProposal` and `Risk[]` | Context and discovery summary |
| 4 | Product requirements analyst | `ProductRequirement[]` and `UserStory[]` | Context, summary, scope, and risks |
| 5 | Delivery planner | `BacklogItem[]` | Requirements and stories |
| 6 | Quality reviewer | `QualityReport` | All prior validated artifacts |

The process is `Process.sequential`. Tasks explicitly forbid invented
evidence, unsupported certainty, claims of external validation, external
actions, and hidden reasoning in returned artifacts.

### Configuration and retry policy

The model factory reads provider configuration lazily from `Settings`; import,
intake, deterministic tests, and mocked adapter tests must not require an API
key. Provider and model identifiers remain outside agent definitions.

Only recognized transient provider/network failures may be retried, with a
bounded attempt count. Schema failures, invalid task results, missing
configuration, authentication failures, and quality errors are not retried.
Every attempted stage records safe event metadata without credentials, prompts,
raw responses, or environment values.

### Tool restrictions

Agents receive no search, file-write, shell, database, or unrestricted network
tools. The application owns persistence and rendering. If CrewAI requires a
tool list, it must be explicitly empty or limited to an approved in-memory
operation with no external side effects.

## Planned implementation commits

The implementation branch is `feat/M3-crewai-runner`. The work is split into
four independently reviewable commits:

| Commit | Planned commit | Contents |
| --- | --- | --- |
| M3-C1 | `Define CrewAI model factory and agent roles` | Lazy model configuration, six agent definitions, and configuration tests |
| M3-C2 | `Implement typed sequential CrewAI tasks` | Ordered tasks, schema-boundary conversion, prompt restrictions, and mocked task tests |
| M3-C3 | `Implement CrewAI runner and safe failure handling` | `DiscoveryRunner` adapter, bounded transient retries, redacted events, and contract tests |
| M3-C4 | `Add opt-in CrewAI smoke validation` | Non-sensitive smoke command, documentation, smoke output checks, and M3 integration validation |

If implementation requires a product-contract change, update this kickoff and
obtain review before changing the runner protocol or commit sequence.

## Acceptance criteria

1. `CrewAIRunner` conforms to every contract test exercised by the deterministic
   runner.
2. Each task result is schema-validated before downstream consumption.
3. Missing configuration, provider failure, task failure, and invalid output
   produce distinguishable, safe, non-zero failures.
4. The default test suite runs without network access or provider credentials.
5. An opt-in smoke run using non-sensitive fixture input produces a draft or
   needs-review package and records redacted stage events.
6. The generated package preserves stable IDs, certainty labels, and
   outcome-to-backlog traceability.
7. The runner exposes no search, external-write, or unrestricted tool
   capability.
8. Raw provider responses, prompts, credentials, environment values, and
   hidden reasoning are absent from persisted events and exported Markdown.
9. The deterministic runner remains available for repeatable tests.

## Validation plan

| Check | Purpose | Provider credential |
| --- | --- | --- |
| Model-factory unit tests | Validate lazy configuration and safe missing-variable errors | No |
| Agent/task construction tests | Validate six roles, sequential ordering, restrictions, and output schemas | No |
| Mocked adapter contract tests | Validate conversion of every task result to domain models | No |
| Failure-path tests | Validate provider, task, schema, and retry boundaries | No |
| Default `uv run pytest` | Preserve the provider-free deterministic suite | No |
| Ruff and mypy | Validate formatting, lint, and typing | No |
| Opt-in smoke command | Run one non-sensitive real-provider package generation | Yes |
| Manual smoke review | Inspect package completeness and redacted event log | Yes |

The smoke command must be excluded from the default suite and must fail
explicitly when provider configuration is missing. Smoke input must be
synthetic and must never include credentials or private project content.
Execute the full procedure in [`M3-smoke-test.md`](./M3-smoke-test.md).

## Dependencies and risks

### Dependencies

- M2 implementation and closure are merged into `main`.
- M3 consumes the existing `DiscoveryRunner`, domain models, validation,
  orchestration, rendering, configuration, and event boundaries.
- A configured provider is required only for the opt-in smoke run.

### Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| CrewAI structured output differs by model/provider | Convert and validate at every task boundary; retain mocked contract tests |
| Provider failures appear as successful drafts | Map failures to typed errors and failed events; never persist success-shaped output |
| Prompts or responses leak into artifacts | Allow-list event fields and inspect smoke output for secret/raw-content exclusion |
| Retry masks permanent failures | Retry only a documented transient exception set with bounded attempts |
| Agent tools create uncontrolled side effects | Configure no tools and keep persistence/rendering in application services |
| Live smoke becomes required for ordinary development | Keep it opt-in and preserve the deterministic runner as the default |

## Branch and review workflow

1. Commit this kickoff on `docs/M3-kickoff`.
2. Open and merge the kickoff pull request into `main`.
3. Create `feat/M3-crewai-runner` from the updated `main`.
4. Implement M3-C1 through M3-C4 and attach validation evidence to the
   implementation pull request.
5. Merge the implementation pull request only after the M3 acceptance criteria
   and validation evidence are reviewed.
6. Update the delivery plan with M3 completion evidence before starting M4.

## Exit evidence

M3 is complete only when all of the following are available:

- merged M3 kickoff pull request;
- implementation pull request with the planned runner commits;
- passing mocked adapter, task-schema, failure, retry-boundary, and default
  provider-free tests;
- passing Ruff and mypy checks;
- a documented opt-in smoke command;
- a non-sensitive smoke package manually reviewed for completeness;
- a redacted smoke event log with no credentials or raw provider response; and
- implementation review confirming the M3 acceptance criteria.
