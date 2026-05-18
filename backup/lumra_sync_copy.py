"""
lumra_sync.py — Lumra ERP · Django Sync Tool
=============================================
Satu script untuk menyelesaikan semua masalah pasca-migrasi template:

  1. Fix NoReverseMatch  → pastikan django_browser_reload + semua namespace benar di urls.py
  2. Fix render() paths  → update 'dashboard.html' → 'sales/dashboard.html' di views.py
  3. Fix {% include %}   → update 'navbar.html' → 'base/navbar.html' di semua .html
  4. Fix lazy_view paths → 'lumra_config.views.X' → 'lumra_config.MODUL.views.X' di urls.py
  5. Check akhir         → jalankan `manage.py check` dan laporkan hasilnya

Penggunaan:
    python lumra_sync.py                    → preview semua (AMAN)
    python lumra_sync.py --apply            → terapkan semua fix
    python lumra_sync.py --apply --step 1   → hanya step tertentu (1-5)
    python lumra_sync.py --apply --yes      → tanpa konfirmasi
    python lumra_sync.py --undo             → rollback dari backup
    python lumra_sync.py --source D:/path  → override root project
"""

import os, re, sys, shutil, json, argparse, subprocess
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / '.lumra_sync_backup'
LOG_FILE   = BASE_DIR / '.lumra_sync_log.json'

# Semua warna terminal
G  = '\033[92m'   # hijau
Y  = '\033[93m'   # kuning
R  = '\033[91m'   # merah
B  = '\033[94m'   # biru
C  = '\033[96m'   # cyan
W  = '\033[97m'   # putih tebal
DIM= '\033[2m'
RST= '\033[0m'
OK = f'{G}✅{RST}'
WN = f'{Y}⚠️ {RST}'
ER = f'{R}❌{RST}'
FX = f'{C}🔧{RST}'

# ─────────────────────────────────────────────────────────────────────────────
# MODULE MAP  (sumber tunggal kebenaran — sama persis dengan migrate_templates)
# ─────────────────────────────────────────────────────────────────────────────

MODULE_MAP = {
    'auth_app': [
        'login', 'logout', 'register', 'password',
    ],
    'sales': [
        'dashboard', 'pos', 'point_of_sale', 'point-of-sale',
        'notification', 'sales_history', 'sales_performance',
        'sales_products', 'purchasing',
    ],
    'master_data': [
        'product', 'categor', 'unit', 'vendor', 'supplier',
        'customer', 'location', 'stock_opname', 'opname',
    ],
    'inventory': [
        'stock_movement', 'stock_planning', 'add_stock',
        'export_stock', 'supplier_price', 'import_product',
        'inventory',
    ],
    'marketing': [
        'campaign', 'discount', 'loyalty', 'promo', 'voucher',
    ],
    'reports': [
        'report', 'insight', 'financial', 'market_insight',
        'trends', 'activity_log', 'transaction_summary',
        'transfer_report', 'requisition_report', 'purchasing_report',
        'profit_loss', 'sales_by_', 'sales_summary',
    ],
    'production': [
        'recipe', 'bom', 'bill_of_material', 'production',
    ],
    'settings_app': [
        'profile', 'settings', 'system_status', 'business',
        'users', 'user_role', 'about', 'contact', 'pricing', 'search',
        'feature_matrix', 'permissions',
    ],
    'base': [
        'navbar', 'sidebar', 'footer', 'modal', 'breadcrumb',
        'pagination', 'alert', 'toast', 'partials', '_partial',
        'layout', 'error', '404', '500',
    ],
}

# Template yang tidak boleh diubah path-nya
PROTECTED_TEMPLATES = {'base.html'}

# Komponen base/ yang biasa di-include dari HTML lain
BASE_COMPONENTS = [
    'navbar', 'sidebar', 'footer', 'modal', 'breadcrumb',
    'pagination', 'alert', 'toast', 'layout',
]

# File urls.py utama yang perlu diperiksa
MAIN_URLS_CANDIDATES = [
    'lumra_system/urls.py',
    'lumra/urls.py',
    'config/urls.py',
    'urls.py',
]

# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

def detect_module(template_name: str) -> str | None:
    """Tentukan modul untuk template_name. None = jangan ubah."""
    if '/' in template_name or template_name in PROTECTED_TEMPLATES:
        return None
    stem = template_name.replace('.html', '').lower()
    for module, patterns in MODULE_MAP.items():
        for p in patterns:
            if p in stem:
                return module
    return None


