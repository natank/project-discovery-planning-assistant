# CrewAI-Based Agentic Systems

Working notes on how the CrewAI framework maps onto the general
agentic-system model developed in
[Agentic Systems and Workflows](./agentic-systems-and-workflows.md). Builds
directly on that document's vocabulary: objectives, the seven components,
and the six relationships.

_Last updated: 2026-09-27_

## What CrewAI absorbs from the control loop, and what stays with the application

CrewAI's `Crew.kickoff()` takes over some control-loop responsibilities —
but only the *inner* loop, not the outer one. Mapped onto the six
relationships:

### Absorbed by CrewAI

**Relationship 1 (control loop ↔ reasoning core) — mostly absorbed.**
CrewAI assembles the call: it takes an `Agent`'s persona/tools/schema (this
is exactly the "Agent = format contract" definition from the base document)
plus the `Task`'s description, formats the actual prompt, sends it to the
LLM API, and parses the response. The call is never hand-built by the
application — CrewAI's internal executor does it.

**Relationship 2 (control loop ↔ action executors) — absorbed, when tools
exist.** Tools are attached to the **Agent** (`Agent(tools=[...])`), not to
the Crew — the Agent carries the tool schema, i.e. the "what can be asked
for" half of relationship 1's format contract. What CrewAI's control loop
(the Crew's internal execution machinery) absorbs is the *dispatch
mechanism*: when the LLM's response requests a tool the Agent was given, the
loop matches it against the actual Python function behind it, calls it,
gets the result, and feeds it back into the *same* task's ongoing reasoning
— CrewAI running its own internal parse → match → dispatch cycle,
potentially many times, before the task is considered finished. This is
real delegated control-loop behavior: multiple relationship-1/relationship-2
round-trips happening entirely inside one `Task.execute()` call, invisible
to the application.

**Relationship 3 (control loop ↔ memory) — partially absorbed, opt-in.**
With `Process.sequential` and multiple tasks, CrewAI automatically appends
each task's output into the next task's input context — CrewAI performing
the write-then-read of short-term memory itself, without the application
doing it by hand. `Crew(memory=True)` extends this further with
cross-task/cross-run retrieval.

**Relationship 5 (termination logic) — absorbed, but only at the
single-task level.** Within one task, CrewAI decides when the agent has
"finished" (produced a final answer vs. still calling tools) — an internal
termination check the application does not implement. The *outer*
termination — was the whole multi-stage job successful, should the pipeline
stop after this task failed — is not CrewAI's decision.

### Stays with the application, regardless

- **The outer sequencing** — which tasks run, in what order, whether task N
  even happens given task N-1's result. `Process.sequential` gives a fixed
  list; anything more conditional (branch, retry with a different agent,
  skip a stage) is application logic, not CrewAI's.
- **Relationship 4 (validation/guardrails)** — CrewAI's `output_pydantic`
  gives schema-shape checking for free (a real, if narrow, guardrail), but
  correctness, policy, or factuality checks are entirely on the
  application.
- **Relationship 6 (human interface)** — CrewAI has no native "pause and
  ask a human" primitive in the sense defined in the base document; if a
  system needs that, it is built entirely in the application layer,
  wrapping CrewAI calls.
- **Cross-task memory design decisions** — whether to trust CrewAI's
  automatic chaining/memory, or reconstruct context by hand, is an
  application-level choice CrewAI merely offers a default for.

### The pattern, stated plainly

CrewAI **absorbs the inner loop** — the call/response/dispatch cycle
*within a single task*, including tool use and (optionally) short-term
memory chaining and single-task termination. It does **not** absorb the
**outer loop** — cross-task workflow logic, validation policy, and
human-escalation path — those remain the application's job regardless of
how much of CrewAI's machinery is opted into.

A system built with exactly one Agent and one Task per Crew invocation
intentionally shrinks CrewAI's absorbed inner loop down to nearly nothing —
just relationship 1 (and an empty relationship 2, if no tools are given) —
while keeping every other responsibility (sequencing, memory, validation,
termination, human review) in application code, where it can be directly
enforced and audited.

### Tasks are nested control loops, not single steps

A `Task`'s execution is itself a complete, self-contained instance of the
inner loop — relationship 1 and relationship 2, repeated as many times as
needed, with its own relationship-5 termination check (has this Agent
produced a final answer, or does it want to call another tool?):

```
Task 1 begins
  -> call Agent A (relationship 1)
  -> response: tool call?  -> dispatch (relationship 2) -> result -> call again (relationship 1)
  -> response: tool call?  -> dispatch (relationship 2) -> result -> call again (relationship 1)
  -> response: final answer -> terminate (relationship 5, task-scoped)
Task 1 ends, produces Output 1
```

The Crew — the outer control loop — then takes that Task's output, chains
it into the next Task's context (relationship 3), and starts the next
Task's inner loop from scratch:

```
Crew (outer control loop)
  runs Task 1's inner loop to completion -> Output 1
  chains Output 1 into Task 2's context
  runs Task 2's inner loop to completion -> Output 2
  chains Output 2 into Task 3's context
  runs Task 3's inner loop to completion -> Output 3 (final)
```

So a Crew running `Process.sequential` is a control loop whose individual
steps are themselves complete control loops — nested, not flat. The outer
loop's "iterations" are entire Tasks; the inner loop's iterations are
individual LLM calls within one Task.

This sharpens the single-task-termination point above: CrewAI fully owns
*when a Task's inner loop stops*, but has no opinion on whether the *Crew*
itself is done, succeeded, or should keep going to the next Task. In
`Process.sequential`, CrewAI's answer to that outer question is simply
"always proceed to the next Task in the list, unconditionally" — there is
no outer termination *logic* in the interesting sense (no "should Task 3
even run, given what happened in Task 2") unless the application adds it.

This is exactly why a design that builds one Agent and one Task per Crew
invocation is a meaningful choice: it takes the "Crew runs multiple nested
inner loops sequentially" structure CrewAI offers, and collapses the outer
loop down to exactly one inner loop per `kickoff()` call — deliberately
moving the outer-loop decision (should the next stage even run, given this
stage's result) out of CrewAI's unconditional sequencing and into the
application's own orchestration code, where it can inspect, validate, and
branch on each stage's result before deciding to proceed.

## CrewAI core concepts

### Agent, Task, and Crew — what each one actually is

These three names map onto our vocabulary but are worth stating precisely,
since "Task" in particular is CrewAI-specific terminology with no 1:1 slot
in the general model.

- **Agent = *who*.** A reusable persona/capability definition: role, goal,
  backstory, tools, and llm choice. This is the full format contract from
  relationship 1, plus the tool schema (relationship 2's "what can be asked
  for"). An Agent can in principle be reused across multiple different
  Tasks — CrewAI does not require a 1:1 pairing, though many designs
  (including the reviewed project) happen to use one Agent per Task.
- **Task = *what, this time*.** A specific job — its own `description` and
  `expected_output` — bound to exactly one Agent that will execute it. A
  Task does not hold context in isolation: its `description` is the
  task-specific instructions (the "what to do this time" part of
  relationship 1's call), while whatever history the Crew chains in from
  prior tasks (relationship 3) is injected into that Task's execution at
  the point the Crew reaches it, not stored on the Task ahead of time.
- **Crew = the outer control loop.** The thing sequencing Tasks (via
  `Process`), auto-chaining each Task's output into the next Task's context,
  and returning a final result once every Task has completed.

```
Crew (the control loop / orchestrator, runs Process.sequential)
  |
  +-- Task 1 --uses--> Agent A  ->  produces Output 1
  |                                        |
  |                          (Crew auto-chains Output 1 into Task 2's context)
  |                                        v
  +-- Task 2 --uses--> Agent B  ->  produces Output 2
  |                                        |
  |                          (Crew auto-chains Output 2 into Task 3's context)
  |                                        v
  +-- Task 3 --uses--> Agent C  ->  produces Output 3 (final)
```

Task is best thought of as the unit that packages "this call's specific
instructions" together with "which Agent fulfills it" — in general
vocabulary, one concrete, independently referenceable instantiation of
relationship 1's Goal and Format Contract fields.

### `kickoff()`

`kickoff()` is the method that actually runs the loop described above — it
is CrewAI's entry point that turns a configured (but inert) `Crew` into
executed behavior. Nothing happens in CrewAI until it is called;
`Agent(...)`, `Task(...)`, and `Crew(...)` are all just configuration.

For a `Crew` with `Process.sequential` and tasks `[T1, T2, T3]`, calling
`crew.kickoff()`:

1. Takes T1, resolves its bound Agent, and builds the call (relationship 1)
   — persona + goal + task description + tool schema + any inputs passed to
   `kickoff()` itself.
2. Sends that call to the LLM, gets a response.
3. If the response requests a tool call (relationship 2), dispatches to the
   tool's executor, gets the result, feeds it back into the same task's
   ongoing context, and repeats — CrewAI's inner loop, running until the
   Agent produces a final answer (the task-scoped termination check,
   relationship 5).
4. Once T1 has a final answer, chains that output into T2's context
   (relationship 3, automatic memory chaining under `Process.sequential`).
5. Repeats steps 1-4 for T2, then T3.
6. Returns a `CrewOutput` once the last task completes — the final task's
   raw output, the parsed/validated result if `output_pydantic`/
   `output_json` was used, and each individual task's output along the way.

A Crew built with exactly one Agent and one Task per `kickoff()` call only
ever executes steps 1-3 once, for a single task, and returns immediately —
step 4 (automatic sequential chaining) cannot happen, since there is never
a second task in the list to chain into. If a pipeline needs six stages
built this way, the application calls `kickoff()` six separate times from
its own orchestration code, rather than once for a six-task Crew.

### `expected_output` vs. `output_pydantic`

Both describe "what the output should be," but they act at different
points in the call/response cycle and with very different force.

| | `expected_output` | `output_pydantic` |
|---|---|---|
| What it is | A sentence describing the goal shape | A real schema (types, required fields) |
| Where it acts | Relationship 1 — folded into the prompt sent to the reasoning core | Relationship 1 (constrains generation, typically via the provider's structured-output mechanism) *and* relationship 4 (validates the result) |
| Enforcement | None — advisory only | Mechanical — raises/fails if violated |
| Failure mode if ignored | Silent — the model may return prose instead of the shape wanted, with nothing to flag it | Loud — a `ValidationError`, catchable, something the control loop must handle |

`expected_output` is the weakest form of format contract named in the base
document — natural-language formatting instructions in the prompt — since
the reasoning core has to correctly interpret the instruction and nothing
enforces that it did. `output_pydantic` is a mechanically-enforced
guardrail: relationship 4's validation, sitting right after relationship 1's
response, before the control loop is allowed to trust it.

They are not redundant. `expected_output` can carry semantic intent a
schema cannot express (e.g. "identify only *material* unanswered
questions" — a schema can only say "a list of `ClarificationQuestion`
objects," never "and don't list trivial ones"). `output_pydantic`
guarantees the shape the response comes back in, or fails loudly. In
practice, both are typically used together: `expected_output` steers what
the model should try to produce; `output_pydantic` guarantees the shape it
comes back in.

## Open threads to go deeper on next

- Trace exactly what happens inside a multi-task `Process.sequential` crew
  when CrewAI's memory chaining is turned on.
- `Process.hierarchical` and how delegation actually works as a tool call
  under the hood.
- Where CrewAI's internal tool-call loop (inside relationship 1/2) has its
  own termination and retry behavior, and how that interacts with the
  application's outer termination logic.
