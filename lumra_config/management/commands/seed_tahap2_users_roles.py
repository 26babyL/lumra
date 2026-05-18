"""
seed_tahap2_users_roles.py
==========================
Seed script untuk Tahap 2: User & Role
Tabel yang diisi (urutan insert):
  1. auth_user               — semua user sistem
  2. system_roles            — role kustom aplikasi
  3. system_role_permissions — hak akses per role per modul
  4. system_user_roles       — mapping user ke role
  5. lumra_config_userprofile — profil tambahan user

Konsep disesuaikan dengan universe Kafe Nusantara:
  - 35 Outpost (Phase 1 Jawa, Phase 2 Sumatera, Phase 3 Bali & Timur)
  - The Final Meridian sebagai HQ/Roastery
  - Role hierarki: Grand Curator → Regional Manager → Outpost Manager
    → Senior Barista → Barista → Cashier → Warehouse Staff → Finance

Nama karyawan diambil random dari lumra_config_customers (jika tersedia).
Jika tabel customers belum ada / kosong, fallback ke daftar nama hardcoded.

Cara pakai:
  pip install psycopg2-binary
  python seed_tahap2_users_roles.py --dry-run   # preview saja
  python seed_tahap2_users_roles.py             # simpan ke DB
"""

import sys
import random
import json
import hashlib
import secrets
import re
from datetime import datetime, timezone, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATABASE = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "lumra_set_allegra",
    "user":     "postgres",
    "password": "123456",
}

# Password default untuk semua user seed (hashed via Django's PBKDF2)
# Di production, ganti via Django manage.py atau admin panel
DEFAULT_PASSWORD_PLAIN = "Ekspedisi2024!"
# ─────────────────────────────────────────────────────────────────────────────

DRY_RUN   = "--dry-run" in sys.argv
NOW       = datetime.now(timezone.utc)
random.seed(42)  # reproducible


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_conn():
    import psycopg2
    return psycopg2.connect(**DATABASE)


def make_django_password(plain: str) -> str:
    """
    Buat hash password kompatibel Django PBKDF2SHA256.
    Format: pbkdf2_sha256$<iterations>$<salt>$<hash>
    """
    import hashlib, base64, hmac
    iterations = 870000
    salt = secrets.token_hex(11)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        plain.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
        dklen=32,
    )
    import base64
    b64hash = base64.b64encode(dk).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt}${b64hash}"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def preview(table, rows, max_show=5):
    print(f"\n{'─'*68}")
    print(f"  TABLE: {table}  ({len(rows)} rows total, showing first {min(max_show, len(rows))})")
    print(f"{'─'*68}")
    for r in rows[:max_show]:
        print(f"  {json.dumps({k: str(v) for k,v in r.items()}, ensure_ascii=False)}")
    if len(rows) > max_show:
        print(f"  ... dan {len(rows)-max_show} baris lainnya")


def insert_many(cur, table, rows, conflict_col=None, return_col="id"):
    """
    Bulk insert. Jika conflict_col diberikan → ON CONFLICT DO NOTHING.
    Returns list of inserted ids.
    """
    if not rows:
        return []
    cols = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_names    = ", ".join(cols)
    conflict = f"ON CONFLICT ({conflict_col}) DO NOTHING" if conflict_col else ""
    sql = (
        f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) "
        f"{conflict} RETURNING {return_col}"
    )
    ids = []
    for row in rows:
        cur.execute(sql, list(row.values()))
        res = cur.fetchone()
        if res:
            ids.append(res[0])
    return ids


