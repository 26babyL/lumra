"""
lumra_fix_master.py
===================
Script master — scan dan perbaiki semua referensi yang salah dalam satu perintah.
Bisa dijalankan berulang kapanpun muncul error baru. Aman dijalankan berkali-kali
(idempoten — yang sudah benar tidak disentuh).

SUMBER KEBENARAN: file .html yang ada di disk.
Script scan semua template, lalu perbaiki referensi yang tidak cocok.
Tidak ada hardcode path — semuanya otomatis dari struktur folder aktual.

Yang diperbaiki:
  1. render() / TemplateResponse() path salah di views.py
  2. lazy_view() modul salah di urls.py
  3. {% include %} / {% extends %} path salah di .html
  4. Import hilang di urls.py (include, path, re_path)

Cara pakai:
  python lumra_fix_master.py                    -> preview (AMAN)
  python lumra_fix_master.py --apply            -> perbaiki semua
  python lumra_fix_master.py --apply --yes      -> tanpa konfirmasi
  python lumra_fix_master.py --undo             -> rollback
  python lumra_fix_master.py --step 1 3        -> hanya step tertentu
  python lumra_fix_master.py --source D:\\APPS\\Project\\lumra
"""

import re, sys, shutil, json, argparse
from pathlib import Path
from datetime import datetime

BASE       = Path(__file__).resolve().parent
BACKUP_DIR = BASE / '.lumra_master_backup'
LOG_FILE   = BASE / '.lumra_master_log.json'

G  = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B  = '\033[94m'; C = '\033[96m'; W = '\033[97m'
DIM= '\033[2m';  RST= '\033[0m'
OK = f'{G}checkmark{RST}'; WN = f'{Y}warn{RST}'; ER = f'{R}err{RST}'; FX = f'{C}fix{RST}'

def sep(title=''):
    pad = (64 - len(title) - 2) // 2 if title else 0
    if title:
        print(f'\n{B}{"="*pad} {W}{title}{RST}{B} {"="*(64-pad-len(title)-2)}{RST}')
    else:
        print(f'{DIM}{"="*64}{RST}')

FUNC_MODULE_ROUTING = [
    ('api_dashboard','api'),('submit_requisition','api'),('confirm_receipt','api'),
    ('submit_purchases','api'),('get_location_stock','api'),
    ('login','auth_app'),('logout','auth_app'),('register','auth_app'),
    ('supplier_price','inventory'),('stock_movement','inventory'),('stock_planning','inventory'),
    ('export_stock','inventory'),('import_product','inventory'),('products_import','inventory'),
    ('import_template','inventory'),('stock_allocation','inventory'),('approve_requisition','inventory'),
    ('dashboard','sales'),('pos','sales'),('notification','sales'),
    ('sales_history','sales'),('sales_performance','sales'),('sales_products','sales'),('purchasing','sales'),
    ('product','master_data'),('categor','master_data'),('unit_','master_data'),
    ('_unit','master_data'),('units_','master_data'),('vendor','master_data'),
    ('customer','master_data'),('location','master_data'),('stock_opname','master_data'),('opname','master_data'),
    ('campaign','marketing'),('discount','marketing'),('loyalty','marketing'),('promo','marketing'),
    ('financial_report','reports'),('market_insight','reports'),('trends_analysis','reports'),
    ('activity_log','reports'),('download_report','reports'),('sales_report','reports'),
    ('transaction_summary','reports'),('transfer_report','reports'),
    ('requisition_report','reports'),('purchasing_report','reports'),
    ('inventory_log','reports'),('inventory_low','reports'),('profit_loss','reports'),('sales_summary','reports'),
    ('recipe','production'),('bom','production'),
    ('profile','settings_app'),('settings','settings_app'),('system_status','settings_app'),
    ('business','settings_app'),('users','settings_app'),('about','settings_app'),
    ('contact','settings_app'),('pricing','settings_app'),('search','settings_app'),
    ('feature_matrix','settings_app'),('permissions','settings_app'),
]

LEGACY_MODULE_PATTERNS = [
    'lumra_config.views',
    'lumra_config.views.inventory_views',
    'lumra_config.views.stock_movement_views',
    'lumra_config.views.api_views',
]

DJANGO_URLS_NAMES = ['path', 'include', 're_path']

def read_file(p):
    for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    return None

