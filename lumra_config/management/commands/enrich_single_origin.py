"""
Kafe Nusantara — Single Origin Excel Enricher
Membaca file Excel, memperkaya dengan logika yang sama seperti generator dummy,
lalu menghasilkan INSERT ke PostgreSQL (sama persis strukturnya).
"""

import io
import re
import sys
import os
import random
import argparse
from datetime import datetime, timezone, timedelta

try:
    import pandas as pd
except ImportError:
    print("❌ pandas tidak ditemukan. Install: pip install pandas openpyxl")
    sys.exit(1)

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("❌ psycopg2 tidak ditemukan. Install: pip install psycopg2-binary")
    sys.exit(1)

random.seed(20240101)

# ═══════════════════════════════════════════════════════════════════════════════
# DB CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME",     "lumra_set_allegra"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     os.getenv("DB_PORT",     "5432"),
}

SIZES = ["100g", "200g", "500g", "1kg"]

# ═══════════════════════════════════════════════════════════════════════════════
# MAPPING: ORIGIN → KEY & ISLAND
# (diperluas untuk cover semua origin di Excel)
# ═══════════════════════════════════════════════════════════════════════════════

ORIGIN_MAP = {
    # display name (lowercase) → (origin_key, island)
    "wanoja kamojang":          ("wanoja_kamojang",  "Jawa"),
    "java sindoro":             ("sindoro",           "Jawa"),
    "java temanggung":          ("temanggung",        "Jawa"),
    "java ciwidey":             ("ciwidey",           "Jawa"),
    "aceh gayo":                ("aceh_gayo",         "Sumatera"),
    "sidikalang":               ("sidikalang",        "Sumatera"),
    "mandheling":               ("mandheling",        "Sumatera"),
    "lintong onan":             ("lintong",           "Sumatera"),
    "lintong":                  ("lintong",           "Sumatera"),
    "toraja sapan":             ("sapan",             "Sulawesi"),
    "toraja kalosi":            ("kalosi",            "Sulawesi"),
    "flores manggarai":         ("flores_manggarai",  "Flores"),
    "flores bajawa":            ("bajawa",            "Flores"),
    "bali kintamani":           ("bali_kintamani",    "Bali"),
    "bali ulian":               ("bali_ulian",        "Bali"),
    "dampit malang":            ("dampit",            "Jawa"),
    "gunung halu":              ("gunung_halu",       "Jawa"),
    "java puntang":             ("puntang",           "Jawa"),
    "java preanger":            ("preanger",          "Jawa"),
    "java manglayang":          ("manglayang",        "Jawa"),
    "kerinci kayu aro":         ("kayu_aro",          "Sumatera"),
    "solok radjo":              ("solok_radjo",       "Sumatera"),
    "papua dogiyai":            ("dogiyai",           "Papua"),
    "papua wamena":             ("wamena",            "Papua"),
    "sembalun rinjani":         ("rinjani",           "Lombok"),
    "semeru":                   ("semeru",            "Jawa"),
    "java ijen raung":          ("ijen_raung",        "Jawa"),
    "java garut":               ("garut",             "Jawa"),
    "bengkulu":                 ("bengkulu",          "Sumatera"),
    "bukit barisan":            ("bukit_barisan",     "Sumatera"),
    "arjuno":                   ("arjuno",            "Jawa"),
    "lampung robusta premium":  ("lampung",           "Sumatera"),
    "lampung robusta":          ("lampung",           "Sumatera"),
    "temanggung":               ("temanggung",        "Jawa"),
}

# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

PROCESS_NORM = {
    "washed":       "Washed",
    "natural":      "Natural",
    "honey":        "Honey",
    "semi washed":  "Semi-Washed",
    "semi-washed":  "Semi-Washed",
    "wet hulled":   "Wet-Hulled",
    "wet-hulled":   "Wet-Hulled",
    "anaerobic":    "Anaerobic",
    "wine":         "Wine",
}

