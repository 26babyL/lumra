#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         LUMRA - JSON Injection Migration Tool                               ║
║         Server-side rendering → Alpine.js JSON injection pattern            ║
╚══════════════════════════════════════════════════════════════════════════════╝

USAGE:
  python lumra_migrate.py scan    [--dir PATH]           # Scan semua template
  python lumra_migrate.py analyze [--file PATH]          # Analisis 1 file
  python lumra_migrate.py migrate [--file PATH] [--dry]  # Migrate 1 file
  python lumra_migrate.py batch   [--dir PATH] [--dry]   # Migrate semua sekaligus
  python lumra_migrate.py validate [--file PATH]         # Validasi hasil
  python lumra_migrate.py report  [--dir PATH]           # Buat laporan lengkap

OPTIONS:
  --dir PATH    Folder template (default: lumra_config/templates/lumra_pages)
  --file PATH   File template spesifik
  --dry         Dry-run, tidak tulis file (preview saja)
  --backup      Buat backup .bak sebelum migrate (default: True)
  --no-backup   Skip backup
  --verbose     Output detail
"""

import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from textwrap import indent, dedent
from typing import Optional

# ─────────────────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────────────────

DEFAULT_TEMPLATE_DIR = "lumra_config/templates/lumra_pages"
BACKUP_SUFFIX = ".bak"

# Warna terminal
class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

def c(color, text): return f"{color}{text}{C.RESET}"
def ok(t):   return c(C.GREEN,  f"✓ {t}")
def err(t):  return c(C.RED,    f"✗ {t}")
def warn(t): return c(C.YELLOW, f"⚠ {t}")
def info(t): return c(C.CYAN,   f"→ {t}")
def bold(t): return c(C.BOLD, t)
def dim(t):  return c(C.DIM, t)

# ─────────────────────────────────────────────────────────
# DETECTOR - Analisis isi template
# ─────────────────────────────────────────────────────────

class TemplateAnalysis:
    def __init__(self, path: Path):
        self.path = path
        self.content = path.read_text(encoding="utf-8")
        self._run()

    def _run(self):
        c = self.content

        # Cari semua inline JSON vars: {{ varname|safe }}
        # Hanya yang di dalam JS context (dalam tag <script>)
        self.inline_json_vars = []
        script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
        for block in script_blocks:
            found = re.findall(r'\{\{\s*(\w+_json)\s*\|safe\s*\}\}', block)
            self.inline_json_vars.extend(found)
        self.inline_json_vars = list(dict.fromkeys(self.inline_json_vars))  # dedupe

        # Cari semua vars yang ada di template (termasuk non-json)
        self.all_safe_vars = list(dict.fromkeys(
            re.findall(r'\{\{\s*(\w+)\s*\|safe\s*\}\}', c)
        ))

        # Block type
        self.has_extra_scripts = bool(re.search(r'\{%[-\s]*block extra_scripts', c))
        self.has_old_scripts   = bool(re.search(r'\{%[-\s]*block scripts?\s*[-\%]\}', c, re.I))

        # Alpine
        self.has_x_data  = 'x-data=' in c
        self.has_x_init  = 'x-init=' in c
        self.has_x_cloak = 'x-cloak' in c

        # Existing script tags untuk JSON
        self.existing_json_script_tags = re.findall(
            r'<script\s+id="([\w-]+)"\s+type="application/json"', c
        )

        # Alpine function names
        self.alpine_functions = re.findall(r'function\s+(\w+App|\w+app)\s*\(', c)
        xdata_fns = re.findall(r'x-data="(\w+)\(\)"', c)
        self.alpine_functions = list(dict.fromkeys(self.alpine_functions + xdata_fns))

        # Deteksi pattern
        self.detected_pattern = self._detect_pattern()

        # Issues
        self.issues = self._collect_issues()

        # Score
        self.score = self._compute_score()

    def _detect_pattern(self):
        c = self.content
        var_count = len(self.inline_json_vars)
        if var_count >= 2:
            return "dual_json"
        if re.search(r'journal|voucher|form.*post|method.*post', c, re.I) and 'select' in c:
            return "form_dropdown"
        if re.search(r'aging|overdue|bucket|days.*due|due.*days', c, re.I):
            return "aging_table"
        if re.search(r'balance.*sheet|profit.*loss|cash.*flow|neraca|laba.*rugi', c, re.I):
            return "complex_report"
        return "simple_list"

    def _collect_issues(self):
        issues = []
        if self.inline_json_vars:
            for v in self.inline_json_vars:
                issues.append({
                    "severity": "error",
                    "code": "INLINE_JSON",
                    "msg": f"Inline JSON: {{{{ {v}|safe }}}} ada di dalam script tag",
                    "var": v,
                    "fix": "Pindahkan ke <script id='...' type='application/json'>"
                })
        if self.has_old_scripts:
            issues.append({
                "severity": "error",
                "code": "WRONG_BLOCK",
                "msg": "Menggunakan {% block scripts %} — harus diganti {% block extra_scripts %}",
                "fix": "Ganti nama block"
            })
        if not self.has_extra_scripts and not self.has_old_scripts:
            issues.append({
                "severity": "warning",
                "code": "NO_BLOCK",
                "msg": "Tidak ada block scripts sama sekali",
                "fix": "Tambahkan {% block extra_scripts %}...{% endblock %}"
            })
        if self.has_x_data and not self.has_x_init:
            issues.append({
                "severity": "warning",
                "code": "NO_X_INIT",
                "msg": "x-data ada tapi x-init='init()' tidak ditemukan",
                "fix": "Tambahkan x-init='init()' pada div x-data"
            })
        if self.inline_json_vars and not self.existing_json_script_tags:
            issues.append({
                "severity": "error",
                "code": "NO_SCRIPT_TAG",
                "msg": "Belum ada <script type='application/json'> untuk inject data",
                "fix": "Buat script tag JSON sebelum Alpine function"
            })
        return issues

    def _compute_score(self):
        score = 100
        for issue in self.issues:
            score -= 30 if issue["severity"] == "error" else 10
        return max(0, score)

    @property
    def needs_migration(self):
        return any(i["severity"] == "error" for i in self.issues)

    @property
    def pattern_label(self):
        labels = {
            "simple_list":     "Simple List",
            "dual_json":       "Dual JSON",
            "form_dropdown":   "Form + Dropdown",
            "aging_table":     "Aging Table",
            "complex_report":  "Complex Report",
        }
        return labels.get(self.detected_pattern, self.detected_pattern)


# ─────────────────────────────────────────────────────────
# MIGRATOR - Transform template content
# ─────────────────────────────────────────────────────────

class TemplateMigrator:
    def __init__(self, analysis: TemplateAnalysis, verbose=False):
        self.a = analysis
        self.verbose = verbose
        self.changes = []

    def migrate(self) -> str:
        content = self.a.content

        if not self.a.inline_json_vars:
            self.changes.append("Tidak ada inline JSON — skip migrasi isi")
            # Tetap perbaiki nama block jika salah
            content = self._fix_block_name(content)
            return content

        content = self._fix_block_name(content)
        content = self._inject_script_tags(content)
        content = self._fix_alpine_function(content)
        content = self._add_x_init_if_missing(content)

        return content

    def _fix_block_name(self, content: str) -> str:
        old_pattern = re.compile(
            r'\{%-?\s*block\s+scripts?\s*-?%\}', re.I
        )
        if old_pattern.search(content):
            content = old_pattern.sub('{% block extra_scripts %}', content)
            # Cari endblock yang match
            content = re.sub(
                r'\{%-?\s*endblock\s+scripts?\s*-?%\}',
                '{% endblock %}',
                content, flags=re.I
            )
            self.changes.append("Block 'scripts' → 'extra_scripts'")
        return content

    def _inject_script_tags(self, content: str) -> str:
        """Buat script tag JSON untuk setiap inline var, lalu hapus inline binding."""
        vars_to_migrate = self.a.inline_json_vars

        # Buat kumpulan script tag
        script_tags = []
        for var in vars_to_migrate:
            tag_id = var.replace("_json", "").replace("_", "-") + "-data"
            script_tags.append(
                f'<script id="{tag_id}" type="application/json">\n'
                f'{{{{ {var}|safe }}}}\n'
                f'</script>'
            )

        script_tags_str = "\n\n".join(script_tags)

        # Cari block extra_scripts dan sisipkan script tags di awal
        def insert_after_block(m):
            return m.group(0) + "\n" + script_tags_str + "\n"

        content = re.sub(
            r'\{%-?\s*block extra_scripts\s*-?%\}',
            insert_after_block,
            content
        )

        # Hapus inline JSON dari dalam function Alpine
        for var in vars_to_migrate:
            # Pattern: prop: {{ var|safe }},
            content = re.sub(
                rf'\b(\w+)\s*:\s*\{{\{{\s*{re.escape(var)}\s*\|safe\s*\}}\}}\s*,?',
                lambda m: f'{m.group(1)}: [],',
                content
            )
            # Pattern: = {{ var|safe }}
            content = re.sub(
                rf'=\s*\{{\{{\s*{re.escape(var)}\s*\|safe\s*\}}\}}',
                '= []',
                content
            )

        self.changes.append(f"Inject {len(vars_to_migrate)} script tag JSON: {', '.join(vars_to_migrate)}")
        return content

    def _fix_alpine_function(self, content: str) -> str:
        """Tambahkan init() yang baca script tag ke dalam setiap Alpine function."""
        vars_to_migrate = self.a.inline_json_vars

        # Build loader code untuk semua vars
        loaders = []
        for var in vars_to_migrate:
            tag_id = var.replace("_json", "").replace("_", "-") + "-data"
            prop   = var.replace("_json", "")
            loaders.append(
                f"      const _{prop}Raw = document.getElementById('{tag_id}');\n"
                f"      if (_{prop}Raw) {{\n"
                f"        try {{ this.{prop} = JSON.parse(_{prop}Raw.textContent); }}\n"
                f"        catch(e) {{ console.error('{tag_id} parse error:', e); }}\n"
                f"      }}"
            )

        init_body = "\n".join(loaders)
        init_block = f"\n\n    init() {{\n{init_body}\n    }},"

        # Cek apakah sudah ada init()
        if re.search(r'\binit\s*\(\s*\)\s*\{', content):
            # Update init() yang sudah ada — tambah loader ke dalamnya
            def update_init(m):
                existing = m.group(0)
                # Tambahkan loader setelah baris pertama init() {
                return re.sub(
                    r'(init\s*\(\s*\)\s*\{)',
                    r'\1\n' + init_body,
                    existing
                )
            # Hanya update jika init tidak mengandung getElementById
            if 'getElementById' not in content:
                first_fn = self.a.alpine_functions[0] if self.a.alpine_functions else None
                if first_fn:
                    content = re.sub(
                        r'(init\s*\(\s*\)\s*\{)',
                        r'\1\n' + init_body,
                        content,
                        count=1
                    )
                    self.changes.append("Update init() — tambah loader JSON")
        else:
            # Sisipkan init() sebelum closing return object
            # Cari pola penutup function: return { ... } }
            def add_init(m):
                return m.group(1) + init_block + "\n  " + m.group(2)

            result = re.sub(
                r'((?:return\s*\{[^}]*(?:\{[^}]*\}[^}]*)*))(\s*\}\s*\})',
                add_init,
                content,
                count=1,
                flags=re.DOTALL
            )
            if result != content:
                content = result
                self.changes.append("Tambah fungsi init() ke Alpine function")

        return content

    def _add_x_init_if_missing(self, content: str) -> str:
        """Tambah x-init='init()' ke elemen x-data jika belum ada."""
        if 'x-data=' in content and 'x-init=' not in content:
            content = re.sub(
                r'(x-data="[^"]*")',
                r'\1 x-init="init()"',
                content,
                count=1
            )
            self.changes.append("Tambah x-init='init()' pada elemen x-data")
        return content


# ─────────────────────────────────────────────────────────
# VALIDATOR - Cek hasil migrasi
# ─────────────────────────────────────────────────────────

VALIDATION_CHECKS = [
    {
        "code": "BLOCK_CORRECT",
        "label": "Pakai {% block extra_scripts %}",
        "critical": True,
        "test": lambda c: bool(re.search(r'\{%[-\s]*block extra_scripts', c)),
    },
    {
        "code": "NO_OLD_BLOCK",
        "label": "Tidak ada {% block scripts %} lama",
        "critical": True,
        "test": lambda c: not bool(re.search(r'\{%[-\s]*block\s+scripts?\s*[-\%]\}', c, re.I)),
    },
    {
        "code": "HAS_SCRIPT_TAG",
        "label": "Ada <script type='application/json'>",
        "critical": True,
        "test": lambda c: 'type="application/json"' in c,
    },
    {
        "code": "NO_INLINE_JSON",
        "label": "Tidak ada inline {{ var_json|safe }} di luar script JSON tag",
        "critical": True,
        "test": lambda c: _check_no_inline_json(c),
    },
    {
        "code": "HAS_GET_ELEMENT",
        "label": "Alpine init() membaca getElementById",
        "critical": True,
        "test": lambda c: 'getElementById' in c and 'JSON.parse' in c,
    },
    {
        "code": "HAS_TRY_CATCH",
        "label": "Ada try/catch pada JSON.parse",
        "critical": False,
        "test": lambda c: bool(re.search(r'try\s*\{.*JSON\.parse', c, re.DOTALL)),
    },
    {
        "code": "HAS_X_DATA",
        "label": "Ada x-data pada elemen Alpine",
        "critical": False,
        "test": lambda c: 'x-data=' in c,
    },
    {
        "code": "HAS_X_INIT",
        "label": "Ada x-init='init()'",
        "critical": False,
        "test": lambda c: 'x-init=' in c,
    },
    {
        "code": "HAS_X_CLOAK",
        "label": "Ada x-cloak (hindari flash)",
        "critical": False,
        "test": lambda c: 'x-cloak' in c,
    },
    {
        "code": "SCRIPT_HAS_ID",
        "label": "Script tag JSON punya id unik",
        "critical": True,
        "test": lambda c: bool(re.search(r'<script\s+id="[\w-]+"\s+type="application/json"', c)),
    },
]

def _check_no_inline_json(content: str) -> bool:
    """Cek apakah masih ada inline {{ var_json|safe }} di dalam JS function (bukan di script tag JSON)."""
    # Hapus semua script tag type=application/json dulu (isinya boleh ada {{ var|safe }})
    content_stripped = re.sub(
        r'<script\s[^>]*type="application/json"[^>]*>.*?</script>',
        '', content, flags=re.DOTALL
    )
    # Cari {{ *_json|safe }} di konten yang tersisa
    remaining_inline = re.findall(
        r'\{\{\s*\w+_json\s*\|\s*safe\s*\}\}', content_stripped
    )
    return len(remaining_inline) == 0

def validate_file(path: Path) -> list[dict]:
    content = path.read_text(encoding="utf-8")
    results = []
    for check in VALIDATION_CHECKS:
        passed = check["test"](content)
        results.append({**check, "passed": passed})
    return results


# ─────────────────────────────────────────────────────────
# SCANNER - Scan seluruh direktori
# ─────────────────────────────────────────────────────────

def scan_directory(base_dir: Path) -> list[TemplateAnalysis]:
    templates = sorted(base_dir.rglob("*.html"))
    analyses = []
    for t in templates:
        try:
            a = TemplateAnalysis(t)
            analyses.append(a)
        except Exception as e:
            print(warn(f"Gagal analisis {t.name}: {e}"))
    return analyses


# ─────────────────────────────────────────────────────────
# PRINTER - Output ke terminal
# ─────────────────────────────────────────────────────────

def print_banner():
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════╗
║      LUMRA · JSON Injection Migration Tool          ║
╚══════════════════════════════════════════════════════╝{C.RESET}
""")

