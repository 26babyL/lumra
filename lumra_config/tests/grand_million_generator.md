"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  KAFE NUSANTARA — GRAND MILLION GENERATOR v2.0                             ║
║  999,999 Blends → Direct PostgreSQL via COPY                               ║
║                                                                              ║
║  Kenapa TIDAK pakai JSON 5GB:                                               ║
║  · JSON 5GB = tidak bisa dibuka di editor, lambat diparse                  ║
║  · Django bulk_create 15M records = 50 menit                               ║
║  · PostgreSQL COPY = 2.5 menit untuk hal yang sama                         ║
║                                                                              ║
║  Strategi:                                                                  ║
║  1. Generate data IN MEMORY per batch (tidak pernah >500MB RAM)            ║
║  2. Stream langsung ke PostgreSQL via psycopg2 copy_expert                 ║
║  3. 4 tabel diisi secara paralel dengan sequence yang benar                ║
║                                                                              ║
║  Output: 14,850,000 rows di 4 tabel PostgreSQL                             ║
║    · lumra_config_products        : 990,000 rows                           ║
║    · lumra_config_productvariants : 3,960,000 rows                         ║
║    · lumra_config_productattribute_items : 9,900,000 rows                  ║
║    · production_recipes           : 990,000 rows (opsional)                ║
║                                                                              ║
║  Estimasi waktu: 5-15 menit (tergantung hardware)                          ║
║                                                                              ║
║  Requirements:                                                              ║
║    pip install psycopg2-binary                                              ║
║                                                                              ║
║  Usage:                                                                     ║
║    python grand_million_generator.py                    # full 990k         ║
║    python grand_million_generator.py --count 100000     # custom count      ║
║    python grand_million_generator.py --dry-run          # test 1000 saja   ║
║    python grand_million_generator.py --skip-attrs       # skip attr_items  ║
║    python grand_million_generator.py --workers 4        # parallel writers ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import io
import random
import math
import time
import argparse
import sys
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ─── psycopg2 check ───────────────────────────────────────────────────────────
try:
    import psycopg2
    import psycopg2.extras
    import psycopg2.extensions
except ImportError:
    print("❌ psycopg2 tidak ditemukan.")
    print("   Install: pip install psycopg2-binary")
    sys.exit(1)

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_system.settings")
    from django.conf import settings as django_settings
    DJANGO_SETTINGS_AVAILABLE = True
except Exception:
    django_settings = None
    DJANGO_SETTINGS_AVAILABLE = False

random.seed(20240101)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG — SESUAIKAN DENGAN ENVIRONMENT KAMU
# ═══════════════════════════════════════════════════════════════════════════════

if DJANGO_SETTINGS_AVAILABLE:
    default_db = django_settings.DATABASES.get("default", {})
else:
    default_db = {}

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME",     default_db.get("NAME", "kafe_nusantara")),
    "user":     os.getenv("DB_USER",     default_db.get("USER", "nusantara_user")),
    "password": os.getenv("DB_PASSWORD", default_db.get("PASSWORD", "nusantara2024!")),
    "host":     os.getenv("DB_HOST",     default_db.get("HOST", "localhost")),
    "port":     os.getenv("DB_PORT",     default_db.get("PORT", "5432")),
}

TARGET_NEW_BLENDS = 990_000   # 999,999 total - 9,999 existing
BATCH_SIZE        = 5_000     # rows per COPY batch (tuned for memory)
SHOW_PROGRESS_EVERY = 10_000  # print progress setiap N blends

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MASTER BEAN DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

ORIGINS = [
    ("aceh_gayo",       "Aceh Gayo",          "Sumatera"),
    ("arjuno",          "Gunung Arjuno",       "Jawa"),
    ("bali_kintamani",  "Bali Kintamani",      "Bali"),
    ("bali_ulian",      "Bali Ulian",          "Bali"),
    ("bajawa",          "Flores Bajawa",       "Flores"),
    ("bengkulu",        "Bengkulu",            "Sumatera"),
    ("bukit_barisan",   "Bukit Barisan",       "Sumatera"),
    ("ciwidey",         "Java Ciwidey",        "Jawa"),
    ("dampit",          "Dampit Malang",       "Jawa"),
    ("dogiyai",         "Papua Dogiyai",       "Papua"),
    ("flores_manggarai","Flores Manggarai",    "Flores"),
    ("garut",           "Java Garut",          "Jawa"),
    ("gunung_halu",     "Gunung Halu",         "Jawa"),
    ("ijen_raung",      "Java Ijen Raung",     "Jawa"),
    ("kalosi",          "Toraja Kalosi",       "Sulawesi"),
    ("kayu_aro",        "Kerinci Kayu Aro",    "Sumatera"),
    ("lampung",         "Lampung Robusta",     "Sumatera"),
    ("lintong",         "Lintong",             "Sumatera"),
    ("mandheling",      "Mandheling",          "Sumatera"),
    ("manglayang",      "Java Manglayang",     "Jawa"),
    ("preanger",        "Java Preanger",       "Jawa"),
    ("puntang",         "Java Puntang",        "Jawa"),
    ("rinjani",         "Sembalun Rinjani",    "Lombok"),
    ("sapan",           "Toraja Sapan",        "Sulawesi"),
    ("semeru",          "Java Semeru",         "Jawa"),
    ("sidikalang",      "Sidikalang",          "Sumatera"),
    ("sindoro",         "Java Sindoro",        "Jawa"),
    ("solok_radjo",     "Solok Radjo",         "Sumatera"),
    ("temanggung",      "Java Temanggung",     "Jawa"),
    ("wamena",          "Papua Wamena",        "Papua"),
    ("wanoja_kamojang", "Wanoja Kamojang",     "Jawa"),
]

ROASTS    = ["Light", "Medium", "Dark"]
PROCESSES = ["Washed", "Natural", "Honey", "Semi-Washed", "Wet-Hulled", "Anaerobic", "Wine"]

# Build full bean list: (origin_key, display, island, roast, process)
BEANS = []
for orig_key, disp, island in ORIGINS:
    for roast in ROASTS:
        for proc in PROCESSES:
            BEANS.append((orig_key, disp, island, roast, proc))
BEAN_COUNT = len(BEANS)  # 651

