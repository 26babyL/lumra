#!/usr/bin/env python3
"""
strip_duplicates.py — Lumra Template CSS Stripper
===================================================
Hapus definisi CSS duplikat dari template Django yang sudah
dipindahkan ke lumra_components.css.

Prinsip:
  - Template boleh punya CSS yang UNIK untuk halaman itu saja
  - Template TIDAK boleh mendefinisikan ulang class yang sudah ada
    di lumra_components.css (glass-card, kpi-card, .reveal, dll)
  - Ini bukan "hapus semua <style>" — ini "hapus yang sudah ada di komponen"

Cara pakai:
  python strip_duplicates.py --dry-run          # lihat apa yang akan dihapus
  python strip_duplicates.py --apply            # eksekusi
  python strip_duplicates.py --apply --only dashboard
  python strip_duplicates.py --report           # lihat duplikasi terbanyak

Output:
  - Setiap file yang diubah di-backup ke _strip_backup/
  - Log di strip_report.json
"""

import re
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Set


# ── Colors ─────────────────────────────────────────────────────────────────────
def _c(n): return f"\033[{n}m"
RST=_c(0); BOLD=_c(1); GRN=_c(32); YLW=_c(33); RED=_c(31); CYN=_c(36); DIM=_c(2); MAG=_c(35)
def ok(m):   print(f"  {GRN}✓{RST}  {m}")
def warn(m): print(f"  {YLW}!{RST}  {m}")
def info(m): print(f"  {CYN}→{RST}  {m}")
def skip(m): print(f"  {DIM}–{RST}  {m}")


# ── CSS classes yang sudah ada di lumra_components.css (SSOT) ─────────────────
# TAMBAH ke sini kalau ada class baru yang dipindahkan ke components.

MANAGED_CLASSES: Set[str] = {
    # Glass foundation
    "lumra-glass", "lumra-glass-strong", "lumra-glass-dark",
    "lumra-glass-highlight",

    # KPI card
    "kpi-card", "kpi-glass", "lumra-kpi",
    "kpi-label", "kpi-label-text", "kpi-val", "kpi-value",
    "kpi-sub", "kpi-subtitle", "kpi-icon",

    # Glass card
    "glass-card", "glass", "lumra-card",

    # Location card
    "loc-card",

    # Modal
    "modal-glass", "modal-in",

    # Toolbar
    "action-bar", "glass-toolbar",

    # Metric row
    "metric-row", "metric-name", "metric-val",

    # Section label
    "section-label",

    # Status badges & chips
    "delta", "status-badge", "status-chip",
    "badge-active", "badge-inactive",
    "status-pill",
    "chip-emerald", "chip-amber", "chip-rose",
    "chip-sky", "chip-info", "chip-new", "chip-transit",
    "chip-neutral",
    "lumra-badge", "lumra-badge-success", "lumra-badge-warning",
    "lumra-badge-danger", "lumra-badge-info", "lumra-badge-accent",
    "lumra-badge-neutral", "lumra-badge-primary",

    # Form
    "form-input", "loc-search", "form-label",
    "lumra-input", "f-input", "inp",
    "lumra-label", "f-label",

    # Buttons
    "btn-add", "btn-primary", "btn-apply",
    "icon-btn",
    "lumra-btn", "lumra-btn-primary", "lumra-btn-glass",
    "lumra-btn-outline", "lumra-btn-ghost", "lumra-btn-danger",
    "lumra-btn-sm", "lumra-btn-lg",

    # Pagination
    "page-btn",

    # Toast
    "toast",

    # Scroll reveal
    "reveal",

    # Nav/tab
    "nav-tab", "tab-container",

    # View toggle
    "view-toggle", "view-btn",

    # Progress
    "progress-track", "progress-fill",

    # Blob background
    "bg-blob", "bg-blob-1", "bg-blob-2", "bg-blob-3",
    "blob", "blob-a", "blob-b", "blob-c",
    "orb", "orb-1", "orb-2", "orb-3",

    # Table
    "lumra-table",

    # Alert
    "lumra-alert",

    # Animation utilities
    "animate-fade-up", "animate-fade-in", "animate-scale-in",
    "animate-spin", "animate-pulse", "lumra-skeleton", "stagger",
}


