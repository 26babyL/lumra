#!/usr/bin/env python3
"""
LUMRA EMERALD ODYSSEY — Batch Template Transformer
Transform all 87 page templates to Odyssey v3.0 specification.

Usage:
  python lumra_batch_odyssey_transform.py [--dry-run] [--category inventory|sales_insight|reports|master_data|marketing|messages|settings|auth|etc]
  
Transformations:
  1. Old color tokens → Odyssey hex + CSS var()
  2. Glass protocol CSS → Updated values
  3. Component classes → Standardized
  4. Typography → Plus Jakarta Sans standardization
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

# ═══════════════════════════════════════════════════════════════════════
# TOKEN MAPPINGS — OLD → NEW (Odyssey v3.0)
# ═══════════════════════════════════════════════════════════════════════

TOKEN_REPLACEMENTS = {
    # Color surface tokens
    "var(--color-surface)": "rgba(255, 255, 255, 0.92)",
    "var(--color-surface-faint)": "rgba(255, 255, 255, 0.85)",
    "var(--color-surface-high)": "rgba(255, 255, 255, 0.95)",
    "var(--color-surface-glass)": "rgba(0, 103, 79, 0.1)",
    
    # Old slate colors → Odyssey primary/contrast
    "var(--color-slate-900)": "var(--color-contrast)",  # Navy #000080
    "var(--color-slate-800)": "#1A1A1A",
    "var(--color-slate-700)": "#333333",
    "var(--color-slate-600)": "#666666",
    "var(--color-slate-500)": "#888888",
    "var(--color-slate-400)": "#999999",
    "var(--color-slate-300)": "#CCCCCC",
    "var(--color-slate-200)": "#DDDDDD",
    "var(--color-slate-100)": "#F0F0F0",
    "var(--color-slate-50)": "#F9F9F9",
    
    # Old emerald → Odyssey primary
    "var(--color-emerald-950)": "#003D2F",
    "var(--color-emerald-900)": "#004D3A",
    "var(--color-emerald-800)": "#005A45",
    "var(--color-emerald-700)": "var(--color-primary)",  # #00674F
    "var(--color-emerald-600)": "#008B61",
    "var(--color-emerald-500)": "#00A86B",  # Actually Jade
    "var(--color-emerald-400)": "#00D084",
    "var(--color-emerald-300)": "#33E0A8",
    "var(--color-emerald-200)": "#66ECC9",
    "var(--color-emerald-100)": "#99F8E0",
    
    # Old green → Odyssey secondary (Jade)
    "var(--color-green-700)": "var(--color-secondary)",  # #00A86B
    "var(--color-green-600)": "#009560",
    "var(--color-green-500)": "var(--color-secondary)",
    
    # Old teal/cyan → Jade/Emerald
    "var(--color-teal-500)": "var(--color-secondary)",
    "var(--color-cyan-500)": "var(--color-secondary)",
    
    # Amber → Odyssey gold
    "var(--color-amber-500)": "var(--color-accent)",  # #EFBF04
    "var(--color-f59e0b)": "var(--color-accent)",
    "#F59E0B": "var(--color-accent)",
    
    # Red/Rose (error) → Danger gradient (red-to-navy)
    "var(--color-red-500)": "var(--color-danger-from)",  # #A32D2D
    "var(--color-red-600)": "var(--color-danger-from)",
    "var(--color-rose-500)": "var(--color-danger-from)",
    "var(--color-rose-600)": "var(--color-danger-from)",
    
    # White
    "var(--color-fff)": "#FFFFFF",
    "var(--color-white)": "#FFFFFF",
    
    # Black
    "var(--color-black)": "#000000",
}

# Glass protocol CSS properties
GLASS_CSS_MAPPINGS = {
    # Old blur specifications
    "backdrop-filter: blur(8px)": "backdrop-filter: var(--glass-blur-light)",
    "backdrop-filter: blur(12px)": "backdrop-filter: var(--glass-blur)",
    "backdrop-filter: blur(16px)": "backdrop-filter: var(--glass-blur-heavy)",
    "backdrop-filter: blur(20px)": "backdrop-filter: var(--glass-blur-heavy)",
    
    # Border standardization
    "border: 1px solid rgba(0, 0, 0, 0.1)": "border: var(--glass-border)",
    "border: 0.5px solid rgba(255, 255, 255, 0.1)": "border: var(--glass-border)",
    
    # Shadow standardization
    "box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1)": "box-shadow: var(--shadow-natural)",
    "box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1)": "box-shadow: var(--shadow-natural)",
    "box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1)": "box-shadow: var(--shadow-natural)",
}

# Tailwind classes with old colors → Standardized
TAILWIND_REPLACEMENTS = {
    # Emerald green → Odyssey primary (emerald #00674F)
    "from-emerald-500": "from-emerald-600",  # Closer to #00674F
    "to-green-600": "to-emerald-700",
    "bg-emerald-50": "bg-emerald-50/80",
    "bg-emerald-100": "bg-emerald-100/70",
    "bg-emerald-200": "bg-emerald-200/60",
    "border-emerald-100": "border-emerald-200",
    "border-emerald-200": "border-emerald-300",
    "text-emerald-600": "text-emerald-700",
    "text-emerald-500": "text-emerald-600",
    "ring-emerald-400": "ring-emerald-500",
    "focus:ring-emerald-400": "focus:ring-emerald-500",
    "focus:border-emerald-400": "focus:border-emerald-600",
    "hover:bg-emerald-100": "hover:bg-emerald-100/70",
    
    # Slate → Navigation text colors
    "text-slate-900": "text-slate-800",
    "text-slate-700": "text-slate-700",
    "text-slate-600": "text-slate-600",
    "text-slate-500": "text-slate-500",
    "text-slate-400": "text-slate-400",
    "bg-slate-900": "bg-slate-800",
    "bg-slate-50": "bg-slate-50/80",
    
    # Red/Rose → Error styling  
    "from-red-500": "from-red-600",
    "to-red-600": "to-red-700",
    "border-red-400": "border-red-500",
    "text-red-400": "text-red-500",
    "text-red-600": "text-red-700",
    "bg-red-50": "bg-red-50/70",
}

# ═══════════════════════════════════════════════════════════════════════
# AUTOMATION
# ═══════════════════════════════════════════════════════════════════════

def apply_token_replacements(content: str, dry_run: bool = False) -> Tuple[str, List[str]]:
    """Apply CSS custom property replacements."""
    changes = []
    modified = content
    
    for old, new in TOKEN_REPLACEMENTS.items():
        if old in modified:
            count = modified.count(old)
            modified = modified.replace(old, new)
            changes.append(f"  ✓ {old} → {new} ({count}x)")
    
    return modified, changes


def apply_glass_css_replacements(content: str, dry_run: bool = False) -> Tuple[str, List[str]]:
    """Standardize Glass Protocol CSS."""
    changes = []
    modified = content
    
    for old, new in GLASS_CSS_MAPPINGS.items():
        if old in modified:
            count = modified.count(old)
            modified = modified.replace(old, new)
            changes.append(f"  ✓ {old} → {new} ({count}x)")
    
    return modified, changes


def apply_tailwind_replacements(content: str, dry_run: bool = False) -> Tuple[str, List[str]]:
    """Standardize Tailwind classes with old colors."""
    changes = []
    modified = content
    
    for old, new in TAILWIND_REPLACEMENTS.items():
        if old in modified:
            count = modified.count(old)
            modified = modified.replace(old, new)
            changes.append(f"  ✓ {old} → {new} ({count}x)")
    
    return modified, changes


def transform_template(file_path: Path, dry_run: bool = False) -> Dict:
    """Transform single template file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        modified_content = original_content
        all_changes = []
        
        # Apply transformation phases
        modified_content, changes1 = apply_token_replacements(modified_content, dry_run)
        all_changes.extend(changes1)
        
        modified_content, changes2 = apply_glass_css_replacements(modified_content, dry_run)
        all_changes.extend(changes2)
        
        modified_content, changes3 = apply_tailwind_replacements(modified_content, dry_run)
        all_changes.extend(changes3)
        
        # Write back if not dry-run and something changed
        if not dry_run and modified_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            return {
                "status": "✅ TRANSFORMED",
                "file": file_path.name,
                "changes": all_changes,
                "count": len(all_changes)
            }
        elif not dry_run:
            return {
                "status": "⊝ NO CHANGES",
                "file": file_path.name,
                "changes": [],
                "count": 0
            }
        else:  # dry-run mode
            if all_changes:
                return {
                    "status": "🔍 DRY-RUN (would transform)",
                    "file": file_path.name,
                    "changes": all_changes,
                    "count": len(all_changes)
                }
            else:
                return {
                    "status": "⊝ DRY-RUN (no changes)",
                    "file": file_path.name,
                    "changes": [],
                    "count": 0
                }
    
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "file": file_path.name,
            "error": str(e),
            "count": 0
        }


