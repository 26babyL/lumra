#!/usr/bin/env python3
"""
lumra_blueprint_fixer_v2.py
============================
Lumra ERP — Blueprint Auto-Fixer v2.0
Lanjutan dari fixer v1 — membaca audit_after.html (bukan JSON).

Perubahan dari v1:
  - Input: audit_after.html (HTML report dari auditor)
  - Expanded hex color map: 70+ warna baru yang tersisa
  - D1: deteksi hex pendek (#111, #aaa, #ccc, dll.)
  - D7: inline style hex map diperluas sama dengan D1
  - D3: snap 6px→8px, 14px→16px, 13px→12px
  - C4: fix per-baris lebih presisi (bukan global rename)
  - D5: inject is-loading comment ke navbar/modal/kpi_card

Cara pakai:
  python lumra_blueprint_fixer_v2.py                           # fix semua
  python lumra_blueprint_fixer_v2.py --audit audit_after.html
  python lumra_blueprint_fixer_v2.py --only D1,D7,D3
  python lumra_blueprint_fixer_v2.py --dry-run
  python lumra_blueprint_fixer_v2.py --no-backup
"""

import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_AUDIT_HTML = Path("audit_after.html")
DEFAULT_HTML_ROOT  = Path("lumra_config/templates")
DEFAULT_PY_ROOT    = Path("lumra_config")
BACKUP_DIR         = Path(".lumra_fixer_backup")

ALL_CATEGORIES = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "C2", "C3", "C4", "C5"}

# ── D1 + D7: Extended hex → token mapping ─────────────────────────
# Diurutkan dari lebih spesifik ke lebih umum
# Format: (exact_hex_lowercase, css_token)
HEX_TOKEN_MAP = {
    # Odyssey & brand variants
    "#00c97e":  "var(--color-secondary)",
    "#00674f":  "var(--color-primary)",
    "#00a86b":  "var(--color-secondary)",
    "#047857":  "var(--color-primary-dark)",
    "#059669":  "var(--color-success)",
    "#34d399":  "var(--color-success-light)",

    # Dark emerald tones (about.html heavy usage)
    "#0a1a14":  "var(--color-surface-dark)",
    "#080f0b":  "var(--color-surface-dark)",
    "#060e09":  "var(--color-surface-dark)",
    "#0a0f0a":  "var(--color-surface-dark)",
    "#0f1a0f":  "var(--color-surface-dark)",
    "#08120d":  "var(--color-surface-dark)",
    "#060814":  "var(--color-bg-deep)",
    "#0a1409":  "var(--color-surface-dark)",
    "#010101":  "var(--color-text-primary)",
    "#0a0a0a":  "var(--color-text-primary)",
    "#1a2e24":  "var(--color-primary-dark)",
    "#4a5a50":  "var(--color-text-muted)",
    "#607060":  "var(--color-text-muted)",
    "#7a8a7a":  "var(--color-text-muted)",

    # Light surface / background
    "#f0faf5":  "var(--color-surface-emerald)",
    "#f8faf8":  "var(--color-surface-light)",
    "#f0f4ff":  "var(--color-surface-blue)",
    "#f1f5f9":  "var(--color-surface-faint)",
    "#f5f5f0":  "var(--color-surface-faint)",
    "#f7f7f4":  "var(--color-surface-faint)",
    "#e8ede6":  "var(--color-border-light)",
    "#f0f0ec":  "var(--color-surface-faint)",
    "#eff6ff":  "var(--color-bg-info)",
    "#bfdbfe":  "var(--color-info-light)",
    "#c9e8f0":  "var(--color-info-faint)",

    # Blues
    "#0284c7":  "var(--color-info)",
    "#0ea5e9":  "var(--color-info)",
    "#3b82f6":  "var(--color-info)",
    "#1877f2":  "var(--color-info)",
    "#4f46e5":  "var(--color-indigo)",
    "#6366f1":  "var(--color-indigo)",
    "#a5b4fc":  "var(--color-indigo-light)",
    "#4f3cc9":  "var(--color-indigo)",
    "#003087":  "var(--color-navy)",
    "#0f172a":  "var(--color-bg-deep)",
    "#1e293b":  "var(--color-text-primary)",

    # Purples
    "#7c3aed":  "var(--color-purple)",
    "#8b5cf6":  "var(--color-purple)",

    # Teals
    "#00aed6":  "var(--color-teal)",
    "#14b8a6":  "var(--color-teal)",

    # Reds / danger
    "#dc2626":  "var(--color-danger)",
    "#ef4444":  "var(--color-danger)",
    "#e11d48":  "var(--color-danger)",
    "#f43f5e":  "var(--color-danger)",
    "#be185d":  "var(--color-pink)",
    "#ec4899":  "var(--color-pink)",
    "#e1306c":  "var(--color-pink)",

    # Oranges / warnings
    "#f59e0b":  "var(--color-warning)",
    "#d97706":  "var(--color-warning)",
    "#f97316":  "var(--color-orange)",
    "#92400e":  "var(--color-warning-dark)",
    "#7a6000":  "var(--color-warning-dark)",
    "#8b6800":  "var(--color-warning-dark)",
    "#3a2e00":  "var(--color-warning-dark)",

    # Greens
    "#84cc16":  "var(--color-lime)",
    "#25d366":  "var(--color-whatsapp)",

    # Grays / text
    "#475569":  "var(--color-text-secondary)",
    "#64748b":  "var(--color-text-secondary)",
    "#94a3b8":  "var(--color-text-muted)",

    # Short hex
    "#111":     "var(--color-text-primary)",
    "#218":     "var(--color-navy)",
    "#221":     "var(--color-text-primary)",
    "#109":     "var(--color-primary)",
    "#666":     "var(--color-text-secondary)",
    "#aaa":     "var(--color-text-muted)",
    "#bbb":     "var(--color-text-muted)",
    "#ccc":     "var(--color-border)",
}

