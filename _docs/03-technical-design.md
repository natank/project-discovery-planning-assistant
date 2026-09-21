# Project Discovery and Planning Assistant — Technical Design

**Status:** Draft
**Source:** [`02-product-requirements.md`](./02-product-requirements.md)
**Scope:** Initial end-to-end demonstration release

## Design goals

This design implements the first vertical slice defined by the product
requirements: one idea owner provides an idea, responds to focused
clarification prompts, and receives a structured, reviewable discovery
package. The implementation must make the CrewAI workflow, its handoffs, and
its outputs inspectable without exposing secrets or internal model reasoning.

The design prioritizes:

- a reproducible local setup;
- explicit, validated artifact contracts;
- a small, comprehensible CrewAI topology;
- a human review boundary before approval;
- meaningful status and failure reporting; and
- deterministic tests that do not require a live model provider.

## Architecture decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| AD-01 | Implement the demonstration in Python 3.11+ with CrewAI. | CrewAI is Python-native and is the framework being explored. |
| AD-02 | Provide a local command-line interface (CLI) as the initial interaction surface. | It supports guided input, review, and reproducible local execution without introducing web infrastructure. |
| AD-03 | Use a sequential CrewAI process with explicit typed task outputs. | The product workflow has a deliberate dependency chain; typed outputs make handoffs inspectable and testable. |
| AD-04 | Use Pydantic models as the canonical contract for input, state, task outputs, and exported packages. | Validated schemas prevent malformed success-shaped output and preserve traceability. |
| AD-05 | Persist each project as local JSON state plus a generated Markdown package. | This meets the single-project demonstration need while keeping artifacts portable and readable. |
| AD-06 | Use environment variables for model configuration and API credentials. | Secrets remain outside version control and provider choice stays configurable. |
| AD-07 | Do not use web search, external research tools, or external write integrations in the initial release. | The product must distinguish provided information from inference, and no integration is needed to prove the core workflow. |
| AD-08 | Treat package acceptance as an explicit local action performed by the idea owner. | This enforces the human-control boundary in NFR-02. |

## System context

```text
Idea owner
    |
    | CLI input, clarification answers, review decision
    v
Application service
    |
    +--> input and state validation
    +--> CrewAI orchestration
    +--> package validation and rendering
    +--> local project artifacts
    |
    v
Configured LLM provider
```

The delivery collaborator and reviewer consume the exported package. They are
not required to access the application in the initial release. The delivery
planner agent and package assembler generate the traceability references; the
delivery collaborator verifies those references as a human reader of the
exported package.

## Logical components

| Component | Responsibility | Inputs | Outputs |
| --- | --- | --- | --- |
| CLI | Guides the idea owner through each stage and reports status or errors. | Command arguments, interactive answers | Validated commands and readable status |
| Input service | Creates and updates the project context. | Idea, target user, outcome, constraints, answers | `ProjectContext` |
| Orchestrator | Selects and runs the applicable CrewAI workflow. | Validated context and workflow stage | Typed task results |
| Crew definitions | Defines agents, tasks, ordering, output contracts, and model configuration. | Context from prior task outputs | Validated domain artifacts |
| Package assembler | Combines domain artifacts, resolves traceability, and computes review state. | Task outputs and project state | `DiscoveryPackage` |
| Quality validator | Enforces structural, traceability, and certainty-label rules. | `DiscoveryPackage` | Validation result or actionable failure |
| Renderer | Writes a human-readable package without secrets or hidden reasoning. | Validated package | Markdown export |
| Project store | Reads and writes one local project directory. | Typed state and artifacts | Versioned local files |

## Proposed repository structure

```text
.
├── README.md
├── .env.example
├── pyproject.toml
├── src/
│   └── project_discovery_assistant/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── errors.py
│       ├── services/
│       │   ├── intake.py
│       │   ├── orchestration.py
│       │   ├── package_assembly.py
│       │   ├── quality.py
│       │   ├── rendering.py
│       │   └── project_store.py
│       └── crew/
│           ├── agents.py
│           ├── tasks.py
│           └── workflow.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── projects/                 # Git-ignored local runtime artifacts
└── _docs/
```

