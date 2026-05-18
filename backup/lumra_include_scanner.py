#!/usr/bin/env python3
"""
lumra_include_scanner.py

Scan semua template Django dan identifikasi pola CSS class yang
berulang dan sebaiknya diextract menjadi {% include %} partial.

Usage:
    python lumra_include_scanner.py
    python lumra_include_scanner.py --template-dir lumra_config/templates
    python lumra_include_scanner.py --output report.md
    python lumra_include_scanner.py --fix --dry-run
"""

import os
import re
import argparse
from collections import defaultdict
from pathlib import Path


# ─────────────────────────────────────────────
# Pola komponen yang dikenali
# ─────────────────────────────────────────────

COMPONENT_PATTERNS = {
    "bg_blob": {
        "classes": ["bg-blob", "bg-blob-1", "bg-blob-2", "bg-blob-3"],
        "partial": "base/partials/bg_bg_blob.html",
        "description": "Background blob decoration (reports, master_data)",
    },
    "blob": {
        "classes": ["blob", "blob-a", "blob-b", "blob-c"],
        "partial": "base/partials/bg_blob.html",
        "description": "Blob decoration (inventory, settings, marketing)",
    },
    "orb": {
        "classes": ["orb", "orb-1", "orb-2", "orb-3"],
        "partial": "base/partials/bg_orb.html",
        "description": "Orb decoration (sales_insight)",
    },
    "sh_bg_orb": {
        "classes": ["sh-bg-orb", "sh-bg-orb-1", "sh-bg-orb-2", "sh-bg-orb-3"],
        "partial": "base/partials/bg_sh_orb.html",
        "description": "Shader orb decoration (sales_intelligence)",
    },
    "kpi_card": {
        "classes": ["kpi-glass", "kpi-icon", "kpi-value", "kpi-label"],
        "partial": "base/kpi_card.html",
        "description": "KPI card widget",
    },
    "glass_card": {
        "classes": ["glass", "glass-card"],
        "partial": "base/partials/glass_card.html",
        "description": "Glass container wrapper",
    },
    "form_field": {
        "classes": ["f-input", "f-label", "inp", "err"],
        "partial": "base/partials/form_field.html",
        "description": "Styled form field",
    },
    "reveal": {
        "classes": ["reveal", "visible"],
        "partial": "base/partials/reveal_script.html",
        "description": "Scroll reveal animation (JS needed)",
    },
    "auth_page": {
        "classes": ["auth-page-bg", "auth-blob", "auth-card"],
        "partial": "base/partials/auth_bg.html",
        "description": "Auth page background",
    },
}

# Template yang sudah pakai include — skip dari laporan
ALREADY_USING_INCLUDE = {
    "base/alert.html",
    "base/base.html",
    "lumra_pages/sales_insight/dashboard.html",
}


# ─────────────────────────────────────────────
# Scanner
# ─────────────────────────────────────────────

def find_templates(template_dir: Path) -> list[Path]:
    """Cari semua file .html dalam direktori template."""
    return sorted(template_dir.rglob("*.html"))


def extract_classes(html_content: str) -> set[str]:
    """Ekstrak semua CSS class dari atribut class="..." di HTML."""
    classes = set()
    # Match class="..." atau class='...'
    for match in re.finditer(r'class=["\']([^"\']+)["\']', html_content):
        for cls in match.group(1).split():
            classes.add(cls.strip())
    return classes


def check_uses_include(html_content: str) -> list[str]:
    """Cari semua {% include %} yang sudah dipakai di template."""
    return re.findall(r'{%[-\s]*include\s+"([^"]+)"', html_content)


def detect_components(html_content: str) -> dict[str, list[str]]:
    """
    Deteksi komponen mana saja yang hadir berdasarkan class yang ditemukan.
    Return: { component_name: [matched_classes] }
    """
    found_classes = extract_classes(html_content)
    detected = {}
    for comp_name, comp_info in COMPONENT_PATTERNS.items():
        matches = [c for c in comp_info["classes"] if c in found_classes]
        if len(matches) >= 2:  # Minimal 2 class dari pola = komponen dipakai
            detected[comp_name] = matches
    return detected


# ─────────────────────────────────────────────
# Fixer (--fix mode)
# ─────────────────────────────────────────────

# Template HTML yang akan disisipkan sebagai pengganti blob inline
INCLUDE_SNIPPETS = {
    "bg_blob": '{% include "base/partials/bg_blob.html" %}',
    "bg_blob_report": '{% include "base/partials/bg_bg_blob.html" %}',
    "orb": '{% include "base/partials/bg_orb.html" %}',
    "kpi_card": (
        '{% include "base/kpi_card.html" with '
        'title="..." value=... icon="..." %}'
    ),
}

# Pola div blob yang sering muncul inline
BLOB_INLINE_PATTERN = re.compile(
    r'<div\s+class=["\'](?:bg-)?blob(?:-[abc123])?\s*["\']>\s*</div>\s*',
    re.MULTILINE
)

BG_BLOB_INLINE_PATTERN = re.compile(
    r'(<div\s+class=["\']bg-blob["\']>\s*</div>\s*'
    r'<div\s+class=["\']bg-blob-1["\']>\s*</div>\s*'
    r'<div\s+class=["\']bg-blob-2["\']>\s*</div>\s*'
    r'(?:<div\s+class=["\']bg-blob-3["\']>\s*</div>\s*)?)',
    re.MULTILINE | re.DOTALL
)