# Pre-compute indices for fast random sampling
BEAN_INDICES = list(range(BEAN_COUNT))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — RARITY ENGINE (fast scalar version)
# ═══════════════════════════════════════════════════════════════════════════════

PROCESS_COMPLEXITY = {
    "Washed": 1, "Natural": 2, "Honey": 2, "Semi-Washed": 3,
    "Wet-Hulled": 3, "Anaerobic": 5, "Wine": 5,
}

EXOTIC_PAIRS = {
    frozenset(["Anaerobic","Wine"]): 10,       frozenset(["Anaerobic","Wet-Hulled"]): 9,
    frozenset(["Wine","Wet-Hulled"]): 9,       frozenset(["Anaerobic","Honey"]): 7,
    frozenset(["Wine","Natural"]): 7,          frozenset(["Anaerobic","Natural"]): 6,
    frozenset(["Wine","Semi-Washed"]): 6,      frozenset(["Wet-Hulled","Natural"]): 5,
}

RARE_ORIGINS = {"dogiyai", "wamena", "rinjani", "solok_radjo", "kayu_aro", "bajawa"}

def score_blend(selected_beans):
    """Fast complexity scoring. selected_beans: list of (orig, disp, island, roast, proc)"""
    n = len(selected_beans)
    origins   = [b[0] for b in selected_beans]
    displays  = [b[1] for b in selected_beans]
    islands   = {b[2] for b in selected_beans}
    roasts    = [b[3] for b in selected_beans]
    processes = [b[4] for b in selected_beans]
    types     = {"Robusta" if o in ("lampung","dampit") else "Arabica" for o in origins}

    score = 0
    # Bean count
    score += {2: 2, 3: 8, 4: 15}.get(n, 2)
    # Process complexity
    score += sum(PROCESS_COMPLEXITY.get(p, 1) for p in processes)
    # Exotic pair
    proc_set = frozenset(processes)
    for pair, bonus in EXOTIC_PAIRS.items():
        if pair.issubset(proc_set):
            score += bonus
            break
    # Cross-island
    ni = len(islands)
    score += 12 if ni >= 3 else (6 if ni == 2 else 0)
    # All-different processes
    if len(set(processes)) == n:
        score += 5
    # Cross-type Arabica+Robusta
    if len(types) > 1:
        score += 4
    # Light+Dark contrast
    if "Light" in roasts and "Dark" in roasts:
        score += 5
    # Papua origin
    if any(o in ("dogiyai","wamena") for o in origins):
        score += 6
    # Dual ferment
    if "Anaerobic" in processes and "Wine" in processes:
        score += 8

    return score

def tier_from_score(score):
    if score >= 40: return "T3"
    if score >= 20: return "T2"
    return "T1"

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CONTENT GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

SEASONS = ["Winter", "Summer", "Autumn", "Spring"]

SEASON_UNIVERSE = {
    "Winter": "The Dark Passage",
    "Summer": "The Open Horizon",
    "Autumn": "The Amber Descent",
    "Spring": "The First Ascent",
}

SEASON_ISLAND_BIAS = {
    "Sumatera": ["Winter","Autumn"],
    "Jawa":     ["Autumn","Spring"],
    "Bali":     ["Summer","Spring"],
    "Flores":   ["Summer","Autumn"],
    "Lombok":   ["Summer","Spring"],
    "Sulawesi": ["Winter","Autumn"],
    "Papua":    ["Winter","Summer"],
}

TIER_META = {
    "T1": {"name": "Tier 1 — The Vanguard",          "label": "Standard",        "emoji": "◆"},
    "T2": {"name": "Tier 2 — The Curator's Reserve",  "label": "Premium",         "emoji": "◈"},
    "T3": {"name": "Tier 3 — The Grand Artifact",     "label": "Mythic · Limited","emoji": "✦"},
}

# Pre-built name pools (will be extended with index to avoid collisions)
NAME_MODS = {
    "Winter": {
        "T1": ["Frozen","Midnight","Smoldering","Shadowed","Iron","Ashen","Ember","Hollow",
               "Veiled","Scorched","Muted","Buried","Charred","Ancient","Forgotten","Darkened",
               "Stormy","Shrouded","Bitter","Sealed","Windswept","Dimmed","Frosted","Heavy",
               "Silent","Rugged","Faded","Blanketed","Hushed","Cracked","Stark","Gloomy"],
        "T2": ["Obsidian","Clandestine","Sovereign","Arcane","Hallowed","Mythic","Forbidden",
               "Encrypted","Classified","Covert","Redacted","Uncharted"],
        "T3": ["Final","Obsidian","Primordial","Singular","Consecrated","Immutable","Abyssal"],
    },
    "Summer": {
        "T1": ["Sunda","Banda","Makassar","Malacca","Timor","Flores","Lombok","Bali","Celebes",
               "Molucca","Java","Borneo","Sulawesi","Ternate","Tidore","Ambon","Kupang","Manado",
               "Padang","Palembang","Demak","Gresik","Tuban","Banten","Aceh","Riau","Jambi",
               "Pontianak","Balikpapan","Sorong","Merauke","Wamena"],
        "T2": ["Admiral's","Captain's","Flagship","Imperial","Grand","Premier","Celestial",
               "Legendary","Sovereign","Mythic"],
        "T3": ["Primordial","Celestial","Singular","Immutable","Sacred"],
    },
    "Autumn": {
        "T1": ["Weathered","Tarnished","Worn","Antique","Aged","Patinated","Rusted","Battered",
               "Burnished","Timeworn","Cracked","Mended","Faded","Engraved","Gilded","Hammered",
               "Polished","Dented","Scarred","Handcrafted","Restored","Inherited","Storied",
               "Hardy","True","Field-worn","Trail-kept","Reliable","Well-used","Faithful"],
        "T2": ["Museum-Grade","Excavated","Preserved","Authenticated","Catalogued","Curated",
               "Hallowed","Antiquarian","Heritage-Class","One-of-a-Kind"],
        "T3": ["Primordial","Sacred","Immutable","Singular","Consecrated"],
    },
    "Spring": {
        "T1": ["First","Morning","Dawn","Early","Rising","Waking","Breaking","Opening","Nascent",
               "Fresh","Young","Gentle","Soft","Tender","Pale","Faint","Quiet","Still","Pure",
               "Wispy","Shifting","Drifting","Hovering","Climbing","Ascending","Blooming",
               "Stirring","Gathering","Nascent","Luminous","Dewy"],
        "T2": ["Inaugural","Pioneering","Trailblazing","Pathfinding","Groundbreaking",
               "Landmark","Defining","Formative","Pristine","Unspoiled"],
        "T3": ["Primordial","Elemental","Singular","Sacred","Immutable"],
    },
}

