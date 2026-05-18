"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  KAFE NUSANTARA — ADDON GENERATOR v1.0                                     ║
║  2,754 Topping · Syrup · Susu · Creamer · Foam · Extract → PostgreSQL      ║
║                                                                              ║
║  Universe: 81 Sumber Tanaman × 10 Tipe Produk × Packaging Variants         ║
║  Naming: Buah Tropis · Buah Subtropis · Bunga · Rempah · Pohon & Akar      ║
║                                                                              ║
║  Selaras dengan world building The Four Expeditions:                        ║
║  · Setiap bahan adalah temuan ekspedisi dari penjuru Nusantara              ║
║  · Nama tanaman = kode lapangan para kurator rasa                           ║
║  · Tier mencerminkan kelangkaan dan kesulitan sumber bahan                  ║
║                                                                              ║
║  Tier:                                                                      ║
║  · T1 Everyday   (~50%) : Bahan umum, mudah didapat                        ║
║  · T2 Artisan    (~35%) : Bahan premium, proses khusus                     ║
║  · T3 Rare       (~15%) : Bahan langka, musiman, single-origin             ║
║                                                                              ║
║  Usage:                                                                     ║
║    python addon_generator.py                    # full 2,754               ║
║    python addon_generator.py --dry-run          # preview 30 items         ║
║    python addon_generator.py --count 1111       # custom count             ║
║    python addon_generator.py --skip-attrs       # skip attr_items          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random, time, argparse, sys, os, io
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
    import psycopg2, psycopg2.extras, psycopg2.extensions
except ImportError:
    print("❌ pip install psycopg2-binary"); sys.exit(1)

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_system.settings")
    from django.conf import settings as django_settings
    DJANGO_SETTINGS_AVAILABLE = True
except Exception:
    django_settings = None
    DJANGO_SETTINGS_AVAILABLE = False

random.seed(20240303)

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

TARGET_ADDONS       = 2_754   # natural max dari 81 sumber × 10 tipe × packaging
BATCH_SIZE          = 300
SHOW_PROGRESS_EVERY = 300

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — PLANT SOURCE DATABASE (81 sumber)
# ═══════════════════════════════════════════════════════════════════════════════
# Format: (key, display_id, en_name, origin_region, harvest, rarity,
#          flavor_profile, world_building_note, tier_bias)

