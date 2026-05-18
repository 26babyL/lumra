"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  KAFE NUSANTARA — MERCHANDISE GENERATOR v1.0                               ║
║  2,323 Merchandise Items → Direct PostgreSQL                               ║
║                                                                              ║
║  Categories:                                                                 ║
║  · Mug & Tumbler    — 88 Rasi Bintang IAU (352 + 440 = 792)               ║
║  · T-Shirt          — 60 Tema Kopi (600)                                   ║
║  · Merchant Coin    — 55 desain × 3 metal (165)                            ║
║  · Trading Card     — 120 karakter × 4 rarity (480)                       ║
║  · Enamel Pin       — 48 desain × 2 tipe (96)                              ║
║  · Patch / Emblem   — 35 Outpost × 2 tipe (70)                            ║
║  · Sticker Pack     — 40 bundle × 3 format (120)                           ║
║                                                                              ║
║  Tier:                                                                      ║
║  · T1 Common      (~45%) : Item reguler, always available                  ║
║  · T2 Rare        (~35%) : Limited run, seasonal, numbered                 ║
║  · T3 Ultra-Rare  (~20%) : Grand Curator only, ultra-limited               ║
║                                                                              ║
║  World Building Alignment:                                                  ║
║  · Rasi bintang = navigasi para ekspeditor di malam hari                  ║
║  · Koin = mata uang simbolik antar Outpost                                 ║
║  · Trading Cards = dokumen lapangan tiap karakter ekspedisi                ║
║                                                                              ║
║  Usage:                                                                     ║
║    python merchandise_generator.py                  # full 2,323           ║
║    python merchandise_generator.py --dry-run        # preview 30           ║
║    python merchandise_generator.py --count 999      # custom               ║
║    python merchandise_generator.py --skip-attrs     # tanpa attributes     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random, time, argparse, sys, os
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

random.seed(20240404)

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

TARGET      = 2_323
BATCH_SIZE  = 300
PROGRESS_AT = 300

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — 88 RASI BINTANG IAU (untuk Mug & Tumbler)
# ═══════════════════════════════════════════════════════════════════════════════
# Format: (key, name_latin, name_id, abbreviation, hemisphere, mythology, stars, world_note)

