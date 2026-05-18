"""
seed_fill_empty_tables_v2_PATCHED.py
====================================
Perbaikan dari v2 — 3 fixes utama:

  1. Orders section: OrderItems & Payments tidak tersimpan
     Root cause: Index mismatch di loop saved_orders
     Fix: Tambah bounds check + proper copy dict

  2. Journals: "Tidak ada payments"
     Root cause: Query payments sebelum orders dibuat
     Fix: Refresh query sebelum journals diproses

  3. Vouchers: AP tidak ada yang paid
     Root cause: Probabilitas paid_pct terlalu rendah
     Fix: Ubah RNG.choice ke [1.0, 1.0, 1.0, 0.5, 0]

Cara pakai (sama seperti v2):
  python manage.py seed_fill_empty_tables_v2_patched --execute --section=orders
  python manage.py seed_fill_empty_tables_v2_patched --execute --section=journals
  python manage.py seed_fill_empty_tables_v2_patched --execute
"""

import os
import sys
import random
import time as time_mod
from decimal import Decimal
from datetime import date, datetime, timedelta
from collections import defaultdict

for _sn in ("stdout", "stderr"):
    _s = getattr(sys, _sn, None)
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

if "django" not in sys.modules:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
    import django
    django.setup()

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

User = get_user_model()

# ═══════════════════════════════════════════════════════════════════════════════
# MODEL RESOLVER
# ═══════════════════════════════════════════════════════════════════════════════

def _by_table(db_table: str):
    """Cari model Django berdasarkan db_table name."""
    target = db_table.lower().strip()
    for model in apps.get_models():
        if model._meta.db_table.lower() == target:
            return model
    return None


def _inspect_models():
    """Print semua model yang ditemukan."""
    print("\n  === Model Registry ===")
    for m in sorted(apps.get_models(), key=lambda x: x._meta.db_table):
        print(f"    {m._meta.app_label:20} {m.__name__:45} {m._meta.db_table}")
    print()


M = {
    "Location":     _by_table("lumra_config_locations"),
    "Variant":      _by_table("lumra_config_productvariants"),
    "Product":      _by_table("lumra_config_products"),
    "Customer":     _by_table("lumra_config_customers"),
    "Vendor":       _by_table("lumra_config_vendors"),
    "Unit":         _by_table("lumra_config_units"),
    "Stock":        _by_table("lumra_config_stock"),
    "StockMove":    _by_table("lumra_config_stockmovement"),
    "Zone":         _by_table("lumra_config_warehouse_zones"),
    "AdjustReason": _by_table("lumra_config_stock_adjustment_reasons"),
    "ProductBatch": _by_table("lumra_config_product_batches"),
    "Transfer":     _by_table("lumra_config_transfers"),
    "TransferItem": _by_table("lumra_config_transferitem"),
    "Requisition":  _by_table("lumra_config_requisitions"),
    "ReqItem":      _by_table("lumra_config_requisitionitem"),
    "Order":        _by_table("lumra_config_orders"),
    "OrderItem":    _by_table("lumra_config_orderitems"),
    "Payment":      _by_table("lumra_config_payments"),
    "Return":       _by_table("lumra_config_returns"),
    "ReturnItem":   _by_table("lumra_config_returnitems"),
    "SalesTarget":  _by_table("lumra_config_sales_targets"),
    "OpnameSession":_by_table("lumra_config_stockopname_session"),
    "OpnameItem":   _by_table("lumra_config_stockopname_item"),
    "ProdOrder":    _by_table("production_orders"),
    "MatCons":      _by_table("production_material_consumptions"),
    "FGR":          _by_table("production_finished_goods_receipts"),
    "Waste":        _by_table("production_waste_records"),
    "BOM":          _by_table("production_bill_of_materials"),
    "BOMItem":      _by_table("production_bom_items"),
    "Account":      _by_table("accounting_accounts"),
    "Journal":      _by_table("accounting_journal_entries"),
    "JournalLine":  _by_table("accounting_journal_entry_lines"),
    "AP":           _by_table("accounting_accounts_payable"),
    "AR":           _by_table("accounting_accounts_receivable"),
    "PayVoucher":   _by_table("accounting_payment_vouchers"),
    "VoucherAlloc": _by_table("accounting_payment_voucher_allocations"),
}


def _fields(model) -> set:
    if model is None:
        return set()
    return {f.name for f in model._meta.get_fields()}


def _attname(model, field_name: str) -> str:
    """Kembalikan attname yang benar untuk FK field."""
    if model is None:
        return field_name
    try:
        f = model._meta.get_field(field_name)
        return f.attname
    except Exception:
        return field_name


def _print_fk_info(model):
    """Debug helper — print FK fields."""
    if model is None:
        return
    from django.db.models import ForeignKey
    print(f"\n  FK fields di {model.__name__} ({model._meta.db_table}):")
    for f in model._meta.get_fields():
        if isinstance(f, ForeignKey):
            print(f"    name={f.name!r:25} attname={f.attname!r:30} column={f.column!r}")


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CACHE & HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

CACHE = {}
RNG   = random.Random(42)


