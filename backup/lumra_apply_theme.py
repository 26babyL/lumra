"""
lumra_apply_theme.py
====================
Terapkan Lumra Design System ke semua file HTML:
  1. Inject <link> CSS ke base.html
  2. Tambah class tema di wrapper utama setiap halaman
     berdasarkan modul (sales, purchasing, inventory, dll)

Cara pakai:
  python lumra_apply_theme.py                    → preview (AMAN)
  python lumra_apply_theme.py --apply            → terapkan
  python lumra_apply_theme.py --apply --yes      → tanpa konfirmasi
  python lumra_apply_theme.py --undo             → rollback
  python lumra_apply_theme.py --source D:\\APPS\\Project\\lumra
  python lumra_apply_theme.py --report           → laporan tema per file
"""

import re, shutil, json, argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

BASE       = Path(__file__).resolve().parent
BACKUP_DIR = BASE / '.lumra_theme_backup'
LOG_FILE   = BASE / '.lumra_theme_log.json'

G  = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B  = '\033[94m'; C = '\033[96m'; W = '\033[97m'
DIM= '\033[2m';  RST= '\033[0m'
OK = f'{G}✅{RST}'; WN = f'{Y}⚠️ {RST}'; FX = f'{C}🔧{RST}'

# CSS file yang akan di-inject (relatif terhadap STATIC_URL)
CSS_STATIC_PATH = 'css/lumra_design_system.css'

# Tag yang akan disisipkan di base.html
CSS_LINK_TAG = f"{{% load static %}}\n<link rel=\"stylesheet\" href=\"{{% static '{CSS_STATIC_PATH}' %}}\">"
CSS_LINK_TAG_SIMPLE = f'<link rel="stylesheet" href="{{% static \'{CSS_STATIC_PATH}\' %}}">'

# ─────────────────────────────────────────────────────────────────────────────
# TEMA MAP
# Format: (class_tema, [substring_nama_file, ...])
# Urutan penting — lebih spesifik di atas
# ─────────────────────────────────────────────────────────────────────────────

THEME_MAP: list[tuple[str, list[str]]] = [
    # Auth — sebelum settings (login/register lebih spesifik)
    ('theme-auth', [
        'login', 'register', 'password',
    ]),
    # Purchasing / Vendor / Supplier — Ink Blue
    ('theme-purchase', [
        'purchasing', 'vendor_form', 'vendor_list', 'vendors_list',
        'vendor_create', 'vendor_update', 'vendor_delete',
        'supplier_price',
    ]),
    # Inventory / Stock — Forest Green
    ('theme-inventory', [
        'stock_overview', 'stock_movement', 'stock_planning',
        'stock_opname', 'stock_allocation',
        'product_list', 'product_detail', 'products_import',
        'inventory',
    ]),
    # Reports / Analytics — Violet
    ('theme-reports', [
        'report_', 'financial_report', 'market_insight', 'trends_analysis',
        'activity_log', 'transaction_summary', 'transfer_report',
        'requisition_report', 'purchasing_report', 'profit_loss',
        'sales_history', 'sales_performance', 'sales_report',
        'sales_by_', 'sales_summary', 'reporting', 'base_report',
    ]),
    # Marketing — Rose
    ('theme-marketing', [
        'campaign', 'discount', 'loyalty',
    ]),
    # Production / Recipe — Amber
    ('theme-production', [
        'recipe', 'bom', 'production',
    ]),
    # Master Data — Teal
    ('theme-master', [
        'customer', 'categories', 'category_form',
        'units_list', 'unit_form', 'location_list',
        'stock_opname_session',
    ]),
    # Settings / System — Slate
    ('theme-settings', [
        'settings', 'profile', 'users', 'user_roles', 'user_list',
        'business_', 'system_status', 'about', 'contact', 'search',
        'feature_matrix', 'permissions', 'pricing',
    ]),
    # Sales — Copper (default, paling umum — di bawah sendiri)
    ('theme-sales', [
        'dashboard', 'pos', 'notification', 'sales_intelligence',
        'sales_insight', 'purchasing_view',
    ]),
]

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
    for c in [root / 'lumra_config' / 'templates', root / 'templates']:
        if c.exists(): return c
    return None