def backup(p):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:    rel = p.relative_to(BASE)
    except: rel = Path(p.name)
    dest = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    return dest

def find_root(source):
    return Path(source).resolve() if source else BASE

def find_templates_dir(root):
    for c in [root / 'lumra_config' / 'templates', root / 'templates']:
        if c.exists():
            return c
    return None

def find_views_files(root):
    lc = root / 'lumra_config'
    return sorted(lc.rglob('views.py')) if lc.exists() else []

def find_html_files(root):
    tmpl = find_templates_dir(root)
    return list(tmpl.rglob('*.html')) if tmpl else []

def find_main_urls(root):
    for rel in ['lumra_system/urls.py', 'lumra/urls.py', 'config/urls.py', 'urls.py']:
        p = root / rel
        if p.exists():
            return p
    for p in root.rglob('urls.py'):
        if 'lumra_config' not in str(p):
            src = read_file(p)
            if src and 'urlpatterns' in src and 'admin' in src:
                return p
    return None

def build_disk_index(root):
    """
    Scan semua .html di templates/.
    Return: { 'dashboard.html': ['lumra_pages/sales/dashboard.html'], ... }
    Path relatif terhadap templates dir = path yang dipakai di render().
    """
    tmpl = find_templates_dir(root)
    if not tmpl:
        return {}
    index = {}
    for f in tmpl.rglob('*.html'):
        rel = str(f.relative_to(tmpl)).replace('\\', '/')
        index.setdefault(f.name, []).append(rel)
    return index

def resolve_template_path(current, disk_index):
    """
    Cari path yang benar berdasarkan disk index.
    Return (correct, reason) — correct=None berarti sudah benar atau tidak bisa ditentukan.
    """
    norm     = current.replace('\\', '/')
    basename = norm.split('/')[-1]
    hits     = disk_index.get(basename)

    if not hits:
        return None, None  # file tidak ada di disk, biarkan

    if len(hits) > 1:
        # Ambiguous: file ada di lebih dari satu lokasi
        return None, f'ambiguous: {", ".join(hits)}'

    correct = hits[0]
    if correct == norm:
        return None, None  # sudah benar

    return correct, f'{norm} -> {correct}'

# ── STEP 1: render() ──────────────────────────────────────────────────────────

RENDER_RE = re.compile(
    r'(render\s*\(\s*\w+\s*,\s*'
    r'|TemplateResponse\s*\(\s*\w+\s*,\s*'
    r'|get_template\s*\('
    r'|loader\.get_template\s*\()'
    r'([\'"])([^\'"]+\.html)\2'
)

def scan_views(root, disk_index):
    results = []
    for py in find_views_files(root):
        src = read_file(py)
        if not src: continue
        changes = []
        for m in RENDER_RE.finditer(src):
            current = m.group(3).replace('\\', '/')
            correct, _ = resolve_template_path(current, disk_index)
            if correct:
                changes.append({'old': current, 'new': correct})
        if changes:
            try:    rel = str(py.relative_to(root))
            except: rel = str(py)
            results.append({'file': py, 'rel': rel, 'changes': changes})
    return results

def apply_views(results, log):
    total = 0
    for item in results:
        src = read_file(item['file'])
        bak = backup(item['file'])
        for c in item['changes']:
            src = src.replace(f"'{c['old']}'", f"'{c['new']}'")
            src = src.replace(f'"{c["old"]}"', f'"{c["new"]}"')
        item['file'].write_text(src, encoding='utf-8')
        log.append({'step': 1, 'file': str(item['file']), 'backup': str(bak)})
        total += len(item['changes'])
        print(f'  [OK] {item["rel"]}  ({len(item["changes"])} fix)')
        for c in item['changes']:
            print(f'       {DIM}{c["old"]}{RST}')
            print(f'       {G}-> {c["new"]}{RST}')
    return total

# ── STEP 2: lazy_view() ───────────────────────────────────────────────────────

LAZY_RE = re.compile(r"""lazy_view\s*\(\s*['"]([^'"]+)['"]\s*\)""")
DEF_RE  = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)

def is_legacy(dotted):
    return any(dotted.startswith(p + '.') for p in LEGACY_MODULE_PATTERNS)

def route_func(func_name):
    fn = func_name.lower()
    for pat, mod in FUNC_MODULE_ROUTING:
        if pat in fn: return mod
    return None