def print_analysis(a: TemplateAnalysis):
    score_color = C.GREEN if a.score >= 80 else C.YELLOW if a.score >= 50 else C.RED
    print(f"\n{bold(a.path.name)}")
    print(f"  {dim('Pattern  :')} {a.pattern_label}")
    print(f"  {dim('Score    :')} {score_color}{a.score}/100{C.RESET}")
    print(f"  {dim('JSON vars:')} {', '.join(a.inline_json_vars) if a.inline_json_vars else dim('(tidak ada)')}")
    print(f"  {dim('Block    :')} {'extra_scripts ✓' if a.has_extra_scripts else 'scripts (salah)' if a.has_old_scripts else 'tidak ada'}")

    if a.issues:
        print(f"  {dim('Issues   :')}")
        for issue in a.issues:
            fn = err if issue["severity"] == "error" else warn
            print(f"    {fn(issue['msg'])}")
            print(f"    {dim('  Fix: ' + issue['fix'])}")
    else:
        print(f"  {ok('Tidak ada issue — sudah OK!')}")

def print_validation(results: list[dict], path: Path):
    passed = sum(1 for r in results if r["passed"])
    critical_fail = [r for r in results if not r["passed"] and r["critical"]]
    score = int(passed / len(results) * 100)

    print(f"\n{bold('Validasi:')} {path.name}")
    print(f"  Score: {score}% ({passed}/{len(results)} checks pass)")

    if critical_fail:
        print(f"  {err(f'{len(critical_fail)} critical issue!')}")
    else:
        print(f"  {ok('Semua critical checks pass!')}")

    print()
    for r in results:
        icon = ok("") if r["passed"] else (err("") if r["critical"] else warn(""))
        tag  = f'{C.RED}[critical]{C.RESET}' if not r["passed"] and r["critical"] else ""
        print(f"  {icon}{r['label']} {tag}")

