#!/usr/bin/env python3
"""
lumra_doc_generator.py
======================
Generate dokumentasi teknis Markdown dari source code Lumra ERP.

Membaca langsung:
  - settings.py      → konfigurasi (database, middleware, installed apps)
  - urls.py          → semua URL patterns
  - models.py        → semua model dan field
  - views/           → semua view functions
  - templates/       → struktur folder template

Output: satu file Markdown lengkap.

Cara pakai:
  python lumra_doc_generator.py
  python lumra_doc_generator.py --root D:\\APPS\\Project\\lumra
  python lumra_doc_generator.py --root D:\\APPS\\Project\\lumra --output docs/technical.md
  python lumra_doc_generator.py --root . --sections arch,models,urls
"""

import re
import ast
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_ROOT   = Path(r"D:\APPS\Project\lumra")
DEFAULT_OUTPUT = Path(r"D:\APPS\Project\lumra\docs\technical_doc.md")

# Nama app utama (folder yang berisi models.py, views/, templates/)
APP_NAME = "lumra_config"

# Nama Django project config folder (berisi settings.py, urls.py)
PROJECT_NAME = "lumra_system"

# Section labels untuk URL grouping
# Key = keyword di module path, Value = emoji + label
URL_SECTION_MAP = {
    "sales"       : ("🛒", "Sales & POS"),
    "pos"         : ("🛒", "Sales & POS"),
    "dashboard"   : ("🛒", "Sales & POS"),
    "notification": ("🛒", "Sales & POS"),
    "purchasing"  : ("🛒", "Sales & POS"),
    "master"      : ("📦", "Master Data"),
    "customer"    : ("📦", "Master Data"),
    "category"    : ("📦", "Master Data"),
    "unit"        : ("📦", "Master Data"),
    "vendor"      : ("📦", "Master Data"),
    "opname"      : ("📦", "Master Data"),
    "inventory"   : ("🏭", "Inventory"),
    "stock"       : ("🏭", "Inventory"),
    "supplier"    : ("🏭", "Inventory"),
    "requisition" : ("🏭", "Inventory"),
    "production"  : ("⚗️",  "Production"),
    "recipe"      : ("⚗️",  "Production"),
    "marketing"   : ("📣", "Marketing"),
    "campaign"    : ("📣", "Marketing"),
    "discount"    : ("📣", "Marketing"),
    "loyalty"     : ("📣", "Marketing"),
    "report"      : ("📊", "Reports & Insights"),
    "insight"     : ("📊", "Reports & Insights"),
    "financial"   : ("📊", "Reports & Insights"),
    "trend"       : ("📊", "Reports & Insights"),
    "transfer"    : ("📊", "Reports & Insights"),
    "transaction" : ("📊", "Reports & Insights"),
    "setting"     : ("⚙️",  "Settings & Users"),
    "profile"     : ("⚙️",  "Settings & Users"),
    "user"        : ("⚙️",  "Settings & Users"),
    "about"       : ("⚙️",  "Settings & Users"),
    "contact"     : ("⚙️",  "Settings & Users"),
    "pricing"     : ("⚙️",  "Settings & Users"),
    "search"      : ("⚙️",  "Settings & Users"),
    "business"    : ("⚙️",  "Settings & Users"),
    "auth"        : ("🔐", "Authentication"),
    "login"       : ("🔐", "Authentication"),
    "logout"      : ("🔐", "Authentication"),
    "api"         : ("🔌", "Internal API"),
}


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def find_file(root: Path, *relative_parts) -> Path | None:
    p = root / Path(*relative_parts)
    return p if p.exists() else None


# ══════════════════════════════════════════════════════════════════
# SECTION 1: ARSITEKTUR
# ══════════════════════════════════════════════════════════════════