`projects/` is runtime data, not source. Tests must use temporary directories
instead of the developer's real project data.

## Domain model and artifact contracts

Pydantic models are the source of truth. Model-generated structured output is
validated at every task boundary before it can be consumed by a later task or
persisted as a package.

### Common metadata

Every material artifact includes:

- `id`: stable identifier appropriate to the artifact type;
- `status`: `draft`, `needs_review`, `accepted`, `deferred`, or `failed` as
  applicable;
- `certainty`: `provided`, `inferred`, `assumption`, or `open_question` for
  claims that require provenance;
- `source_refs`: references to the input, prior artifact, or decision that
  supports the item; and
- `version`: monotonically increasing project package version.

`source_refs` describe artifact-level provenance, not hidden model
chain-of-thought. The application stores concise, user-reviewable rationales
only.

### Core models

| Model | Key fields | Purpose |
| --- | --- | --- |
| `ProjectContext` | `project_id`, `idea`, `target_user`, `desired_outcome`, `constraints`, `answers`, `provided_facts` | Raw and normalized idea-owner input |
| `ClarificationQuestion` | `id`, `question`, `why_it_matters`, `priority`, `status` | Bounded question requested before or during planning |
| `DiscoverySummary` | `problem_statement`, `target_users`, `stakeholders`, `needs`, `outcomes`, `constraints`, `claims` | Problem and target-user framing |
| `ScopeProposal` | `mvp_outcome`, `included_capabilities`, `non_goals`, `follow_ons`, `trade_offs` | Proposed MVP boundary |
| `Risk` | `id`, `category`, `description`, `impact`, `certainty`, `validation_or_mitigation` | Risk that could affect the proposal |
| `ProductRequirement` | `id`, `statement`, `priority`, `target_user_or_outcome`, `rationale`, `dependencies`, `acceptance_considerations` | Observable product behavior |
| `UserStory` | `id`, `target_user_role`, `capability`, `value`, `priority`, `requirement_ids`, `acceptance_criteria` | User-centered expression of behavior |
| `BacklogItem` | `id`, `title`, `outcome`, `story_ids`, `priority`, `dependencies`, `validation_method`, `blockers` | Actionable delivery work |
| `ReviewDecision` | `artifact_ref`, `decision`, `comment`, `decided_at` | Idea-owner approval, rejection, or deferral |
| `DiscoveryPackage` | all artifacts, `traceability`, `review_state`, `generation_status`, `version` | Exportable project package |

### Identifier rules

The application creates stable IDs at package assembly:

- `CQ-001` for clarification questions;
- `RISK-001` for risks;
- `REQ-001` for requirements;
- `US-001` for user stories; and
- `BL-001` for backlog items.

IDs are retained when an item survives regeneration. New or materially changed
items receive new IDs; superseded items remain in project state with a
supersession reference. This makes changes reviewable without requiring
revision-history UI in the first release.

### Package validity rules

`DiscoveryPackage` is invalid when any of the following is true:

- a required top-level artifact is missing;
- an MVP story does not reference at least one requirement;
- an MVP story has no acceptance criteria;
- a backlog item has no linked story, outcome, priority, or validation method;
- a reference points to a nonexistent artifact;
- an accepted package contains an unresolved mandatory validation failure; or
- a claim has no certainty label where one is required.

An invalid package may be saved as a diagnostic draft but cannot be exported
as accepted.

## Interaction and workflow design

The CLI exposes explicit commands rather than running an uncontrolled,
open-ended conversation:

```text
pdpa new
pdpa clarify <project-id>
pdpa generate <project-id>
pdpa review <project-id>
pdpa accept <project-id>
pdpa export <project-id>
```

Command names are provisional; the technical contract is the stage boundary,
not the exact command spelling.

### Stage 1: Create and assess input

