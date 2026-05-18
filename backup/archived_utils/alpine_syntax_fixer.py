#!/usr/bin/env python3
"""
Fix Alpine.js `:class` binding syntax errors from token migration
Issues:
1. :class bindings with embedded style=" strings
2. Unclosed class strings (e.g., 'w-[64px] -translate-x-full md:translate-x-0" without closing ')
3. Malformed x-data objects with style attributes
"""

import re
from pathlib import Path

def fix_alpine_syntax(file_path):
    """Fix Alpine.js syntax errors in templates"""
    
    if not file_path.exists():
        return 0, []
    
    content = file_path.read_text(encoding='utf-8')
    original = content
    fixes = []
    
    # Fix 1: Convert style=" inside :class bindings to :style bindings
    # Pattern: :class="condition ? 'style=" something;"' : 'class'"
    # Should be: :class="condition ? 'class' : 'other'" + separate :style binding
    
    # Fix broken class strings with unclosed quotes
    # Pattern: 'w-[240px]' : 'w-[64px] -translate-x-full md:translate-x-0"
    # Should be: 'w-[240px]' : 'w-[64px] -translate-x-full md:translate-x-0'
    
    patterns = [
        # Fix 1: style=" inside :class - convert to proper :style
        (
            r":class=\"condition \? 'style=[^']*' \: '[^']*'",
            lambda m: m.group(0).replace("'style=", "'").replace("'", ":style='").replace("\":","':"),
            "style in :class"
        ),
        
        # Fix 2: Unclosed quote in :class binding with multiple classes
        (
            r":\s*'w-\[64px\]\s+-translate-x-full\s+md:translate-x-0\"",
            ": 'w-[64px] -translate-x-full md:translate-x-0'",
            "unclosed class quote"
        ),
        
        # Fix 3: activeStore.status with style=" embedded
        (
            r":class=\"activeStore\.status === 'online' \? 'style=\"[^\"]*\"' \: '[^']*'\"",
            lambda m: m.group(0).replace("'style=\"", "'online-status'").replace("\"'", "'"),
            "activeStore status style"
        ),
        
        # Fix 4: store.status with style=" embedded  
        (
            r":class=\"store\.status === 'online' \? 'style=\"[^\"]*\"' \: '[^']*'\"",
            lambda m: m.group(0).replace("'style=\"", "'online-status'").replace("\"'", "'"),
            "store status style"
        ),
    ]
    
    # Apply fixes
    for pattern, replacement, description in patterns:
        matches = re.findall(pattern, content)
        if matches:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
            fixes.append(description)
    
    # More aggressive fix: replace entire malformed :class bindings
    # Example: :class="activeStore.status === 'online' ? 'style=" background-color: var(--em-08);"' : 'bg-slate-300'"
    # With: :class="activeStore.status === 'online' ? 'online-indicator' : 'offline-indicator'" + :style binding
    
    # Pattern for style attributes in :class
    style_in_class = re.compile(
        r":class=\"([^\"]*?)\s+\?[^:]*?'style=\"([^\"]*?)\"'[^:]*?:",
        re.MULTILINE | re.DOTALL
    )
    
    if style_in_class.search(content):
        # Get all matches
        matches = style_in_class.findall(content)
        
        # Replace style=" patterns with proper class names
        content = re.sub(
            r":class=\"(.*?)'style=\"([^\"]*?)\"'(.*?)\"",
            r":class=\"\1'on\3\" :style=\"\1 ? {\2} : {}\"",
            content
        )
        fixes.append("moved inline styles to :style binding")
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return len(fixes), fixes
    
    return 0, []

def main():
    print("=" * 80)
    print("ALPINE.JS :CLASS BINDING SYNTAX FIXER")
    print("=" * 80)
    print()
    
    # Find affected files
    template_dir = Path("lumra_config/templates")
    affected_files = [
        "base/sidebar.html",
        "lumra_pages/sales_insight/dashboard.html",
        # Add more as needed
    ]
    
    total_fixes = 0
    files_fixed = 0
    
    for file_path in affected_files:
        full_path = template_dir / file_path
        
        if full_path.exists():
            fixes_count, fixes_list = fix_alpine_syntax(full_path)
            
            if fixes_count > 0:
                files_fixed += 1
                total_fixes += fixes_count
                print(f"[FIXED] {file_path}")
                for fix in fixes_list:
                    print(f"  - {fix}")
            else:
                print(f"[OK] {file_path} - no issues found")
        else:
            print(f"[SKIP] {file_path} - not found")
    
    print()
    print("=" * 80)
    print(f"Fixed {files_fixed} files with {total_fixes} corrections")
    print("=" * 80)

if __name__ == "__main__":
    main()
