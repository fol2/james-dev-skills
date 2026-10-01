# REVIEW.md (default)

Used for a pull request's review when the target repository has no `REVIEW.md` of its own. A
repository's own `REVIEW.md` replaces this file whole; copy this one there to start.

Each pass is a separate fresh-context subagent that did not write the code. The passes run in parallel
over the unit's diff, with spec.md and plan.md. A pass reports what it found; it does not fix anything.

## [R1] Bugs pass

Correctness against the plan and the spec: wrong results, unhandled inputs and boundaries (empty,
null, zero, one, many, very large), error paths, off-by-one errors, broken callers, state left behind,
and regressions in behaviour the diff did not mean to change. Run the code or its tests if that settles
a question faster than reading.

## [R2] Security pass

Input validation, injection (SQL, shell, path), secrets in code, logs or output, permission changes,
unsafe defaults, destructive operations without a guard, and dependencies added without need.

## [R3] Compliance pass

Against spec.md, plan.md and the repository's CLAUDE.md:
- every acceptance check the unit claims is actually implemented and tested;
- nothing outside the unit's scope was changed (scope creep is a finding);
- the house rules hold (language, naming, commit discipline, forbidden patterns);
- deviations from the plan are declared under "Plan deviations" in the PR body.

## [R4] Severity: Important or Nit

- **Important**: wrong behaviour, a security exposure, a missed acceptance check, or a broken house
  rule. **Blocks the merge.**
- **Nit**: style, naming, or a clearer alternative. Never blocks. Listed in the report.

Zero findings is a valid result: a pass does not invent a finding to justify itself. When unsure
whether something is Important, say why in one line and mark it Important.

## [R5] Skip rules

- The bugs and compliance passes never skip.
- The security pass skips only when the diff touches no executable code and no configuration (docs
  only). The skip and its reason go in the PR body.
- Nothing else skips, however small the diff.

## [R6] Re-review after a fix

Re-run the passes that raised an Important finding, every pass whose files the fix touched, and the
compliance pass. A pass that found nothing and whose files the fix did not touch is not re-run.

## [R7] Pass brief and output

Brief each pass with: this pass's section above, [R4], the unit's diff (or PR URL), spec.md, plan.md and
the repository's CLAUDE.md. Require this output:

```
PASS: <bugs | security | compliance>
VERDICT: <clear | blocked>
FINDINGS:
- [Important|Nit] <file>:<line> <what is wrong> -> <the fix it needs>
```

`blocked` if and only if at least one finding is Important.
