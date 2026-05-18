#!/usr/bin/env python3
"""
lumra_blueprint_auditor.py
==========================
Lumra ERP — Emerald Odyssey Blueprint Auditor v1.0

Memeriksa kepatuhan seluruh codebase terhadap:
  [D1] Palette Odyssey — warna hardcode yang tidak diizinkan
  [D2] Glass Protocol — KPI card wajib pakai .kpi-glass + backdrop-filter + shadow 4 lapis
  [D3] Grid 8px — spacing/padding/margin yang bukan kelipatan 4px
  [D4] Typography — font-size, font-weight, line-height di luar standar
  [D5] Shimmer Loading — area kosong tanpa shimmer saat loading
  [D6] Tabel Odyssey — tabel tanpa .tbl-odyssey
  [D7] Token CSS — penggunaan hex/rgba hardcode di luar inline style yang sudah dimigrasi
  [C1] Anti-God Class — class Python > 300 baris
  [C2] Anti-Duplicate — pola duplikasi (heuristik)
  [C3] Anti-Long Method — function > 30 baris
  [C4] Naming — variable/function dengan nama terlarang
  [C5] Architecture Prudence — N+1 query smell, fat view, magic number

Cara pakai:
  python lumra_blueprint_auditor.py                        # audit semua
  python lumra_blueprint_auditor.py --only design          # hanya design checks
  python lumra_blueprint_auditor.py --only code            # hanya code quality checks
  python lumra_blueprint_auditor.py --category D1,D2,C3   # kategori spesifik
  python lumra_blueprint_auditor.py --report audit.json   # simpan JSON report
  python lumra_blueprint_auditor.py --html audit.html     # simpan HTML report
  python lumra_blueprint_auditor.py --fix-hints           # tampilkan hint perbaikan
  python lumra_blueprint_auditor.py --strict              # exit code 1 jika ada violations

Opsi:
  --root      PATH   Template root HTML (default: lumra_config/templates)
  --src       PATH   Python source root (default: lumra_config)
  --only      MODE   "design" | "code" | "all" (default: all)
  --category  LIST   Comma-separated: D1,D2,D3,D4,D5,D6,D7,C1,C2,C3,C4,C5
  --report    PATH   Simpan JSON report
  --html      PATH   Simpan HTML report interaktif
  --fix-hints        Tampilkan saran perbaikan per violation
  --strict           Exit code 1 jika ada violations (untuk CI/CD)
  --verbose          Tampilkan detail setiap violation
  --no-color         Matikan ANSI color
"""

import re
import ast
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_TEMPLATE_ROOT = Path("lumra_config/templates")
DEFAULT_SRC_ROOT      = Path("lumra_config")

SKIP_DIRS = {
    ".lumra_dup_backup", ".lumra_fix_all_backup", ".lumra_master_backup",
    ".lumra_recolor_backup", ".lumra_rename_backup", ".lumra_reorg_backup",
    ".lumra_sync_backup", ".lumra_theme_backup", "_archive",
    "_emerald_upgrade_backup", "_theme_backup", "_theme_migrate_backup",
    "_token_migration_backup", "_full_migrator_backup",
    "__pycache__", ".git", "node_modules", "venv", ".venv",
    "migrations",
}

# ── Odyssey Palette — warna resmi ──────────────────────────────────
ODYSSEY_PALETTE = {
    "#00674F", "#00674f",
    "#00A86B", "#00a86b",
    "#EFBF04", "#efbf04",
    "#FDFBD4", "#fdfbd4",
    "#000080",
    # alpha variants diperbolehkan via var() token
}

# Warna hardcode yang TIDAK diizinkan (seharusnya sudah pakai token)
FORBIDDEN_HEX_PATTERN = re.compile(
    r'(?<!["\w-])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F"\w-])'
)

FORBIDDEN_RGBA_PATTERN = re.compile(
    r'rgba?\s*\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+(?:\s*,\s*[\d.]+)?\s*\)',
    re.IGNORECASE
)

# Hex yang diizinkan karena bagian dari Odyssey palette + common utilities
ALLOWED_HEX = {
    "#00674F", "#00674f",
    "#00A86B", "#00a86b",
    "#EFBF04", "#efbf04",
    "#FDFBD4", "#fdfbd4",
    "#000080",
    "#fff", "#FFF", "#ffffff", "#FFFFFF",    # putih
    "#000", "#000000",                        # hitam
    "#A32D2D", "#a32d2d",                    # danger odyssey (gradient awal)
    "#888888", "#888",                        # silver tier
}

# ── Glass Protocol requirements ───────────────────────────────────
GLASS_CLASS_PATTERN     = re.compile(r'kpi-glass')
BACKDROP_FILTER_PATTERN = re.compile(r'backdrop-filter\s*:', re.IGNORECASE)
SHADOW_LAYER_PATTERN    = re.compile(r'box-shadow\s*:', re.IGNORECASE)
SHADOW_COUNT_PATTERN    = re.compile(r'rgba\([^)]+\)', re.IGNORECASE)

# ── Typography standards ──────────────────────────────────────────
VALID_FONT_SIZES   = {28, 22, 16, 14, 13, 11, 36, 32, 24, 20, 18, 10}
VALID_FONT_WEIGHTS = {400, 500, 600, 700}
VALID_LINE_HEIGHTS = {20, 24, 28, 32, 36, 40}

FONT_SIZE_PATTERN   = re.compile(r'font-size\s*:\s*([\d.]+)px')
FONT_WEIGHT_PATTERN = re.compile(r'font-weight\s*:\s*(\d+)')
LINE_HEIGHT_PATTERN = re.compile(r'line-height\s*:\s*([\d.]+)px')

# ── Spacing / Grid 8px ────────────────────────────────────────────
SPACING_PATTERN = re.compile(
    r'(?:padding|margin|gap|width|height)\s*:\s*([\d.]+)px',
    re.IGNORECASE
)

# ── Tabel Odyssey ─────────────────────────────────────────────────
TABLE_PATTERN     = re.compile(r'<table', re.IGNORECASE)
TBL_ODYSSEY_PATTERN = re.compile(r'tbl-odyssey')

# ── CSS Token var() ───────────────────────────────────────────────
VAR_TOKEN_PATTERN = re.compile(r'var\(--[^)]+\)')

# ── Shimmer ───────────────────────────────────────────────────────
IS_LOADING_PATTERN = re.compile(r'is-loading|shimmer|skeleton')

