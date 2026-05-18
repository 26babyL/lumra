#!/usr/bin/env python3
"""
lumra_ui_audit.py — UI Audit & Inventory Scanner
=================================================
Memindai SEMUA file HTML, Views Python, dan Models Django,
lalu menyimpan data mentah ke JSON dan menghasilkan laporan .md.

CARA PAKAI:
    # Jalankan dari folder lumra (berisi manage.py)
    python lumra_ui_audit.py

    # Atau tentukan path
    python lumra_ui_audit.py --project-dir D:\\APPS\\Project\\lumra

OUTPUT:
    lumra_ui_audit_data.json   ← data mentah lengkap (bisa dibuka ulang)
    lumra_ui_audit_report.md   ← laporan siap baca

APA YANG DISCAN:
    HTML  → warna hex, tailwind classes, komponen, inline styles,
            animasi, CSS variables, JS libraries, ikon, font
    Views → template yang digunakan per view function, model imports
    Models→ nama field, tipe data, relasi, db_table
"""

import os
import re
import json
import sys
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# ── Terminal colors ─────────────────────────────────────────
def _c(n): return f"\033[{n}m"
RST=_c(0); BOLD=_c(1); GRN=_c(32); YLW=_c(33); CYN=_c(36); RED=_c(31)
def ok(m):   print(f"  {GRN}✓{RST}  {m}")
def warn(m): print(f"  {YLW}!{RST}  {m}")
def info(m): print(f"  {CYN}→{RST}  {m}")
def step(n, m): print(f"\n{BOLD}[{n}]{RST} {m}")
def banner(m):
    print(f"\n{BOLD}{'═'*60}{RST}")
    print(f"{BOLD}  {m}{RST}")
    print(f"{BOLD}{'═'*60}{RST}")


# ══════════════════════════════════════════════════════════════
# BAGIAN 1 — SCANNER HTML
# ══════════════════════════════════════════════════════════════

# Regex
RE_HEX          = re.compile(r'(?<![&\w])#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
RE_RGB          = re.compile(r'rgba?\s*\(\s*[\d.,\s%]+\)')
RE_TW_CLASS_ALL = re.compile(r'class=["\']([^"\']*)["\']|:class=["\']([^"\']*)["\']')
RE_TW_COLOR     = re.compile(
    r'\b(?:bg|text|border|ring|from|to|via|fill|stroke|shadow|outline|decoration|accent|caret|divide)-'
    r'((?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|white|black|transparent|current)'
    r'(?:-\d+(?:\/\d+)?)?)\b'
)
RE_TW_SPACING   = re.compile(r'\b(?:p|m|px|py|mx|my|pt|pb|pl|pr|mt|mb|ml|mr|gap|space-[xy])-(\d+|px|auto|full)\b')
RE_TW_TEXT      = re.compile(r'\btext-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|8xl|9xl)\b')
RE_TW_ROUNDED   = re.compile(r'\brounded(?:-(none|sm|md|lg|xl|2xl|3xl|full))?\b')
RE_TW_SHADOW    = re.compile(r'\bshadow(?:-(none|sm|md|lg|xl|2xl|inner))?\b')
RE_TW_OPACITY   = re.compile(r'\bopacity-(\d+)\b')
RE_TW_TRANSITION= re.compile(r'\btransition(?:-(none|all|colors|opacity|shadow|transform))?\b')
RE_TW_ANIMATE   = re.compile(r'\banimate-(spin|ping|pulse|bounce|none|[\w-]+)\b')
RE_TW_FLEX      = re.compile(r'\bflex(?:-(?:row|col|wrap|nowrap|1|auto|none|shrink|grow))?\b')
RE_TW_GRID      = re.compile(r'\bgrid(?:-cols-(?:\d+|none))?\b')
RE_TW_Z         = re.compile(r'\bz-(\d+|auto)\b')
RE_INLINE_STYLE = re.compile(r'\bstyle=["\']([^"\']{1,200})["\']')
RE_CSS_VAR_DEF  = re.compile(r'--([\w-]+)\s*:', )
RE_CSS_VAR_USE  = re.compile(r'var\(--([\w-]+)\)')
RE_KEYFRAME     = re.compile(r'@keyframes\s+([\w-]+)')
RE_ANIMATION    = re.compile(r'animation(?:-name)?:\s*([\w,\s-]+?)(?:[;\s{]|$)')
RE_CSS_PROP     = re.compile(r'(?:^|\{|;)\s*([\w-]+)\s*:', re.MULTILINE)
RE_TRANSITION   = re.compile(r'transition:\s*([^;}]{1,100})')
RE_FONT_FAMILY  = re.compile(r'font-family\s*:\s*([^;}"\']{1,80})')
RE_BACKDROP     = re.compile(r'backdrop-filter\s*:\s*([^;}"\']{1,80})')
RE_SCRIPT_SRC   = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.I)
RE_ICON_FA      = re.compile(r'\b(?:fa[srb]?|fa)\s+fa-([\w-]+)\b')
RE_ICON_ANY     = re.compile(r'\b(?:bi|ri|ph|si|ti|mi|ci|mdi|material-icons)-?([\w-]+)\b')
RE_EXTENDS      = re.compile(r'\{%\s*extends\s+["\']([^"\']+)["\']')
RE_INCLUDE      = re.compile(r'\{%\s*include\s+["\']([^"\']+)["\']')
RE_BLOCK        = re.compile(r'\{%\s*block\s+([\w]+)')
RE_ALPINE       = re.compile(r'\bx-data=|\bx-show=|\bx-if=|\b@click=|\bx-model=')
RE_HTMX         = re.compile(r'\bhx-get=|\bhx-post=|\bhx-swap=')

KNOWN_LIBS = {
    'alpine':      re.compile(r'alpine', re.I),
    'chart.js':    re.compile(r'chart\.js|chart\.min', re.I),
    'flatpickr':   re.compile(r'flatpickr', re.I),
    'apexcharts':  re.compile(r'apexcharts', re.I),
    'sweetalert':  re.compile(r'sweetalert|swal', re.I),
    'select2':     re.compile(r'select2', re.I),
    'datatables':  re.compile(r'datatable', re.I),
    'sortable':    re.compile(r'sortable', re.I),
    'axios':       re.compile(r'axios', re.I),
    'htmx':        re.compile(r'htmx', re.I),
    'jquery':      re.compile(r'jquery', re.I),
    'dropzone':    re.compile(r'dropzone', re.I),
    'quill':       re.compile(r'quill', re.I),
    'tom-select':  re.compile(r'tom-select', re.I),
}

