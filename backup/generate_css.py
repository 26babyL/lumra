#!/usr/bin/env python3
"""
generate_css.py — Lumra CSS Generator
======================================
Baca lumra.config.json → tulis lumra_design_system.css

Cara pakai:
    python generate_css.py                    # generate dari config default
    python generate_css.py --config path/to/lumra.config.json
    python generate_css.py --out path/to/output/

File yang dihasilkan:
    lumra_design_system.css   ← JANGAN edit manual, ini generated file

SSOT chain:
    lumra.config.json  →  generate_css.py  →  lumra_design_system.css
                                            →  (token untuk glass_fix_v3.py)
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from textwrap import indent


# ── Helpers ───────────────────────────────────────────────────────────────────

def _c(n): return f"\033[{n}m"
RST = _c(0); GRN = _c(32); YLW = _c(33); RED = _c(31); CYN = _c(36); BOLD = _c(1)

def ok(m):   print(f"  {GRN}✓{RST}  {m}")
def warn(m): print(f"  {YLW}!{RST}  {m}")
def err(m):  print(f"  {RED}✗{RST}  {m}")
def info(m): print(f"  {CYN}→{RST}  {m}")


def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_token(cfg: dict, token_path: str) -> str:
    """
    Resolve token reference seperti "color.primary" dari config.
    Dipakai untuk blob color_token references.
    """
    parts = token_path.split(".")
    node = cfg
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return f"/* unresolved: {token_path} */"
    return str(node)


def alpha_variants(hex_color: str, prefix: str, alphas: list) -> str:
    """Generate rgba alpha variants dari hex color."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    lines = []
    for a in alphas:
        key = str(a).replace("0.", "").replace(".", "")
        if len(key) < 2: key = "0" + key
        lines.append(f"  {prefix}-a{key}: rgba({r},{g},{b},{a});")
    return "\n".join(lines)


# ── CSS Block Generators ───────────────────────────────────────────────────────