# ── D1 + D7: rgba → token (extended) ─────────────────────────────
RGBA_TOKEN_MAP = [
    # Putih opacity tinggi
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.9[5-9]\s*\)", "var(--color-surface-high)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.9[0-4]\s*\)", "var(--color-surface-high)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[7-8][0-9]\s*\)", "var(--color-surface-mid)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[5-6][0-9]?\s*\)", "var(--color-surface-mid)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[3-4][0-9]?\s*\)", "var(--color-surface-glass)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[1-2][0-9]?\s*\)", "var(--color-surface-glass)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.0[5-9]\s*\)", "var(--color-surface-faint)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.0[1-4]\s*\)", "var(--color-surface-faint)"),
    # Hitam overlay
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[5-9][0-9]?\s*\)", "var(--color-overlay-heavy)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[3-4][0-9]?\s*\)", "var(--color-overlay-heavy)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[1-2][0-9]?\s*\)", "var(--color-overlay-md)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[7-9]\s*\)", "var(--color-overlay-sm)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[4-6]\s*\)", "var(--color-overlay-sm)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[1-3]\s*\)", "var(--color-overlay-xs)"),
    # Emerald/primary alpha
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*([\d.]+)\s*\)",  "var(--color-primary-alpha)"),
    (r"rgba\(\s*0\s*,\s*168\s*,\s*107\s*,\s*([\d.]+)\s*\)", "var(--color-secondary-alpha)"),
    # Slate/gray overlay
    (r"rgba\(\s*15\s*,\s*23\s*,\s*42\s*,\s*0\.[5-9][0-9]?\s*\)", "var(--color-overlay-heavy)"),
    (r"rgba\(\s*15\s*,\s*23\s*,\s*42\s*,\s*0\.[1-4][0-9]?\s*\)", "var(--color-overlay-md)"),
    (r"rgba\(\s*30\s*,\s*41\s*,\s*59\s*,\s*([\d.]+)\s*\)", "var(--color-overlay-md)"),
]

# ── D3: snap table ────────────────────────────────────────────────
def snap_to_grid(val: float) -> int:
    iv = int(val)
    if iv % 4 == 0:
        return iv
    return round(iv / 4) * 4

# ── D4: valid sets ─────────────────────────────────────────────────
VALID_FONT_SIZES   = {10, 11, 13, 14, 16, 18, 20, 22, 24, 28, 32, 36}
VALID_FONT_WEIGHTS = {400, 500, 600, 700}

def snap_font_size(val: float) -> int:
    return min(VALID_FONT_SIZES, key=lambda s: abs(s - val))

