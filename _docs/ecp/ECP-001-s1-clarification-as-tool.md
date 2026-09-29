# ECP-001: Move clarification question-asking into S1 as an action executor

**Status:** Proposed
**Author:** Design session, 2026-09-28
**Affects:** [`03-agentic-system-design.md`](../03-agentic-system-design.md) —
Step 1 (Stages and sequence), Step 2 (Reasoning-core configurations),
Step 3 (Capability contracts), and Step 4 (Control relationships). All four
are frozen (merged in
[#17](https://github.com/natank/project-discovery-planning-assistant/pull/17),
[#18](https://github.com/natank/project-discovery-planning-assistant/pull/18),
[#19](https://github.com/natank/project-discovery-planning-assistant/pull/19),
[#21](https://github.com/natank/project-discovery-planning-assistant/pull/21)),
including Step 4's "Outer-loop concerns" subsection, which this proposal
would partially undo (see Step 4 section below).

## Summary

Give S1 (Assess clarification needs) an action executor — a tool the
clarification analyst can call to ask the idea owner its questions and
receive answers, skips, or deferrals — instead of treating question-asking
as an outer-control-loop step that happens strictly after S1 has already
terminated.

Under this proposal, S1's own inner loop would: produce candidate
questions, call the tool to ask them, receive the idea owner's responses,
and optionally re-check or refine its questions against those responses
before producing one final output. S1's output would be a discovery-ready
result (questions plus their resolved answers), rather than a bare question
list handed to the outer loop for a separate ask-and-wait step.

## Motivation

Two arguments were raised in favor of this change during design review:

1. **Reuse.** An `ask`-style action executor (the base document's own step
   1 lists "ask" as a legitimate capability type, alongside "look up,
   compute, write") is a natural candidate for reuse if a later stage, or a
   later release, needs to ask the idea owner something mid-task. Building
   it as a tool once, rather than as a one-off outer-loop mechanism specific
   to the S1→S2 boundary, makes that reuse straightforward.
2. **Re-checking.** If asking is a tool call inside S1's own inner loop,
   sending the collected answers back to the reasoning core for a
   consistency re-check ("does this answer actually resolve the ambiguity
   the question was about?") is just another turn of the same loop — no new
   mechanism is needed. Under the current design, S1 runs once and never
   sees the answers at all (S2 is the first stage to read them), so
   re-checking would require inventing a new re-invocation path.

## What this changes, precisely

### Step 1 (Stages and sequence)

- S1's **output** changes from "a bounded list of clarification questions...
  or an explicit no-questions-needed result" to a result that also
  incorporates the idea owner's answers, skips, and deferrals — S1 no
  longer terminates at the question list.
- S1's **capabilities needed** changes from "None" to one ask-style
  capability.
- The **sequence diagram**'s `[ Idea owner answers, skips, or defers each
  question ]` step, currently drawn as a distinct box between S1 and S2,
  would move inside S1's box — S2 would receive S1's output directly, with
  no intervening step drawn in the stage sequence.
- The **inputs accumulation** section, and S2's stated inputs, would need
  revisiting: S2 currently reads "the idea owner's original raw input...
  plus the answers... collected after S1 completes" as two separately
  provenanced inputs read from memory by the outer loop (per the Step 4
  outer-loop fix). Under this proposal, the answers arrive as part of S1's
  output instead, changing what "provenance" means for that data.

### Step 2 (Reasoning-core configurations)

- The clarification analyst's **allowed tools** changes from "None" to
  naming the ask/collect-answers tool.
- The clarification analyst's **instructions** need a new "must" governing
  how it uses the tool (e.g., ask the full bounded question set in one
  call, or ask iteratively; whether and how it may re-ask after seeing an
  answer) and a new "must never" governing misuse (e.g., must not treat an
  unanswered/deferred question as license to invent an answer, must not
  re-ask a question the idea owner already explicitly deferred).
- The clarification analyst's **output shape** changes to include resolved
  answers alongside questions, rather than questions alone.

### Step 3 (Capability contracts)

- Step 3's central conclusion — "there are no capability contracts to
  specify... every stage terminates with reasoning-only output rather than
  an action on the world" — would no longer hold. This proposal introduces
  the first capability contract in the design, requiring a full entry
  against the base document's step 3 table: name and purpose, arguments,
  result, side effects, failure modes, retry safety, and approval needed.
- Step 3's downstream notes for Step 4 and Step 5 ("no capability-failure
  retry/idempotency design needed," "capability dispatch... not
  applicable") would both need to be retracted and replaced.

### Step 4 (Control relationships) — frozen, merged in #21

- S1's **termination** definition (currently: success = a valid question
  list; exhausted = a small fixed number of reasoning-core-call attempts)
  would need to distinguish two independent failure modes within the same
  stage: the reasoning-core call failing (fast, bounded, provider-side) and
  the tool call's human-response wait failing to resolve (unbounded, not
  provider-side). Conflating these was the specific risk raised when this
  proposal was first discussed; resolving it is a precondition for
  accepting this ECP, not a detail to defer.
- The **"Outer-loop concerns" section** (added to the base document in
  [#20](https://github.com/natank/project-discovery-planning-assistant/pull/20)
  and applied to this design) would lose one of its two entries: the
  S1→S2 pause would no longer be an outer-loop concern, since asking would
  happen inside S1. The intake-persistence entry (writing the idea owner's
  raw input into memory before S1 runs) is unaffected and remains an
  outer-loop concern under this proposal.
- S1's and S2's **per-stage table cells**, corrected in the outer-loop fix
  to stop attributing the pause to S1 and to describe S2's two
  differently-provenanced inputs, would need correcting again in the
  opposite direction.

## Alternatives considered

**Keep the current design (S1 produces questions; the outer control loop
invokes the human-interface component as a separate step).** This is the
status quo this ECP proposes to change. Its advantage is exactly what this
ECP gives up: S1's termination condition stays simple (bounded by a single
reasoning-core call), and there is no unbounded wait inside any stage's
inner loop. Its disadvantage is the one this ECP is written to address: no
built-in mechanism for reuse or for the reasoning core to react to answers
before generation moves on to S2.

## Risks and open concerns

- **Termination/retry conflation**, named above and in the motivating
  design discussion, is the main technical risk. It must be resolved by
  this ECP's Step 4 rework, not left as an open question the way several
  earlier findings have been — an unbounded wait miscounted against a
  reasoning-core retry cap would either time out a legitimate human
  response or hang indefinitely on a genuine provider failure.
- **Re-opens a previously resolved question.** Step 4 (draft) already
  resolved "can S1 run again mid-sequence?" with "no — S1 runs once." This
  ECP does not reverse that answer (S1 still runs once, from the outer
  loop's perspective; any re-checking happens as multiple turns *within*
  that one invocation's inner loop), but the distinction is subtle enough
  that it must be stated explicitly in the revised Step 4, not left
  implicit, so a future reader does not mistake this ECP for reversing that
  decision.
- **Precedent for future capabilities.** This is the first capability
  contract in the design. Its shape (an "ask" tool with a human-response
  wait as its side effect) sets a pattern other stages might follow later;
  the committee should consider whether that precedent is desired before
  accepting it here.

## Disposition

Pending committee review. If accepted, Steps 1–4 (all currently frozen)
will be reopened for targeted revision, not a full redo, and each revision
will go through review before being merged, consistent with how each step
was originally reviewed and merged.
