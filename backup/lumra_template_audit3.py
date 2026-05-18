#!/usr/bin/env python3
"""
lumra_template_audit.py
=======================
Dua fungsi utama:

  1. SCAN  — analisis semua template HTML:
             - Apakah urutan CSS benar (tailwind dulu, design_system sesudah)?
             - Extra <link> / <script> apa saja per folder?
             - Apakah folder perlu base template sendiri?

  2. FIX   — perbaiki urutan CSS di semua file yang bermasalah
             (design_system.css harus SETELAH {% tailwind_css %})

Cara pakai:
  python lumra_template_audit.py --scan
  python lumra_template_audit.py --scan --json report.json
  python lumra_template_audit.py --fix --dry-run
  python lumra_template_audit.py --fix
  python lumra_template_audit.py --scan --fix   (scan dulu, lalu fix)
"""

import re
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_ROOT   = Path(r"D:\APPS\Project\lumra\lumra_config\templates")
DEFAULT_BACKUP = Path(r"D:\APPS\Project\lumra\_template_audit_backup")

# Pattern yang dicari saat scan
PAT_TAILWIND_CSS  = re.compile(r'\{%[-\s]*tailwind_css[-\s]*%\}')
PAT_DESIGN_SYSTEM = re.compile(r'<link[^>]+lumra_design_system\.css[^>]*>')
PAT_EXTRA_LINK    = re.compile(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', re.IGNORECASE)
PAT_EXTRA_SCRIPT  = re.compile(r'<script[^>]+src=["\'][^"\']+["\'][^>]*>', re.IGNORECASE)
PAT_EXTENDS       = re.compile(r'\{%[-\s]*extends\s+["\']([^"\']+)["\'][-\s]*%\}')
PAT_BLOCK_CSS     = re.compile(r'\{%[-\s]*block\s+(?:extra_css|extra_head|chart_scripts)[-\s]*%\}(.*?)\{%[-\s]*endblock[-\s]*%\}', re.DOTALL)
PAT_INLINE_STYLE  = re.compile(r'<style[^>]*>', re.IGNORECASE)
PAT_LOAD_STATIC   = re.compile(r'\{%[-\s]*load\s+static[-\s]*%\}')

# Threshold: folder dianggap perlu base sendiri jika
# >= N file di folder itu punya extra CSS/JS yang SAMA
FOLDER_BASE_THRESHOLD = 2

# ── Terminal colors ───────────────────────────────────────────────────────────

C   = "\033[96m"
W   = "\033[97m"
G   = "\033[92m"
Y   = "\033[93m"
R   = "\033[91m"
DIM = "\033[2m"
B   = "\033[1m"
RST = "\033[0m"

def hr(char="─", n=68): return C + char * n + RST


# ── Helpers ───────────────────────────────────────────────────────────────────

def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def folder_label(path: Path, root: Path) -> str:
    """Nama folder relatif dari root, misal 'reports' atau 'base'."""
    try:
        parts = path.relative_to(root).parts
        return parts[0] if len(parts) > 1 else "(root)"
    except ValueError:
        return "(unknown)"


# ── SCAN ──────────────────────────────────────────────────────────────────────

def scan_file(path: Path, root: Path) -> dict:
    """
    Analisis satu file HTML. Return dict dengan:
      - rel_path, folder
      - extends: template yang di-extend (atau None)
      - has_tailwind_css: bool
      - has_design_system: bool
      - css_order_ok: bool (True jika tailwind sebelum design_system, atau salah satu tidak ada)
      - extra_links: list URL stylesheet eksternal
      - extra_scripts: list URL script eksternal
      - block_css_content: list isi {% block extra_css %} / {% block extra_head %}
      - inline_style_count: jumlah <style> block
      - issues: list string masalah yang ditemukan
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"rel_path": rel(path, root), "folder": folder_label(path, root),
                "issues": [f"Read error: {e}"], "error": True}

    result = {
        "rel_path"          : rel(path, root),
        "folder"            : folder_label(path, root),
        "extends"           : None,
        "has_tailwind_css"  : False,
        "has_design_system" : False,
        "css_order_ok"      : True,
        "extra_links"       : [],
        "extra_scripts"     : [],
        "block_css_content" : [],
        "inline_style_count": 0,
        "issues"            : [],
        "error"             : False,
    }

    # extends
    m = PAT_EXTENDS.search(content)
    if m:
        result["extends"] = m.group(1)

    # tailwind_css & design_system positions
    tw_match  = PAT_TAILWIND_CSS.search(content)
    ds_match  = PAT_DESIGN_SYSTEM.search(content)

    result["has_tailwind_css"]  = tw_match is not None
    result["has_design_system"] = ds_match is not None

    if tw_match and ds_match:
        if ds_match.start() < tw_match.start():
            result["css_order_ok"] = False
            result["issues"].append(
                "⚠  CSS order salah: lumra_design_system.css diload SEBELUM {% tailwind_css %}"
            )
    elif ds_match and not tw_match:
        result["issues"].append(
            "ℹ  lumra_design_system.css ada tapi tidak ada {% tailwind_css %} — "
            "pastikan ini bukan base template yang di-extend"
        )

    # Extra external stylesheets (selain design_system & tailwind CDN)
    for lm in PAT_EXTRA_LINK.finditer(content):
        tag = lm.group(0)
        if "lumra_design_system" not in tag and "tailwind" not in tag.lower():
            # Ekstrak href
            href = re.search(r'href=["\']([^"\']+)["\']', tag)
            if href:
                result["extra_links"].append(href.group(1))

    # Extra external scripts
    for sm in PAT_EXTRA_SCRIPT.finditer(content):
        tag = sm.group(0)
        src = re.search(r'src=["\']([^"\']+)["\']', tag)
        if src:
            result["extra_scripts"].append(src.group(1))

    # Block extra_css / extra_head content
    for bm in PAT_BLOCK_CSS.finditer(content):
        body = bm.group(1).strip()
        if body:
            result["block_css_content"].append(body[:200])

    # Inline style count
    result["inline_style_count"] = len(PAT_INLINE_STYLE.findall(content))

    return result


def analyze_folders(file_reports: list[dict]) -> dict:
    """
    Dari semua file report, tentukan folder mana yang perlu base template.

    Kriteria folder perlu base sendiri:
      1. >= FOLDER_BASE_THRESHOLD file di folder itu punya extra_links atau
         extra_scripts yang SAMA (shared dependency)
      2. ATAU ada block_css_content yang berulang di folder yang sama
      3. ATAU ada file yang extend bukan base/base.html (sudah punya base lain)
    """
    folders: dict[str, dict] = defaultdict(lambda: {
        "files": [],
        "all_extra_links": defaultdict(int),
        "all_extra_scripts": defaultdict(int),
        "all_block_css": [],
        "has_own_base": False,
        "extends_targets": defaultdict(int),
    })

    for r in file_reports:
        if r.get("error"):
            continue
        folder = r["folder"]
        fd = folders[folder]
        fd["files"].append(r["rel_path"])

        for link in r["extra_links"]:
            fd["all_extra_links"][link] += 1
        for script in r["extra_scripts"]:
            fd["all_extra_scripts"][script] += 1
        for bc in r["block_css_content"]:
            fd["all_block_css"].append(bc)
        if r["extends"]:
            fd["extends_targets"][r["extends"]] += 1

    recommendations: dict[str, dict] = {}

    for folder, fd in folders.items():
        shared_links   = {k: v for k, v in fd["all_extra_links"].items()
                         if v >= FOLDER_BASE_THRESHOLD}
        shared_scripts = {k: v for k, v in fd["all_extra_scripts"].items()
                         if v >= FOLDER_BASE_THRESHOLD}

        # Cek apakah folder sudah punya base (extend ke sesuatu selain base/base.html)
        own_base_targets = {t for t in fd["extends_targets"]
                           if "base/base" not in t and t != "base.html"}

        needs_base = bool(shared_links or shared_scripts or own_base_targets)
        reason     = []
        if shared_links:
            reason.append(f"shared CSS: {list(shared_links.keys())[:3]}")
        if shared_scripts:
            reason.append(f"shared JS: {list(shared_scripts.keys())[:3]}")
        if own_base_targets:
            reason.append(f"sudah extend ke: {list(own_base_targets)[:2]}")

        recommendations[folder] = {
            "file_count"    : len(fd["files"]),
            "needs_base"    : needs_base,
            "reason"        : reason,
            "shared_links"  : list(shared_links.keys()),
            "shared_scripts": list(shared_scripts.keys()),
            "extends_targets": dict(fd["extends_targets"]),
        }

    return recommendations


def print_scan_report(file_reports: list[dict], folder_recs: dict) -> None:
    print(f"\n{hr('═')}")
    print(f"  {B}LUMRA TEMPLATE AUDIT — HASIL SCAN{RST}")
    print(hr('═'))

    # ── Per-file issues ──
    issues_found = [r for r in file_reports if r.get("issues") and not r.get("error")]
    errors_found = [r for r in file_reports if r.get("error")]

    if issues_found:
        print(f"\n{hr()}")
        print(f"  {B}FILE DENGAN ISSUES  ({len(issues_found)} file){RST}\n")
        for r in issues_found:
            print(f"  {Y}{r['rel_path']}{RST}")
            for issue in r["issues"]:
                severity_color = R if "⚠" in issue else Y
                print(f"    {severity_color}{issue}{RST}")
    else:
        print(f"\n  {G}✅ Semua file — urutan CSS sudah benar{RST}")

    if errors_found:
        print(f"\n  {R}File yang gagal dibaca:{RST}")
        for r in errors_found:
            print(f"  {DIM}{r['rel_path']}: {r['issues'][0]}{RST}")

    # ── Folder analysis ──
    print(f"\n{hr()}")
    print(f"  {B}ANALISIS FOLDER — perlu base template sendiri?{RST}\n")

    needs_base   = {f: d for f, d in folder_recs.items() if d["needs_base"]}
    no_base_need = {f: d for f, d in folder_recs.items() if not d["needs_base"]}

    if needs_base:
        print(f"  {Y}▲  Folder yang DISARANKAN punya base template:{RST}\n")
        for folder, data in sorted(needs_base.items()):
            print(f"  {W}{folder:<20}{RST}  {DIM}{data['file_count']} file{RST}")
            for r in data["reason"]:
                print(f"    {DIM}→ {r}{RST}")
            if data["shared_links"]:
                for link in data["shared_links"][:3]:
                    short = link[-60:] if len(link) > 60 else link
                    print(f"    {DIM}  CSS: …{short}{RST}")
            if data["shared_scripts"]:
                for script in data["shared_scripts"][:3]:
                    short = script[-60:] if len(script) > 60 else script
                    print(f"    {DIM}  JS:  …{short}{RST}")
            print()
    else:
        print(f"  {G}✅ Tidak ada folder yang perlu base template tambahan{RST}\n")

    if no_base_need:
        folders_str = ", ".join(sorted(no_base_need.keys()))
        print(f"  {DIM}Tidak perlu base tambahan: {folders_str}{RST}")

    # ── Summary ──
    print(f"\n{hr()}")
    order_ok    = sum(1 for r in file_reports if r.get("css_order_ok", True) and not r.get("error"))
    order_bad   = sum(1 for r in file_reports if not r.get("css_order_ok", True))
    total       = len(file_reports)

    print(f"  {DIM}Total file   : {W}{total}{RST}")
    print(f"  {DIM}Urutan OK    : {G}{order_ok}{RST}")
    print(f"  {DIM}Perlu di-fix : {R if order_bad else G}{order_bad}{RST}")
    print(f"  {DIM}Error baca   : {len(errors_found)}{RST}")
    print(hr('═'))


# ── FIX ───────────────────────────────────────────────────────────────────────

def fix_css_order(content: str) -> tuple[str, bool]:
    """
    Pastikan {% tailwind_css %} selalu sebelum <link lumra_design_system.css>.

    Handle tiga pola:
      A. design_system ada SEBELUM tailwind_css → swap
      B. design_system ada tapi tailwind_css tidak ada → tidak disentuh
      C. tailwind_css ada tapi design_system tidak ada → tidak disentuh
      D. Keduanya tidak ada → tidak disentuh
    """
    tw_match = PAT_TAILWIND_CSS.search(content)
    ds_match = PAT_DESIGN_SYSTEM.search(content)

    if not (tw_match and ds_match):
        return content, False

    if ds_match.start() < tw_match.start():
        # Pola A: perlu swap
        # Ambil teks exact kedua tag
        tw_tag = tw_match.group(0)
        ds_tag = ds_match.group(0)

        # Hapus design_system dulu (posisi lebih awal)
        content = content[:ds_match.start()] + content[ds_match.end():]

        # Setelah hapus ds, posisi tw bergeser — cari ulang
        tw_match2 = PAT_TAILWIND_CSS.search(content)
        if not tw_match2:
            return content, False  # safety fallback

        # Sisipkan design_system tepat setelah tailwind_css (+ satu newline)
        insert_pos = tw_match2.end()
        content = content[:insert_pos] + "\n  " + ds_tag + content[insert_pos:]

        return content, True

    return content, False


def run_fix(root: Path, backup_dir: Path, dry_run: bool) -> None:
    html_files = list(root.rglob("*.html"))

    fixed   = 0
    skipped = 0
    errors  = 0

    print(f"\n{hr()}")
    print(f"  {B}FIX CSS ORDER  {'[DRY-RUN]' if dry_run else '[APPLY]'}{RST}\n")

    for path in sorted(html_files):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  {R}ERR  {rel(path, root)}: {e}{RST}")
            errors += 1
            continue

        new_content, changed = fix_css_order(content)

        if changed:
            if dry_run:
                print(f"  {Y}WOULD FIX  {rel(path, root)}{RST}")
            else:
                # Backup
                backup_dir.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"{path.stem}_{stamp}{path.suffix}"
                shutil.copy2(path, backup_path)

                path.write_text(new_content, encoding="utf-8")
                print(f"  {G}FIXED      {rel(path, root)}{RST}")
            fixed += 1
        else:
            skipped += 1

    print(f"\n  {B}Selesai:{RST}  "
          f"{G}{fixed} file di-fix{RST}  ·  "
          f"{DIM}{skipped} file tidak perlu fix{RST}  ·  "
          f"{R if errors else DIM}{errors} error{RST}")

    if dry_run and fixed:
        print(f"\n  {Y}Jalankan tanpa --dry-run untuk apply perubahan.{RST}")
    elif not dry_run and fixed:
        print(f"  {DIM}Backup tersimpan di: {backup_dir}{RST}")

    print(hr('═'))


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Lumra Template Audit — scan + fix CSS order",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--root",    type=Path, default=DEFAULT_ROOT)
    p.add_argument("--backup",  type=Path, default=DEFAULT_BACKUP)
    p.add_argument("--scan",    action="store_true", help="Analisis semua template")
    p.add_argument("--fix",     action="store_true", help="Fix CSS order")
    p.add_argument("--dry-run", action="store_true", help="Preview fix tanpa ubah file")
    p.add_argument("--json",    type=Path, default=None, help="Simpan JSON report")
    return p.parse_args()


def main():
    args = parse_args()

    # Default: jika tidak ada flag, scan saja
    if not args.scan and not args.fix:
        args.scan = True

    print(f"\n{hr('═')}")
    print(f"  {B}Lumra Template Audit{RST}")
    print(hr('═'))
    print(f"  Root  : {DIM}{args.root}{RST}")

    html_files = sorted(args.root.rglob("*.html"))
    print(f"  Files : {DIM}{len(html_files)} file HTML ditemukan{RST}\n")

    if not html_files:
        print(f"  {R}Tidak ada file HTML ditemukan. Cek --root path.{RST}\n")
        return

    # ── SCAN ──
    if args.scan:
        print(f"  Scanning...")
        file_reports  = [scan_file(f, args.root) for f in html_files]
        folder_recs   = analyze_folders(file_reports)
        print_scan_report(file_reports, folder_recs)

        if args.json:
            report = {
                "generated"   : datetime.now().isoformat(),
                "root"        : str(args.root),
                "total_files" : len(file_reports),
                "files"       : file_reports,
                "folder_analysis": folder_recs,
            }
            args.json.write_text(
                json.dumps(report, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            print(f"\n  {G}📄 JSON report: {args.json}{RST}")

    # ── FIX ──
    if args.fix:
        run_fix(args.root, args.backup, dry_run=args.dry_run)


if __name__ == "__main__":
    main()