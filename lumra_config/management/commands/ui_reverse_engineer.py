#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║          UI REVERSE ENGINEER — Wireframe Generator                   ║
║   Mengupas lapisan visual HTML → Wireframe / Sketsa Struktural       ║
║                                                                      ║
║  Output:                                                             ║
║    1. wireframe_*.html  — HTML wireframe (grayscale, no styling)     ║
║    2. wireframe_*.png   — Visual wireframe image (Pillow)            ║
║    3. structure_*.json  — JSON struktur komponen terdeteksi          ║
║    4. audit_report.md   — Laporan audit UI/UX lengkap                ║
║    5. summary_index.html— Index semua file yang diproses             ║
╚══════════════════════════════════════════════════════════════════════╝

Cara pakai:
    python3 ui_reverse_engineer.py                        # proses semua *.html di folder saat ini
    python3 ui_reverse_engineer.py file.html              # proses satu file
    python3 ui_reverse_engineer.py folder/               # proses semua html dalam folder
    python3 ui_reverse_engineer.py a.html b.html          # proses beberapa file
    python3 ui_reverse_engineer.py --no-image             # skip generate PNG
    python3 ui_reverse_engineer.py --output ./hasil/      # tentukan folder output
"""

import re
import os
import sys
import json
import copy
import pathlib
import argparse
import textwrap
from datetime import datetime
from collections import defaultdict

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# ── Pillow opsional (untuk PNG wireframe) ─────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_OK = True
except ImportError:
    PILLOW_OK = False
    print("[WARN] Pillow tidak tersedia. PNG wireframe dilewati. Install: pip install Pillow")


# ══════════════════════════════════════════════════════════════════════
#  KONFIGURASI
# ══════════════════════════════════════════════════════════════════════

# Tag HTML yang selalu dihapus (tidak relevan untuk wireframe)
REMOVE_TAGS = {
    "script", "style", "link", "meta", "noscript",
    "svg", "path", "polygon", "circle", "rect",
    "iframe", "video", "audio", "canvas",
}

# Tag yang dipertahankan strukturnya tapi dikosongkan isinya
SKELETON_TAGS = {
    "img", "picture", "figure",
}

# Mapping elemen semantik → label wireframe
SEMANTIC_LABELS = {
    "nav":     "[ NAVIGATION BAR ]",
    "header":  "[ HEADER ]",
    "footer":  "[ FOOTER ]",
    "main":    "[ MAIN CONTENT ]",
    "aside":   "[ SIDEBAR ]",
    "section": "[ SECTION ]",
    "article": "[ ARTICLE ]",
    "form":    "[ FORM ]",
    "table":   "[ TABLE ]",
    "ul":      "[ LIST ]",
    "ol":      "[ ORDERED LIST ]",
    "figure":  "[ IMAGE PLACEHOLDER ]",
    "dialog":  "[ MODAL / DIALOG ]",
    "details": "[ ACCORDION ]",
}

# Pola CSS class → jenis komponen (urutan penting: spesifik dulu)
CLASS_COMPONENT_MAP = [
    # Layout
    (r"\b(navbar|nav-bar|topbar|top-bar)\b",         "navbar",       "NAV BAR"),
    (r"\b(sidebar|side-bar|sidenav)\b",               "sidebar",      "SIDEBAR"),
    (r"\b(footer|bottom-bar)\b",                      "footer",       "FOOTER"),
    (r"\b(hero|banner|jumbotron|masthead)\b",         "hero",         "HERO / BANNER"),
    (r"\b(modal|dialog|overlay|drawer|offcanvas)\b",  "modal",        "MODAL / DRAWER"),

    # Cards & Panels
    (r"\b(glass-card|glass-panel|panel|card)\b",      "card",         "CARD"),
    (r"\b(metric-card|stat-card|kpi)\b",              "metric",       "METRIC CARD"),
    (r"\b(alert|toast|notification|badge-alert)\b",   "alert",        "ALERT / NOTIFICATION"),

    # Forms & Inputs
    (r"\b(form-input|form-control|input-group)\b",    "input",        "INPUT FIELD"),
    (r"\b(ing-row|ing-table|ingredient-row)\b",       "table-row",    "TABLE ROW (ingredient)"),
    (r"\b(search|searchbar|search-bar)\b",            "search",       "SEARCH BAR"),

    # Buttons
    (r"\b(btn-primary|control-btn|btn-start)\b",      "button-primary","BUTTON (Primary)"),
    (r"\b(btn-stop|btn-danger|btn-delete)\b",         "button-danger", "BUTTON (Danger)"),
    (r"\b(filter-btn|filter-chip|tab)\b",             "filter",       "FILTER / TAB"),
    (r"\b(ver-tab|trial-tab)\b",                      "tab",          "TAB"),

    # Data Display
    (r"\b(progress-circle|donut|gauge)\b",            "gauge",        "PROGRESS GAUGE"),
    (r"\b(progress-track|progress-bar|prob-bar)\b",   "progressbar",  "PROGRESS BAR"),
    (r"\b(cost-bar|cost-seg)\b",                      "chart-bar",    "COST BAR CHART"),
    (r"\b(calendar|calendar-grid|day-cell)\b",        "calendar",     "CALENDAR"),
    (r"\b(timeline|tl-item|tl-track)\b",              "timeline",     "TIMELINE"),
    (r"\b(compare-col|compare-grid)\b",               "compare",      "COMPARISON PANEL"),
    (r"\b(flavor-wheel|flavor-dim)\b",                "flavor",       "FLAVOR CHART"),

    # Navigation
    (r"\b(breadcrumb|bread-crumb)\b",                 "breadcrumb",   "BREADCRUMB"),
    (r"\b(pagination|pager)\b",                       "pagination",   "PAGINATION"),

    # Status
    (r"\b(badge|tag|pill|chip|bom-tag|status-badge)\b","badge",       "BADGE / STATUS"),
    (r"\b(promote-banner|promo-banner)\b",            "banner",       "PROMOTE BANNER"),
    (r"\b(empty-state|no-data|no-result)\b",          "empty",        "EMPTY STATE"),
]

# Tailwind class untuk mendeteksi scroll nesting
OVERFLOW_CLASSES = {
    "overflow-auto", "overflow-scroll", "overflow-x-auto", "overflow-x-scroll",
    "overflow-y-auto", "overflow-y-scroll",
}

# CSS properties inline untuk scroll detection
OVERFLOW_CSS_PATTERN = re.compile(
    r"overflow(?:-x|-y)?:\s*(auto|scroll)", re.IGNORECASE
)

# Warna wireframe
WF_COLORS = {
    "bg":          "#F8F8F8",
    "border":      "#CCCCCC",
    "border_dark": "#888888",
    "text":        "#333333",
    "text_light":  "#888888",
    "label_bg":    "#E8E8E8",
    "label_text":  "#444444",
    "input_bg":    "#FFFFFF",
    "button_bg":   "#DDDDDD",
    "button_text": "#333333",
    "card_bg":     "#FFFFFF",
    "image_bg":    "#E0E0E0",
    "image_text":  "#888888",
    "scroll_bg":   "#FFF3CD",   # kuning untuk scroll nesting warning
    "scroll_bdr":  "#FFC107",
    "nav_bg":      "#2C2C2C",
    "nav_text":    "#FFFFFF",
    "highlight_bg":"#E3F2FD",
    "highlight_bdr":"#1565C0",
}


# ══════════════════════════════════════════════════════════════════════
#  UTILITAS
# ══════════════════════════════════════════════════════════════════════

def slugify(text: str) -> str:
    """Buat slug aman untuk nama file."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "_", text).strip("_") or "file"


def get_classes(tag: Tag) -> list[str]:
    """Ambil list class dari tag."""
    if not isinstance(tag, Tag):
        return []
    cls = tag.get("class", [])
    return cls if isinstance(cls, list) else cls.split()


def classes_str(tag: Tag) -> str:
    return " ".join(get_classes(tag))


def get_text_preview(tag: Tag, max_len: int = 60) -> str:
    """Ambil preview teks dari tag, bersihkan whitespace."""
    if not isinstance(tag, Tag):
        return ""
    text = tag.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[:max_len].rstrip() + "…"
    return text


def detect_component(tag: Tag) -> tuple[str, str] | None:
    """
    Deteksi tipe komponen dari class CSS.
    Return (component_type, label) atau None.
    """
    cls = classes_str(tag)
    if not cls:
        return None
    for pattern, comp_type, label in CLASS_COMPONENT_MAP:
        if re.search(pattern, cls, re.IGNORECASE):
            return (comp_type, label)
    return None


def has_scroll(tag: Tag) -> bool:
    """Cek apakah element memiliki scroll (class atau inline style)."""
    cls_set = set(get_classes(tag))
    if cls_set & OVERFLOW_CLASSES:
        return True
    style = tag.get("style", "")
    if style and OVERFLOW_CSS_PATTERN.search(style):
        return True
    return False


def get_grid_info(tag: Tag) -> str | None:
    """Deteksi grid/flex layout dan kolom dari Tailwind classes."""
    cls = classes_str(tag)
    # Grid columns
    m = re.search(r"grid-cols-(\d+|none|subgrid)", cls)
    if m:
        return f"GRID {m.group(1)} cols"
    # Flex
    if re.search(r"\bflex\b", cls):
        direction = "row"
        if re.search(r"\bflex-col\b", cls):
            direction = "column"
        return f"FLEX ({direction})"
    # lg/sm responsive grid
    m2 = re.search(r"lg:grid-cols-(\d+)", cls)
    if m2:
        return f"GRID lg:{m2.group(1)} cols"
    return None


