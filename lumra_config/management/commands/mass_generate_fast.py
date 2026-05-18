"""
LUMRA ERP - Fast Mass Data Generation
Generate produk biji kopi + variants + recipes tanpa tergantung Gemini quota
Gunakan hardcoded data yang sudah siap + minimal AI calls
"""

from decimal import Decimal
from datetime import datetime
import time

from django.core.management.base import BaseCommand
from lumra_config.models import (
    Location, Category, Unit, Vendor, Product, ProductVariant, 
    Recipe, RecipeCategory
)

# Terminal Colors
class C:
    BOLD = '\033[1m'
    RESET = '\033[0m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'

def print_header(title, char='='):
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

# Comprehensive coffee bean name database (100+ entries)
COFFEE_NAMES = [
    # Ethiopian Origins
    "Ethiopian Yirgacheffe", "Ethiopian Sidamo", "Ethiopian Harrar", "Ethiopian Lekempti",
    "Ethiopian Limmu", "Ethiopian Djimmah", "Ethiopian Abaya",
    
    # Colombian Varieties
    "Colombian Geisha", "Colombian Bourbon", "Colombian Typica", "Colombian Caturra",
    "Colombian Catuai", "Colombian Maragogipe", "Colombian Supremo", "Colombian Excelso",
    "Colombian Extra", "Colombian Huila", "Colombian Nariño", "Colombian Tolima",
    
    # Brazilian Beans
    "Brazilian Arabica", "Brazilian Robusta", "Brazilian Santos", "Brazilian Espresso Blend",
    "Brazilian Natural Process", "Brazilian Pulped Natural", "Brazilian Fermented",
    "Brazilian Minas Gerais", "Brazilian São Paulo", "Brazilian Paraná",
    
    # Indonesian Coffees
    "Indonesian Sumatra Mandheling", "Indonesian Gayo Mountain", "Indonesian Lintong",
    "Indonesian Sulawesi Toraja", "Indonesian Bali Blue Moon", "Indonesian Flores",
    "Indonesian Java", "Indonesian Timor", "Indonesian Papua New Guinea",
    
    # Central American
    "Costa Rican Tarrazú", "Costa Rican Central Valley", "Costa Rican Brunca",
    "Guatemalan Antigua", "Guatemalan Huehuetenango", "Guatemalan Atitlán",
    "Salvadoran Santa Ana", "Salvadoran Pacaya", "Salvadoran Chalchuapa",
    "Honduran Copán", "Honduran Comayagua", "Nicaraguan Matagalpa",
    
    # East African
    "Kenyan AA", "Kenyan AB", "Kenyan Peaberry", "Kenyan Nyeri",
    "Tanzanian Peaberry", "Tanzanian Kilimanjaro", "Tanzanian Mbeya",
    "Rwandan Red Bourbon", "Burundian Bourbon", "Ugandan Robusta",
    
    # South American
    "Peruvian Chanchamayo", "Peruvian Cusco", "Peruvian Amazon",
    "Ecuadorian Galapagos", "Ecuadorian Vilcabamba", "Ecuadorian Sumaco",
    "Bolivian Typica", "Bolivian Yungas", "Bolivian Organic",
    
    # Asian-Pacific
    "Vietnamese Robusta", "Vietnamese Arabica", "Vietnamese Dark Roast",
    "Indian Monsooned Malabar", "Indian Mysore", "Indian Plantation AA",
    "Malaysian Robusta", "Philippine Benguet", "Thai Arabica",
    
    # Specialty Blends & Microlots
    "Single Origin Microlot", "Limited Microlot Reserve", "Rare Lot Expression",
    "Processing Innovation", "Anaerobic Fermented", "Honey-Processed Premium",
    "Washed & Fermented", "Natural Orange Wine", "Extended Fermentation",
    "Cold Mountain Altitude", "High Elevation Micro", "Peak Season Select",
]

# Variant size options
VARIANT_SIZES = ["250g", "500g", "1kg", "2kg"]

# Variant modifiers
VARIANT_MODIFIERS = [
    ("Light Roast", 1.0),
    ("Medium Roast", 1.05),
    ("Dark Roast", 1.1),
    ("French Roast", 1.15),
]

