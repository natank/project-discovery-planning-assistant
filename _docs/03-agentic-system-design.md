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
definition). Three categories of work in the product requirements are
deliberately excluded from the stage list on that basis:

- **Intake (FR-01)** is data capture, not reasoning — the idea owner's raw
  input is recorded as-is, with no interpretation required to produce it.
- **Traceability (FR-12) and export (FR-14)** are mostly mechanical:
  traceability links artifacts already produced by earlier stages via their
  IDs, and export renders an already-validated package. Neither requires a
  reasoning-core call to perform the linking or rendering itself. This is
  not a complete exemption, though: FR-12 requires assigning stable IDs and
  marking references that are "missing or uncertain" rather than silently
  omitting them, and both of those are decisions each stage's own output
  format has to support (carried into step 2's output-shape design), not
  something traceability can add after the fact. Both remain memory/assembly
  concerns in step 4, not stages here.
- **FR-13 (review/correction)** and **FR-15/FR-16 (incomplete input,
  execution visibility)** are cross-cutting: they describe the human
  interface and termination/validation behavior that wraps every stage,
  rather than a stage of their own. They are addressed in step 4. One
  exception is carried forward rather than fully deferred: FR-15's
  requirement to detect input "outside the product boundary" (for example,
  input that is not a software idea at all) is reasoning work, not a
  validation rule that can be bolted on afterward, and no stage above
  performs it. It is assigned to S1 below, since S1 is already the stage
  that inspects raw input for material problems before anything downstream
  runs.

What remains is five stages of reasoning work, each with one responsibility
and one output:

| Stage | Responsibility | Inputs | Output | Capabilities needed | FRs |
|---|---|---|---|---|---|
| S1: Assess clarification needs | Identify ambiguity, contradiction, or missing context material enough to affect discovery or scope, including input that falls outside the product boundary entirely (FR-15); produce a bounded set of prioritized questions, or explicitly none. | The idea owner's raw input (idea, target user, outcome, constraints — any of which may be blank) | A bounded list of clarification questions (each with a reason it matters), or an explicit no-questions-needed result | None — reasons only from supplied input; no external lookup | FR-02, FR-03, FR-15 |
| S2: Frame the problem | Produce a coherent discovery summary: problem statement, target users, stakeholders, needs, outcomes, constraints — every claim labeled provided / inferred / assumption / open question. | Idea owner's raw input, plus the idea owner's answers, skips, or deferrals given in response to S1's questions | A `DiscoverySummary`-shaped artifact with certainty labels on every material claim | None | FR-04, FR-05 |
| S3: Propose scope and risks | Propose a focused MVP boundary (included capabilities, non-goals, trade-offs, follow-ons) and the material risks that boundary creates, each carrying its own certainty label. | The discovery summary from S2 | A scope proposal plus a list of risks (each with impact, certainty, and a suggested validation/mitigation) | None | FR-05, FR-06, FR-07 |
| S4: Specify requirements, stories, and acceptance criteria | Derive testable, prioritized, certainty-labeled requirements from the scope, express them as user stories, and give each MVP story observable acceptance criteria — as one coherent, internally-consistent set. | Discovery summary, scope, and risks from S2/S3 | Requirements, user stories (linked to requirements), and acceptance criteria (linked to stories) | None | FR-05, FR-08, FR-09, FR-10 |
| S5: Plan delivery | Turn requirements and stories into a prioritized, dependency-aware backlog with a validation method per item, MVP work separated from future work, unresolved blocking risks/questions carried onto each affected item, and a reasonable starting point identified. | Requirements and stories from S4; risks and follow-ons from S3; open questions from S2 | A backlog: item, outcome, linked story/requirement, priority, dependencies, validation method, unresolved blockers | None | FR-11 |

None of the five stages requires a capability beyond reasoning over
supplied context — this follows directly from the non-goals in
`02-product-requirements.md` ("does not... execute irreversible actions in
external systems," no market research, no external validation). Step 3 of
this design will confirm whether this holds once tool needs are considered
more deliberately, but nothing in the requirements currently implies a
stage needs to look anything up, write anywhere, or call an external
service.

**Why S3 bundles scope and risk into one stage rather than two:** this
appears to fail the base document's "and" heuristic ("if describing a
stage's output needs the word 'and,' it is probably two stages"), so the
exception is stated explicitly rather than left implicit, the same way S4's
and S5's bundling decisions are. Risks here are defined *relative to* the
scope boundary being proposed in the same breath — what's excluded, what's
uncertain about the boundary chosen — so producing them in one reasoning
pass keeps each risk consistent with the exact scope decision that produced
it, rather than requiring a second stage to re-derive the same boundary
reasoning to check its risks against.

**Why S4 bundles requirements, stories, and acceptance criteria into one
stage:** a story references a requirement, and acceptance criteria belong
to a story — one reasoning call keeps them mutually consistent by
construction, rather than needing a second or third stage to re-validate
links a split would have introduced.

**Why S5 (backlog) is a separate stage rather than folded into S4:** unlike
S4's bundling, a backlog item's defining relationship is to
*already-finalized* stories and requirements, and it introduces its own
distinct concerns (dependency ordering, a validation method, identifying a
starting item) that are not naturally checked by the same reasoning pass
that produced S4's output. Keeping it separate makes its dependency and
sequencing logic independently validated, consistent with how each bundling
decision above is judged case-by-case rather than by a blanket rule.

### Sequence

The stage *order* is linear and follows the dependency chain in the
requirements — no requirement in the product spec implies a branch, a
parallel split, or an automatic loop-back. The *inputs*, however, are not
strictly one-stage-feeds-the-next: they accumulate. S5 in particular needs
output from S2, S3, and S4, not only the stage immediately before it
(FR-11's requirement that each backlog item carry "unresolved risks or
questions that could block delivery," and separate MVP from future work,
pulls directly from S3's risks/follow-ons and S2's open questions, not only
S4's requirements and stories). Stating this plainly matters because it is
the main constraint step 4's memory design has to satisfy: whatever carries
state between stages must make every earlier stage's output available to
every later stage that needs it, not just to its immediate successor.

The sequence also contains one guaranteed pause that is not itself a
stage: after S1 produces its questions, the run stops and waits for the
idea owner to answer, skip, or defer each one (FR-03) before S2 can run.
This is a human-interface point, not a reasoning stage — S1's job is
producing the questions, not conducting the wait — so it is shown in the
diagram as a distinct step whose mechanics (how the wait is implemented,
what happens if the idea owner never responds) are deferred to step 4,
consistent with how every other human-interface and termination concern in
this document is deferred.

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
  [ Idea owner answers, skips, or defers each question ]   (human interface; mechanics in step 4)
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
  +----------------------+                 accumulated inputs:
  | S5 Plan delivery      | <-------------- S2's open questions,
  +----------------------+                 S3's risks and follow-ons,
        |                                  S4's requirements and stories
        v
  Discovery package (draft)
```

Per the base document's guidance ("a linear sequence is the easiest to
validate, test, and explain — use a richer shape only when a requirement
forces it"), nothing in `02-product-requirements.md` forces a richer
*order* than the linear one shown. FR-13's correction/regeneration behavior
does re-enter this sequence, but as a human-triggered re-run starting from
whichever stage is affected, not as an automatic loop — that is
control-relationship (human interface and termination) design, deferred to
step 4.

### Comparison with the removed technical design

The removed technical design (PR #15) reached a similar stage list —
clarification, discovery framing, scope/risk, requirements, delivery
planning, quality review — arrived at directly in CrewAI's vocabulary
(`Agent`/`Task` roles) rather than derived independently first. Two
differences are worth naming: that design included a sixth, explicit
quality-review stage, where this document treats structural and semantic
validation as a control relationship (step 4) applied to each stage's
output rather than a stage of its own; and it placed the idea-owner pause
between clarification and framing at a CLI command boundary (`pdpa clarify`
→ `pdpa generate`), outside the crew, then ran clarification assessment a
second time as the first task *inside* the crew. The pause existed, but
repeating clarification inside the generation pipeline blurred the line
between the clarification stage and the human pause that follows it. This
document instead runs S1 once and shows the pause as its own step (see
finding 1 of the [step 1 review](./reviews/03-step1-review.md)). Both
differences are revisited once step 4 is complete, since either could
change once validation and human-interface design are worked through
explicitly rather than assumed.

### Open questions carried into later steps

- Whether S1 (clarification) should be able to run again mid-sequence
  (e.g., if S3 or S4 discovers new material ambiguity) or whether it only
  ever runs once, at the start — this is a termination/control question for
  step 4, not a sequencing question, since the requirements do not
  currently describe generation-time re-clarification as a first-class
  path (FR-03 describes the *initial* bounded question set). The removed
  technical design took a position on this: it bounded the first question
  set and allowed "a later generation [to] surface additional open
  questions only when they materially affect scope, risk, or acceptance
  criteria." That policy is a candidate answer to evaluate in step 4.
- Whether S4's bundling (requirements + stories + acceptance criteria in
  one stage) remains viable once step 2 defines the reasoning-core
  configuration for it, or whether the combined responsibility is too large
  for one configuration to hold reliably — worth revisiting once step 2 is
  underway.
- Whether the product requirements' caution against presenting "downstream
  planning as final when upstream ambiguity remains material," combined
  with FR-13, implies additional idea-owner sign-off pauses between stages
  beyond the one after S1 (for example, confirming S2's framing before S3
  proposes scope against it) — a human-interface and termination question
  for step 4, not a sequencing question.
- FR-13's regeneration model ("regenerate downstream content after a
  material correction") requires every stage to be re-runnable from the
  saved outputs of earlier stages, not only run once end-to-end — a
  constraint step 4's memory design has to satisfy.

## Step 2 — Reasoning-core configurations

_Pending._

## Step 3 — Capability contracts

_Pending._

## Step 4 — Control relationships

_Pending._

## Step 5 — Framework mapping

_Pending._
