"""
lumra_fix_master.py
===================
Script master — scan dan perbaiki semua referensi yang salah dalam satu perintah.
Bisa dijalankan berulang kapanpun muncul error baru. Aman dijalankan berkali-kali
(idempoten — yang sudah benar tidak disentuh).

Yang diperbaiki:
  1. render() / TemplateResponse() path salah di views.py
     → Sumber kebenaran: file .html di disk + TEMPLATE_REGISTRY
  2. lazy_view() modul salah di urls.py
     → 'lumra_config.views.X' → 'lumra_config.MODUL.views.X'
  3. {% include %} / {% extends %} path salah di .html
     → Sumber kebenaran: file .html di disk
  4. Import hilang di urls.py
     → 'include', 'path', 're_path' ditambah otomatis

Cara pakai:
  python lumra_fix_master.py              → preview (AMAN)
  python lumra_fix_master.py --apply      → perbaiki semua
  python lumra_fix_master.py --apply --yes→ tanpa konfirmasi
  python lumra_fix_master.py --undo       → rollback
  python lumra_fix_master.py --step 1 3  → hanya step tertentu
  python lumra_fix_master.py --source D:\\APPS\\Project\\lumra
"""

import re, sys, shutil, json, argparse
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
    pad = (64 - len(title) - 2) // 2 if title else 0
    if title:
        print(f'\n{B}{"═"*pad} {W}{title}{RST}{B} {"═"*(64-pad-len(title)-2)}{RST}')
    else:
        print(f'{DIM}{"═"*64}{RST}')

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE REGISTRY
# Sumber kebenaran manual: alias / nama lama → path canonical di disk.
# Update bagian ini kalau ada rename/pindah template baru.
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATE_REGISTRY: dict[str, str] = {
    # ── Sales ──────────────────────────────────────────────────────────────
    'sales/dashboard.html'              : 'lumra_pages/sales/dashboard.html',
    'sales/notification.html'           : 'lumra_pages/sales/notification.html',
    'sales/pos.html'                    : 'lumra_pages/sales/pos.html',
    'sales/purchasing.html'             : 'lumra_pages/sales/purchasing.html',
    'sales/sales_insight.html'          : 'lumra_pages/sales/sales_intelligence.html',
    'sales/sales_intelligence.html'     : 'lumra_pages/sales/sales_intelligence.html',
    # tanpa subfolder (path lama dari views monolitik)
    'dashboard.html'                    : 'lumra_pages/sales/dashboard.html',
    'notification.html'                 : 'lumra_pages/sales/notification.html',
    'pos.html'                          : 'lumra_pages/sales/pos.html',
    'purchasing.html'                   : 'lumra_pages/sales/purchasing.html',
    'sales_insight.html'                : 'lumra_pages/sales/sales_intelligence.html',

    # ── Master Data ────────────────────────────────────────────────────────
    'master_data/customer.html'         : 'lumra_pages/master_data/customer_form.html',
    'master_data/customers.html'        : 'lumra_pages/master_data/customers_list.html',
    'master_data/customers_list.html'   : 'lumra_pages/master_data/customers_list.html',
    'master_data/locations.html'        : 'lumra_pages/master_data/location_list.html',
    'master_data/vendors_list.html'     : 'lumra_pages/master_data/vendor_list.html',
    'customer.html'                     : 'lumra_pages/master_data/customer_form.html',
    'customers.html'                    : 'lumra_pages/master_data/customers_list.html',
    'locations.html'                    : 'lumra_pages/master_data/location_list.html',
    'vendors_list.html'                 : 'lumra_pages/master_data/vendor_list.html',

    # ── Inventory ──────────────────────────────────────────────────────────
    'inventory/inventory.html'          : 'lumra_pages/inventory/stock_overview.html',
    'inventory/products.html'           : 'lumra_pages/inventory/product_list.html',
    'inventory/add_stock_movement.html' : 'lumra_pages/inventory/stock_movement_form.html',
    'inventory.html'                    : 'lumra_pages/inventory/stock_overview.html',
    'products.html'                     : 'lumra_pages/inventory/product_list.html',
    'add_stock_movement.html'           : 'lumra_pages/inventory/stock_movement_form.html',

    # ── Reports ────────────────────────────────────────────────────────────
    'reports/activity_log.html'         : 'lumra_pages/reports/report_activity_log.html',
    'activity_log.html'                 : 'lumra_pages/reports/report_activity_log.html',

    # ── Settings ───────────────────────────────────────────────────────────
    'settings/users.html'               : 'lumra_pages/settings/user_list.html',
    'settings/business_form_general.html': 'lumra_pages/settings/business_profile.html',
    'users.html'                        : 'lumra_pages/settings/user_list.html',
    'business_form_general.html'        : 'lumra_pages/settings/business_profile.html',
}

