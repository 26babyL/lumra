# lumra_config/views/misc_views.py
# Auto-generated oleh lumra_sync.py dari core/views/misc_views.py
# JANGAN EDIT MANUAL — edit core/views/misc_views.py lalu jalankan lumra_sync.py lagi

# Miscellaneous views yang tidak fit dalam kategori khusus

import json
from datetime import timedelta, datetime, time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, DecimalField, F, Q, Sum
from django.db.models.functions import TruncDate
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from decimal import Decimal
from lumra_config.models import Location


from lumra_config.models import (
    Location,
    Customer,
    Order,
    OrderItem,
    Product,
    ProductVariant,
    SalesTarget,
    UserProfile,
    Vendor,
)
from .helpers import (check_queryset_empty, create_empty_context, create_error_context, safe_get, safe_related, safe_select_related, model_has_field)


# ------------------------------------------------------------------
# Role‑based access support
#
# The RBAC engine is defined in the frontend (`user_roles_permissions.html`)
# and includes a big default matrix of permissions keyed by role names.  In
# order for the various business‑settings templates to behave correctly they
# need to know which permissions the *current* user has.  We reproduce a
# small subset of the JS defaults here and expose them via the view context
# so the templates can render accordingly (show/hide buttons, display an
# "access denied" message, etc.).  This keeps the Python and JS sides in
# sync and avoids sprinkling hard‑coded role checks through the markup.

DEFAULT_ROLE_PERMS = {
    'superadmin': {
        # full‑access shortcut; every key is True
        # in practice the frontend computes this with ``_allTrue()`` but
        # replicating the full dictionary is easiest for testing.
        **{k: True for k in [
            # small sample, the template will ignore extras
            'sys_config', 'sys_status', 'sys_logs', 'sys_backup',
            'sku_view', 'pos_access', 'sales_view',
        ]},
    },
    'admin': {
        'sys_config': False,  # admins are not automatically granted shop
                             # configuration rights in the default matrix
        'sys_status': True,
        'sys_logs': True,
        'sys_backup': False,
        'sku_view': True,
        'pos_access': True,
        'sales_view': True,
    },
    'manager': {
        'sys_config': False,
        'sys_status': False,
        'sys_logs': False,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        'sys_backup': False,
        'sku_view': True,
        'pos_access': True,
        'sales_view': True,
    },
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    'staff': {
        'sys_config': False,
        'sys_status': False,
        'sys_logs': False,
        'sys_backup': False,
        'sku_view': True,
        'pos_access': True,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        'sales_view': False,
    },
    'viewer': {
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        'sys_config': False,
        'sys_status': False,
        'sys_logs': False,
        'sys_backup': False,
        'sku_view': True,
        'pos_access': False,
        'sales_view': True,
    },
}


def get_user_permissions(user):
    """Return a permissions dict for the given user.

    The returned object mirrors the shape that the frontend expects for
    ``perms-data``.  Currently we only care about a handful of keys –
    ``sys_config`` is the one used by the business‑settings pages – but we
    keep the printed dictionary small so the JSON payload is light.
    """
    role = getattr(getattr(user, 'profile', None), 'role', '') or ''
    role_key = role.lower()
    return DEFAULT_ROLE_PERMS.get(role_key, DEFAULT_ROLE_PERMS['viewer'])



# =====================================================
# TODO[C3-LONG]: 'pos_view' = 51 baris (max 30). Pecah: pos_view_validate(), pos_view_query(), pos_view_render()
# SALES & POS VIEWS
# =====================================================
 # TODO[C3-LONG]: 'pos_view' terlalu panjang (54 baris). Pecah: pos_view_validate(), pos_view_build_context(), pos_view_render()

@login_required
# TODO[C3-LONG]: 'pos_view' = 63 baris (maks 30). Pecah: pos_view_validate(), pos_view_process(), pos_view_respond()
def pos_view(request):
    """Point of Sale (POS) untuk transaksi penjualan.

    The template expects `products` to be a JSON string (consumed via
    `json_script`) rather than a raw queryset.  Previously we were
    passing a queryset directly which triggered the
    ``Object of type QuerySet is not JSON serializable`` error.

    We also supply a ``categories`` value so the tab bar loop in the
    template has something to iterate over.
    """

    # queryset of variants with related product and category for later
    # serialization; ordering mimics original behaviour
    variants = (
        ProductVariant.objects
        .select_related("product__category")
        .order_by("sku")
    )

    # convert to plain Python objects suitable for json.dumps()
    products_data = []
    for value_item in variants:
        prod = v.product
        products_data.append({
            "id": v.id,
            "name": prod.name,
            "sku": v.sku,
            "price": float(v.price_sell),
            "stock": int(v.total_stock),
            "image_url": prod.image.url if getattr(prod, "image", None) else "",
            "category_id": str(prod.category_id) if prod.category_id else "",
            "category": prod.category.name if prod.category else "",
        })
    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.

    products_json = json.dumps(products_data)
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan Model.objects.select_related('...').prefetch_related('...')

    # categories for the tabs; use Category model so IDs are available
    from lumra_config.models import Category
    categories = Category.objects.filter(is_active=True).order_by("name")

    # minimal extras so template can always call json_script safely
    context = {
        "products": products_json,
        "categories": categories,
        "discount_presets": json.dumps([]),   # will be replaced with real data later
        "payment_methods": json.dumps([]),
        "held_orders": json.dumps([]),
        "tax_rate": 0,
    }
    return render(request, "lumra_pages/sales_insight/pos.html", context)


# ------------------------------------------------------------------
# SALES / POS API
# ------------------------------------------------------------------

# we import json here with alias to avoid shadowing earlier 'json'
import json as _json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # template uses fetch with csrftoken header


