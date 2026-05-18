#!/usr/bin/env python3
"""
lumra_sync.py — Skrip Sinkronisasi Lumra ERP
=============================================
Membuat struktur views/ yang benar di dalam folder lumra/lumra_config/
dengan menyalin & mengadaptasi logika dari folder core (lama).

CARA PAKAI:
    python lumra_sync.py --project-dir /path/to/lumra --core-dir /path/to/core

    Atau jalankan dari dalam folder lumra (auto-detect):
    python lumra_sync.py

YANG DILAKUKAN SKRIP INI:
    1. Scan semua fungsi di folder core/views/
    2. Buat struktur lumra_config/views/ dengan sub-modul yang benar
    3. Copy & rename import dari 'core.' → 'lumra_config.'
    4. Buat __init__.py yang meng-export semua fungsi
    5. Buat views.py stub di setiap app (sales, marketing, dll)
    6. Cek & laporkan template yang mungkin butuh disesuaikan
    7. Validasi bahwa semua fungsi di urls.py tersedia

STRUKTUR TARGET lumra_config/:
    lumra_config/
    ├── views/
    │   ├── __init__.py          ← central exports
    │   ├── dashboard_views.py   ← dashboard + notification
    │   ├── auth_views.py        ← login/logout
    │   ├── inventory_views.py   ← products, stock planning, locations
    │   ├── masterdata_views.py  ← categories, units, vendors
    │   ├── customer_views.py    ← customers CRUD
    │   ├── stock_movement_views.py
    │   ├── stock_opname_views.py
    │   ├── production_views.py  ← recipes
    │   ├── pricing_views.py     ← supplier prices
    │   ├── report_views.py      ← all reports
    │   ├── misc_views.py        ← POS, sales, marketing, settings
    │   ├── api_views.py         ← internal API endpoints
    │   └── helpers.py
    ├── sales/views.py           ← stub → lumra_config.views
    ├── marketing/views.py       ← stub → lumra_config.views
    ├── inventory/views.py       ← stub → lumra_config.views
    ├── master_data/views.py     ← stub → lumra_config.views
    ├── production/views.py      ← stub → lumra_config.views
    ├── reports/views.py         ← stub → lumra_config.views
    ├── api/views.py             ← stub → lumra_config.views
    ├── auth_app/views.py        ← stub → lumra_config.views
    └── settings_app/views.py   ← stub → lumra_config.views
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================
# KONFIGURASI MAPPING: url module → fungsi mana yang dibutuhkan
# ============================================================

# Dari urls.py lumra, setiap modul butuh fungsi-fungsi berikut:
URL_MODULE_FUNCTIONS = {
    "lumra_config.sales.views": [
        "dashboard_view", "notification_view", "pos_view", "pos_create_order",
        "sales_history_view", "sales_history_products_view", "sales_performance_view",
        "purchasing_view", "purchasing_report",
    ],
    "lumra_config.master_data.views": [
        "locations_view", "products_view", "product_detail_view",
        "categories_list", "category_create", "category_update", "category_delete",
        "units_list", "unit_create", "unit_update", "unit_delete",
        "vendors_list", "vendor_create", "vendor_update", "vendor_delete",
        "customer_list", "customer_create", "customer_detail", "customer_update",
        "customer_delete", "customer_redeem_points",
        "stock_opname_locations", "stock_opname_form",
        "stock_opname_approvals", "stock_opname_approval_detail",
        "report_sales_by_product",
    ],
    "lumra_config.inventory.views": [
        "products_import_template", "products_import",
        "stock_planning_view", "stock_movement_view", "add_stock_movement_view",
        "export_stock_movement", "supplier_price_list", "supplier_price_form",
        "supplier_price_delete", "approve_requisition", "submit_stock_allocation",
    ],
    "lumra_config.production.views": [
        "recipe_list", "recipe_form", "recipe_detail", "recipe_delete",
    ],
    "lumra_config.marketing.views": [
        "campaign_list_view", "add_campaign_view", "edit_campaign_view", "delete_campaign_view",
        "discount_list_view", "add_discount_view", "edit_discount_view", "delete_discount_view",
        "loyalty_members_view", "add_loyalty_member_view", "edit_loyalty_member_view",
        "delete_loyalty_member_view",
    ],
    "lumra_config.reports.views": [
        "financial_reports_view", "market_insights_view", "trends_analysis_view",
        "activity_log_view", "download_report_view", "export_trends_view",
        "sales_report", "transaction_summary", "transfer_report", "requisition_report",
        "report_inventory_log", "report_inventory_low", "report_inventory_stock",
        "report_profit_loss_detail", "report_sales_by_outlet", "report_sales_by_payment",
        "report_sales_summary",
    ],
    "lumra_config.settings_app.views": [
        "users_view", "profile_view", "settings_view", "system_status_view",
        "business_settings_view", "business_form_general_view",
        "business_feature_matrix_view", "user_roles_permissions_view",
        "about_view", "contact_view", "pricing_view", "search_view",
    ],
    "lumra_config.auth_app.views": [
        "login_view", "logout_view",
    ],
    "lumra_config.api.views": [
        "api_dashboard_data", "api_dashboard_chart_data",
        "submit_requisition", "submit_purchases", "confirm_receipt", "get_location_stock",
    ],
}

# Mapping: fungsi → file views sumber di core
FUNCTION_SOURCE_MAP = {
    # dashboard_views.py
    "dashboard_view": "dashboard_views",
    "notification_view": "dashboard_views",
    "api_dashboard_data": "dashboard_views",
    "api_dashboard_chart_data": "dashboard_views",
    # auth_views.py
    "login_view": "auth_views",
    "logout_view": "auth_views",
    # inventory_views.py
    "products_view": "inventory_views",
    "product_detail_view": "inventory_views",
    "stock_planning_view": "inventory_views",
    "locations_view": "inventory_views",
    "products_import_template": "inventory_views",
    "products_import": "inventory_views",
    # stock_movement_views.py
    "stock_movement_view": "stock_movement_views",
    "export_stock_movement": "stock_movement_views",
    "add_stock_movement_view": "stock_movement_views",
    # masterdata_views.py
    "categories_list": "masterdata_views",
    "category_create": "masterdata_views",
    "category_update": "masterdata_views",
    "category_delete": "masterdata_views",
    "units_list": "masterdata_views",
    "unit_create": "masterdata_views",
    "unit_update": "masterdata_views",
    "unit_delete": "masterdata_views",
    "vendors_list": "masterdata_views",
    "vendor_create": "masterdata_views",
    "vendor_update": "masterdata_views",
    "vendor_delete": "masterdata_views",
    # customer_views.py
    "customer_list": "customer_views",
    "customer_detail": "customer_views",
    "customer_create": "customer_views",
    "customer_update": "customer_views",
    "customer_delete": "customer_views",
    "customer_redeem_points": "customer_views",
    # stock_opname_views.py
    "stock_opname_locations": "stock_opname_views",
    "stock_opname_form": "stock_opname_views",
    "stock_opname_approvals": "stock_opname_views",
    "stock_opname_approval_detail": "stock_opname_views",
    # api_views.py
    "submit_requisition": "api_views",
    "approve_requisition": "api_views",
    "confirm_receipt": "api_views",
    "submit_stock_allocation": "api_views",
    "get_location_stock": "api_views",
    "submit_purchases": "api_views",
    # production_views.py
    "recipe_list": "production_views",
    "recipe_form": "production_views",
    "recipe_detail": "production_views",
    "recipe_delete": "production_views",
    # pricing_views.py
    "supplier_price_list": "pricing_views",
    "supplier_price_form": "pricing_views",
    "supplier_price_delete": "pricing_views",
    # report_views.py
    "sales_report": "report_views",
    "transaction_summary": "report_views",
    "transfer_report": "report_views",
    "requisition_report": "report_views",
    "purchasing_report": "report_views",
    "report_inventory_log": "report_views",
    "report_inventory_low": "report_views",
    "report_inventory_stock": "report_views",
    "report_profit_loss_detail": "report_views",
    "report_sales_by_outlet": "report_views",
    "report_sales_by_payment": "report_views",
    "report_sales_by_product": "report_views",
    "report_sales_summary": "report_views",
    # misc_views.py
    "pos_view": "misc_views",
    "pos_create_order": "misc_views",
    "purchasing_view": "misc_views",
    "sales_history_view": "misc_views",
    "sales_history_products_view": "misc_views",
    "sales_performance_view": "misc_views",
    "campaign_list_view": "misc_views",
    "add_campaign_view": "misc_views",
    "edit_campaign_view": "misc_views",
    "delete_campaign_view": "misc_views",
    "discount_list_view": "misc_views",
    "add_discount_view": "misc_views",
    "edit_discount_view": "misc_views",
    "delete_discount_view": "misc_views",
    "loyalty_members_view": "misc_views",
    "add_loyalty_member_view": "misc_views",
    "edit_loyalty_member_view": "misc_views",
    "delete_loyalty_member_view": "misc_views",
    "financial_reports_view": "misc_views",
    "market_insights_view": "misc_views",
    "trends_analysis_view": "misc_views",
    "activity_log_view": "misc_views",
    "users_view": "misc_views",
    "profile_view": "misc_views",
    "settings_view": "misc_views",
    "system_status_view": "misc_views",
    "business_settings_view": "misc_views",
    "business_feature_matrix_view": "misc_views",
    "business_form_general_view": "misc_views",
    "user_roles_permissions_view": "misc_views",
    "download_report_view": "misc_views",
    "export_trends_view": "misc_views",
    "about_view": "misc_views",
    "contact_view": "misc_views",
    "search_view": "misc_views",
    "pricing_view": "misc_views",
    # helpers.py
    "parse_date_aware": "helpers",
    "smart_currency_format": "helpers",
    "safe_percent_format": "helpers",
}

# Mapping app stub → daftar fungsi yang perlu di-export
APP_STUB_EXPORTS = {
    "sales": [
        "dashboard_view", "notification_view", "pos_view", "pos_create_order",
        "sales_history_view", "sales_history_products_view", "sales_performance_view",
        "purchasing_view", "purchasing_report",
    ],
    "master_data": [
        "locations_view", "products_view", "product_detail_view",
        "categories_list", "category_create", "category_update", "category_delete",
        "units_list", "unit_create", "unit_update", "unit_delete",
        "vendors_list", "vendor_create", "vendor_update", "vendor_delete",
        "customer_list", "customer_create", "customer_detail", "customer_update",
        "customer_delete", "customer_redeem_points",
        "stock_opname_locations", "stock_opname_form",
        "stock_opname_approvals", "stock_opname_approval_detail",
        "report_sales_by_product",
    ],
    "inventory": [
        "products_import_template", "products_import",
        "stock_planning_view", "stock_movement_view", "add_stock_movement_view",
        "export_stock_movement", "supplier_price_list", "supplier_price_form",
        "supplier_price_delete", "approve_requisition", "submit_stock_allocation",
    ],
    "production": [
        "recipe_list", "recipe_form", "recipe_detail", "recipe_delete",
    ],
    "marketing": [
        "campaign_list_view", "add_campaign_view", "edit_campaign_view", "delete_campaign_view",
        "discount_list_view", "add_discount_view", "edit_discount_view", "delete_discount_view",
        "loyalty_members_view", "add_loyalty_member_view", "edit_loyalty_member_view",
        "delete_loyalty_member_view",
    ],
    "reports": [
        "financial_reports_view", "market_insights_view", "trends_analysis_view",
        "activity_log_view", "download_report_view", "export_trends_view",
        "sales_report", "transaction_summary", "transfer_report", "requisition_report",
        "report_inventory_log", "report_inventory_low", "report_inventory_stock",
        "report_profit_loss_detail", "report_sales_by_outlet", "report_sales_by_payment",
        "report_sales_summary",
    ],
    "settings_app": [
        "users_view", "profile_view", "settings_view", "system_status_view",
        "business_settings_view", "business_form_general_view",
        "business_feature_matrix_view", "user_roles_permissions_view",
        "about_view", "contact_view", "pricing_view", "search_view",
    ],
    "auth_app": [
        "login_view", "logout_view",
    ],
    "api": [
        "api_dashboard_data", "api_dashboard_chart_data",
        "submit_requisition", "submit_purchases", "confirm_receipt", "get_location_stock",
    ],
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def banner(text: str, char: str = "=") -> None:
    width = 60
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def info(text: str) -> None:
    print(f"  [INFO]  {text}")


def ok(text: str) -> None:
    print(f"  [ OK ]  {text}")


def warn(text: str) -> None:
    print(f"  [WARN]  {text}")


def err(text: str) -> None:
    print(f"  [ERR ]  {text}")


def adapt_imports(content: str, app_name: str = "lumra_config") -> str:
    """
    Ganti semua 'from core.' → 'from lumra_config.'
    dan 'from core import' → 'from lumra_config import'
    dan 'import core.' → 'import lumra_config.'
    Juga ganti template paths jika pakai 'lumra_pages/' agar tetap konsisten.
    """
    # Replace module imports
    content = re.sub(r'\bfrom core\.', f'from {app_name}.', content)
    content = re.sub(r'\bimport core\.', f'import {app_name}.', content)
    content = re.sub(r'\bfrom core\b', f'from {app_name}', content)
    # Replace internal views cross-references  
    content = content.replace('from .views import', f'from {app_name}.views import')
    return content


def extract_functions(filepath: Path) -> List[str]:
    """Ekstrak semua nama fungsi publik (bukan dimulai _) dari file Python."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        return re.findall(r'^def ([a-zA-Z][a-zA-Z0-9_]*)\s*\(', content, re.MULTILINE)
    except Exception:
        return []


