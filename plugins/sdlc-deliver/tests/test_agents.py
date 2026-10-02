"""U8: every subagent the skill dispatches is pinned to Opus 5.5 at xhigh effort (verification.md [V8]).

    python plugins/sdlc-deliver/tests/test_agents.py     (or pytest)

The pin lives in the plugin agents' frontmatter because the Agent tool has no effort parameter, and a
per-invocation `model` overrides the frontmatter. So the router must name the agents and must not
tell the caller to pass a model.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
AGENTS = PLUGIN / "agents"
ROUTER = PLUGIN / "skills" / "sdlc-deliver" / "SKILL.md"
VERIFICATION = PLUGIN / "skills" / "sdlc-deliver" / "references" / "verification.md"
PLAN = PLUGIN / "skills" / "sdlc-deliver" / "references" / "templates" / "plan.md"


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, f"{path.name} has no frontmatter"
    return {k.strip(): v.strip() for k, v in (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)}


def test_both_agents_pin_opus_at_xhigh():
    """Catches an agent file that leaves `model` as inherit, or spells the effort `extra-high`, which
    Claude Code ignores, so the subagent silently runs on the session's model and effort."""
    for name in ("sdlc-worker", "sdlc-verifier"):
        fm = frontmatter(AGENTS / f"{name}.md")
        assert fm.get("name") == name
        assert fm.get("model") == "opus", f"{name}: model is {fm.get('model')!r}"
        assert fm.get("effort") == "xhigh", f"{name}: effort is {fm.get('effort')!r}"


def test_verifier_keeps_bash_and_read_only():
    """Catches a verifier given Edit or Write (or no tools line, which inherits every tool), letting
    the role that must never fix quietly fix what it was meant to report."""
    tools = {t.strip() for t in frontmatter(AGENTS / "sdlc-verifier.md").get("tools", "").split(",")}
    assert tools == {"Bash", "Read"}, tools


def test_router_names_the_agents_and_never_asks_for_a_model_parameter():
    """Catches a router that dispatches a generic subagent with `model: "opus"`: that selects the
    model but drops the xhigh effort, and overrides the frontmatter pin."""
    router = ROUTER.read_text(encoding="utf-8")
    assert "`sdlc-worker`" in router and "`sdlc-verifier`" in router
    assert "[V8]" in router
    assert not re.search(r"model\s*[:=]\s*[\"']?opus", router), "the router must not pass a model"


def test_plan_check_asks_what_each_test_catches():
    """Catches a plan check that still asks only the first two questions, so a test that a wrong
    implementation also passes (the 2026-10-01 dayfirst date bug) gets through planning."""
    router = ROUTER.read_text(encoding="utf-8")
    assert "three questions" in router and "plausible wrong implementation" in router
    assert "plausible wrong implementation it fails" in VERIFICATION.read_text(encoding="utf-8")
    assert "| Check | Test | A plausible wrong implementation it fails |" in PLAN.read_text(encoding="utf-8")


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