# ── Python Code Quality ───────────────────────────────────────────
BANNED_NAMES = {
    "data", "info", "tmp", "temp", "x", "y", "z", "i", "j",
    "flag", "check", "val", "value", "res", "result", "obj",
    "item", "stuff", "process", "handle", "do_stuff",
}

MAGIC_NUMBER_PATTERN = re.compile(r'\b(?<!\.)(\d{2,}(?:\.\d+)?)\b')
MAGIC_NUMBER_EXEMPT  = {0, 1, 2, 10, 100, 200, 404, 500}

N_PLUS_ONE_PATTERN = re.compile(
    r'for\s+\w+\s+in\s+.*:\s*\n(?:.*\n)*?.*\.objects\.(?:get|filter|all)\(',
    re.MULTILINE
)

FAT_VIEW_INDICATORS = {"send_mail", "generate_pdf", "upload_to", "create_pdf", "send_whatsapp"}

ABSTRACT_WITH_ONE_IMPL_PATTERN = re.compile(
    r'class\s+Abstract\w+|@abstractmethod',
    re.MULTILINE
)


# ══════════════════════════════════════════════════════════════════
# TERMINAL COLORS
# ══════════════════════════════════════════════════════════════════

USE_COLOR = True

def _c(code: str, text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

def cyan(t):    return _c("96", t)
def white(t):   return _c("97", t)
def green(t):   return _c("92", t)
def yellow(t):  return _c("93", t)
def red(t):     return _c("91", t)
def dim(t):     return _c("2",  t)
def bold(t):    return _c("1",  t)
def magenta(t): return _c("95", t)

def hr(char="─", n=72):
    return cyan(char * n)

SEVERITY_COLOR = {
    "critical": red,
    "high":     yellow,
    "medium":   magenta,
    "low":      dim,
}

SEVERITY_ICON = {
    "critical": "✖",
    "high":     "⚠",
    "medium":   "◆",
    "low":      "·",
}


# ══════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ══════════════════════════════════════════════════════════════════

@dataclass
class Violation:
    category:    str          # D1, D2, ..., C5
    severity:    str          # critical | high | medium | low
    file:        str
    line:        int
    message:     str
    snippet:     str = ""
    fix_hint:    str = ""

@dataclass
class FileResult:
    path:       str
    violations: list = field(default_factory=list)

    @property
    def violation_count(self):
        return len(self.violations)

    @property
    def critical_count(self):
        return sum(1 for v in self.violations if v.severity == "critical")

    @property
    def high_count(self):
        return sum(1 for v in self.violations if v.severity == "high")


# ══════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════

def is_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def find_html_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.html") if not is_skip(p))


def find_python_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.py") if not is_skip(p))


def read_file(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def get_line(content: str, pos: int) -> int:
    return content[:pos].count("\n") + 1


def is_inside_style_block(content: str, pos: int) -> bool:
    """Cek apakah posisi berada di dalam <style>...</style>"""
    before = content[:pos]
    style_opens  = before.count("<style")
    style_closes = before.count("</style")
    return style_opens > style_closes


def is_inside_inline_style(content: str, pos: int) -> bool:
    """Cek apakah posisi berada di dalam style='...' attribute"""
    # Sederhana: cek apakah ada style=" sebelum posisi di baris yang sama
    line_start = content.rfind("\n", 0, pos) + 1
    line_before = content[line_start:pos]
    return bool(re.search(r'style\s*=\s*["\']', line_before))


# ══════════════════════════════════════════════════════════════════
# [D1] PALETTE ODYSSEY CHECK
# ══════════════════════════════════════════════════════════════════

def check_d1_palette(content: str, rel_path: str) -> list[Violation]:
    """
    Cari hex/rgba hardcode di file HTML yang bukan bagian dari Odyssey palette
    dan bukan di dalam var() token.
    """
    violations = []
    lines = content.split("\n")

    for lineno, line in enumerate(lines, 1):
        # Skip komentar HTML
        if "<!--" in line and "-->" in line:
            continue
        # Skip jika sudah pakai var()
        if "var(--" in line and not re.search(r'(?<!\w)#[0-9a-fA-F]{3,6}', line):
            continue

        # Cari hex colors
        for m in FORBIDDEN_HEX_PATTERN.finditer(line):
            hex_val = m.group(0)
            if hex_val.lower() in {h.lower() for h in ALLOWED_HEX}:
                continue
            # Izinkan jika diikuti langsung var() (transisi)
            if "var(--" in line[m.start()-10:m.end()+10]:
                continue

            violations.append(Violation(
                category="D1",
                severity="high",
                file=rel_path,
                line=lineno,
                message=f"Warna hardcode {hex_val} — gunakan CSS token Odyssey",
                snippet=line.strip()[:80],
                fix_hint=f"Ganti {hex_val} dengan var(--color-primary) atau token Odyssey yang sesuai. "
                         f"Jalankan lumra_full_migrator.py --apply untuk migrasi otomatis.",
            ))

        # Cari rgba hardcode (bukan dalam var())
        for m in FORBIDDEN_RGBA_PATTERN.finditer(line):
            if "var(--" not in line[max(0, m.start()-5):m.end()+5]:
                violations.append(Violation(
                    category="D1",
                    severity="medium",
                    file=rel_path,
                    line=lineno,
                    message=f"rgba() hardcode — gunakan CSS token alpha variant",
                    snippet=line.strip()[:80],
                    fix_hint="Ganti dengan var(--color-primary-a10) atau token alpha sesuai. "
                             "Lihat BAB 10 CSS Token Reference.",
                ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [D2] GLASS PROTOCOL CHECK
# ══════════════════════════════════════════════════════════════════

def check_d2_glass(content: str, rel_path: str) -> list[Violation]:
    """
    KPI card yang tidak pakai .kpi-glass atau tidak punya backdrop-filter.
    """
    violations = []
    lines = content.split("\n")

    # Cari semua elemen yang terlihat seperti KPI card
    kpi_indicators = re.finditer(
        r'class="[^"]*(?:kpi|card|stat)[^"]*"',
        content, re.IGNORECASE
    )

    for m in kpi_indicators:
        classes = m.group(0)
        lineno  = get_line(content, m.start())

        # Harus punya kpi-glass
        if "kpi-glass" not in classes and ("kpi" in classes.lower() or "stat-card" in classes.lower()):
            violations.append(Violation(
                category="D2",
                severity="high",
                file=rel_path,
                line=lineno,
                message="KPI/stat card tidak menggunakan class .kpi-glass",
                snippet=classes[:80],
                fix_hint="Tambahkan class kpi-glass. Pastikan juga ada backdrop-filter, "
                         "box-shadow 4 lapis, dan border frosted edge. Lihat BAB 02 Glass Protocol.",
            ))

    # Cek backdrop-filter di <style> block — minimal 12px
    style_blocks = re.finditer(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)
    for sb in style_blocks:
        style_content = sb.group(1)
        bf_matches = re.finditer(r'backdrop-filter\s*:\s*blur\((\d+)px\)', style_content, re.IGNORECASE)
        for bf in bf_matches:
            blur_val = int(bf.group(1))
            if blur_val < 12:
                lineno = get_line(content, sb.start() + bf.start())
                violations.append(Violation(
                    category="D2",
                    severity="medium",
                    file=rel_path,
                    line=lineno,
                    message=f"backdrop-filter blur({blur_val}px) terlalu kecil — minimum 12px untuk Glass Protocol",
                    snippet=bf.group(0),
                    fix_hint="Naikkan ke minimal blur(12px). Di bawah 12px tidak ada efek frosted glass yang terlihat. "
                             "Lihat BAB 02 Glass Protocol.",
                ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [D3] GRID 8PX CHECK
# ══════════════════════════════════════════════════════════════════

def check_d3_grid(content: str, rel_path: str) -> list[Violation]:
    """
    Spacing yang bukan kelipatan 4px.
    """
    violations = []
    lines = content.split("\n")

    EXCEPTIONS = {0, 1, 2, 3}  # nilai sangat kecil dibiarkan

    for lineno, line in enumerate(lines, 1):
        for m in SPACING_PATTERN.finditer(line):
            try:
                val = float(m.group(1))
            except ValueError:
                continue

            if val in EXCEPTIONS:
                continue
            if val % 4 != 0:
                prop = m.group(0).split(":")[0].strip()
                violations.append(Violation(
                    category="D3",
                    severity="medium",
                    file=rel_path,
                    line=lineno,
                    message=f"{prop}: {val}px — bukan kelipatan 4px (Grid 8px violation)",
                    snippet=line.strip()[:80],
                    fix_hint=f"Ganti {val}px dengan kelipatan terdekat: "
                             f"{int((val // 4) * 4)}px atau {int((val // 4 + 1) * 4)}px. "
                             "Lihat BAB 05 The Invisible Grid.",
                ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [D4] TYPOGRAPHY CHECK
# ══════════════════════════════════════════════════════════════════

def check_d4_typography(content: str, rel_path: str) -> list[Violation]:
    """
    font-size, font-weight, line-height di luar standar Blueprint.
    """
    violations = []
    lines = content.split("\n")

    for lineno, line in enumerate(lines, 1):
        # font-size
        for m in FONT_SIZE_PATTERN.finditer(line):
            val = float(m.group(1))
            if val not in VALID_FONT_SIZES:
                violations.append(Violation(
                    category="D4",
                    severity="low",
                    file=rel_path,
                    line=lineno,
                    message=f"font-size: {val}px tidak sesuai hierarki tipografi (valid: {sorted(VALID_FONT_SIZES)})",
                    snippet=line.strip()[:80],
                    fix_hint=f"Gunakan font-size sesuai BAB 02: 28/22/16/14/13/11px untuk body. "
                             f"28-36px untuk KPI number.",
                ))

        # font-weight
        for m in FONT_WEIGHT_PATTERN.finditer(line):
            val = int(m.group(1))
            if val not in VALID_FONT_WEIGHTS:
                violations.append(Violation(
                    category="D4",
                    severity="low",
                    file=rel_path,
                    line=lineno,
                    message=f"font-weight: {val} tidak sesuai standar (valid: 400/500/600/700)",
                    snippet=line.strip()[:80],
                    fix_hint="Gunakan font-weight: 400 (body), 500 (label), 600 (heading/KPI).",
                ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [D5] SHIMMER / LOADING STATE CHECK
# ══════════════════════════════════════════════════════════════════

def check_d5_shimmer(content: str, rel_path: str) -> list[Violation]:
    """
    Halaman yang punya data-kpi atau fetch tapi tidak ada shimmer/is-loading.
    """
    violations = []

    has_kpi_attr  = bool(re.search(r'data-kpi', content, re.IGNORECASE))
    has_fetch     = bool(re.search(r'fetch\(|\.ajax|htmx', content, re.IGNORECASE))
    has_shimmer   = bool(IS_LOADING_PATTERN.search(content))
    has_api_view  = bool(re.search(r'/api/', content))

    if (has_kpi_attr or (has_fetch and has_api_view)) and not has_shimmer:
        violations.append(Violation(
            category="D5",
            severity="high",
            file=rel_path,
            line=1,
            message="Halaman fetch data API tanpa shimmer/is-loading state",
            snippet="",
            fix_hint="Tambahkan class is-loading pada KPI card saat data belum tersedia. "
                     "Gunakan pola: {% if not value %}is-loading{% endif %}. "
                     "Lihat BAB 06 Shimmer & Loading States.",
        ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [D6] TABEL ODYSSEY CHECK
# ══════════════════════════════════════════════════════════════════

def check_d6_table(content: str, rel_path: str) -> list[Violation]:
    """
    Tabel tanpa class .tbl-odyssey.
    """
    violations = []

    table_matches = list(TABLE_PATTERN.finditer(content))
    if not table_matches:
        return []

    has_tbl_odyssey = bool(TBL_ODYSSEY_PATTERN.search(content))

    if not has_tbl_odyssey:
        for m in table_matches:
            lineno = get_line(content, m.start())
            # Cek apakah tabel ini punya class
            tag_end = content.find(">", m.end())
            tag_str = content[m.start():tag_end + 1]

            violations.append(Violation(
                category="D6",
                severity="high",
                file=rel_path,
                line=lineno,
                message="Tabel tanpa class .tbl-odyssey — header emerald dan zebra tint wajib",
                snippet=tag_str[:80].strip(),
                fix_hint="Tambahkan class tbl-odyssey pada <table>. "
                         "Header harus background #00674F (atau var(--color-primary)), "
                         "zebra odd: rgba(0,103,79,.035). Lihat BAB 04 Tabel & Data Grid.",
            ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [D7] CSS TOKEN CHECK
# ══════════════════════════════════════════════════════════════════

def check_d7_tokens(content: str, rel_path: str) -> list[Violation]:
    """
    Inline style yang masih pakai hardcode padahal seharusnya token.
    Lebih ringan dari D1 — fokus pada style attribute khusus.
    """
    violations = []

    inline_styles = re.finditer(r'style\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)

    for m in inline_styles:
        style_val = m.group(1)
        lineno    = get_line(content, m.start())

        # Jika masih ada hex di inline style
        hex_matches = FORBIDDEN_HEX_PATTERN.findall(style_val)
        for h in hex_matches:
            if h.lower() not in {x.lower() for x in ALLOWED_HEX}:
                violations.append(Violation(
                    category="D7",
                    severity="medium",
                    file=rel_path,
                    line=lineno,
                    message=f"Inline style masih pakai hex hardcode {h} — belum dimigrasi ke token",
                    snippet=style_val[:80],
                    fix_hint="Jalankan lumra_full_migrator.py --apply untuk migrasi otomatis. "
                             "Atau ganti manual dengan var(--color-...) sesuai BAB 10.",
                ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [C1] ANTI-GOD CLASS CHECK
# ══════════════════════════════════════════════════════════════════

def check_c1_god_class(tree: ast.AST, content: str, rel_path: str) -> list[Violation]:
    """
    Class Python > 300 baris atau dengan nama ambigu.
    """
    violations = []
    lines = content.split("\n")

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Hitung panjang class
        start_line = node.lineno
        end_line   = node.end_lineno if hasattr(node, "end_lineno") else start_line
        class_len  = end_line - start_line + 1

        if class_len > 300:
            violations.append(Violation(
                category="C1",
                severity="critical",
                file=rel_path,
                line=start_line,
                message=f"Class '{node.name}' terlalu panjang: {class_len} baris (max: 300)",
                snippet=f"class {node.name}: ... ({class_len} lines)",
                fix_hint=f"Split class '{node.name}' berdasarkan tanggung jawab. "
                         f"Ekstrak bisnis logic ke services.py, query ke selectors.py. "
                         f"Lihat BAB 14 Rule 01 Anti-God Class.",
            ))

        # Nama class ambigu
        ambiguous_suffixes = {"Manager", "Handler", "Controller", "Helper", "Util", "Utils"}
        for suffix in ambiguous_suffixes:
            if node.name.endswith(suffix) and not node.name.replace(suffix, "").strip():
                violations.append(Violation(
                    category="C1",
                    severity="medium",
                    file=rel_path,
                    line=start_line,
                    message=f"Class '{node.name}' — nama terlalu ambigu (suffix '{suffix}' tanpa spesifikasi)",
                    snippet=f"class {node.name}:",
                    fix_hint=f"Ganti '{node.name}' dengan nama yang spesifik: "
                             f"misal 'OrderPricingService', 'StockTransferService'. "
                             f"Lihat BAB 14 Rule 04 Naming.",
                ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [C2] ANTI-DUPLICATE CHECK (heuristik)
# ══════════════════════════════════════════════════════════════════

def check_c2_duplicate(content: str, rel_path: str) -> list[Violation]:
    """
    Heuristik: cari blok kode identik (minimal 5 baris) yang muncul lebih dari sekali.
    """
    violations = []
    lines = content.split("\n")

    # Normalisasi lines (hapus leading whitespace untuk perbandingan)
    normalized = [l.strip() for l in lines]

    WINDOW = 5
    seen_blocks: dict[tuple, int] = {}

    for i in range(len(normalized) - WINDOW):
        block = tuple(normalized[i:i + WINDOW])
        # Skip block kosong atau trivial
        if sum(len(l) for l in block) < 50:
            continue
        # Skip block yang hanya komentar atau import
        if all(l.startswith("#") or l.startswith("import") or l.startswith("from") or not l for l in block):
            continue

        if block in seen_blocks:
            first_occurrence = seen_blocks[block]
            violations.append(Violation(
                category="C2",
                severity="medium",
                file=rel_path,
                line=i + 1,
                message=f"Blok kode duplikat ({WINDOW} baris) — pertama muncul di baris {first_occurrence}",
                snippet=" | ".join(block[:2])[:80],
                fix_hint="Extract ke function atau service method. "
                         "Setiap pengetahuan harus punya satu representasi resmi (DRY). "
                         "Lihat BAB 14 Rule 02 Anti-Duplicate.",
            ))
        else:
            seen_blocks[block] = i + 1

    return violations


# ══════════════════════════════════════════════════════════════════
# [C3] ANTI-LONG METHOD CHECK
# ══════════════════════════════════════════════════════════════════

def check_c3_long_method(tree: ast.AST, content: str, rel_path: str) -> list[Violation]:
    """
    Function/method > 30 baris.
    """
    violations = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        start = node.lineno
        end   = node.end_lineno if hasattr(node, "end_lineno") else start
        length = end - start + 1

        if length > 30:
            severity = "critical" if length > 60 else "high"
            violations.append(Violation(
                category="C3",
                severity=severity,
                file=rel_path,
                line=start,
                message=f"Function '{node.name}' terlalu panjang: {length} baris (max: 30)",
                snippet=f"def {node.name}(...): ... ({length} lines)",
                fix_hint=f"Pecah '{node.name}' menjadi beberapa function kecil. "
                         f"Setiap seksi yang punya komentar blok → extract jadi function baru. "
                         f"Lihat BAB 14 Rule 03 Anti-Long Method.",
            ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [C4] NAMING AS DOCUMENTATION CHECK
# ══════════════════════════════════════════════════════════════════

def check_c4_naming(tree: ast.AST, content: str, rel_path: str) -> list[Violation]:
    """
    Variable/function dengan nama yang dilarang.
    """
    violations = []

    for node in ast.walk(tree):
        # Variable assignments
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id in BANNED_NAMES:
                        violations.append(Violation(
                            category="C4",
                            severity="medium",
                            file=rel_path,
                            line=node.lineno,
                            message=f"Nama variable terlarang: '{target.id}' — tidak deskriptif",
                            snippet=f"{target.id} = ...",
                            fix_hint=f"Ganti '{target.id}' dengan nama yang menjelaskan isi: "
                                     f"misal 'order_list', 'active_customers', 'total_price'. "
                                     f"Lihat BAB 14 Rule 04 Naming.",
                        ))

        # Function definitions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in BANNED_NAMES:
                violations.append(Violation(
                    category="C4",
                    severity="high",
                    file=rel_path,
                    line=node.lineno,
                    message=f"Nama function terlarang: '{node.name}' — tidak menjelaskan aksi",
                    snippet=f"def {node.name}(...):",
                    fix_hint=f"Ganti '{node.name}' dengan verb yang spesifik: "
                             f"misal 'calculate_order_total', 'send_confirmation', 'get_active_orders'. "
                             f"Lihat BAB 14 Rule 04 Naming.",
                ))

        # Magic numbers
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            val = node.value
            if val not in MAGIC_NUMBER_EXEMPT and isinstance(val, (int, float)) and abs(val) > 1:
                if isinstance(val, float) and 0 < val < 1:
                    # Tax rate atau alpha — cek konteks
                    violations.append(Violation(
                        category="C4",
                        severity="low",
                        file=rel_path,
                        line=node.lineno,
                        message=f"Magic number {val} — beri nama constant",
                        snippet=str(val),
                        fix_hint=f"Extract {val} ke constant: misal TAX_RATE = Decimal('{val}'), "
                                 f"LOW_STOCK_THRESHOLD = {val}. Lihat BAB 14 Rule 04 Magic Number.",
                    ))

    return violations


# ══════════════════════════════════════════════════════════════════
# [C5] ARCHITECTURE PRUDENCE CHECK
# ══════════════════════════════════════════════════════════════════

def check_c5_architecture(content: str, rel_path: str) -> list[Violation]:
    """
    Fat view, N+1 smell, premature abstraction.
    """
    violations = []
    lines = content.split("\n")

    # Fat view detection — views.py yang punya email/PDF/upload
    if "views.py" in rel_path or "view" in rel_path.lower():
        fat_indicators_found = []
        for lineno, line in enumerate(lines, 1):
            for indicator in FAT_VIEW_INDICATORS:
                if indicator in line:
                    fat_indicators_found.append((lineno, indicator, line.strip()))

        if fat_indicators_found:
            for lineno, indicator, snippet in fat_indicators_found:
                violations.append(Violation(
                    category="C5",
                    severity="high",
                    file=rel_path,
                    line=lineno,
                    message=f"Fat View — '{indicator}' seharusnya ada di service layer, bukan views.py",
                    snippet=snippet[:80],
                    fix_hint=f"Pindahkan '{indicator}' ke NotificationService atau DocumentService. "
                             f"View hanya boleh: terima request, delegasi ke service, return response. "
                             f"Lihat BAB 14 Rule 01 Struktur File Django.",
                ))

    # N+1 smell — .objects. di dalam for loop
    in_loop    = False
    loop_start = 0
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r'for\s+\w+\s+in\s+', stripped):
            in_loop    = True
            loop_start = lineno
        elif in_loop and stripped and not stripped.startswith("#"):
            indent = len(line) - len(line.lstrip())
            if indent == 0 and stripped:
                in_loop = False
            elif ".objects." in stripped and any(m in stripped for m in [".get(", ".filter(", ".all("]):
                violations.append(Violation(
                    category="C5",
                    severity="critical",
                    file=rel_path,
                    line=lineno,
                    message=f"N+1 Query smell — .objects. query di dalam loop (mulai baris {loop_start})",
                    snippet=stripped[:80],
                    fix_hint="Gunakan select_related() atau prefetch_related() sebelum loop. "
                             "Atau pindahkan query ke selectors.py dengan prefetch yang tepat. "
                             "Lihat BAB 14 Django-Specific N+1 Problem.",
                ))

    # Premature abstraction — abstract class dengan < 2 concrete implementations
    abstract_matches = list(ABSTRACT_WITH_ONE_IMPL_PATTERN.finditer(content))
    if abstract_matches and "Abstract" in content:
        # Heuristic: count concrete implementations
        concrete_count = len(re.findall(r'class\s+\w+\([^)]*Abstract\w+[^)]*\)', content))
        if concrete_count <= 1:
            lineno = get_line(content, abstract_matches[0].start())
            violations.append(Violation(
                category="C5",
                severity="medium",
                file=rel_path,
                line=lineno,
                message="Premature abstraction — Abstract class dengan ≤ 1 implementasi concrete",
                snippet=abstract_matches[0].group(0),
                fix_hint="Hapus abstraction, pakai concrete class langsung. "
                         "Tambahkan abstraction nanti jika benar-benar butuh 2+ implementasi. "
                         "YAGNI — You Aren't Gonna Need It. Lihat BAB 14 Rule 05.",
            ))

    return violations


# ══════════════════════════════════════════════════════════════════
# MAIN AUDITOR
# ══════════════════════════════════════════════════════════════════

def audit_html_file(
    path: Path,
    root: Path,
    categories: set[str],
) -> FileResult:
    rel_path = str(path.relative_to(root)).replace("\\", "/")
    content  = read_file(path)
    if content is None:
        return FileResult(path=rel_path)

    result = FileResult(path=rel_path)

    if "D1" in categories:
        result.violations.extend(check_d1_palette(content, rel_path))
    if "D2" in categories:
        result.violations.extend(check_d2_glass(content, rel_path))
    if "D3" in categories:
        result.violations.extend(check_d3_grid(content, rel_path))
    if "D4" in categories:
        result.violations.extend(check_d4_typography(content, rel_path))
    if "D5" in categories:
        result.violations.extend(check_d5_shimmer(content, rel_path))
    if "D6" in categories:
        result.violations.extend(check_d6_table(content, rel_path))
    if "D7" in categories:
        result.violations.extend(check_d7_tokens(content, rel_path))

    return result


def audit_python_file(
    path: Path,
    root: Path,
    categories: set[str],
) -> FileResult:
    rel_path = str(path.relative_to(root)).replace("\\", "/")
    content  = read_file(path)
    if content is None:
        return FileResult(path=rel_path)

    result = FileResult(path=rel_path)

    # Parse AST
    tree = None
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        result.violations.append(Violation(
            category="C0",
            severity="critical",
            file=rel_path,
            line=e.lineno or 1,
            message=f"Syntax error — tidak bisa diparse: {e}",
            snippet="",
            fix_hint="Perbaiki syntax error sebelum menjalankan audit.",
        ))
        return result

    if "C1" in categories:
        result.violations.extend(check_c1_god_class(tree, content, rel_path))
    if "C2" in categories:
        result.violations.extend(check_c2_duplicate(content, rel_path))
    if "C3" in categories:
        result.violations.extend(check_c3_long_method(tree, content, rel_path))
    if "C4" in categories:
        result.violations.extend(check_c4_naming(tree, content, rel_path))
    if "C5" in categories:
        result.violations.extend(check_c5_architecture(content, rel_path))

    return result


# ══════════════════════════════════════════════════════════════════
# REPORTING
# ══════════════════════════════════════════════════════════════════

CATEGORY_INFO = {
    "D1": ("Palette Odyssey",       "Warna hardcode di luar token Odyssey"),
    "D2": ("Glass Protocol",        "KPI card/panel tanpa glass protocol lengkap"),
    "D3": ("Grid 8px",              "Spacing/padding bukan kelipatan 4px"),
    "D4": ("Typography",            "Font-size/weight di luar standar Blueprint"),
    "D5": ("Shimmer Loading",       "Fetch data tanpa shimmer/loading state"),
    "D6": ("Tabel Odyssey",         "Tabel tanpa .tbl-odyssey standard"),
    "D7": ("CSS Token",             "Inline style belum dimigrasi ke token"),
    "C1": ("Anti-God Class",        "Class Python > 300 baris"),
    "C2": ("Anti-Duplicate",        "Duplikasi kode (heuristik 5-baris window)"),
    "C3": ("Anti-Long Method",      "Function Python > 30 baris"),
    "C4": ("Naming",                "Nama variable/function terlarang / magic number"),
    "C5": ("Architecture Prudence", "Fat view, N+1 query, premature abstraction"),
}

def build_report(
    html_results:   list[FileResult],
    python_results: list[FileResult],
    categories:     set[str],
    duration_sec:   float,
) -> dict:
    all_results   = html_results + python_results
    all_violations = [v for r in all_results for v in r.violations]

    by_category: dict[str, list] = defaultdict(list)
    by_severity:  dict[str, int]  = defaultdict(int)

    for v in all_violations:
        by_category[v.category].append(asdict(v))
        by_severity[v.severity] += 1

    return {
        "timestamp":     datetime.now().isoformat(),
        "duration_sec":  round(duration_sec, 2),
        "summary": {
            "html_files_scanned":   len(html_results),
            "python_files_scanned": len(python_results),
            "total_violations":     len(all_violations),
            "critical":             by_severity.get("critical", 0),
            "high":                 by_severity.get("high",     0),
            "medium":               by_severity.get("medium",   0),
            "low":                  by_severity.get("low",      0),
            "by_category": {
                cat: len(vs) for cat, vs in sorted(by_category.items())
            },
        },
        "files": {
            "html":   [{"path": r.path, "violations": [asdict(v) for v in r.violations]} for r in html_results   if r.violations],
            "python": [{"path": r.path, "violations": [asdict(v) for v in r.violations]} for r in python_results if r.violations],
        },
        "by_category": dict(by_category),
    }


def print_console_report(
    report:     dict,
    verbose:    bool,
    fix_hints:  bool,
) -> None:
    s    = report["summary"]
    ts   = report["timestamp"]

    print(f"\n{hr('═')}")
    print(f"  {bold('Lumra Blueprint Auditor')}  {dim('v1.0')}  ·  {dim(ts[:19].replace('T',' '))}")
    print(hr('═'))

    # Summary box
    total = s["total_violations"]
    crit  = s["critical"]
    high  = s["high"]
    med   = s["medium"]
    low_  = s["low"]

    print(f"  {bold('Files scanned')}  :  "
          f"HTML {white(str(s['html_files_scanned']))}  ·  "
          f"Python {white(str(s['python_files_scanned']))}")
    print()

    status_str = (
        red("✖ GAGAL")   if crit > 0 else
        yellow("⚠ PERLU PERHATIAN") if high > 0 else
        green("✔ BERSIH")
    )
    print(f"  {bold('Status')}         :  {status_str}")
    print()
    print(f"  {bold('Violations')}     :  "
          f"{red(str(crit))} critical  "
          f"{yellow(str(high))} high  "
          f"{magenta(str(med))} medium  "
          f"{dim(str(low_))} low  "
          f"= {bold(str(total))} total")
    print()

    # Per category
    print(f"  {bold('Per Kategori')}")
    print(f"  {dim('─' * 60)}")
    for cat, count in sorted(s["by_category"].items()):
        if count == 0:
            continue
        name, desc = CATEGORY_INFO.get(cat, (cat, ""))
        bar_len     = min(count, 40)
        bar         = "█" * bar_len
        color_fn    = red if count > 20 else yellow if count > 5 else magenta
        print(f"  [{cyan(cat)}] {name:<28} {color_fn(bar)} {white(str(count))}")

    print(hr())

    if total == 0:
        print(f"\n  {green('✔ Tidak ada violations! Lumra Blueprint compliant.')}\n")
        print(hr('═') + "\n")
        return

    # Detail per file
    if verbose:
        print(f"\n  {bold('Detail Violations')}")
        print()

        all_files = report["files"]["html"] + report["files"]["python"]
        all_files.sort(key=lambda f: -len(f["violations"]))

        for file_data in all_files:
            if not file_data["violations"]:
                continue

            vcount = len(file_data["violations"])
            print(f"  {bold(cyan(file_data['path']))}  {dim(f'({vcount} violations)')}")

            for v in file_data["violations"]:
                sev      = v["severity"]
                color_fn = SEVERITY_COLOR.get(sev, dim)
                icon     = SEVERITY_ICON.get(sev, "·")
                cat      = v["category"]

                line_num = v["line"]
                print(f"    {color_fn(icon)} {dim(f'L{line_num:>4}')}  [{cyan(cat)}]  {v['message']}")
                if v["snippet"]:
                    print(f"           {dim(v['snippet'])}")
                if fix_hints and v["fix_hint"]:
                    print(f"           {green('→')} {dim(v['fix_hint'][:100])}")

            print()
    else:
        # Summary per file — top 10 paling banyak violations
        all_files = report["files"]["html"] + report["files"]["python"]
        all_files.sort(key=lambda f: -len(f["violations"]))
        top = all_files[:15]

        print(f"\n  {bold('Top Files dengan Violations')}")
        header_row = f"  {'File':<50} {'Crit':>6} {'High':>6} {'Med':>6} {'Total':>7}"
        print(f"  {dim(header_row)}")
        print(f"  {dim('─' * 75)}")

        for file_data in top:
            vs    = file_data["violations"]
            crit  = sum(1 for v in vs if v["severity"] == "critical")
            high_ = sum(1 for v in vs if v["severity"] == "high")
            med_  = sum(1 for v in vs if v["severity"] == "medium")
            total_ = len(vs)

            c_str = red(str(crit))    if crit  else dim("—")
            h_str = yellow(str(high_)) if high_ else dim("—")
            m_str = magenta(str(med_)) if med_  else dim("—")

            print(f"  {dim(file_data['path'][:50]):<50} {c_str:>6} {h_str:>6} {m_str:>6} {bold(str(total_)):>7}")

        print(f"\n  {dim('Jalankan dengan --verbose untuk detail setiap violation.')}")
        print(f"  {dim('Jalankan dengan --fix-hints untuk saran perbaikan.')}")

    print()
    print(hr('═'))
    print()


def generate_html_report(report: dict) -> str:
    """Generate HTML report yang bisa dibuka di browser."""
    s       = report["summary"]
    ts      = report["timestamp"][:19].replace("T", " ")
    total   = s["total_violations"]
    crit    = s["critical"]
    high_   = s["high"]
    med_    = s["medium"]
    low__   = s["low"]

    all_files = report["files"]["html"] + report["files"]["python"]
    all_files.sort(key=lambda f: -len(f["violations"]))

    # Build violation rows
    rows_html = ""
    for file_data in all_files:
        for v in file_data["violations"]:
            sev   = v["severity"]
            sev_color = {
                "critical": "#ef4444",
                "high":     "#f59e0b",
                "medium":   "#a78bfa",
                "low":      "#94a3b8",
            }.get(sev, "#94a3b8")

            rows_html += f"""
            <tr>
                <td><span class="badge" style="background:{sev_color}20;color:{sev_color};border:1px solid {sev_color}40">{sev}</span></td>
                <td><span class="cat-badge">{v["category"]}</span></td>
                <td class="file-path">{v["file"]}</td>
                <td class="line-num">L{v["line"]}</td>
                <td>{v["message"]}</td>
                <td class="fix-hint">{v["fix_hint"][:120] if v["fix_hint"] else "—"}</td>
            </tr>"""

    # Category summary
    cat_rows = ""
    for cat, count in sorted(s["by_category"].items()):
        name, desc = CATEGORY_INFO.get(cat, (cat, ""))
        pct        = int(count / max(total, 1) * 100)
        cat_rows  += f"""
        <tr>
            <td><span class="cat-badge">{cat}</span></td>
            <td><strong>{name}</strong></td>
            <td>{desc}</td>
            <td>
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="flex:1;background:#1e293b;height:6px;border-radius:3px">
                        <div style="width:{pct}%;background:var(--primary);height:6px;border-radius:3px"></div>
                    </div>
                    <span style="color:#00A86B;font-weight:600;min-width:30px">{count}</span>
                </div>
            </td>
        </tr>"""

    status_color = "#ef4444" if crit > 0 else "#f59e0b" if high_ > 0 else "#00A86B"
    status_text  = "GAGAL" if crit > 0 else "PERLU PERHATIAN" if high_ > 0 else "BERSIH"

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lumra Blueprint Audit — {ts}</title>
<style>
  :root {{
    --primary: #00674F;
    --secondary: #00A86B;
    --accent: #EFBF04;
    --navy: #000080;
    --bg: #0b1120;
    --surface: rgba(0,103,79,.08);
    --border: rgba(255,255,255,.08);
    --text: #e2e8f0;
    --text-muted: #94a3b8;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    line-height: 1.6;
  }}
  .header {{
    background: linear-gradient(135deg, rgba(0,103,79,.15) 0%, rgba(0,0,128,.08) 100%);
    border-bottom: 1px solid var(--border);
    padding: 32px 40px;
    position: sticky; top: 0; z-index: 10;
    backdrop-filter: blur(20px);
  }}
  .header-top {{ display:flex; justify-content:space-between; align-items:center; }}
  .logo {{ font-size: 22px; font-weight: 700; color: var(--secondary); letter-spacing: -0.5px; }}
  .logo span {{ color: var(--accent); }}
  .timestamp {{ color: var(--text-muted); font-size: 12px; }}
  .status-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    background: {status_color}20; color: {status_color};
    border: 1px solid {status_color}40;
    padding: 6px 16px; border-radius: 100px;
    font-weight: 600; font-size: 13px; margin-top: 12px;
  }}
  .main {{ max-width: 1400px; margin: 0 auto; padding: 32px 40px; }}
  .grid-4 {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px;
  }}
  .stat-card {{
    background: var(--surface);
    border: 0.5px solid var(--border);
    border-top-color: rgba(255,255,255,.15);
    backdrop-filter: blur(12px);
    border-radius: 14px; padding: 20px;
    text-align: center;
  }}
  .stat-card .num {{ font-size: 36px; font-weight: 700; font-variant-numeric: tabular-nums; }}
  .stat-card .label {{ color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; margin-top: 4px; }}
  .section-title {{
    font-size: 16px; font-weight: 600; color: var(--secondary);
    margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
  }}
  .section-title::before {{ content:""; width:3px; height:16px; background:var(--secondary); border-radius:2px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{
    background: var(--primary); color: white;
    font-size: 10px; letter-spacing: .08em; text-transform: uppercase;
    padding: 10px 12px; text-align: left;
    position: sticky; top: 0;
  }}
  td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  tr:nth-child(odd) td {{ background: rgba(0,103,79,.035); }}
  tr:hover td {{ background: rgba(0,103,79,.07); transition: 150ms; }}
  .badge {{
    display: inline-block; padding: 2px 8px; border-radius: 100px;
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .04em;
  }}
  .cat-badge {{
    display: inline-block; padding: 2px 8px; border-radius: 6px;
    background: rgba(0,168,107,.15); color: var(--secondary);
    font-size: 11px; font-weight: 700; font-family: monospace;
  }}
  .file-path {{ font-family: monospace; font-size: 12px; color: var(--text-muted); }}
  .line-num {{ font-family: monospace; font-size: 12px; color: var(--accent); }}
  .fix-hint {{ font-size: 12px; color: var(--text-muted); }}
  .card {{ background: var(--surface); border: 0.5px solid var(--border); border-radius: 14px; padding: 24px; margin-bottom: 24px; }}
  .search-bar {{
    width: 100%; background: rgba(255,255,255,.05); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 16px; color: var(--text);
    font-size: 14px; margin-bottom: 16px; outline: none;
  }}
  .search-bar:focus {{ border-color: var(--secondary); box-shadow: 0 0 0 3px rgba(0,168,107,.2); }}
  .filter-bar {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }}
  .filter-btn {{
    padding: 4px 12px; border-radius: 100px; border: 1px solid var(--border);
    background: transparent; color: var(--text-muted); cursor: pointer; font-size: 12px;
    transition: 150ms;
  }}
  .filter-btn:hover, .filter-btn.active {{
    background: rgba(0,103,79,.15); color: var(--secondary);
    border-color: rgba(0,168,107,.3);
  }}
</style>
</head>
<body>
<div class="header">
  <div class="header-top">
    <div class="logo">Lumra <span>Odyssey</span> Blueprint Auditor</div>
    <div class="timestamp">{ts}</div>
  </div>
  <div class="status-badge">● {status_text} — {total} violations</div>
</div>

<div class="main">
  <div class="grid-4">
    <div class="stat-card">
      <div class="num" style="color:#ef4444">{crit}</div>
      <div class="label">Critical</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:#f59e0b">{high_}</div>
      <div class="label">High</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:#a78bfa">{med_}</div>
      <div class="label">Medium</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:#94a3b8">{low__}</div>
      <div class="label">Low</div>
    </div>
  </div>

  <div class="card">
    <div class="section-title">Ringkasan per Kategori</div>
    <table>
      <thead><tr><th>Kode</th><th>Kategori</th><th>Deskripsi</th><th>Jumlah</th></tr></thead>
      <tbody>{cat_rows}</tbody>
    </table>
  </div>

  <div class="card">
    <div class="section-title">Semua Violations</div>
    <input type="text" class="search-bar" id="searchInput" placeholder="Cari file, pesan, kategori...">
    <div class="filter-bar" id="filterBar">
      <button class="filter-btn active" onclick="filterSev('all')">Semua</button>
      <button class="filter-btn" onclick="filterSev('critical')" style="color:#ef4444">Critical</button>
      <button class="filter-btn" onclick="filterSev('high')" style="color:#f59e0b">High</button>
      <button class="filter-btn" onclick="filterSev('medium')" style="color:#a78bfa">Medium</button>
      <button class="filter-btn" onclick="filterSev('low')">Low</button>
    </div>
    <table id="mainTable">
      <thead><tr>
        <th>Severity</th><th>Kategori</th><th>File</th><th>Baris</th>
        <th>Pesan</th><th>Saran Perbaikan</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</div>

<script>
let currentSev = 'all';
const input = document.getElementById('searchInput');
const rows  = document.querySelectorAll('#mainTable tbody tr');

function filterRows() {{
  const q = input.value.toLowerCase();
  rows.forEach(row => {{
    const text = row.textContent.toLowerCase();
    const sev  = row.querySelector('.badge')?.textContent?.toLowerCase() || '';
    const sevOk = currentSev === 'all' || sev === currentSev;
    row.style.display = (text.includes(q) && sevOk) ? '' : 'none';
  }});
}}

function filterSev(sev) {{
  currentSev = sev;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  filterRows();
}}

input.addEventListener('input', filterRows);
</script>
</body>
</html>"""

    return html


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

ALL_CATEGORIES = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "C1", "C2", "C3", "C4", "C5"}
DESIGN_CATS    = {"D1", "D2", "D3", "D4", "D5", "D6", "D7"}
CODE_CATS      = {"C1", "C2", "C3", "C4", "C5"}


def parse_args():
    p = argparse.ArgumentParser(
        description="Lumra Blueprint Auditor — cek kepatuhan terhadap Emerald Odyssey Blueprint v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--root",       type=Path, default=DEFAULT_TEMPLATE_ROOT,
                   help=f"Template root HTML (default: {DEFAULT_TEMPLATE_ROOT})")
    p.add_argument("--src",        type=Path, default=DEFAULT_SRC_ROOT,
                   help=f"Python source root (default: {DEFAULT_SRC_ROOT})")
    p.add_argument("--only",       choices=["design", "code", "all"], default="all",
                   help="Audit hanya design (D*), code (C*), atau all (default: all)")
    p.add_argument("--category",   type=str, default=None,
                   help="Kategori spesifik, comma-separated: D1,D2,C3")
    p.add_argument("--report",     type=Path, default=None,
                   help="Simpan JSON report ke path ini")
    p.add_argument("--html",       type=Path, default=None,
                   help="Simpan HTML report interaktif ke path ini")
    p.add_argument("--fix-hints",  action="store_true",
                   help="Tampilkan saran perbaikan per violation")
    p.add_argument("--strict",     action="store_true",
                   help="Exit code 1 jika ada critical violations (untuk CI/CD)")
    p.add_argument("--verbose",    action="store_true",
                   help="Tampilkan detail setiap violation di console")
    p.add_argument("--no-color",   action="store_true",
                   help="Matikan ANSI color output")
    return p.parse_args()


def main():
    global USE_COLOR
    args = parse_args()

    if args.no_color:
        USE_COLOR = False

    # Tentukan kategori yang aktif
    if args.category:
        categories = {c.strip().upper() for c in args.category.split(",")}
    elif args.only == "design":
        categories = DESIGN_CATS
    elif args.only == "code":
        categories = CODE_CATS
    else:
        categories = ALL_CATEGORIES

    print(f"\n{hr('═')}")
    print(f"  {bold('Lumra Blueprint Auditor')}  {dim('v1.0')}")
    print(hr('═'))
    print(f"  Template root  : {dim(str(args.root))}")
    print(f"  Python src     : {dim(str(args.src))}")
    print(f"  Kategori aktif : {cyan(', '.join(sorted(categories)))}")
    print()

    import time
    t0 = time.time()

    # Audit HTML templates
    html_files   = find_html_files(args.root)
    python_files = find_python_files(args.src)

    print(f"  {dim('Scanning')} {white(str(len(html_files)))} HTML files...", end="", flush=True)
    html_results = []
    for path in html_files:
        result = audit_html_file(path, args.root, categories)
        html_results.append(result)
    print(f" {green('✓')}")

    print(f"  {dim('Scanning')} {white(str(len(python_files)))} Python files...", end="", flush=True)
    python_results = []
    for path in python_files:
        result = audit_python_file(path, args.src, categories)
        python_results.append(result)
    print(f" {green('✓')}")

    duration = time.time() - t0
    print(f"  {dim(f'Selesai dalam {duration:.2f} detik')}\n")

    # Build report
    report = build_report(html_results, python_results, categories, duration)

    # Print console report
    print_console_report(report, verbose=args.verbose, fix_hints=args.fix_hints)

    # Save JSON report
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"  {green('📄')} JSON report: {white(str(args.report))}")

    # Save HTML report
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        html_content = generate_html_report(report)
        args.html.write_text(html_content, encoding="utf-8")
        print(f"  {green('🌐')} HTML report: {white(str(args.html))}")

    if args.report or args.html:
        print()

    # Strict mode — exit 1 jika ada critical
    if args.strict and report["summary"]["critical"] > 0:
        print(f"  {red('✖ STRICT MODE: Ada ' + str(report['summary']['critical']) + ' critical violations.')}")
        print(f"  {red('  Exit code 1 — pipeline dihentikan.')}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()