# ── CSS block extractor ─────────────────────────────────────────────────────────

def extract_style_blocks(html: str) -> list:
    """
    Extract semua <style>...</style> blocks dari HTML.
    Returns list of (start_pos, end_pos, content).
    """
    blocks = []
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE):
        blocks.append({
            "start": m.start(),
            "end":   m.end(),
            "open":  m.group(0)[:m.group(0).index(m.group(1))],
            "css":   m.group(1),
            "close": "</style>",
        })
    return blocks


def parse_css_rules(css: str) -> list:
    """
    Parse CSS rules dari string. Returns list of (selector, body, full_text).
    Handles nested braces untuk @media, @keyframes, dll.
    """
    rules = []
    i = 0
    text = css.strip()
    n = len(text)

    while i < n:
        # Skip whitespace dan komentar
        while i < n and text[i] in " \t\n\r": i += 1
        if i >= n: break

        # Skip komentar /* ... */
        if text[i:i+2] == "/*":
            end = text.find("*/", i+2)
            if end == -1: break
            i = end + 2
            continue

        # Cari selector dan body
        brace_start = text.find("{", i)
        if brace_start == -1: break

        selector_raw = text[i:brace_start].strip()
        if not selector_raw:
            i = brace_start + 1
            continue

        # Hitung depth untuk nested braces
        depth = 1
        j = brace_start + 1
        while j < n and depth > 0:
            if text[j] == "{":   depth += 1
            elif text[j] == "}": depth -= 1
            j += 1

        body = text[brace_start+1:j-1].strip()
        full_text = text[i:j].strip()

        rules.append({
            "selector": selector_raw,
            "body":     body,
            "full":     full_text,
            "start":    i,
            "end":      j,
        })
        i = j

    return rules


def get_class_names_from_selector(selector: str) -> Set[str]:
    """Extract class names dari selector CSS."""
    classes = set()
    # Match .classname (dengan berbagai prefix: :hover, ::before, dll)
    for m in re.finditer(r"\.([a-zA-Z][a-zA-Z0-9_-]*)", selector):
        classes.add(m.group(1))
    return classes


def is_duplicate_rule(rule: dict) -> bool:
    """
    Returns True jika rule mendefinisikan ulang class yang sudah di components.
    """
    selector = rule["selector"]

    # Selalu pertahankan @keyframes, @media, @import
    if re.match(r"@(?:keyframes|media|import|font-face|supports)", selector.strip()):
        return False

    classes_in_rule = get_class_names_from_selector(selector)

    # Jika semua class dalam selector ada di MANAGED_CLASSES, ini duplikat
    if not classes_in_rule:
        return False  # selector non-class (element selector, :root, dll) — pertahankan

    # Jika ADA class yang managed, tandai sebagai duplikat
    # (konservatif: hanya hapus jika primary class adalah managed)
    primary_classes = {c for c in classes_in_rule if c in MANAGED_CLASSES}
    return len(primary_classes) > 0


@dataclass
class StripResult:
    file: Path
    original_size: int
    new_size: int
    removed_rules: List[str] = field(default_factory=list)
    kept_rules: List[str] = field(default_factory=list)
    empty_blocks_removed: int = 0

    @property
    def changed(self) -> bool:
        return bool(self.removed_rules) or self.empty_blocks_removed > 0

    @property
    def savings_bytes(self) -> int:
        return self.original_size - self.new_size

    @property
    def savings_pct(self) -> float:
        if self.original_size == 0: return 0
        return self.savings_bytes / self.original_size * 100


