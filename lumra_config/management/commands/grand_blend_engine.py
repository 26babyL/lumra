"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  KAFE NUSANTARA — THE GRAND BLEND ENGINE v1.0                              ║
║  "From 7 Billion Possibilities — 9,999 Are Chosen"                        ║
║                                                                              ║
║  Arsitektur:                                                                 ║
║  1. BEAN MASTER DATABASE   — 651 profil biji unik (31 origin × 3 × 7)     ║
║  2. RARITY ENGINE          — Complexity Scorer & Tier Classifier           ║
║  3. BLEND GENERATOR        — 7.463 House Blend baru (anti-duplikasi)       ║
║  4. PRICING ENGINE         — Harga berdasarkan rarity + komponen           ║
║  5. COPYWRITING ENGINE     — 3-layer narasi per tier                       ║
║  6. EXPORT                 — Excel (4 sheet) + JSON (DB-ready)             ║
║                                                                              ║
║  Output:                                                                    ║
║    · kopi_9999_MASTER.xlsx  (4 sheet)                                      ║
║    · kopi_9999_db.json      (siap import ke Django/schema)                 ║
║                                                                              ║
║  Target: 9.999 total menu                                                   ║
║    · 2.536 Single Origin (preserve dari v3)                                ║
║    · 7.463 House Blend baru dengan rarity tier                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import json
import math
import itertools
from pathlib import Path
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

random.seed(2024)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MASTER BEAN DATABASE (651 profil biji unik)
# ═══════════════════════════════════════════════════════════════════════════════

ORIGINS_MASTER = {
    "aceh_gayo":        {"display":"Aceh Gayo",          "region":"Dataran Tinggi Gayo, Aceh",             "type":"Arabica",  "altitude":"1200–1700"},
    "arjuno":           {"display":"Gunung Arjuno",       "region":"Malang, Jawa Timur",                    "type":"Arabica",  "altitude":"1200–1600"},
    "bali_kintamani":   {"display":"Bali Kintamani",      "region":"Kintamani, Bangli, Bali",               "type":"Arabica",  "altitude":"1200–1500"},
    "bali_ulian":       {"display":"Bali Ulian",          "region":"Bangli, Bali",                          "type":"Arabica",  "altitude":"800–1200"},
    "bajawa":           {"display":"Flores Bajawa",       "region":"Ngada, Flores, NTT",                    "type":"Arabica",  "altitude":"1200–1800"},
    "bengkulu":         {"display":"Bengkulu",            "region":"Bengkulu, Sumatera",                    "type":"Arabica",  "altitude":"700–1400"},
    "bukit_barisan":    {"display":"Bukit Barisan",       "region":"Pegunungan Bukit Barisan, Sumatera",    "type":"Arabica",  "altitude":"1000–1600"},
    "ciwidey":          {"display":"Java Ciwidey",        "region":"Ciwidey, Bandung Selatan",              "type":"Arabica",  "altitude":"1400–1700"},
    "dampit":           {"display":"Dampit Malang",       "region":"Dampit, Malang, Jawa Timur",            "type":"Robusta",  "altitude":"400–900"},
    "dogiyai":          {"display":"Papua Dogiyai",       "region":"Dogiyai, Papua Tengah",                 "type":"Arabica",  "altitude":"1500–2000"},
    "flores_manggarai": {"display":"Flores Manggarai",    "region":"Manggarai, Flores, NTT",                "type":"Arabica",  "altitude":"1000–1600"},
    "garut":            {"display":"Java Garut",          "region":"Garut, Jawa Barat",                     "type":"Arabica",  "altitude":"1000–1400"},
    "gunung_halu":      {"display":"Gunung Halu",         "region":"Bandung Barat, Jawa Barat",             "type":"Arabica",  "altitude":"1200–1600"},
    "ijen_raung":       {"display":"Java Ijen Raung",     "region":"Bondowoso–Banyuwangi, Jawa Timur",      "type":"Arabica",  "altitude":"1000–1500"},
    "kalosi":           {"display":"Toraja Kalosi",       "region":"Enrekang, Sulawesi Selatan",            "type":"Arabica",  "altitude":"1000–1800"},
    "kayu_aro":         {"display":"Kerinci Kayu Aro",    "region":"Kayu Aro, Kerinci, Jambi",              "type":"Arabica",  "altitude":"1400–1800"},
    "lampung":          {"display":"Lampung Robusta",     "region":"Lampung, Sumatera Selatan",             "type":"Robusta",  "altitude":"400–800"},
    "lintong":          {"display":"Lintong",             "region":"Lintong Nihuta, Tapanuli, Sumut",       "type":"Arabica",  "altitude":"1400–1600"},
    "mandheling":       {"display":"Mandheling",          "region":"Mandailing Natal, Sumatera Utara",      "type":"Arabica",  "altitude":"900–1500"},
    "manglayang":       {"display":"Java Manglayang",     "region":"Gunung Manglayang, Bandung",            "type":"Arabica",  "altitude":"1000–1400"},
    "preanger":         {"display":"Java Preanger",       "region":"Priangan, Jawa Barat",                  "type":"Arabica",  "altitude":"1000–1400"},
    "puntang":          {"display":"Java Puntang",        "region":"Pengalengan, Bandung",                  "type":"Arabica",  "altitude":"1400–1700"},
    "rinjani":          {"display":"Sembalun Rinjani",    "region":"Sembalun, Lombok Timur",                "type":"Arabica",  "altitude":"1000–2000"},
    "sapan":            {"display":"Toraja Sapan",        "region":"Sapan, Toraja Utara, Sulsel",           "type":"Arabica",  "altitude":"1200–1800"},
    "semeru":           {"display":"Java Semeru",         "region":"Lumajang, Jawa Timur",                  "type":"Arabica",  "altitude":"900–1600"},
    "sidikalang":       {"display":"Sidikalang",          "region":"Dairi, Sumatera Utara",                 "type":"Arabica",  "altitude":"1200–1600"},
    "sindoro":          {"display":"Java Sindoro",        "region":"Temanggung–Wonosobo, Jawa Tengah",      "type":"Arabica",  "altitude":"1200–1700"},
    "solok_radjo":      {"display":"Solok Radjo",         "region":"Solok, Sumatera Barat",                 "type":"Arabica",  "altitude":"1200–1600"},
    "temanggung":       {"display":"Java Temanggung",     "region":"Temanggung, Jawa Tengah",               "type":"Arabica",  "altitude":"800–1200"},
    "wamena":           {"display":"Papua Wamena",        "region":"Lembah Baliem, Papua Pegunungan",       "type":"Arabica",  "altitude":"1500–2000"},
    "wanoja_kamojang":  {"display":"Wanoja Kamojang",     "region":"Kamojang, Garut, Jawa Barat",           "type":"Arabica",  "altitude":"1300–1700"},
}

ROASTS = ["Light", "Medium", "Dark"]

PROCESSES = ["Washed", "Natural", "Honey", "Semi-Washed", "Wet-Hulled", "Anaerobic", "Wine"]

# Complexity weight per process (untuk scoring)
PROCESS_COMPLEXITY = {
    "Washed":      1,   # Standard — paling mudah
    "Natural":     2,   # Lebih berisiko, fruity
    "Honey":       2,   # Medium complexity
    "Semi-Washed": 3,   # Less common
    "Wet-Hulled":  3,   # Khas Sumatera, tricky
    "Anaerobic":   5,   # Eksperimental, sangat sulit
    "Wine":        5,   # Paling eksperimental
}

# "Exotic" process pairs — kombinasi yang sangat sulit
EXOTIC_PAIRS = {
    frozenset(["Anaerobic", "Wine"]):       10,
    frozenset(["Anaerobic", "Wet-Hulled"]): 9,
    frozenset(["Wine", "Wet-Hulled"]):      9,
    frozenset(["Anaerobic", "Honey"]):      7,
    frozenset(["Wine", "Natural"]):         7,
    frozenset(["Anaerobic", "Natural"]):    6,
    frozenset(["Wine", "Semi-Washed"]):     6,
    frozenset(["Wet-Hulled", "Natural"]):   5,
}

# Rare origin combinations (lintas pulau yang berbeda)
ISLAND_MAP = {
    "aceh_gayo": "Sumatera", "bengkulu": "Sumatera", "bukit_barisan": "Sumatera",
    "kayu_aro": "Sumatera", "lampung": "Sumatera", "lintong": "Sumatera",
    "mandheling": "Sumatera", "sidikalang": "Sumatera", "solok_radjo": "Sumatera",
    "arjuno": "Jawa", "ciwidey": "Jawa", "dampit": "Jawa", "garut": "Jawa",
    "gunung_halu": "Jawa", "ijen_raung": "Jawa", "manglayang": "Jawa",
    "preanger": "Jawa", "puntang": "Jawa", "semeru": "Jawa",
    "sindoro": "Jawa", "temanggung": "Jawa", "wanoja_kamojang": "Jawa",
    "bali_kintamani": "Bali", "bali_ulian": "Bali",
    "bajawa": "Flores", "flores_manggarai": "Flores", "rinjani": "Lombok",
    "kalosi": "Sulawesi", "sapan": "Sulawesi",
    "dogiyai": "Papua", "wamena": "Papua",
}

