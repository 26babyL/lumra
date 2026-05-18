#!/usr/bin/env python
# =============================================================
# tools/run_tests_report.py
#
# Jalankan integration test + coverage, lalu generate laporan .md
#
# Cara pakai:
#   python tools/run_tests_report.py
#
# Output:
#   reports/test_report_YYYY-MM-DD_HH-MM.md
# =============================================================

import os
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path

# =============================================================
# CONFIG
# =============================================================
BASE_DIR      = Path(__file__).resolve().parent.parent
REPORTS_DIR   = BASE_DIR / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)

TIMESTAMP     = datetime.now().strftime('%Y-%m-%d_%H-%M')
REPORT_FILE   = REPORTS_DIR / f'test_report_{TIMESTAMP}.md'
COVERAGE_DIR  = BASE_DIR / 'htmlcov'
TEST_MODULE   = 'lumra_config.tests.test_integration'


# =============================================================
# HELPERS
# =============================================================
def run_command(cmd, cwd=BASE_DIR):
    """Jalankan command dan return (stdout, stderr, returncode)."""
    result = subprocess.run(
        cmd, cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout, result.stderr, result.returncode


def parse_test_results(output):
    """
    Parse output dari `python manage.py test --verbosity=2`
    Return dict berisi list passed, failed, error, skipped.
    """
    passed  = []
    failed  = []
    errors  = []
    skipped = []

    # Regex untuk baris hasil test
    # Contoh: "test_login_valid ... ok"
    # Contoh: "test_login_wrong ... FAIL"
    # Contoh: "test_api_leak ... ERROR"
    # Contoh: "test_something ... skipped 'alasan'"
    pattern = re.compile(
        r'^(test\S+)\s+\((\S+)\)\s+\.\.\.\s+(ok|FAIL|ERROR|skipped.*?)$',
        re.MULTILINE
    )

    for match in pattern.finditer(output):
        test_name  = match.group(1)
        test_class = match.group(2).split('.')[-1]
        status     = match.group(3)
        label      = f"`{test_class}.{test_name}`"

        if status == 'ok':
            passed.append(label)
        elif status == 'FAIL':
            failed.append(label)
        elif status == 'ERROR':
            errors.append(label)
        elif status.startswith('skipped'):
            reason = status.replace('skipped', '').strip().strip("'\"")
            skipped.append(f"{label} — *{reason}*")

    return passed, failed, errors, skipped


def parse_failure_details(output):
    """
    Ekstrak detail FAIL dan ERROR dari output test.
    Return list of dict {title, detail}
    """
    details = []
    # Blok error dimulai dengan "=====" dan diakhiri "-----"
    blocks = re.split(r'={70}', output)
    for block in blocks:
        block = block.strip()
        if block.startswith(('FAIL:', 'ERROR:')):
            lines = block.splitlines()
            title  = lines[0] if lines else 'Unknown'
            detail = '\n'.join(lines[1:]).strip()
            details.append({'title': title, 'detail': detail})
    return details


def parse_coverage(output):
    """
    Parse output dari `coverage report`
    Return list of dict {file, stmts, miss, cover}
    """
    rows = []
    in_table = False
    for line in output.splitlines():
        if line.startswith('---'):
            in_table = True
            continue
        if in_table and line.startswith('TOTAL'):
            parts = line.split()
            rows.append({
                'file': '**TOTAL**',
                'stmts': parts[1],
                'miss': parts[2],
                'cover': parts[-1]
            })
            break
        if in_table:
            parts = line.split()
            if len(parts) >= 4:
                rows.append({
                    'file': parts[0],
                    'stmts': parts[1],
                    'miss': parts[2],
                    'cover': parts[-1]
                })
    return rows


def coverage_badge(percent_str):
    """Return emoji badge berdasarkan coverage %."""
    try:
        pct = int(percent_str.replace('%', ''))
        if pct >= 80: return '🟢'
        if pct >= 60: return '🟡'
        return '🔴'
    except:
        return '⚪'


def error_explanation(error_text):
    """
    Baca traceback error dan return penjelasan + saran fix dalam bahasa manusia.
    """
    explanations = {
        'NoReverseMatch': (
            "URL tidak ditemukan di `urls.py`.",
            "Pastikan `name='...'` di `urls.py` sesuai dengan yang dipanggil di test. "
            "Atau gunakan `safe_url()` dengan `fallback`."
        ),
        'TemplateDoesNotExist': (
            "File template tidak ditemukan.",
            "Cek nama dan lokasi file `.html` di folder `templates/`. "
            "Pastikan nama di `assertTemplateUsed` cocok dengan path aktual."
        ),
        'OperationalError': (
            "Koneksi atau struktur database bermasalah.",
            "Cek apakah migration sudah dijalankan. "
            "Jalankan `python manage.py migrate` lalu coba lagi."
        ),
        'ProgrammingError': (
            "Tabel atau kolom tidak ditemukan di database test.",
            "Tambahkan `CREATE TABLE IF NOT EXISTS` di `setUpTestData`, "
            "atau aktifkan `managed=True` di Meta model yang bersangkutan."
        ),
        'AssertionError': (
            "Hasil test tidak sesuai ekspektasi.",
            "Baca pesan assertion di atas untuk tahu nilai yang diharapkan vs aktual. "
            "Sesuaikan logika view atau test-nya."
        ),
        'ImproperlyConfigured': (
            "Konfigurasi Django bermasalah.",
            "Cek `settings.py` — bisa dari MIDDLEWARE, INSTALLED_APPS, atau DATABASE yang salah."
        ),
        'ModuleNotFoundError': (
            "Module Python tidak ditemukan.",
            "Jalankan `pip install <nama-package>` atau cek apakah path import sudah benar."
        ),
        'IntegrityError': (
            "Pelanggaran constraint database (duplicate key, null, dll).",
            "Cek data yang diinsert di `setUpTestData` — kemungkinan ada duplikat "
            "atau field wajib yang kosong."
        ),
    }
    for key, (cause, fix) in explanations.items():
        if key in error_text:
            return cause, fix
    return (
        "Error tidak dikenali secara otomatis.",
        "Baca traceback di atas secara lengkap untuk identifikasi penyebab."
    )


# =============================================================
# MAIN — Jalankan test & generate report
# =============================================================
def main():
    print("🚀 Lumra Test Runner — Generating Report...")
    print(f"   Target : {TEST_MODULE}")
    print(f"   Output : {REPORT_FILE}\n")

    # ----------------------------------------------------------
    # STEP 1: Jalankan test dengan verbosity=2
    # ----------------------------------------------------------
    print("⏳ Running tests...")
    test_stdout, test_stderr, test_rc = run_command([
        sys.executable, 'manage.py', 'test', TEST_MODULE,
        '--verbosity=2', '--no-input'
    ])
    test_output = test_stdout + test_stderr
    test_passed = (test_rc == 0)

    # ----------------------------------------------------------
    # STEP 2: Jalankan coverage
    # ----------------------------------------------------------
    print("⏳ Running coverage...")
    run_command([sys.executable, '-m', 'coverage', 'run',
                 'manage.py', 'test', TEST_MODULE, '--no-input'])

    cov_stdout, _, _ = run_command(
        [sys.executable, '-m', 'coverage', 'report', '--skip-covered']
    )
    run_command([sys.executable, '-m', 'coverage', 'html'])

    # ----------------------------------------------------------
    # STEP 3: Parse hasil
    # ----------------------------------------------------------
    passed, failed, errors, skipped = parse_test_results(test_output)
    failure_details = parse_failure_details(test_output)
    coverage_rows   = parse_coverage(cov_stdout)

    total_tests = len(passed) + len(failed) + len(errors) + len(skipped)
    status_icon = "✅ PASSED" if test_passed else "❌ FAILED"

    # ----------------------------------------------------------
    # STEP 4: Tulis file .md
    # ----------------------------------------------------------
    lines = []
    a = lines.append  # shorthand

    a(f"# 🧪 Lumra Integration Test Report")
    a(f"")
    a(f"> Generated: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  ")
    a(f"> Module: `{TEST_MODULE}`  ")
    a(f"> Status: **{status_icon}**")
    a(f"")

    # --- Summary table ---
    a(f"## 📊 Summary")
    a(f"")
    a(f"| Kategori | Jumlah |")
    a(f"|---|---|")
    a(f"| ✅ Passed  | **{len(passed)}** |")
    a(f"| ❌ Failed  | **{len(failed)}** |")
    a(f"| 💥 Error   | **{len(errors)}** |")
    a(f"| ⏭️ Skipped | **{len(skipped)}** |")
    a(f"| **Total**  | **{total_tests}** |")
    a(f"")

    # --- Passed ---
    if passed:
        a(f"## ✅ Passed ({len(passed)})")
        a(f"")
        for t in passed:
            a(f"- {t}")
        a(f"")

    # --- Skipped ---
    if skipped:
        a(f"## ⏭️ Skipped ({len(skipped)})")
        a(f"")
        for t in skipped:
            a(f"- {t}")
        a(f"")

    # --- Failed ---
    if failed:
        a(f"## ❌ Failed ({len(failed)})")
        a(f"")
        for t in failed:
            a(f"- {t}")
        a(f"")

    # --- Errors ---
    if errors:
        a(f"## 💥 Error ({len(errors)})")
        a(f"")
        for t in errors:
            a(f"- {t}")
        a(f"")

    # --- Detail setiap failure/error ---
    if failure_details:
        a(f"## 🔍 Detail Error & Cara Menyelesaikannya")
        a(f"")
        for i, item in enumerate(failure_details, 1):
            cause, fix = error_explanation(item['detail'])
            a(f"### {i}. {item['title']}")
            a(f"")
            a(f"**🔎 Penyebab:** {cause}")
            a(f"")
            a(f"**🔧 Cara Fix:** {fix}")
            a(f"")
            a(f"<details>")
            a(f"<summary>📋 Lihat Traceback Lengkap</summary>")
            a(f"")
            a(f"```")
            a(item['detail'])
            a(f"```")
            a(f"</details>")
            a(f"")

    # --- Coverage ---
    a(f"## 📈 Coverage Report")
    a(f"")
    if coverage_rows:
        a(f"| File | Statements | Missed | Coverage |")
        a(f"|---|---|---|---|")
        for row in coverage_rows:
            badge = coverage_badge(row['cover'])
            a(f"| `{row['file']}` | {row['stmts']} | {row['miss']} | {badge} {row['cover']} |")
        a(f"")
        a(f"> 🟢 ≥80% &nbsp; 🟡 60–79% &nbsp; 🔴 <60%")
        a(f">")
        a(f"> Laporan HTML lengkap: `htmlcov/index.html`")
    else:
        a(f"> ⚠️ Coverage data tidak tersedia. Pastikan `coverage` sudah terinstall:")
        a(f"> ```")
        a(f"> pip install coverage")
        a(f"> ```")
    a(f"")

    # --- Raw output (collapsible) ---
    a(f"## 📄 Raw Test Output")
    a(f"")
    a(f"<details>")
    a(f"<summary>Klik untuk lihat output lengkap dari terminal</summary>")
    a(f"")
    a(f"```")
    a(test_output[:8000])  # Batasi agar file tidak terlalu besar
    if len(test_output) > 8000:
        a(f"... (output dipotong, lihat terminal untuk lengkapnya)")
    a(f"```")
    a(f"</details>")
    a(f"")

    # --- Footer ---
    a(f"---")
    a(f"*Report ini di-generate otomatis oleh `tools/run_tests_report.py`*  ")
    a(f"*Lumra SaaS Retail — Enterprise Grade Testing*")

    # ----------------------------------------------------------
    # STEP 5: Simpan file
    # ----------------------------------------------------------
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n{'='*55}")
    print(f"  {'✅ Semua test passed!' if test_passed else '❌ Ada test yang gagal!'}")
    print(f"  📄 Report  : reports/test_report_{TIMESTAMP}.md")
    print(f"  🌐 Coverage: htmlcov/index.html")
    print(f"{'='*55}")

    return 0 if test_passed else 1


if __name__ == '__main__':
    sys.exit(main())