# Claude Handoff: master_data

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 24
Jumlah view terkait: 40

## Template Scope

### lumra_pages/master_data/bank_accounts.html
- File: `lumra_config/templates/lumra_pages/master_data/bank_accounts.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ page_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Cari...: Cari...
  - BUTTON: [icon]: 
  - SEARCH BAR: 

### lumra_pages/master_data/customer.html
- File: `lumra_config/templates/lumra_pages/master_data/customer.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=0, interactive=0, issues=0, scroll_nesting=0

### lumra_pages/master_data/location_list.html
- File: `lumra_config/templates/lumra_pages/master_data/location_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=83, interactive=18, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / {% trans "Locations" %}
  - HEADING (H1): {% trans "Locations" %}
  - BUTTON: {% trans "Add Location" %}: {% trans "Add Location" %}
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: {% trans "Total" %} {% trans "All outlets" %}
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/payment_terms_list.html
- File: `lumra_config/templates/lumra_pages/master_data/payment_terms_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ page_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Cari...: Cari...
  - BUTTON: [icon]: 
  - SEARCH BAR: 

### lumra_pages/master_data/reason_codes.html
- File: `lumra_config/templates/lumra_pages/master_data/reason_codes.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ page_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Cari...: Cari...
  - BUTTON: [icon]: 
  - SEARCH BAR: 

### lumra_pages/master_data/stock_opname.html
- File: `lumra_config/templates/lumra_pages/master_data/stock_opname.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=59, interactive=18, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {# ── HEADER ────────────────────────────────────────────…
  - ALPINE COMPONENT [stockOpname()]: {# ── HEADER ───────────────────────────────────────────────…
  - [ NAVIGATION BAR ]: Dashboard / Stock Opname /
  - [ ORDERED LIST ]: Dashboard / Stock Opname /
  - HEADING (H1): Stock Opname
  - [ SECTION ]: Pilih Lokasi untuk Opname {% for loc in locations %} '|cut:''|default:loc.name|e…
  - HEADING (H2): Pilih Lokasi untuk Opname
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/tags_list.html
- File: `lumra_config/templates/lumra_pages/master_data/tags_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ page_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Cari...: Cari...
  - BUTTON: [icon]: 
  - SEARCH BAR: 

### lumra_pages/master_data/tax_list.html
- File: `lumra_config/templates/lumra_pages/master_data/tax_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ page_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Cari...: Cari...
  - BUTTON: [icon]: 
  - SEARCH BAR: 

### lumra_pages/master_data/vendor_list.html
- File: `lumra_config/templates/lumra_pages/master_data/vendor_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=69, interactive=11, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {{ vendors_json|json_script:"vendors-data" }} Dashboard /…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Vendors
  - HEADING (H1): Partner Vendors
  - BUTTON: Tambah Vendor: Tambah Vendor
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/bank_account_form.html
- File: `lumra_config/templates/lumra_pages/master_data/bank_account_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/master_data/category_form.html
- File: `lumra_config/templates/lumra_pages/master_data/category_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=21, interactive=8, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Categories / {% if is_edit %}Edit{% else %}Tambah{% endif %}
  - HEADING (H1): {% if is_edit %}Edit{% else %}Tambah{% endif %} Kategori
  - CARD: Preview
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BADGE / STATUS: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ FORM ]: {% csrf_token %} Nama Kategori * Slug (URL) — otomatis Deskripsi (opsional) Warn…
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/customer_form.html
- File: `lumra_config/templates/lumra_pages/master_data/customer_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=26, interactive=13, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [customerForm()]: Dashboard / Pelanggan / {% if form.instance.pk %}Edit{% else…
  - [ NAVIGATION BAR ]: Dashboard / Pelanggan / {% if form.instance.pk %}Edit{% else %}Tambah Baru{% end…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {% if form.instance.pk %}Edit Pelanggan{% else %}Tambah Pelanggan Baru{% endif %}
  - [ FORM ]: {% csrf_token %} Identitas Pelanggan Nama Lengkap * {% for err in form.name.erro…
  - CARD: Identitas Pelanggan Nama Lengkap * {% for err in form.name.errors %} {{ err }} {…
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - INPUT [text] Nama lengkap pelanggan: Nama lengkap pelanggan
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/customers.html
- File: `lumra_config/templates/lumra_pages/master_data/customers.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=64, interactive=14, issues=1, scroll_nesting=0
- Routes: `customers/` (customers), `customers/add/` (add_customer), `customers/<int:customer_id>/` (view_customer), `customers/<int:customer_id>/edit/` (edit_customer), `customers/<int:customer_id>/delete/` (delete_customer)
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Total Pelanggan {{ total_customers|default:0 }} Registered
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Member Gold {{ gold_count|default:0 }} ⭐ Gold Tier
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Member VIP {{ vip_count|default:0 }} 👑 VIP Tier
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/payment_terms_form.html
- File: `lumra_config/templates/lumra_pages/master_data/payment_terms_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/master_data/stock_opname_session_detail.html
- File: `lumra_config/templates/lumra_pages/master_data/stock_opname_session_detail.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=24, interactive=6, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {# ── HEADER ────────────────────────────────────────────…
  - ALPINE COMPONENT [approvalDetail()]: {# ── HEADER ───────────────────────────────────────────────…
  - [ NAVIGATION BAR ]: Dashboard / Approvals / {{ approval.location.name }}
  - [ ORDERED LIST ]: Dashboard / Approvals / {{ approval.location.name }}
  - HEADING (H1): Approval Detail — {{ approval.location.name }}
  - HEADING (H2): Ringkasan Approval
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/tax_form.html
- File: `lumra_config/templates/lumra_pages/master_data/tax_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/master_data/unit_form.html
- File: `lumra_config/templates/lumra_pages/master_data/unit_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=39, interactive=6, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Units / {% if is_edit %}Edit{% else %}Tambah{% endif %}
  - HEADING (H1): {% if is_edit %}Edit{% else %}Tambah{% endif %} Satuan
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: {% csrf_token %} {# §1 — Group Picker #} Kategori Satuan * {# §2 — Name + Symbol…
  - [ FORM ]: {% csrf_token %} {# §1 — Group Picker #} Kategori Satuan * {# §2 — Name + Symbol…
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/categories_list.html
- File: `lumra_config/templates/lumra_pages/master_data/categories_list.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=43, interactive=9, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {{ categories_json|json_script:"categories-data" }} Dashb…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Categories
  - HEADING (H1): Product Categories
  - BUTTON (Primary): Tambah Kategori
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/customer_detail.html
- File: `lumra_config/templates/lumra_pages/master_data/customer_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=66, interactive=7, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Pelanggan / {{ customer.name }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: {{ customer.name|slice:":2"|upper }} {% if customer.tier == 'vip' %}👑{% elif cus…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/customers_list.html
- File: `lumra_config/templates/lumra_pages/master_data/customers_list.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=64, interactive=14, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Total Pelanggan {{ total_customers|default:0 }} Registered
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Member Gold {{ gold_count|default:0 }} ⭐ Gold Tier
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Member VIP {{ vip_count|default:0 }} 👑 VIP Tier
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/locations.html
- File: `lumra_config/templates/lumra_pages/master_data/locations.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=83, interactive=18, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / {% trans "Locations" %}
  - HEADING (H1): {% trans "Locations" %}
  - BUTTON: {% trans "Add Location" %}: {% trans "Add Location" %}
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: {% trans "Total" %} {% trans "All outlets" %}
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/units_list.html
- File: `lumra_config/templates/lumra_pages/master_data/units_list.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=70, interactive=20, issues=3, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Units
  - HEADING (H1): Units — Satuan Ukur
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
  - BUTTON: [icon]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class=''
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='' class='w-3.5 h-3.5 accent-emerald-500 rounded cursor-poin'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/vendor_form.html
- File: `lumra_config/templates/lumra_pages/master_data/vendor_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=64, interactive=6, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Kembali: Kembali
  - [ NAVIGATION BAR ]: Dashboard / Vendors / {{ vendor.name }}
  - HERO / BANNER: {{ vendor.name|slice:":2"|upper }} {{ vendor.code|default:"VND-000" }} {% if ven…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/master_data/vendors_list.html
- File: `lumra_config/templates/lumra_pages/master_data/vendors_list.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=69, interactive=11, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {{ vendors_json|json_script:"vendors-data" }} Dashboard /…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Vendors
  - HEADING (H1): Partner Vendors
  - BUTTON: Tambah Vendor: Tambah Vendor
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### customer_list
- File: `lumra_config/views/customer_views.py`:131
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def customer_list(request):
    q = request.GET.get('search', '').strip()
    tier = request.GET.get('tier')
    sort_by = request.GET.get('sort_by', 'created_at')
    order = request.GET.get('order', 'desc')

    qs = Customer.objects.order_by('-created_at')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    if tier:
        if tier == 'regular':
            qs = qs.exclude(tier__in=['silver', 'gold', 'platinum', 'vip'])
        else:
            qs = qs.filter(tier=tier)

    # sort mapping for a few custom keys
    if sort_by in ('points', 'lifetime_value', 'name', 'last_visit', 'created_at'):
        mapping = {
            'points': 'loyalty_points',
            'lifetime_value': 'total_spent',
            'last_visit': 'last_order_date',
        }
        field = mapping.get(sort_by, sort_by)
        if order == 'desc':
            field = '-' + field
        qs = qs.order_by(field)

    # summary stats used by the KPI cards
    total_customers = qs.count()
    gold_count = qs.filter(tier='gold').count()
    vip_count = qs.filter(tier='vip').count()
    total_points = qs.aggregate(Sum('loyalty_points'))['loyalty_points__sum'] or 0
    birthday_this_month = 0  # model has no birth_date yet

    # handle export (csv only for now)
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'WhatsApp/Phone', 'Tier', 'Points'])
        for c in qs:
            writer.writerow([c.name, c.email, c.phone or '', c.tier, c.loyalty_points])
        return response

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    customers = list(page_obj.object_list)
    for c in customers:
        _augment_customer(c)

    context = {
        'customers': customers,
        'page_obj': page_obj,
        'query': q,
        'report_title': 'Customers',
        'is_empty': False,
        'tier_choices': _tier_choices(),
        'total_customers': total_customers,
        'gold_count': gold_count,
        'vip_count': vip_count,
        'total_points': total_points,
        'birthday_this_month': birthday_this_month,
    }
    return render(request, 'lumra_pages/master_data/customers_list.html', context)
```

### customer_detail
- File: `lumra_config/views/customer_views.py`:160
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def customer_detail(request, pk):
    cust = get_object_or_404(Customer, pk=pk)
    _augment_customer(cust)

    # transactions from OrderItem similar to sales_report
    transactions = OrderItem.objects.filter(order__customer=cust).select_related(
        'order', 'variant', 'variant__product'
    )

    total_earned_points = sum(getattr(tx, 'points_earned', 0) or 0 for tx in transactions)

    # no persistent log table yet; return empty list
    point_logs = []

    context = {
        'customer': cust,
        'transactions': transactions,
        'total_earned_points': total_earned_points,
        'point_logs': point_logs,
        'report_title': 'Customer Detail',
        'is_empty': False,
        'tier_choices': _tier_choices(),
    }
    return render(request, 'lumra_pages/master_data/customer_detail.html', context)
```

### customer_create
- File: `lumra_config/views/customer_views.py`:178
- Decorators: `login_required`
- Context keys eksplisit: `form`, `tier_choices`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.phone = form.cleaned_data.get('whatsapp', '')
            c.loyalty_points = form.cleaned_data.get('initial_points') or 0
            c.save()
            messages.success(request, f"Customer '{c.name}' dibuat.")
            return redirect('customer_detail', c.pk)
    else:
        form = CustomerForm()
    return render(request, 'lumra_pages/master_data/customer_form.html', {
        'form': form,
        'tier_choices': _tier_choices(),
    })
```

### customer_update
- File: `lumra_config/views/customer_views.py`:201
- Decorators: `login_required`
- Context keys eksplisit: `form`, `tier_choices`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def customer_update(request, pk):
    c = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=c)
        if form.is_valid():
            c = form.save(commit=False)
            c.phone = form.cleaned_data.get('whatsapp', '')
            c.save()
            messages.success(request, f"Customer '{c.name}' diperbarui.")
            return redirect('customer_detail', c.pk)
    else:
        initial = {'whatsapp': c.phone}
        form = CustomerForm(instance=c, initial=initial)
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    return render(request, 'lumra_pages/master_data/customer_form.html', {
        'form': form,
        'tier_choices': _tier_choices(),
    })
```

### locations_view
- File: `lumra_config/views/inventory_views.py`:933
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def locations_view(request):
    """
    Location list with JSON payload for Alpine.js front-end.

    Uses json_script-safe serialisation (consistent with recipe_list pattern).
    Fields not present in the model (city, phone, etc.) are NOT fabricated
    here — the front-end should handle missing keys gracefully instead.
    """

    locations_qs = Location.objects.all().order_by("name")

    # Check if locations is empty
    if not locations_qs.exists():
        return render(
            request,
            "lumra_pages/master_data/locations.html",
            create_empty_context("Locations Management", "Data lokasi tidak ditemukan. Silahkan tambah lokasi terlebih dahulu.")
        )

    # Serialise only fields that actually exist on the model
    locations_data = [
        {
            "id":            loc.id,
            "name":          loc.name,
            "address":       loc.address,
            "location_type": loc.location_type,
            "created_at":    localtime(loc.created_at).strftime("%Y-%m-%d"),
        }
        for loc in locations_qs
    ]

    context = {
        "locations":      locations_qs,          # for server-side rendering fallback
        "locations_json": json.dumps(locations_data),  # for Alpine.js
        "report_title":   "Locations Management",
        "is_empty": False,
    }

    return render(request, "lumra_pages/master_data/locations.html", context)
```

### locations_view
- File: `lumra_config/views/inventory_views.py`:958
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def locations_view(request):
    """
    Location list with JSON payload for Alpine.js front-end.

    Uses json_script-safe serialisation (consistent with recipe_list pattern).
    Fields not present in the model (city, phone, etc.) are NOT fabricated
    here — the front-end should handle missing keys gracefully instead.
    """

    locations_qs = Location.objects.all().order_by("name")

    # Check if locations is empty
    if not locations_qs.exists():
        return render(
            request,
            "lumra_pages/master_data/locations.html",
            create_empty_context("Locations Management", "Data lokasi tidak ditemukan. Silahkan tambah lokasi terlebih dahulu.")
        )

    # Serialise only fields that actually exist on the model
    locations_data = [
        {
            "id":            loc.id,
            "name":          loc.name,
            "address":       loc.address,
            "location_type": loc.location_type,
            "created_at":    localtime(loc.created_at).strftime("%Y-%m-%d"),
        }
        for loc in locations_qs
    ]

    context = {
        "locations":      locations_qs,          # for server-side rendering fallback
        "locations_json": json.dumps(locations_data),  # for Alpine.js
        "report_title":   "Locations Management",
        "is_empty": False,
    }

    return render(request, "lumra_pages/master_data/locations.html", context)
```

### bank_accounts
- File: `lumra_config/views/master_data_extended_views.py`:20
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def bank_accounts(request):
    """List all bank accounts."""
    context = {}
    return render(request, 'lumra_pages/master_data/bank_accounts.html', context)
```

### bank_account_form
- File: `lumra_config/views/master_data_extended_views.py`:27
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def bank_account_form(request, pk=None):
    """Create/Edit bank account."""
    context = {}
    return render(request, 'lumra_pages/master_data/bank_account_form.html', context)
```

### payment_terms_list
- File: `lumra_config/views/master_data_extended_views.py`:36
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def payment_terms_list(request):
    """List all payment terms."""
    context = {}
    return render(request, 'lumra_pages/master_data/payment_terms_list.html', context)
```

### payment_terms_form
- File: `lumra_config/views/master_data_extended_views.py`:43
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def payment_terms_form(request, pk=None):
    """Create/Edit payment terms."""
    context = {}
    return render(request, 'lumra_pages/master_data/payment_terms_form.html', context)
```

### tax_list
- File: `lumra_config/views/master_data_extended_views.py`:52
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def tax_list(request):
    """List all tax rates."""
    context = {}
    return render(request, 'lumra_pages/master_data/tax_list.html', context)
```

### tax_form
- File: `lumra_config/views/master_data_extended_views.py`:59
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def tax_form(request, pk=None):
    """Create/Edit tax rate."""
    context = {}
    return render(request, 'lumra_pages/master_data/tax_form.html', context)
```

### reason_codes
- File: `lumra_config/views/master_data_extended_views.py`:68
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def reason_codes(request):
    """List all reason codes."""
    context = {}
    return render(request, 'lumra_pages/master_data/reason_codes.html', context)
```

### tags_list
- File: `lumra_config/views/master_data_extended_views.py`:77
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def tags_list(request):
    """List all tags."""
    context = {}
    return render(request, 'lumra_pages/master_data/tags_list.html', context)
```

### locations
- File: `lumra_config/views/master_data_extended_views.py`:86
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def locations(request):
    """List all warehouse locations."""
    context = {}
    return render(request, 'lumra_pages/master_data/locations.html', context)
```

### location_list
- File: `lumra_config/views/master_data_extended_views.py`:93
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def location_list(request):
    """Alternative endpoint for locations."""
    context = {}
    return render(request, 'lumra_pages/master_data/location_list.html', context)
```

### customers
- File: `lumra_config/views/master_data_extended_views.py`:102
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customers(request):
    """List all customers."""
    context = {}
    return render(request, 'lumra_pages/master_data/customers.html', context)
```

### customers_list
- File: `lumra_config/views/master_data_extended_views.py`:109
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customers_list(request):
    """Alternative endpoint for customers list."""
    context = {}
    return render(request, 'lumra_pages/master_data/customers_list.html', context)
```

### customer
- File: `lumra_config/views/master_data_extended_views.py`:116
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customer(request, pk=None):
    """Alternative endpoint for customer."""
    context = {}
    return render(request, 'lumra_pages/master_data/customer.html', context)
```

### customer_detail
- File: `lumra_config/views/master_data_extended_views.py`:123
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customer_detail(request, pk):
    """View customer detail."""
    context = {}
    return render(request, 'lumra_pages/master_data/customer_detail.html', context)
```

### customer_form
- File: `lumra_config/views/master_data_extended_views.py`:130
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customer_form(request, pk=None):
    """Create/Edit customer."""
    context = {}
    return render(request, 'lumra_pages/master_data/customer_form.html', context)
```

### stock_opname
- File: `lumra_config/views/master_data_extended_views.py`:139
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def stock_opname(request):
    """Stock opname management."""
    context = {}
    return render(request, 'lumra_pages/master_data/stock_opname.html', context)
```

### stock_opname_session_detail
- File: `lumra_config/views/master_data_extended_views.py`:146
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def stock_opname_session_detail(request, pk):
    """View stock opname session detail."""
    context = {}
    return render(request, 'lumra_pages/master_data/stock_opname_session_detail.html', context)
```

### categories_list
- File: `lumra_config/views/masterdata_views.py`:44
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def categories_list(request):
    q = request.GET.get("q", "").strip()
    qs = Category.objects.order_by("name")

    if q:
        qs = qs.filter(name__icontains=q)

    # Check if categories is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/categories_list.html",
            create_empty_context("Categories", "Data kategori tidak ditemukan. Silahkan tambah kategori terlebih dahulu.")
        )

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "categories":  page_obj.object_list,
        "page_obj":    page_obj,
        "query":       q,
        "report_title": "Categories",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/categories_list.html", context)
```

### categories_list
- File: `lumra_config/views/masterdata_views.py`:60
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def categories_list(request):
    q = request.GET.get("q", "").strip()
    qs = Category.objects.order_by("name")

    if q:
        qs = qs.filter(name__icontains=q)

    # Check if categories is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/categories_list.html",
            create_empty_context("Categories", "Data kategori tidak ditemukan. Silahkan tambah kategori terlebih dahulu.")
        )

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "categories":  page_obj.object_list,
        "page_obj":    page_obj,
        "query":       q,
        "report_title": "Categories",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/categories_list.html", context)
```

### category_create
- File: `lumra_config/views/masterdata_views.py`:74
- Decorators: `login_required`
- Context keys eksplisit: `form`, `is_edit`, `report_title`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Category '{model_instance.name}' created successfully.")
            return redirect("categories_list")
    else:
        form = CategoryForm()

    return render(
        request,
        "lumra_pages/master_data/category_form.html",
        {"form": form, "is_edit": False, "report_title": "Add Category"},
    )
```

### category_update
- File: `lumra_config/views/masterdata_views.py`:94
- Decorators: `login_required`
- Context keys eksplisit: `form`, `is_edit`, `report_title`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def category_update(request, pk):
    model_instance = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=model_instance)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Category '{model_instance.name}' updated successfully.")
            return redirect("categories_list")
    else:
        form = CategoryForm(instance=model_instance)

    return render(
        request,
        "lumra_pages/master_data/category_form.html",
        {"form": form, "is_edit": True, "report_title": "Edit Category"},
    )
```

### units_list
- File: `lumra_config/views/masterdata_views.py`:152
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def units_list(request):
    q = request.GET.get("q", "").strip()
    qs = Unit.objects.order_by("name")

    if q:
        # FIX: was Q(short_name__icontains=q) — field renamed to 'symbol' in refactored model
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(symbol__icontains=q)
        )

    # Check if units is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/units_list.html",
            create_empty_context("Units", "Data satuan tidak ditemukan. Silahkan tambah satuan terlebih dahulu.")
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        )
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "units":        page_obj.object_list,
        "page_obj":     page_obj,
        "query":        q,
        "report_title": "Units",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/units_list.html", context)
```

### units_list
- File: `lumra_config/views/masterdata_views.py`:173
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def units_list(request):
    q = request.GET.get("q", "").strip()
    qs = Unit.objects.order_by("name")

    if q:
        # FIX: was Q(short_name__icontains=q) — field renamed to 'symbol' in refactored model
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(symbol__icontains=q)
        )

    # Check if units is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/units_list.html",
            create_empty_context("Units", "Data satuan tidak ditemukan. Silahkan tambah satuan terlebih dahulu.")
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        )
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "units":        page_obj.object_list,
        "page_obj":     page_obj,
        "query":        q,
        "report_title": "Units",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/units_list.html", context)
