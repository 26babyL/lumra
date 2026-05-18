#!/usr/bin/env python3
"""
lumra_glass_audit.py  v2 — Glassmorphism Quality Scanner
=========================================================
Membaca lumra_ui_audit_data.json dan mengevaluasi setiap file HTML
berdasarkan 5 parameter kualitas glassmorphism.

PERUBAHAN dari v1:
  - P1: Deteksi var(--glass-blur*) sebagai valid blur (sebelumnya hanya blur(Npx) literal)
  - P2: Deteksi var(--glass-bg), var(--color-surface) sebagai valid transparency
  - P3: Deteksi border-white/N Tailwind + var(--glass-border)
  - P4: Deteksi var(--shadow-card), var(--glass-shadow) sebagai valid shadow
  - P5: Deteksi blob class di HTML attr + drift keyframe

5 PARAMETER:
    P1 — Backdrop Blur     : var(--glass-blur*) atau blur(10-24px)
    P2 — Transparansi      : var(--glass-bg) atau rgba opacity 0.3–0.85
    P3 — Frosted Edge      : border-white/N atau var(--glass-border)
    P4 — Natural Shadow    : var(--shadow-card) atau shadow-* Tailwind
    P5 — Layered Background: blob class, drift animation, gradient

CARA PAKAI:
    python lumra_glass_audit.py
    python lumra_glass_audit.py --data lumra_ui_audit_data.json
    python lumra_glass_audit.py --glass-only   # hanya file dengan glassmorphism
"""

import json
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ── Terminal ────────────────────────────────────────────────────
def _c(n): return f"\033[{n}m"
RST=_c(0); BOLD=_c(1); GRN=_c(32); YLW=_c(33); RED=_c(31); CYN=_c(36); DIM=_c(2)
def ok(m):   print(f"  {GRN}✓{RST}  {m}")
def warn(m): print(f"  {YLW}!{RST}  {m}")
def info(m): print(f"  {CYN}→{RST}  {m}")
def step(n, m): print(f"\n{BOLD}[{n}]{RST} {m}")
def banner(m):
    print(f"\n{BOLD}{'═'*62}{RST}\n{BOLD}  {m}{RST}\n{BOLD}{'═'*62}{RST}")


# ══════════════════════════════════════════════════════════════════
# TOKEN → VALUE MAPS (sinkron dengan design_system v2)
# ══════════════════════════════════════════════════════════════════

# Blur token → equivalent px
GLASS_BLUR_TOKENS: dict[str, float] = {
    '--glass-blur':      20.0,   # blur(20px) saturate(180%) — sweet spot
    '--glass-blur-sm':   10.0,   # blur(10px) saturate(160%) — sweet spot
    '--glass-blur-lg':   36.0,   # blur(36px) saturate(200%) — acceptable
    '--glass-dark-blur':  8.0,   # blur(8px) — acceptable
}

# Background token → alpha equivalent
GLASS_BG_TOKENS: dict[str, float] = {
    '--glass-bg':           0.72,
    '--glass-bg-strong':    0.94,
    '--glass-bg-subtle':    0.48,
    '--color-surface':      0.92,
    '--color-surface-strong': 0.99,
    '--color-surface-subtle': 0.60,
    '--glass-dark-bg':      0.42,
}

# Border tokens that indicate frosted edge
GLASS_BORDER_TOKENS = {
    '--glass-border', '--glass-border-em', '--glass-dark-border',
}

# Shadow tokens
GLASS_SHADOW_TOKENS = {
    '--glass-shadow', '--glass-shadow-lg', '--glass-shadow-glow',
    '--shadow-card', '--shadow-card-hover', '--shadow-dropdown',
    '--shadow-md', '--shadow-lg', '--shadow-xl', '--shadow-2xl',
}

# Blob/orb CSS classes that indicate layered background
BLOB_CLASSES = {
    'blob', 'blob-a', 'blob-b', 'blob-c',
    'bg-blob', 'bg-blob-1', 'bg-blob-2', 'bg-blob-3',
    'orb', 'orb-1', 'orb-2', 'orb-3',
    'sh-bg-orb', 'sh-bg-orb-1', 'sh-bg-orb-2', 'sh-bg-orb-3',
    'lumra-blob', 'lumra-blob-primary', 'lumra-blob-accent',
}

