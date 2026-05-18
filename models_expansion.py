"""
models_expansion.py
===================
Django Models untuk tabel-tabel hasil seed_expansion.py yang belum
terdaftar sebagai Model di Django.

Cara integrasi:
  1. Copy file ini ke lumra_config/models_expansion.py
     (atau split ke app masing-masing sesuai struktur project)

  2. Di lumra_config/models/__init__.py (atau models.py utama), tambahkan:
       from .models_expansion import *

  3. Karena tabel sudah ADA di DB (dibuat via raw SQL), gunakan:
       managed = False
     supaya Django tidak mencoba CREATE/DROP tabel ini via migrations.

  4. Jalankan:
       python manage.py makemigrations --empty lumra_config
     Lalu edit migration yang dibuat untuk menambahkan
       migrations.CreateModel(..., options={"managed": False}, ...)
     atau cukup biarkan karena managed=False tidak menghasilkan migration DDL.

Tabel yang di-cover (20 tabel):
  Procurement  : lumra_procurement_purchase_orders, po_items,
                 goods_receipts, grn_items
  CRM          : lumra_crm_rfm_scores
  Sales        : lumra_sales_promotions, promotion_usage
  Report       : lumra_report_sales_daily, sales_monthly,
                 product_performance, inventory_snapshot
  Ops          : lumra_ops_shifts, shift_sales_summary
  Dashboard    : lumra_dashboard_kpi_cache
  System       : lumra_system_audit_trails
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


# ═══════════════════════════════════════════════════════════════════════════════
# PROCUREMENT
# ═══════════════════════════════════════════════════════════════════════════════

class PurchaseOrder(models.Model):
    """
    Purchase Order ke vendor. Dokumen resmi pemesanan barang.
    Status flow: draft → sent → partial → completed | cancelled
    """
    STATUS_CHOICES = [
        ("draft",     "Draft"),
        ("sent",      "Sent to Vendor"),
        ("partial",   "Partially Received"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    po_number    = models.CharField(max_length=50, unique=True)
    vendor       = models.ForeignKey(
        "lumra_config.Vendors",
        on_delete=models.PROTECT,
        db_column="vendor_id",
        related_name="purchase_orders",
    )
    location     = models.ForeignKey(
        "lumra_config.Locations",
        on_delete=models.PROTECT,
        db_column="location_id",
        related_name="purchase_orders",
    )
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    order_date   = models.DateField()
    expected_date= models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes        = models.TextField(default="", blank=True)
    created_by   = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="created_by_id", related_name="po_created",
    )
    approved_by  = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="approved_by_id", related_name="po_approved",
    )
    approved_at  = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        managed  = False
        db_table = "lumra_procurement_purchase_orders"
        ordering = ["-order_date", "-id"]
        indexes  = [
            models.Index(fields=["status"]),
            models.Index(fields=["vendor", "status"]),
            models.Index(fields=["order_date"]),
        ]

    def __str__(self):
        return f"{self.po_number} [{self.status}]"

    @property
    def is_editable(self):
        return self.status in ("draft", "sent")


class PurchaseOrderItem(models.Model):
    """Detail item per Purchase Order."""
    po       = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE,
        db_column="po_id", related_name="items",
    )
    variant  = models.ForeignKey(
        "lumra_config.ProductVariants",
        on_delete=models.PROTECT,
        db_column="variant_id",
        related_name="po_items",
    )
    quantity     = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price   = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal     = models.DecimalField(max_digits=15, decimal_places=2)
    received_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes        = models.TextField(default="", blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "lumra_procurement_po_items"

    def __str__(self):
        return f"POItem {self.po_id} / variant {self.variant_id}"

    @property
    def remaining_qty(self):
        return self.quantity - self.received_qty


class GoodsReceipt(models.Model):
    """
    Good Receipt Note (GRN) — bukti terima barang dari vendor.
    Bisa linked ke PO atau standalone (pembelian langsung).
    """
    STATUS_CHOICES = [
        ("draft",     "Draft"),
        ("completed", "Completed"),
        ("rejected",  "Rejected"),
    ]

    grn_number   = models.CharField(max_length=50, unique=True)
    po           = models.ForeignKey(
        PurchaseOrder, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="po_id", related_name="goods_receipts",
    )
    vendor       = models.ForeignKey(
        "lumra_config.Vendors",
        on_delete=models.PROTECT,
        db_column="vendor_id",
        related_name="goods_receipts",
    )
    location     = models.ForeignKey(
        "lumra_config.Locations",
        on_delete=models.PROTECT,
        db_column="location_id",
        related_name="goods_receipts",
    )
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    receipt_date  = models.DateField()
    total_received= models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes         = models.TextField(default="", blank=True)
    received_by   = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="received_by_id", related_name="grn_received",
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        managed  = False
        db_table = "lumra_procurement_goods_receipts"
        ordering = ["-receipt_date", "-id"]

    def __str__(self):
        return f"{self.grn_number} [{self.status}]"


class GoodsReceiptItem(models.Model):
    """Detail barang yang diterima per GRN."""
    grn      = models.ForeignKey(
        GoodsReceipt, on_delete=models.CASCADE,
        db_column="grn_id", related_name="items",
    )
    variant  = models.ForeignKey(
        "lumra_config.ProductVariants",
        on_delete=models.PROTECT,
        db_column="variant_id",
        related_name="grn_items",
    )
    po_item  = models.ForeignKey(
        PurchaseOrderItem, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="po_item_id", related_name="grn_items",
    )
    quantity_ordered  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_rejected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price        = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal          = models.DecimalField(max_digits=15, decimal_places=2)
    batch_number      = models.CharField(max_length=100, default="", blank=True)
    expiry_date       = models.DateField(null=True, blank=True)
    notes             = models.TextField(default="", blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "lumra_procurement_grn_items"

    def __str__(self):
        return f"GRNItem {self.grn_id} / variant {self.variant_id}"


# ═══════════════════════════════════════════════════════════════════════════════
# CRM — RFM SCORES
# ═══════════════════════════════════════════════════════════════════════════════

class CustomerRFMScore(models.Model):
    """
    RFM (Recency / Frequency / Monetary) scoring per customer.
    Di-recalculate secara berkala via management command atau cron.

    Segment labels:
      champion, loyal, potential, at_risk, cannot_lose,
      lost_big, lost, need_attention, hibernating, promising, new
    """
    SEGMENT_CHOICES = [
        ("champion",      "Champion"),
        ("loyal",         "Loyal Customer"),
        ("potential",     "Potential Loyalist"),
        ("promising",     "Promising"),
        ("need_attention","Need Attention"),
        ("at_risk",       "At Risk"),
        ("cannot_lose",   "Cannot Lose Them"),
        ("hibernating",   "Hibernating"),
        ("lost_big",      "Lost (High Value)"),
        ("lost",          "Lost"),
        ("new",           "New Customer"),
    ]

    customer      = models.OneToOneField(
        "lumra_config.Customers",
        on_delete=models.CASCADE,
        db_column="customer_id",
        related_name="rfm_score",
    )
    recency_days  = models.IntegerField(default=0)
    frequency     = models.IntegerField(default=0)
    monetary_total= models.DecimalField(max_digits=15, decimal_places=2, default=0)
    avg_order_value=models.DecimalField(max_digits=12, decimal_places=2, default=0)
    r_score       = models.SmallIntegerField(default=1)  # 1-5
    f_score       = models.SmallIntegerField(default=1)  # 1-5
    m_score       = models.SmallIntegerField(default=1)  # 1-5
    rfm_score     = models.SmallIntegerField(default=3)  # sum r+f+m (3-15)
    segment       = models.CharField(max_length=30, choices=SEGMENT_CHOICES, default="new")
    first_order_date= models.DateField(null=True, blank=True)
    last_order_date = models.DateField(null=True, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        managed  = False
        db_table = "lumra_crm_rfm_scores"
        indexes  = [
            models.Index(fields=["segment"]),
            models.Index(fields=["-rfm_score"]),
        ]

    def __str__(self):
        return f"RFM {self.customer_id} → {self.segment} ({self.rfm_score})"

    @property
    def rfm_label(self):
        return f"R{self.r_score}F{self.f_score}M{self.m_score}"


# ═══════════════════════════════════════════════════════════════════════════════
# SALES — PROMOTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class Promotion(models.Model):
    """
    Promo Kafe Nusantara: Morning Ration, Transit Special, Curator Share, dll.

    promo_type  : bundle | loyalty | voucher | birthday | seasonal |
                  onboarding | multi_buy
    discount_type: percentage | fixed
    applicable_session: all | first_light | midday_transit | twilight_bivouac
    """
    PROMO_TYPE_CHOICES = [
        ("bundle",     "Bundle"),
        ("loyalty",    "Loyalty"),
        ("voucher",    "Voucher"),
        ("birthday",   "Birthday"),
        ("seasonal",   "Seasonal"),
        ("onboarding", "Onboarding"),
        ("multi_buy",  "Multi Buy"),
    ]
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage (%)"),
        ("fixed",      "Fixed (Rp)"),
    ]
    SESSION_CHOICES = [
        ("all",              "All Sessions"),
        ("first_light",      "First Light (07-12)"),
        ("midday_transit",   "Midday Transit (12-18)"),
        ("twilight_bivouac", "Twilight Bivouac (18-23)"),
    ]

    code           = models.CharField(max_length=30, unique=True)
    name           = models.CharField(max_length=150)
    description    = models.TextField(default="", blank=True)
    promo_type     = models.CharField(max_length=30, choices=PROMO_TYPE_CHOICES)
    discount_type  = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default="percentage")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_purchase   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    applicable_session   = models.CharField(max_length=20, choices=SESSION_CHOICES, default="all")
    applicable_hour_start= models.SmallIntegerField(default=0)
    applicable_hour_end  = models.SmallIntegerField(default=23)
    valid_from     = models.DateField()
    valid_until    = models.DateField(null=True, blank=True)
    is_active      = models.BooleanField(default=True)
    usage_limit    = models.IntegerField(null=True, blank=True)
    usage_count    = models.IntegerField(default=0)
    created_by     = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="created_by_id", related_name="promotions_created",
    )
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        managed  = False
        db_table = "lumra_sales_promotions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.code}] {self.name}"

    @property
    def is_expired(self):
        from datetime import date
        return self.valid_until and self.valid_until < date.today()

    @property
    def is_quota_full(self):
        return self.usage_limit is not None and self.usage_count >= self.usage_limit


class PromotionUsage(models.Model):
    """Log pemakaian promo per order."""
    promotion      = models.ForeignKey(
        Promotion, on_delete=models.PROTECT,
        db_column="promotion_id", related_name="usages",
    )
    order          = models.ForeignKey(
        "lumra_config.Orders",
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="promo_usages",
    )
    customer       = models.ForeignKey(
        "lumra_config.Customers",
        null=True, blank=True, on_delete=models.SET_NULL,
        db_column="customer_id", related_name="promo_usages",
    )
    discount_amount= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    used_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "lumra_sales_promotion_usage"
        indexes  = [
            models.Index(fields=["order"]),
            models.Index(fields=["promotion"]),
        ]

    def __str__(self):
        return f"Promo {self.promotion_id} / Order {self.order_id}"


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT — SALES AGGREGATES
# ═══════════════════════════════════════════════════════════════════════════════

class SalesDaily(models.Model):
    """
    Agregasi penjualan harian per lokasi.
    Di-refresh tiap malam via cron / management command.
    location=NULL berarti agregat semua outpost.
    """
    report_date    = models.DateField()
    location       = models.ForeignKey(
        "lumra_config.Locations",
        null=True, blank=True, on_delete=models.SET_NULL,
        db_column="location_id", related_name="sales_daily",
    )
    total_orders   = models.IntegerField(default=0)
    total_revenue  = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_items_sold=models.IntegerField(default=0)
    avg_order_value= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_returns  = models.IntegerField(default=0)
    return_value   = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_revenue    = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_sales     = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    qris_sales     = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    transfer_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    card_sales     = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    new_customers  = models.IntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed     = False
        db_table    = "lumra_report_sales_daily"
        unique_together = [("report_date", "location")]
        ordering    = ["-report_date"]
        indexes     = [
            models.Index(fields=["-report_date"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        loc = self.location_id or "ALL"
        return f"Sales {self.report_date} / loc={loc}"


class SalesMonthly(models.Model):
    """
    Agregasi penjualan bulanan per lokasi.
    Include vs target, MoM growth, YoY growth.
    """
    year           = models.SmallIntegerField()
    month          = models.SmallIntegerField()
    location       = models.ForeignKey(
        "lumra_config.Locations",
        null=True, blank=True, on_delete=models.SET_NULL,
        db_column="location_id", related_name="sales_monthly",
    )
    total_orders   = models.IntegerField(default=0)
    total_revenue  = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_items_sold=models.IntegerField(default=0)
    avg_order_value= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_returns  = models.IntegerField(default=0)
    return_value   = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_revenue    = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    target_amount  = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    achievement_pct= models.DecimalField(max_digits=6, decimal_places=2, default=0)
    mom_growth_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    yoy_growth_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    new_customers  = models.IntegerField(default=0)
    active_customers=models.IntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        managed     = False
        db_table    = "lumra_report_sales_monthly"
        unique_together = [("year", "month", "location")]
        ordering    = ["-year", "-month"]
        indexes     = [
            models.Index(fields=["-year", "-month"]),
        ]

    def __str__(self):
        loc = self.location_id or "ALL"
        return f"Sales {self.year}-{self.month:02d} / loc={loc} | achv={self.achievement_pct}%"


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT — PRODUCT PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

class ProductPerformance(models.Model):
    """
    Performa per produk: revenue, margin, turnover, velocity.
    velocity_label: fast_moving | normal | slow_moving
    """
    VELOCITY_CHOICES = [
        ("fast_moving", "Fast Moving"),
        ("normal",      "Normal"),
        ("slow_moving", "Slow Moving"),
    ]

    variant          = models.OneToOneField(
        "lumra_config.ProductVariants",
        on_delete=models.CASCADE,
        db_column="variant_id",
        related_name="performance",
    )
    total_sold_qty   = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_sold_revenue=models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_sold_cogs  = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_margin     = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    margin_pct       = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    avg_selling_price= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders     = models.IntegerField(default=0)
    total_returns    = models.IntegerField(default=0)
    return_rate_pct  = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    current_stock    = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    stock_turnover_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    velocity_label   = models.CharField(max_length=20, choices=VELOCITY_CHOICES, default="normal")
    last_sold_date   = models.DateField(null=True, blank=True)
    calculated_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "lumra_report_product_performance"
        indexes  = [
            models.Index(fields=["velocity_label"]),
            models.Index(fields=["-margin_pct"]),
        ]

    def __str__(self):
        return f"Perf variant {self.variant_id} | {self.velocity_label} | margin {self.margin_pct}%"


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT — INVENTORY SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════════════

class InventorySnapshot(models.Model):
    """
    Snapshot stok akhir bulan per (lokasi × variant).
    Digunakan untuk audit akuntansi tanpa re-query seluruh mutasi histori.
    """
    snapshot_year  = models.SmallIntegerField()
    snapshot_month = models.SmallIntegerField()
    location       = models.ForeignKey(
        "lumra_config.Locations",
        null=True, blank=True, on_delete=models.SET_NULL,
        db_column="location_id", related_name="inv_snapshots",
    )
    variant        = models.ForeignKey(
        "lumra_config.ProductVariants",
        null=True, blank=True, on_delete=models.SET_NULL,
        db_column="variant_id", related_name="inv_snapshots",
    )
    qty_opening    = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    qty_in         = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    qty_out        = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    qty_closing    = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    qty_on_hand    = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    value_on_hand  = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed     = False
        db_table    = "lumra_report_inventory_snapshot"
        unique_together = [("snapshot_year", "snapshot_month", "location", "variant")]
        indexes     = [
            models.Index(fields=["-snapshot_year", "-snapshot_month"]),
        ]

    def __str__(self):
        return f"InvSnap {self.snapshot_year}-{self.snapshot_month:02d} / loc={self.location_id} / var={self.variant_id}"


# ═══════════════════════════════════════════════════════════════════════════════
# OPS — SHIFTS
# ═══════════════════════════════════════════════════════════════════════════════

class Shift(models.Model):
    """
    Data shift kerja per outpost.
    3 shift: First Light (07-12), Midday Transit (12-18), Twilight Bivouac (18-23).
    """
    SHIFT_TYPE_CHOICES = [
        ("first_light",      "First Light (07-12)"),
        ("midday_transit",   "Midday Transit (12-18)"),
        ("twilight_bivouac", "Twilight Bivouac (18-23)"),
    ]
    STATUS_CHOICES = [
        ("open",   "Open"),
        ("closed", "Closed"),
    ]

    shift_code   = models.CharField(max_length=50, unique=True)
    location     = models.ForeignKey(
        "lumra_config.Locations",
        on_delete=models.PROTECT,
        db_column="location_id",
        related_name="shifts",
    )
    shift_date   = models.DateField()
    shift_type   = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES)
    start_time   = models.DateTimeField()
    end_time     = models.DateTimeField(null=True, blank=True)
    opened_by    = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="opened_by_id", related_name="shifts_opened",
    )
    closed_by    = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="closed_by_id", related_name="shifts_closed",
    )
    opening_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_cash= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_variance= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default="closed")
    notes        = models.TextField(default="", blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "lumra_ops_shifts"
        ordering = ["-shift_date", "shift_type"]
        indexes  = [
            models.Index(fields=["-shift_date"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.shift_code} [{self.shift_type}] {self.shift_date}"

    @property
    def variance_pct(self):
        if self.expected_cash and self.expected_cash != 0:
            return round(float(self.cash_variance) / float(self.expected_cash) * 100, 2)
        return 0.0


class ShiftSalesSummary(models.Model):
    """
    Ringkasan penjualan per shift.
    Diisi otomatis saat shift ditutup.
    """
    shift         = models.OneToOneField(
        Shift, on_delete=models.CASCADE,
        db_column="shift_id", related_name="sales_summary",
    )
    total_orders  = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qris_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_received= models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items   = models.IntegerField(default=0)
    avg_order_value=models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "lumra_ops_shift_sales_summary"

    def __str__(self):
        return f"ShiftSummary shift={self.shift_id} | rev={self.total_revenue}"


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD — KPI CACHE
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardKPICache(models.Model):
    """
    Cache KPI untuk dashboard. Di-refresh tiap jam via cron.
    Menghindari query berat ke tabel jutaan rows setiap load dashboard.

    metric_group : sales | crm | inventory | operations | finance
    period_type  : today | week | month | year | custom
    trend        : up | down | neutral
    """
    TREND_CHOICES = [
        ("up",      "Up"),
        ("down",    "Down"),
        ("neutral", "Neutral"),
    ]
    PERIOD_CHOICES = [
        ("today",  "Today"),
        ("week",   "This Week"),
        ("month",  "This Month"),
        ("year",   "This Year"),
        ("custom", "Custom Range"),
    ]

    metric_key    = models.CharField(max_length=80, unique=True)
    metric_group  = models.CharField(max_length=40)
    metric_label  = models.CharField(max_length=120)
    value_numeric = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    value_text    = models.TextField(null=True, blank=True)
    value_json    = models.JSONField(null=True, blank=True)
    unit          = models.CharField(max_length=20, default="", blank=True)
    period_type   = models.CharField(max_length=20, choices=PERIOD_CHOICES, default="today")
    period_start  = models.DateField(null=True, blank=True)
    period_end    = models.DateField(null=True, blank=True)
    location      = models.ForeignKey(
        "lumra_config.Locations",
        null=True, blank=True, on_delete=models.SET_NULL,
        db_column="location_id", related_name="kpi_cache",
    )
    trend         = models.CharField(max_length=10, choices=TREND_CHOICES, default="neutral")
    change_pct    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    refreshed_at  = models.DateTimeField(auto_now=True)
    next_refresh_at=models.DateTimeField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "lumra_dashboard_kpi_cache"
        indexes  = [
            models.Index(fields=["metric_group"]),
        ]

    def __str__(self):
        return f"KPI [{self.metric_group}] {self.metric_key} = {self.value_numeric} {self.unit}"

    @classmethod
    def get(cls, key, default=None):
        """Shortcut: ambil satu KPI by metric_key."""
        try:
            return cls.objects.get(metric_key=key)
        except cls.DoesNotExist:
            return default

    @classmethod
    def get_group(cls, group):
        """Ambil semua KPI dalam satu group."""
        return cls.objects.filter(metric_group=group)


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM — AUDIT TRAILS
# ═══════════════════════════════════════════════════════════════════════════════

class AuditTrail(models.Model):
    """
    Log audit perubahan data krusial: order, harga, stok adjustment, resep, user.

    Tidak menggunakan FK ke table_name/record_id karena bersifat generic
    (bisa menunjuk ke tabel mana saja). Gunakan GenericForeignKey jika perlu.
    """
    ACTION_CHOICES = [
        ("INSERT", "Insert"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
    ]

    table_name    = models.CharField(max_length=80)
    record_id     = models.BigIntegerField()
    action        = models.CharField(max_length=10, choices=ACTION_CHOICES)
    actor         = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        db_column="actor_id", related_name="audit_trails",
    )
    actor_username= models.CharField(max_length=150, null=True, blank=True)
    old_values    = models.JSONField(null=True, blank=True)
    new_values    = models.JSONField(null=True, blank=True)
    changed_fields= ArrayField(
        models.CharField(max_length=100),
        null=True, blank=True,
    )
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    user_agent    = models.TextField(default="", blank=True)
    notes         = models.TextField(default="", blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = "lumra_system_audit_trails"
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["table_name", "record_id"]),
            models.Index(fields=["actor"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Audit [{self.action}] {self.table_name}#{self.record_id} by {self.actor_username or self.actor_id}"

    @classmethod
    def log(cls, table_name, record_id, action, actor=None,
            old_values=None, new_values=None, changed_fields=None,
            ip_address=None, user_agent="", notes=""):
        """
        Helper untuk menulis audit log dari kode lain.
        Contoh:
            AuditTrail.log(
                "lumra_config_orders", order.id, "UPDATE",
                actor=request.user,
                old_values={"status": "pending"},
                new_values={"status": "completed"},
                changed_fields=["status"],
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        """
        return cls.objects.create(
            table_name=table_name,
            record_id=record_id,
            action=action,
            actor=actor,
            actor_username=actor.username if actor else None,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields or [],
            ip_address=ip_address,
            user_agent=user_agent,
            notes=notes,
        )