COMP_PATTERNS = {
    'table':             re.compile(r'<table[\s>]'),
    'thead':             re.compile(r'<thead[\s>]'),
    'form':              re.compile(r'<form[\s>]'),
    'input_text':        re.compile(r'<input[^>]+type=["\']text["\']'),
    'input_number':      re.compile(r'<input[^>]+type=["\']number["\']'),
    'input_search':      re.compile(r'type=["\']search["\']|name=["\']q["\']'),
    'input_select':      re.compile(r'<select[\s>]'),
    'input_textarea':    re.compile(r'<textarea[\s>]'),
    'input_file':        re.compile(r'<input[^>]+type=["\']file["\']'),
    'input_checkbox':    re.compile(r'<input[^>]+type=["\']checkbox["\']'),
    'button':            re.compile(r'<button[\s>]'),
    'modal':             re.compile(r'(?:modal|x-show.*modal|dialog)', re.I),
    'dropdown':          re.compile(r'dropdown|x-show.*drop', re.I),
    'sidebar':           re.compile(r'sidebar|aside\b', re.I),
    'navbar':            re.compile(r'navbar|<nav\b', re.I),
    'breadcrumb':        re.compile(r'breadcrumb', re.I),
    'pagination':        re.compile(r'pagination|page.*next|page.*prev', re.I),
    'badge':             re.compile(r'\bbadge\b', re.I),
    'alert':             re.compile(r'\balert\b|\bnotice\b', re.I),
    'toast':             re.compile(r'\btoast\b', re.I),
    'card':              re.compile(r'\bcard\b|\bkpi\b', re.I),
    'tab':               re.compile(r'\btabs?\b|\btab-panel\b', re.I),
    'accordion':         re.compile(r'accordion', re.I),
    'tooltip':           re.compile(r'tooltip|title=', re.I),
    'progress_bar':      re.compile(r'progress', re.I),
    'avatar':            re.compile(r'\bavatar\b', re.I),
    'chart':             re.compile(r'Chart\(|ApexCharts|chartjs', re.I),
    'datepicker':        re.compile(r'flatpickr|datepicker|date-picker', re.I),
    'datatable':         re.compile(r'DataTable|datatables', re.I),
    'search_command':    re.compile(r'command.*palette|cmd.*palette|cmdk', re.I),
    'glassmorphism':     re.compile(r'backdrop-filter|glass|bg-white/\d|bg-slate/\d'),
    'animation_scroll':  re.compile(r'reveal|scroll.*anim|on-scroll', re.I),
    'skeleton_loader':   re.compile(r'skeleton|shimmer|loading.*pulse', re.I),
}


def scan_html_file(filepath: Path, templates_root: Path) -> dict:
    """Scan satu file HTML, return dict data."""
    rel = str(filepath.relative_to(templates_root))
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return {'file': rel, 'error': str(e)}

    result = {
        'file': rel,
        'size_kb': round(filepath.stat().st_size / 1024, 1),
        'lines': content.count('\n'),
    }

    # ── Extends / Includes / Blocks ────────────────────────
    result['extends']  = RE_EXTENDS.findall(content)
    result['includes'] = RE_INCLUDE.findall(content)
    result['blocks']   = RE_BLOCK.findall(content)

    # ── Hex colors ─────────────────────────────────────────
    result['hex_colors'] = [('#' + m.upper()) for m in RE_HEX.findall(content)]

    # ── RGB colors ─────────────────────────────────────────
    result['rgb_colors'] = RE_RGB.findall(content)

    # ── Tailwind classes — collect all, then categorize ───
    all_classes = []
    for m in RE_TW_CLASS_ALL.finditer(content):
        raw = m.group(1) or m.group(2) or ''
        all_classes.extend(raw.split())

    result['tw_colors']     = [c for c in all_classes if RE_TW_COLOR.match(c)]
    result['tw_spacing']    = [c for c in all_classes if RE_TW_SPACING.match(c)]
    result['tw_text_sizes'] = [c for c in all_classes if RE_TW_TEXT.match(c)]
    result['tw_rounded']    = [c for c in all_classes if RE_TW_ROUNDED.match(c)]
    result['tw_shadows']    = [c for c in all_classes if RE_TW_SHADOW.match(c)]
    result['tw_opacity']    = [c for c in all_classes if RE_TW_OPACITY.match(c)]
    result['tw_transitions']= [c for c in all_classes if RE_TW_TRANSITION.match(c)]
    result['tw_animate']    = [c for c in all_classes if RE_TW_ANIMATE.match(c)]
    result['tw_flex']       = [c for c in all_classes if RE_TW_FLEX.match(c)]
    result['tw_grid']       = [c for c in all_classes if RE_TW_GRID.match(c)]
    result['tw_z_index']    = [c for c in all_classes if RE_TW_Z.match(c)]

    # ── Inline styles ──────────────────────────────────────
    inline_raw = RE_INLINE_STYLE.findall(content)
    result['inline_styles'] = inline_raw
    result['inline_style_count'] = len(inline_raw)

    # ── CSS within <style> tags ────────────────────────────
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.I)
    css_text = '\n'.join(style_blocks)

    result['css_vars_defined'] = RE_CSS_VAR_DEF.findall(css_text)
    result['css_vars_used']    = RE_CSS_VAR_USE.findall(content)
    result['keyframes']        = RE_KEYFRAME.findall(css_text)
    result['animations']       = [a.strip() for a in RE_ANIMATION.findall(css_text)]
    result['transitions_css']  = [t.strip() for t in RE_TRANSITION.findall(css_text)]
    result['font_families']    = RE_FONT_FAMILY.findall(css_text)
    result['backdrop_filters'] = RE_BACKDROP.findall(content)
    result['css_properties']   = list(set(RE_CSS_PROP.findall(css_text)))

    # ── JS Libraries ──────────────────────────────────────
    script_srcs = RE_SCRIPT_SRC.findall(content)
    libs_found = []
    for name, pattern in KNOWN_LIBS.items():
        if pattern.search(content):
            libs_found.append(name)
    result['js_libraries'] = libs_found
    result['script_srcs']  = script_srcs

    # Alpine & HTMX usage (count, not just boolean)
    result['alpine_directives'] = len(RE_ALPINE.findall(content))
    result['htmx_directives']   = len(RE_HTMX.findall(content))

    # ── Icons ─────────────────────────────────────────────
    fa_icons = RE_ICON_FA.findall(content)
    result['icons_fa']    = fa_icons
    result['icons_other'] = RE_ICON_ANY.findall(content)
    result['svg_inline']  = len(re.findall(r'<svg\b', content))

    # ── Components ────────────────────────────────────────
    found_comps = []
    for comp, pattern in COMP_PATTERNS.items():
        if pattern.search(content):
            found_comps.append(comp)
    result['components'] = found_comps

    # ── Has inline script ─────────────────────────────────
    inline_scripts = re.findall(r'<script(?![^>]+src=)[^>]*>(.*?)</script>',
                                  content, re.DOTALL | re.I)
    result['has_inline_script'] = len(inline_scripts) > 0
    result['inline_script_count'] = len(inline_scripts)

    return result


