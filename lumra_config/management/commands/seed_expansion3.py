"""
seed_expansion3_adjusted.py
==========================
KAFE NUSANTARA — World Building Phase 3 (Adjusted)
Ekspansi database tahap 3 - DISESUAIKAN dengan tabel existing.

STRATEGY:
  ✓ Gunakan tabel existing (auth_user, lumra_config_*, loyalty_*, hr_*)
  ✓ Buat tabel BARU hanya untuk: task_queue, search, reporting, api_gateway, security
  ✓ Untuk recipe, events, cs, analytics, config → UPSERT ke tabel existing atau simpan di skema terpisah
  ✓ Skip modul yang overlap 100% dengan existing schema

MODUL YANG DISESUAIKAN (5 modul utama baru):
  20. task_queue      — celery tasks, job logs (TABEL BARU)
  21. search          — Meilisearch config, query logs (TABEL BARU)
  22. reporting       — report templates, generated reports (TABEL BARU)
  23. api_gateway     — API keys, webhooks, usage logs (TABEL BARU)
  24. security        — login events, security alerts (TABEL BARU + sec_login_events from django-axes)

MODUL YANG ADAPT KE EXISTING:
  25. recipe_mgmt     → Extend via recipe_v2 tables ATAU simpan di JSON field
  26. events_calendar → Buat tbl sederhana (tbl existing tidak ada)
  27. customer_support→ cs_* tables (buat minimal)
  28. analytics_cube  → Pre-agg tables (TIDAK duplicate loyalty/finance existing)
  29. config_store    → cfg_* tables (minimal + upsert ke django_celery_beat)

Cara pakai:
  python manage.py seed_expansion3_adj --execute
  python manage.py seed_expansion3_adj --execute --section=task_queue
  python manage.py seed_expansion3_adj --list-sections
"""

import os, sys, random, time, json, hashlib, uuid
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
    elif a.startswith("--section="): SECTION = a.split("=", 1)[1]

if "--list-sections" in sys.argv:
    print("Sections: task_queue search reporting api_gateway security "
          "recipe_mgmt events_calendar customer_support analytics_cube config_store all")
    sys.exit(0)

RNG = random.Random(777)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
import django; django.setup()
from django.db import connection

# ── Utilities ─────────────────────────────────────────────────────────────────
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

def rand_hex(n=32):
    return hashlib.sha256(str(RNG.random()).encode()).hexdigest()[:n]

def rand_uuid():
    return str(uuid.UUID(int=RNG.getrandbits(128)))

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
    # From existing tables
    CTX["employee_ids"] = [r[0] for r in q("SELECT id FROM hr_employees ORDER BY id")] \
                          if table_exists("hr_employees") else []
    CTX["loyalty_tiers"]= [r[0] for r in q("SELECT id FROM loyalty_tiers ORDER BY id")] \
                          if table_exists("loyalty_tiers") else []
    ok(f"Context: {len(CTX['location_ids'])} locs, {len(CTX['customer_ids'])} custs, "
       f"{len(CTX['order_ids'])} orders, {len(CTX['employee_ids'])} emps, "
       f"{len(CTX['loyalty_tiers'])} loyalty tiers")

today = date.today()

# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 20 — TASK QUEUE (Celery + Redis)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_task_queue(dry_run=False):
    head("MODUL 20 — TASK QUEUE (Celery Jobs, Scheduled Tasks, DLQ)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS tq_task_definitions (
            id              BIGSERIAL PRIMARY KEY,
            task_name       VARCHAR(120) UNIQUE NOT NULL,
            task_path       VARCHAR(255) NOT NULL,
            description     TEXT DEFAULT '',
            category        VARCHAR(40) DEFAULT 'general',
            default_queue   VARCHAR(50) DEFAULT 'default',
            priority        SMALLINT DEFAULT 5,
            max_retries     SMALLINT DEFAULT 3,
            retry_backoff    INT DEFAULT 60,
            timeout_seconds  INT DEFAULT 300,
            is_scheduled    BOOLEAN DEFAULT FALSE,
            cron_expression VARCHAR(50) DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_task_definitions IS
            'Definisi semua Celery task. Category: reporting, sync, notification, cleanup, analytics.';
        """, "tq_task_definitions"),

        ("""
        CREATE TABLE IF NOT EXISTS tq_job_logs (
            id              BIGSERIAL PRIMARY KEY,
            task_id         VARCHAR(36) NOT NULL,
            task_name       VARCHAR(120) NOT NULL,
            queue           VARCHAR(50) DEFAULT 'default',
            status          VARCHAR(20) DEFAULT 'pending',
            args_summary    TEXT DEFAULT '',
            triggered_by    VARCHAR(50) DEFAULT 'schedule',
            triggered_by_id BIGINT,
            worker_name     VARCHAR(100) DEFAULT '',
            started_at      TIMESTAMPTZ,
            completed_at    TIMESTAMPTZ,
            duration_ms     INT,
            result_summary  TEXT DEFAULT '',
            error_message   TEXT DEFAULT '',
            retry_count     SMALLINT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_job_logs IS 'Log eksekusi setiap Celery task. Untuk monitoring dan debugging.';
        CREATE INDEX IF NOT EXISTS idx_tq_status    ON tq_job_logs(status);
        CREATE INDEX IF NOT EXISTS idx_tq_task_name ON tq_job_logs(task_name);
        CREATE INDEX IF NOT EXISTS idx_tq_created   ON tq_job_logs(created_at DESC);
        """, "tq_job_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS tq_dead_letter_queue (
            id              BIGSERIAL PRIMARY KEY,
            original_task_id VARCHAR(36) NOT NULL,
            task_name       VARCHAR(120) NOT NULL,
            queue           VARCHAR(50) DEFAULT 'default',
            args_payload    JSONB DEFAULT '{}',
            kwargs_payload  JSONB DEFAULT '{}',
            failure_reason  TEXT NOT NULL DEFAULT '',
            failed_at       TIMESTAMPTZ DEFAULT NOW(),
            retry_attempts  SMALLINT DEFAULT 0,
            is_resolved     BOOLEAN DEFAULT FALSE,
            resolved_at     TIMESTAMPTZ,
            resolved_by_id  BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_dead_letter_queue IS 'Task yang gagal setelah max_retries.';
        CREATE INDEX IF NOT EXISTS idx_dlq_resolved ON tq_dead_letter_queue(is_resolved);
        """, "tq_dead_letter_queue"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Task Definitions
    tasks_data = [
        ("refresh_kpi_cache",        "lumra.tasks.refresh_kpi_cache",
         "Refresh semua KPI dashboard cache",                "analytics",     "high",    8,  3,  120, True,  "0 * * * *"),
        ("recalculate_rfm_scores",   "lumra.tasks.recalculate_rfm_scores",
         "Hitung ulang RFM score semua customer",            "analytics",     "default", 5,  2,  600, True,  "0 2 * * *"),
        ("generate_sales_daily",     "lumra.tasks.generate_sales_daily",
         "Agregasi penjualan harian ke report table",        "reporting",     "default", 6,  3,  300, True,  "5 0 * * *"),
        ("sync_meilisearch_products","lumra.tasks.sync_meilisearch_products",
         "Sync produk ke Meilisearch index",                 "sync",          "default", 5,  3,  180, True,  "*/15 * * * *"),
        ("send_promo_notifications", "lumra.tasks.send_promo_notifications",
         "Kirim notifikasi promo terjadwal",                 "notification",  "high",    7,  3,  120, True,  "0 9 * * *"),
        ("cleanup_old_job_logs",     "lumra.tasks.cleanup_old_job_logs",
         "Hapus job logs lebih dari 90 hari",                "cleanup",       "low",     3,  1,  300, True,  "0 4 * * 0"),
        ("generate_pdf_report",      "lumra.tasks.generate_pdf_report",
         "Generate PDF report on-demand via WeasyPrint",     "reporting",     "default", 5,  2,  120, False, ""),
        ("process_webhook_event",    "lumra.tasks.process_webhook_event",
         "Proses outgoing webhook event",                    "webhook",       "high",    8,  5,  30,  False, ""),
        ("send_email_notification",  "lumra.tasks.send_email_notification",
         "Kirim email notifikasi",                           "notification",  "default", 6,  3,  30,  False, ""),
        ("check_reorder_alerts",     "lumra.tasks.check_reorder_alerts",
         "Cek stok dan buat reorder alert jika perlu",       "procurement",   "default", 7,  3,  180, True,  "0 8 * * *"),
        ("auto_close_tickets",       "lumra.tasks.auto_close_tickets",
         "Auto-close ticket yang sudah resolved > 7 hari",  "cleanup",       "low",     3,  1,  120, True,  "0 6 * * *"),
    ]
    task_rows = [(name, path, desc, cat, queue, priority, max_ret, 60, timeout,
                  is_sched, cron, True, datetime.now())
                 for name, path, desc, cat, queue, priority, max_ret, timeout, is_sched, cron in tasks_data]

    if dry_run:
        log(f"[DRY RUN] {len(task_rows)} task defs + ~30k job logs + DLQ")
        return

    n = bulk_insert("tq_task_definitions",
        ["task_name","task_path","description","category","default_queue","priority",
         "max_retries","retry_backoff","timeout_seconds","is_scheduled","cron_expression",
         "is_active","created_at"],
        task_rows, on_conflict="ON CONFLICT (task_name) DO NOTHING")
    ok(f"Task definitions: {n}")

    # Job Logs (30k entries)
    task_names   = [t[0] for t in tasks_data]
    queue_names  = ["default","high","low","notification","reporting","sync","webhook"]
    workers      = [f"worker-{i}@lumra-prod" for i in range(1, 6)]
    statuses_w   = ["success","success","success","failure","revoked","retry"]
    statuses_wts = [65, 0, 0, 15, 5, 15]

    log("Generating job logs...")
    job_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(30000):
        task_name  = RNG.choice(task_names)
        status     = RNG.choices(statuses_w, weights=statuses_wts)[0]
        created_at = datetime.now() - timedelta(
            days=RNG.randint(0, min(days_range, 365)),
            hours=RNG.randint(0, 23), minutes=RNG.randint(0, 59)
        )
        started_at    = created_at + timedelta(seconds=RNG.randint(0, 30))
        duration_ms   = RNG.randint(50, 30000) if status != "revoked" else 0
        completed_at  = started_at + timedelta(milliseconds=duration_ms) if duration_ms else None
        retry_count   = RNG.randint(0, 2) if status in ("failure","retry") else 0
        error_msg     = "" if status == "success" else RNG.choice([
            "ConnectionError: Redis timeout",
            "OperationalError: DB connection failed",
            "TimeoutError: Task exceeded timeout",
        ])

        job_rows.append((
            rand_uuid(), task_name,
            RNG.choice(queue_names), status,
            f"args: [{RNG.randint(1,100)}]",
            RNG.choice(["schedule","api","manual","celery_beat"]),
            None, RNG.choice(workers),
            started_at, completed_at, duration_ms if duration_ms else None,
            "OK" if status == "success" else "",
            error_msg, retry_count, created_at
        ))

    n = bulk_insert("tq_job_logs",
        ["task_id","task_name","queue","status","args_summary",
         "triggered_by","triggered_by_id","worker_name","started_at","completed_at",
         "duration_ms","result_summary","error_message","retry_count","created_at"],
        job_rows, batch=2000)
    ok(f"Job logs: {n:,}")

    # Dead Letter Queue
    dlq_rows = []
    for _ in range(200):
        created_at = datetime.now() - timedelta(days=RNG.randint(0, 90))
        resolved   = RNG.random() < 0.4
        dlq_rows.append((
            rand_uuid(), RNG.choice(task_names),
            RNG.choice(queue_names),
            json.dumps({"location_id": RNG.randint(1, 20)}),
            json.dumps({"period": today.strftime("%Y-%m")}),
            RNG.choice(["Max retries exceeded","Task timeout","Unhandled exception"]),
            created_at, RNG.randint(3, 5),
            resolved, created_at + timedelta(days=RNG.randint(1, 7)) if resolved else None,
            CTX["admin_id"] if resolved else None, created_at
        ))

    n = bulk_insert("tq_dead_letter_queue",
        ["original_task_id","task_name","queue","args_payload","kwargs_payload",
         "failure_reason","failed_at","retry_attempts","is_resolved","resolved_at",
         "resolved_by_id","created_at"],
        dlq_rows)
    ok(f"Dead letter queue: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 21 — SEARCH (Meilisearch)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_search(dry_run=False):
    head("MODUL 21 — SEARCH (Meilisearch Index Config, Query Logs, Synonyms)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS search_index_configs (
            id              BIGSERIAL PRIMARY KEY,
            index_uid       VARCHAR(60) UNIQUE NOT NULL,
            display_name    VARCHAR(100) NOT NULL,
            source_table    VARCHAR(80) NOT NULL,
            primary_key     VARCHAR(30) DEFAULT 'id',
            searchable_attrs JSONB DEFAULT '[]',
            filterable_attrs JSONB DEFAULT '[]',
            total_documents INT DEFAULT 0,
            last_synced_at  TIMESTAMPTZ,
            sync_enabled    BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE search_index_configs IS
            'Konfigurasi index Meilisearch per entity. Sinkron otomatis via Celery task.';
        """, "search_index_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS search_query_logs (
            id              BIGSERIAL PRIMARY KEY,
            index_uid       VARCHAR(60) NOT NULL,
            query_text      VARCHAR(500) NOT NULL DEFAULT '',
            user_id         BIGINT REFERENCES auth_user(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            results_count   INT DEFAULT 0,
            response_ms     INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE search_query_logs IS
            'Log setiap pencarian: kata kunci, jumlah hasil. Untuk search analytics.';
        CREATE INDEX IF NOT EXISTS idx_sq_index   ON search_query_logs(index_uid);
        CREATE INDEX IF NOT EXISTS idx_sq_date    ON search_query_logs(created_at DESC);
        """, "search_query_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS search_synonyms (
            id              BIGSERIAL PRIMARY KEY,
            index_uid       VARCHAR(60) NOT NULL,
            word            VARCHAR(100) NOT NULL,
            synonyms        TEXT[] NOT NULL DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(index_uid, word)
        );
        COMMENT ON TABLE search_synonyms IS
            'Sinonim pencarian per index. Contoh: es kopi = iced coffee = cold brew.';
        """, "search_synonyms"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Index Configs
    indexes_data = [
        ("products",      "Produk & Menu",       "lumra_config_productvariants",
         ["name","description","category","tags"],
         ["category","is_active","price"]),
        ("customers",     "Database Customer",   "lumra_config_customers",
         ["full_name","phone","email","member_id"],
         ["tier","is_active"]),
        ("orders",        "Riwayat Transaksi",   "lumra_config_orders",
         ["order_number","customer_name","notes"],
         ["status","payment_method","location_id"]),
        ("locations",     "Outpost Directory",   "lumra_config_locations",
         ["name","address","city","description"],
         ["is_active","city"]),
        ("vendors",       "Daftar Vendor",       "lumra_config_vendors",
         ["name","contact_name","email","phone"],
         ["is_active"]),
    ]

    idx_rows = []
    for uid, dname, src, srch, filt in indexes_data:
        idx_rows.append((
            uid, dname, src, "id",
            json.dumps(srch), json.dumps(filt),
            RNG.randint(100, 50000),
            datetime.now() - timedelta(minutes=RNG.randint(0, 60)),
            True, datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(idx_rows)} indexes + query logs + synonyms")
        return

    n = bulk_insert("search_index_configs",
        ["index_uid","display_name","source_table","primary_key",
         "searchable_attrs","filterable_attrs","total_documents","last_synced_at",
         "sync_enabled","created_at"],
        idx_rows, on_conflict="ON CONFLICT (index_uid) DO NOTHING")
    ok(f"Search index configs: {n}")

    # Query Logs
    SAMPLE_QUERIES = [
        "es kopi susu","cold brew","americano","filter coffee","latte",
        "pastry","croissant","granola bowl","matcha","chocolate",
        "promo weekend","voucher","diskon","paket hemat",
        "outpost bandung","outpost jakarta","buka jam berapa",
        "menu seasonal","single origin",
    ]

    index_uids = [row[0] for row in indexes_data]
    customer_ids = CTX["customer_ids"]
    user_ids     = CTX["user_ids"]

    ql_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(50000):
        query   = RNG.choice(SAMPLE_QUERIES)
        n_results = RNG.randint(1, 50)
        uid     = RNG.choice(index_uids)
        cid     = RNG.choice(customer_ids) if RNG.random() < 0.6 else None
        uid_user= RNG.choice(user_ids) if RNG.random() < 0.3 else None
        created = datetime.now() - timedelta(
            days=RNG.randint(0, min(days_range, 365)),
            hours=RNG.randint(0, 23)
        )
        ql_rows.append((
            uid, query, uid_user, cid,
            n_results,
            RNG.randint(2, 150), created
        ))

    n = bulk_insert("search_query_logs",
        ["index_uid","query_text","user_id","customer_id",
         "results_count","response_ms","created_at"],
        ql_rows, batch=2000)
    ok(f"Search query logs: {n:,}")

    # Synonyms
    synonyms_data = {
        "products": {
            "es kopi susu": ["iced coffee latte","cold coffee milk"],
            "cold brew":    ["kopi dingin","es kopi"],
            "americano":    ["black coffee","kopi hitam"],
            "latte":        ["coffee latte","kopi susu"],
            "croissant":    ["roti tanduk","pastry"],
        },
        "customers": {
            "member":   ["pelanggan","customer"],
            "loyal":    ["setia","champion"],
        },
        "locations": {
            "outpost":  ["cabang","gerai","toko"],
            "bandung":  ["bdg","kota kembang"],
        }
    }
    syn_rows = []
    for idx_uid, syns in synonyms_data.items():
        for word, synonyms in syns.items():
            syn_rows.append((idx_uid, word, synonyms, True, datetime.now()))

    n = bulk_insert("search_synonyms",
        ["index_uid","word","synonyms","is_active","created_at"],
        syn_rows, on_conflict="ON CONFLICT (index_uid, word) DO NOTHING")
    ok(f"Search synonyms: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 22 — REPORTING (WeasyPrint PDF Reports)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_reporting(dry_run=False):
    head("MODUL 22 — REPORTING (Templates, Generated Reports, Delivery)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS report_templates (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(40) UNIQUE NOT NULL,
            title           VARCHAR(150) NOT NULL,
            description     TEXT DEFAULT '',
            report_type     VARCHAR(30) NOT NULL DEFAULT 'operational',
            template_path   VARCHAR(255) NOT NULL DEFAULT '',
            output_format   VARCHAR(10) DEFAULT 'pdf',
            parameters      JSONB DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            requires_role   VARCHAR(40) DEFAULT 'staff',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_templates IS
            'Template laporan PDF via WeasyPrint. Type: operational, financial, hr, analytics.';
        """, "report_templates"),

        ("""
        CREATE TABLE IF NOT EXISTS report_generated (
            id              BIGSERIAL PRIMARY KEY,
            template_id     BIGINT REFERENCES report_templates(id),
            report_title    VARCHAR(200) NOT NULL,
            parameters      JSONB DEFAULT '{}',
            file_name       VARCHAR(255) NOT NULL DEFAULT '',
            file_size_kb    INT DEFAULT 0,
            page_count      INT DEFAULT 1,
            status          VARCHAR(20) DEFAULT 'generating',
            generated_by_id BIGINT REFERENCES auth_user(id),
            generation_ms   INT DEFAULT 0,
            error_message   TEXT DEFAULT '',
            download_count  INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_generated IS 'Log setiap laporan yang di-generate.';
        CREATE INDEX IF NOT EXISTS idx_rg_template ON report_generated(template_id);
        CREATE INDEX IF NOT EXISTS idx_rg_date     ON report_generated(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_rg_status   ON report_generated(status);
        """, "report_generated"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Templates
    templates_data = [
        ("DAILY_SALES",       "Laporan Penjualan Harian",         "operational"),
        ("WEEKLY_SALES",      "Laporan Penjualan Mingguan",       "operational"),
        ("MONTHLY_SALES",     "Laporan Penjualan Bulanan",        "operational"),
        ("PAYSLIP",           "Slip Gaji Karyawan",               "hr"),
        ("PAYROLL_SUMMARY",   "Rekapitulasi Payroll Bulanan",     "hr"),
        ("INVENTORY_STOCK",   "Laporan Stok Inventaris",          "operational"),
        ("CUSTOMER_STATEMENT","Laporan Transaksi Customer",       "crm"),
        ("RFM_REPORT",        "Analisis RFM Customer",            "analytics"),
        ("WASTE_REPORT",      "Laporan Waste Produksi",           "operational"),
        ("FINANCIAL_SUMMARY", "Ringkasan Keuangan Bulanan",       "financial"),
        ("SHIFT_SUMMARY",     "Ringkasan Shift Harian",           "operational"),
    ]
    tmpl_rows = [(code, title, "", rtype, "", "pdf",
                  json.dumps({}), True, "manager", datetime.now())
                 for code, title, rtype in templates_data]

    if dry_run:
        log(f"[DRY RUN] {len(tmpl_rows)} templates + generated reports")
        return

    n = bulk_insert("report_templates",
        ["code","title","description","report_type","template_path","output_format",
         "parameters","is_active","requires_role","created_at"],
        tmpl_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Report templates: {n}")

    # Generated Reports
    tmpl_ids  = [r[0] for r in q("SELECT id FROM report_templates ORDER BY id")]
    gen_rows   = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(3000):
        tid      = RNG.choice(tmpl_ids)
        status   = RNG.choices(["completed","completed","failed"],
                               weights=[90, 0, 10])[0]
        gen_ms   = RNG.randint(500, 15000) if status == "completed" else 0
        created  = datetime.now() - timedelta(days=RNG.randint(0, min(days_range, 365)))
        user_ids = CTX["user_ids"]
        gen_rows.append((
            tid,
            f"Laporan #{RNG.randint(1000,9999)}",
            json.dumps({"period": created.strftime("%Y-%m")}),
            f"report_{rand_hex(8)}.pdf",
            RNG.randint(50, 5000),
            RNG.randint(1, 50),
            status,
            RNG.choice(user_ids) if user_ids else CTX["admin_id"],
            gen_ms, "",
            RNG.randint(0, 20), created
        ))

    n = bulk_insert("report_generated",
        ["template_id","report_title","parameters","file_name",
         "file_size_kb","page_count","status","generated_by_id","generation_ms",
         "error_message","download_count","created_at"],
        gen_rows, batch=2000)
    ok(f"Generated reports: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 23 — API GATEWAY (DRF — API Keys, Rate Limits, Webhooks)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_api_gateway(dry_run=False):
    head("MODUL 23 — API GATEWAY (API Keys, Usage Logs, Webhooks)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id              BIGSERIAL PRIMARY KEY,
            key_id          VARCHAR(20) UNIQUE NOT NULL,
            key_hash        VARCHAR(64) NOT NULL,
            name            VARCHAR(100) NOT NULL,
            owner_id        BIGINT REFERENCES auth_user(id),
            scopes          TEXT[] DEFAULT '{}',
            allowed_ips     TEXT[] DEFAULT '{}',
            rate_limit_tier VARCHAR(20) DEFAULT 'standard',
            is_active       BOOLEAN DEFAULT TRUE,
            expires_at      TIMESTAMPTZ,
            last_used_at    TIMESTAMPTZ,
            total_requests  BIGINT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_keys IS
            'API Keys untuk akses DRF endpoints. Scopes: read, write, admin, webhook.';
        CREATE INDEX IF NOT EXISTS idx_api_key_owner ON api_keys(owner_id);
        """, "api_keys"),

        ("""
        CREATE TABLE IF NOT EXISTS api_usage_logs (
            id              BIGSERIAL PRIMARY KEY,
            api_key_id      BIGINT REFERENCES api_keys(id),
            endpoint        VARCHAR(200) NOT NULL,
            method          VARCHAR(10) NOT NULL DEFAULT 'GET',
            status_code     SMALLINT NOT NULL DEFAULT 200,
            response_ms     INT DEFAULT 0,
            ip_address      INET,
            error_code      VARCHAR(30) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_usage_logs IS
            'Log setiap API request. Untuk billing, analytics, debugging.';
        CREATE INDEX IF NOT EXISTS idx_api_usage_key    ON api_usage_logs(api_key_id);
        CREATE INDEX IF NOT EXISTS idx_api_usage_date   ON api_usage_logs(created_at DESC);
        """, "api_usage_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS api_webhooks (
            id              BIGSERIAL PRIMARY KEY,
            webhook_id      VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            owner_id        BIGINT REFERENCES auth_user(id),
            target_url      VARCHAR(500) NOT NULL,
            secret_key      VARCHAR(64) NOT NULL DEFAULT '',
            events          TEXT[] NOT NULL DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            failure_count   INT DEFAULT 0,
            last_triggered_at TIMESTAMPTZ,
            last_status     VARCHAR(20) DEFAULT 'never',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_webhooks IS
            'Webhook endpoints untuk event push. Events: order.completed, stock.low, payroll.processed.';
        """, "api_webhooks"),

        ("""
        CREATE TABLE IF NOT EXISTS api_webhook_deliveries (
            id              BIGSERIAL PRIMARY KEY,
            webhook_id      BIGINT NOT NULL REFERENCES api_webhooks(id),
            event_type      VARCHAR(60) NOT NULL,
            payload         JSONB NOT NULL DEFAULT '{}',
            response_code   SMALLINT,
            duration_ms     INT DEFAULT 0,
            attempt_number  SMALLINT DEFAULT 1,
            status          VARCHAR(20) DEFAULT 'pending',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_webhook_deliveries IS
            'Log pengiriman webhook. Retry otomatis 3x dengan exponential backoff.';
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_webhook ON api_webhook_deliveries(webhook_id);
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_status  ON api_webhook_deliveries(status);
        """, "api_webhook_deliveries"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]

    # API Keys
    SCOPES_SETS = [
        ["read"],
        ["read","write"],
        ["read","write","webhook"],
        ["read","write","admin","webhook"],
    ]
    APP_NAMES = [
        "Lumra POS Mobile","Lumra Dashboard Web","Lumra Manager App",
        "Inventory Scanner","Analytics Platform","WhatsApp Bot",
    ]
    key_rows = []
    for i in range(30):
        uid    = RNG.choice(user_ids) if user_ids else admin_id
        kid    = f"KN{rand_hex(6).upper()}"
        khash  = rand_hex(64)
        created = datetime.now() - timedelta(days=RNG.randint(0, 365))
        key_rows.append((
            kid, khash,
            RNG.choice(APP_NAMES),
            uid,
            RNG.choice(SCOPES_SETS),
            [],
            RNG.choice(["standard","standard","premium"]),
            RNG.random() > 0.1,
            created + timedelta(days=365) if RNG.random() < 0.2 else None,
            datetime.now() - timedelta(hours=RNG.randint(0, 720)),
            RNG.randint(100, 500000),
            created
        ))

    if dry_run:
        log(f"[DRY RUN] 30 API keys + usage logs + webhooks + deliveries")
        return

    n = bulk_insert("api_keys",
        ["key_id","key_hash","name","owner_id","scopes","allowed_ips",
         "rate_limit_tier","is_active","expires_at","last_used_at",
         "total_requests","created_at"],
        key_rows, on_conflict="ON CONFLICT (key_id) DO NOTHING")
    ok(f"API keys: {n}")

    # Usage Logs
    key_ids   = [r[0] for r in q("SELECT id FROM api_keys ORDER BY id")]
    ENDPOINTS = [
        "/api/v1/orders/","/api/v1/products/",
        "/api/v1/customers/","/api/v1/inventory/stock/",
        "/api/v1/reports/sales-daily/","/api/v1/promotions/",
    ]
    METHODS   = ["GET","GET","GET","POST","PUT"]
    STATUSES  = [200,200,200,201,400,401,404,500]
    STAT_WTS  = [65, 0, 0, 15, 8, 5, 5, 2]
    IPS       = [f"10.{RNG.randint(0,5)}.{RNG.randint(0,255)}.{RNG.randint(1,254)}" for _ in range(20)]

    usage_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(50000):
        created = datetime.now() - timedelta(
            days=RNG.randint(0, min(days_range, 365)), hours=RNG.randint(0, 23)
        )
        status = RNG.choices(STATUSES, weights=STAT_WTS)[0]
        usage_rows.append((
            RNG.choice(key_ids) if key_ids else None,
            RNG.choice(ENDPOINTS),
            RNG.choice(METHODS),
            status,
            RNG.randint(5, 2000),
            RNG.choice(IPS),
            "" if status < 400 else RNG.choice(["RATE_LIMIT","NOT_FOUND","AUTH_FAILED"]),
            created
        ))

    n = bulk_insert("api_usage_logs",
        ["api_key_id","endpoint","method","status_code","response_ms",
         "ip_address","error_code","created_at"],
        usage_rows, batch=2000)
    ok(f"API usage logs: {n:,}")

    # Webhooks
    EVENTS_SETS = [
        ["order.completed","order.cancelled"],
        ["stock.low","stock.out"],
        ["customer.registered","customer.tier_upgrade"],
    ]
    wh_rows = []
    for i in range(15):
        uid = RNG.choice(user_ids) if user_ids else admin_id
        wh_rows.append((
            f"WH{rand_hex(8).upper()}", f"Webhook #{i+1}",
            uid, f"https://hooks.example{i}.com/lumra",
            rand_hex(32), RNG.choice(EVENTS_SETS), True,
            RNG.randint(0, 5),
            datetime.now() - timedelta(hours=RNG.randint(0, 720)),
            RNG.choice(["success","success","failed"]),
            datetime.now()
        ))

    n = bulk_insert("api_webhooks",
        ["webhook_id","name","owner_id","target_url","secret_key","events",
         "is_active","failure_count","last_triggered_at","last_status","created_at"],
        wh_rows, on_conflict="ON CONFLICT (webhook_id) DO NOTHING")
    ok(f"Webhooks: {n}")

    # Webhook Deliveries
    wh_ids   = [r[0] for r in q("SELECT id FROM api_webhooks ORDER BY id")]
    WH_EVENTS= ["order.completed","stock.low","customer.registered"]
    wdlv_rows= []
    for _ in range(5000):
        wid    = RNG.choice(wh_ids) if wh_ids else 1
        status = RNG.choices(["delivered","delivered","failed"],
                             weights=[80, 0, 20])[0]
        created= datetime.now() - timedelta(days=RNG.randint(0, 90))
        wdlv_rows.append((
            wid, RNG.choice(WH_EVENTS),
            json.dumps({"event": "test", "data": {"id": RNG.randint(1,1000)}}),
            200 if status == "delivered" else RNG.choice([400, 500, None]),
            RNG.randint(50, 3000),
            RNG.randint(1, 3),
            status, created
        ))

    n = bulk_insert("api_webhook_deliveries",
        ["webhook_id","event_type","payload","response_code",
         "duration_ms","attempt_number","status","created_at"],
        wdlv_rows, batch=2000)
    ok(f"Webhook deliveries: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 24 — SECURITY (Login Events, Alerts)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_security(dry_run=False):
    head("MODUL 24 — SECURITY (Login Events, Security Alerts)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS sec_login_events (
            id              BIGSERIAL PRIMARY KEY,
            user_id         BIGINT REFERENCES auth_user(id),
            event_type      VARCHAR(20) NOT NULL DEFAULT 'login_success',
            ip_address      INET NOT NULL,
            user_agent      TEXT DEFAULT '',
            device_fingerprint VARCHAR(64) DEFAULT '',
            is_suspicious   BOOLEAN DEFAULT FALSE,
            failure_reason  VARCHAR(50) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_login_events IS
            'Log semua login attempt. Event: login_success, login_failed, logout, password_reset.';
        CREATE INDEX IF NOT EXISTS idx_login_user ON sec_login_events(user_id);
        CREATE INDEX IF NOT EXISTS idx_login_date ON sec_login_events(created_at DESC);
        """, "sec_login_events"),

        ("""
        CREATE TABLE IF NOT EXISTS sec_security_alerts (
            id              BIGSERIAL PRIMARY KEY,
            alert_type      VARCHAR(40) NOT NULL,
            severity        VARCHAR(10) NOT NULL DEFAULT 'medium',
            title           VARCHAR(200) NOT NULL,
            description     TEXT DEFAULT '',
            affected_user_id BIGINT REFERENCES auth_user(id),
            ip_address      INET,
            status          VARCHAR(20) DEFAULT 'open',
            acknowledged_by_id BIGINT REFERENCES auth_user(id),
            acknowledged_at TIMESTAMPTZ,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_security_alerts IS
            'Alert keamanan: brute force, unusual location, privilege escalation.';
        CREATE INDEX IF NOT EXISTS idx_sec_alert_type ON sec_security_alerts(alert_type);
        CREATE INDEX IF NOT EXISTS idx_sec_alert_sev  ON sec_security_alerts(severity);
        CREATE INDEX IF NOT EXISTS idx_sec_alert_date ON sec_security_alerts(created_at DESC);
        """, "sec_security_alerts"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]
    days_range = (today - CTX["min_date"]).days

    IPS = [f"{RNG.randint(1,223)}.{RNG.randint(0,255)}.{RNG.randint(0,255)}.{RNG.randint(1,254)}"
           for _ in range(100)]
    UAS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit LumraPOS/3.2",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
        "LumraManager/2.1 (Android 14)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14) Safari/17",
    ]

    # Login Events
    login_rows = []
    for _ in range(15000):
        uid    = RNG.choice(user_ids) if user_ids else admin_id
        etype  = RNG.choices(
            ["login_success","login_success","login_success","login_failed","logout"],
            weights=[70, 0, 0, 20, 10]
        )[0]
        is_sus = etype == "login_failed" and RNG.random() < 0.2
        created= datetime.now() - timedelta(
            days=RNG.randint(0, min(days_range, 365)), hours=RNG.randint(0, 23)
        )
        login_rows.append((
            uid,
            etype,
            RNG.choice(IPS),
            RNG.choice(UAS),
            rand_hex(16),
            is_sus,
            "" if etype != "login_failed" else RNG.choice(["wrong_password","account_locked"]),
            created
        ))

    if dry_run:
        log(f"[DRY RUN] login events + security alerts")
        return

    n = bulk_insert("sec_login_events",
        ["user_id","event_type","ip_address","user_agent",
         "device_fingerprint","is_suspicious","failure_reason","created_at"],
        login_rows, batch=2000)
    ok(f"Login events: {n:,}")

    # Security Alerts
    ALERT_TYPES = ["brute_force","unusual_location",
                   "privilege_escalation","api_abuse"]
    SEVERITIES  = ["low","medium","high","critical"]
    alert_rows  = []
    for _ in range(150):
        atype   = RNG.choice(ALERT_TYPES)
        sev     = RNG.choices(SEVERITIES, weights=[25,40,25,10])[0]
        created = datetime.now() - timedelta(days=RNG.randint(0, 90))
        status  = RNG.choices(["open","acknowledged","resolved"],weights=[35,30,35])[0]
        uid     = RNG.choice(user_ids) if user_ids else admin_id
        alert_rows.append((
            atype, sev,
            f"[{sev.upper()}] {atype.replace('_',' ').title()}",
            f"Suspicious activity from IP {RNG.choice(IPS)}",
            uid,
            RNG.choice(IPS),
            status,
            admin_id if status != "open" else None,
            created + timedelta(hours=2) if status != "open" else None,
            created
        ))

    n = bulk_insert("sec_security_alerts",
        ["alert_type","severity","title","description","affected_user_id","ip_address",
         "status","acknowledged_by_id","acknowledged_at","created_at"],
        alert_rows)
    ok(f"Security alerts: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 25 — EVENTS CALENDAR (Minimal)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_events_calendar(dry_run=False):
    head("MODUL 25 — EVENTS CALENDAR (Events, Registrations)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS events_calendar (
            id              BIGSERIAL PRIMARY KEY,
            event_code      VARCHAR(30) UNIQUE NOT NULL,
            title           VARCHAR(200) NOT NULL,
            description     TEXT DEFAULT '',
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            start_datetime  TIMESTAMPTZ NOT NULL,
            end_datetime    TIMESTAMPTZ NOT NULL,
            capacity        INT DEFAULT 0,
            ticket_price    NUMERIC(10,2) DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'upcoming',
            is_published    BOOLEAN DEFAULT FALSE,
            created_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE events_calendar IS
            'Event Kafe Nusantara: cupping session, live music, workshop, menu launch.';
        CREATE INDEX IF NOT EXISTS idx_evt_location ON events_calendar(location_id);
        CREATE INDEX IF NOT EXISTS idx_evt_date     ON events_calendar(start_datetime);
        """, "events_calendar"),

        ("""
        CREATE TABLE IF NOT EXISTS event_registrations (
            id              BIGSERIAL PRIMARY KEY,
            event_id        BIGINT NOT NULL REFERENCES events_calendar(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            registrant_name VARCHAR(100) NOT NULL DEFAULT '',
            registrant_email VARCHAR(100) DEFAULT '',
            ticket_qty      INT DEFAULT 1,
            total_paid      NUMERIC(10,2) DEFAULT 0,
            payment_status  VARCHAR(20) DEFAULT 'paid',
            check_in_at     TIMESTAMPTZ,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE event_registrations IS 'Pendaftaran peserta event.';
        CREATE INDEX IF NOT EXISTS idx_evtreg_event ON event_registrations(event_id);
        """, "event_registrations"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    customer_ids = CTX["customer_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]
    days_range   = (today - CTX["min_date"]).days

    EVENT_TYPES  = ["cupping_session","barista_workshop","live_music","menu_launching"]

    evt_rows = []
    for i in range(80):
        start_date  = CTX["min_date"] + timedelta(days=RNG.randint(0, days_range + 60))
        start_dt    = datetime.combine(start_date, dtime(RNG.randint(9, 19), 0))
        end_dt      = start_dt + timedelta(hours=RNG.randint(2, 4))
        status      = ("completed" if end_dt < datetime.now() else
                       "ongoing"   if start_dt <= datetime.now() <= end_dt else
                       "upcoming")
        is_free     = RNG.random() < 0.2
        ticket_price= Decimal("0") if is_free else Decimal(str(RNG.randint(50000, 250000)))
        capacity    = RNG.randint(10, 60)
        evt_rows.append((
            f"EVT-{i+1:04d}",
            f"{RNG.choice(EVENT_TYPES).replace('_',' ').title()} #{i+1}",
            "Bergabunglah dalam pengalaman kopi yang tak terlupakan.",
            RNG.choice(location_ids),
            start_dt, end_dt,
            capacity, ticket_price, status, True,
            RNG.choice(user_ids) if user_ids else admin_id,
            datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(evt_rows)} events + registrations")
        return

    n = bulk_insert("events_calendar",
        ["event_code","title","description","location_id",
         "start_datetime","end_datetime","capacity","ticket_price",
         "status","is_published","created_by_id","created_at"],
        evt_rows, on_conflict="ON CONFLICT (event_code) DO NOTHING")
    ok(f"Events: {n}")

    # Registrations
    evt_data  = q("SELECT id, capacity, ticket_price FROM events_calendar ORDER BY id")
    reg_rows  = []
    for eid, cap, ticket_price in evt_data:
        n_reg = RNG.randint(0, min(cap, 20))
        for _ in range(n_reg):
            cid = RNG.choice(customer_ids) if RNG.random() < 0.7 else None
            qty = RNG.randint(1, 2)
            paid = Decimal(str(ticket_price or 0)) * qty
            attended = RNG.random() < 0.85
            reg_rows.append((
                eid, cid,
                f"Peserta {RNG.randint(1000,9999)}",
                f"peserta{RNG.randint(1000,9999)}@email.com",
                qty, paid.quantize(Decimal("0.01")),
                "paid",
                datetime.now() - timedelta(hours=RNG.randint(1, 48)) if attended else None,
                datetime.now()
            ))

    n = bulk_insert("event_registrations",
        ["event_id","customer_id","registrant_name","registrant_email",
         "ticket_qty","total_paid","payment_status","check_in_at","created_at"],
        reg_rows, batch=2000)
    ok(f"Event registrations: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 26 — CUSTOMER SUPPORT (Minimal)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_customer_support(dry_run=False):
    head("MODUL 26 — CUSTOMER SUPPORT (Tickets, Messages)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS cs_tickets (
            id              BIGSERIAL PRIMARY KEY,
            ticket_number   VARCHAR(20) UNIQUE NOT NULL,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            channel         VARCHAR(20) DEFAULT 'app',
            category        VARCHAR(30) NOT NULL DEFAULT 'general',
            priority        VARCHAR(10) DEFAULT 'normal',
            status          VARCHAR(20) DEFAULT 'open',
            subject         VARCHAR(200) NOT NULL,
            description     TEXT NOT NULL DEFAULT '',
            assigned_to_id  BIGINT REFERENCES auth_user(id),
            resolved_at     TIMESTAMPTZ,
            satisfaction_score SMALLINT CHECK(satisfaction_score BETWEEN 1 AND 5),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_tickets IS
            'Tiket support customer. Category: product_quality, order_issue, payment, complaint.';
        CREATE INDEX IF NOT EXISTS idx_ticket_status   ON cs_tickets(status);
        CREATE INDEX IF NOT EXISTS idx_ticket_customer ON cs_tickets(customer_id);
        """, "cs_tickets"),

        ("""
        CREATE TABLE IF NOT EXISTS cs_ticket_messages (
            id              BIGSERIAL PRIMARY KEY,
            ticket_id       BIGINT NOT NULL REFERENCES cs_tickets(id),
            sender_type     VARCHAR(10) NOT NULL DEFAULT 'customer',
            sender_id       BIGINT REFERENCES auth_user(id),
            message         TEXT NOT NULL,
            is_internal     BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_ticket_messages IS
            'Pesan dalam tiket. sender_type: customer, agent, system.';
        CREATE INDEX IF NOT EXISTS idx_tm_ticket ON cs_ticket_messages(ticket_id);
        """, "cs_ticket_messages"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    customer_ids = CTX["customer_ids"]
    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]
    days_range   = (today - CTX["min_date"]).days

    CATEGORIES = ["product_quality","order_issue","payment","complaint","suggestion"]
    CHANNELS   = ["app","whatsapp","email"]
    PRIORITIES = ["low","normal","normal","normal","high"]
    SUBJECTS   = [
        "Pesanan saya salah","Kopi terasa pahit","Promo tidak berfungsi",
        "Stamp tidak bertambah","Refund request","Saran menu baru",
        "Compliment untuk barista","Request khusus",
    ]

    ticket_rows = []
    for i in range(2000):
        created = datetime.now() - timedelta(
            days=RNG.randint(0, min(days_range, 365)), hours=RNG.randint(0, 23)
        )
        status   = RNG.choices(["open","in_progress","resolved","closed"],
                               weights=[20, 30, 35, 15])[0]
        resolved_at = created + timedelta(hours=RNG.randint(2, 96)) \
                      if status in ("resolved","closed") else None
        ticket_rows.append((
            f"TKT-{i+1:06d}",
            RNG.choice(customer_ids),
            RNG.choice(location_ids),
            RNG.choice(CHANNELS),
            RNG.choice(CATEGORIES), RNG.choice(PRIORITIES),
            status,
            RNG.choice(SUBJECTS),
            "Detail keluhan dari customer.",
            RNG.choice(user_ids) if user_ids else admin_id,
            resolved_at,
            RNG.randint(3, 5) if status == "closed" else None,
            created
        ))

    if dry_run:
        log(f"[DRY RUN] tickets + messages")
        return

    n = bulk_insert("cs_tickets",
        ["ticket_number","customer_id","location_id","channel",
         "category","priority","status","subject","description",
         "assigned_to_id","resolved_at","satisfaction_score","created_at"],
        ticket_rows, batch=2000,
        on_conflict="ON CONFLICT (ticket_number) DO NOTHING")
    ok(f"Tickets: {n:,}")

    # Messages
    ticket_ids = [r[0] for r in q("SELECT id FROM cs_tickets ORDER BY id")]
    msg_rows   = []
    CUST_MSGS  = [
        "Saya ingin melaporkan pesanan yang tidak sesuai.",
        "Kopi saya terasa berbeda dari biasanya.",
        "Stamp saya tidak bertambah.",
        "Terima kasih atas penanganannya!",
    ]
    AGENT_MSGS = [
        "Halo, terima kasih sudah menghubungi kami. Kami sedang meninjau laporan Anda.",
        "Kami mohon maaf atas ketidaknyamanan ini.",
        "Stamp Anda sudah kami tambahkan. Mohon maaf.",
        "Masalah sudah berhasil diselesaikan.",
    ]

    for tid in ticket_ids:
        n_msg = RNG.randint(2, 6)
        for j in range(n_msg):
            is_agent = j % 2 == 1
            msg_rows.append((
                tid,
                "agent" if is_agent else "customer",
                RNG.choice(user_ids) if is_agent and user_ids else None,
                RNG.choice(AGENT_MSGS if is_agent else CUST_MSGS),
                RNG.random() < 0.1 and is_agent,
                datetime.now() - timedelta(days=RNG.randint(0, 30))
            ))

    n = bulk_insert("cs_ticket_messages",
        ["ticket_id","sender_type","sender_id","message","is_internal","created_at"],
        msg_rows, batch=2000)
    ok(f"Ticket messages: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 27 — ANALYTICS CUBE (Pre-aggregated, NO duplicate existing)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_analytics_cube(dry_run=False):
    head("MODUL 27 — ANALYTICS CUBE (Conversion Funnel, Product Affinity)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS analytics_conversion_funnel (
            id              BIGSERIAL PRIMARY KEY,
            funnel_date     DATE NOT NULL,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            channel         VARCHAR(20) DEFAULT 'all',
            stage           VARCHAR(30) NOT NULL,
            stage_order     SMALLINT NOT NULL,
            users_count     INT DEFAULT 0,
            conversion_rate NUMERIC(6,3) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(funnel_date, location_id, channel, stage)
        );
        COMMENT ON TABLE analytics_conversion_funnel IS
            'Funnel konversi: visit → browse → add_to_cart → checkout → order → repeat.';
        """, "analytics_conversion_funnel"),

        ("""
        CREATE TABLE IF NOT EXISTS analytics_product_affinity (
            id              BIGSERIAL PRIMARY KEY,
            variant_a_id    BIGINT REFERENCES lumra_config_productvariants(id),
            variant_b_id    BIGINT REFERENCES lumra_config_productvariants(id),
            co_purchase_count INT DEFAULT 0,
            support_pct     NUMERIC(6,3) DEFAULT 0,
            confidence_pct  NUMERIC(6,3) DEFAULT 0,
            lift_score      NUMERIC(8,4) DEFAULT 0,
            period          VARCHAR(7) NOT NULL,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(variant_a_id, variant_b_id, period)
        );
        COMMENT ON TABLE analytics_product_affinity IS
            'Market basket: produk yang sering dibeli bersama. Basis untuk cross-sell.';
        CREATE INDEX IF NOT EXISTS idx_affinity_lift ON analytics_product_affinity(lift_score DESC);
        """, "analytics_product_affinity"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    variant_ids  = CTX["variant_ids"]
    days_range   = (today - CTX["min_date"]).days

    # Conversion Funnel
    FUNNEL_STAGES = [
        ("visit",        1),
        ("browse_menu",  2),
        ("add_to_cart",  3),
        ("checkout",     4),
        ("order_placed", 5),
    ]
    CHANNELS = ["dine_in","takeaway","app"]
    fnl_rows = []
    for d in range(min(days_range, 60)):
        fdate = today - timedelta(days=d)
        for lid in location_ids:
            for channel in CHANNELS:
                base_visits = RNG.randint(50, 300)
                prev_count  = base_visits
                for stage, sorder in FUNNEL_STAGES:
                    drop = RNG.uniform(0.6, 0.95) if stage != "visit" else 1.0
                    current = int(prev_count * drop)
                    conv_rate = round(current / base_visits * 100, 3) if base_visits > 0 else 0
                    fnl_rows.append((
                        fdate, lid, channel, stage, sorder,
                        current, conv_rate, datetime.now()
                    ))
                    prev_count = current

    if dry_run:
        log(f"[DRY RUN] funnel + product affinity")
        return

    n = bulk_insert("analytics_conversion_funnel",
        ["funnel_date","location_id","channel","stage","stage_order",
         "users_count","conversion_rate","created_at"],
        fnl_rows, batch=2000,
        on_conflict="ON CONFLICT (funnel_date, location_id, channel, stage) DO NOTHING")
    ok(f"Conversion funnel: {n:,}")

    # Product Affinity
    aff_rows = []
    sample_variants = RNG.sample(variant_ids, min(60, len(variant_ids)))
    for period_offset in range(4):
        period = (today.replace(day=1) - timedelta(days=period_offset * 30)).replace(day=1).strftime("%Y-%m")
        for i in range(len(sample_variants)):
            for j in range(i+1, min(i+8, len(sample_variants))):
                va = sample_variants[i]
                vb = sample_variants[j]
                co_count   = RNG.randint(5, 150)
                support    = round(co_count / 5000 * 100, 3)
                confidence = round(RNG.uniform(0.1, 0.7), 3)
                lift       = round(confidence / RNG.uniform(0.05, 0.25), 4)
                aff_rows.append((va, vb, co_count, support, confidence, lift, period, datetime.now()))

    n = bulk_insert("analytics_product_affinity",
        ["variant_a_id","variant_b_id","co_purchase_count","support_pct",
         "confidence_pct","lift_score","period","created_at"],
        aff_rows, batch=2000,
        on_conflict="ON CONFLICT (variant_a_id, variant_b_id, period) DO NOTHING")
    ok(f"Product affinity: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 28 — CONFIG STORE (Minimal)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_config_store(dry_run=False):
    head("MODUL 28 — CONFIG STORE (Feature Flags, App Configs)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS cfg_feature_flags (
            id              BIGSERIAL PRIMARY KEY,
            flag_key        VARCHAR(80) UNIQUE NOT NULL,
            display_name    VARCHAR(120) NOT NULL,
            description     TEXT DEFAULT '',
            flag_type       VARCHAR(20) DEFAULT 'boolean',
            default_value   JSONB NOT NULL DEFAULT 'false',
            current_value   JSONB NOT NULL DEFAULT 'false',
            rollout_pct     SMALLINT DEFAULT 100 CHECK(rollout_pct BETWEEN 0 AND 100),
            is_active       BOOLEAN DEFAULT TRUE,
            changed_by_id   BIGINT REFERENCES auth_user(id),
            changed_at      TIMESTAMPTZ DEFAULT NOW(),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_feature_flags IS
            'Feature flags untuk A/B testing dan gradual rollout.';
        """, "cfg_feature_flags"),

        ("""
        CREATE TABLE IF NOT EXISTS cfg_app_configs (
            id              BIGSERIAL PRIMARY KEY,
            config_key      VARCHAR(80) UNIQUE NOT NULL,
            config_group    VARCHAR(40) NOT NULL DEFAULT 'general',
            value_type      VARCHAR(20) DEFAULT 'string',
            value           JSONB NOT NULL DEFAULT 'null',
            description     TEXT DEFAULT '',
            changed_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_app_configs IS
            'Konfigurasi aplikasi yang bisa diubah tanpa deploy.';
        CREATE INDEX IF NOT EXISTS idx_cfg_group ON cfg_app_configs(config_group);
        """, "cfg_app_configs"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    admin_id = CTX["admin_id"]

    # Feature Flags
    flags_data = [
        ("loyalty_v2_enabled",         "Loyalty Program V2",           "boolean", True,   True,  100),
        ("meilisearch_enabled",         "Meilisearch Search",           "boolean", True,   True,  100),
        ("ai_recommendations",          "AI Product Recommendations",   "boolean", False,  False, 20),
        ("new_pos_ui",                  "New POS Interface",            "boolean", False,  True,  50),
        ("digital_receipt",             "Digital Receipt Only",         "boolean", False,  False, 0),
        ("qris_split_payment",          "QRIS Split Payment",           "boolean", False,  True,  100),
        ("whatsapp_notifications",      "WhatsApp Notifications",       "boolean", True,   True,  100),
    ]

    flag_rows = [(key, name, "", "boolean",
                  json.dumps(default), json.dumps(current),
                  rollout, True, admin_id, datetime.now(), datetime.now())
                 for key, name, ftype, default, current, rollout in flags_data]

    if dry_run:
        log(f"[DRY RUN] {len(flag_rows)} feature flags + app configs")
        return

    n = bulk_insert("cfg_feature_flags",
        ["flag_key","display_name","description","flag_type","default_value","current_value",
         "rollout_pct","is_active","changed_by_id","changed_at","created_at"],
        flag_rows, on_conflict="ON CONFLICT (flag_key) DO NOTHING")
    ok(f"Feature flags: {n}")

    # App Configs
    app_configs = [
        ("loyalty.stamp_per_order",         "loyalty", "integer",  1),
        ("loyalty.min_spend_for_stamp",      "loyalty", "integer",  25000),
        ("loyalty.points_per_stamp",         "loyalty", "integer",  10),
        ("payment.qris_surcharge_pct",       "payment", "float",    0.0),
        ("payment.cash_rounding",            "payment", "integer",  500),
        ("pos.session_timeout_minutes",      "pos",     "integer",  30),
        ("pos.enable_split_payment",         "pos",     "boolean",  True),
        ("stock.low_stock_alert_threshold",  "stock",   "float",    1.5),
        ("general.timezone",                 "general", "string",   "Asia/Jakarta"),
        ("general.currency",                 "general", "string",   "IDR"),
    ]
    cfg_rows = [(key, group, vtype, json.dumps(val), "", admin_id, datetime.now(), datetime.now())
                for key, group, vtype, val in app_configs]

    n = bulk_insert("cfg_app_configs",
        ["config_key","config_group","value_type","value","description","changed_by_id","created_at","updated_at"],
        cfg_rows, on_conflict="ON CONFLICT (config_key) DO NOTHING")
    ok(f"App configs: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "task_queue":       fill_task_queue,
    "search":           fill_search,
    "reporting":        fill_reporting,
    "api_gateway":      fill_api_gateway,
    "security":         fill_security,
    "events_calendar":  fill_events_calendar,
    "customer_support": fill_customer_support,
    "analytics_cube":   fill_analytics_cube,
    "config_store":     fill_config_store,
}

ORDER = ["task_queue","search","reporting","api_gateway","security",
         "events_calendar","customer_support","analytics_cube","config_store"]

NEW_TABLES = [
    # Task Queue
    "tq_task_definitions","tq_job_logs","tq_dead_letter_queue",
    # Search
    "search_index_configs","search_query_logs","search_synonyms",
    # Reporting
    "report_templates","report_generated",
    # API Gateway
    "api_keys","api_usage_logs","api_webhooks","api_webhook_deliveries",
    # Security
    "sec_login_events","sec_security_alerts",
    # Events
    "events_calendar","event_registrations",
    # Customer Support
    "cs_tickets","cs_ticket_messages",
    # Analytics Cube
    "analytics_conversion_funnel","analytics_product_affinity",
    # Config Store
    "cfg_feature_flags","cfg_app_configs",
]

def main():
    t_total = time.time()
    print("\n" + "═"*70)
    print("  KAFE NUSANTARA — World Building Phase 3 (ADJUSTED)")
    print("  9 modul baru yang compatible dengan existing schema")
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
        print(f"  {icon} {sec:<25} {res}")
    print("═"*70)

    if DRY_RUN:
        print("\n  Jalankan dengan --execute untuk menyimpan ke DB\n")

    print(f"\n  {'Tabel Baru':<48} {'Rows':>12}")
    print("─"*63)
    for t in NEW_TABLES:
        cnt     = row_count(t) if not DRY_RUN else "—"
        cnt_str = f"{cnt:,}" if isinstance(cnt, int) and cnt >= 0 else str(cnt)
        print(f"  {t:<48} {cnt_str:>12}")
    print(f"\n  Total tabel baru di phase 3: {len(NEW_TABLES)} tabel")
    print(f"  Total tabel keseluruhan: ~90+ tabel (seed 1+2+3)\n")


try:
    from django.core.management.base import BaseCommand
    class Command(BaseCommand):
        help = "Kafe Nusantara — World Building Phase 3 (Adjusted)"
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