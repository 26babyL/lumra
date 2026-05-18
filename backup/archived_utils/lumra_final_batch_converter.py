#!/usr/bin/env python3
"""
LUMRA Final Batch Converter - Process remaining 60 template files
Handles: master_data, messages, production, reports, sales_insight additions, settings
"""

import re
from pathlib import Path
import sys

# Comprehensive conversion patterns
PATTERNS = [
    # ===== TEXT COLORS =====
    (r"\btext-emerald-300\b", 'style="color: var(--em-12);"', "text emerald-300"),
    (r"\btext-emerald-(?:600|700)\b", 'style="color: var(--em);"', "text emerald primary"),
    (r"\btext-emerald-(?:400|500)\b", 'style="color: var(--jade);"', "text emerald secondary"),
    (r"\btext-emerald-800\b", 'style="color: var(--navy);"', "text emerald-800"),
    (r"\btext-emerald-900\b", 'style="color: var(--navy);"', "text emerald-900"),
    (r"\btext-green-(?:600|700)\b", 'style="color: var(--jade);"', "text green primary"),
    (r"\btext-green-(?:400|500)\b", 'style="color: var(--jade);"', "text green secondary"),
    
    # ===== BACKGROUND COLORS =====
    (r"\bbg-emerald-(?:50|100)\b", 'style="background-color: var(--em-08);"', "bg emerald light"),
    (r"\bbg-emerald-(?:600|700)\b", 'style="background-color: var(--em);"', "bg emerald primary"),
    (r"\bbg-emerald-(?:400|500)\b", 'style="background-color: var(--jade);"', "bg emerald secondary"),
    (r"\bbg-green-50\b", 'style="background-color: var(--jade-08);"', "bg green-50"),
    (r"\bbg-green-100\b", 'style="background-color: var(--jade-08);"', "bg green-100"),
    (r"\bbg-green-(?:600|700)\b", 'style="background-color: var(--jade);"', "bg green primary"),
    (r"\bbg-teal-50\b", 'style="background-color: var(--em-08);"', "bg teal-50"),
    (r"\bbg-teal-100\b", 'style="background-color: var(--em-12);"', "bg teal-100"),
    (r"\bbg-emerald-900\b", 'style="background-color: var(--navy);"', "bg emerald-900"),
    (r"\bbg-red-(?:50|100|200)\b", 'style="background-color: var(--em-08);"', "bg red light"),
    (r"\bbg-purple-(?:100|200)\b", 'style="background-color: var(--em-08);"', "bg purple light"),
    (r"\bbg-blue-(?:100|200)\b", 'style="background-color: var(--em-08);"', "bg blue light"),
    
    # ===== BORDER COLORS =====
    (r"\bborder-emerald-200\b", 'style="border-color: var(--em-15);"', "border emerald-200"),
    (r"\bborder-emerald-300\b", 'style="border-color: var(--em-12);"', "border emerald-300"),
    (r"\bborder-emerald-400\b", 'style="border-color: var(--jade);"', "border emerald-400"),
    
    # ===== GRADIENT PATTERNS =====
    (r"from-emerald-600\s+to-emerald-700", 'style="background: linear-gradient(135deg, var(--em) 0%, var(--em) 100%);"', "gradient em-em"),
    (r"from-emerald-(?:600|700)\s+to-jade-(?:500|600)", 'style="background: linear-gradient(135deg, var(--em) 0%, var(--jade) 100%);"', "gradient em-jade"),
    (r"from-green-100\s+to-green-200", 'style="background: linear-gradient(135deg, var(--jade-08) 0%, var(--jade-08) 100%);"', "gradient green light"),
    (r"bg-gradient-to-br\s+from-green-100\s+to-green-200", 'style="background: linear-gradient(135deg, var(--jade-08) 0%, var(--jade-08) 100%);"', "gradient br green"),
]

