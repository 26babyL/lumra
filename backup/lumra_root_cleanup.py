"""
lumra_root_cleanup.py — Lumra ERP · Root lumra_pages/ Cleanup
=============================================================
Memindahkan file HTML yang berserakan di root lumra_pages/
ke subfolder yang tepat.

Aturan:
  - File sudah ada di subfolder → SKIP (tidak ditimpa)
  - File belum ada di subfolder → PINDAH
  - Setelah semua dipindah → hapus sisa di root lumra_pages/

Cara pakai:
  python lumra_root_cleanup.py           → preview
  python lumra_root_cleanup.py --apply   → eksekusi
  python lumra_root_cleanup.py --undo    → rollback
"""

import shutil, json, argparse, sys
from pathlib import Path
from datetime import datetime

# ── Warna ──────────────────────────────────────────────────────────────
G='\033[92m'; Y='\033[93m'; R='\033[91m'; B='\033[94m'
C='\033[96m'; DIM='\033[2m'; W='\033[97m'; RST='\033[0m'

def OK(m):   print(f'  {G}✅  {m}{RST}')
def WARN(m): print(f'  {Y}⚠️   {m}{RST}')
def INFO(m): print(f'  {C}ℹ️   {m}{RST}')
def HEAD(m): print(f'\n{B}{"═"*10} {W}{m}{RST}{B} {"═"*10}{RST}')
def ERR(m):  print(f'  {R}❌  {m}{RST}')

# ── Path ───────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
LUMRA_PAGES = BASE_DIR / 'lumra_config' / 'templates' / 'lumra_pages'
ARCHIVE_DIR = BASE_DIR / '_archive' / 'lumra_pages_root'
LOG_FILE    = BASE_DIR / '.lumra_root_cleanup_log.json'

# ── Mapping file → subfolder ───────────────────────────────────────────
# Berdasarkan kondisi aktual dari dir output
FILE_MAP = {
    # Sales
    'dashboard.html'          : 'sales',
    'notification.html'       : 'sales',
    'stock_movement.html'     : 'sales',
    'add_stock_movement.html' : 'sales',

    # Settings
    'about.html'              : 'settings',
    'contact.html'            : 'settings',
    'search.html'             : 'settings',
    'profile.html'            : 'settings',
    'users.html'              : 'settings',
    'user_roles_permissions.html': 'settings',

    # Marketing
    'campaign.html'           : 'marketing',
    'discount.html'           : 'marketing',
    'loyalty_members.html'    : 'marketing',

    # Reports / Insights
    'activity_log.html'       : 'reports',
    'market_insights.html'    : 'reports',
    'trends_analysis.html'    : 'reports',

    # Master data
    'customers.html'          : 'master_data',

    # Tetap di root lumra_pages/ (error pages & utility)
    'error_403.html'          : None,   # None = tetap di root
}

# ── Log ────────────────────────────────────────────────────────────────
def save_log(log):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def load_log():
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            return json.load(f)
    return []

# ── Analisis ───────────────────────────────────────────────────────────
def analyze():
    to_move   = []  # pindah ke subfolder
    to_skip   = []  # sudah ada di subfolder → skip
    to_keep   = []  # tetap di root (None mapping)
    unknown   = []  # ada di root tapi tidak ada di FILE_MAP

    root_files = [f for f in LUMRA_PAGES.iterdir() if f.is_file() and f.suffix == '.html']

    for f in sorted(root_files):
        name = f.name

        if name not in FILE_MAP:
            unknown.append(f)
            continue

        subfolder = FILE_MAP[name]

        if subfolder is None:
            to_keep.append(f)
            continue

        dst = LUMRA_PAGES / subfolder / name

        if dst.exists():
            to_skip.append({'src': f, 'dst': dst})
        else:
            to_move.append({'src': f, 'dst': dst})

    return {
        'to_move' : to_move,
        'to_skip' : to_skip,
        'to_keep' : to_keep,
        'unknown' : unknown,
    }