def strip_file(fp: Path, dry_run: bool = True,
               backup_dir: Path = None) -> StripResult:
    """
    Hapus CSS rule yang sudah ada di components dari file HTML.
    """
    html = fp.read_text(encoding="utf-8", errors="replace")
    result = StripResult(file=fp, original_size=len(html), new_size=len(html))

    style_blocks = extract_style_blocks(html)
    if not style_blocks:
        return result

    new_html = html
    offset = 0  # track posisi setelah penggantian

    for block in style_blocks:
        css = block["css"]
        rules = parse_css_rules(css)

        removed = []
        kept_css_parts = []

        # Pertahankan komentar di awal block
        leading_comment = re.match(r"^\s*(/\*.*?\*/\s*)", css, re.DOTALL)
        if leading_comment:
            kept_css_parts.append(leading_comment.group(1))

        for rule in rules:
            if is_duplicate_rule(rule):
                classes = get_class_names_from_selector(rule["selector"])
                managed = classes & MANAGED_CLASSES
                removed.append(f".{', .'.join(sorted(managed))} (selector: {rule['selector'][:60]})")
            else:
                kept_css_parts.append(rule["full"])

        result.removed_rules.extend(removed)

        if not removed:
            continue  # tidak ada yang dihapus dari block ini

        # Rebuild CSS dari rules yang tersisa
        new_css = "\n\n  ".join(kept_css_parts)

        # Jika block jadi kosong (atau hanya whitespace), hapus seluruh <style> block
        if not new_css.strip():
            new_block = ""
            result.empty_blocks_removed += 1
        else:
            new_block = f"{block['open']}\n  {new_css}\n{block['close']}"

        if not dry_run:
            start = block["start"] + offset
            end = block["end"] + offset
            new_html = new_html[:start] + new_block + new_html[end:]
            offset += len(new_block) - (block["end"] - block["start"])

    if not dry_run and result.removed_rules:
        if backup_dir:
            backup_dir.mkdir(parents=True, exist_ok=True)
            dst = backup_dir / fp.name
            if dst.exists():
                dst = backup_dir / (
                    fp.stem + f"_{datetime.now().strftime('%H%M%S')}" + fp.suffix
                )
            shutil.copy2(fp, dst)
        fp.write_text(new_html, encoding="utf-8")

    result.new_size = len(new_html)
    return result


# ── Report ──────────────────────────────────────────────────────────────────────

