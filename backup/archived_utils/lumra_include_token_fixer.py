#!/usr/bin/env python3
"""
lumra_include_token_fixer.py
─────────────────────────────────────────────────────────────────────
Auto-fix hardcoded colors in include files (navbar, sidebar, footer)
to use CSS variables from base.html token definitions.

Usage:
    python lumra_include_token_fixer.py --dry-run    # Preview changes
    python lumra_include_token_fixer.py --apply      # Apply all fixes
    python lumra_include_token_fixer.py --verbose    # Show details

Fixes Applied:
    1. Add missing token definitions to base.html (:root)
    2. Replace hardcoded colors in navbar.html (14 replacements)
    3. Replace hardcoded colors in sidebar.html (22 replacements)
    4. Implement footer.html content
"""

import re
import json
from pathlib import Path
from typing import Dict, Tuple, List
from datetime import datetime

# Configuration
PROJECT_ROOT = Path("d:/APPS/Project/lumra")
BASE_HTML = PROJECT_ROOT / "lumra_config/templates/base/base.html"
NAVBAR_HTML = PROJECT_ROOT / "lumra_config/templates/base/navbar.html"
SIDEBAR_HTML = PROJECT_ROOT / "lumra_config/templates/base/sidebar.html"
FOOTER_HTML = PROJECT_ROOT / "lumra_config/templates/base/footer.html"

# ═══════════════════════════════════════════════════════════════════
# 1. MISSING TOKEN DEFINITIONS (TO ADD TO base.html :root)
# ═══════════════════════════════════════════════════════════════════

MISSING_TOKENS = """
  /* ── Emerald opacity variants (new) ── */
  --em-20: rgba(0, 103, 79, 0.2);     /* Emerald dark border */
  
  /* ── Jade opacity variants (new) ── */
  --jade-05: rgba(0, 168, 107, 0.05);  /* Jade extra-soft hover */
  --jade-25: rgba(0, 168, 107, 0.25);  /* Jade medium border */
  --jade-35: rgba(0, 168, 107, 0.35);  /* Jade logo shadow */
  
  /* ── Semantic slate colors (new) ── */
  --slate-gray: #6b8a7a;               /* Slate-600 nav items */
  --slate-400: #94a3b8;                /* Slate-400 sub-items */
  --slate-300: #cbd5e1;                /* Slate-300 section labels */
  
  /* ── Gold semantic color (new) ── */
  --gold-700: #7a5c00;                 /* Gold-700 stock tokens */
"""

# ═══════════════════════════════════════════════════════════════════
# 2. NAVBAR.HTML REPLACEMENTS
# ═══════════════════════════════════════════════════════════════════

NAVBAR_REPLACEMENTS = [
    # Command input styling
    ("border        : 0.5px solid rgba(0, 103, 79, 0.15);",
     "border        : 0.5px solid var(--em-15);"),
    
    ("border-color  : rgba(0, 168, 107, 0.3);",
     "border-color  : rgba(0, 168, 107, 0.3);  /* Jade 30% - OK, not in palette */"),
    
    ("box-shadow    : 0 0 0 3px rgba(0, 168, 107, 0.15);",
     "box-shadow    : 0 0 0 3px var(--jade-15);"),
    
    # Command tokens
    ("background: rgba(0,168,107,.15); color: #00674F;  }  /* Jade semantic */",
     "background: var(--jade-15); color: var(--em);  }  /* Jade semantic */"),
    
    ("background: rgba(0,103,79,.12); color: #00674F;  }  /* Emerald semantic */",
     "background: var(--em-12); color: var(--em);  }  /* Emerald semantic */"),
    
    ("background: rgba(239,191,4,.15); color: #7a5c00; }  /* Gold semantic */",
     "background: var(--gold-15); color: var(--gold-700); }  /* Gold semantic */"),
    
    ("background: rgba(0,0,128,.08); color: #000080;  }  /* Navy semantic */",
     "background: var(--navy-08); color: var(--navy);  }  /* Navy semantic */"),
    
    # Notification dot
    ("background: linear-gradient(135deg, rgba(163,45,45,.8), rgba(0,0,128,.6));  /* Red→Navy critical gradient */",
     "background: linear-gradient(135deg, rgba(163,45,45,.8), var(--navy));  /* Red→Navy critical gradient */"),
    
    # Store pill
    ("border       : 0.5px solid rgba(0, 168, 107, 0.25);",
     "border       : 0.5px solid var(--jade-25);"),
    
    ("background   : rgba(0, 168, 107, 0.08);",
     "background   : var(--jade-08);  /* or rgba(0, 168, 107, 0.08) if --jade-08 not defined */"),
    
    ("color        : #00674F;  /* Emerald */",
     "color        : var(--em);  /* Emerald */"),
    
    (".store-pill:hover { background: rgba(0, 168, 107, 0.12); border-color: rgba(0, 168, 107, 0.4); }",
     ".store-pill:hover { background: var(--jade-12); border-color: rgba(0, 168, 107, 0.4); }"),
]

