"""
lumra_rename.py
===============
Rename file template secara konsisten + otomatis update semua referensi:
  - render() / TemplateResponse() di views.py
  - {% include %} dan {% extends %} di semua .html

Rename map sudah dikonfirmasi — tidak ada auto-detect.

Cara pakai:
  python lumra_rename.py              → preview (AMAN, tidak ada yang diubah)
  python lumra_rename.py --apply      → eksekusi dengan konfirmasi
  python lumra_rename.py --apply --yes→ eksekusi tanpa konfirmasi
  python lumra_rename.py --undo       → rollback dari backup
  python lumra_rename.py --source D:/APPS/Project/lumra  → override root
"""

import re, sys, shutil, json, argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

BASE       = Path(__file__).resolve().parent
BACKUP_DIR = BASE / '.lumra_rename_backup'
LOG_FILE   = BASE / '.lumra_rename_log.json'

G  = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B  = '\033[94m'; C = '\033[96m'; W = '\033[97m'
DIM= '\033[2m';  RST= '\033[0m'

# ─────────────────────────────────────────────────────────────────────────────
# RENAME MAP — dikonfirmasi manual
# Format: 'subfolder/nama_lama.html' → 'subfolder/nama_baru.html'
# Subfolder relatif terhadap lumra_pages/
# ─────────────────────────────────────────────────────────────────────────────

RENAME_MAP: dict[str, str] = {
    # master_data
    'master_data/customer.html'             : 'master_data/customer_form.html',
    'master_data/vendors_list.html'         : 'master_data/vendor_list.html',
    'master_data/locations.html'            : 'master_data/location_list.html',

    # inventory
    'inventory/products.html'               : 'inventory/product_list.html',
    'inventory/inventory.html'              : 'inventory/stock_overview.html',
    'inventory/add_stock_movement.html'     : 'inventory/stock_movement_form.html',

    # reports
    'reports/activity_log.html'             : 'reports/report_activity_log.html',

    # sales
    'sales/sales_insight.html'              : 'sales/sales_intelligence.html',

    # settings
    'settings/users.html'                   : 'settings/user_list.html',
    'settings/business_form_general.html'   : 'settings/business_profile.html',
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

def find_lumra_pages(root: Path) -> Path | None:
    """Cari folder lumra_pages/ di dalam project root."""
    candidates = [
        root / 'lumra_config' / 'templates' / 'lumra_pages',
        root / 'templates' / 'lumra_pages',
    ]
    for c in candidates:
        if c.exists():
            return c
    # fallback: cari di seluruh project
    for p in root.rglob('lumra_pages'):
        if p.is_dir():
            return p
    return None


def find_views_files(root: Path) -> list[Path]:
    """Kumpulkan semua views.py di lumra_config/."""
    lc = root / 'lumra_config'
    if not lc.exists():
        return []
    return sorted(lc.rglob('views.py'))


def find_html_files(lumra_pages: Path) -> list[Path]:
    """Semua .html di dalam lumra_pages/ dan base/."""
    files = list(lumra_pages.rglob('*.html'))
    # Tambahkan base/ jika ada
    base_dir = lumra_pages.parent / 'base'
    if base_dir.exists():
        files.extend(base_dir.rglob('*.html'))
    return files


def read_file(p: Path) -> str | None:
    for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    return None


def backup_file(filepath: Path) -> Path:
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        rel  = filepath.relative_to(BASE)
    except ValueError:
        rel  = Path(filepath.name)
    dest = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, dest)
    return dest


def sep(title: str = ''):
    pad  = (62 - len(title) - 2) // 2 if title else 0
    line = '═' * 62
    if title:
        print(f'\n{B}{"═"*pad} {W}{title}{RST}{B} {"═"*(62-pad-len(title)-2)}{RST}')
    else:
        print(f'{DIM}{line}{RST}')


# ─────────────────────────────────────────────────────────────────────────────
# CORE: BUILD FULL PATH MAP
# ─────────────────────────────────────────────────────────────────────────────

