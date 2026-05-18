#!/usr/bin/env python3
"""
lumra_emerald_upgrade.py
========================
Upgrade hardcode emerald di HTML templates ke Emerald Premium Lumra.

Cara pakai:
  python lumra_emerald_upgrade.py --dry-run
  python lumra_emerald_upgrade.py --dry-run --file dashboard.html
  python lumra_emerald_upgrade.py --apply
  python lumra_emerald_upgrade.py --report
  python lumra_emerald_upgrade.py --restore
"""

import re, sys, shutil, argparse
from pathlib import Path
from datetime import datetime

TEMPLATE_ROOT = Path(r"D:\APPS\Project\lumra\lumra_config\templates")
BACKUP_DIR    = Path(r"D:\APPS\Project\lumra\_emerald_upgrade_backup")
SKIP_PATTERNS = ["purchasing","vendor_form","vendor_list","vendors_list","supplier_price"]

# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE STRATEGY — placeholder-based
#
# Masalah: kalau replace #10b981→#059669 dulu, lalu #059669→#047857,
# hex yang baru di-replace ikut kena lagi (double-replacement).
#
# Solusi: ganti dulu ke placeholder unik, baru resolve di akhir sekaligus.
#
# Emerald shift map (satu shade lebih dalam):
#   #10b981  em-500  →  #059669  em-600 (jadi primary baru)
#   #059669  em-600  →  #047857  em-700
#   #047857  em-700  →  #065f46  em-800
#   #065f46  em-800  →  #022C22  em-900 (British Racing Green)
#   #064e3b  em-950  →  #011F17  near-black
#   rgba(16,185,129,...)  em-500  →  rgba(5,150,105,...)   em-600
#   rgba(5,150,105,...)   em-600  →  rgba(4,120,87,...)    em-700
#   rgba(4,120,87,...)    em-700  →  rgba(6,95,70,...)     em-800
#   rgba(52,211,153,...)  em-400  →  rgba(16,185,129,...)  em-500
#
# Yang TIDAK diubah (tetap, hanya light accent):
#   #34d399  em-400  — sparkle/glow
#   #6ee7b7  em-300  — light highlight
#   #ecfdf5  em-50   — background
#   #d1fae5  em-100  — background
#   #a7f3d0  em-200  — background
# ─────────────────────────────────────────────────────────────────────────────

# Placeholder → final value
PLACEHOLDER_MAP = {
    '__EM500__' : '#059669',
    '__EM600__' : '#047857',
    '__EM700__' : '#065f46',
    '__EM800__' : '#022C22',
    '__EM950__' : '#011F17',
    '__RGBA500__': 'rgba(5,150,105,',
    '__RGBA600__': 'rgba(4,120,87,',
    '__RGBA700__': 'rgba(6,95,70,',
    '__RGBA400__': 'rgba(16,185,129,',
}

