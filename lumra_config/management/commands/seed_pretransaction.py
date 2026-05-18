"""
seed_pretransaction.py
======================
Seed semua tabel yang WAJIB terisi sebelum transaksi apapun bisa berjalan.

Tabel yang diisi:
  1. system_numbering_sequences  — format nomor dokumen otomatis
  2. system_email_settings       — konfigurasi email sistem
  3. accounting_accounts         — Chart of Accounts (CoA) lengkap
  4. lumra_config_supplier_prices — harga beli per vendor per varian (sample)
  5. lumra_config_sales_targets  — target penjualan per bulan
  6. lumra_config_stock          — stok awal per varian per lokasi
  7. lumra_config_inventory_batches — batch inventory internal
  8. production_bill_of_materials — BOM untuk produksi
  9. lumra_config_stores         — audit & lengkapi data toko

Syarat sebelum run:
  - lumra_config_locations       sudah ada (56 rows) ✓
  - lumra_config_vendors         sudah ada (20 rows) ✓
  - lumra_config_productvariants sudah ada (~4M rows) ✓
  - auth_user                    sudah ada (1923 rows) ✓

Cara pakai:
  pip install psycopg2-binary
  python seed_pretransaction.py --dry-run   # preview
  python seed_pretransaction.py             # simpan ke DB
  python seed_pretransaction.py --section numbering   # jalankan section tertentu
  python seed_pretransaction.py --section coa
  python seed_pretransaction.py --section stock
  python seed_pretransaction.py --section all         # default semua
"""

import sys
import json
import random
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATABASE = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "lumra_set_allegra",
    "user":     "postgres",
    "password": "123456",
}
# ─────────────────────────────────────────────────────────────────────────────

DRY_RUN = "--dry-run" in sys.argv
NOW     = datetime.now(timezone.utc)
TODAY   = date.today()
random.seed(42)

# Section filter
SECTION = "all"
for i, arg in enumerate(sys.argv):
    if arg == "--section" and i+1 < len(sys.argv):
        SECTION = sys.argv[i+1]

SECTIONS = {"numbering", "email", "coa", "supplier_prices", "sales_targets",
            "stock", "inventory_batches", "bom", "stores", "all"}


def should_run(section_name):
    return SECTION == "all" or SECTION == section_name


def get_conn():
    import psycopg2
    return psycopg2.connect(**DATABASE)


def preview(table, rows, max_show=3):
    print(f"\n{'─'*70}")
    print(f"  TABLE: {table}  ({len(rows)} rows, showing {min(max_show, len(rows))})")
    print(f"{'─'*70}")
    for r in rows[:max_show]:
        print(f"  {json.dumps({k: str(v) for k,v in r.items()}, ensure_ascii=False)}")
    if len(rows) > max_show:
        print(f"  ... +{len(rows)-max_show} rows lainnya")


def upsert_rows(cur, table, rows, conflict_cols, update_cols=None):
    """
    Upsert dengan ON CONFLICT DO UPDATE atau DO NOTHING.
    conflict_cols: list of column names for the conflict target
    update_cols: list of columns to update on conflict (None = DO NOTHING)
    Returns count inserted/updated.
    """
    if not rows:
        return 0
    cols   = list(rows[0].keys())
    ph     = ", ".join(["%s"] * len(cols))
    cn     = ", ".join(cols)
    ct     = ", ".join(conflict_cols)
    if update_cols:
        upd = ", ".join([f"{c}=EXCLUDED.{c}" for c in update_cols])
        suffix = f"ON CONFLICT ({ct}) DO UPDATE SET {upd}"
    else:
        suffix = f"ON CONFLICT ({ct}) DO NOTHING"
    sql = f"INSERT INTO {table} ({cn}) VALUES ({ph}) {suffix}"
    count = 0
    for row in rows:
        cur.execute(sql, list(row.values()))
        count += cur.rowcount
    return count


