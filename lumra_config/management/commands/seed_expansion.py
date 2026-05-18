"""
seed_expansion.py
=================
Script ekspansi database Kafe Nusantara — membuat dan mengisi tabel-tabel
yang melengkapi siklus bisnis, reporting, CRM, dan dashboard.

Semua operasi menggunakan raw SQL via Django connection.cursor()
untuk menghindari masalah managed=False dan FK attname.

MODUL (jalankan per section atau semua sekaligus):
  1. procurement    — purchase_orders, purchase_order_items,
                      goods_receipt_notes, goods_receipt_items
  2. rfm            — customer_rfm_scores (Recency/Frequency/Monetary)
  3. promotions     — promotions, promotion_usage
  4. sales_agg      — sales_daily_summary, sales_monthly_summary
  5. product_perf   — product_performance_summary
  6. inv_snapshot   — inventory_snapshot_monthly
  7. shifts         — shifts, shift_sales_summary
  8. kpi_cache      — dashboard_kpi_cache
  9. audit          — system_audit_trails (opsional, bisa besar)

Cara pakai:
  python seed_expansion.py --dry-run
  python seed_expansion.py --execute
  python seed_expansion.py --execute --section=procurement
  python seed_expansion.py --execute --section=rfm
  python seed_expansion.py --execute --section=sales_agg
  python seed_expansion.py --list-sections
"""

import os, sys, random, time, json
from decimal import Decimal
from datetime import date, datetime, timedelta

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
    print("Sections: procurement rfm promotions sales_agg product_perf inv_snapshot shifts kpi_cache audit all")
    sys.exit(0)

RNG = random.Random(42)

# ── Django ────────────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
import django; django.setup()
from django.db import connection
from django.utils import timezone

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def log(msg): print(f"  {msg}", flush=True)
def ok(msg):  print(f"  ✓ {msg}", flush=True)
def warn(msg):print(f"  ⚠ {msg}", flush=True)
def head(msg):
    print(f"\n{'▓'*60}")
    print(f"  {msg}")
    print(f"{'▓'*60}")

def q(sql, params=None):
    with connection.cursor() as cur:
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
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
            warn(f"Batch {i//batch+1} error [{table}]: {e}")
            for row in chunk:
                try:
                    with connection.cursor() as cur:
                        cur.execute(sql, row)
                        total += 1
                except: pass
    return total

def progress(done, total, t0, label=""):
    pct = done/max(1,total)*100
    ela = time.time()-t0
    eta = (ela/max(1,done))*(total-done) if done<total else 0
    bar = "█"*int(pct/5)+"░"*(20-int(pct/5))
    print(f"\r    [{bar}] {pct:5.1f}%  {done:,}/{total:,}  ETA {eta:.0f}s  {label}   ",
          end="", flush=True)

