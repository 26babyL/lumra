"""
LUMRA ERP - Mass Data Generation Script
Generate ratusan produk biji kopi + variants + recipes dengan nama dari Gemini
sampai limit API terpenuhi
"""

from decimal import Decimal
from datetime import date, datetime, timezone
import time

from django.core.management.base import BaseCommand
from django.db.models import F

from lumra_config.models import (
    Location, Category, Unit, Vendor, Product, ProductVariant, 
    Recipe, RecipeCategory, Customer, Order
)
from lumra_config.management.commands.gemini_data_generator import CoffeeShopDataGenerator

# Terminal Colors
class C:
    BOLD = '\033[1m'
    RESET = '\033[0m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'

def print_header(title, char='═'):
    width = 70
    print(f"\n{C.BLUE}{char * width}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{title.center(width)}{C.RESET}")
    print(f"{C.BLUE}{char * width}{C.RESET}\n")

def print_success(msg):
    print(f"  {C.GREEN}✓{C.RESET} {msg}")

def print_info(msg):
    print(f"  {C.BLUE}→{C.RESET} {msg}")

def print_warning(msg):
    print(f"  {C.YELLOW}⚠{C.RESET} {msg}")

def print_error(msg):
    print(f"  {C.RED}✗{C.RESET} {msg}")