def snap_font_weight(val: int) -> int:
    return min(VALID_FONT_WEIGHTS, key=lambda w: abs(w - val))

# ── C4: rename map ─────────────────────────────────────────────────
RENAME_VAR_MAP = {
    "data":   "records",
    "obj":    "model_instance",
    "val":    "field_value",
    "item":   "record_item",
    "res":    "response_data",
    "result": "query_result",
    "tmp":    "temp_value",
    "temp":   "temp_value",
    "flag":   "is_valid",
    "check":  "is_checked",
    "info":   "detail_info",
    "stuff":  "payload",
    "value":  "field_value",
    "x":      "x_coord",
    "y":      "y_coord",
}


# ══════════════════════════════════════════════════════════════════
# TERMINAL COLORS
# ══════════════════════════════════════════════════════════════════

USE_COLOR = True

def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text

def green(t):   return _c("92", t)
def yellow(t):  return _c("93", t)
def red(t):     return _c("91", t)
def cyan(t):    return _c("96", t)
def dim(t):     return _c("2",  t)
def bold(t):    return _c("1",  t)
def magenta(t): return _c("95", t)

def hr(char="─", n=70):
    return cyan(char * n)


# ══════════════════════════════════════════════════════════════════
# PARSE AUDIT HTML
# ══════════════════════════════════════════════════════════════════

def parse_audit_html(html_path: Path) -> dict[str, list[dict]]:
    """
    Ekstrak semua violations dari HTML report auditor.
    Return: {file_path: [violation_dict, ...]}
    """
    content = html_path.read_text(encoding="utf-8")
    rows = re.findall(
        r'<tr>\s*<td><span class="badge"[^>]*>(\w+)</span></td>'
        r'\s*<td><span class="cat-badge">(\w+)</span></td>'
        r'\s*<td class="file-path">([^<]+)</td>'
        r'\s*<td class="line-num">L(\d+)</td>'
        r'\s*<td>([^<]*)</td>'
        r'\s*<td class="fix-hint">([^<]*)</td>',
        content,
    )
    by_file: dict[str, list] = defaultdict(list)
    for sev, cat, fpath, line, msg, hint in rows:
        by_file[fpath.strip()].append({
            "severity": sev.strip(),
            "category": cat.strip(),
            "file":     fpath.strip(),
            "line":     int(line),
            "message":  msg.strip(),
            "fix_hint": hint.strip(),
        })
    return dict(by_file)


# ══════════════════════════════════════════════════════════════════
# FILE FIXER HELPER
# ══════════════════════════════════════════════════════════════════

class FileFixer:
    def __init__(self, path: Path, dry_run: bool, verbose: bool, backup_root):
        self.path        = path
        self.dry_run     = dry_run
        self.verbose     = verbose
        self.backup_root = backup_root
        self.original    = None
        self.content     = None
        self.changes     = []

    def load(self) -> bool:
        if not self.path.exists():
            return False
        try:
            self.original = self.path.read_text(encoding="utf-8")
            self.content  = self.original
            return True
        except Exception as e:
            print(f"  {red('✖')} Gagal baca {self.path}: {e}")
            return False

    def save(self) -> int:
        if self.content == self.original:
            return 0
        if not self.dry_run:
            if self.backup_root:
                rel  = self.path
                dest = self.backup_root / self.path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.copy2(self.path, dest)
            self.path.write_text(self.content, encoding="utf-8")
        return len(self.changes)

    def replace(self, pattern: str, replacement: str, flags=re.IGNORECASE, label="") -> int:
        try:
            count = len(re.findall(pattern, self.content, flags=flags))
            new   = re.sub(pattern, replacement, self.content, flags=flags)
        except re.error:
            return 0
        if new != self.content:
            self.content = new
            self.changes.append((label or pattern[:40], count))
            if self.verbose:
                print(f"      {dim('→')} {dim((label or pattern)[:70])} ({count}x)")
        return count

    def get_lines(self) -> list[str]:
        return self.content.splitlines(keepends=True)

    def set_lines(self, lines: list[str]):
        self.content = "".join(lines)

    def get_line(self, lineno: int) -> str:
        lines = self.get_lines()
        return lines[lineno - 1] if 0 < lineno <= len(lines) else ""

    def replace_line(self, lineno: int, new_line: str) -> bool:
        lines = self.get_lines()
        if 0 < lineno <= len(lines):
            if lines[lineno - 1].rstrip("\n") != new_line.rstrip("\n"):
                lines[lineno - 1] = new_line
                self.set_lines(lines)
                self.changes.append((f"line {lineno}", 1))
                return True
        return False

    def insert_before_line(self, lineno: int, text: str) -> bool:
        lines = self.get_lines()
        if 0 < lineno <= len(lines):
            lines.insert(lineno - 1, text)
            self.set_lines(lines)
            self.changes.append((f"insert L{lineno}", 1))
            return True
        return False