def is_button(tag: Tag) -> bool:
    """Apakah tag ini adalah tombol (button, a[btn], input[submit])."""
    if tag.name == "button":
        return True
    if tag.name == "input" and tag.get("type") in ("submit", "button", "reset"):
        return True
    if tag.name == "a":
        cls = classes_str(tag)
        if re.search(r"\bbtn\b|button|control-btn|filter-btn", cls, re.I):
            return True
    return False


def is_input(tag: Tag) -> bool:
    """Apakah tag ini adalah field input."""
    if tag.name in ("input", "textarea", "select"):
        return True
    return False


def is_image(tag: Tag) -> bool:
    return tag.name in ("img", "picture", "figure", "video")


# ══════════════════════════════════════════════════════════════════════
#  STEP 1: PARSE & ANALISIS STRUKTUR
# ══════════════════════════════════════════════════════════════════════

class UIStructureAnalyzer:
    """
    Menganalisis HTML dan mengekstrak struktur komponen, scroll nesting,
    layout grid, dan metadata UI.
    """

    def __init__(self, html: str, filename: str = ""):
        self.filename = filename
        self.soup = BeautifulSoup(html, "lxml")
        self.components: list[dict] = []
        self.scroll_nestings: list[dict] = []
        self.layout_tree: list[dict] = []
        self.issues: list[dict] = []
        self._scroll_stack: list[Tag] = []
        self._component_counter: dict[str, int] = defaultdict(int)

    def analyze(self) -> dict:
        """Jalankan semua analisis dan return hasil."""
        # Bersihkan komentar Django template dan script
        self._clean_soup()

        # Analisis dari body
        body = self.soup.find("body") or self.soup
        self._walk(body, depth=0, parent_path="root")

        # Deteksi isu tambahan
        self._detect_issues()

        return {
            "filename":       self.filename,
            "title":          self._get_title(),
            "components":     self.components,
            "scroll_nestings":self.scroll_nestings,
            "layout_tree":    self.layout_tree,
            "issues":         self.issues,
            "stats":          self._build_stats(),
        }

    def _clean_soup(self):
        """Hapus elemen tidak relevan."""
        for tag in self.soup.find_all(True):
            if tag.name in REMOVE_TAGS:
                tag.decompose()
        for comment in self.soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

    def _get_title(self) -> str:
        t = self.soup.find("title")
        if t:
            return t.get_text(strip=True)
        h1 = self.soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return pathlib.Path(self.filename).stem if self.filename else "Untitled"

    def _walk(self, tag: Tag, depth: int, parent_path: str):
        """Rekursif walk DOM untuk analisis."""
        if not isinstance(tag, Tag):
            return

        path = f"{parent_path}/{tag.name}"
        node_info = self._analyze_node(tag, depth, path)

        if node_info:
            self.components.append(node_info)
            self.layout_tree.append({
                "depth": depth,
                "path": path,
                "type": node_info["type"],
                "label": node_info.get("label", tag.name),
                "text_preview": node_info.get("text_preview", ""),
            })

        # Deteksi scroll nesting
        if has_scroll(tag):
            if self._scroll_stack:
                self.scroll_nestings.append({
                    "outer": self._describe_tag(self._scroll_stack[-1]),
                    "inner": self._describe_tag(tag),
                    "depth": depth,
                    "path": path,
                })
            self._scroll_stack.append(tag)

        # Rekursi ke children
        for child in tag.children:
            if isinstance(child, Tag):
                self._walk(child, depth + 1, path)

        # Pop scroll stack
        if has_scroll(tag) and self._scroll_stack and self._scroll_stack[-1] is tag:
            self._scroll_stack.pop()

    def _analyze_node(self, tag: Tag, depth: int, path: str) -> dict | None:
        """Analisis satu node, return dict info atau None jika tidak relevan."""
        name = tag.name

        # Skip tag terlalu generik dan kecil
        if name in ("html", "body", "head"):
            return None

        # Cek komponen dari class
        comp = detect_component(tag)
        if comp:
            comp_type, label = comp
            self._component_counter[comp_type] += 1
            return {
                "type":         comp_type,
                "tag":          name,
                "label":        label,
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": get_text_preview(tag, 80),
                "has_scroll":   has_scroll(tag),
                "grid_info":    get_grid_info(tag),
                "is_interactive": self._is_interactive(tag),
                "children_count": len([c for c in tag.children if isinstance(c, Tag)]),
                "has_form_fields": bool(tag.find(["input", "select", "textarea"])),
                "id":           tag.get("id", ""),
                "x_data":       tag.get("x-data", ""),
            }

        # Cek tag semantik
        if name in SEMANTIC_LABELS:
            self._component_counter[name] += 1
            return {
                "type":         name,
                "tag":          name,
                "label":        SEMANTIC_LABELS[name],
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": get_text_preview(tag, 80),
                "has_scroll":   has_scroll(tag),
                "grid_info":    get_grid_info(tag),
                "is_interactive": self._is_interactive(tag),
                "children_count": len([c for c in tag.children if isinstance(c, Tag)]),
                "has_form_fields": bool(tag.find(["input", "select", "textarea"])),
                "id":           tag.get("id", ""),
                "x_data":       tag.get("x-data", ""),
            }

        # Heading
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return {
                "type":         "heading",
                "tag":          name,
                "label":        f"HEADING ({name.upper()})",
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": get_text_preview(tag, 100),
                "has_scroll":   False,
                "grid_info":    None,
                "is_interactive": False,
                "children_count": 0,
                "has_form_fields": False,
                "id":           tag.get("id", ""),
                "x_data":       "",
            }

        # Button
        if is_button(tag):
            self._component_counter["button"] += 1
            return {
                "type":         "button",
                "tag":          name,
                "label":        f"BUTTON: {get_text_preview(tag, 40) or '[icon]'}",
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": get_text_preview(tag, 60),
                "has_scroll":   False,
                "grid_info":    None,
                "is_interactive": True,
                "children_count": 0,
                "has_form_fields": False,
                "id":           tag.get("id", ""),
                "x_data":       "",
            }

        # Input fields
        if is_input(tag):
            self._component_counter["input"] += 1
            input_type = tag.get("type", "text") if name == "input" else name
            placeholder = tag.get("placeholder", "")
            label_text = tag.get("x-model", tag.get("name", ""))
            return {
                "type":         "input",
                "tag":          name,
                "label":        f"INPUT [{input_type}] {placeholder or label_text}",
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": placeholder or label_text,
                "has_scroll":   False,
                "grid_info":    None,
                "is_interactive": True,
                "children_count": 0,
                "has_form_fields": True,
                "id":           tag.get("id", ""),
                "x_data":       "",
            }

        # Image
        if is_image(tag):
            alt = tag.get("alt", "") if name == "img" else ""
            return {
                "type":         "image",
                "tag":          name,
                "label":        f"IMAGE {('[' + alt + ']') if alt else '[no alt]'}",
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": alt,
                "has_scroll":   False,
                "grid_info":    None,
                "is_interactive": False,
                "children_count": 0,
                "has_form_fields": False,
                "id":           tag.get("id", ""),
                "x_data":       "",
            }

        # Grid/flex container yang signifikan
        grid = get_grid_info(tag)
        if grid and depth <= 8:
            return {
                "type":         "layout",
                "tag":          name,
                "label":        f"LAYOUT CONTAINER [{grid}]",
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": "",
                "has_scroll":   has_scroll(tag),
                "grid_info":    grid,
                "is_interactive": False,
                "children_count": len([c for c in tag.children if isinstance(c, Tag)]),
                "has_form_fields": bool(tag.find(["input", "select", "textarea"])),
                "id":           tag.get("id", ""),
                "x_data":       tag.get("x-data", ""),
            }

        # Alpine component root
        if tag.get("x-data") and depth <= 6:
            return {
                "type":         "alpine-root",
                "tag":          name,
                "label":        f"ALPINE COMPONENT [{tag.get('x-data', '')[:40]}]",
                "depth":        depth,
                "path":         path,
                "classes":      classes_str(tag),
                "text_preview": get_text_preview(tag, 60),
                "has_scroll":   has_scroll(tag),
                "grid_info":    grid,
                "is_interactive": True,
                "children_count": len([c for c in tag.children if isinstance(c, Tag)]),
                "has_form_fields": bool(tag.find(["input", "select", "textarea"])),
                "id":           tag.get("id", ""),
                "x_data":       tag.get("x-data", ""),
            }

        return None

    def _is_interactive(self, tag: Tag) -> bool:
        """Cek apakah element memiliki event handler."""
        attrs = tag.attrs
        interactive_attrs = {"@click", "@submit", "@input", "@change", "x-on:click",
                             "onclick", "onsubmit", "href", "x-show", "x-if"}
        return bool(set(attrs.keys()) & interactive_attrs)

    def _describe_tag(self, tag: Tag) -> str:
        """Deskripsi singkat sebuah tag untuk laporan."""
        cls = classes_str(tag)[:50]
        id_ = tag.get("id", "")
        return f"<{tag.name}> id='{id_}' class='{cls}'"

    def _detect_issues(self):
        """Deteksi berbagai masalah UI."""
        body = self.soup.find("body") or self.soup

        # 1. Scroll nesting
        for sn in self.scroll_nestings:
            self.issues.append({
                "type":     "scroll_nesting",
                "severity": "warning",
                "message":  f"Scroll nesting terdeteksi: {sn['outer']} berisi {sn['inner']}",
                "path":     sn["path"],
            })

        # 2. Button tanpa teks / aria-label
        for btn in self.soup.find_all("button"):
            text = btn.get_text(strip=True)
            aria = btn.get("aria-label", "")
            xtext = btn.get(":x-text", btn.get("x-text", ""))
            if not text and not aria and not xtext:
                self.issues.append({
                    "type":     "empty_button",
                    "severity": "warning",
                    "message":  f"Tombol tanpa teks/aria-label: {self._describe_tag(btn)}",
                    "path":     "",
                })

        # 3. Input tanpa label
        for inp in self.soup.find_all(["input", "select", "textarea"]):
            inp_id = inp.get("id", "")
            inp_type = inp.get("type", "text")
            if inp_type in ("hidden", "submit", "button"):
                continue
            has_label = False
            if inp_id:
                has_label = bool(self.soup.find("label", attrs={"for": inp_id}))
            aria_label = inp.get("aria-label", "") or inp.get("placeholder", "")
            x_model = inp.get("x-model", "")
            if not has_label and not aria_label and not x_model:
                self.issues.append({
                    "type":     "input_no_label",
                    "severity": "info",
                    "message":  f"Input tanpa label/placeholder: {self._describe_tag(inp)}",
                    "path":     "",
                })

        # 4. Tabel tanpa header
        for tbl in self.soup.find_all("table"):
            if not tbl.find("th") and not tbl.find("thead"):
                self.issues.append({
                    "type":     "table_no_header",
                    "severity": "info",
                    "message":  f"Tabel tanpa <th>/<thead>: {self._describe_tag(tbl)}",
                    "path":     "",
                })

        # 5. Img tanpa alt
        for img in self.soup.find_all("img"):
            if not img.get("alt") and not img.get(":src") and not img.get("x-bind:src"):
                self.issues.append({
                    "type":     "img_no_alt",
                    "severity": "info",
                    "message":  f"<img> tanpa alt attribute",
                    "path":     "",
                })

        # 6. Form tanpa submit action
        for form in self.soup.find_all("form"):
            action = form.get("action", "")
            submit = form.find("button", attrs={"type": "submit"}) or \
                     form.find("input", attrs={"type": "submit"})
            x_submit = form.get("@submit") or form.get("x-on:submit")
            if not action and not submit and not x_submit:
                self.issues.append({
                    "type":     "form_no_action",
                    "severity": "warning",
                    "message":  f"Form tanpa action/submit handler: {self._describe_tag(form)}",
                    "path":     "",
                })

        # 7. Heading hierarchy
        headings = self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        prev_level = 0
        for h in headings:
            level = int(h.name[1])
            if prev_level > 0 and level > prev_level + 1:
                self.issues.append({
                    "type":     "heading_skip",
                    "severity": "info",
                    "message":  f"Heading melompat dari h{prev_level} ke h{level}: '{h.get_text(strip=True)[:40]}'",
                    "path":     "",
                })
            prev_level = level

        # 8. Alpine x-cloak tanpa CSS
        for el in self.soup.find_all(attrs={"x-cloak": True}):
            self.issues.append({
                "type":     "alpine_xcloak",
                "severity": "info",
                "message":  f"x-cloak ditemukan — pastikan CSS [x-cloak]{{display:none}} ada di base template",
                "path":     "",
            })
            break  # cukup 1 kali warning

    def _build_stats(self) -> dict:
        """Hitung statistik komponen."""
        type_counts = defaultdict(int)
        for c in self.components:
            type_counts[c["type"]] += 1

        interactive = sum(1 for c in self.components if c.get("is_interactive"))
        with_scroll = sum(1 for c in self.components if c.get("has_scroll"))
        with_form   = sum(1 for c in self.components if c.get("has_form_fields"))

        return {
            "total_components": len(self.components),
            "by_type":          dict(type_counts),
            "interactive":      interactive,
            "with_scroll":      with_scroll,
            "with_form_fields": with_form,
            "scroll_nestings":  len(self.scroll_nestings),
            "issues":           len(self.issues),
            "issues_by_severity": {
                "warning": sum(1 for i in self.issues if i["severity"] == "warning"),
                "info":    sum(1 for i in self.issues if i["severity"] == "info"),
            },
        }


