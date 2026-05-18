# Claude Handoff: marketing

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 11
Jumlah view terkait: 24

## Template Scope

### lumra_pages/marketing/add_campaign.html
- File: `lumra_config/templates/lumra_pages/marketing/add_campaign.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=85, interactive=40, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Campaigns / {% if campaign %}Edit{% else %}Buat Baru{% endif %}
  - HEADING (H1): {% if campaign %}Edit Campaign {% else %}Campaign Baru {% endif %}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BADGE / STATUS: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ FORM ]: {% csrf_token %} 1 Pilih Tipe Promo % Diskon Persen / Flat Potongan % atau nomin…
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-7 h-7 rounded-lg bg-rose-50 text-rose-400 hover:'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/marketing/campaign_list.html
- File: `lumra_config/templates/lumra_pages/marketing/campaign_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=64, interactive=7, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Total Campaigns {{ total_campaigns|default:0 }} All time
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Active Now {{ active_campaigns|default:0 }} ▶ Running
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Total Budget {{ total_budget|default:0|floatformat:0 }} Across all
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/marketing/customer_segment_list.html
- File: `lumra_config/templates/lumra_pages/marketing/customer_segment_list.html`
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

### lumra_pages/marketing/discount.html
- File: `lumra_config/templates/lumra_pages/marketing/discount.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=24, interactive=3, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 💸 Discounts
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/marketing/loyalty_members.html
- File: `lumra_config/templates/lumra_pages/marketing/loyalty_members.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=24, interactive=3, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 🏆 Loyalty Program Members
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/marketing/promotion_calendar.html
- File: `lumra_config/templates/lumra_pages/marketing/promotion_calendar.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=57, interactive=11, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Voucher / Kalender Promo
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Kalender Promo
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - ALERT / NOTIFICATION: tumpang tindih terdeteksi Lihat semua detail
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/marketing/voucher_claim_log.html
- File: `lumra_config/templates/lumra_pages/marketing/voucher_claim_log.html`
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

### lumra_pages/marketing/voucher_list.html
- File: `lumra_config/templates/lumra_pages/marketing/voucher_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=60, interactive=11, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Voucher
  - HEADING (H1): Voucher & Promo
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CALENDAR: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='' class='mt-1 w-3.5 h-3.5 accent-emerald-500 rounded cursor'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/marketing/campaign.html
- File: `lumra_config/templates/lumra_pages/marketing/campaign.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=64, interactive=7, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Total Campaigns {{ total_campaigns|default:0 }} All time
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Active Now {{ active_campaigns|default:0 }} ▶ Running
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Total Budget {{ total_budget|default:0|floatformat:0 }} Across all
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/marketing/customer_segment_form.html
- File: `lumra_config/templates/lumra_pages/marketing/customer_segment_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/marketing/voucher_form.html
- File: `lumra_config/templates/lumra_pages/marketing/voucher_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=53, interactive=22, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Voucher /
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: {# ══════════ LEFT: Form Fields ══════════ #} {# ── Section: Info Dasar ── #} In…
  - [ FORM ]: {# ══════════ LEFT: Form Fields ══════════ #} {# ── Section: Info Dasar ── #} In…
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### campaign_list
- File: `lumra_config/views/marketing_views.py`:20
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def campaign_list(request):
    """List all Campaigns."""
    context = {}
    return render(request, 'lumra_pages/marketing/campaign_list.html', context)
```

### campaign_detail
- File: `lumra_config/views/marketing_views.py`:34
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def campaign_detail(request, pk):
    """View Campaign detail."""
    context = {}
    return render(request, 'lumra_pages/marketing/campaign.html', context)
```

### discount_list
- File: `lumra_config/views/marketing_views.py`:43
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def discount_list(request):
    """List all Discounts."""
    context = {}
    return render(request, 'lumra_pages/marketing/discount.html', context)
```

### discount_form
- File: `lumra_config/views/marketing_views.py`:50
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def discount_form(request, pk=None):
    """Create/Edit Discount."""
    context = {}
    return render(request, 'lumra_pages/marketing/discount.html', context)
```

### voucher_list
- File: `lumra_config/views/marketing_views.py`:59
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def voucher_list(request):
    """List all Vouchers."""
    context = {}
    return render(request, 'lumra_pages/marketing/voucher_list.html', context)
```

### voucher_form
- File: `lumra_config/views/marketing_views.py`:66
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def voucher_form(request, pk=None):
    """Create/Edit Voucher."""
    context = {}
    return render(request, 'lumra_pages/marketing/voucher_form.html', context)
```

### voucher_claim_log
- File: `lumra_config/views/marketing_views.py`:73
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def voucher_claim_log(request):
    """View Voucher Claim Log."""
    context = {}
    return render(request, 'lumra_pages/marketing/voucher_claim_log.html', context)
```