# Drift/float animation names
DRIFT_ANIMATIONS = {'drift', 'orb-drift', 'lumra-blob', 'float', 'breathe', 'pulse-glow'}

# Thresholds
BLUR_SWEET  = (10, 24)
BLUR_ACCP   = (6, 36)
ALPHA_SWEET = (0.30, 0.80)
ALPHA_ACCP  = (0.10, 0.94)

# Regexes
RE_BLUR_PX     = re.compile(r'blur\s*\(\s*([\d.]+)\s*px\s*\)')
RE_RGBA_BG     = re.compile(r'background(?:-color)?\s*:[^;]*rgba?\s*\([^)]+,\s*([\d.]+)\s*\)')
RE_VAR_BG      = re.compile(r'background(?:-color)?\s*:[^;]*var\s*\(\s*--([\w-]+)\s*\)')
RE_BORDER_RGBA = re.compile(r'border(?:-color)?\s*:[^;]*rgba?\s*\([^)]+\)')
RE_VAR_BORDER  = re.compile(r'border(?:-color)?\s*:[^;]*var\s*\(\s*--([\w-]+)\s*\)')
RE_CSS_SHADOW  = re.compile(r'box-shadow\s*:\s*([^;}{]{10,150})', re.DOTALL)
RE_SHADOW_HEAVY= re.compile(r'rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*([\d.]+)\)')
RE_GRADIENT    = re.compile(r'(?:linear|radial|conic)-gradient\s*\(')
RE_GRADIENT_TW = re.compile(r'bg-gradient-to-')
RE_TW_BG_OP    = re.compile(r'^bg-(?:white|slate|gray|black|neutral)/(\d+)$')
RE_TW_BORDER_OP= re.compile(r'^border-(?:white|slate-\d+)/\d+$')
RE_TW_SHADOW   = re.compile(r'^shadow(?:-(sm|md|lg|xl|2xl|inner))?$')


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _css_used_list(file_data: dict) -> list[str]:
    """Normalize css_vars_used to a list of var names."""
    cv = file_data.get('css_vars_used', {})
    if isinstance(cv, dict): return list(cv.keys())
    if isinstance(cv, list): return [str(v) for v in cv]
    return []


def _inline_text(file_data: dict) -> str:
    return ' '.join(str(s) for s in (file_data.get('inline_styles') or []))


def _tw_list(file_data: dict) -> list[str]:
    return [str(c) for c in (file_data.get('tw_colors') or [])]


def _backdrops(file_data: dict) -> list[str]:
    return [str(b) for b in (file_data.get('backdrop_filters') or [])]


# ══════════════════════════════════════════════════════════════════
# P1 — BACKDROP BLUR
# ══════════════════════════════════════════════════════════════════

def score_blur(fd: dict) -> dict:
    backdrops = _backdrops(fd)
    inline    = _inline_text(fd)

    blur_vals: list[float] = []

    # 1. var(--glass-blur*) token in backdrop_filters
    for bd in backdrops:
        for token, px in GLASS_BLUR_TOKENS.items():
            if token in bd:
                blur_vals.append(px)
        # Also literal px values
        for m in RE_BLUR_PX.finditer(bd):
            blur_vals.append(float(m.group(1)))

    # 2. Literal blur in inline styles
    for m in RE_BLUR_PX.finditer(inline):
        blur_vals.append(float(m.group(1)))

    # 3. var(--glass-blur) in inline backdrop-filter
    for token, px in GLASS_BLUR_TOKENS.items():
        if token in inline:
            blur_vals.append(px)

    if not blur_vals:
        return {'score': 0, 'max': 2, 'values': [],
                'verdict': '❌ Tidak ada backdrop-filter blur',
                'detail': 'Tambahkan backdrop-filter: var(--glass-blur) atau Tailwind backdrop-blur-xl'}

    sweet = [b for b in blur_vals if BLUR_SWEET[0] <= b <= BLUR_SWEET[1]]
    accp  = [b for b in blur_vals if BLUR_ACCP[0]  <= b <= BLUR_ACCP[1]]

    if sweet:
        return {'score': 2, 'max': 2, 'values': sorted(set(blur_vals)),
                'verdict': f'✅ Blur optimal ({min(sweet):.0f}–{max(sweet):.0f}px)',
                'detail': f'{len(blur_vals)} blur: {sorted(set(blur_vals))}px'}
    elif accp:
        return {'score': 1, 'max': 2, 'values': sorted(set(blur_vals)),
                'verdict': f'🟡 Blur di luar sweet spot ({min(blur_vals):.0f}px)',
                'detail': f'Sweet spot: 10–24px. Gunakan var(--glass-blur) = 20px'}
    else:
        return {'score': 0, 'max': 2, 'values': sorted(set(blur_vals)),
                'verdict': f'❌ Blur terlalu kecil/besar ({min(blur_vals):.0f}px)',
                'detail': 'Gunakan var(--glass-blur) atau backdrop-blur-xl'}


