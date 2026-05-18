#!/usr/bin/env python3
"""
lumra_css_scanner.py
====================
Scan semua file HTML di template root dan buat laporan lengkap:
  - CSS properties apa saja yang ada di <style> block tiap file
  - JS functions / variables dari <script> block
  - Kandidat token untuk dipindah ke :root (warna, shadow, radius, dll)
  - Inkonsistensi antar file (nilai yang mirip tapi beda)

Cara pakai:
  python lumra_css_scanner.py
  python lumra_css_scanner.py --root D:\\APPS\\Project\\lumra\\lumra_config\\templates
  python lumra_css_scanner.py --root ./templates --output report.json
  python lumra_css_scanner.py --root ./templates --summary
"""

import re
import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional

# ─── Default config ───────────────────────────────────────────────────────────
DEFAULT_ROOT = Path(r"D:\APPS\Project\lumra\lumra_config\templates")
SKIP_PATTERNS = ["purchasing", "vendor_form", "vendor_list", "vendors_list", "supplier_price"]

# ─── Token categories: regex pattern → token group ────────────────────────────
#
# Catatan gradient regex — 2-level nested parentheses:
#
#   Level 0  : konten langsung di dalam gradient(...)
#   Level 1  : satu nested call, misal rgba(...) atau hsl(...)
#   Level 2  : dua nested call, misal color-mix(in srgb, rgba(...), hsl(...))
#
#   Pattern:
#     [^()]*           — teks tanpa parens (level 0)
#     (?:
#       \(             — buka level 1
#         [^()]*       — teks tanpa parens (level 1)
#         (?:
#           \(         — buka level 2
#             [^()]*   — teks tanpa parens (level 2)
#           \)         — tutup level 2
#           [^()]*
#         )*
#       \)             — tutup level 1
#       [^()]*
#     )*
#
#   re.DOTALL ditambahkan agar `.` juga match newline — berguna jika
#   developer menulis gradient multi-baris.
#
TOKEN_PATTERNS = {
    "color_hex"    : re.compile(r'#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b'),
    "color_rgba"   : re.compile(r'rgba?\([^)]+\)'),
    "border_radius": re.compile(r'border-radius\s*:\s*([^;]+);'),
    "box_shadow"   : re.compile(r'box-shadow\s*:\s*([^;]+);'),
    "transition"   : re.compile(r'transition\s*:\s*([^;]+);'),
    "font_size"    : re.compile(r'font-size\s*:\s*([^;]+);'),
    "font_weight"  : re.compile(r'font-weight\s*:\s*([^;]+);'),
    "backdrop"     : re.compile(r'backdrop-filter\s*:\s*([^;]+);'),
    "gradient"     : re.compile(
                        r'(?:linear|radial)-gradient\('   # fungsi gradient
                        r'[^()]*'                         # level 0: teks biasa
                        r'(?:'
                            r'\('                         # buka level 1
                            r'[^()]*'                     # level 1: teks biasa
                            r'(?:'
                                r'\('                     # buka level 2
                                r'[^()]*'                 # level 2: teks biasa
                                r'\)'                     # tutup level 2
                                r'[^()]*'
                            r')*'
                            r'\)'                         # tutup level 1
                            r'[^()]*'
                        r')*'
                        r'\)',                            # tutup gradient
                        re.DOTALL
                    ),
    "z_index"      : re.compile(r'z-index\s*:\s*([^;]+);'),
    "opacity"      : re.compile(r'\bopacity\s*:\s*([^;]+);'),
}

# ─── JS pattern ───────────────────────────────────────────────────────────────
JS_FUNC_PATTERN   = re.compile(r'\bfunction\s+(\w+)\s*\(')
JS_ARROW_PATTERN  = re.compile(r'\bconst\s+(\w+)\s*=\s*(?:async\s*)?\(')
JS_FETCH_PATTERN  = re.compile(r"fetch\(['\"`]([^'\"` ]+)['\"`]")
JS_LOCALSTORAGE   = re.compile(r'localStorage\.(get|set)Item\([\'"`]([^\'"`]+)[\'"`]')
JS_EVENT_PATTERN  = re.compile(r"addEventListener\(['\"`](\w+)['\"`]")

