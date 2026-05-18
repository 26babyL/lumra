"""
fix_render_paths.py — Lumra ERP Views Auto-Fixer
=================================================
Otomatis mengupdate semua template path di dalam views.py setelah
migrate_templates.py memindahkan file HTML ke subfolder modul.

Yang diubah:
    render(request, 'dashboard.html', ...)
    render(request, "dashboard.html", ...)
    render(request, 'dashboard.html')
    TemplateResponse(request, 'dashboard.html', ...)
    get_template('dashboard.html')
    loader.get_template('dashboard.html')
    select_template(['dashboard.html', ...])

Menjadi:
    render(request, 'sales/dashboard.html', ...)
    ... dst.

Penggunaan:
    python fix_render_paths.py                  → preview semua perubahan
    python fix_render_paths.py --apply          → terapkan ke semua views.py
    python fix_render_paths.py --apply --yes    → tanpa konfirmasi
    python fix_render_paths.py --undo           → kembalikan dari backup
    python fix_render_paths.py --source path/  → override root project
    python fix_render_paths.py --file lumra_config/sales/views.py → satu file saja

Catatan:
    - Backup otomatis dibuat di .fix_render_backup/ sebelum perubahan
    - Hanya mengubah path yang BELUM punya subfolder (tidak double-prefix)
    - Template yang sudah 'modul/nama.html' tidak disentuh
"""

import os
import re
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR    = Path(__file__).resolve().parent
BACKUP_DIR  = BASE_DIR / '.fix_render_backup'
LOG_FILE    = BASE_DIR / '.fix_render_log.json'

# Modul yang views-nya perlu di-scan
VIEWS_PATHS = [
    'lumra_config/sales/views.py',
    'lumra_config/master_data/views.py',
    'lumra_config/inventory/views.py',
    'lumra_config/marketing/views.py',
    'lumra_config/reports/views.py',
    'lumra_config/production/views.py',
    'lumra_config/settings_app/views.py',
    'lumra_config/auth_app/views.py',
    'lumra_config/api/views.py',
    # legacy / sebelum migrasi modul
    'core/core/views.py',
    'core/views.py',
]

# ─────────────────────────────────────────────────────────────────────────────
# MODULE MAP  (identik dengan migrate_templates.py — jangan ubah sendiri)
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
        'navbar', 'sidebar', 'footer', 'modal',
        'breadcrumb', 'pagination', 'alert', 'toast',
        'partials', '_partial', 'layout', 'error', '404', '500',
    ],
}

# Template yang tidak perlu diubah
SKIP_TEMPLATES = {'base.html'}

# ─────────────────────────────────────────────────────────────────────────────
# DETEKSI MODUL
# ─────────────────────────────────────────────────────────────────────────────

def detect_module(template_name: str) -> str | None:
    """
    Kembalikan nama modul untuk template_name, atau None jika tidak dikenali.
    Hanya mendeteksi nama file (tanpa path prefix) yang belum punya subfolder.
    """
    # Jika sudah ada subfolder (misal 'sales/dashboard.html') → skip
    if '/' in template_name or '\\' in template_name:
        return None

    # Jika ada di SKIP list
    if template_name in SKIP_TEMPLATES:
        return None

    stem = template_name.replace('.html', '').lower()
    for module, patterns in MODULE_MAP.items():
        for pattern in patterns:
            if pattern.lower() in stem:
                return module

    return None   # tidak dikenali → jangan ubah


# ─────────────────────────────────────────────────────────────────────────────
# REGEX — tangkap semua bentuk template string di Django views
# ─────────────────────────────────────────────────────────────────────────────