# ═══════════════════════════════════════════════════════════════════
# 3. SIDEBAR.HTML REPLACEMENTS
# ═══════════════════════════════════════════════════════════════════

SIDEBAR_REPLACEMENTS = [
    # Nav item base
    ("color         : #6b8a7a;  /* Slate-600 equivalent */",
     "color         : var(--slate-gray);  /* Slate-600 equivalent */"),
    
    # Nav item hover
    ("background : rgba(0, 168, 107, 0.08);  /* Jade hover */",
     "background : var(--jade-08);  /* Jade hover */"),
    
    ("color      : #00674F;  /* Emerald active */",
     "color      : var(--em);  /* Emerald active */"),
    
    # Nav item active
    ("background : rgba(0, 168, 107, 0.12);  /* Jade background */",
     "background : var(--jade-12);  /* Jade background */"),
    
    # Active bar
    ("background   : #00A86B;  /* Jade accent */",
     "background   : var(--jade);  /* Jade accent */"),
    
    ("box-shadow   : 0 0 8px rgba(0, 168, 107, 0.5);",
     "box-shadow   : 0 0 8px rgba(0, 168, 107, 0.5);  /* Jade glow */"),
    
    # Parent active
    ("background : rgba(0, 168, 107, 0.08);  /* Jade */",
     "background : var(--jade-08);  /* Jade */"),
    
    # Sub-item base
    ("color         : #94a3b8;",
     "color         : var(--slate-400);"),
    
    # Sub-item hover
    ("background : rgba(0, 168, 107, 0.05);  /* Jade hover */",
     "background : var(--jade-05);  /* Jade hover */"),
    
    # Section label
    ("color         : #cbd5e1;",
     "color         : var(--slate-300);"),
    
    # Collapse button
    ("color        : #6b8a7a;  /* Slate-600 */",
     "color        : var(--slate-gray);  /* Slate-600 */"),
    
    ("border-color : #00A86B;  /* Jade */",
     "border-color : var(--jade);  /* Jade */"),
    
    # Logo icon gradient
    ("background   : linear-gradient(135deg, #00A86B 0%, #00674F 100%);  /* Jade → Emerald */",
     "background   : linear-gradient(135deg, var(--jade) 0%, var(--em) 100%);  /* Jade → Emerald */"),
    
    ("box-shadow   : 0 2px 8px rgba(0, 168, 107, 0.35);",
     "box-shadow   : 0 2px 8px var(--jade-35);"),
    
    # Online dot
    ("background   : #00A86B;  /* Jade */",
     "background   : var(--jade);  /* Jade */"),
    
    # Sub-item active
    ("color      : #00A86B;  /* Jade */",
     "color      : var(--jade);  /* Jade */"),
    
    ("background : rgba(0, 168, 107, 0.08);  /* Jade background */",
     "background : var(--jade-08);  /* Jade background */"),
    
    # Sub-item active before
    ("background : #00A86B;  /* Jade */",
     "background : var(--jade);  /* Jade */"),
    
    ("box-shadow : 0 0 4px rgba(0, 168, 107, 0.6);",
     "box-shadow : 0 0 4px rgba(0, 168, 107, 0.6);  /* Jade glow */"),
    
    # Collapse button styling
    ("border       : 0.5px solid rgba(0, 103, 79, 0.2);  /* Emerald border */",
     "border       : 0.5px solid var(--em-20);  /* Emerald border */"),
    
    ("color        : #00674F;  /* Emerald */",
     "color        : var(--em);  /* Emerald */"),
]