`new` collects the initial idea plus optional target user, desired outcome, and
constraints. The input service records blank optional fields as unknown, never
as inferred values.

The clarification assessor returns zero to five prioritized questions. Each
question includes why it matters. A user can answer, skip, or defer a
question. Skipped and deferred answers remain explicit in `ProjectContext`.

The design bounds the first question set to prevent a long form. A later
generation may surface additional open questions only when they materially
affect scope, risk, or acceptance criteria.

### Stage 2: Generate the discovery package

`generate` runs the sequential crew using the latest validated context:

```text
project context
  -> clarification assessment
  -> discovery framing
  -> scope and risk proposal
  -> requirements specification
  -> delivery backlog
  -> quality review
  -> package assembly and validation
```

Generation creates a `draft` package. The renderer emits a Markdown package
and the store persists the machine-readable state. A package with quality
errors is `failed` or `needs_review`, never silently marked complete.

### Stage 3: Review, correction, and acceptance

`review` displays the current artifacts, open questions, assumptions, risks,
quality findings, and decisions needed from the idea owner. The idea owner can
update context or record a decision.

When a material correction is made, the application marks dependent artifacts
as stale and regenerates them on the next `generate` command. The MVP
implementation regenerates the complete downstream package rather than
attempting partial task replay; accepted artifacts are preserved as a prior
version until the idea owner accepts the replacement.

`accept` succeeds only when:

- the package is structurally valid;
- no mandatory workflow stage failed;
- the idea owner explicitly confirms package acceptance; and
- unresolved assumptions and open questions are still shown in the final
  package.

### Stage 4: Export

`export` writes an accessible Markdown package that contains:

1. package metadata and review status;
2. project input and supplied evidence;
3. discovery summary;
4. assumptions, open questions, and risks;
5. MVP scope and non-goals;
6. requirements, stories, and acceptance criteria;
7. delivery backlog; and
8. traceability matrix.

The export excludes credentials, runtime environment values, provider
responses that are not part of the reviewed artifacts, and hidden reasoning.

## CrewAI design

### Process

Use `Process.sequential`. The workflow is intentionally ordered because scope
depends on framing, requirements depend on scope, and planning depends on
requirements. The quality review executes last and does not silently rewrite
approved upstream content.

A hierarchical manager process is not used in the first release. It would make
handoffs less predictable while adding little value to this bounded workflow.

### Agents

| Agent | Responsibility | Primary output |
| --- | --- | --- |
| Clarification analyst | Detects material ambiguity, contradiction, and missing context; proposes concise questions. | `ClarificationQuestion[]` |
| Discovery strategist | Frames the problem, target users, needs, outcomes, and constraints using only available context. | `DiscoverySummary` |
| Scope strategist | Proposes a focused MVP, non-goals, trade-offs, follow-ons, and risks. | `ScopeProposal`, `Risk[]` |
| Requirements analyst | Derives observable requirements, user stories, and acceptance criteria. | `ProductRequirement[]`, `UserStory[]` |
| Delivery planner | Builds a prioritized, dependency-aware delivery backlog. | `BacklogItem[]` |
| Quality reviewer | Checks completeness, coherence, traceability, certainty labels, and scope discipline. | `QualityReport` |

These are CrewAI agent roles, not product personas. Product personas are human
roles defined in the PRD.

### Tasks and handoffs

| Order | Task | Agent | Required input | Required output |
| --- | --- | --- | --- | --- |
| 1 | Assess clarification needs | Clarification analyst | `ProjectContext` | Questions or an explicit no-question result |
| 2 | Frame discovery | Discovery strategist | Context and answers | `DiscoverySummary` |
| 3 | Shape scope and risks | Scope strategist | Context and summary | `ScopeProposal`, `Risk[]` |
| 4 | Specify product behavior | Requirements analyst | Summary, scope, risks | Requirements and stories |
| 5 | Plan delivery | Delivery planner | Requirements and stories | Backlog items |
| 6 | Validate package quality | Quality reviewer | All prior outputs | `QualityReport` |

