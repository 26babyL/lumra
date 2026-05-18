"""
lumra_reorganize.py
====================
Dua tugas sekaligus:
  1. Pindahkan template dari root lumra_pages/ ke subfolder yang benar
  2. Fix semua render() path di views agar sesuai lokasi baru

Cara pakai:
  python lumra_reorganize.py           → preview
  python lumra_reorganize.py --apply   → eksekusi
  python lumra_reorganize.py --undo    → rollback
"""

import re, sys, shutil, json, argparse
from pathlib import Path
from datetime import datetime

BASE       = Path(__file__).resolve().parent
TEMPLATES  = BASE / 'lumra_config' / 'templates'
LUMRA_PAGES= TEMPLATES / 'lumra_pages'
VIEWS_DIR  = BASE / 'lumra_config' / 'views'
BACKUP_DIR = BASE / '.lumra_reorg_backup'
LOG_FILE   = BASE / '.lumra_reorg_log.json'

G='\033[92m'; Y='\033[93m'; R='\033[91m'
B='\033[94m'; C='\033[96m'; DIM='\033[2m'; W='\033[97m'; RST='\033[0m'

def HEAD(m): print(f'\n{B}{"═"*10} {W}{m}{RST}{B} {"═"*10}{RST}')
def OK(m):   print(f'  {G}✅  {m}{RST}')
def WARN(m): print(f'  {Y}⚠️   {m}{RST}')
def INFO(m): print(f'  {C}ℹ️   {m}{RST}')

# ══════════════════════════════════════════════════════
# MASTER MAP — file → subfolder yang benar
# ══════════════════════════════════════════════════════
MOVE_MAP = {
    # Sales
    'dashboard.html'             : 'lumra_pages/sales',
    'notification.html'          : 'lumra_pages/sales',
    'sales_insight.html'         : 'lumra_pages/sales',

    # Master data
    'customers.html'             : 'lumra_pages/master_data',
    'customer.html'              : 'lumra_pages/master_data',

    # Marketing
    'campaign.html'              : 'lumra_pages/marketing',
    'discount.html'              : 'lumra_pages/marketing',
    'loyalty_members.html'       : 'lumra_pages/marketing',

    # Reports
    'market_insights.html'       : 'lumra_pages/reports',
    'trends_analysis.html'       : 'lumra_pages/reports',
    'activity_log.html'          : 'lumra_pages/reports',

    # Inventory
    'stock_movement.html'        : 'lumra_pages/inventory',
    'add_stock_movement.html'    : 'lumra_pages/inventory',

    # Settings
    'users.html'                 : 'lumra_pages/settings',
    'profile.html'               : 'lumra_pages/settings',
    'about.html'                 : 'lumra_pages/settings',
    'contact.html'               : 'lumra_pages/settings',
    'search.html'                : 'lumra_pages/settings',
    'user_roles_permissions.html': 'lumra_pages/settings',

    # Error pages — tetap di lumra_pages/ root
    # 'error_403.html' → tidak dipindah
}

# ══════════════════════════════════════════════════════
# BUILD FINAL TRUTH MAP
# Setelah pemindahan, ini adalah lokasi canonical semua file
# ══════════════════════════════════════════════════════
def build_final_truth():
    """
    Scan template di disk + terapkan MOVE_MAP →
    kembalikan dict: filename → correct_full_path (relatif ke TEMPLATES)
    """
    truth = {}

    # Scan semua file yang sudah ada di subfolder (sudah benar)
    for f in LUMRA_PAGES.rglob('*.html'):
        rel      = str(f.relative_to(TEMPLATES)).replace('\\', '/')
        basename = f.name
        folder   = str(f.parent.relative_to(LUMRA_PAGES)).replace('\\', '/')

        # Kalau file ini ada di MOVE_MAP → lokasi barunya
        if basename in MOVE_MAP:
            target_folder = MOVE_MAP[basename]
            correct = f'{target_folder}/{basename}'
        else:
            correct = rel

        # Ambiguous check: skip kalau ada di 2 subfolder dan tidak di MOVE_MAP
        if basename in truth and truth[basename] != correct:
            if basename not in MOVE_MAP:
                truth[basename] = None  # ambiguous, jangan auto-fix
                continue

        truth[basename] = correct

    # Hapus yang None (ambiguous)
    truth = {k: v for k, v in truth.items() if v is not None}
    return truth


# ══════════════════════════════════════════════════════
# STEP 1 — Rencana pemindahan file
# ══════════════════════════════════════════════════════
def plan_moves():
    moves = []
    for filename, target_folder in MOVE_MAP.items():
        src = LUMRA_PAGES / filename
        if not src.exists():
            continue  # sudah dipindah atau tidak ada

        dst_folder = TEMPLATES / Path(target_folder)
        dst = dst_folder / filename

        if src.resolve() == dst.resolve():
            continue  # sudah di tempat yang benar

        moves.append({'src': src, 'dst': dst, 'filename': filename,
                      'from': str(src.relative_to(TEMPLATES)),
                      'to'  : str(dst.relative_to(TEMPLATES))})
    return moves


# ══════════════════════════════════════════════════════
# STEP 2 — Rencana fix render() di views
# ══════════════════════════════════════════════════════
RENDER_RE = re.compile(
    r"""(render\s*\(\s*\w+\s*,\s*|TemplateResponse\s*\(\s*\w+\s*,\s*)(['"])([^'"]+\.html)\2""",
    re.VERBOSE
)