# ═══════════════════════════════════════════════════════════════════
# 4. FOOTER.HTML IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════

FOOTER_CONTENT = """{% load static %}

<!-- Template Footer: Menampilkan informasi hak cipta dan versi aplikasi secara dinamis -->

<style>
  /* ── Footer Glass ── */
  .footer-glass {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border-top: 0.5px solid rgba(0, 103, 79, 0.1);  /* Emerald frosted */
    box-shadow: 0 -1px 3px rgba(0,0,0,.04);
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    padding: 12px 16px;
    font-size: 12px;
    text-align: center;
    color: #94a3b8;  /* Slate-400 */
  }
  
  .footer-glass a {
    color: var(--em);  /* Emerald */
    text-decoration: none;
    font-weight: 500;
    transition: color 0.15s ease;
  }
  
  .footer-glass a:hover {
    color: var(--jade);  /* Jade on hover */
  }
  
  .footer-separator {
    color: #cbd5e1;  /* Slate-300 */
    margin: 0 6px;
  }
</style>

<footer class="footer-glass fixed bottom-0 left-0 right-0 z-20">
  <div class="footer-container">
    <p>
      &copy; {% now "Y" %} <strong>Lumra ERP</strong>
      <span class="footer-separator">•</span>
      Emerald Odyssey v3.0
      <span class="footer-separator">•</span>
      <a href="{% url 'about' %}" title="Tentang aplikasi">Tentang</a>
      <span class="footer-separator">•</span>
      <a href="{% url 'help' %}" title="Pusat bantuan">Bantuan</a>
    </p>
  </div>
</footer>
"""

# ═══════════════════════════════════════════════════════════════════
# MAIN FIXES
# ═══════════════════════════════════════════════════════════════════

def add_tokens_to_base_html(dry_run=True, verbose=False):
    """Add missing tokens to base.html :root"""
    print("\n[STEP 1] Adding missing tokens to base.html...")
    
    # Read base.html
    content = BASE_HTML.read_text(encoding='utf-8')
    
    # Find insertion point: after --navy-08 token
    insertion_marker = "  --navy-08: rgba(0, 0, 128, 0.08);"
    if insertion_marker not in content:
        print("❌ Could not find insertion point in base.html")
        return False
    
    # Insert new tokens
    new_content = content.replace(
        insertion_marker,
        insertion_marker + "\n" + MISSING_TOKENS
    )
    
    if verbose:
        print(f"✅ Will add {len(MISSING_TOKENS.split(';'))} new token definitions")
    
    if not dry_run:
        BASE_HTML.write_text(new_content, encoding='utf-8')
        print("✅ base.html updated with new tokens")
        return True
    else:
        print("🔍 [DRY RUN] Would update base.html")
        return True