# ─────────────────────────────────────────────────────────────────────────────
# LAZY_VIEW ROUTING TABLE
# Nama fungsi → modul yang benar
# ─────────────────────────────────────────────────────────────────────────────

FUNC_MODULE_ROUTING: list[tuple[str, str]] = [
    ('api_dashboard',       'api'),   ('submit_requisition',  'api'),
    ('confirm_receipt',     'api'),   ('submit_purchases',    'api'),
    ('get_location_stock',  'api'),
    ('login',               'auth_app'), ('logout',           'auth_app'),
    ('register',            'auth_app'),
    ('supplier_price',      'inventory'), ('stock_movement',  'inventory'),
    ('stock_planning',      'inventory'), ('export_stock',    'inventory'),
    ('import_product',      'inventory'), ('products_import', 'inventory'),
    ('import_template',     'inventory'), ('stock_allocation','inventory'),
    ('approve_requisition', 'inventory'),
    ('dashboard',           'sales'),  ('pos',               'sales'),
    ('notification',        'sales'),  ('sales_history',     'sales'),
    ('sales_performance',   'sales'),  ('sales_products',    'sales'),
    ('purchasing',          'sales'),
    ('product',             'master_data'), ('categor',       'master_data'),
    ('unit_',               'master_data'), ('_unit',         'master_data'),
    ('units_',              'master_data'), ('vendor',        'master_data'),
    ('customer',            'master_data'), ('location',      'master_data'),
    ('stock_opname',        'master_data'), ('opname',        'master_data'),
    ('campaign',            'marketing'),   ('discount',      'marketing'),
    ('loyalty',             'marketing'),   ('promo',         'marketing'),
    ('financial_report',    'reports'),     ('market_insight','reports'),
    ('trends_analysis',     'reports'),     ('activity_log',  'reports'),
    ('download_report',     'reports'),     ('sales_report',  'reports'),
    ('transaction_summary', 'reports'),     ('transfer_report','reports'),
    ('requisition_report',  'reports'),     ('purchasing_report','reports'),
    ('inventory_log',       'reports'),     ('inventory_low', 'reports'),
    ('profit_loss',         'reports'),     ('sales_summary', 'reports'),
    ('recipe',              'production'),  ('bom',           'production'),
    ('profile',             'settings_app'),('settings',      'settings_app'),
    ('system_status',       'settings_app'),('business',      'settings_app'),
    ('users',               'settings_app'),('about',         'settings_app'),
    ('contact',             'settings_app'),('pricing',       'settings_app'),
    ('search',              'settings_app'),('feature_matrix','settings_app'),
    ('permissions',         'settings_app'),
]