class Command(BaseCommand):
    help = 'Fast mass generate coffee bean products without heavy AI dependency'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of products to generate')
        parser.add_argument('--variants-per-product', type=int, default=3, help='Variants per product')
        parser.add_argument('--no-variants', action='store_true', help='Skip variant creation')
        parser.add_argument('--batch-size', type=int, default=10, help='Batch size for printing')

    def handle(self, *args, **options):
        self.run_fast_generation(
            count=options['count'],
            variants_per_product=options['variants_per_product'],
            skip_variants=options['no_variants'],
            batch_size=options['batch_size'],
        )

    def run_fast_generation(self, count=100, variants_per_product=3, skip_variants=False, batch_size=10):
        print_header("LUMRA ERP - FAST MASS DATA GENERATION", "═")
        print_info(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"Target: {count} produk biji kopi")
        print_info(f"Variants/Produk: {variants_per_product if not skip_variants else 0}")
        print_info(f"Mode: Optimized dengan fallback data\n")

        try:
            # Setup
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
            
            recipe_cat, _ = RecipeCategory.objects.get_or_create(
                name="Kopi Specialty",
                defaults={'description': 'Premium coffee roasting formulas'}
            )
            print_success(f"Kategori Resep: {recipe_cat.name}")
            
            vendor = Vendor.objects.first()
            if not vendor:
                vendor = Vendor.objects.create(
                    name="Premium Coffee Importers",
                    contact_person="Manager",
                    email="import@coffee.com",
                    phone="021-9999-9999"
                )
            print_success(f"Vendor: {vendor.name}")
            
            # ════════════════════════════════════════════════════════════
            # MAIN GENERATION LOOP
            # ════════════════════════════════════════════════════════════
            
            print_header(f"Generating {count} Coffee Products", "=")
            
            products_created = 0
            variants_created = 0
            recipes_created = 0
            errors = 0
            
            # Repeat coffee names if count > available
            coffee_list = (COFFEE_NAMES * ((count // len(COFFEE_NAMES)) + 1))[:count]
            
            for idx, coffee_name in enumerate(coffee_list, 1):
                try:
                    # Add batch number to make unique
                    unique_name = f"{coffee_name} #{idx}"
                    
                    # Create product
                    product, created = Product.objects.get_or_create(
                        name=unique_name,
                        defaults={
                            'category': biji_kopi_cat,
                            'unit': kg_unit,
                            'description': f"Premium arabica coffee - Batch {idx}",
                            'sell_price': Decimal('95000.00') + (Decimal(idx % 20) * Decimal('5000')),
                        }
                    )
                    
                    if created:
                        products_created += 1
                    
                    # Create variants
                    if not skip_variants:
                        for v_idx in range(min(variants_per_product, len(VARIANT_SIZES))):
                            size = VARIANT_SIZES[v_idx]
                            roast, roast_multiplier = VARIANT_MODIFIERS[v_idx % len(VARIANT_MODIFIERS)]
                            
                            sku = f"COFFEE-{idx:05d}-{v_idx+1}".replace(" ", "")[:50]
                            base_price = product.sell_price * roast_multiplier
                            
                            variant, v_created = ProductVariant.objects.get_or_create(
                                sku=sku,
                                defaults={
                                    'product': product,
                                    'size_weight': size,
                                    'price_buy': base_price * Decimal('0.55'),  # 55% of sell
                                    'price_sell': base_price,
                                }
                            )
                            if v_created:
                                variants_created += 1
                    
                    # Create recipe every 2 products
                    if idx % 2 == 0:
                        recipe_name = f"{coffee_name} Roasting Profile #{idx}"[:255]
                        recipe, r_created = Recipe.objects.get_or_create(
                            name=recipe_name,
                            defaults={
                                'description': f"Optimal roasting & brewing guide - {coffee_name}",
                                'category': recipe_cat,
                                'yield_quantity': Decimal('1'),
                                'yield_unit': kg_unit,
                                'preparation_time': 20 + (idx % 40),
                                'total_cost': product.sell_price * Decimal('0.55'),
                                'cost_per_unit': product.sell_price * Decimal('0.55'),
                            }
                        )
                        if r_created:
                            recipes_created += 1
                    
                    # Print batch summary
                    if idx % batch_size == 0 or idx == count:
                        status = f"{C.GREEN}✓{C.RESET} [{idx}/{count}]"
                        print(f"  {status} {products_created} products | {variants_created} variants | {recipes_created} recipes")
                    
                except Exception as e:
                    errors += 1
                    if idx % batch_size == 0:
                        print_warning(f"Error at item {idx}: {str(e)[:40]}")
            
            # ════════════════════════════════════════════════════════════
            # SUMMARY & STATISTICS
            # ════════════════════════════════════════════════════════════
            
            print_header("RINGKASAN HASIL", "=")
            
            print(f"\n{C.BOLD}Data Created:{C.RESET}\n")
            print_success(f"Produk Baru: {products_created}")
            if not skip_variants:
                print_success(f"Variants Baru: {variants_created}")
            print_success(f"Recipes Baru: {recipes_created}")
            print_success(f"Errors: {errors}")
            
            # Database stats
            total_products = Product.objects.count()
            total_variants = ProductVariant.objects.count()
            total_recipes = Recipe.objects.count()
            total_in_category = Product.objects.filter(category=biji_kopi_cat).count()
            
            print(f"\n{C.BOLD}Database Status:{C.RESET}\n")
            print_info(f"Total Produk: {total_products}")
            print_info(f"Produk di kategori 'Biji Kopi': {total_in_category}")
            print_info(f"Total Variants: {total_variants}")
            print_info(f"Total Recipes: {total_recipes}")
            
            # Estimation
            print(f"\n{C.BOLD}Estimasi Data:{C.RESET}\n")
            total_variants_all = total_variants if not skip_variants else 0
            total_rows = total_products + total_variants_all + total_recipes
            print_info(f"Total Rows Created: {total_rows}")
            print_info(f"Storage Size (approx): {total_rows * 2}KB")
            
            print(f"\n{C.GREEN}[GENERATION COMPLETE]{C.RESET}\n")
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Successfully created {products_created} products!")
            )
            
        except Exception as e:
            print_error(f"Fatal: {str(e)}")
            import traceback
            traceback.print_exc()
            self.stdout.write(self.style.ERROR(f"✗ Failed: {str(e)}"))


if __name__ == '__main__':
    pass
