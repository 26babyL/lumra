"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          LUMRA ERP — HISTORICAL BULK DATA GENERATOR v4.0                    ║
║                                                                              ║
║  PERUBAHAN v4.0 (dari v3):                                                  ║
║    • Loop per HARI (bukan count flat) — 2019-01-01 s/d hari ini            ║
║    • Growth curve realistis (Samsung/Apple tier) per tahun                  ║
║    • Checkpoint otomatis — bisa resume kalau interrupt                       ║
║    • bulk_create() — jauh lebih cepat dari create() satu-satu              ║
║    • Progress bar + ETA di terminal                                          ║
║    • Dry-run mode — estimasi tanpa nulis ke DB                              ║
║                                                                              ║
║  Cara jalankan:                                                              ║
║    python manage.py run_ops_test                        → dry-run dulu      ║
║    python manage.py run_ops_test --execute              → jalankan sungguhan ║
║    python manage.py run_ops_test --execute --resume     → lanjut dari titik terakhir ║
║    python manage.py run_ops_test --execute --from-date 2019-01-01           ║
║    python manage.py run_ops_test --execute --from-date 2023-01-01 --to-date 2023-12-31 ║
║    python manage.py run_ops_test --execute --workers 4  → parallel insert   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import random
import traceback
import time as time_mod
from decimal import Decimal
from datetime import date, datetime, time, timedelta
from pathlib import Path
from collections import defaultdict

# ─── UTF-8 ──────────────────────────────────────────────────────────────────
for _sn in ("stdout", "stderr"):
    _s = getattr(sys, _sn, None)
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════════════════
# GROWTH CURVE — transaksi per hari per tahun (Samsung/Apple tier)
# Setiap entry = (tx_min, tx_max) per hari di tahun itu
# ══════════════════════════════════════════════════════════════════════════════

DAILY_TX_RANGE = {
    2019: (18,  35),
    2020: (20,  38),   # covid dip Q2-Q3, recover Q4
    2021: (38,  65),   # recovery + ekspansi
    2022: (65,  105),  # skala nasional penuh
    2023: (100, 155),  # ekspansi internasional
    2024: (148, 210),  # AI-driven demand
    2025: (200, 295),  # peak growth
    2026: (270, 340),  # current year
}

# Faktor koreksi per bulan per tahun (covid, dll)
SPECIAL_FACTORS = {
    (2020, 4): 0.45, (2020, 5): 0.40, (2020, 6): 0.50, (2020, 7): 0.58,
    (2021, 1): 0.72, (2021, 2): 0.75,
    (2019, 1): 0.70, (2019, 2): 0.68,  # bisnis baru, masih kecil
}

ANNUAL_INFLATION = {
    2019: Decimal("1.028"), 2020: Decimal("1.016"), 2021: Decimal("1.016"),
    2022: Decimal("1.042"), 2023: Decimal("1.037"), 2024: Decimal("1.025"),
    2025: Decimal("1.024"), 2026: Decimal("1.025"),
}

MONTH_SEASONALITY = {
    1: Decimal("0.88"), 2: Decimal("0.86"), 3: Decimal("0.96"),
    4: Decimal("1.14"), 5: Decimal("1.10"), 6: Decimal("1.08"),
    7: Decimal("1.05"), 8: Decimal("1.00"), 9: Decimal("0.98"),
    10: Decimal("1.03"), 11: Decimal("1.10"), 12: Decimal("1.24"),
}

WEEKDAY_SEASONALITY = {
    0: Decimal("0.92"), 1: Decimal("0.94"), 2: Decimal("0.98"),
    3: Decimal("1.03"), 4: Decimal("1.14"), 5: Decimal("1.28"),
    6: Decimal("1.12"),
}

# ══════════════════════════════════════════════════════════════════════════════
# UNIT PROFILE MAP — unit-aware qty (dari v3)
# ══════════════════════════════════════════════════════════════════════════════

UNIT_PROFILE_MAP = {
    "gram": ("weight_gram", 50,  [250, 500, 1000, 2000, 5000]),
    "gr":   ("weight_gram", 50,  [250, 500, 1000, 2000, 5000]),
    "g":    ("weight_gram", 50,  [250, 500, 1000, 2000, 5000]),
    "kg":   ("weight_kg",   0.5, [5, 10, 15, 20, 25, 50]),
    "kilogram": ("weight_kg", 0.5, [5, 10, 15, 20, 25, 50]),
    "ml":   ("volume_ml",   50,  [250, 500, 1000, 2000, 5000]),
    "milliliter": ("volume_ml", 50, [250, 500, 1000, 2000, 5000]),
    "liter":("volume_l",    0.5, [5, 10, 15, 20, 25, 50]),
    "l":    ("volume_l",    0.5, [5, 10, 15, 20, 25, 50]),
    "lt":   ("volume_l",    0.5, [5, 10, 15, 20, 25, 50]),
    "pcs":  ("count",       12,  [12, 24, 36, 48, 60, 120]),
    "pc":   ("count",       12,  [12, 24, 36, 48, 60, 120]),
    "buah": ("count",       12,  [12, 24, 36, 48, 60, 120]),
    "unit": ("count",       12,  [12, 24, 36, 48, 60, 120]),
    "item": ("count",       12,  [12, 24, 36, 48, 60, 120]),
    "pack": ("pack",        6,   [6, 12, 24, 36, 48, 60]),
    "pck":  ("pack",        6,   [6, 12, 24, 36, 48, 60]),
    "paket":("pack",        6,   [6, 12, 24, 36, 48, 60]),
    "box":  ("box",         6,   [6, 12, 24, 36, 48]),
    "kotak":("box",         6,   [6, 12, 24, 36, 48]),
    "carton":("carton",     4,   [4, 8, 12, 16, 20]),
    "karton":("carton",     4,   [4, 8, 12, 16, 20]),
    "ctn":  ("carton",      4,   [4, 8, 12, 16, 20]),
    "bag":  ("bag",         5,   [5, 10, 15, 20, 25, 50]),
    "sack": ("bag",         5,   [5, 10, 15, 20, 25, 50]),
    "karung":("bag",        5,   [5, 10, 15, 20, 25, 50]),
    "botol":("bottle",      12,  [12, 24, 48, 60, 120]),
    "bottle":("bottle",     12,  [12, 24, 48, 60, 120]),
    "kaleng":("can",        12,  [12, 24, 48, 60]),
    "can":  ("can",         12,  [12, 24, 48, 60]),
    "sachet":("sachet",     10,  [10, 20, 50, 100, 200]),
    "meter":("length_m",    5,   [5, 10, 20, 50, 100]),
    "m":    ("length_m",    5,   [5, 10, 20, 50, 100]),
    "cm":   ("length_cm",   50,  [50, 100, 200, 500]),
    "mm":   ("length_mm",   100, [100, 200, 500, 1000]),
    "yard": ("length_m",    5,   [5, 10, 20, 50]),
    "lembar":("sheet",      10,  [10, 20, 50, 100]),
    "sheet":("sheet",       10,  [10, 20, 50, 100]),
    "roll": ("roll",        6,   [6, 12, 24, 48]),
    "gulung":("roll",       6,   [6, 12, 24, 48]),
    "set":  ("set",         6,   [6, 12, 24, 36]),
    "pasang":("pair",       6,   [6, 12, 24, 36]),
    "pair": ("pair",        6,   [6, 12, 24, 36]),
    "lusin":("dozen",       1,   [1, 2, 3, 5, 10]),
    "dozen":("dozen",       1,   [1, 2, 3, 5, 10]),
    "gross":("gross",       1,   [1, 2, 3, 5]),
    "porsi":("serving",     10,  [10, 20, 30, 50]),
    "serving":("serving",   10,  [10, 20, 30, 50]),
    "cup":  ("serving",     10,  [10, 20, 30, 50]),
    "gelas":("serving",     10,  [10, 20, 30, 50]),
    "biji": ("seed",        10,  [10, 20, 50, 100, 200]),
}

