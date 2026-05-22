---
description: "Reflective memory consolidation — review recent activity, synthesize learnings into typed memory files, and prune stale entries."
allowed-tools: Bash(ls:*), Bash(find:*), Bash(grep:*), Bash(cat:*), Bash(stat:*), Bash(wc:*), Bash(head:*), Bash(tail:*), Bash(rm:*.md), Read, Write, Glob, Grep, CronCreate, CronList, CronDelete
argument-hint: "[nightly | additional context]"
---

# Dream

User invocation: `/dream $ARGUMENTS`

## Routing

Compute `_` from `$ARGUMENTS`:

1. Trim whitespace.
2. If `_` equals exactly `consolidate` (whole-string, case-sensitive — this is the sentinel sent by the scheduled cron job), set `_ = ""`.
3. Test `_` against the regex `/^(nightly|schedule|overnight)\b/i`.
   - **If it matches:** strip the matched keyword from the start, trim again, and follow **Mode A — Schedule**. The remaining text becomes the additional-context string for the immediate-run step at the end of Mode A.
   - **Otherwise:** follow **Mode B — Consolidate now** with `_` as the additional-context string.

---

## Mode A — Schedule Nightly Consolidation

The user wants to set up a recurring nightly memory consolidation job.

**Step 1 — Pick a randomized cron**

Generate a random number `R` in `0..359`. Build the cron string:

- `minute = R mod 60`
- `hour = floor(R / 60)` (which gives `0..5`)
- Result: `"<minute> <hour> * * *"` — fires once per day at a random time between midnight and 6am local.

The randomization spreads load across the fleet and avoids everyone landing on `:00`.

**Step 2 — Dedup any existing nightly job**

Call `CronList`. Look for any existing job whose `prompt` is exactly `"/dream consolidate"`. If one exists, call `CronDelete` with its id first so renewal doesn't leave overlapping jobs.

**Step 3 — Schedule**

Call `CronCreate` with:
- `cron`: the random expression from Step 1
- `prompt`: `"/dream consolidate"`
- `recurring`: `true`
- `durable`: `true`