# ─── CSS class pattern ────────────────────────────────────────────────────────
CSS_CLASS_PATTERN = re.compile(r'\.([\w-]+)\s*\{')
CSS_ANIM_PATTERN  = re.compile(r'@keyframes\s+([\w-]+)')


# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class CSSBlock:
    classes: list = field(default_factory=list)
    animations: list = field(default_factory=list)
    tokens: dict = field(default_factory=dict)   # category → [values]
    raw: str = ""

@dataclass
class JSBlock:
    functions: list = field(default_factory=list)
    arrow_funcs: list = field(default_factory=list)
    fetch_urls: list = field(default_factory=list)
    localstorage_keys: list = field(default_factory=list)
    event_listeners: list = field(default_factory=list)
    raw_lines: int = 0

@dataclass
class InlineStyleIssue:
    severity: str   # "high" = color hardcode | "medium" = pixel value
    category: str   # "color_hex" | "color_rgba" | "pixel_value"
    attribute: str  # nilai atribut style mentah (max 120 char)
    values: list    # nilai spesifik yang ditangkap, misal ["#059669", "20px"]

@dataclass
class FileReport:
    path: str
    rel_path: str
    css_blocks: list = field(default_factory=list)            # list of CSSBlock (as dict)
    js_blocks: list = field(default_factory=list)             # list of JSBlock (as dict)
    tailwind_classes: list = field(default_factory=list)
    django_tags: list = field(default_factory=list)
    inline_style_issues: list = field(default_factory=list)   # list of InlineStyleIssue (as dict)
    issues: list = field(default_factory=list)


# ─── Extraction helpers ───────────────────────────────────────────────────────

def extract_blocks(content: str, tag: str) -> list[str]:
    """Extract all <tag>...</tag> block contents."""
    pattern = re.compile(rf'<{tag}[^>]*>(.*?)</{tag}>', re.DOTALL | re.IGNORECASE)
    return [m.group(1) for m in pattern.finditer(content)]


def parse_css_block(css: str) -> CSSBlock:
    block = CSSBlock(raw=css[:200] + ("..." if len(css) > 200 else ""))

    # Classes & keyframes
    block.classes   = sorted(set(CSS_CLASS_PATTERN.findall(css)))
    block.animations = sorted(set(CSS_ANIM_PATTERN.findall(css)))

    # Token extraction
    for category, pattern in TOKEN_PATTERNS.items():
        matches = pattern.findall(css)
        cleaned = [m.strip() for m in matches if m.strip()]
        if cleaned:
            # deduplicate but keep order
            seen = set()
            unique = []
            for v in cleaned:
                if v.lower() not in seen:
                    seen.add(v.lower())
                    unique.append(v)
            block.tokens[category] = unique

    return block


def parse_js_block(js: str) -> JSBlock:
    block = JSBlock()
    block.raw_lines = js.count('\n') + 1

    block.functions       = sorted(set(JS_FUNC_PATTERN.findall(js)))
    block.arrow_funcs     = sorted(set(JS_ARROW_PATTERN.findall(js)))
    block.fetch_urls      = sorted(set(JS_FETCH_PATTERN.findall(js)))
    block.event_listeners = sorted(set(JS_EVENT_PATTERN.findall(js)))
    block.localstorage_keys = [
        f"{m[0]}Item('{m[1]}')"
        for m in JS_LOCALSTORAGE.findall(js)
    ]

    return block


