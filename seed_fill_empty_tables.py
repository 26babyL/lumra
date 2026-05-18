"""
seed_fill_empty_tables.py
=========================
Management command Django untuk mengisi semua tabel yang masih kosong,
menggunakan data yang sudah ada di DB.

Tabel yang diisi (urutan aman):
  1. lumra_config_stock_adjustment_reasons  — master static
  2. lumra_config_product_batches           — dari vendors + variants + locations
  3. lumra_config_orders + orderitems       — dari transfers + customers
  4. lumra_config_payments                  — dari orders
  5. lumra_config_returns + returnitems     — dari orders (~8% rate)
  6. production_waste_records               — dari production_orders
  7. lumra_config_stockopname_session+item  — dari locations + stock
  8. accounting_journal_entries + lines     — double-entry dari orders + payments
  9. accounting_accounts_payable            — dari vendors + journal_entries
 10. accounting_accounts_receivable         — dari customers + journal_entries
 11. accounting_payment_vouchers + alloc    — dari ap + accounts

Cara pakai:
  # Dari root Django project (tempat manage.py berada):
  python manage.py fill_empty_tables --dry-run
  python manage.py fill_empty_tables --execute
  python manage.py fill_empty_tables --execute --section orders
  python manage.py fill_empty_tables --execute --section waste
  python manage.py fill_empty_tables --execute --section accounting

  # Section yang tersedia:
  #   adjustment_reasons, product_batches, orders, payments,
  #   returns, waste, stockopname, accounting, ap_ar, vouchers, all

Letakkan file ini di:
  <project_root>/<any_app>/management/commands/fill_empty_tables.py
  
  Atau jalankan langsung sebagai standalone:
  python seed_fill_empty_tables.py --execute
  (akan auto-setup Django jika DJANGO_SETTINGS_MODULE di-set)
"""

import os
import sys
import random
import time as time_mod
from decimal import Decimal
from datetime import date, datetime, timedelta
from collections import defaultdict

# ── UTF-8 safe output ─────────────────────────────────────────────────────────
for _sn in ("stdout", "stderr"):
    _s = getattr(sys, _sn, None)
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# ── Django setup (jika dijalankan standalone) ─────────────────────────────────
if "django" not in sys.modules:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
    import django
    django.setup()

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.utils import timezone

User = get_user_model()

# ═══════════════════════════════════════════════════════════════════════════════
# MODEL RESOLVER — cari model by app + beberapa kemungkinan nama
# ═══════════════════════════════════════════════════════════════════════════════

def _resolve(candidates: list):
    """
    Coba beberapa (app_label, model_name) sampai ketemu.
    Django menyimpan nama model dalam lowercase tanpa underscore.
    """
    for app, name in candidates:
        try:
            m = apps.get_model(app, name)
            if m is not None:
                return m
        except Exception:
            pass
    return None


def _fields(model) -> set:
    if model is None:
        return set()
    return {f.name for f in model._meta.get_fields()}


def _safe_kw(model, kwargs: dict) -> dict:
    """Hanya sertakan field yang benar-benar ada di model."""
    valid = _fields(model)
    return {k: v for k, v in kwargs.items() if k in valid}


# ── Model registry ────────────────────────────────────────────────────────────
M = {
    # lumra_config
    "Location":    _resolve([("lumra_config", "Locations"), ("lumra_config", "Location")]),
    "Variant":     _resolve([("lumra_config", "Productvariants"), ("lumra_config", "ProductVariant")]),
    "Product":     _resolve([("lumra_config", "Products"), ("lumra_config", "Product")]),
    "Customer":    _resolve([("lumra_config", "Customers"), ("lumra_config", "Customer")]),
    "Vendor":      _resolve([("lumra_config", "Vendors"), ("lumra_config", "Vendor")]),
    "Unit":        _resolve([("lumra_config", "Units"), ("lumra_config", "Unit")]),
    "Stock":       _resolve([("lumra_config", "Stock"), ("lumra_config", "LumraConfigStock")]),
    "StockMove":   _resolve([("lumra_config", "Stockmovement"), ("lumra_config", "StockMovement")]),
    "Zone":        _resolve([("lumra_config", "Warehousezones"), ("lumra_config", "WarehouseZone")]),
    "AdjustReason":_resolve([("lumra_config", "Stockadjustmentreasons"),
                              ("lumra_config", "StockAdjustmentReason")]),
    "ProductBatch":_resolve([("lumra_config", "Productbatches"),
                              ("lumra_config", "ProductBatch"),
                              ("lumra_config", "LumraConfigProductBatches")]),
    "Transfer":    _resolve([("lumra_config", "Transfers"), ("lumra_config", "Transfer")]),
    "TransferItem":_resolve([("lumra_config", "Transferitem"), ("lumra_config", "TransferItem")]),
    "Requisition": _resolve([("lumra_config", "Requisitions"), ("lumra_config", "Requisition")]),
    "ReqItem":     _resolve([("lumra_config", "Requisitionitem"), ("lumra_config", "RequisitionItem")]),
    "Order":       _resolve([("lumra_config", "Orders"), ("lumra_config", "Order")]),
    "OrderItem":   _resolve([("lumra_config", "Orderitems"), ("lumra_config", "OrderItem")]),
    "Payment":     _resolve([("lumra_config", "Payments"), ("lumra_config", "Payment")]),
    "Return":      _resolve([("lumra_config", "Returns"), ("lumra_config", "Return")]),
    "ReturnItem":  _resolve([("lumra_config", "Returnitems"), ("lumra_config", "ReturnItem")]),
    "SalesTarget": _resolve([("lumra_config", "Salestargets"), ("lumra_config", "SalesTarget")]),
    "OpnameSession":_resolve([("lumra_config", "Stockopnamesession"),
                               ("lumra_config", "StockOpnameSession")]),
    "OpnameItem":  _resolve([("lumra_config", "Stockopnameitem"),
                              ("lumra_config", "StockOpnameItem")]),
    # production
    "ProdOrder":   _resolve([("production", "Orders"), ("production", "Productionorders"),
                              ("lumra_config", "Productionorders")]),
    "MatCons":     _resolve([("production", "Materialconsumptions"),
                              ("production", "Productionmaterialconsumptions")]),
    "FGR":         _resolve([("production", "Finishedgoodsreceipts"),
                              ("production", "Productionfinishedgoodsreceipts")]),
    "Waste":       _resolve([("production", "Wasterecords"),
                              ("production", "Productionwasterecords")]),
    "BOM":         _resolve([("production", "Billofmaterials"),
                              ("production", "Productionbillofmaterials")]),
    "BOMItem":     _resolve([("production", "Bomitems"),
                              ("production", "Productionbomitems")]),
    # accounting
    "Account":     _resolve([("accounting", "Accounts"), ("accounting", "Accountingaccounts"),
                              ("lumra_config", "Accountingaccounts")]),
    "Journal":     _resolve([("accounting", "Journalentries"),
                              ("accounting", "Accountingjournalentries"),
                              ("lumra_config", "Accountingjournalentries")]),
    "JournalLine": _resolve([("accounting", "Journalentrylines"),
                              ("accounting", "Accountingjournalentrylines"),
                              ("lumra_config", "Accountingjournalentrylines")]),
    "AP":          _resolve([("accounting", "Accountspayable"),
                              ("accounting", "Accountingaccountspayable"),
                              ("lumra_config", "Accountingaccountspayable")]),
    "AR":          _resolve([("accounting", "Accountsreceivable"),
                              ("accounting", "Accountingaccountsreceivable"),
                              ("lumra_config", "Accountingaccountsreceivable")]),
    "PayVoucher":  _resolve([("accounting", "Paymentvouchers"),
                              ("accounting", "Accountingpaymentvouchers"),
                              ("lumra_config", "Accountingpaymentvouchers")]),
    "VoucherAlloc":_resolve([("accounting", "Paymentvoucherallocations"),
                              ("accounting", "Accountingpaymentvoucherallocations"),
                              ("lumra_config", "Accountingpaymentvoucherallocations")]),
}

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CACHE
# ═══════════════════════════════════════════════════════════════════════════════

