"""
lumra_recolor.py
================
Ganti semua hardcode warna di HTML template ke palet Lumra Design System.
Setiap modul punya palet sendiri tapi semua berbasis copper/amber tone.

Cara pakai:
  python lumra_recolor.py --list                         → lihat semua modul
  python lumra_recolor.py --module sales                 → preview modul sales
  python lumra_recolor.py --module sales --apply         → apply modul sales
  python lumra_recolor.py --all                          → preview semua
  python lumra_recolor.py --all --apply                  → apply semua
  python lumra_recolor.py --all --apply --yes            → tanpa konfirmasi
  python lumra_recolor.py --undo                         → rollback
  python lumra_recolor.py --source D:\\APPS\\Project\\lumra
  python lumra_recolor.py --report                       → laporan warna per file
"""

import re, shutil, json, argparse
from pathlib import Path
from datetime import datetime

BASE       = Path(__file__).resolve().parent
BACKUP_DIR = BASE / '.lumra_recolor_backup'
LOG_FILE   = BASE / '.lumra_recolor_log.json'

G  = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B  = '\033[94m'; C = '\033[96m'; W = '\033[97m'
DIM= '\033[2m';  RST= '\033[0m'
OK = f'{G}✅{RST}'; WN = f'{Y}⚠️ {RST}'; FX = f'{C}🔧{RST}'

def sep(title=''):
    pad = (66 - len(title) - 2) // 2 if title else 0
    if title:
        print(f'\n{B}{"═"*pad} {W}{title}{RST}{B} {"═"*(66-pad-len(title)-2)}{RST}')
    else:
        print(f'{DIM}{"═"*66}{RST}')

# ─────────────────────────────────────────────────────────────────────────────
# PALET LENGKAP
# Semua berbasis copper/amber family, beda modul beda shade/tone
# ─────────────────────────────────────────────────────────────────────────────

