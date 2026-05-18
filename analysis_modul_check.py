#!/usr/bin/env python3
"""
Analisa Kesesuaian Module Structure dengan petunjuk_modul.md
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# ==================== DATA DARI PETUNJUK_MODUL ====================

REQUIRED_TEMPLATES = {
    "MODUL_1_SHARED": [
        "base.html", "empty_state.html", "pagination.html", "confirm_modal.html"
    ],
    "MODUL_2_AUTH": [
        "login.html", "register.html", "forgot_password.html", "verify_email.html",
        "reset_password.html", "two_factor.html", "lock_screen.html", "session_expired.html"
    ],
    "MODUL_3_ONBOARDING": [
        "welcome.html", "step_business.html", "step_location.html", 
        "step_category.html", "step_complete.html"
    ],
    "MODUL_4_INVENTORY": [
        "stock_overview.html", "stock_movement.html", "stock_movement_form.html",
        "stock_planning.html", "stock_opname_locations.html", "stock_opname_form.html",
        "stock_opname_approvals.html", "stock_opname_approval_detail.html",
        "stock_opname_session_detail.html", "requisition_list.html", "requisition_form.html",
        "requisition_detail.html", "batch_list.html", "batch_form.html", "batch_detail.html",
        "expiry_tracking.html", "warehouse_zones.html", "warehouse_zone_form.html",
        "adjustment_reasons.html", "supplier_evaluation.html"
    ],
    "MODUL_5_SALES": [
        "pos.html", "order_list.html", "order_detail.html", "sales_order_list.html",
        "sales_order_form.html", "sales_order_detail.html", "quotation_list.html",
        "quotation_form.html", "quotation_detail.html", "invoice_list.html",
        "invoice_form.html", "invoice_detail.html", "payment_list.html",
        "payment_form.html", "retur_list.html", "retur_form.html", "retur_detail.html"
    ],
    "MODUL_6_PRODUCTION": [
        "recipe_list.html", "recipe_form.html", "recipe_detail.html",
        "production_order_list.html", "production_order_form.html",
        "production_order_detail.html", "bom_list.html", "bom_form.html",
        "bom_detail.html", "production_scheduling.html", "material_consumption.html",
        "finished_goods_receipt.html", "production_waste.html", "production_costing.html"
    ],
    "MODUL_7_MARKETING": [
        "campaign.html", "voucher_list.html", "voucher_form.html",
        "voucher_claim_log.html", "customer_segment_list.html",
        "customer_segment_form.html", "promotion_calendar.html"
    ],
    "MODUL_8_MASTER_DATA": [
        "categories_list.html", "category_form.html", "units_list.html",
        "unit_form.html", "vendors_list.html", "vendor_form.html",
        "customers.html", "customer_detail.html", "customer_form.html",
        "locations.html", "products.html", "product_details.html",
        "tax_list.html", "tax_form.html", "bank_accounts.html",
        "bank_account_form.html", "payment_terms_list.html", "tags_list.html",
        "reason_codes.html"
    ],
    "MODUL_9_ACCOUNTING": [
        "chart_of_accounts.html", "chart_of_accounts_form.html",
        "journal_entry_list.html", "journal_entry_form.html",
        "journal_entry_detail.html", "general_ledger.html", "trial_balance.html",
        "balance_sheet.html", "cash_flow.html", "accounts_payable.html",
        "accounts_receivable.html", "payment_voucher_form.html"
    ],
    "MODUL_10_PRINT": [
        "print_receipt.html", "print_invoice.html", "print_quotation.html",
        "print_sales_order.html", "print_purchase_order.html",
        "print_delivery_note.html", "print_stock_opname.html",
        "print_credit_note.html", "print_payment_receipt.html",
        "print_production_order.html", "print_base.html"
    ],
    "MODUL_11_MESSAGES": [
        "notifications.html", "compose.html", "message_detail.html",
        "broadcast.html", "message_templates.html"
    ],
    "MODUL_12_REPORTS": [
        "sales_dashboard.html", "sales_intelligence.html", "sales_performance.html",
        "market_insights.html", "trends_analysis.html", "sales_report.html",
        "inventory_report.html", "financial_reports.html", "operational_report.html",
        "report_production.html", "report_expiry.html", "report_customer_lifetime.html",
        "report_staff_performance.html", "report_inventory_age.html"
    ],
    "MODUL_13_SETTINGS": [
        "roles.html", "role_form.html", "permission_matrix.html",
        "numbering_settings.html", "email_settings.html",
        "notification_settings.html", "backup_restore.html", "api_keys.html"
    ]
}

REQUIRED_MODELS = {
    "CRITICAL_NEW": [
        "stockmovement", "returns", "returitems", "payments", "productbatches"
    ],
    "HIGHLY_RECOMMENDED": [
        "unitconversions", "cashiershifts", "adjustmentreasons"
    ],
    "FIELD_ADDITIONS": {
        "products": ["sell_price", "barcode", "min_stock", "max_stock", "is_active", "track_batch", "has_expiry"],
        "orders": ["order_type", "payment_status", "payment_method", "paid_amount", "change_amount", "cashier_id", "shift_id", "table_number", "dining_option"],
        "orderitems": ["cost_price", "discount_amount", "discount_percent", "batch_id", "notes"],
        "customers": ["customer_type", "points_balance", "total_purchases", "visit_count", "last_purchase_at", "is_active"],
        "userprofile": ["role", "default_location_id", "is_active"],
        "stock": ["reserved_quantity", "available_quantity", "currency"]
    }
}

# ==================== SCAN WORKSPACE ====================

def get_all_templates():
    """Ambil semua file .html dari lumra_pages"""
    templates_dir = Path("lumra_config/templates/lumra_pages")
    templates = {}
    
    if not templates_dir.exists():
        print(f"⚠️ Directory tidak ditemukan: {templates_dir}")
        return templates
    
    for html_file in templates_dir.rglob("*.html"):
        rel_path = str(html_file.relative_to(templates_dir))
        filename = html_file.name
        templates[filename] = rel_path
    
    return templates

def get_all_models():
    """Extract semua model class dari models.py"""
    models_file = Path("lumra_config/models.py")
    models = []
    
    if not models_file.exists():
        return models
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find all class definitions that inherit from models.Model
        pattern = r'class\s+(\w+)\(.*models\.Model.*\):'
        matches = re.findall(pattern, content)
        models = matches
    
    return models

def get_all_views():
    """Scan semua views files"""
    views_dir = Path("lumra_config/views")
    views = {}
    
    if not views_dir.exists():
        return views
    
    for py_file in views_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find class-based views
                pattern = r'class\s+(\w+View)\('
                matches = re.findall(pattern, content)
                views[py_file.name] = matches
    
    return views

def get_orphaned_scripts():
    """Cari script Python yang tidak terpakai di root dan tools/"""
    orphaned = []
    root = Path(".")
    
    # Root level Python files
    for py_file in root.glob("*.py"):
        if py_file.name not in ["manage.py"]:
            orphaned.append(str(py_file))
    
    # Check if tools exist
    tools_dir = Path("tools")
    if tools_dir.exists():
        for py_file in tools_dir.glob("*.py"):
            orphaned.append(str(py_file))
    
    return orphaned

# ==================== ANALISIS ====================

def analyze_coverage():
    """Analisis coverage templates vs requirements"""
    templates = get_all_templates()
    current_filenames = set(templates.keys())
    
    print("=" * 80)
    print("ANALISIS PETUNJUK_MODUL.MD")
    print("=" * 80)
    print()
    
    missing_templates = defaultdict(list)
    found_templates = defaultdict(list)
    
    for modul, required in REQUIRED_TEMPLATES.items():
        for template_name in required:
            if template_name in current_filenames:
                found_templates[modul].append(template_name)
            else:
                missing_templates[modul].append(template_name)
    
    # Print summary
    total_required = sum(len(v) for v in REQUIRED_TEMPLATES.values())
    total_found = sum(len(v) for v in found_templates.values())
    
    print(f"📊 TEMPLATE COVERAGE: {total_found}/{total_required} ({100*total_found//total_required}%)")
    print()
    
    # Print missing per modul
    print("🔴 MISSING TEMPLATES PER MODUL:")
    print()
    for modul in sorted(REQUIRED_TEMPLATES.keys()):
        missing = missing_templates.get(modul, [])
        found = len(found_templates.get(modul, []))
        required = len(REQUIRED_TEMPLATES[modul])
        
        if missing:
            status = "❌ INCOMPLETE" if missing else "✅ COMPLETE"
            print(f"  {modul}: {found}/{required} ✓")
            for t in missing:
                print(f"    - ❌ {t}")
        else:
            print(f"  {modul}: {found}/{required} ✅ COMPLETE")
    
    print()
    print()
    
    # Models analysis
    print("=" * 80)
    print("MODEL ANALYSIS")
    print("=" * 80)
    print()
    
    models = get_all_models()
    models_lower = [m.lower() for m in models]
    
    print("🔴 CRITICAL NEW MODELS (WAJIB):")
    for model_name in REQUIRED_MODELS["CRITICAL_NEW"]:
        if model_name.lower() in models_lower:
            print(f"  ✅ {model_name}")
        else:
            print(f"  ❌ {model_name} - HARUS DIBUAT")
    
    print()
    print("🟡 HIGHLY RECOMMENDED MODELS:")
    for model_name in REQUIRED_MODELS["HIGHLY_RECOMMENDED"]:
        if model_name.lower() in models_lower:
            print(f"  ✅ {model_name}")
        else:
            print(f"  ⚠️ {model_name} - Disarankan")
    
    print()
    print()
    
    # Views analysis
    print("=" * 80)
    print("VIEWS ANALYSIS")
    print("=" * 80)
    print()
    
    views = get_all_views()
    all_views = []
    for file_views in views.values():
        all_views.extend(file_views)
    
    print(f"Total Views ditemukan: {len(all_views)}")
    print(f"Views files: {', '.join(views.keys())}")
    
    print()
    print()
    
    # Orphaned files
    print("=" * 80)
    print("ORPHANED/UTILITY FILES")
    print("=" * 80)
    print()
    
    orphaned = get_orphaned_scripts()
    print(f"⚠️ Potential files untuk di-archive: {len(orphaned)} files")
    for file in orphaned:
        print(f"  • {file}")
    
    print()
    print()
    
    # Extra templates
    print("=" * 80)
    print("EXTRA TEMPLATES (Tidak di petunjuk_modul)")
    print("=" * 80)
    print()
    
    required_filenames = set()
    for templates_list in REQUIRED_TEMPLATES.values():
        required_filenames.update(templates_list)
    
    extra = current_filenames - required_filenames
    print(f"Extra templates: {len(extra)}")
    for ext in sorted(extra):
        print(f"  • {ext} → {templates[ext]}")

if __name__ == "__main__":
    os.chdir("d:\\APPS\\Project\\lumra")
    analyze_coverage()
