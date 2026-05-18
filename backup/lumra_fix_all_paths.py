"""
lumra_fix_all_paths.py — Lumra ERP · Final Path Fixer
======================================================
Memperbaiki SEMUA render() path di views berdasarkan lokasi file
aktual di disk. Ground truth = struktur lumra_pages/ yang ada sekarang.

Yang diperbaiki:
  'dashboard.html'                → 'lumra_pages/sales/dashboard.html'
  'lumra_pages/dashboard.html'    → 'lumra_pages/sales/dashboard.html'
  'sales/dashboard.html'          → 'lumra_pages/sales/dashboard.html'
  'lumra_pages/sales/dashboard.html' → tidak disentuh (sudah benar)

Cara pakai:
  python lumra_fix_all_paths.py              → preview
  python lumra_fix_all_paths.py --apply      → eksekusi
  python lumra_fix_all_paths.py --apply --yes → tanpa konfirmasi
  python lumra_fix_all_paths.py --undo       → rollback
"""

import re, sys, json, shutil, argparse
from pathlib import Path
from datetime import datetime

# ── Warna ──────────────────────────────────────────────────────────────
G='\033[92m'; Y='\033[93m'; R='\033[91m'
B='\033[94m'; C='\033[96m'; DIM='\033[2m'; W='\033[97m'; RST='\033[0m'

def OK(m):   print(f'  {G}✅  {m}{RST}')
def WARN(m): print(f'  {Y}⚠️   {m}{RST}')
def INFO(m): print(f'  {C}ℹ️   {m}{RST}')
def HEAD(m): print(f'\n{B}{"═"*12} {W}{m}{RST}{B} {"═"*12}{RST}')
def ERR(m):  print(f'  {R}❌  {m}{RST}')

# ── Path ───────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
LUMRA_PAGES = BASE_DIR / 'lumra_config' / 'templates' / 'lumra_pages'
VIEWS_ROOT  = BASE_DIR / 'lumra_config'
BACKUP_DIR  = BASE_DIR / '.lumra_fix_all_backup'
LOG_FILE    = BASE_DIR / '.lumra_fix_all_log.json'

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

# ── Build ground truth dari disk ───────────────────────────────────────

def build_truth_map() -> dict[str, str]:
    """
    Scan lumra_pages/ di disk → buat mapping:
      filename.html → lumra_pages/subfolder/filename.html

    Jika ada nama file yang sama di 2 subfolder berbeda,
    keduanya dicatat dengan key = subfolder/filename untuk
    menghindari ambiguitas.
    """
    truth = {}          # key: basename  → value: correct full path
    ambiguous = {}      # key: basename  → list of paths (ada duplikat)

    if not LUMRA_PAGES.exists():
        return truth

    for f in LUMRA_PAGES.rglob('*.html'):
        try:
            rel = str(f.relative_to(LUMRA_PAGES.parent)).replace('\\', '/')
        except ValueError:
            continue

        basename = f.name

        if basename in truth:
            # Sudah ada → tandai ambiguous
            if basename not in ambiguous:
                ambiguous[basename] = [truth[basename]]
            ambiguous[basename].append(rel)
        else:
            truth[basename] = rel

    # Hapus yang ambiguous dari truth (tidak bisa auto-resolve)
    for basename in ambiguous:
        truth.pop(basename, None)

    return truth, ambiguous


def normalize_path(tmpl: str) -> str:
    """
    Normalisasi path apapun ke basename.
    'lumra_pages/sales/dashboard.html' → 'dashboard.html'
    'sales/dashboard.html'             → 'dashboard.html'
    'dashboard.html'                   → 'dashboard.html'
    """
    return Path(tmpl.replace('\\', '/')).name


def is_already_correct(tmpl: str, truth: dict) -> bool:
    """True jika path sudah menunjuk ke lokasi yang benar."""
    clean = tmpl.replace('\\', '/')
    basename = Path(clean).name
    if basename not in truth:
        return False
    return clean == truth[basename]


def needs_fix(tmpl: str, truth: dict) -> tuple[bool, str | None]:
    """
    Kembalikan (perlu_fix, correct_path).
    Tidak disentuh jika:
    - sudah benar
    - ada di base/ (extends/include komponen)
    - tidak dikenali di truth map
    """
    clean    = tmpl.replace('\\', '/')
    basename = Path(clean).name

    # base/ components tidak disentuh
    if clean.startswith('base/') or basename in {
        'base.html', 'navbar.html', 'sidebar.html', 'footer.html',
        'alert.html', 'alert_inner.html', 'kpi_card.html',
        'kpi_card_inner.html', 'kpi_card_white.html',
        'sidebar_item.html', 'sidebar_right.html',
        'activity_drawer.html', 'approval_modal.html',
        'error_404.html', 'error_500.html',
    }:
        return False, None

    if basename not in truth:
        return False, None  # tidak dikenali → jangan ubah

    correct = truth[basename]
    if clean == correct:
        return False, None  # sudah benar

    return True, correct


# ── Fix source ─────────────────────────────────────────────────────────

def fix_source(source: str, truth: dict) -> tuple[str, list]:
    changes = []

    def replacer(m: re.Match) -> str:
        full  = m.group(0)
        quote = m.group(1)
        tmpl  = m.group(2)

        need, correct = needs_fix(tmpl, truth)
        if not need:
            return full

        changes.append({'old': tmpl, 'new': correct})
        return full.replace(f'{quote}{tmpl}{quote}', f'{quote}{correct}{quote}', 1)

    return RENDER_RE.sub(replacer, source), changes