@login_required
@csrf_exempt
def pos_create_order(request):
    """Endpoint called by the POS front end (``confirmPayment()``).

    This stub mirrors the example from the user’s description; it
    simply validates the request payload and returns a success flag
    until you wire it up to your actual Order/OrderItem models.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = _json.loads(request.body)
    except _json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    # TODO: implement order creation logic (see earlier comment in
    # conversation for a reference snippet)

    # TODO[C3-LONG]: 'purchasing_view' = 32 baris (max 30). Pecah: purchasing_view_validate(), purchasing_view_query(), purchasing_view_render()
    # placeholder response
    return JsonResponse({"success": True, "order_id": 0})

 # TODO[C3-LONG]: 'purchasing_view' terlalu panjang (33 baris). Pecah: purchasing_view_validate(), purchasing_view_build_context(), purchasing_view_render()

@login_required
# TODO[C3-LONG]: 'purchasing_view' = 36 baris (maks 30). Pecah: purchasing_view_validate(), purchasing_view_process(), purchasing_view_respond()
def purchasing_view(request):
    """Halaman untuk manajemen pembelian."""
    # Lazy loading: hanya ambil 1000 data pertama
    page = int(request.GET.get('page', 1))
    per_page = 1000
    
    # FIX: annotate langsung, tidak perlu loop manual set _cached_total_stock
    products = (
        ProductVariant.objects
        .select_related("product")
        .annotate(total_stock=Sum("stock_entries__quantity"))
    )

    # Pagination
    paginator = Paginator(products, per_page)
    page_obj  = paginator.get_page(page)
    
    # Total count untuk UI
    total_count = products.count()
    has_more = total_count > (page * per_page)
    
    vendors = [
        {"id": vendor.id, "name": vendor.name, "price": 0}
        for vendor in Vendor.objects.filter(is_active=True).order_by("name")
    ]

    context = {
        "page_obj":          page_obj,
        "vendors":           Vendor.objects.filter(is_active=True).order_by("name"),
        "vendors_json":      json.dumps(vendors),
        "requisition_count": 0,
        "is_empty": False,
        "total_count": total_count,
        "current_page": page,
        "per_page": per_page,
        "has_more": has_more,
        "is_loading_more": False,
    }
    return render(request, "lumra_pages/purchasing/purchasing.html", context)


# TODO[C3-LONG]: 'sales_history_view' terlalu panjang (142 baris). Pecah: sales_history_view_validate(), sales_history_view_build_context(), sales_history_view_render()
@login_required
@login_required
# TODO[C3-LONG]: 'sales_history_view' = 150 baris (maks 30). Pecah: sales_history_view_validate(), sales_history_view_process(), sales_history_view_respond()
def sales_history_view(request):
    """
    Sales History — satu view, dua entry point:
      /sales/history/          (sidebar Sales)
      /insights/sales_insight/ (sidebar Insights) — alias di bawah
    Template: lumra_pages/sales/sales_insight.html
    """
    from .helpers import safe_get, safe_select_related
 
    # ── Sorting ───────────────────────────────────────────────────────
    ALLOWED_SORT = {
        'order.id'            : 'order__id',
        'order.customer_name' : 'order__customer_name',
        'order.created_at'    : 'order__created_at',
        'variant.product.name': 'variant__product__name',
        'quantity'            : 'quantity',
        'price'               : 'price',
        'total'               : 'quantity',
    }
    sort_by = request.GET.get('sort_by', 'order.created_at')
    order   = request.GET.get('order', 'desc')
    db_sort = ALLOWED_SORT.get(sort_by, 'order__created_at')
    if order == 'desc':
        db_sort = '-' + db_sort
 
    # ── Base queryset — hanya field yang PASTI ada ────────────────────
    qs = OrderItem.objects.select_related(
        'order',
        'order__customer',
        'variant',
        'variant__product',
    )
 
    # Field opsional — ditambahkan hanya kalau ada di model
    qs = safe_select_related(
        qs,
        'order__location',     # belum ada di model sekarang → di-skip otomatis
        'order__cashier',      # idem
        'variant__product__category',
    )
 
    qs = qs.order_by(db_sort)
 
    # ── Filters ───────────────────────────────────────────────────────
    search     = request.GET.get('search', '').strip()
    store_id   = request.GET.get('store', '').strip()
    date_start = request.GET.get('date_start', '').strip()
    date_end   = request.GET.get('date_end', '').strip()
 
    if search:
        qs = qs.filter(
            Q(order__customer_name__icontains=search) |
            Q(variant__product__name__icontains=search) |
            Q(variant__sku__icontains=search)
        )
 
    # Filter store hanya kalau field-nya ada di model Order
    if store_id and model_has_field(Order, 'location'):
        qs = qs.filter(order__location_id=store_id)
 
    if date_start:
        qs = qs.filter(order__created_at__date__gte=date_start)
    if date_end:
        qs = qs.filter(order__created_at__date__lte=date_end)
 
    # ── Aggregates ────────────────────────────────────────────────────
    sales_list   = list(qs)
    total_qty    = sum(i.quantity for i in sales_list)
    total_amount = sum(i.quantity * i.price for i in sales_list)
    total_orders = len({i.order_id for i in sales_list})
 
    # ── Anomaly detection — transaksi > 2× rata-rata ──────────────────
    avg_amount  = float(total_amount) / total_orders if total_orders > 0 else 0
    threshold   = avg_amount * 2
    anomaly_ids = []
 
    for item in sales_list:
        item_total      = float(item.quantity * item.price)
        item.is_anomaly = item_total > threshold and threshold > 0
        if item.is_anomaly:
            anomaly_ids.append(item.order_id)
 
    anomaly_count = len(anomaly_ids)
 
    # ── Daily growth ──────────────────────────────────────────────────
    today     = timezone.now().date()
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan Model.objects.select_related('...').prefetch_related('...')
    yesterday = today - timedelta(days=1)
 
    def day_revenue(d):
        try:
            rows = OrderItem.objects.filter(order__created_at__date=d)
            return float(sum(r.quantity * r.price for r in rows))
        except Exception:
            return 0.0
 
    today_rev     = day_revenue(today)
    yesterday_rev = day_revenue(yesterday)
    daily_growth  = (
        round((today_rev - yesterday_rev) / yesterday_rev * 100, 1)
        if yesterday_rev > 0 else 0
    )
 
    # ── Sparkline 7 hari ─────────────────────────────────────────────
    day_names        = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
    sparkline_labels = []
    sparkline_data   = []
 
    for i in range(6, -1, -1):
        data_dict = today - timedelta(days=i)
        sparkline_labels.append('Hari Ini' if i == 0 else day_names[d.weekday()])
        sparkline_data.append(day_revenue(d))
 
    # ── Pagination ────────────────────────────────────────────────────
    paginator = Paginator(sales_list, 25)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
 
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan Model.objects.select_related('...').prefetch_related('...')
    # ── Stores — hanya kalau model Order punya field location ─────────
    stores = []
    if model_has_field(Order, 'location'):
        stores = Location.objects.all().order_by('name')
 
    context = {
        'sales'            : page_obj,
        'page_obj'         : page_obj,
        'total_orders'     : total_orders,
        'total_qty'        : total_qty,
        'total_amount'     : total_amount,
        'avg_amount'       : round(avg_amount, 2),
        'anomaly_ids'      : anomaly_ids,
        'anomaly_count'    : anomaly_count,
        'daily_growth'     : daily_growth,
        'sparkline_labels' : sparkline_labels,
        'sparkline_data'   : sparkline_data,
        'stores'           : stores,
        'sort_by'          : sort_by,
        'order'            : order,
        'today_str'        : today.strftime('%Y-%m-%d'),
        'yesterday_str'    : yesterday.strftime('%Y-%m-%d'),
        'report_title'     : 'Sales History',
    }
 
    return render(request, 'lumra_pages/sales_insight/sales_intelligence.html', context)
 
  # TODO[C3-LONG]: 'sales_history_products_view' = 66 baris (max 30). Pecah: sales_history_products_view_validate(), sales_history_products_view_query(), sales_history_products_view_render()
 
# Alias — URL /insights/sales_insight/ pakai view yang sama
sales_insight_view = sales_history_view


# TODO[C3-LONG]: 'sales_history_products_view' terlalu panjang (67 baris). Pecah: sales_history_products_view_validate(), sales_history_products_view_build_context(), sales_history_products_view_render()
# FIX: tambah @login_required yang sebelumnya hilang
@login_required
# TODO[C3-LONG]: 'sales_history_products_view' = 67 baris (maks 30). Pecah: sales_history_products_view_validate(), sales_history_products_view_process(), sales_history_products_view_respond()
def sales_history_products_view(request):
    """Sales history per produk dengan detail — N+1 diperbaiki."""

    products = Product.objects.select_related("category").all()

    # Check if products is empty
    if not products.exists():
        return render(
            request,
            "lumra_pages/reports/sales_history_product.html",
            create_empty_context("Sales History - Products", "Data produk tidak ditemukan.")
        )

    thirty_days_ago = timezone.now() - timedelta(days=30)

    # FIX: ganti loop + per-product query → 2 bulk query
    # Query 1: total units & revenue per product (all-time)
    totals_by_product = {
        row["variant__product_id"]: row
        for row in OrderItem.objects.values("variant__product_id").annotate(
            units_sold=Sum("quantity"),
            revenue=Sum(F("quantity") * F("price"), output_field=DecimalField()),
        )
    }

    # Query 2: daily sales per product (30 hari terakhir)
    recent_qs = (
        OrderItem.objects
        .filter(order__created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate("order__created_at"))
        .values("variant__product_id", "date")
        .annotate(
            units=Sum("quantity"),
            revenue=Sum(F("quantity") * F("price"), output_field=DecimalField()),
        )
        .order_by("variant__product_id", "-date")
    )

    # Group recent sales by product id
    recent_by_product: dict[int, list] = {}
    for row in recent_qs:
        pid = row["variant__product_id"]
        recent_by_product.setdefault(pid, []).append({
            "date":    str(row["date"]),
            "units":   row["units"],
            "revenue": float(row["revenue"] or 0),
        })

    product_sales = []
    for product in products:
        totals = totals_by_product.get(product.id, {})
        product_sales.append({
            "id":           product.id,
            "name":         product.name,
            "description":  product.description,
            "category":     product.category.name if product.category else None,
            "unitsSold":    totals.get("units_sold") or 0,
            "revenue":      float(totals.get("revenue") or 0),
            "salesHistory": recent_by_product.get(product.id, []),
        })

    # TODO[C3-LONG]: 'sales_performance_view' = 308 baris (max 30). Pecah: sales_performance_view_validate(), sales_performance_view_query(), sales_performance_view_render()
    context = {
        "products": json.dumps(product_sales, default=str),
        "is_empty": False,
    }
    return render(request, "lumra_pages/reports/sales_history_product.html", context)
sales_insight_view = sales_history_view  # alias untuk /insights/sales_insight/ yang sebelumnya hilang
 # TODO[C3-LONG]: 'sales_performance_view' terlalu panjang (308 baris). Pecah: sales_performance_view_validate(), sales_performance_view_build_context(), sales_performance_view_render()

@login_required
# TODO[C3-LONG]: 'sales_performance_view' = 317 baris (maks 30). Pecah: sales_performance_view_validate(), sales_performance_view_process(), sales_performance_view_respond()
def sales_performance_view(request):
    """
    Sales Performance — 3 sections:
    1. Target vs Realisasi (SalesTarget model)
    2. Trend harian/mingguan (Chart.js line+bar)
    3. Performa customer (repeat buyers, tier, new vs returning)
 
    Menerima context dari Sales History via:
      ?date_start=...&date_end=...&from=sales_history&highlight=trend
    """
    from django.db.models import Avg, Count, Max, Min
    from django.db.models.functions import TruncDate, TruncWeek
    from lumra_config.models import Customer, SalesTarget
    import calendar
 
    # ── 1. Params & date range ─────────────────────
    date_start = request.GET.get('date_start', '')
    date_end   = request.GET.get('date_end',   '')
    from_page  = request.GET.get('from', '')       # 'sales_history' or ''
    highlight  = request.GET.get('highlight', '')  # 'trend' | 'target' | 'customer'
 
    today = timezone.now().date()
 
    if date_start and date_end:
        try:
            ds = datetime.strptime(date_start, '%Y-%m-%d').date()
            de = datetime.strptime(date_end,   '%Y-%m-%d').date()
        except ValueError:
            ds = today.replace(day=1)
            de = today
    else:
        ds = today.replace(day=1)   # default: bulan ini
        de = today
 
    filter_start = timezone.make_aware(datetime.combine(ds, time.min))
    filter_end   = timezone.make_aware(datetime.combine(de, time.max))
 
    # ── 2. Base queryset ───────────────────────────
    orders_qs = (
        Order.objects
        .filter(created_at__range=(filter_start, filter_end))
        .annotate(
            order_total=Sum(
                F('items__quantity') * F('items__price'),
                output_field=DecimalField()
            )
        )
    )
 
    # ── 3. Section 1: Target vs Realisasi ─────────
    # Ambil target untuk bulan-bulan dalam range
    months_in_range = set()
    cur = ds.replace(day=1)
    while cur <= de:
        months_in_range.add((cur.year, cur.month))
        # Next month
        if cur.month == 12:
            cur = cur.replace(year=cur.year+1, month=1)
        else:
            cur = cur.replace(month=cur.month+1)
 
    targets_qs = SalesTarget.objects.filter(
        year__in=[y for y,m in months_in_range],
        month__in=[m for y,m in months_in_range],
    )
    target_map = {(t.year, t.month): float(t.target_amount) for t in targets_qs}
 
    # Realisasi per bulan
    from django.db.models.functions import TruncMonth
    monthly_revenue = (
        Order.objects
        .filter(created_at__range=(filter_start, filter_end))
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            revenue=Sum(
                F('items__quantity') * F('items__price'),
                output_field=DecimalField()
            ),
            order_count=Count('id', distinct=True)
        )
        .order_by('month')
    )
 
    target_chart = []
    for row in monthly_revenue:
        m = row['month']
        yr, mo = m.year, m.month
        tgt = target_map.get((yr, mo), 0)
        rev = float(row['revenue'] or 0)
        pct = round((rev / tgt * 100), 1) if tgt > 0 else None
        target_chart.append({
            'label'      : f"{m.strftime('%b')} {yr}",
            'target'     : tgt,
            'realisasi'  : rev,
            'pct'        : pct,
            'order_count': row['order_count'],
            'status'     : 'achieved' if (pct or 0) >= 100
                           else 'on_track' if (pct or 0) >= 70
                           else 'behind',
        })
 
    # Total target & realisasi dalam range
    total_target     = sum(target_map.get(ym, 0) for ym in months_in_range)
    total_realisasi  = sum(r['realisasi'] for r in target_chart)
    total_pct        = round(total_realisasi / total_target * 100, 1) if total_target else None
 
    # Handle POST: set target baru
    if request.method == 'POST' and request.user.is_staff:
        try:
            yr  = int(request.POST.get('target_year'))
            mo  = int(request.POST.get('target_month'))
            amt = float(request.POST.get('target_amount', 0))
            notes = request.POST.get('notes', '')
            SalesTarget.objects.update_or_create(
                year=yr, month=mo,
                defaults={
                    'target_amount': amt,
                    'notes'        : notes,
                    'created_by'   : request.user,
                }
            )
            messages.success(request, f"Target berhasil disimpan.")
        except (ValueError, TypeError):
            messages.error(request, "Format angka tidak valid.")
        return redirect(request.path + f'?date_start={date_start}&date_end={date_end}')
 
    # ── 4. Section 2: Trend harian ─────────────────
    daily_trend = (
        OrderItem.objects
        .filter(order__created_at__range=(filter_start, filter_end))
        .annotate(date=TruncDate('order__created_at'))
        .values('date')
        .annotate(
            revenue=Sum(F('quantity') * F('price'), output_field=DecimalField()),
            order_count=Count('order', distinct=True),
            items_sold=Sum('quantity'),
        )
        .order_by('date')
    )
 
    trend_labels   = []
    trend_revenue  = []
    trend_orders   = []
    trend_items    = []
    for row in daily_trend:
        trend_labels.append(row['date'].strftime('%d %b'))
        trend_revenue.append(float(row['revenue'] or 0))
        trend_orders.append(row['order_count'])
        trend_items.append(row['items_sold'])
 
    # Moving average 3-hari
    ma3 = []
    for i in range(len(trend_revenue)):
        window = trend_revenue[max(0, i-2):i+1]
        ma3.append(round(sum(window) / len(window), 2))
 
    # ── 5. Section 3: Customer performance ─────────
    # Revenue per customer dalam periode
    customer_revenue = (
        Order.objects
        .filter(created_at__range=(filter_start, filter_end))
        .values('customer_id', 'customer__name', 'customer__tier')
        .annotate(
            period_revenue=Sum(
                F('items__quantity') * F('items__price'),
                output_field=DecimalField()
            ),
            period_orders=Count('id', distinct=True),
        )
        .filter(customer_id__isnull=False)
        .order_by('-period_revenue')[:10]
    )
 
    top_customers = [
        {
            'name'    : r['customer__name'] or 'Guest',
            'tier'    : r['customer__tier'] or 'bronze',
            'revenue' : float(r['period_revenue'] or 0),
            'orders'  : r['period_orders'],
            'avg'     : float(r['period_revenue'] or 0) / r['period_orders']
                        if r['period_orders'] else 0,
        }
        for r in customer_revenue
    ]
 
    # Tier distribution dalam periode
    tier_dist = (
        Order.objects
        .filter(
            created_at__range=(filter_start, filter_end),
            customer__isnull=False
        )
        .values('customer__tier')
        .annotate(
            count=Count('id', distinct=True),
            revenue=Sum(
                F('items__quantity') * F('items__price'),
                output_field=DecimalField()
            )
        )
        .order_by('-revenue')
    )
    tier_labels  = []
    tier_counts  = []
    tier_revenue = []
    TIER_COLORS  = {
        'platinum': '#6366f1',
        'gold'    : '#f59e0b',
        'silver'  : '#94a3b8',
        'bronze'  : '#92400e',
    }
    for t in tier_dist:
        tier_labels.append((t['customer__tier'] or 'bronze').capitalize())
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan Model.objects.select_related('...').prefetch_related('...')
        tier_counts.append(t['count'])
        tier_revenue.append(float(t['revenue'] or 0))
 
    # New vs returning (customer created dalam periode = new)
    new_customers = Customer.objects.filter(
        created_at__range=(filter_start, filter_end)
    ).count()
    returning_customers = (
        Order.objects
        .filter(
            created_at__range=(filter_start, filter_end),
            customer__created_at__lt=filter_start,
            customer__isnull=False
        )
        .values('customer_id')
        .distinct()
        .count()
    )
 
    # Repeat buyers (order > 1 dalam periode)
    repeat_buyers = (
        Order.objects
        .filter(created_at__range=(filter_start, filter_end))
        .values('customer_id')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1, customer_id__isnull=False)
        .count()
    )
 
    # Summary stats
    total_orders_count = orders_qs.count()
    total_revenue      = float(
        orders_qs.aggregate(t=Sum('order_total'))['t'] or 0
    )
    avg_order_value    = total_revenue / total_orders_count if total_orders_count else 0
 
    # Back-link context (dari Sales History)
    back_context = None
    if from_page == 'sales_history':
        back_context = {
            'url'        : f"/reports/history/?date_start={date_start}&date_end={date_end}",
            'label'      : f"Sales History ({ds.strftime('%d %b')} – {de.strftime('%d %b %Y')})",
            'orders'     : total_orders_count,
            'revenue'    : total_revenue,
        }
 
    # ── 6. Context ─────────────────────────────────
    context = {
        # Meta
        'report_title'    : 'Sales Performance',
        'date_start'      : str(ds),
        'date_end'        : str(de),
        'from_page'       : from_page,
        'highlight'       : highlight,
        'back_context'    : back_context,
 
        # Summary KPI
        'total_revenue'   : total_revenue,
        'total_orders'    : total_orders_count,
        'avg_order_value' : avg_order_value,
        'total_target'    : total_target,
        'total_pct'       : total_pct,
 
        # Section 1 — Target
        'target_chart_json': json.dumps(target_chart),
        'total_target'     : total_target,
        'total_realisasi'  : total_realisasi,
        'months_in_range'  : sorted(months_in_range),
        'current_year'     : today.year,
        'current_month'    : today.month,
        'month_choices'    : [
            (1,'Januari'),(2,'Februari'),(3,'Maret'),(4,'April'),
            (5,'Mei'),(6,'Juni'),(7,'Juli'),(8,'Agustus'),
            (9,'September'),(10,'Oktober'),(11,'November'),(12,'Desember'),
        ],
        'presets'          : [],   # passed as JS inline
        'target_chart'     : target_chart,
 
        # Section 2 — Trend
        'trend_labels_json'  : json.dumps(trend_labels),
        'trend_revenue_json' : json.dumps(trend_revenue),
        'trend_orders_json'  : json.dumps(trend_orders),
        'trend_ma3_json'     : json.dumps(ma3),
 
        # Section 3 — Customer
        'top_customers_json' : json.dumps(top_customers),
        'tier_labels_json'   : json.dumps(tier_labels),
        'tier_revenue_json'  : json.dumps(tier_revenue),
        'new_customers'      : new_customers,
        'returning_customers': returning_customers,
        'repeat_buyers'      : repeat_buyers,
    }
 
    return render(request, 'lumra_pages/sales_insight/sales_performance.html', context)
 
 
 
# =====================================================
# CUSTOMER MANAGEMENT
# =====================================================
 
@login_required
def customers_view(request):
    context = {"customers": []}
    return render(request, "lumra_pages/master_data/customers.html", context)
 
 
@login_required
def add_customer_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/master_data/customers.html", context)


@login_required
def view_customer_view(request, customer_id):
    context = {"customer_id": customer_id}
    return render(request, "lumra_pages/master_data/customers.html", context)


@login_required
def edit_customer_view(request, customer_id):
    context = {"customer_id": customer_id, "action": "edit"}
    return render(request, "lumra_pages/master_data/customers.html", context)


@login_required
def delete_customer_view(request, customer_id):
    # FIX: stub views untuk destructive actions sebaiknya POST-only
    if request.method != "POST":
        return render(request, "lumra_pages/master_data/customers.html", {"customer_id": customer_id})
    # TODO: implement actual delete logic
    messages.warning(request, "Delete customer belum diimplementasi.")
    return redirect("customers")


# =====================================================
# CAMPAIGN MANAGEMENT
# =====================================================

@login_required
def campaign_list_view(request):
    targets = SalesTarget.objects.order_by("-year", "-month")[:1000]
    campaigns = [
        {
            "id": target.id,
            "name": f"Sales Target {target.get_month_display()} {target.year}",
            "description": target.notes,
            "type": "loyalty",
            "status": "active",
            "target_scope": "all",
            "budget": target.target_amount,
            "start_date": datetime(target.year, target.month, 1).date(),
            "end_date": (
                datetime(target.year + (target.month // 12), (target.month % 12) + 1, 1).date()
                - timedelta(days=1)
            ),
            "usage_count": 0,
            "usage_limit": None,
            "customer_tier": "",
        }
        for target in targets
    ]
    context = {
        "total_campaigns":     SalesTarget.objects.count(),
        "active_campaigns":    len(campaigns),
        "completed_campaigns": 0,
        "total_budget":        sum((item["budget"] for item in campaigns), Decimal("0")),
        "avg_roi":             0,
        "campaigns":           campaigns,
        "query":               request.GET.get("q", ""),
    }
    return render(request, "lumra_pages/marketing/campaign_list.html", context)


@login_required
def add_campaign_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/marketing/campaign.html", context)


@login_required
def edit_campaign_view(request, campaign_id):
    context = {"campaign_id": campaign_id, "action": "edit"}
    return render(request, "lumra_pages/marketing/campaign.html", context)


@login_required
def delete_campaign_view(request, campaign_id):
    if request.method != "POST":
        return render(request, "lumra_pages/marketing/campaign.html", {"campaign_id": campaign_id})
    messages.warning(request, "Delete campaign belum diimplementasi.")
    return redirect("campaign_list")


# =====================================================
# DISCOUNT MANAGEMENT
# =====================================================

@login_required
def discount_list_view(request):
    discounted_items = (
        OrderItem.objects
        .select_related("order", "variant", "variant__product")
        .filter(Q(discount_amount__gt=0) | Q(discount_percent__gt=0))
        .order_by("-order__created_at")[:1000]
    )
    discounts = []
    total_savings = Decimal("0")
    for item in discounted_items:
        is_percent = bool(item.discount_percent and item.discount_percent > 0)
        value = item.discount_percent if is_percent else item.discount_amount
        total_savings += (item.discount_amount or Decimal("0"))
        discounts.append({
            "id": item.id,
            "name": item.variant.product.name,
            "code": f"DISC-{item.id:05d}",
            "type": "percentage" if is_percent else "fixed",
            "value": value,
            "status": "active",
            "start_date": item.order.created_at.date(),
            "end_date": item.order.created_at.date(),
        })
    context = {
        "total_discounts":  OrderItem.objects.filter(Q(discount_amount__gt=0) | Q(discount_percent__gt=0)).count(),
        "active_discounts": len(discounts),
        "total_usage":      len(discounts),
        "total_savings":    total_savings,
        "discounts":        discounts,
        "query":            request.GET.get("q", ""),
    }
    return render(request, "lumra_pages/marketing/discount.html", context)


@login_required
def add_discount_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/marketing/discount.html", context)


@login_required
def edit_discount_view(request, discount_id):
    context = {"discount_id": discount_id, "action": "edit"}
    return render(request, "lumra_pages/marketing/discount.html", context)


@login_required
def delete_discount_view(request, discount_id):
    if request.method != "POST":
        return render(request, "lumra_pages/marketing/discount.html", {"discount_id": discount_id})
    messages.warning(request, "Delete discount belum diimplementasi.")
    return redirect("discount_list")


# =====================================================
# LOYALTY PROGRAM MANAGEMENT
# =====================================================

@login_required
def loyalty_members_view(request):
    query = request.GET.get("q", "").strip()
    tier = request.GET.get("tier", "").strip()
    members_qs = Customer.objects.order_by("-loyalty_points", "name")
    if query:
        members_qs = members_qs.filter(Q(name__icontains=query) | Q(email__icontains=query))
    if tier:
        members_qs = members_qs.filter(tier=tier)
    paginator = Paginator(members_qs, 1000)
    page_obj = paginator.get_page(request.GET.get("page"))
    members = [
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "points": customer.loyalty_points,
            "tier": customer.tier,
            "join_date": customer.created_at,
            "status": "active" if customer.is_active else "inactive",
        }
        for customer in page_obj.object_list
    ]
    context = {
        "total_members":  Customer.objects.count(),
        "active_members": Customer.objects.filter(is_active=True).count(),
        "total_points_redeemed": 0,
        "avg_points": int(Customer.objects.aggregate(avg=Avg("loyalty_points"))["avg"] or 0),
        "members":        members,
        "page_obj":       page_obj,
        "is_paginated":   page_obj.has_other_pages(),
        "query":          query,
        "tier":           tier,
    }
    return render(request, "lumra_pages/marketing/loyalty_members.html", context)


@login_required
def add_loyalty_member_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/marketing/loyalty_members.html", context)


@login_required
def edit_loyalty_member_view(request, member_id):
    context = {"member_id": member_id, "action": "edit"}
    return render(request, "lumra_pages/marketing/loyalty_members.html", context)


@login_required
def delete_loyalty_member_view(request, member_id):
    if request.method != "POST":
        return render(request, "lumra_pages/marketing/loyalty_members.html", {"member_id": member_id})
    # TODO[C3-LONG]: 'financial_reports_view' = 206 baris (max 30). Pecah: financial_reports_view_validate(), financial_reports_view_query(), financial_reports_view_render()
    messages.warning(request, "Delete loyalty member belum diimplementasi.")
    return redirect("loyalty_members")


# =====================================================
# INSIGHTS & ANALYTICS
# =====================================================
 # TODO[C3-LONG]: 'financial_reports_view' terlalu panjang (207 baris). Pecah: financial_reports_view_validate(), financial_reports_view_build_context(), financial_reports_view_render()

@login_required
# TODO[C3-LONG]: 'financial_reports_view' = 210 baris (maks 30). Pecah: financial_reports_view_validate(), financial_reports_view_process(), financial_reports_view_respond()
def financial_reports_view(request):
    """
    Financial Reports — P&L dashboard:
      - KPI: Revenue, HPP, Gross Profit, Gross Margin %
      - Target vs Realisasi (dari SalesTarget)
      - Trend Revenue vs HPP per bulan
      - Naik/turun vs periode sebelumnya
      - Diskon: placeholder (belum ada di model)
    """
    from django.db.models.functions import TruncMonth
    from decimal import Decimal

    # ── Parse dates ──────────────────────────────────────────────
    today = datetime.today().date()
    default_start = today.replace(day=1)                          # awal bulan ini
    default_end   = today

    try:
        date_start = datetime.strptime(request.GET.get('date_start', ''), '%Y-%m-%d').date()
    except ValueError:
        date_start = default_start

    try:
        date_end = datetime.strptime(request.GET.get('date_end', ''), '%Y-%m-%d').date()
    except ValueError:
        date_end = default_end

    dt_start = datetime.combine(date_start, time.min)
    dt_end   = datetime.combine(date_end,   time.max)

    # ── Periode sebelumnya (untuk perbandingan naik/turun) ────────
    period_days  = (date_end - date_start).days + 1
    prev_end     = date_start - timedelta(days=1)
    prev_start   = prev_end   - timedelta(days=period_days - 1)
    dt_prev_start = datetime.combine(prev_start, time.min)
    dt_prev_end   = datetime.combine(prev_end,   time.max)

    # ── Helper: hitung revenue + HPP dari OrderItem queryset ──────
    def calc_financials(qs_orders):
        items = OrderItem.objects.filter(
            order__in=qs_orders,
            order__status='completed',
        ).select_related('variant')
        revenue = items.aggregate(
            rev=Sum(F('quantity') * F('price'), output_field=DecimalField())
        )['rev'] or Decimal('0')
        hpp = items.aggregate(
            hpp=Sum(F('quantity') * F('variant__price_buy'), output_field=DecimalField())
        )['hpp'] or Decimal('0')
        order_count = qs_orders.filter(status='completed').count()
        return revenue, hpp, order_count

    # ── Data periode ini ──────────────────────────────────────────
    orders_now  = Order.objects.filter(created_at__range=(dt_start, dt_end))
    revenue, hpp, order_count = calc_financials(orders_now)
    gross_profit = revenue - hpp
    gross_margin = round(gross_profit / revenue * 100, 1) if revenue else Decimal('0')

    # ── Data periode sebelumnya ───────────────────────────────────
    orders_prev = Order.objects.filter(created_at__range=(dt_prev_start, dt_prev_end))
    rev_prev, hpp_prev, _ = calc_financials(orders_prev)
    profit_prev = rev_prev - hpp_prev

    def pct_change(now, prev):
        if not prev:
            return None
        return round((now - prev) / prev * 100, 1)

    rev_change    = pct_change(revenue, rev_prev)
    profit_change = pct_change(gross_profit, profit_prev)
    margin_prev   = round(profit_prev / rev_prev * 100, 1) if rev_prev else Decimal('0')
    margin_change = pct_change(gross_margin, margin_prev)

    # ── Target bulan ini (dari SalesTarget) ───────────────────────
    months_in_range = set()
    cursor = date_start.replace(day=1)
    while cursor <= date_end:
        months_in_range.add((cursor.year, cursor.month))
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)

    targets = SalesTarget.objects.filter(
        year__in=[y for y, m in months_in_range],
        month__in=[m for y, m in months_in_range],
    )
    target_map = {(t.year, t.month): t.target_amount for t in targets}

    total_target = sum(
        target_map.get(ym, Decimal('0')) for ym in months_in_range
    )
    target_pct = round(revenue / total_target * 100, 1) if total_target else None

    # ── Monthly trend (Revenue vs HPP per bulan) ──────────────────
    monthly_items = OrderItem.objects.filter(
        order__created_at__range=(dt_start, dt_end),
        order__status='completed',
    ).annotate(
        month=TruncMonth('order__created_at')
    ).values('month').annotate(
        revenue=Sum(F('quantity') * F('price'),         output_field=DecimalField()),
        hpp    =Sum(F('quantity') * F('variant__price_buy'), output_field=DecimalField()),
    ).order_by('month')

    trend_labels  = []
    trend_revenue = []
    trend_hpp     = []
    trend_profit  = []

    MONTH_ID = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

    for row in monthly_items:
        m = row['month']
        lbl = f"{MONTH_ID[m.month]} {m.year}"
        rev = float(row['revenue'] or 0)
        h   = float(row['hpp']     or 0)
        trend_labels.append(lbl)
        trend_revenue.append(rev)
        trend_hpp.append(h)
        trend_profit.append(round(rev - h, 2))

    # ── Target vs Realisasi per bulan (untuk chart bar) ───────────
    target_bars = []
    for ym in sorted(months_in_range):
        y, m = ym
        lbl = f"{MONTH_ID[m]} {y}"
        tgt = float(target_map.get(ym, 0))
        # cari revenue bulan itu dari trend
        rev_month = 0
        for i, row in enumerate(monthly_items):
            if row['month'].year == y and row['month'].month == m:
                rev_month = float(row['revenue'] or 0)
                break
        pct = round(rev_month / tgt * 100, 1) if tgt else None
        status = 'achieved' if pct and pct >= 100 else \
                 'on_track' if pct and pct >= 70  else \
                 'behind'   if pct                else 'no_target'
        target_bars.append({
            'label'    : lbl,
            'target'   : tgt,
            'realisasi': rev_month,
            'pct'      : pct,
            'status'   : status,
        })

    # ── Avg daily revenue (untuk ekspektasi) ─────────────────────
    avg_daily = float(revenue) / period_days if period_days else 0

    # Proyeksi akhir bulan (kalau periode ini < 1 bulan penuh)
    days_in_month = 30
    expected_monthly = avg_daily * days_in_month

    # ── Presets untuk date filter ──────────────────────────────────
    presets = [
        ('Bulan Ini', 0),
        ('30 Hari',  30),
        ('90 Hari',  90),
        ('Tahun Ini', -1),
    ]

    context = {
        'date_start': date_start.strftime('%Y-%m-%d'),
        'date_end'  : date_end.strftime('%Y-%m-%d'),

        # KPI cards
        'revenue'       : revenue,
        'hpp'           : hpp,
        'gross_profit'  : gross_profit,
        'gross_margin'  : gross_margin,
        'order_count'   : order_count,
        'avg_order_value': round(revenue / order_count, 2) if order_count else 0,

        # Perbandingan periode
        'rev_change'    : rev_change,
        'profit_change' : profit_change,
        'margin_change' : margin_change,
        'rev_prev'      : rev_prev,
        'profit_prev'   : profit_prev,

        # Target
        'total_target'  : total_target,
        'target_pct'    : target_pct,

        # Proyeksi
        'avg_daily'     : round(avg_daily, 0),
        'expected_monthly': round(expected_monthly, 0),
        'period_days'   : period_days,

        # Trend chart data (JSON)
        'trend_labels_json' : json.dumps(trend_labels),
        'trend_revenue_json': json.dumps(trend_revenue),
        'trend_hpp_json'    : json.dumps(trend_hpp),
        'trend_profit_json' : json.dumps(trend_profit),

        # Target bars
        'target_bars'       : target_bars,
        'target_bars_json'  : json.dumps(target_bars),
 # TODO[C3-LONG]: 'market_insights_view' = 295 baris (max 30). Pecah: market_insights_view_validate(), market_insights_view_query(), market_insights_view_render()

        # Misc
        'presets'      : presets,
        'current_year' : today.year,
        'current_month': today.month,
    }
    return render(request, 'lumra_pages/sales_insight/financial_reports.html', context)

 # TODO[C3-LONG]: 'market_insights_view' terlalu panjang (298 baris). Pecah: market_insights_view_validate(), market_insights_view_build_context(), market_insights_view_render()

@login_required
# TODO[C3-LONG]: 'market_insights_view' = 230 baris (maks 30). Pecah: market_insights_view_validate(), market_insights_view_process(), market_insights_view_respond()
def market_insights_view(request):
    """
    Market Insights — 3 sections:
    1. Peak Hours & Waktu (heatmap jam × hari, jam tersibuk, hari terbaik)
    2. Customer Behavior (pertumbuhan, churn risk, frekuensi, tier)
    3. Product Intelligence (top laris, margin, slow-moving)
    """
    from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay
    from django.db.models import Avg, Max, Min, Count, DecimalField, F, Sum, Q
    from lumra_config.models import Customer, ProductVariant, Product
    from decimal import Decimal

    today = timezone.now().date()

    # ── Parse dates ──────────────────────────────────────────────
    try:
        date_start = datetime.strptime(request.GET.get('date_start', ''), '%Y-%m-%d').date()
    except ValueError:
        date_start = today - timedelta(days=29)

    try:
        date_end = datetime.strptime(request.GET.get('date_end', ''), '%Y-%m-%d').date()
    except ValueError:
        date_end = today

    dt_start = timezone.make_aware(datetime.combine(date_start, time.min))
    dt_end   = timezone.make_aware(datetime.combine(date_end,   time.max))

    period_days = (date_end - date_start).days + 1

    # ── Base order queryset ───────────────────────────────────────
    orders_qs = Order.objects.filter(
        created_at__range=(dt_start, dt_end),
        status='completed',
    )
    has_data = orders_qs.exists()

    # ════════════════════════════════════════════════════
    # SECTION 1 — PEAK HOURS & WAKTU
    # ════════════════════════════════════════════════════

    # Transaksi per jam (0-23)
    hourly = (
        orders_qs
        .annotate(hour=ExtractHour('created_at'))
        .values('hour')
        .annotate(count=Count('id'), revenue=Sum(
            F('items__quantity') * F('items__price'),
            output_field=DecimalField()
        ))
        .order_by('hour')
    )

    hour_counts  = [0] * 24
    hour_revenue = [0.0] * 24
    for row in hourly:
        h = row['hour']
        if 0 <= h < 24:
            hour_counts[h]  = row['count']
            hour_revenue[h] = float(row['revenue'] or 0)

    peak_hour = hour_counts.index(max(hour_counts)) if any(hour_counts) else None
    peak_hour_count = max(hour_counts) if any(hour_counts) else 0

    # Transaksi per hari (1=Minggu, 2=Senin... 7=Sabtu di Django ExtractWeekDay)
    DAY_NAMES = ['', 'Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab']
    DAY_FULL  = ['', 'Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']

    daily_pattern = (
        orders_qs
        .annotate(weekday=ExtractWeekDay('created_at'))
        .values('weekday')
        .annotate(count=Count('id'), revenue=Sum(
            F('items__quantity') * F('items__price'),
            output_field=DecimalField()
        ))
        .order_by('weekday')
    )

    day_counts  = [0] * 8   # index 1-7
    day_revenue = [0.0] * 8
    for row in daily_pattern:
        data_dict = row['weekday']
        if 1 <= d <= 7:
            day_counts[d]  = row['count']
            day_revenue[d] = float(row['revenue'] or 0)

    best_day_idx = day_counts.index(max(day_counts[1:], default=0)) if any(day_counts[1:]) else None
    best_day_name = DAY_FULL[best_day_idx] if best_day_idx else None

    # Heatmap data: jam × hari (untuk JS grid)
    heatmap_raw = (
        orders_qs
        .annotate(hour=ExtractHour('created_at'), weekday=ExtractWeekDay('created_at'))
        .values('hour', 'weekday')
        .annotate(count=Count('id'))
    )
    heatmap = {}
    for row in heatmap_raw:
        heatmap[f"{row['weekday']}-{row['hour']}"] = row['count']
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan Model.objects.select_related('...').prefetch_related('...')

    # ════════════════════════════════════════════════════
    # SECTION 2 — CUSTOMER BEHAVIOR
    # ════════════════════════════════════════════════════

    total_customers = Customer.objects.filter(is_active=True).count()

    # Pertumbuhan customer baru per bulan (6 bulan terakhir)
    six_months_ago = today.replace(day=1) - timedelta(days=5*30)
    growth_qs = (
        Customer.objects
        .filter(created_at__date__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(new_count=Count('id'))
        .order_by('month')
    )
    MONTH_ID = ['','Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']
    growth_labels = []
    growth_data   = []
    for row in growth_qs:
        m = row['month']
        growth_labels.append(f"{MONTH_ID[m.month]} {m.year}")
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan Model.objects.select_related('...').prefetch_related('...')
        growth_data.append(row['new_count'])

    # Churn risk — customer yang tidak order > 30 hari
    churn_threshold = today - timedelta(days=30)
    churn_count = Customer.objects.filter(
        is_active=True,
        last_order_date__isnull=False,
        last_order_date__date__lt=churn_threshold,
    ).count()
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan Model.objects.select_related('...').prefetch_related('...')
    churn_pct = round(churn_count / total_customers * 100, 1) if total_customers else 0

    # Customer belum pernah order sama sekali
    never_ordered = Customer.objects.filter(
        is_active=True,
        last_order_date__isnull=True,
    ).count()

    # Frekuensi kunjungan rata-rata (orders per customer dalam periode)
    active_customers_in_period = (
        orders_qs
        .filter(customer__isnull=False)
        .values('customer_id')
        .annotate(order_count=Count('id'))
    )
    if active_customers_in_period.exists():
        avg_frequency = round(
            sum(r['order_count'] for r in active_customers_in_period) /
            active_customers_in_period.count(), 1
        )
        max_frequency = max(r['order_count'] for r in active_customers_in_period)
    else:
        avg_frequency = 0
        max_frequency = 0

    # Tier distribution
    tier_dist = (
        Customer.objects
        .filter(is_active=True)
        .values('tier')
        .annotate(count=Count('id'))
        .order_by('-count')
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    )
    tier_labels_list = []
    tier_counts_list = []
    TIER_COLOR = {
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        'platinum': '#6366f1',
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        'gold'    : '#f59e0b',
        'silver'  : '#94a3b8',
        'bronze'  : '#92400e',
    }
    for t in tier_dist:
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
        tier_labels_list.append((t['tier'] or 'bronze').capitalize())
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan Model.objects.select_related('...').prefetch_related('...')
        tier_counts_list.append(t['count'])

    # Top spending customers
    top_spenders = Customer.objects.filter(
        is_active=True, total_orders__gt=0
    ).order_by('-total_spent')[:5]

    # ════════════════════════════════════════════════════
    # SECTION 3 — PRODUCT INTELLIGENCE
    # ════════════════════════════════════════════════════

    # Top 10 produk terlaris dalam periode
    top_products = (
        OrderItem.objects
        .filter(order__in=orders_qs)
        .values('variant__product__name', 'variant__product_id')
        .annotate(
            qty_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('price'), output_field=DecimalField()),
        )
        .order_by('-qty_sold')[:10]
    )
    top_products_list = [
        {
            'name'   : r['variant__product__name'],
            'qty'    : r['qty_sold'],
            'revenue': float(r['revenue'] or 0),
        }
        for r in top_products
    ]

    # Margin per produk (price_sell - price_buy) / price_sell × 100
    margin_products = (
    ProductVariant.objects
    .select_related('product')
    .filter(price_sell__gt=0, price_buy__gt=0)
    .annotate(
        margin_pct=(
            (F('price_sell') - F('price_buy')) * 100 / F('price_sell')
        )
    )
    .order_by('-margin_pct')[:10]
)
    margin_list = [
        {
            'name'      : v.product.name,
            'sku'       : v.sku,
            'price_sell': float(v.price_sell),
            'price_buy' : float(v.price_buy),
            'margin_pct': round(float((v.price_sell - v.price_buy) / v.price_sell * 100), 1),
        }
        for value_item in margin_products
    ]

    # Slow-moving — produk yang tidak terjual dalam periode tapi punya stok
    sold_product_ids = set(
        OrderItem.objects
        .filter(order__in=orders_qs)
        .values_list('variant__product_id', flat=True)
        .distinct()
    )
    slow_moving = (
        Product.objects
        .exclude(id__in=sold_product_ids)
        .filter(variants__isnull=False)
        .distinct()
        .order_by('name')[:10]
    )
    slow_moving_list = [
        {'name': p.name, 'id': p.id}
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        for page_obj in slow_moving
    ]

    # ── Presets ───────────────────────────────────────────────────
    presets = [
        ('7 Hari',   7),
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        ('30 Hari',  30),
        ('90 Hari',  90),
        ('Tahun Ini', -1),
    ]

    context = {
        'date_start' : date_start.strftime('%Y-%m-%d'),
        'date_end'   : date_end.strftime('%Y-%m-%d'),
        'period_days': period_days,
        'has_data'   : has_data,
        'presets'    : presets,

        # Section 1 — Peak hours
        'hour_counts_json'  : json.dumps(hour_counts),
        'hour_revenue_json' : json.dumps(hour_revenue),
        'day_counts_json'   : json.dumps(day_counts[1:]),   # index 1-7 → list 7 item
        'day_revenue_json'  : json.dumps(day_revenue[1:]),
        'day_names_json'    : json.dumps(DAY_NAMES[1:]),
        'heatmap_json'      : json.dumps(heatmap),
        'peak_hour'         : peak_hour,
        'peak_hour_count'   : peak_hour_count,
        'best_day_name'     : best_day_name,

        # Section 2 — Customer behavior
        'total_customers'   : total_customers,
        'churn_count'       : churn_count,
        'churn_pct'         : churn_pct,
        'never_ordered'     : never_ordered,
        'avg_frequency'     : avg_frequency,
        'max_frequency'     : max_frequency,
        'growth_labels_json': json.dumps(growth_labels),
        'growth_data_json'  : json.dumps(growth_data),
        'tier_labels_json'  : json.dumps(tier_labels_list),
        'tier_counts_json'  : json.dumps(tier_counts_list),
        'top_spenders'      : top_spenders,

        # Section 3 — Product intelligence
        'top_products_json' : json.dumps(top_products_list),
        'margin_list_json'  : json.dumps(margin_list),
        'slow_moving_list'  : slow_moving_list,
        'top_products_count': len(top_products_list),
        'slow_moving_count' : len(slow_moving_list),
    }
    return render(request, 'lumra_pages/sales_insight/market_insights.html', context)


@login_required
def trends_analysis_view(request):
    context = {"trends": {}}
    return render(request, "lumra_pages/sales_insight/trends_analysis.html", context)


@login_required
def activity_log_view(request):
    context = {"activities": []}
    return render(request, "lumra_pages/reports/activity_log.html", context)


# =====================================================
# SYSTEM & SETTINGS
# =====================================================

@login_required
def users_view(request):
    """Manajemen pengguna — staff/admin only."""
    # FIX: gunakan redirect ke 403 page, bukan render langsung (status code tetap 200 di versi lama)
    if not request.user.is_staff:
        return render(request, "lumra_pages/etc/error_403.html", status=403)

    # FIX: pindahkan import ke atas file — import di dalam fungsi hanya untuk menghindari circular import
    users = User.objects.select_related("userprofile").order_by("username")
    context = {"users": users}
    return render(request, "lumra_pages/settings/users.html", context)


@login_required
def profile_view(request):
    """User profile page."""
    # FIX: get_or_create untuk menghindari RelatedObjectDoesNotExist jika profile belum ada
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    context = {"user_profile": profile}
    return render(request, "lumra_pages/settings/profile.html", context)


@login_required
def settings_view(request):
    return render(request, "lumra_pages/settings/settings.html")


@login_required
def system_status_view(request):
    context = {"status": {}}
    return render(request, "lumra_pages/settings/system_status.html", context)


@login_required
def business_settings_view(request):
    # the template expects several JSON blobs for Alpine;
    # provide empty defaults so the page still loads even if no data yet
    context = {
        "settings": {},
        "settings_json": "{}",
        "audit_json": "{}",
        "outlets_json": "[]",
    }

    # attach permissions so the template and its JS know whether the
    # current user is allowed to access / modify anything on this page.
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)

    return render(request, "lumra_pages/settings/business_settings.html", context)


# ---  Business sub‑pages -------------------------------------------------

@login_required
def business_feature_matrix_view(request):
    """Blank endpoint for the feature‑matrix page.

    The ability to view or edit the feature matrix is controlled by the same
    ``sys_config`` permission used by the main settings screen.  Passing the
    permissions object into the template allows the frontend to make
    decisions such as disabling the save button or hiding the upgrade banner
    entirely for unauthorized users.
    """
    context = {"features_json": "[]"}
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)
    return render(request, "lumra_pages/settings/business_feature_matrix.html", context)


@login_required
def business_form_general_view(request):
    """Company profile form page.

    Access restricted by ``sys_config`` permission; unauthorized users will
    see a simple notice instead of the editable form.  We still send a
    minimal JSON payload so the Alpine component is safe to initialize.
    """
    context = {"profile_json": "{}"}
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)
    return render(request, "lumra_pages/settings/business_form_general.html", context)


@login_required
def user_roles_permissions_view(request):
    """Simple placeholder for roles & permissions screen."""
    context = {"roles_json": "[]", "perms_json": "[]"}
    return render(request, "lumra_pages/settings/user_roles_permissions.html", context)

# =====================================================
# EXPORT & DOWNLOAD
# =====================================================

VALID_REPORT_TYPES = {"sales", "inventory", "financial", "movement"}
VALID_TREND_TYPES  = {"weekly", "monthly", "quarterly", "yearly"}


@login_required
def download_report_view(request, report_type):
    # FIX: validasi report_type — sebelumnya semua string diterima dan dirender begitu saja
    if report_type not in VALID_REPORT_TYPES:
        raise Http404(f"Report type '{report_type}' tidak dikenal.")
    context = {"report_type": report_type}
    return render(request, "lumra_pages/sales_insight/market_insights.html", context)


@login_required
def export_trends_view(request, trend_type):
    # FIX: validasi trend_type
    if trend_type not in VALID_TREND_TYPES:
        raise Http404(f"Trend type '{trend_type}' tidak dikenal.")
    context = {"trend_type": trend_type}
    return render(request, "lumra_pages/sales_insight/trends_analysis.html", context)


# =====================================================
# PUBLIC PAGES
# =====================================================

def about_view(request):
    context = {
        "founded_year": 2024,
        "clients_count": 100,
    }
    return render(request, "lumra_pages/settings/about.html", context)


def contact_view(request):
    return render(request, "lumra_pages/settings/contact.html", {})


def search_view(request):
    query = request.GET.get("q", "").strip()
    context = {"query": query}
    return render(request, "lumra_pages/settings/search.html", context)
