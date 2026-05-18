#!/usr/bin/env python
"""Audit all HTML templates for database field references."""
import os
import re
from pathlib import Path

# Known model fields by app/model
MODELS_FIELDS = {
    'Product': ['name', 'description', 'category', 'vendor', 'tax', 'unit', 'sell_price', 'barcode', 'min_stock', 'max_stock', 'is_active', 'track_batch', 'has_expiry', 'created_at', 'updated_at'],
    'ProductVariant': ['product', 'sku', 'size_weight', 'price_buy', 'price_sell', 'updated_at', 'total_stock', '_cached_total_stock'],
    'Category': ['name', 'description', 'parent', 'slug', 'code', 'icon_url', 'is_active', 'created_at', 'updated_at'],
    'Vendor': ['name', 'contact_person', 'phone', 'code', 'email', 'address', 'website', 'tax_number', 'is_active', 'created_at', 'updated_at'],
    'Location': ['name', 'address', 'location_type', 'created_at'],
    'Stock': ['variant', 'location', 'quantity', 'transaction_type', 'notes', 'reserved_quantity', 'last_updated', 'created_at'],
    'Customer': ['name', 'email', 'phone', 'address', 'city', 'tier', 'is_active', 'created_at', 'updated_at'],
    'Unit': ['name', 'symbol', 'description', 'is_active', 'created_at'],
    'Tax': ['name', 'rate', 'description', 'is_active', 'created_at'],
}

# Known problematic patterns
SUSPICIOUS_FIELDS = re.compile(r'\b(base_price|unit_price|qty|total_qty)\b', re.IGNORECASE)

# Template directory
template_dir = Path('lumra_config/templates')

print("=" * 80)
print("  LUMRA TEMPLATE AUDIT - DATABASE FIELD REFERENCE CHECK")
print("=" * 80)

html_files = sorted(template_dir.rglob('*.html'))
suspicious_files = []
field_issues = {}

print(f"\nScanning {len(html_files)} HTML templates...\n")

for html_file in html_files:
    content = html_file.read_text(errors='ignore')
    
    # Check for suspicious field names
    matches = SUSPICIOUS_FIELDS.findall(content)
    if matches:
        suspicious_files.append(html_file)
        field_issues[str(html_file.relative_to('.'))] = matches

# Print results
if suspicious_files:
    print("⚠️  SUSPICIOUS FIELD REFERENCES FOUND:\n")
    for file, fields in field_issues.items():
        print(f"  📄 {file}")
        for field in set(fields):
            print(f"     - {field}")
    print()
else:
    print("✅ No obvious field reference issues found.\n")

# Check for database-related patterns
print("CHECKING DATABASE-RELATED PATTERNS:\n")

patterns = {
    'model field access': r'\{\{[^}]*\.[a-z_]+[^}]*\}\}',
    'for loops': r'\{%\s*for\s+\w+\s+in',
    'if conditions': r'\{%\s*if\s+[^%]+%\}',
}

file_count = 0
for html_file in html_files[:10]:  # Sample first 10
    content = html_file.read_text(errors='ignore')
    has_patterns = False
    
    for pattern_name, regex in patterns.items():
        if re.search(regex, content):
            if not has_patterns:
                print(f"  📄 {html_file.name}")
                has_patterns = True
            # Count matches
            matches = len(re.findall(regex, content))
            print(f"     - {pattern_name}: {matches} occurrences")
    
    if has_patterns:
        file_count += 1

print(f"\n✓ Sampled {min(10, len(html_files))} template files")

print("\n" + "=" * 80)
print("  AUDIT SUMMARY - ALL TEMPLATES SHOULD USE REAL DATABASE FIELDS ONLY")
print("=" * 80)
print(f"Total templates scanned: {len(html_files)}")
print(f"Suspicious field references: {len(suspicious_files)}")
print("\n[ACTION] Review the suspicious files listed above and replace with correct field names")
print("=" * 80)
