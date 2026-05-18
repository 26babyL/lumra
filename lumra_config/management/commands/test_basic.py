#!/usr/bin/env python
"""
Django management command for LUMRA ERP test
Simpler version that works with actual model structures
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import date
import sys


class Command(BaseCommand):
    help = 'LUMRA ERP — Full Flow Test dengan Gemini AI'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n[OK] Starting LUMRA ERP Full Flow Test\n'))
        
        try:
            from lumra_config.models import Category, Unit, Vendor, Product, Location, Customer
            
            # ═══════════════════════════════════════════════════════════
            # FASE 0: SETUP AWAL
            # ═══════════════════════════════════════════════════════════
            
            self.stdout.write(self.style.HTTP_INFO('\n[FASE 0] SETUP AWAL'))
            
            # Create Locations
            self.stdout.write('[0.1] Creating Locations...')
            locs = {}
            for code, name, ltype in [
                ('TKO-001', 'Main Store', 'store'),
                ('GUD-001', 'Warehouse', 'warehouse'),
                ('DPR-001', 'Production', 'production'),
            ]:
                loc, created = Location.objects.get_or_create(
                    name=name,
                    defaults={'location_type': ltype, 'address': 'Default Address'}
                )
                locs[code] = loc
                status = '[NEW]' if created else '[EXISTS]'
                self.stdout.write(f'  {status} {code}: {loc.name}')
            
            # Create Categories
            self.stdout.write('[0.2] Creating Categories...')
            cats = {}
            for cat_name in ['Minuman', 'Makanan', 'Biji Kopi', 'Bahan Baku']:
                cat, created = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={'description': f'Kategori {cat_name}'}
                )
                cats[cat_name] = cat
                status = '[NEW]' if created else '[EXISTS]'
                self.stdout.write(f'  {status} {cat_name}')
            
            # ═══════════════════════════════════════════════════════════
            # FASE 1: MASTER DATA
            # ═══════════════════════════════════════════════════════════
            
            self.stdout.write(self.style.HTTP_INFO('\n[FASE 1] MASTER DATA'))
            
            # Create Units
            self.stdout.write('[1.1] Creating Units...')
            units = {}
            for unit_name, symbol in [('Cup', 'cup'), ('Pcs', 'pcs'), ('Kg', 'kg'), ('Liter', 'L')]:
                unit, created = Unit.objects.get_or_create(
                    name=unit_name,
                    defaults={'symbol': symbol, 'description': f'{unit_name} unit'}
                )
                units[unit_name] = unit
                status = '[NEW]' if created else '[EXISTS]'
                self.stdout.write(f'  {status} {unit.name} ({unit.symbol})')
            
            # Create Vendors
            self.stdout.write('[1.2] Creating Vendors...')
            vendors = {}
            vendor_data = [
                ('PT. Kopi Nusantara', '021-5555-1111'),
                ('CV. Roaster Indonesia', '021-5555-2222'),
            ]
            for vendor_name, phone in vendor_data:
                vendor, created = Vendor.objects.get_or_create(
                    name=vendor_name,
                    defaults={'phone': phone, 'email': f'{vendor_name.lower()}@example.com'}
                )
                vendors[vendor_name] = vendor
                status = '[NEW]' if created else '[EXISTS]'
                self.stdout.write(f'  {status} {vendor.name} ({phone})')
            
            # Create Products
            self.stdout.write('[1.3] Creating Products...')
            products = {}
            product_list = [
                ('Espresso', 'minuman', Decimal('25000')),
                ('Latte', 'minuman', Decimal('30000')),
                ('Cappuccino', 'minuman', Decimal('32000')),
                ('Croissant', 'makanan', Decimal('15000')),
                ('Sandwich', 'makanan', Decimal('20000')),
                ('Arabica Coffee', 'biji_kopi', Decimal('50000')),
            ]
            
            for prod_name, cat_key, price in product_list:
                # Map category key to actual category
                cat_map = {
                    'minuman': cats.get('Minuman'),
                    'makanan': cats.get('Makanan'),
                    'biji_kopi': cats.get('Biji Kopi'),
                }
                cat = cat_map.get(cat_key)
                unit = units.get('Cup' if cat_key == 'minuman' else ('Pcs' if cat_key == 'makanan' else 'Kg'))
                
                prod, created = Product.objects.get_or_create(
                    name=prod_name,
                    defaults={
                        'category': cat,
                        'unit': unit,
                        'sell_price': price,
                        'description': f'{prod_name} product',
                    }
                )
                products[prod_name] = prod
                status = '[NEW]' if created else '[EXISTS]'
                self.stdout.write(f'  {status} {prod.name}: Rp {price:,.0f}')
            
            # ═══════════════════════════════════════════════════════════
            # FASE 2: CUSTOMER
            # ═══════════════════════════════════════════════════════════
            
            self.stdout.write(self.style.HTTP_INFO('\n[FASE 2] CUSTOMER'))
            
            # Create Customer
            self.stdout.write('[2.1] Creating Customer...')
            customer, created = Customer.objects.get_or_create(
                name='John Doe',
                defaults={
                    'phone': '081234567890',
                    'email': 'john@example.com',
                    'address': 'Jl. Example No. 123'
                }
            )
            status = '[NEW]' if created else '[EXISTS]'
            self.stdout.write(f'  {status} {customer.name}')
            
            # ═══════════════════════════════════════════════════════════
            # SUMMARY
            # ═══════════════════════════════════════════════════════════
            
            self.stdout.write(self.style.HTTP_INFO('\n[SUMMARY] Data Created'))
            self.stdout.write(f'  Locations: {len(locs)}')
            self.stdout.write(f'  Categories: {len(cats)}')
            self.stdout.write(f'  Units: {len(units)}')
            self.stdout.write(f'  Vendors: {len(vendors)}')
            self.stdout.write(f'  Products: {len(products)}')
            self.stdout.write(f'  Customers: 1')
            
            self.stdout.write(self.style.SUCCESS('\n[OK] Test completed successfully!\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] {e}\n'))
            import traceback
            traceback.print_exc()
            sys.exit(1)