NAME_ANCHORS = {
    "Winter": {
        "T1": ["Bivouac","Shelter","Outpost","Refuge","Camp","Garrison","Waystation","Bastion",
               "Stronghold","Lodge","Barracks","Depot","Station","Passage","Encampment",
               "Redoubt","Rampart","Crossing","Threshold","Citadel","Alcove","Hollow",
               "Burrow","Den","Hearth","Keep","Vault","Sanctum","Watchtower","Fort"],
        "T2": ["Chronicle","Dispatch","Dossier","Registry","Compendium","Scroll","Parchment",
               "Folio","Atlas","Cipher","Codex","Ledger","Manifest","Annals","Tome"],
        "T3": ["Codex","Grimoire","Manuscript","Arcanum","Testament","Sigil","Relic","Cipher"],
    },
    "Summer": {
        "T1": ["Voyage","Current","Trade Wind","Meridian","Bearing","Transit","Passage","Wake",
               "Swell","Drift","Channel","Strait","Route","Course","Convoy","Fleet","Charter",
               "Cargo","Expedition","Crossing","Traverse","Approach","Anchorage","Heading",
               "Manifest","Run","Reach","Log","Watch","Bearing"],
        "T2": ["Galleon","Clipper","Brigantine","Frigate","Schooner","Carrack","Dhow","Junk",
               "Proa","Pinnace","Corvette","Bark","Ketch","Sloop","Cutter"],
        "T3": ["Armada","Flotilla","Convoy","Syndicate","Federation"],
    },
    "Autumn": {
        "T1": ["Compass","Sextant","Theodolite","Astrolabe","Barometer","Chronometer",
               "Altimeter","Clinometer","Transit","Protractor","Divider","Planimeter",
               "Odometer","Flask","Canteen","Lantern","Haversack","Rucksack","Penknife",
               "Awl","Chisel","Hammer","Ledger","Logbook","Field Notes","Survey Map","Awl"],
        "T2": ["Relic","Artifact","Heirloom","Specimen","Exhibit","Trophy","Keepsake",
               "Token","Signet","Medallion","Talisman","Amulet","Seal","Insignia"],
        "T3": ["Talisman","Amulet","Seal","Insignia","Emblem"],
    },
    "Spring": {
        "T1": ["Dew","Mist","Frost","Haze","Fog","Vapor","Cloud","Rime","Bloom","Blossom",
               "Pollen","Spore","Runoff","Snowmelt","Brook","Rivulet","Lichen","Moss",
               "Fern","Sprig","Tendril","Sunbreak","Wellspring","Headwater","Clearing",
               "Creek","Spring","Thaw","Drizzle","Shower"],
        "T2": ["Entry","Record","Account","Memoir","Testament","Dispatch","Notation",
               "Inscription","Discovery","Finding","Observation","Revelation"],
        "T3": ["Revelation","Disclosure","Venture","Initiative","Genesis"],
    },
}

TIER_PREFIX = {
    "T1": {"Winter": "",            "Summer": "",            "Autumn": "",        "Spring": ""},
    "T2": {"Winter": "Curator's",   "Summer": "Mariner's",   "Autumn": "Relic",   "Spring": "Pioneer's"},
    "T3": {"Winter": "Grand Artifact","Summer":"Grand Mariner","Autumn":"Grand Relic","Spring":"Grand Pioneer"},
}

