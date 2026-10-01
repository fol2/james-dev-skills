# Local mode: repositories with no remote

Job folders, scratch repositories and anything without `origin` cannot open a pull request or run CI.
Local mode keeps every gate and every check; only the transport changes.

## [L1] When it applies

`git remote` prints nothing. Decide once at Stage 0 and record the mode in plan.md's Assumptions.
Never add a remote to make remote mode work.

## [L2] A branch stands in for a pull request

- The unit's branch `feat/<slug>-u<N>` is the pull request. Review reads `git diff main...<branch>`
  (three dots: what the branch changed since it left main).
- The "PR body" (verify command and output, plan deviations, skipped passes) goes in the merge
  commit's message.
- Merge with `git merge --no-ff <branch>` run in the main checkout, only when that checkout is on main
  and `git status` is clean. Never switch its branch to make the merge work. If it is dirty, stop and
  report: the uncommitted work belongs to someone.
- The report's "Units and PRs" table records the branch name and the merge commit.

## [L3] The repository's own checks stand in for CI

At the merge gate run the unit's verify command, then the repository's full test command (from its
CLAUDE.md, README or build file). Both must pass on the branch head before the merge, and the full test
command again on main after it.