# ══════════════════════════════════════════════════════════════════
# [D1] Palette — rgba + hex hardcode → token
# ══════════════════════════════════════════════════════════════════

def fix_d1(fixer: FileFixer, violations: list) -> int:
    total = 0

    # 1. rgba patterns (broad, applies to all content)
    for pattern, token in RGBA_TOKEN_MAP:
        total += fixer.replace(pattern, token, label=f"D1 rgba→{token}")

    # 2. hex colors — dari violations, extract hex yang perlu diganti
    hex_seen = set()
    for v in violations:
        m = re.search(r"(#[0-9a-fA-F]{3,6})\b", v["message"])
        if m:
            hex_seen.add(m.group(1).lower())

    # Juga apply semua mapping yang ada (karena banyak file yang sama)
    for hex_val, token in HEX_TOKEN_MAP.items():
        # Jangan ganti hex yang ada di dalam var() atau url()
        pattern = rf"(?<!var\()(?<!url\()(?<![\"'#\w]){re.escape(hex_val)}(?![0-9a-fA-F\"'\w])"
        total  += fixer.replace(pattern, token, flags=re.IGNORECASE, label=f"D1 {hex_val}→{token}")

    return total


# ══════════════════════════════════════════════════════════════════
# [D2] Glass Protocol
# ══════════════════════════════════════════════════════════════════

def fix_d2(fixer: FileFixer, violations: list) -> int:
    total = 0
    for v in violations:
        if "tidak menggunakan class .kpi-glass" in v["message"]:
            line = fixer.get_line(v["line"])
            if "kpi-glass" not in line:
                new_line = re.sub(
                    r'class="([^"]*(?:kpi|stat-card)[^"]*)"',
                    lambda m: f'class="{m.group(1)} kpi-glass"',
                    line, flags=re.IGNORECASE,
                )
                if fixer.replace_line(v["line"], new_line):
                    total += 1

    total += fixer.replace(
        r"backdrop-filter\s*:\s*blur\(([1-9]|1[01])px\)",
        "backdrop-filter: blur(12px)",
        label="D2 blur→12px",
    )
    return total


# ══════════════════════════════════════════════════════════════════
# [D3] Grid 8px
# ══════════════════════════════════════════════════════════════════

SPACING_PROPS_RE = re.compile(
    r"((?:padding|margin|gap|top|left|right|bottom)\s*:\s*)"
    r"([\d.]+)px",
    re.IGNORECASE,
)

def fix_d3(fixer: FileFixer, violations: list) -> int:
    # Kumpulkan nilai buruk dari violations
    bad_vals = set()
    for v in violations:
        m = re.search(r"([\d.]+)px\s*—", v["message"])
        if m:
            bad_vals.add(float(m.group(1)))

    total = 0
    for val in bad_vals:
        snapped = snap_to_grid(val)
        if snapped == int(val):
            continue
        val_str = str(int(val)) if val == int(val) else str(val)
        # Hanya replace dalam context spacing property
        pattern = rf"((?:padding|margin|gap|top|left|right|bottom)\s*:\s*(?:[^;]* )?){re.escape(val_str)}px"
        total  += fixer.replace(pattern, rf"\g<1>{snapped}px", label=f"D3 {val_str}px→{snapped}px")

    return total


# ══════════════════════════════════════════════════════════════════
# [D4] Typography
# ══════════════════════════════════════════════════════════════════