def collect_view_funcs(root):
    result = {}
    lc = root / 'lumra_config'
    if not lc.exists(): return result
    for vf in lc.rglob('views.py'):
        src = read_file(vf)
        if not src: continue
        try:
            rel = vf.relative_to(root).with_suffix('').as_posix().replace('/', '.')
        except: continue
        result[rel] = set(DEF_RE.findall(src))
    return result

def build_correct_lazy(func_name, view_funcs):
    mod = route_func(func_name)
    if mod:
        candidate = f'lumra_config.{mod}.views'
        if candidate in view_funcs:
            return f'{candidate}.{func_name}'
        for mp, funcs in view_funcs.items():
            if func_name in funcs: return f'{mp}.{func_name}'
        return f'lumra_config.{mod}.views.{func_name}'
    for mp, funcs in view_funcs.items():
        if func_name in funcs: return f'{mp}.{func_name}'
    return None

def scan_lazy_views(root):
    urls_path  = find_main_urls(root)
    view_funcs = collect_view_funcs(root)
    fixable = []; unfixable = []
    if not urls_path:
        return {'urls_path': None, 'fixable': [], 'unfixable': [], 'view_funcs': view_funcs}
    src = read_file(urls_path)
    if not src:
        return {'urls_path': urls_path, 'fixable': [], 'unfixable': [], 'view_funcs': view_funcs}
    for m in LAZY_RE.finditer(src):
        dotted = m.group(1)
        if not is_legacy(dotted): continue
        func_name = dotted.rsplit('.', 1)[-1]
        correct = build_correct_lazy(func_name, view_funcs)
        if correct: fixable.append({'old': dotted, 'new': correct})
        else: unfixable.append(dotted)
    return {'urls_path': urls_path, 'fixable': fixable,
            'unfixable': unfixable, 'view_funcs': view_funcs}

def apply_lazy_views(data, log):
    urls_path = data['urls_path']
    if not urls_path or not data['fixable']: return 0
    src = read_file(urls_path)
    bak = backup(urls_path)
    def replacer(m):
        dotted = m.group(1)
        if not is_legacy(dotted): return m.group(0)
        func_name = dotted.rsplit('.', 1)[-1]
        correct = build_correct_lazy(func_name, data['view_funcs'])
        if not correct: return m.group(0)
        q = "'" if f"'{dotted}'" in m.group(0) else '"'
        return m.group(0).replace(f'{q}{dotted}{q}', f'{q}{correct}{q}', 1)
    new_src = LAZY_RE.sub(replacer, src)
    urls_path.write_text(new_src, encoding='utf-8')
    log.append({'step': 2, 'file': str(urls_path), 'backup': str(bak)})
    n = len(data['fixable'])
    try: rel = str(urls_path.relative_to(BASE))
    except: rel = str(urls_path)
    print(f'  [OK] {rel}  ({n} fix)')
    for c in data['fixable']:
        print(f'       {DIM}{c["old"]}{RST}')
        print(f'       {G}-> {c["new"]}{RST}')
    return n

# ── STEP 3: include/extends ───────────────────────────────────────────────────

INCLUDE_RE = re.compile(
    r'({%-?\s*(?:include|extends)\s+)([\'"])([^\'"]+\.html)\2',
    re.IGNORECASE,
)

def scan_html_includes(root, disk_index):
    results = []
    for html in find_html_files(root):
        src = read_file(html)
        if not src: continue
        changes = []
        for m in INCLUDE_RE.finditer(src):
            current = m.group(3).replace('\\', '/')
            correct, _ = resolve_template_path(current, disk_index)
            if correct:
                changes.append({'old': current, 'new': correct})
        if changes:
            try: rel = str(html.relative_to(root))
            except: rel = str(html)
            results.append({'file': html, 'rel': rel, 'changes': changes})
    return results

def apply_html_includes(results, log):
    total = 0
    for item in results:
        src = read_file(item['file'])
        bak = backup(item['file'])
        for c in item['changes']:
            src = src.replace(f"'{c['old']}'", f"'{c['new']}'")
            src = src.replace(f'"{c["old"]}"', f'"{c["new"]}"')
        item['file'].write_text(src, encoding='utf-8')
        log.append({'step': 3, 'file': str(item['file']), 'backup': str(bak)})
        total += len(item['changes'])
        print(f'  [OK] {item["rel"]}  ({len(item["changes"])} fix)')
        for c in item['changes']:
            print(f'       {DIM}{c["old"]}{RST}')
            print(f'       {G}-> {c["new"]}{RST}')
    return total

