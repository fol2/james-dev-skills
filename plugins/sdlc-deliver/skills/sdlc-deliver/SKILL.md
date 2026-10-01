---
name: sdlc-deliver
description: "AI-native delivery pipeline. Turns an idea, an issue or a contract into committed intent, spec and plan artefacts, builds each unit in a worktree against its own verification command, reviews each PR by REVIEW.md passes, verifies the whole with a fresh-context verifier, and feeds mistakes back into CLAUDE.md, skills and evals. The owner decides only at four risk-tiered gates (G1 intent and spec, G2 plan, G3 high-risk merge, G4 runtime or outward release). Trigger when the user says '/sdlc-deliver <path>', 'deliver this contract', 'deliver', 'execute this plan end to end' or 'run the full delivery cycle'. Needs a path to an idea, issue, contract or earlier artefact folder; refuses without one."
disable-model-invocation: true
---

# AI-native delivery

Deliver the work described at $ARGUMENTS: an idea, an issue, a contract, or the artefact folder (or an
artefact) of an earlier run.

**No input, no run.** If $ARGUMENTS is empty or names nothing readable, stop and reply only:
"No input provided. Usage: `/sdlc-deliver path/to/idea-issue-or-contract.md`".

## How it works

Agents do everything that needs no judgement; the owner decides only what does, at gates tiered by
risk ([T1], [T2]). Each stage commits an artefact the next stage reads, so a run survives a lost
context and git history is the audit trail. Done is proved by commands that pass ([V1], [V2]), not by
how many reviewers agreed. Every delivery feeds its mistakes back ([V7]).

Paths below are relative to this skill's base directory. The locked-test check is
`${CLAUDE_PLUGIN_ROOT}/scripts/locked_tests_check.py`; if that variable is not expanded, the plugin
root is the directory two levels above this skill's base directory.

| Reference | Holds |
|---|---|
| `references/gates.md` | risk tier [T1], gates G1–G4 [T2], questions [T3], stopping and resuming at a gate [T4], runtime and outward steps [T5] |
| `references/verification.md` | one command per unit [V1], locked tests [V2], the verifier [V3], declared dimensions [V4], Stage 6 [V5], mechanical before prose [V6], the loop [V7] |
| `references/REVIEW.default.md` | PR passes [R1] [R2] [R3], severity [R4], skips [R5], re-review [R6], pass brief [R7]; used only when the target repo has no `REVIEW.md` |
| `references/local-mode.md` | repos with no remote [L1], a branch as the PR [L2], local checks as CI [L3] |
| `references/templates/` | `intent.md`, `spec.md`, `plan.md`, `report.md` |

## Integrity rule

Only a fix clears a finding. An Important finding clears when the code is fixed and the pass that
raised it re-reviews it ([R6]); a failing check is fixed in code, never explained away in the report.
No agent reviews or approves work it wrote, and you, the orchestrator, never clear a finding or
overturn a verdict yourself. If you find yourself arguing that a rule does not apply to this case,
that argument is the signal to follow it.

## Stage 0: Set up

1. Read the input in full and classify it: idea, issue, contract, or earlier artefacts (resume).
2. Choose a kebab-case slug. The artefact folder is the target repo's `docs/delivery/<slug>/`, or, for
   analytics work in a job folder, that job folder.
3. Choose the mode: `git remote` prints nothing → local mode [L1]; otherwise remote mode with `gh`.
4. Load the house rules: the target repo's CLAUDE.md, and its `REVIEW.md`, else
   `references/REVIEW.default.md`.
5. Make a worktree for the artefacts (`/ce-worktree`, or `git worktree add <path> -b delivery/<slug>`).
   All writes happen in worktrees. The main checkout never changes branch.

**Resume.** When the input is an artefact folder, or an artefact whose status line reads
`awaiting G<n>`, follow [T4]: re-read every artefact from disk, record the owner's reply, and continue
from the stage after the gate. Never redo a stage whose artefact is accepted.

Report progress only at stage transitions, one line each: "Stage N complete: <artefact>."

## Stage 1: Intent → `intent.md`

From `references/templates/intent.md`: the originator's problem, the outcome wanted, constraints and
non-goals. Quote the originator's own words. Anything only the owner can decide goes under "Open
questions", each with your proposed answer, so "accept" is a valid reply.

## Stage 2: Spec → `spec.md`

Requirements and design in one pass, from `references/templates/spec.md`, with the target repo's
CLAUDE.md and any relevant skills loaded. Three parts are load-bearing:

1. **Risk tier** by the rubric [T1], quoting the line that decided it.
2. **Review dimensions**: the three core dimensions plus the specialists the rubric selects [V4].
3. **Acceptance checks**: every requirement as a command with its expected result.

A step in the input that an agent cannot perform becomes an executable equivalent: manual QA becomes
automated tests, "observe production for N days" becomes time-simulation tests. A judgement call (a
stakeholder sign-off, a legal or compliance approval) stays human: it becomes a gate item or a
"Deferred: requires a human" entry, never a reviewer's verdict.

