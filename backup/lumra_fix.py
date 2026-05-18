#!/usr/bin/env python3
"""
lumra_fix.py v2 — Validator & Auto-Fixer Lumra ERP
====================================================
Mendeteksi dan memperbaiki semua masalah agar Django bisa berjalan:

  1. SyntaxError pada stub views.py (import tanpa koma)
  2. Import 'from core.' yang belum diganti ke 'from lumra_config.'
  3. Template HTML yang direferensikan views tapi tidak ada → copy dari core
  4. Template yang pathnya berubah (mis: views render lumra_pages/campaign.html
     padahal di core ada di lumra_pages/campaign/campaign_list.html)
  5. Validasi settings.py

CARA PAKAI:
    python lumra_fix.py
    python lumra_fix.py --project-dir D:\APPS\Project\lumra --core-dir D:\APPS\Project\core
    python lumra_fix.py --check-only    # hanya laporan, tidak ubah file
    python lumra_fix.py --templates     # fokus ke template saja
"""

import ast, os, re, sys, shutil, argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# ── Warna terminal ──────────────────────────────────────────
def _c(code): return f"\033[{code}m"
R=_c(0); B=_c(1); RED=_c(31); GRN=_c(32); YLW=_c(33); CYN=_c(36)
def ok(m):   print(f"  {GRN}OK{R}  {m}")
def err(m):  print(f"  {RED}XX{R}  {m}")
def warn(m): print(f"  {YLW}!!{R}  {m}")
def info(m): print(f"  {CYN}->{R}  {m}")
def banner(m, c="="):
    print(f"\n{B}{c*62}{R}\n{B}  {m}{R}\n{B}{c*62}{R}")
def sub(m):
    print(f"\n  {B}{CYN}{m}{R}\n  {chr(9472)*52}")


# ======================================================
# BAGIAN 1 — STUB VIEWS.PY FIXER
# ======================================================

APP_REQUIRED_FUNCTIONS = {
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
    "production": ["recipe_list", "recipe_form", "recipe_detail", "recipe_delete"],
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
    "auth_app": ["login_view", "logout_view"],
    "api": [
        "api_dashboard_data", "api_dashboard_chart_data",
        "submit_requisition", "submit_purchases", "confirm_receipt", "get_location_stock",
    ],
}


def check_syntax(path):
    try:
        ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return None
    except SyntaxError as e:
        return f"baris {e.lineno}: {e.msg}"


def rebuild_stub(path, app, funcs):
    """Buat stub views.py dengan syntax benar — koma di setiap baris."""
    path.parent.mkdir(parents=True, exist_ok=True)
    init = path.parent / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")

    imports = ",\n    ".join(funcs)
    all_list = ", ".join(f"'{f}'" for f in funcs)
    path.write_text(
        f"# lumra_config/{app}/views.py\n"
        f"# Auto-generated oleh lumra_fix.py\n\n"
        f"from lumra_config.views import (\n"
        f"    {imports},\n"
        f")\n\n"
        f"__all__ = [{all_list}]\n",
        encoding="utf-8"
    )


def scan_available_functions(views_dir):
    funcs = set()
    if not views_dir.exists():
        return funcs
    for p in views_dir.glob("*.py"):
        if p.name == "__init__.py":
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            funcs.update(f for f in re.findall(r"^def ([a-zA-Z]\w*)\s*\(", src, re.MULTILINE)
                         if not f.startswith("_"))
        except Exception:
            pass
    return funcs


def extract_url_functions(urls_file):
    if not urls_file or not urls_file.exists():
        return {}
    src = urls_file.read_text(encoding="utf-8", errors="replace")
    result = {}
    for app, func in re.findall(
            r"lazy_view\(['\"]lumra_config\.(\w+)\.views\.(\w+)['\"]\)", src):
        result.setdefault(app, [])
        if func not in result[app]:
            result[app].append(func)
    return result