# ══════════════════════════════════════════════════════════════════
# P2 — TRANSPARANSI
# ══════════════════════════════════════════════════════════════════

def score_transparency(fd: dict) -> dict:
    inline   = _inline_text(fd)
    tw_list  = _tw_list(fd)
    css_used = _css_used_list(fd)

    alphas: list[float] = []

    # 1. var(--glass-bg*) token used → indicates correct transparency
    for token, alpha in GLASS_BG_TOKENS.items():
        if any(token in v for v in css_used) or token in inline:
            alphas.append(alpha)

    # 2. Literal rgba in inline style
    for m in RE_RGBA_BG.finditer(inline):
        alphas.append(float(m.group(1)))

    # 3. Tailwind bg-white/N
    for cls in tw_list:
        m = RE_TW_BG_OP.match(cls)
        if m:
            alphas.append(int(m.group(1)) / 100)

    if not alphas:
        return {'score': 0, 'max': 2, 'values': [],
                'verdict': '❌ Tidak ada transparansi background',
                'detail': 'Gunakan var(--glass-bg) atau bg-white/70'}

    sweet = [a for a in alphas if ALPHA_SWEET[0] <= a <= ALPHA_SWEET[1]]
    accp  = [a for a in alphas if ALPHA_ACCP[0]  <= a <= ALPHA_ACCP[1]]

    if sweet:
        return {'score': 2, 'max': 2, 'values': [round(a,2) for a in sorted(set(alphas))],
                'verdict': f'✅ Opacity tepat ({min(sweet):.2f}–{max(sweet):.2f})',
                'detail': f'{len(alphas)} alpha: {[round(a,2) for a in sorted(set(alphas))[:5]]}'}
    elif accp:
        return {'score': 1, 'max': 2, 'values': [round(a,2) for a in sorted(set(alphas))],
                'verdict': f'🟡 Opacity ada tapi extreme ({min(alphas):.2f}–{max(alphas):.2f})',
                'detail': 'Sweet spot opacity: 0.30–0.80'}
    else:
        return {'score': 0, 'max': 2, 'values': [round(a,2) for a in sorted(set(alphas))],
                'verdict': '❌ Opacity tidak sesuai',
                'detail': 'Gunakan rgba(255,255,255,0.72) atau var(--glass-bg)'}


# ══════════════════════════════════════════════════════════════════
# P3 — FROSTED EDGE
# ══════════════════════════════════════════════════════════════════

def score_frosted_edge(fd: dict) -> dict:
    inline   = _inline_text(fd)
    tw_list  = _tw_list(fd)
    css_used = _css_used_list(fd)

    # Token-aware: var(--glass-border) used
    has_border_token = any(t in css_used for t in GLASS_BORDER_TOKENS) or \
                       any(t in inline for t in GLASS_BORDER_TOKENS)

    # CSS rgba border in inline
    has_border_rgba = bool(RE_BORDER_RGBA.search(inline))

    # Tailwind: border-white/N, border-slate-N/N
    has_tw_border = any(RE_TW_BORDER_OP.match(cls) for cls in tw_list) or \
                    any(re.match(r'^border-white(?:/\d+)?$', cls) for cls in tw_list)

    sources = sum([has_border_token, has_border_rgba, has_tw_border])

    if sources >= 2:
        used = []
        if has_border_token:  used.append('CSS var')
        if has_border_rgba:   used.append('CSS rgba')
        if has_tw_border:     used.append('Tailwind')
        return {'score': 2, 'max': 2,
                'verdict': f'✅ Frosted border ({" + ".join(used)})',
                'detail': f'border token: {has_border_token}, rgba: {has_border_rgba}, tw: {has_tw_border}'}
    elif sources == 1:
        source = 'CSS var' if has_border_token else ('CSS rgba' if has_border_rgba else 'Tailwind')
        return {'score': 1, 'max': 2,
                'verdict': f'🟡 Frosted border sebagian ({source})',
                'detail': 'Tambahkan border-white/20 atau border: 1px solid var(--glass-border)'}
    else:
        return {'score': 0, 'max': 2,
                'verdict': '❌ Tidak ada frosted border',
                'detail': 'Tambahkan border: 1px solid var(--glass-border) atau class border-white/20'}