def build_path_map(lumra_pages: Path) -> dict[str, str]:
    """
    Dari RENAME_MAP, buat peta:
      old_full_path (relatif ke lumra_pages)  →  new_full_path
    Contoh:
      'master_data/customer.html'  →  'master_data/customer_form.html'

    Juga buat peta terbalik untuk mendeteksi referensi di views/html:
      old_template_string  →  new_template_string
    dengan semua kemungkinan prefix (lumra_pages/, tanpa prefix, dll).
    """
    return RENAME_MAP.copy()


def build_reference_map(rename_map: dict[str, str]) -> list[tuple[str, str]]:
    """
    Buat semua kemungkinan string referensi yang perlu diganti.
    Satu file bisa direferensikan dengan berbagai cara di views/html:
      - 'lumra_pages/master_data/customer.html'
      - 'master_data/customer.html'          (jarang, tapi mungkin)
    """
    refs = []
    for old_rel, new_rel in rename_map.items():
        # Dengan prefix lumra_pages/ (paling umum)
        refs.append((f'lumra_pages/{old_rel}', f'lumra_pages/{new_rel}'))
        # Tanpa prefix (jika ada yang langsung pakai subfolder)
        refs.append((old_rel, new_rel))
    return refs


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Rencana rename file fisik
# ─────────────────────────────────────────────────────────────────────────────

def plan_file_renames(lumra_pages: Path) -> list[dict]:
    renames = []
    for old_rel, new_rel in RENAME_MAP.items():
        src = lumra_pages / old_rel
        dst = lumra_pages / new_rel

        if not src.exists():
            renames.append({
                'src'    : src,
                'dst'    : dst,
                'old_rel': old_rel,
                'new_rel': new_rel,
                'status' : 'not_found',  # file tidak ada di disk
            })
            continue

        if dst.exists():
            renames.append({
                'src'    : src,
                'dst'    : dst,
                'old_rel': old_rel,
                'new_rel': new_rel,
                'status' : 'conflict',   # nama baru sudah ada
            })
            continue

        renames.append({
            'src'    : src,
            'dst'    : dst,
            'old_rel': old_rel,
            'new_rel': new_rel,
            'status' : 'ok',             # siap direname
        })
    return renames


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Rencana fix referensi di views.py
# ─────────────────────────────────────────────────────────────────────────────

RENDER_RE = re.compile(
    r"""(render\s*\(\s*\w+\s*,\s*"""
    r"""|TemplateResponse\s*\(\s*\w+\s*,\s*"""
    r"""|get_template\s*\("""
    r"""|loader\.get_template\s*\()"""
    r"""(['"])([^'"]+\.html)\2""",
    re.VERBOSE,
)


def plan_views_fixes(root: Path, ref_map: list[tuple[str, str]]) -> list[dict]:
    files   = find_views_files(root)
    results = []

    for py in files:
        src = read_file(py)
        if not src:
            continue

        file_changes = []
        for old_ref, new_ref in ref_map:
            # Cari dalam konteks render/TemplateResponse/get_template
            for m in RENDER_RE.finditer(src):
                tmpl = m.group(3)
                if tmpl == old_ref:
                    file_changes.append({'old': old_ref, 'new': new_ref})

        if file_changes:
            try:
                rel = py.relative_to(root)
            except ValueError:
                rel = py
            results.append({
                'file'   : py,
                'rel'    : str(rel),
                'changes': file_changes,
            })

    return results


def apply_views_fix(py: Path, changes: list[dict]) -> str:
    src = read_file(py)
    for c in changes:
        # Ganti dengan single quote
        src = src.replace(f"'{c['old']}'", f"'{c['new']}'")
        # Ganti dengan double quote
        src = src.replace(f'"{c["old"]}"', f'"{c["new"]}"')
    return src


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Rencana fix {% include %} dan {% extends %} di HTML
# ─────────────────────────────────────────────────────────────────────────────