def fix_stubs(lumra_config_dir, views_dir, urls_file, dry_run):
    available = scan_available_functions(views_dir)
    url_funcs = extract_url_functions(urls_file)
    fixed = 0

    all_apps = set(list(url_funcs.keys()) + list(APP_REQUIRED_FUNCTIONS.keys()))
    for app in sorted(all_apps):
        stub = lumra_config_dir / app / "views.py"
        needed = list(dict.fromkeys(
            url_funcs.get(app, []) + APP_REQUIRED_FUNCTIONS.get(app, [])
        ))
        valid = [f for f in needed if f in available] if available else needed
        missing = [f for f in needed if f not in available] if available else []
        if missing:
            warn(f"  {app}/views.py — belum ada di views/: {missing[:3]}"
                 + ("..." if len(missing) > 3 else ""))
        if not valid:
            warn(f"  {app}/views.py — tidak ada fungsi valid, skip")
            continue

        needs_fix = (not stub.exists() or check_syntax(stub) is not None
                     or any(f not in stub.read_text(encoding="utf-8", errors="replace")
                            for f in valid[:3]))
        if needs_fix:
            if not dry_run:
                rebuild_stub(stub, app, valid)
                e = check_syntax(stub)
                if e:
                    err(f"  {app}/views.py — masih error: {e}")
                else:
                    ok(f"  {app}/views.py — rebuilt ({len(valid)} fungsi)")
                    fixed += 1
            else:
                info(f"  [DRY] Would rebuild: {app}/views.py ({len(valid)} fungsi)")
                fixed += 1
        else:
            ok(f"  {app}/views.py — OK ({len(valid)} fungsi)")
    return fixed


def rebuild_views_init(views_dir, dry_run):
    if not views_dir.exists():
        return False
    module_funcs = {}
    for p in sorted(views_dir.glob("*.py")):
        if p.name == "__init__.py":
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            funcs = [f for f in re.findall(r"^def ([a-zA-Z]\w*)\s*\(", src, re.MULTILINE)
                     if not f.startswith("_")]
            if funcs:
                module_funcs[p.stem] = funcs
        except Exception:
            pass

    lines = ["# lumra_config/views/__init__.py", "# Auto-rebuilt oleh lumra_fix.py", ""]
    all_exports = []
    for mod, funcs in sorted(module_funcs.items()):
        lines.append(f"from .{mod} import (")
        for f in funcs:
            lines.append(f"    {f},")
        lines.append(")")
        lines.append("")
        all_exports.extend(funcs)
    lines += ["__all__ = ["] + [f"    '{f}'," for f in sorted(set(all_exports))] + ["]", ""]

    init = views_dir / "__init__.py"
    if not dry_run:
        init.write_text("\n".join(lines), encoding="utf-8")
        ok(f"  views/__init__.py — rebuilt ({len(all_exports)} exports)")
    else:
        info(f"  [DRY] Would rebuild views/__init__.py")
    return True


# ======================================================
# BAGIAN 2 — IMPORT FIXER
# ======================================================

def fix_core_imports(scan_dir, dry_run):
    fixed = 0
    for pyfile in sorted(scan_dir.rglob("*.py")):
        if "__pycache__" in str(pyfile) or "migrations" in str(pyfile):
            continue
        try:
            src = pyfile.read_text(encoding="utf-8", errors="replace")
            new = re.sub(r"\bfrom core\.", "from lumra_config.", src)
            new = re.sub(r"\bimport core\.", "import lumra_config.", new)
            new = re.sub(r"\bfrom core\b", "from lumra_config", new)
            if new != src:
                rel = pyfile.relative_to(scan_dir.parent)
                if not dry_run:
                    pyfile.write_text(new, encoding="utf-8")
                    ok(f"  {rel}")
                else:
                    info(f"  [DRY] {rel}")
                fixed += 1
        except Exception as e:
            err(f"  {pyfile.name}: {e}")
    if fixed == 0:
        ok("  Tidak ada import 'core.' yang tersisa")
    return fixed


# ======================================================
# BAGIAN 3 — TEMPLATE SYNC
# ======================================================