def backup(filepath: Path) -> Path:
    """Buat backup sebelum modifikasi."""
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        rel  = filepath.relative_to(BASE_DIR)
    except ValueError:
        rel  = Path(filepath.name)
    dest = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, dest)
    return dest


def read_file(p: Path) -> str | None:
    for enc in ('utf-8', 'utf-8-sig', 'cp1252'):
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    return None


def write_file(p: Path, content: str):
    p.write_text(content, encoding='utf-8')


def sep(title: str = ''):
    line = '═' * 65
    if title:
        pad = (65 - len(title) - 2) // 2
        print(f'\n{B}{"═"*pad} {W}{title}{RST}{B} {"═"*(65-pad-len(title)-2)}{RST}')
    else:
        print(f'{DIM}{line}{RST}')


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Fix NoReverseMatch: django_browser_reload + namespace
# ─────────────────────────────────────────────────────────────────────────────

RELOAD_INCLUDE_OLD = re.compile(
    r'path\s*\(\s*["\']__reload__/["\']'
    r'\s*,\s*include\s*\(\s*["\']django_browser_reload\.urls["\']'
    r'(?!\s*,\s*namespace)',   # belum punya namespace
    re.IGNORECASE,
)

RELOAD_INCLUDE_NEW = (
    "path('__reload__/', include('django_browser_reload.urls',"
    " namespace='django_browser_reload'))"
)

def find_main_urls(root: Path) -> Path | None:
    for rel in MAIN_URLS_CANDIDATES:
        p = root / rel
        if p.exists():
            return p
    # fallback: cari urls.py yang mengandung 'urlpatterns'
    for p in root.rglob('urls.py'):
        if 'lumra_config' not in str(p):
            src = read_file(p)
            if src and 'urlpatterns' in src and 'admin' in src:
                return p
    return None


def step1_preview(root: Path) -> dict:
    urls_path = find_main_urls(root)
    result = {'urls_path': urls_path, 'needs_reload_fix': False, 'issues': []}

    if not urls_path:
        result['issues'].append('File urls.py utama tidak ditemukan')
        return result

    src = read_file(urls_path)
    if not src:
        result['issues'].append(f'Tidak bisa membaca {urls_path}')
        return result

    # Cek django_browser_reload
    if 'django_browser_reload' in src:
        if RELOAD_INCLUDE_OLD.search(src):
            result['needs_reload_fix'] = True
            result['issues'].append(
                "django_browser_reload include() tidak memiliki namespace='django_browser_reload'"
            )
        elif "namespace='django_browser_reload'" in src or 'namespace="django_browser_reload"' in src:
            pass  # sudah benar
        else:
            result['issues'].append(
                'django_browser_reload ditemukan tapi format include()-nya tidak dikenali — periksa manual'
            )
    else:
        result['issues'].append(
            f'{DIM}django_browser_reload tidak ditemukan di urls.py (mungkin tidak dipakai){RST}'
        )

    return result


def step1_apply(root: Path, log: list) -> bool:
    data = step1_preview(root)
    urls_path = data['urls_path']

    if not urls_path or not data['needs_reload_fix']:
        return False

    src     = read_file(urls_path)
    bak     = backup(urls_path)
    new_src = RELOAD_INCLUDE_OLD.sub(RELOAD_INCLUDE_NEW, src)
    write_file(urls_path, new_src)
    log.append({'type': 'step1', 'file': str(urls_path), 'backup': str(bak)})
    return True


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Fix render() / TemplateResponse() paths di views.py
# ─────────────────────────────────────────────────────────────────────────────

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


def fix_render_source(source: str) -> tuple[str, list]:
    changes = []

    def replacer(m):
        full, quote, tmpl = m.group(0), m.group(1), m.group(2)
        mod = detect_module(tmpl)
        if mod is None:
            return full
        new_tmpl = f'{mod}/{tmpl}'
        changes.append({'old': tmpl, 'new': new_tmpl})
        return full.replace(f'{quote}{tmpl}{quote}', f'{quote}{new_tmpl}{quote}', 1)

    return RENDER_RE.sub(replacer, source), changes