def warm_cache(verbose=True):
    t0 = time_mod.time()
    if verbose:
        print("\n  Warming cache...", end="", flush=True)

    CACHE["users"]     = list(User.objects.filter(is_active=True).order_by("id")[:200])
    CACHE["admin"]     = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    CACHE["user_ids"]  = [u.id for u in CACHE["users"]]

    all_locs = list(M["Location"].objects.all().order_by("id"))
    CACHE["locations"]  = all_locs
    CACHE["warehouses"] = [
        l for l in all_locs
        if "warehouse" in getattr(l, "location_type", "").lower()
        or "gudang" in getattr(l, "name", "").lower()
    ] or all_locs[:3]
    CACHE["stores"] = [
        l for l in all_locs
        if "store" in getattr(l, "location_type", "").lower()
        or "outlet" in getattr(l, "location_type", "").lower()
    ] or all_locs[3:] or all_locs

    CACHE["vendors"] = list(M["Vendor"].objects.all().order_by("id"))

    total_v = M["Variant"].objects.count()
    step    = max(1, total_v // 2000)
    ids     = list(M["Variant"].objects.values_list("id", flat=True).order_by("id")[::step][:2000])
    CACHE["variants"] = list(
        M["Variant"].objects.filter(id__in=ids).select_related("product")
    )

    CACHE["customers"] = list(
        M["Customer"].objects.filter(is_active=True).order_by("id")[:5000]
    )
    CACHE["customer_ids"] = [c.id for c in CACHE["customers"]]

    CACHE["accounts"] = {}
    if M["Account"]:
        accs = list(M["Account"].objects.filter(allow_posting=True, is_active=True).order_by("code"))
        for a in accs:
            nm = (a.name or "").lower()
            cd = (a.code or "").lower()
            if not CACHE["accounts"].get("cash") and (
                "kas tunai" in nm or "1-1001" in cd or "1-1010" in cd
            ):
                CACHE["accounts"]["cash"] = a
            if not CACHE["accounts"].get("sales") and (
                "penjualan" in nm or "4-1001" in cd or "4-1002" in cd
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

        fb = accs[0] if accs else None
        for k in ("cash", "sales", "hpp", "inventory", "ap", "ar", "waste"):
            if not CACHE["accounts"].get(k):
                CACHE["accounts"][k] = fb

    if verbose:
        elapsed = time_mod.time() - t0
        print(f" OK ({elapsed:.1f}s)")
        print(f"    users={len(CACHE['users'])}  locs={len(all_locs)}  "
              f"variants={len(CACHE['variants'])}  customers={len(CACHE['customers'])}  "
              f"vendors={len(CACHE['vendors'])}")
        accs_info = {k: (v.code if v else None) for k, v in CACHE["accounts"].items()}
        print(f"    accounts={accs_info}")

        if M["Order"]:
            _print_fk_info(M["Order"])
        if M["Payment"]:
            _print_fk_info(M["Payment"])


def _now():
    return timezone.now()


def _aware(dt_or_date, hour=8, minute=0):
    if isinstance(dt_or_date, date) and not isinstance(dt_or_date, datetime):
        dt_or_date = datetime(dt_or_date.year, dt_or_date.month, dt_or_date.day, hour, minute)
    if timezone.is_naive(dt_or_date):
        return timezone.make_aware(dt_or_date, timezone.get_current_timezone())
    return dt_or_date


def _pick(lst):
    return RNG.choice(lst) if lst else None


def _seq(prefix: str, n: int) -> str:
    yr = timezone.now().year
    return f"{prefix}-{yr}-{n:06d}"


def _bulk_save(model, objects, batch=300):
    if not objects or not model:
        return 0
    total = 0
    for i in range(0, len(objects), batch):
        chunk = objects[i:i + batch]
        try:
            with transaction.atomic():
                created = model.objects.bulk_create(chunk, ignore_conflicts=True, batch_size=batch)
            total += len(created)
        except Exception as e:
            for obj in chunk:
                try:
                    obj.save()
                    total += 1
                except Exception:
                    pass
    return total


def _progress(done, total, t0):
    pct     = done / max(1, total) * 100
    elapsed = time_mod.time() - t0
    eta     = (elapsed / max(1, done)) * (total - done) if done < total else 0
    bar     = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"\r    [{bar}] {pct:5.1f}%  {done:,}/{total:,}  ETA {eta:.0f}s   ",
          end="", flush=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — adjustment_reasons
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
        print("  ⚠  Tabel lumra_config_stock_adjustment_reasons tidak ada — skip")
        return 0

    flds = _fields(model)
    rows = []
    for code, name, desc in ADJUSTMENT_REASONS:
        kw = {}
        if "code" in flds:        kw["code"] = code
        if "name" in flds:        kw["name"] = name
        if "description" in flds: kw["description"] = desc
        if "is_active" in flds:   kw["is_active"] = True
        rows.append(model(**kw))

    print(f"    {len(rows)} adjustment reasons")
    if dry_run:
        return len(rows)
    return _bulk_save(model, rows)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — product_batches
# ═══════════════════════════════════════════════════════════════════════════════

def fill_product_batches(dry_run=False, limit=3000):
    model = M["ProductBatch"]
    if not model:
        print("  ⚠  Tabel lumra_config_product_batches tidak ditemukan — skip")
        return 0

    flds = _fields(model)

    variants_q = M["Variant"].objects.select_related("product")
    try:
        variants_q = variants_q.filter(product__has_expiry=True)
    except Exception:
        pass
    variants_list = list(variants_q.order_by("id")[:limit])
    if not variants_list:
        variants_list = list(M["Variant"].objects.order_by("id")[:limit])

    warehouses = CACHE["warehouses"]
    vendors    = CACHE["vendors"]
    admin      = CACHE["admin"]
    today      = timezone.now().date()

    if not warehouses or not vendors or not variants_list:
        print("  ⚠  Data kurang — skip product_batches")
        return 0

    rows    = []
    counter = 1

    vendor_ids    = [v.id for v in vendors]
    warehouse_ids = [l.id for l in warehouses]

    product_att  = _attname(model, "product")   if "product" in flds else None
    location_att = _attname(model, "location")  if "location" in flds else None
    supplier_att = _attname(model, "supplier")  if "supplier" in flds else None

    for variant in variants_list:
        for _ in range(RNG.randint(1, 2)):
            mfg_ago  = RNG.randint(30, 270)
            mfg      = today - timedelta(days=mfg_ago)
            shelf    = RNG.choice([90, 180, 270, 365])
            exp      = mfg + timedelta(days=shelf)
            qty_in   = Decimal(str(RNG.randint(24, 240)))

            kw = {}
            if product_att:
                kw[product_att] = variant.id
            if location_att:
                kw[location_att] = RNG.choice(warehouse_ids)
            if supplier_att:
                kw[supplier_att] = RNG.choice(vendor_ids)
            if "batch_number" in flds:
                kw["batch_number"] = f"BTH-{today.year}-{counter:06d}"
            if "supplier_batch_number" in flds:
                kw["supplier_batch_number"] = f"SUP-{RNG.randint(10000, 99999)}"
            if "manufacturing_date" in flds:
                kw["manufacturing_date"] = mfg
            if "expiry_date" in flds:
                kw["expiry_date"] = exp
            if "quantity_in" in flds:
                kw["quantity_in"] = qty_in
            if "quantity_available" in flds:
                kw["quantity_available"] = (qty_in * Decimal(str(RNG.uniform(0.5, 0.98)))).quantize(Decimal("0.01"))
            if "notes" in flds:
                kw["notes"] = "Batch seeded"
            if "created_at" in flds:
                kw["created_at"] = _aware(mfg, 8)
            if "updated_at" in flds:
                kw["updated_at"] = _now()

            rows.append(model(**kw))
            counter += 1

    print(f"    {len(rows)} product batches dari {len(variants_list)} variants")
    if dry_run:
        return len(rows)
    return _bulk_save(model, rows, batch=500)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3+4+5 — orders, orderitems, payments, returns [PATCHED]
# ═══════════════════════════════════════════════════════════════════════════════

def fill_orders_payments_returns(dry_run=False):
    if not all([M["Order"], M["OrderItem"], M["Payment"]]):
        print("  ⚠  Model Order/OrderItem/Payment tidak ditemukan — skip")
        return {}

    order_flds = _fields(M["Order"])
    oi_flds    = _fields(M["OrderItem"])
    pay_flds   = _fields(M["Payment"])
    ret_flds   = _fields(M["Return"])   if M["Return"]   else set()
    reti_flds  = _fields(M["ReturnItem"]) if M["ReturnItem"] else set()

    order_customer_att = _attname(M["Order"], "customer") if "customer" in order_flds else None
    order_cashier_att  = (
        _attname(M["Order"], "cashier_id") if "cashier_id" in order_flds
        else (_attname(M["Order"], "cashier") if "cashier" in order_flds else None)
    )

    pay_order_att      = _attname(M["Payment"], "order")        if "order" in pay_flds else None
    pay_receiver_att   = (
        _attname(M["Payment"], "received_by") if "received_by" in pay_flds else None
    )

    print(f"    Order FK attnames: customer={order_customer_att}, cashier={order_cashier_att}")
    print(f"    Payment FK attnames: order={pay_order_att}, received_by={pay_receiver_att}")

    store_ids   = {l.id for l in CACHE["stores"]}
    user_ids    = CACHE["user_ids"]
    cust_ids    = CACHE["customer_ids"]
    vendor_ids  = [v.id for v in CACHE["vendors"]]

    trf_qs = M["Transfer"].objects.filter(status="received").order_by("created_at")
    transfers  = list(trf_qs)

    if not transfers:
        print("  ⚠  Tidak ada transfers status=received — skip")
        return {}

    print(f"    Source transfers: {len(transfers):,}")

    trf_ids      = [t.id for t in transfers]
    trf_item_map = defaultdict(list)
    CHUNK        = 2000
    for i in range(0, len(trf_ids), CHUNK):
        for ti in M["TransferItem"].objects.filter(
            transfer_id__in=trf_ids[i:i + CHUNK]
        ).values("transfer_id", "variant_id", "quantity_received"):
            trf_item_map[ti["transfer_id"]].append(ti)

    all_data    = []
    order_ctr   = 1
    pay_ctr     = 1
    ret_ctr     = 1

    pay_methods = ["cash", "transfer", "qris", "card", "debit"]
    dine_opts   = ["dine_in", "takeaway", "delivery"]

    t0 = time_mod.time()
    for idx, trf in enumerate(transfers):
        if idx % 10000 == 0:
            _progress(idx, len(transfers), t0)

        ti_list = trf_item_map.get(trf.id, [])
        if not ti_list:
            continue

        dest_id = getattr(trf, "destination_location_id", None)
        if store_ids and dest_id and dest_id not in store_ids:
            continue

        trf_dt = getattr(trf, "received_at", None) or getattr(trf, "created_at", None) or _now()
        trf_dt_aware = _aware(trf_dt)

        num_orders = RNG.randint(1, 3)

        for k in range(num_orders):
            order_dt   = trf_dt_aware + timedelta(hours=RNG.randint(2, 72), minutes=k * 15)
            cust_id    = RNG.choice(cust_ids) if cust_ids else None
            cashier_id = RNG.choice(user_ids) if user_ids else None
            method     = _pick(pay_methods)

            oi_list      = []
            total_amount = Decimal("0")

            for ti in ti_list:
                avail = int(ti.get("quantity_received") or 0)
                if avail <= 0:
                    continue
                sold = max(1, int(avail * RNG.uniform(0.05, 0.4) / num_orders))

                price = Decimal(str(RNG.randint(5000, 150000)))
                total_amount += price * sold

                oi_kw = {}
                oi_variant_att = _attname(M["OrderItem"], "variant") if "variant" in oi_flds else None
                if oi_variant_att:
                    oi_kw[oi_variant_att] = ti["variant_id"]
                if "quantity" in oi_flds:       oi_kw["quantity"] = sold
                if "price" in oi_flds:          oi_kw["price"] = price
                if "cost_price" in oi_flds:     oi_kw["cost_price"] = (price * Decimal("0.65")).quantize(Decimal("0.01"))
                if "discount_amount" in oi_flds: oi_kw["discount_amount"] = Decimal("0")
                if "discount_percent" in oi_flds: oi_kw["discount_percent"] = Decimal("0")
                if "notes" in oi_flds:          oi_kw["notes"] = ""
                oi_list.append(oi_kw)

            if not oi_list:
                continue

            ord_kw = {}
            if "customer_name" in order_flds:
                ord_kw["customer_name"] = f"Customer-{cust_id or 0}"
            if "status" in order_flds:
                ord_kw["status"] = "completed"
            if order_customer_att and cust_id:
                ord_kw[order_customer_att] = cust_id
            if order_cashier_att and cashier_id:
                ord_kw[order_cashier_att] = cashier_id
            if "change_amount" in order_flds:
                ord_kw["change_amount"] = Decimal("0")
            if "dining_option" in order_flds:
                ord_kw["dining_option"] = _pick(dine_opts)
            if "order_type" in order_flds:
                ord_kw["order_type"] = "pos"
            if "paid_amount" in order_flds:
                ord_kw["paid_amount"] = total_amount
            if "payment_method" in order_flds:
                ord_kw["payment_method"] = method
            if "payment_status" in order_flds:
                ord_kw["payment_status"] = "paid"
            if "shift_id" in order_flds:
                ord_kw["shift_id"] = f"SHF-{order_dt.strftime('%Y%m%d')}-{order_dt.hour // 8 + 1}"
            if "table_number" in order_flds:
                ord_kw["table_number"] = f"T-{RNG.randint(1, 30)}"
            if "created_at" in order_flds:
                ord_kw["created_at"] = order_dt

            pay_kw = {}
            if "payment_number" in pay_flds:
                pay_kw["payment_number"] = _seq("PAY", pay_ctr); pay_ctr += 1
            if "payment_date" in pay_flds:
                pay_kw["payment_date"] = order_dt.date()
            if "amount" in pay_flds:
                pay_kw["amount"] = total_amount
            if "payment_method" in pay_flds:
                pay_kw["payment_method"] = method
            if "status" in pay_flds:
                pay_kw["status"] = "completed"
            if "reference_number" in pay_flds:
                pay_kw["reference_number"] = (
                    f"REF-{RNG.randint(100000, 999999)}" if method != "cash" else ""
                )
            if pay_receiver_att and cashier_id:
                pay_kw[pay_receiver_att] = cashier_id
            if "notes" in pay_flds:
                pay_kw["notes"] = ""
            if "created_at" in pay_flds:
                pay_kw["created_at"] = order_dt
            if "updated_at" in pay_flds:
                pay_kw["updated_at"] = order_dt

            ret_kw = reti_kw = None
            if RNG.random() < 0.08 and M["Return"] and ret_flds:
                ret_kw = {}
                ret_att_order    = _attname(M["Return"], "order")    if "order" in ret_flds else None
                ret_att_customer = _attname(M["Return"], "customer") if "customer" in ret_flds else None
                ret_att_created  = (
                    _attname(M["Return"], "created_by") if "created_by" in ret_flds else None
                )
                if ret_att_customer and cust_id: ret_kw[ret_att_customer] = cust_id
                if "retur_number" in ret_flds:  ret_kw["retur_number"] = _seq("RET", ret_ctr)
                if "retur_date" in ret_flds:
                    ret_kw["retur_date"] = order_dt.date() + timedelta(days=RNG.randint(1, 7))
                if "total_amount" in ret_flds:
                    ret_kw["total_amount"] = (total_amount * Decimal(str(RNG.uniform(0.2, 0.5)))).quantize(Decimal("0.01"))
                if "status" in ret_flds:
                    ret_kw["status"] = RNG.choice(["approved", "pending"])
                if "reason" in ret_flds:
                    ret_kw["reason"] = RNG.choice([
                        "Produk rusak", "Salah item", "Kualitas tidak sesuai", "Lainnya"
                    ])
                if "notes" in ret_flds:      ret_kw["notes"] = ""
                if ret_att_created and CACHE["admin"]:
                    ret_kw[ret_att_created] = CACHE["admin"].id
                if "created_at" in ret_flds:  ret_kw["created_at"] = _now()
                if "updated_at" in ret_flds:  ret_kw["updated_at"] = _now()

                if oi_list and M["ReturnItem"] and reti_flds:
                    src = oi_list[0]
                    variant_id = src.get(_attname(M["OrderItem"], "variant") if "variant" in oi_flds else "variant_id")
                    ret_qty = max(1, int(src.get("quantity", 1) * RNG.uniform(0.3, 1.0)))
                    reti_kw = {}
                    reti_att_ret  = _attname(M["ReturnItem"], "retur_header") if "retur_header" in reti_flds else None
                    reti_att_prod = _attname(M["ReturnItem"], "product")      if "product" in reti_flds else None
                    if reti_att_prod and variant_id:    reti_kw[reti_att_prod] = variant_id
                    if "quantity" in reti_flds:         reti_kw["quantity"] = Decimal(str(ret_qty))
                    if "unit_price" in reti_flds:       reti_kw["unit_price"] = src.get("price", Decimal("5000"))
                    if "total_price" in reti_flds:
                        reti_kw["total_price"] = (Decimal(str(ret_qty)) * src.get("price", Decimal("5000"))).quantize(Decimal("0.01"))
                    if "reason" in reti_flds:
                        reti_kw["reason"] = RNG.choice(["damaged", "wrong_item", "quality", "other"])
                    if "notes" in reti_flds:            reti_kw["notes"] = ""
                    if "created_at" in reti_flds:       reti_kw["created_at"] = _now()

                ret_ctr += 1

            all_data.append((ord_kw, oi_list, pay_kw, ret_kw, reti_kw))
            order_ctr += 1

    print()
    total_oi = sum(len(d[1]) for d in all_data)
    print(f"    Generated: {len(all_data):,} orders  {total_oi:,} items  "
          f"{sum(1 for d in all_data if d[3])} returns")

    if dry_run:
        return {
            "orders": len(all_data),
            "items": total_oi,
            "payments": len(all_data),
            "returns": sum(1 for d in all_data if d[3]),
        }

    saved = {"orders": 0, "items": 0, "payments": 0, "returns": 0, "return_items": 0}
    BATCH = 300

    oi_order_att  = _attname(M["OrderItem"], "order") if "order" in oi_flds else "order_id"
    pay_order_att_final = pay_order_att or "order_id"

    ret_order_att = None
    if M["Return"] and ret_flds:
        ret_order_att = _attname(M["Return"], "order") if "order" in ret_flds else None

    reti_ret_att = None
    if M["ReturnItem"] and reti_flds:
        reti_ret_att = _attname(M["ReturnItem"], "retur_header") if "retur_header" in reti_flds else None

    t0 = time_mod.time()
    for batch_start in range(0, len(all_data), BATCH):
        chunk = all_data[batch_start:batch_start + BATCH]

        try:
            with transaction.atomic():
                # 1. Save Orders
                order_objs  = [M["Order"](**d[0]) for d in chunk]
                saved_orders = M["Order"].objects.bulk_create(order_objs, batch_size=BATCH)
                saved["orders"] += len(saved_orders)

                # 2. OrderItems — FIX: proper index handling
                oi_objs = []
                for i, s_ord in enumerate(saved_orders):
                    if i >= len(chunk):  # ← BOUNDS CHECK
                        break
                    for oi_kw in chunk[i][1]:
                        oi_kw[oi_order_att] = s_ord.id
                        oi_objs.append(M["OrderItem"](**oi_kw))
                if oi_objs:
                    M["OrderItem"].objects.bulk_create(oi_objs, batch_size=BATCH * 2)
                    saved["items"] += len(oi_objs)

                # 3. Payments — FIX: proper dict copy + index handling
                pay_objs = []
                for i, s_ord in enumerate(saved_orders):
                    if i >= len(chunk):  # ← BOUNDS CHECK
                        break
                    pk = dict(chunk[i][2])  # ← PROPER DICT COPY
                    pk[pay_order_att_final] = s_ord.id
                    pay_objs.append(M["Payment"](**pk))
                if pay_objs:
                    M["Payment"].objects.bulk_create(pay_objs, batch_size=BATCH)
                    saved["payments"] += len(pay_objs)

                # 4. Returns — FIX: proper bounds checking
                if M["Return"] and ret_order_att:
                    ret_objs  = []
                    reti_data = []
                    for i, s_ord in enumerate(saved_orders):
                        if i >= len(chunk):  # ← BOUNDS CHECK
                            break
                        ret_kw = chunk[i][3]
                        if ret_kw is None:
                            continue
                        rk = dict(ret_kw)
                        rk[ret_order_att] = s_ord.id
                        ret_objs.append((M["Return"](**rk), chunk[i][4]))

                    if ret_objs:
                        saved_rets = M["Return"].objects.bulk_create(
                            [r for r, _ in ret_objs], batch_size=BATCH
                        )
                        saved["returns"] += len(saved_rets)

                        # ReturnItems — FIX: proper bounds checking
                        if M["ReturnItem"] and reti_ret_att:
                            ri_objs = []
                            for j, s_ret in enumerate(saved_rets):
                                if j >= len(ret_objs):  # ← BOUNDS CHECK
                                    break
                                reti_kw = ret_objs[j][1]
                                if reti_kw is None:
                                    continue
                                rk2 = dict(reti_kw)
                                rk2[reti_ret_att] = s_ret.id
                                ri_objs.append(M["ReturnItem"](**rk2))
                            if ri_objs:
                                M["ReturnItem"].objects.bulk_create(ri_objs, batch_size=BATCH)
                                saved["return_items"] += len(ri_objs)

        except Exception as e:
            print(f"\n    ⚠  Batch {batch_start}-{batch_start+BATCH}: {e}")

        if batch_start % (BATCH * 20) == 0:
            _progress(batch_start, len(all_data), t0)

    print(f"\r    ✓ orders={saved['orders']:,}  items={saved['items']:,}  "
          f"payments={saved['payments']:,}  returns={saved['returns']:,}  "
          f"return_items={saved['return_items']:,}      ")
    return saved


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — waste_records
# ═══════════════════════════════════════════════════════════════════════════════

def fill_waste_records(dry_run=False):
    if not M["Waste"]:
        print("  ⚠  Tabel production_waste_records tidak ditemukan — skip")
        return 0
    if not M["MatCons"]:
        print("  ⚠  Tabel production_material_consumptions tidak ditemukan — skip")
        return 0

    flds       = _fields(M["Waste"])
    cons_flds  = _fields(M["MatCons"])

    po_att   = _attname(M["Waste"], "production_order") if "production_order" in flds else None
    comp_att = _attname(M["Waste"], "component")        if "component" in flds else None
    unit_att = _attname(M["Waste"], "unit")             if "unit" in flds else None

    print(f"    Waste FK attnames: po={po_att}, comp={comp_att}, unit={unit_att}")

    cons_list = list(
        M["MatCons"].objects.values(
            "id", "production_order_id", "component_id", "unit_id", "quantity"
        ).order_by("id")[:80000]
    )

    if not cons_list:
        print("  ⚠  Tidak ada material_consumptions — skip waste")
        return 0

    rows       = []
    waste_types = ["defect", "spillage", "expired", "process_loss", "damage"]

    for cons in cons_list:
        if RNG.random() > 0.12:
            continue

        waste_qty = Decimal(str(cons["quantity"])) * Decimal(str(RNG.uniform(0.01, 0.05)))
        waste_qty = max(Decimal("0.01"), waste_qty.quantize(Decimal("0.01")))

        rec_at = _now() - timedelta(days=RNG.randint(1, 365))

        kw = {}
        if po_att:   kw[po_att]   = cons["production_order_id"]
        if comp_att: kw[comp_att] = cons["component_id"]
        if unit_att and cons.get("unit_id"):
            kw[unit_att] = cons["unit_id"]
        if "waste_type" in flds:   kw["waste_type"]  = _pick(waste_types)
        if "quantity" in flds:     kw["quantity"]     = waste_qty
        if "recorded_at" in flds:  kw["recorded_at"]  = rec_at
        if "notes" in flds:        kw["notes"]         = "Generated waste record"

        rows.append(M["Waste"](**kw))

    print(f"    {len(rows):,} waste records dari {len(cons_list):,} consumptions (12% rate)")
    if dry_run:
        return len(rows)
    return _bulk_save(M["Waste"], rows, batch=500)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — stockopname
# ═══════════════════════════════════════════════════════════════════════════════

def fill_stockopname(dry_run=False):
    if not M["OpnameSession"] or not M["OpnameItem"]:
        print("  ⚠  Model OpnameSession/OpnameItem tidak ditemukan — skip")
        return 0

    existing = M["OpnameSession"].objects.count()
    if existing > 0:
        print(f"  ⚠  Sudah ada {existing} sessions — skip")
        return 0

    sess_flds = _fields(M["OpnameSession"])
    item_flds = _fields(M["OpnameItem"])
    admin     = CACHE["admin"]
    today     = timezone.now().date()

    loc_att  = _attname(M["OpnameSession"], "location")   if "location" in sess_flds else None
    user_att = _attname(M["OpnameSession"], "created_by") if "created_by" in sess_flds else None

    sess_att    = _attname(M["OpnameItem"], "session") if "session" in item_flds else None
    var_att_oi  = _attname(M["OpnameItem"], "variant") if "variant" in item_flds else None

    locs_with_stock = list(
        M["Stock"].objects.values_list("location_id", flat=True).distinct()
    )[:20]

    total_items    = 0
    total_sessions = 0

    for loc_id in locs_with_stock:
        stocks = list(
            M["Stock"].objects.filter(location_id=loc_id)
            .values("variant_id", "quantity")[:200]
        )
        if not stocks:
            continue

        sess_kw = {}
        if loc_att:  sess_kw[loc_att]  = loc_id
        if user_att and admin: sess_kw[user_att] = admin.id
        if "status" in sess_flds:      sess_kw["status"] = RNG.choice(["approved", "submitted"])
        if "notes" in sess_flds:       sess_kw["notes"]  = f"Opname rutin {today.strftime('%B %Y')}"
        if "created_at" in sess_flds:
            sess_kw["created_at"] = _aware(today - timedelta(days=RNG.randint(1, 30)))
        if "submitted_at" in sess_flds:
            sess_kw["submitted_at"] = _aware(today - timedelta(days=RNG.randint(0, 7)))
        if "approved_at" in sess_flds and sess_kw.get("status") == "approved":
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
            print(f"\n    ⚠  Session lokasi {loc_id}: {e}")
            continue

        item_objs = []
        for stk in stocks:
            sys_qty = stk["quantity"]
            counted = max(0, int(sys_qty * RNG.uniform(0.93, 1.04)))
            ik = {}
            if sess_att:    ik[sess_att] = session.id
            if var_att_oi:  ik[var_att_oi] = stk["variant_id"]
            if "current_stock" in item_flds: ik["current_stock"] = sys_qty
            if "counted_qty" in item_flds:   ik["counted_qty"]   = counted
            if "notes" in item_flds:
                diff = counted - sys_qty
                ik["notes"] = f"Selisih {diff:+d}" if diff != 0 else "Sesuai"
            if "created_at" in item_flds:    ik["created_at"] = sess_kw.get("created_at", _now())
            item_objs.append(M["OpnameItem"](**ik))

        saved = _bulk_save(M["OpnameItem"], item_objs, batch=300)
        total_items += saved

    print(f"    {total_sessions} sessions  {total_items:,} opname items")
    return total_items


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — journal_entries [PATCHED - refresh payment query]
# ═══════════════════════════════════════════════════════════════════════════════

def fill_journals(dry_run=False):
    if not M["Journal"]:
        print("  ⚠  Tabel accounting_journal_entries tidak ditemukan di Django — skip")
        return 0
    if not M["JournalLine"]:
        print("  ⚠  Tabel accounting_journal_entry_lines tidak ditemukan — skip")
        return 0

    accs = CACHE["accounts"]
    if not accs.get("cash") or not accs.get("sales"):
        print("  ⚠  Akun cash/sales tidak ditemukan — skip")
        return 0

    je_flds   = _fields(M["Journal"])
    line_flds = _fields(M["JournalLine"])
    admin     = CACHE["admin"]

    je_user_att      = _attname(M["Journal"], "created_by") if "created_by" in je_flds else None
    je_posted_att    = _attname(M["Journal"], "posted_by")  if "posted_by" in je_flds else None
    line_je_att      = (
        _attname(M["JournalLine"], "journal_entry") if "journal_entry" in line_flds else None
    )
    line_acc_att     = _attname(M["JournalLine"], "account") if "account" in line_flds else None

    print(f"    Journal FK: created_by={je_user_att}, line.journal_entry={line_je_att}, line.account={line_acc_att}")

    # FIX: Refresh payment query (payments dibuat di section orders)
    payments = list(
        M["Payment"].objects.order_by("created_at")[:15000]
    )

    if not payments:
        print("  ⚠  Tidak ada payments — skip journals")
        print("     💡 Jalankan --section=orders terlebih dahulu untuk generate payments")
        return 0

    print(f"    Source: {len(payments):,} payments")

    total_je   = 0
    total_line = 0
    je_ctr     = 1
    BATCH      = 300

    t0 = time_mod.time()
    for batch_start in range(0, len(payments), BATCH):
        batch = payments[batch_start:batch_start + BATCH]
        je_dicts   = []
        line_pairs = []

        for pay in batch:
            amount = getattr(pay, "amount", None) or Decimal("0")
            if amount <= 0:
                continue

            pay_dt = getattr(pay, "created_at", None) or _now()
            pay_dt = _aware(pay_dt)

            jk = {}
            if "number" in je_flds:       jk["number"]      = _seq("JE", je_ctr)
            if "date" in je_flds:         jk["date"]         = pay_dt.date()
            if "reference" in je_flds:    jk["reference"]    = getattr(pay, "payment_number", str(pay.id))
            if "description" in je_flds:  jk["description"]  = "Penjualan POS"
            if "status" in je_flds:       jk["status"]       = "posted"
            if "source" in je_flds:       jk["source"]       = "sale"
            if je_user_att and admin:     jk[je_user_att]    = admin.id
            if je_posted_att and admin:   jk[je_posted_att]  = admin.id
            if "posted_at" in je_flds:    jk["posted_at"]    = pay_dt
            if "created_at" in je_flds:   jk["created_at"]   = pay_dt
            if "updated_at" in je_flds:   jk["updated_at"]   = pay_dt

            je_dicts.append(jk)

            l1 = {}
            if line_acc_att: l1[line_acc_att] = accs["cash"].id
            if "debit" in line_flds:       l1["debit"]       = amount
            if "credit" in line_flds:      l1["credit"]      = Decimal("0")
            if "description" in line_flds: l1["description"] = "Penerimaan kas"
            if "created_at" in line_flds:  l1["created_at"]  = pay_dt

            l2 = {}
            if line_acc_att: l2[line_acc_att] = accs["sales"].id
            if "debit" in line_flds:       l2["debit"]       = Decimal("0")
            if "credit" in line_flds:      l2["credit"]      = amount
            if "description" in line_flds: l2["description"] = "Pendapatan penjualan"
            if "created_at" in line_flds:  l2["created_at"]  = pay_dt

            line_pairs.append((l1, l2))
            je_ctr += 1

        if not je_dicts:
            continue

        if dry_run:
            total_je   += len(je_dicts)
            total_line += len(je_dicts) * 2
            continue

        try:
            with transaction.atomic():
                saved_jes = M["Journal"].objects.bulk_create(
                    [M["Journal"](**kw) for kw in je_dicts],
                    batch_size=BATCH
                )
                total_je += len(saved_jes)

                all_lines = []
                for i, s_je in enumerate(saved_jes):
                    if i >= len(line_pairs):
                        break
                    l1_kw, l2_kw = line_pairs[i]
                    if line_je_att:
                        l1_kw[line_je_att] = s_je.id
                        l2_kw[line_je_att] = s_je.id
                    all_lines.append(M["JournalLine"](**l1_kw))
                    all_lines.append(M["JournalLine"](**l2_kw))

                if all_lines:
                    M["JournalLine"].objects.bulk_create(all_lines, batch_size=BATCH * 2)
                    total_line += len(all_lines)

        except Exception as e:
            print(f"\n    ⚠  JE batch {batch_start}: {e}")

        if batch_start % (BATCH * 10) == 0:
            _progress(batch_start, len(payments), t0)

    print(f"\r    ✓ journal_entries={total_je:,}  journal_lines={total_line:,}      ")
    return total_je


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9+10 — AP + AR [PATCHED - better paid_pct]
# ═══════════════════════════════════════════════════════════════════════════════

def fill_ap_ar(dry_run=False):
    ap_count = 0
    ar_count = 0
    today    = timezone.now().date()
    admin    = CACHE["admin"]

    if M["AP"]:
        ap_flds  = _fields(M["AP"])
        vendors  = CACHE["vendors"]
        je_ids   = list(M["Journal"].objects.values_list("id", flat=True).order_by("id")[:len(vendors)])

        vendor_att = _attname(M["AP"], "vendor")        if "vendor" in ap_flds else None
        je_att     = _attname(M["AP"], "journal_entry") if "journal_entry" in ap_flds else None

        ap_rows = []
        for i, v in enumerate(vendors[:100]):
            inv_date = today - timedelta(days=RNG.randint(7, 90))
            due_date = inv_date + timedelta(days=RNG.choice([30, 45, 60]))
            total    = Decimal(str(RNG.randint(500000, 25000000)))
            
            # FIX: Better probabilitas paid (60% fully paid, 20% partial, 20% unpaid)
            paid_pct = RNG.choice([1.0, 1.0, 1.0, 0.5, 0])
            
            paid     = (total * Decimal(str(paid_pct))).quantize(Decimal("0.01"))
            status   = "paid" if paid >= total else ("partial" if paid > 0 else "unpaid")

            kw = {}
            if vendor_att:                kw[vendor_att]       = v.id
            if "invoice_number" in ap_flds: kw["invoice_number"] = f"BILL-{today.year}-{i+1:05d}"
            if "invoice_date" in ap_flds:   kw["invoice_date"]   = inv_date
            if "due_date" in ap_flds:       kw["due_date"]        = due_date
            if "total_amount" in ap_flds:   kw["total_amount"]    = total
            if "paid_amount" in ap_flds:    kw["paid_amount"]     = paid
            if "status" in ap_flds:         kw["status"]          = status
            if "memo" in ap_flds:           kw["memo"]            = f"Invoice dari {v.name}"
            if je_att and i < len(je_ids):  kw[je_att]           = je_ids[i]
            if "created_at" in ap_flds:     kw["created_at"]     = _aware(inv_date)
            if "updated_at" in ap_flds:     kw["updated_at"]     = _now()
            ap_rows.append(M["AP"](**kw))

        print(f"    accounts_payable: {len(ap_rows)}")
        if not dry_run:
            ap_count = _bulk_save(M["AP"], ap_rows)
        else:
            ap_count = len(ap_rows)
    else:
        print("  ⚠  Tabel accounting_accounts_payable tidak ditemukan — skip AP")

    if M["AR"]:
        ar_flds   = _fields(M["AR"])
        customers = CACHE["customers"]
        je_ids2   = list(M["Journal"].objects.values_list("id", flat=True).order_by("-id")[:300])

        cust_att = _attname(M["AR"], "customer")       if "customer" in ar_flds else None
        je_att2  = _attname(M["AR"], "journal_entry")  if "journal_entry" in ar_flds else None

        sample_custs = RNG.sample(customers, min(300, len(customers)))
        ar_rows = []
        for i, c in enumerate(sample_custs):
            inv_date = today - timedelta(days=RNG.randint(1, 90))
            due_date = inv_date + timedelta(days=30)
            total    = Decimal(str(RNG.randint(100000, 8000000)))
            
            # FIX: Better probabilitas paid
            paid_pct = RNG.choice([1.0, 1.0, 1.0, 0.5, 0])
            
            paid     = (total * Decimal(str(paid_pct))).quantize(Decimal("0.01"))
            status   = "paid" if paid >= total else ("partial" if paid > 0 else "unpaid")

            kw = {}
            if cust_att:                    kw[cust_att]         = c.id
            if "invoice_number" in ar_flds: kw["invoice_number"] = f"INV-{today.year}-{i+1:05d}"
            if "invoice_date" in ar_flds:   kw["invoice_date"]   = inv_date
            if "due_date" in ar_flds:       kw["due_date"]        = due_date
            if "total_amount" in ar_flds:   kw["total_amount"]    = total
            if "paid_amount" in ar_flds:    kw["paid_amount"]     = paid
            if "status" in ar_flds:         kw["status"]          = status
            if "memo" in ar_flds:           kw["memo"]            = f"Invoice ke {c.name}"
            if je_att2 and i < len(je_ids2): kw[je_att2]          = je_ids2[i]
            if "created_at" in ar_flds:     kw["created_at"]     = _aware(inv_date)
            if "updated_at" in ar_flds:     kw["updated_at"]     = _now()
            ar_rows.append(M["AR"](**kw))

        print(f"    accounts_receivable: {len(ar_rows)}")
        if not dry_run:
            ar_count = _bulk_save(M["AR"], ar_rows)
        else:
            ar_count = len(ar_rows)
    else:
        print("  ⚠  Tabel accounting_accounts_receivable tidak ditemukan — skip AR")

    return {"ap": ap_count, "ar": ar_count}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — payment_vouchers
# ═══════════════════════════════════════════════════════════════════════════════

def fill_payment_vouchers(dry_run=False):
    if not M["PayVoucher"]:
        print("  ⚠  Tabel accounting_payment_vouchers tidak ditemukan — skip")
        return 0
    if not M["AP"]:
        print("  ⚠  AP tidak ada — skip vouchers")
        return 0

    pv_flds    = _fields(M["PayVoucher"])
    alloc_flds = _fields(M["VoucherAlloc"]) if M["VoucherAlloc"] else set()
    cash_acc   = CACHE["accounts"].get("cash")
    admin      = CACHE["admin"]

    if not cash_acc:
        print("  ⚠  Akun cash tidak ditemukan — skip vouchers")
        return 0

    vendor_att  = _attname(M["PayVoucher"], "vendor")       if "vendor" in pv_flds else None
    acc_att     = _attname(M["PayVoucher"], "cash_account")  if "cash_account" in pv_flds else None
    user_att_pv = _attname(M["PayVoucher"], "created_by")   if "created_by" in pv_flds else None
    je_att_pv   = _attname(M["PayVoucher"], "journal_entry") if "journal_entry" in pv_flds else None

    print(f"    Voucher FK: vendor={vendor_att}, cash_account={acc_att}, created_by={user_att_pv}")

    # FIX: Refresh AP query (mungkin ada yang baru tersimpan)
    ap_list = list(M["AP"].objects.filter(
        status__in=["paid", "partial"]
    ).values("id", "vendor_id", "paid_amount", "invoice_date", "invoice_number")
     .order_by("id")[:500])

    if not ap_list:
        print("  ⚠  Tidak ada AP paid/partial — skip vouchers")
        print("     💡 Jalankan --section=ap_ar terlebih dahulu")
        return 0

    vch_rows = []
    ap_map   = []
    vch_ctr  = 1

    for ap in ap_list:
        pay_amount = ap["paid_amount"] or Decimal("0")
        if pay_amount <= 0:
            continue
        inv_date = ap["invoice_date"]
        pay_date = (inv_date + timedelta(days=RNG.randint(1, 30))
                    if isinstance(inv_date, date) else timezone.now().date())

        kw = {}
        if "number" in pv_flds:      kw["number"]      = _seq("PV", vch_ctr)
        if "date" in pv_flds:        kw["date"]         = pay_date
        if vendor_att:               kw[vendor_att]     = ap["vendor_id"]
        if acc_att:                  kw[acc_att]        = cash_acc.id
        if "method" in pv_flds:      kw["method"]       = RNG.choice(["transfer", "cash"])
        if "amount_paid" in pv_flds: kw["amount_paid"]  = pay_amount
        if "memo" in pv_flds:        kw["memo"]         = f"Bayar {ap['invoice_number']}"
        if user_att_pv and admin:    kw[user_att_pv]   = admin.id
        if "created_at" in pv_flds:  kw["created_at"]   = _aware(pay_date)
        if "updated_at" in pv_flds:  kw["updated_at"]   = _now()

        vch_rows.append(kw)
        ap_map.append(ap)
        vch_ctr += 1

    print(f"    {len(vch_rows)} payment vouchers dari {len(ap_list)} AP")
    if dry_run:
        return len(vch_rows)

    alloc_vch_att = _attname(M["VoucherAlloc"], "voucher")       if M["VoucherAlloc"] and "voucher" in alloc_flds else None
    alloc_ap_att  = _attname(M["VoucherAlloc"], "payable_entry") if M["VoucherAlloc"] and "payable_entry" in alloc_flds else None

    try:
        with transaction.atomic():
            saved_vchs = M["PayVoucher"].objects.bulk_create(
                [M["PayVoucher"](**kw) for kw in vch_rows], batch_size=300
            )

            if M["VoucherAlloc"] and alloc_vch_att and alloc_ap_att:
                alloc_objs = []
                for i, s_vch in enumerate(saved_vchs):
                    al = {}
                    al[alloc_vch_att] = s_vch.id
                    al[alloc_ap_att]  = ap_map[i]["id"]
                    if "amount" in alloc_flds:
                        al["amount"] = ap_map[i]["paid_amount"] or Decimal("0")
                    alloc_objs.append(M["VoucherAlloc"](**al))
                if alloc_objs:
                    M["VoucherAlloc"].objects.bulk_create(alloc_objs, batch_size=300)
                    print(f"    {len(alloc_objs)} voucher allocations")

    except Exception as e:
        print(f"\n    ⚠  Error vouchers: {e}")
        return 0

    return len(saved_vchs)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "adjustment_reasons": fill_adjustment_reasons,
    "product_batches":    fill_product_batches,
    "orders":             fill_orders_payments_returns,
    "waste":              fill_waste_records,
    "stockopname":        fill_stockopname,
    "journals":           fill_journals,
    "ap_ar":              fill_ap_ar,
    "vouchers":           fill_payment_vouchers,
}


def run(section="all", dry_run=True, verbose=True, debug_models=False):
    t0 = time_mod.time()
    print("\n" + "═" * 70)
    print("  KAFE NUSANTARA — Fill Empty Tables v2 [PATCHED]")
    print("═" * 70)
    print(f"  Mode    : {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"  Section : {section}")

    if debug_models:
        _inspect_models()

    print("\n  Model resolution (by db_table):")
    missing = []
    for key, model in M.items():
        status = f"✓ {model.__name__} ({model._meta.app_label})" if model else "✗ NOT FOUND"
        if not model:
            missing.append(key)
        print(f"    {key:<15} {status}")

    if missing:
        print(f"\n  ⚠  Models tidak ditemukan: {missing}")

    warm_cache(verbose=verbose)

    sections_to_run = (
        list(SECTION_MAP.keys()) if section == "all" else [section]
    )

    results = {}
    for sec in sections_to_run:
        fn = SECTION_MAP.get(sec)
        if not fn:
            print(f"\n  ⚠  Section '{sec}' tidak dikenal")
            continue
        print(f"\n  ▶ [{sec}]")
        try:
            results[sec] = fn(dry_run=dry_run)
        except Exception as e:
            import traceback
            print(f"  ✗ ERROR di section {sec}: {e}")
            if verbose:
                traceback.print_exc()
            results[sec] = f"ERROR"

    elapsed = time_mod.time() - t0
    print("\n" + "═" * 70)
    print(f"  SELESAI dalam {elapsed:.1f}s")
    print("─" * 70)
    for sec, res in results.items():
        print(f"  {sec:<25} {str(res)}")
    print("═" * 70 + "\n")
    return results


try:
    from django.core.management.base import BaseCommand

    class Command(BaseCommand):
        help = "Fill empty tables v2 [PATCHED] — fixed orders/payments, journals, vouchers"

        def add_arguments(self, parser):
            parser.add_argument("--execute", action="store_true", default=False)
            parser.add_argument("--section", default="all")
            parser.add_argument("--debug-models", action="store_true")
            parser.add_argument("--quiet", action="store_true")

        def handle(self, *args, **opts):
            run(
                section=opts["section"],
                dry_run=not opts["execute"],
                verbose=not opts["quiet"],
                debug_models=opts["debug_models"],
            )
except ImportError:
    pass

if __name__ == "__main__":
    section       = "all"
    dry_run       = True
    debug_models  = False
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--execute":       dry_run = False
        elif a == "--debug-models": debug_models = True
        elif a == "--section" and i + 1 < len(args): section = args[i + 1]
        elif a.startswith("--section="): section = a.split("=", 1)[1]
    run(section=section, dry_run=dry_run, debug_models=debug_models)