def fix_d4(fixer: FileFixer, violations: list) -> int:
    total = 0
    for v in violations:
        if "font-size" in v["message"]:
            m = re.search(r"font-size:\s*([\d.]+)px", v["message"])
            if m:
                val     = float(m.group(1))
                snapped = snap_font_size(val)
                if snapped != int(val):
                    val_str = str(int(val)) if val == int(val) else str(val)
                    total  += fixer.replace(
                        rf"(font-size\s*:\s*){re.escape(val_str)}px",
                        rf"\g<1>{snapped}px",
                        label=f"D4 fs {val_str}→{snapped}px",
                    )
        elif "font-weight" in v["message"]:
            m = re.search(r"font-weight:\s*(\d+)", v["message"])
            if m:
                val     = int(m.group(1))
                snapped = snap_font_weight(val)
                if snapped != val:
                    total += fixer.replace(
                        rf"(font-weight\s*:\s*){val}\b",
                        rf"\g<1>{snapped}",
                        label=f"D4 fw {val}→{snapped}",
                    )
    return total


# ══════════════════════════════════════════════════════════════════
# [D5] Shimmer
# ══════════════════════════════════════════════════════════════════

D5_COMMENT = (
    "{# BLUEPRINT D5: Tambahkan class is-loading saat data belum tersedia. #}\n"
    "{# Contoh: <div class=\"kpi-glass {% if not kpi_value %}is-loading{% endif %}\"> #}\n"
)

def fix_d5(fixer: FileFixer, violations: list) -> int:
    if not violations:
        return 0
    if "BLUEPRINT D5" in fixer.content:
        return 0
    # Inject sebelum {% block content %} jika ada, atau di awal file
    if "{%" in fixer.content:
        new = re.sub(
            r"(\{%\s*block\s+content\s*%\})",
            D5_COMMENT + r"\1",
            fixer.content, count=1,
        )
    else:
        new = D5_COMMENT + fixer.content
    if new != fixer.content:
        fixer.content = new
        fixer.changes.append(("D5 shimmer comment", 1))
        return 1
    return 0


# ══════════════════════════════════════════════════════════════════
# [D6] Tabel Odyssey
# ══════════════════════════════════════════════════════════════════

def fix_d6(fixer: FileFixer, violations: list) -> int:
    total = 0

    total += fixer.replace(
        r"<table(?!\s[^>]*class=)([^>]*)>",
        r'<table class="tbl-odyssey"\1>',
        label='D6 <table>→tbl-odyssey',
    )

    def append_tbl_class(m):
        existing = m.group(2)
        if "tbl-odyssey" not in existing:
            return f'<table{m.group(1)}class="{existing} tbl-odyssey"{m.group(3)}>'
        return m.group(0)

    new = re.sub(
        r'<table(\s[^>]*)class="([^"]*)"([^>]*)>',
        append_tbl_class, fixer.content, flags=re.IGNORECASE,
    )
    if new != fixer.content:
        fixer.content = new
        fixer.changes.append(("D6 append tbl-odyssey", 1))
        total += 1

    return total


# ══════════════════════════════════════════════════════════════════
# [D7] CSS Token — inline style
# ══════════════════════════════════════════════════════════════════

def fix_d7(fixer: FileFixer, violations: list) -> int:
    total = 0
    # Apply full hex map, tapi hanya dalam konteks style="..."
    for hex_val, token in HEX_TOKEN_MAP.items():
        pattern = rf'(style="[^"]*){re.escape(hex_val)}([^"]*")'
        total  += fixer.replace(
            pattern, rf'\g<1>{token}\2',
            flags=re.IGNORECASE, label=f"D7 {hex_val}→{token}",
        )
    # rgba dalam inline style
    for pattern, token in RGBA_TOKEN_MAP:
        total += fixer.replace(
            rf'(style="[^"]*){pattern}([^"]*")',
            rf'\g<1>{token}\2',
            label=f"D7 rgba→{token}",
        )
    return total


# ══════════════════════════════════════════════════════════════════
# [C2] Anti-Duplicate — inject TODO comment
# ══════════════════════════════════════════════════════════════════

