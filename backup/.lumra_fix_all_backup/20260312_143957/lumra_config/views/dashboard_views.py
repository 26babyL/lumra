# lumra_config/views/dashboard_views.py
# Auto-generated oleh lumra_sync.py dari core/views/dashboard_views.py
# JANGAN EDIT MANUAL — edit core/views/dashboard_views.py lalu jalankan lumra_sync.py lagi

#
# CHANGELOG / BUG FIXES
# ─────────────────────────────────────────────────────────────────────
# FIX-1  _build_kpis() was missing the 'pending_orders' key.
#        Template card "Pending Orders" rendered "—" because
#        {{ kpis.pending_orders|default:"—" }} had nothing to show.
#
# FIX-2  Quick Stats values of 0 (int/falsy) triggered Django's
#        |default filter and printed "—" instead of the real value.
#        All quick_stats values are now explicitly cast to str so that
#        0 → "0" (truthy) before hitting the template.
#
# FIX-3  dashboard.html had three closing </div> tags but only two
#        matching opening tags (<div x-data> + <div class="max-w-7xl">).
#        The extra </div> broke Alpine's scope and cut off Quick Stats
#        from being rendered inside the reactive component.
#        → Removed the extra </div> (see dashboard.html fix).
#
# FIX-4  _update_kpis() in JS used el.querySelector('[data-kpi-value]')
#        which silently fell back to overwriting the entire card innerHTML
#        with a plain string when the attribute was absent.
#        → The JS now targets the value element by the more reliable
#          selector '[data-kpi-value]' but also safely falls back; the
#          real guard is that _build_kpis now emits all expected keys.
#
# FIX-5  api_dashboard_data() re-uses _build_kpis() so it inherits
#        FIX-1 automatically — no separate change needed there.
# ─────────────────────────────────────────────────────────────────────

import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, DecimalField, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models.functions import Coalesce

from lumra_config.models import (
    Customer,
    Location,
    Order,
    OrderItem,
    Product,
    ProductVariant,
    Stock,
)
from .helpers import safe_percent_format, smart_currency_format


# ──────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────

INBOUND  = ("in", "transfer_received", "adjustment")
OUTBOUND = ("out", "transfer_sent")
LOW_STOCK_THRESHOLD = 10


# ──────────────────────────────────────────────────────────────────────
# DATE HELPERS
# ──────────────────────────────────────────────────────────────────────

def _month_start(ref: date, offset_months: int = 0) -> date:
    """First day of the month, offset_months relative to ref."""
    month = ref.month + offset_months
    year  = ref.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return date(year, month, 1)


def _month_range(ref: date, offset_months: int = 0):
    """(start_inclusive, end_exclusive) for a calendar month."""
    start = _month_start(ref, offset_months)
    end   = _month_start(ref, offset_months + 1)
    return start, end


# ──────────────────────────────────────────────────────────────────────
# CENTRALISED DATA FETCH
# ──────────────────────────────────────────────────────────────────────

