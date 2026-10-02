---
description: "A supplied contract that is not owner-approved: the compliance sign-off stays a human item (shared rule); v2 also stops at G1 before any code (v2 feature)."
tags: [behaviour, mixed]
runs: 2
max_turns: 25
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Write, Edit]
append_system_prompt: "Evaluation environment: this session has no shell, so Bash and git are unavailable. The working directory is a checkout of the target repository with no remote (local mode). Where the skill asks for a worktree, write the artefacts inside the working directory instead, at the path the skill names; where it asks for a commit, state the commit you would make and carry on."
---

/sdlc-deliver docs/contracts/csv-export.md