CrewAI task descriptions will state the relevant schema, certainty-label
rules, and forbidden behavior: no invented evidence, no claims of validation,
no external action, and no private reasoning in outputs.

CrewAI outputs must be converted to the corresponding Pydantic model before
the next task runs. A schema-validation failure stops the affected stage and
creates an actionable error record.

## Configuration and local infrastructure

### Dependencies

The implementation will declare the following classes of dependency in
`pyproject.toml`:

- `crewai` for agents, tasks, crews, and process orchestration;
- `pydantic` for contracts and validation;
- `pydantic-settings` for configuration;
- a CLI library such as `typer`;
- `pytest` and test helpers; and
- a formatter/linter selected during implementation.

Exact package versions will be pinned or constrained according to the package
manager's lock-file convention.

### Environment variables

`.env.example` documents names and non-secret placeholders only:

```dotenv
# Required: credentials for the configured provider. Never commit a real value.
OPENAI_API_KEY=

# Optional: model and endpoint override for a compatible provider.
MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=

# Local runtime configuration.
PDPA_PROJECTS_DIR=./projects
PDPA_LOG_LEVEL=INFO
```

The configuration layer must:

- load variables from the environment and an optional untracked `.env` file;
- fail fast with a clear message when a required credential or model setting is
  missing;
- redact secret values in errors and logs;
- validate that `PDPA_PROJECTS_DIR` resolves within the local workspace or an
  explicitly configured safe path; and
- prevent exports from including configuration values.

`OPENAI_*` is the initial provider contract because CrewAI uses LiteLLM-backed
model configuration. The application isolates configuration behind a model
factory so a compatible provider can be introduced without changing product
logic.

### Runtime artifacts

For a project ID `my-idea`, the project store uses:

```text
projects/
└── my-idea/
    ├── state.json
    ├── package-v001.md
    ├── package-v002.md
    └── run-events.jsonl
```

Writes use a temporary sibling file followed by an atomic rename where the
platform supports it. The store validates deserialized JSON before returning
it to the application.

## Error handling and observability

### Failure taxonomy

| Failure | Product behavior | Persisted status |
| --- | --- | --- |
| Invalid CLI input | Explain the invalid field and request correction. | No run started |
| Missing configuration | Explain the missing variable without exposing values. | No run started |
| Provider or network failure | Report the failed stage and a retry action. | `failed` |
| Crew task failure | Report agent task/stage and safe diagnostic context. | `failed` |
| Schema validation failure | Report invalid structured output; do not continue downstream. | `failed` |
| Quality validation finding | Display actionable findings for review or regeneration. | `needs_review` |
| Storage failure | Report that artifacts were not safely persisted. | `failed` |

The application must not catch all failures and continue. It may attach a
specific causal error to the project run, but it must propagate a non-zero CLI
exit code for failed commands.

### Run events

Each run records redacted, structured events:

- timestamp;
- project ID and package version;
- workflow stage and task name;
- start, success, failure, or skipped status;
- duration;
- model identifier, if configured; and
- safe error category and message when relevant.

Run events must not contain API keys, raw environment values, or hidden model
reasoning. Idea-owner content is recorded only in project artifacts; logs
should use identifiers and summaries where possible.

## Quality assurance strategy

### Automated checks

| Test level | Scope | Live model required |
| --- | --- | --- |
| Unit | Pydantic validation, ID allocation, traceability, certainty labels, review-state transitions, renderer, and store | No |
| Contract | Mocked task outputs converted through the CrewAI adapter | No |
| Integration | Full CLI happy path using deterministic fake crew outputs | No |
| Smoke | One manually initiated real-provider run using non-sensitive fixture input | Yes, opt-in |

The deterministic fake crew implements the same adapter contract as the real
CrewAI runner. It lets the test suite verify the product contract without
calling an uncontrolled external service.

### Required validation scenarios