# Target files by category
FILES_TO_CONVERT = {
    "master_data": [
        "categories_list.html", "category_form.html", "customer_detail.html",
        "customer_form.html", "customer.html", "customers_list.html",
        "customers.html", "location_list.html", "locations.html",
        "stock_opname_session_detail.html", "stock_opname.html", "unit_form.html",
        "units_list.html", "vendor_form.html", "vendor_list.html", "vendors_list.html"
    ],
    "messages": ["inbox.html", "notification.html"],
    "production": ["recipe_detail.html", "recipe_form.html", "recipe_list.html"],
    "reports": [
        "activity_log.html", "base_report.html", "purchasing_report.html",
        "report_activity_log.html", "report_inventory_log.html", "report_inventory_low.html",
        "report_inventory_stock.html", "report_profit_loss_detail.html",
        "report_sales_by_outlet.html", "report_sales_by_payment.html",
        "report_sales_by_product.html", "report_sales_summary.html", "reporting.html",
        "requisition_report.html", "sales_history_product.html", "sales_history.html",
        "sales_report_after.html", "sales_report.html", "transaction_summary.html",
        "transfer_report.html"
    ],
    "sales_insight": [
        "financial_reports.html", "market_insights.html", "pos.html",
        "sales_intelligence.html", "sales_performance.html", "trends_analysis.html"
    ],
    "settings": [
        "about.html", "business_feature_matrix.html", "business_form_general.html",
        "business_profile.html", "business_settings.html", "contact.html", "profile.html",
        "search.html", "settings.html", "system_status.html", "user_list.html",
        "user_roles_permissions.html", "users.html"
    ]
}

def convert_file(filepath: Path, dry_run: bool = True) -> tuple[int, list]:
    """Convert Tailwind colors in a file."""
    
    if not filepath.exists():
        return 0, [f"NOT FOUND: {filepath.name}"]
    
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        replacements_made = 0
        changes = []
        
        for pattern, replacement, description in PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                old_content = content
                content = re.sub(pattern, replacement, content)
                if content != old_content:
                    count = len(re.findall(pattern, old_content))
                    replacements_made += count
                    changes.append(f"{count}x {description}")
        
        if replacements_made > 0 and not dry_run:
            filepath.write_text(content, encoding='utf-8')
        
        return replacements_made, changes
    
    except Exception as e:
        return 0, [f"ERROR: {str(e)}"]

def main():
    base_dir = Path("lumra_config/templates/lumra_pages")
    dry_run = "--apply" not in sys.argv
    verbose = "--verbose" in sys.argv
    
    print("=" * 70)
    print("LUMRA FINAL BATCH CONVERTER - 60 FILES")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print()
    
    total_replacements = 0
    files_modified = 0
    
    for category, files in FILES_TO_CONVERT.items():
        category_total = 0
        category_files = 0
        
        print(f"\n[{category.upper()}]")
        print("-" * 70)
        
        for filename in files:
            filepath = base_dir / category / filename
            replacements, changes = convert_file(filepath, dry_run)
            
            if replacements > 0:
                files_modified += 1
                category_files += 1
                category_total += replacements
                total_replacements += replacements
                
                status = "[DRY]" if dry_run else "[OK]"
                print(f"{status} {filename}: {replacements} items")
                
                if verbose and changes:
                    for change in changes[:3]:  # Show first 3 changes
                        print(f"      {change}")
            else:
                status = "[SKIP]" if dry_run else "[OK-0]"
                print(f"{status} {filename}: 0 items")
        
        if category_total > 0:
            print(f"  Category total: {category_total} items in {category_files} files")
    
    print()
    print("=" * 70)
    if dry_run:
        print(f"[DRY RUN] Would convert {total_replacements} items in {files_modified} files")
        print("\nTo apply: python lumra_final_batch_converter.py --apply")
    else:
        print(f"[OK] Converted {total_replacements} items in {files_modified} files")
        print("\nNext: python backup/lumra_deployment_validator.py --generate-report")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()
