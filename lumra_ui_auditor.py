"""
LUMRA UI/UX Template Auditor
============================
Jalankan dari root project lumra:
    python lumra_ui_auditor.py

Atau dengan path custom:
    python lumra_ui_auditor.py --path D:/APPS/Project/lumra/lumra_config/templates
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from datetime import datetime


# ─────────────────────────────────────────────
# KONFIGURASI AUDIT
# ─────────────────────────────────────────────

# Pola yang kita anggap sebagai "standar" Lumra
STANDARD_BTN_PRIMARY    = re.compile(r'btn[-\s]*(primary|emerald|green)', re.I)
STANDARD_BTN_SECONDARY  = re.compile(r'btn[-\s]*(secondary|gray|outline)', re.I)
STANDARD_TABLE          = re.compile(r'<table[^>]*class="[^"]*', re.I)
STANDARD_CARD           = re.compile(r'class="[^"]*\bcard\b[^"]*"', re.I)
STANDARD_EXTENDS        = re.compile(r'\{%\s*extends\s+["\'](.+?)["\']\s*%\}')
STANDARD_BLOCK_CONTENT  = re.compile(r'\{%\s*block\s+(\w+)\s*%\}')
STANDARD_CSRF           = re.compile(r'\{%\s*csrf_token\s*%\}')

# Pola inkonsistensi yang dicari
CHECKS = {
    "missing_page_title": {
        "desc": "Tidak ada {% block title %} atau <title>",
        "pattern": re.compile(r'\{%\s*block\s+title\s*%\}|<title>', re.I),
        "expect_found": True,
    },
    "missing_csrf": {
        "desc": "Ada <form> tapi tidak ada {% csrf_token %}",
        "pattern": None,  # logic khusus
        "expect_found": True,
    },
    "inline_style": {
        "desc": "Ada style=\"...\" inline (sebaiknya pakai class)",
        "pattern": re.compile(r'\bstyle\s*=\s*["\'][^"\']{15,}["\']'),
        "expect_found": False,
    },
    "hardcoded_color": {
        "desc": "Warna hardcoded (#hex / rgb) di dalam style/class",
        "pattern": re.compile(r'(?:color|background)[^;"\n]{0,10}(?:#[0-9a-fA-F]{3,6}|rgb\()'),
        "expect_found": False,
    },
    "mixed_btn_style": {
        "desc": "Memakai lebih dari satu varian gaya tombol (btn-primary, btn-emerald, dll)",
        "pattern": None,  # logic khusus
        "expect_found": False,
    },
    "no_empty_state": {
        "desc": "Tidak ada handling empty state ({% empty %} atau 'tidak ada data')",
        "pattern": re.compile(r'\{%\s*empty\s*%\}|tidak ada data|no data|belum ada|kosong', re.I),
        "expect_found": True,  # hanya flag jika ada {% for %} tapi tidak ada empty
    },
    "inconsistent_table_class": {
        "desc": "Tabel tanpa class standar (table, table-striped, dll)",
        "pattern": re.compile(r'<table(?!\s[^>]*class)[^>]*>'),
        "expect_found": False,
    },
    "missing_loading_state": {
        "desc": "Ada form submit / AJAX tapi tidak ada indikator loading",
        "pattern": re.compile(r'(fetch\(|\.ajax\(|axios\.|submit\(\))', re.I),
        "expect_found": False,  # tidak wajib, tapi dicatat
    },
    "raw_alert_js": {
        "desc": "Memakai alert() bawaan browser (sebaiknya pakai toast/modal)",
        "pattern": re.compile(r'\balert\s*\('),
        "expect_found": False,
    },
    "console_log": {
        "desc": "Ada console.log() yang tertinggal",
        "pattern": re.compile(r'\bconsole\.log\s*\('),
        "expect_found": False,
    },
    "deprecated_jquery": {
        "desc": "Memakai jQuery versi lama (.live(), .die(), .size())",
        "pattern": re.compile(r'\.(live|die|size)\s*\('),
        "expect_found": False,
    },
    "broken_url_tag": {
        "desc": "Kemungkinan URL tag rusak (url tanpa nama atau kwarg)",
        "pattern": re.compile(r"\{%\s*url\s+['\"]['\"]"),
        "expect_found": False,
    },
    "missing_block_content": {
        "desc": "File extends tapi tidak punya block content/main",
        "pattern": None,  # logic khusus
        "expect_found": True,
    },
}

# Kategori halaman berdasarkan path
SECTION_MAP = {
    "accounting": "💰 Accounting",
    "auth": "🔐 Auth",
    "etc": "⚠️ Error Pages",
    "inventory": "📦 Inventory",
    "marketing": "📣 Marketing",
    "master_data": "🗂️ Master Data",
    "messages": "💬 Messages",
    "onboarding": "🚀 Onboarding",
    "print": "🖨️ Print",
    "production": "🏭 Production",
    "reports": "📊 Reports",
    "sales": "🛒 Sales",
    "sales_insight": "📈 Sales Insight",
    "settings": "⚙️ Settings",
}


# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class FileIssue:
    check_key: str
    severity: str  # "error" | "warning" | "info"
    desc: str
    lines: List[int] = field(default_factory=list)
    detail: str = ""


@dataclass
class FileReport:
    path: Path
    section: str
    issues: List[FileIssue] = field(default_factory=list)
    meta: Dict = field(default_factory=dict)

    @property
    def score(self):
        weights = {"error": 10, "warning": 5, "info": 1}
        return sum(weights.get(i.severity, 0) for i in self.issues)

    @property
    def status(self):
        if self.score == 0:
            return "✅ CLEAN"
        elif self.score <= 10:
            return "⚠️  MINOR"
        elif self.score <= 25:
            return "🔶 MODERATE"
        else:
            return "🔴 NEEDS WORK"


# ─────────────────────────────────────────────
# CORE AUDITOR
# ─────────────────────────────────────────────

class LumraAuditor:
    def __init__(self, template_root: Path):
        self.root = template_root
        self.reports: List[FileReport] = []
        self.global_stats = defaultdict(int)
        self.extends_map: Dict[str, str] = {}      # file -> base template
        self.btn_variants: Dict[str, Set[str]] = {} # file -> set of btn classes

    def get_section(self, path: Path) -> str:
        parts = path.parts
        for part in parts:
            if part in SECTION_MAP:
                return SECTION_MAP[part]
        return "🔧 Other"

    def find_templates(self) -> List[Path]:
        templates = []
        for html in self.root.rglob("*.html"):
            # Skip file di dalam folder backup
            if any(p.startswith('.') or p in ('backup', '__pycache__') 
                   for p in html.parts):
                continue
            templates.append(html)
        return sorted(templates)

    def audit_file(self, path: Path) -> FileReport:
        report = FileReport(path=path, section=self.get_section(path))

        try:
            content = path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            report.issues.append(FileIssue(
                check_key="read_error", severity="error",
                desc=f"Tidak bisa dibaca: {e}"
            ))
            return report

        lines = content.splitlines()
        report.meta['lines'] = len(lines)
        report.meta['size_kb'] = round(path.stat().st_size / 1024, 1)

        # Cek extends
        extends_match = STANDARD_EXTENDS.search(content)
        report.meta['extends'] = extends_match.group(1) if extends_match else None

        # Cek blocks
        blocks = STANDARD_BLOCK_CONTENT.findall(content)
        report.meta['blocks'] = blocks

        # ── 1. missing_page_title ──────────────────────
        if not CHECKS["missing_page_title"]["pattern"].search(content):
            report.issues.append(FileIssue(
                "missing_page_title", "warning",
                CHECKS["missing_page_title"]["desc"]
            ))

        # ── 2. missing_csrf ────────────────────────────
        has_form = bool(re.search(r'<form\b', content, re.I))
        has_csrf = bool(STANDARD_CSRF.search(content))
        if has_form and not has_csrf:
            form_lines = [i+1 for i, l in enumerate(lines) if re.search(r'<form\b', l, re.I)]
            report.issues.append(FileIssue(
                "missing_csrf", "error",
                CHECKS["missing_csrf"]["desc"],
                lines=form_lines[:3]
            ))

        # ── 3. inline_style ────────────────────────────
        inline_hits = []
        for i, line in enumerate(lines):
            if re.search(r'\bstyle\s*=\s*["\'][^"\']{15,}["\']', line):
                inline_hits.append(i+1)
        if inline_hits:
            report.issues.append(FileIssue(
                "inline_style", "info",
                CHECKS["inline_style"]["desc"],
                lines=inline_hits[:5],
                detail=f"Total: {len(inline_hits)} baris"
            ))

        # ── 4. hardcoded_color ─────────────────────────
        color_hits = []
        for i, line in enumerate(lines):
            if CHECKS["hardcoded_color"]["pattern"].search(line):
                color_hits.append(i+1)
        if color_hits:
            report.issues.append(FileIssue(
                "hardcoded_color", "info",
                CHECKS["hardcoded_color"]["desc"],
                lines=color_hits[:5]
            ))

        # ── 5. mixed_btn_style ─────────────────────────
        btn_classes = set(re.findall(
            r'class="[^"]*\b(btn-(?:primary|secondary|success|danger|warning|'
            r'info|dark|light|emerald|green|red|blue|gray|outline-\w+))\b[^"]*"',
            content, re.I
        ))
        if len(btn_classes) > 2:
            report.issues.append(FileIssue(
                "mixed_btn_style", "warning",
                CHECKS["mixed_btn_style"]["desc"],
                detail=f"Ditemukan: {', '.join(sorted(btn_classes))}"
            ))
        report.meta['btn_classes'] = btn_classes

        # ── 6. no_empty_state ──────────────────────────
        has_for_loop = bool(re.search(r'\{%\s*for\s+', content))
        has_empty = bool(re.search(r'\{%\s*empty\s*%\}|tidak ada data|no data|belum ada|Tidak ada', content, re.I))
        if has_for_loop and not has_empty:
            report.issues.append(FileIssue(
                "no_empty_state", "info",
                "Ada {% for %} tapi tidak ada empty state / pesan 'data kosong'"
            ))

        # ── 7. inconsistent_table_class ───────────────
        bare_table = re.findall(r'<table(?!\s[^>]*class)[^>]*>', content, re.I)
        if bare_table:
            report.issues.append(FileIssue(
                "inconsistent_table_class", "warning",
                CHECKS["inconsistent_table_class"]["desc"],
                detail=f"{len(bare_table)} tabel tanpa class"
            ))

        # ── 8. raw_alert_js ───────────────────────────
        alert_hits = [i+1 for i, l in enumerate(lines) if re.search(r'\balert\s*\(', l)]
        if alert_hits:
            report.issues.append(FileIssue(
                "raw_alert_js", "warning",
                CHECKS["raw_alert_js"]["desc"],
                lines=alert_hits[:3]
            ))

        # ── 9. console_log ────────────────────────────
        console_hits = [i+1 for i, l in enumerate(lines) if re.search(r'\bconsole\.log\s*\(', l)]
        if console_hits:
            report.issues.append(FileIssue(
                "console_log", "info",
                CHECKS["console_log"]["desc"],
                lines=console_hits[:3],
                detail=f"Total: {len(console_hits)}"
            ))

        # ── 10. missing_block_content ─────────────────
        if report.meta['extends'] and 'content' not in blocks and 'main' not in blocks:
            report.issues.append(FileIssue(
                "missing_block_content", "warning",
                f"Extends '{report.meta['extends']}' tapi tidak ada block content/main. "
                f"Blocks ada: {blocks or ['(none)']}"
            ))

        # ── 11. deprecated_jquery ─────────────────────
        jq_hits = [i+1 for i, l in enumerate(lines) 
                   if re.search(r'\.(live|die|size)\s*\(', l)]
        if jq_hits:
            report.issues.append(FileIssue(
                "deprecated_jquery", "warning",
                CHECKS["deprecated_jquery"]["desc"],
                lines=jq_hits
            ))

        return report

    def run(self):
        templates = self.find_templates()
        print(f"\n🔍 Scanning {len(templates)} template files...\n")

        for path in templates:
            report = self.audit_file(path)
            self.reports.append(report)

            for issue in report.issues:
                self.global_stats[issue.check_key] += 1
                self.global_stats[f"sev_{issue.severity}"] += 1

        return self

    def generate_report(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = []
        a = lines.append

        # ── HEADER ────────────────────────────────────
        a("=" * 70)
        a("  LUMRA UI/UX TEMPLATE AUDIT REPORT")
        a(f"  Generated: {now}")
        a(f"  Template Root: {self.root}")
        a("=" * 70)

        # ── RINGKASAN GLOBAL ──────────────────────────
        total = len(self.reports)
        clean = sum(1 for r in self.reports if r.score == 0)
        errors = self.global_stats.get("sev_error", 0)
        warnings = self.global_stats.get("sev_warning", 0)
        infos = self.global_stats.get("sev_info", 0)

        a(f"\n📊 RINGKASAN")
        a(f"   Total file    : {total}")
        a(f"   ✅ Clean       : {clean} ({clean*100//total}%)")
        a(f"   🔴 Errors      : {errors}")
        a(f"   ⚠️  Warnings    : {warnings}")
        a(f"   ℹ️  Info        : {infos}")

        # ── TOP ISSUES ────────────────────────────────
        a(f"\n📌 MASALAH TERBANYAK")
        sorted_checks = sorted(
            [(k, v) for k, v in self.global_stats.items() if not k.startswith("sev_")],
            key=lambda x: x[1], reverse=True
        )
        for check_key, count in sorted_checks[:10]:
            desc = CHECKS.get(check_key, {}).get("desc", check_key)
            bar = "█" * min(count, 40)
            a(f"   {count:3d}x  {bar}  {desc}")

        # ── PALING BUTUH PERHATIAN ────────────────────
        a(f"\n🔴 TOP 15 FILE BUTUH PERBAIKAN")
        worst = sorted(self.reports, key=lambda r: r.score, reverse=True)[:15]
        for r in worst:
            rel = r.path.relative_to(self.root) if self.root in r.path.parents else r.path
            a(f"   [{r.score:3d} pts] {r.status}  {rel}")
            for issue in r.issues[:3]:
                sev_icon = {"error": "🔴", "warning": "⚠️ ", "info": "ℹ️ "}.get(issue.severity, "  ")
                a(f"            {sev_icon} {issue.desc}")
                if issue.lines:
                    a(f"               → baris: {issue.lines}")
                if issue.detail:
                    a(f"               → {issue.detail}")

        # ── DETAIL PER SECTION ────────────────────────
        a(f"\n{'─'*70}")
        a(f"  DETAIL PER SECTION")
        a(f"{'─'*70}")

        by_section = defaultdict(list)
        for r in self.reports:
            by_section[r.section].append(r)

        for section in sorted(by_section.keys()):
            reports = by_section[section]
            section_score = sum(r.score for r in reports)
            a(f"\n{section}  ({len(reports)} file, total score: {section_score})")
            a("  " + "─" * 50)

            for r in sorted(reports, key=lambda x: x.score, reverse=True):
                rel = r.path.name
                if r.score == 0:
                    a(f"  ✅  {rel}")
                else:
                    a(f"  {r.status}  {rel}  [{r.score} pts]")
                    for issue in r.issues:
                        sev_icon = {"error": "🔴", "warning": "⚠️ ", "info": "ℹ️ "}.get(issue.severity, "  ")
                        line_info = f" (baris: {issue.lines[:3]})" if issue.lines else ""
                        detail_info = f" — {issue.detail}" if issue.detail else ""
                        a(f"      {sev_icon} {issue.desc}{line_info}{detail_info}")

        # ── BTN CONSISTENCY MAP ───────────────────────
        a(f"\n{'─'*70}")
        a(f"  BUTTON CLASS CONSISTENCY MAP")
        a(f"{'─'*70}")
        all_btn = defaultdict(int)
        for r in self.reports:
            for cls in r.meta.get('btn_classes', set()):
                all_btn[cls.lower()] += 1

        if all_btn:
            a(f"\n  Varian tombol yang dipakai di seluruh project:")
            for cls, count in sorted(all_btn.items(), key=lambda x: x[1], reverse=True):
                a(f"  {count:3d}x  .{cls}")
            
            dominant = max(all_btn, key=all_btn.get)
            a(f"\n  ✨ Rekomendasi standar: '.{dominant}' (paling banyak dipakai)")
        else:
            a("\n  Tidak ada class tombol terdeteksi.")

        # ── CLEAN FILES ───────────────────────────────
        clean_files = [r for r in self.reports if r.score == 0]
        if clean_files:
            a(f"\n{'─'*70}")
            a(f"  ✅ FILE YANG SUDAH BERSIH ({len(clean_files)} file)")
            a(f"{'─'*70}")
            for r in clean_files:
                rel = r.path.relative_to(self.root) if self.root in r.path.parents else r.path.name
                a(f"  ✅  {rel}")

        # ── FOOTER ────────────────────────────────────
        a(f"\n{'='*70}")
        a(f"  END OF REPORT  |  Total issues: {errors + warnings + infos}")
        a(f"{'='*70}\n")

        return "\n".join(lines)

    def save_json(self, output_path: Path):
        """Simpan hasil audit dalam format JSON untuk diproses lebih lanjut."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "template_root": str(self.root),
            "summary": {
                "total_files": len(self.reports),
                "clean_files": sum(1 for r in self.reports if r.score == 0),
                "total_errors": self.global_stats.get("sev_error", 0),
                "total_warnings": self.global_stats.get("sev_warning", 0),
                "total_info": self.global_stats.get("sev_info", 0),
            },
            "files": [
                {
                    "path": str(r.path),
                    "section": r.section,
                    "score": r.score,
                    "status": r.status,
                    "meta": {
                        "lines": r.meta.get("lines"),
                        "extends": r.meta.get("extends"),
                        "blocks": r.meta.get("blocks", []),
                        "btn_classes": list(r.meta.get("btn_classes", set())),
                    },
                    "issues": [
                        {
                            "check": i.check_key,
                            "severity": i.severity,
                            "desc": i.desc,
                            "lines": i.lines,
                            "detail": i.detail,
                        }
                        for i in r.issues
                    ]
                }
                for r in sorted(self.reports, key=lambda x: x.score, reverse=True)
            ]
        }
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Lumra UI/UX Template Auditor")
    parser.add_argument(
        "--path", 
        default=None,
        help="Path ke folder templates (default: auto-detect dari cwd)"
    )
    parser.add_argument(
        "--output",
        default="lumra_ui_audit_report.txt",
        help="Nama file output teks (default: lumra_ui_audit_report.txt)"
    )
    parser.add_argument(
        "--json",
        default="lumra_ui_audit_report.json",
        help="Nama file output JSON (default: lumra_ui_audit_report.json)"
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Jangan buat file JSON"
    )
    args = parser.parse_args()

    # Auto-detect path
    if args.path:
        template_root = Path(args.path)
    else:
        # Coba beberapa kemungkinan
        candidates = [
            Path.cwd() / "lumra_config" / "templates" / "lumra_pages",
            Path.cwd() / "templates" / "lumra_pages",
            Path("D:/APPS/Project/lumra/lumra_config/templates/lumra_pages"),
        ]
        template_root = None
        for c in candidates:
            if c.exists():
                template_root = c
                break
        
        if not template_root:
            print("❌ Tidak bisa menemukan folder templates.")
            print("   Jalankan dengan: python lumra_ui_auditor.py --path <path_ke_templates>")
            print(f"   Contoh: python lumra_ui_auditor.py --path D:/APPS/Project/lumra/lumra_config/templates/lumra_pages")
            return

    if not template_root.exists():
        print(f"❌ Path tidak ditemukan: {template_root}")
        return

    print(f"📁 Template root: {template_root}")

    # Jalankan audit
    auditor = LumraAuditor(template_root)
    auditor.run()

    # Generate report teks
    report_text = auditor.generate_report()
    print(report_text)

    # Simpan ke file
    output_path = Path(args.output)
    output_path.write_text(report_text, encoding='utf-8')
    print(f"📄 Laporan teks disimpan ke: {output_path.absolute()}")

    # Simpan JSON
    if not args.no_json:
        json_path = Path(args.json)
        auditor.save_json(json_path)
        print(f"📊 Laporan JSON disimpan ke: {json_path.absolute()}")


if __name__ == "__main__":
    main()