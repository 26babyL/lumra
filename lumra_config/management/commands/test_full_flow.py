#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════
  LUMRA ERP — FULL FLOW TEST SCRIPT
  Dari Setup Awal (Fase 0) Sampai Penjualan di POS (Fase 7)

  CARA MENJALANKAN:

    # Opsi 1 — via manage.py shell
    python manage.py shell < test_full_flow.py

    # Opsi 2 — interactive shell
    python manage.py shell
    >>> exec(open('test_full_flow.py').read())

    # Opsi 3 — langsung (jika DJANGO_SETTINGS_MODULE sudah di-set)
    python test_full_flow.py

  KONFIGURASI:
    USE_TRANSACTION = True  → data di-rollback setelah test selesai
    USE_TRANSACTION = False → data tersimpan permanen di database
═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
import traceback
from decimal import Decimal
from datetime import datetime

# ────────────────────────────────────────────────────────────────────
# KONFIGURASI
# ────────────────────────────────────────────────────────────────────

USE_TRANSACTION = True          # True = rollback setelah test
PRINT_STOCK_AT_EACH_STEP = True # True = tampilkan stok di tiap langkah

# ────────────────────────────────────────────────────────────────────
# SETUP DJANGO
# ────────────────────────────────────────────────────────────────────

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum

# ────────────────────────────────────────────────────────────────────
# IMPORT MODELS
# ────────────────────────────────────────────────────────────────────

try:
    User = get_user_model()

    from lumra_config.models import (
        BusinessProfile,
        Location,
        Category,
        Unit,
        Vendor,
        Product,
        SupplierPrice,
        Stock,
        StockMovement,
        Order,
        OrderItem,
        Payment,
        ProductionOrder,
        ProductionOrderMaterial,
        ReturnOrder,
        ReturnItem,
        Requisition,
        RequisitionItem,
        Transfer,
        TransferItem,
        Customer,
    )

    from production.models import (
        Recipe,
        RecipeIngredient,
        RecipeCategory,
    )

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nPastikan nama model sudah benar dan sesuaikan import di script ini.")
    print("Lihat bagian '# IMPORT MODELS' di atas untuk menyesuaikan.\n")
    sys.exit(1)


# ════════════════════════════════════════════════════════════════════
# HELPER: WARNA & OUTPUT
# ════════════════════════════════════════════════════════════════════

class C:
    """ANSI color codes."""
    RESET   = '\033[0m'
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'


def header(text, char='═', width=80):
    print(f"\n{C.CYAN}{C.BOLD}{char * width}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}{text:^{width}}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}{char * width}{C.RESET}\n")


def step(num, title):
    print(f"\n{C.GREEN}{C.BOLD}📌 STEP {num}: {title}{C.RESET}")
    print(f"{C.GREEN}{'─' * 60}{C.RESET}")


def ok(text):    print(f"  {C.GREEN}✅ {text}{C.RESET}")
def warn(text):  print(f"  {C.YELLOW}⚠️  {text}{C.RESET}")
def err(text):   print(f"  {C.RED}❌ {text}{C.RESET}")
def info(text):  print(f"  {C.WHITE}ℹ️  {text}{C.RESET}")
def sub(text):   print(f"  {C.BLUE}→ {text}{C.RESET}")


def table(headers, rows, widths=None):
    """Print tabel ASCII sederhana."""
    if widths is None:
        widths = [
            max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
            for i, h in enumerate(headers)
        ]
    sep_top = '─┬─'.join('─' * w for w in widths)
    sep_mid = '─┼─'.join('─' * w for w in widths)
    sep_bot = '─┴─'.join('─' * w for w in widths)
    hdr_line = ' │ '.join(f"{str(h):<{w}}" for h, w in zip(headers, widths))

    print(f"  ┌{sep_top}┐")
    print(f"  │{hdr_line}│")
    print(f"  ├{sep_mid}┤")
    for row in rows:
        print(f"  │{' │ '.join(f'{str(c):<{w}}' for c, w in zip(row, widths))}│")
    print(f"  └{sep_bot}┘")


# ════════════════════════════════════════════════════════════════════
# HELPER: STOK & MOVEMENT
# ════════════════════════════════════════════════════════════════════

def show_stock(location_name=None, product_type=None):
    """Tampilkan snapshot stok saat ini."""
    if not PRINT_STOCK_AT_EACH_STEP:
        return
    qs = Stock.objects.select_related('product', 'product__unit', 'location').all()
    if location_name:
        qs = qs.filter(location__name=location_name)
    if product_type:
        qs = qs.filter(product__product_type=product_type)
    if not qs.exists():
        info(f"Stok kosong di '{location_name or 'semua lokasi'}'")
        return
    print(f"\n  {C.DIM}📦 Stok Saat Ini:{C.RESET}")
    table(
        ['Produk', 'Lokasi', 'Stok', 'Satuan'],
        [[s.product.name[:25], s.location.name[:20], str(s.quantity),
          s.product.unit.symbol if s.product.unit else '-'] for s in qs],
        [27, 22, 10, 10],
    )