# Mapping: path yg di-render views -> path di core/templates
# Jika path sama, cukup copy. Jika beda, ini adalah rename/alias.
TEMPLATE_MAP = {
    # Same path — langsung copy
    "lumra_pages/auth/login.html":                          "lumra_pages/auth/login.html",
    "lumra_pages/about.html":                               "lumra_pages/about.html",
    "lumra_pages/activity_log.html":                        "lumra_pages/activity_log.html",
    "lumra_pages/add_stock_movement.html":                  "lumra_pages/add_stock_movement.html",
    "lumra_pages/contact.html":                             "lumra_pages/contact.html",
    "lumra_pages/dashboard.html":                           "lumra_pages/dashboard.html",
    "lumra_pages/error_403.html":                           "lumra_pages/error_403.html",
    "lumra_pages/error_404.html":                           "lumra_pages/error_404.html",
    "lumra_pages/error_500.html":                           "lumra_pages/error_500.html",
    "lumra_pages/notification.html":                        "lumra_pages/notification.html",
    "lumra_pages/pricing.html":                             "lumra_pages/pricing.html",
    "lumra_pages/search.html":                              "lumra_pages/search.html",
    "lumra_pages/stock_movement.html":                      "lumra_pages/stock_movement.html",
    "lumra_pages/user_roles_permissions.html":              "lumra_pages/user_roles_permissions.html",
    "lumra_pages/users.html":                               "lumra_pages/users.html",
    "lumra_pages/master_data/categories_list.html":         "lumra_pages/master_data/categories_list.html",
    "lumra_pages/master_data/category_form.html":           "lumra_pages/master_data/category_form.html",
    "lumra_pages/master_data/customer_detail.html":         "lumra_pages/master_data/customer_detail.html",
    "lumra_pages/master_data/customer_form.html":           "lumra_pages/master_data/customer_form.html",
    "lumra_pages/master_data/customers_list.html":          "lumra_pages/master_data/customers_list.html",
    "lumra_pages/master_data/locations.html":               "lumra_pages/master_data/locations.html",
    "lumra_pages/master_data/unit_form.html":               "lumra_pages/master_data/unit_form.html",
    "lumra_pages/master_data/units_list.html":              "lumra_pages/master_data/units_list.html",
    "lumra_pages/master_data/vendor_form.html":             "lumra_pages/master_data/vendor_form.html",
    "lumra_pages/master_data/vendors_list.html":            "lumra_pages/master_data/vendors_list.html",
    "lumra_pages/inventory/product_details.html":           "lumra_pages/inventory/product_details.html",
    "lumra_pages/inventory/products.html":                  "lumra_pages/inventory/products.html",
    "lumra_pages/inventory/stock_opname_approval_detail.html": "lumra_pages/inventory/stock_opname_approval_detail.html",
    "lumra_pages/inventory/stock_opname_approvals.html":    "lumra_pages/inventory/stock_opname_approvals.html",
    "lumra_pages/inventory/stock_opname_form.html":         "lumra_pages/inventory/stock_opname_form.html",
    "lumra_pages/inventory/stock_opname_locations.html":    "lumra_pages/inventory/stock_opname_locations.html",
    "lumra_pages/inventory/stock_planning.html":            "lumra_pages/inventory/stock_planning.html",
    "lumra_pages/inventory/supplier_price_form.html":       "lumra_pages/inventory/supplier_price_form.html",
    "lumra_pages/inventory/supplier_price_list.html":       "lumra_pages/inventory/supplier_price_list.html",
    "lumra_pages/production/recipe_form.html":              "lumra_pages/production/recipe_form.html",
    "lumra_pages/production/recipe_list.html":              "lumra_pages/production/recipe_list.html",
    "lumra_pages/reports/financial_reports.html":           "lumra_pages/reports/financial_reports.html",
    "lumra_pages/reports/purchasing_report.html":           "lumra_pages/reports/purchasing_report.html",
    "lumra_pages/reports/report_inventory_log.html":        "lumra_pages/reports/report_inventory_log.html",
    "lumra_pages/reports/report_inventory_low.html":        "lumra_pages/reports/report_inventory_low.html",
    "lumra_pages/reports/report_inventory_stock.html":      "lumra_pages/reports/report_inventory_stock.html",
    "lumra_pages/reports/report_profit_loss_detail.html":   "lumra_pages/reports/report_profit_loss_detail.html",
    "lumra_pages/reports/report_sales_by_outlet.html":      "lumra_pages/reports/report_sales_by_outlet.html",
    "lumra_pages/reports/report_sales_by_payment.html":     "lumra_pages/reports/report_sales_by_payment.html",
    "lumra_pages/reports/report_sales_by_product.html":     "lumra_pages/reports/report_sales_by_product.html",
    "lumra_pages/reports/report_sales_summary.html":        "lumra_pages/reports/report_sales_summary.html",
    "lumra_pages/reports/requisition_report.html":          "lumra_pages/reports/requisition_report.html",
    "lumra_pages/reports/sales_history.html":               "lumra_pages/reports/sales_history.html",
    "lumra_pages/reports/sales_history_product.html":       "lumra_pages/reports/sales_history_product.html",
    "lumra_pages/reports/sales_performance.html":           "lumra_pages/reports/sales_performance.html",
    "lumra_pages/reports/sales_report.html":                "lumra_pages/reports/sales_report.html",
    "lumra_pages/reports/transaction_summary.html":         "lumra_pages/reports/transaction_summary.html",
    "lumra_pages/reports/transfer_report.html":             "lumra_pages/reports/transfer_report.html",
    "lumra_pages/sales/pos.html":                           "lumra_pages/sales/pos.html",
    "lumra_pages/sales/purchasing.html":                    "lumra_pages/sales/purchasing.html",
    "lumra_pages/settings/business_feature_matrix.html":    "lumra_pages/settings/business_feature_matrix.html",
    "lumra_pages/settings/business_form_general.html":      "lumra_pages/settings/business_form_general.html",
    "lumra_pages/settings/business_settings.html":          "lumra_pages/settings/business_settings.html",
    "lumra_pages/settings/settings.html":                   "lumra_pages/settings/settings.html",
    "lumra_pages/settings/system_status.html":              "lumra_pages/settings/system_status.html",
    # Alias — path di views BERBEDA dari path di core
    "lumra_pages/campaign.html":            "lumra_pages/campaign/campaign_list.html",
    "lumra_pages/discount.html":            "lumra_pages/campaign/discount.html",
    "lumra_pages/loyalty_members.html":     "lumra_pages/campaign/loyalty_members.html",
    "lumra_pages/market_insights.html":     "lumra_pages/campaign/market_insights.html",
    "lumra_pages/trends_analysis.html":     "lumra_pages/campaign/trends_analysis.html",
    "lumra_pages/profile.html":             "lumra_pages/settings/profile.html",
    "lumra_pages/customers.html":           "lumra_pages/master_data/customers_list.html",
    # Fallback — pakai template terdekat karena original tidak ada
    "lumra_pages/production/recipe_detail.html":                "lumra_pages/production/recipe_list.html",
    "lumra_pages/inventory/supplier_price_confirm_delete.html": "lumra_pages/inventory/supplier_price_list.html",
}


