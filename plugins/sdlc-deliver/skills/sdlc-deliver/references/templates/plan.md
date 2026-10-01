# Plan: <title>

Reads `spec.md`. **Risk tier:** <low | medium | high> (from spec.md, never lowered).
**Status:** draft
<!-- Status values, exactly one:
  draft
  awaiting G2
  approved at G2, <YYYY-MM-DD> ("<the owner's words>")
  G2 not required (low risk)
-->

## Units

One verification command per unit (verification.md [V1]). A unit without one goes back to planning.

| # | Unit | Files | Verify command | Covers checks | Depends on |
|---|---|---|---|---|---|
| U1 | <name> | `<paths>` | `<command>` | <A1, A2> | <none / U-n> |

## Parallel groups

<Which units can be built at the same time, e.g. "U1 and U2 together; U3 after both". "None: strictly sequential." is valid.>

## Locked tests

Bug units commit the failing test first (verification.md [V2]). The test commit is filled in at build
time, before the fix is written.

| Unit | Test file(s) | Fails for | Test commit |
|---|---|---|---|
| <U-n> | `<path>` | <the stated reason it must fail> | <sha, filled at build> |

## Risks

<What could go wrong, and the mitigation for each.>

## Assumptions

<Decisions taken under gates.md [T3] while planning. "None." if none.>
