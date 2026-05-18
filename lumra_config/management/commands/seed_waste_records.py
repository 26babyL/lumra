"""
seed_waste_records.py
=====================
Mengisi tabel production_waste_records langsung via raw SQL.

Kenapa raw SQL dan bukan Django ORM?
  Model ProductionWasteRecords punya managed=False di Meta class.
  Django tidak expose model ini via apps.get_models() dengan cara biasa,
  sehingga _by_table() dan apps.get_model() selalu return None.
  Raw SQL langsung ke DB adalah solusi paling bersih dan paling cepat.

Sumber data:
  - production_material_consumptions (684,606 rows) JOIN production_orders
  - ~12% dari consumptions dipilih secara random -> waste record
  - waste_qty = 1-5% dari qty konsumsi

Cara pakai:
  # Standalone (langsung ke PostgreSQL):
  python seed_waste_records.py --dry-run
  python seed_waste_records.py --execute

  # Atau sebagai Django management command:
  python manage.py seed_waste_records --execute
  python manage.py seed_waste_records --dry-run
  python manage.py seed_waste_records --execute --rate=0.15 --batch=2000

Args:
  --execute     Sungguhan tulis ke DB (default: dry-run)
  --rate=0.12   Persentase consumptions yang jadi waste (default: 12%)
  --batch=1000  Ukuran batch insert (default: 1000)
  --limit=0     Max rows yang dibaca (0 = semua, default: 0)
"""

import os
import sys
import random
import time
from decimal import Decimal, ROUND_HALF_UP

# ── UTF-8 ─────────────────────────────────────────────────────────────────────
for _s in ("stdout", "stderr"):
    _obj = getattr(sys, _s, None)
    if hasattr(_obj, "reconfigure"):
        try:
            _obj.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# ── Parse args ────────────────────────────────────────────────────────────────
DRY_RUN  = "--execute" not in sys.argv
RATE     = 0.12
BATCH    = 1000
LIMIT    = 0

for arg in sys.argv[1:]:
    if arg.startswith("--rate="):
        RATE = float(arg.split("=", 1)[1])
    elif arg.startswith("--batch="):
        BATCH = int(arg.split("=", 1)[1])
    elif arg.startswith("--limit="):
        LIMIT = int(arg.split("=", 1)[1])

RNG = random.Random(42)

WASTE_TYPES = ["defect", "spillage", "expired", "process_loss", "damage"]

# ── Django setup ──────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")

import django
django.setup()

from django.db import connection
from django.utils import timezone

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Cek kondisi awal
# ═══════════════════════════════════════════════════════════════════════════════

def check_tables():
    """Verifikasi semua tabel yang dibutuhkan ada dan cek row count."""
    with connection.cursor() as cur:
        tables_to_check = [
            "production_waste_records",
            "production_material_consumptions",
            "production_orders",
            "lumra_config_productvariants",
            "lumra_config_units",
        ]
        print("\n  Cek tabel:")
        info = {}
        for tbl in tables_to_check:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                cnt = cur.fetchone()[0]
                print(f"    {tbl:<45} {cnt:>12,} rows")
                info[tbl] = cnt
            except Exception as e:
                print(f"    {tbl:<45} ERROR: {e}")
                info[tbl] = -1
        return info


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Baca sumber data
# ═══════════════════════════════════════════════════════════════════════════════

READ_SQL = """
SELECT
    mc.id                    AS mc_id,
    mc.production_order_id   AS po_id,
    mc.component_id          AS component_id,
    mc.unit_id               AS unit_id,
    mc.quantity              AS qty,
    COALESCE(
        po.completed_at,
        po.started_at,
        po.created_at,
        NOW()
    )                        AS base_time
FROM production_material_consumptions mc
JOIN production_orders po
    ON po.id = mc.production_order_id
WHERE po.status = 'completed'
  AND mc.quantity > 0
{limit_clause}
ORDER BY mc.id
"""


def load_consumptions(limit=0):
    limit_clause = f"LIMIT {limit}" if limit > 0 else ""
    sql = READ_SQL.format(limit_clause=limit_clause)

    print(f"\n  Membaca consumptions dari DB...", end="", flush=True)
    t0 = time.time()

    with connection.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    elapsed = time.time() - t0
    print(f" {len(rows):,} rows ({elapsed:.1f}s)")
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Generate waste records
# ═══════════════════════════════════════════════════════════════════════════════