def scan_all_html(templates_dir: Path) -> list:
    results = []
    all_files = sorted(templates_dir.rglob('*.html'))
    info(f"Ditemukan {len(all_files)} file HTML")
    for fp in all_files:
        r = scan_html_file(fp, templates_dir)
        results.append(r)
    return results


# ══════════════════════════════════════════════════════════════
# BAGIAN 2 — SCANNER VIEWS
# ══════════════════════════════════════════════════════════════

def scan_views(views_dir: Path) -> list:
    results = []
    for pyfile in sorted(views_dir.glob('*.py')):
        if pyfile.name.startswith('_'):
            continue
        try:
            src = pyfile.read_text(encoding='utf-8', errors='replace')
        except:
            continue

        # Split by function
        blocks = re.split(r'\n(?=(?:@\w|\s*def ))', src)
        for block in blocks:
            m = re.search(r'def (\w+)\s*\(request', block)
            if not m:
                continue
            fname = m.group(1)
            if fname.startswith('_'):
                continue

            # Template used
            tmpl_m = re.search(r"render\s*\([^,]+,\s*['\"]([^'\"]+)['\"]", block)

            # Models imported/used
            models_used = sorted(set(re.findall(
                r'\b(Category|Vendor|Tax|Unit|Location|Product|ProductVariant|'
                r'ProductAttribute|Stock|Requisition|RequisitionItem|Transfer|TransferItem|'
                r'UserProfile|Customer|Order|OrderItem|ProductDetail|StockOpnameSession|'
                r'StockOpnameItem|RecipeCategory|Recipe|RecipeIngredient|SupplierPrice)\b',
                block
            )))

            # HTTP methods
            methods = ['GET']
            if "request.POST" in block or "method == 'POST'" in block or 'method ==" POST"' in block:
                methods = ['GET', 'POST']

            # JsonResponse
            returns_json = 'JsonResponse' in block or 'json_response' in block.lower()

            # login_required
            auth = '@login_required' in block or 'login_required' in block[:200]

            # Queryset operations
            qs_ops = sorted(set(re.findall(r'\.(?:filter|exclude|get|all|annotate|aggregate|order_by|select_related|prefetch_related)\(', block)))

            results.append({
                'function': fname,
                'source_file': pyfile.name,
                'template': tmpl_m.group(1) if tmpl_m else None,
                'models_used': models_used,
                'methods': methods,
                'returns_json': returns_json,
                'auth_required': auth,
                'queryset_ops': qs_ops,
            })

    return results


# ══════════════════════════════════════════════════════════════
# BAGIAN 3 — SCANNER MODELS
# ══════════════════════════════════════════════════════════════

def scan_models(models_file: Path) -> list:
    if not models_file.exists():
        return []
    src = models_file.read_text(encoding='utf-8', errors='replace')

    results = []
    classes = re.findall(r'^class (\w+)\(', src, re.MULTILINE)

    for cls in classes:
        # Get class body
        body_m = re.search(
            rf'class {cls}\b.*?(?=\nclass |\Z)', src, re.DOTALL
        )
        if not body_m:
            continue
        body = body_m.group(0)

        # db_table
        tbl_m = re.search(r"db_table\s*=\s*['\"]([^'\"]+)['\"]", body)
        db_table = tbl_m.group(1) if tbl_m else f'lumra_config_{cls.lower()}'

        # Fields
        fields = []
        for fm in re.finditer(r'^\s{4}(\w+)\s*=\s*models\.(\w+)\(([^)]*)\)', body, re.MULTILINE):
            fname, ftype, fargs = fm.groups()
            if fname in ('Meta', 'id'):
                continue

            # FK target
            fk_to = None
            fk_m = re.search(r"['\"]([A-Z]\w+)['\"]|^(\w+)", fargs)
            if ftype in ('ForeignKey', 'OneToOneField', 'ManyToManyField') and fk_m:
                fk_to = fk_m.group(1) or fk_m.group(2)

            # null/blank/default
            null    = 'null=True'    in fargs
            blank   = 'blank=True'   in fargs
            default = re.search(r'default=([^,)]+)', fargs)

            fields.append({
                'name':    fname,
                'type':    ftype,
                'fk_to':   fk_to,
                'null':    null,
                'blank':   blank,
                'default': default.group(1).strip() if default else None,
            })

        # Methods defined
        methods = re.findall(r'def ([\w]+)\s*\(self', body)

        # Meta ordering
        ordering_m = re.search(r'ordering\s*=\s*\[([^\]]+)\]', body)

        results.append({
            'model': cls,
            'db_table': db_table,
            'fields': fields,
            'methods': methods,
            'ordering': ordering_m.group(1).strip() if ordering_m else None,
            'field_count': len(fields),
        })

    return results


# ══════════════════════════════════════════════════════════════
# BAGIAN 4 — SCAN URLS
# ══════════════════════════════════════════════════════════════

def scan_urls(urls_file: Path) -> list:
    if not urls_file.exists():
        return []
    src = urls_file.read_text(encoding='utf-8', errors='replace')
    entries = []
    for m in re.finditer(
        r"path\s*\(\s*'([^']*)'\s*,\s*\n?\s*lazy_view\s*\(\s*'lumra_config\.(\w+)\.views\.(\w+)'\s*\)"
        r"\s*,?\s*\n?\s*(?:name\s*=\s*'(\w+)')?\s*\)",
        src, re.DOTALL
    ):
        url, app, func, name = m.groups()
        entries.append({
            'url': '/' + url,
            'app': app,
            'view_func': func,
            'url_name': name or func,
        })
    return entries


# ══════════════════════════════════════════════════════════════
# BAGIAN 5 — AGGREGATE DATA
# ══════════════════════════════════════════════════════════════

