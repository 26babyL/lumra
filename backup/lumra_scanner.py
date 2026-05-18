#!/usr/bin/env python3
"""
lumra_scanner.py — Template HTML Scanner
==========================================
Jalankan dari root project lumra:
    python lumra_scanner.py

Output:
    blueprint_data.json  ← upload file ini ke Claude

Tidak mengubah file apapun. Read-only.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ── Config ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent  # folder tempat script ini dijalankan

TEMPLATE_DIRS = [
    "lumra_config/templates/lumra_pages",
    "lumra_config/templates/base",
]

BACKUP_PREFIXES = ("_", ".")  # folder dengan prefix ini di-skip

# CSS classes yang kita lacak keberadaannya
TRACKED_CLASSES = [
    # Glass components
    "lumra-glass", "glass-card", "glass", "lumra-card",
    "kpi-card", "kpi-glass", "lumra-kpi",
    "kpi-label", "kpi-val", "kpi-value", "delta",
    # Table
    "lumra-table",
    # Badge & chip
    "lumra-badge", "status-chip", "status-badge", "status-pill",
    "chip-emerald", "chip-amber", "chip-rose", "chip-sky",
    "chip-info", "chip-neutral", "chip-accent",
    # Form
    "lumra-input", "f-input", "form-input", "lumra-label", "f-label",
    "form-label", "f-field",
    # Button
    "lumra-btn", "lumra-btn-primary", "btn-add", "btn-primary",
    # Layout
    "reveal", "bg-blob", "orb",
    # Alert
    "lumra-alert",
    # Misc
    "loc-card", "metric-row", "section-label", "nav-tab",
    "progress-track", "progress-fill", "lumra-skeleton",
    "modal-glass", "modal-overlay",
]

# Font imports yang tidak diizinkan
FORBIDDEN_FONTS = [
    "fonts.googleapis.com/css2?family=Syne",
    "fonts.googleapis.com/css2?family=Plus+Jakarta+Sans",
]

# Warna hardcoded yang tidak boleh ada di luar :root
HARDCODED_VALUES = [
    "rgba(255, 255, 255, 0.82)",
    "rgba(255,255,255,0.82)",
    "rgba(255, 255, 255, 0.72)",
    "rgba(255,255,255,0.72)",
    "rgba(15, 23, 42, 0.82)",
    "#059669",
    "#00674F",
]


# ── Helpers ─────────────────────────────────────────────────────────────────────

def is_backup(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    return any(part.startswith(BACKUP_PREFIXES) for part in rel.parts)


def find_html_files(root: Path) -> list[Path]:
    files = []
    for tdir in TEMPLATE_DIRS:
        d = root / tdir
        if not d.exists():
            continue
        for fp in sorted(d.rglob("*.html")):
            if not is_backup(fp, root):
                files.append(fp)
    return files


# ── Per-file analysis ──────────────────────────────────────────────────────────

def analyze_file(fp: Path, root: Path) -> dict:
    try:
        text = fp.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e)}

    lines = text.splitlines()
    rel = str(fp.relative_to(root)).replace("\\", "/")

    result = {
        "path": rel,
        "module": _get_module(rel),
        "name": fp.stem,
        "size_lines": len(lines),
        "size_bytes": fp.stat().st_size,

        # Template structure
        "extends": None,
        "blocks": [],
        "includes": [],

        # Design system usage
        "uses_classes": [],
        "font_imports": [],           # semua @import font
        "forbidden_fonts": [],        # font yang tidak diizinkan
        "hardcoded_values": [],       # { line, value }
        "has_style_block": False,
        "style_block_lines": 0,

        # Layout indicators
        "is_standalone": False,       # tidak extends base
        "has_kpi_cards": False,
        "has_table": False,
        "has_form": False,
        "has_chart": False,
        "has_modal": False,
        "has_approval": False,
        "has_export": False,
        "has_pagination": False,
        "has_search": False,
        "has_date_filter": False,
        "has_blob": False,

        # URL patterns (dari href/action/url tag)
        "url_names": [],

        # Issues
        "issues": [],
    }

    # ── Parse line by line ──────────────────────────────────────────────────────
    in_style = False
    style_line_count = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # extends
        m = re.search(r"""\{%[-\s]*extends\s+['"]([^'"]+)['"]""", line)
        if m:
            result["extends"] = m.group(1)

        # blocks
        for bm in re.finditer(r"\{%[-\s]*block\s+(\w+)", line):
            bname = bm.group(1)
            if bname not in result["blocks"]:
                result["blocks"].append(bname)

        # includes
        for im in re.finditer(r"""\{%[-\s]*include\s+['"]([^'"]+)['"]""", line):
            inc = im.group(1)
            if inc not in result["includes"]:
                result["includes"].append(inc)

        # url names
        for um in re.finditer(r"""\{%[-\s]*url\s+['"]([^'"]+)['"]""", line):
            uname = um.group(1)
            if uname not in result["url_names"]:
                result["url_names"].append(uname)

        # style blocks
        if "<style" in stripped.lower():
            in_style = True
            result["has_style_block"] = True
        if in_style:
            style_line_count += 1
        if "</style>" in stripped.lower():
            in_style = False

        # font imports
        if "@import" in line and "fonts.googleapis" in line:
            # extract URL
            fm = re.search(r"@import\s+url\(['\"]?([^'\")\s]+)['\"]?\)", line)
            url = fm.group(1) if fm else line.strip()
            if url not in result["font_imports"]:
                result["font_imports"].append(url)
            for ff in FORBIDDEN_FONTS:
                if ff in line:
                    result["forbidden_fonts"].append({
                        "line": i, "value": url
                    })

        # hardcoded values (skip :root dan komentar)
        is_token_def = bool(re.match(r"\s*--", line))
        is_comment = "/*" in line or "<!--" in line or stripped.startswith("*")
        if not is_token_def and not is_comment:
            for val in HARDCODED_VALUES:
                if val in line:
                    result["hardcoded_values"].append({
                        "line": i,
                        "value": val,
                        "context": stripped[:100]
                    })

        # CSS class detection (dalam class="..." attribute atau CSS rule)
        for cls in TRACKED_CLASSES:
            if cls in line and cls not in result["uses_classes"]:
                # verifikasi bahwa ini bukan komentar
                if f'"{cls}"' in line or f"'{cls}'" in line \
                        or f" {cls}" in line or f".{cls}" in line \
                        or f'class="{cls}' in line:
                    result["uses_classes"].append(cls)

    # ── Indicator flags ─────────────────────────────────────────────────────────
    full_text_lower = text.lower()

    result["style_block_lines"] = style_line_count
    result["is_standalone"] = result["extends"] is None
    result["has_kpi_cards"] = any(c in result["uses_classes"]
                                   for c in ["kpi-card", "kpi-glass", "lumra-kpi"])
    result["has_table"] = "lumra-table" in result["uses_classes"] \
                          or "<table" in full_text_lower
    result["has_form"] = "<form" in full_text_lower \
                         or any(c in result["uses_classes"]
                                for c in ["lumra-input", "f-input", "form-input"])
    result["has_chart"] = any(k in full_text_lower
                              for k in ["chart.js", "chartjs", "apexchart",
                                        "echarts", "canvas id=", "<canvas"])
    result["has_modal"] = "modal" in full_text_lower \
                          or "modal-glass" in result["uses_classes"]
    result["has_approval"] = "approval_modal" in text \
                              or "approve" in full_text_lower
    result["has_export"] = any(k in full_text_lower
                               for k in ["export", "download", "xlsx", "csv", "pdf"])
    result["has_pagination"] = any(k in full_text_lower
                                   for k in ["pagination", "page-btn",
                                             "paginator", "next_page", "prev_page"])
    result["has_search"] = any(k in full_text_lower
                               for k in ["search", "cari", "q=", "filter"])
    result["has_date_filter"] = any(k in full_text_lower
                                    for k in ["date_from", "date_to", "tanggal",
                                              "daterange", "datepicker"])
    result["has_blob"] = "bg-blob" in text or "bg_blob" in text

    # ── Issues ──────────────────────────────────────────────────────────────────
    if result["forbidden_fonts"]:
        result["issues"].append({
            "type": "forbidden-font",
            "count": len(result["forbidden_fonts"]),
            "fix": "python validate.py --fix-fonts"
        })
    if result["hardcoded_values"]:
        result["issues"].append({
            "type": "hardcoded-value",
            "count": len(result["hardcoded_values"]),
            "fix": "Ganti dengan var(--token)"
        })
    if result["is_standalone"] and "auth" not in rel and "etc" not in rel:
        result["issues"].append({
            "type": "missing-extends",
            "count": 1,
            "fix": "Tambahkan {% extends 'base/base.html' %}"
        })
    if result["has_style_block"] and result["style_block_lines"] > 100:
        result["issues"].append({
            "type": "large-style-block",
            "count": result["style_block_lines"],
            "fix": "Pertimbangkan pindahkan ke lumra_components.css"
        })

    return result


def _get_module(rel_path: str) -> str:
    parts = rel_path.replace("\\", "/").split("/")
    # cari segment setelah lumra_pages atau base
    for i, part in enumerate(parts):
        if part in ("lumra_pages", "base"):
            return parts[i + 1] if i + 1 < len(parts) else "root"
    return "unknown"


# ── Aggregate stats ────────────────────────────────────────────────────────────

def build_summary(files_data: list) -> dict:
    modules = defaultdict(list)
    total_issues = defaultdict(int)
    class_usage = defaultdict(int)
    all_forbidden_fonts = []
    all_hardcodes = []
    standalone_pages = []

    for f in files_data:
        if "error" in f:
            continue
        modules[f["module"]].append(f["name"])

        for issue in f.get("issues", []):
            total_issues[issue["type"]] += issue["count"]

        for cls in f.get("uses_classes", []):
            class_usage[cls] += 1

        if f.get("forbidden_fonts"):
            all_forbidden_fonts.append({
                "file": f["path"],
                "fonts": f["forbidden_fonts"]
            })

        if f.get("hardcoded_values"):
            all_hardcodes.append({
                "file": f["path"],
                "values": f["hardcoded_values"]
            })

        if f.get("is_standalone") and f["module"] not in ("auth", "etc"):
            standalone_pages.append(f["path"])

    return {
        "total_files": len(files_data),
        "modules": {k: {"count": len(v), "files": v}
                    for k, v in sorted(modules.items())},
        "issues_summary": dict(total_issues),
        "class_usage": dict(sorted(class_usage.items(),
                                   key=lambda x: -x[1])),
        "forbidden_font_files": all_forbidden_fonts,
        "hardcode_files": all_hardcodes,
        "standalone_pages": standalone_pages,
        "feature_stats": {
            "has_kpi_cards":   sum(1 for f in files_data if f.get("has_kpi_cards")),
            "has_table":       sum(1 for f in files_data if f.get("has_table")),
            "has_form":        sum(1 for f in files_data if f.get("has_form")),
            "has_chart":       sum(1 for f in files_data if f.get("has_chart")),
            "has_modal":       sum(1 for f in files_data if f.get("has_modal")),
            "has_export":      sum(1 for f in files_data if f.get("has_export")),
            "has_pagination":  sum(1 for f in files_data if f.get("has_pagination")),
            "has_search":      sum(1 for f in files_data if f.get("has_search")),
            "has_date_filter": sum(1 for f in files_data if f.get("has_date_filter")),
            "has_blob":        sum(1 for f in files_data if f.get("has_blob")),
            "has_approval":    sum(1 for f in files_data if f.get("has_approval")),
        }
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"\nLumra Template Scanner")
    print(f"Root: {ROOT.resolve()}")
    print("─" * 50)

    files = find_html_files(ROOT)
    if not files:
        print("  ✗ Tidak ada file HTML ditemukan.")
        print("  Pastikan script dijalankan dari root project lumra/")
        print("  (folder yang berisi lumra_config/)")
        return

    print(f"  Ditemukan {len(files)} file HTML aktif")
    print("  Scanning", end="", flush=True)

    files_data = []
    for i, fp in enumerate(files):
        data = analyze_file(fp, ROOT)
        files_data.append(data)
        if (i + 1) % 10 == 0:
            print(".", end="", flush=True)

    print(f" done\n")

    summary = build_summary(files_data)

    output = {
        "_meta": {
            "generated": datetime.now().isoformat(),
            "root": str(ROOT.resolve()),
            "total_files": len(files_data),
            "scanner_version": "1.0.0",
        },
        "summary": summary,
        "files": files_data,
    }

    out_path = ROOT / "blueprint_data.json"
    out_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # ── Print ringkasan ─────────────────────────────────────────────────────────
    print(f"  Hasil scan:")
    print(f"    Total file    : {len(files_data)}")
    print(f"    Modul         : {len(summary['modules'])}")

    print(f"\n  Per modul:")
    for mod, info in summary["modules"].items():
        print(f"    {mod:<20} {info['count']} file")

    print(f"\n  Issues ditemukan:")
    for issue_type, count in summary["issues_summary"].items():
        print(f"    {issue_type:<25} ×{count}")

    if not summary["issues_summary"]:
        print(f"    Tidak ada issue!")

    print(f"\n  Fitur terdeteksi:")
    for feat, count in summary["feature_stats"].items():
        bar = "█" * min(count, 20)
        print(f"    {feat.replace('has_', ''):<15} {bar} {count}")

    print(f"\n  ✓ Output: {out_path}")
    print(f"  → Upload blueprint_data.json ke Claude\n")


if __name__ == "__main__":
    main()