LEGACY_MODULE_PATTERNS = [
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
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    return None

def backup(p: Path) -> Path:
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:    rel = p.relative_to(BASE)
    except: rel = Path(p.name)
    dest = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    return dest

def find_root(source: str | None) -> Path:
    return Path(source).resolve() if source else BASE

def find_templates_dir(root: Path) -> Path | None:
    for candidate in [
        root / 'lumra_config' / 'templates',
        root / 'templates',
    ]:
        if candidate.exists():
            return candidate
    return None

def find_lumra_pages(root: Path) -> Path | None:
    tmpl = find_templates_dir(root)
    if tmpl:
        lp = tmpl / 'lumra_pages'
        if lp.exists():
            return lp
    for p in root.rglob('lumra_pages'):
        if p.is_dir():
            return p
    return None

def find_views_files(root: Path) -> list[Path]:
    lc = root / 'lumra_config'
    return sorted(lc.rglob('views.py')) if lc.exists() else []

def find_html_files(root: Path) -> list[Path]:
    tmpl = find_templates_dir(root)
    return list(tmpl.rglob('*.html')) if tmpl else []

def find_main_urls(root: Path) -> Path | None:
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

# ─────────────────────────────────────────────────────────────────────────────
# DISK INDEX — scan semua .html di disk, buat lookup: basename → full_path
# ─────────────────────────────────────────────────────────────────────────────

def build_disk_index(root: Path) -> dict[str, list[str]]:
    """
    Kembalikan dict: 'dashboard.html' → ['lumra_pages/sales/dashboard.html', ...]
    Satu basename bisa ada di beberapa lokasi (ambiguous).
    Path relatif terhadap templates dir.
    """
    tmpl = find_templates_dir(root)
    if not tmpl:
        return {}
    index: dict[str, list[str]] = {}
    for f in tmpl.rglob('*.html'):
        rel = str(f.relative_to(tmpl)).replace('\\', '/')
        bn  = f.name
        index.setdefault(bn, []).append(rel)
    return index

def resolve_template_path(
    current_path: str,
    disk_index: dict[str, list[str]],
) -> str | None:
    """
    Cari path yang benar untuk current_path.

    Prioritas:
    1. TEMPLATE_REGISTRY (rename map manual)
    2. Disk index: kalau ada persis satu file dengan nama itu → pakai
    3. None = tidak bisa ditentukan otomatis
    """
    norm = current_path.replace('\\', '/')

    # Semua variasi key yang mungkin ada di registry
    basename = norm.split('/')[-1]
    for key in [norm, norm.removeprefix('lumra_pages/'), basename]:
        if key in TEMPLATE_REGISTRY:
            correct = TEMPLATE_REGISTRY[key]
            return correct if correct != norm else None

    # 2. Disk index — satu-satunya file dengan nama itu
    if basename in disk_index:
        hits = disk_index[basename]
        if len(hits) == 1:
            correct = hits[0]
            return correct if correct != norm else None
    return None

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Fix render() di views.py
# ─────────────────────────────────────────────────────────────────────────────

RENDER_RE = re.compile(
    r"""(render\s*\(\s*\w+\s*,\s*"""
    r"""|TemplateResponse\s*\(\s*\w+\s*,\s*"""
    r"""|get_template\s*\("""
    r"""|loader\.get_template\s*\()"""
    r"""(['"])([^'"]+\.html)\2""",
)

def scan_views(root: Path, disk_index: dict) -> list[dict]:
    results = []
    for py in find_views_files(root):
        src = read_file(py)
        if not src:
            continue
        changes = []
        for m in RENDER_RE.finditer(src):
            current = m.group(3).replace('\\', '/')
            correct = resolve_template_path(current, disk_index)
            if correct and correct != current:
                changes.append({'old': current, 'new': correct})
        if changes:
            try:    rel = str(py.relative_to(root))
            except: rel = str(py)
            results.append({'file': py, 'rel': rel, 'changes': changes})
    return results

def apply_views(results: list[dict], log: list):
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
        print(f'  {OK} {item["rel"]}  ({len(item["changes"])} render path difix)')
        for c in item['changes']:
            print(f'       {DIM}{c["old"]}{RST}')
            print(f'       {G}→ {c["new"]}{RST}')
    return total

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Fix lazy_view() di urls.py
# ─────────────────────────────────────────────────────────────────────────────

LAZY_RE  = re.compile(r"""lazy_view\s*\(\s*['"]([^'"]+)['"]\s*\)""")
DEF_RE   = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)

def is_legacy(dotted: str) -> bool:
    return any(dotted.startswith(p + '.') for p in LEGACY_MODULE_PATTERNS)

def route_func(func_name: str) -> str | None:
    fn = func_name.lower()
    for pat, mod in FUNC_MODULE_ROUTING:
        if pat in fn:
            return mod
    return None

def collect_view_funcs(root: Path) -> dict[str, set[str]]:
    result = {}
    lc = root / 'lumra_config'
    if not lc.exists():
        return result
    for vf in lc.rglob('views.py'):
        src = read_file(vf)
        if not src:
            continue
        try:    rel = str(vf.relative_to(root).with_suffix('').as_posix()).replace('/', '.')
        except: continue
        result[rel] = set(DEF_RE.findall(src))
    return result