# Shared: semua emerald hex → copper hex (berlaku untuk semua modul)
EMERALD_TO_COPPER = [
    # Hex colors
    ('#ecfdf5', '#FBF4EC'),   # emerald-50  → copper-50
    ('#d1fae5', '#F5DFC0'),   # emerald-100 → copper-100
    ('#a7f3d0', '#E8B878'),   # emerald-200 → copper-200
    ('#6ee7b7', '#D49A4E'),   # emerald-300 → copper-300
    ('#34d399', '#C98A3E'),   # emerald-400 → copper-400
    ('#10b981', '#A66B20'),   # emerald-500 → copper-500  ★ UTAMA
    ('#059669', '#8A5518'),   # emerald-600 → copper-600
    ('#047857', '#7D4E14'),   # emerald-700 → copper-700
    ('#065f46', '#53320C'),   # emerald-800/900 → copper-800
    ('#064e3b', '#3A220A'),   # emerald-950 → copper-950

    # rgba emerald → rgba copper
    ('rgba(16,185,129,',    'rgba(166,107,32,'),
    ('rgba(16, 185, 129,',  'rgba(166, 107, 32,'),
    ('rgba(5,150,105,',     'rgba(138,85,24,'),
    ('rgba(5, 150, 105,',   'rgba(138, 85, 24,'),
    ('rgba(4,120,87,',      'rgba(125,78,20,'),
    ('rgba(4, 120, 87,',    'rgba(125, 78, 20,'),
    ('rgba(52,211,153,',    'rgba(212,154,78,'),
    ('rgba(52, 211, 153,',  'rgba(212, 154, 78,'),
    ('rgba(6,95,70,',       'rgba(83,50,12,'),
    ('rgba(209,250,229,',   'rgba(245,223,192,'),
    ('rgba(240,253,244,',   'rgba(251,244,236,'),

    # Tailwind classes — emerald → amber/copper approximation via CSS var
    # (diganti ke CSS variable agar ikut tema)
    ('bg-emerald-50',      'bg-[var(--accent-light,#FBF4EC)]'),
    ('bg-emerald-100',     'bg-[var(--accent-medium,#F5DFC0)]'),
    ('bg-emerald-200',     'bg-[#E8B878]'),
    ('bg-emerald-300',     'bg-[#D49A4E]'),
    ('bg-emerald-400',     'bg-[#C98A3E]'),
    ('bg-emerald-500',     'bg-[var(--accent,#A66B20)]'),
    ('bg-emerald-600',     'bg-[#8A5518]'),
    ('bg-emerald-700',     'bg-[#7D4E14]'),
    ('bg-emerald-800',     'bg-[#53320C]'),
    ('bg-emerald-900',     'bg-[#3A220A]'),
    ('text-emerald-50',    'text-[#FBF4EC]'),
    ('text-emerald-100',   'text-[#F5DFC0]'),
    ('text-emerald-200',   'text-[#E8B878]'),
    ('text-emerald-300',   'text-[#D49A4E]'),
    ('text-emerald-400',   'text-[#C98A3E]'),
    ('text-emerald-500',   'text-[var(--accent,#A66B20)]'),
    ('text-emerald-600',   'text-[var(--accent,#A66B20)]'),
    ('text-emerald-700',   'text-[var(--accent-dark,#7D4E14)]'),
    ('text-emerald-800',   'text-[#53320C]'),
    ('text-emerald-900',   'text-[#3A220A]'),
    ('border-emerald-50',  'border-[#FBF4EC]'),
    ('border-emerald-100', 'border-[#F5DFC0]'),
    ('border-emerald-200', 'border-[var(--accent-200,#E8B878)]'),
    ('border-emerald-300', 'border-[#D49A4E]'),
    ('border-emerald-400', 'border-[#C98A3E]'),
    ('border-emerald-500', 'border-[var(--accent,#A66B20)]'),
    ('border-emerald-600', 'border-[#8A5518]'),
    ('ring-emerald-400',   'ring-[#C98A3E]'),
    ('ring-emerald-500',   'ring-[var(--accent,#A66B20)]'),
    ('from-emerald-500',   'from-[#A66B20]'),
    ('from-emerald-600',   'from-[#8A5518]'),
    ('to-emerald-500',     'to-[#A66B20]'),
    ('to-emerald-600',     'to-[#8A5518]'),
    ('via-emerald-500',    'via-[#A66B20]'),
    ('hover:bg-emerald-50',  'hover:bg-[#FBF4EC]'),
    ('hover:bg-emerald-100', 'hover:bg-[#F5DFC0]'),
    ('hover:bg-emerald-500', 'hover:bg-[#A66B20]'),
    ('hover:text-emerald-600', 'hover:text-[#8A5518]'),
    ('hover:text-emerald-700', 'hover:text-[#7D4E14]'),
    ('hover:border-emerald-400', 'hover:border-[#C98A3E]'),
    ('focus:ring-emerald-400', 'focus:ring-[#C98A3E]'),
    ('focus:ring-emerald-500', 'focus:ring-[var(--accent,#A66B20)]'),

    # Gradient strings
    ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #A66B20'),
    ('linear-gradient(135deg, #065f46', 'linear-gradient(135deg, #53320C'),
    ('linear-gradient(135deg, #047857', 'linear-gradient(135deg, #7D4E14'),
    ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #A66B20'),
    ('linear-gradient(90deg, #059669',  'linear-gradient(90deg, #8A5518'),
    ('radial-gradient(#10b981',         'radial-gradient(#A66B20'),
    ('radial-gradient(#059669',         'radial-gradient(#8A5518'),

    # JS/Alpine string literals
    ("'bg-emerald-",   "'bg-[#A66B20]"),
    ('"bg-emerald-',   '"bg-[#A66B20]'),
    ("'text-emerald-", "'text-[var(--accent,#A66B20)]"),
    ('"text-emerald-', '"text-[var(--accent,#A66B20)]'),
    # Alpine :class binding patterns
    ("'text-emerald-600'", "'text-[var(--accent,#A66B20)]'"),
    ("'text-emerald-700'", "'text-[var(--accent-dark,#7D4E14)]'"),
    ("'bg-emerald-50'",    "'bg-[var(--accent-light,#FBF4EC)]'"),
    ("'bg-emerald-500'",   "'bg-[var(--accent,#A66B20)]'"),
    ("'border-emerald-400'", "'border-[#C98A3E]'"),
]

# ─────────────────────────────────────────────────────────────────────────────
# PALET PER MODUL
# Setiap modul punya override tambahan di atas EMERALD_TO_COPPER
# ─────────────────────────────────────────────────────────────────────────────

