# Project Discovery and Planning Assistant — Agentic System Design

**Status:** Draft
**Source:** [`02-product-requirements.md`](./02-product-requirements.md)
**Scope:** Initial demonstration release

## Reference documents

This design is produced by applying the design process defined in
[Agentic Systems and Workflows](./agentic-systems-and-workflows.md) to the
product requirements. That document defines the vocabulary used
throughout this one:

- the six objectives an agentic system must satisfy;
- the seven components (reasoning core, control loop, action executors,
  memory/state, validation/guardrails, termination logic, human interface)
  and the six relationships between them;
- the five-step, framework-agnostic design process (stages and sequence →
  reasoning-core configurations → capability contracts → control
  relationships → framework mapping) used as the structure for this
  document.

Once this design reaches its framework-mapping step, it draws on
[CrewAI-Based Agentic Systems](./crewai-based-agentic-systems.md) for how
CrewAI's primitives (`Agent`, `Task`, `Crew`, `Process`, `kickoff()`) map
onto the relationships defined in the base document, and which of those
relationships CrewAI absorbs versus which remain the application's
responsibility.

## Introduction

The previous technical design for this project (since removed; see
[pull request #15](https://github.com/natank/project-discovery-planning-assistant/pull/15))
committed to CrewAI as its first architecture decision, before working
through a framework-agnostic decomposition of the product requirements.
That made it difficult to see, after the fact, which control-loop
responsibilities the framework was actually absorbing and which had been
implemented by hand in application code — the two were established
together, in framework vocabulary, from the start.

This document restarts the design from
[`02-product-requirements.md`](./02-product-requirements.md) alone, which
explicitly defers "framework and agent topology," model provider, and other
implementation choices to technical design. The design process is applied
in order:

1. **Stages and sequence** — decompose the product requirements into
   discrete stages of reasoning work, and fix the order they run in,
   without naming a framework.
2. **Reasoning-core configurations** — for each stage, define the role,
   instructions, allowed tools, and output shape a reasoning core needs to
   perform it.
3. **Capability contracts** — specify the business logic behind every tool
   named in step 2: arguments, results, failure modes, retry safety, and
   whether it needs human approval.
4. **Control relationships** — for each stage, decide what it needs from
   memory, what validates its output, what counts as its success, failure,
   and exhausted outcomes, and whether it needs human sign-off.
5. **Framework mapping** — only at this point, choose a framework (CrewAI
   or otherwise) and record which of the six relationships it absorbs
   versus which remain application code.

Each step is worked through independently against the requirements, before
comparing the result to the removed technical design. The goal is a design
that can name, for every stage, exactly which component is responsible for
which of the six relationships — the gap identified when reviewing the
original technical design against this same process.

## Step 1 — Stages and sequence

A stage is a point where a distinct piece of reasoning must produce a
distinct output before later work can proceed (see the base document's
definition). Two categories of work in the product requirements are
deliberately excluded from the stage list on that basis:

- **Intake (FR-01)** is data capture, not reasoning — the idea owner's raw
  input is recorded as-is, with no interpretation required to produce it.
- **Traceability (FR-12) and export (FR-14)** are mechanical: traceability
  links artifacts already produced by earlier stages via their IDs, and
  export renders an already-validated package. Neither requires a
  reasoning-core call. Both are revisited in step 4 as memory/assembly
  concerns, not as stages here.
- **FR-13 (review/correction)** and **FR-15/FR-16 (incomplete input,
  execution visibility)** are cross-cutting: they describe the human
  interface and termination/validation behavior that wraps every stage,
  rather than a stage of their own. They are addressed in step 4.

What remains is four stages of reasoning work, each with one responsibility
and one output:

| Stage | Responsibility | Inputs | Output | Capabilities needed |
|---|---|---|---|---|
| S1: Assess clarification needs | Identify ambiguity, contradiction, or missing context material enough to affect discovery or scope; produce a bounded set of prioritized questions, or explicitly none. | The idea owner's raw input (idea, target user, outcome, constraints — any of which may be blank) | A bounded list of clarification questions (each with a reason it matters), or an explicit no-questions-needed result | None — reasons only from supplied input; no external lookup |
| S2: Frame the problem | Produce a coherent discovery summary: problem statement, target users, stakeholders, needs, outcomes, constraints — every claim labeled provided / inferred / assumption / open question. | Idea owner's input plus any answers, skips, or deferrals from S1 | A `DiscoverySummary`-shaped artifact with certainty labels on every material claim | None |
| S3: Propose scope and risks | Propose a focused MVP boundary (included capabilities, non-goals, trade-offs, follow-ons) and the material risks that boundary creates. | The discovery summary from S2 | A scope proposal plus a list of risks (each with impact, certainty, and a suggested validation/mitigation) | None |
| S4: Specify requirements, stories, and acceptance criteria | Derive testable, prioritized requirements from the scope, express them as user stories, and give each MVP story observable acceptance criteria — as one coherent, internally-consistent set. | Discovery summary, scope, and risks from S2/S3 | Requirements, user stories (linked to requirements), and acceptance criteria (linked to stories) | None |

None of the four stages requires a capability beyond reasoning over
supplied context — this follows directly from the non-goals in
`02-product-requirements.md` ("does not... execute irreversible actions in
external systems," no market research, no external validation). Step 3 of
this design will confirm whether this holds once tool needs are considered
more deliberately, but nothing in the requirements currently implies a
stage needs to look anything up, write anywhere, or call an external
service.

A fifth candidate — a dedicated backlog-generation stage for FR-11 — was
considered and folded into a decision below rather than left implicit.

**Why backlog generation (FR-11) is not listed as a fifth stage here:**
unlike requirements/stories/acceptance-criteria (bundled into S4 because a
story references a requirement and criteria belong to a story — one
reasoning call keeps them mutually consistent by construction), a backlog
item's defining relationship is to *already-finalized* stories and
requirements, and it introduces its own distinct concerns (dependency
ordering, a validation method, identifying a starting item) that are not
naturally checked by the same reasoning pass that produced S4's output.
Treating it as a separate stage — **S5: Plan delivery** — keeps its
dependency and sequencing logic separable and independently validated,
consistent with how bundling was judged case-by-case above rather than by
a blanket rule. It is included in the sequence below.

| Stage | Responsibility | Inputs | Output | Capabilities needed |
|---|---|---|---|---|
| S5: Plan delivery | Turn requirements and stories into a prioritized, dependency-aware backlog with a validation method per item and a reasonable starting point identified. | Requirements and stories from S4 | A backlog: item, outcome, linked story/requirement, priority, dependencies, validation method | None |

### Sequence

The dependency chain is linear: each stage's output is the next stage's
required input, with no requirement in the product spec implying a branch,
a parallel split, or a loop-back.

```
  Idea owner input
        |
        v
  +----------------------+
  | S1 Assess             |
  | clarification needs   |
  +----------------------+
        |
        v
  +----------------------+
  | S2 Frame the problem  |
  +----------------------+
        |
        v
  +----------------------+
  | S3 Propose scope      |
  | and risks             |
  +----------------------+
        |
        v
  +----------------------+
  | S4 Specify            |
  | requirements/stories/ |
  | acceptance criteria   |
  +----------------------+
        |
        v
  +----------------------+
  | S5 Plan delivery      |
  +----------------------+
        |
        v
  Discovery package (draft)
```

Per the base document's guidance ("a linear sequence is the easiest to
validate, test, and explain — use a richer shape only when a requirement
forces it"), nothing in `02-product-requirements.md` forces a richer shape:
there is no requirement for stages to run out of order, concurrently, or to
loop back into each other automatically. FR-13's correction/regeneration
behavior does re-enter this sequence, but as a human-triggered re-run
starting from whichever stage is affected, not as an automatic loop — that
is control-relationship (human interface and termination) design, deferred
to step 4.

### Open questions carried into later steps

- Whether S1 (clarification) should be able to run again mid-sequence
  (e.g., if S3 or S4 discovers new material ambiguity) or whether it only
  ever runs once, at the start — this is a termination/control question for
  step 4, not a sequencing question, since the requirements do not
  currently describe generation-time re-clarification as a first-class
  path (FR-03 describes the *initial* bounded question set).
- Whether S4's bundling (requirements + stories + acceptance criteria in
  one stage) remains viable once step 2 defines the reasoning-core
  configuration for it, or whether the combined responsibility is too large
  for one configuration to hold reliably — worth revisiting once step 2 is
  underway.

## Step 2 — Reasoning-core configurations

_Pending._

## Step 3 — Capability contracts

_Pending._

## Step 4 — Control relationships

_Pending._

## Step 5 — Framework mapping

_Pending._