INCLUDE_RE = re.compile(
    r"""({%-?\s*(?:include|extends)\s+)(['"])([^'"]+\.html)\2""",
    re.IGNORECASE,
)


def plan_html_fixes(lumra_pages: Path, ref_map: list[tuple[str, str]]) -> list[dict]:
    html_files = find_html_files(lumra_pages)
    results    = []

    for html in html_files:
        src = read_file(html)
        if not src:
            continue

        file_changes = []
        for m in INCLUDE_RE.finditer(src):
            tmpl = m.group(3)
            for old_ref, new_ref in ref_map:
                if tmpl == old_ref:
                    file_changes.append({'old': old_ref, 'new': new_ref})

        if file_changes:
            try:
                rel = html.relative_to(lumra_pages.parent)
            except ValueError:
                rel = html
            results.append({
                'file'   : html,
                'rel'    : str(rel),
                'changes': file_changes,
            })

    return results


def apply_html_fix(html: Path, changes: list[dict]) -> str:
    src = read_file(html)
    for c in changes:
        src = src.replace(f"'{c['old']}'", f"'{c['new']}'")
        src = src.replace(f'"{c["old"]}"', f'"{c["new"]}"')
    return src


# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW
# ─────────────────────────────────────────────────────────────────────────────

def run_preview(root: Path) -> tuple:
    lumra_pages = find_lumra_pages(root)
    if not lumra_pages:
        print(f'  {R}❌  lumra_pages/ tidak ditemukan di {root}{RST}')
        sys.exit(1)

    rename_map  = build_path_map(lumra_pages)
    ref_map     = build_reference_map(rename_map)
    file_renames= plan_file_renames(lumra_pages)
    views_fixes = plan_views_fixes(root, ref_map)
    html_fixes  = plan_html_fixes(lumra_pages, ref_map)

    # ── File renames ────────────────────────────────────────────────────────
    sep('STEP 1 — Rename File Template')
    ok_renames = [r for r in file_renames if r['status'] == 'ok']
    nf_renames = [r for r in file_renames if r['status'] == 'not_found']
    cf_renames = [r for r in file_renames if r['status'] == 'conflict']

    if ok_renames:
        for r in ok_renames:
            old_name = Path(r['old_rel']).name
            new_name = Path(r['new_rel']).name
            folder   = Path(r['old_rel']).parent
            print(f'  {DIM}{folder}/{RST}{Y}{old_name}{RST}')
            print(f'  {DIM}{folder}/{RST}{G}{new_name}{RST}\n')
    else:
        print(f'  {G}✅  Semua file sudah menggunakan nama yang benar.{RST}')

    if nf_renames:
        print(f'  {DIM}── Tidak ditemukan di disk (mungkin sudah direname):{RST}')
        for r in nf_renames:
            print(f'  {DIM}  {r["old_rel"]}{RST}')

    if cf_renames:
        print(f'  {Y}⚠️   Konflik — nama baru sudah ada:{RST}')
        for r in cf_renames:
            print(f'  {Y}  {r["old_rel"]} → {r["new_rel"]} (SKIP){RST}')

    # ── Views fixes ─────────────────────────────────────────────────────────
    sep('STEP 2 — Update render() di views.py')
    if views_fixes:
        for vf in views_fixes:
            print(f'  {C}📄  {vf["rel"]}{RST}')
            for c in vf['changes']:
                print(f'    {DIM}{c["old"]}{RST}')
                print(f'    {G}→ {c["new"]}{RST}')
            print()
    else:
        print(f'  {G}✅  Tidak ada render() yang perlu diupdate.{RST}')

    # ── HTML fixes ──────────────────────────────────────────────────────────
    sep('STEP 3 — Update {%% include/extends %%} di HTML')
    if html_fixes:
        for hf in html_fixes:
            print(f'  {C}🌐  {hf["rel"]}{RST}')
            for c in hf['changes']:
                print(f'    {DIM}{c["old"]}{RST}')
                print(f'    {G}→ {c["new"]}{RST}')
            print()
    else:
        print(f'  {G}✅  Tidak ada include/extends yang perlu diupdate.{RST}')

    # ── Summary ─────────────────────────────────────────────────────────────
    sep()
    total_views = sum(len(v['changes']) for v in views_fixes)
    total_html  = sum(len(h['changes']) for h in html_fixes)
    print(f'  File direname         : {G}{len(ok_renames)}{RST}')
    print(f'  render() diupdate     : {G}{total_views}{RST}')
    print(f'  include/extends diupdate: {G}{total_html}{RST}')
    if nf_renames:
        print(f'  Tidak ditemukan (skip): {DIM}{len(nf_renames)}{RST}')
    if cf_renames:
        print(f'  Konflik (skip)        : {Y}{len(cf_renames)}{RST}')
    print()

    return lumra_pages, file_renames, views_fixes, html_fixes, ref_map