def fix_c2(fixer: FileFixer, violations: list) -> int:
    injected = 0
    lines = fixer.get_lines()
    offset = 0  # track line shifts from insertions
    for v in sorted(violations, key=lambda x: x["line"]):
        lineno = v["line"] + offset
        if lineno > 0 and lineno <= len(lines):
            existing = lines[lineno - 1]
            if "TODO[C2]" not in existing:
                indent = " " * (len(existing) - len(existing.lstrip()))
                comment = indent + "# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah\n"
                lines.insert(lineno - 1, comment)
                offset += 1
                injected += 1
    fixer.set_lines(lines)
    if injected:
        fixer.changes.append(("C2 TODO comments", injected))
    return injected


# ══════════════════════════════════════════════════════════════════
# [C3] Anti-Long Method — inject TODO
# ══════════════════════════════════════════════════════════════════

def fix_c3(fixer: FileFixer, violations: list) -> int:
    injected = 0
    lines  = fixer.get_lines()
    offset = 0
    for v in sorted(violations, key=lambda x: x["line"]):
        lineno = v["line"] + offset
        if lineno <= 0 or lineno > len(lines):
            continue
        existing = lines[lineno - 1]
        if "TODO[C3]" in existing:
            continue
        m_name = re.search(r"Function '(\w+)'", v["message"])
        m_len  = re.search(r"(\d+) baris", v["message"])
        fname  = m_name.group(1) if m_name else "fungsi_ini"
        flen   = m_len.group(1)  if m_len  else "?"
        indent = " " * (len(existing) - len(existing.lstrip()))
        comment = (
            indent +
            f"# TODO[C3-LONG]: '{fname}' terlalu panjang ({flen} baris). "
            f"Pecah: {fname}_validate(), {fname}_build_context(), {fname}_render()\n"
        )
        lines.insert(lineno - 1, comment)
        offset   += 1
        injected += 1
    fixer.set_lines(lines)
    if injected:
        fixer.changes.append(("C3 TODO comments", injected))
    return injected


# ══════════════════════════════════════════════════════════════════
# [C4] Naming — precision rename per-violation-line
# ══════════════════════════════════════════════════════════════════

def fix_c4(fixer: FileFixer, violations: list) -> int:
    total = 0
    lines = fixer.get_lines()

    for v in violations:
        m = re.search(r"terlarang:\s*'(\w+)'", v["message"])
        if not m:
            continue
        bad_name  = m.group(1)
        is_func   = "function" in v["message"].lower()
        good_name = RENAME_VAR_MAP.get(bad_name, f"{bad_name}_value")

        lineno = v["line"] - 1  # 0-indexed
        if lineno < 0 or lineno >= len(lines):
            continue

        line = lines[lineno]

        if is_func:
            # Rename def function_name
            new = re.sub(rf"\bdef\s+{re.escape(bad_name)}\b", f"def {good_name}", line)
        else:
            # Rename dalam assignment — hanya sisi kiri = atau for ... in
            new = re.sub(
                rf"(?<!['\"\w]){re.escape(bad_name)}\b(?=\s*(?:=(?!=)|\s+in\s))",
                good_name, line,
            )

        if new != line:
            lines[lineno] = new
            fixer.changes.append((f"C4 {bad_name}→{good_name} L{v['line']}", 1))
            total += 1

    fixer.set_lines(lines)
    return total


# ══════════════════════════════════════════════════════════════════
# [C5] Architecture — N+1 & fat view comments
# ══════════════════════════════════════════════════════════════════

def fix_c5(fixer: FileFixer, violations: list) -> int:
    injected = 0
    lines  = fixer.get_lines()
    offset = 0
    inserted_lines = set()

    for v in sorted(violations, key=lambda x: x["line"]):
        lineno = v["line"] + offset
        if lineno <= 0 or lineno > len(lines):
            continue
        key = (v["file"], v["line"])
        if key in inserted_lines:
            continue

        existing = lines[lineno - 1]
        is_n1  = "N+1" in v["message"]
        tag    = "TODO[C5-N1]" if is_n1 else "TODO[C5-FAT]"

        if tag in existing:
            continue

        indent = " " * (len(existing) - len(existing.lstrip()))
        if is_n1:
            comment = (
                indent + "# TODO[C5-N1]: Pindahkan query ini ke atas loop.\n" +
                indent + "# Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')\n"
            )
        else:
            indicator = re.search(r"'(\w+)'", v["message"])
            ind_name  = indicator.group(1) if indicator else "fungsi_ini"
            comment   = (
                indent + f"# TODO[C5-FAT]: '{ind_name}' → pindahkan ke services/{{module}}_service.py\n"
            )

        lines.insert(lineno - 1, comment)
        offset         += comment.count("\n")
        injected       += 1
        inserted_lines.add(key)

    fixer.set_lines(lines)
    if injected:
        fixer.changes.append(("C5 TODO comments", injected))
    return injected