def get_views_files(root: Path) -> list[Path]:
    found = []
    lc = root / 'lumra_config'
    if lc.exists():
        found.extend(lc.rglob('views.py'))
    # legacy paths
    for rel in ['core/core/views.py', 'core/views.py']:
        p = root / rel
        if p.exists():
            found.append(p)
    return sorted(set(found))


def step2_preview(root: Path) -> dict:
    files   = get_views_files(root)
    result  = {'files': {}}
    for f in files:
        src = read_file(f)
        if not src:
            continue
        _, changes = fix_render_source(src)
        if changes:
            rel = f.relative_to(root) if f.is_relative_to(root) else f
            result['files'][str(rel)] = {'path': f, 'changes': changes}
    return result


def step2_apply(root: Path, log: list) -> int:
    data  = step2_preview(root)
    total = 0
    for rel, info in data['files'].items():
        fpath = info['path']
        src   = read_file(fpath)
        new_src, changes = fix_render_source(src)
        bak   = backup(fpath)
        write_file(fpath, new_src)
        log.append({'type': 'step2', 'file': str(fpath), 'backup': str(bak)})
        total += len(changes)
        print(f'  {OK} {rel}  ({len(changes)} path diperbarui)')
        for c in changes:
            print(f'       {DIM}{c["old"]}{RST}  →  {G}{c["new"]}{RST}')
    return total


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Fix {% include %} dan {% extends %} di semua .html
# ─────────────────────────────────────────────────────────────────────────────

def build_include_replacements() -> list[tuple[re.Pattern, str]]:
    """
    Buat list pasangan (pattern, replacement) untuk setiap komponen base/.
    Hanya menarget include/extends yang belum punya subfolder.
    """
    pairs = []
    for comp in BASE_COMPONENTS:
        # {% include 'navbar.html' %} atau {% include "navbar.html" %}
        for q in ('"', "'"):
            # Tangkap jika belum ada 'base/' prefix
            pat = re.compile(
                r"""({%-?\s*include\s+)"""
                + re.escape(q)
                + r"""(?!base/)"""
                + r"""(""" + re.escape(comp) + r"""[^"']*\.html)"""
                + re.escape(q),
                re.IGNORECASE,
            )
            rep = r'\g<1>' + q + r'base/\g<2>' + q
            pairs.append((pat, rep))
    return pairs

INCLUDE_PAIRS = build_include_replacements()


def fix_html_source(source: str) -> tuple[str, list]:
    changes = []
    result  = source
    for pat, rep in INCLUDE_PAIRS:
        new = pat.sub(rep, result)
        if new != result:
            # Cari semua yang berubah untuk logging
            for m in pat.finditer(result):
                changes.append({
                    'old': m.group(0).strip(),
                    'new': pat.sub(rep, m.group(0)).strip(),
                })
            result = new
    return result, changes


def get_html_files(root: Path) -> list[Path]:
    tmpl_root = root / 'lumra_config' / 'templates'
    if not tmpl_root.exists():
        return []
    # Semua .html di subfolder modul (bukan root templates langsung)
    return [
        p for p in tmpl_root.rglob('*.html')
        if p.parent != tmpl_root   # bukan file di root templates/
    ]


def step3_preview(root: Path) -> dict:
    files  = get_html_files(root)
    result = {'files': {}}
    for f in files:
        src = read_file(f)
        if not src:
            continue
        _, changes = fix_html_source(src)
        if changes:
            rel = f.relative_to(root) if f.is_relative_to(root) else f
            result['files'][str(rel)] = {'path': f, 'changes': changes}
    return result


def step3_apply(root: Path, log: list) -> int:
    data  = step3_preview(root)
    total = 0
    for rel, info in data['files'].items():
        fpath = info['path']
        src   = read_file(fpath)
        new_src, changes = fix_html_source(src)
        bak   = backup(fpath)
        write_file(fpath, new_src)
        log.append({'type': 'step3', 'file': str(fpath), 'backup': str(bak)})
        total += len(changes)
        print(f'  {OK} {rel}  ({len(changes)} include diperbarui)')
        for c in changes:
            print(f'       {DIM}{c["old"]}{RST}')
            print(f'       {G}{c["new"]}{RST}')
    return total


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Auto-fix lazy_view: lumra_config.views.X → lumra_config.MODUL.views.X
# ─────────────────────────────────────────────────────────────────────────────

