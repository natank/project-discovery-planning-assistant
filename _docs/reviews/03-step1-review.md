# Review — Agentic System Design, Step 1 (Stages and sequence)

**Reviewed document:** [`03-agentic-system-design.md`](../03-agentic-system-design.md), section "Step 1 — Stages and sequence"
**Reviewed at commit:** `2cbece8` (branch `docs/step1-stages-and-sequence`)
**Review date:** 2026-09-27
**Reviewer role:** Engineering manager
**Checked against:**
[`02-product-requirements.md`](../02-product-requirements.md) (FR-01–FR-16) and
[`agentic-systems-and-workflows.md`](../agentic-systems-and-workflows.md), design process step 1

## Verdict

**Nearly ready, with conditions.** The decomposition is sound. Five linear
stages is the right call, and the reasons for excluding intake, traceability,
export, and the cross-cutting FRs are well argued.

One design gap (finding 1) must be closed before step 2, because step 2's
"allowed tools" column is derived directly from step 1's "capabilities"
column. Finding 2 should be closed at the same time. The remaining findings
are consistency fixes that take about 30 minutes of editing.

## Findings

### Must fix before step 2

#### 1. The pause for the human between S1 and S2 is missing, and S1's capabilities are wrong

S2's input is described as "answers, skips, or deferrals from S1." Those
don't come from S1. They come from the idea owner, after S1's questions are
shown to them (FR-03). The sequence diagram draws S1 → S2 as a direct
handoff, which hides the one guaranteed point where the run stops and waits
for a person.