def gen_header(cfg: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    version = cfg["_meta"]["version"]
    return f"""\
/* ============================================================
   LUMRA DESIGN SYSTEM  v{version}  — Auto-Generated
   lumra_design_system.css

   ⚠️  JANGAN EDIT FILE INI SECARA MANUAL ⚠️
   File ini di-generate otomatis dari lumra.config.json
   
   Untuk mengubah nilai:
     1. Edit lumra.config.json
     2. Jalankan: python generate_css.py
     3. Commit kedua file (config + CSS)

   Generated: {ts}
   Generator: generate_css.py
   Config   : lumra.config.json v{version}
   ============================================================ */

"""


def gen_font_import(cfg: dict) -> str:
    url = cfg["typography"]["google_fonts_url"]
    return f'@import url("{url}");\n\n'


def gen_root(cfg: dict) -> str:
    t = cfg["typography"]
    r = cfg["radius"]
    sp = cfg["spacing"]
    tr = cfg["transition"]
    z = cfg["z_index"]
    la = cfg["layout"]
    brand = cfg["brand"]
    glass = cfg["glass"]
    color = cfg["color"]
    em = cfg["emerald_scale"]
    sl = cfg["slate_scale"]
    sh = cfg["shadow"]

    # Primary alpha variants
    primary_hex = brand["primary"]
    r_val = int(primary_hex[1:3], 16)
    g_val = int(primary_hex[3:5], 16)
    b_val = int(primary_hex[5:7], 16)

    alphas = [0.03, 0.05, 0.06, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25,
              0.28, 0.30, 0.35, 0.40, 0.50, 0.55, 0.60, 0.65, 0.70, 0.80, 0.90]

    primary_alpha_lines = []
    for a in alphas:
        key = f"{a:.2f}".replace("0.", "").replace(".", "")
        if len(key) < 2: key = "0" + key
        primary_alpha_lines.append(
            f"  --color-primary-a{key}: rgba({r_val},{g_val},{b_val},{a});"
        )
    primary_alphas = "\n".join(primary_alpha_lines)

    emerald_vars = "\n".join(
        f"  --color-emerald-{k}: {v};"
        for k, v in em.items()
    )
    slate_vars = "\n".join(
        f"  --color-slate-{k}: {v};"
        for k, v in sl.items()
    )

    return f"""\
/* ============================================================
   1. DESIGN TOKENS — :root
   ============================================================ */

:root {{

  /* ── Font ──────────────────────────────────────────────── */
  --font-sans    : {t["font_sans"]};
  --font-display : {t["font_display"]};
  --font-mono    : {t["font_mono"]};

  --text-xs   : {t["size"]["xs"]};
  --text-sm   : {t["size"]["sm"]};
  --text-base : {t["size"]["base"]};
  --text-md   : {t["size"]["md"]};
  --text-lg   : {t["size"]["lg"]};
  --text-xl   : {t["size"]["xl"]};
  --text-2xl  : {t["size"]["2xl"]};
  --text-3xl  : {t["size"]["3xl"]};
  --text-4xl  : {t["size"]["4xl"]};

  --leading-tight   : {t["leading"]["tight"]};
  --leading-snug    : {t["leading"]["snug"]};
  --leading-normal  : {t["leading"]["normal"]};
  --leading-relaxed : {t["leading"]["relaxed"]};

  --tracking-tightest: {t["tracking"]["tightest"]};
  --tracking-tight   : {t["tracking"]["tight"]};
  --tracking-normal  : {t["tracking"]["normal"]};
  --tracking-wide    : {t["tracking"]["wide"]};
  --tracking-widest  : {t["tracking"]["widest"]};

  --font-light    : {t["weight"]["light"]};
  --font-normal   : {t["weight"]["normal"]};
  --font-medium   : {t["weight"]["medium"]};
  --font-semibold : {t["weight"]["semibold"]};
  --font-bold     : {t["weight"]["bold"]};


  /* ── Emerald — brand primary ────────────────────────── */
{emerald_vars}


  /* ── Slate — neutral scale ──────────────────────────── */
{slate_vars}


  /* ── Primary — brand ────────────────────────────────── */
  --color-primary        : {brand["primary"]};
  --color-primary-light  : {brand["primary_light"]};
  --color-primary-subtle : {brand["primary_subtle"]};
  --color-primary-dark   : {brand["primary_dark"]};
  --color-primary-glow   : {brand["primary_glow"]};

{primary_alphas}


  /* ── Semantik ───────────────────────────────────────── */
  --color-success        : {color["success"]};
  --color-success-bg     : {color["success_bg"]};
  --color-success-border : {color["success_border"]};
  --color-success-text   : {color["success_text"]};

  --color-warning        : {color["warning"]};
  --color-warning-bg     : {color["warning_bg"]};
  --color-warning-border : {color["warning_border"]};
  --color-warning-text   : {color["warning_text"]};

  --color-danger         : {color["danger"]};
  --color-danger-bg      : {color["danger_bg"]};
  --color-danger-border  : {color["danger_border"]};
  --color-danger-text    : {color["danger_text"]};

  --color-info           : {color["info"]};
  --color-info-bg        : {color["info_bg"]};
  --color-info-border    : {color["info_border"]};
  --color-info-text      : {color["info_text"]};

  --color-accent         : {color["accent"]};
  --color-accent-bg      : {color["accent_bg"]};
  --color-accent-border  : {color["accent_border"]};
  --color-accent-text    : {color["accent_text"]};


  /* ── Surface & Teks ─────────────────────────────────── */
  --color-bg            : {color["bg"]};
  --color-surface       : {color["surface"]};
  --color-surface-strong: {color["surface_strong"]};
  --color-border        : {color["border"]};
  --color-border-focus  : {color["border_focus"]};
  --color-text          : {color["text"]};
  --color-text-muted    : {color["text_muted"]};
  --color-text-subtle   : {color["text_subtle"]};
  --color-text-inverse  : {color["text_inverse"]};
  --color-text-primary  : {brand["primary"]};


  /* ── Glassmorphism ──────────────────────────────────── */
  --glass-bg         : {glass["bg"]};
  --glass-bg-strong  : {glass["bg_strong"]};
  --glass-bg-subtle  : {glass["bg_subtle"]};
  --glass-border     : {glass["border"]};
  --glass-border-em  : {glass["border_em"]};
  --glass-blur       : {glass["blur"]};
  --glass-blur-sm    : {glass["blur_sm"]};
  --glass-blur-lg    : {glass["blur_lg"]};
  --glass-shadow     : {glass["shadow"]};
  --glass-shadow-lg  : {glass["shadow_lg"]};
  --glass-shadow-glow: {glass["shadow_glow"]};
  --glass-dark-bg    : {glass["dark_bg"]};
  --glass-dark-blur  : {glass["dark_blur"]};
  --glass-dark-border: {glass["dark_border"]};


  /* ── Shadow ─────────────────────────────────────────── */
  --shadow-xs  : {sh["xs"]};
  --shadow-sm  : {sh["sm"]};
  --shadow-md  : {sh["md"]};
  --shadow-lg  : {sh["lg"]};
  --shadow-xl  : {sh["xl"]};
  --shadow-2xl : {sh["2xl"]};
  --shadow-focus        : {sh["focus"]};
  --shadow-focus-danger : {sh["focus_danger"]};
  --shadow-glow         : {sh["glow"]};
  --shadow-glow-sm      : {sh["glow_sm"]};
  --shadow-card         : var(--shadow-md);
  --shadow-card-hover   : var(--shadow-lg);
  --shadow-dropdown     : var(--shadow-xl);


  /* ── Border radius ──────────────────────────────────── */
  --radius-xs  : {r["xs"]};
  --radius-sm  : {r["sm"]};
  --radius-md  : {r["md"]};
  --radius-lg  : {r["lg"]};
  --radius-xl  : {r["xl"]};
  --radius-2xl : {r["2xl"]};
  --radius-3xl : {r["3xl"]};
  --radius-full: {r["full"]};


  /* ── Spacing ────────────────────────────────────────── */
{chr(10).join(f"  --space-{k}  : {v};" for k, v in sp.items())}


  /* ── Transition ─────────────────────────────────────── */
  --ease-out    : {tr["ease_out"]};
  --ease-in-out : {tr["ease_in_out"]};
  --ease-bounce : {tr["ease_bounce"]};
  --ease-smooth : {tr["ease_smooth"]};
  --transition-fast  : {tr["fast"]} var(--ease-out);
  --transition-base  : {tr["base"]} var(--ease-out);
  --transition-slow  : {tr["slow"]} var(--ease-out);
  --transition-color : color var(--transition-fast), background-color var(--transition-fast), border-color var(--transition-fast);
  --transition-shadow: box-shadow var(--transition-base), transform var(--transition-base);
  --transition-all   : all var(--transition-base);


  /* ── Z-index ────────────────────────────────────────── */
{chr(10).join(f"  --z-{k.replace('_', '-')}     : {v};" for k, v in z.items())}


  /* ── Layout ─────────────────────────────────────────── */
  --sidebar-width           : {la["sidebar_width"]};
  --sidebar-width-collapsed : {la["sidebar_width_collapsed"]};
  --navbar-height           : {la["navbar_height"]};
  --content-max-width       : {la["content_max_width"]};


  /* ── Backward-compat aliases ─────────────────────────── */
  --emerald   : var(--color-primary);
  --blue      : var(--color-info);
  --amber     : var(--color-warning);
  --r         : var(--radius-md);

  /* Sidebar vars */
  --sb-bg          : var(--glass-bg);
  --sb-border      : var(--glass-border);
  --sb-text        : var(--color-text-muted);
  --sb-hover-bg    : var(--color-primary-a08);
  --sb-hover-text  : var(--color-primary);
  --sb-active-bg   : var(--color-primary-a12);
  --sb-active-text : var(--color-primary);
}}

"""


def gen_blob_css(cfg: dict) -> str:
    b = cfg["blob"]
    s = b["sizes"]
    lines = []
    for i, (key, blob) in enumerate(s.items(), 1):
        w, h = blob["w"], blob["h"]
        delay = blob["delay_s"]
        color_ref = blob.get("color") or resolve_token(cfg, blob.get("color_token", "brand.primary"))
        pos_parts = []
        if "top" in blob:    pos_parts.append(f"top:{blob['top']}px")
        if "bottom" in blob: pos_parts.append(f"bottom:{blob['bottom']}px")
        if "left" in blob:   pos_parts.append(f"left:{blob['left']}px")
        if "right" in blob:  pos_parts.append(f"right:{blob['right']}px")
        if "top_pct" in blob:  pos_parts.append(f"top:{blob['top_pct']}")
        if "left_pct" in blob: pos_parts.append(f"left:{blob['left_pct']}")
        pos_css = "; ".join(pos_parts)
        lines.append(
            f".bg-blob-{key} {{ width:{w}px; height:{h}px; background:{color_ref}; "
            f"{pos_css}; animation-delay:{delay}s; }}"
        )

    return f"""\
/* ============================================================
   BLOB BACKGROUND — generated from config.blob
   ============================================================ */

.bg-blob {{
  position      : fixed;
  border-radius : 50%;
  filter        : blur({b['blur_px']}px);
  opacity       : {b['opacity']};
  pointer-events: none;
  z-index       : 0;
  animation     : blobDrift {b['animation_duration_s']}s ease-in-out infinite alternate;
}}

{chr(10).join(lines)}

@keyframes blobDrift {{
  from {{ transform: translate(0, 0) scale(1); }}
  to   {{ transform: translate(20px, 28px) scale(1.06); }}
}}

"""


def gen_kpi_accents(cfg: dict) -> str:
    accents = cfg["kpi_card"]["accents"]
    lines = []
    for key, color in accents.items():
        lines.append(
            f".kpi-card.{key}::after, .kpi-glass.{key}::after, "
            f".lumra-kpi.{key}::after {{ background: {color}; }}"
        )
    return "\n".join(lines) + "\n"


def gen_validate_comment(cfg: dict) -> str:
    """Embed config hash ke CSS sebagai komentar — untuk validator."""
    import hashlib
    config_str = json.dumps(cfg, sort_keys=True)
    h = hashlib.md5(config_str.encode()).hexdigest()[:8]
    return f"/* config-hash: {h} */\n"


# ── Main Generator ─────────────────────────────────────────────────────────────

def generate(config_path: Path, out_dir: Path) -> Path:
    cfg = load_config(config_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "lumra_design_system.css"

    parts = [
        gen_header(cfg),
        gen_validate_comment(cfg),
        gen_font_import(cfg),
        gen_root(cfg),
        # Komponen dasar (reset, base body, dll) — tetap dari template statis
        # karena ini bukan nilai yang berubah-ubah, tapi struktur
        _STATIC_COMPONENTS,
        gen_blob_css(cfg),
        gen_kpi_accents(cfg),
        _STATIC_ANIMATIONS,
        _STATIC_PRINT_RESPONSIVE,
    ]

    css = "".join(parts)
    out_path.write_text(css, encoding="utf-8")
    return out_path


# ── Static CSS blocks (struktur, bukan nilai) ──────────────────────────────────
# Blok-blok ini tidak berisi nilai hardcoded — semua nilai adalah var(--token)
# Kalau ada nilai baru yang perlu dikontrol, TAMBAH ke config, bukan ke sini.

_STATIC_COMPONENTS = """\
/* ============================================================
   2. RESET & BASE
   ============================================================ */

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
  scroll-behavior: smooth;
  scrollbar-gutter: stable;
}

body {
  font-family            : var(--font-sans);
  font-size              : var(--text-base);
  line-height            : var(--leading-normal);
  color                  : var(--color-text);
  background             : var(--color-bg);
  -webkit-font-smoothing : antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a { color: var(--color-primary-light); text-decoration: none; transition: var(--transition-color); }
a:hover { color: var(--color-primary); }
button { cursor: pointer; font-family: inherit; }
input, textarea, select { font-family: inherit; }
code, pre, kbd { font-family: var(--font-mono); }
hr { border: none; border-top: 1px solid var(--color-border); margin: var(--space-4) 0; }


/* ============================================================
   3. GLASSMORPHISM UTILITIES
   ============================================================ */

.lumra-glass {
  background             : var(--glass-bg);
  backdrop-filter        : var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border                 : 1px solid var(--glass-border);
  box-shadow             : var(--glass-shadow);
  transition             : var(--transition-shadow);
}
.lumra-glass:hover { box-shadow: var(--glass-shadow-lg); transform: translateY(-2px); }

.lumra-glass-strong {
  background             : var(--glass-bg-strong);
  backdrop-filter        : var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border                 : 1px solid var(--glass-border);
  box-shadow             : var(--glass-shadow);
}

.lumra-glass-dark {
  background             : var(--glass-dark-bg);
  backdrop-filter        : var(--glass-dark-blur);
  -webkit-backdrop-filter: var(--glass-dark-blur);
  border                 : 1px solid var(--glass-dark-border);
}


/* ============================================================
   4. KPI CARD
   ============================================================ */

.kpi-card, .kpi-glass, .lumra-kpi {
  background             : var(--glass-bg);
  backdrop-filter        : var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border                 : 1px solid var(--glass-border);
  border-radius          : var(--radius-xl);
  box-shadow             : var(--glass-shadow);
  position               : relative;
  overflow               : hidden;
  transition             : box-shadow 0.2s ease, transform 0.2s ease;
}

.kpi-card::before, .kpi-glass::before, .lumra-kpi::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 1px; background: rgba(255,255,255,0.60);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  pointer-events: none; z-index: 1;
}

.kpi-card::after, .kpi-glass::after, .lumra-kpi::after {
  content: ''; position: absolute; top: 0; right: 0;
  width: 60px; height: 60px;
  border-radius: 0 var(--radius-xl) 0 100%;
  opacity: 0.07; pointer-events: none;
}

.kpi-card:hover, .kpi-glass:hover, .lumra-kpi:hover {
  box-shadow: var(--glass-shadow-lg); transform: translateY(-2px);
}


/* ============================================================
   5. GLASS CARD
   ============================================================ */

.glass-card, .glass, .lumra-card {
  background             : var(--glass-bg);
  backdrop-filter        : var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border                 : 1px solid var(--glass-border);
  border-radius          : var(--radius-xl);
  box-shadow             : var(--glass-shadow);
}


/* ============================================================
   6. SCROLLBAR & SELECTION
   ============================================================ */

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--color-slate-300); border-radius: var(--radius-full); }
::-webkit-scrollbar-thumb:hover { background: var(--color-slate-400); }
* { scrollbar-width: thin; scrollbar-color: var(--color-slate-300) transparent; }

::selection { background: var(--color-primary-a25); color: var(--color-primary-dark); }

:focus { outline: none; }
:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 3px; }
button:focus-visible, a:focus-visible, input:focus-visible {
  outline: 2px solid var(--color-primary); outline-offset: 2px; box-shadow: var(--shadow-focus);
}


/* ============================================================
   7. SCROLL REVEAL
   ============================================================ */

.reveal { opacity: 0; transform: translateY(14px); transition: opacity 0.42s ease, transform 0.42s ease; }
.reveal.visible { opacity: 1; transform: none; }

"""

_STATIC_ANIMATIONS = """\
/* ============================================================
   KEYFRAMES
   ============================================================ */

@keyframes lumra-fade-up  { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
@keyframes lumra-fade-in  { from { opacity: 0; } to { opacity: 1; } }
@keyframes lumra-scale-in { from { opacity: 0; transform: scale(0.94); } to { opacity: 1; transform: scale(1); } }
@keyframes lumra-pulse    { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
@keyframes lumra-spin     { to { transform: rotate(360deg); } }
@keyframes lumra-shimmer  { from { background-position: -400px 0; } to { background-position: 400px 0; } }
@keyframes tIn  { from { opacity: 0; transform: translateX(16px); } to { opacity: 1; transform: none; } }
@keyframes tOut { from { opacity: 1; } to { opacity: 0; transform: translateX(16px); } }

.animate-fade-up  { animation: lumra-fade-up  350ms var(--ease-out) both; }
.animate-fade-in  { animation: lumra-fade-in  250ms var(--ease-out) both; }
.animate-scale-in { animation: lumra-scale-in 200ms var(--ease-bounce) both; }
.animate-spin     { animation: lumra-spin 800ms linear infinite; }

.lumra-skeleton {
  background     : linear-gradient(90deg, var(--color-slate-100) 25%, var(--color-slate-200) 50%, var(--color-slate-100) 75%);
  background-size: 400px 100%;
  animation      : lumra-shimmer 1.4s ease-in-out infinite;
  border-radius  : var(--radius-sm);
}

"""

_STATIC_PRINT_RESPONSIVE = """\
/* ============================================================
   PRINT
   ============================================================ */

@media print {
  .bg-blob, .lumra-navbar, .lumra-sidebar { display: none !important; }
  .glass-card, .kpi-card, .kpi-glass, .lumra-kpi, .glass {
    background     : transparent !important;
    backdrop-filter: none !important;
    border         : 1px solid #ccc !important;
    box-shadow     : none !important;
  }
}

@media (max-width: 768px) {
  :root { --navbar-height: 52px; }
}
"""


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Lumra CSS Generator — baca config, tulis CSS")
    ap.add_argument("--config", "-c", default="lumra.config.json",
                    help="Path ke lumra.config.json")
    ap.add_argument("--out", "-o", default="static/css",
                    help="Output directory untuk CSS yang dihasilkan")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print output ke stdout, tidak tulis file")
    args = ap.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        err(f"Config tidak ditemukan: {config_path}")
        sys.exit(1)

    print(f"\n{BOLD}Lumra CSS Generator{RST}")
    print(f"  Config : {config_path}")

    if args.dry_run:
        cfg = load_config(config_path)
        css = "".join([
            gen_header(cfg), gen_validate_comment(cfg),
            gen_font_import(cfg), gen_root(cfg),
            _STATIC_COMPONENTS, gen_blob_css(cfg),
            gen_kpi_accents(cfg), _STATIC_ANIMATIONS, _STATIC_PRINT_RESPONSIVE
        ])
        print(css[:3000])
        print(f"\n  ... ({len(css)} chars total)")
        return

    out_dir = Path(args.out)
    out_path = generate(config_path, out_dir)

    file_size = out_path.stat().st_size
    ok(f"Wrote {out_path} ({file_size:,} bytes)")
    print(f"\n  Langkah selanjutnya:")
    print(f"    python validate.py --config {config_path} --css {out_path}")
    print()


if __name__ == "__main__":
    main()