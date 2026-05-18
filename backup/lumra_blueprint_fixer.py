#!/usr/bin/env python3
"""
lumra_blueprint_fixer.py
========================
Lumra ERP — Emerald Odyssey Blueprint Auto-Fixer v1.0

Membaca audit.json dan memperbaiki SEMUA violations secara otomatis:
  [D1] Palette Odyssey     — rgba/hex hardcode → CSS token
  [D2] Glass Protocol      — tambah .kpi-glass, fix blur < 12px
  [D3] Grid 8px            — snap spacing ke kelipatan 4px
  [D4] Typography          — snap font-size/weight ke standar
  [D5] Shimmer Loading     — tambah is-loading state hint
  [D6] Tabel Odyssey       — inject class tbl-odyssey
  [D7] CSS Token           — migrasi inline style hex ke token
  [C2] Anti-Duplicate      — laporan saja (tidak bisa auto-fix)
  [C3] Anti-Long Method    — laporan + extract hint
  [C4] Naming              — rename variable/function terlarang
  [C5] Architecture        — wrap N+1 query dengan prefetch comment

Cara pakai:
  python lumra_blueprint_fixer.py                        # fix semua dari audit.json
  python lumra_blueprint_fixer.py --audit path/audit.json
  python lumra_blueprint_fixer.py --only D1,D3,D6        # kategori tertentu
  python lumra_blueprint_fixer.py --dry-run              # preview tanpa write
  python lumra_blueprint_fixer.py --no-backup            # tanpa backup (tidak disarankan)

Opsi:
  --audit     PATH   Path ke audit.json (default: audit.json)
  --html-root PATH   Root template HTML (default: lumra_config/templates)
  --py-root   PATH   Root Python source (default: lumra_config)
  --only      LIST   Kategori yang mau di-fix, comma-separated: D1,D3,C4
  --dry-run          Tampilkan apa yang akan diubah tanpa write
  --no-backup        Skip backup (tidak disarankan)
  --verbose          Tampilkan setiap perubahan
"""

import re
import json
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_AUDIT_PATH = Path("audit.json")
DEFAULT_HTML_ROOT  = Path("lumra_config/templates")
DEFAULT_PY_ROOT    = Path("lumra_config")
BACKUP_DIR         = Path(".lumra_fixer_backup")

ALL_CATEGORIES = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "C2", "C3", "C4", "C5"}

# ── D1: rgba → token mapping ──────────────────────────────────────
# Format: (regex_pattern, replacement_token)
RGBA_TOKEN_MAP = [
    # Putih opacity tinggi (glass surface)
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.9[0-9]\s*\)", "var(--color-surface-high)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.8[0-9]\s*\)", "var(--color-surface-high)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.7[0-9]\s*\)", "var(--color-surface-mid)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[4-6][0-9]?\s*\)", "var(--color-surface-mid)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.[1-3][0-9]?\s*\)", "var(--color-surface-glass)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.0[5-9]\s*\)", "var(--color-surface-faint)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*0\.0[1-4]\s*\)", "var(--color-surface-faint)"),
    # Hitam overlay
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[3-9][0-9]?\s*\)", "var(--color-overlay-heavy)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.[1-2][0-9]?\s*\)", "var(--color-overlay-md)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[7-9]\s*\)", "var(--color-overlay-sm)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[4-6]\s*\)", "var(--color-overlay-sm)"),
    (r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\.0[1-3]\s*\)", "var(--color-overlay-xs)"),
    # Odyssey primary alpha
    (r"rgba\(\s*0\s*,\s*103\s*,\s*79\s*,\s*0\.([0-9]+)\s*\)", "var(--color-primary-a\\1)"),
    (r"rgba\(\s*0\s*,\s*168\s*,\s*107\s*,\s*0\.([0-9]+)\s*\)", "var(--color-secondary-a\\1)"),
]

