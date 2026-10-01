"""U3: the locked-test check on real throwaway git repositories.

    python -m pytest plugins/sdlc-deliver/tests/test_locked_tests_check.py

Cases from the plan: an untouched test passes; an edited, deleted or renamed locked test fails with a
non-zero exit; a non-test edit passes; a missing test commit exits 2.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "locked_tests_check.py"
TEST_FILE = "tests/test_calc.py"


def git(repo: Path, *args: str) -> str:
    # A fixture repository: an empty hooks directory keeps the caller's global hooks out of it.
    hooks = repo / ".nohooks"
    hooks.mkdir(exist_ok=True)
    out = subprocess.run(["git", "-C", str(repo), "-c", f"core.hooksPath={hooks}", "-c", "user.name=t",
                          "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false", *args],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), *args],
                          capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path: Path) -> tuple[Path, str]:
    """A repo with code, then a commit adding the failing test, then the fix. Returns (repo, test sha)."""
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "calc.py").write_text("def add(a, b):\n    return a - b\n")
    git(tmp_path, "add", "calc.py")
    git(tmp_path, "commit", "-q", "-m", "code")
    (tmp_path / "tests").mkdir()
    (tmp_path / TEST_FILE).write_text("from calc import add\n\ndef test_add():\n    assert add(2, 2) == 4\n")
    git(tmp_path, "add", TEST_FILE)
    git(tmp_path, "commit", "-q", "-m", "test: failing test for add")
    sha = git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "calc.py").write_text("def add(a, b):\n    return a + b\n")
    git(tmp_path, "commit", "-q", "-am", "fix: add")
    return tmp_path, sha


def test_untouched_locked_test_passes(repo):
    path, sha = repo
    res = run(path, "--test-commit", sha, "--tests", TEST_FILE)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "LOCKED-TESTS OK" in res.stdout


def test_non_test_edit_passes(repo):
    path, sha = repo
    (path / "calc.py").write_text("def add(a, b):\n    return b + a\n")
    git(path, "commit", "-q", "-am", "refactor")
    assert run(path, "--test-commit", sha, "--tests", TEST_FILE).returncode == 0


def test_edited_locked_test_fails(repo):
    path, sha = repo
    (path / TEST_FILE).write_text("from calc import add\n\ndef test_add():\n    assert add(2, 2) == 0\n")
    git(path, "commit", "-q", "-am", "weaken the test")
    res = run(path, "--test-commit", sha, "--tests", TEST_FILE)
    assert res.returncode == 1, res.stdout
    assert "LOCKED-TESTS FAIL" in res.stdout and f"M\t{TEST_FILE}" in res.stdout


def test_deleted_locked_test_fails(repo):
    path, sha = repo
    git(path, "rm", "-q", TEST_FILE)
    git(path, "commit", "-q", "-m", "drop the test")
    res = run(path, "--test-commit", sha, "--tests", TEST_FILE)
    assert res.returncode == 1 and f"D\t{TEST_FILE}" in res.stdout, res.stdout


def test_renamed_locked_test_fails(repo):
    path, sha = repo
    git(path, "mv", TEST_FILE, "tests/test_calc_old.py")
    git(path, "commit", "-q", "-m", "rename the test")
    res = run(path, "--test-commit", sha, "--tests", TEST_FILE)
    assert res.returncode == 1 and f"D\t{TEST_FILE}" in res.stdout, res.stdout


def test_missing_test_commit_exits_2(repo):
    path, _ = repo
    res = run(path, "--test-commit", "0" * 40, "--tests", TEST_FILE)
    assert res.returncode == 2 and "RECORD ERROR" in res.stdout, res.stdout


def test_locked_file_absent_from_test_commit_exits_2(repo):
    path, sha = repo
    res = run(path, "--test-commit", sha, "--tests", "tests/test_never_committed.py")
    assert res.returncode == 2 and "not in test commit" in res.stdout, res.stdout


def test_head_option_checks_a_branch_without_checking_it_out(repo):
    path, sha = repo
    git(path, "branch", "weakened")
    git(path, "worktree", "add", "-q", str(path / "wt"), "weakened")
    (path / "wt" / TEST_FILE).write_text("def test_add():\n    pass\n")
    git(path / "wt", "commit", "-q", "-am", "weaken on a branch")
    assert run(path, "--test-commit", sha, "--tests", TEST_FILE).returncode == 0
    assert run(path, "--test-commit", sha, "--tests", TEST_FILE, "--head", "weakened").returncode == 1
