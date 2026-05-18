"""
lumra_master.py  —  Lumra ERP · Master Fix Tool
================================================
Menggabungkan lumra_sync.py + lumra_fix_master.py menjadi satu script.
Sumber kebenaran: file .html dan views.py yang ADA DI DISK.
Aman dijalankan berulang kali — yang sudah benar tidak disentuh.

Yang diperbaiki:
  1. __init__.py  → rebuild export (tambah alias yang hilang, sync dengan views/*.py)
  2. render()     → fix path template di views.py berdasarkan lokasi file di disk
  3. lazy_view()  → fix modul path di urls.py
  4. include/extends → fix path di .html berdasarkan lokasi file di disk
  5. import       → tambah import django.urls yang hilang (include, path, re_path)
  6. check        → jalankan manage.py check

Cara pakai:
  python lumra_master.py                     → preview semua (AMAN)
  python lumra_master.py --apply             → fix semua
  python lumra_master.py --apply --yes       → fix tanpa konfirmasi
  python lumra_master.py --apply --step 1 3  → hanya step tertentu
  python lumra_master.py --undo              → rollback
  python lumra_master.py --source D:\\APPS\\Project\\lumra
"""

import re, sys, shutil, json, argparse, subprocess
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

BASE       = Path(__file__).resolve().parent
BACKUP_DIR = BASE / '.lumra_master_backup'
LOG_FILE   = BASE / '.lumra_master_log.json'

G  = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B  = '\033[94m'; C = '\033[96m'; W = '\033[97m'
DIM= '\033[2m';  RST= '\033[0m'
OK = f'{G}✅{RST}'; WN = f'{Y}⚠️ {RST}'; ER = f'{R}❌{RST}'; FX = f'{C}🔧{RST}'

def sep(title=''):
    pad = (66 - len(title) - 2) // 2 if title else 0
    if title:
        print(f'\n{B}{"═"*pad} {W}{title}{RST}{B} {"═"*(66-pad-len(title)-2)}{RST}')
    else:
        print(f'{DIM}{"═"*66}{RST}')

# ─────────────────────────────────────────────────────────────────────────────
# ROUTING TABLE  (fungsi → modul)
# Urutan penting — lebih spesifik di atas
# ─────────────────────────────────────────────────────────────────────────────

FUNC_MODULE_ROUTING: list[tuple[str, str]] = [
    # api — PALING ATAS
    ('api_dashboard',       'api'),   ('submit_requisition',  'api'),
    ('confirm_receipt',     'api'),   ('submit_purchases',    'api'),
    ('get_location_stock',  'api'),   ('submit_stock_allocation', 'api'),
    # auth
    ('login',               'auth_app'), ('logout',           'auth_app'),
    ('register',            'auth_app'),
    # inventory — sebelum master_data
    ('supplier_price',      'inventory'), ('stock_movement',  'inventory'),
    ('stock_planning',      'inventory'), ('export_stock',    'inventory'),
    ('import_product',      'inventory'), ('products_import', 'inventory'),
    ('import_template',     'inventory'), ('stock_allocation','inventory'),
    ('approve_requisition', 'inventory'), ('add_stock_movement','inventory'),
    ('stock_opname',        'inventory'), ('opname',          'inventory'),
    # sales
    ('dashboard',           'sales'),  ('pos',               'sales'),
    ('notification',        'sales'),  ('sales_history',     'sales'),
    ('sales_insight',       'sales'),  ('sales_performance', 'sales'),
    ('sales_products',      'sales'),  ('purchasing',        'sales'),
    # master_data
    ('product',             'master_data'), ('categor',       'master_data'),
    ('unit_',               'master_data'), ('_unit',         'master_data'),
    ('units_',              'master_data'), ('vendor',        'master_data'),
    ('customer',            'master_data'), ('location',      'master_data'),
    # marketing
    ('campaign',            'marketing'),   ('discount',      'marketing'),
    ('loyalty',             'marketing'),   ('promo',         'marketing'),
    # reports
    ('financial_report',    'reports'),   ('market_insight',  'reports'),
    ('trends_analysis',     'reports'),   ('activity_log',    'reports'),
    ('download_report',     'reports'),   ('export_trends',   'reports'),
    ('sales_report',        'reports'),   ('transaction_summary','reports'),
    ('transfer_report',     'reports'),   ('requisition_report','reports'),
    ('purchasing_report',   'reports'),   ('inventory_log',   'reports'),
    ('inventory_low',       'reports'),   ('inventory_stock', 'reports'),
    ('profit_loss',         'reports'),   ('sales_by_',       'reports'),
    ('sales_summary',       'reports'),   ('report_',         'reports'),
    # production
    ('recipe',              'production'), ('bom',            'production'),
    # settings_app
    ('profile',             'settings_app'), ('settings',     'settings_app'),
    ('system_status',       'settings_app'), ('business',     'settings_app'),
    ('users',               'settings_app'), ('user_role',    'settings_app'),
    ('about',               'settings_app'), ('contact',      'settings_app'),
    ('pricing',             'settings_app'), ('search',       'settings_app'),
    ('feature_matrix',      'settings_app'), ('permissions',  'settings_app'),
]

