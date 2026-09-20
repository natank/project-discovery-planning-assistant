# CrewAI Demonstration Project — Kickoff

## Purpose

This workspace will be used to explore the CrewAI framework by building a small,
complete, end-to-end demonstration. The project should be understandable to
someone encountering CrewAI for the first time and realistic enough to show the
decisions involved in turning an idea into a working agentic application.

The project is intentionally documentation-led. We will first define the
problem and desired product without choosing a framework or implementation
technique. We will then translate that product definition into a technical
design and an incremental delivery plan, and only then implement it with
CrewAI.

## Intent

The demonstration should:

- provide a simple, useful user-facing workflow;
- show how multiple agents, roles, tasks, and outputs can work together;
- make the orchestration and handoffs easy to inspect;
- include the infrastructure and environment configuration needed to run it
  locally;
- establish a clear path from product intent to executable software; and
- be small enough to understand, test, and iterate within this workspace.

The goal is not to build a production-grade autonomous system. The goal is to
learn the framework through a coherent example while preserving sound
engineering practices: explicit requirements, reproducible setup, observable
execution, safe handling of configuration, and verifiable outcomes.

## Working approach

We will use the following sequence:

1. **Kickoff** — capture the intent, scope, workflow, and documentation
   standards for the project. This document is the starting point.
2. **Vision** — describe the problem, users, value, desired experience, and
   boundaries in implementation-agnostic terms.
3. **Product requirements** — derive capabilities and behavior from the vision,
   including personas, user stories, acceptance criteria, non-functional
   requirements, and a prioritized backlog.
4. **Technical design** — select the implementation approach and describe the
   system architecture, CrewAI concepts, integrations, data flow, configuration,
   observability, testing strategy, and operational considerations.
5. **Delivery plan** — divide the design into implementable stories with
   dependencies, sequencing, definition of done, and validation steps.
6. **Implementation** — build the smallest useful vertical slice first, then
   expand through the planned stories.
7. **Validation and learning** — run the demonstration end to end, compare the
   result with the requirements, document framework-specific lessons, and
   record follow-up improvements.

Each stage should refine the previous stage rather than silently changing it.
Material changes in scope or behavior should be recorded as decisions in the
relevant document.

## Planned documentation set

All project-development documents belong in `_docs`:

| Document | Purpose |
| --- | --- |
| `00-kickoff.md` | Project intent, workflow, scope boundaries, and document conventions |
| `01-vision.md` | Implementation-agnostic product vision |
| `02-product-requirements.md` | Requirements, user stories, acceptance criteria, and backlog |
| `03-technical-design.md` | Architecture and implementation design, including CrewAI mapping |
| `04-delivery-plan.md` | Story-level execution plan, sequencing, and validation |
| `05-lessons-learned.md` | Findings from implementation and end-to-end use |

Files may be added when they clarify a substantial decision or concern, but the
numbered documents above are the canonical project narrative.

## Scope boundaries

### In scope

- one focused end-to-end use case;
- local development and demonstration setup;
- environment-variable and secret-handling conventions;
- the minimum infrastructure required to run the application;
- agent, task, crew, and process design needed by the use case;
- deterministic or mockable tests for important behavior;
- a runnable demonstration path and concise operating instructions; and
- documentation of trade-offs and framework lessons.

### Out of scope unless later approved

- production deployment and high availability;
- unrestricted autonomous actions in external systems;
- handling real user secrets or sensitive production data;
- broad benchmarking across many agent frameworks;
- building a general-purpose agent platform; and
- optimizing for scale before the basic workflow is reliable.

## Definition of a successful demonstration

The project is successful when a new contributor can follow the documented
setup, provide the required configuration, run the end-to-end workflow, inspect
the resulting output and meaningful execution trace, and understand how the
result maps back to the product requirements. The implementation should expose
the value of CrewAI without making the demonstration depend on undocumented
local state or manual intervention.

## Selected use case

The project will build a **Project Discovery and Planning Assistant**. A user
will describe a software idea, and the system will help clarify the problem,
identify target users, draft product requirements, propose a focused MVP, and
produce an implementation backlog with risks and acceptance criteria.

This use case is the foundation for the vision document. It is a good fit for
the demonstration because the workflow naturally separates into research,
product, requirements, planning, and review responsibilities while producing
an inspectable set of project artifacts.

## Working agreements

- Product documents remain implementation agnostic until the technical-design
  stage.
- Requirements should describe observable behavior, not internal classes or
  framework APIs.
- Every planned story has a clear outcome and a validation method.
- Configuration examples may use placeholders, but secrets must never be
  committed.
- Prefer a small vertical slice over broad, unfinished infrastructure.
- Record important assumptions and decisions where they are made.
- Keep the demonstration reproducible from a clean checkout.

## Decision record

- **Decision:** Use the Project Discovery and Planning Assistant as the
  demonstration use case.
- **Status:** Accepted
- **Date:** 2026-09-20
- **Rationale:** It provides a clear end-to-end workflow with multiple
  complementary responsibilities and produces outputs that can be evaluated
  against explicit requirements.

## Open decisions for the next stage

The vision document should resolve:

- the problem being solved and why an agentic workflow is appropriate;
- the primary user and other relevant stakeholders;
- the expected input and output;
- the boundaries of agent autonomy and human involvement;
- the quality bar for a useful result; and
- the assumptions, risks, and deliberate non-goals.