def build_dir_tree(path: Path, root: Path, prefix: str = "", max_depth: int = 4, depth: int = 0) -> list[str]:
    """Rekursif build tree folder seperti `tree` command."""
    if depth > max_depth:
        return []

    SKIP = {"__pycache__", ".git", ".venv", "venv", "node_modules",
            "staticfiles", "media", ".idea", ".vscode", "migrations",
            "*.pyc"}

    lines = []
    try:
        entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        return []

    entries = [e for e in entries if e.name not in SKIP and not e.name.endswith(".pyc")]
    # Jika migrations, tunjukkan hanya sebagai placeholder
    entries_filtered = []
    for e in entries:
        if e.is_dir() and e.name == "migrations":
            entries_filtered.append(("migrations_placeholder", e))
        else:
            entries_filtered.append(("normal", e))

    for i, (kind, entry) in enumerate(entries_filtered):
        is_last   = i == len(entries_filtered) - 1
        connector = "└───" if is_last else "├───"
        child_pfx = prefix + ("    " if is_last else "│   ")

        if kind == "migrations_placeholder":
            lines.append(f"{prefix}{connector}migrations/            ← database migrations")
            continue

        # Annotate file tertentu
        annotation = ""
        name = entry.name
        ann_map = {
            "settings.py"  : "← database, middleware, templates",
            "urls.py"       : "← router utama",
            "wsgi.py"       : "",
            "asgi.py"       : "",
            "models.py"     : "← models",
            "middleware.py" : "← EnsureUserProfileMiddleware",
            "context_processors.py": "← app_version di semua template",
            "signals.py"    : "← auto stock deduction",
            "admin.py"      : "← Django admin registrations",
            "apps.py"       : "← AppConfig + signals ready()",
            "__init__.py"   : "",
        }
        if name in ann_map and ann_map[name]:
            annotation = f"  {ann_map[name]}"

        if entry.is_dir():
            lines.append(f"{prefix}{connector}{name}/{annotation}")
            if depth < max_depth:
                lines.extend(build_dir_tree(entry, root, child_pfx, max_depth, depth + 1))
        else:
            lines.append(f"{prefix}{connector}{name}{annotation}")

    return lines


def section_architecture(root: Path) -> str:
    lines = ["## 1. Arsitektur Project\n", "```"]
    rel = root.name + "/"
    lines.append(rel)
    lines.extend(build_dir_tree(root, root, max_depth=3))
    lines.append("```\n")

    # URL pattern explanation
    urls_path = find_file(root, PROJECT_NAME, "urls.py")
    if urls_path:
        content = safe_read(urls_path)
        lazy_match = re.search(r'def lazy_view\(.*?\).*?(?=\ndef |\Z)', content, re.DOTALL)
        if lazy_match or "lazy_view" in content:
            lines.append("### Pola URL → View\n")
            lines.append("Semua URL menggunakan `lazy_view()` untuk menghindari circular import:\n")
            lines.append("```python")
            lines.append(f"# {PROJECT_NAME}/urls.py")
            lines.append(f"path('/', lazy_view('{APP_NAME}.sales.views.dashboard_view'), name='dashboard')")
            lines.append(f"#          └── {APP_NAME}/sales/views.py (stub)")
            lines.append(f"#                └── from {APP_NAME}.views import dashboard_view")
            lines.append(f"#                       └── {APP_NAME}/views/dashboard_views.py")
            lines.append("```\n")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# SECTION 2: DATABASE & MODEL
# ══════════════════════════════════════════════════════════════════

FIELD_TYPE_MAP = {
    "CharField"         : "CharField",
    "TextField"         : "TextField",
    "IntegerField"      : "IntegerField",
    "DecimalField"      : "DecimalField",
    "BooleanField"      : "BooleanField",
    "DateTimeField"     : "DateTimeField",
    "DateField"         : "DateField",
    "EmailField"        : "EmailField",
    "ForeignKey"        : "ForeignKey",
    "OneToOneField"     : "OneToOneField",
    "ManyToManyField"   : "ManyToManyField",
    "ImageField"        : "ImageField",
    "FileField"         : "FileField",
    "FloatField"        : "FloatField",
    "PositiveIntegerField": "PositiveIntegerField",
    "SlugField"         : "SlugField",
    "JSONField"         : "JSONField",
    "UUIDField"         : "UUIDField",
}


