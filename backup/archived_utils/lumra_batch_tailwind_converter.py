#!/usr/bin/env python3
"""
lumra_batch_tailwind_converter.py
Convert remaining Tailwind color utilities to Odyssey tokens in batch files.

Batch 3: Inventory (17 files)
Batch 4: Marketing (5 files)
"""

import re
from pathlib import Path

PROJECT_ROOT = Path("d:/APPS/Project/lumra")
TEMPLATES_DIR = PROJECT_ROOT / "lumra_config/templates/lumra_pages"

# Batch file mappings
BATCHES = {
    "batch_3_inventory": [
        "inventory/add_stock_movement.html",
        "inventory/product_details.html",
        "inventory/product_list.html",
        "inventory/products.html",
        "inventory/stock_movement_form.html",
        "inventory/stock_movement.html",
        "inventory/stock_opname_approval_detail.html",
        "inventory/stock_opname_approvals.html",
        "inventory/stock_opname_form.html",
        "inventory/stock_opname_locations.html",
        "inventory/stock_overview.html",
        "inventory/stock_planning.html",
        "inventory/stock_purchasing.html",
        "inventory/supplier_price_confirm_delete.html",
        "inventory/supplier_price_form.html",
        "inventory/supplier_price_list.html",
    ],
    "batch_4_marketing": [
        "marketing/add_campaign.html",
        "marketing/campaign_list.html",
        "marketing/campaign.html",
        "marketing/discount.html",
        "marketing/loyalty_members.html",
    ]
}

# Color conversion map: regex pattern -> replacement
COLOR_REPLACEMENTS = [
    # Emerald 700
    (r"text-emerald-700(?![a-z0-9-])", "\" :style=\"color: var(--em)"),
    (r"bg-emerald-700(?![a-z0-9-])", "\" :style=\"background-color: var(--em)"),
    
    # Emerald 600
    (r"text-emerald-600(?![a-z0-9-])", "\" :style=\"color: var(--em)"),
    (r"bg-emerald-600(?![a-z0-9-])", "\" :style=\"background-color: var(--em)"),
    
    # Emerald 500
    (r"text-emerald-500(?![a-z0-9-])", "\" :style=\"color: var(--jade)"),
    (r"bg-emerald-500(?![a-z0-9-])", "\" :style=\"background-color: var(--jade)"),
    
    # Emerald 400
    (r"text-emerald-400(?![a-z0-9-])", "\" :style=\"color: var(--jade)"),
    (r"bg-emerald-400(?![a-z0-9-])", "\" :style=\"background-color: var(--jade)"),
    
    # Emerald 50
    (r"bg-emerald-50(?![a-z0-9-])", "\" :style=\"background-color: var(--em-08)"),
    (r"text-emerald-50(?![a-z0-9-])", "\" :style=\"color: var(--em-08)"),
    
    # Emerald 100
    (r"bg-emerald-100(?![a-z0-9-])", "\" :style=\"background-color: var(--em-12)"),
    
    # Green 50 / Teal
    (r"bg-green-50(?![a-z0-9-])", "\" :style=\"background-color: var(--jade-08)"),
    (r"bg-teal-50(?![a-z0-9-])", "\" :style=\"background-color: var(--em-08)"),
    
    # Border emerald
    (r"border-emerald-400(?![a-z0-9-])", "\" :style=\"border-color: var(--jade)"),
    (r"border-emerald-200(?![a-z0-9-])", "\" :style=\"border-color: var(--em-15)"),
    (r"border-emerald-300(?![a-z0-9-])", "\" :style=\"border-color: var(--em-12)"),
    
    # Focus rings with emerald
    (r"focus:ring-emerald-500", "focus:ring-offset-0\" :style=\"--ring-color: var(--em)"),
    (r"focus:border-emerald-600", "\" :style=\"--focus-border: var(--em)"),
    (r"focus:border-emerald-400", "\" :style=\"--focus-border: var(--jade)"),
    
    # Hover variants
    (r"hover:bg-emerald-700(?![a-z0-9-])", "hover:opacity-75"),
    (r"hover:bg-emerald-600(?![a-z0-9-])", "hover:opacity-75"),
    (r"hover:text-emerald-700(?![a-z0-9-])", "hover:opacity-75\" :style=\"color: var(--em)"),
    (r"hover:text-emerald-600(?![a-z0-9-])", "hover:opacity-75\" :style=\"color: var(--em)"),
]