# ─────────────────────────────────────────────────────────────────────────────
# APPLY
# ─────────────────────────────────────────────────────────────────────────────

def run_apply(root: Path, yes: bool = False):
    lumra_pages, file_renames, views_fixes, html_fixes, _ = run_preview(root)

    ok_renames = [r for r in file_renames if r['status'] == 'ok']
    if not ok_renames and not views_fixes and not html_fixes:
        print(f'  {G}✅  Tidak ada yang perlu dilakukan.{RST}\n')
        return

    if not yes:
        try:
            confirm = input('  Terapkan semua perubahan di atas? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.')
            return
        if confirm != 'y':
            print('  Dibatalkan.')
            return

    log = {'file_renames': [], 'views_fixes': [], 'html_fixes': []}

    # ── Step 1: Rename file ──────────────────────────────────────────────────
    sep('STEP 1 — Rename File')
    for r in ok_renames:
        bak = backup_file(r['src'])
        r['dst'].parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(r['src']), str(r['dst']))
        log['file_renames'].append({
            'src': str(r['src']),
            'dst': str(r['dst']),
            'bak': str(bak),
        })
        old_name = Path(r['old_rel']).name
        new_name = Path(r['new_rel']).name
        print(f'  {G}✅{RST}  {Y}{old_name}{RST}  →  {G}{new_name}{RST}')

    if not ok_renames:
        print(f'  {G}✅  Tidak ada file yang perlu direname.{RST}')

    # ── Step 2: Fix views ────────────────────────────────────────────────────
    sep('STEP 2 — Fix render() di views.py')
    for vf in views_fixes:
        bak     = backup_file(vf['file'])
        new_src = apply_views_fix(vf['file'], vf['changes'])
        vf['file'].write_text(new_src, encoding='utf-8')
        log['views_fixes'].append({
            'file'   : str(vf['file']),
            'bak'    : str(bak),
            'changes': vf['changes'],
        })
        print(f'  {G}✅{RST}  {vf["rel"]}')
        for c in vf['changes']:
            print(f'    {DIM}{c["old"]}{RST}  →  {G}{c["new"]}{RST}')

    if not views_fixes:
        print(f'  {G}✅  Tidak ada yang diubah.{RST}')

    # ── Step 3: Fix HTML ─────────────────────────────────────────────────────
    sep('STEP 3 — Fix include/extends di HTML')
    for hf in html_fixes:
        bak     = backup_file(hf['file'])
        new_src = apply_html_fix(hf['file'], hf['changes'])
        hf['file'].write_text(new_src, encoding='utf-8')
        log['html_fixes'].append({
            'file'   : str(hf['file']),
            'bak'    : str(bak),
            'changes': hf['changes'],
        })
        print(f'  {G}✅{RST}  {hf["rel"]}')
        for c in hf['changes']:
            print(f'    {DIM}{c["old"]}{RST}  →  {G}{c["new"]}{RST}')

    if not html_fixes:
        print(f'  {G}✅  Tidak ada yang diubah.{RST}')

    # ── Simpan log ───────────────────────────────────────────────────────────
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    sep()
    total_renamed = len(ok_renames)
    total_views   = sum(len(v['changes']) for v in views_fixes)
    total_html    = sum(len(h['changes']) for h in html_fixes)
    print(f'  {G}✅  Selesai!{RST}')
    print(f'     {total_renamed} file direname')
    print(f'     {total_views} render() diupdate')
    print(f'     {total_html} include/extends diupdate')
    print(f'  {DIM}Backup : {BACKUP_DIR}{RST}')
    print(f'  {DIM}Rollback: python lumra_rename.py --undo{RST}')
    print(f'\n  {C}Verifikasi: python manage.py check{RST}\n')


