---
name: enable-dream
description: >-
  Patch Claude Code binary to enable /dream command and auto-dream background
  memory consolidation. Use when the user says "enable dream", "patch dream",
  "unlock dream", "enable auto-dream", or complains that /dream returns
  "Unknown skill" or that auto-dream toggle is missing from /memory.
  Also use when the user upgrades Claude Code and needs to re-apply the dream
  patch on the new version. This skill handles detection, backup, patching,
  and verification automatically.
---

# Enable Dream — Claude Code Binary Patcher

This skill patches the Claude Code binary to bypass three server-side feature
gates that control /dream and auto-dream availability. The gates are Statsig
feature flags that Anthropic rolls out gradually; this patch makes them always
return true so the features work regardless of rollout status.

## What it patches

Three gate functions are identified structurally (not by minified names) and
patched with same-length byte replacements:

| Gate | Statsig flag | Controls |
|---|---|---|
| Availability gate | `tengu_onyx_plover` | Whether dream features are visible in UI |
| Skill gate | `tengu_kairos_dream` | Whether `/dream` command is registered |
| Runner gate | uses availability gate + `autoDreamEnabled` | Whether background auto-dream fires |

## How to use

### Step 1 — Run the patcher

Run the bundled script. It auto-detects the Claude Code binary location.

```bash
python <this-skill-dir>/scripts/dream_patcher.py patch
```

On Windows (Claude Code typically runs in Git Bash), use:
```bash
python "<this-skill-dir>/scripts/dream_patcher.py" patch
```

**Flags:**
- `--dry-run` — show what would be patched without writing
- `--binary PATH` — explicit path to claude binary (skips auto-detection)

### Step 2 — Offer to disable auto-updater (ASK THE USER FIRST)

The auto-updater will overwrite the patch on next update, so the user has
to re-patch each time Claude Code updates. Disabling it keeps the patch
stable but also means the user stops receiving Anthropic's updates until
they turn it back on — that's a trade-off the **user must decide**, not you.

After the patch succeeds, ask the user something like:

> "Patch applied. Auto-updater will overwrite it on the next `claude update`.
> Want me to set `DISABLE_AUTOUPDATER: "1"` in `~/.claude/settings.json` to
> lock the patched version in? (You can re-enable and re-patch manually
> anytime.)"

Only edit `~/.claude/settings.json` if the user says yes. If they decline
or don't answer, skip this step — they may prefer to keep getting updates
and re-patch each time, or manage the env var themselves at the OS level.

If the user says yes, add this under `"env"` in `~/.claude/settings.json`:

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

### Step 3 — Restart Claude Code

The patch applies to the binary on disk. The current running session still
uses the old binary. Start a new session to load the patched version.

### Step 4 — Verify

In the new session:
- `/memory` should show an "Auto-dream" toggle
- `/dream` should work (not "Unknown skill")
- `autoDreamEnabled: true` in settings.json enables background consolidation

## Other commands

### Check status
```bash
python <this-skill-dir>/scripts/dream_patcher.py status
```

Shows: version, patch state (patched/unpatched/partially patched), backup info.

### Restore original
```bash
python <this-skill-dir>/scripts/dream_patcher.py restore
```

Restores the most recent backup. If the binary is currently running (Windows),
it uses rename-swap and you need to restart.

### Re-patch after update

When you update Claude Code (`claude update`), re-run the patcher:
```bash
python <this-skill-dir>/scripts/dream_patcher.py patch
```

The script detects the new version, creates a fresh backup, and finds the
gate functions in the new binary. Minified function names change between
versions but the script matches structurally via stable anchor strings.

## When the patcher fails

If the script reports "pattern not found", it means Anthropic changed the
gating architecture in the new version. Possible causes:

1. **Different Statsig flag names** — check the binary for new flag names
   near `auto_dream` or `dream` strings
2. **Restructured gate logic** — the function shape changed beyond what
   structural matching can handle
3. **Encrypted/obfuscated JS bundle** — unlikely but possible
4. **Integrity checks added** — the Node.js SEA blob may have checksums

In these cases, the manual approach from the `references/architecture.md`
document explains the underlying mechanism so you can adapt.

## Important notes

- Patches are **same-length byte replacements** — no offsets shift, binary
  size is unchanged, the Node.js SEA structure stays intact
- The original binary is always backed up before patching
- **macOS**: the patcher auto-detects Darwin and runs
  `codesign --force --sign -` on the patched binary. Any byte edit
  invalidates the Apple code signature, so without re-signing the kernel
  would refuse to launch the binary (typically `killed: 9` on arm64).
  Requires Xcode Command Line Tools (`xcode-select --install`) for
  `codesign` to be available.
- **macOS/Linux**: `~/.local/bin/claude` is usually a symlink to the
  versioned binary (`~/.local/share/claude/versions/<ver>`). The patcher
  resolves symlinks so backups land next to the real file and restore
  finds them reliably.
- **Windows**: the running binary cannot be overwritten directly. The
  script uses a rename-swap strategy (rename running exe, put patched
  one in place)
- The `autoDreamEnabled: true` setting in `~/.claude/settings.json` is
  still needed for auto-dream to run. The patch just makes the setting
  take effect instead of being ignored by the gate.
