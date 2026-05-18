"""
lumra_consolidate.py — Lumra ERP · Template Consolidation Tool
==============================================================
Menggabungkan semua template ke dalam lumra_pages/ sebagai satu-satunya
sumber template aktif, lalu mengarsipkan folder app yang sudah tidak dipakai.

STEP 1 — MERGE
  Scan folder app (sales/, inventory/, dll)
  → File yang BELUM ada di lumra_pages/ → PINDAH ke lumra_pages/subfolder/
  → File yang SUDAH ada di lumra_pages/ → SKIP (tidak ditimpa)

STEP 2 — ARCHIVE
  Folder app yang sudah kosong atau semua isinya sudah ada di lumra_pages/
  → Pindah ke _archive/app_templates/

Cara pakai:
  python lumra_consolidate.py              → preview (AMAN)
  python lumra_consolidate.py --apply      → eksekusi
  python lumra_consolidate.py --apply --yes → tanpa konfirmasi
  python lumra_consolidate.py --undo       → rollback
"""

import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ── Warna ─────────────────────────────────────────────────────────────
G   = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B   = '\033[94m'; C = '\033[96m'; DIM = '\033[2m'; W = '\033[97m'; RST = '\033[0m'

def OK(m):   print(f'  {G}✅  {m}{RST}')
def WARN(m): print(f'  {Y}⚠️   {m}{RST}')
def INFO(m): print(f'  {C}ℹ️   {m}{RST}')
def HEAD(m): print(f'\n{B}{"═"*10} {W}{m}{RST}{B} {"═"*10}{RST}')
def ERR(m):  print(f'  {R}❌  {m}{RST}')


# ── Konfigurasi ────────────────────────────────────────────────────────

BASE_DIR      = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'lumra_config' / 'templates'
LUMRA_PAGES   = TEMPLATES_DIR / 'lumra_pages'
ARCHIVE_DIR   = BASE_DIR / '_archive' / 'app_templates'
LOG_FILE      = BASE_DIR / '.lumra_consolidate_log.json'

# Mapping: folder app → subfolder di lumra_pages/
# Sesuaikan jika nama subfolder di lumra_pages/ berbeda
FOLDER_MAP = {
    'auth_app'    : 'auth',          # templates/auth_app/ → lumra_pages/auth/
    'inventory'   : 'inventory',     # templates/inventory/ → lumra_pages/inventory/
    'marketing'   : 'marketing',     # templates/marketing/ → lumra_pages/marketing/ (buat jika belum ada)
    'master_data' : 'master_data',   # templates/master_data/ → lumra_pages/master_data/
    'production'  : 'production',    # templates/production/ → lumra_pages/production/
    'reports'     : 'reports',       # templates/reports/ → lumra_pages/reports/
    'sales'       : 'sales',         # templates/sales/ → lumra_pages/sales/
    'settings_app': 'settings',      # templates/settings_app/ → lumra_pages/settings/
}

# Folder/file di root templates/ yang langsung diarsip (tidak perlu merge)
ROOT_ORPHANS = [
    'base.html',    # duplikat dari base/base.html
    '_archive',     # folder archive lama di dalam templates/
]

# Folder yang tidak pernah diarsip
PROTECTED_FOLDERS = {'base', 'lumra_pages'}


# ── Helper ─────────────────────────────────────────────────────────────

def read_file(p: Path) -> str | None:
    for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    return None


def save_log(log: list):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def load_log() -> list:
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            return json.load(f)
    return []


# ── Analisis ───────────────────────────────────────────────────────────

def analyze() -> dict:
    """
    Scan semua folder app dan tentukan:
    - to_move   : file yang belum ada di lumra_pages/ → perlu dipindah
    - to_skip   : file yang sudah ada di lumra_pages/ → skip
    - to_archive: folder yang sudah semua isinya ada di lumra_pages/
    """
    to_move   = []  # {'src': Path, 'dst': Path, 'reason': str}
    to_skip   = []  # {'src': Path, 'dst': Path, 'reason': str}
    to_archive_folders = []
    to_archive_orphans = []

    for app_folder, lp_subfolder in FOLDER_MAP.items():
        src_dir = TEMPLATES_DIR / app_folder
        dst_dir = LUMRA_PAGES / lp_subfolder

        if not src_dir.exists():
            continue

        files = list(src_dir.rglob('*.html'))
        folder_all_covered = True

        for src_file in files:
            # Path relatif terhadap src_dir
            rel = src_file.relative_to(src_dir)
            dst_file = dst_dir / rel

            if dst_file.exists():
                to_skip.append({
                    'src'   : src_file,
                    'dst'   : dst_file,
                    'reason': 'sudah ada di lumra_pages/',
                })
            else:
                to_move.append({
                    'src'   : src_file,
                    'dst'   : dst_file,
                    'reason': f'hanya ada di {app_folder}/',
                })
                folder_all_covered = False

        # Folder bisa diarsip kalau semua filenya sudah di lumra_pages/
        if folder_all_covered and files:
            to_archive_folders.append(src_dir)
        elif not files:
            # Folder kosong → langsung arsip
            to_archive_folders.append(src_dir)

    # Root orphans
    for name in ROOT_ORPHANS:
        target = TEMPLATES_DIR / name
        if target.exists():
            to_archive_orphans.append(target)

    return {
        'to_move'            : to_move,
        'to_skip'            : to_skip,
        'to_archive_folders' : to_archive_folders,
        'to_archive_orphans' : to_archive_orphans,
    }


