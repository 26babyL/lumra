#!/usr/bin/env python
"""
Simple LUMRA ERP Test - Minimal working version
Tests core ERP functionality without Gemini complexity
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_config.settings')
django.setup()

from decimal import Decimal
from datetime import datetime
from lumra_config.models import (
    Location, Category, Unit, Vendor, Product, Customer, 
    Stock, Order, OrderItem, Requisition, Transfer, Location
)

print("\n" + "="*70)
print(" LUMRA ERP — SIMPLE FUNCTIONALITY TEST")
print("="*70 + "\n")

try:
    # Test 1: Create Categories
    print("[1] Creating Categories...")
    cat_minuman, _ = Category.objects.get_or_create(
        name="Minuman",
        defaults={"description": "Beverage Products"}
    )
    print(f"    OK - Category: {cat_minuman.name}")
    
    # Test 2: Create Unit
    print("[2] Creating Units...")
    unit_cup, _ = Unit.objects.get_or_create(
        name="Cup",
        defaults={"abbreviation": "cup"}
    )
    print(f"    OK - Unit: {unit_cup.name}")
    
    # Test 3: Create Vendor
    print("[3] Creating Vendors...")
    vendor, _ = Vendor.objects.get_or_create(
        name="PT Kopi Nusantara",
        defaults={
            "phone": "021-5555-1234",
            "email": "vendor@kopiindo.com",
            "address": "Jl. Gatot Subroto, Jakarta"
        }
    )
    print(f"    OK - Vendor: {vendor.name}")
    
    # Test 4: Create Location
    print("[4] Creating Locations...")
    loc_store, _ = Location.objects.get_or_create(
        code="LOC-001",
        defaults={
            "name": "Main Store",
            "location_type": "store"
        }
    )
    print(f"    OK - Location: {loc_store.code} ({loc_store.name})")
    
    # Test 5: Create Product
    print("[5] Creating Products...")
    product, _ = Product.objects.get_or_create(
        sku="PROD-001",
        defaults={
            "name": "Espresso",
            "category": cat_minuman,
            "unit": unit_cup,
            "price_buy": Decimal("5000"),
            "price_sell": Decimal("25000")
        }
    )
    print(f"    OK - Product: {product.sku} ({product.name})")
    
    # Test 6: Create Stock
    print("[6] Creating Stock...")
    stock, _ = Stock.objects.get_or_create(
        product=product,
        location=loc_store,
        defaults={
            "quantity": Decimal("100"),
            "reserved_quantity": Decimal("0")
        }
    )
    print(f"    OK - Stock: {stock.quantity} x {stock.product.name}")
    
    # Test 7: Create Customer
    print("[7] Creating Customers...")
    customer, _ = Customer.objects.get_or_create(
        phone="081234567890",
        defaults={
            "name": "John Doe",
            "email": "john@example.com",
            "address": "Jl. Customer, Jakarta"
        }
    )
    print(f"    OK - Customer: {customer.name}")
    
    print("\n" + "="*70)
    print(" ALL TESTS PASSED")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