def generate_waste_rows(consumptions, rate=0.12):
    """
    Dari list consumptions, pilih ~rate% secara random.
    Return list of tuples siap INSERT.

    Kolom INSERT:
      production_order_id, component_id, unit_id,
      waste_type, quantity, recorded_at, notes
    """
    print(f"\n  Generating waste records (rate={rate:.0%})...", end="", flush=True)
    t0 = time.time()

    waste_rows = []
    tz_name = connection.settings_dict.get("TIME_ZONE", "UTC")

    for row in consumptions:
        mc_id, po_id, comp_id, unit_id, qty, base_time = row

        # Random selection
        if RNG.random() > rate:
            continue

        # Qty waste: 1-5% dari qty konsumsi
        waste_pct = Decimal(str(round(RNG.uniform(0.01, 0.05), 4)))
        raw_qty   = Decimal(str(qty)) * waste_pct
        waste_qty = raw_qty.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if waste_qty <= Decimal("0.00"):
            waste_qty = Decimal("0.01")

        # Waktu: base_time + 0-4 jam
        offset_hours = RNG.randint(0, 4)
        offset_mins  = RNG.randint(0, 59)

        # base_time sudah aware dari PostgreSQL COALESCE(completed_at, ...)
        # PostgreSQL mengembalikan datetime aware jika kolom punya timezone info
        recorded_at = f"{base_time} + interval '{offset_hours} hours {offset_mins} minutes'"

        waste_type = RNG.choice(WASTE_TYPES)
        notes      = f"Waste dari produksi (rate: {float(waste_pct):.1%})"

        waste_rows.append((
            po_id,
            comp_id,   # nullable
            unit_id,   # nullable
            waste_type,
            waste_qty,
            offset_hours,   # akan diolah saat insert
            offset_mins,
            base_time,
            notes,
        ))

    elapsed = time.time() - t0
    print(f" {len(waste_rows):,} waste rows ({elapsed:.1f}s)")
    return waste_rows


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Insert ke DB
# ═══════════════════════════════════════════════════════════════════════════════

INSERT_SQL = """
INSERT INTO production_waste_records
    (production_order_id, component_id, unit_id,
     waste_type, quantity, recorded_at, notes)
VALUES
    (%s, %s, %s, %s, %s, %s + interval '1 hour' * %s + interval '1 minute' * %s, %s)
ON CONFLICT DO NOTHING
"""