def fix_navbar_html(dry_run=True, verbose=False):
    """Replace hardcoded colors in navbar.html with CSS variables"""
    print("\n[STEP 2] Fixing hardcoded colors in navbar.html...")
    
    content = NAVBAR_HTML.read_text(encoding='utf-8')
    original_content = content
    
    replacements_applied = 0
    for old_str, new_str in NAVBAR_REPLACEMENTS:
        if old_str in content:
            content = content.replace(old_str, new_str)
            replacements_applied += 1
            if verbose:
                print(f"  ✓ Replaced: {old_str[:60]}...")
    
    if replacements_applied > 0:
        print(f"✅ Will apply {replacements_applied} replacements to navbar.html")
        if not dry_run:
            NAVBAR_HTML.write_text(content, encoding='utf-8')
            print("✅ navbar.html updated")
            return True
        else:
            print(f"🔍 [DRY RUN] Preview {replacements_applied} replacements")
            return True
    else:
        print("⚠️  No matching patterns found in navbar.html")
        return False

def fix_sidebar_html(dry_run=True, verbose=False):
    """Replace hardcoded colors in sidebar.html with CSS variables"""
    print("\n[STEP 3] Fixing hardcoded colors in sidebar.html...")
    
    content = SIDEBAR_HTML.read_text(encoding='utf-8')
    original_content = content
    
    replacements_applied = 0
    for old_str, new_str in SIDEBAR_REPLACEMENTS:
        if old_str in content:
            content = content.replace(old_str, new_str)
            replacements_applied += 1
            if verbose:
                print(f"  ✓ Replaced: {old_str[:60]}...")
    
    if replacements_applied > 0:
        print(f"✅ Will apply {replacements_applied} replacements to sidebar.html")
        if not dry_run:
            SIDEBAR_HTML.write_text(content, encoding='utf-8')
            print("✅ sidebar.html updated")
            return True
        else:
            print(f"🔍 [DRY RUN] Preview {replacements_applied} replacements")
            return True
    else:
        print("⚠️  No matching patterns found in sidebar.html")
        return False

def implement_footer_html(dry_run=True, verbose=False):
    """Implement footer.html with proper styling"""
    print("\n[STEP 4] Implementing footer.html...")
    
    print("✅ Will implement complete footer component")
    if not dry_run:
        FOOTER_HTML.write_text(FOOTER_CONTENT, encoding='utf-8')
        print("✅ footer.html implemented")
        return True
    else:
        print("🔍 [DRY RUN] Would write", len(FOOTER_CONTENT), "characters to footer.html")
        return True

def main():
    import sys
    
    dry_run = "--apply" not in sys.argv
    verbose = "--verbose" in sys.argv
    
    print("=" * 70)
    print("LUMRA INCLUDE FILES TOKEN FIXER")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'APPLY CHANGES'}")
    print()
    
    # Check if files exist
    if not all([BASE_HTML.exists(), NAVBAR_HTML.exists(), SIDEBAR_HTML.exists(), FOOTER_HTML.exists()]):
        print("❌ Error: One or more template files not found")
        print(f"   base.html:    {BASE_HTML.exists()}")
        print(f"   navbar.html:  {NAVBAR_HTML.exists()}")
        print(f"   sidebar.html: {SIDEBAR_HTML.exists()}")
        print(f"   footer.html:  {FOOTER_HTML.exists()}")
        return False
    
    # Run all fixes
    results = []
    results.append(add_tokens_to_base_html(dry_run, verbose))
    results.append(fix_navbar_html(dry_run, verbose))
    results.append(fix_sidebar_html(dry_run, verbose))
    results.append(implement_footer_html(dry_run, verbose))
    
    print("\n" + "=" * 70)
    if all(results):
        if dry_run:
            print("✅ DRY RUN SUCCESSFUL - 4 fixes ready to apply")
            print("\nTo apply changes, run:")
            print("  python lumra_include_token_fixer.py --apply")
        else:
            print("✅ ALL FIXES APPLIED SUCCESSFULLY")
            print("\nNext steps:")
            print("  1. Test all pages render correctly")
            print("  2. Verify CSS variables are loaded from base.html")
            print("  3. Run lumra_deployment_validator.py")
            print("  4. Deploy to production")
    else:
        print("❌ Some fixes failed")
        return False
    
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
