#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════
  LUMRA ERP — FULL FLOW TEST SCRIPT
  Dari Setup Awal Sampai Penjualan di POS
═══════════════════════════════════════════════════════════════════════

Cara menjalankan:
  
  cd /path/to/your/project
  python manage.py shell < test_full_flow.py

  ATAU
  
  python manage.py shell
  >>> exec(open('test_full_flow.py').read())

  ATAU (jika ingin rollback setelah selesai):
  
  Edit bagian USE_TRANSACTION di bawah menjadi True
═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
from decimal import Decimal
from datetime import datetime, date

# ============================================================
# KONFIGURASI
# ============================================================
USE_TRANSACTION = True  # Set True untuk rollback setelah test
PRINT_STOCK_AT_EACH_STEP = True  # Print stok di setiap langkah

# ============================================================
# SETUP DJANGO
# ============================================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, F

# ============================================================
# IMPORT MODELS — SESUAIKAN DENGAN PROJECT KAMU
# ============================================================
try:
    User = get_user_model()
    
    # Import dari app lumra_config
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
    
    # Import dari app production
    from production.models import (
        Recipe,
        RecipeIngredient,
        RecipeCategory,
    )
    
    IMPORTS_OK = True
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPastikan models sudah dibuat dengan nama yang benar.")
    print("Sesuaikan import statements di script ini.")
    IMPORTS_OK = False
    # Exit jika import gagal
    sys.exit(1)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def print_header(text, char='=', width=80):
    """Print header dengan warna"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{char * width}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^{width}}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{char * width}{Colors.RESET}\n")


def print_step(step_num, title):
    """Print step number dan title"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}📌 STEP {step_num}: {title}{Colors.RESET}")
    print(f"{Colors.GREEN}{'─' * 60}{Colors.RESET}")


def print_substep(text):
    """Print substep"""
    print(f"  {Colors.BLUE}→ {text}{Colors.RESET}")


