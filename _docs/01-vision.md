# Project Discovery and Planning Assistant — Vision

**Status:** Draft  
**Decision horizon:** Product and user outcomes only; implementation choices are
deferred to the technical design.

## Vision statement

Enable people with software ideas to move from an incomplete concept to a
shared, actionable project direction by guiding discovery, clarifying needs,
shaping a focused first release, and organizing the work required to deliver
it.

## The problem

Early software ideas are often expressed as a short description, a collection
of assumptions, or a desired feature rather than a well-understood problem.
Turning that starting point into a useful plan requires several kinds of
thinking:

- understanding who has the problem and in what context;
- distinguishing the underlying need from proposed features;
- identifying unanswered questions and risky assumptions;
- deciding what belongs in a valuable first release;
- translating outcomes into requirements and testable acceptance criteria; and
- organizing the work so that another person can begin implementation.

This work is commonly inconsistent, time-consuming, and difficult to review.
Important decisions may remain implicit, while plans become either too vague to
act on or too detailed before the problem is understood.

## Target users

### Primary user: idea owner

Someone with a software idea who needs help turning it into a clearer product
direction. They may be a developer, founder, product manager, analyst, or
student. They can explain the initial idea but may not know which questions
must be answered before implementation begins.

### Secondary user: delivery collaborator

A developer, designer, or project contributor who needs a shared understanding
of the problem, intended users, scope, requirements, and first implementation
steps before committing to work.

### Beneficiary: reviewer or stakeholder

Someone who needs to assess whether the proposed problem, scope, and plan are
coherent without reconstructing the discovery process from scattered notes.

## Desired user outcome

After using the assistant, the idea owner should have a credible, reviewable
discovery package that answers:

1. What problem are we solving?
2. Who experiences it and in what situation?
3. What outcome would users and stakeholders consider valuable?
4. What assumptions and uncertainties still need validation?
5. What is the smallest meaningful first release?
6. What capabilities and behaviors must that release provide?
7. How can the work be divided into actionable delivery items?

The package should make uncertainty visible rather than presenting guesses as
facts. It should help people make decisions, not replace their ownership of
those decisions.

## Guiding principles

- **Problem before solution:** understand the user problem before committing to
  features or technology.
- **Progressive clarification:** ask or surface the most valuable questions
  before expanding the plan.
- **Evidence and assumptions are distinct:** clearly label what is known,
  inferred, or still unvalidated.
- **Smallest valuable scope:** favor a coherent first release over a broad
  collection of partially defined features.
- **Traceable reasoning:** connect goals to requirements, requirements to
  stories, and stories to acceptance criteria.
- **Human-owned decisions:** recommendations remain reviewable and editable by
  the idea owner.
- **Useful artifacts over conversation alone:** produce documents that can be
  shared, revised, and used for delivery.

## Conceptual experience

The experience should support the following stages:

1. **Describe** — the user provides an initial idea in natural language and,
   when available, context such as intended audience, constraints, or desired
   outcome.
2. **Clarify** — the assistant identifies ambiguity, asks focused questions,
   and establishes a shared understanding of the problem.
3. **Discover** — the assistant frames users, situations, needs, outcomes,
   assumptions, and risks.
4. **Shape** — the assistant proposes a focused first release and distinguishes
   essential capabilities from later opportunities.
5. **Specify** — the assistant expresses the proposed behavior as requirements,
   user stories, and acceptance criteria.
6. **Plan** — the assistant organizes the work into a sequenced backlog with
   dependencies, risks, and validation steps.
7. **Review** — the user inspects, corrects, accepts, or revises the resulting
   package before it is treated as a delivery baseline.

These stages describe the desired product experience, not a required internal
workflow.

## Core outputs

The assistant should be able to produce a coherent set of artifacts containing:

- a concise problem and opportunity statement;
- primary users, stakeholders, and relevant usage context;
- desired outcomes and indicators of value;
- assumptions, open questions, and risks;
- a proposed MVP boundary and explicit non-goals;
- product requirements and user stories;
- acceptance criteria that describe observable behavior;
- a prioritized, dependency-aware implementation backlog; and
- a summary of decisions requiring human confirmation.

The exact format and storage mechanism will be defined later.

## Scope for the initial vision

The initial product is focused on software-project discovery and planning from
an idea supplied by a user. It should support iterative refinement of one
project at a time and should make the generated reasoning and artifacts easy
to review.

The vision does not assume access to private organizational systems, a
particular research corpus, or a particular delivery platform. Those
integration and infrastructure questions belong in the product requirements
and technical design.

## Non-goals

The assistant is not intended to:

- autonomously approve a project or commit an organization to a plan;
- replace domain experts, user research, product judgment, or engineering
  review;
- guarantee that a proposed idea is commercially viable;
- generate a complete production system from a short prompt;
- make irreversible changes to external systems;
- conceal uncertainty behind confident-sounding output; or
- optimize a plan for scale, cost, or organizational policy without relevant
  input.

## Early success indicators

The vision will be considered validated when representative users can:

- start with a vague but realistic software idea;
- recognize their problem and intended users in the resulting discovery
  summary;
- identify which assumptions and questions remain unresolved;
- understand why the proposed MVP scope was selected;
- hand the requirements and backlog to a delivery collaborator with minimal
  re-explanation; and
- revise the output when the assistant makes an incorrect assumption.

Quantitative thresholds, quality criteria, and testable acceptance conditions
will be defined in the product requirements document.

## Assumptions to validate

- Users will provide enough context for meaningful clarification, or will
  answer focused follow-up questions.
- A structured discovery package is more useful than an unstructured answer.
- Users value transparent assumptions and review points.
- A single project context is an appropriate initial boundary.
- The resulting artifacts can be evaluated for completeness, coherence, and
  actionability by a human reviewer.

## Risks and uncertainties

- The assistant may produce plausible but incorrect interpretations of the
  idea.
- Generic planning advice may not reflect the user's domain or constraints.
- Excessive questioning may make the experience feel slow or burdensome.
- Generated requirements may appear precise without being sufficiently
  validated.
- Different users may expect different levels of detail from the same input.
- A useful workflow may require external context that is unavailable in the
  initial version.

These risks should become explicit requirements, safeguards, or backlog items
rather than being hidden in the implementation.

## Questions for the product requirements stage

- What is the smallest input a user must provide to begin?
- Which clarification questions are essential, and when should they be asked?
- Which outputs are mandatory for the first release?
- How does a user review, edit, accept, or reject an output?
- What makes a requirement or backlog item sufficiently actionable?
- Which quality dimensions should be scored or checked?
- What should happen when information is missing, contradictory, or uncertain?
- What is the intended level of domain-specific research?
- Which project artifact formats and persistence behavior are needed initially?
