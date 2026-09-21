# Milestone M2 — Deterministic Vertical Slice Kickoff

**Status:** Draft
**Milestone:** M2 — Deterministic vertical slice
**Source:** [`04-delivery-plan.md`](../04-delivery-plan.md)
**Kickoff branch:** `docs/M2-kickoff`
**Implementation branch:** `feat/M2-deterministic-slice`

## Objective

Deliver the first complete, provider-free product workflow. An idea owner must
be able to create a project, provide and clarify an idea, generate a validated
discovery package through a deterministic fake runner, inspect its status and
unresolved items, and receive a readable Markdown draft.

M2 proves the product contract end to end before model behavior or CrewAI
integration is introduced. The fake runner must conform to the adapter
interface that the real sequential CrewAI runner will implement in M3.

## Expected outcome

At the end of M2:

- the CLI can create and update one project;
- clarification questions and answers are persisted;
- a deterministic runner produces all required domain artifacts;
- each runner boundary is schema validated;
- package assembly enforces IDs and traceability;
- the Markdown package is readable and reviewable by collaborators;
- draft and needs-review status are visible; and
- the complete happy path and important failure paths run without a provider
  credential or network access.

## Scope

### In scope

- DP-04: CLI intake, clarification answers, and project commands;
- DP-05: runner adapter and deterministic fake crew;
- DP-06: package assembly, validation, and rendering;
- DP-07: deterministic end-to-end draft workflow;
- B-01 through B-12 for the deterministic path;
- CLI commands needed for `new`, `clarify`, and `generate`;
- fixture-driven runner outputs;
- Markdown export of a draft package; and
- integration tests using temporary project directories.

### Out of scope

- real CrewAI agents, tasks, model calls, or provider smoke runs (DP-08);
- explicit review, correction, regeneration, and acceptance commands (DP-09
  and DP-10);
- semantic quality judgments beyond deterministic structural checks;
- web UI, authentication, external research, or delivery-tool integrations;
- asynchronous execution or background workers; and
- production deployment.

## Linked requirements and design

| Source | Link |
| --- | --- |
| Delivery stories | DP-04, DP-05, DP-06, DP-07 |
| PRD backlog | B-01 through B-12 |
| Milestone exit criterion | The CLI creates and clarifies a project, then produces a validated draft Markdown package with the fake crew and no API key. |
| Functional requirements | FR-01 through FR-12, FR-14 through FR-16 |
| Quality requirements | NFR-01, NFR-03 through NFR-09 |
| Technical design | CLI stages; domain contracts; package validity rules; runner handoffs; package assembly; rendering; deterministic fake crew |

## Tailored detailed-design decision

**Decision: required for M2.**

The approved technical design defines the components and workflow but leaves
the application-level runner protocol, fixture shape, command behavior, and
Markdown section contract open. These interfaces must be fixed before the
real CrewAI adapter is added in M3.

### Runner protocol

Define a `DiscoveryRunner` protocol with stage methods that accept validated
context and return validated domain objects:

```text
assess_clarification(context)
  -> ClarificationQuestion[]

frame_discovery(context)
  -> DiscoverySummary

propose_scope(context, summary)
  -> ScopeProposal, Risk[]

specify_requirements(context, summary, scope, risks)
  -> ProductRequirement[], UserStory[]

plan_delivery(requirements, stories)
  -> BacklogItem[]

review_quality(all_artifacts)
  -> QualityReport
```

The orchestration service owns ordering and package assembly. The runner owns
stage execution. The CLI and persistence services must not import CrewAI or
fixture implementation details.

### Deterministic fake

The fake runner returns a known, schema-valid project package for a fixture
idea, using only the supplied context and deterministic identifiers. It must
also expose controlled failure modes for:

- invalid task output;
- a failed stage;
- a clarification question result; and
- a quality error.

Tests select these modes explicitly; production commands must not depend on
test-only behavior.

### CLI contract

M2 implements the following commands:

```text
pdpa new
pdpa clarify <project-id>
pdpa generate <project-id>
```

Command output must identify project ID, stage status, package status, output
path, unresolved items, and the next action. Commands return non-zero status
for invalid input, missing projects, failed stages, schema failures, and
storage failures.

`new` records idea, target user, desired outcome, and constraints. `clarify`
records answer, skip, or defer decisions. `generate` executes the complete
deterministic sequence and persists a draft package.

### Markdown contract

The draft package contains, in order:

1. metadata and generation status;
2. idea-owner input and provided evidence;
3. discovery summary;
4. certainty labels, assumptions, and open questions;
5. risks;
6. MVP scope and non-goals;
7. functional requirements;
8. user stories and acceptance criteria;
9. prioritized backlog; and
10. outcome-to-backlog traceability.