def aggregate(html_results: list) -> dict:
    """Gabungkan semua hasil scan HTML menjadi summary."""
    agg = {
        'hex_colors':       Counter(),
        'rgb_colors':       Counter(),
        'tw_colors':        Counter(),
        'tw_spacing':       Counter(),
        'tw_text_sizes':    Counter(),
        'tw_rounded':       Counter(),
        'tw_shadows':       Counter(),
        'tw_opacity':       Counter(),
        'tw_animate':       Counter(),
        'tw_z_index':       Counter(),
        'css_vars_defined': Counter(),
        'css_vars_used':    Counter(),
        'keyframes':        Counter(),
        'animations':       Counter(),
        'transitions':      Counter(),
        'font_families':    Counter(),
        'backdrop_filters': Counter(),
        'components':       Counter(),   # comp → count of files
        'js_libraries':     Counter(),
        'icons_fa':         Counter(),
        'files_with_inline': [],
        'inline_style_total': 0,
        'svg_total':        0,
        'alpine_total':     0,
        'htmx_total':       0,
        'files_per_comp':   defaultdict(list),
        'extends_map':      Counter(),
        'includes_used':    Counter(),
    }

    for r in html_results:
        if 'error' in r:
            continue
        f = r['file']

        for k in ['hex_colors','rgb_colors','tw_colors','tw_spacing','tw_text_sizes',
                  'tw_rounded','tw_shadows','tw_opacity','tw_animate','tw_z_index']:
            agg[k].update(r.get(k, []))

        for k in ['css_vars_defined','css_vars_used','keyframes','animations','font_families','backdrop_filters']:
            agg[k].update(r.get(k, []))

        agg['transitions'].update(r.get('transitions_css', []))
        agg['js_libraries'].update(r.get('js_libraries', []))
        agg['icons_fa'].update(r.get('icons_fa', []))

        for comp in r.get('components', []):
            agg['components'][comp] += 1
            agg['files_per_comp'][comp].append(f)

        if r.get('inline_style_count', 0) > 0:
            agg['files_with_inline'].append({
                'file': f,
                'count': r['inline_style_count'],
                'samples': r.get('inline_styles', [])[:3],
            })
        agg['inline_style_total'] += r.get('inline_style_count', 0)
        agg['svg_total']    += r.get('svg_inline', 0)
        agg['alpine_total'] += r.get('alpine_directives', 0)
        agg['htmx_total']   += r.get('htmx_directives', 0)

        for ext in r.get('extends', []):
            agg['extends_map'][ext] += 1
        for inc in r.get('includes', []):
            agg['includes_used'][inc] += 1

    # Sort files_with_inline by count desc
    agg['files_with_inline'].sort(key=lambda x: -x['count'])

    # Convert Counter to dict for JSON
    for k in list(agg.keys()):
        if isinstance(agg[k], Counter):
            agg[k] = dict(agg[k].most_common())
        elif isinstance(agg[k], defaultdict):
            agg[k] = dict(agg[k])

    return agg


# ══════════════════════════════════════════════════════════════
# BAGIAN 6 — GENERATE MARKDOWN
# ══════════════════════════════════════════════════════════════

def bar(n, max_n, w=18):
    if not max_n: return '░' * w
    f = int(n / max_n * w)
    return '█' * f + '░' * (w - f)

def sev(n, warn_at=50, crit_at=200):
    if n >= crit_at: return '🔴'
    if n >= warn_at:  return '🟡'
    return '🟢'

