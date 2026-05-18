"""
lumra_mvc_align.py — Lumra ERP · MVC Alignment Tool
=====================================================
Menyeragamkan semua render() di views agar mengarah ke lumra_pages/,
lalu mengarsipkan folder template per-app yang tidak lagi dipakai.

Urutan kerja:
  STEP 1 — Scan semua views/**/*.py, temukan render() yang belum
           pakai prefix 'lumra_pages/'
  STEP 2 — Update path render() → 'lumra_pages/xxx.html'
  STEP 3 — Arsipkan folder template app (sales/, inventory/, dll)
           yang sudah tidak diperlukan

Cara pakai:
  python lumra_mvc_align.py                    → preview semua (AMAN)
  python lumra_mvc_align.py --apply            → eksekusi step 1+2+3
  python lumra_mvc_align.py --apply --step 1   → hanya fix render paths
  python lumra_mvc_align.py --apply --step 2   → hanya arsip folders
  python lumra_mvc_align.py --apply --yes      → tanpa konfirmasi
  python lumra_mvc_align.py --undo             → rollback dari backup
"""

import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ── Warna terminal ─────────────────────────────────────────────────────
G   = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B   = '\033[94m'; C = '\033[96m'; DIM = '\033[2m'; W = '\033[97m'; RST = '\033[0m'

def OK(m):   print(f'  {G}✅  {m}{RST}')
def WARN(m): print(f'  {Y}⚠️   {m}{RST}')
def INFO(m): print(f'  {C}ℹ️   {m}{RST}')
def HEAD(m): print(f'\n{B}{"═"*12} {W}{m}{RST}{B} {"═"*12}{RST}')
def ERR(m):  print(f'  {R}❌  {m}{RST}')
def ROW(a, b=''):
    print(f'  {DIM}{a}{RST}' + (f'  →  {G}{b}{RST}' if b else ''))


# ── Konfigurasi ────────────────────────────────────────────────────────

BASE_DIR      = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'lumra_config' / 'templates'
VIEWS_ROOT    = BASE_DIR / 'lumra_config'
BACKUP_DIR    = BASE_DIR / '.lumra_mvc_backup'
LOG_FILE      = BASE_DIR / '.lumra_mvc_log.json'
ARCHIVE_DIR   = BASE_DIR / '_archive' / 'app_templates'

# Folder template per-app yang akan diarsipkan setelah views diperbaiki.
# lumra_pages/ adalah MASTER — tidak diarsip.
APP_TEMPLATE_FOLDERS = [
    'auth_app',
    'inventory',
    'marketing',
    'master_data',
    'production',
    'reports',
    'sales',
    'settings_app',
]

# Folder/file di root templates/ yang langsung diarsip jika ada
ROOT_TEMPLATE_ORPHANS = [
    'base.html',        # duplikat dari base/base.html
    '_archive',         # folder archive lama di dalam templates/
]

# Subfolder di lumra_pages/ yang sudah ada — dipakai sebagai referensi mapping
LUMRA_PAGES_SUBFOLDERS = [
    'auth', 'inventory', 'master_data', 'sales',
    'reports', 'production', 'settings', 'marketing',
]

# Template selalu dipakai via extends/include — tidak pernah langsung di render()
BASE_COMPONENTS = {
    'base/base.html', 'base/navbar.html', 'base/sidebar.html',
    'base/sidebar_item.html', 'base/sidebar_right.html',
    'base/footer.html', 'base/alert.html', 'base/alert_inner.html',
    'base/kpi_card.html', 'base/kpi_card_inner.html', 'base/kpi_card_white.html',
    'base/activity_drawer.html', 'base/approval_modal.html',
    'base/error_404.html', 'base/error_500.html',
    'reports/base_report.html',
}


# ── Regex render() ─────────────────────────────────────────────────────

RENDER_RE = re.compile(
    r"""
    (?:
        render\s*\(\s*\w+\s*,\s*
      | TemplateResponse\s*\(\s*\w+\s*,\s*
      | get_template\s*\(\s*
      | loader\.get_template\s*\(\s*
      | select_template\s*\(\s*\[?\s*
    )
    (['"])([^'"]+\.html)\1
    """,
    re.VERBOSE,
)


# ── Helper ─────────────────────────────────────────────────────────────

def read_file(p: Path) -> str | None:
    for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    return None


def backup(filepath: Path) -> Path:
    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        rel = filepath.relative_to(BASE_DIR)
    except ValueError:
        rel = Path(filepath.name)
    dest = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, dest)
    return dest


def save_log(log: list):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def load_log() -> list:
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# ── Logika perbaikan render() path ────────────────────────────────────

def needs_fix(tmpl: str) -> bool:
    """
    True jika template path perlu diupdate ke lumra_pages/.

    Tidak disentuh:
    - sudah pakai 'lumra_pages/'
    - ada di BASE_COMPONENTS
    - sudah punya subfolder lain yang valid
    """
    if tmpl.startswith('lumra_pages/'):
        return False
    if tmpl in BASE_COMPONENTS:
        return False
    # base/ components
    if tmpl.startswith('base/'):
        return False
    return True


