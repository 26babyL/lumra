"""
Comprehensive Dummy Data Seeder untuk Lumra Coffee Shop
========================================================
Mengisi database dengan dummy data untuk sistem kopi shop lengkap.

Theme: Coffee shops seperti Starbucks, Kopi Kenangan, Janji Jiwa, Point Coffee
Data: Multiple stores, thousands of customers, staff, products, sales history

Run:
  python manage.py seed_comprehensive_data
  python manage.py seed_comprehensive_data --clear     (hapus data lama dulu)
  python manage.py seed_comprehensive_data --products  (hanya products)
  python manage.py seed_comprehensive_data --customers (hanya customers)
"""

import json
import random
from decimal import Decimal as D
from datetime import date, timedelta, datetime
from typing import List, Dict, Tuple

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from lumra_config.models import (
    Category, Tax, Unit, Vendor, Location, Product, ProductVariant,
    Customer, UserProfile, Role, User as LumraUser,
)

User = get_user_model()

# ============================================================================
# INDONESIAN COFFEE SHOP DATA - Starbucks, Kopi Kenangan, Janji Jiwa Style
# ============================================================================

STORE_LOCATIONS = [
    {
        "name": "Lumra Coffee - CBD Jakarta",
        "code": "LUM-CGK",
        "address": "Jl. Sudirman No.123, Jakarta Pusat 12190",
        "city": "Jakarta",
        "area": "CBD",
        "phone": "021-1234567-1",
        "type": "store",
        "latitude": "-6.1944",
        "longitude": "106.8296",
    },
    {
        "name": "Lumra Coffee - Senayan",
        "code": "LUM-SEN",
        "address": "Jl. Benda No.45, Kemang, Jakarta Selatan 12560",
        "city": "Jakarta",
        "area": "Kemang",
        "phone": "021-1234567-2",
        "type": "store",
        "latitude": "-6.2647",
        "longitude": "106.7763",
    },
    {
        "name": "Lumra Coffee - Bandung",
        "code": "LUM-BDG",
        "address": "Jl. Riau No.88, Bandung 40113",
        "city": "Bandung",
        "area": "Dago",
        "phone": "0274-1234567-1",
        "type": "store",
        "latitude": "-6.8957",
        "longitude": "107.6338",
    },
    {
        "name": "Lumra Coffee - Surabaya",
        "code": "LUM-SBY",
        "address": "Jl. Ngagel Rejo No.56, Surabaya 60188",
        "city": "Surabaya",
        "area": "Ngagel",
        "phone": "031-1234567-1",
        "type": "store",
        "latitude": "-7.2575",
        "longitude": "112.7521",
    },
    {
        "name": "Lumra Coffee - Medan",
        "code": "LUM-MDN",
        "address": "Jl. Katamso No.234, Medan 20233",
        "city": "Medan",
        "area": "Pusat",
        "phone": "061-1234567-1",
        "type": "store",
        "latitude": "3.5952",
        "longitude": "98.6722",
    },
    {
        "name": "Lumra Roastery - Jakarta",
        "code": "LUM-ROAST-JKT",
        "address": "Jl. Industri No.22, Cikarang, Bekasi 17530",
        "city": "Bekasi",
        "area": "Industrial",
        "phone": "021-1234567-R",
        "type": "roastery",
        "latitude": "-6.1300",
        "longitude": "107.1500",
    },
    {
        "name": "Lumra Warehouse - Depok",
        "code": "LUM-WH-DPK",
        "address": "Jl. Raya Bogor Km.32, Depok 16411",
        "city": "Depok",
        "area": "Warehouse",
        "phone": "021-1234567-W",
        "type": "warehouse",
        "latitude": "-6.4000",
        "longitude": "106.8000",
    },
]