# ── Preview ────────────────────────────────────────────────────────────

def run_preview(data: dict):
    HEAD('STEP 1 — MERGE: File dipindah ke lumra_pages/')

    if not data['to_move']:
        OK('Tidak ada file yang perlu dipindah — semua sudah ada di lumra_pages/')
    else:
        for item in data['to_move']:
            src_rel = item['src'].relative_to(TEMPLATES_DIR)
            dst_rel = item['dst'].relative_to(TEMPLATES_DIR)
            print(f"  {G}→{RST}  {DIM}{src_rel}{RST}  →  {G}{dst_rel}{RST}")

    if data['to_skip']:
        print(f"\n  {DIM}Skip (sudah ada di lumra_pages/) — {len(data['to_skip'])} file:{RST}")
        for item in data['to_skip']:
            src_rel = item['src'].relative_to(TEMPLATES_DIR)
            print(f"  {DIM}⏭   {src_rel}{RST}")

    HEAD('STEP 2 — ARCHIVE: Folder app yang tidak lagi dibutuhkan')

    if not data['to_archive_folders'] and not data['to_archive_orphans']:
        OK('Tidak ada folder yang perlu diarsip (masih ada file unik di folder app)')
    else:
        for folder in data['to_archive_folders']:
            rel = folder.relative_to(TEMPLATES_DIR)
            file_count = len(list(folder.rglob('*.html')))
            status = f'{file_count} file (semua sudah di lumra_pages/)' if file_count else 'kosong'
            print(f"  {Y}📁  {rel}  [{status}]  →  _archive/app_templates/{RST}")
        for orphan in data['to_archive_orphans']:
            rel = orphan.relative_to(TEMPLATES_DIR)
            print(f"  {Y}📄  {rel}  →  _archive/app_templates/{RST}")

    # Ringkasan
    print(f'\n  {"─"*55}')
    print(f'  {G}Dipindah ke lumra_pages/ : {len(data["to_move"])} file{RST}')
    print(f'  {DIM}Skip (sudah ada)        : {len(data["to_skip"])} file{RST}')
    print(f'  {Y}Diarsipkan              : {len(data["to_archive_folders"]) + len(data["to_archive_orphans"])} folder/file{RST}')

    # Folder yang belum bisa diarsip karena masih ada file unik
    folders_not_ready = set(FOLDER_MAP.keys()) - {
        f.name for f in data['to_archive_folders']
    } - {'_archive', 'base.html'}

    # Saring yang ada di disk
    folders_not_ready = [
        f for f in folders_not_ready
        if (TEMPLATES_DIR / f).exists()
    ]

    if folders_not_ready:
        print(f'\n  {Y}⚠️   Folder berikut belum bisa diarsip (masih ada file unik):{RST}')
        for fname in sorted(folders_not_ready):
            folder = TEMPLATES_DIR / fname
            unique = [
                item for item in data['to_move']
                if item['src'].is_relative_to(folder)
            ]
            print(f'  {Y}     {fname}/ — {len(unique)} file unik akan dipindah dulu{RST}')
        INFO('Jalankan --apply untuk merge+arsip sekaligus.')

    print(f'\n  Gunakan {C}--apply{RST} untuk menerapkan.\n')


# ── Apply ──────────────────────────────────────────────────────────────