def parse_models(models_path: Path) -> list[dict]:
    """Parse models.py menggunakan AST. Return list of model dicts."""
    source = safe_read(models_path)
    if not source:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    models = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Hanya class yang inherit dari Model atau models.Model
        bases = [
            ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", getattr(b, "attr", ""))
            for b in node.bases
        ]
        is_model = any(
            "Model" in b for b in bases
        )
        if not is_model:
            continue

        model = {
            "name"    : node.name,
            "fields"  : [],
            "meta"    : {},
            "docstring": ast.get_docstring(node) or "",
        }

        for item in node.body:
            # Field assignments: name = models.CharField(...)
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if not isinstance(target, ast.Name):
                        continue
                    field_name = target.id
                    if field_name.startswith("_"):
                        continue

                    # Get field type
                    call = item.value
                    if not isinstance(call, ast.Call):
                        continue

                    func = call.func
                    if isinstance(func, ast.Attribute):
                        field_type = func.attr
                    elif isinstance(func, ast.Name):
                        field_type = func.id
                    else:
                        continue

                    if field_type not in FIELD_TYPE_MAP:
                        continue

                    model["fields"].append({
                        "name" : field_name,
                        "type" : field_type,
                    })

            # Meta class
            elif isinstance(item, ast.ClassDef) and item.name == "Meta":
                for meta_item in item.body:
                    if isinstance(meta_item, ast.Assign):
                        for t in meta_item.targets:
                            if isinstance(t, ast.Name) and t.id == "db_table":
                                if isinstance(meta_item.value, ast.Constant):
                                    model["meta"]["db_table"] = meta_item.value.value

        if model["fields"] or model["name"]:
            models.append(model)

    return models


def section_models(root: Path) -> str:
    models_path = find_file(root, APP_NAME, "models.py")
    if not models_path:
        return "## 2. Database & Model\n\n*models.py tidak ditemukan.*\n"

    models = parse_models(models_path)
    if not models:
        return "## 2. Database & Model\n\n*Tidak ada model yang ditemukan.*\n"

    lines = [f"## 2. Database & Model\n"]
    lines.append(f"**Database**: PostgreSQL  ")
    lines.append(f"**App label**: `{APP_NAME}`  ")
    lines.append(f"**Total model**: {len(models)}\n")

    # Summary table
    lines.append("| Model | Tabel PostgreSQL | Keterangan |")
    lines.append("|-------|-----------------|------------|")

    shared_tables = {"production_recipe_categories", "production_recipes", "production_recipe_ingredients"}

    for m in models:
        db_table = m["meta"].get("db_table", f"{APP_NAME}_{m['name'].lower()}s")
        shared_note = " ⚠️ *shared dengan core*" if db_table in shared_tables else ""
        lines.append(f"| `{m['name']}` | `{db_table}` | {shared_note} |")

    lines.append("")

    # Detail per model (hanya model dengan banyak field atau penting)
    key_models = {"UserProfile", "Product", "ProductVariant", "Stock", "Order",
                  "Customer", "Recipe", "Vendor", "Location", "OrderItem"}

    lines.append("### Detail Field Model Utama\n")

    for m in models:
        if m["name"] not in key_models:
            continue
        if not m["fields"]:
            continue

        db_table = m["meta"].get("db_table", f"{APP_NAME}_{m['name'].lower()}s")
        lines.append(f"#### `{m['name']}` → tabel `{db_table}`")
        lines.append("| Field | Tipe |")
        lines.append("|-------|------|")

        shown = 0
        for f in m["fields"]:
            lines.append(f"| `{f['name']}` | `{f['type']}` |")
            shown += 1

        remaining = len(m["fields"]) - shown
        if remaining > 0:
            lines.append(f"| *...{remaining} field lainnya* | |")
        lines.append("")

    # Shared tables warning
    lines.append("> ⚠️ **Tabel shared** (`production_*`) namanya sama antara `core` dan `lumra`.")
    lines.append("> Saat migrate gunakan `--fake-initial` agar tidak error DuplicateTable.\n")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# SECTION 3: URL → VIEW → TEMPLATE
# ══════════════════════════════════════════════════════════════════