VENDORS_DATA = [
    {
        "name": "PT Toraja Sulawesi Coffee",
        "code": "TOR",
        "contact_person": "Pak Budi",
        "phone": "+62-812-3456-7001",
        "email": "budi@torajacoffee.co.id",
        "address": "Jl. Sa'dan No.12, Rantepao, Toraja, Sulawesi Selatan 71211",
        "city": "Toraja",
        "province": "Sulawesi Selatan",
        "tax_number": "02.123.456.7-001.000",
        "type": "supplier_kopi",
    },
    {
        "name": "CV Gayo Highland Farm",
        "code": "GAY",
        "contact_person": "Ibu Ratna",
        "phone": "+62-812-3456-7002",
        "email": "ratna@gayohighland.co.id",
        "address": "Jl. Takengon-Bireuen Km.5, Takengon, Aceh Tengah 24511",
        "city": "Takengon",
        "province": "Aceh",
        "tax_number": "02.123.456.7-002.000",
        "type": "supplier_kopi",
    },
    {
        "name": "PT Java Preanger Estate",
        "code": "JPE",
        "contact_person": "Pak Hendra",
        "phone": "+62-812-3456-7003",
        "email": "hendra@javapreanger.co.id",
        "address": "Jl. Perkebunan No.8, Pangalengan, Bandung, Jawa Barat 40378",
        "city": "Bandung",
        "province": "Jawa Barat",
        "tax_number": "02.123.456.7-003.000",
        "type": "supplier_kopi",
    },
    {
        "name": "PT Mandailing Coffee Co",
        "code": "MDL",
        "contact_person": "Pak Surya",
        "phone": "+62-812-3456-7004",
        "email": "surya@mandailingcoffee.co.id",
        "address": "Jl. Lintas Sumatera No.45, Mandailing Natal, Sumatera Utara",
        "city": "Mandailing",
        "province": "Sumatera Utara",
        "tax_number": "02.123.456.7-004.000",
        "type": "supplier_kopi",
    },
    {
        "name": "CV Fresh Dairy Indonesia",
        "code": "FDI",
        "contact_person": "Ibu Maya",
        "phone": "+62-812-3456-7005",
        "email": "maya@freshdairy.co.id",
        "address": "Jl. Raya Bogor Km.28, Ciomas, Bogor, Jawa Barat 16610",
        "city": "Bogor",
        "province": "Jawa Barat",
        "tax_number": "02.123.456.7-005.000",
        "type": "supplier_dairy",
    },
    {
        "name": "PT Indo Food Supply",
        "code": "IFS",
        "contact_person": "Pak Doni",
        "phone": "+62-812-3456-7006",
        "email": "doni@indofoodsupply.co.id",
        "address": "Jl. Industri No.22, Cikarang, Bekasi, Jawa Barat 17530",
        "city": "Bekasi",
        "province": "Jawa Barat",
        "tax_number": "02.123.456.7-006.000",
        "type": "supplier_makanan",
    },
    {
        "name": "CV Sugar & Syrup Nusantara",
        "code": "SSN",
        "contact_person": "Pak Andi",
        "phone": "+62-812-3456-7007",
        "email": "andi@sugarsyrup.co.id",
        "address": "Jl. Gula No.15, Sidoarjo, Jawa Timur 61234",
        "city": "Sidoarjo",
        "province": "Jawa Timur",
        "tax_number": "02.123.456.7-007.000",
        "type": "supplier_syrup",
    },
    {
        "name": "PT Packaging Solutions Indonesia",
        "code": "PKG",
        "contact_person": "Pak Rianto",
        "phone": "+62-812-3456-7008",
        "email": "rianto@packagingid.co.id",
        "address": "Jl. Kemasan No.99, Surabaya, Jawa Timur 60188",
        "city": "Surabaya",
        "province": "Jawa Timur",
        "tax_number": "02.123.456.7-008.000",
        "type": "supplier_packaging",
    },
]

# ============================================================================
# COFFEE PRODUCTS - Comprehensive Menu
# ============================================================================