_DEFAULT_UNIT_PROFILE = ("count", 12, [12, 24, 36, 48, 60])

# ══════════════════════════════════════════════════════════════════════════════
# CHECKPOINT — simpan & load progress
# ══════════════════════════════════════════════════════════════════════════════

CHECKPOINT_PATH = Path("lumra_ops_checkpoint.json")

def checkpoint_save(state: dict):
    CHECKPOINT_PATH.write_text(json.dumps(state, default=str), encoding="utf-8")

def checkpoint_load() -> dict:
    if CHECKPOINT_PATH.exists():
        try:
            return json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def checkpoint_clear():
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()

# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS BAR
# ══════════════════════════════════════════════════════════════════════════════

class Progress:
    def __init__(self, total_days: int, start_time: float):
        self.total_days  = total_days
        self.start_time  = start_time
        self.done_days   = 0
        self.done_tx     = 0
        self.done_rows   = 0
        self.errors      = 0
        self._last_print = 0

    def update(self, days=0, tx=0, rows=0, errors=0):
        self.done_days  += days
        self.done_tx    += tx
        self.done_rows  += rows
        self.errors     += errors

    def print(self, current_date: date, force=False):
        now = time_mod.time()
        if not force and (now - self._last_print) < 2.0:
            return
        self._last_print = now

        pct     = self.done_days / max(1, self.total_days) * 100
        elapsed = now - self.start_time
        eta_sec = (elapsed / max(1, self.done_days)) * (self.total_days - self.done_days)
        eta_str = _fmt_duration(eta_sec)
        bar_len = 30
        filled  = int(bar_len * pct / 100)
        bar     = "█" * filled + "░" * (bar_len - filled)

        print(
            f"\r  [{bar}] {pct:5.1f}%  "
            f"{current_date}  "
            f"tx={self.done_tx:,}  rows={self.done_rows:,}  "
            f"err={self.errors}  ETA={eta_str}   ",
            end="", flush=True
        )

    def final(self):
        elapsed = time_mod.time() - self.start_time
        print()
        print(f"\n  Selesai dalam {_fmt_duration(elapsed)}")
        print(f"  Total hari diproses : {self.done_days:,}")
        print(f"  Total transaksi     : {self.done_tx:,}")
        print(f"  Total rows inserted : {self.done_rows:,}")
        print(f"  Errors              : {self.errors}")


def _fmt_duration(sec: float) -> str:
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}j {m}m {s}d"
    if m:
        return f"{m}m {s}d"
    return f"{s}d"

# ══════════════════════════════════════════════════════════════════════════════
# DJANGO SETUP
# ══════════════════════════════════════════════════════════════════════════════

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")

import django
try:
    django.setup()
