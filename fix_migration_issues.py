#!/usr/bin/env python3
"""
Fix Migration Issues Script
Mengidentifikasi dan memperbaiki templates yang masih belum sempurna

Jenis issues yang ditangani:
1. Templates dengan "skip" status (forms tanpa JSON) → ensure {% block extra_scripts %} ada
2. Templates dengan "warn" status → manual review
3. Verify script tag injection syntax
"""

import json
import re
from pathlib import Path
from typing import List, Tuple

class TemplateFixer:
    def __init__(self):
        self.log_file = Path("migration_log.json")
        self.template_base = Path("lumra_config/templates/lumra_pages")
        self.issues = []
        self.fixes = []
        
    def analyze_issues(self):
        """Analisis migration log dan identifikasi issues"""
        with open(self.log_file) as f:
            logs = json.load(f)
        
        for log in logs:
            if log['status'] != 'ok':
                self._check_template(log)
    
    def _check_template(self, log: dict):
        """Cek individual template untuk issues"""
        filename = log['file']
        
        # Find template file
        template_path = self._find_template(filename)
        if not template_path:
            self.issues.append({
                'file': filename,
                'severity': 'error',
                'issue': 'Template file not found',
                'fix': f'Cannot locate {filename}'
            })
            return
        
        # Read template content
        try:
            content = template_path.read_text(encoding='utf-8')
        except Exception as e:
            self.issues.append({
                'file': filename,
                'severity': 'error',
                'issue': f'Cannot read file: {e}',
                'fix': 'Check file permissions'
            })
            return
        
        # Check for issues
        issues = self._detect_issues(content, filename, log)
        self.issues.extend(issues)
    
    def _find_template(self, filename: str) -> Path:
        """Find template file by searching common locations"""
        search_paths = [
            self.template_base / "accounting" / filename,
            self.template_base / "inventory" / filename,
            self.template_base / "master_data" / filename,
            self.template_base / "reports" / filename,
            self.template_base / "sales" / filename,
            self.template_base / "purchasing" / filename,
            self.template_base / "hrm" / filename,
            self.template_base / "crm" / filename,
            self.template_base / "asset_management" / filename,
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        # Fallback: search recursively
        for path in self.template_base.rglob(filename):
            return path
        
        return None
    
    def _detect_issues(self, content: str, filename: str, log: dict) -> List[dict]:
        """Detect specific issues dalam template"""
        issues = []
        
        # Issue 1: Has {% block extra_scripts %} ?
        if not re.search(r'\{%[-\s]*block extra_scripts', content):
            issues.append({
                'file': filename,
                'severity': 'warn',
                'issue': 'Missing {% block extra_scripts %}',
                'fix': 'Add {% block extra_scripts %}...{% endblock %} before </body>',
                'log_status': log['status']
            })
        
        # Issue 2: Script tags not properly closed?
        script_tags = re.findall(r'<script[^>]*type="application/json"[^>]*>', content)
        script_closes = len(re.findall(r'</script>', content))
        if script_tags and len(script_tags) != script_closes:
            issues.append({
                'file': filename,
                'severity': 'error',
                'issue': f'Mismatched script tags: {len(script_tags)} open, {script_closes} close',
                'fix': 'Verify all script tags are properly closed'
            })
        
        # Issue 3: x-data without x-init on main Alpine element
        if 'x-data=' in content and 'x-init=' not in content:
            # Check if x-init is on same element
            xdata_lines = re.findall(r'x-data="[^"]*"[^>]*', content)
            for xdata_line in xdata_lines:
                if 'x-init=' not in xdata_line:
                    issues.append({
                        'file': filename,
                        'severity': 'warn',
                        'issue': 'x-data without x-init on same element',
                        'fix': 'Add x-init="init()" to the element with x-data',
                        'context': xdata_line[:80]
                    })
                    break
        
        # Issue 4: Missing closing {% endblock %} for extra_scripts
        if '{% block extra_scripts %}' in content:
            if not re.search(r'\{%[-\s]*endblock', content.split('{% block extra_scripts %}')[-1][:200]):
                issues.append({
                    'file': filename,
                    'severity': 'error',
                    'issue': 'Missing closing {% endblock %} for extra_scripts',
                    'fix': 'Add {% endblock %} after </script> block'
                })
        
        # Issue 5: Alpine function not defined but x-data references it
        alpine_funcs = re.findall(r'function\s+(\w+)\s*\(', content)
        xdata_funcs = re.findall(r'x-data="(\w+)\(\)"', content)
        for xdata_func in xdata_funcs:
            if xdata_func not in alpine_funcs:
                issues.append({
                    'file': filename,
                    'severity': 'error',
                    'issue': f'x-data references undefined function: {xdata_func}()',
                    'fix': f'Define function {xdata_func}() or fix x-data reference'
                })
        
        return issues
    
    def generate_report(self):
        """Generate issue report"""
        print("\n" + "="*80)
        print("🔧 TEMPLATE FIX REPORT")
        print("="*80)
        
        if not self.issues:
            print("\n✅ No issues detected! All templates look good.")
            return
        
        # Group by severity
        errors = [i for i in self.issues if i['severity'] == 'error']
        warnings = [i for i in self.issues if i['severity'] == 'warn']
        
        if errors:
            print(f"\n❌ ERRORS ({len(errors)} found):")
            print("-"*80)
            for issue in errors:
                print(f"\n📄 {issue['file']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Fix:   {issue['fix']}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)} found):")
            print("-"*80)
            for issue in warnings[:10]:  # Show first 10
                print(f"\n📄 {issue['file']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Fix:   {issue['fix']}")
                if 'context' in issue:
                    print(f"   Context: {issue['context']}")
            
            if len(warnings) > 10:
                print(f"\n   ... and {len(warnings)-10} more warnings")
        
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"Errors:   {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print(f"Total:    {len(self.issues)}")

# Run analysis
if __name__ == '__main__':
    fixer = TemplateFixer()
    fixer.analyze_issues()
    fixer.generate_report()