def plan_view_fixes(truth):
    fixes = []
    for py in sorted(VIEWS_DIR.rglob('*.py')):
        src = py.read_text(encoding='utf-8', errors='ignore')
        file_fixes = []
        for m in RENDER_RE.finditer(src):
            tmpl     = m.group(3).replace('\\', '/')
            basename = Path(tmpl).name
            if basename not in truth:
                continue
            correct = truth[basename]
            if tmpl != correct:
                file_fixes.append({'old': tmpl, 'new': correct})
        if file_fixes:
            fixes.append({'file': py, 'filename': py.name, 'changes': file_fixes})
    return fixes


def apply_view_fix(pyfile: Path, changes: list):
    src = pyfile.read_text(encoding='utf-8', errors='ignore')
    for c in changes:
        src = src.replace(f'"{c["old"]}"', f'"{c["new"]}"')
        src = src.replace(f"'{c['old']}'", f"'{c['new']}'")
    pyfile.write_text(src, encoding='utf-8')


# ══════════════════════════════════════════════════════
# PREVIEW
# ══════════════════════════════════════════════════════
def preview():
    moves      = plan_moves()
    truth      = build_final_truth()
    view_fixes = plan_view_fixes(truth)

    HEAD('Step 1 — Pemindahan template ke subfolder')
    if moves:
        for m in moves:
            print(f'  {DIM}{m["from"]}{RST}')
            print(f'  {G}→ {m["to"]}{RST}\n')
    else:
        OK('Semua template sudah di subfolder yang benar.')

    HEAD('Step 2 — Fix render() path di views')
    if view_fixes:
        for vf in view_fixes:
            print(f'  {C}📄  {vf["filename"]}{RST}')
            for c in vf['changes']:
                print(f'    {DIM}{c["old"]}{RST}')
                print(f'    {G}→ {c["new"]}{RST}')
            print()
    else:
        OK('Semua render() sudah menggunakan path yang benar.')

    total_moves = len(moves)
    total_fixes = sum(len(v['changes']) for v in view_fixes)
    print(f'  {"─"*50}')
    print(f'  {Y}File dipindah  : {total_moves}{RST}')
    print(f'  {G}render() difix : {total_fixes}{RST}')
    print()

    return moves, truth, view_fixes


# ══════════════════════════════════════════════════════
# APPLY
# ══════════════════════════════════════════════════════
def apply(yes=False):
    moves, truth, view_fixes = preview()

    if not moves and not view_fixes:
        OK('Tidak ada yang perlu dilakukan.')
        return

    if not yes:
        try:
            confirm = input('  Terapkan semua perubahan? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.')
            return
        if confirm != 'y':
            print('  Dibatalkan.')
            return

    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    log = {'moves': [], 'view_fixes': []}

    HEAD('Memindahkan template')
    for m in moves:
        bak = BACKUP_DIR / ts / 'templates' / m['from']
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(m['src'], bak)

        m['dst'].parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(m['src']), str(m['dst']))

        log['moves'].append({
            'src': str(m['src']), 'dst': str(m['dst']), 'bak': str(bak)
        })
        print(f'  {G}✅{RST}  {m["from"]}  →  {m["to"]}')

    HEAD('Fix render() di views')
    for vf in view_fixes:
        bak = BACKUP_DIR / ts / 'views' / vf['file'].name
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(vf['file'], bak)

        apply_view_fix(vf['file'], vf['changes'])

        log['view_fixes'].append({
            'file': str(vf['file']), 'bak': str(bak),
            'changes': vf['changes']
        })
        print(f'  {G}✅{RST}  {vf["filename"]}')
        for c in vf['changes']:
            print(f'    {DIM}{c["old"]}{RST}  →  {G}{c["new"]}{RST}')

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    HEAD('Selesai')
    OK(f'{len(moves)} template dipindah.')
    OK(f'{sum(len(v["changes"]) for v in view_fixes)} render() path difix.')
    INFO('Verifikasi: python manage.py check')
    INFO('Rollback  : python lumra_reorganize.py --undo')
    print()


# ══════════════════════════════════════════════════════
# UNDO
# ══════════════════════════════════════════════════════
def undo():
    if not LOG_FILE.exists():
        OK('Tidak ada log.')
        return
    with open(LOG_FILE) as f:
        log = json.load(f)

    HEAD('Rollback template')
    for entry in reversed(log.get('moves', [])):
        bak = Path(entry['bak'])
        dst = Path(entry['dst'])
        src = Path(entry['src'])
        if bak.exists():
            if dst.exists():
                dst.unlink()
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bak, src)
            print(f'  ↩️  {dst.name} kembali ke {src.parent.name}/')

    HEAD('Rollback views')
    for entry in log.get('view_fixes', []):
        bak  = Path(entry['bak'])
        orig = Path(entry['file'])
        if bak.exists():
            shutil.copy2(bak, orig)
            print(f'  ↩️  {orig.name}')

    LOG_FILE.unlink(missing_ok=True)
    OK('Rollback selesai.')


# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description='Lumra — Reorganize templates + fix render() paths')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--yes',   action='store_true')
    parser.add_argument('--undo',  action='store_true')
    args = parser.parse_args()

    print(f'\n{B}{"═"*54}')
    print(f'  {W}Lumra ERP — Template Reorganizer{RST}')
    print(f'{B}{"═"*54}{RST}')
    print(f'  Mode : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}')

    if not LUMRA_PAGES.exists():
        print(f'  {R}lumra_pages/ tidak ditemukan{RST}')
        sys.exit(1)

    if args.undo:
        undo()
        return

    if args.apply:
        apply(yes=args.yes)
    else:
        preview()
        WARN('Ini PREVIEW — gunakan --apply untuk menerapkan.')
        print()


if __name__ == '__main__':
    main()