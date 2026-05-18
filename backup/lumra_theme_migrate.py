#!/usr/bin/env python3
"""
lumra_theme_migrate.py
======================
Membuat semua template HTML LUMRA ikut theme toggle (light/dark).

Strategi:
  A. bg-white / bg-slate-* di class="" → ganti ke inline style pakai CSS var
     Kenapa: background tidak bisa di-override dari luar tanpa !important cascade hell
  B. text-slate-* / border-slate-* → TIDAK diubah di HTML
     Cukup tambahkan CSS overrides di design system (output: theme_overrides.css)

Cara pakai:
  # Preview — tidak ubah file apapun
  python lumra_theme_migrate.py --dry-run

  # Apply ke semua template
  python lumra_theme_migrate.py --apply

  # Hanya lihat statistik
  python lumra_theme_migrate.py --stats

  # Apply ke satu file
  python lumra_theme_migrate.py --apply --file dashboard.html

  # Generate CSS overrides saja (untuk design system)
  python lumra_theme_migrate.py --css-only

Opsi:
  --root    PATH   Template root (default: D:\\APPS\\...)
  --backup  PATH   Direktori backup (default: ./_theme_migrate_backup)
  --output  PATH   Output CSS overrides (default: ./theme_overrides.css)
"""

import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ══════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════

DEFAULT_ROOT   = Path(r"D:\APPS\Project\lumra\lumra_config\templates")
DEFAULT_BACKUP = Path(r"D:\APPS\Project\lumra\_theme_migrate_backup")
DEFAULT_OUTPUT = Path(r"D:\APPS\Project\lumra\lumra_config\static\css\theme_overrides.css")

SKIP_PATTERNS = ["purchasing", "vendor_form", "vendor_list", "vendors_list", "supplier_price"]

# ══════════════════════════════════════════════════════════════════
# MAPPING: Tailwind bg class → CSS variable
# ══════════════════════════════════════════════════════════════════
#
# Prinsip mapping:
#   bg-white / bg-slate-50      → --color-surface     (kartu, panel utama)
#   bg-slate-100                → --color-bg           (background halaman)
#   bg-slate-800 / bg-slate-900 → --color-surface-strong (header gelap, dll)
#   bg-slate-200..700           → interpolasi antara surface dan surface-strong
#
# Format: "tailwind-class": ("css-var", "fallback-hex-light")
#
BG_MAP = {
    # Putih / sangat terang → surface utama
    "bg-white"     : ("--color-surface",        "rgba(255,255,255,0.90)"),
    "bg-white/40"  : ("--color-surface",        "rgba(255,255,255,0.40)"),
    "bg-white/50"  : ("--color-surface",        "rgba(255,255,255,0.50)"),
    "bg-white/60"  : ("--color-surface",        "rgba(255,255,255,0.60)"),
    "bg-white/70"  : ("--color-surface",        "rgba(255,255,255,0.70)"),
    "bg-white/80"  : ("--color-surface",        "rgba(255,255,255,0.80)"),
    "bg-white/90"  : ("--color-surface",        "rgba(255,255,255,0.90)"),

    # Slate sangat terang → background halaman
    "bg-slate-50"  : ("--color-bg",             "#f8fafc"),
    "bg-slate-100" : ("--color-bg",             "#f1f5f9"),

    # Slate menengah → surface raised
    "bg-slate-200" : ("--color-surface",        "#e2e8f0"),
    "bg-slate-300" : ("--color-surface",        "#cbd5e1"),

    # Slate gelap → surface strong (navbar, header gelap)
    "bg-slate-700" : ("--color-surface-strong", "#334155"),
    "bg-slate-800" : ("--color-surface-strong", "#1e293b"),
    "bg-slate-900" : ("--color-surface-strong", "#0f172a"),

    # Opacity variants slate-50
    "bg-slate-50/50" : ("--color-bg",           "rgba(248,250,252,0.50)"),
    "bg-slate-50/80" : ("--color-bg",           "rgba(248,250,252,0.80)"),
}