def categorize_url(url_pattern: str, view_name: str) -> tuple[str, str]:
    """Return (emoji, section_label) berdasarkan URL atau view name."""
    text = (url_pattern + " " + view_name).lower()
    for keyword, (emoji, label) in URL_SECTION_MAP.items():
        if keyword in text:
            return emoji, label
    return "🌐", "Lainnya"


def parse_url_patterns(urls_path: Path) -> list[dict]:
    """
    Parse urls.py dan extract semua path() / re_path() definitions.
    Return list of { url, method, view, name, requires_auth }
    """
    source = safe_read(urls_path)
    if not source:
        return []

    results = []

    # Match: path('url/', view_func, name='name')
    # Juga handle lazy_view(...) patterns
    path_pattern = re.compile(
        r"""(?:re_)?path\s*\(\s*
            r?['"]([^'"]*)['"]\s*,\s*   # URL pattern
            ([^\),]+)                    # view function / lazy_view(...)
            (?:,\s*name\s*=\s*['"]([^'"]+)['"])?  # optional name=
        """,
        re.VERBOSE | re.DOTALL
    )

    for m in path_pattern.finditer(source):
        url_str  = m.group(1).strip()
        view_str = m.group(2).strip()
        name_str = m.group(3) or ""

        # Extract view function name dari lazy_view('module.path.view_name')
        lazy_match = re.search(r"lazy_view\s*\(\s*['\"]([^'\"]+)['\"]", view_str)
        if lazy_match:
            full_path = lazy_match.group(1)
            view_name = full_path.split(".")[-1]
        else:
            # Direct reference: views.func_name atau func_name
            view_name = view_str.strip().split(".")[-1].split(",")[0].strip()
            # Bersihkan dari karakter noise
            view_name = re.sub(r'[^a-zA-Z0-9_]', '', view_name)

        if not view_name or not url_str:
            continue

        # Tentukan method (heuristic dari URL pattern dan nama)
        method = "GET"
        if any(kw in view_name.lower() for kw in ["create", "add", "form", "submit", "save"]):
            method = "GET, POST"
        elif any(kw in view_name.lower() for kw in ["update", "edit"]):
            method = "GET, POST"
        elif any(kw in view_name.lower() for kw in ["delete"]):
            method = "GET"

        # Cek login_required (heuristic dari nama view atau URL)
        requires_auth = "login" in view_name.lower() or "login_required" in source[:source.find(view_name) + 200]

        # Bersihkan URL — tambah leading slash
        clean_url = "/" + url_str.lstrip("^").rstrip("$")

        results.append({
            "url"         : clean_url,
            "method"      : method,
            "view"        : view_name,
            "name"        : name_str,
            "requires_auth": requires_auth,
        })

    return results


def find_template_for_view(view_name: str, views_dir: Path, templates_dir: Path) -> str:
    """
    Cari nama template yang dipakai oleh sebuah view function.
    Scan semua file di views/ dan cari render(..., 'template_name')
    """
    if not views_dir.exists():
        return "—"

    # Baca semua file view
    view_files = list(views_dir.glob("*.py")) if views_dir.is_dir() else [views_dir]

    for vf in view_files:
        content = safe_read(vf)
        if view_name not in content:
            continue

        # Cari fungsi definisi
        func_start = content.find(f"def {view_name}")
        if func_start == -1:
            continue

        # Ambil 60 baris setelah definisi fungsi
        snippet = content[func_start:func_start + 3000]

        # Pattern: render(request, 'template.html') atau render(request, "template.html")
        render_match = re.search(
            r'render\s*\(\s*\w+\s*,\s*[\'"]([^\'"]+\.html)[\'"]',
            snippet
        )
        if render_match:
            tmpl = render_match.group(1)
            # Ambil nama file saja, bukan full path
            return Path(tmpl).name

        # Pattern: template_name = 'template.html'
        tmpl_match = re.search(
            r'template_name\s*=\s*[\'"]([^\'"]+\.html)[\'"]',
            snippet
        )
        if tmpl_match:
            return Path(tmpl_match.group(1)).name

    return "—"


