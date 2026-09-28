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

Reviews of each step are kept in [`reviews/`](./reviews/), starting with
the [step 1 review](./reviews/03-step1-review.md).

## Introduction

This document derives the system design from
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

Each step is worked through against the requirements. The goal is a design
that names, for every stage, exactly which component is responsible for
each of the six relationships, with the framework chosen only after that is
settled.

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
| S2: Frame the problem | Produce a coherent discovery summary: problem statement, target users, stakeholders, needs, outcomes, constraints — every claim labeled provided / inferred / assumption / open question. | The idea owner's original raw input (unchanged since before S1 ran), plus the idea owner's answers, skips, or deferrals collected after S1 completes | A `DiscoverySummary`-shaped artifact with certainty labels on every material claim | None | FR-04, FR-05 |
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

Each stage from step 1 needs a reasoning-core configuration: a role,
instructions, allowed tools, and output shape. This step asks what each
stage's configuration must be, independent of any framework's `Agent`
class.

### Configurations

| Configuration | Role | Instructions | Allowed tools | Output shape |
|---|---|---|---|---|
| Clarification analyst | Identifies material ambiguity, contradiction, and missing context in an idea owner's raw input, and detects input that falls outside the product's boundary entirely. | Must: read only the supplied input; raise a question only when the answer would materially change discovery or scope; state why each question matters; bound the question set rather than exhaustively enumerating every gap; explicitly return zero questions when input is sufficient. Must never: invent a target user, outcome, or constraint not stated or answered; treat a blank optional field as a problem requiring a question, since FR-01 allows it to remain unknown; ask about something only relevant to a later stage. | None | A bounded list of questions, each with the question text and why it matters, or an explicit no-questions-needed result; a distinct out-of-boundary result when the input is not a software idea at all (FR-15) |
| Discovery framer | Frames the problem, target users, needs, outcomes, and constraints from the idea owner's context. | Must: use only the idea owner's input plus S1's recorded answers, skips, and deferrals; label every material claim as provided, inferred, assumption, or open question; carry forward a skipped or deferred question as an open question rather than silently dropping it. Must never: present an inference or assumption as a verified fact; resolve an open question on its own initiative; introduce a target user, stakeholder, or constraint the idea owner did not state or the analyst did not ask about. | None | A discovery summary: problem statement, target users, stakeholders, needs, outcomes, constraints, each material claim certainty-labeled |
| Scope strategist | Proposes a focused MVP boundary and the risks that boundary creates. | Must: derive the boundary from the discovery summary alone; state the trade-off or constraint behind each inclusion and exclusion; identify follow-on opportunities separately from the MVP; give every risk an impact, a certainty label, and a suggested validation or mitigation activity. Must never: propose a capability the discovery summary gives no outcome or need for; omit a risk directly implied by an excluded capability or an open question in the discovery summary; claim a risk has been validated or mitigated rather than merely suggesting how it could be. | None | A scope proposal (included capabilities, non-goals, trade-offs, follow-ons) plus a list of risks, each certainty-labeled |
| Requirements analyst | Derives testable requirements, user stories, and acceptance criteria from the MVP boundary the scope strategist proposed. | Must: derive every requirement only from a capability the scope strategist placed in `included_capabilities` (the MVP boundary itself, not the scope proposal's non-goals or follow-ons), or from a need/outcome in the discovery summary that an included capability serves; give each requirement a rationale traceable to that in-scope source; give each MVP story at least one linked requirement and observable acceptance criteria; keep requirements free of implementation detail. Must never: invent a requirement with no traceable source; derive a requirement from a capability listed in the scope proposal's non-goals or follow-ons, since neither is part of the MVP boundary FR-06 defines; produce a story without acceptance criteria; describe an acceptance criterion in terms of how the software is built rather than what it does. | None | Requirements (identifier, statement, target user/outcome, priority, rationale, dependencies, acceptance considerations), user stories (identifier, role, capability, value, priority, linked requirements), acceptance criteria per MVP story |
| Delivery planner | Turns requirements and stories into a prioritized, dependency-aware delivery backlog. | Must: link every backlog item to at least one requirement or story; give every item a priority, a validation method, and its dependencies; separate MVP items from future work; carry forward any risk or open question from earlier stages that could block an item; identify a reasonable starting item. Must never: introduce a backlog item with no linked requirement or story; state a dependency that contradicts the proposed delivery order; drop a risk or open question that materially affects an item's readiness. | None | A backlog: item, outcome, linked story/requirement, priority, dependencies, validation method, unresolved blockers |

### Allocation

Each stage gets its own configuration. No two stages share one, even though
every configuration currently has the same "None" tools column — reuse is
judged on role and instructions, not on tool overlap, and each stage here
asks for a genuinely different expertise (assessing ambiguity is not the
same skill as proposing a scope boundary, which is not the same skill as
writing acceptance criteria). Collapsing any two into one configuration
would mean asking a single role to hold two distinct sets of "must never"
instructions at once, which is exactly the risk the base document's
least-capability rule warns against, applied here to role clarity rather
than to tool access.

```
  Stages                                    Configurations
  +----------------------------+
  | S1 Assess clarification    |----------> [ Clarification analyst ]
  | needs                      |
  +----------------------------+
  | S2 Frame the problem       |----------> [ Discovery framer      ]
  +----------------------------+
  | S3 Propose scope and risks |----------> [ Scope strategist      ]
  +----------------------------+
  | S4 Specify requirements/   |----------> [ Requirements analyst  ]
  | stories/acceptance criteria|
  +----------------------------+
  | S5 Plan delivery           |----------> [ Delivery planner      ]
  +----------------------------+
```

### Coverage and least-capability check

- **Least capability:** every configuration's allowed-tools column is
  "None" — this restates step 1's finding that no stage needs a capability
  beyond reasoning over supplied context, now confirmed at the
  configuration level rather than the stage level. There is nothing to
  over-grant.
- **Coverage:** since no stage needs a tool, coverage in the sense of "does
  every capability a stage needs appear on its configuration" is trivially
  satisfied. The real coverage question at this step is instructional, not
  tool-based: does each configuration's instructions actually cover what
  its stage's responsibility (step 1) and inputs require it to do. The
  "Must" column above is written to enumerate exactly the responsibility
  from step 1's stage table, and the "Must never" column is written to
  enumerate the non-goals and certainty-labeling requirements (FR-05,
  the product's non-goals section) that apply to every stage rather than
  restating them once and hoping each configuration inherits them.
- **MVP boundary ownership:** the scope strategist (S3) is the only
  configuration that decides what is in the MVP — its output separates
  `included_capabilities` from `non_goals` and `follow_ons` precisely so
  that decision is explicit and checkable. An earlier draft of the
  requirements analyst's instructions said to derive requirements from any
  "capability, outcome, or risk named in the discovery summary or scope
  proposal," which is broader than intended: the scope proposal also
  contains non-goals and follow-ons, and both are capabilities the scope
  strategist explicitly excluded from the MVP. A requirement traced to
  either would still pass a naive reading of "traceable to the scope
  proposal." The requirements analyst's instructions now name
  `included_capabilities` specifically, and its must-never list states the
  failure this closes: deriving a requirement from a non-goal or follow-on
  contradicts FR-06's "each MVP requirement" framing, since neither is part
  of the MVP.

### Open questions carried into later steps

- Whether the requirements analyst's combined responsibility (requirements,
  stories, and acceptance criteria in one call) is reliably held by one set
  of instructions once real output is produced against it, or whether it
  needs splitting after all — this was flagged in step 1 as an open
  question and remains open here, since step 2 alone cannot resolve it;
  only observing real output can.
- Whether the discovery framer's instruction to "carry forward a skipped or
  deferred question as an open question" needs a more precise output-shape
  rule (e.g., a required field rather than a prose mention) to make FR-03's
  "deferred questions remain visible" requirement checkable by validation
  in step 4, rather than merely instructed here.

## Step 3 — Capability contracts

Step 1 and step 2 each concluded, independently, that none of the five
stages needs a capability beyond reasoning over supplied context. That
conclusion is re-checked here directly against the requirements, rather
than simply carried forward, since a design step that only restates an
earlier step's output without re-examining it against the source is exactly
how the step 2 review's MVP-boundary gap slipped through — the earlier
draft trusted "traceable to the scope proposal" without checking what the
scope proposal actually contained.

### Re-checking against the requirements

Searching `02-product-requirements.md` for anything that would imply a
stage needs to look up, compute, write, or ask beyond what step 1 and step
2 already assumed:

- The **non-goals** section rules out market validation, replacing domain
  expertise, external system integration, and multi-project/workspace
  management — none of which any of the five stages would need a
  capability for even if they were in scope.
- **NFR-02** ("must not take irreversible external actions") and the
  architecture-level non-goal against external search, retrieval, or
  research integrations both rule out a stage having a write or lookup
  capability by design, not merely by omission — this is a constraint the
  product actively enforces, not an area the requirements are simply silent
  on.
- **FR-15** ("It shall either ask for clarification or produce a visibly
  qualified partial package") could be misread as implying an "ask"
  capability in the sense the base document lists (relationship 2, a tool
  the reasoning core calls mid-task). It does not: FR-15's "ask for
  clarification" is exactly what S1 already does as its entire
  responsibility — producing a bounded list of clarification questions,
  which is S1's ordinary output, not an interruption S1 makes mid-task via
  a tool call. No stage in this design produces output, then pauses,
  then asks a follow-up question through a capability; the one guaranteed
  pause in the whole system is the human-interface point after S1
  completes (step 1's sequence), not a tool any stage invokes.

Nothing else in the functional requirements, non-functional requirements,
or backlog implies a stage-level capability. The conclusion from steps 1
and 2 holds.

### Capability contracts

There are no capability contracts to specify. No stage's configuration
(step 2) lists an allowed tool, so there is no business logic, argument
schema, failure mode, retry policy, or approval requirement to define at
this step. This is a legitimate, checked outcome of the design process, not
a skipped step: the base document's step 3 exists to specify the action
executors behind relationship 2, and this design has no relationship 2 to
specify, because every stage terminates with reasoning-only output rather
than an action on the world.

### What this implies for step 4 and step 5

- **Step 4** will not need to design retry or idempotency behavior for any
  capability failure, since there are none. Its termination logic instead
  concerns only relationship 1 failures (a stage's reasoning-core call
  producing no valid output) and relationship 4 rejections (a stage's
  output failing validation) — not relationship 2 failures.
- **Step 5** will find that whichever framework is chosen absorbs
  relationship 2 by default, trivially, since no stage ever populates a
  tool list. A framework mapping table entry for "capability dispatch" will
  read "not applicable" rather than naming who owns it.

### Open question carried into later steps

- If a future release adds a capability to any stage (for example, the
  deferred backlog items for domain context or delivery-tool integration in
  `02-product-requirements.md`), step 3 will need to be revisited for that
  stage specifically; nothing in this design assumes the "no capabilities"
  finding is permanent, only that it holds for the requirements as
  currently scoped.

## Step 4 — Control relationships

Steps 1–3 describe what the system does. This step describes how each
stage stays trustworthy while doing it: what it needs from memory, what
validates its output, what counts as its success, failure, and exhausted
outcomes, and whether it needs human sign-off.

Before working stage by stage, five questions carried forward from steps
1–3 are resolved, since several of them constrain every stage's control
design rather than one stage's.

### Resolving the carried-forward questions

**1. Can S1 re-run mid-sequence, or does it only ever run once, at the
start?**

S1 runs once, at the start. Nothing in `02-product-requirements.md`
describes generation-time re-clarification as a first-class path; FR-03
describes a single, initial, bounded question set. Introducing a second,
implicit clarification pass triggered automatically by S3 or S4 finding
new ambiguity would create exactly the kind of automatic loop-back step 1
found no requirement forcing, and it would blur which stage owns detecting
ambiguity (S1's entire responsibility) versus which stage owns proposing
content (S3, S4). If a later stage's reasoning surfaces new material
ambiguity, that is a validation finding on *that* stage's own output
(recorded as an open question below, per-stage), not a re-invocation of
S1. This also means S1 needs no iteration-count or loop-detection
termination logic of its own beyond the single-call default every stage
gets (see the per-stage tables below) — there is no inner loop across
multiple S1 invocations to bound.

**2. Does the "don't present downstream planning as final" caution, plus
FR-13, imply idea-owner sign-off pauses between every stage, not only after
S1?**

No — one pause is sufficient, and adding a pause after every stage would
contradict NFR-04 ("the primary path should minimize unnecessary questions
and present one clear next action at each stage"). The caution against
presenting downstream planning as final is satisfied by **visible,
carried-forward uncertainty**, not by an approval gate at every stage
boundary: S2's certainty labels, S3's risks, and S4/S5's traceable
open-question carry-forward (FR-05, FR-12) already make unresolved
ambiguity visible in the final package without stopping the pipeline to ask
about it mid-run. The one pause that remains structurally necessary is
after S1, because it is the only point where the pipeline cannot
meaningfully proceed at all without idea-owner input — S2 through S5 each
have a well-defined output even when upstream certainty is low (the
certainty label itself *is* that output). Review of the *complete* draft
package (FR-13, "review" command) remains a single pass at the end of
generation, not a pause folded into the middle of it, and correction from
that review is handled by the re-run mechanism resolved in question 3, not
by additional mid-pipeline pauses.

**3. Every stage must be re-runnable from earlier stages' saved outputs
(FR-13 regeneration) — what does this require of memory?**

This means memory cannot be purely transient, scoped only to one
end-to-end run. Each stage's output must be persisted, addressable, and
re-loadable independently, so that a correction affecting (for example)
S2's framing can trigger S3, S4, and S5 to re-run from the corrected S2
output without re-running S1. This is stated here as a memory design
constraint the per-stage tables below satisfy by giving every stage both a
persisted input and a persisted output, not merely an in-memory handoff to
the next stage. It also means "memory" in this design has both a
run-scoped role (accumulating inputs within one generation, per step 1's
sequence section) and a cross-run role (surviving a correction and a
subsequent partial re-run) — both are addressed per stage below.

**4. Does the discovery framer's "carry forward deferred questions"
instruction need a stricter, checkable output-shape rule?**

Yes. "Carry forward a skipped or deferred question as an open question" is
adequate as an instruction to the reasoning core (step 2) but not
adequate as something validation can check. This step resolves it: S2's
output shape must include open questions as a structured, required list
field (not merely as text embedded in prose), so that validation can
mechanically confirm every question skipped or deferred in S1 appears in
that field, and FR-03's "deferred questions remain visible" becomes a
checkable rule rather than a hoped-for behavior. This is recorded in S2's
validation row below.

**5. Is the requirements analyst's combined scope (requirements + stories
+ acceptance criteria in one call) reliable?**

This remains genuinely open, as noted when first raised in step 1: it is a
question about a specific configuration's reliability under real output,
which no amount of design-time reasoning resolves. What step 4 *can* do is
make the failure mode this question is worried about — a story missing
acceptance criteria, or a story with no linked requirement — mechanically
detectable rather than something only a human reviewer would catch. S4's
validation row below does this. If observed output later shows this
configuration is unreliable even with validation catching failures, step 2
would need revisiting to split S4 into separate stages; that revisit is
not performed here, since it depends on evidence step 4 cannot produce on
its own.

### Per-stage control relationships

| Stage | Memory | Validation | Termination | Human interface |
|---|---|---|---|---|
| S1: Assess clarification needs | In: the idea owner's raw input, written to memory by the outer control loop before S1 is invoked (see "Outer-loop concerns" below — this is not S1's own action). Out: the question list (or no-questions/out-of-boundary result), persisted for the outer loop and for S2 to read. No cross-run role beyond this — S1 does not need prior-run history, since it only ever runs once per project. | Shape: output matches the clarification-question schema (question, reason, priority) or one of the two explicit alternative results. Content: each question's stated reason must reference something present in the raw input (a check against fabricated rationale) — reject and retry within this stage's own call if a question has no traceable reason. | Success: a valid question list (zero or more) or a valid out-of-boundary result. Failure: the reasoning-core call produces no parseable output after retry. Exhausted: not applicable at the per-call level (single call, per question 1 above) but applicable at the project level if S1 cannot produce valid output after a small, fixed number of attempts (e.g., 2) — treated as a configuration/provider failure, not a content problem. | None required to run S1 itself. The pause where the idea owner answers, skips, or defers each question happens after S1 completes and is not part of S1's own envelope — see "Outer-loop concerns" below. |
| S2: Frame the problem | In: two inputs of different provenance, both read from memory by the outer control loop when it invokes S2 — the idea owner's original raw input (written before S1 ran) and the answers/skips/deferrals collected during the pause after S1 (see "Outer-loop concerns" below). Out: the discovery summary, including the structured open-questions field from question 4 above, persisted so S3 (and a later regeneration) can read it without re-running S1 or S2. | Shape: output matches the `DiscoverySummary` schema, and every material claim carries one of the four certainty labels (FR-05) — reject if any required claim is unlabeled. Content: every question skipped or deferred in S1 must appear in S2's structured open-questions field (the check that resolves question 4) — reject and retry if any is missing. | Success: a certainty-labeled, schema-valid summary with no missing carried-forward question. Failure: schema-invalid output, or a missing carried-forward question, after retry. Exhausted: a small fixed retry cap (consistent with S1), beyond which this is a provider/configuration failure rather than a content one. | None. S2 does not pause for approval; its output's certainty labels are what make its uncertainty visible downstream (per question 2), not a gate that stops the pipeline. |
| S3: Propose scope and risks | In: the discovery summary from S2. Out: the scope proposal (with `included_capabilities`, `non_goals`, `follow_ons` as distinct fields per step 2's fix) and the risk list, persisted independently so S4 and S5 can each read exactly what they need without re-running S2 or S3. | Shape: output matches the scope/risk schema, `included_capabilities` and `non_goals` are disjoint sets (a capability cannot be both included and excluded — a structural check directly enforcing the step 2 fix), every risk has an impact, a certainty label, and a suggested validation/mitigation. Content: every excluded capability or open question from S2 that plausibly creates a risk must have a corresponding risk entry (the check step 1 already named: "omit a risk directly implied by an excluded capability... " is a must-never for the configuration; this is its validation-side enforcement). | Success: schema-valid, disjoint scope sets, risk coverage check passes. Failure: `included_capabilities`/`non_goals` overlap, or a risk-coverage gap, after retry. Exhausted: same fixed retry cap as S1/S2. | None required to run. Whether a human should confirm the scope boundary before S4 builds requirements against it was considered under question 2 and rejected as a mandatory gate — S4's requirements are traceably reversible (a later correction to S3 triggers S4's re-run, per question 3), so a blocking approval here is not required by the product requirements, only a single end-of-run review. |
| S4: Specify requirements, stories, and acceptance criteria | In: discovery summary (S2), scope and risks (S3). Out: requirements, stories, and acceptance criteria, persisted together as one unit (they are validated together, per the check below) so a regeneration of S4 has a single, complete artifact to replace. | Shape: output matches the requirements/story/acceptance-criteria schema. Content, mechanically checked per the step 2 fix: every requirement's source capability is a member of S3's `included_capabilities`, not of `non_goals` or `follow_ons` — reject and retry if any requirement traces to an excluded capability; every MVP story has at least one linked requirement and at least one acceptance criterion — reject if any story is missing either. | Success: schema-valid, every requirement in-scope, every story has a requirement and criteria. Failure: an out-of-scope requirement, or a story missing a link or criteria, after retry. Exhausted: same fixed retry cap. | None required to run. This is the stage flagged as an open reliability question (question 5); its validation check is the concrete mitigation available at this step, and the check is content-specific enough (traces the exact step 2 fix) that a validation failure here is informative rather than a generic reject. |
| S5: Plan delivery | In: requirements and stories (S4); risks and follow-ons (S3); open questions (S2) — the accumulated-inputs case step 1 identified as the main memory constraint. Out: the backlog, persisted as the final generation-stage artifact before assembly (traceability, export) takes over. | Shape: output matches the backlog schema; every item has a priority, a validation method, and at least one dependency reference or an explicit "no dependencies" marker. Content: every backlog item links to at least one S4 requirement or story (no orphaned items); every item's "unresolved blockers" field is checked against S3's risk list and S2's open-question list for anything that plausibly blocks it, rather than left empty by default; at least one item is marked as the starting item. | Success: schema-valid, every item linked, blockers populated where applicable, a starting item identified. Failure: an orphaned item, an empty blockers field where S3/S2 clearly named a relevant risk or question, or no starting item, after retry. Exhausted: same fixed retry cap. | None required to run S5 itself. S5's completion is what makes the draft package complete and ready for the single end-of-run human review (FR-13), which is the human-interface point for the run as a whole rather than for S5 specifically. |

### The stage envelope, applied to this design

Every stage above follows the same shape the base document describes,
specialized to this design's actual, small set of outcomes (no capability
failures, since step 3 found none apply; retry stays within one stage
rather than escalating automatically, since no requirement calls for
automatic escalation mid-generation):

```
        memory in (accumulated                    memory out
        prior-stage outputs,                        |
        per step 1's sequence)                       v
             |                              +--------------------+
             v                              | persisted, keyed   |
  +----------------------------------+      | to this stage, for |
  |  Stage N                          |     | later stages and   |
  |    reasoning core config (step 2) |---->| for FR-13 re-run   |
  |    capabilities: none   (step 3)  |     +--------------------+
  +----------------------------------+
             |
             v
  +--------------------+
  |  Validation         |--reject (within retry cap)--> retry Stage N
  |  (shape + content,  |
  |   per table above)  |
  +--------------------+
             |
     +-------+-------+
     |               |
   pass          exhausted
     |               |
     v               v
  next stage   provider/configuration
               failure (NFR-05: surfaced
               explicitly, non-zero exit,
               no success-shaped package)
```

No stage in this design has an "escalate to human mid-generation" path out
of its validation box, unlike the base document's general envelope —
question 2 above establishes that this product's human-interface point is
a single pause after S1 plus a single end-of-run review, not a per-stage
escalation gate. A validation failure that exhausts its retry cap becomes a
failed run (NFR-05), surfaced to the idea owner with a useful next action
(FR-16), not a mid-run request for human input.

The diagram's "pass leads to next stage" arrow describes every stage
*except* the step between S1 and S2, which is not a stage property at all
— it is covered separately below, in "Outer-loop concerns," since it
belongs to the outer control loop rather than to either stage's envelope.

### Outer-loop concerns

The per-stage table and the envelope diagram above describe what happens
inside each stage's own boundary. Two things in this design belong to the
outer control loop instead — the orchestrator that invokes each stage and
sequences them — and are recorded here rather than attributed to a stage,
per the base document's step 4 guidance.

**Writing the idea owner's raw input into memory.** Before S1 can run, the
idea owner's raw input has to already be in memory for S1 to read (S1's
memory row above says "persisted at intake," which describes *that* it is
persisted, not *who* persists it). Persisting it is not part of S1 itself
— S1's inner loop begins only once that input already exists in memory —
so it is the outer control loop's responsibility, performed once, as the
very first action of a run, before S1 is invoked at all:

```
  Idea owner provides raw input (FR-01, intake; not a stage)
        |
        v
  Outer control loop writes it to memory
        |
        v
  Outer control loop invokes S1
```

**The pause between S1 and S2.** For every stage except S1, `pass` in the
envelope diagram above genuinely does mean the next stage starts
immediately. Between S1 and S2 specifically, S1's own completion (a valid
question list, or an explicit no-questions/out-of-boundary result) does
not mean S2 starts — the idea owner must first answer, skip, or defer each
question (FR-03). This is not an escalation out of S1's own validation (S1
already passed); it is the outer control loop invoking the human-interface
component as its own step between two stage invocations, the same way it
invokes each stage itself:

```
  Outer control loop invokes S1
        |
        v
  S1 completes (passes validation): a question list, or explicit
  no-questions/out-of-boundary result
        |
        v
  Outer control loop invokes the human-interface component
  (idea owner answers, skips, or defers each question; skipped
  if S1 returned zero questions)
        |
        v
  Outer control loop invokes S2, reading:
    - the original raw input, written to memory before S1 ran
    - the answers/skips/deferrals just collected
```

The second diagram also corrects an imprecision in S2's memory row above:
S2's two inputs are not both "given in response to S1's questions." The
raw input was written once, before S1 ever ran; only the
answers/skips/deferrals are new, collected after S1 completes. Both are
read from memory by S2 when the outer loop invokes it — S2 does not receive
either directly from the idea owner.

If the idea owner never responds to the pause, the project remains in a
pending-input state indefinitely rather than proceeding with fabricated
answers (NFR-02) — there is no timeout that silently substitutes a default;
this restates what S1's human-interface cell already says, attributed here
to the outer loop rather than to S1, since S1 has already completed by the
time this wait begins.

### System-level termination

Beyond each stage's own success/failure/exhausted outcomes, the run as a
whole has its own termination definition, since NFR-05 requires the
product to "not return a success-shaped package when a mandatory stage has
failed":

- **Run success:** all five stages complete successfully in sequence; the
  resulting package is `draft` or `needs_review` (never automatically
  `accepted` — that requires the separate, explicit FR-13 acceptance
  action, outside this generation run entirely).
- **Run failure:** any stage exhausts its retry cap. The run stops at that
  stage; no downstream stage runs; the failure and the last completed stage
  are surfaced to the idea owner (FR-16) with a next action, and no
  package is written as though generation succeeded.
- **Run exhausted, as a distinct case:** not applicable at the run level in
  this design — "exhausted" only occurs at the single-stage retry-cap
  level (per stage above), and a stage-level exhaustion is treated as a
  run failure, not as its own ambiguous run-level outcome. This is
  possible only because retry is bounded and small per stage; there is no
  scenario in this design where the run continues indefinitely without
  reaching either success or a stage failure.

### Open questions carried into step 5

- The specific numeric retry cap (referred to above as "a small, fixed
  number") is left as an implementation parameter rather than fixed here,
  since nothing in the product requirements specifies it — this is a
  framework/implementation decision appropriate to step 5 or later, not a
  product-level control-relationship decision.
- Whether the persisted, keyed-per-stage memory this step requires (for
  FR-13 re-runs) is implemented as its own storage layer or delegated to
  whatever the chosen framework offers by default is a step 5 question:
  this step only establishes that per-stage persistence is required, not
  how it is implemented.

## Step 5 — Framework mapping

_Pending._