def extract_tailwind(content: str) -> list[str]:
    """Collect unique Tailwind-like class names from class= attributes."""
    class_attr = re.compile(r'class=["\']([^"\']+)["\']')
    tw_like = re.compile(
        r'\b(?:bg|text|border|ring|shadow|flex|grid|gap|p|px|py|m|mx|my|w|h|'
        r'rounded|font|tracking|leading|opacity|z|overflow|transition|'
        r'duration|ease|translate|scale|rotate|skew|origin|cursor|'
        r'pointer|select|resize|appearance|outline|sr|not)-[\w\[\]/.-]+'
    )
    found = set()
    for cls_str in class_attr.findall(content):
        for cls in cls_str.split():
            if tw_like.match(cls):
                found.add(cls)
    return sorted(found)


def extract_django_tags(content: str) -> list[str]:
    tags = set()
    for m in re.finditer(r'\{%\s*([\w]+)', content):
        tags.add(m.group(1))
    return sorted(tags)


# ─── Inline style auditor ─────────────────────────────────────────────────────
#
# 3-level severity:
#   HIGH   — hardcode warna (hex/rgba/hsl) → harus jadi CSS variable
#   MEDIUM — pixel value di properti layout → kandidat Tailwind utility
#   SKIP   — display, visibility, dll → conditional rendering, diabaikan
#
_INLINE_STYLE_ATTR = re.compile(
    r'style\s*=\s*(?:"([^"]*?)"|\'([^\']*?)\')',
    re.IGNORECASE
)

_COLOR_HEX  = re.compile(r'#[0-9a-fA-F]{3,8}\b')
_COLOR_RGBA = re.compile(r'(?:rgba?|hsla?)\([^)]+\)')

# MEDIUM: pixel / rem / em / % pada properti layout spesifik
_PIXEL_PROP = re.compile(
    r'(?:margin|padding|width|height|top|right|bottom|left|gap|'
    r'font-size|line-height|border-width|border-radius|letter-spacing)'
    r'\s*:\s*'
    r'([\d.]+(?:px|rem|em|%|vw|vh)(?:\s+[\d.]+(?:px|rem|em|%|vw|vh))*)',
    re.IGNORECASE
)

# SKIP: properti conditional rendering dan utilitas — diabaikan
_SKIP_PROPS = re.compile(
    r'^\s*(?:display|visibility|opacity|pointer-events|user-select|'
    r'overflow|position|cursor|float|clear|content|z-index|'
    r'flex|grid|white-space|word-break|text-overflow)\s*:',
    re.IGNORECASE
)


def scan_inline_styles(content: str) -> list[dict]:
    """
    Scan semua atribut style="" dalam HTML.
    Klasifikasi: HIGH (warna hardcode) | MEDIUM (pixel layout) | SKIP (diabaikan).
    """
    issues = []

    for m in _INLINE_STYLE_ATTR.finditer(content):
        raw = (m.group(1) or m.group(2) or "").strip()
        if not raw:
            continue

        # Lewati atribut yang sepenuhnya berisi properti SKIP
        declarations = [d.strip() for d in raw.split(";") if d.strip()]
        non_skip = [d for d in declarations if not _SKIP_PROPS.match(d)]
        if not non_skip:
            continue

        attr_preview = raw[:120] + ("…" if len(raw) > 120 else "")

        # HIGH: warna hardcode
        hex_vals  = _COLOR_HEX.findall(raw)
        rgba_vals = _COLOR_RGBA.findall(raw)

        if hex_vals:
            issues.append({"severity": "high", "category": "color_hex",
                            "attribute": attr_preview, "values": hex_vals})
        if rgba_vals:
            issues.append({"severity": "high", "category": "color_rgba",
                            "attribute": attr_preview, "values": rgba_vals})

        # MEDIUM: pixel value — hanya jika belum di-flag HIGH (hindari duplikat)
        if not hex_vals and not rgba_vals:
            non_skip_str = "; ".join(non_skip)
            px_vals = _PIXEL_PROP.findall(non_skip_str)
            if px_vals:
                issues.append({"severity": "medium", "category": "pixel_value",
                                "attribute": attr_preview, "values": list(px_vals)})

    return issues


