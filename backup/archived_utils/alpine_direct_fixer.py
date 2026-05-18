#!/usr/bin/env python3
"""
Direct pattern fixer for embedded style= in class attributes
Handles patterns like: class="text-[9px] style="color: var(--em);"
Converts to: class="text-[9px]" style="color: var(--em);"
"""

import re
from pathlib import Path
import json

def fix_embedded_styles_direct(file_path: Path):
    """Fix embedded styles in class and :class attributes"""
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        fixes = []
        
        # Pattern 1: class="...something style="..."...
        # Find the embedded style= and extract both the classes and style
        pattern1 = r'class="([^"]*)?\s+style="([^"]*)?"'
        
        def replace_class_style(match):
            classes = match.group(1).strip() if match.group(1) else ""
            style = match.group(2).strip() if match.group(2) else ""
            
            if classes and style:
                fixes.append(f"Separated: {style[:50]}")
                return f'class="{classes}" style="{style}"'
            return match.group(0)
        
        content = re.sub(pattern1, replace_class_style, content)
        
        # Pattern 2: :class="..."style=" inside it (already quoted)
        # This is in Alpine.js bindings, need to be more careful
        # Pattern: :class="condition ? 'class-name' : 'style=\"...\"'"
        # This is tricky because quotes are nested
        
        # Pattern 3: Look for fas fa- with style embedded
        pattern3 = r'class="(fas\s+fa-[^\s"]*)\s+style="([^"]*)?"'
        
        def replace_icon_style(match):
            icon_class = match.group(1).strip()
            style = match.group(2).strip() if match.group(2) else ""
            
            if icon_class and style:
                fixes.append(f"Separated icon style: {style[:40]}")
                return f'class="{icon_class}" style="{style}"'
            return match.group(0)
        
        content = re.sub(pattern3, replace_icon_style, content)
        
        # Pattern 4: Fix unclosed :class with embedded styles
        # :class="store.status === 'online' ? 'text-green-600 style=\"color: var(--em);\"' : 'text-gray'"?
        # This needs careful handling
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return len(fixes), fixes
        
        return 0, []
    
    except Exception as e:
        return 0, [f"Error: {str(e)}"]

def main():
    template_dir = Path("lumra_config/templates")
    
    if not template_dir.exists():
        print(f"Template directory not found")
        return
    
    print("=" * 80)
    print("DIRECT PATTERN FIXER - Embedded style= in class attributes")
    print("=" * 80 + "\n")
    
    total_files = 0
    fixed_files = 0
    total_fixes = 0
    all_results = []
    
    for html_file in sorted(template_dir.rglob("*.html")):
        fix_count, fix_list = fix_embedded_styles_direct(html_file)
        
        if fix_count > 0:
            fixed_files += 1
            total_fixes += fix_count
            rel_path = html_file.relative_to(template_dir)
            print(f"✅ {rel_path}")
            
            for fix in fix_list[:3]:
                print(f"   - {fix}")
            
            if len(fix_list) > 3:
                print(f"   ... and {len(fix_list) - 3} more")
            
            all_results.append({
                "file": str(rel_path),
                "fixes": fix_count
            })
        
        total_files += 1
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: Fixed {fixed_files}/{total_files} files with {total_fixes} total corrections")
    print("=" * 80)
    
    if all_results:
        with open("direct_fix_results.json", "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"📄 Results saved: direct_fix_results.json")

if __name__ == "__main__":
    main()
