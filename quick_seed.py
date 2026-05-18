#!/usr/bin/env python
"""
Quick seed script untuk insert data minimal ke database
Cukup kategori, unit, tax, location, vendor untuk bisa test sidebar menu
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_system.settings")
django.setup()

from django.contrib.auth import get_user_model
from lumra_config.models import (
    Category, Unit, Tax, Vendor, Location, UserProfile
)
from decimal import Decimal

User = get_user_model()

print("Seeding database dengan data minimal...")

# 1. Create admin user
user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@lumra.test',
        'first_name': 'Admin',
        'last_name': 'Lumra',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    user.set_password('admin@123')
    user.save()
    print("[+] User created: admin")
else:
    print("[*] User already exists: admin")

# 2. Create categories
categories_data = [
    ("Kopi Biji", "Biji kopi sangrai", "kopi-biji", "KB"),
    ("Minuman Kopi", "Menu minuman kopi", "minuman-kopi", "MK"),
    ("Non-Kopi", "Minuman non-kopi", "non-kopi", "NK"),
]

for name, desc, slug, code in categories_data:
    cat, created = Category.objects.get_or_create(
        name=name,
        defaults={"description": desc, "slug": slug, "code": code, "is_active": True}
    )
    if created:
        print(f"[+] Category created: {name}")
    else:
        print(f"[*] Category exists: {name}")

# 3. Create units
units_data = [
    ("Gram", "g", "Satuan berat gram"),
    ("Kilogram", "kg", "Satuan berat kilogram"),
    ("Mililiter", "ml", "Satuan volume mililiter"),
    ("Liter", "L", "Satuan volume liter"),
    ("Pcs", "pcs", "Satuan buah/pieces"),
]

for name, symbol, desc in units_data:
    unit, created = Unit.objects.get_or_create(
        name=name,
        defaults={"symbol": symbol, "description": desc, "is_active": True}
    )
    if created:
        print(f"[+] Unit created: {name}")
    else:
        print(f"[*] Unit exists: {name}")

# 4. Create taxes
taxes_data = [
    ("PPN 11%", Decimal("11.00"), "Pajak Pertambahan Nilai"),
    ("PPN 0%", Decimal("0.00"), "Non-PPN"),
]

for name, rate, desc in taxes_data:
    tax, created = Tax.objects.get_or_create(
        name=name,
        defaults={"rate": rate, "description": desc, "is_active": True}
    )
    if created:
        print(f"[+] Tax created: {name}")
    else:
        print(f"[*] Tax exists: {name}")

# 5. Create vendors
vendors_data = [
    ("PT Toraja Coffee", "Pak Budi", "081234567001", "TOR"),
    ("CV Gayo Highland", "Ibu Ratna", "081234567002", "GAY"),
]

for name, cp, phone, code in vendors_data:
    vendor, created = Vendor.objects.get_or_create(
        name=name,
        defaults={"contact_person": cp, "phone": phone, "code": code, "is_active": True}
    )
    if created:
        print(f"[+] Vendor created: {name}")
    else:
        print(f"[*] Vendor exists: {name}")

# 6. Create locations
locations_data = [
    ("Toko Utama", "Jl. Sudirman No.123", "store"),
    ("Gudang Jakarta", "Jl. Raya Bogor Km.32", "warehouse"),
]

for name, addr, loc_type in locations_data:
    location, created = Location.objects.get_or_create(
        name=name,
        defaults={"address": addr, "location_type": loc_type}
    )
    if created:
        print(f"[+] Location created: {name}")
    else:
        print(f"[*] Location exists: {name}")

# 7. Create user profile
location = Location.objects.first()  # Get first location
try:
    profile = UserProfile.objects.get(user=user)
    print("[*] UserProfile exists")
except UserProfile.DoesNotExist:
    profile = UserProfile.objects.create(
        user=user,
        location=location,
        role="admin",
        is_active=True
    )
    print("[+] UserProfile created")

print("\n✓ Seeding selesai!")
print(f"  - Admin user: admin / admin@123")
print(f"  - Categories: {Category.objects.count()}")
print(f"  - Units: {Unit.objects.count()}")
print(f"  - Taxes: {Tax.objects.count()}")
print(f"  - Vendors: {Vendor.objects.count()}")
print(f"  - Locations: {Location.objects.count()}")