# Hex color → token mapping
HEX_TOKEN_MAP = [
    (r"#1a73e8", "var(--color-info)"),
    (r"#1A73E8", "var(--color-info)"),
    (r"#4285f4", "var(--color-info)"),
    (r"#4285F4", "var(--color-info)"),
    (r"#dc3545", "var(--color-danger)"),
    (r"#DC3545", "var(--color-danger)"),
    (r"#28a745", "var(--color-success)"),
    (r"#28A745", "var(--color-success)"),
    (r"#ffc107", "var(--color-warning)"),
    (r"#FFC107", "var(--color-warning)"),
    (r"#6c757d", "var(--color-text-muted)"),
    (r"#6C757D", "var(--color-text-muted)"),
    (r"#343a40", "var(--color-text-primary)"),
    (r"#343A40", "var(--color-text-primary)"),
    (r"#212529", "var(--color-text-primary)"),
    (r"#f8f9fa", "var(--color-surface-faint)"),
    (r"#F8F9FA", "var(--color-surface-faint)"),
    (r"#e9ecef", "var(--color-border)"),
    (r"#E9ECEF", "var(--color-border)"),
    (r"#dee2e6", "var(--color-border)"),
    (r"#DEE2E6", "var(--color-border)"),
    (r"#2d3748", "var(--color-text-primary)"),
    (r"#2D3748", "var(--color-text-primary)"),
    (r"#718096", "var(--color-text-secondary)"),
    (r"#4a5568", "var(--color-text-secondary)"),
    (r"#4A5568", "var(--color-text-secondary)"),
    (r"#e2e8f0", "var(--color-border)"),
    (r"#E2E8F0", "var(--color-border)"),
    (r"#f7fafc", "var(--color-surface-faint)"),
    (r"#F7FAFC", "var(--color-surface-faint)"),
]

# ── D3: nilai px yang perlu di-snap ──────────────────────────────
SNAP_MAP = {
    1: 0, 2: 0, 3: 4,
    5: 4, 6: 8, 7: 8,
    9: 8, 10: 8, 11: 12,
    13: 12, 14: 16, 15: 16,
    17: 16, 18: 20, 19: 20,
    21: 20, 22: 24, 23: 24,
    25: 24, 26: 28, 27: 28,
    29: 28, 30: 32, 31: 32,
    33: 32, 34: 36, 35: 36,
    37: 36, 38: 40, 39: 40,
    41: 40, 42: 44, 43: 44,
    45: 44, 46: 48, 47: 48,
    49: 48, 50: 48, 51: 52,
}

def snap_to_grid(val: float) -> int:
    iv = int(val)
    if iv in SNAP_MAP:
        return SNAP_MAP[iv]
    if iv % 4 == 0:
        return iv
    return round(iv / 4) * 4

# ── D4: typography snap ───────────────────────────────────────────
VALID_FONT_SIZES   = {10, 11, 13, 14, 16, 18, 20, 22, 24, 28, 32, 36}
VALID_FONT_WEIGHTS = {400, 500, 600, 700}

def snap_font_size(val: float) -> int:
    sizes = sorted(VALID_FONT_SIZES)
    return min(sizes, key=lambda s: abs(s - val))

def snap_font_weight(val: int) -> int:
    weights = sorted(VALID_FONT_WEIGHTS)
    return min(weights, key=lambda w: abs(w - val))

# ── C4: nama terlarang → pengganti ──────────────────────────────
RENAME_VAR_MAP = {
    "data":    "records",
    "info":    "detail_info",
    "tmp":     "temp_value",
    "temp":    "temp_value",
    "val":     "field_value",
    "res":     "response_data",
    "result":  "query_result",
    "obj":     "model_instance",
    "item":    "record_item",
    "stuff":   "payload",
    "flag":    "is_valid",
    "check":   "is_checked",
    "value":   "field_value",
    "x":       "x_coord",
    "y":       "y_coord",
    "z":       "z_value",
    "i":       "idx",
    "j":       "inner_idx",
}

