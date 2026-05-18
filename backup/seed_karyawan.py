import os
import django
import unicodedata
import random
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')
django.setup()

import openpyxl
from django.contrib.auth.models import User
from django.db import connection, transaction

EXCEL_FILE = "data_orang.xlsx"
DEFAULT_PASSWORD = "LumraChangeMe123!"

# ============================================================
# HELPER
# ============================================================
def make_username(name):
    normalized = unicodedata.normalize('NFKD', name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9_]', '', ascii_name.lower().replace(" ", "_"))

def get_all_store_ids():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM lumra_config_stores WHERE is_active = TRUE")
        rows = cursor.fetchall()
    return [row[0] for row in rows]

# ============================================================
# SEED CUSTOMERS → lumra_config_customers
# ============================================================
def seed_customers(names):
    print(f"\n👥 Seeding {len(names)} Customers...")
    created = skipped = 0

    with connection.cursor() as cursor:
        for name in names:
            cursor.execute(
                "SELECT id FROM lumra_config_customers WHERE name = %s", [name]
            )
            if cursor.fetchone():
                print(f"  🟡 Skipped : {name}")
                skipped += 1
                continue

            # Handle email collision
            base_email = f"{make_username(name)}@placeholder.lumra.id"
            email = base_email
            counter = 1
            while True:
                cursor.execute(
                    "SELECT id FROM lumra_config_customers WHERE email = %s", [email]
                )
                if not cursor.fetchone():
                    break
                email = f"{make_username(name)}_{counter}@placeholder.lumra.id"
                counter += 1

            cursor.execute("""
                INSERT INTO lumra_config_customers (
                    name, email, phone, address, city,
                    tier, loyalty_points, total_spent,
                    total_orders, is_active, created_at, updated_at
                ) VALUES (
                    %s, %s, '', '', '',
                    'bronze', 0, 0.00,
                    0, TRUE, NOW(), NOW()
                )
            """, [name, email])
            print(f"  ✅ Customer: {name}")
            created += 1

    print(f"  → {created} dibuat, {skipped} dilewati.")

# ============================================================
# SEED STAFF → auth_user + lumra_config_userprofile
# ============================================================
def seed_staff(names, store_ids):
    print(f"\n👔 Seeding {len(names)} Staff...")
    if not store_ids:
        print("  ❌ Tidak ada store aktif di database! Jalankan seed_stores dulu.")
        return

    created = skipped = 0

    for name in names:
        username = make_username(name)

        # Handle username collision
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        if User.objects.filter(first_name=name).exists():
            print(f"  🟡 Skipped : {name}")
            skipped += 1
            continue

        with transaction.atomic():
            # Buat user Django
            user = User.objects.create_user(
                username=username,
                password=DEFAULT_PASSWORD,
                first_name=name,
                is_active=False,  # Staff aktif setelah set password sendiri
            )

            # Assign ke store secara random
            assigned_store_id = random.choice(store_ids)

            with connection.cursor() as cursor:
                # Cek apakah lumra_config_userprofile punya kolom store_id
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'lumra_config_userprofile'
                    AND column_name = 'store_id'
                """)
                has_store_col = cursor.fetchone()

                if has_store_col:
                    cursor.execute("""
                        INSERT INTO lumra_config_userprofile (user_id, store_id, location_id)
                        VALUES (%s, %s, NULL)
                    """, [user.id, assigned_store_id])
                else:
                    # Pakai location_id sebagai fallback
                    cursor.execute("""
                        INSERT INTO lumra_config_userprofile (user_id, location_id)
                        VALUES (%s, NULL)
                    """, [user.id])

            print(f"  ✅ Staff : {name:<30} @{username} → store_id={assigned_store_id}")
            created += 1

    print(f"  → {created} dibuat, {skipped} dilewati.")

# ============================================================
# MAIN
# ============================================================
def main():
    print("📂 Membaca file Excel...")
    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb.active

    customers = []
    staff = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        name, role = row[0], row[1]
        if not name or not role:
            continue
        name = str(name).strip()
        role = str(role).strip().lower()

        if role == "customer":
            customers.append(name)
        elif role == "staff":
            staff.append(name)
        else:
            print(f"  ⚠️  Role tidak dikenal: '{role}' untuk '{name}' — dilewati")

    print(f"  → Ditemukan: {len(customers)} customers, {len(staff)} staff")

    store_ids = get_all_store_ids()
    print(f"  → Store aktif tersedia: {len(store_ids)} stores")

    seed_customers(customers)
    seed_staff(staff, store_ids)

    print(f"\n{'='*55}")
    print(f"  🚀 Lumra Seeding Selesai!")
    print(f"  💡 Staff login pertama pakai password: {DEFAULT_PASSWORD}")
    print(f"  💡 is_active=False → aktif setelah staff set password sendiri")
    print(f"{'='*55}")

if __name__ == "__main__":
    main()