ROAST_NORM = {
    "light roast":  "Light",
    "medium roast": "Medium",
    "dark roast":   "Dark",
    "light":        "Light",
    "medium":       "Medium",
    "dark":         "Dark",
}

# ═══════════════════════════════════════════════════════════════════════════════
# FLAVOR ENGINE (sama persis dari generator)
# ═══════════════════════════════════════════════════════════════════════════════

FLAVOR_DEFAULTS = {
    ("Washed",      "Light"):  ["citrus", "jasmine", "peach", "lemon zest"],
    ("Washed",      "Medium"): ["brown sugar", "hazelnut", "almond", "milk chocolate"],
    ("Washed",      "Dark"):   ["dark chocolate", "molasses", "smoky caramel"],
    ("Natural",     "Light"):  ["blueberry", "strawberry", "tropical fruit", "hibiscus"],
    ("Natural",     "Medium"): ["dark chocolate", "berry jam", "dried fig", "molasses"],
    ("Natural",     "Dark"):   ["dark berry", "espresso", "tar", "charcoal"],
    ("Honey",       "Light"):  ["apricot", "honeysuckle", "white grape", "floral"],
    ("Honey",       "Medium"): ["honey", "toffee", "dried apricot", "maple syrup"],
    ("Honey",       "Dark"):   ["burnt caramel", "toffee", "smoked almond"],
    ("Semi-Washed", "Light"):  ["mandarin", "oolong tea", "light caramel", "papaya"],
    ("Semi-Washed", "Medium"): ["milk caramel", "vanilla", "roasted nut", "apricot"],
    ("Semi-Washed", "Dark"):   ["roasted grain", "dark caramel", "walnut", "intense spice"],
    ("Wet-Hulled",  "Light"):  ["herb", "cedar", "tobacco leaf", "lime", "green pepper"],
    ("Wet-Hulled",  "Medium"): ["earthy", "tobacco", "spice", "woody", "leather"],
    ("Wet-Hulled",  "Dark"):   ["peat", "bark", "dark tobacco", "clove", "intense earth"],
    ("Anaerobic",   "Light"):  ["passion fruit", "lychee", "raspberry", "rum raisin", "cola"],
    ("Anaerobic",   "Medium"): ["fermented fruit", "tropical punch", "cacao nib", "tamarind"],
    ("Anaerobic",   "Dark"):   ["black cherry", "smoke", "dark rum", "fermented cocoa"],
    ("Wine",        "Light"):  ["wine", "blackcurrant", "dark cherry", "grape must", "plum"],
    ("Wine",        "Medium"): ["port wine", "dark plum", "roasted grape", "balsamic"],
    ("Wine",        "Dark"):   ["aged wine", "tobacco", "dark espresso", "smoked plum"],
}

WHEEL_KEYWORDS = {
    "Fruity":     ["fruit", "berry", "citrus", "plum", "fig", "apricot", "peach", "lychee", "passion", "tropical", "lemon"],
    "Sweet":      ["caramel", "honey", "toffee", "molasses", "sugar", "maple", "vanilla"],
    "Nutty":      ["nut", "almond", "hazelnut", "walnut"],
    "Chocolatey": ["chocolate", "cocoa", "cacao", "mocha"],
    "Spicy":      ["spice", "cinnamon", "clove", "pepper", "rum"],
    "Floral":     ["floral", "jasmine", "rose", "honeysuckle", "bloom"],
    "Earthy":     ["earthy", "mushroom", "wood", "woody", "peat", "bark", "herb", "cedar", "tobacco"],
    "Roasted":    ["smoke", "roast", "charcoal", "espresso", "tar", "dark roast"],
    "Fermented":  ["wine", "rum", "aged", "ferment", "balsamic", "raisin", "cola"],
}