def sync_templates(lumra_tpl_dir, core_tpl_dir, views_dir, dry_run):
    if not dry_run:
        lumra_tpl_dir.mkdir(parents=True, exist_ok=True)

    # Kumpulkan semua render() refs dari views
    refs = set()
    if views_dir.exists():
        for p in views_dir.glob("*.py"):
            try:
                src = p.read_text(encoding="utf-8", errors="replace")
                refs.update(re.findall(r"render\s*\([^,]+,\s*['\"]([^'\"]+)['\"]", src))
            except Exception:
                pass

    copied = skipped = 0
    still_missing = []

    for ref in sorted(refs):
        dest = lumra_tpl_dir / ref
        if dest.exists():
            skipped += 1
            continue

        # Cari di mapping
        core_rel = TEMPLATE_MAP.get(ref)
        src_file = None

        if core_rel and core_tpl_dir:
            candidate = core_tpl_dir / core_rel
            if candidate.exists():
                src_file = candidate
                note = f" (alias dari {core_rel})" if core_rel != ref else ""

        # Fallback: cari berdasarkan nama file
        if not src_file and core_tpl_dir:
            fname = Path(ref).name
            matches = list(core_tpl_dir.rglob(fname))
            if matches:
                src_file = matches[0]
                note = f" (auto-match)"

        if src_file:
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest)
                ok(f"  {ref}{note}")
            else:
                info(f"  [DRY] {ref}")
            copied += 1
        else:
            still_missing.append(ref)

    return copied, skipped, still_missing


