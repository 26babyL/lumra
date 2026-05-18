"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          LUMRA ERP — FULL OPERATIONAL DATA GENERATOR v2.0                   ║
║                                                                              ║
║  Script ini akan MENGISI DATA OPERASIONAL ke database LUMRA ERP:            ║
║    FASE 1 · INBOUND    — PO dari Vendor → Barang masuk Gudang               ║
║    FASE 2 · RnD        — Recipe percobaan → Uji coba → Approve → BOM        ║
║    FASE 3 · PRODUKSI   — Production Order → Requisition → Proses → FG       ║
║    FASE 4 · TRANSFER   — Gudang → Toko/Cabang                               ║
║    FASE 5 · RETURN     — Toko → Gudang Karantina → QC Decision              ║
║                                                                              ║
║  Cara jalankan:                                                              ║
║    python manage.py shell < lumra_full_ops_test_v2.py                        ║
║    python manage.py run_ops_test --mode small                                ║
║    python manage.py run_ops_test --mode parallel --count 5                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import random
import traceback
from decimal import Decimal
from datetime import date, datetime, time, timedelta

# ─── UTF-8 stdout/stderr ────────────────────────────────────────────────────
for _sn in ("stdout", "stderr"):
    _s = getattr(sys, _sn, None)
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════════════════
# KONFIGURASI
# ══════════════════════════════════════════════════════════════════════════════

CFG = {
    "mode": "parallel",
    "count": 4,
    "rollback": False,
    "seed": 42,
    "verbose": True,
    "start_year": 2019,
    "start_date": None,
    "end_date": None,
}

OPS_CLOCK = {"now": None, "profile": None}
CODE_SEQ = 0
VARIANT_CACHE = {"components": None, "finished": None}

# ══════════════════════════════════════════════════════════════════════════════
# DJANGO SETUP
# ══════════════════════════════════════════════════════════════════════════════

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")

import django
try:
    django.setup()
except RuntimeError as e:
    print(f"[ERROR] Django setup gagal: {e}")
    print("Jalankan lewat: python manage.py shell < lumra_full_ops_test_v2.py")
    sys.exit(1)

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.db.models import Sum, Q
from django.utils import timezone

User = get_user_model()

# ══════════════════════════════════════════════════════════════════════════════
# IMPORT MODELS - DYNAMIC LOADING dengan fallback
# ══════════════════════════════════════════════════════════════════════════════

def get_model_or_none(app_label, model_name):
    """Ambil model dengan aman, return None jika tidak ada."""
    try:
        from django.apps import apps
        return apps.get_model(app_label, model_name)
    except Exception:
        return None

# Dictionary untuk menyimpan semua model yang berhasil di-load
MODELS = {}

# Core models
MODELS['Location'] = get_model_or_none('lumra_config', 'Location')
MODELS['ProductVariant'] = get_model_or_none('lumra_config', 'ProductVariant')
MODELS['Product'] = get_model_or_none('lumra_config', 'Product')
MODELS['Stock'] = get_model_or_none('lumra_config', 'Stock')
MODELS['StockMovement'] = get_model_or_none('lumra_config', 'StockMovement')
MODELS['Vendor'] = get_model_or_none('lumra_config', 'Vendor')
MODELS['Unit'] = get_model_or_none('lumra_config', 'Unit')
MODELS['Store'] = get_model_or_none('lumra_config', 'Store')

# Transaction models
MODELS['Requisition'] = get_model_or_none('lumra_config', 'Requisition')
MODELS['RequisitionItem'] = get_model_or_none('lumra_config', 'RequisitionItem')
MODELS['Transfer'] = get_model_or_none('lumra_config', 'Transfer')
MODELS['TransferItem'] = get_model_or_none('lumra_config', 'TransferItem')

# Production models
MODELS['ProductionOrder'] = get_model_or_none('production', 'ProductionOrder') or \
                            get_model_or_none('lumra_config', 'ProductionOrder')
MODELS['ProductionMaterialConsumption'] = get_model_or_none('production', 'ProductionMaterialConsumption') or \
                                          get_model_or_none('lumra_config', 'ProductionMaterialConsumption')
MODELS['FinishedGoodsReceipt'] = get_model_or_none('production', 'FinishedGoodsReceipt') or \
                                 get_model_or_none('lumra_config', 'FinishedGoodsReceipt')
MODELS['BillOfMaterial'] = get_model_or_none('production', 'BillOfMaterial') or \
                           get_model_or_none('lumra_config', 'BillOfMaterial')
MODELS['BillOfMaterialItem'] = get_model_or_none('production', 'BillOfMaterialItem') or \
                               get_model_or_none('lumra_config', 'BillOfMaterialItem')
MODELS['Recipe'] = get_model_or_none('production', 'Recipe') or \
                   get_model_or_none('lumra_config', 'Recipe')
MODELS['RecipeIngredient'] = get_model_or_none('production', 'RecipeIngredient') or \
                             get_model_or_none('lumra_config', 'RecipeIngredient')
MODELS['RecipeCategory'] = get_model_or_none('production', 'RecipeCategory') or \
                           get_model_or_none('lumra_config', 'RecipeCategory')

# Return models
MODELS['Return'] = get_model_or_none('lumra_config', 'Return')
MODELS['ReturnItem'] = get_model_or_none('lumra_config', 'ReturnItem')

# Cek model yang berhasil di-load
print("\n" + "="*70)
print("MODEL LOADING STATUS:")
print("="*70)
for name, model in MODELS.items():
    status = f"✓ {model.__name__}" if model else "✗ MISSING"
    table_name = model._meta.db_table if model else "N/A"
    print(f"  {name:<35} | {status:<20} | Table: {table_name}")
print("="*70 + "\n")

# ══════════════════════════════════════════════════════════════════════════════
# WARNA & HELPER PRINT
# ══════════════════════════════════════════════════════════════════════════════

class C:
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"

def _v(text):
    """Hanya print jika verbose."""
    if CFG["verbose"]:
        print(text)

def hdr(text, width=72):
    _v(f"\n{C.BOLD}{C.BLUE}{'═'*width}{C.RESET}")
    _v(f"{C.BOLD}{C.BLUE}{text:^{width}}{C.RESET}")
    _v(f"{C.BOLD}{C.BLUE}{'═'*width}{C.RESET}\n")

def step(num, text):
    _v(f"{C.CYAN}  ▶ STEP {num}: {text}{C.RESET}")

def ok(text):
    _v(f"{C.GREEN}    ✓ {text}{C.RESET}")

def info(text):
    _v(f"    → {text}")

def warn(text):
    _v(f"{C.YELLOW}    ⚠ {text}{C.RESET}")

def err(text):
    print(f"{C.RED}    ✗ {text}{C.RESET}")

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE SCHEMA INSPECTOR
# ══════════════════════════════════════════════════════════════════════════════

