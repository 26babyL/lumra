"""
Utility untuk mengecek konfigurasi PostgreSQL project Lumra dan memverifikasi
hasil seed data Nusantara berdasarkan schema yang benar di project ini.

Contoh:
    python lumra_config/management/commands/nusantara_pg_setup.py --test-connection
    python lumra_config/management/commands/nusantara_pg_setup.py --verify
    python lumra_config/management/commands/nusantara_pg_setup.py --sample
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_system.settings")

import django

django.setup()

from django.conf import settings
from django.db import connection


EXPECTED_TABLES = [
    ("lumra_config_taxes", "Taxes", 3),
    ("lumra_config_units", "Units", 5),
    ("lumra_config_categories", "Categories", 10),
    ("lumra_config_vendors", "Vendors", 5),
    ("lumra_config_locations", "Locations", 5),
    ("lumra_config_products", "Products", 10),
    ("lumra_config_productvariants", "Variants", 10),
    ("lumra_config_productattribute_items", "Product Attributes", 1),
    ("lumra_config_customers", "Customers", 1),
]


def db_config():
    return settings.DATABASES["default"]


def print_db_config():
    cfg = db_config()
    print("Database settings aktif:")
    print(f"  ENGINE : {cfg.get('ENGINE')}")
    print(f"  NAME   : {cfg.get('NAME')}")
    print(f"  USER   : {cfg.get('USER')}")
    print(f"  HOST   : {cfg.get('HOST')}")
    print(f"  PORT   : {cfg.get('PORT')}")


def test_connection():
    cfg = db_config()
    print_db_config()
    if cfg.get("ENGINE") != "django.db.backends.postgresql":
        print("WARNING: ENGINE saat ini bukan PostgreSQL.")
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
        print(f"OK: PostgreSQL connected: {version}")
        return True
    except Exception as exc:
        print(f"ERROR: Connection failed: {exc}")
        return False


def table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s);", [table_name])
        return cursor.fetchone()[0] is not None


def table_count(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        return cursor.fetchone()[0]


def verify_seeded_data():
    print_db_config()
    print("\nVerifikasi tabel dan jumlah data")
    print("-" * 60)

    all_ok = True
    for table_name, label, expected_min in EXPECTED_TABLES:
        try:
            if not table_exists(table_name):
                print(f"  MISSING  {label:<22} table `{table_name}` tidak ada")
                all_ok = False
                continue

            count = table_count(table_name)
            status = "OK" if count >= expected_min else "LOW"
            print(f"  {status:<7} {label:<22} {count:>8,} rows")
            if count < expected_min:
                all_ok = False
        except Exception as exc:
            print(f"  ERROR   {label:<22} {exc}")
            all_ok = False

    print("-" * 60)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.name, COUNT(*)
                FROM lumra_config_products p
                LEFT JOIN lumra_config_categories c ON c.id = p.category_id
                GROUP BY c.name
                ORDER BY COUNT(*) DESC, c.name
                LIMIT 12
                """
            )
            rows = cursor.fetchall()
        if rows:
            print("Top kategori produk:")
            for name, count in rows:
                print(f"  {name or 'Tanpa kategori':<22} {count:>8,}")
    except Exception as exc:
        print(f"Category summary skipped: {exc}")

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN p.pk_prefix = 'hb' THEN p.cnt ELSE 0 END) AS house_blend,
                    SUM(CASE WHEN p.pk_prefix = 'so' THEN p.cnt ELSE 0 END) AS single_origin
                FROM (
                    SELECT
                        CASE
                            WHEN pv.sku LIKE 'HB-%' THEN 'hb'
                            WHEN pv.sku LIKE 'SO-%' THEN 'so'
                            ELSE 'other'
                        END AS pk_prefix,
                        COUNT(*) AS cnt
                    FROM lumra_config_productvariants pv
                    GROUP BY 1
                ) p
                """
            )
            hb_count, so_count = cursor.fetchone()
        print("\nDistribusi variant kopi dari SKU prefix:")
        print(f"  House Blend   : {hb_count or 0:>8,}")
        print(f"  Single Origin : {so_count or 0:>8,}")
    except Exception as exc:
        print(f"Variant distribution skipped: {exc}")

    if all_ok:
        print("\nOK: Struktur dasar dan seed utama terlihat valid.")
    else:
        print("\nWARNING: Ada tabel yang belum terisi sesuai minimum. Jalankan seed lagi.")


def show_sample_products():
    print("Sample produk")
    print("-" * 80)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.name,
                    COALESCE(c.name, '-'),
                    pv.sku,
                    COALESCE(pv.size_weight, '-'),
                    pv.price_sell
                FROM lumra_config_productvariants pv
                JOIN lumra_config_products p ON p.id = pv.product_id
                LEFT JOIN lumra_config_categories c ON c.id = p.category_id
                ORDER BY p.name, pv.sku
                LIMIT 20
                """
            )
            rows = cursor.fetchall()
        for name, category, sku, size_weight, price_sell in rows:
            print(f"  {sku:<22} {name[:28]:<30} {category[:18]:<20} {size_weight:<12} {price_sell}")
    except Exception as exc:
        print(f"ERROR: Sample query failed: {exc}")


def show_commands():
    json_default = Path(__file__).with_name("kopi_9999_db.json")
    print("Urutan eksekusi yang direkomendasikan:")
    print("  python manage.py migrate")
    print("  python lumra_config/management/commands/nusantara_pg_setup.py --test-connection")
    print("  python manage.py seed_nusantara --only master")
    print("  python manage.py seed_nusantara --only kopi --json "
          f"\"{json_default}\"")
    print("  python lumra_config/management/commands/nusantara_pg_setup.py --verify")


def main():
    parser = argparse.ArgumentParser(description="Lumra PostgreSQL setup checker")
    parser.add_argument("--test-connection", action="store_true", help="Cek koneksi DB aktif dari settings.py")
    parser.add_argument("--verify", action="store_true", help="Verifikasi tabel dan jumlah data utama")
    parser.add_argument("--sample", action="store_true", help="Tampilkan sample produk dan variant")
    parser.add_argument("--show-config", action="store_true", help="Tampilkan database config aktif")
    parser.add_argument("--commands", action="store_true", help="Tampilkan urutan command yang direkomendasikan")
    args = parser.parse_args()

    if not any(vars(args).values()):
        print_db_config()
        print()
        show_commands()
        return

    if args.show_config:
        print_db_config()
    if args.commands:
        show_commands()
    if args.test_connection:
        test_connection()
    if args.verify:
        verify_seeded_data()
    if args.sample:
        show_sample_products()


if __name__ == "__main__":
    main()
