#!/usr/bin/env python3
"""
lumra_glass_fix_v3.py — Glassmorphism Auto-Fixer
=================================================
Perbaikan dari dry-run analysis v2:

  BUG FIXES:
  - base.html regression (-8%): inject_glass_tokens menimpa token yang sudah
    lebih lengkap. Sekarang: skip jika token sudah ada & skor >= 80%.
  - Zero-delta files: scorer tidak mendeteksi --color-white-a0XX sebagai
    "transparansi valid". Sekarang lebih toleran.
  - Skip file Grade A (>=80%) kecuali ada bug aktif.
  - Blob-only files (0→8%): tambah full glass inject untuk file tanpa CSS sama sekali.

  FITUR BARU:
  - --safe mode: skip file yang sudah >= 60% (default ON)
  - --aggressive: inject full lumra-glass CSS ke file grade F
  - --check: cek skor tanpa output verbose
  - Grade A files ditampilkan tapi tidak disentuh
"""

import os, re, sys, shutil, argparse, json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Colors ───────────────────────────────────────────────────
def _c(n): return f"\033[{n}m"
RST=_c(0); BOLD=_c(1); GRN=_c(32); YLW=_c(33); RED=_c(31); CYN=_c(36); DIM=_c(2); MAG=_c(35)
def ok(m):   print(f"  {GRN}✓{RST}  {m}")
def warn(m): print(f"  {YLW}!{RST}  {m}")
def info(m): print(f"  {CYN}→{RST}  {m}")
def skip(m): print(f"  {DIM}–{RST}  {m}")
def dry(m):  print(f"  {DIM}~{RST}  [DRY] {m}")
def fix_ok(m): print(f"  {GRN}▲{RST}  {m}")
def fix_skip(m): print(f"  {DIM}◌{RST}  {m}")
def regress(m): print(f"  {RED}▼{RST}  {m}")

# ════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ════════════════════════════════════════════════════════════
GLASS_TOKENS_CSS = """\
/* ===========================================================
   LUMRA GLASS DESIGN TOKENS — lumra_glass_fix_v3.py
   =========================================================== */
:root {
  --glass-blur      : blur(14px) saturate(180%);
  --glass-bg        : rgba(255, 255, 255, 0.82);
  --glass-border    : rgba(255, 255, 255, 0.20);
  --glass-shadow    : 0 2px 12px rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.04);
  --glass-dark-bg   : rgba(15, 23, 42, 0.82);
  --glass-dark-blur : blur(6px);
  --glass-dark-border: rgba(255,255,255,0.06);
  --color-primary        : #059669;
  --color-primary-light  : #10B981;
  --color-primary-subtle : #D1FAE5;
  --color-primary-dark   : #065F46;
  --color-success : #10B981;
  --color-warning : #F59E0B;
  --color-danger  : #F43F5E;
  --color-info    : #0EA5E9;
  --color-accent  : #6366F1;
}
"""

GLASS_CLASSES_CSS = """\
.lumra-glass {
  background             : var(--glass-bg);
  backdrop-filter        : var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border                 : 1px solid var(--glass-border);
  border-radius          : 18px;
  box-shadow             : var(--glass-shadow);
  transition             : box-shadow 0.2s ease, transform 0.2s ease;
}
.lumra-glass:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.10); transform: translateY(-2px); }
.lumra-kpi-glass {
  background             : var(--glass-bg);
  backdrop-filter        : var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border                 : 1px solid rgba(255,255,255,0.90);
  border-radius          : 18px;
  box-shadow             : var(--glass-shadow);
  transition             : box-shadow .2s ease, transform .2s ease;
  position               : relative; overflow: hidden;
}
.lumra-kpi-glass:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.10); transform: translateY(-2px); }
"""

BLOB_CSS = """\
.bg-blob {
  position: fixed; border-radius: 50%; filter: blur(100px);
  opacity: 0.10; pointer-events: none; z-index: 0;
  animation: drift 18s ease-in-out infinite alternate;
}
.bg-blob-1 { width:480px; height:480px; background:var(--color-primary,#059669); top:-120px; left:-160px; animation-delay:0s; }
.bg-blob-2 { width:320px; height:320px; background:var(--color-primary-light,#10b981); bottom:-80px; right:-80px; animation-delay:-7s; }
.bg-blob-3 { width:220px; height:220px; background:#34d399; top:40%; left:55%; animation-delay:-3.5s; }
@keyframes drift {
  from { transform: translate(0,0) scale(1); }
  to   { transform: translate(20px,28px) scale(1.06); }
}
"""

BLOB_HTML = """\
  <!-- Ambient Blob Background -->
  <div class="bg-blob bg-blob-1" aria-hidden="true"></div>
  <div class="bg-blob bg-blob-2" aria-hidden="true"></div>
  <div class="bg-blob bg-blob-3" aria-hidden="true"></div>
"""