# Alias yang sering hilang di __init__.py: nama_alias → nama_asli
KNOWN_ALIASES = {
    'sales_insight_view'  : 'sales_history_view',
    'sales_insight'       : 'sales_history_view',
}

LEGACY_PREFIXES = [
    'lumra_config.views',
    'lumra_config.views.inventory_views',
    'lumra_config.views.stock_movement_views',
    'lumra_config.views.api_views',
]

DJANGO_URLS_NAMES = ['path', 'include', 're_path']

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def read_file(p: Path) -> str | None:
    for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
        try: return p.read_text(encoding=enc)
        except: continue
    return None

def write_file(p: Path, src: str):
    p.write_text(src, encoding='utf-8')

def backup(p: Path) -> Path:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:    rel = p.relative_to(BASE)
    except: rel = Path(p.name)
    dest = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    return dest

def find_root(source: str | None) -> Path:
    return Path(source).resolve() if source else BASE

def find_templates_dir(root: Path) -> Path | None:
    for c in [root/'lumra_config'/'templates', root/'templates']:
        if c.exists(): return c
    return None

def find_views_dir(root: Path) -> Path | None:
    p = root / 'lumra_config' / 'views'
    return p if p.exists() else None

def find_main_urls(root: Path) -> Path | None:
    for rel in ['lumra_system/urls.py','lumra/urls.py','config/urls.py','urls.py']:
        p = root / rel
        if p.exists(): return p
    for p in root.rglob('urls.py'):
        if 'lumra_config' not in str(p):
            src = read_file(p)
            if src and 'urlpatterns' in src and 'admin' in src: return p
    return None

def find_manage(root: Path) -> Path | None:
    p = root / 'manage.py'
    if p.exists(): return p
    for f in root.rglob('manage.py'): return f
    return None

# ─────────────────────────────────────────────────────────────────────────────
# DISK INDEX  —  basename → [rel_path, ...]  (relatif terhadap templates/)
# ─────────────────────────────────────────────────────────────────────────────

def build_disk_index(root: Path) -> dict[str, list[str]]:
    tmpl = find_templates_dir(root)
    if not tmpl: return {}
    idx: dict[str, list[str]] = {}
    for f in tmpl.rglob('*.html'):
        rel = str(f.relative_to(tmpl)).replace('\\', '/')
        idx.setdefault(f.name, []).append(rel)
    return idx

def resolve_template(current: str, idx: dict) -> str | None:
    """
    Kembalikan path yang benar dari disk index.
    None = sudah benar atau tidak bisa ditentukan.
    """
    norm     = current.replace('\\', '/')
    basename = norm.split('/')[-1]
    hits     = idx.get(basename)
    if not hits or len(hits) > 1: return None
    correct = hits[0]
    return correct if correct != norm else None

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Rebuild __init__.py
# Tambah alias yang hilang + pastikan semua export sync dengan views/*.py
# ─────────────────────────────────────────────────────────────────────────────

DEF_RE = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)