COFFEE_PRODUCTS = [
    # ──────────── COFFEE BEANS ────────────
    {
        "name": "Toraja Sapan Kalosi Premium",
        "code": "BEAN-TOR",
        "category": "Kopi Biji - Single Origin",
        "description": "Single origin arabika dari Toraja. Dark chocolate, brown sugar, full body.",
        "unit": "Gram",
        "tax": "PPN 11%",
        "vendor": "PT Toraja Sulawesi Coffee",
        "variants": [
            {"sku": "BEAN-TOR-250", "name": "250g", "buy": 55000, "sell": 95000},
            {"sku": "BEAN-TOR-500", "name": "500g", "buy": 100000, "sell": 175000},
            {"sku": "BEAN-TOR-1KG", "name": "1kg", "buy": 185000, "sell": 330000},
        ],
    },
    {
        "name": "Gayo Red Honey Arabica",
        "code": "BEAN-GAY",
        "category": "Kopi Biji - Single Origin",
        "description": "Red honey processed dari Aceh. Red fruit, jasmine, medium body.",
        "unit": "Gram",
        "tax": "PPN 11%",
        "vendor": "CV Gayo Highland Farm",
        "variants": [
            {"sku": "BEAN-GAY-250", "name": "250g", "buy": 65000, "sell": 110000},
            {"sku": "BEAN-GAY-500", "name": "500g", "buy": 120000, "sell": 205000},
            {"sku": "BEAN-GAY-1KG", "name": "1kg", "buy": 225000, "sell": 390000},
        ],
    },
    {
        "name": "Java Preanger Natural",
        "code": "BEAN-JPR",
        "category": "Kopi Biji - Single Origin",
        "description": "Natural processed dari Bandung. Tropical fruit, citrus, floral.",
        "unit": "Gram",
        "tax": "PPN 11%",
        "vendor": "PT Java Preanger Estate",
        "variants": [
            {"sku": "BEAN-JPR-250", "name": "250g", "buy": 60000, "sell": 105000},
            {"sku": "BEAN-JPR-500", "name": "500g", "buy": 110000, "sell": 195000},
            {"sku": "BEAN-JPR-1KG", "name": "1kg", "buy": 205000, "sell": 370000},
        ],
    },
    {
        "name": "Lumra House Blend",
        "code": "BEAN-HB",
        "category": "Kopi Biji - Blended",
        "description": "Signature blend: 60% Toraja + 40% Mandheling. Perfect untuk espresso.",
        "unit": "Gram",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "BEAN-HB-250", "name": "250g", "buy": 45000, "sell": 78000},
            {"sku": "BEAN-HB-500", "name": "500g", "buy": 82000, "sell": 145000},
            {"sku": "BEAN-HB-1KG", "name": "1kg", "buy": 155000, "sell": 275000},
        ],
    },
    {
        "name": "Lumra Morning Blend",
        "code": "BEAN-MB",
        "category": "Kopi Biji - Blended",
        "description": "Morning blend: 50% Java + 30% Gayo + 20% Colombia. Medium roast.",
        "unit": "Gram",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "BEAN-MB-250", "name": "250g", "buy": 50000, "sell": 88000},
            {"sku": "BEAN-MB-500", "name": "500g", "buy": 92000, "sell": 165000},
            {"sku": "BEAN-MB-1KG", "name": "1kg", "buy": 175000, "sell": 315000},
        ],
    },

    # ──────────── HOT ESPRESSO DRINKS ────────────
    {
        "name": "Espresso",
        "code": "DRINK-ESP",
        "category": "Minuman Kopi - Espresso Based",
        "description": "Single/Double shot espresso. Bold dan concentrated.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "ESP-SGL", "name": "Single (30ml)", "buy": 5000, "sell": 22000},
            {"sku": "ESP-DBL", "name": "Double (60ml)", "buy": 8000, "sell": 28000},
        ],
    },
    {
        "name": "Americano",
        "code": "DRINK-AME",
        "category": "Minuman Kopi - Espresso Based",
        "description": "Espresso + hot water. Clean dan bold.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "AME-S", "name": "Small (240ml)", "buy": 6000, "sell": 25000},
            {"sku": "AME-R", "name": "Regular (350ml)", "buy": 7000, "sell": 30000},
            {"sku": "AME-L", "name": "Large (470ml)", "buy": 8000, "sell": 35000},
        ],
    },
    {
        "name": "Cappuccino",
        "code": "DRINK-CAP",
        "category": "Minuman Kopi - Espresso Based",
        "description": "Espresso + steamed milk + thick foam. Italian classic.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "CAP-S", "name": "Small (200ml)", "buy": 9000, "sell": 30000},
            {"sku": "CAP-R", "name": "Regular (280ml)", "buy": 11000, "sell": 35000},
            {"sku": "CAP-L", "name": "Large (360ml)", "buy": 13000, "sell": 40000},
        ],
    },
    {
        "name": "Caffe Latte",
        "code": "DRINK-LAT",
        "category": "Minuman Kopi - Espresso Based",
        "description": "Espresso + plenty steamed milk. Smooth dan creamy.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "LAT-S", "name": "Small (250ml)", "buy": 10000, "sell": 32000},
            {"sku": "LAT-R", "name": "Regular (350ml)", "buy": 12000, "sell": 37000},
            {"sku": "LAT-L", "name": "Large (470ml)", "buy": 15000, "sell": 42000},
        ],
    },
    {
        "name": "Flat White",
        "code": "DRINK-FW",
        "category": "Minuman Kopi - Espresso Based",
        "description": "Double espresso + microfoam. Velvety texture.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "FW-R", "name": "Regular (250ml)", "buy": 12000, "sell": 35000},
            {"sku": "FW-L", "name": "Large (350ml)", "buy": 15000, "sell": 40000},
        ],
    },
    {
        "name": "Mocha",
        "code": "DRINK-MOC",
        "category": "Minuman Kopi - Espresso Based",
        "description": "Espresso + chocolate + steamed milk + whipped cream.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "MOC-S", "name": "Small (250ml)", "buy": 13000, "sell": 35000},
            {"sku": "MOC-R", "name": "Regular (350ml)", "buy": 15000, "sell": 40000},
            {"sku": "MOC-L", "name": "Large (470ml)", "buy": 18000, "sell": 45000},
        ],
    },
    {
        "name": "Macchiato",
        "code": "DRINK-MAC",
        "category": "Minuman Kopi - Espresso Based",
        "description": "Espresso 'stained' with milk foam. Bold espresso forward.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "MAC-SGL", "name": "Single (60ml)", "buy": 6000, "sell": 24000},
            {"sku": "MAC-DBL", "name": "Double (90ml)", "buy": 9000, "sell": 30000},
        ],
    },

    # ──────────── COLD DRINKS ────────────
    {
        "name": "Iced Americano",
        "code": "DRINK-IAME",
        "category": "Minuman Kopi - Cold Brew",
        "description": "Espresso + water + ice. Refreshing.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "IAME-R", "name": "Regular (300ml)", "buy": 8000, "sell": 30000},
            {"sku": "IAME-L", "name": "Large (400ml)", "buy": 10000, "sell": 35000},
        ],
    },
    {
        "name": "Iced Latte",
        "code": "DRINK-ILAT",
        "category": "Minuman Kopi - Cold Brew",
        "description": "Espresso + cold milk + ice.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "ILAT-R", "name": "Regular (300ml)", "buy": 11000, "sell": 35000},
            {"sku": "ILAT-L", "name": "Large (400ml)", "buy": 13000, "sell": 40000},
        ],
    },
    {
        "name": "Iced Cappuccino",
        "code": "DRINK-ICAP",
        "category": "Minuman Kopi - Cold Brew",
        "description": "Espresso + cold milk + foam + ice.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "ICAP-R", "name": "Regular (300ml)", "buy": 12000, "sell": 36000},
            {"sku": "ICAP-L", "name": "Large (400ml)", "buy": 14000, "sell": 42000},
        ],
    },
    {
        "name": "Cold Brew",
        "code": "DRINK-CB",
        "category": "Minuman Kopi - Cold Brew",
        "description": "18-hour cold brewed. Smooth, low acidity.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "CB-R", "name": "Regular (250ml)", "buy": 10000, "sell": 35000},
            {"sku": "CB-L", "name": "Large (400ml)", "buy": 14000, "sell": 42000},
        ],
    },

    # ──────────── MANUAL BREW ────────────
    {
        "name": "V60 Single Origin",
        "code": "DRINK-V60",
        "category": "Minuman Kopi - Manual Brew",
        "description": "V60 dripper dengan single origin pilihan.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "V60-TOR", "name": "Toraja (250ml)", "buy": 12000, "sell": 38000},
            {"sku": "V60-GAY", "name": "Gayo (250ml)", "buy": 14000, "sell": 42000},
            {"sku": "V60-JPR", "name": "Java (250ml)", "buy": 13000, "sell": 40000},
        ],
    },
    {
        "name": "French Press",
        "code": "DRINK-FP",
        "category": "Minuman Kopi - Manual Brew",
        "description": "Full immersion brew. Rich body.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "FP-R", "name": "Regular (350ml)", "buy": 10000, "sell": 38000},
        ],
    },

    # ──────────── NON-COFFEE ────────────
    {
        "name": "Matcha Latte",
        "code": "DRINK-MATCHA",
        "category": "Minuman Kopi - Non Coffee",
        "description": "Ceremonial grade matcha + steamed milk.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "MATCHA-S", "name": "Small (250ml)", "buy": 12000, "sell": 35000},
            {"sku": "MATCHA-R", "name": "Regular (350ml)", "buy": 15000, "sell": 40000},
            {"sku": "MATCHA-L", "name": "Large (470ml)", "buy": 18000, "sell": 45000},
        ],
    },
    {
        "name": "Hot Chocolate",
        "code": "DRINK-HC",
        "category": "Minuman Kopi - Non Coffee",
        "description": "Belgian dark chocolate + steamed milk.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": None,
        "variants": [
            {"sku": "HC-S", "name": "Small (250ml)", "buy": 10000, "sell": 32000},
            {"sku": "HC-R", "name": "Regular (350ml)", "buy": 13000, "sell": 37000},
            {"sku": "HC-L", "name": "Large (470ml)", "buy": 16000, "sell": 42000},
        ],
    },
    {
        "name": "Mineral Water",
        "code": "DRINK-WATER",
        "category": "Minuman Kopi - Non Coffee",
        "description": "Mineral water 600ml.",
        "unit": "Pcs",
        "tax": "PPN 0%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "WATER-600", "name": "600ml", "buy": 2500, "sell": 8000},
        ],
    },

    # ──────────── PASTRY & FOOD ────────────
    {
        "name": "Croissant Butter",
        "code": "FOOD-CRS",
        "category": "Makanan & Kue - Pastry",
        "description": "Butter croissant. Flakey dan buttery.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "CRS-1", "name": "1 pcs", "buy": 10000, "sell": 25000},
        ],
    },
    {
        "name": "Banana Bread",
        "code": "FOOD-BB",
        "category": "Makanan & Kue - Pastry",
        "description": "Banana bread homemade. Moist.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "BB-1", "name": "1 slice", "buy": 10000, "sell": 28000},
        ],
    },
    {
        "name": "Brownies Dark Chocolate",
        "code": "FOOD-BRW",
        "category": "Makanan & Kue - Pastry",
        "description": "Fudgy brownies Belgian chocolate.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "BRW-1", "name": "1 pcs", "buy": 8000, "sell": 22000},
        ],
    },
    {
        "name": "Blueberry Muffin",
        "code": "FOOD-MUFF",
        "category": "Makanan & Kue - Pastry",
        "description": "Fresh blueberry muffin.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "MUFF-1", "name": "1 pcs", "buy": 9000, "sell": 24000},
        ],
    },
    {
        "name": "Cheese Cake Slice",
        "code": "FOOD-CHEESECAKE",
        "category": "Makanan & Kue - Pastry",
        "description": "Creamy New York cheesecake.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "CHEESECAKE-1", "name": "1 slice", "buy": 12000, "sell": 35000},
        ],
    },
    {
        "name": "Club Sandwich",
        "code": "FOOD-CLUB",
        "category": "Makanan & Kue - Savory",
        "description": "Triple decker: chicken, egg, lettuce, tomato.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "CLUB-1", "name": "1 set", "buy": 18000, "sell": 42000},
        ],
    },
    {
        "name": "Caesar Salad",
        "code": "FOOD-SALAD",
        "category": "Makanan & Kue - Savory",
        "description": "Fresh caesar salad dengan croutons.",
        "unit": "Pcs",
        "tax": "PPN 11%",
        "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "SALAD-1", "name": "1 portion", "buy": 15000, "sell": 38000},
        ],
    },
]