Commit `intent.md` and `spec.md` by path, then **G1** [T2]. It does not fire when the input was an
already-approved contract or issue; record why on both status lines.

## Stage 3: Plan → `plan.md`

Explore read-only first. Then write `plan.md` from `references/templates/plan.md`:
- units in order, with the files each touches;
- one verification command per unit [V1];
- the locked tests for each bug unit [V2];
- risks;
- which units can run in parallel.

Use `/ce-plan` as the engine when there are more than three units or the code is unfamiliar, giving it
the template as the output shape. Otherwise write the plan directly. Either way the engine runs under
[T3]: it decides, and records its assumptions instead of asking.

Then run one fresh-context **plan check**: a subagent that reads only spec.md and plan.md and answers
two questions. Does every acceptance check map to a unit? Does every unit have a runnable verification
command? Fix the plan until both answers are yes, then commit it.

**G2** [T2] fires for medium and high risk. A low-risk plan records `G2 not required (low risk)` and
the run continues.

## Stage 4: Build and verify, per unit

In plan order. Parallel groups run together.

1. A worker subagent, using `/ce-work` as the engine, builds the unit in its own worktree on
   `feat/<slug>-u<N>`, branched from the current main.
2. **Bug unit:** the worker first commits the failing test on its own and confirms it fails for the
   stated reason. It records the sha in plan.md's locked-test table [V2]. Only then does it write the
   fix.
3. The worker runs the unit's verification command until it passes, then opens a PR (remote mode) or
   leaves the branch ready (local mode, [L2]). The command and the tail of its passing output go in the
   PR body.
4. Worker rules:
   - no `git stash`;
   - any deviation from the plan goes under "Plan deviations" in the PR body;
   - UI work uses `/frontend-design` (`/allianz-one-vis` for Allianz-branded output).

No owner prompt fires during the build; questions follow [T3]. Fixes from Stage 5 or 6 are built the
same way.

## Stage 5: Review, per PR

Run the repo's REVIEW.md passes ([R1] bugs, [R2] security, [R3] compliance) on the unit's diff. Each
pass is a fresh subagent that did not write the code, all dispatched in parallel and briefed per [R7].
Only Important findings block [R4]. A pass skips only under [R5]. After a fix, re-review per [R6].

**Merge gate.** Mechanical and in this order; every step must pass:
1. Re-run the unit's verification command on the PR head.
2. For a bug unit, run
   `python <plugin root>/scripts/locked_tests_check.py --test-commit <sha> --tests <files>`.
   It must exit 0 [V2].
3. CI is green (remote mode), or the repo's own test command passes (local mode, [L3]).
4. No Important finding is open.
5. **G3** [T2]: high risk only.

Then merge: `gh pr merge --squash --delete-branch` in remote mode, or the local merge [L2].

## Stage 6: Verify the whole

Run [V5]:
1. Run the full acceptance-check list.
2. Dispatch the fresh-context verifier [V3].
3. Run each dimension spec.md declared, as a fresh subagent over the whole delivery diff.
   `/ce-code-review` may be the engine for integration and regression.

Important findings and failed checks go back to Stage 4 as fix units. Record each check's evidence in
report.md as it runs.

## Stage 7: Release

In remote mode, push what has merged. In local mode, confirm that main holds every unit. A
runtime-affecting or outward-facing step (a deploy, a scheduled job, production data, publication)
passes the freeze check and **G4** first [T5], whatever the plan says. Destructive steps are high risk
by [T1] and need G4 even inside an approved plan.

## Stage 8: Learn → `report.md`

Complete `report.md` from `references/templates/report.md`:
- every requirement mapped to its evidence;
- the metrics;
- the loop actions [V7]: mistake-twice edits, an eval for each escaped defect, and follow-ups as
  intent stubs.

Run `/ce-compound` only when the delivery produced a learning that the code, tests and docs do not
already record. Commit and merge the report.

**Housekeeping:**
1. Remove the delivery worktrees.
2. Delete the merged delivery branches.
3. `git fetch --prune` (remote mode).
4. Confirm that only the main worktree remains, that the main checkout is on the branch it started on,
   and that `git status` is clean.

## Stopping

- At a gate, stop exactly as [T4] says. Never fire a gate the tier does not require.
- A blocker no gate covers stops the run: a missing credential, a broken environment, or the same
  finding returning a third time. Commit what exists, set report.md's status to
  `stopped at Stage <N>: <reason>`, and report.
- Errors you can fix stay within the run:
  - a worker that cannot push: check the branch and the remote, then re-dispatch it;
  - red CI: read the log, then dispatch a fix unit;
  - a merge conflict: rebase on the latest main and re-run the verification command.

## House rules this skill never relaxes

- Every artefact is in UK English.
- Commits are path-bounded (`git commit -- <paths>`). Never use `--no-verify`, and after a hook runs
  confirm with `git log -1` that the commit exists.
- Never branch or check out in the main worktree.
- No destructive action without the owner's approval at a gate.
- Use `set -o pipefail` and read the step's own exit code [V6].