LAZY_VIEW_RE = re.compile(
    r"""lazy_view\s*\(\s*['"]([^'"]+)['"]\s*\)""",
)

DEF_RE = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)

# ── Tabel routing fungsi → modul ─────────────────────────────────────────────
# Diprioritaskan dari atas ke bawah: lebih spesifik dulu.
# Format: (substring_in_func_name, target_module)
FUNC_MODULE_ROUTING: list[tuple[str, str]] = [
    # ── api (HARUS PALING ATAS — cegah api_dashboard → sales) ────────────────
    ('api_dashboard',          'api'),
    ('submit_requisition',     'api'),
    ('confirm_receipt',        'api'),
    ('submit_purchases',       'api'),
    ('get_location_stock',     'api'),

    # ── auth ──────────────────────────────────────────────────────────────────
    ('login',                  'auth_app'),
    ('logout',                 'auth_app'),
    ('register',               'auth_app'),

    # ── inventory (SEBELUM master_data — cegah products_import → master_data) ─
    ('supplier_price',         'inventory'),
    ('stock_movement',         'inventory'),
    ('stock_planning',         'inventory'),
    ('export_stock',           'inventory'),
    ('import_product',         'inventory'),
    ('products_import',        'inventory'),   # products_import_template
    ('import_template',        'inventory'),   # *_import_template
    ('stock_allocation',       'inventory'),
    ('approve_requisition',    'inventory'),

    # ── sales ─────────────────────────────────────────────────────────────────
    ('dashboard',              'sales'),
    ('pos',                    'sales'),
    ('notification',           'sales'),
    ('sales_history',          'sales'),
    ('sales_performance',      'sales'),
    ('sales_products',         'sales'),
    ('purchasing',             'sales'),

    # ── master_data ───────────────────────────────────────────────────────────
    ('product',                'master_data'),
    ('categor',                'master_data'),
    ('unit_',                  'master_data'),
    ('_unit',                  'master_data'),
    ('units_',                 'master_data'),
    ('vendor',                 'master_data'),
    ('customer',               'master_data'),
    ('location',               'master_data'),
    ('stock_opname',           'master_data'),
    ('opname',                 'master_data'),

    # ── marketing ─────────────────────────────────────────────────────────────
    ('campaign',               'marketing'),
    ('discount',               'marketing'),
    ('loyalty',                'marketing'),
    ('promo',                  'marketing'),

    # ── reports ───────────────────────────────────────────────────────────────
    ('financial_report',       'reports'),
    ('market_insight',         'reports'),
    ('trends_analysis',        'reports'),
    ('activity_log',           'reports'),
    ('download_report',        'reports'),
    ('export_trends',          'reports'),
    ('sales_report',           'reports'),
    ('transaction_summary',    'reports'),
    ('transfer_report',        'reports'),
    ('requisition_report',     'reports'),
    ('purchasing_report',      'reports'),
    ('inventory_log',          'reports'),
    ('inventory_low',          'reports'),
    ('inventory_stock',        'reports'),
    ('profit_loss',            'reports'),
    ('sales_by_',              'reports'),
    ('sales_summary',          'reports'),
    ('report_',                'reports'),

    # ── production ────────────────────────────────────────────────────────────
    ('recipe',                 'production'),
    ('bom',                    'production'),

    # ── settings_app ──────────────────────────────────────────────────────────
    ('profile',                'settings_app'),
    ('settings',               'settings_app'),
    ('system_status',          'settings_app'),
    ('business',               'settings_app'),
    ('users',                  'settings_app'),
    ('user_role',              'settings_app'),
    ('about',                  'settings_app'),
    ('contact',                'settings_app'),
    ('pricing',                'settings_app'),
    ('search',                 'settings_app'),
    ('feature_matrix',         'settings_app'),
    ('permissions',            'settings_app'),
]

# Modul monolitik lama yang harus diganti
LEGACY_MODULE_PATTERNS = [
    'lumra_config.views',           # lumra_config.views.dashboard_view
    'lumra_config.views.inventory_views',   # sub-file lama
    'lumra_config.views.stock_movement_views',
    'lumra_config.views.api_views',
]


