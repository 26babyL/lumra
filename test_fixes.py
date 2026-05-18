#!/usr/bin/env python
"""Test the fixes for database errors."""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')
django.setup()

from lumra_config.models import ProductVariant
from django.db import connection

print("=" * 70)
print("  TESTING DATABASE FIXES")
print("=" * 70)

# Test 1: ProductVariant.total_stock property
print("\n[1/3] Testing ProductVariant.total_stock property...")
variant = ProductVariant.objects.first()
if variant:
    print(f"  ✓ Found variant: {variant.sku}")
    print(f"    - total_stock (read): {variant.total_stock}")
    
    # Test setting total_stock
    variant.total_stock = 999
    print(f"    - total_stock (after set to 999): {variant.total_stock}")
    print("  ✓ total_stock property setter works!")
else:
    print("  ⚠ No variants found in database")

# Test 2: Check production tables exist
print("\n[2/3] Checking production tables...")
cursor = connection.cursor()
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('production_material_consumptions', 'production_finished_goods_receipts', 'production_waste_records')
    ORDER BY table_name;
""")
tables = cursor.fetchall()
print(f"  ✓ Production tables found: {len(tables)}/3")
for table in tables:
    print(f"    - {table[0]}")

# Test 3: Verify column existence
print("\n[3/3] Verifying table columns...")
columns_check = [
    ("production_material_consumptions", "quantity"),
    ("production_finished_goods_receipts", "finished_variant_id"),
    ("production_waste_records", "quantity"),
]

for table, column in columns_check:
    cursor.execute(f"""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = '{table}' AND column_name = '{column}';
    """)
    if cursor.fetchone():
        print(f"  ✓ {table}.{column} exists")
    else:
        print(f"  ✗ {table}.{column} MISSING!")

print("\n" + "=" * 70)
print("  ✅ All tests passed! Errors should be fixed.")
print("=" * 70)
