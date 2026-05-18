"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  KAFE NUSANTARA — MASTER SEEDER v1.0                                       ║
║  Management Command: seed_nusantara                                         ║
║                                                                              ║
║  Handles:                                                                    ║
║  · Master data  : taxes, units, categories, vendors, locations              ║
║  · Menu kafe    : 55 produk, ~130 variant (Starbucks/Kenangan style)        ║
║  · Kopi 9,999   : 7.463 House Blend + 2.536 Single Origin                  ║
║  · Production   : recipes + ingredients per produk                          ║
║  · Customers    : 5.000 dummy customers dengan tier                         ║
║  · Staff        : manager, barista, kasir per outpost                       ║
║                                                                              ║
║  Usage:                                                                      ║
║    python manage.py seed_nusantara                    # full seed           ║
║    python manage.py seed_nusantara --clear            # clear then seed     ║
║    python manage.py seed_nusantara --only master      # only master data    ║
║    python manage.py seed_nusantara --only menu        # only cafe menu      ║
║    python manage.py seed_nusantara --only kopi        # only 9999 kopi      ║
║    python manage.py seed_nusantara --only customers   # only customers      ║
║    python manage.py seed_nusantara --only staff       # only staff          ║
║    python manage.py seed_nusantara --json kopi_9999_db.json                ║
║    python manage.py seed_nusantara --batch-size 500   # custom batch        ║
║    python manage.py seed_nusantara --dry-run          # preview only        ║
║                                                                              ║
║  Requirements:                                                               ║
║    pip install psycopg2-binary tqdm                                         ║
║                                                                              ║
║  File placement:                                                             ║
║    yourapp/management/commands/seed_nusantara.py                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import random
from decimal import Decimal as D
from datetime import timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

User = get_user_model()

# ─── safe imports (tqdm optional) ─────────────────────────────────────────────
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# ─── model imports ─────────────────────────────────────────────────────────────
# Sesuaikan import path dengan struktur app kamu
try:
    from lumra_config.models import (
        Category  as CategoryModel,
        Tax       as TaxModel,
        Unit      as UnitModel,
        Vendor    as VendorModel,
        Location  as LocationModel,
        Product   as ProductModel,
        ProductVariant as ProductVariantModel,
        Customer  as CustomerModel,
        UserProfile,
    )
    # Model atribut di project ini bernama ProductAttribute
    try:
        from lumra_config.models import ProductAttribute as ProductAttributeItem
        HAS_ATTR = True
    except ImportError:
        HAS_ATTR = False
        ProductAttributeItem = None

    # Role — optional
    try:
        from lumra_config.models import Role
        HAS_ROLE = True
    except ImportError:
        HAS_ROLE = False
        Role = None

except ImportError as e:
    raise CommandError(
        f"Import error: {e}\n"
        "Pastikan nama model di lumra_config.models sesuai.\n"
        "Cek: Category, Tax, Unit, Vendor, Location, Product, ProductVariant, Customer"
    )

try:
    from production.models import (
        RecipeCategory as RecipeCategoryModel,
        Recipe         as RecipeModel,
        RecipeIngredient as RecipeIngredientModel,
    )
    HAS_PRODUCTION = True
except ImportError:
    HAS_PRODUCTION = False
    RecipeCategoryModel = RecipeModel = RecipeIngredientModel = None

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MASTER DATA DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

TAXES_DATA = [
    {"name": "PPN 11%",    "rate": D("11.00"), "description": "Pajak Pertambahan Nilai 11%", "is_active": True},
    {"name": "PPN 0%",     "rate": D("0.00"),  "description": "Bebas PPN (kebutuhan pokok)", "is_active": True},
    {"name": "Service 5%", "rate": D("5.00"),  "description": "Service charge 5%",            "is_active": True},
]

UNITS_DATA = [
    {"name": "Gram",       "symbol": "g",   "description": "Satuan berat kopi biji/bubuk",    "is_active": True},
    {"name": "Kilogram",   "symbol": "kg",  "description": "Satuan berat bulk",                "is_active": True},
    {"name": "Mililiter",  "symbol": "ml",  "description": "Satuan volume minuman",            "is_active": True},
    {"name": "Liter",      "symbol": "L",   "description": "Satuan volume bahan baku",         "is_active": True},
    {"name": "Pcs",        "symbol": "pcs", "description": "Satuan per item",                  "is_active": True},
    {"name": "Sachet",     "symbol": "sct", "description": "Satuan sachet/bungkus kecil",      "is_active": True},
    {"name": "Botol",      "symbol": "btl", "description": "Satuan botol",                     "is_active": True},
    {"name": "Karton",     "symbol": "ktn", "description": "Satuan karton/dus",                "is_active": True},
]

CATEGORIES_DATA = [
    # Parent categories
    {"name": "Minuman Kopi",        "slug": "minuman-kopi",       "code": "MK",  "description": "Semua produk minuman berbasis kopi",        "is_active": True, "parent": None},
    {"name": "Minuman Non-Kopi",    "slug": "minuman-non-kopi",   "code": "MNK", "description": "Minuman tanpa kopi",                         "is_active": True, "parent": None},
    {"name": "Makanan",             "slug": "makanan",            "code": "MKN", "description": "Pastry, dessert, dan savory food",           "is_active": True, "parent": None},
    {"name": "Kopi Retail",         "slug": "kopi-retail",        "code": "KR",  "description": "Kopi biji dan bubuk untuk dibawa pulang",    "is_active": True, "parent": None},
    {"name": "Merchandise",         "slug": "merchandise",        "code": "MRC", "description": "Produk merchandise Kafe Nusantara",         "is_active": True, "parent": None},
    {"name": "Bahan Baku",          "slug": "bahan-baku",         "code": "BB",  "description": "Raw materials untuk produksi",               "is_active": True, "parent": None},
    # Child categories — Minuman Kopi
    {"name": "Signature Coffee",    "slug": "signature-coffee",   "code": "SIG", "description": "Kopi susu dan signature drinks Nusantara",   "is_active": True, "parent": "Minuman Kopi"},
    {"name": "Espresso Based",      "slug": "espresso-based",     "code": "ESP", "description": "Minuman berbasis espresso shot",              "is_active": True, "parent": "Minuman Kopi"},
    {"name": "Iced Coffee",         "slug": "iced-coffee",        "code": "ICE", "description": "Kopi dingin dan cold brew",                   "is_active": True, "parent": "Minuman Kopi"},
    {"name": "Manual Brew",         "slug": "manual-brew",        "code": "MBW", "description": "V60, French Press, AeroPress",                "is_active": True, "parent": "Minuman Kopi"},
    {"name": "House Blend",         "slug": "house-blend",        "code": "HB",  "description": "Blend campuran eksklusif Kafe Nusantara",    "is_active": True, "parent": "Kopi Retail"},
    {"name": "Single Origin",       "slug": "single-origin",      "code": "SO",  "description": "Single origin coffee dari seluruh Nusantara","is_active": True, "parent": "Kopi Retail"},
    # Child categories — Makanan
    {"name": "Pastry",              "slug": "pastry",             "code": "PST", "description": "Croissant, muffin, danish",                   "is_active": True, "parent": "Makanan"},
    {"name": "Dessert",             "slug": "dessert",            "code": "DST", "description": "Cake, gelato, pudding",                       "is_active": True, "parent": "Makanan"},
    {"name": "Savory",              "slug": "savory",             "code": "SAV", "description": "Sandwich, salad, nasi",                       "is_active": True, "parent": "Makanan"},
    # Child categories — Non Coffee
    {"name": "Tea & Others",        "slug": "tea-others",         "code": "TEA", "description": "Teh, coklat, juice",                          "is_active": True, "parent": "Minuman Non-Kopi"},
]

