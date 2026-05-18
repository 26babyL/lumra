#!/usr/bin/env python3
"""
validate.py — Lumra Design System CI Validator v2
===================================================
Fix dari v1:
  - Exclude semua folder backup dari scan (prefix _ atau .)
  - Tambah --fix-fonts untuk auto-hapus @import Syne dari template aktif
  - Summary lebih ringkas, group by rule

Cara pakai:
  python validate.py                     # cek template aktif saja
  python validate.py --fix-fonts --dry-run  # preview hapus @import Syne
  python validate.py --fix-fonts         # hapus @import Syne (ada backup otomatis)
  python validate.py --ci                # exit 1 jika ada error
  python validate.py --include-backups   # scan backup juga (debug only)
"""

import json, re, sys, hashlib, shutil, argparse
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


# ── Colors ─────────────────────────────────────────────────────────────────────
def _c(n): return f"\033[{n}m"
RST=_c(0); BOLD=_c(1); GRN=_c(32); YLW=_c(33); RED=_c(31); CYN=_c(36); DIM=_c(2)
def ok(m):   print(f"  {GRN}✓{RST}  {m}")
def warn(m): print(f"  {YLW}⚠{RST}  {m}")
def fail(m): print(f"  {RED}✗{RST}  {m}")
def info(m): print(f"  {CYN}→{RST}  {m}")


# ── Backup folder detection ─────────────────────────────────────────────────────
# Semua folder dengan prefix _ atau . dianggap backup, tidak perlu di-validasi.

BACKUP_FOLDER_PATTERNS = [
    r"^_",          # folder mulai _ (misalnya _strip_backup, _archive, _full_migrator_backup)
    r"^\.",         # folder mulai . (misalnya .lumra_recolor_backup)
]

def is_backup_path(rel_path: Path) -> bool:
    """Return True jika salah satu segment path adalah folder backup."""
    for part in rel_path.parts:
        for pattern in BACKUP_FOLDER_PATTERNS:
            if re.match(pattern, part):
                return True
    return False


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class Violation:
    file: str
    line: int
    rule: str
    message: str
    severity: str = "error"
    fix_hint: str = ""


@dataclass
class Report:
    violations: List[Violation] = field(default_factory=list)
    checks_run: int = 0
    files_checked: int = 0

    @property
    def errors(self):   return [v for v in self.violations if v.severity == "error"]
    @property
    def warnings(self): return [v for v in self.violations if v.severity == "warning"]
    def add(self, v):   self.violations.append(v)
    def passed(self):   return len(self.errors) == 0


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def config_hash(cfg: dict) -> str:
    return hashlib.md5(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]

def find_html_files(root: Path, include_backups: bool = False) -> List[Path]:
    files = []
    for fp in sorted(root.rglob("*.html")):
        try:
            rel = fp.relative_to(root)
        except ValueError:
            continue
        if not include_backups and is_backup_path(rel):
            continue
        files.append(fp)
    return files


# ── Checks ─────────────────────────────────────────────────────────────────────

def check_css_hash(css_file: Path, cfg: dict, report: Report):
    if not css_file.exists():
        report.add(Violation(
            file=str(css_file), line=0, rule="css-file-missing",
            message=f"CSS tidak ditemukan: {css_file}",
            severity="error", fix_hint="Jalankan: python generate_css.py"
        ))
        return
    text = css_file.read_text(encoding="utf-8")
    m = re.search(r"/\* config-hash: ([a-f0-9]+) \*/", text)
    if not m:
        report.add(Violation(
            file=str(css_file), line=1, rule="css-hash-missing",
            message="CSS tidak punya config-hash — mungkin diedit manual",
            severity="warning", fix_hint="Jalankan: python generate_css.py"
        ))
        return
    expected = config_hash(cfg)
    if m.group(1) != expected:
        report.add(Violation(
            file=str(css_file), line=1, rule="css-hash-mismatch",
            message=f"Config diubah tapi CSS belum di-regenerate (hash: {m.group(1)} ≠ {expected})",
            severity="error", fix_hint="Jalankan: python generate_css.py"
        ))
    report.checks_run += 1