def collect_view_funcs(root: Path) -> dict[str, set[str]]:
    """Return { 'lumra_config.X.views': {func1, func2, ...} }"""
    result: dict[str, set[str]] = {}
    vd = find_views_dir(root)
    if not vd: return result
    for vf in vd.rglob('views.py'):
        src = read_file(vf)
        if not src: continue
        try:
            rel = vf.relative_to(root).with_suffix('').as_posix().replace('/', '.')
        except: continue
        result[rel] = set(DEF_RE.findall(src))
    # Juga baca semua *_views.py di lumra_config/views/
    views_dir = root / 'lumra_config' / 'views'
    if views_dir.exists():
        for vf in views_dir.glob('*_views.py'):
            src = read_file(vf)
            if not src: continue
            key = f'lumra_config.views.{vf.stem}'
            result[key] = set(DEF_RE.findall(src))
        # __init__.py juga
        init = views_dir / '__init__.py'
        if init.exists():
            src = read_file(init)
            if src:
                result['lumra_config.views'] = set(DEF_RE.findall(src))
    return result

def scan_init_issues(root: Path) -> dict:
    """
    Scan __init__.py untuk:
    - Alias yang ada di urls.py tapi tidak di-export __init__.py
    - Import yang rusak (nama tidak ada di file sumber)
    """
    init_path = root / 'lumra_config' / 'views' / '__init__.py'
    if not init_path.exists():
        return {'init_path': None, 'missing_aliases': [], 'broken_imports': []}

    init_src = read_file(init_path)
    urls_path = find_main_urls(root)

    # Kumpulkan semua nama yang diimport di urls.py via lazy_view
    lazy_funcs = set()
    if urls_path:
        src = read_file(urls_path) or ''
        LAZY_RE = re.compile(r"""lazy_view\s*\(\s*['"][^'"]*\.(\w+)['"]\s*\)""")
        for m in LAZY_RE.finditer(src):
            lazy_funcs.add(m.group(1))

    # Cari alias yang hilang
    missing_aliases = []
    for alias, real_name in KNOWN_ALIASES.items():
        # Cek apakah dipakai di urls.py
        if alias not in lazy_funcs: continue
        # Cek apakah sudah ada di __init__.py
        if alias not in init_src:
            missing_aliases.append({'alias': alias, 'real': real_name})

    return {
        'init_path'      : init_path,
        'missing_aliases': missing_aliases,
        'init_src'       : init_src,
    }

def apply_init_fix(root: Path, log: list) -> int:
    data = scan_init_issues(root)
    if not data['missing_aliases'] or not data['init_path']:
        return 0

    init_path = data['init_path']
    src       = data['init_src']
    n         = 0

    bak = backup(init_path)
    new_src = src

    for item in data['missing_aliases']:
        alias     = item['alias']
        real_name = item['real']

        # Pastikan real_name ada di __init__.py
        if real_name not in new_src:
            print(f'  {WN} {real_name} tidak ditemukan di __init__.py — skip alias {alias}')
            continue

        # Tambah alias setelah baris real_name di imports
        # Cari baris from .misc_views import (...) dan tambahkan
        # Cara paling aman: tambah assignment di akhir file sebelum __all__
        all_pos = new_src.find('\n__all__')
        insert_line = f'\n# Alias untuk backward compatibility\n{alias} = {real_name}\n'
        if all_pos != -1:
            new_src = new_src[:all_pos] + insert_line + new_src[all_pos:]
        else:
            new_src = new_src + insert_line

        # Tambahkan ke __all__ juga
        all_match = re.search(r'__all__\s*=\s*\[([^\]]*)\]', new_src, re.DOTALL)
        if all_match:
            all_content = all_match.group(1)
            if alias not in all_content:
                new_all = all_content.rstrip() + f"\n    '{alias}',\n"
                new_src = new_src[:all_match.start(1)] + new_all + new_src[all_match.end(1):]

        print(f'  {OK} Tambah alias: {G}{alias}{RST} = {real_name}')
        n += 1

    if n > 0:
        write_file(init_path, new_src)
        log.append({'step': 1, 'file': str(init_path), 'backup': str(bak)})

    return n

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Fix render() di views.py  (disk-based)
# ─────────────────────────────────────────────────────────────────────────────

RENDER_RE = re.compile(
    r'(render\s*\(\s*\w+\s*,\s*'
    r'|TemplateResponse\s*\(\s*\w+\s*,\s*'
    r'|get_template\s*\('
    r'|loader\.get_template\s*\()'
    r'([\'"])([^\'"]+\.html)\2'
)