# Regex untuk menemukan class attribute di HTML
# Match: class="..." atau class='...'  (termasuk multi-line via re.DOTALL)
RE_CLASS_ATTR = re.compile(
    r'(class\s*=\s*")((?:[^"\\]|\\.)*)(")|'   # double-quote
    r"(class\s*=\s*')((?:[^'\\]|\\.)*)(')  ",   # single-quote
    re.DOTALL
)

# Regex untuk menemukan style attribute yang sudah ada
RE_STYLE_ATTR = re.compile(
    r'(style\s*=\s*")((?:[^"\\]|\\.)*)(")| '
    r"(style\s*=\s*')((?:[^'\\]|\\.)*)(')  ",
    re.DOTALL
)

# ══════════════════════════════════════════════════════════════════
# TERMINAL COLORS
# ══════════════════════════════════════════════════════════════════

C   = "\033[96m"; W = "\033[97m"; G = "\033[92m"
Y   = "\033[93m"; R = "\033[91m"; DIM= "\033[2m"; B = "\033[1m"; RST= "\033[0m"
def hr(n=68): return C + "─"*n + RST


# ══════════════════════════════════════════════════════════════════
# CORE: bg class replacement
# ══════════════════════════════════════════════════════════════════

def classes_to_replace(class_str: str) -> dict[str, str]:
    """
    Dari string class="...", temukan bg-* classes yang perlu diganti.
    Return: { "bg-white": "--color-surface", ... }
    """
    classes = class_str.split()
    found   = {}
    for cls in classes:
        if cls in BG_MAP:
            found[cls] = BG_MAP[cls]
    return found


def replace_bg_in_tag(tag: str) -> tuple[str, int]:
    """
    Proses satu HTML tag (misal <div class="bg-white p-4" ...>).
    Ganti bg-* classes dengan inline style.
    Return: (tag_baru, jumlah_penggantian)
    """
    if 'class=' not in tag and "class =" not in tag:
        return tag, 0

    # Parse class attribute
    # Cari class="..." atau class='...'
    cls_match = re.search(r'''class\s*=\s*(?:"([^"]*?)"|'([^']*?)')''', tag)
    if not cls_match:
        return tag, 0

    class_str = cls_match.group(1) or cls_match.group(2) or ""
    to_replace = classes_to_replace(class_str)

    if not to_replace:
        return tag, 0

    # Hapus bg classes dari class=""
    new_class_str = class_str
    bg_styles = []

    for cls, (var, _fallback) in to_replace.items():
        # Hapus class
        new_class_str = re.sub(r'\b' + re.escape(cls) + r'\b', '', new_class_str)
        # Tentukan property CSS
        if var in ("--color-surface", "--color-bg", "--color-surface-strong"):
            prop = "background"
        else:
            prop = "background"
        bg_styles.append(f"{prop}:var({var})")

    # Bersihkan spasi berlebih di class string
    new_class_str = re.sub(r'\s+', ' ', new_class_str).strip()

    # Cari style attribute yang sudah ada
    style_match = re.search(r'''style\s*=\s*(?:"([^"]*?)"|'([^']*?)')''', tag)

    if style_match:
        # Tambahkan ke style yang sudah ada
        existing_style = (style_match.group(1) or style_match.group(2) or "").rstrip(";")
        new_style_str  = existing_style + (";" if existing_style else "") + ";".join(bg_styles)
        # Ganti style attribute
        old_style_full = style_match.group(0)
        quote = '"' if '"' in old_style_full else "'"
        new_style_full = f'style={quote}{new_style_str}{quote}'
        tag = tag.replace(old_style_full, new_style_full, 1)
    else:
        # Sisipkan style attribute baru setelah class attribute
        new_style_str  = ";".join(bg_styles)
        old_class_full = cls_match.group(0)
        quote_used     = '"' if '"' in old_class_full else "'"
        new_class_full = f'class={quote_used}{new_class_str}{quote_used} style="{new_style_str}"'
        tag = tag.replace(old_class_full, new_class_full, 1)

    # Update class attribute dengan yang sudah bersih
    if style_match:
        # Hanya update class (style sudah diupdate di atas)
        old_class_full = cls_match.group(0)
        quote_used     = '"' if '"' in old_class_full else "'"
        new_class_full = f'class={quote_used}{new_class_str}{quote_used}'
        tag = tag.replace(old_class_full, new_class_full, 1)

    return tag, len(to_replace)