except RuntimeError as e:
    print(f"[ERROR] Django setup gagal: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()

# ══════════════════════════════════════════════════════════════════════════════
# MODEL LOADER
# ══════════════════════════════════════════════════════════════════════════════

def _get_model(app_label, model_name):
    try:
        from django.apps import apps
        return apps.get_model(app_label, model_name)
    except Exception:
        return None

MODELS = {}
MODELS['Location']       = _get_model('lumra_config', 'Location')
MODELS['ProductVariant'] = _get_model('lumra_config', 'ProductVariant')
MODELS['Product']        = _get_model('lumra_config', 'Product')
MODELS['Stock']          = _get_model('lumra_config', 'Stock')
MODELS['StockMovement']  = _get_model('lumra_config', 'StockMovement')
MODELS['Vendor']         = _get_model('lumra_config', 'Vendor')
MODELS['Unit']           = _get_model('lumra_config', 'Unit')
MODELS['Requisition']    = _get_model('lumra_config', 'Requisition')
MODELS['RequisitionItem']= _get_model('lumra_config', 'RequisitionItem')
MODELS['Transfer']       = _get_model('lumra_config', 'Transfer')
MODELS['TransferItem']   = _get_model('lumra_config', 'TransferItem')
MODELS['Return']         = _get_model('lumra_config', 'Return')
MODELS['ReturnItem']     = _get_model('lumra_config', 'ReturnItem')

for _app in ('production', 'lumra_config'):
    for _name in ('ProductionOrder', 'ProductionMaterialConsumption',
                  'FinishedGoodsReceipt', 'BillOfMaterial', 'BillOfMaterialItem',
                  'Recipe', 'RecipeIngredient', 'RecipeCategory'):
        if MODELS.get(_name) is None:
            MODELS[_name] = _get_model(_app, _name)

# ── Schema inspector ──────────────────────────────────────────────────────────

class SchemaInspector:
    def __init__(self):
        self._cache = {}

    def fields(self, model):
        if model is None:
            return []
        key = f"{model._meta.app_label}.{model._meta.model_name}"
        if key not in self._cache:
            self._cache[key] = {
                f.name: f for f in model._meta.get_fields()
            }
        return self._cache[key]

    def has(self, model, field_name: str) -> bool:
        return field_name in self.fields(model)

    def filter_kwargs(self, model, kwargs: dict) -> dict:
        valid = set(self.fields(model).keys())
        skipped = set(kwargs) - valid
        if skipped:
            pass  # silent in bulk mode
        return {k: v for k, v in kwargs.items() if k in valid}

SI = SchemaInspector()

# ══════════════════════════════════════════════════════════════════════════════
# VARIANT & LOCATION CACHE — load sekali, pakai terus
# ══════════════════════════════════════════════════════════════════════════════

_CACHE = {
    "variants": None,   # list ProductVariant
    "vendors":  None,   # list Vendor
    "units":    None,   # list Unit
    "boms":     None,   # list BillOfMaterial (yang sudah approved)
    "locations": None,
    "warehouse": None,
    "production": None,
    "quarantine": None,
    "stores": None,
    "actor": None,
}

def warm_cache():
    """Load semua data yang dibutuhkan ke memory sekali saja."""
    print("  Warming cache...", end="", flush=True)

    VariantModel = MODELS['ProductVariant']
    ProductModel = MODELS['Product']
    VendorModel  = MODELS['Vendor']
    UnitModel    = MODELS['Unit']
    BOMModel     = MODELS['BillOfMaterial']
    LocationModel= MODELS['Location']

    # Variants — ambil sample representatif dari 4M+
    base = VariantModel.objects.select_related("product", "product__unit")
    if ProductModel and SI.has(ProductModel, 'is_active'):
        base = base.filter(product__is_active=True)

    # Ambil dari berbagai rentang ID agar variatif
    total_variants = base.count()
    step_size      = max(1, total_variants // 5000)
    sampled_ids    = list(
        base.values_list('id', flat=True).order_by('id')[::step_size][:5000]
    )
    _CACHE["variants"] = list(
        base.filter(id__in=sampled_ids).select_related("product", "product__unit")
    )

    _CACHE["vendors"]  = list(VendorModel.objects.all().order_by("id")[:200])
    _CACHE["units"]    = list(UnitModel.objects.all().order_by("id"))

    if BOMModel:
        _CACHE["boms"] = list(BOMModel.objects.select_related(
            "finished_variant", "finished_variant__product"
        ).order_by("id")[:500])

    # Locations
    locs = list(LocationModel.objects.all().order_by("name"))

    def _find(keywords, exclude_ids):
        for loc in locs:
            if loc.id in exclude_ids:
                continue
            hay = f"{getattr(loc, 'location_type', '')} {getattr(loc, 'name', '')}".lower()
            if any(k in hay for k in keywords):
                return loc
        return None

    used = set()
    wh = _find(["warehouse", "gudang", "wh"], used) or locs[0]
    used.add(wh.id)
    pr = _find(["production", "produksi", "dapur", "kitchen"], used) \
         or next((l for l in locs if l.id not in used), wh)
    used.add(pr.id)
    qr = _find(["quarantine", "karantina", "qc", "hold"], used) \
         or next((l for l in locs if l.id not in used), pr)
    used.add(qr.id)
    stores = [l for l in locs if l.id not in used]
    if not stores:
        stores = [locs[-1]]

    _CACHE["warehouse"]  = wh
    _CACHE["production"] = pr
    _CACHE["quarantine"] = qr
    _CACHE["stores"]     = stores
    _CACHE["locations"]  = locs

    actor = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    if not actor:
        actor = User.objects.create_user(
            username="ops.seed", email="ops.seed@lumra.local",
            password="lumra123", is_staff=True,
        )
    _CACHE["actor"] = actor

    print(f" OK  ({len(_CACHE['variants'])} variants, "
          f"{len(_CACHE['vendors'])} vendors, "
          f"{len(stores)} stores)")

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _make_aware(day: date, hour: int, minute: int = 0):
    naive = datetime.combine(day, time(hour=hour, minute=minute))
    return timezone.make_aware(naive, timezone.get_current_timezone())


def _inflation(day: date) -> Decimal:
    factor = Decimal("1.00")
    for yr in range(2019, day.year + 1):
        factor *= ANNUAL_INFLATION.get(yr, Decimal("1.025"))
    return factor.quantize(Decimal("0.0001"))


def _get_unit_profile(unit_obj):
    if unit_obj is None:
        return _DEFAULT_UNIT_PROFILE
    for attr in ("abbreviation", "symbol", "code", "name"):
        val = getattr(unit_obj, attr, None)
        if val:
            key = str(val).strip().lower()
            if key in UNIT_PROFILE_MAP:
                return UNIT_PROFILE_MAP[key]
            for k, p in UNIT_PROFILE_MAP.items():
                if k in key or key in k:
                    return p
    return _DEFAULT_UNIT_PROFILE


def _round_to_step(value, step):
    if step <= 0:
        return Decimal(str(value))
    d_val  = Decimal(str(value))
    d_step = Decimal(str(step))
    rem    = d_val % d_step
    return d_val if rem == 0 else d_val + (d_step - rem)


def _pick_prod_qty(unit_obj, rng, demand: Decimal) -> Decimal:
    _, step, candidates = _get_unit_profile(unit_obj)
    base   = Decimal(str(rng.choice(candidates)))
    scaled = base * demand
    nice   = _round_to_step(scaled, step)
    return max(Decimal(str(step)), nice)


def _variant_unit(variant):
    try:
        return variant.product.unit
    except Exception:
        return None


_CODE_SEQ = 0
def _ts_code(prefix: str, day: date) -> str:
    global _CODE_SEQ
    _CODE_SEQ += 1
    ts = timezone.now().strftime("%H%M%S%f")[-6:]
    return f"{prefix}-{day.strftime('%Y%m%d')}-{_CODE_SEQ:07d}-{ts}"


def _tx_per_day(day: date, rng) -> int:
    lo, hi = DAILY_TX_RANGE.get(day.year, (100, 200))
    factor = SPECIAL_FACTORS.get((day.year, day.month), 1.0)
    seasonal = float(MONTH_SEASONALITY.get(day.month, Decimal("1.00")))
    weekday  = float(WEEKDAY_SEASONALITY.get(day.weekday(), Decimal("1.00")))
    raw = rng.uniform(lo, hi) * factor * seasonal * weekday
    return max(1, int(raw))


def _demand_factor(day: date, rng) -> Decimal:
    years_since = Decimal(str(max(0, day.year - 2019)))
    growth   = Decimal("1.00") + years_since * Decimal("0.075")
    seasonal = MONTH_SEASONALITY.get(day.month, Decimal("1.00"))
    weekday  = WEEKDAY_SEASONALITY.get(day.weekday(), Decimal("1.00"))
    shock    = Decimal(str(round(rng.uniform(0.88, 1.18), 3)))
    factor   = SPECIAL_FACTORS.get((day.year, day.month), 1.0)
    raw = growth * seasonal * weekday * shock * Decimal(str(factor))
    return max(Decimal("0.45"), raw).quantize(Decimal("0.0001"))

# ══════════════════════════════════════════════════════════════════════════════
# BULK BUFFER — kumpulkan objek, insert sekaligus
# ══════════════════════════════════════════════════════════════════════════════

class BulkBuffer:
    """
    Kumpulkan unsaved model instances, flush dengan bulk_create()
    setiap FLUSH_EVERY item atau saat flush() dipanggil manual.
    """
    FLUSH_EVERY = 500  # per model

    def __init__(self, dry_run=False):
        self.dry_run  = dry_run
        self._buf     = defaultdict(list)
        self.inserted = 0
        self.skipped  = 0

    def add(self, instance):
        key = type(instance)
        self._buf[key].append(instance)
        if len(self._buf[key]) >= self.FLUSH_EVERY:
            self._flush_model(key)

    def add_many(self, instances):
        for inst in instances:
            self.add(inst)

    def flush(self):
        for key in list(self._buf.keys()):
            self._flush_model(key)

    def _flush_model(self, model_cls):
        items = self._buf.pop(model_cls, [])
        if not items:
            return
        if self.dry_run:
            self.skipped += len(items)
            return
        try:
            with transaction.atomic():
                created = model_cls.objects.bulk_create(
                    items,
                    ignore_conflicts=True,
                    batch_size=200,
                )
            self.inserted += len(created)
        except Exception as e:
            # Fallback: coba satu per satu
            for obj in items:
                try:
                    obj.save()
                    self.inserted += 1
                except Exception:
                    self.skipped += 1

    @property
    def total_rows(self):
        return self.inserted + self.skipped

# ══════════════════════════════════════════════════════════════════════════════
# SINGLE-TRANSACTION BUILDER
# Setiap skenario membangun objek in-memory, tambah ke BulkBuffer
# ══════════════════════════════════════════════════════════════════════════════

def _build_scenario(rng, day: date, demand: Decimal, infl: Decimal,
                    used_variant_ids: set, buf: BulkBuffer, scenario_idx: int):
    """
    Bangun 1 skenario lengkap (5 fase) secara in-memory.
    Semua objek ditambahkan ke buf, TIDAK langsung di-save.
    Return (row_count, error_msg_or_None)
    """
    StockModel       = MODELS['Stock']
    MovModel         = MODELS['StockMovement']
    ReqModel         = MODELS['Requisition']
    ReqItemModel     = MODELS['RequisitionItem']
    TrfModel         = MODELS['Transfer']
    TrfItemModel     = MODELS['TransferItem']
    ProdOrdModel     = MODELS['ProductionOrder']
    MatConsModel     = MODELS['ProductionMaterialConsumption']
    FGRModel         = MODELS['FinishedGoodsReceipt']
    BOMModel         = MODELS['BillOfMaterial']
    BOMItemModel     = MODELS['BillOfMaterialItem']
    RecipeModel      = MODELS['Recipe']
    RecipeIngModel   = MODELS['RecipeIngredient']
    ReturnModel      = MODELS['Return']
    RetItemModel     = MODELS['ReturnItem']

    actor     = _CACHE["actor"]
    warehouse = _CACHE["warehouse"]
    production= _CACHE["production"]
    quarantine= _CACHE["quarantine"]
    stores    = _CACHE["stores"]
    variants  = _CACHE["variants"]
    vendors   = _CACHE["vendors"]

    if not variants or not vendors:
        return 0, "Cache kosong"

    # ── Pick data ─────────────────────────────────────────────────────────
    pool = [v for v in variants if v.id not in used_variant_ids]
    if len(pool) < 4:
        pool = variants  # reset jika habis

    try:
        fg = rng.choice(pool)
        comp_pool = [v for v in pool if v.id != fg.id]
        n_comp = min(3, len(comp_pool))
        if n_comp < 1:
            return 0, "Tidak cukup variant"
        components = rng.sample(comp_pool, n_comp)
    except Exception as e:
        return 0, f"pick variant: {e}"

    vendor = rng.choice(vendors)
    store  = rng.choice(stores)
    fg_unit= _variant_unit(fg)

    # Tandai sebagai used
    used_variant_ids.add(fg.id)
    for c in components:
        used_variant_ids.add(c.id)

    # ── Waktu operasional ─────────────────────────────────────────────────
    hour_wt = [6, 10, 12, 12, 10, 8, 5, 3]
    hour = rng.choices([7, 8, 9, 10, 13, 15, 17, 19], weights=hour_wt)[0]
    minute = rng.choice([0, 5, 10, 15, 20, 30, 40, 45, 50])

    def t(offset_hours=0):
        base = _make_aware(day, hour, minute)
        return base + timedelta(hours=offset_hours)

    row_count = 0

    # ══════════════════════════════════════════════════════════════════════
    # FASE 1 — INBOUND
    # ══════════════════════════════════════════════════════════════════════
    inbound_qty = {}
    for comp in components:
        u  = _variant_unit(comp)
        qty = int(_round_to_step(
            Decimal(str(rng.randint(20, 60))) * demand, _get_unit_profile(u)[1]
        ))
        qty = max(int(_get_unit_profile(u)[1]), qty)

        if StockModel:
            s_kw = SI.filter_kwargs(StockModel, {
                'variant': comp, 'location': warehouse,
                'quantity': qty, 'notes': f"PO dari {vendor.name}",
                'transaction_type': 'in',
                'created_at': t(0),
            })
            buf.add(StockModel(**s_kw))
            row_count += 1

        if MovModel:
            m_kw = SI.filter_kwargs(MovModel, {
                'product': comp, 'location': warehouse,
                'quantity': Decimal(str(qty)),
                'movement_type': 'purchase_in',
                'reference_type': 'purchase_order',
                'reference_id': scenario_idx,
                'reference_number': _ts_code("PO", day),
                'created_by': actor,
                'notes': f"Inbound dari {vendor.name}",
                'created_at': t(0),
            })
            buf.add(MovModel(**m_kw))
            row_count += 1

        inbound_qty[comp.id] = qty

    # ══════════════════════════════════════════════════════════════════════
    # FASE 2 — RnD → BOM
    # ══════════════════════════════════════════════════════════════════════
    yield_qty    = _pick_prod_qty(fg_unit, rng, demand)
    comp_qty_rcp = {}

    # Recipe
    recipe = None
    if RecipeModel:
        r_kw = SI.filter_kwargs(RecipeModel, {
            'name': f"[TRIAL] {fg.product.name[:40]} {_ts_code('RCP', day)}",
            'description': f"Recipe percobaan untuk {fg.product.name[:60]}",
            'instructions': "1. Siapkan bahan\n2. Mixing\n3. QC\n4. Evaluasi",
            'yield_quantity': yield_qty,
            'yield_unit': fg_unit,
            'preparation_time': rng.choice([30, 45, 60, 90]),
            'total_cost': Decimal("0"),
            'cost_per_unit': Decimal("0"),
            'is_archived': False,
            'created_by': actor,
            'created_at': t(1),
        })
        recipe = RecipeModel(**r_kw)
        # NOTE: recipe harus di-save dulu karena RecipeIngredient butuh FK
        # Ini satu-satunya model yang tidak di-bulk karena perlu PK-nya
        if not buf.dry_run:
            try:
                recipe.save()
                row_count += 1
            except Exception:
                recipe = None

    # Recipe ingredients
    if recipe and RecipeIngModel:
        total_cost = Decimal("0")
        for comp in components:
            u   = _variant_unit(comp)
            qty = _pick_prod_qty(u, rng, demand * Decimal("0.3"))
            uc  = (Decimal(str(getattr(comp, 'price_buy', None) or 1000)) * infl).quantize(Decimal("0.01"))
            sub = qty * uc
            total_cost += sub
            ri_kw = SI.filter_kwargs(RecipeIngModel, {
                'recipe': recipe, 'variant': comp,
                'quantity': qty, 'unit': u,
                'unit_cost': uc, 'subtotal_cost': sub,
                'notes': getattr(comp, 'sku', str(comp.id)),
            })
            buf.add(RecipeIngModel(**ri_kw))
            row_count += 1
            comp_qty_rcp[comp.id] = qty

        # Update recipe cost
        if not buf.dry_run and recipe.pk:
            try:
                recipe.total_cost    = total_cost
                recipe.cost_per_unit = total_cost / yield_qty if yield_qty else Decimal("0")
                recipe.save(update_fields=['total_cost', 'cost_per_unit'])
            except Exception:
                pass

    # Konsumsi uji coba
    for comp in components:
        trial_qty = int(comp_qty_rcp.get(comp.id, Decimal("5")))
        if StockModel:
            buf.add(StockModel(**SI.filter_kwargs(StockModel, {
                'variant': comp, 'location': warehouse,
                'quantity': trial_qty, 'transaction_type': 'out',
                'notes': "Konsumsi uji coba RnD", 'created_at': t(2),
            })))
            row_count += 1

    # BOM
    bom = None
    if BOMModel:
        bom_kw = SI.filter_kwargs(BOMModel, {
            'code': _ts_code("BOM", day),
            'version': 1,
            'name': f"BOM — {fg.product.name[:50]}",
            'notes': "Auto-generated dari recipe percobaan",
            'created_by': actor,
            'created_at': t(2),
        })
        if SI.has(BOMModel, 'finished_variant'):
            bom_kw['finished_variant'] = fg
        elif SI.has(BOMModel, 'product'):
            bom_kw['product'] = getattr(fg, 'product', fg)
        bom = BOMModel(**bom_kw)
        if not buf.dry_run:
            try:
                bom.save()
                row_count += 1
            except Exception:
                bom = None

    if bom and BOMItemModel:
        for comp in components:
            if comp.id in comp_qty_rcp:
                bi_kw = SI.filter_kwargs(BOMItemModel, {
                    'bom': bom, 'component': comp,
                    'quantity': comp_qty_rcp[comp.id],
                    'unit': _variant_unit(comp),
                    'notes': "Dari recipe approved",
                })
                buf.add(BOMItemModel(**bi_kw))
                row_count += 1

    # ══════════════════════════════════════════════════════════════════════
    # FASE 3 — PRODUKSI
    # ══════════════════════════════════════════════════════════════════════
    target_qty = _pick_prod_qty(fg_unit, rng, demand)
    if yield_qty and target_qty < yield_qty:
        target_qty = yield_qty

    # Kebutuhan bahan proporsional
    needed = {}
    for comp in components:
        base  = comp_qty_rcp.get(comp.id, Decimal("5"))
        ratio = target_qty / yield_qty if yield_qty else Decimal("1")
        u     = _variant_unit(comp)
        _, step_c, _ = _get_unit_profile(u)
        raw   = base * ratio
        nice  = _round_to_step(raw, step_c)
        needed[comp.id] = max(int(step_c), int(nice))

    # Requisition
    req = None
    if ReqModel:
        rq_kw = SI.filter_kwargs(ReqModel, {
            'status': 'completed',
            'from_location': warehouse,
            'to_location': production,
            'requested_by': actor,
            'approved_by': actor,
            'approved_at': t(3),
            'notes': "Requisisi produksi",
            'created_at': t(2),
        })
        req = ReqModel(**rq_kw)
        if not buf.dry_run:
            try:
                req.save()
                row_count += 1
            except Exception:
                req = None

    if req and ReqItemModel:
        for comp in components:
            ri_kw = SI.filter_kwargs(ReqItemModel, {
                'requisition': req, 'variant': comp,
                'quantity': needed.get(comp.id, 5),
            })
            buf.add(ReqItemModel(**ri_kw))
            row_count += 1

    # Transfer gudang → produksi
    trf_prod = None
    if TrfModel:
        tf_kw = SI.filter_kwargs(TrfModel, {
            'status': 'received',
            'source_location': warehouse,
            'destination_location': production,
            'created_by': actor,
            'sent_at': t(3), 'received_at': t(4),
            'notes': "Transfer bahan ke produksi",
            'created_at': t(3),
        })
        if req and SI.has(TrfModel, 'requisition'):
            tf_kw['requisition'] = req
        trf_prod = TrfModel(**tf_kw)
        if not buf.dry_run:
            try:
                trf_prod.save()
                row_count += 1
            except Exception:
                trf_prod = None

    if trf_prod and TrfItemModel:
        for comp in components:
            q = needed.get(comp.id, 5)
            ti_kw = SI.filter_kwargs(TrfItemModel, {
                'transfer': trf_prod, 'variant': comp,
                'quantity_sent': q, 'quantity_received': q,
            })
            buf.add(TrfItemModel(**ti_kw))
            row_count += 1

            # Stock movements: gudang → produksi
            for loc, qty_v, tx, mv in [
                (warehouse,  q, "transfer_sent",     "transfer_out"),
                (production, q, "transfer_received", "transfer_in"),
            ]:
                if StockModel:
                    buf.add(StockModel(**SI.filter_kwargs(StockModel, {
                        'variant': comp, 'location': loc, 'quantity': qty_v,
                        'transaction_type': tx, 'created_at': t(4),
                        'notes': f"Transfer bahan ke produksi",
                    })))
                    row_count += 1
                if MovModel:
                    buf.add(MovModel(**SI.filter_kwargs(MovModel, {
                        'product': comp, 'location': loc,
                        'quantity': Decimal(str(qty_v)),
                        'movement_type': mv, 'reference_type': 'transfer',
                        'reference_id': trf_prod.pk or 0,
                        'created_by': actor, 'created_at': t(4),
                        'notes': "Bahan ke produksi",
                    })))
                    row_count += 1

    # Production Order
    prod_order = None
    if ProdOrdModel:
        po_kw = SI.filter_kwargs(ProdOrdModel, {
            'code': _ts_code("PROD", day),
            'status': 'completed',
            'target_quantity': target_qty,
            'produced_quantity': target_qty,
            'scheduled_date': day,
            'priority': rng.choice(['Normal', 'High', 'Urgent']),
            'started_at': t(5), 'completed_at': t(9),
            'created_by': actor,
            'notes': "Production order",
            'created_at': t(4),
        })
        if bom and SI.has(ProdOrdModel, 'bom'):
            po_kw['bom'] = bom
        if fg_unit and SI.has(ProdOrdModel, 'unit'):
            po_kw['unit'] = fg_unit
        prod_order = ProdOrdModel(**po_kw)
        if not buf.dry_run:
            try:
                prod_order.save()
                row_count += 1
            except Exception:
                prod_order = None

    # Material consumption
    if prod_order and MatConsModel:
        for comp in components:
            q = needed.get(comp.id, 5)
            mc_kw = SI.filter_kwargs(MatConsModel, {
                'production_order': prod_order,
                'component': comp,
                'quantity': Decimal(str(q)),
                'unit': _variant_unit(comp),
                'consumed_at': t(7),
                'notes': "Konsumsi produksi",
            })
            buf.add(MatConsModel(**mc_kw))
            row_count += 1

            # Stock keluar dari produksi
            if StockModel:
                buf.add(StockModel(**SI.filter_kwargs(StockModel, {
                    'variant': comp, 'location': production,
                    'quantity': q, 'transaction_type': 'out',
                    'created_at': t(7), 'notes': "Konsumsi produksi",
                })))
                row_count += 1

    # Finished goods masuk gudang
    if prod_order and FGRModel:
        fg_kw = SI.filter_kwargs(FGRModel, {
            'production_order': prod_order,
            'finished_variant': fg,
            'location': warehouse,
            'quantity_received': target_qty,
            'received_at': t(10),
            'notes': "FG dari produksi",
        })
        buf.add(FGRModel(**fg_kw))
        row_count += 1

    if StockModel:
        buf.add(StockModel(**SI.filter_kwargs(StockModel, {
            'variant': fg, 'location': warehouse,
            'quantity': int(target_qty),
            'transaction_type': 'in',
            'created_at': t(10),
            'notes': "FG masuk gudang",
        })))
        row_count += 1

    # ══════════════════════════════════════════════════════════════════════
    # FASE 4 — TRANSFER → TOKO
    # ══════════════════════════════════════════════════════════════════════
    _, step_fg, _ = _get_unit_profile(fg_unit)
    raw_send = int(target_qty) * rng.uniform(0.5, 0.85)
    send_qty = max(int(step_fg), int(_round_to_step(raw_send, step_fg)))

    req_store = None
    if ReqModel:
        rs_kw = SI.filter_kwargs(ReqModel, {
            'status': 'completed',
            'from_location': warehouse,
            'to_location': store,
            'requested_by': actor,
            'approved_by': actor,
            'approved_at': t(12),
            'notes': f"Requisisi ke {store.name}",
            'created_at': t(11),
        })
        req_store = ReqModel(**rs_kw)
        if not buf.dry_run:
            try:
                req_store.save()
                row_count += 1
            except Exception:
                req_store = None

    if req_store and ReqItemModel:
        ri2_kw = SI.filter_kwargs(ReqItemModel, {
            'requisition': req_store, 'variant': fg,
            'quantity': send_qty,
        })
        buf.add(ReqItemModel(**ri2_kw))
        row_count += 1

    trf_store = None
    if TrfModel:
        ts_kw = SI.filter_kwargs(TrfModel, {
            'status': 'received',
            'source_location': warehouse,
            'destination_location': store,
            'created_by': actor,
            'sent_at': t(13), 'received_at': t(15),
            'notes': f"FG ke {store.name}",
            'created_at': t(13),
        })
        if req_store and SI.has(TrfModel, 'requisition'):
            ts_kw['requisition'] = req_store
        trf_store = TrfModel(**ts_kw)
        if not buf.dry_run:
            try:
                trf_store.save()
                row_count += 1
            except Exception:
                trf_store = None

    if trf_store and TrfItemModel:
        ti2_kw = SI.filter_kwargs(TrfItemModel, {
            'transfer': trf_store, 'variant': fg,
            'quantity_sent': send_qty, 'quantity_received': send_qty,
        })
        buf.add(TrfItemModel(**ti2_kw))
        row_count += 1

    for loc, qty_v, tx, mv in [
        (warehouse, send_qty, "transfer_sent",     "transfer_out"),
        (store,     send_qty, "transfer_received", "transfer_in"),
    ]:
        if StockModel:
            buf.add(StockModel(**SI.filter_kwargs(StockModel, {
                'variant': fg, 'location': loc, 'quantity': qty_v,
                'transaction_type': tx, 'created_at': t(14),
                'notes': f"FG ke {store.name}",
            })))
            row_count += 1
        if MovModel:
            buf.add(MovModel(**SI.filter_kwargs(MovModel, {
                'product': fg, 'location': loc,
                'quantity': Decimal(str(qty_v)),
                'movement_type': mv, 'reference_type': 'transfer',
                'reference_id': trf_store.pk or 0,
                'created_by': actor, 'created_at': t(14),
                'notes': f"FG ke {store.name}",
            })))
            row_count += 1

    # ══════════════════════════════════════════════════════════════════════
    # FASE 5 — RETURN + QC
    # ══════════════════════════════════════════════════════════════════════
    raw_ret   = int(send_qty * rng.uniform(0.10, 0.30))
    ret_qty   = max(int(step_fg), int(_round_to_step(raw_ret, step_fg)))

    ret_obj = None
    if ReturnModel:
        ret_kw = SI.filter_kwargs(ReturnModel, {
            'status': 'in_quarantine',
            'origin_location': store,
            'destination_location': quarantine,
            'created_by': actor,
            'notes': f"Return dari {store.name}",
            'created_at': t(20),
        })
        ret_obj = ReturnModel(**ret_kw)
        if not buf.dry_run:
            try:
                ret_obj.save()
                row_count += 1
            except Exception:
                ret_obj = None

    if ret_obj and MODELS['ReturnItem']:
        ri_kw = SI.filter_kwargs(MODELS['ReturnItem'], {
            'return_record': ret_obj, 'variant': fg,
            'quantity': ret_qty, 'reason': "Quality issue",
        })
        buf.add(MODELS['ReturnItem'](**ri_kw))
        row_count += 1

    # Stock: toko → karantina
    for loc, qty_v, tx in [
        (store,      ret_qty, "out"),
        (quarantine, ret_qty, "in"),
    ]:
        if StockModel:
            buf.add(StockModel(**SI.filter_kwargs(StockModel, {
                'variant': fg, 'location': loc, 'quantity': qty_v,
                'transaction_type': tx, 'created_at': t(21),
                'notes': "Return masuk karantina",
            })))
            row_count += 1

    # QC decision
    qc = rng.choices(["LULUS", "DISPOSAL"], weights=[70, 30])[0]

    if qc == "LULUS":
        for loc, qty_v, tx in [
            (quarantine, ret_qty, "out"),
            (warehouse,  ret_qty, "in"),
        ]:
            if StockModel:
                buf.add(StockModel(**SI.filter_kwargs(StockModel, {
                    'variant': fg, 'location': loc, 'quantity': qty_v,
                    'transaction_type': tx, 'created_at': t(22),
                    'notes': "QC lulus — restock",
                })))
                row_count += 1
        if ret_obj and not buf.dry_run:
            try:
                ret_obj.status = 'cleared'
                ret_obj.save(update_fields=['status'])
            except Exception:
                pass
    else:
        if StockModel:
            buf.add(StockModel(**SI.filter_kwargs(StockModel, {
                'variant': fg, 'location': quarantine, 'quantity': ret_qty,
                'transaction_type': 'out', 'created_at': t(22),
                'notes': "QC gagal — disposal",
            })))
            row_count += 1
        if ret_obj and not buf.dry_run:
            try:
                ret_obj.status = 'disposed'
                ret_obj.save(update_fields=['status'])
            except Exception:
                pass

    return row_count, None


# ══════════════════════════════════════════════════════════════════════════════
# DAILY RUNNER — proses satu hari
# ══════════════════════════════════════════════════════════════════════════════

def _process_day(day: date, rng, used_variant_ids: set,
                 buf: BulkBuffer, prog: Progress, scenario_counter: list):
    n_tx   = _tx_per_day(day, rng)
    demand = _demand_factor(day, rng)
    infl   = _inflation(day)

    day_rows   = 0
    day_errors = 0

    for i in range(n_tx):
        scenario_counter[0] += 1
        try:
            rows, err = _build_scenario(
                rng, day, demand, infl,
                used_variant_ids, buf, scenario_counter[0]
            )
            day_rows += rows
            if err:
                day_errors += 1
        except Exception:
            day_errors += 1

    # Flush buffer setelah tiap hari
    buf.flush()

    prog.update(days=1, tx=n_tx, rows=day_rows, errors=day_errors)
    return n_tx, day_rows


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_historical(
    from_date: str = "2019-01-01",
    to_date:   str = None,
    execute:   bool = False,
    resume:    bool = False,
    seed:      int  = 42,
    verbose:   bool = True,
):
    """
    Main entry point.

    Args:
        from_date : tanggal mulai (YYYY-MM-DD), default 2019-01-01
        to_date   : tanggal akhir (YYYY-MM-DD), default hari ini
        execute   : False = dry-run, True = sungguhan tulis ke DB
        resume    : lanjut dari checkpoint terakhir
        seed      : random seed
        verbose   : print detail
    """
    dry_run = not execute

    # ── Parse tanggal ─────────────────────────────────────────────────────
    start = datetime.strptime(from_date, "%Y-%m-%d").date()
    end   = (datetime.strptime(to_date, "%Y-%m-%d").date()
             if to_date else timezone.localdate())
    if start > end:
        start, end = end, start

    total_days = (end - start).days + 1

    # ── Banner ────────────────────────────────────────────────────────────
    print("\n" + "═"*70)
    print(f"  LUMRA ERP — HISTORICAL BULK GENERATOR v4.0")
    print("═"*70)
    print(f"  Mode      : {'DRY-RUN (tidak ada yang disimpan)' if dry_run else 'EXECUTE — menulis ke database'}")
    print(f"  Periode   : {start} s/d {end} ({total_days:,} hari)")
    print(f"  Seed      : {seed}")
    print(f"  Resume    : {resume}")
    print()

    # ── Dry-run estimate ──────────────────────────────────────────────────
    if dry_run:
        rng_est = random.Random(seed)
        total_est_tx   = 0
        total_est_rows = 0
        cur = start
        while cur <= end:
            n = _tx_per_day(cur, rng_est)
            total_est_tx   += n
            total_est_rows += n * 28  # ~28 rows per skenario
            cur += timedelta(days=1)

        print(f"  Estimasi total transaksi  : {total_est_tx:,}")
        print(f"  Estimasi total rows       : {total_est_rows:,}")
        print(f"  Estimasi durasi (bulk)    : {_fmt_duration(total_est_rows / 3000)}")
        print()
        print("  Jalankan dengan --execute untuk mulai menulis ke database.")
        print("═"*70 + "\n")
        return

    # ── Resume dari checkpoint ────────────────────────────────────────────
    ckpt     = {}
    resume_from = start
    if resume:
        ckpt = checkpoint_load()
        if ckpt.get("last_date"):
            resume_from = datetime.strptime(ckpt["last_date"], "%Y-%m-%d").date() + timedelta(days=1)
            print(f"  Melanjutkan dari: {resume_from}")
        else:
            print("  Tidak ada checkpoint ditemukan, mulai dari awal.")

    # ── Warm cache ────────────────────────────────────────────────────────
    warm_cache()

    if not _CACHE["variants"] or not _CACHE["vendors"]:
        print("  [ERROR] Cache kosong — pastikan ProductVariant & Vendor sudah ada.")
        return

    # ── Setup ─────────────────────────────────────────────────────────────
    rng             = random.Random(seed)
    buf             = BulkBuffer(dry_run=dry_run)
    start_time      = time_mod.time()
    prog            = Progress(total_days, start_time)
    used_ids        = set()
    scenario_counter= [ckpt.get("total_tx", 0)]

    # Advance rng ke posisi resume (approximate)
    if resume_from > start:
        skip_days = (resume_from - start).days
        for _ in range(skip_days * 50):  # ~50 rng calls per hari
            rng.random()

    # ── Loop per hari ─────────────────────────────────────────────────────
    cur = resume_from
    try:
        while cur <= end:
            # Reset used_ids tiap hari agar tidak habis
            if len(used_ids) > len(_CACHE["variants"]) * 0.8:
                used_ids.clear()

            n_tx, n_rows = _process_day(cur, rng, used_ids, buf, prog, scenario_counter)

            prog.print(cur)

            # Checkpoint setiap 7 hari
            if cur.day % 7 == 0 or cur == end:
                checkpoint_save({
                    "last_date":  cur.isoformat(),
                    "total_tx":   scenario_counter[0],
                    "total_rows": buf.inserted,
                    "saved_at":   timezone.now().isoformat(),
                })

            cur += timedelta(days=1)

    except KeyboardInterrupt:
        print("\n\n  [INTERRUPT] Dihentikan oleh user.")
        buf.flush()
        checkpoint_save({
            "last_date":  cur.isoformat(),
            "total_tx":   scenario_counter[0],
            "total_rows": buf.inserted,
            "saved_at":   timezone.now().isoformat(),
        })
        print(f"  Checkpoint disimpan di: {CHECKPOINT_PATH}")
        print(f"  Jalankan dengan --execute --resume untuk melanjutkan.\n")
        prog.final()
        return

    # ── Flush sisa buffer ─────────────────────────────────────────────────
    buf.flush()
    prog.print(end, force=True)
    prog.final()

    # ── Hapus checkpoint jika selesai penuh ───────────────────────────────
    if cur > end:
        checkpoint_clear()
        print("  Checkpoint dihapus (proses selesai).\n")

    print("═"*70)
    print(f"  ✓ SELESAI — {buf.inserted:,} rows dimasukkan ke database")
    print("═"*70 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# DJANGO MANAGEMENT COMMAND
# ══════════════════════════════════════════════════════════════════════════════

from django.core.management.base import BaseCommand  # noqa

class Command(BaseCommand):
    help = "Lumra ERP — Historical bulk data generator (2019 → hari ini)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute", action="store_true", default=False,
            help="Sungguhan tulis ke DB (default: dry-run saja)"
        )
        parser.add_argument(
            "--resume", action="store_true", default=False,
            help="Lanjut dari checkpoint terakhir"
        )
        parser.add_argument(
            "--from-date", default="2019-01-01",
            help="Tanggal mulai YYYY-MM-DD (default: 2019-01-01)"
        )
        parser.add_argument(
            "--to-date", default=None,
            help="Tanggal akhir YYYY-MM-DD (default: hari ini)"
        )
        parser.add_argument(
            "--seed", type=int, default=42,
            help="Random seed (default: 42)"
        )
        parser.add_argument(
            "--quiet", action="store_true",
            help="Kurangi output"
        )

    def handle(self, *args, **options):
        run_historical(
            from_date = options["from_date"],
            to_date   = options["to_date"],
            execute   = options["execute"],
            resume    = options["resume"],
            seed      = options["seed"],
            verbose   = not options["quiet"],
        )


# ══════════════════════════════════════════════════════════════════════════════
# JALANKAN LANGSUNG
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_historical(execute=False)