"""
seed_expansion3.py
==================
KAFE NUSANTARA — World Building Phase 3
Ekspansi database tahap 3: domain yang belum ter-cover dari stack lengkap.

Stack yang di-leverage:
  Celery/Redis  → task_queue, celery_scheduled_jobs, background_job_logs
  Meilisearch   → search_index_config, search_query_logs, search_synonyms
  WeasyPrint    → report_templates, generated_reports, report_schedules
  DRF           → api_keys, api_rate_limits, api_usage_logs, webhooks
  Sentry        → error_tracking_summary, performance_snapshots
  django-axes   → login_attempts (extend), security_events
  Celery Beat   → extended job configs

MODUL BARU (10 modul):
  20. task_queue      — celery tasks, job logs, dead letter queue
  21. search          — Meilisearch index config, query logs, synonyms, analytics
  22. reporting       — report templates, schedules, generated reports, delivery logs
  23. api_gateway     — API keys, rate limits, usage logs, webhook configs
  24. security        — login events, security alerts, ip_whitelist, device_registry
  25. recipe_mgmt     — recipes v2, recipe_versions, costing, yield_tests
  26. events_calendar — events, event_registrations, event_revenue
  27. customer_support— tickets, ticket_messages, sla_configs, escalations
  28. analytics_cube  — pre-aggregated OLAP cubes: hourly, cohort, funnel
  29. config_store    — feature_flags, app_configs, location_configs, changelog

Cara pakai:
  python manage.py seed_expansion3 --execute
  python manage.py seed_expansion3 --execute --section=task_queue
  python manage.py seed_expansion3 --list-sections
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
    # From expansion2 if available
    CTX["employee_ids"] = [r[0] for r in q("SELECT id FROM hr_employees ORDER BY id")] \
                          if table_exists("hr_employees") else []
    CTX["variant_names"]= {r[0]: r[1] for r in q("SELECT id, name FROM lumra_config_productvariants ORDER BY id LIMIT 2000")} \
                          if True else {}
    ok(f"Context: {len(CTX['location_ids'])} locs, {len(CTX['customer_ids'])} customers, "
       f"{len(CTX['order_ids'])} orders, {len(CTX['employee_ids'])} employees")

today = date.today()

# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 20 — TASK QUEUE (Celery + Redis)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_task_queue(dry_run=False):
    head("MODUL 20 — TASK QUEUE (Celery Jobs, Scheduled Tasks, Dead Letter Queue)")

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
            'Definisi semua Celery task. Termasuk scheduled tasks (beat).
            Category: reporting, sync, notification, cleanup, analytics, procurement.';
        """, "tq_task_definitions"),

        ("""
        CREATE TABLE IF NOT EXISTS tq_job_logs (
            id              BIGSERIAL PRIMARY KEY,
            task_id         VARCHAR(36) NOT NULL,
            task_name       VARCHAR(120) NOT NULL,
            queue           VARCHAR(50) DEFAULT 'default',
            status          VARCHAR(20) DEFAULT 'pending',
            args_summary    TEXT DEFAULT '',
            kwargs_summary  TEXT DEFAULT '',
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
        COMMENT ON TABLE tq_job_logs IS
            'Log eksekusi setiap Celery task. Untuk monitoring dan debugging.';
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
        COMMENT ON TABLE tq_dead_letter_queue IS
            'Task yang gagal setelah max_retries. Perlu manual intervention.';
        CREATE INDEX IF NOT EXISTS idx_dlq_resolved ON tq_dead_letter_queue(is_resolved);
        """, "tq_dead_letter_queue"),

        ("""
        CREATE TABLE IF NOT EXISTS tq_scheduled_jobs (
            id              BIGSERIAL PRIMARY KEY,
            job_name        VARCHAR(100) UNIQUE NOT NULL,
            task_path       VARCHAR(255) NOT NULL,
            cron_expression VARCHAR(50) NOT NULL,
            description     TEXT DEFAULT '',
            queue           VARCHAR(50) DEFAULT 'default',
            kwargs          JSONB DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            last_run_at     TIMESTAMPTZ,
            next_run_at     TIMESTAMPTZ,
            last_status     VARCHAR(20) DEFAULT 'never_run',
            run_count       INT DEFAULT 0,
            fail_count      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_scheduled_jobs IS
            'Celery Beat scheduled jobs. Sinkron dengan django_celery_beat_periodictask.';
        """, "tq_scheduled_jobs"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Task Definitions
    tasks_data = [
        # (name, path, desc, category, queue, priority, max_retries, timeout, scheduled, cron)
        ("refresh_kpi_cache",        "lumra_config.tasks.refresh_kpi_cache",
         "Refresh semua KPI dashboard cache",                "analytics",     "high",    8,  3,  120, True,  "0 * * * *"),
        ("recalculate_rfm_scores",   "lumra_config.tasks.recalculate_rfm_scores",
         "Hitung ulang RFM score semua customer",            "analytics",     "default", 5,  2,  600, True,  "0 2 * * *"),
        ("generate_sales_daily",     "lumra_config.tasks.generate_sales_daily",
         "Agregasi penjualan harian ke report table",        "reporting",     "default", 6,  3,  300, True,  "5 0 * * *"),
        ("generate_sales_monthly",   "lumra_config.tasks.generate_sales_monthly",
         "Agregasi penjualan bulanan",                       "reporting",     "default", 6,  3,  300, True,  "10 0 1 * *"),
        ("sync_meilisearch_products","lumra_config.tasks.sync_meilisearch_products",
         "Sync produk ke Meilisearch index",                 "sync",          "default", 5,  3,  180, True,  "*/15 * * * *"),
        ("sync_meilisearch_customers","lumra_config.tasks.sync_meilisearch_customers",
         "Sync customer data ke Meilisearch",                "sync",          "default", 4,  3,  300, True,  "0 3 * * *"),
        ("send_promo_notifications", "lumra_config.tasks.send_promo_notifications",
         "Kirim notifikasi promo terjadwal",                 "notification",  "high",    7,  3,  120, True,  "0 9 * * *"),
        ("send_birthday_notifs",     "lumra_config.tasks.send_birthday_notifs",
         "Kirim ucapan ulang tahun ke customer",             "notification",  "default", 7,  3,  60,  True,  "0 7 * * *"),
        ("cleanup_old_job_logs",     "lumra_config.tasks.cleanup_old_job_logs",
         "Hapus job logs lebih dari 90 hari",                "cleanup",       "low",     3,  1,  300, True,  "0 4 * * 0"),
        ("cleanup_expired_tokens",   "lumra_config.tasks.cleanup_expired_tokens",
         "Hapus API tokens yang expired",                    "cleanup",       "low",     3,  1,  60,  True,  "0 4 * * *"),
        ("generate_pdf_report",      "lumra_config.tasks.generate_pdf_report",
         "Generate PDF report on-demand via WeasyPrint",     "reporting",     "default", 5,  2,  120, False, ""),
        ("process_webhook_event",    "lumra_config.tasks.process_webhook_event",
         "Proses outgoing webhook event",                    "webhook",       "high",    8,  5,  30,  False, ""),
        ("send_email_notification",  "lumra_config.tasks.send_email_notification",
         "Kirim email notifikasi",                           "notification",  "default", 6,  3,  30,  False, ""),
        ("update_stock_snapshot",    "lumra_config.tasks.update_stock_snapshot",
         "Update snapshot stok bulanan",                     "sync",          "default", 5,  2,  300, True,  "0 1 1 * *"),
        ("compute_demand_forecast",  "lumra_config.tasks.compute_demand_forecast",
         "Hitung demand forecast dengan moving average",     "analytics",     "default", 4,  2,  600, True,  "0 3 * * 1"),
        ("check_reorder_alerts",     "lumra_config.tasks.check_reorder_alerts",
         "Cek stok dan buat reorder alert jika perlu",       "procurement",   "default", 7,  3,  180, True,  "0 8 * * *"),
        ("send_shift_summary",       "lumra_config.tasks.send_shift_summary",
         "Kirim ringkasan shift ke manager",                 "reporting",     "default", 6,  2,  60,  True,  "0 23 * * *"),
        ("index_search_queries",     "lumra_config.tasks.index_search_queries",
         "Analisis query search untuk improve relevancy",    "analytics",     "low",     3,  1,  300, True,  "0 5 * * *"),
        ("auto_close_tickets",       "lumra_config.tasks.auto_close_tickets",
         "Auto-close ticket yang sudah resolved > 7 hari",  "cleanup",       "low",     3,  1,  120, True,  "0 6 * * *"),
        ("generate_payslips",        "lumra_config.tasks.generate_payslips",
         "Generate slip gaji bulanan PDF",                   "reporting",     "default", 5,  2,  600, True,  "0 10 25 * *"),
    ]
    task_rows = [(name, path, desc, cat, queue, priority, max_ret, timeout,
                  is_sched, cron, True, datetime.now())
                 for name, path, desc, cat, queue, priority, max_ret, timeout, is_sched, cron in tasks_data]

    if dry_run:
        log(f"[DRY RUN] {len(task_rows)} task defs + ~50k job logs + DLQ + scheduled jobs")
        return

    n = bulk_insert("tq_task_definitions",
        ["task_name","task_path","description","category","default_queue","priority",
         "max_retries","retry_backoff","timeout_seconds","is_scheduled","cron_expression",
         "is_active","created_at"],
        task_rows, on_conflict="ON CONFLICT (task_name) DO NOTHING")
    ok(f"Task definitions: {n}")

    # Job Logs (50k entries — 2 tahun ke belakang)
    task_names   = [t[0] for t in tasks_data]
    queue_names  = ["default","high","low","notification","reporting","sync","webhook","procurement"]
    workers      = [f"worker-{i}@lumra-prod" for i in range(1, 9)]
    statuses_w   = ["success","success","success","success","failure","revoked","retry"]
    statuses_wts = [60, 0, 0, 0, 15, 5, 20]

    log("Generating job logs...")
    job_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(50000):
        task_name  = RNG.choice(task_names)
        status     = RNG.choices(statuses_w, weights=statuses_wts)[0]
        created_at = datetime.now() - timedelta(
            days=RNG.randint(0, days_range),
            hours=RNG.randint(0, 23), minutes=RNG.randint(0, 59)
        )
        started_at    = created_at + timedelta(seconds=RNG.randint(0, 30))
        duration_ms   = RNG.randint(50, 30000) if status != "revoked" else 0
        completed_at  = started_at + timedelta(milliseconds=duration_ms) if duration_ms else None
        retry_count   = RNG.randint(0, 3) if status in ("failure","retry") else 0
        error_msg     = RNG.choice([
            "ConnectionError: Redis timeout",
            "OperationalError: DB connection failed",
            "ValueError: Invalid argument",
            "TimeoutError: Task exceeded timeout",
            ""
        ]) if status == "failure" else ""

        job_rows.append((
            rand_uuid(), task_name,
            RNG.choice(queue_names), status,
            f"args: [{RNG.randint(1,100)}]", "{}",
            RNG.choice(["schedule","api","manual","celery_beat"]),
            None, RNG.choice(workers),
            started_at, completed_at, duration_ms if duration_ms else None,
            "OK" if status == "success" else "",
            error_msg, retry_count, created_at
        ))

    n = bulk_insert("tq_job_logs",
        ["task_id","task_name","queue","status","args_summary","kwargs_summary",
         "triggered_by","triggered_by_id","worker_name","started_at","completed_at",
         "duration_ms","result_summary","error_message","retry_count","created_at"],
        job_rows, batch=3000)
    ok(f"Job logs: {n:,}")

    # Dead Letter Queue (failed setelah max retry)
    dlq_rows = []
    for _ in range(500):
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

    # Scheduled Jobs
    scheduled_tasks = [t for t in tasks_data if t[8]]  # is_scheduled == True
    sched_rows = []
    for name, path, desc, cat, queue, priority, _, _, _, cron in scheduled_tasks:
        last_run = datetime.now() - timedelta(hours=RNG.randint(1, 48))
        next_run = last_run + timedelta(hours=1)
        run_count = RNG.randint(50, 2000)
        sched_rows.append((
            f"beat_{name}", path, cron, desc, queue,
            json.dumps({}), True,
            last_run, next_run,
            RNG.choice(["success","success","success","failure"]),
            run_count, int(run_count * RNG.uniform(0, 0.05)),
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("tq_scheduled_jobs",
        ["job_name","task_path","cron_expression","description","queue","kwargs",
         "is_active","last_run_at","next_run_at","last_status","run_count","fail_count",
         "created_at","updated_at"],
        sched_rows, on_conflict="ON CONFLICT (job_name) DO NOTHING")
    ok(f"Scheduled jobs: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 21 — SEARCH (Meilisearch)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_search(dry_run=False):
    head("MODUL 21 — SEARCH (Meilisearch Index Config, Query Logs, Synonyms, Analytics)")

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
            sortable_attrs   JSONB DEFAULT '[]',
            displayed_attrs  JSONB DEFAULT '[]',
            ranking_rules    JSONB DEFAULT '["words","typo","proximity","attribute","sort","exactness"]',
            facets           JSONB DEFAULT '[]',
            total_documents INT DEFAULT 0,
            last_synced_at  TIMESTAMPTZ,
            sync_enabled    BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
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
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            results_count   INT DEFAULT 0,
            clicked_result_id BIGINT,
            response_ms     INT DEFAULT 0,
            filters_applied JSONB DEFAULT '{}',
            session_id      VARCHAR(40) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE search_query_logs IS
            'Log setiap pencarian: kata kunci, jumlah hasil, klik. Untuk search analytics.';
        CREATE INDEX IF NOT EXISTS idx_sq_index   ON search_query_logs(index_uid);
        CREATE INDEX IF NOT EXISTS idx_sq_query   ON search_query_logs(query_text);
        CREATE INDEX IF NOT EXISTS idx_sq_date    ON search_query_logs(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_sq_results ON search_query_logs(results_count);
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

        ("""
        CREATE TABLE IF NOT EXISTS search_analytics_daily (
            id              BIGSERIAL PRIMARY KEY,
            report_date     DATE NOT NULL,
            index_uid       VARCHAR(60) NOT NULL,
            total_searches  INT DEFAULT 0,
            unique_queries  INT DEFAULT 0,
            zero_result_searches INT DEFAULT 0,
            avg_response_ms NUMERIC(8,2) DEFAULT 0,
            top_queries     JSONB DEFAULT '[]',
            top_zero_results JSONB DEFAULT '[]',
            click_through_rate NUMERIC(5,3) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(report_date, index_uid)
        );
        COMMENT ON TABLE search_analytics_daily IS
            'Statistik pencarian harian. Dasar untuk improve ranking dan synonyms.';
        CREATE INDEX IF NOT EXISTS idx_sa_date ON search_analytics_daily(report_date DESC);
        """, "search_analytics_daily"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Index Configs
    indexes_data = [
        ("products",      "Produk & Menu",       "lumra_config_productvariants",
         ["name","description","category","tags"],
         ["category","is_active","price"],
         ["name","price","popularity"],
         ["id","name","price","category","image_url"],
         ["category","price_range"]),
        ("customers",     "Database Customer",   "lumra_config_customers",
         ["full_name","phone","email","member_id"],
         ["tier","is_active","created_at"],
         ["full_name","created_at","lifetime_spend"],
         ["id","full_name","phone","email","tier"],
         ["tier"]),
        ("orders",        "Riwayat Transaksi",   "lumra_config_orders",
         ["order_number","customer_name","notes"],
         ["status","payment_method","location_id","created_at"],
         ["created_at","paid_amount"],
         ["id","order_number","status","paid_amount","created_at"],
         ["status","payment_method","location_id"]),
        ("locations",     "Outpost Directory",   "lumra_config_locations",
         ["name","address","city","description"],
         ["is_active","city"],
         ["name","city"],
         ["id","name","address","city","latitude","longitude"],
         ["city"]),
        ("vendors",       "Daftar Vendor",       "lumra_config_vendors",
         ["name","contact_name","email","phone","address"],
         ["is_active"],
         ["name"],
         ["id","name","contact_name","email","phone"],
         []),
        ("promotions",    "Promo Aktif",         "lumra_sales_promotions",
         ["name","code","description"],
         ["is_active","promo_type","applicable_session"],
         ["name","discount_value"],
         ["id","code","name","discount_type","discount_value","valid_until"],
         ["promo_type","applicable_session"]),
        ("rfm_segments",  "Customer Segments",   "lumra_crm_rfm_scores",
         ["segment"],
         ["segment","r_score","f_score","m_score"],
         ["rfm_score","monetary_total"],
         ["customer_id","segment","rfm_score","monetary_total"],
         ["segment"]),
        ("assets",        "Asset Registry",      "maint_asset_registry",
         ["asset_name","brand","model","serial_number"],
         ["category","status","location_id"],
         ["asset_name","current_value"],
         ["id","asset_code","asset_name","category","status","location_id"],
         ["category","status"]) if table_exists("maint_asset_registry") else None,
    ]
    indexes_data = [x for x in indexes_data if x is not None]

    idx_rows = [(uid, dname, src, pkey,
                 json.dumps(srch), json.dumps(filt),
                 json.dumps(sort), json.dumps(disp),
                 json.dumps(["words","typo","proximity","attribute","sort","exactness"]),
                 json.dumps(facets),
                 RNG.randint(100, 50000),
                 datetime.now() - timedelta(minutes=RNG.randint(0, 60)),
                 True, datetime.now(), datetime.now())
                for uid, dname, src, srch, filt, sort, disp, facets in [
                    (uid, dn, src, srch, filt, sort, disp, facets)
                    for uid, dn, src, srch, filt, sort, disp, facets in indexes_data
                    # unpack properly
                ]
               ]

    # Rebuild properly
    idx_rows = []
    for row in indexes_data:
        uid, dn, src, srch, filt, sort_, disp, facets = row
        idx_rows.append((
            uid, dn, src, "id",
            json.dumps(srch), json.dumps(filt),
            json.dumps(sort_), json.dumps(disp),
            json.dumps(["words","typo","proximity","attribute","sort","exactness"]),
            json.dumps(facets),
            RNG.randint(100, 50000),
            datetime.now() - timedelta(minutes=RNG.randint(0, 60)),
            True, datetime.now(), datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(idx_rows)} indexes + query logs + synonyms + daily analytics")
        return

    n = bulk_insert("search_index_configs",
        ["index_uid","display_name","source_table","primary_key",
         "searchable_attrs","filterable_attrs","sortable_attrs","displayed_attrs",
         "ranking_rules","facets","total_documents","last_synced_at",
         "sync_enabled","created_at","updated_at"],
        idx_rows, on_conflict="ON CONFLICT (index_uid) DO NOTHING")
    ok(f"Search index configs: {n}")

    # Query Logs
    SAMPLE_QUERIES = [
        "es kopi susu","cold brew","americano","filter coffee","latte",
        "pastry","croissant","granola bowl","matcha","chocolate",
        "promo weekend","voucher","diskon","paket hemat","morning ration",
        "outpost bandung","outpost jakarta","buka jam berapa",
        "menu seasonal","grand reserve","single origin",
        "kopi ethiopia","kenya","flores","gayo","toraja",
        "cemara","kuningan","dago","sudirman","kemang",
    ]
    ZERO_RESULT = ["kopi boba","menu vegan","kopi decaf","delivery order","kopi kopi"]

    index_uids = [row[0] for row in indexes_data]
    customer_ids = CTX["customer_ids"]
    user_ids     = CTX["user_ids"]
    location_ids = CTX["location_ids"]

    ql_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(100000):
        is_zero = RNG.random() < 0.08
        query   = RNG.choice(ZERO_RESULT) if is_zero else RNG.choice(SAMPLE_QUERIES)
        n_results = 0 if is_zero else RNG.randint(1, 50)
        uid     = RNG.choice(index_uids)
        cid     = RNG.choice(customer_ids) if RNG.random() < 0.6 else None
        uid_user= RNG.choice(user_ids) if RNG.random() < 0.3 else None
        created = datetime.now() - timedelta(
            days=RNG.randint(0, days_range),
            hours=RNG.randint(0, 23)
        )
        ql_rows.append((
            uid, query, uid_user, cid,
            RNG.choice(location_ids) if RNG.random() < 0.5 else None,
            n_results,
            RNG.randint(1, 100) if n_results > 0 and RNG.random() < 0.3 else None,
            RNG.randint(2, 150),
            json.dumps({}), rand_hex(8), created
        ))

    n = bulk_insert("search_query_logs",
        ["index_uid","query_text","user_id","customer_id","location_id",
         "results_count","clicked_result_id","response_ms","filters_applied",
         "session_id","created_at"],
        ql_rows, batch=3000)
    ok(f"Search query logs: {n:,}")

    # Synonyms
    synonyms_data = {
        "products": {
            "es kopi susu": ["iced coffee latte","cold coffee milk","kopi susu dingin"],
            "cold brew":    ["kopi dingin","es kopi","cold coffee"],
            "americano":    ["black coffee","kopi hitam","long black"],
            "latte":        ["coffee latte","kopi susu","caffe latte"],
            "croissant":    ["roti tanduk","pastry"],
            "granola":      ["granola bowl","cereal","oatmeal"],
            "matcha":       ["green tea","teh hijau"],
            "single origin":["specialty coffee","kopi specialty","kopi premium"],
        },
        "customers": {
            "member":   ["pelanggan","customer"],
            "loyal":    ["setia","champion","reguler"],
        },
        "locations": {
            "outpost":  ["cabang","gerai","toko","kafe"],
            "bandung":  ["bdg","kota kembang"],
            "jakarta":  ["jkt","ibukota"],
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

    # Daily Analytics
    sa_rows = []
    TOP_QUERIES_SAMPLE = [
        [{"q": "es kopi susu", "count": 120}, {"q": "cold brew", "count": 80}],
        [{"q": "americano", "count": 60}, {"q": "latte", "count": 45}],
    ]
    for d in range(days_range):
        report_date = today - timedelta(days=d)
        for uid in index_uids:
            total  = RNG.randint(50, 2000)
            unique = int(total * RNG.uniform(0.3, 0.7))
            zero   = int(total * RNG.uniform(0.05, 0.15))
            ctr    = round(RNG.uniform(0.1, 0.5), 3)
            sa_rows.append((
                report_date, uid, total, unique, zero,
                round(RNG.uniform(10, 100), 2),
                json.dumps(RNG.choice(TOP_QUERIES_SAMPLE)),
                json.dumps([{"q": q, "count": RNG.randint(1,10)} for q in ZERO_RESULT[:2]]),
                ctr, datetime.now()
            ))

    n = bulk_insert("search_analytics_daily",
        ["report_date","index_uid","total_searches","unique_queries",
         "zero_result_searches","avg_response_ms","top_queries","top_zero_results",
         "click_through_rate","created_at"],
        sa_rows, batch=3000,
        on_conflict="ON CONFLICT (report_date, index_uid) DO NOTHING")
    ok(f"Search analytics daily: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 22 — REPORTING (WeasyPrint PDF Reports)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_reporting(dry_run=False):
    head("MODUL 22 — REPORTING (Templates, Schedules, Generated Reports, Delivery)")

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
        CREATE TABLE IF NOT EXISTS report_schedules (
            id              BIGSERIAL PRIMARY KEY,
            template_id     BIGINT NOT NULL REFERENCES report_templates(id),
            schedule_name   VARCHAR(100) NOT NULL,
            cron_expression VARCHAR(50) NOT NULL,
            parameters      JSONB DEFAULT '{}',
            recipients      JSONB DEFAULT '[]',
            delivery_method VARCHAR(20) DEFAULT 'email',
            is_active       BOOLEAN DEFAULT TRUE,
            last_run_at     TIMESTAMPTZ,
            next_run_at     TIMESTAMPTZ,
            run_count       INT DEFAULT 0,
            created_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_schedules IS
            'Jadwal otomatis generate + kirim laporan. Delivery: email, slack, sftp.';
        """, "report_schedules"),

        ("""
        CREATE TABLE IF NOT EXISTS report_generated (
            id              BIGSERIAL PRIMARY KEY,
            template_id     BIGINT REFERENCES report_templates(id),
            schedule_id     BIGINT REFERENCES report_schedules(id),
            report_title    VARCHAR(200) NOT NULL,
            parameters      JSONB DEFAULT '{}',
            file_name       VARCHAR(255) NOT NULL DEFAULT '',
            file_size_kb    INT DEFAULT 0,
            page_count      INT DEFAULT 1,
            status          VARCHAR(20) DEFAULT 'generating',
            generated_by_id BIGINT REFERENCES auth_user(id),
            generation_ms   INT DEFAULT 0,
            error_message   TEXT DEFAULT '',
            expires_at      TIMESTAMPTZ,
            download_count  INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_generated IS
            'Log setiap laporan yang di-generate. File disimpan di storage.';
        CREATE INDEX IF NOT EXISTS idx_rg_template ON report_generated(template_id);
        CREATE INDEX IF NOT EXISTS idx_rg_date     ON report_generated(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_rg_status   ON report_generated(status);
        """, "report_generated"),

        ("""
        CREATE TABLE IF NOT EXISTS report_delivery_log (
            id              BIGSERIAL PRIMARY KEY,
            report_id       BIGINT NOT NULL REFERENCES report_generated(id),
            recipient       VARCHAR(150) NOT NULL,
            delivery_method VARCHAR(20) DEFAULT 'email',
            status          VARCHAR(20) DEFAULT 'sent',
            sent_at         TIMESTAMPTZ DEFAULT NOW(),
            opened_at       TIMESTAMPTZ,
            error_message   TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_delivery_log IS 'Log pengiriman laporan ke penerima.';
        CREATE INDEX IF NOT EXISTS idx_rdl_report ON report_delivery_log(report_id);
        """, "report_delivery_log"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Templates
    templates_data = [
        ("DAILY_SALES",       "Laporan Penjualan Harian",         "operational",
         "reports/daily_sales.html",     "pdf",  {"location_id": None, "date": "today"}),
        ("WEEKLY_SALES",      "Laporan Penjualan Mingguan",       "operational",
         "reports/weekly_sales.html",    "pdf",  {"location_id": None, "week_offset": 0}),
        ("MONTHLY_SALES",     "Laporan Penjualan Bulanan",        "operational",
         "reports/monthly_sales.html",   "pdf",  {"year": None, "month": None}),
        ("PAYSLIP",           "Slip Gaji Karyawan",               "hr",
         "reports/payslip.html",         "pdf",  {"employee_id": None, "period": None}),
        ("PAYROLL_SUMMARY",   "Rekapitulasi Payroll Bulanan",     "hr",
         "reports/payroll_summary.html", "pdf",  {"period": None, "location_id": None}),
        ("INVENTORY_STOCK",   "Laporan Stok Inventaris",          "operational",
         "reports/inventory_stock.html", "pdf",  {"location_id": None, "as_of_date": "today"}),
        ("PO_DOCUMENT",       "Dokumen Purchase Order",           "procurement",
         "reports/purchase_order.html",  "pdf",  {"po_id": None}),
        ("GRN_DOCUMENT",      "Dokumen Good Receipt Note",        "procurement",
         "reports/grn.html",             "pdf",  {"grn_id": None}),
        ("CUSTOMER_STATEMENT","Laporan Transaksi Customer",       "crm",
         "reports/customer_statement.html","pdf",{"customer_id": None, "months": 3}),
        ("RFM_REPORT",        "Analisis RFM Customer",            "analytics",
         "reports/rfm_analysis.html",   "pdf",  {"segment": None}),
        ("WASTE_REPORT",      "Laporan Waste Produksi",           "operational",
         "reports/waste_report.html",    "pdf",  {"location_id": None, "period": None}),
        ("FINANCIAL_SUMMARY", "Ringkasan Keuangan Bulanan",       "financial",
         "reports/financial_summary.html","pdf", {"year": None, "month": None}),
        ("BUDGET_VS_ACTUAL",  "Realisasi vs Anggaran",            "financial",
         "reports/budget_actual.html",  "pdf",  {"year": None, "quarter": None}),
        ("SUPPLIER_SCORECARD","Supplier Scorecard Report",        "procurement",
         "reports/supplier_scorecard.html","pdf",{"vendor_id": None, "period": None}),
        ("SHIFT_SUMMARY",     "Ringkasan Shift Harian",           "operational",
         "reports/shift_summary.html",  "pdf",  {"location_id": None, "date": "today"}),
        ("NPS_DASHBOARD",     "Net Promoter Score Dashboard",     "analytics",
         "reports/nps_dashboard.html",  "pdf",  {"period": None}),
        ("TRAINING_PROGRESS", "Progress Training Karyawan",       "hr",
         "reports/training_progress.html","pdf", {"location_id": None}),
        ("ASSET_REGISTER",    "Daftar Aset Per Lokasi",           "operational",
         "reports/asset_register.html", "pdf",  {"location_id": None}),
        ("MENU_PERFORMANCE",  "Menu Engineering Report",          "analytics",
         "reports/menu_performance.html","pdf",  {"location_id": None, "period": None}),
        ("CONSOLIDATED_P&L",  "Laporan Laba Rugi Konsolidasi",    "financial",
         "reports/pnl_consolidated.html","pdf",  {"year": None, "month": None}),
    ]
    tmpl_rows = [(code, title, "", rtype, tpath, fmt,
                  json.dumps(params), True, "manager", datetime.now())
                 for code, title, rtype, tpath, fmt, params in templates_data]

    if dry_run:
        log(f"[DRY RUN] {len(tmpl_rows)} templates + schedules + generated reports + delivery logs")
        return

    n = bulk_insert("report_templates",
        ["code","title","description","report_type","template_path","output_format",
         "parameters","is_active","requires_role","created_at"],
        tmpl_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Report templates: {n}")

    # Schedules
    tmpl_ids    = [r[0] for r in q("SELECT id FROM report_templates ORDER BY id")]
    admin_id    = CTX["admin_id"]
    user_ids    = CTX["user_ids"]
    sched_rows  = []
    RECIPS      = ["manager@kafenusantara.id","ops@kafenusantara.id","cfo@kafenusantara.id"]
    for tid in tmpl_ids[:10]:
        last_run = datetime.now() - timedelta(hours=RNG.randint(1, 72))
        sched_rows.append((
            tid, f"auto_schedule_{tid}",
            RNG.choice(["0 7 * * *","0 8 * * 1","0 9 1 * *"]),
            json.dumps({"location_id": None}),
            json.dumps(RNG.sample(RECIPS, RNG.randint(1, 3))),
            "email", True,
            last_run, last_run + timedelta(days=1),
            RNG.randint(10, 200),
            RNG.choice(user_ids) if user_ids else admin_id,
            datetime.now()
        ))

    n = bulk_insert("report_schedules",
        ["template_id","schedule_name","cron_expression","parameters","recipients",
         "delivery_method","is_active","last_run_at","next_run_at","run_count",
         "created_by_id","created_at"],
        sched_rows)
    ok(f"Report schedules: {n}")

    # Generated Reports
    sched_ids  = [r[0] for r in q("SELECT id FROM report_schedules ORDER BY id")]
    gen_rows   = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(5000):
        tid      = RNG.choice(tmpl_ids)
        sid      = RNG.choice(sched_ids) if sched_ids else None
        status   = RNG.choices(["completed","completed","failed","generating"],
                               weights=[85, 0, 10, 5])[0]
        gen_ms   = RNG.randint(500, 15000) if status == "completed" else 0
        created  = datetime.now() - timedelta(days=RNG.randint(0, days_range))
        gen_rows.append((
            tid, sid,
            f"Laporan #{RNG.randint(1000,9999)} - {created.strftime('%Y-%m-%d')}",
            json.dumps({"period": created.strftime("%Y-%m")}),
            f"report_{rand_hex(8)}.pdf",
            RNG.randint(50, 5000),
            RNG.randint(1, 50),
            status,
            RNG.choice(user_ids) if user_ids else admin_id,
            gen_ms, "",
            created + timedelta(days=30),
            RNG.randint(0, 20), created
        ))

    n = bulk_insert("report_generated",
        ["template_id","schedule_id","report_title","parameters","file_name",
         "file_size_kb","page_count","status","generated_by_id","generation_ms",
         "error_message","expires_at","download_count","created_at"],
        gen_rows, batch=3000)
    ok(f"Generated reports: {n:,}")

    # Delivery Logs
    rpt_ids    = [r[0] for r in q("SELECT id FROM report_generated WHERE status='completed' ORDER BY id LIMIT 3000")]
    dlv_rows   = []
    for rid in rpt_ids:
        n_recip = RNG.randint(1, 3)
        for recip in RNG.sample(RECIPS, min(n_recip, len(RECIPS))):
            sent  = datetime.now() - timedelta(days=RNG.randint(0, 90))
            status= RNG.choices(["sent","delivered","opened","failed"],
                                weights=[15, 40, 40, 5])[0]
            dlv_rows.append((
                rid, recip, "email", status, sent,
                sent + timedelta(minutes=RNG.randint(1, 60)) if status == "opened" else None,
                "", sent
            ))

    n = bulk_insert("report_delivery_log",
        ["report_id","recipient","delivery_method","status","sent_at",
         "opened_at","error_message","created_at"],
        dlv_rows, batch=3000)
    ok(f"Report delivery logs: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 23 — API GATEWAY (DRF — API Keys, Rate Limits, Webhooks)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_api_gateway(dry_run=False):
    head("MODUL 23 — API GATEWAY (API Keys, Rate Limits, Usage Logs, Webhooks)")

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
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_keys IS
            'API Keys untuk akses DRF endpoints. Scopes: read, write, admin, webhook.';
        CREATE INDEX IF NOT EXISTS idx_api_key_owner ON api_keys(owner_id);
        """, "api_keys"),

        ("""
        CREATE TABLE IF NOT EXISTS api_rate_limit_tiers (
            id              BIGSERIAL PRIMARY KEY,
            tier_name       VARCHAR(20) UNIQUE NOT NULL,
            requests_per_minute INT DEFAULT 60,
            requests_per_hour   INT DEFAULT 1000,
            requests_per_day    INT DEFAULT 10000,
            burst_limit         INT DEFAULT 100,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_rate_limit_tiers IS
            'Tier rate limiting untuk API keys. Tier: free, standard, premium, internal.';
        """, "api_rate_limit_tiers"),

        ("""
        CREATE TABLE IF NOT EXISTS api_usage_logs (
            id              BIGSERIAL PRIMARY KEY,
            api_key_id      BIGINT REFERENCES api_keys(id),
            endpoint        VARCHAR(200) NOT NULL,
            method          VARCHAR(10) NOT NULL DEFAULT 'GET',
            status_code     SMALLINT NOT NULL DEFAULT 200,
            response_ms     INT DEFAULT 0,
            request_size_b  INT DEFAULT 0,
            response_size_b INT DEFAULT 0,
            ip_address      INET,
            user_agent      VARCHAR(200) DEFAULT '',
            error_code      VARCHAR(30) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_usage_logs IS
            'Log setiap API request. Untuk billing, analytics, debugging.';
        CREATE INDEX IF NOT EXISTS idx_api_usage_key    ON api_usage_logs(api_key_id);
        CREATE INDEX IF NOT EXISTS idx_api_usage_date   ON api_usage_logs(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage_logs(endpoint);
        CREATE INDEX IF NOT EXISTS idx_api_usage_status ON api_usage_logs(status_code);
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
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
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
            response_body   TEXT DEFAULT '',
            duration_ms     INT DEFAULT 0,
            attempt_number  SMALLINT DEFAULT 1,
            status          VARCHAR(20) DEFAULT 'pending',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_webhook_deliveries IS
            'Log pengiriman webhook. Retry otomatis 3x dengan exponential backoff.';
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_webhook ON api_webhook_deliveries(webhook_id);
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_status  ON api_webhook_deliveries(status);
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_date    ON api_webhook_deliveries(created_at DESC);
        """, "api_webhook_deliveries"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]

    # Rate Limit Tiers
    tier_rows = [
        ("free",      30,   500,    5000,   50),
        ("standard",  60,   1000,   10000,  100),
        ("premium",   300,  10000,  100000, 500),
        ("internal",  1000, 100000, 1000000,2000),
    ]
    if not dry_run:
        n = bulk_insert("api_rate_limit_tiers",
            ["tier_name","requests_per_minute","requests_per_hour","requests_per_day","burst_limit","is_active","created_at"],
            [(t, rpm, rph, rpd, burst, True, datetime.now()) for t, rpm, rph, rpd, burst in tier_rows],
            on_conflict="ON CONFLICT (tier_name) DO NOTHING")
        ok(f"Rate limit tiers: {n}")

    # API Keys
    SCOPES_SETS = [
        ["read"],
        ["read","write"],
        ["read","write","webhook"],
        ["read","write","admin","webhook"],
        ["read","analytics"],
    ]
    APP_NAMES = [
        "Lumra POS Mobile","Lumra Dashboard Web","Lumra Manager App",
        "Inventory Scanner","Third Party Integration","Analytics Platform",
        "WhatsApp Bot","Instagram Integration","Delivery Partner API",
    ]
    key_rows = []
    for i in range(50):
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
            RNG.choice(["standard","standard","premium","internal","free"]),
            RNG.random() > 0.1,
            created + timedelta(days=365) if RNG.random() < 0.3 else None,
            datetime.now() - timedelta(hours=RNG.randint(0, 720)),
            RNG.randint(100, 1000000),
            created, created
        ))

    if dry_run:
        log(f"[DRY RUN] 50 API keys + usage logs + webhooks + deliveries")
        return

    n = bulk_insert("api_keys",
        ["key_id","key_hash","name","owner_id","scopes","allowed_ips",
         "rate_limit_tier","is_active","expires_at","last_used_at",
         "total_requests","created_at","updated_at"],
        key_rows, on_conflict="ON CONFLICT (key_id) DO NOTHING")
    ok(f"API keys: {n}")

    # Usage Logs (100k entries)
    key_ids   = [r[0] for r in q("SELECT id FROM api_keys ORDER BY id")]
    ENDPOINTS = [
        "/api/v1/orders/","/api/v1/orders/{id}/","/api/v1/products/",
        "/api/v1/customers/","/api/v1/customers/{id}/","/api/v1/inventory/stock/",
        "/api/v1/reports/sales-daily/","/api/v1/promotions/","/api/v1/locations/",
        "/api/v1/rfm/segments/","/api/v1/kpi/dashboard/","/api/v1/auth/token/",
        "/api/v1/search/","/api/v1/webhooks/","/api/v1/notifications/",
    ]
    METHODS   = ["GET","GET","GET","POST","PUT","PATCH","DELETE"]
    STATUSES  = [200,200,200,201,400,401,403,404,429,500]
    STAT_WTS  = [60,0,0,15,8,5,3,5,2,2]
    IPS       = [f"10.{RNG.randint(0,5)}.{RNG.randint(0,255)}.{RNG.randint(1,254)}" for _ in range(20)]

    usage_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(100000):
        created = datetime.now() - timedelta(
            days=RNG.randint(0, days_range), hours=RNG.randint(0, 23)
        )
        status = RNG.choices(STATUSES, weights=STAT_WTS)[0]
        usage_rows.append((
            RNG.choice(key_ids) if key_ids else None,
            RNG.choice(ENDPOINTS),
            RNG.choice(METHODS),
            status,
            RNG.randint(5, 2000),
            RNG.randint(100, 5000),
            RNG.randint(200, 50000),
            RNG.choice(IPS),
            "LumraClient/1.0",
            "" if status < 400 else RNG.choice(["RATE_LIMIT","NOT_FOUND","AUTH_FAILED","VALIDATION"]),
            created
        ))

    n = bulk_insert("api_usage_logs",
        ["api_key_id","endpoint","method","status_code","response_ms",
         "request_size_b","response_size_b","ip_address","user_agent",
         "error_code","created_at"],
        usage_rows, batch=3000)
    ok(f"API usage logs: {n:,}")

    # Webhooks
    EVENTS_SETS = [
        ["order.completed","order.cancelled"],
        ["stock.low","stock.out"],
        ["payroll.processed"],
        ["customer.registered","customer.tier_upgrade"],
        ["report.generated"],
    ]
    wh_rows = []
    for i in range(20):
        uid = RNG.choice(user_ids) if user_ids else admin_id
        wh_rows.append((
            f"WH{rand_hex(8).upper()}", f"Webhook #{i+1}",
            uid, f"https://hooks.example{i}.com/lumra",
            rand_hex(32), RNG.choice(EVENTS_SETS), True,
            RNG.randint(0, 10),
            datetime.now() - timedelta(hours=RNG.randint(0, 720)),
            RNG.choice(["success","success","failed"]),
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("api_webhooks",
        ["webhook_id","name","owner_id","target_url","secret_key","events",
         "is_active","failure_count","last_triggered_at","last_status","created_at","updated_at"],
        wh_rows, on_conflict="ON CONFLICT (webhook_id) DO NOTHING")
    ok(f"Webhooks: {n}")

    # Webhook Deliveries
    wh_ids   = [r[0] for r in q("SELECT id FROM api_webhooks ORDER BY id")]
    WH_EVENTS= ["order.completed","stock.low","customer.registered","report.generated","payroll.processed"]
    wdlv_rows= []
    for _ in range(10000):
        wid    = RNG.choice(wh_ids) if wh_ids else 1
        status = RNG.choices(["delivered","delivered","failed","pending"],
                             weights=[75, 0, 20, 5])[0]
        created= datetime.now() - timedelta(days=RNG.randint(0, 90))
        wdlv_rows.append((
            wid, RNG.choice(WH_EVENTS),
            json.dumps({"event": "test", "data": {"id": RNG.randint(1,1000)}}),
            200 if status == "delivered" else RNG.choice([400, 500, None]),
            "{}" if status == "delivered" else "Connection refused",
            RNG.randint(50, 3000),
            RNG.randint(1, 3),
            status, created
        ))

    n = bulk_insert("api_webhook_deliveries",
        ["webhook_id","event_type","payload","response_code","response_body",
         "duration_ms","attempt_number","status","created_at"],
        wdlv_rows, batch=3000)
    ok(f"Webhook deliveries: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 24 — SECURITY (Login Events, Alerts, IP Whitelist)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_security(dry_run=False):
    head("MODUL 24 — SECURITY (Login Events, Security Alerts, Device Registry)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS sec_login_events (
            id              BIGSERIAL PRIMARY KEY,
            user_id         BIGINT REFERENCES auth_user(id),
            username_attempt VARCHAR(150) NOT NULL DEFAULT '',
            event_type      VARCHAR(20) NOT NULL DEFAULT 'login_success',
            ip_address      INET NOT NULL,
            user_agent      TEXT DEFAULT '',
            device_fingerprint VARCHAR(64) DEFAULT '',
            location_hint   VARCHAR(100) DEFAULT '',
            is_suspicious   BOOLEAN DEFAULT FALSE,
            failure_reason  VARCHAR(50) DEFAULT '',
            session_id      VARCHAR(40) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_login_events IS
            'Log semua login attempt. Event: login_success, login_failed, logout, password_reset.
            Terintegrasi dengan django-axes.';
        CREATE INDEX IF NOT EXISTS idx_login_user ON sec_login_events(user_id);
        CREATE INDEX IF NOT EXISTS idx_login_ip   ON sec_login_events(ip_address);
        CREATE INDEX IF NOT EXISTS idx_login_date ON sec_login_events(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_login_susp ON sec_login_events(is_suspicious) WHERE is_suspicious=TRUE;
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
            related_data    JSONB DEFAULT '{}',
            status          VARCHAR(20) DEFAULT 'open',
            acknowledged_by_id BIGINT REFERENCES auth_user(id),
            acknowledged_at TIMESTAMPTZ,
            resolved_at     TIMESTAMPTZ,
            auto_blocked    BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_security_alerts IS
            'Alert keamanan: brute force, unusual location, mass download, privilege escalation.';
        CREATE INDEX IF NOT EXISTS idx_sec_alert_type ON sec_security_alerts(alert_type);
        CREATE INDEX IF NOT EXISTS idx_sec_alert_sev  ON sec_security_alerts(severity);
        CREATE INDEX IF NOT EXISTS idx_sec_alert_date ON sec_security_alerts(created_at DESC);
        """, "sec_security_alerts"),

        ("""
        CREATE TABLE IF NOT EXISTS sec_ip_whitelist (
            id              BIGSERIAL PRIMARY KEY,
            ip_address      INET NOT NULL,
            ip_range        VARCHAR(20) DEFAULT '',
            label           VARCHAR(100) NOT NULL DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            added_by_id     BIGINT REFERENCES auth_user(id),
            expires_at      DATE,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_ip_whitelist IS
            'IP yang di-whitelist untuk akses admin/API tanpa rate limit.';
        """, "sec_ip_whitelist"),

        ("""
        CREATE TABLE IF NOT EXISTS sec_device_registry (
            id              BIGSERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL REFERENCES auth_user(id),
            device_id       VARCHAR(64) UNIQUE NOT NULL,
            device_name     VARCHAR(100) DEFAULT '',
            device_type     VARCHAR(20) DEFAULT 'mobile',
            os              VARCHAR(30) DEFAULT '',
            browser         VARCHAR(30) DEFAULT '',
            is_trusted      BOOLEAN DEFAULT FALSE,
            is_active       BOOLEAN DEFAULT TRUE,
            first_seen_at   TIMESTAMPTZ DEFAULT NOW(),
            last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
            last_ip         INET,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_device_registry IS
            'Device yang pernah dipakai login per user. Basis MFA dan suspicious login detection.';
        CREATE INDEX IF NOT EXISTS idx_device_user ON sec_device_registry(user_id);
        """, "sec_device_registry"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]
    days_range = (today - CTX["min_date"]).days

    IPS = [f"{RNG.randint(1,223)}.{RNG.randint(0,255)}.{RNG.randint(0,255)}.{RNG.randint(1,254)}"
           for _ in range(100)]
    INTERNAL_IPS = [f"10.0.{RNG.randint(0,5)}.{RNG.randint(1,254)}" for _ in range(20)]
    UAS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit LumraPOS/3.2",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
        "LumraManager/2.1 (Android 14; Samsung Galaxy)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14) Safari/17",
        "LumraInventory/1.5 (Sunmi T2 Pro)",
    ]

    # Login Events
    login_rows = []
    for _ in range(30000):
        uid    = RNG.choice(user_ids) if user_ids else admin_id
        etype  = RNG.choices(
            ["login_success","login_success","login_success","login_failed","logout","password_reset"],
            weights=[60, 0, 0, 20, 15, 5]
        )[0]
        is_sus = etype == "login_failed" and RNG.random() < 0.3
        created= datetime.now() - timedelta(
            days=RNG.randint(0, days_range), hours=RNG.randint(0, 23)
        )
        login_rows.append((
            uid if etype != "login_failed" else None,
            f"user_{uid}" if uid else "unknown",
            etype,
            RNG.choice(IPS + INTERNAL_IPS),
            RNG.choice(UAS),
            rand_hex(16),
            RNG.choice(["Bandung, ID","Jakarta, ID","Unknown","Surabaya, ID",""]),
            is_sus,
            "" if etype != "login_failed" else RNG.choice(["wrong_password","account_locked","ip_blocked"]),
            rand_hex(8), created
        ))

    if dry_run:
        log(f"[DRY RUN] login events, security alerts, IP whitelist, device registry")
        return

    n = bulk_insert("sec_login_events",
        ["user_id","username_attempt","event_type","ip_address","user_agent",
         "device_fingerprint","location_hint","is_suspicious","failure_reason",
         "session_id","created_at"],
        login_rows, batch=3000)
    ok(f"Login events: {n:,}")

    # Security Alerts
    ALERT_TYPES = ["brute_force","unusual_location","mass_data_export",
                   "privilege_escalation","api_abuse","account_takeover"]
    SEVERITIES  = ["low","medium","high","critical"]
    alert_rows  = []
    for _ in range(200):
        atype   = RNG.choice(ALERT_TYPES)
        sev     = RNG.choices(SEVERITIES, weights=[30,40,20,10])[0]
        created = datetime.now() - timedelta(days=RNG.randint(0, 90))
        status  = RNG.choices(["open","acknowledged","resolved"],weights=[30,30,40])[0]
        uid     = RNG.choice(user_ids) if user_ids else admin_id
        alert_rows.append((
            atype, sev,
            f"[{sev.upper()}] {atype.replace('_',' ').title()} detected",
            f"Suspicious activity detected from IP {RNG.choice(IPS)}",
            uid,
            RNG.choice(IPS),
            json.dumps({"attempts": RNG.randint(5, 50), "ip": RNG.choice(IPS)}),
            status,
            admin_id if status != "open" else None,
            created + timedelta(hours=2) if status != "open" else None,
            created + timedelta(hours=24) if status == "resolved" else None,
            sev == "critical" and RNG.random() < 0.5,
            created
        ))

    n = bulk_insert("sec_security_alerts",
        ["alert_type","severity","title","description","affected_user_id","ip_address",
         "related_data","status","acknowledged_by_id","acknowledged_at","resolved_at",
         "auto_blocked","created_at"],
        alert_rows)
    ok(f"Security alerts: {n}")

    # IP Whitelist
    wl_rows = [(ip, "", f"Internal Network {i}", True, admin_id, None, "", datetime.now())
               for i, ip in enumerate(INTERNAL_IPS)]
    n = bulk_insert("sec_ip_whitelist",
        ["ip_address","ip_range","label","is_active","added_by_id","expires_at","notes","created_at"],
        wl_rows)
    ok(f"IP whitelist: {n}")

    # Device Registry
    dev_rows = []
    DEVICES   = ["mobile","mobile","tablet","desktop","pos_terminal"]
    OS_LIST   = ["iOS 17","Android 14","Android 13","Windows 11","macOS 14","HarmonyOS 4"]
    BROWSERS  = ["LumraPOS","Chrome","Safari","Firefox","LumraManager"]
    for uid in user_ids:
        for _ in range(RNG.randint(1, 4)):
            dev_rows.append((
                uid, rand_hex(16),
                RNG.choice(["iPhone 15","Samsung S24","Sunmi T2","MacBook Pro","iPad Air"]),
                RNG.choice(DEVICES),
                RNG.choice(OS_LIST), RNG.choice(BROWSERS),
                RNG.random() < 0.7, True,
                datetime.now() - timedelta(days=RNG.randint(30, 365)),
                datetime.now() - timedelta(hours=RNG.randint(0, 72)),
                RNG.choice(INTERNAL_IPS),
                datetime.now() - timedelta(days=RNG.randint(30, 365))
            ))

    n = bulk_insert("sec_device_registry",
        ["user_id","device_id","device_name","device_type","os","browser",
         "is_trusted","is_active","first_seen_at","last_seen_at","last_ip","created_at"],
        dev_rows, on_conflict="ON CONFLICT (device_id) DO NOTHING")
    ok(f"Device registry: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 25 — RECIPE MANAGEMENT V2
# ═══════════════════════════════════════════════════════════════════════════════

def fill_recipe_mgmt(dry_run=False):
    head("MODUL 25 — RECIPE MANAGEMENT V2 (Versions, Costing, Yield Tests)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS recipe_v2 (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            name            VARCHAR(150) NOT NULL,
            version         SMALLINT DEFAULT 1,
            category        VARCHAR(40) DEFAULT 'beverage',
            serving_size    NUMERIC(8,2) DEFAULT 1,
            serving_unit    VARCHAR(20) DEFAULT 'cup',
            preparation_time_min INT DEFAULT 5,
            is_current      BOOLEAN DEFAULT TRUE,
            is_active       BOOLEAN DEFAULT TRUE,
            approved_by_id  BIGINT REFERENCES auth_user(id),
            approved_at     TIMESTAMPTZ,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_v2 IS
            'Resep produk dengan versioning. is_current=True = versi aktif dipakai barista.';
        CREATE INDEX IF NOT EXISTS idx_recipe_variant ON recipe_v2(variant_id);
        CREATE INDEX IF NOT EXISTS idx_recipe_current ON recipe_v2(is_current) WHERE is_current=TRUE;
        """, "recipe_v2"),

        ("""
        CREATE TABLE IF NOT EXISTS recipe_v2_ingredients (
            id              BIGSERIAL PRIMARY KEY,
            recipe_id       BIGINT NOT NULL REFERENCES recipe_v2(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            ingredient_name VARCHAR(100) NOT NULL DEFAULT '',
            quantity        NUMERIC(10,3) NOT NULL,
            unit            VARCHAR(20) NOT NULL DEFAULT 'gram',
            preparation     VARCHAR(50) DEFAULT '',
            is_optional     BOOLEAN DEFAULT FALSE,
            sort_order      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_v2_ingredients IS
            'Bahan-bahan per resep dengan kuantitas spesifik.';
        CREATE INDEX IF NOT EXISTS idx_ri_recipe ON recipe_v2_ingredients(recipe_id);
        """, "recipe_v2_ingredients"),

        ("""
        CREATE TABLE IF NOT EXISTS recipe_costing (
            id              BIGSERIAL PRIMARY KEY,
            recipe_id       BIGINT NOT NULL UNIQUE REFERENCES recipe_v2(id),
            total_ingredient_cost NUMERIC(12,2) DEFAULT 0,
            packaging_cost  NUMERIC(10,2) DEFAULT 0,
            labor_cost_allocation NUMERIC(10,2) DEFAULT 0,
            overhead_allocation   NUMERIC(10,2) DEFAULT 0,
            total_cogs      NUMERIC(12,2) DEFAULT 0,
            selling_price   NUMERIC(12,2) DEFAULT 0,
            gross_margin    NUMERIC(12,2) DEFAULT 0,
            margin_pct      NUMERIC(6,2) DEFAULT 0,
            break_even_qty  INT DEFAULT 0,
            costed_at       TIMESTAMPTZ DEFAULT NOW(),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_costing IS
            'Kalkulasi COGS per resep. Dasar penetapan harga jual.';
        """, "recipe_costing"),

        ("""
        CREATE TABLE IF NOT EXISTS recipe_yield_tests (
            id              BIGSERIAL PRIMARY KEY,
            recipe_id       BIGINT NOT NULL REFERENCES recipe_v2(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            tester_id       BIGINT REFERENCES auth_user(id),
            test_date       DATE NOT NULL,
            batch_size      INT DEFAULT 1,
            expected_output NUMERIC(10,3) DEFAULT 0,
            actual_output   NUMERIC(10,3) DEFAULT 0,
            yield_pct       NUMERIC(5,2) DEFAULT 0,
            quality_score   SMALLINT DEFAULT 5 CHECK(quality_score BETWEEN 1 AND 10),
            taste_notes     TEXT DEFAULT '',
            visual_notes    TEXT DEFAULT '',
            adjustments     TEXT DEFAULT '',
            passed          BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_yield_tests IS
            'Uji yield/konsistensi resep. Dilakukan saat recipe baru atau ada update bahan.';
        """, "recipe_yield_tests"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    variant_ids  = CTX["variant_ids"]
    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    CATEGORIES   = ["beverage_hot","beverage_cold","beverage_specialty","food_pastry","food_savory","food_dessert"]
    SERVING_UNITS= ["cup","glass","bowl","plate","piece","portion"]
    INGREDIENTS_POOL = [
        ("Espresso Shot",   "ml",  20,  40),
        ("Whole Milk",      "ml",  100, 250),
        ("Oat Milk",        "ml",  100, 250),
        ("Simple Syrup",    "ml",  10,  30),
        ("Ice",             "gram",100, 250),
        ("Coffee Beans",    "gram",18,  22),
        ("Chocolate Powder","gram",15,  25),
        ("Vanilla Extract", "ml",  2,   5),
        ("Caramel Sauce",   "ml",  10,  20),
        ("Whipped Cream",   "gram",20,  40),
        ("Cold Brew",       "ml",  150, 200),
        ("Matcha Powder",   "gram",3,   6),
        ("Sugar",           "gram",5,   15),
        ("Salt",            "gram",0.5, 1),
        ("Flour",           "gram",100, 200),
        ("Butter",          "gram",50,  100),
        ("Eggs",            "pcs", 1,   3),
        ("Heavy Cream",     "ml",  50,  100),
    ]

    recipe_rows = []
    recipe_ctr  = 1
    for i, vid in enumerate(RNG.sample(variant_ids, min(100, len(variant_ids)))):
        cat = RNG.choice(CATEGORIES)
        version = RNG.randint(1, 3)
        for v in range(1, version + 1):
            is_current = (v == version)
            recipe_rows.append((
                f"RCP-{recipe_ctr:04d}", vid,
                f"Recipe #{recipe_ctr} v{v}",
                v, cat,
                Decimal(str(RNG.choice([1, 2]))),
                RNG.choice(SERVING_UNITS),
                RNG.randint(3, 15),
                is_current, True,
                admin_id,
                datetime.now() - timedelta(days=RNG.randint(0, 180)),
                "", datetime.now(), datetime.now()
            ))
            recipe_ctr += 1

    if dry_run:
        log(f"[DRY RUN] {len(recipe_rows)} recipes + ingredients + costing + yield tests")
        return

    n = bulk_insert("recipe_v2",
        ["code","variant_id","name","version","category","serving_size","serving_unit",
         "preparation_time_min","is_current","is_active","approved_by_id","approved_at",
         "notes","created_at","updated_at"],
        recipe_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Recipes v2: {n:,}")

    # Ingredients
    rcp_ids   = [r[0] for r in q("SELECT id FROM recipe_v2 ORDER BY id")]
    ingr_rows = []
    for rid in rcp_ids:
        n_ingr = RNG.randint(3, 8)
        for i, (iname, unit, qmin, qmax) in enumerate(RNG.sample(INGREDIENTS_POOL, min(n_ingr, len(INGREDIENTS_POOL)))):
            qty = Decimal(str(round(RNG.uniform(qmin, qmax), 1)))
            ingr_rows.append((
                rid, None, iname, qty, unit,
                RNG.choice(["","freshly brewed","chilled","heated","steamed"]),
                RNG.random() < 0.1, i, datetime.now()
            ))

    n = bulk_insert("recipe_v2_ingredients",
        ["recipe_id","variant_id","ingredient_name","quantity","unit",
         "preparation","is_optional","sort_order","created_at"],
        ingr_rows, batch=3000)
    ok(f"Recipe ingredients: {n:,}")

    # Costing
    cost_rows = []
    for rid in rcp_ids:
        ingr_cost  = Decimal(str(RNG.randint(3000, 25000)))
        pkg_cost   = Decimal(str(RNG.randint(500, 3000)))
        labor      = Decimal(str(RNG.randint(500, 2000)))
        overhead   = Decimal(str(RNG.randint(500, 3000)))
        total_cogs = ingr_cost + pkg_cost + labor + overhead
        sell_price = total_cogs * Decimal(str(round(RNG.uniform(2.5, 4.5), 1)))
        margin     = sell_price - total_cogs
        margin_pct = (margin / sell_price * 100).quantize(Decimal("0.01")) if sell_price > 0 else Decimal("0")
        bep        = int(1000000 / float(margin)) if float(margin) > 0 else 999
        cost_rows.append((
            rid, ingr_cost, pkg_cost, labor, overhead,
            total_cogs, sell_price.quantize(Decimal("0.01")),
            margin.quantize(Decimal("0.01")), margin_pct, bep,
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("recipe_costing",
        ["recipe_id","total_ingredient_cost","packaging_cost","labor_cost_allocation",
         "overhead_allocation","total_cogs","selling_price","gross_margin","margin_pct",
         "break_even_qty","costed_at","created_at"],
        cost_rows, on_conflict="ON CONFLICT (recipe_id) DO NOTHING")
    ok(f"Recipe costing: {n:,}")

    # Yield Tests
    yt_rows = []
    for rid in RNG.sample(rcp_ids, min(len(rcp_ids), 200)):
        for _ in range(RNG.randint(1, 5)):
            expected = Decimal(str(RNG.randint(200, 400)))
            actual   = expected * Decimal(str(round(RNG.uniform(0.88, 1.02), 2)))
            yld_pct  = (actual / expected * 100).quantize(Decimal("0.01"))
            yt_rows.append((
                rid, RNG.choice(location_ids),
                RNG.choice(user_ids) if user_ids else admin_id,
                today - timedelta(days=RNG.randint(0, 180)),
                RNG.randint(3, 20),
                expected, actual.quantize(Decimal("0.001")),
                yld_pct,
                RNG.randint(6, 10),
                RNG.choice(["Balance baik","Perlu sedikit adjustment","Rasa konsisten",""]),
                "","",
                float(yld_pct) >= 90,
                datetime.now()
            ))

    n = bulk_insert("recipe_yield_tests",
        ["recipe_id","location_id","tester_id","test_date","batch_size",
         "expected_output","actual_output","yield_pct","quality_score",
         "taste_notes","visual_notes","adjustments","passed","created_at"],
        yt_rows)
    ok(f"Yield tests: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 26 — EVENTS CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

def fill_events_calendar(dry_run=False):
    head("MODUL 26 — EVENTS CALENDAR (Events, Registrations, Revenue)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS events_calendar (
            id              BIGSERIAL PRIMARY KEY,
            event_code      VARCHAR(30) UNIQUE NOT NULL,
            title           VARCHAR(200) NOT NULL,
            description     TEXT DEFAULT '',
            event_type      VARCHAR(30) DEFAULT 'tasting',
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            start_datetime  TIMESTAMPTZ NOT NULL,
            end_datetime    TIMESTAMPTZ NOT NULL,
            capacity        INT DEFAULT 0,
            registered_count INT DEFAULT 0,
            ticket_price    NUMERIC(10,2) DEFAULT 0,
            is_free         BOOLEAN DEFAULT FALSE,
            status          VARCHAR(20) DEFAULT 'upcoming',
            host_name       VARCHAR(100) DEFAULT '',
            banner_url      VARCHAR(500) DEFAULT '',
            is_published    BOOLEAN DEFAULT FALSE,
            created_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE events_calendar IS
            'Event Kafe Nusantara: cupping session, live music, workshop barista, launching menu.';
        CREATE INDEX IF NOT EXISTS idx_evt_location ON events_calendar(location_id);
        CREATE INDEX IF NOT EXISTS idx_evt_date     ON events_calendar(start_datetime);
        CREATE INDEX IF NOT EXISTS idx_evt_status   ON events_calendar(status);
        """, "events_calendar"),

        ("""
        CREATE TABLE IF NOT EXISTS event_registrations (
            id              BIGSERIAL PRIMARY KEY,
            event_id        BIGINT NOT NULL REFERENCES events_calendar(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            registrant_name VARCHAR(100) NOT NULL DEFAULT '',
            registrant_phone VARCHAR(20) DEFAULT '',
            registrant_email VARCHAR(100) DEFAULT '',
            ticket_qty      INT DEFAULT 1,
            total_paid      NUMERIC(10,2) DEFAULT 0,
            payment_method  VARCHAR(20) DEFAULT 'transfer',
            payment_status  VARCHAR(20) DEFAULT 'paid',
            attendance_status VARCHAR(20) DEFAULT 'registered',
            check_in_at     TIMESTAMPTZ,
            qr_code         VARCHAR(40) DEFAULT '',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE event_registrations IS
            'Pendaftaran peserta event. QR code untuk check-in di pintu masuk.';
        CREATE INDEX IF NOT EXISTS idx_evtreg_event ON event_registrations(event_id);
        CREATE INDEX IF NOT EXISTS idx_evtreg_cust  ON event_registrations(customer_id);
        """, "event_registrations"),

        ("""
        CREATE TABLE IF NOT EXISTS event_revenue_summary (
            id              BIGSERIAL PRIMARY KEY,
            event_id        BIGINT NOT NULL UNIQUE REFERENCES events_calendar(id),
            total_registered INT DEFAULT 0,
            total_attended  INT DEFAULT 0,
            gross_revenue   NUMERIC(12,2) DEFAULT 0,
            refund_amount   NUMERIC(10,2) DEFAULT 0,
            net_revenue     NUMERIC(12,2) DEFAULT 0,
            avg_ticket_price NUMERIC(10,2) DEFAULT 0,
            venue_cost      NUMERIC(10,2) DEFAULT 0,
            host_fee        NUMERIC(10,2) DEFAULT 0,
            marketing_cost  NUMERIC(10,2) DEFAULT 0,
            net_profit      NUMERIC(12,2) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE event_revenue_summary IS 'Ringkasan pendapatan dan biaya per event.';
        """, "event_revenue_summary"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    customer_ids = CTX["customer_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    EVENT_TYPES  = ["cupping_session","barista_workshop","live_music","menu_launching",
                    "coffee_talk","latte_art_class","seasonal_launch","community_gathering"]
    HOSTS        = ["Rizky - Head Barista","Dimas - Coffee Educator","Tia - Barista Champion",
                    "Andi - Coffee Roaster","Sari - Culinary Director","Guest: World Barista Champion"]

    evt_rows = []
    days_range = (today - CTX["min_date"]).days
    for i in range(120):
        start_date  = CTX["min_date"] + timedelta(days=RNG.randint(0, days_range + 60))
        start_dt    = datetime.combine(start_date, dtime(RNG.randint(9, 19), 0))
        end_dt      = start_dt + timedelta(hours=RNG.randint(2, 4))
        status      = ("completed" if end_dt < datetime.now() else
                       "ongoing"   if start_dt <= datetime.now() <= end_dt else
                       "upcoming")
        is_free     = RNG.random() < 0.2
        ticket_price= Decimal("0") if is_free else Decimal(str(RNG.randint(50000, 350000)))
        capacity    = RNG.randint(10, 60)
        registered  = RNG.randint(0, capacity) if status in ("completed","ongoing") else RNG.randint(0, capacity)
        evt_rows.append((
            f"EVT-{i+1:04d}",
            f"{RNG.choice(EVENT_TYPES).replace('_',' ').title()} #{i+1}",
            "Bergabunglah dalam pengalaman kopi yang tak terlupakan.",
            RNG.choice(EVENT_TYPES),
            RNG.choice(location_ids),
            start_dt, end_dt,
            capacity, registered,
            ticket_price, is_free, status,
            RNG.choice(HOSTS), "", True,
            RNG.choice(user_ids) if user_ids else admin_id,
            datetime.now(), datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(evt_rows)} events + registrations + revenue summary")
        return

    n = bulk_insert("events_calendar",
        ["event_code","title","description","event_type","location_id",
         "start_datetime","end_datetime","capacity","registered_count","ticket_price",
         "is_free","status","host_name","banner_url","is_published","created_by_id",
         "created_at","updated_at"],
        evt_rows, on_conflict="ON CONFLICT (event_code) DO NOTHING")
    ok(f"Events: {n}")

    # Registrations
    evt_data  = q("SELECT id, capacity, ticket_price, is_free, registered_count FROM events_calendar ORDER BY id")
    reg_rows  = []
    for eid, cap, ticket_price, is_free, registered in evt_data:
        n_reg = registered if registered else RNG.randint(0, min(cap, 30))
        for _ in range(n_reg):
            cid = RNG.choice(customer_ids) if RNG.random() < 0.7 else None
            qty = RNG.randint(1, 2)
            paid = Decimal("0") if is_free else Decimal(str(ticket_price or 0)) * qty
            attended = RNG.random() < 0.85
            reg_rows.append((
                eid, cid,
                f"Peserta {RNG.randint(1000,9999)}",
                f"08{RNG.randint(100000000,999999999)}",
                f"peserta{RNG.randint(1000,9999)}@email.com",
                qty, paid.quantize(Decimal("0.01")),
                RNG.choice(["transfer","qris","cash"]),
                "paid", "attended" if attended else "registered",
                datetime.now() - timedelta(hours=RNG.randint(1, 48)) if attended else None,
                rand_hex(8), "", datetime.now()
            ))

    n = bulk_insert("event_registrations",
        ["event_id","customer_id","registrant_name","registrant_phone","registrant_email",
         "ticket_qty","total_paid","payment_method","payment_status","attendance_status",
         "check_in_at","qr_code","notes","created_at"],
        reg_rows, batch=3000)
    ok(f"Event registrations: {n:,}")

    # Revenue Summary
    rev_rows = []
    for eid, cap, ticket_price, is_free, registered in evt_data:
        n_attended = int((registered or 0) * RNG.uniform(0.7, 0.95))
        gross      = Decimal(str(ticket_price or 0)) * registered if not is_free else Decimal("0")
        refund     = gross * Decimal("0.05") if RNG.random() < 0.1 else Decimal("0")
        net_rev    = gross - refund
        venue      = Decimal(str(RNG.randint(500000, 3000000)))
        host_fee   = Decimal(str(RNG.randint(200000, 1500000)))
        marketing  = Decimal(str(RNG.randint(100000, 500000)))
        net_profit = net_rev - venue - host_fee - marketing
        rev_rows.append((
            eid, registered or 0, n_attended,
            gross.quantize(Decimal("0.01")),
            refund.quantize(Decimal("0.01")),
            net_rev.quantize(Decimal("0.01")),
            Decimal(str(ticket_price or 0)),
            venue, host_fee, marketing,
            net_profit.quantize(Decimal("0.01")),
            datetime.now()
        ))

    n = bulk_insert("event_revenue_summary",
        ["event_id","total_registered","total_attended","gross_revenue","refund_amount",
         "net_revenue","avg_ticket_price","venue_cost","host_fee","marketing_cost",
         "net_profit","created_at"],
        rev_rows, on_conflict="ON CONFLICT (event_id) DO NOTHING")
    ok(f"Event revenue summary: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 27 — CUSTOMER SUPPORT (Tickets, SLA, Escalations)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_customer_support(dry_run=False):
    head("MODUL 27 — CUSTOMER SUPPORT (Tickets, Messages, SLA, Escalations)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS cs_sla_configs (
            id              BIGSERIAL PRIMARY KEY,
            priority        VARCHAR(10) UNIQUE NOT NULL,
            first_response_hours  INT NOT NULL DEFAULT 24,
            resolution_hours      INT NOT NULL DEFAULT 72,
            escalation_hours      INT NOT NULL DEFAULT 48,
            applies_to_categories TEXT[] DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_sla_configs IS 'Konfigurasi SLA per prioritas ticket.';
        """, "cs_sla_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS cs_tickets (
            id              BIGSERIAL PRIMARY KEY,
            ticket_number   VARCHAR(20) UNIQUE NOT NULL,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            channel         VARCHAR(20) DEFAULT 'app',
            category        VARCHAR(30) NOT NULL DEFAULT 'general',
            subcategory     VARCHAR(50) DEFAULT '',
            priority        VARCHAR(10) DEFAULT 'normal',
            status          VARCHAR(20) DEFAULT 'open',
            subject         VARCHAR(200) NOT NULL,
            description     TEXT NOT NULL DEFAULT '',
            assigned_to_id  BIGINT REFERENCES auth_user(id),
            first_response_at TIMESTAMPTZ,
            resolved_at     TIMESTAMPTZ,
            closed_at       TIMESTAMPTZ,
            sla_breached    BOOLEAN DEFAULT FALSE,
            satisfaction_score SMALLINT CHECK(satisfaction_score BETWEEN 1 AND 5),
            tags            TEXT[] DEFAULT '{}',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_tickets IS
            'Tiket support customer. Channel: app, whatsapp, email, walk_in, social_media.
            Category: product_quality, order_issue, payment, loyalty, complaint, suggestion.';
        CREATE INDEX IF NOT EXISTS idx_ticket_status   ON cs_tickets(status);
        CREATE INDEX IF NOT EXISTS idx_ticket_customer ON cs_tickets(customer_id);
        CREATE INDEX IF NOT EXISTS idx_ticket_priority ON cs_tickets(priority);
        CREATE INDEX IF NOT EXISTS idx_ticket_date     ON cs_tickets(created_at DESC);
        """, "cs_tickets"),

        ("""
        CREATE TABLE IF NOT EXISTS cs_ticket_messages (
            id              BIGSERIAL PRIMARY KEY,
            ticket_id       BIGINT NOT NULL REFERENCES cs_tickets(id),
            sender_type     VARCHAR(10) NOT NULL DEFAULT 'customer',
            sender_id       BIGINT REFERENCES auth_user(id),
            message         TEXT NOT NULL,
            attachments     JSONB DEFAULT '[]',
            is_internal     BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_ticket_messages IS
            'Pesan dalam tiket. sender_type: customer, agent, system. is_internal=True = catatan internal agent.';
        CREATE INDEX IF NOT EXISTS idx_tm_ticket ON cs_ticket_messages(ticket_id);
        CREATE INDEX IF NOT EXISTS idx_tm_date   ON cs_ticket_messages(created_at);
        """, "cs_ticket_messages"),

        ("""
        CREATE TABLE IF NOT EXISTS cs_escalations (
            id              BIGSERIAL PRIMARY KEY,
            ticket_id       BIGINT NOT NULL REFERENCES cs_tickets(id),
            from_agent_id   BIGINT REFERENCES auth_user(id),
            to_agent_id     BIGINT REFERENCES auth_user(id),
            escalation_type VARCHAR(20) DEFAULT 'priority',
            reason          TEXT NOT NULL DEFAULT '',
            new_priority    VARCHAR(10),
            resolved        BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_escalations IS 'Log eskalasi tiket ke agent atau supervisor yang lebih senior.';
        """, "cs_escalations"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # SLA Configs
    sla_data = [
        ("critical", 1,   4,   2),
        ("high",     4,   24,  12),
        ("normal",   8,   48,  24),
        ("low",      24,  120, 72),
    ]
    sla_rows = [(p, fr, res, esc, [], True, datetime.now()) for p, fr, res, esc in sla_data]

    if dry_run:
        log(f"[DRY RUN] SLA configs + tickets + messages + escalations")
        return

    n = bulk_insert("cs_sla_configs",
        ["priority","first_response_hours","resolution_hours","escalation_hours",
         "applies_to_categories","is_active","created_at"],
        sla_rows, on_conflict="ON CONFLICT (priority) DO NOTHING")
    ok(f"SLA configs: {n}")

    customer_ids = CTX["customer_ids"]
    order_ids    = CTX["order_ids"]
    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]
    days_range   = (today - CTX["min_date"]).days

    CATEGORIES = ["product_quality","order_issue","payment","loyalty","complaint","suggestion","other"]
    CHANNELS   = ["app","whatsapp","email","walk_in","social_media"]
    PRIORITIES = ["low","normal","normal","normal","high","critical"]
    SUBJECTS   = [
        "Pesanan saya salah","Kopi terasa pahit","Promo tidak berfungsi",
        "Stamp tidak bertambah","Refund request","Keluhan kebersihan",
        "Saran menu baru","Barista tidak ramah","Harga tidak sesuai",
        "Aplikasi error","Wi-Fi tidak ada","Tempat duduk kurang",
        "Compliment untuk barista","Request khusus untuk event",
    ]

    ticket_rows = []
    for i in range(5000):
        created = datetime.now() - timedelta(
            days=RNG.randint(0, days_range), hours=RNG.randint(0, 23)
        )
        priority = RNG.choice(PRIORITIES)
        status   = RNG.choices(["open","in_progress","resolved","closed","pending_customer"],
                               weights=[15, 25, 30, 25, 5])[0]
        resolved_at = created + timedelta(hours=RNG.randint(2, 96)) \
                      if status in ("resolved","closed") else None
        sla_breached= resolved_at and (resolved_at - created).total_seconds() > 48*3600
        ticket_rows.append((
            f"TKT-{i+1:06d}",
            RNG.choice(customer_ids),
            RNG.choice(order_ids) if RNG.random() < 0.4 and order_ids else None,
            RNG.choice(location_ids),
            RNG.choice(CHANNELS),
            RNG.choice(CATEGORIES), "",
            priority, status,
            RNG.choice(SUBJECTS),
            "Detail keluhan dari customer.",
            RNG.choice(user_ids) if user_ids else admin_id,
            created + timedelta(hours=RNG.randint(0, 4)) if status != "open" else None,
            resolved_at, resolved_at,
            bool(sla_breached),
            RNG.randint(3, 5) if status == "closed" else None,
            json.dumps([]),
            created, created
        ))

    n = bulk_insert("cs_tickets",
        ["ticket_number","customer_id","order_id","location_id","channel",
         "category","subcategory","priority","status","subject","description",
         "assigned_to_id","first_response_at","resolved_at","closed_at",
         "sla_breached","satisfaction_score","tags","created_at","updated_at"],
        ticket_rows, batch=3000,
        on_conflict="ON CONFLICT (ticket_number) DO NOTHING")
    ok(f"Tickets: {n:,}")

    # Messages
    ticket_ids = [r[0] for r in q("SELECT id FROM cs_tickets ORDER BY id")]
    msg_rows   = []
    CUST_MSGS  = [
        "Saya ingin melaporkan pesanan yang tidak sesuai.",
        "Kopi saya terasa berbeda dari biasanya.",
        "Stamp saya tidak bertambah setelah transaksi.",
        "Apakah promo ini masih berlaku?",
        "Terima kasih atas penanganannya!",
    ]
    AGENT_MSGS = [
        "Halo, terima kasih sudah menghubungi Kafe Nusantara. Kami sedang meninjau laporan Anda.",
        "Kami mohon maaf atas ketidaknyamanan ini. Tim kami sedang menyelidiki masalah tersebut.",
        "Stamp Anda sudah kami tambahkan secara manual. Mohon maaf atas ketidaknyamanan ini.",
        "Promo tersebut masih berlaku hingga akhir bulan. Ada yang bisa kami bantu lagi?",
        "Masalah sudah berhasil diselesaikan. Terima kasih atas kesabaran Anda!",
    ]

    for tid in ticket_ids:
        n_msg = RNG.randint(2, 8)
        for j in range(n_msg):
            is_agent = j % 2 == 1
            msg_rows.append((
                tid,
                "agent" if is_agent else "customer",
                RNG.choice(user_ids) if is_agent and user_ids else None,
                RNG.choice(AGENT_MSGS if is_agent else CUST_MSGS),
                json.dumps([]),
                RNG.random() < 0.1 and is_agent,
                datetime.now() - timedelta(days=RNG.randint(0, 30))
            ))

    n = bulk_insert("cs_ticket_messages",
        ["ticket_id","sender_type","sender_id","message","attachments","is_internal","created_at"],
        msg_rows, batch=3000)
    ok(f"Ticket messages: {n:,}")

    # Escalations
    esc_rows = []
    for tid in RNG.sample(ticket_ids, min(300, len(ticket_ids))):
        if RNG.random() < 0.3:
            esc_rows.append((
                tid,
                RNG.choice(user_ids) if user_ids else admin_id,
                admin_id,
                RNG.choice(["priority","department","manager"]),
                "SLA terancam breach. Perlu penanganan segera.",
                "high", RNG.random() < 0.6,
                datetime.now() - timedelta(days=RNG.randint(0, 30))
            ))

    n = bulk_insert("cs_escalations",
        ["ticket_id","from_agent_id","to_agent_id","escalation_type","reason",
         "new_priority","resolved","created_at"],
        esc_rows)
    ok(f"Escalations: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 28 — ANALYTICS CUBE (Pre-aggregated OLAP)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_analytics_cube(dry_run=False):
    head("MODUL 28 — ANALYTICS CUBE (Hourly, Cohort, Funnel, Retention)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS analytics_hourly_sales (
            id              BIGSERIAL PRIMARY KEY,
            sale_date       DATE NOT NULL,
            sale_hour       SMALLINT NOT NULL CHECK(sale_hour BETWEEN 0 AND 23),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            shift_type      VARCHAR(20) DEFAULT '',
            total_orders    INT DEFAULT 0,
            total_revenue   NUMERIC(15,2) DEFAULT 0,
            avg_order_value NUMERIC(12,2) DEFAULT 0,
            new_customers   INT DEFAULT 0,
            promo_orders    INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(sale_date, sale_hour, location_id)
        );
        COMMENT ON TABLE analytics_hourly_sales IS
            'Agregasi penjualan per jam per outpost. Untuk heatmap dan peak hour analysis.';
        CREATE INDEX IF NOT EXISTS idx_hs_date ON analytics_hourly_sales(sale_date DESC);
        CREATE INDEX IF NOT EXISTS idx_hs_hour ON analytics_hourly_sales(sale_hour);
        """, "analytics_hourly_sales"),

        ("""
        CREATE TABLE IF NOT EXISTS analytics_customer_cohorts (
            id              BIGSERIAL PRIMARY KEY,
            cohort_month    VARCHAR(7) NOT NULL,
            period_offset   SMALLINT NOT NULL DEFAULT 0,
            cohort_size     INT DEFAULT 0,
            retained_customers INT DEFAULT 0,
            retention_rate  NUMERIC(6,3) DEFAULT 0,
            avg_orders      NUMERIC(8,3) DEFAULT 0,
            avg_revenue     NUMERIC(12,2) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(cohort_month, period_offset)
        );
        COMMENT ON TABLE analytics_customer_cohorts IS
            'Cohort retention analysis. cohort_month = bulan pertama customer order.
            period_offset = 0 (bulan pertama), 1 (1 bulan kemudian), dst.
            retention_rate = % customer yang masih aktif di periode tersebut.';
        CREATE INDEX IF NOT EXISTS idx_cohort_month ON analytics_customer_cohorts(cohort_month);
        """, "analytics_customer_cohorts"),

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
            drop_off_rate   NUMERIC(6,3) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(funnel_date, location_id, channel, stage)
        );
        COMMENT ON TABLE analytics_conversion_funnel IS
            'Funnel konversi: visit → browse_menu → add_to_cart → checkout → order → repeat.';
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
            'Market basket analysis: produk yang sering dibeli bersama.
            Basis untuk cross-sell recommendation.';
        CREATE INDEX IF NOT EXISTS idx_affinity_lift ON analytics_product_affinity(lift_score DESC);
        CREATE INDEX IF NOT EXISTS idx_affinity_a    ON analytics_product_affinity(variant_a_id);
        """, "analytics_product_affinity"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    variant_ids  = CTX["variant_ids"]
    min_date     = CTX["min_date"]
    days_range   = (today - min_date).days

    # Hourly Sales (simulasi dari distribusi traffic kafe)
    # Peak: 8-10 (morning), 12-14 (lunch), 17-19 (after office)
    HOUR_WEIGHTS = [0,0,0,0,0,0,1,5,15,18,12,8,12,14,10,8,10,14,12,8,5,3,2,1]
    SHIFT_MAP_H  = {h: ("first_light" if 7 <= h < 12 else
                        "midday_transit" if 12 <= h < 18 else
                        "twilight_bivouac") for h in range(24)}

    log("Generating hourly sales...")
    hs_rows = []
    for d in range(min(days_range, 730)):
        sale_date = today - timedelta(days=d)
        for lid in location_ids:
            daily_revenue = Decimal(str(RNG.randint(2000000, 20000000)))
            for hour in range(7, 23):
                weight    = HOUR_WEIGHTS[hour]
                pct       = weight / sum(HOUR_WEIGHTS[7:23])
                h_revenue = daily_revenue * Decimal(str(round(pct * RNG.uniform(0.7, 1.3), 4)))
                h_orders  = max(0, int(h_revenue / Decimal(str(RNG.randint(30000, 60000)))))
                aov       = h_revenue / h_orders if h_orders > 0 else Decimal("0")
                hs_rows.append((
                    sale_date, hour, lid,
                    SHIFT_MAP_H[hour],
                    h_orders,
                    h_revenue.quantize(Decimal("0.01")),
                    aov.quantize(Decimal("0.01")),
                    RNG.randint(0, max(1, h_orders // 10)),
                    RNG.randint(0, max(1, h_orders // 5)),
                    datetime.now()
                ))

    if dry_run:
        log(f"[DRY RUN] {len(hs_rows)} hourly rows + cohorts + funnel + affinity")
        return

    n = bulk_insert("analytics_hourly_sales",
        ["sale_date","sale_hour","location_id","shift_type","total_orders",
         "total_revenue","avg_order_value","new_customers","promo_orders","created_at"],
        hs_rows, batch=3000,
        on_conflict="ON CONFLICT (sale_date, sale_hour, location_id) DO NOTHING")
    ok(f"Hourly sales: {n:,}")

    # Cohort Analysis
    cohort_rows = []
    for mo_offset in range(24):  # 24 bulan cohort
        cohort_ref = today.replace(day=1) - timedelta(days=mo_offset * 30)
        cohort_month = cohort_ref.replace(day=1).strftime("%Y-%m")
        cohort_size  = RNG.randint(50, 500)
        for period in range(min(13, 24 - mo_offset)):  # max 12 bulan follow-up
            if period == 0:
                retained = cohort_size
                ret_rate = Decimal("100.0")
            else:
                # Retention curve: menurun dengan waktu
                base_retention = 0.7 * (0.85 ** period)
                retained = int(cohort_size * RNG.uniform(base_retention * 0.8, base_retention * 1.2))
                ret_rate = Decimal(str(round(retained / cohort_size * 100, 3)))

            cohort_rows.append((
                cohort_month, period, cohort_size, retained,
                ret_rate,
                Decimal(str(round(RNG.uniform(1.5, 4.0), 3))),
                Decimal(str(RNG.randint(50000, 250000))),
                datetime.now()
            ))

    n = bulk_insert("analytics_customer_cohorts",
        ["cohort_month","period_offset","cohort_size","retained_customers",
         "retention_rate","avg_orders","avg_revenue","created_at"],
        cohort_rows,
        on_conflict="ON CONFLICT (cohort_month, period_offset) DO NOTHING")
    ok(f"Cohort analysis: {n:,}")

    # Conversion Funnel
    FUNNEL_STAGES = [
        ("visit",        1),
        ("browse_menu",  2),
        ("add_to_cart",  3),
        ("checkout",     4),
        ("order_placed", 5),
        ("repeat_order", 6),
    ]
    CHANNELS = ["dine_in","takeaway","app"]
    fnl_rows = []
    for d in range(min(days_range, 90)):
        fdate = today - timedelta(days=d)
        for lid in location_ids:
            for channel in CHANNELS:
                base_visits = RNG.randint(50, 500)
                prev_count  = base_visits
                for stage, sorder in FUNNEL_STAGES:
                    drop = RNG.uniform(0.6, 0.95) if stage != "visit" else 1.0
                    current = int(prev_count * drop)
                    conv_rate = round(current / base_visits * 100, 3) if base_visits > 0 else 0
                    drop_rate = round((prev_count - current) / prev_count * 100, 3) if prev_count > 0 else 0
                    fnl_rows.append((
                        fdate, lid, channel, stage, sorder,
                        current, conv_rate, drop_rate, datetime.now()
                    ))
                    prev_count = current

    n = bulk_insert("analytics_conversion_funnel",
        ["funnel_date","location_id","channel","stage","stage_order",
         "users_count","conversion_rate","drop_off_rate","created_at"],
        fnl_rows, batch=3000,
        on_conflict="ON CONFLICT (funnel_date, location_id, channel, stage) DO NOTHING")
    ok(f"Conversion funnel: {n:,}")

    # Product Affinity (Market Basket)
    aff_rows = []
    sample_variants = RNG.sample(variant_ids, min(80, len(variant_ids)))
    for period_offset in range(6):
        period = (today.replace(day=1) - timedelta(days=period_offset * 30)).replace(day=1).strftime("%Y-%m")
        for i in range(len(sample_variants)):
            for j in range(i+1, min(i+10, len(sample_variants))):
                va = sample_variants[i]
                vb = sample_variants[j]
                co_count   = RNG.randint(5, 200)
                support    = round(co_count / 10000 * 100, 3)
                confidence = round(RNG.uniform(0.1, 0.8), 3)
                lift       = round(confidence / RNG.uniform(0.05, 0.3), 4)
                aff_rows.append((va, vb, co_count, support, confidence, lift, period, datetime.now()))

    n = bulk_insert("analytics_product_affinity",
        ["variant_a_id","variant_b_id","co_purchase_count","support_pct",
         "confidence_pct","lift_score","period","created_at"],
        aff_rows, batch=3000,
        on_conflict="ON CONFLICT (variant_a_id, variant_b_id, period) DO NOTHING")
    ok(f"Product affinity: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 29 — CONFIG STORE (Feature Flags, App Configs, Changelog)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_config_store(dry_run=False):
    head("MODUL 29 — CONFIG STORE (Feature Flags, App Configs, Location Configs, Changelog)")

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
            applies_to      VARCHAR(20) DEFAULT 'all',
            allowed_locations BIGINT[] DEFAULT '{}',
            allowed_tiers   TEXT[] DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            changed_by_id   BIGINT REFERENCES auth_user(id),
            changed_at      TIMESTAMPTZ DEFAULT NOW(),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_feature_flags IS
            'Feature flags untuk A/B testing dan gradual rollout fitur baru.
            flag_type: boolean, percentage, string, json.
            applies_to: all, location, customer_tier, employee_role.';
        """, "cfg_feature_flags"),

        ("""
        CREATE TABLE IF NOT EXISTS cfg_app_configs (
            id              BIGSERIAL PRIMARY KEY,
            config_key      VARCHAR(80) UNIQUE NOT NULL,
            config_group    VARCHAR(40) NOT NULL DEFAULT 'general',
            display_name    VARCHAR(120) NOT NULL,
            value_type      VARCHAR(20) DEFAULT 'string',
            value           JSONB NOT NULL DEFAULT 'null',
            default_value   JSONB NOT NULL DEFAULT 'null',
            description     TEXT DEFAULT '',
            is_sensitive    BOOLEAN DEFAULT FALSE,
            requires_restart BOOLEAN DEFAULT FALSE,
            changed_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_app_configs IS
            'Konfigurasi aplikasi yang bisa diubah tanpa deploy. Group: general, payment, notification, loyalty, reporting.';
        CREATE INDEX IF NOT EXISTS idx_cfg_group ON cfg_app_configs(config_group);
        """, "cfg_app_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS cfg_location_configs (
            id              BIGSERIAL PRIMARY KEY,
            location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
            config_key      VARCHAR(80) NOT NULL,
            value           JSONB NOT NULL DEFAULT 'null',
            override_reason TEXT DEFAULT '',
            changed_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(location_id, config_key)
        );
        COMMENT ON TABLE cfg_location_configs IS
            'Override konfigurasi per lokasi spesifik (contoh: jam buka, menu khusus, price list).';
        CREATE INDEX IF NOT EXISTS idx_lc_location ON cfg_location_configs(location_id);
        """, "cfg_location_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS cfg_changelog (
            id              BIGSERIAL PRIMARY KEY,
            change_type     VARCHAR(30) NOT NULL,
            entity_type     VARCHAR(40) NOT NULL,
            entity_id       BIGINT,
            change_summary  VARCHAR(200) NOT NULL,
            old_value       JSONB DEFAULT '{}',
            new_value       JSONB DEFAULT '{}',
            changed_by_id   BIGINT REFERENCES auth_user(id),
            reason          TEXT DEFAULT '',
            ip_address      INET,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_changelog IS
            'Log semua perubahan konfigurasi. Immutable audit trail untuk compliance.';
        CREATE INDEX IF NOT EXISTS idx_chg_type  ON cfg_changelog(change_type);
        CREATE INDEX IF NOT EXISTS idx_chg_entity ON cfg_changelog(entity_type, entity_id);
        CREATE INDEX IF NOT EXISTS idx_chg_date  ON cfg_changelog(created_at DESC);
        """, "cfg_changelog"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    admin_id     = CTX["admin_id"]
    user_ids     = CTX["user_ids"]
    location_ids = CTX["location_ids"]

    # Feature Flags
    flags_data = [
        ("loyalty_v2_enabled",         "Loyalty Program V2",           "boolean", True,   True,  100, "all"),
        ("meilisearch_enabled",         "Meilisearch Search",           "boolean", True,   True,  100, "all"),
        ("ai_recommendations",          "AI Product Recommendations",   "boolean", False,  False, 20,  "all"),
        ("new_pos_ui",                  "New POS Interface",            "boolean", False,  True,  50,  "location"),
        ("digital_receipt",             "Digital Receipt Only",         "boolean", False,  False, 0,   "all"),
        ("qris_split_payment",          "QRIS Split Payment",           "boolean", False,  True,  100, "all"),
        ("real_time_stock_sync",        "Real-time Stock Sync",         "boolean", True,   True,  100, "all"),
        ("whatsapp_notifications",      "WhatsApp Notifications",       "boolean", True,   True,  100, "all"),
        ("seasonal_menu_preview",       "Early Access Seasonal Menu",   "boolean", False,  True,  0,   "customer_tier"),
        ("advanced_analytics_dashboard","Advanced Analytics Dashboard", "boolean", False,  True,  100, "employee_role"),
        ("auto_reorder",                "Automatic Reorder PO",         "boolean", False,  False, 0,   "all"),
        ("customer_facing_kiosk",       "Self-Order Kiosk Mode",        "boolean", False,  True,  30,  "location"),
        ("loyalty_points_expiry",       "Loyalty Points Expiry",        "boolean", False,  False, 0,   "all"),
        ("pdf_receipts",                "PDF Receipt Generation",       "boolean", True,   True,  100, "all"),
        ("multi_currency",              "Multi-currency Support",       "boolean", False,  False, 0,   "all"),
        ("dark_mode_pos",               "Dark Mode POS",                "boolean", False,  True,  100, "all"),
        ("stamp_card_nfc",              "NFC Stamp Card",               "boolean", False,  False, 10,  "location"),
        ("waste_tracking",              "Waste Tracking Module",        "boolean", True,   True,  100, "all"),
        ("training_portal",             "Employee Training Portal",     "boolean", True,   True,  100, "all"),
        ("event_booking",               "Event Booking System",         "boolean", True,   True,  100, "all"),
    ]

    flag_rows = [(key, name, "", "boolean",
                  json.dumps(default), json.dumps(current),
                  rollout, applies, json.dumps([]), json.dumps([]),
                  True, admin_id, datetime.now(), datetime.now())
                 for key, name, ftype, default, current, rollout, applies in flags_data]

    if dry_run:
        log(f"[DRY RUN] {len(flag_rows)} feature flags + app configs + location configs + changelog")
        return

    n = bulk_insert("cfg_feature_flags",
        ["flag_key","display_name","description","flag_type","default_value","current_value",
         "rollout_pct","applies_to","allowed_locations","allowed_tiers","is_active",
         "changed_by_id","changed_at","created_at"],
        flag_rows, on_conflict="ON CONFLICT (flag_key) DO NOTHING")
    ok(f"Feature flags: {n}")

    # App Configs
    app_configs = [
        ("loyalty.stamp_per_order",         "loyalty", "Stamps per Order",              "integer",  1,          1),
        ("loyalty.min_spend_for_stamp",      "loyalty", "Minimum Spend untuk Stamp",     "integer",  25000,      25000),
        ("loyalty.points_per_stamp",         "loyalty", "Poin per Stamp",               "integer",  10,         10),
        ("loyalty.stamp_validity_days",      "loyalty", "Masa berlaku stamp (hari)",    "integer",  365,        365),
        ("payment.qris_surcharge_pct",       "payment", "QRIS Surcharge (%)",           "float",    0.0,        0.0),
        ("payment.cash_rounding",            "payment", "Cash Rounding (nearest Rp)",   "integer",  500,        500),
        ("notification.push_batch_size",     "notification","Push Notif Batch Size",    "integer",  1000,       1000),
        ("notification.email_from",          "notification","Email From Address",        "string",   "noreply@kafenusantara.id","noreply@kafenusantara.id"),
        ("reporting.auto_send_daily",        "reporting","Auto-kirim Laporan Harian",   "boolean",  True,       True),
        ("reporting.retention_days",         "reporting","Simpan laporan (hari)",       "integer",  90,         90),
        ("search.min_query_length",          "search",  "Panjang minimum query",        "integer",  2,          2),
        ("search.results_per_page",          "search",  "Hasil per halaman",            "integer",  20,         20),
        ("pos.session_timeout_minutes",      "pos",     "Timeout sesi POS (menit)",     "integer",  30,         30),
        ("pos.receipt_footer_text",          "pos",     "Teks footer struk",            "string",   "Terima kasih sudah singgah!","Terima kasih sudah singgah!"),
        ("pos.enable_split_payment",         "pos",     "Aktifkan Split Payment",       "boolean",  True,       True),
        ("stock.low_stock_alert_threshold",  "stock",   "Threshold alert stok menipis", "float",    1.5,        1.5),
        ("stock.auto_reorder_enabled",       "stock",   "Auto Reorder aktif",           "boolean",  False,      False),
        ("hr.overtime_multiplier",           "hr",      "Multiplier lembur",            "float",    1.5,        1.5),
        ("hr.late_deduction_per_minute",     "hr",      "Potongan per menit terlambat", "integer",  2000,       2000),
        ("general.timezone",                 "general", "Timezone aplikasi",            "string",   "Asia/Jakarta","Asia/Jakarta"),
        ("general.currency",                 "general", "Mata uang",                    "string",   "IDR",      "IDR"),
        ("general.date_format",              "general", "Format tanggal",               "string",   "DD/MM/YYYY","DD/MM/YYYY"),
    ]
    cfg_rows = [(key, group, name, vtype,
                 json.dumps(val), json.dumps(default),
                 "", False, False, admin_id,
                 datetime.now(), datetime.now())
                for key, group, name, vtype, default, val in app_configs]

    n = bulk_insert("cfg_app_configs",
        ["config_key","config_group","display_name","value_type","value","default_value",
         "description","is_sensitive","requires_restart","changed_by_id","created_at","updated_at"],
        cfg_rows, on_conflict="ON CONFLICT (config_key) DO NOTHING")
    ok(f"App configs: {n}")

    # Location Configs (override per lokasi)
    loc_cfg_rows = []
    LOC_OVERRIDES = [
        ("pos.receipt_footer_text",    lambda: f"Terima kasih! Outpost #{RNG.randint(1,56)}"),
        ("loyalty.stamp_per_order",    lambda: str(RNG.choice([1, 2]))),
        ("pos.session_timeout_minutes",lambda: str(RNG.choice([20, 30, 45, 60]))),
        ("stock.low_stock_alert_threshold", lambda: str(round(RNG.uniform(1.0, 2.5), 1))),
    ]
    for lid in location_ids:
        for key, val_fn in RNG.sample(LOC_OVERRIDES, RNG.randint(1, 3)):
            loc_cfg_rows.append((
                lid, key, json.dumps(val_fn()), "",
                admin_id, datetime.now(), datetime.now()
            ))

    n = bulk_insert("cfg_location_configs",
        ["location_id","config_key","value","override_reason","changed_by_id","created_at","updated_at"],
        loc_cfg_rows,
        on_conflict="ON CONFLICT (location_id, config_key) DO NOTHING")
    ok(f"Location configs: {n}")

    # Changelog
    chg_rows = []
    CHANGE_TYPES = ["config_update","flag_toggle","price_change","recipe_update",
                    "permission_change","menu_update","sla_update"]
    ENTITY_TYPES = ["cfg_feature_flags","cfg_app_configs","menu_item","recipe_v2",
                    "loyalty_tiers","cs_sla_configs"]
    IPS = [f"10.0.0.{i}" for i in range(1, 20)]

    days_range = (today - CTX["min_date"]).days
    for _ in range(2000):
        created = datetime.now() - timedelta(days=RNG.randint(0, days_range))
        chg_rows.append((
            RNG.choice(CHANGE_TYPES),
            RNG.choice(ENTITY_TYPES),
            RNG.randint(1, 100),
            f"Updated config via admin panel",
            json.dumps({"value": RNG.choice([True, False, 10, 25000])}),
            json.dumps({"value": RNG.choice([True, False, 15, 30000])}),
            RNG.choice(user_ids) if user_ids else admin_id,
            "Operational requirement",
            RNG.choice(IPS), created
        ))

    n = bulk_insert("cfg_changelog",
        ["change_type","entity_type","entity_id","change_summary",
         "old_value","new_value","changed_by_id","reason","ip_address","created_at"],
        chg_rows, batch=3000)
    ok(f"Changelog entries: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "task_queue":       fill_task_queue,
    "search":           fill_search,
    "reporting":        fill_reporting,
    "api_gateway":      fill_api_gateway,
    "security":         fill_security,
    "recipe_mgmt":      fill_recipe_mgmt,
    "events_calendar":  fill_events_calendar,
    "customer_support": fill_customer_support,
    "analytics_cube":   fill_analytics_cube,
    "config_store":     fill_config_store,
}

ORDER = ["task_queue","search","reporting","api_gateway","security",
         "recipe_mgmt","events_calendar","customer_support","analytics_cube","config_store"]

NEW_TABLES = [
    # Task Queue
    "tq_task_definitions","tq_job_logs","tq_dead_letter_queue","tq_scheduled_jobs",
    # Search
    "search_index_configs","search_query_logs","search_synonyms","search_analytics_daily",
    # Reporting
    "report_templates","report_schedules","report_generated","report_delivery_log",
    # API Gateway
    "api_keys","api_rate_limit_tiers","api_usage_logs","api_webhooks","api_webhook_deliveries",
    # Security
    "sec_login_events","sec_security_alerts","sec_ip_whitelist","sec_device_registry",
    # Recipe
    "recipe_v2","recipe_v2_ingredients","recipe_costing","recipe_yield_tests",
    # Events
    "events_calendar","event_registrations","event_revenue_summary",
    # Customer Support
    "cs_sla_configs","cs_tickets","cs_ticket_messages","cs_escalations",
    # Analytics Cube
    "analytics_hourly_sales","analytics_customer_cohorts",
    "analytics_conversion_funnel","analytics_product_affinity",
    # Config Store
    "cfg_feature_flags","cfg_app_configs","cfg_location_configs","cfg_changelog",
]

def main():
    t_total = time.time()
    print("\n" + "═"*70)
    print("  KAFE NUSANTARA — World Building Phase 3 (seed_expansion3)")
    print("  10 modul baru: TaskQueue, Search, Reporting, API Gateway,")
    print("  Security, Recipe V2, Events, CS, Analytics Cube, Config Store")
    print(f"  Stack: Celery+Redis · Meilisearch · WeasyPrint · DRF · django-axes")
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
    print(f"\n  Total tabel baru: {len(NEW_TABLES)}")
    print(f"  Grand total tabel (seed 1+2+3): ~{15 + 40 + len(NEW_TABLES)} tabel\n")


try:
    from django.core.management.base import BaseCommand
    class Command(BaseCommand):
        help = "Kafe Nusantara — World Building Phase 3 (10 modul baru)"
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