def build_correct_lazy(func_name: str, view_funcs: dict) -> str | None:
    mod = route_func(func_name)
    if mod:
        candidate = f'lumra_config.{mod}.views'
        # Verifikasi fungsi ada, atau pakai routing saja
        if candidate in view_funcs and func_name in view_funcs[candidate]:
            return f'{candidate}.{func_name}'
        if candidate in view_funcs:
            return f'{candidate}.{func_name}'
        # Fallback scan semua
        for mod_path, funcs in view_funcs.items():
            if func_name in funcs:
                return f'{mod_path}.{func_name}'
        return f'lumra_config.{mod}.views.{func_name}'
    # Scan semua views kalau tidak ada di routing table
    for mod_path, funcs in view_funcs.items():
        if func_name in funcs:
            return f'{mod_path}.{func_name}'
    return None

def scan_lazy_views(root: Path) -> dict:
    urls_path  = find_main_urls(root)
    view_funcs = collect_view_funcs(root)
    fixable    = []
    unfixable  = []

    if not urls_path:
        return {'urls_path': None, 'fixable': [], 'unfixable': ['urls.py tidak ditemukan'],
                'view_funcs': view_funcs}

    src = read_file(urls_path)
    if not src:
        return {'urls_path': urls_path, 'fixable': [], 'unfixable': [],
                'view_funcs': view_funcs}

    for m in LAZY_RE.finditer(src):
        dotted    = m.group(1)
        func_name = dotted.rsplit('.', 1)[-1]
        if not is_legacy(dotted):
            continue
        correct = build_correct_lazy(func_name, view_funcs)
        if correct:
            fixable.append({'old': dotted, 'new': correct})
        else:
            unfixable.append(dotted)

    return {'urls_path': urls_path, 'fixable': fixable,
            'unfixable': unfixable, 'view_funcs': view_funcs}

def apply_lazy_views(data: dict, log: list) -> int:
    urls_path = data['urls_path']
    if not urls_path or not data['fixable']:
        return 0
    src = read_file(urls_path)
    bak = backup(urls_path)

    def replacer(m):
        dotted    = m.group(1)
        func_name = dotted.rsplit('.', 1)[-1]
        if not is_legacy(dotted):
            return m.group(0)
        correct = build_correct_lazy(func_name, data['view_funcs'])
        if not correct:
            return m.group(0)
        q = "'" if f"'{dotted}'" in m.group(0) else '"'
        return m.group(0).replace(f'{q}{dotted}{q}', f'{q}{correct}{q}', 1)

    new_src = LAZY_RE.sub(replacer, src)
    urls_path.write_text(new_src, encoding='utf-8')
    log.append({'step': 2, 'file': str(urls_path), 'backup': str(bak)})

    n = len(data['fixable'])
    try:    rel = str(urls_path.relative_to(BASE))
    except: rel = str(urls_path)
    print(f'  {OK} {rel}  ({n} lazy_view path difix)')
    for c in data['fixable']:
        print(f'       {DIM}{c["old"]}{RST}')
        print(f'       {G}→ {c["new"]}{RST}')
    return n

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Fix {% include %} / {% extends %} di HTML
# ─────────────────────────────────────────────────────────────────────────────

INCLUDE_RE = re.compile(
    r"""({%-?\s*(?:include|extends)\s+)(['"])([^'"]+\.html)\2""",
    re.IGNORECASE,
)

def scan_html_includes(root: Path, disk_index: dict) -> list[dict]:
    results = []
    for html in find_html_files(root):
        src = read_file(html)
        if not src:
            continue
        changes = []
        for m in INCLUDE_RE.finditer(src):
            current = m.group(3).replace('\\', '/')
            correct = resolve_template_path(current, disk_index)
            if correct and correct != current:
                changes.append({'old': current, 'new': correct})
        if changes:
            try:    rel = str(html.relative_to(root))
            except: rel = str(html)
            results.append({'file': html, 'rel': rel, 'changes': changes})
    return results

def apply_html_includes(results: list[dict], log: list) -> int:
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
        print(f'  {OK} {item["rel"]}  ({len(item["changes"])} include/extends difix)')
        for c in item['changes']:
            print(f'       {DIM}{c["old"]}{RST}')
            print(f'       {G}→ {c["new"]}{RST}')
    return total

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Fix import hilang di urls.py
# ─────────────────────────────────────────────────────────────────────────────

IMPORT_RE = re.compile(r'^from\s+django\.urls\s+import\s+(.+)$', re.MULTILINE)