def apply_upgrades(content):
    """
    Two-phase upgrade:
    Phase 1 — replace semua source color ke placeholder unik
    Phase 2 — resolve semua placeholder ke final value
    """
    original = content
    changes  = 0

    # ── PHASE 1: Gradients & multi-token patterns dulu ──────────
    # Harus sebelum single-token replacement

    grad_replacements = [
        # 3-stop gradient (perf strip)
        ('linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%)',
         'linear-gradient(135deg,__EM800__ 0%,__EM700__ 50%,__EM600__ 100%)'),
        ('linear-gradient(135deg,#065f46 0%,#047857 50%,#059669 100%)',
         'linear-gradient(135deg,__EM800__ 0%,__EM700__ 50%,__EM600__ 100%)'),
        # 2-stop gradients
        ('linear-gradient(135deg, #10b981 0%, #059669 100%)',
         'linear-gradient(135deg,__EM500__ 0%,__EM600__ 100%)'),
        ('linear-gradient(135deg,#10b981 0%,#059669 100%)',
         'linear-gradient(135deg,__EM500__ 0%,__EM600__ 100%)'),
        ('linear-gradient(135deg, #10B981 0%, #059669 100%)',
         'linear-gradient(135deg,__EM500__ 0%,__EM600__ 100%)'),
        ('linear-gradient(135deg, #047857 0%, #059669 100%)',
         'linear-gradient(135deg,__EM700__ 0%,__EM600__ 100%)'),
        ('linear-gradient(135deg,#047857 0%,#059669 100%)',
         'linear-gradient(135deg,__EM700__ 0%,__EM600__ 100%)'),
        ('linear-gradient(90deg, #10b981, #059669)',
         'linear-gradient(90deg,__EM500__,__EM600__)'),
        ('linear-gradient(90deg,#10b981,#059669)',
         'linear-gradient(90deg,__EM500__,__EM600__)'),
        ('linear-gradient(90deg, #10b981, #34d399)',
         'linear-gradient(90deg,__EM500__,#34d399)'),
        ('linear-gradient(90deg,#10b981,#34d399)',
         'linear-gradient(90deg,__EM500__,#34d399)'),
        # radial-gradient orb
        ('radial-gradient(#10b981, #059669)','radial-gradient(__EM500__,__EM600__)'),
        ('radial-gradient(#10b981,#059669)', 'radial-gradient(__EM500__,__EM600__)'),
        ('radial-gradient(#10B981,#059669)', 'radial-gradient(__EM500__,__EM600__)'),
        ('radial-gradient(#10B981, #059669)','radial-gradient(__EM500__,__EM600__)'),
        ('radial-gradient(#059669,#047857)', 'radial-gradient(__EM600__,__EM700__)'),
        ('radial-gradient(#059669, #047857)','radial-gradient(__EM600__,__EM700__)'),
    ]

    for old, new in grad_replacements:
        if old in content:
            n = content.count(old)
            content = content.replace(old, new)
            changes += n

    # ── PHASE 1b: rgba ───────────────────────────────────────────
    rgba_map = [
        # em-400 → em-500 placeholder
        ('rgba(52, 211, 153,', '__RGBA400__'),
        ('rgba(52,211,153,',   '__RGBA400__'),
        # em-500 → em-600 placeholder
        ('rgba(16, 185, 129,', '__RGBA500__'),
        ('rgba(16,185,129,',   '__RGBA500__'),
        # em-600 → em-700 placeholder
        ('rgba(5, 150, 105,',  '__RGBA600__'),
        ('rgba(5,150,105,',    '__RGBA600__'),
        # em-700 → em-800 placeholder
        ('rgba(4, 120, 87,',   '__RGBA700__'),
        ('rgba(4,120,87,',     '__RGBA700__'),
        # em-800+ — tetap (sudah sangat gelap, jarang dipakai)
    ]
    for old, new in rgba_map:
        if old in content:
            n = content.count(old)
            content = content.replace(old, new)
            changes += n

    # ── PHASE 1c: hex bare (pakai regex word boundary) ───────────
    hex_map = [
        (r'(?<![0-9a-fA-F])#10[bB]981(?![0-9a-fA-F])', '__EM500__'),
        (r'(?<![0-9a-fA-F])#059669(?![0-9a-fA-F])',     '__EM600__'),
        (r'(?<![0-9a-fA-F])#047857(?![0-9a-fA-F])',     '__EM700__'),
        (r'(?<![0-9a-fA-F])#065[fF]46(?![0-9a-fA-F])', '__EM800__'),
        (r'(?<![0-9a-fA-F])#064[eE]3[bB](?![0-9a-fA-F])','__EM950__'),
    ]
    for pattern, placeholder in hex_map:
        new_content, n = re.subn(pattern, placeholder, content)
        changes += n
        content = new_content

    # ── PHASE 2: resolve semua placeholder sekaligus ─────────────
    for placeholder, final in PLACEHOLDER_MAP.items():
        content = content.replace(placeholder, final)

    return content, changes


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def is_skip(path): return any(p in path.stem.lower() for p in SKIP_PATTERNS)

def find_files(root, target=None):
    if target:
        return [f for f in root.rglob(f"*{target}*") if f.suffix=='.html' and not is_skip(f)]
    return [f for f in sorted(root.rglob("*.html")) if not is_skip(f)]

def backup(path, backup_root):
    rel = path.relative_to(TEMPLATE_ROOT)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)

def restore(backup_root):
    if not backup_root.exists(): print("❌ Backup tidak ditemukan."); return
    n = 0
    for src in backup_root.rglob("*.html"):
        dest = TEMPLATE_ROOT / src.relative_to(backup_root)
        if dest.exists(): shutil.copy2(src, dest); print(f"  ↩  {src.name}"); n += 1
    print(f"\n✅ {n} file dikembalikan.")

