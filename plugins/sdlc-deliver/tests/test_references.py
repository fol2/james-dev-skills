"""U2: each rule is defined in exactly one reference file, and the router cites every one.

    python plugins/sdlc-deliver/tests/test_references.py     (or pytest)

A rule stated in two places drifts into two rules; a rule the router never cites is never read.
Rules are the `## [X<n>] Title` headings in references/*.md (templates excluded).
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "sdlc-deliver"
REFS = SKILL_DIR / "references"
ROUTER = SKILL_DIR / "SKILL.md"
RULE_HEADING = re.compile(r"^## \[([A-Z]\d+)\] (.+)$", re.MULTILINE)
CITATION = re.compile(r"\[([A-Z]\d+)\]")


def reference_files() -> list[Path]:
    return sorted(p for p in REFS.glob("*.md"))


def definitions() -> list[tuple[str, str, str]]:
    """(rule id, title, file name) for every rule heading in every reference file."""
    out = []
    for path in reference_files():
        for m in RULE_HEADING.finditer(path.read_text(encoding="utf-8")):
            out.append((m.group(1), m.group(2).strip(), path.name))
    return out


def test_policy_files_exist():
    names = {p.name for p in reference_files()}
    for wanted in ("REVIEW.default.md", "gates.md", "verification.md", "local-mode.md"):
        assert wanted in names, f"missing reference: {wanted}"


def test_every_reference_file_defines_rules():
    by_file = Counter(f for _, _, f in definitions())
    empty = [p.name for p in reference_files() if not by_file[p.name]]
    assert not empty, f"reference files with no rule headings: {empty}"


def test_each_rule_id_is_defined_once():
    counts = Counter(rule for rule, _, _ in definitions())
    dupes = {rule: n for rule, n in counts.items() if n > 1}
    assert not dupes, f"rule ids defined more than once: {dupes}"


def test_each_rule_title_lives_in_one_file():
    homes: dict[str, set[str]] = {}
    for _, title, name in definitions():
        homes.setdefault(title.lower(), set()).add(name)
    split = {t: sorted(f) for t, f in homes.items() if len(f) > 1}
    assert not split, f"the same rule title is defined in several files: {split}"


def test_router_cites_every_rule_and_no_unknown_one():
    text = ROUTER.read_text(encoding="utf-8")
    defined = {rule for rule, _, _ in definitions()}
    cited = set(CITATION.findall(text))
    assert not (defined - cited), f"rules the router never cites: {sorted(defined - cited)}"
    assert not (cited - defined), f"router cites undefined rules: {sorted(cited - defined)}"


def test_router_names_every_reference_file():
    text = ROUTER.read_text(encoding="utf-8")
    unnamed = [p.name for p in reference_files() if f"references/{p.name}" not in text]
    assert not unnamed, f"reference files the router never names: {unnamed}"


def test_router_defines_no_rule_of_its_own():
    assert not RULE_HEADING.search(ROUTER.read_text(encoding="utf-8")), "rule headings belong in references/"


def _run_as_script() -> int:
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failed += 1
                print(f"FAIL {name}: {exc}")
    print(f"{'FAILED' if failed else 'OK'}: {failed} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_as_script())