class Command(BaseCommand):
    help = 'Mass generate coffee bean products with Gemini AI'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of coffee beans to generate')
        parser.add_argument('--variants-per-product', type=int, default=3, help='Variants per product')
        parser.add_argument('--no-variants', action='store_true', help='Skip variant creation')

    def handle(self, *args, **options):
        self.run_mass_generation(
            count=options['count'],
            variants_per_product=options['variants_per_product'],
            skip_variants=options['no_variants']
        )

    def run_mass_generation(self, count=100, variants_per_product=3, skip_variants=False):
        print_header("LUMRA ERP - MASS DATA GENERATION", "═")
        print_info(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"Target: {count} biji kopi + {variants_per_product} variants/produk")
        print_info(f"Mode: {'Produk only' if skip_variants else 'Produk + Variants'}\n")

        try:
            # Initialize Gemini generator
            generator = CoffeeShopDataGenerator(verbose=True)
            
            # Get or create base setup
            print_header("Setup Awal", "─")
            biji_kopi_cat = Category.objects.get_or_create(
                name="Biji Kopi",
                defaults={'parent': None}
            )[0]
            print_success(f"Kategori: {biji_kopi_cat.name}")
            
            kg_unit = Unit.objects.get_or_create(
                name="Kg",
                defaults={'symbol': 'kg'}
            )[0]
            print_success(f"Satuan: {kg_unit.name}")
            
            # Get or create recipe category
            recipe_cat, _ = RecipeCategory.objects.get_or_create(
                name="Kopi Specialty",
                defaults={'description': 'Premium coffee beans recipes'}
            )
            print_success(f"Kategori Resep: {recipe_cat.name}")
            
            # Get first vendor
            vendor = Vendor.objects.first()
            if not vendor:
                print_warning("Tidak ada vendor, membuat default...")
                vendor = Vendor.objects.create(
                    name="Default Coffee Supplier",
                    contact_person="Manager",
                    email="supplier@coffee.com",
                    phone="021-1234567"
                )
                print_success(f"Vendor dibuat: {vendor.name}")
            
            # ════════════════════════════════════════════════════════════
            # MAIN LOOP: Generate Coffee Beans
            # ════════════════════════════════════════════════════════════
            
            print_header(f"Generating {count} Coffee Beans", "▓")
            
            products_created = 0
            variants_created = 0
            recipes_created = 0
            gemini_requests = 0
            
            for i in range(count):
                try:
                    # Generate coffee name from Gemini
                    coffee_names = generator.generate_products("Biji Kopi", 1)
                    gemini_requests += 1
                    
                    if not coffee_names:
                        coffee_names = [f"Coffee Bean Variant #{i+1}"]
                    
                    coffee_name = coffee_names[0] if isinstance(coffee_names, list) else coffee_names
                    
                    # Clean name
                    coffee_name = str(coffee_name).strip()[:255]
                    
                    # Create product
                    product, created = Product.objects.get_or_create(
                        name=coffee_name,
                        defaults={
                            'category': biji_kopi_cat,
                            'unit': kg_unit,
                            'description': f"Premium coffee bean - Batch #{i+1}",
                            'sell_price': Decimal('85000.00') + (Decimal(i % 10) * Decimal('5000')),
                        }
                    )
                    
                    if created:
                        products_created += 1
                        print_success(f"[{i+1}/{count}] {coffee_name}")
                    else:
                        print_info(f"[{i+1}/{count}] {coffee_name} (exists)")
                    
                    # Create ProductVariants if not skipped
                    if not skip_variants:
                        for v in range(variants_per_product):
                            size_names = ["250g", "500g", "1kg"]
                            size_name = size_names[v % len(size_names)]
                            
                            sku = f"{product.id}-{v+1}".replace(" ", "")[:50]
                            price = product.sell_price + (Decimal(v) * Decimal('10000'))
                            
                            variant, v_created = ProductVariant.objects.get_or_create(
                                sku=sku,
                                defaults={
                                    'product': product,
                                    'size_weight': size_name,
                                    'price_buy': price * Decimal('0.6'),  # 60% of sell price
                                    'price_sell': price,
                                }
                            )
                            if v_created:
                                variants_created += 1
                    
                    # Create recipe (untuk coffee roasting formula)
                    if i % 2 == 0:  # Create recipe untuk setiap 2 produk
                        recipe_name = f"{coffee_name} Roasting Formula"
                        recipe, r_created = Recipe.objects.get_or_create(
                            name=recipe_name[:255],
                            defaults={
                                'description': f"Optimal roasting profile for {coffee_name}",
                                'category': recipe_cat,
                                'yield_quantity': Decimal('1'),
                                'yield_unit': kg_unit,
                                'preparation_time': 30 + (i % 60),
                            }
                        )
                        if r_created:
                            recipes_created += 1
                    
                    # Rate limiting di level loop
                    if (i + 1) % 5 == 0:  # Every 5 products
                        time.sleep(2)
                    
                except Exception as e:
                    print_error(f"[{i+1}/{count}] Error: {str(e)[:60]}")
                    # Continue dengan produk berikutnya
                    continue
            
            # ════════════════════════════════════════════════════════════
            # SUMMARY
            # ════════════════════════════════════════════════════════════
            
            print_header("RINGKASAN HASIL", "═")
            
            print(f"\n{C.BOLD}Data yang dibuat:{C.RESET}\n")
            print_success(f"Produk: {products_created}")
            if not skip_variants:
                print_success(f"Variants: {variants_created}")
            print_success(f"Recipes: {recipes_created}")
            
            print(f"\n{C.BOLD}AI Usage:{C.RESET}\n")
            print_success(f"Gemini Requests: {gemini_requests}")
            print_info(f"Estimated Cost: ~${gemini_requests * 0.000001:.4f} (approx)")
            
            total_products = Product.objects.count()
            total_variants = ProductVariant.objects.count()
            total_recipes = Recipe.objects.count()
            
            print(f"\n{C.BOLD}Database Status:{C.RESET}\n")
            print_info(f"Total Produk: {total_products}")
            print_info(f"Total Variants: {total_variants}")
            print_info(f"Total Recipes: {total_recipes}")
            
            print(f"\n{C.GREEN}═ MASS GENERATION COMPLETE ═{C.RESET}\n")
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Generated {products_created} products successfully!")
            )
            
        except Exception as e:
            print_error(f"Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.stdout.write(self.style.ERROR(f"✗ Generation failed: {str(e)}"))


def run_mass_generation_cli(count=100, variants_per_product=3, skip_variants=False):
    """CLI wrapper"""
    cmd = Command()
    cmd.run_mass_generation(count, variants_per_product, skip_variants)


if __name__ == '__main__':
    run_mass_generation_cli()