def count_old(content):
    return sum(content.count(c) for c in ['#10b981','#10B981'])

def preview(old, new, limit=8):
    shown = 0
    for i,(a,b) in enumerate(zip(old.splitlines(), new.splitlines())):
        if a!=b and shown<limit:
            print(f"    \033[2mL{i+1:4d}\033[0m  \033[91m- {a.strip()[:88]}\033[0m")
            print(f"           \033[92m+ {b.strip()[:88]}\033[0m")
            shown+=1
    if shown==limit: print("           \033[2m…\033[0m")

def main():
    G='\033[92m';Y='\033[93m';C='\033[96m';W='\033[97m';DIM='\033[2m';RST='\033[0m'
    ap = argparse.ArgumentParser(description='Lumra Emerald Upgrade')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply',   action='store_true')
    ap.add_argument('--report',  action='store_true')
    ap.add_argument('--restore', action='store_true')
    ap.add_argument('--file',    type=str, default=None)
    ap.add_argument('--root',    type=str, default=None)
    ap.add_argument('--yes',     action='store_true')
    args = ap.parse_args()

    root = Path(args.root) if args.root else TEMPLATE_ROOT
    if not root.exists(): print(f"❌ Root tidak ditemukan: {root}"); sys.exit(1)

    print(f"\n{C}{'═'*66}")
    print(f"  {W}Lumra Emerald Upgrade{RST} — Tailwind Default → Emerald Premium")
    print(f"{C}{'═'*66}{RST}  Root: {DIM}{root}{RST}\n")

    if args.restore: restore(BACKUP_DIR); return

    files = find_files(root, args.file)
    if not files: print(f"{Y}  ⚠  Tidak ada file ditemukan.{RST}"); return

    if args.report:
        print(f"  {C}LAPORAN{RST}  ({len(files)} file)\n")
        dirty = 0
        for path in files:
            try: content = path.read_text(encoding='utf-8')
            except: continue
            n = count_old(content)
            if n:
                print(f"  {Y}⚠{RST}  {str(path.relative_to(root)):55s}  {Y}×{n}{RST}")
                dirty += 1
        print(f"\n  {'─'*60}")
        print(f"  {Y if dirty else G}{dirty} file masih ada warna lama.{RST}" if dirty else f"  {G}✅ Semua sudah upgrade!{RST}")
        return

    if not args.dry_run and not args.apply:
        print(f"  Gunakan --dry-run atau --apply\n"); return

    print(f"  Mode  : {G if args.apply else Y}{'APPLY' if args.apply else 'DRY RUN'}{RST}")
    print(f"  Files : {len(files)}\n")

    if args.apply and not args.yes:
        try: confirm = input("  Lanjutkan? (y/N): ").strip().lower()
        except: print("Dibatalkan."); return
        if confirm != 'y': print("Dibatalkan."); return
        print()

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_root = BACKUP_DIR / ts
    tf = tc = clean = 0

    for path in files:
        try: content = path.read_text(encoding='utf-8')
        except Exception as e: print(f"  ⚠  Skip {path.name}: {e}"); continue

        new_content, n = apply_upgrades(content)
        if n == 0: clean += 1; continue

        rel = path.relative_to(root)
        print(f"  {G}🔼{RST} {str(rel):55s} {G}{n:3d}{RST}")
        if args.dry_run:
            preview(content, new_content); print()
        else:
            backup(path, backup_root)
            path.write_text(new_content, encoding='utf-8')
        tf += 1; tc += n

    print(f"\n{C}{'═'*66}{RST}")
    if args.dry_run: print(f"  {Y}[DRY RUN]{RST} — tidak ada yang disimpan")
    else: print(f"  {G}✅ Selesai!{RST}")
    print(f"  File diubah  : {G}{tf}{RST}  |  Bersih: {clean}  |  Total: {G}{tc}{RST}")
    if args.apply and tf > 0:
        print(f"  Backup       : {DIM}{backup_root}{RST}")
        print(f"  Rollback     : python lumra_emerald_upgrade.py --restore")
    print(f"{C}{'═'*66}{RST}\n")

if __name__ == '__main__': main()