ANNUAL_INFLATION = {
    2019: Decimal("1.028"),
    2020: Decimal("1.016"),
    2021: Decimal("1.016"),
    2022: Decimal("1.042"),
    2023: Decimal("1.037"),
    2024: Decimal("1.025"),
    2025: Decimal("1.024"),
    2026: Decimal("1.025"),
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


def parse_ymd(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def make_aware_at(day, hour, minute=0):
    naive = datetime.combine(day, time(hour=hour, minute=minute))
    return timezone.make_aware(naive, timezone.get_current_timezone())


def timeline_bounds():
    end_day = parse_ymd(CFG.get("end_date")) or timezone.localdate()
    start_day = parse_ymd(CFG.get("start_date")) or date(int(CFG.get("start_year") or 2019), 1, 1)
    if start_day > end_day:
        start_day, end_day = end_day, start_day
    return start_day, end_day


def inflation_multiplier(day):
    factor = Decimal("1.00")
    for year in range(2019, day.year + 1):
        factor *= ANNUAL_INFLATION.get(year, Decimal("1.025"))
    return factor.quantize(Decimal("0.0001"))


def business_profile_for(day, rng):
    years_since_2019 = Decimal(str(max(0, day.year - 2019)))
    growth = Decimal("1.00") + years_since_2019 * Decimal("0.075")
    seasonal = MONTH_SEASONALITY.get(day.month, Decimal("1.00"))
    weekday = WEEKDAY_SEASONALITY.get(day.weekday(), Decimal("1.00"))
    shock = Decimal(str(round(rng.uniform(0.82, 1.22), 3)))
    event_lift = Decimal("1.00")

    if day.month == 12:
        event_lift += Decimal("0.12")
    if day.month in (4, 5):
        event_lift += Decimal("0.08")
    if day.year == 2020 and day.month in (4, 5, 6, 7):
        event_lift -= Decimal("0.22")
    if day.year == 2021 and day.month in (1, 2, 7):
        event_lift -= Decimal("0.12")

    demand = max(Decimal("0.45"), growth * seasonal * weekday * shock * event_lift)
    return {
        "date": day,
        "demand": demand.quantize(Decimal("0.0001")),
        "inflation": inflation_multiplier(day),
        "seasonality": (seasonal * weekday * event_lift).quantize(Decimal("0.0001")),
    }


def scenario_day(index, total, rng):
    start_day, end_day = timeline_bounds()
    span_days = max(0, (end_day - start_day).days)
    if total <= 1 or span_days == 0:
        return end_day
    segment = span_days / total
    low = int(index * segment)
    high = int((index + 1) * segment)
    return start_day + timedelta(days=rng.randint(low, max(low, high)))


def set_ops_clock(day, rng, profile=None, hour=None):
    if hour is None:
        hour = rng.choices([7, 8, 9, 10, 13, 15, 17, 19], weights=[6, 10, 12, 12, 10, 8, 5, 3])[0]
    minute = rng.choice([0, 5, 10, 15, 20, 30, 40, 45, 50])
    OPS_CLOCK["now"] = make_aware_at(day, hour, minute)
    OPS_CLOCK["profile"] = profile or business_profile_for(day, rng)
    return OPS_CLOCK["now"]


def ops_now(offset_hours=0):
    return (OPS_CLOCK.get("now") or timezone.now()) + timedelta(hours=offset_hours)


def scale_qty(base_qty, minimum=1):
    profile = OPS_CLOCK.get("profile") or {}
    demand = Decimal(str(profile.get("demand", Decimal("1.00"))))
    qty = int((Decimal(str(base_qty)) * demand).to_integral_value())
    return max(minimum, qty)


def inflate_money(value):
    profile = OPS_CLOCK.get("profile") or {}
    inflation = Decimal(str(profile.get("inflation", Decimal("1.00"))))
    return (Decimal(str(value or 0)) * inflation).quantize(Decimal("0.01"))


class SchemaInspector:
    """Inspect database schema untuk mendapatkan field info."""
    
    def __init__(self):
        self.cache = {}
    
    def get_fields(self, model):
        """Get all fields dari model beserta type-nya."""
        if model is None:
            return []
        
        model_key = f"{model._meta.app_label}.{model._meta.model_name}"
        if model_key not in self.cache:
            fields = []
            for field in model._meta.get_fields():
                field_info = {
                    'name': field.name,
                    'type': type(field).__name__,
                    'internal_type': getattr(field, 'internal_type', 'Unknown'),
                    'is_relation': field.is_relation,
                    'null': getattr(field, 'null', True),
                    'blank': getattr(field, 'blank', True),
                    'default': getattr(field, 'default', None),
                    'choices': getattr(field, 'choices', None),
                }
                # Jika foreign key, simpan related model
                if field.is_relation and hasattr(field, 'related_model'):
                    field_info['related_model'] = field.related_model
                fields.append(field_info)
            self.cache[model_key] = fields
        return self.cache[model_key]
    
    def has_field(self, model, field_name):
        """Cek apakah model memiliki field tertentu."""
        fields = self.get_fields(model)
        return any(f['name'] == field_name for f in fields)
    
    def get_required_fields(self, model):
        """Get fields yang required (not null, no default)."""
        fields = self.get_fields(model)
        required = []
        for f in fields:
            if not f['null'] and not f['blank'] and f['default'] is None:
                if f['name'] != 'id':  # Skip auto id
                    required.append(f)
        return required
    
    def safe_create(self, model, **kwargs):
        """Create instance dengan aman, hanya gunakan field yang ada."""
        if model is None:
            raise ValueError(f"Model is None")

        occurred_at = kwargs.pop("_occurred_at", None)
        
        valid_fields = {f['name'] for f in self.get_fields(model)}
        
        # Filter kwargs hanya yang field-nya ada
        safe_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        # Log jika ada field yang di-skip
        skipped = set(kwargs.keys()) - set(safe_kwargs.keys())
        if skipped:
            warn(f"Field di-skip (tidak ada di {model._meta.model_name}): {skipped}")
        
        with transaction.atomic():
            obj = model.objects.create(**safe_kwargs)
        if occurred_at:
            updates = {}
            if "created_at" in valid_fields:
                updates["created_at"] = occurred_at
            if "updated_at" in valid_fields:
                updates["updated_at"] = occurred_at
            if "last_updated" in valid_fields:
                updates["last_updated"] = occurred_at
            if updates:
                model.objects.filter(pk=obj.pk).update(**updates)
                for field, value in updates.items():
                    setattr(obj, field, value)
        return obj

inspector = SchemaInspector()

# ══════════════════════════════════════════════════════════════════════════════
# HELPER: STOCK (dengan dynamic field handling)
# ══════════════════════════════════════════════════════════════════════════════

def stock_net(variant, location) -> int:
    """Hitung stok bersih (in - out) untuk variant di lokasi tertentu."""
    StockModel = MODELS['Stock']
    if StockModel is None:
        warn("Model Stock tidak tersedia, return 0")
        return 0
    
    qs = StockModel.objects.filter(variant=variant, location=location)
    
    # Dynamic transaction types berdasarkan field yang ada
    inbound_types = ["in", "adjustment", "transfer_received"]
    outbound_types = ["out", "transfer_sent"]
    
    # Cek field transaction_type ada
    if inspector.has_field(StockModel, 'transaction_type'):
        inbound = qs.filter(transaction_type__in=inbound_types).aggregate(t=Sum("quantity"))["t"] or 0
        outbound = qs.filter(transaction_type__in=outbound_types).aggregate(t=Sum("quantity"))["t"] or 0
    else:
        # Fallback: sum semua quantity positif/negatif
        inbound = qs.filter(quantity__gt=0).aggregate(t=Sum("quantity"))["t"] or 0
        outbound = qs.filter(quantity__lt=0).aggregate(t=Sum("quantity"))["t"] or 0
        outbound = abs(outbound)
    
    return int(inbound) - int(outbound)


def add_stock(variant, location, qty: int, tx_type: str, notes: str):
    """Tambah record stock dengan dynamic field handling."""
    StockModel = MODELS['Stock']
    if StockModel is None:
        warn("Model Stock tidak tersedia")
        return None
    
    kwargs = {
        'variant': variant,
        'location': location,
        'quantity': qty,
        'notes': notes,
        '_occurred_at': ops_now(),
    }
    
    # Tambahkan transaction_type jika field ada
    if inspector.has_field(StockModel, 'transaction_type'):
        kwargs['transaction_type'] = tx_type
    
    # Tambahkan created_at jika ada
    if inspector.has_field(StockModel, 'created_at'):
        kwargs['created_at'] = ops_now()
    if inspector.has_field(StockModel, 'last_updated'):
        kwargs['last_updated'] = ops_now()
    
    try:
        return inspector.safe_create(StockModel, **kwargs)
    except Exception as e:
        warn(f"Gagal create Stock: {e}")
        return None


def add_movement(variant, location, qty, mv_type, ref_type, ref_id, ref_no, actor, notes):
    """Tambah StockMovement dengan dynamic field handling."""
    MovementModel = MODELS['StockMovement']
    if MovementModel is None:
        warn("Model StockMovement tidak tersedia")
        return None
    
    kwargs = {
        'product': variant,
        'location': location,
        'quantity': Decimal(str(qty)),
        'notes': notes,
        '_occurred_at': ops_now(),
    }
    
    # Mapping field dinamis
    field_mappings = {
        'movement_type': mv_type,
        'reference_type': ref_type,
        'reference_id': ref_id,
        'reference_number': ref_no,
        'created_by': actor,
    }
    
    for field, value in field_mappings.items():
        if inspector.has_field(MovementModel, field):
            kwargs[field] = value
    
    if inspector.has_field(MovementModel, 'created_at'):
        kwargs['created_at'] = ops_now()
    
    try:
        return inspector.safe_create(MovementModel, **kwargs)
    except Exception as e:
        warn(f"Gagal create StockMovement: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# HELPER: PICKING DATA EXISTING (dengan validasi ketat)
# ══════════════════════════════════════════════════════════════════════════════

def ensure_actor() -> User:
    """Pastikan ada user untuk menjadi actor."""
    actor = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.filter(is_staff=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    if not actor:
        actor = User.objects.create_user(
            username="ops.seed",
            email="ops.seed@lumra.local",
            password="lumra123",
            is_staff=True,
        )
        warn(f"Tidak ada user existing — dibuat user seed: {actor.username}")
    return actor


def pick_locations():
    """
    Ambil lokasi dari database existing.
    Prioritas: warehouse → production → store → quarantine.
    """
    LocationModel = MODELS['Location']
    if LocationModel is None:
        raise ValueError("Model Location tidak tersedia!")
    
    locs = list(LocationModel.objects.all().order_by("name")[:100])  # Limit 100 untuk performa
    if len(locs) < 3:
        raise ValueError(
            f"Minimal perlu 3 lokasi (ada {len(locs)}). "
            "Pastikan lumra_config_locations sudah terisi."
        )

    def _find(keywords, exclude_ids):
        for loc in locs:
            if loc.id in exclude_ids:
                continue
            # Cek beberapa kemungkinan nama field
            loc_type = getattr(loc, 'location_type', '') or ''
            loc_name = getattr(loc, 'name', '') or ''
            hay = f"{loc_type} {loc_name}".lower()
            if any(k in hay for k in keywords):
                return loc
        return None

    used = set()

    warehouse = _find(["warehouse", "gudang", "wh"], used)
    if not warehouse:
        warehouse = locs[0]
    used.add(warehouse.id)

    production = _find(["production", "produksi", "dapur", "kitchen", "manufaktur"], used)
    if not production:
        production = next((l for l in locs if l.id not in used), None) or warehouse
    used.add(production.id)

    quarantine = _find(["quarantine", "karantina", "qc", "hold"], used)
    if not quarantine:
        quarantine = next((l for l in locs if l.id not in used), None) or production
    used.add(quarantine.id)

    store = _find(["store", "toko", "cabang", "retail", "outlet"], used)
    if not store:
        store = next((l for l in locs if l.id not in used), None) or locs[-1]

    return warehouse, production, quarantine, store


def pick_variants(rng: random.Random, n_components=3, exclude_ids=None):
    """
    Pilih variant secara random dari database existing.
    - Komponen (bahan baku): n_components variant harga rendah
    - Finished good: 1 variant harga lebih tinggi
    """
    VariantModel = MODELS['ProductVariant']
    ProductModel = MODELS['Product']
    
    if VariantModel is None:
        raise ValueError("Model ProductVariant tidak tersedia!")
    
    exclude_ids = exclude_ids or set()

    if VARIANT_CACHE["components"] is None or VARIANT_CACHE["finished"] is None:
        base = VariantModel.objects.select_related("product", "product__unit")
        if ProductModel and inspector.has_field(ProductModel, 'is_active'):
            base = base.filter(product__is_active=True)

        # Tabel variant bisa jutaan row. Hindari ORDER BY harga karena mahal;
        # pakai PK-index windows sebagai sample stabil dan cukup realistis.
        VARIANT_CACHE["components"] = list(base.order_by("id")[:2000])
        VARIANT_CACHE["finished"] = list(base.order_by("-id")[:2000])

    components_pool = [v for v in VARIANT_CACHE["components"] if v.id not in exclude_ids]
    finished_pool = [v for v in VARIANT_CACHE["finished"] if v.id not in exclude_ids]

    if len(components_pool) < n_components or not finished_pool:
        raise ValueError(
            f"Perlu minimal {n_components + 1} ProductVariant active "
            f"(cache: {len(components_pool)} komponen, {len(finished_pool)} finished)."
        )

    components = rng.sample(components_pool, n_components)
    comp_ids = {c.id for c in components}
    fg_candidates = [v for v in finished_pool if v.id not in comp_ids]
    if not fg_candidates:
        raise ValueError("Tidak dapat menemukan variant untuk finished good.")
    fg = rng.choice(fg_candidates)

    return fg, components


def pick_vendor(rng: random.Random):
    """Pilih vendor aktif secara random."""
    VendorModel = MODELS['Vendor']
    if VendorModel is None:
        raise ValueError("Model Vendor tidak tersedia!")
    
    vendors = list(VendorModel.objects.all().order_by("id")[:50])
    if not vendors:
        raise ValueError("Tidak ada vendor di tabel vendors.")
    return rng.choice(vendors)


def pick_unit(rng: random.Random):
    """Pilih unit aktif secara random."""
    UnitModel = MODELS['Unit']
    if UnitModel is None:
        raise ValueError("Model Unit tidak tersedia!")
    
    units = list(UnitModel.objects.all().order_by("id")[:50])
    if not units:
        raise ValueError("Tidak ada unit di tabel units.")
    return rng.choice(units)


def ts_code(prefix: str) -> str:
    """Generate kode unik berbasis timestamp."""
    global CODE_SEQ
    CODE_SEQ += 1
    live_suffix = timezone.now().strftime("%H%M%S%f")[-8:]
    return f"{prefix}-{ops_now().strftime('%Y%m%d')}-{CODE_SEQ:06d}-{live_suffix}"

# ══════════════════════════════════════════════════════════════════════════════
# FASE 1 — INBOUND: PO VENDOR → GUDANG
# ══════════════════════════════════════════════════════════════════════════════

def fase_inbound(rng, actor, warehouse, components, vendor, scenario_tag=""):
    """
    Simulasi barang masuk dari vendor ke gudang.
    Returns dict qty per component.
    """
    step("1", f"[{scenario_tag}] INBOUND — Barang masuk dari vendor ke gudang")
    info(f"Vendor : {vendor.name}")
    info(f"Gudang : {warehouse.name}")

    inbound_qty = {}
    for comp in components:
        qty = scale_qty(rng.randint(20, 60), minimum=8)
        
        # Create stock record
        add_stock(comp, warehouse, qty, "in",
                  f"[{scenario_tag}] PO dari {vendor.name}")
        
        # Create movement record
        add_movement(comp, warehouse, qty, "purchase_in",
                     "purchase_order", 0, ts_code("PO"), actor,
                     f"[{scenario_tag}] Inbound dari {vendor.name}")
        
        inbound_qty[comp.id] = qty
        ok(f"  {getattr(comp, 'sku', comp.id)} masuk {qty} unit → {warehouse.name}")

    return inbound_qty


# ══════════════════════════════════════════════════════════════════════════════
# FASE 2 — RnD: RECIPE PERCOBAAN → UJI COBA → APPROVE → BOM
# ══════════════════════════════════════════════════════════════════════════════

def fase_rnd(rng, actor, warehouse, finished_variant, components, unit, scenario_tag=""):
    """
    Flow RnD lengkap.
    Returns (recipe, bom, component_qty)
    """
    step("2", f"[{scenario_tag}] RnD — Recipe percobaan → Uji coba → BOM")

    RecipeModel = MODELS['Recipe']
    RecipeCatModel = MODELS['RecipeCategory']
    RecipeIngModel = MODELS['RecipeIngredient']
    BOMModel = MODELS['BillOfMaterial']
    BOMItemModel = MODELS['BillOfMaterialItem']

    # ── 2a. Buat/Buat Category ─────────────────────────────────────────────
    recipe_cat = None
    if RecipeCatModel:
        try:
            recipe_cat, _ = RecipeCatModel.objects.get_or_create(
                name="Trial Batch",
                defaults={"description": "Kategori untuk recipe percobaan RnD"},
            )
        except Exception as e:
            warn(f"Gagal buat RecipeCategory: {e}")

    # ── 2b. Buat Recipe ────────────────────────────────────────────────────
    yield_qty = Decimal(str(rng.choice([10, 12, 15, 20])))
    recipe_name = f"[TRIAL] {finished_variant.product.name} {ts_code('RCP')}"
    
    recipe = None
    if RecipeModel:
        try:
            recipe_kwargs = {
                'name': recipe_name,
                'description': f"Recipe percobaan untuk {finished_variant.product.name}",
                'instructions': "1. Siapkan bahan\n2. Proses mixing\n3. QC output\n4. Evaluasi",
                'yield_quantity': yield_qty,
                'yield_unit': unit,
                'preparation_time': rng.choice([30, 45, 60, 90]),
                'total_cost': Decimal("0"),
                'cost_per_unit': Decimal("0"),
                'is_archived': False,
                '_occurred_at': ops_now(),
            }
            
            if recipe_cat and inspector.has_field(RecipeModel, 'category'):
                recipe_kwargs['category'] = recipe_cat
            
            if inspector.has_field(RecipeModel, 'created_by'):
                recipe_kwargs['created_by'] = actor
            
            recipe = inspector.safe_create(RecipeModel, **recipe_kwargs)
            info(f"Recipe dibuat  : {recipe.name} (yield {yield_qty})")
            
        except Exception as e:
            err(f"Gagal buat Recipe: {e}")
            traceback.print_exc()

    # ── 2c. Tambahkan bahan ke recipe ─────────────────────────────────────
    component_qty = {}
    if recipe and RecipeIngModel:
        for comp in components:
            qty = Decimal(str(rng.randint(3, 10)))
            unit_cost = inflate_money(getattr(comp, 'price_buy', None) or Decimal("1000"))
            
            ing_kwargs = {
                'recipe': recipe,
                'variant': comp,
                'quantity': qty,
                'unit': getattr(comp.product, 'unit', None) if hasattr(comp, 'product') else unit,
                'unit_cost': unit_cost,
                'subtotal_cost': qty * unit_cost,
                'notes': f"Bahan percobaan dari {getattr(comp, 'sku', comp.id)}",
            }
            
            try:
                RecipeIngModel.objects.create(**ing_kwargs)
                component_qty[comp.id] = qty
                info(f"  Bahan recipe : {getattr(comp, 'sku', comp.id)} × {qty}")
            except Exception as e:
                warn(f"  Gagal tambah ingredient: {e}")

    # Update total cost recipe
    if recipe:
        try:
            total_cost = sum(
                Decimal(str(component_qty[c.id])) * inflate_money(getattr(c, 'price_buy', None) or Decimal("1000"))
                for c in components if c.id in component_qty
            )
            update_fields = ['total_cost', 'cost_per_unit']
            recipe.total_cost = total_cost
            recipe.cost_per_unit = total_cost / yield_qty if yield_qty else Decimal("0")
            
            if inspector.has_field(recipe.__class__, 'updated_at'):
                recipe.updated_at = ops_now(1)
                update_fields.append('updated_at')
            
            recipe.save(update_fields=update_fields)
        except Exception as e:
            warn(f"Gagal update cost recipe: {e}")

    # ── 2d. Uji coba: ambil stok dari gudang ─────────────────────────────
    info("Uji coba: ambil stok bahan dari gudang...")
    for comp in components:
        if comp.id not in component_qty:
            continue
            
        trial_qty = int(component_qty[comp.id])
        current = stock_net(comp, warehouse)
        if current < trial_qty:
            warn(f"  Stok {getattr(comp, 'sku', comp.id)} kurang ({current} < {trial_qty}), top-up otomatis")
            add_stock(comp, warehouse, trial_qty - current + 5, "adjustment",
                      f"[{scenario_tag}] Auto top-up untuk uji coba RnD")
        
        add_stock(comp, warehouse, trial_qty, "out",
                  f"[{scenario_tag}] Konsumsi uji coba recipe {recipe_name}")
        add_movement(comp, warehouse, trial_qty, "rnd_out",
                     "recipe_trial", recipe.id if recipe else 0, recipe_name, actor,
                     f"[{scenario_tag}] Konsumsi bahan uji coba")
        ok(f"  Uji coba konsumsi {getattr(comp, 'sku', comp.id)} : {trial_qty} unit dari gudang")

    # ── 2e. Approve recipe → buat BOM ─────────────────────────────────────
    bom = None
    if BOMModel:
        try:
            bom_code = ts_code("BOM")
            bom_kwargs = {
                'code': bom_code,
                'version': 1,
                'name': f"BOM — {finished_variant.product.name} (dari {recipe_name})",
                'notes': f"Auto-generated dari recipe percobaan: {recipe_name}",
                '_occurred_at': ops_now(1),
            }
            
            # Cek field finished_variant atau product
            if inspector.has_field(BOMModel, 'finished_variant'):
                bom_kwargs['finished_variant'] = finished_variant
            elif inspector.has_field(BOMModel, 'product'):
                bom_kwargs['product'] = finished_variant.product if hasattr(finished_variant, 'product') else finished_variant
            
            if inspector.has_field(BOMModel, 'created_by'):
                bom_kwargs['created_by'] = actor
            
            bom = inspector.safe_create(BOMModel, **bom_kwargs)
            
            # BOM Items
            if BOMItemModel:
                for comp in components:
                    if comp.id in component_qty:
                        item_kwargs = {
                            'bom': bom,
                            'component': comp,
                            'quantity': component_qty[comp.id],
                            'unit': getattr(comp.product, 'unit', None) if hasattr(comp, 'product') else unit,
                            'notes': "Dari recipe percobaan yang sudah approved",
                        }
                        try:
                            BOMItemModel.objects.create(**item_kwargs)
                        except Exception as e:
                            warn(f"  Gagal buat BOM Item: {e}")
            
            ok(f"BOM dibuat     : {bom.code} → {bom.name}")
            
        except Exception as e:
            err(f"Gagal buat BOM: {e}")
            traceback.print_exc()

    return recipe, bom, component_qty


# ══════════════════════════════════════════════════════════════════════════════
# FASE 3 — PRODUKSI: PRODUCTION ORDER → REQUISITION → PROSES → FINISHED GOODS
# ══════════════════════════════════════════════════════════════════════════════

def fase_produksi(rng, actor, warehouse, production, finished_variant, components,
                  bom, component_qty_recipe, unit, scenario_tag=""):
    """
    Alur produksi penuh.
    Returns (production_order, fg_qty)
    """
    step("3", f"[{scenario_tag}] PRODUKSI — Production Order")

    ProdOrderModel = MODELS['ProductionOrder']
    MatConsumpModel = MODELS['ProductionMaterialConsumption']
    FGReceiptModel = MODELS['FinishedGoodsReceipt']
    RequisitionModel = MODELS['Requisition']
    ReqItemModel = MODELS['RequisitionItem']
    TransferModel = MODELS['Transfer']
    TransferItemModel = MODELS['TransferItem']

    # ── 3a. Target qty produksi ────────────────────────────────────────────
    target_qty = Decimal(str(scale_qty(rng.choice([24, 30, 36, 48, 60]), minimum=12)))
    scheduled_date = (OPS_CLOCK.get("profile") or {}).get("date", timezone.localdate())

    info(f"BOM         : {bom.code if bom else 'N/A'}")
    info(f"Target qty  : {target_qty}")
    info(f"Lokasi prod : {production.name}")

    # ── 3b. Production Order ───────────────────────────────────────────────
    prod_order = None
    if ProdOrderModel:
        try:
            prod_code = ts_code("PROD")
            po_kwargs = {
                'code': prod_code,
                'status': 'completed',
                'target_quantity': target_qty,
                'produced_quantity': target_qty,
                'scheduled_date': scheduled_date,
                'priority': rng.choice(['Normal', 'High', 'Urgent']),
                'notes': f"[{scenario_tag}] Production order",
                '_occurred_at': ops_now(3),
            }
            
            # Field opsional
            if inspector.has_field(ProdOrderModel, 'bom') and bom:
                po_kwargs['bom'] = bom
            if inspector.has_field(ProdOrderModel, 'unit'):
                po_kwargs['unit'] = unit
            if inspector.has_field(ProdOrderModel, 'line'):
                po_kwargs['line'] = rng.choice(['Line A', 'Line B', 'Line C'])
            if inspector.has_field(ProdOrderModel, 'started_at'):
                po_kwargs['started_at'] = ops_now(3)
            if inspector.has_field(ProdOrderModel, 'completed_at'):
                po_kwargs['completed_at'] = ops_now(8)
            if inspector.has_field(ProdOrderModel, 'created_by'):
                po_kwargs['created_by'] = actor
            
            prod_order = inspector.safe_create(ProdOrderModel, **po_kwargs)
            ok(f"Production Order  : {prod_order.code}")
            
        except Exception as e:
            err(f"Gagal buat ProductionOrder: {e}")
            traceback.print_exc()

    # ── 3c. Hitung kebutuhan bahan & Requisition ──────────────────────────
    needed_qty = {}
    for comp in components:
        base_qty = component_qty_recipe.get(comp.id, Decimal("5"))
        needed = base_qty * target_qty / Decimal("10")
        needed = max(needed, Decimal("1"))
        needed_qty[comp.id] = int(needed)

    # Requisition
    req = None
    if RequisitionModel:
        try:
            req_kwargs = {
                'status': 'completed',
                'notes': f"[{scenario_tag}] Requisisi produksi",
                '_occurred_at': ops_now(1),
            }
            
            if inspector.has_field(RequisitionModel, 'from_location'):
                req_kwargs['from_location'] = warehouse
            if inspector.has_field(RequisitionModel, 'to_location'):
                req_kwargs['to_location'] = production
            if inspector.has_field(RequisitionModel, 'requested_by'):
                req_kwargs['requested_by'] = actor
            if inspector.has_field(RequisitionModel, 'approved_by'):
                req_kwargs['approved_by'] = actor
            if inspector.has_field(RequisitionModel, 'approved_at'):
                req_kwargs['approved_at'] = ops_now(2)
            
            req = inspector.safe_create(RequisitionModel, **req_kwargs)
            
            # Requisition Items
            if ReqItemModel:
                for comp in components:
                    q = needed_qty.get(comp.id, 5)
                    try:
                        ReqItemModel.objects.create(
                            requisition=req,
                            variant=comp,
                            quantity=q,
                        )
                    except Exception as e:
                        warn(f"  Gagal buat RequisitionItem: {e}")
            
            info(f"Requisition     : #{req.id}")
            
        except Exception as e:
            warn(f"Gagal buat Requisition: {e}")

    # ── 3d. Transfer gudang → produksi ────────────────────────────────────
    trf_gd_prod = None
    if TransferModel:
        try:
            trf_kwargs = {
                'status': 'received',
                'notes': f"[{scenario_tag}] Transfer bahan ke produksi",
                '_occurred_at': ops_now(2),
            }
            
            if inspector.has_field(TransferModel, 'requisition') and req:
                trf_kwargs['requisition'] = req
            if inspector.has_field(TransferModel, 'source_location'):
                trf_kwargs['source_location'] = warehouse
            if inspector.has_field(TransferModel, 'destination_location'):
                trf_kwargs['destination_location'] = production
            if inspector.has_field(TransferModel, 'created_by'):
                trf_kwargs['created_by'] = actor
            if inspector.has_field(TransferModel, 'sent_at'):
                trf_kwargs['sent_at'] = ops_now(2)
            if inspector.has_field(TransferModel, 'received_at'):
                trf_kwargs['received_at'] = ops_now(3)
            
            trf_gd_prod = inspector.safe_create(TransferModel, **trf_kwargs)
            
            # Transfer Items
            if TransferItemModel:
                for comp in components:
                    q = needed_qty.get(comp.id, 5)
                    
                    # Cek stok & top-up jika perlu
                    current = stock_net(comp, warehouse)
                    if current < q:
                        warn(f"  Stok gudang {getattr(comp, 'sku', comp.id)} kurang, top-up otomatis")
                        add_stock(comp, warehouse, q - current + 5, "adjustment",
                                  f"[{scenario_tag}] Auto top-up sebelum transfer")
                    
                    try:
                        ti_kwargs = {
                            'transfer': trf_gd_prod,
                            'variant': comp,
                            'quantity_sent': q,
                            'quantity_received': q,
                        }
                        TransferItemModel.objects.create(**ti_kwargs)
                        
                        # Update stok
                        add_stock(comp, warehouse, q, "transfer_sent",
                                  f"Transfer #{trf_gd_prod.id} ke produksi")
                        add_stock(comp, production, q, "transfer_received",
                                  f"Transfer #{trf_gd_prod.id} dari gudang")
                        add_movement(comp, warehouse, q, "transfer_out", 
                                    "transfer", trf_gd_prod.id, f"TRF-{trf_gd_prod.id}", 
                                    actor, "Keluar ke produksi")
                        add_movement(comp, production, q, "transfer_in",
                                    "transfer", trf_gd_prod.id, f"TRF-{trf_gd_prod.id}",
                                    actor, "Masuk dari gudang")
                        
                        ok(f"  Transfer {getattr(comp, 'sku', comp.id)} : {q} unit → {production.name}")
                        
                    except Exception as e:
                        warn(f"  Gagal buat TransferItem: {e}")
                        
        except Exception as e:
            warn(f"Gagal buat Transfer: {e}")

    # ── 3e. Proses produksi (konsumsi bahan) ──────────────────────────────
    if MatConsumpModel and prod_order:
        for comp in components:
            q = needed_qty.get(comp.id, 5)
            try:
                mc_kwargs = {
                    'production_order': prod_order,
                    'component': comp,
                    'quantity': Decimal(str(q)),
                    'notes': f"[{scenario_tag}] Konsumsi produksi",
                }
                
                if inspector.has_field(MatConsumpModel, 'unit'):
                    mc_kwargs['unit'] = getattr(comp.product, 'unit', None) if hasattr(comp, 'product') else unit
                if inspector.has_field(MatConsumpModel, 'consumed_at'):
                    mc_kwargs['consumed_at'] = ops_now(5)
                
                MatConsumpModel.objects.create(**mc_kwargs)
                
                add_stock(comp, production, q, "out",
                          f"Produksi konsumsi {getattr(comp, 'sku', comp.id)}")
                add_movement(comp, production, q, "production_out",
                            "production_order", prod_order.id, 
                            getattr(prod_order, 'code', str(prod_order.id)),
                            actor, "Dikonsumsi dalam produksi")
                
                ok(f"  Konsumsi produksi {getattr(comp, 'sku', comp.id)} : {q}")
                
            except Exception as e:
                warn(f"  Gagal catat MaterialConsumption: {e}")

    # ── 3f. Finished goods masuk gudang utama ─────────────────────────────
    if FGReceiptModel and prod_order:
        try:
            fgr_kwargs = {
                'quantity_received': target_qty,
                'notes': f"[{scenario_tag}] FG dari produksi",
            }
            
            if inspector.has_field(FGReceiptModel, 'production_order'):
                fgr_kwargs['production_order'] = prod_order
            if inspector.has_field(FGReceiptModel, 'finished_variant'):
                fgr_kwargs['finished_variant'] = finished_variant
            if inspector.has_field(FGReceiptModel, 'location'):
                fgr_kwargs['location'] = warehouse
            if inspector.has_field(FGReceiptModel, 'received_at'):
                fgr_kwargs['received_at'] = ops_now(9)
            
            FGReceiptModel.objects.create(**fgr_kwargs)
            
            add_stock(finished_variant, warehouse, int(target_qty), "in",
                      f"FG dari produksi {getattr(prod_order, 'code', prod_order.id)}")
            add_movement(finished_variant, warehouse, target_qty, "production_in",
                        "production_order", prod_order.id,
                        getattr(prod_order, 'code', str(prod_order.id)),
                        actor, "Finished goods masuk gudang")
            
            ok(f"Finished goods    : {getattr(finished_variant, 'sku', finished_variant.id)} × {target_qty} → {warehouse.name}")
            
        except Exception as e:
            warn(f"Gagal catat FinishedGoodsReceipt: {e}")

    return prod_order, int(target_qty)


# ══════════════════════════════════════════════════════════════════════════════
# FASE 4 — TRANSFER: GUDANG → TOKO
# ══════════════════════════════════════════════════════════════════════════════

def fase_transfer(rng, actor, warehouse, store, finished_variant,
                  available_qty: int, scenario_tag=""):
    """
    Transfer finished goods dari gudang ke toko/cabang.
    Returns (transfer_obj, send_qty)
    """
    step("4", f"[{scenario_tag}] TRANSFER — Gudang → Toko")
    info(f"Toko : {store.name}")

    send_qty = max(1, int(available_qty * rng.uniform(0.5, 0.85)))

    RequisitionModel = MODELS['Requisition']
    ReqItemModel = MODELS['RequisitionItem']
    TransferModel = MODELS['Transfer']
    TransferItemModel = MODELS['TransferItem']

    # Requisition
    req_store = None
    if RequisitionModel:
        try:
            req_kwargs = {'status': 'completed', '_occurred_at': ops_now(11)}
            
            if inspector.has_field(RequisitionModel, 'from_location'):
                req_kwargs['from_location'] = warehouse
            if inspector.has_field(RequisitionModel, 'to_location'):
                req_kwargs['to_location'] = store
            if inspector.has_field(RequisitionModel, 'requested_by'):
                req_kwargs['requested_by'] = actor
            if inspector.has_field(RequisitionModel, 'approved_by'):
                req_kwargs['approved_by'] = actor
            if inspector.has_field(RequisitionModel, 'approved_at'):
                req_kwargs['approved_at'] = ops_now(12)
            
            req_store = inspector.safe_create(RequisitionModel, **req_kwargs)
            
            if ReqItemModel:
                ReqItemModel.objects.create(
                    requisition=req_store,
                    variant=finished_variant,
                    quantity=send_qty,
                )
                
        except Exception as e:
            warn(f"Gagal buat Requisition toko: {e}")

    # Transfer
    trf_store = None
    if TransferModel:
        try:
            trf_kwargs = {
                'status': 'received',
                'notes': f"[{scenario_tag}] Kiriman FG ke toko {store.name}",
                '_occurred_at': ops_now(13),
            }
            
            if inspector.has_field(TransferModel, 'requisition') and req_store:
                trf_kwargs['requisition'] = req_store
            if inspector.has_field(TransferModel, 'source_location'):
                trf_kwargs['source_location'] = warehouse
            if inspector.has_field(TransferModel, 'destination_location'):
                trf_kwargs['destination_location'] = store
            if inspector.has_field(TransferModel, 'created_by'):
                trf_kwargs['created_by'] = actor
            if inspector.has_field(TransferModel, 'sent_at'):
                trf_kwargs['sent_at'] = ops_now(13)
            if inspector.has_field(TransferModel, 'received_at'):
                trf_kwargs['received_at'] = ops_now(15)
            
            trf_store = inspector.safe_create(TransferModel, **trf_kwargs)
            
            if TransferItemModel:
                TransferItemModel.objects.create(
                    transfer=trf_store,
                    variant=finished_variant,
                    quantity_sent=send_qty,
                    quantity_received=send_qty,
                )
            
            # Update stok
            add_stock(finished_variant, warehouse, send_qty, "transfer_sent",
                      f"Transfer #{trf_store.id} ke {store.name}")
            add_stock(finished_variant, store, send_qty, "transfer_received",
                      f"Transfer #{trf_store.id} dari gudang")
            add_movement(finished_variant, warehouse, Decimal(str(send_qty)),
                        "transfer_out", "transfer", trf_store.id,
                        f"TRF-{trf_store.id}", actor, f"FG keluar ke {store.name}")
            add_movement(finished_variant, store, Decimal(str(send_qty)),
                        "transfer_in", "transfer", trf_store.id,
                        f"TRF-{trf_store.id}", actor, f"FG masuk di {store.name}")
            
            ok(f"Transfer selesai  : {getattr(finished_variant, 'sku', finished_variant.id)} × {send_qty} → {store.name}")
            
        except Exception as e:
            err(f"Gagal buat Transfer toko: {e}")
            traceback.print_exc()

    return trf_store, send_qty


# ══════════════════════════════════════════════════════════════════════════════
# FASE 5 — RETURN: TOKO → GUDANG KARANTINA → QC DECISION
# ══════════════════════════════════════════════════════════════════════════════

def fase_return(rng, actor, store, warehouse, quarantine,
                finished_variant, store_qty: int, scenario_tag=""):
    """
    Return dari toko ke karantina → QC decision.
    Returns (qc_result, return_qty)
    """
    step("5", f"[{scenario_tag}] RETURN — Toko → Karantina → QC")

    return_qty = max(1, int(store_qty * rng.uniform(0.10, 0.30)))
    info(f"Return qty   : {return_qty} dari {store.name}")
    info(f"Karantina    : {quarantine.name}")

    ReturnModel = MODELS['Return']
    ReturnItemModel = MODELS['ReturnItem']

    # ── 5a. Stok keluar dari toko, masuk karantina ────────────────────────
    ret_obj = None
    if ReturnModel:
        try:
            ret_kwargs = {
                'status': 'in_quarantine',
                'notes': f"[{scenario_tag}] Return dari {store.name}",
                '_occurred_at': ops_now(20),
            }
            
            if inspector.has_field(ReturnModel, 'origin_location'):
                ret_kwargs['origin_location'] = store
            if inspector.has_field(ReturnModel, 'destination_location'):
                ret_kwargs['destination_location'] = quarantine
            if inspector.has_field(ReturnModel, 'created_by'):
                ret_kwargs['created_by'] = actor
            
            ret_obj = inspector.safe_create(ReturnModel, **ret_kwargs)
            
            if ReturnItemModel:
                ReturnItemModel.objects.create(
                    return_record=ret_obj,
                    variant=finished_variant,
                    quantity=return_qty,
                    reason=f"[{scenario_tag}] Quality issue",
                )
                
        except Exception as e:
            warn(f"Gagal buat Return: {e}")

    # Update stok
    add_stock(finished_variant, store,      return_qty, "out",
              f"[{scenario_tag}] Return ke karantina")
    add_stock(finished_variant, quarantine, return_qty, "in",
              f"[{scenario_tag}] Return masuk karantina dari {store.name}")
    add_movement(finished_variant, store,      Decimal(str(return_qty)),
                "return_out", "return", ret_obj.id if ret_obj else 0, 
                ts_code("RET"), actor, f"[{scenario_tag}] Barang return keluar dari toko")
    add_movement(finished_variant, quarantine, Decimal(str(return_qty)),
                "return_in",  "return", ret_obj.id if ret_obj else 0,
                ts_code("RET"), actor, f"[{scenario_tag}] Barang return masuk karantina")

    ok(f"Karantina menerima: {getattr(finished_variant, 'sku', finished_variant.id)} × {return_qty}")

    # ── 5b. QC Decision ───────────────────────────────────────────────────
    qc_result = rng.choices(["LULUS", "DISPOSAL"], weights=[70, 30])[0]
    info(f"QC Decision  : {qc_result}")

    if qc_result == "LULUS":
        # Restock ke gudang utama
        add_stock(finished_variant, quarantine, return_qty, "out",
                  f"[{scenario_tag}] QC lulus — keluar karantina")
        add_stock(finished_variant, warehouse,  return_qty, "in",
                  f"[{scenario_tag}] QC lulus — restock ke gudang")
        add_movement(finished_variant, quarantine, Decimal(str(return_qty)),
                    "qc_out",    "qc_clearance", 0, ts_code("QC"), actor,
                    f"[{scenario_tag}] QC lulus, keluar karantina")
        add_movement(finished_variant, warehouse, Decimal(str(return_qty)),
                    "restock_in", "qc_clearance", 0, ts_code("QC"), actor,
                    f"[{scenario_tag}] Restock ke gudang utama")
        ok(f"  ✅ QC LULUS → {getattr(finished_variant, 'sku', finished_variant.id)} × {return_qty} restock ke {warehouse.name}")
        
        # Update return status jika ada field status
        if ret_obj and inspector.has_field(ret_obj.__class__, 'status'):
            try:
                ret_obj.status = 'cleared'
                ret_obj.save(update_fields=['status'])
            except:
                pass
                
    else:
        # Disposal / waste
        add_stock(finished_variant, quarantine, return_qty, "out",
                  f"[{scenario_tag}] QC gagal — disposal/waste")
        add_movement(finished_variant, quarantine, Decimal(str(return_qty)),
                    "disposal", "waste", 0, ts_code("WAS"), actor,
                    f"[{scenario_tag}] QC gagal — barang di-dispose")
        ok(f"  🗑 QC DISPOSAL → {getattr(finished_variant, 'sku', finished_variant.id)} × {return_qty} di-dispose")
        
        if ret_obj and inspector.has_field(ret_obj.__class__, 'status'):
            try:
                ret_obj.status = 'disposed'
                ret_obj.save(update_fields=['status'])
            except:
                pass

    return qc_result, return_qty


# ══════════════════════════════════════════════════════════════════════════════
# SKENARIO TUNGGAL — wrapper semua fase
# ══════════════════════════════════════════════════════════════════════════════

def run_scenario(rng: random.Random, actor, warehouse, production, quarantine,
                 store, scenario_tag="S1", exclude_variant_ids=None, profile=None):
    """
    Jalankan satu skenario lengkap (semua 5 fase).
    Returns dict ringkasan hasil.
    """
    hdr(f"SKENARIO: {scenario_tag}")
    if profile:
        set_ops_clock(profile["date"], rng, profile=profile)
        info(
            f"Tanggal operasional: {profile['date']} | "
            f"demand {profile['demand']} | inflasi {profile['inflation']}"
        )

    # ── Pick data ──────────────────────────────────────────────────────────
    try:
        finished_variant, components = pick_variants(
            rng, n_components=3, exclude_ids=exclude_variant_ids or set()
        )
    except Exception as e:
        err(f"Gagal pick variants: {e}")
        raise
    
    vendor = pick_vendor(rng)
    unit = getattr(finished_variant.product, 'unit', None) if hasattr(finished_variant, 'product') else pick_unit(rng)
    if not unit:
        unit = pick_unit(rng)

    info(f"Finished good : {getattr(finished_variant, 'sku', finished_variant.id)} — {finished_variant.product.name}")
    for i, c in enumerate(components, 1):
        info(f"Komponen {i}    : {getattr(c, 'sku', c.id)} — {c.product.name}")

    results = {}

    # ── Fase 1: Inbound ────────────────────────────────────────────────────
    results["inbound_qty"] = fase_inbound(
        rng, actor, warehouse, components, vendor, scenario_tag
    )

    # ── Fase 2: RnD ───────────────────────────────────────────────────────
    recipe, bom, comp_qty_recipe = fase_rnd(
        rng, actor, warehouse, finished_variant, components, unit, scenario_tag
    )
    results["recipe"] = recipe
    results["bom"]    = bom

    # ── Fase 3: Produksi ──────────────────────────────────────────────────
    prod_order, fg_qty = fase_produksi(
        rng, actor, warehouse, production,
        finished_variant, components,
        bom, comp_qty_recipe, unit, scenario_tag
    )
    results["production_order"] = prod_order
    results["fg_qty"]           = fg_qty

    # ── Fase 4: Transfer ──────────────────────────────────────────────────
    transfer, sent_qty = fase_transfer(
        rng, actor, warehouse, store, finished_variant, fg_qty, scenario_tag
    )
    results["transfer"]  = transfer
    results["sent_qty"]  = sent_qty

    # ── Fase 5: Return ────────────────────────────────────────────────────
    qc_result, return_qty = fase_return(
        rng, actor, store, warehouse, quarantine,
        finished_variant, sent_qty, scenario_tag
    )
    results["qc_result"]   = qc_result
    results["return_qty"]  = return_qty

    # ── Stok akhir ────────────────────────────────────────────────────────
    results["stock_gudang"]    = stock_net(finished_variant, warehouse)
    results["stock_toko"]      = stock_net(finished_variant, store)
    results["stock_karantina"] = stock_net(finished_variant, quarantine)
    results["finished_variant"] = finished_variant
    results["components"]       = components
    results["profile"]          = profile or OPS_CLOCK.get("profile")

    return results


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT: run_full_test()
# ══════════════════════════════════════════════════════════════════════════════

def run_full_test(mode=None, count=None, rollback=None, seed=None, verbose=None,
                  start_year=None, start_date=None, end_date=None):
    """
    Main runner.
    """
    if mode    is not None: CFG["mode"]    = mode
    if count   is not None: CFG["count"]   = count
    if rollback is not None: CFG["rollback"] = rollback
    if seed    is not None: CFG["seed"]    = seed
    if verbose is not None: CFG["verbose"] = verbose
    if start_year is not None: CFG["start_year"] = start_year
    if start_date is not None: CFG["start_date"] = start_date
    if end_date is not None: CFG["end_date"] = end_date

    hdr("LUMRA ERP — FULL OPERATIONAL DATA GENERATOR v2.0")
    start_day, end_day = timeline_bounds()
    _v(f"  Mode      : {CFG['mode']}")
    _v(f"  Count     : {CFG['count']}")
    _v(f"  Periode   : {start_day} s/d {end_day}")
    _v(f"  Rollback  : {CFG['rollback']}")
    _v(f"  Seed      : {CFG['seed']}")
    _v(f"  Waktu     : {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if CFG["rollback"]:
        warn("MODE ROLLBACK AKTIF — semua data akan di-rollback setelah test selesai!")

    rng = random.Random(CFG["seed"])

    # ── Ambil data existing ────────────────────────────────────────────────
    try:
        actor = ensure_actor()
        warehouse, production, quarantine, store = pick_locations()
    except Exception as e:
        err(f"Gagal setup lokasi/actor: {e}")
        traceback.print_exc()
        return

    _v(f"\n  Aktor      : {actor.username}")
    _v(f"  Gudang     : {warehouse.name}")
    _v(f"  Produksi   : {production.name}")
    _v(f"  Karantina  : {quarantine.name}")
    _v(f"  Toko/Cabang: {store.name}\n")

    # ── Tentukan jumlah skenario ───────────────────────────────────────────
    if   CFG["mode"] == "small":    n_scenarios = 1
    elif CFG["mode"] == "parallel": n_scenarios = max(2, CFG["count"])
    elif CFG["mode"] == "batch":    n_scenarios = max(5, CFG["count"])
    else:
        warn(f"Mode '{CFG['mode']}' tidak dikenal, fallback ke 'small'")
        n_scenarios = 1

    all_results  = []
    used_variant_ids = set()
    errors = []

    tx = None
    if CFG["rollback"]:
        tx = transaction.atomic()
        tx.__enter__()

    try:
        for i in range(n_scenarios):
            scenario_tag = f"S{i+1:02d}"
            day = scenario_day(i, n_scenarios, rng)
            profile = business_profile_for(day, rng)
            try:
                res = run_scenario(
                    rng, actor,
                    warehouse, production, quarantine, store,
                    scenario_tag=scenario_tag,
                    exclude_variant_ids=used_variant_ids,
                    profile=profile,
                )
                all_results.append(res)
                # Tandai variant yang sudah dipakai agar tidak duplikat
                used_variant_ids.add(res["finished_variant"].id)
                for c in res["components"]:
                    used_variant_ids.add(c.id)

            except Exception as e:
                err(f"[{scenario_tag}] GAGAL: {e}")
                traceback.print_exc()
                errors.append((scenario_tag, str(e)))
                continue

        # ══════════════════════════════════════════════════════════════════
        # RINGKASAN
        # ══════════════════════════════════════════════════════════════════
        hdr("RINGKASAN HASIL TEST")

        _v(f"  Total skenario    : {n_scenarios}")
        _v(f"  Berhasil          : {len(all_results)}")
        _v(f"  Gagal             : {len(errors)}")
        _v("")

        for i, res in enumerate(all_results, 1):
            fv  = res["finished_variant"]
            profile = res.get("profile") or {}
            _v(f"         Tanggal: {profile.get('date', '-')} | demand={profile.get('demand', '-')} | inflasi={profile.get('inflation', '-')}")
            _v(f"  {C.BOLD}[S{i:02d}]{C.RESET} {getattr(fv, 'sku', fv.id)} — {fv.product.name}")
            if res.get('recipe'):
                _v(f"         Recipe : {res['recipe'].name[:60]}")
            if res.get('bom'):
                _v(f"         BOM    : {res['bom'].code}")
            if res.get('production_order'):
                _v(f"         PO     : {res['production_order'].code}")
            _v(f"         FG qty : {res['fg_qty']}")
            _v(f"         Kirim  : {res['sent_qty']} → {store.name}")
            _v(f"         Return : {res['return_qty']} ({res['qc_result']})")
            _v(f"         Stok akhir — Gudang: {res['stock_gudang']}  "
               f"Toko: {res['stock_toko']}  Karantina: {res['stock_karantina']}")
            _v("")

        if errors:
            warn("Skenario yang gagal:")
            for tag, msg in errors:
                err(f"  [{tag}] {msg}")

        # ── Stock report ringkas ───────────────────────────────────────────
        _v(f"\n  {C.BOLD}STOK AKHIR PER KOMPONEN (skenario terakhir):{C.RESET}")
        if all_results:
            last = all_results[-1]
            for comp in last["components"]:
                gd  = stock_net(comp, warehouse)
                pr  = stock_net(comp, production)
                _v(f"    {getattr(comp, 'sku', comp.id):<20} | Gudang: {gd:>5}  Produksi: {pr:>5}")

        if CFG["rollback"] and tx is not None:
            tx.__exit__(None, None, None)
            warn("\nMODE ROLLBACK: semua data yang dibuat telah di-rollback.")
        else:
            ok(f"\nTest selesai — {len(all_results)} skenario tersimpan di database.")

        _v(f"\n{C.BOLD}{C.GREEN}{'═'*50}{C.RESET}")
        _v(f"{C.BOLD}{C.GREEN}  ✓ FULL OPS FLOW TEST SELESAI{C.RESET}")
        _v(f"{C.BOLD}{C.GREEN}{'═'*50}{C.RESET}\n")

    except Exception as e:
        err(f"Fatal error: {e}")
        traceback.print_exc()
        if CFG["rollback"] and tx is not None:
            tx.__exit__(type(e), e, e.__traceback__)
        raise


# ══════════════════════════════════════════════════════════════════════════════
# DJANGO MANAGEMENT COMMAND
# ══════════════════════════════════════════════════════════════════════════════

from django.core.management.base import BaseCommand  # noqa

class Command(BaseCommand):
    help = "Lumra ERP full operational flow test (inbound→RnD→produksi→transfer→return)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=["small", "parallel", "batch"],
            default="parallel",
            help="small=1 skenario | parallel=N paralel | batch=N besar",
        )
        parser.add_argument("--count",    type=int, default=4,  help="Jumlah skenario (untuk mode parallel/batch)")
        parser.add_argument("--seed",     type=int, default=42, help="Random seed")
        parser.add_argument("--start-year", type=int, default=2019, help="Tahun awal timeline realistis")
        parser.add_argument("--start-date", default=None, help="Tanggal awal YYYY-MM-DD, override start-year")
        parser.add_argument("--end-date", default=None, help="Tanggal akhir YYYY-MM-DD, default hari ini")
        parser.add_argument("--rollback", action="store_true",  help="Rollback semua data setelah test")
        parser.add_argument("--quiet",    action="store_true",  help="Kurangi output")

    def handle(self, *args, **options):
        run_full_test(
            mode     = options["mode"],
            count    = options["count"],
            seed     = options["seed"],
            rollback = options["rollback"],
            verbose  = not options["quiet"],
            start_year = options["start_year"],
            start_date = options["start_date"],
            end_date = options["end_date"],
        )


# ══════════════════════════════════════════════════════════════════════════════
# JALANKAN LANGSUNG (via manage.py shell)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_full_test()
