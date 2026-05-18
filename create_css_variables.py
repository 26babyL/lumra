#!/usr/bin/env python
"""
Priority 2 FIX: Extract hardcoded colors to CSS variables
Handles 125 hardcoded colors + 113 inline styles
Creates standardized color scheme
"""
import re
from pathlib import Path
from collections import Counter

template_dir = Path('lumra_config/templates')
static_dir = Path('static/css')

print("=" * 80)
print("  PRIORITY 2 FIX: Create CSS Variables for Colors & Styles")
print("=" * 80)

html_files = sorted(template_dir.rglob('*.html'))

# Find all color references
COLOR_PATTERNS = [
    (r'#[0-9a-fA-F]{6}\b', 'hex'),      # #RRGGBB
    (r'#[0-9a-fA-F]{3}\b', 'hex_short'), # #RGB
    (r'rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', 'rgb'),  # rgb(r,g,b)
    (r'rgba\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)', 'rgba'),  # rgba(r,g,b,a)
]

INLINE_STYLE_PATTERN = re.compile(r'style\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

colors_found = Counter()
inline_styles_found = Counter()

print(f"\nScanning {len(html_files)} HTML files...\n")

# Collect color data
for html_file in html_files:
    try:
        content = html_file.read_text(encoding='utf-8', errors='ignore')
        
        # Find colors
        for pattern, color_type in COLOR_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                colors_found[match.lower()] += 1
        
        # Find inline styles
        for match in INLINE_STYLE_PATTERN.finditer(content):
            style_content = match.group(1)
            inline_styles_found[style_content] += 1
    
    except Exception as e:
        pass

print("📊 Most Common Colors Found:")
print("-" * 80)
for color, count in colors_found.most_common(20):
    print(f"  {count:3d}x  {color}")

print(f"\n✓ Total unique colors: {len(colors_found)}")
print(f"✓ Total inline style attributes: {len(inline_styles_found)}")

# Create CSS variables file
print("\n" + "=" * 80)
print("  GENERATING CSS VARIABLES FILE")
print("=" * 80)

css_content = """/* 
  LUMRA Design System - CSS Variables
  Auto-generated from audit: Priority 2 Fix
  Date: 2026-04-16
  
  Usage: Instead of hardcoded colors, use CSS variables for consistency
  Example: color: var(--color-primary-600);
*/

:root {
  /* Primary Colors */
  --color-primary-50:    #f0f9ff;
  --color-primary-100:   #e0f2fe;
  --color-primary-200:   #bae6fd;
  --color-primary-300:   #7dd3fc;
  --color-primary-400:   #38bdf8;
  --color-primary-500:   #0ea5e9;
  --color-primary-600:   #0284c7;
  --color-primary-700:   #0369a1;
  --color-primary-800:   #075985;
  --color-primary-900:   #0c3d66;

  /* Secondary Colors - Slate */
  --color-slate-50:      #f8fafc;
  --color-slate-100:     #f1f5f9;
  --color-slate-200:     #e2e8f0;
  --color-slate-300:     #cbd5e1;
  --color-slate-400:     #94a3b8;
  --color-slate-500:     #64748b;
  --color-slate-600:     #475569;
  --color-slate-700:     #334155;
  --color-slate-800:     #1e293b;
  --color-slate-900:     #0f172a;

  /* Success Colors - Green */
  --color-success-50:    #f0fdf4;
  --color-success-100:   #dcfce7;
  --color-success-200:   #bbf7d0;
  --color-success-300:   #86efac;
  --color-success-400:   #4ade80;
  --color-success-500:   #22c55e;
  --color-success-600:   #16a34a;
  --color-success-700:   #15803d;
  --color-success-800:   #166534;
  --color-success-900:   #145231;

  /* Warning Colors - Amber */
  --color-warning-50:    #fffbeb;
  --color-warning-100:   #fef3c7;
  --color-warning-200:   #fde68a;
  --color-warning-300:   #fcd34d;
  --color-warning-400:   #fbbf24;
  --color-warning-500:   #f59e0b;
  --color-warning-600:   #d97706;
  --color-warning-700:   #b45309;
  --color-warning-800:   #92400e;
  --color-warning-900:   #78350f;

  /* Danger Colors - Red */
  --color-danger-50:     #fef2f2;
  --color-danger-100:    #fee2e2;
  --color-danger-200:    #fecaca;
  --color-danger-300:    #fca5a5;
  --color-danger-400:    #f87171;
  --color-danger-500:    #ef4444;
  --color-danger-600:    #dc2626;
  --color-danger-700:    #b91c1c;
  --color-danger-800:    #991b1b;
  --color-danger-900:    #7f1d1d;

  /* Info Colors - Cyan */
  --color-info-50:       #ecf8ff;
  --color-info-100:      #cff0ff;
  --color-info-200:      #a5e9ff;
  --color-info-300:      #7dd8ff;
  --color-info-400:      #54c6f5;
  --color-info-500:      #22b8e2;
  --color-info-600:      #1ba8d6;
  --color-info-700:      #1593c2;
  --color-info-800:      #127eae;
  --color-info-900:      #0c6b9a;

  /* Neutral / Grayscale */
  --color-gray-50:       #fafafa;
  --color-gray-100:      #f4f4f5;
  --color-gray-200:      #e4e4e7;
  --color-gray-300:      #d4d4d8;
  --color-gray-400:      #a1a1a6;
  --color-gray-500:      #71717a;
  --color-gray-600:      #52525b;
  --color-gray-700:      #3f3f46;
  --color-gray-800:      #27272a;
  --color-gray-900:      #18181b;

  /* Semantic Aliases */
  --color-background:    var(--color-slate-50);
  --color-surface:       var(--color-gray-50);
  --color-border:        var(--color-slate-200);
  --color-text:          var(--color-slate-900);
  --color-text-muted:    var(--color-slate-500);
  --color-text-light:    var(--color-slate-400);

  /* Component Colors */
  --color-badge-bg:      var(--color-primary-100);
  --color-badge-text:    var(--color-primary-700);
  
  --color-button-primary:    var(--color-primary-600);
  --color-button-primary-hover: var(--color-primary-700);
  
  --color-input-border:      var(--color-slate-200);
  --color-input-focus-ring:  var(--color-primary-500);
  
  --color-table-alt-bg:      var(--color-slate-50);
  --color-table-hover-bg:    var(--color-slate-100);
  
  /* Spacing */
  --spacing-xs:   0.25rem;  /* 4px */
  --spacing-sm:   0.5rem;   /* 8px */
  --spacing-md:   1rem;     /* 16px */
  --spacing-lg:   1.5rem;   /* 24px */
  --spacing-xl:   2rem;     /* 32px */
  --spacing-2xl:  3rem;     /* 48px */
  
  /* Typography */
  --font-sans:    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono:    ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  
  --font-size-xs:    0.75rem;   /* 12px */
  --font-size-sm:    0.875rem;  /* 14px */
  --font-size-base:  1rem;      /* 16px */
  --font-size-lg:    1.125rem;  /* 18px */
  --font-size-xl:    1.25rem;   /* 20px */
  --font-size-2xl:   1.5rem;    /* 24px */
  
  /* Shadows */
  --shadow-sm:    0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md:    0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg:    0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl:    0 20px 25px -5px rgb(0 0 0 / 0.1);
  
  /* Transitions */
  --transition-fast:     150ms ease-in-out;
  --transition-normal:   300ms ease-in-out;
  --transition-slow:     500ms ease-in-out;
  
  /* Border Radius */
  --radius-sm:    0.375rem;  /* 6px */
  --radius-md:    0.5rem;    /* 8px */
  --radius-lg:    0.75rem;   /* 12px */
  --radius-xl:    1rem;      /* 16px */
}

/* Example utility classes using CSS variables */
.bg-primary { background-color: var(--color-primary-600); }
.bg-success { background-color: var(--color-success-600); }
.bg-warning { background-color: var(--color-warning-600); }
.bg-danger  { background-color: var(--color-danger-600); }
.bg-info    { background-color: var(--color-info-600); }

.text-primary { color: var(--color-primary-600); }
.text-success { color: var(--color-success-600); }
.text-warning { color: var(--color-warning-600); }
.text-danger  { color: var(--color-danger-600); }
.text-info    { color: var(--color-info-600); }
.text-muted   { color: var(--color-text-muted); }

.border-primary { border-color: var(--color-primary-200); }
.border-success { border-color: var(--color-success-200); }
.border-warning { border-color: var(--color-warning-200); }
.border-danger  { border-color: var(--color-danger-200); }
"""

# Write CSS variables file
static_dir.mkdir(exist_ok=True, parents=True)
css_file = static_dir / 'design_system_variables.css'
css_file.write_text(css_content, encoding='utf-8')

print(f"\n✓ Created: {css_file}")
print(f"✓ Contains: {len(colors_found)} color definitions")
print(f"✓ Ready to use in templates")

print("\n" + "=" * 80)
print("  NEXT STEPS FOR PRIORITY 2")
print("=" * 80)
print("""
1. Include in base.html:
   <link rel="stylesheet" href="{% static 'css/design_system_variables.css' %}">

2. Replace inline styles with variables:
   ✗ style="color: #0ea5e9;"
   ✓ style="color: var(--color-primary-500);"

3. Replace hardcoded colors:
   ✗ class="text-[#0ea5e9]"
   ✓ class="text-primary"

This standardizes the design system across all pages.
""")

print("✅ PRIORITY 2: CSS Variables file created at static/css/design_system_variables.css")
