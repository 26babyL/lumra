#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         LUMRA - JSON Injection Migration Tool v2                            ║
║         Full-depth fix: block rename + JSON inject + Chart.js data          ║
╚══════════════════════════════════════════════════════════════════════════════╝

USAGE:
  python lumra_migrate_v2.py scan     [--dir PATH]            # Scan & laporan
  python lumra_migrate_v2.py analyze  --file PATH             # Analisis 1 file
  python lumra_migrate_v2.py migrate  --file PATH [--dry]     # Fix 1 file
  python lumra_migrate_v2.py batch    [--dir PATH] [--dry]    # Fix semua
  python lumra_migrate_v2.py validate --file PATH             # Validasi hasil
  python lumra_migrate_v2.py report   [--dir PATH]            # Laporan .md
"""

import re
import sys
import json
import shutil
import argparse
from copy import deepcopy
from pathlib import Path
from datetime import datetime
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL COLORS
# ─────────────────────────────────────────────────────────────────────────────

class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

def clr(color, text): return f"{color}{text}{C.RESET}"
def ok(t):   return clr(C.GREEN,  f"✓ {t}")
def err(t):  return clr(C.RED,    f"✗ {t}")
def warn(t): return clr(C.YELLOW, f"⚠ {t}")
def info(t): return clr(C.CYAN,   f"→ {t}")
def bold(t): return clr(C.BOLD, t)
def dim(t):  return clr(C.DIM, t)

BACKUP_SUFFIX = ".bak"
DEFAULT_DIR   = "lumra_config/templates/lumra_pages"

# ─────────────────────────────────────────────────────────────────────────────
# DETECTOR — Analisis mendalam isi template
# ─────────────────────────────────────────────────────────────────────────────

class TemplateAnalysis:
    """
    Mendeteksi SEMUA jenis masalah dalam template:
    1. Inline JSON vars di dalam JS function      → {{ var_json|safe }}
    2. Block scripts lama                          → {% block scripts %}
    3. Chart.js / Apex data yang di-hardcode       → labels: {{ x|safe }}
    4. Var non-json yang perlu script tag          → {{ labels|safe }}, dll
    5. Alpine function tanpa init()
    6. x-data tanpa x-init
    """

    def __init__(self, path: Path):
        self.path    = path
        self.content = path.read_text(encoding="utf-8")
        self.module  = self._detect_module()
        self._run()

    def _detect_module(self) -> str:
        parts = self.path.parts
        known = ["accounting", "inventory", "sales", "purchasing",
                 "reports", "crm", "production", "settings"]
        for p in parts:
            if p in known:
                return p.capitalize()
        return "Other"

    def _run(self):
        c = self.content

        # ── Semua script blocks ──────────────────────────────────────────────
        # Ambil seluruh konten script blocks (bukan type=application/json)
        self._all_js_blocks = re.findall(
            r'<script(?!\s[^>]*type=["\']application/json["\'])[^>]*>(.*?)</script>',
            c, re.DOTALL
        )
        js_combined = "\n".join(self._all_js_blocks)

        # ── Inline JSON vars  ( {{ varname|safe }} di dalam JS ) ────────────
        # Termasuk var yang berakhiran _json MAUPUN yang bukan (labels, dll)
        self.inline_json_vars = list(dict.fromkeys(
            re.findall(r'\{\{\s*(\w+_json)\s*\|safe\s*\}\}', js_combined)
        ))

        # Var non-_json yang di-pipe safe di dalam JS (Chart labels, data arrays)
        self.inline_other_vars = list(dict.fromkeys([
            v for v in re.findall(r'\{\{\s*(\w+)\s*\|safe\s*\}\}', js_combined)
            if not v.endswith('_json')
        ]))

        # Gabungan semua var yang perlu dimigrate
        self.all_inline_vars = self.inline_json_vars + self.inline_other_vars

        # ── Block type ───────────────────────────────────────────────────────
        self.has_extra_scripts = bool(re.search(r'\{%[-\s]*block extra_scripts', c))
        self.has_old_scripts   = bool(re.search(r'\{%[-\s]*block\s+scripts?\s*[-\%]\}', c, re.I))

        # ── Script tag JSON yang sudah ada ───────────────────────────────────
        self.existing_script_tags = re.findall(
            r'<script\s+id="([\w-]+)"\s+type="application/json"', c
        )

        # ── Alpine ───────────────────────────────────────────────────────────
        self.has_x_data  = 'x-data=' in c
        self.has_x_init  = 'x-init=' in c
        self.has_x_cloak = 'x-cloak' in c

        # Nama Alpine functions
        self.alpine_fns = list(dict.fromkeys(
            re.findall(r'function\s+(\w+)\s*\(\s*\)\s*\{', js_combined) +
            re.findall(r'x-data="(\w+)\(\)"', c)
        ))

        # Sudah ada init() ?
        self.has_init_fn = bool(re.search(r'\binit\s*\(\s*\)\s*\{', js_combined))
        self.has_get_element = 'getElementById' in js_combined

        # ── Chart.js / ApexCharts detection ──────────────────────────────────
        self.has_chartjs = bool(re.search(r'new Chart\(|Chart\.', js_combined))
        self.has_apex    = bool(re.search(r'new ApexCharts|ApexCharts\(', js_combined))

        # ── Pattern otomatis ─────────────────────────────────────────────────
        self.detected_pattern = self._detect_pattern()

        # ── Issues & Score ───────────────────────────────────────────────────
        self.issues = self._collect_issues()
        self.score  = self._compute_score()

    # ── Pattern Detection ────────────────────────────────────────────────────

    def _detect_pattern(self) -> str:
        c  = self.content.lower()
        nv = len(self.all_inline_vars)

        if self.has_chartjs or self.has_apex:
            return "chart_data"
        if nv >= 4:
            return "complex_report"
        if nv == 2 or nv == 3:
            return "dual_json"
        if re.search(r'journal|voucher|form.*post|method.*post', c) and 'select' in c:
            return "form_dropdown"
        if re.search(r'aging|overdue|bucket|days.*due', c):
            return "aging_table"
        if re.search(r'balance.*sheet|profit.*loss|cash.*flow|neraca|laba.*rugi', c):
            return "complex_report"
        return "simple_list"

    PATTERN_LABELS = {
        "simple_list":    "Simple List",
        "dual_json":      "Dual JSON",
        "form_dropdown":  "Form + Dropdown",
        "aging_table":    "Aging Table",
        "complex_report": "Complex Report",
        "chart_data":     "Chart.js Data",
    }

    @property
    def pattern_label(self): return self.PATTERN_LABELS.get(self.detected_pattern, self.detected_pattern)

    # ── Issue Collector ───────────────────────────────────────────────────────

    def _collect_issues(self):
        issues = []
        c = self.content

        # ERROR: inline _json vars di JS
        for v in self.inline_json_vars:
            issues.append({
                "sev": "error", "code": "INLINE_JSON_VAR",
                "msg": f"Inline JSON: {{{{ {v}|safe }}}} di dalam script JS",
                "fix": f"Pindah ke <script id='...' type='application/json'>",
                "var": v,
            })

        # WARNING: inline non-json vars di JS (Chart labels dll)
        for v in self.inline_other_vars:
            issues.append({
                "sev": "warning", "code": "INLINE_OTHER_VAR",
                "msg": f"Inline var non-json: {{{{ {v}|safe }}}} di dalam script",
                "fix": f"Pertimbangkan script tag JSON juga untuk {v}",
                "var": v,
            })

        # ERROR: block salah nama
        if self.has_old_scripts:
            issues.append({
                "sev": "error", "code": "WRONG_BLOCK",
                "msg": "{% block scripts %} → harus {% block extra_scripts %}",
                "fix": "Rename block"
            })

        # WARNING: tidak ada block scripts sama sekali
        if not self.has_extra_scripts and not self.has_old_scripts:
            if self.has_x_data or self.all_inline_vars:
                issues.append({
                    "sev": "warning", "code": "NO_BLOCK",
                    "msg": "Template punya Alpine/JS tapi tidak ada block scripts",
                    "fix": "Tambahkan {% block extra_scripts %}...{% endblock %}"
                })

        # WARNING: x-data tanpa x-init
        if self.has_x_data and not self.has_x_init and self.all_inline_vars:
            issues.append({
                "sev": "warning", "code": "NO_X_INIT",
                "msg": "x-data ada, x-init='init()' tidak ada",
                "fix": "Tambahkan x-init='init()' pada elemen x-data"
            })

        # WARNING: sudah ada JSON tapi init() tidak baca script tag
        if self.existing_script_tags and not self.has_get_element:
            issues.append({
                "sev": "warning", "code": "INIT_NOT_READING",
                "msg": "Script tag JSON ada tapi init() tidak pakai getElementById",
                "fix": "Update init() untuk baca dari script tag"
            })

        return issues

    def _compute_score(self):
        score = 100
        for i in self.issues:
            score -= 30 if i["sev"] == "error" else 10
        return max(0, score)

    # ── Status ────────────────────────────────────────────────────────────────

    @property
    def status(self):
        if any(i["sev"] == "error" for i in self.issues):
            return "error"
        if self.issues:
            return "warn"
        return "ok"

    @property
    def needs_migration(self):
        return self.status in ("error", "warn")


# ─────────────────────────────────────────────────────────────────────────────
# MIGRATOR — Transform konten template
# ─────────────────────────────────────────────────────────────────────────────

class TemplateMigrator:
    def __init__(self, analysis: TemplateAnalysis):
        self.a       = analysis
        self.changes = []
        self._new    = analysis.content  # working copy

    # ── Public API ────────────────────────────────────────────────────────────

    def migrate(self) -> str:
        # Step 1: Rename block (selalu)
        self._rename_block()

        # Step 2: Inject script tags JSON untuk setiap inline var
        if self.a.all_inline_vars:
            self._inject_script_tags()
            self._remove_inline_bindings()
            self._upsert_init_function()
            self._add_x_init_if_missing()

        # Step 3: Fix init() yang sudah ada tapi tidak baca script tag
        elif self.a.existing_script_tags and not self.a.has_get_element:
            self._fix_existing_init()

        return self._new

    # ── Step 1: Rename Block ──────────────────────────────────────────────────

    def _rename_block(self):
        old = re.compile(r'\{%-?\s*block\s+scripts?\s*-?%\}', re.I)
        if not old.search(self._new):
            return

        self._new = old.sub('{% block extra_scripts %}', self._new)
        self._new = re.sub(
            r'\{%-?\s*endblock\s+scripts?\s*-?%\}',
            '{% endblock %}',
            self._new, flags=re.I
        )
        self.changes.append("Rename: {% block scripts %} → {% block extra_scripts %}")

    # ── Step 2a: Inject script tags ───────────────────────────────────────────

    def _var_to_tag_id(self, var: str) -> str:
        """invoices_json → invoices-data, trend_labels → trend-labels-data"""
        base = var.replace("_json", "").replace("_", "-")
        return f"{base}-data"

    def _inject_script_tags(self):
        vars_to_inject = [
            v for v in self.a.all_inline_vars
            if self._var_to_tag_id(v) not in self.a.existing_script_tags
        ]
        if not vars_to_inject:
            return

        tags = []
        for var in vars_to_inject:
            tag_id = self._var_to_tag_id(var)
            tags.append(
                f'<script id="{tag_id}" type="application/json">\n'
                f'{{{{ {var}|safe }}}}\n'
                f'</script>'
            )

        tags_str = "\n\n".join(tags) + "\n\n"

        # Sisipkan setelah {% block extra_scripts %}
        self._new = re.sub(
            r'(\{%-?\s*block extra_scripts\s*-?%\})',
            r'\1\n' + tags_str,
            self._new,
            count=1
        )
        self.changes.append(
            f"Inject {len(vars_to_inject)} script tag JSON: "
            + ", ".join(vars_to_inject[:5])
            + (f" +{len(vars_to_inject)-5} lainnya" if len(vars_to_inject) > 5 else "")
        )

    # ── Step 2b: Hapus inline bindings ───────────────────────────────────────

    def _remove_inline_bindings(self):
        """Ganti {{ var|safe }} di dalam JS function dengan [] atau nilai kosong."""
        # Dapatkan semua JS script blocks (bukan type=application/json)
        def replace_in_js(content: str, var: str) -> str:
            # Pattern: propertyName: {{ var|safe }},
            content = re.sub(
                rf'(\b\w+\b\s*:\s*)\{{\{{\s*{re.escape(var)}\s*\|safe\s*\}}\}}(\s*,?)',
                r'\1[]\2',
                content
            )
            # Pattern: = {{ var|safe }}
            content = re.sub(
                rf'=\s*\{{\{{\s*{re.escape(var)}\s*\|safe\s*\}}\}}',
                '= []',
                content
            )
            # Pattern: labels: {{ var|safe }} (tanpa koma akhir)
            content = re.sub(
                rf'(\b\w+\b\s*:\s*)\{{\{{\s*{re.escape(var)}\s*\|safe\s*\}}\}}',
                r'\1[]',
                content
            )
            return content

        for var in self.a.all_inline_vars:
            self._new = replace_in_js(self._new, var)

        self.changes.append(f"Hapus {len(self.a.all_inline_vars)} inline binding dari JS")

    # ── Step 2c: Upsert init() ────────────────────────────────────────────────

    def _build_loader_code(self, vars_list: list, indent_n: int = 6) -> str:
        """Build kode loader untuk semua vars."""
        pad    = " " * indent_n
        loaders = []
        for var in vars_list:
            tag_id = self._var_to_tag_id(var)
            prop   = var.replace("_json", "")
            loaders.append(
                f"{pad}const _{prop}El = document.getElementById('{tag_id}');\n"
                f"{pad}if (_{prop}El) {{\n"
                f"{pad}  try {{ this.{prop} = JSON.parse(_{prop}El.textContent); }}\n"
                f"{pad}  catch(e) {{ console.error('[lumra] {tag_id}:', e); }}\n"
                f"{pad}}}"
            )
        return "\n\n".join(loaders)

    def _upsert_init_function(self):
        """Tambahkan atau update init() di dalam Alpine function."""
        loader_code = self._build_loader_code(self.a.all_inline_vars)

        if self.a.has_init_fn and not self.a.has_get_element:
            # Sudah ada init(), tapi belum baca script tag → inject di awal init()
            self._new = re.sub(
                r'(init\s*\(\s*\)\s*\{)',
                r'\1\n' + loader_code,
                self._new,
                count=1
            )
            self.changes.append("Update init() — tambah loader script tag")

        elif not self.a.has_init_fn:
            # Belum ada init() → cari Alpine return object dan sisipkan
            # Cari pola: function FnName() { return { ... } }
            # Sisipkan init() sebelum closing } dari return object
            inserted = self._insert_init_into_return(loader_code)
            if inserted:
                self.changes.append("Tambah fungsi init() ke Alpine return object")
            else:
                # Fallback: append di akhir block extra_scripts
                self._new = re.sub(
                    r'(\{%-?\s*endblock\s*-?%\})',
                    self._build_standalone_init(loader_code) + r'\n\1',
                    self._new,
                    count=1
                )
                self.changes.append("Tambah init() standalone (fallback)")

    def _insert_init_into_return(self, loader_code: str) -> bool:
        """Sisipkan init() ke dalam return { } dari Alpine function."""
        # Pattern: mendeteksi return object dari Alpine function
        pattern = re.compile(
            r'(function\s+\w+\s*\(\s*\)\s*\{[^}]*return\s*\{)'
            r'((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)'
            r'(\s*\})',
            re.DOTALL
        )

        init_snippet = (
            "\n\n    init() {\n"
            + loader_code
            + "\n    },"
        )

        def inject(m):
            return m.group(1) + m.group(2) + init_snippet + m.group(3)

        new_content = pattern.sub(inject, self._new, count=1)
        if new_content != self._new:
            self._new = new_content
            return True
        return False

    def _build_standalone_init(self, loader_code: str) -> str:
        fn_name = self.a.alpine_fns[0] if self.a.alpine_fns else "pageApp"
        return (
            f"\n<script>\n"
            f"// Auto-generated init() by lumra_migrate_v2\n"
            f"document.addEventListener('alpine:init', () => {{\n"
            f"  Alpine.data('{fn_name}', () => ({{...{fn_name}(), init() {{\n"
            f"{loader_code}\n"
            f"  }}}}))\n"
            f"}});\n"
            f"</script>"
        )

    def _fix_existing_init(self):
        """Fix init() yang sudah ada tapi tidak baca script tag."""
        loader_code = self._build_loader_code(self.a.existing_script_tags, indent_n=6)
        self._new = re.sub(
            r'(init\s*\(\s*\)\s*\{)',
            r'\1\n' + loader_code,
            self._new, count=1
        )
        self.changes.append("Fix init() — tambah getElementById untuk script tags yang ada")

    # ── Step 3: x-init ────────────────────────────────────────────────────────

    def _add_x_init_if_missing(self):
        if 'x-data=' in self._new and 'x-init=' not in self._new:
            self._new = re.sub(
                r'(x-data="[^"]*")',
                r'\1 x-init="init()"',
                self._new, count=1
            )
            self.changes.append("Tambah x-init='init()' pada elemen x-data")


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATOR — 12 titik cek
# ─────────────────────────────────────────────────────────────────────────────

CHECKS = [
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
        "test": lambda c: _has_any_json_script(c),
    },
    {
        "code": "NO_INLINE_JSON",
        "label": "Tidak ada inline {{ var_json|safe }} di JS function",
        "critical": True,
        "test": lambda c: _no_inline_json_in_js(c),
    },
    {
        "code": "NO_INLINE_OTHER",
        "label": "Tidak ada inline {{ var|safe }} non-json di JS function",
        "critical": False,
        "test": lambda c: _no_inline_other_in_js(c),
    },
    {
        "code": "HAS_GET_ELEMENT",
        "label": "init() membaca dengan getElementById",
        "critical": True,
        "test": lambda c: _init_reads_script_tag(c),
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
        "label": "Ada x-cloak (hindari FOUC)",
        "critical": False,
        "test": lambda c: 'x-cloak' in c,
    },
    {
        "code": "SCRIPT_HAS_ID",
        "label": "Script tag JSON punya id unik",
        "critical": True,
        "test": lambda c: bool(re.search(r'<script\s+id="[\w-]+"\s+type="application/json"', c)),
    },
    {
        "code": "NO_DUPLICATE_ID",
        "label": "Tidak ada script tag dengan id duplikat",
        "critical": False,
        "test": lambda c: _no_duplicate_script_ids(c),
    },
]

def _has_any_json_script(c: str) -> bool:
    return 'type="application/json"' in c

def _no_inline_json_in_js(c: str) -> bool:
    # Strip script tags JSON terlebih dahulu
    stripped = re.sub(
        r'<script\s[^>]*type=["\']application/json["\'][^>]*>.*?</script>',
        '', c, flags=re.DOTALL
    )
    js_blocks = re.findall(
        r'<script(?!\s[^>]*type=["\']application/json["\'])[^>]*>(.*?)</script>',
        stripped, re.DOTALL
    )
    combined = "\n".join(js_blocks)
    return not bool(re.search(r'\{\{\s*\w+_json\s*\|\s*safe\s*\}\}', combined))

def _no_inline_other_in_js(c: str) -> bool:
    stripped = re.sub(
        r'<script\s[^>]*type=["\']application/json["\'][^>]*>.*?</script>',
        '', c, flags=re.DOTALL
    )
    js_blocks = re.findall(
        r'<script(?!\s[^>]*type=["\']application/json["\'])[^>]*>(.*?)</script>',
        stripped, re.DOTALL
    )
    combined = "\n".join(js_blocks)
    other = re.findall(r'\{\{\s*(\w+)\s*\|\s*safe\s*\}\}', combined)
    return len(other) == 0

def _init_reads_script_tag(c: str) -> bool:
    js_blocks = re.findall(
        r'<script(?!\s[^>]*type=["\']application/json["\'])[^>]*>(.*?)</script>',
        c, re.DOTALL
    )
    combined = "\n".join(js_blocks)
    # Cek apakah ada init yang baca getElementById
    return 'getElementById' in combined and 'JSON.parse' in combined

def _no_duplicate_script_ids(c: str) -> bool:
    ids = re.findall(r'<script\s+id="([\w-]+)"\s+type="application/json"', c)
    return len(ids) == len(set(ids))

def validate_file(path: Path) -> list:
    content = path.read_text(encoding="utf-8")
    results = []
    for check in CHECKS:
        # Skip checks yang tidak relevan (tidak ada script JSON tag → skip check terkait)
        if check["code"] in ("HAS_GET_ELEMENT","SCRIPT_HAS_ID","NO_DUPLICATE_ID","HAS_TRY_CATCH"):
            if not _has_any_json_script(content):
                results.append({**check, "passed": True, "skipped": True})
                continue
        results.append({**check, "passed": check["test"](content), "skipped": False})
    return results


# ─────────────────────────────────────────────────────────────────────────────
# SCANNER
# ─────────────────────────────────────────────────────────────────────────────

def scan_directory(base_dir: Path) -> list:
    templates = sorted(base_dir.rglob("*.html"))
    analyses  = []
    for t in templates:
        try:
            analyses.append(TemplateAnalysis(t))
        except Exception as e:
            print(warn(f"Gagal baca {t.name}: {e}"))
    return analyses


# ─────────────────────────────────────────────────────────────────────────────
# PRINTER
# ─────────────────────────────────────────────────────────────────────────────

def print_banner():
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════╗
║      LUMRA · JSON Injection Migration Tool v2           ║
╚══════════════════════════════════════════════════════════╝{C.RESET}
""")

