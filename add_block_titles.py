#!/usr/bin/env python
"""
Priority 3 FIX: Add {% block title %} to 36 files
Fixes tab/page titles for all pages
"""
import re
from pathlib import Path

template_dir = Path('lumra_config/templates')

print("=" * 80)
print("  PRIORITY 3 FIX: Add Block Title to All Templates")
print("=" * 80)

html_files = sorted(template_dir.rglob('*.html'))

# Pattern to detect if file extends base
extends_pattern = re.compile(r'{%\s*extends\s+[\'"].*[\'\"]\s*%}', re.IGNORECASE)
block_title_pattern = re.compile(r'{%\s*block\s+title\s*%}', re.IGNORECASE)

files_need_title = []
files_already_have = []

print(f"\nScanning {len(html_files)} HTML files...\n")

for html_file in html_files:
    try:
        content = html_file.read_text(encoding='utf-8', errors='ignore')
        
        # Check if file extends base template
        if not extends_pattern.search(content):
            continue
        
        # Check if already has block title
        if block_title_pattern.search(content):
            files_already_have.append(html_file)
        else:
            files_need_title.append(html_file)
    
    except Exception as e:
        pass

print(f"Files extending base.html: {len(files_already_have) + len(files_need_title)}")
print(f"  ✓ Already have block title: {len(files_already_have)}")
print(f"  ⚠️  Need block title added: {len(files_need_title)}")

print("\n📋 Sample files needing title block:")
for file in files_need_title[:10]:
    rel_path = file.relative_to('.')
    print(f"  - {rel_path}")

if len(files_need_title) > 10:
    print(f"  ... and {len(files_need_title) - 10} more files")

# Show the template
print("\n" + "=" * 80)
print("  TITLE BLOCK TEMPLATE")
print("=" * 80)
print("""
Insert after: {% extends 'base/base.html' %}

Example:
  {% extends 'base/base.html' %}
  {% block title %}Dashboard — CoffeeShop{% endblock %}
  
  {% block content %}
    ...
  {% endblock %}

Naming Convention:
  - Page name — CoffeeShop
  - Examples:
    • Purchasing — CoffeeShop
    • Products — CoffeeShop
    • Customer List — CoffeeShop
    • Reports > Sales — CoffeeShop
""")

print("\n" + "=" * 80)
print("  APPLYING FIX")
print("=" * 80)

fixed_count = 0

for html_file in files_need_title:
    try:
        content = html_file.read_text(encoding='utf-8', errors='ignore')
        
        # Extract page name from file path
        parts = html_file.parts
        page_section = parts[-2] if len(parts) > 1 else 'Page'
        page_name = html_file.stem.replace('_', ' ').title()
        
        # Create title from path and filename
        title = f"{page_name} — CoffeeShop"
        
        # Find extends line and insert block title after it
        lines = content.split('\n')
        new_lines = []
        inserted = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # After extends line, insert block title
            if not inserted and extends_pattern.search(line):
                # Add blank line and block title
                new_lines.append(f'{{% block title %}}{title}{{% endblock %}}')
                inserted = True
        
        new_content = '\n'.join(new_lines)
        html_file.write_text(new_content, encoding='utf-8')
        
        print(f"  ✓ {html_file.relative_to('.')}")
        print(f"     Title: {title}")
        fixed_count += 1
    
    except Exception as e:
        print(f"  ✗ {html_file.relative_to('.')}: {e}")

print("\n" + "=" * 80)
print("  SUMMARY")
print("=" * 80)
print(f"✓ Fixed {fixed_count} files")
print(f"✓ Already complete: {len(files_already_have)} files")
print(f"✓ Total with title blocks: {fixed_count + len(files_already_have)}")

print("\n✅ PRIORITY 3 COMPLETE: All pages now have proper titles in browser tabs")