# ── Context: ambil data dari DB sekali ───────────────────────────────────────
CTX = {}
def load_context():
    log("Loading context dari DB...")
    CTX["admin_id"]     = (
        q1("SELECT id FROM auth_user WHERE is_superuser=true ORDER BY id LIMIT 1") or
        q1("SELECT id FROM auth_user ORDER BY id LIMIT 1")
    )
    CTX["user_ids"]     = [r[0] for r in q("SELECT id FROM auth_user WHERE is_active=true ORDER BY id LIMIT 200")]
    CTX["location_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_locations ORDER BY id")]
    CTX["vendor_ids"]   = [r[0] for r in q("SELECT id FROM lumra_config_vendors ORDER BY id")]
    CTX["customer_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_customers WHERE is_active=true ORDER BY id LIMIT 5000")]
    CTX["variant_ids"]  = [r[0] for r in q("SELECT id FROM lumra_config_productvariants ORDER BY id LIMIT 2000")]
    CTX["unit_ids"]     = [r[0] for r in q("SELECT id FROM lumra_config_units ORDER BY id")]
    CTX["category_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_categories WHERE is_active=true ORDER BY id")]

    # FIX: gunakan parameterized query agar '%' tidak diinterpretasikan sebagai placeholder
    CTX["account_cash"]  = q1(
        "SELECT id FROM accounting_accounts WHERE code=%s OR name ILIKE %s LIMIT 1",
        ["1-1001", "%kas tunai%"]
    )
    CTX["account_ap"]    = q1(
        "SELECT id FROM accounting_accounts WHERE code=%s OR name ILIKE %s LIMIT 1",
        ["2-1001", "%hutang dagang%"]
    )
    CTX["account_inv"]   = q1(
        "SELECT id FROM accounting_accounts WHERE code LIKE %s OR name ILIKE %s LIMIT 1",
        ["1-12%", "%persediaan%"]
    )
    CTX["account_sales"] = q1(
        "SELECT id FROM accounting_accounts WHERE code LIKE %s OR name ILIKE %s LIMIT 1",
        ["4-1%", "%penjualan%"]
    )

    CTX["ap_ids"]         = [r[0] for r in q("SELECT id FROM accounting_accounts_payable ORDER BY id")]
    CTX["order_min_date"] = q1("SELECT MIN(created_at)::date FROM lumra_config_orders")
    CTX["order_max_date"] = q1("SELECT MAX(created_at)::date FROM lumra_config_orders")

    ok(
        f"Context loaded: {len(CTX['location_ids'])} locs, {len(CTX['vendor_ids'])} vendors, "
        f"{len(CTX['user_ids'])} users, {len(CTX['customer_ids'])} customers"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 1 — PROCUREMENT (PO → GRN → Stock In)
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_PURCHASE_ORDERS = """
CREATE TABLE IF NOT EXISTS lumra_procurement_purchase_orders (
    id              BIGSERIAL PRIMARY KEY,
    po_number       VARCHAR(50) UNIQUE NOT NULL,
    vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
    location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'draft',
    order_date      DATE NOT NULL,
    expected_date   DATE,
    total_amount    NUMERIC(15,2) NOT NULL DEFAULT 0,
    notes           TEXT DEFAULT '',
    created_by_id   BIGINT REFERENCES auth_user(id),
    approved_by_id  BIGINT REFERENCES auth_user(id),
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_purchase_orders IS
    'Purchase Order ke vendor. Dokumen resmi pemesanan barang.';
"""

CREATE_PO_ITEMS = """
CREATE TABLE IF NOT EXISTS lumra_procurement_po_items (
    id              BIGSERIAL PRIMARY KEY,
    po_id           BIGINT NOT NULL REFERENCES lumra_procurement_purchase_orders(id),
    variant_id      BIGINT NOT NULL REFERENCES lumra_config_productvariants(id),
    quantity        NUMERIC(12,2) NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    subtotal        NUMERIC(15,2) NOT NULL,
    received_qty    NUMERIC(12,2) DEFAULT 0,
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_po_items IS
    'Detail item per Purchase Order.';
"""

CREATE_GRN = """
CREATE TABLE IF NOT EXISTS lumra_procurement_goods_receipts (
    id              BIGSERIAL PRIMARY KEY,
    grn_number      VARCHAR(50) UNIQUE NOT NULL,
    po_id           BIGINT REFERENCES lumra_procurement_purchase_orders(id),
    vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
    location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'draft',
    receipt_date    DATE NOT NULL,
    total_received  NUMERIC(15,2) DEFAULT 0,
    notes           TEXT DEFAULT '',
    received_by_id  BIGINT REFERENCES auth_user(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_goods_receipts IS
    'Good Receipt Note (GRN) — bukti terima barang dari vendor.';
"""

CREATE_GRN_ITEMS = """
CREATE TABLE IF NOT EXISTS lumra_procurement_grn_items (
    id              BIGSERIAL PRIMARY KEY,
    grn_id          BIGINT NOT NULL REFERENCES lumra_procurement_goods_receipts(id),
    variant_id      BIGINT NOT NULL REFERENCES lumra_config_productvariants(id),
    po_item_id      BIGINT REFERENCES lumra_procurement_po_items(id),
    quantity_ordered NUMERIC(12,2) DEFAULT 0,
    quantity_received NUMERIC(12,2) NOT NULL,
    quantity_rejected NUMERIC(12,2) DEFAULT 0,
    unit_price      NUMERIC(12,2) NOT NULL,
    subtotal        NUMERIC(15,2) NOT NULL,
    batch_number    VARCHAR(100) DEFAULT '',
    expiry_date     DATE,
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_grn_items IS
    'Detail barang yang diterima per GRN.';
"""

def fill_procurement(dry_run=False):
    head("MODUL 1 — PROCUREMENT (PO + GRN)")

    if not dry_run:
        for sql, label in [
            (CREATE_PURCHASE_ORDERS, "lumra_procurement_purchase_orders"),
            (CREATE_PO_ITEMS,        "lumra_procurement_po_items"),
            (CREATE_GRN,             "lumra_procurement_goods_receipts"),
            (CREATE_GRN_ITEMS,       "lumra_procurement_grn_items"),
        ]:
            execute_sql(sql, f"CREATE {label}")

    today        = date.today()
    vendor_ids   = CTX["vendor_ids"]
    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    variant_ids  = CTX["variant_ids"]
    admin_id     = CTX["admin_id"]

    po_rows      = []
    po_item_rows = []
    grn_rows     = []
    grn_item_rows= []

    # Ambil data dari AP yang sudah ada sebagai basis PO
    if table_exists("accounting_accounts_payable"):
        ap_data = q("""
            SELECT ap.id, ap.vendor_id, ap.invoice_date, ap.total_amount, ap.status
            FROM accounting_accounts_payable ap
            ORDER BY ap.id
        """)
    else:
        ap_data = []

    po_ctr  = 1
    grn_ctr = 1

    for ap_id, vendor_id, inv_date, total_amount, ap_status in ap_data:
        if not inv_date:
            inv_date = today - timedelta(days=RNG.randint(30, 90))
        order_date    = inv_date - timedelta(days=RNG.randint(3, 14))
        expected_date = inv_date
        loc_id        = RNG.choice(location_ids)
        creator       = RNG.choice(user_ids) if user_ids else admin_id
        approver      = admin_id
        po_status     = "completed" if ap_status == "paid" else "sent"
        po_number     = f"PO-{today.year}-{po_ctr:05d}"
        po_rows.append((
            po_number, vendor_id, loc_id, po_status,
            order_date, expected_date, total_amount or 0,
            f"PO untuk vendor {vendor_id}", creator, approver,
            inv_date, inv_date, inv_date
        ))
        po_ctr += 1

    # Tambah 400 PO extra
    for i in range(400):
        days_ago   = RNG.randint(7, 730)
        order_date = today - timedelta(days=days_ago)
        exp_date   = order_date + timedelta(days=RNG.randint(3, 14))
        vendor_id  = RNG.choice(vendor_ids)
        loc_id     = RNG.choice(location_ids)
        creator    = RNG.choice(user_ids) if user_ids else admin_id
        total      = Decimal(str(RNG.randint(500000, 50000000)))
        po_status  = RNG.choices(
            ["completed","completed","sent","partial","cancelled"],
            weights=[50, 20, 15, 10, 5]
        )[0]
        po_number   = f"PO-{today.year}-{po_ctr:05d}"
        approved_at = exp_date if po_status not in ["draft","cancelled"] else None
        po_rows.append((
            po_number, vendor_id, loc_id, po_status,
            order_date, exp_date, total,
            "PO pembelian operasional", creator,
            admin_id if po_status not in ["draft","cancelled"] else None,
            approved_at,
            order_date, order_date
        ))
        po_ctr += 1

    log(f"PO rows: {len(po_rows)}")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(po_rows)} PO")
        return

    n = bulk_insert(
        "lumra_procurement_purchase_orders",
        ["po_number","vendor_id","location_id","status","order_date","expected_date",
         "total_amount","notes","created_by_id","approved_by_id","approved_at",
         "created_at","updated_at"],
        po_rows
    )
    ok(f"PO inserted: {n:,}")

    saved_pos = q("SELECT id, location_id, vendor_id, total_amount, status, order_date FROM lumra_procurement_purchase_orders ORDER BY id")

    for po_id, loc_id, vendor_id, total_amt, po_status, order_date in saved_pos:
        n_items    = RNG.randint(1, 5)
        sampled    = RNG.sample(variant_ids, min(n_items, len(variant_ids)))
        item_total = Decimal("0")

        for var_id in sampled:
            qty   = Decimal(str(RNG.randint(12, 120)))
            price = Decimal(str(RNG.randint(3000, 80000)))
            sub   = qty * price
            item_total += sub
            po_item_rows.append((po_id, var_id, qty, price, sub, 0, "", order_date))

        if po_status in ("completed", "partial"):
            grn_number = f"GRN-{today.year}-{grn_ctr:05d}"
            if isinstance(order_date, str):
                receipt_dt = today - timedelta(days=RNG.randint(1, 30))
            else:
                receipt_dt = order_date + timedelta(days=RNG.randint(1, 7))
            rcvr = RNG.choice(user_ids) if user_ids else admin_id
            grn_rows.append((
                grn_number, po_id, vendor_id, loc_id, "completed",
                receipt_dt, item_total, "GRN dari PO", rcvr,
                receipt_dt, receipt_dt
            ))
            grn_ctr += 1

    n = bulk_insert(
        "lumra_procurement_po_items",
        ["po_id","variant_id","quantity","unit_price","subtotal","received_qty","notes","created_at"],
        po_item_rows
    )
    ok(f"PO items inserted: {n:,}")

    n = bulk_insert(
        "lumra_procurement_goods_receipts",
        ["grn_number","po_id","vendor_id","location_id","status","receipt_date",
         "total_received","notes","received_by_id","created_at","updated_at"],
        grn_rows
    )
    ok(f"GRN inserted: {n:,}")

    saved_grns   = q("SELECT id, po_id FROM lumra_procurement_goods_receipts ORDER BY id")
    po_items_map = {}
    for row in q("SELECT id, po_id, variant_id, quantity, unit_price FROM lumra_procurement_po_items"):
        pi_id, po_id, var_id, qty, price = row
        po_items_map.setdefault(po_id, []).append((pi_id, var_id, qty, price))

    for grn_id, po_id in saved_grns:
        for pi_id, var_id, qty, price in po_items_map.get(po_id, []):
            rcv = qty * Decimal(str(RNG.uniform(0.9, 1.0)))
            rej = qty - rcv
            sub = rcv * price
            exp = date.today() + timedelta(days=RNG.choice([90, 180, 270, 365]))
            grn_item_rows.append((
                grn_id, var_id, pi_id, qty, rcv.quantize(Decimal("0.01")),
                rej.quantize(Decimal("0.01")),
                price, sub.quantize(Decimal("0.01")),
                f"BTH-{RNG.randint(10000,99999)}", exp, "", date.today()
            ))

    n = bulk_insert(
        "lumra_procurement_grn_items",
        ["grn_id","variant_id","po_item_id","quantity_ordered","quantity_received",
         "quantity_rejected","unit_price","subtotal","batch_number","expiry_date",
         "notes","created_at"],
        grn_item_rows
    )
    ok(f"GRN items inserted: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 2 — CUSTOMER RFM SCORES
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_RFM = """
CREATE TABLE IF NOT EXISTS lumra_crm_rfm_scores (
    id                  BIGSERIAL PRIMARY KEY,
    customer_id         BIGINT NOT NULL UNIQUE REFERENCES lumra_config_customers(id),
    recency_days        INT NOT NULL DEFAULT 0,
    frequency           INT NOT NULL DEFAULT 0,
    monetary_total      NUMERIC(15,2) NOT NULL DEFAULT 0,
    avg_order_value     NUMERIC(12,2) NOT NULL DEFAULT 0,
    r_score             SMALLINT NOT NULL DEFAULT 1,
    f_score             SMALLINT NOT NULL DEFAULT 1,
    m_score             SMALLINT NOT NULL DEFAULT 1,
    rfm_score           SMALLINT NOT NULL DEFAULT 3,
    segment             VARCHAR(30) NOT NULL DEFAULT 'new',
    first_order_date    DATE,
    last_order_date     DATE,
    calculated_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_crm_rfm_scores IS
    'RFM (Recency/Frequency/Monetary) scoring per customer. '
    'Segment: champion, loyal, at_risk, lost, new, potential, promising.';
CREATE INDEX IF NOT EXISTS idx_rfm_segment ON lumra_crm_rfm_scores(segment);
CREATE INDEX IF NOT EXISTS idx_rfm_score   ON lumra_crm_rfm_scores(rfm_score DESC);
"""

def fill_rfm(dry_run=False):
    head("MODUL 2 — CUSTOMER RFM SCORES")

    if not dry_run:
        execute_sql(CREATE_RFM, "CREATE lumra_crm_rfm_scores")

    rfm_sql = """
    SELECT
        o.customer_id,
        EXTRACT(DAY FROM NOW() - MAX(o.created_at))::int   AS recency_days,
        COUNT(o.id)                                          AS frequency,
        COALESCE(SUM(o.paid_amount), 0)                     AS monetary,
        COALESCE(AVG(o.paid_amount), 0)                     AS avg_order,
        MIN(o.created_at)::date                              AS first_date,
        MAX(o.created_at)::date                              AS last_date
    FROM lumra_config_orders o
    WHERE o.customer_id IS NOT NULL
      AND o.status = 'completed'
    GROUP BY o.customer_id
    """

    log("Menghitung RFM dari orders...")
    t0 = time.time()
    rfm_data = q(rfm_sql)
    log(f"RFM dihitung untuk {len(rfm_data):,} customers ({time.time()-t0:.1f}s)")

    if not rfm_data:
        cust_ids = CTX["customer_ids"]
        log(f"Fallback: generate RFM dari {len(cust_ids)} customers tanpa order history")
        rfm_data = [
            (cid, RNG.randint(1, 365), RNG.randint(1, 50),
             RNG.randint(50000, 5000000), RNG.randint(50000, 500000),
             date.today() - timedelta(days=RNG.randint(30, 730)),
             date.today() - timedelta(days=RNG.randint(1, 30)))
            for cid in cust_ids
        ]

    recencies   = sorted([r[1] for r in rfm_data])
    frequencies = sorted([r[2] for r in rfm_data])
    monetaries  = sorted([r[3] for r in rfm_data])

    def pctile_score(val, sorted_list, reverse=False):
        idx   = sorted_list.index(val) / max(1, len(sorted_list)-1)
        score = int(idx * 4) + 1
        return (6 - score) if reverse else score

    segments = {
        (5,5): "champion",      (5,4): "champion",       (4,5): "loyal",
        (4,4): "loyal",         (3,5): "potential",      (3,4): "potential",
        (5,3): "at_risk",       (4,3): "at_risk",        (3,3): "promising",
        (2,5): "cannot_lose",   (2,4): "cannot_lose",    (1,5): "lost_big",
        (1,4): "lost_big",      (2,3): "at_risk",        (1,3): "lost",
        (5,2): "need_attention",(4,2): "need_attention", (3,2): "hibernating",
        (2,2): "hibernating",   (1,2): "lost",           (5,1): "new",
        (4,1): "new",           (3,1): "new",            (2,1): "lost",
        (1,1): "lost",
    }

    rows = []
    now  = datetime.now()
    for cid, rec, freq, mon, avg, first_dt, last_dt in rfm_data:
        r = pctile_score(rec, recencies, reverse=True)
        f = pctile_score(freq, frequencies)
        m = pctile_score(mon, monetaries)
        r, f, m  = max(1, min(5,r)), max(1, min(5,f)), max(1, min(5,m))
        rfm_total = r + f + m
        seg       = segments.get((r,f), segments.get((r,3), "promising"))
        rows.append((
            cid, int(rec), int(freq),
            Decimal(str(mon)).quantize(Decimal("0.01")),
            Decimal(str(avg)).quantize(Decimal("0.01")),
            r, f, m, rfm_total, seg,
            first_dt, last_dt,
            now, now
        ))

    log(f"RFM rows: {len(rows):,}")
    if dry_run:
        from collections import Counter
        segs = Counter(r[9] for r in rows)
        log("[DRY RUN] Segment distribution:")
        for seg, cnt in segs.most_common():
            print(f"      {seg:<20} {cnt:>6,}")
        return

    n = bulk_insert(
        "lumra_crm_rfm_scores",
        ["customer_id","recency_days","frequency","monetary_total","avg_order_value",
         "r_score","f_score","m_score","rfm_score","segment",
         "first_order_date","last_order_date","calculated_at","updated_at"],
        rows,
        on_conflict="ON CONFLICT (customer_id) DO UPDATE SET "
                    "recency_days=EXCLUDED.recency_days, frequency=EXCLUDED.frequency, "
                    "monetary_total=EXCLUDED.monetary_total, rfm_score=EXCLUDED.rfm_score, "
                    "segment=EXCLUDED.segment, updated_at=EXCLUDED.updated_at"
    )
    ok(f"RFM rows: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 3 — PROMOTIONS
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_PROMOTIONS = """
CREATE TABLE IF NOT EXISTS lumra_sales_promotions (
    id              BIGSERIAL PRIMARY KEY,
    code            VARCHAR(30) UNIQUE NOT NULL,
    name            VARCHAR(150) NOT NULL,
    description     TEXT DEFAULT '',
    promo_type      VARCHAR(30) NOT NULL,
    discount_type   VARCHAR(20) NOT NULL DEFAULT 'percentage',
    discount_value  NUMERIC(10,2) NOT NULL DEFAULT 0,
    min_purchase    NUMERIC(12,2) DEFAULT 0,
    max_discount    NUMERIC(12,2),
    applicable_session VARCHAR(20) DEFAULT 'all',
    applicable_hour_start SMALLINT DEFAULT 0,
    applicable_hour_end   SMALLINT DEFAULT 23,
    valid_from      DATE NOT NULL,
    valid_until     DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    usage_limit     INT,
    usage_count     INT DEFAULT 0,
    created_by_id   BIGINT REFERENCES auth_user(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_sales_promotions IS
    'Promo Kafe Nusantara: Morning Ration, Transit Special, Curator Share, dll.';
"""

CREATE_PROMO_USAGE = """
CREATE TABLE IF NOT EXISTS lumra_sales_promotion_usage (
    id              BIGSERIAL PRIMARY KEY,
    promotion_id    BIGINT NOT NULL REFERENCES lumra_sales_promotions(id),
    order_id        BIGINT NOT NULL REFERENCES lumra_config_orders(id),
    customer_id     BIGINT REFERENCES lumra_config_customers(id),
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    used_at         TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_promo_usage_order ON lumra_sales_promotion_usage(order_id);
CREATE INDEX IF NOT EXISTS idx_promo_usage_promo ON lumra_sales_promotion_usage(promotion_id);
"""

PROMOTIONS_DATA = [
    ("MR-BASIC",   "Morning Ration Basic",
     "Filter coffee house blend + croissant plain.",
     "bundle",     "percentage", 15, 0,       50000,  "first_light",      7,  12),
    ("MR-SELECT",  "Morning Ration Select",
     "Single origin pilihan + pastry seasonal.",
     "bundle",     "percentage", 10, 0,       75000,  "first_light",      7,  12),
    ("MR-CURATED", "Morning Ration Curated",
     "Speciality blend + granola bowl artisan. Bonus stamp.",
     "bundle",     "percentage",  5, 0,       100000, "first_light",      7,  12),
    ("CT-COLD",    "Cold Transit",
     "Es kopi susu any size + cold dessert pilihan.",
     "bundle",     "percentage", 20, 0,       60000,  "midday_transit",   12, 18),
    ("CT-RECHARGE","Recharge Combo",
     "Cold brew + savory sandwich.",
     "bundle",     "percentage", 15, 0,       50000,  "midday_transit",   12, 18),
    ("CT-AFTERNOON","Afternoon Pairing",
     "Racikan dingin Speciality + artisan dessert. Bonus stamp.",
     "bundle",     "percentage", 10, 0,       80000,  "midday_transit",   12, 18),
    ("TB-SHARED",  "The Curator's Share — Shared Brew",
     "2x racikan seasonal pilihan barista.",
     "bundle",     "percentage", 25, 0,       100000, "twilight_bivouac", 18, 23),
    ("TB-DUO",     "The Curator's Duo",
     "2x Speciality Blend bebas pilihan. Bonus 2 stamps.",
     "bundle",     "percentage", 20, 0,       150000, "twilight_bivouac", 18, 23),
    ("TB-GRAND",   "Grand Share",
     "2x signature mocktail + 1 savory sharing.",
     "bundle",     "percentage", 15, 0,       200000, "twilight_bivouac", 18, 23),
    ("PASSPORT-5", "Expedition Passport 5 Outpost",
     "Field Surveyor — Diskon permanent 5% untuk member.",
     "loyalty",    "percentage",  5, 0,       None,   "all",              0,  23),
    ("PASSPORT-10","Expedition Passport 10 Outpost",
     "Senior Cartographer — Early access menu seasonal.",
     "loyalty",    "percentage",  8, 0,       None,   "all",              0,  23),
    ("VOUCHER-50K","Voucher Rp 50.000",
     "Voucher nominal Rp 50.000 untuk pembelian minimum Rp 150.000.",
     "voucher",    "fixed",   50000, 150000,  None,   "all",              0,  23),
    ("VOUCHER-100K","Voucher Rp 100.000",
     "Voucher nominal Rp 100.000 untuk pembelian minimum Rp 300.000.",
     "voucher",    "fixed",  100000, 300000,  None,   "all",              0,  23),
    ("BIRTHDAY",   "Birthday Privilege",
     "Diskon 20% di hari ulang tahun customer.",
     "birthday",   "percentage", 20, 0,       100000, "all",              0,  23),
    ("WEEKEND-10", "Weekend Expedition",
     "10% untuk semua order di Sabtu-Minggu.",
     "seasonal",   "percentage", 10, 0,       75000,  "all",              0,  23),
    ("NEW-MEMBER", "Welcome Expeditor",
     "15% untuk order pertama member baru.",
     "onboarding", "percentage", 15, 0,       50000,  "all",              0,  23),
    ("GRAND-RESERVE","Grand Reserve Access",
     "Akses eksklusif Grand Reserve menu.",
     "loyalty",    "percentage",  0, 0,       None,   "all",              0,  23),
    ("MULTI-BUY-2","Multi Buy — Beli 2 Gratis 1 Pastry",
     "Beli 2 minuman utama, gratis 1 pastry pilihan.",
     "multi_buy",  "fixed",   25000, 80000,   25000,  "all",              0,  23),
    ("RAMADAN",    "Ramadan Special",
     "Diskon 10% setelah Maghrib selama bulan Ramadan.",
     "seasonal",   "percentage", 10, 0,       50000,  "twilight_bivouac", 18, 23),
    ("ANNIVERSARY","Anniversary Kafe Nusantara",
     "Hari jadi Kafe Nusantara — diskon spesial 25%.",
     "seasonal",   "percentage", 25, 50000,   200000, "all",              0,  23),
]

def fill_promotions(dry_run=False):
    head("MODUL 3 — PROMOTIONS & USAGE")

    if not dry_run:
        execute_sql(CREATE_PROMOTIONS, "CREATE lumra_sales_promotions")
        execute_sql(CREATE_PROMO_USAGE, "CREATE lumra_sales_promotion_usage")

    today    = date.today()
    admin_id = CTX["admin_id"]
    promo_rows = []

    for code, name, desc, ptype, disc_type, disc_val, min_pur, max_disc, session, hs, he in PROMOTIONS_DATA:
        promo_rows.append((
            code, name, desc, ptype, disc_type,
            Decimal(str(disc_val)),
            Decimal(str(min_pur)) if min_pur else Decimal("0"),
            Decimal(str(max_disc)) if max_disc else None,
            session, hs, he,
            date(2019, 1, 1), None, True, None, 0,
            admin_id, today, today
        ))

    log(f"Promotions: {len(promo_rows)}")
    if dry_run:
        log("[DRY RUN] Akan insert 20 promotions + ~20% order usage")
        return

    n = bulk_insert(
        "lumra_sales_promotions",
        ["code","name","description","promo_type","discount_type","discount_value",
         "min_purchase","max_discount","applicable_session",
         "applicable_hour_start","applicable_hour_end",
         "valid_from","valid_until","is_active","usage_limit","usage_count",
         "created_by_id","created_at","updated_at"],
        promo_rows,
        on_conflict="ON CONFLICT (code) DO NOTHING"
    )
    ok(f"Promotions inserted: {n}")

    promo_ids = [r[0] for r in q("SELECT id FROM lumra_sales_promotions ORDER BY id")]
    if not promo_ids:
        warn("Tidak ada promo tersimpan — skip usage")
        return

    orders = q("""
        SELECT id, customer_id, paid_amount, created_at
        FROM lumra_config_orders
        WHERE status='completed'
        ORDER BY id
        LIMIT 200000
    """)

    usage_rows = []
    t0 = time.time()
    for i, (oid, cid, paid, created_at) in enumerate(orders):
        if RNG.random() > 0.20:
            continue
        promo_id = RNG.choice(promo_ids)
        disc     = Decimal(str(paid or 0)) * Decimal(str(round(RNG.uniform(0.05, 0.25), 2)))
        usage_rows.append((promo_id, oid, cid, disc.quantize(Decimal("0.01")), created_at))
        if i % 10000 == 0:
            progress(i, len(orders), t0, "promo usage")

    print()
    n = bulk_insert(
        "lumra_sales_promotion_usage",
        ["promotion_id","order_id","customer_id","discount_amount","used_at"],
        usage_rows
    )
    ok(f"Promotion usage: {n:,}")

    execute_sql("""
        UPDATE lumra_sales_promotions p
        SET usage_count = (
            SELECT COUNT(*) FROM lumra_sales_promotion_usage u WHERE u.promotion_id = p.id
        )
    """, "Update usage_count")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 4 — SALES AGGREGATES (daily + monthly)
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_SALES_DAILY = """
CREATE TABLE IF NOT EXISTS lumra_report_sales_daily (
    id              BIGSERIAL PRIMARY KEY,
    report_date     DATE NOT NULL,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    total_orders    INT NOT NULL DEFAULT 0,
    total_revenue   NUMERIC(15,2) NOT NULL DEFAULT 0,
    total_items_sold INT NOT NULL DEFAULT 0,
    avg_order_value NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_returns   INT NOT NULL DEFAULT 0,
    return_value    NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_revenue     NUMERIC(15,2) NOT NULL DEFAULT 0,
    cash_sales      NUMERIC(15,2) DEFAULT 0,
    qris_sales      NUMERIC(15,2) DEFAULT 0,
    transfer_sales  NUMERIC(15,2) DEFAULT 0,
    card_sales      NUMERIC(15,2) DEFAULT 0,
    new_customers   INT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(report_date, location_id)
);
CREATE INDEX IF NOT EXISTS idx_sales_daily_date ON lumra_report_sales_daily(report_date DESC);
CREATE INDEX IF NOT EXISTS idx_sales_daily_loc  ON lumra_report_sales_daily(location_id);
COMMENT ON TABLE lumra_report_sales_daily IS
    'Agregasi penjualan harian per lokasi. Di-refresh tiap malam via cron.';
"""

CREATE_SALES_MONTHLY = """
CREATE TABLE IF NOT EXISTS lumra_report_sales_monthly (
    id              BIGSERIAL PRIMARY KEY,
    year            SMALLINT NOT NULL,
    month           SMALLINT NOT NULL,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    total_orders    INT NOT NULL DEFAULT 0,
    total_revenue   NUMERIC(15,2) NOT NULL DEFAULT 0,
    total_items_sold INT NOT NULL DEFAULT 0,
    avg_order_value NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_returns   INT NOT NULL DEFAULT 0,
    return_value    NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_revenue     NUMERIC(15,2) NOT NULL DEFAULT 0,
    target_amount   NUMERIC(15,2) DEFAULT 0,
    achievement_pct NUMERIC(6,2)  DEFAULT 0,
    mom_growth_pct  NUMERIC(6,2)  DEFAULT 0,
    yoy_growth_pct  NUMERIC(6,2)  DEFAULT 0,
    new_customers   INT DEFAULT 0,
    active_customers INT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(year, month, location_id)
);
CREATE INDEX IF NOT EXISTS idx_sales_monthly_ym ON lumra_report_sales_monthly(year DESC, month DESC);
COMMENT ON TABLE lumra_report_sales_monthly IS
    'Agregasi penjualan bulanan per lokasi. Include vs target & growth metrics.';
"""

def fill_sales_agg(dry_run=False):
    head("MODUL 4 — SALES AGGREGATES (daily + monthly)")

    if not dry_run:
        execute_sql(CREATE_SALES_DAILY, "CREATE lumra_report_sales_daily")
        execute_sql(CREATE_SALES_MONTHLY, "CREATE lumra_report_sales_monthly")

    log("Menghitung sales daily dari orders...")
    t0 = time.time()

    daily_raw = q("""
        SELECT
            DATE(o.created_at)             AS report_date,
            COUNT(o.id)                    AS total_orders,
            COALESCE(SUM(o.paid_amount),0) AS total_revenue,
            COALESCE(AVG(o.paid_amount),0) AS avg_order,
            SUM(CASE WHEN o.payment_method='cash'     THEN o.paid_amount ELSE 0 END) AS cash,
            SUM(CASE WHEN o.payment_method='qris'     THEN o.paid_amount ELSE 0 END) AS qris,
            SUM(CASE WHEN o.payment_method='transfer' THEN o.paid_amount ELSE 0 END) AS trf,
            SUM(CASE WHEN o.payment_method='card'     THEN o.paid_amount ELSE 0 END) AS card
        FROM lumra_config_orders o
        WHERE o.status = 'completed'
        GROUP BY DATE(o.created_at)
        ORDER BY report_date
    """)

    ret_raw = q("""
        SELECT DATE(r.created_at) AS rdate, COUNT(*) AS cnt, COALESCE(SUM(r.total_amount),0) AS val
        FROM lumra_config_returns r
        GROUP BY DATE(r.created_at)
    """)
    ret_map = {r[0]: (r[1], r[2]) for r in ret_raw}

    items_raw = q("""
        SELECT DATE(o.created_at), SUM(oi.quantity)
        FROM lumra_config_orders o
        JOIN lumra_config_orderitems oi ON oi.order_id = o.id
        WHERE o.status='completed'
        GROUP BY DATE(o.created_at)
    """)
    items_map = {r[0]: r[1] for r in items_raw}

    daily_rows = []
    now        = datetime.now()

    for rdate, n_ord, rev, avg, cash, qris, trf, card in daily_raw:
        ret_cnt, ret_val = ret_map.get(rdate, (0, 0))
        items_sold       = items_map.get(rdate, 0) or 0
        net_rev          = Decimal(str(rev)) - Decimal(str(ret_val))
        daily_rows.append((
            rdate, None, int(n_ord),
            Decimal(str(rev)).quantize(Decimal("0.01")),
            int(items_sold),
            Decimal(str(avg)).quantize(Decimal("0.01")),
            int(ret_cnt),
            Decimal(str(ret_val)).quantize(Decimal("0.01")),
            net_rev.quantize(Decimal("0.01")),
            Decimal(str(cash)).quantize(Decimal("0.01")),
            Decimal(str(qris)).quantize(Decimal("0.01")),
            Decimal(str(trf)).quantize(Decimal("0.01")),
            Decimal(str(card)).quantize(Decimal("0.01")),
            0, now
        ))

    log(f"Daily rows: {len(daily_rows):,} ({time.time()-t0:.1f}s)")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(daily_rows)} daily rows")
    else:
        n = bulk_insert(
            "lumra_report_sales_daily",
            ["report_date","location_id","total_orders","total_revenue","total_items_sold",
             "avg_order_value","total_returns","return_value","net_revenue",
             "cash_sales","qris_sales","transfer_sales","card_sales","new_customers","created_at"],
            daily_rows,
            on_conflict="ON CONFLICT (report_date, location_id) DO UPDATE SET "
                        "total_orders=EXCLUDED.total_orders, total_revenue=EXCLUDED.total_revenue, "
                        "net_revenue=EXCLUDED.net_revenue"
        )
        ok(f"Sales daily: {n:,}")

    log("Menghitung sales monthly...")
    monthly_raw = q("""
        SELECT
            EXTRACT(YEAR FROM o.created_at)::int  AS yr,
            EXTRACT(MONTH FROM o.created_at)::int AS mo,
            COUNT(o.id)                           AS total_orders,
            COALESCE(SUM(o.paid_amount),0)        AS total_revenue,
            COALESCE(AVG(o.paid_amount),0)        AS avg_order,
            COUNT(DISTINCT o.customer_id)         AS active_customers
        FROM lumra_config_orders o
        WHERE o.status = 'completed'
        GROUP BY yr, mo
        ORDER BY yr, mo
    """)

    ret_monthly = q("""
        SELECT EXTRACT(YEAR FROM created_at)::int, EXTRACT(MONTH FROM created_at)::int,
               COUNT(*), COALESCE(SUM(total_amount),0)
        FROM lumra_config_returns GROUP BY 1,2
    """)
    ret_m_map = {(r[0],r[1]):(r[2],r[3]) for r in ret_monthly}

    targets    = q("SELECT year, month, target_amount FROM lumra_config_sales_targets")
    target_map = {(r[0],r[1]): r[2] for r in targets}

    monthly_rows = []
    prev_revenue = {}

    for yr, mo, n_ord, rev, avg, active_custs in monthly_raw:
        ret_cnt, ret_val = ret_m_map.get((yr, mo), (0, 0))
        net_rev = Decimal(str(rev)) - Decimal(str(ret_val))
        target  = target_map.get((yr, mo), None) or Decimal("0")
        achieve = (Decimal(str(rev)) / Decimal(str(target)) * 100).quantize(Decimal("0.01")) \
                  if target and Decimal(str(target)) > 0 else Decimal("0")

        prev_mo  = (yr, mo-1) if mo > 1 else (yr-1, 12)
        prev_rev = prev_revenue.get(prev_mo, Decimal("0"))
        mom = ((Decimal(str(rev)) - prev_rev) / prev_rev * 100).quantize(Decimal("0.01")) \
              if prev_rev > 0 else Decimal("0")

        yoy_rev = prev_revenue.get((yr-1, mo), Decimal("0"))
        yoy = ((Decimal(str(rev)) - yoy_rev) / yoy_rev * 100).quantize(Decimal("0.01")) \
              if yoy_rev > 0 else Decimal("0")

        prev_revenue[(yr, mo)] = Decimal(str(rev))

        monthly_rows.append((
            yr, mo, None,
            int(n_ord),
            Decimal(str(rev)).quantize(Decimal("0.01")),
            0,
            Decimal(str(avg)).quantize(Decimal("0.01")),
            int(ret_cnt),
            Decimal(str(ret_val)).quantize(Decimal("0.01")),
            net_rev.quantize(Decimal("0.01")),
            Decimal(str(target)).quantize(Decimal("0.01")),
            achieve, mom, yoy,
            0, int(active_custs),
            datetime.now(), datetime.now()
        ))

    log(f"Monthly rows: {len(monthly_rows):,}")
    if not dry_run:
        n = bulk_insert(
            "lumra_report_sales_monthly",
            ["year","month","location_id","total_orders","total_revenue","total_items_sold",
             "avg_order_value","total_returns","return_value","net_revenue",
             "target_amount","achievement_pct","mom_growth_pct","yoy_growth_pct",
             "new_customers","active_customers","created_at","updated_at"],
            monthly_rows,
            on_conflict="ON CONFLICT (year, month, location_id) DO UPDATE SET "
                        "total_revenue=EXCLUDED.total_revenue, net_revenue=EXCLUDED.net_revenue, "
                        "achievement_pct=EXCLUDED.achievement_pct, updated_at=EXCLUDED.updated_at"
        )
        ok(f"Sales monthly: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 5 — PRODUCT PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_PRODUCT_PERF = """
CREATE TABLE IF NOT EXISTS lumra_report_product_performance (
    id                  BIGSERIAL PRIMARY KEY,
    variant_id          BIGINT NOT NULL UNIQUE REFERENCES lumra_config_productvariants(id),
    total_sold_qty      NUMERIC(15,2) DEFAULT 0,
    total_sold_revenue  NUMERIC(15,2) DEFAULT 0,
    total_sold_cogs     NUMERIC(15,2) DEFAULT 0,
    gross_margin        NUMERIC(15,2) DEFAULT 0,
    margin_pct          NUMERIC(6,2) DEFAULT 0,
    avg_selling_price   NUMERIC(12,2) DEFAULT 0,
    total_orders        INT DEFAULT 0,
    total_returns       INT DEFAULT 0,
    return_rate_pct     NUMERIC(6,2) DEFAULT 0,
    current_stock       NUMERIC(15,2) DEFAULT 0,
    stock_turnover_rate NUMERIC(8,2) DEFAULT 0,
    velocity_label      VARCHAR(20) DEFAULT 'normal',
    last_sold_date      DATE,
    calculated_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_prod_perf_velocity ON lumra_report_product_performance(velocity_label);
CREATE INDEX IF NOT EXISTS idx_prod_perf_margin   ON lumra_report_product_performance(margin_pct DESC);
COMMENT ON TABLE lumra_report_product_performance IS
    'Performa per produk: revenue, margin, turnover, velocity (fast/slow moving).';
"""

def fill_product_perf(dry_run=False):
    head("MODUL 5 — PRODUCT PERFORMANCE")

    if not dry_run:
        execute_sql(CREATE_PRODUCT_PERF, "CREATE lumra_report_product_performance")

    log("Menghitung product performance dari orderitems...")
    t0 = time.time()

    perf_raw = q("""
        SELECT
            oi.variant_id,
            SUM(oi.quantity)                              AS qty_sold,
            SUM(oi.price * oi.quantity)                   AS revenue,
            SUM(COALESCE(oi.cost_price,0) * oi.quantity) AS cogs,
            AVG(oi.price)                                 AS avg_price,
            COUNT(DISTINCT oi.order_id)                   AS n_orders,
            MAX(o.created_at)::date                       AS last_sold
        FROM lumra_config_orderitems oi
        JOIN lumra_config_orders o ON o.id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY oi.variant_id
        LIMIT 50000
    """)

    stock_raw = q("""
        SELECT variant_id, SUM(quantity) AS total_stock
        FROM lumra_config_stock
        GROUP BY variant_id
    """)
    stock_map = {r[0]: Decimal(str(r[1])) for r in stock_raw}

    ret_raw = q("""
        SELECT ri.product_id, COUNT(*)
        FROM lumra_config_returnitems ri
        GROUP BY ri.product_id
    """)
    ret_map = {r[0]: r[1] for r in ret_raw}

    rows = []
    now  = datetime.now()

    all_revenues = sorted([float(r[2] or 0) for r in perf_raw], reverse=True)
    p80 = all_revenues[int(len(all_revenues)*0.2)] if all_revenues else 0
    p20 = all_revenues[int(len(all_revenues)*0.8)] if all_revenues else 0

    for var_id, qty, rev, cogs, avg_price, n_ord, last_sold in perf_raw:
        rev    = Decimal(str(rev or 0))
        cogs   = Decimal(str(cogs or 0))
        qty    = Decimal(str(qty or 0))
        margin = rev - cogs
        margin_pct = (margin/rev*100).quantize(Decimal("0.01")) if rev > 0 else Decimal("0")

        curr_stock = stock_map.get(var_id, Decimal("0"))
        turnover   = (qty / curr_stock).quantize(Decimal("0.01")) if curr_stock > 0 else Decimal("0")

        ret_cnt  = ret_map.get(var_id, 0)
        ret_rate = (Decimal(str(ret_cnt)) / Decimal(str(n_ord)) * 100).quantize(Decimal("0.01")) \
                   if n_ord > 0 else Decimal("0")

        velocity = ("fast_moving" if float(rev) >= p80
                    else "slow_moving" if float(rev) <= p20
                    else "normal")

        rows.append((
            var_id, qty.quantize(Decimal("0.01")),
            rev.quantize(Decimal("0.01")), cogs.quantize(Decimal("0.01")),
            margin.quantize(Decimal("0.01")), margin_pct,
            Decimal(str(avg_price or 0)).quantize(Decimal("0.01")),
            int(n_ord), int(ret_cnt), ret_rate,
            curr_stock.quantize(Decimal("0.01")), turnover,
            velocity, last_sold, now
        ))

    log(f"Product perf rows: {len(rows):,} ({time.time()-t0:.1f}s)")
    if dry_run:
        fast = sum(1 for r in rows if r[12]=="fast_moving")
        slow = sum(1 for r in rows if r[12]=="slow_moving")
        log(f"[DRY RUN] fast={fast:,} normal={len(rows)-fast-slow:,} slow={slow:,}")
        return

    n = bulk_insert(
        "lumra_report_product_performance",
        ["variant_id","total_sold_qty","total_sold_revenue","total_sold_cogs",
         "gross_margin","margin_pct","avg_selling_price","total_orders","total_returns",
         "return_rate_pct","current_stock","stock_turnover_rate","velocity_label",
         "last_sold_date","calculated_at"],
        rows,
        on_conflict="ON CONFLICT (variant_id) DO UPDATE SET "
                    "total_sold_qty=EXCLUDED.total_sold_qty, "
                    "total_sold_revenue=EXCLUDED.total_sold_revenue, "
                    "margin_pct=EXCLUDED.margin_pct, "
                    "velocity_label=EXCLUDED.velocity_label, "
                    "calculated_at=EXCLUDED.calculated_at"
    )
    ok(f"Product performance: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 6 — INVENTORY SNAPSHOT MONTHLY
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_INV_SNAPSHOT = """
CREATE TABLE IF NOT EXISTS lumra_report_inventory_snapshot (
    id              BIGSERIAL PRIMARY KEY,
    snapshot_year   SMALLINT NOT NULL,
    snapshot_month  SMALLINT NOT NULL,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
    qty_opening     NUMERIC(15,2) DEFAULT 0,
    qty_in          NUMERIC(15,2) DEFAULT 0,
    qty_out         NUMERIC(15,2) DEFAULT 0,
    qty_closing     NUMERIC(15,2) DEFAULT 0,
    qty_on_hand     NUMERIC(15,2) DEFAULT 0,
    value_on_hand   NUMERIC(15,2) DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(snapshot_year, snapshot_month, location_id, variant_id)
);
CREATE INDEX IF NOT EXISTS idx_inv_snap_ym ON lumra_report_inventory_snapshot(snapshot_year DESC, snapshot_month DESC);
COMMENT ON TABLE lumra_report_inventory_snapshot IS
    'Snapshot stok akhir bulan — untuk audit akuntansi tanpa re-query seluruh mutasi.';
"""

def fill_inv_snapshot(dry_run=False):
    head("MODUL 6 — INVENTORY SNAPSHOT MONTHLY")

    if not dry_run:
        execute_sql(CREATE_INV_SNAPSHOT, "CREATE lumra_report_inventory_snapshot")

    log("Generating snapshot dari stockmovement per bulan...")
    t0 = time.time()

    # FIX: ILIKE '%in%' dan '%out%' aman di sini karena tidak ada params=[] — driver tidak parse %
    snap_raw = q("""
        SELECT
            EXTRACT(YEAR  FROM created_at)::int AS yr,
            EXTRACT(MONTH FROM created_at)::int AS mo,
            location_id,
            product_id AS variant_id,
            SUM(CASE WHEN movement_type ILIKE '%in%'  THEN quantity ELSE 0 END) AS qty_in,
            SUM(CASE WHEN movement_type ILIKE '%out%' THEN quantity ELSE 0 END) AS qty_out
        FROM lumra_config_stockmovement
        GROUP BY yr, mo, location_id, product_id
        ORDER BY yr, mo
        LIMIT 500000
    """)

    curr_stock = q("""
        SELECT location_id, variant_id, quantity
        FROM lumra_config_stock
        LIMIT 500000
    """)
    stock_map = {(r[0],r[1]): Decimal(str(r[2])) for r in curr_stock}

    rows = []
    now  = datetime.now()

    for yr, mo, loc_id, var_id, qty_in, qty_out in snap_raw:
        qty_in  = Decimal(str(qty_in  or 0))
        qty_out = Decimal(str(qty_out or 0))
        qty_net = qty_in - qty_out
        on_hand = stock_map.get((loc_id, var_id), Decimal("0"))
        opening = on_hand - qty_net
        rows.append((
            int(yr), int(mo), loc_id, var_id,
            opening.quantize(Decimal("0.01")),
            qty_in.quantize(Decimal("0.01")),
            qty_out.quantize(Decimal("0.01")),
            (opening + qty_net).quantize(Decimal("0.01")),
            on_hand.quantize(Decimal("0.01")),
            Decimal("0"),
            now
        ))

    log(f"Snapshot rows: {len(rows):,} ({time.time()-t0:.1f}s)")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(rows):,} snapshot rows")
        return

    n = bulk_insert(
        "lumra_report_inventory_snapshot",
        ["snapshot_year","snapshot_month","location_id","variant_id",
         "qty_opening","qty_in","qty_out","qty_closing","qty_on_hand",
         "value_on_hand","created_at"],
        rows, batch=3000,
        on_conflict="ON CONFLICT (snapshot_year,snapshot_month,location_id,variant_id) DO NOTHING"
    )
    ok(f"Inventory snapshot: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 7 — SHIFTS + SHIFT SALES SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_SHIFTS = """
CREATE TABLE IF NOT EXISTS lumra_ops_shifts (
    id              BIGSERIAL PRIMARY KEY,
    shift_code      VARCHAR(50) UNIQUE NOT NULL,
    location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
    shift_date      DATE NOT NULL,
    shift_type      VARCHAR(20) NOT NULL,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ,
    opened_by_id    BIGINT REFERENCES auth_user(id),
    closed_by_id    BIGINT REFERENCES auth_user(id),
    opening_cash    NUMERIC(12,2) DEFAULT 0,
    closing_cash    NUMERIC(12,2) DEFAULT 0,
    expected_cash   NUMERIC(12,2) DEFAULT 0,
    cash_variance   NUMERIC(12,2) DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'closed',
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_shifts_date ON lumra_ops_shifts(shift_date DESC);
CREATE INDEX IF NOT EXISTS idx_shifts_loc  ON lumra_ops_shifts(location_id);
COMMENT ON TABLE lumra_ops_shifts IS
    'Data shift kerja per outpost. 3 shift: First Light (7-12), Midday (12-18), Twilight (18-close).';
"""

CREATE_SHIFT_SUMMARY = """
CREATE TABLE IF NOT EXISTS lumra_ops_shift_sales_summary (
    id              BIGSERIAL PRIMARY KEY,
    shift_id        BIGINT NOT NULL REFERENCES lumra_ops_shifts(id),
    total_orders    INT DEFAULT 0,
    total_revenue   NUMERIC(15,2) DEFAULT 0,
    cash_received   NUMERIC(12,2) DEFAULT 0,
    qris_received   NUMERIC(12,2) DEFAULT 0,
    other_received  NUMERIC(12,2) DEFAULT 0,
    total_items     INT DEFAULT 0,
    avg_order_value NUMERIC(12,2) DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shift_id)
);
COMMENT ON TABLE lumra_ops_shift_sales_summary IS
    'Ringkasan penjualan per shift. Link ke shift_id dari lumra_ops_shifts.';
"""

def fill_shifts(dry_run=False):
    head("MODUL 7 — SHIFTS & SHIFT SALES SUMMARY")

    if not dry_run:
        execute_sql(CREATE_SHIFTS, "CREATE lumra_ops_shifts")
        execute_sql(CREATE_SHIFT_SUMMARY, "CREATE lumra_ops_shift_sales_summary")

    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    min_date = CTX["order_min_date"] or date(2023, 1, 1)
    max_date = CTX["order_max_date"] or date.today()

    SHIFT_TYPES = [
        ("first_light",      7,  12, "First Light"),
        ("midday_transit",   12, 18, "Midday Transit"),
        ("twilight_bivouac", 18, 23, "Twilight Bivouac"),
    ]

    shift_rows = []
    current    = min_date
    shift_ctr  = 1

    log(f"Generating shifts: {min_date} → {max_date}, {len(location_ids)} lokasi × 3 shift")
    t0         = time.time()
    total_days = (max_date - min_date).days + 1
    day_idx    = 0

    while current <= max_date:
        for loc_id in location_ids:
            opener       = RNG.choice(user_ids) if user_ids else admin_id
            closer       = RNG.choice(user_ids) if user_ids else admin_id
            opening_cash = Decimal(str(RNG.randint(500000, 2000000)))

            for stype, sh, eh, slabel in SHIFT_TYPES:
                code     = f"SHF-{current.strftime('%Y%m%d')}-{loc_id}-{stype[:2].upper()}"
                start_dt = datetime(current.year, current.month, current.day, sh, 0)
                end_dt   = datetime(current.year, current.month, current.day, eh, 0)
                exp_cash = opening_cash + Decimal(str(RNG.randint(100000, 5000000)))
                actual_cash = exp_cash * Decimal(str(RNG.uniform(0.95, 1.05)))
                variance    = actual_cash - exp_cash

                shift_rows.append((
                    code, loc_id, current, stype,
                    start_dt, end_dt,
                    opener, closer,
                    opening_cash.quantize(Decimal("0.01")),
                    actual_cash.quantize(Decimal("0.01")),
                    exp_cash.quantize(Decimal("0.01")),
                    variance.quantize(Decimal("0.01")),
                    "closed", "", current
                ))
                shift_ctr += 1

        if day_idx % 100 == 0:
            progress(day_idx, total_days, t0, "generating shifts")
        current += timedelta(days=1)
        day_idx += 1

    print()
    log(f"Shift rows: {len(shift_rows):,}")

    if dry_run:
        log(f"[DRY RUN] Akan insert {len(shift_rows):,} shifts")
        return

    n = bulk_insert(
        "lumra_ops_shifts",
        ["shift_code","location_id","shift_date","shift_type","start_time","end_time",
         "opened_by_id","closed_by_id","opening_cash","closing_cash","expected_cash",
         "cash_variance","status","notes","created_at"],
        shift_rows, batch=3000,
        on_conflict="ON CONFLICT (shift_code) DO NOTHING"
    )
    ok(f"Shifts inserted: {n:,}")

    log("Generating shift_sales_summary dari orders.shift_id...")
    saved_shifts = q("SELECT id, shift_code FROM lumra_ops_shifts ORDER BY id LIMIT 100000")
    shift_id_map = {r[1]: r[0] for r in saved_shifts}

    order_agg = q("""
        SELECT
            o.shift_id,
            COUNT(o.id)                    AS n_orders,
            COALESCE(SUM(o.paid_amount),0) AS revenue,
            SUM(CASE WHEN o.payment_method='cash' THEN o.paid_amount ELSE 0 END),
            SUM(CASE WHEN o.payment_method='qris' THEN o.paid_amount ELSE 0 END),
            SUM(CASE WHEN o.payment_method NOT IN ('cash','qris') THEN o.paid_amount ELSE 0 END),
            COUNT(DISTINCT oi.id) AS total_items
        FROM lumra_config_orders o
        LEFT JOIN lumra_config_orderitems oi ON oi.order_id = o.id
        WHERE o.status = 'completed' AND o.shift_id IS NOT NULL
        GROUP BY o.shift_id
    """)

    summary_rows = []
    now = datetime.now()
    for shift_str, n_ord, rev, cash, qris, other, items in order_agg:
        shift_db_id = shift_id_map.get(shift_str)
        if not shift_db_id:
            continue
        avg = Decimal(str(rev)) / int(n_ord) if n_ord else Decimal("0")
        summary_rows.append((
            shift_db_id, int(n_ord),
            Decimal(str(rev)).quantize(Decimal("0.01")),
            Decimal(str(cash)).quantize(Decimal("0.01")),
            Decimal(str(qris)).quantize(Decimal("0.01")),
            Decimal(str(other)).quantize(Decimal("0.01")),
            int(items or 0),
            avg.quantize(Decimal("0.01")), now
        ))

    n = bulk_insert(
        "lumra_ops_shift_sales_summary",
        ["shift_id","total_orders","total_revenue","cash_received","qris_received",
         "other_received","total_items","avg_order_value","created_at"],
        summary_rows,
        on_conflict="ON CONFLICT (shift_id) DO NOTHING"
    )
    ok(f"Shift summary: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 8 — DASHBOARD KPI CACHE
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_KPI_CACHE = """
CREATE TABLE IF NOT EXISTS lumra_dashboard_kpi_cache (
    id              BIGSERIAL PRIMARY KEY,
    metric_key      VARCHAR(80) UNIQUE NOT NULL,
    metric_group    VARCHAR(40) NOT NULL,
    metric_label    VARCHAR(120) NOT NULL,
    value_numeric   NUMERIC(20,4),
    value_text      TEXT,
    value_json      JSONB,
    unit            VARCHAR(20) DEFAULT '',
    period_type     VARCHAR(20) DEFAULT 'today',
    period_start    DATE,
    period_end      DATE,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    trend           VARCHAR(10) DEFAULT 'neutral',
    change_pct      NUMERIC(8,2) DEFAULT 0,
    refreshed_at    TIMESTAMPTZ DEFAULT NOW(),
    next_refresh_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_kpi_group ON lumra_dashboard_kpi_cache(metric_group);
COMMENT ON TABLE lumra_dashboard_kpi_cache IS
    'Cache KPI untuk dashboard. Di-refresh tiap jam via cron.';
"""

def fill_kpi_cache(dry_run=False):
    head("MODUL 8 — DASHBOARD KPI CACHE")

    if not dry_run:
        execute_sql(CREATE_KPI_CACHE, "CREATE lumra_dashboard_kpi_cache")

    now   = datetime.now()
    today = date.today()

    def safe_q1(sql, default=0):
        try: return q1(sql) or default
        except: return default

    # FIX: semua f-string di bawah tidak pakai LIKE/ILIKE jadi aman
    rev_today = safe_q1(f"""
        SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders
        WHERE DATE(created_at)='{today}' AND status='completed'
    """)
    rev_ytd = safe_q1(f"""
        SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders
        WHERE EXTRACT(YEAR FROM created_at)={today.year} AND status='completed'
    """)
    rev_mtd = safe_q1(f"""
        SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders
        WHERE EXTRACT(YEAR FROM created_at)={today.year}
          AND EXTRACT(MONTH FROM created_at)={today.month}
          AND status='completed'
    """)
    ord_today = safe_q1(f"""
        SELECT COUNT(*) FROM lumra_config_orders
        WHERE DATE(created_at)='{today}' AND status='completed'
    """)
    avg_order = safe_q1(f"""
        SELECT COALESCE(AVG(paid_amount),0) FROM lumra_config_orders
        WHERE EXTRACT(YEAR FROM created_at)={today.year} AND status='completed'
    """)
    total_orders  = safe_q1("SELECT COUNT(*) FROM lumra_config_orders WHERE status='completed'")
    total_revenue = safe_q1("SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders WHERE status='completed'")

    total_customers   = safe_q1("SELECT COUNT(*) FROM lumra_config_customers WHERE is_active=true")
    new_customers_mtd = safe_q1(f"""
        SELECT COUNT(*) FROM lumra_config_customers
        WHERE EXTRACT(YEAR FROM created_at)={today.year}
          AND EXTRACT(MONTH FROM created_at)={today.month}
    """)
    champions = safe_q1("SELECT COUNT(*) FROM lumra_crm_rfm_scores WHERE segment='champion'") \
                if table_exists("lumra_crm_rfm_scores") else 0
    at_risk   = safe_q1("SELECT COUNT(*) FROM lumra_crm_rfm_scores WHERE segment='at_risk'") \
                if table_exists("lumra_crm_rfm_scores") else 0

    total_stock_qty = safe_q1("SELECT COALESCE(SUM(quantity),0) FROM lumra_config_stock")
    low_stock = safe_q1("""
        SELECT COUNT(DISTINCT s.variant_id)
        FROM lumra_config_stock s
        JOIN lumra_config_productvariants pv ON pv.id=s.variant_id
        JOIN lumra_config_products p ON p.id=pv.product_id
        WHERE s.quantity < p.min_stock AND p.min_stock > 0
    """)
    expiring_30d = safe_q1(f"""
        SELECT COUNT(*) FROM lumra_config_product_batches
        WHERE expiry_date BETWEEN '{today}' AND '{today + timedelta(days=30)}'
          AND quantity_available > 0
    """)

    total_transfers      = safe_q1("SELECT COUNT(*) FROM lumra_config_transfers WHERE status='received'")
    pending_requisitions = safe_q1("SELECT COUNT(*) FROM lumra_config_requisitions WHERE status='pending'")
    active_production    = safe_q1("SELECT COUNT(*) FROM production_orders WHERE status='in_progress'")
    waste_this_month     = safe_q1(f"""
        SELECT COALESCE(SUM(quantity),0) FROM production_waste_records
        WHERE EXTRACT(YEAR FROM recorded_at)={today.year}
          AND EXTRACT(MONTH FROM recorded_at)={today.month}
    """)

    total_ap = safe_q1("SELECT COALESCE(SUM(total_amount-paid_amount),0) FROM accounting_accounts_payable WHERE status!='paid'")
    total_ar = safe_q1("SELECT COALESCE(SUM(total_amount-paid_amount),0) FROM accounting_accounts_receivable WHERE status!='paid'")

    target_this_month = safe_q1(f"""
        SELECT target_amount FROM lumra_config_sales_targets
        WHERE year={today.year} AND month={today.month}
    """) or 1
    achievement = float(rev_mtd) / float(target_this_month) * 100 if target_this_month else 0

    next_refresh = now + timedelta(hours=1)

    def kpi(key, group, label, num=None, text=None, jval=None,
            unit="", period="today", p_start=None, p_end=None,
            trend="neutral", change=0):
        return (key, group, label, num, text, jval, unit, period,
                p_start or today, p_end or today,
                None, trend, change, now, next_refresh)

    kpis = [
        kpi("revenue_today",       "sales", "Revenue Hari Ini",           float(rev_today),          unit="IDR", trend="up"),
        kpi("revenue_mtd",         "sales", "Revenue MTD",                float(rev_mtd),            unit="IDR", period="month", p_start=today.replace(day=1)),
        kpi("revenue_ytd",         "sales", "Revenue YTD",                float(rev_ytd),            unit="IDR", period="year",  p_start=today.replace(month=1,day=1)),
        kpi("revenue_total",       "sales", "Total Revenue All Time",     float(total_revenue),      unit="IDR"),
        kpi("orders_today",        "sales", "Orders Hari Ini",            float(ord_today),          unit="trx"),
        kpi("orders_total",        "sales", "Total Orders",               float(total_orders),       unit="trx"),
        kpi("avg_order_value",     "sales", "Avg Order Value (YTD)",      float(avg_order),          unit="IDR", period="year"),
        kpi("target_achievement",  "sales", "Pencapaian Target Bulan Ini",achievement,               unit="%",   period="month",
            trend="up" if achievement>=100 else "down", change=achievement-100),

        kpi("customers_total",     "crm", "Total Customer Aktif",         float(total_customers),    unit="customer"),
        kpi("customers_new_mtd",   "crm", "Customer Baru MTD",           float(new_customers_mtd),  unit="customer", period="month"),
        kpi("rfm_champions",       "crm", "Segment Champion",             float(champions),          unit="customer"),
        kpi("rfm_at_risk",         "crm", "Segment At Risk",              float(at_risk),            unit="customer", trend="down"),

        kpi("stock_qty_total",     "inventory", "Total Qty Stok",         float(total_stock_qty),    unit="unit"),
        kpi("stock_low_alert",     "inventory", "Produk Stok Menipis",    float(low_stock),          unit="sku",   trend="down" if low_stock>0 else "neutral"),
        kpi("batch_expiring_30d",  "inventory", "Batch Exp <= 30 hari",   float(expiring_30d),       unit="batch", trend="down" if expiring_30d>0 else "neutral"),

        kpi("transfers_completed", "operations","Transfer Selesai",        float(total_transfers),    unit="trf"),
        kpi("requisitions_pending","operations","Requisisi Pending",       float(pending_requisitions),unit="req"),
        kpi("production_active",   "operations","Production Order Aktif",  float(active_production),  unit="po"),
        kpi("waste_qty_mtd",       "operations","Waste Produksi MTD",      float(waste_this_month),   unit="qty", period="month"),

        kpi("ap_outstanding",      "finance","Hutang Belum Bayar",         float(total_ap),           unit="IDR", trend="down"),
        kpi("ar_outstanding",      "finance","Piutang Belum Terima",       float(total_ar),           unit="IDR"),
    ]

    log(f"KPI metrics: {len(kpis)}")
    if dry_run:
        log("[DRY RUN] Akan insert KPI cache")
        for k in kpis[:5]:
            print(f"      {k[0]:<30} {k[1]:<12} {str(k[3])[:15]}")
        return

    n = bulk_insert(
        "lumra_dashboard_kpi_cache",
        ["metric_key","metric_group","metric_label","value_numeric","value_text",
         "value_json","unit","period_type","period_start","period_end",
         "location_id","trend","change_pct","refreshed_at","next_refresh_at"],
        kpis,
        on_conflict="ON CONFLICT (metric_key) DO UPDATE SET "
                    "value_numeric=EXCLUDED.value_numeric, trend=EXCLUDED.trend, "
                    "change_pct=EXCLUDED.change_pct, refreshed_at=EXCLUDED.refreshed_at, "
                    "next_refresh_at=EXCLUDED.next_refresh_at"
    )
    ok(f"KPI cache: {n} metrics")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 9 — AUDIT TRAILS
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_AUDIT = """
CREATE TABLE IF NOT EXISTS lumra_system_audit_trails (
    id              BIGSERIAL PRIMARY KEY,
    table_name      VARCHAR(80) NOT NULL,
    record_id       BIGINT NOT NULL,
    action          VARCHAR(10) NOT NULL,
    actor_id        BIGINT REFERENCES auth_user(id),
    actor_username  VARCHAR(150),
    old_values      JSONB,
    new_values      JSONB,
    changed_fields  TEXT[],
    ip_address      INET,
    user_agent      TEXT DEFAULT '',
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_table ON lumra_system_audit_trails(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON lumra_system_audit_trails(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_time  ON lumra_system_audit_trails(created_at DESC);
COMMENT ON TABLE lumra_system_audit_trails IS
    'Log audit perubahan data krusial: order, harga, stok adjustment, resep, user.';
"""

def fill_audit(dry_run=False, limit=50000):
    head("MODUL 9 — SYSTEM AUDIT TRAILS")

    if not dry_run:
        execute_sql(CREATE_AUDIT, "CREATE lumra_system_audit_trails")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]
    fake_ips = ["10.0.1."+str(i) for i in range(1, 56)]
    now      = datetime.now()

    audit_rows = []

    orders = q(f"""
        SELECT id, customer_id, paid_amount, status, created_at
        FROM lumra_config_orders
        ORDER BY RANDOM()
        LIMIT {limit // 3}
    """)
    for oid, cid, paid, status, created_at in orders:
        actor = RNG.choice(user_ids) if user_ids else admin_id
        audit_rows.append((
            "lumra_config_orders", oid, "UPDATE",
            actor, None,
            json.dumps({"status": "pending", "paid_amount": str(paid)}),
            json.dumps({"status": status,    "paid_amount": str(paid)}),
            ["status"],
            RNG.choice(fake_ips), "Mozilla/5.0 (Lumra POS)",
            "Order status update", created_at
        ))

    stock_mvs = q(f"""
        SELECT sm.id, sm.location_id, sm.product_id, sm.quantity, sm.movement_type, sm.created_at
        FROM lumra_config_stockmovement sm
        ORDER BY RANDOM()
        LIMIT {limit // 3}
    """)
    for sm_id, loc_id, var_id, qty, mvtype, created_at in stock_mvs:
        actor   = RNG.choice(user_ids) if user_ids else admin_id
        old_qty = int(qty or 0) + RNG.randint(-50, 50)
        audit_rows.append((
            "lumra_config_stock", var_id, "UPDATE",
            actor, None,
            json.dumps({"quantity": old_qty,       "location_id": loc_id}),
            json.dumps({"quantity": int(qty or 0), "location_id": loc_id}),
            ["quantity"],
            RNG.choice(fake_ips), "Lumra Inventory System",
            f"Stock {mvtype}", created_at
        ))

    pos = q(f"""
        SELECT id, code, status, created_at FROM production_orders
        ORDER BY RANDOM() LIMIT {limit // 6}
    """)
    for po_id, code, status, created_at in pos:
        actor = RNG.choice(user_ids) if user_ids else admin_id
        audit_rows.append((
            "production_orders", po_id, "UPDATE",
            actor, None,
            json.dumps({"status": "in_progress", "code": code}),
            json.dumps({"status": status,         "code": code}),
            ["status"],
            RNG.choice(fake_ips), "Lumra Production",
            "Production status update", created_at
        ))

    log(f"Audit trail rows: {len(audit_rows):,}")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(audit_rows):,} audit rows")
        return

    n = bulk_insert(
        "lumra_system_audit_trails",
        ["table_name","record_id","action","actor_id","actor_username",
         "old_values","new_values","changed_fields","ip_address","user_agent",
         "notes","created_at"],
        audit_rows, batch=2000
    )
    ok(f"Audit trails: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "procurement":  fill_procurement,
    "rfm":          fill_rfm,
    "promotions":   fill_promotions,
    "sales_agg":    fill_sales_agg,
    "product_perf": fill_product_perf,
    "inv_snapshot": fill_inv_snapshot,
    "shifts":       fill_shifts,
    "kpi_cache":    fill_kpi_cache,
    "audit":        fill_audit,
}

ORDER = ["procurement","rfm","promotions","sales_agg","product_perf","inv_snapshot","shifts","kpi_cache","audit"]

def main():
    t_total = time.time()
    print("\n" + "═"*70)
    print("  KAFE NUSANTARA — Database Expansion Script")
    print("  9 modul: Procurement, RFM, Promotions, Sales Agg,")
    print("           Product Perf, Inv Snapshot, Shifts, KPI Cache, Audit")
    print("═"*70)
    print(f"  Mode    : {'DRY RUN' if DRY_RUN else 'EXECUTE'}")
    print(f"  Section : {SECTION}")

    load_context()

    to_run  = ORDER if SECTION == "all" else [SECTION]
    results = {}

    for sec in to_run:
        fn = SECTION_MAP.get(sec)
        if not fn:
            warn(f"Section '{sec}' tidak dikenal. Pilihan: {list(SECTION_MAP.keys())}")
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
        print(f"  {icon} {sec:<20} {res}")
    print("═"*70)

    if DRY_RUN:
        print("\n  Jalankan dengan --execute untuk menyimpan ke DB\n")

    new_tables = [
        "lumra_procurement_purchase_orders",
        "lumra_procurement_po_items",
        "lumra_procurement_goods_receipts",
        "lumra_procurement_grn_items",
        "lumra_crm_rfm_scores",
        "lumra_sales_promotions",
        "lumra_sales_promotion_usage",
        "lumra_report_sales_daily",
        "lumra_report_sales_monthly",
        "lumra_report_product_performance",
        "lumra_report_inventory_snapshot",
        "lumra_ops_shifts",
        "lumra_ops_shift_sales_summary",
        "lumra_dashboard_kpi_cache",
        "lumra_system_audit_trails",
    ]
    print("  Tabel yang dibuat/diisi:")
    for t in new_tables:
        cnt     = row_count(t) if not DRY_RUN else "—"
        cnt_str = f"{cnt:,}" if isinstance(cnt, int) else cnt
        print(f"    {t:<45} {cnt_str:>12}")
    print()


try:
    from django.core.management.base import BaseCommand
    class Command(BaseCommand):
        help = "Kafe Nusantara — Database expansion (9 modules)"
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