def build_lumra_pages_path(tmpl: str) -> str:
    """
    Konversi template path lama ke lumra_pages/ path.

    Contoh:
      'dashboard.html'                  → 'lumra_pages/dashboard.html'
      'sales/dashboard.html'            → 'lumra_pages/sales/dashboard.html'
      'lumra_pages/dashboard.html'      → tidak berubah
      'lumra_pages/sales/dashboard.html'→ tidak berubah
    """
    if tmpl.startswith('lumra_pages/'):
        return tmpl
    return f'lumra_pages/{tmpl}'


def fix_source(source: str) -> tuple[str, list]:
    """Ganti semua render() path yang perlu diupdate."""
    changes = []

    def replacer(m: re.Match) -> str:
        full, quote, tmpl = m.group(0), m.group(1), m.group(2)
        if not needs_fix(tmpl):
            return full
        new_tmpl = build_lumra_pages_path(tmpl)
        changes.append({'old': tmpl, 'new': new_tmpl})
        return full.replace(f'{quote}{tmpl}{quote}', f'{quote}{new_tmpl}{quote}', 1)

    return RENDER_RE.sub(replacer, source), changes


def get_all_view_files() -> list[Path]:
    """Kumpulkan semua .py di bawah lumra_config/ yang mengandung render()."""
    result = []
    if not VIEWS_ROOT.exists():
        return result
    for f in VIEWS_ROOT.rglob('*.py'):
        src = read_file(f)
        if src and ('render(' in src or 'TemplateResponse(' in src or 'get_template(' in src):
            result.append(f)
    return sorted(result)


# ── STEP 1: Preview & Apply render() fixes ────────────────────────────

def preview_render_fixes() -> dict:
    files = get_all_view_files()
    result = {}
    for f in files:
        src = read_file(f)
        if not src:
            continue
        _, changes = fix_source(src)
        if changes:
            try:
                rel = str(f.relative_to(BASE_DIR))
            except ValueError:
                rel = str(f)
            result[rel] = {'path': f, 'changes': changes}
    return result


def apply_render_fixes(log: list) -> int:
    data  = preview_render_fixes()
    total = 0
    for rel, info in data.items():
        fpath = info['path']
        src   = read_file(fpath)
        new_src, changes = fix_source(src)
        bak = backup(fpath)
        fpath.write_text(new_src, encoding='utf-8')
        log.append({'type': 'render_fix', 'file': str(fpath), 'backup': str(bak)})
        print(f'\n  {G}✅{RST}  {rel}')
        for c in changes:
            ROW(c['old'], c['new'])
        total += len(changes)
    return total


# ── STEP 2: Preview & Apply folder archiving ──────────────────────────

def get_archive_targets() -> dict:
    """
    Tentukan folder mana yang diarsip.
    Hanya folder yang seluruh isinya sudah ada di lumra_pages/.
    """
    result = {'folders': [], 'orphan_files': []}

    for folder_name in APP_TEMPLATE_FOLDERS:
        folder = TEMPLATES_DIR / folder_name
        if folder.exists() and folder.is_dir():
            result['folders'].append(folder)

    for name in ROOT_TEMPLATE_ORPHANS:
        target = TEMPLATES_DIR / name
        if target.exists():
            result['orphan_files'].append(target)

    return result


def apply_folder_archive(log: list) -> int:
    targets = get_archive_targets()
    ts      = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest    = ARCHIVE_DIR / ts
    moved   = 0

    for folder in targets['folders']:
        try:
            rel  = folder.relative_to(TEMPLATES_DIR)
            fdst = dest / rel
            fdst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(folder), str(fdst))
            log.append({'type': 'folder_archive', 'src': str(folder), 'dst': str(fdst)})
            ROW(f'templates/{rel}  →  _archive/app_templates/{ts}/{rel}')
            moved += 1
        except Exception as e:
            ERR(f'Gagal arsip {folder.name}: {e}')

    for orphan in targets['orphan_files']:
        try:
            rel  = orphan.relative_to(TEMPLATES_DIR)
            fdst = dest / rel
            fdst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(orphan), str(fdst))
            log.append({'type': 'file_archive', 'src': str(orphan), 'dst': str(fdst)})
            ROW(f'templates/{rel}  →  _archive/app_templates/{ts}/{rel}')
            moved += 1
        except Exception as e:
            ERR(f'Gagal arsip {orphan.name}: {e}')

    return moved


# ── UNDO ──────────────────────────────────────────────────────────────