# ══════════════════════════════════════════════════════════════════
# P4 — NATURAL SHADOW
# ══════════════════════════════════════════════════════════════════

def score_shadow(fd: dict) -> dict:
    inline   = _inline_text(fd)
    tw_shads = fd.get('tw_shadows') or []
    css_used = _css_used_list(fd)

    # Token shadow: var(--shadow-card) etc
    has_token_shadow = any(t in css_used for t in GLASS_SHADOW_TOKENS) or \
                       any(t in inline for t in GLASS_SHADOW_TOKENS)

    # Tailwind shadow
    has_tw_shadow = bool(tw_shads)

    # Custom CSS shadow
    custom_shadows = RE_CSS_SHADOW.findall(inline)

    # Heavy black shadows (bad)
    heavy = [float(m.group(1))
             for s in custom_shadows
             for m in RE_SHADOW_HEAVY.finditer(s)
             if float(m.group(1)) > 0.30]

    if not (has_token_shadow or has_tw_shadow or custom_shadows):
        return {'score': 0, 'max': 2,
                'verdict': '❌ Tidak ada shadow',
                'detail': 'Tambahkan var(--shadow-card) atau class shadow-xl'}

    if has_token_shadow and not heavy:
        return {'score': 2, 'max': 2,
                'verdict': '✅ Shadow natural (CSS var)',
                'detail': f'Menggunakan design system shadow token'}
    elif heavy:
        return {'score': 1, 'max': 2,
                'verdict': f'🟡 Shadow terlalu pekat (opacity: {heavy})',
                'detail': 'Ganti rgba(0,0,0,0.5) → var(--shadow-card) atau rgba(0,0,0,0.06)'}
    elif has_tw_shadow:
        return {'score': 1, 'max': 2,
                'verdict': f'🟡 Shadow Tailwind ({tw_shads[:2]})',
                'detail': 'Pertimbangkan var(--shadow-card) untuk konsistensi'}
    else:
        return {'score': 1, 'max': 2,
                'verdict': '🟡 Shadow custom CSS',
                'detail': 'Cek apakah opacity cukup rendah'}


# ══════════════════════════════════════════════════════════════════
# P5 — LAYERED BACKGROUND
# ══════════════════════════════════════════════════════════════════

def score_layered_bg(fd: dict) -> dict:
    inline    = _inline_text(fd)
    tw_list   = _tw_list(fd)
    tw_str    = ' '.join(tw_list)
    keyframes = [str(k) for k in (fd.get('keyframes') or [])]
    css_vars  = fd.get('css_vars_defined') or []
    css_used  = _css_used_list(fd)

    # Blob classes in TW (HTML class attrs)
    has_blob = bool(BLOB_CLASSES & set(tw_list)) or \
               bool(re.search(r'\b(?:blob|orb|bg-blob|sh-bg-orb)\b', inline + tw_str, re.I))

    # Drift/float animation
    has_drift = any(k in DRIFT_ANIMATIONS for k in keyframes) or \
                any(re.search(r'drift|breathe|lumra-blob', k, re.I) for k in keyframes)

    # Gradient
    has_grad_css = bool(RE_GRADIENT.search(inline))
    has_grad_tw  = bool(RE_GRADIENT_TW.search(tw_str))

    # lumra-blob component class
    has_lumra_blob = 'lumra-blob' in tw_str or 'lumra-blob' in inline or \
                     any('lumra-blob' in str(v) for v in css_vars)

    signals = sum([has_blob, has_drift, has_grad_css, has_grad_tw, has_lumra_blob])

    if signals >= 2:
        detail_parts = []
        if has_blob:       detail_parts.append('blob class')
        if has_drift:      detail_parts.append('drift animation')
        if has_grad_css:   detail_parts.append('CSS gradient')
        if has_grad_tw:    detail_parts.append('TW gradient')
        if has_lumra_blob: detail_parts.append('lumra-blob')
        return {'score': 2, 'max': 2,
                'verdict': f'✅ Layered background ({", ".join(detail_parts)})',
                'detail': f'signals: {signals}'}
    elif signals == 1:
        return {'score': 1, 'max': 2,
                'verdict': '🟡 Layered background minimal',
                'detail': 'Tambahkan blob/gradient di belakang elemen glass'}
    else:
        return {'score': 0, 'max': 2,
                'verdict': '❌ Tidak ada layered background',
                'detail': 'Tambahkan <div class="blob blob-a"></div> atau lumra-blob class'}


