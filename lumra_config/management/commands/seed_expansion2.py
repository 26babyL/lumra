"""
seed_expansion2.py
==================
KAFE NUSANTARA — World Building Extension
Ekspansi database tahap 2: semua domain bisnis yang belum ter-cover.

MODUL BARU (10 modul tambahan):
  10. hr              — employees, schedules, attendance, payroll, payslip
  11. loyalty         — loyalty_tiers, stamp_cards, stamp_transactions, rewards, redemptions
  12. customer_journey— sessions, touchpoints, feedback, nps_responses
  13. finance_gl      — chart_of_accounts_ext, journal_entries, gl_postings, budgets, budget_actuals
  14. maintenance      — asset_registry, maintenance_schedules, work_orders, spare_parts
  15. supply_chain     — demand_forecast, reorder_alerts, supplier_scorecards, lead_times
  16. notifications    — notification_templates, notification_log, user_notification_prefs
  17. menu_engineering — menu_items_ext, item_modifiers, combos, menu_performance, ab_tests
  18. waste_costing    — waste_categories, waste_logs, waste_cost_summary, root_cause_tags
  19. training         — courses, enrollments, assessments, certifications, skill_matrix

Jalankan:
  python manage.py seed_expansion2 --execute
  python manage.py seed_expansion2 --execute --section=hr
  python manage.py seed_expansion2 --list-sections
"""

import os, sys, random, time, json, math
from decimal import Decimal
from datetime import date, datetime, timedelta, time as dtime

for _s in ("stdout", "stderr"):
    _o = getattr(sys, _s, None)
    if hasattr(_o, "reconfigure"):
        try: _o.reconfigure(encoding="utf-8", errors="replace")
        except: pass

# ── Args ──────────────────────────────────────────────────────────────────────
DRY_RUN = "--execute" not in sys.argv
SECTION = "all"
for i, a in enumerate(sys.argv[1:], 1):
    if a == "--section" and i < len(sys.argv): SECTION = sys.argv[i]
    elif a.startswith("--section="): SECTION = a.split("=",1)[1]

if "--list-sections" in sys.argv:
    print("Sections: hr loyalty customer_journey finance_gl maintenance "
          "supply_chain notifications menu_engineering waste_costing training all")
    sys.exit(0)

RNG = random.Random(99)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
import django; django.setup()
from django.db import connection

# ── Utilities (sama dengan seed_expansion.py) ─────────────────────────────────
def log(msg):  print(f"  {msg}", flush=True)
def ok(msg):   print(f"  ✓ {msg}", flush=True)
def warn(msg): print(f"  ⚠ {msg}", flush=True)
def head(msg):
    print(f"\n{'▓'*60}\n  {msg}\n{'▓'*60}")

def q(sql, params=None):
    with connection.cursor() as cur:
        cur.execute(sql, params) if params else cur.execute(sql)
        return cur.fetchall()

def q1(sql, params=None):
    rows = q(sql, params)
    return rows[0][0] if rows else None

def table_exists(name):
    return q1("SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s", [name]) > 0

def row_count(name):
    try: return q1(f"SELECT COUNT(*) FROM {name}")
    except: return -1

def execute_sql(sql, label=""):
    try:
        with connection.cursor() as cur:
            cur.execute(sql)
        if label: ok(label)
        return True
    except Exception as e:
        warn(f"{label}: {e}")
        return False

def bulk_insert(table, columns, rows, batch=2000, on_conflict="ON CONFLICT DO NOTHING"):
    if not rows: return 0
    cols = ", ".join(columns)
    ph   = ", ".join(["%s"] * len(columns))
    sql  = f"INSERT INTO {table} ({cols}) VALUES ({ph}) {on_conflict}"
    total = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i:i+batch]
        try:
            with connection.cursor() as cur:
                cur.executemany(sql, chunk)
                total += cur.rowcount if cur.rowcount >= 0 else len(chunk)
        except Exception as e:
            warn(f"Batch {i//batch+1} [{table}]: {e}")
            for row in chunk:
                try:
                    with connection.cursor() as cur:
                        cur.execute(sql, row)
                        total += 1
                except: pass
    return total

def progress(done, total, t0, label=""):
    pct = done / max(1, total) * 100
    ela = time.time() - t0
    eta = (ela / max(1, done)) * (total - done) if done < total else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"\r    [{bar}] {pct:5.1f}%  {done:,}/{total:,}  ETA {eta:.0f}s  {label}   ",
          end="", flush=True)

# ── Context ───────────────────────────────────────────────────────────────────
CTX = {}
def load_context():
    log("Loading context...")
    CTX["admin_id"]     = q1("SELECT id FROM auth_user WHERE is_superuser=true ORDER BY id LIMIT 1") \
                          or q1("SELECT id FROM auth_user ORDER BY id LIMIT 1")
    CTX["user_ids"]     = [r[0] for r in q("SELECT id FROM auth_user WHERE is_active=true ORDER BY id LIMIT 200")]
    CTX["location_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_locations ORDER BY id")]
    CTX["vendor_ids"]   = [r[0] for r in q("SELECT id FROM lumra_config_vendors ORDER BY id")]
    CTX["customer_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_customers WHERE is_active=true ORDER BY id LIMIT 5000")]
    CTX["variant_ids"]  = [r[0] for r in q("SELECT id FROM lumra_config_productvariants ORDER BY id LIMIT 2000")]
    CTX["order_ids"]    = [r[0] for r in q("SELECT id FROM lumra_config_orders WHERE status='completed' ORDER BY id LIMIT 50000")]
    CTX["min_date"]     = q1("SELECT MIN(created_at)::date FROM lumra_config_orders") or date(2023, 1, 1)
    CTX["max_date"]     = q1("SELECT MAX(created_at)::date FROM lumra_config_orders") or date.today()
    ok(f"Context: {len(CTX['location_ids'])} locs, {len(CTX['customer_ids'])} customers, "
       f"{len(CTX['order_ids'])} orders, {len(CTX['user_ids'])} users")

today = date.today()

# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 10 — HR: EMPLOYEES, SCHEDULE, ATTENDANCE, PAYROLL
# ═══════════════════════════════════════════════════════════════════════════════

