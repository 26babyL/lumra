#!/usr/bin/env python3
"""
Comprehensive Alpine.js and class attribute fixer
Fixes embedded style=" inside class and :class attributes
"""

import re
from pathlib import Path
from typing import Tuple, List
import json

class AlpineStyleFixer:
    def __init__(self):
        self.fixes_by_file = {}
        self.template_dir = Path("lumra_config/templates")
    
    def fix_embedded_styles_in_class(self, content: str) -> Tuple[str, List[str]]:
        """Fix embedded style= attributes inside class= attributes"""
        fixes = []
        
        # Pattern 1: class="...style="..." in regular class attribute
        # Find: class="some-class style="color: var(--X);"..."
        # Replace with: class="some-class" and separate :style
        
        # This is complex because style= is embedded in quoted string
        # We need to find patterns like: class="text[...] style="color: var(--X);"..."
        
        # Pattern: class=" ... style=" ... ;" ...
        pattern1 = r'class="([^"]*?)\s+style="([^"]*?)"([^"]*?)"'
        
        def replace1(match):
            classes = match.group(1).strip()
            style_content = match.group(2).strip()
            remaining = match.group(3).strip()
            
            # Extract style property and value
            # e.g., "color: var(--em)" -> color, "var(--em)"
            style_parts = style_content.split(':', 1)
            if len(style_parts) == 2:
                prop = style_parts[0].strip()
                value = style_parts[1].strip().rstrip(';')
                
                # Convert CSS property to camelCase for JavaScript
                # color -> color, background-color -> backgroundColor
                js_prop = ''.join(word if i == 0 else word.capitalize() 
                                for i, word in enumerate(prop.split('-')))
                
                # Create separate :style binding
                result = f'class="{classes}" :style="{{ {js_prop}: \'{value}\' }}"'
                fixes.append(f"Separated style from class: {style_content}")
                return result
            
            return match.group(0)
        
        new_content = re.sub(pattern1, replace1, content)
        
        return new_content if new_content != content else content, fixes
    
    def fix_embedded_styles_in_alpine_class(self, content: str) -> Tuple[str, List[str]]:
        """Fix embedded style= inside :class= bindings"""
        fixes = []
        
        # Pattern: :class="condition ? 'style=\"color: var(--X);\"' : 'class'"
        # This is very complex because of quote escaping
        
        # First, let's find all :class=" ... " patterns
        alpine_class_pattern = r':class="([^"]*?(?:\'style="[^"]*?"\'[^"]*?)*[^"]*)"'
        
        def fix_alpine_class(content_str):
            current = content_str
            count = 0
            
            # Find all :class=" bindings
            matches = list(re.finditer(r':class="[^"]*(?:\'style="[^"]*?"\')?[^"]*"', current))
            
            # Process from end to start to preserve positions
            for match in reversed(matches):
                binding = match.group(0)
                
                # Check if it has embedded style="..."
                if "'style=\"" in binding:
                    # Extract the binding content (without :class=" and ")
                    content_part = binding[8:-1]  # Remove :class=" and "
                    
                    # Try to separate styles from classes
                    # Pattern: condition ? 'style="..."' : 'class'
                    style_match = re.search(r"'style=\"([^\"]*?)\"'", content_part)
                    
                    if style_match:
                        style_content = style_match.group(1)
                        style_start = style_match.start()
                        style_end = style_match.end()
                        
                        # Extract before and after
                        before = content_part[:style_start]
                        after = content_part[style_end:]
                        
                        # Extract style property and value
                        style_parts = style_content.split(':', 1)
                        if len(style_parts) == 2:
                            prop = style_parts[0].strip()
                            value = style_parts[1].strip().rstrip(';')
                            
                            # Convert to camelCase
                            js_prop = ''.join(word if i == 0 else word.capitalize() 
                                            for i, word in enumerate(prop.split('-')))
                            
                            # Replace the style string with a proper class name
                            # Find what's before and after to determine the condition
                            if before.strip().endswith('?'):
                                # It's a ternary - use a temporary class name
                                new_class_name = 'status-active'
                                new_binding = f':class="{before}{new_class_name}{after}"'
                                # Also add :style binding
                                new_binding += f' :style="{{\'{js_prop}\': \'{value}\'}}"'
                                
                                current = current[:match.start()] + new_binding + current[match.end():]
                                count += 1
                                fixes.append(f"Separated Alpine style: {style_content}")
                        
            return current, count
        
        result, fix_count = fix_alpine_class(content)
        return result, fixes if fix_count > 0 else []
    
    def process_file(self, html_file: Path) -> dict:
        """Process a single HTML file"""
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content
            all_fixes = []
            
            # Fix 1: Regular class attributes with embedded styles
            content, fixes1 = self.fix_embedded_styles_in_class(content)
            all_fixes.extend(fixes1)
            
            # Fix 2: Alpine :class bindings with embedded styles
            content, fixes2 = self.fix_embedded_styles_in_alpine_class(content)
            all_fixes.extend(fixes2)
            
            # Write back if changes made
            if content != original:
                html_file.write_text(content, encoding='utf-8')
                return {
                    "file": str(html_file),
                    "fixed": True,
                    "fixes_applied": all_fixes,
                    "count": len(all_fixes)
                }
            else:
                return {
                    "file": str(html_file),
                    "fixed": False,
                    "fixes_applied": [],
                    "count": 0
                }
        
        except Exception as e:
            return {
                "file": str(html_file),
                "error": str(e)
            }
    
    def run(self):
        """Run the fixer on all template files"""
        if not self.template_dir.exists():
            print(f"Template directory not found: {self.template_dir}")
            return
        
        print("=" * 80)
        print("COMPREHENSIVE ALPINE.JS & CLASS ATTRIBUTE FIXER")
        print("=" * 80 + "\n")
        
        total_files = 0
        fixed_files = 0
        total_fixes = 0
        
        all_results = []
        
        # Process all HTML files
        for html_file in sorted(self.template_dir.rglob("*.html")):
            result = self.process_file(html_file)
            all_results.append(result)
            
            if "error" not in result:
                total_files += 1
                if result["fixed"]:
                    fixed_files += 1
                    total_fixes += result["count"]
                    print(f"✅ {html_file.relative_to(self.template_dir)}")
                    for fix in result["fixes_applied"][:3]:  # Show first 3 fixes
                        print(f"   - {fix}")
                    if result["count"] > 3:
                        print(f"   ... and {result['count'] - 3} more fixes")
        
        print("\n" + "=" * 80)
        print(f"SUMMARY: Fixed {fixed_files} files with {total_fixes} corrections")
        print("=" * 80)
        
        # Save detailed report
        with open("alpine_comprehensive_fix_report.json", "w") as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved: alpine_comprehensive_fix_report.json")

if __name__ == "__main__":
    fixer = AlpineStyleFixer()
    fixer.run()
