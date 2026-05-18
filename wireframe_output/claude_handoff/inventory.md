# Claude Handoff: inventory

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 27
Jumlah view terkait: 32

## Template Scope

### lumra_pages/inventory/product_list.html
- File: `lumra_config/templates/lumra_pages/inventory/product_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=115, interactive=52, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} Master Data Daftar Produk Kelola semua produk, harga, sto…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Daftar Produk
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Import: Import
  - BUTTON: Export CSV: Export CSV
  - BUTTON (Primary): Tambah Produk N
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_overview.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_overview.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=81, interactive=32, issues=4, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {{ inventory_items|json_script:"inventory-items-data" }}…
  - ALPINE COMPONENT [inventoryPlanner()]: {# ── HEADER ── #} Dashboard / Inventory Planner Inventory P…
  - [ NAVIGATION BAR ]: Dashboard / Inventory Planner
  - [ ORDERED LIST ]: Dashboard / Inventory Planner
  - HEADING (H1): Inventory Planner
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:text-blue-600 hover:bg-'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:style='
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:text-purple-600 hover:b'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/add_stock_movement.html
- File: `lumra_config/templates/lumra_pages/inventory/add_stock_movement.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=38, interactive=9, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Record
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: {% csrf_token %} Record Movement Manage your 118K SKU Flow Tipe Pergerakan Stock…
  - CARD: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/adjustment_reasons.html