RENAME_FUNC_MAP = {
    "process":    "process_data",
    "handle":     "handle_request",
    "do_stuff":   "execute_task",
    "check":      "validate_input",
    "result":     "get_result",
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
# BACKUP
# ══════════════════════════════════════════════════════════════════

def backup_file(path: Path, backup_root: Path) -> None:
    rel      = path.relative_to(path.anchor) if path.is_absolute() else path
    dest     = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(path, dest)


# ══════════════════════════════════════════════════════════════════
# FIXER CLASSES
# ══════════════════════════════════════════════════════════════════

class FileFixer:
    def __init__(self, path: Path, dry_run: bool, verbose: bool, backup_root: Path | None):
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
                backup_file(self.path, self.backup_root)
            self.path.write_text(self.content, encoding="utf-8")
        return len(self.changes)

    def replace(self, pattern: str, replacement: str, flags=re.IGNORECASE, label="") -> int:
        new = re.sub(pattern, replacement, self.content, flags=flags)
        count = len(re.findall(pattern, self.content, flags=flags))
        if new != self.content:
            self.content = new
            self.changes.append((label or pattern, count))
            if self.verbose:
                print(f"      → {dim(label or pattern[:60])} ({count}x)")
        return count

    def replace_line(self, lineno: int, new_line: str) -> bool:
        lines = self.content.splitlines(keepends=True)
        if 0 < lineno <= len(lines):
            old = lines[lineno - 1]
            if old.rstrip("\n") != new_line.rstrip("\n"):
                lines[lineno - 1] = new_line
                self.content = "".join(lines)
                self.changes.append((f"line {lineno}", 1))
                return True
        return False

    def get_line(self, lineno: int) -> str:
        lines = self.content.splitlines(keepends=True)
        if 0 < lineno <= len(lines):
            return lines[lineno - 1]
        return ""


# ══════════════════════════════════════════════════════════════════
# [D1] Palette Odyssey — rgba/hex → token
# ══════════════════════════════════════════════════════════════════

def fix_d1(fixer: FileFixer, violations: list) -> int:
    total = 0
    for pattern, token in RGBA_TOKEN_MAP:
        total += fixer.replace(pattern, token, label=f"D1 rgba→{token}")
    for pattern, token in HEX_TOKEN_MAP:
        total += fixer.replace(pattern, token, flags=re.IGNORECASE, label=f"D1 hex→{token}")
    return total


# ══════════════════════════════════════════════════════════════════
# [D2] Glass Protocol — kpi-glass + backdrop-filter fix
# ══════════════════════════════════════════════════════════════════

def fix_d2(fixer: FileFixer, violations: list) -> int:
    total = 0

    # 1. Tambah kpi-glass ke card yang kurang
    for v in violations:
        if "tidak menggunakan class .kpi-glass" in v["message"]:
            lineno = v["line"]
            line   = fixer.get_line(lineno)
            if "kpi-glass" not in line:
                # Tambahkan kpi-glass ke class yang ada
                new_line = re.sub(
                    r'class="([^"]*(?:kpi|stat-card)[^"]*)"',
                    lambda m: f'class="{m.group(1)} kpi-glass"',
                    line,
                    flags=re.IGNORECASE,
                )
                if new_line != line:
                    fixer.replace_line(lineno, new_line)
                    total += 1

    # 2. Fix backdrop-filter blur < 12px
    total += fixer.replace(
        r"backdrop-filter\s*:\s*blur\(([1-9]|1[01])px\)",
        "backdrop-filter: blur(12px)",
        label="D2 blur<12→blur(12px)",
    )

    return total


# ══════════════════════════════════════════════════════════════════
# [D3] Grid 8px — snap spacing ke kelipatan 4
# ══════════════════════════════════════════════════════════════════

SPACING_PROPS = r"(?:padding|margin|gap|top|left|right|bottom|width|height)"

def fix_d3(fixer: FileFixer, violations: list) -> int:
    # Kumpulkan nilai yang perlu di-snap dari violations
    bad_values = set()
    for v in violations:
        m = re.search(r":\s*([\d.]+)px", v["message"])
        if m:
            bad_values.add(float(m.group(1)))

    total = 0
    for val in bad_values:
        snapped = snap_to_grid(val)
        if snapped != int(val):
            # Hanya replace dalam context property spacing
            pattern = rf"({SPACING_PROPS}\s*:\s*(?:[^;]*?\s)?){re.escape(str(int(val) if val == int(val) else val))}px"
            replacement = rf"\g<1>{snapped}px"
            count = fixer.replace(
                pattern, replacement,
                label=f"D3 {val}px→{snapped}px",
            )
            total += count

    return total


# ══════════════════════════════════════════════════════════════════
# [D4] Typography — snap font-size/weight
# ══════════════════════════════════════════════════════════════════

def fix_d4(fixer: FileFixer, violations: list) -> int:
    total = 0
    bad_sizes   = set()
    bad_weights = set()

    for v in violations:
        if "font-size" in v["message"]:
            m = re.search(r"font-size:\s*([\d.]+)px", v["message"])
            if m:
                bad_sizes.add(float(m.group(1)))
        elif "font-weight" in v["message"]:
            m = re.search(r"font-weight:\s*(\d+)", v["message"])
            if m:
                bad_weights.add(int(m.group(1)))

    for val in bad_sizes:
        snapped = snap_font_size(val)
        if snapped != int(val):
            pattern = rf"(font-size\s*:\s*){re.escape(str(int(val) if val == int(val) else val))}px"
            total += fixer.replace(pattern, rf"\g<1>{snapped}px", label=f"D4 font-size {val}→{snapped}px")

    for val in bad_weights:
        snapped = snap_font_weight(val)
        if snapped != val:
            pattern = rf"(font-weight\s*:\s*){val}\b"
            total += fixer.replace(pattern, rf"\g<1>{snapped}", label=f"D4 font-weight {val}→{snapped}")

    return total


# ══════════════════════════════════════════════════════════════════
# [D5] Shimmer — tambah is-loading hint ke template
# ══════════════════════════════════════════════════════════════════

D5_COMMENT = (
    "\n{# BLUEPRINT D5: Tambahkan class is-loading saat data belum tersedia. #}\n"
    "{# Contoh: <div class=\"kpi-glass {% if not kpi_value %}is-loading{% endif %}\"> #}\n"
)

def fix_d5(fixer: FileFixer, violations: list) -> int:
    if not violations:
        return 0
    # Jika belum ada is-loading comment, tambahkan di atas {% block content %}
    if "is-loading" not in fixer.content and "BLUEPRINT D5" not in fixer.content:
        fixer.content = re.sub(
            r"(\{%\s*block\s+content\s*%\})",
            D5_COMMENT + r"\1",
            fixer.content,
        )
        fixer.changes.append(("D5 shimmer comment injected", 1))
        return 1
    return 0


# ══════════════════════════════════════════════════════════════════
# [D6] Tabel Odyssey — inject tbl-odyssey
# ══════════════════════════════════════════════════════════════════

def fix_d6(fixer: FileFixer, violations: list) -> int:
    total = 0

    # <table> tanpa class → tambah class tbl-odyssey
    count = fixer.replace(
        r"<table(?!\s[^>]*class=)([^>]*)>",
        r'<table class="tbl-odyssey"\1>',
        label='D6 <table>→tbl-odyssey',
    )
    total += count

    # <table class="..."> tanpa tbl-odyssey → append
    def append_class(m):
        existing = m.group(2)
        if "tbl-odyssey" not in existing:
            return f'<table{m.group(1)}class="{existing} tbl-odyssey"{m.group(3)}>'
        return m.group(0)

    new = re.sub(
        r'<table(\s[^>]*)class="([^"]*)"([^>]*)>',
        append_class,
        fixer.content,
        flags=re.IGNORECASE,
    )
    if new != fixer.content:
        diff = fixer.content.count('<table') - new.count('tbl-odyssey')
        fixer.content = new
        fixer.changes.append(("D6 append tbl-odyssey", 1))
        total += 1

    return total


# ══════════════════════════════════════════════════════════════════
# [D7] CSS Token — inline style hex → token
# ══════════════════════════════════════════════════════════════════

def fix_d7(fixer: FileFixer, violations: list) -> int:
    total = 0
    for pattern, token in HEX_TOKEN_MAP:
        # Hanya dalam konteks style="..."
        count = fixer.replace(
            rf'(style="[^"]*){pattern}([^"]*")',
            rf'\g<1>{token}\2',
            label=f"D7 inline {pattern}→{token}",
        )
        total += count
    # rgba dalam inline style juga
    for pattern, token in RGBA_TOKEN_MAP:
        count = fixer.replace(
            rf'(style="[^"]*){pattern}([^"]*")',
            rf'\g<1>{token}\2',
            label=f"D7 inline rgba→{token}",
        )
        total += count
    return total


# ══════════════════════════════════════════════════════════════════
# [C2] Anti-Duplicate — tidak bisa auto-fix, hanya laporan
# ══════════════════════════════════════════════════════════════════

def fix_c2(fixer: FileFixer, violations: list) -> int:
    # Inject komentar TODO di baris yang berduplikat
    for v in violations:
        lineno = v["line"]
        line   = fixer.get_line(lineno)
        if "# TODO[C2]" not in line and line.strip():
            # Cari indent
            indent = len(line) - len(line.lstrip())
            todo   = " " * indent + f"# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah\n"
            lines  = fixer.content.splitlines(keepends=True)
            if 0 < lineno <= len(lines):
                lines.insert(lineno - 1, todo)
                fixer.content = "".join(lines)
                fixer.changes.append((f"C2 TODO comment line {lineno}", 1))
    return len(violations)


# ══════════════════════════════════════════════════════════════════
# [C3] Anti-Long Method — inject TODO comment
# ══════════════════════════════════════════════════════════════════

def fix_c3(fixer: FileFixer, violations: list) -> int:
    injected = 0
    for v in violations:
        lineno = v["line"]
        line   = fixer.get_line(lineno)
        if "# TODO[C3]" not in fixer.content[max(0, fixer.content.find(line) - 5):fixer.content.find(line) + 5]:
            indent = len(line) - len(line.lstrip())
            # Ekstrak nama function dari message
            m_name = re.search(r"Function '(\w+)'", v["message"])
            m_len  = re.search(r"(\d+) baris", v["message"])
            fname  = m_name.group(1) if m_name else "fungsi_ini"
            flen   = m_len.group(1) if m_len else "?"
            todo   = (
                " " * indent +
                f"# TODO[C3-LONG]: '{fname}' = {flen} baris (max 30). "
                f"Pecah: {fname}_validate(), {fname}_query(), {fname}_render()\n"
            )
            lines = fixer.content.splitlines(keepends=True)
            if 0 < lineno <= len(lines):
                lines.insert(lineno - 1, todo)
                fixer.content = "".join(lines)
                fixer.changes.append((f"C3 TODO {fname}", 1))
                injected += 1
    return injected


# ══════════════════════════════════════════════════════════════════
# [C4] Naming — rename variable/function terlarang
# ══════════════════════════════════════════════════════════════════

def fix_c4(fixer: FileFixer, violations: list) -> int:
    total = 0
    for v in violations:
        # Cari nama terlarang dari message
        m = re.search(r"terlarang:\s*'(\w+)'", v["message"])
        if not m:
            continue
        bad_name = m.group(1)

        if "variable" in v["message"].lower():
            good_name = RENAME_VAR_MAP.get(bad_name, f"{bad_name}_value")
            # Rename assignment saja (bukan dalam string atau komentar)
            # Hanya rename di scope baris violations tersebut ± 5 baris untuk keamanan
            lineno = v["line"]
            lines  = fixer.content.splitlines(keepends=True)
            start  = max(0, lineno - 3)
            end    = min(len(lines), lineno + 3)
            for i in range(start, end):
                old = lines[i]
                # Hanya jika baris ini adalah assignment dari bad_name
                new = re.sub(rf"\b{bad_name}\b(?=\s*=(?!=))", good_name, old)
                if new != old:
                    lines[i] = new
                    fixer.changes.append((f"C4 var {bad_name}→{good_name} L{i+1}", 1))
                    total += 1
            fixer.content = "".join(lines)

        elif "function" in v["message"].lower():
            good_name = RENAME_FUNC_MAP.get(bad_name, f"{bad_name}_action")
            count = fixer.replace(
                rf"\bdef\s+{bad_name}\b",
                f"def {good_name}",
                label=f"C4 func {bad_name}→{good_name}",
            )
            total += count

    return total


# ══════════════════════════════════════════════════════════════════
# [C5] Architecture — N+1 wrap comment + prefetch hint
# ══════════════════════════════════════════════════════════════════

N1_PREFETCH_COMMENT = (
    "    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.\n"
    "    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)\n"
    "    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.\n"
)

FAT_VIEW_COMMENT = (
    "    # TODO[C5-FAT]: Logika ini seharusnya di service layer, bukan views.py.\n"
    "    # Buat: services/{module}_service.py → class {Name}Service dengan method ini.\n"
)

def fix_c5(fixer: FileFixer, violations: list) -> int:
    injected = 0
    for v in violations:
        lineno = v["line"]
        line   = fixer.get_line(lineno)
        tag    = "TODO[C5-N1]" if "N+1" in v["message"] else "TODO[C5-FAT]"
        if tag not in fixer.content:
            comment = N1_PREFETCH_COMMENT if "N+1" in v["message"] else FAT_VIEW_COMMENT
            lines   = fixer.content.splitlines(keepends=True)
            if 0 < lineno <= len(lines):
                lines.insert(lineno - 1, comment)
                fixer.content = "".join(lines)
                fixer.changes.append((f"C5 comment L{lineno}", 1))
                injected += 1
    return injected


# ══════════════════════════════════════════════════════════════════
# DISPATCHER
# ══════════════════════════════════════════════════════════════════

HTML_FIXERS = {
    "D1": fix_d1,
    "D2": fix_d2,
    "D3": fix_d3,
    "D4": fix_d4,
    "D5": fix_d5,
    "D6": fix_d6,
    "D7": fix_d7,
}

PY_FIXERS = {
    "C2": fix_c2,
    "C3": fix_c3,
    "C4": fix_c4,
    "C5": fix_c5,
}


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Lumra Blueprint Auto-Fixer — perbaiki semua violations dari audit.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--audit",    type=Path, default=DEFAULT_AUDIT_PATH)
    p.add_argument("--html-root",type=Path, default=DEFAULT_HTML_ROOT)
    p.add_argument("--py-root",  type=Path, default=DEFAULT_PY_ROOT)
    p.add_argument("--only",     type=str,  default=None,
                   help="Kategori spesifik, comma-separated: D1,D3,C4")
    p.add_argument("--dry-run",  action="store_true",
                   help="Preview tanpa write ke disk")
    p.add_argument("--no-backup",action="store_true",
                   help="Skip backup (tidak disarankan!)")
    p.add_argument("--verbose",  action="store_true")
    p.add_argument("--no-color", action="store_true")
    return p.parse_args()


def main():
    global USE_COLOR
    args = parse_args()

    if args.no_color:
        USE_COLOR = False

    # Tentukan kategori aktif
    if args.only:
        categories = {c.strip().upper() for c in args.only.split(",")}
    else:
        categories = ALL_CATEGORIES

    # Load audit.json
    if not args.audit.exists():
        print(red(f"✖ File audit tidak ditemukan: {args.audit}"))
        print(dim("  Jalankan lumra_blueprint_auditor.py --report audit.json terlebih dahulu."))
        sys.exit(1)

    audit = json.loads(args.audit.read_text(encoding="utf-8"))

    # Setup backup
    backup_root = None
    if not args.no_backup and not args.dry_run:
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = BACKUP_DIR / ts
        backup_root.mkdir(parents=True, exist_ok=True)

    # Banner
    print(f"\n{hr('═')}")
    print(f"  {bold('Lumra Blueprint Auto-Fixer')}  {dim('v1.0')}")
    if args.dry_run:
        print(f"  {yellow('⚠  DRY-RUN MODE — tidak ada file yang diubah')}")
    if backup_root:
        print(f"  {dim('Backup → ' + str(backup_root))}")
    print(hr('═'))
    print(f"  Kategori aktif : {cyan(', '.join(sorted(categories)))}")
    print()

    # Stats
    stats = defaultdict(lambda: {"files": 0, "fixes": 0})
    total_files  = 0
    total_fixes  = 0
    skipped      = 0

    # ── HTML files ────────────────────────────────────────────────
    html_files_data = audit.get("files", {}).get("html", [])

    # Grup violations per file
    html_by_file: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for fdata in html_files_data:
        for v in fdata["violations"]:
            cat = v["category"]
            if cat in categories and cat in HTML_FIXERS:
                html_by_file[fdata["path"]][cat].append(v)

    if html_by_file:
        print(f"  {bold('HTML Templates')}  ({len(html_by_file)} files dengan violations)")
        print(f"  {dim('─' * 60)}")

    for rel_path, cat_violations in sorted(html_by_file.items()):
        full_path = args.html_root / rel_path
        fixer     = FileFixer(full_path, args.dry_run, args.verbose, backup_root)

        if not fixer.load():
            print(f"  {yellow('⚠')} Skip (tidak ditemukan): {dim(rel_path)}")
            skipped += 1
            continue

        file_fixes = 0
        for cat, violations in sorted(cat_violations.items()):
            fn      = HTML_FIXERS[cat]
            count   = fn(fixer, violations)
            file_fixes += count
            stats[cat]["fixes"] += count

        saved = fixer.save()
        if saved > 0 or (args.dry_run and file_fixes > 0):
            status = yellow("[DRY]") if args.dry_run else green("✔")
            print(f"  {status} {rel_path}  {dim(f'({file_fixes} fixes)')}")
            total_files += 1
            total_fixes += file_fixes
            for cat in sorted(cat_violations.keys()):
                stats[cat]["files"] += 1
        else:
            if args.verbose:
                print(f"  {dim('─')} {dim(rel_path)}  (no change)")

    # ── Python files ──────────────────────────────────────────────
    py_files_data = audit.get("files", {}).get("python", [])

    py_by_file: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for fdata in py_files_data:
        for v in fdata["violations"]:
            cat = v["category"]
            if cat in categories and cat in PY_FIXERS:
                py_by_file[fdata["path"]][cat].append(v)

    if py_by_file:
        print()
        print(f"  {bold('Python Sources')}  ({len(py_by_file)} files dengan violations)")
        print(f"  {dim('─' * 60)}")

    for rel_path, cat_violations in sorted(py_by_file.items()):
        full_path = args.py_root / rel_path
        fixer     = FileFixer(full_path, args.dry_run, args.verbose, backup_root)

        if not fixer.load():
            print(f"  {yellow('⚠')} Skip (tidak ditemukan): {dim(rel_path)}")
            skipped += 1
            continue

        file_fixes = 0
        for cat, violations in sorted(cat_violations.items()):
            fn      = PY_FIXERS[cat]
            count   = fn(fixer, violations)
            file_fixes += count
            stats[cat]["fixes"] += count

        saved = fixer.save()
        if saved > 0 or (args.dry_run and file_fixes > 0):
            status = yellow("[DRY]") if args.dry_run else green("✔")
            print(f"  {status} {rel_path}  {dim(f'({file_fixes} fixes)')}")
            total_files += 1
            total_fixes += file_fixes
            for cat in sorted(cat_violations.keys()):
                stats[cat]["files"] += 1
        else:
            if args.verbose:
                print(f"  {dim('─')} {dim(rel_path)}  (no change)")

    # ── Summary ───────────────────────────────────────────────────
    print()
    print(hr('═'))
    print(f"  {bold('Ringkasan')}")
    print(f"  {dim('─' * 60)}")
    print(f"  Files diproses   : {bold(str(total_files))}")
    print(f"  Files dilewati   : {yellow(str(skipped))} (path tidak ditemukan)")
    print(f"  Total fixes      : {green(bold(str(total_fixes)))}")
    print()

    if stats:
        print(f"  {'Kategori':<8} {'Files':>7} {'Fixes':>8}")
        print(f"  {dim('─' * 25)}")
        for cat in sorted(stats.keys()):
            print(f"  {cyan(cat):<8} {str(stats[cat]['files']):>7} {green(str(stats[cat]['fixes'])):>8}")

    print()

    if args.dry_run:
        print(f"  {yellow('─── DRY-RUN: tidak ada file yang diubah. Hilangkan --dry-run untuk apply. ───')}")
    elif total_fixes > 0:
        print(f"  {green('✔ Selesai!')} Jalankan auditor lagi untuk verifikasi:")
        print(f"  {dim('  python lumra_blueprint_auditor.py --report audit_after.json --html audit_after.html')}")
    else:
        print(f"  {dim('Tidak ada perubahan.')}")

    # Kategori yang tidak bisa auto-fix
    manual_needed = categories & {"C2", "C3"}
    if manual_needed:
        print()
        print(f"  {yellow('⚠  Perlu review manual:')} {', '.join(sorted(manual_needed))}")
        print(f"  {dim('   C2/C3: komentar TODO sudah diinjeksi — review & refactor secara manual.')}")

    print(hr('═'))
    print()


if __name__ == "__main__":
    main()