# Inventory — Forest Green (tetap hijau tapi lebih mature)
INVENTORY_OVERRIDES = [
    ('#10b981', '#2D7A4F'),
    ('rgba(16,185,129,', 'rgba(45,122,79,'),
    ('bg-emerald-500', 'bg-[#2D7A4F]'),
    ('text-emerald-600', 'text-[#2D7A4F]'),
    ('border-emerald-200', 'border-[#A8D5B8]'),
    ('bg-emerald-50', 'bg-[#EBF5EF]'),
    ('#ecfdf5', '#EBF5EF'),
    ('#d1fae5', '#C2DFC9'),
    ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #2D7A4F'),
    ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #2D7A4F'),
]

# Reports — Violet
REPORTS_OVERRIDES = [
    ('#10b981', '#6B52B8'),
    ('rgba(16,185,129,', 'rgba(107,82,184,'),
    ('bg-emerald-500', 'bg-[#6B52B8]'),
    ('text-emerald-600', 'text-[#6B52B8]'),
    ('border-emerald-200', 'border-[#BAA8E2]'),
    ('bg-emerald-50', 'bg-[#F4F0FB]'),
    ('#ecfdf5', '#F4F0FB'),
    ('#d1fae5', '#D9CEEF'),
    ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #6B52B8'),
    ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #6B52B8'),
]

# Marketing — Rose
MARKETING_OVERRIDES = [
    ('#10b981', '#A84878'),
    ('rgba(16,185,129,', 'rgba(168,72,120,'),
    ('bg-emerald-500', 'bg-[#A84878]'),
    ('text-emerald-600', 'text-[#A84878]'),
    ('border-emerald-200', 'border-[#E29EBE]'),
    ('bg-emerald-50', 'bg-[#FBF0F5]'),
    ('#ecfdf5', '#FBF0F5'),
    ('#d1fae5', '#F0C8DC'),
    ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #A84878'),
    ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #A84878'),
]

# Master Data — Teal
MASTER_OVERRIDES = [
    ('#10b981', '#3D7070'),
    ('rgba(16,185,129,', 'rgba(61,112,112,'),
    ('bg-emerald-500', 'bg-[#3D7070]'),
    ('text-emerald-600', 'text-[#3D7070]'),
    ('border-emerald-200', 'border-[#98B8B8]'),
    ('bg-emerald-50', 'bg-[#F0F4F4]'),
    ('#ecfdf5', '#F0F4F4'),
    ('#d1fae5', '#C8D8D8'),
    ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #3D7070'),
    ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #3D7070'),
]

# Production — Amber warm
PRODUCTION_OVERRIDES = [
    ('#10b981', '#A07828'),
    ('rgba(16,185,129,', 'rgba(160,120,40,'),
    ('bg-emerald-500', 'bg-[#A07828]'),
    ('text-emerald-600', 'text-[#A07828]'),
    ('border-emerald-200', 'border-[#E0C080]'),
    ('bg-emerald-50', 'bg-[#FBF5EB]'),
    ('#ecfdf5', '#FBF5EB'),
    ('#d1fae5', '#F0DDB8'),
    ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #A07828'),
    ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #A07828'),
]

# Settings — Slate monochrome
SETTINGS_OVERRIDES = [
    ('#10b981', '#5E5A53'),
    ('rgba(16,185,129,', 'rgba(94,90,83,'),
    ('bg-emerald-500', 'bg-[#5E5A53]'),
    ('text-emerald-600', 'text-[#5E5A53]'),
    ('border-emerald-200', 'border-[#D9D6D0]'),
    ('bg-emerald-50', 'bg-[#F8F7F4]'),
    ('#ecfdf5', '#F8F7F4'),
    ('#d1fae5', '#EEECEA'),
    ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #5E5A53'),
    ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #5E5A53'),
]

# Auth — sama dengan settings tapi lebih minimal
AUTH_OVERRIDES = SETTINGS_OVERRIDES

# ─────────────────────────────────────────────────────────────────────────────
# MODULE DEFINITION
# format: module_name → (folder_patterns, color_rules)
# ─────────────────────────────────────────────────────────────────────────────

