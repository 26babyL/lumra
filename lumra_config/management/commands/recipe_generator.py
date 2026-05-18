"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  KAFE NUSANTARA — PRODUCTION RECIPE GENERATOR v2.0                         ║
║                                                                              ║
║  Mengisi tabel production_recipes + production_recipe_ingredients           ║
║  untuk semua produk yang memiliki proses produksi nyata.                   ║
║                                                                              ║
║  ARSITEKTUR INGREDIENTS (SKU-linked):                                       ║
║  · Blend A      → ingredients = biji kopi SO-WANOJA-WSL + SO-GAYO-NTL     ║
║                   dengan qty gramasi sesuai resep (misal 600g + 400g)      ║
║  · Single Origin → ingredient = 1 biji kopi 1000g green bean              ║
║  · Addon Syrup  → ingredient = bahan baku (beli dari vendor)               ║
║  · Menu Kafe    → ingredients = blend/SO + milk/water + addon              ║
║                                                                              ║
║  FIX v2.0:                                                                  ║
║  · Fix KeyError '='*50 di template .format()                               ║
║  · Fix ON CONFLICT clause production_recipe_ingredients                    ║
║  · Fix ingredient linkage: pakai SKU untuk cari variant bahan baku         ║
║  · Ingredients di-resolve dari description/recipe gramasi produk asli      ║
║                                                                              ║
║  Usage:                                                                     ║
║    python recipe_generator_v2.py                   # semua resep           ║
║    python recipe_generator_v2.py --dry-run         # preview               ║
║    python recipe_generator_v2.py --type blend      # hanya House Blend     ║
║    python recipe_generator_v2.py --type single     # hanya Single Origin   ║
║    python recipe_generator_v2.py --type menu       # hanya menu kafe       ║
║    python recipe_generator_v2.py --type addon      # hanya addon           ║
║    python recipe_generator_v2.py --skip-ingredients                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random, time, argparse, sys, os, re
from decimal import Decimal as D
from datetime import datetime, timezone

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    import psycopg2, psycopg2.extras
except ImportError:
    print("❌ pip install psycopg2-binary"); sys.exit(1)

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_system.settings")
    from django.conf import settings as django_settings
    _db = django_settings.DATABASES.get("default", {})
except Exception:
    _db = {}

random.seed(20240505)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME",     _db.get("NAME",     "lumra_set_allegra")),
    "user":     os.getenv("DB_USER",     _db.get("USER",     "postgres")),
    "password": os.getenv("DB_PASSWORD", _db.get("PASSWORD", "123456")),
    "host":     os.getenv("DB_HOST",     _db.get("HOST",     "localhost")),
    "port":     os.getenv("DB_PORT",     _db.get("PORT",     "5432")),
}

BATCH_SIZE  = 300
PROGRESS_AT = 500

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — RECIPE CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