def print_scan_summary(analyses: list[TemplateAnalysis]):
    needs_mig  = [a for a in analyses if a.needs_migration]
    warnings   = [a for a in analyses if a.issues and not a.needs_migration]
    clean      = [a for a in analyses if not a.issues]

    print(f"\n{bold('SCAN SUMMARY')}")
    print(f"  Total template   : {len(analyses)}")
    print(f"  {err(f'Perlu migrasi    : {len(needs_mig)}')}")
    print(f"  {warn(f'Ada warning      : {len(warnings)}')}")
    print(f"  {ok( f'Sudah OK         : {len(clean)}')}")

    if needs_mig:
        print(f"\n{bold('Template yang perlu dimigrasi:')}")
        for a in needs_mig:
            rel = a.path.name
            vars_str = ', '.join(a.inline_json_vars[:3])
            if len(a.inline_json_vars) > 3:
                vars_str += f" +{len(a.inline_json_vars)-3}"
            print(f"  {err('✗')} {rel:<45} {dim(a.pattern_label):<18} {dim(vars_str)}")

    if warnings:
        print(f"\n{bold('Template dengan warning:')}")
        for a in warnings:
            print(f"  {warn('⚠')} {a.path.name}")


# ─────────────────────────────────────────────────────────
# COMMANDS
# ─────────────────────────────────────────────────────────