def print_analysis(a: TemplateAnalysis, verbose=False):
    sc = C.GREEN if a.score >= 80 else C.YELLOW if a.score >= 50 else C.RED
    status_icon = ok("") if a.status == "ok" else warn("") if a.status == "warn" else err("")

    print(f"\n{status_icon}{bold(a.path.name)}")
    print(f"  {dim('Modul    :')} {a.module}")
    print(f"  {dim('Pattern  :')} {a.pattern_label}")
    print(f"  {dim('Score    :')} {sc}{a.score}/100{C.RESET}")

    if a.all_inline_vars:
        print(f"  {dim('JSON vars:')} {', '.join(a.all_inline_vars)}")
    if a.inline_other_vars:
        print(f"  {dim('Other vars:')} {', '.join(a.inline_other_vars)}")

    block_state = "extra_scripts ✓" if a.has_extra_scripts else \
                  f"{C.RED}scripts (salah){C.RESET}" if a.has_old_scripts else \
                  dim("tidak ada")
    print(f"  {dim('Block    :')} {block_state}")

    if a.has_chartjs: print(f"  {dim('Chart    :')} Chart.js terdeteksi")
    if a.has_apex:    print(f"  {dim('Chart    :')} ApexCharts terdeteksi")

    if a.issues:
        for issue in a.issues:
            fn = err if issue["sev"] == "error" else warn
            print(f"  {fn(issue['msg'])}")
            if verbose:
                print(f"    {dim('Fix: ' + issue['fix'])}")
    else:
        print(f"  {ok('Tidak ada issue — sudah OK!')}")