# ══════════════════════════════════════════════════════════════════
# MASTER EVALUATOR
# ══════════════════════════════════════════════════════════════════

PARAM_LABELS = {
    'p1_blur':         'P1 — Backdrop Blur',
    'p2_transparency': 'P2 — Transparansi',
    'p3_frosted_edge': 'P3 — Frosted Edge',
    'p4_shadow':       'P4 — Natural Shadow',
    'p5_layered_bg':   'P5 — Layered Background',
}
PARAM_WEIGHT = {'p1_blur': 3, 'p2_transparency': 2,
                'p3_frosted_edge': 2, 'p4_shadow': 1, 'p5_layered_bg': 2}


def evaluate_file(fd: dict) -> dict:
    scores = {
        'p1_blur':         score_blur(fd),
        'p2_transparency': score_transparency(fd),
        'p3_frosted_edge': score_frosted_edge(fd),
        'p4_shadow':       score_shadow(fd),
        'p5_layered_bg':   score_layered_bg(fd),
    }
    weighted     = sum(scores[p]['score'] * w for p, w in PARAM_WEIGHT.items())
    max_weighted = sum(scores[p]['max']   * w for p, w in PARAM_WEIGHT.items())
    pct          = weighted / max_weighted * 100 if max_weighted else 0

    if pct >= 80:   grade, badge = 'A', '🏆 PREMIUM'
    elif pct >= 60: grade, badge = 'B', '✅ SOLID'
    elif pct >= 40: grade, badge = 'C', '🟡 PERLU PERBAIKAN'
    elif pct >= 20: grade, badge = 'D', '🔴 LEMAH'
    else:           grade, badge = 'F', '💀 TIDAK ADA GLASS'

    missing = [PARAM_LABELS[p].split(' — ')[1] for p, s in scores.items() if s['score'] == 0]
    partial = [PARAM_LABELS[p].split(' — ')[1] for p, s in scores.items() if s['score'] == 1]

    return {
        'file': fd['file'], 'scores': scores,
        'weighted': weighted, 'max_weighted': max_weighted,
        'pct': round(pct, 1), 'grade': grade, 'badge': badge,
        'missing': missing, 'partial': partial,
        'has_glass': 'glassmorphism' in (fd.get('components') or []),
    }


# ══════════════════════════════════════════════════════════════════
# WHAT-TO-FIX GENERATOR
# ══════════════════════════════════════════════════════════════════

# Pages that are partial/utility — don't need full glass treatment
EXEMPT_PREFIXES = {
    'base/alert', 'base/alert_inner', 'base/footer',
    'base/kpi_card_inner', 'base/kpi_card_white',
    'base/sidebar_item', 'base/partials/',
    'lumra_pages/etc/', 'lumra_pages/auth/register',
    'lumra_pages/reports/sales_report_after',
    'lumra_pages/master_data/customer.html',
    'lumra_pages/messages/inbox',
}

def is_exempt(file_path: str) -> bool:
    p = file_path.replace('\\', '/').split('templates/')[-1]
    return any(p.startswith(e) for e in EXEMPT_PREFIXES)


