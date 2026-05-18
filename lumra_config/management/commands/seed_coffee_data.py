"""
Seed Coffee Data untuk Lumra POS System
========================================
Run:  python manage.py seed_coffee_data
      python manage.py seed_coffee_data --clear    (hapus data lama dulu)
      python manage.py seed_coffee_data --dry-run  (cek saja, tidak insert)

Order insert (respek FK):
  1. User + Store
  2. Categories (parent dulu, lalu child)
  3. Units
  4. Taxes
  5. Vendors
  6. Locations
  7. UserProfile
  8. Products
  9. ProductVariants
  10. ProductBatches
  11. Stock
  12. Customers
  13. RecipeCategories
  14. Recipes + RecipeIngredients
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

# ============================================================================
# MODEL IMPORT — sesuaikan nama model dengan models.py kamu
# ============================================================================
# Jika nama model beda, edit bagian ini saja.

from lumra_config.models import (
    Category,
    Tax,
    Unit,
    Vendor,
    Location,
    Product,
    ProductVariant,
    ProductBatches,
    Stock,
    Customer,
    UserProfile,
    RecipeCategory,
    Recipe,
    RecipeIngredient,
)

# Note: Store model not found in current models.py, will handle separately

User = get_user_model()

# ============================================================================
# CONSTANTS
# ============================================================================
NOW = timezone.now()
TOMORROW = NOW + timedelta(days=1)


def d(val):
    """Shortcut Decimal."""
    return Decimal(str(val))


# ============================================================================
# DATA DEFINITIONS
# ============================================================================

CATEGORIES = [
    # (name, description, slug, code, icon_url, is_active, parent_slug)
    # === LEVEL 0 (parent) ===
    ("Kopi Biji", "Biji kopi sangrai siap seduh atau untuk supply", "kopi-biji", "KB",
     "/icons/coffee-beans.svg", True, None),
    ("Minuman Kopi", "Menu minuman berbasis kopi", "minuman-kopi", "MK",
     "/icons/coffee-cup.svg", True, None),
    ("Manual Brew", "Minuman kopi dengan metode manual brewing", "manual-brew", "MB",
     "/icons/v60.svg", True, None),
    ("Non-Kopi", "Minuman non-kopi dan variasi lain", "non-kopi", "NK",
     "/icons/tea-cup.svg", True, None),
    ("Makanan & Kue", "Pastry, cake, dan makanan pendamping", "makanan-kue", "MKU",
     "/icons/croissant.svg", True, None),
    ("Merchandise", "Produk merchandise dan perlengkapan kopi", "merchandise", "MER",
     "/icons/tshirt.svg", True, None),
    ("Bahan Baku", "Bahan baku produksi (bukan dijual langsung)", "bahan-baku", "BB",
     "/icons/ingredient.svg", True, None),

    # === LEVEL 1 (child) ===
    ("Single Origin", "Kopi single origin dari satu daerah spesifik", "single-origin", "SO",
     "/icons/globe.svg", True, "kopi-biji"),
    ("House Blend", "Campuran biji kopi racikan rumah", "house-blend", "HB",
     "/icons/blender.svg", True, "kopi-biji"),
    ("Espresso Based", "Minuman berbasis espresso shot", "espresso-based", "EB",
     "/icons/espresso.svg", True, "minuman-kopi"),
    ("Cold Brew", "Minuman kopi yang diseduh dingin", "cold-brew", "CB",
     "/icons/cold-brew.svg", True, "minuman-kopi"),
    ("Sirup & Topping", "Sirup, saus, dan topping tambahan", "sirup-topping", "ST",
     "/icons/syrup.svg", True, "bahan-baku"),
    ("Susu & Dairy", "Susu dan produk dairy", "susu-dairy", "SD",
     "/icons/milk.svg", True, "bahan-baku"),
]

UNITS = [
    # (name, symbol, description, is_active)
    ("Gram", "g", "Satuan berat gram", True),
    ("Kilogram", "kg", "Satuan berat kilogram", True),
    ("Mililiter", "ml", "Satuan volume mililiter", True),
    ("Liter", "L", "Satuan volume liter", True),
    ("Pcs", "pcs", "Satuan buah/pieces", True),
    ("Pack", "pack", "Satuan paket", True),
    ("Sachet", "sachet", "Satuan sachet", True),
    ("Box", "box", "Satuan kotak", True),
    ("Ons", "oz", "Satuan berat ons (~28.35 gram)", True),
]

TAXES = [
    # (name, rate, description, is_active)
    ("PPN 11%", d("11.00"), "Pajak Pertambahan Nilai sesuai UU HPP", True),
    ("PPN 0%", d("0.00"), "Non-PPN / barang tidak kena pajak", True),
]

VENDORS = [
    # (name, contact_person, phone, code, email, address, website, tax_number, is_active)
    ("PT Toraja Sulawesi Coffee",
     "Pak Budi", "081234567001", "TOR", "budi@torajacoffee.co.id",
     "Jl. Sa'dan No.12, Rantepao, Toraja, Sulawesi Selatan 71211",
     "https://torajacoffee.co.id", "02.123.456.7-001.000", True),

    ("CV Gayo Highland Farm",
     "Ibu Ratna", "081234567002", "GAY", "ratna@gayohighland.co.id",
     "Jl. Takengon-Bireuen Km.5, Takengon, Aceh Tengah 24511",
     "https://gayohighland.co.id", "02.123.456.7-002.000", True),

    ("PT Java Preanger Estate",
     "Pak Hendra", "081234567003", "JPE", "hendra@javapreanger.co.id",
     "Jl. Perkebunan No.8, Pangalengan, Bandung, Jawa Barat 40378",
     "https://javapreanger.co.id", "02.123.456.7-003.000", True),

    ("PT Mandailing Coffee Co",
     "Pak Surya", "081234567004", "MDL", "surya@mandailingcoffee.co.id",
     "Jl. Lintas Sumatera No.45, Mandailing Natal, Sumatera Utara 22911",
     "https://mandailingcoffee.co.id", "02.123.456.7-004.000", True),

    ("CV Fresh Dairy Indonesia",
     "Ibu Maya", "081234567005", "FDI", "maya@freshdairy.co.id",
     "Jl. Raya Bogor Km.28, Ciomas, Bogor, Jawa Barat 16610",
     "https://freshdairy.co.id", "02.123.456.7-005.000", True),

    ("PT Indo Food Supply",
     "Pak Doni", "081234567006", "IFS", "doni@indofoodsupply.co.id",
     "Jl. Industri No.22, Cikarang, Bekasi, Jawa Barat 17530",
     "https://indofoodsupply.co.id", "02.123.456.7-006.000", True),

    ("CV Sugar & Syrup Nusantara",
     "Pak Andi", "081234567007", "SSN", "andi@sugarsyrup.co.id",
     "Jl. Gula No.15, Sidoarjo, Jawa Timur 61234",
     "https://sugarsyrup.co.id", "02.123.456.7-007.000", True),
]

LOCATIONS = [
    # (name, address, location_type)
    ("Toko Utama Kopi Lumra",
     "Jl. Sudirman No.123, Blok M, Jakarta Selatan 12190",
     "store"),
    ("Gudang Jakarta",
     "Jl. Raya Bogor Km.32, Depok, Jawa Barat 16411",
     "warehouse"),
    ("Roastery Bandung",
     "Jl. Dago No.88, Coblong, Bandung, Jawa Barat 40135",
     "roastery"),
]

# ---------------------------------------------------------------------------
# Products: list of dicts
#   Each product can have multiple variants
# ---------------------------------------------------------------------------
PRODUCTS = [
    # ─────────── SINGLE ORIGIN BEANS ───────────
    {
        "name": "Toraja Sapan Kalosi",
        "description": (
            "Single origin dari Toraja, Sulawesi Selatan. "
            "Profil rasa: dark chocolate, brown sugar, spicy, full body. "
            "Proses: Wet-hulled (Giling Basah). "
            "Altitude: 1.400-1.800 mdpl. Varietas: S795, Typica."
        ),
        "slug": "toraja-sapan-kalosi",
        "code": "TSK",
        "category_slug": "single-origin",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": "PT Toraja Sulawesi Coffee",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("50.00"),
        "min_stock": d("5.00"),
        "sell_price": None,  # harga di variant
        "track_batch": True,
        "variants": [
            {"sku": "TSK-250", "size_weight": "250 gram", "price_buy": d("55000"), "price_sell": d("95000")},
            {"sku": "TSK-500", "size_weight": "500 gram", "price_buy": d("100000"), "price_sell": d("175000")},
            {"sku": "TSK-1KG", "size_weight": "1 kilogram", "price_buy": d("185000"), "price_sell": d("330000")},
        ],
    },
    {
        "name": "Gayo Arabica Red Honey",
        "description": (
            "Single origin dari dataran tinggi Gayo, Aceh. "
            "Profil rasa: red fruit, winey, jasmine, medium body. "
            "Proses: Red Honey. Altitude: 1.500-1.700 mdpl. Varietas: Tim Tim, Ateng."
        ),
        "slug": "gayo-arabica-red-honey",
        "code": "GAH",
        "category_slug": "single-origin",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": "CV Gayo Highland Farm",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("50.00"),
        "min_stock": d("5.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "GAH-250", "size_weight": "250 gram", "price_buy": d("65000"), "price_sell": d("110000")},
            {"sku": "GAH-500", "size_weight": "500 gram", "price_buy": d("120000"), "price_sell": d("205000")},
            {"sku": "GAH-1KG", "size_weight": "1 kilogram", "price_buy": d("225000"), "price_sell": d("390000")},
        ],
    },
    {
        "name": "Java Preanger Natural",
        "description": (
            "Single origin dari perkebunan Preanger, Pangalengan, Bandung. "
            "Profil rasa: tropical fruit, citrus, floral, clean finish. "
            "Proses: Natural. Altitude: 1.200-1.500 mdpl. Varietas: Typica, USDA."
        ),
        "slug": "java-preanger-natural",
        "code": "JPN",
        "category_slug": "single-origin",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": "PT Java Preanger Estate",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("40.00"),
        "min_stock": d("5.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "JPN-250", "size_weight": "250 gram", "price_buy": d("60000"), "price_sell": d("105000")},
            {"sku": "JPN-500", "size_weight": "500 gram", "price_buy": d("110000"), "price_sell": d("195000")},
            {"sku": "JPN-1KG", "size_weight": "1 kilogram", "price_buy": d("205000"), "price_sell": d("370000")},
        ],
    },
    {
        "name": "Sumatra Mandheling Grade 1",
        "description": (
            "Single origin dari Mandailing Natal, Sumatera Utara. "
            "Profil rasa: earthy, herbal, dark chocolate, heavy body, low acidity. "
            "Proses: Wet-hulled (Giling Basah). Altitude: 1.100-1.600 mdpl."
        ),
        "slug": "sumatra-mandheling-g1",
        "code": "SMG",
        "category_slug": "single-origin",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": "PT Mandailing Coffee Co",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("50.00"),
        "min_stock": d("5.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "SMG-250", "size_weight": "250 gram", "price_buy": d("50000"), "price_sell": d("85000")},
            {"sku": "SMG-500", "size_weight": "500 gram", "price_buy": d("90000"), "price_sell": d("160000")},
            {"sku": "SMG-1KG", "size_weight": "1 kilogram", "price_buy": d("170000"), "price_sell": d("300000")},
        ],
    },
    {
        "name": "Ethiopia Yirgacheffe Washed",
        "description": (
            "Import single origin dari Yirgacheffe, Ethiopia. "
            "Profil rasa: bergamot, lemon, jasmine, tea-like body. "
            "Proses: Washed. Altitude: 1.800-2.200 mdpl. Varietas: Heirloom."
        ),
        "slug": "ethiopia-yirgacheffe",
        "code": "ETH",
        "category_slug": "single-origin",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": "PT Toraja Sulawesi Coffee",  # importir
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "ETH-250", "size_weight": "250 gram", "price_buy": d("85000"), "price_sell": d("150000")},
            {"sku": "ETH-500", "size_weight": "500 gram", "price_buy": d("155000"), "price_sell": d("280000")},
        ],
    },
    {
        "name": "Colombia Huila Supremo",
        "description": (
            "Import single origin dari Huila, Colombia. "
            "Profil rasa: caramel, red apple, nutty, medium body. "
            "Proses: Washed. Altitude: 1.600-2.000 mdpl. Varietas: Caturra, Castillo."
        ),
        "slug": "colombia-huila",
        "code": "COL",
        "category_slug": "single-origin",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": "PT Toraja Sulawesi Coffee",  # importir
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "COL-250", "size_weight": "250 gram", "price_buy": d("78000"), "price_sell": d("135000")},
            {"sku": "COL-500", "size_weight": "500 gram", "price_buy": d("142000"), "price_sell": d("250000")},
        ],
    },

    # ─────────── HOUSE BLEND BEANS ───────────
    {
        "name": "Lumra House Blend",
        "description": (
            "Racikan signature Kopi Lumra. Campuran 60% Toraja + 40% Mandheling. "
            "Profil rasa: chocolate, nutty, caramel, full body, low acidity. "
            "Cocok untuk espresso dan susu-based drinks. "
            "Medium-dark roast."
        ),
        "slug": "lumra-house-blend",
        "code": "LHB",
        "category_slug": "house-blend",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": None,  # internal blend
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("100.00"),
        "min_stock": d("10.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "LHB-250", "size_weight": "250 gram", "price_buy": d("45000"), "price_sell": d("78000")},
            {"sku": "LHB-500", "size_weight": "500 gram", "price_buy": d("82000"), "price_sell": d("145000")},
            {"sku": "LHB-1KG", "size_weight": "1 kilogram", "price_buy": d("155000"), "price_sell": d("275000")},
        ],
    },
    {
        "name": "Lumra Morning Blend",
        "description": (
            "Campuran untuk morning coffee. 50% Java + 30% Gayo + 20% Colombia. "
            "Profil rasa: bright citrus, caramel, clean finish. "
            "Medium roast. Cocok untuk filter/manual brew."
        ),
        "slug": "lumra-morning-blend",
        "code": "LMB",
        "category_slug": "house-blend",
        "tax_name": "PPN 11%",
        "unit_name": "Gram",
        "vendor_name": None,
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("60.00"),
        "min_stock": d("8.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "LMB-250", "size_weight": "250 gram", "price_buy": d("50000"), "price_sell": d("88000")},
            {"sku": "LMB-500", "size_weight": "500 gram", "price_buy": d("92000"), "price_sell": d("165000")},
            {"sku": "LMB-1KG", "size_weight": "1 kilogram", "price_buy": d("175000"), "price_sell": d("315000")},
        ],
    },

    # ─────────── ESPRESSO BASED ───────────
    {
        "name": "Espresso",
        "description": "Single/double shot espresso dari House Blend. Diseduh dengan mesin La Marzocco Linea PB.",
        "slug": "espresso",
        "code": "ESP",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "ESP-SGL", "size_weight": "Single Shot (30ml)", "price_buy": d("5000"), "price_sell": d("22000")},
            {"sku": "ESP-DBL", "size_weight": "Double Shot (60ml)", "price_buy": d("8000"), "price_sell": d("28000")},
        ],
    },
    {
        "name": "Americano",
        "description": "Espresso + hot water. Clean dan bold.",
        "slug": "americano",
        "code": "AMR",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "AMR-S", "size_weight": "Small (240ml)", "price_buy": d("6000"), "price_sell": d("25000")},
            {"sku": "AMR-R", "size_weight": "Regular (350ml)", "price_buy": d("7000"), "price_sell": d("30000")},
            {"sku": "AMR-L", "size_weight": "Large (470ml)", "price_buy": d("8000"), "price_sell": d("35000")},
        ],
    },
    {
        "name": "Cappuccino",
        "description": "Espresso + steamed milk + thick milk foam. Rasio 1:1:1.",
        "slug": "cappuccino",
        "code": "CAP",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "CAP-S", "size_weight": "Small (200ml)", "price_buy": d("9000"), "price_sell": d("30000")},
            {"sku": "CAP-R", "size_weight": "Regular (280ml)", "price_buy": d("11000"), "price_sell": d("35000")},
            {"sku": "CAP-L", "size_weight": "Large (360ml)", "price_buy": d("13000"), "price_sell": d("40000")},
        ],
    },
    {
        "name": "Caffe Latte",
        "description": "Espresso + plenty of steamed milk + thin foam. Smooth dan creamy.",
        "slug": "caffe-latte",
        "code": "LAT",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "LAT-S", "size_weight": "Small (250ml)", "price_buy": d("10000"), "price_sell": d("32000")},
            {"sku": "LAT-R", "size_weight": "Regular (350ml)", "price_buy": d("12000"), "price_sell": d("37000")},
            {"sku": "LAT-L", "size_weight": "Large (470ml)", "price_buy": d("15000"), "price_sell": d("42000")},
        ],
    },
    {
        "name": "Flat White",
        "description": "Double espresso + microfoam milk. Stronger than latte, velvety texture.",
        "slug": "flat-white",
        "code": "FLW",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "FLW-R", "size_weight": "Regular (250ml)", "price_buy": d("12000"), "price_sell": d("35000")},
            {"sku": "FLW-L", "size_weight": "Large (350ml)", "price_buy": d("15000"), "price_sell": d("40000")},
        ],
    },
    {
        "name": "Mocha",
        "description": "Espresso + chocolate sauce + steamed milk + whipped cream. Sweet indulgence.",
        "slug": "mocha",
        "code": "MOC",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "MOC-S", "size_weight": "Small (250ml)", "price_buy": d("13000"), "price_sell": d("35000")},
            {"sku": "MOC-R", "size_weight": "Regular (350ml)", "price_buy": d("15000"), "price_sell": d("40000")},
            {"sku": "MOC-L", "size_weight": "Large (470ml)", "price_buy": d("18000"), "price_sell": d("45000")},
        ],
    },
    {
        "name": "Macchiato",
        "description": "Espresso 'stained' with a dash of milk foam. Bold espresso forward.",
        "slug": "macchiato",
        "code": "MAC",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "MAC-SGL", "size_weight": "Single (60ml)", "price_buy": d("6000"), "price_sell": d("24000")},
            {"sku": "MAC-DBL", "size_weight": "Double (90ml)", "price_buy": d("9000"), "price_sell": d("30000")},
        ],
    },
    {
        "name": "Affogato",
        "description": "Single espresso poured over vanilla ice cream. Classic Italian dessert-coffee.",
        "slug": "affogato",
        "code": "AFF",
        "category_slug": "espresso-based",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "AFF-R", "size_weight": "Regular (1 scoop)", "price_buy": d("14000"), "price_sell": d("38000")},
        ],
    },

    # ─────────── COLD BREW ───────────
    {
        "name": "Cold Brew",
        "description": "House Blend yang diseduh dingin selama 18 jam. Smooth, low acidity, naturally sweet.",
        "slug": "cold-brew",
        "code": "CBW",
        "category_slug": "cold-brew",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "CBW-R", "size_weight": "Regular (250ml)", "price_buy": d("10000"), "price_sell": d("35000")},
            {"sku": "CBW-L", "size_weight": "Large (400ml)", "price_buy": d("14000"), "price_sell": d("42000")},
        ],
    },
    {
        "name": "Espresso Tonic",
        "description": "Double espresso + premium tonic water + ice. Refreshing dan citrusy.",
        "slug": "espresso-tonic",
        "code": "EST",
        "category_slug": "cold-brew",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "EST-R", "size_weight": "Regular (300ml)", "price_buy": d("12000"), "price_sell": d("38000")},
        ],
    },

    # ─────────── MANUAL BREW ───────────
    {
        "name": "V60 Single Origin",
        "description": "Manual brew V60 dengan biji pilihan single origin. Disajikan panas.",
        "slug": "v60-single-origin",
        "code": "V60",
        "category_slug": "manual-brew",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "V60-TSK", "size_weight": "Toraja Sapan (250ml)", "price_buy": d("12000"), "price_sell": d("38000")},
            {"sku": "V60-GAH", "size_weight": "Gayo Red Honey (250ml)", "price_buy": d("14000"), "price_sell": d("42000")},
            {"sku": "V60-JPN", "size_weight": "Java Preanger (250ml)", "price_buy": d("13000"), "price_sell": d("40000")},
            {"sku": "V60-ETH", "size_weight": "Ethiopia Yirgacheffe (250ml)", "price_buy": d("18000"), "price_sell": d("55000")},
            {"sku": "V60-COL", "size_weight": "Colombia Huila (250ml)", "price_buy": d("16000"), "price_sell": d("48000")},
        ],
    },
    {
        "name": "French Press",
        "description": "Full immersion brew dengan French Press. Rich body, smooth. Menggunakan House Blend.",
        "slug": "french-press",
        "code": "FP",
        "category_slug": "manual-brew",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "FP-R", "size_weight": "Regular (350ml)", "price_buy": d("10000"), "price_sell": d("38000")},
        ],
    },
    {
        "name": "Aeropress",
        "description": "Pressure brew dengan Aeropress. Clean, concentrated, versatile. Single origin pilihan.",
        "slug": "aeropress",
        "code": "APR",
        "category_slug": "manual-brew",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "APR-SO", "size_weight": "Single Origin (200ml)", "price_buy": d("12000"), "price_sell": d("38000")},
        ],
    },

    # ─────────── NON-KOPI ───────────
    {
        "name": "Matcha Latte",
        "description": "Japanese ceremonial grade matcha + steamed milk. Creamy dan earthy.",
        "slug": "matcha-latte",
        "code": "MAT",
        "category_slug": "non-kopi",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "MAT-S", "size_weight": "Small (250ml)", "price_buy": d("12000"), "price_sell": d("35000")},
            {"sku": "MAT-R", "size_weight": "Regular (350ml)", "price_buy": d("15000"), "price_sell": d("40000")},
            {"sku": "MAT-L", "size_weight": "Large (470ml)", "price_buy": d("18000"), "price_sell": d("45000")},
        ],
    },
    {
        "name": "Hot Chocolate",
        "description": "Belgian dark chocolate + steamed milk + whipped cream. Rich dan indulgent.",
        "slug": "hot-chocolate",
        "code": "HCH",
        "category_slug": "non-kopi",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "HCH-S", "size_weight": "Small (250ml)", "price_buy": d("10000"), "price_sell": d("32000")},
            {"sku": "HCH-R", "size_weight": "Regular (350ml)", "price_buy": d("13000"), "price_sell": d("37000")},
            {"sku": "HCH-L", "size_weight": "Large (470ml)", "price_buy": d("16000"), "price_sell": d("42000")},
        ],
    },
    {
        "name": "Lemon Tea",
        "description": "Black tea + fresh lemon + honey. Refreshing hot atau iced.",
        "slug": "lemon-tea",
        "code": "LMT",
        "category_slug": "non-kopi",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": None,
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("0.00"),
        "min_stock": d("0.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "LMT-HOT", "size_weight": "Hot (300ml)", "price_buy": d("4000"), "price_sell": d("20000")},
            {"sku": "LMT-ICD", "size_weight": "Iced (350ml)", "price_buy": d("5000"), "price_sell": d("23000")},
        ],
    },
    {
        "name": "Mineral Water",
        "description": "Air mineral kemasan 600ml.",
        "slug": "mineral-water",
        "code": "MW",
        "category_slug": "non-kopi",
        "tax_name": "PPN 0%",
        "unit_name": "Pcs",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("200.00"),
        "min_stock": d("24.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "MW-600", "size_weight": "600 ml", "price_buy": d("2500"), "price_sell": d("8000")},
        ],
    },

    # ─────────── MAKANAN & KUE ───────────
    {
        "name": "Croissant Butter",
        "description": "Croissant classic dengan European butter. Flakey dan buttery. Dipanggang fresh setiap hari.",
        "slug": "croissant-butter",
        "code": "CRS",
        "category_slug": "makanan-kue",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("30.00"),
        "min_stock": d("5.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "CRS-PCS", "size_weight": "1 pcs", "price_buy": d("10000"), "price_sell": d("25000")},
        ],
    },
    {
        "name": "Banana Bread",
        "description": "Banana bread homemade dengan walnut dan cinnamon. Moist dan flavorful.",
        "slug": "banana-bread",
        "code": "BB",
        "category_slug": "makanan-kue",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "BB-SLC", "size_weight": "1 slice", "price_buy": d("10000"), "price_sell": d("28000")},
        ],
    },
    {
        "name": "Brownies Dark Chocolate",
        "description": "Fudgy brownies dengan Belgian dark chocolate 70%. Rich dan dense.",
        "slug": "brownies-chocolate",
        "code": "BRW",
        "category_slug": "makanan-kue",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "BRW-PCS", "size_weight": "1 pcs", "price_buy": d("8000"), "price_sell": d("22000")},
        ],
    },
    {
        "name": "Cookies Assorted",
        "description": "Cookies campuran: chocolate chip, oatmeal raisin, double chocolate. Per pcs.",
        "slug": "cookies-assorted",
        "code": "CKI",
        "category_slug": "makanan-kue",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("30.00"),
        "min_stock": d("5.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "CKI-PCS", "size_weight": "1 pcs", "price_buy": d("5000"), "price_sell": d("15000")},
        ],
    },
    {
        "name": "Club Sandwich",
        "description": "Triple decker: chicken, egg, lettuce, tomato, mayo. Dengan side salad.",
        "slug": "club-sandwich",
        "code": "CSW",
        "category_slug": "makanan-kue",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("15.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "CSW-PCS", "size_weight": "1 set", "price_buy": d("18000"), "price_sell": d("42000")},
        ],
    },

    # ─────────── BAHAN BAKU (tidak dijual langsung ke customer) ───────────
    {
        "name": "Fresh Whole Milk",
        "description": "Susu segar full cream untuk produksi minuman. 1 liter.",
        "slug": "fresh-whole-milk",
        "code": "MILK",
        "category_slug": "susu-dairy",
        "tax_name": "PPN 0%",
        "unit_name": "Liter",
        "vendor_name": "CV Fresh Dairy Indonesia",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("50.00"),
        "min_stock": d("10.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "MILK-1L", "size_weight": "1 liter", "price_buy": d("16000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Vanilla Syrup",
        "description": "Sirup vanilla premium untuk minuman. 750ml per bottle.",
        "slug": "vanilla-syrup",
        "code": "VSYR",
        "category_slug": "sirup-topping",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "CV Sugar & Syrup Nusantara",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "VSYR-750", "size_weight": "750 ml", "price_buy": d("45000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Chocolate Sauce",
        "description": "Belgian dark chocolate sauce untuk mocha, affogato, topping. 1kg per bottle.",
        "slug": "chocolate-sauce",
        "code": "CSCE",
        "category_slug": "sirup-topping",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "CV Sugar & Syrup Nusantara",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("15.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "CSCE-1K", "size_weight": "1 kg", "price_buy": d("65000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Caramel Syrup",
        "description": "Caramel syrup untuk latte, frappe. 750ml per bottle.",
        "slug": "caramel-syrup",
        "code": "CSYR",
        "category_slug": "sirup-topping",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "CV Sugar & Syrup Nusantara",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("15.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "CSYR-750", "size_weight": "750 ml", "price_buy": d("42000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Whipped Cream Liquid",
        "description": "Whipping cream cair untuk topping. 1 liter per carton.",
        "slug": "whipped-cream",
        "code": "WCRM",
        "category_slug": "susu-dairy",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "CV Fresh Dairy Indonesia",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("10.00"),
        "min_stock": d("2.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "WCRM-1L", "size_weight": "1 liter", "price_buy": d("35000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Matcha Powder Premium",
        "description": "Ceremonial grade matcha powder dari Uji, Kyoto. 100g per tin.",
        "slug": "matcha-powder",
        "code": "MPOW",
        "category_slug": "sirup-topping",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "CV Sugar & Syrup Nusantara",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("10.00"),
        "min_stock": d("2.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "MPOW-100", "size_weight": "100 gram", "price_buy": d("120000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Ice Cream Vanilla",
        "description": "Vanilla ice cream premium untuk affogato dan dessert. 2 liter per tub.",
        "slug": "ice-cream-vanilla",
        "code": "ICRM",
        "category_slug": "susu-dairy",
        "tax_name": "PPN 11%",
        "unit_name": "Pcs",
        "vendor_name": "CV Fresh Dairy Indonesia",
        "has_expiry": True,
        "is_active": True,
        "max_stock": d("8.00"),
        "min_stock": d("2.00"),
        "sell_price": None,
        "track_batch": True,
        "variants": [
            {"sku": "ICRM-2L", "size_weight": "2 liter", "price_buy": d("55000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Paper Cup 8oz",
        "description": "Gelas kertas 8oz (240ml) untuk minuman small. 1000 pcs per box.",
        "slug": "paper-cup-8oz",
        "code": "PC8",
        "category_slug": "merchandise",
        "tax_name": "PPN 0%",
        "unit_name": "Box",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "PC8-1000", "size_weight": "1000 pcs", "price_buy": d("180000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Paper Cup 12oz",
        "description": "Gelas kertas 12oz (360ml) untuk minuman regular. 1000 pcs per box.",
        "slug": "paper-cup-12oz",
        "code": "PC12",
        "category_slug": "merchandise",
        "tax_name": "PPN 0%",
        "unit_name": "Box",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "PC12-1000", "size_weight": "1000 pcs", "price_buy": d("220000"), "price_sell": d("0")},
        ],
    },
    {
        "name": "Paper Cup 16oz",
        "description": "Gelas kertas 16oz (480ml) untuk minuman large. 1000 pcs per box.",
        "slug": "paper-cup-16oz",
        "code": "PC16",
        "category_slug": "merchandise",
        "tax_name": "PPN 0%",
        "unit_name": "Box",
        "vendor_name": "PT Indo Food Supply",
        "has_expiry": False,
        "is_active": True,
        "max_stock": d("20.00"),
        "min_stock": d("3.00"),
        "sell_price": None,
        "track_batch": False,
        "variants": [
            {"sku": "PC16-1000", "size_weight": "1000 pcs", "price_buy": d("250000"), "price_sell": d("0")},
        ],
    },
]

# ---------------------------------------------------------------------------
# Initial stock per variant per location
# Format: {sku: [(location_name, qty, reserved_qty), ...]}
# Only for items we actually stock (skip bahan baku that sell_price=0 from here
# unless you want to track raw material stock too)
# ---------------------------------------------------------------------------
INITIAL_STOCK = {
    # ── Kopi Biji (di Gudang + Toko) ──
    "TSK-250": [("Gudang Jakarta", 30, 0), ("Toko Utama Kopi Lumra", 10, 0)],
    "TSK-500": [("Gudang Jakarta", 20, 0), ("Toko Utama Kopi Lumra", 5, 0)],
    "TSK-1KG": [("Gudang Jakarta", 15, 0), ("Toko Utama Kopi Lumra", 3, 0)],
    "GAH-250": [("Gudang Jakarta", 25, 0), ("Toko Utama Kopi Lumra", 8, 0)],
    "GAH-500": [("Gudang Jakarta", 18, 0), ("Toko Utama Kopi Lumra", 4, 0)],
    "GAH-1KG": [("Gudang Jakarta", 12, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "JPN-250": [("Gudang Jakarta", 20, 0), ("Toko Utama Kopi Lumra", 6, 0)],
    "JPN-500": [("Gudang Jakarta", 15, 0), ("Toko Utama Kopi Lumra", 3, 0)],
    "JPN-1KG": [("Gudang Jakarta", 10, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "SMG-250": [("Gudang Jakarta", 25, 0), ("Toko Utama Kopi Lumra", 8, 0)],
    "SMG-500": [("Gudang Jakarta", 18, 0), ("Toko Utama Kopi Lumra", 5, 0)],
    "SMG-1KG": [("Gudang Jakarta", 10, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "ETH-250": [("Gudang Jakarta", 10, 0), ("Toko Utama Kopi Lumra", 4, 0)],
    "ETH-500": [("Gudang Jakarta", 8, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "COL-250": [("Gudang Jakarta", 10, 0), ("Toko Utama Kopi Lumra", 4, 0)],
    "COL-500": [("Gudang Jakarta", 8, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "LHB-250": [("Gudang Jakarta", 40, 0), ("Toko Utama Kopi Lumra", 15, 0)],
    "LHB-500": [("Gudang Jakarta", 30, 0), ("Toko Utama Kopi Lumra", 10, 0)],
    "LHB-1KG": [("Gudang Jakarta", 20, 0), ("Toko Utama Kopi Lumra", 5, 0)],
    "LMB-250": [("Gudang Jakarta", 25, 0), ("Toko Utama Kopi Lumra", 8, 0)],
    "LMB-500": [("Gudang Jakarta", 18, 0), ("Toko Utama Kopi Lumra", 5, 0)],
    "LMB-1KG": [("Gudang Jakarta", 12, 0), ("Toko Utama Kopi Lumra", 3, 0)],
    # ── Bahan Baku (Gudang saja) ──
    "MILK-1L": [("Gudang Jakarta", 25, 0), ("Toko Utama Kopi Lumra", 8, 0)],
    "VSYR-750": [("Gudang Jakarta", 6, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "CSCE-1K": [("Gudang Jakarta", 4, 0), ("Toko Utama Kopi Lumra", 1, 0)],
    "CSYR-750": [("Gudang Jakarta", 4, 0), ("Toko Utama Kopi Lumra", 1, 0)],
    "WCRM-1L": [("Gudang Jakarta", 5, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "MPOW-100": [("Gudang Jakarta", 4, 0)],
    "ICRM-2L": [("Gudang Jakarta", 3, 0), ("Toko Utama Kopi Lumra", 1, 0)],
    "PC8-1000": [("Gudang Jakarta", 5, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "PC12-1000": [("Gudang Jakarta", 5, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    "PC16-1000": [("Gudang Jakarta", 5, 0), ("Toko Utama Kopi Lumra", 2, 0)],
    # ── Makanan (Toko saja) ──
    "CRS-PCS": [("Toko Utama Kopi Lumra", 12, 0)],
    "BB-SLC": [("Toko Utama Kopi Lumra", 8, 0)],
    "BRW-PCS": [("Toko Utama Kopi Lumra", 10, 0)],
    "CKI-PCS": [("Toko Utama Kopi Lumra", 15, 0)],
    "CSW-PCS": [("Toko Utama Kopi Lumra", 5, 0)],
    # ── Minuman (Toko saja) ──
    "MW-600": [("Toko Utama Kopi Lumra", 48, 0), ("Gudang Jakarta", 96, 0)],
}

# ---------------------------------------------------------------------------
# Product Batches — untuk biji kopi yang track_batch=True
# Format: {sku: [(batch_number, mfg_date, exp_date, qty_in, supplier_batch_no, location_name, supplier_name, notes), ...]}
# ---------------------------------------------------------------------------
PRODUCT_BATCHES = {
    "TSK-250": [
        ("TSK-250-2026-04", date(2026, 4, 1), date(2027, 4, 1), 25, "TF-2026-Q1-A", "Gudang Jakarta", "PT Toraja Sulawesi Coffee", "Roast date: 28 Mar 2026. Medium-dark."),
        ("TSK-250-2026-03", date(2026, 3, 15), date(2027, 3, 15), 8, "TF-2026-Q1-B", "Toko Utama Kopi Lumra", "PT Toraja Sulawesi Coffee", "Roast date: 12 Mar 2026. Medium-dark."),
    ],
    "TSK-500": [
        ("TSK-500-2026-04", date(2026, 4, 1), date(2027, 4, 1), 18, "TF-2026-Q1-A", "Gudang Jakarta", "PT Toraja Sulawesi Coffee", "Roast date: 28 Mar 2026."),
        ("TSK-500-2026-03", date(2026, 3, 15), date(2027, 3, 15), 5, "TF-2026-Q1-B", "Toko Utama Kopi Lumra", "PT Toraja Sulawesi Coffee", "Roast date: 12 Mar 2026."),
    ],
    "TSK-1KG": [
        ("TSK-1KG-2026-04", date(2026, 4, 1), date(2027, 4, 1), 12, "TF-2026-Q1-A", "Gudang Jakarta", "PT Toraja Sulawesi Coffee", "Roast date: 28 Mar 2026."),
        ("TSK-1KG-2026-03", date(2026, 3, 15), date(2027, 3, 15), 3, "TF-2026-Q1-B", "Toko Utama Kopi Lumra", "PT Toraja Sulawesi Coffee", "Roast date: 12 Mar 2026."),
    ],
    "GAH-250": [
        ("GAH-250-2026-04", date(2026, 4, 5), date(2027, 4, 5), 20, "GH-2026-Q1-A", "Gudang Jakarta", "CV Gayo Highland Farm", "Roast date: 2 Apr 2026. Medium roast."),
        ("GAH-250-2026-03", date(2026, 3, 20), date(2027, 3, 20), 6, "GH-2026-Q1-B", "Toko Utama Kopi Lumra", "CV Gayo Highland Farm", "Roast date: 17 Mar 2026."),
    ],
    "GAH-500": [
        ("GAH-500-2026-04", date(2026, 4, 5), date(2027, 4, 5), 15, "GH-2026-Q1-A", "Gudang Jakarta", "CV Gayo Highland Farm", "Roast date: 2 Apr 2026."),
        ("GAH-500-2026-03", date(2026, 3, 20), date(2027, 3, 20), 4, "GH-2026-Q1-B", "Toko Utama Kopi Lumra", "CV Gayo Highland Farm", "Roast date: 17 Mar 2026."),
    ],
    "GAH-1KG": [
        ("GAH-1KG-2026-04", date(2026, 4, 5), date(2027, 4, 5), 10, "GH-2026-Q1-A", "Gudang Jakarta", "CV Gayo Highland Farm", "Roast date: 2 Apr 2026."),
        ("GAH-1KG-2026-03", date(2026, 3, 20), date(2027, 3, 20), 2, "GH-2026-Q1-B", "Toko Utama Kopi Lumra", "CV Gayo Highland Farm", "Roast date: 17 Mar 2026."),
    ],
    "LHB-250": [
        ("LHB-250-2026-04A", date(2026, 4, 10), date(2027, 4, 10), 30, "INTERNAL-2026-W15", "Gudang Jakarta", None, "Roasted at Roastery Bandung. Medium-dark roast."),
        ("LHB-250-2026-04B", date(2026, 4, 10), date(2027, 4, 10), 15, "INTERNAL-2026-W15", "Toko Utama Kopi Lumra", None, "Roasted at Roastery Bandung. Medium-dark roast."),
    ],
    "LHB-500": [
        ("LHB-500-2026-04A", date(2026, 4, 10), date(2027, 4, 10), 25, "INTERNAL-2026-W15", "Gudang Jakarta", None, "Roasted at Roastery Bandung."),
        ("LHB-500-2026-04B", date(2026, 4, 10), date(2027, 4, 10), 10, "INTERNAL-2026-W15", "Toko Utama Kopi Lumra", None, "Roasted at Roastery Bandung."),
    ],
    "LHB-1KG": [
        ("LHB-1KG-2026-04A", date(2026, 4, 10), date(2027, 4, 10), 18, "INTERNAL-2026-W15", "Gudang Jakarta", None, "Roasted at Roastery Bandung."),
        ("LHB-1KG-2026-04B", date(2026, 4, 10), date(2027, 4, 10), 5, "INTERNAL-2026-W15", "Toko Utama Kopi Lumra", None, "Roasted at Roastery Bandung."),
    ],
    "LMB-250": [
        ("LMB-250-2026-04", date(2026, 4, 8), date(2027, 4, 8), 20, "INTERNAL-2026-W14", "Gudang Jakarta", None, "Medium roast. For filter brewing."),
        ("LMB-250-2026-04B", date(2026, 4, 8), date(2027, 4, 8), 8, "INTERNAL-2026-W14", "Toko Utama Kopi Lumra", None, "Medium roast. For filter brewing."),
    ],
    "LMB-500": [
        ("LMB-500-2026-04", date(2026, 4, 8), date(2027, 4, 8), 15, "INTERNAL-2026-W14", "Gudang Jakarta", None, "Medium roast."),
        ("LMB-500-2026-04B", date(2026, 4, 8), date(2027, 4, 8), 5, "INTERNAL-2026-W14", "Toko Utama Kopi Lumra", None, "Medium roast."),
    ],
    "LMB-1KG": [
        ("LMB-1KG-2026-04", date(2026, 4, 8), date(2027, 4, 8), 10, "INTERNAL-2026-W14", "Gudang Jakarta", None, "Medium roast."),
        ("LMB-1KG-2026-04B", date(2026, 4, 8), date(2027, 4, 8), 3, "INTERNAL-2026-W14", "Toko Utama Kopi Lumra", None, "Medium roast."),
    ],
    "ETH-250": [
        ("ETH-250-2026-03", date(2026, 3, 25), date(2027, 3, 25), 8, "IMP-ETH-2026-Q1", "Gudang Jakarta", "PT Toraja Sulawesi Coffee", "Import batch. Light roast for filter."),
        ("ETH-250-2026-03B", date(2026, 3, 25), date(2027, 3, 25), 4, "IMP-ETH-2026-Q1", "Toko Utama Kopi Lumra", "PT Toraja Sulawesi Coffee", "Import batch. Light roast for filter."),
    ],
    "ETH-500": [
        ("ETH-500-2026-03", date(2026, 3, 25), date(2027, 3, 25), 6, "IMP-ETH-2026-Q1", "Gudang Jakarta", "PT Toraja Sulawesi Coffee", "Import batch. Light roast."),
        ("ETH-500-2026-03B", date(2026, 3, 25), date(2027, 3, 25), 2, "IMP-ETH-2026-Q1", "Toko Utama Kopi Lumra", "PT Toraja Sulawesi Coffee", "Import batch. Light roast."),
    ],
    "COL-250": [
        ("COL-250-2026-03", date(2026, 3, 20), date(2027, 3, 20), 8, "IMP-COL-2026-Q1", "Gudang Jakarta", "PT Toraja Sulawesi Coffee", "Import batch. Medium roast."),
        ("COL-250-2026-03B", date(2026, 3, 20), date(2027, 3, 20), 4, "IMP-COL-2026-Q1", "Toko Utama Kopi Lumra", "PT Toraja Sulawesi Coffee", "Import batch. Medium roast."),
    ],
    "COL-500": [
        ("COL-500-2026-03", date(2026, 3, 20), date(2027, 3, 20), 6, "IMP-COL-2026-Q1", "Gudang Jakarta", "PT Toraja Sulawesi Coffee", "Import batch."),
        ("COL-500-2026-03B", date(2026, 3, 20), date(2027, 3, 20), 2, "IMP-COL-2026-Q1", "Toko Utama Kopi Lumra", "PT Toraja Sulawesi Coffee", "Import batch."),
    ],
    "JPN-250": [
        ("JPN-250-2026-04", date(2026, 4, 3), date(2027, 4, 3), 15, "JPE-2026-Q1-A", "Gudang Jakarta", "PT Java Preanger Estate", "Natural process. Light-medium roast."),
        ("JPN-250-2026-03", date(2026, 3, 18), date(2027, 3, 18), 6, "JPE-2026-Q1-B", "Toko Utama Kopi Lumra", "PT Java Preanger Estate", "Natural process. Light-medium roast."),
    ],
    "JPN-500": [
        ("JPN-500-2026-04", date(2026, 4, 3), date(2027, 4, 3), 12, "JPE-2026-Q1-A", "Gudang Jakarta", "PT Java Preanger Estate", "Natural process."),
        ("JPN-500-2026-03", date(2026, 3, 18), date(2027, 3, 18), 3, "JPE-2026-Q1-B", "Toko Utama Kopi Lumra", "PT Java Preanger Estate", "Natural process."),
    ],
    "SMG-250": [
        ("SMG-250-2026-04", date(2026, 4, 2), date(2027, 4, 2), 20, "MDL-2026-Q1-A", "Gudang Jakarta", "PT Mandailing Coffee Co", "Wet-hulled. Dark roast."),
        ("SMG-250-2026-03", date(2026, 3, 16), date(2027, 3, 16), 8, "MDL-2026-Q1-B", "Toko Utama Kopi Lumra", "PT Mandailing Coffee Co", "Wet-hulled. Dark roast."),
    ],
    "SMG-500": [
        ("SMG-500-2026-04", date(2026, 4, 2), date(2027, 4, 2), 15, "MDL-2026-Q1-A", "Gudang Jakarta", "PT Mandailing Coffee Co", "Wet-hulled."),
        ("SMG-500-2026-03", date(2026, 3, 16), date(2027, 3, 16), 5, "MDL-2026-Q1-B", "Toko Utama Kopi Lumra", "PT Mandailing Coffee Co", "Wet-hulled."),
    ],
    "MILK-1L": [
        ("MILK-1L-2026-04A", date(2026, 4, 14), date(2026, 4, 28), 20, "FDI-APR-2026-1", "Gudang Jakarta", "CV Fresh Dairy Indonesia", "Best before 14 days from production."),
        ("MILK-1L-2026-04B", date(2026, 4, 14), date(2026, 4, 28), 8, "FDI-APR-2026-1", "Toko Utama Kopi Lumra", "CV Fresh Dairy Indonesia", "Best before 14 days from production."),
    ],
    "WCRM-1L": [
        ("WCRM-1L-2026-03", date(2026, 3, 20), date(2026, 9, 20), 5, "FDI-MAR-2026-1", "Gudang Jakarta", "CV Fresh Dairy Indonesia", "Frozen. Use within 6 months."),
        ("WCRM-1L-2026-03B", date(2026, 3, 20), date(2026, 9, 20), 2, "FDI-MAR-2026-1", "Toko Utama Kopi Lumra", "CV Fresh Dairy Indonesia", "Frozen."),
    ],
    "MPOW-100": [
        ("MPOW-100-2026-01", date(2026, 1, 15), date(2027, 1, 15), 4, "SSN-JAN-2026", "Gudang Jakarta", "CV Sugar & Syrup Nusantara", "Uji, Kyoto. Keep refrigerated after opening."),
    ],
    "ICRM-2L": [
        ("ICRM-2L-2026-04", date(2026, 4, 10), date(2026, 10, 10), 3, "FDI-APR-2026-2", "Gudang Jakarta", "CV Fresh Dairy Indonesia", "Keep frozen. Shelf life 6 months."),
        ("ICRM-2L-2026-04B", date(2026, 4, 10), date(2026, 10, 10), 1, "FDI-APR-2026-2", "Toko Utama Kopi Lumra", "CV Fresh Dairy Indonesia", "Keep frozen."),
    ],
}

# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------
CUSTOMERS = [
    # (name, email, phone, address, city, tier, loyalty_points, total_spent, total_orders,
    #  is_active, last_order_date, customer_type)
    ("Rina Sari", "rina.sari@email.com", "08111222333",
     "Jl. Kemang Raya No.45, Kemang", "Jakarta Selatan", "gold", 2450,
     d("4520000"), 38, True, NOW - timedelta(days=2), "retail"),
    ("Budi Santoso", "budi.s@email.com", "08122333444",
     "Jl. Sudirman Kav.52, Senayan", "Jakarta Selatan", "silver", 890,
     d("1850000"), 15, True, NOW - timedelta(days=5), "retail"),
    ("PT Maju Bersama", "order@majubersama.co.id", "02155667788",
     "Jl. Gatot Subroto Kav.35, Kuningan", "Jakarta Selatan", "platinum", 12000,
     d("28500000"), 52, True, NOW - timedelta(days=1), "corporate"),
    ("Dewi Anggraini", "dewi.anggraini@email.com", "08133444555",
     "Jl. Bintaro Sektor 7, Bintaro", "Tangerang Selatan", "bronze", 220,
     d("680000"), 6, True, NOW - timedelta(days=10), "retail"),
    ("Andi Pratama", "andi.pratama@email.com", "08144555666",
     "Jl. Boulevard Raya, Kelapa Gading", "Jakarta Utara", "gold", 3200,
     d("5800000"), 45, True, NOW - timedelta(days=1), "retail"),
    ("CV Kopi Nusantara", "info@kopinusantara.co.id", "02177889900",
     "Jl. TB Simatupang No.22, Cilandak", "Jakarta Selatan", "platinum", 18500,
     d("42000000"), 78, True, NOW - timedelta(days=3), "corporate"),
    ("Siti Nurhaliza", "siti.nurhaliza@email.com", "08155666777",
     "Jl. Alun-Alun No.8, Bogor", "Bogor", "bronze", 150,
     d("420000"), 4, True, NOW - timedelta(days=15), "retail"),
    ("Reza Firmansyah", "reza.f@email.com", "08166777888",
     "Jl. Dago No.55, Bandung", "Bandung", "silver", 680,
     d("1450000"), 12, True, NOW - timedelta(days=7), "retail"),
    ("Maya Indah", "maya.indah@email.com", "08177888999",
     "Jl. Pondok Indah Raya No.12", "Jakarta Selatan", "gold", 2800,
     d("3900000"), 32, True, NOW - timedelta(days=4), "retail"),
    ("PT Digital Kreatif", "procurement@digitalkreatif.co.id", "02188990011",
     "Jl. Rasuna Said Blok X-2, Kuningan", "Jakarta Selatan", "gold", 4100,
     d("7200000"), 28, True, NOW - timedelta(days=6), "corporate"),
]

# ---------------------------------------------------------------------------
# Recipe Categories
# ---------------------------------------------------------------------------
RECIPE_CATEGORIES = [
    ("Espresso Based", "Resep minuman berbasis espresso shot", True),
    ("Manual Brew", "Resep minuman manual brewing", True),
    ("Cold Beverages", "Resep minuman dingin", True),
    ("Non-Coffee", "Resep minuman non-kopi", True),
]

# ---------------------------------------------------------------------------
# Recipes + Ingredients
# Format: (recipe_name, description, instructions, yield_qty, prep_time_min,
#          category_name, yield_unit_name, [(ingredient_sku, qty, unit_name, notes), ...])
# ---------------------------------------------------------------------------
RECIPES = [
    (
        "Espresso Doppio",
        "Double shot espresso menggunakan mesin La Marzocco Linea PB. "
        "Grind size: fine. Dose: 18g. Yield: 36ml. Time: 25-30 detik.",
        "1. Grind 18g House Blend ke fine setting\n"
        "2. Distribute dan tamp dengan pressure 15kg\n"
        "3. Lock portafilter, start extraction\n"
        "4. Target 36ml dalam 25-30 detik\n"
        "5. Serve segera dalam demitasse cup",
        d("36.00"), 3, "Espresso Based", "Mililiter",
        [
            ("LHB-250", d("18.00"), "Gram", "Dose untuk double shot"),
        ],
    ),
    (
        "Cappuccino Regular",
        "Cappuccino dengan rasio 1:1:1 (espresso:milk:foam). 280ml total.",
        "1. Pull double espresso shot (36ml)\n"
        "2. Steam 150ml whole milk ke 65°C, buat microfoam\n"
        "3. Pour milk ke cup, rasio foam dan liquid 1:1\n"
        "4. Latte art opsional (rosetta/heart)\n"
        "5. Taburkan cocoa powder di atas foam",
        d("280.00"), 5, "Espresso Based", "Mililiter",
        [
            ("LHB-250", d("18.00"), "Gram", "Double shot espresso"),
            ("MILK-1L", d("150.00"), "Mililiter", "Steamed milk"),
        ],
    ),
    (
        "Caffe Latte Regular",
        "Caffe latte dengan lebih banyak milk dan tipis foam. 350ml total.",
        "1. Pull double espresso shot (36ml)\n"
        "2. Steam 220ml whole milk ke 65°C\n"
        "3. Pour milk perlahan, ending dengan thin foam layer\n"
        "4. Latte art di tengah",
        d("350.00"), 5, "Espresso Based", "Mililiter",
        [
            ("LHB-250", d("18.00"), "Gram", "Double shot espresso"),
            ("MILK-1L", d("220.00"), "Mililiter", "Steamed milk"),
        ],
    ),
    (
        "Flat White Regular",
        "Flat white: double ristretto + velvety microfoam. Stronger than latte. 250ml.",
        "1. Pull double ristretto shot (20g dose, 30ml yield, 20 detik)\n"
        "2. Steam 150ml whole milk, microfoam sangat halus\n"
        "3. Pour dengan teknik free-pour, foam terintegrasi dengan milk\n"
        "4. Konsistensi creamy dan velvety",
        d("250.00"), 5, "Espresso Based", "Mililiter",
        [
            ("LHB-250", d("20.00"), "Gram", "Double ristretto dose"),
            ("MILK-1L", d("150.00"), "Mililiter", "Velvety steamed milk"),
        ],
    ),
    (
        "Mocha Regular",
        "Mocha: espresso + chocolate + steamed milk + whipped cream. 350ml.",
        "1. Pump 30ml chocolate sauce ke cup\n"
        "2. Pull double espresso shot, mix dengan sauce\n"
        "3. Steam 180ml whole milk ke 65°C\n"
        "4. Pour milk, aduk rata\n"
        "5. Top dengan whipped cream\n"
        "6. Drizzle chocolate sauce di atas whipped cream",
        d("350.00"), 6, "Espresso Based", "Mililiter",
        [
            ("LHB-250", d("18.00"), "Gram", "Double shot espresso"),
            ("MILK-1L", d("180.00"), "Mililiter", "Steamed milk"),
            ("CSCE-1K", d("30.00"), "Mililiter", "Chocolate sauce"),
            ("WCRM-1L", d("30.00"), "Mililiter", "Whipped cream topping"),
        ],
    ),
    (
        "Americano Regular",
        "Americano: espresso + hot water. Bold tapi clean. 350ml.",
        "1. Pull double espresso shot (36ml)\n"
        "2. Tambahkan 314ml hot water (90-95°C)\n"
        "3. Water ditambahkan SETELAH espresso untuk menjaga crema",
        d("350.00"), 3, "Espresso Based", "Mililiter",
        [
            ("LHB-250", d("18.00"), "Gram", "Double shot espresso"),
        ],
    ),
    (
        "Affogato",
        "Espresso over vanilla ice cream. Classic Italian dessert-coffee.",
        "1. Place 1 scoop vanilla ice cream (60g) di glass/cup\n"
        "2. Pull single espresso shot (30ml)\n"
        "3. Pour hot espresso langsung over ice cream\n"
        "4. Serve segera sebelum ice cream完全 mencair",
        d("90.00"), 3, "Espresso Based", "Mililiter",
        [
            ("LHB-250", d("18.00"), "Gram", "Single shot espresso"),
            ("ICRM-2L", d("60.00"), "Gram", "1 scoop vanilla ice cream"),
        ],
    ),
    (
        "V60 Toraja Sapan",
        "V60 pour over dengan Toraja Sapan Kalosi. 250ml.",
        "1. Boil water ke 93°C\n"
        "2. Grind 15g Toraja Sapan Kalosi ke medium-fine\n"
        "3. Rinse filter paper dengan hot water\n"
        "4. Bloom: 30ml water, tunggu 30 detik\n"
        "5. First pour: 60ml, circular motion\n"
        "6. Second pour: 90ml\n"
        "7. Final pour: 65ml, total ~250ml\n"
        "8. Total brew time: 2:30-3:00 menit",
        d("250.00"), 4, "Manual Brew", "Mililiter",
        [
            ("TSK-250", d("15.00"), "Gram", "Medium-fine grind"),
        ],
    ),
    (
        "V60 Ethiopia Yirgacheffe",
        "V60 pour over dengan Ethiopia Yirgacheffe. Light roast, highlight floral notes.",
        "1. Boil water ke 92°C (lebih rendah untuk light roast)\n"
        "2. Grind 15g Ethiopia Yirgacheffe ke medium-fine\n"
        "3. Rinse filter paper\n"
        "4. Bloom: 30ml, tunggu 45 detik (degassing lebih banyak)\n"
        "5. Pour dalam 3 stages, total 250ml\n"
        "6. Target brew time: 2:45-3:15 menit",
        d("250.00"), 4, "Manual Brew", "Mililiter",
        [
            ("ETH-250", d("15.00"), "Gram", "Medium-fine grind"),
        ],
    ),
    (
        "Cold Brew House Blend",
        "Cold brew 18 jam menggunakan House Blend. Smooth, low acidity.",
        "1. Grind 80g House Blend ke coarse\n"
        "2. Masukkan ke container, tambah 1000ml cold/room temp water\n"
        "3. Ratio 1:12.5\n"
        "4. Stir sekali, cover, masukkan kulkas\n"
        "5. Steep 18 jam (12-24 jam range)\n"
        "6. Filter dengan double filter (paper + fine mesh)\n"
        "7. Dilute to taste: 1 part concentrate : 1 part water/ice",
        d("1000.00"), 5, "Cold Beverages", "Mililiter",
        [
            ("LHB-250", d("80.00"), "Gram", "Coarse grind"),
        ],
    ),
    (
        "Matcha Latte Regular",
        "Matcha latte dengan ceremonial grade matcha. 350ml.",
        "1. Sift 3g matcha powder ke bowl\n"
        "2. Add 30ml hot water (80°C, BUKAN boiling)\n"
        "3. Whisk dengan chasen (bamboo whisk) sampai frothy, ~15 detik\n"
        "4. Steam 220ml milk ke 65°C\n"
        "5. Pour matcha ke cup, top dengan steamed milk\n"
        "6. Opsional: dust matcha powder di atas",
        d("350.00"), 4, "Non-Coffee", "Mililiter",
        [
            ("MPOW-100", d("3.00"), "Gram", "Ceremonial grade matcha"),
            ("MILK-1L", d("220.00"), "Mililiter", "Steamed milk"),
        ],
    ),
    (
        "Hot Chocolate Regular",
        "Hot chocolate dengan Belgian dark chocolate. 350ml.",
        "1. Heat 200ml milk di saucepan ke 70°C\n"
        "2. Add 30ml chocolate sauce, whisk sampai tercampur rata\n"
        "3. Pour ke cup\n"
        "4. Top dengan whipped cream\n"
        "5. Drizzle chocolate sauce di atas",
        d("350.00"), 5, "Non-Coffee", "Mililiter",
        [
            ("MILK-1L", d("200.00"), "Mililiter", "Heated milk"),
            ("CSCE-1K", d("30.00"), "Mililiter", "Belgian dark chocolate sauce"),
            ("WCRM-1L", d("25.00"), "Mililiter", "Whipped cream topping"),
        ],
    ),
]


# ============================================================================
# COMMAND
# ============================================================================
class Command(BaseCommand):
    help = "Seed database dengan data kopi lengkap untuk Lumra POS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true",
            help="Hapus semua data seed sebelum insert (DANGEROUS!)",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Tampilkan apa yang akan di-insert tanpa benar-benar insert",
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.clear = options["clear"]
        self.stats = {}

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  KOPI LUMRA - DATABASE SEED"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        if self.dry_run:
            self.stdout.write(self.style.WARNING("  [DRY RUN] MODE - tidak ada data yang diubah"))
        if self.clear:
            self.stdout.write(self.style.ERROR("  [CLEAR] MODE - semua data seed akan dihapus!"))

        self.stdout.write("")

        try:
            self._seed_user_and_store()
            self._seed_categories()
            self._seed_units()
            self._seed_taxes()
            self._seed_vendors()
            self._seed_locations()
            self._seed_user_profile()
            self._seed_products()
            self._seed_batches()
            self._seed_stock()
            self._seed_customers()
            self._seed_recipe_categories()
            self._seed_recipes()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n[ERROR]: {e}"))
            raise

        self._print_summary()

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _create(self, model, defaults, lookup=None, key="name"):
        """get_or_create wrapper yang支持 dry-run."""
        if lookup is None:
            lookup = {key: defaults[key]}
        if self.dry_run:
            self.stdout.write(f"    [DRY] {model.__name__}: {defaults.get(key, lookup)}")
            return None, True
        obj, created = model.objects.get_or_create(defaults=defaults, **lookup)
        status = "CREATED" if created else "EXISTS"
        color = self.style.SUCCESS if created else self.style.WARNING
        self.stdout.write(f"    {color(f'[{status}]')} {model.__name__}: {obj}")
        return obj, created

    def _get(self, model, **kwargs):
        """Safe get dengan error message jelas."""
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            available = list(model.objects.values_list("name", flat=True)[:10])
            raise ValueError(
                f"{model.__name__} tidak ditemukan dengan {kwargs}. "
                f"Available: {available}..."
            )

    def _count(self, label):
        return self.stats.get(label, 0)

    def _inc(self, label, n=1):
        self.stats[label] = self._count(label) + n

    # ------------------------------------------------------------------
    # 1. User + Store
    # ------------------------------------------------------------------
    def _seed_user_and_store(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 1] User & Store"))

        if self.clear and not self.dry_run:
            Store.objects.filter(name="Kopi Lumra").delete()
            User.objects.filter(username="admin_lumra").delete()

        if not self.dry_run:
            user, created = User.objects.get_or_create(
                username="admin_lumra",
                defaults={
                    "first_name": "Admin",
                    "last_name": "Lumra",
                    "email": "admin@kopilumra.co.id",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                },
            )
            if created:
                user.set_password("admin123")
                user.save()
            self.stdout.write(f"    [{'CREATED' if created else 'EXISTS'}] User: {user.username}")
            self._inc("users", 1 if created else 0)

            store, created = Store.objects.get_or_create(
                name="Kopi Lumra",
                defaults={
                    "subdomain": "kopilumra",
                    "business_type": "coffee_shop",
                    "description": "Specialty Coffee Shop & Roastery — Jakarta Selatan",
                    "logo_url": "/logo/lumra-logo.svg",
                    "is_active": True,
                    "plan": "premium",
                    "owner": user,
                    "created_at": NOW,
                    "updated_at": NOW,
                },
            )
            self.stdout.write(f"    [{'CREATED' if created else 'EXISTS'}] Store: {store.name}")
            self._inc("stores", 1 if created else 0)
        else:
            self.stdout.write("    [DRY] User: admin_lumra")
            self.stdout.write("    [DRY] Store: Kopi Lumra")

    # ------------------------------------------------------------------
    # 2. Categories
    # ------------------------------------------------------------------
    def _seed_categories(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 2] Categories"))

        if self.clear and not self.dry_run:
            Categories.objects.filter(slug__in=[c[2] for c in CATEGORIES]).delete()

        self._cat_map = {}  # slug -> instance
        for name, desc, slug, code, icon, is_active, parent_slug in CATEGORIES:
            parent = self._cat_map.get(parent_slug) if parent_slug else None
            defaults = {
                "name": name,
                "description": desc,
                "code": code,
                "icon_url": icon,
                "is_active": is_active,
                "created_at": NOW,
                "updated_at": NOW,
                "parent": parent,
            }
            obj, created = self._create(Category, defaults, lookup={"slug": slug}, key="slug")
            if obj:
                self._cat_map[slug] = obj
            self._inc("categories", 1 if created else 0)

    # ------------------------------------------------------------------
    # 3. Units
    # ------------------------------------------------------------------
    def _seed_units(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 3] Units"))

        if self.clear and not self.dry_run:
            Units.objects.filter(name__in=[u[0] for u in UNITS]).delete()

        self._unit_map = {}
        for name, symbol, desc, is_active in UNITS:
            defaults = {
                "symbol": symbol,
                "description": desc,
                "is_active": is_active,
                "created_at": NOW,
            }
            obj, created = self._create(Unit, defaults)
            if obj:
                self._unit_map[name] = obj
            self._inc("units", 1 if created else 0)

    # ------------------------------------------------------------------
    # 4. Taxes
    # ------------------------------------------------------------------
    def _seed_taxes(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 4] Taxes"))

        if self.clear and not self.dry_run:
            Tax.objects.filter(name__in=[t[0] for t in TAXES]).delete()

        self._tax_map = {}
        for name, rate, desc, is_active in TAXES:
            defaults = {
                "name": name,
                "rate": rate,
                "description": desc,
                "is_active": is_active,
                "created_at": NOW,
            }
            obj, created = self._create(Tax, defaults)
            if obj:
                self._tax_map[name] = obj
            self._inc("taxes", 1 if created else 0)

    # ------------------------------------------------------------------
    # 5. Vendors
    # ------------------------------------------------------------------
    def _seed_vendors(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 5] Vendors"))

        if self.clear and not self.dry_run:
            Vendor.objects.filter(name__in=[v[0] for v in VENDORS]).delete()

        self._vendor_map = {}
        for name, cp, phone, code, email, addr, web, tax_no, is_active in VENDORS:
            defaults = {
                "name": name,
                "contact_person": cp,
                "phone": phone,
                "code": code,
                "email": email,
                "address": addr,
                "website": web,
                "tax_number": tax_no,
                "is_active": is_active,
                "created_at": NOW,
                "updated_at": NOW,
            }
            obj, created = self._create(Vendor, defaults)
            if obj:
                self._vendor_map[name] = obj
            self._inc("vendors", 1 if created else 0)

    # ------------------------------------------------------------------
    # 6. Locations
    # ------------------------------------------------------------------
    def _seed_locations(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 6] Locations"))

        if self.clear and not self.dry_run:
            Location.objects.filter(name__in=[l[0] for l in LOCATIONS]).delete()

        self._loc_map = {}
        for name, addr, loc_type in LOCATIONS:
            defaults = {
                "address": addr,
                "location_type": loc_type,
                "created_at": NOW,
            }
            obj, created = self._create(Location, defaults)
            if obj:
                self._loc_map[name] = obj
            self._inc("locations", 1 if created else 0)

    # ------------------------------------------------------------------
    # 7. UserProfile
    # ------------------------------------------------------------------
    def _seed_user_profile(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 7] UserProfile"))

        if self.dry_run:
            self.stdout.write("    [DRY] UserProfile: admin_lumra")
            return

        try:
            user = User.objects.get(username="admin_lumra")
            main_store = self._get(Location, name="Toko Utama Kopi Lumra")
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "location": main_store,
                    "default_location_id": main_store,
                    "is_active": True,
                    "role": "admin",
                },
            )
            status = "CREATED" if created else "EXISTS"
            self.stdout.write(f"    [{status}] UserProfile: {user.username} ({profile.role})")
            self._inc("profiles", 1 if created else 0)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"    SKIP UserProfile: {e}"))

    # ------------------------------------------------------------------
    # 8. Products + Variants
    # ------------------------------------------------------------------
    def _seed_products(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 8] Products & Variants"))

        if self.clear and not self.dry_run:
            slugs = [p["slug"] for p in PRODUCTS]
            Product.objects.filter(slug__in=slugs).delete()

        self._product_map = {}  # slug -> product instance
        self._variant_map = {}  # sku -> variant instance

        for pdef in PRODUCTS:
            # Resolve FKs
            category = self._cat_map.get(pdef["category_slug"])
            tax = self._tax_map.get(pdef["tax_name"])
            unit = self._unit_map.get(pdef["unit_name"])
            vendor = self._vendor_map.get(pdef["vendor_name"]) if pdef["vendor_name"] else None

            if not self.dry_run:
                if category is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    SKIP Product '{pdef['name']}': "
                            f"category '{pdef['category_slug']}' not found"
                        )
                    )
                    continue

            product_defaults = {
                "name": pdef["name"],
                "description": pdef["description"],
                "code": pdef["code"],
                "category": category,
                "tax": tax,
                "unit": unit,
                "vendor": vendor,
                "has_expiry": pdef["has_expiry"],
                "is_active": pdef["is_active"],
                "max_stock": pdef["max_stock"],
                "min_stock": pdef["min_stock"],
                "sell_price": pdef["sell_price"],
                "track_batch": pdef["track_batch"],
                "created_at": NOW,
                "updated_at": NOW,
            }

            product, p_created = self._create(
                Product, product_defaults, lookup={"slug": pdef["slug"]}, key="slug"
            )
            if product:
                self._product_map[pdef["slug"]] = product
            self._inc("products", 1 if p_created else 0)

            # Variants
            for vdef in pdef.get("variants", []):
                if product is None:
                    break
                v_defaults = {
                    "size_weight": vdef["size_weight"],
                    "price_buy": vdef["price_buy"],
                    "price_sell": vdef["price_sell"],
                    "product": product,
                    "updated_at": NOW,
                }
                variant, v_created = self._create(
                    ProductVariant, v_defaults, lookup={"sku": vdef["sku"]}, key="sku"
                )
                if variant:
                    self._variant_map[vdef["sku"]] = variant
                self._inc("variants", 1 if v_created else 0)

    # ------------------------------------------------------------------
    # 9. Product Batches
    # ------------------------------------------------------------------
    def _seed_batches(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 9] Product Batches"))

        for sku, batches in PRODUCT_BATCHES.items():
            variant = self._variant_map.get(sku)
            if variant is None:
                if not self.dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"    SKIP batch for {sku}: variant not found")
                    )
                continue

            for batch_no, mfg, exp, qty_in, sup_batch, loc_name, sup_name, notes in batches:
                location = self._loc_map.get(loc_name)
                supplier = self._vendor_map.get(sup_name) if sup_name else None

                if location is None:
                    self.stdout.write(
                        self.style.WARNING(f"    SKIP batch {batch_no}: location '{loc_name}' not found")
                    )
                    continue

                defaults = {
                    "batch_number": batch_no,
                    "manufacturing_date": mfg,
                    "expiry_date": exp,
                    "quantity_in": d(str(qty_in)),
                    "quantity_available": d(str(qty_in)),
                    "supplier_batch_number": sup_batch,
                    "notes": notes,
                    "product": variant,
                    "location": location,
                    "supplier": supplier,
                    "created_at": NOW,
                    "updated_at": NOW,
                }
                obj, created = self._create(
                    ProductBatch, defaults,
                    lookup={"product": variant, "batch_number": batch_no, "location": location},
                    key="batch_number",
                )
                self._inc("batches", 1 if created else 0)

    # ------------------------------------------------------------------
    # 10. Stock
    # ------------------------------------------------------------------
    def _seed_stock(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 10] Stock"))

        for sku, entries in INITIAL_STOCK.items():
            variant = self._variant_map.get(sku)
            if variant is None:
                if not self.dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"    SKIP stock for {sku}: variant not found")
                    )
                continue

            for loc_name, qty, reserved in entries:
                location = self._loc_map.get(loc_name)
                if location is None:
                    self.stdout.write(
                        self.style.WARNING(f"    SKIP stock {sku}@{loc_name}: location not found")
                    )
                    continue

                defaults = {
                    "quantity": qty,
                    "transaction_type": "initial",
                    "notes": "Initial stock from seed data",
                    "reserved_quantity": d(str(reserved)),
                    "variant": variant,
                    "location": location,
                    "last_updated": NOW,
                    "created_at": NOW,
                }
                obj, created = self._create(
                    Stock, defaults,
                    lookup={"variant": variant, "location": location},
                    key=None,
                )
                self._inc("stock", 1 if created else 0)

    # ------------------------------------------------------------------
    # 11. Customers
    # ------------------------------------------------------------------
    def _seed_customers(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 11] Customers"))

        if self.clear and not self.dry_run:
            emails = [c[1] for c in CUSTOMERS]
            Customer.objects.filter(email__in=emails).delete()

        for (name, email, phone, addr, city, tier, points,
             total_spent, total_orders, is_active, last_order, ctype) in CUSTOMERS:
            defaults = {
                "name": name,
                "phone": phone,
                "address": addr,
                "city": city,
                "tier": tier,
                "loyalty_points": points,
                "total_spent": total_spent,
                "total_orders": total_orders,
                "is_active": is_active,
                "created_at": NOW - timedelta(days=180),
                "updated_at": NOW,
                "last_order_date": last_order,
                "customer_type": ctype,
            }
            obj, created = self._create(
                Customer, defaults, lookup={"email": email}, key="email"
            )
            self._inc("customers", 1 if created else 0)

    # ------------------------------------------------------------------
    # 12. Recipe Categories
    # ------------------------------------------------------------------
    def _seed_recipe_categories(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 12] Recipe Categories"))

        if self.clear and not self.dry_run:
            RecipeCategory.objects.filter(name__in=[r[0] for r in RECIPE_CATEGORIES]).delete()

        self._rcat_map = {}
        for name, desc, is_active in RECIPE_CATEGORIES:
            defaults = {
                "description": desc,
                "is_active": is_active,
                "created_at": NOW,
                "updated_at": NOW,
            }
            obj, created = self._create(RecipeCategory, defaults)
            if obj:
                self._rcat_map[name] = obj
            self._inc("recipe_categories", 1 if created else 0)

    # ------------------------------------------------------------------
    # 13. Recipes + Ingredients
    # ------------------------------------------------------------------
    def _seed_recipes(self):
        self.stdout.write(self.style.HTTP_INFO("\n[Step 13] Recipes & Ingredients"))

        for (rname, rdesc, rinstr, ryield, rtime,
             cat_name, yield_unit_name, ingredients) in RECIPES:

            category = self._rcat_map.get(cat_name)
            yield_unit = self._unit_map.get(yield_unit_name)

            if category is None or yield_unit is None:
                self.stdout.write(
                    self.style.WARNING(f"    SKIP Recipe '{rname}': category or unit not found")
                )
                continue

            # Hitung total cost & cost per unit
            total_cost = d("0")
            for ing_sku, ing_qty, ing_unit_name, ing_notes in ingredients:
                variant = self._variant_map.get(ing_sku)
                if variant:
                    # cost = (price_buy / qty_per_unit) * qty_used
                    # Untuk biji kopi: price_buy per pack, kita asumsi pack = 250g
                    # Jadi cost per gram = price_buy / 250
                    unit_obj = self._unit_map.get(ing_unit_name)
                    cost_per_ing = d("0")
                    if ing_unit_name == "Gram" and "250" in variant.sku:
                        cost_per_ing = (variant.price_buy / d("250")) * ing_qty
                    elif ing_unit_name == "Gram" and "500" in variant.sku:
                        cost_per_ing = (variant.price_buy / d("500")) * ing_qty
                    elif ing_unit_name == "Gram" and "1KG" in variant.sku:
                        cost_per_ing = (variant.price_buy / d("1000")) * ing_qty
                    elif ing_unit_name == "Mililiter" and "1L" in variant.sku:
                        cost_per_ing = (variant.price_buy / d("1000")) * ing_qty
                    elif ing_unit_name == "Mililiter" and "750" in variant.sku:
                        cost_per_ing = (variant.price_buy / d("750")) * ing_qty
                    elif ing_unit_name == "Mililiter" and "1K" in variant.sku:
                        # chocolate sauce 1kg ≈ 1000ml
                        cost_per_ing = (variant.price_buy / d("1000")) * ing_qty
                    elif ing_unit_name == "Gram" and "100" in variant.sku:
                        cost_per_ing = (variant.price_buy / d("100")) * ing_qty
                    elif ing_unit_name == "Gram" and "2L" in variant.sku:
                        # ice cream: 2 liter ≈ 2000g
                        cost_per_ing = (variant.price_buy / d("2000")) * ing_qty
                    else:
                        cost_per_ing = variant.price_buy * (ing_qty / d("1"))
                    total_cost += cost_per_ing.quantize(d("0.01"), rounding=ROUND_HALF_UP)

            cost_per_unit = (total_cost / ryield).quantize(d("0.01"), rounding=ROUND_HALF_UP) if ryield > 0 else d("0")

            recipe_defaults = {
                "name": rname,
                "description": rdesc,
                "instructions": rinstr,
                "yield_quantity": ryield,
                "preparation_time": rtime,
                "total_cost": total_cost,
                "cost_per_unit": cost_per_unit,
                "is_archived": False,
                "category": category,
                "yield_unit": yield_unit,
                "created_at": NOW,
                "updated_at": NOW,
            }
            recipe, r_created = self._create(Recipe, recipe_defaults)
            self._inc("recipes", 1 if r_created else 0)

            # Ingredients
            if recipe is None:
                continue
            for ing_sku, ing_qty, ing_unit_name, ing_notes in ingredients:
                variant = self._variant_map.get(ing_sku)
                unit = self._unit_map.get(ing_unit_name)
                if variant is None or unit is None:
                    continue

                # Recalculate unit_cost for this ingredient
                unit_cost = d("0")
                if ing_unit_name == "Gram" and "250" in variant.sku:
                    unit_cost = (variant.price_buy / d("250")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                elif ing_unit_name == "Gram" and "500" in variant.sku:
                    unit_cost = (variant.price_buy / d("500")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                elif ing_unit_name == "Gram" and "1KG" in variant.sku:
                    unit_cost = (variant.price_buy / d("1000")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                elif ing_unit_name == "Mililiter" and "1L" in variant.sku:
                    unit_cost = (variant.price_buy / d("1000")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                elif ing_unit_name == "Mililiter" and "750" in variant.sku:
                    unit_cost = (variant.price_buy / d("750")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                elif ing_unit_name == "Mililiter" and "1K" in variant.sku:
                    unit_cost = (variant.price_buy / d("1000")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                elif ing_unit_name == "Gram" and "100" in variant.sku:
                    unit_cost = (variant.price_buy / d("100")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                elif ing_unit_name == "Gram" and "2L" in variant.sku:
                    unit_cost = (variant.price_buy / d("2000")).quantize(d("0.01"), rounding=ROUND_HALF_UP)
                else:
                    unit_cost = variant.price_buy

                subtotal = (unit_cost * ing_qty).quantize(d("0.01"), rounding=ROUND_HALF_UP)

                ing_defaults = {
                    "quantity": ing_qty,
                    "unit_cost": unit_cost,
                    "subtotal_cost": subtotal,
                    "notes": ing_notes,
                    "recipe": recipe,
                    "variant": variant,
                    "unit": unit,
                    "created_at": NOW,
                }
                obj, i_created = self._create(
                    RecipeIngredient, ing_defaults,
                    lookup={"recipe": recipe, "variant": variant},
                    key=None,
                )
                self._inc("recipe_ingredients", 1 if i_created else 0)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    def _print_summary(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("  📊 SEED SUMMARY"))
        self.stdout.write("=" * 60)

        items = [
            ("Users", "users"),
            ("Stores", "stores"),
            ("Categories", "categories"),
            ("Units", "units"),
            ("Taxes", "taxes"),
            ("Vendors", "vendors"),
            ("Locations", "locations"),
            ("User Profiles", "profiles"),
            ("Products", "products"),
            ("Product Variants", "variants"),
            ("Product Batches", "batches"),
            ("Stock Records", "stock"),
            ("Customers", "customers"),
            ("Recipe Categories", "recipe_categories"),
            ("Recipes", "recipes"),
            ("Recipe Ingredients", "recipe_ingredients"),
        ]

        total = 0
        for label, key in items:
            n = self._count(key)
            total += n
            self.stdout.write(f"    {label:<25} {n:>4}")

        self.stdout.write("    " + "-" * 30)
        self.stdout.write(self.style.SUCCESS(f"    {'TOTAL':<25} {total:>4}"))

        if self.dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("  [DRY RUN] - jalankan tanpa --dry-run untuk insert sebenarnya"))

        self.stdout.write("")