def generate_md(agg: dict, html_results: list, views: list,
                models: list, urls: list, meta: dict) -> str:
    L = []
    now = meta['scanned_at']
    total_html = meta['total_html']
    total_views = meta['total_views']
    total_models = meta['total_models']
    total_urls = meta['total_urls']

    L += [
        '# 🎨 Lumra ERP — UI Audit Report',
        '',
        f'> **Tanggal Scan**: {now}  ',
        f'> **HTML di-scan**: {total_html} file  ',
        f'> **View Functions**: {total_views}  ',
        f'> **Model Django**: {total_models}  ',
        f'> **URL Routes**: {total_urls}  ',
        '',
        '---',
        '',
        '## 📋 Daftar Isi',
        '',
        '1. [Executive Summary](#1-executive-summary)',
        '2. [Warna — Hex Hardcoded](#2-warna--hex-hardcoded)',
        '3. [Warna — Tailwind Classes](#3-warna--tailwind-classes)',
        '4. [Komponen UI](#4-komponen-ui)',
        '5. [CSS & Animasi](#5-css--animasi)',
        '6. [Inline Styles](#6-inline-styles)',
        '7. [JavaScript & Libraries](#7-javascript--libraries)',
        '8. [Ikon](#8-ikon)',
        '9. [Layout & Spacing](#9-layout--spacing)',
        '10. [Views → Template → Model](#10-views--template--model)',
        '11. [Model Database](#11-model-database)',
        '12. [Design Tokens yang Disarankan](#12-design-tokens-yang-disarankan)',
        '13. [Rekomendasi Prioritas](#13-rekomendasi-prioritas)',
        '',
        '---',
        '',
    ]

    # ── 1. Executive Summary ────────────────────────────────
    unique_hex = len(agg['hex_colors'])
    unique_tw  = len(agg['tw_colors'])
    inline_total = agg['inline_style_total']
    inline_files = len(agg['files_with_inline'])
    comp_count = len(agg['components'])

    L += [
        '## 1. Executive Summary',
        '',
        '| Metrik | Nilai | Status |',
        '|--------|-------|--------|',
        f'| File HTML di-scan | **{total_html}** | — |',
        f'| View Functions | **{total_views}** | — |',
        f'| Model Database | **{total_models}** | — |',
        f'| URL Routes | **{total_urls}** | — |',
        f'| Warna Hex unik (hardcoded) | **{unique_hex}** | {sev(unique_hex, 20, 50)} |',
        f'| Kelas warna Tailwind unik | **{unique_tw}** | {sev(unique_tw, 100, 200)} |',
        f'| Total inline `style=""` | **{inline_total:,}×** | {sev(inline_total, 100, 500)} |',
        f'| File dengan inline style | **{inline_files}** | {sev(inline_files, 20, 80)} |',
        f'| Jenis komponen UI | **{comp_count}** | 🟢 |',
        f'| CSS custom keyframe | **{len(agg["keyframes"])}** | — |',
        f'| CSS variable didefinisikan | **{len(agg["css_vars_defined"])}** | — |',
        f'| SVG inline | **{agg["svg_total"]}** | — |',
        f'| Alpine.js directives | **{agg["alpine_total"]:,}** | — |',
        '',
        '---', '',
    ]

    # ── 2. Hex Colors ───────────────────────────────────────
    hex_items = list(agg['hex_colors'].items())
    L += [
        '## 2. Warna — Hex Hardcoded',
        '',
        f'**{unique_hex} warna Hex unik** ditemukan tersebar di seluruh file HTML.',
        'Ini adalah warna yang di-hardcode langsung (bukan via Tailwind class).',
        '',
        '| Rank | Hex | Kemunculan | Termasuk Keluarga |',
        '|------|-----|------------|------------------|',
    ]

    COLOR_FAMILY_MAP = {
        '#059659': 'Emerald', '#059669': 'Emerald', '#10B981': 'Emerald',
        '#6EE7B7': 'Emerald', '#34D399': 'Emerald', '#D1FAE5': 'Emerald',
        '#065F46': 'Emerald', '#047857': 'Emerald',
        '#94A3B8': 'Slate', '#475569': 'Slate', '#1E293B': 'Slate',
        '#64748B': 'Slate', '#E2E8F0': 'Slate', '#CBD5E1': 'Slate',
        '#F1F5F9': 'Slate', '#0F172A': 'Slate', '#334155': 'Slate',
        '#6366F1': 'Indigo', '#4F46E5': 'Indigo', '#C7D2FE': 'Indigo',
        '#8B5CF6': 'Violet', '#7C3AED': 'Violet', '#6D28D9': 'Violet',
        '#0EA5E9': 'Sky', '#38BDF8': 'Sky',
        '#3B82F6': 'Blue', '#2563EB': 'Blue', '#BFDBFE': 'Blue',
        '#F59E0B': 'Amber', '#D97706': 'Amber', '#B45309': 'Amber',
        '#F43F5E': 'Rose', '#E11D48': 'Rose', '#BE185D': 'Rose',
        '#FFF': 'White', '#FFFFFF': 'White',
        '#000': 'Black', '#000000': 'Black',
    }
    for i, (color, count) in enumerate(hex_items[:40], 1):
        family = COLOR_FAMILY_MAP.get(color, '—')
        L.append(f'| {i} | `{color}` | {count}× | {family} |')

    if len(hex_items) > 40:
        L.append(f'| … | *+{len(hex_items)-40} warna lainnya* | | |')

    # Group by family
    family_totals = defaultdict(int)
    for color, count in hex_items:
        fam = COLOR_FAMILY_MAP.get(color, 'Lainnya')
        family_totals[fam] += count

    L += [
        '',
        '### Ringkasan per Keluarga Warna (Hex)',
        '',
        '| Keluarga | Total Kemunculan |',
        '|----------|-----------------|',
    ]
    for fam, total in sorted(family_totals.items(), key=lambda x: -x[1]):
        L.append(f'| {fam} | {total}× |')

    L += ['', '---', '']

    # ── 3. Tailwind Colors ──────────────────────────────────
    tw_items = list(agg['tw_colors'].items())
    tw_total_count = sum(v for _, v in tw_items)

    # Group by color family
    tw_family = defaultdict(int)
    for cls, n in tw_items:
        # extract family: text-slate-400 → slate
        parts = cls.split('-')
        color_part = None
        for p in parts[1:]:  # skip prefix
            if p in ('slate','gray','zinc','neutral','stone','red','orange','amber',
                     'yellow','lime','green','emerald','teal','cyan','sky','blue',
                     'indigo','violet','purple','fuchsia','pink','rose','white','black'):
                color_part = p
                break
        if color_part:
            tw_family[color_part] += n

    L += [
        '## 3. Warna — Tailwind Classes',
        '',
        f'**{unique_tw} kelas warna Tailwind unik**, total **{tw_total_count:,} kemunculan**.',
        '',
        '### 3.1 Top 40 Kelas Warna Tailwind',
        '',
        '| Rank | Class | Kemunculan | Prefix |',
        '|------|-------|------------|--------|',
    ]
    for i, (cls, n) in enumerate(tw_items[:40], 1):
        prefix = cls.split('-')[0]
        L.append(f'| {i} | `{cls}` | {n}× | `{prefix}` |')

    if len(tw_items) > 40:
        L.append(f'| … | *+{len(tw_items)-40} kelas lainnya* | | |')

    L += [
        '',
        '### 3.2 Distribusi Keluarga Warna Tailwind',
        '',
        '| Keluarga | Total | Proporsi |',
        '|----------|-------|----------|',
    ]
    tw_fam_sorted = sorted(tw_family.items(), key=lambda x: -x[1])
    max_tw_fam = tw_fam_sorted[0][1] if tw_fam_sorted else 1
    tw_grand_total = sum(v for _, v in tw_fam_sorted)
    for fam, n in tw_fam_sorted:
        pct = n / tw_grand_total * 100
        L.append(f'| `{fam}` | {n:,} | `{bar(n, max_tw_fam)}` {pct:.1f}% |')

    L += ['', '---', '']

    # ── 4. Components ───────────────────────────────────────
    comp_items = sorted(agg['components'].items(), key=lambda x: -x[1])
    L += [
        '## 4. Komponen UI',
        '',
        f'Ditemukan **{len(comp_items)} jenis komponen** di {total_html} file HTML.',
        '',
        '| Komponen | File | Penetrasi | Catatan |',
        '|----------|------|-----------|---------|',
    ]

    COMP_NOTES = {
        'button':          'Variasi gaya button perlu audit',
        'toast':           'Pattern JS toast berbeda-beda?',
        'navbar':          'Kemungkinan via base.html include',
        'card':            'Padding & shadow belum tentu seragam',
        'input_text':      'Perlu cek styling focus state',
        'input_select':    'Custom select atau native?',
        'form':            'CSRF token selalu ada?',
        'badge':           'Warna status badge konsisten?',
        'table':           'Gaya header/row berbeda per modul',
        'thead':           'Semua table punya thead?',
        'pagination':      'Satu pattern atau beragam?',
        'avatar':          'Fallback saat foto tidak ada?',
        'modal':           'Alpine x-show atau custom?',
        'chart':           'Chart.js — wrapper component?',
        'dropdown':        'Alpine dropdown — konsisten?',
        'datepicker':      'flatpickr — versi dikunci?',
        'breadcrumb':      'Struktur HTML seragam?',
        'glassmorphism':   'backdrop-filter — performa mobile?',
        'animation_scroll':'Reveal on scroll — konsisten?',
        'skeleton_loader': 'Loading state — ada standar?',
    }

    max_comp = comp_items[0][1] if comp_items else 1
    for comp, n in comp_items:
        pct = n / total_html * 100
        note = COMP_NOTES.get(comp, '—')
        L.append(f'| `{comp}` | **{n}** | `{bar(n, max_comp, 12)}` {pct:.0f}% | {note} |')

    L += ['', '---', '']

    # ── 5. CSS & Animasi ────────────────────────────────────
    kf_items = list(agg['keyframes'].items())
    cv_def   = list(agg['css_vars_defined'].items())
    cv_use   = list(agg['css_vars_used'].items())

    L += [
        '## 5. CSS & Animasi',
        '',
        '### 5.1 CSS Custom Variables yang Didefinisikan',
        '',
        '| Variable | Kemunculan |',
        '|----------|------------|',
    ]
    for var, n in sorted(cv_def, key=lambda x: -x[1]):
        L.append(f'| `--{var}` | {n}× |')

    L += [
        '',
        '### 5.2 CSS Custom Variables yang Digunakan (`var(--*)`)',
        '',
        '| Variable | Kemunculan |',
        '|----------|------------|',
    ]
    for var, n in sorted(cv_use, key=lambda x: -x[1])[:20]:
        L.append(f'| `--{var}` | {n}× |')

    L += [
        '',
        '### 5.3 Animasi (@keyframes)',
        '',
        '| Keyframe Name | Kemunculan | Tipe Efek |',
        '|---------------|------------|-----------|',
    ]
    ANIM_TYPE = {
        'drift': 'Float/ambient bg',
        'reveal': 'Scroll reveal',
        'shimmer': 'Skeleton loading',
        'slideIn': 'Panel masuk',
        'slideOut': 'Panel keluar',
        'slideUp': 'Elemen naik',
        'toastIn': 'Toast masuk',
        'toastOut': 'Toast keluar',
        'modalIn': 'Modal masuk',
        'mIn': 'Modal masuk (alias)',
        'spin': 'Loading spinner',
        'pulse': 'Pulse effect',
        'blink': 'Blink / kedip',
        'breathe': 'Breathing / gentle pulse',
        'barUp': 'Progress bar',
        'flashGreen': 'Flash sukses',
        'flashRed': 'Flash error',
        'ticker': 'Scroll text/marquee',
        'dropIn': 'Dropdown masuk',
        'confirmIn': 'Konfirmasi dialog',
    }
    for kf, n in sorted(kf_items, key=lambda x: -x[1]):
        atype = ANIM_TYPE.get(kf, '—')
        L.append(f'| `{kf}` | {n}× | {atype} |')

    # Backdrop filters
    bd_items = list(agg['backdrop_filters'].items())
    if bd_items:
        L += [
            '',
            '### 5.4 Backdrop Filters (Glassmorphism)',
            '',
            '| Filter | Kemunculan |',
            '|--------|------------|',
        ]
        for bd, n in sorted(bd_items, key=lambda x: -x[1])[:10]:
            L.append(f'| `{bd[:60]}` | {n}× |')

    # Font families
    font_items = list(agg['font_families'].items())
    if font_items:
        L += [
            '',
            '### 5.5 Font Families Ditemukan',
            '',
            '| Font | Kemunculan |',
            '|------|------------|',
        ]
        for ft, n in sorted(font_items, key=lambda x: -x[1])[:10]:
            L.append(f'| `{ft[:60].strip()}` | {n}× |')

    L += ['', '---', '']

    # ── 6. Inline Styles ────────────────────────────────────
    files_inline = agg['files_with_inline']
    L += [
        '## 6. Inline Styles',
        '',
        f'**{inline_total:,}** penggunaan `style=""` di **{inline_files}** file.',
        '',
        '> ⚠️ Inline styles tidak bisa di-override oleh CSS class, tidak konsisten,',
        '> dan tidak bisa diubah secara global. Ini adalah technical debt utama.',
        '',
        '| File | Jumlah `style=""` | Contoh |',
        '|------|-------------------|--------|',
    ]
    for item in files_inline[:30]:
        sample = item['samples'][0][:50].replace('|', '\\|') if item['samples'] else '—'
        L.append(f'| `{item["file"]}` | {item["count"]} | `{sample}` |')

    if len(files_inline) > 30:
        L.append(f'| *...+{len(files_inline)-30} file lainnya* | | |')

    L += ['', '---', '']

    # ── 7. JavaScript ───────────────────────────────────────
    js_items = list(agg['js_libraries'].items())
    L += [
        '## 7. JavaScript & Libraries',
        '',
        '| Library | File yang Menggunakan | Catatan |',
        '|---------|----------------------|---------|',
    ]
    JS_NOTES = {
        'alpine':     'Interaktivitas reaktif — sudah jadi standar ✅',
        'chart.js':   'Grafik — sudah standar ✅',
        'flatpickr':  'Date picker — sudah standar ✅',
        'apexcharts': 'Grafik alternatif — duplikat Chart.js?',
        'sweetalert': 'Alert dialog — konsisten?',
        'select2':    'Custom select — diganti Alpine?',
        'datatables': 'Table pagination JS',
        'sortable':   'Drag & drop sort',
        'axios':      'HTTP client (jika ada AJAX)',
        'htmx':       'HTML-over-the-wire',
        'jquery':     '⚠️ Legacy — perlu dihapus jika ada',
    }
    for lib, n in sorted(js_items, key=lambda x: -x[1]):
        note = JS_NOTES.get(lib, '—')
        L.append(f'| **{lib}** | {n} file | {note} |')

    L += [
        '',
        f'| Alpine directives total | {agg["alpine_total"]:,} | `x-data`, `x-show`, `@click`, dll |',
        f'| HTMX directives total | {agg["htmx_total"]:,} | `hx-get`, `hx-post`, dll |',
        '',
        '---', '',
    ]

    # ── 8. Icons ────────────────────────────────────────────
    icon_items = list(agg['icons_fa'].items())
    L += [
        '## 8. Ikon',
        '',
        f'**Font Awesome** adalah library ikon utama.',
        f'Ditemukan **{len(icon_items)} ikon unik**, total **{sum(v for _,v in icon_items):,}** kemunculan.',
        f'SVG inline: **{agg["svg_total"]}** elemen `<svg>`.',
        '',
        '### Top 40 Ikon Paling Sering Dipakai',
        '',
        '| Rank | Ikon | Kemunculan |',
        '|------|------|------------|',
    ]
    for i, (icon, n) in enumerate(icon_items[:40], 1):
        L.append(f'| {i} | `fa-{icon}` | {n}× |')

    L += ['', '---', '']

    # ── 9. Layout & Spacing ─────────────────────────────────
    flex_total = sum(agg.get('tw_colors', {}).get(c, 0)
                     for c in agg.get('tw_colors', {}))  # reuse
    # Count from all_classes
    spacing_items  = list(agg['tw_spacing'].items())
    textsize_items = list(agg['tw_text_sizes'].items())
    rounded_items  = list(agg['tw_rounded'].items())
    shadow_items   = list(agg['tw_shadows'].items())
    opacity_items  = list(agg['tw_opacity'].items())

    L += [
        '## 9. Layout & Spacing',
        '',
        '### 9.1 Spacing Paling Sering (p-*, m-*, gap-*, dll)',
        '',
        '| Class | Kemunculan |',
        '|-------|------------|',
    ]
    for cls, n in spacing_items[:20]:
        L.append(f'| `{cls}` | {n}× |')

    L += [
        '',
        '### 9.2 Ukuran Teks',
        '',
        '| Class | Kemunculan |',
        '|-------|------------|',
    ]
    for cls, n in textsize_items:
        L.append(f'| `{cls}` | {n}× |')

    L += [
        '',
        '### 9.3 Border Radius',
        '',
        '| Class | Kemunculan |',
        '|-------|------------|',
    ]
    for cls, n in rounded_items:
        L.append(f'| `{cls}` | {n}× |')

    L += [
        '',
        '### 9.4 Shadow',
        '',
        '| Class | Kemunculan |',
        '|-------|------------|',
    ]
    for cls, n in shadow_items:
        L.append(f'| `{cls}` | {n}× |')

    L += [
        '',
        '### 9.5 Opacity',
        '',
        '| Class | Kemunculan |',
        '|-------|------------|',
    ]
    for cls, n in sorted(opacity_items, key=lambda x: -x[1])[:15]:
        L.append(f'| `{cls}` | {n}× |')

    L += ['', '---', '']

    # ── 10. Views → Template → Model ───────────────────────
    # Build func → url map
    url_map = {e['view_func']: e for e in urls}

    L += [
        '## 10. Views → Template → Model',
        '',
        f'Total **{total_views} view functions** di {len(set(v["source_file"] for v in views))} file.',
        '',
    ]

    # Group by source file
    by_file = defaultdict(list)
    for v in views:
        by_file[v['source_file']].append(v)

    for srcfile in sorted(by_file.keys()):
        L += [f'### `{srcfile}`', '', '| Function | URL | Method | Template | Models | Auth |',
              '|----------|-----|--------|----------|--------|------|']
        for v in by_file[srcfile]:
            ue = url_map.get(v['function'], {})
            url_str  = ue.get('url', '—')
            tmpl     = v.get('template') or '—'
            tmpl_short = tmpl.split('/')[-1] if tmpl != '—' else '—'
            models_str = ', '.join(v.get('models_used', [])) or '—'
            methods  = ' / '.join(v.get('methods', ['GET']))
            auth     = '🔒' if v.get('auth_required') else '🌐'
            L.append(f'| `{v["function"]}` | `{url_str}` | {methods} | `{tmpl_short}` | {models} | {auth} |')
        L.append('')

    L += ['---', '']

    # ── 11. Models ──────────────────────────────────────────
    L += [
        '## 11. Model Database',
        '',
        f'Total **{total_models} model** di `lumra_config/models.py`.',
        '',
        '| Model | Tabel DB | Fields | Relasi |',
        '|-------|----------|--------|--------|',
    ]
    for m in models:
        fk_fields = [f['name'] for f in m['fields'] if f['type'] in ('ForeignKey', 'OneToOneField', 'ManyToManyField')]
        rel_str = ', '.join(f"`{f}`" for f in fk_fields) if fk_fields else '—'
        L.append(f'| `{m["model"]}` | `{m["db_table"]}` | {m["field_count"]} | {rel_str} |')

    L += ['']

    # Detail per model
    for m in models:
        L += [
            f'### `{m["model"]}` → `{m["db_table"]}`',
            '',
            '| Field | Tipe | FK ke | Null | Default |',
            '|-------|------|-------|------|---------|',
        ]
        for f in m['fields']:
            fk = f'`{f["fk_to"]}`' if f['fk_to'] else '—'
            null = '✓' if f['null'] else ''
            default = f'`{f["default"]}`' if f['default'] else '—'
            L.append(f'| `{f["name"]}` | `{f["type"]}` | {fk} | {null} | {default} |')
        if m.get('ordering'):
            L.append(f'')
            L.append(f'*Ordering: `{m["ordering"]}`*')
        L.append('')

    L += ['---', '']

    # ── 12. Design Tokens ───────────────────────────────────
    # Derive tokens from actual scan data
    hex_top = list(agg['hex_colors'].items())
    tw_top  = list(agg['tw_colors'].items())

    # Find dominant colors
    primary_hex   = hex_top[0][0] if hex_top else '#059669'
    primary2_hex  = hex_top[1][0] if len(hex_top) > 1 else '#10B981'
    neutral1_hex  = next((c for c,_ in hex_top if c in ('#1E293B','#0F172A','#334155')), '#1E293B')
    warning_hex   = next((c for c,_ in hex_top if c in ('#F59E0B','#D97706','#FBBF24')), '#F59E0B')
    danger_hex    = next((c for c,_ in hex_top if c in ('#F43F5E','#EF4444','#E11D48')), '#F43F5E')
    info_hex      = next((c for c,_ in hex_top if c in ('#0EA5E9','#3B82F6','#38BDF8')), '#0EA5E9')
    accent_hex    = next((c for c,_ in hex_top if c in ('#6366F1','#4F46E5','#8B5CF6')), '#6366F1')

    # Dominant keyframes for animation reference
    top_kf = [k for k,_ in sorted(agg['keyframes'].items(), key=lambda x: -x[1])[:5]]
    top_kf_str = ', '.join(f'`{k}`' for k in top_kf) if top_kf else '—'

    L += [
        '## 12. Design Tokens yang Disarankan',
        '',
        '> Berdasarkan data scan nyata — warna terbanyak digunakan dijadikan token.',
        '',
        '```css',
        ':root {',
        f'  /* ── Primary Color (dominan: {primary_hex}, {primary_hex[0:7]}) ─── */',
        f'  --color-primary:        {primary_hex};',
        f'  --color-primary-light:  {primary2_hex};',
        f'  --color-primary-subtle: #D1FAE5;',
        f'  --color-primary-dark:   #065F46;',
        '',
        f'  /* ── Neutral (Slate) ────────────────── */',
        f'  --color-neutral-950:    #020617;',
        f'  --color-neutral-900:    #0F172A;',
        f'  --color-neutral-800:    {neutral1_hex};',
        f'  --color-neutral-600:    #475569;',
        f'  --color-neutral-500:    #64748B;',
        f'  --color-neutral-400:    #94A3B8;',
        f'  --color-neutral-200:    #E2E8F0;',
        f'  --color-neutral-100:    #F1F5F9;',
        f'  --color-neutral-50:     #F8FAFC;',
        '',
        f'  /* ── Semantic ───────────────────────── */',
        f'  --color-success:        {primary_hex};',
        f'  --color-warning:        {warning_hex};',
        f'  --color-danger:         {danger_hex};',
        f'  --color-info:           {info_hex};',
        f'  --color-accent:         {accent_hex};',
        '',
        f'  /* ── Glassmorphism (dipakai di project ini) */',
        f'  --glass-bg:     rgba(255,255,255,0.72);',
        f'  --glass-border: rgba(255,255,255,0.9);',
        f'  --glass-blur:   blur(20px) saturate(160%);',
        '',
        f'  /* ── Typography ─────────────────────── */',
        f'  --font-body:    "Inter", sans-serif;',
        f'  --font-display: "Plus Jakarta Sans", sans-serif;',
        '',
        f'  /* ── Spacing (dari tw_spacing scan) ─── */',
        f'  --space-1:  0.25rem;',
        f'  --space-2:  0.5rem;',
        f'  --space-3:  0.75rem;',
        f'  --space-4:  1rem;',
        f'  --space-6:  1.5rem;',
        f'  --space-8:  2rem;',
        '',
        f'  /* ── Border Radius ──────────────────── */',
        f'  --radius-sm:   0.375rem;',
        f'  --radius-md:   0.5rem;',
        f'  --radius-lg:   0.75rem;',
        f'  --radius-xl:   1rem;',
        f'  --radius-full: 9999px;',
        '',
        f'  /* ── Shadow ─────────────────────────── */',
        f'  --shadow-sm:    0 1px 2px rgba(0,0,0,.05);',
        f'  --shadow-card:  0 2px 12px rgba(0,0,0,.06), 0 0 0 0.5px rgba(0,0,0,.04);',
        f'  --shadow-modal: 0 20px 60px rgba(0,0,0,.15);',
        '}',
        '```',
        '',
        f'**Animasi yang sudah ada** (jangan duplikasi): {top_kf_str}',
        '',
        '---', '',
    ]

    # ── 13. Rekomendasi ─────────────────────────────────────
    L += [
        '## 13. Rekomendasi Prioritas',
        '',
        '### 🔴 P1 — Kritis (Kerjakan Dulu)',
        '',
        '| # | Masalah | Data | Aksi |',
        '|---|---------|------|------|',
        f'| 1 | **{unique_hex} warna Hex hardcoded** | tersebar di {total_html} file | Pindah ke CSS `var(--color-*)` |',
        f'| 2 | **{inline_total:,} inline `style=""`** | di {inline_files} file | Refactor ke Tailwind/class |',
        f'| 3 | **{unique_tw} kelas warna Tailwind** | `gray`+`slate`+`zinc` overlap | Pilih 1 family: standar ke `slate` |',
        '',
        '### 🟡 P2 — Perlu Standarisasi',
        '',
        '| # | Komponen | File | Aksi |',
        '|---|----------|------|------|',
    ]
    # Top 5 components
    for i, (comp, n) in enumerate(comp_items[:5], 1):
        L.append(f'| {i} | `{comp}` | {n} file | Buat 1 component class / Django include |')

    L += [
        '',
        '### 🟢 P3 — Sudah Baik, Pertahankan',
        '',
        '- **Font Awesome** — ikon library tunggal ✅',
        '- **flatpickr** — date picker tunggal ✅',
        '- **Chart.js** — charting library tunggal ✅',
        '- **Alpine.js** — interaktivitas reaktif ✅',
        '- **Emerald + Slate** — palet warna sudah dominan (tinggal konsolidasi) ✅',
        '',
        '---',
        '',
        f'*Laporan dibuat otomatis oleh `lumra_ui_audit.py` pada {now}.*  ',
        '*Edit skrip untuk menambah pattern deteksi komponen baru.*',
    ]

    return '\n'.join(L)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def find_dir(base: Path, *candidates) -> Path:
    for c in candidates:
        p = base / c
        if p.exists():
            return p
    return None


