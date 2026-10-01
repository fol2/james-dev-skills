"""U1: each artefact template carries the headings the stages after it depend on.

    python plugins/sdlc-deliver/tests/test_templates.py     (or pytest)

A later stage reads an earlier stage's artefact, so a template that loses a heading breaks the
chain silently: the plan stops carrying verify commands, the report stops carrying metrics.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "skills" / "sdlc-deliver" / "references" / "templates"

REQUIRED = {
    "intent.md": ["In the originator's words", "Problem", "Outcome wanted", "Constraints", "Non-goals",
                  "Open questions for the owner"],
    "spec.md": ["Risk tier", "Requirements", "Design", "Review dimensions", "Acceptance checks", "Assumptions"],
    "plan.md": ["Units", "Parallel groups", "Locked tests", "Risks", "Assumptions"],
    "report.md": ["Requirement → evidence", "Units and PRs", "Findings", "Metrics", "Learnings and loop",
                  "Deferred: requires a human"],
}


def headings(name: str) -> list[str]:
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    return [m.group(1).strip() for m in re.finditer(r"^#{2,3} (.+)$", text, re.MULTILINE)]


def body(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def test_every_template_exists_and_has_its_headings():
    assert sorted(p.name for p in TEMPLATES.glob("*.md")) == sorted(REQUIRED), "template set changed"
    for name, wanted in REQUIRED.items():
        missing = [h for h in wanted if h not in headings(name)]
        assert not missing, f"{name} lacks {missing}"


def test_every_template_carries_a_status_line():
    for name in REQUIRED:
        assert "**Status:**" in body(name), f"{name} has no Status line, so a run cannot resume from it"


def test_spec_carries_tier_dimensions_and_checks():
    spec = body("spec.md")
    assert "**Tier:**" in spec and "**Rubric line:**" in spec
    for dim in ("Contract completeness", "Tests and edge cases", "Integration and regression",
                "Security", "Performance", "UX/UI", "Documentation", "Architecture"):
        assert f"| {dim} |" in spec, f"dimension row missing: {dim}"
    assert "| # | Requirement | Command | Expected result |" in spec


def test_plan_carries_a_verify_command_per_unit_and_locked_tests():
    plan = body("plan.md")
    assert "| Verify command |" in plan
    assert "| Test commit |" in plan
    for status in ("awaiting G2", "approved at G2", "G2 not required (low risk)"):
        assert status in plan, f"plan status value missing: {status}"


def test_report_carries_evidence_and_every_metric():
    report = body("report.md")
    assert "| Check | Requirement | Evidence | Status |" in report
    for metric in ("First-pass verify rate", "Review rounds per PR", "Important findings per PR",
                   "Owner wait time per gate", "Elapsed time per stage"):
        assert metric in report, f"metric missing: {metric}"


def test_intent_and_spec_share_the_g1_status_values():
    for status in ("awaiting G1", "accepted at G1", "G1 not required"):
        assert status in body("intent.md"), status
    assert "awaiting G1" in body("spec.md")


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