def sep(title=''):
    pad = (66 - len(title) - 2) // 2 if title else 0
    if title:
        print(f'\n{B}{"═"*pad} {W}{title}{RST}{B} {"═"*(66-pad-len(title)-2)}{RST}')
    else:
        print(f'{DIM}{"═"*66}{RST}')

# ─────────────────────────────────────────────────────────────────────────────
# DETEKSI TEMA DARI NAMA FILE
# ─────────────────────────────────────────────────────────────────────────────

def detect_theme(filename: str) -> str | None:
    """
    Kembalikan class tema berdasarkan nama file.
    None = tidak ada tema khusus (pakai default copper/sales).
    """
    name = filename.lower().replace('.html', '')
    for theme_class, patterns in THEME_MAP:
        for pat in patterns:
            if pat in name:
                return theme_class
    return None  # default = theme-sales (tidak perlu inject)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Inject <link> CSS ke base.html
# ─────────────────────────────────────────────────────────────────────────────

def find_base_html(root: Path) -> Path | None:
    tmpl = find_templates_dir(root)
    if not tmpl: return None
    # Cari base/base.html dulu, lalu fallback
    for candidate in [tmpl / 'base' / 'base.html', tmpl / 'base.html']:
        if candidate.exists(): return candidate
    for p in tmpl.rglob('base.html'):
        return p
    return None

def scan_base_html(root: Path) -> dict:
    base = find_base_html(root)
    if not base:
        return {'base': None, 'needs_css': False, 'needs_load_static': False}
    src = read_file(base) or ''
    already = CSS_STATIC_PATH in src
    has_load = '{% load static %}' in src
    return {
        'base'              : base,
        'needs_css'         : not already,
        'needs_load_static' : not has_load,
        'src'               : src,
    }

def apply_base_html(data: dict, log: list) -> bool:
    if not data['needs_css'] or not data['base']: return False
    src  = data['src']
    base = data['base']

    # Tentukan tag yang akan disisipkan
    if data['needs_load_static']:
        inject = f'{{% load static %}}\n<link rel="stylesheet" href="{{% static \'{CSS_STATIC_PATH}\' %}}">'
    else:
        inject = f'<link rel="stylesheet" href="{{% static \'{CSS_STATIC_PATH}\' %}}">'

    # Cari posisi terbaik: setelah </title> atau setelah <head>
    patterns = [
        (r'(</title>)', r'\1\n  ' + inject),
        (r'(<head[^>]*>)', r'\1\n  ' + inject),
    ]
    new_src = src
    for pat, rep in patterns:
        new_src, n = re.subn(pat, rep, new_src, count=1)
        if n: break
    else:
        # Fallback: prepend ke file
        new_src = inject + '\n' + src

    bak = backup(base)
    write_file(base, new_src)
    log.append({'step': 1, 'file': str(base), 'backup': str(bak)})
    try:    rel = str(base.relative_to(BASE))
    except: rel = str(base)
    print(f'  {OK} {rel}')
    print(f'       {G}→ <link> CSS ditambahkan{RST}')
    return True

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Tambah class tema di wrapper halaman
# ─────────────────────────────────────────────────────────────────────────────

# Pattern wrapper yang biasa jadi container utama di page template Django
# Urutan: yang paling spesifik dulu
WRAPPER_PATTERNS = [
    # <div class="...page-wrapper..."> atau <main class="...">
    re.compile(r'(<(?:div|main|section)\s[^>]*class\s*=\s*["\'][^"\']*(?:page-wrapper|page-content|main-content|container-fluid|app-content|content-wrapper)[^"\']*["\'][^>]*>)', re.IGNORECASE),
    # <div id="main-content"> atau sejenisnya
    re.compile(r'(<(?:div|main)\s[^>]*id\s*=\s*["\'](?:main|content|app|wrapper|page)[^"\']*["\'][^>]*>)', re.IGNORECASE),
    # Fallback: <body ...>
    re.compile(r'(<body(?:\s[^>]*)?>)', re.IGNORECASE),
]

