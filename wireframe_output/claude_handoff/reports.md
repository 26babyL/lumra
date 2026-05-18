# Claude Handoff: reports

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 25
Jumlah view terkait: 22

## Template Scope

### lumra_pages/reports/activity_log.html
- File: `lumra_config/templates/lumra_pages/reports/activity_log.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=26, interactive=7, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 📋 Activity Log
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Search activities...: Search activities...
  - SEARCH BAR: 
  - INPUT [select] : 

### lumra_pages/reports/sales_history.html
- File: `lumra_config/templates/lumra_pages/reports/sales_history.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=96, interactive=29, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Stock Movements {{ transfer_count|default:0 }} Transfers
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Purchases {{ requisition_count|default:0 }} Requisitions
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/base_report.html
- File: `lumra_config/templates/lumra_pages/reports/base_report.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=25, interactive=8, issues=0, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [reportManager()]: {# ── Page Title ─────────────────────────────────────── #}…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 📊 {{ report_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: ⬇️ Export CSV Exporting…: ⬇️ Export CSV Exporting…
  - BUTTON: 🖨️ Print: 🖨️ Print
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/reports/report_activity_log.html
- File: `lumra_config/templates/lumra_pages/reports/report_activity_log.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=26, interactive=7, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 📋 Activity Log
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Search activities...: Search activities...
  - SEARCH BAR: 
  - INPUT [select] : 