def convert_file(filepath: Path, dry_run: bool = True) -> tuple[int, int]:
    """Convert Tailwind colors in a file. Returns (replacements_made, file_size)"""
    
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return 0, 0
    
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    replacements = 0
    
    # Smart replacements using regex with context awareness
    patterns = [
        # Pattern 1: Emerald colors (keeping as primary/em)
        (r"text-emerald-(?:600|700)(?![a-z0-9-])", "style=\"color: var(--em);", "emerald primary text"),
        (r"bg-emerald-(?:600|700)(?![a-z0-9-])", "style=\"background-color: var(--em);", "emerald primary bg"),
        
        # Pattern 2: Jade/green secondary colors
        (r"text-emerald-(?:400|500)(?![a-z0-9-])", "style=\"color: var(--jade);", "emerald secondary text"),
        (r"bg-emerald-(?:400|500)(?![a-z0-9-])", "style=\"background-color: var(--jade);", "emerald secondary bg"),
        
        # Pattern 3: Light backgrounds
        (r"bg-emerald-(?:50|100)(?![a-z0-9-])", "style=\"background-color: var(--em-08);", "emerald light bg"),
        (r"bg-green-(?:50|100)(?![a-z0-9-])", "style=\"background-color: var(--jade-08);", "green light bg"),
        (r"bg-teal-(?:50|100)(?![a-z0-9-])", "style=\"background-color: var(--em-12);", "teal light bg"),
        
        # Pattern 4: Borders
        (r"border-emerald-(?:200|300|400)(?![a-z0-9-])", "style=\"border-color: var(--em-12);", "emerald border"),
        
        # Pattern 5: Focus/hover states (convert to inline or remove)
        (r"focus:(?:ring|border)-emerald-\d+", "", "focus emerald"),
        (r"hover:(?:bg|text)-emerald-\d+", "", "hover emerald"),
    ]
    
    for pattern, replacement, description in patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            replacements += len(matches)
    
    if dry_run:
        if content != original_content:
            print(f"[DRY RUN] {filepath.name}: {replacements} items would be converted")
            return replacements, len(original_content)
        return 0, 0
    else:
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            print(f"[OK] {filepath.name}: {replacements} items converted")
            return replacements, len(original_content)
        return 0, 0

def main():
    import sys
    
    dry_run = "--apply" not in sys.argv
    verbose = "--verbose" in sys.argv
    batch = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1].startswith("batch_") else None
    
    print("=" * 70)
    print("LUMRA BATCH TAILWIND -> ODYSSEY CONVERTER")  
    print("=" * 70)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'APPLY CHANGES'}")
    print()
    
    total_replacements = 0
    total_files = 0
    
    batches_to_run = {batch: BATCHES[batch]} if batch and batch in BATCHES else BATCHES
    
    for batch_name, files in batches_to_run.items():
        print(f"\n[BATCH] {batch_name.upper()}")
        print("-" * 70)
        
        for file_rel_path in files:
            file_path = TEMPLATES_DIR / file_rel_path
            replacements, size = convert_file(file_path, dry_run)
            
            if replacements > 0:
                total_replacements += replacements
                total_files += 1
    
    print("\n" + "=" * 70)
    if total_files > 0:
        if dry_run:
            print(f"[OK] DRY RUN COMPLETE")
            print(f"   Would convert {total_replacements} color items in {total_files} files")
            print(f"\n   To apply changes, run:")
            print(f"   python lumra_batch_tailwind_converter.py --apply")
        else:
            print(f"[OK] CONVERSION COMPLETE")
            print(f"   Converted {total_replacements} color items in {total_files} files")
            print(f"\n   Next: Run validator")
            print(f"   python backup/lumra_deployment_validator.py --generate-report")
    else:
        print("ℹ️  No Tailwind color utilities found to convert")
    
    print("=" * 70)
    return total_files > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