def print_success(text):
    """Print success message"""
    print(f"  {Colors.GREEN}✅ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"  {Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"  {Colors.RED}❌ {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"  {Colors.WHITE}ℹ️  {text}{Colors.RESET}")


def print_data_table(headers, rows, col_widths=None):
    """Print formatted table"""
    if col_widths is None:
        col_widths = [max(len(str(h)), max(len(str(r[i])) for r in rows) if rows else 0) 
                      for i, h in enumerate(headers)]
    
    # Header
    header_line = ' │ '.join(f"{str(h):<{w}}" for h, w in zip(headers, col_widths))
    separator = '─┼─'.join('─' * w for w in col_widths)
    
    print(f"  ┌{'─┬─'.join('─' * w for w in col_widths)}┐")
    print(f"  │{header_line}│")
    print(f"  ├{separator}┤")
    
    # Rows
    for row in rows:
        row_line = ' │ '.join(f"{str(cell):<{w}}" for cell, w in zip(row, col_widths))
        print(f"  │{row_line}│")
    
    print(f"  └{'─┴─'.join('─' * w for w in col_widths)}┘")


def print_stock_snapshot(location_name=None, product_type=None):
    """Print snapshot stok saat ini"""
    if not PRINT_STOCK_AT_EACH_STEP:
        return
    
    stocks = Stock.objects.all()
    
    if location_name:
        stocks = stocks.filter(location__name=location_name)
    
    if product_type:
        stocks = stocks.filter(product__product_type=product_type)
    
    if not stocks.exists():
        print_info(f"Stok kosong di {location_name or 'semua lokasi'}")
        return
    
    headers = ['Produk', 'Lokasi', 'Stok', 'Satuan']
    rows = []
    
    for stock in stocks:
        rows.append([
            stock.product.name[:25],
            stock.location.name[:20],
            str(stock.quantity),
            stock.product.unit.name if stock.product.unit else '-'
        ])
    
    print(f"\n  {Colors.DIM}📦 Stok Saat Ini:{Colors.RESET}")
    print_data_table(headers, rows, [27, 22, 10, 10])


def print_stock_movement_log(reference_code=None, limit=10):
    """Print log pergerakan stok"""
    movements = StockMovement.objects.all()
    
    if reference_code:
        movements = movements.filter(reference_code=reference_code)
    
    movements = movements[:limit]
    
    if not movements.exists():
        print_info("Tidak ada movement log")
        return
    
    headers = ['Waktu', 'Produk', 'Qty', 'Tipe', 'Ref']
    rows = []
    
    for m in movements:
        sign = '+' if m.quantity > 0 else ''
        rows.append([
            m.created_at.strftime('%H:%M:%S'),
            m.product.name[:20],
            f"{sign}{m.quantity}",
            m.movement_type,
            m.reference_code or '-'
        ])
    
    print(f"\n  {Colors.DIM}📋 Movement Log:{Colors.RESET}")
    print_data_table(headers, rows, [10, 22, 8, 15, 15])


def generate_code(prefix, model, date_format='%Y%m'):
    """Generate kode dokumen otomatis"""
    today = datetime.now().strftime(date_format)
    last = model.objects.filter(
        code__startswith=f"{prefix}-{today}"
    ).order_by('-code').first()
    
    if last:
        last_num = int(last.code.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}-{today}-{new_num:04d}"


# ============================================================
# MAIN TEST FLOW
# ============================================================

def run_full_flow_test():
    """Jalankan test alur lengkap"""
    
    print_header("LUMRA ERP — FULL FLOW TEST")
    print(f"  Waktu test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Transaction: {'ON (akan di-rollback)' if USE_TRANSACTION else 'OFF (data tersimpan)'}")
    
    if USE_TRANSACTION:
        print_warning("Mode transaksi AKTIF — semua data akan di-rollback setelah test")
    
    # Wrap in transaction jika diminta
    if USE_TRANSACTION:
        context = transaction.atomic()
        context.__enter__()
    
    try:
        # Track semua objek yang dibuat
        created = {}
        
        # ══════════════════════════════════════════════════════
        # FASE 0: SETUP AWAL
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 0: SETUP AWAL", '═')
        
        # ─── STEP 0.1: Nama Bisnis ───────────────────────────
        print_step("0.1", "Setup Nama Bisnis")
        
        business, created_flag = BusinessProfile.objects.get_or_create(
            business_name="LUMRA Cafe",
            defaults={
                'industry': 'F&B',
                'address': 'Jl. Merdeka No. 1, Jakarta Pusat',
                'phone': '021-1234567',
                'email': 'info@lumracafe.com',
                'is_setup_completed': False,
            }
        )
        created['business'] = business
        print_success(f"Bisnis: {business.business_name}")
        print_info(f"Industri: {business.industry}")
        print_info(f"Alamat: {business.address}")
        
        # ─── STEP 0.2: Nama Toko / Cabang ───────────────────
        print_step("0.2", "Setup Lokasi / Toko / Cabang")
        
        locations_data = [
            {'name': 'LUMRA Cafe Pusat', 'code': 'TKO-001', 'type': 'store', 'address': 'Jl. Merdeka No. 1'},
            {'name': 'Gudang Utama', 'code': 'GUD-001', 'type': 'warehouse', 'address': 'Jl. Industri No. 5'},
            {'name': 'Dapur Produksi', 'code': 'DPR-001', 'type': 'production', 'address': 'Jl. Industri No. 5 (Lt.2)'},
            {'name': 'LUMRA Cafe Cabang 2', 'code': 'TKO-002', 'type': 'store', 'address': 'Jl. Sudirman No. 10'},
        ]
        
        locations = {}
        for loc_data in locations_data:
            loc, _ = Location.objects.get_or_create(
                code=loc_data['code'],
                defaults=loc_data
            )
            locations[loc_data['code']] = loc
            print_success(f"Lokasi: {loc.name} ({loc.code})")
        
        created['locations'] = locations
        
        # ─── STEP 0.3: Kategori Produk ──────────────────────
        print_step("0.3", "Setup Kategori Produk")
        
        categories_data = [
            {'name': 'Bahan Baku', 'parent': None},
            {'name': 'Produk Jadi', 'parent': None},
            {'name': 'Roti', 'parent': 'Produk Jadi'},
            {'name': 'Minuman', 'parent': 'Produk Jadi'},
            {'name': 'Kue', 'parent': 'Produk Jadi'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            parent = None
            if cat_data['parent']:
                parent = categories.get(cat_data['parent'])
            
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'parent': parent}
            )
            categories[cat_data['name']] = cat
            parent_name = f" → {parent.name}" if parent else ""
            print_success(f"Kategori: {cat.name}{parent_name}")
        
        created['categories'] = categories
        
        # ══════════════════════════════════════════════════════
        # FASE 1: MASTER DATA
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 1: MASTER DATA", '═')
        
        # ─── STEP 1.1: Satuan ───────────────────────────────
        print_step("1.1", "Setup Satuan")
        
        units_data = [
            {'name': 'Kilogram', 'symbol': 'kg'},
            {'name': 'Gram', 'symbol': 'g'},
            {'name': 'Liter', 'symbol': 'L'},
            {'name': 'Mililiter', 'symbol': 'ml'},
            {'name': 'Pcs', 'symbol': 'pcs'},
            {'name': 'Butir', 'symbol': 'btr'},
            {'name': 'Sendok Makan', 'symbol': 'sdm'},
        ]
        
        units = {}
        for unit_data in units_data:
            unit, _ = Unit.objects.get_or_create(
                symbol=unit_data['symbol'],
                defaults=unit_data
            )
            units[unit_data['symbol']] = unit
            print_success(f"Satuan: {unit.name} ({unit.symbol})")
        
        created['units'] = units
        
        # ─── STEP 1.2: Supplier ─────────────────────────────
        print_step("1.2", "Setup Supplier")
        
        vendors_data = [
            {
                'name': 'PT Bogasari Flour Mills',
                'contact_person': 'Budi Santoso',
                'phone': '021-1234567',
                'email': 'budi@bogasari.co.id',
                'address': 'Jl. Industri No. 100, Jakarta'
            },
            {
                'name': 'CV Segar Jaya',
                'contact_person': 'Siti Aminah',
                'phone': '081-23456789',
                'email': 'siti@segarjaya.com',
                'address': 'Jl. Pasar No. 5, Bandung'
            },
            {
                'name': 'UD Susu Makmur',
                'contact_person': 'Pak Hadi',
                'phone': '081-98765432',
                'email': 'hadi@susumakmur.com',
                'address': 'Jl. Peternakan No. 3, Malang'
            },
        ]
        
        vendors = {}
        for vendor_data in vendors_data:
            vendor, _ = Vendor.objects.get_or_create(
                name=vendor_data['name'],
                defaults=vendor_data
            )
            vendors[vendor_data['name']] = vendor
            print_success(f"Supplier: {vendor.name} - {vendor.contact_person}")
        
        created['vendors'] = vendors
        
        # ─── STEP 1.3: Produk Bahan Baku ────────────────────
        print_step("1.3", "Setup Produk Bahan Baku")
        
        raw_materials_data = [
            {'sku': 'BB01', 'name': 'Tepung Terigu', 'category': 'Bahan Baku', 'unit': 'kg', 'cost_price': 12000, 'sell_price': 0, 'product_type': 'raw_material'},
            {'sku': 'BB02', 'name': 'Gula Pasir', 'category': 'Bahan Baku', 'unit': 'kg', 'cost_price': 15000, 'sell_price': 0, 'product_type': 'raw_material'},
            {'sku': 'BB03', 'name': 'Telur Ayam', 'category': 'Bahan Baku', 'unit': 'btr', 'cost_price': 2500, 'sell_price': 0, 'product_type': 'raw_material'},
            {'sku': 'BB04', 'name': 'Margarin', 'category': 'Bahan Baku', 'unit': 'kg', 'cost_price': 25000, 'sell_price': 0, 'product_type': 'raw_material'},
            {'sku': 'BB05', 'name': 'Susu UHT', 'category': 'Bahan Baku', 'unit': 'L', 'cost_price': 18000, 'sell_price': 0, 'product_type': 'raw_material'},
            {'sku': 'BB06', 'name': 'Ragi Instan', 'category': 'Bahan Baku', 'unit': 'sdm', 'cost_price': 500, 'sell_price': 0, 'product_type': 'raw_material'},
            {'sku': 'BB07', 'name': 'Garam', 'category': 'Bahan Baku', 'unit': 'kg', 'cost_price': 10000, 'sell_price': 0, 'product_type': 'raw_material'},
            {'sku': 'BB08', 'name': 'Coklat Bubuk', 'category': 'Bahan Baku', 'unit': 'kg', 'cost_price': 45000, 'sell_price': 0, 'product_type': 'raw_material'},
        ]
        
        products = {}
        for prod_data in raw_materials_data:
            product, _ = Product.objects.get_or_create(
                sku_code=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': categories[prod_data['category']],
                    'unit': units[prod_data['unit']],
                    'cost_price': prod_data['cost_price'],
                    'sell_price': prod_data['sell_price'],
                    'product_type': prod_data['product_type'],
                    'is_active': True,
                }
            )
            products[prod_data['sku']] = product
            print_success(f"Produk: {product.sku_code} - {product.name} ({product.cost_price:,.0f}/{product.unit.symbol})")
        
        created['products'] = products
        
        # ─── STEP 1.4: Harga Supplier ───────────────────────
        print_step("1.4", "Setup Harga Supplier")
        
        supplier_prices_data = [
            {'vendor': 'PT Bogasari Flour Mills', 'product': 'BB01', 'price': 12000, 'min_order': 25},
            {'vendor': 'PT Bogasari Flour Mills', 'product': 'BB02', 'price': 14000, 'min_order': 10},
            {'vendor': 'CV Segar Jaya', 'product': 'BB03', 'price': 2500, 'min_order': 100},
            {'vendor': 'CV Segar Jaya', 'product': 'BB04', 'price': 24000, 'min_order': 5},
            {'vendor': 'UD Susu Makmur', 'product': 'BB05', 'price': 17500, 'min_order': 10},
            {'vendor': 'CV Segar Jaya', 'product': 'BB06', 'price': 450, 'min_order': 50},
            {'vendor': 'CV Segar Jaya', 'product': 'BB07', 'price': 9500, 'min_order': 5},
            {'vendor': 'CV Segar Jaya', 'product': 'BB08', 'price': 43000, 'min_order': 1},
        ]
        
        for sp_data in supplier_prices_data:
            sp, _ = SupplierPrice.objects.get_or_create(
                vendor=vendors[sp_data['vendor']],
                product=products[sp_data['product']],
                defaults={
                    'price': sp_data['price'],
                    'min_order_qty': sp_data['min_order'],
                }
            )
            print_success(f"Harga: {sp.product.name} dari {sp.vendor.name} = Rp {sp.price:,.0f} (min {sp.min_order_qty})")
        
        # ─── STEP 1.5: User / Pengguna ──────────────────────
        print_step("1.5", "Setup User / Pengguna")
        
        users_data = [
            {'username': 'admin', 'email': 'admin@lumra.com', 'password': 'admin123', 'role': 'super_admin', 'location': 'TKO-001'},
            {'username': 'siti', 'email': 'siti@lumra.com', 'password': 'siti123', 'role': 'warehouse_manager', 'location': 'GUD-001'},
            {'username': 'budi', 'email': 'budi@lumra.com', 'password': 'budi123', 'role': 'production_head', 'location': 'DPR-001'},
            {'username': 'dewi', 'email': 'dewi@lumra.com', 'password': 'dewi123', 'role': 'cashier', 'location': 'TKO-001'},
            {'username': 'rina', 'email': 'rina@lumra.com', 'password': 'rina123', 'role': 'cashier', 'location': 'TKO-002'},
        ]
        
        test_users = {}
        for user_data in users_data:
            user, created_flag = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_staff': user_data['role'] == 'super_admin',
                    'is_superuser': user_data['role'] == 'super_admin',
                }
            )
            if created_flag:
                user.set_password(user_data['password'])
                user.save()
            
            # Update atau buat profile
            profile, _ = user.profile.get_or_create()
            profile.role = user_data['role']
            profile.default_location = locations[user_data['location']]
            profile.save()
            
            test_users[user_data['username']] = user
            print_success(f"User: {user.username} ({profile.role}) → {profile.default_location.name}")
        
        created['users'] = test_users
        
        # ══════════════════════════════════════════════════════
        # FASE 2: RESEP / PRODUKSI SETUP
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 2: RESEP / RECIPE", '═')
        
        # ─── STEP 2.1: Buat Resep Roti Coklat ────────────────
        print_step("2.1", "Buat Resep Roti Coklat")
        
        recipe_category, _ = RecipeCategory.objects.get_or_create(
            name='Roti',
            defaults={'description': 'Aneka roti'}
        )
        
        recipe, _ = Recipe.objects.get_or_create(
            name='Roti Coklat',
            defaults={
                'category': recipe_category,
                'description': 'Roti isi coklat lembut dan nikmat',
                'yield_qty': Decimal('10'),
                'yield_unit': units['pcs'],
                'production_time_minutes': 120,
                'sell_price': Decimal('15000'),
                'instructions': '1. Campurkan tepung, gula, ragi, garam. 2. Tambahkan telur, susu, margarin. 3. Uleni sampai kalis. 4. Fermentasi 60 menit. 5. Bentuk dan isi coklat. 6. Fermentasi 30 menit. 7. Panggang 25 menit.',
            }
        )
        created['recipe'] = recipe
        
        print_success(f"Resep: {recipe.name}")
        print_info(f"Yield: {recipe.yield_qty} {recipe.yield_unit.symbol}")
        print_info(f"Waktu: {recipe.production_time_minutes} menit")
        print_info(f"Harga Jual: Rp {recipe.sell_price:,.0f} / {recipe.yield_unit.symbol}")
        
        # ─── STEP 2.2: Input Bahan Baku Resep ───────────────
        print_step("2.2", "Input Bahan Baku ke Resep")
        
        ingredients_data = [
            {'product': 'BB01', 'qty': Decimal('1.0'), 'unit': 'kg'},
            {'product': 'BB02', 'qty': Decimal('0.2'), 'unit': 'kg'},
            {'product': 'BB03', 'qty': Decimal('4'), 'unit': 'btr'},
            {'product': 'BB04', 'qty': Decimal('0.15'), 'unit': 'kg'},
            {'product': 'BB05', 'qty': Decimal('0.3'), 'unit': 'L'},
            {'product': 'BB06', 'qty': Decimal('2'), 'unit': 'sdm'},
            {'product': 'BB07', 'qty': Decimal('0.01'), 'unit': 'kg'},
            {'product': 'BB08', 'qty': Decimal('0.1'), 'unit': 'kg'},
        ]
        
        total_cost = Decimal('0')
        for ing_data in ingredients_data:
            product = products[ing_data['product']]
            unit = units[ing_data['unit']]
            cost = product.cost_price * ing_data['qty']
            total_cost += cost
            
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                product=product,
                defaults={
                    'quantity': ing_data['qty'],
                    'unit': unit,
                }
            )
            print_success(f"  {product.name}: {ing_data['qty']} {unit.symbol} = Rp {cost:,.0f}")
        
        cost_per_unit = total_cost / recipe.yield_qty
        margin = ((recipe.sell_price - cost_per_unit) / recipe.sell_price * 100)
        
        print_info(f"\n  Total Biaya Bahan: Rp {total_cost:,.0f}")
        print_info(f"  Biaya per {recipe.yield_unit.symbol}: Rp {cost_per_unit:,.0f}")
        print_info(f"  Harga Jual: Rp {recipe.sell_price:,.0f}")
        print_info(f"  Margin: {margin:.1f}%")
        
        # ─── STEP 2.3: Buat Produk Jadi (Roti Coklat) ────────
        print_step("2.3", "Buat Produk Jadi dari Resep")
        
        product_roti, _ = Product.objects.get_or_create(
            sku_code='PJ01',
            defaults={
                'name': 'Roti Coklat',
                'category': categories['Roti'],
                'unit': units['pcs'],
                'cost_price': cost_per_unit,
                'sell_price': recipe.sell_price,
                'product_type': 'finished_goods',
                'is_active': True,
                'recipe': recipe,  # FK ke recipe jika ada
            }
        )
        products['PJ01'] = product_roti
        print_success(f"Produk Jadi: {product_roti.sku_code} - {product_roti.name}")
        print_info(f"Harga Jual: Rp {product_roti.sell_price:,.0f} / pcs")
        
        # ══════════════════════════════════════════════════════
        # FASE 3: BARANG MENTAH DATANG
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 3: BARANG MENTAH DATANG (PROCUREMENT)", '═')
        
        # ─── STEP 3.1: Input Pembelian dari Supplier ────────
        print_step("3.1", "Input Pembelian (Purchase Order)")
        
        po_code = generate_code('PO', Order)
        
        # Hitung subtotal
        po_items_data = [
            {'product': 'BB01', 'qty': 50, 'unit': 'kg', 'price': 12000},
            {'product': 'BB02', 'qty': 20, 'unit': 'kg', 'price': 14000},
            {'product': 'BB03', 'qty': 100, 'unit': 'btr', 'price': 2500},
            {'product': 'BB04', 'qty': 10, 'unit': 'kg', 'price': 24000},
            {'product': 'BB05', 'qty': 20, 'unit': 'L', 'price': 17500},
            {'product': 'BB06', 'qty': 100, 'unit': 'sdm', 'price': 450},
            {'product': 'BB07', 'qty': 5, 'unit': 'kg', 'price': 9500},
            {'product': 'BB08', 'qty': 5, 'unit': 'kg', 'price': 43000},
        ]
        
        subtotal = sum(item['qty'] * item['price'] for item in po_items_data)
        tax_amount = subtotal * Decimal('0.11')
        total_amount = subtotal + tax_amount
        
        purchase_order = Order.objects.create(
            code=po_code,
            order_type='purchase',
            vendor=vendors['PT Bogasari Flour Mills'],
            location=locations['GUD-001'],
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status='completed',
            notes='Pembelian rutin bahan baku',
            created_by=test_users['admin'],
        )
        created['purchase_order'] = purchase_order
        
        print_success(f"PO: {po_code}")
        print_info(f"Supplier: PT Bogasari Flour Mills")
        print_info(f"Lokasi: Gudang Utama")
        
        # Buat order items
        for item_data in po_items_data:
            OrderItem.objects.create(
                order=purchase_order,
                product=products[item_data['product']],
                quantity=Decimal(str(item_data['qty'])),
                unit_price=Decimal(str(item_data['price'])),
                subtotal=Decimal(str(item_data['qty'] * item_data['price'])),
            )
            print_success(f"  {products[item_data['product']].name}: {item_data['qty']} {item_data['unit']} × Rp {item_data['price']:,.0f}")
        
        print_info(f"\n  Subtotal: Rp {subtotal:,.0f}")
        print_info(f"  PPN 11%: Rp {tax_amount:,.0f}")
        print_info(f"  Total: Rp {total_amount:,.0f}")
        
        # ─── STEP 3.2: Update Stok + Movement Log ───────────
        print_step("3.2", "Terima Barang → Update Stok")
        
        gudang = locations['GUD-001']
        
        for item_data in po_items_data:
            product = products[item_data['product']]
            qty = Decimal(str(item_data['qty']))
            
            # Update atau buat stok
            stock, _ = Stock.objects.get_or_create(
                product=product,
                location=gudang,
                defaults={'quantity': Decimal('0')}
            )
            stock.quantity += qty
            stock.save()
            
            # Log movement
            StockMovement.objects.create(
                product=product,
                location=gudang,
                quantity=qty,
                movement_type='purchase',
                reference_code=po_code,
                reference_type='order',
                notes=f'Diterima dari PO {po_code}',
                created_by=test_users['admin'],
            )
        
        print_success(f"Stok di Gudang Utama diperbarui")
        print_stock_snapshot('Gudang Utama')
        print_stock_movement_log(po_code)
        
        # ══════════════════════════════════════════════════════
        # FASE 4: TRANSFER GUDANG → DAPUR
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 4: TRANSFER GUDANG → DAPUR PRODUKSI", '═')
        
        # ─── STEP 4.1: Buat Requisition ─────────────────────
        print_step("4.1", "Buat Permintaan Bahan (Requisition)")
        
        req_code = generate_code('REQ', Requisition)
        
        requisition = Requisition.objects.create(
            code=req_code,
            from_location=locations['GUD-001'],
            to_location=locations['DPR-001'],
            requested_by=test_users['budi'],
            status='pending',
            notes='Bahan untuk produksi Roti Coklat 50 pcs',
        )
        created['requisition'] = requisition
        
        # Bahan yang diminta (5x resep untuk 50 pcs)
        req_items_data = [
            {'product': 'BB01', 'qty': Decimal('5.0')},   # 5 kg
            {'product': 'BB02', 'qty': Decimal('1.0')},   # 1 kg
            {'product': 'BB03', 'qty': Decimal('20')},    # 20 butir
            {'product': 'BB04', 'qty': Decimal('0.75')},  # 0.75 kg
            {'product': 'BB05', 'qty': Decimal('1.5')},   # 1.5 L
            {'product': 'BB06', 'qty': Decimal('10')},    # 10 sdm
            {'product': 'BB07', 'qty': Decimal('0.05')},  # 0.05 kg
            {'product': 'BB08', 'qty': Decimal('0.5')},   # 0.5 kg
        ]
        
        for item_data in req_items_data:
            product = products[item_data['product']]
            
            # Cek stok tersedia
            stock = Stock.objects.filter(product=product, location=gudang).first()
            available = stock.quantity if stock else Decimal('0')
            
            RequisitionItem.objects.create(
                requisition=requisition,
                product=product,
                quantity_requested=item_data['qty'],
                notes=f'Tersedia: {available}',
            )
            
            status_icon = '✅' if available >= item_data['qty'] else '❌'
            print_success(f"  {status_icon} {product.name}: {item_data['qty']} (tersedia: {available})")
        
        # ─── STEP 4.2: Approve Requisition ─────────────────
        print_step("4.2", "Approve Requisition")
        
        requisition.status = 'approved'
        requisition.approved_by = test_users['siti']
        requisition.approved_at = datetime.now()
        requisition.save()
        print_success(f"Requisition {req_code} disetujui oleh Siti (Manager Gudang)")
        
        # ─── STEP 4.3: Buat Transfer ────────────────────────
        print_step("4.3", "Buat Transfer & Eksekusi")
        
        trf_code = generate_code('TRF', Transfer)
        
        transfer = Transfer.objects.create(
            code=trf_code,
            from_location=locations['GUD-001'],
            to_location=locations['DPR-001'],
            reference_requisition=requisition,
            status='completed',
            notes='Transfer bahan untuk produksi Roti Coklat',
            created_by=test_users['siti'],
        )
        created['transfer'] = transfer
        
        dapur = locations['DPR-001']
        
        for item_data in req_items_data:
            product = products[item_data['product']]
            qty = item_data['qty']
            
            # Buat transfer item
            TransferItem.objects.create(
                transfer=transfer,
                product=product,
                quantity=qty,
            )
            
            # Kurangi stok Gudang
            stock_gudang = Stock.objects.get(product=product, location=gudang)
            stock_gudang.quantity -= qty
            stock_gudang.save()
            
            # Tambah stok Dapur
            stock_dapur, _ = Stock.objects.get_or_create(
                product=product,
                location=dapur,
                defaults={'quantity': Decimal('0')}
            )
            stock_dapur.quantity += qty
            stock_dapur.save()
            
            # Log movement - keluar dari gudang
            StockMovement.objects.create(
                product=product,
                location=gudang,
                quantity=-qty,
                movement_type='transfer_out',
                reference_code=trf_code,
                reference_type='transfer',
                notes=f'Transfer ke Dapur Produksi',
                created_by=test_users['siti'],
            )
            
            # Log movement - masuk ke dapur
            StockMovement.objects.create(
                product=product,
                location=dapur,
                quantity=qty,
                movement_type='transfer_in',
                reference_code=trf_code,
                reference_type='transfer',
                notes=f'Terima dari Gudang Utama',
                created_by=test_users['siti'],
            )
        
        print_success(f"Transfer {trf_code} selesai")
        print_stock_snapshot('Gudang Utama')
        print_stock_snapshot('Dapur Produksi')
        print_stock_movement_log(trf_code)
        
        # Update requisition status
        requisition.status = 'fulfilled'
        requisition.save()
        
        # ══════════════════════════════════════════════════════
        # FASE 5: PROSES PRODUKSI
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 5: PROSES PRODUKSI", '═')
        
        # ─── STEP 5.1: Buat Production Order ────────────────
        print_step("5.1", "Buat Production Order")
        
        prd_code = generate_code('PRD', ProductionOrder)
        target_qty = Decimal('50')  # 50 pcs roti
        
        production_order = ProductionOrder.objects.create(
            po_code=prd_code,
            recipe=recipe,
            location=dapur,
            assigned_to=test_users['budi'],
            target_qty=target_qty,
            status='draft',
            output_location=locations['TKO-001'],  # Hasil ke toko pusat
            notes='Produksi Roti Coklat untuk Toko Pusat',
            created_by=test_users['budi'],
        )
        created['production_order'] = production_order
        
        print_success(f"Production Order: {prd_code}")
        print_info(f"Resep: {recipe.name}")
        print_info(f"Target: {target_qty} pcs")
        print_info(f"Lokasi: Dapur Produksi")
        print_info(f"Output ke: LUMRA Cafe Pusat")
        
        # ─── STEP 5.2: Hitung Bahan yang Dibutuhkan ─────────
        print_step("5.2", "Hitung Kebutuhan Bahan Baku")
        
        # Ratio: resep untuk 10 pcs, kita mau 50 pcs = 5x
        ratio = target_qty / recipe.yield_qty
        
        total_material_cost = Decimal('0')
        
        print(f"\n  {Colors.DIM}Resep untuk {recipe.yield_qty} pcs, target {target_qty} pcs = ratio {ratio}x{Colors.RESET}\n")
        
        for ingredient in recipe.ingredients.all():
            qty_required = ingredient.quantity * ratio
            cost = ingredient.product.cost_price * qty_required
            total_material_cost += cost
            
            # Cek stok di dapur
            stock_dapur = Stock.objects.filter(
                product=ingredient.product,
                location=dapur
            ).first()
            available = stock_dapur.quantity if stock_dapur else Decimal('0')
            enough = '✅' if available >= qty_required else '❌'
            
            ProductionOrderMaterial.objects.create(
                production_order=production_order,
                product=ingredient.product,
                quantity_required=qty_required,
                unit=ingredient.unit,
                cost_price=ingredient.product.cost_price,
            )
            
            print_success(f"  {enough} {ingredient.product.name}: {qty_required} {ingredient.unit.symbol} (tersedia: {available}) = Rp {cost:,.0f}")
        
        print_info(f"\n  Total Biaya Material: Rp {total_material_cost:,.0f}")
        print_info(f"  Estimasi Biaya/pcs: Rp {total_material_cost / target_qty:,.0f}")
        
        # ─── STEP 5.3: Mulai Produksi ───────────────────────
        print_step("5.3", "Mulai Produksi (Kurangi Stok Bahan)")
        
        production_order.status = 'in_progress'
        production_order.started_at = datetime.now()
        production_order.total_material_cost = total_material_cost
        production_order.save()
        
        for material in production_order.materials.all():
            qty_used = material.quantity_required
            
            # Kurangi stok bahan baku di dapur
            stock_dapur = Stock.objects.get(
                product=material.product,
                location=dapur
            )
            stock_dapur.quantity -= qty_used
            stock_dapur.save()
            
            # Update material dengan actual qty
            material.quantity_used = qty_used
            material.save()
            
            # Log movement
            StockMovement.objects.create(
                product=material.product,
                location=dapur,
                quantity=-qty_used,
                movement_type='production_out',
                reference_code=prd_code,
                reference_type='production_order',
                notes=f'Dipakai untuk produksi {prd_code}',
                created_by=test_users['budi'],
            )
        
        print_success(f"Produksi {prd_code} dimulai")
        print_info(f"Stok bahan baku di Dapur berkurang")
        print_stock_snapshot('Dapur Produksi')
        print_stock_movement_log(prd_code)
        
        # ─── STEP 5.4: Selesai Produksi ─────────────────────
        print_step("5.4", "Produksi Selesai — Terima Hasil")
        
        actual_qty = Decimal('48')  # Aktual 48 pcs (2 pcs rusak)
        waste_qty = target_qty - actual_qty
        waste_reason = '2 pcs gosong, tidak bisa dijual'
        
        production_order.status = 'completed'
        production_order.actual_qty = actual_qty
        production_order.waste_qty = waste_qty
        production_order.waste_reason = waste_reason
        production_order.completed_at = datetime.now()
        production_order.save()
        
        # Tambah stok produk jadi di toko
        toko_pusat = locations['TKO-001']
        stock_toko, _ = Stock.objects.get_or_create(
            product=product_roti,
            location=toko_pusat,
            defaults={'quantity': Decimal('0')}
        )
        stock_toko.quantity += actual_qty
        stock_toko.save()
        
        # Log movement
        StockMovement.objects.create(
            product=product_roti,
            location=toko_pusat,
            quantity=actual_qty,
            movement_type='production_in',
            reference_code=prd_code,
            reference_type='production_order',
            notes=f'Hasil produksi dari {prd_code}',
            created_by=test_users['budi'],
        )
        
        print_success(f"Produksi {prd_code} selesai!")
        print_info(f"Target: {target_qty} pcs")
        print_info(f"Aktual: {actual_qty} pcs")
        print_warning(f"Waste: {waste_qty} pcs — {waste_reason}")
        print_info(f"Biaya aktual/pcs: Rp {total_material_cost / actual_qty:,.0f}")
        
        print_stock_snapshot('LUMRA Cafe Pusat')
        print_stock_movement_log(prd_code)
        
        # ══════════════════════════════════════════════════════
        # FASE 6: PENJUALAN DI POS
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 6: PENJUALAN DI POS", '═')
        
        # ─── STEP 6.1: Transaksi Pertama ────────────────────
        print_step("6.1", "Transaksi 1 — Penjualan Roti Coklat 2 pcs")
        
        so_code_1 = generate_code('SO', Order)
        qty_sell_1 = Decimal('2')
        price_per_unit = product_roti.sell_price
        subtotal_1 = qty_sell_1 * price_per_unit
        tax_1 = subtotal_1 * Decimal('0.11')
        total_1 = subtotal_1 + tax_1
        paid_1 = Decimal('50000')
        change_1 = paid_1 - total_1
        
        # Buat order
        sales_order_1 = Order.objects.create(
            code=so_code_1,
            order_type='sales',
            location=toko_pusat,
            customer=None,  # Walk-in
            subtotal=subtotal_1,
            tax_amount=tax_1,
            discount_amount=Decimal('0'),
            total_amount=total_1,
            payment_method='cash',
            paid_amount=paid_1,
            change_amount=change_1,
            status='completed',
            created_by=test_users['dewi'],
        )
        created['sales_order_1'] = sales_order_1
        
        # Buat order item
        OrderItem.objects.create(
            order=sales_order_1,
            product=product_roti,
            quantity=qty_sell_1,
            unit_price=price_per_unit,
            subtotal=subtotal_1,
        )
        
        # Kurangi stok
        stock_toko.quantity -= qty_sell_1
        stock_toko.save()
        
        # Log movement
        StockMovement.objects.create(
            product=product_roti,
            location=toko_pusat,
            quantity=-qty_sell_1,
            movement_type='sale',
            reference_code=so_code_1,
            reference_type='order',
            notes=f'Penjualan di POS',
            created_by=test_users['dewi'],
        )
        
        # Buat payment
        pay_code_1 = generate_code('PAY', Payment)
        Payment.objects.create(
            payment_code=pay_code_1,
            order=sales_order_1,
            payment_method='cash',
            amount=total_1,
            paid_at=datetime.now(),
            created_by=test_users['dewi'],
        )
        
        print_success(f"Order: {so_code_1}")
        print_info(f"Produk: Roti Coklat × {qty_sell_1}")
        print_info(f"Subtotal: Rp {subtotal_1:,.0f}")
        print_info(f"PPN 11%: Rp {tax_1:,.0f}")
        print_info(f"Total: Rp {total_1:,.0f}")
        print_info(f"Bayar: Rp {paid_1:,.0f}")
        print_info(f"Kembalian: Rp {change_1:,.0f}")
        
        print_stock_snapshot('LUMRA Cafe Pusat')
        
        # ─── STEP 6.2: Transaksi Kedua ──────────────────────
        print_step("6.2", "Transaksi 2 — Penjualan Roti Coklat 3 pcs")
        
        so_code_2 = generate_code('SO', Order)
        qty_sell_2 = Decimal('3')
        subtotal_2 = qty_sell_2 * price_per_unit
        tax_2 = subtotal_2 * Decimal('0.11')
        total_2 = subtotal_2 + tax_2
        paid_2 = Decimal('100000')
        change_2 = paid_2 - total_2
        
        sales_order_2 = Order.objects.create(
            code=so_code_2,
            order_type='sales',
            location=toko_pusat,
            customer=None,
            subtotal=subtotal_2,
            tax_amount=tax_2,
            discount_amount=Decimal('0'),
            total_amount=total_2,
            payment_method='qris',
            paid_amount=paid_2,
            change_amount=Decimal('0'),
            status='completed',
            created_by=test_users['dewi'],
        )
        created['sales_order_2'] = sales_order_2
        
        OrderItem.objects.create(
            order=sales_order_2,
            product=product_roti,
            quantity=qty_sell_2,
            unit_price=price_per_unit,
            subtotal=subtotal_2,
        )
        
        stock_toko.quantity -= qty_sell_2
        stock_toko.save()
        
        StockMovement.objects.create(
            product=product_roti,
            location=toko_pusat,
            quantity=-qty_sell_2,
            movement_type='sale',
            reference_code=so_code_2,
            reference_type='order',
            notes=f'Penjualan di POS',
            created_by=test_users['dewi'],
        )
        
        pay_code_2 = generate_code('PAY', Payment)
        Payment.objects.create(
            payment_code=pay_code_2,
            order=sales_order_2,
            payment_method='qris',
            amount=total_2,
            paid_at=datetime.now(),
            created_by=test_users['dewi'],
        )
        
        print_success(f"Order: {so_code_2}")
        print_info(f"Produk: Roti Coklat × {qty_sell_2}")
        print_info(f"Total: Rp {total_2:,.0f} (QRIS)")
        
        print_stock_snapshot('LUMRA Cafe Pusat')
        
        # ─── STEP 6.3: Transaksi Ketiga — Ada Retur ─────────
        print_step("6.3", "Transaksi 3 — Penjualan + Retur 1 pcs")
        
        so_code_3 = generate_code('SO', Order)
        qty_sell_3 = Decimal('5')
        subtotal_3 = qty_sell_3 * price_per_unit
        tax_3 = subtotal_3 * Decimal('0.11')
        total_3 = subtotal_3 + tax_3
        paid_3 = total_3  # Pas bayar
        
        sales_order_3 = Order.objects.create(
            code=so_code_3,
            order_type='sales',
            location=toko_pusat,
            customer=None,
            subtotal=subtotal_3,
            tax_amount=tax_3,
            discount_amount=Decimal('0'),
            total_amount=total_3,
            payment_method='cash',
            paid_amount=paid_3,
            change_amount=Decimal('0'),
            status='completed',
            created_by=test_users['dewi'],
        )
        created['sales_order_3'] = sales_order_3
        
        OrderItem.objects.create(
            order=sales_order_3,
            product=product_roti,
            quantity=qty_sell_3,
            unit_price=price_per_unit,
            subtotal=subtotal_3,
        )
        
        stock_toko.quantity -= qty_sell_3
        stock_toko.save()
        
        StockMovement.objects.create(
            product=product_roti,
            location=toko_pusat,
            quantity=-qty_sell_3,
            movement_type='sale',
            reference_code=so_code_3,
            reference_type='order',
            notes=f'Penjualan di POS',
            created_by=test_users['dewi'],
        )
        
        print_success(f"Order: {so_code_3} — Roti Coklat × {qty_sell_3}")
        
        # ─── STEP 6.4: Proses Retur ─────────────────────────
        print_step("6.4", "Proses Retur 1 pcs dari Order 3")
        
        ret_code = generate_code('RET', ReturnOrder)
        qty_return = Decimal('1')
        return_subtotal = qty_return * price_per_unit
        return_tax = return_subtotal * Decimal('0.11')
        return_total = return_subtotal + return_tax
        
        return_order = ReturnOrder.objects.create(
            return_code=ret_code,
            order=sales_order_3,
            return_date=datetime.now(),
            subtotal=return_subtotal,
            tax_amount=return_tax,
            total_amount=return_total,
            status='completed',
            reason='Roti kurang matang, pelanggan komplain',
            created_by=test_users['dewi'],
        )
        created['return_order'] = return_order
        
        ReturnItem.objects.create(
            return_order=return_order,
            product=product_roti,
            quantity=qty_return,
            unit_price=price_per_unit,
            subtotal=return_subtotal,
            reason='Kurang matang',
        )
        
        # Kembalikan stok
        stock_toko.quantity += qty_return
        stock_toko.save()
        
        # Log movement
        StockMovement.objects.create(
            product=product_roti,
            location=toko_pusat,
            quantity=qty_return,
            movement_type='return_in',
            reference_code=ret_code,
            reference_type='return',
            notes=f'Retur dari {so_code_3}',
            created_by=test_users['dewi'],
        )
        
        print_success(f"Retur: {ret_code}")
        print_info(f"Produk: Roti Coklat × {qty_return}")
        print_info(f"Nilai Retur: Rp {return_total:,.0f}")
        print_warning(f"Alasan: Roti kurang matang")
        
        print_stock_snapshot('LUMRA Cafe Pusat')
        
        # ══════════════════════════════════════════════════════
        # FASE 7: RINGKASAN & VALIDASI
        # ══════════════════════════════════════════════════════
        
        print_header("FASE 7: RINGKASAN & VALIDASI", '═')
        
        # ─── STEP 7.1: Ringkasan Stok Akhir ─────────────────
        print_step("7.1", "Ringkasan Stok Akhir Semua Lokasi")
        
        all_stocks = Stock.objects.exclude(quantity=0).select_related('product', 'product__unit', 'location')
        
        headers = ['Lokasi', 'Produk', 'Tipe', 'Stok', 'Satuan', 'Nilai Stok']
        rows = []
        
        for stock in all_stocks:
            stock_value = stock.quantity * (stock.product.cost_price or 0)
            rows.append([
                stock.location.name[:20],
                stock.product.name[:20],
                stock.product.get_product_type_display() or stock.product.product_type,
                str(stock.quantity),
                stock.product.unit.symbol,
                f"Rp {stock_value:,.0f}"
            ])
        
        print_data_table(headers, rows, [22, 22, 15, 10, 8, 15])
        
        total_value = sum(s.quantity * (s.product.cost_price or 0) for s in all_stocks)
        print_info(f"\n  Total Nilai Stok: Rp {total_value:,.0f}")
        
        # ─── STEP 7.2: Ringkasan Penjualan ──────────────────
        print_step("7.2", "Ringkasan Penjualan")
        
        sales_orders = Order.objects.filter(order_type='sales', status='completed')
        total_sales = sales_orders.aggregate(
            total=Sum('total_amount'),
            count=Sum('orderitem__quantity')
        )
        
        headers = ['No. Order', 'Waktu', 'Items', 'Total', 'Metode']
        rows = []
        
        for order in sales_orders:
            items_count = order.orderitem_set.aggregate(qty=Sum('quantity'))['qty'] or 0
            rows.append([
                order.code,
                order.created_at.strftime('%H:%M:%S'),
                str(items_count),
                f"Rp {order.total_amount:,.0f}",
                order.get_payment_method_display() or order.payment_method,
            ])
        
        print_data_table(headers, rows, [18, 10, 8, 15, 12])
        
        print_info(f"\n  Total Penjualan: {sales_orders.count()} transaksi")
        print_info(f"  Total Items Terjual: {total_sales['count'] or 0} pcs")
        print_info(f"  Total Revenue: Rp {total_sales['total'] or 0:,.0f}")
        
        # ─── STEP 7.3: Ringkasan Produksi ───────────────────
        print_step("7.3", "Ringkasan Produksi")
        
        headers = ['No. Produksi', 'Produk', 'Target', 'Aktual', 'Waste', 'Status']
        rows = [[
            production_order.po_code,
            production_order.recipe.name,
            str(production_order.target_qty),
            str(production_order.actual_qty),
            str(production_order.waste_qty),
            production_order.get_status_display(),
        ]]
        
        print_data_table(headers, rows, [18, 15, 10, 10, 8, 15])
        
        # ─── STEP 7.4: Validasi Stok Roti Coklat ────────────
        print_step("7.4", "Validasi Stok Roti Coklat (Audit Trail)")
        
        print_info("Rumus: Produksi Masuk - Penjualan Keluar + Retur Masuk = Stok Akhir")
        print()
        
        # Hitung dari movement log
        movements = StockMovement.objects.filter(
            product=product_roti,
            location=toko_pusat
        )
        
        produced = movements.filter(movement_type='production_in').aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        sold = abs(movements.filter(movement_type='sale').aggregate(total=Sum('quantity'))['total'] or Decimal('0'))
        returned = movements.filter(movement_type='return_in').aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        expected_stock = produced - sold + returned
        
        # Stok aktual di database
        actual_stock = Stock.objects.get(product=product_roti, location=toko_pusat).quantity
        
        print(f"  Produksi Masuk  : +{produced} pcs")
        print(f"  Penjualan Keluar: -{sold} pcs")
        print(f"  Retur Masuk     : +{returned} pcs")
        print(f"  ─────────────────────────────")
        print(f"  Stok Expected   : {expected_stock} pcs")
        print(f"  Stok Aktual DB  : {actual_stock} pcs")
        
        if expected_stock == actual_stock:
            print_success(f"\n  ✅ VALIDASI BERHASIL — Stok konsisten!")
        else:
            print_error(f"\n  ❌ VALIDASI GAGAL — Selisih {abs(expected_stock - actual_stock)} pcs")
        
        # ─── STEP 7.5: Full Movement Log ────────────────────
        print_step("7.5", "Full Movement Log — Roti Coklat di Toko Pusat")
        
        all_movements = StockMovement.objects.filter(
            product=product_roti,
            location=toko_pusat
        ).order_by('created_at')
        
        headers = ['#', 'Waktu', 'Tipe', 'Qty', 'Ref', 'Notes']
        rows = []
        running_balance = Decimal('0')
        
        for i, m in enumerate(all_movements, 1):
            running_balance += m.quantity
            sign = '+' if m.quantity > 0 else ''
            rows.append([
                str(i),
                m.created_at.strftime('%H:%M:%S'),
                m.movement_type,
                f"{sign}{m.quantity}",
                m.reference_code or '-',
                m.notes[:25] if m.notes else '-',
            ])
        
        print_data_table(headers, rows, [4, 10, 15, 8, 18, 27])
        print_info(f"\n  Running Balance: {running_balance} pcs")
        
        # ─── STEP 7.6: Complete Setup ───────────────────────
        print_step("7.6", "Mark Setup as Completed")
        
        business.is_setup_completed = True
        business.save()
        print_success(f"Setup bisnis '{business.business_name}' ditandai selesai")
        
        # ══════════════════════════════════════════════════════
        # FINAL SUMMARY
        # ══════════════════════════════════════════════════════
        
        print_header("TEST COMPLETED SUCCESSFULLY", '═')
        
        summary_data = [
            ['Lokasi', str(Location.objects.count())],
            ['Kategori', str(Category.objects.count())],
            ['Satuan', str(Unit.objects.count())],
            ['Supplier', str(Vendor.objects.count())],
            ['Produk', str(Product.objects.count())],
            ['Harga Supplier', str(SupplierPrice.objects.count())],
            ['Resep', str(Recipe.objects.count())],
            ['Bahan Resep', str(RecipeIngredient.objects.count())],
            ['Purchase Orders', str(Order.objects.filter(order_type='purchase').count())],
            ['Requisitions', str(Requisition.objects.count())],
            ['Transfers', str(Transfer.objects.count())],
            ['Production Orders', str(ProductionOrder.objects.count())],
            ['Sales Orders', str(Order.objects.filter(order_type='sales').count())],
            ['Payments', str(Payment.objects.count())],
            ['Returns', str(ReturnOrder.objects.count())],
            ['Stock Records', str(Stock.objects.count())],
            ['Stock Movements', str(StockMovement.objects.count())],
        ]
        
        headers = ['Entity', 'Count']
        print_data_table(headers, summary_data, [25, 10])
        
        print(f"\n  {Colors.GREEN}{Colors.BOLD}🎉 Semua alur berhasil dijalankan!{Colors.RESET}")
        
        if USE_TRANSACTION:
            print(f"\n  {Colors.YELLOW}⚠️  Data akan di-rollback karena USE_TRANSACTION = True{Colors.RESET}")
            print(f"  {Colors.YELLOW}   Set USE_TRANSACTION = False untuk menyimpan data permanen{Colors.RESET}")
        
        return True
        
    except Exception as e:
        print_error(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        if USE_TRANSACTION:
            print_warning("\nTransaction akan di-rollback karena error")
        
        return False
    
    finally:
        if USE_TRANSACTION:
            print(f"\n  {Colors.DIM}🔄 Rolling back transaction...{Colors.RESET}")
            context.__exit__(None, None, None)
            print_success("Rollback complete — database bersih")


# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    run_full_flow_test()