def scan_views(root: Path, idx: dict) -> list[dict]:
    results = []
    vd = root / 'lumra_config'
    if not vd.exists(): return results
    for py in sorted(vd.rglob('views.py')) + sorted(vd.rglob('*_views.py')):
        src = read_file(py)
        if not src: continue
        changes = []
        seen = set()
        for m in RENDER_RE.finditer(src):
            current = m.group(3).replace('\\', '/')
            if current in seen: continue
            correct = resolve_template(current, idx)
            if correct:
                seen.add(current)
                changes.append({'old': current, 'new': correct})
        if changes:
            try:    rel = str(py.relative_to(root))
            except: rel = str(py)
            results.append({'file': py, 'rel': rel, 'changes': changes})
    return results

def apply_views(results: list[dict], log: list) -> int:
    total = 0
    for item in results:
        src = read_file(item['file'])
        bak = backup(item['file'])
        for c in item['changes']:
            src = src.replace(f"'{c['old']}'", f"'{c['new']}'")
            src = src.replace(f'"{c["old"]}"', f'"{c["new"]}"')
        write_file(item['file'], src)
        log.append({'step': 2, 'file': str(item['file']), 'backup': str(bak)})
        total += len(item['changes'])
        print(f'  {OK} {item["rel"]}  ({len(item["changes"])} fix)')
        for c in item['changes']:
            print(f'       {DIM}{c["old"]}{RST}')
            print(f'       {G}→ {c["new"]}{RST}')
    return total

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Fix lazy_view() di urls.py
# ─────────────────────────────────────────────────────────────────────────────

LAZY_RE = re.compile(r"""lazy_view\s*\(\s*['"]([^'"]+)['"]\s*\)""")

def is_legacy(dotted: str) -> bool:
    return any(dotted.startswith(p + '.') for p in LEGACY_PREFIXES)

def route_func(name: str) -> str | None:
    fn = name.lower()
    for pat, mod in FUNC_MODULE_ROUTING:
        if pat in fn: return mod
    return None

def build_correct_lazy(func_name: str, view_funcs: dict) -> str | None:
    mod = route_func(func_name)
    if mod:
        candidate = f'lumra_config.{mod}.views'
        if candidate in view_funcs: return f'{candidate}.{func_name}'
        for mp, funcs in view_funcs.items():
            if func_name in funcs: return f'{mp}.{func_name}'
        return f'lumra_config.{mod}.views.{func_name}'
    for mp, funcs in view_funcs.items():
        if func_name in funcs: return f'{mp}.{func_name}'
    return None

def scan_lazy(root: Path) -> dict:
    urls_path  = find_main_urls(root)
    view_funcs = collect_view_funcs(root)
    fixable = []; unfixable = []
    if not urls_path:
        return {'urls_path': None, 'fixable': [], 'unfixable': [], 'vf': view_funcs}
    src = read_file(urls_path) or ''
    seen = set()
    for m in LAZY_RE.finditer(src):
        dotted = m.group(1)
        if not is_legacy(dotted): continue
        if dotted in seen: continue
        seen.add(dotted)
        fn = dotted.rsplit('.', 1)[-1]
        correct = build_correct_lazy(fn, view_funcs)
        if correct and correct != dotted:
            fixable.append({'old': dotted, 'new': correct})
        elif not correct:
            unfixable.append(dotted)
    return {'urls_path': urls_path, 'fixable': fixable,
            'unfixable': unfixable, 'vf': view_funcs}

def apply_lazy(data: dict, log: list) -> int:
    if not data['urls_path'] or not data['fixable']: return 0
    src = read_file(data['urls_path'])
    bak = backup(data['urls_path'])
    def replacer(m):
        dotted = m.group(1)
        if not is_legacy(dotted): return m.group(0)
        fn = dotted.rsplit('.', 1)[-1]
        correct = build_correct_lazy(fn, data['vf'])
        if not correct or correct == dotted: return m.group(0)
        q = "'" if f"'{dotted}'" in m.group(0) else '"'
        return m.group(0).replace(f'{q}{dotted}{q}', f'{q}{correct}{q}', 1)
    new_src = LAZY_RE.sub(replacer, src)
    write_file(data['urls_path'], new_src)
    log.append({'step': 3, 'file': str(data['urls_path']), 'backup': str(bak)})
    n = len(data['fixable'])
    try:    rel = str(data['urls_path'].relative_to(BASE))
    except: rel = str(data['urls_path'])
    print(f'  {OK} {rel}  ({n} fix)')
    for c in data['fixable']:
        print(f'       {DIM}{c["old"]}{RST}')
        print(f'       {G}→ {c["new"]}{RST}')
    return n

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Fix include/extends di .html  (disk-based)
# ─────────────────────────────────────────────────────────────────────────────