# ============================================================================
# INDONESIAN NAMES FOR CUSTOMERS & STAFF
# ============================================================================

FIRST_NAMES = [
    "Ahmad", "Budi", "Citra", "Dian", "Eka", "Farah", "Gita", "Hendra",
    "Indra", "Joko", "Kunia", "Lina", "Musa", "Nita", "Oka", "Putri",
    "Reza", "Siti", "Toni", "Usman", "Vina", "Wawan", "Xiaomin", "Yoni",
    "Zahra", "Aditya", "Bagas", "Cahya", "Desy", "Emy", "Firman", "Gara",
    "Hana", "Irfan", "Jaya", "Karen", "Luki", "Maya", "Nando", "Obi",
    "Prita", "Qori", "Raja", "Sasha", "Tania", "Uddin", "Vanessa", "Widi",
]

LAST_NAMES = [
    "Wijaya", "Rahman", "Santoso", "Nurdin", "Kusuma", "Gunawan", "Setiawan",
    "Handoko", "Saputra", "Hidayat", "Suryanto", "Hartono", "Lestari", "Dewi",
    "Putri", "Amelia", "Rahayu", "Suharto", "Permana", "Utama", "Jatna", "Kurnia",
]

INDONESIAN_EMAILS = [
    "@gmail.com", "@outlook.com", "@yahoo.com", "@hotmail.com", "@telkomsel.co.id",
    "@indosat.co.id", "@axistelstra.com", "@3indo.co.id",
]

