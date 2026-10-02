---
description: "v2 feature: an idea is valid input; Stage 1-2 write intent.md and spec.md with 'awaiting G1' status lines and a risk tier, then stop at G1."
tags: [behaviour, v2-feature]
runs: 2
max_turns: 25
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Write, Edit]
append_system_prompt: "Evaluation environment: this session has no shell, so Bash and git are unavailable. The working directory is a checkout of the target repository with no remote (local mode). Where the skill asks for a worktree, write the artefacts inside the working directory instead, at the path the skill names; where it asks for a commit, state the commit you would make and carry on."
---

/sdlc-deliver ideas/broker-filter.md
