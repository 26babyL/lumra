"""
Lumra Coffee Shop - Dummy Data Seeder
======================================
Theme: Starbucks, Kopi Kenangan, Fore Coffee, Janji Jiwa

Run:
  python manage.py seed_comprehensive_data2
  python manage.py seed_comprehensive_data --clear
  python manage.py seed_comprehensive_data --customers-only
  python manage.py seed_comprehensive_data --num-customers 1000
"""

import random
from decimal import Decimal as D
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from lumra_config.models import (
    Category, Tax, Unit, Vendor, Location, Product, ProductVariant,
    Customer, UserProfile, Role,
)

User = get_user_model()

# ═══════════════════════════════════════════════════════════════════════════
# MASTER DATA
# ═══════════════════════════════════════════════════════════════════════════

STORE_LOCATIONS = [
    {"name": "Lumra Coffee - Sudirman", "code": "LUM-SDR", "address": "Jl. Sudirman No.123, Jakarta Pusat", "city": "Jakarta", "type": "store"},
    {"name": "Lumra Coffee - Kemang", "code": "LUM-KMG", "address": "Jl. Kemang Raya No.45, Jakarta Selatan", "city": "Jakarta", "type": "store"},
    {"name": "Lumra Coffee - Dago", "code": "LUM-DGO", "address": "Jl. Ir. H. Juanda No.88, Bandung", "city": "Bandung", "type": "store"},
    {"name": "Lumra Coffee - Tunjungan", "code": "LUM-TJN", "address": "Jl. Tunjungan No.56, Surabaya", "city": "Surabaya", "type": "store"},
    {"name": "Lumra Coffee - Gatot Subroto", "code": "LUM-GTS", "address": "Jl. Gatot Subroto No.234, Medan", "city": "Medan", "type": "store"},
    {"name": "Lumra Coffee - Malioboro", "code": "LUM-MLB", "address": "Jl. Malioboro No.77, Yogyakarta", "city": "Yogyakarta", "type": "store"},
    {"name": "Lumra Coffee - Diponegoro", "code": "LUM-DPN", "address": "Jl. Diponegoro No.99, Semarang", "city": "Semarang", "type": "store"},
    {"name": "Lumra Roastery - Cikarang", "code": "LUM-RST", "address": "Jl. Industri No.22, Cikarang", "city": "Bekasi", "type": "roastery"},
    {"name": "Lumra Warehouse - Depok", "code": "LUM-WH", "address": "Jl. Raya Bogor Km.32, Depok", "city": "Depok", "type": "warehouse"},
]

VENDORS = [
    {"name": "PT Toraja Sulawesi Coffee", "code": "TOR", "contact": "Pak Budi", "phone": "0812-3456-7001", "type": "supplier_kopi"},
    {"name": "CV Gayo Highland Farm", "code": "GAY", "contact": "Ibu Ratna", "phone": "0812-3456-7002", "type": "supplier_kopi"},
    {"name": "PT Java Preanger Estate", "code": "JPE", "contact": "Pak Hendra", "phone": "0812-3456-7003", "type": "supplier_kopi"},
    {"name": "PT Mandailing Coffee Co", "code": "MDL", "contact": "Pak Surya", "phone": "0812-3456-7004", "type": "supplier_kopi"},
    {"name": "CV Fresh Dairy Indonesia", "code": "FDI", "contact": "Ibu Maya", "phone": "0812-3456-7005", "type": "supplier_dairy"},
    {"name": "PT Indo Food Supply", "code": "IFS", "contact": "Pak Doni", "phone": "0812-3456-7006", "type": "supplier_makanan"},
    {"name": "CV Sugar & Syrup Nusantara", "code": "SSN", "contact": "Pak Andi", "phone": "0812-3456-7007", "type": "supplier_syrup"},
    {"name": "PT Packaging Solutions", "code": "PKG", "contact": "Pak Rianto", "phone": "0812-3456-7008", "type": "supplier_packaging"},
    {"name": "PT UHT Milk Indonesia", "code": "UHT", "contact": "Ibu Sari", "phone": "0812-3456-7009", "type": "supplier_dairy"},
    {"name": "CV Gula Aren Nusantara", "code": "GAN", "contact": "Pak Wahyu", "phone": "0812-3456-7010", "type": "supplier_syrup"},
]

# ═══════════════════════════════════════════════════════════════════════════
# PRODUCTS - Kopi Kenangan / Fore / Starbucks Style
# ═══════════════════════════════════════════════════════════════════════════

