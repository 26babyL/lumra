#!/usr/bin/env python
"""
Priority 1 FIX: Add csrf_token to all <form> tags without it
This is critical for security - forms won't work without CSRF protection
"""
import re
from pathlib import Path

template_dir = Path('lumra_config/templates')

print("=" * 80)
print("  PRIORITY 1 FIX: Add csrf_token to Forms (Security)")
print("=" * 80)

# Find all HTML files
html_files = sorted(template_dir.rglob('*.html'))

# Pattern to find forms without csrf_token
form_pattern = re.compile(r'<form[^>]*?method\s*=\s*["\']post["\']', re.IGNORECASE)
csrf_pattern = re.compile(r'{%\s*csrf_token\s*%}', re.IGNORECASE)

files_to_fix = []
fixed_count = 0

print(f"\nScanning {len(html_files)} HTML files...\n")

for html_file in html_files:
    content = html_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check if file has POST forms
    if form_pattern.search(content):
        # Check if CSRF token already exists
        if not csrf_pattern.search(content):
            files_to_fix.append(html_file)

print(f"Found {len(files_to_fix)} files with forms missing csrf_token:\n")

for i, file in enumerate(files_to_fix[:10], 1):
    rel_path = file.relative_to('.')
    print(f"  {i:2d}. {rel_path}")

if len(files_to_fix) > 10:
    print(f"  ... and {len(files_to_fix) - 10} more files")

print("\n" + "-" * 80)
print("  FIXING STRATEGY:")
print("-" * 80)
print("""
  1. For each form, find: <form ... method="post">
  2. Add {% csrf_token %} as first line after <form> opening
  3. Format: Insert after form tag, before first form field
  
  Pattern to match (method must be POST):
     <form method="post">  OR  <form method='post'>  OR  <form ... method="post" ...>
     
  Insert:
     {% csrf_token %}
""")

# Generate fix script
fix_script = f"""
# Run this to apply fixes:
python fix_csrf_tokens.py

This will:
  - Add csrf_token to {len(files_to_fix)} forms
  - Maintain indentation
  - Preserve file structure
  - Show summary of changes
"""

print(fix_script)

print("\n✅ Analysis complete. Ready for actual fixes with fix_csrf_tokens.py")
