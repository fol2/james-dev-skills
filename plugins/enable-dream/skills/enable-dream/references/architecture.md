# Dream Feature Gating Architecture

Technical reference for understanding and adapting the patcher when
Anthropic changes the binary structure.

## Binary structure

Claude Code ships as a **Node.js SEA** (Single Executable Application).
The PE32+/Mach-O/ELF binary embeds a bundled JS blob containing the full
application code, minified. The JS bundle typically appears **twice** in
the binary (two copies at different offsets ~100MB apart).

## Three gate functions

### 1. Availability gate

**Anchor string:** `"tengu_onyx_plover"` (Statsig flag name)

**Purpose:** Controls whether dream features are available at all.
Both the UI toggle and the runner check this.

**Structure (v2.1.101 example, minified names will differ):**
```javascript
function Xi8() {
    let H = _M_();  // fetch Statsig flag "tengu_onyx_plover"
    if (H?.enabled === !0 || H?.available === !0) return !0;
    return HR8();  // fallback check
}
```

**Detection:** Find functions containing `tengu_onyx_plover` AND
`?.enabled` AND `?.available` with body < 300 bytes.

**Patch:** Replace entire body with `return!0;/*...*/`

### 2. Skill gate

**Anchor string:** `"tengu_kairos_dream"` (separate Statsig flag)

**Purpose:** Controls whether `/dream` skill is registered and
invocable. Passed as `isEnabled` to the skill registration call.

**Structure:**
```javascript
function GU1() {
    return !DG() && lf() && FE("tengu_kairos_dream", !1, ZU1);
    //     ^check1  ^check2  ^Statsig flag eval (default: false)
}
```

**Detection:** Find functions containing `tengu_kairos_dream` AND
`FE(` with body < 200 bytes, NOT containing `autoDreamEnabled`.

**Patch:** Replace entire body with `return!0;/*...*/`

### 3. Runner gate

**Anchor string:** `"autoDreamEnabled"` (settings key)

**Purpose:** Controls whether background auto-dream fires. This is
the `isAutoDreamEnabled()` check.

**Structure:**
```javascript
function R_8() {
    if (!Xi8()) return !1;          // ← availability gate check
    let H = X$().autoDreamEnabled;  // user setting
    if (H !== void 0) return H;     // user override wins
    if (_M_()?.enabled === !0) return !0;
    return HR8();
}
```

**Detection:** Find functions containing `autoDreamEnabled` AND
matching `if(!XXXX())return!1` with body < 300 bytes.

**Patch:** Flip single byte in `return!1` → `return!0` (1→0)

## Stable vs unstable identifiers

| Identifier | Stable? | Notes |
|---|---|---|
| `tengu_onyx_plover` | Yes | Statsig flag name, server-side |
| `tengu_kairos_dream` | Yes | Statsig flag name, server-side |
| `autoDreamEnabled` | Yes | Settings schema key |
| `Xi8`, `GU1`, `R_8` | No | Minifier-generated, change each build |
| `FE(` | Likely stable | Statsig SDK function, may change on SDK update |
| `?.enabled`, `?.available` | Likely stable | JS optional chaining on flag object |
| `auto_dream` (telemetry) | Yes | Event names rarely change |

## What changes between versions

1. **Function names** — minifier generates new names each build
2. **Function positions** — byte offsets shift as code changes
3. **Number of copies** — typically 2, could change with build config
4. **Minor structural changes** — e.g., adding a new condition to
   an existing gate, reordering checks

## What would break the patcher

1. **Renamed Statsig flags** — different anchor strings needed
2. **Gate logic moved to server** — client-side patch ineffective
3. **Encrypted JS bundle** — can't find strings
4. **SEA integrity checksums** — patched binary fails to load
5. **WebAssembly gates** — logic moved out of JS

## Debugging a failed patch

```bash
# Check if anchor strings still exist
python -c "
data = open(r'path/to/claude.exe', 'rb').read()
for s in [b'tengu_onyx_plover', b'tengu_kairos_dream', b'autoDreamEnabled']:
    print(f'{s!r}: {data.count(s)} occurrences')
"

# Extract functions around a known anchor
python -c "
import re
data = open(r'path/to/claude.exe', 'rb').read()
for m in re.finditer(rb'tengu_onyx_plover', data):
    region = data[max(0,m.start()-500):m.end()+200]
    text = re.sub(rb'[^\x20-\x7e]', b' ', region).decode()
    text = re.sub(r' {3,}', ' | ', text)
    print(f'--- offset {m.start()} ---')
    print(text[:600])
"
```

## Auto-dream trigger conditions

Even after patching, auto-dream requires:
- `autoDreamEnabled: true` in `~/.claude/settings.json`
- ≥ 24 hours since last dream
- ≥ 5 sessions with activity
- Both conditions must be met simultaneously

Manual `/dream` has no such conditions — it runs immediately.