def add_theme_class(src: str, theme_class: str) -> tuple[str, bool]:
    """
    Tambahkan theme_class ke wrapper pertama yang ditemukan.
    Return (new_src, changed).
    """
    # Jika sudah ada class tema — skip
    if f'theme-' in src and any(f'class{tc}' in src.replace(' ', '') for tc in [theme_class]):
        return src, False
    # Jika sudah ada theme class apapun di file ini — skip (tidak overwrite)
    if re.search(r'\btheme-(?:sales|purchase|inventory|reports|master|marketing|production|settings|auth)\b', src):
        return src, False

    for pat in WRAPPER_PATTERNS:
        m = pat.search(src)
        if not m:
            continue
        tag = m.group(1)
        # Tambahkan class ke existing class="..." atau buat class baru
        if 'class=' in tag.lower():
            # Cari akhir nilai class
            new_tag = re.sub(
                r'(class\s*=\s*["\'])([^"\']*?)(["\'])',
                lambda cm: f'{cm.group(1)}{cm.group(2)} {theme_class}{cm.group(3)}',
                tag, count=1, flags=re.IGNORECASE
            )
        else:
            # Tidak ada class — tambahkan sebelum >
            new_tag = tag[:-1] + f' class="{theme_class}">'
        new_src = src[:m.start(1)] + new_tag + src[m.end(1):]
        return new_src, True

    return src, False

def scan_html_themes(root: Path) -> list[dict]:
    tmpl = find_templates_dir(root)
    if not tmpl: return []
    results = []
    for html in tmpl.rglob('*.html'):
        if html.name == 'base.html': continue
        theme = detect_theme(html.name)
        if not theme: continue
        src = read_file(html) or ''
        # Skip jika sudah ada theme class
        if re.search(r'\btheme-(?:sales|purchase|inventory|reports|master|marketing|production|settings|auth)\b', src):
            continue
        try:    rel = str(html.relative_to(root))
        except: rel = str(html)
        results.append({'file': html, 'rel': rel, 'theme': theme, 'name': html.name})
    return results

def apply_html_themes(results: list[dict], log: list) -> int:
    total = 0
    for item in results:
        src = read_file(item['file']) or ''
        new_src, changed = add_theme_class(src, item['theme'])
        if not changed: continue
        bak = backup(item['file'])
        write_file(item['file'], new_src)
        log.append({'step': 2, 'file': str(item['file']), 'backup': str(bak)})
        total += 1
        print(f'  {OK} {item["rel"]}')
        print(f'       {G}+ {item["theme"]}{RST}')
    return total

# ─────────────────────────────────────────────────────────────────────────────
# REPORT — tampilkan tema per file
# ─────────────────────────────────────────────────────────────────────────────

THEME_COLORS = {
    'theme-sales'      : '\033[33m',   # kuning (copper)
    'theme-purchase'   : '\033[34m',   # biru
    'theme-inventory'  : '\033[32m',   # hijau
    'theme-reports'    : '\033[35m',   # magenta (violet)
    'theme-master'     : '\033[36m',   # cyan (teal)
    'theme-marketing'  : '\033[95m',   # magenta terang (rose)
    'theme-production' : '\033[33m',   # kuning (amber)
    'theme-settings'   : '\033[90m',   # abu-abu
    'theme-auth'       : '\033[90m',   # abu-abu
    None               : '\033[2m',    # dim (default)
}

def run_report(root: Path):
    tmpl = find_templates_dir(root)
    if not tmpl:
        print(f'\n  {WN} templates/ tidak ditemukan\n'); return
    sep('TEMA PER FILE')
    by_theme: dict[str | None, list[str]] = {}
    for html in sorted(tmpl.rglob('*.html')):
        theme = detect_theme(html.name)
        # Cek apakah sudah diterapkan di file
        src = read_file(html) or ''
        applied = bool(re.search(r'\btheme-\w+\b', src))
        label   = f'{"✓ " if applied else "  "}{html.name}'
        by_theme.setdefault(theme, []).append(label)
    for theme, files in sorted(by_theme.items(), key=lambda x: x[0] or 'zzz'):
        col = THEME_COLORS.get(theme, DIM)
        label = theme or '(default copper/sales)'
        print(f'\n  {col}{label}{RST}  {DIM}({len(files)} file){RST}')
        for f in files:
            print(f'    {DIM}{f}{RST}')
    sep()

# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW / APPLY / UNDO
# ─────────────────────────────────────────────────────────────────────────────