DESSERT_MAP = {
    "Chocolatey": ["Chocolate Lava Cake", "Dark Brownies", "Tiramisu"],
    "Nutty":      ["Almond Croissant", "Hazelnut Tart", "Tiramisu"],
    "Fruity":     ["Fruit Tart", "Berry Cheesecake", "Pavlova"],
    "Spicy":      ["Cinnamon Roll", "Carrot Cake", "Speculaas"],
    "Earthy":     ["Tiramisu", "Matcha Cake", "Panna Cotta"],
    "Floral":     ["French Macarons", "Earl Grey Cake", "Rose Tart"],
    "Sweet":      ["Crème Brûlée", "Honey Toast", "Flan"],
    "Roasted":    ["Espresso Brownies", "Mocha Layer Cake", "Tiramisu"],
    "Fermented":  ["Dark Chocolate Truffles", "Rum Cake", "Aged Cheese Tart"],
}

PROCESS_BREW = {
    "Washed":     "V60 · Pour Over",
    "Natural":    "AeroPress · French Press",
    "Honey":      "V60 · AeroPress",
    "Semi-Washed":"French Press · AeroPress",
    "Wet-Hulled": "French Press · Moka Pot",
    "Anaerobic":  "AeroPress · Espresso",
    "Wine":       "AeroPress · Ristretto",
}

ORIGIN_MULT = {
    "dogiyai":       1.35, "wamena":      1.35, "rinjani":    1.25,
    "solok_radjo":   1.20, "kayu_aro":    1.18, "bali_kintamani": 1.15,
    "bajawa":        1.15,
}

PRICE_BASE_SINGLE = {
    "T1": 40_000, "T2": 70_000, "T3": 120_000,
}

PROCESS_MULT = {
    "Washed": 1.0, "Natural": 1.15, "Honey": 1.12, "Semi-Washed": 1.10,
    "Wet-Hulled": 1.08, "Anaerobic": 1.45, "Wine": 1.50,
}

SIZE_MULT = {"100g": 1.0, "200g": 1.85, "500g": 4.20, "1kg": 7.80}

ROAST_SCORES = {"Light": 1, "Medium": 2, "Dark": 3}
SWEETNESS_BY_PROC = {
    "Natural": 7, "Honey": 6, "Wine": 6, "Anaerobic": 5,
    "Washed": 4, "Semi-Washed": 5, "Wet-Hulled": 4,
}

ISLAND_SEASON = {
    "Sumatera": ["Winter", "Autumn"],
    "Jawa":     ["Autumn", "Spring"],
    "Bali":     ["Summer", "Spring"],
    "Flores":   ["Summer", "Autumn"],
    "Lombok":   ["Summer", "Spring"],
    "Sulawesi": ["Winter", "Autumn"],
    "Papua":    ["Winter", "Summer"],
}

SEASON_UNIVERSE = {
    "Winter": "The Dark Passage",
    "Summer": "The Open Horizon",
    "Autumn": "The Amber Descent",
    "Spring": "The First Ascent",
}

RARE_ORIGINS = {"dogiyai", "wamena", "rinjani", "solok_radjo", "kayu_aro", "bajawa", "bali_kintamani"}

# SKU counter
_sku_counters = {"SO": 0}

def make_sku_single(origin_key, process_code, roast_code):
    _sku_counters["SO"] += 1
    proc_abbr = {"Washed":"WS","Natural":"NA","Honey":"HN","Semi-Washed":"SW",
                 "Wet-Hulled":"WH","Anaerobic":"AN","Wine":"WN"}.get(process_code, "XX")
    roast_abbr = {"Light":"L","Medium":"M","Dark":"D"}.get(roast_code, "X")
    origin_abbr = origin_key.upper()[:6].replace("_","")
    return f"SO-{origin_abbr}-{proc_abbr}{roast_abbr}-{_sku_counters['SO']:05d}"

def get_notes(process, roast):
    return FLAVOR_DEFAULTS.get((process, roast), ["balanced", "smooth", "rich"])

def notes_to_wheel(notes_list):
    text = " ".join(notes_list).lower()
    scores = {k: sum(1 for kw in kws if kw in text) for k, kws in WHEEL_KEYWORDS.items()}
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = [k for k, v in top[:3] if v > 0]
    return ", ".join(result) if result else "Nutty, Chocolatey"

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