The base document also lists **"ask"** as a capability
(`agentic-systems-and-workflows.md`, step 1: "look up, compute, write,
ask"), yet S1 records "None."

**Decide one of these:**

- **(a)** S1 has the "ask" capability and owns the wait, or
- **(b)** S1 only produces the questions, and the diagram shows a separate
  `[Idea owner answers]` step between S1 and S2, whose mechanics are left to
  step 4.

**Recommendation:** option (b). It keeps S1 purely reasoning and fits how
the document already defers human-interface design to step 4. Either way,
the diagram has to show the pause.

#### 2. The inputs aren't strictly linear, and S5 is missing some

FR-11 says each backlog item must carry "unresolved risks or questions that
could block delivery," and the backlog must separate MVP work from future
work. That means S5 needs S3's risks and follow-on items, plus S2's open
questions, not just S4's requirements and stories.

The claim that "each stage's output is the next stage's required input" is
too strong. The *order* is linear, but the *inputs build up* from all
earlier stages.

**Action:**

- Correct S5's inputs.
- State explicitly that inputs build up across stages. This is the main
  thing step 4 has to design for memory.

### Should fix (consistency and auditability)

#### 3. S3 fails the "and" test without explanation

The base document says: "If describing a stage's output needs the word
'and,' it is probably two stages." S3 ("scope and risks") produces two
outputs. S4's bundling and S5's split both come with reasons, but S3's
bundling has none.

**Action:** either add a reason (risks are defined relative to the scope
boundary, so producing them in the same pass keeps them consistent) or split
the stage.

#### 4. The document contradicts itself about the fifth stage

- The text says "What remains is four stages" but five are defined.
- It says backlog generation "was considered and folded into a decision
  below."
- The following heading reads "Why backlog generation (FR-11) is **not**
  listed as a fifth stage here," and then the text adds it as S5.

It reads like an earlier draft that wasn't cleaned up.

**Action:**

- Merge S5 into the main stage table.
- Change "four" to "five."
- Replace the S5 story with a short reason for the split, placed next to
  the S4 bundling reason.

#### 5. The count of excluded categories is wrong

The exclusions paragraph says "Two categories" but three bullets follow.

#### 6. No column maps stages to FRs

For each stage, the base document asks "which requirements" it needs.
Coverage can't be checked at a glance without that mapping. Proposed
mapping:

| Stage | FRs |
|---|---|
| S1 Assess clarification needs | FR-02, FR-03 (plus FR-15 detection; see finding 8) |
| S2 Frame the problem | FR-04, FR-05 |
| S3 Propose scope and risks | FR-06, FR-07, FR-05 |
| S4 Specify requirements, stories, acceptance criteria | FR-08, FR-09, FR-10, FR-05 |
| S5 Plan delivery | FR-11 |

FR-05 (certainty labels) applies to S3's risks and S4's output too, not
only S2. The table currently mentions labels only for S2.

### Note and carry forward (fine to defer)

#### 7. FR-12 is only partly mechanical

Linking artifacts is mechanical. Assigning stable IDs and marking "missing or
uncertain links" is not: both have to be part of each stage's output format.

**Carry to:** step 2 output shapes.

#### 8. FR-15's "outside the product boundary" check has no owner

Deciding that input is outside the product boundary (for example, it isn't
a software idea) is reasoning work, and no stage is assigned to it. It's
most naturally part of S1's job.

**Action:** note it in S1's responsibility, or list it explicitly as
deferred.

#### 9. Review points between stages may add pauses

The product requirements say downstream planning shouldn't be presented as
final "when upstream ambiguity remains material." Together with FR-13, that
could require the idea owner to sign off (for example, on the framing before
scope is proposed). If so, the sequence gains more pauses.

**Action:** add this to "Open questions carried into later steps" (step 4).

#### 10. FR-13 regeneration needs re-runnable stages

Re-running "from whichever stage is affected" means every stage must be
able to re-run from the saved outputs of earlier stages.

**Carry to:** step 4, as a constraint on memory design.

#### 11. The promised comparison with the removed design is missing

The introduction says each step is compared with the removed technical
design, but step 1 doesn't include a comparison.

**Action:** either add a short comparison note to step 1, or change the
introduction to promise a single comparison at the end.

## What's good

- The exclusions have principled reasons, and FR-13 regeneration is
  correctly treated as a re-run the human starts, not a built-in loop.
- The decision on the S4 and S5 bundling (cross-checking a set of outputs
  vs. validating them in sequence) is well reasoned.
- Both open questions (running S1 again mid-sequence, and whether S4's
  bundling holds up) are the right ones, and they're assigned to the right
  later steps.
- The sequence rightly stays with the simplest shape the requirements
  allow, as the base document advises.

## Exit criteria for step 1

- [x] Finding 1 resolved: S1 capability decided, and the diagram shows where
      the idea owner answers.
- [x] Finding 2 resolved: S5 inputs corrected, and cumulative inputs stated.
- [x] Findings 3–6 addressed.
- [x] Findings 7–11 recorded as carry-forward items, or addressed.

## Re-review — 2026-09-28

**Reviewed at commit:** `4fe73e3` ("Address step 1 review findings")

**Verdict: Approved, with one correction to make before merge.**

| Finding | Resolution |
|---|---|
| 1 | Option (b) chosen. S1 keeps "None" for capabilities, and the diagram shows `[ Idea owner answers, skips, or defers each question ]` as a separate human-interface step whose mechanics are deferred to step 4. |
| 2 | S5's inputs now include S2's open questions and S3's risks and follow-ons. The Sequence section says order is linear but inputs accumulate, and calls this out as the main constraint on step 4's memory design. The diagram shows the accumulated inputs. |
| 3 | A reason for S3's bundling was added (risks are defined relative to the proposed scope boundary). |
| 4 | The stage table is merged, the text says "five stages," and the S4 and S5 reasons sit side by side. |
| 5 | Changed to "Three categories." |
| 6 | FRs column added, matching the proposed mapping, including FR-05 on S3 and S4 and FR-15 on S1. |
| 7 | The FR-12 bullet now carries ID assignment and "missing or uncertain" marking into step 2 output shapes. |
| 8 | Detecting input outside the product boundary is assigned to S1. |
| 9 | Added as an open question for step 4. |
| 10 | Added as an open question and a constraint on step 4 memory design. |
| 11 | A "Comparison with the removed technical design" subsection was added. See the correction below. |

### Correction required: the comparison mischaracterizes the removed design

The new comparison says the removed design "did not surface the idea-owner
pause between clarification and framing as an explicit step." The removed
`03-technical-design.md` (see `git show 64cdf6b:_docs/03-technical-design.md`)
contradicts this:

- It had explicit CLI commands `pdpa clarify` → `pdpa generate`, and a
  section headed "Stage 1: Create and assess input" in which the user
  answers, skips, or defers questions before generation.
- Its generation pipeline then ran clarification assessment *again*, as the
  first task inside the crew (`project context -> clarification assessment
  -> discovery framing -> ...`).
- It already allowed "a later generation [to] surface additional open
  questions" when they materially affect scope, risk, or acceptance
  criteria.

The accurate difference is this. The removed design *did* have the pause,
but placed it at a CLI command boundary outside the crew. It then repeated
clarification assessment inside the crew, which blurred the line between S1
and the pause rather than omitting the pause. Its policy of re-surfacing
open questions later is directly relevant to the first open question
(whether S1 can run again mid-sequence) and should be cited there.

The sixth quality-review stage claim is accurate: task 6, "Validate package
quality," run by a quality-reviewer agent.

### Minor (optional)

- The comparison section cites "finding 1 of this step's review," but the
  review file is not linked or committed. Commit
  `_docs/reviews/03-step1-review.md` alongside the design doc and link to
  it.
