"""
╔══════════════════════════════════════════════════════════════════════╗
║   KAFE NUSANTARA — BLEND SKU GENERATOR v2.0                        ║
║   "The Four Expeditions" · Narrative Naming Engine                 ║
║                                                                      ║
║   Convention per season:                                            ║
║   WINTER  · The Dark Passage    → nama pos perhentian ekspedisi    ║
║   SUMMER  · The Open Horizon    → nama kapal / rute dagang kuno    ║
║   AUTUMN  · The Amber Descent   → artefak & alat penjelajah       ║
║   SPRING  · The First Ascent    → fenomena alam pegunungan         ║
║                                                                      ║
║   Speciality tier = sub-universe eksklusif dalam setiap season     ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import csv
import random
from pathlib import Path
from collections import Counter

random.seed(42)

# ─────────────────────────────────────────────────────────────────────
# 1. LOAD DATA MASTER
# ─────────────────────────────────────────────────────────────────────

def parse_menu_md(filepath: str) -> list[dict]:
    beans = []
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[1:]:
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

# ─────────────────────────────────────────────────────────────────────
# 2. NAMING UNIVERSE — THE FOUR EXPEDITIONS
# ─────────────────────────────────────────────────────────────────────

NAMING = {

    # ── WINTER · The Dark Passage ────────────────────────────────────
    # Nama blend = pos perhentian / shelter dalam ekspedisi pegunungan
    # Format: [Kata Sifat/Kondisi] + [Nama Pos/Tempat Berteduh]
    "Winter": {
        "universe_name": "The Dark Passage",
        "tagline": "Di mana perjalanan dimulai — dalam kegelapan yang menyimpan bara.",
        "seasonal": {
            # Kata depan: kondisi/suasana pos
            "modifiers": [
                "Frozen", "Midnight", "Smoldering", "Shadowed", "Iron",
                "Ashen", "Ember", "Hollow", "Veiled", "Scorched",
                "Muted", "Buried", "Charred", "Ancient", "Forgotten",
                "Darkened", "Stormy", "Shrouded", "Bitter", "Sealed",
                "Windswept", "Dimmed", "Frosted", "Cracked", "Heavy",
                "Silent", "Rugged", "Faded", "Blanketed", "Hushed",
            ],
            # Kata belakang: tipe pos / tempat perlindungan ekspedisi
            "anchors": [
                "Bivouac", "Shelter", "Outpost", "Refuge", "Camp",
                "Garrison", "Waystation", "Bastion", "Stronghold", "Lodge",
                "Barracks", "Depot", "Quarters", "Station", "Passage",
                "Encampment", "Redoubt", "Rampart", "Crossing", "Threshold",
                "Citadel", "Alcove", "Hollow", "Burrow", "Den",
                "Hearth", "Keep", "Vault", "Sanctum", "Watchtower",
            ],
        },
        "speciality": {
            # Sub-universe: The Cartographer's Cache
            # Nama = koleksi peta / dokumen rahasia sang kartografer
            "modifiers": [
                "Forbidden", "Unmapped", "Sealed", "Obsidian", "Classified",
                "Encrypted", "Clandestine", "Redacted", "Covert", "Sovereign",
                "Mythic", "Arcane", "Uncharted", "Rarest", "Hallowed",
            ],
            "anchors": [
                "Codex", "Manuscript", "Folio", "Atlas", "Cipher",
                "Grimoire", "Ledger", "Chronicle", "Cartouche", "Dispatch",
                "Dossier", "Registry", "Compendium", "Scroll", "Parchment",
            ],
            "prefix": "Cartographer's",
        },
    },

    # ── SUMMER · The Open Horizon ────────────────────────────────────
    # Nama blend = kapal legendaris / rute pelayaran dagang Nusantara
    # Format: [Nama Kapal/Rute] + [Penanda Navigasi/Laut]
    "Summer": {
        "universe_name": "The Open Horizon",
        "tagline": "Ketika laut dan langit melebur — dan setiap tegukan terasa seperti angin pertama.",
        "seasonal": {
            # Kata depan: nama kapal atau rute pelayaran
            "modifiers": [
                "Sunda", "Banda", "Makassar", "Malacca", "Timor",
                "Flores", "Lombok", "Bali", "Celebes", "Molucca",
                "Java", "Borneo", "Sulawesi", "Ternate", "Tidore",
                "Ambon", "Kupang", "Manado", "Sorong", "Padang",
                "Palembang", "Demak", "Gresik", "Tuban", "Banten",
                "Aceh", "Riau", "Jambi", "Pontianak", "Balikpapan",
            ],
            # Kata belakang: elemen navigasi / laut
            "anchors": [
                "Voyage", "Current", "Trade Wind", "Meridian", "Bearing",
                "Transit", "Passage", "Wake", "Swell", "Drift",
                "Channel", "Strait", "Route", "Course", "Convoy",
                "Fleet", "Manifest", "Charter", "Cargo", "Expedition",
                "Crossing", "Traverse", "Run", "Reach", "Approach",
                "Anchorage", "Berth", "Starboard", "Portside", "Heading",
            ],
        },
        "speciality": {
            # Sub-universe: The Mariner's Reserve
            # Nama = kapal armada legendaris / log pelayaran bersejarah
            "modifiers": [
                "Golden", "Admiral's", "Captain's", "Flagship", "Imperial",
                "Grand", "First-Class", "Sovereign", "Celestial", "Hallowed",
                "Legendary", "Mythic", "Chartered", "Premier", "Elite",
            ],
            "anchors": [
                "Galleon", "Clipper", "Brigantine", "Frigate", "Schooner",
                "Carrack", "Dhow", "Junk", "Proa", "Pinnace",
                "Corvette", "Bark", "Ketch", "Sloop", "Cutter",
            ],
            "prefix": "Mariner's",
        },
    },

    # ── AUTUMN · The Amber Descent ───────────────────────────────────
    # Nama blend = alat & artefak yang ditemukan dalam perjalanan
    # Format: [Kondisi Artefak] + [Nama Alat/Benda]
    "Autumn": {
        "universe_name": "The Amber Descent",
        "tagline": "Turun gunung sambil membawa cerita — dan aroma tanah yang belum terlupakan.",
        "seasonal": {
            # Kata depan: kondisi / usia artefak
            "modifiers": [
                "Weathered", "Tarnished", "Worn", "Antique", "Aged",
                "Patinated", "Rusted", "Battered", "Burnished", "Timeworn",
                "Cracked", "Mended", "Faded", "Engraved", "Embossed",
                "Gilded", "Hammered", "Polished", "Dented", "Scarred",
                "Handcrafted", "Field-worn", "Trail-kept", "Well-used", "Restored",
                "Inherited", "Storied", "Hardy", "Reliable", "True",
            ],
            # Kata belakang: alat / benda milik penjelajah
            "anchors": [
                "Compass", "Sextant", "Theodolite", "Astrolabe", "Barometer",
                "Chronometer", "Altimeter", "Clinometer", "Aneroid", "Transit",
                "Protractor", "Divider", "Planimeter", "Odometer", "Pedometer",
                "Flask", "Canteen", "Lantern", "Haversack", "Rucksack",
                "Penknife", "Awl", "Chisel", "Hammer", "Mallet",
                "Ledger", "Logbook", "Field Notes", "Survey Map", "Sketch Pad",
            ],
        },
        "speciality": {
            # Sub-universe: The Relic Edition
            # Nama = benda kuno / relik yang hanya ditemukan sekali
            "modifiers": [
                "Museum-Grade", "Excavated", "Preserved", "One-of-a-Kind", "Unearthed",
                "Authenticated", "Catalogued", "Archived", "Curated", "Hallowed",
                "Consecrated", "Antiquarian", "Heritage-Class", "Grand", "Pristine",
            ],
            "anchors": [
                "Relic", "Artifact", "Heirloom", "Specimen", "Exhibit",
                "Trophy", "Keepsake", "Token", "Signet", "Medallion",
                "Talisman", "Amulet", "Seal", "Insignia", "Emblem",
            ],
            "prefix": "Relic",
        },
    },

    # ── SPRING · The First Ascent ────────────────────────────────────
    # Nama blend = fenomena alam pegunungan saat fajar & musim baru
    # Format: [Waktu/Momen] + [Fenomena Alam]
    "Spring": {
        "universe_name": "The First Ascent",
        "tagline": "Sebelum puncak — ada langkah pertama yang paling jujur.",
        "seasonal": {
            # Kata depan: waktu / momen fenomena terjadi
            "modifiers": [
                "First", "Morning", "Dawn", "Early", "Rising",
                "Waking", "Breaking", "Opening", "Nascent", "New",
                "Fresh", "Young", "Gentle", "Soft", "Tender",
                "Pale", "Faint", "Quiet", "Still", "Pure",
                "Thin", "Wispy", "Shifting", "Drifting", "Hovering",
                "Climbing", "Ascending", "Gathering", "Blooming", "Stirring",
            ],
            # Kata belakang: fenomena alam pegunungan
            "anchors": [
                "Dew", "Mist", "Frost", "Haze", "Fog",
                "Vapor", "Cloud", "Cumulus", "Cirrus", "Stratus",
                "Rime", "Bloom", "Blossom", "Pollen", "Spore",
                "Spring", "Runoff", "Snowmelt", "Brook", "Rivulet",
                "Lichen", "Moss", "Fern", "Sprig", "Tendril",
                "Sunbreak", "Clearance", "Clearwater", "Wellspring", "Headwater",
            ],
        },
        "speciality": {
            # Sub-universe: The Pioneer's Journal
            # Nama = entri jurnal pertama sang pionir
            "modifiers": [
                "Inaugural", "Pioneering", "Trailblazing", "Pathfinding", "Groundbreaking",
                "Landmark", "Defining", "Formative", "Foundational", "Pristine",
                "Unspoiled", "Untouched", "Virgin", "Primal", "Elemental",
            ],
            "anchors": [
                "Entry", "Record", "Account", "Memoir", "Testament",
                "Dispatch", "Notation", "Inscription", "Observation", "Discovery",
                "Finding", "Revelation", "Disclosure", "Venture", "Initiative",
            ],
            "prefix": "Pioneer's",
        },
    },
}

# ─────────────────────────────────────────────────────────────────────
# 3. FLAVOR, TEXTURE, DESKRIPSI — DIPERKAYA DENGAN NARASI SEASON
# ─────────────────────────────────────────────────────────────────────

FLAVOR_PROFILE = {
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

# Deskripsi intro — setiap season punya nada cerita yang berbeda
DESC_INTRO = {
    "Winter": [
        "Dalam keheningan malam di antara dua puncak,",
        "Seperti api yang tak kunjung padam di pos terakhir,",
        "Ketika angin gunung membekukan jejak perjalanan,",
        "Di singgahan terakhir sebelum salju menutup jalur,",
        "Bagi para ekspeditor yang melewati malam terpanjang,",
        "Dari kegelapan yang menjaga bara tetap hidup,",
    ],
    "Summer": [
        "Seperti angin laut yang pertama kali menyentuh dek,",
        "Ketika layar dibentangkan dan cakrawala terbuka lebar,",
        "Dari pelabuhan tua yang menyimpan ribuan cerita,",
        "Terinspirasi dari rute dagang yang telah melintasi generasi,",
        "Seperti kapal yang menemukan teluknya setelah berbulan berlayar,",
        "Di mana muara sungai berjumpa dengan lautan terbuka,",
    ],
    "Autumn": [
        "Ditemukan dalam catatan perjalanan seorang penjelajah tua,",
        "Seperti kompas yang selalu menunjuk ke tempat yang tepat,",
        "Diilhami dari artefak yang bertahan melewati puluhan ekspedisi,",
        "Dari tangan-tangan yang pernah mengukur setiap jengkal dataran,",
        "Terekam dalam logbook yang lusuh namun tak pernah salah,",
        "Seperti alat ukur yang semakin akurat seiring bertambah usia,",
    ],
    "Spring": [
        "Saat kabut pagi pertama mulai mengangkat tirainya,",
        "Seperti embun yang jatuh pada daun pertama musim baru,",
        "Dari mata air yang baru saja membuka jejaknya di lereng,",
        "Ketika langkah pertama meninggalkan bekas di tanah yang bersih,",
        "Terinspirasi dari fajar yang menerangi jalur yang belum pernah dilalui,",
        "Di mana benih harapan tumbuh dari tanah yang baru mencair,",
    ],
}

# Kalimat penutup deskripsi — kohesif dengan narasi ekspedisi
DESC_CLOSING = {
    "Winter": [
        "Sebuah penghormatan kepada mereka yang tak takut melangkah dalam gelap.",
        "Diciptakan untuk jiwa-jiwa yang memahami bahwa perjalanan terbaik dimulai dari yang paling sunyi.",
        "Untuk setiap ekspeditor yang pernah menemukan kehangatan di tempat yang paling dingin.",
        "Blend yang diracik bagi mereka yang menghargai keberanian sebuah permulaan.",
    ],
    "Summer": [
        "Sebuah persembahan kepada rute-rute yang telah menghubungkan Nusantara selama berabad-abad.",
        "Untuk para pelaut dalam diri kita — yang selalu menemukan jalan pulang.",
        "Diciptakan dari spirit jalur dagang yang mengalirkan kekayaan rasa lintas samudera.",
        "Blend yang merayakan keberanian membuka cakrawala baru, satu tegukan sekaligus.",
    ],
    "Autumn": [
        "Diwariskan dari tangan-tangan yang mengukur bumi sebelum peta pernah ada.",
        "Untuk setiap penjelajah yang memahami bahwa alat terbaik adalah yang paling sering dipakai.",
        "Sebuah penghormatan kepada artefak yang merekam lebih dari sekadar perjalanan.",
        "Diciptakan bagi mereka yang menemukan keindahan dalam sesuatu yang telah melalui banyak hal.",
    ],
    "Spring": [
        "Untuk langkah pertama yang selalu lebih jujur dari seribu langkah berikutnya.",
        "Diciptakan bagi mereka yang memahami bahwa setiap puncak dimulai dari sebuah pagi.",
        "Sebuah perayaan atas keberanian memulai — ketika segala sesuatunya masih bersih dan mungkin.",
        "Blend yang merekam kesegaran dari tempat di mana perjalanan baru saja dimulai.",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# 4. NAMING ENGINE BARU
# ─────────────────────────────────────────────────────────────────────

def build_blend_name(season: str, kategori: str, idx: int, used_names: set) -> tuple[str, str]:
    """
    Returns (nama_blend, narrative_context)
    narrative_context = penjelasan singkat kenapa nama ini dipilih (untuk marketing copy)
    """
    convention = NAMING[season]

    for _ in range(50):
        if kategori == "Speciality Blend":
            pool    = convention["speciality"]
            prefix  = pool["prefix"]
            mod     = random.choice(pool["modifiers"])
            anchor  = random.choice(pool["anchors"])
            name    = f"{prefix} {mod} {anchor}"
        else:
            pool   = convention["seasonal"]
            mod    = random.choice(pool["modifiers"])
            anchor = random.choice(pool["anchors"])
            name   = f"{mod} {anchor}"

        if name not in used_names:
            used_names.add(name)
            # buat konteks narasi singkat
            universe = convention["universe_name"]
            if kategori == "Speciality Blend":
                ctx = f"{universe} · {convention['speciality']['prefix']} sub-universe"
            else:
                ctx = f"{universe} · Seasonal collection"
            return name, ctx

    # fallback jika collision ekstrem
    fallback = f"{season} Expedition #{idx}"
    used_names.add(fallback)
    return fallback, "Fallback name"


def build_description(season: str, kategori: str, blend_name: str,
                       beans: list[dict], flavor_pool: list[str]) -> str:
    intro   = random.choice(DESC_INTRO[season])
    closing = random.choice(DESC_CLOSING[season])

    # Flavor notes unik, maksimal 3
    notes = list(dict.fromkeys(flavor_pool))
    notes_str = ", ".join(notes[:3])

    # Proses unik dalam blend
    processes = list(dict.fromkeys(b["processing"] for b in beans))
    proc_str = " dan ".join(processes[:2])

    # Asal-usul biji
    origins = " serta ".join(b["origin"] for b in beans)

    # Kalimat inti berbeda untuk Speciality vs Seasonal
    if kategori == "Speciality Blend":
        body = (
            f"blend eksklusif ini merajut karakter biji pilihan dari {origins} "
            f"menjadi sebuah komposisi yang tak mudah ditemukan. "
            f"Melalui proses {proc_str}, lahirlah profil rasa {notes_str} — "
            f"kompleks, berlapis, dan tak tergesa-gesa mengungkap dirinya."
        )
    else:
        body = (
            f"blend ini mempertemukan biji-biji dari {origins} "
            f"dalam sebuah komposisi yang menceritakan kekayaan dataran Nusantara. "
            f"Diproses dengan metode {proc_str}, menghadirkan nuansa {notes_str} "
            f"yang bersih namun penuh kedalaman."
        )

    return f"{intro} {body} {closing}"


# ─────────────────────────────────────────────────────────────────────
# 5. HELPERS (SAMA SEPERTI v1)
# ─────────────────────────────────────────────────────────────────────

def get_flavor_notes(bean: dict) -> list[str]:
    key = (bean["roast"], bean["processing"])
    return FLAVOR_PROFILE.get(key, ["complex", "balanced", "smooth"])

def weighted_percentages(n: int) -> list[int]:
    if n == 2:
        a = random.choice([40, 45, 50, 55, 60, 65, 70])
        return [a, 100 - a]
    elif n == 3:
        return random.choice([
            [50, 30, 20], [60, 25, 15], [40, 35, 25],
            [45, 35, 20], [50, 25, 25], [55, 30, 15],
        ])
    return [100]

def build_resep_gramasi(beans: list[dict], pcts: list[int]) -> dict:
    base = 1000
    resep = {}
    for bean, pct in zip(beans, pcts):
        gram = int(base * pct / 100)
        resep[f"{bean['origin']} ({bean['roast']} / {bean['processing']})"] = f"{gram}g ({pct}%)"
    resep["total"] = f"{base}g"
    return resep

def pick_dominant_roast(beans: list[dict], pcts: list[int]) -> str:
    score = {"Light": 1, "Medium": 2, "Dark": 3}
    weighted = sum(score.get(b["roast"], 2) * p for b, p in zip(beans, pcts))
    avg = weighted / sum(pcts)
    if avg < 1.7:   return "Light"
    elif avg < 2.5: return "Medium"
    else:           return "Dark"

# ─────────────────────────────────────────────────────────────────────
# 6. MAIN GENERATOR
# ─────────────────────────────────────────────────────────────────────

def generate_sku_parent(seasons_config: dict) -> list[dict]:
    results = []
    used_names = set()
    used_compositions = set()
    season_codes = {"Winter": "WIN", "Summer": "SUM", "Autumn": "AUT", "Spring": "SPR"}

    for season, (n_seasonal, n_speciality) in seasons_config.items():
        code = season_codes[season]
        counter = 1

        for kategori, count in [("Seasonal Blend", n_seasonal), ("Speciality Blend", n_speciality)]:
            generated = 0
            attempts  = 0

            while generated < count and attempts < count * 50:
                attempts += 1

                n_beans = random.choices([2, 3], weights=[0.45, 0.55])[0]

                # Speciality: prioritaskan biji premium
                if kategori == "Speciality Blend":
                    premium = [b for b in BEANS if b["processing"] in ("Anaerobic", "Wine", "Natural")]
                    pool = premium if len(premium) >= n_beans else BEANS
                else:
                    pool = BEANS

                chosen = random.sample(pool, n_beans)

                comp_key = tuple(sorted(
                    (b["origin"], b["roast"], b["processing"]) for b in chosen
                ))
                if comp_key in used_compositions:
                    continue
                used_compositions.add(comp_key)

                pcts          = weighted_percentages(n_beans)
                dominant_roast = pick_dominant_roast(chosen, pcts)

                all_flavors = []
                for bean in chosen:
                    all_flavors.extend(get_flavor_notes(bean))
                random.shuffle(all_flavors)

                sku          = f"S-{code}-{counter:03d}"
                nama, ctx    = build_blend_name(season, kategori, counter, used_names)
                texture      = random.choice(TEXTURE_MAP[dominant_roast])
                desc         = build_description(season, kategori, nama, chosen, all_flavors)
                resep        = build_resep_gramasi(chosen, pcts)
                brew         = random.choice(BREWING_SUGGEST[dominant_roast])

                komposisi = [
                    {
                        "bean_type":    b["type"],
                        "origin":       b["origin"],
                        "region":       b["region"],
                        "roast":        b["roast"],
                        "processing":   b["processing"],
                        "percentage":   p,
                        "flavor_notes": get_flavor_notes(b)[:3],
                    }
                    for b, p in zip(chosen, pcts)
                ]

                results.append({
                    "sku":                    sku,
                    "season":                 season,
                    "season_universe":        NAMING[season]["universe_name"],
                    "season_tagline":         NAMING[season]["tagline"],
                    "kategori":               kategori,
                    "nama_blend":             nama,
                    "narrative_context":      ctx,
                    "komposisi_biji":         komposisi,
                    "deskripsi":              desc,
                    "texture":                texture,
                    "dominant_roast":         dominant_roast,
                    "resep_gramasi":          resep,
                    "rekomendasi_penyajian":  brew,
                })

                counter   += 1
                generated += 1

        print(f"  ✅ {season} ({NAMING[season]['universe_name']}): {counter - 1} blends")

    return results

def generate_sku_child(parents: list[dict]) -> list[dict]:
    SIZES  = ["100g", "200g", "500g", "1kg"]
    GRINDS = ["Whole Bean", "Coarse", "Medium", "Fine", "Extra Fine"]
    GRIND_MAP = {"Whole Bean": "WB", "Coarse": "CRS", "Medium": "MED", "Fine": "FIN", "Extra Fine": "XF"}
    SIZE_MAP  = {"100g": "100", "200g": "200", "500g": "500", "1kg": "1K"}

    PRICE_BASE = {
        "100g":  {"Seasonal Blend": 35000,  "Speciality Blend": 55000},
        "200g":  {"Seasonal Blend": 62000,  "Speciality Blend": 98000},
        "500g":  {"Seasonal Blend": 140000, "Speciality Blend": 220000},
        "1kg":   {"Seasonal Blend": 255000, "Speciality Blend": 400000},
    }
    GRIND_PREMIUM = {"Whole Bean": 0, "Coarse": 2000, "Medium": 2500, "Fine": 3000, "Extra Fine": 3500}

    children = []
    for parent in parents:
        for size in SIZES:
            for grind in GRINDS:
                child_sku = f"{parent['sku']}-{SIZE_MAP[size]}-{GRIND_MAP[grind]}"
                price = PRICE_BASE[size][parent["kategori"]] + GRIND_PREMIUM[grind]
                children.append({
                    "child_sku":         child_sku,
                    "parent_sku":        parent["sku"],
                    "nama_blend":        parent["nama_blend"],
                    "season":            parent["season"],
                    "season_universe":   parent["season_universe"],
                    "kategori":          parent["kategori"],
                    "ukuran":            size,
                    "grind_size":        grind,
                    "harga_idr":         price,
                    "berat_bersih_g":    int(size.replace("kg", "000").replace("g", "")),
                    "deskripsi_singkat": parent["deskripsi"][:130] + "...",
                })
    return children

# ─────────────────────────────────────────────────────────────────────
# 7. OUTPUT
# ─────────────────────────────────────────────────────────────────────

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  💾 JSON: {path}  ({len(data)} records)")

def save_csv(data, path, flatten_fn=None):
    if not data: return
    rows = [flatten_fn(r) for r in data] if flatten_fn else data
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  💾 CSV:  {path}  ({len(rows)} records)")

def flatten_parent(r):
    komposisi_str = " | ".join(
        f"{c['origin']} {c['roast']} {c['processing']} {c['percentage']}%"
        for c in r["komposisi_biji"]
    )
    resep_str = " | ".join(f"{k}: {v}" for k, v in r["resep_gramasi"].items())
    return {
        "sku":                   r["sku"],
        "season":                r["season"],
        "season_universe":       r["season_universe"],
        "season_tagline":        r["season_tagline"],
        "kategori":              r["kategori"],
        "nama_blend":            r["nama_blend"],
        "narrative_context":     r["narrative_context"],
        "komposisi_biji":        komposisi_str,
        "dominant_roast":        r["dominant_roast"],
        "deskripsi":             r["deskripsi"],
        "texture":               r["texture"],
        "resep_gramasi":         resep_str,
        "rekomendasi_penyajian": r["rekomendasi_penyajian"],
    }

if __name__ == "__main__":
    OUT = Path("/home/claude/output_v2")
    OUT.mkdir(exist_ok=True)

    print("\n🚀 GENERATING 1.000 PARENT BLEND SKUs — The Four Expeditions Edition...\n")
    seasons_config = {
        "Winter": (200, 50),
        "Summer": (200, 50),
        "Autumn": (200, 50),
        "Spring": (200, 50),
    }
    parents = generate_sku_parent(seasons_config)
    print(f"\n✅ Total parent SKUs: {len(parents)}")

    print("\n📦 Saving parent data...")
    save_json(parents, str(OUT / "blend_parent_v2_1000.json"))
    save_csv(parents,  str(OUT / "blend_parent_v2_1000.csv"), flatten_parent)

    print("\n🚀 GENERATING 20.000 CHILD RETAIL SKUs...")
    children = generate_sku_child(parents)
    print(f"✅ Total child SKUs: {len(children)}")
    save_json(children, str(OUT / "blend_child_v2_20000.json"))
    save_csv(children,  str(OUT / "blend_child_v2_20000.csv"))

    # ── Preview sampel per season ────────────────────────────────────
    print("\n" + "─"*60)
    print("📋 PREVIEW SAMPEL — satu blend per season")
    print("─"*60)
    seen = set()
    for p in parents:
        if p["season"] not in seen:
            seen.add(p["season"])
            print(f"\n[{p['season']} · {p['season_universe']}]")
            print(f"  SKU          : {p['sku']}")
            print(f"  Nama         : {p['nama_blend']}")
            print(f"  Kategori     : {p['kategori']}")
            print(f"  Context      : {p['narrative_context']}")
            print(f"  Komposisi    : ", end="")
            for c in p["komposisi_biji"]:
                print(f"{c['origin']} ({c['roast']}/{c['processing']}) {c['percentage']}%", end="  ")
            print(f"\n  Texture      : {p['texture']}")
            print(f"  Penyajian    : {p['rekomendasi_penyajian']}")
            print(f"  Deskripsi    :\n    {p['deskripsi']}")

    # ── Statistik nama ───────────────────────────────────────────────
    print("\n" + "─"*60)
    print("📊 STATISTIK NAMING")
    print("─"*60)
    for season in ["Winter", "Summer", "Autumn", "Spring"]:
        s_blends = [p for p in parents if p["season"] == season]
        seasonal  = [p for p in s_blends if p["kategori"] == "Seasonal Blend"]
        speciality = [p for p in s_blends if p["kategori"] == "Speciality Blend"]
        print(f"\n  {season} · {NAMING[season]['universe_name']}")
        print(f"    Seasonal   ({len(seasonal):3d}): sample → {seasonal[0]['nama_blend']}, {seasonal[1]['nama_blend']}, {seasonal[2]['nama_blend']}")
        print(f"    Speciality ({len(speciality):3d}): sample → {speciality[0]['nama_blend']}, {speciality[1]['nama_blend']}")

    print(f"\n✅ DONE — semua file tersimpan di {OUT}/")