def section_urls(root: Path) -> str:
    urls_path = find_file(root, PROJECT_NAME, "urls.py")
    if not urls_path:
        # Coba cari di app
        urls_path = find_file(root, APP_NAME, "urls.py")
    if not urls_path:
        return "## 3. URL → View → Template\n\n*urls.py tidak ditemukan.*\n"

    patterns  = parse_url_patterns(urls_path)
    views_dir = root / APP_NAME / "views"
    if not views_dir.exists():
        views_dir = root / APP_NAME / "views.py"

    templates_dir = root / APP_NAME / "templates"

    # Cache template lookups
    template_cache: dict[str, str] = {}

    def get_template(view_name: str) -> str:
        if view_name not in template_cache:
            template_cache[view_name] = find_template_for_view(view_name, views_dir, templates_dir)
        return template_cache[view_name]

    # Group by section
    sections: dict[str, list[dict]] = defaultdict(list)
    section_order: dict[str, tuple] = {}

    for p in patterns:
        emoji, label = categorize_url(p["url"], p["view"])
        key = label
        sections[key].append(p)
        section_order[key] = (emoji, label)

    # Sort sections by a defined order
    ORDER = [
        "Sales & POS", "Master Data", "Inventory", "Production",
        "Marketing", "Reports & Insights", "Settings & Users",
        "Authentication", "Internal API", "Lainnya"
    ]

    lines = [
        f"## 3. URL → View → Template\n",
        f"Total: **{len(patterns)} URL** aktif\n",
    ]

    for section_label in ORDER:
        if section_label not in sections:
            continue

        emoji, _ = section_order.get(section_label, ("🌐", section_label))
        lines.append(f"### {emoji} {section_label}\n")
        lines.append("| URL | Method | View Function | Template | Auth |")
        lines.append("|-----|--------|---------------|----------|------|")

        for p in sections[section_label]:
            tmpl      = get_template(p["view"])
            auth_icon = "🔒" if p["requires_auth"] else "🌐"
            method    = p["method"]
            lines.append(
                f"| `{p['url']}` | {method} | `{p['view']}` | `{tmpl}` | {auth_icon} |"
            )

        lines.append("")

    lines.append("> 🔒 = Login required &nbsp;&nbsp; 🌐 = Public\n")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# SECTION 4: SETTINGS
# ══════════════════════════════════════════════════════════════════

def section_settings(root: Path) -> str:
    settings_path = find_file(root, PROJECT_NAME, "settings.py")
    if not settings_path:
        return ""

    content = safe_read(settings_path)

    lines = ["## 4. Settings & Konfigurasi\n"]
    lines.append(f"File: `{PROJECT_NAME}/settings.py`\n")

    # Database
    db_match = re.search(r"DATABASES\s*=\s*(\{.*?\})\s*\n\n", content, re.DOTALL)
    if db_match:
        lines.append("### Database")
        lines.append("```python")
        lines.append(db_match.group(0).strip())
        lines.append("```\n")

    # Middleware
    mw_match = re.search(r"MIDDLEWARE\s*=\s*(\[.*?\])", content, re.DOTALL)
    if mw_match:
        lines.append("### Middleware (urutan penting!)")
        lines.append("```python")
        lines.append(mw_match.group(0).strip())
        lines.append("```\n")

    # Installed apps
    apps_match = re.search(r"INSTALLED_APPS\s*=\s*(\[.*?\])", content, re.DOTALL)
    if apps_match:
        lines.append("### INSTALLED_APPS")
        lines.append("```python")
        lines.append(apps_match.group(0).strip())
        lines.append("```\n")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# MAIN ASSEMBLER
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
# SECTION 5: TEMPLATE AUDIT
# ══════════════════════════════════════════════════════════════════