def run_preview(root: Path):
    sep('STEP 1 — base.html: inject CSS link')
    data = scan_base_html(root)
    if not data['base']:
        print(f'  {WN} base.html tidak ditemukan')
    elif not data['needs_css']:
        print(f'  {OK} CSS sudah di-include di base.html')
    else:
        try:    rel = str(data['base'].relative_to(root))
        except: rel = str(data['base'])
        print(f'  {FX} {rel}')
        if data['needs_load_static']:
            print(f'       {Y}+ {{% load static %}}{RST}')
        print(f'       {Y}+ <link> lumra_design_system.css{RST}')

    sep('STEP 2 — class tema di wrapper HTML')
    results = scan_html_themes(root)
    if not results:
        print(f'  {OK} Semua file sudah punya class tema atau tidak perlu tema khusus.')
    else:
        by_theme: dict[str, list] = {}
        for item in results:
            by_theme.setdefault(item['theme'], []).append(item)
        for theme, items in sorted(by_theme.items()):
            col = THEME_COLORS.get(theme, DIM)
            print(f'\n  {col}{theme}{RST}  {DIM}({len(items)} file){RST}')
            for item in items:
                print(f'    {FX} {item["name"]}')

    sep()
    print(f'  Jalankan dengan {C}--apply{RST} untuk menerapkan.\n')

def run_apply(root: Path, yes: bool):
    run_preview(root)
    if not yes:
        try:
            confirm = input('  Terapkan semua? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.'); return
        if confirm != 'y':
            print('  Dibatalkan.'); return

    log = []

    sep('STEP 1 — Fix base.html')
    data = scan_base_html(root)
    if data['needs_css']:
        apply_base_html(data, log)
    else:
        print(f'  {OK} CSS sudah ada.')

    sep('STEP 2 — Inject class tema')
    results = scan_html_themes(root)
    n = apply_html_themes(results, log) if results else 0
    if not results:
        print(f'  {OK} Tidak ada yang perlu diupdate.')

    if log:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    sep()
    print(f'  {OK} Selesai!')
    print(f'     base.html CSS    : {"ditambahkan" if data["needs_css"] else "sudah ada"}')
    print(f'     class tema inject: {n} file')
    print(f'  {DIM}Rollback: python lumra_apply_theme.py --undo{RST}')
    print(f'\n  {C}Lihat laporan: python lumra_apply_theme.py --report{RST}\n')

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
        description='Lumra ERP — Apply Design System Theme',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Yang dilakukan:
  1. Inject <link rel="stylesheet"> lumra_design_system.css ke base.html
  2. Tambah class tema di wrapper utama setiap halaman:
       theme-sales       → dashboard, pos, notification (default copper)
       theme-purchase    → purchasing, vendor, supplier (ink blue)
       theme-inventory   → stock, product, opname (forest green)
       theme-reports     → report_*, financial, trends (violet)
       theme-master      → customer, category, unit, location (teal)
       theme-marketing   → campaign, discount, loyalty (rose)
       theme-production  → recipe, bom (amber)
       theme-settings    → settings, profile, users, business (slate)
       theme-auth        → login, register (slate neutral)

Contoh:
  python lumra_apply_theme.py                        → preview
  python lumra_apply_theme.py --apply                → terapkan
  python lumra_apply_theme.py --apply --yes          → tanpa konfirmasi
  python lumra_apply_theme.py --undo                 → rollback
  python lumra_apply_theme.py --report               → laporan per file
  python lumra_apply_theme.py --source D:\\Project
        """
    )
    parser.add_argument('--apply',  action='store_true')
    parser.add_argument('--yes',    action='store_true')
    parser.add_argument('--undo',   action='store_true')
    parser.add_argument('--report', action='store_true')
    parser.add_argument('--source', type=str, default=None)
    args = parser.parse_args()
    root = find_root(args.source)

    print(f'\n{B}{"═"*66}')
    print(f'  {W}Lumra ERP — Apply Design System Theme{RST}')
    print(f'{B}{"═"*66}{RST}')
    print(f'  Root : {DIM}{root}{RST}')
    print(f'  Mode : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}\n')

    if args.undo:     run_undo()
    elif args.report: run_report(root)
    elif args.apply:  run_apply(root, yes=args.yes)
    else:             run_preview(root)

if __name__ == '__main__':
    main()