def make_blend_name(season, tier_code, idx):
    """Generate blend name. Uses index as suffix to guarantee uniqueness."""
    mods    = NAME_MODS[season][tier_code]
    anchors = NAME_ANCHORS[season][tier_code]
    prefix  = TIER_PREFIX[tier_code][season]

    mod    = mods[idx % len(mods)]
    anchor = anchors[(idx // len(mods)) % len(anchors)]

    # Rotate suffix for extra uniqueness at large scales
    rotation = idx // (len(mods) * len(anchors))
    suffix = f" {rotation}" if rotation > 0 else ""

    if prefix:
        return f"{prefix} {mod} {anchor}{suffix}"
    return f"{mod} {anchor}{suffix}"

FLAVOR_DEFAULTS = {
    ("Washed",    "Light"):  ["citrus","jasmine","peach","lemon zest"],
    ("Washed",    "Medium"): ["brown sugar","hazelnut","almond","milk chocolate"],
    ("Washed",    "Dark"):   ["dark chocolate","molasses","smoky caramel"],
    ("Natural",   "Light"):  ["blueberry","strawberry","tropical fruit","hibiscus"],
    ("Natural",   "Medium"): ["dark chocolate","berry jam","dried fig","molasses"],
    ("Natural",   "Dark"):   ["dark berry","espresso","tar","charcoal"],
    ("Honey",     "Light"):  ["apricot","honeysuckle","white grape","floral"],
    ("Honey",     "Medium"): ["honey","toffee","dried apricot","maple syrup"],
    ("Honey",     "Dark"):   ["burnt caramel","toffee","smoked almond"],
    ("Semi-Washed","Light"): ["mandarin","oolong tea","light caramel","papaya"],
    ("Semi-Washed","Medium"):["milk caramel","vanilla","roasted nut","apricot"],
    ("Semi-Washed","Dark"):  ["roasted grain","dark caramel","walnut","intense spice"],
    ("Wet-Hulled","Light"):  ["herb","cedar","tobacco leaf","lime","green pepper"],
    ("Wet-Hulled","Medium"): ["earthy","tobacco","spice","woody","leather"],
    ("Wet-Hulled","Dark"):   ["peat","bark","dark tobacco","clove","intense earth"],
    ("Anaerobic", "Light"):  ["passion fruit","lychee","raspberry","rum raisin","cola"],
    ("Anaerobic", "Medium"): ["fermented fruit","tropical punch","cacao nib","tamarind"],
    ("Anaerobic", "Dark"):   ["black cherry","smoke","dark rum","fermented cocoa"],
    ("Wine",      "Light"):  ["wine","blackcurrant","dark cherry","grape must","plum"],
    ("Wine",      "Medium"): ["port wine","dark plum","roasted grape","balsamic"],
    ("Wine",      "Dark"):   ["aged wine","tobacco","dark espresso","smoked plum"],
}

def get_notes(process, roast):
    return FLAVOR_DEFAULTS.get((process, roast), ["balanced","smooth","complex","rich"])

WHEEL_KEYWORDS = {
    "Fruity":     ["fruit","berry","citrus","plum","fig","apricot","peach","watermelon","lychee","passion","tropical","lemon"],
    "Sweet":      ["caramel","honey","toffee","molasses","sugar","maple","vanilla"],
    "Nutty":      ["nut","almond","hazelnut","walnut","macadamia"],
    "Chocolatey": ["chocolate","cocoa","cacao","mocha"],
    "Spicy":      ["spice","cinnamon","clove","pepper","nutmeg","rum"],
    "Floral":     ["floral","jasmine","rose","lavender","chamomile","honeysuckle","bloom"],
    "Earthy":     ["earthy","mushroom","wood","woody","peat","bark","herb","cedar","tobacco"],
    "Roasted":    ["smoke","roast","charcoal","espresso","tar","dark roast","intense"],
    "Fermented":  ["wine","rum","aged","ferment","balsamic","licorice","raisin","cola"],
}

def notes_to_wheel(notes_list):
    text = " ".join(notes_list).lower()
    scores = {k: sum(1 for kw in kws if kw in text) for k, kws in WHEEL_KEYWORDS.items()}
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = [k for k, v in top[:3] if v > 0]
    return ", ".join(result) if result else "Nutty, Chocolatey"

DESSERT_MAP = {
    "Chocolatey": ["Chocolate Lava Cake","Dark Brownies","Tiramisu"],
    "Nutty":      ["Almond Croissant","Hazelnut Tart","Tiramisu"],
    "Fruity":     ["Fruit Tart","Berry Cheesecake","Pavlova"],
    "Spicy":      ["Cinnamon Roll","Carrot Cake","Speculaas"],
    "Earthy":     ["Tiramisu","Matcha Cake","Panna Cotta"],
    "Floral":     ["French Macarons","Earl Grey Cake","Rose Tart"],
    "Sweet":      ["Crème Brûlée","Honey Toast","Flan"],
    "Roasted":    ["Espresso Brownies","Mocha Layer Cake","Tiramisu"],
    "Fermented":  ["Dark Chocolate Truffles","Rum Cake","Aged Cheese Tart"],
}

def wheel_to_dessert(wheel_str):
    wheels = [w.strip() for w in wheel_str.split(",")]
    seen, out = set(), []
    for w in wheels:
        for d in DESSERT_MAP.get(w, []):
            if d not in seen:
                seen.add(d); out.append(d)
            if len(out) >= 2:
                return ", ".join(out)
    return "Tiramisu, Dark Brownies"

PROCESS_BREW = {
    "Washed":     "V60 · Pour Over",      "Natural": "AeroPress · French Press",
    "Honey":      "V60 · AeroPress",      "Semi-Washed": "French Press · AeroPress",
    "Wet-Hulled": "French Press · Moka Pot", "Anaerobic": "AeroPress · Espresso",
    "Wine":       "AeroPress · Ristretto",
}

# Pricing tables
PRICE_BASE = {
    (2,"T1"):45_000, (2,"T2"):75_000,  (2,"T3"):135_000,
    (3,"T1"):55_000, (3,"T2"):95_000,  (3,"T3"):195_000,
    (4,"T1"):65_000, (4,"T2"):120_000, (4,"T3"):275_000,
}
PROCESS_MULT = {"Washed":1.0,"Natural":1.15,"Honey":1.12,"Semi-Washed":1.1,
                "Wet-Hulled":1.08,"Anaerobic":1.45,"Wine":1.5}
ORIGIN_MULT  = {"dogiyai":1.35,"wamena":1.35,"rinjani":1.25,"solok_radjo":1.2,
                "kayu_aro":1.18,"bali_kintamani":1.15,"bajawa":1.15}
SIZE_MULT    = {"100g":1.0,"200g":1.85,"500g":4.20,"1kg":7.80}

def compute_price(selected_beans, tier_code, score):
    n = len(selected_beans)
    base = PRICE_BASE.get((n, tier_code), 65_000)
    proc_mult = max(PROCESS_MULT.get(b[4], 1.0) for b in selected_beans)
    orig_mult = 1.0
    pcts = weighted_pcts(n)
    for b, pct in zip(selected_beans, pcts):
        orig_mult += (ORIGIN_MULT.get(b[0], 1.0) - 1.0) * (pct / 100)
    score_bonus = 1.0 + (max(score - 20, 0) / 200)
    p100 = int(base * proc_mult * orig_mult * score_bonus)
    p100 = max(round(p100 / 5000) * 5000, 35_000)
    return {s: int(p100 * m) for s, m in SIZE_MULT.items()}, p100

def weighted_pcts(n):
    if n == 2:
        a = random.choice([40,45,50,55,60,65,70]); return [a, 100-a]
    if n == 3:
        return random.choice([[50,30,20],[60,25,15],[40,35,25],[45,35,20],[55,30,15]])
    return random.choice([[40,25,20,15],[35,30,20,15],[50,20,15,15]])

# SKU counter
_sku_counters = {"T1": 0, "T2": 0, "T3": 0}
_season_codes = {"Winter":"WIN","Summer":"SUM","Autumn":"AUT","Spring":"SPR"}

def make_sku(season, tier_code):
    _sku_counters[tier_code] += 1
    return f"HB-{_season_codes[season]}-{tier_code}-{_sku_counters[tier_code]:06d}"

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DATABASE LAYER
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
    cur.execute(
        """
        SELECT id, barcode
        FROM lumra_config_products
        WHERE barcode = ANY(%s)
        """,
        (barcodes,),
    )
    rows = cur.fetchall()
    cur.close()
    return {barcode: product_id for product_id, barcode in rows}


def fetch_existing_variants_by_skus(conn, skus):
    if not skus:
        return {}
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, sku
        FROM lumra_config_productvariants
        WHERE sku = ANY(%s)
        """,
        (skus,),
    )
    rows = cur.fetchall()
    cur.close()
    return {sku: variant_id for variant_id, sku in rows}


def fetch_existing_attr_keys(conn, variant_ids):
    if not variant_ids:
        return set()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT variant_id, attr_name, attr_value
        FROM lumra_config_productattribute_items
        WHERE variant_id = ANY(%s)
        """,
        (variant_ids,),
    )
    rows = cur.fetchall()
    cur.close()
    return set(rows)

def fetch_fk_ids(conn):
    """Fetch all FK IDs needed for insert."""
    cur = conn.cursor()
    ids = {}

    # Category IDs
    cur.execute("SELECT name, id FROM _categories WHERE name IN ('House Blend','Single Origin')")
    for name, id_ in cur.fetchall():
        ids[f"cat_{name.lower().replace(' ','_')}"] = id_

    # Tax ID
    cur.execute("SELECT id FROM _taxes WHERE name = 'PPN 11%' LIMIT 1")
    row = cur.fetchone()
    ids["tax_ppn11"] = row[0] if row else None

    # Unit ID
    cur.execute("SELECT id FROM _units WHERE name = 'Gram' LIMIT 1")
    row = cur.fetchone()
    ids["unit_gram"] = row[0] if row else None

    # Recipe category ID (optional)
    try:
        cur.execute("SELECT id FROM production_recipe_categories WHERE name = 'House Blend' LIMIT 1")
        row = cur.fetchone()
        ids["recipe_cat"] = row[0] if row else None
    except Exception:
        ids["recipe_cat"] = None

    cur.close()
    return ids

def ensure_recipe_category(conn):
    """Pastikan recipe category ada."""
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO production_recipe_categories (name, description, is_active, created_at, updated_at)
            VALUES ('House Blend', 'Production recipes untuk semua house blend', TRUE, NOW(), NOW())
            ON CONFLICT (name) DO NOTHING
            RETURNING id
        """)
        conn.commit()
        cur.execute("SELECT id FROM production_recipe_categories WHERE name='House Blend'")
        row = cur.fetchone()
        cur.close()
        return row[0] if row else None
    except Exception:
        conn.rollback()
        return None

def get_next_sequences(conn, table_col_map):
    """Get current max IDs to avoid conflicts."""
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

def copy_to_table(conn, table, columns, rows_iter):
    """Stream rows into PostgreSQL via COPY. rows_iter: iterable of tuples."""
    buf = io.StringIO()
    count = 0
    cur = conn.cursor()

    for row in rows_iter:
        # Escape tabs and newlines in text fields
        escaped = []
        for v in row:
            if v is None:
                escaped.append("\\N")
            else:
                s = str(v).replace("\\","\\\\").replace("\t","\\t").replace("\n","\\n").replace("\r","\\r")
                escaped.append(s)
        buf.write("\t".join(escaped) + "\n")
        count += 1

    buf.seek(0)
    cur.copy_expert(
        f"COPY {table} ({', '.join(columns)}) FROM STDIN WITH (FORMAT TEXT, NULL '\\N')",
        buf
    )
    conn.commit()
    cur.close()
    return count

def bulk_insert_products(conn, product_rows, fk_ids):
    """
    product_rows: list of dicts with blend data
    Table: lumra_config_products
    """
    COLS = ["name","description","is_active","has_expiry","track_batch",
            "min_stock","max_stock","created_at","updated_at",
            "category_id","tax_id","unit_id","vendor_id","barcode"]

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")
    cat_id  = fk_ids.get("cat_house_blend") or fk_ids.get("cat_single_origin")
    tax_id  = fk_ids.get("tax_ppn11")
    unit_id = fk_ids.get("unit_gram")

    def rows_gen():
        for p in product_rows:
            yield (
                p["name"],
                p["description"][:500],   # truncate for safety
                True,
                False,
                True,
                "0",                        # min_stock
                "9999",                     # max_stock
                now_str,
                now_str,
                cat_id,
                tax_id,
                unit_id,
                None,                       # vendor_id
                p["barcode"],
            )

    return copy_to_table(conn, "lumra_config_products", COLS, rows_gen())

def bulk_insert_variants(conn, variant_rows):
    """
    variant_rows: list of (sku, product_id, size_weight, price_buy, price_sell)
    """
    COLS = ["sku","product_id","size_weight","price_buy","price_sell","updated_at"]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")

    def rows_gen():
        for sku, pid, size, pbuy, psell in variant_rows:
            yield (sku, pid, size, str(pbuy), str(psell), now_str)

    return copy_to_table(conn, "lumra_config_productvariants", COLS, rows_gen())

def bulk_insert_attrs(conn, attr_rows):
    """
    attr_rows: list of (variant_id, attr_name, attr_value)
    """
    COLS = ["variant_id","attr_name","attr_value","updated_at"]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")

    def rows_gen():
        for vid, aname, aval in attr_rows:
            yield (vid, aname, str(aval)[:500], now_str)

    return copy_to_table(conn, "lumra_config_productattribute_items", COLS, rows_gen())

def bulk_insert_recipes(conn, recipe_rows, fk_ids):
    """
    recipe_rows: list of (name, description, instructions, product_id)
    """
    COLS = ["name","description","instructions","yield_quantity","preparation_time",
            "total_cost","cost_per_unit","is_archived","created_at","updated_at",
            "category_id","yield_unit_id"]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")
    cat_id  = fk_ids.get("recipe_cat")

    def rows_gen():
        for name, desc, instr, total_cost in recipe_rows:
            yield (
                name[:255],
                desc[:500],
                instr[:2000],
                "1",           # yield_quantity
                "5",           # preparation_time minutes
                str(total_cost),
                str(total_cost),
                False,
                now_str,
                now_str,
                cat_id,
                fk_ids.get("unit_gram"),
            )

    return copy_to_table(conn, "production_recipes", COLS, rows_gen())

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — BLEND GENERATOR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_blend(tier_code, idx_in_tier):
    """Generate one blend. Returns dict with all fields."""

    # Bean count bias per tier
    n_map = {"T1": [2,2,3], "T2": [2,3,3,4], "T3": [3,3,4,4]}
    n = random.choice(n_map[tier_code])

    # Sample beans without replacement
    selected_indices = random.sample(BEAN_INDICES, n)
    selected_beans   = [BEANS[i] for i in selected_indices]

    # Score
    score = score_blend(selected_beans)

    # Determine season from dominant island
    islands = [b[2] for b in selected_beans]
    dom_island = max(set(islands), key=islands.count)
    season = random.choice(SEASON_ISLAND_BIAS.get(dom_island, ["Autumn","Winter"]))

    # Build content
    pcts = weighted_pcts(n)
    all_notes = []
    for b in selected_beans:
        notes = get_notes(b[4], b[3])
        all_notes.extend(notes[:2])
    # dedupe notes
    seen_n, uniq_notes = set(), []
    for n_ in all_notes:
        if n_.lower() not in seen_n:
            seen_n.add(n_.lower()); uniq_notes.append(n_)
    tasting_notes = ", ".join(uniq_notes[:5])

    wheel   = notes_to_wheel(uniq_notes)
    dessert = wheel_to_dessert(wheel)
    prices, p100 = compute_price(selected_beans, tier_code, score)

    # Dominant roast
    roast_score = {"Light":1,"Medium":2,"Dark":3}
    w = sum(roast_score.get(b[3],2)*pct for b,pct in zip(selected_beans,pcts))
    avg_r = w / sum(pcts)
    dom_roast = "Light" if avg_r<1.7 else ("Dark" if avg_r>=2.5 else "Medium")

    # Name & SKU
    name  = make_blend_name(season, tier_code, idx_in_tier)
    sku   = make_sku(season, tier_code)

    # Resep
    resep_parts = []
    for b, pct in zip(selected_beans, pcts):
        gram = int(1000*pct/100)
        resep_parts.append(f"{b[1]} ({b[3]}/{b[4]}): {gram}g ({pct}%)")
    resep_parts.append("total: 1000g")
    resep = " | ".join(resep_parts)

    # Brew method
    main_proc = selected_beans[0][4]
    brew = PROCESS_BREW.get(main_proc, "AeroPress · V60")
    if tier_code == "T3":
        brew = "Cupping · AeroPress · Ristretto"

    # Description (compact — no random.choice for speed)
    tier_m = TIER_META[tier_code]
    su     = SEASON_UNIVERSE[season]
    origin_str = " + ".join(b[1] for b in selected_beans[:2])
    if tier_code == "T3":
        desc = (
            f"Blend {n} biji dari {len({b[2] for b in selected_beans})} pulau berbeda. "
            f"{resep[:100]}. Complexity score: {score}/100. "
            f"Salah satu dari 0.0133% kombinasi yang dipilih dari 7 miliar kemungkinan. "
            f"Tersedia 50 cup/bulan seluruh jaringan. — {su} Collection."
        )
    elif tier_code == "T2":
        proc_str = " × ".join({b[4] for b in selected_beans})
        desc = (
            f"Blend presisi dari {origin_str}, diproses dengan {proc_str}. "
            f"Profil rasa {tasting_notes[:80]}. Complexity score: {score}/100. "
            f"— {su} · {season} Collection."
        )
    else:
        desc = (
            f"Blend dari {origin_str}. "
            f"Profil rasa {tasting_notes[:80]}. "
            f"— {su} · {season} Collection."
        )

    return {
        "name":          name,
        "sku_base":      sku,
        "description":   desc,
        "barcode":       sku,
        "season":        season,
        "season_universe": su,
        "tier_code":     tier_code,
        "tier_name":     tier_m["name"],
        "tier_label":    tier_m["label"],
        "complexity_score": score,
        "n_beans":       n,
        "origin_1":      selected_beans[0][1] if n>0 else "",
        "origin_2":      selected_beans[1][1] if n>1 else "",
        "origin_3":      selected_beans[2][1] if n>2 else "",
        "origin_4":      selected_beans[3][1] if n>3 else "",
        "dominant_roast":dom_roast,
        "resep_gramasi": resep,
        "brew_method":   brew,
        "tasting_notes": tasting_notes,
        "flavour_wheel": wheel,
        "dessert":       dessert,
        "texture":       {"Light":"Silky & Clean","Medium":"Smooth & Balanced","Dark":"Bold & Heavy"}[dom_roast],
        "body":          round(sum({"Light":4,"Medium":6,"Dark":8}.get(b[3],6)*p/100 for b,p in zip(selected_beans,pcts))),
        "acidity":       round(sum({"Light":7,"Medium":5,"Dark":3}.get(b[3],5)*p/100 for b,p in zip(selected_beans,pcts))),
        "sweetness":     round(sum({"Natural":7,"Honey":6,"Wine":6,"Anaerobic":5,"Washed":4,"Semi-Washed":5,"Wet-Hulled":4}.get(b[4],5)*p/100 for b,p in zip(selected_beans,pcts))),
        "price_100g":    prices["100g"],
        "price_200g":    prices["200g"],
        "price_500g":    prices["500g"],
        "price_1kg":     prices["1kg"],
        "is_market_price": (tier_code=="T3" and score>=60),
        "monthly_limit": 50 if tier_code=="T3" else None,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

SIZES = ["100g","200g","500g","1kg"]

ATTRS_TEMPLATE = [
    "season","season_universe","rarity_tier","rarity_label","complexity_score",
    "tasting_notes","texture_profile","flavour_wheel","body","acidity","sweetness",
    "brew_method","is_market_price","monthly_limit","copy_packaging","copy_social",
    "origin_1","origin_2","origin_3","origin_4","dominant_roast","resep_gramasi",
]

def run_pipeline(total_new, batch_size, skip_attrs, skip_recipes, dry_run):
    print("═" * 65)
    print("  KAFE NUSANTARA — GRAND MILLION GENERATOR v2.0")
    print(f"  Target: {total_new:,} new blends → PostgreSQL COPY")
    print("═" * 65)

    if dry_run:
        total_new = min(total_new, 1000)
        print(f"  [DRY RUN] Generating {total_new:,} blends only (no DB write)")

    # Connect
    print(f"\n📡 Connecting to PostgreSQL ({DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']})...")
    try:
        conn = get_connection()
        print("  ✅ Connected")
    except Exception as e:
        print(f"  ❌ {e}")
        sys.exit(1)

    # Fetch FK IDs
    fk_ids = fetch_fk_ids(conn)
    print(f"  FK IDs: {fk_ids}")
    if not fk_ids.get("cat_house_blend"):
        print("  ❌ Category 'House Blend' tidak ditemukan!")
        print("     Jalankan: python manage.py seed_nusantara --only master")
        sys.exit(1)

    if not skip_recipes:
        fk_ids["recipe_cat"] = ensure_recipe_category(conn)

    # Current max IDs
    seqs = get_next_sequences(conn, {
        "lumra_config_products": "id",
        "lumra_config_productvariants": "id",
        "lumra_config_productattribute_items": "id",
    })
    print(f"  Current max product ID   : {seqs['lumra_config_products']:,}")
    print(f"  Current max variant ID   : {seqs['lumra_config_productvariants']:,}")

    # Tier distribution
    t1_count = int(total_new * 0.60)
    t2_count = int(total_new * 0.30)
    t3_count = total_new - t1_count - t2_count
    tier_plan = [("T1", t1_count), ("T2", t2_count), ("T3", t3_count)]

    print(f"\n📐 Blend Distribution Plan:")
    for tc, cnt in tier_plan:
        print(f"   {TIER_META[tc]['name']:<40} {cnt:>8,}")
    print(f"   {'TOTAL':<40} {total_new:>8,}")
    print()

    # Stats
    total_products_inserted = 0
    total_variants_inserted = 0
    total_attrs_inserted    = 0
    total_recipes_inserted  = 0
    used_names = set()
    start_time = time.time()

    for tier_code, tier_total in tier_plan:
        print(f"\n🔄 Generating {tier_total:,} × {TIER_META[tier_code]['name']}...")
        tier_start = time.time()
        tier_done  = 0

        # Process in batches
        batch_idx = 0
        while tier_done < tier_total:
            current_batch_size = min(batch_size, tier_total - tier_done)

            # ── Generate blends ──────────────────────────────────────────────
            blends_batch = []
            for i in range(current_batch_size):
                b = generate_blend(tier_code, tier_done + i)
                # Ensure unique name
                base_name = b["name"]
                if base_name in used_names:
                    b["name"] = f"{base_name} #{tier_done+i}"
                used_names.add(b["name"])
                blends_batch.append(b)

            if dry_run:
                tier_done += current_batch_size
                total_products_inserted += current_batch_size
                if tier_done % SHOW_PROGRESS_EVERY == 0 or tier_done >= tier_total:
                    elapsed = time.time() - start_time
                    rate = (total_products_inserted) / max(elapsed, 0.01)
                    print(f"   [{tier_code}] {tier_done:>8,}/{tier_total:,} | {rate:,.0f} blend/s | DRY RUN")
                continue

            # ── Insert products ──────────────────────────────────────────────
            product_data = [{"name": b["name"], "description": b["description"], "barcode": b["barcode"]}
                            for b in blends_batch]

            # Use execute_values for products (need RETURNING id)
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
                    (p["name"], p["description"][:500], True, False, True,
                     0, 9999, datetime.now(timezone.utc), datetime.now(timezone.utc),
                     fk_ids.get("cat_house_blend"),
                     fk_ids.get("tax_ppn11"),
                     fk_ids.get("unit_gram"),
                     None, p["barcode"])
                    for p in product_data
                ],
                page_size=500
            )
            returning = cur.fetchall()
            conn.commit()
            cur.close()

            # Map barcode → product_id, termasuk produk yang sudah ada.
            batch_barcodes = [p["barcode"] for p in product_data]
            barcode_to_pid = fetch_existing_products_by_barcodes(conn, batch_barcodes)
            products_in_batch = len(returning)
            total_products_inserted += products_in_batch

            # ── Insert variants ──────────────────────────────────────────────
            variant_rows = []
            for b in blends_batch:
                pid = barcode_to_pid.get(b["barcode"])
                if not pid:
                    continue
                for size in SIZES:
                    price_key = f"price_{size.replace('kg','1kg').replace('100g','100g')}"
                    # normalize key
                    pk = "price_" + size
                    psell = b.get(pk, 35_000)
                    pbuy  = int(psell * 0.65)
                    sku   = f"{b['sku_base']}-{size.upper().replace('KG','KG').replace('G','G')}"
                    # cleaner SKU format
                    sku   = f"{b['sku_base']}-{size}"
                    variant_rows.append((sku, pid, size, pbuy, psell))

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
                [(sku, pid, size, pbuy, psell, datetime.now(timezone.utc))
                 for sku, pid, size, pbuy, psell in variant_rows],
                page_size=1000
            )
            var_returning = cur.fetchall()
            conn.commit()
            cur.close()

            # Map SKU → variant_id, termasuk variant yang sudah ada.
            batch_skus = [sku for sku, _, _, _, _ in variant_rows]
            sku_to_vid = fetch_existing_variants_by_skus(conn, batch_skus)
            total_variants_inserted += len(var_returning)

            # ── Insert attribute items ───────────────────────────────────────
            if not skip_attrs:
                existing_attr_keys = fetch_existing_attr_keys(conn, list(sku_to_vid.values()))
                attr_rows = []
                batch_attr_keys = set()
                truncated_attr_count = 0
                for b in blends_batch:
                    # Find 100g variant id
                    sku_100g = f"{b['sku_base']}-100g"
                    vid = sku_to_vid.get(sku_100g)
                    if not vid:
                        continue

                    now_str = datetime.now(timezone.utc)
                    attrs = {
                        "season":            b["season"],
                        "season_universe":   b["season_universe"],
                        "rarity_tier":       b["tier_name"],
                        "rarity_label":      b["tier_label"],
                        "complexity_score":  str(b["complexity_score"]),
                        "tasting_notes":     b["tasting_notes"],
                        "texture_profile":   b["texture"],
                        "flavour_wheel":     b["flavour_wheel"],
                        "body":              str(b["body"]),
                        "acidity":           str(b["acidity"]),
                        "sweetness":         str(b["sweetness"]),
                        "brew_method":       b["brew_method"],
                        "is_market_price":   str(b["is_market_price"]),
                        "monthly_limit":     str(b["monthly_limit"]) if b["monthly_limit"] else "unlimited",
                        "origin_1":          b["origin_1"],
                        "origin_2":          b["origin_2"],
                        "origin_3":          b["origin_3"],
                        "dominant_roast":    b["dominant_roast"],
                        "recommended_dessert": b["dessert"],
                    }
                    for attr_name, attr_val in attrs.items():
                        normalized_attr_val, was_truncated = normalize_attr_value(attr_val)
                        attr_key = (vid, attr_name, normalized_attr_val)
                        if attr_key in existing_attr_keys or attr_key in batch_attr_keys:
                            continue
                        if was_truncated:
                            truncated_attr_count += 1
                        batch_attr_keys.add(attr_key)
                        attr_rows.append((vid, attr_name, normalized_attr_val, now_str))

                if attr_rows:
                    cur = conn.cursor()
                    psycopg2.extras.execute_values(
                        cur,
                        """
                        INSERT INTO lumra_config_productattribute_items
                            (variant_id, attr_name, attr_value, updated_at)
                        VALUES %s
                        """,
                        attr_rows,
                        page_size=2000
                    )
                    total_attrs_inserted += len(attr_rows)
                    conn.commit()
                    cur.close()
                    if truncated_attr_count:
                        print(f"     [WARN] Attr truncated in batch: {truncated_attr_count:,}")

            # ── Insert recipes ───────────────────────────────────────────────
            if not skip_recipes and fk_ids.get("recipe_cat"):
                recipe_rows = []
                for b in blends_batch:
                    recipe_rows.append((
                        b["name"][:255],
                        b["description"][:500],
                        b["resep_gramasi"][:1000],
                        b["price_100g"] * 0.6  # estimated total_cost
                    ))
                if recipe_rows:
                    try:
                        cur = conn.cursor()
                        psycopg2.extras.execute_values(
                            cur,
                            """
                            INSERT INTO production_recipes
                                (name, description, instructions, yield_quantity,
                                 preparation_time, total_cost, cost_per_unit,
                                 is_archived, created_at, updated_at,
                                 category_id, yield_unit_id)
                            VALUES %s
                            ON CONFLICT (name) DO NOTHING
                            """,
                            [(r[0], r[1][:500], r[2][:2000], 1, 5,
                              r[3], r[3], False,
                              datetime.now(timezone.utc), datetime.now(timezone.utc),
                              fk_ids.get("recipe_cat"), fk_ids.get("unit_gram"))
                             for r in recipe_rows],
                            page_size=500
                        )
                        total_recipes_inserted += cur.rowcount
                        conn.commit()
                        cur.close()
                    except Exception:
                        conn.rollback()

            # ── Progress ─────────────────────────────────────────────────────
            tier_done  += current_batch_size
            batch_idx  += 1
            elapsed     = time.time() - start_time
            tier_elapsed= time.time() - tier_start
            rate        = total_products_inserted / max(elapsed, 0.01)
            eta_sec     = (total_new - total_products_inserted) / max(rate, 1)

            if tier_done % SHOW_PROGRESS_EVERY == 0 or tier_done >= tier_total:
                eta_str = str(timedelta(seconds=int(eta_sec)))
                print(
                    f"   [{tier_code}] {tier_done:>8,}/{tier_total:,} | "
                    f"Total: {total_products_inserted:>8,} | "
                    f"{rate:,.0f} blend/s | ETA: {eta_str}"
                )

        tier_elapsed = time.time() - tier_start
        print(f"   ✅ {tier_code} done in {tier_elapsed:.1f}s")

    # ── Final stats ────────────────────────────────────────────────────────────
    conn.close()
    total_elapsed = time.time() - start_time

    print()
    print("═" * 65)
    print("  📊 FINAL STATISTICS")
    print("═" * 65)
    stats = [
        ("Products inserted",        total_products_inserted),
        ("Variants inserted",         total_variants_inserted),
        ("Attribute items inserted",  total_attrs_inserted),
        ("Recipes inserted",          total_recipes_inserted),
        ("Total rows",                total_products_inserted + total_variants_inserted +
                                      total_attrs_inserted + total_recipes_inserted),
        ("Time elapsed",              f"{total_elapsed:.1f}s ({total_elapsed/60:.1f} min)"),
        ("Throughput",                f"{total_products_inserted/max(total_elapsed,1):,.0f} blend/s"),
    ]
    for label, val in stats:
        print(f"  ✦ {label:<35} {val!s:>15}")
    print("═" * 65)

    if not dry_run:
        print()
        print("  💡 Verifikasi dengan:")
        print("     python nusantara_pg_setup.py --verify")
        print("     python nusantara_pg_setup.py --sample")
        print()
        print("  📋 SQL quick check:")
        print("     SELECT COUNT(*) FROM lumra_config_products WHERE category_id IN")
        print("       (SELECT id FROM _categories WHERE name='House Blend');")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Kafe Nusantara — Grand Million Generator: 999,999 blends ke PostgreSQL"
    )
    parser.add_argument("--count",        type=int,  default=TARGET_NEW_BLENDS,
                        help=f"Jumlah blend baru (default: {TARGET_NEW_BLENDS:,})")
    parser.add_argument("--batch-size",   type=int,  default=BATCH_SIZE,
                        help=f"Batch size per commit (default: {BATCH_SIZE:,})")
    parser.add_argument("--skip-attrs",   action="store_true",
                        help="Skip insert ke productattribute_items (lebih cepat)")
    parser.add_argument("--skip-recipes", action="store_true",
                        help="Skip insert ke production_recipes")
    parser.add_argument("--dry-run",      action="store_true",
                        help="Generate 1,000 blend tanpa insert ke DB")
    parser.add_argument("--db-name",      type=str, default=None)
    parser.add_argument("--db-user",      type=str, default=None)
    parser.add_argument("--db-password",  type=str, default=None)
    parser.add_argument("--db-host",      type=str, default=None)
    parser.add_argument("--db-port",      type=str, default=None)

    args = parser.parse_args()

    # Override DB config from args
    if args.db_name:     DB_CONFIG["dbname"]   = args.db_name
    if args.db_user:     DB_CONFIG["user"]      = args.db_user
    if args.db_password: DB_CONFIG["password"]  = args.db_password
    if args.db_host:     DB_CONFIG["host"]      = args.db_host
    if args.db_port:     DB_CONFIG["port"]      = args.db_port

    run_pipeline(
        total_new    = args.count,
        batch_size   = args.batch_size,
        skip_attrs   = args.skip_attrs,
        skip_recipes = args.skip_recipes,
        dry_run      = args.dry_run,
    )
