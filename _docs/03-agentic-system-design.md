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

_Pending._

## Step 2 — Reasoning-core configurations

_Pending._

## Step 3 — Capability contracts

_Pending._

## Step 4 — Control relationships

_Pending._

## Step 5 — Framework mapping

_Pending._
