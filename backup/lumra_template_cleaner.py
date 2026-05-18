"""
lumra_template_cleaner.py — Lumra ERP · Template Cleanup Tool
==============================================================
Memisahkan template HTML yang AKTIF (dipanggil views) vs TIDAK AKTIF,
lalu memindahkan yang tidak aktif ke folder _archive/

Cara pakai:
    python lumra_template_cleaner.py              → preview
    python lumra_template_cleaner.py --apply      → eksekusi
    python lumra_template_cleaner.py --apply --yes → tanpa konfirmasi

Logika:
    1. Scan semua views.py → kumpulkan semua template path yang di-render
    2. Scan semua .html di templates/ → bandingkan
    3. Yang tidak ditemukan di views.py → arsip ke _archive/unused_templates/
"""

import os, re, sys, shutil, argparse
from pathlib import Path
from datetime import datetime

# ── Warna terminal ────────────────────────────────────────────────────
G   = '\033[92m'
Y   = '\033[93m'
R   = '\033[91m'
B   = '\033[94m'
C   = '\033[96m'
DIM = '\033[2m'
W   = '\033[97m'
RST = '\033[0m'

def OK(m):   print(f'  {G}✅  {m}{RST}')
def WARN(m): print(f'  {Y}⚠️   {m}{RST}')
def INFO(m): print(f'  {C}ℹ️   {m}{RST}')
def HEAD(m): print(f'\n{B}{"═"*12} {W}{m}{RST}{B} {"═"*12}{RST}')
def ERR(m):  print(f'  {R}❌  {m}{RST}')
def ROW(m):  print(f'  {DIM}{m}{RST}')


# ── Konfigurasi ───────────────────────────────────────────────────────

BASE_DIR      = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'lumra_config' / 'templates'
VIEWS_DIR     = BASE_DIR / 'lumra_config'
ARCHIVE_DIR   = BASE_DIR / '_archive' / 'unused_templates'

# Template yang SELALU dipertahankan meskipun tidak ada di render()
# (dipakai via {% extends %} atau {% include %})
ALWAYS_KEEP = {
    'base/base.html',
    'base/navbar.html',
    'base/sidebar.html',
    'base/sidebar_item.html',
    'base/sidebar_right.html',
    'base/footer.html',
    'base/alert.html',
    'base/alert_inner.html',
    'base/kpi_card.html',
    'base/kpi_card_inner.html',
    'base/kpi_card_white.html',
    'base/activity_drawer.html',
    'base/approval_modal.html',
    'base/error_404.html',
    'base/error_500.html',
    'reports/base_report.html',   # base template untuk semua report
}

# Regex untuk menangkap semua template yang di-render di views.py
RENDER_RE = re.compile(
    r"""(?:render\s*\(\s*\w+\s*,|TemplateResponse\s*\(\s*\w+\s*,|"""
    r"""get_template\s*\(|loader\.get_template\s*\()\s*['"]([^'"]+\.html)['"]""",
    re.VERBOSE,
)

# Regex untuk {% extends %} dan {% include %} di HTML
EXTENDS_RE = re.compile(r"""{%[-\s]*extends\s+['"]([^'"]+\.html)['"]""")
INCLUDE_RE = re.compile(r"""{%[-\s]*include\s+['"]([^'"]+\.html)['"]""")


# ── Scanner ───────────────────────────────────────────────────────────

def scan_views() -> set[str]:
    """Kumpulkan semua template path dari semua views.py"""
    used = set()
    views_files = list(VIEWS_DIR.rglob('views.py'))

    for vf in views_files:
        try:
            src = vf.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for m in RENDER_RE.finditer(src):
            used.add(m.group(1).strip())

    return used


def scan_html_references(templates: set[str]) -> set[str]:
    """
    Dari template yang sudah diketahui aktif,
    ikuti semua {% extends %} dan {% include %} secara rekursif.
    Ini memastikan partial/component tidak ikut diarsip.
    """
    referenced = set()
    to_check   = list(templates)
    checked    = set()

    while to_check:
        tmpl = to_check.pop()
        if tmpl in checked:
            continue
        checked.add(tmpl)

        fpath = TEMPLATES_DIR / tmpl
        if not fpath.exists():
            continue

        try:
            src = fpath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        for pattern in (EXTENDS_RE, INCLUDE_RE):
            for m in pattern.finditer(src):
                ref = m.group(1).strip()
                referenced.add(ref)
                if ref not in checked:
                    to_check.append(ref)

    return referenced


def scan_all_templates() -> set[str]:
    """Kumpulkan semua file .html di TEMPLATES_DIR (relatif ke TEMPLATES_DIR)"""
    all_files = set()
    if not TEMPLATES_DIR.exists():
        return all_files
    for f in TEMPLATES_DIR.rglob('*.html'):
        try:
            rel = f.relative_to(TEMPLATES_DIR)
            all_files.add(str(rel).replace('\\', '/'))
        except ValueError:
            pass
    return all_files


# ── Main Logic ────────────────────────────────────────────────────────