# ── STEP 4: import ────────────────────────────────────────────────────────────

IMPORT_RE = re.compile(r'^from\s+django\.urls\s+import\s+(.+)$', re.MULTILINE)

def scan_missing_imports(root):
    urls_path = find_main_urls(root)
    blank = {'urls_path': None, 'missing': [], 'existing_line': None, 'existing_names': [], 'src': ''}
    if not urls_path: return blank
    src = read_file(urls_path)
    if not src: return {**blank, 'urls_path': urls_path}
    m = IMPORT_RE.search(src)
    existing_line  = m.group(0) if m else None
    existing_names = []
    if m:
        raw = re.sub(r'\\\n|[()]', ' ', m.group(1))
        existing_names = [n.strip() for n in raw.split(',') if n.strip()]
    missing = [n for n in DJANGO_URLS_NAMES
               if re.search(rf'\b{n}\s*\(', src) and n not in existing_names]
    return {'urls_path': urls_path, 'missing': missing,
            'existing_line': existing_line, 'existing_names': existing_names, 'src': src}

def apply_missing_imports(data, log):
    if not data['missing'] or not data['urls_path']: return 0
    urls_path = data['urls_path']
    src, missing = data['src'], data['missing']
    if data['existing_line']:
        order = ['path', 'include', 're_path', 'register_converter']
        all_names = data['existing_names'] + [n for n in missing if n not in data['existing_names']]
        all_names.sort(key=lambda x: order.index(x) if x in order else 99)
        new_import = f"from django.urls import {', '.join(all_names)}"
        new_src = src.replace(data['existing_line'], new_import, 1)
        desc = new_import
    else:
        new_line = f"from django.urls import {', '.join(sorted(missing))}"
        matches  = list(re.finditer(r'^(from django\b.*|import django\b.*)$', src, re.MULTILINE))
        pos      = matches[-1].end() if matches else 0
        new_src  = src[:pos] + '\n' + new_line + src[pos:] if pos else new_line + '\n' + src
        desc     = new_line
    bak = backup(urls_path)
    urls_path.write_text(new_src, encoding='utf-8')
    log.append({'step': 4, 'file': str(urls_path), 'backup': str(bak)})
    try: rel = str(urls_path.relative_to(BASE))
    except: rel = str(urls_path)
    print(f'  [OK] {rel}')
    print(f'       {G}{desc}{RST}')
    return len(missing)

# ── PREVIEW / APPLY / UNDO ────────────────────────────────────────────────────

def run_preview(root, steps):
    disk_index = build_disk_index(root)
    if not disk_index:
        print(f'\n  [ERR] Folder templates/ tidak ditemukan di {root}')
        print(f'  Gunakan --source untuk menentukan root project.\n')
        return
    total_files = sum(len(v) for v in disk_index.values())
    print(f'  {DIM}Disk: {total_files} template ditemukan{RST}')

    if 1 in steps:
        sep('STEP 1 - render() di views.py')
        results = scan_views(root, disk_index)
        if not results:
            print(f'  [OK] Semua render() sudah benar.')
        for item in results:
            print(f'\n  [FIX] {item["rel"]}')
            for c in item['changes']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}-> {c["new"]}{RST}')

    if 2 in steps:
        sep('STEP 2 - lazy_view() di urls.py')
        data = scan_lazy_views(root)
        if not data['fixable'] and not data['unfixable']:
            print(f'  [OK] Semua lazy_view() sudah benar.')
        if data['fixable']:
            print(f'  [FIX] {len(data["fixable"])} path akan difix:')
            for c in data['fixable']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}-> {c["new"]}{RST}')
        if data['unfixable']:
            print(f'  [WARN] {len(data["unfixable"])} tidak bisa auto-fix:')
            for u in data['unfixable']:
                print(f'       {R}{u}{RST}')

    if 3 in steps:
        sep('STEP 3 - include/extends di .html')
        results = scan_html_includes(root, disk_index)
        if not results:
            print(f'  [OK] Semua include/extends sudah benar.')
        for item in results:
            print(f'\n  [FIX] {item["rel"]}')
            for c in item['changes']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}-> {c["new"]}{RST}')

    if 4 in steps:
        sep('STEP 4 - Import hilang di urls.py')
        data = scan_missing_imports(root)
        if not data['missing']:
            print(f'  [OK] Semua import django.urls sudah lengkap.')
        else:
            print(f'  [FIX] Akan ditambahkan: {G}{", ".join(data["missing"])}{RST}')

    sep()
    print(f'  Jalankan dengan {C}--apply{RST} untuk menerapkan.\n')