def scan_missing_imports(root: Path) -> dict:
    urls_path = find_main_urls(root)
    if not urls_path:
        return {'urls_path': None, 'missing': [], 'existing_line': None, 'existing_names': []}

    src = read_file(urls_path)
    if not src:
        return {'urls_path': urls_path, 'missing': [], 'existing_line': None, 'existing_names': []}

    m = IMPORT_RE.search(src)
    existing_line  = m.group(0) if m else None
    existing_names = []
    if m:
        raw = re.sub(r'\\\n|[()]', ' ', m.group(1))
        existing_names = [n.strip() for n in raw.split(',') if n.strip()]

    missing = []
    for name in DJANGO_URLS_NAMES:
        if re.search(rf'\b{name}\s*\(', src) and name not in existing_names:
            missing.append(name)

    return {
        'urls_path'     : urls_path,
        'missing'       : missing,
        'existing_line' : existing_line,
        'existing_names': existing_names,
        'src'           : src,
    }

def apply_missing_imports(data: dict, log: list) -> int:
    if not data['missing'] or not data['urls_path']:
        return 0

    urls_path = data['urls_path']
    src       = data['src']
    missing   = data['missing']

    if data['existing_line']:
        order     = ['path', 'include', 're_path', 'register_converter']
        all_names = data['existing_names'] + [n for n in missing if n not in data['existing_names']]
        all_names.sort(key=lambda x: order.index(x) if x in order else 99)
        new_import = f"from django.urls import {', '.join(all_names)}"
        new_src    = src.replace(data['existing_line'], new_import, 1)
        desc       = f"expanded → {new_import}"
    else:
        new_line = f"from django.urls import {', '.join(sorted(missing))}"
        insert_re = re.compile(r'^(from django\b.*|import django\b.*)$', re.MULTILINE)
        matches   = list(insert_re.finditer(src))
        if matches:
            pos     = matches[-1].end()
            new_src = src[:pos] + '\n' + new_line + src[pos:]
        else:
            new_src = new_line + '\n' + src
        desc = f"added: {new_line}"

    bak = backup(urls_path)
    urls_path.write_text(new_src, encoding='utf-8')
    log.append({'step': 4, 'file': str(urls_path), 'backup': str(bak)})

    try:    rel = str(urls_path.relative_to(BASE))
    except: rel = str(urls_path)
    print(f'  {OK} {rel}')
    print(f'       {G}{desc}{RST}')
    return len(missing)

# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW
# ─────────────────────────────────────────────────────────────────────────────

def run_preview(root: Path, steps: set[int]):
    disk_index = build_disk_index(root)

    if 1 in steps:
        sep('STEP 1 — render() di views.py')
        results = scan_views(root, disk_index)
        if not results:
            print(f'  {OK} Semua render() sudah benar.')
        for item in results:
            print(f'\n  {FX} {item["rel"]}')
            for c in item['changes']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}→ {c["new"]}{RST}')

    if 2 in steps:
        sep('STEP 2 — lazy_view() di urls.py')
        data = scan_lazy_views(root)
        if not data['fixable'] and not data['unfixable']:
            print(f'  {OK} Semua lazy_view() sudah benar.')
        if data['fixable']:
            print(f'  {FX} {len(data["fixable"])} path akan difix:')
            for c in data['fixable']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}→ {c["new"]}{RST}')
        if data['unfixable']:
            print(f'  {WN} {len(data["unfixable"])} tidak bisa auto-fix (perlu manual):')
            for u in data['unfixable']:
                print(f'       {R}{u}{RST}')

    if 3 in steps:
        sep('STEP 3 — include/extends di HTML')
        results = scan_html_includes(root, disk_index)
        if not results:
            print(f'  {OK} Semua include/extends sudah benar.')
        for item in results:
            print(f'\n  {FX} {item["rel"]}')
            for c in item['changes']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}→ {c["new"]}{RST}')

    if 4 in steps:
        sep('STEP 4 — Import hilang di urls.py')
        data = scan_missing_imports(root)
        if not data['missing']:
            print(f'  {OK} Semua import django.urls sudah lengkap.')
        else:
            print(f'  {FX} Akan ditambahkan: {G}{", ".join(data["missing"])}{RST}')

    sep()
    print(f'  Jalankan dengan  {C}--apply{RST}  untuk menerapkan.\n')

# ─────────────────────────────────────────────────────────────────────────────
# APPLY
# ─────────────────────────────────────────────────────────────────────────────

