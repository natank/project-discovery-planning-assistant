# Milestone M1 — Contract Foundation Kickoff

**Status:** Draft
**Milestone:** M1 — Contract foundation
**Source:** [`04-delivery-plan.md`](../04-delivery-plan.md)
**Kickoff branch:** `docs/M1-kickoff`
**Implementation branch:** `feat/M1-contract-foundation`

## Objective

Implement the validated domain contracts, stable identifiers, package-quality
rules, local project persistence, and redacted run-event storage required by
all later application workflows.

At the end of M1, the project can represent and validate the complete
discovery-package shape, reject invalid packages, persist valid state in an
isolated local project directory, and record safe run events without a model
provider or CLI workflow.

## Expected outcome

M1 provides the non-agent foundation for the product:

- Pydantic models for project context and every discovery-package artifact;
- stable artifact IDs and version metadata;
- certainty, review, generation, and quality-finding states;
- structural and traceability validation;
- atomic local JSON and Markdown artifact persistence;
- accepted-version retention when a later draft is written; and
- redacted, structured run-event persistence.

## Scope

### In scope

- DP-02: domain contracts, identifiers, and package-quality rules;
- DP-03: local project persistence and redacted run events;
- models defined in the technical design;
- invalid-package rules and quality finding severities;
- project-ID and artifact-ID validation;
- versioned package storage and accepted-draft separation;
- temporary-file/atomic-replacement writes where supported; and
- deterministic unit tests and negative fixtures.

### Out of scope

- interactive CLI commands or user-facing workflow orchestration (DP-04);
- CrewAI agents, tasks, runner adapters, or model calls (DP-05 and DP-08);
- package generation from an idea;
- semantic quality judgments that require a model;
- browser UI, database persistence, authentication, or external integrations;
- revision-history UI beyond retaining persisted versions; and
- changes to the approved product requirements or technical architecture.

## Linked requirements and design

| Source | Link |
| --- | --- |
| Delivery stories | DP-02 and DP-03 |
| PRD backlog | B-01, B-05, B-09, B-10, B-12, B-13, B-15 |
| Milestone exit criterion | Validated contracts, local persistence, IDs, events, and invalid-package handling pass unit tests without a model provider. |
| Product requirements | FR-05, FR-12, FR-13, FR-14, FR-16; NFR-01, NFR-02, NFR-03, NFR-05, NFR-06, NFR-07, NFR-08, NFR-09 |
| Technical design | AD-04, AD-05, AD-08; domain model and artifact contracts; package validity rules; runtime artifacts; run events |

## Tailored detailed-design decision

**Decision: required for M1.**

The technical design names the models and validity rules but does not define
their complete field constraints, state transitions, serialization envelope,
atomic-write behavior, or event-redaction contract. These details are shared
interfaces for every later milestone and must be settled before CLI and
CrewAI work begins.

### Contract design

All persisted and task-boundary objects are Pydantic models. Models should
reject empty identifiers, empty required text, duplicate IDs, invalid
references, and unsupported state values at the boundary.

The model groups are:

| Group | Models | Design responsibility |
| --- | --- | --- |
| Input | `ProjectContext`, clarification answer/status types | Preserve idea-owner input and explicit unknown, skipped, and deferred values |
| Discovery | `DiscoverySummary`, claim/provenance types, `ScopeProposal`, `Risk` | Preserve certainty labels and user-reviewable rationales |
| Planning | `ProductRequirement`, `UserStory`, `BacklogItem` | Enforce links, priorities, acceptance criteria, dependencies, and validation methods |
| Review | `ReviewDecision`, review-state types, quality findings | Prevent implicit acceptance and distinguish errors from warnings |
| Package | `DiscoveryPackage`, traceability entries, generation metadata | Provide one validated exportable contract |

The implementation may use nested models and enums, but the serialized shape
must remain readable and versionable. Model validation errors must identify the
field and invariant that failed.

### State transitions

```text
draft -> needs_review -> accepted
  |          |
  +--------> failed
  |
  +--------> stale (after material source correction)
```

`accepted` is only valid after explicit review decisions and successful
structural validation. A new generation creates a draft package and does not
overwrite the accepted package. `failed` records a causal failure and cannot
be exported as accepted.

### Identifier and version design

Use the documented prefixes:

- `CQ-001` clarification question;
- `RISK-001` risk;
- `REQ-001` requirement;
- `US-001` user story; and
- `BL-001` backlog item.

Allocation is deterministic within a project and preserves IDs for unchanged
items. The package version is a positive integer that increments for each
persisted package generation. M1 must not attempt semantic matching of
regenerated artifacts; it provides the allocation and reference primitives
needed by later orchestration.

### Persistence design

For project ID `my-idea`, persist:

```text
<projects-dir>/
└── my-idea/
    ├── state.json
    ├── package-v001.md
    └── run-events.jsonl
```

The state envelope contains the project ID, current package, package versions,
review decisions, and schema version. Package Markdown is stored as an opaque
rendered artifact for now; DP-06 owns rendering behavior.

Writes must:

1. validate the model before serialization;
2. write to a temporary sibling path;
3. flush and atomically replace the target where supported;
4. avoid leaving a target that looks complete after a failed write; and
5. surface storage errors as typed application errors.

Project IDs must resolve to a safe child directory under the configured
projects directory. Path traversal, empty IDs, and ambiguous path separators
must be rejected.

### Run-event design

Each JSONL event includes only:

- ISO timestamp;
- project ID;
- package version when known;
- stage and task name;
- outcome (`started`, `succeeded`, `failed`, or `skipped`);
- duration when complete; and
- safe error category/message when failed.

Events must exclude API keys, environment values, hidden model reasoning, and
unnecessary raw project content. Event writing failure must be visible to the
caller; it must not be silently swallowed.

## Planned implementation commits

The implementation branch is `feat/M1-contract-foundation`. It must contain
at least one independently valid implementation commit; the following
four-commit plan keeps contracts and persistence reviewable:

| Commit | Planned commit | Contents |
| --- | --- | --- |
| M1-C1 | `Define domain models and state enums` | Pydantic model groups, enums, schema/version metadata, and model unit tests |
| M1-C2 | `Add identifiers and package quality validation` | Stable ID allocation, traceability validation, invalid-package rules, and negative fixtures |
| M1-C3 | `Implement local project persistence` | Project store, state envelope, versioned artifacts, safe project paths, and atomic-write tests |
| M1-C4 | `Add redacted run-event persistence` | Structured JSONL events, redaction checks, failure behavior, and complete M1 validation |

If the implementation requires a different commit split, update this kickoff
before adding scope or merging the implementation branch.

## Acceptance criteria

1. Valid fixtures for project context, discovery, scope, risks, requirements,
   stories, backlog, review, and package models deserialize and round-trip.
2. Required fields, identifiers, states, priorities, certainty labels, and
   reference IDs are validated at model boundaries.
3. A story without a requirement or acceptance criteria is rejected.
4. A backlog item without a linked story, outcome, priority, dependency
   validity, or validation method is rejected.
5. Missing top-level artifacts, broken references, and unlabeled required
   claims are rejected.
6. Stable IDs follow the documented prefixes and are retained for unchanged
   items.
7. Two project IDs remain isolated and cannot overwrite one another.
8. Malformed state and failed writes produce explicit typed errors.
9. A later draft does not overwrite an accepted package or its version.
10. Run events are structured and redact secrets, environment values, and raw
    hidden reasoning.
11. The full M1 test suite runs without network access or provider credentials.
12. M1 introduces no CLI, CrewAI, or external-service dependency beyond the
    toolchain already merged in M0.

## Validation plan

| Check | Purpose | Provider credential |
| --- | --- | --- |
| Model round-trip tests | Verify valid serialization and deserialization | No |
| Negative model fixtures | Verify required-field and invariant failures | No |
| Traceability tests | Verify references and outcome-to-backlog coverage | No |
| State-transition tests | Verify draft, review, accepted, failed, and stale rules | No |
| Temporary-directory store tests | Verify isolation, round trips, and version retention | No |
| Atomic-write failure tests | Verify no false success after storage failure | No |
| Event-redaction tests | Verify secrets and raw sensitive content are excluded | No |
| `uv run pytest` | Verify the complete provider-free suite | No |
| Ruff and mypy commands | Verify formatting, lint, and type safety | No |

## Dependencies and risks

### Dependencies

- M0 kickoff and implementation PRs must be merged into `main`.
- M1 uses the settings and error types established in M0.
- DP-04, DP-05, DP-06, DP-07, DP-08, DP-09, and DP-10 depend on these
  contracts and persistence boundaries.

### Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Overly strict models block later legitimate outputs | Validate product invariants and required fields, not generated prose style |
| Model schema changes cause incompatible persisted state | Include a schema version and test the current serialized envelope |
| Atomic replacement differs across platforms | Isolate filesystem operations behind the store and test supported behavior |
| JSONL event content leaks project input | Use an allow-list event model and sentinel redaction tests |
| ID allocation is unstable after regeneration | Keep allocation deterministic and preserve IDs only through explicit source references |
| Persistence scope grows into a database design | Keep M1 local, single-process, and file-backed as approved |

## Branch and review workflow

1. Commit this kickoff on `docs/M1-kickoff`.
2. Open and merge the kickoff pull request into `main`.
3. Create `feat/M1-contract-foundation` from the updated `main`.
4. Implement the planned M1 commits and attach validation evidence to the
   implementation pull request.
5. Merge the implementation pull request only after the M1 exit criterion and
   acceptance criteria pass.
6. Update the delivery plan with M1 completion evidence before starting M2.

## Exit evidence

M1 is complete only when all of the following are available:

- merged M1 kickoff pull request;
- implementation pull request with at least one valid implementation commit;
- passing model, validation, persistence, state-transition, and event-redaction
  tests;
- passing provider-free pytest, Ruff, and mypy commands;
- evidence that invalid packages cannot be accepted or exported as accepted;
- evidence that accepted versions survive later draft persistence;
- evidence that no runtime artifact or secret is tracked; and
- implementation review confirming the M1 acceptance criteria.