MODULES = {
    'sales': {
        'folders'     : ['sales'],
        'file_patterns': ['dashboard', 'pos', 'notification', 'sales_intelligence',
                          'sales_insight', 'purchasing'],
        'rules'       : EMERALD_TO_COPPER,   # full copper
        'label'       : 'Sales → Copper #A66B20',
        'preview_color': '\033[33m',
    },
    'inventory': {
        'folders'     : ['inventory'],
        'file_patterns': ['stock', 'product', 'inventory', 'opname'],
        'rules'       : INVENTORY_OVERRIDES + EMERALD_TO_COPPER,
        'label'       : 'Inventory → Forest Green #2D7A4F',
        'preview_color': '\033[32m',
    },
    'reports': {
        'folders'     : ['reports'],
        'file_patterns': ['report', 'financial', 'sales_history', 'sales_performance',
                          'transaction', 'transfer', 'trends', 'market', 'profit',
                          'activity', 'purchasing_report', 'requisition'],
        'rules'       : REPORTS_OVERRIDES + EMERALD_TO_COPPER,
        'label'       : 'Reports → Violet #6B52B8',
        'preview_color': '\033[35m',
    },
    'marketing': {
        'folders'     : ['marketing'],
        'file_patterns': ['campaign', 'discount', 'loyalty'],
        'rules'       : MARKETING_OVERRIDES + EMERALD_TO_COPPER,
        'label'       : 'Marketing → Rose #A84878',
        'preview_color': '\033[95m',
    },
    'master': {
        'folders'     : ['master_data'],
        'file_patterns': ['customer', 'categor', 'unit', 'vendor', 'location',
                          'stock_opname'],
        'rules'       : MASTER_OVERRIDES + EMERALD_TO_COPPER,
        'label'       : 'Master Data → Teal #3D7070',
        'preview_color': '\033[36m',
    },
    'production': {
        'folders'     : ['production'],
        'file_patterns': ['recipe', 'bom'],
        'rules'       : PRODUCTION_OVERRIDES + EMERALD_TO_COPPER,
        'label'       : 'Production → Amber #A07828',
        'preview_color': '\033[33m',
    },
    'settings': {
        'folders'     : ['settings'],
        'file_patterns': ['settings', 'profile', 'users', 'user_list', 'user_roles',
                          'business', 'system_status', 'about', 'contact', 'search',
                          'feature_matrix', 'permissions'],
        'rules'       : SETTINGS_OVERRIDES + EMERALD_TO_COPPER,
        'label'       : 'Settings → Slate #5E5A53',
        'preview_color': '\033[90m',
    },
    'auth': {
        'folders'     : ['auth'],
        'file_patterns': ['login', 'register', 'password'],
        'rules'       : AUTH_OVERRIDES + EMERALD_TO_COPPER,
        'label'       : 'Auth → Slate #5E5A53',
        'preview_color': '\033[90m',
    },
    'purchase': {
        'folders'     : ['sales', 'inventory', 'master_data'],
        'file_patterns': ['purchasing', 'vendor', 'supplier_price', 'vendors_list',
                          'purchasing_report'],
        'rules'       : [
            # Ink Blue untuk purchasing/vendor
            ('#10b981',              '#3D5FC4'),
            ('rgba(16,185,129,',     'rgba(61,95,196,'),
            ('bg-emerald-500',       'bg-[#3D5FC4]'),
            ('text-emerald-600',     'text-[#3D5FC4]'),
            ('border-emerald-200',   'border-[#A3B5E4]'),
            ('bg-emerald-50',        'bg-[#EEF2FB]'),
            ('#ecfdf5',              '#EEF2FB'),
            ('#d1fae5',              '#C8D4F0'),
            ('linear-gradient(135deg, #10b981', 'linear-gradient(135deg, #3D5FC4'),
            ('linear-gradient(90deg, #10b981',  'linear-gradient(90deg, #3D5FC4'),
        ] + EMERALD_TO_COPPER,
        'label'       : 'Purchasing/Vendor → Ink Blue #3D5FC4',
        'preview_color': '\033[34m',
    },
}

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

def apply_rules(src: str, rules: list[tuple]) -> tuple[str, int]:
    """Apply semua replacement rules. Return (new_src, n_changes)."""
    total = 0
    for old, new in rules:
        count = src.count(old)
        if count:
            src = src.replace(old, new)
            total += count
    return src, total

