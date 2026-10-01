# Gates: risk, owner decisions, questions, runtime

One person usually holds every human role (product owner, tech lead, code owner, release manager),
so the gates are few, tiered by risk and batched. Everything between them is the agents' job.

## [T1] Risk tier rubric

Assigned at Stage 2 and written into spec.md with the line that decided it. **Never lowered later**:
new evidence can only raise it. When two lines apply, the higher wins.

- **High**: runtime-affecting (DDL or DML on production or scheduled objects, refresh or deploy
  scripts, scheduled jobs); touches production data; touches credentials; destructive (deletes,
  drops, overwrites, history rewrites); outward-facing (a new repository, a visibility change,
  publication outside the owner's own repositories).
- **Medium**: changes a shared interface (anything imported, called or read by another repository,
  skill or team), a gate or test harness, or more than one repository.
- **Low**: everything else.

The tier decides which of G2, G3 and G4 fire. It never reduces verification.

## [T2] Owner gates G1–G4

| Gate | Fires for | The owner decides |
|---|---|---|
| **G1** | every input except an already-approved contract or issue | accept intent.md and spec.md together, including the tier and the open questions' proposed answers |
| **G2** | medium and high | approve plan.md |
| **G3** | high | approve the merge of a reviewed PR; independent PRs are presented together in one batch |
| **G4** | any runtime or outward-facing release step, whatever the tier | approve that step |

"Already approved" needs evidence on the input itself: a status line saying the owner approved it, or
an issue the owner labelled ready for an agent. A contract the owner merely supplied is not approved.
When G1 does not fire, record `G1 not required: <the evidence>` on both status lines.

## [T3] Questions go to the owner only at a gate

Between gates, decide, write the decision and its reason under "Assumptions" in the current artefact,
and carry on. An assumption the owner would want to overturn is listed again at the next gate. A
question no gate covers is a sign the spec was incomplete: fold it into the next gate's summary, or
into the report when no gate remains, rather than stopping for it.

Stopping without a gate is for blockers only: a missing credential, a broken environment, or the same
finding returning a third time. That is a stop with a report, not a question.

## [T4] How a gate stops and resumes

**Stop.**
1. Commit every artefact written so far, by path.
2. Set the gated artefact's status line to `awaiting G<n>`.
3. Print one block, then end the turn:

```
GATE G<n>: awaiting the owner
Artefacts: <paths>
Decide: <the decision, one line>
Proposed: <your recommendation, and what happens next if accepted>
Reply: "G<n> OK", or the amendments
```

In an interactive session the block may be asked through the question tool instead, with "approve"
as the first option. Never fire a gate the tier does not require, and never fire one twice.

**Resume.** On the owner's reply in the same session, or when the skill is re-invoked on the artefact
folder or on the artefact that is `awaiting G<n>`:
1. Re-read every artefact from disk; the conversation may have been compacted.
2. Record the approval on the status line: `approved at G<n>, <date> ("<the owner's words>")`, or
   apply the amendments and re-present the gate.
3. Commit, and continue from the stage after the gate. Never redo an accepted stage.

## [T5] Runtime and outward-facing steps

Before any runtime-affecting or outward-facing step, even one an approved plan lists:

1. **Freeze check.** `date +%u` printing `4` means Thursday: no runtime change. Then apply the target
   repository's own freeze rule as its CLAUDE.md states it (for example, "no runtime change while a
   refresh cycle is running"). A freeze blocks the step unless the owner waives that specific step;
   record the waiver in the report.
2. **G4.** The owner approves the step itself. Approval of the plan is not approval to execute a
   destructive or outward step.
3. Read the step's own exit code, never a pipe's (verification.md [V6]).