# ─── File scanner ─────────────────────────────────────────────────────────────

def scan_file(path: Path, root: Path) -> FileReport:
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        report = FileReport(path=str(path), rel_path=str(path.relative_to(root)))
        report.issues.append(f"Read error: {e}")
        return report

    report = FileReport(
        path=str(path),
        rel_path=str(path.relative_to(root)),
    )

    # CSS blocks
    css_raws = extract_blocks(content, 'style')
    for css in css_raws:
        report.css_blocks.append(asdict(parse_css_block(css)))

    # JS blocks
    js_raws = extract_blocks(content, 'script')
    for js in js_raws:
        parsed = parse_js_block(js)
        if parsed.raw_lines > 1:   # skip empty/trivial blocks
            report.js_blocks.append(asdict(parsed))

    # Tailwind classes
    report.tailwind_classes = extract_tailwind(content)

    # Django tags
    report.django_tags = extract_django_tags(content)

    # Issues
    if not css_raws:
        report.issues.append("Tidak ada <style> block")
    if not js_raws:
        report.issues.append("Tidak ada <script> block")

    # Inline style audit — 3 severity levels
    #   HIGH   : hardcode warna (hex / rgba) → harus jadi CSS variable
    #   MEDIUM : pixel value (margin, padding, width, dll) → kandidat Tailwind
    #   SKIP   : display / visibility / opacity utilitas → dibiarkan
    report.inline_style_issues = scan_inline_styles(content)

    # Surfacing high-severity ke issues agar terlihat di summary
    high = [i for i in report.inline_style_issues if i["severity"] == "high"]
    med  = [i for i in report.inline_style_issues if i["severity"] == "medium"]
    if high:
        report.issues.append(f"[HIGH] {len(high)} inline style dengan hardcode warna")
    if med:
        report.issues.append(f"[MEDIUM] {len(med)} inline style dengan pixel value hardcode")

    return report


# ─── Cross-file analysis ──────────────────────────────────────────────────────

def analyze_tokens(reports: list[FileReport]) -> dict:
    """
    Aggregate semua token dari semua file.
    Return dict per category: value → [files yang pakai]
    """
    aggregated = defaultdict(lambda: defaultdict(list))

    for r in reports:
        for css_block in r.css_blocks:
            for category, values in css_block.get('tokens', {}).items():
                for val in values:
                    aggregated[category][val.lower()].append(r.rel_path)

    # Convert ke format yang mudah dibaca
    result = {}
    for category, value_map in aggregated.items():
        entries = []
        for val, files in sorted(value_map.items(), key=lambda x: -len(x[1])):
            entries.append({
                "value"     : val,
                "count"     : len(files),
                "files"     : files,
                "candidate" : len(files) >= 2,   # muncul di 2+ file = kandidat token
            })
        result[category] = entries

    return result


def find_css_inconsistencies(reports: list[FileReport]) -> list[dict]:
    """
    Cari CSS class yang sama tapi nilai propertinya beda antar file.
    Misal: .nav-item di navbar.html vs sidebar.html — apakah identik?
    """
    class_definitions = defaultdict(dict)   # class_name → {file: css_snippet}

    for r in reports:
        full_content = ""
        try:
            full_content = Path(r.path).read_text(encoding='utf-8')
        except:
            continue

        css_raws = extract_blocks(full_content, 'style')
        for css in css_raws:
            # Extract class definitions dengan propertinya
            class_body = re.finditer(
                r'\.([\w-]+)\s*\{([^}]+)\}', css, re.DOTALL
            )
            for m in class_body:
                cls_name = m.group(1)
                body     = re.sub(r'\s+', ' ', m.group(2).strip())
                class_definitions[cls_name][r.rel_path] = body

    inconsistencies = []
    for cls_name, file_map in class_definitions.items():
        if len(file_map) < 2:
            continue
        bodies = list(file_map.values())
        if len(set(bodies)) > 1:   # nilai berbeda
            inconsistencies.append({
                "class"   : f".{cls_name}",
                "files"   : list(file_map.keys()),
                "variants": [
                    {"file": f, "definition": b}
                    for f, b in file_map.items()
                ]
            })

    return sorted(inconsistencies, key=lambda x: x['class'])