# Flavor notes per origin × process × roast
FLAVOR_MATRIX = {
    # Format: (origin_key, process, roast) -> [notes]
    # Washed
    ("aceh_gayo",   "Washed", "Light"):  ["citrus", "jasmine", "peach", "lemon zest"],
    ("aceh_gayo",   "Washed", "Medium"): ["brown sugar", "hazelnut", "almond", "milk chocolate"],
    ("aceh_gayo",   "Washed", "Dark"):   ["dark chocolate", "molasses", "smoky caramel"],
    ("bali_kintamani","Washed","Light"):  ["bergamot", "green tea", "citrus", "lemon zest"],
    ("bali_kintamani","Washed","Medium"): ["caramel", "almond", "brown sugar"],
    ("bali_kintamani","Washed","Dark"):   ["bitter chocolate", "dark roast", "molasses"],
    ("kalosi",      "Washed", "Light"):  ["dark cherry", "citrus", "floral"],
    ("kalosi",      "Washed", "Medium"): ["dark chocolate", "hazelnut", "caramel"],
    ("kalosi",      "Washed", "Dark"):   ["dark espresso", "smoky", "bitter chocolate"],
    ("mandheling",  "Washed", "Light"):  ["herb", "cedar", "lime"],
    ("mandheling",  "Washed", "Medium"): ["earthy", "tobacco", "dark chocolate"],
    ("mandheling",  "Washed", "Dark"):   ["peat", "intense earth", "dark tobacco"],
    # Anaerobic
    ("aceh_gayo",   "Anaerobic", "Light"):  ["passion fruit", "lychee", "raspberry", "cola"],
    ("aceh_gayo",   "Anaerobic", "Medium"): ["fermented fruit", "tropical punch", "cacao nib"],
    ("aceh_gayo",   "Anaerobic", "Dark"):   ["black cherry", "dark rum", "fermented cocoa"],
    ("kalosi",      "Anaerobic", "Light"):  ["lychee", "passion fruit", "hibiscus"],
    ("kalosi",      "Anaerobic", "Medium"): ["tamarind", "cacao nib", "rum raisin"],
    ("kalosi",      "Anaerobic", "Dark"):   ["black cherry", "smoke", "dark rum"],
    ("dogiyai",     "Anaerobic", "Light"):  ["watermelon", "tropical fruit", "wine"],
    ("dogiyai",     "Anaerobic", "Medium"): ["dark chocolate", "fermented fruit", "dried fig"],
    ("wamena",      "Anaerobic", "Light"):  ["aged wine", "fermented fruit", "dark rum"],
    ("wamena",      "Anaerobic", "Medium"): ["smoke", "aged wine", "dark rum"],
    # Wine
    ("aceh_gayo",   "Wine", "Light"):   ["wine", "blackcurrant", "dark cherry", "grape must"],
    ("aceh_gayo",   "Wine", "Medium"):  ["port wine", "dark plum", "balsamic"],
    ("aceh_gayo",   "Wine", "Dark"):    ["aged wine", "tobacco", "smoked plum"],
    ("solok_radjo", "Wine", "Light"):   ["rum raisin", "passion fruit", "lychee"],
    ("solok_radjo", "Wine", "Medium"):  ["dark plum", "port wine", "cinnamon"],
    ("dogiyai",     "Wine", "Light"):   ["wine", "tropical fruit", "dried fig"],
    ("dogiyai",     "Wine", "Medium"):  ["dark plum", "roasted grape", "balsamic"],
    ("wamena",      "Wine", "Light"):   ["aged wine", "dark rum", "fermented fruit"],
    ("wamena",      "Wine", "Dark"):    ["tobacco", "tar", "smoked plum"],
    # Natural
    ("aceh_gayo",   "Natural", "Light"):  ["blueberry", "strawberry", "tropical fruit"],
    ("aceh_gayo",   "Natural", "Medium"): ["dark chocolate", "berry jam", "dried fig"],
    ("aceh_gayo",   "Natural", "Dark"):   ["dark berry", "espresso", "tar"],
    ("kalosi",      "Natural", "Light"):  ["blueberry", "hibiscus", "watermelon"],
    ("kalosi",      "Natural", "Medium"): ["dark chocolate", "prune", "molasses"],
    ("sapan",       "Natural", "Light"):  ["honey", "tropical fruit", "floral"],
    ("sapan",       "Natural", "Medium"): ["maple syrup", "dried fig", "milk chocolate"],
    # Wet-Hulled
    ("mandheling",  "Wet-Hulled", "Light"):  ["herb", "cedar", "green pepper"],
    ("mandheling",  "Wet-Hulled", "Medium"): ["earthy", "tobacco", "spice"],
    ("mandheling",  "Wet-Hulled", "Dark"):   ["peat", "bark", "dark tobacco"],
    ("aceh_gayo",   "Wet-Hulled", "Light"):  ["herb", "cedar", "lime"],
    ("aceh_gayo",   "Wet-Hulled", "Medium"): ["earthy", "spice", "woody"],
    ("aceh_gayo",   "Wet-Hulled", "Dark"):   ["intense earth", "clove", "dark tobacco"],
    # Honey
    ("bali_kintamani","Honey","Light"):  ["apricot", "honeysuckle", "white grape"],
    ("bali_kintamani","Honey","Medium"): ["honey", "toffee", "maple syrup"],
    ("kayu_aro",    "Honey", "Light"):   ["dried apricot", "tea-like", "cinnamon"],
    ("kayu_aro",    "Honey", "Medium"):  ["maple syrup", "honey", "fruity"],
    ("gunung_halu", "Honey", "Light"):   ["honey", "white grape", "floral"],
    ("gunung_halu", "Honey", "Medium"):  ["toffee", "caramel", "maple syrup"],
}

def get_flavor_notes(origin, process, roast):
    """Get flavor notes with fallback logic."""
    # Direct lookup
    key = (origin, process, roast)
    if key in FLAVOR_MATRIX:
        return FLAVOR_MATRIX[key]

    # Fallback by origin + process
    for r in ROASTS:
        k = (origin, process, r)
        if k in FLAVOR_MATRIX:
            notes = FLAVOR_MATRIX[k][:]
            # Adjust for roast level
            if roast == "Dark":
                notes = [n for n in notes if "fruit" not in n.lower()] + ["dark roast", "molasses"]
            elif roast == "Light":
                notes = [n for n in notes if "dark" not in n.lower() and "smoke" not in n.lower()]
            return notes[:4]

    # Generic fallback by process
    process_defaults = {
        "Washed":      ["citrus", "clean", "bright", "caramel"],
        "Natural":     ["berry", "tropical fruit", "honey", "dark chocolate"],
        "Honey":       ["honey", "apricot", "floral", "caramel"],
        "Semi-Washed": ["mandarin", "caramel", "light body", "clean"],
        "Wet-Hulled":  ["earthy", "tobacco", "spice", "woody"],
        "Anaerobic":   ["passion fruit", "fermented", "tropical", "cacao nib"],
        "Wine":        ["wine", "dark plum", "balsamic", "rum raisin"],
    }
    roast_adds = {
        "Light":  ["bright", "clean"],
        "Medium": ["caramel", "balanced"],
        "Dark":   ["dark roast", "molasses"],
    }
    base = process_defaults.get(process, ["balanced", "smooth"])[:3]
    base += roast_adds.get(roast, [])[:1]
    return base

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — RARITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

RARITY_TIERS = {
    "Tier 1 — The Vanguard":       {"code": "T1", "min_score": 0,  "max_score": 19,  "label": "Standard",       "emoji": "◆"},
    "Tier 2 — The Curator's Reserve": {"code": "T2", "min_score": 20, "max_score": 39,  "label": "Premium",        "emoji": "◈"},
    "Tier 3 — The Grand Artifact": {"code": "T3", "min_score": 40, "max_score": 100, "label": "Mythic · Limited","emoji": "✦"},
}

def compute_complexity_score(components):
    """
    Score seberapa 'gila' sebuah blend.
    components: list of {origin, roast, process, pct}
    Returns: (score:int, factors:list[str])
    """
    score = 0
    factors = []

    n = len(components)
    origins  = [c["origin"]  for c in components]
    processes = [c["process"] for c in components]
    roasts   = [c["roast"]   for c in components]

    # 1. Bean count bonus
    if n == 2: score += 2;  factors.append("2-bean blend (+2)")
    if n == 3: score += 8;  factors.append("3-bean blend (+8)")
    if n == 4: score += 15; factors.append("4-bean blend (+15)")

    # 2. Process complexity
    total_proc_score = sum(PROCESS_COMPLEXITY.get(p, 1) for p in processes)
    score += total_proc_score
    factors.append(f"process complexity +{total_proc_score} ({', '.join(processes)})")

    # 3. Exotic process pair bonus
    proc_set = frozenset(processes)
    for pair, bonus in EXOTIC_PAIRS.items():
        if pair.issubset(proc_set):
            score += bonus
            factors.append(f"exotic pair {'+'.join(sorted(pair))} +{bonus}")
            break

    # 4. Cross-island origin bonus
    islands = [ISLAND_MAP.get(o, "Unknown") for o in origins]
    unique_islands = len(set(islands))
    if unique_islands >= 3:
        score += 12; factors.append(f"3+ islands ({', '.join(set(islands))}) +12")
    elif unique_islands == 2:
        score += 6;  factors.append(f"2 islands ({', '.join(set(islands))}) +6")

    # 5. All-different process bonus
    if len(set(processes)) == n:
        score += 5; factors.append("all-different processes +5")

    # 6. Cross-type (Arabica + Robusta) bonus
    types = [ORIGINS_MASTER.get(o, {}).get("type", "Arabica") for o in origins]
    if len(set(types)) > 1:
        score += 4; factors.append("Arabica+Robusta cross-type +4")

    # 7. Extreme roast contrast (Light + Dark in same blend)
    if "Light" in roasts and "Dark" in roasts:
        score += 5; factors.append("Light+Dark roast contrast +5")

    # 8. High-altitude all-origin bonus (all >= 1200 mdpl)
    high_alt_count = 0
    for o in origins:
        alt = ORIGINS_MASTER.get(o, {}).get("altitude", "0–0")
        try:
            low = int(alt.split("–")[0])
            if low >= 1200:
                high_alt_count += 1
        except Exception:
            pass
    if high_alt_count == n:
        score += 5; factors.append(f"all high-altitude ({high_alt_count}/{n}) +5")

    # 9. Papua origin premium (ultra-rare, limited harvest)
    if any(o in ("dogiyai", "wamena") for o in origins):
        score += 6; factors.append("Papua origin (ultra-rare) +6")

    # 10. Anaerobic × Wine combination (the hardest)
    if "Anaerobic" in processes and "Wine" in processes:
        score += 8; factors.append("Anaerobic+Wine dual-ferment +8")

    return score, factors

def assign_rarity_tier(score):
    for tier_name, meta in RARITY_TIERS.items():
        if meta["min_score"] <= score <= meta["max_score"]:
            return tier_name, meta
    return "Tier 1 — The Vanguard", RARITY_TIERS["Tier 1 — The Vanguard"]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PRICING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

