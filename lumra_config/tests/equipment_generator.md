"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  KAFE NUSANTARA — EQUIPMENT GENERATOR v1.0                                 ║
║  9,999 Alat Kopi → Direct PostgreSQL                                       ║
║                                                                              ║
║  Universe: 35 Merek Batu/Permata × 42 Jenis Alat × Material × Tier        ║
║  Merek menggunakan nama batu alam & permata — selaras dengan world building ║
║  "The Four Expeditions": alat adalah artefak perjalanan sang ekspeditor.   ║
║                                                                              ║
║  Tier Alat (sejajar dengan blend tier):                                    ║
║  · T1 — The Vanguard      : Standard / Entry-level (60%)                  ║
║  · T2 — The Curator's     : Professional / Mid-range (30%)                ║
║  · T3 — The Grand Artifact: Expedition Grade / Collector (10%)            ║
║                                                                              ║
║  Tabel target (sama dengan blend):                                         ║
║  · lumra_config_products                                                   ║
║  · lumra_config_productvariants  (color/size variants)                     ║
║  · lumra_config_productattribute_items  (specs & world building)           ║
║                                                                              ║
║  Usage:                                                                     ║
║    python equipment_generator.py                   # full 9,999            ║
║    python equipment_generator.py --dry-run         # preview 50 items      ║
║    python equipment_generator.py --count 500       # custom count          ║
║    python equipment_generator.py --skip-attrs      # skip attr_items       ║
║    python equipment_generator.py --db-name mydb    # custom DB             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import io
import random
import time
import argparse
import sys
import os
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    import psycopg2
    import psycopg2.extras
    import psycopg2.extensions
except ImportError:
    print("❌ psycopg2 tidak ditemukan. Install: pip install psycopg2-binary")
    sys.exit(1)

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_system.settings")
    from django.conf import settings as django_settings
    DJANGO_SETTINGS_AVAILABLE = True
except Exception:
    django_settings = None
    DJANGO_SETTINGS_AVAILABLE = False

random.seed(20240202)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

if DJANGO_SETTINGS_AVAILABLE:
    default_db = django_settings.DATABASES.get("default", {})
else:
    default_db = {}

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME",     default_db.get("NAME",     "lumra_set_allegra")),
    "user":     os.getenv("DB_USER",     default_db.get("USER",     "postgres")),
    "password": os.getenv("DB_PASSWORD", default_db.get("PASSWORD", "123456")),
    "host":     os.getenv("DB_HOST",     default_db.get("HOST",     "localhost")),
    "port":     os.getenv("DB_PORT",     default_db.get("PORT",     "5432")),
}

TARGET_EQUIPMENT  = 9_999
BATCH_SIZE        = 500
SHOW_PROGRESS_EVERY = 500

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — BRAND UNIVERSE (nama batu alam & permata)
# ═══════════════════════════════════════════════════════════════════════════════