Artifact IDs are visible in headings, tables, or references. The renderer must
not include credentials, environment values, raw provider responses, or hidden
reasoning.

## Planned implementation commits

The implementation branch is `feat/M2-deterministic-slice`. It must contain at
least one independently valid implementation commit; the following four-commit
plan preserves the vertical-slice boundaries:

| Commit | Planned commit | Contents |
| --- | --- | --- |
| M2-C1 | `Implement deterministic CLI intake workflow` | CLI commands, input validation, clarification state updates, and command-level tests |
| M2-C2 | `Add runner protocol and deterministic fake` | Runner protocol, fake outputs/failure modes, boundary validation, and contract tests |
| M2-C3 | `Assemble and render discovery packages` | Package assembler, traceability generation, Markdown renderer, and export/secret-safety tests |
| M2-C4 | `Wire deterministic end-to-end generation` | Orchestration, stage events/status, draft persistence, full CLI integration tests, and M2 validation |

If implementation reveals a necessary contract change, update this kickoff
before expanding the approved scope or changing the commit sequence.

## Acceptance criteria

1. An idea owner can create a project with required and optional context using
   the CLI without a provider credential.
2. Optional blank context remains explicitly unknown and is not invented.
3. Clarification questions can be answered, skipped, or deferred and remain
   visible in persisted state.
4. The fake runner returns typed results for every defined stage.
5. Invalid runner output stops downstream execution and produces a non-zero
   command result.
6. `generate` creates a structurally valid draft or needs-review package with
   all required PRD sections.
7. Requirements, stories, acceptance criteria, backlog items, and traceability
   references are present and navigable by stable IDs.
8. Provided, inferred, assumption, and open-question content is visibly
   distinguished where applicable.
9. The Markdown package contains no credentials, environment values, raw
   provider responses, or hidden reasoning.
10. A delivery collaborator can review outcome-to-backlog links from the
    exported Markdown without using the CLI.
11. Failed stages and quality errors are visible and never appear as accepted
    success.
12. The full deterministic workflow runs from a temporary project directory
    with no network access or provider credential.

## Validation plan

| Check | Purpose | Provider credential |
| --- | --- | --- |
| CLI unit tests | Validate input parsing, project selection, and status messages | No |
| Runner contract tests | Validate fake outputs and boundary failures | No |
| Renderer tests | Validate required sections, IDs, and secret exclusion | No |
| Traceability tests | Validate complete outcome-to-backlog links | No |
| End-to-end CLI test | Validate `new` → `clarify` → `generate` | No |
| Failure-path integration tests | Validate failed stage and invalid output behavior | No |
| `uv run pytest` | Validate the provider-free suite | No |
| Ruff and mypy commands | Validate formatting, lint, and typing | No |

M2 does not require a live-provider smoke run. That evidence belongs to M3.

## Dependencies and risks

### Dependencies

- M0 and M1 kickoff and implementation PRs must be merged into `main`.
- M2 consumes M1 models, validation, `ProjectStore`, `RunEvent`, and
  configuration/error boundaries.
- M3 must implement the runner protocol without changing the product-facing
  orchestration contract.

### Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Fake outputs hide ambiguity in the real workflow | Include explicit question, deferred-answer, and quality-error fixtures |
| CLI design becomes an accidental long-term UI contract | Keep commands thin and services protocol-driven |
| Renderer duplicates domain truth | Render only validated models and test required sections against the model contract |
| Orchestration bypasses validation | Validate every runner result before passing it downstream |
| Traceability is generated but not readable | Use stable IDs in every relevant section and test traversal from outcome to backlog |
| M2 expands into review UX | Keep acceptance/correction actions explicitly deferred to DP-09 and DP-10 |

## Branch and review workflow

1. Commit this kickoff on `docs/M2-kickoff`.
2. Open and merge the kickoff pull request into `main`.
3. Create `feat/M2-deterministic-slice` from the updated `main`.
4. Implement M2-C1 through M2-C4 and attach validation evidence to the
   implementation pull request.
5. Merge the implementation pull request only after the M2 exit criterion and
   all acceptance criteria pass.
6. Update the delivery plan with M2 completion evidence before starting M3.

## Exit evidence

M2 is complete only when all of the following are available:

- merged M2 kickoff pull request;
- implementation pull request with at least one valid implementation commit;
- passing provider-free CLI, runner, renderer, traceability, and integration
  tests;
- passing pytest, Ruff, and mypy commands;
- a generated Markdown draft reviewed against the PRD acceptance baseline;
- evidence that failure and invalid-output paths are visibly non-successful;
- evidence that the export excludes secrets and hidden reasoning; and
- implementation review confirming the M2 acceptance criteria.
