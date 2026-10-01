# Verification: commands, locked tests, the verifier and the loop

Verification replaces review volume. Most of what a panel of reviewers checked, a command can prove,
and a command does not get tired, agree with its neighbour or rationalise. Review is kept for what a
command cannot see.

## [V1] Feedback loop: one command per unit

- Every plan unit names one verification command, runnable from the repository root, that exits 0
  only when the unit is done. Usually the unit's tests; sometimes a script that checks the output.
- The worker runs it until it passes and puts the command and the tail of its passing output in the
  PR body (or the local merge message).
- The merge gate re-runs it on the PR head. A pass claimed in prose but not re-run does not count.
- A unit with no runnable check is a planning defect: it goes back to Stage 3, it is not built.

## [V2] Tests as the contract

For a bug, the test is written and committed **before** the fix, so the fix cannot weaken it.

1. The worker commits the failing test alone: `test(<slug>): failing test for <bug>`.
2. It runs the test, confirms it fails **for the stated reason** (not an import error or a typo), and
   records the commit sha and the failure line in plan.md's locked-test table.
3. Only then is the fix written, in later commits.
4. The merge gate runs, from the repository root:
   `python <plugin root>/scripts/locked_tests_check.py --test-commit <sha> --tests <file> [<file> ...]`
   - exit 0: every locked file is byte-identical to the test commit;
   - exit 1: a locked file was edited, deleted or renamed. The merge is blocked;
   - exit 2: the record is wrong (unknown commit, or a file absent from it). Fix the record, never the test.

Acceptance-check tests written before their code may be locked the same way. A locked test that is
itself wrong is unlocked only by the owner at a gate, never by a worker.

## [V3] Fresh-context verifier

One subagent that did not build anything, with **Bash and Read only**. Its brief: spec.md, the
acceptance-check list, and how to run the code. It:

- exercises the change the way a user would, then its two nearest neighbouring flows (the callers or
  features most likely to break);
- reports each check as pass or fail with the command and its output;
- never edits a file and never proposes a fix. A failure goes back to Stage 4 as a fix unit.

## [V4] Declared review dimensions

Chosen at Stage 2, before code exists, so a later skip cannot be a rationalisation. Rows are added,
never removed.

- **Core, always:** contract completeness; tests and edge cases; integration and regression.
- **Specialists, by rubric:**
  - security: touches authentication, permissions, input parsing, secrets, external I/O or a
    destructive operation;
  - performance: touches a query, a loop over data, a hot path or a scheduled job;
  - UX/UI: changes anything a user sees or clicks;
  - documentation: changes a public interface, a command, or user-facing docs;
  - architecture: adds a module or boundary, or spans more than one repository.

## [V5] Stage 6: verifying the whole

1. Run every acceptance check in spec.md. Record each command and its result in report.md's
   "Requirement → evidence" table as it runs.
2. Dispatch the verifier ([V3]).
3. Run each declared dimension ([V4]) as its own fresh subagent over the whole delivery diff, with
   spec.md and plan.md. Each returns findings with severities from REVIEW.md, or none. Zero findings is
   a valid result.
4. Important findings and failed checks become fix units, built by Stage 4 and reviewed by Stage 5;
   then re-run the checks, the verifier, and the dimensions that raised an Important finding or whose
   files the fix touched.

Stage 6 passes when every acceptance check passes, the verifier reports every check as pass, and no
Important finding is open.

## [V6] Mechanical before prose

A rule that must always hold is enforced by a command, hook or gate, not by a sentence:

- the locked-test check ([V2]);
- CI and the repository's pre-commit gates. Never `--no-verify`; after a hook runs, check `git log -1`
  to confirm the commit actually exists;
- no direct push to main from a delivery branch: merges go through the merge gate;
- the freeze check before any runtime step (gates.md [T5]);
- `set -o pipefail`, and read the step's own exit code: `cmd | tail` reports `tail`'s status, and a
  failed step then looks like a pass.

When a prose rule keeps being broken, the fix is to turn it into one of these.

## [V7] The loop: every delivery leaves the system smarter

- **Mistake twice.** A finding raised on two PRs in one delivery, or in two deliveries (search earlier
  reports in the artefact folders), becomes a CLAUDE.md or skill edit in the same delivery.
- **Evals.** An escaped defect, meaning one found after its merge, becomes a permanent eval: for
  analytics, a blind-question entry where the repository keeps one; for code, a regression test; for a
  skill, a `claude plugin eval` case.
- **Follow-ups** are written as `intent.md` stubs in the backlog or issue tracker, never as a running
  TODO document.
- **Metrics** go in report.md every time: first-pass verify rate, review rounds per PR, Important
  findings per PR, owner wait time per gate, elapsed time per stage.
