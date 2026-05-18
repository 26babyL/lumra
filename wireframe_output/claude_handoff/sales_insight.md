# Claude Handoff: sales_insight

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 7
Jumlah view terkait: 10

## Template Scope

### lumra_pages/sales_insight/dashboard.html
- File: `lumra_config/templates/lumra_pages/sales_insight/dashboard.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=90, interactive=16, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ SECTION ]: Home / Sales Insight / Dashboard Quick Actions Akses cepat untuk operasional har…
  - BREADCRUMB: Home / Sales Insight / Dashboard
  - BREADCRUMB: /
  - BREADCRUMB: /
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H2): Akses cepat untuk operasional hari ini
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales_insight/trends_analysis.html
- File: `lumra_config/templates/lumra_pages/sales_insight/trends_analysis.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=30, interactive=3, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 📈 Trends Analysis
  - [ FORM ]: Last 7 Days Last 30 Days Last 90 Days Last Year All Categories Coffee Non-Coffee…
  - INPUT [select] period: period
  - INPUT [select] category: category
  - BUTTON: 🔄 Update: 🔄 Update
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/sales_insight/pos.html
- File: `lumra_config/templates/lumra_pages/sales_insight/pos.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=77, interactive=21, issues=1, scroll_nesting=0
- Routes: `pos/` (pos)
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ HEADER ]: Point of Sale Kasir aktif —
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Point of Sale
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales_insight/market_insights.html
- File: `lumra_config/templates/lumra_pages/sales_insight/market_insights.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=100, interactive=5, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Market Insights
  - HEADING (H1): Market Insights
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ FORM ]: {{ date_start }} → {{ date_end }} {% for label, days in presets %} {{ label }} {…
  - CALENDAR: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales_insight/sales_intelligence.html
- File: `lumra_config/templates/lumra_pages/sales_insight/sales_intelligence.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=71, interactive=21, issues=1, scroll_nesting=0
- Routes: `history/` (sales_history)
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Sales & Insights / Sales History
  - HEADING (H1): Sales History
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BADGE / STATUS: {{ anomaly_count }} anomali
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Export: Export
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales_insight/financial_reports.html
- File: `lumra_config/templates/lumra_pages/sales_insight/financial_reports.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=95, interactive=6, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Financial Reports
  - HEADING (H1): Financial Reports
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Print: Print
  - [ FORM ]: {{ date_start }} → {{ date_end }} {% for label, days in presets %} {{ label }} {…
  - CALENDAR: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales_insight/sales_performance.html
- File: `lumra_config/templates/lumra_pages/sales_insight/sales_performance.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=87, interactive=20, issues=1, scroll_nesting=0
- Routes: `performance/` (sales_performance)
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Revenue {{ total_revenue|rupiah }} {{ date_start }} → {{ date_end }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Transaksi {{ total_orders }} Orders
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Order {{ avg_order_value|rupiah }} Per transaksi
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### dashboard_view
- File: `lumra_config/views/dashboard_views.py`:457
- Decorators: `login_required`
- Context keys eksplisit: `dashboard_data`, `kpis`, `notifications`, `notifications_count`, `quick_stats`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
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

    return render(request, "lumra_pages/sales_insight/dashboard.html", {
        "kpis":                kpis,
        "quick_stats":         quick_stats,
        "dashboard_data":      dashboard_data,
        "notifications_count": notifications_count,
        "notifications":       notifications,
    })
```

### pos_view
- File: `lumra_config/views/misc_views.py`:185
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
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
```

### sales_history_view
- File: `lumra_config/views/misc_views.py`:415
- Decorators: `login_required`, `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### sales_performance_view
- File: `lumra_config/views/misc_views.py`:810
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### financial_reports_view
- File: `lumra_config/views/misc_views.py`:1169
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### market_insights_view
- File: `lumra_config/views/misc_views.py`:1493
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### trends_analysis_view
- File: `lumra_config/views/misc_views.py`:1499
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def trends_analysis_view(request):
    context = {"trends": {}}
    return render(request, "lumra_pages/sales_insight/trends_analysis.html", context)
```

### download_report_view
- File: `lumra_config/views/misc_views.py`:1619
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def download_report_view(request, report_type):
    # FIX: validasi report_type — sebelumnya semua string diterima dan dirender begitu saja
    if report_type not in VALID_REPORT_TYPES:
        raise Http404(f"Report type '{report_type}' tidak dikenal.")
    context = {"report_type": report_type}
    return render(request, "lumra_pages/sales_insight/market_insights.html", context)
```

### export_trends_view
- File: `lumra_config/views/misc_views.py`:1628
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def export_trends_view(request, trend_type):
    # FIX: validasi trend_type
    if trend_type not in VALID_TREND_TYPES:
        raise Http404(f"Trend type '{trend_type}' tidak dikenal.")
    context = {"trend_type": trend_type}
    return render(request, "lumra_pages/sales_insight/trends_analysis.html", context)
```

### pos_view
- File: `lumra_config/views/sales_views.py`:40
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def pos_view(request):
    """Point of Sale interface - main POS page with cart and products."""
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    # Placeholder: In production, fetch from database
    products_json = json.dumps([], cls=DjangoJSONEncoder)
    categories_json = json.dumps([], cls=DjangoJSONEncoder)
    customers_json = json.dumps([], cls=DjangoJSONEncoder)
    discounts_json = json.dumps([], cls=DjangoJSONEncoder)
    payment_methods_json = json.dumps([
        {'code': 'cash', 'name': 'Cash'},
        {'code': 'card', 'name': 'Kartu Kredit'},
        {'code': 'transfer', 'name': 'Transfer Bank'},
    ], cls=DjangoJSONEncoder)
    
    context = {
        'products_json': products_json,
        'categories_json': categories_json,
        'customers_json': customers_json,
        'discounts_json': discounts_json,
        'payment_methods_json': payment_methods_json,
    }
    return render(request, 'lumra_pages/sales_insight/pos.html', context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