def fix_template(path: Path, dry_run: bool = True) -> tuple[bool, str]:
    """
    Coba replace pola blob/orb inline dengan {% include %}.
    Return: (changed: bool, diff_summary: str)
    """
    content = path.read_text(encoding="utf-8")
    new_content = content

    changes = []

    # Ganti bg-blob block
    if re.search(r'class=["\']bg-blob["\']', content):
        new_content = BG_BLOB_INLINE_PATTERN.sub(
            '{% include "base/partials/bg_bg_blob.html" %}\n',
            new_content
        )
        if new_content != content:
            changes.append("bg-blob → include bg_bg_blob.html")
            content = new_content

    changed = new_content != path.read_text(encoding="utf-8")

    if changed and not dry_run:
        path.write_text(new_content, encoding="utf-8")

    return changed, "; ".join(changes) if changes else "no change"


# ─────────────────────────────────────────────
# Reporter
# ─────────────────────────────────────────────

def generate_report(
    template_dir: Path,
    fix: bool = False,
    dry_run: bool = True,
) -> str:
    templates = find_templates(template_dir)

    # Stats
    total = len(templates)
    has_inline = 0
    has_include = 0
    component_frequency: dict[str, int] = defaultdict(int)
    template_report: list[dict] = []

    for tpl_path in templates:
        try:
            content = tpl_path.read_text(encoding="utf-8")
        except Exception:
            continue

        rel_path = str(tpl_path.relative_to(template_dir)).replace("\\", "/")
        includes = check_uses_include(content)
        components = detect_components(content)
        all_classes = extract_classes(content)

        if components:
            has_inline += 1
        if includes:
            has_include += 1

        for comp in components:
            component_frequency[comp] += 1

        fix_result = None
        if fix:
            changed, summary = fix_template(tpl_path, dry_run=dry_run)
            fix_result = f"{'[DRY RUN] ' if dry_run else ''}{'✓ ' + summary if changed else '— no change'}"

        template_report.append({
            "path": rel_path,
            "inline_count": len(all_classes),
            "components": components,
            "includes": includes,
            "fix": fix_result,
        })

    # Sort by inline class count desc
    template_report.sort(key=lambda x: x["inline_count"], reverse=True)

    # Build markdown
    lines = [
        "# Lumra Include Scanner — Laporan",
        "",
        f"**Total template:** {total}  ",
        f"**Punya komponen inline:** {has_inline}  ",
        f"**Sudah pakai include:** {has_include}  ",
        "",
        "---",
        "",
        "## Frekuensi Komponen Inline",
        "",
        "| Komponen | Dipakai di N Template | Partial yang Perlu Dibuat |",
        "|---|---|---|",
    ]
    for comp, freq in sorted(component_frequency.items(), key=lambda x: -x[1]):
        info = COMPONENT_PATTERNS[comp]
        lines.append(f"| `{comp}` | {freq} | `{info['partial']}` |")

    lines += [
        "",
        "---",
        "",
        "## Detail per Template (urut: class inline terbanyak)",
        "",
        "| Template | Class Count | Komponen Terdeteksi | Include Saat Ini |",
        "|---|---|---|---|",
    ]

    for item in template_report:
        if not item["components"]:
            continue
        comp_names = ", ".join(f"`{c}`" for c in item["components"])
        inc_names = ", ".join(f"`{i}`" for i in item["includes"]) if item["includes"] else "—"
        fix_note = f" ← {item['fix']}" if item["fix"] else ""
        lines.append(
            f"| `{item['path']}` | {item['inline_count']} "
            f"| {comp_names} | {inc_names}{fix_note} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Template yang Sudah Bersih (tidak ada komponen inline)",
        "",
    ]
    clean = [t for t in template_report if not t["components"]]
    if clean:
        for item in clean:
            inc_names = ", ".join(f"`{i}`" for i in item["includes"]) if item["includes"] else "—"
            lines.append(f"- `{item['path']}` — includes: {inc_names}")
    else:
        lines.append("*(belum ada)*")

    lines += ["", "---", "", "*Dibuat oleh lumra_include_scanner.py*"]
    return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scan Lumra templates untuk pola CSS inline yang perlu di-include-kan"
    )
    parser.add_argument(
        "--template-dir",
        default="lumra_config/templates",
        help="Path ke direktori template (default: lumra_config/templates)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Simpan laporan ke file .md (default: print ke stdout)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Coba otomatis ganti blob inline dengan {% include %}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Jika --fix, hanya tampilkan perubahan tanpa tulis file (default: True)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Jika --fix, tulis perubahan ke file (override --dry-run)",
    )
    args = parser.parse_args()

    template_dir = Path(args.template_dir)
    if not template_dir.exists():
        print(f"[ERROR] Direktori tidak ditemukan: {template_dir}")
        return

    dry_run = not args.write  # --write mengaktifkan mode tulis
    report = generate_report(template_dir, fix=args.fix, dry_run=dry_run)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"[OK] Laporan disimpan ke: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()