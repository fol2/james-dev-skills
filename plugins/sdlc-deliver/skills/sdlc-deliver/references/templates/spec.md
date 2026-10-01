# Spec: <title>

Reads `intent.md`. **Status:** draft, awaiting G1
<!-- Same status values as intent.md; the two are accepted together at G1. -->

## Risk tier

**Tier:** <low | medium | high>
**Rubric line:** <the line of gates.md [T1] that decided it, quoted>
The tier is fixed here and never lowered later. When two lines apply, the higher one wins.

## Requirements

<Numbered. Each one traceable to a line of intent.md.>

## Design

<The shape of the change: modules, interfaces, data, and why this shape over the obvious alternative.>

## Review dimensions

Chosen now, before any code exists, by verification.md [V4]. Rows may be added later, never removed.

| Dimension | Selected | Reason |
|---|---|---|
| Contract completeness | core | always runs |
| Tests and edge cases | core | always runs |
| Integration and regression | core | always runs |
| Security | <yes / no> | <rubric reason> |
| Performance | <yes / no> | <rubric reason> |
| UX/UI | <yes / no> | <rubric reason> |
| Documentation | <yes / no> | <rubric reason> |
| Architecture | <yes / no> | <rubric reason> |

## Acceptance checks

Every requirement as an executable check. A check without a command is a spec defect.

| # | Requirement | Command | Expected result |
|---|---|---|---|
| A1 | <R1> | `<command>` | <exit 0 / exact output> |

## Assumptions

<Decisions taken without the owner under gates.md [T3], each with its reason. "None." if none.>