PRODUCTS = [
    # ── SIGNATURE INDONESIAN COFFEE (Kopi Kenangan/Janji Jiwa Style) ──
    {
        "name": "Kopi Susu Lumra", "code": "KS-LUM", "category": "Signature Coffee",
        "desc": "Signature kopi susu dengan gula aren. Creamy, manis pas, kopi nendang.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "KS-LUM-S", "name": "Small (250ml)", "buy": 8000, "sell": 22000},
            {"sku": "KS-LUM-R", "name": "Regular (350ml)", "buy": 10000, "sell": 27000},
            {"sku": "KS-LUM-L", "name": "Large (470ml)", "buy": 12000, "sell": 32000},
        ],
    },
    {
        "name": "Kopi Gula Aren", "code": "KS-GA", "category": "Signature Coffee",
        "desc": "Espresso + fresh milk + gula aren asli. Manis alami.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "KS-GA-S", "name": "Small (250ml)", "buy": 9000, "sell": 24000},
            {"sku": "KS-GA-R", "name": "Regular (350ml)", "buy": 11000, "sell": 29000},
            {"sku": "KS-GA-L", "name": "Large (470ml)", "buy": 13000, "sell": 34000},
        ],
    },
    {
        "name": "Kopi Susu Pandan", "code": "KS-PDN", "category": "Signature Coffee",
        "desc": "Kopi susu dengan essence pandan asli. Aromatik dan unik.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "KS-PDN-S", "name": "Small (250ml)", "buy": 9000, "sell": 25000},
            {"sku": "KS-PDN-R", "name": "Regular (350ml)", "buy": 11000, "sell": 30000},
            {"sku": "KS-PDN-L", "name": "Large (470ml)", "buy": 13000, "sell": 35000},
        ],
    },
    {
        "name": "Kopi Susu Kelapa", "code": "KS-KLP", "category": "Signature Coffee",
        "desc": "Kopi susu dengan santan segar. Creamy tropical vibe.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "KS-KLP-R", "name": "Regular (350ml)", "buy": 11000, "sell": 28000},
            {"sku": "KS-KLP-L", "name": "Large (470ml)", "buy": 13000, "sell": 33000},
        ],
    },
    {
        "name": "Es Kopi Kental Manis", "code": "EKKM", "category": "Signature Coffee",
        "desc": "Es kopi kental manis klasik Indonesia. Kenangan masa kecil.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "EKKM-R", "name": "Regular (300ml)", "buy": 7000, "sell": 20000},
            {"sku": "EKKM-L", "name": "Large (400ml)", "buy": 9000, "sell": 25000},
        ],
    },
    {
        "name": "Matcha Latte", "code": "ML-STD", "category": "Signature Coffee",
        "desc": "Ceremonial grade matcha Uji + fresh milk.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "ML-S", "name": "Small (250ml)", "buy": 12000, "sell": 30000},
            {"sku": "ML-R", "name": "Regular (350ml)", "buy": 15000, "sell": 35000},
            {"sku": "ML-L", "name": "Large (470ml)", "buy": 18000, "sell": 40000},
        ],
    },
    {
        "name": "Chocolate Sensation", "code": "CHC-SEN", "category": "Signature Coffee",
        "desc": "Belgian dark chocolate + espresso + whipped cream.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "CHC-S", "name": "Small (250ml)", "buy": 11000, "sell": 30000},
            {"sku": "CHC-R", "name": "Regular (350ml)", "buy": 14000, "sell": 35000},
            {"sku": "CHC-L", "name": "Large (470ml)", "buy": 17000, "sell": 40000},
        ],
    },
    {
        "name": "Taro Latte", "code": "TR-LAT", "category": "Signature Coffee",
        "desc": "Taro root + fresh milk. Purple vibes.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "TR-R", "name": "Regular (350ml)", "buy": 12000, "sell": 32000},
            {"sku": "TR-L", "name": "Large (470ml)", "buy": 15000, "sell": 37000},
        ],
    },

    # ── ESPRESSO BASED (Starbucks Style) ──
    {
        "name": "Espresso", "code": "ESP", "category": "Espresso Based",
        "desc": "Single/Double shot. Bold dan concentrated.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "ESP-SGL", "name": "Single (30ml)", "buy": 5000, "sell": 22000},
            {"sku": "ESP-DBL", "name": "Double (60ml)", "buy": 8000, "sell": 28000},
        ],
    },
    {
        "name": "Americano", "code": "AME", "category": "Espresso Based",
        "desc": "Espresso + hot water. Clean dan bold.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "AME-S", "name": "Small (240ml)", "buy": 6000, "sell": 24000},
            {"sku": "AME-R", "name": "Regular (350ml)", "buy": 7000, "sell": 28000},
            {"sku": "AME-L", "name": "Large (470ml)", "buy": 8000, "sell": 32000},
        ],
    },
    {
        "name": "Cappuccino", "code": "CAP", "category": "Espresso Based",
        "desc": "Espresso + steamed milk + thick foam.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "CAP-S", "name": "Small (200ml)", "buy": 9000, "sell": 28000},
            {"sku": "CAP-R", "name": "Regular (280ml)", "buy": 11000, "sell": 33000},
            {"sku": "CAP-L", "name": "Large (360ml)", "buy": 13000, "sell": 38000},
        ],
    },
    {
        "name": "Caffe Latte", "code": "LAT", "category": "Espresso Based",
        "desc": "Espresso + steamed milk. Smooth dan creamy.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "LAT-S", "name": "Small (250ml)", "buy": 10000, "sell": 30000},
            {"sku": "LAT-R", "name": "Regular (350ml)", "buy": 12000, "sell": 35000},
            {"sku": "LAT-L", "name": "Large (470ml)", "buy": 15000, "sell": 40000},
        ],
    },
    {
        "name": "Flat White", "code": "FW", "category": "Espresso Based",
        "desc": "Double ristretto + microfoam. Velvety.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "FW-R", "name": "Regular (250ml)", "buy": 12000, "sell": 33000},
            {"sku": "FW-L", "name": "Large (350ml)", "buy": 15000, "sell": 38000},
        ],
    },
    {
        "name": "Mocha", "code": "MOC", "category": "Espresso Based",
        "desc": "Espresso + chocolate + milk + whipped cream.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "MOC-S", "name": "Small (250ml)", "buy": 13000, "sell": 33000},
            {"sku": "MOC-R", "name": "Regular (350ml)", "buy": 15000, "sell": 38000},
            {"sku": "MOC-L", "name": "Large (470ml)", "buy": 18000, "sell": 43000},
        ],
    },
    {
        "name": "Caramel Macchiato", "code": "CRM", "category": "Espresso Based",
        "desc": "Vanilla + milk + espresso + caramel drizzle.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "CRM-S", "name": "Small (250ml)", "buy": 14000, "sell": 36000},
            {"sku": "CRM-R", "name": "Regular (350ml)", "buy": 16000, "sell": 41000},
            {"sku": "CRM-L", "name": "Large (470ml)", "buy": 19000, "sell": 46000},
        ],
    },
    {
        "name": "Affogato", "code": "AFO", "category": "Espresso Based",
        "desc": "Espresso shot over vanilla gelato.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "AFO-1", "name": "1 scoop (200ml)", "buy": 15000, "sell": 38000},
            {"sku": "AFO-2", "name": "2 scoop (250ml)", "buy": 22000, "sell": 48000},
        ],
    },

    # ── ICED COFFEE ──
    {
        "name": "Iced Americano", "code": "I-AME", "category": "Iced Coffee",
        "desc": "Espresso + water + ice. Refreshing bold.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "I-AME-R", "name": "Regular (300ml)", "buy": 8000, "sell": 28000},
            {"sku": "I-AME-L", "name": "Large (400ml)", "buy": 10000, "sell": 33000},
        ],
    },
    {
        "name": "Iced Latte", "code": "I-LAT", "category": "Iced Coffee",
        "desc": "Espresso + cold milk + ice.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "I-LAT-R", "name": "Regular (300ml)", "buy": 11000, "sell": 33000},
            {"sku": "I-LAT-L", "name": "Large (400ml)", "buy": 13000, "sell": 38000},
        ],
    },
    {
        "name": "Iced Mocha", "code": "I-MOC", "category": "Iced Coffee",
        "desc": "Espresso + chocolate + cold milk + ice.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "I-MOC-R", "name": "Regular (300ml)", "buy": 14000, "sell": 36000},
            {"sku": "I-MOC-L", "name": "Large (400ml)", "buy": 17000, "sell": 41000},
        ],
    },
    {
        "name": "Cold Brew", "code": "CB", "category": "Iced Coffee",
        "desc": "18-hour cold steeped. Smooth, low acidity, natural sweet.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "CB-R", "name": "Regular (250ml)", "buy": 10000, "sell": 32000},
            {"sku": "CB-L", "name": "Large (400ml)", "buy": 14000, "sell": 40000},
        ],
    },
    {
        "name": "Cold Brew Gula Aren", "code": "CB-GA", "category": "Iced Coffee",
        "desc": "Cold brew + gula aren. Best seller!",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "CB-GA-R", "name": "Regular (300ml)", "buy": 12000, "sell": 35000},
            {"sku": "CB-GA-L", "name": "Large (400ml)", "buy": 15000, "sell": 42000},
        ],
    },
    {
        "name": "Es Teler Kopi", "code": "ET-KPI", "category": "Iced Coffee",
        "desc": "Kopi + kelapa muda + nangka + es. Indonesian fusion.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "ET-KPI-R", "name": "Regular (400ml)", "buy": 15000, "sell": 38000},
        ],
    },

    # ── MANUAL BREW ──
    {
        "name": "V60 Single Origin", "code": "V60", "category": "Manual Brew",
        "desc": "V60 pour over single origin pilihan.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "V60-TOR", "name": "Toraja (250ml)", "buy": 12000, "sell": 38000},
            {"sku": "V60-GAY", "name": "Gayo (250ml)", "buy": 14000, "sell": 42000},
            {"sku": "V60-JAV", "name": "Java (250ml)", "buy": 13000, "sell": 40000},
            {"sku": "V60-MDL", "name": "Mandailing (250ml)", "buy": 13000, "sell": 40000},
        ],
    },
    {
        "name": "French Press", "code": "FP", "category": "Manual Brew",
        "desc": "Full immersion brew. Rich body, bold.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "FP-1", "name": "1 cup (350ml)", "buy": 10000, "sell": 35000},
            {"sku": "FP-2", "name": "2 cups (600ml)", "buy": 16000, "sell": 55000},
        ],
    },
    {
        "name": "Aeropress", "code": "AP", "category": "Manual Brew",
        "desc": "Aeropress. Clean cup, versatile.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "AP-1", "name": "1 cup (250ml)", "buy": 10000, "sell": 35000},
        ],
    },
    {
        "name": "Kopi Tubruk Nusantara", "code": "KT-NUS", "category": "Manual Brew",
        "desc": "Kopi tubruk tradisional. Robusta pilihan.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "KT-1", "name": "1 cup (250ml)", "buy": 5000, "sell": 18000},
        ],
    },
    {
        "name": "Es Kopi Klotok", "code": "EK-KLT", "category": "Manual Brew",
        "desc": "Kopi klotok ala Jogja. Diseduh tradisional.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "EK-KLT-1", "name": "1 cup (200ml)", "buy": 5000, "sell": 20000},
        ],
    },

    # ── NON-COFFEE ──
    {
        "name": "Hot Chocolate", "code": "HCHOC", "category": "Non Coffee",
        "desc": "Belgian dark chocolate + steamed milk.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "HCHOC-S", "name": "Small (250ml)", "buy": 10000, "sell": 30000},
            {"sku": "HCHOC-R", "name": "Regular (350ml)", "buy": 13000, "sell": 35000},
            {"sku": "HCHOC-L", "name": "Large (470ml)", "buy": 16000, "sell": 40000},
        ],
    },
    {
        "name": "Thai Tea", "code": "THTEA", "category": "Non Coffee",
        "desc": "Thai tea klasik + condensed milk.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "THTEA-R", "name": "Regular (350ml)", "buy": 8000, "sell": 25000},
            {"sku": "THTEA-L", "name": "Large (470ml)", "buy": 10000, "sell": 30000},
        ],
    },
    {
        "name": "Teh Tarik", "code": "TTRK", "category": "Non Coffee",
        "desc": "Teh tarik ala mamak. Frothy dan creamy.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "TTRK-R", "name": "Regular (300ml)", "buy": 6000, "sell": 22000},
            {"sku": "TTRK-L", "name": "Large (400ml)", "buy": 8000, "sell": 27000},
        ],
    },
    {
        "name": "Lemon Tea", "code": "LMTEA", "category": "Non Coffee",
        "desc": "Fresh lemon + black tea.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "LMTEA-R", "name": "Regular (300ml)", "buy": 6000, "sell": 22000},
            {"sku": "LMTEA-L", "name": "Large (400ml)", "buy": 8000, "sell": 27000},
        ],
    },
    {
        "name": "Fresh Juice Orange", "code": "FJ-ORG", "category": "Non Coffee",
        "desc": "Fresh squeezed orange juice. No sugar added.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "FJ-ORG-R", "name": "Regular (300ml)", "buy": 12000, "sell": 30000},
            {"sku": "FJ-ORG-L", "name": "Large (400ml)", "buy": 16000, "sell": 38000},
        ],
    },
    {
        "name": "Mineral Water", "code": "WATER", "category": "Non Coffee",
        "desc": "Mineral water 600ml.",
        "unit": "Pcs", "tax": "PPN 0%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "WATER-600", "name": "600ml", "buy": 2500, "sell": 8000},
        ],
    },

    # ── KOPI BIJI (Retail) ──
    {
        "name": "Toraja Sapan Kalosi", "code": "BN-TOR", "category": "Kopi Biji",
        "desc": "Single origin. Dark chocolate, brown sugar, full body.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "PT Toraja Sulawesi Coffee",
        "variants": [
            {"sku": "BN-TOR-250", "name": "250g", "buy": 55000, "sell": 95000},
            {"sku": "BN-TOR-500", "name": "500g", "buy": 100000, "sell": 175000},
            {"sku": "BN-TOR-1KG", "name": "1kg", "buy": 185000, "sell": 330000},
        ],
    },
    {
        "name": "Gayo Red Honey", "code": "BN-GAY", "category": "Kopi Biji",
        "desc": "Red honey process. Red fruit, jasmine, medium body.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "CV Gayo Highland Farm",
        "variants": [
            {"sku": "BN-GAY-250", "name": "250g", "buy": 65000, "sell": 110000},
            {"sku": "BN-GAY-500", "name": "500g", "buy": 120000, "sell": 205000},
            {"sku": "BN-GAY-1KG", "name": "1kg", "buy": 225000, "sell": 390000},
        ],
    },
    {
        "name": "Java Preanger Natural", "code": "BN-JAV", "category": "Kopi Biji",
        "desc": "Natural process. Tropical fruit, citrus, floral.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "PT Java Preanger Estate",
        "variants": [
            {"sku": "BN-JAV-250", "name": "250g", "buy": 60000, "sell": 105000},
            {"sku": "BN-JAV-500", "name": "500g", "buy": 110000, "sell": 195000},
            {"sku": "BN-JAV-1KG", "name": "1kg", "buy": 205000, "sell": 370000},
        ],
    },
    {
        "name": "Mandailing Grade 1", "code": "BN-MDL", "category": "Kopi Biji",
        "desc": "Wet hull process. Earthy, herbal, heavy body.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": "PT Mandailing Coffee Co",
        "variants": [
            {"sku": "BN-MDL-250", "name": "250g", "buy": 50000, "sell": 90000},
            {"sku": "BN-MDL-500", "name": "500g", "buy": 92000, "sell": 170000},
            {"sku": "BN-MDL-1KG", "name": "1kg", "buy": 175000, "sell": 320000},
        ],
    },
    {
        "name": "Lumra House Blend", "code": "BN-HB", "category": "Kopi Biji",
        "desc": "60% Toraja + 40% Mandailing. Signature espresso blend.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "BN-HB-250", "name": "250g", "buy": 45000, "sell": 78000},
            {"sku": "BN-HB-500", "name": "500g", "buy": 82000, "sell": 145000},
            {"sku": "BN-HB-1KG", "name": "1kg", "buy": 155000, "sell": 275000},
        ],
    },
    {
        "name": "Lumra Morning Blend", "code": "BN-MB", "category": "Kopi Biji",
        "desc": "50% Java + 30% Gayo + 20% Brazil. Medium roast.",
        "unit": "Gram", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "BN-MB-250", "name": "250g", "buy": 48000, "sell": 85000},
            {"sku": "BN-MB-500", "name": "500g", "buy": 88000, "sell": 160000},
            {"sku": "BN-MB-1KG", "name": "1kg", "buy": 168000, "sell": 305000},
        ],
    },

    # ── PASTRY & DESSERT ──
    {
        "name": "Croissant Butter", "code": "P-CRS", "category": "Pastry",
        "desc": "Classic French butter croissant. Flakey, golden, buttery.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-CRS-1", "name": "1 pcs", "buy": 10000, "sell": 28000},
        ],
    },
    {
        "name": "Croissant Chocolate", "code": "P-CRS-CHC", "category": "Pastry",
        "desc": "Pain au chocolat. Dark chocolate filling.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-CRS-CHC-1", "name": "1 pcs", "buy": 12000, "sell": 32000},
        ],
    },
    {
        "name": "Croissant Almond", "code": "P-CRS-ALM", "category": "Pastry",
        "desc": "Almond croissant with frangipane filling.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-CRS-ALM-1", "name": "1 pcs", "buy": 14000, "sell": 35000},
        ],
    },
    {
        "name": "Banana Bread", "code": "P-BB", "category": "Pastry",
        "desc": "Homemade banana bread. Moist dengan walnut.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-BB-1", "name": "1 slice", "buy": 10000, "sell": 28000},
            {"sku": "P-BB-FULL", "name": "Whole loaf", "buy": 55000, "sell": 125000},
        ],
    },
    {
        "name": "Brownies Dark Choco", "code": "P-BRW", "category": "Pastry",
        "desc": "Fudgy brownies Belgian dark chocolate 70%.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-BRW-1", "name": "1 pcs", "buy": 8000, "sell": 25000},
        ],
    },
    {
        "name": "Blueberry Muffin", "code": "P-MUF-BLB", "category": "Pastry",
        "desc": "Fresh blueberry muffin dengan streusel topping.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-MUF-BLB-1", "name": "1 pcs", "buy": 9000, "sell": 25000},
        ],
    },
    {
        "name": "Chocolate Muffin", "code": "P-MUF-CHC", "category": "Pastry",
        "desc": "Double chocolate muffin dengan chocolate chips.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-MUF-CHC-1", "name": "1 pcs", "buy": 9000, "sell": 25000},
        ],
    },
    {
        "name": "Cinnamon Roll", "code": "P-CIN", "category": "Pastry",
        "desc": "Soft cinnamon roll dengan cream cheese glaze.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-CIN-1", "name": "1 pcs", "buy": 12000, "sell": 32000},
        ],
    },
    {
        "name": "Danish Pastry", "code": "P-DAN", "category": "Pastry",
        "desc": "Danish pastry dengan custard dan fruits.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "P-DAN-1", "name": "1 pcs", "buy": 12000, "sell": 30000},
        ],
    },

    # ── CAKE & DESSERT ──
    {
        "name": "New York Cheesecake", "code": "D-NYCC", "category": "Dessert",
        "desc": "Classic NY cheesecake. Dense, creamy, graham crust.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-NYCC-1", "name": "1 slice", "buy": 15000, "sell": 40000},
            {"sku": "D-NYCC-W", "name": "Whole (6 inch)", "buy": 130000, "sell": 285000},
        ],
    },
    {
        "name": "Tiramisu", "code": "D-TRM", "category": "Dessert",
        "desc": "Classic Italian tiramisu. Espresso soaked ladyfinger.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-TRM-1", "name": "1 portion", "buy": 16000, "sell": 42000},
        ],
    },
    {
        "name": "Red Velvet Cake", "code": "D-RVC", "category": "Dessert",
        "desc": "Red velvet dengan cream cheese frosting.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-RVC-1", "name": "1 slice", "buy": 14000, "sell": 38000},
            {"sku": "D-RVC-W", "name": "Whole (6 inch)", "buy": 120000, "sell": 265000},
        ],
    },
    {
        "name": "Chocolate Lava Cake", "code": "D-CLC", "category": "Dessert",
        "desc": "Warm chocolate lava cake. Molten center.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-CLC-1", "name": "1 pcs", "buy": 14000, "sell": 38000},
        ],
    },
    {
        "name": "Panna Cotta", "code": "D-PNC", "category": "Dessert",
        "desc": "Italian panna cotta dengan berry compote.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-PNC-1", "name": "1 portion", "buy": 12000, "sell": 35000},
        ],
    },
    {
        "name": "Pisang Goreng Keju", "code": "D-PGK", "category": "Dessert",
        "desc": "Pisang goreng crispy dengan lelehan keju dan coklat.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-PGK-3", "name": "3 pcs", "buy": 10000, "sell": 25000},
            {"sku": "D-PGK-5", "name": "5 pcs", "buy": 15000, "sell": 38000},
        ],
    },
    {
        "name": "Klepon Cake", "code": "D-KLC", "category": "Dessert",
        "desc": "Kue klepon modern. Pandan, gula aren, kelapa.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-KLC-1", "name": "1 slice", "buy": 13000, "sell": 35000},
        ],
    },
    {
        "name": "Es Krim Gelato", "code": "D-GLT", "category": "Dessert",
        "desc": "Artisan gelato. Pilihan rasa.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "D-GLT-VNL", "name": "Vanilla (1 scoop)", "buy": 10000, "sell": 25000},
            {"sku": "D-GLT-CHC", "name": "Chocolate (1 scoop)", "buy": 10000, "sell": 25000},
            {"sku": "D-GLT-STR", "name": "Strawberry (1 scoop)", "buy": 10000, "sell": 25000},
            {"sku": "D-GLT-MTC", "name": "Matcha (1 scoop)", "buy": 12000, "sell": 28000},
            {"sku": "D-GLT-2S", "name": "2 Scoops", "buy": 18000, "sell": 40000},
        ],
    },

    # ── SAVORY FOOD ──
    {
        "name": "Club Sandwich", "code": "F-CLUB", "category": "Savory",
        "desc": "Triple decker: chicken, egg, lettuce, tomato, mayo.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "F-CLUB-1", "name": "1 set", "buy": 18000, "sell": 45000},
        ],
    },
    {
        "name": "Chicken Croissant Sandwich", "code": "F-CCS", "category": "Savory",
        "desc": "Croissant + grilled chicken + salad + mayo.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "F-CCS-1", "name": "1 set", "buy": 16000, "sell": 42000},
        ],
    },
    {
        "name": "Caesar Salad", "code": "F-CSL", "category": "Savory",
        "desc": "Romaine, croutons, parmesan, caesar dressing.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "F-CSL-1", "name": "1 portion", "buy": 15000, "sell": 40000},
            {"sku": "F-CSL-CHK", "name": "+ Chicken", "buy": 22000, "sell": 55000},
        ],
    },
    {
        "name": "French Fries", "code": "F-FF", "category": "Savory",
        "desc": "Crispy french fries.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "F-FF-R", "name": "Regular", "buy": 10000, "sell": 25000},
            {"sku": "F-FF-L", "name": "Large + Cheese", "buy": 15000, "sell": 35000},
        ],
    },
    {
        "name": "Nasi Goreng Lumra", "code": "F-NG", "category": "Savory",
        "desc": "Nasi goreng spesial dengan telur, ayam, kerupuk.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "F-NG-1", "name": "1 porsi", "buy": 18000, "sell": 42000},
        ],
    },
    {
        "name": "Indomie Rebus Spesial", "code": "F-IDS", "category": "Savory",
        "desc": "Indomie rebus + telur + sayur + keju. Comfort food!",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "F-IDS-1", "name": "1 porsi", "buy": 12000, "sell": 28000},
        ],
    },
    {
        "name": "Roti Bakar", "code": "F-RBK", "category": "Savory",
        "desc": "Roti bakar tebal dengan topping pilihan.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Indo Food Supply",
        "variants": [
            {"sku": "F-RBK-CKC", "name": "Coklat Keju", "buy": 10000, "sell": 25000},
            {"sku": "F-RBK-STR", "name": "Strawberry Keju", "buy": 10000, "sell": 25000},
            {"sku": "F-RBK-EGG", "name": "Telur Keju", "buy": 12000, "sell": 28000},
        ],
    },

    # ── MERCHANDISE ──
    {
        "name": "Lumra Tumbler 500ml", "code": "M-TMB-500", "category": "Merchandise",
        "desc": "Stainless steel tumbler. Keep hot 6hrs / cold 12hrs.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Packaging Solutions",
        "variants": [
            {"sku": "M-TMB-500-BLK", "name": "Black", "buy": 65000, "sell": 125000},
            {"sku": "M-TMB-500-WHT", "name": "White", "buy": 65000, "sell": 125000},
            {"sku": "M-TMB-500-GRN", "name": "Forest Green", "buy": 65000, "sell": 125000},
        ],
    },
    {
        "name": "Lumra Tumbler 750ml", "code": "M-TMB-750", "category": "Merchandise",
        "desc": "Large tumbler. Keep hot 8hrs / cold 24hrs.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Packaging Solutions",
        "variants": [
            {"sku": "M-TMB-750-BLK", "name": "Black", "buy": 85000, "sell": 165000},
            {"sku": "M-TMB-750-WHT", "name": "White", "buy": 85000, "sell": 165000},
        ],
    },
    {
        "name": "Lumra Canvas Tote Bag", "code": "M-TOT", "category": "Merchandise",
        "desc": "Canvas tote bag dengan logo Lumra emboss.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Packaging Solutions",
        "variants": [
            {"sku": "M-TOT-NAT", "name": "Natural", "buy": 35000, "sell": 75000},
            {"sku": "M-TOT-BLK", "name": "Black", "buy": 38000, "sell": 80000},
        ],
    },
    {
        "name": "Lumra Drip Bag Set", "code": "M-DRP", "category": "Merchandise",
        "desc": "Set 10 drip bag. House blend.",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": None,
        "variants": [
            {"sku": "M-DRP-HB", "name": "House Blend (10pcs)", "buy": 65000, "sell": 120000},
            {"sku": "M-DRP-GA", "name": "Gayo (10pcs)", "buy": 85000, "sell": 150000},
        ],
    },
    {
        "name": "Lumra V60 Starter Kit", "code": "M-V60", "category": "Merchandise",
        "desc": "V60 ceramic dripper + server + filter papers (50pcs).",
        "unit": "Pcs", "tax": "PPN 11%", "vendor": "PT Packaging Solutions",
        "variants": [
            {"sku": "M-V60-1", "name": "Full Set", "buy": 150000, "sell": 285000},
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════════════
# NAME GENERATORS
# ═══════════════════════════════════════════════════════════════════════════

FIRST_NAMES = [
    "Ahmad", "Budi", "Citra", "Dian", "Eka", "Farah", "Gita", "Hendra",
    "Indra", "Joko", "Kunia", "Lina", "Musa", "Nita", "Oka", "Putri",
    "Reza", "Siti", "Toni", "Usman", "Vina", "Wawan", "Yoni", "Zahra",
    "Aditya", "Bagas", "Cahya", "Desy", "Emy", "Firman", "Hana", "Irfan",
    "Jaya", "Karen", "Luki", "Maya", "Nando", "Obi", "Prita", "Qori",
    "Raja", "Sasha", "Tania", "Uddin", "Vanessa", "Widi", "Andi", "Rini",
    "Dimas", "Galih", "Intan", "Kevin", "Lisa", "Rizky", "Anisa", "Bayu",
]

LAST_NAMES = [
    "Wijaya", "Rahman", "Santoso", "Nurdin", "Kusuma", "Gunawan", "Setiawan",
    "Handoko", "Saputra", "Hidayat", "Suryanto", "Hartono", "Lestari", "Dewi",
    "Putri", "Amelia", "Rahayu", "Permana", "Utama", "Kurnia", "Pratama",
    "Nugraha", "Purnama", "Syahputra", "Wibowo",
]

STREETS = [
    "Sudirman", "Gatot Subroto", "Diponegoro", "Imam Bonjol", "H. Agus Salim",
    "Asia Afrika", "Braga", "Dago", "Juanda", "Malioboro", "Pemuda",
    "Hayam Wuruk", "Gajah Mada", "Veteran", "Sisingamangaraja", "Kebon Jeruk",
]

CITIES = [
    "Jakarta", "Bandung", "Surabaya", "Medan", "Semarang", "Makassar",
    "Palembang", "Yogyakarta", "Bogor", "Bekasi", "Tangerang", "Depok",
    "Denpasar", "Malang", "Solo",
]

TIERS = ["bronze", "bronze", "bronze", "silver", "silver", "gold", "gold", "platinum"]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]

PHONE_PREFIXES = ["0812", "0813", "0821", "0822", "0852", "0853", "0857", "0858", "0811", "0814"]


def gen_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def gen_email_from_name(name):
    parts = name.lower().split()
    base = random.choice([
        f"{parts[0]}.{parts[1]}",
        f"{parts[0]}{parts[1]}",
        f"{parts[0]}_{parts[1]}",
        f"{parts[0][0]}{parts[1]}",
    ])
    num = random.randint(1, 9999)
    return f"{base}{num}@{random.choice(EMAIL_DOMAINS)}"


def gen_phone():
    return f"{random.choice(PHONE_PREFIXES)}{''.join(str(random.randint(0,9)) for _ in range(8))}"


def gen_address():
    return f"Jl. {random.choice(STREETS)} No.{random.randint(1,999)}, {random.choice(CITIES)}"


# ═══════════════════════════════════════════════════════════════════════════
# COMMAND
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = "Seed database dengan dummy data coffee shop lengkap"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Hapus data lama")
        parser.add_argument("--customers-only", action="store_true", help="Hanya customers")
        parser.add_argument("--products-only", action="store_true", help="Hanya products")
        parser.add_argument("--num-customers", type=int, default=5000, help="Jumlah customers")

    def handle(self, *args, **options):
        self.stats = {}
        self.stdout.write(self.style.SUCCESS("═" * 60))
        self.stdout.write(self.style.SUCCESS("  ☕ LUMRA COFFEE - DATA SEEDER"))
        self.stdout.write(self.style.SUCCESS("═" * 60))

        try:
            if options["clear"]:
                self._clear()

            if not options["customers_only"]:
                self._seed_admin()
                self._seed_locations()
                self._seed_vendors()
                self._seed_masters()
                self._seed_products()

            if not options["products_only"]:
                self._seed_customers(options["num_customers"])
                self._seed_staff()

            self._summary()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ {e}"))
            raise

    def _clear(self):
        self.stdout.write(self.style.WARNING("🗑️  Clearing data..."))
        for m in [ProductVariant, Product, Customer, Location, Vendor, Category, Tax, Unit, Role]:
            c = m.objects.count()
            m.objects.all().delete()
            if c: self.stdout.write(f"   {m.__name__}: {c}")

    def _seed_admin(self):
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@lumra.coffee", "is_staff": True, "is_superuser": True}
        )
        if created:
            user.set_password("admin123")
            user.save()
        self._inc("users", int(created))

    def _seed_locations(self):
        for d in STORE_LOCATIONS:
            _, created = Location.objects.get_or_create(name=d["name"], defaults={
                "address": d["address"], "location_type": d["type"]
            })
            self._inc("locations", int(created))

    def _seed_vendors(self):
        for d in VENDORS:
            _, created = Vendor.objects.get_or_create(name=d["name"], defaults={
                "code": d["code"], "contact_person": d["contact"],
                "phone": d["phone"], "is_active": True
            })
            self._inc("vendors", int(created))

    def _seed_masters(self):
        cats = [
            ("Signature Coffee", "Kopi susu dan signature drinks", "signature-coffee"),
            ("Espresso Based", "Minuman berbasis espresso", "espresso-based"),
            ("Iced Coffee", "Kopi dingin dan cold brew", "iced-coffee"),
            ("Manual Brew", "V60, French press, Aeropress", "manual-brew"),
            ("Non Coffee", "Teh, coklat, juice", "non-coffee"),
            ("Kopi Biji", "Biji kopi retail", "kopi-biji"),
            ("Pastry", "Croissant, muffin, bread", "pastry"),
            ("Dessert", "Cake, gelato, puding", "dessert"),
            ("Savory", "Sandwich, salad, nasi", "savory"),
            ("Merchandise", "Tumbler, tote bag, kit", "merchandise"),
        ]
        for name, desc, slug in cats:
            _, c = Category.objects.get_or_create(name=name, defaults={"description": desc, "slug": slug, "is_active": True})
            self._inc("categories", int(c))

        for name, sym in [("Gram", "g"), ("Kilogram", "kg"), ("Mililiter", "ml"), ("Liter", "L"), ("Pcs", "pcs")]:
            _, c = Unit.objects.get_or_create(name=name, defaults={"symbol": sym, "is_active": True})
            self._inc("units", int(c))

        for name, rate in [("PPN 11%", D("11.00")), ("PPN 0%", D("0.00"))]:
            _, c = Tax.objects.get_or_create(name=name, defaults={"rate": rate, "is_active": True})
            self._inc("taxes", int(c))

        for name, code in [("Admin", "ADM"), ("Manager", "MGR"), ("Barista", "BAR"), ("Kasir", "KSR")]:
            _, c = Role.objects.get_or_create(name=name, defaults={"code": code, "is_active": True})
            self._inc("roles", int(c))

    def _seed_products(self):
        for p in PRODUCTS:
            try:
                cat = Category.objects.get(name=p["category"])
            except Category.DoesNotExist:
                continue

            unit = Unit.objects.filter(name=p["unit"]).first()
            tax = Tax.objects.filter(name=p["tax"]).first()
            vendor = Vendor.objects.filter(name=p["vendor"]).first() if p["vendor"] else None

            product, created = Product.objects.get_or_create(
                name=p["name"],
                defaults={
                    "barcode": p["code"], "category": cat, "description": p["desc"],
                    "unit": unit, "tax": tax, "vendor": vendor, "is_active": True,
                }
            )
            self._inc("products", int(created))

            for v in p["variants"]:
                _, vc = ProductVariant.objects.get_or_create(
                    sku=v["sku"],
                    defaults={
                        "product": product, "size_weight": v["name"],
                        "price_buy": D(v["buy"]), "price_sell": D(v["sell"]),
                    }
                )
                self._inc("variants", int(vc))

    def _seed_customers(self, n):
        self.stdout.write(f"👥 Creating {n} customers...")
        created = 0
        for i in range(n):
            if (i + 1) % 1000 == 0:
                self.stdout.write(f"   {i+1}/{n}...")

            name = gen_name()
            email = gen_email_from_name(name)

            _, c = Customer.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "phone": gen_phone(),
                    "address": gen_address(),
                    "city": random.choice(CITIES),
                    "tier": random.choice(TIERS),
                    "is_active": True,
                }
            )
            created += int(c)

        self._inc("customers", created)

    def _seed_staff(self):
        """Create staff users for each store."""
        stores = Location.objects.filter(location_type="store")
        barista_role = Role.objects.filter(name="Barista").first()
        kasir_role = Role.objects.filter(name="Kasir").first()
        mgr_role = Role.objects.filter(name="Manager").first()

        if not stores.exists():
            return

        created = 0
        for store in stores:
            # 1 manager per store
            name = gen_name()
            uname = f"mgr_{store.code.lower()}"
            user, c = User.objects.get_or_create(
                username=uname,
                defaults={"email": f"{uname}@lumra.coffee", "is_staff": True}
            )
            if c:
                user.set_password("staff123")
                user.save()
                if mgr_role:
                    UserProfile.objects.get_or_create(user=user, defaults={"role": mgr_role})
                created += 1

            # 2 barista per store
            for j in range(2):
                name = gen_name()
                uname = f"bar_{store.code.lower()}_{j}"
                user, c = User.objects.get_or_create(
                    username=uname,
                    defaults={"email": f"{uname}@lumra.coffee", "is_staff": True}
                )
                if c:
                    user.set_password("staff123")
                    user.save()
                    if barista_role:
                        UserProfile.objects.get_or_create(user=user, defaults={"role": barista_role})
                    created += 1

            # 1 kasir per store
            name = gen_name()
            uname = f"ksr_{store.code.lower()}"
            user, c = User.objects.get_or_create(
                username=uname,
                defaults={"email": f"{uname}@lumra.coffee", "is_staff": True}
            )
            if c:
                user.set_password("staff123")
                user.save()
                if kasir_role:
                    UserProfile.objects.get_or_create(user=user, defaults={"role": kasir_role})
                created += 1

        self._inc("staff", created)

    def _inc(self, k, n=1):
        self.stats[k] = self.stats.get(k, 0) + n

    def _summary(self):
        self.stdout.write(self.style.SUCCESS("\n" + "═" * 60))
        self.stdout.write(self.style.SUCCESS("  📊 SUMMARY"))
        self.stdout.write(self.style.SUCCESS("═" * 60))

        for k, v in sorted(self.stats.items()):
            if v:
                self.stdout.write(f"  ✦ {k:<20} {v:>5}")

        self.stdout.write(self.style.SUCCESS("═" * 60))
        self.stdout.write(self.style.SUCCESS("  ✅ Done!"))
        self.stdout.write(self.style.SUCCESS("  👤 admin / admin123"))
        self.stdout.write(self.style.SUCCESS("  👷 mgr_[store] / staff123"))
        self.stdout.write(self.style.SUCCESS("═" * 60))