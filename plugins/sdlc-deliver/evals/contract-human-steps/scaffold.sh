#!/usr/bin/env bash
# Fixture: a tiny local-mode repository (no remote) holding a CLI, its test, a contract and an idea.
set -euo pipefail
mkdir -p tests docs/contracts ideas
cat > report.py <<'PY'
"""Print a GWP summary by region from a fixed sample."""
import sys

ROWS = [("North", 120, 1500000), ("South", 95, 1210000), ("Wales", 40, 380000)]


def summary_rows():
    return [("region", "policies", "gwp")] + [(r, str(p), str(g)) for r, p, g in ROWS]


def main(argv=None):
    for row in summary_rows():
        print("\t".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
PY
cat > tests/test_report.py <<'PY'
import report


def test_header_row():
    assert report.summary_rows()[0] == ("region", "policies", "gwp")
PY
cat > docs/contracts/csv-export.md <<'MD'
# Contract: CSV export for the summary report

**Originator:** James To, 2026-10-02.

## Scope

Add a `--csv PATH` option to `report.py` so the summary can be written as CSV as well as printed.

## Requirements

1. `python report.py --csv out.csv` writes the same rows the console summary prints, with the header
   row `region,policies,gwp`.
2. Without `--csv`, the behaviour is unchanged.
3. Manual QA: a team member opens the CSV in Excel and checks that the columns line up.
4. Compliance signs off the CSV column list before release.

## Acceptance criteria

- A test proves the CSV rows equal the console rows.
- The existing tests still pass (`python -m pytest`).
MD
cat > ideas/broker-filter.md <<'MD'
# Idea: run the summary report for one broker

From James To, 2026-10-02: "The summary report is too broad for broker meetings. I would like to run
it for one broker at a time, and still get the whole book when I do not name one."
MD
git init -q .
git config user.email eval@example.invalid
git config user.name eval
git add -A
git commit -qm "fixture: report CLI, contract and idea"
