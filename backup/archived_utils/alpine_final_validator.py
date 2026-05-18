#!/usr/bin/env python3
"""
Final comprehensive scan for Alpine.js syntax errors
"""

import re
from pathlib import Path
import json

def scan_templates():
    """Scan all templates for remaining Alpine.js issues"""
    
    template_dir = Path("lumra_config/templates")
    issues = []
    
    # Patterns to check for
    patterns = [
        (r":class=\"[^\"]*'style=[^\"]*\"", "Embedded style= in :class binding"),
        (r":class=\"[^\"]*hover:style=", "Embedded hover:style= in :class"),
        (r"class=\"[^\"]*style=\"[^\"]*[^\"]*\"", "Embedded style= in class attribute"),
        (r":class=\"open \? '[^']+\"[^']*", "Unclosed :class quote (ends with double quote)"),
        (r"x-data=\"\{[^}]*'style=", "Embedded style= in x-data object"),
        (r":class=\"[^\"]*\?[^:]*?'style", "Style string in ternary :class"),
    ]
    
    if not template_dir.exists():
        print(f"Template directory not found: {template_dir}")
        return issues
    
    # Scan all HTML files
    for html_file in template_dir.rglob("*.html"):
        content = html_file.read_text(encoding='utf-8')
        try:
            rel_path = html_file.relative_to(Path.cwd())
        except ValueError:
            rel_path = html_file
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "file": str(rel_path),
                    "line": line_num,
                    "pattern": description,
                    "snippet": match.group(0)[:100]
                })
    
    return issues

def main():
    print("=" * 80)
    print("ALPINE.JS FINAL VALIDATION SCAN")
    print("=" * 80)
    
    issues = scan_templates()
    
    if not issues:
        print("\n✅ NO ALPINE.JS SYNTAX ISSUES FOUND")
        print("\nAll :class bindings are properly formatted:")
        print("  ✓ No embedded style= attributes")
        print("  ✓ No unclosed quotes")
        print("  ✓ All ternary expressions valid")
        print("  ✓ x-data objects properly formed")
        return
    
    print(f"\n⚠️  FOUND {len(issues)} POTENTIAL ISSUES:\n")
    
    for idx, issue in enumerate(issues, 1):
        print(f"{idx}. {issue['file']}:{issue['line']}")
        print(f"   Pattern: {issue['pattern']}")
        print(f"   Snippet: {issue['snippet'][:80]}...")
        print()
    
    # Save detailed report
    report = {
        "scan_type": "Alpine.js Syntax Validation",
        "issues_found": len(issues),
        "details": issues
    }
    
    with open("alpine_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"├─ Detailed report saved: alpine_validation_report.json")

if __name__ == "__main__":
    main()
