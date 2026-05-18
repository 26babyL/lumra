#!/usr/bin/env python3
"""
lumra_token_migrator.py  v2
===========================
Script migrasi CSS — scope: <style> block di template.

PERUBAHAN dari v1:
  - Step 4 (overwrite :root di lumra_design_system.css) DIHAPUS.
    Design system v2 sudah final, jangan ditimpa.
  - _KNOWN_COLORS diupdate ke v2 token map (#00674F, semantic tokens, dll).
  - Hanya lakukan Step 5: replace nilai hardcode di <style> block template.

Scope: warna (hex + rgba) dan backdrop-filter di dalam <style>...</style>.
Untuk inline style=\"\" → pakai lumra_full_migrator.py

Cara pakai:
  python lumra_token_migrator.py --dry-run     # preview, tidak ubah file
  python lumra_token_migrator.py --apply       # apply ke template

Opsi:
  --root     PATH   Template root (default: lumra_config/templates)
  --backup   PATH   Direktori backup (default: ./_token_migration_backup)
  --threshold N     Token dimigrasikan jika muncul >= N kali (default: 1)
  --report   PATH   Simpan JSON report
"""

import re
import json
import shutil
import argparse
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_ROOT   = Path(r"lumra_config/templates")
DEFAULT_BACKUP = Path(r"_token_migration_backup")

SKIP_DIRS = {
    ".lumra_dup_backup", ".lumra_fix_all_backup", ".lumra_master_backup",
    ".lumra_recolor_backup", ".lumra_rename_backup", ".lumra_reorg_backup",
    ".lumra_sync_backup", ".lumra_theme_backup", "_archive",
    "_emerald_upgrade_backup", "_theme_backup", "_theme_migrate_backup",
    "_token_migration_backup", "_full_migrator_backup",
}


# ══════════════════════════════════════════════════════════════════
# TERMINAL
# ══════════════════════════════════════════════════════════════════

C   = "\033[96m"
W   = "\033[97m"
G   = "\033[92m"
Y   = "\033[93m"
R   = "\033[91m"
DIM = "\033[2m"
B   = "\033[1m"
RST = "\033[0m"

def hr(char="─", n=68): return C + char * n + RST


# ══════════════════════════════════════════════════════════════════
# V2 TOKEN MAP — single source of truth
# Sinkron dengan lumra_design_system.css v2
# Urutan: paling spesifik/panjang dulu
# ══════════════════════════════════════════════════════════════════

# [A] HEX → token name
HEX_TOKEN_MAP: dict[str, str] = {
    # ── Emerald v2 (jewel-tone) ──────────────────────────────────
    "#00674f": "--color-primary",
    "#2e8c69": "--color-primary-light",
    "#e6f2ee": "--color-primary-subtle",
    "#003d2c": "--color-primary-dark",
    "#5da88a": "--color-primary-glow",
    "#90c4ac": "--color-emerald-200",
    "#c0dfcf": "--color-emerald-100",

    # ── Emerald Tailwind lama → mapped ke v2 token ───────────────
    "#10b981": "--color-emerald-500",
    "#059669": "--color-emerald-600",
    "#047857": "--color-primary",        # lama: emerald-700 → v2: primary
    "#065f46": "--color-emerald-800",
    "#064e3b": "--color-emerald-900",
    "#022c22": "--color-emerald-950",
    "#6ee7b7": "--color-emerald-300",
    "#34d399": "--color-emerald-400",
    "#a7f3d0": "--color-emerald-200",
    "#d1fae5": "--color-emerald-100",
    "#ecfdf5": "--color-emerald-50",

    # ── Slate / Neutral ──────────────────────────────────────────
    "#0f172a": "--color-text",           # lama: slate-900 → v2: color-text
    "#1e293b": "--color-slate-800",
    "#334155": "--color-slate-700",
    "#475569": "--color-text-muted",     # lama: slate-600 → v2: text-muted
    "#64748b": "--color-slate-500",
    "#94a3b8": "--color-text-subtle",    # lama: slate-400 → v2: text-subtle
    "#cbd5e1": "--color-slate-300",
    "#e2e8f0": "--color-slate-200",
    "#f1f5f9": "--color-slate-100",
    "#f8fafc": "--color-slate-50",

    # ── White / Black ─────────────────────────────────────────────
    "#ffffff": "--color-fff",            # lama: color-white → v2: color-fff
    "#fff":    "--color-fff",

    # ── Semantic ─────────────────────────────────────────────────
    "#e11d48": "--color-danger",
    "#f43f5e": "--color-danger",
    "#ef4444": "--color-red-500",
    "#d97706": "--color-warning",
    "#f59e0b": "--color-warning",
    "#fbbf24": "--color-warning",
    "#0284c7": "--color-info",
    "#0ea5e9": "--color-info",
    "#38bdf8": "--color-sky-400",
    "#4f46e5": "--color-accent",
    "#6366f1": "--color-indigo-500",
    "#818cf8": "--color-indigo-400",
    "#a5b4fc": "--color-indigo-300",
    "#c7d2fe": "--color-indigo-200",
    "#eff6ff": "--color-indigo-50",
    "#8b5cf6": "--color-violet-500",
    "#a78bfa": "--color-violet-400",
    "#7c3aed": "--color-violet-600",
    "#3b82f6": "--color-blue-500",
    "#60a5fa": "--color-blue-400",
    "#bfdbfe": "--color-blue-200",
    "#dbeafe": "--color-blue-100",
    "#be185d": "--color-pink-700",
    "#ec4899": "--color-pink-400",
    "#bbf7d0": "--color-green-200",
    "#86efac": "--color-green-300",
    "#f0fdf4": "--color-green-100",
    "#16a34a": "--color-green-500",
    "#92400e": "--color-amber-800",
}