VENDORS_DATA = [
    # Supplier Kopi
    {"name": "PT Toraja Sulawesi Coffee",  "code": "TOR-SUL", "contact_person": "Pak Budi Santoso",  "phone": "0812-3456-7001", "email": "budi@torajacoffee.id",    "address": "Jl. Poros Makassar-Toraja No.1, Toraja Utara",    "tax_number": "01.234.567.8-901.000", "website": "https://torajacoffee.id"},
    {"name": "CV Gayo Highland Farm",      "code": "GAY-HLD", "contact_person": "Ibu Ratna Dewi",    "phone": "0812-3456-7002", "email": "ratna@gayofarm.id",        "address": "Jl. Takengon-Bebesen No.22, Aceh Tengah",         "tax_number": "02.345.678.9-012.000", "website": "https://gayofarm.id"},
    {"name": "PT Java Preanger Estate",    "code": "JPE-EST", "contact_person": "Pak Hendra Wijaya", "phone": "0812-3456-7003", "email": "hendra@preanger.id",      "address": "Jl. Pengalengan No.88, Bandung Selatan",          "tax_number": "03.456.789.0-123.000", "website": "https://preanger.id"},
    {"name": "PT Mandailing Coffee Co",    "code": "MDL-COF", "contact_person": "Pak Surya Rahman",  "phone": "0812-3456-7004", "email": "surya@mandailing.id",     "address": "Jl. Panyabungan No.77, Mandailing Natal",         "tax_number": "04.567.890.1-234.000", "website": "https://mandailingcoffee.id"},
    {"name": "CV Kintamani Bali Estate",   "code": "KIN-BAL", "contact_person": "Pak Wayan Dharma",  "phone": "0812-3456-7005", "email": "wayan@kintamanicoffee.id","address": "Jl. Kintamani-Bangli No.15, Bangli, Bali",        "tax_number": "05.678.901.2-345.000", "website": "https://kintamanicoffee.id"},
    {"name": "PT Papua Highland Coffee",   "code": "PAP-HLD", "contact_person": "Pak Filemon Waromi","phone": "0812-3456-7006", "email": "filemon@papuacoffee.id",  "address": "Jl. Wamena-Jayawijaya No.3, Wamena",             "tax_number": "06.789.012.3-456.000", "website": "https://papuahighland.id"},
    # Supplier Non-Kopi
    {"name": "CV Fresh Dairy Indonesia",   "code": "FRS-DRY", "contact_person": "Ibu Maya Putri",   "phone": "0812-3456-7007", "email": "maya@freshdairy.id",      "address": "Jl. Lembang No.55, Bandung Barat",               "tax_number": "07.890.123.4-567.000", "website": "https://freshdairy.id"},
    {"name": "PT Indo Food Supply",        "code": "IFS-SUP", "contact_person": "Pak Doni Kusuma",  "phone": "0812-3456-7008", "email": "doni@indofoodsupply.id",  "address": "Jl. Raya Bogor Km.45, Bekasi",                   "tax_number": "08.901.234.5-678.000", "website": "https://indofoodsupply.id"},
    {"name": "CV Sugar & Syrup Nusantara", "code": "SSN-SYR", "contact_person": "Pak Andi Hartono", "phone": "0812-3456-7009", "email": "andi@sugarsyrup.id",      "address": "Jl. Industri No.12, Karawang",                   "tax_number": "09.012.345.6-789.000", "website": "https://sugarsyrup.id"},
    {"name": "CV Gula Aren Nusantara",     "code": "GAN-ARE", "contact_person": "Pak Wahyu Setiawan","phone": "0812-3456-7010","email": "wahyu@gulaaren.id",       "address": "Jl. Pangandaran No.8, Ciamis",                   "tax_number": "10.123.456.7-890.000", "website": "https://gulaaren.id"},
    {"name": "PT UHT Milk Indonesia",      "code": "UHT-MLK", "contact_person": "Ibu Sari Indah",   "phone": "0812-3456-7011", "email": "sari@uhtmilk.id",         "address": "Jl. Raya Sentul No.33, Bogor",                   "tax_number": "11.234.567.8-901.000", "website": "https://uhtmilk.id"},
    {"name": "PT Packaging Solutions",     "code": "PKG-SOL", "contact_person": "Pak Rianto",        "phone": "0812-3456-7012", "email": "rianto@packagingsol.id",  "address": "Jl. Cibinong Industrial Park No.7, Bogor",       "tax_number": "12.345.678.9-012.000", "website": "https://packagingsol.id"},
]

