#!/usr/bin/env python3
"""
lumra_migrate_fix.py — Fix Migration PostgreSQL (Clean Reset)
=============================================================
Database boleh di-reset bersih.

Skrip ini akan:
  1. Drop SEMUA tabel di database
  2. Hapus folder migrations/ lama
  3. Buat migration baru dari scratch
  4. Migrate bersih

CARA PAKAI:
  Letakkan di folder yang sama dengan manage.py, lalu:

    python lumra_migrate_fix.py

  Opsi lain:
    python lumra_migrate_fix.py --check-only    (diagnosis saja)
    python lumra_migrate_fix.py --fake-initial  (pertahankan data)
    python lumra_migrate_fix.py --project-dir D:\\APPS\\Project\\lumra
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


def banner(msg, c="="):
    print(f"\n{c*62}\n  {msg}\n{c*62}")
def ok(msg):    print(f"  \033[32m✓\033[0m  {msg}")
def err(msg):   print(f"  \033[31m✗\033[0m  {msg}")
def warn(msg):  print(f"  \033[33m!\033[0m  {msg}")
def info(msg):  print(f"  \033[36m→\033[0m  {msg}")
def step(n, msg): print(f"\n  \033[1m[Step {n}]\033[0m {msg}")


def run(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def find_manage(start: Path) -> Path:
    for p in [start / "manage.py", start / "lumra" / "manage.py"]:
        if p.exists():
            return p
    for p in start.rglob("manage.py"):
        return p
    return None


def find_python(manage_py: Path) -> str:
    candidates = [
        # Struktur project Anda: D:\APPS\Project\lumra\core\.venv
        manage_py.parent.parent / "core" / ".venv" / "Scripts" / "python.exe",
        manage_py.parent.parent / "core" / ".venv" / "bin" / "python",
        manage_py.parent / ".venv" / "Scripts" / "python.exe",
        manage_py.parent / ".venv" / "bin" / "python",
        manage_py.parent / "venv" / "Scripts" / "python.exe",
        manage_py.parent / "venv" / "bin" / "python",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable


def find_migrations(manage_parent: Path) -> Path:
    for p in [
        manage_parent / "lumra_config" / "migrations",
        manage_parent / "lumra" / "lumra_config" / "migrations",
    ]:
        if p.exists():
            return p
    return manage_parent / "lumra_config" / "migrations"


def manage_cmd(python: str, manage_py: Path, args: str):
    cmd = f'"{python}" "{manage_py}" {args}'
    return run(cmd, cwd=str(manage_py.parent))


# ══════════════════════════════════════════════════════════════
# DIAGNOSIS
# ══════════════════════════════════════════════════════════════

def diagnose(python: str, manage_py: Path):
    banner("DIAGNOSIS", "-")

    step("D1", "Cek koneksi & isi database")

    script = """\
import django, os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')
try:
    django.setup()
    from django.db import connection
    tables = sorted(connection.introspection.table_names())
    print(f"OK:{len(tables)}")
    for t in tables:
        print(f"T:{t}")
except Exception as e:
    print(f"ERR:{e}")
"""
    tmp = manage_py.parent / "_diag.py"
    tmp.write_text(script, encoding="utf-8")
    code, out, _ = run(f'"{python}" "{tmp}"', cwd=str(manage_py.parent))
    tmp.unlink(missing_ok=True)

    tables = []
    if out.startswith("OK:"):
        count = int(out.split('\n')[0].replace("OK:", ""))
        tables = [l.replace("T:", "") for l in out.split('\n') if l.startswith("T:")]
        ok(f"Koneksi PostgreSQL OK — {count} tabel ditemukan")

        lumra_tables   = [t for t in tables if t.startswith("lumra_config_")]
        prod_tables    = [t for t in tables if t.startswith("production_")]
        django_tables  = [t for t in tables if t.startswith("django_") or t.startswith("auth_")]
        other_tables   = [t for t in tables if t not in lumra_tables + prod_tables + django_tables]

        print(f"\n       Breakdown tabel:")
        print(f"       {'lumra_config_*':<30} {len(lumra_tables)} tabel")
        print(f"       {'production_*':<30} {len(prod_tables)} tabel  ← shared dgn core")
        print(f"       {'django_* / auth_*':<30} {len(django_tables)} tabel")
        if other_tables:
            print(f"       {'lainnya':<30} {len(other_tables)} tabel")

        if prod_tables:
            print()
            warn("Tabel production_* sudah ada (dari core) — ini penyebab error DuplicateTable")
            for t in prod_tables:
                print(f"       ⚠  {t}")
    elif out.startswith("ERR:"):
        err(f"Koneksi gagal: {out.replace('ERR:', '')}")
        err("Pastikan PostgreSQL berjalan dan settings DATABASE sudah benar")
    else:
        warn(f"Tidak bisa cek tabel: {out[:200]}")

    step("D2", "Status migration lumra_config")
    code, out, _ = manage_cmd(python, manage_py, "showmigrations lumra_config")
    if "(no migrations)" in out or not out.strip():
        warn("Belum ada migration untuk lumra_config → perlu makemigrations")
    else:
        applied = [l for l in out.split('\n') if '[X]' in l]
        pending = [l for l in out.split('\n') if '[ ]' in l]
        if applied:
            ok(f"{len(applied)} migration sudah diapply")
        if pending:
            warn(f"{len(pending)} migration belum diapply")

    return tables


# ══════════════════════════════════════════════════════════════
# STRATEGI A: CLEAN RESET
# ══════════════════════════════════════════════════════════════

def strategy_clean_reset(python: str, manage_py: Path) -> bool:

    # Step 1: Drop semua tabel
    step(1, "Drop semua tabel di PostgreSQL")

    drop_script = """\