INCLUDE_RE = re.compile(
    r'({%-?\s*(?:include|extends)\s+)([\'"])([^\'"]+\.html)\2',
    re.IGNORECASE,
)

def scan_html(root: Path, idx: dict) -> list[dict]:
    tmpl = find_templates_dir(root)
    if not tmpl: return []
    results = []
    for html in tmpl.rglob('*.html'):
        src = read_file(html)
        if not src: continue
        changes = []
        seen = set()
        for m in INCLUDE_RE.finditer(src):
            current = m.group(3).replace('\\', '/')
            if current in seen: continue
            correct = resolve_template(current, idx)
            if correct:
                seen.add(current)
                changes.append({'old': current, 'new': correct})
        if changes:
            try:    rel = str(html.relative_to(root))
            except: rel = str(html)
            results.append({'file': html, 'rel': rel, 'changes': changes})
    return results

def apply_html(results: list[dict], log: list) -> int:
    total = 0
    for item in results:
        src = read_file(item['file'])
        bak = backup(item['file'])
        for c in item['changes']:
            src = src.replace(f"'{c['old']}'", f"'{c['new']}'")
            src = src.replace(f'"{c["old"]}"', f'"{c["new"]}"')
        write_file(item['file'], src)
        log.append({'step': 4, 'file': str(item['file']), 'backup': str(bak)})
        total += len(item['changes'])
        print(f'  {OK} {item["rel"]}  ({len(item["changes"])} fix)')
        for c in item['changes']:
            print(f'       {DIM}{c["old"]}{RST}')
            print(f'       {G}→ {c["new"]}{RST}')
    return total

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Fix import hilang di urls.py
# ─────────────────────────────────────────────────────────────────────────────

IMPORT_RE = re.compile(r'^from\s+django\.urls\s+import\s+(.+)$', re.MULTILINE)

def scan_imports(root: Path) -> dict:
    urls_path = find_main_urls(root)
    blank = {'urls_path': None, 'missing': [], 'existing_line': None,
             'existing_names': [], 'src': ''}
    if not urls_path: return blank
    src = read_file(urls_path) or ''
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

def apply_imports(data: dict, log: list) -> int:
    if not data['missing'] or not data['urls_path']: return 0
    src, missing = data['src'], data['missing']
    if data['existing_line']:
        order = ['path', 'include', 're_path', 'register_converter']
        names = data['existing_names'] + [n for n in missing if n not in data['existing_names']]
        names.sort(key=lambda x: order.index(x) if x in order else 99)
        new_import = f"from django.urls import {', '.join(names)}"
        new_src = src.replace(data['existing_line'], new_import, 1)
        desc = new_import
    else:
        new_line = f"from django.urls import {', '.join(sorted(missing))}"
        matches  = list(re.finditer(r'^(from django\b.*|import django\b.*)$', src, re.MULTILINE))
        pos      = matches[-1].end() if matches else 0
        new_src  = src[:pos] + '\n' + new_line + src[pos:] if pos else new_line + '\n' + src
        desc     = new_line
    bak = backup(data['urls_path'])
    write_file(data['urls_path'], new_src)
    log.append({'step': 5, 'file': str(data['urls_path']), 'backup': str(bak)})
    try:    rel = str(data['urls_path'].relative_to(BASE))
    except: rel = str(data['urls_path'])
    print(f'  {OK} {rel}')
    print(f'       {G}{desc}{RST}')
    return len(missing)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — manage.py check
# ─────────────────────────────────────────────────────────────────────────────