(The `consolidate` suffix means this prompt won't match the `nightly|schedule|overnight` regex when it fires — so it runs the consolidation path, not the schedule path.)

**Step 4 — Confirm**

Tell the user, formatting the time as 12-hour with am/pm:
- `/dream` will run nightly at approximately `<HH:MM><am|pm>` local to consolidate and organize memories
- The schedule persists across sessions (written to `.claude/scheduled_tasks.json`)
- Recurring tasks auto-expire after 7 days — re-run `/dream nightly` to renew
- Cancel anytime with `CronDelete` (include the job id from Step 3)

**Step 5 — Run an immediate consolidation**

After confirming the schedule, run **Mode B** in the same turn so the user sees the first consolidation result immediately. Pass through the additional-context string captured from the routing step (whatever followed `nightly`/`schedule`/`overnight` in the original `$ARGUMENTS`).

---

## Mode B — Memory Consolidation

You are performing a dream — a reflective pass over your memory files. Synthesize what you've learned recently into durable, well-organized memories so that future sessions can orient quickly.

Your memory directory path is given in the auto-memory section of your system prompt — use that path directly. It already exists; write to it with the Write tool (do not run `mkdir` or check for its existence).

Session transcripts are stored as `.jsonl` files under `~/.claude/projects/<sanitized-cwd>/`. Grep narrowly; don't read whole files.

**Tool constraints for this run:** Shell access is restricted to read-only commands (`ls`, `find`, `grep`, `cat`, `stat`, `wc`, `head`, `tail`, and similar) plus deleting `.md` paths inside the memory directory. Edit is not permitted — memories are immutable, so delete + Write to replace, never edit in place. Plan your exploration with this in mind — no need to probe.

---

### Phase 1 — Orient

- `ls` the memory directory to see what already exists
- Read `MEMORY.md` to understand the current index
- Skim existing topic files so you improve them rather than creating duplicates
- `ls -R logs/` — recent activity logs (one file per session under `YYYY/MM/DD/`). If a `sessions/` subdirectory also exists, review recent entries there too

### Phase 2 — Gather recent signal

Look for new information worth persisting. Sources in rough priority order:

1. **Session logs** (`logs/YYYY/MM/DD/<id>-<title>.md`) — the append-only activity stream, one file per session. Read the most recent 1–3 days of sessions (the filename title tells you what each was about); each line is prefix-coded (`>` user, `<` assistant, `.` tool call)
2. **Existing memories that drifted** — facts that contradict something you see in the codebase now
3. **Transcript search** — if you need specific context (e.g., "what was the error message from yesterday's build failure?"), grep the JSONL transcripts for narrow terms:
   `grep -rn "<narrow term>" ~/.claude/projects/ --include="*.jsonl" | tail -50`

Don't exhaustively read transcripts. Look only for things you already suspect matter.

### Team memory (`team/` subdirectory)

If — and only if — a `team/` subdirectory exists in the memory directory, treat it as memories shared across everyone working in this repo. Other teammates' Claude sessions write here too:

- **Phase 1:** `ls team/` and skim it alongside your personal files. A teammate may have already captured something you'd otherwise duplicate.
- **Phase 3:** Merge near-duplicates *within* `team/` the same way you would personal memories. If a personal memory restates a team memory, delete the personal one.
- **Phase 4 — be conservative pruning `team/`:**
  - DO delete or fix a team memory that is clearly contradicted by the current code, or that a newer team memory marks as superseded.
  - DO NOT delete a team memory just because you don't recognize it or it isn't relevant to *your* recent sessions — a teammate may rely on it.
  - When unsure, leave it. A stale team memory costs little; deleting a teammate's load-bearing note costs a lot.

Do not promote personal memories into `team/` during a dream — that's a deliberate choice the user makes via `/remember`, not something to do reflexively.

If no `team/` subdirectory exists, skip this section entirely.

### Phase 3 — Consolidate

For each thing worth remembering, write or update a memory file at the top level of the memory directory. Use the memory file format and type conventions from your system prompt's auto-memory section — it's the source of truth for what to save, how to structure it, and what NOT to save.

Focus on:
- Merging new signal into existing topic files rather than creating near-duplicates
- Converting relative dates ("yesterday", "last week") to absolute dates so they remain interpretable after time passes
- Deleting contradicted facts — if today's investigation disproves an old memory, fix it at the source

### Phase 4 — Prune and index

Update `MEMORY.md` so it stays under 200 lines AND under ~25KB. It's an **index**, not a dump — each entry should be one line under ~150 characters: `- [Title](file.md) — one-line hook`. Never write memory content directly into it.

- Remove pointers to memories that are now stale, wrong, or superseded
- Demote verbose entries: if an index line is over ~200 chars, it's carrying content that belongs in the topic file — shorten the line, move the detail
- Add pointers to newly important memories
- Resolve contradictions — if two files disagree, fix the wrong one

#### Reconcile memories against CLAUDE.md

Project CLAUDE.md instructions are loaded in your system prompt. For each `feedback` or `project` memory, check whether it contradicts a CLAUDE.md instruction on the same topic:

- **Memory is stale** — CLAUDE.md and the memory describe different procedures for the same task: CLAUDE.md is the maintained, checked-in source. Delete the memory, or rewrite it to agree if it carries context worth keeping (the *why* is still useful but the *how* is wrong).
- **CLAUDE.md may be stale** — the memory is clearly dated after CLAUDE.md and explicitly corrects it: do NOT edit CLAUDE.md during a dream. Annotate the memory with "contradicts CLAUDE.md — verify which is current" and list it in your summary so the user can update CLAUDE.md.
- **Not a conflict** — the memory adds detail CLAUDE.md doesn't cover, or narrows a CLAUDE.md rule with a stated reason. Leave it.

A `feedback` memory's "Why: the user corrected me" framing is not evidence it's newer than CLAUDE.md — CLAUDE.md may have been updated since.

---

Return a brief summary of what you consolidated, updated, or pruned — include a list of what you deleted, combined, or left alone. If nothing changed (memories are already tight), say so.

### Additional context

If the routing step produced a non-empty additional-context string (i.e. `$ARGUMENTS` after stripping any `nightly`/`schedule`/`overnight` prefix and excluding the bare `consolidate` sentinel), append it verbatim below and weight it while consolidating:

```
$ARGUMENTS
```