PLANT_SOURCES = [

    # ── BUAH TROPIS (20) ──────────────────────────────────────────────────────
    ("mangga",       "Mangga",         "Mango",           "Nusantara",          "Sep–Jan",  "common",
     ["tropical sweetness","juicy","stone fruit","honeyed"],
     "Ditemukan oleh ekspeditor di pasar terapung Kalimantan — manis yang tidak perlu penjelasan.", "T1"),

    ("lychee",       "Lychee",         "Lychee",          "Sumatera & Jawa",    "Nov–Feb",  "common",
     ["floral","rose water","sweet","grape-like"],
     "Buah kecil yang menyimpan aroma mawar di dalamnya — temuan dari perkebunan lereng Bandung.", "T1"),

    ("rambutan",     "Rambutan",       "Rambutan",        "Kalimantan & Jawa",  "Des–Mar",  "common",
     ["lychee-adjacent","mild sweet","floral","translucent"],
     "Buah bertanduk yang menyembunyikan kesegaran di balik kulitnya yang liar.", "T1"),

    ("salak",        "Salak",          "Snake Fruit",     "Jawa & Bali",        "Okt–Jan",  "uncommon",
     ["tannic","honey","dry sweet","earthy undertone"],
     "Buah ular dari lereng Merapi — rasa yang tidak ada duanya di luar Nusantara.", "T2"),

    ("markisa",      "Markisa",        "Passion Fruit",   "Sumatera & NTT",     "Sepanjang","common",
     ["tart","tropical","bright","acidic","floral"],
     "Bunga dan buah sekaligus — aromanya menyerang duluan sebelum rasanya sampai.", "T1"),

    ("jambu_biji",   "Jambu Biji",     "Guava",           "Seluruh Nusantara",  "Sepanjang","common",
     ["tropical","sweet-tart","green","herbal-fruity"],
     "Buah paling demokratis di Nusantara — ada di halaman rumah dari Aceh sampai Papua.", "T1"),

    ("nanas",        "Nanas",          "Pineapple",       "Sumatera & Kalimantan","Sepanjang","common",
     ["acidic","bright","tropical","caramelized when roasted"],
     "Asam yang menjadi manis setelah karamelisasi — transformasi yang mengejutkan barista.", "T1"),

    ("kelapa",       "Kelapa",         "Coconut",         "Pesisir Nusantara",  "Sepanjang","common",
     ["creamy","tropical","mild sweet","nutty"],
     "Buah yang tidak pernah jauh dari laut — sekarang hadir dalam cangkir.", "T1"),

    ("pisang",       "Pisang",         "Banana",          "Seluruh Nusantara",  "Sepanjang","common",
     ["sweet","creamy","tropical","caramel undertone"],
     "1.000 varietas pisang di Nusantara, setiap daerah punya pilihan berbeda.", "T1"),

    ("durian",       "Durian",         "Durian",          "Kalimantan & Sumatera","Mei–Agt", "uncommon",
     ["pungent","creamy","custard","complex","divisive"],
     "Raja buah yang membelah dunia menjadi dua kubu — syrup untuk mereka yang tahu.", "T2"),

    ("sirsak",       "Sirsak",         "Soursop",         "Jawa & Sumatera",    "Sepanjang","common",
     ["creamy-tart","tropical","cotton candy","citrus"],
     "Putih daging, gelap rasa — sirsak membawa keseimbangan asam-manis yang jarang ada.", "T1"),

    ("belimbing",    "Belimbing",      "Starfruit",       "Jawa & Kalimantan",  "Sepanjang","uncommon",
     ["tart","crisp","mild","watery-sweet","visual"],
     "Buah bintang yang aromanya malu-malu tapi rasanya langsung hadir.", "T2"),

    ("buah_naga",    "Buah Naga",      "Dragon Fruit",    "Jawa & Kalimantan",  "Sepanjang","common",
     ["mild sweet","earthy","beetroot-adjacent","subtle floral"],
     "Kulitnya dramatis, rasanya elegan — kontras yang indah seperti malam ekspedisi.", "T1"),

    ("pepaya",       "Pepaya",         "Papaya",          "Seluruh Nusantara",  "Sepanjang","common",
     ["tropical","creamy","mild sweet","honeyed","musky"],
     "Buah matahari yang matang di ladang dekat The Bogor Botanical Gate.", "T1"),

    ("jambu_air",    "Jambu Air",      "Water Apple",     "Jawa & Sumatera",    "Sep–Jan",  "uncommon",
     ["crisp","watery","mild tart","floral"],
     "Kesegaran yang tersimpan dalam daging renyah — air dalam bentuk buah.", "T2"),

    ("lengkeng",     "Lengkeng",       "Longan",          "Sumatera & Kalimantan","Agt–Nov","uncommon",
     ["musky sweet","floral","honey","lychee-adjacent"],
     "Mata naga kecil yang menyimpan musk manis di dalamnya.", "T2"),

    ("duku",         "Duku",           "Duku/Langsat",    "Sumatera",           "Des–Mar",  "uncommon",
     ["tannic","sweet-bitter","citrus","grape"],
     "Musiman dari Palembang — aromanya menandai musim, seperti kopi pertanda panen.", "T2"),

    ("cempedak",     "Cempedak",       "Cempedak",        "Kalimantan & Sumatera","Sep–Jan","rare",
     ["jackfruit-adjacent","intense tropical","caramel","funky"],
     "Saudara dekat nangka yang lebih liar dan lebih dalam karakternya.", "T3"),

    ("matoa",        "Matoa",          "Matoa",           "Papua",              "Okt–Feb",  "rare",
     ["rambutan-lychee fusion","coconut undertone","unique","earthy floral"],
     "Hanya dari Papua — buah yang belum punya nama padanan di bahasa manapun. Titik.", "T3"),

    ("gandaria",     "Gandaria",       "Gandaria Plum",   "Maluku & Jawa",      "Nov–Feb",  "rare",
     ["sour-sweet","mango-plum","tropical acid","unique"],
     "Kerabat mangga yang lebih asam dan lebih jujur — hampir punah dari pasar modern.", "T3"),

    # ── BUAH SUBTROPIS (16) ───────────────────────────────────────────────────
    ("stroberi",     "Stroberi",       "Strawberry",      "Jawa (Ciwidey, Bedugul)","Sep–Feb","common",
     ["bright red fruit","sweet-tart","jammy","floral"],
     "Stroberi Jawa dari ketinggian Ciwidey — lebih kecil, lebih asam, lebih berkarakter.", "T1"),

    ("bluberi",      "Bluberi",        "Blueberry",       "Impor · Highland",   "Sepanjang","uncommon",
     ["dark berry","earthy","tart","antioxidant-rich"],
     "Impor tapi diadopsi — karakternya melengkapi kopi natural dengan cara yang tepat.", "T2"),

    ("raspberry",    "Raspberry",      "Raspberry",       "Impor · Highland",   "Sepanjang","uncommon",
     ["tart","bright red","floral","jammy"],
     "Acidity yang menyengat dan bunga yang tersembunyi — paduan yang tidak terduga.", "T2"),

    ("ceri",         "Ceri",           "Cherry",          "Impor / Jawa Tengah","Jun–Agt",  "uncommon",
     ["dark fruit","sweet-tart","almond-adjacent","wine-like"],
     "Cherry Java — kecil, hitam, dan punya kedalaman yang melampaui ukurannya.", "T2"),

    ("plum",         "Plum",           "Plum",            "Impor",              "Jun–Sep",  "uncommon",
     ["dark fruit","tart-sweet","wine","prune at dark roast"],
     "Gelap dan dalam — plum adalah nada minor dalam simfoni rasa kopi.", "T2"),

    ("apricot",      "Apricot",        "Apricot",         "Impor / NTB",        "Mei–Agt",  "uncommon",
     ["stone fruit","honey","dried apricot","light tart"],
     "Manis yang terasa seperti matahari kering — nota dominan kopi honey process.", "T2"),

    ("persik",       "Persik",         "Peach",           "Impor",              "Jun–Sep",  "uncommon",
     ["stone fruit","floral","honeyed","fuzzy sweetness"],
     "Peach adalah musim panas dalam bentuk buah — syrup yang membawa First Light mood.", "T2"),

    ("pir",          "Pir",            "Pear",            "Impor / Malang",     "Agt–Nov",  "uncommon",
     ["mild sweet","floral","green","crisp","delicate"],
     "Paling elegan di antara buah — kehalusan yang menemani Spring blend.", "T2"),

    ("anggur_merah", "Anggur Merah",   "Red Grape",       "Impor / Bali",       "Agt–Nov",  "common",
     ["jammy","wine-like","dark fruit","tannin"],
     "Anggur Bali dari perkebunan eksperimental — setetes wine dalam cangkir kopi.", "T1"),

    ("lemon",        "Lemon",          "Lemon",           "Jawa & Sulawesi",    "Sepanjang","common",
     ["bright citrus","tart","zesty","clean acid"],
     "Acid paling bersih — lemon adalah kompas rasa yang selalu menunjuk ke kejernihan.", "T1"),

    ("jeruk_nipis",  "Jeruk Nipis",    "Lime",            "Seluruh Nusantara",  "Sepanjang","common",
     ["sharp citrus","floral-citrus","bright","tropical acid"],
     "Jeruk kecil dengan nyali besar — getiran di ujung espresso tonic yang sempurna.", "T1"),

    ("mandarin",     "Mandarin",       "Mandarin",        "Jawa & Kalimantan",  "Jun–Agt",  "common",
     ["sweet citrus","mild","floral","approachable"],
     "Citrus yang paling bersahabat — gateway rasa untuk mereka baru mulai ekspedisi.", "T1"),

    ("yuzu",         "Yuzu",           "Yuzu",            "Impor / Jawa Dataran Tinggi","Des–Feb","rare",
     ["floral citrus","complex","grapefruit-lemon hybrid","aromatic"],
     "Citrus Jepang yang diadaptasi — aromanya memenuhi ruangan sebelum dicicipi.", "T3"),

    ("bergamot",     "Bergamot",       "Bergamot",        "Impor / Mediterania","Mar–Jun",  "rare",
     ["Earl Grey floral","citrus-perfume","complex","distinctive"],
     "Bergamot adalah nama lain untuk kerinduan — aroma teh Earl Grey dalam wujud liquid.", "T3"),

    ("kaffir_lime",  "Jeruk Purut",    "Kaffir Lime",     "Seluruh Nusantara",  "Sepanjang","uncommon",
     ["aromatic citrus","herbal","distinctive","floral-earthy"],
     "Bukan buahnya, tapi kulitnya — zest yang membawa aroma dapur dan hutan sekaligus.", "T2"),

    ("pomelo",       "Jeruk Bali",     "Pomelo",          "Jawa & Bali",        "Agt–Nov",  "uncommon",
     ["mild bitter","floral","grapefruit-gentle","thick pith"],
     "Jeruk besar yang rasanya pelan datang — seperti cerita yang perlu waktu untuk dipahami.", "T2"),

    # ── BUNGA (15) ────────────────────────────────────────────────────────────
    ("melati",       "Melati",         "Jasmine",         "Jawa & Sumatera",    "Sepanjang","common",
     ["floral","delicate","tea-like","sweet aromatic"],
     "Bunga nasional yang sudah meracuni teh Indonesia selama berabad-abad. Kini kopi.", "T1"),

    ("mawar",        "Mawar",          "Rose",            "Jawa (Malang, Dieng)","Sepanjang","common",
     ["floral","romantic","sweet","perfumed"],
     "Mawar bukan hanya simbol — dalam syrup, ia membawa dimensi rasa yang tidak tergantikan.", "T1"),

    ("lavender",     "Lavender",       "Lavender",        "Impor / Jawa Tengah","Jun–Sep",  "uncommon",
     ["herbal floral","calming","provence","slightly medicinal"],
     "Ekspeditor Twilight Bivouac kenal lavender — aroma yang menenangkan setelah perjalanan panjang.", "T2"),

    ("chamomile",    "Chamomile",      "Chamomile",       "Impor / Jawa Dataran Tinggi","Mei–Agt","uncommon",
     ["gentle floral","apple-honey","calming","herbal"],
     "Bunga kecil yang menyimpan ketenangan — ditemukan di sudut The Cikini Reading Room.", "T2"),

    ("hibiscus",     "Hibiscus / Rosella","Hibiscus",    "Jawa & NTT",         "Sepanjang","common",
     ["tart","cranberry-like","bright red","floral acid"],
     "Rosella merah yang juga tumbuh di kebun penjelajah — asam cerah yang menyegarkan.", "T1"),

    ("elderflower",  "Elderflower",    "Elderflower",     "Impor / Eropa",      "Mei–Jun",  "rare",
     ["delicate floral","honey-like","spring","light muscat"],
     "Bunga tua Eropa yang menemukan rumah barunya di Summer collection The Open Horizon.", "T3"),

    ("violet",       "Violet",         "Violet",          "Impor",              "Mar–Mei",  "rare",
     ["perfumed","powdery floral","sweet","candy-like"],
     "Floral yang paling misterius — syrup violet bercerita tentang kegelapan yang harum.", "T3"),

    ("calendula",    "Calendula",      "Calendula",       "Jawa & Bali",        "Apr–Sep",  "uncommon",
     ["mild floral","earthy","slightly bitter","herbal"],
     "Bunga matahari kecil yang mekar di The Kintamani Crater Post — earthiness yang menenangkan.", "T2"),

    ("osmanthus",    "Osmanthus",      "Osmanthus",       "Impor / Asia Timur", "Sep–Nov",  "rare",
     ["apricot-floral","honey","delicate","complex"],
     "Bunga musim gugur Asia yang aromanya bertahan lama bahkan setelah diseduh.", "T3"),

    ("sakura",       "Sakura",         "Cherry Blossom",  "Impor / Jepang",     "Mar–Apr",  "rare",
     ["delicate floral","light sweet","subtle","seasonal"],
     "Sakura hanya ada sebentar — dan itulah yang membuatnya berharga. Limited by nature.", "T3"),

    ("butterfly_pea","Telang",         "Butterfly Pea",   "Seluruh Nusantara",  "Sepanjang","common",
     ["earthy floral","color-changing (blue→purple)","mild","visual"],
     "Bunga telang adalah sihir dalam cangkir — biru berubah ungu saat pH berubah.", "T1"),

    ("rosehip",      "Rose Hip",       "Rose Hip",        "Impor / Jawa Dataran Tinggi","Agt–Nov","uncommon",
     ["tart","berry-like","rose","vitamin C rich"],
     "Buah mawar yang lebih asam dari bunganya — ironi yang menyenangkan.", "T2"),

    ("dandelion",    "Dandelion",      "Dandelion",       "Jawa Dataran Tinggi","Mar–Agt",  "uncommon",
     ["bitter","earthy","coffee-adjacent","herbal"],
     "Gulma yang ternyata adalah minuman — akar dandelion sudah menjadi kopi sejak abad pertengahan.", "T2"),

    ("chrysanthemum","Krisan",         "Chrysanthemum",   "Jawa & Sumatera",    "Sepanjang","uncommon",
     ["floral","slightly bitter","herbal","cooling"],
     "Bunga teh Tiongkok yang sudah berakar di Nusantara selama berabad-abad.", "T2"),

    ("jasmine_green","Jasmine Green Tea","Jasmine Green",  "Jawa & Sumatera",   "Sepanjang","uncommon",
     ["double floral","green tea","light","clean"],
     "Melati yang meresap ke dalam teh hijau — aroma berlapis dari satu sumber.", "T2"),

    # ── REMPAH & DAUN (20) ───────────────────────────────────────────────────
    ("kayu_manis",   "Kayu Manis",     "Cinnamon",        "Sumatera & Jawa",    "Sepanjang","common",
     ["warm spice","sweet","baking","comforting"],
     "Rempah paling akrab di Nusantara — aromanya menghidupkan The Amber Descent.", "T1"),

    ("cengkeh",      "Cengkeh",        "Clove",           "Maluku",             "Okt–Jan",  "uncommon",
     ["intense spice","medicinal","dark","numbing"],
     "Dari Maluku ke dunia — cengkeh adalah rempah yang mengubah sejarah umat manusia.", "T2"),

    ("kapulaga",     "Kapulaga",       "Cardamom",        "Jawa & Sumatera",    "Sepanjang","uncommon",
     ["complex spice","citrus-herbal","aromatic","Middle Eastern"],
     "Rempah kopi Arab yang menemukan koalisi sempurna dengan kopi Nusantara.", "T2"),

    ("vanila",       "Vanila",         "Vanilla",         "Jawa & Sulawesi",    "Sepanjang","common",
     ["sweet","creamy","floral","warm","universal"],
     "Vanila Jawa adalah standar dunia — manis yang tidak pernah salah.", "T1"),

    ("pala",         "Pala",           "Nutmeg",          "Maluku (Banda)",     "Jun–Agt",  "uncommon",
     ["warm spice","woody","slightly sweet","complex"],
     "Pala Banda yang pernah diperebutkan kerajaan Eropa — kini bebas dalam syrup.", "T2"),

    ("jahe",         "Jahe",           "Ginger",          "Seluruh Nusantara",  "Sepanjang","common",
     ["spicy","warm","pungent","digestive","earthy"],
     "Jahe adalah api dalam bentuk rempah — menghangatkan dari dalam sejak zaman ekspedisi pertama.", "T1"),

    ("kunyit",       "Kunyit",         "Turmeric",        "Seluruh Nusantara",  "Sepanjang","common",
     ["earthy","bitter","warm","golden","anti-inflammatory"],
     "Emas Nusantara — kunyit adalah warna dan karakter yang tidak bisa disembunyikan.", "T1"),

    ("lengkuas",     "Lengkuas",       "Galangal",        "Seluruh Nusantara",  "Sepanjang","common",
     ["peppery","citrus-pine","herbal","earthy"],
     "Jahe yang lebih sophiticated — karakter dapur Nusantara yang kuat tanpa mendominasi.", "T1"),

    ("serai",        "Serai",          "Lemongrass",      "Seluruh Nusantara",  "Sepanjang","common",
     ["citrus-herbal","fresh","aromatic","light earthy"],
     "Serai adalah kesegaran yang berasal dari bumi — aroma yang menarik First Light.", "T1"),

    ("pandan",       "Daun Pandan",    "Pandan",          "Asia Tenggara",      "Sepanjang","common",
     ["green","floral-nutty","sweet","distinctive Nusantara"],
     "Vanila Asia Tenggara — tidak ada padanannya di belahan bumi manapun.", "T1"),

    ("mint",         "Daun Mint",      "Mint",            "Jawa Dataran Tinggi","Sepanjang","common",
     ["cooling","fresh","menthol","cleansing"],
     "Penyegar paling cepat bekerja — setetes mint mengubah segalanya dalam dua detik.", "T1"),

    ("basil",        "Kemangi",        "Thai Basil",      "Seluruh Nusantara",  "Sepanjang","common",
     ["herbal","anise-clove","peppery","aromatic"],
     "Kemangi bukan hiasan — dalam cold brew yang tepat, ia adalah karakter utama.", "T1"),

    ("rosemary",     "Rosemary",       "Rosemary",        "Jawa Dataran Tinggi","Sepanjang","uncommon",
     ["piney","herbal","resinous","aromatic","savory-sweet"],
     "Rempah pegunungan yang menemukan padanan sempurna dengan dark roast earthy.", "T2"),

    ("thyme",        "Thyme",          "Thyme",           "Jawa Dataran Tinggi","Sepanjang","uncommon",
     ["herbal","slightly lemon","savory","delicate"],
     "Thyme adalah subtilitas — karakternya hanya muncul bagi yang mau memperhatikan.", "T2"),

    ("lada_hitam",   "Lada Hitam",     "Black Pepper",    "Lampung & Kalimantan","Sepanjang","common",
     ["pungent spice","sharp","bold","earthy heat"],
     "Raja rempah yang lebih kompleks dari yang terlihat — bukan sekadar pedas.", "T1"),

    ("lada_putih",   "Lada Putih",     "White Pepper",    "Bangka Belitung",    "Sepanjang","uncommon",
     ["sharp spice","fermented","musty","complex heat"],
     "Lada putih Bangka adalah berbeda kelas dari lada biasa — proses fermentasi mengubah segalanya.", "T2"),

    ("wijen",        "Wijen",          "Sesame",          "Jawa & NTB",         "Mar–Jun",  "uncommon",
     ["nutty","toasted","earthy","rich","buttery"],
     "Biji kecil dengan kandungan lemak yang memberi body dan nuttiness unik.", "T2"),

    ("saffron",      "Safron",         "Saffron",         "Impor / Iran & Kashmir","Okt–Nov","rare",
     ["floral","honey","metallic","complex","most expensive"],
     "Rempah termahal di dunia — 1 gram saffron = 200 bunga crocus dipetik tangan.", "T3"),

    ("kencur",       "Kencur",         "Galangal Minor",  "Jawa",               "Sepanjang","uncommon",
     ["camphor-like","earthy","pungent","warming"],
     "Rempah rahasia dapur Jawa yang belum pernah dikenal dunia luar — saatnya diperkenalkan.", "T2"),

    ("andaliman",    "Andaliman",      "Sichuan Pepper Nusantara","Sumatera (Batak)","Des–Mar","rare",
     ["numbing spice","citrus","unique","Batak cuisine"],
     "Andaliman dari tanah Batak — Sichuan pepper Nusantara yang menimbulkan sensasi kebas.", "T3"),

    # ── POHON & AKAR (10) ────────────────────────────────────────────────────
    ("kayu_secang",  "Kayu Secang",    "Sappanwood",      "Jawa & Sumatera",    "Sepanjang","uncommon",
     ["earthy red","woody","mild sweet","antioxidant"],
     "Kayu merah yang mewarnai minuman tradisional Jawa — sekarang menemukan peran modernnya.", "T2"),

    ("kayu_manis_bark","Kayu Manis Bark","Cinnamon Bark",  "Sumatera",          "Sepanjang","uncommon",
     ["intensely spiced","woody","warm","baking"],
     "Lebih dalam dari bubuk kayu manis — bark memberikan ekstraksi lambat yang lebih kaya.", "T2"),

    ("cacao_bark",   "Cacao Bark",     "Cacao Shell/Husk","Sulawesi & Jawa",    "Sepanjang","uncommon",
     ["mild chocolate","earthy","tea-like","subtle"],
     "Kulit biji kakao yang biasanya terbuang — kurator menemukan nilainya dalam teh dan syrup.", "T2"),

    ("akar_licorice","Akar Licorice",  "Licorice Root",   "Impor",              "Sepanjang","rare",
     ["anise-sweet","distinct","herbal","bold","polarizing"],
     "Manis yang sangat berbeda dari gula — licorice adalah karakter yang tidak bisa dinegosiasi.", "T3"),

    ("maple_bark",   "Maple Bark",     "Maple",           "Impor / Kanada",     "Mar–Apr",  "rare",
     ["maple syrup","warm sweet","caramel","autumn"],
     "Sap pohon maple yang membeku di musim dingin dan mencair di musim semi — metafora ekspedisi.", "T3"),

    ("oak_smoked",   "Oak Smoked",     "Smoked Oak",      "Impor / Eropa",      "Sepanjang","rare",
     ["smoky","woody","whisky-adjacent","bold","savory-sweet"],
     "Kayu oak yang dibakar perlahan memberi dimensi rasa yang tidak ada di tanaman lain.", "T3"),

    ("bambu",        "Bambu",          "Bamboo",          "Seluruh Nusantara",  "Sepanjang","uncommon",
     ["grassy","fresh","clean","mineral","subtle"],
     "Bambu muda yang diekstrak — kesegaran yang berasal dari tanaman paling cepat tumbuh di bumi.", "T2"),

    ("bajakah",      "Kayu Bajakah",   "Bajakah Root",    "Kalimantan",         "Sepanjang","rare",
     ["earthy","slightly sweet","tannin","herbal","local pride"],
     "Akar ajaib Kalimantan yang baru dipelajari dunia — local pride dalam bentuk extract.", "T3"),

    ("akar_jahe",    "Akar Jahe Tua",  "Old Ginger Root", "Jawa & Sumatera",    "Sepanjang","uncommon",
     ["intense spicy","earthy","pungent","warming-deep"],
     "Jahe yang dibiarkan menua dan mengering — karakternya jauh lebih dalam dari jahe segar.", "T2"),

    ("secang_hitam", "Secang Hitam",   "Black Sappanwood","Jawa",               "Sepanjang","rare",
     ["deep red","tannic","woody","complex","antioxidant-rich"],
     "Varietas langka kayu secang yang hitam pekat — ditemukan oleh kurator di pasar jamu Solo.", "T3"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — PRODUCT TYPE DATABASE (10 tipe)
# ═══════════════════════════════════════════════════════════════════════════════
# Format: (type_key, display, category_db, unit, has_variants,
#          variant_forms, description_template, usage_note,
#          min_stock, max_stock, has_expiry, track_batch,
#          price_t1_range, price_t2_range, price_t3_range)

PRODUCT_TYPES = [
    {
        "key":      "syrup",
        "display":  "Syrup",
        "category": "Addon Syrup",
        "unit":     "Botol",
        "variants": [
            ("250ml Bottle",  "SYR-250", 1.0),
            ("750ml Bottle",  "SYR-750", 2.6),
            ("1L Bottle",     "SYR-1L",  3.5),
            ("5L Jerigen",    "SYR-5L",  15.0),
        ],
        "desc_template": "Syrup {plant} berkualitas tinggi — diekstrak dari {plant_en} segar {origin}. Profil rasa: {flavor}. Cocok untuk kopi, teh, mocktail, dan dessert. {world_note}",
        "usage": "Espresso drinks · Signature coffee · Mocktail · Dessert",
        "min_stock": 6, "max_stock": 120,
        "has_expiry": True, "track_batch": True,
        "price_t1": (45_000,  95_000),
        "price_t2": (85_000,  185_000),
        "price_t3": (175_000, 450_000),
    },
    {
        "key":      "topping_sauce",
        "display":  "Topping Sauce",
        "category": "Addon Topping",
        "unit":     "Botol",
        "variants": [
            ("150ml Squeeze", "SCS-150", 1.0),
            ("300ml Squeeze", "SCS-300", 1.9),
            ("1L Pump Bottle","SCS-1L",  6.0),
        ],
        "desc_template": "Saus topping {plant} untuk drizzle dan finishing. Diekstrak dari {plant_en} pilihan {origin}. {flavor}. {world_note}",
        "usage": "Drizzle · Latte Art · Dessert topping · Waffle",
        "min_stock": 6, "max_stock": 60,
        "has_expiry": True, "track_batch": True,
        "price_t1": (35_000,  75_000),
        "price_t2": (65_000,  145_000),
        "price_t3": (130_000, 380_000),
    },
    {
        "key":      "powder_mix",
        "display":  "Powder Mix",
        "category": "Addon Powder",
        "unit":     "Sachet",
        "variants": [
            ("100g Pouch",    "PWD-100", 1.0),
            ("250g Pouch",    "PWD-250", 2.3),
            ("1kg Bulk Bag",  "PWD-1KG", 8.5),
        ],
        "desc_template": "Bubuk minuman {plant} premium — dikeringkan dan digiling dari {plant_en} {origin}. Mudah dilarutkan, cocok untuk hot dan cold drinks. {world_note}",
        "usage": "Powder drinks · Blended beverages · Ice cream · Baking",
        "min_stock": 10, "max_stock": 200,
        "has_expiry": True, "track_batch": True,
        "price_t1": (35_000,  80_000),
        "price_t2": (70_000,  160_000),
        "price_t3": (150_000, 420_000),
    },
    {
        "key":      "milk_nabati",
        "display":  "Susu Nabati",
        "category": "Addon Milk",
        "unit":     "Karton",
        "variants": [
            ("250ml Single",  "MLK-250", 1.0),
            ("1L Carton",     "MLK-1L",  3.5),
            ("Barista 1L",    "MLK-BAR", 4.2),
        ],
        "desc_template": "Susu nabati berbasis {plant} — plant-based milk dari {plant_en} pilihan {origin}. Bebas laktosa, cocok untuk vegan dan lactose-intolerant. {world_note}",
        "usage": "Latte · Cappuccino · Barista blend · Smoothie",
        "min_stock": 12, "max_stock": 144,
        "has_expiry": True, "track_batch": True,
        "price_t1": (18_000,  45_000),
        "price_t2": (38_000,  85_000),
        "price_t3": (75_000,  175_000),
    },
    {
        "key":      "creamer",
        "display":  "Creamer",
        "category": "Addon Creamer",
        "unit":     "Sachet",
        "variants": [
            ("50 Sachet Box", "CRM-50S", 1.0),
            ("500g Pouch",    "CRM-500", 2.8),
            ("1kg Bulk",      "CRM-1KG", 5.0),
        ],
        "desc_template": "Creamer non-dairy berbasis {plant} — menghadirkan kekayaan rasa {plant_en} ke dalam kopi tanpa susu. {world_note}",
        "usage": "Kopi · Teh · Hot beverages · Self-service station",
        "min_stock": 10, "max_stock": 200,
        "has_expiry": True, "track_batch": False,
        "price_t1": (25_000,  55_000),
        "price_t2": (50_000,  110_000),
        "price_t3": (100_000, 250_000),
    },
    {
        "key":      "foam",
        "display":  "Flavoured Foam",
        "category": "Addon Foam",
        "unit":     "Botol",
        "variants": [
            ("250ml Bottle",  "FOM-250", 1.0),
            ("500ml Bottle",  "FOM-500", 1.8),
        ],
        "desc_template": "Foam mix beraroma {plant} — siap dikocok menjadi cold foam atau hot foam. Menghadirkan {flavor} dalam lapisan ringan di atas minuman. {world_note}",
        "usage": "Cold foam topping · Hot cappuccino foam · Dessert cloud",
        "min_stock": 6, "max_stock": 60,
        "has_expiry": True, "track_batch": True,
        "price_t1": (55_000,  120_000),
        "price_t2": (105_000, 230_000),
        "price_t3": (210_000, 550_000),
    },
    {
        "key":      "extract_concentrate",
        "display":  "Extract Concentrate",
        "category": "Addon Extract",
        "unit":     "Botol",
        "variants": [
            ("50ml Dropper",  "EXT-50",  1.0),
            ("100ml Bottle",  "EXT-100", 1.8),
            ("500ml Pro",     "EXT-500", 8.0),
        ],
        "desc_template": "Ekstrak pekat {plant} — cold-extracted atau steam-distilled dari {plant_en} {origin}. Gunakan 3–5 tetes per sajian. {world_note}",
        "usage": "Specialty drinks · Baking · Cocktail & mocktail · Precision flavoring",
        "min_stock": 6, "max_stock": 60,
        "has_expiry": True, "track_batch": True,
        "price_t1": (65_000,  150_000),
        "price_t2": (130_000, 300_000),
        "price_t3": (280_000, 750_000),
    },
    {
        "key":      "boba_topping",
        "display":  "Boba & Jelly Topping",
        "category": "Addon Boba",
        "unit":     "Gram",
        "variants": [
            ("500g Pack",     "BOB-500", 1.0),
            ("1kg Pack",      "BOB-1KG", 1.9),
            ("3kg Bulk",      "BOB-3KG", 5.5),
        ],
        "desc_template": "Boba & jelly beraroma {plant} — pearl atau jelly dengan rasa {plant_en} dari {origin}. Tekstur kenyal, rasa autentik. {world_note}",
        "usage": "Bubble tea · Cold drinks topping · Dessert mix-in",
        "min_stock": 10, "max_stock": 100,
        "has_expiry": True, "track_batch": True,
        "price_t1": (35_000,  75_000),
        "price_t2": (65_000,  145_000),
        "price_t3": (130_000, 350_000),
    },
    {
        "key":      "dried_topping",
        "display":  "Dried Fruit & Flower Topping",
        "category": "Addon Topping",
        "unit":     "Gram",
        "variants": [
            ("50g Bag",       "DRY-50",  1.0),
            ("100g Bag",      "DRY-100", 1.9),
            ("500g Bulk",     "DRY-500", 8.0),
        ],
        "desc_template": "Topping kering {plant} — irisan atau bunga {plant_en} yang dikeringkan dengan metode freeze-dry atau sun-dry dari {origin}. Visual dan rasa sekaligus. {world_note}",
        "usage": "Garnish · Latte art decoration · Dessert topping · Retail packaging",
        "min_stock": 5, "max_stock": 50,
        "has_expiry": True, "track_batch": True,
        "price_t1": (45_000,  100_000),
        "price_t2": (90_000,  200_000),
        "price_t3": (185_000, 500_000),
    },
    {
        "key":      "infused_sugar",
        "display":  "Infused Sugar",
        "category": "Addon Sugar",
        "unit":     "Gram",
        "variants": [
            ("200g Jar",      "SUG-200", 1.0),
            ("500g Bag",      "SUG-500", 2.4),
            ("1kg Bulk",      "SUG-1KG", 4.5),
        ],
        "desc_template": "Gula infused {plant} — cane sugar atau coconut sugar yang diinfus dengan {plant_en} dari {origin}. Sweetener yang juga membawa karakter rasa. {world_note}",
        "usage": "Sweetener · Coffee bar · Cocktail sugar · Gifting",
        "min_stock": 10, "max_stock": 100,
        "has_expiry": True, "track_batch": False,
        "price_t1": (28_000,  65_000),
        "price_t2": (55_000,  125_000),
        "price_t3": (110_000, 300_000),
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TIER & RARITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

TIER_META = {
    "T1": {"name": "Tier 1 — Everyday",      "label": "Standard",    "emoji": "◆"},
    "T2": {"name": "Tier 2 — Artisan",        "label": "Premium",     "emoji": "◈"},
    "T3": {"name": "Tier 3 — Rare & Exotic",  "label": "Single Origin Rare", "emoji": "✦"},
}

RARITY_TO_TIER = {"common": "T1", "uncommon": "T2", "rare": "T3"}

SEASON_FLAVOR_MAP = {
    "floral": "Spring", "fruity": "Summer", "tropical": "Summer",
    "warm spice": "Autumn", "earthy": "Autumn", "smoky": "Winter",
    "cooling": "Spring", "citrus": "Summer", "herbal": "Spring",
    "spicy": "Winter", "sweet": "Autumn", "dark": "Winter",
    "tart": "Summer", "nutty": "Autumn",
}

def flavor_to_season(flavor_list):
    for f in flavor_list:
        for keyword, season in SEASON_FLAVOR_MAP.items():
            if keyword in f.lower():
                return season
    return random.choice(["Winter","Summer","Autumn","Spring"])

SEASON_UNIVERSE = {
    "Winter": "The Dark Passage",
    "Summer": "The Open Horizon",
    "Autumn": "The Amber Descent",
    "Spring": "The First Ascent",
}

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — NAME, SKU & DESCRIPTION GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

_sku_counter = {"T1": 0, "T2": 0, "T3": 0}

def make_addon_sku(plant_key, type_key, tier_code, variant_code):
    _sku_counter[tier_code] += 1
    plant_ab = plant_key[:4].upper().replace("_","")
    type_ab  = type_key[:3].upper().replace("_","")
    seq      = _sku_counter[tier_code]
    return f"AD-{plant_ab}-{type_ab}-{tier_code}-{seq:04d}-{variant_code}"

def make_addon_name(plant_display, type_display, variant_label, tier_code):
    if tier_code == "T3":
        prefix = random.choice(["Single Origin","Rare Harvest","Artisan Reserve","Expedition Grade"])
        return f"{prefix} {plant_display} {type_display} [{variant_label}]"
    elif tier_code == "T2":
        prefix = random.choice(["Artisan","Premium","Small Batch","Reserve"])
        return f"{prefix} {plant_display} {type_display} [{variant_label}]"
    else:
        return f"{plant_display} {type_display} [{variant_label}]"

def make_addon_description(plant, ptype, tier_code, season):
    key, display, en_name, origin, harvest, rarity, flavors, world_note, _ = plant
    flavor_str = ", ".join(flavors[:3])
    su = SEASON_UNIVERSE[season]

    desc = ptype["desc_template"].format(
        plant    = display,
        plant_en = en_name,
        origin   = origin.split("&")[0].strip(),
        flavor   = flavor_str,
        world_note = world_note,
    )

    if tier_code == "T3":
        desc += (
            f" — Hanya tersedia dalam batch terbatas sesuai musim panen {harvest}. "
            f"Setiap botol/kemasan mencantumkan nomor batch dan tanggal harvest. "
            f"Bagian dari koleksi Rare & Exotic {su}."
        )
    elif tier_code == "T2":
        desc += f" — Artisan batch, small-batch production dari {origin}."

    return desc[:490]

def make_addon_attrs(plant, ptype, tier_code, variant_label, season, price):
    key, display, en_name, origin, harvest, rarity, flavors, world_note, _ = plant
    su = SEASON_UNIVERSE[season]
    tm = TIER_META[tier_code]

    return {
        # Plant identity
        "plant_name_id":       display,
        "plant_name_en":       en_name,
        "plant_origin":        origin,
        "plant_harvest":       harvest,
        "plant_rarity":        rarity,
        "plant_family":        _plant_family(key),
        # Product
        "product_type":        ptype["display"],
        "product_category":    ptype["category"],
        "usage":               ptype["usage"],
        "variant":             variant_label,
        # Flavor
        "flavor_profile":      ", ".join(flavors[:4]),
        "flavor_primary":      flavors[0] if flavors else "complex",
        "flavor_secondary":    flavors[1] if len(flavors) > 1 else "",
        # Tier & world building
        "addon_tier":          tm["name"],
        "tier_code":           tier_code,
        "tier_label":          tm["label"],
        "season":              season,
        "season_universe":     su,
        # Pairing
        "pairs_with_blend":    _pairing_blend_tier(rarity),
        "pairs_with_method":   _pairing_brew_method(key),
        "pairs_with_sesi":     _pairing_sesi(flavors),
        "outpost_affinity":    _pairing_outpost(key),
        # Expedition world note
        "world_note":          world_note[:250],
        "expedition_use":      _expedition_use(ptype["key"], tier_code),
    }

def _plant_family(plant_key):
    families = {
        "mangga":"Anacardiaceae","lychee":"Sapindaceae","rambutan":"Sapindaceae",
        "salak":"Arecaceae","markisa":"Passifloraceae","jambu_biji":"Myrtaceae",
        "nanas":"Bromeliaceae","kelapa":"Arecaceae","pisang":"Musaceae",
        "durian":"Malvaceae","sirsak":"Annonaceae","belimbing":"Oxalidaceae",
        "buah_naga":"Cactaceae","pepaya":"Caricaceae","jambu_air":"Myrtaceae",
        "lengkeng":"Sapindaceae","duku":"Meliaceae","cempedak":"Moraceae",
        "matoa":"Sapindaceae","gandaria":"Anacardiaceae",
        "stroberi":"Rosaceae","bluberi":"Ericaceae","raspberry":"Rosaceae",
        "ceri":"Rosaceae","plum":"Rosaceae","apricot":"Rosaceae",
        "persik":"Rosaceae","pir":"Rosaceae","anggur_merah":"Vitaceae",
        "lemon":"Rutaceae","jeruk_nipis":"Rutaceae","mandarin":"Rutaceae",
        "yuzu":"Rutaceae","bergamot":"Rutaceae","kaffir_lime":"Rutaceae","pomelo":"Rutaceae",
        "melati":"Oleaceae","mawar":"Rosaceae","lavender":"Lamiaceae",
        "chamomile":"Asteraceae","hibiscus":"Malvaceae","elderflower":"Adoxaceae",
        "violet":"Violaceae","calendula":"Asteraceae","osmanthus":"Oleaceae",
        "sakura":"Rosaceae","butterfly_pea":"Fabaceae","rosehip":"Rosaceae",
        "dandelion":"Asteraceae","chrysanthemum":"Asteraceae","jasmine_green":"Oleaceae",
        "kayu_manis":"Lauraceae","cengkeh":"Myrtaceae","kapulaga":"Zingiberaceae",
        "vanila":"Orchidaceae","pala":"Myristicaceae","jahe":"Zingiberaceae",
        "kunyit":"Zingiberaceae","lengkuas":"Zingiberaceae","serai":"Poaceae",
        "pandan":"Pandanaceae","mint":"Lamiaceae","basil":"Lamiaceae",
        "rosemary":"Lamiaceae","thyme":"Lamiaceae","lada_hitam":"Piperaceae",
        "lada_putih":"Piperaceae","wijen":"Pedaliaceae","saffron":"Iridaceae",
        "kencur":"Zingiberaceae","andaliman":"Rutaceae",
        "kayu_secang":"Fabaceae","kayu_manis_bark":"Lauraceae","cacao_bark":"Malvaceae",
        "akar_licorice":"Fabaceae","maple_bark":"Sapindaceae","oak_smoked":"Fagaceae",
        "bambu":"Poaceae","bajakah":"Vitaceae","akar_jahe":"Zingiberaceae","secang_hitam":"Fabaceae",
    }
    return families.get(plant_key, "Plantae")

def _pairing_blend_tier(rarity):
    return {"common": "T1 — The Vanguard", "uncommon": "T2 — The Curator's Reserve",
            "rare": "T3 — The Grand Artifact"}[rarity]

def _pairing_brew_method(plant_key):
    pairings = {
        "melati": "V60 · Chemex", "mawar": "V60 · AeroPress", "lavender": "Chemex · Cold Brew",
        "kayu_manis": "Espresso · French Press", "jahe": "French Press · Vietnam Drip",
        "vanila": "Semua metode", "butterfly_pea": "Cold Brew · Iced drinks",
        "lemon": "Espresso Tonic · Cold Brew", "markisa": "Cold Brew · AeroPress",
        "kelapa": "Vietnam Drip · Kopi Susu", "pandan": "Semua metode · Khas Asia",
        "mint": "Cold Brew · Iced Americano", "hibiscus": "Cold Brew · Iced Tea",
    }
    return pairings.get(plant_key, "Semua metode brewing")

def _pairing_sesi(flavors):
    flavor_str = " ".join(flavors).lower()
    if any(k in flavor_str for k in ["warm","spice","dark","smoky","pungent"]):
        return "Twilight Bivouac"
    if any(k in flavor_str for k in ["citrus","tropical","tart","bright","cooling"]):
        return "Midday Transit"
    return "First Light"

def _pairing_outpost(plant_key):
    outpost_map = {
        "melati":       "Outpost 07: The Cikini Reading Room · Outpost 15: The Solo Kepatihan",
        "pandan":       "Semua Outpost — terutama Outpost 23: The Aceh Gateway",
        "butterfly_pea":"Outpost 30: The Kintamani Crater Post · Outpost 31: The Denpasar Island Hub",
        "kayu_secang":  "Outpost 15: The Solo Kepatihan Shelter",
        "cengkeh":      "Outpost 23: The Aceh Gateway · Outpost 32: The Makassar Fortpost",
        "kapulaga":     "Outpost 24: The Medan Trade Post",
        "vanila":       "Semua Outpost",
        "durian":       "Outpost 02: The Priangan Counting House (seasonal)",
        "matoa":        "Outpost 35: The Eastern Terminus",
        "bajakah":      "Outpost 35: The Eastern Terminus",
        "andaliman":    "Outpost 28: The Batak Ridge Shelter",
    }
    return outpost_map.get(plant_key, "Semua Outpost The Archipelagic Outposts")

def _expedition_use(type_key, tier_code):
    uses = {
        "syrup":              "Bar service · Signature drinks · Seasonal specials",
        "topping_sauce":      "Finishing touch · Latte art · Dessert plating",
        "powder_mix":         "Blended beverages · Cold brew infusion · Take-home retail",
        "milk_nabati":        "Vegan menu · Barista alternative · Health-conscious guests",
        "creamer":            "Self-service station · To-go drinks · Quick service",
        "foam":               "Premium latte topping · Twilight Bivouac signature",
        "extract_concentrate":"Precision flavoring · Cocktail bar · R&D experiments",
        "boba_topping":       "Gen-Z menu · Bubble drinks · Social media content",
        "dried_topping":      "Visual garnish · Premium packaging · Gift products",
        "infused_sugar":      "Sweetener upgrade · Bar accessory · Retail gifting",
    }
    t3_add = " — RARE BATCH: disajikan hanya di Outpost pilihan dengan advance order." if tier_code == "T3" else ""
    return uses.get(type_key, "Bar service") + t3_add

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — PRICING
# ═══════════════════════════════════════════════════════════════════════════════

RARITY_MULT = {"common": 1.0, "uncommon": 1.35, "rare": 2.2}

def compute_addon_price(ptype, tier_code, rarity, variant_mult):
    lo, hi = ptype[f"price_{tier_code.lower()}"]
    base    = int(lo + (hi - lo) * (0.2 + random.random() * 0.65))
    r_mult  = RARITY_MULT.get(rarity, 1.0)
    price   = int(base * r_mult * variant_mult)
    price   = max(round(price / 1_000) * 1_000, lo)
    return min(int(price), int(hi * r_mult * variant_mult * 1.15))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — DATABASE LAYER (identical pattern to grand_million_generator.py)
# ═══════════════════════════════════════════════════════════════════════════════

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(autocommit=False)
    return conn

def normalize_attr_value(value, max_length=255):
    text = str(value)
    return (text, False) if len(text) <= max_length else (text[:max_length], True)

def fetch_existing_barcodes(conn, barcodes):
    if not barcodes: return {}
    cur = conn.cursor()
    cur.execute("SELECT id, barcode FROM lumra_config_products WHERE barcode = ANY(%s)", (barcodes,))
    result = {b: pid for pid, b in cur.fetchall()}
    cur.close()
    return result

def fetch_existing_skus(conn, skus):
    if not skus: return {}
    cur = conn.cursor()
    cur.execute("SELECT id, sku FROM lumra_config_productvariants WHERE sku = ANY(%s)", (skus,))
    result = {sku: vid for vid, sku in cur.fetchall()}
    cur.close()
    return result

def fetch_existing_attr_keys(conn, variant_ids):
    if not variant_ids: return set()
    cur = conn.cursor()
    cur.execute(
        "SELECT variant_id, attr_name, attr_value FROM lumra_config_productattribute_items WHERE variant_id = ANY(%s)",
        (variant_ids,)
    )
    result = set(cur.fetchall())
    cur.close()
    return result

def fetch_fk_ids(conn):
    cur = conn.cursor()
    ids = {}
    cur.execute(
        "SELECT name, id FROM _categories WHERE name IN "
        "('Addon Syrup','Addon Topping','Addon Powder','Addon Milk',"
        "'Addon Creamer','Addon Foam','Addon Extract','Addon Boba','Addon Sugar')"
    )
    for name, id_ in cur.fetchall():
        ids[f"cat_{name.lower().replace(' ','_')}"] = id_

    # Fallback
    if not ids:
        cur.execute("SELECT id FROM _categories LIMIT 1")
        row = cur.fetchone()
        if row: ids["cat_fallback"] = row[0]

    cur.execute("SELECT id FROM _taxes WHERE name='PPN 11%' LIMIT 1")
    row = cur.fetchone()
    ids["tax_ppn11"] = row[0] if row else None

    for unit_name, key in [("Botol","unit_botol"),("Sachet","unit_sachet"),
                            ("Gram","unit_gram"),("Karton","unit_karton"),("Pcs","unit_pcs")]:
        cur.execute("SELECT id FROM _units WHERE name=%s LIMIT 1", (unit_name,))
        row = cur.fetchone()
        ids[key] = row[0] if row else None

    # Final fallback unit
    if not any(ids.get(k) for k in ["unit_botol","unit_sachet","unit_gram","unit_karton"]):
        cur.execute("SELECT id FROM _units LIMIT 1")
        row = cur.fetchone()
        if row: ids["unit_fallback"] = row[0]

    cur.close()
    return ids

def get_unit_id(ptype_key, fk_ids):
    unit_map = {
        "syrup": "unit_botol", "topping_sauce": "unit_botol",
        "foam": "unit_botol", "extract_concentrate": "unit_botol",
        "powder_mix": "unit_sachet", "creamer": "unit_sachet",
        "infused_sugar": "unit_gram", "dried_topping": "unit_gram", "boba_topping": "unit_gram",
        "milk_nabati": "unit_karton",
    }
    key = unit_map.get(ptype_key, "unit_pcs")
    return fk_ids.get(key) or fk_ids.get("unit_pcs") or fk_ids.get("unit_fallback")

def get_cat_id(category_name, fk_ids):
    key = f"cat_{category_name.lower().replace(' ','_')}"
    return fk_ids.get(key) or fk_ids.get("cat_fallback")

def ensure_addon_categories(conn):
    cats = [
        ("Addon",         "addon",          "ADD", "Semua topping, syrup, dan bahan tambahan"),
        ("Addon Syrup",   "addon-syrup",    "SYR", "Syrup berbasis tanaman"),
        ("Addon Topping", "addon-topping",  "TOP", "Saus topping dan dried topping"),
        ("Addon Powder",  "addon-powder",   "PWD", "Powder mix berbasis tanaman"),
        ("Addon Milk",    "addon-milk",     "MLK", "Susu nabati plant-based"),
        ("Addon Creamer", "addon-creamer",  "CRM", "Creamer non-dairy"),
        ("Addon Foam",    "addon-foam",     "FOM", "Flavoured foam mix"),
        ("Addon Extract", "addon-extract",  "EXT", "Extract dan concentrate"),
        ("Addon Boba",    "addon-boba",     "BOB", "Boba dan jelly topping"),
        ("Addon Sugar",   "addon-sugar",    "SUG", "Infused sugar"),
    ]
    cur = conn.cursor()
    for name, slug, code, desc in cats:
        cur.execute("""
            INSERT INTO _categories (name, description, slug, code, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW(), NOW())
            ON CONFLICT (name) DO NOTHING
        """, (name, desc, slug, code))
    conn.commit()
    cur.close()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — ADDON GENERATOR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_all_addons(target_count):
    """
    Build complete product list from plant × type × variant combinations.
    Returns list of product dicts ready for DB insertion.
    """
    all_items = []

    # Build full combination pool
    pool = []
    for plant in PLANT_SOURCES:
        tier_bias = plant[8]  # T1/T2/T3
        rarity    = plant[5]
        for ptype in PRODUCT_TYPES:
            pool.append((plant, ptype, tier_bias, rarity))

    random.shuffle(pool)

    # Tier targets
    t1_target = int(target_count * 0.50)
    t2_target = int(target_count * 0.35)
    t3_target = target_count - t1_target - t2_target

    tier_pools = {"T1": [], "T2": [], "T3": []}
    for plant, ptype, tier_bias, rarity in pool:
        tier_pools[tier_bias].append((plant, ptype, rarity))

    # Pad if needed
    for tier in ["T1","T2","T3"]:
        while len(tier_pools[tier]) < {"T1":t1_target,"T2":t2_target,"T3":t3_target}[tier]:
            tier_pools[tier].extend(tier_pools[tier])

    targets = {"T1": t1_target, "T2": t2_target, "T3": t3_target}

    idx_global = 0
    for tier_code, t_target in targets.items():
        t_pool = tier_pools[tier_code]
        for i in range(t_target):
            combo_idx = i % len(t_pool)
            plant, ptype, rarity = t_pool[combo_idx]
            p_key, p_disp, p_en, p_origin, p_harvest, p_rarity, p_flavors, p_note, _ = plant

            cycle       = i // len(t_pool)
            cycle_sfx   = f" Mk.{cycle+1}" if cycle > 0 else ""
            season      = flavor_to_season(p_flavors)

            # Build variants
            variants = []
            for var_label, var_code, var_mult in ptype["variants"]:
                price_sell = compute_addon_price(ptype, tier_code, rarity, var_mult)
                price_buy  = int(price_sell * 0.55)
                sku        = make_addon_sku(p_key, ptype["key"], tier_code, var_code)
                variants.append({
                    "sku":        sku,
                    "size_weight": var_label + cycle_sfx,
                    "price_buy":  price_buy,
                    "price_sell": price_sell,
                    "var_label":  var_label,
                })

            # Product name uses first variant as anchor
            product_name = make_addon_name(p_disp, ptype["display"], ptype["variants"][0][0], tier_code)
            if cycle > 0:
                product_name = f"{product_name}{cycle_sfx}"

            barcode     = variants[0]["sku"] if variants else f"AD-{p_key[:6]}-{idx_global:06d}"
            description = make_addon_description(plant, ptype, tier_code, season)
            attrs       = make_addon_attrs(plant, ptype, tier_code, ptype["variants"][0][0], season, variants[0]["price_sell"])

            all_items.append({
                "barcode":       barcode,
                "name":          product_name[:254],
                "description":   description,
                "tier_code":     tier_code,
                "category":      ptype["category"],
                "unit_key":      ptype["key"],
                "has_expiry":    ptype["has_expiry"],
                "track_batch":   ptype["track_batch"],
                "min_stock":     ptype["min_stock"],
                "max_stock":     ptype["max_stock"],
                "variants":      variants,
                "attrs":         attrs,
            })
            idx_global += 1

    return all_items

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_pipeline(total_target, batch_size, skip_attrs, dry_run):
    print("═" * 65)
    print("  KAFE NUSANTARA — ADDON GENERATOR v1.0")
    print(f"  Target  : {total_target:,} addon products → PostgreSQL")
    print(f"  Sources : {len(PLANT_SOURCES)} plant sources × {len(PRODUCT_TYPES)} product types")
    print(f"  Natural : {len(PLANT_SOURCES) * len(PRODUCT_TYPES):,} base combinations")
    print("═" * 65)

    if dry_run:
        total_target = min(total_target, 30)
        print(f"  [DRY RUN] Preview {total_target} items")

    print(f"\n📡 Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}...")
    try:
        conn = get_connection(); print("  ✅ Connected")
    except Exception as e:
        print(f"  ❌ {e}"); sys.exit(1)

    ensure_addon_categories(conn)
    fk_ids = fetch_fk_ids(conn)
    print(f"  FK IDs: { {k:v for k,v in fk_ids.items() if v} }")

    t1 = int(total_target * 0.50)
    t2 = int(total_target * 0.35)
    t3 = total_target - t1 - t2
    print(f"\n📐 Distribution:")
    print(f"   T1 Everyday           : {t1:>6,}")
    print(f"   T2 Artisan            : {t2:>6,}")
    print(f"   T3 Rare & Exotic      : {t3:>6,}")
    print(f"   TOTAL                 : {total_target:>6,}")

    print(f"\n🌿 Generating {total_target:,} addon items...")
    all_items = generate_all_addons(total_target)
    print(f"   Generated {len(all_items):,} items in memory")

    if dry_run:
        print(f"\n📋 SAMPLE (10 items):")
        for item in all_items[:10]:
            v0 = item["variants"][0]
            print(f"   [{item['tier_code']}] {item['name'][:58]}")
            print(f"         SKU: {v0['sku']} | Rp {v0['price_sell']:,} | {item['category']}")
        return

    total_products = total_variants = total_attrs = 0
    start_time = time.time()
    now_str = datetime.now(timezone.utc)
    used_skus = set()

    for batch_start in range(0, len(all_items), batch_size):
        batch = all_items[batch_start : batch_start + batch_size]

        # ── Products ──────────────────────────────────────────────────────────
        barcodes         = [item["barcode"] for item in batch]
        existing_barcodes= fetch_existing_barcodes(conn, barcodes)
        new_items        = [item for item in batch if item["barcode"] not in existing_barcodes]

        barcode_to_pid = dict(existing_barcodes)

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
                [(
                    item["name"][:254],
                    item["description"][:490],
                    True,
                    item["has_expiry"],
                    item["track_batch"],
                    item["min_stock"],
                    item["max_stock"],
                    now_str, now_str,
                    get_cat_id(item["category"], fk_ids),
                    fk_ids.get("tax_ppn11"),
                    get_unit_id(item["unit_key"], fk_ids),
                    None,
                    item["barcode"],
                ) for item in new_items],
                page_size=200,
            )
            rows = cur.fetchall()
            conn.commit(); cur.close()
            barcode_to_pid.update({b: pid for pid, b in rows})
            total_products += len(rows)

        # ── Variants ──────────────────────────────────────────────────────────
        variant_rows = []
        for item in batch:
            pid = barcode_to_pid.get(item["barcode"])
            if not pid: continue
            for v in item["variants"]:
                if v["sku"] not in used_skus:
                    used_skus.add(v["sku"])
                    variant_rows.append((v["sku"], pid, v["size_weight"], v["price_buy"], v["price_sell"]))

        sku_to_vid = {}
        if variant_rows:
            existing_skus = fetch_existing_skus(conn, [r[0] for r in variant_rows])
            new_vrows = [r for r in variant_rows if r[0] not in existing_skus]
            sku_to_vid.update(existing_skus)

            if new_vrows:
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
                    [(sku, pid, sw, pb, ps, now_str) for sku, pid, sw, pb, ps in new_vrows],
                    page_size=500,
                )
                var_rows = cur.fetchall()
                conn.commit(); cur.close()
                sku_to_vid.update({sku: vid for vid, sku in var_rows})
                total_variants += len(var_rows)

        # ── Attribute Items ───────────────────────────────────────────────────
        if not skip_attrs:
            attr_rows = []
            batch_attr_keys = set()
            all_vids = list(sku_to_vid.values())
            existing_attr_keys = fetch_existing_attr_keys(conn, all_vids) if all_vids else set()

            for item in batch:
                first_sku = item["variants"][0]["sku"] if item["variants"] else None
                vid = sku_to_vid.get(first_sku) if first_sku else None
                if not vid: continue

                for attr_name, attr_val in item["attrs"].items():
                    norm_val, _ = normalize_attr_value(attr_val)
                    attr_key = (vid, attr_name, norm_val)
                    if attr_key in existing_attr_keys or attr_key in batch_attr_keys:
                        continue
                    batch_attr_keys.add(attr_key)
                    attr_rows.append((vid, attr_name, norm_val, now_str))

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
                    attr_rows, page_size=1000,
                )
                total_attrs += len(attr_rows)
                conn.commit(); cur.close()

        # ── Progress ──────────────────────────────────────────────────────────
        done = batch_start + len(batch)
        if done % SHOW_PROGRESS_EVERY == 0 or done >= len(all_items):
            elapsed = time.time() - start_time
            rate = total_products / max(elapsed, 0.01)
            print(f"   [{done:>5,}/{len(all_items):,}] "
                  f"Prod: {total_products:,} | Var: {total_variants:,} | "
                  f"Attr: {total_attrs:,} | {rate:.0f} prod/s")

    conn.close()
    elapsed = time.time() - start_time

    print()
    print("═" * 65)
    print("  📊 FINAL STATISTICS")
    print("═" * 65)
    for label, val in [
        ("Products inserted",       total_products),
        ("Variants inserted",       total_variants),
        ("Attribute items",         total_attrs),
        ("Total rows",              total_products + total_variants + total_attrs),
        ("Time",                    f"{elapsed:.1f}s ({elapsed/60:.1f} min)"),
    ]:
        print(f"  ✦ {label:<30} {val!s:>12}")
    print("═" * 65)
    print()
    print("  📋 SQL check:")
    print("     SELECT c.name, COUNT(p.id) FROM _categories c")
    print("     JOIN lumra_config_products p ON p.category_id=c.id")
    print("     WHERE c.name LIKE 'Addon%' GROUP BY c.name ORDER BY c.name;")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Kafe Nusantara — Addon Generator: syrup, topping, susu, dll."
    )
    parser.add_argument("--count",       type=int, default=TARGET_ADDONS,
                        help=f"Jumlah addon (default: {TARGET_ADDONS:,})")
    parser.add_argument("--batch-size",  type=int, default=BATCH_SIZE)
    parser.add_argument("--skip-attrs",  action="store_true")
    parser.add_argument("--dry-run",     action="store_true")
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