def upsert_stock_rows(cur, rows):
    """
    Upsert lumra_config_stock without relying on a database unique constraint.

    The stock table has an index on (variant_id, location_id), but not a unique
    constraint, so PostgreSQL cannot use ON CONFLICT for this pair.
    """
    count = 0
    for row in rows:
        cur.execute(
            """
            UPDATE lumra_config_stock
            SET quantity=%s,
                transaction_type=%s,
                notes=%s,
                reserved_quantity=%s,
                last_updated=%s
            WHERE variant_id=%s AND location_id=%s
            """,
            (
                row["quantity"],
                row["transaction_type"],
                row["notes"],
                row["reserved_quantity"],
                row["last_updated"],
                row["variant_id"],
                row["location_id"],
            ),
        )

        if cur.rowcount:
            count += cur.rowcount
            continue

        cur.execute(
            """
            INSERT INTO lumra_config_stock
            (variant_id, location_id, quantity, transaction_type, notes,
             reserved_quantity, last_updated, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                row["variant_id"],
                row["location_id"],
                row["quantity"],
                row["transaction_type"],
                row["notes"],
                row["reserved_quantity"],
                row["last_updated"],
                row["created_at"],
            ),
        )
        count += cur.rowcount

    return count


def fetch_one(cur, sql, params=()):
    cur.execute(sql, params)
    r = cur.fetchone()
    return r[0] if r else None


def fetch_all(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SYSTEM_NUMBERING_SEQUENCES
# ═══════════════════════════════════════════════════════════════════════════════
# Format nomor otomatis untuk semua dokumen transaksi.
# use_date_prefix=True  → ORD-2024-00001
# use_date_prefix=False → PV-00001

NUMBERING_SEQUENCES = [
    # POS & Penjualan
    {
        "key":            "sale_order",
        "name":           "Nomor Order Penjualan",
        "prefix":         "ORD",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "payment",
        "name":           "Nomor Pembayaran",
        "prefix":         "PAY",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "return_order",
        "name":           "Nomor Retur Penjualan",
        "prefix":         "RET",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    # Inventori
    {
        "key":            "stock_transfer",
        "name":           "Nomor Transfer Stok",
        "prefix":         "TRF",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "requisition",
        "name":           "Nomor Requisition",
        "prefix":         "REQ",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "stock_opname",
        "name":           "Nomor Stock Opname",
        "prefix":         "SOP",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "product_batch",
        "name":           "Nomor Batch Produk",
        "prefix":         "BTH",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    # Akuntansi
    {
        "key":            "journal_entry",
        "name":           "Nomor Jurnal",
        "prefix":         "JE",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "payment_voucher",
        "name":           "Nomor Payment Voucher",
        "prefix":         "PV",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "invoice_ar",
        "name":           "Nomor Invoice Piutang",
        "prefix":         "INV",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "invoice_ap",
        "name":           "Nomor Invoice Hutang",
        "prefix":         "BILL",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    # Produksi
    {
        "key":            "production_order",
        "name":           "Nomor Order Produksi",
        "prefix":         "PRD",
        "digits":         5,
        "current_value":  0,
        "reset_period":   "yearly",
        "use_date_prefix": True,
        "is_active":      True,
        "updated_at":     NOW,
    },
    {
        "key":            "bom",
        "name":           "Nomor Bill of Materials",
        "prefix":         "BOM",
        "digits":         4,
        "current_value":  1,  # sudah ada 1 BOM
        "reset_period":   "none",
        "use_date_prefix": False,
        "is_active":      True,
        "updated_at":     NOW,
    },
    # Sistem
    {
        "key":            "api_key",
        "name":           "Nomor API Key",
        "prefix":         "lmr",
        "digits":         8,
        "current_value":  0,
        "reset_period":   "none",
        "use_date_prefix": False,
        "is_active":      True,
        "updated_at":     NOW,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SYSTEM_EMAIL_SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

EMAIL_SETTINGS = {
    "encryption":      "TLS",
    "host":            "smtp.gmail.com",
    "port":            587,
    "username":        "noreply@kafenusantara.id",
    "password":        "GANTI_DENGAN_APP_PASSWORD",  # ganti setelah seed
    "from_name":       "Kafe Nusantara System",
    "from_email":      "noreply@kafenusantara.id",
    "enabled":         False,   # aktifkan setelah konfigurasi real
    "test_recipient":  "admin@kafenusantara.id",
    "updated_by_id":   None,    # akan diisi dengan admin user id
    "updated_at":      NOW,
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ACCOUNTING_ACCOUNTS — Chart of Accounts (CoA)
# ═══════════════════════════════════════════════════════════════════════════════
# Struktur CoA untuk Kafe Nusantara:
# Level 1 = Kelompok utama    (allow_posting=False)
# Level 2 = Sub kelompok      (allow_posting=False)
# Level 3 = Akun detail       (allow_posting=True)
#
# Format: parent_code=None → root. parent_code="X-XXXX" → child.
# Script akan resolve parent_id secara otomatis.

COA_RAW = [
    # ══════════════════════════════════════════
    # 1 — ASET
    # ══════════════════════════════════════════
    {"code":"1-0000","name":"Aset",                            "type":"asset",    "level":1,"parent_code":None,   "allow_posting":False,"is_cash":False,"opening":0},

    # 1.1 Aset Lancar
    {"code":"1-1000","name":"Aset Lancar",                     "type":"asset",    "level":2,"parent_code":"1-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"1-1001","name":"Kas Tunai — Operasional",         "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":True, "opening":5000000},
    {"code":"1-1002","name":"Kas Tunai — Petty Cash Outpost",  "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":True, "opening":2000000},
    {"code":"1-1010","name":"Bank BCA — Operasional Utama",    "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":True, "opening":50000000},
    {"code":"1-1011","name":"Bank Mandiri — Payroll",          "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":True, "opening":20000000},
    {"code":"1-1012","name":"Bank BNI — Tabungan Ekspansi",    "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":True, "opening":100000000},
    {"code":"1-1020","name":"QRIS Settlement Account",         "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":True, "opening":0},
    {"code":"1-1021","name":"GoPay / OVO Settlement",          "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":True, "opening":0},
    {"code":"1-1100","name":"Piutang Dagang",                  "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-1101","name":"Piutang Karyawan",                "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-1200","name":"Persediaan — Bahan Baku Kopi",    "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":15000000},
    {"code":"1-1201","name":"Persediaan — Bahan Baku F&B",     "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":8000000},
    {"code":"1-1202","name":"Persediaan — Merchandise",        "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":3000000},
    {"code":"1-1202","name":"Persediaan — Packaging",          "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":2000000},
    {"code":"1-1300","name":"Biaya Dibayar di Muka",           "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-1301","name":"Sewa Dibayar di Muka",            "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-1302","name":"Asuransi Dibayar di Muka",        "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-1400","name":"PPN Masukan",                     "type":"asset",    "level":3,"parent_code":"1-1000","allow_posting":True, "is_cash":False,"opening":0},

    # 1.2 Aset Tetap
    {"code":"1-2000","name":"Aset Tetap",                      "type":"asset",    "level":2,"parent_code":"1-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"1-2001","name":"Mesin Espresso & Grinder",        "type":"asset",    "level":3,"parent_code":"1-2000","allow_posting":True, "is_cash":False,"opening":350000000},
    {"code":"1-2002","name":"Peralatan Roastery",              "type":"asset",    "level":3,"parent_code":"1-2000","allow_posting":True, "is_cash":False,"opening":500000000},
    {"code":"1-2003","name":"Furnitur & Fixture Outpost",      "type":"asset",    "level":3,"parent_code":"1-2000","allow_posting":True, "is_cash":False,"opening":200000000},
    {"code":"1-2004","name":"Kendaraan Operasional",           "type":"asset",    "level":3,"parent_code":"1-2000","allow_posting":True, "is_cash":False,"opening":150000000},
    {"code":"1-2005","name":"Komputer & Perangkat POS",        "type":"asset",    "level":3,"parent_code":"1-2000","allow_posting":True, "is_cash":False,"opening":50000000},
    {"code":"1-2100","name":"Akumulasi Penyusutan",            "type":"asset",    "level":2,"parent_code":"1-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"1-2101","name":"Akum. Penys. Mesin & Grinder",   "type":"asset",    "level":3,"parent_code":"1-2100","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-2102","name":"Akum. Penys. Peralatan Roastery", "type":"asset",   "level":3,"parent_code":"1-2100","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-2103","name":"Akum. Penys. Furnitur Outpost",   "type":"asset",   "level":3,"parent_code":"1-2100","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-2104","name":"Akum. Penys. Kendaraan",          "type":"asset",   "level":3,"parent_code":"1-2100","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"1-2105","name":"Akum. Penys. Perangkat POS",      "type":"asset",   "level":3,"parent_code":"1-2100","allow_posting":True, "is_cash":False,"opening":0},

    # 1.3 Aset Tidak Berwujud
    {"code":"1-3000","name":"Aset Tidak Berwujud",             "type":"asset",    "level":2,"parent_code":"1-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"1-3001","name":"Hak Merek Kafe Nusantara",        "type":"asset",    "level":3,"parent_code":"1-3000","allow_posting":True, "is_cash":False,"opening":50000000},
    {"code":"1-3002","name":"Software POS & ERP",              "type":"asset",    "level":3,"parent_code":"1-3000","allow_posting":True, "is_cash":False,"opening":30000000},
    {"code":"1-3003","name":"Biaya Pengembangan Aplikasi",     "type":"asset",    "level":3,"parent_code":"1-3000","allow_posting":True, "is_cash":False,"opening":20000000},

    # ══════════════════════════════════════════
    # 2 — KEWAJIBAN
    # ══════════════════════════════════════════
    {"code":"2-0000","name":"Kewajiban",                       "type":"liability","level":1,"parent_code":None,   "allow_posting":False,"is_cash":False,"opening":0},

    # 2.1 Kewajiban Lancar
    {"code":"2-1000","name":"Kewajiban Lancar",                "type":"liability","level":2,"parent_code":"2-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"2-1001","name":"Hutang Dagang — Supplier Kopi",   "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1002","name":"Hutang Dagang — Supplier F&B",    "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1003","name":"Hutang Dagang — Packaging",       "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1010","name":"Utang Gaji Karyawan",             "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1011","name":"Utang BPJS Ketenagakerjaan",      "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1012","name":"Utang PPh 21 Karyawan",           "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1020","name":"PPN Keluaran",                    "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1021","name":"Utang PPh 23",                    "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1030","name":"Pendapatan Diterima di Muka",     "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1031","name":"Deposit Loyalty / Voucher",       "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-1040","name":"Utang Sewa Jangka Pendek",        "type":"liability","level":3,"parent_code":"2-1000","allow_posting":True, "is_cash":False,"opening":0},

    # 2.2 Kewajiban Jangka Panjang
    {"code":"2-2000","name":"Kewajiban Jangka Panjang",        "type":"liability","level":2,"parent_code":"2-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"2-2001","name":"Utang Bank — KMK BCA",            "type":"liability","level":3,"parent_code":"2-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-2002","name":"Utang Bank — KI Mandiri",         "type":"liability","level":3,"parent_code":"2-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"2-2010","name":"Utang Sewa Jangka Panjang",       "type":"liability","level":3,"parent_code":"2-2000","allow_posting":True, "is_cash":False,"opening":0},

    # ══════════════════════════════════════════
    # 3 — EKUITAS
    # ══════════════════════════════════════════
    {"code":"3-0000","name":"Ekuitas",                         "type":"equity",   "level":1,"parent_code":None,   "allow_posting":False,"is_cash":False,"opening":0},
    {"code":"3-1000","name":"Modal Disetor",                   "type":"equity",   "level":2,"parent_code":"3-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"3-1001","name":"Modal Awal Grand Curator",        "type":"equity",   "level":3,"parent_code":"3-1000","allow_posting":True, "is_cash":False,"opening":1000000000},
    {"code":"3-1002","name":"Tambahan Modal Disetor",          "type":"equity",   "level":3,"parent_code":"3-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"3-2000","name":"Laba Ditahan",                    "type":"equity",   "level":2,"parent_code":"3-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"3-2001","name":"Laba Ditahan Tahun Lalu",         "type":"equity",   "level":3,"parent_code":"3-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"3-2002","name":"Laba / Rugi Tahun Berjalan",      "type":"equity",   "level":3,"parent_code":"3-2000","allow_posting":True, "is_cash":False,"opening":0},

    # ══════════════════════════════════════════
    # 4 — PENDAPATAN
    # ══════════════════════════════════════════
    {"code":"4-0000","name":"Pendapatan",                      "type":"revenue",  "level":1,"parent_code":None,   "allow_posting":False,"is_cash":False,"opening":0},

    # 4.1 Pendapatan Utama
    {"code":"4-1000","name":"Pendapatan Penjualan",            "type":"revenue",  "level":2,"parent_code":"4-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"4-1001","name":"Penjualan — Minuman Panas",       "type":"revenue",  "level":3,"parent_code":"4-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-1002","name":"Penjualan — Minuman Dingin",      "type":"revenue",  "level":3,"parent_code":"4-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-1003","name":"Penjualan — Makanan & Pastry",    "type":"revenue",  "level":3,"parent_code":"4-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-1004","name":"Penjualan — Kopi Retail & Bag",   "type":"revenue",  "level":3,"parent_code":"4-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-1005","name":"Penjualan — Merchandise Ekspedisi","type":"revenue", "level":3,"parent_code":"4-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-1006","name":"Penjualan — Grand Reserve Menu",  "type":"revenue",  "level":3,"parent_code":"4-1000","allow_posting":True, "is_cash":False,"opening":0},

    # 4.2 Pendapatan Lain
    {"code":"4-2000","name":"Pendapatan Lain-lain",            "type":"revenue",  "level":2,"parent_code":"4-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"4-2001","name":"Pendapatan Franchise Fee",        "type":"revenue",  "level":3,"parent_code":"4-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-2002","name":"Pendapatan Expedition Passport",  "type":"revenue",  "level":3,"parent_code":"4-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-2003","name":"Pendapatan Cupping & Workshop",   "type":"revenue",  "level":3,"parent_code":"4-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-2004","name":"Pendapatan Bunga Bank",           "type":"revenue",  "level":3,"parent_code":"4-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-2005","name":"Pendapatan Lainnya",              "type":"revenue",  "level":3,"parent_code":"4-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-3000","name":"Retur & Diskon Penjualan",        "type":"revenue",  "level":2,"parent_code":"4-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"4-3001","name":"Retur Penjualan",                 "type":"revenue",  "level":3,"parent_code":"4-3000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"4-3002","name":"Diskon Penjualan",                "type":"revenue",  "level":3,"parent_code":"4-3000","allow_posting":True, "is_cash":False,"opening":0},

    # ══════════════════════════════════════════
    # 5 — HARGA POKOK
    # ══════════════════════════════════════════
    {"code":"5-0000","name":"Harga Pokok Penjualan",           "type":"expense",  "level":1,"parent_code":None,   "allow_posting":False,"is_cash":False,"opening":0},
    {"code":"5-1000","name":"HPP — Minuman",                   "type":"expense",  "level":2,"parent_code":"5-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"5-1001","name":"HPP — Biji Kopi & Roasting",      "type":"expense",  "level":3,"parent_code":"5-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-1002","name":"HPP — Susu & Dairy",              "type":"expense",  "level":3,"parent_code":"5-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-1003","name":"HPP — Sirup & Bahan Pendukung",   "type":"expense",  "level":3,"parent_code":"5-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-2000","name":"HPP — Makanan",                   "type":"expense",  "level":2,"parent_code":"5-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"5-2001","name":"HPP — Pastry & Bakery",           "type":"expense",  "level":3,"parent_code":"5-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-2002","name":"HPP — Savory & Kitchen",          "type":"expense",  "level":3,"parent_code":"5-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-3000","name":"HPP — Retail & Merchandise",      "type":"expense",  "level":2,"parent_code":"5-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"5-3001","name":"HPP — Kopi Retail",               "type":"expense",  "level":3,"parent_code":"5-3000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-3002","name":"HPP — Merchandise Ekspedisi",     "type":"expense",  "level":3,"parent_code":"5-3000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-4000","name":"Biaya Produksi Lainnya",          "type":"expense",  "level":2,"parent_code":"5-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"5-4001","name":"Biaya Tenaga Kerja Langsung",     "type":"expense",  "level":3,"parent_code":"5-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-4002","name":"Overhead Produksi Roastery",      "type":"expense",  "level":3,"parent_code":"5-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-4003","name":"Biaya Waste & Susut Produksi",    "type":"expense",  "level":3,"parent_code":"5-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"5-4004","name":"Packaging & Supplies",            "type":"expense",  "level":3,"parent_code":"5-4000","allow_posting":True, "is_cash":False,"opening":0},

    # ══════════════════════════════════════════
    # 6 — BIAYA OPERASIONAL
    # ══════════════════════════════════════════
    {"code":"6-0000","name":"Biaya Operasional",               "type":"expense",  "level":1,"parent_code":None,   "allow_posting":False,"is_cash":False,"opening":0},

    # 6.1 Biaya Personalia
    {"code":"6-1000","name":"Biaya Personalia",                "type":"expense",  "level":2,"parent_code":"6-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"6-1001","name":"Gaji — Barista & Kasir",          "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-1002","name":"Gaji — Outpost Manager",          "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-1003","name":"Gaji — Regional Manager",         "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-1004","name":"Gaji — Head Roaster & HQ",        "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-1005","name":"BPJS Ketenagakerjaan",            "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-1006","name":"BPJS Kesehatan",                  "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-1007","name":"Tunjangan Makan & Transport",     "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-1008","name":"Biaya Training & Sertifikasi",    "type":"expense",  "level":3,"parent_code":"6-1000","allow_posting":True, "is_cash":False,"opening":0},

    # 6.2 Biaya Outpost / Sewa
    {"code":"6-2000","name":"Biaya Tempat & Utilitas",         "type":"expense",  "level":2,"parent_code":"6-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"6-2001","name":"Sewa Outpost — Phase 1 Jawa",     "type":"expense",  "level":3,"parent_code":"6-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-2002","name":"Sewa Outpost — Phase 2 Sumatera", "type":"expense",  "level":3,"parent_code":"6-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-2003","name":"Sewa Outpost — Phase 3 Bali&Timur","type":"expense", "level":3,"parent_code":"6-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-2004","name":"Sewa Roastery — The Final Meridian","type":"expense","level":3,"parent_code":"6-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-2010","name":"Listrik — Outpost",               "type":"expense",  "level":3,"parent_code":"6-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-2011","name":"Air — Outpost",                   "type":"expense",  "level":3,"parent_code":"6-2000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-2012","name":"Internet & Telepon",              "type":"expense",  "level":3,"parent_code":"6-2000","allow_posting":True, "is_cash":False,"opening":0},

    # 6.3 Biaya Marketing & Ekspedisi
    {"code":"6-3000","name":"Biaya Marketing & Brand",         "type":"expense",  "level":2,"parent_code":"6-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"6-3001","name":"Iklan & Promosi Digital",         "type":"expense",  "level":3,"parent_code":"6-3000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-3002","name":"Event & Grand Expedition Gala",   "type":"expense",  "level":3,"parent_code":"6-3000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-3003","name":"Desain & Konten Kreatif",         "type":"expense",  "level":3,"parent_code":"6-3000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-3004","name":"Expedition Passport — Reward",    "type":"expense",  "level":3,"parent_code":"6-3000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-3005","name":"Biaya Artefak Display Outpost",   "type":"expense",  "level":3,"parent_code":"6-3000","allow_posting":True, "is_cash":False,"opening":0},

    # 6.4 Biaya Administrasi
    {"code":"6-4000","name":"Biaya Administrasi & Umum",       "type":"expense",  "level":2,"parent_code":"6-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"6-4001","name":"Biaya Kantor & ATK",              "type":"expense",  "level":3,"parent_code":"6-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-4002","name":"Biaya Software & Lisensi",        "type":"expense",  "level":3,"parent_code":"6-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-4003","name":"Biaya Asuransi",                  "type":"expense",  "level":3,"parent_code":"6-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-4004","name":"Biaya Legal & Notaris",           "type":"expense",  "level":3,"parent_code":"6-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-4005","name":"Biaya Akuntansi & Audit",         "type":"expense",  "level":3,"parent_code":"6-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-4006","name":"Biaya Perjalanan Dinas",          "type":"expense",  "level":3,"parent_code":"6-4000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-4007","name":"Biaya Representasi & Kuratorial", "type":"expense",  "level":3,"parent_code":"6-4000","allow_posting":True, "is_cash":False,"opening":0},

    # 6.5 Biaya Keuangan
    {"code":"6-5000","name":"Biaya Keuangan",                  "type":"expense",  "level":2,"parent_code":"6-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"6-5001","name":"Biaya Bunga Pinjaman",            "type":"expense",  "level":3,"parent_code":"6-5000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-5002","name":"Biaya Administrasi Bank",         "type":"expense",  "level":3,"parent_code":"6-5000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-5003","name":"Biaya Transfer & Payment Gateway","type":"expense",  "level":3,"parent_code":"6-5000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-5004","name":"Selisih Kurs",                    "type":"expense",  "level":3,"parent_code":"6-5000","allow_posting":True, "is_cash":False,"opening":0},

    # 6.6 Penyusutan
    {"code":"6-6000","name":"Biaya Penyusutan",                "type":"expense",  "level":2,"parent_code":"6-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"6-6001","name":"Penys. Mesin Espresso & Grinder", "type":"expense",  "level":3,"parent_code":"6-6000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-6002","name":"Penys. Peralatan Roastery",       "type":"expense",  "level":3,"parent_code":"6-6000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-6003","name":"Penys. Furnitur & Fixture",       "type":"expense",  "level":3,"parent_code":"6-6000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-6004","name":"Penys. Kendaraan",                "type":"expense",  "level":3,"parent_code":"6-6000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-6005","name":"Penys. Perangkat POS",            "type":"expense",  "level":3,"parent_code":"6-6000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-6006","name":"Amortisasi Aset Tidak Berwujud",  "type":"expense",  "level":3,"parent_code":"6-6000","allow_posting":True, "is_cash":False,"opening":0},

    # 6.7 Biaya Pajak
    {"code":"6-7000","name":"Biaya Pajak",                     "type":"expense",  "level":2,"parent_code":"6-0000","allow_posting":False,"is_cash":False,"opening":0},
    {"code":"6-7001","name":"PPh Badan",                       "type":"expense",  "level":3,"parent_code":"6-7000","allow_posting":True, "is_cash":False,"opening":0},
    {"code":"6-7002","name":"PBB & Pajak Daerah",              "type":"expense",  "level":3,"parent_code":"6-7000","allow_posting":True, "is_cash":False,"opening":0},
]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. LUMRA_CONFIG_SALES_TARGETS — Target penjualan 12 bulan ke depan
# ═══════════════════════════════════════════════════════════════════════════════
# Target berdasarkan fase ekspansi Kafe Nusantara (35 outpost)
# Dihitung berdasarkan asumsi:
#   - 22 outpost Jawa: avg Rp 50jt/bulan/outpost
#   - 7 outpost Sumatera: avg Rp 35jt/bulan/outpost
#   - 6 outpost Bali & Timur: avg Rp 40jt/bulan/outpost
# Total basis: 22×50 + 7×35 + 6×40 = 1100 + 245 + 240 = 1585jt/bulan
# Dengan growth factor seasonal dan ramping new outpost

YEAR = TODAY.year

def gen_sales_targets():
    targets = []
    # Monthly multiplier (seasonal): Jan ramp-up, peak Aug-Sep (lebaran preparation), dip Feb
    seasonal = {1:0.85, 2:0.80, 3:0.90, 4:1.05, 5:1.10, 6:1.00,
                7:0.95, 8:1.15, 9:1.10, 10:1.00, 11:1.05, 12:1.20}
    base = 1_585_000_000  # 1.585 Miliar
    for m in range(1, 13):
        targets.append({
            "year":          YEAR,
            "month":         m,
            "target_amount": int(base * seasonal[m]),
            "notes":         (
                f"Target {YEAR} — Phase 1 Jawa (22 outpost) + "
                f"Phase 2 Sumatera (7 outpost) + Phase 3 Bali & Timur (6 outpost). "
                f"Faktor seasonal {seasonal[m]}"
            ),
            "created_by_id": None,  # akan diisi dengan admin user id
            "created_at":    NOW,
            "updated_at":    NOW,
        })
    # Tambah target tahun depan untuk planning
    next_year = YEAR + 1
    for m in range(1, 7):  # H1 tahun depan
        targets.append({
            "year":          next_year,
            "month":         m,
            "target_amount": int(base * seasonal[m] * 1.15),  # 15% growth
            "notes":         f"Target {next_year} H1 — projected 15% growth dari {YEAR}",
            "created_by_id": None,
            "created_at":    NOW,
            "updated_at":    NOW,
        })
    return targets


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run():
    print("\n" + "═"*72)
    print("  KAFE NUSANTARA — Seed Pre-Transaksi")
    print("  Tabel wajib sebelum transaksi apapun bisa berjalan")
    print("═"*72)
    if DRY_RUN:
        print("\n  ⚠  MODE DRY RUN — tidak ada yang disimpan ke database\n")
    if SECTION != "all":
        print(f"  ► Section filter: {SECTION}\n")

    conn = None
    cur  = None
    if not DRY_RUN:
        conn = get_conn()
        cur  = conn.cursor()

    results = {}

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1: SYSTEM_NUMBERING_SEQUENCES
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("numbering"):
        print("\n" + "▓"*60)
        print("  [1/8] SYSTEM_NUMBERING_SEQUENCES")
        print("▓"*60)
        preview("system_numbering_sequences", NUMBERING_SEQUENCES)
        if not DRY_RUN:
            n = upsert_rows(cur, "system_numbering_sequences",
                            NUMBERING_SEQUENCES, ["key"],
                            update_cols=["name","prefix","digits","reset_period",
                                         "use_date_prefix","is_active","updated_at"])
            conn.commit()
            results["numbering_sequences"] = n
            print(f"\n  ✓ {n} rows upserted")
        else:
            results["numbering_sequences"] = len(NUMBERING_SEQUENCES)
            print(f"\n  ✓ [DRY RUN] {len(NUMBERING_SEQUENCES)} rows akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2: SYSTEM_EMAIL_SETTINGS
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("email"):
        print("\n" + "▓"*60)
        print("  [2/8] SYSTEM_EMAIL_SETTINGS")
        print("▓"*60)

        # Cari admin user id
        admin_id = None
        if not DRY_RUN:
            admin_id = fetch_one(cur, "SELECT id FROM auth_user WHERE username='admin' LIMIT 1")
            if not admin_id:
                admin_id = fetch_one(cur, "SELECT id FROM auth_user ORDER BY id LIMIT 1")

        email_row = dict(EMAIL_SETTINGS)
        email_row["updated_by_id"] = admin_id

        preview("system_email_settings", [email_row])
        if not DRY_RUN:
            # Tabel ini tidak punya unique key yang jelas — hapus dulu jika ada, insert baru
            cur.execute("SELECT COUNT(*) FROM system_email_settings")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute(
                    "INSERT INTO system_email_settings "
                    "(encryption,host,port,username,password,from_name,from_email,"
                    "enabled,test_recipient,updated_by_id,updated_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    list(email_row.values())
                )
                conn.commit()
                results["email_settings"] = 1
                print(f"\n  ✓ 1 row inserted")
            else:
                print(f"\n  ⚠  Sudah ada {count} row — skip (tidak overwrite konfigurasi existing)")
                results["email_settings"] = 0
        else:
            results["email_settings"] = 1
            print(f"\n  ✓ [DRY RUN] 1 row akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3: ACCOUNTING_ACCOUNTS (CoA)
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("coa"):
        print("\n" + "▓"*60)
        print("  [3/8] ACCOUNTING_ACCOUNTS — Chart of Accounts")
        print("▓"*60)

        # Deduplicate COA_RAW by code (ambil yang pertama jika ada duplikat)
        seen_codes = {}
        coa_dedup = []
        for c in COA_RAW:
            if c["code"] not in seen_codes:
                seen_codes[c["code"]] = True
                coa_dedup.append(c)

        # Pass 1: insert roots (parent_code=None)
        roots    = [c for c in coa_dedup if c["parent_code"] is None]
        children = [c for c in coa_dedup if c["parent_code"] is not None]

        code_to_id = {}

        def build_coa_row(c, parent_id):
            return {
                "code":            c["code"],
                "name":            c["name"],
                "account_type":    c["type"],
                "level":           c["level"],
                "parent_id":       parent_id,
                "is_active":       True,
                "allow_posting":   c["allow_posting"],
                "is_cash_account": c["is_cash"],
                "opening_balance": c["opening"],
                "notes":           "",
                "created_at":      NOW,
                "updated_at":      NOW,
            }

        root_rows = [build_coa_row(c, None) for c in roots]
        preview("accounting_accounts (root, level 1)", root_rows)

        if not DRY_RUN:
            for row in root_rows:
                cur.execute(
                    "INSERT INTO accounting_accounts "
                    "(code,name,account_type,level,parent_id,is_active,allow_posting,"
                    "is_cash_account,opening_balance,notes,created_at,updated_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                    "ON CONFLICT (code) DO UPDATE SET "
                    "name=EXCLUDED.name,account_type=EXCLUDED.account_type,"
                    "level=EXCLUDED.level,allow_posting=EXCLUDED.allow_posting,"
                    "is_cash_account=EXCLUDED.is_cash_account,"
                    "opening_balance=EXCLUDED.opening_balance,"
                    "updated_at=EXCLUDED.updated_at "
                    "RETURNING id, code",
                    list(row.values())
                )
                res = cur.fetchone()
                if res:
                    code_to_id[res[1]] = res[0]
            conn.commit()

            # Re-fetch semua existing untuk children
            rows_existing = fetch_all(cur, "SELECT id, code FROM accounting_accounts")
            for rid, rcode in rows_existing:
                code_to_id[rcode] = rid

        else:
            # Dry run: simulasi id
            for i, c in enumerate(roots):
                code_to_id[c["code"]] = i + 1

        # Pass 2: children (level 2 dan 3)
        # Urut dari level rendah ke tinggi
        children_sorted = sorted(children, key=lambda x: x["level"])
        child_rows = []
        skip_count = 0
        for c in children_sorted:
            parent_id = code_to_id.get(c["parent_code"])
            if parent_id is None and not DRY_RUN:
                skip_count += 1
                continue
            child_rows.append(build_coa_row(c, parent_id or 999))

        preview("accounting_accounts (level 2-3)", child_rows)

        if not DRY_RUN:
            for row in child_rows:
                cur.execute(
                    "INSERT INTO accounting_accounts "
                    "(code,name,account_type,level,parent_id,is_active,allow_posting,"
                    "is_cash_account,opening_balance,notes,created_at,updated_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                    "ON CONFLICT (code) DO UPDATE SET "
                    "name=EXCLUDED.name,parent_id=EXCLUDED.parent_id,"
                    "allow_posting=EXCLUDED.allow_posting,"
                    "is_cash_account=EXCLUDED.is_cash_account,"
                    "opening_balance=EXCLUDED.opening_balance,"
                    "updated_at=EXCLUDED.updated_at "
                    "RETURNING id, code",
                    list(row.values())
                )
                res = cur.fetchone()
                if res:
                    code_to_id[res[1]] = res[0]
            conn.commit()
            total_coa = len(root_rows) + len(child_rows)
            results["coa"] = total_coa
            print(f"\n  ✓ CoA: {len(root_rows)} root + {len(child_rows)} children = {total_coa} akun")
            if skip_count:
                print(f"  ⚠  {skip_count} akun dilewati (parent tidak ditemukan)")
        else:
            total_coa = len(root_rows) + len(child_rows)
            results["coa"] = total_coa
            print(f"\n  ✓ [DRY RUN] {total_coa} akun akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4: LUMRA_CONFIG_SUPPLIER_PRICES
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("supplier_prices"):
        print("\n" + "▓"*60)
        print("  [4/8] LUMRA_CONFIG_SUPPLIER_PRICES")
        print("▓"*60)

        # Ambil vendor ids dan variant ids dari DB
        vendor_rows  = []
        variant_rows = []
        admin_id     = None

        if not DRY_RUN:
            vendor_rows  = fetch_all(cur, "SELECT id, code FROM lumra_config_vendors ORDER BY id LIMIT 20")
            variant_rows = fetch_all(cur,
                "SELECT id, sku FROM lumra_config_productvariants "
                "ORDER BY id LIMIT 100")
            admin_id = fetch_one(cur, "SELECT id FROM auth_user WHERE username='admin' LIMIT 1")
        else:
            # Simulasi
            vendor_rows  = [(i, f"VND-{i:03d}") for i in range(1, 11)]
            variant_rows = [(i, f"SKU-{i:05d}") for i in range(1, 51)]
            admin_id = 1

        if not vendor_rows or not variant_rows:
            print("  ⚠  Vendor atau variant belum ada — skip supplier_prices")
        else:
            # Generate sample: setiap vendor dikaitkan dengan beberapa varian
            sp_rows = []
            valid_until = date(TODAY.year, 12, 31)
            effective   = date(TODAY.year, 1, 1)

            # Ambil sample varian per vendor (maks 10 varian per vendor)
            random.shuffle(list(variant_rows))
            v_chunks = [variant_rows[i:i+10] for i in range(0, min(len(variant_rows), 100), 10)]

            for vi, (vid, vcode) in enumerate(vendor_rows[:10]):
                chunk = v_chunks[vi % len(v_chunks)]
                for var_id, var_sku in chunk:
                    base_price = random.randint(3000, 50000)
                    sp_rows.append({
                        "vendor_id":       vid,
                        "variant_id":      var_id,
                        "unit_price":      base_price,
                        "currency":        "IDR",
                        "minimum_quantity": random.choice([1, 6, 12, 24]),
                        "maximum_quantity": None,
                        "lead_time_days":  random.randint(1, 14),
                        "is_active":       True,
                        "is_preferred":    (vi == 0),  # vendor pertama = preferred
                        "effective_date":  effective,
                        "valid_until":     valid_until,
                        "created_at":      NOW,
                        "updated_at":      NOW,
                        "last_updated_by_id": admin_id,
                    })

            preview("lumra_config_supplier_prices", sp_rows)
            if not DRY_RUN:
                n = upsert_rows(cur, "lumra_config_supplier_prices", sp_rows,
                                ["vendor_id","variant_id"],
                                update_cols=["unit_price","lead_time_days","valid_until",
                                             "is_active","is_preferred","updated_at"])
                conn.commit()
                results["supplier_prices"] = n
                print(f"\n  ✓ {n} supplier price rows upserted")
            else:
                results["supplier_prices"] = len(sp_rows)
                print(f"\n  ✓ [DRY RUN] {len(sp_rows)} rows akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 5: LUMRA_CONFIG_SALES_TARGETS
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("sales_targets"):
        print("\n" + "▓"*60)
        print("  [5/8] LUMRA_CONFIG_SALES_TARGETS")
        print("▓"*60)

        admin_id = None
        if not DRY_RUN:
            admin_id = fetch_one(cur, "SELECT id FROM auth_user WHERE username='admin' LIMIT 1")

        targets = gen_sales_targets()
        for t in targets:
            t["created_by_id"] = admin_id

        preview("lumra_config_sales_targets", targets)

        if not DRY_RUN:
            n = upsert_rows(cur, "lumra_config_sales_targets", targets,
                            ["year","month"],
                            update_cols=["target_amount","notes","updated_at"])
            conn.commit()
            results["sales_targets"] = n
            print(f"\n  ✓ {n} target rows upserted")
        else:
            results["sales_targets"] = len(targets)
            print(f"\n  ✓ [DRY RUN] {len(targets)} rows akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 6: LUMRA_CONFIG_STOCK (stok awal per varian per lokasi)
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("stock"):
        print("\n" + "▓"*60)
        print("  [6/8] LUMRA_CONFIG_STOCK — Stok Awal")
        print("▓"*60)
        print("  Logika: ambil kombinasi variant × location yang belum ada stoknya")
        print("  lalu seed dengan qty opening yang masuk akal per tipe lokasi")

        loc_rows     = []
        variant_rows = []

        if not DRY_RUN:
            loc_rows     = fetch_all(cur, "SELECT id, name, location_type FROM lumra_config_locations ORDER BY id LIMIT 56")
            variant_rows = fetch_all(cur,
                "SELECT pv.id, p.min_stock, p.max_stock "
                "FROM lumra_config_productvariants pv "
                "JOIN lumra_config_products p ON pv.product_id = p.id "
                "WHERE p.is_active=true ORDER BY pv.id LIMIT 200")
        else:
            loc_rows     = [(i, f"Lokasi {i}", "warehouse" if i <= 5 else "store") for i in range(1, 15)]
            variant_rows = [(i, 10, 200) for i in range(1, 51)]

        stock_rows = []
        for loc_id, loc_name, loc_type in loc_rows:
            # Tentukan qty range berdasarkan tipe lokasi
            qty_factor = {"warehouse": (50, 200), "store": (10, 80)}.get(loc_type, (5, 50))

            for var_id, min_stock, max_stock in variant_rows[:50]:  # sample 50 varian
                qty = random.randint(int(qty_factor[0]), int(qty_factor[1]))
                stock_rows.append({
                    "variant_id":         var_id,
                    "location_id":        loc_id,
                    "quantity":           qty,
                    "transaction_type":   "opening",
                    "notes":              f"Stok awal opening — {loc_name}",
                    "reserved_quantity":  0,
                    "last_updated":       NOW,
                    "created_at":         NOW,
                })

        preview("lumra_config_stock", stock_rows)
        print(f"  Total: {len(stock_rows)} stock rows ({len(loc_rows)} lokasi × ~50 varian)")

        if not DRY_RUN:
            n = upsert_stock_rows(cur, stock_rows)
            conn.commit()
            results["stock"] = n
            print(f"\n  ✓ {n} stock rows upserted")
        else:
            results["stock"] = len(stock_rows)
            print(f"\n  ✓ [DRY RUN] {len(stock_rows)} rows akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 7: LUMRA_CONFIG_INVENTORY_BATCHES
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("inventory_batches"):
        print("\n" + "▓"*60)
        print("  [7/8] LUMRA_CONFIG_INVENTORY_BATCHES")
        print("▓"*60)

        loc_rows     = []
        zone_rows    = []
        variant_rows = []
        admin_id     = None

        if not DRY_RUN:
            loc_rows     = fetch_all(cur,
                "SELECT id FROM lumra_config_locations WHERE location_type='warehouse' LIMIT 10")
            zone_rows    = fetch_all(cur,
                "SELECT id, location_id FROM lumra_config_warehouse_zones "
                "WHERE is_active=true LIMIT 50")
            variant_rows = fetch_all(cur,
                "SELECT id FROM lumra_config_productvariants ORDER BY id LIMIT 100")
            admin_id     = fetch_one(cur, "SELECT id FROM auth_user WHERE username='admin' LIMIT 1")
        else:
            loc_rows     = [(i,) for i in range(1, 6)]
            zone_rows    = [(i, ((i-1)//5)+1) for i in range(1, 21)]
            variant_rows = [(i,) for i in range(1, 51)]
            admin_id = 1

        if not loc_rows:
            print("  ⚠  Tidak ada warehouse location — skip")
        else:
            batch_rows = []
            zone_by_loc = {}
            for zone_id, loc_id in zone_rows:
                zone_by_loc.setdefault(loc_id, []).append(zone_id)

            batch_counter = 1
            for (loc_id,) in loc_rows:
                zones = zone_by_loc.get(loc_id, [None])
                for (var_id,) in variant_rows[:20]:
                    zone_id = random.choice(zones)
                    prod_date = TODAY - timedelta(days=random.randint(30, 180))
                    exp_date  = TODAY + timedelta(days=random.randint(90, 365))
                    qty = random.randint(20, 100)
                    batch_rows.append({
                        "variant_id":       var_id,
                        "location_id":      loc_id,
                        "zone_id":          zone_id,
                        "code":             f"INV-{batch_counter:05d}",
                        "quantity_on_hand": qty,
                        "production_date":  prod_date,
                        "expiry_date":      exp_date,
                        "notes":            "Stok awal seed",
                        "created_by_id":    admin_id,
                        "created_at":       NOW,
                        "updated_at":       NOW,
                    })
                    batch_counter += 1

            preview("lumra_config_inventory_batches", batch_rows)
            if not DRY_RUN:
                n = upsert_rows(cur, "lumra_config_inventory_batches", batch_rows,
                                ["location_id","code"],
                                update_cols=["quantity_on_hand","updated_at"])
                conn.commit()
                results["inventory_batches"] = n
                print(f"\n  ✓ {n} inventory batch rows upserted")
            else:
                results["inventory_batches"] = len(batch_rows)
                print(f"\n  ✓ [DRY RUN] {len(batch_rows)} rows akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 8: PRODUCTION_BILL_OF_MATERIALS
    # ─────────────────────────────────────────────────────────────────────────
    if should_run("bom"):
        print("\n" + "▓"*60)
        print("  [8/8] PRODUCTION_BILL_OF_MATERIALS")
        print("▓"*60)
        print("  Sudah ada 1 BOM di DB. Script menambah BOM untuk varian produk utama.")

        admin_id     = None
        variant_rows = []

        if not DRY_RUN:
            admin_id     = fetch_one(cur, "SELECT id FROM auth_user WHERE username='admin' LIMIT 1")
            variant_rows = fetch_all(cur,
                "SELECT pv.id, pv.sku, p.name "
                "FROM lumra_config_productvariants pv "
                "JOIN lumra_config_products p ON pv.product_id=p.id "
                "WHERE p.is_active=true AND p.has_expiry=false "
                "ORDER BY pv.id LIMIT 30")
        else:
            variant_rows = [(i, f"SKU-{i:05d}", f"Produk {i}") for i in range(1, 11)]
            admin_id = 1

        bom_rows = []
        bom_counter = 2  # sudah ada 1
        for var_id, sku, prod_name in variant_rows:
            bom_rows.append({
                "finished_variant_id": var_id,
                "code":               f"BOM-{bom_counter:04d}",
                "version":            1,
                "name":               f"BOM — {prod_name} ({sku})",
                "is_active":          True,
                "notes":              "Generated dari seed pre-transaksi",
                "created_by_id":      admin_id,
                "created_at":         NOW,
                "updated_at":         NOW,
            })
            bom_counter += 1

        preview("production_bill_of_materials", bom_rows)
        if not DRY_RUN:
            n = upsert_rows(cur, "production_bill_of_materials", bom_rows,
                            ["code"],
                            update_cols=["name","is_active","updated_at"])
            conn.commit()
            results["bom"] = n
            print(f"\n  ✓ {n} BOM rows upserted")
        else:
            results["bom"] = len(bom_rows)
            print(f"\n  ✓ [DRY RUN] {len(bom_rows)} rows akan diinsert")

    # ─────────────────────────────────────────────────────────────────────────
    # Cleanup
    # ─────────────────────────────────────────────────────────────────────────
    if not DRY_RUN and cur:
        cur.close()
        conn.close()

    # ─────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "═"*72)
    print("  RINGKASAN SEED PRE-TRANSAKSI")
    print("─"*72)
    table_map = {
        "numbering_sequences": "system_numbering_sequences",
        "email_settings":      "system_email_settings",
        "coa":                 "accounting_accounts (CoA)",
        "supplier_prices":     "lumra_config_supplier_prices",
        "sales_targets":       "lumra_config_sales_targets",
        "stock":               "lumra_config_stock",
        "inventory_batches":   "lumra_config_inventory_batches",
        "bom":                 "production_bill_of_materials",
    }
    total = 0
    for key, tname in table_map.items():
        val = results.get(key, "—")
        total += val if isinstance(val, int) else 0
        print(f"  {tname:<45} {str(val):>8} rows")
    print("─"*72)
    print(f"  {'TOTAL':<45} {total:>8} rows")
    print("─"*72)
    print("""
  LANGKAH BERIKUTNYA setelah seed ini:
  ─────────────────────────────────────────────────────────────────────
  1. system_email_settings → Ganti password SMTP dengan App Password Gmail
     kemudian set enabled=True setelah test berhasil.

  2. accounting_accounts   → Review CoA, tambahkan akun khusus jika perlu.
     Pastikan opening_balance sudah sesuai neraca awal bisnis.

  3. lumra_config_stock    → Script ini hanya seed sample 50 varian × semua lokasi.
     Jalankan script terpisah untuk full stock sesuai data fisik gudang.

  4. lumra_config_supplier_prices → Script seed sample 10 vendor × 10 varian.
     Isi harga real per vendor dari data negosiasi aktual.

  5. production_bill_of_materials → Setelah BOM ada, lengkapi dengan
     production_bom_items (komponen per BOM) — tabel ini MISSING di DB,
     perlu dibuatkan via migration terlebih dahulu.

  6. system_stores         → Audit 36 rows yang sudah ada, sesuaikan dengan
     35 outpost Archipelagic Outposts + 1 HQ Final Meridian.
  ─────────────────────────────────────────────────────────────────────
""")
    if DRY_RUN:
        print("  ⚠  Dry run selesai. Tidak ada data yang disimpan.")
    else:
        print("  ✓ Semua section selesai. Database siap untuk transaksi.")
    print("═"*72 + "\n")


if __name__ == "__main__":
    run()
