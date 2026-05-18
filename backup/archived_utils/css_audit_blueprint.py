#!/usr/bin/env python3
"""
CSS Audit Tool — Check 11 CSS files against LUMRA_ERP_EMERALD_ODYSSEY.md blueprint
Generates audit report dengan rekomendasi fix
"""

import re
from pathlib import Path
from datetime import datetime

class CSSAudit:
    def __init__(self):
        self.css_dir = Path("lumra_config/static/css")
        self.blueprint = {
            "colors": {
                "--color-primary": "#00674F",
                "--color-secondary": "#00A86B", 
                "--color-accent": "#EFBF04",
                "--color-neutral": "#FDFBD4",
                "--color-contrast": "#000080",
            },
            "glass_protocol": [
                "backdrop-filter: blur(12px)",
                "border: 0.5px solid rgba(255,255,255,0.10)",
                "background: rgba(0,103,79,.08)",
            ],
            "typography": {
                "h1": "28px 600",
                "h2": "22px 600",
                "h3": "16px 500",
                "body": "14px 400",
            },
            "spacing": [8, 16, 24, 32, 40, 48, 56, 64, 240],  # All 8px multiples
        }
        self.issues = {}
        self.files_status = {}

    def audit_file(self, filename):
        filepath = self.css_dir / filename
        if not filepath.exists():
            return {"status": "MISSING", "errors": [f"File not found: {filepath}"]}
        
        content = filepath.read_text(encoding='utf-8')
        errors = []
        warnings = []
        
        # Check 1: Primary colors exist
        if "--color-primary" not in content or "#00674F" not in content:
            errors.append("Missing primary color --color-primary: #00674F")
        
        if "--color-secondary" not in content or "#00A86B" not in content:
            errors.append("Missing secondary color --color-secondary: #00A86B")
            
        if "--color-accent" not in content or "#EFBF04" not in content:
            errors.append("Missing accent color --color-accent: #EFBF04")
        
        # Check 2: Glass Protocol (if not tokens file)
        if filename not in ["lumra_tokens.css", "lumra_base.css"]:
            glass_items = sum(1 for item in self.blueprint["glass_protocol"] 
                            if item in content)
            if glass_items < 3:
                warnings.append(f"Glass Protocol incomplete ({glass_items}/3 items)")
        
        # Check 3: No old Tailwind colors (except design_system which is generated)
        old_tailwind = ["#047857", "#059669", "#94a3b8", "emerald-600", "emerald-700"]
        found_old = [color for color in old_tailwind if color in content]
        if found_old and filename not in ["lumra_design_system.css"]:
            warnings.append(f"Contains old Tailwind colors: {found_old}")
        
        # Check 4: Line count sanity check
        lines = len(content.split('\n'))
        if lines < 20:
            errors.append(f"File too small ({lines} lines) - might be incomplete")
        
        # Check 5: CSS syntax validity (basic)
        brace_open = content.count('{')
        brace_close = content.count('}')
        if brace_open != brace_close:
            errors.append(f"CSS syntax error: {brace_open} open braces vs {brace_close} close")
        
        status = "ERROR" if errors else ("WARNING" if warnings else "OK")
        return {
            "status": status,
            "size": len(content),
            "lines": lines,
            "errors": errors,
            "warnings": warnings,
        }

    def run_audit(self):
        print("=" * 80)
        print("CSS AUDIT REPORT — Emerald Odyssey v3.0")
        print("=" * 80)
        print(f"\nAudit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Blueprint: LUMRA_ERP_EMERALD_ODYSSEY.md")
        print(f"CSS Directory: {self.css_dir.absolute()}\n")
        
        css_files = [
            "lumra_tokens.css",
            "lumra_base.css",
            "lumra_components.css",
            "lumra_sidebar.css",
            "lumra_navbar.css",
            "lumra_dashboard.css",
            "lumra_design_system.css",
            "lumra_form.css",
            "lumra_typography.css",
            "lumra_bg_blob.css",
            "theme_overrides.css",
        ]
        
        total_files = len(css_files)
        ok_count = 0
        warning_count = 0
        error_count = 0
        
        for filename in css_files:
            result = self.audit_file(filename)
            self.files_status[filename] = result
            
            status = result["status"]
            if status == "OK":
                ok_count += 1
                symbol = "✅"
            elif status == "WARNING":
                warning_count += 1
                symbol = "⚠️"
            else:
                error_count += 1
                symbol = "❌"
            
            size_kb = result.get("size", 0) / 1024
            print(f"{symbol} {filename:<35} ({size_kb:>6.1f} KB, {result['lines']:>4} lines) [{status}]")
            
            # Show issues
            if result["errors"]:
                for error in result["errors"]:
                    print(f"    ERROR: {error}")
            
            if result["warnings"]:
                for warning in result["warnings"]:
                    print(f"    WARNING: {warning}")
        
        print("\n" + "=" * 80)
        print(f"SUMMARY: {ok_count} OK, {warning_count} WARNINGS, {error_count} ERRORS")
        print("=" * 80)
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:\n")
        if error_count > 0:
            print("🔴 CRITICAL ISSUES TO FIX:")
            for filename, result in self.files_status.items():
                if result["status"] == "ERROR":
                    print(f"   • {filename}")
        
        print("\n📌 ACTION ITEMS:")
        print("   1. Verify all 11 CSS files are present and not empty")
        print("   2. Ensure all Odyssey primary colors are defined correctly")
        print("   3. Check Glass Protocol is implemented in component files")
        print("   4. Verify typography matches blueprint specifications")
        print("   5. Remove old Tailwind-specific colors (except design_system.css)")
        print("   6. Run: python manage.py tailwind build")
        print("   7. Reload browser and verify styling\n")

if __name__ == "__main__":
    audit = CSSAudit()
    audit.run_audit()
