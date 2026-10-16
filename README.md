# fol2-dev-skills

James To's Claude Code plugin marketplace. Install with `/plugin marketplace add fol2/james-dev-skills`, then `/plugin install <name>@fol2-dev-skills`.

| Plugin | Use it for |
|---|---|
| `sdlc-deliver` | Contract work for a client: an artefact chain (intent, spec, plan, units, review, verifier, report) with risk-tiered owner gates G1 to G4, verification commands and locked tests. Run `/sdlc-deliver <path to the contract>`. |
| `claude-design` | Craft-level HTML design artefacts: landing pages, decks, prototypes, animations. |
| `humanise` | Rewriting text for the dissertation and casual registers only. Not for product, company or repo text. |

## sdlc-deliver and ai-sdlc

`sdlc-deliver` is the separate **contracts mode**. It is not the delivery loop for eugnel-ltd's own products.

- **ai-sdlc** (eugnel-ltd/ai-sdlc, private) runs eugnel-ltd's own products end to end with one owner and full autonomy: an autonomy ledger per task type, a cross-vendor review on the exact head, and three owner touchpoints (north star, owner decisions, expenditure). Use it in any repo that has `AGENTS.md` and `docs/autonomy-ledger.md`.
- **sdlc-deliver** runs work that a client, not the owner, accepts: named human gates (G1 intent and spec, G2 plan, G3 high-risk merge, G4 release), artefacts under `docs/delivery/<slug>/`, and a local mode for repos with no remote.

Both keep the failing-test-first rule and share `locked_tests_check.py` (ai-sdlc carries a copy in `scripts/`). Do not install both triggers in one repo. Owner decision of 14 Oct 2026, recorded in ai-sdlc's README ("ai-sdlc and sdlc-deliver").

## Tests and evals

- `python3 -m pytest plugins/sdlc-deliver/tests`
- Behaviour evals: `plugins/sdlc-deliver/evals/<case>/` (`prompt.md`, `graders/`, optional `case.yaml` and `scaffold.sh`). ai-sdlc's `modules/evals.md` describes the format.