def audit_template(path):
    source = safe_read(path)
    if not source:
        return {}
    result = {
        "rel_path"      : str(path),
        "extends"       : None,
        "includes"      : [],
        "inline_css"    : False,
        "inline_kpi"    : False,
        "heavy_classes" : [],
        "component_type": "page",
    }
    # extends
    pat_ext = re.compile(r"{%-?\s*extends\s+['\"]([^'\"]+)['\"]\s*-?%}")
    m = pat_ext.search(source)
    if m:
        result["extends"] = m.group(1)
    # includes
    pat_inc = re.compile(r"{%-?\s*include\s+['\"]([^'\"]+)['\"]\s*-?%}")
    for m in pat_inc.finditer(source):
        result["includes"].append(m.group(1))
    # inline style
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", source, re.DOTALL | re.IGNORECASE)
    if style_blocks:
        result["inline_css"] = True
        for block in style_blocks:
            classes = re.findall(r"\.([-\w]+)\s*\{", block)
            result["heavy_classes"].extend(classes)
    # kpi inline detection
    kpi_signals = ["kpi-glass", "kpi_glass", "kpi-icon", "data-kpi-value",
                   "today's sales", "transactions", "low stock", "best_seller"]
    src_lower = source.lower()
    for sig in kpi_signals:
        if sig in src_lower:
            result["inline_kpi"] = True
            break
    # component type
    has_block = "{% block" in source or "{%block" in source
    if not result["extends"] and has_block:
        result["component_type"] = "base"
    elif result["extends"] and "{% block content" in source:
        result["component_type"] = "page"
    elif not result["extends"] and not has_block:
        result["component_type"] = "partial"
    else:
        result["component_type"] = "standalone"
    return result


def section_template_audit(root):
    templates_dir = root / APP_NAME / "templates"
    if not templates_dir.exists():
        return "## 5. Template Audit\n\n*Folder templates tidak ditemukan.*\n"
    html_files = sorted(templates_dir.rglob("*.html"))
    if not html_files:
        return "## 5. Template Audit\n\n*Tidak ada file HTML.*\n"
    audits = []
    for f in html_files:
        a = audit_template(f)
        if a:
            a["rel_path"] = str(f.relative_to(templates_dir))
            audits.append(a)
    inline_kpi   = [a for a in audits if a["inline_kpi"]]
    has_css      = [a for a in audits if a["inline_css"]]
    heavy_inline = [a for a in audits if len(a["heavy_classes"]) >= 3]
    uses_inc     = [a for a in audits if a["includes"]]
    standalones  = [a for a in audits if a["component_type"] == "standalone"]
    lines = [
        "## 5. Template Audit\n",
        f"**Total template**: {len(audits)}  ",
        f"**Punya inline CSS**: {len(has_css)}  ",
        f"**Punya KPI/card inline** (bukan via include): {len(inline_kpi)}  ",
        f"**Pakai include**: {len(uses_inc)}  ",
        f"**Standalone** (tidak extend apapun): {len(standalones)}\n",
    ]
    if inline_kpi:
        lines.append("### \u26a0\ufe0f Template dengan KPI/Card Inline (perlu refactor)\n")
        lines.append("> Template ini render KPI card **langsung** tanpa include.")
        lines.append("> Jika ingin mengubah desain card, perlu edit setiap file ini satu per satu.\n")
        lines.append("| Template | Extends | Inline Classes |")
        lines.append("|----------|---------|----------------|")
        for a in inline_kpi:
            ext = f"`{a['extends']}`" if a["extends"] else "\u2014"
            cls = ", ".join(f"`{c}`" for c in a["heavy_classes"][:5])
            if len(a["heavy_classes"]) > 5:
                cls += f" +{len(a['heavy_classes'])-5} lainnya"
            lines.append(f"| `{a['rel_path']}` | {ext} | {cls} |")
        lines.append("")
    if uses_inc:
        lines.append("### \u2705 Template yang Sudah Pakai include\n")
        lines.append("| Template | Include |")
        lines.append("|----------|---------|")
        for a in uses_inc:
            incl = ", ".join(f"`{i}`" for i in a["includes"][:3])
            if len(a["includes"]) > 3:
                incl += f" +{len(a['includes'])-3}"
            lines.append(f"| `{a['rel_path']}` | {incl} |")
        lines.append("")
    if heavy_inline:
        lines.append("### \U0001f536 Template dengan Banyak CSS Inline\n")
        lines.append("| Template | Jumlah Class | Classes |")
        lines.append("|----------|-------------|----------|")
        for a in sorted(heavy_inline, key=lambda x: -len(x["heavy_classes"])):
            cls = ", ".join(f"`{c}`" for c in a["heavy_classes"][:6])
            lines.append(f"| `{a['rel_path']}` | {len(a['heavy_classes'])} | {cls} |")
        lines.append("")
    if standalones:
        lines.append("### \U0001f50d Standalone Templates (tidak extend base)\n")
        lines.append("| Template |")
        lines.append("|----------|")
        for a in standalones:
            lines.append(f"| `{a['rel_path']}` |")
        lines.append("")
    return "\n".join(lines)


