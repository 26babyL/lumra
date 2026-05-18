import os
import sys
import random
import traceback
from decimal import Decimal
from datetime import date, datetime, time, timedelta
from collections import defaultdict

# ─── UTF-8 SETUP ─────────────────────────────────────────────────────────────
for _sn in ("stdout", "stderr"):
    _s = getattr(sys, _sn, None)
    if hasattr(_s, "reconfigure"):
        try: _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass

# ─── DJANGO SETUP ────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")

import django
try: django.setup()
except RuntimeError as e:
    print(f"[ERROR] Django setup gagal: {e}")
    sys.exit(1)

from django.db import transaction, connection
from django.db.models import Sum, Q, F
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC MODEL LOADER
# Mengambil model berdasarkan nama aplikasi dan nama model
# ══════════════════════════════════════════════════════════════════════════════

def get_model(app, name):
    from django.apps import apps
    try: return apps.get_model(app, name)
    except: return None

M = {}
# Config / ERP Models
M['Location'] = get_model('lumra_config', 'Locations')
M['ProductVariant'] = get_model('lumra_config', 'Productvariants')
M['Product'] = get_model('lumra_config', 'Products')
M['Customer'] = get_model('lumra_config', 'Customers')
M['Order'] = get_model('lumra_config', 'Orders')
M['OrderItem'] = get_model('lumra_config', 'Orderitems')
M['Payment'] = get_model('lumra_config', 'Payments')
M['Transfer'] = get_model('lumra_config', 'Transfers')
M['TransferItem'] = get_model('lumra_config', 'Transferitem')
M['Return'] = get_model('lumra_config', 'Returns')
M['ReturnItem'] = get_model('lumra_config', 'Returnitems')

# Production Models
M['ProductionOrder'] = get_model('production', 'Orders') or get_model('lumra_config', 'ProductionOrders') # Check both
if not M['ProductionOrder']: M['ProductionOrder'] = get_model('production', 'ProductionOrders') # Last resort

M['MatConsumption'] = get_model('production', 'MaterialConsumptions') or get_model('production', 'ProductionMaterialConsumptions')
M['WasteRecord'] = get_model('production', 'WasteRecords') or get_model('production', 'ProductionWasteRecords')

# Accounting Models
M['Account'] = get_model('accounting', 'Accounts') or get_model('accounting', 'AccountingAccounts')
M['JournalEntry'] = get_model('accounting', 'JournalEntries') or get_model('accounting', 'AccountingJournalEntries')
M['JournalLine'] = get_model('accounting', 'JournalEntryLines') or get_model('accounting', 'AccountingJournalEntryLines')

# Inspect Schema Fields
def get_fields(model):
    return [f.name for f in model._meta.get_fields()] if model

SCHEMA = {k: get_fields(v) for k, v in M.items()}

print("\n" + "="*70)
print("  LUMRA ERP — MISSING DATA FILLER (Sales, Payments, Waste, Accounting)")
print("="*70)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG & HELPERS
# ══════════════════════════════════════════════════════════════════════════════

CFG = {
    "waste_rate_range": (0.01, 0.07), # Range lebih baik drpd satu angka
    "sales_peak_hours": {
        "lunch": [11, 12, 13], 
        "dinner": [18, 19, 20]
    },
    "weekend_multiplier": 1.5, # Penjualan sabtu-minggu lebih tinggi
    "seed": 42,
}

random.seed(CFG["seed"])