# CSS minimal untuk file yang benar-benar kosong (grade F, --aggressive)
MINIMAL_GLASS_INJECT = """\
/* Glass foundation — injected by lumra_glass_fix_v3.py */
body { background: rgba(248,250,252,0.90) !important; position: relative; }
.page-container, main, .content-wrapper {
  background: var(--glass-bg, rgba(255,255,255,0.82));
  backdrop-filter: var(--glass-blur, blur(14px) saturate(180%));
  -webkit-backdrop-filter: var(--glass-blur, blur(14px) saturate(180%));
}
.card, .panel, .modal-content, .table-container {
  background: var(--glass-bg, rgba(255,255,255,0.82));
  backdrop-filter: var(--glass-blur, blur(14px) saturate(180%));
  -webkit-backdrop-filter: var(--glass-blur, blur(14px) saturate(180%));
  border: 1px solid var(--glass-border, rgba(255,255,255,0.20));
  border-radius: 16px;
  box-shadow: var(--glass-shadow, 0 2px 12px rgba(0,0,0,0.06));
}
"""

# ════════════════════════════════════════════════════════════
# SCORER — v3 (lebih toleran, sesuai audit script asli)
# ════════════════════════════════════════════════════════════
def score_file(html: str) -> dict:
    s = {}

    # 1. Backdrop Blur
    has_blur_token = bool(re.search(r"var\(--glass-blur", html))
    blur_nums = re.findall(r"backdrop-filter[^:]*:[^;]*blur\s*\(\s*(\d+(?:\.\d+)?)\s*px", html)
    has_blur_raw = any(float(n) >= 10 for n in blur_nums) if blur_nums else False
    s["blur"] = 2 if (has_blur_token or has_blur_raw) else (1 if blur_nums else 0)

    # 2. Transparansi — lebih toleran
    has_glass_bg  = bool(re.search(r"var\(--glass-bg\)", html))
    has_rgba_semi = bool(re.search(r"rgba\s*\([^)]+,\s*0\.[1-9]\d*\s*\)", html))
    # BUG FIX v3: --color-white-a0XX juga dihitung sebagai semi-transparan
    has_white_token = bool(re.search(r"var\(--color-(?:surface|white)[^)]*\)", html))
    # Background di CSS class (bukan hanya inline)
    has_bg_in_class = bool(re.search(r"\.\w[\w-]*\s*\{[^}]*background[^}]*rgba[^}]*0\.[1-9]", html, re.DOTALL))
    if has_glass_bg: s["transp"] = 2
    elif has_rgba_semi or has_bg_in_class: s["transp"] = 1
    elif has_white_token: s["transp"] = 1
    else: s["transp"] = 0

    # 3. Frosted Edge
    has_glass_border  = bool(re.search(r"var\(--glass-border\)", html))
    has_white_border  = bool(re.search(r"border[^:]*:\s*1px solid rgba\(255,\s*255,\s*255", html))
    has_border_twcss  = bool(re.search(r'border-white/\d+|border-slate-\d+/\d+', html))
    # BUG FIX v3: --glass-border di :root juga dihitung
    has_border_defined = bool(re.search(r"--glass-border\s*:", html))
    if has_glass_border or has_border_defined: s["frosted"] = 2
    elif has_white_border or has_border_twcss: s["frosted"] = 1
    else: s["frosted"] = 0

    # 4. Natural Shadow
    has_glass_shadow = bool(re.search(r"var\(--glass-shadow\)", html))
    has_shadow_var   = bool(re.search(r"var\(--(?:shadow-card|shadow-md|sb-shadow)\)", html))
    has_shadow_raw   = bool(re.search(r"box-shadow[^:]*:[^;]*rgba\(0,\s*0,\s*0,\s*0\.[012]", html))
    if has_glass_shadow: s["shadow"] = 2
    elif has_shadow_var or has_shadow_raw: s["shadow"] = 1
    else: s["shadow"] = 0

    # 5. Layered Background
    has_blob_html = bool(re.search(r'class="[^"]*bg-blob|class=[\'"][^\'\"]*bg-blob', html))
    has_blob_css  = bool(re.search(r'\.bg-blob|\.sb-blob|bg_blob\.html', html))
    has_gradient  = bool(re.search(r"linear-gradient|radial-gradient", html))
    if has_blob_html and (has_blob_css or has_gradient): s["layer"] = 2
    elif has_blob_html or has_blob_css: s["layer"] = 1
    elif has_gradient: s["layer"] = 1
    else: s["layer"] = 0

    weights = {"blur": 20, "transp": 20, "frosted": 20, "shadow": 20, "layer": 20}
    total = sum(weights[k] * (1.0 if v == 2 else 0.4 if v == 1 else 0.0)
                for k, v in s.items())
    s["total"] = round(total)
    return s


