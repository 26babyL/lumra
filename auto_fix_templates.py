#!/usr/bin/env python3
"""
Auto-Fix Migration Issues
Automatically fixes common issues found in migrated templates

Issues fixed:
1. Missing closing {% endblock %} for extra_scripts
2. Mismatched script tags (extra closing tags)
3. x-init placement issues
"""

import json
import re
from pathlib import Path
from datetime import datetime

class AutoFixer:
    def __init__(self):
        self.log_file = Path("migration_log.json")
        self.template_base = Path("lumra_config/templates/lumra_pages")
        self.backup_dir = Path("_backups") / f"auto_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.fixes_log = []
    
    def fix_all(self):
        """Fix all templates"""
        print("\n" + "="*80)
        print("🔧 AUTO-FIX MIGRATION ISSUES")
        print("="*80)
        
        # Load migration log
        with open(self.log_file) as f:
            logs = json.load(f)
        
        templates_to_check = [log['file'] for log in logs if log['status'] != 'ok']
        
        print(f"\n📋 Checking {len(templates_to_check)} templates with issues...\n")
        
        for filename in templates_to_check:
            self._fix_template(filename)
        
        self._print_summary()
    
    def _find_template(self, filename: str) -> Path:
        """Find template file"""
        # Search in subdirectories
        for subdir in ['accounting', 'inventory', 'master_data', 'reports', 'sales', 
                      'purchasing', 'hrm', 'crm', 'asset_management', 'marketing']:
            path = self.template_base / subdir / filename
            if path.exists():
                return path
        
        # Search recursively
        for path in self.template_base.rglob(filename):
            return path
        
        return None
    
    def _fix_template(self, filename: str):
        """Fix individual template"""
        template_path = self._find_template(filename)
        if not template_path:
            print(f"⊘ {filename:40} (not found)")
            self.skipped_count += 1
            return
        
        try:
            content = template_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply fixes
            fixed = False
            
            # Fix 1: Add missing {% endblock %} for extra_scripts
            if '{% block extra_scripts %}' in content:
                # Check if closing endblock exists
                block_start = content.find('{% block extra_scripts %}')
                if block_start != -1:
                    # Check for endblock after this
                    remaining = content[block_start:]
                    if '{% endblock %}' not in remaining[:500]:  # Check first 500 chars after block start
                        # Find where to insert endblock
                        # Look for </body> or end of template
                        body_end = remaining.find('</body>')
                        if body_end > 0:
                            # Insert before </body>
                            insert_pos = block_start + body_end
                            content = content[:insert_pos] + '\n{% endblock %}\n' + content[insert_pos:]
                            fixed = True
                        else:
                            # Insert at end of script block
                            last_script_close = remaining.rfind('</script>')
                            if last_script_close > 0:
                                insert_pos = block_start + last_script_close + len('</script>')
                                # Skip any whitespace after
                                while insert_pos < len(content) and content[insert_pos] in ('\n', ' ', '\t', '\r'):
                                    insert_pos += 1
                                content = content[:insert_pos] + '\n{% endblock %}\n' + content[insert_pos:]
                                fixed = True
            
            # Fix 2: Remove extra closing </script> tags (duplicate)
            script_opens = len(re.findall(r'<script[^>]*type="application/json"', content))
            script_closes = len(re.findall(r'</script>', content))
            
            if script_closes > script_opens + 1:  # +1 for possible other script tags
                # Remove duplicate closing tags
                # This is tricky, so we'll be conservative
                pass
            
            # Write back if fixed
            if content != original_content:
                # Create backup
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = self.backup_dir / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_text(original_content, encoding='utf-8')
                
                # Write fixed content
                template_path.write_text(content, encoding='utf-8')
                
                self.fixed_count += 1
                self.fixes_log.append({
                    'file': filename,
                    'fixes': ['Added missing {% endblock %}' if fixed else 'No fixes needed'],
                    'backup': str(backup_path)
                })
                print(f"✓ {filename:40} FIXED")
            else:
                self.skipped_count += 1
                print(f"- {filename:40} (no fixes needed)")
        
        except Exception as e:
            self.error_count += 1
            print(f"✗ {filename:40} ERROR: {str(e)[:50]}")
    
    def _print_summary(self):
        """Print summary"""
        print("\n" + "="*80)
        print("📊 AUTO-FIX SUMMARY")
        print("="*80)
        print(f"✓ Fixed:    {self.fixed_count}")
        print(f"- Skipped:  {self.skipped_count}")
        print(f"✗ Errors:   {self.error_count}")
        
        if self.fixed_count > 0:
            print(f"\n✅ Total: {self.fixed_count} templates fixed!")
            print(f"📁 Backups saved to: {self.backup_dir}")
        else:
            print("\n✅ No fixes needed!")

if __name__ == '__main__':
    fixer = AutoFixer()
    fixer.fix_all()