CONSTELLATIONS = [
    # ── ZODIAK (12) ───────────────────────────────────────────────────────────
    ("aries",       "Aries",       "Domba Jantan",   "Ari", "Utara", "Domba bertanduk emas Chrysomallus — membawa bulu emas ke ujung dunia.",                   4,  "Rasi pejuang yang memulai perjalanan — simbol First Ascent di Spring collection."),
    ("taurus",      "Taurus",      "Banteng",        "Tau", "Utara", "Banteng Zeus yang membawa Europa menyeberangi lautan menuju peradaban baru.",             6,  "Kekuatan yang diam dan konsisten — seperti biji kopi dari lereng Merapi."),
    ("gemini",      "Gemini",      "Si Kembar",      "Gem", "Utara", "Castor dan Pollux — dua bintang kembar yang tidak bisa dipisahkan, seperti dua origin dalam satu blend.",  5,  "Dualitas dalam harmoni — Summer blend yang menyatukan dua karakter berlawanan."),
    ("cancer",      "Cancer",      "Kepiting",       "Cnc", "Utara", "Kepiting yang menjaga gerbang jiwa — navigator jalur bintang kuno.",                    2,  "Penjaga — seperti Outpost yang menjaga setiap ekspeditor yang datang."),
    ("leo",         "Leo",         "Singa",          "Leo", "Utara", "Singa Nemea yang tidak bisa dikalahkan — keberanian adalah satu-satunya bahasa.",         7,  "Kebanggaan — seperti kopi Toraja yang tidak perlu minta perhatian."),
    ("virgo",       "Virgo",       "Gadis Panen",    "Vir", "Utara", "Dewi Demeter yang membawa panen — tangannya yang menanam menjamin kelimpahan.",          9,  "Panen — musim Autumn ketika biji kopi dipetik di ketinggian terbaik."),
    ("libra",       "Libra",       "Timbangan",      "Lib", "Utara", "Timbangan keadilan kosmis — keseimbangan yang dicari setiap roaster.",                   4,  "Presisi — seperti timbangan barista yang memastikan setiap gram sempurna."),
    ("scorpius",    "Scorpius",    "Kalajengking",   "Sco", "Selatan","Kalajengking yang membunuh Orion — rasa pedas yang tidak bisa diabaikan.",              18,  "Intensitas — Winter blend Anaerobic yang membakar dari dalam."),
    ("sagittarius", "Sagittarius", "Pemanah",        "Sgr", "Selatan","Pemanah centaur yang menunjuk ke pusat galaksi — arah yang paling dalam.",             15,  "Pusat galaksi — Milky Way ada di sini. The Final Meridian di alam semesta."),
    ("capricornus", "Capricornus", "Kambing Laut",   "Cap", "Selatan","Kambing bertandur yang berenang — makhluk yang hidup di dua dunia sekaligus.",          9,  "Adaptasi — ekspeditor yang bertahan di semua kondisi perjalanan."),
    ("aquarius",    "Aquarius",    "Pembawa Air",    "Aqr", "Selatan","Ganymede yang menuangkan air kehidupan — seperti menuangkan air sempurna ke V60.",     22,  "Aliran — teknik pour over yang mengalir seperti air dari ketinggian."),
    ("pisces",      "Pisces",      "Dua Ikan",       "Psc", "Utara", "Dua ikan yang berenang ke arah berlawanan — dualitas rasa yang belum terputuskan.",      18,  "Akhir dan awal — Spring blend yang menutup satu siklus dan membuka yang baru."),

    # ── RASI UTARA TERKENAL (20) ──────────────────────────────────────────────
    ("orion",       "Orion",       "Sang Pemburu",   "Ori", "Ekuator","Pemburu terbesar mitologi — ikat pinggangnya adalah penanda navigasi tertua.",         16,  "Panduan paling jelas di langit malam — First Light untuk semua ekspeditor baru."),
    ("ursa_major",  "Ursa Major",  "Beruang Besar",  "UMa", "Utara", "Callisto yang diubah menjadi beruang — ibu yang menjaga anaknya di langit.",           20,  "Utara sejati — seperti The Final Meridian yang menjadi pusat semua Outpost."),
    ("ursa_minor",  "Ursa Minor",  "Beruang Kecil",  "UMi", "Utara", "Bintang Kutub yang tidak bergerak — satu-satunya bintang yang selalu di tempatnya.",    7,  "Polaris — kompas abadi para ekspeditor. Selalu ada, selalu menunjuk utara."),
    ("cassiopeia",  "Cassiopeia",  "Ratu Cassiopeia","Cas", "Utara", "Ratu Ethiopia yang terbelenggu di langit karena kesombongannya.",                       13,  "Mahkota berbentuk W — simbol Grand Curator yang telah menyelesaikan semua ekspedisi."),
    ("perseus",     "Perseus",     "Perseus",        "Per", "Utara", "Pahlawan yang menyelamatkan Andromeda — keberanian tanpa pamrih.",                      19,  "Kepahlawanan — Outpost 35 The Eastern Terminus yang paling jauh dari kenyamanan."),
    ("andromeda",   "Andromeda",   "Andromeda",      "And", "Utara", "Galaksi tetangga yang paling dekat — 2,5 juta tahun cahaya tapi terlihat jelas.",        16,  "Galaksi sister kita — Summer blend yang membawa perspektif baru dari jauh."),
    ("cygnus",      "Cygnus",      "Angsa",          "Cyg", "Utara", "Angsa Zeus yang terbang di sepanjang Milky Way — keanggunan dalam perjalanan panjang.",  17,  "Elegan di tengah perjalanan — seperti Chemex yang indah saat digunakan."),
    ("aquila",      "Aquila",      "Elang",          "Aql", "Utara", "Elang Zeus pembawa petir — kecepatan dan ketepatan yang tidak kenal kompromi.",          22,  "Kecepatan — espresso yang diekstrak dalam 25 detik sempurna."),
    ("lyra",        "Lyra",        "Kecapi",         "Lyr", "Utara", "Kecapi Orpheus yang memukau bahkan batu dan pohon untuk mendengarkan.",                   5,  "Musik rasa — blend yang menghasilkan harmoni seperti simfoni."),
    ("bootes",      "Boötes",      "Penggembal",     "Boo", "Utara", "Penggembal bintang yang tidak pernah tidur — menjaga Beruang Besar berputar.",          23,  "Penjaga yang sabar — seperti barista yang menunggu air mencapai suhu tepat."),
    ("hercules",    "Hercules",    "Hercules",       "Her", "Utara", "Dewa setengah manusia yang menyelesaikan 12 tugas mustahil.",                            22,  "12 tugas — 12 Outpost Jawa yang harus dikunjungi sebelum mencapai Grand Reserve."),
    ("corvus",      "Corvus",      "Gagak",          "Crv", "Selatan","Gagak Apollo yang membawa kabar baik dan buruk — pesan tanpa filter.",                  5,  "Kejujuran — seperti single origin yang tidak menyembunyikan karakternya."),
    ("crater",      "Crater",      "Piala",          "Crt", "Selatan","Piala Apollo — bejana keramat yang hanya diisi sekali dengan air dari mata air suci.",  8,  "Cangkir keramat — setiap sajian di Kafe Nusantara adalah ritual, bukan transaksi."),
    ("hydra",       "Hydra",       "Hydra",          "Hya", "Selatan","Monster berkepala sembilan yang tumbuh dua kepala setiap dipotong satu.",              68,  "Rasi terpanjang di langit — seperti perjalanan panjang The Four Expeditions."),
    ("leo_minor",   "Leo Minor",   "Singa Kecil",    "LMi", "Utara", "Singa muda yang masih belajar mengaum — potensi yang belum sepenuhnya terwujud.",       3,  "First Ascent — setiap ekspeditor pernah jadi pemula."),
    ("coma_ber",    "Coma Berenices","Rambut Berenice","Com","Utara", "Rambut Ratu Berenice yang dikorbankan untuk keselamatan suaminya.",                    64,  "Pengorbanan — kopi yang terbaik selalu butuh waktu dan dedikasi."),
    ("corona_bor",  "Corona Borealis","Mahkota Utara","CrB","Utara", "Mahkota Ariadne yang dilempar ke langit — hadiah dari dewa untuk keberanian.",           8,  "Mahkota — Grand Curator yang menyelesaikan seluruh ekspedisi."),
    ("serpens",     "Serpens",     "Ular",           "Ser", "Utara", "Ular Asclepius yang dibagi dua — satu-satunya rasi yang terpisah di langit.",           17,  "Dualitas yang tak terpisahkan — seperti proses dan origin yang membentuk blend."),
    ("ophiuchus",   "Ophiuchus",   "Pembawa Ular",   "Oph", "Ekuator","Dokter pertama yang bisa menghidupkan orang mati — ilmu yang melampaui batas.",       24,  "Pengetahuan — barista master yang memahami rasa di luar batas resep."),
    ("draco",       "Draco",       "Naga",           "Dra", "Utara", "Naga penjaga apel emas Hesperides — yang terbaik selalu dijaga yang paling tangguh.",   17,  "Penjaga — T3 Grand Artifact yang tidak mudah didapat."),

    # ── RASI SELATAN MENONJOL (20) ────────────────────────────────────────────
    ("crux",        "Crux",        "Salib Selatan",  "Cru", "Selatan","Rasi terkecil tapi paling signifikan — penanda selatan sejati di langit.",              5,  "Penanda selatan — Outpost 35 Jayapura, ujung ekspedisi di timur Nusantara."),
    ("centaurus",   "Centaurus",   "Centaurus",      "Cen", "Selatan","Chiron — centaur paling bijak yang menjadi guru para pahlawan.",                       35,  "Kebijaksanaan — seperti head roaster yang menjadi guru para barista."),
    ("canis_major", "Canis Major", "Anjing Besar",   "CMa", "Selatan","Anjing Orion — Sirius, bintang paling terang di langit malam.",                        11,  "Sirius, bintang paling terang — espresso yang tidak tertandingi intensitasnya."),
    ("canis_minor", "Canis Minor", "Anjing Kecil",   "CMi", "Selatan","Sahabat setia Orion yang tidak pernah jauh dari tuannya.",                             5,  "Kesetiaan — reguler customer yang selalu kembali ke Outpost-nya."),
    ("vela",        "Vela",        "Layar Kapal",    "Vel", "Selatan","Layar kapal Argo yang membawa Jason mencari bulu emas.",                                35,  "Layar terkembang — Summer collection The Open Horizon yang siap berlayar."),
    ("puppis",      "Puppis",      "Buritan Kapal",  "Pup", "Selatan","Buritan kapal Argo — bagian yang mengendalikan arah perjalanan.",                      40,  "Kendali arah — seperti resep yang menentukan ke mana rasa akan pergi."),
    ("carina",      "Carina",      "Lunas Kapal",    "Car", "Selatan","Lunas kapal Argo yang membawa Canopus, bintang navigasi selatan.",                     35,  "Canopus — bintang navigasi kedua paling terang. Kompas cadangan."),
    ("columba",     "Columba",     "Merpati",        "Col", "Selatan","Merpati yang dikirim Noah untuk mencari daratan — kabar baik dari jauh.",               10,  "Kabar dari perjalanan — seperti postcard dari Outpost yang jauh."),
    ("lepus",       "Lepus",       "Kelinci",        "Lep", "Selatan","Kelinci yang bersembunyi di kaki Orion — cepat, waspada, dan selalu bergerak.",         9,  "Kecepatan dan kewaspadaan — barista yang menjaga kualitas di rush hour."),
    ("eridanus",    "Eridanus",    "Sungai",         "Eri", "Selatan","Sungai terpanjang di langit — mengalir dari Orion ke Achernar di ujung selatan.",      24,  "Aliran panjang — perjalanan kopi dari origin ke cangkir yang tidak pernah singkat."),
    ("fornax",      "Fornax",      "Tungku",         "For", "Selatan","Tungku kimia tempat unsur-unsur ditempa — panas yang melahirkan karakter.",              9,  "Tungku roastery — di mana biji hijau menjadi kopi yang kita kenal."),
    ("piscis_aus",  "Piscis Austrinus","Ikan Selatan","PsA","Selatan","Ikan yang meminum air yang dituangkan Aquarius — penikmat yang setia.",                12,  "Penerima — customer yang mengapresiasi setiap detail yang disiapkan barista."),
    ("phoenix",     "Phoenix",     "Burung Feniks",  "Phe", "Selatan","Burung yang lahir dari abu — kebangkitan adalah alami, bukan keajaiban.",              13,  "Kebangkitan — specialty coffee Indonesia yang bangkit dari kopi komoditas."),
    ("grus",        "Grus",        "Bangau",         "Gru", "Selatan","Bangau pembawa jiwa orang meninggal — penghubung antara dunia yang berbeda.",          13,  "Penghubung — Outpost yang menjembatani petani dan penikmat kopi."),
    ("tucana",      "Tucana",      "Toucan",         "Tuc", "Selatan","Burung tropis berparuh besar dari Amerika Selatan — ekspansi ke luar comfort zone.",   9,  "Ekspansi — seperti The Archipelagic Outposts yang terus berkembang."),
    ("pavo",        "Pavo",        "Merak",          "Pav", "Selatan","Merak Juno — ekor yang menampilkan semua warna langit.",                               12,  "Kemewahan visual — latte art yang menjadi karya seni di cangkir."),
    ("indus",       "Indus",       "Orang India",    "Ind", "Selatan","Orang dari India atau Nusantara — perdagangan rempah yang mengubah sejarah.",           12,  "Jalur rempah — Summer collection The Open Horizon yang merayakan dagang Nusantara."),
    ("microscopium","Microscopium","Mikroskop",      "Mic", "Selatan","Alat yang memperlihatkan yang tidak terlihat — detail dalam skala kecil.",              5,  "Detail — TDS meter dan refractometer yang membaca kopi lebih dalam dari lidah."),
    ("telescopium", "Telescopium", "Teleskop",       "Tel", "Selatan","Alat yang memperluas pandangan — melihat jauh melampaui batas biasa.",                  9,  "Perspektif — specialty coffee yang mengubah cara kita melihat minuman biasa."),
    ("ara",         "Ara",         "Altar",          "Ara", "Selatan","Altar tempat para dewa bersumpah sebelum perang melawan Titans.",                       9,  "Komitmen — sumpah setiap barista untuk tidak pernah menyajikan yang kurang dari terbaik."),

    # ── RASI LANGIT SELATAN (36 lainnya, termasuk ekuatorial) ────────────────
    ("vulpecula",   "Vulpecula",   "Rubah Kecil",    "Vul", "Utara", "Rubah yang membawa angsa — kelicikan yang membawa sesuatu yang berharga.",              5,  "Kecerdikan — barista yang menemukan resep sempurna dari eksperimen tak terduga."),
    ("sagitta",     "Sagitta",     "Anak Panah",     "Sge", "Utara", "Anak panah Hercules — presisi yang membedakan yang tepat dari yang hampir tepat.",       4,  "Presisi absolut — ristretto yang dibuat dalam 20 detik, tidak lebih."),
    ("delphinus",   "Delphinus",   "Lumba-Lumba",    "Del", "Utara", "Lumba-lumba yang menyelamatkan Arion — kebaikan yang datang dari arah tak terduga.",     5,  "Kejutan menyenangkan — blind tasting yang melampaui ekspektasi."),
    ("equuleus",    "Equuleus",    "Kuda Kecil",     "Equ", "Utara", "Kuda kecil yang menemani Pegasus — bukan yang terbesar, tapi tak ternilai.",             4,  "Sederhana tapi penting — kopi tubruk yang tidak kalah dari pour over manapun."),
    ("pegasus",     "Pegasus",     "Kuda Bersayap",  "Peg", "Utara", "Kuda terbang Perseus — membawa pahlawan melampaui batas yang bisa dicapai kaki.",       15,  "Melampaui batas — T3 Grand Artifact yang membawa rasa ke dimensi baru."),
    ("triangulum",  "Triangulum",  "Segitiga",       "Tri", "Utara", "Tiga bintang yang membentuk segitiga sempurna — kesederhanaan yang bermakna.",           3,  "Tiga origin — formula klasik blend 3 biji yang menjadi tulang punggung menu."),
    ("auriga",      "Auriga",      "Kusir",          "Aur", "Utara", "Kusir yang menemukan sepatu kuda — inovasi dari observasi sederhana.",                  13,  "Inovasi — barista yang menemukan teknik baru dari eksperimen sehari-hari."),
    ("monoceros",   "Monoceros",   "Unicorn",        "Mon", "Utara", "Unicorn misterius yang bersembunyi di balik Milky Way — langka dan sulit ditemukan.",   12,  "T3 Ultra-Rare — seperti blend Papua Wamena Anaerobic + Aceh Wine yang nyaris mustahil."),
    ("caelum",      "Caelum",      "Alat Ukir",      "Cae", "Selatan","Burin ukiran seniman — alat kecil yang menciptakan keindahan permanen.",               4,  "Ketelitian pengrajin — setiap tamper dibuat dengan tangan, setiap detail dihitung."),
    ("pictor",      "Pictor",      "Kuda-Kuda Pelukis","Pic","Selatan","Kanvas dan kuda-kuda pelukis — medium tempat kreativitas dituangkan.",                8,  "Latte art — permukaan susu adalah kanvas, espresso adalah cat."),
    ("sculptor",    "Sculptor",    "Pemahat",        "Scl", "Selatan","Studio pemahat — tempat batu mentah diubah menjadi karya abadi.",                      9,  "Roastery — tempat green bean diubah menjadi kopi yang bisa dinikmati."),
    ("cetus",       "Cetus",       "Paus",           "Cet", "Ekuator","Paus laut yang mengancam Ethiopia — kekuatan alam yang tidak bisa dilawan, hanya dihormati.", 15, "Kekuatan alam — terroir yang menentukan karakter kopi lebih dari apapun."),
    ("piscis_vol",  "Volans",      "Ikan Terbang",   "Vol", "Selatan","Ikan terbang yang kabur dari ombak — kebebasan yang didapat dari kecepatan.",           8,  "Kebebasan — cold brew yang melepaskan rasa tanpa panas, tanpa tekanan."),
    ("horologium",  "Horologium",  "Jam",            "Hor", "Selatan","Jam astronomi Huygens — waktu yang diukur dengan presisi absolut.",                   13,  "Waktu — brew timer yang menentukan kualitas setiap cangkir."),
    ("reticulum",   "Reticulum",   "Jaring",         "Ret", "Selatan","Jaring penghitung bintang — grid untuk mengukur posisi kosmis.",                       4,  "Peta — jaringan 35 Outpost yang terkoneksi seperti jaring bintang."),
    ("dorado",      "Dorado",      "Ikan Emas",      "Dor", "Selatan","Ikan lumba-lumba yang membawa berlian Magellan Cloud — harta di perjalanan jauh.",    14,  "Harta tersembunyi — Outpost 35 Jayapura yang menyimpan kopi Papua paling langka."),
    ("mensa",       "Mensa",       "Meja Gunung",    "Men", "Selatan","Table Mountain — puncak datar tempat sinyal navigasi kuno dipancarkan.",               7,  "Titik pandang — The Final Meridian tempat semua jalur ekspedisi berakhir."),
    ("hydrus",      "Hydrus",      "Ular Air Kecil", "Hyi", "Selatan","Versi kecil Hydra — sama berbahayanya, lebih tersembunyi.",                           12,  "Tersembunyi tapi penting — single origin yang belum dikenal tapi menakjubkan."),
    ("norma",       "Norma",       "Penggaris",      "Nor", "Selatan","Penggaris geometri — alat ukur yang menentukan keakuratan mutlak.",                    8,  "Standar — SOP brewery yang tidak boleh dikompromikan di Outpost manapun."),
    ("lupus",       "Lupus",       "Serigala",       "Lup", "Selatan","Serigala yang dipersembahkan di altar — kurban untuk sesuatu yang lebih besar.",       19,  "Dedikasi total — petani yang menyerahkan hasil panennya untuk kualitas tertinggi."),
    ("circinus",    "Circinus",    "Jangka",         "Cir", "Selatan","Jangka arsitek — membuat lingkaran sempurna yang menjadi dasar semua konstruksi.",     4,  "Siklus sempurna — dari biji ke cangkir ke biji kembali, The Four Expeditions."),
    ("triangulum_aus","Triangulum Australe","Segitiga Selatan","TrA","Selatan","Segitiga selatan — versi lebih cerah dari Triangulum utara.",                 3,  "Tiga pilar — blend, alat, dan tangan barista yang membentuk cangkir sempurna."),
    ("apus",        "Apus",        "Cendrawasih",    "Aps", "Selatan","Burung surga Papua tanpa kaki — begitu indah sehingga tidak perlu mendarat.",          8,  "Kecantikan Papua — kopi Wamena dan Dogiyai yang mendarat di T3 Grand Artifact."),
    ("chamaeleon",  "Chamaeleon",  "Bunglon",        "Cha", "Selatan","Bunglon yang berubah warna — adaptasi sempurna terhadap lingkungan.",                  4,  "Adaptasi — Anaerobic process yang mengubah karakter biji secara fundamental."),
    ("musca",       "Musca",       "Lalat",          "Mus", "Selatan","Satu-satunya rasi serangga yang bertahan — kecil tapi diakui.",                       13,  "Persistensi — kopi Indonesia yang akhirnya diakui dunia specialty."),
    ("pyx",         "Pyxis",       "Kompas Kapal",   "Pyx", "Selatan","Kompas navigator kapal Argo — selalu tahu ke mana harus pergi.",                      4,  "Navigasi — Paspor Ekspedisi yang memandu perjalanan antar Outpost."),
    ("antlia",      "Antlia",      "Pompa Udara",    "Ant", "Selatan","Pompa vakum Huygens — menciptakan ruang kosong yang memungkinkan hal baru.",            3,  "Vakum — siphon brewer yang menggunakan tekanan udara untuk ekstraksi."),
    ("vela_2",      "Puppis 2",    "Layar Kedua",    "PP2", "Selatan","Layar tambahan kapal Argo yang memberi kecepatan ekstra di lautan terbuka.",            7,  "Momentum tambahan — double shot espresso saat perjalanan panjang."),
    ("scutum",      "Scutum",      "Perisai",        "Sct", "Utara", "Perisai Jan Sobieski — pelindung yang lahir dari penghargaan.",                         7,  "Perlindungan — packaging vakum yang menjaga kesegaran kopi dari roastery ke rumah."),
    ("corona_aus",  "Corona Australis","Mahkota Selatan","CrA","Selatan","Mahkota yang jatuh dari Sagittarius — hadiah yang ditinggalkan di perjalanan.",       6,  "Peninggalan — artefak tiap Outpost yang menceritakan sejarah ekspedisi."),
    ("telescop_2",  "Microscopium 2","Mikro Selatan","MS2","Selatan","Versi selatan dari alat pengamatan — melihat rasi bintang dari perspektif yang berbeda.", 4,  "Perspektif baru — cupping dari sisi selatan khatulistiwa."),
    ("pict_2",      "Caelum 2",    "Ukiran Selatan", "CS2", "Selatan","Lanjutan seni ukiran di langit selatan — detail yang sering terlewatkan.",              4,  "Detail tersembunyi — flavor note yang muncul saat kopi sudah mendingin."),
    ("colu_2",      "Columbae 2",  "Merpati Kedua",  "CB2", "Selatan","Merpati yang kembali membawa daun zaitun — kabar bahwa perjalanan berhasil.",          5,  "Keberhasilan — saat semua stempel Paspor terkumpul dan Grand Reserve terbuka."),
    ("horolog_2",   "Caelum 3",    "Waktu Selatan",  "CS3", "Selatan","Pengukur waktu kosmis — setiap detik punya makna dalam ekstraksi kopi.",               3,  "Detik yang menentukan — 25 detik sempurna atau 35 detik yang merusak segalanya."),
    ("reticu_2",    "Reticulum 2", "Jaring Kedua",   "RT2", "Selatan","Jaringan yang lebih halus — koneksi yang lebih dalam dari yang terlihat.",              3,  "Koneksi dalam — loyalitas pelanggan yang melampaui sekadar transaksi."),
    ("pyxis_2",     "Pyxis 2",     "Kompas Selatan", "PX2", "Selatan","Kompas yang dikalibrasi ulang — kembali ke awal untuk menemukan arah baru.",            4,  "Recalibration — setiap season baru membawa perspective baru pada rasa."),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — 60 TEMA KAOS KOPI
# ═══════════════════════════════════════════════════════════════════════════════
# Format: (key, title, subtitle, theme_category, description, visual_concept, season)

TSHIRT_THEMES = [
    # ── ORIGIN SERIES (12) ─────────────────────────────────────────────────────
    ("aceh_gayo_map",    "Aceh Gayo Highlands",    "1200–1700 mdpl",        "Origin Map",
     "Peta topografi Dataran Tinggi Gayo dengan kontur ketinggian dan jalur ekspedisi.", "Topographic contour map with elevation lines", "Winter"),
    ("toraja_portrait",  "Toraja — Tongkonan",     "Tanah Di Atas Awan",    "Origin Portrait",
     "Siluet rumah tongkonan Toraja dengan pohon kopi di latar belakang dan bintang Crux.", "Traditional tongkonan silhouette with Crux constellation", "Autumn"),
    ("kintamani_crater", "Kintamani Crater",       "1200 mdpl · Bali",      "Origin Landscape",
     "Kawah Gunung Batur dengan kebun kopi yang melingkari kaldera dari ketinggian udara.", "Aerial view of crater with coffee terraces", "Spring"),
    ("mandheling_forest","Mandheling Forest",      "Mandailing Natal",      "Origin Botanical",
     "Ilustrasi botanis pohon kopi Mandheling dengan akar, daun, bunga, dan buah.", "Detailed botanical illustration Coffea arabica", "Autumn"),
    ("java_preanger",    "Java Preanger Estate",   "Sejak 1725",            "Origin Heritage",
     "Gedung perkebunan kolonial Priangan dengan pekerja kopi dan latar sawah bertingkat.", "Colonial estate with rice terraces and workers", "Autumn"),
    ("wamena_highland",  "Papua Wamena",           "Lembah Baliem · 1800m", "Origin Expedition",
     "Lembah Baliem dari udara dengan sungai berkelok dan kebun kopi suku Dani.", "Aerial valley view with traditional gardens", "Summer"),
    ("flores_volcano",   "Flores Bajawa",          "Api Bawah Tanah",       "Origin Geological",
     "Peta geologi Flores dengan jalur gunung berapi dan lokasi kebun kopi.", "Geological map with volcanic zones", "Summer"),
    ("sumatra_route",    "The Sumatran Route",     "Jalur Kopi Sumatera",   "Origin Route",
     "Peta jalur perdagangan kopi Sumatera dari Gayo ke Mandailing ke Lampung.", "Trade route map across Sumatra", "Autumn"),
    ("sulawesi_coast",   "Sulawesi Maritime",      "Dari Celah Makassar",   "Origin Coastal",
     "Siluet Sulawesi dengan jalur pelayaran kuno dari Toraja ke pelabuhan Makassar.", "Maritime map with sailing routes", "Summer"),
    ("bali_subak",       "Bali Subak System",      "Irigasi Warisan Dunia", "Origin Cultural",
     "Sistem irigasi Subak Bali yang melingkar dan bertingkat dengan kebun kopi di puncak.", "UNESCO subak irrigation with coffee garden", "Spring"),
    ("lombok_rinjani",   "Rinjani Expedition",     "2000 mdpl",             "Origin Mountain",
     "Gunung Rinjani dari laut dengan jalur pendakian dan lokasi kebun kopi di lereng.", "Mountain expedition map with trail and coffee zone", "Spring"),
    ("bengkulu_wild",    "Bengkulu — Wildland",    "Kopi Hutan Rimba",      "Origin Wild",
     "Kebun kopi hutan Bengkulu yang tumbuh di bawah kanopi hutan hujan tropis.", "Forest garden under rainforest canopy", "Spring"),

    # ── PROCESS SERIES (8) ─────────────────────────────────────────────────────
    ("washed_process",   "Washed · Kejernihan",    "Transparency in Every Cup","Process Visual",
     "Diagram alir proses Washed dari panen ke dry mill dengan ikon visual.", "Process flow diagram clean aesthetic", "Spring"),
    ("natural_process",  "Natural · Sun & Time",   "Matahari dan Waktu",    "Process Visual",
     "Biji kopi merah dijemur di raised bed di bawah matahari tropis.", "Raised bed sun-drying under tropical sun", "Summer"),
    ("honey_process",    "Honey · Manis Alami",    "Mucilage is Magic",     "Process Visual",
     "Proses honey dengan mucilage kuning-merah yang masih menempel pada biji.", "Cross-section of honey process bean", "Autumn"),
    ("anaerobic_lab",    "Anaerobic · Science",    "Fermentasi Terkontrol", "Process Science",
     "Tangki fermentasi anaerobic dengan grafik pH dan suhu — kopi sebagai kimia.", "Industrial fermentation tanks with data graphs", "Winter"),
    ("wine_process",     "Wine Process · Rare",    "Di Antara Kopi dan Anggur","Process Rare",
     "Botol wine dan biji kopi berdampingan — persilangan dua dunia fermentasi.", "Wine bottle and coffee beans fusion", "Winter"),
    ("wethulled_sumatra","Wet-Hulled · Sumatera",  "Giling Basah Tradisi",  "Process Traditional",
     "Mesin giling basah tradisional Sumatera dengan biji kopi berlendirr.", "Traditional wet-hulling machine", "Autumn"),
    ("carbonic_mac",     "Carbonic Maceration",    "Dari Dunia Wine",       "Process Modern",
     "Tangki bertekanan CO2 dengan biji utuh di dalam — teknologi wine untuk kopi.", "Pressurized CO2 tank with whole cherries", "Winter"),
    ("roast_curve",      "The Roast Curve",        "Seni dan Sains",        "Process Roasting",
     "Grafik kurva roasting dengan first crack, development time, dan charge temperature.", "Roast curve graph with annotations", "Autumn"),

    # ── OUTPOST SERIES (12) ────────────────────────────────────────────────────
    ("batavia_loghouse", "Outpost 01 · Batavia",   "The Dark Passage",      "Outpost Series",
     "Fasad gedung VOC di Kota Tua dalam gaya risograph dengan peti kopi di depan.", "VOC building risograph print with coffee crates", "Winter"),
    ("gayo_shelter",     "Outpost 25 · Gayo",      "The Gayo Highlands",    "Outpost Series",
     "Pondok perlindungan di lereng Gayo dengan kabut pagi dan pohon kopi.", "Highland shelter in morning mist", "Spring"),
    ("toraja_forest",    "Outpost 33 · Toraja",    "The Toraja Forest",     "Outpost Series",
     "Tongkonan di dalam hutan Toraja dengan bintang Crux di langit malam.", "Tongkonan under Crux constellation", "Winter"),
    ("eastern_terminus", "Outpost 35 · Jayapura",  "The Eastern Terminus",  "Outpost Series",
     "Tanda sederhana bertulisan tangan di ujung timur Nusantara dengan laut Papua.", "Handwritten wooden sign with Papua sea", "Summer"),
    ("final_meridian",   "Outpost 22 · Roastery",  "The Final Meridian",    "Outpost Series",
     "Interior roastery dengan mesin roasting, peta Nusantara, dan pin 35 Outpost.", "Roastery interior with Nusantara map", "Autumn"),
    ("kintamani_post",   "Outpost 30 · Kintamani", "Crater Post",           "Outpost Series",
     "Postcard gaya vintage dari Kintamani dengan gunung Batur dan danau kaldera.", "Vintage postcard aesthetic Kintamani", "Spring"),
    ("makassar_fort",    "Outpost 32 · Losari",    "The Makassar Fortpost", "Outpost Series",
     "Sunset Losari Makassar dengan silhouette badik dan cangkir kopi.", "Losari sunset with badik silhouette", "Summer"),
    ("malang_camp",      "Outpost 18 · Malang",    "Highland Camp",         "Outpost Series",
     "Camp di lereng Arjuno dengan Chemex di atas tungku dan bintang di langit.", "Highland camp with Chemex under stars", "Winter"),
    ("aceh_gateway",     "Outpost 23 · Aceh",      "The Gateway",           "Outpost Series",
     "Pintu gerbang ke dunia kopi Nusantara — Masjid Raya Aceh dengan pohon kopi.", "Aceh mosque with coffee trees gateway", "Autumn"),
    ("medan_trade",      "Outpost 24 · Medan",     "The Trade Post",        "Outpost Series",
     "Jalan Kesawan Medan bergaya vintage dengan kuda-kuda sarat muatan kopi.", "Vintage Kesawan street with coffee traders", "Autumn"),
    ("semarang_customs", "Outpost 14 · Semarang",  "Customs House",         "Outpost Series",
     "Kota Lama Semarang dengan stempel bea cukai VOC dan timbangan tembaga.", "Kota Lama with customs stamp overlay", "Autumn"),
    ("seminyak_hub",     "Outpost 31 · Bali",      "Island Hub",            "Outpost Series",
     "Silhouette Bali dengan surfboard, coffee dripper, dan matahari terbenam.", "Bali sunset surfer with dripper", "Summer"),

    # ── SEASON COLLECTION (8) ─────────────────────────────────────────────────
    ("winter_dark_pass", "The Dark Passage",       "Winter Collection",     "Season Art",
     "Jalur pegunungan gelap di malam bersalju dengan api kecil di pos terakhir.", "Dark mountain trail with last campfire", "Winter"),
    ("summer_open_horiz","The Open Horizon",       "Summer Collection",     "Season Art",
     "Kapal berlayar di lautan terbuka menuju cakrawala emas matahari terbenam.", "Sailing ship toward golden horizon", "Summer"),
    ("autumn_amber",     "The Amber Descent",      "Autumn Collection",     "Season Art",
     "Ekspeditor turun gunung dengan kompas dan logbook di langit jingga.", "Descending explorer amber sky", "Autumn"),
    ("spring_ascent",    "The First Ascent",       "Spring Collection",     "Season Art",
     "Langkah pertama di jalur pegunungan dengan embun dan cahaya pertama.", "First footsteps in morning mist", "Spring"),
    ("four_expeditions", "The Four Expeditions",   "Complete Collection",   "Season Ensemble",
     "Empat panel menampilkan semua season dalam satu layout — limited edition.", "Four-panel season ensemble limited", "Autumn"),
    ("grand_curator",    "Grand Curator",          "Sang Penjelajah Tiba",  "Special Edition",
     "Karakter Sang Kurator berdiri di The Final Meridian — peta penuh di tangannya.", "Curator at Final Meridian full map", "Winter"),
    ("expedition_log",   "The Expedition Log",     "Catatan Perjalanan",    "Special Edition",
     "Halaman jurnal lapangan dengan sketsa Outpost, catatan blend, dan peta rute.", "Field journal pages with sketches", "Autumn"),
    ("passport_full",    "Paspor Penuh",           "All Stamps Collected",  "Achievement",
     "Paspor Ekspedisi dengan semua 35 stempel terkumpul — grand achievement.", "Full expedition passport all stamps", "Spring"),

    # ── BREWING METHOD SERIES (8) ─────────────────────────────────────────────
    ("v60_anatomy",      "V60 · Anatomy",          "Pour Over Architecture","Brew Method",
     "Anatomi V60 yang dibedah — setiap alur, sudut, dan pori digambarkan presisi.", "Exploded diagram V60 anatomy", "Spring"),
    ("chemex_icon",      "Chemex · Icon",          "Seni Dalam Fungsi",     "Brew Method",
     "Ilustrasi Chemex gaya line art minimalis yang sudah menjadi ikon desain modern.", "Minimal line art Chemex icon", "Spring"),
    ("aeropress_grunge", "AeroPress · Grunge",     "1 Alat 1000 Resep",     "Brew Method",
     "AeroPress dalam gaya poster konser punk — bold, berantakan, dan penuh karakter.", "Concert poster grunge AeroPress", "Summer"),
    ("french_press_warm","French Press · Warmth",  "4 Menit Ketenangan",    "Brew Method",
     "French press di meja kayu dengan buku terbuka dan sinar pagi — cozy morning.", "Cozy morning French Press scene", "Winter"),
    ("espresso_science", "Espresso · Physics",     "25 Detik Fisika",       "Brew Method",
     "Diagram fisika ekstraksi espresso — tekanan 9 bar, suhu, partikel, dan aliran.", "Physics diagram espresso extraction", "Autumn"),
    ("cold_brew_night",  "Cold Brew · Night",      "18 Jam Dalam Dingin",   "Brew Method",
     "Cold brew jar di kulkas malam hari — bintang Orion terlihat dari jendela.", "Cold brew jar with Orion outside window", "Winter"),
    ("siphon_theatre",   "Siphon · Theatre",       "Sains adalah Seni",     "Brew Method",
     "Siphon brewer dalam gaya poster teater vintage — dramatis dan teatrikal.", "Vintage theatre poster siphon", "Autumn"),
    ("moka_journey",     "Moka Pot · Journey",     "Italia Bertemu Nusantara","Brew Method",
     "Moka pot dengan latar belakang peta perjalanan dari Napoli ke Nusantara.", "Moka journey map Napoli to Nusantara", "Summer"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — COIN, TRADING CARD, PIN, PATCH, STICKER DESIGNS
# ═══════════════════════════════════════════════════════════════════════════════

COIN_DESIGNS = [
    # (key, name, series, obverse_desc, reverse_desc, material_default, edition, world_note)

    # ── Outpost Series (27 outpost) ───────────────────────────────────────────
    *[
        (f"coin_outpost_{n:02d}", f"Outpost {n:02d} Coin", "Archipelagic Outposts",
         f"Relief Outpost {n:02d} dengan nama resminya terukir di tepi luar",
         "Balik: Logo The Four Expeditions + tahun pendirian Outpost",
         "Bronze", "Standard Edition",
         f"Koin memorial Outpost {n:02d} — bukti fisik bahwa ekspeditor pernah ada di sana.")
        for n in [1,2,3,4,5,6,7,8,9,10,11,14,15,16,17,18,22,23,24,25,26,30,31,32,33,35,29]
    ],

    # ── Origin Landmark Series (10) ───────────────────────────────────────────
    ("coin_aceh_gayo",    "Aceh Gayo Landmark",   "Origin Series",  "Relief kebun kopi Gayo dengan Danau Laut Tawar","Logo The Four Expeditions + koordinat","Silver","Rare Edition","Koin perak dari tanah kopi pertama Nusantara."),
    ("coin_toraja",       "Toraja Sapan",         "Origin Series",  "Tongkonan Toraja dengan pohon kopi","Tahun 1890 — tahun kopi Toraja mulai dikenal","Silver","Rare Edition","Koin perak dari tanah kopi Sulawesi."),
    ("coin_kintamani",    "Bali Kintamani",       "Origin Series",  "Kaldera Batur dengan kebun kopi","GI Kintamani — Indikasi Geografis pertama kopi Indonesia","Silver","Rare Edition","Koin perak dari satu-satunya kopi ber-GI di Indonesia."),
    ("coin_wamena",       "Papua Wamena",         "Origin Series",  "Lembah Baliem Papua dari udara","Koordinat: 4°06'S 138°57'E — Ujung Timur","Gold","Ultra-Rare","Koin emas dari origin paling langka — produksi terbatas 100 koin per tahun."),
    ("coin_mandheling",   "Mandheling Heritage",  "Origin Series",  "Danau Toba dari ketinggian","Tahun 1888 — tahun kopi Mandheling pertama diekspor","Silver","Rare Edition","Koin perak dari origin yang mengubah reputasi kopi Sumatera."),
    ("coin_bajawa",       "Flores Bajawa",        "Origin Series",  "Gunung Inerie Flores","Altitude 1200–1800 mdpl","Silver","Rare Edition","Koin perak dari ujung timur kopi Nusantara."),
    ("coin_preanger",     "Java Preanger",        "Origin Series",  "Perkebunan Priangan colonial","Tahun 1725 — cultuurstelsel kopi pertama","Silver","Rare Edition","Koin perak dari sejarah kopi Jawa yang penuh kontradiksi."),
    ("coin_solok",        "Solok Radjo",          "Origin Series",  "Danau Singkarak Sumatera Barat","Coffee Wine Process — inovasi tanpa henti","Silver","Rare Edition","Koin perak dari laboratorium fermentasi hidup."),
    ("coin_dogiyai",      "Papua Dogiyai",        "Origin Series",  "Pegunungan Tengah Papua","2000 mdpl — highest altitude coffee in Indonesia","Gold","Ultra-Rare","Koin emas dari kopi dengan ketinggian tertinggi di Nusantara."),
    ("coin_rinjani",      "Sembalun Rinjani",     "Origin Series",  "Gunung Rinjani dari Lombok","GI pending — altitude 1000–2000 mdpl","Silver","Rare Edition","Koin perak dari lereng gunung berapi aktif."),

    # ── Special Event Series (8) ──────────────────────────────────────────────
    ("coin_grand_curator","Grand Curator Medal",  "Achievement",    "Sang Kurator berdiri di The Final Meridian","35 Outpost stamps imprinted on edge","Gold","Grand Curator Only","Koin emas yang hanya bisa didapat setelah menyelesaikan seluruh ekspedisi."),
    ("coin_founding",     "Founding Expedition",  "Special",        "Tanggal berdirinya Kafe Nusantara","'In the beginning there was a bean'","Gold","Founding Edition","Koin edisi pendiri — hanya tersedia di hari jadi pertama."),
    ("coin_four_exp",     "The Four Expeditions", "Special",        "Empat simbol season dalam satu koin","Winter-Summer-Autumn-Spring unified","Silver","Annual Release","Koin tahunan yang merayakan satu putaran penuh The Four Expeditions."),
    ("coin_passport",     "Expedition Passport",  "Achievement",    "Buku paspor terbuka dengan semua stempel","'The journey never ends — it transforms'","Bronze","Member Gift","Koin gift untuk semua member baru Kafe Nusantara."),
    ("coin_first_batch",  "First Batch",          "Production",     "Tanggal roasting batch pertama","Serial number + batch number terukir","Bronze","Production Run","Koin untuk setiap batch produksi — menandai momen peluncuran blend baru."),
    ("coin_solstice",     "Winter Solstice",      "Seasonal",       "The Dark Passage — malam terpanjang","'In darkness we find the warmest cup'","Silver","Seasonal"),
    ("coin_equinox_sp",   "Spring Equinox",       "Seasonal",       "The First Ascent — keseimbangan lahir","'Equal night, equal light'","Bronze","Seasonal"),
    ("coin_harvest",      "Harvest Moon",         "Seasonal",       "The Amber Descent — bulan panen","'Earth gives, we receive, we return'","Silver","Seasonal"),
]

# Tambahkan world_note untuk seasonal coins yang hilang
COIN_DESIGNS = [c if len(c) >= 9 else c + (f"Koin seasonal {c[1]} — hanya tersedia selama season berlangsung.",) for c in COIN_DESIGNS]

TRADING_CARDS = [
    # ── Outpost Character Cards (35) ─────────────────────────────────────────
    *[
        (f"card_outpost_{n:02d}", f"Outpost {n:02d}", "Outpost Chronicles",
         f"Ilustrasi karakter unik Outpost {n:02d} dalam gaya art card premium",
         f"Stats: Location · Specialty · Signature Blend · Founded Year",
         "Character Card", "N/A",
         f"Kartu koleksi Outpost {n:02d} — lengkap dengan lore, specialty, dan blend signature.")
        for n in [1,2,3,4,5,6,7,8,9,10,11,14,15,16,17,18,22,23,24,25,26,29,30,31,32,33,35,36,37,38,39,40,41,42,43]
    ],

    # ── Origin Profile Cards (31) ─────────────────────────────────────────────
    *[
        (f"card_origin_{key}", f"{name} Origin", "Origin Atlas",
         f"Ilustrasi peta dan profil origin {name} dengan botanical illustration",
         f"Flavor notes · Altitude · Process · Outpost affiliation",
         "Origin Card", "N/A",
         f"Kartu atlas origin {name} — panduan lengkap untuk ekspeditor dan barista.")
        for key, name in [
            ("aceh_gayo","Aceh Gayo"),("arjuno","Gunung Arjuno"),("kintamani","Bali Kintamani"),
            ("ulian","Bali Ulian"),("bajawa","Flores Bajawa"),("bengkulu","Bengkulu"),
            ("bukit_barisan","Bukit Barisan"),("ciwidey","Java Ciwidey"),("dampit","Dampit Malang"),
            ("dogiyai","Papua Dogiyai"),("manggarai","Flores Manggarai"),("garut","Java Garut"),
            ("halu","Gunung Halu"),("ijen","Ijen Raung"),("kalosi","Toraja Kalosi"),
            ("kayu_aro","Kerinci Kayu Aro"),("lampung","Lampung"),("lintong","Lintong"),
            ("mandheling","Mandheling"),("manglayang","Java Manglayang"),("preanger","Java Preanger"),
            ("puntang","Java Puntang"),("rinjani","Sembalun Rinjani"),("sapan","Toraja Sapan"),
            ("semeru","Java Semeru"),("sidikalang","Sidikalang"),("sindoro","Java Sindoro"),
            ("solok","Solok Radjo"),("temanggung","Java Temanggung"),("wamena","Papua Wamena"),
            ("kamojang","Wanoja Kamojang"),
        ]
    ],

    # ── Season Universe Cards (4) ─────────────────────────────────────────────
    ("card_winter_uni",  "The Dark Passage",     "Season Universe", "Full-art ilustrasi jalur pegunungan gelap Winter","Season lore + signature flavor + universe tagline","Universe Card","N/A","Kartu universe Winter — lore lengkap The Dark Passage."),
    ("card_summer_uni",  "The Open Horizon",     "Season Universe", "Full-art kapal di lautan Summer","Season lore + signature flavor + universe tagline","Universe Card","N/A","Kartu universe Summer — lore lengkap The Open Horizon."),
    ("card_autumn_uni",  "The Amber Descent",    "Season Universe", "Full-art ekspeditor turun gunung Autumn","Season lore + signature flavor + universe tagline","Universe Card","N/A","Kartu universe Autumn — lore lengkap The Amber Descent."),
    ("card_spring_uni",  "The First Ascent",     "Season Universe", "Full-art langkah pertama di Spring","Season lore + signature flavor + universe tagline","Universe Card","N/A","Kartu universe Spring — lore lengkap The First Ascent."),

    # ── Blend Character Cards (10 iconic) ─────────────────────────────────────
    ("card_grand_art_1", "Grand Artifact #001",  "Legendary Blends","Full-art blend paling kompleks T3 — 4 biji dari 3 pulau","Complexity score 81/100 · Papua × Aceh × Toraja","Legendary Card","N/A","Kartu legendaris blend T3 paling tinggi skornya."),
    ("card_grand_art_2", "Grand Artifact #002",  "Legendary Blends","Anaerobic + Wine + Wet-Hulled triple process","Rarity: 1 dari 7 miliar kombinasi yang dipilih","Legendary Card","N/A","Kartu blend dual-ferment yang mendekati mustahil."),
    ("card_curator",     "Sang Kurator",         "Character",       "Karakter Sang Kurator di The Final Meridian","'Dari 7 miliar kemungkinan — 9.999 yang dipilih'","Character Card","N/A","Kartu karakter utama — Sang Kurator yang membangun seluruh ekspedisi."),
    ("card_barista",     "The Barista",          "Character",       "Karakter barista di balik mesin espresso","'Setiap cangkir adalah tanda tangan'","Character Card","N/A","Kartu karakter barista — tangan yang menghidupkan setiap blend."),
    ("card_farmer",      "The Farmer",           "Character",       "Karakter petani kopi di lereng gunung","'Sebelum cangkir ada tangan yang menanam'","Character Card","N/A","Kartu karakter petani — awal dari seluruh perjalanan kopi."),
    ("card_expedition",  "The Expeditor",        "Character",       "Karakter member Paspor Ekspedisi","Tier: Novice → Field Surveyor → Senior → Master → Grand Curator","Character Card","N/A","Kartu karakter ekspeditor — perjalanan dari nol ke Grand Reserve."),
    ("card_roaster",     "The Roastmaster",      "Character",       "Karakter roastmaster di The Final Meridian","'Green bean speaks, we listen and translate'","Character Card","N/A","Kartu karakter roastmaster — penerjemah antara biji dan cangkir."),
    ("card_paspor",      "Expedition Passport",  "Item",            "Buku paspor dengan halaman yang mulai terisi","Collect 35 stamps to unlock The Grand Reserve","Item Card","N/A","Kartu item — Paspor Ekspedisi sebagai objek dalam game koleksi."),
    ("card_compass",     "The Expedition Compass","Item",           "Kompas antik dengan koordinat 35 Outpost","'Every direction leads to a new origin'","Item Card","N/A","Kartu item — kompas navigasi ekspeditor."),
    ("card_logbook",     "The Field Logbook",    "Item",            "Logbook lapangan penuh catatan dan sketsa","'Every page is a journey completed'","Item Card","N/A","Kartu item — logbook tempat semua catatan ekspedisi tersimpan."),
    ("card_final_mer",   "The Final Meridian",   "Location",        "Full-art The Final Meridian dari dalam","'This is where all expeditions end — and begin'","Location Card","N/A","Kartu lokasi The Final Meridian — destinasi akhir setiap ekspeditor."),

]

PIN_DESIGNS = [
    # (key, name, series, design_desc, material, size_mm, world_note)
    # ── Season Series (4) ─────────────────────────────────────────────────────
    ("pin_winter",    "Pin Winter",        "Season",     "Ikon The Dark Passage — kobaran api dalam kegelapan","Hard Enamel","25mm","Pin identitas season Winter — dipakai ekspeditor The Dark Passage."),
    ("pin_summer",    "Pin Summer",        "Season",     "Ikon The Open Horizon — layar kapal di cakrawala","Hard Enamel","25mm","Pin identitas season Summer — The Open Horizon collection."),
    ("pin_autumn",    "Pin Autumn",        "Season",     "Ikon The Amber Descent — kompas antik berwarna amber","Hard Enamel","25mm","Pin identitas season Autumn — The Amber Descent collection."),
    ("pin_spring",    "Pin Spring",        "Season",     "Ikon The First Ascent — bunga pertama di lereng gunung","Hard Enamel","25mm","Pin identitas season Spring — The First Ascent collection."),
    # ── Tier Series (3) ───────────────────────────────────────────────────────
    ("pin_vanguard",  "Pin T1 Vanguard",   "Tier",       "Ikon berlian biru gelap dengan tulisan 'VANGUARD'","Hard Enamel","20mm","Pin tier T1 — identitas ekspeditor Vanguard."),
    ("pin_curator",   "Pin T2 Curator",    "Tier",       "Ikon mahkota ganda dengan tulisan 'CURATOR'","Hard Enamel Gold","22mm","Pin tier T2 — identitas ekspeditor Curator's Reserve."),
    ("pin_artifact",  "Pin T3 Artifact",   "Tier",       "Ikon bintang berlapis dengan tulisan 'GRAND ARTIFACT'","Die-Cut Gold Glitter","25mm","Pin tier T3 — identitas ekspeditor Grand Artifact. Ultra-rare."),
    # ── Tool Icon Series (9) ──────────────────────────────────────────────────
    ("pin_v60",       "Pin V60",           "Tools",      "Siluet V60 dripper dengan spiral ribbing khas","Hard Enamel","22mm","Pin alat V60 — untuk ekspeditor pour over."),
    ("pin_chemex",    "Pin Chemex",        "Tools",      "Siluet Chemex dengan collar kayu","Hard Enamel","22mm","Pin alat Chemex — ikon desain klasik."),
    ("pin_aeropress", "Pin AeroPress",     "Tools",      "Siluet AeroPress dalam posisi inverted","Hard Enamel","22mm","Pin alat AeroPress — senjata ekspeditor lapangan."),
    ("pin_frenchpress","Pin French Press", "Tools",      "Siluet French Press dengan plunger terangkat","Hard Enamel","22mm","Pin alat French Press — yang paling demokratis."),
    ("pin_moka",      "Pin Moka Pot",      "Tools",      "Siluet Moka Pot 6-cup stovetop klasik","Hard Enamel","20mm","Pin alat Moka Pot — Italia bertemu Nusantara."),
    ("pin_espresso",  "Pin Espresso",      "Tools",      "Siluet mesin espresso semi-auto","Hard Enamel","25mm","Pin alat espresso — engine di balik setiap Outpost."),
    ("pin_grinder",   "Pin Grinder",       "Tools",      "Siluet hand grinder conical dari samping","Hard Enamel","22mm","Pin alat grinder — awal dari segalanya."),
    ("pin_kettle",    "Pin Gooseneck",     "Tools",      "Siluet gooseneck kettle dengan leher panjang","Hard Enamel","22mm","Pin alat gooseneck — tarian air di atas V60."),
    ("pin_scale",     "Pin Scale",         "Tools",      "Siluet timbangan kopi dengan display digital","Hard Enamel","20mm","Pin alat scale — kompas presisi ekspeditor."),
    # ── Achievement Series (6) ────────────────────────────────────────────────
    ("pin_first_stamp","Pin First Stamp",  "Achievement","Stempel pertama Paspor Ekspedisi — hari pertama bergabung","Soft Enamel","22mm","Pin penanda hari pertama ekspedisi dimulai."),
    ("pin_5_outpost", "Pin 5 Outposts",   "Achievement","Angka 5 dengan bintang — Field Surveyor milestone","Hard Enamel Bronze","22mm","Pin pencapaian 5 Outpost — Field Surveyor tier."),
    ("pin_10_outpost","Pin 10 Outposts",  "Achievement","Angka 10 dengan mahkota — Senior Cartographer","Hard Enamel Silver","22mm","Pin pencapaian 10 Outpost — Senior Cartographer tier."),
    ("pin_20_outpost","Pin 20 Outposts",  "Achievement","Angka 20 dengan teleskop — Master Explorer","Hard Enamel Gold","25mm","Pin pencapaian 20 Outpost — Master Explorer tier."),
    ("pin_grand_curator","Pin Grand Curator","Achievement","Paspor penuh dengan tulisan 'GRAND CURATOR'","Die-Cut Gold Premium","30mm","Pin tertinggi — hanya untuk yang telah mengunjungi semua Outpost."),
    ("pin_annual",    "Pin Annual",       "Special",    "Desain eksklusif tahunan — berubah setiap tahun","Glow in the Dark","25mm","Pin tahunan edisi terbatas — hanya tersedia selama satu tahun."),
    # ── Constellation Mini Series (26) ────────────────────────────────────────
    *[
        (f"pin_const_{c[3].lower()}", f"Pin {c[1]}", "Constellation Mini",
         f"Pola bintang {c[1]} ({c[3]}) dengan garis penghubung minimal",
         "Hard Enamel Glow","18mm", c[7])
        for c in CONSTELLATIONS[:26]
    ],
]

PATCH_DESIGNS = [
    # (key, name, series, emblem_desc, size, border, world_note)
    *[
        (f"patch_outpost_{n:02d}", f"Outpost {n:02d} Emblem", "Outpost Emblems",
         f"Emblem resmi Outpost {n:02d} — lambang, nama resmi, dan koordinat",
         "7cm", "Merit Badge Style",
         f"Patch identitas Outpost {n:02d} — dijahitkan pada jaket ekspedisi sebagai tanda kunjungan.")
        for n in [1,2,3,4,5,6,7,8,9,10,11,14,15,16,17,18,22,23,24,25,26,29,30,31,32,33,35]
    ],
    ("patch_grand_curator","Grand Curator Emblem","Achievement","Lambang Grand Curator — mahkota dan paspor","10cm","Gold Border","Patch tertinggi — hanya Grand Curator yang berhak memakainya."),
    ("patch_expedition",  "The Four Expeditions","Series Logo","Logo lengkap The Four Expeditions — 4 season unified","8cm","Standard Border","Patch utama identitas Kafe Nusantara."),
    ("patch_roastery",    "The Final Meridian",  "Location",  "Logo Roastery The Final Meridian","7cm","Copper Border","Patch lokasi roastery utama — simbol asal semua blend."),
    ("patch_first_light", "First Light",         "Session",   "Ikon First Light 07:00–12:00","6cm","Standard Border","Patch sesi First Light — untuk ekspeditor pagi hari."),
    ("patch_midday",      "Midday Transit",      "Session",   "Ikon Midday Transit 12:00–18:00","6cm","Standard Border","Patch sesi Midday Transit."),
    ("patch_twilight",    "Twilight Bivouac",    "Session",   "Ikon Twilight Bivouac 18:00–tutup","6cm","Standard Border","Patch sesi Twilight Bivouac — untuk ekspeditor malam hari."),
    ("patch_passport",    "Expedition Passport", "Achievement","Logo Paspor Ekspedisi","7cm","Standard Border","Patch identitas member — dijahit di tas atau jaket sejak hari pertama."),
]

STICKER_THEMES = [
    # (key, name, format_type, contents, world_note)
    ("stk_season_winter", "Winter Pack",          "A5 Sheet",   "12 stiker tema The Dark Passage — outpost, bintang, dan kopi Winter","Pack stiker winter untuk laptop, botol, dan jurnal."),
    ("stk_season_summer", "Summer Pack",          "A5 Sheet",   "12 stiker tema The Open Horizon — kapal, rute, dan kopi Summer","Pack stiker summer — cerah dan penuh energi."),
    ("stk_season_autumn", "Autumn Pack",          "A5 Sheet",   "12 stiker tema The Amber Descent — artefak, alat, dan kopi Autumn","Pack stiker autumn — hangat dan nostalgic."),
    ("stk_season_spring", "Spring Pack",          "A5 Sheet",   "12 stiker tema The First Ascent — alam, bunga, dan kopi Spring","Pack stiker spring — fresh dan hopeful."),
    ("stk_outpost_jawa",  "Jawa Outpost Pack",    "A5 Sheet",   "12 stiker 22 Outpost Jawa yang paling ikonik dalam gaya stamp","Pack stiker semua Outpost Jawa."),
    ("stk_outpost_sumbar","Sumatra & Beyond Pack","A5 Sheet",   "12 stiker Outpost luar Jawa — Sumatera, Bali, Sulawesi, Papua","Pack stiker ekspansi nusantara."),
    ("stk_constellations","Star Map Pack",        "A5 Sheet",   "12 stiker rasi bintang gaya vintage — termasuk Crux dan Orion","Pack stiker navigasi bintang untuk ekspeditor."),
    ("stk_tools",         "Brew Tools Pack",      "A5 Sheet",   "12 stiker alat kopi — V60, Chemex, AeroPress, Moka, dan lainnya","Pack stiker alat untuk barista dan home brewer."),
    ("stk_origin_id",     "Origin Indonesia Pack","A5 Sheet",   "12 stiker origin kopi Indonesia dengan ilustrasi botanical","Pack stiker origin untuk pecinta kopi single origin."),
    ("stk_phrases",       "Expedition Quotes Pack","A5 Sheet",  "12 stiker kutipan ekspedisi dari jurnal Sang Kurator","Pack stiker kutipan motivasi perjalanan."),
    ("stk_characters",    "Characters Pack",      "A5 Sheet",   "12 stiker karakter — Kurator, Barista, Petani, Ekspeditor","Pack stiker karakter utama The Four Expeditions."),
    ("stk_passport_stamps","Passport Style Pack", "Die-Cut",    "12 stiker gaya stempel paspor dari setiap Outpost yang dikunjungi","Pack stiker gaya stempel — untuk journal atau planner."),
    ("stk_holographic",   "Holographic Blend Pack","Holographic","8 stiker holografik — T3 Grand Artifact blend dan rasi bintang langka","Pack stiker holografik ultra-premium — limited print run."),
    ("stk_mini_coins",    "Mini Coin Stickers",   "Die-Cut",    "15 stiker kecil bergaya koin logam — semua seri outpost","Pack stiker gaya koin untuk koleksi."),
    ("stk_botanical",     "Plant Source Pack",    "A5 Sheet",   "12 stiker botanical illustration — 12 tanaman sumber addon terbaik","Pack stiker botanical untuk pecinta alam dan kopi."),
    ("stk_grand_curator", "Grand Curator Set",    "Holographic","6 stiker premium set — hanya tersedia untuk Grand Curator member","Pack stiker eksklusif Grand Curator — tidak dijual bebas."),
    ("stk_craft_coffee",  "Craft Coffee Pack",    "Die-Cut",    "10 stiker craft coffee culture — latte art, cupping, dan tools","Pack stiker craft coffee untuk komunitas barista."),
    ("stk_nusantara_map", "Nusantara Map Pack",   "A5 Sheet",   "4 stiker besar peta Nusantara dengan semua 35 Outpost ditandai","Pack stiker peta besar untuk dinding atau planner."),
    ("stk_brewing_guide", "Brewing Guide Pack",   "A5 Sheet",   "8 stiker tip brewing — suhu, gramasi, dan waktu setiap metode","Pack stiker panduan brewing untuk dapur barista."),
    ("stk_anniversary",   "Anniversary Edition",  "Holographic","12 stiker anniversary edisi terbatas — berubah setiap tahun","Pack anniversary holografik — collector's item tahunan."),
    ("stk_mini_origins",  "Mini Origins Pack",    "Die-Cut",    "20 stiker kecil bulat semua 31 origin + 4 season","Pack stiker mini origin — lengkap 31 origin Nusantara."),
    ("stk_expedition_log","Expedition Log Pack",  "Die-Cut",    "10 stiker jurnal lapangan — tanggal, koordinat, dan notasi brewlog","Pack stiker untuk mencatat di jurnal atau brew log."),
    ("stk_tools_detail",  "Tools Detail Pack",    "A5 Sheet",   "8 stiker besar detail teknis alat — V60 anatomy, Chemex exploded","Pack stiker ilustrasi teknis alat untuk barista."),
    ("stk_animal_coffee", "Coffee Animals Pack",  "Die-Cut",    "12 stiker hewan lokal Nusantara yang terasosiasi dengan origin kopi","Pack stiker fauna Nusantara dan kopi — cendrawasih, tapir, maleo."),
    ("stk_diecut_brew",   "Brew Shape Pack",      "Die-Cut",    "8 stiker die-cut berbentuk alat kopi 3D-style — sangat detail","Pack stiker die-cut premium berbentuk alat brewing."),
    ("stk_reward_silver", "Silver Member Pack",   "Holographic","10 stiker khusus member Silver — upgrade dari Bronze","Pack reward member Silver — lebih premium."),
    ("stk_reward_gold",   "Gold Member Pack",     "Holographic","10 stiker khusus member Gold tier","Pack reward member Gold — eksklusif dan limited."),
    ("stk_reward_plat",   "Platinum Member Pack", "Holographic","8 stiker ultra-premium member Platinum — full holographic","Pack reward member Platinum — tertinggi di luar Grand Curator."),
    ("stk_region_sumatra","Sumatra Stories Pack", "A5 Sheet",   "12 stiker cerita kopi Sumatera — dari Gayo ke Lampung","Pack stiker narasi kopi Sumatera."),
    ("stk_region_java",   "Java Stories Pack",    "A5 Sheet",   "12 stiker cerita kopi Jawa — dari Preanger ke Ijen","Pack stiker narasi kopi Jawa."),
    ("stk_region_east",   "Eastern Islands Pack", "A5 Sheet",   "12 stiker kopi Bali, Flores, Sulawesi, dan Papua","Pack stiker narasi kopi Indonesia Timur."),
    ("stk_blend_t3",      "Grand Artifact Pack",  "Holographic","8 stiker blend T3 terpilih — nama dan complexity score","Pack stiker ultra-rare untuk blend T3 paling kompleks."),
    ("stk_flavor_wheel",  "Flavor Wheel Pack",    "Die-Cut",    "1 stiker besar flavor wheel + 9 stiker kategori rasa","Pack stiker flavor wheel untuk edukasi dan dekorasi."),
    ("stk_daily_exp",     "Daily Expedition Pack","A5 Sheet",   "12 stiker rutinitas kopi harian — First Light, Midday, Twilight","Pack stiker 3 sesi The Daily Expedition."),
    ("stk_kombucha_kopi", "Fermentation Pack",    "A5 Sheet",   "10 stiker proses fermentasi kopi — anaerobic, wine, carbonic mac","Pack stiker proses fermentasi untuk kafein nerd."),
    ("stk_altitude",      "Altitude Pack",        "Die-Cut",    "8 stiker kontur ketinggian origin kopi — dari 400 mdpl ke 2000 mdpl","Pack stiker peta ketinggian — altitude matters in coffee."),
    ("stk_latte_art",     "Latte Art Pack",       "Die-Cut",    "8 stiker pola latte art — tulip, rosetta, heart, swan","Pack stiker latte art untuk barista kreatif."),
    ("stk_cold_brew_kit", "Cold Brew Kit Pack",   "A5 Sheet",   "10 stiker panduan cold brew — jar, grind size, time, serve","Pack stiker panduan cold brew lengkap."),
    ("stk_espresso_tips", "Espresso Tips Pack",   "A5 Sheet",   "10 stiker tips espresso — tamping, distribution, extraction","Pack stiker tips espresso untuk barista."),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — PRICING TABLES
# ═══════════════════════════════════════════════════════════════════════════════

PRICING = {
    # (category_key): {tier: (lo, hi)}
    "mug": {
        "T1": (85_000,  185_000),
        "T2": (165_000, 385_000),
        "T3": (350_000, 850_000),
    },
    "tumbler": {
        "T1": (125_000, 275_000),
        "T2": (250_000, 550_000),
        "T3": (500_000, 1_500_000),
    },
    "tshirt": {
        "T1": (95_000,  195_000),
        "T2": (185_000, 395_000),
        "T3": (375_000, 950_000),
    },
    "coin": {
        "Bronze": (85_000,  175_000),
        "Silver": (200_000, 495_000),
        "Gold":   (550_000, 1_500_000),
    },
    "trading_card": {
        "Common":      (15_000,  35_000),
        "Uncommon":    (35_000,  85_000),
        "Rare":        (85_000,  250_000),
        "Holographic": (250_000, 750_000),
    },
    "pin": {
        "T1": (45_000,  95_000),
        "T2": (85_000,  185_000),
        "T3": (175_000, 450_000),
    },
    "patch": {
        "T1": (55_000,  120_000),
        "T2": (115_000, 250_000),
        "T3": (240_000, 600_000),
    },
    "sticker": {
        "T1": (25_000,  55_000),
        "T2": (50_000,  115_000),
        "T3": (110_000, 280_000),
    },
}

TIER_META = {
    "T1": {"name": "Tier 1 — Common",      "label": "Standard"},
    "T2": {"name": "Tier 2 — Rare",         "label": "Limited Run"},
    "T3": {"name": "Tier 3 — Ultra-Rare",   "label": "Collector's Edition"},
}

MUG_VARIANTS  = [("Ceramic 250ml","MUG-250-CER"),("Ceramic 350ml","MUG-350-CER"),("Enamel 300ml","MUG-300-ENM"),("Stainless 300ml","MUG-300-STL")]
TUMBLER_VARIANTS=[("350ml Stainless","TMB-350"),("500ml Stainless","TMB-500"),("750ml Stainless","TMB-750"),("500ml Titanium","TMB-500-TIT"),("350ml Copper","TMB-350-COP")]
SHIRT_VARIANTS = [("S Unisex","SHT-S"),("M Unisex","SHT-M"),("L Unisex","SHT-L"),("XL Unisex","SHT-XL"),("XXL Unisex","SHT-XXL"),("S Women","SHT-SW"),("M Women","SHT-MW"),("L Women","SHT-LW"),("S Oversized","SHT-SO"),("L Oversized","SHT-LO")]
COIN_METALS    = [("Bronze","CN-BRZ"),("Silver","CN-SLV"),("Gold","CN-GLD")]
CARD_RARITIES  = [("Common","CRD-CMN"),("Uncommon","CRD-UNC"),("Rare","CRD-RAR"),("Holographic","CRD-HOL")]
PIN_VARIANTS   = [("Standard","PIN-STD"),("Limited Edition","PIN-LTD")]
PATCH_VARIANTS = [("Iron-On","PCH-IRN"),("Sew-On","PCH-SEW")]
STICKER_FORMATS= [("A5 Sheet","STK-A5"),("Die-Cut Single","STK-DC"),("Holographic","STK-HOL")]

def price_range(cat_key, tier_or_sub):
    p = PRICING.get(cat_key, {})
    lo, hi = p.get(tier_or_sub, (50_000, 200_000))
    return int(lo + (hi-lo) * (0.2 + random.random() * 0.65))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — ITEM BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

_sku_ctr = {}

def next_sku(prefix, tier):
    k = f"{prefix}_{tier}"
    _sku_ctr[k] = _sku_ctr.get(k, 0) + 1
    return f"MRC-{prefix}-{tier}-{_sku_ctr[k]:04d}"

def constellation_tier(c):
    # Rasi paling terkenal = T2/T3; sisanya T1
    famous = {"orion","ursa_major","ursa_minor","cassiopeia","crux","canis_major",
              "scorpius","sagittarius","leo","virgo","Perseus","gemini","taurus"}
    mythic = {"orion","crux","sagittarius","cassiopeia","canis_major"}
    if c[0] in mythic:     return "T3"
    if c[0] in famous:     return "T2"
    return "T1"

def build_mug_items():
    items = []
    for c in CONSTELLATIONS:
        tier = constellation_tier(c)
        key, latin, id_name, abbr, hemi, myth, n_stars, world = c
        name_base = f"Mug {latin} — {id_name}"
        desc = (
            f"Mug dengan desain rasi bintang {latin} ({abbr}) — {id_name}. "
            f"Bintang utama: {n_stars}. Belahan langit: {hemi}. "
            f"Mitologi: {myth[:120]}. {world}"
        )
        for var_label, var_code in MUG_VARIANTS:
            p = price_range("mug", tier)
            sku = f"{next_sku('MUG', tier)}-{var_code}"
            items.append({
                "barcode": f"MRC-MUG-{key[:8].upper()}-{var_code}",
                "name": f"{name_base} [{var_label}]"[:254],
                "description": desc[:490],
                "category": "Merch Mug",
                "unit_key": "unit_pcs",
                "tier": tier, "has_expiry": False, "track_batch": True,
                "min_stock": 2, "max_stock": 50,
                "variants": [{"sku": sku, "size_weight": var_label,
                               "price_buy": int(p*0.55), "price_sell": p}],
                "attrs": {
                    "item_type": "Mug", "design_key": key, "constellation_latin": latin,
                    "constellation_id": id_name, "abbreviation": abbr,
                    "hemisphere": hemi, "main_stars": str(n_stars),
                    "mythology": myth[:250], "world_note": world,
                    "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                    "variant": var_label, "material": var_code.split("-")[-1],
                    "season_pairing": _const_season(key),
                    "outpost_pairing": _const_outpost(key),
                },
            })
    return items

def build_tumbler_items():
    items = []
    for c in CONSTELLATIONS:
        tier = constellation_tier(c)
        key, latin, id_name, abbr, hemi, myth, n_stars, world = c
        name_base = f"Tumbler {latin} — {id_name}"
        desc = (
            f"Tumbler double-wall dengan desain rasi bintang {latin} ({abbr}). "
            f"{world} Bintang utama: {n_stars}, belahan {hemi}."
        )
        for var_label, var_code in TUMBLER_VARIANTS:
            p = price_range("tumbler", tier)
            sku = f"{next_sku('TMB', tier)}-{var_code}"
            items.append({
                "barcode": f"MRC-TMB-{key[:8].upper()}-{var_code}",
                "name": f"{name_base} [{var_label}]"[:254],
                "description": desc[:490],
                "category": "Merch Tumbler",
                "unit_key": "unit_pcs",
                "tier": tier, "has_expiry": False, "track_batch": True,
                "min_stock": 2, "max_stock": 30,
                "variants": [{"sku": sku, "size_weight": var_label,
                               "price_buy": int(p*0.55), "price_sell": p}],
                "attrs": {
                    "item_type": "Tumbler", "design_key": key, "constellation_latin": latin,
                    "constellation_id": id_name, "abbreviation": abbr,
                    "hemisphere": hemi, "main_stars": str(n_stars),
                    "mythology": myth[:250], "world_note": world,
                    "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                    "variant": var_label, "season_pairing": _const_season(key),
                },
            })
    return items

def build_tshirt_items():
    items = []
    for theme in TSHIRT_THEMES:
        key, title, subtitle, cat, desc_full, visual, season = theme
        # Determine tier from category
        tier = "T3" if "Special Edition" in cat or "Achievement" in cat else \
               "T2" if "Series" in cat and ("Outpost" in cat or "Season" in cat) else "T1"
        for var_label, var_code in SHIRT_VARIANTS:
            p = price_range("tshirt", tier)
            sku = f"{next_sku('SHT', tier)}-{var_code}"
            items.append({
                "barcode": f"MRC-SHT-{key[:8].upper()}-{var_code}",
                "name": f"Kaos {title} [{var_label}]"[:254],
                "description": (
                    f"Kaos {title} — {subtitle}. {desc_full} "
                    f"Visual concept: {visual}. Season: {season} · {SEASON_UNIVERSE.get(season,'')}."
                )[:490],
                "category": "Merch T-Shirt",
                "unit_key": "unit_pcs",
                "tier": tier, "has_expiry": False, "track_batch": False,
                "min_stock": 3, "max_stock": 100,
                "variants": [{"sku": sku, "size_weight": var_label,
                               "price_buy": int(p*0.55), "price_sell": p}],
                "attrs": {
                    "item_type": "T-Shirt", "design_key": key, "design_title": title,
                    "subtitle": subtitle, "theme_category": cat,
                    "visual_concept": visual[:250], "season": season,
                    "season_universe": SEASON_UNIVERSE.get(season,""),
                    "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                    "variant": var_label,
                },
            })
    return items

def build_coin_items():
    items = []
    for coin in COIN_DESIGNS:
        key, name, series, obv, rev, metal, edition = coin[:7]
        world_note = coin[7] if len(coin) > 7 else ""
        tier = "T3" if metal == "Gold" else ("T2" if metal == "Silver" else "T1")
        p = price_range("coin", metal)
        sku = f"{next_sku('COIN', tier)}-CN-{metal[:3].upper()}"
        items.append({
            "barcode": f"MRC-COIN-{key[:10].upper()}-{metal[:3].upper()}",
            "name": f"{name} — {metal}"[:254],
            "description": (
                f"Koin logam {metal.lower()} — {name}. Seri: {series}. "
                f"Obverse: {obv}. Reverse: {rev}. Edisi: {edition}. {world_note}"
            )[:490],
            "category": "Merch Coin",
            "unit_key": "unit_pcs",
            "tier": tier, "has_expiry": False, "track_batch": True,
            "min_stock": 1 if tier == "T3" else 5,
            "max_stock": 10 if tier == "T3" else (50 if tier == "T2" else 200),
            "variants": [{"sku": sku, "size_weight": f"{metal} — 40mm",
                          "price_buy": int(p*0.50), "price_sell": p}],
            "attrs": {
                "item_type": "Merchant Coin", "design_key": key, "coin_series": series,
                "metal": metal, "edition": edition,
                "obverse_design": obv[:250], "reverse_design": rev[:250],
                "world_note": world_note[:250], "diameter": "40mm", "thickness": "3mm",
                "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                "collectible_category": "Numismatic",
                "availability": "Grand Reserve Only" if tier == "T3" else "All Outposts",
            },
        })
    return items

def build_card_items():
    items = []
    for card in TRADING_CARDS:
        key, name, series, front, back, card_type, special = card[:7]
        world_note = card[7] if len(card) > 7 else ""
        for rarity_label, rarity_code in CARD_RARITIES:
            tier = "T3" if rarity_label == "Holographic" else \
                   "T2" if rarity_label in ("Rare","Uncommon") else "T1"
            p = price_range("trading_card", rarity_label)
            sku = f"{next_sku('CARD', tier)}-{rarity_code}"
            items.append({
                "barcode": f"MRC-CARD-{key[:10].upper()}-{rarity_code}",
                "name": f"Trading Card: {name} [{rarity_label}]"[:254],
                "description": (
                    f"Kartu koleksi: {name}. Seri: {series}. Rarity: {rarity_label}. "
                    f"Front: {front[:120]}. Back: {back[:120]}. {world_note}"
                )[:490],
                "category": "Merch Trading Card",
                "unit_key": "unit_pcs",
                "tier": tier, "has_expiry": False, "track_batch": True,
                "min_stock": 1 if tier == "T3" else (3 if tier == "T2" else 10),
                "max_stock": 5 if tier == "T3" else (30 if tier == "T2" else 200),
                "variants": [{"sku": sku, "size_weight": f"{rarity_label} — 63×88mm",
                              "price_buy": int(p*0.40), "price_sell": p}],
                "attrs": {
                    "item_type": "Trading Card", "design_key": key,
                    "card_name": name, "card_series": series,
                    "card_type": card_type, "rarity": rarity_label,
                    "front_desc": front[:250], "back_desc": back[:250],
                    "world_note": world_note[:250],
                    "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                    "card_size": "63×88mm (standard TCG)",
                    "print_run": "Unlimited" if rarity_label == "Common" else
                                 ("Limited 1000" if rarity_label == "Uncommon" else
                                  ("Limited 100" if rarity_label == "Rare" else "Limited 20")),
                    "collectible_category": "Collectible Card Game",
                },
            })
    return items

def build_pin_items():
    items = []
    for pin in PIN_DESIGNS:
        key, name, series, design, material, size, world_note = pin
        tier = "T3" if "Ultra" in material or "Glow" in material or "Premium" in material else \
               "T2" if "Gold" in material or "Silver" in material or "Limited" in series else "T1"
        for var_label, var_code in PIN_VARIANTS:
            p = price_range("pin", tier)
            sku = f"{next_sku('PIN', tier)}-{var_code}"
            items.append({
                "barcode": f"MRC-PIN-{key[:10].upper()}-{var_code}",
                "name": f"{name} [{var_label}]"[:254],
                "description": (
                    f"Enamel pin {name}. Seri: {series}. Desain: {design}. "
                    f"Material: {material}. Ukuran: {size}. {world_note}"
                )[:490],
                "category": "Merch Pin",
                "unit_key": "unit_pcs",
                "tier": tier, "has_expiry": False, "track_batch": True,
                "min_stock": 2, "max_stock": 100 if tier == "T1" else 20,
                "variants": [{"sku": sku, "size_weight": f"{size} {var_label}",
                              "price_buy": int(p*0.50), "price_sell": p}],
                "attrs": {
                    "item_type": "Enamel Pin", "design_key": key, "pin_name": name,
                    "pin_series": series, "design_desc": design[:250],
                    "material": material, "size": size, "world_note": world_note[:250],
                    "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                    "variant": var_label, "backing_type": "Butterfly clutch",
                    "collectible_category": "Pin Badge",
                },
            })
    return items

def build_patch_items():
    items = []
    for patch in PATCH_DESIGNS:
        key, name, series, emblem, size, border, world_note = patch
        tier = "T3" if "Gold" in border or "Copper" in border else \
               "T2" if "Achievement" in series or "Curator" in name else "T1"
        for var_label, var_code in PATCH_VARIANTS:
            p = price_range("patch", tier)
            sku = f"{next_sku('PATCH', tier)}-{var_code}"
            items.append({
                "barcode": f"MRC-PCH-{key[:10].upper()}-{var_code}",
                "name": f"Patch {name} [{var_label}]"[:254],
                "description": (
                    f"Patch bordir {name}. Seri: {series}. Desain: {emblem}. "
                    f"Ukuran: {size}, bingkai {border}. {var_label}. {world_note}"
                )[:490],
                "category": "Merch Patch",
                "unit_key": "unit_pcs",
                "tier": tier, "has_expiry": False, "track_batch": False,
                "min_stock": 3, "max_stock": 50,
                "variants": [{"sku": sku, "size_weight": f"{size} {var_label}",
                              "price_buy": int(p*0.50), "price_sell": p}],
                "attrs": {
                    "item_type": "Embroidered Patch", "design_key": key,
                    "patch_name": name, "patch_series": series,
                    "emblem_desc": emblem[:250], "size": size,
                    "border_style": border, "attachment": var_label,
                    "world_note": world_note[:250],
                    "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                },
            })
    return items

def build_sticker_items():
    items = []
    for stk in STICKER_THEMES:
        key, name, fmt_type, contents, world_note = stk
        tier = "T3" if "Holographic" in fmt_type or "Grand Curator" in name or "Platinum" in name else \
               "T2" if "Gold" in name or "Silver" in name or "Premium" in fmt_type else "T1"
        for var_label, var_code in STICKER_FORMATS:
            # Only match relevant format
            if fmt_type == "Holographic" and var_code != "STK-HOL": continue
            if fmt_type == "Die-Cut"     and var_code == "STK-A5":  continue
            if fmt_type == "A5 Sheet"    and var_code == "STK-HOL": continue
            p = price_range("sticker", tier)
            sku = f"{next_sku('STK', tier)}-{var_code}"
            items.append({
                "barcode": f"MRC-STK-{key[:10].upper()}-{var_code}",
                "name": f"Stiker {name} [{var_label}]"[:254],
                "description": (
                    f"Pack stiker {name}. Format: {fmt_type} / {var_label}. "
                    f"Konten: {contents[:150]}. {world_note}"
                )[:490],
                "category": "Merch Sticker",
                "unit_key": "unit_pcs",
                "tier": tier, "has_expiry": False, "track_batch": False,
                "min_stock": 5, "max_stock": 200,
                "variants": [{"sku": sku, "size_weight": f"{var_label} — {fmt_type}",
                              "price_buy": int(p*0.45), "price_sell": p}],
                "attrs": {
                    "item_type": "Sticker Pack", "design_key": key,
                    "pack_name": name, "format_type": fmt_type,
                    "contents": contents[:250], "world_note": world_note[:250],
                    "tier": TIER_META[tier]["name"], "tier_label": TIER_META[tier]["label"],
                    "variant": var_label, "material": "Waterproof Vinyl + UV Coating",
                },
            })
    return items

def _const_season(key):
    winter_c = {"orion","canis_major","gemini","taurus","auriga","draco","scorpius","cetus"}
    summer_c = {"leo","virgo","cygnus","aquila","lyra","vela","centaurus","crux","indus"}
    spring_c = {"aries","cancer","bootes","corvus","crater","phoenix","apus","musca"}
    if key in winter_c: return "Winter"
    if key in summer_c: return "Summer"
    if key in spring_c: return "Spring"
    return "Autumn"

def _const_outpost(key):
    special = {
        "crux":       "Outpost 35: The Eastern Terminus",
        "ursa_minor": "Outpost 22: The Final Meridian",
        "orion":      "Semua Outpost — panduan pertama ekspeditor baru",
        "canis_major":"Outpost 05: The Glass Meridian (Sirius = bintang paling terang)",
        "sagittarius":"Outpost 22: The Final Meridian (menunjuk pusat galaksi)",
        "apus":       "Outpost 35: The Eastern Terminus (Cendrawasih Papua)",
    }
    return special.get(key, "Semua Outpost The Archipelagic Outposts")

SEASON_UNIVERSE = {
    "Winter": "The Dark Passage", "Summer": "The Open Horizon",
    "Autumn": "The Amber Descent", "Spring": "The First Ascent",
}

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — DATABASE LAYER
# ═══════════════════════════════════════════════════════════════════════════════

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(autocommit=False)
    return conn

def normalize_attr_value(v, max_len=255):
    s = str(v)
    return (s, False) if len(s) <= max_len else (s[:max_len], True)

def fetch_existing_barcodes(conn, barcodes):
    if not barcodes: return {}
    cur = conn.cursor()
    cur.execute("SELECT id, barcode FROM lumra_config_products WHERE barcode = ANY(%s)", (barcodes,))
    result = {b: pid for pid, b in cur.fetchall()}
    cur.close(); return result

def fetch_existing_skus(conn, skus):
    if not skus: return {}
    cur = conn.cursor()
    cur.execute("SELECT id, sku FROM lumra_config_productvariants WHERE sku = ANY(%s)", (skus,))
    result = {sku: vid for vid, sku in cur.fetchall()}
    cur.close(); return result

def fetch_existing_attr_keys(conn, vids):
    if not vids: return set()
    cur = conn.cursor()
    cur.execute("SELECT variant_id, attr_name, attr_value FROM lumra_config_productattribute_items WHERE variant_id = ANY(%s)", (vids,))
    result = set(cur.fetchall()); cur.close(); return result

def fetch_fk_ids(conn):
    cur = conn.cursor()
    ids = {}
    cat_names = ["Merch Mug","Merch Tumbler","Merch T-Shirt","Merch Coin",
                 "Merch Trading Card","Merch Pin","Merch Patch","Merch Sticker","Merchandise"]
    cur.execute("SELECT name, id FROM lumra_config_categories WHERE name = ANY(%s)", (cat_names,))
    for n, i in cur.fetchall():
        ids[f"cat_{n.lower().replace(' ','_')}"] = i

    if not ids:
        cur.execute("SELECT id FROM lumra_config_categories LIMIT 1")
        row = cur.fetchone()
        if row: ids["cat_fallback"] = row[0]

    for unit, key in [("Pcs","unit_pcs"),("Gram","unit_gram")]:
        cur.execute("SELECT id FROM lumra_config_units WHERE name=%s LIMIT 1", (unit,))
        row = cur.fetchone(); ids[key] = row[0] if row else None

    if not ids.get("unit_pcs"):
        cur.execute("SELECT id FROM lumra_config_units LIMIT 1")
        row = cur.fetchone()
        if row: ids["unit_pcs"] = row[0]

    cur.execute("SELECT id FROM lumra_config_taxes WHERE name='PPN 11%' LIMIT 1")
    row = cur.fetchone(); ids["tax_ppn11"] = row[0] if row else None
    cur.close(); return ids

CAT_MAP = {
    "Merch Mug":          "cat_merch_mug",
    "Merch Tumbler":      "cat_merch_tumbler",
    "Merch T-Shirt":      "cat_merch_t-shirt",
    "Merch Coin":         "cat_merch_coin",
    "Merch Trading Card": "cat_merch_trading_card",
    "Merch Pin":          "cat_merch_pin",
    "Merch Patch":        "cat_merch_patch",
    "Merch Sticker":      "cat_merch_sticker",
}

def get_cat(cat_name, fk_ids):
    return fk_ids.get(CAT_MAP.get(cat_name,"")) or fk_ids.get("cat_merchandise") or fk_ids.get("cat_fallback")

def ensure_merch_categories(conn):
    cats = [
        ("Merchandise",        "merchandise",       "MRC","Semua produk merchandise Kafe Nusantara"),
        ("Merch Mug",          "merch-mug",         "MUG","Mug rasi bintang"),
        ("Merch Tumbler",      "merch-tumbler",     "TMB","Tumbler rasi bintang"),
        ("Merch T-Shirt",      "merch-tshirt",      "SHT","Kaos tema kopi"),
        ("Merch Coin",         "merch-coin",        "CON","Merchant coins"),
        ("Merch Trading Card", "merch-trading-card","CRD","Trading cards koleksi"),
        ("Merch Pin",          "merch-pin",         "PIN","Enamel pins"),
        ("Merch Patch",        "merch-patch",       "PCH","Embroidered patches"),
        ("Merch Sticker",      "merch-sticker",     "STK","Sticker packs"),
    ]
    cur = conn.cursor()
    for name, slug, code, desc in cats:
        cur.execute("""
            INSERT INTO lumra_config_categories (name, description, slug, code, is_active, created_at, updated_at)
            VALUES (%s,%s,%s,%s,TRUE,NOW(),NOW()) ON CONFLICT (name) DO NOTHING
        """, (name, desc, slug, code))
    conn.commit(); cur.close()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_pipeline(total_target, batch_size, skip_attrs, dry_run):
    print("═"*65)
    print("  KAFE NUSANTARA — MERCHANDISE GENERATOR v1.0")
    print(f"  Target : {total_target:,} merch items → PostgreSQL")
    print(f"  Sources: 88 rasi bintang + 60 tema kaos + coin + card + pin + patch + sticker")
    print("═"*65)

    print("\n🏗️  Building merchandise universe...")
    all_items = (
        build_mug_items()     +
        build_tumbler_items() +
        build_tshirt_items()  +
        build_coin_items()    +
        build_card_items()    +
        build_pin_items()     +
        build_patch_items()   +
        build_sticker_items()
    )

    # Trim or cycle to hit target
    if len(all_items) > total_target:
        all_items = all_items[:total_target]
    elif len(all_items) < total_target:
        extra = total_target - len(all_items)
        for i in range(extra):
            base = all_items[i % len(all_items)]
            clone = dict(base)
            clone["barcode"] = base["barcode"] + f"-EX{i:04d}"
            clone["name"]    = (base["name"] + f" Mk.{i//len(all_items)+2}")[:254]
            clone["variants"] = [dict(v, sku=v["sku"]+f"-EX{i:04d}") for v in base["variants"]]
            all_items.append(clone)

    # Count by category
    from collections import Counter
    cat_dist = Counter(i["category"] for i in all_items)
    tier_dist= Counter(i["tier"] for i in all_items)

    print(f"   Total generated: {len(all_items):,}")
    for cat, cnt in sorted(cat_dist.items()):
        print(f"   · {cat:<25}: {cnt:>5,}")
    print(f"   Tier T1/T2/T3: {tier_dist.get('T1',0):,}/{tier_dist.get('T2',0):,}/{tier_dist.get('T3',0):,}")

    if dry_run:
        print(f"\n📋 SAMPLE (10 items):")
        for item in all_items[:10]:
            v = item["variants"][0]
            print(f"   [{item['tier']}] {item['name'][:58]}")
            print(f"         SKU: {v['sku']} | Rp {v['price_sell']:,}")
        return

    print(f"\n📡 Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}...")
    try:
        conn = get_connection(); print("  ✅ Connected")
    except Exception as e:
        print(f"  ❌ {e}"); sys.exit(1)

    ensure_merch_categories(conn)
    fk_ids = fetch_fk_ids(conn)

    total_p = total_v = total_a = 0
    start = time.time()
    now   = datetime.now(timezone.utc)
    used_skus = set()

    for bs in range(0, len(all_items), batch_size):
        batch = all_items[bs:bs+batch_size]

        # Products
        barcodes  = [i["barcode"] for i in batch]
        existing_b= fetch_existing_barcodes(conn, barcodes)
        new_items = [i for i in batch if i["barcode"] not in existing_b]
        b2pid     = dict(existing_b)

        if new_items:
            cur = conn.cursor()
            psycopg2.extras.execute_values(
                cur,
                """INSERT INTO lumra_config_products
                   (name,description,is_active,has_expiry,track_batch,
                    min_stock,max_stock,created_at,updated_at,
                    category_id,tax_id,unit_id,vendor_id,barcode)
                   VALUES %s ON CONFLICT (barcode) DO NOTHING RETURNING id,barcode""",
                [(i["name"][:254],i["description"][:490],True,i["has_expiry"],i["track_batch"],
                  i["min_stock"],i["max_stock"],now,now,
                  get_cat(i["category"],fk_ids),fk_ids.get("tax_ppn11"),
                  fk_ids.get("unit_pcs"),None,i["barcode"]) for i in new_items],
                page_size=200)
            rows = cur.fetchall(); conn.commit(); cur.close()
            b2pid.update({b:pid for pid,b in rows})
            total_p += len(rows)

        # Variants
        vrows = []
        for item in batch:
            pid = b2pid.get(item["barcode"])
            if not pid: continue
            for v in item["variants"]:
                if v["sku"] not in used_skus:
                    used_skus.add(v["sku"])
                    vrows.append((v["sku"],pid,v["size_weight"],v["price_buy"],v["price_sell"]))

        sku2vid = {}
        if vrows:
            ex_skus = fetch_existing_skus(conn,[r[0] for r in vrows])
            new_v = [r for r in vrows if r[0] not in ex_skus]
            sku2vid.update(ex_skus)
            if new_v:
                cur = conn.cursor()
                psycopg2.extras.execute_values(
                    cur,
                    """INSERT INTO lumra_config_productvariants
                       (sku,product_id,size_weight,price_buy,price_sell,updated_at)
                       VALUES %s ON CONFLICT (sku) DO NOTHING RETURNING id,sku""",
                    [(sku,pid,sw,pb,ps,now) for sku,pid,sw,pb,ps in new_v],page_size=500)
                rows = cur.fetchall(); conn.commit(); cur.close()
                sku2vid.update({sku:vid for vid,sku in rows})
                total_v += len(rows)

        # Attrs
        if not skip_attrs:
            arows, batch_keys = [], set()
            ex_attrs = fetch_existing_attr_keys(conn,list(sku2vid.values())) if sku2vid else set()
            for item in batch:
                first_sku = item["variants"][0]["sku"] if item["variants"] else None
                vid = sku2vid.get(first_sku) if first_sku else None
                if not vid: continue
                for aname, aval in item["attrs"].items():
                    nv, _ = normalize_attr_value(aval)
                    k = (vid, aname, nv)
                    if k not in ex_attrs and k not in batch_keys:
                        batch_keys.add(k); arows.append((vid,aname,nv,now))
            if arows:
                cur = conn.cursor()
                psycopg2.extras.execute_values(
                    cur,
                    """INSERT INTO lumra_config_productattribute_items
                       (variant_id,attr_name,attr_value,updated_at)
                       VALUES %s ON CONFLICT DO NOTHING""",
                    arows,page_size=1000)
                total_a += len(arows); conn.commit(); cur.close()

        done = bs + len(batch)
        if done % PROGRESS_AT == 0 or done >= len(all_items):
            elapsed = time.time()-start
            print(f"   [{done:>5,}/{len(all_items):,}] "
                  f"Prod:{total_p:,} Var:{total_v:,} Attr:{total_a:,} "
                  f"| {total_p/max(elapsed,0.01):.0f} p/s")

    conn.close()
    elapsed = time.time()-start
    print(); print("═"*65); print("  📊 FINAL")
    for lbl, val in [("Products",total_p),("Variants",total_v),
                     ("Attrs",total_a),("Total rows",total_p+total_v+total_a),
                     ("Time",f"{elapsed:.1f}s")]:
        print(f"  ✦ {lbl:<20} {val!s:>12}")
    print("═"*65)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Kafe Nusantara — Merchandise Generator")
    p.add_argument("--count",       type=int,  default=TARGET)
    p.add_argument("--batch-size",  type=int,  default=BATCH_SIZE)
    p.add_argument("--skip-attrs",  action="store_true")
    p.add_argument("--dry-run",     action="store_true")
    p.add_argument("--db-name",     type=str, default=None)
    p.add_argument("--db-user",     type=str, default=None)
    p.add_argument("--db-password", type=str, default=None)
    p.add_argument("--db-host",     type=str, default=None)
    p.add_argument("--db-port",     type=str, default=None)
    args = p.parse_args()

    for k,v in [("dbname",args.db_name),("user",args.db_user),("password",args.db_password),
                ("host",args.db_host),("port",args.db_port)]:
        if v: DB_CONFIG[k] = v

    run_pipeline(args.count, args.batch_size, args.skip_attrs, args.dry_run)