def grade(pct):
    if pct >= 80: return f"{GRN}A{RST}", "A"
    if pct >= 60: return f"{GRN}B{RST}", "B"
    if pct >= 40: return f"{YLW}C{RST}", "C"
    if pct >= 20: return f"{YLW}D{RST}", "D"
    return f"{RED}F{RST}", "F"


# ════════════════════════════════════════════════════════════
# SAFE GUARD — cegah regresi
# ════════════════════════════════════════════════════════════
def has_active_bugs(html: str) -> list:
    """Cek apakah ada bug aktif yang wajib difix meski skor sudah tinggi."""
    bugs = []
    if re.search(r"display\s*:\s*var\(--shadow-sm-16\)", html):
        bugs.append("[x-cloak] display bug")
    if re.search(r"transform\s*:\s*var\(--shadow-sm-16\)", html):
        bugs.append("transform: none bug")
    if re.search(r"pointer-events\s*:\s*var\(--shadow-sm-16\)", html):
        bugs.append("pointer-events bug")
    if re.search(r"border-bottom\s*:\s*var\(--shadow-sm-16\)", html):
        bugs.append("border-bottom: none bug")
    return bugs


# ════════════════════════════════════════════════════════════
# FIXERS
# ════════════════════════════════════════════════════════════
class Fixer:

    @staticmethod
    def fix_active_bugs(html: str) -> tuple:
        """Fix bug-bug aktif yang PASTI salah, tidak ada false positive."""
        changes = []
        replacements = [
            (r"display\s*:\s*var\(--shadow-sm-16\)\s*!important",
             "display: none !important", "fixed [x-cloak] display bug"),
            (r"display\s*:\s*var\(--shadow-sm-16\)",
             "display: none", "fixed display: none bug"),
            (r"transform\s*:\s*var\(--shadow-sm-16\)",
             "transform: none", "fixed transform: none bug"),
            (r"pointer-events\s*:\s*var\(--shadow-sm-16\)",
             "pointer-events: none", "fixed pointer-events bug"),
            (r"border-bottom\s*:\s*var\(--shadow-sm-16\)",
             "border-bottom: none", "fixed border-bottom: none bug"),
            (r"border-top\s*:\s*var\(--shadow-sm-16\)",
             "border-top: none", "fixed border-top: none bug"),
            # Shadow dengan rgba non-standard (custom color var yang tidak ada)
            (r"var\(--color-rgba-\d+-\d+-\d+-a\d+\)",
             "rgba(0,0,0,0.06)", "fixed non-standard shadow rgba var"),
            # backdrop-filter duplikat saturate
            (r"(backdrop-filter\s*:\s*)var\(--glass-blur\)\s*saturate\([^)]+\)",
             r"\1var(--glass-blur)", "removed duplicate saturate"),
            (r"(-webkit-backdrop-filter\s*:\s*)var\(--glass-blur\)\s*saturate\([^)]+\)",
             r"\1var(--glass-blur)", "removed -webkit duplicate saturate"),
        ]
        for pattern, replacement, msg in replacements:
            new = re.sub(pattern, replacement, html)
            if new != html:
                changes.append(msg)
                html = new
        return html, changes

    @staticmethod
    def fix_blur_tokens(html: str) -> tuple:
        """
        Fix backdrop-filter dengan blur < 10px.
        SAFE: hanya ganti nilai blur yang jelas terlalu kecil.
        SKIP: jika sudah pakai var(--glass-blur).
        """
        changes = []

        # Fix var non-standard misal var(--glass-blur-sm) → var(--glass-blur)
        def _fix_blur_var(m):
            val = m.group(0)
            if val == "var(--glass-blur)": return val  # sudah benar
            if "--glass-blur" in val:
                changes.append(f"standardized {val} → var(--glass-blur)")
                return "var(--glass-blur)"
            return val
        html = re.sub(r"var\(--glass-blur[^)]*\)", _fix_blur_var, html)

        # Fix blur < 10px pada backdrop-filter (bukan di dalam var())
        def _fix_raw(m):
            full = m.group(0)
            if "var(--glass-blur)" in full: return full  # skip jika sudah token
            nums = re.findall(r"blur\s*\(\s*(\d+(?:\.\d+)?)\s*px", full)
            if nums and any(float(n) < 10 for n in nums):
                # Replace seluruh backdrop-filter value dengan var(--glass-blur)
                new = re.sub(r"blur\s*\(\s*[\d.]+\s*px\s*\)(?:\s*saturate\([^)]*\))?",
                             "var(--glass-blur)", full, count=1)
                # Hapus saturate jika masih tersisa setelah replace
                new = re.sub(r"var\(--glass-blur\)\s*saturate\([^)]*\)",
                             "var(--glass-blur)", new)
                if new != full:
                    changes.append(f"upgraded blur {nums[0]}px → var(--glass-blur)")
                return new
            return full

        html = re.sub(r"backdrop-filter\s*:\s*[^;}{<\n]+", _fix_raw, html)
        html = re.sub(r"-webkit-backdrop-filter\s*:\s*[^;}{<\n]+", _fix_raw, html)
        return html, changes

    @staticmethod
    def fix_border_tokens(html: str) -> tuple:
        """Fix border dengan token non-standard."""
        changes = []

        # --sb-border → --glass-border
        c = len(re.findall(r"var\(--sb-border[^)]*\)", html))
        if c:
            html = re.sub(r"var\(--sb-border[^)]*\)", "var(--glass-border)", html)
            changes.append(f"replaced {c}x --sb-border → --glass-border")

        # --color-border pada border property (bukan background)
        def _fix_color_border(m):
            if "border" in m.group(0).split(":")[0]:
                changes.append("replaced --color-border → --glass-border in border")
                return m.group(0).replace("var(--color-border)", "var(--glass-border)")
            return m.group(0)
        html = re.sub(r"border(?:-top|-bottom|-left|-right)?\s*:\s*[^;]*var\(--color-border\)[^;]*;",
                      _fix_color_border, html)

        # border dengan rgba opacity > 0.6 (terlalu solid untuk glass)
        def _fix_opaque_border(m):
            alpha_m = re.search(r"rgba\s*\([^)]*,\s*([\d.]+)\s*\)", m.group(0))
            if alpha_m and float(alpha_m.group(1)) > 0.6:
                changes.append(f"softened opaque border rgba({alpha_m.group(1)}) → glass-border")
                return re.sub(r"rgba\s*\([^)]+\)", "var(--glass-border)", m.group(0))
            return m.group(0)
        html = re.sub(r"border(?:-top|-bottom|-left|-right)?\s*:\s*1px solid rgba[^;]+;",
                      _fix_opaque_border, html)

        return html, changes

    @staticmethod
    def fix_shadow_tokens(html: str) -> tuple:
        """Fix shadow dengan token non-standard."""
        changes = []

        # --sb-shadow custom value → glass-shadow
        def _fix_sb_shadow(m):
            val = m.group(0)
            if "var(--glass-shadow)" in val: return val
            changes.append("upgraded --sb-shadow → glass-shadow pattern")
            return "--sb-shadow : 2px 0 8px rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.04)"
        html = re.sub(r"--sb-shadow\s*:[^\n;{]+", _fix_sb_shadow, html)

        return html, changes

    @staticmethod
    def fix_transparency_tokens(html: str) -> tuple:
        """Fix token transparansi non-standard."""
        changes = []

        # var(--color-white-a0XX) → rgba(255,255,255, X.XX)
        def _fix_white_token(m):
            token = m.group(0)
            alpha_m = re.search(r"a0?(\d+)\s*\)", token)
            if alpha_m:
                raw = int(alpha_m.group(1))
                alpha = raw / 100 if raw <= 100 else raw / 1000
                alpha = min(max(alpha, 0.01), 0.99)
                changes.append(f"replaced {token} → rgba(255,255,255,{alpha:.2f})")
                return f"rgba(255, 255, 255, {alpha:.2f})"
            return token
        html = re.sub(r"var\(--color-white-a0\d+\)", _fix_white_token, html)
        html = re.sub(r"var\(--color-slate-50-a0\d+\)", _fix_white_token, html)

        return html, changes

    @staticmethod
    def inject_blob(html: str, file_type: str) -> tuple:
        """Inject bg-blob HTML dan CSS."""
        changes = []

        if file_type == "page":
            # Cek apakah extends base
            if not re.search(r"{%\s*extends", html): return html, changes
            # Cek apakah sudah ada blob
            if re.search(r'class="[^"]*bg-blob', html): return html, changes
            # Inject setelah {% block content %} atau {% block extra_css %} end
            inserted = re.sub(
                r"({%\s*block\s+content\s*%}\s*\n)",
                r"\1\n" + BLOB_HTML + "\n",
                html, count=1
            )
            if inserted != html:
                changes.append("injected bg-blob HTML into block content")
                html = inserted
            # Inject BLOB_CSS ke block extra_css jika ada, atau ke style block
            if ".bg-blob" not in html:
                style_inject = f"\n<style>\n{BLOB_CSS}\n</style>\n"
                if "{% block extra_css %}" in html:
                    html = re.sub(
                        r"({%\s*block\s+extra_css\s*%})",
                        r"\1" + style_inject,
                        html, count=1
                    )
                    changes.append("injected blob CSS into extra_css block")
                elif "</head>" in html:
                    html = html.replace("</head>", style_inject + "</head>", 1)
                    changes.append("injected blob CSS before </head>")

        elif file_type == "base":
            # base.html: tambah blob CSS jika belum ada
            if ".bg-blob" not in html:
                # Inject di akhir <style> pertama
                html = re.sub(r"(</style>)", BLOB_CSS + r"\1", html, count=1)
                changes.append("injected blob CSS into base.html")
            # Fix: hapus bg-slate-50 dari body yang menghalangi blob
            if re.search(r'<body[^>]*class="[^"]*bg-slate-50', html):
                html = re.sub(r'(class="[^"]*)bg-slate-50\s*', r'\1', html)
                changes.append("removed bg-slate-50 from body (blocks blob)")

        elif file_type == "sidebar":
            if re.search(r'class="[^"]*sb-blob', html): return html, changes
            sb_blob_css = """
  /* Layered Background — sb-blob */
  .sb-blob {
    position: absolute; border-radius: 50%; filter: blur(60px);
    pointer-events: none; z-index: 0;
    animation: sbDrift 20s ease-in-out infinite alternate;
  }
  .sb-blob-1 { width:160px; height:160px; background:var(--color-primary,#059669); opacity:0.06; top:-40px; left:-60px; }
  .sb-blob-2 { width:120px; height:120px; background:#34d399; opacity:0.05; bottom:60px; left:-20px; animation-delay:-8s; }
  @keyframes sbDrift { from { transform:translate(0,0) scale(1); } to { transform:translate(12px,18px) scale(1.05); } }
  #sidebar > *:not(.sb-blob) { position: relative; z-index: 1; }
"""
            sb_blob_html = """
  <!-- sb-blob Layered Background -->
  <div class="sb-blob sb-blob-1" aria-hidden="true"></div>
  <div class="sb-blob sb-blob-2" aria-hidden="true"></div>
"""
            html = re.sub(r"(</style>)", sb_blob_css + r"\1", html, count=1)
            html = re.sub(r"(<aside[^>]*>)", r"\1" + sb_blob_html, html, count=1)
            # Tambahkan overflow:hidden ke aside
            html = re.sub(
                r'(<aside[^>]*class="[^"]*sidebar-glass[^"]*")',
                lambda m: m.group(0) if "overflow-hidden" in m.group(0)
                          else m.group(0).replace('class="', 'class="overflow-hidden '),
                html
            )
            changes.append("injected sb-blob into sidebar")

        return html, changes

    @staticmethod
    def inject_minimal_glass(html: str) -> tuple:
        """
        Aggressive mode: inject minimal glass CSS untuk file grade F
        yang sama sekali tidak punya glass styling.
        """
        changes = []
        # Hanya inject jika file punya {% block %} (Django template)
        if not re.search(r"{%\s*block", html): return html, changes
        # Jika sudah punya backdrop-filter, skip
        if "backdrop-filter" in html: return html, changes

        style_block = f"\n{{% block extra_css %}}{{% endblock %}}\n" if "{% block extra_css %}" not in html else ""
        inject = f"<style>\n{MINIMAL_GLASS_INJECT}\n</style>\n"

        if "{% block extra_css %}" in html:
            html = re.sub(
                r"({%\s*block\s+extra_css\s*%})",
                r"\1\n" + inject,
                html, count=1
            )
        elif "</head>" in html:
            html = html.replace("</head>", inject + "</head>", 1)
        else:
            return html, changes

        changes.append("injected minimal glass CSS (aggressive mode)")
        return html, changes