def check_template_fonts(files: List[Path], templates_dir: Path,
                          cfg: dict, report: Report):
    forbidden = cfg.get("validator_rules", {}).get("forbidden_font_imports", [])
    if not forbidden:
        return
    for fp in files:
        text = fp.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            for f_import in forbidden:
                if f_import in line and "@import" in line:
                    report.add(Violation(
                        file=str(fp.relative_to(templates_dir)),
                        line=i, rule="forbidden-font-import",
                        message=f"@import tidak diizinkan: '{f_import}'",
                        severity="error",
                        fix_hint="Jalankan: python validate.py --fix-fonts"
                    ))
        report.files_checked += 1
    report.checks_run += 1


def check_hardcodes(files: List[Path], templates_dir: Path,
                    cfg: dict, report: Report):
    forbidden = cfg.get("validator_rules", {}).get("forbidden_hardcodes", [])
    if not forbidden:
        return
    for fp in files:
        text = fp.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if re.match(r"\s*--", line): continue
            if "/*" in line or "<!--" in line: continue
            for val in forbidden:
                if val in line:
                    report.add(Violation(
                        file=str(fp.relative_to(templates_dir)),
                        line=i, rule="template-hardcode",
                        message=f"Hardcoded '{val}' dalam template",
                        severity="warning",
                        fix_hint="Pindahkan ke CSS class dengan var(--token)"
                    ))
    report.checks_run += 1


# ── Fix: hapus font imports ────────────────────────────────────────────────────