def process_html(content: str) -> tuple[str, int, list[str]]:
    """
    Proses seluruh HTML content.
    Return: (content_baru, total_penggantian, list_detail)
    """
    total   = 0
    details = []

    # Match semua opening tags HTML (bukan self-closing style, bukan comment)
    # Pattern: <tagname ...>  tanpa melewati newline di dalam tag name
    tag_pattern = re.compile(
        r'<([a-zA-Z][a-zA-Z0-9-]*)(\s[^>]*?)?>',
        re.DOTALL
    )

    def replace_tag(m: re.Match) -> str:
        nonlocal total
        original = m.group(0)
        new_tag, n = replace_bg_in_tag(original)
        if n > 0:
            total += n
            # Catat class yang diganti (untuk --stats)
            cls_m = re.search(r'''class\s*=\s*(?:"([^"]*?)"|'([^']*?)')''', original)
            if cls_m:
                cls_str  = cls_m.group(1) or cls_m.group(2) or ""
                replaced = [c for c in cls_str.split() if c in BG_MAP]
                details.extend(replaced)
        return new_tag

    new_content = tag_pattern.sub(replace_tag, content)
    return new_content, total, details


# ══════════════════════════════════════════════════════════════════
# CSS OVERRIDES — Cara B: text-slate-* dan border-slate-*
# ══════════════════════════════════════════════════════════════════