# ======================================================
# BAGIAN 4 — SETTINGS CHECK
# ======================================================

def check_settings(settings_file):
    if not settings_file or not settings_file.exists():
        return ["settings.py tidak ditemukan"]
    content = settings_file.read_text(encoding="utf-8", errors="replace")
    checks = {
        "EnsureUserProfileMiddleware": "lumra_config.middleware",
        "app_settings context processor": "context_processors.app_settings",
        "LOGIN_REDIRECT_URL": "LOGIN_REDIRECT_URL",
        "APP_VERSION": "APP_VERSION",
        "MEDIA_URL": "MEDIA_URL",
        "TIME_ZONE Asia/Jakarta": "Asia/Jakarta",
    }
    return [label for label, kw in checks.items() if kw not in content]


# ======================================================
# MAIN
# ======================================================

def find_path(base, *candidates):
    for c in candidates:
        p = base / c
        if p.exists():
            return p
    return None


def main():
    parser = argparse.ArgumentParser(description="Lumra ERP — Auto-Fixer v2")
    parser.add_argument("--project-dir", "-p", default=".")
    parser.add_argument("--core-dir", "-c", default=None)
    parser.add_argument("--check-only", "-n", action="store_true")
    parser.add_argument("--templates", "-t", action="store_true")
    args = parser.parse_args()

    dry_run = args.check_only
    project_dir = Path(args.project_dir).resolve()

    banner("LUMRA FIX v2 — Validator & Auto-Fixer")
    print(f"  Project : {project_dir}")
    print(f"  Mode    : {'CHECK ONLY' if dry_run else 'FIX'}")

    lumra_config_dir = find_path(project_dir, "lumra_config", "lumra/lumra_config")
    if not lumra_config_dir:
        err("lumra_config/ tidak ditemukan.")
        sys.exit(1)
    info(f"lumra_config : {lumra_config_dir}")

    views_dir = lumra_config_dir / "views"

    # Locate core
    if args.core_dir:
        core_dir = Path(args.core_dir).resolve()
    else:
        core_dir = None
        for c in [project_dir.parent / "core", project_dir / "core",
                  project_dir.parent / "core_old"]:
            if c.is_dir():
                core_dir = c
                break

    core_tpl_dir = None
    if core_dir:
        for ct in [core_dir / "templates", core_dir / "core" / "templates"]:
            if ct.exists():
                core_tpl_dir = ct
                break
        info(f"core dir     : {core_dir}")
    else:
        warn("core dir tidak ditemukan — gunakan --core-dir jika perlu sync template")

    # Locate lumra templates
    lumra_tpl_dir = (find_path(lumra_config_dir, "templates")
                     or lumra_config_dir / "templates")

    urls_file     = find_path(project_dir, "lumra_system/urls.py", "lumra/lumra_system/urls.py")
    settings_file = find_path(project_dir, "lumra_system/settings.py", "lumra/lumra_system/settings.py")

    total_fixed = 0

    if args.templates:
        sub("TEMPLATE SYNC")
        if not core_tpl_dir:
            err("--templates memerlukan --core-dir")
            sys.exit(1)
        c, s, miss = sync_templates(lumra_tpl_dir, core_tpl_dir, views_dir, dry_run)
        ok(f"{c} template di-copy, {s} sudah ada")
        if miss:
            warn(f"{len(miss)} template tidak ditemukan (buat manual):")
            for m in miss:
                print(f"    !! {m}")
        return

    # STEP 1 — Syntax check
    sub("STEP 1 — Cek Syntax Semua File Python")
    syntax_errors = []
    for pyfile in sorted(lumra_config_dir.rglob("*.py")):
        if "__pycache__" in str(pyfile) or "migrations" in str(pyfile):
            continue
        e = check_syntax(pyfile)
        if e:
            syntax_errors.append((pyfile.relative_to(lumra_config_dir.parent), e))
    if syntax_errors:
        err(f"{len(syntax_errors)} file punya SyntaxError:")
        for rel, msg in syntax_errors:
            print(f"    XX {rel}  ({msg})")
    else:
        ok("Semua file Python — syntax OK")

    # STEP 2 — Fix core imports
    sub("STEP 2 — Fix Import 'core.' -> 'lumra_config.'")
    n = fix_core_imports(lumra_config_dir, dry_run)
    total_fixed += n

    # STEP 3 — Rebuild views/__init__.py
    sub("STEP 3 — Rebuild views/__init__.py")
    if views_dir.exists():
        rebuild_views_init(views_dir, dry_run)
        total_fixed += 1
    else:
        warn("views/ belum ada — jalankan lumra_sync.py dulu")

    # STEP 4 — Fix stub views.py
    sub("STEP 4 — Fix & Rebuild App Stub views.py")
    n = fix_stubs(lumra_config_dir, views_dir, urls_file, dry_run)
    total_fixed += n

    # STEP 5 — Template sync
    sub("STEP 5 — Sinkronisasi Template HTML dari Core")
    if core_tpl_dir:
        c, s, miss = sync_templates(lumra_tpl_dir, core_tpl_dir, views_dir, dry_run)
        ok(f"{c} template di-copy dari core")
        ok(f"{s} template sudah ada")
        if miss:
            warn(f"{len(miss)} template tidak ada di core manapun (buat manual):")
            for m in miss:
                print(f"    !! {m}")
        total_fixed += c
    else:
        warn("core dir tidak diketahui — lewati sync template")
        info("Gunakan: python lumra_fix.py --core-dir /path/ke/core")

    # STEP 6 — Final syntax check
    sub("STEP 6 — Verifikasi Final Syntax")
    errors_after = []
    for pyfile in sorted(lumra_config_dir.rglob("*.py")):
        if "__pycache__" in str(pyfile) or "migrations" in str(pyfile):
            continue
        e = check_syntax(pyfile)
        if e:
            errors_after.append((pyfile.relative_to(lumra_config_dir.parent), e))
    if errors_after:
        err(f"{len(errors_after)} file MASIH punya SyntaxError:")
        for rel, msg in errors_after:
            print(f"    XX {rel}  ({msg})")
    else:
        ok("Semua file Python — syntax BERSIH")

    # STEP 7 — Settings check
    sub("STEP 7 — Cek settings.py")
    issues = check_settings(settings_file)
    if issues:
        warn(f"settings.py perlu diperbarui ({len(issues)} item):")
        for i in issues:
            print(f"    !! {i}")
        info("Jalankan lumra_sync.py untuk auto-patch settings.py")
    else:
        ok("settings.py — semua konfigurasi wajib ada")

    # Summary
    banner("HASIL AKHIR")
    if not dry_run:
        print(f"  Perubahan    : {total_fixed} item diperbaiki")
        print(f"  Syntax error : {len(errors_after)} file")
    else:
        print(f"  [CHECK ONLY] — tidak ada yang diubah")
    if not errors_after:
        print(f"\n  Siap! Jalankan:")
        print(f"    python manage.py check")
        print(f"    python manage.py runserver")
    else:
        print(f"\n  Masih ada error — cek file di atas")


if __name__ == "__main__":
    main()