def upsert_roles(cur, roles):
    """
    Insert/update system_roles while reusing older role rows.

    The table has unique constraints on both name and code. Older seed data used
    shorter codes such as BAR/KSR/GDG, so ON CONFLICT(code) is not enough when
    the role name already exists.
    """
    legacy_aliases = {
        "SUPERADMIN": {
            "names": ["Super Admin", "Admin"],
            "codes": ["SUPER_ADMIN", "ADM"],
        },
        "OUTPOST_MANAGER": {
            "names": ["Manager"],
            "codes": ["MGR"],
        },
        "HEAD_ROASTER": {
            "names": ["Roaster"],
            "codes": ["RST"],
        },
        "BARISTA": {
            "names": ["Staff"],
            "codes": ["BAR", "STAFF"],
        },
        "CASHIER": {
            "names": ["Kasir"],
            "codes": ["KSR"],
        },
        "WAREHOUSE_STAFF": {
            "names": ["Gudang"],
            "codes": ["GDG"],
        },
    }

    role_ids = []
    for role in roles:
        aliases = legacy_aliases.get(role["code"], {})
        names = [role["name"], *aliases.get("names", [])]
        codes = [role["code"], *aliases.get("codes", [])]

        cur.execute(
            """
            SELECT id
            FROM system_roles
            WHERE code = ANY(%s) OR name = ANY(%s)
            ORDER BY
              CASE
                WHEN name = %s THEN 0
                WHEN code = %s THEN 1
                ELSE 2
              END,
              id
            LIMIT 1
            """,
            (codes, names, role["name"], role["code"]),
        )
        existing = cur.fetchone()

        if existing:
            cur.execute(
                """
                UPDATE system_roles
                SET name=%s,
                    code=%s,
                    description=%s,
                    role_type=%s,
                    is_active=%s,
                    is_system=%s,
                    updated_at=%s
                WHERE id=%s
                RETURNING id
                """,
                (
                    role["name"],
                    role["code"],
                    role["description"],
                    role["role_type"],
                    role["is_active"],
                    role["is_system"],
                    role["updated_at"],
                    existing[0],
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO system_roles
                (name, code, description, role_type, is_active, is_system, created_at, updated_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (
                    role["name"],
                    role["code"],
                    role["description"],
                    role["role_type"],
                    role["is_active"],
                    role["is_system"],
                    role["created_at"],
                    role["updated_at"],
                ),
            )

        role_ids.append(cur.fetchone()[0])

    return role_ids


def fetch_customer_names(cur, limit=300):
    """Ambil nama dari lumra_config_customers jika tersedia."""
    try:
        cur.execute(
            "SELECT name FROM lumra_config_customers "
            "WHERE name IS NOT NULL AND name != '' "
            "ORDER BY name LIMIT %s",
            (limit,)
        )
        rows = cur.fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []


def fetch_location_ids(cur):
    """Ambil semua location id yang tersedia."""
    try:
        cur.execute("SELECT id, name FROM lumra_config_locations ORDER BY id")
        return cur.fetchall()  # list of (id, name)
    except Exception:
        return []


# ── FALLBACK NAMES (dipakai jika customers tabel kosong) ─────────────────────
FALLBACK_NAMES = [
    "Ahmad Fauzi","Budi Santoso","Citra Dewi","Dian Permata","Eko Prasetyo",
    "Fitriani Sari","Guntur Wicaksono","Hana Kusuma","Indra Wijaya","Joko Susilo",
    "Kartika Putri","Luthfi Hakim","Maya Anggraeni","Nanda Rizky","Okta Suhendra",
    "Putri Rahayu","Qori Islamiyah","Reza Firmansyah","Sinta Maharani","Taufik Hidayat",
    "Ulfa Nuraini","Vino Pradipta","Wulandari Saputri","Xena Mahardhika","Yusuf Kurniawan",
    "Zahra Azizah","Aditya Nugraha","Bella Octaviani","Cahyo Purnomo","Dina Rosmawati",
    "Endra Setiawan","Farah Diba","Gilang Ramadhan","Hesti Wulandari","Irfan Maulana",
    "Julia Susanti","Kevin Hartanto","Laila Nurazizah","Muhamad Ridwan","Nita Permatasari",
    "Oscar Budiman","Prita Andriani","Rian Saputra","Syifa Fadilah","Tika Ramadhani",
    "Usman Harun","Vika Amelia","Wahyu Pratama","Yanti Kusumawati","Zaki Abdullah",
    "Angga Saputra","Bayu Nugroho","Clara Handayani","Dede Hermawan","Elsa Rahmawati",
    "Fajar Kusuma","Grace Susanto","Hendra Gunawan","Ika Yulianti","Jimmy Salim",
    "Kiki Andriani","Lukman Hakim","Mira Lestari","Niko Santoso","Opik Nurwahid",
    "Pandu Kusuma","Qila Rahmadani","Rika Apriyanti","Surya Dinata","Tomi Wibowo",
    "Uni Maharani","Vendi Saputra","Wendi Kurniawan","Yogi Prasetyo","Zulfa Karima",
    "Arief Hidayat","Bondan Setya","Caca Putri","Dodi Prabowo","Elva Nuraeni",
    "Fandi Ahmad","Gita Nirmala","Hadi Sasmita","Ita Damayanti","Jefri Iskandar",
    "Kania Rahayu","Lina Andriyani","Maman Suherman","Nina Permatasari","Oki Firdaus",
    "Pepen Suparno","Riyan Maulana","Sari Indah","Teguh Santosa","Umi Kulsum",
    "Vera Andriani","Wawan Setiawan","Yayan Taryana","Zainab Mardiah","Agus Salim",
]


def split_name(full_name: str):
    parts = full_name.strip().split()
    first = parts[0] if parts else "User"
    last  = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first, last


def make_username(full_name: str, suffix: str = "") -> str:
    parts  = full_name.lower().strip().split()
    first  = re.sub(r"[^a-z]", "", parts[0]) if parts else "user"
    last   = re.sub(r"[^a-z]", "", parts[-1]) if len(parts) > 1 else ""
    base   = f"{first}.{last}" if last else first
    return f"{base}{suffix}" if suffix else base


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ROLES DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

ROLES = [
    {
        "name": "Grand Curator",
        "code": "GRAND_CURATOR",
        "description": (
            "Pemilik dan kepala ekspedisi. Akses penuh ke semua sistem termasuk "
            "Grand Reserve, Final Meridian, dan seluruh 35 Outpost."
        ),
        "role_type": "system",
        "is_active": True,
        "is_system": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Superadmin",
        "code": "SUPERADMIN",
        "description": (
            "Administrator teknis sistem. Akses penuh ke konfigurasi sistem, "
            "user management, dan semua modul. Tidak perlu akses ke floor."
        ),
        "role_type": "system",
        "is_active": True,
        "is_system": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Regional Manager",
        "code": "REGIONAL_MANAGER",
        "description": (
            "Manajer regional yang mengawasi beberapa outpost dalam satu phase "
            "(Phase 1 Jawa / Phase 2 Sumatera / Phase 3 Bali & Timur). "
            "Akses laporan semua outpost di regionnya, approval transfer & requisition."
        ),
        "role_type": "management",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Finance Manager",
        "code": "FINANCE_MANAGER",
        "description": (
            "Manajer keuangan. Akses penuh ke modul akuntansi: journal entries, "
            "AP/AR, payment vouchers, dan laporan keuangan semua outpost."
        ),
        "role_type": "management",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Outpost Manager",
        "code": "OUTPOST_MANAGER",
        "description": (
            "Manajer outpost individual. Bertanggung jawab atas operasional harian, "
            "approval requisition, laporan penjualan, dan pengelolaan tim di outpost-nya."
        ),
        "role_type": "operational",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Head Roaster",
        "code": "HEAD_ROASTER",
        "description": (
            "Kepala roastery di The Final Meridian. Akses ke produksi, BOM, resep, "
            "blend management, dan Grand Reserve menu. Khusus 1 orang di HQ."
        ),
        "role_type": "specialist",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Senior Barista",
        "code": "SENIOR_BARISTA",
        "description": (
            "Barista senior dengan akses training, cupping session, dan mentoring. "
            "Bisa input catatan resep dan feedback blend ke Head Roaster."
        ),
        "role_type": "operational",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Barista",
        "code": "BARISTA",
        "description": (
            "Barista reguler. Akses POS (buat order, proses pembayaran), "
            "lihat menu harian, dan input stockopname di akhir shift."
        ),
        "role_type": "operational",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Cashier",
        "code": "CASHIER",
        "description": (
            "Kasir outpost. Akses POS untuk transaksi penjualan, proses pembayaran, "
            "cetak struk, dan refund sederhana."
        ),
        "role_type": "operational",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Warehouse Staff",
        "code": "WAREHOUSE_STAFF",
        "description": (
            "Staff gudang. Akses pengelolaan stok: terima transfer, proses requisition, "
            "input stockopname, dan kelola batch produk."
        ),
        "role_type": "operational",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Finance Staff",
        "code": "FINANCE_STAFF",
        "description": (
            "Staff keuangan outpost. Akses input pembayaran, lihat AP/AR outpost, "
            "dan submit laporan keuangan ke Finance Manager."
        ),
        "role_type": "operational",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "name": "Expedition Guide",
        "code": "EXPEDITION_GUIDE",
        "description": (
            "Pemandu di Origin Outpost (Gayo, Kintamani, Toraja). Akses cupping session, "
            "tour scheduling, dan input catatan farm-to-cup."
        ),
        "role_type": "specialist",
        "is_active": True,
        "is_system": False,
        "created_at": NOW,
        "updated_at": NOW,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PERMISSIONS MATRIX PER ROLE PER MODULE
# ═══════════════════════════════════════════════════════════════════════════════
#
# Modules dalam sistem Kafe Nusantara:
#   pos.orders          — POS & Transaksi penjualan
#   pos.payments        — Pembayaran
#   pos.returns         — Retur penjualan
#   inventory.stock     — Stok & movement
#   inventory.transfer  — Transfer & requisition
#   inventory.batch     — Batch tracking & expiry
#   inventory.opname    — Stock opname
#   purchasing.vendor   — Vendor management
#   purchasing.prices   — Harga supplier
#   production.recipe   — Resep & BOM
#   production.orders   — Order produksi
#   production.waste    — Waste records
#   accounting.journal  — Jurnal akuntansi
#   accounting.ap_ar    — AP / AR
#   accounting.voucher  — Payment vouchers
#   customer.profiles   — Data customer
#   customer.loyalty    — Loyalty & passport ekspedisi
#   reporting.sales     — Laporan penjualan
#   reporting.inventory — Laporan inventori
#   reporting.finance   — Laporan keuangan
#   system.users        — User management
#   system.roles        — Role & permission
#   system.config       — Konfigurasi sistem
#   blend.recipes       — Manajemen blend & kurator
#   blend.grand_reserve — Grand Reserve (khusus Head Roaster & Grand Curator)

MODULES = [
    ("pos.orders",           "POS - Orders & Transaksi"),
    ("pos.payments",         "POS - Pembayaran"),
    ("pos.returns",          "POS - Retur Penjualan"),
    ("inventory.stock",      "Inventori - Stok & Movement"),
    ("inventory.transfer",   "Inventori - Transfer & Requisition"),
    ("inventory.batch",      "Inventori - Batch Tracking"),
    ("inventory.opname",     "Inventori - Stock Opname"),
    ("purchasing.vendor",    "Pembelian - Vendor"),
    ("purchasing.prices",    "Pembelian - Harga Supplier"),
    ("production.recipe",    "Produksi - Resep & BOM"),
    ("production.orders",    "Produksi - Order Produksi"),
    ("production.waste",     "Produksi - Waste Records"),
    ("accounting.journal",   "Akuntansi - Jurnal"),
    ("accounting.ap_ar",     "Akuntansi - AP/AR"),
    ("accounting.voucher",   "Akuntansi - Payment Voucher"),
    ("customer.profiles",    "Customer - Profil"),
    ("customer.loyalty",     "Customer - Loyalty & Passport"),
    ("reporting.sales",      "Laporan - Penjualan"),
    ("reporting.inventory",  "Laporan - Inventori"),
    ("reporting.finance",    "Laporan - Keuangan"),
    ("system.users",         "Sistem - User Management"),
    ("system.roles",         "Sistem - Role & Permission"),
    ("system.config",        "Sistem - Konfigurasi"),
    ("blend.recipes",        "Blend - Resep & Kurasi"),
    ("blend.grand_reserve",  "Blend - Grand Reserve"),
]

# access_level: "full" | "read_write" | "read_only" | "none"
# Tuple: (access_level, can_create, can_update, can_delete, can_approve)
PERM_FULL       = ("full",        True,  True,  True,  True)
PERM_RW         = ("read_write",  True,  True,  False, False)
PERM_RW_APPROVE = ("read_write",  True,  True,  False, True)
PERM_RO_APPROVE = ("read_only",   False, False, False, True)
PERM_RO         = ("read_only",   False, False, False, False)
PERM_NONE       = ("none",        False, False, False, False)

# Matrix: role_code → { module_key: perm_tuple }
PERMISSION_MATRIX = {

    "GRAND_CURATOR": {m[0]: PERM_FULL for m in MODULES},

    "SUPERADMIN": {
        "pos.orders":         PERM_RO,
        "pos.payments":       PERM_RO,
        "pos.returns":        PERM_RO,
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_RO,
        "inventory.batch":    PERM_RO,
        "inventory.opname":   PERM_RO,
        "purchasing.vendor":  PERM_FULL,
        "purchasing.prices":  PERM_FULL,
        "production.recipe":  PERM_RO,
        "production.orders":  PERM_RO,
        "production.waste":   PERM_RO,
        "accounting.journal": PERM_RO,
        "accounting.ap_ar":   PERM_RO,
        "accounting.voucher": PERM_RO,
        "customer.profiles":  PERM_FULL,
        "customer.loyalty":   PERM_FULL,
        "reporting.sales":    PERM_RO,
        "reporting.inventory":PERM_RO,
        "reporting.finance":  PERM_RO,
        "system.users":       PERM_FULL,
        "system.roles":       PERM_FULL,
        "system.config":      PERM_FULL,
        "blend.recipes":      PERM_RO,
        "blend.grand_reserve":PERM_RO,
    },

    "REGIONAL_MANAGER": {
        "pos.orders":         PERM_RO,
        "pos.payments":       PERM_RO,
        "pos.returns":        PERM_RO_APPROVE,
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_RW_APPROVE,
        "inventory.batch":    PERM_RO,
        "inventory.opname":   PERM_RO_APPROVE,
        "purchasing.vendor":  PERM_RO,
        "purchasing.prices":  PERM_RO,
        "production.recipe":  PERM_RO,
        "production.orders":  PERM_RO_APPROVE,
        "production.waste":   PERM_RO,
        "accounting.journal": PERM_RO,
        "accounting.ap_ar":   PERM_RO,
        "accounting.voucher": PERM_RO_APPROVE,
        "customer.profiles":  PERM_RO,
        "customer.loyalty":   PERM_RW,
        "reporting.sales":    PERM_FULL,
        "reporting.inventory":PERM_FULL,
        "reporting.finance":  PERM_RO,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_RO,
        "blend.grand_reserve":PERM_NONE,
    },

    "FINANCE_MANAGER": {
        "pos.orders":         PERM_RO,
        "pos.payments":       PERM_RO,
        "pos.returns":        PERM_RO,
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_RO,
        "inventory.batch":    PERM_RO,
        "inventory.opname":   PERM_RO,
        "purchasing.vendor":  PERM_RW,
        "purchasing.prices":  PERM_RW,
        "production.recipe":  PERM_RO,
        "production.orders":  PERM_RO,
        "production.waste":   PERM_RO,
        "accounting.journal": PERM_FULL,
        "accounting.ap_ar":   PERM_FULL,
        "accounting.voucher": PERM_FULL,
        "customer.profiles":  PERM_RO,
        "customer.loyalty":   PERM_RO,
        "reporting.sales":    PERM_FULL,
        "reporting.inventory":PERM_RO,
        "reporting.finance":  PERM_FULL,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_NONE,
        "blend.grand_reserve":PERM_NONE,
    },

    "OUTPOST_MANAGER": {
        "pos.orders":         PERM_RW_APPROVE,
        "pos.payments":       PERM_RW_APPROVE,
        "pos.returns":        PERM_RW_APPROVE,
        "inventory.stock":    PERM_RW,
        "inventory.transfer": PERM_RW_APPROVE,
        "inventory.batch":    PERM_RW,
        "inventory.opname":   PERM_RW_APPROVE,
        "purchasing.vendor":  PERM_RO,
        "purchasing.prices":  PERM_RO,
        "production.recipe":  PERM_RO,
        "production.orders":  PERM_RW,
        "production.waste":   PERM_RW,
        "accounting.journal": PERM_RO,
        "accounting.ap_ar":   PERM_RO,
        "accounting.voucher": PERM_RO,
        "customer.profiles":  PERM_RW,
        "customer.loyalty":   PERM_RW,
        "reporting.sales":    PERM_RO,
        "reporting.inventory":PERM_RO,
        "reporting.finance":  PERM_NONE,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_RO,
        "blend.grand_reserve":PERM_NONE,
    },

    "HEAD_ROASTER": {
        "pos.orders":         PERM_NONE,
        "pos.payments":       PERM_NONE,
        "pos.returns":        PERM_NONE,
        "inventory.stock":    PERM_RW,
        "inventory.transfer": PERM_RO,
        "inventory.batch":    PERM_RW,
        "inventory.opname":   PERM_RO,
        "purchasing.vendor":  PERM_RO,
        "purchasing.prices":  PERM_RO,
        "production.recipe":  PERM_FULL,
        "production.orders":  PERM_FULL,
        "production.waste":   PERM_FULL,
        "accounting.journal": PERM_NONE,
        "accounting.ap_ar":   PERM_NONE,
        "accounting.voucher": PERM_NONE,
        "customer.profiles":  PERM_NONE,
        "customer.loyalty":   PERM_RO,
        "reporting.sales":    PERM_RO,
        "reporting.inventory":PERM_RO,
        "reporting.finance":  PERM_NONE,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_FULL,
        "blend.grand_reserve":PERM_FULL,
    },

    "SENIOR_BARISTA": {
        "pos.orders":         PERM_RW,
        "pos.payments":       PERM_RW,
        "pos.returns":        PERM_RW,
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_RO,
        "inventory.batch":    PERM_RO,
        "inventory.opname":   PERM_RW,
        "purchasing.vendor":  PERM_NONE,
        "purchasing.prices":  PERM_NONE,
        "production.recipe":  PERM_RO,
        "production.orders":  PERM_RO,
        "production.waste":   PERM_RW,
        "accounting.journal": PERM_NONE,
        "accounting.ap_ar":   PERM_NONE,
        "accounting.voucher": PERM_NONE,
        "customer.profiles":  PERM_RW,
        "customer.loyalty":   PERM_RW,
        "reporting.sales":    PERM_RO,
        "reporting.inventory":PERM_NONE,
        "reporting.finance":  PERM_NONE,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_RO,
        "blend.grand_reserve":PERM_NONE,
    },

    "BARISTA": {
        "pos.orders":         PERM_RW,
        "pos.payments":       PERM_RW,
        "pos.returns":        ("read_write", True, False, False, False),
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_NONE,
        "inventory.batch":    PERM_NONE,
        "inventory.opname":   ("read_write", True, False, False, False),
        "purchasing.vendor":  PERM_NONE,
        "purchasing.prices":  PERM_NONE,
        "production.recipe":  PERM_RO,
        "production.orders":  PERM_NONE,
        "production.waste":   PERM_NONE,
        "accounting.journal": PERM_NONE,
        "accounting.ap_ar":   PERM_NONE,
        "accounting.voucher": PERM_NONE,
        "customer.profiles":  ("read_write", True, True, False, False),
        "customer.loyalty":   ("read_write", True, True, False, False),
        "reporting.sales":    PERM_NONE,
        "reporting.inventory":PERM_NONE,
        "reporting.finance":  PERM_NONE,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_RO,
        "blend.grand_reserve":PERM_NONE,
    },

    "CASHIER": {
        "pos.orders":         PERM_RW,
        "pos.payments":       PERM_RW,
        "pos.returns":        ("read_write", True, False, False, False),
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_NONE,
        "inventory.batch":    PERM_NONE,
        "inventory.opname":   PERM_NONE,
        "purchasing.vendor":  PERM_NONE,
        "purchasing.prices":  PERM_NONE,
        "production.recipe":  PERM_NONE,
        "production.orders":  PERM_NONE,
        "production.waste":   PERM_NONE,
        "accounting.journal": PERM_NONE,
        "accounting.ap_ar":   PERM_NONE,
        "accounting.voucher": PERM_NONE,
        "customer.profiles":  ("read_write", True, True, False, False),
        "customer.loyalty":   ("read_write", False, True, False, False),
        "reporting.sales":    PERM_NONE,
        "reporting.inventory":PERM_NONE,
        "reporting.finance":  PERM_NONE,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_NONE,
        "blend.grand_reserve":PERM_NONE,
    },

    "WAREHOUSE_STAFF": {
        "pos.orders":         PERM_RO,
        "pos.payments":       PERM_NONE,
        "pos.returns":        PERM_RO,
        "inventory.stock":    PERM_RW,
        "inventory.transfer": PERM_RW,
        "inventory.batch":    PERM_RW,
        "inventory.opname":   PERM_RW,
        "purchasing.vendor":  PERM_RO,
        "purchasing.prices":  PERM_RO,
        "production.recipe":  PERM_NONE,
        "production.orders":  PERM_RO,
        "production.waste":   PERM_RW,
        "accounting.journal": PERM_NONE,
        "accounting.ap_ar":   PERM_NONE,
        "accounting.voucher": PERM_NONE,
        "customer.profiles":  PERM_NONE,
        "customer.loyalty":   PERM_NONE,
        "reporting.sales":    PERM_NONE,
        "reporting.inventory":PERM_RO,
        "reporting.finance":  PERM_NONE,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_NONE,
        "blend.grand_reserve":PERM_NONE,
    },

    "FINANCE_STAFF": {
        "pos.orders":         PERM_RO,
        "pos.payments":       PERM_RW,
        "pos.returns":        PERM_RO,
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_RO,
        "inventory.batch":    PERM_NONE,
        "inventory.opname":   PERM_NONE,
        "purchasing.vendor":  PERM_RO,
        "purchasing.prices":  PERM_RO,
        "production.recipe":  PERM_NONE,
        "production.orders":  PERM_NONE,
        "production.waste":   PERM_NONE,
        "accounting.journal": PERM_RW,
        "accounting.ap_ar":   PERM_RW,
        "accounting.voucher": PERM_RW,
        "customer.profiles":  PERM_RO,
        "customer.loyalty":   PERM_NONE,
        "reporting.sales":    PERM_RO,
        "reporting.inventory":PERM_NONE,
        "reporting.finance":  PERM_RO,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_NONE,
        "blend.grand_reserve":PERM_NONE,
    },

    "EXPEDITION_GUIDE": {
        "pos.orders":         PERM_RO,
        "pos.payments":       PERM_NONE,
        "pos.returns":        PERM_NONE,
        "inventory.stock":    PERM_RO,
        "inventory.transfer": PERM_NONE,
        "inventory.batch":    PERM_RO,
        "inventory.opname":   PERM_RO,
        "purchasing.vendor":  PERM_NONE,
        "purchasing.prices":  PERM_NONE,
        "production.recipe":  PERM_RW,
        "production.orders":  PERM_RO,
        "production.waste":   PERM_RW,
        "accounting.journal": PERM_NONE,
        "accounting.ap_ar":   PERM_NONE,
        "accounting.voucher": PERM_NONE,
        "customer.profiles":  PERM_RO,
        "customer.loyalty":   PERM_RO,
        "reporting.sales":    PERM_NONE,
        "reporting.inventory":PERM_NONE,
        "reporting.finance":  PERM_NONE,
        "system.users":       PERM_NONE,
        "system.roles":       PERM_NONE,
        "system.config":      PERM_NONE,
        "blend.recipes":      PERM_RW,
        "blend.grand_reserve":PERM_NONE,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. OUTPOST → LOCATION MAPPING (untuk userprofile.location_id)
# ═══════════════════════════════════════════════════════════════════════════════
# Daftar 35 outpost + tipe + phase (dipakai untuk assign user ke lokasi)
OUTPOSTS = [
    # Phase 1 - Jawa
    (1,  "The Batavia Loghouse",        "Kota Tua",          "outpost", "jawa"),
    (2,  "The Priangan Counting House", "Braga",             "outpost", "jawa"),
    (3,  "The Preanger Hillpost",       "Dago Atas",         "shelter", "jawa"),
    (4,  "The Ciliwung Depot",          "Menteng",           "outpost", "jawa"),
    (5,  "The Glass Meridian",          "SCBD",              "outpost", "jawa"),
    (6,  "The Kemang Waystation",       "Kemang",            "outpost", "jawa"),
    (7,  "The Cikini Reading Room",     "Cikini",            "shelter", "jawa"),
    (8,  "The Kelapa Gading Anchorage", "Kelapa Gading",     "outpost", "jawa"),
    (9,  "The Serpong Survey Camp",     "BSD City",          "outpost", "jawa"),
    (10, "The Depok Crossroads",        "Margonda",          "outpost", "jawa"),
    (11, "The Bogor Botanical Gate",    "Suryakencana",      "outpost", "jawa"),
    (12, "The Karawang Transit Point",  "Kawasan Industri",  "outpost", "jawa"),
    (13, "The Cirebon Passage",         "Pelabuhan Lama",    "outpost", "jawa"),
    (14, "The Semarang Customs House",  "Kota Lama",         "outpost", "jawa"),
    (15, "The Solo Kepatihan Shelter",  "Laweyan",           "shelter", "jawa"),
    (16, "The Yogyakarta Elevation Post","Prawirotaman",     "outpost", "jawa"),
    (17, "The Surabaya Iron Wharf",     "Tunjungan",         "outpost", "jawa"),
    (18, "The Malang Highland Camp",    "Kayutangan",        "shelter", "jawa"),
    (19, "The East Java Depot",         "Darmo",             "outpost", "jawa"),
    (20, "The Mojokerto Field Station", "Pusat Kota",        "outpost", "jawa"),
    (21, "The Banyuwangi Shore Post",   "Pusat Kota",        "shelter", "jawa"),
    (22, "The Final Meridian",          "Jakarta Selatan",   "roastery","hq"),
    # Phase 2 - Sumatera
    (23, "The Aceh Gateway",            "Peunayong",         "outpost", "sumatera"),
    (24, "The Medan Trade Post",        "Kesawan",           "outpost", "sumatera"),
    (25, "The Gayo Highlands Shelter",  "Takengon",          "shelter", "sumatera"),
    (26, "The Padang Spice Harbor",     "Kota Lama",         "outpost", "sumatera"),
    (27, "The Palembang River Station", "Tepian Musi",       "outpost", "sumatera"),
    (28, "The Batak Ridge Shelter",     "Parapat",           "shelter", "sumatera"),
    (29, "The Batam Free Port",         "Nagoya",            "outpost", "sumatera"),
    # Phase 3 - Bali & Timur
    (30, "The Kintamani Crater Post",   "Kintamani",         "outpost", "bali_timur"),
    (31, "The Denpasar Island Hub",     "Seminyak",          "outpost", "bali_timur"),
    (32, "The Makassar Fortpost",       "Losari",            "outpost", "bali_timur"),
    (33, "The Toraja Forest Shelter",   "Rantepao",          "shelter", "bali_timur"),
    (34, "The Manado Northern Reach",   "Megamas",           "outpost", "bali_timur"),
    (35, "The Eastern Terminus",        "Jayapura",          "outpost", "bali_timur"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FIXED / VIP USERS (hardcoded, tidak random)
# ═══════════════════════════════════════════════════════════════════════════════
# Format: (username, first_name, last_name, email, role_code, outpost_no, is_staff, is_superuser)
FIXED_USERS = [
    # ── System ───────────────────────────────────────────────────────────────
    ("admin",           "System",    "Administrator", "admin@kafenusantara.id",          "SUPERADMIN",       22, True,  True),
    ("grand.curator",   "Sang",      "Kurator",       "curator@kafenusantara.id",        "GRAND_CURATOR",    22, True,  False),

    # ── HQ — The Final Meridian ───────────────────────────────────────────────
    ("roaster.kepala",  "Rizki",     "Dharmaputra",   "roaster@kafenusantara.id",        "HEAD_ROASTER",     22, False, False),
    ("finance.manager", "Elvira",    "Kusumastuti",   "finance@kafenusantara.id",        "FINANCE_MANAGER",  22, False, False),

    # ── Regional Managers ─────────────────────────────────────────────────────
    ("rm.jawa",         "Arya",      "Wicaksono",     "rm.jawa@kafenusantara.id",        "REGIONAL_MANAGER", 1,  False, False),
    ("rm.sumatera",     "Safitri",   "Harahap",       "rm.sumatera@kafenusantara.id",    "REGIONAL_MANAGER", 23, False, False),
    ("rm.bali",         "Gede",      "Dharma",        "rm.bali@kafenusantara.id",        "REGIONAL_MANAGER", 30, False, False),

    # ── Origin Outpost Guides ─────────────────────────────────────────────────
    ("guide.gayo",      "Hamzah",    "Syahputra",     "guide.gayo@kafenusantara.id",     "EXPEDITION_GUIDE", 25, False, False),
    ("guide.kintamani", "Wayan",     "Suardana",      "guide.kintamani@kafenusantara.id","EXPEDITION_GUIDE", 30, False, False),
    ("guide.toraja",    "Yenni",     "Palamba",       "guide.toraja@kafenusantara.id",   "EXPEDITION_GUIDE", 33, False, False),
]


# ═══════════════════════════════════════════════════════════════════════════════
# 5. GENERATE RANDOM STAFF PER OUTPOST
# ═══════════════════════════════════════════════════════════════════════════════
# Setiap outpost mendapat staf:
#   - 1 Outpost Manager
#   - 1–2 Senior Barista
#   - 2–3 Barista
#   - 1–2 Cashier
#   - 1 Warehouse Staff  (hanya outpost, bukan shelter)
#   - 1 Finance Staff    (hanya outpost)
# Shelter lebih kecil:
#   - 1 Outpost Manager
#   - 1 Senior Barista
#   - 1–2 Barista
#   - 1 Cashier

STAFF_BLUEPRINT = {
    "outpost":  [
        ("OUTPOST_MANAGER",  1, 1),
        ("SENIOR_BARISTA",   1, 2),
        ("BARISTA",          2, 3),
        ("CASHIER",          2, 3),
        ("WAREHOUSE_STAFF",  2, 3),
        ("FINANCE_STAFF",    1, 2),
    ],
    "shelter": [
        ("OUTPOST_MANAGER",  1, 1),
        ("SENIOR_BARISTA",   1, 2),
        ("BARISTA",          1, 2),
        ("CASHIER",          1, 2),
    ],
    "roastery": [],  # diisi manual via FIXED_USERS
}


def generate_staff(name_pool, used_usernames):
    """
    Generate daftar staff untuk semua 35 outpost.
    Returns list of dict dengan field auth_user + meta (role_code, outpost_no).
    """
    staff = []
    name_pool = list(name_pool)
    random.shuffle(name_pool)
    name_idx = 0

    for (outpost_no, outpost_name, area, otype, phase) in OUTPOSTS:
        if otype == "roastery":
            continue  # HQ diisi manual
        blueprint = STAFF_BLUEPRINT.get(otype, STAFF_BLUEPRINT["shelter"])

        for (role_code, min_n, max_n) in blueprint:
            count = random.randint(min_n, max_n)
            for _ in range(count):
                if name_idx >= len(name_pool):
                    name_idx = 0
                    random.shuffle(name_pool)

                full_name = name_pool[name_idx]
                name_idx += 1
                first, last = split_name(full_name)

                # Generate unique username
                base_uname = make_username(full_name)
                suffix = 1
                uname = base_uname
                while uname in used_usernames:
                    uname = f"{base_uname}{suffix}"
                    suffix += 1
                used_usernames.add(uname)

                role_slug = slugify(role_code)
                email = f"{uname}@kafenusantara.id"

                staff.append({
                    "_username":   uname,
                    "_first":      first,
                    "_last":       last,
                    "_email":      email,
                    "_role_code":  role_code,
                    "_outpost_no": outpost_no,
                })
    return staff


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run():
    print("\n" + "═" * 68)
    print("  KAFE NUSANTARA — Seed Tahap 2: User & Role")
    print("═" * 68)

    if DRY_RUN:
        print("\n  ⚠  MODE DRY RUN — tidak ada yang disimpan ke database\n")

    hashed_pw = make_django_password(DEFAULT_PASSWORD_PLAIN)
    print(f"  Password default: {DEFAULT_PASSWORD_PLAIN}")
    print(f"  Hash (PBKDF2):    {hashed_pw[:40]}...")

    # ── Koneksi DB (atau mock untuk dry-run) ──────────────────────────────────
    conn = None
    cur  = None
    if not DRY_RUN:
        conn = get_conn()
        cur  = conn.cursor()

    # ── Fetch nama dari customers ─────────────────────────────────────────────
    name_pool = []
    if not DRY_RUN:
        name_pool = fetch_customer_names(cur, limit=400)
        if name_pool:
            print(f"\n  ✓ Berhasil ambil {len(name_pool)} nama dari lumra_config_customers")
        else:
            print(f"\n  ⚠  Tabel customers kosong atau belum ada — pakai fallback names")

    if not name_pool:
        name_pool = FALLBACK_NAMES
        print(f"  ✓ Pakai {len(name_pool)} fallback names")

    # ── Fetch location ids ────────────────────────────────────────────────────
    location_rows = []
    loc_name_to_id = {}
    if not DRY_RUN:
        location_rows = fetch_location_ids(cur)
        loc_name_to_id = {name: lid for lid, name in location_rows}
        print(f"  ✓ Ditemukan {len(location_rows)} lokasi di DB")
    else:
        # Dry run: simulasi loc_id = outpost_no
        loc_name_to_id = {op[1]: op[0] for op in OUTPOSTS}

    # ── Generate staff list ───────────────────────────────────────────────────
    used_usernames = {u[0] for u in FIXED_USERS}
    staff_list = generate_staff(name_pool, used_usernames)
    print(f"  ✓ Generated {len(staff_list)} staff dari 35 outpost")
    print(f"  ✓ Fixed users: {len(FIXED_USERS)}")
    print(f"  ✓ Total users akan diinsert: {len(FIXED_USERS) + len(staff_list)}")

    # ═════════════════════════════════════════════════════════════════
    # STEP 1: SYSTEM_ROLES
    # ═════════════════════════════════════════════════════════════════
    preview("system_roles", ROLES)
    role_code_to_id = {}
    if not DRY_RUN:
        ids = upsert_roles(cur, ROLES)
        conn.commit()
        # Re-fetch untuk dapat id-nya (in case sudah ada)
        cur.execute("SELECT id, code FROM system_roles")
        role_code_to_id = {code: rid for rid, code in cur.fetchall()}
        print(f"\n  ✓ system_roles: {len(role_code_to_id)} roles tersedia")
    else:
        role_code_to_id = {r["code"]: i+1 for i, r in enumerate(ROLES)}

    # ═════════════════════════════════════════════════════════════════
    # STEP 2: SYSTEM_ROLE_PERMISSIONS
    # ═════════════════════════════════════════════════════════════════
    perm_rows = []
    for role_code, module_perms in PERMISSION_MATRIX.items():
        role_id = role_code_to_id.get(role_code)
        if not role_id:
            continue
        for (module_key, module_name) in MODULES:
            perm = module_perms.get(module_key, PERM_NONE)
            perm_rows.append({
                "role_id":      role_id,
                "module_key":   module_key,
                "module_name":  module_name,
                "access_level": perm[0],
                "can_create":   perm[1],
                "can_update":   perm[2],
                "can_delete":   perm[3],
                "can_approve":  perm[4],
                "created_at":   NOW,
                "updated_at":   NOW,
            })

    preview("system_role_permissions", perm_rows)
    if not DRY_RUN:
        # Hapus dulu jika ada konflik (role_id + module_key)
        for row in perm_rows:
            cur.execute(
                "INSERT INTO system_role_permissions "
                "(role_id, module_key, module_name, access_level, can_create, can_update, can_delete, can_approve, created_at, updated_at) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (role_id, module_key) DO UPDATE SET "
                "access_level=EXCLUDED.access_level, can_create=EXCLUDED.can_create, "
                "can_update=EXCLUDED.can_update, can_delete=EXCLUDED.can_delete, "
                "can_approve=EXCLUDED.can_approve, updated_at=EXCLUDED.updated_at",
                list(row.values())
            )
        conn.commit()
        print(f"\n  ✓ system_role_permissions: {len(perm_rows)} permission rows diinsert/diupdate")
    else:
        print(f"\n  ✓ [DRY RUN] {len(perm_rows)} permission rows akan diinsert")

    # ═════════════════════════════════════════════════════════════════
    # STEP 3: AUTH_USER
    # ═════════════════════════════════════════════════════════════════
    all_user_meta = []  # list of dict dengan _role_code, _outpost_no + user data

    # Fixed users
    joined_base = NOW - timedelta(days=365)
    for (uname, first, last, email, role_code, outpost_no, is_staff, is_su) in FIXED_USERS:
        all_user_meta.append({
            "password":     hashed_pw,
            "last_login":   None,
            "is_superuser": is_su,
            "username":     uname,
            "first_name":   first,
            "last_name":    last,
            "email":        email,
            "is_staff":     is_staff,
            "is_active":    True,
            "date_joined":  joined_base,
            # meta (tidak masuk ke auth_user)
            "_role_code":   role_code,
            "_outpost_no":  outpost_no,
        })

    # Random staff
    for s in staff_list:
        days_ago = random.randint(30, 365)
        all_user_meta.append({
            "password":     hashed_pw,
            "last_login":   None,
            "is_superuser": False,
            "username":     s["_username"],
            "first_name":   s["_first"],
            "last_name":    s["_last"],
            "email":        s["_email"],
            "is_staff":     False,
            "is_active":    True,
            "date_joined":  NOW - timedelta(days=days_ago),
            "_role_code":   s["_role_code"],
            "_outpost_no":  s["_outpost_no"],
        })

    # Pisahkan auth_user fields dari meta fields
    auth_user_rows = []
    for u in all_user_meta:
        auth_user_rows.append({k: v for k, v in u.items() if not k.startswith("_")})

    preview("auth_user", auth_user_rows)

    username_to_id = {}
    if not DRY_RUN:
        ids = insert_many(cur, "auth_user", auth_user_rows, conflict_col="username", return_col="id")
        conn.commit()
        # Re-fetch semua username → id
        cur.execute("SELECT id, username FROM auth_user")
        username_to_id = {uname: uid for uid, uname in cur.fetchall()}
        print(f"\n  ✓ auth_user: {len(username_to_id)} users tersedia di DB")
    else:
        username_to_id = {u["username"]: i+1 for i, u in enumerate(auth_user_rows)}
        print(f"\n  ✓ [DRY RUN] {len(auth_user_rows)} auth_user rows akan diinsert")

    # ═════════════════════════════════════════════════════════════════
    # STEP 4: SYSTEM_USER_ROLES
    # ═════════════════════════════════════════════════════════════════
    # Admin user id untuk assigned_by
    admin_id = username_to_id.get("admin", 1)

    user_role_rows = []
    for u in all_user_meta:
        uid     = username_to_id.get(u["username"])
        role_id = role_code_to_id.get(u["_role_code"])
        if not uid or not role_id:
            continue
        user_role_rows.append({
            "user_id":      uid,
            "role_id":      role_id,
            "assigned_by_id": admin_id,
            "assigned_at":  u.get("date_joined", NOW),
        })

    preview("system_user_roles", user_role_rows)
    if not DRY_RUN:
        # ON CONFLICT (user, role) DO NOTHING
        for row in user_role_rows:
            cur.execute(
                "INSERT INTO system_user_roles (user_id, role_id, assigned_by_id, assigned_at) "
                "VALUES (%s,%s,%s,%s) ON CONFLICT (user_id, role_id) DO NOTHING",
                list(row.values())
            )
        conn.commit()
        print(f"\n  ✓ system_user_roles: {len(user_role_rows)} mapping diinsert")
    else:
        print(f"\n  ✓ [DRY RUN] {len(user_role_rows)} user-role mapping akan diinsert")

    # ═════════════════════════════════════════════════════════════════
    # STEP 5: LUMRA_CONFIG_USERPROFILE
    # ═════════════════════════════════════════════════════════════════
    # Cari location_id berdasarkan outpost_no
    # Konvensi: location di DB seharusnya punya nama outpost yang sama
    # Fallback: jika tidak ditemukan, pakai outpost_no sebagai location_id langsung

    def get_loc_id(outpost_no):
        # Cari nama outpost
        for (no, name, area, otype, phase) in OUTPOSTS:
            if no == outpost_no:
                # Cari di loc_name_to_id
                if name in loc_name_to_id:
                    return loc_name_to_id[name]
                # Fallback: pakai id=outpost_no
                return outpost_no
        return None

    profile_rows = []
    for u in all_user_meta:
        uid = username_to_id.get(u["username"])
        if not uid:
            continue
        loc_id = get_loc_id(u["_outpost_no"])

        # Map role_code ke legacy role string (field 'role' di userprofile)
        legacy_role_map = {
            "GRAND_CURATOR":    "grand_curator",
            "SUPERADMIN":       "superadmin",
            "REGIONAL_MANAGER": "manager",
            "FINANCE_MANAGER":  "finance_manager",
            "OUTPOST_MANAGER":  "manager",
            "HEAD_ROASTER":     "head_roaster",
            "SENIOR_BARISTA":   "senior_barista",
            "BARISTA":          "barista",
            "CASHIER":          "cashier",
            "WAREHOUSE_STAFF":  "warehouse_staff",
            "FINANCE_STAFF":    "finance_staff",
            "EXPEDITION_GUIDE": "expedition_guide",
        }
        legacy_role = legacy_role_map.get(u["_role_code"], "staff")

        profile_rows.append({
            "user_id":              uid,
            "location_id":          loc_id,
            "default_location_id":  loc_id,
            "is_active":            True,
            "role":                 legacy_role,
        })

    preview("lumra_config_userprofile", profile_rows)
    if not DRY_RUN:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'lumra_config_userprofile'
            """
        )
        profile_columns = {row[0] for row in cur.fetchall()}
        has_default_location = "default_location_id" in profile_columns

        for row in profile_rows:
            if has_default_location:
                cur.execute(
                    "INSERT INTO lumra_config_userprofile "
                    "(user_id, location_id, default_location_id, is_active, role) "
                    "VALUES (%s,%s,%s,%s,%s) "
                    "ON CONFLICT (user_id) DO UPDATE SET "
                    "location_id=EXCLUDED.location_id, "
                    "default_location_id=EXCLUDED.default_location_id, "
                    "is_active=EXCLUDED.is_active, "
                    "role=EXCLUDED.role",
                    list(row.values())
                )
            else:
                cur.execute(
                    "INSERT INTO lumra_config_userprofile "
                    "(user_id, location_id, is_active, role) "
                    "VALUES (%s,%s,%s,%s) "
                    "ON CONFLICT (user_id) DO UPDATE SET "
                    "location_id=EXCLUDED.location_id, "
                    "is_active=EXCLUDED.is_active, "
                    "role=EXCLUDED.role",
                    (
                        row["user_id"],
                        row["location_id"],
                        row["is_active"],
                        row["role"],
                    )
                )
        conn.commit()
        print(f"\n  ✓ lumra_config_userprofile: {len(profile_rows)} profil diinsert/diupdate")
        cur.close()
        conn.close()
    else:
        print(f"\n  ✓ [DRY RUN] {len(profile_rows)} userprofile rows akan diinsert")

    # ═════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═════════════════════════════════════════════════════════════════
    # Hitung distribusi per role
    role_dist = {}
    for u in all_user_meta:
        rc = u["_role_code"]
        role_dist[rc] = role_dist.get(rc, 0) + 1

    # Hitung distribusi per phase
    phase_dist = {}
    for u in all_user_meta:
        for (no, name, area, otype, phase) in OUTPOSTS:
            if no == u["_outpost_no"]:
                phase_dist[phase] = phase_dist.get(phase, 0) + 1
                break

    total_users = len(auth_user_rows)
    total_perms = len(perm_rows)

    print(f"\n{'═'*68}")
    print(f"  RINGKASAN TAHAP 2")
    print(f"{'─'*68}")
    print(f"  system_roles             : {len(ROLES)} roles")
    print(f"  system_role_permissions  : {total_perms} permission rows ({len(MODULES)} modul × {len(ROLES)} roles)")
    print(f"  auth_user                : {total_users} users total")
    print(f"  system_user_roles        : {len(user_role_rows)} mapping")
    print(f"  lumra_config_userprofile : {len(profile_rows)} profil")
    print(f"{'─'*68}")
    print(f"  DISTRIBUSI USER PER ROLE:")
    for rc, cnt in sorted(role_dist.items(), key=lambda x: -x[1]):
        bar = "█" * min(cnt, 30)
        print(f"    {rc:<25} {cnt:>4}  {bar}")
    print(f"{'─'*68}")
    print(f"  DISTRIBUSI USER PER PHASE:")
    for phase, cnt in sorted(phase_dist.items(), key=lambda x: -x[1]):
        print(f"    {phase:<25} {cnt:>4} users")
    print(f"{'─'*68}")
    print(f"  Password default: {DEFAULT_PASSWORD_PLAIN}")
    print(f"  ⚠  Segera ganti password semua user setelah seed!")
    if DRY_RUN:
        print(f"\n  ⚠  Dry run selesai. Tidak ada data yang disimpan.")
    else:
        print(f"\n  ✓ Semua data Tahap 2 berhasil disimpan ke database.")
    print("═" * 68 + "\n")


if __name__ == "__main__":
    run()