import django, os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_system.settings')
django.setup()
from django.db import connection
with connection.cursor() as cur:
    cur.execute(\"\"\"
        DO $$ DECLARE r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public')
            LOOP
                EXECUTE 'DROP TABLE IF EXISTS \"' || r.tablename || '\" CASCADE';
            END LOOP;
        END $$;
    \"\"\")
with connection.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'")
    remaining = cur.fetchone()[0]
print(f"DROP_OK:{remaining}")
"""
    tmp = manage_py.parent / "_drop.py"
    tmp.write_text(drop_script, encoding="utf-8")
    code, out, stderr = run(f'"{python}" "{tmp}"', cwd=str(manage_py.parent))
    tmp.unlink(missing_ok=True)

    if "DROP_OK:0" in out:
        ok("Semua tabel berhasil di-drop (0 tersisa)")
    elif "DROP_OK:" in out:
        n = out.split("DROP_OK:")[1].split('\n')[0]
        ok(f"Drop selesai ({n} tabel tersisa — mungkin system tables)")
    else:
        err(f"Gagal drop tabel:\n  {stderr[:400]}")
        print("""
  Coba manual di psql atau pgAdmin:
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;
    GRANT ALL ON SCHEMA public TO postgres;
    GRANT ALL ON SCHEMA public TO public;
        """)
        return False

    # Step 2: Hapus migrations lama
    step(2, "Bersihkan migrations/ lama")

    mig_dir = find_migrations(manage_py.parent)
    if mig_dir.exists():
        deleted = 0
        for f in mig_dir.iterdir():
            if f.name != "__init__.py" and (f.suffix == ".py" or f.is_dir()):
                if f.is_dir():
                    shutil.rmtree(f, ignore_errors=True)
                else:
                    f.unlink()
                deleted += 1
        ok(f"Dihapus {deleted} file/folder migration lama")
    else:
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "__init__.py").touch()
        ok(f"Folder migrations/ dibuat: {mig_dir}")

    # Pastikan __init__.py ada
    init = mig_dir / "__init__.py"
    if not init.exists():
        init.touch()

    # Step 3: makemigrations
    step(3, "makemigrations lumra_config")

    code, out, stderr = manage_cmd(python, manage_py, "makemigrations lumra_config")
    if code == 0:
        ok("makemigrations berhasil")
        for line in out.split('\n'):
            if line.strip(): print(f"       {line}")
    else:
        err("makemigrations gagal:")
        for line in stderr.split('\n')[:20]:
            if line.strip(): print(f"    \033[31m{line}\033[0m")
        err("Kemungkinan ada error di models.py — cek dengan: python manage.py check")
        return False

    # Step 4: migrate
    step(4, "migrate — buat semua tabel baru")

    code, out, stderr = manage_cmd(python, manage_py, "migrate")
    if code == 0:
        ok("migrate berhasil!")
        for line in out.split('\n'):
            if not line.strip(): continue
            icon = "✓" if ("OK" in line or "Applying" in line) else "→"
            print(f"       {icon} {line.strip()}")
        return True
    else:
        err("migrate gagal:")
        for line in stderr.split('\n')[:20]:
            if line.strip(): print(f"    \033[31m{line}\033[0m")
        return False


# ══════════════════════════════════════════════════════════════
# STRATEGI B: FAKE-INITIAL (pertahankan data)
# ══════════════════════════════════════════════════════════════

def strategy_fake_initial(python: str, manage_py: Path) -> bool:

    step(1, "makemigrations lumra_config")
    code, out, stderr = manage_cmd(python, manage_py, "makemigrations lumra_config")
    if code == 0:
        ok("makemigrations OK")
        for line in out.split('\n'):
            if line.strip(): print(f"       {line}")
    else:
        if "No changes" in out + stderr:
            ok("Tidak ada perubahan model")
        else:
            warn(f"Warning: {stderr[:200]}")

    step(2, "migrate --fake-initial")
    info("Tabel yang sudah ada akan di-skip, tabel baru akan dibuat")
    code, out, stderr = manage_cmd(python, manage_py, "migrate --fake-initial")
    if code == 0:
        ok("migrate --fake-initial berhasil!")
        for line in out.split('\n'):
            if line.strip(): print(f"       {line.strip()}")
        return True
    else:
        err(f"Gagal: {stderr[:300]}")
        warn("Coba manual:")
        print("    python manage.py migrate lumra_config 0001 --fake")
        print("    python manage.py migrate")
        return False


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Fix migration error PostgreSQL — Lumra ERP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--project-dir", "-p", default=".",
                        help="Folder berisi manage.py (default: folder sekarang)")
    parser.add_argument("--check-only", "-c", action="store_true",
                        help="Diagnosis saja, tidak ubah apapun")
    parser.add_argument("--fake-initial", action="store_true",
                        help="Pertahankan data (fake-initial)")
    parser.add_argument("--python", default=None,
                        help="Path python interpreter (default: auto-detect venv)")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    banner("LUMRA MIGRATE FIX")
    print(f"  Project dir : {project_dir}")

    manage_py = find_manage(project_dir)
    if not manage_py:
        err("manage.py tidak ditemukan!")
        print("\n  Coba: python lumra_migrate_fix.py --project-dir D:\\APPS\\Project\\lumra")
        sys.exit(1)
    ok(f"manage.py   : {manage_py}")

    python = args.python or find_python(manage_py)
    ok(f"Python      : {python}")

    mode = "CHECK ONLY" if args.check_only else ("FAKE-INITIAL" if args.fake_initial else "CLEAN RESET")
    print(f"  Mode        : \033[1m{mode}\033[0m")

    # Selalu diagnosis dulu
    diagnose(python, manage_py)

    if args.check_only:
        banner("REKOMENDASI")
        print("""
  Jalankan clean reset (database dikosongkan, buat ulang):

    python lumra_migrate_fix.py

  Atau jika ada data yang mau dipertahankan:

    python lumra_migrate_fix.py --fake-initial
        """)
        return

    # Konfirmasi untuk clean reset
    if not args.fake_initial:
        banner("KONFIRMASI", "!")
        print("""
  ⚠️  CLEAN RESET — semua tabel akan di-DROP dan dibuat ulang.
  ⚠️  Semua data di database akan HILANG.
        """)
        confirm = input("  Ketik 'reset' untuk lanjut, Enter untuk batal: ").strip()
        if confirm.lower() != "reset":
            info("Dibatalkan.")
            return

    banner("MENJALANKAN FIX")

    if args.fake_initial:
        success = strategy_fake_initial(python, manage_py)
    else:
        success = strategy_clean_reset(python, manage_py)

    banner("VERIFIKASI AKHIR")
    if success:
        code, out, stderr = manage_cmd(python, manage_py, "check")
        if code == 0:
            ok("manage.py check → \033[32mPASSED\033[0m ✓")
        else:
            warn("Ada issue di manage.py check:")
            for line in (out + "\n" + stderr).split('\n')[:10]:
                if line.strip(): print(f"    {line}")

        print(f"""
  \033[32m\033[1m✓ Database bersih! Langkah selanjutnya:\033[0m

    1. Buat superuser:
         python manage.py createsuperuser

    2. Jalankan server:
         python manage.py runserver

    3. Buka browser:
         http://localhost:8000/
        """)
    else:
        err("Fix tidak berhasil — lihat pesan error di atas")
        print("""
  Coba manual di psql:
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;
    GRANT ALL ON SCHEMA public TO postgres;

  Lalu:
    python manage.py makemigrations lumra_config
    python manage.py migrate
        """)


if __name__ == "__main__":
    main()