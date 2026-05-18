#!/usr/bin/env python3
"""
lumra_theme_purchasing.py
=========================
Mengubah tema warna Emerald → Blue untuk halaman Purchasing/Vendor/Supplier.

Visual language Lumra ERP:
  🟢 Emerald  = Sales, Revenue, Customer  (uang masuk)
  🔵 Blue     = Purchasing, Vendor, Supplier (uang keluar)

Cara pakai:
  python lumra_theme_purchasing.py --dry-run     # preview saja
  python lumra_theme_purchasing.py               # apply perubahan
  python lumra_theme_purchasing.py --restore     # kembalikan dari backup

Author : Lumra ERP Team
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────────────────────────────────────

# Root folder template — sesuaikan dengan path project kamu
TEMPLATE_ROOT = Path(r"D:\APPS\Project\lumra\lumra_config\templates")

# File yang masuk kategori Purchasing (akan diberi tema biru)
PURCHASING_PATTERNS = [
    "purchasing",
    "vendor_form",
    "vendor_list",
    "vendors_list",
    "supplier_price",
]

# Folder backup
BACKUP_DIR = Path(r"D:\APPS\Project\lumra\_theme_backup")

# ─────────────────────────────────────────────────────────────────────────────
# PETA WARNA: Emerald → Blue
# ─────────────────────────────────────────────────────────────────────────────

# Format: (pattern_regex, replacement)
# Urutan penting — spesifik dulu, umum belakangan

COLOR_MAP = [

    # ── Tailwind opacity shorthand ─────────────────────────────────────────
    # bg-emerald-* → bg-blue-*
    (r'\bbg-emerald-(\d+)',          r'bg-blue-\1'),
    # text-emerald-* → text-blue-*
    (r'\btext-emerald-(\d+)',        r'text-blue-\1'),
    # border-emerald-* → border-blue-*
    (r'\bborder-emerald-(\d+)',      r'border-blue-\1'),
    # ring-emerald-* → ring-blue-*
    (r'\bring-emerald-(\d+)',        r'ring-blue-\1'),
    # from-emerald-* → from-blue-*
    (r'\bfrom-emerald-(\d+)',        r'from-blue-\1'),
    # to-emerald-* → to-blue-*
    (r'\bto-emerald-(\d+)',          r'to-blue-\1'),
    # via-emerald-* → via-blue-*
    (r'\bvia-emerald-(\d+)',         r'via-blue-\1'),
    # divide-emerald-* → divide-blue-*
    (r'\bdivide-emerald-(\d+)',      r'divide-blue-\1'),
    # focus:ring-emerald-* → focus:ring-blue-*
    (r'\bfocus:ring-emerald-(\d+)', r'focus:ring-blue-\1'),
    # hover:bg-emerald-* → hover:bg-blue-*
    (r'\bhover:bg-emerald-(\d+)',   r'hover:bg-blue-\1'),
    # hover:text-emerald-* → hover:text-blue-*
    (r'\bhover:text-emerald-(\d+)', r'hover:text-blue-\1'),
    # hover:border-emerald-* → hover:border-blue-*
    (r'\bhover:border-emerald-(\d+)', r'hover:border-blue-\1'),
    # animate:bg-emerald-* etc. (catch-all prefix:emerald)
    (r'\b(\w+):emerald-(\d+)',      r'\1:blue-\2'),

    # ── CSS rgba emerald tones ─────────────────────────────────────────────
    # #10b981 (emerald-500) → #3b82f6 (blue-500)
    (r'#10b981',  '#3b82f6'),
    # #059669 (emerald-600) → #2563eb (blue-600)
    (r'#059669',  '#2563eb'),
    # #047857 (emerald-700) → #1d4ed8 (blue-700)
    (r'#047857',  '#1d4ed8'),
    # #34d399 (emerald-400) → #60a5fa (blue-400)
    (r'#34d399',  '#60a5fa'),
    # #6ee7b7 (emerald-300) → #93c5fd (blue-300)
    (r'#6ee7b7',  '#93c5fd'),
    # #a7f3d0 (emerald-200) → #bfdbfe (blue-200)
    (r'#a7f3d0',  '#bfdbfe'),
    # #d1fae5 (emerald-100) → #dbeafe (blue-100)
    (r'#d1fae5',  '#dbeafe'),
    # #ecfdf5 (emerald-50)  → #eff6ff (blue-50)
    (r'#ecfdf5',  '#eff6ff'),
    # #065f46 (emerald-900) → #1e3a5f (blue-900-ish)
    (r'#065f46',  '#1e3a8a'),
    # #064e3b (emerald-950) → #1e3a5f
    (r'#064e3b',  '#1e3a5f'),

    # ── CSS rgba dengan emerald tones (inline style) ───────────────────────
    # rgba(16,185,129,...) → rgba(59,130,246,...)   emerald-500 → blue-500
    (r'rgba\(16,\s*185,\s*129,',    'rgba(59,130,246,'),
    (r'rgba\(16,185,129,',          'rgba(59,130,246,'),
    # rgba(5,150,105,...) → rgba(37,99,235,...)     emerald-600 → blue-600
    (r'rgba\(5,\s*150,\s*105,',     'rgba(37,99,235,'),
    (r'rgba\(5,150,105,',           'rgba(37,99,235,'),
    # rgba(4,120,87,...) → rgba(29,78,216,...)      emerald-700 → blue-700
    (r'rgba\(4,\s*120,\s*87,',      'rgba(29,78,216,'),
    # rgba(52,211,153,...) → rgba(96,165,250,...)   emerald-400 → blue-400
    (r'rgba\(52,\s*211,\s*153,',    'rgba(96,165,250,'),
    # rgba(209,250,229,...) → rgba(219,234,254,...)  emerald-100 → blue-100
    (r'rgba\(209,\s*250,\s*229,',   'rgba(219,234,254,'),
    # rgba(240,253,244,...) → rgba(239,246,255,...)  emerald-50 → blue-50
    (r'rgba\(240,\s*253,\s*244,',   'rgba(239,246,255,'),
    # rgba(6,95,70,...) → rgba(30,58,138,...)        emerald-900 → blue-900
    (r'rgba\(6,\s*95,\s*70,',       'rgba(30,58,138,'),

    # ── CSS gradient string emerald ────────────────────────────────────────
    # radial-gradient(#10b981,...) → radial-gradient(#3b82f6,...)
    (r'radial-gradient\(#10b981,\s*#059669\)',
     'radial-gradient(#3b82f6,#2563eb)'),
    # linear-gradient emerald → blue
    (r'linear-gradient\(135deg,\s*#10b981\s+0%,\s*#059669\s+100%\)',
     'linear-gradient(135deg,#3b82f6 0%,#2563eb 100%)'),
    (r'linear-gradient\(90deg,\s*#10b981,\s*#059669\)',
     'linear-gradient(90deg,#3b82f6,#2563eb)'),

    # ── Orb/blob background ────────────────────────────────────────────────
    # background:radial-gradient(#10b981 orb → blue
    (r'(background\s*:\s*radial-gradient\()#10b981,\s*#059669(\))',
     r'\1#3b82f6,#2563eb\2'),

    # ── CSS variable nesting (kalau ada --color-accent:emerald) ───────────
    (r'--color-accent\s*:\s*#10b981', '--color-accent:#3b82f6'),
    (r'--color-accent-dark\s*:\s*#059669', '--color-accent-dark:#2563eb'),

    # ── box-shadow emerald glow ────────────────────────────────────────────
    # 0 3px 10px rgba(16,185,129,...) → blue
    (r'box-shadow\s*:\s*0\s+3px\s+10px\s+rgba\(16,185,129,',
     'box-shadow:0 3px 10px rgba(59,130,246,'),
    (r'box-shadow\s*:\s*0\s+5px\s+16px\s+rgba\(16,185,129,',
     'box-shadow:0 5px 16px rgba(59,130,246,'),

    # ── Alpine / JS string literals ────────────────────────────────────────
    # 'text-emerald-600' → 'text-blue-600' (dalam JS string)
    (r"'text-emerald-(\d+)'",   r"'text-blue-\1'"),
    (r'"text-emerald-(\d+)"',   r'"text-blue-\1"'),
    (r"'bg-emerald-(\d+)'",     r"'bg-blue-\1'"),
    (r'"bg-emerald-(\d+)"',     r'"bg-blue-\1"'),
    (r"'border-emerald-(\d+)'", r"'border-blue-\1'"),
    (r'"border-emerald-(\d+)"', r'"border-blue-\1"'),

    # ── focus:outline + ring ───────────────────────────────────────────────
    (r'focus:ring-2 focus:ring-emerald-400', 'focus:ring-2 focus:ring-blue-400'),
    (r'focus:ring-emerald-500',  'focus:ring-blue-500'),

    # ── animate-pulse dot (notif / status) ────────────────────────────────
    # bg-emerald-500 animate-pulse → bg-blue-500 (status dot)
    # sudah tercakup di bg-emerald-* di atas

]

# ─────────────────────────────────────────────────────────────────────────────
# TAMBAHAN: Teks label kontekstual (opsional — default OFF)
# Uncomment baris di bawah kalau mau ganti teks juga
# ─────────────────────────────────────────────────────────────────────────────

LABEL_MAP = [
    # (r'Riwayat Penjualan',  'Riwayat Pembelian'),
    # (r'Sales History',      'Purchase History'),
]


# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI UTAMA
# ─────────────────────────────────────────────────────────────────────────────

def is_purchasing_file(path: Path) -> bool:
    """True kalau nama file match salah satu PURCHASING_PATTERNS."""
    name = path.stem.lower()  # nama file tanpa ekstensi
    return any(p in name for p in PURCHASING_PATTERNS)


def find_target_files(root: Path) -> list[Path]:
    """Cari semua .html yang masuk kategori purchasing."""
    targets = []
    for f in root.rglob("*.html"):
        if is_purchasing_file(f):
            targets.append(f)
    return sorted(targets)


def apply_replacements(content: str, rules: list[tuple]) -> tuple[str, int]:
    """Apply semua replacement rules, return (new_content, total_changes)."""
    total = 0
    for pattern, replacement in rules:
        new_content, n = re.subn(pattern, replacement, content)
        total += n
        content = new_content
    # Normalisasi rgba spacing tidak konsisten setelah replace
    content = re.sub(
        r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*",
        lambda m: f"rgba({m.group(1)},{m.group(2)},{m.group(3)},",
        content
    )
    return content, total


def backup_file(path: Path, backup_root: Path) -> Path:
    """Copy file ke backup dir dengan timestamp."""
    rel = path.relative_to(TEMPLATE_ROOT)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    return dest


def restore_from_backup(backup_root: Path):
    """Kembalikan semua file dari backup."""
    if not backup_root.exists():
        print("❌ Backup tidak ditemukan.")
        return

    restored = 0
    for src in backup_root.rglob("*.html"):
        rel  = src.relative_to(backup_root)
        dest = TEMPLATE_ROOT / rel
        if dest.exists():
            shutil.copy2(src, dest)
            print(f"  ↩️  Restored: {rel}")
            restored += 1

    print(f"\n✅ {restored} file berhasil dikembalikan.")


def preview_changes(content: str, new_content: str, path: Path, max_lines: int = 8):
    """Tampilkan diff sederhana."""
    old_lines = content.splitlines()
    new_lines = new_content.splitlines()
    shown = 0
    for i, (a, b) in enumerate(zip(old_lines, new_lines)):
        if a != b and shown < max_lines:
            print(f"    L{i+1:4d}  - {a.strip()[:90]}")
            print(f"           + {b.strip()[:90]}")
            shown += 1
    if shown == max_lines:
        print("           … (lebih banyak perubahan)")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Lumra Theme Switcher — Emerald → Blue untuk Purchasing pages"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview perubahan tanpa menyimpan file"
    )
    parser.add_argument(
        "--restore", action="store_true",
        help="Kembalikan file dari backup"
    )
    parser.add_argument(
        "--root", type=str, default=None,
        help=f"Override TEMPLATE_ROOT (default: {TEMPLATE_ROOT})"
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Skip backup (tidak direkomendasikan)"
    )
    args = parser.parse_args()

    # Override root jika diberikan
    root = Path(args.root) if args.root else TEMPLATE_ROOT
    if not root.exists():
        print(f"❌ Template root tidak ditemukan: {root}")
        sys.exit(1)

    # Restore mode
    if args.restore:
        print("↩️  Mode RESTORE — mengembalikan file dari backup...\n")
        restore_from_backup(BACKUP_DIR)
        return

    # Buat backup dir dengan timestamp
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = BACKUP_DIR / ts

    # Cari file target
    targets = find_target_files(root)

    if not targets:
        print("⚠️  Tidak ada file purchasing/vendor ditemukan.")
        print(f"   Root  : {root}")
        print(f"   Pattern: {PURCHASING_PATTERNS}")
        return

    all_rules = COLOR_MAP + LABEL_MAP

    print("=" * 65)
    print("  🎨 Lumra Theme Switcher — Emerald → Blue (Purchasing)")
    print("=" * 65)
    print(f"  Root     : {root}")
    print(f"  Target   : {len(targets)} file")
    print(f"  Mode     : {'DRY RUN (tidak ada yang disimpan)' if args.dry_run else 'APPLY'}")
    if not args.dry_run and not args.no_backup:
        print(f"  Backup   : {backup_root}")
    print()

    total_files_changed = 0
    total_replacements  = 0

    for path in targets:
        rel = path.relative_to(root)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  ⚠️  Skip {rel} — error baca: {e}")
            continue

        new_content, n_changes = apply_replacements(content, all_rules)

        if n_changes == 0:
            print(f"  ⬜ {rel}  (tidak ada perubahan)")
            continue

        print(f"  🔵 {rel}  ({n_changes} perubahan)")
        if args.dry_run:
            preview_changes(content, new_content, path)
        else:
            # Backup dulu
            if not args.no_backup:
                backup_file(path, backup_root)
            # Tulis file baru
            path.write_text(new_content, encoding="utf-8")

        total_files_changed += 1
        total_replacements  += n_changes

    print()
    print("=" * 65)
    print(f"  {'[DRY RUN] ' if args.dry_run else ''}Selesai!")
    print(f"  File diubah   : {total_files_changed}/{len(targets)}")
    print(f"  Total replace : {total_replacements}")
    if not args.dry_run and not args.no_backup and total_files_changed > 0:
        print(f"  Backup di     : {backup_root}")
        print(f"  Restore       : python lumra_theme_purchasing.py --restore")
    print("=" * 65)


if __name__ == "__main__":
    main()