CSS_OVERRIDES = '''/* ============================================================
   LUMRA THEME OVERRIDES — Auto-generated by lumra_theme_migrate.py
   {timestamp}
   ============================================================
   Cara B: CSS override untuk Tailwind text-* dan border-* classes.
   HTML tidak diubah — design system yang override saat dark mode.

   Import di lumra_design_system.css:
     @import url('theme_overrides.css');
   Atau tambahkan <link> di base.html setelah design system.
   ============================================================ */


/* ══════════════════════════════════════════════════════════════
   TEXT COLOR OVERRIDES
   Semua varian text-slate-* → ikut CSS variable saat dark mode
══════════════════════════════════════════════════════════════ */

/* Teks utama — heading, body, label penting */
[data-theme="dark"] .text-slate-900,
[data-theme="dark"] .text-slate-800,
[data-theme="dark"] .text-gray-900,
[data-theme="dark"] .text-gray-800 {{
  color: var(--color-text) !important;
}}

/* Teks muted — subtitle, helper text */
[data-theme="dark"] .text-slate-700,
[data-theme="dark"] .text-slate-600,
[data-theme="dark"] .text-gray-700,
[data-theme="dark"] .text-gray-600 {{
  color: var(--color-text-muted) !important;
}}

/* Teks subtle — placeholder, hint, secondary */
[data-theme="dark"] .text-slate-500,
[data-theme="dark"] .text-slate-400,
[data-theme="dark"] .text-gray-500,
[data-theme="dark"] .text-gray-400 {{
  color: var(--color-text-subtle) !important;
}}

/* Teks sangat subtle — disabled, decorative */
[data-theme="dark"] .text-slate-300,
[data-theme="dark"] .text-slate-200,
[data-theme="dark"] .text-gray-300,
[data-theme="dark"] .text-gray-200 {{
  color: rgba(255,255,255,0.25) !important;
}}

/* Teks putih tetap putih */
[data-theme="dark"] .text-white {{
  color: var(--color-text) !important;
}}

/* Teks hitam → dibalik ke putih */
[data-theme="dark"] .text-black,
[data-theme="dark"] .text-gray-950 {{
  color: var(--color-text) !important;
}}


/* ══════════════════════════════════════════════════════════════
   BORDER COLOR OVERRIDES
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] .border-slate-100,
[data-theme="dark"] .border-slate-200,
[data-theme="dark"] .border-gray-100,
[data-theme="dark"] .border-gray-200 {{
  border-color: var(--color-border) !important;
}}

[data-theme="dark"] .border-slate-300,
[data-theme="dark"] .border-slate-400,
[data-theme="dark"] .border-gray-300,
[data-theme="dark"] .border-gray-400 {{
  border-color: rgba(255,255,255,0.12) !important;
}}

[data-theme="dark"] .border-white,
[data-theme="dark"] .border-white\\/20,
[data-theme="dark"] .border-white\\/40,
[data-theme="dark"] .border-white\\/80 {{
  border-color: var(--color-border) !important;
}}

/* Divide (hr separator) */
[data-theme="dark"] .divide-slate-100 > * + *,
[data-theme="dark"] .divide-slate-200 > * + * {{
  border-color: var(--color-border) !important;
}}


/* ══════════════════════════════════════════════════════════════
   BACKGROUND OVERRIDES — bg-white/opacity variants
   (Backup untuk yang tidak tertangkap script Python)
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] .bg-white {{
  background: var(--color-surface) !important;
}}
[data-theme="dark"] .bg-white\\/40,
[data-theme="dark"] .bg-white\\/50,
[data-theme="dark"] .bg-white\\/60,
[data-theme="dark"] .bg-white\\/70,
[data-theme="dark"] .bg-white\\/80,
[data-theme="dark"] .bg-white\\/90 {{
  background: var(--color-surface) !important;
}}
[data-theme="dark"] .bg-slate-50,
[data-theme="dark"] .bg-slate-100 {{
  background: var(--color-bg) !important;
}}
[data-theme="dark"] .bg-slate-200,
[data-theme="dark"] .bg-slate-300 {{
  background: rgba(255,255,255,0.06) !important;
}}
[data-theme="dark"] .bg-slate-50\\/50,
[data-theme="dark"] .bg-slate-50\\/80 {{
  background: var(--color-bg) !important;
}}


/* ══════════════════════════════════════════════════════════════
   RING / OUTLINE COLOR OVERRIDES
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] .ring-slate-200,
[data-theme="dark"] .ring-slate-300 {{
  --tw-ring-color: rgba(255,255,255,0.10);
}}
[data-theme="dark"] .ring-white {{
  --tw-ring-color: rgba(255,255,255,0.15);
}}


/* ══════════════════════════════════════════════════════════════
   PLACEHOLDER COLOR OVERRIDES
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] .placeholder-slate-300::placeholder,
[data-theme="dark"] .placeholder-slate-400::placeholder,
[data-theme="dark"] .placeholder\\:text-slate-300::placeholder,
[data-theme="dark"] .placeholder\\:text-slate-400::placeholder {{
  color: var(--color-text-subtle) !important;
}}


/* ══════════════════════════════════════════════════════════════
   BACKDROP / GLASSMORPHISM CLASS OVERRIDES
   Untuk class inline seperti backdrop-blur-md di template
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] .backdrop-blur-md,
[data-theme="dark"] .backdrop-blur-xl,
[data-theme="dark"] .backdrop-blur-2xl {{
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
}}


/* ══════════════════════════════════════════════════════════════
   INPUT / FORM OVERRIDES
   Tailwind form classes yang perlu ikut dark mode
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] input:not([type="range"]):not([type="checkbox"]):not([type="radio"]),
[data-theme="dark"] textarea,
[data-theme="dark"] select {{
  background    : rgba(255,255,255,0.05) !important;
  border-color  : var(--color-border) !important;
  color         : var(--color-text) !important;
}}

[data-theme="dark"] input:focus:not([type="range"]):not([type="checkbox"]):not([type="radio"]),
[data-theme="dark"] textarea:focus,
[data-theme="dark"] select:focus {{
  background    : rgba(255,255,255,0.08) !important;
  border-color  : var(--color-primary) !important;
  box-shadow    : var(--shadow-focus) !important;
}}


/* ══════════════════════════════════════════════════════════════
   TABLE OVERRIDES
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] table,
[data-theme="dark"] .table {{
  color: var(--color-text);
}}

[data-theme="dark"] thead,
[data-theme="dark"] .thead {{
  background: rgba(255,255,255,0.03) !important;
}}

[data-theme="dark"] th {{
  color        : var(--color-text-muted) !important;
  border-color : var(--color-border) !important;
}}

[data-theme="dark"] td {{
  border-color: var(--color-border) !important;
  color       : var(--color-text) !important;
}}

[data-theme="dark"] tr:hover td {{
  background: var(--color-primary-a05) !important;
}}


/* ══════════════════════════════════════════════════════════════
   MODAL / DROPDOWN OVERRIDES
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] [class*="bg-white"][class*="rounded"],
[data-theme="dark"] [class*="bg-white"][class*="shadow"] {{
  background  : var(--color-surface) !important;
  border-color: var(--color-border) !important;
}}

/* Dropdown options */
[data-theme="dark"] option {{
  background: #111827;
  color     : var(--color-text);
}}


/* ══════════════════════════════════════════════════════════════
   SCROLLBAR OVERRIDES
══════════════════════════════════════════════════════════════ */

[data-theme="dark"] ::-webkit-scrollbar-thumb {{
  background: rgba(255,255,255,0.12);
}}
[data-theme="dark"] ::-webkit-scrollbar-thumb:hover {{
  background: rgba(255,255,255,0.20);
}}
'''


