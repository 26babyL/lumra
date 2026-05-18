"""
migrate_templates.py — Lumra ERP Template Organizer
=====================================================
Memindahkan file .html dari lumra_config/templates/ ke subfolder
per-modul sesuai struktur urls.py.

Penggunaan:
    python migrate_templates.py           → preview (AMAN, tidak mengubah file)
    python migrate_templates.py --apply   → jalankan pemindahan
    python migrate_templates.py --undo    → batalkan (kembalikan ke semula)

Struktur output:
    lumra_config/templates/
    ├── base/          → base.html, komponen, layout
    ├── sales/         → dashboard, pos, notification, history, performance, purchasing
    ├── master_data/   → products, categories, units, vendors, customers, locations, opname
    ├── inventory/     → stock_movement, planning, supplier_prices
    ├── marketing/     → campaigns, discounts, loyalty
    ├── reports/       → insights, financial, sales reports
    ├── production/    → recipes
    ├── settings_app/  → profile, settings, users, business, about, contact, pricing, search
    └── auth_app/      → login, logout
"""

import os
import shutil
import json
import argparse
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI PATH
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).resolve().parent
TMPL_ROOT  = BASE_DIR / 'lumra_config' / 'templates'
LOG_FILE   = BASE_DIR / '.migrate_templates_log.json'


# ─────────────────────────────────────────────────────────────────────────────
# PETA MODUL → POLA NAMA FILE
# Urutan penting: lebih spesifik di atas, lebih umum di bawah.
# ─────────────────────────────────────────────────────────────────────────────

MODULE_MAP = {

    # ── auth ──────────────────────────────────────────────────────────────────
    'auth_app': [
        'login', 'logout', 'register', 'password',
    ],

    # ── sales ─────────────────────────────────────────────────────────────────
    'sales': [
        'dashboard', 'pos', 'point_of_sale', 'point-of-sale',
        'notification', 'sales_history', 'sales_performance',
        'sales_products', 'purchasing',
    ],

    # ── master_data ───────────────────────────────────────────────────────────
    'master_data': [
        'product',        # product_list, product_detail, products, dll
        'categor',        # categories_list, category_form, category_update, dll
        'unit',           # units_list, unit_form, dll
        'vendor',         # vendors_list, vendor_form, dll
        'supplier',       # supplier_list — bukan supplier_price (sudah di inventory)
        'customer',       # customer_list, customer_detail, dll
        'location',       # locations_view
        'stock_opname',   # stock_opname_*, opname_form
        'opname',
    ],

    # ── inventory ─────────────────────────────────────────────────────────────
    'inventory': [
        'stock_movement', 'stock_planning', 'add_stock',
        'export_stock',   'supplier_price', 'import_product',
        'inventory',
    ],

    # ── marketing ─────────────────────────────────────────────────────────────
    'marketing': [
        'campaign', 'discount', 'loyalty', 'promo', 'voucher',
    ],

    # ── reports ───────────────────────────────────────────────────────────────
    'reports': [
        'report', 'insight', 'financial', 'market_insight',
        'trends', 'activity_log', 'transaction_summary',
        'transfer_report', 'requisition_report', 'purchasing_report',
        'profit_loss', 'sales_by_', 'sales_summary',
    ],

    # ── production ────────────────────────────────────────────────────────────
    'production': [
        'recipe', 'bom', 'bill_of_material', 'production',
    ],

    # ── settings_app ──────────────────────────────────────────────────────────
    'settings_app': [
        'profile', 'settings', 'system_status', 'business',
        'users', 'user_role', 'about', 'contact', 'pricing', 'search',
        'feature_matrix', 'permissions',
    ],

    # ── base (fallback: komponen / layout / base.html sendiri) ────────────────
    'base': [
        'navbar', 'sidebar', 'footer', 'modal',
        'breadcrumb', 'pagination', 'alert', 'toast',
        'partials', '_partial', 'layout', 'error', '404', '500',
    ],
}

# File yang TIDAK boleh dipindah sama sekali
SKIP_FILES = {
    'base.html',    # base template induk — tetap di root templates
}

# Modul fallback jika tidak ada pola yang cocok
DEFAULT_MODULE = 'base'


# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI UTAMA
# ─────────────────────────────────────────────────────────────────────────────

def detect_module(filename: str) -> str:
    """
    Tentukan modul tujuan berdasarkan nama file.
    Cek setiap pola di MODULE_MAP secara berurutan.
    """
    stem = filename.replace('.html', '').lower()

    for module, patterns in MODULE_MAP.items():
        for pattern in patterns:
            if pattern.lower() in stem:
                return module

    return DEFAULT_MODULE


def collect_files() -> list[dict]:
    """
    Scan TMPL_ROOT (non-rekursif) untuk file .html,
    kembalikan daftar rencana pemindahan.
    """
    if not TMPL_ROOT.exists():
        raise FileNotFoundError(
            f"Folder templates tidak ditemukan: {TMPL_ROOT}\n"
            "Pastikan script dijalankan dari root project Lumra."
        )

    plan = []
    for item in sorted(TMPL_ROOT.iterdir()):
        if not item.is_file() or item.suffix != '.html':
            continue
        if item.name in SKIP_FILES:
            continue
        if item.parent.name != TMPL_ROOT.name:
            # sudah di subfolder — abaikan
            continue

        module   = detect_module(item.name)
        dest_dir = TMPL_ROOT / module
        dest     = dest_dir / item.name

        plan.append({
            'file'    : item.name,
            'src'     : str(item),
            'dst'     : str(dest),
            'dst_dir' : str(dest_dir),
            'module'  : module,
        })

    return plan