BASE_PRICES = {
    # (n_beans, tier_code) → base_price per 100g in IDR
    (2, "T1"): 45_000,
    (2, "T2"): 75_000,
    (2, "T3"): 135_000,
    (3, "T1"): 55_000,
    (3, "T2"): 95_000,
    (3, "T3"): 195_000,
    (4, "T1"): 65_000,
    (4, "T2"): 120_000,
    (4, "T3"): 275_000,
}

PROCESS_PREMIUM = {
    "Washed": 1.0, "Natural": 1.15, "Honey": 1.12,
    "Semi-Washed": 1.10, "Wet-Hulled": 1.08,
    "Anaerobic": 1.45, "Wine": 1.50,
}

ORIGIN_PREMIUM = {
    "dogiyai": 1.35, "wamena": 1.35, "rinjani": 1.25,
    "solok_radjo": 1.20, "kayu_aro": 1.18, "bali_kintamani": 1.15,
    "bajawa": 1.15, "sapan": 1.12, "kalosi": 1.12,
    "bukit_barisan": 1.10, "aceh_gayo": 1.10,
}

RETAIL_SIZES = {
    "100g":  1.0,
    "200g":  1.85,
    "500g":  4.20,
    "1kg":   7.80,
}

GRIND_PREMIUM = {
    "Whole Bean": 0,
    "Coarse":     2_500,
    "Medium":     3_000,
    "Fine":       3_500,
    "Extra Fine": 4_000,
}

MONTHLY_LIMIT_T3 = 50  # cup/bulan seluruh jaringan