def fix_font_imports(files: List[Path], templates_dir: Path,
                     cfg: dict, dry_run: bool = True) -> int:
    forbidden = cfg.get("validator_rules", {}).get("forbidden_font_imports", [])
    if not forbidden:
        return 0

    changed = 0
    ts = datetime.now().strftime("%H%M%S")

    for fp in files:
        text = fp.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines(keepends=True)
        new_lines, removed = [], []

        for i, line in enumerate(lines, 1):
            remove = any(fi in line and "@import" in line for fi in forbidden)
            if remove:
                removed.append((i, line.rstrip()))
            else:
                new_lines.append(line)

        if not removed:
            continue

        rel = str(fp.relative_to(templates_dir))
        sym = "~" if dry_run else "✓"
        clr = YLW if dry_run else GRN
        print(f"  {clr}{sym}{RST}  {rel}")
        for ln, lt in removed:
            print(f"       {DIM}line {ln}: {lt[:80]}{RST}")

        if not dry_run:
            shutil.copy2(fp, fp.parent / f"_{fp.stem}_{ts}_font_bak{fp.suffix}")
            fp.write_text("".join(new_lines), encoding="utf-8")

        changed += 1

    return changed


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Lumra Validator v2")
    ap.add_argument("--config", "-c", default="lumra.config.json")
    ap.add_argument("--css-dir", default="static/css")
    ap.add_argument("--templates", "-t", default=".")
    ap.add_argument("--fix-fonts", action="store_true",
                    help="Hapus @import font yang tidak diizinkan dari template aktif")
    ap.add_argument("--dry-run", action="store_true",
                    help="Preview saja, tidak ubah file (pakai bersama --fix-fonts)")
    ap.add_argument("--include-backups", action="store_true",
                    help="Scan folder backup juga (default: skip)")
    ap.add_argument("--no-hardcode-check", action="store_true",
                    help="Skip cek hardcoded values (kurangi warning noise)")
    ap.add_argument("--ci", action="store_true",
                    help="Exit 1 jika ada error (untuk pre-commit hook)")
    ap.add_argument("--strict", action="store_true",
                    help="Treat warnings sebagai errors")
    args = ap.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        fail(f"Config tidak ditemukan: {config_path}"); sys.exit(1)

    cfg = load_config(config_path)
    templates_dir = Path(args.templates)

    print(f"\n{BOLD}Lumra Validator v2{RST}  (config v{cfg['_meta']['version']})")
    if not args.include_backups:
        print(f"  {DIM}Folder backup (prefix _ atau .) di-skip otomatis.{RST}")
    print("─" * 60)

    # ── Fix mode ───────────────────────────────────────────────
    if args.fix_fonts:
        mode = f"{YLW}DRY-RUN{RST}" if args.dry_run else f"{GRN}APPLY{RST}"
        info(f"Fix font imports  [{mode}]")
        files = find_html_files(templates_dir, include_backups=False)
        n = fix_font_imports(files, templates_dir, cfg, dry_run=args.dry_run)
        print()
        if n == 0:
            ok("Tidak ada @import font yang perlu dihapus.")
        elif args.dry_run:
            warn(f"{n} file akan diubah. Jalankan tanpa --dry-run:")
            print(f"    {GRN}python validate.py --fix-fonts{RST}")
        else:
            ok(f"{n} file diupdate. Backup ada di folder yang sama (prefix _).")
        print()
        return

    # ── Validate mode ──────────────────────────────────────────
    all_count = len(list(templates_dir.rglob("*.html")))
    files = find_html_files(templates_dir, include_backups=args.include_backups)
    skipped = all_count - len(files)
    info(f"Scanning {len(files)} template aktif  {DIM}({skipped} backup di-skip){RST}")

    report = Report()

    info("CSS hash check...")
    check_css_hash(Path(args.css_dir) / "lumra_design_system.css", cfg, report)

    info("Font import check...")
    check_template_fonts(files, templates_dir, cfg, report)

    if not args.no_hardcode_check:
        info("Hardcode check...")
        check_hardcodes(files, templates_dir, cfg, report)

    # ── Summary ────────────────────────────────────────────────
    errors  = report.errors
    warnings = report.warnings
    err_by_rule  = defaultdict(list)
    warn_by_rule = defaultdict(list)
    for v in errors:   err_by_rule[v.rule].append(v)
    for v in warnings: warn_by_rule[v.rule].append(v)

    print(f"\n{'─'*60}")

    if errors:
        print(f"\n  {RED}{BOLD}ERRORS  ({len(errors)}){RST}")
        for rule, vs in err_by_rule.items():
            n_files = len({v.file for v in vs})
            print(f"\n  {RED}✗{RST}  [{rule}]  {n_files} file")
            for v in vs[:3]:
                print(f"       {DIM}{v.file}:{v.line}{RST}  {v.message}")
            if len(vs) > 3:
                print(f"       {DIM}... +{len(vs)-3} lainnya{RST}")
            if vs[0].fix_hint:
                print(f"       {DIM}→ {vs[0].fix_hint}{RST}")

    if warnings and not args.no_hardcode_check:
        print(f"\n  {YLW}WARNINGS  ({len(warnings)}){RST}"
              f"  {DIM}(--no-hardcode-check untuk hide){RST}")
        for rule, vs in warn_by_rule.items():
            print(f"  {YLW}⚠{RST}  [{rule}]  ×{len(vs)}")

    print()
    if not errors and not warnings:
        ok(f"Semua {len(files)} template aktif passed ✓")
    elif not errors:
        ok(f"Passed  ({len(files)} template, {len(warnings)} warnings)")
    else:
        fail(f"{len(errors)} error di template aktif")

    # Hint spesifik untuk font import
    font_vs = err_by_rule.get("forbidden-font-import", [])
    if font_vs:
        n = len({v.file for v in font_vs})
        print(f"\n  {YLW}Fix {n} file dengan @import Syne:{RST}")
        print(f"    {GRN}python validate.py --fix-fonts --dry-run{RST}   ← preview")
        print(f"    {GRN}python validate.py --fix-fonts{RST}             ← eksekusi")

    print()

    if args.ci:
        sys.exit(1 if (errors or (args.strict and warnings)) else 0)


if __name__ == "__main__":
    main()