def find_root_candidates(token_analysis: dict) -> list[dict]:
    """
    Filter token candidates yang paling layak jadi CSS variable di :root.
    Prioritas: muncul di banyak file, bukan utility value, bukan warna very light.
    """
    candidates = []
    SKIP_VALUES = {'transparent','inherit','none','auto','initial','currentcolor',
                   '#fff','#ffffff','white','black','#000','#000000'}

    for category, entries in token_analysis.items():
        for e in entries:
            if not e['candidate']:
                continue
            val = e['value'].lower().strip()
            if val in SKIP_VALUES:
                continue
            # Skip very light colors (background tints)
            if category == 'color_hex':
                # skip jika ini warna light (em-50 sampai em-200, slate-50, dll)
                light_patterns = ['#ecfdf5','#d1fae5','#a7f3d0','#f0fdf4',
                                  '#f8fafc','#f1f5f9','#e2e8f0','#dbeafe',
                                  '#fef3c7','#fee2e2']
                if val in light_patterns:
                    continue

            suggested_name = suggest_var_name(category, e['value'])
            candidates.append({
                "category"      : category,
                "value"         : e['value'],
                "count"         : e['count'],
                "files"         : e['files'],
                "suggested_var" : suggested_name,
            })

    return sorted(candidates, key=lambda x: (-x['count'], x['category']))


def suggest_var_name(category: str, value: str) -> str:
    """Suggest a CSS variable name for a given token value."""
    v = value.lower().strip()

    # Known emerald colors
    color_map = {
        '#047857': '--color-primary',
        '#059669': '--color-primary-light',
        '#022c22': '--color-primary-dark',
        '#065f46': '--color-primary-deeper',
        '#34d399': '--color-primary-accent',
        '#6ee7b7': '--color-primary-glow',
        '#d1fae5': '--color-primary-subtle',
        '#94a3b8': '--color-muted',
        '#64748b': '--color-muted-dark',
        '#475569': '--color-muted-darker',
        '#0f172a': '--color-neutral-900',
        '#1e293b': '--color-neutral-800',
        '#e2e8f0': '--color-neutral-200',
        '#f1f5f9': '--color-neutral-100',
        '#f8fafc': '--color-neutral-50',
        '#ef4444': '--color-danger',
        '#f59e0b': '--color-warning',
    }
    if category in ('color_hex', 'color_rgba') and v in color_map:
        return color_map[v]

    prefix_map = {
        'border_radius' : '--radius',
        'box_shadow'    : '--shadow',
        'transition'    : '--transition',
        'font_size'     : '--font-size',
        'font_weight'   : '--font-weight',
        'backdrop'      : '--backdrop',
        'z_index'       : '--z',
        'opacity'       : '--opacity',
        'gradient'      : '--gradient',
    }
    return prefix_map.get(category, '--token') + '-' + re.sub(r'[^a-z0-9]', '-', v)[:30]


# ─── Report rendering ─────────────────────────────────────────────────────────

G   = '\033[92m'
Y   = '\033[93m'
C   = '\033[96m'
W   = '\033[97m'
R   = '\033[91m'
DIM = '\033[2m'
RST = '\033[0m'
B   = '\033[1m'