# Versi yang lebih simple kalau interval syntax bermasalah:
INSERT_SQL_SIMPLE = """
INSERT INTO production_waste_records
    (production_order_id, component_id, unit_id,
     waste_type, quantity, recorded_at, notes)
VALUES
    (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""


def insert_waste(waste_rows, batch_size=1000, dry_run=True):
    if dry_run:
        print(f"\n  [DRY RUN] Akan insert {len(waste_rows):,} rows")
        print(f"  Contoh 3 rows pertama:")
        for row in waste_rows[:3]:
            po_id, comp_id, unit_id, wtype, qty, oh, om, bt, notes = row
            print(f"    po={po_id}  comp={comp_id}  unit={unit_id}  "
                  f"type={wtype}  qty={qty}  notes={notes[:30]}")
        return 0

    total_inserted = 0
    total_batches  = (len(waste_rows) + batch_size - 1) // batch_size
    t0             = time.time()
    errors         = 0

    print(f"\n  Inserting {len(waste_rows):,} rows dalam {total_batches} batch "
          f"(batch_size={batch_size})...")

    # Coba insert dengan datetime yang sudah dihitung di Python dulu
    # (lebih portable dari interval SQL)
    from datetime import timedelta as td

    for batch_num, start in enumerate(range(0, len(waste_rows), batch_size)):
        chunk = waste_rows[start:start + batch_size]

        # Build params tuple — hitung recorded_at di Python
        params = []
        for row in chunk:
            po_id, comp_id, unit_id, wtype, qty, oh, om, base_time, notes = row

            # base_time dari psycopg2 sudah berupa datetime object
            if hasattr(base_time, 'year'):
                recorded_at = base_time + td(hours=oh, minutes=om)
                # Pastikan aware
                if timezone.is_naive(recorded_at):
                    recorded_at = timezone.make_aware(recorded_at)
            else:
                recorded_at = timezone.now()

            params.append((
                po_id,
                comp_id,   # bisa None
                unit_id,   # bisa None
                wtype,
                qty,
                recorded_at,
                notes,
            ))

        try:
            with connection.cursor() as cur:
                cur.executemany(INSERT_SQL_SIMPLE, params)
                total_inserted += cur.rowcount if cur.rowcount >= 0 else len(params)
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"\n    ⚠  Batch {batch_num+1} error: {e}")
                # Coba satu per satu untuk identifikasi row bermasalah
                for p in params:
                    try:
                        with connection.cursor() as cur:
                            cur.execute(INSERT_SQL_SIMPLE, p)
                            total_inserted += 1
                    except Exception as row_err:
                        if errors <= 3:
                            print(f"       Row error: {row_err} | data: {p[:4]}")
                        errors += 1

        # Progress bar
        pct     = (batch_num + 1) / total_batches * 100
        elapsed = time.time() - t0
        eta     = (elapsed / (batch_num + 1)) * (total_batches - batch_num - 1)
        bar     = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"\r    [{bar}] {pct:5.1f}%  inserted={total_inserted:,}  "
              f"err={errors}  ETA={eta:.0f}s   ",
              end="", flush=True)

    elapsed = time.time() - t0
    print(f"\n\n  ✓ Selesai dalam {elapsed:.1f}s")
    print(f"    Inserted : {total_inserted:,}")
    print(f"    Errors   : {errors}")
    return total_inserted


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Verifikasi hasil
# ═══════════════════════════════════════════════════════════════════════════════

def verify_results():
    print("\n  Verifikasi hasil:")
    with connection.cursor() as cur:
        # Total count
        cur.execute("SELECT COUNT(*) FROM production_waste_records")
        total = cur.fetchone()[0]
        print(f"    Total rows         : {total:,}")

        # Per waste_type
        cur.execute("""
            SELECT waste_type, COUNT(*), 
                   ROUND(AVG(quantity::numeric), 3),
                   ROUND(SUM(quantity::numeric), 2)
            FROM production_waste_records
            GROUP BY waste_type
            ORDER BY COUNT(*) DESC
        """)
        rows = cur.fetchall()
        print(f"\n    {'waste_type':<15} {'count':>8}  {'avg_qty':>10}  {'total_qty':>12}")
        print(f"    {'─'*15} {'─'*8}  {'─'*10}  {'─'*12}")
        for wtype, cnt, avg_qty, total_qty in rows:
            print(f"    {wtype:<15} {cnt:>8,}  {avg_qty:>10}  {total_qty:>12}")

        # Sample rows
        cur.execute("""
            SELECT wr.id, wr.production_order_id, wr.component_id, 
                   wr.waste_type, wr.quantity, wr.recorded_at
            FROM production_waste_records wr
            ORDER BY wr.id
            LIMIT 5
        """)
        samples = cur.fetchall()
        print(f"\n    Sample 5 rows:")
        for s in samples:
            print(f"      id={s[0]}  po={s[1]}  comp={s[2]}  "
                  f"type={s[3]}  qty={s[4]}  at={s[5]}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 70)
    print("  SEED production_waste_records (raw SQL)")
    print("═" * 70)
    print(f"  Mode      : {'DRY RUN — tidak ada yang disimpan' if DRY_RUN else 'EXECUTE — menulis ke DB'}")
    print(f"  Rate      : {RATE:.0%} dari consumptions")
    print(f"  Batch size: {BATCH:,}")
    print(f"  Limit     : {'semua' if LIMIT == 0 else f'{LIMIT:,}'}")

    # 1. Cek tabel
    info = check_tables()

    if info.get("production_waste_records", -1) > 0 and not DRY_RUN:
        existing = info["production_waste_records"]
        print(f"\n  ⚠  Tabel sudah berisi {existing:,} rows")
        print("     Script akan menambah data baru (ON CONFLICT DO NOTHING)")
        print("     Tekan Ctrl+C dalam 5 detik untuk batalkan...")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n  Dibatalkan.")
            return

    if info.get("production_material_consumptions", 0) == 0:
        print("\n  ✗ production_material_consumptions kosong — tidak ada sumber data")
        return

    # 2. Load sumber data
    consumptions = load_consumptions(limit=LIMIT)
    if not consumptions:
        print("  ✗ Tidak ada data consumptions — selesai")
        return

    # 3. Generate waste rows
    waste_rows = generate_waste_rows(consumptions, rate=RATE)
    if not waste_rows:
        print("  ✗ Tidak ada waste rows yang digenerate")
        return

    # 4. Estimasi sebelum execute
    print(f"\n  Estimasi:")
    print(f"    Source consumptions : {len(consumptions):,}")
    print(f"    Waste rows          : {len(waste_rows):,} ({len(waste_rows)/len(consumptions):.1%})")
    est_sec = len(waste_rows) / 5000  # ~5000 rows/sec
    print(f"    Estimasi durasi     : {est_sec:.0f}s")

    if DRY_RUN:
        insert_waste(waste_rows, batch_size=BATCH, dry_run=True)
        print("\n  Jalankan dengan --execute untuk menyimpan ke DB")
    else:
        inserted = insert_waste(waste_rows, batch_size=BATCH, dry_run=False)
        if inserted > 0:
            verify_results()

    print("\n" + "═" * 70 + "\n")


# ── Management command wrapper ────────────────────────────────────────────────
try:
    from django.core.management.base import BaseCommand

    class Command(BaseCommand):
        help = "Seed production_waste_records dari material_consumptions via raw SQL"

        def add_arguments(self, parser):
            parser.add_argument("--execute", action="store_true", default=False)
            parser.add_argument("--rate",  type=float, default=0.12)
            parser.add_argument("--batch", type=int,   default=1000)
            parser.add_argument("--limit", type=int,   default=0)

        def handle(self, *args, **opts):
            global DRY_RUN, RATE, BATCH, LIMIT
            DRY_RUN = not opts["execute"]
            RATE    = opts["rate"]
            BATCH   = opts["batch"]
            LIMIT   = opts["limit"]
            main()

except ImportError:
    pass

if __name__ == "__main__":
    main()