def preview(plan: list[dict]):
    """Tampilkan rencana pemindahan tanpa melakukan apa pun."""
    if not plan:
        print("\n✅  Tidak ada file yang perlu dipindahkan.\n")
        return

    # Kelompokkan per modul
    by_module: dict[str, list] = {}
    for item in plan:
        by_module.setdefault(item['module'], []).append(item['file'])

    print("\n" + "═" * 60)
    print("  PREVIEW RENCANA PEMINDAHAN TEMPLATE")
    print("  (Gunakan --apply untuk menjalankan)")
    print("═" * 60)

    for module in sorted(by_module):
        dest_rel = f"lumra_config/templates/{module}/"
        print(f"\n  📁  {dest_rel}")
        for fname in sorted(by_module[module]):
            print(f"       └─ {fname}")

    skipped = [f for f in TMPL_ROOT.iterdir()
               if f.is_file() and f.suffix == '.html' and f.name in SKIP_FILES]
    if skipped:
        print(f"\n  ⏭   Dilewati (tetap di root templates/):")
        for f in skipped:
            print(f"       └─ {f.name}")

    print(f"\n  Total file akan dipindahkan : {len(plan)}")
    print("═" * 60 + "\n")


def apply(plan: list[dict]):
    """Jalankan pemindahan dan simpan log untuk --undo."""
    if not plan:
        print("\n✅  Tidak ada yang perlu dipindahkan.\n")
        return

    log = []
    moved = 0
    skipped_exist = 0

    for item in plan:
        dst_dir = Path(item['dst_dir'])
        dst     = Path(item['dst'])
        src     = Path(item['src'])

        # Buat subfolder jika belum ada
        dst_dir.mkdir(parents=True, exist_ok=True)

        # Hindari overwrite tanpa konfirmasi
        if dst.exists():
            print(f"  ⚠️  SKIP (sudah ada): {item['module']}/{item['file']}")
            skipped_exist += 1
            continue

        shutil.move(str(src), str(dst))
        log.append({'src': item['src'], 'dst': item['dst']})
        moved += 1
        print(f"  ✅  {item['file']}  →  {item['module']}/")

    # Tulis log untuk --undo
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    print(f"\n  Selesai: {moved} file dipindahkan, {skipped_exist} dilewati.")
    print(f"  Log disimpan di: {LOG_FILE}")
    print(f"  Jalankan  python migrate_templates.py --undo  untuk membatalkan.\n")


def undo():
    """Kembalikan semua file ke posisi semula berdasarkan log."""
    if not LOG_FILE.exists():
        print("\n❌  Log tidak ditemukan — tidak ada yang bisa di-undo.\n")
        return

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log = json.load(f)

    if not log:
        print("\n✅  Log kosong — tidak ada yang perlu di-undo.\n")
        return

    restored = 0
    for entry in log:
        src = Path(entry['src'])
        dst = Path(entry['dst'])

        if not dst.exists():
            print(f"  ⚠️  File tidak ditemukan di tujuan, skip: {dst}")
            continue

        # Pastikan folder asal masih ada
        src.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dst), str(src))
        restored += 1
        print(f"  ↩️  {dst.name}  ←  dikembalikan ke {src.parent.name}/")

    # Hapus subfolder kosong
    for module in MODULE_MAP:
        module_dir = TMPL_ROOT / module
        if module_dir.exists() and not any(module_dir.iterdir()):
            module_dir.rmdir()
            print(f"  🗑   Folder kosong dihapus: {module}/")

    LOG_FILE.unlink(missing_ok=True)
    print(f"\n  Selesai: {restored} file dikembalikan.\n")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Migrate Lumra ERP templates ke subfolder per-modul.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python migrate_templates.py           → lihat preview
  python migrate_templates.py --apply   → jalankan pemindahan
  python migrate_templates.py --undo    → batalkan
        """
    )
    parser.add_argument('--apply', action='store_true',
                        help='Jalankan pemindahan (default: preview saja)')
    parser.add_argument('--undo',  action='store_true',
                        help='Kembalikan semua file ke posisi semula')
    parser.add_argument('--source', type=str, default=None,
                        help='Override path folder templates (opsional)')
    args = parser.parse_args()

    # Override TMPL_ROOT jika --source diberikan
    global TMPL_ROOT
    if args.source:
        TMPL_ROOT = Path(args.source).resolve()
        print(f"  Source override: {TMPL_ROOT}")

    if args.undo:
        undo()
        return

    try:
        plan = collect_files()
    except FileNotFoundError as e:
        print(f"\n❌  {e}\n")
        return

    if args.apply:
        preview(plan)
        confirm = input("Lanjutkan? (y/N): ").strip().lower()
        if confirm == 'y':
            apply(plan)
        else:
            print("  Dibatalkan.\n")
    else:
        preview(plan)
        print("  Jalankan dengan  --apply  untuk melanjutkan.\n")


if __name__ == '__main__':
    main()