def print_file_summary(report: FileReport):
    print(f"\n  {B}{C}{report.rel_path}{RST}")

    css_count = len(report.css_blocks)
    js_count  = len(report.js_blocks)

    # CSS summary
    total_classes = sum(len(b.get('classes', [])) for b in report.css_blocks)
    total_anims   = sum(len(b.get('animations', [])) for b in report.css_blocks)
    all_colors    = set()
    for b in report.css_blocks:
        all_colors.update(b.get('tokens', {}).get('color_hex', []))
        all_colors.update(b.get('tokens', {}).get('color_rgba', []))

    print(f"    {DIM}CSS{RST}  {css_count} block  ·  {total_classes} class  ·  "
          f"{total_anims} animasi  ·  {len(all_colors)} unique color")

    # JS summary
    all_funcs = []
    all_fetches = []
    total_js_lines = 0
    for b in report.js_blocks:
        all_funcs   += b.get('functions', []) + b.get('arrow_funcs', [])
        all_fetches += b.get('fetch_urls', [])
        total_js_lines += b.get('raw_lines', 0)

    if report.js_blocks:
        print(f"    {DIM}JS {RST}  {js_count} block  ·  {len(all_funcs)} function  ·  "
              f"{len(all_fetches)} fetch  ·  ~{total_js_lines} baris")

    # Inline style issues — per severity
    high_inline = [i for i in report.inline_style_issues if i["severity"] == "high"]
    med_inline  = [i for i in report.inline_style_issues if i["severity"] == "medium"]
    if high_inline:
        print(f"    {R}▲  [HIGH]   {len(high_inline)} inline style — warna hardcode{RST}")
        for i in high_inline[:3]:
            vals = ", ".join(i["values"][:4])
            print(f"       {DIM}{i['attribute'][:70]}  → {vals}{RST}")
        if len(high_inline) > 3:
            print(f"       {DIM}… {len(high_inline)-3} lainnya{RST}")
    if med_inline:
        print(f"    {Y}●  [MEDIUM] {len(med_inline)} inline style — pixel value hardcode{RST}")
        for i in med_inline[:2]:
            vals = ", ".join(i["values"][:4])
            print(f"       {DIM}{i['attribute'][:70]}  → {vals}{RST}")
        if len(med_inline) > 2:
            print(f"       {DIM}… {len(med_inline)-2} lainnya{RST}")

    # General issues
    for issue in report.issues:
        if not issue.startswith("[HIGH]") and not issue.startswith("[MEDIUM]"):
            print(f"    {Y}⚠  {issue}{RST}")


def print_token_candidates(candidates: list[dict], limit: int = 30):
    print(f"\n{C}{'─'*66}{RST}")
    print(f"  {B}KANDIDAT CSS VARIABLES (:root){RST}  — muncul di 2+ file\n")

    current_cat = None
    shown = 0
    for c in candidates:
        if shown >= limit:
            print(f"  {DIM}  … {len(candidates)-limit} kandidat lainnya (lihat JSON output){RST}")
            break
        if c['category'] != current_cat:
            current_cat = c['category']
            print(f"  {DIM}{current_cat.upper()}{RST}")
        files_str = ', '.join(
            Path(f).name for f in c['files'][:3]
        ) + (f' +{len(c["files"])-3}' if len(c['files']) > 3 else '')
        print(f"    {G}{c['suggested_var']:<35}{RST}  {W}{c['value']:<30}{RST}  "
              f"{DIM}×{c['count']}  [{files_str}]{RST}")
        shown += 1