def build_toc(sections: list[str]) -> str:
    toc = ["## 📋 Daftar Isi\n"]
    for i, s in enumerate(sections, 1):
        slug = s.lower().replace(" ", "-").replace("&", "").replace("→", "").replace("/", "").replace("__", "-")
        slug = re.sub(r"-+", "-", slug).strip("-")
        toc.append(f"{i}. [{s}](#{slug})")
    return "\n".join(toc) + "\n"


def generate(root: Path, output: Path, sections_filter: list[str] | None = None) -> None:
    print(f"\n  Lumra Doc Generator")
    print(f"  Root   : {root}")
    print(f"  Output : {output}\n")

    timestamp = datetime.now().strftime("%d %B %Y %H:%M")

    parts = []

    # Header
    parts.append(f"# 📖 Lumra ERP — Buku Dokumentasi Teknis\n")
    parts.append(f"> Dibuat otomatis dari source code pada {timestamp}\n")
    parts.append("---\n")

    # Sections
    enabled = sections_filter or ["arch", "models", "urls", "settings", "templates"]

    section_titles = []
    section_contents = []

    if "arch" in enabled:
        print("  [1/4] Scanning arsitektur project...")
        content = section_architecture(root)
        section_titles.append("Arsitektur Project")
        section_contents.append(content)

    if "models" in enabled:
        print("  [2/4] Parsing models.py...")
        content = section_models(root)
        section_titles.append("Database & Model")
        section_contents.append(content)

    if "urls" in enabled:
        print("  [3/4] Parsing urls.py + views/...")
        content = section_urls(root)
        section_titles.append("URL → View → Template")
        section_contents.append(content)

    if "settings" in enabled:
        print("  [4/5] Parsing settings.py...")
        content = section_settings(root)
        if content:
            section_titles.append("Settings & Konfigurasi")
            section_contents.append(content)

    if "templates" in enabled:
        print("  [5/5] Auditing templates (inline vs include)...")
        content = section_template_audit(root)
        section_titles.append("Template Audit")
        section_contents.append(content)

    # Assemble
    parts.append(build_toc(section_titles))
    parts.append("---\n")
    for c in section_contents:
        parts.append(c)
        parts.append("\n---\n")

    parts.append(f"\n*Dokumentasi ini dibuat otomatis dari source code {APP_NAME} ERP.*\n")

    # Write
    final = "\n".join(parts)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(final, encoding="utf-8")

    lines   = final.count("\n")
    urls_ct = final.count("| `")
    model_ct = final.count("#### `")

    print(f"\n  ✅ Selesai!")
    print(f"     {lines:,} baris  ·  {urls_ct} URL  ·  {model_ct} model detail")
    print(f"     → {output}\n")


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description="Lumra Doc Generator — generate technical docs dari source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--root",     type=Path, default=DEFAULT_ROOT,
                   help=f"Root folder project (default: {DEFAULT_ROOT})")
    p.add_argument("--output",   type=Path, default=DEFAULT_OUTPUT,
                   help=f"Output Markdown (default: {DEFAULT_OUTPUT})")
    p.add_argument("--sections", type=str, default=None,
                   help="Comma-separated: arch,models,urls,settings,templates (default: semua)")
    args = p.parse_args()

    sections = [s.strip() for s in args.sections.split(",")] if args.sections else None

    if not args.root.exists():
        print(f"  ERROR: Root folder tidak ditemukan: {args.root}")
        sys.exit(1)

    generate(args.root, args.output, sections)


if __name__ == "__main__":
    main()