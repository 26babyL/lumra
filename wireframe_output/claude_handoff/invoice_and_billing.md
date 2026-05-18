# Claude Handoff: invoice_and_billing

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 5
Jumlah view terkait: 5

## Template Scope

### lumra_pages/sales/invoice_and_billing/invoice_list.html
- File: `lumra_config/templates/lumra_pages/sales/invoice_and_billing/invoice_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=29, interactive=4, issues=3, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Faktur
  - HEADING (H1): Daftar Faktur
  - BUTTON: Buat Faktur: Buat Faktur
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Tagihan
  - CARD: Jatuh Tempo
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-emerald-50 text-emerald-600 hover:b'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs text-emerald-600 font-bold px-2 flex items'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales/invoice_and_billing/payment_list.html
- File: `lumra_config/templates/lumra_pages/sales/invoice_and_billing/payment_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=26, interactive=3, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Pembayaran
  - HEADING (H1): Riwayat Pembayaran
  - BUTTON: Catat Manual: Catat Manual
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Masuk
  - CARD: Perlu Verifikasi
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-emerald-50 text-emerald-600 hover:b'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales/invoice_and_billing/invoice_detail.html
- File: `lumra_config/templates/lumra_pages/sales/invoice_and_billing/invoice_detail.html`
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

### lumra_pages/sales/invoice_and_billing/invoice_form.html
- File: `lumra_config/templates/lumra_pages/sales/invoice_and_billing/invoice_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/sales/invoice_and_billing/payment_form.html
- File: `lumra_config/templates/lumra_pages/sales/invoice_and_billing/payment_form.html`
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

### invoice_list
- File: `lumra_config/views/sales_views.py`:162
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def invoice_list(request):
    """List all Invoices."""
    context = {}
    return render(request, 'lumra_pages/sales/invoice_and_billing/invoice_list.html', context)
```

### invoice_form
- File: `lumra_config/views/sales_views.py`:169
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def invoice_form(request, pk=None):
    """Create/Edit Invoice."""
    context = {}
    return render(request, 'lumra_pages/sales/invoice_and_billing/invoice_form.html', context)
```

### invoice_detail
- File: `lumra_config/views/sales_views.py`:176
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def invoice_detail(request, pk):
    """View Invoice detail."""
    context = {}
    return render(request, 'lumra_pages/sales/invoice_and_billing/invoice_detail.html', context)
```

### payment_list
- File: `lumra_config/views/sales_views.py`:183
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def payment_list(request):
    """List all Payments."""
    context = {}
    return render(request, 'lumra_pages/sales/invoice_and_billing/payment_list.html', context)
```

### payment_form
- File: `lumra_config/views/sales_views.py`:190
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def payment_form(request, pk=None):
    """Create/Edit Payment."""
    context = {}
    return render(request, 'lumra_pages/sales/invoice_and_billing/payment_form.html', context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
