# Claude Handoff: retur_and_refund

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 3
Jumlah view terkait: 3

## Template Scope

### lumra_pages/sales/retur_and_refund/retur_list.html
- File: `lumra_config/templates/lumra_pages/sales/retur_and_refund/retur_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=28, interactive=4, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Retur Penjualan
  - HEADING (H1): Retur Penjualan
  - BUTTON: Buat Retur: Buat Retur
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Retur
  - CARD: Pending
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs text-slate-400 hover:text-slate-600 px-2'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/sales/retur_and_refund/retur_detail.html
- File: `lumra_config/templates/lumra_pages/sales/retur_and_refund/retur_detail.html`
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

### lumra_pages/sales/retur_and_refund/retur_form.html
- File: `lumra_config/templates/lumra_pages/sales/retur_and_refund/retur_form.html`
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

### retur_list
- File: `lumra_config/views/sales_views.py`:199
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def retur_list(request):
    """List all Returns/Refunds."""
    context = {}
    return render(request, 'lumra_pages/sales/retur_and_refund/retur_list.html', context)
```

### retur_form
- File: `lumra_config/views/sales_views.py`:206
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def retur_form(request, pk=None):
    """Create/Edit Return/Refund."""
    context = {}
    return render(request, 'lumra_pages/sales/retur_and_refund/retur_form.html', context)
```

### retur_detail
- File: `lumra_config/views/sales_views.py`:213
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def retur_detail(request, pk):
    """View Return/Refund detail."""
    context = {}
    return render(request, 'lumra_pages/sales/retur_and_refund/retur_detail.html', context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
