"""
╔══════════════════════════════════════════════════════════════╗
║      KAFE NUSANTARA — BLEND SKU GENERATOR                   ║
║      1.000 Parent Blend + 20.000 Child Retail SKU           ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import csv
import random
import itertools
from pathlib import Path

random.seed(42)  # reproducible output

# ─────────────────────────────────────────────
# 1. LOAD & PARSE DATA MASTER DARI menu.md
# ─────────────────────────────────────────────

def parse_menu_md(filepath: str) -> list[dict]:
    beans = []
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[1:]:  # skip header
        parts = [p.strip() for p in line.strip().split("\t")]
        if len(parts) < 5:
            continue
        beans.append({
            "type":       parts[0],
            "origin":     parts[1],
            "region":     parts[2],
            "roast":      parts[3].replace(" Roast", ""),
            "processing": parts[4],
        })
    return beans

BEANS = parse_menu_md("/mnt/user-data/uploads/menu.md")
print(f"✅ Data master loaded: {len(BEANS)} bean profiles")

# ─────────────────────────────────────────────
# 2. KAMUS FLAVOR & DESKRIPSI
# ─────────────────────────────────────────────

FLAVOR_PROFILE = {
    # (roast, processing) -> flavor notes
    ("Light",  "Washed"):      ["citrus", "jasmine", "peach", "lemon zest", "bergamot", "green tea"],
    ("Light",  "Honey"):       ["apricot", "honeysuckle", "white grape", "floral", "pear", "nectarine"],
    ("Light",  "Natural"):     ["blueberry", "strawberry", "tropical fruit", "hibiscus", "watermelon"],
    ("Light",  "Anaerobic"):   ["passion fruit", "lychee", "raspberry", "rum raisin", "cola"],
    ("Light",  "Wine"):        ["wine", "blackcurrant", "dark cherry", "grape must", "plum"],
    ("Light",  "SemiWashed"):  ["mandarin", "oolong tea", "light caramel", "papaya"],
    ("Light",  "WetHulled"):   ["herb", "cedar", "tobacco leaf", "lime", "green pepper"],
    ("Medium", "Washed"):      ["brown sugar", "hazelnut", "caramel", "milk chocolate", "almond"],
    ("Medium", "Honey"):       ["honey", "toffee", "dried apricot", "maple syrup", "macadamia"],
    ("Medium", "Natural"):     ["dark chocolate", "berry jam", "dried fig", "molasses", "prune"],
    ("Medium", "Anaerobic"):   ["fermented fruit", "tropical punch", "cacao nib", "tamarind"],
    ("Medium", "Wine"):        ["port wine", "dark plum", "roasted grape", "balsamic", "espresso"],
    ("Medium", "SemiWashed"):  ["milk caramel", "vanilla", "roasted nut", "apricot jam"],
    ("Medium", "WetHulled"):   ["earthy", "tobacco", "spice", "woody", "leather", "mushroom"],
    ("Dark",   "Washed"):      ["dark roast", "smoky caramel", "bitter chocolate", "molasses"],
    ("Dark",   "Honey"):       ["burnt caramel", "toffee", "smoked almond", "dark sugar"],
    ("Dark",   "Natural"):     ["dark berry", "espresso", "tar", "charcoal", "licorice"],
    ("Dark",   "Anaerobic"):   ["black cherry", "smoke", "dark rum", "fermented cocoa"],
    ("Dark",   "Wine"):        ["aged wine", "tobacco", "dark espresso", "smoked plum"],
    ("Dark",   "SemiWashed"):  ["roasted grain", "dark caramel", "walnut", "intense spice"],
    ("Dark",   "WetHulled"):   ["peat", "bark", "dark tobacco", "clove", "intense earth"],
}

TEXTURE_MAP = {
    "Light":  ["Light Body", "Tea-like", "Silky", "Delicate", "Clean"],
    "Medium": ["Medium Body", "Smooth", "Balanced", "Velvety", "Round"],
    "Dark":   ["Heavy Body", "Bold", "Full Body", "Thick", "Syrupy"],
}

BREWING_SUGGEST = {
    "Light":  ["Best for V60", "Ideal for Chemex", "Cocok untuk AeroPress", "Pour Over Recommended"],
    "Medium": ["Versatile for Espresso & Filter", "Best for Moka Pot", "Cocok untuk French Press & Espresso"],
    "Dark":   ["Best for Espresso", "Ideal untuk Ristretto", "Cocok untuk Cold Brew", "Best for Batch Brew"],
}

# Nama komponen komersial
BLEND_PREFIXES = [
    "Archipelago", "Nusantara", "Equator", "Volcano", "Sunrise", "Harvest",
    "Summit", "Golden", "Ancient", "Heritage", "Timeless", "Ritual",
    "Twilight", "Dawn", "Ember", "Horizon", "Whisper", "Highland",
    "Celestial", "Mystic", "Sacred", "Serenity", "Elysian", "Primal",
    "Midnight", "Amber", "Copper", "Bronze", "Velvet", "Silk",
]

BLEND_SUFFIXES = [
    "Reserve", "Estate", "Collection", "Series", "Edition", "Signature",
    "Crest", "Ridge", "Valley", "Peak", "Spring", "Blend", "Fusion",
    "Journey", "Story", "Chapter", "Craft", "Select", "Origin", "Legacy",
]

SPECIALITY_PREFIX = [
    "Grand", "Prestige", "Premier", "Luxe", "Elite", "Ultra", "Rare",
    "Exceptional", "Distinguished", "Exclusive", "Pinnacle", "Apex",
    "Crown", "Imperial", "Opulent", "Sovereign", "Quintessential",
    "Benchmark", "Hallmark", "Masterwork", "Paragon", "Pinnacle",
]

# Season themes
SEASON_THEMES = {
    "Winter": {
        "adjectives": ["bold", "warming", "spiced", "dark", "intense", "comforting"],
        "desc_intro": ["Cocok dinikmati di malam dingin,", "Menemani hari hujan dengan sempurna,",
                       "Blend musim dingin yang menghangatkan jiwa,", "Rasa tebal dan mengenyangkan,"],
    },
    "Summer": {
        "adjectives": ["bright", "fruity", "refreshing", "vibrant", "tropical", "lively"],
        "desc_intro": ["Segar dan penuh semangat,", "Cerah seperti pagi musim panas,",
                       "Karakter buah tropis yang menawan,", "Ringan namun penuh kepribadian,"],
    },
    "Autumn": {
        "adjectives": ["warm", "mellow", "caramelized", "earthy", "golden", "rustic"],
        "desc_intro": ["Hangat seperti senja musim gugur,", "Aroma karamel dan rempah yang khas,",
                       "Karakter earthy yang menenangkan,", "Kaya rasa dengan kedalaman yang tak tertandingi,"],
    },
    "Spring": {
        "adjectives": ["floral", "delicate", "light", "aromatic", "clean", "fresh"],
        "desc_intro": ["Halus seperti angin semi,", "Aroma bunga yang menyegarkan,",
                       "Profil rasa yang bersih dan elegan,", "Karakter floral yang memanjakan indra,"],
    },
}

# ─────────────────────────────────────────────
# 3. LOGIKA BLEND GENERATOR
# ─────────────────────────────────────────────

def get_flavor_notes(bean: dict) -> list[str]:
    key = (bean["roast"], bean["processing"])
    return FLAVOR_PROFILE.get(key, ["complex", "balanced", "smooth"])

def weighted_percentages(n: int) -> list[int]:
    """Generate percentages for n components summing to 100."""
    if n == 2:
        a = random.choice([40, 45, 50, 55, 60, 65, 70])
        return [a, 100 - a]
    elif n == 3:
        options = [
            [50, 30, 20], [60, 25, 15], [40, 35, 25],
            [45, 35, 20], [50, 25, 25], [55, 30, 15],
        ]
        return random.choice(options)
    return [100]

def build_blend_name(season: str, kategori: str, idx: int, used_names: set) -> str:
    for _ in range(20):
        if kategori == "Speciality Blend":
            prefix = random.choice(SPECIALITY_PREFIX)
            suffix = random.choice(BLEND_SUFFIXES)
        else:
            prefix = random.choice(BLEND_PREFIXES)
            suffix = random.choice(BLEND_SUFFIXES)
        name = f"{prefix} {season} {suffix}"
        if name not in used_names:
            used_names.add(name)
            return name
    # fallback
    name = f"{season} Blend #{idx}"
    used_names.add(name)
    return name

def build_description(season: str, beans: list[dict], flavor_pool: list[str]) -> str:
    theme = SEASON_THEMES[season]
    intro = random.choice(theme["desc_intro"])
    adj   = random.choice(theme["adjectives"])
    
    # pilih 3-4 flavor note unik
    notes = list(dict.fromkeys(flavor_pool))[:4]
    notes_str = ", ".join(notes[:3])
    
    origins = " dan ".join([b["origin"] for b in beans])
    processes = list({b["processing"] for b in beans})
    proc_str = " & ".join(processes[:2])
    
    desc = (
        f"{intro} blend {adj} ini memadukan biji-biji terbaik dari {origins}. "
        f"Diproses dengan metode {proc_str}, menghadirkan profil rasa {notes_str} "
        f"yang kompleks namun harmonis. "
        f"Sebuah perpaduan yang dirancang untuk memuaskan selera pecinta kopi sejati."
    )
    return desc

def build_resep_gramasi(beans: list[dict], pcts: list[int]) -> dict:
    base = 1000  # gram
    resep = {}
    for bean, pct in zip(beans, pcts):
        gram = int(base * pct / 100)
        resep[f"{bean['origin']} ({bean['roast']} / {bean['processing']})"] = f"{gram}g ({pct}%)"
    resep["total"] = f"{base}g"
    return resep

def pick_dominant_roast(beans: list[dict], pcts: list[int]) -> str:
    score = {"Light": 1, "Medium": 2, "Dark": 3}
    weighted = sum(score.get(b["roast"], 2) * p for b, p in zip(beans, pcts))
    total = sum(pcts)
    avg = weighted / total
    if avg < 1.7:
        return "Light"
    elif avg < 2.5:
        return "Medium"
    else:
        return "Dark"

def generate_sku_parent(seasons_config: dict) -> list[dict]:
    """Generate all 1000 parent blends."""
    results = []
    used_names = set()
    used_compositions = set()

    season_codes = {"Winter": "WIN", "Summer": "SUM", "Autumn": "AUT", "Spring": "SPR"}

    for season, (n_seasonal, n_speciality) in seasons_config.items():
        code = season_codes[season]
        counter = 1

        for kategori, count in [("Seasonal Blend", n_seasonal), ("Speciality Blend", n_speciality)]:
            generated = 0
            attempts = 0
            max_attempts = count * 50

            while generated < count and attempts < max_attempts:
                attempts += 1

                # pilih 2 atau 3 biji
                n_beans = random.choices([2, 3], weights=[0.45, 0.55])[0]

                # Speciality blend: lebih banyak pakai biji premium (anaerobic/wine/natural)
                if kategori == "Speciality Blend":
                    premium = [b for b in BEANS if b["processing"] in ("Anaerobic", "Wine", "Natural")]
                    pool = premium if len(premium) >= n_beans else BEANS
                else:
                    pool = BEANS

                chosen = random.sample(pool, n_beans)

                # cek duplikasi komposisi
                comp_key = tuple(sorted(
                    (b["origin"], b["roast"], b["processing"]) for b in chosen
                ))
                if comp_key in used_compositions:
                    continue
                used_compositions.add(comp_key)

                pcts = weighted_percentages(n_beans)
                dominant_roast = pick_dominant_roast(chosen, pcts)

                # kumpulkan flavor notes
                all_flavors = []
                for bean in chosen:
                    all_flavors.extend(get_flavor_notes(bean))
                random.shuffle(all_flavors)

                sku = f"S-{code}-{counter:03d}"
                nama = build_blend_name(season, kategori, counter, used_names)
                texture = random.choice(TEXTURE_MAP[dominant_roast])
                desc = build_description(season, chosen, all_flavors)
                resep = build_resep_gramasi(chosen, pcts)
                brew = random.choice(BREWING_SUGGEST[dominant_roast])

                komposisi = [
                    {
                        "bean_type": b["type"],
                        "origin": b["origin"],
                        "region": b["region"],
                        "roast": b["roast"],
                        "processing": b["processing"],
                        "percentage": p,
                        "flavor_notes": get_flavor_notes(b)[:3],
                    }
                    for b, p in zip(chosen, pcts)
                ]

                results.append({
                    "sku":                    sku,
                    "season":                 season,
                    "kategori":               kategori,
                    "nama_blend":             nama,
                    "komposisi_biji":         komposisi,
                    "deskripsi":              desc,
                    "texture":                texture,
                    "dominant_roast":         dominant_roast,
                    "resep_gramasi":          resep,
                    "rekomendasi_penyajian":  brew,
                })

                counter += 1
                generated += 1

        print(f"  ✅ {season}: {counter - 1} blends generated")

    return results

def generate_sku_child(parents: list[dict]) -> list[dict]:
    """Expand 1000 parent → 20000 child SKUs."""
    SIZES     = ["100g", "200g", "500g", "1kg"]
    GRINDS    = ["Whole Bean", "Coarse", "Medium", "Fine", "Extra Fine"]
    GRIND_MAP = {
        "Whole Bean": "WB", "Coarse": "CRS", "Medium": "MED",
        "Fine": "FIN", "Extra Fine": "XF",
    }
    SIZE_MAP  = {"100g": "100", "200g": "200", "500g": "500", "1kg": "1K"}

    PRICE_BASE = {  # IDR per 100g base
        "100g":  {"Seasonal Blend": 35000,  "Speciality Blend": 55000},
        "200g":  {"Seasonal Blend": 62000,  "Speciality Blend": 98000},
        "500g":  {"Seasonal Blend": 140000, "Speciality Blend": 220000},
        "1kg":   {"Seasonal Blend": 255000, "Speciality Blend": 400000},
    }
    GRIND_PREMIUM = {
        "Whole Bean": 0, "Coarse": 2000, "Medium": 2500,
        "Fine": 3000, "Extra Fine": 3500,
    }

    children = []
    for parent in parents:
        parent_sku = parent["sku"]
        kat = parent["kategori"]
        for size in SIZES:
            for grind in GRINDS:
                g_code   = GRIND_MAP[grind]
                s_code   = SIZE_MAP[size]
                child_sku = f"{parent_sku}-{s_code}-{g_code}"
                price = PRICE_BASE[size][kat] + GRIND_PREMIUM[grind]

                children.append({
                    "child_sku":      child_sku,
                    "parent_sku":     parent_sku,
                    "nama_blend":     parent["nama_blend"],
                    "season":         parent["season"],
                    "kategori":       parent["kategori"],
                    "ukuran":         size,
                    "grind_size":     grind,
                    "harga_idr":      price,
                    "berat_bersih_g": int(size.replace("kg", "000").replace("g", "")),
                    "deskripsi_singkat": parent["deskripsi"][:120] + "...",
                })

    return children

# ─────────────────────────────────────────────
# 4. MAIN EXECUTION
# ─────────────────────────────────────────────

def save_json(data: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  💾 JSON saved: {path} ({len(data)} records)")

def save_csv(data: list, path: str, flatten_fn=None):
    if not data:
        return
    rows = [flatten_fn(r) for r in data] if flatten_fn else data
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  💾 CSV saved:  {path} ({len(rows)} records)")

def flatten_parent(r: dict) -> dict:
    komposisi_str = " | ".join(
        f"{c['origin']} {c['roast']} {c['processing']} {c['percentage']}%"
        for c in r["komposisi_biji"]
    )
    resep_str = " | ".join(f"{k}: {v}" for k, v in r["resep_gramasi"].items())
    return {
        "sku":                   r["sku"],
        "season":                r["season"],
        "kategori":              r["kategori"],
        "nama_blend":            r["nama_blend"],
        "komposisi_biji":        komposisi_str,
        "dominant_roast":        r["dominant_roast"],
        "deskripsi":             r["deskripsi"],
        "texture":               r["texture"],
        "resep_gramasi":         resep_str,
        "rekomendasi_penyajian": r["rekomendasi_penyajian"],
    }

if __name__ == "__main__":
    OUT = Path("/home/claude/output")
    OUT.mkdir(exist_ok=True)

    print("\n🚀 GENERATING 1.000 PARENT BLEND SKUs...")
    seasons_config = {
        "Winter": (200, 50),
        "Summer": (200, 50),
        "Autumn": (200, 50),
        "Spring": (200, 50),
    }
    parents = generate_sku_parent(seasons_config)
    print(f"\n✅ Total parent SKUs generated: {len(parents)}")

    print("\n📦 Saving parent data...")
    save_json(parents, str(OUT / "blend_parent_1000.json"))
    save_csv(parents, str(OUT / "blend_parent_1000.csv"), flatten_parent)

    print("\n🚀 GENERATING 20.000 CHILD RETAIL SKUs...")
    children = generate_sku_child(parents)
    print(f"✅ Total child SKUs generated: {len(children)}")

    print("\n📦 Saving child data...")
    save_json(children, str(OUT / "blend_child_20000.json"))
    save_csv(children, str(OUT / "blend_child_20000.csv"))

    # Stats
    print("\n📊 SUMMARY STATISTIK:")
    from collections import Counter
    season_counts = Counter(p["season"] for p in parents)
    for s, c in season_counts.items():
        kat_counts = Counter(p["kategori"] for p in parents if p["season"] == s)
        print(f"  {s}: {c} total | Seasonal: {kat_counts['Seasonal Blend']} | Speciality: {kat_counts['Speciality Blend']}")

    roast_dist = Counter(p["dominant_roast"] for p in parents)
    print(f"\n  Dominant Roast Distribution:")
    for r, c in roast_dist.items():
        print(f"    {r}: {c} blends")

    n2 = sum(1 for p in parents if len(p["komposisi_biji"]) == 2)
    n3 = sum(1 for p in parents if len(p["komposisi_biji"]) == 3)
    print(f"\n  Komposisi: 2-biji={n2} | 3-biji={n3}")
    print(f"\n  Total child retail SKUs: {len(children)}")
    print("\n✅ DONE! Semua file tersimpan di /home/claude/output/")