def print_validation(results: list, path: Path):
    passed   = sum(1 for r in results if r["passed"])
    skipped  = sum(1 for r in results if r.get("skipped"))
    critical_fail = [r for r in results if not r["passed"] and r["critical"] and not r.get("skipped")]
    score    = int(passed / len(results) * 100)

    print(f"\n{bold('Validasi:')} {path.name}")
    print(f"  Score: {score}% ({passed}/{len(results)} pass, {skipped} skip)")

    if critical_fail:
        print(f"  {err(str(len(critical_fail)) + ' critical issue harus diperbaiki!')}")
    else:
        print(f"  {ok('Semua critical checks pass!')}")

    print()
    for r in results:
        if r.get("skipped"):
            icon = dim("⊘")
            tag  = dim("[skip]")
        elif r["passed"]:
            icon = ok("")
            tag  = ""
        else:
            icon = err("") if r["critical"] else warn("")
            tag  = f'{C.RED}[critical]{C.RESET}' if r["critical"] else ""
        print(f"  {icon}{r['label']} {tag}")

def print_scan_summary(analyses: list):
    ok_t   = [a for a in analyses if a.status == "ok"]
    warn_t = [a for a in analyses if a.status == "warn"]
    err_t  = [a for a in analyses if a.status == "error"]

    # Module breakdown
    modules = {}
    for a in analyses:
        m = modules.setdefault(a.module, {"ok":0,"warn":0,"error":0,"total":0})
        m[a.status] += 1
        m["total"] += 1

    print(f"\n{'═'*60}")
    print(bold("SCAN SUMMARY"))
    print(f"{'─'*60}")
    print(f"  {ok( f'Sudah OK         : {len(ok_t):3d}')}")
    print(f"  {warn(f'Warning (WARN)   : {len(warn_t):3d}')}")
    print(f"  {err( f'Error (kritis)   : {len(err_t):3d}')}")
    print(f"  {dim( f'Total            : {len(analyses):3d}')}")

    print(f"\n{bold('Per Modul:')}")
    for mod, counts in sorted(modules.items()):
        bar = (f"{C.GREEN}✓{counts['ok']}{C.RESET} "
               f"{C.YELLOW}⚠{counts['warn']}{C.RESET} "
               f"{C.RED}✗{counts['error']}{C.RESET}")
        print(f"  {mod:<20} {bar}  {dim(str(counts['total'])+' template')}")

    if err_t:
        print(f"\n{bold('ERROR — harus difix:')}")
        for a in err_t[:20]:
            print(f"  {err(a.path.name):<50} {dim(a.pattern_label)}")

    if warn_t:
        print(f"\n{bold('WARN — perlu review:')}")
        for a in warn_t[:30]:
            vars_str = (", ".join(a.all_inline_vars[:3])
                       + (f" +{len(a.all_inline_vars)-3}" if len(a.all_inline_vars) > 3 else ""))
            issues_str = "; ".join(i["code"] for i in a.issues[:2])
            print(f"  {warn(a.path.name):<50} {dim(issues_str)}")

    print(f"{'═'*60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# COMMANDS
# ─────────────────────────────────────────────────────────────────────────────

def cmd_scan(args):
    base = Path(args.dir)
    if not base.exists(): _abort(f"Direktori tidak ditemukan: {base}")
    print(info(f"Scanning: {base.resolve()}"))
    analyses = scan_directory(base)
    print_scan_summary(analyses)

def cmd_analyze(args):
    path = Path(args.file)
    if not path.exists(): _abort(f"File tidak ditemukan: {path}")
    a = TemplateAnalysis(path)
    print_analysis(a, verbose=True)

def cmd_migrate(args):
    path = Path(args.file)
    if not path.exists(): _abort(f"File tidak ditemukan: {path}")

    a = TemplateAnalysis(path)
    print_analysis(a)

    if not a.needs_migration:
        print(ok("Tidak perlu migrasi!"))
        return

    migrator    = TemplateMigrator(a)
    new_content = migrator.migrate()

    if args.dry:
        _print_diff(a.content, new_content)
        print(f"\n  {bold('Yang akan dilakukan:')}")
        for ch in migrator.changes:
            print(f"  {info(ch)}")
        return

    _write_with_backup(path, new_content, args)
    print(ok(f"Migrated: {path.name}"))
    for ch in migrator.changes:
        print(f"  {info(ch)}")
    print()
    results = validate_file(path)
    print_validation(results, path)

def cmd_batch(args):
    base = Path(args.dir)
    if not base.exists(): _abort(f"Direktori tidak ditemukan: {base}")

    analyses   = scan_directory(base)
    to_migrate = [a for a in analyses if a.needs_migration]

    if not to_migrate:
        print(ok("Semua template sudah OK!"))
        return

    # Stats
    errors = [a for a in to_migrate if a.status == "error"]
    warns  = [a for a in to_migrate if a.status == "warn"]

    print(f"\n{bold(f'Template yang akan diproses: {len(to_migrate)}')}"
          f"{'  ' + dim('(DRY RUN)') if args.dry else ''}")
    print(f"  {err(f'Error: {len(errors)}')}")
    print(f"  {warn(f'Warn : {len(warns)}')}")

    if not args.dry:
        try:
            confirm = input(f"\n{C.YELLOW}Lanjutkan migrasi? (y/N): {C.RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nDibatalkan.")
            return
        if confirm != 'y':
            print("Dibatalkan.")
            return

    success, failed = 0, 0
    log = []
    stats = {"block_rename":0, "json_inject":0, "init_added":0, "x_init_added":0}

    for a in to_migrate:
        try:
            migrator    = TemplateMigrator(a)
            new_content = migrator.migrate()

            if not args.dry:
                _write_with_backup(a.path, new_content, args)

            # Update stats
            for ch in migrator.changes:
                if "Rename" in ch:            stats["block_rename"] += 1
                if "Inject" in ch or "script tag" in ch: stats["json_inject"] += 1
                if "init()" in ch.lower() and "Tambah" in ch: stats["init_added"] += 1
                if "x-init" in ch:            stats["x_init_added"] += 1

            # Validate (only if actually written)
            crit_fails = 0
            if not args.dry:
                results    = validate_file(a.path)
                crit_fails = sum(1 for r in results
                                 if not r["passed"] and r["critical"] and not r.get("skipped"))

            status = "dry" if args.dry else ("ok" if not crit_fails else "warn")
            icon   = ok(a.path.name) if status in ("ok","dry") else warn(a.path.name)
            print(f"  {icon:<65} {dim(', '.join(migrator.changes[:2]))}")

            log.append({
                "file": a.path.name,
                "module": a.module,
                "status": status,
                "changes": migrator.changes,
                "timestamp": datetime.now().isoformat(),
            })
            success += 1

        except Exception as e:
            print(f"  {err(a.path.name)}: {e}")
            log.append({"file": a.path.name, "status": "error", "error": str(e),
                        "timestamp": datetime.now().isoformat()})
            failed += 1

    # Summary
    print(f"\n{'─'*60}")
    print(f"  {ok( f'Berhasil : {success}')}")
    if failed: print(f"  {err(f'Gagal    : {failed}')}")
    print(f"\n  {dim('Stats:')}")
    print(f"    Block rename  : {stats['block_rename']}")
    print(f"    JSON injected : {stats['json_inject']}")
    print(f"    init() added  : {stats['init_added']}")
    print(f"    x-init added  : {stats['x_init_added']}")

    if not args.dry:
        _write_log(log)

def cmd_validate(args):
    path = Path(args.file)
    if not path.exists(): _abort(f"File tidak ditemukan: {path}")
    results = validate_file(path)
    print_validation(results, path)
    critical_ok = all(r["passed"] for r in results if r["critical"] and not r.get("skipped"))
    sys.exit(0 if critical_ok else 1)

def cmd_report(args):
    base = Path(args.dir)
    if not base.exists(): _abort(f"Direktori tidak ditemukan: {base}")

    analyses = scan_directory(base)
    ts       = datetime.now().strftime("%Y-%m-%d_%H-%M")
    out_path = Path(f"migration_report_{ts}.md")

    ok_t   = [a for a in analyses if a.status == "ok"]
    warn_t = [a for a in analyses if a.status == "warn"]
    err_t  = [a for a in analyses if a.status == "error"]

    # Module stats
    modules: dict = {}
    for a in analyses:
        m = modules.setdefault(a.module, {"ok":0,"warn":0,"error":0,"total":0})
        m[a.status] += 1
        m["total"] += 1

    lines = [
        f"# Migration Report — {datetime.now().strftime('%d %B %Y %H:%M')}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|-------|",
        f"| ✅ OK    | {len(ok_t)} |",
        f"| ⚠️ Warn  | {len(warn_t)} |",
        f"| ❌ Error | {len(err_t)} |",
        f"| **Total** | **{len(analyses)}** |",
        "",
        "## Per Module",
        "",
        "| Module | OK | Warn | Error | Total |",
        "|--------|----|------|-------|-------|",
    ]
    for mod, counts in sorted(modules.items()):
        lines.append(f"| {mod} | {counts['ok']} | {counts['warn']} | {counts['error']} | {counts['total']} |")

    lines += ["", "## Templates Butuh Fix", ""]
    for a in sorted(err_t + warn_t, key=lambda x: x.status):
        prefix = "❌" if a.status == "error" else "⚠️"
        vars_s = ", ".join(a.all_inline_vars) if a.all_inline_vars else "-"
        issues = "; ".join(i["code"] for i in a.issues)
        lines.append(f"### {prefix} `{a.path.name}` ({a.module})")
        lines.append(f"- Pattern : {a.pattern_label}")
        lines.append(f"- Vars    : {vars_s}")
        lines.append(f"- Issues  : {issues}")
        for issue in a.issues:
            sev = "🔴" if issue["sev"] == "error" else "🟡"
            lines.append(f"  - {sev} **{issue['code']}**: {issue['msg']}")
        lines.append("")

    lines += ["## Templates Sudah OK", ""]
    for a in ok_t:
        lines.append(f"- ✅ `{a.path.name}` ({a.module})")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(ok(f"Report: {out_path}"))
    print_scan_summary(analyses)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _abort(msg: str):
    print(err(msg))
    sys.exit(1)

def _write_with_backup(path: Path, content: str, args):
    do_backup = not getattr(args, "no_backup", False)
    if do_backup:
        bak = path.with_suffix(path.suffix + BACKUP_SUFFIX)
        shutil.copy2(path, bak)
    path.write_text(content, encoding="utf-8")

def _write_log(entries: list):
    log_path = Path("migration_log.json")
    existing = []
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text())
        except Exception:
            existing = []
    existing.extend(entries)
    log_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    print(f"  {info(f'Log: {log_path}')}")