def cmd_scan(args):
    base = Path(args.dir)
    if not base.exists():
        print(err(f"Direktori tidak ditemukan: {base}"))
        sys.exit(1)

    print(info(f"Scanning: {base}"))
    analyses = scan_directory(base)
    print_scan_summary(analyses)

    if args.verbose:
        for a in analyses:
            if a.issues:
                print_analysis(a)


def cmd_analyze(args):
    path = Path(args.file)
    if not path.exists():
        print(err(f"File tidak ditemukan: {path}"))
        sys.exit(1)

    a = TemplateAnalysis(path)
    print_analysis(a)


def cmd_migrate(args):
    path = Path(args.file)
    if not path.exists():
        print(err(f"File tidak ditemukan: {path}"))
        sys.exit(1)

    a = TemplateAnalysis(path)
    print_analysis(a)

    if not a.needs_migration:
        print(ok("Tidak perlu migrasi!"))
        return

    migrator = TemplateMigrator(a, verbose=args.verbose)
    new_content = migrator.migrate()

    if args.dry:
        print(f"\n{bold('--- DRY RUN PREVIEW ---')}")
        # Tunjukkan diff sederhana
        old_lines = a.content.splitlines()
        new_lines = new_content.splitlines()
        changes = 0
        for i, (ol, nl) in enumerate(zip(old_lines, new_lines), 1):
            if ol != nl:
                changes += 1
                if changes <= 20:
                    print(f"  {C.RED}- {ol[:100]}{C.RESET}")
                    print(f"  {C.GREEN}+ {nl[:100]}{C.RESET}")
        added = len(new_lines) - len(old_lines)
        if added > 0:
            for nl in new_lines[len(old_lines):min(len(old_lines)+10, len(new_lines))]:
                print(f"  {C.GREEN}+ {nl[:100]}{C.RESET}")
        print(f"\n  Total perubahan: ~{changes + max(0, added)} baris")
        print(f"\n  {bold('Changes yang akan dilakukan:')}")
        for ch in migrator.changes:
            print(f"  {info(ch)}")
        return

    # Backup
    do_backup = not getattr(args, 'no_backup', False)
    if do_backup:
        bak = path.with_suffix(path.suffix + BACKUP_SUFFIX)
        shutil.copy2(path, bak)
        print(ok(f"Backup: {bak.name}"))

    # Tulis
    path.write_text(new_content, encoding="utf-8")
    print(ok(f"Migrated: {path.name}"))

    print(f"\n  {bold('Perubahan:')}")
    for ch in migrator.changes:
        print(f"  {info(ch)}")

    # Auto-validate
    print()
    results = validate_file(path)
    print_validation(results, path)