# [B] RGBA base → token name template
# Format: (r,g,b) → (token_prefix, note)
# Alpha di-append: 0.12 → -a12
RGBA_BASE_MAP: dict[tuple, str] = {
    # Emerald bases → primary
    (5,   150, 105): "--color-primary",   # rgba(5,150,105,α)
    (4,   120, 87):  "--color-primary",   # rgba(4,120,87,α)
    (0,   103, 79):  "--color-primary",   # rgba(0,103,79,α)  — v2 emerald
    # Glass / surface
    (255, 255, 255): "--color-white",     # resolve lebih lanjut per alpha
    (15,  23,  42):  "--glass-dark",      # resolve per alpha
    (0,   0,   0):   "--color-black",
    # Semantic
    (99,  102, 241): "--color-indigo",
    (139, 92,  246): "--color-violet",
    (14,  165, 233): "--color-sky",
    (244, 63,  94):  "--color-rose",
    (245, 158, 11):  "--color-amber",
    (226, 232, 240): "--color-slate-200",  # border
    (248, 250, 252): "--color-surface",    # surface
    (241, 245, 249): "--color-slate-100",
}

# Peta alpha khusus untuk rgba(255,255,255,α)
WHITE_ALPHA_MAP = {
    "0.20": "--color-white-a020", "0.2":  "--color-white-a020",
    ".20":  "--color-white-a020", ".2":   "--color-white-a020",
    "0.30": "--color-white-a030", "0.3":  "--color-white-a030",
    ".30":  "--color-white-a030", ".3":   "--color-white-a030",
    "0.40": "--color-white-a040", "0.4":  "--color-white-a040",
    ".40":  "--color-white-a040", ".4":   "--color-white-a040",
    "0.48": "--glass-bg-subtle",
    ".48":  "--glass-bg-subtle",
    "0.50": "--color-white-a050", "0.5":  "--color-white-a050",
    ".50":  "--color-white-a050", ".5":   "--color-white-a050",
    "0.60": "--color-white-a060", "0.6":  "--color-white-a060",
    ".60":  "--color-white-a060", ".6":   "--color-white-a060",
    "0.70": "--glass-bg",         "0.7":  "--glass-bg",
    ".70":  "--glass-bg",         ".7":   "--glass-bg",
    "0.72": "--glass-bg",
    ".72":  "--glass-bg",
    "0.80": "--glass-border",     "0.8":  "--glass-border",
    ".80":  "--glass-border",     ".8":   "--glass-border",
    "0.82": "--glass-border",
    ".82":  "--glass-border",
    "0.85": "--color-white-a085",
    ".85":  "--color-white-a085",
    "0.90": "--color-white-a090", "0.9":  "--color-white-a090",
    ".90":  "--color-white-a090", ".9":   "--color-white-a090",
    "0.92": "--glass-bg-strong",
    ".92":  "--glass-bg-strong",
    "0.94": "--glass-bg-strong",
    ".94":  "--glass-bg-strong",
    "0.95": "--color-white-a095",
    ".95":  "--color-white-a095",
    "0.08": "--glass-dark-border",
    ".08":  "--glass-dark-border",
}

# Peta alpha untuk rgba(15,23,42,α) — dark overlay
DARK_ALPHA_MAP = {
    "0.35": "--glass-dark-bg", ".35": "--glass-dark-bg",
    "0.40": "--glass-dark-bg", "0.4": "--glass-dark-bg",
    ".40":  "--glass-dark-bg", ".4":  "--glass-dark-bg",
    "0.42": "--glass-dark-bg", ".42": "--glass-dark-bg",
    "0.90": "--glass-bg-strong", "0.9": "--glass-bg-strong",
    ".90":  "--glass-bg-strong", ".9": "--glass-bg-strong",
    "0.92": "--glass-bg-strong", ".92": "--glass-bg-strong",
}

