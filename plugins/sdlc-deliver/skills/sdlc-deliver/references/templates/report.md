# Report: <title>

**Status:** <delivered | stopped at Stage <N>: <reason>>
**Risk tier:** <tier>. **Gates fired:** <e.g. "G2 (approved <date>)", or "none after G1">

## Requirement → evidence

One row per acceptance check in spec.md. Evidence is a command and its result, a commit or a PR, never
an opinion.

| Check | Requirement | Evidence | Status |
|---|---|---|---|
| A1 | <R1> | `<command>` → <result>; <commit / PR> | <pass / fail> |

## Units and PRs

| Unit | Branch / PR | Merge commit | Verify command result |
|---|---|---|---|

## Findings

| Pass or dimension | Severity | Finding | Resolution |
|---|---|---|---|

## Metrics

- First-pass verify rate: <units whose verify command passed on the first worker run> / <units>
- Review rounds per PR: <per PR>
- Important findings per PR: <per PR>
- Owner wait time per gate: <gate: time from stop to reply>
- Elapsed time per stage: <stage: time>

## Learnings and loop

- Mistake-twice edits: <CLAUDE.md or skill diffs made in this delivery, or "none">
- New evals: <one per escaped defect, or "none">
- Follow-up intents: <paths of intent.md stubs, or "none">

## Deferred: requires a human

<Judgement calls, credentials or hardware outside the agent's reach. "None." if none.>
