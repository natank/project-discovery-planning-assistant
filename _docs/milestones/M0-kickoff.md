# Milestone M0 — Toolchain Decision Kickoff

**Status:** Draft
**Milestone:** M0 — Toolchain decision
**Source:** [`04-delivery-plan.md`](../04-delivery-plan.md)
**Kickoff branch:** `docs/M0-kickoff`
**Implementation branch:** `feat/M0-toolchain`

## Objective

Establish a reproducible Python development toolchain and safe local
configuration boundary for the Project Discovery and Planning Assistant. At
the end of M0, a contributor should be able to create the documented
environment from a clean checkout, run the default test command without a
provider credential, and understand which versions and commands the later
milestones rely on.

## Expected outcome

The repository contains:

- a Python package and test layout matching the technical design;
- a declared and reproducible dependency set;
- safe environment-variable configuration with a non-secret example file;
- ignored local runtime and secret paths;
- documented formatting, linting/type-checking, and test commands; and
- a minimal test proving configuration behavior without calling a model
  provider.

## Scope

### In scope

- DP-01: establish the Python toolchain and safe local configuration;
- supported Python version selection;
- package and dependency-management convention;
- CrewAI version compatibility check;
- CLI, test, formatting, linting, and type-checking tool selection;
- typed settings boundary and secret redaction behavior;
- repository skeleton and developer documentation; and
- clean-checkout validation without an API key.

### Out of scope

- domain models and package contracts (DP-02);
- project persistence and run-event storage (DP-03);
- CLI commands beyond toolchain verification;
- CrewAI agents, tasks, crews, or live model execution;
- application behavior or user-facing discovery workflow;
- provider credentials, real `.env` files, or project runtime artifacts; and
- production deployment or hosted infrastructure.

## Linked requirements and design

| Source | Link |
| --- | --- |
| Delivery story | DP-01 |
| PRD backlog | B-01 foundation, B-16 foundation |
| Milestone exit criterion | The documented local environment and default test command work from a clean checkout without a provider credential. |
| Technical design decisions | AD-01 Python/CrewAI, AD-06 environment configuration |
| Technical-design sections | Proposed repository structure; configuration and local infrastructure; security and privacy boundaries |
| Relevant PRD qualities | NFR-03 reproducibility, NFR-06 privacy/configuration safety, NFR-08 testability |

## Tailored detailed-design decision

**Decision: required for M0.**

The approved technical design identifies the required dependency classes and
configuration behavior but intentionally leaves Python/package versions,
dependency-management convention, CLI library, formatter/linter, type checker,
and model factory details open. These choices affect every later milestone and
therefore require a focused M0 design rather than being selected ad hoc during
implementation.

### M0 toolchain design

| Concern | M0 decision | Reason |
| --- | --- | --- |
| Python | Python 3.11+; use the locally available supported minor version and document the minimum | Matches the approved design while retaining current typing and package support |
| Dependency management | `pyproject.toml` with `uv` and a committed `uv.lock` | Provides reproducible resolution and fast clean-checkout setup |
| Application package | `src/project_discovery_assistant/` | Prevents accidental imports from the repository root |
| CLI | Typer dependency reserved for the application command surface | Fits the documented command-oriented interaction without building the CLI in M0 |
| Test runner | pytest | Supports unit, contract, integration, and opt-in smoke test separation |
| Formatting | Ruff formatter | One fast, repository-local formatter |
| Linting | Ruff | Keeps baseline linting in one tool |
| Type checking | mypy | Makes the Pydantic and runner contracts explicit before implementation grows |
| Configuration | `pydantic-settings` loading environment and optional untracked `.env` | Typed settings and safe provider configuration |
| Initial model dependency | CrewAI plus its supported model integration dependencies | Verifies that the selected CrewAI release can support the planned sequential runner |
| Default test mode | No provider credential or network required | Preserves deterministic development and CI behavior |

The exact resolved versions belong in `pyproject.toml` and `uv.lock`. A real
provider key must not be required merely to install dependencies or run the
default test suite.

### Configuration contract

M0 establishes the names and safety rules, while later milestones implement
application-specific consumers:

```dotenv
OPENAI_API_KEY=
MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=
PDPA_PROJECTS_DIR=./projects
PDPA_LOG_LEVEL=INFO
```

The settings boundary must:

- load environment variables and an optional untracked `.env`;
- avoid logging or including secret values in error messages;
- leave provider credentials optional for non-provider commands and tests;
- validate local runtime paths when they are used; and
- keep `.env`, `projects/`, caches, and virtual environments out of version
  control.

M0 does not implement the model factory or invoke CrewAI. It only establishes
the dependency and configuration boundary they will use.

## Planned implementation commits

The implementation branch is `feat/M0-toolchain`. It must contain at least one
independently valid implementation commit; the following three-commit plan is
preferred:

| Commit | Planned commit | Contents |
| --- | --- | --- |
| M0-C1 | `Bootstrap Python toolchain and repository layout` | `pyproject.toml`, `uv.lock`, source/test package skeleton, ignore rules, and tool configuration |
| M0-C2 | `Add typed local configuration boundary` | `.env.example`, settings model, redaction behavior, and configuration tests |
| M0-C3 | `Document and validate developer setup` | README setup commands, default test command, clean-checkout verification, and directly related documentation |

If dependency resolution requires a separate corrective commit, keep it
focused and update this kickoff before changing the planned scope.

## Acceptance criteria

1. A clean checkout can install the declared dependencies with the documented
   command.
2. The repository uses the approved `src/` package and `tests/` layout.
3. The default test command completes without a provider credential or
   network access.
4. `.env.example` contains placeholders only and documents the required
   configuration names.
5. `.env`, `projects/`, virtual environments, caches, and other local runtime
   artifacts are ignored.
6. The settings boundary can load valid non-secret configuration.
7. Missing provider configuration produces an actionable, redacted message only
   when a provider-dependent command requests it.
8. No test, log, or error output exposes a credential value.
9. The selected CrewAI release installs successfully and is compatible with
   the planned sequential-process and typed-output adapter approach.
10. README instructions state the supported Python version, setup command,
    formatting/linting/type-checking commands, and default test command.

## Validation plan

Run these checks on the implementation branch and record their results in the
implementation pull request:

| Check | Purpose | Provider credential |
| --- | --- | --- |
| Clean environment setup | Proves reproducible dependency installation | No |
| `uv run pytest` | Proves default test path | No |
| `uv run ruff format --check .` | Proves formatting | No |
| `uv run ruff check .` | Proves lint baseline | No |
| `uv run mypy src` | Proves type-check baseline | No |
| Configuration unit tests | Proves loading, optional provider use, and redaction | No |
| CrewAI import/compatibility check | Proves selected dependency can be imported | No |

The clean-environment setup must use a temporary environment and must not
create committed or persistent project artifacts. If the selected toolchain
cannot run one command on a supported platform, the failure and replacement
command must be documented before the milestone is accepted.

## Dependencies and risks

### Dependencies

- M0 starts from the merged `main` containing the approved technical design.
- Later DP-02 through DP-08 depend on the package and configuration boundaries
  established here.
- Provider-dependent smoke execution is intentionally deferred to DP-08.

### Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| CrewAI dependency changes the supported Python range | Pin the resolved version, record the compatibility check, and keep the runner behind an adapter |
| Dependency installation requires network access in clean setup | Document network as an installation prerequisite; keep tests provider/network-free after installation |
| Tooling creates conflicting formatting or typing rules | Configure one canonical command per concern and validate it in the same clean environment |
| Configuration redaction is incomplete | Add tests with sentinel values and inspect captured output |
| Local artifacts are accidentally committed | Add ignore rules before runtime files and verify `git status` in validation |
| Provider configuration is forced too early | Load provider settings lazily for provider-dependent commands only |

## Branch and review workflow

1. This kickoff is committed on `docs/M0-kickoff`.
2. Open and merge the kickoff pull request into `main`.
3. Create `feat/M0-toolchain` from the updated `main`.
4. Implement M0 using the planned commits.
5. Run the validation plan and attach evidence to the implementation pull
   request.
6. Merge the implementation pull request only when the M0 exit criterion and
   all acceptance criteria pass.
7. Synchronize local `main` and record M0 as complete before creating the M1
   kickoff.

## Exit evidence

M0 is complete only when all of the following are available:

- merged kickoff pull request;
- implementation pull request with at least one valid implementation commit;
- reproducible clean-checkout setup result;
- passing default test, format, lint, and type-check results;
- passing configuration and CrewAI compatibility checks;
- confirmation that no secret or runtime artifact is tracked; and
- implementation review confirming the M0 acceptance criteria.