# Peta alpha suffix untuk primary (5,150,105), (4,120,87), (0,103,79)
def _primary_alpha_token(alpha_str: str) -> str:
    """rgba emerald → --color-primary-aXX"""
    # Normalize alpha ke 2 digit
    a = alpha_str.lstrip('.')
    if '.' not in a:
        a = '0.' + a
    try:
        val = float(a)
        pct = int(round(val * 100))
        # Map ke token yang ada
        token_map = {
            0:  "--color-primary-a03",  # 0.00 ~ transparent
            3:  "--color-primary-a03",
            5:  "--color-primary-a05",
            6:  "--color-primary-a06",
            8:  "--color-primary-a08",
            10: "--color-primary-a10",
            12: "--color-primary-a12",
            15: "--color-primary-a15",
            20: "--color-primary-a20",
            25: "--color-primary-a25",
            28: "--color-primary-a28",
            30: "--color-primary-a30",
            35: "--color-primary-a35",
            40: "--color-primary-a40",
            50: "--color-primary-a50",
            55: "--color-primary-a55",
            60: "--color-primary-a60",
            65: "--color-primary-a65",
            70: "--color-primary-a70",
            80: "--color-primary-a80",
            90: "--color-primary-a90",
        }
        # Cari yang paling dekat
        closest = min(token_map.keys(), key=lambda x: abs(x - pct))
        return token_map[closest]
    except Exception:
        return f"--color-primary-a{alpha_str.replace('.','').lstrip('0') or '0'}"


# ══════════════════════════════════════════════════════════════════
# REGEX
# ══════════════════════════════════════════════════════════════════

RE_STYLE_BLOCK = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.DOTALL | re.IGNORECASE)
RE_HEX         = re.compile(r'(?<![a-fA-F0-9#])#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![a-fA-F0-9])')
RE_RGBA        = re.compile(
    r'rgba?\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\s*\)',
    re.IGNORECASE
)


# ══════════════════════════════════════════════════════════════════
# RESOLVERS
# ══════════════════════════════════════════════════════════════════

def resolve_hex(raw: str) -> str | None:
    """Resolve hex → token name. Return None jika tidak ada di map."""
    return HEX_TOKEN_MAP.get(raw.lower())


def resolve_rgba(r_str, g_str, b_str, a_str) -> str | None:
    """Resolve rgba → token name. Return None jika tidak ada di map."""
    try:
        r, g, b = int(float(r_str)), int(float(g_str)), int(float(b_str))
    except Exception:
        return None

    base = (r, g, b)

    # Primary emerald bases
    if base in {(5,150,105), (4,120,87), (0,103,79)}:
        if a_str is None:
            return "--color-primary"
        return _primary_alpha_token(a_str)

    # White
    if base == (255, 255, 255):
        if a_str is None:
            return "--color-fff"
        return WHITE_ALPHA_MAP.get(a_str) or WHITE_ALPHA_MAP.get(
            str(round(float(a_str), 2))
        )

    # Dark overlay
    if base == (15, 23, 42):
        if a_str is None:
            return "--glass-dark-bg"
        return DARK_ALPHA_MAP.get(a_str) or DARK_ALPHA_MAP.get(
            str(round(float(a_str), 2))
        )

    # Other bases — check with tolerance ±3
    for known_base, token_prefix in RGBA_BASE_MAP.items():
        kr, kg, kb = known_base
        if abs(kr-r) <= 3 and abs(kg-g) <= 3 and abs(kb-b) <= 3:
            if base in {(255,255,255), (15,23,42), (5,150,105), (4,120,87), (0,103,79)}:
                continue  # already handled above
            # Add alpha suffix — normalize to 2-digit integer pct
            if a_str is None:
                return token_prefix
            try:
                a_val = float(a_str)
                pct   = int(round(a_val * 100))
                return f"{token_prefix}-a{pct:02d}"
            except Exception:
                return f"{token_prefix}-a{a_str.replace('.','').lstrip('0') or '0'}"

    return None


# ══════════════════════════════════════════════════════════════════
# PROCESSOR
# ══════════════════════════════════════════════════════════════════

def process_style_block(css: str) -> tuple[str, int, list]:
    """
    Replace hex + rgba hardcode di dalam satu <style> block.
    Return: (new_css, count, samples)
    """
    count   = 0
    samples = []
    result  = css

    # 1. Replace rgba dulu (lebih spesifik, hindari partial match dengan hex)
    def rgba_replacer(m):
        nonlocal count
        r_s, g_s, b_s, a_s = m.group(1), m.group(2), m.group(3), m.group(4)
        token = resolve_rgba(r_s, g_s, b_s, a_s)
        if token:
            count += 1
            orig = m.group(0)
            samples.append((orig, f"var({token})"))
            return f"var({token})"
        return m.group(0)

    result = RE_RGBA.sub(rgba_replacer, result)

    # 2. Replace hex
    def hex_replacer(m):
        nonlocal count
        raw = m.group(0)  # '#047857'
        token = resolve_hex(raw)
        if token:
            count += 1
            samples.append((raw, f"var({token})"))
            return f"var({token})"
        return raw

    result = RE_HEX.sub(hex_replacer, result)

    return result, count, samples