- minimal idea with missing optional context;
- ambiguous idea that produces focused clarification questions;
- deferred answer carried into open questions;
- provided, inferred, assumed, and open-question labels in one package;
- requirement-to-story-to-backlog traceability;
- missing acceptance criteria rejected by the quality validator;
- invalid task output stops the workflow without an accepted export;
- material input correction marks downstream artifacts stale;
- explicit acceptance required before accepted export; and
- missing API key produces a redacted configuration error.

### Quality report rules

The quality reviewer reports findings with severity:

- `error`: package cannot be accepted or exported as accepted;
- `warning`: package may proceed only with an explicit unresolved item; and
- `note`: recommended human review without blocking progression.

Programmatic validation enforces structural rules. The CrewAI quality reviewer
provides semantic findings, which remain visible to the idea owner and never
automatically become accepted facts.

## Requirements traceability

| Requirements | Design response | Validation |
| --- | --- | --- |
| FR-01, FR-15 | CLI intake, `ProjectContext`, input validation, qualified partial state | Unit and CLI integration tests |
| FR-02, FR-03 | Clarification analyst, bounded questions, deferred-answer state | Fixture-based workflow test |
| FR-04, FR-05 | Discovery schemas, certainty labels, source references | Schema and rendered-package tests |
| FR-06, FR-07 | Scope strategist, scope and risk models | Contract test with fixture output |
| FR-08, FR-09, FR-10 | Requirements analyst and validated requirement/story schemas | Traceability and criteria tests |
| FR-11 | Delivery planner and backlog schema | Dependency and validation-method tests |
| FR-12 | Package assembler and programmatic traceability validator | Broken-reference rejection test |
| FR-13 | Review decisions, stale state, versioned package generation | Review and regeneration integration test |
| FR-14 | Markdown renderer and export command | Export content and secret-exclusion test |
| FR-16 | CLI status and redacted run events | Success, failure, and retry-message tests |
| NFR-01–NFR-02 | Certainty labels, explicit acceptance, no external write tools | Artifact and state-transition tests |
| NFR-03 | Schemas, versioned artifacts, deterministic fake crew | Repeatable integration fixture |
| NFR-04–NFR-05 | Guided commands, bounded questions, typed failures | CLI interaction and error-path tests |
| NFR-06–NFR-07 | Environment config, redaction, local event log | Configuration and log-safety tests |
| NFR-08–NFR-09 | Test fixture strategy and structured Markdown renderer | CI test run and package snapshot |

## Security and privacy boundaries

- Do not commit `.env`, project artifacts, API keys, or production-like user
  data.
- Include `.env` and `projects/` in `.gitignore`; commit `.env.example` only.
- Use synthetic or non-sensitive ideas in fixtures and demonstrations.
- Do not grant agents file-write tools beyond the application-controlled
  project store.
- Do not configure tools that make network requests beyond the configured
  model provider in the initial release.
- Redact secrets from logs, error messages, events, and exported packages.
- Treat provider prompts as external disclosure of project input; document
  that local runs send input to the configured provider.

## Deferred design work

The following remains out of the first implementation slice:

- browser-based user interface;
- user authentication and multi-user authorization;
- database-backed persistence and concurrent editing;
- external search, retrieval, or domain research;
- project-management-system integration;
- incremental dependency-graph regeneration;
- background workers, queues, and asynchronous execution;
- hosted deployment, monitoring platform, and production SLOs; and
- alternative artifact formats beyond Markdown and JSON.

These capabilities should be designed as extensions of the validated artifact
contracts and review boundary, not as shortcuts around them.

## Open implementation questions

These questions must be resolved during implementation planning without
changing the product contract:

1. Which supported CrewAI and Python versions provide stable structured-output
   support for the selected models?
2. Which CLI library best fits the desired local command ergonomics?
3. What model default provides sufficient artifact quality at an acceptable
   demonstration cost?
4. What retry policy is appropriate for transient provider failures without
   hiding persistent failure?
5. Which formatter, linter, and type checker best fit the Python toolchain?
6. Does the initial CrewAI version allow all task schemas to be enforced
   directly, or is an adapter required at each handoff?
