#!/usr/bin/env python3
"""
Analisis migration_log.json dan buat fix script untuk yang belum sempurna
Usage: python analyze_migration_and_fix.py
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Load migration log
log_file = Path("migration_log.json")
with open(log_file) as f:
    logs = json.load(f)

print("=" * 80)
print("📊 MIGRATION ANALYSIS REPORT")
print("=" * 80)

# Status summary
ok_count = len([l for l in logs if l['status'] == 'ok'])
warn_count = len([l for l in logs if l['status'] == 'warn'])
error_count = len([l for l in logs if l['status'] == 'error'])

print(f"\n✓ OK:    {ok_count} templates")
print(f"⚠ WARN:  {warn_count} templates")
print(f"✗ ERROR: {error_count} templates")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"TOTAL:   {len(logs)} templates")

# Analyze WARN templates
if warn_count > 0:
    print(f"\n\n{'='*80}")
    print("⚠️  TEMPLATES WITH WARNINGS (Need Review)")
    print("=" * 80)
    warn_files = [l for l in logs if l['status'] == 'warn']
    for log in warn_files:
        print(f"\n📄 {log['file']}")
        for change in log['changes']:
            print(f"   • {change}")

# Analyze ERROR templates
if error_count > 0:
    print(f"\n\n{'='*80}")
    print("❌ TEMPLATES WITH ERRORS (Need Fixing)")
    print("=" * 80)
    error_files = [l for l in logs if l['status'] == 'error']
    for log in error_files:
        print(f"\n📄 {log['file']}")
        for change in log['changes']:
            print(f"   • {change}")

# Analyze changes by type
print(f"\n\n{'='*80}")
print("📈 CHANGES BY TYPE")
print("=" * 80)

change_types = defaultdict(int)
for log in logs:
    for change in log['changes']:
        # Extract change type
        if "Block" in change:
            change_types["Block rename"] += 1
        elif "Inject" in change:
            change_types["JSON injection"] += 1
        elif "Update init" in change:
            change_types["Init update"] += 1
        elif "Tambah fungsi init" in change:
            change_types["Add init function"] += 1
        elif "Tambah x-init" in change:
            change_types["Add x-init"] += 1
        elif "skip" in change:
            change_types["Skipped (no JSON)"] += 1
        else:
            change_types["Other"] += 1

for change_type, count in sorted(change_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  • {change_type}: {count}")

# Summary by module
print(f"\n\n{'='*80}")
print("📁 MIGRATION BY MODULE")
print("=" * 80)

modules = defaultdict(lambda: {"ok": 0, "warn": 0, "error": 0, "total": 0})
for log in logs:
    # Extract module from filename path if available (usually just filename though)
    # For now, we can categorize by common patterns
    filename = log['file']
    
    if 'accounting' in filename or any(x in filename for x in ['balance', 'cash', 'profit', 'journal', 'voucher', 'ledger', 'trial', 'accounts']):
        module = 'Accounting'
    elif 'inventory' in filename or 'stock' in filename:
        module = 'Inventory'
    elif 'report' in filename:
        module = 'Reports'
    elif 'sale' in filename or 'invoice' in filename or 'order' in filename:
        module = 'Sales'
    elif 'purchase' in filename or 'po' in filename or 'quotation' in filename:
        module = 'Purchasing'
    elif 'hrm' in filename or 'employee' in filename or 'payroll' in filename:
        module = 'HRM'
    elif 'crm' in filename or 'customer' in filename or 'contact' in filename:
        module = 'CRM'
    elif 'asset' in filename or 'depreciation' in filename:
        module = 'Asset Management'
    else:
        module = 'Other'
    
    modules[module][log['status']] += 1
    modules[module]['total'] += 1

# Print module summary
for module in sorted(modules.keys()):
    stats = modules[module]
    status_str = f"✓{stats['ok']} ⚠{stats['warn']} ✗{stats['error']}"
    print(f"  {module:20} {status_str:20} ({stats['total']} total)")

# Overall stats
print(f"\n\n{'='*80}")
print("🎯 OVERALL ASSESSMENT")
print("=" * 80)

success_rate = (ok_count / len(logs)) * 100
print(f"Success Rate: {success_rate:.1f}% ({ok_count}/{len(logs)})")

if error_count == 0 and warn_count <= 5:
    print("\n✅ MIGRATION STATUS: EXCELLENT")
    print("   Most templates migrated successfully!")
    if warn_count > 0:
        print(f"   {warn_count} templates have minor issues (review recommended)")
elif error_count == 0:
    print("\n⚠️  MIGRATION STATUS: GOOD")
    print("   All templates processed, but some have warnings")
else:
    print("\n❌ MIGRATION STATUS: NEEDS ATTENTION")
    print(f"   {error_count} templates have errors")

# Recommendations
print(f"\n\n{'='*80}")
print("💡 NEXT STEPS")
print("=" * 80)

if error_count > 0:
    print(f"\n1. Fix {error_count} ERROR templates:")
    print("   → Run: python fix_migration_errors.py")
    
if warn_count > 0:
    print(f"\n2. Review {warn_count} WARN templates:")
    print("   → May need manual adjustments")
    print("   → See section above for details")

print("\n3. Validation:")
print("   → python manage.py runserver")
print("   → Visit each endpoint to verify rendering")

print("\n4. Performance test:")
print("   → Check browser console for JS errors")
print("   → Test filtering/sorting if applicable")

print("\n" + "=" * 80)