def print_inconsistencies(inconsistencies: list[dict], limit: int = 15):
    if not inconsistencies:
        print(f"\n  {G}✅ Tidak ada CSS class dengan definisi berbeda antar file.{RST}")
        return

    print(f"\n{C}{'─'*66}{RST}")
    print(f"  {B}INKONSISTENSI CSS CLASS{RST}  — class sama, nilai beda\n")
    for inc in inconsistencies[:limit]:
        print(f"  {Y}{inc['class']}{RST}  ({len(inc['files'])} file)")
        for v in inc['variants'][:3]:
            fname = Path(v['file']).name
            defn  = v['definition'][:80] + ('…' if len(v['definition']) > 80 else '')
            print(f"    {DIM}{fname:<20}{RST}  {defn}")
        print()
    if len(inconsistencies) > limit:
        print(f"  {DIM}… {len(inconsistencies)-limit} inkonsistensi lainnya (lihat JSON){RST}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def is_skip(path: Path) -> bool:
    return any(p in path.stem.lower() for p in SKIP_PATTERNS)


def find_files(root: Path, target: Optional[str] = None) -> list[Path]:
    if target:
        return [f for f in root.rglob(f"*{target}*")
                if f.suffix == '.html' and not is_skip(f)]
    return [f for f in sorted(root.rglob("*.html")) if not is_skip(f)]


def main():
    ap = argparse.ArgumentParser(description='Lumra CSS/JS Scanner')
    ap.add_argument('--root',    type=str, default=None,
                    help='Root template directory')
    ap.add_argument('--file',    type=str, default=None,
                    help='Filter by filename substring')
    ap.add_argument('--output',  type=str, default=None,
                    help='Save full JSON report to file')
    ap.add_argument('--summary', action='store_true',
                    help='Print per-file summary only')
    ap.add_argument('--tokens',  action='store_true',
                    help='Show token candidates only')
    ap.add_argument('--diff',    action='store_true',
                    help='Show CSS inconsistencies only')
    args = ap.parse_args()

    root = Path(args.root) if args.root else DEFAULT_ROOT
    if not root.exists():
        print(f"\n{R}❌ Root tidak ditemukan: {root}{RST}")
        print(f"   Gunakan --root <path> untuk menentukan direktori template.\n")
        sys.exit(1)

    print(f"\n{C}{'═'*66}{RST}")
    print(f"  {W}Lumra CSS/JS Scanner{RST}")
    print(f"{C}{'═'*66}{RST}  Root: {DIM}{root}{RST}\n")

    files = find_files(root, args.file)
    if not files:
        print(f"{Y}  ⚠  Tidak ada file HTML ditemukan.{RST}\n")
        return

    print(f"  Scanning {len(files)} file...\n")

    reports = [scan_file(f, root) for f in files]

    # ── Per-file summary ──
    if not args.tokens and not args.diff:
        print(f"{C}{'─'*66}{RST}")
        print(f"  {B}PER-FILE SUMMARY{RST}\n")
        for r in reports:
            print_file_summary(r)

    # ── Cross-file analysis ──
    token_analysis   = analyze_tokens(reports)
    root_candidates  = find_root_candidates(token_analysis)
    inconsistencies  = find_css_inconsistencies(reports)

    if not args.summary:
        if not args.diff:
            print_token_candidates(root_candidates)
        if not args.tokens:
            print_inconsistencies(inconsistencies)

    # ── Top-level stats ──
    print(f"\n{C}{'═'*66}{RST}")
    total_css = sum(len(r.css_blocks) for r in reports)
    total_js  = sum(len(r.js_blocks)  for r in reports)
    total_cls = sum(
        len(b.get('classes', []))
        for r in reports for b in r.css_blocks
    )
    print(f"  Files    : {W}{len(reports)}{RST}")
    print(f"  CSS block: {W}{total_css}{RST}  ·  Total class: {W}{total_cls}{RST}")
    print(f"  JS block : {W}{total_js}{RST}")
    print(f"  Kandidat :root token : {G}{len(root_candidates)}{RST}")
    print(f"  Inkonsistensi class  : {Y if inconsistencies else G}{len(inconsistencies)}{RST}")
    print(f"{C}{'═'*66}{RST}\n")

    # ── JSON output ──
    if args.output:
        out_path = Path(args.output)
        full_report = {
            "root"             : str(root),
            "files_scanned"    : len(reports),
            "reports"          : [asdict(r) for r in reports],
            "token_analysis"   : token_analysis,
            "root_candidates"  : root_candidates,
            "inconsistencies"  : inconsistencies,
        }
        out_path.write_text(
            json.dumps(full_report, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"  {G}✅ JSON report disimpan: {out_path}{RST}\n")


if __name__ == '__main__':
    main()