def print_duplication_report(files: List[Path], templates_dir: Path):
    """Tampilkan report berapa banyak duplikasi per class."""
    class_count: Dict[str, int] = defaultdict(int)
    class_files: Dict[str, List[str]] = defaultdict(list)

    for fp in files:
        html = fp.read_text(encoding="utf-8", errors="replace")
        blocks = extract_style_blocks(html)
        for block in blocks:
            rules = parse_css_rules(block["css"])
            for rule in rules:
                classes = get_class_names_from_selector(rule["selector"])
                managed = classes & MANAGED_CLASSES
                for cls in managed:
                    class_count[cls] += 1
                    rel = str(fp.relative_to(templates_dir))
                    if rel not in class_files[cls]:
                        class_files[cls].append(rel)

    if not class_count:
        ok("Tidak ada duplikasi terdeteksi."); return

    print(f"\n  Class yang paling banyak didefinisikan ulang:")
    print(f"  {'Class':<30} {'Count':>5}  Files")
    print(f"  {'─'*30} {'─'*5}  {'─'*30}")

    for cls, count in sorted(class_count.items(), key=lambda x: -x[1]):
        if count < 2: continue
        files_str = ", ".join(class_files[cls][:3])
        if len(class_files[cls]) > 3: files_str += " ..."
        print(f"  {GRN}.{cls:<29}{RST} {count:>5}  {DIM}{files_str}{RST}")

    total_dups = sum(c for c in class_count.values() if c >= 2)
    print(f"\n  Total definisi duplikat: {YLW}{total_dups}{RST}")


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Lumra Template CSS Stripper")
    ap.add_argument("--templates", "-t", default=".",
                    help="Root direktori template Django")
    ap.add_argument("--apply", action="store_true",
                    help="Eksekusi (default: dry-run)")
    ap.add_argument("--only", metavar="FOLDER",
                    help="Filter: hanya proses file dalam folder ini")
    ap.add_argument("--file", metavar="NAME",
                    help="Proses satu file saja")
    ap.add_argument("--report", action="store_true",
                    help="Hanya tampilkan report duplikasi, tidak strip")
    ap.add_argument("--no-backup", action="store_true")
    ap.add_argument("--json-out", metavar="FILE",
                    help="Simpan hasil ke JSON")
    args = ap.parse_args()

    mode = f"{GRN}APPLY{RST}" if args.apply else f"{YLW}DRY-RUN{RST}"
    templates_dir = Path(args.templates)

    print(f"\n{BOLD}Lumra Template CSS Stripper{RST}")
    print(f"  Mode      : {mode}")
    print(f"  Templates : {templates_dir}")
    print(f"  Classes managed: {len(MANAGED_CLASSES)}")

    # Cari file HTML
    files = []
    for fp in sorted(templates_dir.rglob("*.html")):
        if any(x in str(fp) for x in ["_archive", "_strip_backup", "__pycache__"]):
            continue
        if args.file and fp.name != args.file:
            continue
        if args.only and args.only not in str(fp):
            continue
        files.append(fp)

    if not files:
        warn("Tidak ada file ditemukan."); return

    info(f"Ditemukan {len(files)} file HTML")

    if args.report:
        print_duplication_report(files, templates_dir); return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = None if args.no_backup else (
        templates_dir / f"_strip_backup_{ts}"
    ) if args.apply else None

    print(f"\n{'─'*60}")

    results = []
    total_removed = 0
    total_savings = 0

    for fp in files:
        result = strip_file(
            fp,
            dry_run=not args.apply,
            backup_dir=backup_dir
        )
        results.append(result)

        if not result.changed:
            continue

        rel = str(fp.relative_to(templates_dir))
        verb = "stripped" if args.apply else "would strip"
        n = len(result.removed_rules)
        savings = f"-{result.savings_bytes:,}B" if args.apply else f"~-{n*80}B"
        print(f"  {verb:<10} {rel:<45} {n} rules  {DIM}{savings}{RST}")

        for r in result.removed_rules[:5]:
            print(f"             {DIM}• {r[:70]}{RST}")
        if len(result.removed_rules) > 5:
            print(f"             {DIM}• +{len(result.removed_rules)-5} more...{RST}")

        total_removed += n
        total_savings += result.savings_bytes if args.apply else n * 80

    # Summary
    changed = [r for r in results if r.changed]
    print(f"\n{'─'*60}")
    print(f"  File {'diubah' if args.apply else 'akan diubah'}    : {BOLD}{len(changed)}{RST} dari {len(files)}")
    print(f"  Rules dihapus : {BOLD}{total_removed}{RST}")
    print(f"  Savings (~)   : {total_savings:,} bytes")

    if backup_dir and args.apply:
        ok(f"Backup: {backup_dir.name}/")

    if args.json_out:
        out = [{
            "file": str(r.file.name),
            "removed": r.removed_rules,
            "kept": len(r.kept_rules),
            "savings_bytes": r.savings_bytes,
        } for r in results if r.changed]
        Path(args.json_out).write_text(json.dumps(out, indent=2), encoding="utf-8")
        ok(f"Report: {args.json_out}")

    if not args.apply and total_removed > 0:
        print(f"\n  Jalankan dengan --apply:")
        cmd = "python strip_duplicates.py --apply"
        if args.only: cmd += f" --only {args.only}"
        if args.file: cmd += f" --file {args.file}"
        print(f"    {GRN}{cmd}{RST}")


if __name__ == "__main__":
    main()