def run_apply(root: Path, steps: set[int], yes: bool):
    run_preview(root, steps)

    if not yes:
        try:
            confirm = input('  Terapkan semua perbaikan? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.')
            return
        if confirm != 'y':
            print('  Dibatalkan.')
            return

    log        = []
    disk_index = build_disk_index(root)
    total      = {'views': 0, 'lazy': 0, 'html': 0, 'imports': 0}

    if 1 in steps:
        sep('STEP 1 — Fix render()')
        results = scan_views(root, disk_index)
        if results:
            total['views'] = apply_views(results, log)
        else:
            print(f'  {OK} Tidak ada yang perlu difix.')

    if 2 in steps:
        sep('STEP 2 — Fix lazy_view()')
        data = scan_lazy_views(root)
        if data['fixable']:
            total['lazy'] = apply_lazy_views(data, log)
        else:
            print(f'  {OK} Tidak ada yang perlu difix.')
        if data['unfixable']:
            print(f'  {WN} {len(data["unfixable"])} tidak bisa auto-fix (perlu manual):')
            for u in data['unfixable']:
                print(f'       {DIM}{u}{RST}')

    if 3 in steps:
        sep('STEP 3 — Fix include/extends')
        results = scan_html_includes(root, disk_index)
        if results:
            total['html'] = apply_html_includes(results, log)
        else:
            print(f'  {OK} Tidak ada yang perlu difix.')

    if 4 in steps:
        sep('STEP 4 — Fix import urls.py')
        data = scan_missing_imports(root)
        if data['missing']:
            total['imports'] = apply_missing_imports(data, log)
        else:
            print(f'  {OK} Semua import sudah lengkap.')

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    sep()
    grand_total = sum(total.values())
    if grand_total:
        print(f'  {OK} Selesai!')
        print(f'     render()      : {total["views"]} fix')
        print(f'     lazy_view()   : {total["lazy"]} fix')
        print(f'     include/extends: {total["html"]} fix')
        print(f'     import        : {total["imports"]} fix')
        print(f'  {DIM}Rollback: python lumra_fix_master.py --undo{RST}')
    else:
        print(f'  {OK} Tidak ada yang perlu diperbaiki — project sudah bersih.')
    print()

# ─────────────────────────────────────────────────────────────────────────────
# UNDO
# ─────────────────────────────────────────────────────────────────────────────

def run_undo():
    if not LOG_FILE.exists():
        print(f'\n  {WN} Log tidak ditemukan.\n')
        return
    with open(LOG_FILE) as f:
        log = json.load(f)
    restored = 0
    for entry in log:
        orig = Path(entry['file'])
        bak  = Path(entry['backup'])
        if bak.exists():
            shutil.copy2(bak, orig)
            restored += 1
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
        description='Lumra ERP — Master Fix Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps:
  1  render() / TemplateResponse() path salah di views.py
  2  lazy_view() modul salah di urls.py
  3  include/extends path salah di .html
  4  import hilang di urls.py

Contoh:
  python lumra_fix_master.py                     → preview semua
  python lumra_fix_master.py --apply             → fix semua
  python lumra_fix_master.py --apply --step 1    → fix hanya render()
  python lumra_fix_master.py --apply --yes       → tanpa konfirmasi
  python lumra_fix_master.py --undo              → rollback
  python lumra_fix_master.py --source D:\\Project
        """
    )
    parser.add_argument('--apply',  action='store_true')
    parser.add_argument('--yes',    action='store_true')
    parser.add_argument('--undo',   action='store_true')
    parser.add_argument('--step',   type=int, nargs='+', choices=[1,2,3,4])
    parser.add_argument('--source', type=str, default=None)
    args  = parser.parse_args()
    root  = find_root(args.source)
    steps = set(args.step) if args.step else {1, 2, 3, 4}

    print(f'\n{B}{"═"*64}')
    print(f'  {W}Lumra ERP — Master Fix Script{RST}')
    print(f'{B}{"═"*64}{RST}')
    print(f'  Root  : {DIM}{root}{RST}')
    print(f'  Steps : {C}{sorted(steps)}{RST}')
    print(f'  Mode  : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}\n')

    if args.undo:
        run_undo()
    elif args.apply:
        run_apply(root, steps, yes=args.yes)
    else:
        run_preview(root, steps)

if __name__ == '__main__':
    main()