def compute_pricing(components, tier_code, score):
    n = len(components)
    base = BASE_PRICES.get((n, tier_code), 65_000)

    # Process premium (highest process wins)
    proc_multiplier = max(PROCESS_PREMIUM.get(c["process"], 1.0) for c in components)

    # Origin premium (weighted average)
    origin_mult = 1.0
    for c in components:
        om = ORIGIN_PREMIUM.get(c["origin"], 1.0)
        origin_mult += (om - 1.0) * (c["pct"] / 100)

    # Score premium (each 10 points above threshold = +5%)
    score_bonus = 1.0 + (max(score - 20, 0) / 200)

    price_100g = int(base * proc_multiplier * origin_mult * score_bonus)

    # Round to nearest 5000
    price_100g = round(price_100g / 5_000) * 5_000
    price_100g = max(price_100g, 35_000)

    retail_prices = {
        size: int(price_100g * mult) + GRIND_PREMIUM["Whole Bean"]
        for size, mult in RETAIL_SIZES.items()
    }

    # Market price flag for T3
    is_market_price = (tier_code == "T3" and score >= 60)

    return {
        "price_per_100g": price_100g,
        "price_200g":     retail_prices["200g"],
        "price_500g":     retail_prices["500g"],
        "price_1kg":      retail_prices["1kg"],
        "is_market_price":is_market_price,
        "monthly_limit":  MONTHLY_LIMIT_T3 if tier_code == "T3" else None,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — WORLD BUILDING UNIVERSE
# ═══════════════════════════════════════════════════════════════════════════════

SEASON_UNIVERSE = {
    "Winter": {
        "universe": "The Dark Passage",
        "tagline":  "Di mana perjalanan dimulai — dalam kegelapan yang menyimpan bara.",
        "intro_pool": [
            "Dalam keheningan malam di antara dua puncak,",
            "Seperti api yang tak kunjung padam di pos terakhir,",
            "Ketika angin gunung membekukan jejak perjalanan,",
            "Di singgahan terakhir sebelum salju menutup jalur,",
        ],
        "closing_pool": {
            "T1": ["Sebuah penghormatan kepada mereka yang tak takut melangkah dalam gelap.",
                   "Diciptakan untuk jiwa-jiwa yang memahami bahwa perjalanan terbaik dimulai dari yang paling sunyi."],
            "T2": ["Hanya mereka yang pernah melewati malam terpanjang yang tahu — rasa ini tidak bisa dibeli dengan terburu-buru.",
                   "Dari tangan roaster yang telah gagal ratusan kali sebelum menemukan keseimbangan ini."],
            "T3": ["Ini bukan kopi. Ini adalah rekam jejak dari eksperimen yang berlangsung selama bertahun-tahun — dan hampir tidak pernah berhasil.",
                   "Di antara 7 miliar kemungkinan kombinasi, hanya blend ini yang selamat dari 300 sesi cupping. Bukan karena beruntung — tapi karena memang benar."],
        },
    },
    "Summer": {
        "universe": "The Open Horizon",
        "tagline":  "Ketika laut dan langit melebur — dan setiap tegukan terasa seperti angin pertama.",
        "intro_pool": [
            "Seperti angin laut yang pertama kali menyentuh dek,",
            "Ketika layar dibentangkan dan cakrawala terbuka lebar,",
            "Dari pelabuhan tua yang menyimpan ribuan cerita,",
            "Di mana muara sungai berjumpa dengan lautan terbuka,",
        ],
        "closing_pool": {
            "T1": ["Sebuah persembahan kepada rute-rute yang telah menghubungkan Nusantara selama berabad-abad.",
                   "Untuk para pelaut dalam diri kita — yang selalu menemukan jalan pulang."],
            "T2": ["Setiap tegukan menyimpan jejak tangan petani dari pulau-pulau berbeda yang tidak pernah bertemu — tapi bahannya bertemu di sini.",
                   "Butuh 18 bulan eksperimen sebelum rasio ini ditemukan. Kini ia hadir dalam satu cangkir."],
            "T3": ["Kombinasi ini tidak ada namanya di buku teks kopi manapun. Kami yang menamakannya — setelah 400 sesi cupping yang kebanyakan berakhir dengan kekecewaan.",
                   "Tiga pulau, tiga proses, satu harmoni yang nyaris mustahil. Produksi: 50 cangkir per bulan. Tidak lebih."],
        },
    },
    "Autumn": {
        "universe": "The Amber Descent",
        "tagline":  "Turun gunung sambil membawa cerita — dan aroma tanah yang belum terlupakan.",
        "intro_pool": [
            "Ditemukan dalam catatan perjalanan seorang penjelajah tua,",
            "Seperti kompas yang selalu menunjuk ke tempat yang tepat,",
            "Diilhami dari artefak yang bertahan melewati puluhan ekspedisi,",
            "Terekam dalam logbook yang lusuh namun tak pernah salah,",
        ],
        "closing_pool": {
            "T1": ["Diwariskan dari tangan-tangan yang mengukur bumi sebelum peta pernah ada.",
                   "Untuk setiap penjelajah yang memahami bahwa alat terbaik adalah yang paling sering dipakai."],
            "T2": ["Ini adalah blend yang lahir dari kegagalan — dan dari pembelajaran panjang yang mengikutinya.",
                   "Tidak semua artefak ditemukan di permukaan. Yang ini membutuhkan penggalian ratusan percobaan."],
            "T3": ["Ketika proses Anaerobic bertemu Wet-Hulled dalam satu blend, sebagian besar roaster menyerah di percobaan ke-50. Kami tidak. Inilah hasilnya.",
                   "Blend ini pernah gagal 247 kali sebelum batch ke-248 menghasilkan sesuatu yang tidak bisa dijelaskan dengan kata-kata biasa."],
        },
    },
    "Spring": {
        "universe": "The First Ascent",
        "tagline":  "Sebelum puncak — ada langkah pertama yang paling jujur.",
        "intro_pool": [
            "Saat kabut pagi pertama mulai mengangkat tirainya,",
            "Seperti embun yang jatuh pada daun pertama musim baru,",
            "Dari mata air yang baru saja membuka jejaknya di lereng,",
            "Di mana benih harapan tumbuh dari tanah yang baru mencair,",
        ],
        "closing_pool": {
            "T1": ["Untuk langkah pertama yang selalu lebih jujur dari seribu langkah berikutnya.",
                   "Sebuah perayaan atas keberanian memulai."],
            "T2": ["Ada biji yang tumbuh setahun sekali, di lereng yang tidak mudah dijangkau. Kami pergi ke sana. Ini hasilnya.",
                   "Kejernihan ini tidak lahir dari kesederhanaan — tapi dari kompleksitas yang telah dipelajari sampai menjadi instingtif."],
            "T3": ["Di antara 45 juta kemungkinan blend 3-biji, hanya ini yang melewati seluruh panel cupping kami dengan konsensus bulat. Satu dari 45 juta.",
                   "Proses Wine dari Solok Radjo, Anaerobic dari Papua Wamena, Wet-Hulled dari Aceh Gayo — tiga filosofi proses yang tidak seharusnya bertemu. Tapi saat bertemu, hasilnya adalah ini."],
        },
    },
}

SEASON_KEYWORDS = {
    "Winter": ["winter", "dark", "frost", "smoke", "night", "shadow", "midnight", "iron",
               "ember", "ash", "storm", "bitter", "coal", "cave", "black", "cozy night",
               "dark symphony", "espresso frost", "arctic", "choco snow"],
    "Summer": ["summer", "beach", "coastal", "ocean", "tropical", "fresh dawn", "citrus",
               "bloom", "fruity", "elevation", "fruity waves", "golden", "fresh", "bright"],
    "Autumn": ["autumn", "caramel", "harvest", "forest", "oak", "spice",
               "cozy cup", "cinnamon", "caramel forest", "green valley", "breeze", "warm"],
    "Spring": ["spring", "floral", "blooming", "blossom", "floral escape", "cool bold",
               "flower", "garden", "dew", "mist", "dawn", "petal"],
}

# Naming pools per tier per season
BLEND_NAMES = {
    "Winter": {
        "T1": {
            "modifiers": ["Frozen","Midnight","Smoldering","Shadowed","Iron","Ashen",
                          "Ember","Hollow","Veiled","Scorched","Muted","Buried","Charred",
                          "Ancient","Forgotten","Darkened","Stormy","Shrouded","Bitter",
                          "Sealed","Windswept","Dimmed","Frosted","Cracked","Heavy",
                          "Silent","Rugged","Faded","Blanketed","Hushed"],
            "anchors":   ["Bivouac","Shelter","Outpost","Refuge","Camp","Garrison",
                          "Waystation","Bastion","Stronghold","Lodge","Barracks","Depot",
                          "Quarters","Station","Passage","Encampment","Redoubt",
                          "Rampart","Crossing","Threshold","Citadel","Alcove",
                          "Hollow","Burrow","Den","Hearth","Keep","Vault","Sanctum"],
        },
        "T2": {
            "modifiers": ["Obsidian","Clandestine","Sovereign","Arcane","Rarest",
                          "Hallowed","Mythic","Uncharted","Forbidden","Encrypted"],
            "anchors":   ["Chronicle","Dispatch","Dossier","Registry","Compendium",
                          "Scroll","Parchment","Folio","Atlas","Cipher"],
            "prefix":    "Curator's",
        },
        "T3": {
            "modifiers": ["Final","Obsidian","Primordial","Singular","Consecrated",
                          "Immutable","Abyssal","Sovereign"],
            "anchors":   ["Codex","Grimoire","Manuscript","Arcanum","Testament",
                          "Sigil","Relic","Cipher"],
            "prefix":    "Grand Artifact",
        },
    },
    "Summer": {
        "T1": {
            "modifiers": ["Sunda","Banda","Makassar","Malacca","Timor","Flores",
                          "Lombok","Bali","Celebes","Molucca","Java","Borneo",
                          "Sulawesi","Ternate","Tidore","Ambon","Kupang","Manado",
                          "Padang","Palembang","Demak","Gresik","Tuban","Banten",
                          "Aceh","Riau","Jambi","Pontianak","Balikpapan","Sorong"],
            "anchors":   ["Voyage","Current","Trade Wind","Meridian","Bearing",
                          "Transit","Passage","Wake","Swell","Drift","Channel",
                          "Strait","Route","Course","Convoy","Fleet","Charter",
                          "Cargo","Expedition","Crossing","Traverse","Approach",
                          "Anchorage","Berth","Heading"],
        },
        "T2": {
            "modifiers": ["Admiral's","Captain's","Flagship","Imperial","Grand",
                          "Premier","Celestial","Legendary","Mythic","Sovereign"],
            "anchors":   ["Galleon","Clipper","Brigantine","Frigate","Schooner",
                          "Carrack","Dhow","Junk","Proa","Pinnace"],
            "prefix":    "Mariner's",
        },
        "T3": {
            "modifiers": ["Primordial","Celestial","Singular","Immutable","Sacred"],
            "anchors":   ["Armada","Flotilla","Convoy","Fleet","Syndicate"],
            "prefix":    "Grand Mariner",
        },
    },
    "Autumn": {
        "T1": {
            "modifiers": ["Weathered","Tarnished","Worn","Antique","Aged","Patinated",
                          "Rusted","Battered","Burnished","Timeworn","Cracked","Mended",
                          "Faded","Engraved","Embossed","Gilded","Hammered","Polished",
                          "Dented","Scarred","Handcrafted","Field-worn","Trail-kept",
                          "Well-used","Restored","Inherited","Storied","Hardy","True"],
            "anchors":   ["Compass","Sextant","Theodolite","Astrolabe","Barometer",
                          "Chronometer","Altimeter","Clinometer","Aneroid","Transit",
                          "Protractor","Divider","Planimeter","Odometer","Pedometer",
                          "Flask","Canteen","Lantern","Haversack","Rucksack",
                          "Penknife","Awl","Chisel","Hammer","Mallet",
                          "Ledger","Logbook","Field Notes","Survey Map"],
        },
        "T2": {
            "modifiers": ["Museum-Grade","Excavated","Preserved","One-of-a-Kind",
                          "Unearthed","Authenticated","Catalogued","Archived",
                          "Curated","Hallowed","Antiquarian","Heritage-Class"],
            "anchors":   ["Relic","Artifact","Heirloom","Specimen","Exhibit",
                          "Trophy","Keepsake","Token","Signet","Medallion"],
            "prefix":    "Relic",
        },
        "T3": {
            "modifiers": ["Primordial","Sacred","Immutable","Singular","Consecrated"],
            "anchors":   ["Talisman","Amulet","Seal","Insignia","Emblem"],
            "prefix":    "Grand Relic",
        },
    },
    "Spring": {
        "T1": {
            "modifiers": ["First","Morning","Dawn","Early","Rising","Waking","Breaking",
                          "Opening","Nascent","New","Fresh","Young","Gentle","Soft",
                          "Tender","Pale","Faint","Quiet","Still","Pure","Thin","Wispy",
                          "Shifting","Drifting","Hovering","Climbing","Ascending",
                          "Gathering","Blooming","Stirring"],
            "anchors":   ["Dew","Mist","Frost","Haze","Fog","Vapor","Cloud","Cumulus",
                          "Cirrus","Rime","Bloom","Blossom","Pollen","Spore",
                          "Spring","Runoff","Snowmelt","Brook","Rivulet",
                          "Lichen","Moss","Fern","Sprig","Tendril",
                          "Sunbreak","Clearance","Wellspring","Headwater"],
        },
        "T2": {
            "modifiers": ["Inaugural","Pioneering","Trailblazing","Pathfinding",
                          "Groundbreaking","Landmark","Defining","Formative",
                          "Foundational","Pristine","Unspoiled","Untouched"],
            "anchors":   ["Entry","Record","Account","Memoir","Testament",
                          "Dispatch","Notation","Inscription","Discovery","Finding"],
            "prefix":    "Pioneer's",
        },
        "T3": {
            "modifiers": ["Primordial","Elemental","Singular","Sacred","Immutable"],
            "anchors":   ["Revelation","Disclosure","Venture","Initiative","Genesis"],
            "prefix":    "Grand Pioneer",
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def detect_season(name_str):
    name_lower = name_str.lower()
    for season, keywords in SEASON_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return season
    return random.choice(["Autumn", "Winter", "Spring", "Summer"])

def build_blend_name(season, tier_code, used_names, attempt=0):
    pool = BLEND_NAMES.get(season, BLEND_NAMES["Autumn"])
    tier_pool = pool.get(tier_code, pool["T1"])

    prefix  = tier_pool.get("prefix", "")
    mods    = tier_pool["modifiers"]
    anchors = tier_pool["anchors"]

    for _ in range(60):
        mod    = random.choice(mods)
        anchor = random.choice(anchors)
        if prefix:
            name = f"{prefix} {mod} {anchor}"
        else:
            name = f"{mod} {anchor}"
        if name not in used_names:
            used_names.add(name)
            return name

    fallback = f"{season} Blend #{len(used_names)+1+attempt}"
    used_names.add(fallback)
    return fallback

def build_description(components, tier_code, season, score, factors, tasting_notes):
    su = SEASON_UNIVERSE.get(season, SEASON_UNIVERSE["Autumn"])
    intro   = random.choice(su["intro_pool"])
    closing = random.choice(su["closing_pool"][tier_code])

    origins_display = []
    for c in components:
        orig_info = ORIGINS_MASTER.get(c["origin"], {})
        origins_display.append(orig_info.get("display", c["origin"].replace("_", " ").title()))

    if len(origins_display) == 1:
        origins_str = origins_display[0]
    elif len(origins_display) == 2:
        origins_str = f"{origins_display[0]} dan {origins_display[1]}"
    else:
        origins_str = f"{', '.join(origins_display[:-1])}, dan {origins_display[-1]}"

    processes = list({c["process"] for c in components})
    proc_str  = " × ".join(processes[:3])

    notes_str = ", ".join(tasting_notes[:3]) if tasting_notes else "kompleks, berlapis"

    if tier_code == "T1":
        body = (
            f"blend ini mempertemukan biji dari {origins_str} "
            f"melalui proses {proc_str}. "
            f"Profil rasa {notes_str} hadir dengan kejujuran yang langsung."
        )
    elif tier_code == "T2":
        body = (
            f"blend ini merajut karakter biji dari {origins_str} "
            f"dalam eksperimen proses {proc_str} yang membutuhkan presisi tinggi. "
            f"Profil rasa {notes_str} — berlapis dan tidak mudah dilupakan. "
            f"Complexity score: {score}/100."
        )
    else:  # T3
        n_bean = len(components)
        island_str = ", ".join(sorted({ISLAND_MAP.get(c["origin"], "Nusantara") for c in components}))
        body = (
            f"ini adalah blend {n_bean} biji dari {island_str} — "
            f"{origins_str} — yang diproses dengan metode {proc_str}. "
            f"Kombinasi ini termasuk dalam 0.0001% dari 7 miliar kemungkinan blend yang ada. "
            f"Profil rasa {notes_str}. "
            f"Complexity score: {score}/100. "
            f"Tersedia maksimal {MONTHLY_LIMIT_T3} cangkir per bulan di seluruh jaringan The Archipelagic Outposts."
        )

    return f"{intro} {body} {closing}"

def compute_tasting_notes_blend(components):
    all_notes = []
    for c in components:
        notes = get_flavor_notes(c["origin"], c["process"], c["roast"])
        weight = c["pct"] / 100
        # Take more notes from higher-percentage beans
        n_take = max(1, round(len(notes) * weight * 2))
        all_notes.extend(random.sample(notes, min(n_take, len(notes))))

    seen, unique = set(), []
    for n in all_notes:
        if n.lower() not in seen:
            seen.add(n.lower()); unique.append(n)
    return unique[:5]

def compute_flavour_wheel(notes):
    text = " ".join(notes).lower()
    kmap = {
        "Fruity":     ["fruit","berry","citrus","plum","fig","apricot","peach","watermelon",
                       "grape","lychee","passion","blueberry","tropical","lemon"],
        "Sweet":      ["caramel","honey","toffee","molasses","sugar","maple","vanilla"],
        "Nutty":      ["nut","almond","hazelnut","walnut","macadamia","pecan"],
        "Chocolatey": ["chocolate","cocoa","cacao","mocha","fudge"],
        "Spicy":      ["spice","cinnamon","clove","pepper","nutmeg","ginger"],
        "Floral":     ["floral","jasmine","rose","lavender","chamomile","honeysuckle","bloom"],
        "Earthy":     ["earthy","mushroom","wood","woody","soil","peat","bark","herb","cedar"],
        "Roasted":    ["smok","roast","tobacco","charcoal","espresso","tar","dark roast"],
        "Fermented":  ["wine","rum","aged","ferment","balsamic","licorice","raisin","cola"],
    }
    scores = {k: sum(1 for kw in kws if kw in text) for k, kws in kmap.items()}
    top = [k for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True) if v > 0]
    return ", ".join(top[:3]) if top else "Nutty, Chocolatey"

DESSERT_MAP = {
    "Chocolatey": ["Chocolate Lava Cake","Dark Brownies","Espresso Mousse","Tiramisu"],
    "Nutty":      ["Almond Croissant","Hazelnut Tart","Pistachio Cake","Tiramisu"],
    "Fruity":     ["Fruit Tart","Berry Cheesecake","Pavlova","Panna Cotta"],
    "Spicy":      ["Cinnamon Roll","Carrot Cake","Gingerbread","Speculaas"],
    "Earthy":     ["Tiramisu","Matcha Cake","Panna Cotta","Affogato"],
    "Floral":     ["French Macarons","Earl Grey Cake","Rose Tart","Lavender Cookies"],
    "Sweet":      ["Crème Brûlée","Caramel Pudding","Honey Toast","Flan"],
    "Roasted":    ["Espresso Brownies","Mocha Layer Cake","Coffee Cake","Tiramisu"],
    "Fermented":  ["Dark Chocolate Truffles","Rum Cake","Aged Cheese Tart","Wine Cake"],
}

def compute_dessert(wheel_str):
    wheels = [w.strip() for w in wheel_str.split(",")]
    seen, out = set(), []
    for w in wheels:
        for d in DESSERT_MAP.get(w, []):
            if d not in seen:
                seen.add(d); out.append(d)
            if len(out) >= 3:
                return ", ".join(out)
    return ", ".join(out) if out else "Tiramisu, Dark Brownies"

def weighted_percentages(n):
    if n == 2:
        a = random.choice([40,45,50,55,60,65,70])
        return [a, 100 - a]
    elif n == 3:
        opts = [[50,30,20],[60,25,15],[40,35,25],[45,35,20],[55,30,15],[50,25,25]]
        return random.choice(opts)
    else:  # 4
        opts = [[40,25,20,15],[35,30,20,15],[50,20,15,15],[45,25,20,10]]
        return random.choice(opts)

def build_sku(season, tier_code, idx):
    season_codes = {"Winter":"WIN","Summer":"SUM","Autumn":"AUT","Spring":"SPR"}
    s = season_codes.get(season, "AUT")
    return f"HB-{s}-{tier_code}-{idx:04d}"

def build_resep_str(components):
    parts = []
    for c in components:
        disp = ORIGINS_MASTER.get(c["origin"], {}).get("display", c["origin"].title())
        parts.append(f"{disp} ({c['roast']}/{c['process']}): {c['gram']}g ({c['pct']}%)")
    total = sum(c["gram"] for c in components)
    parts.append(f"total: {total}g")
    return " | ".join(parts)

def get_brew_method(components, tier_code):
    process_brew = {
        "Washed":      ["V60","Chemex","Pour Over"],
        "Natural":     ["AeroPress","French Press","Cold Brew"],
        "Honey":       ["V60","AeroPress","Chemex"],
        "Semi-Washed": ["French Press","AeroPress","Pour Over"],
        "Wet-Hulled":  ["French Press","Moka Pot","Vietnam Drip"],
        "Anaerobic":   ["AeroPress","Espresso","Ristretto"],
        "Wine":        ["AeroPress","French Press","Ristretto"],
    }
    if tier_code == "T3":
        # Speciality brewing only
        return "Cupping · AeroPress · Ristretto"

    all_methods = []
    for c in components:
        all_methods.extend(process_brew.get(c["process"], ["AeroPress"]))
    scores = {}
    for m in all_methods:
        scores[m] = scores.get(m, 0) + 1
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return " · ".join(m for m, _ in top[:2])

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — BLEND GENERATOR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_blend_components(n_beans, tier_code):
    """Generate n_beans components biased by tier requirements."""
    origins_list = list(ORIGINS_MASTER.keys())

    # T3: bias toward exotic processes and rare origins
    if tier_code == "T3":
        exotic_processes = ["Anaerobic", "Wine", "Wet-Hulled"]
        standard_processes = ["Washed", "Natural", "Honey", "Semi-Washed"]
        rare_origins = ["dogiyai", "wamena", "rinjani", "solok_radjo", "kayu_aro", "bajawa"]

        chosen_origins = random.sample(
            rare_origins + origins_list,
            min(n_beans, len(rare_origins + origins_list))
        )[:n_beans]
        # Ensure at least 1 rare origin
        if not any(o in rare_origins for o in chosen_origins):
            chosen_origins[0] = random.choice(rare_origins)
        chosen_origins = list(dict.fromkeys(chosen_origins))[:n_beans]
        if len(chosen_origins) < n_beans:
            extras = [o for o in origins_list if o not in chosen_origins]
            chosen_origins += random.sample(extras, n_beans - len(chosen_origins))

        # Ensure at least 1 exotic process, and variety
        processes = [random.choice(exotic_processes)]
        for _ in range(n_beans - 1):
            processes.append(random.choice(PROCESSES))
        # Shuffle so exotic isn't always first
        random.shuffle(processes)
        # Ensure no more than n_beans/2 identical processes
        if len(set(processes)) == 1:
            processes[0] = random.choice(exotic_processes)

    elif tier_code == "T2":
        # Mix: some exotic, some standard
        chosen_origins = random.sample(origins_list, n_beans)
        processes = []
        for i in range(n_beans):
            if i == 0:
                processes.append(random.choice(["Anaerobic","Wine","Natural","Honey"]))
            else:
                processes.append(random.choice(PROCESSES))

    else:  # T1
        chosen_origins = random.sample(origins_list, n_beans)
        processes = [random.choice(["Washed","Natural","Honey","Semi-Washed"]) for _ in range(n_beans)]

    roasts_chosen = [random.choice(ROASTS) for _ in range(n_beans)]
    pcts = weighted_percentages(n_beans)
    base_gram = 1000

    components = []
    for i, (o, proc, roast, pct) in enumerate(zip(chosen_origins, processes, roasts_chosen, pcts)):
        components.append({
            "origin":  o,
            "process": proc,
            "roast":   roast,
            "pct":     pct,
            "gram":    int(base_gram * pct / 100),
        })
    return components

def generate_all_blends(target_hb=7463):
    """Generate target_hb new House Blend entries with full rarity scoring."""

    # Tier distribution
    t1_target = int(target_hb * 0.60)  # ~4,477
    t2_target = int(target_hb * 0.30)  # ~2,238
    t3_target = target_hb - t1_target - t2_target  # ~748

    # Bean count distribution per tier
    tier_bean_dist = {
        "T1": [2, 2, 2, 3],           # mostly 2-bean, some 3
        "T2": [2, 3, 3, 3, 4],        # mostly 3-bean, some 4
        "T3": [3, 3, 4, 4, 4],        # mostly 4-bean, some 3
    }

    used_compositions = set()
    used_names = set()
    results = []

    tier_configs = [
        ("Tier 1 — The Vanguard", "T1", t1_target),
        ("Tier 2 — The Curator's Reserve", "T2", t2_target),
        ("Tier 3 — The Grand Artifact", "T3", t3_target),
    ]

    sku_counters = {"T1": 1, "T2": 1, "T3": 1}

    for tier_name, tier_code, count in tier_configs:
        generated = 0
        attempts = 0
        max_attempts = count * 30
        print(f"  Generating {count:,} × {tier_name}...")

        while generated < count and attempts < max_attempts:
            attempts += 1

            n_beans = random.choice(tier_bean_dist[tier_code])
            components = generate_blend_components(n_beans, tier_code)
            origins = [c["origin"] for c in components]

            # Anti-duplicate: composition key
            comp_key = tuple(sorted(
                (c["origin"], c["roast"], c["process"]) for c in components
            ))
            if comp_key in used_compositions:
                continue
            used_compositions.add(comp_key)

            # Score & tier check
            score, factors = compute_complexity_score(components)
            assigned_tier, tier_meta = assign_rarity_tier(score)
            assigned_code = tier_meta["code"]

            # Enforce tier match (with some tolerance to hit targets)
            # T3 needs score >= 40, T2 needs 20-39, T1 is 0-19
            if tier_code == "T3" and score < 35:
                continue
            if tier_code == "T2" and (score < 15 or score > 50):
                continue
            if tier_code == "T1" and score > 30:
                continue

            # Determine season from origins (dominant island → season bias)
            islands = [ISLAND_MAP.get(o, "Jawa") for o in origins]
            island_counter = {}
            for isl in islands:
                island_counter[isl] = island_counter.get(isl, 0) + 1
            dominant_island = max(island_counter, key=island_counter.get)
            island_season_bias = {
                "Jawa":     ["Autumn", "Spring"],
                "Sumatera": ["Winter", "Autumn"],
                "Bali":     ["Summer", "Spring"],
                "Flores":   ["Summer", "Autumn"],
                "Lombok":   ["Summer", "Spring"],
                "Sulawesi": ["Winter", "Autumn"],
                "Papua":    ["Winter", "Summer"],
            }
            season = random.choice(island_season_bias.get(dominant_island, ["Autumn","Winter"]))

            # Build all fields
            tasting_notes = compute_tasting_notes_blend(components)
            notes_str     = ", ".join(tasting_notes)
            wheel         = compute_flavour_wheel(tasting_notes)
            dessert       = compute_dessert(wheel)
            brew          = get_brew_method(components, tier_code)
            pricing       = compute_pricing(components, tier_code, score)
            name          = build_blend_name(season, tier_code, used_names)
            sku           = build_sku(season, tier_code, sku_counters[tier_code])
            desc          = build_description(components, tier_code, season, score, factors, tasting_notes)
            resep_str     = build_resep_str(components)

            su = SEASON_UNIVERSE.get(season, SEASON_UNIVERSE["Autumn"])

            # Texture from dominant roast
            roast_score_map = {"Light": 1, "Medium": 2, "Dark": 3}
            w_roast = sum(roast_score_map.get(c["roast"], 2) * c["pct"] for c in components)
            avg_r   = w_roast / max(sum(c["pct"] for c in components), 1)
            dom_roast = "Light" if avg_r < 1.7 else ("Dark" if avg_r >= 2.5 else "Medium")
            texture_map = {"Light": "Silky & Clean", "Medium": "Smooth & Balanced", "Dark": "Bold & Heavy"}
            texture = texture_map[dom_roast]

            # Body / Acidity / Sweetness
            body_base     = sum({"Light":4,"Medium":6,"Dark":8}.get(c["roast"],6) * c["pct"]/100 for c in components)
            acidity_base  = sum({"Light":7,"Medium":5,"Dark":3}.get(c["roast"],5) * c["pct"]/100 for c in components)
            sweetness_base= sum({"Natural":7,"Honey":6,"Wine":6,"Anaerobic":5,
                                  "Washed":4,"Semi-Washed":5,"Wet-Hulled":4}.get(c["process"],5) * c["pct"]/100 for c in components)
            body     = max(1, min(10, round(body_base)))
            acidity  = max(1, min(10, round(acidity_base)))
            sweetness= max(1, min(10, round(sweetness_base)))

            # Copywriting snippets
            origin_displays = [ORIGINS_MASTER.get(c["origin"],{}).get("display", c["origin"]) for c in components]
            copy_pkg = (
                f"{name}\n"
                f"{su['universe']} · {season} · {tier_meta['label']}\n"
                f"{' & '.join(origin_displays[:2])} · {tasting_notes[0] if tasting_notes else 'complex'}\n"
                f"Rp {pricing['price_per_100g']:,} / 100g"
            )
            if tier_code == "T3":
                copy_social = (
                    f"Tidak ada yang mudah tentang kopi ini.\n\n"
                    f"Perkenalkan {name} — dari {su['universe']}.\n"
                    f"Complexity score: {score}/100. "
                    f"Tersedia {MONTHLY_LIMIT_T3} cangkir/bulan. Seluruh Nusantara.\n\n"
                    f"Harga: Rp {pricing['price_per_100g']:,}/100g · Market price berlaku.\n\n"
                    f"#GrandArtifact #TheFourExpeditions #KafeNusantara #RareCoffee"
                )
            else:
                copy_social = (
                    f"Perkenalkan {name} — {season} · {su['universe']}.\n"
                    f"{'·'.join(origin_displays[:2])} · {notes_str[:60]}\n\n"
                    f"#TheFourExpeditions #{season}Blend #KafeNusantara"
                )

            entry = {
                "sku":                   sku,
                "name":                  name,
                "category":              "House Blend",
                "season":                season,
                "season_universe":       su["universe"],
                "rarity_tier":           tier_name,
                "rarity_tier_code":      tier_code,
                "rarity_label":          tier_meta["label"],
                "complexity_score":      score,
                "complexity_factors":    " | ".join(factors),
                "n_beans":               n_beans,
                "origin_1":              ORIGINS_MASTER.get(origins[0],{}).get("display","") if len(origins)>0 else "",
                "origin_2":              ORIGINS_MASTER.get(origins[1],{}).get("display","") if len(origins)>1 else "",
                "origin_3":              ORIGINS_MASTER.get(origins[2],{}).get("display","") if len(origins)>2 else "",
                "origin_4":              ORIGINS_MASTER.get(origins[3],{}).get("display","") if len(origins)>3 else "",
                "dominant_roast":        dom_roast,
                "resep_gramasi":         resep_str,
                "rekomendasi_penyajian": brew,
                "deskripsi":             desc,
                "tasting_notes":         notes_str,
                "texture_profile":       texture,
                "flavour_wheel":         wheel,
                "body":                  body,
                "acidity":               acidity,
                "sweetness":             sweetness,
                "recommended_dessert":   dessert,
                "price_per_100g":        pricing["price_per_100g"],
                "price_200g":            pricing["price_200g"],
                "price_500g":            pricing["price_500g"],
                "price_1kg":             pricing["price_1kg"],
                "is_market_price":       pricing["is_market_price"],
                "monthly_limit":         pricing["monthly_limit"] or "",
                "affiliated_outpost":    f"Outpost 22: The Final Meridian",
                "copywriting_packaging": copy_pkg,
                "copywriting_social":    copy_social,
            }
            results.append(entry)
            sku_counters[tier_code] += 1
            generated += 1

        print(f"    ✅ Generated {generated:,} / {count:,}  (attempts: {attempts:,})")

    return results

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — EXCEL EXPORT (4 sheets)
# ═══════════════════════════════════════════════════════════════════════════════

TIER_COLORS = {
    "T1": {"dark": "1C3A5E", "light": "D6E4F0", "text": "FFFFFF"},
    "T2": {"dark": "4A0E2A", "light": "F5EAF0", "text": "FFFFFF"},
    "T3": {"dark": "7D5A00", "light": "FBF6E8", "text": "FFFFFF"},
}
SEASON_COLORS = {
    "Winter": ("1C3A5E", "D6E4F0"),
    "Summer": ("8B4A00", "FDEBD0"),
    "Autumn": ("5C3800", "FAE5D3"),
    "Spring": ("1D5C2E", "D5F5E3"),
}

def hf(hex_str):
    return PatternFill(start_color=hex_str, end_color=hex_str, fill_type="solid")

def export_excel(blends, output_path):
    wb = Workbook()
    THIN = Border(
        left=Side(style="thin",color="CCCCCC"), right=Side(style="thin",color="CCCCCC"),
        top=Side(style="thin",color="CCCCCC"),  bottom=Side(style="thin",color="CCCCCC"),
    )
    CENTER  = Alignment(horizontal="center", vertical="center", wrap_text=True)
    WRAP_T  = Alignment(horizontal="left",   vertical="top",    wrap_text=True)
    HDR_FNT = lambda: Font(name="Arial", size=10, bold=True, color="FFFFFF")
    BOD_FNT = lambda: Font(name="Arial", size=10, color="1A1A1A")
    BLD_FNT = lambda: Font(name="Arial", size=10, bold=True, color="1A1A1A")
    SCR_FNT = lambda: Font(name="Arial", size=10, bold=True, color="FFFFFF")

    # ── Sheet 1: Full Blend Data ──────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = "House Blend 7463"

    COLS = [
        ("sku",                   "SKU",                    18),
        ("name",                  "Nama Blend",             32),
        ("season",                "Season",                 12),
        ("season_universe",       "Universe",               22),
        ("rarity_tier",           "Rarity Tier",            28),
        ("rarity_label",          "Label",                  18),
        ("complexity_score",      "Complexity Score",       16),
        ("n_beans",               "# Biji",                  8),
        ("origin_1",              "Origin 1",               20),
        ("origin_2",              "Origin 2",               20),
        ("origin_3",              "Origin 3",               20),
        ("origin_4",              "Origin 4",               20),
        ("dominant_roast",        "Dominant Roast",         14),
        ("resep_gramasi",         "Resep / Gramasi",        55),
        ("rekomendasi_penyajian", "Rekomendasi Penyajian",  28),
        ("deskripsi",             "Deskripsi",              65),
        ("tasting_notes",         "Tasting Notes",          42),
        ("texture_profile",       "Texture Profile",        22),
        ("flavour_wheel",         "Flavour Wheel",          28),
        ("body",                  "Body (1–10)",            11),
        ("acidity",               "Acidity (1–10)",         12),
        ("sweetness",             "Sweetness (1–10)",       13),
        ("recommended_dessert",   "Recommended Dessert",    38),
        ("price_per_100g",        "Harga / 100g (IDR)",     18),
        ("price_200g",            "Harga 200g",             14),
        ("price_500g",            "Harga 500g",             14),
        ("price_1kg",             "Harga 1kg",              14),
        ("is_market_price",       "Market Price?",          14),
        ("monthly_limit",         "Limit/Bulan",            12),
        ("complexity_factors",    "Complexity Factors",     55),
        ("copywriting_packaging", "Copy: Packaging",        45),
        ("copywriting_social",    "Copy: Social",           55),
    ]

    # Header
    for ci, (key, label, width) in enumerate(COLS, 1):
        c = ws1.cell(row=1, column=ci, value=label)
        c.fill = hf("1B1B2F"); c.font = HDR_FNT()
        c.alignment = CENTER; c.border = THIN
        ws1.column_dimensions[get_column_letter(ci)].width = width
    ws1.row_dimensions[1].height = 36

    for ri, row in enumerate(blends, 2):
        tc = row.get("rarity_tier_code", "T1")
        season = row.get("season", "Autumn")
        tc_colors = TIER_COLORS.get(tc, TIER_COLORS["T1"])
        sc_dark, sc_light = SEASON_COLORS.get(season, ("5C3800","FAF0DC"))
        alt = ri % 2 == 0

        desc_len = len(str(row.get("deskripsi","")))
        ws1.row_dimensions[ri].height = 80 if desc_len > 250 else (55 if desc_len > 120 else 38)

        for ci, (key, label, _) in enumerate(COLS, 1):
            val = row.get(key, "")
            c = ws1.cell(row=ri, column=ci, value=val)
            c.border = THIN

            if key == "season":
                c.fill = hf(sc_dark)
                c.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
                c.alignment = CENTER
            elif key == "rarity_tier":
                c.fill = hf(tc_colors["dark"])
                c.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")
                c.alignment = WRAP_T
            elif key == "complexity_score":
                sc_val = int(val) if str(val).isdigit() else 0
                bg = "E74C3C" if sc_val < 20 else ("F39C12" if sc_val < 40 else "27AE60")
                c.fill = hf(bg); c.font = SCR_FNT(); c.alignment = CENTER
            elif key in ("body","acidity","sweetness"):
                try:
                    sv = int(val)
                    bg = "27AE60" if sv>=7 else ("F39C12" if sv>=4 else "E74C3C")
                    c.fill = hf(bg); c.font = SCR_FNT(); c.alignment = CENTER
                except Exception:
                    c.fill = hf(sc_light); c.font = BOD_FNT(); c.alignment = CENTER
            elif key in ("price_per_100g","price_200g","price_500g","price_1kg"):
                c.fill = hf(tc_colors["light"] if tc in ("T2","T3") else ("F0F0F0" if alt else "FFFFFF"))
                c.font = BLD_FNT(); c.alignment = CENTER
                if tc == "T3":
                    c.font = Font(name="Arial", size=10, bold=True, color="7D5A00")
            elif key == "is_market_price":
                c.fill = hf("FBF6E8" if val else ("F0F0F0" if alt else "FFFFFF"))
                c.font = Font(name="Arial", size=10, bold=bool(val),
                              color="B8922A" if val else "7A7469")
                c.alignment = CENTER
            elif key == "name":
                c.fill = hf(tc_colors["light"] if alt else "FFFFFF")
                c.font = BLD_FNT(); c.alignment = WRAP_T
            else:
                c.fill = hf(sc_light if alt else "FFFFFF")
                c.font = BOD_FNT(); c.alignment = WRAP_T

    ws1.freeze_panes = "C2"
    ws1.auto_filter.ref = f"A1:{get_column_letter(len(COLS))}1"

    # ── Sheet 2: Rarity Tier Guide ─────────────────────────────────────────────
    ws2 = wb.create_sheet("Rarity Tier Guide")
    ws2.column_dimensions["A"].width = 30
    ws2.column_dimensions["B"].width = 18
    ws2.column_dimensions["C"].width = 18
    ws2.column_dimensions["D"].width = 60
    ws2.column_dimensions["E"].width = 22
    ws2.column_dimensions["F"].width = 22

    hdr2 = ["Tier Name","Code","Score Range","Kriteria & Deskripsi","Harga Base/100g","Monthly Limit"]
    for ci, h in enumerate(hdr2, 1):
        c = ws2.cell(row=1, column=ci, value=h)
        c.fill = hf("1B1B2F"); c.font = HDR_FNT(); c.alignment = CENTER; c.border = THIN
    ws2.row_dimensions[1].height = 32

    tier_info = [
        ("Tier 1 — The Vanguard",        "T1", "0–19",
         "Blend 2-3 biji dengan proses standar (Washed/Natural/Honey). "
         "Menu harian — accessible, consistent, reliable. "
         "Basis dari The Four Expeditions.",
         "Rp 45.000–65.000", "Tidak ada batas"),
        ("Tier 2 — The Curator's Reserve","T2", "20–39",
         "Blend 2-4 biji lintas pulau atau menggunakan proses eksperimental "
         "(Wine/Anaerobic). Membutuhkan presisi tinggi dalam roasting. "
         "Hanya tersedia di Outpost tertentu.",
         "Rp 75.000–120.000", "Tidak ada batas"),
        ("Tier 3 — The Grand Artifact",  "T3", "40–100",
         "Blend 3-4 biji lintas 2-3+ pulau dengan ≥2 proses eksperimental. "
         "Complexity score ≥40. Butuh ratusan sesi cupping untuk finalisasi. "
         "Harga Market Price. Limited 50 cup/bulan seluruh jaringan.",
         "Rp 135.000–275.000", "50 cup/bulan · seluruh jaringan"),
    ]

    for ri, (tname, code, score_r, crit, price, limit) in enumerate(tier_info, 2):
        tc_c = TIER_COLORS.get(code, TIER_COLORS["T1"])
        vals = [tname, code, score_r, crit, price, limit]
        for ci, v in enumerate(vals, 1):
            c = ws2.cell(row=ri, column=ci, value=v)
            c.border = THIN; c.alignment = WRAP_T
            if ci <= 2:
                c.fill = hf(tc_c["dark"])
                c.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
                c.alignment = CENTER
            else:
                c.fill = hf(tc_c["light"])
                c.font = BOD_FNT()
        ws2.row_dimensions[ri].height = 70

    # Complexity scoring breakdown
    ws2.cell(row=6, column=1, value="COMPLEXITY SCORING BREAKDOWN").font = Font(name="Arial", size=11, bold=True)
    score_rows = [
        ["Factor", "Points", "Keterangan"],
        ["2-bean blend",          "+2",  "Dasar blend 2 biji"],
        ["3-bean blend",          "+8",  "Lebih kompleks, butuh balancing lebih cermat"],
        ["4-bean blend",          "+15", "Sangat sulit — densitas & roast profile berbeda"],
        ["Proses Washed",         "+1",  "Standard"],
        ["Proses Natural/Honey",  "+2",  "Lebih kompleks, fruity-forward"],
        ["Proses Wet-Hulled/Semi","+3",  "Karakteristik unik Sumatera"],
        ["Proses Anaerobic/Wine", "+5",  "Eksperimental, sangat sulit dikontrol"],
        ["Anaerobic × Wine pair", "+10", "Dual-ferment — the hardest combination"],
        ["Cross-island (2 pulau)","+6",  "Biji dari 2 pulau berbeda"],
        ["Cross-island (3+ pulau)","+12","Biji dari 3+ pulau berbeda"],
        ["All-different processes","+5", "Semua biji punya proses berbeda"],
        ["Arabica + Robusta mix",  "+4", "Cross-type blend"],
        ["Light + Dark roast",    "+5",  "Kontras ekstrem, sulit dibalance"],
        ["All high-altitude",     "+5",  "Semua biji dari ketinggian ≥1200 mdpl"],
        ["Papua origin",          "+6",  "Ultra-rare, harvest sangat terbatas"],
    ]
    for ri, row_vals in enumerate(score_rows, 7):
        for ci, v in enumerate(row_vals, 1):
            c = ws2.cell(row=ri, column=ci, value=v)
            c.border = THIN
            if ri == 7:
                c.fill = hf("1B1B2F"); c.font = HDR_FNT(); c.alignment = CENTER
            else:
                c.fill = hf("F8F8F8" if ri%2==0 else "FFFFFF"); c.font = BOD_FNT(); c.alignment = WRAP_T

    # ── Sheet 3: Stats & Distribution ─────────────────────────────────────────
    ws3 = wb.create_sheet("Stats & Distribution")
    ws3.column_dimensions["A"].width = 32
    ws3.column_dimensions["B"].width = 16
    ws3.column_dimensions["C"].width = 16
    ws3.column_dimensions["D"].width = 16
    ws3.column_dimensions["E"].width = 16

    from collections import Counter
    tier_counts  = Counter(b["rarity_tier_code"] for b in blends)
    season_counts= Counter(b["season"] for b in blends)
    score_dist   = {"<20":0, "20–39":0, "40–59":0, "60+":0}
    for b in blends:
        sc = b["complexity_score"]
        if sc < 20:   score_dist["<20"] += 1
        elif sc < 40: score_dist["20–39"] += 1
        elif sc < 60: score_dist["40–59"] += 1
        else:         score_dist["60+"] += 1

    stat_sections = [
        ("TOTAL OVERVIEW", [
            ("Total House Blend Generated", len(blends)),
            ("Tier 1 — The Vanguard",       tier_counts.get("T1",0)),
            ("Tier 2 — The Curator's Reserve", tier_counts.get("T2",0)),
            ("Tier 3 — The Grand Artifact",  tier_counts.get("T3",0)),
            ("", ""),
            ("SEASON DISTRIBUTION", ""),
            ("Winter · The Dark Passage",  season_counts.get("Winter",0)),
            ("Summer · The Open Horizon",  season_counts.get("Summer",0)),
            ("Autumn · The Amber Descent", season_counts.get("Autumn",0)),
            ("Spring · The First Ascent",  season_counts.get("Spring",0)),
            ("", ""),
            ("COMPLEXITY SCORE DISTRIBUTION", ""),
            ("Score < 20 (T1 territory)",   score_dist["<20"]),
            ("Score 20–39 (T2 territory)",  score_dist["20–39"]),
            ("Score 40–59 (T3 territory)",  score_dist["40–59"]),
            ("Score 60+ (Ultra-rare T3)",   score_dist["60+"]),
            ("", ""),
            ("AVG COMPLEXITY SCORE", round(sum(b["complexity_score"] for b in blends)/max(len(blends),1),1)),
            ("AVG BODY (1–10)",      round(sum(b["body"] for b in blends)/max(len(blends),1),1)),
            ("AVG ACIDITY (1–10)",   round(sum(b["acidity"] for b in blends)/max(len(blends),1),1)),
            ("AVG SWEETNESS (1–10)", round(sum(b["sweetness"] for b in blends)/max(len(blends),1),1)),
            ("", ""),
            ("PRICING RANGE", ""),
            ("T1 Harga min/100g", f"Rp {min(b['price_per_100g'] for b in blends if b['rarity_tier_code']=='T1'):,}"),
            ("T1 Harga max/100g", f"Rp {max(b['price_per_100g'] for b in blends if b['rarity_tier_code']=='T1'):,}"),
            ("T2 Harga min/100g", f"Rp {min(b['price_per_100g'] for b in blends if b['rarity_tier_code']=='T2'):,}"),
            ("T2 Harga max/100g", f"Rp {max(b['price_per_100g'] for b in blends if b['rarity_tier_code']=='T2'):,}"),
            ("T3 Harga min/100g", f"Rp {min(b['price_per_100g'] for b in blends if b['rarity_tier_code']=='T3'):,}"),
            ("T3 Harga max/100g", f"Rp {max(b['price_per_100g'] for b in blends if b['rarity_tier_code']=='T3'):,}"),
            ("T3 Market Price count", sum(1 for b in blends if b.get("is_market_price"))),
        ]),
    ]

    row_cur = 1
    c = ws3.cell(row=row_cur, column=1, value="STATISTIK BLEND GENERATOR")
    c.font = Font(name="Arial", size=13, bold=True)
    row_cur += 1
    for section_name, rows in stat_sections:
        for metric, value in rows:
            row_cur += 1
            cm = ws3.cell(row=row_cur, column=1, value=metric)
            cv = ws3.cell(row=row_cur, column=2, value=value)
            if not metric and not value:
                continue
            if value == "" and metric:
                cm.font = Font(name="Arial", size=11, bold=True, color="1B1B2F")
                cm.fill = hf("E8E8E8")
            else:
                cm.font = Font(name="Arial", size=10, bold=(str(value).startswith("Rp")))
                cv.font = Font(name="Arial", size=10, bold=True)
                cm.fill = hf("F8F8F8" if row_cur%2==0 else "FFFFFF")
                cv.fill = hf("F8F8F8" if row_cur%2==0 else "FFFFFF")
            cm.border = THIN; cv.border = THIN; cv.alignment = CENTER

    # ── Sheet 4: DB Schema Mapping ─────────────────────────────────────────────
    ws4 = wb.create_sheet("DB Schema Mapping")
    ws4.column_dimensions["A"].width = 28
    ws4.column_dimensions["B"].width = 28
    ws4.column_dimensions["C"].width = 18
    ws4.column_dimensions["D"].width = 55

    mapping_hdr = ["Excel Column", "Django Model Field", "Model", "Keterangan"]
    for ci, h in enumerate(mapping_hdr, 1):
        c = ws4.cell(row=1, column=ci, value=h)
        c.fill = hf("1B1B2F"); c.font = HDR_FNT(); c.alignment = CENTER; c.border = THIN

    mappings = [
        ("sku",                   "sku",            "LumraConfigProductvariants", "SKU unik produk variant"),
        ("name",                  "name",           "LumraConfigProducts",         "Nama produk blend"),
        ("category",              "category_id",    "LumraConfigProducts",         "FK ke lumra_config_categories (House Blend)"),
        ("deskripsi",             "description",    "LumraConfigProducts",         "Deskripsi produk untuk UI"),
        ("rarity_tier",           "attr_value",     "LumraConfigProductattributeItems","attr_name='rarity_tier'"),
        ("complexity_score",      "attr_value",     "LumraConfigProductattributeItems","attr_name='complexity_score'"),
        ("season",                "attr_value",     "LumraConfigProductattributeItems","attr_name='season'"),
        ("season_universe",       "attr_value",     "LumraConfigProductattributeItems","attr_name='season_universe'"),
        ("tasting_notes",         "attr_value",     "LumraConfigProductattributeItems","attr_name='tasting_notes'"),
        ("texture_profile",       "attr_value",     "LumraConfigProductattributeItems","attr_name='texture_profile'"),
        ("flavour_wheel",         "attr_value",     "LumraConfigProductattributeItems","attr_name='flavour_wheel'"),
        ("body",                  "attr_value",     "LumraConfigProductattributeItems","attr_name='body'  (integer 1–10)"),
        ("acidity",               "attr_value",     "LumraConfigProductattributeItems","attr_name='acidity' (integer 1–10)"),
        ("sweetness",             "attr_value",     "LumraConfigProductattributeItems","attr_name='sweetness' (integer 1–10)"),
        ("price_per_100g",        "price_sell",     "LumraConfigProductvariants",  "Harga jual 100g (size_weight='100g')"),
        ("price_200g",            "price_sell",     "LumraConfigProductvariants",  "Harga jual 200g (size_weight='200g')"),
        ("price_500g",            "price_sell",     "LumraConfigProductvariants",  "Harga jual 500g (size_weight='500g')"),
        ("price_1kg",             "price_sell",     "LumraConfigProductvariants",  "Harga jual 1kg  (size_weight='1kg')"),
        ("is_market_price",       "attr_value",     "LumraConfigProductattributeItems","attr_name='is_market_price' (bool)"),
        ("monthly_limit",         "max_stock",      "LumraConfigProducts",         "Untuk T3: max_stock=50 (per outpost)"),
        ("resep_gramasi",         "instructions",   "ProductionRecipes",           "Instruksi resep untuk produksi"),
        ("rekomendasi_penyajian", "attr_value",     "LumraConfigProductattributeItems","attr_name='brew_method'"),
        ("origin_1/2/3/4",        "attr_value",     "LumraConfigProductattributeItems","attr_name='origin_1' dst"),
        ("complexity_factors",    "notes",          "ProductionRecipes",           "Catatan kompleksitas resep"),
        ("copywriting_packaging", "attr_value",     "LumraConfigProductattributeItems","attr_name='copy_packaging'"),
        ("copywriting_social",    "attr_value",     "LumraConfigProductattributeItems","attr_name='copy_social'"),
    ]

    for ri, (excel_col, field, model, note) in enumerate(mappings, 2):
        vals = [excel_col, field, model, note]
        for ci, v in enumerate(vals, 1):
            c = ws4.cell(row=ri, column=ci, value=v)
            c.border = THIN; c.alignment = WRAP_T
            c.fill = hf("F0F0F0" if ri%2==0 else "FFFFFF")
            if ci == 3:
                c.font = Font(name="Arial", size=9, color="1C3A5E", bold=True)
            elif ci == 1:
                c.font = Font(name="Courier New", size=9, color="1A1A1A")
            else:
                c.font = BOD_FNT()
        ws4.row_dimensions[ri].height = 24

    wb.save(output_path)
    print(f"✅ Excel saved: {output_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — JSON EXPORT (DB-ready)
# ═══════════════════════════════════════════════════════════════════════════════

def export_json(blends, output_path):
    """Export JSON siap import ke Django fixtures atau custom seeder."""
    fixtures = []
    for i, b in enumerate(blends, 1):
        # Product record
        fixtures.append({
            "model": "lumra_config.products",
            "pk": f"hb_{i}",
            "fields": {
                "name":        b["name"],
                "description": b["deskripsi"],
                "is_active":   True,
                "has_expiry":  False,
                "track_batch": True,
                "max_stock":   b["monthly_limit"] if b["monthly_limit"] else 9999,
                "min_stock":   1,
            }
        })
        # Variant records (4 sizes)
        for size, price_key in [("100g","price_per_100g"),("200g","price_200g"),("500g","price_500g"),("1kg","price_1kg")]:
            sku_full = f"{b['sku']}-{size.replace('g','G').replace('kg','KG')}"
            fixtures.append({
                "model": "lumra_config.productvariants",
                "pk": f"{b['sku']}_{size}",
                "fields": {
                    "sku":        sku_full,
                    "size_weight": size,
                    "price_buy":  round(b[price_key] * 0.65),
                    "price_sell": b[price_key],
                    "product":    f"hb_{i}",
                }
            })
        # Attribute items (metadata)
        attrs = {
            "season":            b["season"],
            "season_universe":   b["season_universe"],
            "rarity_tier":       b["rarity_tier"],
            "rarity_label":      b["rarity_label"],
            "complexity_score":  str(b["complexity_score"]),
            "tasting_notes":     b["tasting_notes"],
            "texture_profile":   b["texture_profile"],
            "flavour_wheel":     b["flavour_wheel"],
            "body":              str(b["body"]),
            "acidity":           str(b["acidity"]),
            "sweetness":         str(b["sweetness"]),
            "brew_method":       b["rekomendasi_penyajian"],
            "is_market_price":   str(b["is_market_price"]),
            "monthly_limit":     str(b["monthly_limit"]) if b["monthly_limit"] else "unlimited",
            "copy_packaging":    b["copywriting_packaging"],
            "copy_social":       b["copywriting_social"],
        }
        for attr_name, attr_val in attrs.items():
            fixtures.append({
                "model": "lumra_config.productattribute_items",
                "fields": {
                    "variant": f"{b['sku']}_100g",
                    "attr_name":  attr_name,
                    "attr_value": attr_val,
                }
            })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON saved: {output_path}  ({len(fixtures):,} fixture records)")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  KAFE NUSANTARA — THE GRAND BLEND ENGINE v1.0")
    print("  7 Billion Possibilities → 9,999 Are Chosen")
    print("=" * 70)

    TARGET_HB    = 7_463
    OUT_EXCEL    = "/mnt/user-data/outputs/kopi_9999_MASTER.xlsx"
    OUT_JSON     = "/mnt/user-data/outputs/kopi_9999_db.json"
    OUT_SCRIPT   = "/mnt/user-data/outputs/grand_blend_engine.py"

    print(f"\n📐 Rarity Distribution Plan:")
    print(f"   T1 Vanguard       (~60%): {int(TARGET_HB*0.60):,} blends")
    print(f"   T2 Curator's Reserve (~30%): {int(TARGET_HB*0.30):,} blends")
    print(f"   T3 Grand Artifact  (~10%): {TARGET_HB - int(TARGET_HB*0.60) - int(TARGET_HB*0.30):,} blends")
    print(f"   Total HB target         : {TARGET_HB:,}")
    print(f"   + Existing SO           : 2,536")
    print(f"   = Grand Total           : {TARGET_HB + 2536:,} / 9,999\n")

    print("🚀 Generating House Blends...")
    blends = generate_all_blends(TARGET_HB)

    print(f"\n📊 Generation Complete:")
    from collections import Counter
    tier_dist = Counter(b["rarity_tier_code"] for b in blends)
    season_dist = Counter(b["season"] for b in blends)
    t3_blends = [b for b in blends if b["rarity_tier_code"] == "T3"]

    print(f"   Total generated: {len(blends):,}")
    for tc, cnt in sorted(tier_dist.items()):
        print(f"   {tc}: {cnt:,}")
    print(f"\n   Season breakdown:")
    for s, cnt in season_dist.most_common():
        print(f"   · {s}: {cnt:,}")

    if t3_blends:
        avg_t3_score = sum(b["complexity_score"] for b in t3_blends) / len(t3_blends)
        max_t3 = max(t3_blends, key=lambda x: x["complexity_score"])
        print(f"\n   T3 avg complexity score: {avg_t3_score:.1f}")
        print(f"   T3 highest score blend : '{max_t3['name']}' ({max_t3['complexity_score']})")
        print(f"   T3 price range         : Rp {min(b['price_per_100g'] for b in t3_blends):,} – Rp {max(b['price_per_100g'] for b in t3_blends):,} / 100g")
        market_price_count = sum(1 for b in t3_blends if b.get("is_market_price"))
        print(f"   T3 Market Price items  : {market_price_count}")

    print(f"\n💾 Exporting Excel (4 sheets)...")
    export_excel(blends, OUT_EXCEL)

    print(f"\n💾 Exporting JSON (Django fixtures)...")
    export_json(blends, OUT_JSON)

    import shutil
    shutil.copy(__file__, OUT_SCRIPT)
    print(f"✅ Script saved: {OUT_SCRIPT}")

    print(f"\n{'=' * 70}")
    print(f"  ✅ DONE — The Grand Blend Engine")
    print(f"  · {len(blends):,} new House Blend generated")
    print(f"  · + 2,536 existing Single Origin = {len(blends)+2536:,} total menu")
    print(f"  · Output: kopi_9999_MASTER.xlsx + kopi_9999_db.json")
    print(f"{'=' * 70}")