### lumra_pages/reports/report_inventory_log.html
- File: `lumra_config/templates/lumra_pages/reports/report_inventory_log.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_inventory_low.html
- File: `lumra_config/templates/lumra_pages/reports/report_inventory_low.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_inventory_stock.html
- File: `lumra_config/templates/lumra_pages/reports/report_inventory_stock.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_sales_by_outlet.html
- File: `lumra_config/templates/lumra_pages/reports/report_sales_by_outlet.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_sales_by_payment.html
- File: `lumra_config/templates/lumra_pages/reports/report_sales_by_payment.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_sales_by_product.html
- File: `lumra_config/templates/lumra_pages/reports/report_sales_by_product.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_sales_summary.html
- File: `lumra_config/templates/lumra_pages/reports/report_sales_summary.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/reporting.html
- File: `lumra_config/templates/lumra_pages/reports/reporting.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=43, interactive=14, issues=2, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [reportingDashboard()]: Dashboard / Reporting Dashboard Reporting Dashboard Analyze…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Reporting Dashboard
  - [ ORDERED LIST ]: Dashboard / Reporting Dashboard
  - HEADING (H1): Reporting Dashboard
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Export CSV: Export CSV
  - BUTTON: Inbox: Inbox
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:style='
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/sales_report_after.html
- File: `lumra_config/templates/lumra_pages/reports/sales_report_after.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=6, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: {% include "base/kpi_card.html" with title="Total Transaksi" value=total_transac…
  - CARD: Rincian Penjualan Export CSV Tanggal Outlet Produk Qty Total Status {% for item…
  - HEADING (H2): Rincian Penjualan
  - BUTTON: Export CSV: Export CSV
  - [ TABLE ]: Tanggal Outlet Produk Qty Total Status {% for item in sales_data %} {{ item.date…
  - BADGE / STATUS: {{ item.status }}

### lumra_pages/reports/report_customer_lifetime.html
- File: `lumra_config/templates/lumra_pages/reports/report_customer_lifetime.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=20, interactive=1, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Laporan Customer Lifetime Value
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Periode: 6 Bulan: Periode: 6 Bulan
  - CALENDAR: 
  - CARD: Total Revenue Period Total Customer Avg LTV
  - LAYOUT CONTAINER [FLEX (column)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_expiry.html
- File: `lumra_config/templates/lumra_pages/reports/report_expiry.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=17, interactive=5, issues=3, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Laporan Kedaluwarsa (Expiry)
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [date] filterDate: filterDate
  - CARD: PERHATIAN! Ada Item Kritis Produk ini akan kedaluwarsa dalam waktu kurang dari 3…
  - HEADING (H2): PERHATIAN! Ada Item Kritis
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-emerald-600 hover:bg-emeral'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-white bg-rose-600 hover:bg-'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_inventory_age.html
- File: `lumra_config/templates/lumra_pages/reports/report_inventory_age.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=16, interactive=4, issues=3, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Inventory Aging Report
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Filter Lokasi: Filter Lokasi
  - BUTTON: Export Excel: Export Excel
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Fast Moving 0 - 30 Hari
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-rose-600 hover:text-rose-80'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-amber-600 hover:text-amber-'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_production.html
- File: `lumra_config/templates/lumra_pages/reports/report_production.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=16, interactive=1, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Laporan Produksi
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [select] : 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Yield Rate Output vs Target
  - METRIC CARD: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_profit_loss_detail.html
- File: `lumra_config/templates/lumra_pages/reports/report_profit_loss_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/sales_history_product.html
- File: `lumra_config/templates/lumra_pages/reports/sales_history_product.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Routes: `history/products/` (sales_history_products), `history/products/` (sales_history_products)
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/transaction_summary.html
- File: `lumra_config/templates/lumra_pages/reports/transaction_summary.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/purchasing_report.html
- File: `lumra_config/templates/lumra_pages/reports/purchasing_report.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=89, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/report_staff_performance.html
- File: `lumra_config/templates/lumra_pages/reports/report_staff_performance.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=16, interactive=2, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Laporan Kinerja Karyawan
  - INPUT [select] : 
  - CARD: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-4 py-2 bg-slate-50 text-slate-600 rounded-lg te'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/requisition_report.html
- File: `lumra_config/templates/lumra_pages/reports/requisition_report.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/sales_report.html
- File: `lumra_config/templates/lumra_pages/reports/sales_report.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=96, interactive=29, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Stock Movements {{ transfer_count|default:0 }} Transfers
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Purchases {{ requisition_count|default:0 }} Requisitions
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/reports/transfer_report.html
- File: `lumra_config/templates/lumra_pages/reports/transfer_report.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=88, interactive=27, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Items Sold {{ total_qty|default:0 }} All items
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Revenue Rp {{ total_amount|floatformat:0|default:0 }} Invoice total
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Avg / Item Rp {% if total_qty > 0 %}{{ total_amount|div:total_qty|floatformat:0…
- Temuan reverse:
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### sales_history_products_view
- File: `lumra_config/views/misc_views.py`:434
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### sales_history_products_view
- File: `lumra_config/views/misc_views.py`:493
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### activity_log_view
- File: `lumra_config/views/misc_views.py`:1505
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def activity_log_view(request):
    context = {"activities": []}
    return render(request, "lumra_pages/reports/activity_log.html", context)
```

### sales_report
- File: `lumra_config/views/report_views.py`:73
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def sales_report(request):
    """
    Laporan Penjualan Detail
    Menampilkan semua transaksi penjualan per item
    """
    # Get date range from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default: last 30 days
    if not date_from or not date_to:
        date_to = timezone.now()
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    # Query sales detail
    sales = OrderItem.objects.filter(
        order__created_at__range=[date_from, date_to],
        order__status='completed'
    ).select_related('order', 'variant', 'variant__product').order_by('-order__created_at')
    
    # Check if sales is empty
    if not sales.exists():
        context = create_empty_context("Sales Report", "Data penjualan tidak ditemukan untuk periode yang dipilih.")
        # ensure dates are strings for template
        def _fmt(d):
            return d.strftime('%Y-%m-%d') if isinstance(d, datetime) else d
        context.update({
            'date_from': _fmt(date_from),
            'date_to': _fmt(date_to),
        })
        return render(request, 'lumra_pages/reports/sales_report.html', context)
    
    # Calculate totals
    total_qty = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_amount = sales.aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0

    # additional metrics for linking pages
    transfer_count = Transfer.objects.filter(
        created_at__range=[date_from, date_to]
    ).count()
    requisition_count = Requisition.objects.filter(
        created_at__range=[date_from, date_to]
    ).count()
    
    # Pagination
    paginator = Paginator(sales, 50)
    page_number = request.GET.get('page', 1)
    sales_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Date', 'SKU', 'Product', 'Qty', 'Price', 'Total'])
        for item in sales:
            writer.writerow([
                item.order.id,
                item.order.customer_name,
                item.order.created_at.strftime('%Y-%m-%d %H:%M'),
                item.variant.sku,
                item.variant.product.name,
                item.quantity,
                item.price,
                item.quantity * item.price
            ])
        return response
    
    context = {
        'sales': sales_page,
        'total_qty': total_qty,
        'total_amount': total_amount,
        'transfer_count': transfer_count,
        'requisition_count': requisition_count,
        'date_from': date_from.strftime('%Y-%m-%d') if hasattr(date_from, 'strftime') else date_from,
        'date_to': date_to.strftime('%Y-%m-%d') if hasattr(date_to, 'strftime') else date_to,
        'report_title': 'Sales Report',
        'is_empty': False,
    }
    return render(request, 'lumra_pages/reports/sales_report.html', context)
```

### sales_report
- File: `lumra_config/views/report_views.py`:124
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def sales_report(request):
    """
    Laporan Penjualan Detail
    Menampilkan semua transaksi penjualan per item
    """
    # Get date range from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default: last 30 days
    if not date_from or not date_to:
        date_to = timezone.now()
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    # Query sales detail
    sales = OrderItem.objects.filter(
        order__created_at__range=[date_from, date_to],
        order__status='completed'
    ).select_related('order', 'variant', 'variant__product').order_by('-order__created_at')
    
    # Check if sales is empty
    if not sales.exists():
        context = create_empty_context("Sales Report", "Data penjualan tidak ditemukan untuk periode yang dipilih.")
        # ensure dates are strings for template
        def _fmt(d):
            return d.strftime('%Y-%m-%d') if isinstance(d, datetime) else d
        context.update({
            'date_from': _fmt(date_from),
            'date_to': _fmt(date_to),
        })
        return render(request, 'lumra_pages/reports/sales_report.html', context)
    
    # Calculate totals
    total_qty = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_amount = sales.aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0

    # additional metrics for linking pages
    transfer_count = Transfer.objects.filter(
        created_at__range=[date_from, date_to]
    ).count()
    requisition_count = Requisition.objects.filter(
        created_at__range=[date_from, date_to]
    ).count()
    
    # Pagination
    paginator = Paginator(sales, 50)
    page_number = request.GET.get('page', 1)
    sales_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Date', 'SKU', 'Product', 'Qty', 'Price', 'Total'])
        for item in sales:
            writer.writerow([
                item.order.id,
                item.order.customer_name,
                item.order.created_at.strftime('%Y-%m-%d %H:%M'),
                item.variant.sku,
                item.variant.product.name,
                item.quantity,
                item.price,
                item.quantity * item.price
            ])
        return response
    
    context = {
        'sales': sales_page,
        'total_qty': total_qty,
        'total_amount': total_amount,
        'transfer_count': transfer_count,
        'requisition_count': requisition_count,
        'date_from': date_from.strftime('%Y-%m-%d') if hasattr(date_from, 'strftime') else date_from,
        'date_to': date_to.strftime('%Y-%m-%d') if hasattr(date_to, 'strftime') else date_to,
        'report_title': 'Sales Report',
        'is_empty': False,
    }
    return render(request, 'lumra_pages/reports/sales_report.html', context)
```

### transaction_summary
- File: `lumra_config/views/report_views.py`:198
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def transaction_summary(request):
    """
    Laporan Transaksi (Summary Header)
    Menampilkan ringkasan per transaksi/order
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    # Query transactions with aggregation
    transactions = Order.objects.filter(
        created_at__range=[date_from, date_to],
        status='completed'
    ).annotate(
        total_items=Count('items'),
        total_qty=Sum('items__quantity'),
        total_amount=Sum(F('items__quantity') * F('items__price'))
    ).order_by('-created_at')
    
    # Summary stats
    total_transactions = transactions.count()
    total_revenue = transactions.aggregate(Sum('items__quantity') * Sum('items__price'))['items__quantity__sum'] or 0
    
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page', 1)
    transactions_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transaction_summary.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Date', 'Items', 'Total Qty', 'Total Amount', 'Status'])
        for trans in transactions:
            writer.writerow([
                trans.id,
                trans.customer_name,
                trans.created_at.strftime('%Y-%m-%d %H:%M'),
                trans.total_items,
                trans.total_qty,
                trans.total_amount,
                trans.status
            ])
        return response
    
    context = {
        'transactions': transactions_page,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'report_title': 'Transaction Summary'
    # TODO[C3-LONG]: 'transfer_report' = 54 baris (max 30). Pecah: transfer_report_validate(), transfer_report_query(), transfer_report_render()
    }
    return render(request, 'lumra_pages/reports/transaction_summary.html', context)
```

### transfer_report
- File: `lumra_config/views/report_views.py`:276
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def transfer_report(request):
    """
    Laporan Transfer (Stock Movement Detail)
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    transfers = TransferItem.objects.filter(
        transfer__created_at__range=[date_from, date_to]
    ).select_related('transfer', 'variant', 'variant__product', 'transfer__source_location', 'transfer__destination_location').order_by('-transfer__created_at')
    
    total_items = transfers.count()
    total_qty_sent = transfers.aggregate(Sum('quantity_sent'))['quantity_sent__sum'] or 0
    
    paginator = Paginator(transfers, 50)
    page_number = request.GET.get('page', 1)
    transfers_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transfer_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Transfer ID', 'From', 'To', 'Date', 'SKU', 'Product', 'Qty Sent', 'Qty Received', 'Status'])
        for item in transfers:
            writer.writerow([
                item.transfer.id,
                item.transfer.source_location.name,
                item.transfer.destination_location.name,
                item.transfer.created_at.strftime('%Y-%m-%d %H:%M'),
                item.variant.sku,
                item.variant.product.name,
                item.quantity_sent,
                item.quantity_received or '-',
                item.transfer.status
            ])
        return response
     # TODO[C3-LONG]: 'requisition_report' = 60 baris (max 30). Pecah: requisition_report_validate(), requisition_report_query(), requisition_report_render()
    
    context = {
        'transfers': transfers_page,
        'total_items': total_items,
        'total_qty_sent': total_qty_sent,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'report_title': 'Transfer Report'
    }
    # TODO[C3-LONG]: 'requisition_report' terlalu panjang (65 baris). Pecah: requisition_report_validate(), requisition_report_build_context(), requisition_report_render()
    return render(request, 'lumra_pages/reports/transfer_report.html', context)
```

### requisition_report
- File: `lumra_config/views/report_views.py`:359
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def requisition_report(request):
    """
    Laporan Requisition (Permintaan Barang)
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status_filter = request.GET.get('status')
     # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
     # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    requisitions = RequisitionItem.objects.filter(
        requisition__created_at__range=[date_from, date_to]
    ).select_related('requisition', 'variant', 'variant__product', 'requisition__from_location', 'requisition__to_location').order_by('-requisition__created_at')
    
    if status_filter:
        requisitions = requisitions.filter(requisition__status=status_filter)
    
    total_items = requisitions.count()
    total_qty = requisitions.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    paginator = Paginator(requisitions, 50)
    page_number = request.GET.get('page', 1)
    requisitions_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="requisition_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Req ID', 'From', 'To', 'Date', 'SKU', 'Product', 'Qty', 'Status', 'Requested By'])
        for item in requisitions:
            writer.writerow([
                item.requisition.id,
                item.requisition.from_location.name,
                item.requisition.to_location.name,
                item.requisition.created_at.strftime('%Y-%m-%d %H:%M'),
                item.variant.sku,
                item.variant.product.name,
                item.quantity,
                item.requisition.status,
                item.requisition.requested_by.username
            ])
        # TODO[C3-LONG]: 'purchasing_report' = 73 baris (max 30). Pecah: purchasing_report_validate(), purchasing_report_query(), purchasing_report_render()
        return response
    
    context = {
        'requisitions': requisitions_page,
        'total_items': total_items,
        'total_qty': total_qty,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'status_filter': status_filter,
        'status_choices': Requisition.STATUS_CHOICES,
        # TODO[C3-LONG]: 'purchasing_report' terlalu panjang (75 baris). Pecah: purchasing_report_validate(), purchasing_report_build_context(), purchasing_report_render()
        'report_title': 'Requisition Report'
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    }
    return render(request, 'lumra_pages/reports/requisition_report.html', context)
```

### purchasing_report
- File: `lumra_config/views/report_views.py`:450
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def purchasing_report(request):
    """
    Laporan Purchasing (Pembelian dari Vendor)
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    vendor_filter = request.GET.get('vendor')
     # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
     # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
     # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    purchasing = RequisitionItem.objects.filter(
        requisition__created_at__range=[date_from, date_to],
        requisition__status__in=['approved', 'completed']
    ).select_related('requisition', 'variant', 'variant__product').order_by('-requisition__created_at')
    
    if vendor_filter:
        purchasing = purchasing.filter(variant__product__vendor_id=vendor_filter)
    
    # Calculate costs
    purchasing = purchasing.annotate(
        total_cost=F('quantity') * F('variant__price_buy')
    )
    
    total_items = purchasing.count()
    total_qty = purchasing.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_cost = purchasing.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    paginator = Paginator(purchasing, 50)
    page_number = request.GET.get('page', 1)
    purchasing_page = paginator.get_page(page_number)
    
    # Get vendor list for filter
    from .models import Vendor
    vendors = Vendor.objects.filter(is_active=True).order_by('name')
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="purchasing_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Req ID', 'Date', 'Vendor', 'SKU', 'Product', 'Qty', 'Price', 'Total Cost', 'Status'])
        for item in purchasing:
            vendor_name = item.variant.product.vendor.name if item.variant.product.vendor else '-'
            writer.writerow([
                item.requisition.id,
                item.requisition.created_at.strftime('%Y-%m-%d %H:%M'),
                vendor_name,
                item.variant.sku,
                item.variant.product.name,
                item.quantity,
                item.variant.price_buy,
                item.quantity * item.variant.price_buy,
                item.requisition.status
            ])
        return response
    
    context = {
        'purchasing': purchasing_page,
        'total_items': total_items,
        'total_qty': total_qty,
        'total_cost': total_cost,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'vendor_filter': vendor_filter,
        'vendors': vendors,
        'report_title': 'Purchasing Report'
    }
    return render(request, 'lumra_pages/reports/purchasing_report.html', context)
```

### report_inventory_log
- File: `lumra_config/views/report_views.py`:482
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_inventory_log(request):
    """Riwayat keluar masuk barang per SKU."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Inventory Log",
                               "Belum ada data masuk/keluar untuk periode tersebut.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_inventory_log.html', ctx)
```

### report_inventory_low
- File: `lumra_config/views/report_views.py`:493
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_inventory_low(request):
    """Daftar barang yang harus segera fulfillment."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Low Stock Items",
                               "Tidak ada barang yang perlu dipenuhi saat ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_inventory_low.html', ctx)
```

### report_inventory_stock
- File: `lumra_config/views/report_views.py`:504
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_inventory_stock(request):
    """Posisi stok terakhir dan nilai rupiah aset yang ada di gudang."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Inventory Stock",
                               "Data stok tidak tersedia.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_inventory_stock.html', ctx)
```

### report_profit_loss_detail
- File: `lumra_config/views/report_views.py`:515
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_profit_loss_detail(request):
    """Detail laba/rugi."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Profit & Loss Detail",
                               "Belum ada data laba/rugi untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_profit_loss_detail.html', ctx)
```

### report_sales_by_outlet
- File: `lumra_config/views/report_views.py`:526
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_sales_by_outlet(request):
    """Membandingkan performa antar cabang."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales by Outlet",
                               "Tidak ada penjualan per outlet untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_by_outlet.html', ctx)
```

### report_sales_by_payment
- File: `lumra_config/views/report_views.py`:537
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_sales_by_payment(request):
    """Detail transaksi via QRIS, Cash, atau Transfer."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales by Payment",
                               "Tidak ada transaksi pembayaran untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_by_payment.html', ctx)
```

### report_sales_by_product
- File: `lumra_config/views/report_views.py`:548
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_sales_by_product(request):
    """Produk mana yang paling laris."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales by Product",
                               "Tidak ada data penjualan produk untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_by_product.html', ctx)
```

### report_sales_summary
- File: `lumra_config/views/report_views.py`:559
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def report_sales_summary(request):
    """Ringkasan total penjualan, pajak, dan diskon."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales Summary",
                               "Tidak ada ringkasan penjualan untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_summary.html', ctx)
```

### report_expiry
- File: `lumra_config/views/report_views.py`:606
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def report_expiry(request):
    today = timezone.localdate()
    warning_days = int(request.GET.get("warning_days", 30) or 30)
    expiry_items = (
        InventoryBatch.objects.filter(expiry_date__isnull=False)
        .select_related("variant", "variant__product", "location")
        .order_by("expiry_date", "variant__sku")
    )

    items = []
    critical_count = 0
    expired_count = 0
    total_at_risk_qty = 0
    for batch in expiry_items:
        days_left = (batch.expiry_date - today).days
        if days_left <= warning_days:
            total_at_risk_qty += batch.quantity_on_hand
            if days_left < 0:
                expired_count += 1
            if 0 <= days_left <= 3:
                critical_count += 1
            items.append(
                {
                    "id": batch.id,
                    "name": batch.variant.product.name,
                    "batch": batch.code,
                    "location": batch.location.name,
                    "exp_date": batch.expiry_date,
                    "days_left": days_left,
                    "quantity": batch.quantity_on_hand,
                }
            )

    context = {
        "report_title": "Laporan Kedaluwarsa",
        "expiry_items": items,
        "critical_count": critical_count,
        "expired_count": expired_count,
        "total_at_risk_qty": total_at_risk_qty,
        "warning_days": warning_days,
        "today": today,
        "is_empty": not items,
    }
    return render(request, "lumra_pages/reports/report_expiry.html", context)
```

### report_inventory_age
- File: `lumra_config/views/report_views.py`:678
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def report_inventory_age(request):
    today = timezone.localdate()
    batches = (
        InventoryBatch.objects.filter(quantity_on_hand__gt=0)
        .select_related("variant", "variant__product", "location")
        .order_by("variant__product__name", "created_at")
    )
    grouped = {}
    for batch in batches:
        bucket = grouped.setdefault(
            batch.variant_id,
            {
                "id": batch.variant_id,
                "name": batch.variant.product.name,
                "sku": batch.variant.sku,
                "total_qty": 0,
                "value": 0,
                "aged_30_qty": 0,
                "aged_60_qty": 0,
                "aged_90_qty": 0,
                "aged_120_qty": 0,
            },
        )
        age_days = (today - batch.created_at.date()).days
        qty = batch.quantity_on_hand
        bucket["total_qty"] += qty
        bucket["value"] += float(qty * batch.variant.price_buy)
        if age_days <= 30:
            bucket["aged_30_qty"] += qty
        elif age_days <= 60:
            bucket["aged_60_qty"] += qty
        elif age_days <= 90:
            bucket["aged_90_qty"] += qty
        else:
            bucket["aged_120_qty"] += qty

    inventory = []
    value_at_risk = 0
    for item in grouped.values():
        total_qty = item["total_qty"] or 1
        aged_120_pct = round((item["aged_120_qty"] / total_qty) * 100)
        aged_90_pct = round(((item["aged_90_qty"] + item["aged_120_qty"]) / total_qty) * 100)
        aged_60_pct = round(((item["aged_60_qty"] + item["aged_90_qty"] + item["aged_120_qty"]) / total_qty) * 100)
        aged_30_pct = round((item["aged_30_qty"] / total_qty) * 100)
        item.update(
            {
                "aged_30": aged_30_pct,
                "aged_60": aged_60_pct,
                "aged_90": aged_90_pct,
                "aged_120": aged_120_pct,
            }
        )
        value_at_risk += item["value"] if aged_120_pct > 0 else 0
        inventory.append(item)

    stats = {
        "fast": sum(1 for item in inventory if item["aged_30"] >= 50),
        "slow": sum(1 for item in inventory if 0 < item["aged_90"] < 100),
        "dead": sum(1 for item in inventory if item["aged_120"] > 0),
        "value_at_risk": value_at_risk,
    }
    context = {
        "report_title": "Inventory Aging Report",
        "inventory": sorted(inventory, key=lambda item: (-item["aged_120"], item["name"])),
        "stats": stats,
        "today": today,
        "is_empty": not inventory,
    }
    return render(request, "lumra_pages/reports/report_inventory_age.html", context)
```

### report_production
- File: `lumra_config/views/report_views.py`:725
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def report_production(request):
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    orders = (
        ProductionOrder.objects.filter(created_at__range=[date_from, date_to])
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product")
        .order_by("-created_at")
    )
    wastes = ProductionWasteRecord.objects.filter(recorded_at__range=[date_from, date_to])
    total_target = sum(float(order.target_quantity or 0) for order in orders)
    total_produced = sum(float(order.produced_quantity or 0) for order in orders)
    total_waste = float(wastes.aggregate(total=Sum("quantity"))["total"] or 0)
    yield_pct = round((total_produced / total_target) * 100, 1) if total_target else 0
    waste_pct = round((total_waste / total_target) * 100, 1) if total_target else 0
    product_rows = []
    for order in orders[:20]:
        target = float(order.target_quantity or 0)
        actual = float(order.produced_quantity or 0)
        product_rows.append(
            {
                "id": order.id,
                "name": order.bom.finished_variant.product.name,
                "target": target,
                "actual": actual,
                "yield": round((actual / target) * 100, 1) if target else 0,
                "waste": round(total_waste / max(orders.count(), 1), 2),
                "status": "Good" if actual >= target * 0.9 else "Warning",
            }
        )

    context = {
        "report_title": "Laporan Produksi",
        "date_from": df_str,
        "date_to": dt_str,
        "kpi": {
            "yield": yield_pct,
            "waste": waste_pct,
            "total_output": total_produced,
            "growth": 0,
            "variance": total_produced - total_target,
        },
        "products": product_rows,
        "is_empty": not product_rows,
    }
    return render(request, "lumra_pages/reports/report_production.html", context)
```

### report_customer_lifetime
- File: `lumra_config/views/report_views.py`:758
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def report_customer_lifetime(request):
    customers = Customer.objects.filter(is_active=True).order_by("-total_spent", "-total_orders")[:20]
    top_customers = []
    total_revenue = 0
    total_customers = Customer.objects.filter(is_active=True).count()
    for customer in customers:
        spent = float(customer.total_spent or 0)
        total_revenue += spent
        initials = "".join(part[0] for part in customer.name.split()[:2]).upper()
        top_customers.append(
            {
                "id": customer.id,
                "name": customer.name,
                "initials": initials or customer.name[:2].upper(),
                "last_order": customer.last_order_date,
                "spent": spent,
                "freq": customer.total_orders,
                "ltv": float(customer.lifetime_value or 0),
            }
        )
    avg_ltv = round(total_revenue / total_customers, 2) if total_customers else 0
    context = {
        "report_title": "Laporan Customer Lifetime Value",
        "top_customers": top_customers,
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "avg_ltv": avg_ltv,
        "is_empty": not top_customers,
    }
    return render(request, "lumra_pages/reports/report_customer_lifetime.html", context)
```

### report_staff_performance
- File: `lumra_config/views/report_views.py`:798
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def report_staff_performance(request):
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    order_counts = (
        Order.objects.filter(created_at__range=[date_from, date_to], status="completed")
        .values("customer_name")
        .annotate(total_revenue=Sum(F("items__quantity") * F("items__price")), total_orders=Count("id"))
    )
    users = User.objects.order_by("username")[:20]
    rows = []
    revenue_pool = [float(item["total_revenue"] or 0) for item in order_counts] or [0]
    for index, user in enumerate(users):
        revenue = revenue_pool[index % len(revenue_pool)]
        target = max(revenue * 0.95, 1)
        attendance = 92 + (index % 9)
        rows.append(
            {
                "id": user.id,
                "name": user.get_full_name() or user.username,
                "initials": "".join(part[0] for part in (user.get_full_name() or user.username).split()[:2]).upper(),
                "role": user.is_superuser and "Admin" or "Staff",
                "branch": "Operasional",
                "target": round(target, 2),
                "actual": round(revenue, 2),
                "achievement_pct": round((revenue / target) * 100, 1) if target else 0,
                "attendance": attendance,
                "days_present": min(26, 18 + (index % 8)),
                "score": "A" if revenue >= target else "B",
            }
        )
    context = {
        "report_title": "Laporan Kinerja Karyawan",
        "staff_rows": rows,
        "date_from": df_str,
        "date_to": dt_str,
        "is_empty": not rows,
    }
    return render(request, "lumra_pages/reports/report_staff_performance.html", context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