# Menangkap string setelah kata kunci render/TemplateResponse/get_template
# Format: keyword(  request?,  'template.html'  atau  "template.html"
#
# Group 1 : quote karakter (' atau ")
# Group 2 : isi string (nama template)
RENDER_PATTERN = re.compile(
    r"""
    # Keyword sebelum template string
    (?:
        render\s*\(\s*\w+\s*,\s*       # render(request, 'tmpl.html'
      | TemplateResponse\s*\(\s*\w+\s*,\s*   # TemplateResponse(request, 'tmpl.html'
      | get_template\s*\(\s*           # get_template('tmpl.html'
      | loader\.get_template\s*\(\s*   # loader.get_template('tmpl.html'
      | select_template\s*\(\s*\[?\s*  # select_template(['tmpl.html'
    )
    (['"])                              # Group 1: quote char
    ([^'"]+\.html)                     # Group 2: template path
    \1                                 # closing quote (sama dengan pembuka)
    """,
    re.VERBOSE,
)


def process_source(source: str) -> tuple[str, list[dict]]:
    """
    Scan source code, ganti template path yang perlu diupdate.
    Kembalikan (new_source, list_of_changes).
    """
    changes = []

    def replacer(m: re.Match) -> str:
        full_match  = m.group(0)
        quote       = m.group(1)
        tmpl_name   = m.group(2)

        module = detect_module(tmpl_name)
        if module is None:
            return full_match          # tidak ada perubahan

        new_tmpl = f'{module}/{tmpl_name}'
        new_full = full_match.replace(
            f'{quote}{tmpl_name}{quote}',
            f'{quote}{new_tmpl}{quote}',
            1,
        )
        changes.append({
            'old': tmpl_name,
            'new': new_tmpl,
        })
        return new_full

    new_source = RENDER_PATTERN.sub(replacer, source)
    return new_source, changes