INDONESIAN_CITIES = [
    "Jakarta", "Bandung", "Surabaya", "Medan", "Semarang", "Makassar", "Palembang",
    "Yogyakarta", "Bogor", "Bekasi", "Tangerang", "Depok", "Cirebon", "Pekanbaru",
]


def generate_name() -> str:
    """Generate Indonesian name."""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def generate_email() -> str:
    """Generate email from name."""
    name = generate_name().lower().replace(" ", "")
    domain = random.choice(INDONESIAN_EMAILS)
    number = random.randint(1, 999)
    return f"{name}{number}{domain}"


def generate_phone() -> str:
    """Generate Indonesian phone number."""
    operators = ["0812", "0813", "0814", "0815", "0816", "0817", "0818", "0819",
                 "0821", "0822", "0823", "0851", "0852", "0853", "0854"]
    operator = random.choice(operators)
    number = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{operator}{number}"


# ============================================================================
# COMMAND
# ============================================================================

class Command(BaseCommand):
    help = "Seed database dengan comprehensive dummy data untuk coffee shop"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true",
            help="Hapus semua data sebelum insert",
        )
        parser.add_argument(
            "--customers-only", action="store_true",
            help="Hanya seed customers",
        )
        parser.add_argument(
            "--products-only", action="store_true",
            help="Hanya seed products",
        )
        parser.add_argument(
            "--num-customers", type=int, default=5000,
            help="Jumlah customers yang akan dibuat (default: 5000)",
        )

    def handle(self, *args, **options):
        self.clear_flag = options["clear"]
        self.dry_run = False
        self.stats = {}

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  LUMRA COFFEE - COMPREHENSIVE DUMMY DATA SEEDER"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        try:
            if self.clear_flag:
                self._clear_data()

            if not options["customers_only"]:
                self.stdout.write(self.style.HTTP_INFO("\n[1/6] Seeding Admin User..."))
                self._seed_admin_user()

                self.stdout.write(self.style.HTTP_INFO("\n[2/6] Seeding Locations..."))
                self._seed_locations()

                self.stdout.write(self.style.HTTP_INFO("\n[3/6] Seeding Vendors..."))
                self._seed_vendors()

                self.stdout.write(self.style.HTTP_INFO("\n[4/6] Seeding Categories, Units, Taxes..."))
                self._seed_basic_data()

                self.stdout.write(self.style.HTTP_INFO("\n[5/6] Seeding Products..."))
                self._seed_products()

            self.stdout.write(self.style.HTTP_INFO(f"\n[6/6] Seeding Customers ({options['num_customers']})..."))
            self._seed_customers(num_customers=options["num_customers"])

            self._print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ ERROR: {e}"))
            import traceback
            traceback.print_exc()
            raise

    def _clear_data(self):
        """Hapus data lama dengan hati-hati."""
        self.stdout.write(self.style.WARNING("⚠️  Clearing old data..."))
        # Perhatian: Jangan hapus auth_user karena Django perlu itu
        models_to_clear = [
            Product, ProductVariant, Customer, Location, Vendor,
            Category, Tax, Unit,
        ]
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f"  • {model.__name__}: {count} deleted")

    def _seed_admin_user(self):
        """Create admin user dan superuser."""
        # Admin user
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@lumracoffee.local",
                "first_name": "Admin",
                "last_name": "Lumra",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            user.set_password("admin@123")
            user.save()
            self.stdout.write(f"  ✓ Admin user created: admin / admin@123")
        else:
            self.stdout.write(f"  ✓ Admin user exists")

        # Staff role
        role, created = Role.objects.get_or_create(
            name="Staff",
            defaults={
                "code": "STAFF",
                "description": "Barista dan staff kopi shop",
                "role_type": "staff",
                "is_active": True,
            }
        )
        self._inc("roles", 1 if created else 0)

        # Manager role
        role, created = Role.objects.get_or_create(
            name="Manager",
            defaults={
                "code": "MGR",
                "description": "Manager toko",
                "role_type": "staff",
                "is_active": True,
            }
        )
        self._inc("roles", 1 if created else 0)

    def _seed_locations(self):
        """Seed store locations."""
        for loc_data in STORE_LOCATIONS:
            location, created = Location.objects.get_or_create(
                name=loc_data["name"],
                defaults={
                    "address": loc_data["address"],
                    "location_type": loc_data["type"],
                }
            )
            if created:
                self.stdout.write(f"  ✓ {location.name}")
            self._inc("locations", 1 if created else 0)

    def _seed_vendors(self):
        """Seed vendors/suppliers."""
        for vendor_data in VENDORS_DATA:
            vendor, created = Vendor.objects.get_or_create(
                name=vendor_data["name"],
                defaults={
                    "code": vendor_data["code"],
                    "contact_person": vendor_data["contact_person"],
                    "phone": vendor_data["phone"],
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(f"  ✓ {vendor.name}")
            self._inc("vendors", 1 if created else 0)

    def _seed_basic_data(self):
        """Seed categories, units, taxes."""
        # Categories
        categories = [
            ("Kopi Biji - Single Origin", "Single origin arabika", "kopi-biji-so"),
            ("Kopi Biji - Blended", "Kopi blend signature", "kopi-biji-blend"),
            ("Minuman Kopi - Espresso Based", "Minuman berbasis espresso", "minuman-espresso"),
            ("Minuman Kopi - Cold Brew", "Minuman kopi dingin", "minuman-cold"),
            ("Minuman Kopi - Manual Brew", "V60, French press, dll", "minuman-manual"),
            ("Minuman Kopi - Non Coffee", "Non-coffee drinks", "minuman-non-coffee"),
            ("Makanan & Kue - Pastry", "Pastry dan kue", "makanan-pastry"),
            ("Makanan & Kue - Savory", "Makanan gurih", "makanan-savory"),
        ]
        for name, desc, slug in categories:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": desc, "slug": slug, "is_active": True}
            )
            self._inc("categories", 1 if created else 0)

        # Units
        units = [
            ("Gram", "g"),
            ("Kilogram", "kg"),
            ("Mililiter", "ml"),
            ("Liter", "L"),
            ("Pcs", "pcs"),
        ]
        for name, symbol in units:
            unit, created = Unit.objects.get_or_create(
                name=name,
                defaults={"symbol": symbol, "is_active": True}
            )
            self._inc("units", 1 if created else 0)

        # Taxes
        taxes = [
            ("PPN 11%", D("11.00")),
            ("PPN 0%", D("0.00")),
        ]
        for name, rate in taxes:
            tax, created = Tax.objects.get_or_create(
                name=name,
                defaults={"rate": rate, "is_active": True}
            )
            self._inc("taxes", 1 if created else 0)

    def _seed_products(self):
        """Seed coffee products."""
        for prod_data in COFFEE_PRODUCTS:
            # Get or create category
            try:
                category = Category.objects.get(name=prod_data["category"])
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Category not found: {prod_data['category']}")
                )
                continue

            # Get units and tax
            try:
                unit = Unit.objects.get(name=prod_data["unit"])
            except Unit.DoesNotExist:
                unit = None

            try:
                tax = Tax.objects.get(name=prod_data["tax"])
            except Tax.DoesNotExist:
                tax = None

            # Get vendor if specified
            if prod_data["vendor"]:
                try:
                    vendor = Vendor.objects.get(name=prod_data["vendor"])
                except Vendor.DoesNotExist:
                    vendor = None
            else:
                vendor = None

            # Get or create product
            product, created = Product.objects.get_or_create(
                name=prod_data["name"],
                defaults={
                    "barcode": prod_data["code"],
                    "category": category,
                    "description": prod_data["description"],
                    "unit": unit,
                    "tax": tax,
                    "vendor": vendor,
                    "is_active": True,
                }
            )

            if created:
                self.stdout.write(f"  ✓ {product.name}")

            # Create variants
            for var_data in prod_data["variants"]:
                variant, var_created = ProductVariant.objects.get_or_create(
                    sku=var_data["sku"],
                    defaults={
                        "product": product,
                        "size_weight": var_data["name"],
                        "price_buy": D(var_data["buy"]),
                        "price_sell": D(var_data["sell"]),
                    }
                )
                self._inc("variants", 1 if var_created else 0)

            self._inc("products", 1 if created else 0)

    def _seed_customers(self, num_customers: int = 5000):
        """Seed dummy customers."""
        self.stdout.write(f"  Creating {num_customers} customers...")

        created_count = 0
        for i in range(num_customers):
            if (i + 1) % 500 == 0:
                self.stdout.write(f"    {i + 1}/{num_customers}...")

            name = generate_name()
            email = generate_email()
            phone = generate_phone()
            city = random.choice(INDONESIAN_CITIES)

            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "phone": phone,
                    "address": f"Jl. {random.choice(['Sudirman', 'Gatot Subroto', 'Diponegoro', 'Imam Bonjol', 'H. Agus Salim'])} No. {random.randint(1, 999)}",
                    "city": city,
                    "tier": random.choice(["bronze", "silver", "gold", "platinum"]),
                    "is_active": True,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f"  ✓ Created/verified {created_count} customers")
        self._inc("customers", created_count)

    def _inc(self, label, n=1):
        self.stats[label] = self.stats.get(label, 0) + n

    def _print_summary(self):
        """Print summary of seeded data."""
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("  📊 SEEDING SUMMARY"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        for label, count in sorted(self.stats.items()):
            if count > 0:
                self.stdout.write(f"  ✓ {label.capitalize():.<40} {count:>5}")

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  ✅ Database seeding completed!"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("  🚀 Ready to use!"))
        self.stdout.write(self.style.HTTP_INFO("  URL: http://localhost:8000"))
        self.stdout.write(self.style.HTTP_INFO("  Login: admin / admin@123"))
        self.stdout.write("")