### loyalty_members
- File: `lumra_config/views/marketing_views.py`:82
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def loyalty_members(request):
    """List all Loyalty Members."""
    context = {}
    return render(request, 'lumra_pages/marketing/loyalty_members.html', context)
```

### loyalty_member_form
- File: `lumra_config/views/marketing_views.py`:89
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def loyalty_member_form(request, pk=None):
    """Create/Edit Loyalty Member."""
    context = {}
    return render(request, 'lumra_pages/marketing/loyalty_members.html', context)
```

### customer_segment_list
- File: `lumra_config/views/marketing_views.py`:98
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customer_segment_list(request):
    """List all Customer Segments."""
    context = {}
    return render(request, 'lumra_pages/marketing/customer_segment_list.html', context)
```

### customer_segment_form
- File: `lumra_config/views/marketing_views.py`:105
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def customer_segment_form(request, pk=None):
    """Create/Edit Customer Segment."""
    context = {}
    return render(request, 'lumra_pages/marketing/customer_segment_form.html', context)
```

### promotion_calendar
- File: `lumra_config/views/marketing_views.py`:114
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def promotion_calendar(request):
    """View Promotion Calendar."""
    context = {}
    return render(request, 'lumra_pages/marketing/promotion_calendar.html', context)
```

### campaign_list_view
- File: `lumra_config/views/misc_views.py`:864
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def campaign_list_view(request):
    context = {
        "total_campaigns":     0,
        "active_campaigns":    0,
        "completed_campaigns": 0,
        "campaigns":           [],
    }
    return render(request, "lumra_pages/marketing/campaign.html", context)
```

### add_campaign_view
- File: `lumra_config/views/misc_views.py`:870
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def add_campaign_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/marketing/campaign.html", context)
```

### edit_campaign_view
- File: `lumra_config/views/misc_views.py`:876
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def edit_campaign_view(request, campaign_id):
    context = {"campaign_id": campaign_id, "action": "edit"}
    return render(request, "lumra_pages/marketing/campaign.html", context)
```

### delete_campaign_view
- File: `lumra_config/views/misc_views.py`:882
- Decorators: `login_required`
- Context keys eksplisit: `campaign_id`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def delete_campaign_view(request, campaign_id):
    if request.method != "POST":
        return render(request, "lumra_pages/marketing/campaign.html", {"campaign_id": campaign_id})
    messages.warning(request, "Delete campaign belum diimplementasi.")
    return redirect("campaign_list")
```

### discount_list_view
- File: `lumra_config/views/misc_views.py`:898
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def discount_list_view(request):
    context = {
        "total_discounts":  0,
        "active_discounts": 0,
        "discounts":        [],
    }
    return render(request, "lumra_pages/marketing/discount.html", context)
```

### add_discount_view
- File: `lumra_config/views/misc_views.py`:904
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def add_discount_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/marketing/discount.html", context)
```

### edit_discount_view
- File: `lumra_config/views/misc_views.py`:910
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def edit_discount_view(request, discount_id):
    context = {"discount_id": discount_id, "action": "edit"}
    return render(request, "lumra_pages/marketing/discount.html", context)
```

### delete_discount_view
- File: `lumra_config/views/misc_views.py`:916
- Decorators: `login_required`
- Context keys eksplisit: `discount_id`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def delete_discount_view(request, discount_id):
    if request.method != "POST":
        return render(request, "lumra_pages/marketing/discount.html", {"discount_id": discount_id})
    messages.warning(request, "Delete discount belum diimplementasi.")
    return redirect("discount_list")
```

### loyalty_members_view
- File: `lumra_config/views/misc_views.py`:932
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def loyalty_members_view(request):
    context = {
        "total_members":  0,
        "active_members": 0,
        "members":        [],
    }
    return render(request, "lumra_pages/marketing/loyalty_members.html", context)
```

### add_loyalty_member_view
- File: `lumra_config/views/misc_views.py`:938
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def add_loyalty_member_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/marketing/loyalty_members.html", context)
```

### edit_loyalty_member_view
- File: `lumra_config/views/misc_views.py`:944
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def edit_loyalty_member_view(request, member_id):
    context = {"member_id": member_id, "action": "edit"}
    return render(request, "lumra_pages/marketing/loyalty_members.html", context)
```

### delete_loyalty_member_view
- File: `lumra_config/views/misc_views.py`:950
- Decorators: `login_required`
- Context keys eksplisit: `member_id`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def delete_loyalty_member_view(request, member_id):
    if request.method != "POST":
        return render(request, "lumra_pages/marketing/loyalty_members.html", {"member_id": member_id})
    # TODO[C3-LONG]: 'financial_reports_view' = 206 baris (max 30). Pecah: financial_reports_view_validate(), financial_reports_view_query(), financial_reports_view_render()
    messages.warning(request, "Delete loyalty member belum diimplementasi.")
    return redirect("loyalty_members")
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