LOCATIONS_DATA = [
    # Phase 1 — Jawa (sesuai world building outpost)
    {"name": "Outpost 01: The Batavia Loghouse",      "address": "Kota Tua, Jakarta Barat",             "location_type": "store",     "code": "OP-01"},
    {"name": "Outpost 02: The Priangan Counting House","address": "Jl. Braga No.12, Bandung",           "location_type": "store",     "code": "OP-02"},
    {"name": "Outpost 03: The Preanger Hillpost",      "address": "Jl. Dago Atas No.88, Bandung",      "location_type": "store",     "code": "OP-03"},
    {"name": "Outpost 04: The Ciliwung Depot",         "address": "Jl. Menteng Raya No.22, Jakarta",   "location_type": "store",     "code": "OP-04"},
    {"name": "Outpost 05: The Glass Meridian",         "address": "SCBD, Jl. Jend. Sudirman, Jakarta", "location_type": "store",     "code": "OP-05"},
    {"name": "Outpost 06: The Kemang Waystation",      "address": "Jl. Kemang Raya No.45, Jakarta",    "location_type": "store",     "code": "OP-06"},
    {"name": "Outpost 07: The Cikini Reading Room",    "address": "Jl. Cikini Raya No.77, Jakarta",    "location_type": "store",     "code": "OP-07"},
    {"name": "Outpost 08: The Kelapa Gading Anchorage","address": "Jl. Kelapa Gading Bvd No.5, Jakarta","location_type": "store",    "code": "OP-08"},
    {"name": "Outpost 09: The Serpong Survey Camp",    "address": "BSD City, Tangerang Selatan",        "location_type": "store",     "code": "OP-09"},
    {"name": "Outpost 10: The Depok Crossroads",       "address": "Jl. Margonda Raya No.200, Depok",   "location_type": "store",     "code": "OP-10"},
    {"name": "Outpost 11: The Bogor Botanical Gate",   "address": "Jl. Suryakencana No.33, Bogor",     "location_type": "store",     "code": "OP-11"},
    {"name": "Outpost 14: The Semarang Customs House", "address": "Kota Lama, Semarang",               "location_type": "store",     "code": "OP-14"},
    {"name": "Outpost 15: The Solo Kepatihan Shelter", "address": "Jl. Laweyan No.11, Solo",           "location_type": "store",     "code": "OP-15"},
    {"name": "Outpost 16: The Yogyakarta Elevation Post","address": "Jl. Prawirotaman No.55, Yogyakarta","location_type": "store",   "code": "OP-16"},
    {"name": "Outpost 17: The Surabaya Iron Wharf",   "address": "Jl. Tunjungan No.56, Surabaya",      "location_type": "store",     "code": "OP-17"},
    {"name": "Outpost 18: The Malang Highland Camp",  "address": "Jl. Kayutangan No.88, Malang",       "location_type": "store",     "code": "OP-18"},
    # Phase 2 — Sumatera
    {"name": "Outpost 23: The Aceh Gateway",           "address": "Jl. Peunayong, Banda Aceh",         "location_type": "store",     "code": "OP-23"},
    {"name": "Outpost 24: The Medan Trade Post",       "address": "Jl. Kesawan No.22, Medan",          "location_type": "store",     "code": "OP-24"},
    {"name": "Outpost 25: The Gayo Highlands Shelter", "address": "Jl. Takengon, Aceh Tengah",         "location_type": "store",     "code": "OP-25"},
    {"name": "Outpost 26: The Padang Spice Harbor",    "address": "Jl. Kota Lama, Padang",             "location_type": "store",     "code": "OP-26"},
    # Phase 3 — Bali & Timur
    {"name": "Outpost 30: The Kintamani Crater Post",  "address": "Kintamani, Bangli, Bali",           "location_type": "store",     "code": "OP-30"},
    {"name": "Outpost 31: The Denpasar Island Hub",    "address": "Jl. Seminyak, Bali",                "location_type": "store",     "code": "OP-31"},
    {"name": "Outpost 32: The Makassar Fortpost",      "address": "Jl. Losari, Makassar",              "location_type": "store",     "code": "OP-32"},
    {"name": "Outpost 33: The Toraja Forest Shelter",  "address": "Jl. Rantepao, Toraja Utara",        "location_type": "store",     "code": "OP-33"},
    {"name": "Outpost 35: The Eastern Terminus",       "address": "Jl. Jayapura, Papua",               "location_type": "store",     "code": "OP-35"},
    # Operational
    {"name": "Outpost 22: The Final Meridian",         "address": "Roastery Utama, Jakarta Selatan",   "location_type": "roastery",  "code": "OP-22"},
    {"name": "Lumra Warehouse — Cikarang",             "address": "Jl. Industri No.22, Cikarang",      "location_type": "warehouse", "code": "WH-CKR"},
    {"name": "Lumra Cold Storage — Depok",             "address": "Jl. Raya Bogor Km.32, Depok",       "location_type": "warehouse", "code": "WH-DPK"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — MENU KAFE (55 produk, ~130 variant)
# ═══════════════════════════════════════════════════════════════════════════════

MENU_PRODUCTS = [
    # ── SIGNATURE COFFEE ──────────────────────────────────────────────────────
    {
        "name": "Kopi Susu Lumra", "code": "KS-LUM", "category": "Signature Coffee",
        "description": "Signature kopi susu dengan gula aren asli. Espresso medium roast, fresh milk, gula aren Ciamis. Creamy, manis pas, kopi nendang — identitas Kafe Nusantara.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "KS-LUM-S",  "size_weight": "Small 250ml",   "price_buy": 8_000,  "price_sell": 22_000},
            {"sku": "KS-LUM-R",  "size_weight": "Regular 350ml", "price_buy": 10_000, "price_sell": 27_000},
            {"sku": "KS-LUM-L",  "size_weight": "Large 470ml",   "price_buy": 12_000, "price_sell": 32_000},
        ],
    },
    {
        "name": "Kopi Gula Aren Premium", "code": "KS-GA", "category": "Signature Coffee",
        "description": "Double shot espresso + fresh milk + gula aren premium Ciamis. Manis alami dari tanah Nusantara.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "KS-GA-S",   "size_weight": "Small 250ml",   "price_buy": 9_000,  "price_sell": 24_000},
            {"sku": "KS-GA-R",   "size_weight": "Regular 350ml", "price_buy": 11_000, "price_sell": 29_000},
            {"sku": "KS-GA-L",   "size_weight": "Large 470ml",   "price_buy": 13_000, "price_sell": 34_000},
        ],
    },
    {
        "name": "Kopi Susu Pandan", "code": "KS-PDN", "category": "Signature Coffee",
        "description": "Kopi susu dengan essence pandan asli dari daun segar. Aromatik, creamy, dan unik. Paduan Nusantara yang tidak ada duanya.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "KS-PDN-S",  "size_weight": "Small 250ml",   "price_buy": 9_000,  "price_sell": 25_000},
            {"sku": "KS-PDN-R",  "size_weight": "Regular 350ml", "price_buy": 11_000, "price_sell": 30_000},
            {"sku": "KS-PDN-L",  "size_weight": "Large 470ml",   "price_buy": 13_000, "price_sell": 35_000},
        ],
    },
    {
        "name": "Kopi Susu Kelapa", "code": "KS-KLP", "category": "Signature Coffee",
        "description": "Espresso + santan segar + sedikit gula aren. Creamy tropical vibe — kopi dan kelapa muda Indonesia.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "KS-KLP-R",  "size_weight": "Regular 350ml", "price_buy": 11_000, "price_sell": 28_000},
            {"sku": "KS-KLP-L",  "size_weight": "Large 470ml",   "price_buy": 13_000, "price_sell": 33_000},
        ],
    },
    {
        "name": "Es Kopi Kental Manis", "code": "EKKM", "category": "Signature Coffee",
        "description": "Es kopi kental manis klasik Indonesia. Robusta bold + kental manis + es batu. Kenangan masa kecil dalam satu gelas.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "EKKM-R",    "size_weight": "Regular 300ml", "price_buy": 7_000,  "price_sell": 20_000},
            {"sku": "EKKM-L",    "size_weight": "Large 400ml",   "price_buy": 9_000,  "price_sell": 25_000},
        ],
    },
    {
        "name": "Matcha Latte", "code": "ML-STD", "category": "Signature Coffee",
        "description": "Ceremonial grade matcha Uji, Kyoto + fresh whole milk. Earthy, creamy, dan sedikit bitter yang menyeimbangkan.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "ML-S",      "size_weight": "Small 250ml",   "price_buy": 12_000, "price_sell": 30_000},
            {"sku": "ML-R",      "size_weight": "Regular 350ml", "price_buy": 15_000, "price_sell": 35_000},
            {"sku": "ML-L",      "size_weight": "Large 470ml",   "price_buy": 18_000, "price_sell": 40_000},
        ],
    },
    {
        "name": "Chocolate Sensation", "code": "CHC-SEN", "category": "Signature Coffee",
        "description": "Belgian dark chocolate 70% + single shot espresso + steamed milk + whipped cream. Rich, bold, dan satisfying.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "CHC-S",     "size_weight": "Small 250ml",   "price_buy": 11_000, "price_sell": 30_000},
            {"sku": "CHC-R",     "size_weight": "Regular 350ml", "price_buy": 14_000, "price_sell": 35_000},
            {"sku": "CHC-L",     "size_weight": "Large 470ml",   "price_buy": 17_000, "price_sell": 40_000},
        ],
    },
    {
        "name": "Taro Latte", "code": "TR-LAT", "category": "Signature Coffee",
        "description": "Taro root natural + fresh milk. Purple vibes, creamy, dan subtly sweet.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "TR-R",      "size_weight": "Regular 350ml", "price_buy": 12_000, "price_sell": 32_000},
            {"sku": "TR-L",      "size_weight": "Large 470ml",   "price_buy": 15_000, "price_sell": 37_000},
        ],
    },
    # ── ESPRESSO BASED ─────────────────────────────────────────────────────────
    {
        "name": "Espresso", "code": "ESP", "category": "Espresso Based",
        "description": "Single/Double shot espresso dari House Blend signature. 25-30 detik ekstraksi, 93°C. Bold, concentrated, dengan crema sempurna.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "ESP-SGL",   "size_weight": "Single 30ml",   "price_buy": 5_000,  "price_sell": 22_000},
            {"sku": "ESP-DBL",   "size_weight": "Double 60ml",   "price_buy": 8_000,  "price_sell": 28_000},
            {"sku": "ESP-RST",   "size_weight": "Ristretto 25ml","price_buy": 5_000,  "price_sell": 25_000},
        ],
    },
    {
        "name": "Americano", "code": "AME", "category": "Espresso Based",
        "description": "Double espresso + hot water. Clean, bold, dan aromatic. Cara terbaik menikmati karakter kopi tanpa dairy.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "AME-S",     "size_weight": "Small 240ml",   "price_buy": 6_000,  "price_sell": 24_000},
            {"sku": "AME-R",     "size_weight": "Regular 350ml", "price_buy": 7_000,  "price_sell": 28_000},
            {"sku": "AME-L",     "size_weight": "Large 470ml",   "price_buy": 8_000,  "price_sell": 32_000},
        ],
    },
    {
        "name": "Cappuccino", "code": "CAP", "category": "Espresso Based",
        "description": "Double espresso + steamed milk + microfoam tebal. 1:1:1 ratio klasik. Untuk yang menghargai tradisi.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "CAP-S",     "size_weight": "Small 200ml",   "price_buy": 9_000,  "price_sell": 28_000},
            {"sku": "CAP-R",     "size_weight": "Regular 280ml", "price_buy": 11_000, "price_sell": 33_000},
            {"sku": "CAP-L",     "size_weight": "Large 360ml",   "price_buy": 13_000, "price_sell": 38_000},
        ],
    },
    {
        "name": "Caffe Latte", "code": "LAT", "category": "Espresso Based",
        "description": "Double espresso + steamed whole milk + thin microfoam. Smooth, creamy, dan balanced. Canvas sempurna untuk latte art.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "LAT-S",     "size_weight": "Small 250ml",   "price_buy": 10_000, "price_sell": 30_000},
            {"sku": "LAT-R",     "size_weight": "Regular 350ml", "price_buy": 12_000, "price_sell": 35_000},
            {"sku": "LAT-L",     "size_weight": "Large 470ml",   "price_buy": 15_000, "price_sell": 40_000},
        ],
    },
    {
        "name": "Flat White", "code": "FW", "category": "Espresso Based",
        "description": "Double ristretto + 120ml microfoam padat. Lebih kecil dari latte, lebih intens. Velvety dan robust.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "FW-R",      "size_weight": "Regular 250ml", "price_buy": 12_000, "price_sell": 33_000},
            {"sku": "FW-L",      "size_weight": "Large 350ml",   "price_buy": 15_000, "price_sell": 38_000},
        ],
    },
    {
        "name": "Caramel Macchiato", "code": "CRM", "category": "Espresso Based",
        "description": "Vanilla syrup + steamed milk + double espresso dituang di atas + caramel drizzle. Layered beauty.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "CRM-S",     "size_weight": "Small 250ml",   "price_buy": 14_000, "price_sell": 36_000},
            {"sku": "CRM-R",     "size_weight": "Regular 350ml", "price_buy": 16_000, "price_sell": 41_000},
            {"sku": "CRM-L",     "size_weight": "Large 470ml",   "price_buy": 19_000, "price_sell": 46_000},
        ],
    },
    {
        "name": "Affogato", "code": "AFO", "category": "Espresso Based",
        "description": "Hot double espresso shot dituang langsung di atas vanilla gelato artisan. Hot meets cold. Sempre classico.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "AFO-1",     "size_weight": "1 Scoop 200ml", "price_buy": 15_000, "price_sell": 38_000},
            {"sku": "AFO-2",     "size_weight": "2 Scoop 250ml", "price_buy": 22_000, "price_sell": 48_000},
        ],
    },
    # ── ICED COFFEE ────────────────────────────────────────────────────────────
    {
        "name": "Iced Americano", "code": "I-AME", "category": "Iced Coffee",
        "description": "Double espresso + cold water + ice cube. Refreshing dan bold. First Light terbaik untuk hari-hari panas.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "I-AME-R",   "size_weight": "Regular 300ml", "price_buy": 8_000,  "price_sell": 28_000},
            {"sku": "I-AME-L",   "size_weight": "Large 400ml",   "price_buy": 10_000, "price_sell": 33_000},
        ],
    },
    {
        "name": "Iced Latte", "code": "I-LAT", "category": "Iced Coffee",
        "description": "Double espresso + cold milk + ice. Smooth dan creamy meski dingin. Versatile sepanjang hari.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "I-LAT-R",   "size_weight": "Regular 300ml", "price_buy": 11_000, "price_sell": 33_000},
            {"sku": "I-LAT-L",   "size_weight": "Large 400ml",   "price_buy": 13_000, "price_sell": 38_000},
        ],
    },
    {
        "name": "Cold Brew", "code": "CB", "category": "Iced Coffee",
        "description": "18-hour cold steep dari single origin pilihan. Smooth, low acidity, naturally sweet. Tanpa panas, tanpa terburu-buru.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "CB-R",      "size_weight": "Regular 250ml", "price_buy": 10_000, "price_sell": 32_000},
            {"sku": "CB-L",      "size_weight": "Large 400ml",   "price_buy": 14_000, "price_sell": 40_000},
        ],
    },
    {
        "name": "Cold Brew Gula Aren", "code": "CB-GA", "category": "Iced Coffee",
        "description": "Cold brew 18 jam + gula aren asli Ciamis. Best seller The Open Horizon season. Smooth cold brew meets Indonesian sweetness.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "CB-GA-R",   "size_weight": "Regular 300ml", "price_buy": 12_000, "price_sell": 35_000},
            {"sku": "CB-GA-L",   "size_weight": "Large 400ml",   "price_buy": 15_000, "price_sell": 42_000},
        ],
    },
    {
        "name": "Espresso Tonic", "code": "ESP-TON", "category": "Iced Coffee",
        "description": "Double ristretto dituang perlahan di atas tonic water + ice. Crisp, juicy, dan kompleks. The Open Horizon dalam satu gelas.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "ESP-TON-R", "size_weight": "Regular 300ml", "price_buy": 14_000, "price_sell": 38_000},
            {"sku": "ESP-TON-L", "size_weight": "Large 400ml",   "price_buy": 17_000, "price_sell": 45_000},
        ],
    },
    # ── MANUAL BREW ────────────────────────────────────────────────────────────
    {
        "name": "V60 Single Origin", "code": "V60", "category": "Manual Brew",
        "description": "V60 pour over dari single origin pilihan barista hari ini. 15g kopi, 250ml air, 90-93°C. Setiap cangkir adalah perjalanan ke origin-nya.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "V60-TOR",   "size_weight": "Toraja 250ml",     "price_buy": 12_000, "price_sell": 38_000},
            {"sku": "V60-GAY",   "size_weight": "Gayo 250ml",       "price_buy": 14_000, "price_sell": 42_000},
            {"sku": "V60-JAV",   "size_weight": "Java 250ml",       "price_buy": 13_000, "price_sell": 40_000},
            {"sku": "V60-KIN",   "size_weight": "Kintamani 250ml",  "price_buy": 13_000, "price_sell": 40_000},
            {"sku": "V60-PAP",   "size_weight": "Papua 250ml",      "price_buy": 16_000, "price_sell": 48_000},
        ],
    },
    {
        "name": "French Press", "code": "FP", "category": "Manual Brew",
        "description": "Full immersion brew 4 menit. Rich body, bold, dan oily. Untuk yang menyukai kopi dengan karakter penuh.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "FP-1",      "size_weight": "1 cup 350ml",   "price_buy": 10_000, "price_sell": 35_000},
            {"sku": "FP-2",      "size_weight": "2 cups 600ml",  "price_buy": 16_000, "price_sell": 55_000},
        ],
    },
    {
        "name": "AeroPress", "code": "AP", "category": "Manual Brew",
        "description": "AeroPress full recipe 15g + 200ml + 85°C. Clean cup, versatile, dan low acidity. Cara tercepat mendapat kopi berkualitas.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "AP-1",      "size_weight": "1 cup 250ml",   "price_buy": 10_000, "price_sell": 35_000},
        ],
    },
    {
        "name": "Kopi Tubruk Nusantara", "code": "KT-NUS", "category": "Manual Brew",
        "description": "Kopi tubruk tradisional Indonesia. Robusta Lampung pilihan, digiling kasar, diseduh langsung. Sederhana, jujur, dan autentik.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "KT-1",      "size_weight": "1 cup 250ml",   "price_buy": 5_000,  "price_sell": 18_000},
        ],
    },
    # ── NON COFFEE ─────────────────────────────────────────────────────────────
    {
        "name": "Hot Chocolate", "code": "HCHOC", "category": "Tea & Others",
        "description": "Belgian dark chocolate 70% + steamed whole milk. Rich, velvety, dan tidak terlalu manis. Untuk hari-hari yang butuh kehangatan.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "HCHOC-S",   "size_weight": "Small 250ml",   "price_buy": 10_000, "price_sell": 30_000},
            {"sku": "HCHOC-R",   "size_weight": "Regular 350ml", "price_buy": 13_000, "price_sell": 35_000},
            {"sku": "HCHOC-L",   "size_weight": "Large 470ml",   "price_buy": 16_000, "price_sell": 40_000},
        ],
    },
    {
        "name": "Teh Tarik Nusantara", "code": "TTRK", "category": "Tea & Others",
        "description": "Teh tarik ala mamak dengan teh hitam Ceylon + susu kental manis. Frothy dan creamy dari tradisi Melayu.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": False, "track_batch": False,
        "min_stock": 0, "max_stock": 9999,
        "variants": [
            {"sku": "TTRK-R",    "size_weight": "Regular 300ml", "price_buy": 6_000,  "price_sell": 22_000},
            {"sku": "TTRK-L",    "size_weight": "Large 400ml",   "price_buy": 8_000,  "price_sell": 27_000},
        ],
    },
    {
        "name": "Mineral Water", "code": "WATER", "category": "Tea & Others",
        "description": "Mineral water botol 600ml.",
        "unit": "Pcs", "tax": "PPN 0%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": True,
        "min_stock": 24, "max_stock": 240,
        "variants": [
            {"sku": "WATER-600", "size_weight": "600ml",         "price_buy": 2_500,  "price_sell": 8_000},
        ],
    },
    # ── PASTRY ─────────────────────────────────────────────────────────────────
    {
        "name": "Croissant Butter", "code": "P-CRS", "category": "Pastry",
        "description": "Classic French butter croissant. Flakey, golden, dan buttery. Dibuat fresh setiap pagi dari butter premium Eropa.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 5, "max_stock": 50,
        "variants": [
            {"sku": "P-CRS-1",   "size_weight": "1 pcs",         "price_buy": 10_000, "price_sell": 28_000},
        ],
    },
    {
        "name": "Croissant Chocolate", "code": "P-CRS-CHC", "category": "Pastry",
        "description": "Pain au chocolat dengan dark chocolate Valrhona 64%. Buttery pastry meets premium chocolate.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 5, "max_stock": 50,
        "variants": [
            {"sku": "P-CRS-CHC-1","size_weight": "1 pcs",        "price_buy": 12_000, "price_sell": 32_000},
        ],
    },
    {
        "name": "Banana Bread", "code": "P-BB", "category": "Pastry",
        "description": "Homemade banana bread dengan walnut. Moist, dense, dan penuh rasa pisang matang. Comfort food terbaik Twilight Bivouac.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 5, "max_stock": 30,
        "variants": [
            {"sku": "P-BB-1",    "size_weight": "1 slice",        "price_buy": 10_000, "price_sell": 28_000},
            {"sku": "P-BB-FULL", "size_weight": "Whole loaf",     "price_buy": 55_000, "price_sell": 125_000},
        ],
    },
    {
        "name": "Brownies Dark Choco", "code": "P-BRW", "category": "Pastry",
        "description": "Fudgy brownies Belgian dark chocolate 70%. Dense, chewy di tengah, crispy di luar. Recommended dessert untuk hampir semua blend.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 5, "max_stock": 50,
        "variants": [
            {"sku": "P-BRW-1",   "size_weight": "1 pcs",          "price_buy": 8_000,  "price_sell": 25_000},
        ],
    },
    {
        "name": "Cinnamon Roll", "code": "P-CIN", "category": "Pastry",
        "description": "Soft cinnamon roll dengan cream cheese glaze. Warm, spiced, dan indulgent. Pairing sempurna untuk Autumn blend.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 5, "max_stock": 30,
        "variants": [
            {"sku": "P-CIN-1",   "size_weight": "1 pcs",          "price_buy": 12_000, "price_sell": 32_000},
        ],
    },
    # ── DESSERT ────────────────────────────────────────────────────────────────
    {
        "name": "Tiramisu", "code": "D-TRM", "category": "Dessert",
        "description": "Classic Italian tiramisu dengan ladyfinger direndam espresso shot, mascarpone cream, dan cocoa powder. Al perfetto.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 3, "max_stock": 20,
        "variants": [
            {"sku": "D-TRM-1",   "size_weight": "1 portion",      "price_buy": 16_000, "price_sell": 42_000},
        ],
    },
    {
        "name": "Chocolate Lava Cake", "code": "D-CLC", "category": "Dessert",
        "description": "Warm dark chocolate lava cake. Molten center mengalir saat dipotong. Disajikan dengan vanilla gelato. Recommended untuk semua T3 Grand Artifact.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 3, "max_stock": 20,
        "variants": [
            {"sku": "D-CLC-1",   "size_weight": "1 pcs",          "price_buy": 14_000, "price_sell": 38_000},
        ],
    },
    {
        "name": "Panna Cotta", "code": "D-PNC", "category": "Dessert",
        "description": "Italian panna cotta set sempurna dengan berry compote. Silky, delicate, dan elegan — pairing natural untuk Spring blend.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 3, "max_stock": 15,
        "variants": [
            {"sku": "D-PNC-1",   "size_weight": "1 portion",      "price_buy": 12_000, "price_sell": 35_000},
        ],
    },
    {
        "name": "Klepon Cake", "code": "D-KLC", "category": "Dessert",
        "description": "Kue klepon modern: pandan sponge, gula aren lava filling, coconut cream topping. Nusantara dessert yang menemukan versi terbaik dirinya.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 3, "max_stock": 15,
        "variants": [
            {"sku": "D-KLC-1",   "size_weight": "1 slice",        "price_buy": 13_000, "price_sell": 35_000},
        ],
    },
    # ── SAVORY ─────────────────────────────────────────────────────────────────
    {
        "name": "Club Sandwich", "code": "F-CLUB", "category": "Savory",
        "description": "Triple decker: sourdough + grilled chicken + telur mata sapi + lettuce + tomato + mayo + mustard. Twilight Bivouac meal.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 0, "max_stock": 20,
        "variants": [
            {"sku": "F-CLUB-1",  "size_weight": "1 set",          "price_buy": 18_000, "price_sell": 45_000},
        ],
    },
    {
        "name": "Nasi Goreng Lumra", "code": "F-NG", "category": "Savory",
        "description": "Nasi goreng spesial dengan ayam, telur mata sapi, acar, kerupuk, dan sambal matah Bali. Comfort food terbaik untuk Twilight Bivouac.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 0, "max_stock": 20,
        "variants": [
            {"sku": "F-NG-1",    "size_weight": "1 porsi",        "price_buy": 18_000, "price_sell": 42_000},
        ],
    },
    {
        "name": "Indomie Rebus Spesial", "code": "F-IDS", "category": "Savory",
        "description": "Indomie rebus + telur + sayur + keju parut. Comfort food paling demokratis yang pernah ada. Twilight Bivouac must-have.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 0, "max_stock": 30,
        "variants": [
            {"sku": "F-IDS-1",   "size_weight": "1 porsi",        "price_buy": 12_000, "price_sell": 28_000},
        ],
    },
    {
        "name": "French Fries", "code": "F-FF", "category": "Savory",
        "description": "Crispy golden french fries. Regular atau Large + cheese sauce. Snack sempurna untuk Midday Transit.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "is_active": True, "has_expiry": True, "track_batch": False,
        "min_stock": 0, "max_stock": 30,
        "variants": [
            {"sku": "F-FF-R",    "size_weight": "Regular",        "price_buy": 10_000, "price_sell": 25_000},
            {"sku": "F-FF-L",    "size_weight": "Large + Cheese", "price_buy": 15_000, "price_sell": 35_000},
        ],
    },
    # ── KOPI BIJI RETAIL ───────────────────────────────────────────────────────
    {
        "name": "Toraja Sapan Kalosi", "code": "BN-TOR", "category": "Single Origin",
        "description": "Single origin Toraja Sapan/Kalosi. Dark chocolate, brown sugar, full body. Wet-hulled process. Affiliated: Outpost 33 The Toraja Forest Shelter.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "PT Toraja Sulawesi Coffee",
        "is_active": True, "has_expiry": True, "track_batch": True,
        "min_stock": 500, "max_stock": 10_000,
        "variants": [
            {"sku": "BN-TOR-250", "size_weight": "250g",          "price_buy": 55_000, "price_sell": 95_000},
            {"sku": "BN-TOR-500", "size_weight": "500g",          "price_buy": 100_000,"price_sell": 175_000},
            {"sku": "BN-TOR-1KG", "size_weight": "1kg",           "price_buy": 185_000,"price_sell": 330_000},
        ],
    },
    {
        "name": "Gayo Red Honey", "code": "BN-GAY", "category": "Single Origin",
        "description": "Single origin Aceh Gayo, proses Red Honey. Apricot, jasmine, honeysuckle — medium body. Affiliated: Outpost 25 The Gayo Highlands Shelter.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "CV Gayo Highland Farm",
        "is_active": True, "has_expiry": True, "track_batch": True,
        "min_stock": 500, "max_stock": 10_000,
        "variants": [
            {"sku": "BN-GAY-250", "size_weight": "250g",          "price_buy": 65_000, "price_sell": 110_000},
            {"sku": "BN-GAY-500", "size_weight": "500g",          "price_buy": 120_000,"price_sell": 205_000},
            {"sku": "BN-GAY-1KG", "size_weight": "1kg",           "price_buy": 225_000,"price_sell": 390_000},
        ],
    },
    {
        "name": "Java Preanger Natural", "code": "BN-JAV", "category": "Single Origin",
        "description": "Single origin Java Preanger, Natural process. Tropical fruit, citrus, floral. Affiliated: Outpost 02 The Priangan Counting House.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "PT Java Preanger Estate",
        "is_active": True, "has_expiry": True, "track_batch": True,
        "min_stock": 500, "max_stock": 10_000,
        "variants": [
            {"sku": "BN-JAV-250", "size_weight": "250g",          "price_buy": 60_000, "price_sell": 105_000},
            {"sku": "BN-JAV-500", "size_weight": "500g",          "price_buy": 110_000,"price_sell": 195_000},
            {"sku": "BN-JAV-1KG", "size_weight": "1kg",           "price_buy": 205_000,"price_sell": 370_000},
        ],
    },
    {
        "name": "Papua Wamena Anaerobic", "code": "BN-PAP", "category": "Single Origin",
        "description": "Single origin Papua Wamena, proses Anaerobic. Aged wine, dark rum, fermented fruit. Ultra-rare, harvest terbatas. Affiliated: Outpost 35 The Eastern Terminus.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "PT Papua Highland Coffee",
        "is_active": True, "has_expiry": True, "track_batch": True,
        "min_stock": 100, "max_stock": 2_000,
        "variants": [
            {"sku": "BN-PAP-100", "size_weight": "100g",          "price_buy": 65_000, "price_sell": 135_000},
            {"sku": "BN-PAP-250", "size_weight": "250g",          "price_buy": 140_000,"price_sell": 295_000},
            {"sku": "BN-PAP-500", "size_weight": "500g",          "price_buy": 260_000,"price_sell": 545_000},
        ],
    },
    {
        "name": "Lumra House Blend", "code": "BN-HB", "category": "House Blend",
        "description": "60% Toraja Kalosi + 40% Mandailing Grade 1. Signature espresso blend Kafe Nusantara. Chocolate, caramel, full body. Dirancang untuk semua brewing method.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": None,
        "is_active": True, "has_expiry": True, "track_batch": True,
        "min_stock": 1_000, "max_stock": 20_000,
        "variants": [
            {"sku": "BN-HB-250",  "size_weight": "250g",          "price_buy": 45_000, "price_sell": 78_000},
            {"sku": "BN-HB-500",  "size_weight": "500g",          "price_buy": 82_000, "price_sell": 145_000},
            {"sku": "BN-HB-1KG",  "size_weight": "1kg",           "price_buy": 155_000,"price_sell": 275_000},
        ],
    },
    # ── MERCHANDISE ────────────────────────────────────────────────────────────
    {
        "name": "Lumra Tumbler 500ml", "code": "M-TMB-500", "category": "Merchandise",
        "description": "Stainless steel double wall tumbler. Keep hot 6hrs / cold 12hrs. Logo Kafe Nusantara emboss. Edition: The Four Expeditions.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Packaging Solutions",
        "is_active": True, "has_expiry": False, "track_batch": True,
        "min_stock": 10, "max_stock": 200,
        "variants": [
            {"sku": "M-TMB-500-BLK","size_weight": "500ml Black",  "price_buy": 65_000, "price_sell": 125_000},
            {"sku": "M-TMB-500-WHT","size_weight": "500ml White",  "price_buy": 65_000, "price_sell": 125_000},
            {"sku": "M-TMB-500-GRN","size_weight": "500ml Green",  "price_buy": 65_000, "price_sell": 125_000},
            {"sku": "M-TMB-500-NVY","size_weight": "500ml Navy",   "price_buy": 65_000, "price_sell": 125_000},
        ],
    },
    {
        "name": "Lumra Paspor Ekspedisi Kit", "code": "M-PSP", "category": "Merchandise",
        "description": "Kit membership: Paspor Ekspedisi digital activation card + pin set 4 season + lanyard Kafe Nusantara. Welcome gift untuk member baru.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Packaging Solutions",
        "is_active": True, "has_expiry": False, "track_batch": True,
        "min_stock": 50, "max_stock": 500,
        "variants": [
            {"sku": "M-PSP-STD",  "size_weight": "Standard Kit",  "price_buy": 35_000, "price_sell": 75_000},
            {"sku": "M-PSP-PRE",  "size_weight": "Premium Kit",   "price_buy": 75_000, "price_sell": 150_000},
        ],
    },
    {
        "name": "Lumra V60 Starter Kit", "code": "M-V60", "category": "Merchandise",
        "description": "V60 ceramic dripper (01/02) + server glass + filter papers 50pcs + 50g sample kopi. Everything you need to start your first expedition at home.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Packaging Solutions",
        "is_active": True, "has_expiry": False, "track_batch": True,
        "min_stock": 5, "max_stock": 50,
        "variants": [
            {"sku": "M-V60-1",    "size_weight": "Full Set",      "price_buy": 150_000,"price_sell": 285_000},
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CUSTOMER & STAFF DATA
# ═══════════════════════════════════════════════════════════════════════════════

FIRST_NAMES = [
    "Ahmad", "Budi", "Citra", "Dian", "Eka", "Farah", "Gita", "Hendra",
    "Indra", "Joko", "Kurnia", "Lina", "Maya", "Nita", "Oka", "Putri",
    "Reza", "Siti", "Toni", "Usman", "Vina", "Wawan", "Yuni", "Zahra",
    "Aditya", "Bagas", "Cahya", "Desy", "Firman", "Hana", "Irfan", "Jaya",
    "Kevin", "Lisa", "Rizky", "Anisa", "Bayu", "Dimas", "Galih", "Intan",
    "Fajar", "Gilang", "Hasna", "Ivan", "Jesika", "Krisna", "Laras", "Manda",
    "Naufal", "Olivia", "Pandu", "Qisthi", "Rahmat", "Salsa", "Teguh", "Ulfi",
]

LAST_NAMES = [
    "Wijaya", "Rahman", "Santoso", "Nurdin", "Kusuma", "Gunawan", "Setiawan",
    "Handoko", "Saputra", "Hidayat", "Suryanto", "Hartono", "Lestari", "Dewi",
    "Putri", "Amelia", "Rahayu", "Permana", "Utama", "Kurnia", "Pratama",
    "Nugraha", "Purnama", "Syahputra", "Wibowo", "Irawan", "Mulyono",
    "Prasetyo", "Sudarmono", "Harahap", "Sitompul", "Nainggolan",
]

CITIES = [
    "Jakarta", "Bandung", "Surabaya", "Medan", "Semarang", "Makassar",
    "Palembang", "Yogyakarta", "Bogor", "Bekasi", "Tangerang", "Depok",
    "Denpasar", "Malang", "Solo", "Aceh", "Manado", "Padang", "Pekanbaru",
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com"]
PHONE_PREFIXES = ["0811","0812","0813","0814","0815","0821","0822","0852","0853","0857","0858"]
CUSTOMER_TIERS = {
    "bronze":   0.55,
    "silver":   0.25,
    "gold":     0.14,
    "platinum": 0.06,
}
CUSTOMER_TYPES = ["retail", "retail", "retail", "wholesale", "restaurant", "hotel", "clinic"]

ROLES_DATA = [
    {"name": "Admin",      "code": "ADM", "description": "System administrator, akses penuh"},
    {"name": "Manager",    "code": "MGR", "description": "Store manager, approve semua transaksi"},
    {"name": "Barista",    "code": "BAR", "description": "Barista operasional, akses POS"},
    {"name": "Kasir",      "code": "KSR", "description": "Kasir POS, akses transaksi"},
    {"name": "Roaster",    "code": "RST", "description": "Roastmaster, akses produksi"},
    {"name": "Gudang",     "code": "GDG", "description": "Staff gudang, akses inventory"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def gen_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def gen_email(name):
    parts = name.lower().split()
    sep = random.choice([".", "_", ""])
    base = f"{parts[0]}{sep}{parts[1]}"
    num = random.randint(1, 9999)
    domain = random.choice(EMAIL_DOMAINS)
    return f"{base}{num}@{domain}"

def gen_phone():
    return f"{random.choice(PHONE_PREFIXES)}{''.join(str(random.randint(0,9)) for _ in range(8))}"

def gen_address(city=None):
    streets = ["Jl. Sudirman","Jl. Diponegoro","Jl. Gatot Subroto","Jl. Asia Afrika",
               "Jl. Imam Bonjol","Jl. Pemuda","Jl. Veteran","Jl. Hayam Wuruk",
               "Jl. Gajah Mada","Jl. Sisingamangaraja","Jl. A. Yani","Jl. Raya"]
    return f"{random.choice(streets)} No.{random.randint(1,999)}, {city or random.choice(CITIES)}"

def gen_tier():
    r = random.random()
    cumulative = 0
    for tier, prob in CUSTOMER_TIERS.items():
        cumulative += prob
        if r < cumulative:
            return tier
    return "bronze"

def log(cmd, msg, style="normal"):
    if style == "success":
        cmd.stdout.write(cmd.style.SUCCESS(f"  [OK] {msg}"))
    elif style == "warning":
        cmd.stdout.write(cmd.style.WARNING(f"  [WARN] {msg}"))
    elif style == "error":
        cmd.stdout.write(cmd.style.ERROR(f"  [ERR] {msg}"))
    elif style == "header":
        cmd.stdout.write(cmd.style.SUCCESS(f"\n{'-'*60}\n  {msg}\n{'-'*60}"))
    else:
        cmd.stdout.write(f"     {msg}")

def bulk_create_safe(model, objs, batch_size=500, ignore_conflicts=True):
    """Bulk create dengan batching dan conflict handling."""
    if not objs:
        return 0
    created = 0
    for i in range(0, len(objs), batch_size):
        batch = objs[i:i+batch_size]
        result = model.objects.bulk_create(batch, ignore_conflicts=ignore_conflicts, batch_size=batch_size)
        created += len(result)
    return created


def normalize_attr_value(value, max_length=255):
    """Pastikan attr_value tidak melebihi batas kolom database."""
    text = str(value)
    if len(text) <= max_length:
        return text, False
    return text[:max_length], True

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — MANAGEMENT COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = "Seed database Kafe Nusantara — master data, menu, 9999 kopi, customers, staff"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true",
            help="Hapus data lama sebelum seed (HATI-HATI: irreversible)"
        )
        parser.add_argument(
            "--only", type=str, default=None,
            choices=["master", "menu", "kopi", "customers", "staff", "all"],
            help="Jalankan hanya bagian tertentu"
        )
        parser.add_argument(
            "--json", type=str, default=None,
            help="Path ke file kopi_9999_db.json dari grand_blend_engine.py"
        )
        parser.add_argument(
            "--batch-size", type=int, default=500,
            help="Ukuran batch untuk bulk insert (default: 500)"
        )
        parser.add_argument(
            "--num-customers", type=int, default=5000,
            help="Jumlah dummy customers (default: 5000)"
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Preview rencana seed tanpa eksekusi"
        )
        parser.add_argument(
            "--skip-recipes", action="store_true",
            help="Skip pembuatan production recipes (lebih cepat)"
        )

    def handle(self, *args, **options):
        self.stats = {}
        self.batch_size = options["batch_size"]
        self.dry_run    = options["dry_run"]
        self.skip_recipes = options.get("skip_recipes", False)

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  KAFE NUSANTARA - MASTER SEEDER v1.0"))
        self.stdout.write(self.style.SUCCESS("  The Four Expeditions - World Building DB"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        if self.dry_run:
            self.stdout.write(self.style.WARNING("  [DRY RUN] Tidak ada data yang akan diubah"))

        if options["clear"] and not self.dry_run:
            self._clear()

        only = options.get("only")
        run_all = (only is None or only == "all")

        try:
            if run_all or only == "master":
                self._seed_master()
            if run_all or only == "menu":
                self._seed_menu()
            if run_all or only == "kopi":
                json_path = options.get("json")
                self._seed_kopi_9999(json_path)
            if run_all or only == "customers":
                self._seed_customers(options["num_customers"])
            if run_all or only == "staff":
                self._seed_staff()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n[ERR] Error: {e}"))
            import traceback; traceback.print_exc()
            raise

        self._summary()

    # ─── CLEAR ────────────────────────────────────────────────────────────────
    def _clear(self):
        log(self, "CLEARING DATABASE DATA", "header")
        models_to_clear = []
        if HAS_ATTR:
            models_to_clear.append(("ProductAttributeItem", ProductAttributeItem))
        models_to_clear += [
            ("ProductVariant", ProductVariantModel),
            ("Product",        ProductModel),
            ("Customer",       CustomerModel),
            ("Location",       LocationModel),
            ("Vendor",         VendorModel),
            ("Category",       CategoryModel),
            ("Unit",           UnitModel),
            ("Tax",            TaxModel),
        ]
        if HAS_PRODUCTION:
            models_to_clear = [
                ("RecipeIngredient", RecipeIngredientModel),
                ("Recipe",           RecipeModel),
                ("RecipeCategory",   RecipeCategoryModel),
            ] + models_to_clear

        with transaction.atomic():
            for name, model in models_to_clear:
                count = model.objects.count()
                model.objects.all().delete()
                if count:
                    log(self, f"{name}: {count} deleted")

        log(self, "Data lama dihapus", "success")

    # ─── MASTER DATA ──────────────────────────────────────────────────────────
    def _seed_master(self):
        log(self, "SEEDING MASTER DATA", "header")

        # Taxes
        for d in TAXES_DATA:
            if not self.dry_run:
                _, created = TaxModel.objects.get_or_create(name=d["name"], defaults=d)
                self._inc("taxes", int(created))
            else:
                self._inc("taxes [dry]", 1)
        log(self, f"{len(TAXES_DATA)} taxes")

        # Units
        for d in UNITS_DATA:
            if not self.dry_run:
                _, created = UnitModel.objects.get_or_create(name=d["name"], defaults=d)
                self._inc("units", int(created))
        log(self, f"{len(UNITS_DATA)} units")

        # Categories (parent first)
        cat_objs = {}
        parents = [c for c in CATEGORIES_DATA if c["parent"] is None]
        children = [c for c in CATEGORIES_DATA if c["parent"] is not None]

        for d in parents:
            if not self.dry_run:
                obj, created = CategoryModel.objects.get_or_create(
                    name=d["name"],
                    defaults={k: v for k, v in d.items() if k != "parent"}
                )
                cat_objs[d["name"]] = obj
                self._inc("categories", int(created))
            else:
                self._inc("categories [dry]", 1)

        for d in children:
            parent_obj = cat_objs.get(d["parent"])
            if not self.dry_run:
                defaults = {k: v for k, v in d.items() if k not in ("parent",)}
                if parent_obj:
                    defaults["parent"] = parent_obj
                obj, created = CategoryModel.objects.get_or_create(
                    name=d["name"], defaults=defaults
                )
                cat_objs[d["name"]] = obj
                self._inc("categories", int(created))

        log(self, f"{len(CATEGORIES_DATA)} categories (parent + child)")

        # Vendors
        for d in VENDORS_DATA:
            if not self.dry_run:
                _, created = VendorModel.objects.get_or_create(
                    name=d["name"],
                    defaults={**d, "is_active": True,
                               "created_at": timezone.now(),
                               "updated_at": timezone.now()}
                )
                self._inc("vendors", int(created))
        log(self, f"{len(VENDORS_DATA)} vendors")

        # Locations
        for d in LOCATIONS_DATA:
            if not self.dry_run:
                _, created = LocationModel.objects.get_or_create(
                    name=d["name"],
                    defaults={"address": d["address"], "location_type": d["location_type"],
                              "created_at": timezone.now()}
                )
                self._inc("locations", int(created))
        log(self, f"{len(LOCATIONS_DATA)} locations (outpost + warehouse)")

        # Roles
        if HAS_ROLE:
            for d in ROLES_DATA:
                if not self.dry_run:
                    _, created = Role.objects.get_or_create(name=d["name"], defaults=d)
                    self._inc("roles", int(created))
            log(self, f"{len(ROLES_DATA)} roles")

        # Admin user
        if not self.dry_run:
            admin, created = User.objects.get_or_create(
                username="admin",
                defaults={"email": "admin@kafenusantara.id", "is_staff": True, "is_superuser": True,
                          "first_name": "Sang", "last_name": "Kurator"}
            )
            if created:
                admin.set_password("nusantara2024!")
                admin.save()
                self._inc("users", 1)

        log(self, "Master data selesai", "success")

    # ─── CAFE MENU ────────────────────────────────────────────────────────────
    def _seed_menu(self):
        log(self, "SEEDING MENU KAFE (55 produk)", "header")

        if self.dry_run:
            log(self, f"{len(MENU_PRODUCTS)} produk menu (dry run)")
            return

        products_created = 0
        variants_created = 0

        for p in MENU_PRODUCTS:
            try:
                cat = CategoryModel.objects.filter(name=p["category"]).first()
                if not cat:
                    log(self, f"Category not found: {p['category']} — skip", "warning")
                    continue

                unit    = UnitModel.objects.filter(name=p["unit"]).first()
                tax     = TaxModel.objects.filter(name=p["tax"]).first()
                vendor  = VendorModel.objects.filter(name=p["vendor"]).first() if p.get("vendor") else None

                defaults = {
                    "description": p["description"],
                    "category":    cat,
                    "unit":        unit,
                    "tax":         tax,
                    "vendor":      vendor,
                    "barcode":     p["code"],
                    "is_active":   p.get("is_active", True),
                    "has_expiry":  p.get("has_expiry", False),
                    "track_batch": p.get("track_batch", False),
                    "min_stock":   D(str(p.get("min_stock", 0))),
                    "max_stock":   D(str(p.get("max_stock", 9999))),
                    "updated_at":  timezone.now(),
                }

                product = ProductModel.objects.filter(barcode=p["code"]).first()
                pc = False
                if not product:
                    product = ProductModel.objects.filter(name=p["name"]).first()

                if product:
                    changed = False
                    for field, value in defaults.items():
                        if getattr(product, field) != value:
                            setattr(product, field, value)
                            changed = True
                    if changed:
                        product.save(update_fields=list(defaults.keys()))
                else:
                    product = ProductModel.objects.create(
                        name=p["name"],
                        created_at=timezone.now(),
                        **defaults,
                    )
                    pc = True

                products_created += int(pc)

                for v in p["variants"]:
                    variant_defaults = {
                        "product":     product,
                        "size_weight": v["size_weight"],
                        "price_buy":   D(str(v["price_buy"])),
                        "price_sell":  D(str(v["price_sell"])),
                        "updated_at":  timezone.now(),
                    }
                    variant, vc = ProductVariantModel.objects.get_or_create(
                        sku=v["sku"],
                        defaults=variant_defaults,
                    )
                    if not vc:
                        changed = False
                        for field, value in variant_defaults.items():
                            if getattr(variant, field) != value:
                                setattr(variant, field, value)
                                changed = True
                        if changed:
                            variant.save(update_fields=list(variant_defaults.keys()))
                    variants_created += int(vc)

            except Exception as e:
                log(self, f"Error seeding {p['name']}: {e}", "warning")

        self._inc("menu_products", products_created)
        self._inc("menu_variants", variants_created)
        log(self, f"{products_created} produk, {variants_created} variant created", "success")

    # ─── KOPI 9999 ────────────────────────────────────────────────────────────
    def _seed_kopi_9999(self, json_path=None):
        log(self, "SEEDING 9999 KOPI NUSANTARA", "header")

        # Cari JSON file
        if json_path:
            json_file = Path(json_path)
        else:
            # Auto-detect di lokasi umum
            candidates = [
                Path("kopi_9999_db.json"),
                Path(__file__).with_name("kopi_9999_db.json"),
                Path("/mnt/user-data/outputs/kopi_9999_db.json"),
                Path("data/kopi_9999_db.json"),
                Path("../kopi_9999_db.json"),
            ]
            json_file = next((p for p in candidates if p.exists()), None)

        if not json_file or not json_file.exists():
            log(self, "kopi_9999_db.json tidak ditemukan. Gunakan --json /path/to/file.json", "warning")
            log(self, "Skipping kopi seed. Generate file dengan: python grand_blend_engine.py", "warning")
            return

        log(self, f"Loading: {json_file}")
        with open(json_file, encoding="utf-8") as f:
            fixtures = json.load(f)

        log(self, f"Total fixture records: {len(fixtures):,}")

        if self.dry_run:
            products_count = sum(1 for f in fixtures if f["model"].endswith(".products"))
            variants_count = sum(1 for f in fixtures if f["model"].endswith(".productvariants"))
            log(self, f"Dry run: {products_count} products, {variants_count} variants would be created")
            return

        # Pisahkan per model type
        product_fixtures  = [f for f in fixtures if f["model"].endswith(".products")]
        variant_fixtures  = [f for f in fixtures if f["model"].endswith(".productvariants")]
        attr_fixtures     = [f for f in fixtures if f["model"].endswith(".productattribute_items")]

        log(self, f"Products: {len(product_fixtures):,} | Variants: {len(variant_fixtures):,} | Attrs: {len(attr_fixtures):,}")
        product_ref_to_name = {
            str(f["pk"]): f["fields"]["name"]
            for f in product_fixtures
        }
        variant_ref_to_sku = {
            str(f["pk"]): f["fields"]["sku"]
            for f in variant_fixtures
        }

        # Get required FK objects
        hb_cat  = CategoryModel.objects.filter(name="House Blend").first()
        so_cat  = CategoryModel.objects.filter(name="Single Origin").first()
        gram_unit = UnitModel.objects.filter(name="Gram").first()
        ppn11   = TaxModel.objects.filter(name="PPN 11%").first()

        if not hb_cat:
            log(self, "Category 'House Blend' tidak ditemukan. Jalankan --only master dulu.", "error")
            return

        # ── INSERT PRODUCTS ──────────────────────────────────────────────────
        log(self, f"Inserting {len(product_fixtures):,} products...")

        product_objs = []
        existing_names = set(ProductModel.objects.values_list("name", flat=True))

        total = len(product_fixtures)
        chunk = max(1, total // 20)  # 5% progress reports

        for i, f in enumerate(product_fixtures):
            if i % chunk == 0:
                pct = int(i / total * 100)
                self.stdout.write(f"\r     Progress: {i:,}/{total:,} ({pct}%)", ending="")
                self.stdout.flush()

            fields = f["fields"]
            name   = fields["name"]
            if name in existing_names:
                continue

            fixture_pk = str(f.get("pk", "")).lower()
            cat = hb_cat
            if so_cat and fixture_pk.startswith("so_"):
                cat = so_cat

            product_objs.append(ProductModel(
                name        = name,
                description = fields.get("description", ""),
                category    = cat,
                unit        = gram_unit,
                tax         = ppn11,
                vendor      = None,
                is_active   = fields.get("is_active", True),
                has_expiry  = fields.get("has_expiry", False),
                track_batch = fields.get("track_batch", True),
                min_stock   = D(str(fields.get("min_stock", 0))),
                max_stock   = D(str(fields.get("max_stock", 9999))),
                created_at  = timezone.now(),
                updated_at  = timezone.now(),
            ))

        self.stdout.write("")  # newline after progress

        # Bulk insert products
        products_created = 0
        for i in range(0, len(product_objs), self.batch_size):
            batch = product_objs[i:i+self.batch_size]
            with transaction.atomic():
                result = ProductModel.objects.bulk_create(batch, ignore_conflicts=True, batch_size=self.batch_size)
                products_created += len(result)

        log(self, f"Products inserted: {products_created:,}", "success")

        # Refresh product name → id map
        imported_names = [f["fields"]["name"] for f in product_fixtures]
        name_to_product = {
            p.name: p for p in ProductModel.objects.filter(name__in=imported_names)
        }

        # ── INSERT VARIANTS ──────────────────────────────────────────────────
        log(self, f"Inserting {len(variant_fixtures):,} variants...")

        existing_skus = set(ProductVariantModel.objects.values_list("sku", flat=True))
        variant_objs  = []

        for f in variant_fixtures:
            fields  = f["fields"]
            sku     = fields["sku"]
            if sku in existing_skus:
                continue

            product_ref  = str(fields.get("product", ""))
            product_name = product_ref_to_name.get(product_ref)
            product_obj = name_to_product.get(product_name)

            if not product_obj:
                continue

            size = fields.get("size_weight", "100g")

            variant_objs.append(ProductVariantModel(
                sku        = sku,
                product    = product_obj,
                size_weight= size,
                price_buy  = D(str(fields.get("price_buy", 0))),
                price_sell = D(str(fields.get("price_sell", 0))),
                updated_at = timezone.now(),
            ))

        variants_created = 0
        for i in range(0, len(variant_objs), self.batch_size):
            batch = variant_objs[i:i+self.batch_size]
            with transaction.atomic():
                result = ProductVariantModel.objects.bulk_create(batch, ignore_conflicts=True, batch_size=self.batch_size)
                variants_created += len(result)

        log(self, f"Variants inserted: {variants_created:,}", "success")

        # ── INSERT ATTRIBUTE ITEMS ───────────────────────────────────────────
        if HAS_ATTR and attr_fixtures:
            log(self, f"Inserting {len(attr_fixtures):,} attribute items...")

            # Fixture attribute menyimpan referensi ke variant fixture pk, bukan SKU.
            all_variant_refs = {str(f["fields"]["variant"]) for f in attr_fixtures}
            all_skus_in_attrs = [
                variant_ref_to_sku[variant_ref]
                for variant_ref in all_variant_refs
                if variant_ref in variant_ref_to_sku
            ]
            sku_to_id = {}
            for i in range(0, len(all_skus_in_attrs), 1000):
                chunk_skus = all_skus_in_attrs[i:i+1000]
                sku_to_id.update(
                    ProductVariantModel.objects.filter(sku__in=chunk_skus).values_list("sku", "id")
                )

            variant_ids = list(sku_to_id.values())
            existing_attr_keys = set()
            for i in range(0, len(variant_ids), 1000):
                chunk_ids = variant_ids[i:i+1000]
                existing_attr_keys.update(
                    ProductAttributeItem.objects.filter(variant_id__in=chunk_ids).values_list(
                        "variant_id", "attr_name", "attr_value"
                    )
                )

            attr_objs = []
            truncated_count = 0
            skipped_existing = 0
            for f in attr_fixtures:
                fields  = f["fields"]
                variant_ref = str(fields.get("variant"))
                variant_sku = variant_ref_to_sku.get(variant_ref)
                if not variant_sku:
                    continue
                variant_id  = sku_to_id.get(variant_sku)
                if not variant_id:
                    continue

                attr_value, was_truncated = normalize_attr_value(fields["attr_value"])
                attr_key = (variant_id, fields["attr_name"], attr_value)
                if attr_key in existing_attr_keys:
                    skipped_existing += 1
                    continue
                if was_truncated:
                    truncated_count += 1
                existing_attr_keys.add(attr_key)

                attr_objs.append(ProductAttributeItem(
                    variant_id  = variant_id,
                    attr_name   = fields["attr_name"],
                    attr_value  = attr_value,
                    updated_at  = timezone.now(),
                ))

            attrs_created = 0
            for i in range(0, len(attr_objs), self.batch_size):
                batch = attr_objs[i:i+self.batch_size]
                with transaction.atomic():
                    result = ProductAttributeItem.objects.bulk_create(
                        batch, ignore_conflicts=True, batch_size=self.batch_size
                    )
                    attrs_created += len(result)

            self._inc("kopi_attrs", attrs_created)
            log(self, f"Attribute items inserted: {attrs_created:,}", "success")
            if skipped_existing:
                log(self, f"Attribute items skipped (already exist): {skipped_existing:,}")
            if truncated_count:
                log(self, f"Attribute values truncated to 255 chars: {truncated_count:,}", "warning")

        self._inc("kopi_products", products_created)
        self._inc("kopi_variants", variants_created)

    # ─── CUSTOMERS ────────────────────────────────────────────────────────────
    def _seed_customers(self, n: int):
        log(self, f"SEEDING {n:,} CUSTOMERS", "header")

        if self.dry_run:
            log(self, f"{n:,} customers (dry run)")
            return

        existing_emails = set(CustomerModel.objects.values_list("email", flat=True))
        created_count = 0
        batch = []

        for i in range(n):
            if i % 1000 == 0 and i > 0:
                self.stdout.write(f"\r     Progress: {i:,}/{n:,}", ending="")
                self.stdout.flush()

            name   = gen_name()
            email  = gen_email(name)
            # Ensure unique email
            attempts = 0
            while email in existing_emails and attempts < 5:
                email = gen_email(name)
                attempts += 1
            if email in existing_emails:
                continue

            existing_emails.add(email)
            city = random.choice(CITIES)
            tier = gen_tier()
            loyalty = {"bronze": 0, "silver": random.randint(100,999),
                       "gold": random.randint(1000,9999), "platinum": random.randint(10000,99999)}[tier]

            batch.append(CustomerModel(
                name            = name,
                email           = email,
                phone           = gen_phone(),
                address         = gen_address(city),
                city            = city,
                tier            = tier,
                loyalty_points  = loyalty,
                total_spent     = D(str(loyalty * random.randint(10, 50) * 1000)),
                total_orders    = random.randint(1, loyalty // 10 + 1) if loyalty else random.randint(1, 5),
                is_active       = True,
                customer_type   = random.choice(CUSTOMER_TYPES),
                created_at      = timezone.now() - timedelta(days=random.randint(0, 730)),
                updated_at      = timezone.now(),
            ))

            if len(batch) >= self.batch_size:
                with transaction.atomic():
                    result = CustomerModel.objects.bulk_create(batch, ignore_conflicts=True)
                    created_count += len(result)
                batch = []

        # Flush remaining
        if batch:
            with transaction.atomic():
                result = CustomerModel.objects.bulk_create(batch, ignore_conflicts=True)
                created_count += len(result)

        self.stdout.write("")  # newline
        self._inc("customers", created_count)
        log(self, f"{created_count:,} customers created", "success")

    # ─── STAFF ────────────────────────────────────────────────────────────────
    def _seed_staff(self):
        log(self, "SEEDING STAFF USERS", "header")

        if self.dry_run:
            log(self, "Staff seed (dry run)")
            return

        stores   = LocationModel.objects.filter(location_type="store")
        roastery = LocationModel.objects.filter(location_type="roastery").first()

        created = 0

        store_configs = [
            ("mgr",  "Manager",  True,  1),
            ("bar",  "Barista",  False, 3),
            ("ksr",  "Kasir",    False, 1),
        ]

        for store in stores:
            code = store.name.split(":")[0].strip().lower().replace(" ", "_")[:12]

            for prefix, role_name, is_staff, count in store_configs:
                for j in range(count):
                    suffix = f"_{j}" if count > 1 else ""
                    uname  = f"{prefix}_{code}{suffix}"[:30]

                    user, uc = User.objects.get_or_create(
                        username=uname,
                        defaults={
                            "email":      f"{uname}@kafenusantara.id",
                            "first_name": random.choice(FIRST_NAMES),
                            "last_name":  random.choice(LAST_NAMES),
                            "is_staff":   is_staff,
                            "is_active":  True,
                        }
                    )
                    if uc:
                        user.set_password("nusantara2024!")
                        user.save()
                        UserProfile.objects.get_or_create(
                            user=user,
                            defaults={"location": store, "role": role_name, "is_active": True}
                        )
                        created += 1

        # Roastery staff
        if roastery:
            for j in range(2):
                uname = f"roaster_{j}"
                user, uc = User.objects.get_or_create(
                    username=uname,
                    defaults={"email": f"{uname}@kafenusantara.id", "is_staff": True, "is_active": True}
                )
                if uc:
                    user.set_password("nusantara2024!")
                    user.save()
                    UserProfile.objects.get_or_create(
                        user=user,
                        defaults={"location": roastery, "role": "Roaster", "is_active": True}
                    )
                    created += 1

        self._inc("staff_users", created)
        log(self, f"{created} staff users created", "success")
        log(self, "Password semua staff: nusantara2024!")
        log(self, "Admin: admin / nusantara2024!")

    # ─── UTILS ────────────────────────────────────────────────────────────────
    def _inc(self, key, n=1):
        self.stats[key] = self.stats.get(key, 0) + n

    def _summary(self):
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("  SUMMARY"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        total = 0
        for k in sorted(self.stats):
            v = self.stats[k]
            if v:
                self.stdout.write(f"  - {k:<30} {v:>8,}")
                total += v

        self.stdout.write(self.style.SUCCESS(f"  {'-'*40}"))
        self.stdout.write(self.style.SUCCESS(f"  - {'TOTAL RECORDS':<30} {total:>8,}"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  SELESAI - Kafe Nusantara DB Ready"))
        self.stdout.write(self.style.SUCCESS("  Admin  : admin / nusantara2024!"))
        self.stdout.write(self.style.SUCCESS("  Staff  : [username] / nusantara2024!"))
        self.stdout.write(self.style.SUCCESS("  Outpost: 27 locations seeded"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