CACHE = {}
RNG = random.Random(42)


def warm_cache(verbose=True):
    """Load semua lookup data ke memory sekali."""
    t0 = time_mod.time()
    if verbose:
        print("\n  Warming cache...", end="", flush=True)

    # Users
    CACHE["users"] = list(User.objects.filter(is_active=True).order_by("id")[:200])
    CACHE["admin"] = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )

    # Locations
    all_locs = list(M["Location"].objects.all().order_by("id"))
    CACHE["locations"] = all_locs
    CACHE["warehouses"] = [l for l in all_locs
                           if "warehouse" in getattr(l, "location_type", "").lower()
                           or "gudang" in getattr(l, "name", "").lower()]
    CACHE["stores"] = [l for l in all_locs
                       if "store" in getattr(l, "location_type", "").lower()
                       or "outlet" in getattr(l, "location_type", "").lower()
                       or "toko" in getattr(l, "name", "").lower()]
    if not CACHE["warehouses"]:
        CACHE["warehouses"] = all_locs[:3]
    if not CACHE["stores"]:
        CACHE["stores"] = all_locs[3:]

    # Vendors
    CACHE["vendors"] = list(M["Vendor"].objects.all().order_by("id"))

    # Variants — sample 2000 agar memori wajar
    total_v = M["Variant"].objects.count()
    step = max(1, total_v // 2000)
    ids = list(M["Variant"].objects.values_list("id", flat=True).order_by("id")[::step][:2000])
    CACHE["variants"] = list(
        M["Variant"].objects.filter(id__in=ids).select_related("product")
    )

    # Customers — sample 5000
    CACHE["customers"] = list(M["Customer"].objects.filter(is_active=True).order_by("id")[:5000])

    # Accounting accounts
    CACHE["accounts"] = {}
    if M["Account"]:
        accs = list(M["Account"].objects.filter(
            allow_posting=True, is_active=True
        ).order_by("code"))
        for a in accs:
            nm = (a.name or "").lower()
            cd = (a.code or "").lower()
            if not CACHE["accounts"].get("cash") and (
                "kas" in nm or "cash" in nm or "1-1001" in cd or "1-1010" in cd
            ):
                CACHE["accounts"]["cash"] = a
            if not CACHE["accounts"].get("sales") and (
                "pendapatan penjualan" in nm or "4-1001" in cd or "4-1002" in cd
            ):
                CACHE["accounts"]["sales"] = a
            if not CACHE["accounts"].get("hpp") and (
                "hpp" in nm or "harga pokok" in nm or "5-1" in cd
            ):
                CACHE["accounts"]["hpp"] = a
            if not CACHE["accounts"].get("inventory") and (
                "persediaan" in nm or "1-12" in cd
            ):
                CACHE["accounts"]["inventory"] = a
            if not CACHE["accounts"].get("ap") and (
                "hutang dagang" in nm or "2-1001" in cd
            ):
                CACHE["accounts"]["ap"] = a
            if not CACHE["accounts"].get("ar") and (
                "piutang" in nm or "1-1100" in cd
            ):
                CACHE["accounts"]["ar"] = a
            if not CACHE["accounts"].get("waste") and (
                "waste" in nm or "susut" in nm or "5-4003" in cd
            ):
                CACHE["accounts"]["waste"] = a

        # Fallback: pakai akun pertama
        fallback = accs[0] if accs else None
        for k in ("cash", "sales", "hpp", "inventory", "ap", "ar", "waste"):
            if not CACHE["accounts"].get(k):
                CACHE["accounts"][k] = fallback

    elapsed = time_mod.time() - t0
    if verbose:
        print(f" OK ({elapsed:.1f}s)")
        print(f"    users={len(CACHE['users'])}  "
              f"locations={len(CACHE['locations'])}  "
              f"variants={len(CACHE['variants'])}  "
              f"customers={len(CACHE['customers'])}  "
              f"vendors={len(CACHE['vendors'])}")
        accs_found = {k: (v.code if v else None) for k, v in CACHE["accounts"].items()}
        print(f"    accounts={accs_found}")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _now():
    return timezone.now()


def _aware(dt_or_date, hour=8, minute=0):
    """Pastikan datetime aware, atau buat dari date."""
    if isinstance(dt_or_date, date) and not isinstance(dt_or_date, datetime):
        dt_or_date = datetime(dt_or_date.year, dt_or_date.month, dt_or_date.day,
                              hour, minute)
    if timezone.is_naive(dt_or_date):
        return timezone.make_aware(dt_or_date, timezone.get_current_timezone())
    return dt_or_date


def _pick(lst):
    return RNG.choice(lst) if lst else None


def _seq(prefix: str, n: int) -> str:
    yr = timezone.now().year
    return f"{prefix}-{yr}-{n:06d}"


def _bulk_save(model, objects, batch=300, ignore_conflicts=True):
    """Bulk create dengan batching dan error handling."""
    if not objects or not model:
        return 0
    total = 0
    for i in range(0, len(objects), batch):
        chunk = objects[i:i + batch]
        try:
            with transaction.atomic():
                created = model.objects.bulk_create(
                    chunk, ignore_conflicts=ignore_conflicts, batch_size=batch
                )
            total += len(created)
        except Exception as e:
            # Fallback satu per satu
            for obj in chunk:
                try:
                    obj.save()
                    total += 1
                except Exception:
                    pass
    return total


def _progress(label, done, total, t0):
    pct = done / max(1, total) * 100
    elapsed = time_mod.time() - t0
    eta = (elapsed / max(1, done)) * (total - done) if done < total else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"\r    [{bar}] {pct:5.1f}%  {done:,}/{total:,}  ETA {eta:.0f}s   ",
          end="", flush=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — stock_adjustment_reasons (static master)
# ═══════════════════════════════════════════════════════════════════════════════

ADJUSTMENT_REASONS = [
    ("ADJ-001", "Stock Opname Correction",    "Koreksi hasil hitung fisik stock opname"),
    ("ADJ-002", "Damaged Goods",              "Barang rusak tidak bisa dijual"),
    ("ADJ-003", "Expired Product",            "Produk kadaluarsa, dikeluarkan dari stok"),
    ("ADJ-004", "Found Variance",             "Selisih lebih dari hitungan fisik vs sistem"),
    ("ADJ-005", "Lost / Missing",             "Barang hilang tidak diketahui penyebabnya"),
    ("ADJ-006", "Return to Vendor",           "Dikembalikan ke vendor karena cacat produksi"),
    ("ADJ-007", "Promotional Giveaway",       "Diberikan sebagai promosi atau tester"),
    ("ADJ-008", "Internal Consumption",       "Dikonsumsi untuk operasional internal outpost"),
    ("ADJ-009", "Quality Hold Release",       "Dilepas dari karantina setelah QC lulus"),
    ("ADJ-010", "System Error Correction",    "Koreksi kesalahan input sistem"),
    ("ADJ-011", "Opening Balance Adjustment", "Penyesuaian saldo awal saat onboarding"),
    ("ADJ-012", "Transfer Discrepancy",       "Selisih kuantitas saat transfer antar lokasi"),
]


def fill_adjustment_reasons(dry_run=False):
    model = M["AdjustReason"]
    if not model:
        print("  ⚠  Model StockAdjustmentReason tidak ditemukan — skip")
        return 0

    fields = _fields(model)
    rows = []
    for code, name, desc in ADJUSTMENT_REASONS:
        kw = {}
        if "code" in fields:
            kw["code"] = code
        if "name" in fields:
            kw["name"] = name
        if "description" in fields:
            kw["description"] = desc
        if "is_active" in fields:
            kw["is_active"] = True
        rows.append(model(**kw))

    print(f"    {len(rows)} adjustment reasons")
    if dry_run:
        return len(rows)
    return _bulk_save(model, rows, ignore_conflicts=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — product_batches
# ═══════════════════════════════════════════════════════════════════════════════

def fill_product_batches(dry_run=False, limit=5000):
    """
    Buat batch untuk variants yang punya has_expiry=True atau track_batch=True.
    Setiap variant mendapat 1-3 batch per lokasi warehouse.
    """
    model = M["ProductBatch"]
    if not model:
        print("  ⚠  Model ProductBatch tidak ditemukan — skip")
        return 0

    # Ambil variants yang perlu batch tracking
    variants_q = M["Variant"].objects.select_related("product").filter(
        product__is_active=True
    )
    try:
        variants_q = variants_q.filter(product__has_expiry=True)
    except Exception:
        pass
    variants_list = list(variants_q.order_by("id")[:limit])

    if not variants_list:
        # Fallback: ambil semua
        variants_list = list(M["Variant"].objects.select_related("product").order_by("id")[:limit])

    warehouses = CACHE["warehouses"]
    vendors = CACHE["vendors"]
    admin = CACHE["admin"]

    if not warehouses or not vendors or not variants_list:
        print("  ⚠  Data kurang untuk fill product_batches — skip")
        return 0

    fields = _fields(model)
    rows = []
    today = timezone.now().date()
    counter = 1

    for variant in variants_list:
        # 1-2 batch per variant
        n_batch = RNG.randint(1, 2)
        for _ in range(n_batch):
            loc = _pick(warehouses)
            vendor = _pick(vendors)
            mfg_days_ago = RNG.randint(30, 270)
            mfg = today - timedelta(days=mfg_days_ago)
            shelf_life = RNG.choice([90, 180, 270, 365])
            exp = mfg + timedelta(days=shelf_life)
            qty_in = Decimal(str(RNG.randint(24, 240)))

            kw = {}
            if "product_id" in fields:
                kw["product_id"] = variant.id
            elif "product" in fields:
                kw["product"] = variant

            if "location_id" in fields:
                kw["location_id"] = loc.id
            elif "location" in fields:
                kw["location"] = loc

            if "supplier_id" in fields:
                kw["supplier_id"] = vendor.id
            elif "supplier" in fields:
                kw["supplier"] = vendor

            if "batch_number" in fields:
                kw["batch_number"] = f"BTH-{today.year}-{counter:06d}"
            if "supplier_batch_number" in fields:
                kw["supplier_batch_number"] = f"SUP-{RNG.randint(10000, 99999)}"
            if "manufacturing_date" in fields:
                kw["manufacturing_date"] = mfg
            if "expiry_date" in fields:
                kw["expiry_date"] = exp
            if "quantity_in" in fields:
                kw["quantity_in"] = qty_in
            if "quantity_available" in fields:
                kw["quantity_available"] = qty_in * Decimal(str(RNG.uniform(0.6, 0.98)))
            if "notes" in fields:
                kw["notes"] = "Generated batch"
            if "created_at" in fields:
                kw["created_at"] = _aware(mfg, 8)
            if "updated_at" in fields:
                kw["updated_at"] = _now()

            rows.append(model(**kw))
            counter += 1

    print(f"    {len(rows)} product batches (dari {len(variants_list)} variants × max 2 batch × {len(warehouses)} gudang)")
    if dry_run:
        return len(rows)
    return _bulk_save(model, rows, batch=500)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3+4+5 — orders, orderitems, payments, returns
# ═══════════════════════════════════════════════════════════════════════════════

def fill_orders_payments_returns(dry_run=False):
    """
    Strategi:
      - Ambil semua Transfer yang status=received dan destination=store
      - Setiap transfer → 1-4 orders (simulasi penjualan dari stok yang diterima toko)
      - Setiap order → payment
      - ~8% order → return
    
    KRITIS: FK harus di-set via _id (integer), BUKAN object,
    karena object belum punya PK sampai .save() dipanggil.
    Untuk objects yang di-bulk_create, ambil ID dari returned list.
    """
    if not all([M["Order"], M["OrderItem"], M["Payment"]]):
        print("  ⚠  Model Order/OrderItem/Payment tidak ditemukan — skip")
        return {}

    # ── Ambil transfers ke stores ─────────────────────────────────────────
    store_ids = [l.id for l in CACHE["stores"]]
    transfers = list(
        M["Transfer"].objects
        .filter(status="received")
        .select_related("destination_location", "created_by")
        .order_by("created_at")
    )
    if not transfers:
        print("  ⚠  Tidak ada transfer status=received — skip orders")
        return {}

    print(f"    Source: {len(transfers):,} transfers")

    # ── Pre-load transfer items (batch agar tidak N+1) ────────────────────
    transfer_ids = [t.id for t in transfers]
    # Ambil per chunk 1000
    trf_items_map = defaultdict(list)
    chunk_size = 1000
    for i in range(0, len(transfer_ids), chunk_size):
        chunk = transfer_ids[i:i + chunk_size]
        items = M["TransferItem"].objects.filter(
            transfer_id__in=chunk
        ).select_related("variant")
        for ti in items:
            trf_items_map[ti.transfer_id].append(ti)

    customers = CACHE["customers"]
    users = CACHE["users"]
    admin = CACHE["admin"]

    payment_methods = ["cash", "transfer", "qris", "card", "debit"]
    dining_options  = ["dine_in", "takeaway", "delivery"]
    order_fields    = _fields(M["Order"])
    oi_fields       = _fields(M["OrderItem"])
    pay_fields      = _fields(M["Payment"])

    # ── Generate ──────────────────────────────────────────────────────────
    # Kita simpan sebagai list of tuples (order_kw, [oi_kw_list], pay_kw)
    # supaya bisa di-bulk dengan FK linking yang benar
    order_dicts   = []  # list of dict kwargs untuk Order
    oi_groups     = []  # list of list of dict kwargs (index aligned dengan order_dicts)
    pay_dicts     = []  # list of dict kwargs (index aligned)

    order_counter = 1
    pay_counter   = 1

    t0 = time_mod.time()
    for idx, trf in enumerate(transfers):
        if idx % 5000 == 0:
            _progress("orders", idx, len(transfers), t0)

        ti_list = trf_items_map.get(trf.id, [])
        if not ti_list:
            continue

        # Filter store
        dest = trf.destination_location
        if dest and store_ids and dest.id not in store_ids:
            # Tetap proses jika store_ids kosong (fallback)
            if store_ids:
                continue

        # Tanggal order = 1-72 jam setelah transfer received
        trf_dt = trf.received_at or trf.created_at or _now()
        trf_dt_aware = _aware(trf_dt) if trf_dt else _now()
        num_orders = RNG.randint(1, 3)

        for k in range(num_orders):
            order_dt = trf_dt_aware + timedelta(hours=RNG.randint(2, 72), minutes=k * 15)
            customer = _pick(customers)
            cashier  = _pick(users) or admin
            method   = _pick(payment_methods)

            # Build order items
            oi_list = []
            total_amount = Decimal("0")

            for ti in ti_list:
                if not hasattr(ti, "variant") or ti.variant is None:
                    continue
                # Jual sebagian dari qty yang diterima
                avail = int(getattr(ti, "quantity_received", 0) or 0)
                if avail <= 0:
                    continue
                sold = max(1, int(avail * RNG.uniform(0.05, 0.4) / num_orders))
                price = getattr(ti.variant, "price_sell", None) or (
                    (getattr(ti.variant, "price_buy", Decimal("5000")) or Decimal("5000"))
                    * Decimal("1.35")
                )
                price = Decimal(str(price)).quantize(Decimal("0.01"))
                subtotal = price * sold
                total_amount += subtotal

                oi_kw = {}
                if "variant_id" in oi_fields:
                    oi_kw["variant_id"] = ti.variant.id
                elif "variant" in oi_fields:
                    oi_kw["variant"] = ti.variant
                if "quantity" in oi_fields:
                    oi_kw["quantity"] = sold
                if "price" in oi_fields:
                    oi_kw["price"] = price
                if "cost_price" in oi_fields:
                    cp = getattr(ti.variant, "price_buy", None) or price * Decimal("0.65")
                    oi_kw["cost_price"] = Decimal(str(cp)).quantize(Decimal("0.01"))
                if "discount_amount" in oi_fields:
                    oi_kw["discount_amount"] = Decimal("0")
                if "discount_percent" in oi_fields:
                    oi_kw["discount_percent"] = Decimal("0")
                if "notes" in oi_fields:
                    oi_kw["notes"] = ""
                oi_list.append(oi_kw)

            if not oi_list:
                continue

            # Order kwargs (tanpa id)
            ord_kw = {}
            if "customer_name" in order_fields:
                ord_kw["customer_name"] = getattr(customer, "name", "Walk-in")[:100]
            if "status" in order_fields:
                ord_kw["status"] = "completed"
            if "customer_id" in order_fields:
                ord_kw["customer_id"] = customer.id if customer else None
            elif "customer" in order_fields:
                ord_kw["customer"] = customer
            if "cashier_id" in order_fields:
                ord_kw["cashier_id"] = cashier.id if cashier else None
            elif "cashier" in order_fields:
                ord_kw["cashier"] = cashier
            if "change_amount" in order_fields:
                ord_kw["change_amount"] = Decimal("0")
            if "dining_option" in order_fields:
                ord_kw["dining_option"] = _pick(dining_options)
            if "order_type" in order_fields:
                ord_kw["order_type"] = "pos"
            if "paid_amount" in order_fields:
                ord_kw["paid_amount"] = total_amount
            if "payment_method" in order_fields:
                ord_kw["payment_method"] = method
            if "payment_status" in order_fields:
                ord_kw["payment_status"] = "paid"
            if "shift_id" in order_fields:
                ord_kw["shift_id"] = f"SHF-{order_dt.strftime('%Y%m%d')}-{order_dt.hour // 8 + 1}"
            if "table_number" in order_fields:
                ord_kw["table_number"] = f"T-{RNG.randint(1, 30)}"
            if "created_at" in order_fields:
                ord_kw["created_at"] = order_dt

            # Payment kwargs
            pay_kw = {}
            if "payment_number" in pay_fields:
                pay_kw["payment_number"] = _seq("PAY", pay_counter)
                pay_counter += 1
            if "payment_date" in pay_fields:
                pay_kw["payment_date"] = order_dt.date()
            if "amount" in pay_fields:
                pay_kw["amount"] = total_amount
            if "payment_method" in pay_fields:
                pay_kw["payment_method"] = method
            if "status" in pay_fields:
                pay_kw["status"] = "completed"
            if "reference_number" in pay_fields:
                ref_map = {"cash": "", "qris": f"QRIS-{RNG.randint(100000,999999)}",
                           "transfer": f"TF-{RNG.randint(100000,999999)}",
                           "card": f"CARD-{RNG.randint(100000,999999)}",
                           "debit": f"DB-{RNG.randint(100000,999999)}"}
                pay_kw["reference_number"] = ref_map.get(method, "")
            if "notes" in pay_fields:
                pay_kw["notes"] = ""
            if "received_by_id" in pay_fields:
                pay_kw["received_by_id"] = cashier.id if cashier else None
            elif "received_by" in pay_fields:
                pay_kw["received_by"] = cashier
            if "created_at" in pay_fields:
                pay_kw["created_at"] = order_dt
            if "updated_at" in pay_fields:
                pay_kw["updated_at"] = order_dt

            order_dicts.append(ord_kw)
            oi_groups.append(oi_list)
            pay_dicts.append(pay_kw)
            order_counter += 1

    print()
    print(f"    Generated: {len(order_dicts):,} orders, "
          f"{sum(len(g) for g in oi_groups):,} order items")

    if dry_run:
        return {"orders": len(order_dicts), "items": sum(len(g) for g in oi_groups),
                "payments": len(pay_dicts)}

    # ── SAVE — urutan kritis: Order → (OrderItem, Payment) ────────────────
    print("    Saving orders...", end="", flush=True)
    t0 = time_mod.time()

    BATCH = 500
    saved_count = {"orders": 0, "items": 0, "payments": 0,
                   "returns": 0, "return_items": 0}

    ret_fields  = _fields(M["Return"]) if M["Return"] else set()
    reti_fields = _fields(M["ReturnItem"]) if M["ReturnItem"] else set()

    for batch_start in range(0, len(order_dicts), BATCH):
        batch_ord   = order_dicts[batch_start:batch_start + BATCH]
        batch_oi_g  = oi_groups[batch_start:batch_start + BATCH]
        batch_pay   = pay_dicts[batch_start:batch_start + BATCH]

        try:
            with transaction.atomic():
                # 1. Buat Order objects
                order_objs = [M["Order"](**kw) for kw in batch_ord]
                saved_orders = M["Order"].objects.bulk_create(
                    order_objs, batch_size=BATCH
                )
                saved_count["orders"] += len(saved_orders)

                # 2. OrderItems — pakai _id dari saved_orders
                all_oi_objs = []
                for i, saved_ord in enumerate(saved_orders):
                    for oi_kw in batch_oi_g[i]:
                        oi_kw["order_id"] = saved_ord.id
                        all_oi_objs.append(M["OrderItem"](**oi_kw))
                if all_oi_objs:
                    M["OrderItem"].objects.bulk_create(all_oi_objs, batch_size=BATCH)
                    saved_count["items"] += len(all_oi_objs)

                # 3. Payments — pakai _id dari saved_orders
                pay_objs = []
                for i, saved_ord in enumerate(saved_orders):
                    if i < len(batch_pay):
                        pk = batch_pay[i]
                        if "order_id" in pay_fields:
                            pk["order_id"] = saved_ord.id
                        elif "order" in pay_fields:
                            pk["order"] = saved_ord
                        pay_objs.append(M["Payment"](**pk))
                if pay_objs:
                    M["Payment"].objects.bulk_create(pay_objs, batch_size=BATCH)
                    saved_count["payments"] += len(pay_objs)

                # 4. Returns (~8% dari orders)
                if M["Return"] and M["ReturnItem"]:
                    ret_objs  = []
                    reti_objs = []
                    ret_ctr   = M["Return"].objects.count() + 1

                    for i, saved_ord in enumerate(saved_orders):
                        if RNG.random() > 0.08:
                            continue
                        customer_id = batch_ord[i].get("customer_id")
                        ret_kw = {}
                        if "order_id" in ret_fields:
                            ret_kw["order_id"] = saved_ord.id
                        elif "order" in ret_fields:
                            ret_kw["order"] = saved_ord
                        if "customer_id" in ret_fields and customer_id:
                            ret_kw["customer_id"] = customer_id
                        if "retur_number" in ret_fields:
                            ret_kw["retur_number"] = _seq("RET", ret_ctr)
                        if "retur_date" in ret_fields:
                            ret_kw["retur_date"] = batch_ord[i].get(
                                "created_at", _now()
                            ).date() + timedelta(days=RNG.randint(1, 7))
                        if "total_amount" in ret_fields:
                            # 20-50% dari total order
                            ord_total = batch_ord[i].get("paid_amount", Decimal("10000"))
                            ret_kw["total_amount"] = (
                                ord_total * Decimal(str(RNG.uniform(0.2, 0.5)))
                            ).quantize(Decimal("0.01"))
                        if "status" in ret_fields:
                            ret_kw["status"] = RNG.choice(["approved", "pending"])
                        if "reason" in ret_fields:
                            ret_kw["reason"] = RNG.choice([
                                "Produk rusak saat sampai",
                                "Salah item dikirim",
                                "Kualitas tidak sesuai",
                                "Customer berubah pikiran",
                            ])
                        if "notes" in ret_fields:
                            ret_kw["notes"] = ""
                        if "created_by_id" in ret_fields and CACHE["admin"]:
                            ret_kw["created_by_id"] = CACHE["admin"].id
                        if "created_at" in ret_fields:
                            ret_kw["created_at"] = _now()
                        if "updated_at" in ret_fields:
                            ret_kw["updated_at"] = _now()

                        ret_objs.append(M["Return"](**ret_kw))
                        ret_ctr += 1

                    if ret_objs:
                        saved_rets = M["Return"].objects.bulk_create(
                            ret_objs, batch_size=BATCH
                        )
                        saved_count["returns"] += len(saved_rets)

                        # ReturnItems — pakai first item dari order items
                        for j, saved_ret in enumerate(saved_rets):
                            oi_group_idx = [
                                ii for ii, saved_ord in enumerate(saved_orders)
                                if RNG.random() < 0.08  # approximate re-pick
                            ]
                            # Ambil 1 item dari batch_oi_g acak
                            src_group = batch_oi_g[RNG.randint(0, len(batch_oi_g) - 1)]
                            if not src_group:
                                continue
                            src_oi = src_group[0]
                            ret_qty = max(1, int(src_oi.get("quantity", 1) * RNG.uniform(0.3, 1.0)))
                            reti_kw = {}
                            if "retur_header_id" in reti_fields:
                                reti_kw["retur_header_id"] = saved_ret.id
                            elif "retur_header" in reti_fields:
                                reti_kw["retur_header"] = saved_ret
                            if "product_id" in reti_fields:
                                reti_kw["product_id"] = src_oi.get("variant_id")
                            elif "product" in reti_fields:
                                pass  # skip, butuh object
                            if "quantity" in reti_fields:
                                reti_kw["quantity"] = Decimal(str(ret_qty))
                            if "unit_price" in reti_fields:
                                reti_kw["unit_price"] = src_oi.get("price", Decimal("5000"))
                            if "total_price" in reti_fields:
                                reti_kw["total_price"] = (
                                    Decimal(str(ret_qty)) *
                                    src_oi.get("price", Decimal("5000"))
                                ).quantize(Decimal("0.01"))
                            if "reason" in reti_fields:
                                reti_kw["reason"] = RNG.choice(
                                    ["damaged", "wrong_item", "quality", "other"]
                                )
                            if "notes" in reti_fields:
                                reti_kw["notes"] = ""
                            if "created_at" in reti_fields:
                                reti_kw["created_at"] = _now()
                            reti_objs.append(M["ReturnItem"](**reti_kw))

                        if reti_objs:
                            M["ReturnItem"].objects.bulk_create(reti_objs, batch_size=BATCH)
                            saved_count["return_items"] += len(reti_objs)

        except Exception as e:
            print(f"\n    ⚠  Batch {batch_start}-{batch_start+BATCH} error: {e}")
            # Lanjut ke batch berikutnya

        if batch_start % (BATCH * 10) == 0:
            _progress("orders", batch_start, len(order_dicts), t0)

    print(f"\r    ✓ orders={saved_count['orders']:,}  "
          f"items={saved_count['items']:,}  "
          f"payments={saved_count['payments']:,}  "
          f"returns={saved_count['returns']:,}  "
          f"return_items={saved_count['return_items']:,}")
    return saved_count


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — waste_records
# ═══════════════════════════════════════════════════════════════════════════════

def fill_waste_records(dry_run=False):
    """
    Generate waste dari production_material_consumptions.
    ~12% konsumsi menghasilkan waste 1-5% dari qty.
    """
    if not M["Waste"] or not M["MatCons"]:
        print("  ⚠  Model Waste/MatCons tidak ditemukan — skip")
        return 0

    fields = _fields(M["Waste"])
    unit_field = "unit_id" if "unit_id" in fields else ("unit" if "unit" in fields else None)
    comp_field = "component_id" if "component_id" in fields else "component"

    # Ambil sample consumptions
    cons_list = list(
        M["MatCons"].objects.select_related(
            "production_order", "component", "unit"
        ).order_by("id")[:50000]
    )

    if not cons_list:
        print("  ⚠  Tidak ada material_consumptions — skip waste")
        return 0

    rows = []
    waste_types = ["defect", "spillage", "expired", "process_loss", "damage"]

    for cons in cons_list:
        if RNG.random() > 0.12:  # 12% rate
            continue
        po = cons.production_order
        if not po:
            continue

        waste_qty = cons.quantity * Decimal(str(RNG.uniform(0.01, 0.05)))
        waste_qty = max(Decimal("0.01"), waste_qty.quantize(Decimal("0.01")))

        rec_at = getattr(po, "completed_at", None) or getattr(po, "created_at", None) or _now()
        rec_at = _aware(rec_at) + timedelta(hours=RNG.randint(0, 4))

        kw = {}
        if "production_order_id" in fields:
            kw["production_order_id"] = po.id
        elif "production_order" in fields:
            kw["production_order"] = po

        if "component_id" in fields:
            kw["component_id"] = cons.component_id if hasattr(cons, "component_id") else (
                cons.component.id if cons.component else None
            )
        elif "component" in fields:
            kw["component"] = cons.component

        if "waste_type" in fields:
            kw["waste_type"] = _pick(waste_types)
        if "quantity" in fields:
            kw["quantity"] = waste_qty

        if unit_field == "unit_id":
            kw["unit_id"] = cons.unit_id if hasattr(cons, "unit_id") else (
                cons.unit.id if cons.unit else None
            )
        elif unit_field == "unit":
            kw["unit"] = cons.unit

        if "recorded_at" in fields:
            kw["recorded_at"] = rec_at
        if "notes" in fields:
            kw["notes"] = f"Waste dari produksi {getattr(po, 'code', po.id)}"

        rows.append(M["Waste"](**kw))

    print(f"    {len(rows):,} waste records (dari {len(cons_list):,} consumptions @ 12%)")
    if dry_run:
        return len(rows)
    return _bulk_save(M["Waste"], rows, batch=500)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — stockopname_session + item
# ═══════════════════════════════════════════════════════════════════════════════

def fill_stockopname(dry_run=False):
    """
    Buat 1 sesi opname per lokasi (lokasi yang punya stok).
    Setiap sesi berisi semua variant yang punya stok di lokasi itu.
    """
    if not M["OpnameSession"] or not M["OpnameItem"]:
        print("  ⚠  Model OpnameSession/OpnameItem tidak ditemukan — skip")
        return 0

    sess_fields = _fields(M["OpnameSession"])
    item_fields = _fields(M["OpnameItem"])
    admin = CACHE["admin"]

    # Ambil lokasi yang punya stok
    locs_with_stock = list(
        M["Stock"].objects.values_list("location_id", flat=True).distinct()
    )[:20]  # max 20 lokasi untuk tidak overload

    if not locs_with_stock:
        print("  ⚠  Tidak ada stok untuk opname — skip")
        return 0

    today = timezone.now().date()
    total_items = 0
    total_sessions = 0

    for loc_id in locs_with_stock:
        # Ambil stok di lokasi ini
        stocks = list(
            M["Stock"].objects.filter(location_id=loc_id)
            .values("variant_id", "quantity")[:200]  # max 200 item per sesi
        )
        if not stocks:
            continue

        # Buat session
        sess_kw = {}
        if "location_id" in sess_fields:
            sess_kw["location_id"] = loc_id
        elif "location" in sess_fields:
            try:
                sess_kw["location"] = M["Location"].objects.get(id=loc_id)
            except Exception:
                continue
        if "created_by_id" in sess_fields and admin:
            sess_kw["created_by_id"] = admin.id
        elif "created_by" in sess_fields and admin:
            sess_kw["created_by"] = admin
        if "status" in sess_fields:
            sess_kw["status"] = RNG.choice(["approved", "submitted"])
        if "notes" in sess_fields:
            sess_kw["notes"] = f"Stock opname rutin — {today.strftime('%B %Y')}"
        if "created_at" in sess_fields:
            sess_kw["created_at"] = _aware(today - timedelta(days=RNG.randint(1, 30)))
        if "submitted_at" in sess_fields:
            sess_kw["submitted_at"] = _aware(today - timedelta(days=RNG.randint(0, 7)))
        if "approved_at" in sess_fields and sess_kw.get("status") == "approved":
            sess_kw["approved_at"] = _aware(today - timedelta(days=RNG.randint(0, 3)))

        if dry_run:
            total_sessions += 1
            total_items += len(stocks)
            continue

        try:
            session = M["OpnameSession"](**sess_kw)
            session.save()
            total_sessions += 1
        except Exception as e:
            print(f"\n    ⚠  Gagal buat session lokasi {loc_id}: {e}")
            continue

        # Buat items
        item_objs = []
        for stk in stocks:
            sys_qty = stk["quantity"]
            # Hitungan fisik: sedikit berbeda dari sistem (±5%)
            counted = max(0, int(sys_qty * RNG.uniform(0.93, 1.04)))
            item_kw = {}
            if "session_id" in item_fields:
                item_kw["session_id"] = session.id
            elif "session" in item_fields:
                item_kw["session"] = session
            if "variant_id" in item_fields:
                item_kw["variant_id"] = stk["variant_id"]
            elif "variant" in item_fields:
                try:
                    item_kw["variant"] = M["Variant"].objects.get(id=stk["variant_id"])
                except Exception:
                    continue
            if "current_stock" in item_fields:
                item_kw["current_stock"] = sys_qty
            if "counted_qty" in item_fields:
                item_kw["counted_qty"] = counted
            if "notes" in item_fields:
                diff = counted - sys_qty
                item_kw["notes"] = f"Selisih {diff:+d}" if diff != 0 else "Sesuai"
            if "created_at" in item_fields:
                item_kw["created_at"] = sess_kw.get("created_at", _now())
            item_objs.append(M["OpnameItem"](**item_kw))

        saved = _bulk_save(M["OpnameItem"], item_objs, batch=300)
        total_items += saved

    print(f"    {total_sessions} sessions, {total_items:,} opname items")
    return total_items


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — accounting_journal_entries + lines
# ═══════════════════════════════════════════════════════════════════════════════

def fill_journals(dry_run=False):
    """
    Buat journal entries dari orders & payments yang sudah ada.
    Setiap payment → 1 journal (Debit Cash, Credit Sales).
    Sample max 10000 payments agar tidak overload.
    """
    if not M["Journal"] or not M["JournalLine"]:
        print("  ⚠  Model Journal/JournalLine tidak ditemukan — skip")
        return 0

    accs = CACHE["accounts"]
    if not accs.get("cash") or not accs.get("sales"):
        print("  ⚠  Akun cash/sales tidak ditemukan — skip journals")
        return 0

    je_fields   = _fields(M["Journal"])
    line_fields = _fields(M["JournalLine"])
    admin = CACHE["admin"]

    # Ambil payments yang belum punya journal
    payments = list(
        M["Payment"].objects.select_related("order")
        .order_by("created_at")[:10000]
    )

    if not payments:
        print("  ⚠  Tidak ada payments — skip journals")
        return 0

    print(f"    Source: {len(payments):,} payments")

    total_je   = 0
    total_line = 0
    je_ctr     = 1
    BATCH      = 300

    for batch_start in range(0, len(payments), BATCH):
        batch = payments[batch_start:batch_start + BATCH]
        je_objs   = []
        line_pairs = []  # list of (line1_kw, line2_kw)

        for pay in batch:
            amount = pay.amount or Decimal("0")
            if amount <= 0:
                continue

            pay_dt = getattr(pay, "created_at", None) or _now()
            pay_dt = _aware(pay_dt)

            je_kw = {}
            if "number" in je_fields:
                je_kw["number"] = _seq("JE", je_ctr)
            if "date" in je_fields:
                je_kw["date"] = pay_dt.date()
            if "reference" in je_fields:
                je_kw["reference"] = getattr(pay, "payment_number", str(pay.id))
            if "description" in je_fields:
                je_kw["description"] = f"Penjualan — {getattr(pay, 'payment_method', 'cash')}"
            if "status" in je_fields:
                je_kw["status"] = "posted"
            if "source" in je_fields:
                je_kw["source"] = "sale"
            if "created_by_id" in je_fields and admin:
                je_kw["created_by_id"] = admin.id
            elif "created_by" in je_fields and admin:
                je_kw["created_by"] = admin
            if "posted_by_id" in je_fields and admin:
                je_kw["posted_by_id"] = admin.id
            if "posted_at" in je_fields:
                je_kw["posted_at"] = pay_dt
            if "created_at" in je_fields:
                je_kw["created_at"] = pay_dt
            if "updated_at" in je_fields:
                je_kw["updated_at"] = pay_dt

            je_objs.append(je_kw)

            # Debit Cash, Credit Sales
            l1 = {}
            if "account_id" in line_fields:
                l1["account_id"] = accs["cash"].id
            elif "account" in line_fields:
                l1["account"] = accs["cash"]
            if "debit" in line_fields:
                l1["debit"] = amount
            if "credit" in line_fields:
                l1["credit"] = Decimal("0")
            if "description" in line_fields:
                l1["description"] = "Penerimaan kas/transfer"
            if "created_at" in line_fields:
                l1["created_at"] = pay_dt

            l2 = {}
            if "account_id" in line_fields:
                l2["account_id"] = accs["sales"].id
            elif "account" in line_fields:
                l2["account"] = accs["sales"]
            if "debit" in line_fields:
                l2["debit"] = Decimal("0")
            if "credit" in line_fields:
                l2["credit"] = amount
            if "description" in line_fields:
                l2["description"] = "Pendapatan penjualan"
            if "created_at" in line_fields:
                l2["created_at"] = pay_dt

            line_pairs.append((l1, l2))
            je_ctr += 1

        if dry_run:
            total_je   += len(je_objs)
            total_line += len(je_objs) * 2
            continue

        if not je_objs:
            continue

        try:
            with transaction.atomic():
                saved_jes = M["Journal"].objects.bulk_create(
                    [M["Journal"](**kw) for kw in je_objs],
                    batch_size=BATCH
                )
                total_je += len(saved_jes)

                # Link lines ke JE yang baru disave — pakai ID
                all_lines = []
                for i, saved_je in enumerate(saved_jes):
                    if i >= len(line_pairs):
                        break
                    l1_kw, l2_kw = line_pairs[i]
                    if "journal_entry_id" in line_fields:
                        l1_kw["journal_entry_id"] = saved_je.id
                        l2_kw["journal_entry_id"] = saved_je.id
                    elif "journal_entry" in line_fields:
                        l1_kw["journal_entry"] = saved_je
                        l2_kw["journal_entry"] = saved_je
                    all_lines.append(M["JournalLine"](**l1_kw))
                    all_lines.append(M["JournalLine"](**l2_kw))

                if all_lines:
                    M["JournalLine"].objects.bulk_create(all_lines, batch_size=BATCH * 2)
                    total_line += len(all_lines)

        except Exception as e:
            print(f"\n    ⚠  Batch JE error: {e}")

    print(f"    ✓ journal_entries={total_je:,}  journal_lines={total_line:,}")
    return total_je


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9+10 — accounts_payable + accounts_receivable
# ═══════════════════════════════════════════════════════════════════════════════

def fill_ap_ar(dry_run=False):
    """
    AP: dari vendors (1 invoice per vendor dari sample transfer)
    AR: dari customers dengan orders yang belum lunas (simulasi credit)
    """
    ap_count = 0
    ar_count = 0

    # ── AP ────────────────────────────────────────────────────────────────
    if M["AP"]:
        ap_fields = _fields(M["AP"])
        vendors   = CACHE["vendors"]
        je_sample = list(M["Journal"].objects.filter(source="sale").order_by("id")[:len(vendors)])
        admin     = CACHE["admin"]
        today     = timezone.now().date()

        ap_rows = []
        for i, vendor in enumerate(vendors[:50]):
            je = je_sample[i] if i < len(je_sample) else None
            inv_date = today - timedelta(days=RNG.randint(7, 60))
            due_date = inv_date + timedelta(days=RNG.choice([30, 45, 60]))
            total    = Decimal(str(RNG.randint(500000, 20000000)))
            paid     = total * Decimal(str(RNG.choice([0, 0, 0.5, 1.0])))

            status = "paid" if paid >= total else ("partial" if paid > 0 else "unpaid")

            kw = {}
            if "vendor_id" in ap_fields:
                kw["vendor_id"] = vendor.id
            elif "vendor" in ap_fields:
                kw["vendor"] = vendor
            if "invoice_number" in ap_fields:
                kw["invoice_number"] = f"BILL-{today.year}-{i+1:05d}"
            if "invoice_date" in ap_fields:
                kw["invoice_date"] = inv_date
            if "due_date" in ap_fields:
                kw["due_date"] = due_date
            if "total_amount" in ap_fields:
                kw["total_amount"] = total
            if "paid_amount" in ap_fields:
                kw["paid_amount"] = paid
            if "status" in ap_fields:
                kw["status"] = status
            if "memo" in ap_fields:
                kw["memo"] = f"Invoice pembelian dari {vendor.name}"
            if "journal_entry_id" in ap_fields and je:
                kw["journal_entry_id"] = je.id
            elif "journal_entry" in ap_fields and je:
                kw["journal_entry"] = je
            if "created_at" in ap_fields:
                kw["created_at"] = _aware(inv_date)
            if "updated_at" in ap_fields:
                kw["updated_at"] = _now()

            ap_rows.append(M["AP"](**kw))

        if not dry_run:
            ap_count = _bulk_save(M["AP"], ap_rows)
        else:
            ap_count = len(ap_rows)
        print(f"    accounts_payable: {ap_count}")

    # ── AR ────────────────────────────────────────────────────────────────
    if M["AR"]:
        ar_fields  = _fields(M["AR"])
        customers  = CACHE["customers"]
        je_sample2 = list(M["Journal"].objects.filter(source="sale").order_by("id")[:200])
        today      = timezone.now().date()

        ar_rows = []
        for i, cust in enumerate(RNG.sample(customers, min(200, len(customers)))):
            je = je_sample2[i] if i < len(je_sample2) else None
            inv_date = today - timedelta(days=RNG.randint(1, 90))
            due_date = inv_date + timedelta(days=30)
            total    = Decimal(str(RNG.randint(100000, 5000000)))
            paid     = total * Decimal(str(RNG.choice([0, 0, 0.5, 1.0])))
            status   = "paid" if paid >= total else ("partial" if paid > 0 else "unpaid")

            kw = {}
            if "customer_id" in ar_fields:
                kw["customer_id"] = cust.id
            elif "customer" in ar_fields:
                kw["customer"] = cust
            if "invoice_number" in ar_fields:
                kw["invoice_number"] = f"INV-{today.year}-{i+1:05d}"
            if "invoice_date" in ar_fields:
                kw["invoice_date"] = inv_date
            if "due_date" in ar_fields:
                kw["due_date"] = due_date
            if "total_amount" in ar_fields:
                kw["total_amount"] = total
            if "paid_amount" in ar_fields:
                kw["paid_amount"] = paid
            if "status" in ar_fields:
                kw["status"] = status
            if "memo" in ar_fields:
                kw["memo"] = f"Invoice penjualan kredit ke {cust.name}"
            if "journal_entry_id" in ar_fields and je:
                kw["journal_entry_id"] = je.id
            elif "journal_entry" in ar_fields and je:
                kw["journal_entry"] = je
            if "created_at" in ar_fields:
                kw["created_at"] = _aware(inv_date)
            if "updated_at" in ar_fields:
                kw["updated_at"] = _now()

            ar_rows.append(M["AR"](**kw))

        if not dry_run:
            ar_count = _bulk_save(M["AR"], ar_rows)
        else:
            ar_count = len(ar_rows)
        print(f"    accounts_receivable: {ar_count}")

    return {"ap": ap_count, "ar": ar_count}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — payment_vouchers + allocations
# ═══════════════════════════════════════════════════════════════════════════════

def fill_payment_vouchers(dry_run=False):
    """
    Payment voucher = pembayaran hutang ke vendor.
    Buat 1 voucher per AP yang status-nya bukan unpaid.
    """
    if not M["PayVoucher"] or not M["AP"]:
        print("  ⚠  Model PayVoucher/AP tidak ditemukan — skip")
        return 0

    pv_fields    = _fields(M["PayVoucher"])
    alloc_fields = _fields(M["VoucherAlloc"]) if M["VoucherAlloc"] else set()
    accs         = CACHE["accounts"]
    admin        = CACHE["admin"]
    cash_acc     = accs.get("cash")

    if not cash_acc:
        print("  ⚠  Akun cash tidak ditemukan — skip vouchers")
        return 0

    ap_list = list(M["AP"].objects.filter(
        status__in=["paid", "partial"]
    ).select_related("vendor").order_by("id")[:500])

    if not ap_list:
        print("  ⚠  Tidak ada AP paid/partial — skip vouchers")
        return 0

    vch_rows   = []
    alloc_rows = []
    vch_ctr    = 1
    today      = timezone.now().date()

    for ap in ap_list:
        pay_amount = ap.paid_amount or Decimal("0")
        if pay_amount <= 0:
            continue

        pay_date = ap.invoice_date + timedelta(days=RNG.randint(1, 30))

        kw = {}
        if "number" in pv_fields:
            kw["number"] = _seq("PV", vch_ctr)
        if "date" in pv_fields:
            kw["date"] = pay_date
        if "vendor_id" in pv_fields:
            kw["vendor_id"] = ap.vendor_id
        elif "vendor" in pv_fields:
            kw["vendor"] = ap.vendor
        if "cash_account_id" in pv_fields:
            kw["cash_account_id"] = cash_acc.id
        elif "cash_account" in pv_fields:
            kw["cash_account"] = cash_acc
        if "method" in pv_fields:
            kw["method"] = RNG.choice(["transfer", "cash"])
        if "amount_paid" in pv_fields:
            kw["amount_paid"] = pay_amount
        if "memo" in pv_fields:
            kw["memo"] = f"Bayar {ap.invoice_number}"
        if "created_by_id" in pv_fields and admin:
            kw["created_by_id"] = admin.id
        elif "created_by" in pv_fields and admin:
            kw["created_by"] = admin
        if "created_at" in pv_fields:
            kw["created_at"] = _aware(pay_date)
        if "updated_at" in pv_fields:
            kw["updated_at"] = _now()

        vch_rows.append((kw, ap))
        vch_ctr += 1

    print(f"    {len(vch_rows)} payment vouchers dari {len(ap_list)} AP")

    if dry_run:
        return len(vch_rows)

    try:
        with transaction.atomic():
            saved_vchs = M["PayVoucher"].objects.bulk_create(
                [M["PayVoucher"](**kw) for kw, ap in vch_rows],
                batch_size=300
            )

            if M["VoucherAlloc"] and alloc_fields:
                alloc_objs = []
                for i, saved_vch in enumerate(saved_vchs):
                    _, ap = vch_rows[i]
                    al_kw = {}
                    if "voucher_id" in alloc_fields:
                        al_kw["voucher_id"] = saved_vch.id
                    elif "voucher" in alloc_fields:
                        al_kw["voucher"] = saved_vch
                    if "payable_entry_id" in alloc_fields:
                        al_kw["payable_entry_id"] = ap.id
                    elif "payable_entry" in alloc_fields:
                        al_kw["payable_entry"] = ap
                    if "amount" in alloc_fields:
                        al_kw["amount"] = ap.paid_amount or Decimal("0")
                    alloc_objs.append(M["VoucherAlloc"](**al_kw))

                if alloc_objs:
                    M["VoucherAlloc"].objects.bulk_create(alloc_objs, batch_size=300)
                    print(f"    {len(alloc_objs)} voucher allocations")

    except Exception as e:
        print(f"\n    ⚠  Error vouchers: {e}")
        return 0

    return len(saved_vchs)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "adjustment_reasons": fill_adjustment_reasons,
    "product_batches":    fill_product_batches,
    "orders":             fill_orders_payments_returns,
    "waste":              fill_waste_records,
    "stockopname":        fill_stockopname,
    "journals":           fill_journals,
    "accounting":         fill_journals,
    "ap_ar":              fill_ap_ar,
    "vouchers":           fill_payment_vouchers,
}


def run(section="all", dry_run=True, verbose=True):
    t_total = time_mod.time()

    print("\n" + "═" * 70)
    print("  KAFE NUSANTARA — Fill Empty Tables")
    print("═" * 70)
    print(f"  Mode    : {'DRY RUN' if dry_run else 'EXECUTE — menulis ke DB'}")
    print(f"  Section : {section}")

    warm_cache(verbose=verbose)

    results = {}
    sections_to_run = (
        ["adjustment_reasons", "product_batches", "orders",
         "waste", "stockopname", "journals", "ap_ar", "vouchers"]
        if section == "all"
        else [section]
    )

    for sec in sections_to_run:
        fn = SECTION_MAP.get(sec)
        if not fn:
            print(f"\n  ⚠  Section '{sec}' tidak dikenal")
            continue
        print(f"\n  ▶ [{sec}]")
        try:
            result = fn(dry_run=dry_run)
            results[sec] = result
        except Exception as e:
            import traceback
            print(f"  ✗ Error di section {sec}: {e}")
            traceback.print_exc()
            results[sec] = f"ERROR: {e}"

    elapsed = time_mod.time() - t_total
    print("\n" + "═" * 70)
    print(f"  SELESAI dalam {elapsed:.1f}s")
    print("─" * 70)
    for sec, res in results.items():
        print(f"  {sec:<25} {str(res)}")
    print("═" * 70 + "\n")
    return results


# ── Management Command wrapper ────────────────────────────────────────────────
try:
    from django.core.management.base import BaseCommand

    class Command(BaseCommand):
        help = "Fill all empty tables using existing data."

        def add_arguments(self, parser):
            parser.add_argument("--execute", action="store_true", default=False)
            parser.add_argument("--section", default="all",
                                help="all | adjustment_reasons | product_batches | "
                                     "orders | waste | stockopname | journals | ap_ar | vouchers")
            parser.add_argument("--quiet", action="store_true")

        def handle(self, *args, **opts):
            run(section=opts["section"],
                dry_run=not opts["execute"],
                verbose=not opts["quiet"])

except ImportError:
    pass

# ── Standalone ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    section  = "all"
    dry_run  = True
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--execute":
            dry_run = False
        elif arg == "--section" and i + 1 < len(sys.argv):
            section = sys.argv[i + 1]
        elif arg.startswith("--section="):
            section = arg.split("=", 1)[1]
    run(section=section, dry_run=dry_run)