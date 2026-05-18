"""
lumra_cleanup_duplicates.py
============================
Hapus template duplikat — sisakan hanya yang dipakai oleh views.
Ground truth diambil dari hasil grep render() di views.

Cara pakai:
  python lumra_cleanup_duplicates.py           → preview
  python lumra_cleanup_duplicates.py --apply   → hapus duplikat
  python lumra_cleanup_duplicates.py --undo    → kembalikan dari backup
"""

import sys, shutil, json, argparse
from pathlib import Path
from datetime import datetime

BASE       = Path(__file__).resolve().parent
TEMPLATES  = BASE / 'lumra_config' / 'templates'
BACKUP_DIR = BASE / '.lumra_dup_backup'
LOG_FILE   = BASE / '.lumra_dup_log.json'

# ══════════════════════════════════════════════════════
# CANONICAL MAP
# Key   = filename
# Value = folder yang BENAR (dipakai oleh views)
# Duplikat di folder lain akan dihapus.
# ══════════════════════════════════════════════════════
CANONICAL = {
    # inventory — dipakai inventory_views.py & pricing_views.py
    'products.html'                    : 'lumra_pages/inventory',
    'product_details.html'             : 'lumra_pages/inventory',
    'supplier_price_list.html'         : 'lumra_pages/inventory',
    'supplier_price_form.html'         : 'lumra_pages/inventory',
    'stock_opname_approvals.html'      : 'lumra_pages/inventory',
    'stock_opname_approval_detail.html': 'lumra_pages/inventory',
    'stock_opname_form.html'           : 'lumra_pages/inventory',
    'stock_opname_locations.html'      : 'lumra_pages/inventory',
    'add_stock_movement.html'          : 'lumra_pages/inventory',
    'stock_movement.html'              : 'lumra_pages/inventory',

    # reports — dipakai report_views.py & misc_views.py
    'sales_performance.html'           : 'lumra_pages/reports',
    'sales_history_product.html'       : 'lumra_pages/reports',
    'purchasing_report.html'           : 'lumra_pages/reports',
    'report_inventory_log.html'        : 'lumra_pages/reports',
    'report_inventory_low.html'        : 'lumra_pages/reports',
    'report_inventory_stock.html'      : 'lumra_pages/reports',
    'report_sales_by_product.html'     : 'lumra_pages/reports',
}

G   = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
C   = '\033[96m'; DIM = '\033[2m'; W = '\033[97m'; RST = '\033[0m'
B   = '\033[94m'

def HEAD(m): print(f'\n{B}{"═"*10} {W}{m}{RST}{B} {"═"*10}{RST}')
def OK(m):   print(f'  {G}✅  {m}{RST}')
def WARN(m): print(f'  {Y}⚠️   {m}{RST}')
def INFO(m): print(f'  {C}ℹ️   {m}{RST}')


def find_duplicates():
    """
    Untuk setiap file di CANONICAL, cari semua kopiannya di disk.
    Return list of (canonical_path, [duplicate_paths]).
    """
    results = []
    for filename, canonical_folder in CANONICAL.items():
        canonical_path = TEMPLATES / Path(canonical_folder) / filename
        all_copies = list(TEMPLATES.rglob(filename))

        duplicates = [
            p for p in all_copies
            if p.resolve() != canonical_path.resolve()
        ]

        if duplicates or not canonical_path.exists():
            results.append({
                'filename'  : filename,
                'canonical' : canonical_path,
                'exists'    : canonical_path.exists(),
                'duplicates': duplicates,
            })

    return results


def preview(data):
    HEAD('Canonical template locations (dipakai views)')
    for item in data:
        fn  = item['filename']
        can = item['canonical'].relative_to(TEMPLATES)
        exists_mark = f'{G}✅{RST}' if item['exists'] else f'{R}❌ TIDAK ADA{RST}'
        print(f'  {C}{fn}{RST}')
        print(f'    canonical : {can}  {exists_mark}')
        if item['duplicates']:
            for dup in item['duplicates']:
                rel = dup.relative_to(TEMPLATES)
                print(f'    {Y}duplikat  : {rel}  → akan dihapus{RST}')
        print()

    total_dups = sum(len(i['duplicates']) for i in data)
    missing    = sum(1 for i in data if not i['exists'])

    print(f'  {"─"*50}')
    print(f'  {Y}Duplikat yang akan dihapus : {total_dups}{RST}')
    if missing:
        print(f'  {R}Canonical tidak ada di disk: {missing} file{RST}')
        print(f'  {DIM}  (views akan error kalau file ini tidak ada){RST}')
    print()
    return total_dups


def apply_cleanup(data, yes=False):
    total_dups = preview(data)

    if total_dups == 0:
        OK('Tidak ada duplikat — folder sudah bersih.')
        return

    if not yes:
        try:
            confirm = input('  Hapus semua duplikat? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.')
            return
        if confirm != 'y':
            print('  Dibatalkan.')
            return

    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    log = []

    HEAD('Menghapus duplikat')
    for item in data:
        for dup in item['duplicates']:
            rel = dup.relative_to(TEMPLATES)
            bak = BACKUP_DIR / ts / rel
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dup, bak)
            dup.unlink()
            log.append({'deleted': str(dup), 'backup': str(bak)})
            print(f'  {Y}🗑️  {rel}{RST}  →  backup: {DIM}{bak.name}{RST}')

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    HEAD('Selesai')
    OK(f'{len(log)} file duplikat dihapus.')
    INFO('Backup tersimpan di: ' + str(BACKUP_DIR / ts))
    INFO('Rollback: python lumra_cleanup_duplicates.py --undo')


def undo():
    if not LOG_FILE.exists():
        OK('Tidak ada log backup.')
        return
    with open(LOG_FILE) as f:
        log = json.load(f)
    restored = 0
    for entry in log:
        src = Path(entry['backup'])
        dst = Path(entry['deleted'])
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f'  ↩️  {dst.relative_to(TEMPLATES)}')
            restored += 1
        else:
            WARN(f'Backup tidak ada: {src}')
    LOG_FILE.unlink(missing_ok=True)
    OK(f'{restored} file dikembalikan.')


def main():
    parser = argparse.ArgumentParser(description='Lumra — Hapus template duplikat')
    parser.add_argument('--apply', action='store_true', help='Hapus duplikat')
    parser.add_argument('--yes',   action='store_true', help='Tanpa konfirmasi')
    parser.add_argument('--undo',  action='store_true', help='Rollback')
    args = parser.parse_args()

    print(f'\n{B}{"═"*52}')
    print(f'  {W}Lumra ERP — Cleanup Template Duplikat{RST}')
    print(f'{B}{"═"*52}{RST}')

    if not TEMPLATES.exists():
        print(f'  {R}templates/ tidak ditemukan: {TEMPLATES}{RST}')
        sys.exit(1)

    if args.undo:
        undo()
        return

    data = find_duplicates()

    if args.apply:
        apply_cleanup(data, yes=args.yes)
    else:
        preview(data)
        WARN('Ini PREVIEW — gunakan --apply untuk menghapus duplikat.')
        print()


if __name__ == '__main__':
    main()