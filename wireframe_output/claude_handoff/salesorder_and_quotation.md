# Claude Handoff: salesorder_and_quotation

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 6
Jumlah view terkait: 6

## Template Scope

### lumra_pages/sales/salesorder_and_quotation/quotation_list.html
- File: `lumra_config/templates/lumra_pages/sales/salesorder_and_quotation/quotation_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=27, interactive=3, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Penawaran Harga
  - HEADING (H1): Daftar Penawaran
  - BUTTON: Buat Penawaran: Buat Penawaran
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total
  - CARD: Terkirim
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-emerald-50 text-emerald-600 hover:b'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales/salesorder_and_quotation/sales_order_list.html
- File: `lumra_config/templates/lumra_pages/sales/salesorder_and_quotation/sales_order_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=27, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Sales Order
  - HEADING (H1): Daftar Sales Order
  - BUTTON: Buat Order: Buat Order
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Order
  - CARD: Belum Bayar
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales/salesorder_and_quotation/quotation_detail.html
- File: `lumra_config/templates/lumra_pages/sales/salesorder_and_quotation/quotation_detail.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=5, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ detail_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Hapus: Hapus
  - LAYOUT CONTAINER [GRID 2 cols]: 

### lumra_pages/sales/salesorder_and_quotation/quotation_form.html
- File: `lumra_config/templates/lumra_pages/sales/salesorder_and_quotation/quotation_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/sales/salesorder_and_quotation/sales_order_detail.html
- File: `lumra_config/templates/lumra_pages/sales/salesorder_and_quotation/sales_order_detail.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=5, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ detail_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Hapus: Hapus
  - LAYOUT CONTAINER [GRID 2 cols]: 

### lumra_pages/sales/salesorder_and_quotation/sales_order_form.html
- File: `lumra_config/templates/lumra_pages/sales/salesorder_and_quotation/sales_order_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

## View Scope

### sales_order_list
- File: `lumra_config/views/sales_views.py`:118
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def sales_order_list(request):
    """List all Sales Orders."""
    context = {}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/sales_order_list.html', context)
```

### sales_order_form
- File: `lumra_config/views/sales_views.py`:125
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def sales_order_form(request, pk=None):
    """Create/Edit Sales Order."""
    context = {}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/sales_order_form.html', context)
```

### sales_order_detail
- File: `lumra_config/views/sales_views.py`:132
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def sales_order_detail(request, pk):
    """View Sales Order detail."""
    context = {}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/sales_order_detail.html', context)
```

### quotation_list
- File: `lumra_config/views/sales_views.py`:139
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def quotation_list(request):
    """List all Quotations."""
    context = {}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/quotation_list.html', context)
```

### quotation_form
- File: `lumra_config/views/sales_views.py`:146
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def quotation_form(request, pk=None):
    """Create/Edit Quotation."""
    context = {}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/quotation_form.html', context)
```

### quotation_detail
- File: `lumra_config/views/sales_views.py`:153
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def quotation_detail(request, pk):
    """View Quotation detail."""
    context = {}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/quotation_detail.html', context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