def run_apply(data: dict, yes: bool):
    run_preview(data)

    if not data['to_move'] and not data['to_archive_folders'] and not data['to_archive_orphans']:
        OK('Tidak ada yang perlu dilakukan.')
        return

    if not yes:
        try:
            confirm = input('\n  Terapkan semua perubahan di atas? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.\n')
            return
        if confirm != 'y':
            print('  Dibatalkan.\n')
            return

    log = []
    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')

    # ── STEP 1: Merge ───────────────────────────────────────────────
    HEAD('STEP 1 — Merge file ke lumra_pages/')
    merged = 0
    for item in data['to_move']:
        src = item['src']
        dst = item['dst']
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)    # copy dulu, hapus nanti setelah folder diarsip
            log.append({'type': 'merge', 'src': str(src), 'dst': str(dst)})
            src_rel = src.relative_to(TEMPLATES_DIR)
            dst_rel = dst.relative_to(TEMPLATES_DIR)
            print(f'  {G}✓{RST}  {DIM}{src_rel}{RST}  →  {G}{dst_rel}{RST}')
            merged += 1
        except Exception as e:
            ERR(f'Gagal merge {src.name}: {e}')

    OK(f'{merged} file berhasil di-merge ke lumra_pages/')

    # ── Re-analyze setelah merge untuk update status archive ────────
    data_after = analyze()

    # ── STEP 2: Archive ─────────────────────────────────────────────
    HEAD('STEP 2 — Arsipkan folder app')
    archived = 0
    archive_dest = ARCHIVE_DIR / ts

    for folder in data_after['to_archive_folders']:
        try:
            rel  = folder.relative_to(TEMPLATES_DIR)
            dest = archive_dest / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(folder), str(dest))
            log.append({'type': 'archive_folder', 'src': str(folder), 'dst': str(dest)})
            print(f'  {Y}📁  {rel}  →  _archive/app_templates/{ts}/{rel}{RST}')
            archived += 1
        except Exception as e:
            ERR(f'Gagal arsip folder {folder.name}: {e}')

    for orphan in data_after['to_archive_orphans']:
        try:
            rel  = orphan.relative_to(TEMPLATES_DIR)
            dest = archive_dest / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(orphan), str(dest))
            log.append({'type': 'archive_file', 'src': str(orphan), 'dst': str(dest)})
            print(f'  {Y}📄  {rel}  →  _archive/app_templates/{ts}/{rel}{RST}')
            archived += 1
        except Exception as e:
            ERR(f'Gagal arsip {orphan.name}: {e}')

    OK(f'{archived} folder/file diarsipkan')

    save_log(log)

    HEAD('Selesai')
    OK('lumra_pages/ sekarang satu-satunya sumber template aktif.')
    INFO('Verifikasi : python lumra_sync.py')
    INFO('Rollback   : python lumra_consolidate.py --undo')
    print()


# ── Undo ───────────────────────────────────────────────────────────────

def run_undo():
    log = load_log()
    if not log:
        OK('Tidak ada log — tidak ada yang bisa di-undo.')
        return

    restored = 0
    for entry in reversed(log):
        t   = entry['type']
        src = Path(entry['src'])
        dst = Path(entry['dst'])

        if t == 'merge':
            # Hapus file yang di-copy ke lumra_pages/
            if dst.exists():
                dst.unlink()
                print(f'  ↩️  Hapus {dst.relative_to(TEMPLATES_DIR)}')
                restored += 1

        elif t in ('archive_folder', 'archive_file'):
            # Kembalikan dari _archive ke posisi semula
            if dst.exists():
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
                print(f'  ↩️  {dst.name}  ← dikembalikan ke templates/')
                restored += 1
            else:
                WARN(f'Arsip tidak ditemukan: {dst}')

    LOG_FILE.unlink(missing_ok=True)
    OK(f'{restored} item dikembalikan.')


# ── Entry Point ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP — Template Consolidation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python lumra_consolidate.py              → preview
  python lumra_consolidate.py --apply      → merge + arsip
  python lumra_consolidate.py --apply --yes → tanpa konfirmasi
  python lumra_consolidate.py --undo       → rollback
        """
    )
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--yes',   action='store_true')
    parser.add_argument('--undo',  action='store_true')
    args = parser.parse_args()

    print(f'\n{B}{"═"*55}')
    print(f'  {W}Lumra ERP — Template Consolidation Tool{RST}')
    print(f'{B}{"═"*55}{RST}')
    print(f'  Templates : {DIM}{TEMPLATES_DIR}{RST}')
    print(f'  Master    : {G}lumra_pages/{RST}')
    print(f'  Mode      : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}')

    if not TEMPLATES_DIR.exists():
        ERR(f'Folder templates tidak ditemukan: {TEMPLATES_DIR}')
        sys.exit(1)

    if not LUMRA_PAGES.exists():
        ERR(f'lumra_pages/ tidak ditemukan di: {LUMRA_PAGES}')
        ERR('Pastikan lumra_pages/ sudah ada sebelum menjalankan script ini.')
        sys.exit(1)

    if args.undo:
        run_undo()
        return

    data = analyze()

    if args.apply:
        run_apply(data, yes=args.yes)
    else:
        run_preview(data)
        if data['to_move'] or data['to_archive_folders']:
            WARN('Ini PREVIEW — tidak ada perubahan dilakukan.')


if __name__ == '__main__':
    main()