def cmd_batch(args):
    base = Path(args.dir)
    if not base.exists():
        print(err(f"Direktori tidak ditemukan: {base}"))
        sys.exit(1)

    analyses = scan_directory(base)
    to_migrate = [a for a in analyses if a.needs_migration]

    if not to_migrate:
        print(ok("Semua template sudah OK!"))
        return

    print(f"\n{bold(f'Akan migrate {len(to_migrate)} template:')} {'(DRY RUN)' if args.dry else ''}")
    for a in to_migrate:
        print(f"  {dim('·')} {a.path.name}  {dim(a.pattern_label)}")

    if not args.dry:
        confirm = input(f"\n{C.YELLOW}Lanjutkan? (y/N): {C.RESET}").strip().lower()
        if confirm != 'y':
            print("Dibatalkan.")
            return

    success, failed = 0, 0
    log = []

    for a in to_migrate:
        try:
            migrator = TemplateMigrator(a)
            new_content = migrator.migrate()

            if not args.dry:
                do_backup = not getattr(args, 'no_backup', False)
                if do_backup:
                    bak = a.path.with_suffix(a.path.suffix + BACKUP_SUFFIX)
                    shutil.copy2(a.path, bak)
                a.path.write_text(new_content, encoding="utf-8")

            results = validate_file(a.path) if not args.dry else []
            crit_fails = [r for r in results if not r["passed"] and r["critical"]]

            status = "dry_ok" if args.dry else ("ok" if not crit_fails else "warn")
            icon = ok(a.path.name) if status in ("ok","dry_ok") else warn(a.path.name)
            print(f"  {icon}  {dim(', '.join(migrator.changes[:2]))}")

            log.append({"file": a.path.name, "status": status, "changes": migrator.changes})
            success += 1

        except Exception as e:
            print(f"  {err(a.path.name)}: {e}")
            log.append({"file": a.path.name, "status": "error", "error": str(e)})
            failed += 1

    print(f"\n{bold('Selesai!')}")
    print(f"  {ok( f'Berhasil : {success}')}")
    if failed:
        print(f"  {err(f'Gagal    : {failed}')}")

    # Tulis log
    if not args.dry:
        log_path = Path("migration_log.json")
        existing = json.loads(log_path.read_text()) if log_path.exists() else []
        existing.extend([{**l, "timestamp": datetime.now().isoformat()} for l in log])
        log_path.write_text(json.dumps(existing, indent=2))
        print(f"  {info(f'Log: {log_path}')}")