def run_apply(root, steps, yes):
    run_preview(root, steps)
    if not yes:
        try:
            confirm = input('  Terapkan semua perbaikan? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.'); return
        if confirm != 'y':
            print('  Dibatalkan.'); return

    log = []; disk_index = build_disk_index(root)
    total = {'views': 0, 'lazy': 0, 'html': 0, 'imports': 0}

    if 1 in steps:
        sep('STEP 1 - Fix render()')
        results = scan_views(root, disk_index)
        total['views'] = apply_views(results, log) if results else 0
        if not results: print(f'  [OK] Tidak ada yang perlu difix.')

    if 2 in steps:
        sep('STEP 2 - Fix lazy_view()')
        data = scan_lazy_views(root)
        total['lazy'] = apply_lazy_views(data, log) if data['fixable'] else 0
        if not data['fixable']: print(f'  [OK] Tidak ada yang perlu difix.')
        if data['unfixable']:
            print(f'\n  [WARN] {len(data["unfixable"])} tidak bisa auto-fix:')
            for u in data['unfixable']: print(f'       {DIM}{u}{RST}')

    if 3 in steps:
        sep('STEP 3 - Fix include/extends')
        results = scan_html_includes(root, disk_index)
        total['html'] = apply_html_includes(results, log) if results else 0
        if not results: print(f'  [OK] Tidak ada yang perlu difix.')

    if 4 in steps:
        sep('STEP 4 - Fix import urls.py')
        data = scan_missing_imports(root)
        total['imports'] = apply_missing_imports(data, log) if data['missing'] else 0
        if not data['missing']: print(f'  [OK] Semua import sudah lengkap.')

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    sep()
    grand = sum(total.values())
    if grand:
        print(f'  [OK] Selesai!')
        print(f'     render()        : {total["views"]} fix')
        print(f'     lazy_view()     : {total["lazy"]} fix')
        print(f'     include/extends : {total["html"]} fix')
        print(f'     import          : {total["imports"]} fix')
        print(f'  {DIM}Rollback  : python lumra_fix_master.py --undo{RST}')
        print(f'  {C}Verifikasi: python manage.py check{RST}')
    else:
        print(f'  [OK] Project sudah bersih - tidak ada yang perlu diperbaiki.')
    print()

def run_undo():
    if not LOG_FILE.exists():
        print(f'\n  [WARN] Log tidak ditemukan.\n'); return
    with open(LOG_FILE) as f:
        log = json.load(f)
    restored = 0
    for entry in log:
        orig = Path(entry['file']); bak = Path(entry['backup'])
        if bak.exists():
            shutil.copy2(bak, orig); restored += 1
            print(f'  [FIX] Restored: {orig.name}')
        else:
            print(f'  [WARN] Backup tidak ada: {bak}')
    LOG_FILE.unlink(missing_ok=True)
    print(f'\n  [OK] {restored} file dikembalikan.\n')

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP - Master Fix Script (disk-based)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--apply',  action='store_true')
    parser.add_argument('--yes',    action='store_true')
    parser.add_argument('--undo',   action='store_true')
    parser.add_argument('--step',   type=int, nargs='+', choices=[1, 2, 3, 4])
    parser.add_argument('--source', type=str, default=None)
    args  = parser.parse_args()
    root  = find_root(args.source)
    steps = set(args.step) if args.step else {1, 2, 3, 4}

    print(f'\n{B}{"="*64}')
    print(f'  {W}Lumra ERP - Master Fix Script{RST}')
    print(f'{B}{"="*64}{RST}')
    print(f'  Root  : {DIM}{root}{RST}')
    print(f'  Steps : {C}{sorted(steps)}{RST}')
    print(f'  Mode  : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}\n')

    if args.undo: run_undo()
    elif args.apply: run_apply(root, steps, yes=args.yes)
    else: run_preview(root, steps)

if __name__ == '__main__':
    main()