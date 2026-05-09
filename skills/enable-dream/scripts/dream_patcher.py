#!/usr/bin/env python3
"""
Claude Code Dream Feature Patcher

Enables /dream and auto-dream memory consolidation by patching three
server-side feature gates in the Claude Code binary.

Gate functions are identified structurally by their relationship to
stable Statsig flag names (not by minifier-generated identifiers),
making the patcher resilient across version updates.

All patches are same-length byte replacements — no offsets shift,
no blob resizing needed. The binary remains a valid Node.js SEA executable.

Usage:
    python dream_patcher.py patch [--dry-run] [--binary PATH]
    python dream_patcher.py restore [--binary PATH]
    python dream_patcher.py status [--binary PATH]

Three gates are patched:
  1. AVAILABILITY gate: checks tengu_onyx_plover .enabled/.available
     → Controls UI visibility and runner pre-check
  2. SKILL gate: calls evaluator("tengu_kairos_dream", ...)
     → Controls /dream command registration
  3. RUNNER gate: calls availability gate, checks autoDreamEnabled
     → Controls background auto-dream firing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import struct
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FunctionMatch:
    """A JS function found in the binary."""
    name: str
    start: int          # byte offset of 'function' keyword
    end: int            # byte offset AFTER closing '}'
    body: bytes         # full bytes: function name(){...}

    @property
    def inner_body(self) -> bytes:
        """The bytes between { and } (exclusive)."""
        brace_open = self.body.index(b'{')
        return self.body[brace_open + 1:-1]

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end


@dataclass
class PatchSite:
    """A single byte-range replacement."""
    offset: int
    original: bytes
    replacement: bytes
    gate_type: str          # 'availability', 'skill', 'runner'
    description: str

    @property
    def length(self) -> int:
        return len(self.original)


@dataclass
class PatchReport:
    """Result of a patch/status/restore operation."""
    success: bool
    version: str
    binary_path: str
    operation: str
    patches: list[PatchSite] = field(default_factory=list)
    backup_path: Optional[str] = None
    sha256_before: str = ""
    sha256_after: str = ""
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Anchor strings — these are Statsig flag names and setting keys that
# remain stable across minifier runs. They are our structural anchors.
# ---------------------------------------------------------------------------

ANCHOR_AVAILABILITY = b"tengu_onyx_plover"
ANCHOR_SKILL = b"tengu_kairos_dream"
ANCHOR_RUNNER_SETTING = b"autoDreamEnabled"

# Patterns that identify each gate type within its enclosing function
AVAILABILITY_MARKERS = [b"?.enabled", b"?.available"]
SKILL_MARKERS = [b'("' + ANCHOR_SKILL + b'"']  # flag used as function arg (minifier-resilient)
RUNNER_MARKERS = [ANCHOR_RUNNER_SETTING]

# Bypass payload prefix — returned before any gate check
BYPASS_PREFIX = b"return!0;"

# Marker to detect already-patched functions
PATCH_SIGNATURE = b"return!0;/*"


# ---------------------------------------------------------------------------
# Binary location
# ---------------------------------------------------------------------------

def find_claude_binary(explicit_path: Optional[str] = None) -> Path:
    """Locate the Claude Code binary on this system.

    Always returns the fully resolved real path (symlinks followed), so
    patch/backup/restore operate on the versioned binary file rather than
    on a launcher symlink. This matters on macOS/Linux where
    ~/.local/bin/claude typically symlinks to
    ~/.local/share/claude/versions/<ver>.
    """
    if explicit_path:
        p = Path(explicit_path)
        if not p.exists():
            raise FileNotFoundError(f"Binary not found: {p}")
        return p.resolve()

    system = platform.system()
    home = Path.home()

    candidates = []
    if system == "Windows":
        candidates = [
            home / ".local" / "bin" / "claude.exe",
            home / "AppData" / "Local" / "Programs" / "claude" / "claude.exe",
        ]
    elif system == "Darwin":
        candidates = [
            home / ".local" / "bin" / "claude",
            home / ".claude" / "bin" / "claude",
            Path("/usr/local/bin/claude"),
        ]
    else:  # Linux
        candidates = [
            home / ".local" / "bin" / "claude",
            home / ".claude" / "bin" / "claude",
            Path("/usr/local/bin/claude"),
        ]

    # Also check PATH via shutil.which
    which_result = shutil.which("claude")
    if which_result:
        real = Path(which_result).resolve()
        if real not in candidates:
            candidates.insert(0, real)

    for c in candidates:
        if c.exists() and c.is_file():
            return c.resolve()

    raise FileNotFoundError(
        "Could not find Claude Code binary. "
        "Use --binary PATH to specify it explicitly."
    )


def get_version(binary_path: Path) -> str:
    """Extract version string from the binary."""
    import subprocess
    try:
        result = subprocess.run(
            [str(binary_path), "--version"],
            capture_output=True, text=True, timeout=15,
        )
        line = result.stdout.strip().split("\n")[0]
        # "2.1.101 (Claude Code)" → "2.1.101"
        return line.split("(")[0].strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# JS parsing — minimal parser for minified function extraction
# ---------------------------------------------------------------------------

def find_matching_brace(data: bytes, open_pos: int) -> int:
    """Find the } that closes the { at open_pos, respecting JS strings.

    Handles: double-quoted strings, single-quoted strings, template
    literals (backtick — no nested ${} tracking), line comments,
    block comments. Sufficient for minified gate functions.
    """
    depth = 0
    i = open_pos
    length = len(data)

    while i < length:
        b = data[i]

        if b == ord("{"):
            depth += 1
        elif b == ord("}"):
            depth -= 1
            if depth == 0:
                return i
        elif b in (ord('"'), ord("'"), ord("`")):
            # Skip string literal
            quote = b
            i += 1
            while i < length:
                if data[i] == ord("\\"):
                    i += 2  # skip escape sequence
                    continue
                if data[i] == quote:
                    break
                i += 1
        elif b == ord("/") and i + 1 < length:
            nxt = data[i + 1]
            if nxt == ord("/"):
                # Line comment — skip to newline (rare in minified)
                while i < length and data[i] != ord("\n"):
                    i += 1
            elif nxt == ord("*"):
                # Block comment — skip to */
                i += 2
                while i < length - 1:
                    if data[i] == ord("*") and data[i + 1] == ord("/"):
                        i += 1
                        break
                    i += 1

        i += 1

    return -1  # unmatched


# Regex for function declaration: function NAME(ARGS){
_FUNC_DECL_RE = re.compile(
    rb"function\s+([A-Za-z_$][\w$]{0,20})\s*\([^)]{0,200}\)\s*\{"
)


def find_enclosing_function(
    data: bytes, anchor_offset: int, max_lookback: int = 10_000
) -> Optional[FunctionMatch]:
    """Find the innermost function declaration enclosing anchor_offset."""
    search_start = max(0, anchor_offset - max_lookback)
    region = data[search_start : anchor_offset + 1]

    best: Optional[FunctionMatch] = None

    for m in _FUNC_DECL_RE.finditer(region):
        func_abs_start = search_start + m.start()
        brace_abs_start = search_start + m.end() - 1  # position of {

        brace_end = find_matching_brace(data, brace_abs_start)
        if brace_end < 0:
            continue

        # Anchor must be inside this function
        if func_abs_start <= anchor_offset <= brace_end:
            # Prefer innermost (closest start to anchor)
            if best is None or func_abs_start > best.start:
                best = FunctionMatch(
                    name=m.group(1).decode("ascii"),
                    start=func_abs_start,
                    end=brace_end + 1,
                    body=data[func_abs_start : brace_end + 1],
                )

    return best


def find_functions_containing(
    data: bytes, anchor: bytes, max_lookback: int = 10_000
) -> list[FunctionMatch]:
    """Find all function declarations whose body contains anchor."""
    seen: set[tuple[int, int]] = set()
    results: list[FunctionMatch] = []

    for m in re.finditer(re.escape(anchor), data):
        func = find_enclosing_function(data, m.start(), max_lookback)
        if func and (func.start, func.end) not in seen:
            seen.add((func.start, func.end))
            results.append(func)

    return results


# ---------------------------------------------------------------------------
# Gate detection — structural identification
# ---------------------------------------------------------------------------

def _body_contains_all(func: FunctionMatch, markers: list[bytes]) -> bool:
    return all(marker in func.body for marker in markers)


def _find_patched_functions(
    data: bytes, gate_type: str
) -> list[FunctionMatch]:
    """Find functions already patched by this tool (contain our comment tag).

    Patched functions have body: return!0;/*patched:<gate_type>:v1...*/
    Also detects manual patches with descriptive comments.
    """
    # Search for our patch signature with gate type tag
    tag = f"patched:{gate_type}".encode("ascii")
    results = find_functions_containing(data, tag)

    # Also detect manual patches (from early ad-hoc patching sessions)
    # These have descriptive comments like "availability gate bypassed"
    manual_tags = {
        "availability": [b"availability gate bypassed", b"Xi8 availability"],
        "skill": [b"DG()&&lf()&&FE("],
        "runner": [],
    }
    for manual_tag in manual_tags.get(gate_type, []):
        for func in find_functions_containing(data, manual_tag):
            if func not in results and PATCH_SIGNATURE in func.body:
                results.append(func)

    return results


def detect_availability_gates(data: bytes) -> list[FunctionMatch]:
    """Find availability gate functions — both patched and unpatched.

    The availability function does NOT directly contain the Statsig flag
    name (it calls a helper that fetches it). Instead we identify it by:
      - Contains ?.enabled and ?.available optional chaining checks
      - Short function (< 300 bytes body)
      - OR: use the runner gate as a trampoline — extract the function
        name from the runner's if(!XXXX()) pattern and find it.

    Patched: contains our bypass comment tag.
    """
    seen: set[tuple[int, int]] = set()
    gates: list[FunctionMatch] = []

    # Strategy 1: find functions containing ?.enabled AND ?.available
    # These markers are specific enough to the availability gate
    for marker in AVAILABILITY_MARKERS:
        for func in find_functions_containing(data, marker):
            if (
                (func.start, func.end) not in seen
                and _body_contains_all(func, AVAILABILITY_MARKERS)
                and len(func.body) < 300
            ):
                seen.add((func.start, func.end))
                gates.append(func)

    # Strategy 2: trampoline via runner gate — extract called function name
    # Runner has pattern: if(!XXXX())return![01] where XXXX is avail func
    if not gates:
        runners = detect_runner_gates(data)
        for runner in runners:
            m = re.search(rb"if\(!(\w+)\(\)\)return![01]", runner.body)
            if m:
                avail_name = m.group(1)
                # Find function declarations with this name
                decl_pat = rb"function\s+" + re.escape(avail_name) + rb"\s*\("
                for dm in re.finditer(decl_pat, data):
                    func = find_enclosing_function(data, dm.start())
                    if func and (func.start, func.end) not in seen:
                        if len(func.body) < 300:
                            seen.add((func.start, func.end))
                            gates.append(func)

    # Strategy 3: already patched by us
    for func in _find_patched_functions(data, "availability"):
        if (func.start, func.end) not in seen:
            seen.add((func.start, func.end))
            gates.append(func)

    return gates


def detect_skill_gates(data: bytes) -> list[FunctionMatch]:
    """Find skill gate functions — both patched and unpatched.

    Unpatched characteristics:
      - References "tengu_kairos_dream"
      - Contains ("tengu_kairos_dream" as function argument (minifier-resilient)
      - Short function (< 200 bytes body)
      - Does NOT contain autoDreamEnabled (that's the runner gate)

    Patched: contains our bypass comment tag.
    """
    # Unpatched
    gates = []
    for func in find_functions_containing(data, ANCHOR_SKILL):
        if (
            _body_contains_all(func, SKILL_MARKERS)
            and len(func.body) < 200
            and ANCHOR_RUNNER_SETTING not in func.body
        ):
            gates.append(func)

    # Already patched
    for func in _find_patched_functions(data, "skill"):
        if func not in gates:
            gates.append(func)

    return gates


def detect_runner_gates(data: bytes) -> list[FunctionMatch]:
    """Find runner gate functions — both patched and unpatched.

    Unpatched characteristics:
      - References autoDreamEnabled
      - Contains if(!XXXX())return!1
      - Short function (< 300 bytes body)

    Patched: same function but return!1 flipped to return!0.
    """
    gates = []
    for func in find_functions_containing(data, ANCHOR_RUNNER_SETTING):
        if len(func.body) < 300:
            # Match both unpatched (return!1) and patched (return!0)
            if re.search(rb"if\(!\w+\(\)\)return![01]", func.body):
                gates.append(func)

    return gates


# ---------------------------------------------------------------------------
# Patch generation — same-length byte replacements
# ---------------------------------------------------------------------------

def make_bypass_function(func: FunctionMatch, gate_type: str) -> PatchSite:
    """Replace a function body with return!0, padded to exact same length.

    Result: function NAME(){return!0;/*<padded comment>*/}
    """
    m = re.match(
        rb"(function\s+[\w$]+\s*\([^)]*\)\s*\{)(.*?)(\})\s*$",
        func.body,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError(f"Cannot parse function {func.name} at {func.start}")

    prefix = m.group(1)  # function NAME(){
    old_inner = m.group(2)
    suffix = m.group(3)  # }
    inner_len = len(old_inner)

    # Build: return!0;/*<comment>*/
    bypass = BYPASS_PREFIX
    comment_open = b"/*"
    comment_close = b"*/"
    overhead = len(bypass) + len(comment_open) + len(comment_close)

    if inner_len < overhead:
        # Extremely short body — pad return!0 with semicolons
        new_inner = (bypass + b";" * inner_len)[:inner_len]
    else:
        comment_space = inner_len - overhead
        # Descriptive comment text
        tag = f"patched:{gate_type}:v1".encode("ascii")
        padding = tag[:comment_space].ljust(comment_space)
        # Safety: ensure no */ inside comment
        padding = padding.replace(b"*/", b"* ")
        new_inner = bypass + comment_open + padding + comment_close

    assert len(new_inner) == inner_len, (
        f"Inner length mismatch for {func.name}: "
        f"{len(new_inner)} != {inner_len}"
    )

    replacement = prefix + new_inner + suffix
    assert len(replacement) == len(func.body)

    return PatchSite(
        offset=func.start,
        original=func.body,
        replacement=replacement,
        gate_type=gate_type,
        description=(
            f"{gate_type} gate function {func.name}() at offset {func.start}: "
            f"body replaced with return!0"
        ),
    )


def make_runner_flip(data: bytes, func: FunctionMatch) -> PatchSite:
    """Flip return!1 -> return!0 in the runner gate's availability check.

    This is a 1-byte patch: the '1' in 'return!1' becomes '0'.
    """
    pattern = re.compile(rb"if\(!\w+\(\)\)return!1")
    m = pattern.search(func.body)
    if not m:
        raise RuntimeError(
            f"Cannot find if(!XX())return!1 in runner gate {func.name}"
        )

    # The byte to flip is the last char of the match: '1' → '0'
    match_text = m.group()
    rel_offset = m.start() + len(match_text) - 1
    abs_offset = func.start + rel_offset

    assert data[abs_offset] == ord("1"), (
        f"Expected '1' at offset {abs_offset}, got {chr(data[abs_offset])}"
    )

    return PatchSite(
        offset=abs_offset,
        original=b"1",
        replacement=b"0",
        gate_type="runner",
        description=(
            f"runner gate {func.name}() at offset {abs_offset}: "
            f"return!1 -> return!0"
        ),
    )


# ---------------------------------------------------------------------------
# Patch detection (for status check)
# ---------------------------------------------------------------------------

def is_function_patched(func: FunctionMatch) -> bool:
    """Check if a function body already starts with our bypass."""
    inner = func.inner_body
    return inner.lstrip().startswith(BYPASS_PREFIX)


def is_runner_patched(data: bytes, func: FunctionMatch) -> bool:
    """Check if the runner gate already has return!0 (not !1)."""
    # Look for if(!XX())return!0 (patched) vs return!1 (original)
    has_patched = bool(re.search(rb"if\(!\w+\(\)\)return!0", func.body))
    has_original = bool(re.search(rb"if\(!\w+\(\)\)return!1", func.body))
    return has_patched and not has_original


# ---------------------------------------------------------------------------
# Backup management
# ---------------------------------------------------------------------------

BACKUP_SUFFIX = ".dream-backup"
METADATA_FILE = ".dream-patch-meta.json"


def backup_binary(binary_path: Path) -> Path:
    """Create a timestamped backup of the binary."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{binary_path.name}.{ts}{BACKUP_SUFFIX}"
    backup_path = binary_path.parent / backup_name
    shutil.copy2(binary_path, backup_path)
    return backup_path


def find_latest_backup(binary_path: Path) -> Optional[Path]:
    """Find the most recent backup file."""
    parent = binary_path.parent
    pattern = f"{binary_path.name}.*{BACKUP_SUFFIX}"
    backups = sorted(parent.glob(pattern), key=lambda p: p.stat().st_mtime)
    return backups[-1] if backups else None


def save_metadata(binary_path: Path, report: PatchReport):
    """Save patch metadata alongside the binary."""
    meta_path = binary_path.parent / METADATA_FILE
    meta = {
        "version": report.version,
        "patched_at": datetime.now(timezone.utc).isoformat(),
        "sha256_before": report.sha256_before,
        "sha256_after": report.sha256_after,
        "backup": report.backup_path,
        "patches": [
            {
                "gate_type": p.gate_type,
                "offset": p.offset,
                "length": p.length,
                "description": p.description,
            }
            for p in report.patches
        ],
    }
    meta_path.write_text(json.dumps(meta, indent=2))


def load_metadata(binary_path: Path) -> Optional[dict]:
    """Load patch metadata if it exists."""
    meta_path = binary_path.parent / METADATA_FILE
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    return None


# ---------------------------------------------------------------------------
# Main operations
# ---------------------------------------------------------------------------

def analyze_binary(data: bytes) -> dict:
    """Find all gate functions and their patch status."""
    avail = detect_availability_gates(data)
    skill = detect_skill_gates(data)
    runner = detect_runner_gates(data)

    return {
        "availability": {
            "found": len(avail),
            "functions": avail,
            "patched": [is_function_patched(f) for f in avail],
        },
        "skill": {
            "found": len(skill),
            "functions": skill,
            "patched": [is_function_patched(f) for f in skill],
        },
        "runner": {
            "found": len(runner),
            "functions": runner,
            "patched": [is_runner_patched(data, f) for f in runner],
        },
    }


def do_patch(binary_path: Path, dry_run: bool = False) -> PatchReport:
    """Patch the Claude Code binary to enable dream features."""
    version = get_version(binary_path)
    data = bytearray(binary_path.read_bytes())
    sha_before = hashlib.sha256(data).hexdigest()

    report = PatchReport(
        success=False,
        version=version,
        binary_path=str(binary_path),
        operation="patch" if not dry_run else "dry-run",
        sha256_before=sha_before,
    )

    analysis = analyze_binary(bytes(data))
    all_patches: list[PatchSite] = []

    # --- Availability gates ---
    for i, func in enumerate(analysis["availability"]["functions"]):
        if analysis["availability"]["patched"][i]:
            report.messages.append(
                f"availability gate {func.name}() already patched (skip)"
            )
            continue
        try:
            patch = make_bypass_function(func, "availability")
            all_patches.append(patch)
            report.messages.append(
                f"availability gate {func.name}() at {func.start}: "
                f"{len(func.body)}B -> return!0"
            )
        except Exception as e:
            report.errors.append(f"availability gate {func.name}(): {e}")

    # --- Skill gates ---
    for i, func in enumerate(analysis["skill"]["functions"]):
        if analysis["skill"]["patched"][i]:
            report.messages.append(
                f"skill gate {func.name}() already patched (skip)"
            )
            continue
        try:
            patch = make_bypass_function(func, "skill")
            all_patches.append(patch)
            report.messages.append(
                f"skill gate {func.name}() at {func.start}: "
                f"{len(func.body)}B -> return!0"
            )
        except Exception as e:
            report.errors.append(f"skill gate {func.name}(): {e}")

    # --- Runner gates ---
    for i, func in enumerate(analysis["runner"]["functions"]):
        if analysis["runner"]["patched"][i]:
            report.messages.append(
                f"runner gate {func.name}() already patched (skip)"
            )
            continue
        try:
            patch = make_runner_flip(bytes(data), func)
            all_patches.append(patch)
            report.messages.append(patch.description)
        except Exception as e:
            report.errors.append(f"runner gate {func.name}(): {e}")

    # --- Validation ---
    if not analysis["availability"]["functions"]:
        report.errors.append(
            f"No availability gate found (searched for {ANCHOR_AVAILABILITY!r}). "
            "The gating architecture may have changed in this version."
        )
    if not analysis["skill"]["functions"]:
        report.errors.append(
            f"No skill gate found (searched for {ANCHOR_SKILL!r}). "
            "The gating architecture may have changed in this version."
        )
    if not analysis["runner"]["functions"]:
        report.errors.append(
            f"No runner gate found (searched for {ANCHOR_RUNNER_SETTING!r}). "
            "The gating architecture may have changed in this version."
        )

    if not all_patches:
        if not report.errors:
            report.messages.append("All gates already patched — nothing to do")
            report.success = True
        return report

    if report.errors:
        return report

    # --- Apply ---
    if dry_run:
        report.patches = all_patches
        report.success = True
        report.messages.append(
            f"Dry run: {len(all_patches)} patches would be applied"
        )
        return report

    # Backup
    backup_path = backup_binary(binary_path)
    report.backup_path = str(backup_path)
    report.messages.append(f"Backup saved: {backup_path.name}")

    # Apply patches
    for patch in all_patches:
        # Verify original bytes match
        actual = bytes(data[patch.offset : patch.offset + patch.length])
        if actual != patch.original:
            report.errors.append(
                f"Byte mismatch at {patch.offset} for {patch.gate_type} gate "
                f"(expected {len(patch.original)}B, got different content). "
                "Binary may have been modified."
            )
            return report

        data[patch.offset : patch.offset + patch.length] = patch.replacement

    assert len(data) == binary_path.stat().st_size, "Size changed after patching"

    report.sha256_after = hashlib.sha256(data).hexdigest()
    report.patches = all_patches

    # Write — handle Windows locked binary via rename swap
    try:
        _atomic_write(binary_path, bytes(data))
    except PermissionError:
        # Binary is running (Windows) — use rename-swap
        try:
            _rename_swap_write(binary_path, bytes(data))
            report.messages.append(
                "Used rename-swap (binary was locked by running process)"
            )
        except Exception as e:
            report.errors.append(f"Failed to write patched binary: {e}")
            return report

    # Verify written bytes match what we wrote (before any re-signing)
    written = binary_path.read_bytes()
    written_hash = hashlib.sha256(written).hexdigest()
    if written_hash != report.sha256_after:
        report.errors.append("Post-write hash mismatch — patch may be corrupt")
        return report

    # macOS: re-sign ad-hoc because byte edits invalidate the Apple signature.
    # This deliberately happens after the hash check — codesign mutates the
    # Mach-O signature blob, so post-sign sha256 will differ from the planned
    # patch hash. We update sha256_after to reflect the final on-disk bytes.
    if _is_macos():
        ok, msg = ad_hoc_sign_macos(binary_path)
        if ok:
            if msg:
                report.messages.append(msg)
            report.sha256_after = hashlib.sha256(
                binary_path.read_bytes()
            ).hexdigest()
        else:
            report.errors.append(msg)
            return report

    save_metadata(binary_path, report)

    report.success = True
    report.messages.append(
        f"Patched {len(all_patches)} sites in v{version}"
    )
    return report


def do_restore(binary_path: Path) -> PatchReport:
    """Restore the original binary from backup."""
    version = get_version(binary_path)
    report = PatchReport(
        success=False,
        version=version,
        binary_path=str(binary_path),
        operation="restore",
    )

    backup = find_latest_backup(binary_path)
    if not backup:
        report.errors.append(
            f"No backup found matching {binary_path.name}.*{BACKUP_SUFFIX}"
        )
        return report

    report.backup_path = str(backup)

    try:
        _atomic_write(binary_path, backup.read_bytes())
    except PermissionError:
        try:
            _rename_swap_write(binary_path, backup.read_bytes())
            report.messages.append("Used rename-swap for restore")
        except Exception as e:
            report.errors.append(f"Failed to restore: {e}")
            return report

    # Clean up metadata
    meta_path = binary_path.parent / METADATA_FILE
    if meta_path.exists():
        meta_path.unlink()

    report.success = True
    report.messages.append(f"Restored from {backup.name}")
    return report


def do_status(binary_path: Path) -> PatchReport:
    """Check current patch status of the binary."""
    version = get_version(binary_path)
    data = binary_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()

    report = PatchReport(
        success=True,
        version=version,
        binary_path=str(binary_path),
        operation="status",
        sha256_before=sha,
    )

    analysis = analyze_binary(data)
    meta = load_metadata(binary_path)
    backup = find_latest_backup(binary_path)

    for gate_type in ("availability", "skill", "runner"):
        info = analysis[gate_type]
        n = info["found"]
        patched = sum(info["patched"])
        names = [f.name for f in info["functions"]]

        if n == 0:
            report.messages.append(f"{gate_type}: not found")
        elif patched == n:
            report.messages.append(
                f"{gate_type}: PATCHED ({patched}/{n}) "
                f"functions: {', '.join(names)}"
            )
        elif patched > 0:
            report.messages.append(
                f"{gate_type}: PARTIALLY PATCHED ({patched}/{n}) "
                f"functions: {', '.join(names)}"
            )
        else:
            report.messages.append(
                f"{gate_type}: unpatched ({n} found) "
                f"functions: {', '.join(names)}"
            )

    if backup:
        report.backup_path = str(backup)
        report.messages.append(f"latest backup: {backup.name}")

    if meta:
        report.messages.append(
            f"last patched: {meta.get('patched_at', 'unknown')} "
            f"(v{meta.get('version', '?')})"
        )

    return report


# ---------------------------------------------------------------------------
# File writing helpers
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, data: bytes):
    """Write data to path atomically via temp file + rename.

    Preserves the original file mode so the execute bit (crucial on
    macOS/Linux) survives the replacement — a freshly created temp file
    defaults to 0644 which would leave the binary unrunnable.
    """
    tmp = path.with_suffix(path.suffix + ".dream-tmp")
    tmp.write_bytes(data)
    if path.exists():
        try:
            shutil.copymode(str(path), str(tmp))
        except OSError:
            pass  # non-fatal; we'll still try to replace
    os.replace(str(tmp), str(path))


def _rename_swap_write(path: Path, data: bytes):
    """Write by renaming the locked original out and the new file in.

    On Windows, a running .exe can be renamed but not overwritten.
    """
    running = path.with_suffix(path.suffix + ".dream-running")
    tmp = path.with_suffix(path.suffix + ".dream-tmp")

    # Clean up stale files from previous swaps
    for stale in (running, tmp):
        if stale.exists():
            try:
                stale.unlink()
            except PermissionError:
                pass

    tmp.write_bytes(data)

    try:
        os.rename(str(path), str(running))
    except PermissionError:
        tmp.unlink()
        raise RuntimeError(
            "Cannot rename running binary. Close all Claude Code "
            "sessions and retry."
        )

    os.rename(str(tmp), str(path))
    # running file can be cleaned up after process exits


# ---------------------------------------------------------------------------
# macOS code signature handling
# ---------------------------------------------------------------------------

def _is_macos() -> bool:
    return platform.system() == "Darwin"


def ad_hoc_sign_macos(binary_path: Path) -> tuple[bool, str]:
    """Re-sign the binary with an ad-hoc signature on macOS.

    Any byte-level modification invalidates the original Apple code
    signature, after which macOS refuses to load the binary (typically
    with SIGKILL on arm64). Applying an ad-hoc signature
    (`codesign --force --sign -`) restores a locally-valid signature so
    the kernel will execute it again.

    Returns (success, message). A no-op on non-macOS platforms.
    """
    if not _is_macos():
        return True, ""

    import subprocess
    try:
        result = subprocess.run(
            ["codesign", "--force", "--sign", "-", str(binary_path)],
            capture_output=True, text=True, timeout=60,
        )
    except FileNotFoundError:
        return False, (
            "codesign not found — install Xcode Command Line Tools "
            "(`xcode-select --install`) and re-run patch"
        )
    except Exception as e:
        return False, f"codesign invocation failed: {e}"

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        return False, f"codesign failed (exit {result.returncode}): {err}"

    return True, "ad-hoc re-signed (macOS)"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_report(report: PatchReport) -> str:
    """Format a PatchReport for terminal output."""
    lines = []
    status = "OK" if report.success else "FAILED"
    lines.append(f"[{status}] {report.operation} — Claude Code v{report.version}")
    lines.append(f"  binary: {report.binary_path}")

    if report.sha256_before:
        lines.append(f"  sha256: {report.sha256_before[:16]}...")
    if report.sha256_after and report.sha256_after != report.sha256_before:
        lines.append(f"  sha256 (after): {report.sha256_after[:16]}...")
    if report.backup_path:
        lines.append(f"  backup: {Path(report.backup_path).name}")

    for msg in report.messages:
        lines.append(f"  • {msg}")
    for err in report.errors:
        lines.append(f"  ✗ {err}")

    if report.success and report.operation == "patch":
        lines.append("")
        lines.append("  Next steps:")
        lines.append("  1. Restart Claude Code (new session)")
        lines.append('  2. Ensure autoDreamEnabled: true in ~/.claude/settings.json')
        lines.append('  3. Ensure DISABLE_AUTOUPDATER: "1" in settings env')
        lines.append("  4. Test: /memory (toggle) and /dream (command)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code Dream Feature Patcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s patch              Patch the binary\n"
            "  %(prog)s patch --dry-run    Show what would be patched\n"
            "  %(prog)s status             Check current state\n"
            "  %(prog)s restore            Restore from backup\n"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    p_patch = sub.add_parser("patch", help="Patch the binary")
    p_patch.add_argument("--dry-run", action="store_true", help="Preview only")
    p_patch.add_argument("--binary", help="Explicit path to claude binary")
    p_patch.add_argument("--json", action="store_true", help="JSON output")

    p_restore = sub.add_parser("restore", help="Restore from backup")
    p_restore.add_argument("--binary", help="Explicit path to claude binary")
    p_restore.add_argument("--json", action="store_true", help="JSON output")

    p_status = sub.add_parser("status", help="Check patch status")
    p_status.add_argument("--binary", help="Explicit path to claude binary")
    p_status.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        binary_path = find_claude_binary(
            getattr(args, "binary", None)
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "patch":
        report = do_patch(binary_path, dry_run=args.dry_run)
    elif args.command == "restore":
        report = do_restore(binary_path)
    elif args.command == "status":
        report = do_status(binary_path)
    else:
        parser.print_help()
        sys.exit(1)

    if getattr(args, "json", False):
        out = {
            "success": report.success,
            "version": report.version,
            "operation": report.operation,
            "binary": report.binary_path,
            "backup": report.backup_path,
            "sha256_before": report.sha256_before,
            "sha256_after": report.sha256_after,
            "messages": report.messages,
            "errors": report.errors,
            "patches": [
                {
                    "gate_type": p.gate_type,
                    "offset": p.offset,
                    "length": p.length,
                    "description": p.description,
                }
                for p in report.patches
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        print(format_report(report))

    sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