def analyze():
    """Analisis dan kembalikan dict berisi aktif/tidak aktif."""

    HEAD('Scanning views.py')
    used_in_views = scan_views()
    INFO(f'{len(used_in_views)} template terdeteksi di views.py')

    HEAD('Scanning extends & include dari template aktif')
    referenced = scan_html_references(used_in_views)
    INFO(f'{len(referenced)} template tambahan via extends/include')

    # Gabungkan semua yang aktif
    active = used_in_views | referenced | ALWAYS_KEEP
    INFO(f'{len(active)} total template aktif (views + includes + protected)')

    HEAD('Scanning semua file HTML di templates/')
    all_templates = scan_all_templates()
    INFO(f'{len(all_templates)} total file HTML ditemukan')

    # Pisahkan
    unused  = all_templates - active
    missing = active - all_templates  # dipanggil views tapi file tidak ada

    return {
        'active'   : sorted(active & all_templates),
        'unused'   : sorted(unused),
        'missing'  : sorted(missing),
        'all'      : sorted(all_templates),
    }


def preview(data: dict):
    HEAD('File AKTIF — tidak disentuh')
    for f in data['active']:
        print(f'  {G}✓{RST}  {f}')

    HEAD(f"File TIDAK AKTIF — akan diarsip ({len(data['unused'])} file)")
    for f in data['unused']:
        print(f'  {Y}→{RST}  {f}')

    if data['missing']:
        HEAD(f"File MISSING — dipanggil views tapi tidak ada ({len(data['missing'])} file)")
        WARN('File ini dipanggil di views.py tapi HTML-nya tidak ditemukan!')
        for f in data['missing']:
            print(f'  {R}!{RST}  {f}')

    print()
    print(f'  {"─"*50}')
    print(f'  {G}Aktif    : {len(data["active"])} file{RST}')
    print(f'  {Y}Diarsip  : {len(data["unused"])} file{RST}')
    if data['missing']:
        print(f'  {R}Missing  : {len(data["missing"])} file{RST}')
    print(f'  {"─"*50}')
    print(f'  Total    : {len(data["all"])} file')
    print()


def apply_archive(data: dict, yes: bool):
    if not data['unused']:
        OK('Tidak ada file yang perlu diarsip.')
        return

    if not yes:
        try:
            confirm = input(
                f'\n  Arsipkan {len(data["unused"])} file ke _archive/unused_templates/? (y/N): '
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\n  Dibatalkan.\n')
            return
        if confirm != 'y':
            print('  Dibatalkan.\n')
            return

    HEAD('Mengarsipkan file tidak aktif')

    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest_dir = ARCHIVE_DIR / ts
    moved    = 0
    failed   = 0

    for rel_str in data['unused']:
        src  = TEMPLATES_DIR / rel_str
        dest = dest_dir / rel_str

        if not src.exists():
            continue

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            ROW(f'→ _archive/unused_templates/{ts}/{rel_str}')
            moved += 1
        except Exception as e:
            ERR(f'Gagal: {rel_str} — {e}')
            failed += 1

    # Bersihkan folder kosong di templates/
    for dirpath in sorted(TEMPLATES_DIR.rglob('*'), reverse=True):
        if dirpath.is_dir():
            try:
                dirpath.rmdir()  # hanya berhasil jika kosong
            except OSError:
                pass

    print()
    OK(f'{moved} file berhasil diarsip ke _archive/unused_templates/{ts}/')
    if failed:
        ERR(f'{failed} file gagal dipindah — periksa permission.')

    INFO('Untuk rollback: pindahkan manual dari _archive/unused_templates/ kembali ke templates/')
    INFO('Jalankan: python lumra_sync.py  untuk verifikasi akhir')


# ── Entry Point ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Lumra ERP — Template Cleanup Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python lumra_template_cleaner.py              → preview saja
  python lumra_template_cleaner.py --apply      → arsipkan (+ konfirmasi)
  python lumra_template_cleaner.py --apply --yes → tanpa konfirmasi
        """
    )
    parser.add_argument('--apply', action='store_true', help='Eksekusi arsip')
    parser.add_argument('--yes',   action='store_true', help='Skip konfirmasi')
    args = parser.parse_args()

    print(f'\n{B}{"═"*50}')
    print(f'  {W}Lumra ERP — Template Cleanup Tool{RST}')
    print(f'{B}{"═"*50}{RST}')
    print(f'  Templates : {DIM}{TEMPLATES_DIR}{RST}')
    print(f'  Archive   : {DIM}{ARCHIVE_DIR}{RST}')
    print(f'  Mode      : {G if args.apply else Y}{"APPLY" if args.apply else "PREVIEW"}{RST}')

    if not TEMPLATES_DIR.exists():
        ERR(f'Folder templates tidak ditemukan: {TEMPLATES_DIR}')
        ERR('Pastikan script dijalankan dari root project Django.')
        sys.exit(1)

    data = analyze()
    preview(data)

    if args.apply:
        apply_archive(data, yes=args.yes)
    else:
        WARN('Ini PREVIEW — tidak ada perubahan dilakukan.')
        INFO(f'Jalankan dengan --apply untuk eksekusi.')
        print()


if __name__ == '__main__':
    main()