def count_remaining_emerald(src: str) -> int:
    """Hitung sisa emerald yang belum di-replace."""
    patterns = ['emerald', '#10b981', '#059669', '#047857', '#065f46',
                '#ecfdf5', '#d1fae5', 'rgba(16,185,129']
    return sum(src.count(p) for p in patterns)

# ─────────────────────────────────────────────────────────────────────────────
# FILE FINDER
# ─────────────────────────────────────────────────────────────────────────────

def find_module_files(root: Path, module_name: str) -> list[Path]:
    """Cari semua HTML file untuk modul tertentu."""
    tmpl = find_templates_dir(root)
    if not tmpl: return []

    mod  = MODULES[module_name]
    files = []

    # Scan berdasarkan folder
    for folder in mod['folders']:
        folder_path = tmpl / 'lumra_pages' / folder
        if folder_path.exists():
            for f in folder_path.rglob('*.html'):
                # Cek apakah nama file cocok dengan pattern modul ini
                name = f.stem.lower()
                if any(pat in name for pat in mod['file_patterns']):
                    if f not in files:
                        files.append(f)
                # Kalau folder spesifik (hanya 1 modul), ambil semua
                elif len(mod['folders']) == 1:
                    if f not in files:
                        files.append(f)

    return sorted(files)

# ─────────────────────────────────────────────────────────────────────────────
# SCAN
# ─────────────────────────────────────────────────────────────────────────────

def scan_module(root: Path, module_name: str) -> list[dict]:
    """Scan file dalam modul, return list perubahan yang akan dilakukan."""
    files   = find_module_files(root, module_name)
    mod     = MODULES[module_name]
    results = []

    for f in files:
        src = read_file(f)
        if not src: continue

        new_src, n = apply_rules(src, mod['rules'])
        remaining  = count_remaining_emerald(new_src)

        if n > 0:
            try:    rel = str(f.relative_to(root))
            except: rel = str(f)
            results.append({
                'file'     : f,
                'rel'      : rel,
                'name'     : f.name,
                'changes'  : n,
                'remaining': remaining,
                'new_src'  : new_src,
            })

    return results

# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW
# ─────────────────────────────────────────────────────────────────────────────

def preview_module(root: Path, module_name: str):
    mod     = MODULES[module_name]
    col     = mod['preview_color']
    results = scan_module(root, module_name)

    print(f'\n  {col}● {mod["label"]}{RST}')
    if not results:
        print(f'  {OK} Semua file sudah bersih atau tidak ada perubahan.')
        return

    total_changes   = sum(r['changes'] for r in results)
    total_remaining = sum(r['remaining'] for r in results)

    for r in results:
        remain_tag = f'  {WN}{r["remaining"]} sisa' if r['remaining'] else f'  {G}bersih{RST}'
        print(f'  {FX} {r["name"]:45s} {G}{r["changes"]:3d} replace{RST}{remain_tag}')

    print(f'\n  {DIM}Total: {total_changes} replace, {total_remaining} emerald tersisa{RST}')

# ─────────────────────────────────────────────────────────────────────────────
# APPLY
# ─────────────────────────────────────────────────────────────────────────────

def apply_module(root: Path, module_name: str, log: list) -> int:
    results = scan_module(root, module_name)
    if not results: return 0

    total = 0
    for r in results:
        bak = backup(r['file'])
        write_file(r['file'], r['new_src'])
        log.append({'module': module_name, 'file': str(r['file']), 'backup': str(bak)})
        total += r['changes']
        remain = f'  {WN}{r["remaining"]} sisa' if r['remaining'] else f'  {G}bersih{RST}'
        print(f'  {OK} {r["name"]:45s} {G}{r["changes"]:3d} replace{RST}{remain}')

    return total

# ─────────────────────────────────────────────────────────────────────────────
# REPORT — laporan warna per file
# ─────────────────────────────────────────────────────────────────────────────