def route_func_to_module(func_name: str) -> str | None:
    """
    Tentukan modul tujuan untuk nama fungsi tertentu.
    Kembalikan nama modul atau None jika tidak dikenali.
    """
    fn = func_name.lower()
    for pattern, module in FUNC_MODULE_ROUTING:
        if pattern in fn:
            return module
    return None


def collect_view_functions(root: Path) -> dict[str, set[str]]:
    """Kembalikan dict: 'lumra_config.sales.views' → {func1, func2, ...}"""
    result: dict[str, set[str]] = {}
    lc = root / 'lumra_config'
    if not lc.exists():
        return result
    for vfile in lc.rglob('views.py'):
        src = read_file(vfile)
        if not src:
            continue
        try:
            rel   = vfile.relative_to(root)
            parts = list(rel.with_suffix('').parts)
            mod   = '.'.join(parts)
        except ValueError:
            continue
        result[mod] = set(DEF_RE.findall(src))
    return result


def is_legacy_path(dotted: str) -> bool:
    """True jika path masih pakai modul monolitik lama."""
    for legacy in LEGACY_MODULE_PATTERNS:
        if dotted.startswith(legacy + '.'):
            return True
    return False


def build_correct_path(func_name: str, view_funcs: dict[str, set[str]]) -> str | None:
    """
    Cari path yang benar untuk func_name:
    1. Coba cocokkan dari FUNC_MODULE_ROUTING
    2. Verifikasi fungsi benar-benar ada di views.py modul tersebut
    3. Fallback: scan semua views.py untuk mencari fungsi
    """
    # Strategi 1: routing berdasarkan nama
    module = route_func_to_module(func_name)
    if module:
        candidate = f'lumra_config.{module}.views'
        if candidate in view_funcs and func_name in view_funcs[candidate]:
            return f'{candidate}.{func_name}'
        # Modul tepat tapi fungsi belum ada (mungkin belum dimigrate) → tetap pakai
        if candidate in view_funcs:
            return f'{candidate}.{func_name}'

    # Strategi 2: scan semua views.py yang ada
    for mod_path, funcs in view_funcs.items():
        if func_name in funcs:
            return f'{mod_path}.{func_name}'

    # Strategi 3: routing saja tanpa verifikasi (fungsi belum ada tapi path benar)
    if module:
        return f'lumra_config.{module}.views.{func_name}'

    return None


def fix_lazy_view_source(source: str, view_funcs: dict[str, set[str]]) -> tuple[str, list]:
    """
    Ganti semua lazy_view('lumra_config.views.X') → lazy_view('lumra_config.MODUL.views.X')
    Kembalikan (new_source, list_of_changes).
    """
    changes  = []
    result   = source

    def replacer(m: re.Match) -> str:
        full_match = m.group(0)
        dotted     = m.group(1)

        # Hanya proses jika path masih legacy/salah
        if not is_legacy_path(dotted):
            return full_match

        # Ambil nama fungsi (bagian terakhir setelah titik terakhir)
        func_name = dotted.rsplit('.', 1)[-1]

        correct = build_correct_path(func_name, view_funcs)
        if not correct or correct == dotted:
            return full_match

        # Deteksi quote yang dipakai (single atau double)
        quote = "'" if f"'{dotted}'" in full_match else '"'
        new_match = full_match.replace(
            f'{quote}{dotted}{quote}',
            f'{quote}{correct}{quote}',
            1,
        )
        changes.append({'old': dotted, 'new': correct})
        return new_match

    result = LAZY_VIEW_RE.sub(replacer, result)
    return result, changes


def step4_preview(root: Path) -> dict:
    urls_path  = find_main_urls(root)
    view_funcs = collect_view_functions(root)
    result     = {
        'urls_path'    : urls_path,
        'view_funcs'   : view_funcs,
        'fixable'      : [],   # bisa diperbaiki otomatis
        'unfixable'    : [],   # tidak dikenali sama sekali
        'already_ok'   : 0,
    }

    if not urls_path:
        result['unfixable'].append('urls.py utama tidak ditemukan')
        return result

    src = read_file(urls_path)
    if not src:
        result['unfixable'].append(f'Tidak bisa membaca {urls_path}')
        return result

    for m in LAZY_VIEW_RE.finditer(src):
        dotted    = m.group(1)
        func_name = dotted.rsplit('.', 1)[-1]

        if not is_legacy_path(dotted):
            result['already_ok'] += 1
            continue

        correct = build_correct_path(func_name, view_funcs)
        if correct:
            result['fixable'].append({'old': dotted, 'new': correct})
        else:
            result['unfixable'].append(
                f'Tidak bisa routing otomatis: {dotted}'
            )

    return result