def run_check(root: Path) -> dict:
    manage = find_manage(root)
    if not manage: return {'success': False, 'output': 'manage.py tidak ditemukan'}
    try:
        r = subprocess.run(
            [sys.executable, str(manage), 'check'],
            cwd=str(manage.parent), capture_output=True, text=True, timeout=60,
        )
        out = (r.stdout + r.stderr).strip()
        return {'success': r.returncode == 0, 'output': out}
    except subprocess.TimeoutExpired:
        return {'success': False, 'output': 'Timeout'}
    except Exception as e:
        return {'success': False, 'output': str(e)}

# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW
# ─────────────────────────────────────────────────────────────────────────────

def run_preview(root: Path, steps: set):
    idx = build_disk_index(root)
    n_templates = sum(len(v) for v in idx.values())

    if idx:
        print(f'  {DIM}Disk index: {n_templates} template dari {len(idx)} nama unik{RST}')
    else:
        print(f'  {WN} Folder templates/ tidak ditemukan di {root}')
        print(f'  Gunakan --source untuk menentukan root project.')

    if 1 in steps:
        sep('STEP 1 — __init__.py: alias hilang')
        data = scan_init_issues(root)
        if not data['missing_aliases']:
            print(f'  {OK} Semua alias sudah ada di __init__.py')
        for item in data['missing_aliases']:
            print(f'  {FX} Alias hilang: {Y}{item["alias"]}{RST} = {item["real"]}')

    if 2 in steps:
        sep('STEP 2 — render() di views.py')
        results = scan_views(root, idx)
        if not results:
            print(f'  {OK} Semua render() sudah benar.')
        for item in results:
            print(f'\n  {FX} {item["rel"]}')
            for c in item['changes']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}→ {c["new"]}{RST}')

    if 3 in steps:
        sep('STEP 3 — lazy_view() di urls.py')
        data = scan_lazy(root)
        if not data['fixable'] and not data['unfixable']:
            print(f'  {OK} Semua lazy_view() sudah benar.')
        if data['fixable']:
            print(f'  {FX} {len(data["fixable"])} path akan difix:')
            for c in data['fixable']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}→ {c["new"]}{RST}')
        if data['unfixable']:
            print(f'  {WN} {len(data["unfixable"])} tidak bisa auto-fix:')
            for u in data['unfixable']:
                print(f'       {R}{u}{RST}')

    if 4 in steps:
        sep('STEP 4 — include/extends di .html')
        results = scan_html(root, idx)
        if not results:
            print(f'  {OK} Semua include/extends sudah benar.')
        for item in results:
            print(f'\n  {FX} {item["rel"]}')
            for c in item['changes']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}→ {c["new"]}{RST}')

    if 5 in steps:
        sep('STEP 5 — Import hilang di urls.py')
        data = scan_imports(root)
        if not data['missing']:
            print(f'  {OK} Semua import django.urls sudah lengkap.')
        else:
            print(f'  {FX} Akan ditambahkan: {G}{", ".join(data["missing"])}{RST}')

    if 6 in steps:
        sep('STEP 6 — manage.py check')
        print(f'  {DIM}Menjalankan manage.py check...{RST}')
        d = run_check(root)
        icon = OK if d['success'] else ER
        for line in d['output'].splitlines():
            print(f'  {icon}  {line}')

    sep()
    print(f'  Jalankan dengan {C}--apply{RST} untuk menerapkan.\n')

# ─────────────────────────────────────────────────────────────────────────────
# APPLY
# ─────────────────────────────────────────────────────────────────────────────