def compute_price_single(origin_key, process, roast, tier_code):
    rare = origin_key in RARE_ORIGINS
    base = PRICE_BASE_SINGLE[tier_code]
    if rare:
        base = int(base * 1.20)
    proc_m = PROCESS_MULT.get(process, 1.0)
    orig_m = ORIGIN_MULT.get(origin_key, 1.0)
    p100 = int(base * proc_m * orig_m)
    p100 = max(round(p100 / 5000) * 5000, 35_000)
    return {s: int(p100 * m) for s, m in SIZE_MULT.items()}, p100

def determine_tier(origin_key, process):
    is_exotic_proc = process in ("Anaerobic", "Wine")
    is_rare_origin = origin_key in RARE_ORIGINS
    if is_exotic_proc and is_rare_origin:
        return "T3"
    if is_exotic_proc or is_rare_origin:
        return "T2"
    return "T1"

TIER_META = {
    "T1": {"name": "Tier 1 — The Vanguard",         "label": "Standard"},
    "T2": {"name": "Tier 2 — The Curator's Reserve", "label": "Premium"},
    "T3": {"name": "Tier 3 — The Grand Artifact",    "label": "Mythic · Limited"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# ENRICH SINGLE ROW
# ═══════════════════════════════════════════════════════════════════════════════

def enrich_row(row, idx):
    name_raw = str(row["name"]).strip()
    process_raw = str(row["PROCESSES"]).strip().lower()
    roast_raw = str(row["ROASTS"]).strip().lower()
    category = str(row["category_name"]).strip()

    # Normalize process & roast
    process = PROCESS_NORM.get(process_raw, "Washed")
    roast   = ROAST_NORM.get(roast_raw, "Medium")

    # Extract origin from name
    origin_display = None
    origin_key = None
    island = "Jawa"

    for key_display, (ok, isl) in ORIGIN_MAP.items():
        if key_display in name_raw.lower():
            origin_display = key_display.title()
            origin_key = ok
            island = isl
            break

    if not origin_key:
        # fallback: use name as-is
        origin_display = name_raw
        origin_key = re.sub(r'\W+', '_', name_raw.lower())[:20]
        island = "Jawa"

    # Season from island
    season = random.choice(ISLAND_SEASON.get(island, ["Autumn"]))
    season_universe = SEASON_UNIVERSE[season]

    # Tier
    tier_code = determine_tier(origin_key, process)
    tier_m = TIER_META[tier_code]

    # Flavor
    notes = get_notes(process, roast)
    tasting_notes = ", ".join(notes)
    wheel = notes_to_wheel(notes)
    dessert = wheel_to_dessert(wheel)

    # Brew
    brew = PROCESS_BREW.get(process, "AeroPress · V60")

    # Sensory scores
    body      = {"Light": 4, "Medium": 6, "Dark": 8}[roast]
    acidity   = {"Light": 7, "Medium": 5, "Dark": 3}[roast]
    sweetness = SWEETNESS_BY_PROC.get(process, 5)

    # Pricing
    prices, p100 = compute_price_single(origin_key, process, roast, tier_code)

    # SKU
    sku_base = make_sku_single(origin_key, process, roast)
    barcode  = sku_base

    # Texture
    texture = {"Light": "Silky & Clean", "Medium": "Smooth & Balanced", "Dark": "Bold & Heavy"}[roast]

    # Monthly limit
    monthly_limit = 50 if tier_code == "T3" else None
    is_market_price = tier_code == "T3"

    # Description
    type_label = "Robusta" if origin_key in ("lampung", "dampit") else "Arabica"
    desc = (
        f"Single Origin {type_label} dari {origin_display.title()}, "
        f"diproses dengan metode {process} dan di-roast {roast}. "
        f"Tasting notes: {tasting_notes}. "
        f"Cocok disajikan dengan {dessert}. "
        f"Brew method: {brew}. "
        f"— {season_universe} · {season} Collection."
    )

    # Recipe / gramasi
    recipe = f"{name_raw} 100% | 1000g single origin"

    return {
        "name":           name_raw,
        "sku_base":       sku_base,
        "barcode":        barcode,
        "description":    desc,
        "category":       category,
        "season":         season,
        "season_universe":season_universe,
        "tier_code":      tier_code,
        "tier_name":      tier_m["name"],
        "tier_label":     tier_m["label"],
        "origin_display": origin_display.title() if origin_display else name_raw,
        "origin_key":     origin_key,
        "island":         island,
        "process":        process,
        "roast":          roast,
        "tasting_notes":  tasting_notes,
        "flavour_wheel":  wheel,
        "dessert":        dessert,
        "brew_method":    brew,
        "body":           body,
        "acidity":        acidity,
        "sweetness":      sweetness,
        "texture":        texture,
        "price_100g":     prices["100g"],
        "price_200g":     prices["200g"],
        "price_500g":     prices["500g"],
        "price_1kg":      prices["1kg"],
        "is_market_price":is_market_price,
        "monthly_limit":  monthly_limit,
        "recipe":         recipe,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# DB HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(autocommit=False)
    return conn

def fetch_fk_ids(conn):
    cur = conn.cursor()
    ids = {}

    cur.execute("SELECT name, id FROM lumra_config_categories WHERE name IN ('House Blend','Single Origin','Single Origin Series')")
    for name, id_ in cur.fetchall():
        ids[f"cat_{name.lower().replace(' ','_')}"] = id_

    cur.execute("SELECT id FROM lumra_config_taxes WHERE name = 'PPN 11%' LIMIT 1")
    row = cur.fetchone()
    ids["tax_ppn11"] = row[0] if row else None

    cur.execute("SELECT id FROM lumra_config_units WHERE name = 'Gram' LIMIT 1")
    row = cur.fetchone()
    ids["unit_gram"] = row[0] if row else None

    cur.close()

    # Resolve category: prefer Single Origin Series → Single Origin → House Blend
    ids["cat_target"] = (
        ids.get("cat_single_origin_series")
        or ids.get("cat_single_origin")
        or ids.get("cat_house_blend")
    )
    return ids

def fetch_existing_products_by_barcodes(conn, barcodes):
    if not barcodes:
        return {}
    cur = conn.cursor()
    cur.execute("SELECT id, barcode FROM lumra_config_products WHERE barcode = ANY(%s)", (barcodes,))
    rows = cur.fetchall()
    cur.close()
    return {b: pid for pid, b in rows}

def fetch_existing_variants_by_skus(conn, skus):
    if not skus:
        return {}
    cur = conn.cursor()
    cur.execute("SELECT id, sku FROM lumra_config_productvariants WHERE sku = ANY(%s)", (skus,))
    rows = cur.fetchall()
    cur.close()
    return {sku: vid for vid, sku in rows}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def run(excel_path, dry_run, batch_size, skip_attrs, skip_recipes):
    print("═" * 65)
    print("  KAFE NUSANTARA — Single Origin Excel Enricher")
    print(f"  File: {excel_path}")
    print("═" * 65)

    # 1. Read Excel
    df = pd.read_excel(excel_path)
    print(f"\n📄 Loaded {len(df):,} rows from Excel")

    # 2. Enrich all rows
    print("🔧 Enriching products...")
    enriched = []
    for idx, row in df.iterrows():
        try:
            e = enrich_row(row, idx)
            enriched.append(e)
        except Exception as ex:
            print(f"  ⚠️  Row {idx} error: {ex} | name={row.get('name','?')}")

    print(f"  ✅ {len(enriched):,} products enriched")

    # Tier breakdown
    tier_counts = {}
    for e in enriched:
        tier_counts[e["tier_code"]] = tier_counts.get(e["tier_code"], 0) + 1
    for tc, cnt in sorted(tier_counts.items()):
        print(f"     {TIER_META[tc]['name']}: {cnt:,}")

    if dry_run:
        print("\n[DRY RUN] Sample enriched data:")
        for e in enriched[:3]:
            print(f"  • {e['name']}")
            print(f"    SKU: {e['sku_base']} | Tier: {e['tier_code']} | Process: {e['process']} | Roast: {e['roast']}")
            print(f"    Tasting: {e['tasting_notes']}")
            print(f"    Wheel: {e['flavour_wheel']} | Dessert: {e['dessert']}")
            print(f"    Brew: {e['brew_method']}")
            print(f"    Price 100g: Rp {e['price_100g']:,} | 1kg: Rp {e['price_1kg']:,}")
            print()
        print("[DRY RUN] Tidak ada insert ke DB.")
        return

    # 3. Connect DB
    print(f"\n📡 Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}...")
    try:
        conn = get_connection()
        print("  ✅ Connected")
    except Exception as ex:
        print(f"  ❌ {ex}")
        sys.exit(1)

    fk_ids = fetch_fk_ids(conn)
    print(f"  Category target ID : {fk_ids.get('cat_target')}")
    print(f"  Tax ID             : {fk_ids.get('tax_ppn11')}")
    print(f"  Unit ID            : {fk_ids.get('unit_gram')}")

    if not fk_ids.get("cat_target"):
        print("  ❌ Tidak ada category 'Single Origin Series' / 'Single Origin' / 'House Blend'")
        sys.exit(1)

    total_products = 0
    total_variants = 0
    total_attrs    = 0
    now = datetime.now(timezone.utc)

    # 4. Process in batches
    for batch_start in range(0, len(enriched), batch_size):
        batch = enriched[batch_start: batch_start + batch_size]

        # ── Insert products ──────────────────────────────────────────────────
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
                    e["name"], e["description"][:500], True, False, True,
                    0, 9999, now, now,
                    fk_ids["cat_target"],
                    fk_ids.get("tax_ppn11"),
                    fk_ids.get("unit_gram"),
                    None,
                    e["barcode"],
                )
                for e in batch
            ],
            page_size=500,
        )
        returning = cur.fetchall()
        conn.commit()
        cur.close()
        total_products += len(returning)

        barcodes = [e["barcode"] for e in batch]
        barcode_to_pid = fetch_existing_products_by_barcodes(conn, barcodes)

        # ── Insert variants ──────────────────────────────────────────────────
        variant_rows = []
        for e in batch:
            pid = barcode_to_pid.get(e["barcode"])
            if not pid:
                continue
            for size in SIZES:
                price_key = f"price_{size}"
                psell = e.get(price_key, 35_000)
                pbuy  = int(psell * 0.65)
                sku   = f"{e['sku_base']}-{size}"
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
            [(sku, pid, size, pbuy, psell, now) for sku, pid, size, pbuy, psell in variant_rows],
            page_size=1000,
        )
        var_ret = cur.fetchall()
        conn.commit()
        cur.close()
        total_variants += len(var_ret)

        batch_skus = [sku for sku, *_ in variant_rows]
        sku_to_vid = fetch_existing_variants_by_skus(conn, batch_skus)

        # ── Insert attributes ────────────────────────────────────────────────
        if not skip_attrs:
            attr_rows = []
            for e in batch:
                sku_100g = f"{e['sku_base']}-100g"
                vid = sku_to_vid.get(sku_100g)
                if not vid:
                    continue
                attrs = {
                    "season":              e["season"],
                    "season_universe":     e["season_universe"],
                    "rarity_tier":         e["tier_name"],
                    "rarity_label":        e["tier_label"],
                    "origin":              e["origin_display"],
                    "island":              e["island"],
                    "process":             e["process"],
                    "roast":               e["roast"],
                    "tasting_notes":       e["tasting_notes"],
                    "texture_profile":     e["texture"],
                    "flavour_wheel":       e["flavour_wheel"],
                    "body":                str(e["body"]),
                    "acidity":             str(e["acidity"]),
                    "sweetness":           str(e["sweetness"]),
                    "brew_method":         e["brew_method"],
                    "recommended_dessert": e["dessert"],
                    "is_market_price":     str(e["is_market_price"]),
                    "monthly_limit":       str(e["monthly_limit"]) if e["monthly_limit"] else "unlimited",
                }
                for aname, aval in attrs.items():
                    attr_rows.append((vid, aname, str(aval)[:255], now))

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
                    page_size=2000,
                )
                total_attrs += len(attr_rows)
                conn.commit()
                cur.close()

        # ── Insert recipes ───────────────────────────────────────────────────
        if not skip_recipes and fk_ids.get("unit_gram"):
            recipe_rows = []
            for e in batch:
                recipe_rows.append((
                    e["name"][:255],
                    e["description"][:500],
                    e["recipe"][:500],
                    int(e["price_100g"] * 0.60),
                ))
            try:
                cur = conn.cursor()
                psycopg2.extras.execute_values(
                    cur,
                    """
                    INSERT INTO production_recipes
                        (name, description, instructions, yield_quantity,
                         preparation_time, total_cost, cost_per_unit,
                         is_archived, created_at, updated_at,
                         yield_unit_id)
                    VALUES %s
                    ON CONFLICT (name) DO NOTHING
                    """,
                    [
                        (r[0], r[1], r[2], 1, 5, r[3], r[3], False, now, now, fk_ids.get("unit_gram"))
                        for r in recipe_rows
                    ],
                    page_size=500,
                )
                conn.commit()
                cur.close()
            except Exception as ex:
                conn.rollback()
                print(f"  ⚠️  Recipe insert skipped: {ex}")

        done = min(batch_start + batch_size, len(enriched))
        print(f"  ✅ Batch {batch_start+1}–{done}: {len(returning)} products, {len(var_ret)} variants")

    conn.close()

    print()
    print("═" * 65)
    print("  📊 FINAL STATISTICS — Single Origin Insert")
    print("═" * 65)
    print(f"  ✦ {'Products inserted':<35} {total_products:>10,}")
    print(f"  ✦ {'Variants inserted (4 sizes each)':<35} {total_variants:>10,}")
    print(f"  ✦ {'Attribute items inserted':<35} {total_attrs:>10,}")
    print("═" * 65)
    print()
    print("  💡 Verifikasi:")
    print("     SELECT COUNT(*) FROM lumra_config_products")
    print("       WHERE category_id IN (SELECT id FROM lumra_config_categories WHERE name ILIKE '%single origin%');")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single Origin Excel → PostgreSQL")
    parser.add_argument("--excel",        default="D:/APPS/Project/lumra/lumra_config/management/commands/kopi_claude.xlsx",
                        help="Path ke file Excel")
    parser.add_argument("--dry-run",      action="store_true",
                        help="Preview enrichment tanpa insert ke DB")
    parser.add_argument("--batch-size",   type=int, default=200)
    parser.add_argument("--skip-attrs",   action="store_true")
    parser.add_argument("--skip-recipes", action="store_true")
    parser.add_argument("--db-name",      type=str, default=None)
    parser.add_argument("--db-user",      type=str, default=None)
    parser.add_argument("--db-password",  type=str, default=None)
    parser.add_argument("--db-host",      type=str, default=None)
    parser.add_argument("--db-port",      type=str, default=None)
    args = parser.parse_args()

    if args.db_name:     DB_CONFIG["dbname"]   = args.db_name
    if args.db_user:     DB_CONFIG["user"]      = args.db_user
    if args.db_password: DB_CONFIG["password"]  = args.db_password
    if args.db_host:     DB_CONFIG["host"]      = args.db_host
    if args.db_port:     DB_CONFIG["port"]      = args.db_port

    run(
        excel_path   = args.excel,
        dry_run      = args.dry_run,
        batch_size   = args.batch_size,
        skip_attrs   = args.skip_attrs,
        skip_recipes = args.skip_recipes,
    )