# ── Preview ────────────────────────────────────────────────────────────
def run_preview(data):
    HEAD('File dipindah ke subfolder')
    if not data['to_move']:
        OK('Tidak ada file yang perlu dipindah.')
    for item in data['to_move']:
        subfolder = item['dst'].parent.name
        print(f"  {G}→{RST}  {item['src'].name}  →  lumra_pages/{subfolder}/")

    HEAD('Skip — sudah ada di subfolder (tidak ditimpa)')
    if not data['to_skip']:
        print(f'  {DIM}(tidak ada){RST}')
    for item in data['to_skip']:
        subfolder = item['dst'].parent.name
        print(f"  {DIM}⏭   {item['src'].name}  (sudah ada di {subfolder}/){RST}")

    HEAD('Tetap di root lumra_pages/')
    if not data['to_keep']:
        print(f'  {DIM}(tidak ada){RST}')
    for f in data['to_keep']:
        print(f"  {C}📄  {f.name}{RST}")

    if data['unknown']:
        HEAD('⚠️  Tidak ada di mapping — perlu perhatian manual')
        for f in data['unknown']:
            print(f"  {Y}?   {f.name}{RST}")

    print(f'\n  {"─"*50}')
    print(f'  {G}Dipindah : {len(data["to_move"])} file{RST}')
    print(f'  {DIM}Skip     : {len(data["to_skip"])} file (duplikat di subfolder){RST}')
    print(f'  {C}Tetap    : {len(data["to_keep"])} file di root{RST}')
    if data['unknown']:
        print(f'  {Y}Unknown  : {len(data["unknown"])} file — tambahkan ke FILE_MAP manual{RST}')
    print(f'\n  Gunakan {C}--apply{RST} untuk menerapkan.\n')

# ── Apply ──────────────────────────────────────────────────────────────
def run_apply(data, yes):
    run_preview(data)

    if not data['to_move'] and not data['to_skip']:
        OK('Tidak ada yang perlu dilakukan.')
        return

    if not yes:
        try:
            confirm = input('\n  Terapkan? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.\n')
            return
        if confirm != 'y':
            print('  Dibatalkan.\n')
            return

    log  = []
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    moved   = 0
    deleted = 0

    HEAD('Memindahkan file')
    for item in data['to_move']:
        src, dst = item['src'], item['dst']
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            log.append({'type': 'move', 'src': str(src), 'dst': str(dst)})
            print(f"  {G}✓{RST}  {src.name}  →  lumra_pages/{dst.parent.name}/")
            moved += 1
        except Exception as e:
            ERR(f'Gagal pindah {src.name}: {e}')

    # Hapus file dari root yang sudah dipindah atau sudah ada di subfolder
    HEAD('Membersihkan root lumra_pages/')
    files_to_delete = [i['src'] for i in data['to_move']] + [i['src'] for i in data['to_skip']]
    for f in files_to_delete:
        if f.exists():
            # Arsip dulu sebelum hapus
            arc = ARCHIVE_DIR / ts / f.name
            arc.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, arc)
            f.unlink()
            log.append({'type': 'delete_root', 'file': str(f), 'archive': str(arc)})
            print(f"  {DIM}🗑   {f.name} (root copy dihapus){RST}")
            deleted += 1

    save_log(log)

    print()
    HEAD('Selesai')
    OK(f'{moved} file dipindah ke subfolder.')
    OK(f'{deleted} file root copy dibersihkan.')
    if data['unknown']:
        WARN(f"{len(data['unknown'])} file unknown — tambahkan ke FILE_MAP di script ini.")
    INFO('Jalankan ulang audit: python lumra_glass_audit.py')
    print()

# ── Undo ───────────────────────────────────────────────────────────────
def run_undo():
    log = load_log()
    if not log:
        OK('Tidak ada log.')
        return
    restored = 0
    for entry in reversed(log):
        t = entry['type']
        if t == 'move':
            dst = Path(entry['dst'])
            if dst.exists():
                dst.unlink()
                print(f"  ↩️  Hapus {dst.name} dari subfolder")
                restored += 1
        elif t == 'delete_root':
            arc = Path(entry['archive'])
            orig = Path(entry['file'])
            if arc.exists():
                shutil.copy2(arc, orig)
                print(f"  ↩️  Kembalikan {orig.name} ke root")
                restored += 1
    LOG_FILE.unlink(missing_ok=True)
    OK(f'{restored} item dikembalikan.')

# ── Main ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Lumra root lumra_pages/ cleanup')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--yes',   action='store_true')
    parser.add_argument('--undo',  action='store_true')
    args = parser.parse_args()

    print(f'\n{B}{"═"*50}')
    print(f'  {W}Lumra — Root lumra_pages/ Cleanup{RST}')
    print(f'{B}{"═"*50}{RST}')
    print(f'  lumra_pages/ : {DIM}{LUMRA_PAGES}{RST}')
    print(f'  Mode         : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}')

    if not LUMRA_PAGES.exists():
        ERR(f'lumra_pages/ tidak ditemukan.')
        sys.exit(1)

    if args.undo:
        run_undo()
        return

    data = analyze()

    if args.apply:
        run_apply(data, yes=args.yes)
    else:
        run_preview(data)

if __name__ == '__main__':
    main()