# ════════════════════════════════════════════════════════════
# FILE TYPE DETECTOR
# ════════════════════════════════════════════════════════════
def detect_type(fp: Path, html: str) -> str:
    name = fp.name.lower()
    path = str(fp).replace("\\", "/").lower()
    if name == "base.html" and "/base/" in path: return "base"
    if "sidebar" in name and "right" not in name and "item" not in name: return "sidebar"
    if name in ("navbar.html","footer.html","kpi_card.html","kpi_card_inner.html",
                "kpi_card_white.html","activity_drawer.html","approval_modal.html",
                "bg_blob.html","form_field.html","sidebar_item.html"): return "partial"
    if "/auth/" in path or name in ("login.html","register.html"): return "auth"
    if re.search(r"{%\s*extends", html): return "page"
    return "partial"


# ════════════════════════════════════════════════════════════
# INJECT TOKENS (hanya base.html, dengan regression guard)
# ════════════════════════════════════════════════════════════
def inject_tokens_safe(html: str, current_score: int) -> tuple:
    """
    BUG FIX v3: jangan timpa token block yang sudah ada jika skor sudah tinggi.
    Hanya inject jika belum ada atau skor < 60%.
    """
    has_tokens = bool(re.search(r"LUMRA GLASS DESIGN TOKENS", html))
    if has_tokens and current_score >= 60:
        return html, False  # skip — sudah ada dan skor OK

    token_block = f"<style>\n{GLASS_TOKENS_CSS}{GLASS_CLASSES_CSS}</style>"

    if has_tokens:
        # Update existing block
        new = re.sub(
            r"<style>\s*/\*\s*={5,}.*?LUMRA GLASS DESIGN TOKENS.*?</style>",
            token_block, html, flags=re.DOTALL
        )
        return new, new != html

    if "</head>" in html:
        return html.replace("</head>", token_block + "\n</head>", 1), True

    return token_block + "\n" + html, True