def main():
    parser = argparse.ArgumentParser(description="Lumra UI Audit Scanner")
    parser.add_argument("--project-dir", "-p", default=".",
                        help="Folder root project lumra (default: folder sekarang)")
    parser.add_argument("--output-dir", "-o", default=".",
                        help="Folder output JSON dan MD (default: folder sekarang)")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    output_dir  = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    banner("LUMRA UI AUDIT SCANNER")
    print(f"  Project : {project_dir}")
    print(f"  Output  : {output_dir}")

    # ── Cari direktori ─────────────────────────────────────
    templates_dir = find_dir(project_dir,
        "lumra_config/templates",
        "lumra/lumra_config/templates",
    )
    views_dir = find_dir(project_dir,
        "lumra_config/views",
        "lumra/lumra_config/views",
    )
    models_file = None
    for c in ["lumra_config/models.py", "lumra/lumra_config/models.py"]:
        p = project_dir / c
        if p.exists():
            models_file = p
            break
    urls_file = None
    for c in ["lumra_system/urls.py", "lumra/lumra_system/urls.py"]:
        p = project_dir / c
        if p.exists():
            urls_file = p
            break

    if not templates_dir:
        print("  ✗ templates/ tidak ditemukan — jalankan dari folder lumra")
        sys.exit(1)

    ok(f"templates/  : {templates_dir}")
    ok(f"views/      : {views_dir or '(tidak ditemukan)'}")
    ok(f"models.py   : {models_file or '(tidak ditemukan)'}")
    ok(f"urls.py     : {urls_file or '(tidak ditemukan)'}")

    # ── SCAN ───────────────────────────────────────────────
    step(1, "Scan HTML templates...")
    html_results = scan_all_html(templates_dir)
    ok(f"{len(html_results)} file selesai di-scan")

    step(2, "Aggregate data HTML...")
    agg = aggregate(html_results)
    ok("Agregasi selesai")

    step(3, "Scan Views Python...")
    views = scan_views(views_dir) if views_dir else []
    ok(f"{len(views)} view functions ditemukan")

    step(4, "Scan Models Django...")
    models = scan_models(models_file) if models_file else []
    ok(f"{len(models)} model ditemukan")

    step(5, "Scan URLs...")
    urls = scan_urls(urls_file) if urls_file else []
    ok(f"{len(urls)} URL routes ditemukan")

    # ── SIMPAN JSON ────────────────────────────────────────
    step(6, "Simpan data mentah ke JSON...")
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_data = {
        'meta': {
            'scanned_at': now_str,
            'project_dir': str(project_dir),
            'total_html': len(html_results),
            'total_views': len(views),
            'total_models': len(models),
            'total_urls': len(urls),
        },
        'aggregate': agg,
        'html_files': html_results,
        'views': views,
        'models': models,
        'urls': urls,
    }
    json_path = output_dir / "lumra_ui_audit_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)
    ok(f"JSON disimpan: {json_path} ({json_path.stat().st_size // 1024} KB)")

    # ── GENERATE MARKDOWN ──────────────────────────────────
    step(7, "Generate laporan Markdown...")
    meta = full_data['meta']
    md = generate_md(agg, html_results, views, models, urls, meta)
    md_path = output_dir / "lumra_ui_audit_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    ok(f"MD disimpan : {md_path} ({md_path.stat().st_size // 1024} KB)")

    # ── RINGKASAN ──────────────────────────────────────────
    banner("SELESAI")
    print(f"""
  📄 Data mentah  : lumra_ui_audit_data.json
  📋 Laporan      : lumra_ui_audit_report.md

  Ringkasan cepat:
    HTML di-scan         : {len(html_results)} file
    Warna Hex unik       : {len(agg['hex_colors'])} warna
    Kelas Tailwind unik  : {len(agg['tw_colors'])} kelas
    Inline style=""      : {agg['inline_style_total']:,}× di {len(agg['files_with_inline'])} file
    Komponen ditemukan   : {len(agg['components'])} jenis
    Keyframe animasi     : {len(agg['keyframes'])} nama
    CSS variables        : {len(agg['css_vars_defined'])} didefinisikan
    """)


if __name__ == "__main__":
    main()