RECIPE_CATEGORIES = [
    ("Coffee Blending",    "Resep komposisi dan roasting profile untuk House Blend dan Single Origin"),
    ("Espresso Beverages", "Resep minuman berbasis espresso — cappuccino, latte, americano, mocha"),
    ("Signature Drinks",   "Resep minuman signature Kafe Nusantara — kopi susu, gula aren, pandan"),
    ("Filter Coffee",      "Resep manual brew — V60, Chemex, AeroPress, French Press, Nel Drip"),
    ("Cold Beverages",     "Resep cold brew, iced drinks, dan minuman dingin lainnya"),
    ("Addon Production",   "Resep produksi syrup, extract, foam, powder berbasis tanaman"),
    ("Pastry & Dessert",   "Resep pendukung pastry dan dessert yang diproduksi internal"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ROASTING INSTRUCTION TEMPLATES (untuk kopi)
# ═══════════════════════════════════════════════════════════════════════════════

ROAST_INSTRUCTIONS = {
    "Light":  {
        "charge_temp": "200°C", "first_crack": "9-10 menit",
        "drop_temp": "205-210°C", "dev_time": "90-120 detik",
        "total_time": "11-12 menit", "color": "Light brown, cinnamon",
        "moisture_loss": "13-15%", "agtron": "85", "qc_score": "92",
        "desc": "Light roast mempertahankan karakter origin dan keasaman alami. "
                "Profil rasa: fruity, floral, dan tea-like.",
    },
    "Medium": {
        "charge_temp": "195°C", "first_crack": "10-11 menit",
        "drop_temp": "215-220°C", "dev_time": "60-90 detik",
        "total_time": "12-14 menit", "color": "Medium brown, milk chocolate",
        "moisture_loss": "15-18%", "agtron": "65", "qc_score": "88",
        "desc": "Medium roast menyeimbangkan karakter origin dengan body dan sweetness. "
                "Profil rasa: caramel, nutty, dan balanced.",
    },
    "Dark":   {
        "charge_temp": "190°C", "first_crack": "11-12 menit",
        "drop_temp": "225-230°C", "dev_time": "45-60 detik",
        "total_time": "14-16 menit", "color": "Dark brown, dark chocolate",
        "moisture_loss": "18-22%", "agtron": "45", "qc_score": "84",
        "desc": "Dark roast menghasilkan body penuh dan rasa yang bold. "
                "Profil rasa: dark chocolate, smoky, dan intense.",
    },
}

PROCESS_FLAVOR_NOTES = {
    "Washed":      "clean, bright, citrus-forward, high acidity",
    "Natural":     "fruity, winey, heavy body, complex sweetness",
    "Honey":       "balanced sweetness, stone fruit, medium body",
    "Semi-Washed": "clean with mild sweetness, medium-light body",
    "Wet-Hulled":  "earthy, spicy, heavy body, low acidity",
    "Anaerobic":   "fermented, tropical, complex, experimental",
    "Wine":        "deep wine notes, dark fruit, fermented complexity",
}

# ═══════════════════════════════════════════════════════════════════════════════
# SEPARATOR helper — digunakan di semua template agar tidak konflik dengan .format()
# PENTING: Jangan pakai {'='*50} atau {'-'*50} di dalam string yang di-.format()!
# Sebagai gantinya gunakan konstanta SEP dan DASH.
# ═══════════════════════════════════════════════════════════════════════════════

SEP  = "=" * 50
DASH = "-" * 50


def make_blend_instructions(components, dominant_roast):
    """
    Generate step-by-step blending & roasting instructions.
    components: list of dicts {origin_display, roast, process, gram, pct}
    """
    rd = ROAST_INSTRUCTIONS.get(dominant_roast, ROAST_INSTRUCTIONS["Medium"])
    total_gram = sum(c.get("gram", 0) for c in components) or 1000

    comp_lines = []
    for i, c in enumerate(components, 1):
        disp   = c.get("origin_display", c.get("origin", "Unknown"))
        roast  = c.get("roast", "Medium")
        proc   = c.get("process", "Washed")
        gram   = c.get("gram", 0)
        pct    = c.get("pct", 0)
        flavor = PROCESS_FLAVOR_NOTES.get(proc, "balanced")
        comp_lines.append(
            f"   {i}. {disp} — {gram}g ({pct}%) | {roast} Roast | {proc} | {flavor}"
        )

    comp_text  = "\n".join(comp_lines)
    yield_gram = int(total_gram * 0.82)
    loss       = rd["moisture_loss"]

    return f"""BLEND SPECIFICATION
{SEP}
{comp_text}
Total input  : {total_gram}g green bean
Estimated yield: ~{yield_gram}g setelah roasting ({loss} moisture loss)

PRE-ROAST CHECKLIST
{SEP}
1. Verifikasi kondisi green bean setiap lot: kadar air target 10-12%, ukuran screen 15-17, defect <5 per 300g untuk Specialty Grade.
2. Pastikan roaster drum bersih dari residue batch sebelumnya.
3. Set charge temperature {rd['charge_temp']} dan stabilkan 10 menit sebelum charging.
4. Siapkan cooling tray. Aktifkan data logger untuk record Rate of Rise (RoR) setiap 30 detik.

ROASTING PROFILE — {dominant_roast.upper()} ROAST
{SEP}
5. CHARGE: Masukkan {total_gram}g green bean ke drum pada {rd['charge_temp']}.
6. DRYING PHASE (0-4 menit): 130-150°C. RoR target 10-12°C/menit. Warna biji: hijau → kuning.
7. MAILLARD PHASE (4-{rd['first_crack'].split('-')[0]} menit): 150-190°C. RoR turun ke 8-10°C/menit. Aroma roti mulai muncul.
8. FIRST CRACK ({rd['first_crack']}): Suara crack seperti popcorn ringan pada ±196-200°C. Catat waktu & suhu.
9. DEVELOPMENT TIME: {rd['dev_time']} setelah first crack. DTR target 20-25%.
10. DROP pada {rd['drop_temp']}. Aktifkan cooling tray segera.

COOLING & QC
{SEP}
11. COOLING 3-4 menit: Aduk merata. Target suhu akhir <40°C.
12. DEGASSING: Container kedap udara dengan one-way CO2 valve. Rest minimal 12 jam (filter) atau 24-48 jam (espresso).
13. CUPPING QC: SCA protocol, minimum score {rd['qc_score']}/100. Agtron target: {rd['agtron']}.

BLENDING
{SEP}
14. Roast setiap origin SECARA TERPISAH untuk memaksimalkan karakter individual.
15. Blend SETELAH roasting (post-blend) dengan timbangan presisi 0.1g.
16. {rd['desc']}
17. Batch rejected jika QC score di bawah threshold — hold untuk review roastmaster."""


def make_single_origin_instructions(origin_display, roast, process):
    rd     = ROAST_INSTRUCTIONS.get(roast, ROAST_INSTRUCTIONS["Medium"])
    flavor = PROCESS_FLAVOR_NOTES.get(process, "balanced")

    # Dev time note berdasarkan process — tanpa f-string ternary di dalam template
    if process in ("Anaerobic", "Wine", "Natural"):
        proc_note = "Perpanjang dev time 10 detik untuk menonjolkan karakter fermentasi."
    elif process == "Washed":
        proc_note = "Pertahankan dev time standar untuk kejernihan rasa (clean cup)."
    else:
        proc_note = "Dev time standard, amati sweetness development."

    if roast == "Light":
        rest_note = "12-24 jam untuk filter brewing."
    elif roast == "Medium":
        rest_note = "24-48 jam untuk semua metode brewing."
    else:
        rest_note = "48-72 jam untuk espresso, 24 jam untuk filter."

    return f"""SINGLE ORIGIN ROASTING PROFILE
{SEP}
Origin  : {origin_display}
Process : {process}
Roast   : {roast}
Expected: {flavor}

PRE-ROAST
{SEP}
1. Sort green bean manual: pisahkan yang cacat, ukuran tidak seragam, atau berjamur.
2. Water activity check jika memungkinkan (target 0.55-0.65 Aw).
3. Charge temperature {rd['charge_temp']}, stabilkan drum 10 menit.

ROASTING EXECUTION
{SEP}
4. CHARGE dan catat waktu T+0.
5. DRYING PHASE: Jaga 130-155°C. Amati perubahan warna setiap 30 detik.
6. MAILLARD: 155-190°C. Aroma: grassy → hay → bread → caramel.
7. FIRST CRACK pada {rd['first_crack']}: Catat suhu dan waktu sebagai referensi batch berikutnya.
8. DEVELOPMENT TIME: {rd['dev_time']} post first crack untuk {roast} roast.
   Process note: {proc_note}
9. DROP pada {rd['drop_temp']}.

POST-ROAST
{SEP}
10. Cool di bawah 40°C dalam 4 menit.
11. REST: {rest_note}
12. CUPPING: Protokol SCA — 8.25g per 150ml air pada 93°C.
13. Tasting notes target: {flavor}.

QUALITY STANDARD
{SEP}
Minimum SCA cupping score: {rd['qc_score']}/100.
Warna akhir Agtron: {rd['agtron']}.
Batch tidak memenuhi standar di-hold untuk review roastmaster."""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — MENU DRINK RECIPES
# ═══════════════════════════════════════════════════════════════════════════════

# NOTE: Semua instructions di sini TIDAK menggunakan .format() sehingga
# bebas menggunakan karakter '{' atau '}' apapun — termasuk SEP/DASH literal.

MENU_RECIPES = [
    {
        "name": "Espresso — Standard Recipe",
        "category": "Espresso Beverages",
        "description": "Resep standar espresso single/double shot Kafe Nusantara. 9 bar, 92-93°C.",
        "yield_qty": 36, "yield_unit": "Mililiter", "prep_time": 3,
        "instructions": f"""ESPRESSO EXTRACTION PROTOCOL
{SEP}
PERSIAPAN
1. Periksa mesin: boiler 92-93°C, tekanan 9 bar. Backflush jika belum hari ini.
2. Grind 18g dengan flat burr grinder — setting fine. EK43: 6-7.
3. Distribusi kopi di basket dengan WDT tool — tidak ada channeling/clump.
4. Tamp 15-20kg tekanan merata.

EXTRACTION
5. Pasang portafilter, start timer bersamaan pull shot.
6. Target: 18g input → 36-38ml output dalam 25-30 detik (ratio 1:2).
7. Aliran harus seperti madu tipis setelah 5-7 detik pre-infusion.
8. Hentikan saat 36ml. Buang jika: <20 detik (under/sour), >35 detik (over/bitter).

QC
9. Visual: crema emas kecokelatan, 2-3mm.
10. Rasa: balanced bitter-sweet-sour. Sajikan dalam demitasse yang dipanaskan.""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",  "qty": 18.0, "unit": "Gram",
             "notes": "House Blend aktif — variant 1kg untuk produksi bar."},
        ],
        "base_cost": 12_000,
    },
    {
        "name": "Cappuccino — Standard Recipe",
        "category": "Espresso Beverages",
        "description": "Cappuccino 280ml. Ratio espresso:milk:foam = 1:1:1. Microfoam silky.",
        "yield_qty": 280, "yield_unit": "Mililiter", "prep_time": 4,
        "instructions": f"""CAPPUCCINO RECIPE
{SEP}
ESPRESSO BASE
1. Pull double shot 36ml mengikuti Espresso Standard Recipe.

MILK STEAMING
2. 180ml susu segar full cream 4°C ke steam pitcher 350ml.
3. Steam wand 45°, ujung 1cm di bawah permukaan.
4. STRETCH 2-3 detik (inkorporasi udara, volume naik 30%). Lalu ROLL sampai 60-65°C. Jangan >70°C.
5. Lap wand, purge 1 detik. Swirl pitcher, ketuk untuk pecah gelembung besar.

ASSEMBLY
6. Tuang espresso ke cup 280ml yang dipanaskan.
7. Pour susu: mulai tinggi, turunkan untuk latte art (rosetta atau heart).
8. TARGET: Layer espresso (1/3) + steamed milk (1/3) + thick foam (1/3).""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",    "qty": 18.0,  "unit": "Gram",     "notes": "House Blend espresso base."},
            {"sku_prefix": "SUSU-",  "qty": 180.0, "unit": "Mililiter", "notes": "Susu segar full cream."},
        ],
        "base_cost": 11_000,
    },
    {
        "name": "Caffe Latte — Standard Recipe",
        "category": "Espresso Beverages",
        "description": "Latte 350ml. Double shot espresso dan steamed whole milk. Microfoam tipis.",
        "yield_qty": 350, "yield_unit": "Mililiter", "prep_time": 5,
        "instructions": f"""CAFFE LATTE RECIPE
{SEP}
1. Pull double shot 36ml sesuai Espresso Standard Recipe.
2. Steam 280ml susu full cream. Stretch singkat — microfoam tipis silky, bukan tebal seperti cappuccino.
3. Target tekstur: silky, glossy, 'paint-like'. Suhu 60-65°C.
4. Pour dari 10cm → mixing, lalu turunkan untuk latte art.
5. Rosetta atau tulip. Sajikan di saucer.""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",   "qty": 18.0,  "unit": "Gram",     "notes": "House Blend espresso."},
            {"sku_prefix": "SUSU-", "qty": 280.0, "unit": "Mililiter", "notes": "Susu segar full cream."},
        ],
        "base_cost": 12_000,
    },
    {
        "name": "Americano — Standard Recipe",
        "category": "Espresso Beverages",
        "description": "Americano 350ml — double espresso diluted hot water. Mempertahankan karakter espresso.",
        "yield_qty": 350, "yield_unit": "Mililiter", "prep_time": 3,
        "instructions": f"""AMERICANO RECIPE
{SEP}
1. Tuang 270ml hot water 90°C ke cup 350ml TERLEBIH DAHULU.
   (Air dituang sebelum espresso agar crema tidak terganggu.)
2. Pull double espresso 36ml standar.
3. Tuang espresso PERLAHAN di atas air — espresso mengalir ke dasar.
4. Crema mengambang sebagai lapisan tipis keemasan di atas.
5. Sajikan tanpa diaduk. Americano pahit = grind terlalu fine atau dose terlalu banyak.""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",  "qty": 18.0,  "unit": "Gram",     "notes": "House Blend espresso base."},
            {"sku_prefix": "AIR-", "qty": 270.0, "unit": "Mililiter", "notes": "Hot water 90°C."},
        ],
        "base_cost": 7_000,
    },
    {
        "name": "Kopi Susu Lumra — Standard Recipe",
        "category": "Signature Drinks",
        "description": "Signature kopi susu Kafe Nusantara. Espresso + fresh milk + gula aren Ciamis.",
        "yield_qty": 350, "yield_unit": "Mililiter", "prep_time": 4,
        "instructions": f"""KOPI SUSU LUMRA — STANDARD RECIPE
{SEP}
PHILOSOPHY: Toleransi variasi antar Outpost maksimal 0.5 Brix sweetness.

BAHAN PER SAJIAN
— 18g House Blend (SKU: HB-...)
— 200ml susu segar full cream 4°C
— 20ml gula aren cair (density 1.25 g/ml = 25g gula aren)
— 3 kubus es batu besar (untuk iced)

LANGKAH
1. Hangatkan gula aren cair jika mengkristal. Dinginkan sebelum untuk iced.
2. Pull double shot 36ml pada 92°C, 25-28 detik.
3. ICED: Gula aren → es → susu dingin (jangan diaduk, layered) → espresso perlahan dari atas.
4. HOT: Gula aren + espresso panas (aduk). Tuang ke cup. Steam susu, pour dari atas.
5. VISUAL ICED: 3 lapisan — gula aren gelap, susu putih, espresso+crema. Sajikan sebelum customer aduk.
6. QC Brix: target 8-10°. Cek dengan refractometer setiap batch baru gula aren.""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",     "qty": 18.0, "unit": "Gram",     "notes": "House Blend espresso base."},
            {"sku_prefix": "SUSU-",   "qty": 200.0,"unit": "Mililiter", "notes": "Susu segar full cream 4°C."},
            {"sku_prefix": "AD-GAN",  "qty": 20.0, "unit": "Mililiter", "notes": "Gula Aren Syrup — AD-GAN-SYR-T1."},
        ],
        "base_cost": 10_000,
    },
    {
        "name": "Kopi Susu Pandan — Standard Recipe",
        "category": "Signature Drinks",
        "description": "Kopi susu dengan pandan extract segar. Aroma pandan khas Asia Tenggara.",
        "yield_qty": 350, "yield_unit": "Mililiter", "prep_time": 4,
        "instructions": f"""KOPI SUSU PANDAN
{SEP}
1. Pastikan pandan extract tidak lebih dari 3 hari — aroma volatile hilang setelah itu.
2. Pull double espresso 36ml.
3. Mixing: gula aren + pandan extract + susu dingin di gelas berisi es.
4. Tuang espresso dari atas untuk layering effect.
5. Warna hijau tipis pada susu adalah natural (klorofil). Hijau pekat = terlalu banyak extract.
6. QC aroma: pandan harus tercium saat cup diangkat 10cm dari hidung.""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",    "qty": 18.0, "unit": "Gram",     "notes": "House Blend espresso."},
            {"sku_prefix": "SUSU-",  "qty": 200.0,"unit": "Mililiter", "notes": "Susu segar full cream."},
            {"sku_prefix": "AD-PAN", "qty": 8.0,  "unit": "Mililiter", "notes": "Daun Pandan Extract — AD-PAND-EXT-T1."},
            {"sku_prefix": "AD-GAN", "qty": 15.0, "unit": "Mililiter", "notes": "Gula Aren Syrup."},
        ],
        "base_cost": 12_000,
    },
    {
        "name": "V60 Pour Over — Standard Recipe",
        "category": "Filter Coffee",
        "description": "V60 pour over 250ml dengan single origin. Protokol SCA pour over.",
        "yield_qty": 250, "yield_unit": "Mililiter", "prep_time": 5,
        "instructions": f"""V60 POUR OVER PROTOCOL
{SEP}
SETUP
1. Lipat filter V60, pasang ke dripper di atas server.
2. RINSING: Tuang air 93°C ke filter untuk basahi dan panaskan server. Buang air bilasan.
3. Timbang 15g kopi segar (grind: medium-fine, konsistensi tepung roti).
4. Masukkan ke filter, ratakan. Taruh di timbangan, tare ke 0.

BLOOMING
5. Timer start. Tuang 30ml air 93°C (bloom pour). Tunggu 30-45 detik.
   Kopi mengembang = CO2 keluar = kopi masih segar. Tidak mengembang = kopi stale.

MAIN POURS
6. Pour 2 (0:45): Tuang spiral ke 150ml total.
7. Pour 3 (1:30): Tuang ke 220ml total.
8. Pour 4 (2:00): Tuang ke 270ml total.
9. TARGET: Semua habis menetes pada 2:30-3:00 menit.
   Lambat >3:30 = grind terlalu fine. Cepat <2:00 = grind terlalu coarse.

QC
10. TDS target: 1.25-1.45%. Rasa: clean, bright, karakter origin jelas.""",
        "ingredient_keys": [
            {"sku_prefix": "SO-",   "qty": 15.0,  "unit": "Gram",     "notes": "Single Origin Light-Medium Roast Washed pilihan barista."},
            {"sku_prefix": "AIR-",  "qty": 270.0, "unit": "Mililiter", "notes": "Air filtered 93°C."},
        ],
        "base_cost": 14_000,
    },
    {
        "name": "Cold Brew — 18-Hour Batch Recipe",
        "category": "Cold Beverages",
        "description": "Cold brew batch 1L untuk produksi bar. 18 jam cold steep, ratio 1:10.",
        "yield_qty": 1000, "yield_unit": "Mililiter", "prep_time": 1080,
        "instructions": f"""COLD BREW BATCH PRODUCTION
{SEP}
PREP (lakukan malam sebelumnya)
1. Timbang 100g House Blend, grind KASAR (lebih kasar dari French Press).
2. Masukkan ke cold brew jar atau steeper bag.
3. Tuang 1000ml air filtered dingin 4°C.
4. Aduk perlahan, tutup rapat. Label: waktu mulai, nama barista.
5. STEEP 16-18 jam pada 4°C. Jangan dibuka selama proses.

BOTTLING
6. Filter melalui mesh strainer + cheesecloth (drip natural, jangan diperas).
7. Label bottle: tanggal produksi, expired (4 hari), barcode batch.
8. SHELF LIFE: 4 hari di kulkas. Buang jika ada perubahan aroma.

QC
9. TDS target: 1.2-1.6%. Rasa: smooth, naturally sweet, low acidity.""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",  "qty": 100.0,  "unit": "Gram",     "notes": "House Blend coarse grind untuk cold brew."},
            {"sku_prefix": "AIR-", "qty": 1000.0, "unit": "Mililiter", "notes": "Air filtered dingin 4°C."},
        ],
        "base_cost": 15_000,
    },
    {
        "name": "Iced Latte — Standard Recipe",
        "category": "Cold Beverages",
        "description": "Iced latte 350ml — espresso + cold milk + es batu.",
        "yield_qty": 350, "yield_unit": "Mililiter", "prep_time": 3,
        "instructions": f"""ICED LATTE RECIPE
{SEP}
1. Isi gelas 350ml dengan 3-4 kubus es batu BESAR (es besar meleleh lebih lambat).
2. Tuang 200ml susu full cream dingin 4°C di atas es.
3. Pull double espresso 36ml. Biarkan cool 10-15 detik.
4. Tuang espresso PERLAHAN dari sisi gelas — gradient indah sebelum bercampur.
5. Sajikan dengan sendok panjang dan sedotan.
6. Default TANPA syrup. Jika customer minta manis: simple syrup atau gula aren sesuai request.""",
        "ingredient_keys": [
            {"sku_prefix": "HB-",   "qty": 18.0,  "unit": "Gram",     "notes": "House Blend espresso."},
            {"sku_prefix": "SUSU-", "qty": 200.0, "unit": "Mililiter", "notes": "Susu segar full cream 4°C."},
        ],
        "base_cost": 13_000,
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ADDON PRODUCTION INSTRUCTION TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════
# FIX UTAMA: Semua template dipecah menjadi fungsi (bukan string di-format())
# agar tidak ada KeyError dari karakter { } di dalam konten.
# ═══════════════════════════════════════════════════════════════════════════════

PLANT_PREP_MAP = {
    "mangga":        ("Kupas dan potong mangga matang kubus 2cm.",
                      "Blender dengan 100ml air, saring ampas.",
                      "Mangga segar", 400, "55-65"),
    "lychee":        ("Kupas dan buang biji lychee.",
                      "Blender dengan sedikit air, saring.",
                      "Lychee segar/kaleng", 350, "55-65"),
    "markisa":       ("Belah dan keruk isi beserta biji.",
                      "Blender sebentar, saring fine mesh.",
                      "Markisa segar", 300, "60-70"),
    "stroberi":      ("Cuci bersih, buang tangkai, potong-potong.",
                      "Blender halus, saring.",
                      "Stroberi segar", 350, "55-65"),
    "lemon":         ("Peras lemon, parut zest untuk rasa tambahan.",
                      "Campur jus + zest langsung.",
                      "Lemon segar", 250, "50-60"),
    "melati":        ("Cuci bunga melati, pisahkan dari tangkai.",
                      "Cold steep dalam air 4°C selama 24 jam.",
                      "Bunga melati segar", 80, "45-55"),
    "mawar":         ("Gunakan kelopak mawar food-grade, cuci bersih.",
                      "Cold steep atau hot steep 5 menit.",
                      "Kelopak mawar", 100, "50-60"),
    "kayu_manis":    ("Patahkan kayu manis menjadi ruas 3-5cm.",
                      "Simmer dalam air 15 menit, saring.",
                      "Batang kayu manis", 150, "55-65"),
    "vanila":        ("Belah polong vanila, keruk biji di dalamnya.",
                      "Rendam polong+biji dalam simple syrup hangat 24 jam.",
                      "Polong vanila", 30, "60-70"),
    "jahe":          ("Kupas dan slice jahe 3mm.",
                      "Simmer dalam air 20 menit, saring.",
                      "Jahe segar", 200, "55-65"),
    "pandan":        ("Cuci daun pandan, potong-potong.",
                      "Blender dengan sedikit air, saring melalui kain.",
                      "Daun pandan segar", 100, "50-60"),
    "butterfly_pea": ("Cuci bunga telang, pisahkan dari tangkai.",
                      "Hot steep 80°C selama 5 menit.",
                      "Bunga telang kering", 20, "40-50"),
    "hibiscus":      ("Timbang bunga rosella kering.",
                      "Hot steep 85°C selama 5 menit, saring.",
                      "Bunga rosella kering", 30, "50-60"),
    "sakura":        ("Gunakan kelopak sakura food-grade atau sakura powder.",
                      "Cold steep dalam air 4°C selama 12 jam, atau larutkan powder.",
                      "Kelopak sakura food-grade", 50, "45-55"),
    "gula_aren":     ("Larutkan gula aren dalam air hangat 60°C.",
                      "Saring untuk membuang kotoran. Dinginkan.",
                      "Gula aren cetak/cair", 500, "60-70"),
    "kopi":          ("Giling 100g biji kopi medium-coarse.",
                      "Cold brew 12 jam atau espresso extraction.",
                      "Biji kopi House Blend", 100, "N/A"),
}

DEFAULT_PREP = (
    "Bersihkan dan siapkan bahan sesuai jenis.",
    "Ekstrak dengan metode yang sesuai.",
    "Bahan segar", 300, "50-60",
)


def make_syrup_instructions(plant_display, prep_instr, extraction_method,
                             main_ingredient, plant_qty, brix_target):
    return f"""PRODUKSI SYRUP {plant_display.upper()} — BATCH 1L
{SEP}
BAHAN PER BATCH (yield: 1L / 1000ml)
— {main_ingredient}: {plant_qty}g
— Gula pasir atau gula kelapa: 400g
— Air filtered: 600ml
— Asam sitrat (preservatif natural): 2g
— Garam himalaya: 1g (enhancer rasa)

PROSES EKSTRAKSI
1. PREP: {prep_instr} Pastikan bahan bersih dan segar.
2. EKSTRAKSI: {extraction_method}
3. Saring dengan fine mesh strainer.

PEMBUATAN SIMPLE SYRUP
4. Larutkan 400g gula dalam 600ml air di panci stainless. Api sedang, aduk sampai larut (5 menit). JANGAN mendidih kencang.
5. Angkat dari api. Tambahkan 2g asam sitrat + 1g garam. Aduk.

BLENDING
6. Campurkan ekstrak {plant_display} dengan simple syrup yang sudah dingin (<40°C).
7. Aduk merata. Tes rasa: balance antara rasa {plant_display}, manis, sedikit asam.
8. Filter final melalui cheesecloth atau coffee filter.

BOTTLING
9. Tuang ke botol steril. Label: nama, batch number, tanggal produksi, expired (30 hari).
10. QC BRIX: Target {brix_target} Brix (ukur dengan refractometer).
11. SHELF LIFE: 30 hari kulkas, 14 hari suhu ruang."""


def make_extract_instructions(plant_display, prep_instr, main_ingredient, plant_qty):
    return f"""PRODUKSI EKSTRAK PEKAT {plant_display.upper()} — BATCH 500ml
{SEP}
BAHAN
— {main_ingredient}: {plant_qty}g
— Air filtered: 600ml (cold extraction)
— Alkohol food-grade 40%: 50ml (preservatif, opsional)

COLD EXTRACTION
1. PREP: {prep_instr}
2. Masukkan {plant_display} ke mason jar bersih.
3. Tuang 600ml air dingin 4°C.
4. Seal jar, simpan di kulkas 24-48 jam. Kocok perlahan setiap 6 jam.
5. Filter fine mesh + coffee filter (2-3 jam drip natural).
6. Jika pakai alkohol: tambahkan 50ml setelah filtrasi, aduk rata.

CONCENTRATION (opsional)
7. Panaskan ekstrak di bain-marie pada 50-60°C sampai volume berkurang 30-40%.
8. JANGAN >65°C — senyawa aromatik menguap.

BOTTLING
9. Tuang ke dropper bottle (50ml) atau amber bottle.
10. Label: "3-5 tetes per sajian". Expired: 14 hari kulkas, 7 hari suhu ruang.
11. QC: 3 tetes dalam 100ml air harus terasa jelas."""


def make_powder_instructions(plant_display, prep_instr, main_ingredient, plant_qty):
    return f"""PRODUKSI POWDER MIX {plant_display.upper()} — BATCH 500g
{SEP}
BAHAN
— {main_ingredient} kering: {plant_qty}g
— Maltodextrin (carrier): 100g
— Gula bubuk: 150g
— Garam: 2g

PENGERINGAN
1. PREP: {prep_instr}
2. PILIH METODE PENGERINGAN:
   — Food dehydrator 60°C, 8-12 jam (terbaik untuk aroma)
   — Oven 50°C, pintu sedikit terbuka, 10-14 jam
3. Bahan harus benar-benar kering — tidak ada moisture saat diremas.

PENGGILINGAN
4. Giling dengan blender atau spice grinder sampai halus.
5. Ayak melalui sieve 100 mesh. Giling ulang yang tidak lolos.

BLENDING
6. Campurkan powder {plant_display} + maltodextrin + gula bubuk + garam. Aduk merata dalam bowl kering.
7. Tes kelarutan: 2g powder dalam 100ml air hangat harus larut sempurna <30 detik.

PENGEMASAN
8. Timbang sesuai ukuran (100g, 250g, 1kg). Seal panas. Masukkan silica gel.
9. Label: "Larutkan 2 sdt (8g) dalam 200ml air/susu hangat." SHELF LIFE: 6 bulan."""


def make_foam_instructions(plant_display, plant_qty):
    return f"""PRODUKSI FOAM MIX {plant_display.upper()} — BATCH 500ml
{SEP}
BAHAN
— Susu UHT full cream: 300ml
— Ekstrak {plant_display}: 30ml (dibuat terlebih dahulu)
— Stabilizer (lecithin / CMC): 2g
— Gula pasir: 20g
— Garam: 0.5g

PROSES
1. Hangatkan susu UHT ke 40°C — jangan mendidih.
2. Larutkan stabilizer dalam 2 sdt air hangat, aduk sampai gel transparan.
3. Campurkan susu + stabilizer + gula + garam. Aduk rata.
4. Tambahkan ekstrak {plant_display} setelah campuran di bawah 35°C.
5. Blend dengan immersion blender 60 detik.
6. Dinginkan di kulkas 4°C minimal 2 jam sebelum digunakan.

PENGGUNAAN
7. Kocok dengan hand frother atau French Press plunger sampai foam terbentuk.
8. Tuang di atas minuman sebagai cold foam topping (60ml per sajian).
9. SHELF LIFE: 3 hari di kulkas. Kocok kembali sebelum digunakan."""


def make_addon_instructions(product_name, category, plant_key):
    prep_data     = PLANT_PREP_MAP.get(plant_key, DEFAULT_PREP)
    prep_instr, extraction, main_ing, plant_qty, brix_target = prep_data
    plant_display = (plant_key.replace("_", " ").title() if plant_key
                     else product_name.split()[0])

    name_lower = product_name.lower()
    if "syrup" in name_lower or "sirup" in name_lower:
        return ("syrup", 1000.0, "Mililiter", 60,
                make_syrup_instructions(plant_display, prep_instr, extraction,
                                        main_ing, plant_qty, brix_target))
    elif "extract" in name_lower or "ekstrak" in name_lower:
        return ("extract", 500.0, "Mililiter", 1440,
                make_extract_instructions(plant_display, prep_instr,
                                          main_ing, plant_qty))
    elif "foam" in name_lower or "busa" in name_lower:
        return ("foam", 500.0, "Mililiter", 30,
                make_foam_instructions(plant_display, plant_qty))
    else:  # powder
        return ("powder", 500.0, "Gram", 720,
                make_powder_instructions(plant_display, prep_instr,
                                         main_ing, plant_qty))


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — DATABASE LAYER
# ═══════════════════════════════════════════════════════════════════════════════

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(autocommit=False)
    return conn


def fetch_fk_ids(conn):
    cur = conn.cursor()
    ids = {}
    cat_names = [c[0] for c in RECIPE_CATEGORIES]
    cur.execute(
        "SELECT name, id FROM production_recipe_categories WHERE name = ANY(%s)",
        (cat_names,),
    )
    for name, id_ in cur.fetchall():
        ids[f"rcat_{name.lower().replace(' ','_')}"] = id_

    for unit, key in [("Gram", "unit_gram"), ("Mililiter", "unit_ml"), ("Pcs", "unit_pcs")]:
        cur.execute("SELECT id FROM lumra_config_units WHERE name=%s LIMIT 1", (unit,))
        row = cur.fetchone()
        ids[key] = row[0] if row else None
    cur.close()
    return ids


def ensure_recipe_categories(conn):
    cur = conn.cursor()
    for name, desc in RECIPE_CATEGORIES:
        cur.execute("""
            INSERT INTO production_recipe_categories (name, description, is_active, created_at, updated_at)
            VALUES (%s, %s, TRUE, NOW(), NOW())
            ON CONFLICT (name) DO NOTHING
        """, (name, desc))
    conn.commit()
    cur.close()


BLEND_PRODUCT_CATEGORIES = ("House Blend",)
SINGLE_ORIGIN_CATEGORIES = ("Single Origin", "Single Origin Series")
ADDON_PRODUCT_CATEGORIES = ("Addon Syrup", "Addon Extract", "Addon Foam", "Addon Powder")
MENU_PRODUCT_CATEGORIES = ("Signature Coffee", "Espresso Based", "Iced Coffee",
                           "Manual Brew", "Non Coffee", "Tea & Others")
RELEVANT_PRODUCT_CATEGORIES = (
    BLEND_PRODUCT_CATEGORIES
    + SINGLE_ORIGIN_CATEGORIES
    + ADDON_PRODUCT_CATEGORIES
    + MENU_PRODUCT_CATEGORIES
)


def fetch_all_products(conn, categories=None):
    """Fetch relevant products with one primary variant per product."""
    category_filter = tuple(categories or RELEVANT_PRODUCT_CATEGORIES)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (p.id)
            p.id, p.name, p.description,
            c.name AS category,
            pv.id AS variant_id, pv.sku, pv.price_sell, pv.size_weight
        FROM lumra_config_products p
        JOIN lumra_config_categories c ON p.category_id = c.id
        JOIN lumra_config_productvariants pv ON pv.product_id = p.id
        WHERE c.name = ANY(%s)
        ORDER BY p.id, pv.id
    """, (list(category_filter),))
    rows = cur.fetchall()
    cur.close()

    return [{
        "product_id":   row[0],
        "product_name": row[1],
        "product_desc": row[2],
        "category":     row[3],
        "variant_id":   row[4],
        "variant_sku":  row[5],
        "price_sell":   float(row[6]) if row[6] else 0,
        "size_weight":  row[7],
    } for row in rows]


