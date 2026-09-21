# Project Discovery and Planning Assistant — Delivery Plan

**Status:** Draft
**Source:** [`02-product-requirements.md`](./02-product-requirements.md) and
[`03-technical-design.md`](./03-technical-design.md)
**Scope:** Initial end-to-end demonstration release

## Current execution status

- **M0 — Toolchain decision:** Complete
- **M0 kickoff PR:** [#7](https://github.com/natank/project-discovery-planning-assistant/pull/7)
- **M0 implementation PR:** [#8](https://github.com/natank/project-discovery-planning-assistant/pull/8)
- **M0 implementation commits:** `d7ec815`, `6e59e12`, `99ef009`
- **M0 validation:** 6 provider-free tests passed; Ruff format/lint, mypy,
  CLI help, and CrewAI `Process.sequential` compatibility checks passed
- **M1 — Contract foundation:** Complete
- **M1 kickoff PR:** [#9](https://github.com/natank/project-discovery-planning-assistant/pull/9)
- **M1 implementation PR:** [#10](https://github.com/natank/project-discovery-planning-assistant/pull/10)
- **M1 implementation commits:** `94310ea`, `a6f8060`, `f2621a7`, `43e3ec5`
- **M1 validation:** 26 provider-free tests passed; Ruff format/lint and mypy
  passed; model, traceability, persistence, state-retention, and event-redaction
  checks passed
- **Next workflow:** M2 kickoff

## Delivery objective

Deliver a locally runnable CrewAI demonstration in which an idea owner creates
one project, supplies and clarifies a software idea, generates a structured
discovery package, reviews and accepts it, and exports a shareable Markdown
artifact.

The implementation sequence prioritizes a validated product contract and
deterministic test path before a live model-provider path. No story is complete
merely because an agent produces plausible prose: outputs must satisfy the
defined schemas, traceability rules, review boundary, and failure behavior.

## Scope and release boundary

### Release scope

The release implements PRD backlog items B-01 through B-16:

- P0: the complete, single-project discovery workflow (B-01 through B-12);
- P1: stage visibility, correction/regeneration, quality checks, and
  deterministic fixtures (B-13 through B-16).

### Deferred scope

B-17 through B-20 remain after the demonstration release: alternate artifact
formats, project revision-history UX, optional domain context, and external
delivery-tool integration. The larger technical-design deferrals also remain
out of scope, including a web interface, authentication, database persistence,
search tools, and hosted deployment.

## Delivery principles

- **Build the contract first:** Pydantic models, IDs, validation, and
  persistence precede agent prompts.
- **Keep a deterministic path:** all automated tests use a fake crew that
  conforms to the same adapter contract as the real CrewAI runner.
- **Make the human boundary enforceable:** only an explicit idea-owner
  acceptance action marks a package accepted.
- **Fail truthfully:** configuration, provider, schema, storage, and quality
  failures are distinct, persisted where possible, and return non-zero CLI
  status.
- **Integrate in small vertical slices:** every implementation phase ends with
  executable behavior, not only foundational code.
- **Protect project content:** fixtures are synthetic; secrets and runtime
  artifacts are never committed.

## Milestones

| Milestone | Outcome | Completion evidence |
| --- | --- | --- |
| M0: Toolchain decision | Supported Python/CrewAI configuration and developer commands are known. | Locked dependency set and documented local setup pass in a clean environment. |
| M1: Contract foundation | Projects, artifact schemas, validation, and local storage work without a model provider. | Unit tests prove ID, state, persistence, and invalid-package behavior. |
| M2: Deterministic vertical slice | A fake crew produces a complete draft package from synthetic input. | CLI integration test produces a validated package and Markdown export. |
| M3: CrewAI integration | Sequential CrewAI roles and typed handoffs implement the same runner contract. | Opt-in smoke run with a configured provider produces a reviewable draft. |
| M4: Reviewable release | Correction, regeneration, review, acceptance, export, status, and failure paths are complete. | All required tests pass; an accepted package meets the PRD acceptance baseline. |

## Milestone-to-story control matrix

Use this matrix to control implementation progress. A milestone is complete
only when every required story is complete and its listed completion evidence
has been reviewed. A later milestone must not be declared complete based on
plausible generated output alone.

| Milestone | Required stories | Exit criterion |
| --- | --- | --- |
| M0: Toolchain decision | DP-01 | Complete — documented local environment and default test command work from a clean checkout without a provider credential; evidence recorded above. |
| M1: Contract foundation | DP-02, DP-03 | Complete — validated contracts, local persistence, IDs, events, and invalid-package handling pass provider-free tests; evidence recorded above. |
| M2: Deterministic vertical slice | DP-04, DP-05, DP-06, DP-07 | The CLI creates and clarifies a project, then produces a validated draft Markdown package with the fake crew and no API key. |
| M3: CrewAI integration | DP-08 | The real sequential CrewAI runner passes the shared adapter contract tests and an opt-in, non-sensitive provider smoke run yields a reviewable draft. |
| M4: Reviewable release | DP-09, DP-10, DP-11, DP-12 | Correction, acceptance, export, stage visibility, failure handling, and release validation meet the PRD acceptance baseline. |

DP-11 may begin after DP-04 because its failure and status behavior applies to
the CLI and project store; it remains required for M4. DP-12 may add fixtures
as individual paths are delivered, but its release-certification work cannot
complete until DP-07 through DP-11 are complete.

## Milestone execution workflow

Every milestone is delivered as an independent workflow. The milestone
control matrix is updated only after that workflow completes its implementation
and review gates.

### Phase 1: Create and approve the milestone kickoff

Create a dedicated branch named `docs/M[x]-kickoff`, where `M[x]` is the
milestone identifier, for example `docs/M0-kickoff`. The kickoff document must
be committed on that branch and submitted as a separate pull request.

The kickoff document must contain:

- milestone objective and expected outcome;
- in-scope and out-of-scope work;
- linked delivery stories, PRD requirements, and technical-design decisions;
- dependencies, assumptions, risks, and open questions;
- a decision on whether milestone-specific detailed design is needed;
- the tailored detailed design when the existing technical design is
  insufficient;
- milestone-level acceptance criteria and validation plan;
- planned implementation branch name;
- planned commits, with at least one implementation commit; and
- milestone exit evidence required by the control matrix.

If no additional detailed design is needed, the kickoff must state why the
approved technical design is sufficient. If implementation reveals that the
planned design or commit sequence must change, update the kickoff document
before expanding scope.

The kickoff pull request must be reviewed and merged before the implementation
branch is created.

### Phase 2: Implement the milestone

After kickoff approval, create the milestone implementation branch using the
branch name recorded in the kickoff, for example
`feat/M0-toolchain`. All implementation commits for that milestone belong on
this branch.

The implementation branch must:

- contain at least one independently valid implementation commit;
- remain within the approved kickoff scope;
- update the kickoff when design, scope, or planned commits materially change;
- include tests and directly related documentation;
- preserve the repository's configuration and secret-safety rules; and
- produce the validation evidence specified by the kickoff.

The implementation branch is submitted as a separate pull request. It must
not be merged until the milestone acceptance criteria and validation evidence
are reviewed.

### Phase 3: Complete and record the milestone

The milestone implementation pull request is merged into `main` only after
review confirms that:

1. all planned implementation commits are present;
2. the milestone acceptance criteria pass;
3. the control-matrix exit criterion is satisfied;
4. failures and unresolved limitations are explicitly documented; and
5. the repository is synchronized with `main` after merge.

Only then may the milestone be marked complete in project tracking. The next
milestone kickoff may start from the updated `main`, not from an unmerged
implementation branch.

### Standard branch and pull-request sequence

For milestone `M[x]`, use this sequence:

```text
docs/M[x]-kickoff
  -> kickoff pull request
  -> merge to main
      -> feat/M[x]-<short-name>
          -> implementation commits
          -> implementation pull request
          -> merge to main
              -> update milestone status and begin next kickoff
```

The kickoff and implementation pull requests are separate review units. A
milestone cannot be completed by merging only its kickoff documentation.

## Story map and sequencing

```text
DP-01 Toolchain and project skeleton
  -> DP-02 Domain contracts and quality validation
      -> DP-03 Local project store and run events
          -> DP-04 CLI intake and project creation
              -> DP-05 Runner adapter and deterministic fake crew
                  -> DP-06 Package assembly, rendering, and traceability
                      -> DP-07 End-to-end deterministic draft workflow
                          -> DP-08 CrewAI agents, tasks, and sequential runner
                              -> DP-09 Review, correction, and regeneration
                                  -> DP-10 Acceptance and shareable export
                          -> DP-11 Failure handling and stage visibility
                      -> DP-12 Evaluation fixtures and release validation
```

DP-11 can begin after DP-04 and must complete before M4. DP-12 begins as soon
as the corresponding automated paths exist, but its final release check
depends on DP-07 through DP-11.

## Implementation stories

### DP-01: Establish the Python toolchain and safe local configuration

**Backlog coverage:** B-01 (foundation), B-16 (foundation)
**Milestone:** M0
**Dependencies:** None

Create the executable project skeleton and resolve the technical-design open
questions that affect every later story: supported Python and CrewAI versions,
dependency-management convention, CLI library, formatter/linter, type checker,
and default model configuration.

**Implementation work:**

- create `pyproject.toml`, package source layout, and test layout;
- add a lock file if selected by the package manager;
- create `.gitignore` for `.env`, `projects/`, virtual environments, and test
  caches;
- create `.env.example` with placeholders only;
- implement typed settings that load environment values, redact secret values,
  and fail fast for missing required configuration when invoking a real runner;
- establish one command each for formatting, linting/type checking, and tests;
- document setup and commands in `README.md`.

**Acceptance criteria:**

- A clean checkout can create the documented environment and run the test
  command without a provider credential.
- The repository contains no credential, local project artifact, or runtime
  `.env` file.
- Invalid configuration reports a redacted, actionable error.
- The selected CrewAI version supports the planned sequential process and the
  adapter approach for structured task output.

**Validation:** clean-environment setup check; configuration unit tests;
formatter, linter/type-checker, and test commands run successfully.

**Definition of done:** setup documentation, manifests, ignore rules, and
configuration tests are committed; the selected versions and unresolved
provider constraints are documented.

---

### DP-02: Define domain contracts, identifiers, and package-quality rules

**Backlog coverage:** B-01, B-05, B-09, B-15
**Milestone:** M1
**Dependencies:** DP-01

Implement the Pydantic models that make project input, task handoffs,
traceability, review state, and exported package structure explicit.

**Implementation work:**

- define the models in the technical design: project context, clarification
  question, discovery summary, scope, risk, requirement, story, backlog item,
  review decision, package, and quality report;
- implement certainty labels, package and artifact states, source references,
  version fields, and stable ID allocation;
- implement structural validation and traceability validation;
- model quality findings as `error`, `warning`, and `note`;
- ensure invalid packages may be retained only as diagnostic drafts and cannot
  be accepted.

**Acceptance criteria:**

- Valid package fixtures deserialize and reserialize without loss of required
  data.
- Broken references, a story without a requirement or acceptance criteria, a
  backlog item without required delivery fields, and required claims without
  certainty fail validation.
- Quality findings are distinct from hard structural failures.
- Generated identifiers follow the documented prefixes and remain stable for
  unchanged items.

**Validation:** unit tests for each model and validator; negative fixtures for
every invalid-package rule.

**Definition of done:** domain contract API is documented in code, fully
unit-tested, and used as the only input/output type for subsequent stories.

---

### DP-03: Build local project persistence and redacted run events

**Backlog coverage:** B-01, B-10, B-12, B-13
**Milestone:** M1
**Dependencies:** DP-02

Implement the local project store for machine-readable state, versioned
Markdown packages, review decisions, and redacted stage events.

**Implementation work:**

- create and load isolated project directories using validated project IDs;
- write `state.json`, package versions, and `run-events.jsonl` using atomic
  replacement where available;
- validate JSON after reading and before writing;
- record structured start, success, failure, and skipped events;
- ensure event records exclude environment values, secrets, and hidden model
  reasoning;
- report storage failures explicitly rather than leaving partial success state.

**Acceptance criteria:**

- Two project IDs cannot overwrite one another.
- Stored packages and state can be reloaded as validated models.
- An accepted package is retained when a subsequent draft is generated.
- Simulated write or malformed-state failures yield a specific error and no
  falsely successful package state.
- Run events contain stage, duration, outcome, and safe error metadata only.

**Validation:** temporary-directory unit tests for round trips, atomic-write
failure behavior, state corruption, and event redaction.

**Definition of done:** the store is the only runtime artifact writer and all
file-system tests pass on the supported local platform.

---

### DP-04: Implement CLI intake, clarification answers, and project commands

**Backlog coverage:** B-01, B-02, B-03, B-11, B-13
**Milestone:** M2
**Dependencies:** DP-02, DP-03

Implement the local interface for starting a project and recording idea-owner
input before agent generation.

**Implementation work:**

- implement `new` to capture an idea plus optional target user, desired
  outcome, and constraints;
- implement project selection and validated project-ID creation;
- implement `clarify` to show questions, record answers, skips, and deferrals;
- show project status and one clear next action after each command;
- validate inputs before state changes and report missing or conflicting input
  in plain language;
- retain optional blank fields as unknown rather than manufactured values.

**Acceptance criteria:**

- An idea owner can create one project and see submitted input for correction.
- Optional context can be omitted; it remains visibly unknown.
- An answer can be recorded, skipped, or deferred without losing the question
  or its rationale.
- Invalid arguments and unknown project IDs return a non-zero exit status with
  an actionable message.
- Commands do not require a provider credential until a real CrewAI run is
  requested.

**Validation:** CLI integration tests with isolated project directories and
non-interactive input fixtures.

**Definition of done:** a contributor can create and update a project entirely
through the CLI, and project state persists across command invocations.

---

### DP-05: Introduce the runner adapter and deterministic fake crew

**Backlog coverage:** B-03, B-04, B-06, B-07, B-08, B-16
**Milestone:** M2
**Dependencies:** DP-02, DP-03

Define one runner interface for generation and implement a deterministic fake
that returns schema-valid fixtures. This is the test seam between product
logic and CrewAI.

**Implementation work:**

- define the runner protocol for clarification, framing, scope/risk,
  requirements/stories, backlog, and quality outputs;
- create a deterministic fake runner using synthetic fixture data;
- validate every runner result through the domain models before use;
- model zero questions and the explicit “no questions needed” result;
- allow test fixtures to produce malformed, incomplete, and failed responses.

**Acceptance criteria:**

- Product services do not import CrewAI directly; they depend on the runner
  protocol.
- The fake runner can create a complete package for a known minimal idea.
- An invalid fake response is rejected at the task boundary and downstream
  work does not run.
- Tests can simulate each workflow stage failing without a live provider.

**Validation:** contract tests shared by fake and future real runner adapters;
unit tests for schema-boundary failure.

**Definition of done:** the deterministic runner supports all M2 tests and
defines the complete adapter contract that DP-08 must honor.

---

### DP-06: Assemble, validate, and render discovery packages

**Backlog coverage:** B-04 through B-09, B-12, B-15
**Milestone:** M2
**Dependencies:** DP-02, DP-03, DP-05

Implement package assembly and Markdown rendering from validated artifacts,
including readable traceability for delivery collaborators and reviewers.

**Implementation work:**

- assemble task outputs into `DiscoveryPackage`;
- allocate and preserve stable IDs, build source references, and generate the
  outcome-to-backlog traceability matrix;
- invoke structural validation and record quality findings;
- render accessible Markdown with metadata, input/evidence, discovery
  summary, certainty labels, risks, scope, requirements, stories, criteria,
  backlog, review status, and traceability;
- ensure output contains no secrets, environment configuration, raw provider
  response, or hidden reasoning.

**Acceptance criteria:**

- A valid fixture package renders every section required by FR-14.
- A delivery collaborator can navigate from a backlog item to linked stories,
  requirements, and acceptance criteria using IDs in the Markdown package.
- Inferred claims, assumptions, and open questions are visibly distinct from
  provided input.
- The renderer rejects or marks invalid packages rather than emitting an
  accepted-looking document.

**Validation:** renderer snapshot tests; traceability traversal test;
secret-exclusion test; invalid-package rendering test.

**Definition of done:** the renderer produces a portable, readable draft
package from a validated fixture and writes it through the project store.

---

### DP-07: Deliver the deterministic end-to-end draft workflow

**Backlog coverage:** B-01 through B-12
**Milestone:** M2
**Dependencies:** DP-04, DP-05, DP-06

Wire the CLI, project store, runner adapter, package assembler, and renderer
into a complete draft-generation command using the deterministic fake crew.

**Implementation work:**

- implement `generate` orchestration in the documented sequence;
- persist stage transitions and run events;
- prevent downstream execution when a required upstream stage fails;
- write the draft package and surface its location, status, and next action;
- display unresolved items and quality findings as part of the result.

**Acceptance criteria:**

- Starting with a synthetic idea, a contributor can run the full draft
  workflow without an API key.
- The result contains all sections in the PRD initial acceptance baseline.
- The package is `draft` or `needs_review`, never accepted automatically.
- A failed fake stage results in explicit failure status, a non-zero exit, and
  no success-shaped export.

**Validation:** end-to-end CLI integration test plus negative tests for
invalid input, failed stage, and invalid task output.

**Definition of done:** M2 is met and the project demonstrates the whole
product contract deterministically before real-provider integration begins.

---

### DP-08: Implement the sequential CrewAI runner

**Backlog coverage:** B-03 through B-08, B-13
**Milestone:** M3
**Dependencies:** DP-01, DP-05, DP-07

Implement the real CrewAI adapter that satisfies the runner contract and maps
the technical design’s six agent roles and ordered tasks to CrewAI.

**Implementation work:**

- create CrewAI agent definitions for clarification, discovery, scope, product
  requirements, delivery planning, and quality review;
- create sequential tasks with schemas, certainty-label instructions, and
  explicit restrictions against invented evidence, external actions, and
  hidden reasoning;
- configure model creation through the settings layer;
- translate CrewAI results to domain models at every handoff;
- add narrow retry behavior only for documented transient provider failures;
- record safe stage events and return typed failures for provider, task, or
  schema errors.

**Acceptance criteria:**

- The real runner conforms to every contract test used by the fake runner.
- Task output is schema-validated before it is consumed by the next stage.
- A configuration, provider, or schema failure stops the affected workflow and
  gives a safe, actionable error.
- An opt-in run using a configured, non-sensitive fixture produces a package
  requiring human review.
- The runner has no search, external write, or unrestricted tool capability.

**Validation:** mocked CrewAI adapter tests; one opt-in smoke test excluded
from the default suite; manual inspection of the smoke package and redacted
event log.

**Definition of done:** M3 is met, the default suite remains credential-free,
and the real runner has a documented opt-in smoke command.

---

### DP-09: Add review decisions, correction, and full downstream regeneration

**Backlog coverage:** B-10, B-14
**Milestone:** M4
**Dependencies:** DP-04, DP-06, DP-07

Implement the idea-owner review boundary, correction path, stale-state model,
and replacement draft generation.

**Implementation work:**

- implement `review` to display artifacts, findings, assumptions, risks, open
  questions, and pending decisions;
- allow correction of source context and recording acceptance, rejection, or
  deferral decisions;
- identify dependent downstream artifacts as stale after a material change;
- regenerate the complete downstream draft on the next `generate`;
- retain the prior accepted package and its version until replacement
  acceptance.

**Acceptance criteria:**

- The idea owner can correct input and see the affected draft marked stale.
- Regeneration produces a new version without overwriting the accepted
  version.
- Unaffected accepted decisions are retained or explicitly identified for
  reconfirmation.
- The review surface shows unresolved assumptions and open questions.
- No correction silently marks generated content approved.

**Validation:** CLI integration tests for correction, stale state, retained
version, regenerated package, and decision persistence.

**Definition of done:** review and correction behavior meets FR-13 and all
state transitions are covered by automated tests.

---

### DP-10: Enforce explicit acceptance and accepted-package export

**Backlog coverage:** B-10, B-12
**Milestone:** M4
**Dependencies:** DP-06, DP-07, DP-09

Implement the acceptance gate and export behavior for the reviewed package.

**Implementation work:**

- implement `accept` with explicit confirmation;
- block acceptance for structural errors, failed mandatory stages, or invalid
  package state;
- preserve visible warnings, assumptions, and open questions after acceptance;
- implement `export` for the current accepted package and clear messaging when
  no accepted package exists;
- include package version, generation status, and review status in the export.

**Acceptance criteria:**

- A draft cannot be represented as accepted without an explicit idea-owner
  action.
- A structurally invalid or failed package cannot be accepted or exported as
  accepted.
- The accepted Markdown package contains all required sections, visible
  uncertainty, and traceability.
- Export does not include credentials, environment values, or hidden
  reasoning.

**Validation:** acceptance state-transition tests; export snapshot and
secret-exclusion tests; CLI negative-path tests.

**Definition of done:** a delivery collaborator can receive the accepted
Markdown package and independently follow every traceability reference.

---

### DP-11: Complete stage visibility, safe failures, and retry behavior

**Backlog coverage:** B-11, B-13, B-15
**Milestone:** M4
**Dependencies:** DP-03, DP-04, DP-07, DP-08

Harden the operational path so progress is visible, errors are actionable, and
transient failures can be distinguished from permanent failures.

**Implementation work:**

- expose stage start, success, failure, and skipped state in CLI output and
  persisted events;
- define typed application errors for input, configuration, provider, task,
  schema, quality, and storage failures;
- implement bounded retries only for recognized transient provider/network
  failures and record each attempt;
- preserve a diagnostic draft only when it is valid enough to inspect, but
  never claim it is complete;
- standardize non-zero exit codes and safe next-action messages.

**Acceptance criteria:**

- The idea owner can determine the last completed stage and next action after
  every command.
- Missing configuration, provider failure, schema failure, quality finding,
  and storage failure produce distinguishable messages and states.
- Persistent failure is not hidden by unbounded retries or a success-shaped
  package.
- Logs and CLI errors contain no credentials or raw environment values.

**Validation:** unit and integration tests for each failure taxonomy row,
retry-boundary tests, and log-redaction tests.

**Definition of done:** failure behavior satisfies NFR-05 through NFR-07 and
the required negative scenarios pass in the default suite.

---

### DP-12: Establish evaluation fixtures and certify the release

**Backlog coverage:** B-15, B-16
**Milestone:** M4
**Dependencies:** DP-07, DP-08, DP-09, DP-10, DP-11

Create the maintained evaluation set and perform the release-level validation
against the PRD acceptance baseline.

**Implementation work:**

- add synthetic fixtures for minimal, ambiguous, deferred-answer, conflicting,
  and correction scenarios;
- add package-quality assertions for completeness, coherence markers,
  actionability, traceability, transparency, scope discipline, and
  reviewability;
- run the default deterministic suite from a clean environment;
- run one opt-in non-sensitive real-provider smoke scenario;
- document known limitations, provider cost/quality observations, and
  reproducible demonstration steps;
- prepare the final README operating instructions and a lessons-learned
  template for post-implementation findings.

**Acceptance criteria:**

- Every required validation scenario in the technical design has an automated
  deterministic test or an explicitly documented manual smoke check.
- The default suite runs without network access or provider credentials.
- The smoke package is reviewed against the PRD initial acceptance baseline.
- Any known limitation is visible in documentation rather than hidden by a
  passing happy path.

**Validation:** full default test suite, lint/type-check, clean-checkout
setup check, opt-in smoke test, and manual package review.

**Definition of done:** M4 completion evidence is recorded, the demonstration
is reproducible from a clean checkout, and the release is ready for a
post-implementation lessons-learned document.

## Dependency and parallelization rules

Most stories must remain sequential because the product contract is the
interface between them. Safe parallel work is limited to:

| Work | May begin after | Constraint |
| --- | --- | --- |
| Test fixture authoring for models | DP-02 | Fixtures must track the finalized model contracts. |
| CLI command UX tests | DP-04 | Must use temporary project stores and fake runner only. |
| Renderer snapshots | DP-06 | Must not define a second artifact schema. |
| CrewAI prompt/task drafts | DP-05 | Must conform to the runner protocol and final schema validation. |
| Failure-path tests | DP-03 | Must use typed error contract, not ad hoc exception strings. |

No implementation story may bypass DP-02’s contract or write runtime state
outside the project store.

## Cross-story definition of done

Every implementation story must:

1. map to the listed PRD backlog items and functional requirements;
2. add or update automated tests at the appropriate level;
3. pass formatter, linter/type checking, and relevant tests;
4. keep secrets, `.env`, `projects/`, and sensitive fixtures out of version
   control;
5. surface errors explicitly with a safe next action;
6. preserve typed artifact boundaries and traceability;
7. update directly affected documentation; and
8. leave `main` runnable through the documented commands when merged.

## Release acceptance checklist

The initial demonstration is ready when:

- [ ] M0 through M4 completion evidence exists.
- [ ] The default deterministic suite passes without a credential or network.
- [ ] An opt-in real-provider smoke run has completed with non-sensitive
  fixture input.
- [ ] The result contains every item in the PRD initial acceptance baseline.
- [ ] An idea owner can create, clarify, generate, review, correct, accept,
  and export one project.
- [ ] A delivery collaborator can inspect Markdown traceability from outcome
  through backlog item without using the CLI.
- [ ] The reviewer can distinguish provided facts, inferences, assumptions,
  open questions, risks, and acceptance status.
- [ ] Invalid, incomplete, and failed runs are visibly non-successful.
- [ ] Configuration, logs, events, and exports contain no secrets.
- [ ] The README documents setup, commands, limitations, and the opt-in smoke
  workflow.

## Implementation order

Implement and merge stories in this order:

1. DP-01 — toolchain and safe configuration
2. DP-02 — contracts and quality validation
3. DP-03 — project persistence and events
4. DP-04 — CLI intake and clarification
5. DP-05 — runner adapter and deterministic fake crew
6. DP-06 — package assembly and rendering
7. DP-07 — deterministic end-to-end draft workflow
8. DP-08 — sequential CrewAI runner
9. DP-09 — review, correction, and regeneration
10. DP-10 — acceptance and export
11. DP-11 — operational hardening
12. DP-12 — evaluation and release certification

DP-12 closes the implementation phase. Findings from real execution and
evaluation are captured next in `_docs/05-lessons-learned.md`.