# ══════════════════════════════════════════════════════════════════════
#  STEP 2: GENERATE HTML WIREFRAME
# ══════════════════════════════════════════════════════════════════════

class HTMLWireframeGenerator:
    """
    Menghasilkan HTML wireframe dari hasil analisis.
    Semua warna dikupas, hanya struktur grayscale yang tersisa.
    """

    WIREFRAME_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Courier New', monospace;
    background: #F5F5F5;
    color: #333;
    padding: 16px;
    font-size: 13px;
    line-height: 1.5;
}

/* ── Komponen utama ── */
.wf-page        { max-width: 1100px; margin: 0 auto; }
.wf-header      { background: #2C2C2C; color: #fff; padding: 12px 16px; border-radius: 4px; margin-bottom: 12px; font-weight: bold; font-size: 14px; }
.wf-nav         { background: #444; color: #fff; padding: 10px 16px; border-radius: 4px; margin-bottom: 12px; display: flex; gap: 12px; align-items: center; }
.wf-nav-item    { background: #666; color: #ddd; padding: 4px 10px; border-radius: 3px; font-size: 11px; }
.wf-breadcrumb  { color: #888; font-size: 11px; margin-bottom: 8px; }
.wf-breadcrumb span { margin: 0 4px; }

/* ── Sections & Cards ── */
.wf-section     { border: 1.5px solid #CCC; border-radius: 6px; padding: 12px; margin-bottom: 12px; background: #FFF; }
.wf-card        { border: 1px solid #CCC; border-radius: 4px; padding: 10px; background: #FAFAFA; margin-bottom: 8px; }
.wf-card-dark   { border: 1px solid #888; border-radius: 4px; padding: 10px; background: #2C2C2C; color: #EEE; margin-bottom: 8px; }
.wf-metric      { border: 1px solid #CCC; border-radius: 4px; padding: 10px; background: #F0F0F0; text-align: center; }
.wf-metric .val { font-size: 22px; font-weight: bold; margin: 4px 0; }
.wf-metric .lbl { font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.wf-sidebar     { border: 1.5px dashed #AAA; border-radius: 4px; padding: 10px; background: #F8F8F8; }

/* ── Layout ── */
.wf-grid        { display: grid; gap: 10px; margin-bottom: 10px; }
.wf-grid-2      { grid-template-columns: 1fr 1fr; }
.wf-grid-3      { grid-template-columns: 1fr 1fr 1fr; }
.wf-grid-4      { grid-template-columns: 1fr 1fr 1fr 1fr; }
.wf-grid-23     { grid-template-columns: 2fr 1fr; }
.wf-grid-32     { grid-template-columns: 1fr 1fr 1fr 1fr 1fr; }
.wf-flex        { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; }

/* ── Form Elements ── */
.wf-input       { border: 1px solid #BBB; background: #FFF; border-radius: 3px; padding: 7px 10px; font-size: 12px; font-family: inherit; display: block; width: 100%; color: #555; }
.wf-select      { border: 1px solid #BBB; background: #FFF url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="6"><path d="M0 0l5 6 5-6z" fill="%23888"/></svg>') no-repeat right 8px center; border-radius: 3px; padding: 7px 28px 7px 10px; font-size: 12px; font-family: inherit; display: block; width: 100%; appearance: none; color: #555; }
.wf-textarea    { border: 1px solid #BBB; background: #FFF; border-radius: 3px; padding: 7px 10px; font-size: 12px; font-family: inherit; display: block; width: 100%; color: #555; min-height: 60px; resize: vertical; }
.wf-label       { font-size: 10px; font-weight: bold; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; display: block; }
.wf-field-group { margin-bottom: 10px; }

/* ── Buttons ── */
.wf-btn         { border: 1.5px solid #888; background: #E8E8E8; color: #333; padding: 7px 14px; border-radius: 3px; font-size: 12px; font-family: inherit; cursor: default; display: inline-block; font-weight: bold; }
.wf-btn-primary { border-color: #333; background: #333; color: #FFF; }
.wf-btn-danger  { border-color: #AA0000; background: #FFEEEE; color: #AA0000; }
.wf-btn-success { border-color: #006600; background: #EEFFEE; color: #006600; }
.wf-btn-sm      { padding: 4px 10px; font-size: 11px; }

/* ── Filters & Tabs ── */
.wf-filter-row  { display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; align-items: center; }
.wf-chip        { border: 1px solid #CCC; background: #F0F0F0; color: #555; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
.wf-chip-active { border-color: #333; background: #333; color: #FFF; }
.wf-tab-row     { display: flex; gap: 4px; margin-bottom: 10px; border-bottom: 1px solid #CCC; padding-bottom: 6px; }
.wf-tab         { border: 1px solid #CCC; background: #F5F5F5; color: #888; padding: 5px 14px; border-radius: 3px 3px 0 0; font-size: 11px; font-weight: bold; }
.wf-tab-active  { border-bottom-color: #FFF; background: #FFF; color: #333; }

/* ── Table ── */
.wf-table       { width: 100%; border-collapse: collapse; font-size: 12px; }
.wf-table th    { background: #EAEAEA; color: #555; padding: 7px 10px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1.5px solid #CCC; }
.wf-table td    { padding: 7px 10px; border-bottom: 1px solid #EEE; color: #333; }
.wf-table tr:hover td { background: #F8F8F8; }

/* ── Progress & Charts ── */
.wf-progress-bg  { background: #E8E8E8; border-radius: 99px; height: 8px; overflow: hidden; margin: 4px 0; }
.wf-progress-fill{ background: #555; height: 100%; border-radius: 99px; }
.wf-circle       { width: 80px; height: 80px; border-radius: 50%; border: 8px solid #CCC; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; color: #555; }

/* ── Image Placeholder ── */
.wf-img         { background: #E0E0E0; border: 1.5px dashed #AAA; border-radius: 4px; display: flex; align-items: center; justify-content: center; min-height: 60px; color: #888; font-size: 11px; text-align: center; padding: 8px; }

/* ── Badge / Status ── */
.wf-badge       { display: inline-block; border: 1px solid #AAA; background: #EEE; color: #555; padding: 2px 8px; border-radius: 99px; font-size: 10px; font-weight: bold; text-transform: uppercase; }

/* ── Timeline ── */
.wf-timeline    { padding-left: 20px; border-left: 2px solid #CCC; }
.wf-tl-item     { position: relative; padding: 6px 0 6px 12px; }
.wf-tl-item::before { content:''; position: absolute; left: -7px; top: 12px; width: 12px; height: 12px; border-radius: 50%; background: #CCC; border: 2px solid #FFF; box-shadow: 0 0 0 1px #CCC; }
.wf-tl-title    { font-size: 12px; font-weight: bold; color: #333; }
.wf-tl-meta     { font-size: 10px; color: #888; }

/* ── Scroll nesting warning ── */
.wf-scroll-warn { border: 2px dashed #FFC107; background: #FFFDE7; padding: 8px; border-radius: 4px; margin-bottom: 6px; }
.wf-scroll-label{ font-size: 10px; color: #856404; font-weight: bold; margin-bottom: 4px; }

/* ── Footer ── */
.wf-footer      { background: #EAEAEA; border: 1px solid #CCC; border-radius: 4px; padding: 10px 16px; margin-top: 12px; color: #888; font-size: 11px; text-align: center; }

/* ── Alpine root marker ── */
.wf-alpine      { border: 1.5px dotted #AAA; border-radius: 4px; padding: 10px; margin-bottom: 10px; position: relative; }
.wf-alpine::before { content: 'Alpine Component'; position: absolute; top: -9px; left: 8px; background: #FFF; padding: 0 4px; font-size: 9px; color: #AAA; font-weight: bold; }

/* ── Section label ── */
.wf-section-label { font-size: 10px; font-weight: bold; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; padding-bottom: 4px; border-bottom: 1px solid #EEE; }

/* ── Heading styles ── */
.wf-h1 { font-size: 20px; font-weight: bold; color: #111; margin-bottom: 6px; }
.wf-h2 { font-size: 16px; font-weight: bold; color: #222; margin-bottom: 5px; }
.wf-h3 { font-size: 13px; font-weight: bold; color: #333; margin-bottom: 4px; }
.wf-h4 { font-size: 12px; font-weight: bold; color: #444; margin-bottom: 3px; }

/* ── Empty state ── */
.wf-empty { border: 1.5px dashed #CCC; border-radius: 6px; padding: 24px; text-align: center; color: #AAA; font-size: 12px; background: #FAFAFA; }

/* ── Annotations ── */
.wf-annotation  { font-size: 10px; color: #999; font-style: italic; margin-top: 3px; }
.wf-components  { margin-top: 20px; border-top: 2px solid #DDD; padding-top: 12px; }
.wf-comp-item   { font-size: 11px; color: #666; padding: 2px 0; }
.wf-comp-type   { display: inline-block; background: #EAEAEA; border-radius: 3px; padding: 1px 6px; font-size: 10px; font-weight: bold; color: #555; margin-right: 6px; }
.wf-issues      { margin-top: 12px; border-top: 1px solid #EEE; padding-top: 10px; }
.wf-issue       { font-size: 11px; padding: 3px 0 3px 16px; position: relative; color: #666; }
.wf-issue::before { position: absolute; left: 0; }
.wf-issue.warning::before { content: '⚠'; color: #CC8800; }
.wf-issue.info::before    { content: 'ℹ'; color: #0066CC; }
    """

    def __init__(self, analysis: dict, original_html: str = ""):
        self.analysis = analysis
        self.original_html = original_html
        self.soup = BeautifulSoup(original_html, "lxml") if original_html else None

    def generate(self) -> str:
        """Generate HTML wireframe lengkap."""
        title = self.analysis["title"]
        stats = self.analysis["stats"]
        components = self.analysis["components"]
        issues = self.analysis["issues"]
        scroll_nestings = self.analysis["scroll_nestings"]
        now = datetime.now().strftime("%d %b %Y %H:%M")

        # Bangun body wireframe dari soup asli
        wireframe_body = self._transform_html()

        html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wireframe: {title}</title>
  <style>
{self.WIREFRAME_CSS}
  </style>
</head>
<body>
<div class="wf-page">

  <!-- ── WIREFRAME HEADER INFO ───────────────────────── -->
  <div class="wf-header">
    ▦ WIREFRAME: {title}
    <span style="float:right;font-size:11px;font-weight:normal;color:#AAA">
      Generated: {now} &nbsp;|&nbsp;
      {stats['total_components']} komponen &nbsp;|&nbsp;
      {stats['issues']} isu terdeteksi
    </span>
  </div>

  <!-- ── STAT SUMMARY ───────────────────────────────── -->
  <div class="wf-grid wf-grid-4" style="margin-bottom:12px">
    <div class="wf-metric">
      <div class="wf-metric val">{stats['total_components']}</div>
      <div class="wf-metric lbl">Total Komponen</div>
    </div>
    <div class="wf-metric">
      <div class="wf-metric val">{stats['interactive']}</div>
      <div class="wf-metric lbl">Interaktif</div>
    </div>
    <div class="wf-metric">
      <div class="wf-metric val">{stats['scroll_nestings']}</div>
      <div class="wf-metric lbl">Scroll Nesting</div>
    </div>
    <div class="wf-metric">
      <div class="wf-metric val">{stats['issues_by_severity'].get('warning', 0)}</div>
      <div class="wf-metric lbl">⚠ Warnings</div>
    </div>
  </div>

  <!-- ── SCROLL NESTING WARNINGS ────────────────────── -->
  {"".join(
    f'<div class="wf-scroll-warn"><div class="wf-scroll-label">⚠ SCROLL NESTING #{i+1}</div>'
    f'<div>Outer: <code>{sn["outer"][:80]}</code></div>'
    f'<div>Inner: <code>{sn["inner"][:80]}</code></div></div>'
    for i, sn in enumerate(scroll_nestings)
  ) if scroll_nestings else ""}

  <!-- ══ WIREFRAME CONTENT ══════════════════════════════ -->
  <div class="wf-section">
    <div class="wf-section-label">Wireframe Struktur Halaman</div>
    {wireframe_body}
  </div>

  <!-- ── COMPONENT INDEX ────────────────────────────── -->
  <div class="wf-components">
    <div class="wf-section-label">Indeks Komponen Terdeteksi ({len(components)})</div>
    {"".join(
      "<div class='wf-comp-item'>"
      + "<span class='wf-comp-type'>" + c["type"] + "</span>"
      + c["label"]
      + ("  <em style='color:#AAA;font-size:10px'> — " + c["text_preview"] + "</em>" if c.get("text_preview") else "")
      + ("  <span class='wf-badge' style='font-size:9px'>scroll</span>" if c.get("has_scroll") else "")
      + ("  <span class='wf-badge' style='font-size:9px;border-color:#888'>⚡</span>" if c.get("is_interactive") else "")
      + "</div>"
      for c in components
    )}
  </div>

  <!-- ── ISSUES ─────────────────────────────────────── -->
  {"".join([
    '<div class="wf-issues">',
    '<div class="wf-section-label">Isu Terdeteksi (' + str(len(issues)) + ')</div>',
    "".join(
      f'<div class="wf-issue {i["severity"]}">{i["message"]}</div>'
      for i in issues
    ),
    '</div>',
  ]) if issues else ""}

</div>
</body>
</html>"""
        return html

    def _transform_html(self) -> str:
        """
        Transformasi HTML asli → wireframe HTML.
        Kupas semua styling, pertahankan struktur.
        """
        if not self.soup:
            return "<p class='wf-annotation'>Tidak ada HTML untuk ditransformasi.</p>"

        body = self.soup.find("body") or self.soup
        # Clone untuk tidak merusak analisis soup
        body_clone = copy.copy(body)

        result = self._transform_tag(body_clone)
        return result

    def _transform_tag(self, tag: Tag) -> str:
        """Rekursif transform tag → wireframe HTML string."""
        if not isinstance(tag, Tag):
            return ""

        name = tag.name

        # Skip non-structural
        if name in REMOVE_TAGS:
            return ""
        if name in ("html", "head"):
            return ""

        # Ambil child results dulu
        children_html = self._children_html(tag)

        # ── Mapping ke wireframe element ──

        # Nav
        if name == "nav" or (name in ("div", "header") and re.search(r"\bnav\b|\bnavbar\b|\btopbar\b", classes_str(tag), re.I)):
            return f'<div class="wf-nav">[ NAVIGATION ] {self._nav_items(tag)}</div>'

        # Header / Hero
        if name == "header" or re.search(r"\bhero\b|\bbanner\b|\bjumbotron\b", classes_str(tag), re.I):
            return f'<div class="wf-section"><div class="wf-section-label">[ HEADER / HERO ]</div>{children_html}</div>'

        # Footer
        if name == "footer" or re.search(r"\bfooter\b", classes_str(tag), re.I):
            return f'<div class="wf-footer">[ FOOTER ] {get_text_preview(tag, 80)}</div>'

        # Modal / Dialog
        if name == "dialog" or re.search(r"\bmodal\b|\bdialog\b|\boverlayb\b|\bdrawer\b", classes_str(tag), re.I):
            return (f'<div class="wf-section" style="border-style:double;border-color:#888;">'
                    f'<div class="wf-section-label">[ MODAL / DIALOG ]</div>'
                    f'{children_html}</div>')

        # Headings
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            lvl = name  # h1..h6
            text = get_text_preview(tag, 80)
            return f'<div class="wf-{lvl}">{text or f"[{name.upper()} Heading]"}</div>'

        # Paragraphs
        if name == "p":
            text = get_text_preview(tag, 120)
            if not text:
                return ""
            return f'<p style="font-size:12px;color:#555;margin-bottom:6px;">{text}</p>'

        # Buttons
        if is_button(tag):
            text = get_text_preview(tag, 40) or "[icon]"
            cls = classes_str(tag)
            btn_cls = "wf-btn-primary" if re.search(r"bg-slate-[789]|bg-emerald|btn-start|btn-primary|bg-slate-800|bg-slate-700", cls, re.I) else \
                      "wf-btn-danger"  if re.search(r"rose|red|danger|btn-stop|btn-delete", cls, re.I) else \
                      "wf-btn-success" if re.search(r"emerald|green|btn-complete|bg-emerald", cls, re.I) else ""
            return f'<button class="wf-btn {btn_cls}" style="margin:2px">{text}</button>'

        # Inputs
        if name == "input":
            inp_type = tag.get("type", "text")
            if inp_type == "hidden":
                return ""
            if inp_type in ("submit", "button"):
                text = tag.get("value", "Submit")
                return f'<button class="wf-btn wf-btn-primary" style="margin:2px">{text}</button>'
            placeholder = tag.get("placeholder", tag.get("x-model", f"[{inp_type} input]"))
            if inp_type in ("checkbox", "radio"):
                return f'<label style="font-size:12px;display:inline-flex;align-items:center;gap:4px;margin-right:8px"><input type="{inp_type}" disabled> {placeholder}</label>'
            if inp_type in ("date", "datetime-local"):
                return f'<input class="wf-input" type="text" value="[{inp_type}]" placeholder="{placeholder}" disabled style="width:auto">'
            return f'<input class="wf-input" type="text" placeholder="{placeholder}" disabled>'

        if name == "textarea":
            placeholder = tag.get("placeholder", tag.get("x-model", "[textarea]"))
            rows = tag.get("rows", "3")
            return f'<textarea class="wf-textarea" placeholder="{placeholder}" rows="{rows}" disabled></textarea>'

        if name == "select":
            model = tag.get("x-model", tag.get("name", ""))
            options = tag.find_all("option")
            opt_text = options[0].get_text(strip=True) if options else "Pilih..."
            total = len(options)
            return f'<select class="wf-select" disabled><option>{opt_text} ({total} opsi)</option></select>'

        # Label
        if name == "label":
            text = get_text_preview(tag, 60)
            return f'<label class="wf-label">{text}</label>'

        # Images
        if name in ("img", "picture", "figure", "video"):
            alt = tag.get("alt", "") if name == "img" else ""
            return f'<div class="wf-img">[ IMAGE {("— " + alt) if alt else ""} ]</div>'

        # Tables
        if name == "table":
            return f'<div class="wf-section"><div class="wf-section-label">[ TABLE ]</div>{self._transform_table(tag)}</div>'

        # Lists
        if name in ("ul", "ol"):
            items = tag.find_all("li", recursive=False)
            if not items:
                items = tag.find_all("li")
            item_count = len(items)
            list_html = []
            for li in items[:5]:  # max 5 preview items
                text = get_text_preview(li, 60)
                list_html.append(f'<li style="font-size:12px;color:#555;padding:2px 0">{text}</li>')
            if item_count > 5:
                list_html.append(f'<li style="font-size:11px;color:#AAA">... {item_count - 5} item lainnya</li>')
            return f'<{name} style="padding-left:18px;margin-bottom:8px">{"".join(list_html)}</{name}>'

        # Timeline
        if re.search(r"\btl-track\b|\btimeline\b", classes_str(tag), re.I):
            return f'<div class="wf-timeline">{children_html}</div>'
        if re.search(r"\btl-item\b", classes_str(tag), re.I):
            text = get_text_preview(tag, 60)
            return f'<div class="wf-tl-item"><div class="wf-tl-title">{text[:40]}</div></div>'

        # Progress circle
        if re.search(r"\bprogress-circle\b|\bdonut\b|\bgauge\b", classes_str(tag), re.I):
            return '<div style="display:flex;justify-content:center;padding:10px"><div class="wf-circle">xx%</div></div>'

        # Progress bar
        if re.search(r"\bprogress-track\b|\bprogress-bar\b|\bprob-bar-bg\b|\bcost-bar-bg\b", classes_str(tag), re.I):
            return '<div class="wf-progress-bg"><div class="wf-progress-fill" style="width:60%"></div></div>'

        # Badge/tag
        if re.search(r"\bbom-tag\b|\bstatus-badge\b|\bbadge\b|\bpill\b(?!.*progress)", classes_str(tag), re.I):
            text = get_text_preview(tag, 20)
            return f'<span class="wf-badge">{text or "STATUS"}</span> '

        # Filter buttons row
        if re.search(r"\bfilter-btn\b|\bfilter-chip\b", classes_str(tag), re.I):
            text = get_text_preview(tag, 20)
            return f'<button class="wf-chip">{text}</button>'

        # Cards
        if re.search(r"\bglass-card\b|\bglass-panel\b|\bcontrol-panel\b", classes_str(tag), re.I):
            scroll_class = " wf-scroll-warn" if has_scroll(tag) else ""
            scroll_label = '<div class="wf-scroll-label">⚠ SCROLL ELEMENT</div>' if has_scroll(tag) else ""
            return f'<div class="wf-card{scroll_class}">{scroll_label}{children_html}</div>'

        if re.search(r"\bmetric-card\b|\bstat-card\b", classes_str(tag), re.I):
            text = get_text_preview(tag, 60)
            return f'<div class="wf-metric"><div class="wf-metric val">—</div><div class="wf-metric lbl">{text[:30]}</div></div>'

        # Alpine root
        if tag.get("x-data"):
            return f'<div class="wf-alpine">{children_html}</div>'

        # Scroll warning wrapper
        if has_scroll(tag):
            return f'<div class="wf-scroll-warn"><div class="wf-scroll-label">⚠ SCROLL CONTAINER</div>{children_html}</div>'

        # Grid layout
        grid = get_grid_info(tag)
        if grid:
            cols = re.search(r"(\d+)\s*cols", grid)
            n = int(cols.group(1)) if cols else 2
            n = min(n, 4)  # cap at 4 untuk wireframe
            return f'<div class="wf-grid wf-grid-{n}" style="margin-bottom:8px">{children_html}</div>'

        # Flex row dengan banyak buttons → filter row
        if re.search(r"\bflex\b", classes_str(tag), re.I) and name in ("div", "section"):
            btns = [c for c in tag.children if isinstance(c, Tag) and is_button(c)]
            if len(btns) >= 3:
                return f'<div class="wf-filter-row">{children_html}</div>'

        # Section semantic
        if name in ("section", "article", "aside", "main"):
            label = SEMANTIC_LABELS.get(name, f"[ {name.upper()} ]")
            return f'<div class="wf-section"><div class="wf-section-label">{label}</div>{children_html}</div>'

        # Form
        if name == "form":
            return f'<div class="wf-section" style="border-color:#AAA"><div class="wf-section-label">[ FORM ]</div>{children_html}</div>'

        # Default: render children
        if name in ("div", "span", "section", "article", "aside",
                    "main", "header", "footer", "nav", "template"):
            if children_html.strip():
                return children_html
            return ""

        # Catch-all: just children
        if children_html.strip():
            return children_html
        return ""

    def _children_html(self, tag: Tag) -> str:
        """Render semua children dari sebuah tag."""
        parts = []
        for child in tag.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                # Skip Django template tags yang tersisa
                if text and not text.startswith("{%") and not text.startswith("{{"):
                    if len(text) > 1:
                        parts.append(f'<span style="font-size:12px;color:#555">{text[:80]}</span>')
            elif isinstance(child, Tag):
                parts.append(self._transform_tag(child))
        return "".join(parts)

    def _nav_items(self, tag: Tag) -> str:
        """Ambil item navigasi dari tag."""
        items = tag.find_all("a", limit=6)
        if not items:
            items = tag.find_all(["button", "span"], limit=4)
        result = []
        for item in items:
            text = item.get_text(strip=True)[:20]
            if text and not text.startswith("{"):
                result.append(f'<span class="wf-nav-item">{text}</span>')
        return " ".join(result) if result else "<span class='wf-nav-item'>Nav Items</span>"

    def _transform_table(self, tag: Tag) -> str:
        """Transformasi tabel menjadi wireframe tabel."""
        result = ['<table class="wf-table">']
        thead = tag.find("thead")
        if thead:
            result.append("<thead><tr>")
            for th in thead.find_all("th"):
                result.append(f'<th>{get_text_preview(th, 30)}</th>')
            result.append("</tr></thead>")

        tbody = tag.find("tbody")
        if tbody:
            result.append("<tbody>")
            rows = tbody.find_all("tr")
            for i, row in enumerate(rows[:4]):  # max 4 rows preview
                result.append("<tr>")
                for td in row.find_all("td"):
                    text = get_text_preview(td, 30)
                    result.append(f'<td>{text or "—"}</td>')
                result.append("</tr>")
            if len(rows) > 4:
                cols = len(rows[0].find_all("td")) if rows else 1
                result.append(f'<tr><td colspan="{cols}" style="text-align:center;color:#AAA;font-size:11px">... {len(rows) - 4} baris lainnya</td></tr>')
            result.append("</tbody>")

        result.append("</table>")
        return "".join(result)


# ══════════════════════════════════════════════════════════════════════
#  STEP 3: GENERATE PNG WIREFRAME (Pillow)
# ══════════════════════════════════════════════════════════════════════

class PNGWireframeGenerator:
    """
    Menghasilkan gambar wireframe PNG dari hasil analisis komponen.
    Pendekatan: render layout tree sebagai gambar grayscale sketsa.
    """

    # Dimensi
    IMG_W     = 900
    PADDING   = 32
    ROW_H     = 36
    INDENT_W  = 20
    MIN_H     = 500

    # Font
    FONT_SIZE     = 12
    FONT_SMALL    = 10
    FONT_LABEL    = 11

    def __init__(self, analysis: dict):
        self.analysis   = analysis
        self.components = analysis["components"]
        self.issues     = analysis["issues"]
        self.stats      = analysis["stats"]
        self.title      = analysis["title"]

        # Load font (fallback ke default jika tidak ada)
        try:
            self.font       = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", self.FONT_SIZE)
            self.font_bold  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", self.FONT_SIZE)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", self.FONT_SMALL)
            self.font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", self.FONT_LABEL)
        except Exception:
            self.font       = ImageFont.load_default()
            self.font_bold  = self.font
            self.font_small = self.font
            self.font_label = self.font

    def generate(self, output_path: str):
        """Generate dan simpan PNG wireframe."""
        # Hitung tinggi kebutuhan
        n_rows   = len(self.components) + 6  # header + stats + components + footer
        img_h    = max(self.MIN_H, n_rows * self.ROW_H + self.PADDING * 3 + 200)

        img  = Image.new("RGB", (self.IMG_W, img_h), color="#F5F5F5")
        draw = ImageDraw.Draw(img)

        y = self.PADDING

        # ── Header bar ──
        y = self._draw_header(draw, y)
        y += 12

        # ── Stats row ──
        y = self._draw_stats(draw, y)
        y += 16

        # ── Layout tree ──
        y = self._draw_section_title(draw, y, "STRUKTUR KOMPONEN")
        y = self._draw_components(draw, y)
        y += 16

        # ── Issues ──
        if self.issues:
            y = self._draw_section_title(draw, y, f"ISU TERDETEKSI ({len(self.issues)})")
            y = self._draw_issues(draw, y)

        # ── Footer ──
        self._draw_footer(draw, img_h)

        # Trim gambar ke konten aktual
        final_h = min(img_h, y + self.PADDING + 40)
        img = img.crop((0, 0, self.IMG_W, final_h))

        img.save(output_path, "PNG", dpi=(150, 150))
        return output_path

    def _draw_header(self, draw: ImageDraw.Draw, y: int) -> int:
        bar_h = 44
        draw.rectangle([0, y, self.IMG_W, y + bar_h], fill="#2C2C2C")
        draw.text((self.PADDING, y + 8),  f"▦  WIREFRAME: {self.title[:60]}", font=self.font_bold, fill="#FFFFFF")
        draw.text((self.PADDING, y + 24), f"   {self.analysis['filename']}", font=self.font_small, fill="#AAAAAA")
        now = datetime.now().strftime("%d %b %Y %H:%M")
        draw.text((self.IMG_W - 200, y + 16), now, font=self.font_small, fill="#888888")
        return y + bar_h

    def _draw_stats(self, draw: ImageDraw.Draw, y: int) -> int:
        stats = self.stats
        items = [
            ("KOMPONEN",  str(stats["total_components"])),
            ("INTERAKTIF",str(stats["interactive"])),
            ("SCROLL NEST",str(stats["scroll_nestings"])),
            ("⚠ WARNINGS", str(stats["issues_by_severity"].get("warning", 0))),
            ("ℹ INFO",     str(stats["issues_by_severity"].get("info", 0))),
        ]
        box_w  = (self.IMG_W - self.PADDING * 2) // len(items)
        box_h  = 52
        x_start = self.PADDING
        for label, value in items:
            x = x_start
            draw.rectangle([x, y, x + box_w - 6, y + box_h], fill="#EEEEEE", outline="#CCCCCC", width=1)
            # Value
            draw.text((x + 8, y + 6),  value, font=self.font_bold, fill="#222222")
            draw.text((x + 8, y + 28), label, font=self.font_small, fill="#888888")
            x_start += box_w
        return y + box_h

    def _draw_section_title(self, draw: ImageDraw.Draw, y: int, text: str) -> int:
        draw.line([self.PADDING, y + 8, self.IMG_W - self.PADDING, y + 8], fill="#DDDDDD", width=1)
        draw.rectangle([self.PADDING, y, self.PADDING + len(text) * 7 + 12, y + 16], fill="#EEEEEE")
        draw.text((self.PADDING + 6, y + 2), text, font=self.font_small, fill="#666666")
        return y + 22

    def _draw_components(self, draw: ImageDraw.Draw, y: int) -> int:
        # Warna per tipe komponen
        type_colors = {
            "navbar":        ("#2C2C2C", "#FFFFFF"),
            "sidebar":       ("#E8E8E8", "#444444"),
            "card":          ("#FFFFFF", "#333333"),
            "metric":        ("#F0F0F0", "#222222"),
            "button":        ("#DDDDDD", "#333333"),
            "button-primary":("#333333", "#FFFFFF"),
            "button-danger": ("#FFEEEE", "#AA0000"),
            "input":         ("#FFFFFF", "#555555"),
            "table-row":     ("#FAFAFA", "#444444"),
            "heading":       ("#FFFFFF", "#111111"),
            "layout":        ("#F8F8F8", "#666666"),
            "alpine-root":   ("#FFFDE7", "#555500"),
            "modal":         ("#FFFFFF", "#333333"),
            "alert":         ("#FFF3CD", "#664D03"),
            "timeline":      ("#F0F0F0", "#444444"),
            "progressbar":   ("#E8E8E8", "#444444"),
            "badge":         ("#EAEAEA", "#555555"),
            "calendar":      ("#F5F5F5", "#333333"),
            "empty":         ("#FAFAFA", "#AAAAAA"),
        }

        w = self.IMG_W - self.PADDING * 2
        for comp in self.components:
            depth    = min(comp.get("depth", 0), 8)
            indent   = depth * self.INDENT_W
            box_x    = self.PADDING + indent
            box_w    = w - indent
            box_h    = self.ROW_H - 4

            comp_type = comp.get("type", "div")
            bg, fg    = type_colors.get(comp_type, ("#F5F5F5", "#444444"))

            # Scroll warning override
            if comp.get("has_scroll"):
                bg = WF_COLORS["scroll_bg"]

            # Draw box
            draw.rectangle([box_x, y, box_x + box_w, y + box_h],
                           fill=bg, outline="#CCCCCC", width=1)

            # Garis indent
            if depth > 0:
                draw.line([box_x - 6, y, box_x - 6, y + box_h], fill="#DDDDDD", width=1)
                draw.line([box_x - 6, y + box_h // 2, box_x, y + box_h // 2], fill="#DDDDDD", width=1)

            # Type badge
            type_text   = f"[{comp_type[:12]}]"
            badge_w     = len(type_text) * 7 + 6
            draw.rectangle([box_x + 4, y + 4, box_x + 4 + badge_w, y + box_h - 4],
                           fill="#DDDDDD" if bg == "#FFFFFF" else "#CCCCCC")
            draw.text((box_x + 7, y + 7), type_text, font=self.font_small, fill="#555555")

            # Label
            label       = comp.get("label", comp_type)[:55]
            draw.text((box_x + badge_w + 10, y + 7), label, font=self.font, fill=fg)

            # Preview text
            preview = comp.get("text_preview", "")[:40]
            if preview:
                draw.text((box_x + badge_w + 10, y + 20), f"  {preview}", font=self.font_small, fill="#AAAAAA")

            # Scroll icon
            if comp.get("has_scroll"):
                draw.text((box_x + box_w - 60, y + 10), "⚠ scroll", font=self.font_small, fill="#CC8800")

            # Interactive icon
            if comp.get("is_interactive"):
                draw.text((box_x + box_w - 20, y + 10), "⚡", font=self.font_small, fill="#666666")

            y += self.ROW_H

            # Batas bawah gambar
            if y > 9000:
                break

        return y

    def _draw_issues(self, draw: ImageDraw.Draw, y: int) -> int:
        for issue in self.issues[:20]:  # max 20
            sev   = issue.get("severity", "info")
            icon  = "⚠" if sev == "warning" else "ℹ"
            color = "#CC8800" if sev == "warning" else "#0066CC"
            bg    = "#FFFDE7" if sev == "warning" else "#E3F2FD"
            msg   = issue.get("message", "")[:90]

            draw.rectangle([self.PADDING, y, self.IMG_W - self.PADDING, y + 22],
                           fill=bg, outline="#DDDDDD", width=1)
            draw.text((self.PADDING + 6,  y + 5), icon, font=self.font_small, fill=color)
            draw.text((self.PADDING + 20, y + 5), msg,  font=self.font_small, fill="#444444")
            y += 26
        return y

    def _draw_footer(self, draw: ImageDraw.Draw, img_h: int):
        footer_y = img_h - 28
        draw.rectangle([0, footer_y, self.IMG_W, img_h], fill="#EEEEEE")
        draw.text(
            (self.PADDING, footer_y + 8),
            f"UI Reverse Engineer  •  {self.analysis['filename']}  •  {self.stats['total_components']} components",
            font=self.font_small, fill="#AAAAAA"
        )


# ══════════════════════════════════════════════════════════════════════
#  STEP 4: GENERATE AUDIT REPORT (Markdown)
# ══════════════════════════════════════════════════════════════════════

class AuditReportGenerator:
    """Menghasilkan laporan audit UI/UX dalam format Markdown."""

    def __init__(self, all_analyses: list[dict]):
        self.analyses = all_analyses

    def generate(self) -> str:
        now = datetime.now().strftime("%d %B %Y %H:%M")
        total_files = len(self.analyses)
        total_comps = sum(a["stats"]["total_components"] for a in self.analyses)
        total_issues = sum(a["stats"]["issues"] for a in self.analyses)
        total_warnings = sum(a["stats"]["issues_by_severity"].get("warning", 0) for a in self.analyses)
        total_scroll = sum(a["stats"]["scroll_nestings"] for a in self.analyses)

        lines = [
            "# Laporan Audit UI/UX — Reverse Engineering",
            f"**Dibuat:** {now}",
            f"**Total file dianalisis:** {total_files}",
            "",
            "---",
            "",
            "## Ringkasan Eksekutif",
            "",
            f"| Metrik | Nilai |",
            f"|--------|-------|",
            f"| File HTML dianalisis | {total_files} |",
            f"| Total komponen terdeteksi | {total_comps} |",
            f"| Total isu ditemukan | {total_issues} |",
            f"| ⚠ Warnings | {total_warnings} |",
            f"| Scroll nesting | {total_scroll} |",
            "",
            "---",
            "",
        ]

        # Per-file analysis
        for analysis in self.analyses:
            lines += self._file_section(analysis)

        # Cross-file patterns
        lines += self._cross_file_patterns()

        # Rekomendasi
        lines += self._recommendations()

        return "\n".join(lines)

    def _file_section(self, a: dict) -> list[str]:
        stats = a["stats"]
        lines = [
            f"## 📄 {a['title']}",
            f"**File:** `{a['filename']}`",
            "",
            "### Statistik Komponen",
            "",
            "| Tipe | Jumlah |",
            "|------|--------|",
        ]
        for t, n in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
            lines.append(f"| {t} | {n} |")
        lines += [
            "",
            f"- **Total komponen:** {stats['total_components']}",
            f"- **Elemen interaktif:** {stats['interactive']}",
            f"- **Container dengan scroll:** {stats['with_scroll']}",
            f"- **Scroll nesting:** {stats['scroll_nestings']}",
            "",
        ]

        # Scroll nestings
        if a["scroll_nestings"]:
            lines.append("### ⚠ Scroll Nesting Terdeteksi")
            lines.append("")
            for sn in a["scroll_nestings"]:
                lines.append(f"- **Outer:** `{sn['outer'][:80]}`")
                lines.append(f"  **Inner:** `{sn['inner'][:80]}`")
                lines.append("")

        # Issues
        if a["issues"]:
            lines.append("### Isu & Temuan")
            lines.append("")
            warnings = [i for i in a["issues"] if i["severity"] == "warning"]
            infos    = [i for i in a["issues"] if i["severity"] == "info"]
            for issue in warnings:
                lines.append(f"- ⚠ **{issue['type']}:** {issue['message']}")
            for issue in infos:
                lines.append(f"- ℹ {issue['type']}: {issue['message']}")
            lines.append("")

        lines.append("---")
        lines.append("")
        return lines

    def _cross_file_patterns(self) -> list[str]:
        lines = [
            "## Pola Lintas File",
            "",
        ]

        # Komponen paling umum
        type_total: dict[str, int] = defaultdict(int)
        for a in self.analyses:
            for t, n in a["stats"]["by_type"].items():
                type_total[t] += n
        top = sorted(type_total.items(), key=lambda x: -x[1])[:10]

        lines += [
            "### Komponen Paling Banyak Digunakan",
            "",
            "| Tipe | Total (semua file) |",
            "|------|-------------------|",
        ]
        for t, n in top:
            lines.append(f"| {t} | {n} |")
        lines.append("")

        # File dengan paling banyak isu
        by_issues = sorted(self.analyses, key=lambda a: -a["stats"]["issues"])
        lines += [
            "### File dengan Isu Terbanyak",
            "",
        ]
        for a in by_issues[:5]:
            lines.append(f"- **{a['title']}** (`{a['filename']}`): {a['stats']['issues']} isu")
        lines.append("")

        # File dengan scroll nesting
        with_scroll_nest = [a for a in self.analyses if a["stats"]["scroll_nestings"] > 0]
        if with_scroll_nest:
            lines += [
                "### File dengan Scroll Nesting",
                "",
            ]
            for a in with_scroll_nest:
                lines.append(f"- **{a['title']}**: {a['stats']['scroll_nestings']} scroll nesting")
            lines.append("")

        return lines

    def _recommendations(self) -> list[str]:
        # Kumpulkan semua isu unik
        all_issues: dict[str, list[str]] = defaultdict(list)
        for a in self.analyses:
            for issue in a["issues"]:
                all_issues[issue["type"]].append(a["title"])

        lines = [
            "## Rekomendasi Perbaikan",
            "",
        ]

        recs = {
            "scroll_nesting":    ("🔴 Kritis", "Hilangkan scroll nesting. Container scroll tidak boleh berada di dalam container scroll lain. Refactor layout menggunakan CSS Grid/Flexbox yang tepat."),
            "empty_button":      ("🟠 Penting", "Semua tombol harus memiliki teks label atau `aria-label` untuk aksesibilitas screen reader."),
            "input_no_label":    ("🟡 Disarankan", "Setiap input form sebaiknya memiliki `<label>` yang terhubung via `for` attribute, atau minimal `aria-label` / `placeholder` yang deskriptif."),
            "table_no_header":   ("🟡 Disarankan", "Tabel data sebaiknya selalu memiliki baris header `<th>` dalam `<thead>` untuk aksesibilitas dan readability."),
            "img_no_alt":        ("🟡 Disarankan", "Semua `<img>` harus memiliki `alt` attribute. Untuk gambar dekoratif, gunakan `alt=\"\"`."),
            "form_no_action":    ("🟠 Penting", "Form harus memiliki `action` attribute atau `@submit` handler yang jelas. Form tanpa keduanya tidak akan berfungsi."),
            "heading_skip":      ("🟡 Disarankan", "Hierarki heading (h1→h2→h3) tidak boleh melompat. Ini mempengaruhi aksesibilitas dan SEO."),
            "alpine_xcloak":     ("🟢 Info", "Pastikan CSS `[x-cloak] { display: none !important; }` ada di base template untuk mencegah flash of unstyled content."),
        }

        for issue_type, files in sorted(all_issues.items(), key=lambda x: -len(x[1])):
            if issue_type in recs:
                priority, desc = recs[issue_type]
                file_list = ", ".join(f"`{f}`" for f in sorted(set(files))[:3])
                if len(set(files)) > 3:
                    file_list += f" dan {len(set(files))-3} lainnya"
                lines += [
                    f"### {priority} — {issue_type.replace('_', ' ').title()}",
                    f"**Ditemukan di:** {file_list}",
                    f"**Rekomendasi:** {desc}",
                    "",
                ]

        lines += [
            "---",
            "",
            "*Laporan ini dibuat otomatis oleh UI Reverse Engineer.*",
            f"*Generated: {datetime.now().strftime('%d %B %Y %H:%M')}*",
        ]
        return lines


# ══════════════════════════════════════════════════════════════════════
#  STEP 5: GENERATE INDEX HTML
# ══════════════════════════════════════════════════════════════════════

def generate_index(all_analyses: list[dict], output_dir: pathlib.Path) -> str:
    now = datetime.now().strftime("%d %b %Y %H:%M")
    rows = []
    for a in all_analyses:
        slug    = slugify(pathlib.Path(a["filename"]).stem)
        stats   = a["stats"]
        wf_link = f"wireframe_{slug}.html"
        js_link = f"structure_{slug}.json"
        png_link= f"wireframe_{slug}.png"

        warn_badge = ""
        if stats["issues_by_severity"].get("warning", 0) > 0:
            warn_badge = f'<span style="background:#FFC107;color:#333;padding:2px 6px;border-radius:3px;font-size:10px;font-weight:bold">⚠ {stats["issues_by_severity"]["warning"]} warnings</span>'
        scroll_badge = ""
        if stats["scroll_nestings"] > 0:
            scroll_badge = f'<span style="background:#FF5722;color:#FFF;padding:2px 6px;border-radius:3px;font-size:10px;font-weight:bold">🔄 {stats["scroll_nestings"]} scroll nest</span>'

        rows.append(f"""
        <tr>
          <td style="padding:10px 8px;border-bottom:1px solid #EEE">
            <div style="font-weight:bold;color:#222">{a['title']}</div>
            <div style="font-size:11px;color:#888;margin-top:2px">{a['filename']}</div>
          </td>
          <td style="padding:10px 8px;border-bottom:1px solid #EEE;text-align:center">{stats['total_components']}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #EEE;text-align:center">{stats['interactive']}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #EEE">{warn_badge} {scroll_badge}</td>
          <td style="padding:10px 8px;border-bottom:1px solid #EEE">
            <a href="{wf_link}" style="color:#0066CC;margin-right:8px">HTML</a>
            <a href="{png_link}" style="color:#0066CC;margin-right:8px">PNG</a>
            <a href="{js_link}" style="color:#0066CC">JSON</a>
          </td>
        </tr>""")

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Wireframe Index — UI Reverse Engineer</title>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; background: #F5F5F5; color: #333; padding: 32px; }}
    .container {{ max-width: 960px; margin: 0 auto; }}
    .header {{ background: #2C2C2C; color: #FFF; padding: 20px 24px; border-radius: 8px; margin-bottom: 24px; }}
    .header h1 {{ font-size: 20px; margin-bottom: 4px; }}
    .header p  {{ font-size: 12px; color: #AAA; }}
    table {{ width: 100%; border-collapse: collapse; background: #FFF; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    thead {{ background: #F0F0F0; }}
    thead th {{ padding: 10px 8px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; font-weight: bold; }}
    a {{ text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .footer {{ margin-top: 16px; font-size: 11px; color: #AAA; text-align: center; }}
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>▦ UI Reverse Engineer — Wireframe Index</h1>
    <p>Generated: {now} &nbsp;|&nbsp; {len(all_analyses)} files diproses</p>
  </div>
  <table>
    <thead>
      <tr>
        <th>Halaman</th>
        <th style="text-align:center">Komponen</th>
        <th style="text-align:center">Interaktif</th>
        <th>Isu</th>
        <th>Output</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
  <div style="margin-top:16px">
    <a href="audit_report.md" style="color:#0066CC;font-size:13px">📄 Buka Audit Report (Markdown)</a>
  </div>
  <div class="footer">UI Reverse Engineer • Python + BeautifulSoup4 + Pillow</div>
</div>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════

def collect_html_files(targets: list[str]) -> list[pathlib.Path]:
    """Kumpulkan semua file HTML dari argumen target."""
    files = []
    for target in targets:
        p = pathlib.Path(target)
        if p.is_dir():
            files.extend(sorted(p.glob("*.html")))
            files.extend(sorted(p.glob("**/*.html")))
        elif p.is_file() and p.suffix.lower() == ".html":
            files.append(p)
        else:
            print(f"[WARN] Tidak ditemukan: {target}")
    # Deduplicate sambil pertahankan urutan
    seen = set()
    unique = []
    for f in files:
        key = f.resolve()
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def process_file(
    html_path: pathlib.Path,
    output_dir: pathlib.Path,
    generate_png: bool = True,
) -> dict | None:
    """Proses satu file HTML → semua output."""
    print(f"\n  ▶ Processing: {html_path.name}")

    try:
        html_content = html_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"    [ERROR] Tidak bisa membaca file: {e}")
        return None

    slug = slugify(html_path.stem)

    # ── 1. Analisis ──
    print(f"    › Menganalisis struktur...", end="", flush=True)
    analyzer = UIStructureAnalyzer(html_content, filename=html_path.name)
    analysis = analyzer.analyze()
    stats    = analysis["stats"]
    print(f" OK ({stats['total_components']} komponen, {stats['issues']} isu)")

    # ── 2. JSON Structure ──
    json_path = output_dir / f"structure_{slug}.json"
    print(f"    › Menulis JSON struktur...", end="", flush=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
    print(f" OK → {json_path.name}")

    # ── 3. HTML Wireframe ──
    wf_html_path = output_dir / f"wireframe_{slug}.html"
    print(f"    › Membuat HTML wireframe...", end="", flush=True)
    try:
        wf_gen   = HTMLWireframeGenerator(analysis, html_content)
        wf_html  = wf_gen.generate()
        wf_html_path.write_text(wf_html, encoding="utf-8")
        print(f" OK → {wf_html_path.name}")
    except Exception as e:
        print(f" ERROR: {e}")

    # ── 4. PNG Wireframe ──
    if generate_png and PILLOW_OK:
        png_path = output_dir / f"wireframe_{slug}.png"
        print(f"    › Membuat PNG wireframe...", end="", flush=True)
        try:
            png_gen = PNGWireframeGenerator(analysis)
            png_gen.generate(str(png_path))
            print(f" OK → {png_path.name}")
        except Exception as e:
            print(f" ERROR: {e}")
    elif generate_png and not PILLOW_OK:
        print(f"    › PNG dilewati (Pillow tidak tersedia)")

    return analysis


def main():
    parser = argparse.ArgumentParser(
        description="UI Reverse Engineer — HTML → Wireframe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Contoh:
          python3 ui_reverse_engineer.py                     # proses semua *.html di folder ini
          python3 ui_reverse_engineer.py file.html           # satu file
          python3 ui_reverse_engineer.py ./templates/        # semua html dalam folder
          python3 ui_reverse_engineer.py a.html b.html       # beberapa file
          python3 ui_reverse_engineer.py --no-image          # tanpa PNG
          python3 ui_reverse_engineer.py --output ./hasil/   # folder output custom
        """)
    )
    parser.add_argument("targets", nargs="*", default=["."],
                        help="File HTML atau folder (default: folder saat ini)")
    parser.add_argument("--output", "-o", default="./wireframe_output",
                        help="Folder output (default: ./wireframe_output)")
    parser.add_argument("--no-image", action="store_true",
                        help="Skip generate PNG wireframe")
    parser.add_argument("--exclude", nargs="*", default=[],
                        help="Pattern nama file yang dikecualikan")

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║       UI REVERSE ENGINEER — Wireframe Generator      ║")
    print("╚══════════════════════════════════════════════════════╝")

    # ── Setup output dir ──
    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Output folder: {output_dir.resolve()}")

    # ── Kumpulkan file ──
    html_files = collect_html_files(args.targets)

    # Filter exclude
    if args.exclude:
        html_files = [
            f for f in html_files
            if not any(ex in f.name for ex in args.exclude)
        ]

    # Jangan proses file output sendiri
    html_files = [f for f in html_files if f.resolve() != (output_dir / f.name).resolve()]
    html_files = [f for f in html_files if not f.name.startswith("wireframe_")]
    html_files = [f for f in html_files if f.name != "summary_index.html"]

    if not html_files:
        print("\n[ERROR] Tidak ada file HTML yang ditemukan.")
        print("  Pastikan ada file .html di folder yang ditentukan.")
        sys.exit(1)

    print(f"📋 {len(html_files)} file HTML ditemukan:")
    for f in html_files:
        print(f"   • {f.name}")

    generate_png = not args.no_image

    # ── Proses setiap file ──
    print(f"\n{'─'*54}")
    print("  MEMPROSES FILE...")
    print(f"{'─'*54}")

    all_analyses = []
    for html_path in html_files:
        result = process_file(html_path, output_dir, generate_png)
        if result:
            all_analyses.append(result)

    if not all_analyses:
        print("\n[ERROR] Tidak ada file yang berhasil diproses.")
        sys.exit(1)

    # ── Audit Report ──
    print(f"\n{'─'*54}")
    report_path = output_dir / "audit_report.md"
    print(f"  › Membuat audit_report.md...", end="", flush=True)
    report_gen  = AuditReportGenerator(all_analyses)
    report_md   = report_gen.generate()
    report_path.write_text(report_md, encoding="utf-8")
    print(f" OK → {report_path.name}")

    # ── Index HTML ──
    index_path = output_dir / "summary_index.html"
    print(f"  › Membuat summary_index.html...", end="", flush=True)
    index_html = generate_index(all_analyses, output_dir)
    index_path.write_text(index_html, encoding="utf-8")
    print(f" OK → {index_path.name}")

    # ── Summary ──
    total_comps   = sum(a["stats"]["total_components"] for a in all_analyses)
    total_issues  = sum(a["stats"]["issues"] for a in all_analyses)
    total_warnings= sum(a["stats"]["issues_by_severity"].get("warning",0) for a in all_analyses)
    total_scroll  = sum(a["stats"]["scroll_nestings"] for a in all_analyses)

    print(f"\n{'═'*54}")
    print(f"  ✅ SELESAI — {len(all_analyses)} file diproses")
    print(f"{'─'*54}")
    print(f"  Komponen terdeteksi : {total_comps}")
    print(f"  Total isu           : {total_issues}")
    print(f"  ⚠ Warnings          : {total_warnings}")
    print(f"  Scroll nesting      : {total_scroll}")
    print(f"{'─'*54}")
    print(f"  Output di: {output_dir.resolve()}")
    print(f"  Buka:  summary_index.html  untuk navigasi")
    print(f"  Baca:  audit_report.md     untuk laporan audit")
    print(f"{'═'*54}\n")


if __name__ == "__main__":
    main()