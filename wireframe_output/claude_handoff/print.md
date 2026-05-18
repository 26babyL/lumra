# Claude Handoff: print

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 12
Jumlah view terkait: 11

## Template Scope

### lumra_pages/print/print_base.html
- File: `lumra_config/templates/lumra_pages/print/print_base.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=0, interactive=0, issues=0, scroll_nesting=0

### lumra_pages/print/print_purchase_order.html
- File: `lumra_config/templates/lumra_pages/print/print_purchase_order.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=2, interactive=0, issues=1, scroll_nesting=0
- Komponen utama:
  - [ TABLE ]: PURCHASE ORDER {{ document_number }} Tanggal: {{ document_date|date:"d M Y" }} S…
  - [ TABLE ]: Barang Deskripsi Unit Qty Harga Total {% for item in items %} {{ item.name }} {{…
- Temuan reverse:
  - [info] table_no_header: Tabel tanpa <th>/<thead>: <table> id='' class='table-w-full'

### lumra_pages/print/print_credit_note.html
- File: `lumra_config/templates/lumra_pages/print/print_credit_note.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=2, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ dashboard_title }}
  - LAYOUT CONTAINER [GRID 1 cols]: 

### lumra_pages/print/print_delivery_note.html
- File: `lumra_config/templates/lumra_pages/print/print_delivery_note.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=1, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - [ TABLE ]: SKU Produk Deskripsi Unit Qty {% for item in items %} {{ item.sku }} {{ item.nam…

### lumra_pages/print/print_invoice.html
- File: `lumra_config/templates/lumra_pages/print/print_invoice.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=11, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): CoffeeShop
  - HEADING (H1): INVOICE
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - [ TABLE ]: Keterangan Harga Satuan Qty Total {% for item in items %} {{ item.name }} {{ ite…
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/print/print_packing_slip.html
- File: `lumra_config/templates/lumra_pages/print/print_packing_slip.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=1, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - [ TABLE ]: Barang Qty Unit Keterangan {% for item in items %} {{ item.name }} {{ item.quant…

### lumra_pages/print/print_payment_receipt.html
- File: `lumra_config/templates/lumra_pages/print/print_payment_receipt.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=10, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H2): BUKTI KAS
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ amount_received }}
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/print/print_production_order.html
- File: `lumra_config/templates/lumra_pages/print/print_production_order.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=1, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - [ TABLE ]: Komponen SKU Qty Unit Catatan {% for item in bom_items %} {{ item.component.prod…

### lumra_pages/print/print_quotation.html
- File: `lumra_config/templates/lumra_pages/print/print_quotation.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=7, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): CoffeeShop
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ TABLE ]: Deskripsi Satuan Harga Jumlah Total {% for item in items %} {{ item.name }} {{ i…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/print/print_receipt.html
- File: `lumra_config/templates/lumra_pages/print/print_receipt.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=6, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): CoffeeShop
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/print/print_sales_order.html
- File: `lumra_config/templates/lumra_pages/print/print_sales_order.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=0, interactive=0, issues=0, scroll_nesting=0

### lumra_pages/print/print_stock_opname.html
- File: `lumra_config/templates/lumra_pages/print/print_stock_opname.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=2, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ dashboard_title }}
  - LAYOUT CONTAINER [GRID 1 cols]: 

## View Scope

### print_invoice
- File: `lumra_config/views/print_views.py`:95
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_invoice(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context["object"] = order
    return render(request, "lumra_pages/print/print_invoice.html", context)
```

### print_sales_order
- File: `lumra_config/views/print_views.py`:104
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_sales_order(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context["object"] = order
    return render(request, "lumra_pages/print/print_sales_order.html", context)
```

### print_quotation
- File: `lumra_config/views/print_views.py`:113
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_quotation(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context["object"] = order
    return render(request, "lumra_pages/print/print_quotation.html", context)
```

### print_purchase_order
- File: `lumra_config/views/print_views.py`:121
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def print_purchase_order(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    context = _build_purchase_order_context(vendor)
    return render(request, "lumra_pages/print/print_purchase_order.html", context)
```

### print_delivery_note
- File: `lumra_config/views/print_views.py`:136
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_delivery_note(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context.update(
        {
            "document_number": f"DN-{order.id:05d}",
            "source_name": "Gudang Pusat",
            "source_address": "Lokasi operasional utama",
        }
    )
    return render(request, "lumra_pages/print/print_delivery_note.html", context)
```

### print_packing_slip
- File: `lumra_config/views/print_views.py`:150
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_packing_slip(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context.update(
        {
            "document_number": f"PK-{order.id:05d}",
            "package_count": max(1, order.items.count()),
        }
    )
    return render(request, "lumra_pages/print/print_packing_slip.html", context)
```

### print_payment_receipt
- File: `lumra_config/views/print_views.py`:161
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_payment_receipt(request, pk):
    voucher = get_object_or_404(PaymentVoucher.objects.select_related("vendor"), pk=pk)
    context = {
        "voucher": voucher,
        "document_number": voucher.number,
    }
    return render(request, "lumra_pages/print/print_payment_receipt.html", context)
```

### print_receipt
- File: `lumra_config/views/print_views.py`:169
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_receipt(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    return render(request, "lumra_pages/print/print_receipt.html", context)
```

### print_production_order
- File: `lumra_config/views/print_views.py`:196
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_production_order(request, pk):
    production_order = get_object_or_404(
        ProductionOrder.objects.select_related(
            "bom",
            "bom__finished_variant",
            "bom__finished_variant__product",
            "unit",
        ).prefetch_related("bom__items__component__product"),
        pk=pk,
    )
    context = {
        "production_order": production_order,
        "document_number": production_order.code,
        "document_date": production_order.created_at,
        "product_name": production_order.bom.finished_variant.product.name,
        "product_sku": production_order.bom.finished_variant.sku,
        "target_quantity": production_order.target_quantity,
        "produced_quantity": production_order.produced_quantity,
        "unit_name": production_order.unit.symbol if production_order.unit_id else "-",
        "bom_items": production_order.bom.items.all(),
        "notes": production_order.notes,
    }
    return render(request, "lumra_pages/print/print_production_order.html", context)
```

### print_credit_note
- File: `lumra_config/views/print_views.py`:204
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_credit_note(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    return render(request, "lumra_pages/print/print_credit_note.html", context)
```

### print_stock_opname
- File: `lumra_config/views/print_views.py`:218
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def print_stock_opname(request, pk):
    session = get_object_or_404(
        StockOpnameSession.objects.select_related("location", "created_by").prefetch_related("items__variant__product"),
        pk=pk,
    )
    context = {
        "session": session,
        "document_number": f"SO-{session.id:05d}",
    }
    return render(request, "lumra_pages/print/print_stock_opname.html", context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