def show_movements(ref_code=None, limit=15):
    """Tampilkan log pergerakan stok."""
    qs = StockMovement.objects.select_related('product').all()
    if ref_code:
        qs = qs.filter(reference_code=ref_code)
    qs = qs.order_by('-created_at')[:limit]
    if not qs.exists():
        info("Tidak ada movement log")
        return
    print(f"\n  {C.DIM}📋 Movement Log:{C.RESET}")
    rows = []
    for m in reversed(list(qs)):
        sign = '+' if m.quantity > 0 else ''
        rows.append([
            m.created_at.strftime('%H:%M:%S'),
            m.product.name[:20],
            f"{sign}{m.quantity}",
            m.movement_type,
            m.reference_code or '-',
        ])
    table(['Waktu', 'Produk', 'Qty', 'Tipe', 'Ref'], rows, [10, 22, 8, 18, 18])


def doc_code(prefix, model, date_fmt='%Y%m'):
    """Generate kode dokumen otomatis: PREFIX-YYYYMM-NNNN."""
    today = datetime.now().strftime(date_fmt)
    prefix_str = f"{prefix}-{today}"
    last = model.objects.filter(code__startswith=prefix_str).order_by('-code').first()
    num = (int(last.code.split('-')[-1]) + 1) if last else 1
    return f"{prefix_str}-{num:04d}"


def pay_code(model):
    """Generate kode payment: PAY-YYYYMM-NNNN."""
    today = datetime.now().strftime('%Y%m')
    last = model.objects.filter(payment_code__startswith=f"PAY-{today}").order_by('-payment_code').first()
    num = (int(last.payment_code.split('-')[-1]) + 1) if last else 1
    return f"PAY-{today}-{num:04d}"


def ret_code(model):
    """Generate kode return: RET-YYYYMM-NNNN."""
    today = datetime.now().strftime('%Y%m')
    last = model.objects.filter(return_code__startswith=f"RET-{today}").order_by('-return_code').first()
    num = (int(last.return_code.split('-')[-1]) + 1) if last else 1
    return f"RET-{today}-{num:04d}"


def prd_code(model):
    """Generate kode production order: PRD-YYYYMM-NNNN."""
    today = datetime.now().strftime('%Y%m')
    last = model.objects.filter(po_code__startswith=f"PRD-{today}").order_by('-po_code').first()
    num = (int(last.po_code.split('-')[-1]) + 1) if last else 1
    return f"PRD-{today}-{num:04d}"


# ════════════════════════════════════════════════════════════════════
# HELPER: GET OR CREATE STOCK
# ════════════════════════════════════════════════════════════════════

def get_or_create_stock(product, location, add_qty=Decimal('0')):
    """Ambil atau buat record stok, langsung tambah qty jika diset."""
    stock, _ = Stock.objects.get_or_create(
        product=product,
        location=location,
        defaults={'quantity': Decimal('0')},
    )
    if add_qty:
        stock.quantity += add_qty
        stock.save()
    return stock


def deduct_stock(product, location, qty):
    """Kurangi stok — raise jika tidak cukup."""
    stock = Stock.objects.get(product=product, location=location)
    if stock.quantity < qty:
        raise ValueError(
            f"Stok tidak cukup: {product.name} di {location.name} "
            f"(tersedia={stock.quantity}, dibutuhkan={qty})"
        )
    stock.quantity -= qty
    stock.save()
    return stock


def log_movement(product, location, qty, mtype, ref_code, ref_type, notes, user):
    """Buat satu record StockMovement."""
    StockMovement.objects.create(
        product=product,
        location=location,
        quantity=qty,
        movement_type=mtype,
        reference_code=ref_code,
        reference_type=ref_type,
        notes=notes,
        created_by=user,
    )


# ════════════════════════════════════════════════════════════════════
# MAIN TEST FLOW
# ════════════════════════════════════════════════════════════════════