```

### unit_create
- File: `lumra_config/views/masterdata_views.py`:187
- Decorators: `login_required`
- Context keys eksplisit: `form`, `is_edit`, `report_title`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def unit_create(request):
    if request.method == "POST":
        form = UnitForm(request.POST)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Unit '{model_instance.name}' created successfully.")
            return redirect("units_list")
    else:
        form = UnitForm()

    return render(
        request,
        "lumra_pages/master_data/unit_form.html",
        {"form": form, "is_edit": False, "report_title": "Add Unit"},
    )
```

### unit_update
- File: `lumra_config/views/masterdata_views.py`:207
- Decorators: `login_required`
- Context keys eksplisit: `form`, `is_edit`, `report_title`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def unit_update(request, pk):
    model_instance = get_object_or_404(Unit, pk=pk)

    if request.method == "POST":
        form = UnitForm(request.POST, instance=model_instance)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Unit '{model_instance.name}' updated successfully.")
            return redirect("units_list")
    else:
        form = UnitForm(instance=model_instance)

    return render(
        request,
        "lumra_pages/master_data/unit_form.html",
        {"form": form, "is_edit": True, "report_title": "Edit Unit"},
    )
```

### vendors_list
- File: `lumra_config/views/masterdata_views.py`:270
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def vendors_list(request):
    q = request.GET.get("q", "").strip()
    qs = Vendor.objects.order_by("name")

    if q:
        # FIX: was Q(contact_name__icontains=q) — field is 'contact_person' in model
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(contact_person__icontains=q)
        )

    # Check if vendors is empty
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/vendors_list.html",
            create_empty_context("Vendors", "Data vendor tidak ditemukan. Silahkan tambah vendor terlebih dahulu.")
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        )
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "vendors":      page_obj.object_list,
        "page_obj":     page_obj,
        "query":        q,
        "report_title": "Vendors",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/vendors_list.html", context)
```