def cmd_validate(args):
    path = Path(args.file)
    if not path.exists():
        print(err(f"File tidak ditemukan: {path}"))
        sys.exit(1)

    results = validate_file(path)
    print_validation(results, path)

    passed = all(r["passed"] for r in results if r["critical"])
    sys.exit(0 if passed else 1)


def cmd_report(args):
    base = Path(args.dir)
    if not base.exists():
        print(err(f"Direktori tidak ditemukan: {base}"))
        sys.exit(1)

    analyses = scan_directory(base)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    report_path = Path(f"migration_report_{ts}.md")

    needs_mig = [a for a in analyses if a.needs_migration]
    warnings  = [a for a in analyses if a.issues and not a.needs_migration]
    clean     = [a for a in analyses if not a.issues]

    lines = [
        f"# Migration Report — {datetime.now().strftime('%d %B %Y %H:%M')}",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Perlu migrasi | {len(needs_mig)} |",
        f"| Warning | {len(warnings)} |",
        f"| Sudah OK | {len(clean)} |",
        f"| **Total** | **{len(analyses)}** |",
        "",
        "## Template Perlu Migrasi",
        "",
        "| File | Pattern | JSON Vars | Issues |",
        "|------|---------|-----------|--------|",
    ]

    for a in needs_mig:
        errors = [i for i in a.issues if i["severity"] == "error"]
        lines.append(
            f"| {a.path.name} | {a.pattern_label} | "
            f"{', '.join(a.inline_json_vars)} | "
            f"{len(errors)} error(s) |"
        )

    lines += [
        "",
        "## Detail Issues",
        "",
    ]

    for a in needs_mig:
        lines.append(f"### {a.path.name}")
        for issue in a.issues:
            prefix = "🔴" if issue["severity"] == "error" else "🟡"
            lines.append(f"- {prefix} **{issue['code']}**: {issue['msg']}")
            lines.append(f"  - Fix: {issue['fix']}")
        lines.append("")

    lines += [
        "## Template Sudah OK",
        "",
    ]
    for a in clean:
        lines.append(f"- ✅ {a.path.name}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(ok(f"Report disimpan: {report_path}"))
    print_scan_summary(analyses)


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Lumra JSON Injection Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # Shared args
    def add_dir(p):  p.add_argument("--dir",  default=DEFAULT_TEMPLATE_DIR, help="Direktori template")
    def add_file(p): p.add_argument("--file", required=True, help="File template")
    def add_dry(p):  p.add_argument("--dry",  action="store_true", help="Dry-run (preview saja)")
    def add_bak(p):
        g = p.add_mutually_exclusive_group()
        g.add_argument("--backup",    action="store_true", default=True)
        g.add_argument("--no-backup", action="store_true")
    def add_verbose(p): p.add_argument("--verbose", action="store_true")

    p_scan = sub.add_parser("scan",     help="Scan semua template di direktori")
    add_dir(p_scan); add_verbose(p_scan)

    p_ana = sub.add_parser("analyze",   help="Analisis satu file template")
    add_file(p_ana)

    p_mig = sub.add_parser("migrate",   help="Migrate satu file template")
    add_file(p_mig); add_dry(p_mig); add_bak(p_mig); add_verbose(p_mig)

    p_bat = sub.add_parser("batch",     help="Migrate semua template yang perlu")
    add_dir(p_bat); add_dry(p_bat); add_bak(p_bat)

    p_val = sub.add_parser("validate",  help="Validasi satu file hasil migrasi")
    add_file(p_val)

    p_rep = sub.add_parser("report",    help="Generate laporan markdown")
    add_dir(p_rep)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "scan":     cmd_scan,
        "analyze":  cmd_analyze,
        "migrate":  cmd_migrate,
        "batch":    cmd_batch,
        "validate": cmd_validate,
        "report":   cmd_report,
    }

    dispatch[args.command](args)
    print()


if __name__ == "__main__":
    main()