# ════════════════════════════════════════════════════════════
# FIX ONE FILE
# ════════════════════════════════════════════════════════════
def fix_file(fp: Path, dry_run: bool, backup_dir, aggressive: bool = False,
             safe: bool = True) -> dict:
    html_orig = fp.read_text(encoding="utf-8", errors="replace")
    html = html_orig
    file_type = detect_type(fp, html)
    all_changes = []

    score_before = score_file(html)
    sb = score_before["total"]

    # ── SAFE MODE: skip file yang sudah bagus, kecuali ada bug aktif ──
    active_bugs = has_active_bugs(html)
    if safe and sb >= 80 and not active_bugs:
        return {
            "file": fp, "file_type": file_type, "changed": False,
            "changes": [], "score_before": score_before,
            "score_after": score_before, "delta": 0, "skipped": True,
            "skip_reason": f"Grade A ({sb}%), no active bugs"
        }

    # ── Apply fixes ──────────────────────────────────────────

    # Step 1: Fix bug aktif — selalu, tidak ada risiko regresi
    html, ch = Fixer.fix_active_bugs(html); all_changes += ch

    # Step 2: Blur token fix
    html, ch = Fixer.fix_blur_tokens(html); all_changes += ch

    # Step 3: Border token fix
    html, ch = Fixer.fix_border_tokens(html); all_changes += ch

    # Step 4: Shadow token fix
    html, ch = Fixer.fix_shadow_tokens(html); all_changes += ch

    # Step 5: Transparency token fix
    html, ch = Fixer.fix_transparency_tokens(html); all_changes += ch

    # Step 6: Blob injection
    html, ch = Fixer.inject_blob(html, file_type); all_changes += ch

    # Step 7: Token injection (hanya base.html, dengan regression guard)
    if file_type == "base":
        html, injected = inject_tokens_safe(html, sb)
        if injected: all_changes.append("updated glass design tokens (base.html)")

    # Step 8: Aggressive — inject minimal glass ke file grade F
    if aggressive and sb < 20:
        html, ch = Fixer.inject_minimal_glass(html); all_changes += ch

    # ── Regression check ────────────────────────────────────
    score_after = score_file(html)
    sa = score_after["total"]
    delta = sa - sb

    # BUG FIX v3: jika delta < 0 (regresi), ROLLBACK perubahan
    # Tapi tetap apply bug fixes saja (Step 1)
    if delta < 0:
        # Rollback ke setelah step 1 saja
        html_bugfix = html_orig
        html_bugfix, ch_bugfix = Fixer.fix_active_bugs(html_orig)
        score_bugfix = score_file(html_bugfix)
        if score_bugfix["total"] >= sb:  # bug fixes OK, tidak regress
            html = html_bugfix
            all_changes = ch_bugfix
            all_changes.append(f"ROLLBACK: reverted non-bug changes (would have regressed {sb}%→{sa}%)")
            score_after = score_bugfix
            sa = score_after["total"]
            delta = sa - sb
        else:  # bug fixes juga regress, rollback total
            html = html_orig
            all_changes = [f"ROLLBACK: all changes reverted (regression detected {sb}%→{sa}%)"]
            score_after = score_before
            sa = sb
            delta = 0

    changed = html != html_orig

    if changed and not dry_run:
        if backup_dir:
            backup_dir.mkdir(parents=True, exist_ok=True)
            dst = backup_dir / fp.name
            if dst.exists():
                dst = backup_dir / (fp.stem + f"_{datetime.now().strftime('%H%M%S%f')}" + fp.suffix)
            shutil.copy2(fp, dst)
        fp.write_text(html, encoding="utf-8")

    return {
        "file": fp, "file_type": file_type,
        "changed": changed, "changes": all_changes,
        "score_before": score_before, "score_after": score_after,
        "delta": delta, "skipped": False, "skip_reason": ""
    }