def _fetch_dashboard_data(today: date) -> dict:
    """
    Fetch every raw number needed by the dashboard.
    All keys use snake_case — template and JSON payload both use these.
    """
    thirty_days_ago           = today - timedelta(days=30)
    ninety_days_ago           = today - timedelta(days=90)
    this_month_start, next_ms = _month_range(today)
    last_month_start, _       = _month_range(today, -1)
    yesterday                 = today - timedelta(days=1)

    # Q1 — Order counts by status
    order_stats = Order.objects.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
        cancelled=Count("id", filter=Q(status="cancelled")),
        pending=Count("id", filter=Q(status="pending")),
        today_count=Count("id", filter=Q(created_at__date=today)),
        yesterday_count=Count("id", filter=Q(created_at__date=yesterday)),
    )

    # Q2 — Revenue / COGS (completed orders only)
    rev = OrderItem.objects.filter(order__status="completed").aggregate(
        revenue_30d=Sum(
            F("quantity") * F("price"),
            filter=Q(order__created_at__date__gte=thirty_days_ago),
            output_field=DecimalField(),
        ),
        revenue_90d=Sum(
            F("quantity") * F("price"),
            filter=Q(order__created_at__date__gte=ninety_days_ago),
            output_field=DecimalField(),
        ),
        cogs_90d=Sum(
            F("quantity") * F("variant__price_buy"),
            filter=Q(order__created_at__date__gte=ninety_days_ago),
            output_field=DecimalField(),
        ),
        revenue_this_month=Sum(
            F("quantity") * F("price"),
            filter=Q(
                order__created_at__date__gte=this_month_start,
                order__created_at__date__lt=next_ms,
            ),
            output_field=DecimalField(),
        ),
        revenue_last_month=Sum(
            F("quantity") * F("price"),
            filter=Q(
                order__created_at__date__gte=last_month_start,
                order__created_at__date__lt=this_month_start,
            ),
            output_field=DecimalField(),
        ),
        cogs_30d=Sum(
            F("quantity") * F("variant__price_buy"),
            filter=Q(order__created_at__date__gte=thirty_days_ago),
            output_field=DecimalField(),
        ),
        completed_order_count=Count("order_id", distinct=True),
    )

    # Q3 — Today & yesterday sales (all statuses, for "Today's Sales" card)
    def _day_revenue(d: date) -> float:
        return float(
            Order.objects.filter(created_at__date=d).aggregate(
                v=Sum(
                    F("items__quantity") * F("items__price"),
                    output_field=DecimalField(),
                )
            )["v"] or 0
        )

    today_revenue     = _day_revenue(today)
    yesterday_revenue = _day_revenue(yesterday)

    # Q4 — Net inventory value (ledger-aware)
    inv = Stock.objects.aggregate(
        inbound_value=Sum(
            F("quantity") * F("variant__price_buy"),
            filter=Q(transaction_type__in=INBOUND),
            output_field=DecimalField(),
        ),
        outbound_value=Sum(
            F("quantity") * F("variant__price_buy"),
            filter=Q(transaction_type__in=OUTBOUND),
            output_field=DecimalField(),
        ),
    )
    inventory_value = float(inv["inbound_value"] or 0) - float(inv["outbound_value"] or 0)

    # Q5 — Customer stats
    cust = Customer.objects.aggregate(
        total=Count("id"),
        repeat=Count("id", filter=Q(total_orders__gte=2)),
    )

    # Q6 — Best seller
    best_seller = (
        OrderItem.objects
        .values("variant__product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")
        .first()
    )

    # Q7 — Low-stock variants (net ledger stock < threshold)
    low_stock_count = (
        ProductVariant.objects
        .annotate(
            net_in=Coalesce(
                Sum(
                    "stock_entries__quantity",
                    filter=Q(stock_entries__transaction_type__in=INBOUND),
                ),
                0,
            ),
            net_out=Coalesce(
                Sum(
                    "stock_entries__quantity",
                    filter=Q(stock_entries__transaction_type__in=OUTBOUND),
                ),
                0,
            ),
            net_stock=F("net_in") - F("net_out"),
        )
        .filter(net_stock__lt=LOW_STOCK_THRESHOLD)
        .count()
    )

    # Q8 — Quick stats
    active_products = Product.objects.count()
    total_locations = Location.objects.count()

    # ── Derived scalars ──────────────────────────────────────────────
    total_orders    = order_stats["total"] or 0
    completed_ords  = order_stats["completed"] or 0
    cancelled_ords  = order_stats["cancelled"] or 0
    pending_orders  = order_stats["pending"] or 0
    today_count     = order_stats["today_count"] or 0
    yesterday_count = order_stats["yesterday_count"] or 0

    revenue_30d           = float(rev["revenue_30d"] or 0)
    revenue_90d           = float(rev["revenue_90d"] or 0)
    cogs_90d              = float(rev["cogs_90d"] or 0)
    revenue_this_month    = float(rev["revenue_this_month"] or 0)
    revenue_last_month    = float(rev["revenue_last_month"] or 0)
    cogs_30d              = float(rev["cogs_30d"] or 0)
    completed_order_count = rev["completed_order_count"] or 0

    total_customers  = cust["total"] or 0
    repeat_customers = cust["repeat"] or 0

    profit_margin = (
        max(0.0, min(100.0, ((revenue_90d - cogs_90d) / revenue_90d) * 100))
        if revenue_90d > 0 else 0.0
    )
    monthly_growth = (
        ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
        if revenue_last_month > 0
        else (100.0 if revenue_this_month > 0 else 0.0)
    )
    sales_growth = (
        ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
        if yesterday_revenue > 0
        else (100.0 if today_revenue > 0 else 0.0)
    )
    transaction_growth = (
        ((today_count - yesterday_count) / yesterday_count) * 100
        if yesterday_count > 0
        else (100.0 if today_count > 0 else 0.0)
    )
    avg_order_value    = (revenue_30d / completed_order_count) if completed_order_count > 0 else 0.0
    conversion_rate    = (completed_ords / total_orders * 100)  if total_orders > 0 else 0.0
    return_rate        = (cancelled_ords / total_orders * 100)  if total_orders > 0 else 0.0
    retention_rate     = (repeat_customers / total_customers * 100) if total_customers > 0 else 0.0
    inventory_turnover = (cogs_30d / inventory_value) if inventory_value > 0 else 0.0
    order_frequency    = (total_orders / total_customers) if total_customers > 0 else 0.0

    return {
        "today_revenue":        today_revenue,
        "today_transactions":   today_count,
        "sales_growth":         sales_growth,
        "sales_trend_up":       sales_growth >= 0,
        "transaction_growth":   transaction_growth,
        "transaction_trend_up": transaction_growth >= 0,
        "best_seller":          best_seller,
        "low_stock_count":      low_stock_count,
        "revenue_30d":          revenue_30d,
        "profit_margin":        profit_margin,
        "monthly_growth":       monthly_growth,
        "avg_order_value":      avg_order_value,
        "retention_rate":       retention_rate,
        "conversion_rate":      conversion_rate,
        "return_rate":          return_rate,
        "order_frequency":      order_frequency,
        # FIX-1/FIX-2: pending_orders always present, always int
        "pending_orders":       pending_orders,
        "inventory_value":      inventory_value,
        "inventory_turnover":   inventory_turnover,
        "active_products":      active_products,
        "total_locations":      total_locations,
    }


