"""Locked-test check: a fix may not weaken the test that proves it.

    python locked_tests_check.py --test-commit <sha> --tests <file> [<file> ...] [--head HEAD] [--repo .]

The failing test for a bug is committed before the fix. At the merge gate this compares every locked
file between that commit and the head being merged:

    exit 0  every locked file is unchanged since the test commit
    exit 1  a locked file was edited, deleted or renamed: block the merge
    exit 2  the record is wrong: the test commit is unknown, or a locked file is absent from it

The check is mechanical on purpose. Whether an edit to a test "only tidies it" is exactly the
judgement a reviewer can be talked out of; a diff cannot.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

OK, CHANGED, BAD_RECORD = 0, 1, 2


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def resolve(repo: Path, ref: str) -> str | None:
    out = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else None


def present_at(repo: Path, commit: str, path: str) -> bool:
    return git(repo, "cat-file", "-e", f"{commit}:{path}").returncode == 0


def check(repo: Path, test_commit: str, tests: list[str], head: str = "HEAD") -> tuple[int, list[str]]:
    """Return (exit code, report lines)."""
    if not tests:
        return BAD_RECORD, ["LOCKED-TESTS RECORD ERROR: no locked test files given"]
    base = resolve(repo, test_commit)
    if base is None:
        return BAD_RECORD, [f"LOCKED-TESTS RECORD ERROR: test commit {test_commit!r} is not a commit in {repo}"]
    tip = resolve(repo, head)
    if tip is None:
        return BAD_RECORD, [f"LOCKED-TESTS RECORD ERROR: head {head!r} is not a commit in {repo}"]
    paths = [Path(t).as_posix() for t in tests]
    absent = [p for p in paths if not present_at(repo, base, p)]
    if absent:
        return BAD_RECORD, [f"LOCKED-TESTS RECORD ERROR: not in test commit {base[:12]}: {', '.join(absent)}"]

    # --no-renames: a renamed locked file must read as a deletion of the locked path, whatever the
    # caller's diff.renames setting. Pathspecs are literal, so a test path holding glob characters
    # still names exactly one file.
    diff = git(repo, "--literal-pathspecs", "diff", "--no-renames", "--name-status", base, tip, "--", *paths)
    if diff.returncode != 0:
        return BAD_RECORD, [f"LOCKED-TESTS RECORD ERROR: git diff failed: {diff.stderr.strip()}"]
    changes = [line for line in diff.stdout.splitlines() if line.strip()]
    if changes:
        lines = [f"LOCKED-TESTS FAIL: {len(changes)} locked file(s) changed between {base[:12]} and {tip[:12]}"]
        lines += [f"  {line}" for line in changes]
        lines.append("A fix may not edit its locked test. Revert the test, or ask the owner to unlock it at a gate.")
        return CHANGED, lines
    return OK, [f"LOCKED-TESTS OK: {len(paths)} locked file(s) unchanged between {base[:12]} and {tip[:12]}"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--test-commit", required=True, help="the commit that added the failing test")
    ap.add_argument("--tests", nargs="+", required=True, help="locked test files, relative to the repo root")
    ap.add_argument("--head", default="HEAD", help="the commit being merged (default HEAD)")
    ap.add_argument("--repo", type=Path, default=Path("."), help="repository root (default .)")
    args = ap.parse_args(argv)
    code, lines = check(args.repo, args.test_commit, args.tests, args.head)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