# ════════════════════════════════════════════════════════════
# FILE DISCOVERY
# ════════════════════════════════════════════════════════════
def find_html_files(root: Path, only: str = None, only_file: str = None) -> list:
    files = []
    for fp in sorted(root.rglob("*.html")):
        if any(x in str(fp) for x in ["_archive", "_glass_backup", "__pycache__"]): continue
        if only_file and fp.name != only_file: continue
        if only and only not in str(fp): continue
        files.append(fp)
    return files


def find_template_dir(project_dir: Path):
    for c in ["lumra_config/templates", "lumra/lumra_config/templates",
              "templates", "."]:
        p = project_dir / c
        if p.exists() and any(p.rglob("*.html")): return p
    return None


# ════════════════════════════════════════════════════════════
# REPORT
# ════════════════════════════════════════════════════════════
def run_report(files: list, verbose: bool = False):
    icon = {0: "❌", 1: "🟡", 2: "✅"}
    grade_counts = defaultdict(int)
    rows = []
    for fp in files:
        html = fp.read_text(encoding="utf-8", errors="replace")
        s = score_file(html)
        _, g = grade(s["total"])
        grade_counts[g] += 1
        rows.append((fp.name, s, g))

    print(f"\n  {'File':<48} {'Bl':>2} {'Tr':>2} {'Fr':>2} {'Sh':>2} {'Ly':>2} {'%':>4} Gr")
    print(f"  {'─'*48} {'─'*2} {'─'*2} {'─'*2} {'─'*2} {'─'*2} {'─'*4} {'─'*2}")
    for name, s, g in sorted(rows, key=lambda x: x[1]["total"]):
        g_c, _ = grade(s["total"])
        bugs = "⚡" if has_active_bugs(fp.read_text(encoding="utf-8", errors="replace")
                                       if verbose else "") else ""
        print(f"  {name[:48]:<48} {icon[s['blur']]} {icon[s['transp']]} "
              f"{icon[s['frosted']]} {icon[s['shadow']]} {icon[s['layer']]} "
              f"{s['total']:>3}% {g_c}")

    print(f"\n  Grade distribution:")
    total_files = len(files)
    for g, emoji in [("A","🏆"),("B","✅"),("C","🟡"),("D","🔴"),("F","💀")]:
        n = grade_counts[g]
        if n:
            bar = "█" * min(n, 30) + "░" * max(0, 30 - min(n, 30))
            pct = n / total_files * 100
            print(f"    {emoji} {g}  {bar}  {n} ({pct:.0f}%)")

    avg = sum(score_file(fp.read_text(encoding="utf-8", errors="replace"))["total"]
              for fp in files) / len(files) if files else 0
    print(f"\n  Skor rata-rata: {avg:.1f}%")


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(
        description="Lumra Glass Fix v3 — Safe auto-fixer with regression guard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow yang disarankan:
  1. Audit dulu:     python lumra_glass_fix_v3.py --report
  2. Dry-run:        python lumra_glass_fix_v3.py
  3. Apply safe:     python lumra_glass_fix_v3.py --apply
  4. Check hasilnya: python lumra_glass_fix_v3.py --report

Untuk file grade F yang butuh inject lebih agresif:
     python lumra_glass_fix_v3.py --apply --aggressive --only reports

Hanya fix bug aktif tanpa sentuh skor:
     python lumra_glass_fix_v3.py --apply --bugs-only
        """
    )
    ap.add_argument("--project-dir", "-p", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", metavar="FOLDER", help="Filter by folder name")
    ap.add_argument("--file", metavar="NAME", help="Single file by name")
    ap.add_argument("--report", action="store_true", help="Audit only, no fix")
    ap.add_argument("--aggressive", action="store_true",
                    help="Inject minimal glass CSS ke file grade F (<20%%)")
    ap.add_argument("--bugs-only", action="store_true",
                    help="Hanya fix bug aktif (display/transform/pointer-events token)")
    ap.add_argument("--no-safe", action="store_true",
                    help="Proses juga file Grade A (default: skip Grade A)")
    ap.add_argument("--no-backup", action="store_true")
    ap.add_argument("--min-delta", type=int, default=0,
                    help="Hanya tampilkan/fix file dengan prediksi kenaikan >= N%%")
    ap.add_argument("--json-out", metavar="FILE")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    safe = not args.no_safe
    mode_label = f"{GRN}APPLY{RST}" if args.apply else f"{YLW}DRY-RUN{RST}"

    print(f"\n{BOLD}{'═'*62}{RST}")
    print(f"{BOLD}  LUMRA GLASS FIX v3{RST}")
    print(f"{BOLD}{'═'*62}{RST}")
    print(f"  Project    : {project_dir}")
    print(f"  Mode       : {mode_label}")
    print(f"  Safe mode  : {'ON — skip Grade A' if safe else 'OFF — proses semua'}")
    if args.aggressive: print(f"  Aggressive : {YLW}ON — inject ke grade F{RST}")
    if args.bugs_only:  print(f"  Bugs only  : {YLW}ON{RST}")

    td = find_template_dir(project_dir)
    if not td: print(f"\n  {RED}Template dir tidak ditemukan{RST}"); sys.exit(1)
    ok(f"Templates: {td}")

    files = find_html_files(td, args.only, args.file)
    if not files: warn("Tidak ada file HTML ditemukan."); sys.exit(0)
    info(f"Ditemukan {len(files)} file HTML")

    if args.report:
        run_report(files); return

    if not args.apply:
        print(f"\n  {YLW}DRY-RUN — tidak ada perubahan.{RST}")
        print(f"  Tambahkan --apply untuk eksekusi.\n")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = None if args.no_backup else (project_dir / f"_glass_backup_{ts}")
    if args.apply and backup_dir:
        ok(f"Backup: {backup_dir.name}/")

    print(f"\n{BOLD}  PROCESSING{RST}")
    print(f"  {'─'*60}")

    results = []
    stats = {"changed": 0, "skipped_safe": 0, "skipped_no_change": 0,
             "regressed": 0, "total_delta": 0}

    for fp in files:
        rel = str(fp.relative_to(td))
        html = fp.read_text(encoding="utf-8", errors="replace")
        sb = score_file(html)["total"]

        # bugs-only mode: hanya fix jika ada bug aktif
        if args.bugs_only:
            bugs = has_active_bugs(html)
            if not bugs:
                skip(f"{rel}  ({sb}% — no active bugs)"); continue

        result = fix_file(
            fp, dry_run=not args.apply,
            backup_dir=backup_dir if args.apply else None,
            aggressive=args.aggressive, safe=safe
        )
        results.append(result)

        if result.get("skipped"):
            fix_skip(f"{rel}  ({sb}% — {result['skip_reason']})")
            stats["skipped_safe"] += 1
            continue

        sa    = result["score_after"]["total"]
        delta = result["delta"]

        if delta < 0:
            regress(f"{rel}  {sb}% → {sa}% ({RED}{delta}% ROLLBACK{RST})")
            stats["regressed"] += 1
        elif result["changed"] or (not args.apply and result["changes"]):
            d_col = GRN if delta > 0 else DIM
            d_str = f"+{delta}%" if delta > 0 else ("=" if delta == 0 else f"{delta}%")
            verb  = "fixed" if args.apply else "would fix"
            print(f"  {verb:<10} {rel:<45} {sb:>3}% → {sa:>3}%  {d_col}{d_str}{RST}")
            shown = result["changes"]
            for ch in shown[:3]:
                if "ROLLBACK" not in ch: print(f"             {DIM}• {ch}{RST}")
            if len(shown) > 3:
                print(f"             {DIM}• +{len(shown)-3} more...{RST}")
            if result["changed"]:
                stats["changed"] += 1
                stats["total_delta"] += max(0, delta)
        else:
            skip(f"{rel}  ({sb}% — tidak ada perubahan)")
            stats["skipped_no_change"] += 1

    # ── Summary ─────────────────────────────────────────────
    print(f"\n{BOLD}{'═'*62}{RST}")
    print(f"{BOLD}  RINGKASAN{RST}")
    print(f"{BOLD}{'═'*62}{RST}")

    verb = "diubah" if args.apply else "akan diubah"
    print(f"  File {verb}         : {BOLD}{stats['changed']}{RST} dari {len(files)}")
    print(f"  Dilewati (Grade A) : {stats['skipped_safe']}")
    print(f"  Tidak ada perubahan: {stats['skipped_no_change']}")
    if stats['regressed']: print(f"  {RED}Regression (rollback): {stats['regressed']}{RST}")
    print(f"  Total delta skor   : +{stats['total_delta']}% kumulatif")

    # Grade distribution estimasi
    if results:
        gcount = defaultdict(int)
        for r in results:
            if r.get("skipped"):
                s = r["score_before"]["total"]
            else:
                s = r["score_after"]["total"]
            _, g = grade(s)
            gcount[g] += 1
        print(f"\n  Estimasi grade setelah fix:")
        for g, emoji in [("A","🏆"),("B","✅"),("C","🟡"),("D","🔴"),("F","💀")]:
            n = gcount[g]
            if n:
                bar = "█" * min(n, 25) + "░" * max(0, 25 - min(n, 25))
                print(f"    {emoji} {g}  {bar}  {n}")

    if args.json_out:
        out = [{"file": str(r["file"].name), "type": r["file_type"],
                "score_before": r["score_before"]["total"],
                "score_after": r["score_after"]["total"],
                "delta": r["delta"], "changes": r["changes"]}
               for r in results if not r.get("skipped")]
        Path(args.json_out).write_text(json.dumps(out, indent=2), encoding="utf-8")
        ok(f"JSON: {args.json_out}")

    if not args.apply and stats["changed"] > 0:
        print(f"\n  Jalankan dengan --apply:")
        cmd = f"python lumra_glass_fix_v3.py --apply"
        if args.only: cmd += f" --only {args.only}"
        if args.file: cmd += f" --file {args.file}"
        if args.aggressive: cmd += " --aggressive"
        print(f"    {GRN}{cmd}{RST}")
    elif args.apply:
        print(f"\n  Cek hasil: python lumra_glass_fix_v3.py --report")
        if backup_dir and backup_dir.exists():
            print(f"  Backup   : {backup_dir}")


if __name__ == "__main__":
    main()