def fetch_existing_recipes(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM production_recipes")
    result = {row[0] for row in cur.fetchall()}
    cur.close()
    return result


def find_variant_by_sku_prefix(conn, sku_prefix, preferred_size="100g"):
    """
    Cari variant berdasarkan SKU prefix. Prioritas: ukuran preferred_size.
    Returns (variant_id, price_sell, sku) or None.
    """
    cur = conn.cursor()
    # Coba exact size dulu
    cur.execute(
        """SELECT id, price_sell, sku
           FROM lumra_config_productvariants
           WHERE sku ILIKE %s AND size_weight = %s
           LIMIT 1""",
        (f"{sku_prefix}%", preferred_size),
    )
    row = cur.fetchone()
    if not row:
        # Fallback: ambil yang pertama
        cur.execute(
            "SELECT id, price_sell, sku FROM lumra_config_productvariants WHERE sku ILIKE %s ORDER BY id LIMIT 1",
            (f"{sku_prefix}%",),
        )
        row = cur.fetchone()
    cur.close()
    return row  # (id, price_sell, sku) or None


def find_variant_for_ingredient(conn, ing_hint, category_hint=None):
    """
    Resolve bahan baku → variant_id menggunakan product name search.
    ing_hint: keyword seperti "House Blend", "Susu", "Gula Aren", dll.
    Returns (variant_id, price_sell, sku, product_name) or None.
    """
    cur = conn.cursor()
    # Coba cari dari nama produk
    cur.execute(
        """SELECT pv.id, pv.price_sell, pv.sku, p.name
           FROM lumra_config_productvariants pv
           JOIN lumra_config_products p ON pv.product_id = p.id
           WHERE LOWER(p.name) LIKE %s
           ORDER BY pv.price_sell ASC
           LIMIT 1""",
        (f"%{ing_hint.lower()}%",),
    )
    row = cur.fetchone()
    cur.close()
    return row


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — PARSE BLEND COMPONENTS FROM DESCRIPTION
# ═══════════════════════════════════════════════════════════════════════════════

def parse_blend_components(product_desc, product_name):
    """
    Parse komponen blend dari kolom description.
    Format yang dikenali dari grand_million_generator:
      "Wanoja Kamojang (Medium/Washed): 600g (60%) | Aceh Gayo (Light/Natural): 400g (40%) | total: 1000g"
    Returns list of dicts: {origin_display, roast, process, gram, pct}
    """
    components = []
    pattern = r'([^|():\n]+)\((\w+)[/-]([^)]+)\):\s*(\d+)g\s*\((\d+)%\)'
    for m in re.finditer(pattern, product_desc or ""):
        components.append({
            "origin_display": m.group(1).strip(),
            "roast":          m.group(2).strip(),
            "process":        m.group(3).strip().replace(" ", "-"),
            "gram":           int(m.group(4)),
            "pct":            int(m.group(5)),
        })

    # Fallback: coba ekstrak dari nama produk (Single Origin)
    if not components:
        roast = "Medium"
        for r in ("Light", "Dark", "Medium"):
            if r.lower() in (product_name or "").lower():
                roast = r
                break
        process = "Washed"
        for p in ("Anaerobic", "Wine", "Natural", "Honey", "Semi-Washed", "Wet-Hulled", "Washed"):
            if p.lower().replace("-", " ") in (product_name or "").lower():
                process = p
                break
        if product_name:
            components.append({
                "origin_display": product_name,
                "roast": roast, "process": process,
                "gram": 1000, "pct": 100,
            })
    return components


def determine_dominant_roast(components):
    if not components:
        return "Medium"
    rs = {"Light": 1, "Medium": 2, "Dark": 3}
    total_pct = sum(c.get("pct", 50) for c in components) or 100
    weighted  = sum(rs.get(c.get("roast", "Medium"), 2) * c.get("pct", 50) for c in components)
    avg = weighted / total_pct
    return "Light" if avg < 1.7 else ("Dark" if avg >= 2.5 else "Medium")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — RECIPE BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def build_recipe_for_blend(product, fk_ids):
    name       = product["product_name"]
    desc       = product["product_desc"] or ""
    components = parse_blend_components(desc, name)
    dom_roast  = determine_dominant_roast(components)

    instructions = make_blend_instructions(components, dom_roast)
    base_cost_per_gram = {"Light": 0.40, "Medium": 0.38, "Dark": 0.35}.get(dom_roast, 0.38)
    total_cost = 1000 * base_cost_per_gram
    yield_qty  = 820.0

    return {
        "name":             name[:255],
        "description":      (desc[:490] or f"Resep produksi {name}"),
        "instructions":     instructions,
        "yield_quantity":   yield_qty,
        "yield_unit":       "Gram",
        "preparation_time": 75,
        "total_cost":       round(total_cost, 2),
        "cost_per_unit":    round(total_cost / yield_qty, 4),
        "category_key":     "rcat_coffee_blending",
        "components":       components,
        "product":          product,
    }


def build_recipe_for_single_origin(product, fk_ids):
    name       = product["product_name"]
    components = parse_blend_components(None, name)
    dom_roast  = components[0]["roast"] if components else "Medium"
    process    = components[0]["process"] if components else "Washed"

    instructions = make_single_origin_instructions(name, dom_roast, process)
    price      = product["price_sell"] or 50_000
    total_cost = price * {"Dark": 0.30, "Medium": 0.35, "Light": 0.38}.get(dom_roast, 0.35)
    yield_qty  = 820.0

    return {
        "name":             f"{name} — Roasting Profile"[:255],
        "description":      f"Roasting profile untuk {name}. Proses {process}, target {dom_roast} roast.",
        "instructions":     instructions,
        "yield_quantity":   yield_qty,
        "yield_unit":       "Gram",
        "preparation_time": 60,
        "total_cost":       round(total_cost, 2),
        "cost_per_unit":    round(total_cost / yield_qty, 4),
        "category_key":     "rcat_coffee_blending",
        "components":       components,
        "product":          product,
    }


def build_recipe_for_addon(product, fk_ids):
    name     = product["product_name"]
    category = product["category"]
    price    = product["price_sell"] or 50_000

    # Detect plant key
    plant_key = None
    for key in PLANT_PREP_MAP:
        kw = key.replace("_", " ")
        if kw in name.lower() or key in name.lower():
            plant_key = key
            break

    addon_type, yield_qty, yield_unit, prep_time, instructions = \
        make_addon_instructions(name, category, plant_key)

    total_cost = price * 0.40

    return {
        "name":             f"{name} — Production Recipe"[:255],
        "description":      f"Resep produksi batch {name}. Yield: {yield_qty}{'ml' if yield_unit == 'Mililiter' else 'g'} per batch.",
        "instructions":     instructions,
        "yield_quantity":   yield_qty,
        "yield_unit":       yield_unit,
        "preparation_time": prep_time,
        "total_cost":       round(total_cost, 2),
        "cost_per_unit":    round(total_cost / max(yield_qty, 1), 4),
        "category_key":     "rcat_addon_production",
        "components":       [],
        "product":          product,
        "plant_key":        plant_key,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — INGREDIENT RESOLVER
# ═══════════════════════════════════════════════════════════════════════════════

# Cache untuk variant lookup
_variant_cache = {}


def _cached_find(conn, cache_key, finder_fn):
    if cache_key not in _variant_cache:
        _variant_cache[cache_key] = finder_fn()
    return _variant_cache[cache_key]


def resolve_ingredients_for_recipe(conn, recipe_dict, fk_ids):
    """
    Resolve ingredients → list of (variant_id, qty, unit_id, unit_cost, subtotal, notes).

    Logika:
    - House Blend: ingredients = biji kopi SO per komponen (SKU SO-xxx) dengan gram sesuai resep
    - Single Origin: ingredient = produk itu sendiri (1000g green bean)
    - Addon: ingredient = produk itu sendiri (bahan baku)
    - Menu: ingredients dari ingredient_keys (SKU prefix based)
    """
    product    = recipe_dict.get("product", {})
    components = recipe_dict.get("components", [])
    ing_keys   = recipe_dict.get("ingredient_keys", [])  # untuk menu recipes
    category   = product.get("category", "")

    result = []  # list of (variant_id, qty, unit_id, unit_cost, subtotal, notes)
    unit_gram = fk_ids.get("unit_gram")
    unit_ml   = fk_ids.get("unit_ml")

    # ── Menu recipes: gunakan ingredient_keys ────────────────────────────────
    if ing_keys:
        for ing in ing_keys:
            row = find_variant_by_sku_prefix(conn, ing["sku_prefix"])
            if not row:
                continue
            vid, price_sell, sku = row
            price_sell = float(price_sell) if price_sell else 0
            qty        = float(ing["qty"])
            uid        = unit_gram if ing["unit"] == "Gram" else unit_ml
            unit_cost  = price_sell / 1000  # per gram atau per ml
            subtotal   = qty * unit_cost
            result.append((vid, qty, uid, unit_cost, subtotal, ing.get("notes", sku)))
        return result

    # ── House Blend: link ke variant biji kopi per komponen ─────────────────
    if category in ("House Blend",) and components:
        for comp in components:
            origin_kw = comp.get("origin_display", "").lower()
            roast     = comp.get("roast", "Medium")
            process   = comp.get("process", "Washed")
            gram      = float(comp.get("gram", 250))

            # Cari variant SO yang cocok dengan origin + roast + process
            def find_comp_variant():
                cur = conn.cursor()
                # Coba cari SO yang namanya mengandung keyword origin
                words = [w for w in origin_kw.split() if len(w) >= 4]
                for word in words:
                    cur.execute("""
                        SELECT pv.id, pv.price_sell, pv.sku
                        FROM lumra_config_productvariants pv
                        JOIN lumra_config_products p ON pv.product_id = p.id
                        JOIN lumra_config_categories c ON p.category_id = c.id
                        WHERE c.name IN ('Single Origin','Single Origin Series')
                          AND LOWER(p.name) ILIKE %s
                          AND LOWER(p.name) ILIKE %s
                          AND LOWER(p.name) ILIKE %s
                          AND pv.size_weight = '1kg'
                        LIMIT 1
                    """, (f"%{word}%", f"%{roast.lower()}%", f"%{process.lower().replace('-',' ')}%"))
                    row = cur.fetchone()
                    if row:
                        cur.close()
                        return row
                # Fallback: asal ada SO
                cur.execute("""
                    SELECT pv.id, pv.price_sell, pv.sku
                    FROM lumra_config_productvariants pv
                    JOIN lumra_config_products p ON pv.product_id = p.id
                    JOIN lumra_config_categories c ON p.category_id = c.id
                    WHERE c.name IN ('Single Origin','Single Origin Series')
                      AND pv.size_weight = '1kg'
                    ORDER BY RANDOM() LIMIT 1
                """)
                row = cur.fetchone()
                cur.close()
                return row

            cache_key = f"comp_{origin_kw[:20]}_{roast}_{process}"
            row = _cached_find(conn, cache_key, find_comp_variant)
            if not row:
                continue
            vid, price_sell, sku = row
            price_sell = float(price_sell) if price_sell else 0
            unit_cost  = price_sell / 1000  # per gram (dari 1kg = 1000g)
            subtotal   = gram * unit_cost
            notes      = f"{comp['origin_display']} {roast}/{process} — {gram}g ({comp.get('pct',0)}%) | SKU: {sku}"
            result.append((vid, gram, unit_gram, unit_cost, subtotal, notes))
        return result

    # ── Single Origin & Addon: link ke produk itu sendiri ───────────────────
    vid   = product.get("variant_id")
    price = float(product.get("price_sell", 0))
    qty   = float(recipe_dict.get("yield_quantity", 1000))
    uid   = unit_gram if recipe_dict.get("yield_unit") == "Gram" else unit_ml
    unit_cost = price * 0.40 / max(qty, 1)
    subtotal  = price * 0.40
    sku_label = product.get("variant_sku", "")

    if vid:
        result.append((vid, qty, uid, unit_cost, subtotal,
                       f"Bahan baku utama produksi — {sku_label}"))
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — INSERT PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def get_conflict_constraint_name(conn):
    """
    Cek nama constraint UNIQUE di production_recipe_ingredients.
    Beberapa versi skema pakai (recipe_id, variant_id), ada yang lain.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'production_recipe_ingredients'
          AND constraint_type = 'UNIQUE'
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None


def insert_recipe_batch(conn, recipes, fk_ids, existing_recipe_names, skip_ingredients,
                        conflict_constraint):
    """Insert a batch of recipe dicts. Returns (inserted_count, ingredient_count)."""
    now     = datetime.now(timezone.utc)
    new_rec = [r for r in recipes if r["name"] not in existing_recipe_names]
    if not new_rec:
        return 0, 0

    unit_map = {"Gram": fk_ids.get("unit_gram"), "Mililiter": fk_ids.get("unit_ml")}

    cur = conn.cursor()
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO production_recipes
            (name, description, instructions, yield_quantity, preparation_time,
             total_cost, cost_per_unit, is_archived, created_at, updated_at,
             category_id, yield_unit_id)
           VALUES %s
           ON CONFLICT (name) DO NOTHING
           RETURNING id, name""",
        [(
            r["name"],
            (r["description"] or "")[:990],
            r["instructions"][:9990],
            str(r["yield_quantity"]),
            r["preparation_time"],
            str(r["total_cost"]),
            str(r["cost_per_unit"]),
            False, now, now,
            fk_ids.get(r["category_key"]),
            unit_map.get(r.get("yield_unit", "Gram")),
        ) for r in new_rec],
        page_size=200,
    )
    inserted_rows = cur.fetchall()
    conn.commit()
    cur.close()

    recipe_name_to_id = {name: rid for rid, name in inserted_rows}
    for r in new_rec:
        existing_recipe_names.add(r["name"])

    if skip_ingredients or not inserted_rows:
        return len(inserted_rows), 0

    # ── Resolve + insert ingredients ─────────────────────────────────────────
    ingredient_rows = []
    existing_pairs  = set()  # (recipe_id, variant_id) yang sudah ada

    for r in new_rec:
        recipe_id = recipe_name_to_id.get(r["name"])
        if not recipe_id:
            continue
        ings = resolve_ingredients_for_recipe(conn, r, fk_ids)
        for vid, qty, uid, unit_cost, subtotal, notes in ings:
            key = (recipe_id, vid)
            if key in existing_pairs:
                continue
            existing_pairs.add(key)
            ingredient_rows.append((
                recipe_id, vid, str(qty),
                str(round(unit_cost, 4)),
                str(round(subtotal, 2)),
                notes[:500], now, uid,
            ))

    ing_count = 0
    if ingredient_rows:
        cur = conn.cursor()
        # ON CONFLICT: gunakan (recipe_id, variant_id) — standard column names
        try:
            psycopg2.extras.execute_values(
                cur,
                """INSERT INTO production_recipe_ingredients
                    (recipe_id, variant_id, quantity, unit_cost, subtotal_cost,
                     notes, created_at, unit_id)
                   VALUES %s
                   ON CONFLICT (recipe_id, variant_id) DO NOTHING""",
                ingredient_rows,
                page_size=500,
            )
        except psycopg2.errors.UndefinedColumn:
            conn.rollback()
            # Fallback jika nama kolom berbeda di skema
            cur = conn.cursor()
            psycopg2.extras.execute_values(
                cur,
                """INSERT INTO production_recipe_ingredients
                    (recipe_id, variant_id, quantity, unit_cost, subtotal_cost,
                     notes, created_at, unit_id)
                   VALUES %s""",
                ingredient_rows,
                page_size=500,
            )
        ing_count = len(ingredient_rows)
        conn.commit()
        cur.close()

    return len(inserted_rows), ing_count


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_pipeline(recipe_type, skip_ingredients, dry_run, batch_size):
    print("=" * 65)
    print("  KAFE NUSANTARA — PRODUCTION RECIPE GENERATOR v2.0")
    print(f"  Type   : {recipe_type or 'all'}")
    print(f"  Mode   : {'DRY RUN' if dry_run else 'LIVE INSERT'}")
    print("=" * 65)

    print(f"\n📡 Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}...")
    try:
        conn = get_connection()
        print("  ✅ Connected")
    except Exception as e:
        print(f"  ❌ {e}")
        sys.exit(1)

    ensure_recipe_categories(conn)
    fk_ids = fetch_fk_ids(conn)
    print(f"  FK IDs: { {k: v for k, v in fk_ids.items() if v} }")

    conflict_constraint = get_conflict_constraint_name(conn)
    print(f"  Ingredients UNIQUE constraint: {conflict_constraint}")

    existing_recipes = fetch_existing_recipes(conn)
    print(f"  Existing recipes: {len(existing_recipes):,}")

    total_r = total_i = 0
    start = time.time()

    # ── MENU KAFE ─────────────────────────────────────────────────────────────
    if recipe_type in (None, "menu"):
        print(f"\n🍵 Processing {len(MENU_RECIPES)} menu recipes...")
        cat_key_map = {
            "Espresso Beverages": "rcat_espresso_beverages",
            "Signature Drinks":   "rcat_signature_drinks",
            "Filter Coffee":      "rcat_filter_coffee",
            "Cold Beverages":     "rcat_cold_beverages",
        }
        unit_key_map = {"Gram": "unit_gram", "Mililiter": "unit_ml", "Pcs": "unit_pcs"}

        for recipe in MENU_RECIPES:
            if recipe["name"] in existing_recipes:
                print(f"   ↷ SKIP (exists): {recipe['name'][:60]}")
                continue

            if dry_run:
                ings = resolve_ingredients_for_recipe(
                    conn,
                    {"ingredient_keys": recipe.get("ingredient_keys", []),
                     "product": {}, "components": [], "yield_unit": recipe["yield_unit"],
                     "yield_quantity": recipe["yield_qty"]},
                    fk_ids,
                )
                print(f"   [MENU] {recipe['name'][:55]}")
                print(f"          yield: {recipe['yield_qty']}{recipe['yield_unit']} | "
                      f"prep: {recipe['prep_time']}min | "
                      f"ingredients found: {len(ings)}")
                for vid, qty, uid, uc, sub, notes in ings:
                    print(f"          → variant_id={vid} qty={qty} cost={uc:.2f} | {notes[:60]}")
                continue

            now = datetime.now(timezone.utc)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO production_recipes
                    (name, description, instructions, yield_quantity, preparation_time,
                     total_cost, cost_per_unit, is_archived, created_at, updated_at,
                     category_id, yield_unit_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,FALSE,%s,%s,%s,%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """, (
                recipe["name"], recipe["description"], recipe["instructions"],
                str(recipe["yield_qty"]), recipe["prep_time"],
                str(recipe["base_cost"]),
                str(round(recipe["base_cost"] / max(recipe["yield_qty"], 1), 4)),
                now, now,
                fk_ids.get(cat_key_map.get(recipe["category"], "rcat_espresso_beverages")),
                fk_ids.get(unit_key_map.get(recipe["yield_unit"], "unit_gram")),
            ))
            row = cur.fetchone()
            conn.commit()
            cur.close()

            if row:
                recipe_id = row[0]
                total_r  += 1
                existing_recipes.add(recipe["name"])

                if not skip_ingredients:
                    ings = resolve_ingredients_for_recipe(
                        conn,
                        {"ingredient_keys": recipe.get("ingredient_keys", []),
                         "product": {}, "components": [],
                         "yield_unit": recipe["yield_unit"],
                         "yield_quantity": recipe["yield_qty"]},
                        fk_ids,
                    )
                    if ings:
                        cur2 = conn.cursor()
                        try:
                            psycopg2.extras.execute_values(
                                cur2,
                                """INSERT INTO production_recipe_ingredients
                                    (recipe_id, variant_id, quantity, unit_cost,
                                     subtotal_cost, notes, created_at, unit_id)
                                   VALUES %s
                                   ON CONFLICT (recipe_id, variant_id) DO NOTHING""",
                                [(recipe_id, vid, str(qty), str(round(uc, 4)),
                                  str(round(sub, 2)), notes[:500], now, uid)
                                 for vid, qty, uid, uc, sub, notes in ings],
                                page_size=100,
                            )
                            total_i += len(ings)
                            conn.commit()
                        except Exception as ex:
                            conn.rollback()
                            print(f"   ⚠ Ingredient insert error: {ex}")
                        cur2.close()

    # ── HOUSE BLEND ───────────────────────────────────────────────────────────
    if recipe_type in (None, "blend"):
        print(f"\n☕ Fetching House Blend products...")
        blend_prods = fetch_all_products(conn, BLEND_PRODUCT_CATEGORIES)
        print(f"   Found {len(blend_prods):,} blend products")

        batch = []
        for prod in blend_prods:
            r = build_recipe_for_blend(prod, fk_ids)
            batch.append(r)
            if len(batch) >= batch_size:
                if dry_run:
                    s = batch[0]
                    print(f"   [BLEND] {s['name'][:55]} | {len(s['components'])} components")
                    batch = []
                    continue
                rc, ic = insert_recipe_batch(conn, batch, fk_ids, existing_recipes,
                                              skip_ingredients, conflict_constraint)
                total_r += rc; total_i += ic; batch = []
                print(f"   ✓ Running: recipes={total_r:,}, ingredients={total_i:,}")
        if batch:
            if not dry_run:
                rc, ic = insert_recipe_batch(conn, batch, fk_ids, existing_recipes,
                                              skip_ingredients, conflict_constraint)
                total_r += rc; total_i += ic
            else:
                s = batch[0]
                print(f"   [BLEND] Sample: {s['name'][:55]} | {len(s['components'])} components")

    # ── SINGLE ORIGIN ─────────────────────────────────────────────────────────
    if recipe_type in (None, "single"):
        print(f"\n🌱 Fetching Single Origin products...")
        so_prods = fetch_all_products(conn, SINGLE_ORIGIN_CATEGORIES)
        print(f"   Found {len(so_prods):,} single origin products")

        batch = []
        for prod in so_prods:
            r = build_recipe_for_single_origin(prod, fk_ids)
            batch.append(r)
            if len(batch) >= batch_size:
                if dry_run:
                    print(f"   [SO] {batch[0]['name'][:55]}")
                    batch = []; continue
                rc, ic = insert_recipe_batch(conn, batch, fk_ids, existing_recipes,
                                              skip_ingredients, conflict_constraint)
                total_r += rc; total_i += ic; batch = []
        if batch:
            if not dry_run:
                rc, ic = insert_recipe_batch(conn, batch, fk_ids, existing_recipes,
                                              skip_ingredients, conflict_constraint)
                total_r += rc; total_i += ic
            else:
                print(f"   [SO] Sample: {batch[0]['name'][:55]}")

    # ── ADDON ─────────────────────────────────────────────────────────────────
    if recipe_type in (None, "addon"):
        print(f"\n🌿 Fetching addon products from DB...")
        addon_p = fetch_all_products(conn, ADDON_PRODUCT_CATEGORIES)
        print(f"   Found {len(addon_p):,} addon products")

        batch = []
        for prod in addon_p:
            r = build_recipe_for_addon(prod, fk_ids)
            batch.append(r)
            if len(batch) >= batch_size:
                if dry_run:
                    print(f"   [ADDON] {batch[0]['name'][:55]}")
                    batch = []; continue
                rc, ic = insert_recipe_batch(conn, batch, fk_ids, existing_recipes,
                                              skip_ingredients, conflict_constraint)
                total_r += rc; total_i += ic; batch = []
        if batch:
            if not dry_run:
                rc, ic = insert_recipe_batch(conn, batch, fk_ids, existing_recipes,
                                              skip_ingredients, conflict_constraint)
                total_r += rc; total_i += ic
            else:
                print(f"   [ADDON] Sample: {batch[0]['name'][:55]}")

    conn.close()
    elapsed = time.time() - start

    print()
    print("=" * 65)
    print("  📊 FINAL STATISTICS")
    print("=" * 65)
    for lbl, val in [
        ("Recipes inserted",     total_r),
        ("Ingredients inserted", total_i),
        ("Avg ingredients/recipe", f"{total_i / max(total_r, 1):.1f}"),
        ("Time",                 f"{elapsed:.1f}s ({elapsed/60:.1f} min)"),
        ("Rate",                 f"{total_r / max(elapsed, 0.01):.0f} recipe/s"),
    ]:
        print(f"  ✦ {lbl:<30} {val!s:>12}")
    print("=" * 65)
    print()
    print("  📋 SQL verify:")
    print("     SELECT c.name, COUNT(*) FROM production_recipes r")
    print("     JOIN production_recipe_categories c ON r.category_id=c.id")
    print("     GROUP BY c.name ORDER BY c.name;")
    print()
    print("     -- Cek ingredient linkage:")
    print("     SELECT r.name, pv.sku, ri.quantity, ri.notes")
    print("     FROM production_recipe_ingredients ri")
    print("     JOIN production_recipes r ON r.id = ri.recipe_id")
    print("     JOIN lumra_config_productvariants pv ON pv.id = ri.variant_id")
    print("     LIMIT 20;")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Kafe Nusantara — Production Recipe Generator v2.0")
    p.add_argument("--type",             choices=["blend", "single", "menu", "addon"],
                   default=None)
    p.add_argument("--skip-ingredients", action="store_true")
    p.add_argument("--dry-run",          action="store_true")
    p.add_argument("--batch-size",       type=int, default=BATCH_SIZE)
    p.add_argument("--db-name",          type=str, default=None)
    p.add_argument("--db-user",          type=str, default=None)
    p.add_argument("--db-password",      type=str, default=None)
    p.add_argument("--db-host",          type=str, default=None)
    p.add_argument("--db-port",          type=str, default=None)
    args = p.parse_args()

    for k, v in [("dbname", args.db_name), ("user", args.db_user),
                 ("password", args.db_password), ("host", args.db_host),
                 ("port", args.db_port)]:
        if v:
            DB_CONFIG[k] = v

    run_pipeline(args.type, args.skip_ingredients, args.dry_run, args.batch_size)