FIX_SNIPPETS = {
    'p1_blur': {
        'title': 'Tambah backdrop-filter blur',
        'css':   'backdrop-filter: var(--glass-blur);\n  -webkit-backdrop-filter: var(--glass-blur);',
        'tw':    'backdrop-blur-xl backdrop-saturate-150',
    },
    'p2_transparency': {
        'title': 'Perbaiki background transparency',
        'css':   'background: var(--glass-bg);  /* rgba(255,255,255,0.72) */',
        'tw':    'bg-white/70',
    },
    'p3_frosted_edge': {
        'title': 'Tambah frosted border',
        'css':   'border: 1px solid var(--glass-border);  /* rgba(255,255,255,0.82) */',
        'tw':    'border border-white/20',
    },
    'p4_shadow': {
        'title': 'Tambah natural shadow',
        'css':   'box-shadow: var(--shadow-card);',
        'tw':    'shadow-xl',
    },
    'p5_layered_bg': {
        'title': 'Tambah layered background',
        'html':  '<div class="blob blob-a" aria-hidden="true"></div>\n<div class="blob blob-b" aria-hidden="true"></div>',
        'note':  'Atau gunakan {% include "base/partials/bg_blob.html" %}',
    },
}


def generate_fix_plan(results: list[dict]) -> str:
    """Generate actionable fix instructions per file."""
    lines = [
        '# 🔧 Lumra Glass Fix Plan',
        '',
        f'> Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'> Files needing fix: {sum(1 for r in results if r["grade"] not in ("A",) and not is_exempt(r["file"]))}',
        '',
        '---',
        '',
    ]

    # Group by what's needed
    by_fix = defaultdict(list)
    for r in results:
        if r['grade'] == 'A' or is_exempt(r['file']):
            continue
        for p in list(r['missing']) + list(r['partial']):
            by_fix[p].append(r)

    lines += ['## 📋 Fix Dikelompokkan per Masalah', '']

    for param_name, affected in sorted(by_fix.items(), key=lambda x: -len(x[1])):
        # Find the param key
        param_key = next((k for k, v in PARAM_LABELS.items()
                         if v.split(' — ')[1] == param_name), None)
        if not param_key: continue
        snippet = FIX_SNIPPETS.get(param_key, {})

        lines += [
            f'### {param_name} — {len(affected)} file',
            '',
        ]
        if 'css' in snippet:
            lines += [f'**CSS fix:**', '```css', snippet['css'], '```', '']
        if 'tw' in snippet:
            lines += [f'**Tailwind fix:** `{snippet["tw"]}`', '']
        if 'html' in snippet:
            lines += [f'**HTML fix:**', '```html', snippet['html'], '```', '']
        if 'note' in snippet:
            lines += [f'> {snippet["note"]}', '']

        lines += ['**Files:**', '']
        for r in sorted(affected, key=lambda x: x['pct'])[:20]:
            short = r['file'].replace('\\', '/').split('templates/')[-1]
            is_missing = param_name in r['missing']
            tag = '❌ missing' if is_missing else '🟡 partial'
            lines.append(f'- `{short}` — {tag} ({r["pct"]:.0f}%)')
        lines += ['', '']

    # Per-file action plan for worst files
    lines += ['---', '', '## 🔴 Per-File Action Plan (Grade D/F)', '']
    df_files = [r for r in results
                if r['grade'] in ('D', 'F') and not is_exempt(r['file'])]
    df_files.sort(key=lambda x: x['pct'])

    for r in df_files[:30]:
        short = r['file'].replace('\\', '/').split('templates/')[-1]
        lines += [
            f'### `{short}` — {r["pct"]:.0f}% ({r["grade"]})',
            '',
        ]
        if r['missing']:
            lines.append(f'**Tidak ada:** {", ".join(r["missing"])}')
        if r['partial']:
            lines.append(f'**Partial:** {", ".join(r["partial"])}')
        lines += ['']

        for p_name in r['missing']:
            pk = next((k for k,v in PARAM_LABELS.items() if v.split(' — ')[1]==p_name), None)
            if pk and pk in FIX_SNIPPETS:
                s = FIX_SNIPPETS[pk]
                if 'css' in s:
                    lines += [f'*{p_name}:* `{s["css"].split(chr(10))[0]}`']
                elif 'html' in s:
                    lines += [f'*{p_name}:* `{s["html"].split(chr(10))[0]}`']
        lines += ['']

    return '\n'.join(lines)


# ══════════════════════════════════════════════════════════════════
# MARKDOWN REPORT
# ══════════════════════════════════════════════════════════════════