def step4_apply(root: Path, log: list) -> int:
    data       = step4_preview(root)
    urls_path  = data.get('urls_path')
    view_funcs = data.get('view_funcs', {})

    if not urls_path or not data['fixable']:
        return 0

    src                = read_file(urls_path)
    new_src, changes   = fix_lazy_view_source(src, view_funcs)

    if not changes:
        return 0

    bak = backup(urls_path)
    write_file(urls_path, new_src)
    log.append({'type': 'step4', 'file': str(urls_path), 'backup': str(bak)})

    rel = urls_path.relative_to(root) if urls_path.is_relative_to(root) else urls_path
    print(f'  {OK}  {rel}  ({len(changes)} lazy_view path diperbaiki)')
    for c in changes:
        print(f'       {Y}{c["old"]}{RST}')
        print(f'       {G}{c["new"]}{RST}')

    return len(changes)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Jalankan manage.py check
# ─────────────────────────────────────────────────────────────────────────────

def find_manage_py(root: Path) -> Path | None:
    p = root / 'manage.py'
    if p.exists():
        return p
    for found in root.rglob('manage.py'):
        return found
    return None


def step5_run(root: Path) -> dict:
    manage = find_manage_py(root)
    if not manage:
        return {'success': False, 'output': 'manage.py tidak ditemukan'}

    try:
        result = subprocess.run(
            [sys.executable, str(manage), 'check', '--deploy'],
            cwd=str(manage.parent),
            capture_output=True, text=True, timeout=60,
        )
        output   = (result.stdout + result.stderr).strip()
        success  = result.returncode == 0
        # check --deploy bisa warn tentang security, yang normal di dev
        # coba check biasa jika --deploy gagal karena config
        if not success and 'DJANGO_SETTINGS_MODULE' in output:
            result2 = subprocess.run(
                [sys.executable, str(manage), 'check'],
                cwd=str(manage.parent),
                capture_output=True, text=True, timeout=60,
            )
            output  = (result2.stdout + result2.stderr).strip()
            success = result2.returncode == 0
        return {'success': success, 'output': output}
    except subprocess.TimeoutExpired:
        return {'success': False, 'output': 'Timeout saat menjalankan manage.py check'}
    except Exception as e:
        return {'success': False, 'output': str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# UNDO
# ─────────────────────────────────────────────────────────────────────────────

def undo_all():
    if not LOG_FILE.exists():
        print(f'\n{ER}  Log tidak ditemukan. Tidak ada yang bisa di-undo.\n')
        return

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log = json.load(f)

    if not log:
        print(f'\n{OK}  Log kosong — tidak ada perubahan untuk di-rollback.\n')
        return

    restored = 0
    for entry in log:
        fpath  = Path(entry['file'])
        backup = Path(entry['backup'])
        if not backup.exists():
            print(f'  {WN} Backup tidak ada: {backup}')
            continue
        shutil.copy2(backup, fpath)
        restored += 1
        print(f'  {FX} Restored: {fpath.name}')

    LOG_FILE.unlink(missing_ok=True)
    print(f'\n  {OK}  {restored} file dikembalikan ke kondisi semula.\n')


# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW TERPADU
# ─────────────────────────────────────────────────────────────────────────────

def run_preview(root: Path, steps: set[int]):

    # ── STEP 1 ────────────────────────────────────────────────────────────────
    if 1 in steps:
        sep('STEP 1 — NoReverseMatch: Browser Reload & Namespace')
        d = step1_preview(root)
        if d.get('urls_path'):
            print(f'  {DIM}urls.py   : {d["urls_path"].relative_to(root)}{RST}')
        for issue in d.get('issues', []):
            icon = FX if 'namespace' in issue else WN
            print(f'  {icon}  {issue}')
        if not d.get('issues'):
            print(f'  {OK}  Tidak ada masalah namespace ditemukan.')

    # ── STEP 2 ────────────────────────────────────────────────────────────────
    if 2 in steps:
        sep('STEP 2 — render() Template Paths di views.py')
        d = step2_preview(root)
        if not d['files']:
            print(f'  {OK}  Semua render() sudah menggunakan path subfolder.')
        for rel, info in d['files'].items():
            print(f'\n  {FX}  {rel}')
            for c in info['changes']:
                print(f'       {Y}{c["old"]:45s}{RST}  →  {G}{c["new"]}{RST}')

    # ── STEP 3 ────────────────────────────────────────────────────────────────
    if 3 in steps:
        sep('STEP 3 — {%% include %%} Components di HTML')
        d = step3_preview(root)
        if not d['files']:
            print(f'  {OK}  Semua include sudah menggunakan path base/.')
        for rel, info in d['files'].items():
            print(f'\n  {FX}  {rel}')
            for c in info['changes']:
                print(f'       {Y}{c["old"]}{RST}')
                print(f'       {G}{c["new"]}{RST}')

    # ── STEP 4 ────────────────────────────────────────────────────────────────
    if 4 in steps:
        sep('STEP 4 — Auto-fix lazy_view Paths di urls.py')
        d = step4_preview(root)
        if d.get('urls_path'):
            try:
                rel = d['urls_path'].relative_to(root)
            except ValueError:
                rel = d['urls_path']
            print(f'  {DIM}urls.py   : {rel}{RST}')

        if d['already_ok'] and not d['fixable'] and not d['unfixable']:
            print(f'  {OK}  Semua {d["already_ok"]} lazy_view sudah menggunakan path modul yang benar.')
        else:
            if d['already_ok']:
                print(f'  {DIM}  {d["already_ok"]} referensi sudah benar (tidak diubah){RST}')
            if d['fixable']:
                print(f'  {FX}  {len(d["fixable"])} path akan diperbaiki otomatis:')
                for item in d['fixable']:
                    print(f'       {Y}{item["old"]}{RST}')
                    print(f'       {G}{item["new"]}{RST}')
            if d['unfixable']:
                print(f'\n  {WN}  {len(d["unfixable"])} tidak bisa diperbaiki otomatis (perlu manual):')
                for msg in d['unfixable']:
                    print(f'       {R}{msg}{RST}')

    # ── STEP 5 ────────────────────────────────────────────────────────────────
    if 5 in steps:
        sep('STEP 5 — manage.py check')
        print(f'  {DIM}Menjalankan manage.py check ...{RST}')
        d = step5_run(root)
        icon = OK if d['success'] else ER
        print(f'  {icon}  {d["output"]}')

    sep()
    print(f'  Gunakan  {C}--apply{RST}  untuk menerapkan semua perbaikan.\n')


# ─────────────────────────────────────────────────────────────────────────────
# APPLY TERPADU
# ─────────────────────────────────────────────────────────────────────────────

def run_apply(root: Path, steps: set[int], yes: bool):
    # Preview dulu
    run_preview(root, steps)

    if not yes:
        try:
            confirm = input(f'  Terapkan semua perbaikan di atas? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.\n')
            return
        if confirm != 'y':
            print('  Dibatalkan.\n')
            return

    log       = []
    any_change = False

    # ── STEP 1 ────────────────────────────────────────────────────────────────
    if 1 in steps:
        sep('STEP 1 — Fix Browser Reload Namespace')
        d = step1_preview(root)
        if d.get('needs_reload_fix'):
            fixed = step1_apply(root, log)
            if fixed:
                any_change = True
                print(f"  {OK}  namespace='django_browser_reload' ditambahkan.")
            else:
                print(f'  {WN}  Tidak ada perubahan diterapkan.')
        else:
            print(f'  {OK}  Tidak ada yang perlu diperbaiki.')

    # ── STEP 2 ────────────────────────────────────────────────────────────────
    if 2 in steps:
        sep('STEP 2 — Fix render() Paths')
        total = step2_apply(root, log)
        if total == 0:
            print(f'  {OK}  Tidak ada perubahan diperlukan.')
        else:
            any_change = True
            print(f'\n  Total: {total} path diperbarui.')

    # ── STEP 3 ────────────────────────────────────────────────────────────────
    if 3 in steps:
        sep('STEP 3 — Fix {%% include %%} HTML')
        total = step3_apply(root, log)
        if total == 0:
            print(f'  {OK}  Tidak ada perubahan diperlukan.')
        else:
            any_change = True
            print(f'\n  Total: {total} include diperbarui.')

    # ── STEP 4 — AUTO-FIX lazy_view paths ────────────────────────────────────
    if 4 in steps:
        sep('STEP 4 — Auto-fix lazy_view Paths di urls.py')
        d = step4_preview(root)
        if not d['fixable']:
            if d['already_ok']:
                print(f'  {OK}  Semua {d["already_ok"]} lazy_view sudah benar.')
            else:
                print(f'  {OK}  Tidak ada yang perlu diperbaiki.')
        else:
            total = step4_apply(root, log)
            if total:
                any_change = True
                print(f'\n  Total: {total} lazy_view path diperbarui.')
        if d.get('unfixable'):
            print(f'\n  {WN}  {len(d["unfixable"])} tidak bisa diperbaiki otomatis:')
            for msg in d['unfixable']:
                print(f'       {R}{msg}{RST}')
            print(f'  {DIM}  Periksa dan perbaiki nama-nama di atas secara manual.{RST}')

    # ── STEP 5 ────────────────────────────────────────────────────────────────
    if 5 in steps:
        sep('STEP 5 — manage.py check')
        print(f'  {DIM}Menjalankan manage.py check ...{RST}')
        d = step5_run(root)
        icon = OK if d['success'] else ER
        for line in d['output'].splitlines():
            print(f'  {icon if "System check" in line else DIM}  {line}{RST}')
        if d['success']:
            print(f'\n  {OK}  Tidak ada error Django. Proyek siap dijalankan!\n')
        else:
            print(f'\n  {ER}  Ada error Django. Periksa output di atas.\n')

    # ── Simpan log ────────────────────────────────────────────────────────────
    if any_change:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        sep()
        print(f'  {OK}  Selesai. Backup tersimpan di: {BACKUP_DIR}')
        print(f'  {FX}  Rollback: {C}python lumra_sync.py --undo{RST}\n')
    else:
        sep()
        print(f'  {OK}  Tidak ada perubahan yang perlu diterapkan.\n')


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP — Django Sync Tool (URL + View + Template)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Langkah yang dilakukan:
  1. Fix NoReverseMatch  → tambah namespace django_browser_reload di urls.py
  2. Fix render() paths  → 'dashboard.html' → 'sales/dashboard.html' di views.py
  3. Fix {% include %}   → 'navbar.html' → 'base/navbar.html' di semua .html
  4. Fix lazy_view paths → rewrite 'lumra_config.views.X' → 'lumra_config.MODUL.views.X'
  5. manage.py check     → verifikasi akhir Django

Contoh:
  python lumra_sync.py                      → preview semua langkah
  python lumra_sync.py --apply              → terapkan semua (+ konfirmasi)
  python lumra_sync.py --apply --step 2 3  → hanya step 2 dan 3
  python lumra_sync.py --apply --yes       → tanpa konfirmasi
  python lumra_sync.py --undo              → rollback dari backup
  python lumra_sync.py --source D:/Project → override root project
        """
    )
    parser.add_argument('--apply',  action='store_true', help='Terapkan perubahan')
    parser.add_argument('--yes',    action='store_true', help='Skip konfirmasi')
    parser.add_argument('--undo',   action='store_true', help='Rollback dari backup')
    parser.add_argument('--step',   type=int, nargs='+', choices=[1,2,3,4,5],
                        help='Hanya jalankan step tertentu (misal: --step 2 3)')
    parser.add_argument('--source', type=str, default=None,
                        help='Override path root project')
    args = parser.parse_args()

    # Tentukan root
    root = Path(args.source).resolve() if args.source else BASE_DIR
    steps = set(args.step) if args.step else {1, 2, 3, 4, 5}

    # Header
    print(f'\n{B}{"═"*65}')
    print(f'  {W}Lumra ERP — Django Sync Tool{RST}')
    print(f'{B}{"═"*65}{RST}')
    print(f'  Root    : {DIM}{root}{RST}')
    print(f'  Steps   : {C}{sorted(steps)}{RST}')
    print(f'  Mode    : {G}{"APPLY" if args.apply else "PREVIEW"}{RST}\n')

    if args.undo:
        undo_all()
    elif args.apply:
        run_apply(root, steps, yes=args.yes)
    else:
        run_preview(root, steps)


if __name__ == '__main__':
    main()