def run_report(root: Path):
    tmpl = find_templates_dir(root)
    if not tmpl: print(f'\n  {WN} templates/ tidak ditemukan\n'); return

    sep('LAPORAN WARNA PER FILE')
    total_dirty = 0

    for html in sorted(tmpl.rglob('*.html')):
        src = read_file(html) or ''
        n = count_remaining_emerald(src)
        if n == 0: continue
        try:    rel = str(html.relative_to(root))
        except: rel = str(html)
        print(f'  {WN} {rel:55s} {Y}{n} emerald tersisa{RST}')
        total_dirty += 1

    sep()
    if total_dirty:
        print(f'  {Y}{total_dirty} file masih punya hardcode emerald{RST}')
        print(f'  Jalankan: python lumra_recolor.py --all --apply')
    else:
        print(f'  {OK} Semua file sudah bersih!')
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
        description='Lumra ERP — Recolor Templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Modul yang tersedia:
  {'  '.join(MODULES.keys())}

Palet per modul:
  sales      → Copper  #A66B20  (warm amber)
  purchase   → Ink     #3D5FC4  (deep blue)
  inventory  → Forest  #2D7A4F  (mature green)
  reports    → Violet  #6B52B8
  master     → Teal    #3D7070
  marketing  → Rose    #A84878
  production → Amber   #A07828
  settings   → Slate   #5E5A53
  auth       → Slate   #5E5A53

Contoh:
  python lumra_recolor.py --list
  python lumra_recolor.py --report
  python lumra_recolor.py --module sales
  python lumra_recolor.py --module sales --apply
  python lumra_recolor.py --all --apply --yes
  python lumra_recolor.py --undo
        """
    )
    parser.add_argument('--module', type=str, choices=list(MODULES.keys()), help='Modul tertentu')
    parser.add_argument('--all',    action='store_true', help='Semua modul')
    parser.add_argument('--apply',  action='store_true', help='Terapkan perubahan')
    parser.add_argument('--yes',    action='store_true', help='Tanpa konfirmasi')
    parser.add_argument('--undo',   action='store_true', help='Rollback')
    parser.add_argument('--list',   action='store_true', help='Daftar modul')
    parser.add_argument('--report', action='store_true', help='Laporan warna per file')
    parser.add_argument('--source', type=str, default=None)
    args = parser.parse_args()
    root = find_root(args.source)

    print(f'\n{B}{"═"*66}')
    print(f'  {W}Lumra ERP — Recolor Templates{RST}')
    print(f'{B}{"═"*66}{RST}')
    print(f'  Root : {DIM}{root}{RST}')
    print(f'  Mode : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}\n')

    if args.undo:
        run_undo(); return

    if args.report:
        run_report(root); return

    if args.list:
        sep('MODUL TERSEDIA')
        for name, mod in MODULES.items():
            col = mod['preview_color']
            print(f'  {col}● {name:12s}{RST}  {mod["label"]}')
        print()
        return

    # Tentukan modul yang akan diproses
    if args.module:
        target_modules = [args.module]
    elif args.all:
        target_modules = list(MODULES.keys())
    else:
        parser.print_help()
        return

    if args.apply:
        # Preview dulu
        sep('PREVIEW')
        for mod_name in target_modules:
            preview_module(root, mod_name)

        if not args.yes:
            sep()
            try:
                confirm = input('  Terapkan semua di atas? (y/N): ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                print('\n  Dibatalkan.'); return
            if confirm != 'y':
                print('  Dibatalkan.'); return

        log   = []
        total = 0

        for mod_name in target_modules:
            mod = MODULES[mod_name]
            col = mod['preview_color']
            sep(f'{mod_name.upper()}')
            n = apply_module(root, mod_name, log)
            total += n
            if n == 0:
                print(f'  {OK} Tidak ada perubahan.')

        if log:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log, f, indent=2, ensure_ascii=False)

        sep()
        print(f'  {OK} Selesai! Total {total} replacement di {len(log)} file.')
        print(f'  {DIM}Rollback : python lumra_recolor.py --undo{RST}')
        print(f'  {C}Verifikasi: python lumra_recolor.py --report{RST}\n')

    else:
        # Preview only
        for mod_name in target_modules:
            sep(f'PREVIEW — {mod_name.upper()}')
            preview_module(root, mod_name)
        sep()
        print(f'  Jalankan dengan {C}--apply{RST} untuk menerapkan.\n')


if __name__ == '__main__':
    main()