def _print_diff(old: str, new: str):
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    print(f"\n{bold('─── DRY RUN PREVIEW ───')}")
    shown = 0
    max_lines = 30

    # Simple line-by-line diff
    import difflib
    differ = difflib.ndiff(old_lines, new_lines)
    for line in differ:
        if shown >= max_lines:
            print(f"  {dim('... (lebih banyak perubahan — jalankan tanpa --dry untuk apply)')}")
            break
        if line.startswith("- "):
            print(f"  {C.RED}- {line[2:100]}{C.RESET}")
            shown += 1
        elif line.startswith("+ "):
            print(f"  {C.GREEN}+ {line[2:100]}{C.RESET}")
            shown += 1


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print_banner()

    parser = argparse.ArgumentParser(
        prog="lumra_migrate_v2",
        description="Lumra JSON Injection Migration Tool v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    def _d(p): p.add_argument("--dir",  default=DEFAULT_DIR)
    def _f(p): p.add_argument("--file", required=True)
    def _dry(p): p.add_argument("--dry", action="store_true", help="Preview saja, tidak tulis file")
    def _bak(p):
        g = p.add_mutually_exclusive_group()
        g.add_argument("--backup",    action="store_true", default=True)
        g.add_argument("--no-backup", action="store_true")
    def _v(p): p.add_argument("--verbose", action="store_true")

    p_scan = sub.add_parser("scan",     help="Scan semua template")
    _d(p_scan); _v(p_scan)

    p_ana  = sub.add_parser("analyze",  help="Analisis 1 file")
    _f(p_ana)

    p_mig  = sub.add_parser("migrate",  help="Migrate 1 file")
    _f(p_mig); _dry(p_mig); _bak(p_mig)

    p_bat  = sub.add_parser("batch",    help="Migrate semua sekaligus")
    _d(p_bat); _dry(p_bat); _bak(p_bat)

    p_val  = sub.add_parser("validate", help="Validasi hasil migrasi")
    _f(p_val)

    p_rep  = sub.add_parser("report",   help="Generate laporan Markdown")
    _d(p_rep)

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