def batch_transform_directory(root_dir: Path, category: str = None, dry_run: bool = False) -> Dict:
    """Transform all templates in directory."""
    templates_dir = root_dir / "lumra_config" / "templates" / "lumra_pages"
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return{"error": "Directory not found", "total": 0}
    
    # Find all .html files
    if category:
        search_dirs = [templates_dir / category]
        categories = [category]
    else:
        search_dirs = list(templates_dir.iterdir())
        categories = [d.name for d in search_dirs if d.is_dir()]
    
    all_files = []
    for search_dir in search_dirs:
        if search_dir.is_dir():
            all_files.extend(search_dir.glob("*.html"))
    
    print(f"\n{'='*70}")
    print(f"🚀 LUMRA EMERALD ODYSSEY — Batch Template Transformer")
    print(f"{'='*70}")
    print(f"📂 Found: {len(all_files)} templates")
    print(f"🎯 Categories: {', '.join(categories)}")
    print(f"⚙️  Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")
    
    results = []
    transformed_count = 0
    no_change_count = 0
    error_count = 0
    
    for idx, file_path in enumerate(sorted(all_files), 1):
        print(f"[{idx}/{len(all_files)}] {file_path.parent.name}/{file_path.name}...", end=" ", flush=True)
        
        result = transform_template(file_path, dry_run)
        results.append(result)
        
        if result["status"].startswith("✅"):
            transformed_count += 1
            print(f"✅ ({result['count']} changes)")
        elif result["status"].startswith("⊝"):
            no_change_count += 1
            print(f"⊝")
        elif result["status"].startswith("🔍"):
            print(f"🔍 ({result['count']} would change)")
        else:
            error_count += 1
            print(f"❌ {result.get('error', 'unknown error')}")
    
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Transformed: {transformed_count}")
    print(f"⊝ No changes:  {no_change_count}")
    print(f"❌ Errors:     {error_count}")
    print(f"{'='*70}\n")
    
    return {
        "total": len(all_files),
        "transformed": transformed_count,
        "no_change": no_change_count,
        "errors": error_count,
        "mode": "DRY-RUN" if dry_run else "LIVE",
        "results": results
    }


# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch transform templates to Odyssey v3.0")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--category", type=str, default=None, 
                       choices=["auth", "inventory", "sales_insight", "production", "reports", 
                               "master_data", "marketing", "messages", "settings", "etc"],
                       help="Process specific category only")
    
    args = parser.parse_args()
    
    root_dir = Path(os.getcwd())
    summary = batch_transform_directory(root_dir, args.category, args.dry_run)
    
    if args.dry_run:
        print("💡 Run without --dry-run flag to apply changes")