# ══════════════════════════════════════════════════════════════════
# DISPATCHER
# ══════════════════════════════════════════════════════════════════

HTML_FIXERS = {"D1": fix_d1, "D2": fix_d2, "D3": fix_d3, "D4": fix_d4,
               "D5": fix_d5, "D6": fix_d6, "D7": fix_d7}
PY_FIXERS   = {"C2": fix_c2, "C3": fix_c3, "C4": fix_c4, "C5": fix_c5}

# Untuk HTML yang berisi kode Python (jarang, tapi aman dicoba)
COMBINED_FIXERS = {**HTML_FIXERS}

def is_html(path_str: str) -> bool:
    return path_str.endswith(".html")

def is_python(path_str: str) -> bool:
    return path_str.endswith(".py")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Lumra Blueprint Auto-Fixer v2 — lanjutan dari fixer v1, input HTML report",
    )
    p.add_argument("--audit",     type=Path, default=DEFAULT_AUDIT_HTML,
                   help=f"Path ke audit HTML report (default: {DEFAULT_AUDIT_HTML})")
    p.add_argument("--html-root", type=Path, default=DEFAULT_HTML_ROOT)
    p.add_argument("--py-root",   type=Path, default=DEFAULT_PY_ROOT)
    p.add_argument("--only",      type=str,  default=None,
                   help="Kategori spesifik: D1,D3,C4")
    p.add_argument("--dry-run",   action="store_true")
    p.add_argument("--no-backup", action="store_true")
    p.add_argument("--verbose",   action="store_true")
    p.add_argument("--no-color",  action="store_true")
    return p.parse_args()