# ─────────────────────────────────────────────────────────────────────────────
# UNDO
# ─────────────────────────────────────────────────────────────────────────────

def run_undo():
    if not LOG_FILE.exists():
        print(f'  {Y}⚠️   Log tidak ditemukan — tidak ada yang bisa di-rollback.{RST}\n')
        return

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log = json.load(f)

    sep('UNDO — Rollback File Rename')
    for entry in reversed(log.get('file_renames', [])):
        dst = Path(entry['dst'])
        src = Path(entry['src'])
        bak = Path(entry['bak'])
        if bak.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bak, src)
            if dst.exists():
                dst.unlink()
            print(f'  {G}↩️{RST}  {dst.name}  →  {src.name}')
        else:
            print(f'  {Y}⚠️   Backup tidak ada: {bak}{RST}')

    sep('UNDO — Rollback views.py')
    for entry in log.get('views_fixes', []):
        orig = Path(entry['file'])
        bak  = Path(entry['bak'])
        if bak.exists():
            shutil.copy2(bak, orig)
            print(f'  {G}↩️{RST}  {orig.name}')

    sep('UNDO — Rollback HTML')
    for entry in log.get('html_fixes', []):
        orig = Path(entry['file'])
        bak  = Path(entry['bak'])
        if bak.exists():
            shutil.copy2(bak, orig)
            print(f'  {G}↩️{RST}  {orig.name}')

    LOG_FILE.unlink(missing_ok=True)
    sep()
    print(f'  {G}✅  Rollback selesai.{RST}\n')


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP — Template Renamer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Yang dilakukan:
  1. Rename 10 file template sesuai konvensi [object]_[action].html
  2. Update semua render() / TemplateResponse() di views.py
  3. Update semua {% include %} dan {% extends %} di semua .html

Contoh:
  python lumra_rename.py                       → preview (aman)
  python lumra_rename.py --apply               → terapkan
  python lumra_rename.py --apply --yes         → terapkan tanpa konfirmasi
  python lumra_rename.py --undo                → rollback
  python lumra_rename.py --source D:/Project  → override root project
        """
    )
    parser.add_argument('--apply',  action='store_true', help='Terapkan perubahan')
    parser.add_argument('--yes',    action='store_true', help='Skip konfirmasi')
    parser.add_argument('--undo',   action='store_true', help='Rollback dari backup')
    parser.add_argument('--source', type=str, default=None,
                        help='Path root project (default: folder script ini)')
    args = parser.parse_args()

    root = Path(args.source).resolve() if args.source else BASE

    print(f'\n{B}{"═"*62}')
    print(f'  {W}Lumra ERP — Template Renamer{RST}')
    print(f'{B}{"═"*62}{RST}')
    print(f'  Root : {DIM}{root}{RST}')
    print(f'  Mode : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}\n')

    if args.undo:
        run_undo()
    elif args.apply:
        run_apply(root, yes=args.yes)
    else:
        run_preview(root)
        print(f'  {Y}⚠️   Ini PREVIEW — gunakan --apply untuk menerapkan.{RST}\n')


if __name__ == '__main__':
    main()