def run_apply(root: Path, steps: set, yes: bool):
    run_preview(root, steps)

    if not yes:
        try:
            confirm = input('  Terapkan semua perbaikan? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.'); return
        if confirm != 'y':
            print('  Dibatalkan.'); return

    log   = []
    idx   = build_disk_index(root)
    total = {1:0, 2:0, 3:0, 4:0, 5:0}

    if 1 in steps:
        sep('STEP 1 — Fix __init__.py')
        n = apply_init_fix(root, log)
        total[1] = n
        if not n: print(f'  {OK} Tidak ada yang perlu difix.')

    if 2 in steps:
        sep('STEP 2 — Fix render()')
        r = scan_views(root, idx)
        total[2] = apply_views(r, log) if r else 0
        if not r: print(f'  {OK} Tidak ada yang perlu difix.')

    if 3 in steps:
        sep('STEP 3 — Fix lazy_view()')
        data = scan_lazy(root)
        total[3] = apply_lazy(data, log) if data['fixable'] else 0
        if not data['fixable']: print(f'  {OK} Tidak ada yang perlu difix.')
        if data['unfixable']:
            print(f'\n  {WN} {len(data["unfixable"])} tidak bisa auto-fix (perlu manual):')
            for u in data['unfixable']: print(f'       {DIM}{u}{RST}')

    if 4 in steps:
        sep('STEP 4 — Fix include/extends')
        r = scan_html(root, idx)
        total[4] = apply_html(r, log) if r else 0
        if not r: print(f'  {OK} Tidak ada yang perlu difix.')

    if 5 in steps:
        sep('STEP 5 — Fix import urls.py')
        data = scan_imports(root)
        total[5] = apply_imports(data, log) if data['missing'] else 0
        if not data['missing']: print(f'  {OK} Semua import sudah lengkap.')

    if log:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    sep()
    grand = sum(total.values())
    if grand:
        print(f'  {OK} Selesai!')
        print(f'     __init__.py alias : {total[1]} fix')
        print(f'     render()          : {total[2]} fix')
        print(f'     lazy_view()       : {total[3]} fix')
        print(f'     include/extends   : {total[4]} fix')
        print(f'     import            : {total[5]} fix')
        print(f'  {DIM}Rollback  : python lumra_master.py --undo{RST}')
    else:
        print(f'  {OK} Project sudah bersih.')

    if 6 in steps:
        sep('STEP 6 — manage.py check')
        d = run_check(root)
        icon = OK if d['success'] else ER
        for line in d['output'].splitlines():
            print(f'  {icon}  {line}')
    print()

# ─────────────────────────────────────────────────────────────────────────────
# UNDO
# ─────────────────────────────────────────────────────────────────────────────

def run_undo():
    if not LOG_FILE.exists():
        print(f'\n  {WN} Log tidak ditemukan.\n'); return
    with open(LOG_FILE) as f: log = json.load(f)
    restored = 0
    for entry in log:
        orig = Path(entry['file']); bak = Path(entry['backup'])
        if bak.exists():
            shutil.copy2(bak, orig); restored += 1
            print(f'  {FX} Restored: {orig.name}')
        else:
            print(f'  {WN} Backup tidak ada: {bak}')
    LOG_FILE.unlink(missing_ok=True)
    print(f'\n  {OK} {restored} file dikembalikan.\n')

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP — Master Fix Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps:
  1  __init__.py  → tambah alias yang hilang (misal: sales_insight_view)
  2  render()     → fix path template di views.py (dari disk)
  3  lazy_view()  → fix modul path di urls.py
  4  include/extends → fix path di .html (dari disk)
  5  import       → tambah import django.urls yang hilang
  6  check        → jalankan manage.py check

Contoh:
  python lumra_master.py                        → preview semua
  python lumra_master.py --apply                → fix semua
  python lumra_master.py --apply --step 1       → fix hanya __init__.py
  python lumra_master.py --apply --yes          → tanpa konfirmasi
  python lumra_master.py --undo                 → rollback
  python lumra_master.py --source D:\\Project
        """
    )
    parser.add_argument('--apply',  action='store_true')
    parser.add_argument('--yes',    action='store_true')
    parser.add_argument('--undo',   action='store_true')
    parser.add_argument('--step',   type=int, nargs='+', choices=range(1,7))
    parser.add_argument('--source', type=str, default=None)
    args  = parser.parse_args()
    root  = find_root(args.source)
    steps = set(args.step) if args.step else {1,2,3,4,5,6}

    print(f'\n{B}{"═"*66}')
    print(f'  {W}Lumra ERP — Master Fix Tool{RST}')
    print(f'{B}{"═"*66}{RST}')
    print(f'  Root  : {DIM}{root}{RST}')
    print(f'  Steps : {C}{sorted(steps)}{RST}')
    print(f'  Mode  : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}\n')

    if args.undo: run_undo()
    elif args.apply: run_apply(root, steps, yes=args.yes)
    else: run_preview(root, steps)

if __name__ == '__main__':
    main()