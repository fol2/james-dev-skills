---
description: "Shared rule (v1 and v2): a path that names nothing readable is refused, not treated as free-text intent."
tags: [behaviour, shared]
runs: 3
max_turns: 6
timeout_seconds: 240
allowed_tools: [Skill, Read, Glob, Grep, Write, Edit]
---

/sdlc-deliver docs/contracts/billing-export.md