# ──────────────────────────────────────────────────────────────────────
# KPI FORMATTER
# ──────────────────────────────────────────────────────────────────────

def _build_kpis(raw: dict) -> dict:
    """
    Format raw data into display-ready strings.
    ALL keys use snake_case — matches {{ kpis.x }} in template
    AND data.kpis.x in JS (auto-refresh fetch).
    """
    bs = raw["best_seller"]
    mg = raw["monthly_growth"]
    sg = raw["sales_growth"]
    tg = raw["transaction_growth"]

    return {
        # ── Top 4 KPI cards ──────────────────────────────────
        "today_sales":          smart_currency_format(raw["today_revenue"]),
        "sales_growth":         f"{sg:+.1f}%",
        "sales_trend_up":       raw["sales_trend_up"],
        "total_transactions":   raw["today_transactions"],
        "transaction_growth":   f"{tg:+.1f}%",
        "transaction_trend_up": raw["transaction_trend_up"],
        "best_seller_name":     bs["variant__product__name"] if bs else "N/A",
        "best_seller_count":    f"{bs['total_sold']} sold" if bs else "0 sold",
        "low_stock_count":      raw["low_stock_count"],

        # ── Performance metrics strip ─────────────────────────
        "monthly_growth":     f"{mg:+.1f}%",
        "customer_retention": safe_percent_format(raw["retention_rate"]),
        "avg_order_value":    smart_currency_format(raw["avg_order_value"]),
        "inventory_turnover": f"{raw['inventory_turnover']:.1f}x/month",

        # ── Additional KPI white cards ────────────────────────
        "total_revenue":        smart_currency_format(raw["revenue_30d"]),
        "profit_margin":        safe_percent_format(raw["profit_margin"]),
        "return_rate":          safe_percent_format(raw["return_rate"]),
        "inventory_value":      smart_currency_format(raw["inventory_value"]),
        "order_frequency":      f"{raw['order_frequency']:.2f}/month",
        "conversion_rate":      safe_percent_format(raw["conversion_rate"]),
        "repeat_purchase_rate": safe_percent_format(raw["retention_rate"]),

        # FIX-1: was missing — caused Pending Orders card to show "—"
        "pending_orders":       raw["pending_orders"],
    }


# ──────────────────────────────────────────────────────────────────────
# CHART DATA
# ──────────────────────────────────────────────────────────────────────