def find_core_views_dir(core_dir: Path) -> Path:
    """Temukan folder core/views/."""
    candidates = [
        core_dir / "views",
        core_dir / "core" / "views",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    raise FileNotFoundError(f"Folder core/views/ tidak ditemukan di {core_dir}")


def find_lumra_config_dir(project_dir: Path) -> Path:
    """Temukan folder lumra_config/."""
    candidates = [
        project_dir / "lumra_config",
        project_dir / "lumra" / "lumra_config",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    raise FileNotFoundError(f"Folder lumra_config/ tidak ditemukan di {project_dir}")


# ============================================================
# STEP 1: SCAN CORE VIEWS
# ============================================================

def scan_core_views(core_views_dir: Path) -> Dict[str, Dict]:
    """
    Scan semua file views di core, return mapping:
    { "dashboard_views": {"path": Path, "functions": [...], "content": str} }
    """
    result = {}
    view_files = [
        "dashboard_views.py", "auth_views.py", "inventory_views.py",
        "stock_movement_views.py", "masterdata_views.py", "customer_views.py",
        "stock_opname_views.py", "api_views.py", "production_views.py",
        "pricing_views.py", "report_views.py", "reports_views.py",
        "misc_views.py", "helpers.py",
    ]
    for fname in view_files:
        fpath = core_views_dir / fname
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8", errors="replace")
            funcs = re.findall(r'^def ([a-zA-Z][a-zA-Z0-9_]*)\s*\(', content, re.MULTILINE)
            key = fname.replace(".py", "")
            result[key] = {"path": fpath, "functions": funcs, "content": content}
            ok(f"Ditemukan: {fname} ({len(funcs)} fungsi)")
        else:
            warn(f"Tidak ditemukan: {fname}")
    return result


# ============================================================
# STEP 2: BUAT STRUKTUR views/ DI lumra_config
# ============================================================

def create_lumra_views_structure(
    lumra_config_dir: Path,
    core_views: Dict[str, Dict],
    dry_run: bool = False,
) -> None:
    """
    Buat folder lumra_config/views/ dan copy semua file view dari core,
    ganti 'core.' → 'lumra_config.' dalam imports.
    """
    views_dir = lumra_config_dir / "views"

    if not dry_run:
        views_dir.mkdir(exist_ok=True)
        ok(f"Folder {views_dir} siap")

    # File yang akan dicopy dari core ke lumra_config/views/
    copy_map = {
        "dashboard_views": "dashboard_views.py",
        "auth_views": "auth_views.py",
        "inventory_views": "inventory_views.py",
        "stock_movement_views": "stock_movement_views.py",
        "masterdata_views": "masterdata_views.py",
        "customer_views": "customer_views.py",
        "stock_opname_views": "stock_opname_views.py",
        "api_views": "api_views.py",
        "production_views": "production_views.py",
        "pricing_views": "pricing_views.py",
        "report_views": "report_views.py",
        "misc_views": "misc_views.py",
        "helpers": "helpers.py",
    }

    # Handle reports_views → merge ke report_views jika perlu
    if "reports_views" in core_views and "report_views" in core_views:
        info("Menggabungkan reports_views.py (stock opname) → sudah ada di stock_opname_views.py, skip merge")

    for key, fname in copy_map.items():
        if key not in core_views:
            warn(f"  Skip {fname}: tidak ada di core")
            continue

        content = core_views[key]["content"]
        # Ganti imports
        adapted = adapt_imports(content)
        # Tambahkan header komentar
        header = f"# lumra_config/views/{fname}\n# Auto-generated oleh lumra_sync.py dari core/views/{fname}\n# JANGAN EDIT MANUAL — edit core/views/{fname} lalu jalankan lumra_sync.py lagi\n\n"
        # Hapus header lama '# core/views/...' jika ada
        adapted = re.sub(r'^# core/views/.*\n', '', adapted)
        final_content = header + adapted.lstrip()

        target = views_dir / fname
        if not dry_run:
            target.write_text(final_content, encoding="utf-8")
            ok(f"  Copied: {fname}")
        else:
            info(f"  [DRY] Would create: {target}")

    # Buat __init__.py
    _create_views_init(views_dir, core_views, dry_run)


def _create_views_init(views_dir: Path, core_views: Dict, dry_run: bool) -> None:
    """Buat lumra_config/views/__init__.py dengan semua exports."""
    all_exports = []

    # Kumpulkan semua fungsi publik dari semua modul
    module_exports = {}
    for key in ["dashboard_views", "auth_views", "inventory_views", "stock_movement_views",
                "masterdata_views", "customer_views", "stock_opname_views", "api_views",
                "production_views", "pricing_views", "report_views", "misc_views"]:
        if key in core_views:
            funcs = [f for f in core_views[key]["functions"] if not f.startswith("_")]
            module_exports[key] = funcs
            all_exports.extend(funcs)

    lines = [
        "# lumra_config/views/__init__.py",
        "# Central export point - auto-generated oleh lumra_sync.py",
        "# Semua view functions tersedia dari sini untuk diimpor oleh app stubs",
        "",
    ]

    for module, funcs in module_exports.items():
        if not funcs:
            continue
        lines.append(f"from .{module} import (")
        for f in funcs:
            lines.append(f"    {f},")
        lines.append(")")
        lines.append("")

    # helpers
    if "helpers" in core_views:
        helper_funcs = [f for f in core_views["helpers"]["functions"] if not f.startswith("_")]
        if helper_funcs:
            lines.append("from .helpers import (")
            for f in helper_funcs:
                lines.append(f"    {f},")
            lines.append(")")
            lines.append("")

    lines.append("")
    lines.append("__all__ = [")
    for f in sorted(set(all_exports)):
        lines.append(f"    '{f}',")
    lines.append("]")
    lines.append("")

    content = "\n".join(lines)
    target = views_dir / "__init__.py"

    if not dry_run:
        target.write_text(content, encoding="utf-8")
        ok(f"  Created: views/__init__.py ({len(all_exports)} fungsi di-export)")
    else:
        info(f"  [DRY] Would create: {target} ({len(all_exports)} exports)")


# ============================================================
# STEP 3: BUAT APP STUBS
# ============================================================

def create_app_stubs(lumra_config_dir: Path, dry_run: bool = False) -> None:
    """
    Buat views.py stub di setiap app folder yang dibutuhkan oleh urls.py.
    Setiap stub hanya mengimpor ulang dari lumra_config.views.
    """
    for app_name, funcs in APP_STUB_EXPORTS.items():
        app_dir = lumra_config_dir / app_name
        if not dry_run:
            app_dir.mkdir(exist_ok=True)

        # Buat __init__.py jika belum ada
        init_file = app_dir / "__init__.py"
        if not dry_run and not init_file.exists():
            init_file.write_text("", encoding="utf-8")

        # Buat views.py stub
        views_file = app_dir / "views.py"

        # Jangan overwrite jika sudah ada dan sudah punya konten yang bukan stub
        if views_file.exists() and not dry_run:
            existing = views_file.read_text(encoding="utf-8", errors="replace")
            if "auto-generated oleh lumra_sync" not in existing and len(existing) > 200:
                warn(f"  Skip stub {app_name}/views.py: sudah ada konten custom")
                continue

        func_list = "\n    ".join(funcs)
        content = f"""# lumra_config/{app_name}/views.py
# Auto-generated oleh lumra_sync.py
# Stub ini mengimpor ulang semua fungsi dari lumra_config.views
# sehingga urls.py bisa menggunakan path 'lumra_config.{app_name}.views.fungsi_name'

from lumra_config.views import (
    {func_list},
)

__all__ = {repr(funcs)}
"""
        if not dry_run:
            views_file.write_text(content, encoding="utf-8")
            ok(f"  Created stub: {app_name}/views.py ({len(funcs)} fungsi)")
        else:
            info(f"  [DRY] Would create stub: {app_name}/views.py")


# ============================================================
# STEP 4: VALIDASI urls.py
# ============================================================

def validate_urls(urls_file: Path, lumra_config_dir: Path) -> Tuple[List, List]:
    """
    Baca urls.py, ekstrak semua lazy_view() calls, cek apakah fungsinya ada.
    Returns: (ok_list, missing_list)
    """
    if not urls_file.exists():
        err(f"urls.py tidak ditemukan: {urls_file}")
        return [], []

    content = urls_file.read_text(encoding="utf-8", errors="replace")
    # Ekstrak semua 'lumra_config.X.Y.Z'
    calls = re.findall(r"lazy_view\(['\"]([^'\"]+)['\"]\)", content)

    ok_list = []
    missing_list = []

    for dotted_path in calls:
        parts = dotted_path.split(".")
        if len(parts) < 3:
            continue
        # Contoh: lumra_config.sales.views.dashboard_view
        # parts = ['lumra_config', 'sales', 'views', 'dashboard_view']
        if parts[0] != "lumra_config":
            continue

        app = parts[1]  # e.g. 'sales'
        # func bisa di views.func atau views submodule
        func_name = parts[-1]

        # Cek apakah app stub ada
        stub_views = lumra_config_dir / app / "views.py"

        if stub_views.exists():
            stub_content = stub_views.read_text(encoding="utf-8", errors="replace")
            if func_name in stub_content:
                ok_list.append((dotted_path, "stub ok"))
            else:
                missing_list.append((dotted_path, f"fungsi '{func_name}' tidak ada di {app}/views.py"))
        else:
            missing_list.append((dotted_path, f"file {app}/views.py belum dibuat"))

    return ok_list, missing_list


# ============================================================
# STEP 5: CEK TEMPLATE PATHS
# ============================================================

def check_templates(lumra_config_dir: Path, core_views: Dict) -> None:
    """
    Cek semua render(request, 'template_path') di core views.
    Laporkan template yang dipakai.
    """
    all_templates = set()
    for key, data in core_views.items():
        templates = re.findall(r"render\s*\([^,]+,\s*['\"]([^'\"]+)['\"]", data["content"])
        all_templates.update(templates)

    info(f"Template yang digunakan di core views ({len(all_templates)} total):")
    for t in sorted(all_templates):
        print(f"       {t}")


# ============================================================
# STEP 5: SYNC SUPPORT FILES
# ============================================================

def sync_support_files(lumra_config_dir: Path, core_dir: Path, dry_run: bool = False) -> None:
    """
    Sinkronisasi file pendukung dari core ke lumra_config:
      - middleware.py     → Dibutuhkan templates (user.profile, user.role, dll)
      - signals.py        → Auto stock deduction saat order
      - admin.py          → Registrasi model ke Django admin
      - context_processors.py → app_version di semua template
      - apps.py           → Konfigurasi ready() untuk signal
    """

    # Cari folder core root (bukan views)
    core_root = core_dir
    # Jika core_dir adalah folder views/, naik satu level
    if core_dir.name == "views":
        core_root = core_dir.parent

    support_files = [
        ("middleware.py",          _sync_middleware),
        ("signals.py",             _sync_signals),
        ("admin.py",               _sync_admin),
        ("context_processors.py",  _sync_context_processors),
        ("apps.py",                _sync_apps),
    ]

    for filename, handler in support_files:
        src = core_root / filename
        dst = lumra_config_dir / filename
        if src.exists():
            handler(src, dst, dry_run)
        else:
            warn(f"  {filename}: tidak ada di core, skip")


def _sync_middleware(src: Path, dst: Path, dry_run: bool) -> None:
    """Copy middleware.py, ganti 'core.' → 'lumra_config.'"""
    content = src.read_text(encoding="utf-8", errors="replace")
    adapted = adapt_imports(content)
    header = (
        "# lumra_config/middleware.py\n"
        "# Auto-sync dari core/middleware.py oleh lumra_sync.py\n"
        "# Dibutuhkan oleh templates: user.profile, user.role, user.avatar, dll.\n"
        "# WAJIB didaftarkan di settings.py → MIDDLEWARE\n\n"
    )
    final = header + adapted.lstrip("# core/middleware.py\n").lstrip()

    if not dry_run:
        dst.write_text(final, encoding="utf-8")
        ok(f"  middleware.py → sync ({len(final):,} chars)")
    else:
        info(f"  [DRY] Would sync: middleware.py")


def _sync_signals(src: Path, dst: Path, dry_run: bool) -> None:
    """Copy signals.py, ganti import core → lumra_config."""
    content = src.read_text(encoding="utf-8", errors="replace")
    adapted = adapt_imports(content)
    header = (
        "# lumra_config/signals.py\n"
        "# Auto-sync dari core/signals.py oleh lumra_sync.py\n"
        "# Menangani: pengurangan stock otomatis saat order, tracking customer, dll.\n"
        "# WAJIB: apps.py harus memanggil signals di ready()\n\n"
    )
    final = header + re.sub(r'^""".*?"""\n', '', adapted, flags=re.DOTALL).lstrip()

    if not dry_run:
        dst.write_text(final, encoding="utf-8")
        ok(f"  signals.py → sync")
    else:
        info(f"  [DRY] Would sync: signals.py")


def _sync_admin(src: Path, dst: Path, dry_run: bool) -> None:
    """Buat admin.py yang mendaftarkan semua model utama."""
    content = src.read_text(encoding="utf-8", errors="replace")
    adapted = adapt_imports(content)

    header = (
        "# lumra_config/admin.py\n"
        "# Auto-sync dari core/admin.py oleh lumra_sync.py\n\n"
    )

    # Cek apakah lumra admin.py sudah kosong atau minimal
    if dst.exists():
        existing = dst.read_text(encoding="utf-8", errors="replace").strip()
        if len(existing) > 100 and "auto-sync" not in existing.lower():
            warn(f"  admin.py sudah ada konten custom — tidak di-overwrite")
            return

    final = header + adapted.lstrip()

    if not dry_run:
        dst.write_text(final, encoding="utf-8")
        ok(f"  admin.py → sync (model registrations)")
    else:
        info(f"  [DRY] Would sync: admin.py")


def _sync_context_processors(src: Path, dst: Path, dry_run: bool) -> None:
    """
    Pastikan context_processors.py ada dan berisi app_settings.
    Lumra sudah punya file ini, tapi verifikasi isinya cukup.
    """
    content = src.read_text(encoding="utf-8", errors="replace")

    if dst.exists():
        existing = dst.read_text(encoding="utf-8", errors="replace")
        if "app_settings" in existing:
            ok(f"  context_processors.py → sudah OK (app_settings ada)")
            return
        # Append fungsi yang hilang
        if not dry_run:
            adapted = adapt_imports(content)
            merged = existing.rstrip() + "\n\n# Ditambahkan oleh lumra_sync.py\n" + adapted
            dst.write_text(merged, encoding="utf-8")
            ok(f"  context_processors.py → ditambahkan app_settings")
        else:
            info(f"  [DRY] Would add app_settings to context_processors.py")
    else:
        adapted = adapt_imports(content)
        if not dry_run:
            dst.write_text(adapted, encoding="utf-8")
            ok(f"  context_processors.py → dibuat baru")
        else:
            info(f"  [DRY] Would create: context_processors.py")


def _sync_apps(src: Path, dst: Path, dry_run: bool) -> None:
    """
    Update apps.py agar memanggil signals di ready().
    Ini penting agar signals.py bisa berjalan saat server start.
    """
    apps_content = """# lumra_config/apps.py
# Auto-updated oleh lumra_sync.py
# ready() diperlukan agar signals.py terdaftar saat Django startup

from django.apps import AppConfig


class LumraConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lumra_config'

    def ready(self):
        # Daftarkan signals — WAJIB agar auto stock deduction berjalan
        try:
            import lumra_config.signals  # noqa: F401
        except ImportError:
            pass
"""
    if dst.exists():
        existing = dst.read_text(encoding="utf-8", errors="replace")
        if "ready" in existing and "signals" in existing:
            ok(f"  apps.py → sudah ada ready() + signals")
            return

    if not dry_run:
        dst.write_text(apps_content, encoding="utf-8")
        ok(f"  apps.py → updated (ready() + signals)")
    else:
        info(f"  [DRY] Would update: apps.py")


# ============================================================
# STEP 6: PATCH settings.py
# ============================================================

def patch_settings(settings_file: Path, dry_run: bool = False) -> None:
    """
    Cek dan tambahkan konfigurasi yang hilang di lumra_system/settings.py:
      1. EnsureUserProfileMiddleware
      2. context_processors: lumra_config.context_processors.app_settings
      3. LOGIN_REDIRECT_URL
      4. APP_VERSION
      5. MEDIA_URL + MEDIA_ROOT
      6. TIME_ZONE Asia/Jakarta
      7. ALLOWED_HOSTS
    """
    content = settings_file.read_text(encoding="utf-8", errors="replace")
    original = content
    patches_applied = []

    # ── 1. EnsureUserProfileMiddleware ────────────────────────
    mw_line = "    'lumra_config.middleware.EnsureUserProfileMiddleware',"
    if "EnsureUserProfileMiddleware" not in content:
        # Insert setelah AuthenticationMiddleware
        content = content.replace(
            "    'django.contrib.auth.middleware.AuthenticationMiddleware',",
            "    'django.contrib.auth.middleware.AuthenticationMiddleware',\n"
            "    # Pastikan setiap user login punya UserProfile (dibutuhkan oleh templates)\n"
            f"{mw_line}"
        )
        patches_applied.append("+ EnsureUserProfileMiddleware")

    # ── 2. context_processors: app_settings ──────────────────
    cp_line = "                'lumra_config.context_processors.app_settings',"
    if "app_settings" not in content and "context_processors.app_settings" not in content:
        # Insert setelah messages context processor
        content = content.replace(
            "                'django.contrib.messages.context_processors.messages',",
            "                'django.contrib.messages.context_processors.messages',\n"
            f"{cp_line}"
        )
        patches_applied.append("+ context_processors.app_settings")

    # ── 3. LOGIN_REDIRECT_URL ─────────────────────────────────
    if "LOGIN_REDIRECT_URL" not in content:
        content += "\n# Redirect ke dashboard setelah login\nLOGIN_REDIRECT_URL = 'dashboard'\n"
        patches_applied.append("+ LOGIN_REDIRECT_URL")

    # ── 4. APP_VERSION ────────────────────────────────────────
    if "APP_VERSION" not in content:
        content += "\n# Versi aplikasi — tersedia di template via {{ app_version }}\nAPP_VERSION = '1.0.0'\n"
        patches_applied.append("+ APP_VERSION")

    # ── 5. MEDIA_URL + MEDIA_ROOT ─────────────────────────────
    if "MEDIA_URL" not in content:
        content += "\n# Media files (uploads)\nMEDIA_URL = '/media/'\nMEDIA_ROOT = BASE_DIR / 'media'\n"
        patches_applied.append("+ MEDIA_URL / MEDIA_ROOT")

    # ── 6. TIME_ZONE ─────────────────────────────────────────
    if "TIME_ZONE = 'UTC'" in content:
        content = content.replace("TIME_ZONE = 'UTC'", "TIME_ZONE = 'Asia/Jakarta'")
        patches_applied.append("TIME_ZONE → Asia/Jakarta")

    # ── 7. ALLOWED_HOSTS ─────────────────────────────────────
    if "ALLOWED_HOSTS = []" in content:
        content = content.replace(
            "ALLOWED_HOSTS = []",
            "ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']"
        )
        patches_applied.append("ALLOWED_HOSTS → localhost")

    # ── 8. CSRF_TRUSTED_ORIGINS ──────────────────────────────
    if "CSRF_TRUSTED_ORIGINS" not in content:
        content += "\nCSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']\n"
        patches_applied.append("+ CSRF_TRUSTED_ORIGINS")

    # ── 9. DEBUG context processor ──────────────────────────
    if "'django.template.context_processors.debug'" not in content:
        content = content.replace(
            "                'django.template.context_processors.request',",
            "                'django.template.context_processors.debug',\n"
            "                'django.template.context_processors.request',"
        )
        patches_applied.append("+ context_processors.debug")

    if patches_applied:
        if not dry_run:
            settings_file.write_text(content, encoding="utf-8")
            ok(f"  settings.py diperbarui: {len(patches_applied)} patch")
            for p in patches_applied:
                info(f"    {p}")
        else:
            info(f"  [DRY] Would patch settings.py: {patches_applied}")
    else:
        ok(f"  settings.py → sudah lengkap, tidak ada yang diubah")

    # ── Report apa yang sudah ada ─────────────────────────────
    checks = {
        "EnsureUserProfileMiddleware": "EnsureUserProfileMiddleware" in content,
        "app_settings context processor": "app_settings" in content,
        "LOGIN_REDIRECT_URL": "LOGIN_REDIRECT_URL" in content,
        "APP_VERSION": "APP_VERSION" in content,
        "MEDIA_URL": "MEDIA_URL" in content,
        "TIME_ZONE Asia/Jakarta": "Asia/Jakarta" in content,
        "django_browser_reload": "django_browser_reload" in content,
    }
    for label, status in checks.items():
        if status:
            ok(f"    ✓ {label}")
        else:
            warn(f"    ✗ {label} — masih belum ada")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Sinkronisasi logika core → lumra")
    parser.add_argument(
        "--project-dir", "-p",
        default=".",
        help="Folder root project lumra (default: current dir)"
    )
    parser.add_argument(
        "--core-dir", "-c",
        default=None,
        help="Folder root project core/lama (default: auto-detect dari ../core)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Hanya tampilkan apa yang akan dilakukan, jangan ubah file"
    )
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="Hanya validasi urls.py tanpa membuat file baru"
    )
    parser.add_argument(
        "--check-templates",
        action="store_true",
        help="Tampilkan daftar semua template yang digunakan"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    
    if args.core_dir:
        core_dir = Path(args.core_dir).resolve()
    else:
        # Auto-detect: coba beberapa lokasi umum
        candidates = [
            project_dir.parent / "core",
            project_dir / "core",
            project_dir.parent / "core_old",
        ]
        core_dir = None
        for c in candidates:
            if (c / "views").is_dir():
                core_dir = c
                break
        if core_dir is None:
            err("Folder core tidak ditemukan. Gunakan --core-dir untuk menentukan lokasinya.")
            print("\nContoh: python lumra_sync.py --core-dir /path/ke/folder/core")
            sys.exit(1)

    banner("LUMRA SYNC — Mulai Sinkronisasi")
    print(f"  Project (lumra) : {project_dir}")
    print(f"  Core (lama)     : {core_dir}")
    print(f"  Dry run         : {args.dry_run}")

    # ── Find directories ──────────────────────────────────────
    try:
        core_views_dir = find_core_views_dir(core_dir)
        info(f"Core views dir  : {core_views_dir}")
    except FileNotFoundError as e:
        err(str(e))
        sys.exit(1)

    try:
        lumra_config_dir = find_lumra_config_dir(project_dir)
        info(f"lumra_config dir: {lumra_config_dir}")
    except FileNotFoundError as e:
        err(str(e))
        sys.exit(1)

    # ── Cari urls.py ─────────────────────────────────────────
    lumra_system_urls = None
    for candidate in [
        project_dir / "lumra_system" / "urls.py",
        project_dir / "lumra" / "lumra_system" / "urls.py",
        project_dir.parent / "lumra_system" / "urls.py",
    ]:
        if candidate.exists():
            lumra_system_urls = candidate
            break
    if lumra_system_urls is None:
        # fallback: cari rekursif
        for p in project_dir.rglob("urls.py"):
            if "lumra_system" in str(p):
                lumra_system_urls = p
                break
    if lumra_system_urls:
        info(f"urls.py ditemukan: {lumra_system_urls}")
    else:
        warn("urls.py (lumra_system) tidak ditemukan — validasi dilewati")

    # ── STEP 1: Scan core views ───────────────────────────────
    banner("STEP 1: Scan Core Views", "-")
    core_views = scan_core_views(core_views_dir)

    if args.check_templates:
        banner("TEMPLATE PATHS", "-")
        check_templates(lumra_config_dir, core_views)
        return

    if args.validate_only:
        if lumra_system_urls:
            banner("VALIDASI urls.py", "-")
            ok_list, missing_list = validate_urls(lumra_system_urls, lumra_config_dir)
            ok(f"{len(ok_list)} paths OK")
            if missing_list:
                err(f"{len(missing_list)} paths BERMASALAH:")
                for path, reason in missing_list:
                    print(f"       ✗ {path}")
                    print(f"         Alasan: {reason}")
            else:
                ok("Semua URL paths valid!")
        return

    # ── STEP 2: Buat views/ structure ─────────────────────────
    banner("STEP 2: Buat lumra_config/views/", "-")
    create_lumra_views_structure(lumra_config_dir, core_views, args.dry_run)

    # ── STEP 3: Buat app stubs ────────────────────────────────
    banner("STEP 3: Buat App Stubs", "-")
    create_app_stubs(lumra_config_dir, args.dry_run)

    # ── STEP 4: Validasi ─────────────────────────────────────
    if lumra_system_urls:
        banner("STEP 4: Validasi urls.py", "-")
        ok_list, missing_list = validate_urls(lumra_system_urls, lumra_config_dir)
        ok(f"{len(ok_list)} URL paths valid")
        if missing_list:
            warn(f"{len(missing_list)} URL paths masih bermasalah:")
            for path, reason in missing_list:
                print(f"       ✗ {path}")
                print(f"         → {reason}")
        else:
            ok("Semua URL paths valid! ✓")

    # ── STEP 5: Sync support files ────────────────────────────
    banner("STEP 5: Sinkronisasi File Pendukung", "-")
    sync_support_files(lumra_config_dir, core_dir, args.dry_run)

    # ── STEP 6: Patch settings.py ─────────────────────────────
    lumra_settings = None
    for candidate in [
        project_dir / "lumra_system" / "settings.py",
        project_dir / "lumra" / "lumra_system" / "settings.py",
    ]:
        if candidate.exists():
            lumra_settings = candidate
            break
    if lumra_settings:
        banner("STEP 6: Cek & Patch settings.py", "-")
        patch_settings(lumra_settings, args.dry_run)
    else:
        warn("settings.py lumra_system tidak ditemukan — skip patch")

    # ── SUMMARY ───────────────────────────────────────────────
    banner("SELESAI")
    print("""
  Langkah selanjutnya:
  1. Jalankan: python manage.py check
  2. Jalankan: python manage.py makemigrations && python manage.py migrate
  3. Jika ada error 'cannot import name X', periksa:
       lumra_config/views/__init__.py
     dan pastikan fungsi X ada di salah satu file views/*.py
  4. Jika ada TemplateDoesNotExist:
       Jalankan: python lumra_sync.py --check-templates
     dan pastikan TEMPLATES dir di settings.py sudah benar
  5. Untuk validasi saja (tanpa mengubah file):
       python lumra_sync.py --validate-only
    """)


if __name__ == "__main__":
    main()