# ══════════════════════════════════════════════════════════════════
# FILE UTILS
# ══════════════════════════════════════════════════════════════════

def is_skip(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    return any(pat.lower() in parts for pat in SKIP_PATTERNS)


def backup_file(path: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest  = backup_dir / f"{path.stem}_{stamp}{path.suffix}"
    shutil.copy2(path, dest)


# ══════════════════════════════════════════════════════════════════
# MAIN RUNNERS
# ══════════════════════════════════════════════════════════════════

def run_stats(root: Path) -> None:
    """Hitung statistik bg-* classes di semua template."""
    html_files = [p for p in root.rglob("*.html") if not is_skip(p)]
    counter    = defaultdict(int)
    file_count = 0

    for path in html_files:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        # Cari semua class attributes
        for m in re.finditer(r'''class\s*=\s*(?:"([^"]*?)"|'([^']*?)')''', content):
            cls_str = m.group(1) or m.group(2) or ""
            found   = classes_to_replace(cls_str)
            if found:
                file_count += 1
                for cls in found:
                    counter[cls] += 1
        # Break double-count per file — kita hitung per-occurrence bukan per-file
    
    print(f"\n{hr()}")
    print(f"  {B}STATISTIK bg-* classes{RST}\n")
    print(f"  {DIM}File ditemukan : {len(html_files)}{RST}")
    print(f"  {DIM}Occurrence     : {sum(counter.values())}{RST}\n")
    for cls, n in sorted(counter.items(), key=lambda x: -x[1]):
        var, _ = BG_MAP[cls]
        print(f"  {Y}{cls:<25}{RST}  {DIM}×{n:<5}{RST}  → {G}var({var}){RST}")
    print(hr())


def run_apply(root: Path, backup_dir: Path, dry_run: bool, target_file: str | None) -> None:
    """Apply bg-* replacement ke semua (atau satu) file HTML."""
    if target_file:
        html_files = list(root.rglob(target_file))
        if not html_files:
            print(f"  {R}File tidak ditemukan: {target_file}{RST}")
            return
    else:
        html_files = [p for p in root.rglob("*.html") if not is_skip(p)]

    total_files = 0
    total_reps  = 0

    print(f"\n{hr()}")
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"  {B}BG CLASS MIGRATION  [{mode}]{RST}\n")

    for path in sorted(html_files):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  {R}ERR  {path.name}: {e}{RST}")
            continue

        new_content, n, details = process_html(content)

        if n == 0:
            continue

        cls_summary = ", ".join(sorted(set(details)))
        if dry_run:
            print(f"  {Y}WOULD FIX  {path.name:<45}{RST}  {DIM}{n} replacement — {cls_summary}{RST}")
        else:
            backup_file(path, backup_dir)
            path.write_text(new_content, encoding="utf-8")
            print(f"  {G}FIXED      {path.name:<45}{RST}  {DIM}{n} replacement{RST}")

        total_files += 1
        total_reps  += n

    print(f"\n  {B}Selesai:{RST}  {G}{total_reps} replacement{RST} di {G}{total_files} file{RST}")
    if dry_run:
        print(f"  {Y}Jalankan tanpa --dry-run untuk apply.{RST}")
    else:
        print(f"  {DIM}Backup: {backup_dir}{RST}")
    print(hr())


def run_css(output_path: Path) -> None:
    """Generate CSS overrides file (Cara B)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    css_content = CSS_OVERRIDES.format(timestamp=timestamp)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(css_content, encoding="utf-8")
    print(f"\n  {G}✅ CSS overrides disimpan: {output_path}{RST}")
    print(f"  {DIM}Tambahkan ke base.html setelah lumra_design_system.css:{RST}")
    print(f'  {W}<link rel="stylesheet" href="{{% static \'css/theme_overrides.css\' %}}\">{RST}\n')


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="LUMRA Theme Migrator — buat semua template ikut light/dark toggle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--root",     type=Path, default=DEFAULT_ROOT)
    p.add_argument("--backup",   type=Path, default=DEFAULT_BACKUP)
    p.add_argument("--output",   type=Path, default=DEFAULT_OUTPUT,
                   help="Path output CSS overrides")
    p.add_argument("--dry-run",  action="store_true",
                   help="Preview saja, tidak ubah file")
    p.add_argument("--apply",    action="store_true",
                   help="Apply bg replacement ke semua HTML")
    p.add_argument("--stats",    action="store_true",
                   help="Tampilkan statistik bg-* classes")
    p.add_argument("--css-only", action="store_true",
                   help="Generate CSS overrides saja, tidak ubah HTML")
    p.add_argument("--file",     type=str, default=None,
                   help="Apply hanya ke satu file (nama file saja, bukan path)")
    return p.parse_args()


def main():
    args = parse_args()

    # Default: dry-run jika tidak ada --apply
    if not args.apply and not args.stats and not args.css_only:
        args.dry_run = True

    print(f"\n{hr('═' if True else '─', 68)}")
    print(f"  {B}LUMRA Theme Migrator{RST}")
    print(f"  Root   : {DIM}{args.root}{RST}")
    print(f"  Mode   : {W}{'DRY-RUN' if args.dry_run else 'APPLY' if args.apply else 'INFO'}{RST}")
    print(hr())

    if args.stats:
        run_stats(args.root)

    if args.dry_run or args.apply:
        run_apply(args.root, args.backup, dry_run=args.dry_run, target_file=args.file)

    # Selalu generate CSS overrides kecuali --stats saja
    if not args.stats:
        run_css(args.output)


def hr(char="─", n=68):
    return "\033[96m" + char*n + "\033[0m"


if __name__ == "__main__":
    main()