# ── File ops ───────────────────────────────────────────────────────────

def get_view_files() -> list[Path]:
    if not VIEWS_ROOT.exists():
        return []
    result = []
    for f in VIEWS_ROOT.rglob('*.py'):
        try:
            src = f.read_text(encoding='utf-8', errors='ignore')
            if any(kw in src for kw in ['render(', 'TemplateResponse(', 'get_template(']):
                result.append(f)
        except Exception:
            pass
    return sorted(result)


def backup_file(f: Path) -> Path:
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        rel = f.relative_to(BASE_DIR)
    except ValueError:
        rel = Path(f.name)
    dest = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dest)
    return dest


def read_file(f: Path) -> str | None:
    for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
        try:
            return f.read_text(encoding=enc)
        except Exception:
            continue
    return None


# ── Preview ────────────────────────────────────────────────────────────

def run_preview(truth: dict, ambiguous: dict) -> dict:
    files = get_view_files()
    result = {}

    for f in files:
        src = read_file(f)
        if not src:
            continue
        _, changes = fix_source(src, truth)
        if changes:
            try:
                rel = str(f.relative_to(BASE_DIR))
            except ValueError:
                rel = str(f)
            result[rel] = {'path': f, 'changes': changes}

    HEAD('Ground Truth — lokasi file aktual di disk')
    INFO(f'{len(truth)} file terindeks dari lumra_pages/')
    if ambiguous:
        WARN(f'{len(ambiguous)} nama file ambigu (ada di 2+ subfolder) — tidak akan diubah:')
        for name, paths in ambiguous.items():
            print(f'  {Y}  {name}:{RST}')
            for p in paths:
                print(f'  {DIM}    → {p}{RST}')

    HEAD('Perubahan render() yang akan dilakukan')
    if not result:
        OK('Semua render() sudah menggunakan path yang benar.')
    else:
        for rel, info in result.items():
            print(f'\n  {C}📄  {rel}{RST}')
            for c in info['changes']:
                print(f'  {DIM}  {c["old"]}{RST}')
                print(f'  {G}  → {c["new"]}{RST}')

    total = sum(len(v['changes']) for v in result.values())
    print(f'\n  {"─"*55}')
    print(f'  {G}render() yang diupdate : {total}{RST}')
    print(f'  {C}File terdampak         : {len(result)}{RST}')
    if ambiguous:
        print(f'  {Y}Ambigu (skip)          : {len(ambiguous)}{RST}')
    print()

    return result


# ── Apply ──────────────────────────────────────────────────────────────

def run_apply(truth: dict, ambiguous: dict, yes: bool):
    preview_data = run_preview(truth, ambiguous)

    if not preview_data:
        OK('Tidak ada yang perlu diperbaiki.')
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

    log   = []
    total = 0

    HEAD('Menerapkan perubahan')
    for rel, info in preview_data.items():
        fpath = info['path']
        src   = read_file(fpath)
        new_src, changes = fix_source(src, truth)
        bak = backup_file(fpath)
        fpath.write_text(new_src, encoding='utf-8')
        log.append({'file': str(fpath), 'backup': str(bak)})
        print(f'\n  {G}✅{RST}  {rel}')
        for c in changes:
            print(f'  {DIM}  {c["old"]}{RST}  →  {G}{c["new"]}{RST}')
        total += len(changes)

    # Simpan log
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    print()
    HEAD('Selesai')
    OK(f'{total} render() path diperbaiki.')
    INFO('Verifikasi: python manage.py check')
    INFO('Rollback  : python lumra_fix_all_paths.py --undo')
    print()


# ── Undo ───────────────────────────────────────────────────────────────

def run_undo():
    if not LOG_FILE.exists():
        OK('Tidak ada log.')
        return
    with open(LOG_FILE) as f:
        log = json.load(f)
    restored = 0
    for entry in log:
        fpath = Path(entry['file'])
        bak   = Path(entry['backup'])
        if bak.exists():
            shutil.copy2(bak, fpath)
            print(f'  ↩️  {fpath.name}')
            restored += 1
        else:
            WARN(f'Backup tidak ada: {bak}')
    LOG_FILE.unlink(missing_ok=True)
    OK(f'{restored} file dikembalikan.')


# ── Main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP — Final Path Fixer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python lumra_fix_all_paths.py              → preview
  python lumra_fix_all_paths.py --apply      → eksekusi
  python lumra_fix_all_paths.py --apply --yes → tanpa konfirmasi
  python lumra_fix_all_paths.py --undo       → rollback
        """
    )
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--yes',   action='store_true')
    parser.add_argument('--undo',  action='store_true')
    args = parser.parse_args()

    print(f'\n{B}{"═"*55}')
    print(f'  {W}Lumra ERP — Final Path Fixer{RST}')
    print(f'{B}{"═"*55}{RST}')
    print(f'  lumra_pages/ : {DIM}{LUMRA_PAGES}{RST}')
    print(f'  Mode         : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}')

    if not LUMRA_PAGES.exists():
        ERR(f'lumra_pages/ tidak ditemukan: {LUMRA_PAGES}')
        sys.exit(1)

    if args.undo:
        run_undo()
        return

    truth, ambiguous = build_truth_map()

    if not truth:
        ERR('Tidak ada file HTML ditemukan di lumra_pages/')
        sys.exit(1)

    if args.apply:
        run_apply(truth, ambiguous, yes=args.yes)
    else:
        run_preview(truth, ambiguous)
        WARN('Ini PREVIEW — gunakan --apply untuk menerapkan.')
        print()


if __name__ == '__main__':
    main()