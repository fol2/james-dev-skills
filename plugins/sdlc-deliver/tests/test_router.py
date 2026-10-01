"""U4: the SKILL.md router stays short, complete and free of the v1 volume rules.

    python plugins/sdlc-deliver/tests/test_router.py     (or pytest)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "sdlc-deliver"
ROUTER = SKILL_DIR / "SKILL.md"
MAX_LINES = 250
INTEGRITY_SENTENCE = "Only a fix clears a finding."

# Phrases whose return would mean the v1 compensations crept back: a fixed reviewer panel, a ban on
# questions, and escalating prose in place of a mechanical check.
SURVIVORS = ("10 reviewers", "10-reviewer", "ten reviewers", "do not ask", "hardest")


def text() -> str:
    return ROUTER.read_text(encoding="utf-8")


def skill_texts() -> dict[str, str]:
    return {p.relative_to(SKILL_DIR).as_posix(): p.read_text(encoding="utf-8")
            for p in sorted(SKILL_DIR.rglob("*.md"))}


def frontmatter() -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text().replace("\r\n", "\n"), re.DOTALL)
    assert m, "SKILL.md has no frontmatter"
    out = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"')
    return out


def test_router_is_at_most_250_lines():
    n = len(text().splitlines())
    assert n <= MAX_LINES, f"SKILL.md is {n} lines; move detail into references/"


def test_frontmatter_keeps_the_interface():
    fm = frontmatter()
    assert fm.get("name") == "sdlc-deliver"
    assert fm.get("disable-model-invocation") == "true", "the skill must stay user-invoked only"
    desc = fm.get("description", "")
    assert 0 < len(desc) <= 1024, f"description length {len(desc)}"
    assert "/sdlc-deliver" in desc


def test_every_stage_and_gate_is_present():
    body = text()
    for n in range(1, 9):
        assert re.search(rf"^## Stage {n}\b", body, re.MULTILINE), f"Stage {n} heading missing"
    for gate in ("G1", "G2", "G3", "G4"):
        assert f"**{gate}**" in body, f"gate {gate} is never fired in bold in the router"


def test_every_references_path_resolves():
    cited = set(re.findall(r"references/[\w./-]*\w", text()))
    assert cited, "router cites no references"
    missing = sorted(p for p in cited if not (SKILL_DIR / p).exists())
    assert not missing, f"router cites missing paths: {missing}"


def test_integrity_rule_is_stated_once():
    hits = {name: body.count(INTEGRITY_SENTENCE) for name, body in skill_texts().items()}
    assert hits.get("SKILL.md") == 1, f"integrity rule count in SKILL.md: {hits.get('SKILL.md')}"
    elsewhere = {k: v for k, v in hits.items() if v and k != "SKILL.md"}
    assert not elsewhere, f"integrity rule restated in {elsewhere}"
    assert text().count("## Integrity rule") == 1


def test_no_v1_survivors_anywhere_in_the_skill():
    found = [(name, phrase) for name, body in skill_texts().items()
             for phrase in SURVIVORS if phrase in body.lower()]
    assert not found, f"v1 phrases survived: {found}"


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