def main():
    global USE_COLOR
    args = parse_args()
    if args.no_color:
        USE_COLOR = False

    categories = (
        {c.strip().upper() for c in args.only.split(",")}
        if args.only else ALL_CATEGORIES
    )

    if not args.audit.exists():
        print(red(f"✖ File audit tidak ditemukan: {args.audit}"))
        print(dim("  Jalankan auditor dengan --html audit_after.html terlebih dahulu."))
        sys.exit(1)

    print(f"\n{hr('═')}")
    print(f"  {bold('Lumra Blueprint Auto-Fixer')}  {dim('v2.0')}")
    if args.dry_run:
        print(f"  {yellow('⚠  DRY-RUN — tidak ada file yang diubah')}")
    print(hr('═'))

    # Parse HTML report
    print(f"  {dim('Membaca')} {bold(str(args.audit))}...", end="", flush=True)
    by_file = parse_audit_html(args.audit)
    total_v = sum(len(vs) for vs in by_file.values())
    print(f" {green('✓')}  {white(str(total_v))} violations di {white(str(len(by_file)))} files")
    print()

    # Setup backup
    backup_root = None
    if not args.no_backup and not args.dry_run:
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = BACKUP_DIR / ts
        backup_root.mkdir(parents=True, exist_ok=True)
        print(f"  {dim('Backup → ' + str(backup_root))}\n")

    print(f"  Kategori aktif : {cyan(', '.join(sorted(categories)))}\n")

    stats        = defaultdict(lambda: {"files": 0, "fixes": 0})
    total_files  = 0
    total_fixes  = 0
    skipped      = 0

    # Grup violations per file + filter kategori aktif
    html_files = {}
    py_files   = {}
    for fpath, violations in sorted(by_file.items()):
        filtered = [v for v in violations if v["category"] in categories]
        if not filtered:
            continue
        if is_python(fpath):
            py_files[fpath] = defaultdict(list)
            for v in filtered:
                py_files[fpath][v["category"]].append(v)
        else:
            html_files[fpath] = defaultdict(list)
            for v in filtered:
                html_files[fpath][v["category"]].append(v)

    # ── HTML ──────────────────────────────────────────────────────
    if html_files:
        print(f"  {bold('HTML Templates')}  ({len(html_files)} files)")
        print(f"  {dim('─' * 65)}")

    for rel_path, cat_violations in html_files.items():
        full_path = args.html_root / rel_path
        fixer     = FileFixer(full_path, args.dry_run, args.verbose, backup_root)

        if not fixer.load():
            print(f"  {yellow('⚠')} Skip: {dim(rel_path)}")
            skipped += 1
            continue

        file_fixes = 0
        for cat, violations in sorted(cat_violations.items()):
            fn = HTML_FIXERS.get(cat)
            if fn:
                n = fn(fixer, violations)
                file_fixes += n
                stats[cat]["fixes"] += n

        saved = fixer.save()
        if saved > 0 or (args.dry_run and file_fixes > 0):
            status = yellow("[DRY]") if args.dry_run else green("✔")
            cats_str = dim(", ".join(sorted(cat_violations.keys())))
            print(f"  {status} {rel_path:<60} {dim(str(file_fixes)+'fx')} [{cats_str}]")
            total_files += 1
            total_fixes += file_fixes
            for cat in cat_violations:
                stats[cat]["files"] += 1
        elif args.verbose:
            print(f"  {dim('–')} {dim(rel_path)}  (no change)")

    # ── Python ────────────────────────────────────────────────────
    if py_files:
        print()
        print(f"  {bold('Python Sources')}  ({len(py_files)} files)")
        print(f"  {dim('─' * 65)}")

    for rel_path, cat_violations in py_files.items():
        full_path = args.py_root / rel_path
        fixer     = FileFixer(full_path, args.dry_run, args.verbose, backup_root)

        if not fixer.load():
            print(f"  {yellow('⚠')} Skip: {dim(rel_path)}")
            skipped += 1
            continue

        file_fixes = 0
        for cat, violations in sorted(cat_violations.items()):
            fn = PY_FIXERS.get(cat)
            if fn:
                n = fn(fixer, violations)
                file_fixes += n
                stats[cat]["fixes"] += n

        saved = fixer.save()
        if saved > 0 or (args.dry_run and file_fixes > 0):
            status = yellow("[DRY]") if args.dry_run else green("✔")
            cats_str = dim(", ".join(sorted(cat_violations.keys())))
            print(f"  {status} {rel_path:<60} {dim(str(file_fixes)+'fx')} [{cats_str}]")
            total_files += 1
            total_fixes += file_fixes
            for cat in cat_violations:
                stats[cat]["files"] += 1
        elif args.verbose:
            print(f"  {dim('–')} {dim(rel_path)}  (no change)")

    # ── Summary ───────────────────────────────────────────────────
    print()
    print(hr('═'))
    print(f"  {bold('Ringkasan Fix')}")
    print(f"  {dim('─' * 50)}")

    if stats:
        print(f"  {'Cat':<8} {'Files':>7} {'Fixes':>8}")
        print(f"  {dim('─' * 25)}")
        for cat in sorted(stats.keys()):
            bar_len = min(stats[cat]["fixes"] // 5 + 1, 20)
            bar     = "▪" * bar_len
            print(f"  {cyan(cat):<8} {str(stats[cat]['files']):>7} {green(str(stats[cat]['fixes'])):>8}  {dim(bar)}")

    print()
    print(f"  Files diproses : {bold(str(total_files))}")
    print(f"  Files dilewati : {yellow(str(skipped))}")
    print(f"  Total fixes    : {green(bold(str(total_fixes)))}")
    print()

    manual = categories & {"C2", "C3"}
    if manual:
        print(f"  {yellow('⚠  Perlu review manual:')} {', '.join(sorted(manual))}")
        print(f"  {dim('   TODO comments sudah diinjeksi — search TODO[C2]/TODO[C3] dan refactor.')}")
        print()

    if args.dry_run:
        print(f"  {yellow('── DRY-RUN: hilangkan --dry-run untuk apply perubahan ──')}")
    elif total_fixes > 0:
        print(f"  {green('✔ Selesai!')} Verifikasi dengan:")
        print(f"  {dim('  python lumra_blueprint_auditor.py --report audit_v3.json --html audit_v3.html')}")

    print(hr('═'))
    print()


def white(t): return _c("97", t)

if __name__ == "__main__":
    main()