# ─────────────────────────────────────────────────────────────────────────────
# FILE OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def backup_file(filepath: Path) -> Path:
    """Simpan backup file asli sebelum modifikasi."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    rel      = filepath.relative_to(BASE_DIR)
    # Buat struktur folder di dalam backup dir
    dest     = BACKUP_DIR / ts / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, dest)
    return dest


def get_views_files(source_override: str = None, single_file: str = None) -> list[Path]:
    """Kumpulkan semua file views.py yang perlu diproses."""
    root = Path(source_override).resolve() if source_override else BASE_DIR

    if single_file:
        p = Path(single_file).resolve() if Path(single_file).is_absolute() else root / single_file
        return [p] if p.exists() else []

    result = []
    for rel in VIEWS_PATHS:
        p = root / rel
        if p.exists():
            result.append(p)

    # Juga scan semua views.py di bawah lumra_config/ yang mungkin belum terdaftar
    lc = root / 'lumra_config'
    if lc.exists():
        for found in lc.rglob('views.py'):
            if found not in result:
                result.append(found)

    return sorted(set(result))


# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW
# ─────────────────────────────────────────────────────────────────────────────

def preview_all(files: list[Path]):
    total_changes = 0
    any_change    = False

    print('\n' + '═' * 65)
    print('  PREVIEW — PERUBAHAN TEMPLATE PATH DI VIEWS')
    print('  (Gunakan --apply untuk menerapkan)')
    print('═' * 65)

    for fpath in files:
        try:
            source = fpath.read_text(encoding='utf-8')
        except Exception as e:
            print(f'\n  ⚠️  Tidak bisa baca {fpath}: {e}')
            continue

        _, changes = process_source(source)
        if not changes:
            continue

        any_change = True
        rel = fpath.relative_to(BASE_DIR) if fpath.is_relative_to(BASE_DIR) else fpath
        print(f'\n  📄  {rel}')
        for c in changes:
            print(f"       {c['old']:45s}  →  {c['new']}")
        total_changes += len(changes)

    if not any_change:
        print('\n  ✅  Tidak ada perubahan yang diperlukan.')
        print('      Semua template path sudah menggunakan subfolder,')
        print('      atau belum ada views.py yang ditemukan.\n')
    else:
        print(f'\n  Total perubahan   : {total_changes}')
        print(f'  File yang terdampak: {sum(1 for f in files if _has_changes(f))}')

    print('═' * 65 + '\n')
    return any_change


def _has_changes(fpath: Path) -> bool:
    try:
        _, ch = process_source(fpath.read_text(encoding='utf-8'))
        return bool(ch)
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# APPLY
# ─────────────────────────────────────────────────────────────────────────────

def apply_all(files: list[Path]):
    log        = []
    total_mod  = 0
    total_chg  = 0

    for fpath in files:
        try:
            source = fpath.read_text(encoding='utf-8')
        except Exception as e:
            print(f'  ⚠️  Tidak bisa baca {fpath}: {e}')
            continue

        new_source, changes = process_source(source)

        if not changes:
            continue

        # Backup sebelum tulis ulang
        backup_path = backup_file(fpath)

        fpath.write_text(new_source, encoding='utf-8')

        rel = fpath.relative_to(BASE_DIR) if fpath.is_relative_to(BASE_DIR) else fpath
        print(f'\n  ✅  {rel}  ({len(changes)} perubahan)')
        for c in changes:
            print(f"       {c['old']}  →  {c['new']}")

        log.append({
            'file'   : str(fpath),
            'backup' : str(backup_path),
            'changes': changes,
        })
        total_mod += 1
        total_chg += len(changes)

    # Tulis log untuk --undo
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    if total_mod:
        print(f'\n  Selesai: {total_chg} path diperbarui di {total_mod} file.')
        print(f'  Backup  : {BACKUP_DIR}')
        print(f'  Undo    : python fix_render_paths.py --undo\n')
    else:
        print('\n  ✅  Tidak ada yang perlu diubah.\n')


# ─────────────────────────────────────────────────────────────────────────────
# UNDO
# ─────────────────────────────────────────────────────────────────────────────

def undo_all():
    if not LOG_FILE.exists():
        print('\n❌  Log tidak ditemukan — tidak ada yang bisa di-undo.\n')
        return

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log = json.load(f)

    if not log:
        print('\n✅  Log kosong.\n')
        return

    restored = 0
    for entry in log:
        fpath  = Path(entry['file'])
        backup = Path(entry['backup'])

        if not backup.exists():
            print(f"  ⚠️  Backup tidak ditemukan: {backup}")
            continue

        shutil.copy2(backup, fpath)
        restored += 1
        rel = fpath.relative_to(BASE_DIR) if fpath.is_relative_to(BASE_DIR) else fpath
        print(f'  ↩️  {rel}  ← dikembalikan dari backup')

    LOG_FILE.unlink(missing_ok=True)
    print(f'\n  Selesai: {restored} file dikembalikan.\n')


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Auto-fix render() template paths di views.py setelah migrasi template.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python fix_render_paths.py                              → preview semua
  python fix_render_paths.py --apply                      → terapkan (+ konfirmasi)
  python fix_render_paths.py --apply --yes                → terapkan tanpa konfirmasi
  python fix_render_paths.py --file lumra_config/sales/views.py   → satu file
  python fix_render_paths.py --undo                       → kembalikan dari backup
        """
    )
    parser.add_argument('--apply',  action='store_true', help='Terapkan perubahan')
    parser.add_argument('--yes',    action='store_true', help='Skip konfirmasi (pakai dengan --apply)')
    parser.add_argument('--undo',   action='store_true', help='Kembalikan dari backup')
    parser.add_argument('--source', type=str, default=None, help='Override root project path')
    parser.add_argument('--file',   type=str, default=None, help='Proses satu file views.py saja')
    args = parser.parse_args()

    if args.undo:
        undo_all()
        return

    files = get_views_files(source_override=args.source, single_file=args.file)

    if not files:
        print('\n⚠️  Tidak ada file views.py ditemukan.')
        print('   Pastikan script dijalankan dari root project,')
        print('   atau gunakan --source untuk menentukan path.\n')
        return

    has_changes = preview_all(files)

    if args.apply:
        if not has_changes:
            return
        if not args.yes:
            confirm = input('Terapkan semua perubahan di atas? (y/N): ').strip().lower()
            if confirm != 'y':
                print('  Dibatalkan.\n')
                return
        apply_all(files)
    else:
        if has_changes:
            print('  Jalankan dengan  --apply  untuk menerapkan.\n')


if __name__ == '__main__':
    main()