### vendors_list
- File: `lumra_config/views/masterdata_views.py`:292
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def vendors_list(request):
    q = request.GET.get("q", "").strip()
    qs = Vendor.objects.order_by("name")

    if q:
        # FIX: was Q(contact_name__icontains=q) — field is 'contact_person' in model
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(contact_person__icontains=q)
        )

    # Check if vendors is empty
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/vendors_list.html",
            create_empty_context("Vendors", "Data vendor tidak ditemukan. Silahkan tambah vendor terlebih dahulu.")
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        )
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "vendors":      page_obj.object_list,
        "page_obj":     page_obj,
        "query":        q,
        "report_title": "Vendors",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/vendors_list.html", context)
```

### vendor_create
- File: `lumra_config/views/masterdata_views.py`:306
- Decorators: `login_required`
- Context keys eksplisit: `form`, `is_edit`, `report_title`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def vendor_create(request):
    if request.method == "POST":
        form = VendorForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Vendor '{obj.name}' created successfully.")
            return redirect("vendors_list")
    else:
        form = VendorForm()

    return render(
        request,
        "lumra_pages/master_data/vendor_form.html",
        {"form": form, "is_edit": False, "report_title": "Add Vendor"},
    )
```

### vendor_update
- File: `lumra_config/views/masterdata_views.py`:326
- Decorators: `login_required`
- Context keys eksplisit: `form`, `is_edit`, `report_title`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def vendor_update(request, pk):
    model_instance = get_object_or_404(Vendor, pk=pk)

    if request.method == "POST":
        form = VendorForm(request.POST, instance=model_instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Vendor '{obj.name}' updated successfully.")
            return redirect("vendors_list")
    else:
        form = VendorForm(instance=model_instance)

    return render(
        request,
        "lumra_pages/master_data/vendor_form.html",
        {"form": form, "is_edit": True, "report_title": "Edit Vendor"},
    )
```

### customers_view
- File: `lumra_config/views/misc_views.py`:821
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customers_view(request):
    context = {"customers": []}
    return render(request, "lumra_pages/master_data/customers.html", context)
```

### add_customer_view
- File: `lumra_config/views/misc_views.py`:827
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def add_customer_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/master_data/customers.html", context)
```

### view_customer_view
- File: `lumra_config/views/misc_views.py`:833
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def view_customer_view(request, customer_id):
    context = {"customer_id": customer_id}
    return render(request, "lumra_pages/master_data/customers.html", context)
```

### edit_customer_view
- File: `lumra_config/views/misc_views.py`:839
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def edit_customer_view(request, customer_id):
    context = {"customer_id": customer_id, "action": "edit"}
    return render(request, "lumra_pages/master_data/customers.html", context)
```

### delete_customer_view
- File: `lumra_config/views/misc_views.py`:846
- Decorators: `login_required`
- Context keys eksplisit: `customer_id`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def delete_customer_view(request, customer_id):
    # FIX: stub views untuk destructive actions sebaiknya POST-only
    if request.method != "POST":
        return render(request, "lumra_pages/master_data/customers.html", {"customer_id": customer_id})
    # TODO: implement actual delete logic
    messages.warning(request, "Delete customer belum diimplementasi.")
    return redirect("customers")
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