BRANDS = [
    # (brand_key, display_name, stone_origin, stone_lore, tier_affinity)
    # tier_affinity: T1=standard, T2=professional, T3=expedition, None=all
    ("onyx",         "Onyx",         "Turki & India",    "Batu hitam pekat yang menyerap cahaya — seperti kopi pekat yang menyerap malam.",            "T1"),
    ("obsidian",     "Obsidian",     "Indonesia & Meksiko","Kaca vulkanik dari letusan gunung — keras, tajam, dan terbentuk dalam sekejap api.",       "T1"),
    ("quartz",       "Quartz",       "Brasil & Madagaskar","Kristal paling melimpah di bumi — jernih seperti air pertama dari mata air pegunungan.",   "T1"),
    ("jasper",       "Jasper",       "India & Afrika",    "Batu merah membara yang telah menemani manusia sejak zaman batu — tahan dan setia.",        "T1"),
    ("carnelian",    "Carnelian",    "India & Brasil",    "Jingga hangat seperti bara api yang belum padam — energi dan semangat dalam satu batu.",    "T1"),
    ("citrine",      "Citrine",      "Brasil & Spanyol",  "Kuning keemasan seperti secangkir kopi di pagi cerah — menghangatkan dan mencerahkan.",    "T1"),
    ("aventurine",   "Aventurine",   "India & Rusia",     "Hijau bersinar dengan inklusi metalik — keberuntungan yang tersembunyi dalam setiap layer.", "T1"),
    ("howlite",      "Howlite",      "Kanada & Amerika",  "Putih bersih dengan urat abu-abu — ketenangan yang mempersilakan semua rasa masuk.",        "T1"),
    ("fluorite",     "Fluorite",     "Tiongkok & Meksiko","Berwarna-warni dan berkilau — kompleksitas tersembunyi di balik penampilan yang sederhana.", "T1"),
    ("sodalite",     "Sodalite",     "Brasil & Bolivia",  "Biru dalam dengan fleksi putih — kedalaman laut yang membawa ketenangan ekspeditor.",       "T1"),
    ("rhodonite",    "Rhodonite",    "Rusia & Australia", "Merah muda dengan urat hitam — keseimbangan antara kehangatan dan ketegasan.",              "T1"),
    ("peridot",      "Peridot",      "Mesir & Myanmar",   "Hijau zaitun dari perut bumi — satu-satunya permata yang terbentuk di mantel bumi.",        "T2"),
    ("garnet",       "Garnet",       "India & Afrika",    "Merah tua berkilau seperti anggur tua — kompleks, dalam, dan semakin baik seiring waktu.",   "T2"),
    ("topaz",        "Topaz",        "Brasil & Pakistan", "Biru kristal yang jernih seperti langit pegunungan sebelum fajar.",                          "T2"),
    ("tourmaline",   "Tourmaline",   "Brasil & Afganistan","Satu batu, seribu warna — seperti satu blend yang menyimpan ribuan nuansa rasa.",          "T2"),
    ("spinel",       "Spinel",       "Myanmar & Sri Lanka","Sering dikira rubi — karena hanya yang mengerti dapat membedakan keistimewaannya.",        "T2"),
    ("zircon",       "Zircon",       "Kamboja & Australia","Mineral tertua di bumi — mengandung kenangan dari 4 miliar tahun yang lalu.",              "T2"),
    ("malachite",    "Malachite",    "Kongo & Rusia",     "Hijau berlapis seperti sayatan pohon — setiap lapis menyimpan era yang berbeda.",           "T2"),
    ("labradorite",  "Labradorite",  "Kanada & Madagaskar","Abu-abu biasa di luar, lautan warna di dalam — keajaiban bagi yang mau melihat lebih dalam.","T2"),
    ("moonstone",    "Moonstone",    "India & Sri Lanka", "Bercahaya seperti bulan penuh — memancarkan sinar dari dalam, bukan dari luar.",            "T2"),
    ("sunstone",     "Sunstone",     "Norwegia & India",  "Berkilau seperti matahari di permukaan air — energi yang memberi arah pada penjelajah.",    "T2"),
    ("kyanite",      "Kyanite",      "Brasil & Nepal",    "Biru safir yang memanjang seperti jalur ekspedisi — tidak pernah membutuhkan kalibrasi ulang.","T2"),
    ("chrysocolla",  "Chrysocolla",  "Peru & Arizona",    "Biru-hijau seperti lautan tropis — menenangkan dan membuka pikiran untuk perjalanan baru.", "T2"),
    ("chalcedony",   "Chalcedony",   "Brasil & Uruguay",  "Susu biru yang tenang — translucent seperti air danau di ketinggian.",                     "T2"),
    ("amazonite",    "Amazonite",    "Brasil & Colorado",  "Hijau toska legenda — seperti hutan Amazon yang menyimpan lebih banyak dari yang terlihat.", "T2"),
    ("alexandrite",  "Alexandrite",  "Rusia & Sri Lanka", "Berubah warna dari hijau ke merah — satu-satunya permata yang berbeda di bawah cahaya berbeda.","T3"),
    ("opal",         "Opal",         "Australia & Ethiopia","Menyimpan semua warna sekaligus — kaleidoskop waktu dan cahaya dalam satu batu.",         "T3"),
    ("amethyst",     "Amethyst",     "Brasil & Uruguay",  "Ungu yang paling mulia — simbol kebijaksanaan dan ketenangan pikiran penjelajah.",          "T3"),
    ("aquamarine",   "Aquamarine",   "Brasil & Pakistan", "Biru laut dalam yang jernih — dipakai pelaut kuno sebagai jimat keselamatan.",              "T3"),
    ("rhodochrosite","Rhodochrosite","Argentina & Colorado","Merah muda berlapis seperti peta topografi — setiap kontur menyimpan cerita tersendiri.", "T3"),
    ("larimar",      "Larimar",      "Dominika",          "Hanya ada di satu tempat di dunia — eksklusivitas alami yang tidak bisa dipalsukan.",       "T3"),
    ("azurite",      "Azurite",      "Maroko & Namibia",  "Biru terdalam yang pernah ada — seperti langit malam di atas puncak Semeru.",              "T3"),
    ("marcasite",    "Marcasite",    "Prancis & Peru",    "Kilapan metalik seperti bintang — keindahan yang lahir dari tekanan luar biasa.",            "T3"),
    ("pyrite",       "Pyrite",       "Spanyol & Peru",    "'Emas palsu' yang lebih keras dari emas — ketangguhan yang sering disalahpahami.",          "T3"),
    ("selenite",     "Selenite",     "Meksiko & Maroko",  "Transparan sempurna seperti udara — membiarkan segala sesuatu terlihat apa adanya.",       "T3"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TOOL TYPE DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

# Format: (tool_key, display_name, category, method_type, variants_type,
#          brewing_for, temp_range, brew_time, capacity_ml,
#          world_building_role, skill_level, care_note)

TOOLS = [

    # ── MANUAL POUR OVER ──────────────────────────────────────────────────────
    {
        "key": "v60_dripper", "name": "V60 Dripper", "category": "Manual Brew",
        "method": "Pour Over", "power": "Manual", "skill": "Intermediate",
        "brew_time": "2.5–3.5 menit", "temp": "90–93°C", "capacity": "250–500ml",
        "compatible_grind": "Medium-Fine",
        "world_role": "Alat standar ekspeditor — ringan, portabel, dan menghasilkan ekstraksi bersih yang merekam karakter origin dengan jujur.",
        "variants_type": "color_size",
        "size_options": ["01 (1–2 cups)", "02 (1–4 cups)", "03 (1–6 cups)"],
        "colors": ["Matte Black", "Ivory White", "Forest Green", "Copper", "Slate Blue"],
        "materials": ["Ceramic", "Glass", "Polypropylene", "Stainless Steel", "Copper"],
        "care": "Bilas dengan air panas sebelum dan setelah brewing. Simpan filter terpisah.",
        "price_t1": (180_000, 450_000), "price_t2": (450_000, 1_200_000), "price_t3": (1_200_000, 3_500_000),
    },
    {
        "key": "chemex", "name": "Chemex", "category": "Manual Brew",
        "method": "Pour Over", "power": "Manual", "skill": "Intermediate",
        "brew_time": "4–5 menit", "temp": "92–95°C", "capacity": "480–1200ml",
        "compatible_grind": "Medium-Coarse",
        "world_role": "Karya seni yang berfungsi sebagai alat brewing — hadir di meja The Cikini Reading Room dan setiap Shelter yang menghargai estetika.",
        "variants_type": "size_handle",
        "size_options": ["3-Cup 480ml", "6-Cup 900ml", "8-Cup 1200ml"],
        "colors": ["Clear Glass", "Smoked Glass", "Copper Collar", "Wood Collar"],
        "materials": ["Borosilicate Glass", "Borosilicate + Wood", "Borosilicate + Copper"],
        "care": "Cuci dengan sikat khusus Chemex. Jangan gunakan sabun berbau kuat — glass menyerap aroma.",
        "price_t1": (250_000, 650_000), "price_t2": (650_000, 1_800_000), "price_t3": (1_800_000, 5_000_000),
    },
    {
        "key": "kalita_wave", "name": "Kalita Wave", "category": "Manual Brew",
        "method": "Pour Over", "power": "Manual", "skill": "Beginner",
        "brew_time": "3–4 menit", "temp": "90–93°C", "capacity": "200–500ml",
        "compatible_grind": "Medium",
        "world_role": "Flat-bottom dripper yang paling forgiving — pilihan pertama First Light untuk ekspeditor baru yang baru memulai perjalanan.",
        "variants_type": "color_size",
        "size_options": ["155 (1–2 cups)", "185 (2–4 cups)"],
        "colors": ["Matte Black", "Rose Gold", "Gunmetal", "Ivory"],
        "materials": ["Stainless Steel", "Ceramic", "Glass"],
        "care": "Filter Kalita Wave 155/185 tidak bisa ditukar. Selalu gunakan filter asli untuk hasil konsisten.",
        "price_t1": (200_000, 500_000), "price_t2": (500_000, 1_400_000), "price_t3": (1_400_000, 4_000_000),
    },
    {
        "key": "clever_dripper", "name": "Clever Dripper", "category": "Manual Brew",
        "method": "Immersion Pour Over", "power": "Manual", "skill": "Beginner",
        "brew_time": "3–4 menit", "temp": "90–95°C", "capacity": "300–500ml",
        "compatible_grind": "Medium",
        "world_role": "Hybrid antara immersion dan pour over — keseimbangan sempurna untuk ekspeditor yang ingin konsistensi tanpa pengorbanan karakter.",
        "variants_type": "size",
        "size_options": ["Small 300ml", "Large 500ml"],
        "colors": ["Transparent", "Black", "Red", "Blue"],
        "materials": ["BPA-Free Plastic", "Glass"],
        "care": "Bersihkan katup bawah setelah setiap sesi. Rendam dalam air panas 10 menit setiap minggu.",
        "price_t1": (150_000, 380_000), "price_t2": (380_000, 900_000), "price_t3": (900_000, 2_200_000),
    },
    {
        "key": "nel_drip", "name": "Nel Drip", "category": "Manual Brew",
        "method": "Cloth Filter Pour Over", "power": "Manual", "skill": "Advanced",
        "brew_time": "4–6 menit", "temp": "88–92°C", "capacity": "250–500ml",
        "compatible_grind": "Medium-Coarse",
        "world_role": "Metode kuno Jepang yang menghasilkan body paling kaya dan paling tebal — ritual, bukan sekadar rutinitas.",
        "variants_type": "size",
        "size_options": ["1–2 cups", "2–4 cups"],
        "colors": ["Natural Wood", "Ebony", "Bamboo"],
        "materials": ["Flannel + Stainless Steel", "Flannel + Bamboo", "Organic Cotton + Wood"],
        "care": "Simpan filter flannel dalam air dingin di kulkas. Jangan pernah keringkan — flannel yang kering akan rusak.",
        "price_t1": (220_000, 550_000), "price_t2": (550_000, 1_500_000), "price_t3": (1_500_000, 4_500_000),
    },
    {
        "key": "hario_switch", "name": "Immersion Switch", "category": "Manual Brew",
        "method": "Immersion + Pour Over", "power": "Manual", "skill": "Beginner",
        "brew_time": "3–5 menit", "temp": "90–95°C", "capacity": "250–480ml",
        "compatible_grind": "Medium",
        "world_role": "Inovasi V60 dengan katup bawah — dapat digunakan sebagai immersion (seperti French Press) atau pour over. Dua alat dalam satu.",
        "variants_type": "color",
        "size_options": ["250ml", "480ml"],
        "colors": ["Clear", "Smoke Grey", "Black", "Red"],
        "materials": ["Borosilicate Glass", "Borosilicate + Silicone"],
        "care": "Lepas rubber valve setelah brewing untuk menghindari karet menempel. Cuci valve terpisah.",
        "price_t1": (280_000, 700_000), "price_t2": (700_000, 1_800_000), "price_t3": (1_800_000, 5_200_000),
    },

    # ── IMMERSION BREWING ─────────────────────────────────────────────────────
    {
        "key": "french_press", "name": "French Press", "category": "Manual Brew",
        "method": "Full Immersion", "power": "Manual", "skill": "Beginner",
        "brew_time": "4 menit", "temp": "93–95°C", "capacity": "350–1500ml",
        "compatible_grind": "Coarse",
        "world_role": "Alat paling demokratis dalam dunia kopi — hadir di setiap Outpost, dari The Batavia Loghouse hingga The Eastern Terminus di Jayapura.",
        "variants_type": "size_material",
        "size_options": ["350ml (2 cups)", "600ml (4 cups)", "1000ml (8 cups)", "1500ml (12 cups)"],
        "colors": ["Matte Black", "Brushed Silver", "Copper", "Rose Gold", "Forest Green"],
        "materials": ["Borosilicate Glass + Stainless", "Double Wall Stainless", "Copper Plated", "Titanium"],
        "care": "Cuci plunger dan filter screen setelah setiap sesi. Ganti filter screen setiap 6 bulan.",
        "price_t1": (150_000, 400_000), "price_t2": (400_000, 1_200_000), "price_t3": (1_200_000, 4_000_000),
    },
    {
        "key": "aeropress", "name": "AeroPress", "category": "Manual Brew",
        "method": "Pressure Immersion", "power": "Manual", "skill": "Intermediate",
        "brew_time": "1–2 menit", "temp": "80–96°C", "capacity": "60–250ml",
        "compatible_grind": "Fine to Medium",
        "world_role": "Senjata rahasia ekspeditor — ringan, nyaris tidak bisa pecah, dan menghasilkan kopi yang berbeda setiap kali. 1 alat, 1000 resep.",
        "variants_type": "edition",
        "size_options": ["Standard (1 cup)", "XL (2 cups)"],
        "colors": ["Clear", "Black", "White", "Limited Edition"],
        "materials": ["BPA-Free Polypropylene", "Tritan", "Polycarbonate"],
        "care": "Cukup bilas dengan air panas. Sesekali rendam dalam air sabun panas. Tidak perlu sikat.",
        "price_t1": (250_000, 600_000), "price_t2": (600_000, 1_500_000), "price_t3": (1_500_000, 4_000_000),
    },
    {
        "key": "cold_brew_jar", "name": "Cold Brew Jar", "category": "Manual Brew",
        "method": "Cold Extraction", "power": "Manual", "skill": "Beginner",
        "brew_time": "12–24 jam", "temp": "4°C (kulkas)", "capacity": "500–2000ml",
        "compatible_grind": "Coarse",
        "world_role": "Wadah pendingin untuk cold brew 18 jam — menghasilkan Midday Transit menu terbaik. Ditemukan di setiap Outpost untuk batch harian.",
        "variants_type": "size",
        "size_options": ["500ml", "1000ml", "1500ml", "2000ml"],
        "colors": ["Clear Glass", "Amber Glass", "Dark Green Glass", "Matte Black Stainless"],
        "materials": ["Borosilicate Glass", "Stainless Steel", "BPA-Free Tritan"],
        "care": "Cuci dengan baking soda untuk menghilangkan bau. Simpan filter mesh terpisah saat tidak digunakan.",
        "price_t1": (120_000, 300_000), "price_t2": (300_000, 800_000), "price_t3": (800_000, 2_500_000),
    },
    {
        "key": "siphon", "name": "Siphon Brewer", "category": "Manual Brew",
        "method": "Vacuum Pressure", "power": "Manual/Burner", "skill": "Advanced",
        "brew_time": "5–8 menit", "temp": "92–95°C", "capacity": "300–600ml",
        "compatible_grind": "Medium-Fine",
        "world_role": "Alat sains yang menjadi ritual teatrikal — brewing seperti melakukan ekspedisi laboratorium di depan tamu.",
        "variants_type": "size",
        "size_options": ["3-Cup 300ml", "5-Cup 500ml"],
        "colors": ["Clear + Chrome", "Clear + Copper", "Smoked + Black"],
        "materials": ["Borosilicate Glass + Stainless", "Borosilicate + Copper", "Heat-Resistant Glass"],
        "care": "Ganti filter cloth atau glass bead secara berkala. Jangan simpan assembled — glass bisa retak karena perubahan suhu.",
        "price_t1": (400_000, 1_000_000), "price_t2": (1_000_000, 2_800_000), "price_t3": (2_800_000, 8_000_000),
    },

    # ── STOVETOP & TRADITIONAL ────────────────────────────────────────────────
    {
        "key": "moka_pot", "name": "Moka Pot", "category": "Manual Brew",
        "method": "Stovetop Pressure", "power": "Stovetop", "skill": "Intermediate",
        "brew_time": "3–5 menit", "temp": "95°C (steam)", "capacity": "60–300ml",
        "compatible_grind": "Fine",
        "world_role": "Warisan Italia yang menemukan rumah barunya di dapur Nusantara — kuat, sederhana, dan tidak kenal menyerah.",
        "variants_type": "size",
        "size_options": ["1-Cup 60ml", "2-Cup 90ml", "4-Cup 150ml", "6-Cup 300ml", "9-Cup 450ml"],
        "colors": ["Silver Classic", "Matte Black", "Copper", "Red", "Blue"],
        "materials": ["Aluminium", "Stainless Steel", "Copper", "Titanium Coated"],
        "care": "Jangan cuci dengan sabun — patina alami aluminium adalah bagian dari karakternya. Bilas dengan air panas saja.",
        "price_t1": (120_000, 300_000), "price_t2": (300_000, 900_000), "price_t3": (900_000, 3_000_000),
    },
    {
        "key": "vietnamese_phin", "name": "Vietnamese Phin", "category": "Manual Brew",
        "method": "Drip Filter", "power": "Manual", "skill": "Beginner",
        "brew_time": "5–8 menit", "temp": "93–96°C", "capacity": "150–250ml",
        "compatible_grind": "Medium-Coarse",
        "world_role": "Tradisi Asia Tenggara yang paling sederhana — tetes demi tetes, sabar demi sabar. Filosofi First Light yang paling jujur.",
        "variants_type": "size",
        "size_options": ["Single 150ml", "Standard 200ml", "Large 250ml"],
        "colors": ["Stainless Silver", "Copper", "Brass", "Black Coated"],
        "materials": ["Stainless Steel Grade 304", "Food-Grade Brass", "Copper Plated"],
        "care": "Cuci bagian filter dengan sikat kecil. Hindari merendam terlalu lama — bisa mempengaruhi press plate.",
        "price_t1": (50_000, 150_000), "price_t2": (150_000, 450_000), "price_t3": (450_000, 1_500_000),
    },
    {
        "key": "ibrik_cezve", "name": "Ibrik / Cezve", "category": "Manual Brew",
        "method": "Turkish Coffee", "power": "Stovetop", "skill": "Intermediate",
        "brew_time": "3–5 menit", "temp": "80–90°C (pra-mendidih)", "capacity": "50–250ml",
        "compatible_grind": "Extra Fine",
        "world_role": "Metode tertua di dunia — meracik kopi seperti merajut mantra, tidak terburu-buru, tidak boleh ditinggalkan.",
        "variants_type": "size",
        "size_options": ["1-Cup 50ml", "2-Cup 100ml", "4-Cup 150ml", "6-Cup 250ml"],
        "colors": ["Copper Natural", "Copper Embossed", "Brass Engraved", "Silver Plated"],
        "materials": ["Hand-Hammered Copper", "Engraved Brass", "Silver-Plated Copper", "Tinned Copper"],
        "care": "Cuci dengan lemon dan garam untuk membersihkan oksidasi. Jangan gunakan sabun keras yang merusak lapisan timah.",
        "price_t1": (150_000, 400_000), "price_t2": (400_000, 1_200_000), "price_t3": (1_200_000, 5_000_000),
    },
    {
        "key": "percolator", "name": "Stovetop Percolator", "category": "Manual Brew",
        "method": "Percolation", "power": "Stovetop", "skill": "Beginner",
        "brew_time": "7–10 menit", "temp": "95–100°C", "capacity": "600–3000ml",
        "compatible_grind": "Coarse",
        "world_role": "Alat perkemahan legenda — percolator camp-style yang sudah menemani ekspedisi selama satu abad lebih.",
        "variants_type": "size",
        "size_options": ["4-Cup 600ml", "8-Cup 1200ml", "12-Cup 1800ml", "20-Cup 3000ml"],
        "colors": ["Polished Stainless", "Matte Black", "Enamel Blue", "Enamel Red"],
        "materials": ["Stainless Steel Grade 18/8", "Enamel Coated", "Aluminium Camp Grade"],
        "care": "Cuci segera setelah brew — kopi yang mengering di dalam sangat sulit dibersihkan.",
        "price_t1": (180_000, 450_000), "price_t2": (450_000, 1_200_000), "price_t3": (1_200_000, 3_500_000),
    },

    # ── GRINDERS ─────────────────────────────────────────────────────────────
    {
        "key": "hand_grinder_conical", "name": "Hand Grinder Conical", "category": "Grinder",
        "method": "Manual Grinding", "power": "Manual", "skill": "Beginner",
        "brew_time": "1–3 menit grind time", "temp": "N/A", "capacity": "20–40g per grind",
        "compatible_grind": "All (adjustable)",
        "world_role": "Alat wajib ekspeditor sejati — bisa dibawa ke puncak Semeru tanpa listrik. Freshly ground di mana saja, kapan saja.",
        "variants_type": "burr_size",
        "size_options": ["38mm Burr (travel)", "48mm Burr (standard)", "60mm Burr (prosumer)"],
        "colors": ["Matte Black", "Silver Titanium", "Dark Green", "All Black", "Midnight Blue"],
        "materials": ["Steel Burr + Aluminium Body", "Steel Burr + Wood", "Titanium Coated Burr + Carbon Fiber", "Ceramic Burr + Stainless"],
        "care": "Bersihkan burr setiap 200g grinding dengan sikat kecil. Jangan cuci dengan air — burr bisa berkarat.",
        "price_t1": (250_000, 650_000), "price_t2": (650_000, 2_000_000), "price_t3": (2_000_000, 7_000_000),
    },
    {
        "key": "hand_grinder_flat", "name": "Hand Grinder Flat Burr", "category": "Grinder",
        "method": "Manual Grinding", "power": "Manual", "skill": "Intermediate",
        "brew_time": "2–4 menit grind time", "temp": "N/A", "capacity": "20–35g per grind",
        "compatible_grind": "All (adjustable)",
        "world_role": "Flat burr menghasilkan distribusi partikel paling seragam — untuk ekspeditor yang tidak mau kompromi pada konsistensi.",
        "variants_type": "burr_size",
        "size_options": ["38mm Flat Burr", "48mm Flat Burr"],
        "colors": ["All Black", "Silver", "Bronze", "Gunmetal"],
        "materials": ["Coated Steel Burr + Aluminium", "Stainless Burr + Titanium Body", "SSP Burr + Carbon Fiber"],
        "care": "Flat burr lebih sensitif terhadap moisture — simpan di tempat kering. Kalibrasi setiap 1kg kopi.",
        "price_t1": (350_000, 900_000), "price_t2": (900_000, 3_000_000), "price_t3": (3_000_000, 9_000_000),
    },
    {
        "key": "electric_grinder_conical", "name": "Electric Grinder Conical", "category": "Grinder",
        "method": "Electric Grinding", "power": "Electric", "skill": "Beginner",
        "brew_time": "10–30 detik", "temp": "N/A", "capacity": "200–500g hopper",
        "compatible_grind": "All (adjustable)",
        "world_role": "Stamina digital untuk volume tinggi — engine tersembunyi di balik setiap cangkir di The Glass Meridian dan Outpost volume besar.",
        "variants_type": "capacity",
        "size_options": ["200g Hopper (home)", "500g Hopper (prosumer)", "1kg Hopper (commercial)"],
        "colors": ["Matte Black", "White", "Silver", "Red"],
        "materials": ["Coated Steel Burr", "Stainless Steel Burr", "Titanium-Coated Burr"],
        "care": "Bersihkan hopper setiap minggu. Gunakan grinder cleaner tablet setiap bulan.",
        "price_t1": (800_000, 2_000_000), "price_t2": (2_000_000, 6_000_000), "price_t3": (6_000_000, 18_000_000),
    },
    {
        "key": "electric_grinder_flat", "name": "Electric Grinder Flat Burr", "category": "Grinder",
        "method": "Electric Grinding", "power": "Electric", "skill": "Intermediate",
        "brew_time": "5–20 detik", "temp": "N/A", "capacity": "300g–1kg hopper",
        "compatible_grind": "All (adjustable, finest precision)",
        "world_role": "Raja konsistensi di dapur produksi — flat burr elektrik adalah backbone dari setiap menu kopi yang harganya tidak bisa ditawar.",
        "variants_type": "burr_size",
        "size_options": ["64mm Flat Burr (semi-pro)", "80mm Flat Burr (professional)", "98mm Flat Burr (commercial)"],
        "colors": ["Matte Black", "Silver Stainless", "Gunmetal"],
        "materials": ["Steel Burr", "Premium Steel Burr", "Hardened Steel Burr", "Titanium Coated"],
        "care": "Pastikan hopper kosong sebelum membersihkan. Vacuum sisa kopi dari chamber setiap hari.",
        "price_t1": (2_000_000, 5_000_000), "price_t2": (5_000_000, 15_000_000), "price_t3": (15_000_000, 45_000_000),
    },

    # ── ELECTRIC BREWING ──────────────────────────────────────────────────────
    {
        "key": "espresso_machine_semi", "name": "Espresso Machine Semi-Auto", "category": "Espresso Equipment",
        "method": "Pump Espresso", "power": "Electric", "skill": "Intermediate",
        "brew_time": "25–30 detik", "temp": "92–93°C", "capacity": "1–2 shots",
        "compatible_grind": "Fine",
        "world_role": "Pusat gravitasi setiap Outpost — mesin semi-auto yang membutuhkan tangan terlatih untuk menghasilkan espresso yang layak disebut 'dari The Four Expeditions'.",
        "variants_type": "group",
        "size_options": ["1 Group (home)", "2 Group (semi-commercial)"],
        "colors": ["Stainless Silver", "Matte Black", "Racing Red", "Navy Blue"],
        "materials": ["Stainless Steel Boiler", "Dual Boiler Stainless", "Copper Boiler + Stainless"],
        "care": "Backflush setiap hari dengan air, setiap minggu dengan cleaning tablet. Descale setiap 3 bulan.",
        "price_t1": (3_500_000, 8_000_000), "price_t2": (8_000_000, 25_000_000), "price_t3": (25_000_000, 80_000_000),
    },
    {
        "key": "espresso_machine_auto", "name": "Espresso Machine Automatic", "category": "Espresso Equipment",
        "method": "Pump Espresso Auto", "power": "Electric", "skill": "Beginner",
        "brew_time": "30–60 detik", "temp": "92–94°C", "capacity": "1–2 shots automated",
        "compatible_grind": "Fine (auto-ground)",
        "world_role": "Konsistensi tanpa kompromi — untuk Outpost volume tinggi seperti The Glass Meridian SCBD yang melayani ratusan espeditor per hari.",
        "variants_type": "capacity",
        "size_options": ["Home Automatic", "Office Automatic", "Commercial Automatic"],
        "colors": ["Stainless Silver", "Matte Black", "White", "Anthracite"],
        "materials": ["Stainless Steel", "ABS + Stainless", "Full Metal Body"],
        "care": "Ikuti siklus pembersihan otomatis yang disarankan mesin. Ganti filter air setiap 2 bulan.",
        "price_t1": (4_000_000, 10_000_000), "price_t2": (10_000_000, 30_000_000), "price_t3": (30_000_000, 100_000_000),
    },
    {
        "key": "drip_coffee_maker", "name": "Drip Coffee Maker", "category": "Electric Brew",
        "method": "Electric Drip", "power": "Electric", "skill": "Beginner",
        "brew_time": "5–8 menit", "temp": "90–96°C", "capacity": "600–1800ml",
        "compatible_grind": "Medium",
        "world_role": "Mesin batch brew yang menghidupkan First Light di Outpost — memungkinkan satu barista menyeduh 12 cangkir sambil menyiapkan hal lain.",
        "variants_type": "capacity",
        "size_options": ["5-Cup 600ml", "8-Cup 1000ml", "12-Cup 1500ml", "14-Cup 1800ml"],
        "colors": ["Stainless Silver", "Matte Black", "White", "Red"],
        "materials": ["Stainless + ABS", "Full Stainless", "Glass Carafe + Stainless"],
        "care": "Cuci carafe setiap hari. Descale setiap bulan dengan larutan cuka putih + air.",
        "price_t1": (400_000, 1_000_000), "price_t2": (1_000_000, 3_000_000), "price_t3": (3_000_000, 9_000_000),
    },
    {
        "key": "milk_frother_auto", "name": "Automatic Milk Frother", "category": "Espresso Equipment",
        "method": "Milk Frothing", "power": "Electric", "skill": "Beginner",
        "brew_time": "60–90 detik", "temp": "55–65°C", "capacity": "150–600ml",
        "compatible_grind": "N/A",
        "world_role": "Penghasil microfoam sempurna untuk cappuccino dan latte art — barista bisa fokus pada espresso sementara susu diurus sendiri.",
        "variants_type": "capacity",
        "size_options": ["150ml (1 cup)", "300ml (2 cups)", "600ml (4 cups)"],
        "colors": ["Matte Black", "Silver", "White", "Rose Gold"],
        "materials": ["Stainless Inner + ABS Outer", "Full Stainless", "Ceramic Coated"],
        "care": "Cuci setelah setiap gunakan — susu yang mengering sangat sulit dibersihkan.",
        "price_t1": (300_000, 750_000), "price_t2": (750_000, 2_200_000), "price_t3": (2_200_000, 6_500_000),
    },
    {
        "key": "cold_brew_machine", "name": "Cold Brew Machine Electric", "category": "Electric Brew",
        "method": "Electric Cold Extraction", "power": "Electric", "skill": "Beginner",
        "brew_time": "3–6 jam (vs 18 jam manual)", "temp": "4–10°C", "capacity": "500–3000ml",
        "compatible_grind": "Coarse",
        "world_role": "Mempercepat cold brew dari 18 jam menjadi 3-6 jam dengan teknologi pressure assist — backbone dari Cold Brew menu The Open Horizon.",
        "variants_type": "capacity",
        "size_options": ["500ml", "1000ml", "2000ml", "3000ml"],
        "colors": ["Stainless Silver", "Matte Black", "Dark Blue"],
        "materials": ["Stainless Steel", "BPA-Free Tritan + Stainless"],
        "care": "Cuci semua komponen setelah batch. Ganti O-ring seal setiap 6 bulan.",
        "price_t1": (800_000, 2_000_000), "price_t2": (2_000_000, 6_000_000), "price_t3": (6_000_000, 18_000_000),
    },

    # ── KETTLE ───────────────────────────────────────────────────────────────
    {
        "key": "gooseneck_kettle_manual", "name": "Gooseneck Kettle Manual", "category": "Accessories",
        "method": "Water Pouring", "power": "Stovetop", "skill": "Beginner",
        "brew_time": "N/A", "temp": "Variable", "capacity": "600–1200ml",
        "compatible_grind": "N/A",
        "world_role": "Leher angsa yang mengontrol laju tuangan — alat yang mengubah pour over dari sekedar menyeduh menjadi seni menulis kaligrafi dengan air.",
        "variants_type": "capacity",
        "size_options": ["600ml", "800ml", "1000ml", "1200ml"],
        "colors": ["Matte Black", "Polished Copper", "Brushed Gold", "Silver Stainless", "Forest Green"],
        "materials": ["Stainless Steel Grade 304", "Copper Plated Stainless", "Hand-Hammered Copper", "Titanium"],
        "care": "Isi dengan air bersih dan didihkan sekali seminggu untuk mencegah mineral build-up.",
        "price_t1": (200_000, 500_000), "price_t2": (500_000, 1_500_000), "price_t3": (1_500_000, 5_000_000),
    },
    {
        "key": "gooseneck_kettle_electric", "name": "Gooseneck Kettle Electric", "category": "Accessories",
        "method": "Water Heating + Pouring", "power": "Electric", "skill": "Beginner",
        "brew_time": "3–5 menit boil time", "temp": "60–100°C (variable)", "capacity": "600–1500ml",
        "compatible_grind": "N/A",
        "world_role": "Kettle pintar yang menjaga suhu dengan presisi 1°C — karena perbedaan 2°C bisa mengubah segalanya dalam extraction.",
        "variants_type": "capacity",
        "size_options": ["600ml", "800ml", "1000ml", "1200ml", "1500ml"],
        "colors": ["Matte Black", "Silver", "Copper", "Rose Gold", "Dark Blue"],
        "materials": ["Stainless Steel Inner", "Stainless + Copper Exterior", "Full Copper"],
        "care": "Descale setiap 2 bulan. Jangan rendam base elektrik.",
        "price_t1": (350_000, 900_000), "price_t2": (900_000, 2_500_000), "price_t3": (2_500_000, 7_500_000),
    },

    # ── SCALE & MEASUREMENT ───────────────────────────────────────────────────
    {
        "key": "coffee_scale", "name": "Coffee Scale", "category": "Accessories",
        "method": "Measurement", "power": "Battery/USB", "skill": "Beginner",
        "brew_time": "N/A", "temp": "N/A", "capacity": "0.1g – 3000g",
        "compatible_grind": "N/A",
        "world_role": "Kompas presisi untuk ekspeditor — tanpa timbangan, resep hanya tebakan. Dengan timbangan, setiap cangkir bisa diulang sempurna.",
        "variants_type": "precision",
        "size_options": ["Basic 0.1g", "Pro 0.1g + Timer", "Barista 0.01g + Timer + Flow"],
        "colors": ["Matte Black", "White", "Silver", "Black + Gold"],
        "materials": ["ABS + Steel Platform", "Tempered Glass + Steel", "Aluminium Alloy"],
        "care": "Kalibrasi dengan calibration weight setiap bulan. Jangan basahi unit.",
        "price_t1": (150_000, 380_000), "price_t2": (380_000, 1_100_000), "price_t3": (1_100_000, 3_500_000),
    },
    {
        "key": "thermometer", "name": "Coffee Thermometer", "category": "Accessories",
        "method": "Temperature Measurement", "power": "Battery", "skill": "Beginner",
        "brew_time": "N/A", "temp": "0–200°C range", "capacity": "N/A",
        "compatible_grind": "N/A",
        "world_role": "Altimeter suhu untuk brewing — memastikan air masuk di suhu yang tepat, karena 2°C bisa berarti perbedaan antara under-extracted dan perfect.",
        "variants_type": "type",
        "size_options": ["Probe Thermometer", "Clip-On Kettle Thermometer", "Infrared Thermometer", "Digital Combo"],
        "colors": ["Silver Stainless", "Matte Black", "Red Accent"],
        "materials": ["Stainless Steel Probe", "Heat-Resistant ABS", "Food-Grade Stainless"],
        "care": "Kalibrasi dalam air es (harus menunjukkan 0°C) dan air mendidih (100°C) setiap bulan.",
        "price_t1": (80_000, 200_000), "price_t2": (200_000, 600_000), "price_t3": (600_000, 2_000_000),
    },
    {
        "key": "wdt_tool", "name": "WDT Distribution Tool", "category": "Accessories",
        "method": "Espresso Prep", "power": "Manual", "skill": "Intermediate",
        "brew_time": "N/A", "temp": "N/A", "capacity": "N/A",
        "compatible_grind": "Fine (espresso prep)",
        "world_role": "Alat kecil yang mengubah segalanya — needle distribution tool yang menghilangkan channeling dan membuat setiap puck espresso sempurna merata.",
        "variants_type": "needle_count",
        "size_options": ["5-Needle", "8-Needle", "14-Needle", "Custom"],
        "colors": ["Silver", "Matte Black", "Copper", "Gold", "Rose Gold"],
        "materials": ["Stainless Steel Needles + Aluminium", "Titanium Needles + Carbon Fiber", "Copper Needles + Wood"],
        "care": "Bersihkan jarum setelah setiap penggunaan. Simpan dengan cap pelindung.",
        "price_t1": (150_000, 380_000), "price_t2": (380_000, 1_200_000), "price_t3": (1_200_000, 4_500_000),
    },
    {
        "key": "tamper", "name": "Espresso Tamper", "category": "Accessories",
        "method": "Espresso Prep", "power": "Manual", "skill": "Beginner",
        "brew_time": "N/A", "temp": "N/A", "capacity": "Diameter 53–58mm",
        "compatible_grind": "Fine (espresso prep)",
        "world_role": "Alat pertama yang menyentuh kopi sebelum espresso lahir — tekanan yang seragam dan sudut yang benar menentukan segalanya.",
        "variants_type": "diameter",
        "size_options": ["53mm", "54mm", "57mm", "58mm", "58.5mm Custom"],
        "colors": ["Silver Mirror", "Matte Black", "Copper", "Gold", "Rose Gold", "Gunmetal"],
        "materials": ["Aluminium + Stainless Base", "Full Stainless Steel", "Copper Handle + Stainless Base", "Titanium", "Wood Handle + Stainless"],
        "care": "Lap dengan kain kering setelah setiap gunakan. Jangan rendam dalam air.",
        "price_t1": (120_000, 300_000), "price_t2": (300_000, 900_000), "price_t3": (900_000, 3_500_000),
    },
    {
        "key": "server_carafe", "name": "Coffee Server / Carafe", "category": "Accessories",
        "method": "Serving", "power": "Manual", "skill": "Beginner",
        "brew_time": "N/A", "temp": "N/A", "capacity": "300–1200ml",
        "compatible_grind": "N/A",
        "world_role": "Bejana penerima — menampung hasil ekstraksi sebelum disajikan. Di The Cikini Reading Room, server juga menjadi objek visual di atas meja.",
        "variants_type": "capacity",
        "size_options": ["300ml", "480ml", "600ml", "900ml", "1200ml"],
        "colors": ["Clear Glass", "Smoked Glass", "Amber Glass", "Matte Black Stainless"],
        "materials": ["Borosilicate Glass", "Borosilicate + Wood Handle", "Stainless Steel", "Vacuum Insulated Stainless"],
        "care": "Cuci segera setelah digunakan — kopi yang mengering meninggalkan noda yang sulit hilang.",
        "price_t1": (100_000, 280_000), "price_t2": (280_000, 800_000), "price_t3": (800_000, 2_500_000),
    },
    {
        "key": "portafilter", "name": "Portafilter", "category": "Espresso Equipment",
        "method": "Espresso Prep", "power": "Manual", "skill": "Intermediate",
        "brew_time": "N/A", "temp": "N/A", "capacity": "Single 7-10g / Double 14-22g",
        "compatible_grind": "Fine",
        "world_role": "Mahkota espresso machine — portafilter menentukan karakter extraction dan menjadi ekspresi identitas barista.",
        "variants_type": "head_size",
        "size_options": ["53mm Single", "53mm Double", "57mm Single", "57mm Double", "58mm Double", "58mm Bottomless/Naked"],
        "colors": ["Silver Chrome", "Matte Black", "Rose Gold", "Copper", "Gunmetal"],
        "materials": ["Chrome Plated Brass", "Stainless Steel", "Copper Plated", "Titanium Coated"],
        "care": "Rendam basket dalam air panas setiap hari. Semprot group head setelah setiap shot.",
        "price_t1": (200_000, 500_000), "price_t2": (500_000, 1_500_000), "price_t3": (1_500_000, 5_000_000),
    },
    {
        "key": "storage_container", "name": "Coffee Storage Container", "category": "Accessories",
        "method": "Storage", "power": "Manual", "skill": "Beginner",
        "brew_time": "N/A", "temp": "Room temperature (ideal 15-25°C)", "capacity": "100g–2000g",
        "compatible_grind": "N/A",
        "world_role": "Benteng terakhir kesegaran — menyimpan biji kopi dari musuh utamanya: oksigen, cahaya, kelembaban, dan panas.",
        "variants_type": "capacity",
        "size_options": ["100g", "250g", "500g", "1000g", "2000g"],
        "colors": ["Matte Black", "Silver Stainless", "Amber Glass", "Dark Green", "White Ceramic"],
        "materials": ["UV-Protected Glass + Steel Valve", "Stainless Steel Airtight", "Ceramic + CO2 Valve", "Aluminium Vacuum Sealed"],
        "care": "Bersihkan dan keringkan sepenuhnya sebelum mengisi ulang. Ganti CO2 one-way valve setiap tahun.",
        "price_t1": (120_000, 300_000), "price_t2": (300_000, 900_000), "price_t3": (900_000, 3_000_000),
    },
    {
        "key": "travel_dripper", "name": "Travel Dripper / Collapsible", "category": "Manual Brew",
        "method": "Pour Over (Travel)", "power": "Manual", "skill": "Beginner",
        "brew_time": "2.5–4 menit", "temp": "90–93°C", "capacity": "150–300ml",
        "compatible_grind": "Medium-Fine",
        "world_role": "Alat ekspedisi sejati — collapsible, ringan di bawah 100g, masuk di saku jaket gunung. First Light di puncak Semeru, bukan angan-angan.",
        "variants_type": "type",
        "size_options": ["Collapsible Silicone", "Ultralight Titanium", "Compact Steel"],
        "colors": ["Black Silicone", "Red Silicone", "Titanium Natural", "Forest Green", "Orange"],
        "materials": ["Food-Grade Silicone", "Titanium Grade 2", "Stainless Steel Micro"],
        "care": "Bilas dan keringkan sebelum disimpan. Lipat hanya saat sudah benar-benar kering.",
        "price_t1": (100_000, 280_000), "price_t2": (280_000, 800_000), "price_t3": (800_000, 2_500_000),
    },
    {
        "key": "dosing_cup", "name": "Dosing Cup / Grounds Catcher", "category": "Accessories",
        "method": "Espresso Prep", "power": "Manual", "skill": "Beginner",
        "brew_time": "N/A", "temp": "N/A", "capacity": "50–150ml",
        "compatible_grind": "Fine (espresso prep)",
        "world_role": "Perantara antara grinder dan portafilter — mengurangi messy workflow dan memungkinkan weighing sebelum dosing.",
        "variants_type": "diameter",
        "size_options": ["53mm", "54mm", "57mm", "58mm"],
        "colors": ["Silver", "Matte Black", "Copper", "Gold"],
        "materials": ["Aluminium", "Stainless Steel", "Copper Plated Aluminium", "Titanium"],
        "care": "Bersihkan setiap hari — sisa kopi yang mengering mempengaruhi hasil timbangan.",
        "price_t1": (80_000, 200_000), "price_t2": (200_000, 600_000), "price_t3": (600_000, 2_000_000),
    },
    {
        "key": "tds_meter", "name": "TDS / Refractometer", "category": "Accessories",
        "method": "Coffee Analysis", "power": "Battery", "skill": "Advanced",
        "brew_time": "N/A", "temp": "N/A", "capacity": "N/A",
        "compatible_grind": "N/A",
        "world_role": "Alat sains untuk ekspeditor yang serius — mengukur Total Dissolved Solids untuk memverifikasi extraction yield dan mendokumentasikan recipe.",
        "variants_type": "type",
        "size_options": ["Basic TDS Pen", "Coffee Refractometer", "Pro Combo TDS + Refractometer"],
        "colors": ["Silver", "Black", "White"],
        "materials": ["ABS + Stainless Electrode", "Optical Glass + ABS", "Aluminium Pro Body"],
        "care": "Kalibrasi dengan distilled water sebelum setiap sesi pengukuran.",
        "price_t1": (150_000, 400_000), "price_t2": (400_000, 1_200_000), "price_t3": (1_200_000, 4_000_000),
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PRICING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

TIER_META = {
    "T1": {"name": "Tier 1 — The Vanguard",           "label": "Standard",           "target_pct": 0.60},
    "T2": {"name": "Tier 2 — The Curator's Reserve",   "label": "Professional",       "target_pct": 0.30},
    "T3": {"name": "Tier 3 — The Grand Artifact",      "label": "Expedition Grade",   "target_pct": 0.10},
}

BRAND_TIER_AFFINITY = {
    b[0]: b[4] for b in BRANDS
}

MATERIAL_PREMIUM = {
    "Aluminium": 1.0, "BPA-Free Plastic": 1.0, "BPA-Free Polypropylene": 1.0,
    "BPA-Free Tritan": 1.05, "Borosilicate Glass": 1.1, "Stainless Steel": 1.1,
    "Stainless Steel Grade 304": 1.15, "Ceramic": 1.2, "Glass": 1.1,
    "Copper": 1.5, "Copper Plated Stainless": 1.4, "Hand-Hammered Copper": 1.8,
    "Titanium": 2.2, "Carbon Fiber": 2.0, "Wood": 1.3, "Bamboo": 1.25,
}

def compute_equipment_price(tool, tier_code, brand_key, material):
    price_range = tool[f"price_{tier_code.lower()}"]
    lo, hi = price_range
    # Random within range, biased toward middle
    base = int(lo + (hi - lo) * (0.3 + random.random() * 0.5))
    # Material premium
    mat_mult = MATERIAL_PREMIUM.get(material, 1.1)
    price = int(base * mat_mult)
    # Round to nearest 5000
    price = max(round(price / 5000) * 5000, lo)
    price = min(price, hi * 1.2)  # cap at 120% of hi
    return int(price)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — NAME & SKU GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_ABBREV = {
    "v60_dripper":             "V60",  "chemex":               "CHX",
    "kalita_wave":             "KLT",  "clever_dripper":       "CLV",
    "nel_drip":                "NEL",  "hario_switch":         "SWT",
    "french_press":            "FP",   "aeropress":            "ARP",
    "cold_brew_jar":           "CBJ",  "siphon":               "SIP",
    "moka_pot":                "MKP",  "vietnamese_phin":      "PHN",
    "ibrik_cezve":             "IBR",  "percolator":           "PRC",
    "hand_grinder_conical":    "HGC",  "hand_grinder_flat":    "HGF",
    "electric_grinder_conical":"EGC",  "electric_grinder_flat":"EGF",
    "espresso_machine_semi":   "EMS",  "espresso_machine_auto":"EMA",
    "drip_coffee_maker":       "DCM",  "milk_frother_auto":    "MFA",
    "cold_brew_machine":       "CBM",
    "gooseneck_kettle_manual": "GKM",  "gooseneck_kettle_electric":"GKE",
    "coffee_scale":            "SCL",  "thermometer":          "THM",
    "wdt_tool":                "WDT",  "tamper":               "TMP",
    "server_carafe":           "SRV",  "portafilter":          "PTF",
    "storage_container":       "STG",  "travel_dripper":       "TVL",
    "dosing_cup":              "DSC",  "tds_meter":            "TDS",
}

BRAND_ABBREV = {b[0]: b[1][:3].upper() for b in BRANDS}

_sku_counters = {"T1": 0, "T2": 0, "T3": 0}

def make_equipment_sku(brand_key, tool_key, tier_code, variant_suffix=""):
    _sku_counters[tier_code] += 1
    brand_ab = BRAND_ABBREV.get(brand_key, brand_key[:3].upper())
    tool_ab  = TOOL_ABBREV.get(tool_key, tool_key[:3].upper())
    seq      = _sku_counters[tier_code]
    base_sku = f"EQ-{brand_ab}-{tool_ab}-{tier_code}-{seq:04d}"
    if variant_suffix:
        return f"{base_sku}-{variant_suffix[:8]}"
    return base_sku

def make_equipment_name(brand_display, tool_name, material, variant_label=""):
    name = f"{brand_display} {tool_name}"
    if material and material not in ("N/A", ""):
        name += f" — {material}"
    if variant_label:
        name += f" [{variant_label}]"
    return name[:254]  # DB varchar limit

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — DESCRIPTION GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def make_equipment_description(brand, tool, tier_code, material, variant_label):
    b_display = brand[1]
    b_origin  = brand[2]
    b_lore    = brand[3]
    t_name    = tool["name"]
    t_role    = tool["world_role"]
    t_method  = tool["method"]
    t_skill   = tool["skill"]
    tier_m    = TIER_META[tier_code]

    if tier_code == "T3":
        desc = (
            f"{b_display} — batu {b_origin} yang {b_lore} "
            f"Dalam lini Expedition Grade ini, {t_name} dihadirkan untuk ekspeditor "
            f"yang tidak mengenal kompromi. {t_role} "
            f"Material: {material}. Metode: {t_method}. "
            f"Hanya tersedia dalam jumlah sangat terbatas — setiap unit difinishing manual."
        )
    elif tier_code == "T2":
        desc = (
            f"{b_display} Professional Series — nama yang terinspirasi dari batu {b_origin}. "
            f"{b_lore} "
            f"{t_role} "
            f"Dirancang untuk barista yang serius dengan material {material} "
            f"dan presisi yang tidak ditemukan di lini standard. Skill level: {t_skill}."
        )
    else:
        desc = (
            f"{b_display} — terinspirasi dari batu {b_origin.split('&')[0].strip()}. "
            f"{t_role} "
            f"Material {material}. Metode brewing: {t_method}. "
            f"Pilihan solid untuk memulai ekspedisi rasa."
        )

    return desc[:490]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — ATTRIBUTE BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def make_equipment_attrs(brand, tool, tier_code, material, variant_label, price):
    b_key     = brand[0]
    b_display = brand[1]
    b_origin  = brand[2]
    b_lore    = brand[3]
    t_key     = tool["key"]
    t_name    = tool["name"]
    tier_m    = TIER_META[tier_code]

    attrs = {
        # Brand & world building
        "brand_name":         b_display,
        "brand_stone":        b_display,
        "brand_stone_origin": b_origin,
        "brand_lore":         b_lore[:250],
        "equipment_tier":     tier_m["name"],
        "equipment_tier_code":tier_code,
        "tier_label":         tier_m["label"],
        # Tool specs
        "tool_type":          t_name,
        "tool_category":      tool["category"],
        "method":             tool["method"],
        "power_source":       tool["power"],
        "skill_level":        tool["skill"],
        "brew_time":          tool["brew_time"],
        "brew_temp":          tool["temp"],
        "capacity":           tool["capacity"],
        "compatible_grind":   tool["compatible_grind"],
        "material":           material,
        "variant":            variant_label,
        # Care & maintenance
        "care_instruction":   tool["care"][:250],
        # World building connection
        "world_role":         tool["world_role"][:250],
        "expedition_use":     _expedition_use(tool["key"], tier_code),
        "outpost_affinity":   _outpost_affinity(tool["key"]),
        "season_pairing":     _season_pairing(tool["key"], brand[0]),
        "paired_blend_tier":  tier_code,
    }
    return attrs

def _expedition_use(tool_key, tier_code):
    uses = {
        "v60_dripper":             "First Light · Morning Ration ritual harian di semua Outpost",
        "chemex":                  "Twilight Bivouac · Signature pour over untuk tamu Curator's Reserve",
        "kalita_wave":             "First Light · Training tool untuk barista baru The Vanguard tier",
        "clever_dripper":          "Midday Transit · Quick brew yang tidak mengorbankan kualitas",
        "nel_drip":                "Twilight Bivouac · Ritual evening brew di Outpost heritage",
        "hario_switch":            "Semua sesi · Versatile hybrid untuk volume rendah",
        "french_press":            "Semua Outpost · Standard equipment dari Outpost 01 hingga 35",
        "aeropress":               "Ekspedisi lapangan · Alat wajib barista mobile The Four Expeditions",
        "cold_brew_jar":           "Midday Transit · Batch brewing untuk Cold Brew menu siang",
        "siphon":                  "Twilight Bivouac · Teatrikal showcase di Outpost premium",
        "moka_pot":                "First Light · Quick strong brew sebelum perjalanan dimulai",
        "vietnamese_phin":         "First Light · Tradisi Asia Tenggara yang menemukan rumah barunya",
        "ibrik_cezve":             "Twilight Bivouac · Ritual kuno yang tidak berubah selama 500 tahun",
        "percolator":              "Ekspedisi alam · Camp brewing untuk event outdoor Outpost",
        "hand_grinder_conical":    "Ekspedisi lapangan · Grinding di mana pun tanpa listrik",
        "hand_grinder_flat":       "Home brewing · Grind konsisten untuk espresso dan pour over",
        "electric_grinder_conical":"Operasional Outpost · Volume grinder untuk rush hour",
        "electric_grinder_flat":   "Roastery & Outpost premium · Presisi tertinggi untuk T3 blend",
        "espresso_machine_semi":   "Operasional Outpost · Engine utama penghasil pendapatan",
        "espresso_machine_auto":   "Volume tinggi · Konsistensi untuk Outpost kategori The Glass Meridian",
        "drip_coffee_maker":       "Batch brewing · First Light production untuk volume besar",
        "milk_frother_auto":       "Signature drinks · Penghasil microfoam cappuccino dan latte art",
        "cold_brew_machine":       "Produksi cold brew · Mempercepat batch untuk menu Midday Transit",
        "gooseneck_kettle_manual": "Pour over · Kontrol aliran air untuk V60 dan Chemex",
        "gooseneck_kettle_electric":"Precision brewing · Smart temperature untuk specialty brew",
        "coffee_scale":            "Semua brewing · Kompas presisi yang tidak bisa ditinggalkan",
        "thermometer":             "Quality control · Verifikasi suhu untuk setiap brewing session",
        "wdt_tool":                "Espresso prep · Anti-channeling tool untuk shot sempurna",
        "tamper":                  "Espresso prep · Alat pertama yang menyentuh kopi sebelum espresso lahir",
        "server_carafe":           "Serving · Bejana penerima pour over di meja tamu",
        "portafilter":             "Espresso · Mahkota espresso machine yang menentukan karakter extraction",
        "storage_container":       "Preservasi · Benteng terakhir kesegaran biji kopi",
        "travel_dripper":          "Ekspedisi field · Pour over di atas gunung, di tepi pantai, di mana saja",
        "dosing_cup":              "Espresso prep · Mengurangi messy workflow dan memastikan dosis akurat",
        "tds_meter":               "Quality control · Dokumentasi recipe dan verifikasi extraction",
    }
    return uses.get(tool_key, "Semua sesi brewing")

def _outpost_affinity(tool_key):
    affinities = {
        "espresso_machine_semi":   "Outpost 05: The Glass Meridian · Outpost 17: The Surabaya Iron Wharf",
        "espresso_machine_auto":   "Outpost 05: The Glass Meridian · Outpost 08: The Kelapa Gading Anchorage",
        "siphon":                  "Outpost 07: The Cikini Reading Room · Outpost 02: The Priangan Counting House",
        "chemex":                  "Outpost 07: The Cikini Reading Room · Outpost 15: The Solo Kepatihan Shelter",
        "ibrik_cezve":             "Outpost 23: The Aceh Gateway · Outpost 32: The Makassar Fortpost",
        "nel_drip":                "Outpost 02: The Priangan Counting House · Outpost 11: The Bogor Botanical Gate",
        "aeropress":               "Semua Outpost · Khusus field expedition dari Outpost 25 Gayo ke Outpost 35 Jayapura",
        "percolator":              "Outpost 35: The Eastern Terminus · Event outdoor The Archipelagic Outposts",
        "vietnamese_phin":         "Outpost 23: The Aceh Gateway · Outpost 24: The Medan Trade Post",
        "electric_grinder_flat":   "Outpost 22: The Final Meridian (Roastery) · Outpost 05: The Glass Meridian",
        "travel_dripper":          "Outpost 25: The Gayo Highlands · Outpost 30: The Kintamani Crater Post",
        "cold_brew_jar":           "Outpost 06: The Kemang Waystation · Outpost 31: The Denpasar Island Hub",
    }
    return affinities.get(tool_key, "Semua Outpost The Archipelagic Outposts")

def _season_pairing(tool_key, brand_key):
    brand_tier = BRAND_TIER_AFFINITY.get(brand_key, "T1")
    tool_season = {
        "v60_dripper": "Spring", "chemex": "Spring", "kalita_wave": "Spring",
        "nel_drip": "Autumn", "hario_switch": "Summer",
        "french_press": "Winter", "aeropress": "Summer",
        "cold_brew_jar": "Summer", "cold_brew_machine": "Summer",
        "siphon": "Winter", "moka_pot": "Winter",
        "vietnamese_phin": "Autumn", "ibrik_cezve": "Winter",
        "percolator": "Autumn", "hand_grinder_conical": "Spring",
        "hand_grinder_flat": "Autumn", "electric_grinder_conical": "Autumn",
        "electric_grinder_flat": "Winter",
        "espresso_machine_semi": "Winter", "espresso_machine_auto": "Winter",
        "drip_coffee_maker": "Autumn",
        "gooseneck_kettle_manual": "Spring", "gooseneck_kettle_electric": "Spring",
    }
    season = tool_season.get(tool_key, random.choice(["Winter","Summer","Autumn","Spring"]))
    return season

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — DATABASE LAYER (mirror dari grand_million_generator.py)
# ═══════════════════════════════════════════════════════════════════════════════

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(autocommit=False)
    return conn

def normalize_attr_value(value, max_length=255):
    text = str(value)
    if len(text) <= max_length:
        return text, False
    return text[:max_length], True

def fetch_existing_products_by_barcodes(conn, barcodes):
    if not barcodes:
        return {}
    cur = conn.cursor()
    cur.execute("SELECT id, barcode FROM lumra_config_products WHERE barcode = ANY(%s)", (barcodes,))
    rows = cur.fetchall()
    cur.close()
    return {barcode: pid for pid, barcode in rows}

def fetch_existing_variants_by_skus(conn, skus):
    if not skus:
        return {}
    cur = conn.cursor()
    cur.execute("SELECT id, sku FROM lumra_config_productvariants WHERE sku = ANY(%s)", (skus,))
    rows = cur.fetchall()
    cur.close()
    return {sku: vid for vid, sku in rows}

def fetch_existing_attr_keys(conn, variant_ids):
    if not variant_ids:
        return set()
    cur = conn.cursor()
    cur.execute(
        "SELECT variant_id, attr_name, attr_value FROM lumra_config_productattribute_items WHERE variant_id = ANY(%s)",
        (variant_ids,)
    )
    rows = cur.fetchall()
    cur.close()
    return set(rows)

def fetch_fk_ids(conn):
    cur = conn.cursor()
    ids = {}

    cur.execute("SELECT name, id FROM _categories WHERE name IN ('Coffee Equipment','Merchandise','Manual Brew','Espresso Equipment','Grinder','Accessories','Electric Brew')")
    for name, id_ in cur.fetchall():
        ids[f"cat_{name.lower().replace(' ','_')}"] = id_

    # Fallback to any existing category
    if not ids:
        cur.execute("SELECT id FROM _categories LIMIT 1")
        row = cur.fetchone()
        if row:
            ids["cat_fallback"] = row[0]

    cur.execute("SELECT id FROM _taxes WHERE name = 'PPN 11%' LIMIT 1")
    row = cur.fetchone()
    ids["tax_ppn11"] = row[0] if row else None

    cur.execute("SELECT id FROM _units WHERE name = 'Pcs' LIMIT 1")
    row = cur.fetchone()
    ids["unit_pcs"] = row[0] if row else None

    if not ids.get("unit_pcs"):
        cur.execute("SELECT id FROM _units LIMIT 1")
        row = cur.fetchone()
        ids["unit_pcs"] = row[0] if row else None

    cur.close()
    return ids

def get_category_for_tool(tool, fk_ids):
    cat_map = {
        "Manual Brew":          "cat_manual_brew",
        "Espresso Equipment":   "cat_espresso_equipment",
        "Grinder":              "cat_grinder",
        "Accessories":          "cat_accessories",
        "Electric Brew":        "cat_electric_brew",
    }
    key = cat_map.get(tool["category"], "cat_merchandise")
    return fk_ids.get(key) or fk_ids.get("cat_fallback") or list(fk_ids.values())[0]

def ensure_equipment_categories(conn):
    """Pastikan kategori alat kopi ada di database."""
    categories = [
        ("Coffee Equipment",  "coffee-equipment",  "EQ",  "Semua alat dan perlengkapan kopi"),
        ("Manual Brew",       "manual-brew-eq",    "MBQ", "Alat brewing manual — V60, Chemex, AeroPress, dll."),
        ("Espresso Equipment","espresso-equipment","ESP", "Mesin espresso, portafilter, tamper, dll."),
        ("Grinder",           "grinder",           "GRD", "Manual dan electric grinder"),
        ("Accessories",       "accessories",       "ACC", "Aksesoris brewing — kettle, scale, server, dll."),
        ("Electric Brew",     "electric-brew",     "EBW", "Alat brewing elektrik — drip maker, cold brew machine"),
    ]
    cur = conn.cursor()
    for name, slug, code, desc in categories:
        cur.execute("""
            INSERT INTO _categories (name, description, slug, code, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW(), NOW())
            ON CONFLICT (name) DO NOTHING
        """, (name, desc, slug, code))
    conn.commit()
    cur.close()

def get_next_sequences(conn, table_col_map):
    cur = conn.cursor()
    seq = {}
    for table, col in table_col_map.items():
        try:
            cur.execute(f"SELECT COALESCE(MAX({col}), 0) FROM {table}")
            seq[table] = cur.fetchone()[0]
        except Exception:
            seq[table] = 0
    cur.close()
    return seq

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — PRODUCT GENERATOR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_equipment_batch(target_count):
    """
    Generate target_count equipment products dengan distribusi tier yang benar.
    Returns list of product dicts.
    """
    items = []
    brand_list = list(BRANDS)

    tier_targets = {
        "T1": int(target_count * 0.60),
        "T2": int(target_count * 0.30),
        "T3": target_count - int(target_count * 0.60) - int(target_count * 0.30),
    }

    # Pre-build all combinations (brand × tool × material × size)
    combinations = []
    for brand in brand_list:
        brand_aff = brand[4]  # T1, T2, or T3
        for tool in TOOLS:
            for material in tool["materials"]:
                for size_opt in tool["size_options"]:
                    combinations.append({
                        "brand": brand,
                        "tool":  tool,
                        "material": material,
                        "variant_label": size_opt,
                        "brand_affinity": brand_aff,
                    })

    # Separate by tier affinity
    t1_pool = [c for c in combinations if c["brand_affinity"] in ("T1", None)]
    t2_pool = [c for c in combinations if c["brand_affinity"] in ("T2", None)]
    t3_pool = [c for c in combinations if c["brand_affinity"] in ("T3", None)]

    random.shuffle(t1_pool)
    random.shuffle(t2_pool)
    random.shuffle(t3_pool)

    idx = 0
    for tier_code, count in tier_targets.items():
        pool = {"T1": t1_pool, "T2": t2_pool, "T3": t3_pool}[tier_code]

        # If pool smaller than target, cycle through with index suffix
        for i in range(count):
            combo = pool[i % len(pool)]
            brand    = combo["brand"]
            tool     = combo["tool"]
            material = combo["material"]
            var_label = combo["variant_label"]

            # Cycle suffix jika pool habis
            cycle = i // len(pool)
            cycle_suffix = f" Mk.{cycle+1}" if cycle > 0 else ""

            sku_variant = var_label.replace(" ", "")[:8].upper()
            sku_base    = make_equipment_sku(brand[0], tool["key"], tier_code)

            product_name = make_equipment_name(brand[1], tool["name"], material, var_label)
            if cycle > 0:
                product_name = f"{product_name}{cycle_suffix}"

            barcode = f"{sku_base}"
            description = make_equipment_description(brand, tool, tier_code, material, var_label)
            attrs = make_equipment_attrs(brand, tool, tier_code, material, var_label, 0)

            price = compute_equipment_price(tool, tier_code, brand[0], material)
            price_buy = int(price * 0.60)

            # Build size variants (color variants of this product)
            color_variants = []
            colors = tool.get("colors", ["Default"])
            for color in colors:
                c_sku = f"{sku_base}-{color[:4].upper().replace(' ','')}"
                c_price = price + random.randint(-5000, 15000)
                c_price = max(round(c_price / 5000) * 5000, 50_000)
                color_variants.append({
                    "sku":        c_sku,
                    "size_weight": f"{color} — {var_label}",
                    "price_buy":  int(c_price * 0.60),
                    "price_sell": c_price,
                })

            items.append({
                "barcode":        barcode,
                "name":           product_name[:254],
                "description":    description,
                "tier_code":      tier_code,
                "tool_category":  tool["category"],
                "price_sell":     price,
                "price_buy":      price_buy,
                "variants":       color_variants,
                "attrs":          attrs,
                "has_expiry":     False,
                "track_batch":    tier_code == "T3",
                "min_stock":      1 if tier_code == "T3" else (3 if tier_code == "T2" else 5),
                "max_stock":      10 if tier_code == "T3" else (50 if tier_code == "T2" else 200),
            })
            idx += 1

    return items

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_pipeline(total_target, batch_size, skip_attrs, dry_run):
    print("═" * 65)
    print("  KAFE NUSANTARA — EQUIPMENT GENERATOR v1.0")
    print(f"  Target: {total_target:,} alat kopi → PostgreSQL")
    print(f"  Brand universe: {len(BRANDS)} merek batu/permata")
    print(f"  Tool types    : {len(TOOLS)} jenis alat")
    print("═" * 65)

    if dry_run:
        total_target = min(total_target, 50)
        print(f"  [DRY RUN] Preview {total_target} items saja")

    print(f"\n📡 Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}...")
    try:
        conn = get_connection()
        print("  ✅ Connected")
    except Exception as e:
        print(f"  ❌ {e}"); sys.exit(1)

    # Ensure categories exist
    ensure_equipment_categories(conn)

    fk_ids = fetch_fk_ids(conn)
    print(f"  FK IDs: { {k:v for k,v in fk_ids.items() if v} }")

    seqs = get_next_sequences(conn, {
        "lumra_config_products": "id",
        "lumra_config_productvariants": "id",
    })
    print(f"  Current max product ID : {seqs['lumra_config_products']:,}")

    # Tier distribution
    t1 = int(total_target * 0.60)
    t2 = int(total_target * 0.30)
    t3 = total_target - t1 - t2
    print(f"\n📐 Distribution Plan:")
    print(f"   T1 Vanguard Standard    : {t1:>6,}")
    print(f"   T2 Curator Professional : {t2:>6,}")
    print(f"   T3 Grand Artifact Exp.  : {t3:>6,}")
    print(f"   TOTAL                   : {total_target:>6,}")

    # Stats
    total_products  = 0
    total_variants  = 0
    total_attrs     = 0
    start_time      = time.time()
    used_barcodes   = set()
    used_skus       = set()

    # Generate all items
    print(f"\n🔧 Generating {total_target:,} equipment items...")
    all_items = generate_equipment_batch(total_target)
    print(f"   Generated {len(all_items):,} items in memory")

    if dry_run:
        # Print sample
        print(f"\n📋 SAMPLE (5 items):")
        for item in all_items[:5]:
            print(f"   [{item['tier_code']}] {item['name'][:60]}")
            print(f"         SKU: {item['barcode']} | Harga: Rp {item['price_sell']:,}")
            print(f"         Variants: {len(item['variants'])} | Attrs: {len(item['attrs'])}")
        return

    # Process in batches
    print(f"\n💾 Inserting to PostgreSQL in batches of {batch_size}...")
    now_str = datetime.now(timezone.utc)

    for batch_start in range(0, len(all_items), batch_size):
        batch = all_items[batch_start:batch_start + batch_size]

        # ── Products ──────────────────────────────────────────────────────────
        barcodes = [item["barcode"] for item in batch]
        existing_barcodes = fetch_existing_products_by_barcodes(conn, barcodes)
        new_items = [item for item in batch if item["barcode"] not in existing_barcodes]

        if new_items:
            cur = conn.cursor()
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO lumra_config_products
                    (name, description, is_active, has_expiry, track_batch,
                     min_stock, max_stock, created_at, updated_at,
                     category_id, tax_id, unit_id, vendor_id, barcode)
                VALUES %s
                ON CONFLICT (barcode) DO NOTHING
                RETURNING id, barcode
                """,
                [
                    (
                        item["name"][:254],
                        item["description"][:490],
                        True,
                        item["has_expiry"],
                        item["track_batch"],
                        item["min_stock"],
                        item["max_stock"],
                        now_str,
                        now_str,
                        get_category_for_tool(
                            next(t for t in TOOLS if t["name"] in item["name"] or
                                 any(t["name"] in item["name"] for t in TOOLS)), fk_ids
                        ) if fk_ids else None,
                        fk_ids.get("tax_ppn11"),
                        fk_ids.get("unit_pcs"),
                        None,
                        item["barcode"],
                    )
                    for item in new_items
                ],
                page_size=200,
            )
            inserted = cur.fetchall()
            conn.commit()
            cur.close()

            barcode_to_pid = {row[1]: row[0] for row in inserted}
            barcode_to_pid.update(existing_barcodes)
            total_products += len(inserted)
        else:
            barcode_to_pid = existing_barcodes

        # ── Variants ──────────────────────────────────────────────────────────
        all_variant_rows = []
        for item in batch:
            pid = barcode_to_pid.get(item["barcode"])
            if not pid:
                continue
            for v in item["variants"]:
                if v["sku"] not in used_skus:
                    used_skus.add(v["sku"])
                    all_variant_rows.append((v["sku"], pid, v["size_weight"], v["price_buy"], v["price_sell"]))

        if all_variant_rows:
            all_skus = [r[0] for r in all_variant_rows]
            existing_skus_map = fetch_existing_variants_by_skus(conn, all_skus)
            new_variant_rows = [r for r in all_variant_rows if r[0] not in existing_skus_map]

            if new_variant_rows:
                cur = conn.cursor()
                psycopg2.extras.execute_values(
                    cur,
                    """
                    INSERT INTO lumra_config_productvariants
                        (sku, product_id, size_weight, price_buy, price_sell, updated_at)
                    VALUES %s
                    ON CONFLICT (sku) DO NOTHING
                    RETURNING id, sku
                    """,
                    [(sku, pid, sw, pb, ps, now_str)
                     for sku, pid, sw, pb, ps in new_variant_rows],
                    page_size=500,
                )
                var_inserted = cur.fetchall()
                conn.commit()
                cur.close()

                sku_to_vid = {row[1]: row[0] for row in var_inserted}
                sku_to_vid.update(existing_skus_map)
                total_variants += len(var_inserted)
            else:
                sku_to_vid = existing_skus_map
        else:
            sku_to_vid = {}

        # ── Attribute Items ───────────────────────────────────────────────────
        if not skip_attrs:
            attr_rows = []
            batch_attr_keys = set()

            # Get existing attrs for variants in this batch
            all_vids = list(sku_to_vid.values())
            existing_attr_keys = fetch_existing_attr_keys(conn, all_vids) if all_vids else set()

            for item in batch:
                # Get primary variant (first color)
                if not item["variants"]:
                    continue
                first_sku = item["variants"][0]["sku"]
                vid = sku_to_vid.get(first_sku)
                if not vid:
                    continue

                for attr_name, attr_val in item["attrs"].items():
                    normalized_val, _ = normalize_attr_value(attr_val)
                    attr_key = (vid, attr_name, normalized_val)
                    if attr_key in existing_attr_keys or attr_key in batch_attr_keys:
                        continue
                    batch_attr_keys.add(attr_key)
                    attr_rows.append((vid, attr_name, normalized_val, now_str))

            if attr_rows:
                cur = conn.cursor()
                psycopg2.extras.execute_values(
                    cur,
                    """
                    INSERT INTO lumra_config_productattribute_items
                        (variant_id, attr_name, attr_value, updated_at)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                    """,
                    attr_rows,
                    page_size=1000,
                )
                total_attrs += len(attr_rows)
                conn.commit()
                cur.close()

        # ── Progress ──────────────────────────────────────────────────────────
        done = batch_start + len(batch)
        if done % SHOW_PROGRESS_EVERY == 0 or done >= len(all_items):
            elapsed = time.time() - start_time
            rate = total_products / max(elapsed, 0.01)
            print(
                f"   [{done:>6,}/{len(all_items):,}] "
                f"Products: {total_products:,} | Variants: {total_variants:,} | "
                f"Attrs: {total_attrs:,} | {rate:.0f} prod/s"
            )

    conn.close()
    elapsed = time.time() - start_time

    print()
    print("═" * 65)
    print("  📊 FINAL STATISTICS")
    print("═" * 65)
    for label, val in [
        ("Products inserted",       total_products),
        ("Variants inserted",       total_variants),
        ("Attribute items inserted",total_attrs),
        ("Total rows",              total_products + total_variants + total_attrs),
        ("Time elapsed",            f"{elapsed:.1f}s ({elapsed/60:.1f} min)"),
        ("Throughput",              f"{total_products/max(elapsed,1):.0f} product/s"),
    ]:
        print(f"  ✦ {label:<35} {val!s:>15}")
    print("═" * 65)
    print()
    print("  💡 Verifikasi:")
    print("     python nusantara_pg_setup.py --verify")
    print()
    print("  📋 SQL check:")
    print("     SELECT c.name, COUNT(p.id) FROM _categories c")
    print("     JOIN lumra_config_products p ON p.category_id = c.id")
    print("     WHERE c.name IN ('Manual Brew','Espresso Equipment','Grinder','Accessories')")
    print("     GROUP BY c.name;")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Kafe Nusantara — Equipment Generator: 9,999 alat kopi ke PostgreSQL"
    )
    parser.add_argument("--count",       type=int,  default=TARGET_EQUIPMENT,
                        help=f"Jumlah produk alat (default: {TARGET_EQUIPMENT:,})")
    parser.add_argument("--batch-size",  type=int,  default=BATCH_SIZE,
                        help=f"Batch size per commit (default: {BATCH_SIZE})")
    parser.add_argument("--skip-attrs",  action="store_true",
                        help="Skip insert ke productattribute_items")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Preview 50 items tanpa insert ke DB")
    parser.add_argument("--db-name",     type=str, default=None)
    parser.add_argument("--db-user",     type=str, default=None)
    parser.add_argument("--db-password", type=str, default=None)
    parser.add_argument("--db-host",     type=str, default=None)
    parser.add_argument("--db-port",     type=str, default=None)

    args = parser.parse_args()

    if args.db_name:     DB_CONFIG["dbname"]   = args.db_name
    if args.db_user:     DB_CONFIG["user"]      = args.db_user
    if args.db_password: DB_CONFIG["password"]  = args.db_password
    if args.db_host:     DB_CONFIG["host"]      = args.db_host
    if args.db_port:     DB_CONFIG["port"]      = args.db_port

    run_pipeline(
        total_target = args.count,
        batch_size   = args.batch_size,
        skip_attrs   = args.skip_attrs,
        dry_run      = args.dry_run,
    )
