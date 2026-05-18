#!/usr/bin/env python3
"""
LUMRA Comprehensive Tailwind Color Fixer
Handles edge cases and remaining Tailwind color utilities after initial batch conversion.
"""

import re
from pathlib import Path
import sys

# All patterns to convert - comprehensive coverage
COMPREHENSIVE_PATTERNS = [
    # ===== TEXT COLORS =====
    # Emerald shades
    (r"\btext-emerald-300\b", 'style="color: var(--em-12);"', "text emerald-300"),
    (r"\btext-emerald-(?:600|700)\b", 'style="color: var(--em);"', "text emerald primary"),
    (r"\btext-emerald-(?:400|500)\b", 'style="color: var(--jade);"', "text emerald secondary"),
    (r"\btext-emerald-800\b", 'style="color: var(--navy);"', "text emerald-800"),
    (r"\btext-emerald-900\b", 'style="color: var(--navy);"', "text emerald-900"),
    
    # Green shades
    (r"\btext-green-(?:600|700)\b", 'style="color: var(--jade);"', "text green primary"),
    (r"\btext-green-(?:400|500)\b", 'style="color: var(--jade);"', "text green secondary"),
    
    # ===== BACKGROUND COLORS =====
    # Emerald shades
    (r"\bbg-emerald-(?:50|100)\b", 'style="background-color: var(--em-08);"', "bg emerald light"),
    (r"\bbg-emerald-(?:600|700)\b", 'style="background-color: var(--em);"', "bg emerald primary"),
    (r"\bbg-emerald-(?:400|500)\b", 'style="background-color: var(--jade);"', "bg emerald secondary"),
    
    # Green shades
    (r"\bbg-green-50\b", 'style="background-color: var(--jade-08);"', "bg green-50"),
    (r"\bbg-green-100\b", 'style="background-color: var(--jade-08);"', "bg green-100"),
    (r"\bbg-green-(?:600|700)\b", 'style="background-color: var(--jade);"', "bg green primary"),
    
    # Teal shades
    (r"\bbg-teal-50\b", 'style="background-color: var(--em-08);"', "bg teal-50"),
    (r"\bbg-teal-100\b", 'style="background-color: var(--em-12);"', "bg teal-100"),
    
    # ===== BORDER COLORS =====
    (r"\bborder-emerald-200\b", 'style="border-color: var(--em-15);"', "border emerald-200"),
    (r"\bborder-emerald-300\b", 'style="border-color: var(--em-12);"', "border emerald-300"),
    (r"\bborder-emerald-400\b", 'style="border-color: var(--jade);"', "border emerald-400"),
    
    # ===== GRADIENT PATTERNS =====
    (r"from-emerald-600\s+to-emerald-700", 'style="background: linear-gradient(135deg, var(--em) 0%, var(--em) 100%);"', "gradient em-em"),
    (r"from-emerald-(?:600|700)\s+to-jade-(?:500|600)", 'style="background: linear-gradient(135deg, var(--em) 0%, var(--jade) 100%);"', "gradient em-jade"),
    (r"from-green-100\s+to-green-200", 'style="background: linear-gradient(135deg, var(--jade-08) 0%, var(--jade-08) 100%);"', "gradient green light"),
    (r"bg-gradient-to-br\s+from-green-100\s+to-green-200", 'style="background: linear-gradient(135deg, var(--jade-08) 0%, var(--jade-08) 100%);"', "gradient br green"),
    
    # ===== SPECIAL CASES =====
    (r"\bbg-emerald-900\b", 'style="background-color: var(--navy);"', "bg emerald-900"),
    (r"\bbg-red-(?:50|100|200)\b", 'style="background-color: var(--em-08);"', "bg red light (convert to em)"),
    (r"\bbg-purple-(?:100|200)\b", 'style="background-color: var(--em-08);"', "bg purple light"),
    (r"\bbg-blue-(?:100|200)\b", 'style="background-color: var(--em-08);"', "bg blue light"),
    
    # ===== OPACITY MODIFIERS =====
    (r"/\d+\b", "", "remove opacity modifiers after all colors"),
]

def fix_file(filepath: Path, dry_run: bool = True) -> tuple[int, list]:
    """Fix remaining Tailwind colors in a file."""
    
    if not filepath.exists():
        return 0, [f"⚠ File not found: {filepath}"]
    
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        replacements_made = 0
        changes = []
        
        for pattern, replacement, description in COMPREHENSIVE_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                old_content = content
                content = re.sub(pattern, replacement, content)
                if content != old_content:
                    count = len(re.findall(pattern, old_content))
                    replacements_made += count
                    changes.append(f"  {count}x {description}")
        
        if replacements_made > 0:
            if not dry_run:
                filepath.write_text(content, encoding='utf-8')
            return replacements_made, changes
        
        return 0, []
    
    except Exception as e:
        return 0, [f"ERROR: {str(e)}"]

def main():
    # Get all page template files
    template_dir = Path("lumra_config/templates/lumra_pages")
    
    if not template_dir.exists():
        print("ERROR: Template directory not found!")
        return False
    
    dry_run = "--apply" not in sys.argv
    verbose = "--verbose" in sys.argv
    target_batch = sys.argv[-1] if len(sys.argv) > 1 and "batch" in sys.argv[-1] else None
    
    print("=" * 70)
    print("LUMRA COMPREHENSIVE TAILWIND -> ODYSSEY FIXER")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print()
    
    html_files = list(template_dir.rglob("*.html"))
    total_replacements = 0
    files_modified = 0
    
    for html_file in sorted(html_files):
        replacements, changes = fix_file(html_file, dry_run)
        
        if replacements > 0:
            files_modified += 1
            total_replacements += replacements
            status = "[DRY RUN]" if dry_run else "[OK]"
            print(f"{status} {html_file.name}: {replacements} conversions")
            
            if verbose:
                for change in changes:
                    print(change)
    
    print()
    print("=" * 70)
    if dry_run:
        print(f"[DRY RUN] Would convert {total_replacements} items in {files_modified} files")
        print("\nTo apply: python lumra_comprehensive_tailwind_fixer.py --apply")
    else:
        print(f"[OK] Converted {total_replacements} items in {files_modified} files")
        print("\nNext: Run validator")
        print("python backup/lumra_deployment_validator.py --generate-report")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()
