# M3 CrewAI Provider Smoke Test

**Status:** Ready for execution  
**Milestone:** M3 — CrewAI integration  
**Implementation:** `feat/M3-crewai-runner`  
**Purpose:** Validate one real-provider CrewAI generation without weakening the
provider-free default test suite.

## 1. Objective

This smoke test verifies that the real sequential CrewAI runner can take a
synthetic project context through the complete discovery workflow and produce a
reviewable Markdown draft with:

- six ordered CrewAI stages;
- typed, schema-valid handoffs;
- visible uncertainty and quality status;
- stable artifact IDs and traceability;
- persisted stage events; and
- no credentials, raw provider responses, or hidden reasoning in exported
  artifacts.

The smoke test is an opt-in operational check. It may call the configured model
provider and may incur provider charges.

## 2. Scope and non-goals

### In scope

- local configuration loading;
- real CrewAI model and agent construction;
- sequential task execution;
- task-output conversion to domain models;
- package assembly and Markdown rendering;
- persisted state and run-event inspection; and
- safe failure behavior when configuration or provider execution fails.

### Out of scope

- acceptance of the generated package;
- correction or regeneration workflows;
- production data;
- performance benchmarking;
- provider cost optimization; and
- proving semantic correctness beyond the documented review checklist.

## 3. Safety requirements

Before running:

1. Use synthetic project input only.
2. Never paste credentials, private source code, customer data, or secrets into
   the project context.
3. Confirm `.env` is untracked and `projects/` is ignored by Git.
4. Use the intended provider, model, and billing account.
5. Do not commit generated project artifacts.

The smoke command does not print the API key. The runner and event persistence
must not write credentials, raw provider responses, prompts, or hidden
reasoning to the Markdown package or `run-events.jsonl`.

## 4. Prerequisites

From the repository root:

```bash
uv sync --dev
```

Configure the provider in the shell or an untracked `.env` file:

```dotenv
OPENAI_API_KEY=replace-with-a-valid-key
MODEL_NAME=gpt-4o-mini
# Optional:
# OPENAI_BASE_URL=https://api.openai.com/v1
# PDPA_PROJECTS_DIR=./projects
# PDPA_LOG_LEVEL=INFO
```

Verify configuration without displaying the secret:

```bash
uv run python -c \
  "from project_discovery_assistant.config import Settings; print(Settings().model_name)"
```

Expected output is the configured model name, for example:

```text
gpt-4o-mini
```

Do not use `echo $OPENAI_API_KEY` or include the key in command output,
screenshots, logs, or evidence.

## 5. Provider-free preflight

Run the default checks before spending provider credits:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

The suite must pass without requiring the smoke test or a live provider.

## 6. Create the synthetic project

Choose a lowercase project ID. The ID is a local directory identifier, not an
API or provider identifier. This runbook uses `m3-smoke-demo`.

```bash
uv run pdpa new \
  --project-id m3-smoke-demo \
  --idea "Create a local assistant that turns a software idea into a reviewable discovery and delivery plan." \
  --target-user "Idea owner" \
  --desired-outcome "A structured package ready for human review" \
  --constraint "Local-first operation"
```

Expected output includes:

```text
Created project 'm3-smoke-demo'.
```

Confirm the project state exists:

```bash
test -f projects/m3-smoke-demo/state.json
```

## 7. Execute the real-provider smoke run

Run:

```bash
uv run python scripts/smoke_crewai.py m3-smoke-demo
```

Expected output has this shape:

```text
CrewAI smoke run produced package v001 with status 'draft'.
Package: .../projects/m3-smoke-demo/package-v001.md
Review the package and run-events.jsonl for secret-free output.
```

The exact package status may be `draft` or `needs_review`, depending on the
quality findings returned by the provider. Neither status represents
acceptance.

## 8. Inspect generated artifacts

The smoke run should create:

```text
projects/m3-smoke-demo/
├── state.json
├── package-v001.md
└── run-events.jsonl
```