def fill_hr(dry_run=False):
    head("MODUL 10 — HR (Employees, Schedules, Attendance, Payroll)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS hr_employees (
            id              BIGSERIAL PRIMARY KEY,
            employee_number VARCHAR(20) UNIQUE NOT NULL,
            user_id         BIGINT REFERENCES auth_user(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            full_name       VARCHAR(150) NOT NULL,
            nickname        VARCHAR(50) DEFAULT '',
            role            VARCHAR(40) NOT NULL DEFAULT 'barista',
            department      VARCHAR(40) NOT NULL DEFAULT 'operations',
            join_date       DATE NOT NULL,
            end_date        DATE,
            employment_type VARCHAR(20) DEFAULT 'full_time',
            status          VARCHAR(20) DEFAULT 'active',
            base_salary     NUMERIC(12,2) DEFAULT 0,
            allowance       NUMERIC(10,2) DEFAULT 0,
            bank_name       VARCHAR(50) DEFAULT '',
            bank_account    VARCHAR(30) DEFAULT '',
            phone           VARCHAR(20) DEFAULT '',
            emergency_contact VARCHAR(100) DEFAULT '',
            tax_id          VARCHAR(20) DEFAULT '',
            bpjs_health     VARCHAR(20) DEFAULT '',
            bpjs_employment VARCHAR(20) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE hr_employees IS
            'Karyawan Kafe Nusantara per outpost. Role: barista, cashier, supervisor, kitchen, manager.';
        CREATE INDEX IF NOT EXISTS idx_emp_location ON hr_employees(location_id);
        CREATE INDEX IF NOT EXISTS idx_emp_role ON hr_employees(role, status);
        """, "hr_employees"),

        ("""
        CREATE TABLE IF NOT EXISTS hr_work_schedules (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            schedule_date   DATE NOT NULL,
            shift_type      VARCHAR(20) NOT NULL,
            start_time      TIME NOT NULL,
            end_time        TIME NOT NULL,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            status          VARCHAR(20) DEFAULT 'scheduled',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(employee_id, schedule_date, shift_type)
        );
        COMMENT ON TABLE hr_work_schedules IS 'Jadwal kerja mingguan karyawan.';
        CREATE INDEX IF NOT EXISTS idx_sched_date ON hr_work_schedules(schedule_date);
        CREATE INDEX IF NOT EXISTS idx_sched_emp  ON hr_work_schedules(employee_id);
        """, "hr_work_schedules"),

        ("""
        CREATE TABLE IF NOT EXISTS hr_attendance (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            schedule_id     BIGINT REFERENCES hr_work_schedules(id),
            attendance_date DATE NOT NULL,
            clock_in        TIMESTAMPTZ,
            clock_out       TIMESTAMPTZ,
            late_minutes    INT DEFAULT 0,
            early_out_minutes INT DEFAULT 0,
            overtime_minutes  INT DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'present',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE hr_attendance IS
            'Absensi harian. Status: present, absent, sick, leave, holiday.';
        CREATE INDEX IF NOT EXISTS idx_att_date ON hr_attendance(attendance_date DESC);
        CREATE INDEX IF NOT EXISTS idx_att_emp  ON hr_attendance(employee_id);
        """, "hr_attendance"),

        ("""
        CREATE TABLE IF NOT EXISTS hr_payroll (
            id              BIGSERIAL PRIMARY KEY,
            payroll_period  VARCHAR(7) NOT NULL,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            base_salary     NUMERIC(12,2) DEFAULT 0,
            allowance       NUMERIC(10,2) DEFAULT 0,
            overtime_pay    NUMERIC(10,2) DEFAULT 0,
            deduction_late  NUMERIC(10,2) DEFAULT 0,
            deduction_absent NUMERIC(10,2) DEFAULT 0,
            bpjs_health_emp NUMERIC(10,2) DEFAULT 0,
            bpjs_emp_emp    NUMERIC(10,2) DEFAULT 0,
            pph21           NUMERIC(10,2) DEFAULT 0,
            gross_pay       NUMERIC(12,2) DEFAULT 0,
            net_pay         NUMERIC(12,2) DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'draft',
            paid_at         DATE,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(payroll_period, employee_id)
        );
        COMMENT ON TABLE hr_payroll IS
            'Slip gaji bulanan per karyawan. Period format: YYYY-MM.';
        CREATE INDEX IF NOT EXISTS idx_payroll_period ON hr_payroll(payroll_period DESC);
        """, "hr_payroll"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    min_date     = CTX["min_date"]
    max_date     = CTX["max_date"]

    # ── Employees ──────────────────────────────────────────────────────────────
    ROLES = ["barista","barista","barista","cashier","cashier","supervisor","kitchen","kitchen","manager"]
    DEPTS = {"barista":"operations","cashier":"operations","supervisor":"operations",
              "kitchen":"kitchen","manager":"management"}
    EMP_TYPES = ["full_time","full_time","full_time","part_time","contract"]

    FIRST_NAMES = ["Adi","Budi","Citra","Dewi","Eko","Fitri","Galih","Hani","Indra","Joko",
                   "Kartika","Luki","Maya","Nanda","Oki","Putri","Reza","Siti","Toni","Umar",
                   "Vina","Wati","Xandra","Yogi","Zahra","Bagas","Dina","Fajar","Gilang","Hendra"]
    LAST_NAMES  = ["Pratama","Wijaya","Santoso","Kusuma","Setiawan","Rahayu","Putra","Dewi",
                   "Saputra","Nugroho","Hidayat","Permata","Wibowo","Kurniawan","Utama"]

    emp_rows = []
    # ~5-8 karyawan per lokasi
    for loc_id in location_ids:
        n_emp = RNG.randint(5, 8)
        for j in range(n_emp):
            emp_num    = f"EMP-{loc_id:03d}-{j+1:03d}"
            name       = f"{RNG.choice(FIRST_NAMES)} {RNG.choice(LAST_NAMES)}"
            role       = RNG.choice(ROLES)
            dept       = DEPTS[role]
            emp_type   = RNG.choice(EMP_TYPES)
            join_days  = RNG.randint(30, 1200)
            join_date  = today - timedelta(days=join_days)
            base_sal   = Decimal(str({
                "barista": RNG.randint(3000000, 4500000),
                "cashier": RNG.randint(3000000, 4200000),
                "kitchen": RNG.randint(2800000, 4000000),
                "supervisor": RNG.randint(4500000, 6000000),
                "manager": RNG.randint(6000000, 10000000),
            }[role]))
            allowance  = base_sal * Decimal("0.1")
            uid        = RNG.choice(user_ids) if user_ids else None
            emp_rows.append((
                emp_num, uid, loc_id, name,
                name.split()[0], role, dept,
                join_date, None, emp_type, "active",
                base_sal, allowance,
                RNG.choice(["BCA","BNI","Mandiri","BRI"]),
                f"{RNG.randint(1000000000,9999999999)}",
                f"08{RNG.randint(100000000,999999999)}",
                f"{RNG.choice(FIRST_NAMES)} {RNG.choice(LAST_NAMES)} (Saudara)",
                f"{RNG.randint(10,99)}.{RNG.randint(100,999)}.{RNG.randint(100,999)}.{RNG.randint(1,9)}-{RNG.randint(100,999)}.{RNG.randint(100,999)}",
                f"BPJSK{RNG.randint(100000000,999999999)}",
                f"BPJSM{RNG.randint(100000000,999999999)}",
                join_date, join_date
            ))

    log(f"Employees: {len(emp_rows)}")
    if dry_run:
        log(f"[DRY RUN] {len(emp_rows)} employees, schedules, attendance, payroll")
        return

    n = bulk_insert("hr_employees",
        ["employee_number","user_id","location_id","full_name","nickname",
         "role","department","join_date","end_date","employment_type","status",
         "base_salary","allowance","bank_name","bank_account","phone",
         "emergency_contact","tax_id","bpjs_health","bpjs_employment",
         "created_at","updated_at"],
        emp_rows, on_conflict="ON CONFLICT (employee_number) DO NOTHING")
    ok(f"Employees: {n:,}")

    # ── Schedules ──────────────────────────────────────────────────────────────
    employees = q("SELECT id, location_id FROM hr_employees ORDER BY id")
    SHIFT_MAP = [
        ("first_light",      dtime(7,0),  dtime(12,0)),
        ("midday_transit",   dtime(12,0), dtime(18,0)),
        ("twilight_bivouac", dtime(18,0), dtime(23,0)),
    ]

    sched_rows = []
    # 30 hari ke depan + 30 hari ke belakang
    for emp_id, loc_id in employees:
        for d in range(-30, 31):
            sched_date = today + timedelta(days=d)
            # random 1-2 shift per hari, skip 1 hari/minggu (libur)
            if sched_date.weekday() == RNG.randint(0, 6):
                continue
            stype, st, et = RNG.choice(SHIFT_MAP)
            sched_rows.append((
                emp_id, sched_date, stype, st, et, loc_id,
                "completed" if d < 0 else "scheduled",
                "", datetime.now()
            ))

    n = bulk_insert("hr_work_schedules",
        ["employee_id","schedule_date","shift_type","start_time","end_time",
         "location_id","status","notes","created_at"],
        sched_rows, batch=3000,
        on_conflict="ON CONFLICT (employee_id, schedule_date, shift_type) DO NOTHING")
    ok(f"Schedules: {n:,}")

    # ── Attendance ─────────────────────────────────────────────────────────────
    saved_scheds = q("SELECT id, employee_id, schedule_date, start_time, end_time FROM hr_work_schedules WHERE schedule_date < %s ORDER BY id", [today])
    att_rows = []
    for sid, emp_id, sched_date, st, et in saved_scheds:
        status = RNG.choices(
            ["present","present","present","present","absent","sick","leave"],
            weights=[70, 0, 0, 0, 10, 15, 5]
        )[0]
        late = RNG.randint(0, 30) if status == "present" and RNG.random() < 0.2 else 0
        overtime = RNG.randint(0, 90) if status == "present" and RNG.random() < 0.15 else 0
        clock_in  = datetime.combine(sched_date, st) + timedelta(minutes=late) if status == "present" else None
        clock_out = datetime.combine(sched_date, et) + timedelta(minutes=overtime) if status == "present" else None
        att_rows.append((
            emp_id, sid, sched_date,
            clock_in, clock_out,
            late, 0, overtime,
            status, "", datetime.now()
        ))

    n = bulk_insert("hr_attendance",
        ["employee_id","schedule_id","attendance_date","clock_in","clock_out",
         "late_minutes","early_out_minutes","overtime_minutes","status","notes","created_at"],
        att_rows, batch=3000)
    ok(f"Attendance: {n:,}")

    # ── Payroll ────────────────────────────────────────────────────────────────
    emp_detail = q("SELECT id, base_salary, allowance FROM hr_employees")
    payroll_rows = []
    # 12 bulan ke belakang
    for yr_offset in range(12):
        ref = today.replace(day=1) - timedelta(days=yr_offset * 30)
        period = ref.strftime("%Y-%m")
        for emp_id, base_sal, allowance in emp_detail:
            base_sal  = Decimal(str(base_sal or 0))
            allowance = Decimal(str(allowance or 0))
            overtime  = base_sal / 173 * Decimal(str(RNG.randint(0, 20)))
            ded_late  = base_sal / 173 / 60 * Decimal(str(RNG.randint(0, 60)))
            ded_abs   = base_sal / 26 * Decimal(str(RNG.randint(0, 2)))
            bpjs_h    = (base_sal + allowance) * Decimal("0.01")
            bpjs_e    = (base_sal + allowance) * Decimal("0.02")
            gross     = base_sal + allowance + overtime
            pph21     = max(Decimal("0"), (gross * 12 - 54000000) / 12 * Decimal("0.05"))
            net       = gross - ded_late - ded_abs - bpjs_h - bpjs_e - pph21
            payroll_rows.append((
                period, emp_id,
                base_sal.quantize(Decimal("0.01")),
                allowance.quantize(Decimal("0.01")),
                overtime.quantize(Decimal("0.01")),
                ded_late.quantize(Decimal("0.01")),
                ded_abs.quantize(Decimal("0.01")),
                bpjs_h.quantize(Decimal("0.01")),
                bpjs_e.quantize(Decimal("0.01")),
                pph21.quantize(Decimal("0.01")),
                gross.quantize(Decimal("0.01")),
                net.quantize(Decimal("0.01")),
                "paid", ref + timedelta(days=25),
                "", datetime.now()
            ))

    n = bulk_insert("hr_payroll",
        ["payroll_period","employee_id","base_salary","allowance","overtime_pay",
         "deduction_late","deduction_absent","bpjs_health_emp","bpjs_emp_emp",
         "pph21","gross_pay","net_pay","status","paid_at","notes","created_at"],
        payroll_rows,
        on_conflict="ON CONFLICT (payroll_period, employee_id) DO NOTHING")
    ok(f"Payroll: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 11 — LOYALTY PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def fill_loyalty(dry_run=False):
    head("MODUL 11 — LOYALTY (Tiers, Stamp Cards, Transactions, Rewards)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS loyalty_tiers (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(80) NOT NULL,
            description     TEXT DEFAULT '',
            min_points      INT NOT NULL DEFAULT 0,
            max_points      INT,
            discount_pct    NUMERIC(5,2) DEFAULT 0,
            stamp_multiplier NUMERIC(4,2) DEFAULT 1.0,
            perks           JSONB DEFAULT '[]',
            badge_color     VARCHAR(20) DEFAULT '#888888',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_tiers IS
            'Tier loyalty Kafe Nusantara: Expeditor → Field Surveyor → Cartographer → Grand Curator.';
        """, "loyalty_tiers"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_stamp_cards (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT NOT NULL UNIQUE REFERENCES lumra_config_customers(id),
            card_number     VARCHAR(30) UNIQUE NOT NULL,
            tier_id         BIGINT REFERENCES loyalty_tiers(id),
            total_points    INT DEFAULT 0,
            current_stamps  INT DEFAULT 0,
            lifetime_stamps INT DEFAULT 0,
            lifetime_spend  NUMERIC(15,2) DEFAULT 0,
            outposts_visited INT DEFAULT 0,
            last_visit_date DATE,
            member_since    DATE DEFAULT CURRENT_DATE,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_stamp_cards IS
            'Kartu stamp digital per customer. 10 stamps = 1 reward free drink.';
        CREATE INDEX IF NOT EXISTS idx_stamp_tier ON loyalty_stamp_cards(tier_id);
        """, "loyalty_stamp_cards"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_stamp_transactions (
            id              BIGSERIAL PRIMARY KEY,
            card_id         BIGINT NOT NULL REFERENCES loyalty_stamp_cards(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            transaction_type VARCHAR(20) NOT NULL DEFAULT 'earn',
            stamps_delta    INT NOT NULL DEFAULT 0,
            points_delta    INT NOT NULL DEFAULT 0,
            spend_amount    NUMERIC(12,2) DEFAULT 0,
            note            TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_stamp_transactions IS
            'Riwayat earn/redeem stamp dan poin per transaksi.';
        CREATE INDEX IF NOT EXISTS idx_stamp_tx_card ON loyalty_stamp_transactions(card_id);
        CREATE INDEX IF NOT EXISTS idx_stamp_tx_date ON loyalty_stamp_transactions(created_at DESC);
        """, "loyalty_stamp_transactions"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_rewards (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(120) NOT NULL,
            description     TEXT DEFAULT '',
            reward_type     VARCHAR(30) NOT NULL DEFAULT 'free_drink',
            stamps_required INT DEFAULT 10,
            points_required INT DEFAULT 0,
            valid_days      INT DEFAULT 30,
            is_active       BOOLEAN DEFAULT TRUE,
            stock_limit     INT,
            redeemed_count  INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_rewards IS
            'Katalog reward yang bisa diredeem: free drink, pastry, merchandise, diskon.';
        """, "loyalty_rewards"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_redemptions (
            id              BIGSERIAL PRIMARY KEY,
            card_id         BIGINT NOT NULL REFERENCES loyalty_stamp_cards(id),
            reward_id       BIGINT NOT NULL REFERENCES loyalty_rewards(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            stamps_used     INT DEFAULT 0,
            points_used     INT DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'redeemed',
            redeemed_at     TIMESTAMPTZ DEFAULT NOW(),
            expires_at      TIMESTAMPTZ,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_redemptions IS 'Log redeem reward oleh customer.';
        CREATE INDEX IF NOT EXISTS idx_redemption_card ON loyalty_redemptions(card_id);
        """, "loyalty_redemptions"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # ── Tiers ──────────────────────────────────────────────────────────────────
    tiers_data = [
        ("EXPEDITOR",    "Expeditor",          "Member baru yang baru memulai petualangan.",
         0,     999,  0,   1.0, ["Early bird notification"], "#8B7355"),
        ("FIELD_SURVEYOR","Field Surveyor",    "5+ outpost dikunjungi. Diskon 5% permanent.",
         1000,  4999, 5,   1.2, ["5% discount","Priority queue","Monthly newsletter"], "#4A90A4"),
        ("CARTOGRAPHER", "Senior Cartographer","10+ outpost. Early access menu seasonal.",
         5000,  19999,8,   1.5, ["8% discount","Early access seasonal menu","Free size upgrade 1x/month","Birthday privilege"], "#D4AF37"),
        ("GRAND_CURATOR","Grand Curator",      "Elite member. Akses Grand Reserve menu eksklusif.",
         20000, None, 15,  2.0, ["15% permanent","Grand Reserve access","Free drink monthly","VIP event invite","Personal barista note"], "#1A1A2E"),
    ]
    tier_rows = [(code, name, desc, Decimal(str(minp)), maxp,
                  Decimal(str(disc)), Decimal(str(mult)),
                  json.dumps(perks), color, True, datetime.now())
                 for code, name, desc, minp, maxp, disc, mult, perks, color in tiers_data]

    if not dry_run:
        n = bulk_insert("loyalty_tiers",
            ["code","name","description","min_points","max_points",
             "discount_pct","stamp_multiplier","perks","badge_color","is_active","created_at"],
            tier_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
        ok(f"Loyalty tiers: {n}")

    # ── Rewards catalog ────────────────────────────────────────────────────────
    rewards_data = [
        ("FREE-FILTER",  "Free Filter Coffee",      "1 gelas filter coffee house blend gratis.", "free_drink", 10, 0,   30),
        ("FREE-COLD",    "Free Cold Brew",           "1 gelas cold brew any size.",               "free_drink", 12, 0,   30),
        ("FREE-PASTRY",  "Free Pastry",              "1 pastry pilihan gratis.",                  "free_food",  8,  0,   14),
        ("FREE-GRANOLA", "Free Granola Bowl",        "Granola bowl artisan gratis.",               "free_food",  15, 0,   14),
        ("DISC-20PCT",   "Diskon 20%",               "Diskon 20% untuk satu transaksi.",          "discount",   0,  500, 7),
        ("DISC-50K",     "Voucher Rp 50.000",        "Potongan Rp 50.000 min. transaksi 150rb.",  "voucher",    0,  800, 14),
        ("MERCH-TUMBLER","Kafe Nusantara Tumbler",   "Tumbler edisi terbatas Kafe Nusantara.",    "merchandise",0, 2000, 90),
        ("MERCH-TOTE",   "Expedition Tote Bag",      "Tote bag canvas The Daily Expedition.",     "merchandise",0, 1500, 90),
        ("UPGRADE-SIZE", "Size Upgrade Gratis",      "Upgrade size minuman any size.",             "upgrade",    5,  0,   7),
        ("EARLY-ACCESS", "Early Access Menu Seasonal","Preview menu musim baru 3 hari lebih awal.","experience", 0, 300, 30),
    ]
    reward_rows = [(code, name, desc, rtype, stamps, points, vdays, True, None, 0, datetime.now())
                   for code, name, desc, rtype, stamps, points, vdays in rewards_data]

    if not dry_run:
        n = bulk_insert("loyalty_rewards",
            ["code","name","description","reward_type","stamps_required",
             "points_required","valid_days","is_active","stock_limit","redeemed_count","created_at"],
            reward_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
        ok(f"Rewards: {n}")

    # ── Stamp Cards ────────────────────────────────────────────────────────────
    customer_ids = CTX["customer_ids"]
    tier_ids     = [r[0] for r in q("SELECT id FROM loyalty_tiers ORDER BY min_points")]

    card_rows = []
    for i, cid in enumerate(customer_ids):
        lifetime_stamps = RNG.randint(0, 500)
        lifetime_spend  = Decimal(str(lifetime_stamps * RNG.randint(30000, 80000)))
        current_stamps  = lifetime_stamps % 10
        total_points    = lifetime_stamps * RNG.randint(5, 20)
        # tentukan tier berdasarkan total_points
        tier_id = tier_ids[0]
        for tid, minp in q("SELECT id, min_points FROM loyalty_tiers ORDER BY min_points DESC"):
            if total_points >= minp:
                tier_id = tid
                break
        outposts = min(len(CTX["location_ids"]), RNG.randint(1, 20))
        last_visit = today - timedelta(days=RNG.randint(0, 180))
        card_rows.append((
            cid, f"KN{cid:08d}", tier_id,
            total_points, current_stamps, lifetime_stamps,
            lifetime_spend.quantize(Decimal("0.01")),
            outposts, last_visit,
            today - timedelta(days=RNG.randint(30, 730)),
            True, datetime.now(), datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(card_rows)} stamp cards + transactions + redemptions")
        return

    n = bulk_insert("loyalty_stamp_cards",
        ["customer_id","card_number","tier_id","total_points","current_stamps",
         "lifetime_stamps","lifetime_spend","outposts_visited","last_visit_date",
         "member_since","is_active","created_at","updated_at"],
        card_rows,
        on_conflict="ON CONFLICT (customer_id) DO NOTHING")
    ok(f"Stamp cards: {n:,}")

    # ── Stamp Transactions ─────────────────────────────────────────────────────
    card_data    = q("SELECT id, customer_id FROM loyalty_stamp_cards ORDER BY id LIMIT 3000")
    order_ids    = CTX["order_ids"]
    location_ids = CTX["location_ids"]
    reward_ids   = [r[0] for r in q("SELECT id FROM loyalty_rewards ORDER BY id")]

    stamp_tx_rows   = []
    redemption_rows = []

    for card_id, cust_id in card_data:
        n_tx = RNG.randint(3, 30)
        for _ in range(n_tx):
            tx_type  = RNG.choices(["earn","earn","earn","bonus","redeem"], weights=[60,0,0,20,20])[0]
            stamps   = RNG.randint(1, 3) if tx_type in ("earn","bonus") else -10
            points   = stamps * RNG.randint(5, 15)
            spend    = Decimal(str(RNG.randint(25000, 200000))) if tx_type == "earn" else Decimal("0")
            oid      = RNG.choice(order_ids) if order_ids else None
            lid      = RNG.choice(location_ids)
            tx_date  = datetime.now() - timedelta(days=RNG.randint(0, 365))
            stamp_tx_rows.append((
                card_id, oid, lid, tx_type, stamps, points,
                spend.quantize(Decimal("0.01")), "", tx_date
            ))
            if tx_type == "redeem" and reward_ids:
                rid = RNG.choice(reward_ids)
                redemption_rows.append((
                    card_id, rid, oid, lid, 10, 0,
                    "redeemed", tx_date,
                    tx_date + timedelta(days=30), tx_date
                ))

    n = bulk_insert("loyalty_stamp_transactions",
        ["card_id","order_id","location_id","transaction_type","stamps_delta",
         "points_delta","spend_amount","note","created_at"],
        stamp_tx_rows, batch=3000)
    ok(f"Stamp transactions: {n:,}")

    n = bulk_insert("loyalty_redemptions",
        ["card_id","reward_id","order_id","location_id","stamps_used","points_used",
         "status","redeemed_at","expires_at","created_at"],
        redemption_rows)
    ok(f"Redemptions: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 12 — CUSTOMER JOURNEY (Sessions, Touchpoints, Feedback, NPS)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_customer_journey(dry_run=False):
    head("MODUL 12 — CUSTOMER JOURNEY (Sessions, Touchpoints, Feedback, NPS)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS cj_customer_sessions (
            id              BIGSERIAL PRIMARY KEY,
            session_uuid    UUID DEFAULT gen_random_uuid() UNIQUE,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            channel         VARCHAR(30) DEFAULT 'dine_in',
            session_start   TIMESTAMPTZ NOT NULL,
            session_end     TIMESTAMPTZ,
            duration_minutes INT DEFAULT 0,
            order_count     INT DEFAULT 0,
            total_spend     NUMERIC(12,2) DEFAULT 0,
            device_type     VARCHAR(20) DEFAULT 'unknown',
            referral_source VARCHAR(50) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_customer_sessions IS
            'Sesi kunjungan customer per outpost. Channel: dine_in, takeaway, delivery, online.';
        CREATE INDEX IF NOT EXISTS idx_cj_sess_cust ON cj_customer_sessions(customer_id);
        CREATE INDEX IF NOT EXISTS idx_cj_sess_loc  ON cj_customer_sessions(location_id);
        CREATE INDEX IF NOT EXISTS idx_cj_sess_date ON cj_customer_sessions(session_start DESC);
        """, "cj_customer_sessions"),

        ("""
        CREATE TABLE IF NOT EXISTS cj_touchpoints (
            id              BIGSERIAL PRIMARY KEY,
            session_id      BIGINT REFERENCES cj_customer_sessions(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            touchpoint_type VARCHAR(40) NOT NULL,
            channel         VARCHAR(30) DEFAULT 'dine_in',
            content_ref     VARCHAR(100) DEFAULT '',
            sentiment       VARCHAR(10) DEFAULT 'neutral',
            duration_sec    INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_touchpoints IS
            'Titik interaksi customer: menu_view, order, payment, feedback, loyalty_check, promo_claim.';
        CREATE INDEX IF NOT EXISTS idx_tp_session ON cj_touchpoints(session_id);
        CREATE INDEX IF NOT EXISTS idx_tp_type    ON cj_touchpoints(touchpoint_type);
        """, "cj_touchpoints"),

        ("""
        CREATE TABLE IF NOT EXISTS cj_feedback (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            feedback_type   VARCHAR(30) DEFAULT 'general',
            rating_overall  SMALLINT CHECK(rating_overall BETWEEN 1 AND 5),
            rating_product  SMALLINT CHECK(rating_product BETWEEN 1 AND 5),
            rating_service  SMALLINT CHECK(rating_service BETWEEN 1 AND 5),
            rating_ambiance SMALLINT CHECK(rating_ambiance BETWEEN 1 AND 5),
            comment         TEXT DEFAULT '',
            tags            TEXT[] DEFAULT '{}',
            is_public       BOOLEAN DEFAULT FALSE,
            replied_at      TIMESTAMPTZ,
            reply_text      TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_feedback IS
            'Feedback & rating customer per order/kunjungan. 1-5 bintang multi-dimensi.';
        CREATE INDEX IF NOT EXISTS idx_fb_location ON cj_feedback(location_id);
        CREATE INDEX IF NOT EXISTS idx_fb_rating   ON cj_feedback(rating_overall DESC);
        CREATE INDEX IF NOT EXISTS idx_fb_date     ON cj_feedback(created_at DESC);
        """, "cj_feedback"),

        ("""
        CREATE TABLE IF NOT EXISTS cj_nps_responses (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            survey_period   VARCHAR(7) NOT NULL,
            nps_score       SMALLINT NOT NULL CHECK(nps_score BETWEEN 0 AND 10),
            category        VARCHAR(15) GENERATED ALWAYS AS (
                CASE WHEN nps_score >= 9 THEN 'promoter'
                     WHEN nps_score >= 7 THEN 'passive'
                     ELSE 'detractor' END
            ) STORED,
            reason          TEXT DEFAULT '',
            follow_up_done  BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_nps_responses IS
            'Net Promoter Score survey bulanan. 0-6=detractor, 7-8=passive, 9-10=promoter.';
        CREATE INDEX IF NOT EXISTS idx_nps_period ON cj_nps_responses(survey_period);
        CREATE INDEX IF NOT EXISTS idx_nps_score  ON cj_nps_responses(nps_score);
        """, "cj_nps_responses"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    customer_ids = CTX["customer_ids"]
    location_ids = CTX["location_ids"]
    order_ids    = CTX["order_ids"]
    min_date     = CTX["min_date"]
    max_date     = CTX["max_date"]

    CHANNELS      = ["dine_in","dine_in","dine_in","takeaway","delivery"]
    DEVICES       = ["mobile","mobile","desktop","tablet","unknown"]
    REFERRALS     = ["instagram","google","friend","tiktok","walk_in","walk_in","walk_in"]
    TP_TYPES      = ["menu_view","menu_view","order_placed","payment","loyalty_check",
                     "promo_claim","table_service","takeaway_pickup"]
    SENTIMENTS    = ["positive","positive","neutral","neutral","negative"]
    FB_TYPES      = ["general","product","service","ambiance","complaint","compliment"]
    FB_TAGS       = [["kopi_enak","pelayanan_ramah"],["antri_lama"],["tempatnya_nyaman"],
                     ["harga_worth_it"],["barista_friendly"],["ambiance_bagus"],
                     ["cold_brew_top"],["pastry_fresh"]]
    NPS_REASONS   = [
        "Kopi-nya konsisten enak di semua outpost.",
        "Barista-nya ramah dan selalu ingat pesanan saya.",
        "Tempatnya nyaman untuk kerja.",
        "Harga sesuai dengan kualitas.",
        "Kadang antri terlalu lama.",
        "Menu seasonal selalu menarik.",
        "Sudah jadi tempat nongkrong favorit saya.",
        "Loyalty program-nya bikin betah.",
    ]

    # Sessions
    sess_rows = []
    total_days = (max_date - min_date).days
    for cid in RNG.sample(customer_ids, min(2000, len(customer_ids))):
        n_sess = RNG.randint(1, 15)
        for _ in range(n_sess):
            sess_start = datetime.combine(
                min_date + timedelta(days=RNG.randint(0, total_days)),
                dtime(RNG.randint(7, 22), RNG.randint(0, 59))
            )
            duration  = RNG.randint(10, 120)
            sess_end  = sess_start + timedelta(minutes=duration)
            n_orders  = RNG.randint(0, 3)
            spend     = Decimal(str(n_orders * RNG.randint(20000, 100000)))
            sess_rows.append((
                cid, RNG.choice(location_ids),
                RNG.choice(CHANNELS),
                sess_start, sess_end, duration,
                n_orders, spend.quantize(Decimal("0.01")),
                RNG.choice(DEVICES), RNG.choice(REFERRALS),
                sess_start
            ))

    log(f"Sessions: {len(sess_rows)}")
    if dry_run:
        log(f"[DRY RUN] sessions, touchpoints, feedback, NPS")
        return

    n = bulk_insert("cj_customer_sessions",
        ["customer_id","location_id","channel","session_start","session_end",
         "duration_minutes","order_count","total_spend","device_type","referral_source","created_at"],
        sess_rows, batch=3000)
    ok(f"Sessions: {n:,}")

    # Touchpoints
    saved_sessions = q("SELECT id, customer_id FROM cj_customer_sessions ORDER BY id LIMIT 5000")
    tp_rows = []
    for sess_id, cid in saved_sessions:
        for _ in range(RNG.randint(2, 8)):
            tp_rows.append((
                sess_id, cid,
                RNG.choice(TP_TYPES),
                RNG.choice(CHANNELS),
                "", RNG.choice(SENTIMENTS),
                RNG.randint(5, 300),
                datetime.now() - timedelta(days=RNG.randint(0, 365))
            ))

    n = bulk_insert("cj_touchpoints",
        ["session_id","customer_id","touchpoint_type","channel","content_ref",
         "sentiment","duration_sec","created_at"],
        tp_rows, batch=3000)
    ok(f"Touchpoints: {n:,}")

    # Feedback
    fb_rows = []
    for _ in range(min(10000, len(order_ids))):
        oid  = RNG.choice(order_ids)
        cid  = RNG.choice(customer_ids)
        lid  = RNG.choice(location_ids)
        base = RNG.randint(3, 5)
        fb_rows.append((
            cid, oid, lid,
            RNG.choice(FB_TYPES),
            base,
            max(1, base + RNG.randint(-1, 1)),
            max(1, base + RNG.randint(-1, 1)),
            max(1, base + RNG.randint(-1, 1)),
            "",
            json.dumps(RNG.choice(FB_TAGS)),
            RNG.random() < 0.3,
            None, "",
            datetime.now() - timedelta(days=RNG.randint(0, 365))
        ))

    n = bulk_insert("cj_feedback",
        ["customer_id","order_id","location_id","feedback_type",
         "rating_overall","rating_product","rating_service","rating_ambiance",
         "comment","tags","is_public","replied_at","reply_text","created_at"],
        fb_rows, batch=3000)
    ok(f"Feedback: {n:,}")

    # NPS
    nps_rows = []
    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            if date(yr, mo, 1) > today: break
            period    = f"{yr}-{mo:02d}"
            n_resp    = RNG.randint(30, 150)
            respondents = RNG.sample(customer_ids, min(n_resp, len(customer_ids)))
            for cid in respondents:
                # distribusi NPS: ~60% promoter (9-10), ~20% passive (7-8), ~20% detractor (0-6)
                score = RNG.choices(
                    list(range(11)),
                    weights=[2,2,3,3,4,6,10,10,15,20,25]
                )[0]
                nps_rows.append((
                    cid, RNG.choice(location_ids),
                    period, score,
                    RNG.choice(NPS_REASONS),
                    score < 7,
                    datetime.now() - timedelta(days=RNG.randint(0, 30))
                ))

    n = bulk_insert("cj_nps_responses",
        ["customer_id","location_id","survey_period","nps_score",
         "reason","follow_up_done","created_at"],
        nps_rows)
    ok(f"NPS responses: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 13 — FINANCE GL (Journal Entries, Budgets)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_finance_gl(dry_run=False):
    head("MODUL 13 — FINANCE GL (Journal Entries, GL Postings, Budgets)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS finance_journal_entries (
            id              BIGSERIAL PRIMARY KEY,
            entry_number    VARCHAR(30) UNIQUE NOT NULL,
            entry_date      DATE NOT NULL,
            period          VARCHAR(7) NOT NULL,
            entry_type      VARCHAR(30) NOT NULL DEFAULT 'manual',
            description     TEXT NOT NULL DEFAULT '',
            reference_type  VARCHAR(40) DEFAULT '',
            reference_id    BIGINT,
            total_debit     NUMERIC(15,2) DEFAULT 0,
            total_credit    NUMERIC(15,2) DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'posted',
            created_by_id   BIGINT REFERENCES auth_user(id),
            approved_by_id  BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE finance_journal_entries IS
            'Jurnal akuntansi: penjualan, pembelian, biaya, penyesuaian, opening balance.';
        CREATE INDEX IF NOT EXISTS idx_je_date   ON finance_journal_entries(entry_date DESC);
        CREATE INDEX IF NOT EXISTS idx_je_period ON finance_journal_entries(period);
        CREATE INDEX IF NOT EXISTS idx_je_type   ON finance_journal_entries(entry_type);
        """, "finance_journal_entries"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_gl_postings (
            id              BIGSERIAL PRIMARY KEY,
            journal_id      BIGINT NOT NULL REFERENCES finance_journal_entries(id),
            account_id      BIGINT REFERENCES accounting_accounts(id),
            account_code    VARCHAR(20) NOT NULL DEFAULT '',
            account_name    VARCHAR(100) DEFAULT '',
            debit           NUMERIC(15,2) DEFAULT 0,
            credit          NUMERIC(15,2) DEFAULT 0,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            description     TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE finance_gl_postings IS
            'Baris debit/kredit per jurnal. Double-entry bookkeeping.';
        CREATE INDEX IF NOT EXISTS idx_gl_journal  ON finance_gl_postings(journal_id);
        CREATE INDEX IF NOT EXISTS idx_gl_account  ON finance_gl_postings(account_id);
        CREATE INDEX IF NOT EXISTS idx_gl_location ON finance_gl_postings(location_id);
        """, "finance_gl_postings"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_budgets (
            id              BIGSERIAL PRIMARY KEY,
            budget_year     SMALLINT NOT NULL,
            budget_month    SMALLINT,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            category        VARCHAR(50) NOT NULL,
            account_code    VARCHAR(20) DEFAULT '',
            budget_amount   NUMERIC(15,2) NOT NULL DEFAULT 0,
            notes           TEXT DEFAULT '',
            created_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(budget_year, budget_month, location_id, category)
        );
        COMMENT ON TABLE finance_budgets IS
            'Anggaran tahunan/bulanan per kategori dan lokasi.';
        CREATE INDEX IF NOT EXISTS idx_budget_ym ON finance_budgets(budget_year, budget_month);
        """, "finance_budgets"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_budget_actuals (
            id              BIGSERIAL PRIMARY KEY,
            budget_id       BIGINT NOT NULL REFERENCES finance_budgets(id),
            actual_amount   NUMERIC(15,2) DEFAULT 0,
            variance_amount NUMERIC(15,2) DEFAULT 0,
            variance_pct    NUMERIC(6,2) DEFAULT 0,
            as_of_date      DATE NOT NULL,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(budget_id, as_of_date)
        );
        COMMENT ON TABLE finance_budget_actuals IS
            'Realisasi aktual vs anggaran per periode.';
        """, "finance_budget_actuals"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_cost_centers (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            parent_id       BIGINT REFERENCES finance_cost_centers(id),
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE finance_cost_centers IS
            'Cost center per outpost/departemen untuk alokasi biaya.';
        """, "finance_cost_centers"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    admin_id     = CTX["admin_id"]
    user_ids     = CTX["user_ids"]
    min_date     = CTX["min_date"]

    # Cost Centers
    cc_rows = []
    for lid in location_ids:
        for dept in ["operations","kitchen","management","marketing"]:
            cc_rows.append((
                f"CC-{lid:03d}-{dept[:3].upper()}",
                f"Cost Center {dept.title()} - Loc {lid}",
                lid, None, True, datetime.now()
            ))

    if not dry_run:
        n = bulk_insert("finance_cost_centers",
            ["code","name","location_id","parent_id","is_active","created_at"],
            cc_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
        ok(f"Cost centers: {n}")

    # Journal Entries + GL Postings
    JE_TYPES = ["sales_revenue","purchase_expense","payroll_expense","depreciation",
                "accrual","adjustment","opening_balance"]
    accounts = q("SELECT id, code, name FROM accounting_accounts LIMIT 50")
    if not accounts:
        accounts = [(1,"1-1001","Kas Tunai"),(2,"4-1001","Penjualan"),(3,"5-1001","HPP")]

    je_rows = []
    gl_rows = []
    je_ctr  = 1

    # Generate ~2000 jurnal 2 tahun ke belakang
    ref_date = min_date
    days_range = (today - ref_date).days
    for _ in range(2000):
        entry_date = ref_date + timedelta(days=RNG.randint(0, days_range))
        period     = entry_date.strftime("%Y-%m")
        je_type    = RNG.choice(JE_TYPES)
        amount     = Decimal(str(RNG.randint(100000, 50000000)))
        entry_num  = f"JE-{entry_date.year}-{je_ctr:06d}"
        creator    = RNG.choice(user_ids) if user_ids else admin_id

        je_rows.append((
            entry_num, entry_date, period, je_type,
            f"{je_type.replace('_',' ').title()} - {entry_date}",
            je_type, None,
            amount, amount, "posted",
            creator, admin_id, entry_date
        ))
        je_ctr += 1

    if dry_run:
        log(f"[DRY RUN] ~{len(je_rows)} journal entries + GL postings + budgets")
        return

    n = bulk_insert("finance_journal_entries",
        ["entry_number","entry_date","period","entry_type","description",
         "reference_type","reference_id","total_debit","total_credit","status",
         "created_by_id","approved_by_id","created_at"],
        je_rows, on_conflict="ON CONFLICT (entry_number) DO NOTHING")
    ok(f"Journal entries: {n:,}")

    # GL Postings (2 baris per jurnal: debit + kredit)
    saved_jes = q("SELECT id, total_debit FROM finance_journal_entries ORDER BY id")
    for je_id, amount in saved_jes:
        acc_debit  = RNG.choice(accounts)
        acc_credit = RNG.choice(accounts)
        lid        = RNG.choice(location_ids)
        gl_rows.append((je_id, acc_debit[0],  acc_debit[1],  acc_debit[2],  amount, Decimal("0"), lid, "", datetime.now()))
        gl_rows.append((je_id, acc_credit[0], acc_credit[1], acc_credit[2], Decimal("0"), amount, lid, "", datetime.now()))

    n = bulk_insert("finance_gl_postings",
        ["journal_id","account_id","account_code","account_name",
         "debit","credit","location_id","description","created_at"],
        gl_rows, batch=3000)
    ok(f"GL postings: {n:,}")

    # Budgets
    budget_rows = []
    budget_actual_rows = []
    CATEGORIES = ["revenue","cogs","payroll","rent","utilities","marketing",
                  "maintenance","supplies","depreciation","other_opex"]

    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            for lid in location_ids:
                for cat in CATEGORIES:
                    base = Decimal(str({
                        "revenue":   RNG.randint(50000000, 200000000),
                        "cogs":      RNG.randint(15000000, 70000000),
                        "payroll":   RNG.randint(20000000, 50000000),
                        "rent":      RNG.randint(5000000,  20000000),
                        "utilities": RNG.randint(2000000,  8000000),
                        "marketing": RNG.randint(1000000,  5000000),
                        "maintenance":RNG.randint(500000,  3000000),
                        "supplies":  RNG.randint(1000000,  5000000),
                        "depreciation":RNG.randint(500000, 2000000),
                        "other_opex":RNG.randint(500000,  3000000),
                    }[cat]))
                    budget_rows.append((
                        yr, mo, lid, cat, "", base,
                        "", admin_id, datetime.now()
                    ))

    n = bulk_insert("finance_budgets",
        ["budget_year","budget_month","location_id","category","account_code",
         "budget_amount","notes","created_by_id","created_at"],
        budget_rows, batch=3000,
        on_conflict="ON CONFLICT (budget_year, budget_month, location_id, category) DO NOTHING")
    ok(f"Budgets: {n:,}")

    # Budget actuals (realisasi)
    saved_budgets = q("SELECT id, budget_amount FROM finance_budgets ORDER BY id")
    for bid, budget_amt in saved_budgets:
        actual = Decimal(str(budget_amt)) * Decimal(str(round(RNG.uniform(0.7, 1.3), 2)))
        variance = actual - Decimal(str(budget_amt))
        var_pct  = (variance / Decimal(str(budget_amt)) * 100).quantize(Decimal("0.01")) \
                   if budget_amt else Decimal("0")
        budget_actual_rows.append((
            bid, actual.quantize(Decimal("0.01")),
            variance.quantize(Decimal("0.01")),
            var_pct, today
        ))

    n = bulk_insert("finance_budget_actuals",
        ["budget_id","actual_amount","variance_amount","variance_pct","as_of_date"],
        budget_actual_rows, batch=3000,
        on_conflict="ON CONFLICT (budget_id, as_of_date) DO NOTHING")
    ok(f"Budget actuals: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 14 — MAINTENANCE (Asset Registry, Work Orders)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_maintenance(dry_run=False):
    head("MODUL 14 — MAINTENANCE (Assets, Schedules, Work Orders, Spare Parts)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS maint_asset_registry (
            id              BIGSERIAL PRIMARY KEY,
            asset_code      VARCHAR(30) UNIQUE NOT NULL,
            asset_name      VARCHAR(150) NOT NULL,
            category        VARCHAR(40) NOT NULL DEFAULT 'equipment',
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            brand           VARCHAR(80) DEFAULT '',
            model           VARCHAR(80) DEFAULT '',
            serial_number   VARCHAR(80) DEFAULT '',
            purchase_date   DATE,
            purchase_price  NUMERIC(12,2) DEFAULT 0,
            depreciation_rate NUMERIC(5,2) DEFAULT 20.0,
            current_value   NUMERIC(12,2) DEFAULT 0,
            warranty_until  DATE,
            status          VARCHAR(20) DEFAULT 'active',
            last_service_date DATE,
            next_service_date DATE,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE maint_asset_registry IS
            'Inventaris aset per outpost: mesin espresso, grinder, kulkas, POS terminal, dll.';
        CREATE INDEX IF NOT EXISTS idx_asset_loc    ON maint_asset_registry(location_id);
        CREATE INDEX IF NOT EXISTS idx_asset_status ON maint_asset_registry(status);
        """, "maint_asset_registry"),

        ("""
        CREATE TABLE IF NOT EXISTS maint_work_orders (
            id              BIGSERIAL PRIMARY KEY,
            wo_number       VARCHAR(30) UNIQUE NOT NULL,
            asset_id        BIGINT REFERENCES maint_asset_registry(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            wo_type         VARCHAR(30) DEFAULT 'corrective',
            priority        VARCHAR(10) DEFAULT 'normal',
            title           VARCHAR(200) NOT NULL,
            description     TEXT DEFAULT '',
            reported_by_id  BIGINT REFERENCES auth_user(id),
            assigned_to_id  BIGINT REFERENCES auth_user(id),
            status          VARCHAR(20) DEFAULT 'open',
            reported_at     TIMESTAMPTZ DEFAULT NOW(),
            started_at      TIMESTAMPTZ,
            completed_at    TIMESTAMPTZ,
            estimated_hours NUMERIC(5,2) DEFAULT 0,
            actual_hours    NUMERIC(5,2) DEFAULT 0,
            parts_cost      NUMERIC(10,2) DEFAULT 0,
            labor_cost      NUMERIC(10,2) DEFAULT 0,
            total_cost      NUMERIC(12,2) DEFAULT 0,
            root_cause      TEXT DEFAULT '',
            resolution      TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE maint_work_orders IS
            'Work order perawatan/perbaikan. Type: preventive, corrective, emergency.';
        CREATE INDEX IF NOT EXISTS idx_wo_status ON maint_work_orders(status);
        CREATE INDEX IF NOT EXISTS idx_wo_asset  ON maint_work_orders(asset_id);
        CREATE INDEX IF NOT EXISTS idx_wo_loc    ON maint_work_orders(location_id);
        """, "maint_work_orders"),

        ("""
        CREATE TABLE IF NOT EXISTS maint_spare_parts (
            id              BIGSERIAL PRIMARY KEY,
            part_code       VARCHAR(30) UNIQUE NOT NULL,
            part_name       VARCHAR(150) NOT NULL,
            compatible_with TEXT[] DEFAULT '{}',
            unit            VARCHAR(20) DEFAULT 'pcs',
            stock_qty       NUMERIC(10,2) DEFAULT 0,
            min_stock       NUMERIC(10,2) DEFAULT 1,
            unit_cost       NUMERIC(10,2) DEFAULT 0,
            supplier        VARCHAR(100) DEFAULT '',
            lead_time_days  INT DEFAULT 7,
            last_ordered_at DATE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE maint_spare_parts IS
            'Stok suku cadang untuk peralatan kafe: gasket, basket, blade grinder, dll.';
        """, "maint_spare_parts"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    # Assets per lokasi
    ASSETS = [
        ("espresso_machine", "Mesin Espresso",     ["La Marzocca","Synesso","Victoria Arduino"], 25000000, 50000000),
        ("grinder",          "Coffee Grinder",      ["Mahlkonig","Anfim","Eureka"],                5000000,  15000000),
        ("refrigerator",     "Kulkas Display",      ["Sharp","Samsung","Daikin"],                  4000000,  12000000),
        ("pos_terminal",     "POS Terminal",        ["Sunmi","Epson","iMin"],                      3000000,   8000000),
        ("water_purifier",   "Water Purifier",      ["Coway","3M","Panasonic"],                    2000000,   6000000),
        ("blender",          "Commercial Blender",  ["Vitamix","Blendtec"],                        3000000,   8000000),
        ("ice_maker",        "Ice Maker",           ["Hoshizaki","Ice-O-Matic"],                   8000000,  20000000),
        ("air_conditioner",  "AC",                  ["Daikin","Panasonic","Mitsubishi"],            5000000,  15000000),
    ]

    asset_rows = []
    asset_ctr  = 1
    for lid in location_ids:
        for cat, name, brands, min_price, max_price in ASSETS:
            # 1-2 unit per tipe per lokasi
            for unit in range(RNG.randint(1, 2)):
                purchase_date = today - timedelta(days=RNG.randint(30, 1800))
                purchase_price= Decimal(str(RNG.randint(min_price, max_price)))
                age_years     = (today - purchase_date).days / 365
                depr_rate     = Decimal("20.0")  # 20% per tahun
                curr_value    = max(Decimal("0"), purchase_price * (1 - depr_rate/100 * Decimal(str(age_years))))
                last_svc      = today - timedelta(days=RNG.randint(0, 90))
                next_svc      = last_svc + timedelta(days=90)
                asset_rows.append((
                    f"ASSET-{lid:03d}-{asset_ctr:04d}",
                    f"{name} #{unit+1} - Loc {lid}",
                    cat, lid,
                    RNG.choice(brands), f"Model-{RNG.randint(100,999)}",
                    f"SN{RNG.randint(100000000,999999999)}",
                    purchase_date, purchase_price.quantize(Decimal("0.01")),
                    depr_rate, curr_value.quantize(Decimal("0.01")),
                    purchase_date + timedelta(days=365*2),
                    "active", last_svc, next_svc, "",
                    purchase_date, purchase_date
                ))
                asset_ctr += 1

    log(f"Assets: {len(asset_rows)}")
    if dry_run:
        log(f"[DRY RUN] assets, work orders, spare parts")
        return

    n = bulk_insert("maint_asset_registry",
        ["asset_code","asset_name","category","location_id","brand","model",
         "serial_number","purchase_date","purchase_price","depreciation_rate",
         "current_value","warranty_until","status","last_service_date",
         "next_service_date","notes","created_at","updated_at"],
        asset_rows, on_conflict="ON CONFLICT (asset_code) DO NOTHING")
    ok(f"Assets: {n:,}")

    # Work Orders
    asset_ids = [r[0] for r in q("SELECT id, location_id FROM maint_asset_registry")]
    WO_TYPES  = ["preventive","preventive","corrective","corrective","emergency"]
    PRIORITIES= ["low","normal","normal","high","critical"]
    WO_TITLES = [
        "Servis rutin mesin espresso","Kalibrasi grinder","Pembersihan filter air",
        "AC tidak dingin","Mesin espresso bocor","Layar POS mati","Kulkas berembun",
        "Ice maker macet","Lampu display mati","Kebocoran pipa air",
    ]

    wo_rows = []
    wo_ctr  = 1
    for aid in asset_ids:
        n_wo = RNG.randint(1, 5)
        for _ in range(n_wo):
            wo_type    = RNG.choice(WO_TYPES)
            rep_date   = datetime.now() - timedelta(days=RNG.randint(0, 365))
            status     = RNG.choices(["open","in_progress","completed","completed"],
                                     weights=[15,15,35,35])[0]
            started_at = rep_date + timedelta(hours=RNG.randint(1, 24)) if status != "open" else None
            completed_at = started_at + timedelta(hours=RNG.randint(1, 72)) if status == "completed" else None
            est_h      = Decimal(str(RNG.uniform(0.5, 8)))
            act_h      = est_h * Decimal(str(RNG.uniform(0.5, 1.5))) if status == "completed" else Decimal("0")
            parts_cost = Decimal(str(RNG.randint(0, 500000)))
            labor_cost = Decimal(str(RNG.randint(50000, 300000)))
            wo_rows.append((
                f"WO-{today.year}-{wo_ctr:05d}",
                aid,
                RNG.choice(location_ids),
                wo_type, RNG.choice(PRIORITIES),
                RNG.choice(WO_TITLES), "",
                RNG.choice(user_ids) if user_ids else admin_id,
                RNG.choice(user_ids) if user_ids else admin_id,
                status, rep_date, started_at, completed_at,
                est_h.quantize(Decimal("0.01")),
                act_h.quantize(Decimal("0.01")),
                parts_cost, labor_cost,
                (parts_cost + labor_cost).quantize(Decimal("0.01")),
                "", "", rep_date
            ))
            wo_ctr += 1

    n = bulk_insert("maint_work_orders",
        ["wo_number","asset_id","location_id","wo_type","priority","title","description",
         "reported_by_id","assigned_to_id","status","reported_at","started_at","completed_at",
         "estimated_hours","actual_hours","parts_cost","labor_cost","total_cost",
         "root_cause","resolution","created_at"],
        wo_rows, on_conflict="ON CONFLICT (wo_number) DO NOTHING")
    ok(f"Work orders: {n:,}")

    # Spare Parts
    PARTS = [
        ("PART-GASKET-57MM",  "Group Gasket 57mm",    ["espresso_machine"],       "pcs", 20, 5,  15000),
        ("PART-BASKET-20G",   "Portafilter Basket 20g",["espresso_machine"],       "pcs", 10, 3,  45000),
        ("PART-BLADE-BURR",   "Burr Blade Set",        ["grinder"],                "set", 5,  2,  350000),
        ("PART-FILTER-WATER", "Filter Cartridge",      ["water_purifier"],         "pcs", 15, 5,  80000),
        ("PART-PUMP-EP",      "Pump Espresso 15bar",   ["espresso_machine"],       "pcs", 3,  1,  450000),
        ("PART-AC-FILTER",    "AC Filter Mesh",        ["air_conditioner"],        "pcs", 10, 4,  25000),
        ("PART-BLADE-ICE",    "Ice Maker Blade",       ["ice_maker"],              "pcs", 4,  2,  200000),
        ("PART-SCREEN-POS",   "POS Screen Protector",  ["pos_terminal"],           "pcs", 20, 5,  50000),
    ]
    part_rows = [(code, name, json.dumps(compat), unit,
                  RNG.randint(0, 30), min_s,
                  Decimal(str(cost)), "Toko Mesin Jakarta", 7,
                  today - timedelta(days=RNG.randint(10, 90)), datetime.now())
                 for code, name, compat, unit, _, min_s, cost in PARTS]

    n = bulk_insert("maint_spare_parts",
        ["part_code","part_name","compatible_with","unit","stock_qty","min_stock",
         "unit_cost","supplier","lead_time_days","last_ordered_at","created_at"],
        part_rows, on_conflict="ON CONFLICT (part_code) DO NOTHING")
    ok(f"Spare parts: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 15 — SUPPLY CHAIN ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

def fill_supply_chain(dry_run=False):
    head("MODUL 15 — SUPPLY CHAIN (Demand Forecast, Reorder Alerts, Supplier Scorecard)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS sc_demand_forecast (
            id              BIGSERIAL PRIMARY KEY,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            forecast_month  VARCHAR(7) NOT NULL,
            predicted_qty   NUMERIC(12,2) DEFAULT 0,
            actual_qty      NUMERIC(12,2),
            confidence_pct  NUMERIC(5,2) DEFAULT 80.0,
            method          VARCHAR(30) DEFAULT 'moving_average',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(variant_id, location_id, forecast_month)
        );
        COMMENT ON TABLE sc_demand_forecast IS
            'Prediksi kebutuhan bahan/produk per bulan. Method: moving_average, ml_model, manual.';
        CREATE INDEX IF NOT EXISTS idx_forecast_month ON sc_demand_forecast(forecast_month);
        """, "sc_demand_forecast"),

        ("""
        CREATE TABLE IF NOT EXISTS sc_reorder_alerts (
            id              BIGSERIAL PRIMARY KEY,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            current_stock   NUMERIC(12,2) DEFAULT 0,
            reorder_point   NUMERIC(12,2) DEFAULT 0,
            reorder_qty     NUMERIC(12,2) DEFAULT 0,
            days_of_stock   NUMERIC(6,2) DEFAULT 0,
            alert_level     VARCHAR(10) DEFAULT 'normal',
            suggested_po_date DATE,
            preferred_vendor_id BIGINT REFERENCES lumra_config_vendors(id),
            is_resolved     BOOLEAN DEFAULT FALSE,
            resolved_at     TIMESTAMPTZ,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sc_reorder_alerts IS
            'Alert otomatis ketika stok mendekati reorder point. Level: critical, warning, normal.';
        CREATE INDEX IF NOT EXISTS idx_reorder_alert ON sc_reorder_alerts(alert_level, is_resolved);
        """, "sc_reorder_alerts"),

        ("""
        CREATE TABLE IF NOT EXISTS sc_supplier_scorecards (
            id              BIGSERIAL PRIMARY KEY,
            vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
            period          VARCHAR(7) NOT NULL,
            on_time_delivery_pct NUMERIC(5,2) DEFAULT 0,
            quality_acceptance_pct NUMERIC(5,2) DEFAULT 0,
            price_competitiveness NUMERIC(5,2) DEFAULT 0,
            responsiveness_score  NUMERIC(5,2) DEFAULT 0,
            overall_score   NUMERIC(5,2) DEFAULT 0,
            total_orders    INT DEFAULT 0,
            total_value     NUMERIC(15,2) DEFAULT 0,
            issues_count    INT DEFAULT 0,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(vendor_id, period)
        );
        COMMENT ON TABLE sc_supplier_scorecards IS
            'Penilaian performa supplier per bulan: ketepatan delivery, kualitas, harga.';
        CREATE INDEX IF NOT EXISTS idx_scorecard_vendor ON sc_supplier_scorecards(vendor_id);
        CREATE INDEX IF NOT EXISTS idx_scorecard_period ON sc_supplier_scorecards(period DESC);
        """, "sc_supplier_scorecards"),

        ("""
        CREATE TABLE IF NOT EXISTS sc_lead_times (
            id              BIGSERIAL PRIMARY KEY,
            vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            avg_lead_days   NUMERIC(5,1) DEFAULT 0,
            min_lead_days   INT DEFAULT 0,
            max_lead_days   INT DEFAULT 0,
            sample_count    INT DEFAULT 0,
            last_updated    DATE DEFAULT CURRENT_DATE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(vendor_id, variant_id)
        );
        COMMENT ON TABLE sc_lead_times IS
            'Lead time rata-rata per vendor × produk. Basis perhitungan reorder point.';
        """, "sc_lead_times"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    variant_ids  = CTX["variant_ids"]
    location_ids = CTX["location_ids"]
    vendor_ids   = CTX["vendor_ids"]

    # Demand Forecast
    fc_rows = []
    for vid in RNG.sample(variant_ids, min(300, len(variant_ids))):
        for lid in location_ids:
            for mo_offset in range(-6, 3):
                ref = today.replace(day=1) + timedelta(days=mo_offset * 31)
                ref = ref.replace(day=1)
                period     = ref.strftime("%Y-%m")
                predicted  = Decimal(str(RNG.randint(50, 500)))
                actual     = Decimal(str(int(predicted * Decimal(str(RNG.uniform(0.7, 1.3)))))) \
                             if mo_offset < 0 else None
                confidence = Decimal(str(round(RNG.uniform(65, 95), 1)))
                method     = RNG.choice(["moving_average","moving_average","ets_model","manual"])
                fc_rows.append((
                    vid, lid, period, predicted,
                    actual, confidence, method, datetime.now()
                ))

    log(f"Demand forecasts: {len(fc_rows)}")
    if dry_run:
        log(f"[DRY RUN] forecasts, reorder alerts, scorecards, lead times")
        return

    n = bulk_insert("sc_demand_forecast",
        ["variant_id","location_id","forecast_month","predicted_qty","actual_qty",
         "confidence_pct","method","created_at"],
        fc_rows, batch=3000,
        on_conflict="ON CONFLICT (variant_id, location_id, forecast_month) DO NOTHING")
    ok(f"Demand forecasts: {n:,}")

    # Reorder Alerts (dari stock yang rendah)
    stock_data = q("""
        SELECT s.variant_id, s.location_id, s.quantity,
               COALESCE(p.min_stock, 10) AS reorder_point
        FROM lumra_config_stock s
        JOIN lumra_config_productvariants pv ON pv.id = s.variant_id
        JOIN lumra_config_products p ON p.id = pv.product_id
        WHERE s.quantity < COALESCE(p.min_stock, 10) * 2
        LIMIT 2000
    """)

    alert_rows = []
    for vid, lid, curr_stock, reorder_pt in stock_data:
        curr = Decimal(str(curr_stock or 0))
        rp   = Decimal(str(reorder_pt or 10))
        days = float(curr) / max(1, RNG.uniform(1, 10))
        level = "critical" if curr <= rp * Decimal("0.5") else \
                "warning"  if curr <= rp else "normal"
        vendor_id = RNG.choice(vendor_ids) if vendor_ids else None
        alert_rows.append((
            vid, lid, curr.quantize(Decimal("0.01")),
            rp.quantize(Decimal("0.01")),
            (rp * 3).quantize(Decimal("0.01")),
            round(days, 1), level,
            today + timedelta(days=max(0, int(days) - 3)),
            vendor_id, False, None, datetime.now()
        ))

    n = bulk_insert("sc_reorder_alerts",
        ["variant_id","location_id","current_stock","reorder_point","reorder_qty",
         "days_of_stock","alert_level","suggested_po_date","preferred_vendor_id",
         "is_resolved","resolved_at","created_at"],
        alert_rows, batch=3000)
    ok(f"Reorder alerts: {n:,}")

    # Supplier Scorecards
    sc_rows = []
    for vid in vendor_ids:
        for mo_offset in range(-12, 0):
            ref = today.replace(day=1) + timedelta(days=mo_offset * 31)
            period = ref.replace(day=1).strftime("%Y-%m")
            otd    = round(RNG.uniform(70, 99), 1)
            qual   = round(RNG.uniform(80, 100), 1)
            price  = round(RNG.uniform(60, 95), 1)
            resp   = round(RNG.uniform(70, 100), 1)
            overall= round((otd * 0.3 + qual * 0.3 + price * 0.2 + resp * 0.2), 1)
            sc_rows.append((
                vid, period, otd, qual, price, resp, overall,
                RNG.randint(5, 50),
                Decimal(str(RNG.randint(5000000, 100000000))),
                RNG.randint(0, 5), "", datetime.now()
            ))

    n = bulk_insert("sc_supplier_scorecards",
        ["vendor_id","period","on_time_delivery_pct","quality_acceptance_pct",
         "price_competitiveness","responsiveness_score","overall_score",
         "total_orders","total_value","issues_count","notes","created_at"],
        sc_rows, on_conflict="ON CONFLICT (vendor_id, period) DO NOTHING")
    ok(f"Supplier scorecards: {n:,}")

    # Lead Times
    lt_rows = []
    for vid in RNG.sample(vendor_ids, min(20, len(vendor_ids))):
        for var_id in RNG.sample(variant_ids, min(30, len(variant_ids))):
            avg_ld = round(RNG.uniform(1, 14), 1)
            lt_rows.append((
                vid, var_id, avg_ld,
                max(1, int(avg_ld - 2)),
                int(avg_ld + 3),
                RNG.randint(3, 20),
                today - timedelta(days=RNG.randint(0, 30)),
                datetime.now()
            ))

    n = bulk_insert("sc_lead_times",
        ["vendor_id","variant_id","avg_lead_days","min_lead_days","max_lead_days",
         "sample_count","last_updated","created_at"],
        lt_rows, on_conflict="ON CONFLICT (vendor_id, variant_id) DO NOTHING")
    ok(f"Lead times: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 16 — NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def fill_notifications(dry_run=False):
    head("MODUL 16 — NOTIFICATIONS (Templates, Logs, Preferences)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS notif_templates (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(40) UNIQUE NOT NULL,
            name            VARCHAR(120) NOT NULL,
            channel         VARCHAR(20) NOT NULL DEFAULT 'push',
            event_trigger   VARCHAR(60) NOT NULL,
            title_template  VARCHAR(200) NOT NULL DEFAULT '',
            body_template   TEXT NOT NULL DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE notif_templates IS
            'Template notifikasi untuk berbagai event. Channel: push, email, sms, whatsapp.';
        """, "notif_templates"),

        ("""
        CREATE TABLE IF NOT EXISTS notif_log (
            id              BIGSERIAL PRIMARY KEY,
            template_id     BIGINT REFERENCES notif_templates(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            user_id         BIGINT REFERENCES auth_user(id),
            channel         VARCHAR(20) NOT NULL DEFAULT 'push',
            recipient       VARCHAR(150) NOT NULL DEFAULT '',
            title           VARCHAR(200) DEFAULT '',
            body            TEXT DEFAULT '',
            status          VARCHAR(20) DEFAULT 'sent',
            sent_at         TIMESTAMPTZ DEFAULT NOW(),
            opened_at       TIMESTAMPTZ,
            clicked_at      TIMESTAMPTZ,
            error_message   TEXT DEFAULT ''
        );
        COMMENT ON TABLE notif_log IS
            'Log pengiriman notifikasi. Status: queued, sent, delivered, opened, failed.';
        CREATE INDEX IF NOT EXISTS idx_notif_log_cust   ON notif_log(customer_id);
        CREATE INDEX IF NOT EXISTS idx_notif_log_status ON notif_log(status);
        CREATE INDEX IF NOT EXISTS idx_notif_log_date   ON notif_log(sent_at DESC);
        """, "notif_log"),

        ("""
        CREATE TABLE IF NOT EXISTS notif_preferences (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT NOT NULL UNIQUE REFERENCES lumra_config_customers(id),
            push_enabled    BOOLEAN DEFAULT TRUE,
            email_enabled   BOOLEAN DEFAULT TRUE,
            sms_enabled     BOOLEAN DEFAULT FALSE,
            whatsapp_enabled BOOLEAN DEFAULT TRUE,
            promo_notif     BOOLEAN DEFAULT TRUE,
            order_notif     BOOLEAN DEFAULT TRUE,
            loyalty_notif   BOOLEAN DEFAULT TRUE,
            news_notif      BOOLEAN DEFAULT FALSE,
            quiet_hours_start SMALLINT DEFAULT 22,
            quiet_hours_end   SMALLINT DEFAULT 7,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE notif_preferences IS
            'Preferensi notifikasi per customer. Quiet hours = jam tidak boleh kirim notif.';
        """, "notif_preferences"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Templates
    templates_data = [
        ("ORDER_CONFIRM",   "Order Confirmation",       "push",      "order.completed",
         "Pesanan #{order_id} dikonfirmasi!",
         "Pesananmu di {location_name} sedang disiapkan. Estimasi {eta} menit. ☕"),
        ("STAMP_EARNED",    "Stamp Earned",             "push",      "stamp.earned",
         "Kamu dapat {n} stamp baru! 🎯",
         "Total stampmu sekarang {total_stamps}. Butuh {remaining} lagi untuk reward gratis!"),
        ("REWARD_READY",    "Reward Siap Diredeem",     "push",      "reward.available",
         "Reward-mu sudah bisa diredeem! 🎁",
         "Kamu punya reward '{reward_name}' yang siap digunakan. Berlaku hingga {expires}."),
        ("TIER_UPGRADE",    "Naik Tier!",               "push",      "loyalty.tier_upgrade",
         "Selamat! Kamu naik ke tier {tier_name}! 🏆",
         "Nikmati keuntungan baru: {perks}. Terima kasih sudah setia bersama Kafe Nusantara!"),
        ("BIRTHDAY",        "Happy Birthday!",          "push",      "customer.birthday",
         "Selamat Ulang Tahun! 🎂",
         "Hadiah spesial dari Kafe Nusantara: diskon 20% hari ini. Kunjungi outpost terdekat!"),
        ("PROMO_FLASH",     "Flash Promo",              "push",      "promo.flash",
         "Flash Promo hari ini! ⚡",
         "{promo_name} — hanya {duration} jam! Gunakan kode {code}. Jangan sampai kehabisan!"),
        ("NPS_SURVEY",      "Quick Survey",             "push",      "nps.survey_request",
         "Bagaimana pengalamanmu? 📋",
         "Bantu kami jadi lebih baik. Survey singkat 30 detik untuk kunjunganmu di {location}."),
        ("LOW_STOCK_WARN",  "Low Stock Alert",          "email",     "stock.low",
         "[ALERT] Stok {product_name} menipis di {location}",
         "Stok tersisa: {qty} unit. Reorder point: {reorder_pt}. Segera buat PO."),
        ("PAYROLL_SLIP",    "Slip Gaji",                "email",     "payroll.processed",
         "Slip Gaji {period} sudah tersedia",
         "Slip gaji periode {period} sudah bisa dilihat di sistem. Gaji akan ditransfer pada {pay_date}."),
        ("WO_ASSIGNED",     "Work Order Assigned",      "push",      "wo.assigned",
         "Work Order #{wo_number} ditugaskan",
         "Kamu mendapat tugas WO: {title}. Prioritas: {priority}. Cek detail di aplikasi."),
        ("BIRTHDAY_STAFF",  "Birthday Staff",           "push",      "employee.birthday",
         "Ulang Tahun {name}! 🎂",
         "Jangan lupa ucapkan selamat ulang tahun kepada {name} hari ini!"),
        ("SEASONAL_MENU",   "Menu Seasonal Baru",       "push",      "menu.seasonal_launch",
         "Menu Seasonal Baru Sudah Tersedia! 🍵",
         "Coba '{menu_name}' — racikan terbaru dari barista kami. Terbatas selama {duration}!"),
    ]
    tmpl_rows = [(code, name, channel, trigger, title, body, True, datetime.now())
                 for code, name, channel, trigger, title, body in templates_data]

    if dry_run:
        log(f"[DRY RUN] {len(tmpl_rows)} templates + notification logs + preferences")
        return

    n = bulk_insert("notif_templates",
        ["code","name","channel","event_trigger","title_template",
         "body_template","is_active","created_at"],
        tmpl_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Notification templates: {n}")

    # Notification Log
    tmpl_ids     = [r[0] for r in q("SELECT id, channel FROM notif_templates")]
    customer_ids = CTX["customer_ids"]

    notif_rows = []
    for _ in range(50000):
        tmpl = RNG.choice(tmpl_ids)
        cid  = RNG.choice(customer_ids)
        sent = datetime.now() - timedelta(days=RNG.randint(0, 365),
                                          hours=RNG.randint(0, 23))
        status  = RNG.choices(["sent","delivered","opened","failed"],
                               weights=[20, 40, 35, 5])[0]
        opened  = sent + timedelta(minutes=RNG.randint(1, 120)) \
                  if status in ("opened",) else None
        clicked = opened + timedelta(seconds=RNG.randint(5, 60)) \
                  if opened and RNG.random() < 0.4 else None
        notif_rows.append((
            tmpl, cid, None, "push",
            f"customer_{cid}@example.com",
            "Notifikasi Kafe Nusantara", "",
            status, sent, opened, clicked, ""
        ))

    n = bulk_insert("notif_log",
        ["template_id","customer_id","user_id","channel","recipient",
         "title","body","status","sent_at","opened_at","clicked_at","error_message"],
        notif_rows, batch=3000)
    ok(f"Notification logs: {n:,}")

    # Preferences
    pref_rows = []
    for cid in customer_ids:
        pref_rows.append((
            cid,
            RNG.random() < 0.9, RNG.random() < 0.7,
            RNG.random() < 0.3, RNG.random() < 0.8,
            RNG.random() < 0.8, True, True,
            RNG.random() < 0.4,
            22, 7,
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("notif_preferences",
        ["customer_id","push_enabled","email_enabled","sms_enabled","whatsapp_enabled",
         "promo_notif","order_notif","loyalty_notif","news_notif",
         "quiet_hours_start","quiet_hours_end","created_at","updated_at"],
        pref_rows,
        on_conflict="ON CONFLICT (customer_id) DO NOTHING")
    ok(f"Notification preferences: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 17 — MENU ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════

def fill_menu_engineering(dry_run=False):
    head("MODUL 17 — MENU ENGINEERING (Modifiers, Combos, Performance, A/B Tests)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS menu_modifier_groups (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            selection_type  VARCHAR(20) DEFAULT 'single',
            min_select      INT DEFAULT 0,
            max_select      INT DEFAULT 1,
            is_required     BOOLEAN DEFAULT FALSE,
            is_active       BOOLEAN DEFAULT TRUE,
            sort_order      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_modifier_groups IS
            'Grup modifikasi menu: ukuran, suhu, gula, extra shot, topping, dll.';
        """, "menu_modifier_groups"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_modifiers (
            id              BIGSERIAL PRIMARY KEY,
            group_id        BIGINT NOT NULL REFERENCES menu_modifier_groups(id),
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            price_delta     NUMERIC(10,2) DEFAULT 0,
            is_active       BOOLEAN DEFAULT TRUE,
            sort_order      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_modifiers IS
            'Opsi modifikasi: Small/Medium/Large, Hot/Iced, Less/Normal/Extra Sugar, dll.';
        """, "menu_modifiers"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_combos (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(150) NOT NULL,
            description     TEXT DEFAULT '',
            combo_price     NUMERIC(12,2) NOT NULL,
            regular_price   NUMERIC(12,2) DEFAULT 0,
            discount_amount NUMERIC(10,2) DEFAULT 0,
            is_active       BOOLEAN DEFAULT TRUE,
            valid_from      DATE,
            valid_until     DATE,
            applicable_session VARCHAR(20) DEFAULT 'all',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_combos IS
            'Paket bundle menu: Morning Set, Afternoon Deal, dll.';
        """, "menu_combos"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_combo_items (
            id              BIGSERIAL PRIMARY KEY,
            combo_id        BIGINT NOT NULL REFERENCES menu_combos(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            quantity        INT DEFAULT 1,
            is_swappable    BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_combo_items IS 'Item-item yang masuk dalam satu paket combo.';
        """, "menu_combo_items"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_item_performance (
            id              BIGSERIAL PRIMARY KEY,
            variant_id      BIGINT NOT NULL REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            period          VARCHAR(7) NOT NULL,
            qty_sold        NUMERIC(12,2) DEFAULT 0,
            revenue         NUMERIC(15,2) DEFAULT 0,
            contribution_margin NUMERIC(15,2) DEFAULT 0,
            menu_mix_pct    NUMERIC(6,3) DEFAULT 0,
            category        VARCHAR(20) DEFAULT 'plowhorse',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(variant_id, location_id, period)
        );
        COMMENT ON TABLE menu_item_performance IS
            'Matrix menu engineering per item per bulan. '
            'Category: star (high pop + high margin), plowhorse (high pop + low margin), '
            'puzzle (low pop + high margin), dog (low pop + low margin).';
        CREATE INDEX IF NOT EXISTS idx_menu_perf_period ON menu_item_performance(period DESC);
        CREATE INDEX IF NOT EXISTS idx_menu_perf_cat    ON menu_item_performance(category);
        """, "menu_item_performance"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_ab_tests (
            id              BIGSERIAL PRIMARY KEY,
            test_code       VARCHAR(30) UNIQUE NOT NULL,
            test_name       VARCHAR(150) NOT NULL,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            test_type       VARCHAR(30) DEFAULT 'price',
            control_value   JSONB NOT NULL DEFAULT '{}',
            variant_value   JSONB NOT NULL DEFAULT '{}',
            start_date      DATE NOT NULL,
            end_date        DATE,
            location_ids    BIGINT[] DEFAULT '{}',
            control_orders  INT DEFAULT 0,
            variant_orders  INT DEFAULT 0,
            control_revenue NUMERIC(15,2) DEFAULT 0,
            variant_revenue NUMERIC(15,2) DEFAULT 0,
            winner          VARCHAR(10) DEFAULT 'pending',
            status          VARCHAR(20) DEFAULT 'running',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_ab_tests IS
            'A/B testing harga, nama, deskripsi menu. Winner: control, variant, inconclusive, pending.';
        """, "menu_ab_tests"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    variant_ids  = CTX["variant_ids"]
    location_ids = CTX["location_ids"]

    # Modifier Groups + Modifiers
    modifier_groups = [
        ("SIZE",       "Ukuran",       "single", 1, 1, True,  [
            ("SIZE-S",  "Small",   0),
            ("SIZE-M",  "Medium",  5000),
            ("SIZE-L",  "Large",   10000),
        ]),
        ("TEMP",       "Suhu",         "single", 1, 1, True,  [
            ("TEMP-HOT","Hot",     0),
            ("TEMP-ICE","Iced",    3000),
        ]),
        ("SUGAR",      "Tingkat Gula", "single", 0, 1, False, [
            ("SUGAR-0",  "No Sugar",     0),
            ("SUGAR-50", "Less Sweet",   0),
            ("SUGAR-100","Normal Sweet", 0),
            ("SUGAR-150","Extra Sweet",  0),
        ]),
        ("MILK",       "Jenis Susu",   "single", 0, 1, False, [
            ("MILK-REG", "Regular Milk",  0),
            ("MILK-OAT", "Oat Milk",    8000),
            ("MILK-ALM", "Almond Milk", 8000),
            ("MILK-SOY", "Soy Milk",    5000),
        ]),
        ("EXTRA",      "Tambahan",     "multi",  0, 3, False, [
            ("EXTRA-SHOT","Extra Shot", 8000),
            ("EXTRA-SYR", "Extra Syrup",3000),
            ("EXTRA-COLD","Extra Ice",  0),
            ("EXTRA-CHOC","Choco Drizzle",5000),
        ]),
        ("FOOD-TEMP",  "Kondisi",      "single", 0, 1, False, [
            ("FOOD-WARM","Dihangatkan",  0),
            ("FOOD-ROOM","Room Temp",   0),
        ]),
    ]

    mg_rows  = []
    mod_rows = []
    for code, name, sel_type, mn, mx, req, mods in modifier_groups:
        mg_rows.append((code, name, sel_type, mn, mx, req, True, len(mg_rows), datetime.now()))
        for mcode, mname, delta in mods:
            mod_rows.append((None, mcode, mname, Decimal(str(delta)), True, len(mod_rows), datetime.now()))

    if dry_run:
        log(f"[DRY RUN] modifier groups, combos, menu performance, A/B tests")
        return

    n = bulk_insert("menu_modifier_groups",
        ["code","name","selection_type","min_select","max_select",
         "is_required","is_active","sort_order","created_at"],
        mg_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Modifier groups: {n}")

    # Link modifiers ke groups
    saved_mgs = q("SELECT id, code FROM menu_modifier_groups ORDER BY id")
    mg_code_map = {row[1]: row[0] for row in saved_mgs}
    mod_rows_linked = []
    for code, name, sel_type, mn, mx, req, mods in modifier_groups:
        gid = mg_code_map.get(code)
        if not gid: continue
        for i, (mcode, mname, delta) in enumerate(mods):
            mod_rows_linked.append((gid, mcode, mname, Decimal(str(delta)), True, i, datetime.now()))

    n = bulk_insert("menu_modifiers",
        ["group_id","code","name","price_delta","is_active","sort_order","created_at"],
        mod_rows_linked, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Modifiers: {n}")

    # Combos
    SESSIONS = ["all","first_light","midday_transit","twilight_bivouac"]
    combo_rows = []
    combo_item_rows = []
    for i in range(20):
        code  = f"COMBO-{i+1:03d}"
        price = Decimal(str(RNG.randint(35000, 120000)))
        reg   = price + Decimal(str(RNG.randint(5000, 20000)))
        combo_rows.append((
            code, f"Paket Hemat #{i+1}", "",
            price, reg, reg - price, True,
            today - timedelta(days=RNG.randint(30, 180)),
            today + timedelta(days=RNG.randint(30, 180)),
            RNG.choice(SESSIONS), datetime.now()
        ))

    n = bulk_insert("menu_combos",
        ["code","name","description","combo_price","regular_price","discount_amount",
         "is_active","valid_from","valid_until","applicable_session","created_at"],
        combo_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Combos: {n}")

    # Combo Items
    saved_combos = q("SELECT id FROM menu_combos ORDER BY id")
    for (combo_id,) in saved_combos:
        n_items = RNG.randint(2, 3)
        for var_id in RNG.sample(variant_ids, min(n_items, len(variant_ids))):
            combo_item_rows.append((combo_id, var_id, 1, False, datetime.now()))
    existing_combo_items = set(q("SELECT combo_id, variant_id FROM menu_combo_items"))
    combo_item_rows = [
        row for row in combo_item_rows
        if (row[0], row[1]) not in existing_combo_items
    ]

    n = bulk_insert("menu_combo_items",
        ["combo_id","variant_id","quantity","is_swappable","created_at"],
        combo_item_rows)
    ok(f"Combo items: {n}")

    # Menu Item Performance (matrix engineering)
    me_rows = []
    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            if date(yr, mo, 1) > today: break
            period = f"{yr}-{mo:02d}"
            for vid in RNG.sample(variant_ids, min(50, len(variant_ids))):
                for lid in location_ids:
                    qty     = Decimal(str(RNG.randint(10, 500)))
                    price   = Decimal(str(RNG.randint(20000, 80000)))
                    cogs    = price * Decimal(str(round(RNG.uniform(0.25, 0.50), 2)))
                    rev     = qty * price
                    contrib = qty * (price - cogs)
                    mix_pct = round(RNG.uniform(0.001, 0.15), 3)
                    # Matrix: star/plowhorse/puzzle/dog
                    high_pop = mix_pct > 0.05
                    high_mg  = (price - cogs) / price > Decimal("0.55")
                    cat = ("star" if high_pop and high_mg else
                           "plowhorse" if high_pop else
                           "puzzle" if high_mg else "dog")
                    me_rows.append((
                        vid, lid, period, qty, rev.quantize(Decimal("0.01")),
                        contrib.quantize(Decimal("0.01")), mix_pct, cat, datetime.now()
                    ))

    n = bulk_insert("menu_item_performance",
        ["variant_id","location_id","period","qty_sold","revenue",
         "contribution_margin","menu_mix_pct","category","created_at"],
        me_rows, batch=3000,
        on_conflict="ON CONFLICT (variant_id, location_id, period) DO NOTHING")
    ok(f"Menu performance: {n:,}")

    # A/B Tests
    ab_rows = []
    for i in range(15):
        vid = RNG.choice(variant_ids)
        test_type = RNG.choice(["price","name","description","image"])
        old_price  = RNG.randint(25000, 80000)
        new_price  = old_price + RNG.randint(-5000, 10000)
        start = today - timedelta(days=RNG.randint(14, 90))
        end   = start + timedelta(days=RNG.randint(14, 30))
        status= "completed" if end < today else "running"
        ctrl_ord = RNG.randint(100, 1000)
        var_ord  = RNG.randint(80, 1100)
        winner = ("variant" if var_ord > ctrl_ord * 1.05 else
                  "control" if ctrl_ord > var_ord * 1.05 else
                  "inconclusive") if status == "completed" else "pending"
        ab_rows.append((
            f"AB-{i+1:03d}", f"A/B Test #{i+1} - {test_type.title()}",
            vid, test_type,
            json.dumps({"price": old_price}),
            json.dumps({"price": new_price}),
            start, end,
            [RNG.choice(location_ids) for _ in range(RNG.randint(1, 3))],
            ctrl_ord, var_ord,
            Decimal(str(ctrl_ord * old_price)),
            Decimal(str(var_ord * new_price)),
            winner, status, "", datetime.now()
        ))

    n = bulk_insert("menu_ab_tests",
        ["test_code","test_name","variant_id","test_type","control_value","variant_value",
         "start_date","end_date","location_ids","control_orders","variant_orders",
         "control_revenue","variant_revenue","winner","status","notes","created_at"],
        ab_rows, on_conflict="ON CONFLICT (test_code) DO NOTHING")
    ok(f"A/B Tests: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 18 — WASTE & COSTING
# ═══════════════════════════════════════════════════════════════════════════════

def fill_waste_costing(dry_run=False):
    head("MODUL 18 — WASTE & COSTING (Categories, Logs, Cost Summary, Root Cause)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS waste_categories (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(80) NOT NULL,
            waste_type      VARCHAR(30) DEFAULT 'production',
            description     TEXT DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE waste_categories IS
            'Kategori waste: spoilage, over_production, spill, expired, trim.';
        """, "waste_categories"),

        ("""
        CREATE TABLE IF NOT EXISTS waste_logs (
            id              BIGSERIAL PRIMARY KEY,
            category_id     BIGINT NOT NULL REFERENCES waste_categories(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
            waste_date      DATE NOT NULL,
            shift_type      VARCHAR(20) DEFAULT 'first_light',
            quantity        NUMERIC(10,3) NOT NULL,
            unit            VARCHAR(20) DEFAULT 'gram',
            unit_cost       NUMERIC(10,2) DEFAULT 0,
            total_cost      NUMERIC(12,2) DEFAULT 0,
            root_cause_tag  VARCHAR(50) DEFAULT '',
            description     TEXT DEFAULT '',
            recorded_by_id  BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE waste_logs IS
            'Log waste harian per shift. Diisi oleh supervisor shift.';
        CREATE INDEX IF NOT EXISTS idx_waste_date ON waste_logs(waste_date DESC);
        CREATE INDEX IF NOT EXISTS idx_waste_loc  ON waste_logs(location_id);
        CREATE INDEX IF NOT EXISTS idx_waste_cat  ON waste_logs(category_id);
        """, "waste_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS waste_daily_summary (
            id              BIGSERIAL PRIMARY KEY,
            summary_date    DATE NOT NULL,
            location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
            total_waste_qty NUMERIC(12,3) DEFAULT 0,
            total_waste_cost NUMERIC(12,2) DEFAULT 0,
            waste_pct_of_cogs NUMERIC(6,3) DEFAULT 0,
            top_category    VARCHAR(20) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(summary_date, location_id)
        );
        COMMENT ON TABLE waste_daily_summary IS
            'Ringkasan waste harian per outpost. Benchmark: waste < 3%% dari COGS.';
        CREATE INDEX IF NOT EXISTS idx_waste_sum_date ON waste_daily_summary(summary_date DESC);
        """, "waste_daily_summary"),

        ("""
        CREATE TABLE IF NOT EXISTS waste_root_cause_analysis (
            id              BIGSERIAL PRIMARY KEY,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            period          VARCHAR(7) NOT NULL,
            primary_cause   VARCHAR(80) NOT NULL,
            occurrence_count INT DEFAULT 0,
            total_cost_impact NUMERIC(12,2) DEFAULT 0,
            corrective_action TEXT DEFAULT '',
            status          VARCHAR(20) DEFAULT 'open',
            due_date        DATE,
            closed_at       DATE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE waste_root_cause_analysis IS
            'Analisis akar penyebab waste per periode lokasi. Action plan dan tracking.';
        """, "waste_root_cause_analysis"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    variant_ids  = CTX["variant_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]
    min_date     = CTX["min_date"]

    # Categories
    cat_data = [
        ("SPOILAGE",    "Spoilage/Busuk",      "storage",    "Bahan baku yang busuk sebelum dipakai."),
        ("OVER_PROD",   "Over Production",     "production", "Produksi berlebih yang tidak terjual."),
        ("SPILL",       "Spill/Tumpah",        "handling",   "Minuman/bahan yang tumpah saat penyiapan."),
        ("EXPIRED",     "Expired",             "storage",    "Produk melewati batas kadaluarsa."),
        ("TRIM",        "Trim/Sisa Potong",    "production", "Sisa bahan dari proses portioning."),
        ("RETURN",      "Customer Return",     "service",    "Produk yang dikembalikan customer."),
        ("QC_REJECT",   "QC Reject",           "quality",    "Produk tidak lolos quality check internal."),
        ("TRIAL_BATCH", "Trial/Recipe Test",   "production", "Bahan untuk uji coba resep baru."),
    ]
    cat_rows = [(code, name, wtype, desc, True, datetime.now())
                for code, name, wtype, desc in cat_data]

    if dry_run:
        log(f"[DRY RUN] waste categories, logs, summaries, RCA")
        return

    n = bulk_insert("waste_categories",
        ["code","name","waste_type","description","is_active","created_at"],
        cat_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Waste categories: {n}")

    # Waste Logs
    cat_ids    = [r[0] for r in q("SELECT id FROM waste_categories ORDER BY id")]
    SHIFTS     = ["first_light","midday_transit","twilight_bivouac"]
    ROOT_CAUSES= ["improper_storage","over_ordering","skill_gap","equipment_failure",
                  "expired_ingredient","customer_complaint","recipe_error","spill_accident"]
    UNITS      = ["gram","ml","pcs","liter","kg"]

    waste_rows = []
    days_range = (today - min_date).days
    for _ in range(20000):
        waste_date = min_date + timedelta(days=RNG.randint(0, days_range))
        qty   = Decimal(str(round(RNG.uniform(10, 500), 1)))
        cost  = Decimal(str(RNG.randint(500, 50000)))
        waste_rows.append((
            RNG.choice(cat_ids),
            RNG.choice(variant_ids),
            RNG.choice(location_ids),
            waste_date, RNG.choice(SHIFTS),
            qty, RNG.choice(UNITS),
            cost, qty * cost / 1000,
            RNG.choice(ROOT_CAUSES), "",
            RNG.choice(user_ids) if user_ids else admin_id,
            datetime.combine(waste_date, dtime(RNG.randint(7,22), 0))
        ))

    n = bulk_insert("waste_logs",
        ["category_id","variant_id","location_id","waste_date","shift_type",
         "quantity","unit","unit_cost","total_cost","root_cause_tag","description",
         "recorded_by_id","created_at"],
        waste_rows, batch=3000)
    ok(f"Waste logs: {n:,}")

    # Daily Summary (aggregate dari waste_logs per date × location)
    summary_raw = q("""
        SELECT waste_date, location_id,
               SUM(quantity) AS qty,
               SUM(total_cost) AS cost
        FROM waste_logs
        GROUP BY waste_date, location_id
        ORDER BY waste_date
        LIMIT 50000
    """)

    # COGS dari sales_daily
    cogs_map = {}
    try:
        cogs_raw = q("SELECT report_date, COALESCE(total_revenue * 0.35, 0) FROM lumra_report_sales_daily")
        cogs_map = {r[0]: Decimal(str(r[1])) for r in cogs_raw}
    except: pass

    TOP_CATS = ["SPOILAGE","OVER_PROD","SPILL","EXPIRED"]
    sum_rows = []
    for waste_date, loc_id, qty, cost in summary_raw:
        cogs     = cogs_map.get(waste_date, Decimal("1000000"))
        waste_pct= (Decimal(str(cost)) / cogs * 100).quantize(Decimal("0.001")) \
                   if cogs > 0 else Decimal("0")
        sum_rows.append((
            waste_date, loc_id,
            Decimal(str(qty)).quantize(Decimal("0.001")),
            Decimal(str(cost)).quantize(Decimal("0.01")),
            waste_pct, RNG.choice(TOP_CATS), datetime.now()
        ))

    n = bulk_insert("waste_daily_summary",
        ["summary_date","location_id","total_waste_qty","total_waste_cost",
         "waste_pct_of_cogs","top_category","created_at"],
        sum_rows, batch=3000,
        on_conflict="ON CONFLICT (summary_date, location_id) DO NOTHING")
    ok(f"Waste daily summary: {n:,}")

    # Root Cause Analysis
    rca_rows = []
    ACTIONS = [
        "Review SOP penyimpanan bahan baku.",
        "Implementasi FIFO ketat untuk semua bahan.",
        "Training barista teknik portioning yang benar.",
        "Kalibrasi equipment setiap awal shift.",
        "Review par level dan reduce ordering quantity.",
        "Pasang checklist suhu kulkas harian.",
    ]
    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            if date(yr, mo, 1) > today: break
            period = f"{yr}-{mo:02d}"
            for lid in RNG.sample(location_ids, min(3, len(location_ids))):
                for cause in RNG.sample(ROOT_CAUSES, min(3, len(ROOT_CAUSES))):
                    due = date(yr, mo, 1) + timedelta(days=30)
                    status = "closed" if due < today else "open"
                    rca_rows.append((
                        lid, period, cause,
                        RNG.randint(3, 30),
                        Decimal(str(RNG.randint(50000, 2000000))),
                        RNG.choice(ACTIONS),
                        status, due,
                        due if status == "closed" else None,
                        datetime.now()
                    ))

    n = bulk_insert("waste_root_cause_analysis",
        ["location_id","period","primary_cause","occurrence_count","total_cost_impact",
         "corrective_action","status","due_date","closed_at","created_at"],
        rca_rows)
    ok(f"Root cause analysis: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 19 — TRAINING & CERTIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def fill_training(dry_run=False):
    head("MODUL 19 — TRAINING (Courses, Enrollments, Assessments, Certifications)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS training_courses (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            title           VARCHAR(150) NOT NULL,
            description     TEXT DEFAULT '',
            category        VARCHAR(40) DEFAULT 'operations',
            level           VARCHAR(20) DEFAULT 'beginner',
            duration_hours  NUMERIC(5,1) DEFAULT 0,
            passing_score   SMALLINT DEFAULT 70,
            is_mandatory    BOOLEAN DEFAULT FALSE,
            valid_for_months INT DEFAULT 12,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE training_courses IS
            'Kursus pelatihan karyawan: barista skill, service excellence, food safety, leadership.';
        """, "training_courses"),

        ("""
        CREATE TABLE IF NOT EXISTS training_enrollments (
            id              BIGSERIAL PRIMARY KEY,
            course_id       BIGINT NOT NULL REFERENCES training_courses(id),
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            status          VARCHAR(20) DEFAULT 'enrolled',
            enrolled_at     TIMESTAMPTZ DEFAULT NOW(),
            started_at      TIMESTAMPTZ,
            completed_at    TIMESTAMPTZ,
            score           NUMERIC(5,2),
            passed          BOOLEAN,
            attempt_number  INT DEFAULT 1,
            notes           TEXT DEFAULT '',
            UNIQUE(course_id, employee_id, attempt_number)
        );
        COMMENT ON TABLE training_enrollments IS
            'Enrollment karyawan ke kursus. Bisa multi-attempt jika tidak lulus.';
        CREATE INDEX IF NOT EXISTS idx_enroll_emp    ON training_enrollments(employee_id);
        CREATE INDEX IF NOT EXISTS idx_enroll_status ON training_enrollments(status);
        """, "training_enrollments"),

        ("""
        CREATE TABLE IF NOT EXISTS training_certifications (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            course_id       BIGINT NOT NULL REFERENCES training_courses(id),
            cert_number     VARCHAR(50) UNIQUE NOT NULL,
            issued_date     DATE NOT NULL,
            expiry_date     DATE,
            is_valid        BOOLEAN DEFAULT TRUE,
            issued_by       VARCHAR(100) DEFAULT 'Kafe Nusantara Training Center',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE training_certifications IS
            'Sertifikasi karyawan yang lulus training. Auto-expire sesuai valid_for_months kursus.';
        CREATE INDEX IF NOT EXISTS idx_cert_emp ON training_certifications(employee_id);
        CREATE INDEX IF NOT EXISTS idx_cert_exp ON training_certifications(expiry_date);
        """, "training_certifications"),

        ("""
        CREATE TABLE IF NOT EXISTS training_skill_matrix (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            skill_name      VARCHAR(80) NOT NULL,
            skill_category  VARCHAR(40) DEFAULT 'technical',
            proficiency     SMALLINT DEFAULT 1 CHECK(proficiency BETWEEN 1 AND 5),
            assessed_at     DATE DEFAULT CURRENT_DATE,
            assessed_by_id  BIGINT REFERENCES hr_employees(id),
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(employee_id, skill_name)
        );
        COMMENT ON TABLE training_skill_matrix IS
            'Matriks skill per karyawan. Proficiency 1-5: 1=novice, 3=competent, 5=expert.';
        CREATE INDEX IF NOT EXISTS idx_skill_emp ON training_skill_matrix(employee_id);
        """, "training_skill_matrix"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Courses
    courses_data = [
        ("BARI-101",  "Espresso Fundamentals",           "barista",   "beginner",  8,  70,  True,  12),
        ("BARI-201",  "Manual Brewing Techniques",       "barista",   "intermediate",12,75, False, 12),
        ("BARI-301",  "Latte Art & Coffee Aesthetics",   "barista",   "intermediate",10,75, False, 12),
        ("BARI-401",  "Single Origin & Cupping",         "barista",   "advanced",  16, 80,  False, 24),
        ("SVC-101",   "Customer Service Excellence",     "service",   "beginner",  6,  75,  True,  12),
        ("SVC-201",   "Conflict Resolution",             "service",   "intermediate",4, 70, False, 12),
        ("FOOD-101",  "Food Safety & Hygiene (HACCP)",   "food_safety","beginner",  8,  80,  True,  6),
        ("FOOD-201",  "Allergen Awareness",              "food_safety","beginner",  4,  80,  True,  12),
        ("OPS-101",   "POS System & Cash Handling",      "operations","beginner",  6,  75,  True,  12),
        ("OPS-201",   "Inventory Management",            "operations","intermediate",8,70,  False, 12),
        ("OPS-301",   "Shift Management",                "operations","advanced",  12, 75,  False, 12),
        ("MGMT-101",  "Leadership Essentials",           "management","intermediate",16,75, False, 24),
        ("MGMT-201",  "Financial Literacy for Managers", "management","advanced",  12, 75,  False, 24),
        ("RECIPE-101","Signature Recipe Mastery",        "barista",   "intermediate",8, 80, True,  12),
        ("SAFE-101",  "Fire Safety & Emergency Proc.",   "safety",    "beginner",  4,  80,  True,  12),
    ]
    course_rows = [(code, title, "", cat, lvl,
                    Decimal(str(dur)), passing, mandatory, valid, True, datetime.now())
                   for code, title, cat, lvl, dur, passing, mandatory, valid in courses_data]

    if dry_run:
        log(f"[DRY RUN] courses, enrollments, certifications, skill matrix")
        return

    n = bulk_insert("training_courses",
        ["code","title","description","category","level","duration_hours",
         "passing_score","is_mandatory","valid_for_months","is_active","created_at"],
        course_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Courses: {n}")

    # Enrollments + Certifications
    course_data  = q("SELECT id, passing_score, valid_for_months FROM training_courses ORDER BY id")
    employee_ids = [r[0] for r in q("SELECT id FROM hr_employees ORDER BY id")]

    if not employee_ids or not course_data:
        warn("Tidak ada employee atau course — skip enrollment")
        return

    enroll_rows = []
    cert_rows   = []
    cert_ctr    = 1

    for emp_id in employee_ids:
        # Setiap karyawan ambil 3-8 kursus
        sampled_courses = RNG.sample(course_data, min(RNG.randint(3, 8), len(course_data)))
        for cid, passing_score, valid_months in sampled_courses:
            status = RNG.choices(
                ["completed","completed","in_progress","enrolled","failed"],
                weights=[50, 0, 20, 20, 10]
            )[0]
            enrolled_at  = datetime.now() - timedelta(days=RNG.randint(30, 730))
            started_at   = enrolled_at + timedelta(days=RNG.randint(0, 14)) \
                           if status != "enrolled" else None
            completed_at = started_at + timedelta(days=RNG.randint(1, 30)) \
                           if status in ("completed","failed") else None
            score = Decimal(str(round(RNG.uniform(50, 100), 1))) \
                    if status in ("completed","failed") else None
            passed = bool(score >= passing_score) if score else None

            enroll_rows.append((
                cid, emp_id, status,
                enrolled_at, started_at, completed_at,
                score, passed, 1, "", 
            ))

            if passed:
                issued = completed_at.date() if completed_at else today
                expiry = issued + timedelta(days=valid_months * 30)
                cert_rows.append((
                    emp_id, cid,
                    f"CERT-{emp_id:05d}-{cid:03d}-{cert_ctr:04d}",
                    issued, expiry, expiry >= today,
                    "Kafe Nusantara Training Center",
                    datetime.now()
                ))
                cert_ctr += 1

    n = bulk_insert("training_enrollments",
        ["course_id","employee_id","status","enrolled_at","started_at","completed_at",
         "score","passed","attempt_number","notes"],
        enroll_rows,
        on_conflict="ON CONFLICT (course_id, employee_id, attempt_number) DO NOTHING")
    ok(f"Enrollments: {n:,}")

    n = bulk_insert("training_certifications",
        ["employee_id","course_id","cert_number","issued_date","expiry_date",
         "is_valid","issued_by","created_at"],
        cert_rows, on_conflict="ON CONFLICT (cert_number) DO NOTHING")
    ok(f"Certifications: {n:,}")

    # Skill Matrix
    SKILLS = {
        "technical": ["Espresso Extraction","Milk Steaming","Manual Brewing","Latte Art",
                       "Coffee Cupping","Grinder Calibration","POS Operation","Inventory Count"],
        "service":   ["Customer Greeting","Order Taking","Complaint Handling","Upselling",
                       "Product Knowledge","Table Service"],
        "food_safety":["HACCP","Allergen Awareness","Temperature Control","Personal Hygiene"],
        "leadership":["Shift Briefing","Team Communication","Conflict Resolution","Performance Feedback"],
    }

    skill_rows = []
    for emp_id in employee_ids:
        for cat, skill_list in SKILLS.items():
            for skill in RNG.sample(skill_list, min(RNG.randint(2, 5), len(skill_list))):
                skill_rows.append((
                    emp_id, skill, cat,
                    RNG.randint(1, 5),
                    today - timedelta(days=RNG.randint(0, 365)),
                    None, "", datetime.now()
                ))

    n = bulk_insert("training_skill_matrix",
        ["employee_id","skill_name","skill_category","proficiency","assessed_at",
         "assessed_by_id","notes","created_at"],
        skill_rows,
        on_conflict="ON CONFLICT (employee_id, skill_name) DO UPDATE SET "
                    "proficiency=EXCLUDED.proficiency, assessed_at=EXCLUDED.assessed_at")
    ok(f"Skill matrix: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "hr":               fill_hr,
    "loyalty":          fill_loyalty,
    "customer_journey": fill_customer_journey,
    "finance_gl":       fill_finance_gl,
    "maintenance":      fill_maintenance,
    "supply_chain":     fill_supply_chain,
    "notifications":    fill_notifications,
    "menu_engineering": fill_menu_engineering,
    "waste_costing":    fill_waste_costing,
    "training":         fill_training,
}

ORDER = ["hr","loyalty","customer_journey","finance_gl","maintenance",
         "supply_chain","notifications","menu_engineering","waste_costing","training"]

NEW_TABLES = [
    # HR
    "hr_employees", "hr_work_schedules", "hr_attendance", "hr_payroll",
    # Loyalty
    "loyalty_tiers", "loyalty_stamp_cards", "loyalty_stamp_transactions",
    "loyalty_rewards", "loyalty_redemptions",
    # Customer Journey
    "cj_customer_sessions", "cj_touchpoints", "cj_feedback", "cj_nps_responses",
    # Finance GL
    "finance_journal_entries", "finance_gl_postings", "finance_budgets",
    "finance_budget_actuals", "finance_cost_centers",
    # Maintenance
    "maint_asset_registry", "maint_work_orders", "maint_spare_parts",
    # Supply Chain
    "sc_demand_forecast", "sc_reorder_alerts", "sc_supplier_scorecards", "sc_lead_times",
    # Notifications
    "notif_templates", "notif_log", "notif_preferences",
    # Menu Engineering
    "menu_modifier_groups", "menu_modifiers", "menu_combos", "menu_combo_items",
    "menu_item_performance", "menu_ab_tests",
    # Waste
    "waste_categories", "waste_logs", "waste_daily_summary", "waste_root_cause_analysis",
    # Training
    "training_courses", "training_enrollments", "training_certifications", "training_skill_matrix",
]

def main():
    t_total = time.time()
    print("\n" + "═"*70)
    print("  KAFE NUSANTARA — World Building Extension (seed_expansion2)")
    print("  10 modul baru: HR, Loyalty, CJ, Finance GL, Maintenance,")
    print("  Supply Chain, Notifications, Menu Engineering, Waste, Training")
    print("═"*70)
    print(f"  Mode    : {'DRY RUN' if DRY_RUN else 'EXECUTE'}")
    print(f"  Section : {SECTION}")

    load_context()

    to_run  = ORDER if SECTION == "all" else [SECTION]
    results = {}

    for sec in to_run:
        fn = SECTION_MAP.get(sec)
        if not fn:
            warn(f"Section '{sec}' tidak dikenal.")
            continue
        try:
            fn(dry_run=DRY_RUN)
            results[sec] = "OK"
        except Exception as e:
            import traceback
            warn(f"ERROR di {sec}: {e}")
            traceback.print_exc()
            results[sec] = f"ERROR: {e}"

    elapsed = time.time() - t_total
    print("\n" + "═"*70)
    print(f"  SELESAI dalam {elapsed:.1f}s")
    print("─"*70)
    for sec, res in results.items():
        icon = "✓" if res == "OK" else "✗"
        print(f"  {icon} {sec:<22} {res}")
    print("═"*70)

    if DRY_RUN:
        print("\n  Jalankan dengan --execute untuk menyimpan ke DB\n")

    print(f"\n  {'Tabel':<45} {'Rows':>12}")
    print("─"*60)
    for t in NEW_TABLES:
        cnt     = row_count(t) if not DRY_RUN else "—"
        cnt_str = f"{cnt:,}" if isinstance(cnt, int) and cnt >= 0 else str(cnt)
        print(f"  {t:<45} {cnt_str:>12}")
    print()


try:
    from django.core.management.base import BaseCommand
    class Command(BaseCommand):
        help = "Kafe Nusantara — World Building Extension (10 modul baru)"
        def add_arguments(self, p):
            p.add_argument("--execute", action="store_true", default=False)
            p.add_argument("--section", default="all")
        def handle(self, *args, **opts):
            global DRY_RUN, SECTION
            DRY_RUN = not opts["execute"]
            SECTION = opts["section"]
            main()
except ImportError:
    pass

if __name__ == "__main__":
    main()
