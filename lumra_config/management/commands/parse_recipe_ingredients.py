"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  RECIPE INSTRUCTIONS PARSER v2.0 (DYNAMIC LOADER)                         ║
║  Parse kolom instructions → ProductionRecipeIngredients                    ║
║                                                                              ║
║  Usage:                                                                     ║
║    python lumra_config/management/commands/parse_recipe_ingredients.py      ║
║    python lumra_config/management/commands/parse_recipe_ingredients.py      ║
║        --dry-run --recipe-id 403                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import argparse
from decimal import Decimal
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# DJANGO ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_system.settings")

import django
try:
    django.setup()
except Exception as e:
    print(f"❌ Gagal setup Django: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC MODEL LOADER
# Tidak perlu lagi menebak nama app (lumra_config, production, dll).
# Django akan mencarinya sendiri di seluruh INSTALLED_APPS.
# ═══════════════════════════════════════════════════════════════════════════════
from django.apps import apps

def get_model(model_name):
    """Cari model di seluruh app yang terdaftar di settings.INSTALLED_APPS"""
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model(model_name)
            return model
        except LookupError:
            continue
    raise ImportError(f"❌ Model '{model_name}' tidak ditemukan di manapun! Cek nama modelnya.")

print("🔍 Loading models...")
ProductionRecipes = get_model('ProductionRecipes')
ProductionRecipeIngredients = get_model('ProductionRecipeIngredients')
ProductionRecipeCategories = get_model('ProductionRecipeCategories')
LumraConfigProducts = get_model('LumraConfigProducts')
LumraConfigProductvariants = get_model('LumraConfigProductvariants')
Units = get_model('Units')
print("✅ All models loaded successfully.")

from django.db import transaction
from django.db.models import Q


# ═══════════════════════════════════════════════════════════════════════════════
# PARSING LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def parse_instructions(instructions: str) -> list:
    ingredients = []
    parts = instructions.split('|')

    for part in parts:
        part = part.strip()
        if not part or part.lower().startswith('total'):
            continue

        if ':' not in part:
            continue

        name_part, qty_part = part.split(':', 1)
        name = name_part.strip()
        qty_part = qty_part.strip()

        match = re.match(r'([\d.]+)\s*([a-zA-Z]+)(?:\s*\(([\d.]+)%\))?', qty_part)
        if not match:
            print(f"  ⚠ Gagal parse qty: '{qty_part}'")
            continue

        quantity = float(match.group(1))
        unit_str = match.group(2).lower()
        percentage = float(match.group(3)) if match.group(3) else None

        processing = None
        base_name = name
        proc_match = re.search(r'\(([^)]+)\)', name)
        if proc_match:
            processing = proc_match.group(1)
            base_name = name[:proc_match.start()].strip()

        ingredients.append({
            'raw_name': name,
            'base_name': base_name,
            'processing': processing,
            'quantity': quantity,
            'unit_str': unit_str,
            'percentage': percentage,
        })

    return ingredients


# ═══════════════════════════════════════════════════════════════════════════════
# LOOKUP HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def find_variant(ingredient: dict, all_variants) -> tuple:
    raw_name = ingredient['raw_name']
    base_name = ingredient['base_name']
    processing = ingredient['processing']

    # Strategy 1: Exact
    variant = all_variants.filter(name__iexact=raw_name).first()
    if variant:
        return variant, 'exact'

    # Strategy 2: Base name contains
    variant = all_variants.filter(name__icontains=base_name).first()
    if variant:
        return variant, 'base_contains'

    # Strategy 3: Combined dengan processing
    if processing:
        proc_clean = processing.replace('/', ' ').strip()
        search_term = f"{base_name} {proc_clean}"
        variant = all_variants.filter(name__icontains=search_term).first()
        if variant:
            return variant, 'combined'

    # Strategy 4: 2 Kata kunci utama (menggunakan Q objects)
    keywords = base_name.split()[:2]
    if len(keywords) >= 2:
        variant = all_variants.filter(
            Q(name__icontains=keywords[0]) & Q(name__icontains=keywords[1])
        ).first()
        if variant:
            return variant, 'keyword'

    # Strategy 5: Kata pertama saja (longgar)
    if keywords:
        variant = all_variants.filter(name__icontains=keywords[0]).first()
        if variant:
            return variant, 'loose_first_word'

    return None, None


def find_unit(unit_str: str):
    mapping = {
        'g': 'gram', 'gr': 'gram', 'kg': 'kilogram', 'mg': 'milligram',
        'ml': 'milliliter', 'l': 'liter', 'pcs': 'pcs', 'oz': 'ounce',
    }
    unit_name = mapping.get(unit_str.lower(), unit_str.lower())
    return Units.objects.filter(name__iexact=unit_name).first()


def get_variant_unit_cost(variant) -> Decimal:
    """Ambil harga beli variant (disesuaikan: price_buy berdasarkan generator mu)"""
    if hasattr(variant, 'price_buy') and variant.price_buy:
        return variant.price_buy
    if hasattr(variant, 'purchase_price') and variant.purchase_price:
        return variant.purchase_price
    if hasattr(variant, 'cost_price') and variant.cost_price:
        return variant.cost_price
    return Decimal('0')


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
@transaction.atomic
def run_parser(dry_run=False, recipe_id=None, category_name=None):
    qs = ProductionRecipes.objects.filter(is_archived=False)

    if recipe_id:
        qs = qs.filter(id=recipe_id)
        print(f"Filter recipe ID: {recipe_id}")

    if category_name:
        qs = qs.filter(category__name__iexact=category_name)
        print(f"Filter category: {category_name}")

    recipes = qs.select_related('category', 'yield_unit')
    total_recipes = recipes.count()

    if total_recipes == 0:
        print("⚠ Tidak ada resep ditemukan.")
        return

    print(f"\n{'='*70}")
    print(f"Found {total_recipes} recipe(s) to process")
    if dry_run:
        print("🔒 DRY RUN MODE - tidak ada data yang ditulis")
    print(f"{'='*70}\n")

    all_variants = LumraConfigProductvariants.objects.select_related('product').all()
    stats = {
        'recipes_processed': 0,
        'ingredients_created': 0,
        'ingredients_skipped': 0,
        'ingredients_not_found': 0,
    }

    for recipe in recipes:
        category_label = f"[{recipe.category.name}] " if recipe.category else ""
        print(
            f"\n{'─'*70}\n"
            f"📋 {category_label}{recipe.name} (ID: {recipe.id})\n"
            f"   Yield: {recipe.yield_quantity} | Total Cost: {recipe.total_cost}\n"
            f"   Instructions: {recipe.instructions[:80]}..."
        )

        ingredients = parse_instructions(recipe.instructions)

        if not ingredients:
            print("   ⚠ Tidak ada ingredient ter-parse")
            stats['recipes_processed'] += 1
            continue

        print(f"   Parsed {len(ingredients)} ingredient(s):\n")
        now = datetime.now()

        for ing in ingredients:
            variant, match_type = find_variant(ing, all_variants)

            if not variant:
                print(f"   ✗ [{ing['quantity']}{ing['unit_str']}] '{ing['raw_name']}' → VARIANT TIDAK DITEMUKAN")
                stats['ingredients_not_found'] += 1
                continue

            unit = find_unit(ing['unit_str'])
            unit_label = unit.name if unit else ing['unit_str']

            existing = ProductionRecipeIngredients.objects.filter(
                recipe=recipe, variant=variant
            ).first()

            if existing:
                print(f"   ~ [{ing['quantity']}{unit_label}] '{ing['raw_name']}' → {variant.name} (SUDAH ADA, match: {match_type})")
                stats['ingredients_skipped'] += 1
                continue

            unit_cost = get_variant_unit_cost(variant)
            subtotal_cost = unit_cost * Decimal(str(ing['quantity']))

            notes_parts = [f"Parsed from instructions: {ing['raw_name']}"]
            if ing['percentage']:
                notes_parts.append(f"Percentage: {ing['percentage']}%")
            if match_type != 'exact':
                notes_parts.append(f"Match type: {match_type}")

            if not dry_run:
                ProductionRecipeIngredients.objects.create(
                    quantity=Decimal(str(ing['quantity'])),
                    unit_cost=unit_cost,
                    subtotal_cost=subtotal_cost,
                    notes=' | '.join(notes_parts),
                    recipe=recipe,
                    variant=variant,
                    unit=unit,
                    created_at=now,
                    updated_at=now,
                )

            match_indicator = '✓' if match_type == 'exact' else '~'
            print(f"   {match_indicator} [{ing['quantity']}{unit_label}] '{ing['raw_name']}' → {variant.name} (match: {match_type}, cost: {unit_cost})")
            stats['ingredients_created'] += 1

        stats['recipes_processed'] += 1

    # ── Summary ──
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}")
    print(f"  Recipes processed  : {stats['recipes_processed']}")
    print(f"  Ingredients created: {stats['ingredients_created']}")
    print(f"  Ingredients skipped: {stats['ingredients_skipped']}")
    print(f"  Not found          : {stats['ingredients_not_found']}")

    if stats['ingredients_not_found'] > 0:
        print("\n💡 Tip: Untuk ingredient yang tidak ditemukan, pastikan nama variant")
        print("   di LumraConfigProductvariants cocok dengan nama di instructions.")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Recipe Instructions → Ingredients")
    parser.add_argument('--dry-run', action='store_true', help='Hanya simulasi, tidak menulis ke DB')
    parser.add_argument('--recipe-id', type=int, default=None, help='Proses satu resep saja (by ID)')
    parser.add_argument('--category-name', type=str, default=None, help='Filter berdasarkan nama kategori resep')
    
    args = parser.parse_args()
    
    run_parser(
        dry_run=args.dry_run, 
        recipe_id=args.recipe_id, 
        category_name=args.category_name
    )