Inspect the package:

```bash
less projects/m3-smoke-demo/package-v001.md
```

Inspect event fields without exposing the full contents:

```bash
uv run python - <<'PY'
import json
from pathlib import Path

path = Path("projects/m3-smoke-demo/run-events.jsonl")
for line in path.read_text(encoding="utf-8").splitlines():
    event = json.loads(line)
    print(event["stage"], event["task_name"], event["outcome"])
PY
```

Expected stages are:

```text
clarification
discovery
scope
requirements
planning
quality
package
```

Each successful stage should have a corresponding `succeeded` event. A
provider or task failure should instead produce a visible `failed` event and a
non-zero command result.

## 9. Manual package review checklist

Record each result as **Pass**, **Fail**, or **Not applicable**.

### Workflow and status

- [ ] Package metadata identifies the project and version.
- [ ] Generation status is visible and is not represented as accepted.
- [ ] Quality findings, assumptions, and open questions are visible.
- [ ] The package is readable without access to CrewAI or provider logs.

### Structured content

- [ ] Discovery summary contains a problem statement, target users, needs, and
      outcomes.
- [ ] Scope includes MVP capabilities, non-goals, follow-ons, and trade-offs.
- [ ] Risks include certainty and mitigation information.
- [ ] Requirements have stable `REQ-` identifiers.
- [ ] Stories have stable `US-` identifiers and acceptance criteria.
- [ ] Backlog items have stable `BL-` identifiers and validation methods.

### Traceability

- [ ] Every story references at least one requirement.
- [ ] Every backlog item references at least one story.
- [ ] The traceability section is present and navigable.
- [ ] Outcome-to-requirement-to-story-to-backlog links are coherent.

### Safety and provenance

- [ ] Provided, inferred, assumption, and open-question certainty labels are
      used appropriately.
- [ ] No API key or secret appears in the package.
- [ ] No environment values appear in the package.
- [ ] No raw provider response, prompt, or hidden reasoning appears in the
      package.
- [ ] The event log contains only allow-listed safe metadata and diagnostics.
- [ ] No external action or uncontrolled tool use is evidenced.

## 10. Failure handling

### Missing provider configuration

Expected behavior:

- the command exits non-zero;
- the error names the required configuration without revealing a value; and
- no success-shaped package is produced.

Test safely by using a separate shell with the key removed:

```bash
env -u OPENAI_API_KEY uv run python scripts/smoke_crewai.py m3-smoke-demo
```

### Provider or network failure

Expected behavior:

- the affected stage is identified;
- the command exits non-zero;
- a failed event is persisted when storage remains available; and
- no accepted or success-shaped package is claimed.

Do not intentionally induce provider failures against production data.

### Invalid structured output

This path is covered by provider-free adapter tests and must stop downstream
execution before malformed output is assembled or persisted as a valid package.

## 11. Cleanup

Generated project artifacts are ignored by Git. Remove the synthetic smoke
project after capturing evidence:

```bash
rm -rf projects/m3-smoke-demo
```

Only remove this explicitly named synthetic project directory. Do not delete
the entire `projects/` root if it contains other work.

Confirm no tracked files changed:

```bash
git status --short
```

## 12. Evidence record

Complete this section after execution.

| Field | Result |
| --- | --- |
| Date/time | |
| Branch or commit | |
| Project ID | `m3-smoke-demo` |
| Provider/model | |
| Package version | |
| Package status | |
| Command result | Pass / Fail |
| Default test suite | |
| Ruff | |
| mypy | |
| Manual package review | Pass / Fail |
| Event-log safety review | Pass / Fail |
| Cleanup completed | Yes / No |

### Findings and follow-up

Document any provider errors, schema corrections, quality findings, cost
observations, or implementation changes discovered during the run. A passing
smoke run does not close M3 until the implementation review and all kickoff
exit evidence are complete.