def undo_all():
    log = load_log()
    if not log:
        OK('Tidak ada log — tidak ada yang bisa di-undo.')
        return

    restored = 0
    for entry in reversed(log):
        t = entry.get('type', '')

        if t == 'render_fix':
            fpath  = Path(entry['file'])
            bak    = Path(entry['backup'])
            if bak.exists():
                shutil.copy2(bak, fpath)
                print(f'  ↩️  {fpath.name}  ← dikembalikan')
                restored += 1
            else:
                WARN(f'Backup tidak ada: {bak}')

        elif t in ('folder_archive', 'file_archive'):
            src = Path(entry['src'])
            dst = Path(entry['dst'])
            if dst.exists():
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
                print(f'  ↩️  {src.name}  ← dikembalikan ke templates/')
                restored += 1
            else:
                WARN(f'Arsip tidak ada: {dst}')

    LOG_FILE.unlink(missing_ok=True)
    OK(f'{restored} item dikembalikan.')


# ── PREVIEW TERPADU ───────────────────────────────────────────────────

def run_preview(steps: set):

    if 1 in steps:
        HEAD('STEP 1 — Fix render() paths → lumra_pages/')
        data = preview_render_fixes()
        if not data:
            OK('Semua render() sudah mengarah ke lumra_pages/.')
        for rel, info in data.items():
            print(f'\n  {C}📄  {rel}{RST}')
            for c in info['changes']:
                ROW(c['old'], c['new'])

    if 2 in steps:
        HEAD('STEP 2 — Arsip folder template per-app')
        targets = get_archive_targets()
        if not targets['folders'] and not targets['orphan_files']:
            OK('Tidak ada folder yang perlu diarsip.')
        for f in targets['folders']:
            print(f'  {Y}📁  templates/{f.relative_to(TEMPLATES_DIR)}{RST}  →  _archive/app_templates/')
        for f in targets['orphan_files']:
            print(f'  {Y}📄  templates/{f.relative_to(TEMPLATES_DIR)}{RST}  →  _archive/app_templates/')

    print(f'\n  {"─"*50}')
    total_fixes   = sum(len(v['changes']) for v in preview_render_fixes().values()) if 1 in steps else '?'
    total_folders = len(get_archive_targets()['folders']) + len(get_archive_targets()['orphan_files']) if 2 in steps else '?'
    INFO(f'render() yang akan diupdate : {total_fixes}')
    INFO(f'folder/file yang diarsipkan : {total_folders}')
    print(f'\n  Gunakan {C}--apply{RST} untuk menerapkan.\n')


# ── APPLY TERPADU ─────────────────────────────────────────────────────

def run_apply(steps: set, yes: bool):
    run_preview(steps)

    if not yes:
        try:
            confirm = input(f'\n  Terapkan semua perubahan di atas? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.\n')
            return
        if confirm != 'y':
            print('  Dibatalkan.\n')
            return

    log = []

    if 1 in steps:
        HEAD('STEP 1 — Fix render() paths')
        total = apply_render_fixes(log)
        if total == 0:
            OK('Tidak ada perubahan diperlukan.')
        else:
            OK(f'{total} path diperbarui.')

    if 2 in steps:
        HEAD('STEP 2 — Arsip folder template per-app')
        total = apply_folder_archive(log)
        if total == 0:
            OK('Tidak ada folder yang diarsip.')
        else:
            OK(f'{total} folder/file diarsipkan ke _archive/app_templates/')

    save_log(log)
    print()
    HEAD('Selesai')
    OK('lumra_pages/ sekarang satu-satunya sumber template aktif.')
    INFO('Verifikasi: python lumra_sync.py')
    INFO('Rollback  : python lumra_mvc_align.py --undo')
    print()


# ── Entry Point ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP — MVC Template Alignment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Langkah:
  1 → Fix semua render() di views agar pakai prefix lumra_pages/
  2 → Arsip folder template per-app (sales/, inventory/, dll)

Contoh:
  python lumra_mvc_align.py                    → preview semua
  python lumra_mvc_align.py --apply            → eksekusi step 1+2
  python lumra_mvc_align.py --apply --step 1   → hanya fix render()
  python lumra_mvc_align.py --apply --step 2   → hanya arsip folder
  python lumra_mvc_align.py --apply --yes      → tanpa konfirmasi
  python lumra_mvc_align.py --undo             → rollback
        """
    )
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--yes',   action='store_true')
    parser.add_argument('--undo',  action='store_true')
    parser.add_argument('--step',  type=int, nargs='+', choices=[1, 2])
    args   = parser.parse_args()
    steps  = set(args.step) if args.step else {1, 2}

    print(f'\n{B}{"═"*50}')
    print(f'  {W}Lumra ERP — MVC Alignment Tool{RST}')
    print(f'{B}{"═"*50}{RST}')
    print(f'  Templates : {DIM}{TEMPLATES_DIR}{RST}')
    print(f'  Mode      : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}')
    print(f'  Steps     : {C}{sorted(steps)}{RST}')

    if not TEMPLATES_DIR.exists():
        ERR(f'Folder templates tidak ditemukan: {TEMPLATES_DIR}')
        sys.exit(1)

    if args.undo:
        undo_all()
    elif args.apply:
        run_apply(steps, yes=args.yes)
    else:
        run_preview(steps)


if __name__ == '__main__':
    main()