def process_file(content: str) -> tuple[str, int, list]:
    """Process seluruh file — hanya sentuh <style> blocks."""
    total    = 0
    all_samp = []

    def style_replacer(m):
        nonlocal total, all_samp
        open_tag  = m.group(1)
        css       = m.group(2)
        close_tag = m.group(3)
        new_css, n, s = process_style_block(css)
        total    += n
        all_samp += s
        return open_tag + new_css + close_tag

    new_content = RE_STYLE_BLOCK.sub(style_replacer, content)
    return new_content, total, all_samp


# ══════════════════════════════════════════════════════════════════
# FILE UTILITIES
# ══════════════════════════════════════════════════════════════════

def is_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def find_templates(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.html") if not is_skip(p))


def backup_file(path: Path, backup_root: Path) -> None:
    stamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_dir = backup_root / stamp
    try:
        rel  = path.relative_to(Path.cwd())
    except ValueError:
        rel  = Path(path.name)
    dest = dest_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)


# ══════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════

def run(root: Path, backup_dir: Path, dry_run: bool, verbose: bool, threshold: int) -> list[dict]:
    templates = find_templates(root)
    results   = []

    for path in templates:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  {Y}⚠  Gagal baca {path.name}: {e}{RST}")
            continue

        rel          = str(path.relative_to(root)).replace("\\", "/")
        new_content, n, samples = process_file(content)

        if n < threshold:
            continue

        results.append({
            "path"   : rel,
            "count"  : n,
            "samples": samples[:5],
            "changed": new_content != content,
        })

        if verbose:
            print(f"  {DIM}{rel:<55}{RST}  {G}{n:>4} penggantian{RST}")
            for orig, repl in samples[:3]:
                print(f"    {DIM}↳ {orig[:35]:35} → {repl}{RST}")

        if not dry_run and new_content != content:
            backup_file(path, backup_dir)
            path.write_text(new_content, encoding="utf-8")

    return results


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Lumra Token Migrator v2 — <style> block only, tidak overwrite CSS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--root",      type=Path, default=DEFAULT_ROOT)
    p.add_argument("--backup",    type=Path, default=DEFAULT_BACKUP)
    p.add_argument("--threshold", type=int,  default=1,
                   help="Proses file jika ada >= N penggantian (default: 1)")
    p.add_argument("--dry-run",   action="store_true", default=False)
    p.add_argument("--apply",     action="store_true", default=False)
    p.add_argument("--report",    type=Path, default=None)
    p.add_argument("--verbose",   action="store_true", default=False)
    return p.parse_args()


def main():
    args = parse_args()
    if not args.apply:
        args.dry_run = True

    print(f"\n{hr('═')}")
    print(f"  {B}Lumra Token Migrator  v2{RST}  —  <style> blocks only")
    print(hr('═'))
    print(f"  Root   : {DIM}{args.root}{RST}")
    print(f"  Scope  : {W}<style> blocks di template{RST}  (bukan inline style=\"\")")
    print(f"  CSS    : {G}TIDAK diubah{RST}  (design_system.css v2 tetap utuh)")
    print(f"  Mode   : {Y if args.dry_run else G}{'DRY-RUN' if args.dry_run else 'APPLY'}{RST}\n")

    if not args.root.exists():
        print(f"{R}[ERROR] Root tidak ditemukan: {args.root}{RST}")
        sys.exit(1)

    results = run(
        root       = args.root,
        backup_dir = args.backup,
        dry_run    = args.dry_run,
        verbose    = args.verbose or True,  # always show detail
        threshold  = args.threshold,
    )

    total_files = len(results)
    total_n     = sum(r["count"] for r in results)

    print(f"\n{hr()}")
    print(f"  File terpengaruh  : {W}{total_files}{RST}")
    print(f"  Total penggantian : {G}{total_n}{RST}")
    print(hr())

    if args.report:
        args.report.write_text(
            json.dumps(results, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"\n  {G}📄 Report: {args.report}{RST}")

    if args.dry_run:
        print(f"\n  {Y}DRY-RUN — tidak ada file yang diubah.{RST}")
        print(f"  Jalankan dengan {W}--apply{RST} untuk apply.\n")
    else:
        print(f"\n  {G}✅ Selesai. Backup: {args.backup}{RST}\n")

    print(hr('═') + "\n")


if __name__ == "__main__":
    main()