def generate_report(results: list, meta: dict) -> str:
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    L   = []

    grade_c = defaultdict(int)
    for r in results:
        grade_c[r['grade']] += 1

    avg_pct = sum(r['pct'] for r in results) / len(results) if results else 0
    sorted_r = sorted(results, key=lambda x: -x['pct'])

    L += [
        '# 🔬 Lumra — Glassmorphism Quality Audit v2',
        '', f'> **Tanggal**: {now}  ',
        f'> **File dievaluasi**: {len(results)}  ',
        f'> **Versi**: token-aware scoring (var(--glass-blur*) dikenali)',
        '', '---', '',
        '## 📊 Executive Summary', '',
        '| Metrik | Nilai |',
        '|--------|-------|',
        f'| Skor rata-rata | **{avg_pct:.1f}%** |',
        f'| 🏆 Grade A (Premium ≥80%) | **{grade_c["A"]}** file |',
        f'| ✅ Grade B (Solid 60–79%) | **{grade_c["B"]}** file |',
        f'| 🟡 Grade C (Needs fix 40–59%) | **{grade_c["C"]}** file |',
        f'| 🔴 Grade D/F (<40%) | **{grade_c["D"]+grade_c["F"]}** file |',
        '',
    ]

    # Distribution
    total = len(results)
    L.append('### Distribusi Grade\n')
    for g, emoji, label in [('A','🏆','Premium'),('B','✅','Solid'),
                              ('C','🟡','Perlu Fix'),('D','🔴','Lemah'),('F','💀','No Glass')]:
        n   = grade_c[g]
        pct = n / total * 100 if total else 0
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        L.append(f'`{g}` {emoji} `{bar}` {n} file ({pct:.1f}%)')

    # Parameter analysis
    param_scores = defaultdict(list)
    for r in results:
        for p, s in r['scores'].items():
            param_scores[p].append(s['score'])

    L += ['', '---', '', '## 🔍 Analisis Per Parameter', '',
          '| Parameter | Avg | ❌ | 🟡 | ✅ | Gap Utama |',
          '|-----------|-----|----|----|----|-----------| ']
    GAPS = {
        'p1_blur':         'Backdrop-filter tidak ada atau literal px (sudah migrasi → var token)',
        'p2_transparency': 'Background solid, bukan var(--glass-bg) atau rgba semi-transparan',
        'p3_frosted_edge': 'Tidak ada border semi-transparan — tambah border-white/20',
        'p4_shadow':       'Tidak ada shadow — tambah var(--shadow-card)',
        'p5_layered_bg':   'Tidak ada blob/gradient background — tambah include bg_blob.html',
    }
    for p, label in PARAM_LABELS.items():
        vals = param_scores[p]
        avg  = sum(vals)/len(vals) if vals else 0
        c0, c1, c2 = vals.count(0), vals.count(1), vals.count(2)
        short = label.split(' — ')[1]
        L.append(f'| **{short}** | {avg:.1f} | {c0} | {c1} | {c2} | {GAPS[p]} |')

    # Top files
    L += ['', '---', '', '## 🏆 Best Practice Files (Grade A)', '',
          '| File | Skor | Keunggulan |',
          '|------|------|------------|']
    for r in [x for x in sorted_r if x['grade']=='A'][:15]:
        strengths = [PARAM_LABELS[p].split('—')[1].strip()
                     for p, s in r['scores'].items() if s['score']==2]
        short = r['file'].replace('\\','/').split('templates/')[-1]
        L.append(f'| `{short}` | {r["pct"]:.0f}% | {", ".join(strengths[:3])} |')

    # Files needing fix
    needs_fix = [r for r in sorted_r if r['grade'] not in ('A','B') and not is_exempt(r['file'])]
    if needs_fix:
        L += ['', '---', '', f'## 🔧 Files Perlu Fix ({len(needs_fix)} file)', '',
              '| File | Skor | Missing | Partial |',
              '|------|------|---------|---------|']
        for r in needs_fix:
            short   = r['file'].replace('\\','/').split('templates/')[-1]
            missing = ', '.join(r['missing'][:3]) or '—'
            partial = ', '.join(r['partial'][:2]) or '—'
            L.append(f'| `{short}` | **{r["pct"]:.0f}%** | {missing} | {partial} |')

    # Detail per folder
    L += ['', '---', '', '## 📋 Detail Per Folder', '']
    by_folder = defaultdict(list)
    for r in sorted_r:
        folder = r['file'].replace('\\','/').split('/')
        folder = folder[0] if len(folder)==1 else '/'.join(folder[:2])
        folder = folder.split('templates/')[-1]
        by_folder[folder].append(r)

    for folder in sorted(by_folder.keys()):
        frs  = by_folder[folder]
        favg = sum(r['pct'] for r in frs) / len(frs)
        fg   = '🏆' if favg>=80 else '✅' if favg>=60 else '🟡' if favg>=40 else '🔴'
        L += [f'### {fg} `{folder}/` — avg {favg:.0f}%', '',
              '| File | Blur | Transp | Frosted | Shadow | Layer | Score | Grade |',
              '|------|------|--------|---------|--------|-------|-------|-------|']
        for r in frs:
            def cell(p):
                s = r['scores'][p]['score']
                return '✅' if s==2 else '🟡' if s==1 else '❌'
            fname = r['file'].replace('\\','/').split('/')[-1]
            L.append(f'| `{fname}` | {cell("p1_blur")} | {cell("p2_transparency")} | '
                     f'{cell("p3_frosted_edge")} | {cell("p4_shadow")} | {cell("p5_layered_bg")} | '
                     f'**{r["pct"]:.0f}%** | {r["grade"]} |')
        L.append('')

    L += ['---', '', f'*Dibuat `lumra_glass_audit.py` v2 — {now}*']
    return '\n'.join(L)


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description='Lumra Glassmorphism Quality Audit v2')
    p.add_argument('--data',       '-d', default='lumra_ui_audit_data.json')
    p.add_argument('--output',     '-o', default='lumra_glass_audit_report.md')
    p.add_argument('--fix-output', '-f', default='lumra_glass_fix_plan.md')
    p.add_argument('--glass-only', action='store_true')
    p.add_argument('--min-score',  type=int, default=0)
    args = p.parse_args()

    banner('LUMRA GLASSMORPHISM QUALITY AUDIT  v2')

    # Load
    data_path = Path(args.data)
    for candidate in [data_path, Path('lumra_ui_audit_data.json')]:
        if candidate.exists():
            data_path = candidate
            break
    else:
        print(f'  ✗ File tidak ditemukan: {args.data}')
        sys.exit(1)

    info(f'Loading: {data_path}')
    with open(data_path, encoding='utf-8') as f:
        data = json.load(f)

    html_files = data.get('html_files', [])
    meta       = data.get('meta', {})
    ok(f'Loaded {len(html_files)} file HTML')

    # Filter
    targets = [f for f in html_files if 'glassmorphism' in (f.get('components') or [])] \
              if args.glass_only else html_files
    if args.glass_only:
        info(f'Filter glass-only: {len(targets)} dari {len(html_files)} file')

    # Evaluate
    step(1, f'Evaluasi {len(targets)} file...')
    results = []
    for fd in targets:
        if 'error' in fd: continue
        r = evaluate_file(fd)
        if r['pct'] >= args.min_score:
            results.append(r)

    # Summary
    gc = defaultdict(int)
    for r in results: gc[r['grade']] += 1

    ok(f'Selesai — {len(results)} file dievaluasi')
    print()
    for g in ['A','B','C','D','F']:
        bar = '█' * gc[g] + '░' * max(0, 20 - gc[g])
        label = {'A':'Premium','B':'Solid','C':'Needs Fix','D':'Weak','F':'No Glass'}[g]
        print(f'  {g} {bar} {gc[g]:>3} file  ({label})')

    avg = sum(r['pct'] for r in results) / len(results) if results else 0
    print(f'\n  Rata-rata: {avg:.1f}%')

    # Write reports
    step(2, 'Generate laporan...')
    Path(args.output).write_text(generate_report(results, meta), encoding='utf-8')
    ok(f'Audit report: {args.output}')

    Path(args.fix_output).write_text(generate_fix_plan(results), encoding='utf-8')
    ok(f'Fix plan: {args.fix_output}')

    banner('SELESAI')
    print(f'\n  Grade A: {gc["A"]} file  |  Perlu fix: {gc["C"]+gc["D"]+gc["F"]} file\n')


if __name__ == '__main__':
    main()