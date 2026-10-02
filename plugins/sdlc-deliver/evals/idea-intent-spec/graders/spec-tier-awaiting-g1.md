---
# Catches: a spec with no risk tier (so G2-G4 cannot be decided) or no pending-gate status line.
type: tool_used
tool: Write
input_match: '"file_path"\s*:\s*"[^"]*spec\.md"[\s\S]*awaiting G1[\s\S]*Tier:\**\s*\**(low|medium|high|Low|Medium|High)'
min: 1
---
Catches: a spec with no risk tier (so G2-G4 cannot be decided) or no pending-gate status line.