- File: `lumra_config/templates/lumra_pages/inventory/adjustment_reasons.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=19, interactive=10, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Master Data Alasan Koreksi
  - BUTTON: Tambah Alasan: Tambah Alasan
  - CARD: Kode Nama Alasan Tipe Koreksi Deskripsi Singkat Status Aksi
  - [ TABLE ]: Kode Nama Alasan Tipe Koreksi Deskripsi Singkat Status Aksi
  - BADGE / STATUS: 
  - INPUT [checkbox] : 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/batch_list.html
- File: `lumra_config/templates/lumra_pages/inventory/batch_list.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=25, interactive=1, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Inventory / Manajemen Batch
  - HEADING (H1): Batch & Lot Tracking
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Batch
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/expiry_tracking.html
- File: `lumra_config/templates/lumra_pages/inventory/expiry_tracking.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=23, interactive=6, issues=3, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: QC / Pantauan Kedaluwarsa
  - HEADING (H1): Dashboard Kedaluwarsa
  - BUTTON: Export Laporan: Export Laporan
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H2): Distribusi Risiko Stok
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='flex-1 py-2 bg-slate-50 text-slate-600 rounded-lg '
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='flex-1 py-2 bg-white border border-slate-200 text-'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/requisition_list.html
- File: `lumra_config/templates/lumra_pages/inventory/requisition_list.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=24, interactive=0, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Logistik / Permintaan Stok
  - HEADING (H1): Permintaan Stok (Requisition)
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Req
  - CARD: Pending
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_movement_form.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_movement_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=38, interactive=9, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Record
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: {% csrf_token %} Record Movement Manage your 118K SKU Flow Tipe Pergerakan Stock…
  - CARD: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_opname_approvals.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_opname_approvals.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=30, interactive=11, issues=3, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {# ── HEADER ────────────────────────────────────────────…
  - ALPINE COMPONENT [approvalsManager()]: {# ── HEADER ───────────────────────────────────────────────…
  - [ NAVIGATION BAR ]: Dashboard / Approvals
  - [ ORDERED LIST ]: Dashboard / Approvals
  - HEADING (H1): Stock Opname Approvals
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: {{ tab.label }} {% if tab.count is not N…: {{ tab.label }} {% if tab.count is not None %} {{ tab.count…
  - FILTER / TAB: {{ tab.count }}
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='inline-flex items-center gap-1 text-xs font-medium'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='inline-flex items-center gap-1 text-xs font-medium'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/supplier_evaluation.html
- File: `lumra_config/templates/lumra_pages/inventory/supplier_evaluation.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=21, interactive=2, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Evaluasi Performa Supplier
  - BUTTON: Tambah Vendor: Tambah Vendor
  - CARD: Supplier Terbaik Bulan Ini Skor Kualitas
  - HEADING (H2): Supplier Terbaik Bulan Ini
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H2): 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-slate-600 hover:text-emeral'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/supplier_price_confirm_delete.html
- File: `lumra_config/templates/lumra_pages/inventory/supplier_price_confirm_delete.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=47, interactive=17, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {% csrf_token %} Dashboard / Supplier Prices Supplier Pri…
  - ALPINE COMPONENT [supplierPriceManager()]: {% csrf_token %} Dashboard / Supplier Prices Supplier Price…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Supplier Prices
  - [ ORDERED LIST ]: Dashboard / Supplier Prices
  - HEADING (H1): Supplier Price List
  - BUTTON: Tambah Harga: Tambah Harga
  - [ FORM ]: Cari supplier, produk, atau harga Filter supplier Semua Supplier Filter Reset
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/supplier_price_form.html
- File: `lumra_config/templates/lumra_pages/inventory/supplier_price_form.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=8, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [supplierPriceForm()]: {# ── HEADER ───────────────────────────────────────────────…
  - [ NAVIGATION BAR ]: Dashboard / Supplier Prices / {% if is_edit %}Edit{% else %}Tambah{% endif %} Ha…
  - [ ORDERED LIST ]: Dashboard / Supplier Prices / {% if is_edit %}Edit{% else %}Tambah{% endif %} Ha…
  - HEADING (H1): {% if is_edit %}Edit Supplier Price{% else %}Tambah Supplier Price{% endif %}
  - [ FORM ]: {% csrf_token %} {# Supplier #} Supplier * {{ form.supplier }} {# x-text aman —…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/inventory/warehouse_zones.html
- File: `lumra_config/templates/lumra_pages/inventory/warehouse_zones.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=30, interactive=1, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Logistik / Manajemen Zona
  - HEADING (H1): Zona Gudang
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Zona
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/batch_detail.html
- File: `lumra_config/templates/lumra_pages/inventory/batch_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=24, interactive=4, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [batchDetailApp()]: ID Referensi: #REF-99281 Cetak Label Kembali Total Masuk Sis…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Cetak Label: Cetak Label
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/batch_form.html
- File: `lumra_config/templates/lumra_pages/inventory/batch_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=18, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: Input Batch Baru Catat kedatangan barang dengan detail lot Kode Batch / Lot Prod…
  - HEADING (H1): Input Batch Baru
  - [ FORM ]: Kode Batch / Lot Produk Pilih Produk... Lokasi Pilih Lokasi... Zona (Opsional) -…
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - INPUT FIELD: 
  - INPUT FIELD: Pilih Produk...
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/product_details.html
- File: `lumra_config/templates/lumra_pages/inventory/product_details.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=27, interactive=4, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [productDetail()]: {# ── BREADCRUMB ── #} Dashboard / Products / {{ product.nam…
  - [ NAVIGATION BAR ]: Dashboard / Products / {{ product.name }}
  - [ ORDERED LIST ]: Dashboard / Products / {{ product.name }}
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - IMAGE [{{ product.name }}]: {{ product.name }}
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/products.html
- File: `lumra_config/templates/lumra_pages/inventory/products.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=105, interactive=56, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): Produk
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Template CSV: Template CSV
  - BUTTON: Import CSV: Import CSV
  - BUTTON: Export CSV: Export CSV
  - BUTTON (Primary): Tambah Produk
  - LAYOUT CONTAINER [GRID 2 cols]: 

### lumra_pages/inventory/requisition_detail.html
- File: `lumra_config/templates/lumra_pages/inventory/requisition_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=21, interactive=6, issues=5, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [reqDetailApp()]: Dibuat pada Kembali Rute Pengiriman Dari Ke Barang Diminta P…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): 
  - BADGE / STATUS: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-emerald-500 hover:bg-emerald-600 te'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-white border border-rose-200 text-r'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-blue-500 hover:bg-blue-600 text-whi'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-slate-800 hover:bg-slate-700 text-w'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/requisition_form.html
- File: `lumra_config/templates/lumra_pages/inventory/requisition_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=18, interactive=7, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [reqFormApp()]: Buat Permintaan Stok Isi detail untuk memindahkan stok antar…
  - HEADING (H1): Buat Permintaan Stok
  - CARD: Lokasi Asal (Dari) Pilih Lokasi Asal... Lokasi Tujuan (Ke) Pilih Lokasi Tujuan..…
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - INPUT FIELD: Pilih Lokasi Asal...
  - INPUT FIELD: Pilih Lokasi Tujuan...
  - INPUT FIELD: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_movement.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_movement.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=58, interactive=11, issues=3, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} Dashboard / Stock Movement Stock Movement Control Tower L…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Stock Movement
  - HEADING (H1): Stock Movement Control Tower
  - LAYOUT CONTAINER [FLEX (row)]: 
  - ALPINE COMPONENT [{open:false}]: Export CSV Excel
  - BUTTON: Export: Export
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='flex-1 flex items-center justify-center gap-2 py-3'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='flex-1 flex items-center justify-center gap-2 py-3'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_opname_approval_detail.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_opname_approval_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=22, interactive=8, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {# ── HEADER ────────────────────────────────────────────…
  - ALPINE COMPONENT [sessionDetail()]: {# ── HEADER ───────────────────────────────────────────────…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Opname Locations / {{ session.location.name }} #{{ session.id }}
  - [ ORDERED LIST ]: Dashboard / Opname Locations / {{ session.location.name }} #{{ session.id }}
  - HEADING (H1): Session Detail — {{ session.location.name }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Print: Print
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_opname_form.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_opname_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=35, interactive=11, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [stockOpnameForm()]: {# ── HEADER ───────────────────────────────────────────────…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Opname Locations / {{ selected_location.name }}
  - [ ORDERED LIST ]: Dashboard / Opname Locations / {{ selected_location.name }}
  - HEADING (H1): Stock Opname — {{ selected_location.name }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Import CSV: Import CSV
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_opname_locations.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_opname_locations.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=42, interactive=15, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {# ── HEADER ────────────────────────────────────────────…
  - ALPINE COMPONENT [opnameLocations()]: {# ── HEADER ───────────────────────────────────────────────…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Stock Opname
  - [ ORDERED LIST ]: Dashboard / Stock Opname
  - HEADING (H1): Stock Opname
  - BUTTON: Tambah Lokasi: Tambah Lokasi
  - LAYOUT CONTAINER [FLEX (column)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_planning.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_planning.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=70, interactive=13, issues=4, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} Dashboard / Stock Planning Stock Planning Ajukan perminta…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Stock Planning
  - HEADING (H1): Stock Planning
  - BUTTON: Draft Order: Draft Order
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-[11px] font-bold text-indigo-500 hover:text-i'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='btn-submit mt-4 disabled:opacity-40'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full mt-2 py-1.5 rounded-lg text-[10px] font-bol'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/stock_purchasing.html
- File: `lumra_config/templates/lumra_pages/inventory/stock_purchasing.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=70, interactive=13, issues=4, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} Dashboard / Purchasing Purchasing Management Susun Purcha…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Purchasing
  - HEADING (H1): Purchasing Management
  - BUTTON: Draft Order: Draft Order
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-[11px] font-bold text-indigo-500 hover:text-i'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='btn-submit mt-4 disabled:opacity-40'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full mt-2 py-1.5 rounded-lg text-[10px] font-bol'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/supplier_price_list.html
- File: `lumra_config/templates/lumra_pages/inventory/supplier_price_list.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=47, interactive=17, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {% csrf_token %} Dashboard / Supplier Prices Supplier Pri…
  - ALPINE COMPONENT [supplierPriceManager()]: {% csrf_token %} Dashboard / Supplier Prices Supplier Price…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Supplier Prices
  - [ ORDERED LIST ]: Dashboard / Supplier Prices
  - HEADING (H1): Supplier Price List
  - BUTTON: Tambah Harga: Tambah Harga
  - [ FORM ]: Cari supplier, produk, atau harga Filter supplier Semua Supplier Filter Reset
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/inventory/warehouse_zone_form.html
- File: `lumra_config/templates/lumra_pages/inventory/warehouse_zone_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=19, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: Tambah Zona Baru Tentukan area penyimpanan fisik barang Tipe Penyimpanan Rack Ra…
  - HEADING (H1): Tambah Zona Baru
  - [ FORM ]: Tipe Penyimpanan Rack Rak Cold Dingin Frozen Beku Kode Zona Nama Area Lokasi Fis…
  - LAYOUT CONTAINER [GRID 3 cols]: 
  - CARD: Rack Rak
  - CARD: Cold Dingin
  - CARD: Frozen Beku
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### products_view
- File: `lumra_config/views/inventory_views.py`:522
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def products_view(request):
    _ensure_user_profile(request)

    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    stock_filter = request.GET.get("stock", "").strip()
    status_filter = request.GET.get("status", "").strip()
    page_size = min(max(_parse_int(request.GET.get("page_size", "50"), 50), 10), 200)
    low_stock_threshold = 10

    total_products = Product.objects.only("id").count()
    total_sku = ProductVariant.objects.only("id").count()
    categories = Category.objects.filter(is_active=True).order_by("name")

    if total_products == 0:
        ctx = create_empty_context("Products", "Data produk tidak ditemukan. Silahkan tambah produk terlebih dahulu.")
        ctx.update({
            "categories": categories,
            "page_obj": Paginator([], page_size).get_page(1),
            "total_products": 0,
            "filtered_total": 0,
            "low_stock_count": 0,
            "out_of_stock_count": 0,
            "average_price": 0,
            "total_sku": 0,
            "query": q,
            "selected_category": category_id,
            "selected_stock": stock_filter,
            "selected_status": status_filter,
            "page_size": page_size,
            "export_query": "",
            "page_window": [],
            "page_low_stock_count": 0,
            "page_out_of_stock_count": 0,
            "page_average_price": 0,
        })
        return render(request, "lumra_pages/inventory/products.html", ctx)

    products_qs = Product.objects.select_related("category", "vendor").order_by("name")
    filtered_qs = products_qs

    if q:
        filtered_qs = filtered_qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(barcode__icontains=q) |
            Q(variants__sku__icontains=q)
        ).distinct()

    if category_id:
        filtered_qs = filtered_qs.filter(category_id=category_id)

    if status_filter == "active":
        filtered_qs = filtered_qs.filter(is_active=True)
    elif status_filter == "inactive":
        filtered_qs = filtered_qs.filter(is_active=False)

    if stock_filter:
        variants_with_stock = _variants_with_stock_qs()
        if stock_filter == "out":
            matching_product_ids = variants_with_stock.filter(net_stock__lte=0).values_list("product_id", flat=True)
        elif stock_filter == "low":
            matching_product_ids = variants_with_stock.filter(
                net_stock__gt=0,
                net_stock__lt=low_stock_threshold,
            ).values_list("product_id", flat=True)
        else:
            matching_product_ids = variants_with_stock.filter(
                net_stock__gte=low_stock_threshold
            ).values_list("product_id", flat=True)
        filtered_qs = filtered_qs.filter(id__in=matching_product_ids).distinct()

    if request.GET.get("export") == "csv":
        return _product_csv_response(filtered_qs)

    filtered_total = filtered_qs.count()
    paginator = Paginator(filtered_qs, page_size)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_products = list(page_obj.object_list)
    page_product_ids = [product.id for product in page_products]

    variants_by_product = {product_id: [] for product_id in page_product_ids}
    page_low_stock_count = 0
    page_out_of_stock_count = 0
    page_average_price = 0

    if page_product_ids:
        page_variants = list(
            _variants_with_stock_qs()
            .filter(product_id__in=page_product_ids)
            .order_by("product_id", "sku")
        )
        total_sell_price = 0
        has_low_stock = set()
        has_out_of_stock = set()

        for variant in page_variants:
            variants_by_product.setdefault(variant.product_id, []).append(variant)
            total_sell_price += float(variant.price_sell or 0)
            if (variant.net_stock or 0) <= 0:
                has_out_of_stock.add(variant.product_id)
            elif (variant.net_stock or 0) < low_stock_threshold:
                has_low_stock.add(variant.product_id)

        for product in page_products:
            product.variants_with_stock = variants_by_product.get(product.id, [])

        page_low_stock_count = len(has_low_stock)
        page_out_of_stock_count = len(has_out_of_stock)
        if page_variants:
            page_average_price = total_sell_price / len(page_variants)
    else:
        for product in page_products:
            product.variants_with_stock = []

    page_obj.object_list = page_products

    query_dict = request.GET.copy()
    query_dict.pop("page", None)
    query_dict["export"] = "csv"

    context = {
        "report_title": "Products",
        "is_empty": False,
        "page_obj": page_obj,
        "categories": categories,
        "total_products": total_products,
        "filtered_total": filtered_total,
        "low_stock_count": page_low_stock_count,
        "out_of_stock_count": page_out_of_stock_count,
        "average_price": page_average_price,
        "total_sku": total_sku,
        "low_stock_threshold": low_stock_threshold,
        "query": q,
        "selected_category": category_id,
        "selected_stock": stock_filter,
        "selected_status": status_filter,
        "page_size": page_size,
        "export_query": query_dict.urlencode(),
        "page_window": _page_window(page_obj),
        "page_low_stock_count": page_low_stock_count,
        "page_out_of_stock_count": page_out_of_stock_count,
        "page_average_price": page_average_price,
    }
    return render(request, "lumra_pages/inventory/products.html", context)
```

### products_view
- File: `lumra_config/views/inventory_views.py`:630
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def products_view(request):
    _ensure_user_profile(request)

    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    stock_filter = request.GET.get("stock", "").strip()
    status_filter = request.GET.get("status", "").strip()
    page_size = min(max(_parse_int(request.GET.get("page_size", "50"), 50), 10), 200)
    low_stock_threshold = 10

    total_products = Product.objects.only("id").count()
    total_sku = ProductVariant.objects.only("id").count()
    categories = Category.objects.filter(is_active=True).order_by("name")

    if total_products == 0:
        ctx = create_empty_context("Products", "Data produk tidak ditemukan. Silahkan tambah produk terlebih dahulu.")
        ctx.update({
            "categories": categories,
            "page_obj": Paginator([], page_size).get_page(1),
            "total_products": 0,
            "filtered_total": 0,
            "low_stock_count": 0,
            "out_of_stock_count": 0,
            "average_price": 0,
            "total_sku": 0,
            "query": q,
            "selected_category": category_id,
            "selected_stock": stock_filter,
            "selected_status": status_filter,
            "page_size": page_size,
            "export_query": "",
            "page_window": [],
            "page_low_stock_count": 0,
            "page_out_of_stock_count": 0,
            "page_average_price": 0,
        })
        return render(request, "lumra_pages/inventory/products.html", ctx)

    products_qs = Product.objects.select_related("category", "vendor").order_by("name")
    filtered_qs = products_qs

    if q:
        filtered_qs = filtered_qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(barcode__icontains=q) |
            Q(variants__sku__icontains=q)
        ).distinct()

    if category_id:
        filtered_qs = filtered_qs.filter(category_id=category_id)

    if status_filter == "active":
        filtered_qs = filtered_qs.filter(is_active=True)
    elif status_filter == "inactive":
        filtered_qs = filtered_qs.filter(is_active=False)

    if stock_filter:
        variants_with_stock = _variants_with_stock_qs()
        if stock_filter == "out":
            matching_product_ids = variants_with_stock.filter(net_stock__lte=0).values_list("product_id", flat=True)
        elif stock_filter == "low":
            matching_product_ids = variants_with_stock.filter(
                net_stock__gt=0,
                net_stock__lt=low_stock_threshold,
            ).values_list("product_id", flat=True)
        else:
            matching_product_ids = variants_with_stock.filter(
                net_stock__gte=low_stock_threshold
            ).values_list("product_id", flat=True)
        filtered_qs = filtered_qs.filter(id__in=matching_product_ids).distinct()

    if request.GET.get("export") == "csv":
        return _product_csv_response(filtered_qs)

    filtered_total = filtered_qs.count()
    paginator = Paginator(filtered_qs, page_size)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_products = list(page_obj.object_list)
    page_product_ids = [product.id for product in page_products]

    variants_by_product = {product_id: [] for product_id in page_product_ids}
    page_low_stock_count = 0
    page_out_of_stock_count = 0
    page_average_price = 0

    if page_product_ids:
        page_variants = list(
            _variants_with_stock_qs()
            .filter(product_id__in=page_product_ids)
            .order_by("product_id", "sku")
        )
        total_sell_price = 0
        has_low_stock = set()
        has_out_of_stock = set()

        for variant in page_variants:
            variants_by_product.setdefault(variant.product_id, []).append(variant)
            total_sell_price += float(variant.price_sell or 0)
            if (variant.net_stock or 0) <= 0:
                has_out_of_stock.add(variant.product_id)
            elif (variant.net_stock or 0) < low_stock_threshold:
                has_low_stock.add(variant.product_id)

        for product in page_products:
            product.variants_with_stock = variants_by_product.get(product.id, [])

        page_low_stock_count = len(has_low_stock)
        page_out_of_stock_count = len(has_out_of_stock)
        if page_variants:
            page_average_price = total_sell_price / len(page_variants)
    else:
        for product in page_products:
            product.variants_with_stock = []

    page_obj.object_list = page_products

    query_dict = request.GET.copy()
    query_dict.pop("page", None)
    query_dict["export"] = "csv"

    context = {
        "report_title": "Products",
        "is_empty": False,
        "page_obj": page_obj,
        "categories": categories,
        "total_products": total_products,
        "filtered_total": filtered_total,
        "low_stock_count": page_low_stock_count,
        "out_of_stock_count": page_out_of_stock_count,
        "average_price": page_average_price,
        "total_sku": total_sku,
        "low_stock_threshold": low_stock_threshold,
        "query": q,
        "selected_category": category_id,
        "selected_stock": stock_filter,
        "selected_status": status_filter,
        "page_size": page_size,
        "export_query": query_dict.urlencode(),
        "page_window": _page_window(page_obj),
        "page_low_stock_count": page_low_stock_count,
        "page_out_of_stock_count": page_out_of_stock_count,
        "page_average_price": page_average_price,
    }
    return render(request, "lumra_pages/inventory/products.html", context)
```

### product_detail_view
- File: `lumra_config/views/inventory_views.py`:822
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def product_detail_view(request, product_id):
    """
    Product detail with per-variant net stock.

    Optimisations vs. original:
    - Stock aggregated in a single bulk query (dict lookup), not N loops
    - Net stock calculated correctly (inbound − outbound)
    """

    product = get_object_or_404(
        Product.objects.select_related("category", "vendor", "tax", "unit")
                       .prefetch_related("variants__attributes"),
        id=product_id,
    )

    # Single bulk aggregate for all variants of this product
    variant_ids = list(product.variants.values_list("id", flat=True))

    inbound_qs = (
        Stock.objects
        .filter(
            variant_id__in=variant_ids,
            transaction_type__in=("in", "transfer_received", "adjustment"),
        )
        .values("variant_id")
        .annotate(total=Sum("quantity"))
    )
    outbound_qs = (
        Stock.objects
        .filter(
            variant_id__in=variant_ids,
            transaction_type__in=("out", "transfer_sent"),
        )
        .values("variant_id")
        .annotate(total=Sum("quantity"))
    )

    inbound_map  = {row["variant_id"]: row["total"] for row in inbound_qs}
    outbound_map = {row["variant_id"]: row["total"] for row in outbound_qs}

    for variant in product.variants.all():
        net = (inbound_map.get(variant.id) or 0) - (outbound_map.get(variant.id) or 0)
        variant._cached_total_stock = net

    context = {
        "product":      product,
        "report_title": f"Product Detail - {product.name}",
    }

    return render(request, "lumra_pages/inventory/product_details.html", context)
```

### stock_planning_view
- File: `lumra_config/views/inventory_views.py`:872
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_planning_view(request):
    """
    Stock planning / allocation view.

    Optimisations vs. original:
    - annotated_total_stock assigned directly to _cached_total_stock
      without a second per-object query
    - Net stock annotation (inbound − outbound) instead of raw Sum
    """

    q = request.GET.get("q", "").strip()

    variants = (
        ProductVariant.objects
        .select_related("product")
        .annotate(
            inbound=Sum(
                "stock_entries__quantity",
                filter=Q(stock_entries__transaction_type__in=(
                    "in", "transfer_received", "adjustment"
                )),
            ),
            outbound=Sum(
                "stock_entries__quantity",
                filter=Q(stock_entries__transaction_type__in=(
                    "out", "transfer_sent"
                )),
            ),
        )
        .order_by("sku")
    )

    if q:
        variants = variants.filter(
            Q(sku__icontains=q) | Q(product__name__icontains=q)
        )

    # Check if variants is empty
    if not variants.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_planning.html",
            create_empty_context("Stock Planning", "Data varian produk tidak ditemukan. Silahkan tambah produk dan varian terlebih dahulu.")
        )

    paginator = Paginator(variants, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))
    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan Model.objects.select_related('...').prefetch_related('...')
 # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')

    # Cache net stock — no extra queries
    for v in page_obj.object_list:
        v._cached_total_stock = (v.inbound or 0) - (v.outbound or 0)

    requisition_count = Requisition.objects.filter(
        requested_by=request.user
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan Model.objects.select_related('...').prefetch_related('...')
    # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
    ).count()

    context = {
        "page_obj":          page_obj,
        "locations":         Location.objects.all().order_by("name"),
        "requisition_count": requisition_count,
        "query":             q,
        "report_title":      "Stock Planning",
        "is_empty": False,
    }

    return render(request, "lumra_pages/inventory/stock_planning.html", context)
```

### stock_planning_view
- File: `lumra_config/views/inventory_views.py`:909
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_planning_view(request):
    """
    Stock planning / allocation view.

    Optimisations vs. original:
    - annotated_total_stock assigned directly to _cached_total_stock
      without a second per-object query
    - Net stock annotation (inbound − outbound) instead of raw Sum
    """

    q = request.GET.get("q", "").strip()

    variants = (
        ProductVariant.objects
        .select_related("product")
        .annotate(
            inbound=Sum(
                "stock_entries__quantity",
                filter=Q(stock_entries__transaction_type__in=(
                    "in", "transfer_received", "adjustment"
                )),
            ),
            outbound=Sum(
                "stock_entries__quantity",
                filter=Q(stock_entries__transaction_type__in=(
                    "out", "transfer_sent"
                )),
            ),
        )
        .order_by("sku")
    )

    if q:
        variants = variants.filter(
            Q(sku__icontains=q) | Q(product__name__icontains=q)
        )

    # Check if variants is empty
    if not variants.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_planning.html",
            create_empty_context("Stock Planning", "Data varian produk tidak ditemukan. Silahkan tambah produk dan varian terlebih dahulu.")
        )

    paginator = Paginator(variants, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))
    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan Model.objects.select_related('...').prefetch_related('...')
 # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')

    # Cache net stock — no extra queries
    for v in page_obj.object_list:
        v._cached_total_stock = (v.inbound or 0) - (v.outbound or 0)

    requisition_count = Requisition.objects.filter(
        requested_by=request.user
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # TODO[C5-N1]: Pindahkan query ini ke atas loop.
    # Gunakan Model.objects.select_related('...').prefetch_related('...')
    # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
    ).count()

    context = {
        "page_obj":          page_obj,
        "locations":         Location.objects.all().order_by("name"),
        "requisition_count": requisition_count,
        "query":             q,
        "report_title":      "Stock Planning",
        "is_empty": False,
    }

    return render(request, "lumra_pages/inventory/stock_planning.html", context)
```

### batch_list
- File: `lumra_config/views/logistics_views.py`:91
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def batch_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()  # fresh|warning|expired

    batches = InventoryBatch.objects.select_related("variant", "variant__product", "location").all()
    if query:
        batches = batches.filter(
            Q(code__icontains=query)
            | Q(variant__sku__icontains=query)
            | Q(variant__product__name__icontains=query)
        )

    today = date.today()
    warning_threshold = today + timedelta(days=30)

    def _status_for(expiry_date):
        if not expiry_date:
            return "fresh"
        if expiry_date < today:
            return "expired"
        if expiry_date <= warning_threshold:
            return "warning"
        return "fresh"

    batch_rows = []
    for b in batches.order_by("-created_at")[:500]:
        batch_rows.append({
            "id": b.id,
            "code": b.code,
            "product": b.variant.product.name if b.variant and b.variant.product else b.variant.sku,
            "sku": b.variant.sku,
            "qty": b.quantity_on_hand,
            "prod_date": b.production_date.isoformat() if b.production_date else "",
            "exp_date": b.expiry_date.isoformat() if b.expiry_date else "",
            "status": _status_for(b.expiry_date),
            "location": b.location.name,
        })

    if status_filter in {"fresh", "warning", "expired"}:
        batch_rows = [r for r in batch_rows if r["status"] == status_filter]

    context = {"batches_data": batch_rows, "report_title": "Batch & Lot Tracking"}
    return render(request, "lumra_pages/inventory/batch_list.html", context)
```

### batch_form
- File: `lumra_config/views/logistics_views.py`:152
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def batch_form(request, pk=None):
    batch = get_object_or_404(InventoryBatch, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["variant_id", "location_id", "code", "quantity_on_hand"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        variant = get_object_or_404(ProductVariant, pk=payload["variant_id"])
        location = get_object_or_404(Location, pk=payload["location_id"])
        zone = None
        if payload.get("zone_id"):
            zone = get_object_or_404(WarehouseZone, pk=payload["zone_id"])

        if batch:
            obj = batch
        else:
            obj = InventoryBatch(created_by=request.user)

        obj.variant = variant
        obj.location = location
        obj.zone = zone
        obj.code = str(payload["code"]).strip()
        obj.quantity_on_hand = int(payload["quantity_on_hand"] or 0)
        obj.production_date = _parse_iso_date(payload.get("production_date"))
        obj.expiry_date = _parse_iso_date(payload.get("expiry_date"))
        obj.notes = payload.get("notes", "").strip()
        obj.save()

        return JsonResponse({"success": True, "id": obj.id})

    variants = ProductVariant.objects.select_related("product").order_by("sku")[:1000]
    locations = Location.objects.order_by("name")
    zones = WarehouseZone.objects.select_related("location").filter(is_active=True).order_by("location__name", "code")

    context = {
        "is_edit": bool(batch),
        "batch_id": batch.id if batch else None,
        "variants_data": [
            {"id": v.id, "sku": v.sku, "product": v.product.name if v.product else v.sku}
            for v in variants
        ],
        "locations_data": [{"id": l.id, "name": l.name} for l in locations],
        "zones_data": [
            {"id": z.id, "location_id": z.location_id, "code": z.code, "name": z.name}
            for z in zones
        ],
        "submit_url": request.path,
        "list_url": "/inventory/batch/",
        "report_title": "Input Batch",
    }
    return render(request, "lumra_pages/inventory/batch_form.html", context)
```

### batch_detail
- File: `lumra_config/views/logistics_views.py`:175
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def batch_detail(request, pk):
    batch = get_object_or_404(
        InventoryBatch.objects.select_related("variant", "variant__product", "location", "zone"),
        pk=pk,
    )
    data = {
        "id": batch.id,
        "code": batch.code,
        "sku": batch.variant.sku,
        "product": batch.variant.product.name if batch.variant.product else batch.variant.sku,
        "qty": batch.quantity_on_hand,
        "location": batch.location.name,
        "zone": batch.zone.code if batch.zone else "",
        "production_date": batch.production_date.isoformat() if batch.production_date else "",
        "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else "",
        "created_at": localtime(batch.created_at).strftime("%Y-%m-%d %H:%M"),
        "notes": batch.notes,
    }
    context = {"batch_data": data, "report_title": f"Batch Detail - {batch.code}"}
    return render(request, "lumra_pages/inventory/batch_detail.html", context)
```

### expiry_tracking
- File: `lumra_config/views/logistics_views.py`:200
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def expiry_tracking(request):
    today = date.today()
    horizon = today + timedelta(days=90)

    batches = (
        InventoryBatch.objects
        .select_related("variant", "variant__product", "location")
        .filter(expiry_date__isnull=False, expiry_date__lte=horizon)
        .order_by("expiry_date")
    )
    rows = [{
        "id": b.id,
        "code": b.code,
        "sku": b.variant.sku,
        "product": b.variant.product.name if b.variant.product else b.variant.sku,
        "location": b.location.name,
        "qty": b.quantity_on_hand,
        "expiry_date": b.expiry_date.isoformat() if b.expiry_date else "",
    } for b in batches[:1000]]

    context = {"batches_data": rows, "report_title": "Expiry Tracking"}
    return render(request, "lumra_pages/inventory/expiry_tracking.html", context)
```

### requisition_list
- File: `lumra_config/views/logistics_views.py`:235
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def requisition_list(request):
    query = request.GET.get("q", "").strip()

    qs = (
        Requisition.objects
        .select_related("from_location", "to_location", "requested_by", "approved_by")
        .order_by("-created_at")
    )
    if query:
        qs = qs.filter(
            Q(id__icontains=query)
            | Q(from_location__name__icontains=query)
            | Q(to_location__name__icontains=query)
        )

    rows = []
    for r in qs[:500]:
        rows.append({
            "pk": r.pk,
            "code": f"REQ-{r.pk:06d}",
            "from": r.from_location.name,
            "to": r.to_location.name,
            "status": r.status,
            "date": localtime(r.created_at).strftime("%Y-%m-%d"),
        })

    context = {"requisitions_data": rows, "report_title": "Requisitions"}
    return render(request, "lumra_pages/inventory/requisition_list.html", context)
```

### requisition_form
- File: `lumra_config/views/logistics_views.py`:312
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def requisition_form(request, pk=None):
    requisition = get_object_or_404(Requisition, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["from_location_id", "to_location_id", "items"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        from_location = get_object_or_404(Location, pk=payload["from_location_id"])
        to_location = get_object_or_404(Location, pk=payload["to_location_id"])
        items = payload["items"]
        if not isinstance(items, list) or len(items) == 0:
            return JsonResponse({"success": False, "error": "Items must be a non-empty list."}, status=400)

        with transaction.atomic():
            if requisition:
                req_obj = requisition
                req_obj.from_location = from_location
                req_obj.to_location = to_location
            else:
                req_obj = Requisition.objects.create(
                    from_location=from_location,
                    to_location=to_location,
                    requested_by=request.user,
                    status="waiting",
                )

            req_obj.save()

            if requisition:
                req_obj.items.all().delete()

            item_objs = []
            for it in items:
                variant_id = it.get("variant_id")
                qty = it.get("quantity")
                if not variant_id or not qty:
                    continue
                variant = get_object_or_404(ProductVariant, pk=variant_id)
                item_objs.append(RequisitionItem(
                    requisition=req_obj,
                    variant=variant,
                    quantity=int(qty),
                ))

            if not item_objs:
                return JsonResponse({"success": False, "error": "No valid items provided."}, status=400)

            RequisitionItem.objects.bulk_create(item_objs)

        return JsonResponse({"success": True, "pk": req_obj.pk})

    locations = Location.objects.order_by("name")
    variants = ProductVariant.objects.select_related("product").order_by("sku")[:2000]

    context = {
        "is_edit": bool(requisition),
        "requisition_pk": requisition.pk if requisition else None,
        "locations_data": [{"id": l.id, "name": l.name} for l in locations],
        "variants_data": [
            {"id": v.id, "sku": v.sku, "name": v.product.name if v.product else v.sku}
            for v in variants
        ],
        "submit_url": request.path,
        "list_url": "/inventory/requisitions/",
        "report_title": "Requisition Form",
    }
    return render(request, "lumra_pages/inventory/requisition_form.html", context)
```

### requisition_detail
- File: `lumra_config/views/logistics_views.py`:341
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def requisition_detail(request, pk):
    r = get_object_or_404(
        Requisition.objects
        .select_related("from_location", "to_location", "requested_by", "approved_by")
        .prefetch_related("items__variant", "items__variant__product"),
        pk=pk,
    )
    items = []
    for it in r.items.all():
        items.append({
            "sku": it.variant.sku,
            "name": it.variant.product.name if it.variant.product else it.variant.sku,
            "qty": it.quantity,
        })
    data = {
        "pk": r.pk,
        "code": f"REQ-{r.pk:06d}",
        "status": r.status,
        "from": r.from_location.name,
        "to": r.to_location.name,
        "created_at": localtime(r.created_at).strftime("%Y-%m-%d %H:%M"),
        "notes": "",
        "items": items,
    }
    context = {"requisition_data": data, "report_title": f"Requisition Detail - {data['code']}"}
    return render(request, "lumra_pages/inventory/requisition_detail.html", context)
```

### warehouse_zones
- File: `lumra_config/views/logistics_views.py`:363
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def warehouse_zones(request):
    zones = WarehouseZone.objects.select_related("location").order_by("location__name", "code")
    rows = [{
        "id": z.id,
        "location": z.location.name,
        "location_id": z.location_id,
        "code": z.code,
        "name": z.name,
        "zone_type": z.zone_type,
        "capacity": z.capacity,
        "is_active": z.is_active,
        "notes": z.notes,
    } for z in zones[:1000]]
    context = {"zones_data": rows, "report_title": "Warehouse Zones"}
    return render(request, "lumra_pages/inventory/warehouse_zones.html", context)
```

### warehouse_zone_form
- File: `lumra_config/views/logistics_views.py`:403
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def warehouse_zone_form(request, pk=None):
    zone = get_object_or_404(WarehouseZone, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["location_id", "code", "name", "zone_type", "capacity"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        location = get_object_or_404(Location, pk=payload["location_id"])
        obj = zone or WarehouseZone()
        obj.location = location
        obj.code = str(payload["code"]).strip()
        obj.name = str(payload["name"]).strip()
        obj.zone_type = str(payload["zone_type"]).strip() or "rack"
        obj.capacity = int(payload["capacity"] or 0)
        obj.is_active = bool(payload.get("is_active", True))
        obj.notes = str(payload.get("notes", "")).strip()
        obj.save()
        return JsonResponse({"success": True, "id": obj.id})

    locations = Location.objects.order_by("name")
    context = {
        "is_edit": bool(zone),
        "zone_id": zone.id if zone else None,
        "locations_data": [{"id": l.id, "name": l.name} for l in locations],
        "zone_types_data": [{"id": k, "label": v} for k, v in WarehouseZone.ZONE_TYPES],
        "submit_url": request.path,
        "list_url": "/warehouse/zones/",
        "report_title": "Warehouse Zone Form",
    }
    return render(request, "lumra_pages/inventory/warehouse_zone_form.html", context)
```

### adjustment_reasons
- File: `lumra_config/views/logistics_views.py`:421
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def adjustment_reasons(request):
    reasons = StockAdjustmentReason.objects.order_by("code")
    rows = [{
        "id": r.id,
        "code": r.code,
        "name": r.name,
        "description": r.description,
        "is_active": r.is_active,
    } for r in reasons[:2000]]
    context = {"reasons_data": rows, "report_title": "Adjustment Reasons"}
    return render(request, "lumra_pages/inventory/adjustment_reasons.html", context)
```

### supplier_evaluation
- File: `lumra_config/views/logistics_views.py`:455
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def supplier_evaluation(request):
    """
    Lightweight vendor performance snapshot using data currently available
    (SupplierPrice). Replace with PO/GRN-based metrics when purchasing module exists.
    """
    vendors = Vendor.objects.filter(is_active=True).order_by("name")
    # Aggregate supplier prices per vendor as a proxy
    price_stats = (
        SupplierPrice.objects.filter(is_active=True)
        .values("vendor_id")
        .annotate(
            variants_count=Count("variant_id", distinct=True),
            avg_price=Avg("unit_price"),
            preferred_count=Count("id", filter=Q(is_preferred=True)),
        )
    )
    stats_by_vendor = {row["vendor_id"]: row for row in price_stats}

    rows = []
    for v in vendors:
        s = stats_by_vendor.get(v.id, {})
        rows.append({
            "id": v.id,
            "name": v.name,
            "variants_count": int(s.get("variants_count") or 0),
            "preferred_count": int(s.get("preferred_count") or 0),
            "avg_price": float(s.get("avg_price") or 0),
        })

    context = {"vendors_data": rows, "report_title": "Supplier Evaluation"}
    return render(request, "lumra_pages/inventory/supplier_evaluation.html", context)
```

### purchasing_view
- File: `lumra_config/views/misc_views.py`:259
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def purchasing_view(request):
    """Halaman untuk manajemen pembelian."""
    # FIX: annotate langsung, tidak perlu loop manual set _cached_total_stock
    products = (
        ProductVariant.objects
        .select_related("product")
        .annotate(total_stock=Sum("stock_entries__quantity"))
        .order_by("sku")
    )

    # Check if products/variants is empty
    if not products.exists():
        return render(
            request,
            "lumra_pages/sales/purchasing.html",
            create_empty_context("Purchasing", "Data varian produk tidak ditemukan. Silahkan tambah produk terlebih dahulu.")
        )

    paginator = Paginator(products, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))

    # prepare simple JSON list of locations for the Alpine component
    locations = list(Location.objects.order_by("name").values("id","name"))

    context = {
        "page_obj":          page_obj,
        "locations":         Location.objects.order_by("name"),
        "locations_json":    json.dumps(locations),
        "requisition_count": 0,
        "is_empty": False,
    # TODO[C3-LONG]: 'sales_history_view' = 142 baris (max 30). Pecah: sales_history_view_validate(), sales_history_view_query(), sales_history_view_render()
    }
    return render(request, "lumra_pages/inventory/stock_purchasing.html", context)
```

### supplier_price_list
- File: `lumra_config/views/pricing_views.py`:69
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def supplier_price_list(request):
    """
    Menampilkan daftar harga supplier dengan filter vendor dan produk.
    """

    vendor_filter = request.GET.get("vendor")
    product_filter = request.GET.get("product")
    query = request.GET.get("q", "")

    prices = SupplierPrice.objects.select_related(
        "vendor",
        "variant",
        "variant__product"
    ).filter(is_active=True)

    # Filter vendor
    if vendor_filter:
        prices = prices.filter(vendor_id=vendor_filter)

    # Filter product
    if product_filter:
        prices = prices.filter(variant__product_id=product_filter)

    # Search query
    if query:
        prices = prices.filter(
            Q(vendor__name__icontains=query) |
            Q(variant__sku__icontains=query) |
            Q(variant__product__name__icontains=query)
        )

    prices = prices.order_by("-is_preferred", "unit_price")

    # Check if prices is empty
    if not prices.exists():
        vendors = Vendor.objects.filter(is_active=True).order_by("name")
        products = Product.objects.order_by("name")
        context = create_empty_context("Supplier Pricing", "Data harga supplier tidak ditemukan.")
        context.update({
            "vendors": vendors,
            "products": products,
            "vendor_filter": vendor_filter,
            "product_filter": product_filter,
            "query": query,
        })
        return render(request, "lumra_pages/inventory/supplier_price_list.html", context)

    paginator = Paginator(prices, 30)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    vendors = Vendor.objects.filter(is_active=True).order_by("name")
    products = Product.objects.order_by("name")

    context = {
        "prices": page_obj,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        "vendors": vendors,
        "products": products,
        "vendor_filter": vendor_filter,
        "product_filter": product_filter,
        "query": query,
        "total_prices": SupplierPrice.objects.filter(is_active=True).count(),
        "report_title": "Supplier Pricing",
        "is_empty": False,
    }

    return render(
        request,
        "lumra_pages/inventory/supplier_price_list.html",
        context
    )
```

### supplier_price_list
- File: `lumra_config/views/pricing_views.py`:92
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def supplier_price_list(request):
    """
    Menampilkan daftar harga supplier dengan filter vendor dan produk.
    """

    vendor_filter = request.GET.get("vendor")
    product_filter = request.GET.get("product")
    query = request.GET.get("q", "")

    prices = SupplierPrice.objects.select_related(
        "vendor",
        "variant",
        "variant__product"
    ).filter(is_active=True)

    # Filter vendor
    if vendor_filter:
        prices = prices.filter(vendor_id=vendor_filter)

    # Filter product
    if product_filter:
        prices = prices.filter(variant__product_id=product_filter)

    # Search query
    if query:
        prices = prices.filter(
            Q(vendor__name__icontains=query) |
            Q(variant__sku__icontains=query) |
            Q(variant__product__name__icontains=query)
        )

    prices = prices.order_by("-is_preferred", "unit_price")

    # Check if prices is empty
    if not prices.exists():
        vendors = Vendor.objects.filter(is_active=True).order_by("name")
        products = Product.objects.order_by("name")
        context = create_empty_context("Supplier Pricing", "Data harga supplier tidak ditemukan.")
        context.update({
            "vendors": vendors,
            "products": products,
            "vendor_filter": vendor_filter,
            "product_filter": product_filter,
            "query": query,
        })
        return render(request, "lumra_pages/inventory/supplier_price_list.html", context)

    paginator = Paginator(prices, 30)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    vendors = Vendor.objects.filter(is_active=True).order_by("name")
    products = Product.objects.order_by("name")

    context = {
        "prices": page_obj,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        "vendors": vendors,
        "products": products,
        "vendor_filter": vendor_filter,
        "product_filter": product_filter,
        "query": query,
        "total_prices": SupplierPrice.objects.filter(is_active=True).count(),
        "report_title": "Supplier Pricing",
        "is_empty": False,
    }

    return render(
        request,
        "lumra_pages/inventory/supplier_price_list.html",
        context
    )
```

### supplier_price_form
- File: `lumra_config/views/pricing_views.py`:142
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def supplier_price_form(request):
    """
    Tambah atau edit supplier pricing.
    """

    price_id = request.GET.get("id")

    if price_id:
        supplier_price = get_object_or_404(SupplierPrice, id=price_id)
        is_edit = True
    else:
        supplier_price = None
        is_edit = False

    if request.method == "POST":
        form = SupplierPriceForm(request.POST, instance=supplier_price)

        if form.is_valid():
            model_instance = form.save(commit=False)
            obj.last_updated_by = request.user
            obj.save()

            messages.success(request, "Supplier price saved successfully!")
            return redirect("supplier_price_list")

    else:
        form = SupplierPriceForm(instance=supplier_price)

    context = {
        "form": form,
        "is_edit": is_edit,
        "supplier_price": supplier_price,
        "report_title": "Edit Supplier Price" if is_edit else "Add Supplier Price",
    }

    return render(
        request,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        "lumra_pages/inventory/supplier_price_form.html",
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        context
    )
```

### supplier_price_delete
- File: `lumra_config/views/pricing_views.py`:174
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def supplier_price_delete(request, price_id):
    """
    Delete supplier pricing.
    """

    supplier_price = get_object_or_404(SupplierPrice, id=price_id)

    if request.method == "POST":
        supplier_price.delete()
        messages.success(request, "Supplier price deleted successfully!")
        return redirect("supplier_price_list")

    context = {
        "supplier_price": supplier_price,
        "report_title": "Delete Supplier Price",
    }

    return render(
        request,
        "lumra_pages/inventory/supplier_price_confirm_delete.html",
        context
    )
```

### stock_movement_view
- File: `lumra_config/views/stock_movement_views.py`:68
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_movement_view(request):
    """List stock movement entries with filters for search, type, and date."""

    qs = Stock.objects.select_related(
        "variant__product", "location"
    ).order_by("-created_at")

    # ── Filters ──────────────────────────────────────
    q            = request.GET.get("q", "").strip()
    type_filter  = request.GET.get("type", "").strip()
    start_date   = request.GET.get("start_date", "").strip()
    end_date     = request.GET.get("end_date", "").strip()

    if q:
        qs = qs.filter(
            Q(variant__sku__icontains=q)           |  # FIX: tambah SKU search
            Q(variant__product__name__icontains=q) |
            Q(notes__icontains=q)
        )

    # FIX: whitelist tipe transaksi — cegah filter injection
    if type_filter and type_filter in VALID_TXN_TYPES:
        qs = qs.filter(transaction_type=type_filter)

    # FIX: validasi format tanggal sebelum dipakai ke ORM
    if start_date and parse_date(start_date):
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date and parse_date(end_date):
        qs = qs.filter(created_at__date__lte=end_date)

    # Check if stock movements is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_movement.html",
            create_empty_context("Stock Movement", "Data pergerakan stok tidak ditemukan.")
        )

    # ── Metrics (dihitung dari qs sebelum paginate) ──
    # FIX: gabungkan 3 query count + 1 aggregate → 1 query
    aggregated = qs.aggregate(
        stock_in_qty=Sum(
            Case(When(transaction_type=TXN_IN, then=F("quantity")),
                 default=0, output_field=IntegerField())
        ),
        stock_out_qty=Sum(
            Case(When(transaction_type=TXN_OUT, then=F("quantity")),
                 default=0, output_field=IntegerField())
        ),
        net=Sum(
            Case(
                When(transaction_type=TXN_IN,  then=F("quantity")),
                When(transaction_type=TXN_OUT, then=-F("quantity")),
                default=0,
                output_field=IntegerField(),
            )
        ),
    )
    total_movements  = qs.count()
    stock_in_count   = aggregated["stock_in_qty"]  or 0
    stock_out_count  = aggregated["stock_out_qty"] or 0
    net_change       = aggregated["net"]           or 0

    # ── Pagination ───────────────────────────────────
    paginator  = Paginator(qs, PAGE_SIZE)
    page_obj   = paginator.get_page(request.GET.get("page"))

    # FIX: hapus loop rebuild dict — kirim queryset langsung ke template
    # Template tinggal pakai: movement.variant.product.name, movement.created_at, dst.

    context = {
        "movements":      page_obj,          # langsung queryset, bukan list dict
        "page_obj":       page_obj,
        "is_paginated":   page_obj.has_other_pages(),
        "total_movements": total_movements,
        "stock_in_count":  stock_in_count,
        "stock_out_count": stock_out_count,
        "net_change":      net_change,
        "query":           q,
        "type":            type_filter,
        "start_date":      start_date,
        "end_date":        end_date,
        "valid_txn_types": sorted(VALID_TXN_TYPES),  # untuk dropdown template
        "report_title":    "Stock Movement",
        "is_empty": False,
    }
    return render(request, "lumra_pages/inventory/stock_movement.html", context)
```

### stock_movement_view
- File: `lumra_config/views/stock_movement_views.py`:122
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_movement_view(request):
    """List stock movement entries with filters for search, type, and date."""

    qs = Stock.objects.select_related(
        "variant__product", "location"
    ).order_by("-created_at")

    # ── Filters ──────────────────────────────────────
    q            = request.GET.get("q", "").strip()
    type_filter  = request.GET.get("type", "").strip()
    start_date   = request.GET.get("start_date", "").strip()
    end_date     = request.GET.get("end_date", "").strip()

    if q:
        qs = qs.filter(
            Q(variant__sku__icontains=q)           |  # FIX: tambah SKU search
            Q(variant__product__name__icontains=q) |
            Q(notes__icontains=q)
        )

    # FIX: whitelist tipe transaksi — cegah filter injection
    if type_filter and type_filter in VALID_TXN_TYPES:
        qs = qs.filter(transaction_type=type_filter)

    # FIX: validasi format tanggal sebelum dipakai ke ORM
    if start_date and parse_date(start_date):
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date and parse_date(end_date):
        qs = qs.filter(created_at__date__lte=end_date)

    # Check if stock movements is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_movement.html",
            create_empty_context("Stock Movement", "Data pergerakan stok tidak ditemukan.")
        )

    # ── Metrics (dihitung dari qs sebelum paginate) ──
    # FIX: gabungkan 3 query count + 1 aggregate → 1 query
    aggregated = qs.aggregate(
        stock_in_qty=Sum(
            Case(When(transaction_type=TXN_IN, then=F("quantity")),
                 default=0, output_field=IntegerField())
        ),
        stock_out_qty=Sum(
            Case(When(transaction_type=TXN_OUT, then=F("quantity")),
                 default=0, output_field=IntegerField())
        ),
        net=Sum(
            Case(
                When(transaction_type=TXN_IN,  then=F("quantity")),
                When(transaction_type=TXN_OUT, then=-F("quantity")),
                default=0,
                output_field=IntegerField(),
            )
        ),
    )
    total_movements  = qs.count()
    stock_in_count   = aggregated["stock_in_qty"]  or 0
    stock_out_count  = aggregated["stock_out_qty"] or 0
    net_change       = aggregated["net"]           or 0

    # ── Pagination ───────────────────────────────────
    paginator  = Paginator(qs, PAGE_SIZE)
    page_obj   = paginator.get_page(request.GET.get("page"))

    # FIX: hapus loop rebuild dict — kirim queryset langsung ke template
    # Template tinggal pakai: movement.variant.product.name, movement.created_at, dst.

    context = {
        "movements":      page_obj,          # langsung queryset, bukan list dict
        "page_obj":       page_obj,
        "is_paginated":   page_obj.has_other_pages(),
        "total_movements": total_movements,
        "stock_in_count":  stock_in_count,
        "stock_out_count": stock_out_count,
        "net_change":      net_change,
        "query":           q,
        "type":            type_filter,
        "start_date":      start_date,
        "end_date":        end_date,
        "valid_txn_types": sorted(VALID_TXN_TYPES),  # untuk dropdown template
        "report_title":    "Stock Movement",
        "is_empty": False,
    }
    return render(request, "lumra_pages/inventory/stock_movement.html", context)
```

### export_stock_movement
- File: `lumra_config/views/stock_movement_views.py`:139
- Decorators: `login_required`
- Context keys eksplisit: `error`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def export_stock_movement(request):
    """Stub endpoint for exporting stock movement data.

    The front‑end links here with ``?format=csv`` or ``?format=excel``.
    This view currently performs basic validation and returns a placeholder
    response; replace with real CSV/Excel generation logic as needed.
    """
    fmt = request.GET.get("format", "csv").lower()
    if fmt not in ("csv", "excel"):
        return render(request, "lumra_pages/inventory/stock_movement.html", {
            "error": f"Format ekspor tidak dikenal: {fmt}",
        })

    # TODO: query the same filters as ``stock_movement_view`` and emit a file
    return render(request, "lumra_pages/inventory/stock_movement.html", {
        "info": f"Ekspor '{fmt}' belum diimplementasi."
    })
```

### export_stock_movement
- File: `lumra_config/views/stock_movement_views.py`:144
- Decorators: `login_required`
- Context keys eksplisit: `info`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def export_stock_movement(request):
    """Stub endpoint for exporting stock movement data.

    The front‑end links here with ``?format=csv`` or ``?format=excel``.
    This view currently performs basic validation and returns a placeholder
    response; replace with real CSV/Excel generation logic as needed.
    """
    fmt = request.GET.get("format", "csv").lower()
    if fmt not in ("csv", "excel"):
        return render(request, "lumra_pages/inventory/stock_movement.html", {
            "error": f"Format ekspor tidak dikenal: {fmt}",
        })

    # TODO: query the same filters as ``stock_movement_view`` and emit a file
    return render(request, "lumra_pages/inventory/stock_movement.html", {
        "info": f"Ekspor '{fmt}' belum diimplementasi."
    })
```

### add_stock_movement_view
- File: `lumra_config/views/stock_movement_views.py`:190
- Decorators: `login_required`
- Context keys eksplisit: `locations`, `prev`, `valid_txn_types`, `variants`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def add_stock_movement_view(request):
    """Form untuk membuat stock entry baru."""

    if request.method == "POST":
        variant_id  = request.POST.get("variant")
        location_id = request.POST.get("location")
        raw_qty     = request.POST.get("quantity", "").strip()
        txn_type    = request.POST.get("transaction_type", "").strip()
        notes       = request.POST.get("notes", "").strip()

        # ── Validasi ─────────────────────────────────
        errors = []

        if not variant_id:
            errors.append("Variant wajib dipilih.")
        if not location_id:
            errors.append("Lokasi wajib dipilih.")
        if not raw_qty or not raw_qty.lstrip("-").isdigit():
            errors.append("Quantity harus berupa angka.")
        elif int(raw_qty) <= 0:
            errors.append("Quantity harus lebih dari 0.")
        if txn_type not in VALID_TXN_TYPES:
            errors.append(f"Tipe transaksi tidak valid: {txn_type!r}")

        if errors:
            for err in errors:
                messages.error(request, err)
    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
            # Kembalikan form dengan input yang sudah diisi (tidak hilang)
            return render(request, "lumra_pages/inventory/add_stock_movement.html", {
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # Gunakan Model.objects.select_related('...').prefetch_related('...')
                # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
                "variants":        ProductVariant.objects.select_related("product").all(),
                "locations":       Location.objects.all(),
                "valid_txn_types": sorted(VALID_TXN_TYPES),
                "prev":            request.POST,   # repopulate form di template
            })

        # ── Simpan ───────────────────────────────────
        try:
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan Model.objects.select_related('...').prefetch_related('...')
            # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
            variant  = ProductVariant.objects.get(id=variant_id)
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan Model.objects.select_related('...').prefetch_related('...')
            location = Location.objects.get(id=location_id)
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
        except (ProductVariant.DoesNotExist, Location.DoesNotExist):
            messages.error(request, "Variant atau lokasi tidak ditemukan.")
            return redirect("add_stock_movement")

        Stock.objects.create(
            variant=variant,
            location=location,
            quantity=int(raw_qty),
            transaction_type=txn_type,
            notes=notes,
            # FIX: simpan user yang melakukan transaksi jika field tersedia
            # created_by=request.user,
        )

        messages.success(
            request,
            f"Stock movement ({txn_type}) untuk {variant} berhasil disimpan."
        )
        return redirect("stock_movement")

    # ── GET ───────────────────────────────────────────
    context = {
        "variants":        ProductVariant.objects.select_related("product").order_by("sku"),
        "locations":       Location.objects.order_by("name"),
        "valid_txn_types": sorted(VALID_TXN_TYPES),
    }
    return render(request, "lumra_pages/inventory/add_stock_movement.html", context)
```

### add_stock_movement_view
- File: `lumra_config/views/stock_movement_views.py`:239
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def add_stock_movement_view(request):
    """Form untuk membuat stock entry baru."""

    if request.method == "POST":
        variant_id  = request.POST.get("variant")
        location_id = request.POST.get("location")
        raw_qty     = request.POST.get("quantity", "").strip()
        txn_type    = request.POST.get("transaction_type", "").strip()
        notes       = request.POST.get("notes", "").strip()

        # ── Validasi ─────────────────────────────────
        errors = []

        if not variant_id:
            errors.append("Variant wajib dipilih.")
        if not location_id:
            errors.append("Lokasi wajib dipilih.")
        if not raw_qty or not raw_qty.lstrip("-").isdigit():
            errors.append("Quantity harus berupa angka.")
        elif int(raw_qty) <= 0:
            errors.append("Quantity harus lebih dari 0.")
        if txn_type not in VALID_TXN_TYPES:
            errors.append(f"Tipe transaksi tidak valid: {txn_type!r}")

        if errors:
            for err in errors:
                messages.error(request, err)
    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
            # Kembalikan form dengan input yang sudah diisi (tidak hilang)
            return render(request, "lumra_pages/inventory/add_stock_movement.html", {
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # Gunakan Model.objects.select_related('...').prefetch_related('...')
                # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
                "variants":        ProductVariant.objects.select_related("product").all(),
                "locations":       Location.objects.all(),
                "valid_txn_types": sorted(VALID_TXN_TYPES),
                "prev":            request.POST,   # repopulate form di template
            })

        # ── Simpan ───────────────────────────────────
        try:
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan Model.objects.select_related('...').prefetch_related('...')
            # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
            variant  = ProductVariant.objects.get(id=variant_id)
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan Model.objects.select_related('...').prefetch_related('...')
            location = Location.objects.get(id=location_id)
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
        except (ProductVariant.DoesNotExist, Location.DoesNotExist):
            messages.error(request, "Variant atau lokasi tidak ditemukan.")
            return redirect("add_stock_movement")

        Stock.objects.create(
            variant=variant,
            location=location,
            quantity=int(raw_qty),
            transaction_type=txn_type,
            notes=notes,
            # FIX: simpan user yang melakukan transaksi jika field tersedia
            # created_by=request.user,
        )

        messages.success(
            request,
            f"Stock movement ({txn_type}) untuk {variant} berhasil disimpan."
        )
        return redirect("stock_movement")

    # ── GET ───────────────────────────────────────────
    context = {
        "variants":        ProductVariant.objects.select_related("product").order_by("sku"),
        "locations":       Location.objects.order_by("name"),
        "valid_txn_types": sorted(VALID_TXN_TYPES),
    }
    return render(request, "lumra_pages/inventory/add_stock_movement.html", context)
```

### stock_opname_locations
- File: `lumra_config/views/stock_opname_views.py`:52
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_opname_locations(request):
    """Step 1: User memilih lokasi untuk opname."""

    locations = Location.objects.all().order_by("name")

    # Check if locations is empty
    if not locations.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_opname_locations.html",
            create_empty_context("Stock Opname", "Data lokasi tidak ditemukan. Silahkan tambah lokasi terlebih dahulu.")
        )

    context = {
        "locations": locations,
        "report_title": "Select Location for Stock Opname",
        "is_empty": False,
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_locations.html",
        context,
    )
```

### stock_opname_locations
- File: `lumra_config/views/stock_opname_views.py`:64
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_opname_locations(request):
    """Step 1: User memilih lokasi untuk opname."""

    locations = Location.objects.all().order_by("name")

    # Check if locations is empty
    if not locations.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_opname_locations.html",
            create_empty_context("Stock Opname", "Data lokasi tidak ditemukan. Silahkan tambah lokasi terlebih dahulu.")
        )

    context = {
        "locations": locations,
        "report_title": "Select Location for Stock Opname",
        "is_empty": False,
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_locations.html",
        context,
    )
```

### stock_opname_form
- File: `lumra_config/views/stock_opname_views.py`:254
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_opname_form(request, location_id):
    """Step 2: Input opname manual atau import CSV."""

    location = get_object_or_404(Location, pk=location_id)

    # FIX: Gunakan select_for_update-safe pattern — cari dulu, baru create
    session = (
        StockOpnameSession.objects
        .filter(location=location, created_by=request.user, status=STATUS_IN_PROGRESS)
        .first()
    )
    if not session:
        session = StockOpnameSession.objects.create(
            location=location,
            created_by=request.user,
            status=STATUS_IN_PROGRESS,
        )

    # ============================
    # HANDLE CSV IMPORT
    # ============================
    if request.method == "POST" and "import_csv" in request.POST:

        form = StockOpnameCSVImportForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            stream = io.TextIOWrapper(csv_file.file, encoding="utf-8")
            reader = csv.DictReader(stream)

            # Pre-fetch semua SKU yang relevan sekali query
            sku_list = []
            rows = list(reader)
            for row in rows:
                sku = row.get("sku", "").strip()
                if sku:
                    sku_list.append(sku)

            variants_by_sku = {
                v.sku: v
                for v in ProductVariant.objects.filter(sku__in=sku_list)
            }

            # Pre-fetch current stocks sekali query
            stocks_by_variant_id = {
                s["variant_id"]: s["total"]
                for s in Stock.objects.filter(
                    variant__sku__in=sku_list,
                    location=location,
                ).values("variant_id").annotate(total=Sum("quantity"))
            }

            opname_items_to_upsert = []
            for row in rows:
                sku        = row.get("sku", "").strip()
                notes      = row.get("notes", "").strip()

                # FIX: Safe int conversion
                try:
                    counted_qty = int(row.get("counted_qty", 0))
                except (ValueError, TypeError):
                    counted_qty = 0

                variant = variants_by_sku.get(sku)
                if not variant:
                    continue

                current_stock = stocks_by_variant_id.get(variant.id, 0)

                StockOpnameItem.objects.update_or_create(
                    session=session,
                    variant=variant,
                    defaults={
                        "current_stock": current_stock,
                        "counted_qty": counted_qty,
                        "notes": notes,
                    },
                )

            messages.success(request, "CSV berhasil diimport.")
        else:
            messages.error(request, "File CSV tidak valid.")

        return redirect("stock_opname_form", location_id=location.id)

    # ============================
    # HANDLE SUBMIT OPNAME
    # ============================
    if request.method == "POST" and "submit_opname" in request.POST:

        for key, value in request.POST.items():
            if key.startswith("counted_qty_"):
                item_id = key.replace("counted_qty_", "")

    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # Gunakan Model.objects.select_related('...').prefetch_related('...')
                try:
                    record_item = StockOpnameItem.objects.get(id=item_id, session=session)
                    item.counted_qty = int(value) if value else 0
                    item.notes = request.POST.get(f"notes_{item_id}", "")
                    item.save()
                except (StockOpnameItem.DoesNotExist, ValueError):
                    continue

        session.status = STATUS_SUBMITTED
        session.submitted_at = timezone.now()
        session.save()

        messages.success(request, "Opname berhasil disubmit, menunggu approval.")
        return redirect("stock_opname_approvals")

    # ============================
    # GET — build products_data dengan efisien (FIX N+1)
    # ============================

    q = request.GET.get("q", "").strip()

    # Filter variants sebelum pagination
    variants_qs = (
        ProductVariant.objects
        .select_related("product")
        .order_by("sku")
    )
    if q:
        variants_qs = variants_qs.filter(
            models_Q(sku__icontains=q) | models_Q(product__name__icontains=q)
        )

    # Ambil semua stock & opname items dalam 2 query, bukan N query
    all_variant_ids = list(variants_qs.values_list("id", flat=True))

    stock_map = {
        s["variant_id"]: s["total"]
        for s in Stock.objects.filter(
            variant_id__in=all_variant_ids,
            location=location,
        ).values("variant_id").annotate(total=Sum("quantity"))
    }

    item_map = {
        i.variant_id: i
        for i in StockOpnameItem.objects.filter(
            session=session,
            variant_id__in=all_variant_ids,
        )
    }

    products_data = [
        {
            "variant": var,
            "current_stock": stock_map.get(var.id, 0),
            "item": item_map.get(var.id),
        }
        for var in variants_qs
    ]

    # Pagination (search sudah diterapkan sebelum ini — FIX bug lama)
    paginator = Paginator(products_data, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "selected_location": location,
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "query": q,
        "form": StockOpnameCSVImportForm(),
        "report_title": f"Stock Opname - {location.name}",
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_form.html",
        context,
    )
```

### stock_opname_approvals
- File: `lumra_config/views/stock_opname_views.py`:297
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_opname_approvals(request):
    """Step 3: Manager/Admin melihat session opname pending."""

    status_filter = request.GET.get("status", "pending")

    if status_filter == "pending":
        sessions = StockOpnameSession.objects.filter(
            status__in=[STATUS_SUBMITTED, STATUS_IN_PROGRESS]
        )
    else:
        sessions = StockOpnameSession.objects.filter(status=status_filter)

    sessions = sessions.select_related("location", "created_by").order_by("-created_at")

    paginator = Paginator(sessions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "approvals": page_obj.object_list,
        "page_obj": page_obj,
        "status": status_filter,
        "report_title": "Stock Opname Approvals",
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_approvals.html",
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        context,
    )
```

### stock_opname_approval_detail
- File: `lumra_config/views/stock_opname_views.py`:379
- Decorators: `login_required`, `user_passes_test`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def stock_opname_approval_detail(request, session_id):
    """Step 4: Approve / Reject opname session."""

    session = get_object_or_404(StockOpnameSession, pk=session_id)
    opname_items = session.items.select_related("variant", "variant__product")

    if request.method == "POST":
        decision = request.POST.get("decision")

        # ============================
        # APPROVE
        # ============================
        if decision == "approve":
            with transaction.atomic():
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan Model.objects.select_related('...').prefetch_related('...')

                for item in opname_items:
                    # FIX: Hapus semua stock lama, replace dengan satu entry bersih
                    Stock.objects.filter(
                        variant=item.variant,
                        location=session.location,
                    ).delete()

                    Stock.objects.create(
                        variant=item.variant,
                        location=session.location,
                        quantity=item.counted_qty,
                        transaction_type="opname",
                        notes=f"Approved Opname Session #{session.id}",
                        last_updated=timezone.now(),
                    )

                session.status = STATUS_APPROVED
                session.approved_at = timezone.now()
                session.approved_by = request.user
                session.save()

            messages.success(request, f"Session #{session.id} berhasil di-approve.")
            return redirect("stock_opname_approvals")

        # ============================
        # REJECT
        # ============================
        elif decision == "reject":
            reason = request.POST.get("reason", "").strip()
            if not reason:
                messages.error(request, "Alasan penolakan wajib diisi.")
            else:
                session.status = STATUS_REJECTED
                session.notes = reason
                session.save()
                messages.warning(request, f"Session #{session.id} ditolak.")
                return redirect("stock_opname_approvals")

    context = {
        "session": session,
        "opname_data": opname_items,
        "report_title": f"Approval Detail - {session.location.name}",
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_approval_detail.html",
        context,
    )
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