def generate_code(prefix):
    ts = timezone.now().strftime("%Y%m%d%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{prefix}-{ts}-{rand}"

def get_actors():
    return list(User.objects.filter(is_staff=True).order_by('id')[:10]) or [User.objects.first()]

def get_accounts():
    accs = M['Account'].objects.all()
    # Simple heuristics to find accounts
    acc_cash = [a for a in accs if 'kas' in a.name.lower() or 'cash' in a.name.lower()]
    acc_sales = [a for a in accs if 'pendapatan' in a.name.lower() or 'sales' in a.name.lower() or 'penjualan' in a.name.lower()]
    acc_expense = [a for a in accs if 'beban' in a.name.lower() or 'expense' in a.name.lower() or 'rugi' in a.name.lower()]
    acc_inventory = [a for a in accs if 'persediaan' in a.name.lower() or 'inventory' in a.name.lower() or 'stok' in a.name.lower()]
    
    # Fallback to first account if category empty
    return {
        'cash': acc_cash[0] if acc_cash else accs.first(),
        'sales': acc_sales[0] if acc_sales else accs.first(),
        'expense': acc_expense[0] if acc_expense else accs.first(),
        'inventory': acc_inventory[0] if acc_inventory else accs.first()
    }

def make_aware(naive_dt):
    if isinstance(naive_dt, datetime) and timezone.is_naive(naive_dt):
        return timezone.make_aware(naive_dt, timezone.get_current_timezone())
    return naive_dt_dt

# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def run_fill():
    # 1. CHECK PRE-EXISTING DATA
    if M['Order'].objects.count() > 0:
        print("\n[ABORT] Tabel Orders sudah ada data. Gunakan script ini hanya jika tabel kosong.")
        return

    print("\n[INIT] Loading Master Data (Customers, Transfers, Accounts, ProductionOrders)...")
    
    # Load Data
    customers = list(M['Customer'].objects.all()[:5000])
    actors = get_actors()
    accounts = get_accounts()
    
    # Get Transfers that went to a Store (destination is store)
    # Schema: LumraConfigTransfers -> destination_location
    transfers = list(M['Transfer'].objects.filter(status='received').select_related('destination_location', 'created_by').order_by('created_at'))
    
    # Get Production Orders for Waste Generation
    prod_orders = list(M['ProductionOrder'].objects.filter(status='completed').select_related('created_by').order_by('created_at')[:1000])
    
    print(f"  - Customers: {len(customers)}")
    print(f"  - Actors (Staff): {len(actors)}")
    print(f"  - Accounts: Cash({accounts['cash']}), Sales({accounts['sales']}), Expense({accounts['expense']})")
    print(f"  - Transfers (Source for Sales): {len(transfers)}")
    print(f"  - Production Orders (Source for Waste): {len(prod_orders)}")

    if not transfers or not customers or not prod_orders:
        print("\n[ERROR] Data referensi kurang lengkap untuk generate data.")
        return

    # Buffers for bulk creation
    bulk_orders = []
    bulk_order_items = []
    bulk_payments = []
    bulk_returns = []
    bulk_return_items = []
    bulk_waste = []
    bulk_journals = []
    bulk_journal_lines = []

    total_sales = 0
    total_returns = 0
    total_waste = 0

    print("\n[PROCESS] Generating Sales, Payments, and Waste...")

    # ══════════════════════════════════════════════════════════════════════
    # LOOP 1: GENERATE SALES & PAYMENTS FROM TRANSFERS
    # ══════════════════════════════════════════════════════════════════════
    
    for trf in transfers:
        store_loc = trf.destination_location
        if 'store' not in store_loc.location_type.lower() and 'toko' not in store_loc.location_type.lower():
            continue # Skip if not store (though schema implies we need to filter, let's assume all completed transfers are relevant or check location type)
        
        # Get items for this transfer
        trf_items = M['TransferItem'].objects.filter(transfer=trf).select_related('variant')
        
        if not trf_items: continue

        # Create 1-3 Orders per Transfer
        num_orders = random.randint(1, 2)
        order_date = make_aware(trf.created_at) + timedelta(hours=random.randint(2, 48))
        cashier = random.choice(actors)
        customer = random.choice(customers)

        for _ in range(num_orders):
            total_amount = Decimal("0")
            items_buffer = []

            # Order Schema Mapping
            order = M['Order']()
            order.customer_name = customer.name
            order.status = 'completed'
            order.customer = customer
            order.cashier = cashier
            order.created_at = order_date
            
            # Fields from Schema
            order.change_amount = Decimal("0")
            order.dining_option = random.choice(['dine_in', 'take_away'])
            order.order_type = 'pos'
            order.payment_method = random.choice(['cash', 'transfer', 'qris', 'card'])
            order.payment_status = 'paid'
            order.shift_id = f"S-{order_date.hour}"
            order.table_number = f"T-{random.randint(1, 20)}"

            # Process items
            for ti in trf_items:
                # Simulate selling part of the transferred stock
                sold_qty = int(ti.quantity_received * random.uniform(0.1, 0.8) / num_orders)
                if sold_qty <= 0: continue

                price_sell = ti.variant.price_sell or ti.variant.price_buy * Decimal("1.3")
                subtotal = price_sell * sold_qty
                total_amount += subtotal
                
                oi = M['OrderItem']()
                oi.quantity = sold_qty
                oi.price = price_sell
                oi.variant = ti.variant
                oi.discount_amount = Decimal("0")
                oi.discount_percent = Decimal("0")
                oi.notes = "Generated from Transfer"
                items_buffer.append((oi, subtotal))
            
            if not items_buffer: continue

            # Finalize Order
            order.paid_amount = total_amount
            bulk_orders.append(order)
            
            # Add Items
            for oi, sub in items_buffer:
                oi.order = order # Link after order has list ID (handle via bulk save later or set FK manually)
                # Since we bulk create, we can't set FK immediately to objects in the same list.
                # We will map them after save.
                bulk_order_items.append(oi)

            # Create Payment
            pay = M['Payment']()
            pay.payment_number = generate_code("PAY")
            pay.payment_date = order_date.date()
            pay.amount = total_amount
            pay.payment_method = order.payment_method
            pay.status = 'paid'
            pay.order = order # Needs ID
            pay.received_by = cashier
            pay.reference_number = order.customer_name[:20]
            pay.notes = "Auto Payment"
            pay.created_at = order_date
            bulk_payments.append(pay)

            # Create Accounting Entry: SALES
            jv = M['JournalEntry']()
            jv.number = generate_code("JV-SALES")
            jv.date = order_date.date()
            jv.reference = f"Order #{order.id}" # Will be PK after save
            jv.description = f"Sales POS {store_loc.name}"
            jv.status = 'posted'
            jv.source = 'sales'
            jv.created_by = cashier
            jv.created_at = order_date
            bulk_journals.append(jv)

            # Journal Lines (Debit Cash, Credit Sales)
            line1 = M['JournalLine']()
            line1.account = accounts['cash']
            line1.debit = total_amount
            line1.credit = Decimal("0")
            line1.description = "Penjualan Tunai/Card"
            line1.journal_entry = jv
            bulk_journal_lines.append(line1)

            line2 = M['JournalLine']()
            line2.account = accounts['sales']
            line2.debit = Decimal("0")
            line2.credit = total_amount
            line2.description = "Pendapatan Penjualan"
            line2.journal_entry = jv
            bulk_journal_lines.append(line2)

            total_sales += 1

    # ══════════════════════════════════════════════════════════════════════
    # LOOP 2: GENERATE WASTE FROM PRODUCTION
    # ══════════════════════════════════════════════════════════════════════
    
    for po in prod_orders:
        # Check if this PO has consumptions
        consumptions = M['MatConsumption'].objects.filter(production_order=po).select_related('component')
        if not consumptions: continue

        # Create 1-2 waste records per PO
        if random.random() > CFG['waste_rate']: continue # Random skip

        prod_date = make_aware(po.started_at) if po.started_at else make_aware(po.created_at)
        creator = po.created_by if po.created_by else random.choice(actors)

        for cons in random.sample(consumptions, min(2, len(consumptions))):
            waste_qty = cons.quantity * Decimal(str(random.uniform(0.01, 0.05)))
            if waste_qty < Decimal("0.01"): continue

            wr = M['WasteRecord']()
            wr.production_order = po
            wr.component = cons.component
            wr.waste_type = random.choice(['damage', 'expired', 'process_loss', 'spillage'])
            wr.quantity = waste_qty
            wr.unit = cons.unit
            wr.recorded_at = prod_date + timedelta(hours=4)
            wr.notes = f"Waste recorded for PO {po.code}"
            bulk_waste.append(wr)

            # Accounting: WASTE (Debit Expense, Credit Inventory)
            # Note: Usually waste is tracked physically first. Accounting impact is valuation loss.
            # Assuming 'expense' account covers operational loss/waste for simplicity.
            if accounts['expense']:
                jv = M['JournalEntry']()
                jv.number = generate_code("JV-WASTE")
                jv.date = wr.recorded_at.date()
                jv.reference = f"PO {po.code}"
                jv.description = f"Waste Production {wr.waste_type}"
                jv.status = 'posted'
                jv.source = 'waste'
                jv.created_by = creator
                jv.created_at = wr.recorded_at
                bulk_journals.append(jv)

                # Line
                cost_val = waste_qty * (cons.unit_cost if hasattr(cons, 'unit_cost') else Decimal("100"))
                line = M['JournalLine']()
                line.account = accounts['expense']
                line.debit = cost_val
                line.credit = Decimal("0")
                line.description = f"Beban Waste {cons.component.sku}"
                line.journal_entry = jv
                bulk_journal_lines.append(line)
                
                total_waste += 1

    # ══════════════════════════════════════════════════════════════════════
    # SAVING DATA
    # ══════════════════════════════════════════════════════════════════════
    
    print(f"\n[SAVE] Saving data to database...")
    
    with transaction.atomic():
        print(f"  1. Creating Orders ({len(bulk_orders)})...")
        created_orders = M['Order'].objects.bulk_create(bulk_orders)
        order_map = {o.customer_name + str(o.created_at): o for o in created_orders} # Map to link items
        
        # We need a robust way to link Items to Orders since bulk_create returns objects with PKs
        # But our bulk_order_items list contains objects with placeholder FKs (None).
        # Strategy: Zip based on index.
        
        # Since we appended items to bulk_order_items in order of orders, we can re-iterate.
        # This is tricky in a script. Better to assign IDs after creation.
        
        # Re-construct Order -> Items mapping properly
        # We'll assume order_index corresponds.
        order_idx = 0
        created_orders_iter = iter(created_orders)
        
        # Re-iterate logic to link items? No, let's just loop by index
        # Because OrderItem has order FK. We need the ID.
        
        # Let's re-create the mapping approach:
        # We have `bulk_orders` list. `bulk_create` returns list with same order.
        saved_orders = M['Order'].objects.bulk_create(bulk_orders)
        
        # Now link OrderItems
        # The `bulk_order_items` list was appended sequentially.
        item_idx = 0
        for i, order_obj in enumerate(saved_orders):
            # Find how many items this order had.
            # We lost the count. 
            # Let's do it the manual way if strictly needed, or simpler:
            # Create Order, then Create Items inside loop for this specific mapping? 
            # No, bulk_create is too fast to lose.
            
            # Hack: Just filter `bulk_order_items` that match index?
            # We can't.
            pass

        # REFACTOR SAVE STRATEGY FOR FK RELATIONSHIPS
        # Since we need valid PKs for OrderItems, Payments, Journals:
        # We will save Orders first.
        
        # 1. Save Orders
        print(f"  1. Orders ({len(bulk_orders)})...")
        saved_orders = M['Order'].objects.bulk_create(bulk_orders)
        order_ids = [o.id for o in saved_orders]
        
        # 2. Save OrderItems (Need to assign Order ID)
        # We stored items sequentially. We need to know how many items per order.
        # Actually, we can iterate `bulk_order_items` and assign ID incrementally 
        # BUT we need to know which ID belongs to which order.
        # Let's re-map: `items_per_order` list was not saved.
        
        # Let's do: Create a map `order_count = 0`.
        # Iterate through `bulk_order_items`. Since they were appended per order...
        # We need to know the count.
        
        # OK, let's look at the generation loop again.
        # `for _ in range(num_orders):`
        # Inside loop: `for oi, sub in items_buffer: bulk_order_items.append(oi)`
        
        # We missed capturing `items_count_per_order`.
        # Let's do a smaller transaction loop or regenerate mapping?
        # The cleanest way now without rewriting the whole generator logic above:
        # Just create Items one by one or in small chunks per order.
        
        # Actually, for ~200k items, single inserts are slow.
        # Let's assume we can iterate `saved_orders` and `bulk_order_items` if we had the counts.
        # We don't.
        
        # BACKUP PLAN: Create a temporary list of (OrderObject, [ItemObjects]) before saving.
        pass

    # RESTARTING SAVE LOGIC FOR SAFETY
    # Since we need FKs, we organize data better first.
    
    # Re-run logic briefly to group? No, too expensive.
    # Let's clear buffers and just insert sequentially for Orders/Items to ensure integrity,
    # then Bulk for the rest.
    
    # Re-strategy:
    # 1. Save Orders (Bulk).
    # 2. Loop Orders (created) -> Create Items (Bulk per order? No, just Bulk all items by manually assigning IDs).
    #    We can do this: `OrderItem(order_id=saved_orders[i].id, ...)`
    
    # But we need to match indices. 
    # `bulk_order_items` contains items for `bulk_orders[i]`.
    # If we know how many items per order, we can slice `bulk_order_items`.
    # We don't know.
    
    # FIX: We will reconstruct the lists here. 
    # Since we cannot easily go back, I will modify the generator loop to return structured data.
    pass

# OVERWRITING THE MAIN LOGIC WITH SAFE SAVING STRATEGY
def run_fill_v2():
    print("\n[INIT] Loading Master Data...")
    customers = list(M['Customer'].objects.all()[:5000])
    actors = get_actors()
    accounts = get_accounts()
    transfers = list(M['Transfer'].objects.filter(status='received').select_related('destination_location', 'created_by').order_by('created_at'))
    prod_orders = list(M['ProductionOrder'].objects.filter(status='completed').select_related('created_by').order_by('created_at')[:1000])
    
    print("  Data loaded.")

    # Use lists of dictionaries or objects to be saved
    # We will structure: [ {'order': OrderObj, 'items': [ItemObjs], 'payment': PaymentObj, 'journal': JVObj, 'lines': [LineObjs]} ]
    
    transactions_data = []
    
    # Helper to create ID placeholders
    # We will use the objects themselves.

    # LOOP 1: SALES
    for trf in transfers:
        trf_items = M['TransferItem'].objects.filter(transfer=trf).select_related('variant')
        if not trf_items: continue
        
        store_loc = trf.destination_location
        num_orders = random.randint(1, 2)
        base_date = make_aware(trf.created_at) + timedelta(hours=random.randint(2, 48))
        cashier = random.choice(actors)
        customer = random.choice(customers)

        for k in range(num_orders):
            total_amount = Decimal("0")
            items_buffer = []
            
            order = M['Order']()
            order.customer_name = customer.name
            order.status = 'completed'
            order.customer = customer
            order.cashier = cashier
            order.created_at = base_date + timedelta(minutes=k*5)
            order.change_amount = Decimal("0")
            order.dining_option = random.choice(['dine_in', 'take_away'])
            order.order_type = 'pos'
            order.payment_method = random.choice(['cash', 'transfer', 'qris', 'card'])
            order.payment_status = 'paid'
            order.shift_id = f"S-{base_date.hour}"
            order.table_number = f"T-{random.randint(1, 20)}"

            for ti in trf_items:
                sold_qty = int(ti.quantity_received * random.uniform(0.1, 0.8) / num_orders)
                if sold_qty <= 0: continue
                
                price_sell = ti.variant.price_sell or ti.variant.price_buy * Decimal("1.3")
                subtotal = price_sell * sold_qty
                total_amount += subtotal
                
                oi = M['OrderItem']()
                oi.quantity = sold_qty
                oi.price = price_sell
                oi.variant = ti.variant
                oi.discount_amount = Decimal("0")
                oi.discount_percent = Decimal("0")
                oi.notes = "Generated from Transfer"
                items_buffer.append((oi, subtotal))
            
            if not items_buffer: continue
            
            order.paid_amount = total_amount
            
            # Payment
            pay = M['Payment']()
            pay.payment_number = generate_code("PAY")
            pay.payment_date = order.created_at.date()
            pay.amount = total_amount
            pay.payment_method = order.payment_method
            pay.status = 'paid'
            pay.received_by = cashier
            pay.reference_number = order.customer_name[:20]
            pay.notes = "Auto Payment"
            pay.created_at = order.created_at
            
            # Journal
            jv = M['JournalEntry']()
            jv.number = generate_code("JV-SALES")
            jv.date = order.created_at.date()
            jv.reference = f"Order-REF"
            jv.description = f"Sales POS {store_loc.name}"
            jv.status = 'posted'
            jv.source = 'sales'
            jv.created_by = cashier
            jv.created_at = order.created_at
            
            line1 = M['JournalLine']()
            line1.account = accounts['cash']
            line1.debit = total_amount
            line1.credit = Decimal("0")
            line1.description = "Penjualan Tunai/Card"
            
            line2 = M['JournalLine']()
            line2.account = accounts['sales']
            line2.debit = Decimal("0")
            line2.credit = total_amount
            line2.description = "Pendapatan Penjualan"
            
            transactions_data.append({
                'order': order,
                'items': items_buffer,
                'payment': pay,
                'journal': jv,
                'lines': [line1, line2]
            })

    # LOOP 2: WASTE
    waste_data = []
    for po in prod_orders:
        consumptions = M['MatConsumption'].objects.filter(production_order=po).select_related('component')
        if not consumptions: continue
        if random.random() > CFG['waste_rate']: continue

        prod_date = make_aware(po.started_at) if po.started_at else make_aware(po.created_at)
        creator = po.created_by if po.created_by else random.choice(actors)
        
        for cons in random.sample(consumptions, min(2, len(consumptions))):
            waste_qty = cons.quantity * Decimal(str(random.uniform(0.01, 0.05)))
            if waste_qty < Decimal("0.01"): continue
            
            wr = M['WasteRecord']()
            wr.production_order = po
            wr.component = cons.component
            wr.waste_type = random.choice(['damage', 'expired', 'process_loss', 'spillage'])
            wr.quantity = waste_qty
            wr.unit = cons.unit
            wr.recorded_at = prod_date + timedelta(hours=4)
            wr.notes = f"Waste for PO {po.code}"
            
            jv = M['JournalEntry']()
            jv.number = generate_code("JV-WASTE")
            jv.date = wr.recorded_at.date()
            jv.reference = f"PO {po.code}"
            jv.description = f"Waste {wr.waste_type}"
            jv.status = 'posted'
            jv.source = 'waste'
            jv.created_by = creator
            jv.created_at = wr.recorded_at
            
            cost_val = waste_qty * (cons.unit_cost if hasattr(cons, 'unit_cost') else Decimal("100"))
            line = M['JournalLine']()
            line.account = accounts['expense']
            line.debit = cost_val
            line.credit = Decimal("0")
            line.description = f"Beban Waste {cons.component.sku}"
            
            waste_data.append({
                'waste': wr,
                'journal': jv,
                'line': line
            })

    # SAVING PHASE
    print(f"\n[SAVE] Committing {len(transactions_data)} Sales & {len(waste_data)} Waste records...")
    
    with transaction.atomic():
        # 1. Save Orders
        # We need to map ID updates
        saved_orders = M['Order'].objects.bulk_create([d['order'] for d in transactions_data])
        
        # 2. Link Items, Payments, Journals
        # We assume index match
        final_items = []
        final_payments = []
        final_journals = []
        final_lines = []
        
        for i, data in enumerate(transactions_data):
            o_id = saved_orders[i].id
            
            # Items
            for oi_obj, sub in data['items']:
                oi_obj.order_id = o_id
                final_items.append(oi_obj)
            
            # Payment
            pay_obj = data['payment']
            pay_obj.order_id = o_id
            final_payments.append(pay_obj)
            
            # Journal
            jv_obj = data['journal']
            jv_obj.reference = f"Order #{o_id}"
            final_journals.append(jv_obj)
            
            # Lines
            for ln_obj in data['lines']:
                ln_obj.journal_entry = jv_obj
                final_lines.append(ln_obj)

        # Save Items
        if final_items: M['OrderItem'].objects.bulk_create(final_items)
        
        # Save Payments
        if final_payments: M['Payment'].objects.bulk_create(final_payments)
        
        # Save Waste + Waste Journals
        if waste_data:
            final_waste = []
            final_waste_journals = []
            final_waste_lines = []
            
            for d in waste_data:
                final_waste.append(d['waste'])
                final_waste_journals.append(d['journal'])
                d['line'].journal_entry = d['journal'] # Link
                final_waste_lines.append(d['line'])
                
            if final_waste: M['WasteRecord'].objects.bulk_create(final_waste)
            final_journals.extend(final_waste_journals)
            final_lines.extend(final_waste_lines)
        
        # Save All Journals & Lines
        if final_journals:
            saved_journals = M['JournalEntry'].objects.bulk_create(final_journals)
            
            # Re-link lines to their journals (waste lines included)
            # We need to map Journal index to Line index.
            # Sales journals come first.
            # Let's just update journal_id for lines.
            
            # Split lines map? 
            # Simpler: Assign journal entry object to line object (done).
            # But bulk_create lines needs ID.
            
            # We need a flat list of lines, but we need to know which journal they belong to.
            # The `ln_obj.journal_entry` variable currently holds the *unsaved* JV object.
            # `bulk_create(Journal)` returns saved objects with IDs.
            
            # We need to zip `saved_journals` with `final_lines`.
            # Issue: `final_lines` contains 2 lines per sales, 1 line per waste.
            # `saved_journals` is 1 per sales, 1 per waste.
            # So `final_lines` is not 1:1 with `saved_journals`.
            
            # Workaround: Map Journal object (identity) to ID after save.
            journal_id_map = {obj: obj.id for obj in saved_journals}
            
            for ln in final_lines:
                # ln.journal_entry is the original object
                ln.journal_entry_id = journal_id_map.get(ln.journal_entry)
                
            M['JournalLine'].objects.bulk_create(final_lines)

    print("\n[DONE] Process finished.")

if __name__ == "__main__":
    try:
        run_fill_v2()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        traceback.print_exc()