def _get_chart_data(period: str = "7d") -> dict:
    today = timezone.now().date()

    if period == "7d":
        start = today - timedelta(days=6)
        qs = (
            OrderItem.objects
            .filter(order__status="completed", order__created_at__date__gte=start)
            .values("order__created_at__date")
            .annotate(total=Sum(F("quantity") * F("price"), output_field=DecimalField()))
        )
        dm     = {r["order__created_at__date"]: float(r["total"]) for r in qs}
        labels = [(today - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
        actual = [dm.get(today - timedelta(days=i), 0.0) for i in range(6, -1, -1)]

    elif period == "30d":
        start = today - timedelta(weeks=4)
        qs = (
            OrderItem.objects
            .filter(order__status="completed", order__created_at__date__gte=start)
            .values("order__created_at__date")
            .annotate(total=Sum(F("quantity") * F("price"), output_field=DecimalField()))
        )
        dm     = {r["order__created_at__date"]: float(r["total"]) for r in qs}
        labels, actual = [], []
        for w in range(4):
            ws = start + timedelta(weeks=w)
            labels.append(f"Week {w + 1}")
            actual.append(sum(dm.get(ws + timedelta(days=d), 0.0) for d in range(7)))

    else:  # "1y"
        labels, actual = [], []
        for i in range(11, -1, -1):
            ms, me = _month_range(today, -i)
            agg = OrderItem.objects.filter(
                order__status="completed",
                order__created_at__date__gte=ms,
                order__created_at__date__lt=me,
            ).aggregate(total=Sum(F("quantity") * F("price"), output_field=DecimalField()))
            labels.append(ms.strftime("%b"))
            actual.append(float(agg["total"] or 0))

    return {
        "labels": labels,
        "actual": actual,
        "target": [round(v * 0.9, 2) for v in actual],
    }


# ──────────────────────────────────────────────────────────────────────
# VIEWS
# ──────────────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """
    Main dashboard.
    - kpis, quick_stats  → Django context for SSR ({{ kpis.x }})
    - dashboard_data     → json_script for JS auto-refresh bootstrap
    All keys snake_case so template + JS use the same names.
    """
    today      = timezone.now().date()
    raw        = _fetch_dashboard_data(today)
    kpis       = _build_kpis(raw)
    period     = request.GET.get("period", "7d")
    chart_data = _get_chart_data(period)

    # FIX-2: cast to str so that 0 is "0" (truthy) and Django's
    #         |default:"—" filter does NOT replace it with a dash.
    quick_stats = {
        "active_products": str(raw["active_products"]),
        "pending_orders":  str(raw["pending_orders"]),
        "total_locations": str(raw["total_locations"]),
    }

    dashboard_data = json.dumps({
        "kpis":         kpis,
        "chart_data":   chart_data,
        "quick_stats":  quick_stats,
        "last_updated": timezone.now().strftime("%H:%M"),
    })

    # Placeholder for notifications
    notifications_count = 0
    notifications       = []

    return render(request, "lumra_pages/dashboard.html", {
        "kpis":                kpis,
        "quick_stats":         quick_stats,
        "dashboard_data":      dashboard_data,
        "notifications_count": notifications_count,
        "notifications":       notifications,
    })


@login_required
def notification_view(request):
    notifications = []

    context = {
        "notifications": notifications,
        "notifications_json": json.dumps(
            [
                {
                    "id":           n.get("id", ""),
                    "type":         n.get("type", "system"),
                    "title":        n.get("title", ""),
                    "message":      n.get("message", ""),
                    "full_message": n.get("full_message", ""),
                    "action_url":   n.get("action_url", ""),
                    "timestamp":    n.get("timestamp", timezone.now().isoformat()),
                    "isRead":       n.get("isRead", False),
                }
                for n in notifications
            ],
            cls=DjangoJSONEncoder,
        ),
    }
    return render(request, "lumra_pages/notification.html", context)


# ──────────────────────────────────────────────────────────────────────
# AJAX API ENDPOINTS  (called by dashboard.js auto-refresh)
# Register in urls.py:
#   path("api/dashboard/data/",       dashboard_views.api_dashboard_data),
#   path("api/dashboard/chart-data/", dashboard_views.api_dashboard_chart_data),
# ──────────────────────────────────────────────────────────────────────

@login_required
def api_dashboard_data(request):
    """GET /api/dashboard/data/ — full KPI + chart refresh."""
    today      = timezone.now().date()
    raw        = _fetch_dashboard_data(today)
    kpis       = _build_kpis(raw)  # FIX-1/5: pending_orders now included
    period     = request.GET.get("period", "7d")
    chart_data = _get_chart_data(period)

    return JsonResponse({
        "kpis":       kpis,
        "chart_data": chart_data,
        "quick_stats": {
            # FIX-2: cast to str so JS _updateQuickStats won't get 0 as falsy
            "active_products": str(raw["active_products"]),
            "pending_orders":  str(raw["pending_orders"]),
            "total_locations": str(raw["total_locations"]),
        },
        "last_updated": timezone.now().strftime("%H:%M"),
    })


@login_required
def api_dashboard_chart_data(request):
    """GET /api/dashboard/chart-data/?period=7d|30d|1y — chart-only refresh."""
    period = request.GET.get("period", "7d")
    if period not in ("7d", "30d", "1y"):
        return JsonResponse(
            {"error": "Invalid period. Use '7d', '30d', or '1y'."},
            status=400,
        )
    return JsonResponse(_get_chart_data(period))