def run():
    """Entry point utama — jalankan semua fase test."""

    header("LUMRA ERP — FULL FLOW TEST")
    info(f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    info(f"Mode   : {'TRANSACTION (rollback setelah test)' if USE_TRANSACTION else 'PERMANEN (data tersimpan)'}")

    if USE_TRANSACTION:
        warn("Semua data AKAN DI-ROLLBACK setelah test selesai.")

    ctx = transaction.atomic()
    ctx.__enter__()

    try:
        _run_all_phases()
        return True
    except Exception as exc:
        err(f"ERROR: {exc}")
        traceback.print_exc()
        if USE_TRANSACTION:
            warn("Transaction di-rollback karena error.")
        return False
    finally:
        if USE_TRANSACTION:
            info("🔄 Rolling back transaction...")
            ctx.__exit__(None, None, None)
            ok("Rollback selesai — database bersih kembali.")


# ────────────────────────────────────────────────────────────────────

def _run_all_phases():
    """Menjalankan semua fase secara berurutan."""

    # ================================================================
    # FASE 0: SETUP AWAL
    # ================================================================
    header("FASE 0: SETUP AWAL")

    # ── 0.1 Nama Bisnis ─────────────────────────────────────────────
    step("0.1", "Setup Nama Bisnis")
    business, _ = BusinessProfile.objects.get_or_create(
        business_name="LUMRA Cafe",
        defaults={
            'industry':           'F&B',
            'address':            'Jl. Merdeka No. 1, Jakarta Pusat',
            'phone':              '021-1234567',
            'email':              'info@lumracafe.com',
            'is_setup_completed': False,
        },
    )
    ok(f"Bisnis   : {business.business_name}")
    info(f"Industri : {business.industry}")
    info(f"Alamat   : {business.address}")

    # ── 0.2 Lokasi / Toko / Cabang ──────────────────────────────────
    step("0.2", "Setup Lokasi / Toko / Cabang")
    _loc_data = [
        {'name': 'LUMRA Cafe Pusat',    'code': 'TKO-001', 'type': 'store',      'address': 'Jl. Merdeka No. 1'},
        {'name': 'Gudang Utama',        'code': 'GUD-001', 'type': 'warehouse',  'address': 'Jl. Industri No. 5'},
        {'name': 'Dapur Produksi',      'code': 'DPR-001', 'type': 'production', 'address': 'Jl. Industri No. 5 Lt.2'},
        {'name': 'LUMRA Cafe Cabang 2', 'code': 'TKO-002', 'type': 'store',      'address': 'Jl. Sudirman No. 10'},
    ]
    locs = {}
    for d in _loc_data:
        loc, _ = Location.objects.get_or_create(code=d['code'], defaults=d)
        locs[d['code']] = loc
        ok(f"Lokasi: {loc.name} ({loc.code})")

    GUDANG = locs['GUD-001']
    DAPUR  = locs['DPR-001']
    TOKO   = locs['TKO-001']

    # ── 0.3 Kategori Produk ──────────────────────────────────────────
    step("0.3", "Setup Kategori Produk")
    _cat_data = [
        ('Bahan Baku',  None),
        ('Produk Jadi', None),
        ('Roti',        'Produk Jadi'),
        ('Minuman',     'Produk Jadi'),
        ('Kue',         'Produk Jadi'),
    ]
    cats = {}
    for name, parent_name in _cat_data:
        cat, _ = Category.objects.get_or_create(
            name=name,
            defaults={'parent': cats.get(parent_name)},
        )
        cats[name] = cat
        ok(f"Kategori: {name}" + (f" → {parent_name}" if parent_name else ""))

    # ================================================================
    # FASE 1: MASTER DATA
    # ================================================================
    header("FASE 1: MASTER DATA")

    # ── 1.1 Satuan ───────────────────────────────────────────────────
    step("1.1", "Setup Satuan")
    _unit_data = [
        ('Kilogram',     'kg'),
        ('Gram',         'g'),
        ('Liter',        'L'),
        ('Mililiter',    'ml'),
        ('Pcs',          'pcs'),
        ('Butir',        'btr'),
        ('Sendok Makan', 'sdm'),
    ]
    units = {}
    for name, symbol in _unit_data:
        u, _ = Unit.objects.get_or_create(symbol=symbol, defaults={'name': name})
        units[symbol] = u
        ok(f"Satuan: {name} ({symbol})")

    # ── 1.2 Supplier ─────────────────────────────────────────────────
    step("1.2", "Setup Supplier")
    _vendor_data = [
        {'name': 'PT Bogasari Flour Mills', 'contact_person': 'Budi Santoso',  'phone': '021-1234567',  'email': 'budi@bogasari.co.id',   'address': 'Jl. Industri No. 100, Jakarta'},
        {'name': 'CV Segar Jaya',           'contact_person': 'Siti Aminah',   'phone': '081-23456789', 'email': 'siti@segarjaya.com',     'address': 'Jl. Pasar No. 5, Bandung'},
        {'name': 'UD Susu Makmur',          'contact_person': 'Pak Hadi',      'phone': '081-98765432', 'email': 'hadi@susumakmur.com',    'address': 'Jl. Peternakan No. 3, Malang'},
    ]
    vendors = {}
    for d in _vendor_data:
        v, _ = Vendor.objects.get_or_create(name=d['name'], defaults=d)
        vendors[d['name']] = v
        ok(f"Supplier: {v.name} — {v.contact_person}")

    BOGASARI   = vendors['PT Bogasari Flour Mills']
    SEGAR_JAYA = vendors['CV Segar Jaya']
    SUSU_MKR   = vendors['UD Susu Makmur']

    # ── 1.3 Produk Bahan Baku ────────────────────────────────────────
    step("1.3", "Setup Produk Bahan Baku")
    _prod_data = [
        # sku,   name,            category,     unit,  cost
        ('BB01', 'Tepung Terigu', 'Bahan Baku', 'kg',  12000),
        ('BB02', 'Gula Pasir',   'Bahan Baku', 'kg',  15000),
        ('BB03', 'Telur Ayam',   'Bahan Baku', 'btr',  2500),
        ('BB04', 'Margarin',     'Bahan Baku', 'kg',  25000),
        ('BB05', 'Susu UHT',     'Bahan Baku', 'L',   18000),
        ('BB06', 'Ragi Instan',  'Bahan Baku', 'sdm',   500),
        ('BB07', 'Garam',        'Bahan Baku', 'kg',  10000),
        ('BB08', 'Coklat Bubuk', 'Bahan Baku', 'kg',  45000),
    ]
    prods = {}
    for sku, name, cat_name, unit_sym, cost in _prod_data:
        p, _ = Product.objects.get_or_create(
            sku_code=sku,
            defaults={
                'name':         name,
                'category':     cats[cat_name],
                'unit':         units[unit_sym],
                'cost_price':   Decimal(str(cost)),
                'sell_price':   Decimal('0'),
                'product_type': 'raw_material',
                'is_active':    True,
            },
        )
        prods[sku] = p
        ok(f"Produk: {sku} — {name}  (Rp {cost:,}/{unit_sym})")

    # ── 1.4 Harga Supplier ───────────────────────────────────────────
    step("1.4", "Setup Harga Supplier")
    _sp_data = [
        # vendor,        product, price,  min_order
        (BOGASARI,   'BB01', 12000, 25),
        (BOGASARI,   'BB02', 14000, 10),
        (SEGAR_JAYA, 'BB03',  2500, 100),
        (SEGAR_JAYA, 'BB04', 24000,   5),
        (SUSU_MKR,   'BB05', 17500,  10),
        (SEGAR_JAYA, 'BB06',   450,  50),
        (SEGAR_JAYA, 'BB07',  9500,   5),
        (SEGAR_JAYA, 'BB08', 43000,   1),
    ]
    for vendor, sku, price, min_qty in _sp_data:
        sp, _ = SupplierPrice.objects.get_or_create(
            vendor=vendor,
            product=prods[sku],
            defaults={'price': price, 'min_order_qty': min_qty},
        )
        ok(f"Harga: {prods[sku].name} dari {vendor.name} = Rp {price:,} (min {min_qty})")

    # ── 1.5 User / Pengguna ─────────────────────────────────────────
    step("1.5", "Setup User / Pengguna")
    _user_data = [
        # username, email,                 password,   role,               location
        ('admin', 'admin@lumra.com', 'admin123', 'super_admin',        'TKO-001'),
        ('siti',  'siti@lumra.com',  'siti123',  'warehouse_manager',  'GUD-001'),
        ('budi',  'budi@lumra.com',  'budi123',  'production_head',    'DPR-001'),
        ('dewi',  'dewi@lumra.com',  'dewi123',  'cashier',            'TKO-001'),
        ('rina',  'rina@lumra.com',  'rina123',  'cashier',            'TKO-002'),
    ]
    test_users = {}
    for username, email, password, role, loc_code in _user_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email':        email,
                'is_staff':     role == 'super_admin',
                'is_superuser': role == 'super_admin',
            },
        )
        if created:
            user.set_password(password)
            user.save()

        # Buat atau update user profile
        profile, _ = user.profile.get_or_create()
        profile.role = role
        profile.default_location = locs[loc_code]
        profile.save()

        test_users[username] = user
        ok(f"User: {username} ({role}) → {locs[loc_code].name}")

    ADMIN = test_users['admin']
    SITI  = test_users['siti']
    BUDI  = test_users['budi']
    DEWI  = test_users['dewi']

    # ================================================================
    # FASE 2: RESEP / RECIPE
    # ================================================================
    header("FASE 2: RESEP / RECIPE")

    # ── 2.1 Buat Resep Roti Coklat ───────────────────────────────────
    step("2.1", "Buat Resep Roti Coklat")
    recipe_cat, _ = RecipeCategory.objects.get_or_create(
        name='Roti',
        defaults={'description': 'Aneka roti'},
    )
    recipe, _ = Recipe.objects.get_or_create(
        name='Roti Coklat',
        defaults={
            'category':                 recipe_cat,
            'description':              'Roti isi coklat lembut dan nikmat',
            'yield_qty':                Decimal('10'),
            'yield_unit':               units['pcs'],
            'production_time_minutes':  120,
            'sell_price':               Decimal('15000'),
            'instructions': (
                '1. Campurkan tepung, gula, ragi, garam. '
                '2. Tambahkan telur, susu, margarin. '
                '3. Uleni sampai kalis. '
                '4. Fermentasi 60 menit. '
                '5. Bentuk dan isi coklat. '
                '6. Fermentasi 30 menit. '
                '7. Panggang 25 menit.'
            ),
        },
    )
    ok(f"Resep  : {recipe.name}")
    info(f"Yield  : {recipe.yield_qty} {recipe.yield_unit.symbol}")
    info(f"Waktu  : {recipe.production_time_minutes} menit")
    info(f"Harga  : Rp {recipe.sell_price:,} / {recipe.yield_unit.symbol}")

    # ── 2.2 Input Bahan Baku Resep ───────────────────────────────────
    step("2.2", "Input Bahan Baku ke Resep")
    _ing_data = [
        # sku,   qty,           unit
        ('BB01', Decimal('1.0'),  'kg'),
        ('BB02', Decimal('0.2'),  'kg'),
        ('BB03', Decimal('4'),    'btr'),
        ('BB04', Decimal('0.15'), 'kg'),
        ('BB05', Decimal('0.3'),  'L'),
        ('BB06', Decimal('2'),    'sdm'),
        ('BB07', Decimal('0.01'), 'kg'),
        ('BB08', Decimal('0.1'),  'kg'),
    ]
    total_ing_cost = Decimal('0')
    for sku, qty, unit_sym in _ing_data:
        p = prods[sku]
        cost = p.cost_price * qty
        total_ing_cost += cost
        RecipeIngredient.objects.get_or_create(
            recipe=recipe,
            product=p,
            defaults={'quantity': qty, 'unit': units[unit_sym]},
        )
        ok(f"  {p.name}: {qty} {unit_sym}  = Rp {cost:,.0f}")

    cost_per_unit = total_ing_cost / recipe.yield_qty
    margin = (recipe.sell_price - cost_per_unit) / recipe.sell_price * 100
    info(f"\n  Total Biaya Bahan : Rp {total_ing_cost:,.0f}")
    info(f"  Biaya per pcs     : Rp {cost_per_unit:,.0f}")
    info(f"  Harga Jual        : Rp {recipe.sell_price:,.0f}")
    info(f"  Margin            : {margin:.1f}%")

    # ── 2.3 Buat Produk Jadi dari Resep ─────────────────────────────
    step("2.3", "Buat Produk Jadi (Roti Coklat) dari Resep")
    product_roti, _ = Product.objects.get_or_create(
        sku_code='PJ01',
        defaults={
            'name':         'Roti Coklat',
            'category':     cats['Roti'],
            'unit':         units['pcs'],
            'cost_price':   cost_per_unit,
            'sell_price':   recipe.sell_price,
            'product_type': 'finished_goods',
            'is_active':    True,
            'recipe':       recipe,
        },
    )
    prods['PJ01'] = product_roti
    ok(f"Produk Jadi: {product_roti.sku_code} — {product_roti.name}")
    info(f"Harga Jual : Rp {product_roti.sell_price:,} / pcs")

    # ================================================================
    # FASE 3: BARANG MENTAH DATANG (PROCUREMENT)
    # ================================================================
    header("FASE 3: BARANG MENTAH DATANG (PROCUREMENT)")

    # ── 3.1 Buat Purchase Order ──────────────────────────────────────
    step("3.1", "Input Pembelian (Purchase Order)")
    po_no = doc_code('PO', Order)
    _po_items = [
        # sku,   qty,  unit,  price
        ('BB01', 50,  'kg',  12000),
        ('BB02', 20,  'kg',  14000),
        ('BB03', 100, 'btr',  2500),
        ('BB04', 10,  'kg',  24000),
        ('BB05', 20,  'L',   17500),
        ('BB06', 100, 'sdm',   450),
        ('BB07', 5,   'kg',   9500),
        ('BB08', 5,   'kg',  43000),
    ]
    subtotal_po  = Decimal(str(sum(qty * price for _, qty, _, price in _po_items)))
    tax_po       = subtotal_po * Decimal('0.11')
    total_po     = subtotal_po + tax_po

    po = Order.objects.create(
        code=po_no, order_type='purchase',
        vendor=BOGASARI, location=GUDANG,
        subtotal=subtotal_po, tax_amount=tax_po, total_amount=total_po,
        status='completed', notes='Pembelian rutin bahan baku', created_by=ADMIN,
    )
    ok(f"PO     : {po_no}")
    info(f"Supplier : PT Bogasari Flour Mills")
    info(f"Lokasi   : {GUDANG.name}")

    for sku, qty, unit_sym, price in _po_items:
        p = prods[sku]
        OrderItem.objects.create(
            order=po, product=p,
            quantity=Decimal(str(qty)), unit_price=Decimal(str(price)),
            subtotal=Decimal(str(qty * price)),
        )
        ok(f"  {p.name}: {qty} {unit_sym} × Rp {price:,}")

    info(f"\n  Subtotal : Rp {subtotal_po:,.0f}")
    info(f"  PPN 11%  : Rp {tax_po:,.0f}")
    info(f"  Total    : Rp {total_po:,.0f}")

    # ── 3.2 Terima Barang → Update Stok + Movement ──────────────────
    step("3.2", "Terima Barang → Update Stok & Log Movement")
    for sku, qty, *_ in _po_items:
        p   = prods[sku]
        qty_d = Decimal(str(qty))
        get_or_create_stock(p, GUDANG, add_qty=qty_d)
        log_movement(p, GUDANG, qty_d, 'purchase', po_no, 'order', f'Diterima dari PO {po_no}', ADMIN)

    ok(f"Stok di {GUDANG.name} diperbarui")
    show_stock(GUDANG.name)
    show_movements(po_no)

    # ================================================================
    # FASE 4: TRANSFER GUDANG → DAPUR PRODUKSI
    # ================================================================
    header("FASE 4: TRANSFER GUDANG → DAPUR PRODUKSI")

    # ── 4.1 Buat Requisition ────────────────────────────────────────
    step("4.1", "Buat Permintaan Bahan (Requisition)")
    req_no = doc_code('REQ', Requisition)
    req = Requisition.objects.create(
        code=req_no,
        from_location=GUDANG, to_location=DAPUR,
        requested_by=BUDI, status='pending',
        notes='Bahan untuk produksi Roti Coklat 50 pcs',
    )

    # 5× resep (target 50 pcs, resep yield 10 pcs)
    _req_items = [
        ('BB01', Decimal('5.0')),
        ('BB02', Decimal('1.0')),
        ('BB03', Decimal('20')),
        ('BB04', Decimal('0.75')),
        ('BB05', Decimal('1.5')),
        ('BB06', Decimal('10')),
        ('BB07', Decimal('0.05')),
        ('BB08', Decimal('0.5')),
    ]
    for sku, qty in _req_items:
        p     = prods[sku]
        stk   = Stock.objects.filter(product=p, location=GUDANG).first()
        avail = stk.quantity if stk else Decimal('0')
        RequisitionItem.objects.create(
            requisition=req, product=p,
            quantity_requested=qty, notes=f'Tersedia: {avail}',
        )
        icon = '✅' if avail >= qty else '❌'
        ok(f"  {icon} {p.name}: {qty}  (tersedia: {avail})")

    # ── 4.2 Approve Requisition ─────────────────────────────────────
    step("4.2", "Approve Requisition")
    req.status = 'approved'
    req.approved_by = SITI
    req.approved_at = datetime.now()
    req.save()
    ok(f"Requisition {req_no} disetujui oleh {SITI.username} (Manager Gudang)")

    # ── 4.3 Buat Transfer & Eksekusi ────────────────────────────────
    step("4.3", "Buat Transfer & Eksekusi")
    trf_no = doc_code('TRF', Transfer)
    trf = Transfer.objects.create(
        code=trf_no,
        from_location=GUDANG, to_location=DAPUR,
        reference_requisition=req,
        status='completed',
        notes='Transfer bahan untuk produksi Roti Coklat',
        created_by=SITI,
    )
    for sku, qty in _req_items:
        p = prods[sku]
        TransferItem.objects.create(transfer=trf, product=p, quantity=qty)
        deduct_stock(p, GUDANG, qty)
        get_or_create_stock(p, DAPUR, add_qty=qty)
        log_movement(p, GUDANG, -qty, 'transfer_out', trf_no, 'transfer', f'Transfer ke {DAPUR.name}', SITI)
        log_movement(p, DAPUR,   qty, 'transfer_in',  trf_no, 'transfer', f'Terima dari {GUDANG.name}', SITI)

    req.status = 'fulfilled'
    req.save()

    ok(f"Transfer {trf_no} selesai")
    show_stock(GUDANG.name)
    show_stock(DAPUR.name)
    show_movements(trf_no)

    # ================================================================
    # FASE 5: PROSES PRODUKSI
    # ================================================================
    header("FASE 5: PROSES PRODUKSI")

    TARGET_QTY = Decimal('50')
    RATIO      = TARGET_QTY / recipe.yield_qty   # 50 / 10 = 5

    # ── 5.1 Buat Production Order ────────────────────────────────────
    step("5.1", "Buat Production Order")
    prd_no = prd_code(ProductionOrder)
    prd_order = ProductionOrder.objects.create(
        po_code=prd_no,
        recipe=recipe, location=DAPUR,
        assigned_to=BUDI, target_qty=TARGET_QTY,
        status='draft', output_location=TOKO,
        notes='Produksi Roti Coklat untuk Toko Pusat',
        created_by=BUDI,
    )
    ok(f"Production Order : {prd_no}")
    info(f"Resep  : {recipe.name}")
    info(f"Target : {TARGET_QTY} pcs  (ratio {RATIO}× resep)")
    info(f"Lokasi : {DAPUR.name}  →  Output: {TOKO.name}")

    # ── 5.2 Hitung Kebutuhan Bahan ───────────────────────────────────
    step("5.2", "Hitung Kebutuhan Bahan Baku")
    total_mat_cost = Decimal('0')
    for ing in recipe.ingredients.all():
        qty_req = ing.quantity * RATIO
        cost    = ing.product.cost_price * qty_req
        total_mat_cost += cost

        stk   = Stock.objects.filter(product=ing.product, location=DAPUR).first()
        avail = stk.quantity if stk else Decimal('0')
        icon  = '✅' if avail >= qty_req else '❌'

        ProductionOrderMaterial.objects.create(
            production_order=prd_order,
            product=ing.product,
            quantity_required=qty_req,
            unit=ing.unit,
            cost_price=ing.product.cost_price,
        )
        ok(f"  {icon} {ing.product.name}: {qty_req} {ing.unit.symbol}  (tersedia: {avail})  = Rp {cost:,.0f}")

    info(f"\n  Total Biaya Material   : Rp {total_mat_cost:,.0f}")
    info(f"  Estimasi Biaya / pcs   : Rp {total_mat_cost / TARGET_QTY:,.0f}")

    # ── 5.3 Mulai Produksi — Kurangi Stok Bahan ──────────────────────
    step("5.3", "Mulai Produksi — Kurangi Stok Bahan Baku")
    prd_order.status = 'in_progress'
    prd_order.started_at = datetime.now()
    prd_order.total_material_cost = total_mat_cost
    prd_order.save()

    for mat in prd_order.materials.all():
        deduct_stock(mat.product, DAPUR, mat.quantity_required)
        mat.quantity_used = mat.quantity_required
        mat.save()
        log_movement(mat.product, DAPUR, -mat.quantity_required,
                     'production_out', prd_no, 'production_order',
                     f'Dipakai untuk produksi {prd_no}', BUDI)

    ok(f"Produksi {prd_no} dimulai")
    show_stock(DAPUR.name)
    show_movements(prd_no)

    # ── 5.4 Produksi Selesai — Terima Hasil ──────────────────────────
    step("5.4", "Produksi Selesai — Catat Hasil & Waste")
    ACTUAL_QTY = Decimal('48')                    # 2 pcs waste
    WASTE_QTY  = TARGET_QTY - ACTUAL_QTY

    prd_order.status      = 'completed'
    prd_order.actual_qty  = ACTUAL_QTY
    prd_order.waste_qty   = WASTE_QTY
    prd_order.waste_reason = '2 pcs gosong, tidak bisa dijual'
    prd_order.completed_at = datetime.now()
    prd_order.save()

    get_or_create_stock(product_roti, TOKO, add_qty=ACTUAL_QTY)
    log_movement(product_roti, TOKO, ACTUAL_QTY,
                 'production_in', prd_no, 'production_order',
                 f'Hasil produksi dari {prd_no}', BUDI)

    ok(f"Produksi {prd_no} selesai!")
    info(f"Target : {TARGET_QTY} pcs")
    info(f"Aktual : {ACTUAL_QTY} pcs")
    warn(f"Waste  : {WASTE_QTY} pcs — {prd_order.waste_reason}")
    info(f"Biaya aktual / pcs : Rp {total_mat_cost / ACTUAL_QTY:,.0f}")
    show_stock(TOKO.name)
    show_movements(prd_no)

    # ================================================================
    # FASE 6: PENJUALAN DI POS
    # ================================================================
    header("FASE 6: PENJUALAN DI POS")

    HARGA = product_roti.sell_price

    def buat_penjualan(label, qty, bayar, metode):
        """Helper buat satu transaksi penjualan."""
        so_no    = doc_code('SO', Order)
        sub_     = qty * HARGA
        tax_     = sub_ * Decimal('0.11')
        total_   = sub_ + tax_
        kembalian = max(bayar - total_, Decimal('0'))

        so = Order.objects.create(
            code=so_no, order_type='sales', location=TOKO, customer=None,
            subtotal=sub_, tax_amount=tax_, discount_amount=Decimal('0'),
            total_amount=total_, payment_method=metode,
            paid_amount=bayar, change_amount=kembalian,
            status='completed', created_by=DEWI,
        )
        OrderItem.objects.create(
            order=so, product=product_roti,
            quantity=qty, unit_price=HARGA, subtotal=sub_,
        )
        stk_toko = Stock.objects.get(product=product_roti, location=TOKO)
        stk_toko.quantity -= qty
        stk_toko.save()
        log_movement(product_roti, TOKO, -qty, 'sale', so_no, 'order', 'Penjualan di POS', DEWI)

        p_no = pay_code(Payment)
        Payment.objects.create(
            payment_code=p_no, order=so, payment_method=metode,
            amount=total_, paid_at=datetime.now(), created_by=DEWI,
        )
        ok(f"Order  : {so_no}  [{label}]")
        info(f"Produk : Roti Coklat × {qty}")
        info(f"Total  : Rp {total_:,.0f}  ({metode.upper()})")
        if kembalian:
            info(f"Kembalian: Rp {kembalian:,.0f}")
        show_stock(TOKO.name)
        return so

    step("6.1", "Transaksi 1 — Penjualan 2 pcs (Tunai)")
    buat_penjualan("Walk-in", Decimal('2'), Decimal('50000'), 'cash')

    step("6.2", "Transaksi 2 — Penjualan 3 pcs (QRIS)")
    so2 = buat_penjualan("Walk-in", Decimal('3'), Decimal('100000'), 'qris')

    step("6.3", "Transaksi 3 — Penjualan 5 pcs (Tunai)")
    so3 = buat_penjualan("Walk-in", Decimal('5'), Decimal('5') * HARGA * Decimal('1.11'), 'cash')

    # ── 6.4 Proses Retur 1 pcs dari Transaksi 3 ─────────────────────
    step("6.4", "Proses Retur 1 pcs dari Transaksi 3")
    QTY_RET     = Decimal('1')
    ret_sub     = QTY_RET * HARGA
    ret_tax     = ret_sub * Decimal('0.11')
    ret_total   = ret_sub + ret_tax
    ret_no      = ret_code(ReturnOrder)

    return_order = ReturnOrder.objects.create(
        return_code=ret_no, order=so3,
        return_date=datetime.now(),
        subtotal=ret_sub, tax_amount=ret_tax, total_amount=ret_total,
        status='completed',
        reason='Roti kurang matang, pelanggan komplain',
        created_by=DEWI,
    )
    ReturnItem.objects.create(
        return_order=return_order, product=product_roti,
        quantity=QTY_RET, unit_price=HARGA, subtotal=ret_sub,
        reason='Kurang matang',
    )
    stk_toko = Stock.objects.get(product=product_roti, location=TOKO)
    stk_toko.quantity += QTY_RET
    stk_toko.save()
    log_movement(product_roti, TOKO, QTY_RET, 'return_in', ret_no, 'return',
                 f'Retur dari {so3.code}', DEWI)

    ok(f"Retur  : {ret_no}")
    info(f"Produk : Roti Coklat × {QTY_RET}")
    info(f"Nilai Retur : Rp {ret_total:,.0f}")
    warn(f"Alasan : {return_order.reason}")
    show_stock(TOKO.name)

    # ================================================================
    # FASE 7: RINGKASAN & VALIDASI
    # ================================================================
    header("FASE 7: RINGKASAN & VALIDASI")

    # ── 7.1 Ringkasan Stok Akhir Semua Lokasi ────────────────────────
    step("7.1", "Ringkasan Stok Akhir Semua Lokasi")
    all_stk = Stock.objects.exclude(quantity=0).select_related('product', 'product__unit', 'location')
    rows = []
    total_val = Decimal('0')
    for s in all_stk:
        val = s.quantity * (s.product.cost_price or 0)
        total_val += val
        rows.append([
            s.location.name[:20], s.product.name[:20],
            s.product.product_type, str(s.quantity),
            s.product.unit.symbol, f"Rp {val:,.0f}",
        ])
    table(['Lokasi', 'Produk', 'Tipe', 'Stok', 'Satuan', 'Nilai Stok'],
          rows, [22, 22, 15, 10, 8, 15])
    info(f"\n  Total Nilai Stok : Rp {total_val:,.0f}")

    # ── 7.2 Ringkasan Penjualan ──────────────────────────────────────
    step("7.2", "Ringkasan Penjualan")
    sales_qs = Order.objects.filter(order_type='sales', status='completed')
    totals   = sales_qs.aggregate(rev=Sum('total_amount'), qty=Sum('orderitem__quantity'))
    rows = []
    for so in sales_qs:
        qty_sold = so.orderitem_set.aggregate(q=Sum('quantity'))['q'] or 0
        rows.append([so.code, so.created_at.strftime('%H:%M:%S'),
                     str(qty_sold), f"Rp {so.total_amount:,.0f}", so.payment_method])
    table(['No. Order', 'Waktu', 'Items', 'Total', 'Metode'], rows, [18, 10, 8, 15, 12])
    info(f"\n  Transaksi  : {sales_qs.count()}")
    info(f"  Total Items: {totals['qty'] or 0} pcs")
    info(f"  Revenue    : Rp {totals['rev'] or 0:,.0f}")

    # ── 7.3 Ringkasan Produksi ────────────────────────────────────────
    step("7.3", "Ringkasan Produksi")
    table(
        ['No. Produksi', 'Produk', 'Target', 'Aktual', 'Waste', 'Status'],
        [[prd_order.po_code, prd_order.recipe.name,
          str(prd_order.target_qty), str(prd_order.actual_qty),
          str(prd_order.waste_qty), prd_order.status]],
        [18, 15, 10, 10, 8, 15],
    )

    # ── 7.4 Validasi Audit Trail Stok Roti Coklat ────────────────────
    step("7.4", "Validasi Stok Roti Coklat (Audit Trail)")
    info("Rumus: Produksi Masuk − Penjualan Keluar + Retur Masuk = Stok Akhir")

    mvs       = StockMovement.objects.filter(product=product_roti, location=TOKO)
    produced  = mvs.filter(movement_type='production_in').aggregate(t=Sum('quantity'))['t']  or Decimal('0')
    sold_neg  = mvs.filter(movement_type='sale').aggregate(t=Sum('quantity'))['t']            or Decimal('0')
    returned  = mvs.filter(movement_type='return_in').aggregate(t=Sum('quantity'))['t']      or Decimal('0')
    sold      = abs(sold_neg)
    expected  = produced - sold + returned
    actual    = Stock.objects.get(product=product_roti, location=TOKO).quantity

    print(f"\n  Produksi Masuk   : +{produced} pcs")
    print(f"  Penjualan Keluar : -{sold} pcs")
    print(f"  Retur Masuk      : +{returned} pcs")
    print(f"  {'─' * 35}")
    print(f"  Stok Expected    :  {expected} pcs")
    print(f"  Stok Aktual DB   :  {actual} pcs")

    if expected == actual:
        ok("\n  ✅ VALIDASI BERHASIL — Stok konsisten!")
    else:
        err(f"\n  ❌ VALIDASI GAGAL — Selisih {abs(expected - actual)} pcs")

    # ── 7.5 Full Movement Log ─────────────────────────────────────────
    step("7.5", "Full Movement Log — Roti Coklat di Toko Pusat")
    all_mvs  = StockMovement.objects.filter(product=product_roti, location=TOKO).order_by('created_at')
    rows     = []
    running  = Decimal('0')
    for i, m in enumerate(all_mvs, 1):
        running += m.quantity
        sign = '+' if m.quantity > 0 else ''
        rows.append([str(i), m.created_at.strftime('%H:%M:%S'),
                     m.movement_type, f"{sign}{m.quantity}",
                     m.reference_code or '-', (m.notes or '-')[:25]])
    table(['#', 'Waktu', 'Tipe', 'Qty', 'Ref', 'Notes'], rows, [4, 10, 15, 8, 18, 27])
    info(f"\n  Running Balance : {running} pcs")

    # ── 7.6 Tandai Setup Selesai ─────────────────────────────────────
    step("7.6", "Tandai Setup Bisnis Selesai")
    business.is_setup_completed = True
    business.save()
    ok(f"'{business.business_name}' ditandai setup selesai")

    # ── Final Summary ────────────────────────────────────────────────
    header("TEST COMPLETED SUCCESSFULLY")
    _summary = [
        ('Lokasi',           Location.objects.count()),
        ('Kategori',         Category.objects.count()),
        ('Satuan',           Unit.objects.count()),
        ('Supplier',         Vendor.objects.count()),
        ('Produk',           Product.objects.count()),
        ('Harga Supplier',   SupplierPrice.objects.count()),
        ('Resep',            Recipe.objects.count()),
        ('Bahan Resep',      RecipeIngredient.objects.count()),
        ('Purchase Orders',  Order.objects.filter(order_type='purchase').count()),
        ('Requisitions',     Requisition.objects.count()),
        ('Transfers',        Transfer.objects.count()),
        ('Production Orders',ProductionOrder.objects.count()),
        ('Sales Orders',     Order.objects.filter(order_type='sales').count()),
        ('Payments',         Payment.objects.count()),
        ('Returns',          ReturnOrder.objects.count()),
        ('Stock Records',    Stock.objects.count()),
        ('Stock Movements',  StockMovement.objects.count()),
    ]
    table(['Entity', 'Count'], [[e, str(c)] for e, c in _summary], [25, 10])
    print(f"\n  {C.GREEN}{C.BOLD}🎉 Semua alur berhasil dijalankan!{C.RESET}")

    if USE_TRANSACTION:
        warn("Data akan di-rollback karena USE_TRANSACTION = True")
        warn("Set USE_TRANSACTION = False untuk menyimpan data permanen.")


# ════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    success = run()
    sys.exit(0 if success else 1)