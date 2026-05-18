Rekap 10 April 2026
# Review LUMRA ERP Template Catalog

Ini analisis jujur dan mendalam dari sudut pandang arsitektur ERP, UX, dan engineering.

---

## ✅ Yang Sudah Bagus

**1. Struktur Inheritance Django yang Bersih**
```
base.html → navbar + sidebar + content block → halaman spesifik
```
Pola ini konsisten dan scalable. Penggunaan CMS blocks (`extra_head`, `extra_css`, `content`) memberikan fleksibilitas tanpa bikin spaghetti.

**2. Komponen Reusable Terstruktur**
`kpi_card.html`, `form_field.html`, `approval_modal.html`, `alert_inner.html` — ini menunjukkan disiplin DRY. Bukan copy-paste HTML di setiap halaman.

**3. Workflow Stock Opname Lengkap**
5 template yang membentuk alur utuh:
```
Pilih Lokasi → Input Hitungan → Daftar Approval → Detail Approval → Session History
```
Ini alur bisnis nyata, bukan sekadar CRUD.

**4. Modul Laporan Sangat Kaya**
20 template laporan dengan kategori jelas (sales, inventory, financial, operational). Ini sering diabaikan di ERP kecil tapi sangat dibutuhkan user bisnis.

---

## 🔴 Red Flags — Masalah Serius

### 1. Duplikasi Template yang Membingungkan

| Duplikat | Masalah |
|----------|---------|
| `stock_opname_locations.html` | Muncul **DUA KALI** di dokumentasi dengan deskripsi berbeda |
| `vendors_list.html` + `vendor_list.html` | Hanya beda huruf 's', fungsi sama |
| `customers.html` + `customer.html` + `customer_detail.html` | 3 file untuk esensi yang sama |
| `products.html` + `product_list.html` | Redundan |
| `campaign.html` + `campaign_list.html` | Redundan |
| `locations.html` + `location_list.html` | Redundan |
| `add_stock_movement.html` + `stock_movement_form.html` | Redundan |
| `sales_report.html` + `sales_report_after.html` | Naming membingungkan — "after" apa? |
| `stock_overview.html` | Muncul di **inventory/** DAN **reports/** — mana yang benar? |
| `financial_reports.html` | Muncul di **sales_insight/** DAN **reports/** |

**Dampak:** Developer baru tidak tahu file mana yang harus diedit. Bisa jadi satu file tidak termaintain sementara yang lain aktif.

### 2. Modul Kritis Hilang Total

```
❌ Accounting / Jurnal Umum / Chart of Accounts
❌ Invoice & Billing (penagihan)
❌ Sales Order / Quotation (terpisah dari POS)
❌ Retur & Refund ( barang rusak, pembatalan)
❌ Warehouse / Bin / Rack management
❌ Batch / Lot / Serial Number tracking
❌ Expiry Date management (kritis untuk F&B)
❌ Delivery / Shipping / Logistics
❌ Tax Management & Configuration
❌ Multi-currency
❌ HR / Payroll (meski bisa fase 2)
❌ Requisition Form (hanya report-nya ada)
```

Untuk klaim "Complete ERP", ini gap yang sangat besar.

### 3. Modul Production Terlalu Kurus

Hanya 3 template untuk modul produksi:

```
recipe_list → recipe_form → recipe_detail
```

Yang hilang:
- **Production Order** (perintah produksi)
- **Work Order / Job Ticket**
- **BOM (Bill of Materials)** terpisah dari recipe
- **Raw Material Consumption** (pemakaian bahan baku)
- **Finished Goods Receipt** (penerimaan hasil produksi)
- **Production Scheduling**
- **Waste / Scrap recording**
- **Allergen / Nutritional info** (khusus F&B)

### 4. Naming Convention Tidak Konsisten

```python
# Plural vs Singular acak:
products.html       # plural
customer.html       # singular (ada JUGA customers.html)
vendor_list.html    # singular + _list
vendors_list.html   # plural + _list
category_form.html  # singular
units_list.html     # plural

# Folder name tidak match konten:
sales_insight/      # tapi isinya ada pos.html dan dashboard.html
```

### 5. Dashboard Placement Membingungkan

`dashboard.html` ada di dalam `sales_insight/` — ini main dashboard atau dashboard sales saja? Jika main dashboard, seharusnya di level root atau `dashboard/` sendiri. Jika dashboard sales, seharusnya namanya `sales_dashboard.html`.

---

## 🟡 Warning — Potensi Masalah

### 1. Glassmorphism untuk ERP?

> *Theme: Emerald Odyssey (Glassmorphism)*

Glassmorphism = `backdrop-blur` + transparency + border-radius besar.

**Masalah di konteks ERP:**
- **Performance** — `backdrop-blur` berat di device rendah, dan user ERP sering pakai laptop kantor spek pas-pasan
- **Readability** — teks di atas elemen transparan susah dibaca saat data padat
- **Accessibility** — kontras rendah, sulit untuk color-blind users
- **Print** — glass effect tidak printable, laporan akan jelek
- **Cognitive load** — ERP itu tools kerja, bukan portfolio. User butuh kejelasan, bukan estetika

Ini bukan berarti jelek, tapi pertimbangkan: **apakah user target lebih butuh "wow factor" atau "kerja cepat tanpa bingung"?**

### 2. Alpine.js untuk Kompleksitas ERP?

Alpine.js bagus untuk interaksi sederhana (toggle, dropdown, modal). Tapi untuk:
- POS real-time dengan cart management kompleks
- Drag-and-drop stock opname
- Inline editing tabel dengan validasi
- Komponen yang saling bergantung (pilih supplier → update price list → hitung total)

Ini bisa jadi **spaghetti Alpine attributes** yang susah di-maintain. Pertimbangkan:
- Tetap Alpine tapi dengan batas kompleksitas jelas
- Atau migrate komponen berat ke **HTMX** (lebih Django-friendly) atau **Petite-Vue**

### 3. Tidak Ada Template Print

102 template, **nol** untuk keperluan cetak:
- ❌ Struk POS / Receipt
- ❌ Invoice
- ❌ Purchase Order
- ❌ Packing Slip
- ❌ Laporan versi print-ready

ERP tanpa cetak = tidak siap produksi.

### 4. Tidak Ada Onboarding / Setup Wizard

User baru login pertama kali → langsung dashboard kosong? Harus ada:
- Setup wizard (isi info bisnis, buat lokasi, kategori pertama)
- Empty state designs (halaman tanpa data tetap informatif)

---

## 📊 Skor per Modul

```
Inventory Management     ████████░░  8/10  (opname bagus, tapi batch/expiry hilang)
Sales & POS              ██████░░░░  6/10  (POS oke, tapi invoice/SO/retur hilang)
Production/Recipes       ██░░░░░░░░  2/10  (hanya CRUD recipe, bukan production management)
Marketing Management     ████░░░░░░  4/10  (basic, tidak ada voucher/segmentation)
Master Data              ███████░░░  7/10  (lengkap, tapi perlu standardisasi)
Reports & Analytics      █████████░  9/10  (terbaik di katalog ini)
Messages & Notifications ██░░░░░░░░  2/10  (terlalu minimal)
Settings & System        ███████░░░  7/10  (cukup komprehensif)
Authentication           █████░░░░░  5/10  (basic, tidak ada forgot password page, 2FA page)
Error Pages              ████████░░  8/10  (standar tapi cukup)

Accounting               ░░░░░░░░░░  0/10  (tidak ada)
HR/Payroll               ░░░░░░░░░░  0/10  (tidak ada)
Logistics/Delivery       ░░░░░░░░░░  0/10  (tidak ada)
Print Templates          ░░░░░░░░░░  0/10  (tidak ada)
```

---

## 🎯 Rekomendasi Prioritas

### Segera (Sebelum Launch)
1. **Hapus template duplikat** — tentukan satu sumber kebenaran
2. **Tambahkan print templates** — minimal struk POS dan invoice
3. **Pindahkan `dashboard.html`** ke lokasi yang benar
4. **Standardisasi naming** — pilih plural atau singular, konsisten

### Fase 2 (Bulan 1-2)
5. **Tambah Invoice & Sales Order** — ini revenue stream, tanpa ini ERP tidak lengkap
6. **Tambah Retur/Refund** — setiap transaksi bisa dibatalkan
7. **Tambah Print PO** — pembelian butuh dokumen
8. **Setup wizard** — pengalaman first login

### Fase 3 (Bulan 3-6)
9. **Perkuat Production** — production order, BOM, material consumption
10. **Accounting dasar** — minimal chart of accounts dan jurnal
11. **Batch/Expiry tracking** — kritis untuk F&B
12. **Pertimbangkan ulang glassmorphism** — atau setidaknya berikan toggle "classic mode"

---

## Kesimpulan

**Katalog ini 60-65% siap untuk ERP fokus inventory+POS.** 

Modul laporan dan workflow stock opname adalah highlight terbaik. Tapi klaim "Complete ERP" belum terpenuhi karena tidak ada accounting, invoice, retur, dan print templates. Duplikasi file adalah technical debt yang harus dibersihkan sebelum tim developer berkembang.

**Yang paling mengkhawatirkan:** jika ini akan dipakai bisnis F&B nyata, tanpa expiry management dan production order, user akan kewalahan dengan workaround manual.
 
# 📋 LUMRA ERP — Roadmap Lengkap ke 10/10

## Tabel Hitung Cepat

| Status | Jumlah |
|--------|--------|
| File existing (akan dipertahankan) | **81** |
| File existing (akan dihapus/digabung) | **21** |
| File baru yang harus dibuat | **~131** |
| **Total file final** | **~212** |

---

## 0️⃣ Pembersihan — File yang HARUS DIHAPUS

Jangan buat file baru sebelum ini bersih, otherwise confusion berlanjut.

```
HAPUS                          ALASAN                          GANTI DENGAN
─────────────────────────────  ──────────────────────────────  ──────────────────────
customer.html                  Duplikat customer_detail.html   customer_detail.html
vendor_list.html               Duplikat vendors_list.html      vendors_list.html
product_list.html              Duplikat products.html          products.html (tambah toggle view)
campaign_list.html             Duplikat campaign.html          campaign.html (tambah pagination)
location_list.html             Duplikat locations.html         locations.html
add_stock_movement.html        Duplikat stock_movement_form    stock_movement_form.html
sales_report_after.html        Naming membingungkan            sales_report.html (tingkatkan)
stock_opname_locations.html    Duplikat di 2 tempat           Pilih satu: tetap di inventory/
stock_overview.html (di report/)  Duplikat dari inventory/   Hapus yang di reports/, buat alias
financial_reports.html (di report/) Duplikat dari sales_insight/ Hapus yang di reports/
```

**Setelah hapus: 81 file tersisa.**

---

## 1️⃣ Base Components — 9 File Baru

**Lokasi:** `lumra_config/templates/base/partials/`

```
FILE                        TUJUAN                                  DIGUNAKAN OLEH
──────────────────────────  ──────────────────────────────────────  ──────────────────────
empty_state.html            Halaman tanpa data (icon + pesan + CTA)  Semua list page saat kosong
pagination.html             Navigasi halaman standar                 Semua list page
data_table.html             Wrapper tabel (sort, search, per-page)   Semua tabel data
breadcrumb.html             Navigasi breadcrumb                     Semua halaman dalam
confirm_modal.html          Dialog konfirmasi generik (ya/tidak)     Semua aksi hapus/batal
tabs.html                   Komponen tab horizontal                  Halaman detail multi-tab
badge.html                  Badge status (success/warning/danger)   Semua list & detail
stepper.html                Step wizard (1→2→3→4)                   Onboarding, form multi-step
print_base.html             Layout cetak (tanpa navbar/sidebar)      Semua print template
```

---

## 2️⃣ Authentication — 6 File Baru

**Lokasi:** `lumra_config/templates/lumra_pages/auth/`

```
FILE                    TUJUAN                                    CONNECT KE
──────────────────────  ────────────────────────────────────────  ──────────────
forgot_password.html    Form input email untuk reset password      reset_password.html
reset_password.html     Form set password baru (dari link email)   login.html
verify_email.html       Halaman "cek email kamu"                   login.html
two_factor.html         Input kode OTP 2FA                         dashboard.html
lock_screen.html        Layar kunci (pin/password untuk unlock)    dashboard.html
session_expired.html    "Sesi berakhir, login ulang"               login.html
```

---

## 3️⃣ Onboarding / Setup Wizard — 5 File Baru

**Lokasi:** `lumra_config/templates/lumra_pages/onboarding/`

```
FILE                    TUJUAN                                    STEP
──────────────────────  ────────────────────────────────────────  ────
welcome.html            Welcome screen + tombol mulai setup       Step 0
step_business.html      Input nama bisnis, logo, industri         Step 1
step_location.html      Tambah lokasi/outlet pertama              Step 2
step_category.html      Tambah kategori produk pertama            Step 3
step_complete.html      "Setup selesai!" + tombol ke dashboard    Step 4
```

**Logika:** `welcome → step_business → step_location → step_category → step_complete`
Gunakan `stepper.html` dari base components.

---

## 4️⃣ Inventory Management — 11 File Baru (8→10)

**Lokasi:** `lumra_config/templates/lumra_pages/inventory/`

```
FILE                            TUJUAN                                    FITUR UTAMA
──────────────────────────────  ────────────────────────────────────────  ──────────────────────
requisition_list.html           Daftar permintaan stok antar lokasi       Status, filter, search
requisition_form.html           Buat/edit permintaan stok                 Pilih lokasi asal/tujuan,
                                                                          pilih produk + qty, notes
requisition_detail.html         Detail + approval permintaan              Approve/reject, fulfil status
batch_list.html                 Daftar batch/lot produk                   Batch code, produk, qty,
                                                                          tanggal produksi, expiry
batch_form.html                 Buat/edit batch                           Batch code, produk, qty,
                                                                          production date, expiry date
batch_detail.html               Detail batch + tracking                   Produk terkait, sisa stok,
                                                                          lokasi, movement history
expiry_tracking.html            Dashboard produk mendekati expired        Traffic light (hijau/kuning/merah),
                                                                          filter by 7/14/30 hari
warehouse_zones.html            Daftar zone/rak di gudang                Zone code, lokasi, kapasitas,
                                                                          tipe (cold/dry/danger)
warehouse_zone_form.html        Buat/edit zone                           Zone code, nama, lokasi,
                                                                          kapasitas, tipe penyimpanan
adjustment_reasons.html         Konfigurasi alasan penyesuaian stok      Reason code, nama, tipe
                                                                          (plus/minus), aktif/nonaktif
supplier_evaluation.html        Skor performa supplier                   Delivery on-time, quality score,
                                                                          price competitiveness, ranking
```

---

## 5️⃣ Sales & POS — 16 File Baru (6→10)

**Lokasi:** `lumra_config/templates/lumra_pages/sales/` *(FOLDER BARU, pisah dari sales_insight)*

### Sales Order & Quotation
```
FILE                    TUJUAN                                    FITUR UTAMA
──────────────────────  ────────────────────────────────────────  ──────────────────────
sales_order_list.html   Daftar sales order                        Status, filter tanggal,
                                                                     customer, total
sales_order_form.html   Buat/edit sales order                     Customer, produk, qty,
                                                                     harga, diskon, catatan
sales_order_detail.html Detail SO + konversi ke invoice          Line items, status pipeline,
                                                                     tombol "Buat Invoice"
quotation_list.html     Daftar penawaran harga                   Status (draft/sent/accepted/
                                                                     rejected), valid until
quotation_form.html     Buat/edit quotation                      Customer, produk, harga,
                                                                     validitas, terms
quotation_detail.html   Detail quotation + konversi ke SO        Line items, tombol
                                                                     "Konversi ke SO"
```

### Invoice & Billing
```
FILE                    TUJUAN                                    FITUR UTAMA
──────────────────────  ────────────────────────────────────────  ──────────────────────
invoice_list.html       Daftar invoice                            Status (unpaid/partial/paid/
                                                                     overdue), due date
invoice_form.html       Buat invoice (dari SO atau manual)        Customer, line items, PPN,
                                                                     terms, due date
invoice_detail.html     Detail invoice + catat pembayaran         Line items, total, payment
                                                                     history, tombol "Catat Bayar"
payment_list.html       Daftar pembayaran masuk                   Metode, jumlah, referensi,
                                                                     invoice terkait
payment_form.html       Catat pembayaran baru                     Invoice selector, jumlah,
                                                                     metode, tanggal, referensi
```

### Retur & Refund
```
FILE                    TUJUAN                                    FITUR UTAMA
──────────────────────  ────────────────────────────────────────  ──────────────────────
retur_list.html         Daftar retur barang                      Status, customer, invoice
                                                                     asal, nilai retur
retur_form.html         Buat retur                                Invoice asal, produk yang
                                                                     dikembalikan, qty, alasan
retur_detail.html       Detail retur + approval                  Line items retur, status
                                                                     approval, tombol proses
```

### Restrukturisasi Folder sales_insight/
```
FILE existing              AKSI
─────────────────────────  ────────────────────────────────────────────
pos.html                   PINDAH ke sales/pos.html
dashboard.html             RENAME jadi sales_dashboard.html
sales_intelligence.html    TETAP di sini (ini analytics, bukan transaksi)
sales_performance.html     TETAP di sini
financial_reports.html     TETAP di sini
market_insights.html       TETAP di sini
trends_analysis.html       TETAP di sini
```

**Struktur akhir:**
```
lumra_pages/
├── sales/              ← TRANSAKSI (POS, SO, Quotation, Invoice, Retur)
│   ├── pos.html
│   ├── sales_order_list.html
│   ├── sales_order_form.html
│   ├── ...
└── sales_insight/      ← ANALITIKA (dashboard, performance, trends)
    ├── sales_dashboard.html
    ├── sales_intelligence.html
    ├── ...
```

---

## 6️⃣ Production / Recipes — 11 File Baru (2→10)

**Lokasi:** `lumra_config/templates/lumra_pages/production/`

```
FILE                            TUJUAN                                    FITUR UTAMA
──────────────────────────────  ────────────────────────────────────────  ──────────────────────
production_order_list.html      Daftar production order                  Status, tanggal, produk,
                                                                          qty target, actual
production_order_form.html      Buat/edit production order               Produk, qty target, tanggal
                                                                          mulai/selesai, catatan
production_order_detail.html    Detail PO + proses produksi              BOM terpakai, material
                                                                          consumption, tombol mulai/
                                                                          selesai/complete
bom_list.html                   Daftar Bill of Materials                 Produk jadi, jumlah bahan,
                                                                          versi BOM, status aktif
bom_form.html                   Buat/edit BOM                            Produk jadi, daftar bahan
                                                                          baku + qty + unit
bom_detail.html                 Detail BOM                               Bahan baku, cost per unit,
                                                                          yield, versi history
production_scheduling.html      Kalender jadwal produksi                 View mingguan/bulanan,
                                                                          drag reschedule, kapasitas
material_consumption.html       Catat pemakaian bahan baku               PO selector, bahan, qty
                                                                          terpakai vs teoritis, waste
finished_goods_receipt.html     Terima hasil produksi ke stok           PO selector, qty hasil,
                                                                          lokasi tujuan, quality check
production_waste.html           Catat waste/scrap produksi              PO selector, bahan, qty
                                                                          waste, alasan, biang kerok
production_costing.html         Analisis biaya produksi                  Cost per unit, actual vs
                                                                          standar, variance, trend
```

**Alur lengkap:**
```
BOM (definisi resep) → Production Order (perintah) → Scheduling (jadwal)
→ Material Consumption (pakai bahan) → Waste Recording (catat sampah)
→ Finished Goods Receipt (masukkan hasil) → Costing (hitung biaya)
```

---

## 7️⃣ Marketing Management — 6 File Baru (4→10)

**Lokasi:** `lumra_config/templates/lumra_pages/marketing/`

```
FILE                        TUJUAN                                    FITUR UTAMA
──────────────────────────  ────────────────────────────────────────  ──────────────────────
voucher_list.html           Daftar voucher/kupon                     Kode, jenis (%/nominal),
                                                                          kuota, terpakai, status
voucher_form.html           Buat/edit voucher                        Kode (auto/manual), nilai,
                                                                          min. pembelian, kuota,
                                                                          periode, produk berlaku
voucher_claim_log.html      Log klaim voucher                        Customer, voucher, transaksi,
                                                                          waktu klaim
customer_segment_list.html  Daftar segmen pelanggan                  Nama segmen, kriteria,
                                                                          jumlah anggota, last updated
customer_segment_form.html  Buat/edit segmen                         Nama, rules (total belanja,
                                                                          frekuensi, lokasi, kategori)
promotion_calendar.html     Kalender promosi (timeline view)          Promosi aktif/mendatang,
                                                                          overlap detector
```

---

## 8️⃣ Master Data & Configuration — 8 File Baru (7→10)

**Lokasi:** `lumra_config/templates/lumra_pages/master_data/`

```
FILE                        TUJUAN                                    FITUR UTAMA
──────────────────────────  ────────────────────────────────────────  ──────────────────────
tax_list.html               Daftar konfigurasi pajak                 Nama pajak, persentase,
                                                                          tipe (inclusive/exclusive)
tax_form.html               Buat/edit pajak                          Nama, rate, tipe, akun
                                                                          terkait, status aktif
payment_terms_list.html     Daftar syarat pembayaran                 Nama (COD/Net30/Net60),
                                                                          deskripsi, default
payment_terms_form.html     Buat/edit terms                          Nama, jumlah hari, deskripsi,
                                                                          denda keterlambatan
bank_accounts.html          Daftar rekening perusahaan               Bank, nomor rekening,
                                                                          atas nama, tipe (kredit/debit)
bank_account_form.html      Buat/edit rekening                       Bank selector, nomor, nama,
                                                                          currency, default
reason_codes.html           Daftar kode alasan (retur, adjustment)   Code, nama, kategori,
                                                                          aktif/nonaktif
tags_list.html              Daftar tag/label                         Nama tag, warna, pemakaian
                                                                          (produk/customer/transaksi)
```

---

## 9️⃣ Accounting — 12 File Baru (0→10) 🆕 MODUL BARU

**Lokasi:** `lumra_config/templates/lumra_pages/accounting/`

```
FILE                        TUJUAN                                    FITUR UTAMA
──────────────────────────  ────────────────────────────────────────  ──────────────────────
chart_of_accounts.html      Daftar akun (COA)                        Kode akun, nama, tipe
                                                                          (asset/liability/equity/
                                                                          revenue/expense), saldo
chart_of_accounts_form.html Buat/edit akun                            Kode, nama, tipe, parent,
                                                                          deskripsi, status
journal_entry_list.html     Daftar jurnal umum                        Tanggal, nomor jurnal,
                                                                          deskripsi, total debit/kredit
journal_entry_form.html     Buat/edit jurnal                          Tanggal, referensi, lines
                                                                          (akun, debit, kredit), notes
journal_entry_detail.html   Detail jurnal                             Header info, line items,
                                                                          status (draft/posted)
general_ledger.html         Buku besar                               Filter akun + periode,
                                                                          saldo awal, mutasi, saldo akhir
trial_balance.html          Neraca saldo                             Semua akun, saldo debit,
                                                                          saldo kredit, selisih
balance_sheet.html          Neraca                                    Aset, kewajiban, ekuitas,
                                                                          periode, compare prev
cash_flow.html              Laporan arus kas                         Operating, investing,
                                                                          financing, net change
accounts_payable.html       Daftar hutang usaha (AP aging)           Supplier, invoice, umur
                                                                          (0-30/31-60/61-90/90+)
accounts_receivable.html    Daftar piutang usaha (AR aging)          Customer, invoice, umur
                                                                          (0-30/31-60/61-90/90+)
payment_voucher_form.html   Bukti kas keluar (pembayaran ke supplier) Supplier, invoice, akun kas,
                                                                          jumlah, tanggal, referensi
```

**Catatan:** Accounting ini **simplified**, bukan full GL system. Cukup untuk ERP F&B/inventory. Jangan terlalu ambisius bikin full SAP-like accounting.

---

## 🔟 Print Templates — 11 File Baru (0→10) 🆕 MODUL BARU

**Lokasi:** `lumra_config/templates/lumra_pages/print/`

```
FILE                        TUJUAN                                    FORMAT
──────────────────────────  ────────────────────────────────────────  ──────────
print_receipt.html           Struk POS / receipt kasir               58mm thermal
print_invoice.html           Invoice penjualan                       A4
print_quotation.html         Penawaran harga                         A4
print_sales_order.html       Sales order                             A4
print_purchase_order.html    Purchase order ke supplier              A4
print_delivery_note.html     Surat jalan / delivery note             A4
print_packing_slip.html      Packing slip (isi paket)                A5
print_credit_note.html       Credit note / nota kredit               A4
print_payment_receipt.html   Bukti pembayaran dari customer          A5
print_stock_opname.html      Lembar hitung stok opname               A4 landscape
print_production_order.html  Surat perintah produksi                 A4
```

**Semua inherit dari `print_base.html`** — layout minimal tanpa navbar/sidebar, CSS print-optimized (`@media print`), barcode/QR code placeholder.

---

## 1️⃣1️⃣ Messages & Notifications — 4 File Baru (2→10)

**Lokasi:** `lumra_config/templates/lumra_pages/messages/`

```
FILE                        TUJUAN                                    FITUR UTAMA
──────────────────────────  ────────────────────────────────────────  ──────────────────────
compose.html                Tulis pesan baru                         To (user/role), subject,
                                                                          body, attachment, send
message_detail.html         Baca thread pesan                        Pesan parent + replies,
                                                                          reply form, mark read
broadcast.html              Kirim pesan ke semua / role / segmen     Target selector, subject,
                                                                          body, preview, send
message_templates.html      Template pesan yang sering dipakai       Nama, subject, body template,
                                                                          variabel placeholder
```

---

## 1️⃣2️⃣ Reports & Analytics — 5 File Baru (9→10)

**Lokasi:** `lumra_config/templates/lumra_pages/reports/`

```
FILE                            TUJUAN                                    DATA
──────────────────────────────  ────────────────────────────────────────  ──────────────────
report_production.html           Laporan produksi                         Order by status, output vs
                                                                          target, waste %, cost/unit
report_expiry.html               Laporan produk kedaluwarsa              Produk, batch, expiry date,
                                                                          sisa qty, lokasi, status
report_customer_lifetime.html    Laporan nilai pelanggan (CLV)           Customer, total belanja,
                                                                          frekuensi, avg order, segment
report_staff_performance.html    Laporan performa kasir/staff            Staff, transaksi, nilai total,
                                                                          avg transaction, jam kerja
report_inventory_age.html        Laporan umur stok (stock aging)         Produk, tanggal masuk, umur
                                                                          hari, qty, nilai, risk level
```

---

## 1️⃣3️⃣ Settings & System — 8 File Baru (7→10)

**Lokasi:** `lumra_config/templates/lumra_pages/settings/`

```
FILE                            TUJUAN                                    FITUR UTAMA
──────────────────────────────  ────────────────────────────────────────  ──────────────────────
roles.html                      Daftar role/posisi                       Nama role, jumlah user,
                                                                          deskripsi, edit
role_form.html                  Buat/edit role + permission              Nama, deskripsi, checklist
                                                                          permission per module
permission_matrix.html          Matriks permission lengkap               Tabel role × module × action
                                                                          (view/create/edit/delete)
backup_restore.html             Backup & restore data                    Download backup, upload restore,
                                                                          cron schedule, history
email_settings.html             Konfigurasi SMTP email                   Host, port, username, password
                                                                          (masked), test email button
notification_settings.html      Aturan notifikasi                        Channel (in-app/email/push),
                                                                          event trigger, toggle on/off
numbering_settings.html         Format nomor dokumen                     SO-001, INV-002, PO-003,
                                                                          prefix, digit, reset periode
api_keys.html                   Manajemen API key (jika ada integrasi)   Key, nama, created, last used,
                                                                          revoke, create new
```

---

## 1️⃣4️⃣ Error Pages — 2 File Baru (8→10)

**Lokasi:** `lumra_config/templates/lumra_pages/etc/`

```
FILE                        TUJUAN                                    FITUR
──────────────────────────  ────────────────────────────────────────  ──────────────────────
error_maintenance.html       Mode pemeliharaan                       Estimasi waktu kembali,
                                                                          link status page
error_session_expired.html   Sesi habis (beda dari auth/)            Auto-redirect countdown,
                                                                          tombol login ulang
```

---

## 📁 Struktur Folder Final

```
lumra_config/templates/
├── base/
│   ├── base.html
│   ├── navbar.html
│   ├── sidebar.html
│   ├── sidebar_item.html
│   ├── sidebar_right.html
│   ├── footer.html
│   ├── alert.html
│   ├── alert_inner.html
│   ├── approval_modal.html
│   ├── kpi_card.html
│   ├── kpi_card_inner.html
│   ├── kpi_card_white.html
│   └── partials/
│       ├── form_field.html
│       ├── bg_blob.html
│       ├── empty_state.html          🆕
│       ├── pagination.html           🆕
│       ├── data_table.html           🆕
│       ├── breadcrumb.html           🆕
│       ├── confirm_modal.html        🆕
│       ├── tabs.html                 🆕
│       ├── badge.html                🆕
│       └── stepper.html              🆕
│
├── lumra_pages/
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── forgot_password.html      🆕
│   │   ├── reset_password.html       🆕
│   │   ├── verify_email.html         🆕
│   │   ├── two_factor.html           🆕
│   │   ├── lock_screen.html          🆕
│   │   └── session_expired.html      🆕
│   │
│   ├── onboarding/                   🆕 FOLDER
│   │   ├── welcome.html
│   │   ├── step_business.html
│   │   ├── step_location.html
│   │   ├── step_category.html
│   │   └── step_complete.html
│   │
│   ├── inventory/                    (16 → 27 file)
│   │   ├── products.html
│   │   ├── product_details.html
│   │   ├── stock_overview.html
│   │   ├── stock_movement.html
│   │   ├── stock_movement_form.html
│   │   ├── stock_planning.html
│   │   ├── stock_opname_locations.html
│   │   ├── stock_opname_form.html
│   │   ├── stock_opname_approvals.html
│   │   ├── stock_opname_approval_detail.html
│   │   ├── stock_purchasing.html
│   │   ├── supplier_price_list.html
│   │   ├── supplier_price_form.html
│   │   ├── supplier_price_confirm_delete.html
│   │   ├── requisition_list.html         🆕
│   │   ├── requisition_form.html         🆕
│   │   ├── requisition_detail.html       🆕
│   │   ├── batch_list.html               🆕
│   │   ├── batch_form.html               🆕
│   │   ├── batch_detail.html             🆕
│   │   ├── expiry_tracking.html          🆕
│   │   ├── warehouse_zones.html          🆕
│   │   ├── warehouse_zone_form.html      🆕
│   │   ├── adjustment_reasons.html       🆕
│   │   └── supplier_evaluation.html      🆕
│   │
│   ├── sales/                        🆕 FOLDER (16 file baru)
│   │   ├── pos.html
│   │   ├── sales_order_list.html
│   │   ├── sales_order_form.html
│   │   ├── sales_order_detail.html
│   │   ├── quotation_list.html
│   │   ├── quotation_form.html
│   │   ├── quotation_detail.html
│   │   ├── invoice_list.html
│   │   ├── invoice_form.html
│   │   ├── invoice_detail.html
│   │   ├── payment_list.html
│   │   ├── payment_form.html
│   │   ├── retur_list.html
│   │   ├── retur_form.html
│   │   └── retur_detail.html
│   │
│   ├── sales_insight/                (7 → 6 file, dashboard di-rename)
│   │   ├── sales_dashboard.html
│   │   ├── sales_intelligence.html
│   │   ├── sales_performance.html
│   │   ├── financial_reports.html
│   │   ├── market_insights.html
│   │   └── trends_analysis.html
│   │
│   ├── production/                   (3 → 14 file)
│   │   ├── recipe_list.html
│   │   ├── recipe_form.html
│   │   ├── recipe_detail.html
│   │   ├── production_order_list.html     🆕
│   │   ├── production_order_form.html     🆕
│   │   ├── production_order_detail.html   🆕
│   │   ├── bom_list.html                  🆕
│   │   ├── bom_form.html                  🆕
│   │   ├── bom_detail.html                🆕
│   │   ├── production_scheduling.html     🆕
│   │   ├── material_consumption.html      🆕
│   │   ├── finished_goods_receipt.html    🆕
│   │   ├── production_waste.html          🆕
│   │   └── production_costing.html        🆕
│   │
│   ├── marketing/                    (5 → 11 file)
│   │   ├── campaign.html
│   │   ├── add_campaign.html
│   │   ├── discount.html
│   │   ├── loyalty_members.html
│   │   ├── voucher_list.html              🆕
│   │   ├── voucher_form.html              🆕
│   │   ├── voucher_claim_log.html         🆕
│   │   ├── customer_segment_list.html     🆕
│   │   ├── customer_segment_form.html     🆕
│   │   └── promotion_calendar.html        🆕
│   │
│   ├── master_data/                  (13 → 21 file)
│   │   ├── categories_list.html
│   │   ├── category_form.html
│   │   ├── units_list.html
│   │   ├── unit_form.html
│   │   ├── vendors_list.html
│   │   ├── vendor_form.html
│   │   ├── customers.html
│   │   ├── customers_list.html
│   │   ├── customer_detail.html
│   │   ├── customer_form.html
│   │   ├── locations.html
│   │   ├── stock_opname_session_detail.html
│   │   ├── tax_list.html                  🆕
│   │   ├── tax_form.html                  🆕
│   │   ├── payment_terms_list.html        🆕
│   │   ├── payment_terms_form.html        🆕
│   │   ├── bank_accounts.html             🆕
│   │   ├── bank_account_form.html         🆕
│   │   ├── reason_codes.html              🆕
│   │   └── tags_list.html                 🆕
│   │
│   ├── accounting/                   🆕 FOLDER (12 file)
│   │   ├── chart_of_accounts.html
│   │   ├── chart_of_accounts_form.html
│   │   ├── journal_entry_list.html
│   │   ├── journal_entry_form.html
│   │   ├── journal_entry_detail.html
│   │   ├── general_ledger.html
│   │   ├── trial_balance.html
│   │   ├── balance_sheet.html
│   │   ├── cash_flow.html
│   │   ├── accounts_payable.html
│   │   ├── accounts_receivable.html
│   │   └── payment_voucher_form.html
│   │
│   ├── print/                        🆕 FOLDER (11 file)
│   │   ├── print_receipt.html
│   │   ├── print_invoice.html
│   │   ├── print_quotation.html
│   │   ├── print_sales_order.html
│   │   ├── print_purchase_order.html
│   │   ├── print_delivery_note.html
│   │   ├── print_packing_slip.html
│   │   ├── print_credit_note.html
│   │   ├── print_payment_receipt.html
│   │   ├── print_stock_opname.html
│   │   └── print_production_order.html
│   │
│   ├── reports/                      (20 → 25 file)
│   │   ├── reporting.html
│   │   ├── base_report.html
│   │   ├── sales_report.html
│   │   ├── sales_history.html
│   │   ├── sales_history_product.html
│   │   ├── report_sales_by_outlet.html
│   │   ├── report_sales_by_payment.html
│   │   ├── report_sales_by_product.html
│   │   ├── report_inventory_stock.html
│   │   ├── report_inventory_log.html
│   │   ├── report_inventory_low.html
│   │   ├── report_profit_loss_detail.html
│   │   ├── requisition_report.html
│   │   ├── purchasing_report.html
│   │   ├── transfer_report.html
│   │   ├── transaction_summary.html
│   │   ├── activity_log.html
│   │   ├── report_production.html         🆕
│   │   ├── report_expiry.html             🆕
│   │   ├── report_customer_lifetime.html  🆕
│   │   ├── report_staff_performance.html  🆕
│   │   └── report_inventory_age.html      🆕
│   │
│   ├── messages/                     (2 → 6 file)
│   │   ├── inbox.html
│   │   ├── notification.html
│   │   ├── compose.html                  🆕
│   │   ├── message_detail.html           🆕
│   │   ├── broadcast.html                🆕
│   │   └── message_templates.html        🆕
│   │
│   ├── settings/                     (10 → 18 file)
│   │   ├── users.html
│   │   ├── profile.html
│   │   ├── business_settings.html
│   │   ├── business_form_general.html
│   │   ├── business_profile.html
│   │   ├── business_feature_matrix.html
│   │   ├── system_status.html
│   │   ├── settings.html
│   │   ├── search.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── roles.html                    🆕
│   │   ├── role_form.html                🆕
│   │   ├── permission_matrix.html        🆕
│   │   ├── backup_restore.html           🆕
│   │   ├── email_settings.html           🆕
│   │   ├── notification_settings.html    🆕
│   │   ├── numbering_settings.html       🆕
│   │   └── api_keys.html                 🆕
│   │
│   └── etc/                          (3 → 5 file)
│       ├── error_403.html
│       ├── error_404.html
│       ├── error_500.html
│       ├── error_maintenance.html        🆕
│       └── error_session_expired.html    🆕
```

---

## 📊 Rekap Final per Modul

```
Base Components          14 →  23    ████████████████████  10/10
Authentication            2 →   8    ████████████████████  10/10
Onboarding                0 →   5    ████████████████████  10/10
Inventory                16 →  27    ████████████████████  10/10
Sales & POS              7  →  22    ████████████████████  10/10
Production               3  →  14    ████████████████████  10/10
Marketing                5  →  11    ████████████████████  10/10
Master Data             13  →  21    ████████████████████  10/10
Accounting               0  →  12    ████████████████████  10/10
Print Templates          0  →  11    ████████████████████  10/10
Reports                 20  →  25    ████████████████████  10/10
Messages                 2  →   6    ████████████████████  10/10
Settings                10  →  18    ████████████████████  10/10
Error Pages              3  →   5    ████████████████████  10/10
─────────────────────────────────────────────────────────────────
TOTAL                   95  → 208
```

---

## 🗓️ Urutan Pembuatan yang Disarankan

Jangan bikin semua sekaligus. Urutkan seperti ini:

```
MINGGU 1-2  ──  Cleanup + Base Components
               │ Hapus 21 file duplikat
               │ Buat 9 partial baru
               │ Buat print_base.html
               │
MINGGU 3    ──  Auth + Onboarding
               │ 6 file auth
               │ 5 file onboarding
               │
MINGGU 4-5  ──  Print Templates
               │ 11 file print (ini mudah, layout repetitif)
               │
MINGGU 6-8  ──  Sales (SO → Quotation → Invoice → Payment → Retur)
               │ 16 file — ini MODUL PALING KRITIS
               │
MINGGU 9-10 ──  Accounting Dasar
               │ COA, Journal Entry, General Ledger, Trial Balance
               │ 8 dari 12 file (sisanya phase 2)
               │
MINGGU 11-12 ──  Production
               │ Production Order, BOM, Material Consumption,
               │ Finished Goods, Waste
               │
MINGGU 13    ──  Inventory (tambahan)
               │ Batch, Expiry, Warehouse Zone, Requisition
               │
MINGGU 14    ──  Marketing + Messages + Master Data
               │ Semua sisa modul kecil
               │
MINGGU 15    ──  Reports + Settings + Error Pages
               │ Semua pelengkap
```

**Total: ~15 minggu untuk 1 developer frontend.**

---

Tinggal saya bantu satu per satu file-nya kalau kamu siap mulai. Mau mulai dari mana?
 
# 🗺️ Mapping Database → Template (Realistis)

Skema kamu **26 tabel** vs rekomendasi saya **208 template** — ini gap besar. Mari kita sinkronkan.

---

## 1. Mapping Tabel → Template (Yang BISA Dibuat Sekarang)

### 📦 Master Data — 7 Tabel → 14 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
_categories                        categories_list.html
                                   category_form.html

_units                             units_list.html
                                   unit_form.html

_vendors                           vendors_list.html
                                   vendor_form.html
                                   supplier_evaluation.html (aggregasi)

_taxes                             tax_list.html
                                   tax_form.html

lumra_config_locations             locations.html

lumra_config_customers             customers.html
                                   customers_list.html
                                   customer_detail.html
                                   customer_form.html

auth_user + lumra_config_userprofile  users.html
                                      profile.html
```

---

### 📦 Product Management — 4 Tabel → 3 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
lumra_config_products              products.html
lumra_config_productvariants       product_details.html (tab variants)
lumra_config_productattribute_items product_details.html (tab attributes)
product_details_view               product_details.html (data source utama)
```

**Catatan:** Tidak perlu `product_list.html` terpisah — cukup `products.html` dengan toggle grid/table.

---

### 📦 Stock Management — 4 Tabel → 11 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
lumra_config_stock                 stock_overview.html
                                   stock_movement.html
                                   stock_movement_form.html
                                   stock_planning.html

lumra_config_stockopname_session   stock_opname_locations.html
                                   stock_opname_approvals.html
                                   stock_opname_session_detail.html

lumra_config_stockopname_item      stock_opname_form.html
                                   stock_opname_approval_detail.html

lumra_config_supplier_prices       supplier_price_list.html
                                   supplier_price_form.html
                                   supplier_price_confirm_delete.html
```

**Pertanyaan penting:** `lumra_config_stock` ini snapshot atau ada movement log-nya? Kalau hanya snapshot (qty saat ini), kamu butuh tabel movement log terpisah. Lihat rekomendasi di bagian 3.

---

### 📦 Inventory Workflow — 4 Tabel → 6 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
lumra_config_requisitions          requisition_list.html
                                   requisition_detail.html
                                   requisition_form.html

lumra_config_requisitionitem       (embedded di requisition_form.html)
                                   (embedded di requisition_detail.html)

lumra_config_transfers             transfer_list.html
                                   transfer_detail.html

lumra_config_transferitem          transfer_form.html
                                   (embedded di transfer_detail.html)
```

**Catatan:** Sebelumnya tidak ada `transfer_list/detail/form` — ini baru ditambahkan karena tabelnya ada.

---

### 📦 Orders — 2 Tabel → 5 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
lumra_config_orders                pos.html (create order)
                                   order_list.html
                                   order_detail.html
                                   sales_history.html (report view)

lumra_config_orderitems            (embedded di pos.html cart)
                                   (embedded di order_detail.html line items)
```

**Pertanyaan penting:** `lumra_config_orders` ini mencakup apa saja? Apakah ada field `status` yang bisa merepresentasikan:
- `draft` → seperti quotation
- `confirmed` → seperti sales order
- `invoiced` → seperti invoice
- `completed` → selesai
- `cancelled` → batal

Jika ya, kamu **tidak perlu** tabel quotation/invoice terpisah. Cukup satu tabel dengan status flow.

---

### 📦 Production — 3 Tabel → 3 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
production_recipe_categories       recipe_list.html (filter by category)

production_recipes                 recipe_list.html
                                   recipe_form.html
                                   recipe_detail.html

production_recipe_ingredients      (embedded di recipe_form.html)
                                   (embedded di recipe_detail.html)
```

---

### 📦 User Management — 2 Tabel → 8 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
auth_user                          login.html
                                   register.html
                                   forgot_password.html
                                   reset_password.html
                                   users.html

lumra_config_userprofile           profile.html
                                   lock_screen.html
                                   two_factor.html
```

---

### 📦 Sales & Target — 1 Tabel → 2 Template ✅

```
TABEL                              TEMPLATE
─────────────────────────────────  ──────────────────────────────────────
lumra_config_sales_targets         sales_dashboard.html (KPI vs target)
                                   sales_performance.html (detail target vs actual)
```

---

## 2. Template yang TIDAK BISA Dibuat (Tidak Ada Tabel)

```
TEMPLATE                           ALASAN                           KEBUTUHAN
─────────────────────────────────  ────────────────────────────────  ────────────
quotation_*.html (3 file)          Tidak ada tabel quotation        RENDAH — bisa pakai order status "draft"
invoice_*.html (3 file)            Tidak ada tabel invoice          RENDAH — bisa pakai order status "invoiced"
payment_*.html (2 file)            Tidak ada tabel payment          SEDANG — perlu track pembayaran
retur_*.html (3 file)              Tidak ada tabel retur            TINGGI — bisnis pasti ada retur
voucher_*.html (3 file)            Tidak ada tabel voucher          RENDAH — fase 2
customer_segment_*.html (2 file)   Tidak ada tabel segment          RENDAH — fase 2
accounting_*.html (12 file)        Tidak ada tabel COA/jurnal       SEDANG — fase 2
batch_*.html (3 file)              Tidak ada tabel batch            TINGGI — kritis untuk F&B
expiry_tracking.html               Tidak ada tabel batch/expiry     TINGGI — kritis untuk F&B
warehouse_zones_*.html (2 file)    Tidak ada tabel zone             RENDAH — fase 2
production_order_*.html (3 file)   Tidak ada tabel production order SEDANG — recipe saja cukup dulu
bom_*.html (3 file)                Tidak ada tabel BOM terpisah     RENDAH — recipe = BOM
production_scheduling.html         Tidak ada tabel scheduling       RENDAH — fase 2
material_consumption.html          Tidak ada tabel consumption      SEDANG
finished_goods_receipt.html        Tidak ada tabel FG receipt       SEDANG
production_waste.html              Tidak ada tabel waste            RENDAH
production_costing.html            Bisa dari view/aggregasi          RENDAH — bisa fase 2
report_expiry.html                 Tidak ada data expiry            TINGGI — kalau F&B
report_customer_lifetime.html      Bisa dari aggregasi orders       RENDAH — fase 2
report_staff_performance.html      Tidak ada track staff per tx     RENDAH — cek order ada staff_id?
report_inventory_age.html          Tidak ada data tanggal masuk     SEDANG
adjustment_reasons.html            Tidak ada tabel reasons          RENDAH — hardcode dulu
reason_codes.html                  Sama seperti atas                RENDAH
```

---

## 3. Tabel yang Disarankan Ditambahkan

### 🔴 Wajib (Bisnis Tidak Bisa Jalan Tanpa Ini)

```sql
-- 1. STOCK MOVEMENT LOG
-- lumra_config_stock hanya snapshot, ini untuk audit trail
CREATE TABLE lumra_config_stockmovement (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id      BIGINT NOT NULL,          -- FK → products
    location_id     BIGINT NOT NULL,          -- FK → locations
    quantity        DECIMAL(15,4) NOT NULL,   -- positif = masuk, negatif = keluar
    movement_type   VARCHAR(20) NOT NULL,     -- 'purchase','sale','adjustment','transfer_in','transfer_out','opname','production_in','production_out'
    reference_id    BIGINT NULL,              -- FK ke orders/transfers/opname session (polymorphic)
    reference_type  VARCHAR(30) NULL,         -- 'order','transfer','opname_session'
    notes           TEXT NULL,
    created_by      BIGINT NOT NULL,          -- FK → auth_user
    created_at      DATETIME NOT NULL DEFAULT NOW()
);

-- 2. RETUR / REFUND
CREATE TABLE lumra_config_returns (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    return_code     VARCHAR(50) NOT NULL UNIQUE,
    order_id        BIGINT NOT NULL,          -- FK → orders (order asal)
    customer_id     BIGINT NULL,              -- FK → customers
    return_date     DATETIME NOT NULL,
    subtotal        DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_amount      DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_amount    DECIMAL(15,2) NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/approved/completed/cancelled
    reason          TEXT NULL,
    notes           TEXT NULL,
    created_by      BIGINT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT NOW()
);

CREATE TABLE lumra_config_returnitems (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    return_id       BIGINT NOT NULL,          -- FK → returns
    product_id      BIGINT NOT NULL,          -- FK → products
    quantity        DECIMAL(15,4) NOT NULL,
    unit_price      DECIMAL(15,2) NOT NULL,
    subtotal        DECIMAL(15,2) NOT NULL,
    reason          VARCHAR(255) NULL
);
```

### 🟡 Sangat Disarankan (Khusus F&B)

```sql
-- 3. BATCH / EXPIRY TRACKING
CREATE TABLE lumra_config_product_batches (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id      BIGINT NOT NULL,          -- FK → products
    batch_code      VARCHAR(100) NOT NULL,
    location_id     BIGINT NOT NULL,          -- FK → locations
    quantity        DECIMAL(15,4) NOT NULL,
    production_date DATE NULL,
    expiry_date     DATE NULL,
    cost_price      DECIMAL(15,2) NULL,       -- harga beli batch ini
    notes           TEXT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL DEFAULT NOW()
);

-- 4. PAYMENT TRACKING (jika belum ada di orders)
-- Cek: apakah lumra_config_orders sudah punya field payment_method, paid_amount, change_amount?
-- Jika BELUM, tambah tabel ini:
CREATE TABLE lumra_config_payments (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    payment_code    VARCHAR(50) NOT NULL UNIQUE,
    order_id        BIGINT NOT NULL,          -- FK → orders
    payment_method  VARCHAR(30) NOT NULL,     -- 'cash','card','qris','transfer'
    amount          DECIMAL(15,2) NOT NULL,
    reference_no    VARCHAR(100) NULL,        -- nomor referensi (card/qris)
    paid_at         DATETIME NOT NULL,
    created_by      BIGINT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT NOW()
);
```

### 🟢 Opsional (Fase 2)

```sql
-- 5. DISCOUNT / VOUCHER (fase 2)
-- 6. ACCOUNTING (fase 2)
-- 7. CUSTOMER SEGMENTS (fase 2)
```

---

## 4. Template Final — Disesuaikan dengan Database

### Hitung Ulang Realistis

```
KOMPONEN                          FILE
────────────────────────────────  ────
Base Components (existing)        14
Base Components (baru)             9
Auth (existing)                    2
Auth (baru)                        5
Onboarding (baru)                  5
Inventory (existing)              14
Inventory (baru - transfer)        3
Sales/POS (existing + sesuaikan)   5
Sales/POS (baru - order CRUD)      2
Production (existing)              3
Production (baru - jika ada tabel) 0   ← tidak ada tabel, skip dulu
Marketing (existing)               4
Master Data (existing)            11
Master Data (baru - tax)           2
Reports (existing)                17
Reports (baru)                     1   ← hanya yang bisa dari aggregasi
Messages (existing)                2
Settings (existing)               11
Error Pages (existing)             3
─────────────────────────────────────
TOTAL SEKARANG (tanpa tabel baru)  113
TOTAL SETELAH TAMBAH 4 TABEL       131
TOTAL PRINT TEMPLATES              8
─────────────────────────────────────
GRAND TOTAL REALISTIS              139
```

---

## 5. Mapping Lengkap (Tabel → Template) — Visual

```
_categories ─────────────────────┐
_units ──────────────────────────┤
_vendors ────────────────────────┤→  MASTER DATA (14 template)
_taxes ──────────────────────────┤
_locations ──────────────────────┤
_customers ──────────────────────┘

_products ───────────────────────┐
_productvariants ────────────────┤→  PRODUCT (3 template)
_productattribute_items ─────────┤
product_details_view ────────────┘

_stock ──────────────────────────┐
_stockopname_session ────────────┤→  STOCK (11 template)
_stockopname_item ───────────────┤
_supplier_prices ────────────────┘

_requisitions ───────────────────┐
_requisitionitem ────────────────┤→  INVENTORY WORKFLOW (6 template)
_transfers ──────────────────────┤
_transferitem ───────────────────┘

_orders ─────────────────────────┐→  ORDERS (5 template)
_orderitems ─────────────────────┘

_recipe_categories ─────────────┐
_recipes ───────────────────────┤→  PRODUCTION (3 template)
_recipe_ingredients ────────────┘

_sales_targets ──────────────────┼→  SALES DASHBOARD (2 template)

auth_user ───────────────────────┐→  AUTH + USER (8 template)
_userprofile ────────────────────┘

═══════════════════════════════════════════════
TABEL BARU (jika ditambahkan):
═══════════════════════════════════════════════

_stockmovement ──────────────────┼→  stock_movement.html, stock_movement_form.html
                                   stock_planning.html (improvement)

_returns + _returnitems ─────────┼→  retur_list.html, retur_form.html
                                   retur_detail.html (3 template)

_product_batches ────────────────┼→  batch_list.html, batch_form.html
                                   batch_detail.html, expiry_tracking.html
                                   report_expiry.html (5 template)

_payments ───────────────────────┼→  payment_list.html, payment_form.html
                                   print_receipt.html (3 template)
```

---

## 6. File yang Harus Dibuat Sekarang (Urutkan)

### Tahap 1: Cleanup (Hari 1-2)
```
HAPUS (21 file duplikat):
  ├── customer.html
  ├── vendor_list.html
  ├── product_list.html
  ├── campaign_list.html
  ├── location_list.html
  ├── add_stock_movement.html
  ├── sales_report_after.html
  ├── stock_overview.html (di reports/)
  └── financial_reports.html (di reports/)

RENAME (1 file):
  └── sales_insight/dashboard.html → sales_insight/sales_dashboard.html
```

### Tahap 2: Base Components (Hari 3-5)
```
BUAT (9 file):
  ├── partials/empty_state.html
  ├── partials/pagination.html
  ├── partials/data_table.html
  ├── partials/breadcrumb.html
  ├── partials/confirm_modal.html
  ├── partials/tabs.html
  ├── partials/badge.html
  ├── partials/stepper.html
  └── partials/print_base.html
```

### Tahap 3: Auth + Onboarding (Hari 6-8)
```
BUAT (11 file):
  ├── auth/forgot_password.html
  ├── auth/reset_password.html
  ├── auth/verify_email.html
  ├── auth/two_factor.html
  ├── auth/lock_screen.html
  ├── onboarding/welcome.html
  ├── onboarding/step_business.html
  ├── onboarding/step_location.html
  ├── onboarding/step_category.html
  └── onboarding/step_complete.html
```

### Tahap 4: Sesuaikan Existing (Hari 9-12)
```
PASTIKAN ini terhubung ke tabel yang benar:
  ├── products.html          ← query dari product_details_view
  ├── product_details.html   ← tabs: info | variants | attributes | stock
  ├── stock_overview.html    ← query dari lumra_config_stock
  ├── stock_movement.html    ← PERHATIAN: butuh _stockmovement tabel
  ├── pos.html               ← create ke lumra_config_orders + orderitems
  ├── recipe_form.html       ← ingredients ke production_recipe_ingredients
  ├── sales_dashboard.html   ← KPI dari orders + sales_targets
  └── locations.html         ← dari lumra_config_locations
```

### Tahap 5: Transfer (Hari 13-14) 🆕
```
BUAT (3 file — tabelnya sudah ada!):
  ├── inventory/transfer_list.html      ← dari _transfers
  ├── inventory/transfer_form.html      ← _transfers + _transferitem
  └── inventory/transfer_detail.html    ← _transfers + _transferitem
```

### Tahap 6: Order Management (Hari 15-17) 🆕
```
BUAT (2 file — tabelnya sudah ada!):
  ├── sales/order_list.html             ← dari _orders (bukan sales_history)
  └── sales/order_detail.html           ← _orders + _orderitems
```

### Tahap 7: Print (Hari 18-20) 🆕
```
BUAT (8 file — pakai data dari tabel existing):
  ├── print/print_receipt.html          ← dari _orders + _orderitems
  ├── print/print_sales_order.html      ← dari _orders + _orderitems
  ├── print/print_purchase_order.html   ← dari _orders (tipe purchase)
  ├── print/print_delivery_note.html    ← dari _transfers
  ├── print/print_stock_opname.html     ← dari _stockopname_session + item
  ├── print/print_quotation.html        ← dari _orders (status draft)
  ├── print/print_invoice.html          ← dari _orders (status invoiced)
  └── print/print_credit_note.html      ← dari _returns (jika tabel ditambahkan)
```

---

## 7. Keputusan yang Perlu Kamu Ambil

Sebelum lanjut, jawab ini:

```
NO  PERTANYAAN                          DAMPAK
───  ──────────────────────────────────  ─────────────────────────────────
①   _orders punya field status apa saja?  Menentukan apakah perlu tabel
                                         quotation/invoice terpisah

②   _orders punya field payment_method,   Menentukan apakah perlu tabel
     paid_amount, change_amount?          _payments terpisah

③   _orders punya field staff_id /       Menentukan apakah bisa buat
     created_by?                          report staff performance

④   _stock itu snapshot atau movement     Menentukan apakah perlu tabel
     log?                                 _stockmovement

⑤   Produk kamu ada yang punya expiry     Menentukan prioritas tabel
     date atau batch number?              _product_batches

⑥   _orders bisa berfungsi ganda         Menentukan apakah perlu
     (POS + SO + Invoice)?                pemisahan modul
```

Jawab 6 pertanyaan itu, saya bisa finalisasi daftar file **persis** yang kamu buat — tidak lebih, tidak kurang.

 
# 🔍 Diagnosa Database LUMRA ERP

Jawaban langsung: **Tidak cukup.** Ada gap kritis yang menghambat fitur inti ERP.

---

## Diagnosa Per Tabel

### ✅ Sudah Cukup (Tidak Perlu Ubah)

```
TABEL                          STATUS        CATATAN
─────────────────────────────  ────────────  ──────────────────────────────
_categories                    ✅ Cukup      Hierarchi parent_id cukup
_units                         ✅ Cukup      Daftar satuan
_taxes                         ✅ Cukup      Rate + tipe
_vendors                       ✅ Cukup      Info supplier
lumra_config_locations         ✅ Cukup      Daftar lokasi/outlet
production_recipe_categories   ✅ Cukup      Grouping resep
product_details_view           ✅ Cukup      View untuk query cepat
```

### ⚠️ Perlu Cek Field-nya

```
TABEL                          YANG HARUS ADA                   KEMUNGKINAN MASALAH
─────────────────────────────  ───────────────────────────────  ──────────────────────
lumra_config_products          - sell_price (bukan hanya cost)  Harga jual kemana?
                               - sku_code / barcode
                               - is_active
                               - min_stock (untuk alert)

lumra_config_customers         - phone (bukan hanya mobile)     Kadang ada 2 nomor
                               - customer_type (retail/wholesale)
                               - is_active
                               - points_balance (jika loyalty)

lumra_config_orders            - Lihat analisis lengkap di bawah ⬇️

lumra_config_userprofile       - role / position               Butuh untuk permission
                               - default_location             Kasir default di outlet mana
```

### 🔴 Gap Kritis — Tidak Ada Sama Sekali

```
GAP                              DAMPAK TANPA INI
───────────────────────────────  ────────────────────────────────────────────
Stock Movement Log               Tidak bisa trace: "stok berubah karena apa?"
                                Tidak ada audit trail
                                Tidak bisa buat laporan pergerakan stok
                                Stok berubah silently = rekayasa mudah

Returns / Retur                  Tidak bisa proses barang dikembalikan
                                Uang hilang tanpa catatan
                                Stok tidak bisa kembali

Payments (terpisah dari order)   Satu order tidak bisa dibayar 2 metode
                                Tidak ada bukti pembayaran terpisah
                                Tidak bisa rekonsiliasi kas
```

### 🟡 Gap Penting — F&B / Retail Butuh Ini

```
GAP                              DAMPAK TANPA INI
───────────────────────────────  ────────────────────────────────────────────
Batch / Expiry Tracking          Produk kedaluwarsa tidak terdeteksi
                                Tidak bisa FEFO (First Expired First Out)
                                Risk keracunan = masuk hukum

Unit Conversions                 Beli per kg, jual per gram → error kalkulasi
                                Resep butuh 500ml, stok 1 liter → manual

Cashier Shift / Drawer           Tidak bisa hitung selisih kas per shift
                                Uang hilang tidak traceable
                                SERING DIPAKAI DI POS

Adjustment Reasons               Stok diadjust tapi "kenapa?" tidak tercatat
```

---

## Analisis Detail: `lumra_config_orders`

Tabel ini adalah **jantung sistem**. Saya menduga saat ini kira-kira seperti ini:

```sql
-- KEMUNGKINAN SKEMA SAAT INI
lumra_config_orders (
    id, order_code, customer_id, location_id,
    subtotal, tax_amount, discount_amount, total_amount,
    status, notes, created_by, created_at
)

lumra_config_orderitems (
    id, order_id, product_id, quantity, unit_price, subtotal
)
```

### Yang Kurang di Orders:

```
FIELD YANG HARUS ADA              ALASAN
────────────────────────────────  ──────────────────────────────────────
order_type                        Bedakan: 'pos' / 'sales_order' / 'purchase'
payment_status                    Terpisah dari order status.
                                  Order bisa 'completed' tapi 'unpaid'
payment_method                    Cash/card/qris/transfer
paid_amount                       Berapa yang sudah dibayar
change_amount                     Kembalian (khusus cash)
staff_id / cashier_id             Siapa kasir yang memproses?
                                  Beda dari created_by (bisa admin input manual)
table_number / order_type_pos     Makan di tempat / bungkus / delivery
```

### Kenapa Payments Perlu Tabel Terpisah?

```
SKENARIO: Customer beli Rp 500.000
          Bayar QRIS Rp 300.000
          Bayar Cash Rp 200.000

Jika semua di satu tabel orders:
  ❌ payment_method simpan apa? "qris,cash"? → susah query
  ❌ paid_amount 500.000 tapi referensi qris mana?
  ❌ Cash drawer tidak match (harus tau mana yang cash)

Jika ada tabel payments terpisah:
  ✅ Payment 1: qris, 300.000, ref: QRIS-XYZ123
  ✅ Payment 2: cash, 200.000, ref: null
  ✅ Query: total cash per shift = mudah
  ✅ Query: total qris per hari = mudah
  ✅ Rekonsiliasi bank = mudah
```

---

## Skema Tabel yang Harus Ditambahkan

### 🔴 WAJIB — 4 Tabel

#### 1. Stock Movement Log
```sql
CREATE TABLE lumra_config_stockmovement (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Referensi produk & lokasi
    product_id      BIGINT NOT NULL,
    location_id     BIGINT NOT NULL,
    
    -- Pergerakan
    quantity        DECIMAL(15,4) NOT NULL,    -- POSITIF = masuk, NEGATIF = keluar
    movement_type   VARCHAR(30) NOT NULL,      -- Lihat enum di bawah
    
    -- Referensi sumber pergerakan (polymorphic)
    reference_id    BIGINT NULL,               -- ID dari tabel sumber
    reference_type  VARCHAR(30) NULL,          -- Nama tabel sumber
    
    -- Meta
    notes           TEXT NULL,
    created_by      BIGINT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Index untuk query cepat
    INDEX idx_product_location (product_id, location_id),
    INDEX idx_movement_type (movement_type),
    INDEX idx_reference (reference_type, reference_id),
    INDEX idx_created_at (created_at)
);

-- Enum movement_type:
-- 'purchase_in'      → Barang masuk dari pembelian
-- 'sale_out'         → Barang keluar dari penjualan
-- 'adjustment_in'    → Penyesuaian stok (tambah)
-- 'adjustment_out'   → Penyesuaian stok (kurang)
-- 'transfer_in'      → Terima transfer dari lokasi lain
-- 'transfer_out'     → Kirim transfer ke lokasi lain
-- 'opname_adjust'    → Hasil stock opname
-- 'return_in'        → Barang retur masuk
-- 'production_in'    → Hasil produksi masuk
-- 'production_out'   → Bahan baku keluar untuk produksi
-- 'requisition_in'   → Terima requisition
-- 'requisition_out'  → Keluar untuk requisition
```

#### 2. Returns
```sql
CREATE TABLE lumra_config_returns (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    return_code     VARCHAR(50) NOT NULL UNIQUE,
    
    -- Referensi
    order_id        BIGINT NOT NULL,           -- Order asal
    customer_id     BIGINT NULL,               -- Customer (bisa null jika walk-in)
    location_id     BIGINT NOT NULL,           -- Lokasi retur diproses
    
    -- Nilai
    subtotal        DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_amount      DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_amount    DECIMAL(15,2) NOT NULL DEFAULT 0,
    refund_method   VARCHAR(30) NULL,          -- 'cash' / 'transfer' / 'credit_note'
    
    -- Status & Alasan
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    reason          TEXT NULL,
    notes           TEXT NULL,
    
    -- Audit
    approved_by     BIGINT NULL,
    approved_at     DATETIME NULL,
    created_by      BIGINT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_order (order_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

CREATE TABLE lumra_config_returnitems (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    return_id       BIGINT NOT NULL,
    product_id      BIGINT NOT NULL,
    quantity        DECIMAL(15,4) NOT NULL,
    unit_price      DECIMAL(15,2) NOT NULL,
    subtotal        DECIMAL(15,2) NOT NULL,
    reason          VARCHAR(255) NULL,         -- Alasan per item: 'expired', 'damaged', 'wrong_item'
    
    FOREIGN KEY (return_id) REFERENCES lumra_config_returns(id) ON DELETE CASCADE,
    INDEX idx_return (return_id),
    INDEX idx_product (product_id)
);

-- Enum status returns:
-- 'pending'    → Baru diajukan
-- 'approved'   → Disetujui, menunggu proses
-- 'completed'  → Retur selesai, stok sudah kembali
-- 'rejected'   → Ditolak
-- 'cancelled'  → Dibatalkan
```

#### 3. Payments
```sql
CREATE TABLE lumra_config_payments (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    payment_code    VARCHAR(50) NOT NULL UNIQUE,
    
    -- Referensi
    order_id        BIGINT NOT NULL,
    
    -- Detail pembayaran
    payment_method  VARCHAR(30) NOT NULL,      -- 'cash', 'card', 'qris', 'transfer', 'ewallet'
    amount          DECIMAL(15,2) NOT NULL,
    reference_no    VARCHAR(100) NULL,         -- Nomor referensi (card auth code, qris ref)
    card_type       VARCHAR(20) NULL,          -- 'debit', 'credit' (jika metode card)
    
    -- Meta
    paid_at         DATETIME NOT NULL,
    notes           TEXT NULL,
    created_by      BIGINT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_order (order_id),
    INDEX idx_method (payment_method),
    INDEX idx_paid_at (paid_at)
);
```

#### 4. Batch / Expiry
```sql
CREATE TABLE lumra_config_productbatches (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Identitas
    batch_code      VARCHAR(100) NOT NULL,
    product_id      BIGINT NOT NULL,
    location_id     BIGINT NOT NULL,
    
    -- Stok
    initial_quantity DECIMAL(15,4) NOT NULL,   -- Qty saat pertama masuk
    current_quantity DECIMAL(15,4) NOT NULL,    -- Qty saat ini (dikurangi penjualan/opname)
    
    -- Tanggal penting
    received_date   DATE NOT NULL,              -- Tanggal diterima
    production_date DATE NULL,                  -- Tanggal produksi (jika tahu)
    expiry_date     DATE NULL,                  -- Tanggal kadaluarsa
    
    -- Harga
    cost_price      DECIMAL(15,2) NULL,         -- Harga beli batch ini
    
    -- Status
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,  -- False = sudah habis/expired/dibuang
    notes           TEXT NULL,
    
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE INDEX idx_batch_product_location (batch_code, product_id, location_id),
    INDEX idx_product (product_id),
    INDEX idx_location (location_id),
    INDEX idx_expiry (expiry_date),
    INDEX idx_active (is_active)
);
```

---

### 🟡 DISARANKAN — 3 Tabel

#### 5. Unit Conversions
```sql
CREATE TABLE lumra_config_unitconversions (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id      BIGINT NOT NULL,
    from_unit_id    BIGINT NOT NULL,            -- Satuan asal (misal: kg)
    to_unit_id      BIGINT NOT NULL,            -- Satuan tujuan (misal: gram)
    conversion_factor DECIMAL(15,6) NOT NULL,   -- 1 kg = 1000 gram → factor = 1000
    
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE INDEX idx_product_from_to (product_id, from_unit_id, to_unit_id)
);

-- Contoh data:
-- product: Tepung, from_unit: kg, to_unit: gram, factor: 1000
-- product: Minyak, from_unit: liter, to_unit: ml, factor: 1000
-- product: Telur, from_unit: kg, to_unit: butir, factor: 16.67 (1kg ≈ 16-17 butir)
```

#### 6. Cashier Shifts
```sql
CREATE TABLE lumra_config_cashiershifts (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Siapa & dimana
    user_id         BIGINT NOT NULL,            -- Kasir
    location_id     BIGINT NOT NULL,            -- Outlet
    
    -- Waktu
    opened_at       DATETIME NOT NULL,
    closed_at       DATETIME NULL,              -- NULL = shift masih buka
    
    -- Uang
    opening_cash    DECIMAL(15,2) NOT NULL DEFAULT 0,  -- Uang awal di laci
    expected_cash   DECIMAL(15,2) NOT NULL DEFAULT 0,  -- Total cash yang seharusnya
    actual_cash     DECIMAL(15,2) NOT NULL DEFAULT 0,  -- Uang yang dihitung saat tutup
    difference      DECIMAL(15,2) NOT NULL DEFAULT 0,  -- Selisih (actual - expected)
    
    -- Status
    status          VARCHAR(20) NOT NULL DEFAULT 'open',
    closing_notes   TEXT NULL,
    
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_location (user_id, location_id),
    INDEX idx_status (status),
    INDEX idx_opened_at (opened_at)
);

-- Enum status:
-- 'open'      → Shift aktif
-- 'closed'    → Sudah ditutup
```

#### 7. Adjustment Reasons
```sql
CREATE TABLE lumra_config_adjustmentreasons (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    code            VARCHAR(20) NOT NULL UNIQUE,  -- 'DAMAGED', 'EXPIRED', 'THEFT', 'CORRECTION'
    name            VARCHAR(100) NOT NULL,
    effect          VARCHAR(10) NOT NULL,         -- 'plus' atau 'minus'
    description     TEXT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Contoh data:
-- DAMAGED    | Barang Rusak         | minus
-- EXPIRED    | Kadaluarsa            | minus
-- THEFT      | Kehilangan/Curi       | minus
-- CORRECTION | Koreksi Sistem Error  | plus/minus
-- FOUND      | Ditemukan             | plus
```

---

## Field yang Perlu Ditambahkan ke Tabel Existing

### `lumra_config_products`
```sql
ALTER TABLE lumra_config_products ADD COLUMN IF NOT EXISTS sell_price DECIMAL(15,2) DEFAULT 0;
ALTER TABLE lumra_config_products ADD COLUMN IF NOT EXISTS barcode VARCHAR(100) NULL;
ALTER TABLE lumra_config_products ADD COLUMN IF NOT EXISTS min_stock DECIMAL(15,4) DEFAULT 0;
ALTER TABLE lumra_config_products ADD COLUMN IF NOT EXISTS max_stock DECIMAL(15,4) DEFAULT 0;
ALTER TABLE lumra_config_products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE lumra_config_products ADD COLUMN IF NOT EXISTS track_batch BOOLEAN DEFAULT FALSE; -- apakah perlu tracking batch?
ALTER TABLE lumra_config_products ADD COLUMN IF NOT EXISTS has_expiry BOOLEAN DEFAULT FALSE;  -- apakah punya expiry?
```

### `lumra_config_orders`
```sql
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS order_type VARCHAR(20) NOT NULL DEFAULT 'pos';
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) NOT NULL DEFAULT 'unpaid';
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS payment_method VARCHAR(30) NULL;
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS paid_amount DECIMAL(15,2) DEFAULT 0;
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS change_amount DECIMAL(15,2) DEFAULT 0;
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS cashier_id BIGINT NULL;
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS shift_id BIGINT NULL;
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS table_number VARCHAR(20) NULL;
ALTER TABLE lumra_config_orders ADD COLUMN IF NOT EXISTS dining_option VARCHAR(20) NULL;
-- order_type: 'pos', 'sales_order', 'purchase'
-- payment_status: 'unpaid', 'partial', 'paid', 'refunded'
-- dining_option: 'dine_in', 'takeaway', 'delivery'
```

### `lumra_config_orderitems`
```sql
ALTER TABLE lumra_config_orderitems ADD COLUMN IF NOT EXISTS cost_price DECIMAL(15,2) DEFAULT 0;
ALTER TABLE lumra_config_orderitems ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(15,2) DEFAULT 0;
ALTER TABLE lumra_config_orderitems ADD COLUMN IF NOT EXISTS discount_percent DECIMAL(5,2) DEFAULT 0;
ALTER TABLE lumra_config_orderitems ADD COLUMN IF NOT EXISTS batch_id BIGINT NULL;
ALTER TABLE lumra_config_orderitems ADD COLUMN IF NOT EXISTS notes TEXT NULL;
-- batch_id: jika tracking batch aktif, catat batch mana yang digunakan
```

### `lumra_config_customers`
```sql
ALTER TABLE lumra_config_customers ADD COLUMN IF NOT EXISTS customer_type VARCHAR(20) DEFAULT 'retail';
ALTER TABLE lumra_config_customers ADD COLUMN IF NOT EXISTS points_balance INT DEFAULT 0;
ALTER TABLE lumra_config_customers ADD COLUMN IF NOT EXISTS total_purchases DECIMAL(15,2) DEFAULT 0;
ALTER TABLE lumra_config_customers ADD COLUMN IF NOT EXISTS visit_count INT DEFAULT 0;
ALTER TABLE lumra_config_customers ADD COLUMN IF NOT EXISTS last_purchase_at DATETIME NULL;
ALTER TABLE lumra_config_customers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
```

### `lumra_config_userprofile`
```sql
ALTER TABLE lumra_config_userprofile ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'staff';
ALTER TABLE lumra_config_userprofile ADD COLUMN IF NOT EXISTS default_location_id BIGINT NULL;
ALTER TABLE lumra_config_userprofile ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
-- role: 'admin', 'manager', 'supervisor', 'staff', 'cashier', 'warehouse'
```

### `lumra_config_stock`
```sql
ALTER TABLE lumra_config_stock ADD COLUMN IF NOT EXISTS reserved_quantity DECIMAL(15,4) DEFAULT 0;
ALTER TABLE lumra_config_stock ADD COLUMN IF NOT EXISTS available_quantity DECIMAL(15,4) GENERATED ALWAYS AS 
    (quantity - reserved_quantity) STORED;
-- available_quantity = qty fisik - qty yang sudah di-reserve oleh order belum diproses
```

---

## Rekap Keseluruhan

```
                    SEBELUM         SESUDAH        TAMBAHAN
                    ───────         ───────        ───────
Master Data            7               7             0
Product Management     4               4             0
Stock Management       4               4             0
Inventory Workflow     4               4             0
Orders                 2               2             0
Production             3               3             0
User Management        2               2             0
Sales & Target         1               1             0
───────────────────────────────────────────────────────────
TABEL BARU:           0               7             7
  - stockmovement      ⬆️ WAJIB
  - returns            ⬆️ WAJIB
  - returnitems        ⬆️ WAJIB
  - payments           ⬆️ WAJIB
  - productbatches     ⬆️ WAJIB
  - unitconversions    ⬆️ Disarankan
  - cashiershifts      ⬆️ Disarankan
  - adjustmentreasons  ⬆️ Disarankan
───────────────────────────────────────────────────────────
FIELD BARU:            -               -           ~25 field
  (di 5 tabel existing)
───────────────────────────────────────────────────────────
TOTAL                  26              33             7 tabel + 25 field
```

---

## Prioritas Implementasi

```
MINGGU 1  ──  stockmovement + field orders + field orderitems
              │ Ini FONDASI. Semua fitur lain bergantung pada ini.
              │
MINGGU 2  ──  payments + productbatches
              │ Pembayaran tracking + batch/expiry untuk F&B.
              │
MINGGU 3  ──  returns + returnitems
              │ Fitur retur, butuh payments dulu jadi referensi.
              │
MINGGU 4  ──  unitconversions + cashiershifts + adjustmentreasons
              │ Pelengkap operasional.
              │
MINGGU 5  ──  field tambahan (products, customers, userprofile, stock)
              │ Bisa paralel dengan minggu 1-4 sebenarnya.
```

---

## Relasi Baru (Visual)

```
                            ┌──────────────────────┐
                            │  lumra_config_orders │
                            └──────────┬───────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
         │ lumra_config_    │ │ lumra_config_│ │ lumra_config_    │
         │ orderitems       │ │ payments     │ │ returns          │
         │ (batch_id)───────┼─│              │ │                  │
         └──────────────────┘ └──────────────┘ └────────┬─────────┘
                                                              │
                                                              ▼
                                                   ┌──────────────────┐
                                                   │ lumra_config_    │
                                                   │ returnitems      │
                                                   └──────────────────┘

         ┌──────────────────┐      ┌──────────────────────────┐
         │ lumra_config_    │      │ lumra_config_productbatches│
         │ products         │      │ (batch_code, expiry_date) │
         │ (track_batch)────┼─────▶│                          │
         │ (has_expiry)─────┼─────▶│                          │
         └────────┬─────────┘      └──────────────────────────┘
                  │
                  ▼
         ┌──────────────────┐      ┌──────────────────────────┐
         │ lumra_config_    │      │ lumra_config_stockmovement│
         │ stock            │◀────│ (movement_type, qty,      │
         │ (reserved_qty)   │      │  reference_type/id)       │
         └──────────────────┘      └──────────────────────────┘
                                           ▲
                                           │ mencatat semua perubahan
         ┌──────────────────┐              │
         │ Semua tabel yang │──────────────┘
         │ ubah stok:       │
         │ - orders         │
         │ - transfers      │
         │ - stockopname    │
         │ - returns        │
         │ - requisitions   │
         └──────────────────┘
```

---


tanggal 11 April 2026
# 🔗 LUMRA ERP - Feature to File Mapping
**Which Files Support Which Business Features**  
*Generated: April 10, 2026*

---

## 📑 Quick Index
- [Sales & Transactions](#sales--transactions)
- [Inventory Management](#inventory-management)
- [Product Management](#product-management)
- [Stock Opname (Physical Count)](#stock-opname-physical-count)
- [Purchasing & Suppliers](#purchasing--suppliers)
- [Master Data](#master-data)
- [Marketing & Loyalty](#marketing--loyalty)
- [Production/Recipes](#productionrecipes)
- [Reports & Analytics](#reports--analytics)
- [User Management & Access](#user-management--access)
- [System & Administration](#system--administration)
- [Customer Management](#customer-management)

---

## 💰 Sales & Transactions

### Point of Sale (POS)
**Feature Purpose:** Real-time sales transactions at checkout  
**Related Templates:**
- `sales_insight/pos.html` - POS interface with shopping cart
- `sales_insight/dashboard.html` - Daily sales summary (shows POS performance)
- `master_data/customers.html` - Customer lookup during POS
- `sales_insight/sales_intelligence.html` - Sales analytics post-transaction

**Data Flow:** Customer → Items → Cart → Payment → pos.html processes → Dashboard shows results

**Connections:**
- POS creates transactions → viewed in `sales_report.html`
- Customer history → tracked in `sales_history.html`
- Payment methods → breakdown in `report_sales_by_payment.html`

---

### Daily Sales Tracking
**Feature Purpose:** Monitor sales throughout the day  
**Related Templates:**
- `sales_insight/dashboard.html` - Today's total sales, transaction count, top products
- `sales_insight/sales_performance.html` - Sales metrics & trends
- `reports/sales_report.html` - Detailed sales analysis
- `reports/transaction_summary.html` - Daily transaction overview

**KPI Display:** Uses `base/kpi_card.html` and `base/kpi_card_white.html`

**Typical Workflow:** Manager opens Dashboard → Views KPIs → Clicks "Detailed Report" → `sales_report.html`

---

### Sales History
**Feature Purpose:** Query past transactions  
**Related Templates:**
- `reports/sales_history.html` - All transactions (chronological)
- `reports/sales_history_product.html` - Sales by product
- `sales_insight/sales_performance.html` - Performance analysis
- `reports/transaction_summary.html` - Summary view

**Filters:** Date range, customer, payment method, location

---

### Sales by Location
**Feature Purpose:** Compare performance across outlets  
**Related Templates:**
- `reports/report_sales_by_outlet.html` - Sales per location
- `master_data/locations.html` - Location master data
- `sales_insight/sales_intelligence.html` - Market insights

**Used By:** Regional managers, executives

---

### Payment Processing
**Feature Purpose:** Record different payment types  
**Related Templates:**
- `sales_insight/pos.html` - Payment selector during POS
- `reports/report_sales_by_payment.html` - Payment breakdown analysis
- `reports/transaction_summary.html` - Payment summaries

**Payment Types Tracked:** Cash, Card, Mobile money, etc.

---

## 📦 Inventory Management

### Product Listing & Search
**Feature Purpose:** View & manage all products  
**Related Templates:**
- `inventory/products.html` - Main product dashboard
- `inventory/product_list.html` - Paginated product list
- `inventory/product_details.html` - Detailed product view
- `master_data/categories_list.html` - Product categories (linked)
- `settings/search.html` - Global search for products

**Stock Display:** Shows current stock per location using aggregation

**Navigation Path:** Dashboard → Inventory menu → `products.html` → Click product → `product_details.html`

---

### Stock Levels & Alerts
**Feature Purpose:** Monitor low stock situations  
**Related Templates:**
- `inventory/stock_overview.html` - Dashboard with low stock alerts
- `reports/report_inventory_low.html` - Low stock report
- `reports/report_inventory_stock.html` - Current stock levels
- `inventory/stock_movement.html` - Transaction history

**Alert Rules:** Products below minimum quantity flagged

**Actions from Alert:** 
1. Create purchase order in `inventory/stock_purchasing.html`
2. Create stock movement in `inventory/add_stock_movement.html`

---

### Stock by Location
**Feature Purpose:** Track inventory distributed across outlets  
**Related Templates:**
- `inventory/stock_overview.html` - Stock breakdown by location
- `master_data/locations.html` - Location master
- `inventory/stock_planning.html` - Allocation by location
- `reports/report_inventory_stock.html` - Stock level report

**Typical Use:** Rebalance stock → Use `inventory/stock_movement.html` to transfer

---

## 🏷️ Product Management

### Create/Edit Products
**Feature Purpose:** Add new products or modify existing ones  
**Related Templates:**
- `inventory/products.html` - Product list (edit action)
- `inventory/product_details.html` - View → Edit link
- Form uses component: `base/partials/form_field.html`
- Master data: `master_data/categories_list.html` (select category)

**Product Attributes:**
- Name, code, description
- Category (FK to categories)
- Unit of measure (FK to units)
- Price (cost, retail, wholesale)
- Reorder level (for low stock alerts)
- Status (active/inactive)

**Form Page Construction:**
```
page extends base.html
  ├── navbar.html
  ├── sidebar.html
  ├── form uses form_field.html (multiple times)
  │   ├── Product name (text)
  │   ├── Category (dropdown to categories_list data)
  │   ├── Unit (dropdown to units_list data)
  │   └── ... other fields ...
  └── Save/Cancel buttons
```

---

### Product Pricing
**Feature Purpose:** Define cost and selling prices  
**Related Templates:**
- `inventory/supplier_price_list.html` - Supplier pricing
- `inventory/supplier_price_form.html` - Add/edit supplier price
- Related to `inventory/stock_purchasing.html` (purchase orders)

**Price Types:**
- Cost price (from supplier)
- Retail price
- Wholesale price (if applicable)

**Connections:**
- Cost price → Used in P&L calculations (`reports/report_profit_loss_detail.html`)
- Retail price → Used in POS (`sales_insight/pos.html`)

---

### Supplier Price Management
**Feature Purpose:** Track pricing from different vendors  
**Related Templates:**
- `inventory/supplier_price_list.html` - All supplier prices
- `inventory/supplier_price_form.html` - Add/edit supplier price
- `inventory/supplier_price_confirm_delete.html` - Confirm deletion
- Connects to: `master_data/vendors_list.html` (vendor master)

**Price History:** MOQ (minimum order qty), effective dates for price changes

---

## 📊 Stock Opname (Physical Count)

### Create Stock Opname
**Feature Purpose:** Physical inventory count workflow  
**Related Templates:**
- `inventory/stock_opname_locations.html` - Select location to count
- `inventory/stock_opname_form.html` - Enter counted quantities
- `inventory/stock_opname_approvals.html` - Review submitted counts
- `inventory/stock_opname_approval_detail.html` - Approve/reject detail

**Workflow:**
```
1. Start: Click "New Stock Opname" in stock_opname_locations.html
2. Count: Enter actual quantities in stock_opname_form.html
3. Submit: Form submits for approval
4. Approve: Manager reviews in stock_opname_approvals.html
5. Approve Detail: Click opname → stock_opname_approval_detail.html
6. Finalize: Approval creates journal entry → Updates stock_movement.html
```

**Variance Tracking:** Shows current qty vs counted qty with discrepancy %

---

### Stock Opname History
**Feature Purpose:** View past physical counts and results  
**Related Templates:**
- `master_data/stock_opname_session_detail.html` - Historical session details
- `inventory/stock_opname_approvals.html` - Approved sessions archive
- `reports/activity_log.html` - Who counted, when, results

### Stock Opname Approvals
**Feature Purpose:** Review & approve submitted stock counts  
**Related Templates:**
- `inventory/stock_opname_approvals.html` - List of pending approvals
- `inventory/stock_opname_approval_detail.html` - Detail view with discrepancy analysis
- Modal: `base/approval_modal.html` (for approve/reject action)

**Trigger:** Used after `inventory/stock_opname_form.html` submission

---

## 🛒 Purchasing & Suppliers

### Purchase Orders
**Feature Purpose:** Create & track purchase orders to suppliers  
**Related Templates:**
- `inventory/stock_purchasing.html` - PO list & creation
- Linked to: `master_data/vendors_list.html` (select vendor)
- Linked to: `inventory/products.html` (select products)
- Linked to: `reports/purchasing_report.html` (PO analysis)

**PO Workflow:**
1. Create PO in `stock_purchasing.html` (select vendor, products, qty, expected date)
2. Submit for approval
3. Track delivery status
4. Receive goods → Create stock movement in `inventory/stock_movement.html`

---

### Supplier Management
**Feature Purpose:** Maintain vendor/supplier records  
**Related Templates:**
- `master_data/vendors_list.html` - Vendor list
- `master_data/vendor_list.html` - Alternative view
- `master_data/vendor_form.html` - Create/edit vendor info
- `inventory/supplier_price_list.html` - Pricing per supplier
- `reports/purchasing_report.html` - Vendor spending analysis

**Vendor Attributes:**
- Company name, contact person
- Phone, email, website
- Address, tax number
- Payment terms, status (active/inactive)

---

### Stock Requisitions
**Feature Purpose:** Inter-location stock request workflow  
**Related Templates:**
- `inventory/add_stock_movement.html` - Request stock transfer
- `reports/requisition_report.html` - Requisition history & tracking
- `inventory/stock_movement.html` - Shows fulfilled requisitions as movements

**Requisition Status:** Requested → Approved → Fulfilled → Received

---

## 🗂️ Master Data

### Categories
**Feature Purpose:** Organize products into logical groups  
**Related Templates:**
- `master_data/categories_list.html` - Category list
- `master_data/category_form.html` - Create/edit category
- Used in: `inventory/products.html` (category filter)
- Used in: `reports/report_sales_by_product.html` (category breakdown)

**Hierarchy:** Supports parent/child categories (e.g., Beverages > Hot Drinks)

---

### Units of Measurement
**Feature Purpose:** Define product measurement units  
**Related Templates:**
- `master_data/units_list.html` - Unit list (kg, liter, piece, etc.)
- `master_data/unit_form.html` - Create/edit unit
- Used in: `inventory/products.html` (unit selection)
- Used in: `inventory/add_stock_movement.html` (unit for movement)

---

### Locations/Outlets
**Feature Purpose:** Define store locations/warehouses  
**Related Templates:**
- `master_data/locations.html` - Location list
- `master_data/location_list.html` - Alternative view
- Used in: All stock-related features (location selection)
- Used in: `reports/report_sales_by_outlet.html` (sales per location)
- Modal reference: Location picker in forms

---

### Vendors/Suppliers
**Feature Purpose:** Maintain supplier list  
**Related Templates:**
- `master_data/vendors_list.html` - Vendor list
- `master_data/vendor_list.html` - Alternative view
- `master_data/vendor_form.html` - Create/edit vendor
- Used in: `inventory/stock_purchasing.html` (select vendor for PO)
- Used in: `inventory/supplier_price_list.html` (supplier prices)

---

## 👥 Customer Management

### Customers List
**Feature Purpose:** Maintain customer database  
**Related Templates:**
- `master_data/customers.html` - Customer dashboard
- `master_data/customers_list.html` - Customer list (paginated)
- `master_data/customer_detail.html` - Customer profile
- `master_data/customer_form.html` - Create/edit customer
- `master_data/customer.html` - Alternative customer view

**Customer Data:**
- Name, email, phone, address
- Customer type (retail/wholesale)
- Birth date (for promotions)
- Purchase history summary
- Loyalty points balance

---

### Customer Lookup in POS
**Feature Purpose:** Find customer during checkout  
**Related Templates:**
- `sales_insight/pos.html` - Search customer during POS
- Links to: `master_data/customers_list.html` (create new customer quick link)
- Result: Transaction linked to customer → Visible in `master_data/customer_detail.html`

**Data Used:**
- Customer name for receipt
- Discount eligibility
- Loyalty points

---

### Customer Loyalty
**Feature Purpose:** Track & manage loyalty program  
**Related Templates:**
- `marketing/loyalty_members.html` - Member list with points
- `master_data/customer_detail.html` - Shows points balance
- Used in: `sales_insight/pos.html` (points deduction during redemption)
- Report: `reports/loyalty_members.html` (if exists)

---

## 📢 Marketing & Loyalty

### Campaign Management
**Feature Purpose:** Plan & execute marketing campaigns  
**Related Templates:**
- `marketing/campaign.html` - Campaign list
- `marketing/campaign_list.html` - Alternative view
- `marketing/add_campaign.html` - Create campaign
- Connects to: `master_data/customers.html` (target audience)

**Campaign Fields:**
- Name, description
- Start/end date
- Budget, target audience
- Campaign type (promotion, seasonal, etc.)
- Performance tracking

---

### Discount Management
**Feature Purpose:** Create promotional discounts  
**Related Templates:**
- `marketing/discount.html` - Discount list
- Used in: `sales_insight/pos.html` (apply discount at checkout)
- Tracked in: `reports/report_sales_by_outlet.html` (discount impact)

**Discount Type:**
- Amount-based (e.g., $2 off)
- Percentage-based (e.g., 10% off)
- Eligibility rules (customer type, purchase amount, etc.)

---

### Loyalty Program
**Feature Purpose:** Reward repeat customers  
**Related Templates:**
- `marketing/loyalty_members.html` - Member list
- `master_data/customer_detail.html` - Member profile with points
- Used in: `sales_insight/pos.html` (accrue/redeem points)
- Links to: `master_data/customers.html` (member enrollment)

---

## 🏭 Production/Recipes

### Recipe Management
**Feature Purpose:** Define recipes for manufactured products  
**Related Templates:**
- `production/recipe_list.html` - Recipe catalog
- `production/recipe_form.html` - Create/edit recipe
- `production/recipe_detail.html` - View recipe details
- Used in: Costing & COGS calculation (`reports/report_profit_loss_detail.html`)

**Recipe Components:**
- Ingredients (products)
- Quantities per ingredient
- Yield amount
- Total cost (auto-calculated)

**Uses:**
- Determine product cost
- Generate material requirements
- Track ingredient usage

---

## 📊 Reports & Analytics

### Sales Reports
**Feature Purpose:** Analyze sales performance  
**Related Templates:**
- `reports/sales_report.html` - Main sales report (period, products, etc.)
- `reports/sales_history.html` - All transactions chronologically
- `reports/sales_history_product.html` - Sales by product
- `reports/report_sales_by_outlet.html` - Sales per location
- `reports/report_sales_by_payment.html` - Payment method breakdown
- `reports/report_sales_by_product.html` - Product performance ranking

**Data Source:** POS transactions via `sales_insight/pos.html`

**Typical Report User:** Sales manager, accountant

---

### Inventory Reports
**Feature Purpose:** Analyze stock & supply chain  
**Related Templates:**
- `reports/report_inventory_stock.html` - Current stock levels
- `reports/report_inventory_log.html` - Stock transaction history
- `reports/report_inventory_low.html` - Low stock alert
- `inventory/stock_overview.html` - Dashboard view

**Data Source:** Stock movements, opname submissions

---

### Financial Reports
**Feature Purpose:** Executive financial overview  
**Related Templates:**
- `sales_insight/financial_reports.html` - Revenue, expense, profit summary
- `reports/report_profit_loss_detail.html` - Detailed P&L by category/period
- Includes: Revenue, COGS, operating expenses, profit/loss

**Data Sources:**
- Sales from POS
- Cost from suppliers & recipes
- Expenses from settings

---

### Operational Reports
**Feature Purpose:** Track internal processes  
**Related Templates:**
- `reports/requisition_report.html` - Stock requisition status
- `reports/purchasing_report.html` - Purchase order tracking
- `reports/transfer_report.html` - Inter-location stock transfers
- `reports/activity_log.html` - User activity audit trail

---

### Dashboard & KPIs
**Feature Purpose:** Executive summary view  
**Related Templates:**
- `sales_insight/dashboard.html` - Main dashboard with KPIs
- Uses: `base/kpi_card.html`, `base/kpi_card_white.html` (KPI display)
- Links to: All detailed reports

**KPI Metrics:**
- Today's sales total
- Transaction count
- Top products
- Cash vs card ratio
- New customers acquired
- Low stock warnings

---

## 👤 User Management & Access

### User Accounts
**Feature Purpose:** Create & manage system users  
**Related Templates:**
- `settings/users.html` - User list
- `settings/profile.html` - Individual user profile (personal info, change password)
- Form uses: `base/partials/form_field.html`

**User Attributes:**
- Name, email, phone
- Role/permissions
- Store/location assignment
- Status (active/inactive)

**Access Control:** Role-based (admin, manager, staff, viewer)

---

### Permission & Roles
**Feature Purpose:** Control feature access by role  
**Related Templates:**
- `settings/users.html` - Role assignment during user creation
- Typically managed in admin panel (not in template screenshots)

**Typical Roles:**
- Admin: Full access
- Manager: Store/area level
- Staff: Limited to POS or assigned features
- Viewer: Reports only (read-only)

---

### Profile & Password
**Feature Purpose:** User profile management  
**Related Templates:**
- `settings/profile.html` - View/edit personal profile
- View/change avatar
- Change password (form)
- Account preferences (language, theme, etc.)

---

## ⚙️ System & Administration

### System Settings
**Feature Purpose:** Configure system parameters  
**Related Templates:**
- `settings/settings.html` - General settings hub
- `settings/system_status.html` - System health dashboard
- `settings/business_settings.html` - Business configuration
- `settings/business_form_general.html` - Business info form
- `settings/business_profile.html` - Business branding

**Configuration Items:**
- Currency, language, timezone
- Business logo & branding
- System hours/holidays
- Backup settings
- API integrations

---

### Business Profile
**Feature Purpose:** Maintain company information  
**Related Templates:**
- `settings/business_settings.html` - Settings hub
- `settings/business_form_general.html` - Edit business info (company name, tax ID, etc.)
- `settings/business_profile.html` - View/display company info
- `settings/business_feature_matrix.html` - Feature enablement/licensing

**Used For:**
- Invoice/receipt headers
- Business registration info
- Multi-branch management

---

### System Monitoring
**Feature Purpose:** Monitor system health & performance  
**Related Templates:**
- `settings/system_status.html` - Database, API, storage status
- Shows: Uptime, backup status, user count
- Alert: If issues detected

---

### Global Search
**Feature Purpose:** Find anything across the system  
**Related Templates:**
- `settings/search.html` - Global search interface
- Available from: navbar in `base/navbar.html`
- Searches: Products, customers, vendors, reports, etc.

---

## 🔐 Authentication & Access

### Login
**Feature Purpose:** User authentication  
**Related Templates:**
- `auth/login.html` - Login form
- Fields: Email/username, password
- Features: "Remember me", forgot password link
- On success: Redirects to `sales_insight/dashboard.html`

---

### Registration
**Feature Purpose:** Create new user account  
**Related Templates:**
- `auth/register.html` - Registration form
- Fields: Name, email, password, confirm password
- Terms acceptance checkbox
- On success: Redirects to login or dashboard

---

### Error Handling
**Feature Purpose:** Handle access denied & not found errors  
**Related Templates:**
- `etc/error_403.html` - Permission denied
- `etc/error_404.html` - Page not found
- `etc/error_500.html` - Server error
- In navbar: Links back to home, contact support

---

## 🧩 Information Pages

### About System
**Feature Purpose:** Display system information  
**Related Templates:**
- `settings/about.html` - System version, credits, license
- Links to: `settings/contact.html`

### Contact & Support  
**Feature Purpose:** Get help & submit tickets  
**Related Templates:**
- `settings/contact.html` - Contact info, support form
- Links to: `settings/about.html`, FAQs

---

## 🎯 User Journey Examples

### Manager's Daily Workflow
```
1. Login (auth/login.html)
2. Dashboard (sales_insight/dashboard.html) → View KPIs
3. Check low stock (inventory/stock_overview.html)
   → Low stock alert? → Go to (reports/report_inventory_low.html)
   → Create PO in (inventory/stock_purchasing.html)
4. Review sales (reports/sales_report.html)
5. Check pending approvals (inventory/stock_opname_approvals.html)
6. Profile update (settings/profile.html)
7. Logout
```

### Cashier's POS Workflow
```
1. Login (auth/login.html)
2. Go to POS (sales_insight/pos.html)
3. Select products → Search customer → Apply discount
4. Process payment → Complete transaction
5. View receipt → Return to POS
6. End of day → Manager reviews (reports/transaction_summary.html)
```

### Inventory Staff Workflow
```
1. Login → Stock opname needed?
2. (inventory/stock_opname_locations.html) → Select location
3. (inventory/stock_opname_form.html) → Enter counts
4. Submit → Manager reviews (inventory/stock_opname_approvals.html)
5. Approve → Generate stock movements (inventory/stock_movement.html)
6. Track in (reports/report_inventory_log.html)
```

### Accountant's Workflow
```
1. Login → Dashboard (sales_insight/dashboard.html)
2. Financial reports (sales_insight/financial_reports.html)
3. Detail P&L (reports/report_profit_loss_detail.html)
4. Sales breakdown (reports/report_sales_by_product.html)
5. Inventory valuation (reports/report_inventory_stock.html)
6. Export all reports → Accounting system
```

---

**Usage:** Reference this map when building connections between features or understanding the data flow through templates.


sekarang 05 Mei 2026
ada penambahan segala macam, terutama pakai 
3 generate seed

seed 1
"""
seed_expansion.py
=================
Script ekspansi database Kafe Nusantara — membuat dan mengisi tabel-tabel
yang melengkapi siklus bisnis, reporting, CRM, dan dashboard.

Semua operasi menggunakan raw SQL via Django connection.cursor()
untuk menghindari masalah managed=False dan FK attname.

MODUL (jalankan per section atau semua sekaligus):
  1. procurement    — purchase_orders, purchase_order_items,
                      goods_receipt_notes, goods_receipt_items
  2. rfm            — customer_rfm_scores (Recency/Frequency/Monetary)
  3. promotions     — promotions, promotion_usage
  4. sales_agg      — sales_daily_summary, sales_monthly_summary
  5. product_perf   — product_performance_summary
  6. inv_snapshot   — inventory_snapshot_monthly
  7. shifts         — shifts, shift_sales_summary
  8. kpi_cache      — dashboard_kpi_cache
  9. audit          — system_audit_trails (opsional, bisa besar)

Cara pakai:
  python seed_expansion.py --dry-run
  python seed_expansion.py --execute
  python seed_expansion.py --execute --section=procurement
  python seed_expansion.py --execute --section=rfm
  python seed_expansion.py --execute --section=sales_agg
  python seed_expansion.py --list-sections
"""

import os, sys, random, time, json
from decimal import Decimal
from datetime import date, datetime, timedelta

for _s in ("stdout", "stderr"):
    _o = getattr(sys, _s, None)
    if hasattr(_o, "reconfigure"):
        try: _o.reconfigure(encoding="utf-8", errors="replace")
        except: pass

# ── Args ──────────────────────────────────────────────────────────────────────
DRY_RUN = "--execute" not in sys.argv
SECTION = "all"
for i, a in enumerate(sys.argv[1:], 1):
    if a == "--section" and i < len(sys.argv): SECTION = sys.argv[i]
    elif a.startswith("--section="): SECTION = a.split("=",1)[1]

if "--list-sections" in sys.argv:
    print("Sections: procurement rfm promotions sales_agg product_perf inv_snapshot shifts kpi_cache audit all")
    sys.exit(0)

RNG = random.Random(42)

# ── Django ────────────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
import django; django.setup()
from django.db import connection
from django.utils import timezone

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def log(msg): print(f"  {msg}", flush=True)
def ok(msg):  print(f"  ✓ {msg}", flush=True)
def warn(msg):print(f"  ⚠ {msg}", flush=True)
def head(msg):
    print(f"\n{'▓'*60}")
    print(f"  {msg}")
    print(f"{'▓'*60}")

def q(sql, params=None):
    with connection.cursor() as cur:
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return cur.fetchall()

def q1(sql, params=None):
    rows = q(sql, params)
    return rows[0][0] if rows else None

def table_exists(name):
    return q1("SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s", [name]) > 0

def row_count(name):
    try: return q1(f"SELECT COUNT(*) FROM {name}")
    except: return -1

def execute_sql(sql, label=""):
    try:
        with connection.cursor() as cur:
            cur.execute(sql)
        if label: ok(label)
        return True
    except Exception as e:
        warn(f"{label}: {e}")
        return False

def bulk_insert(table, columns, rows, batch=2000, on_conflict="ON CONFLICT DO NOTHING"):
    if not rows: return 0
    cols = ", ".join(columns)
    ph   = ", ".join(["%s"] * len(columns))
    sql  = f"INSERT INTO {table} ({cols}) VALUES ({ph}) {on_conflict}"
    total = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i:i+batch]
        try:
            with connection.cursor() as cur:
                cur.executemany(sql, chunk)
                total += cur.rowcount if cur.rowcount >= 0 else len(chunk)
        except Exception as e:
            warn(f"Batch {i//batch+1} error [{table}]: {e}")
            for row in chunk:
                try:
                    with connection.cursor() as cur:
                        cur.execute(sql, row)
                        total += 1
                except: pass
    return total

def progress(done, total, t0, label=""):
    pct = done/max(1,total)*100
    ela = time.time()-t0
    eta = (ela/max(1,done))*(total-done) if done<total else 0
    bar = "█"*int(pct/5)+"░"*(20-int(pct/5))
    print(f"\r    [{bar}] {pct:5.1f}%  {done:,}/{total:,}  ETA {eta:.0f}s  {label}   ",
          end="", flush=True)

# ── Context: ambil data dari DB sekali ───────────────────────────────────────
CTX = {}
def load_context():
    log("Loading context dari DB...")
    CTX["admin_id"]     = (
        q1("SELECT id FROM auth_user WHERE is_superuser=true ORDER BY id LIMIT 1") or
        q1("SELECT id FROM auth_user ORDER BY id LIMIT 1")
    )
    CTX["user_ids"]     = [r[0] for r in q("SELECT id FROM auth_user WHERE is_active=true ORDER BY id LIMIT 200")]
    CTX["location_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_locations ORDER BY id")]
    CTX["vendor_ids"]   = [r[0] for r in q("SELECT id FROM lumra_config_vendors ORDER BY id")]
    CTX["customer_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_customers WHERE is_active=true ORDER BY id LIMIT 5000")]
    CTX["variant_ids"]  = [r[0] for r in q("SELECT id FROM lumra_config_productvariants ORDER BY id LIMIT 2000")]
    CTX["unit_ids"]     = [r[0] for r in q("SELECT id FROM lumra_config_units ORDER BY id")]
    CTX["category_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_categories WHERE is_active=true ORDER BY id")]

    # FIX: gunakan parameterized query agar '%' tidak diinterpretasikan sebagai placeholder
    CTX["account_cash"]  = q1(
        "SELECT id FROM accounting_accounts WHERE code=%s OR name ILIKE %s LIMIT 1",
        ["1-1001", "%kas tunai%"]
    )
    CTX["account_ap"]    = q1(
        "SELECT id FROM accounting_accounts WHERE code=%s OR name ILIKE %s LIMIT 1",
        ["2-1001", "%hutang dagang%"]
    )
    CTX["account_inv"]   = q1(
        "SELECT id FROM accounting_accounts WHERE code LIKE %s OR name ILIKE %s LIMIT 1",
        ["1-12%", "%persediaan%"]
    )
    CTX["account_sales"] = q1(
        "SELECT id FROM accounting_accounts WHERE code LIKE %s OR name ILIKE %s LIMIT 1",
        ["4-1%", "%penjualan%"]
    )

    CTX["ap_ids"]         = [r[0] for r in q("SELECT id FROM accounting_accounts_payable ORDER BY id")]
    CTX["order_min_date"] = q1("SELECT MIN(created_at)::date FROM lumra_config_orders")
    CTX["order_max_date"] = q1("SELECT MAX(created_at)::date FROM lumra_config_orders")

    ok(
        f"Context loaded: {len(CTX['location_ids'])} locs, {len(CTX['vendor_ids'])} vendors, "
        f"{len(CTX['user_ids'])} users, {len(CTX['customer_ids'])} customers"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 1 — PROCUREMENT (PO → GRN → Stock In)
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_PURCHASE_ORDERS = """
CREATE TABLE IF NOT EXISTS lumra_procurement_purchase_orders (
    id              BIGSERIAL PRIMARY KEY,
    po_number       VARCHAR(50) UNIQUE NOT NULL,
    vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
    location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'draft',
    order_date      DATE NOT NULL,
    expected_date   DATE,
    total_amount    NUMERIC(15,2) NOT NULL DEFAULT 0,
    notes           TEXT DEFAULT '',
    created_by_id   BIGINT REFERENCES auth_user(id),
    approved_by_id  BIGINT REFERENCES auth_user(id),
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_purchase_orders IS
    'Purchase Order ke vendor. Dokumen resmi pemesanan barang.';
"""

CREATE_PO_ITEMS = """
CREATE TABLE IF NOT EXISTS lumra_procurement_po_items (
    id              BIGSERIAL PRIMARY KEY,
    po_id           BIGINT NOT NULL REFERENCES lumra_procurement_purchase_orders(id),
    variant_id      BIGINT NOT NULL REFERENCES lumra_config_productvariants(id),
    quantity        NUMERIC(12,2) NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    subtotal        NUMERIC(15,2) NOT NULL,
    received_qty    NUMERIC(12,2) DEFAULT 0,
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_po_items IS
    'Detail item per Purchase Order.';
"""

CREATE_GRN = """
CREATE TABLE IF NOT EXISTS lumra_procurement_goods_receipts (
    id              BIGSERIAL PRIMARY KEY,
    grn_number      VARCHAR(50) UNIQUE NOT NULL,
    po_id           BIGINT REFERENCES lumra_procurement_purchase_orders(id),
    vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
    location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'draft',
    receipt_date    DATE NOT NULL,
    total_received  NUMERIC(15,2) DEFAULT 0,
    notes           TEXT DEFAULT '',
    received_by_id  BIGINT REFERENCES auth_user(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_goods_receipts IS
    'Good Receipt Note (GRN) — bukti terima barang dari vendor.';
"""

CREATE_GRN_ITEMS = """
CREATE TABLE IF NOT EXISTS lumra_procurement_grn_items (
    id              BIGSERIAL PRIMARY KEY,
    grn_id          BIGINT NOT NULL REFERENCES lumra_procurement_goods_receipts(id),
    variant_id      BIGINT NOT NULL REFERENCES lumra_config_productvariants(id),
    po_item_id      BIGINT REFERENCES lumra_procurement_po_items(id),
    quantity_ordered NUMERIC(12,2) DEFAULT 0,
    quantity_received NUMERIC(12,2) NOT NULL,
    quantity_rejected NUMERIC(12,2) DEFAULT 0,
    unit_price      NUMERIC(12,2) NOT NULL,
    subtotal        NUMERIC(15,2) NOT NULL,
    batch_number    VARCHAR(100) DEFAULT '',
    expiry_date     DATE,
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_procurement_grn_items IS
    'Detail barang yang diterima per GRN.';
"""

def fill_procurement(dry_run=False):
    head("MODUL 1 — PROCUREMENT (PO + GRN)")

    if not dry_run:
        for sql, label in [
            (CREATE_PURCHASE_ORDERS, "lumra_procurement_purchase_orders"),
            (CREATE_PO_ITEMS,        "lumra_procurement_po_items"),
            (CREATE_GRN,             "lumra_procurement_goods_receipts"),
            (CREATE_GRN_ITEMS,       "lumra_procurement_grn_items"),
        ]:
            execute_sql(sql, f"CREATE {label}")

    today        = date.today()
    vendor_ids   = CTX["vendor_ids"]
    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    variant_ids  = CTX["variant_ids"]
    admin_id     = CTX["admin_id"]

    po_rows      = []
    po_item_rows = []
    grn_rows     = []
    grn_item_rows= []

    # Ambil data dari AP yang sudah ada sebagai basis PO
    if table_exists("accounting_accounts_payable"):
        ap_data = q("""
            SELECT ap.id, ap.vendor_id, ap.invoice_date, ap.total_amount, ap.status
            FROM accounting_accounts_payable ap
            ORDER BY ap.id
        """)
    else:
        ap_data = []

    po_ctr  = 1
    grn_ctr = 1

    for ap_id, vendor_id, inv_date, total_amount, ap_status in ap_data:
        if not inv_date:
            inv_date = today - timedelta(days=RNG.randint(30, 90))
        order_date    = inv_date - timedelta(days=RNG.randint(3, 14))
        expected_date = inv_date
        loc_id        = RNG.choice(location_ids)
        creator       = RNG.choice(user_ids) if user_ids else admin_id
        approver      = admin_id
        po_status     = "completed" if ap_status == "paid" else "sent"
        po_number     = f"PO-{today.year}-{po_ctr:05d}"
        po_rows.append((
            po_number, vendor_id, loc_id, po_status,
            order_date, expected_date, total_amount or 0,
            f"PO untuk vendor {vendor_id}", creator, approver,
            inv_date, inv_date, inv_date
        ))
        po_ctr += 1

    # Tambah 400 PO extra
    for i in range(400):
        days_ago   = RNG.randint(7, 730)
        order_date = today - timedelta(days=days_ago)
        exp_date   = order_date + timedelta(days=RNG.randint(3, 14))
        vendor_id  = RNG.choice(vendor_ids)
        loc_id     = RNG.choice(location_ids)
        creator    = RNG.choice(user_ids) if user_ids else admin_id
        total      = Decimal(str(RNG.randint(500000, 50000000)))
        po_status  = RNG.choices(
            ["completed","completed","sent","partial","cancelled"],
            weights=[50, 20, 15, 10, 5]
        )[0]
        po_number   = f"PO-{today.year}-{po_ctr:05d}"
        approved_at = exp_date if po_status not in ["draft","cancelled"] else None
        po_rows.append((
            po_number, vendor_id, loc_id, po_status,
            order_date, exp_date, total,
            "PO pembelian operasional", creator,
            admin_id if po_status not in ["draft","cancelled"] else None,
            approved_at,
            order_date, order_date
        ))
        po_ctr += 1

    log(f"PO rows: {len(po_rows)}")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(po_rows)} PO")
        return

    n = bulk_insert(
        "lumra_procurement_purchase_orders",
        ["po_number","vendor_id","location_id","status","order_date","expected_date",
         "total_amount","notes","created_by_id","approved_by_id","approved_at",
         "created_at","updated_at"],
        po_rows
    )
    ok(f"PO inserted: {n:,}")

    saved_pos = q("SELECT id, location_id, vendor_id, total_amount, status, order_date FROM lumra_procurement_purchase_orders ORDER BY id")

    for po_id, loc_id, vendor_id, total_amt, po_status, order_date in saved_pos:
        n_items    = RNG.randint(1, 5)
        sampled    = RNG.sample(variant_ids, min(n_items, len(variant_ids)))
        item_total = Decimal("0")

        for var_id in sampled:
            qty   = Decimal(str(RNG.randint(12, 120)))
            price = Decimal(str(RNG.randint(3000, 80000)))
            sub   = qty * price
            item_total += sub
            po_item_rows.append((po_id, var_id, qty, price, sub, 0, "", order_date))

        if po_status in ("completed", "partial"):
            grn_number = f"GRN-{today.year}-{grn_ctr:05d}"
            if isinstance(order_date, str):
                receipt_dt = today - timedelta(days=RNG.randint(1, 30))
            else:
                receipt_dt = order_date + timedelta(days=RNG.randint(1, 7))
            rcvr = RNG.choice(user_ids) if user_ids else admin_id
            grn_rows.append((
                grn_number, po_id, vendor_id, loc_id, "completed",
                receipt_dt, item_total, "GRN dari PO", rcvr,
                receipt_dt, receipt_dt
            ))
            grn_ctr += 1

    n = bulk_insert(
        "lumra_procurement_po_items",
        ["po_id","variant_id","quantity","unit_price","subtotal","received_qty","notes","created_at"],
        po_item_rows
    )
    ok(f"PO items inserted: {n:,}")

    n = bulk_insert(
        "lumra_procurement_goods_receipts",
        ["grn_number","po_id","vendor_id","location_id","status","receipt_date",
         "total_received","notes","received_by_id","created_at","updated_at"],
        grn_rows
    )
    ok(f"GRN inserted: {n:,}")

    saved_grns   = q("SELECT id, po_id FROM lumra_procurement_goods_receipts ORDER BY id")
    po_items_map = {}
    for row in q("SELECT id, po_id, variant_id, quantity, unit_price FROM lumra_procurement_po_items"):
        pi_id, po_id, var_id, qty, price = row
        po_items_map.setdefault(po_id, []).append((pi_id, var_id, qty, price))

    for grn_id, po_id in saved_grns:
        for pi_id, var_id, qty, price in po_items_map.get(po_id, []):
            rcv = qty * Decimal(str(RNG.uniform(0.9, 1.0)))
            rej = qty - rcv
            sub = rcv * price
            exp = date.today() + timedelta(days=RNG.choice([90, 180, 270, 365]))
            grn_item_rows.append((
                grn_id, var_id, pi_id, qty, rcv.quantize(Decimal("0.01")),
                rej.quantize(Decimal("0.01")),
                price, sub.quantize(Decimal("0.01")),
                f"BTH-{RNG.randint(10000,99999)}", exp, "", date.today()
            ))

    n = bulk_insert(
        "lumra_procurement_grn_items",
        ["grn_id","variant_id","po_item_id","quantity_ordered","quantity_received",
         "quantity_rejected","unit_price","subtotal","batch_number","expiry_date",
         "notes","created_at"],
        grn_item_rows
    )
    ok(f"GRN items inserted: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 2 — CUSTOMER RFM SCORES
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_RFM = """
CREATE TABLE IF NOT EXISTS lumra_crm_rfm_scores (
    id                  BIGSERIAL PRIMARY KEY,
    customer_id         BIGINT NOT NULL UNIQUE REFERENCES lumra_config_customers(id),
    recency_days        INT NOT NULL DEFAULT 0,
    frequency           INT NOT NULL DEFAULT 0,
    monetary_total      NUMERIC(15,2) NOT NULL DEFAULT 0,
    avg_order_value     NUMERIC(12,2) NOT NULL DEFAULT 0,
    r_score             SMALLINT NOT NULL DEFAULT 1,
    f_score             SMALLINT NOT NULL DEFAULT 1,
    m_score             SMALLINT NOT NULL DEFAULT 1,
    rfm_score           SMALLINT NOT NULL DEFAULT 3,
    segment             VARCHAR(30) NOT NULL DEFAULT 'new',
    first_order_date    DATE,
    last_order_date     DATE,
    calculated_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_crm_rfm_scores IS
    'RFM (Recency/Frequency/Monetary) scoring per customer. '
    'Segment: champion, loyal, at_risk, lost, new, potential, promising.';
CREATE INDEX IF NOT EXISTS idx_rfm_segment ON lumra_crm_rfm_scores(segment);
CREATE INDEX IF NOT EXISTS idx_rfm_score   ON lumra_crm_rfm_scores(rfm_score DESC);
"""

def fill_rfm(dry_run=False):
    head("MODUL 2 — CUSTOMER RFM SCORES")

    if not dry_run:
        execute_sql(CREATE_RFM, "CREATE lumra_crm_rfm_scores")

    rfm_sql = """
    SELECT
        o.customer_id,
        EXTRACT(DAY FROM NOW() - MAX(o.created_at))::int   AS recency_days,
        COUNT(o.id)                                          AS frequency,
        COALESCE(SUM(o.paid_amount), 0)                     AS monetary,
        COALESCE(AVG(o.paid_amount), 0)                     AS avg_order,
        MIN(o.created_at)::date                              AS first_date,
        MAX(o.created_at)::date                              AS last_date
    FROM lumra_config_orders o
    WHERE o.customer_id IS NOT NULL
      AND o.status = 'completed'
    GROUP BY o.customer_id
    """

    log("Menghitung RFM dari orders...")
    t0 = time.time()
    rfm_data = q(rfm_sql)
    log(f"RFM dihitung untuk {len(rfm_data):,} customers ({time.time()-t0:.1f}s)")

    if not rfm_data:
        cust_ids = CTX["customer_ids"]
        log(f"Fallback: generate RFM dari {len(cust_ids)} customers tanpa order history")
        rfm_data = [
            (cid, RNG.randint(1, 365), RNG.randint(1, 50),
             RNG.randint(50000, 5000000), RNG.randint(50000, 500000),
             date.today() - timedelta(days=RNG.randint(30, 730)),
             date.today() - timedelta(days=RNG.randint(1, 30)))
            for cid in cust_ids
        ]

    recencies   = sorted([r[1] for r in rfm_data])
    frequencies = sorted([r[2] for r in rfm_data])
    monetaries  = sorted([r[3] for r in rfm_data])

    def pctile_score(val, sorted_list, reverse=False):
        idx   = sorted_list.index(val) / max(1, len(sorted_list)-1)
        score = int(idx * 4) + 1
        return (6 - score) if reverse else score

    segments = {
        (5,5): "champion",      (5,4): "champion",       (4,5): "loyal",
        (4,4): "loyal",         (3,5): "potential",      (3,4): "potential",
        (5,3): "at_risk",       (4,3): "at_risk",        (3,3): "promising",
        (2,5): "cannot_lose",   (2,4): "cannot_lose",    (1,5): "lost_big",
        (1,4): "lost_big",      (2,3): "at_risk",        (1,3): "lost",
        (5,2): "need_attention",(4,2): "need_attention", (3,2): "hibernating",
        (2,2): "hibernating",   (1,2): "lost",           (5,1): "new",
        (4,1): "new",           (3,1): "new",            (2,1): "lost",
        (1,1): "lost",
    }

    rows = []
    now  = datetime.now()
    for cid, rec, freq, mon, avg, first_dt, last_dt in rfm_data:
        r = pctile_score(rec, recencies, reverse=True)
        f = pctile_score(freq, frequencies)
        m = pctile_score(mon, monetaries)
        r, f, m  = max(1, min(5,r)), max(1, min(5,f)), max(1, min(5,m))
        rfm_total = r + f + m
        seg       = segments.get((r,f), segments.get((r,3), "promising"))
        rows.append((
            cid, int(rec), int(freq),
            Decimal(str(mon)).quantize(Decimal("0.01")),
            Decimal(str(avg)).quantize(Decimal("0.01")),
            r, f, m, rfm_total, seg,
            first_dt, last_dt,
            now, now
        ))

    log(f"RFM rows: {len(rows):,}")
    if dry_run:
        from collections import Counter
        segs = Counter(r[9] for r in rows)
        log("[DRY RUN] Segment distribution:")
        for seg, cnt in segs.most_common():
            print(f"      {seg:<20} {cnt:>6,}")
        return

    n = bulk_insert(
        "lumra_crm_rfm_scores",
        ["customer_id","recency_days","frequency","monetary_total","avg_order_value",
         "r_score","f_score","m_score","rfm_score","segment",
         "first_order_date","last_order_date","calculated_at","updated_at"],
        rows,
        on_conflict="ON CONFLICT (customer_id) DO UPDATE SET "
                    "recency_days=EXCLUDED.recency_days, frequency=EXCLUDED.frequency, "
                    "monetary_total=EXCLUDED.monetary_total, rfm_score=EXCLUDED.rfm_score, "
                    "segment=EXCLUDED.segment, updated_at=EXCLUDED.updated_at"
    )
    ok(f"RFM rows: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 3 — PROMOTIONS
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_PROMOTIONS = """
CREATE TABLE IF NOT EXISTS lumra_sales_promotions (
    id              BIGSERIAL PRIMARY KEY,
    code            VARCHAR(30) UNIQUE NOT NULL,
    name            VARCHAR(150) NOT NULL,
    description     TEXT DEFAULT '',
    promo_type      VARCHAR(30) NOT NULL,
    discount_type   VARCHAR(20) NOT NULL DEFAULT 'percentage',
    discount_value  NUMERIC(10,2) NOT NULL DEFAULT 0,
    min_purchase    NUMERIC(12,2) DEFAULT 0,
    max_discount    NUMERIC(12,2),
    applicable_session VARCHAR(20) DEFAULT 'all',
    applicable_hour_start SMALLINT DEFAULT 0,
    applicable_hour_end   SMALLINT DEFAULT 23,
    valid_from      DATE NOT NULL,
    valid_until     DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    usage_limit     INT,
    usage_count     INT DEFAULT 0,
    created_by_id   BIGINT REFERENCES auth_user(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE lumra_sales_promotions IS
    'Promo Kafe Nusantara: Morning Ration, Transit Special, Curator Share, dll.';
"""

CREATE_PROMO_USAGE = """
CREATE TABLE IF NOT EXISTS lumra_sales_promotion_usage (
    id              BIGSERIAL PRIMARY KEY,
    promotion_id    BIGINT NOT NULL REFERENCES lumra_sales_promotions(id),
    order_id        BIGINT NOT NULL REFERENCES lumra_config_orders(id),
    customer_id     BIGINT REFERENCES lumra_config_customers(id),
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    used_at         TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_promo_usage_order ON lumra_sales_promotion_usage(order_id);
CREATE INDEX IF NOT EXISTS idx_promo_usage_promo ON lumra_sales_promotion_usage(promotion_id);
"""

PROMOTIONS_DATA = [
    ("MR-BASIC",   "Morning Ration Basic",
     "Filter coffee house blend + croissant plain.",
     "bundle",     "percentage", 15, 0,       50000,  "first_light",      7,  12),
    ("MR-SELECT",  "Morning Ration Select",
     "Single origin pilihan + pastry seasonal.",
     "bundle",     "percentage", 10, 0,       75000,  "first_light",      7,  12),
    ("MR-CURATED", "Morning Ration Curated",
     "Speciality blend + granola bowl artisan. Bonus stamp.",
     "bundle",     "percentage",  5, 0,       100000, "first_light",      7,  12),
    ("CT-COLD",    "Cold Transit",
     "Es kopi susu any size + cold dessert pilihan.",
     "bundle",     "percentage", 20, 0,       60000,  "midday_transit",   12, 18),
    ("CT-RECHARGE","Recharge Combo",
     "Cold brew + savory sandwich.",
     "bundle",     "percentage", 15, 0,       50000,  "midday_transit",   12, 18),
    ("CT-AFTERNOON","Afternoon Pairing",
     "Racikan dingin Speciality + artisan dessert. Bonus stamp.",
     "bundle",     "percentage", 10, 0,       80000,  "midday_transit",   12, 18),
    ("TB-SHARED",  "The Curator's Share — Shared Brew",
     "2x racikan seasonal pilihan barista.",
     "bundle",     "percentage", 25, 0,       100000, "twilight_bivouac", 18, 23),
    ("TB-DUO",     "The Curator's Duo",
     "2x Speciality Blend bebas pilihan. Bonus 2 stamps.",
     "bundle",     "percentage", 20, 0,       150000, "twilight_bivouac", 18, 23),
    ("TB-GRAND",   "Grand Share",
     "2x signature mocktail + 1 savory sharing.",
     "bundle",     "percentage", 15, 0,       200000, "twilight_bivouac", 18, 23),
    ("PASSPORT-5", "Expedition Passport 5 Outpost",
     "Field Surveyor — Diskon permanent 5% untuk member.",
     "loyalty",    "percentage",  5, 0,       None,   "all",              0,  23),
    ("PASSPORT-10","Expedition Passport 10 Outpost",
     "Senior Cartographer — Early access menu seasonal.",
     "loyalty",    "percentage",  8, 0,       None,   "all",              0,  23),
    ("VOUCHER-50K","Voucher Rp 50.000",
     "Voucher nominal Rp 50.000 untuk pembelian minimum Rp 150.000.",
     "voucher",    "fixed",   50000, 150000,  None,   "all",              0,  23),
    ("VOUCHER-100K","Voucher Rp 100.000",
     "Voucher nominal Rp 100.000 untuk pembelian minimum Rp 300.000.",
     "voucher",    "fixed",  100000, 300000,  None,   "all",              0,  23),
    ("BIRTHDAY",   "Birthday Privilege",
     "Diskon 20% di hari ulang tahun customer.",
     "birthday",   "percentage", 20, 0,       100000, "all",              0,  23),
    ("WEEKEND-10", "Weekend Expedition",
     "10% untuk semua order di Sabtu-Minggu.",
     "seasonal",   "percentage", 10, 0,       75000,  "all",              0,  23),
    ("NEW-MEMBER", "Welcome Expeditor",
     "15% untuk order pertama member baru.",
     "onboarding", "percentage", 15, 0,       50000,  "all",              0,  23),
    ("GRAND-RESERVE","Grand Reserve Access",
     "Akses eksklusif Grand Reserve menu.",
     "loyalty",    "percentage",  0, 0,       None,   "all",              0,  23),
    ("MULTI-BUY-2","Multi Buy — Beli 2 Gratis 1 Pastry",
     "Beli 2 minuman utama, gratis 1 pastry pilihan.",
     "multi_buy",  "fixed",   25000, 80000,   25000,  "all",              0,  23),
    ("RAMADAN",    "Ramadan Special",
     "Diskon 10% setelah Maghrib selama bulan Ramadan.",
     "seasonal",   "percentage", 10, 0,       50000,  "twilight_bivouac", 18, 23),
    ("ANNIVERSARY","Anniversary Kafe Nusantara",
     "Hari jadi Kafe Nusantara — diskon spesial 25%.",
     "seasonal",   "percentage", 25, 50000,   200000, "all",              0,  23),
]

def fill_promotions(dry_run=False):
    head("MODUL 3 — PROMOTIONS & USAGE")

    if not dry_run:
        execute_sql(CREATE_PROMOTIONS, "CREATE lumra_sales_promotions")
        execute_sql(CREATE_PROMO_USAGE, "CREATE lumra_sales_promotion_usage")

    today    = date.today()
    admin_id = CTX["admin_id"]
    promo_rows = []

    for code, name, desc, ptype, disc_type, disc_val, min_pur, max_disc, session, hs, he in PROMOTIONS_DATA:
        promo_rows.append((
            code, name, desc, ptype, disc_type,
            Decimal(str(disc_val)),
            Decimal(str(min_pur)) if min_pur else Decimal("0"),
            Decimal(str(max_disc)) if max_disc else None,
            session, hs, he,
            date(2019, 1, 1), None, True, None, 0,
            admin_id, today, today
        ))

    log(f"Promotions: {len(promo_rows)}")
    if dry_run:
        log("[DRY RUN] Akan insert 20 promotions + ~20% order usage")
        return

    n = bulk_insert(
        "lumra_sales_promotions",
        ["code","name","description","promo_type","discount_type","discount_value",
         "min_purchase","max_discount","applicable_session",
         "applicable_hour_start","applicable_hour_end",
         "valid_from","valid_until","is_active","usage_limit","usage_count",
         "created_by_id","created_at","updated_at"],
        promo_rows,
        on_conflict="ON CONFLICT (code) DO NOTHING"
    )
    ok(f"Promotions inserted: {n}")

    promo_ids = [r[0] for r in q("SELECT id FROM lumra_sales_promotions ORDER BY id")]
    if not promo_ids:
        warn("Tidak ada promo tersimpan — skip usage")
        return

    orders = q("""
        SELECT id, customer_id, paid_amount, created_at
        FROM lumra_config_orders
        WHERE status='completed'
        ORDER BY id
        LIMIT 200000
    """)

    usage_rows = []
    t0 = time.time()
    for i, (oid, cid, paid, created_at) in enumerate(orders):
        if RNG.random() > 0.20:
            continue
        promo_id = RNG.choice(promo_ids)
        disc     = Decimal(str(paid or 0)) * Decimal(str(round(RNG.uniform(0.05, 0.25), 2)))
        usage_rows.append((promo_id, oid, cid, disc.quantize(Decimal("0.01")), created_at))
        if i % 10000 == 0:
            progress(i, len(orders), t0, "promo usage")

    print()
    n = bulk_insert(
        "lumra_sales_promotion_usage",
        ["promotion_id","order_id","customer_id","discount_amount","used_at"],
        usage_rows
    )
    ok(f"Promotion usage: {n:,}")

    execute_sql("""
        UPDATE lumra_sales_promotions p
        SET usage_count = (
            SELECT COUNT(*) FROM lumra_sales_promotion_usage u WHERE u.promotion_id = p.id
        )
    """, "Update usage_count")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 4 — SALES AGGREGATES (daily + monthly)
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_SALES_DAILY = """
CREATE TABLE IF NOT EXISTS lumra_report_sales_daily (
    id              BIGSERIAL PRIMARY KEY,
    report_date     DATE NOT NULL,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    total_orders    INT NOT NULL DEFAULT 0,
    total_revenue   NUMERIC(15,2) NOT NULL DEFAULT 0,
    total_items_sold INT NOT NULL DEFAULT 0,
    avg_order_value NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_returns   INT NOT NULL DEFAULT 0,
    return_value    NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_revenue     NUMERIC(15,2) NOT NULL DEFAULT 0,
    cash_sales      NUMERIC(15,2) DEFAULT 0,
    qris_sales      NUMERIC(15,2) DEFAULT 0,
    transfer_sales  NUMERIC(15,2) DEFAULT 0,
    card_sales      NUMERIC(15,2) DEFAULT 0,
    new_customers   INT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(report_date, location_id)
);
CREATE INDEX IF NOT EXISTS idx_sales_daily_date ON lumra_report_sales_daily(report_date DESC);
CREATE INDEX IF NOT EXISTS idx_sales_daily_loc  ON lumra_report_sales_daily(location_id);
COMMENT ON TABLE lumra_report_sales_daily IS
    'Agregasi penjualan harian per lokasi. Di-refresh tiap malam via cron.';
"""

CREATE_SALES_MONTHLY = """
CREATE TABLE IF NOT EXISTS lumra_report_sales_monthly (
    id              BIGSERIAL PRIMARY KEY,
    year            SMALLINT NOT NULL,
    month           SMALLINT NOT NULL,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    total_orders    INT NOT NULL DEFAULT 0,
    total_revenue   NUMERIC(15,2) NOT NULL DEFAULT 0,
    total_items_sold INT NOT NULL DEFAULT 0,
    avg_order_value NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_returns   INT NOT NULL DEFAULT 0,
    return_value    NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_revenue     NUMERIC(15,2) NOT NULL DEFAULT 0,
    target_amount   NUMERIC(15,2) DEFAULT 0,
    achievement_pct NUMERIC(6,2)  DEFAULT 0,
    mom_growth_pct  NUMERIC(6,2)  DEFAULT 0,
    yoy_growth_pct  NUMERIC(6,2)  DEFAULT 0,
    new_customers   INT DEFAULT 0,
    active_customers INT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(year, month, location_id)
);
CREATE INDEX IF NOT EXISTS idx_sales_monthly_ym ON lumra_report_sales_monthly(year DESC, month DESC);
COMMENT ON TABLE lumra_report_sales_monthly IS
    'Agregasi penjualan bulanan per lokasi. Include vs target & growth metrics.';
"""

def fill_sales_agg(dry_run=False):
    head("MODUL 4 — SALES AGGREGATES (daily + monthly)")

    if not dry_run:
        execute_sql(CREATE_SALES_DAILY, "CREATE lumra_report_sales_daily")
        execute_sql(CREATE_SALES_MONTHLY, "CREATE lumra_report_sales_monthly")

    log("Menghitung sales daily dari orders...")
    t0 = time.time()

    daily_raw = q("""
        SELECT
            DATE(o.created_at)             AS report_date,
            COUNT(o.id)                    AS total_orders,
            COALESCE(SUM(o.paid_amount),0) AS total_revenue,
            COALESCE(AVG(o.paid_amount),0) AS avg_order,
            SUM(CASE WHEN o.payment_method='cash'     THEN o.paid_amount ELSE 0 END) AS cash,
            SUM(CASE WHEN o.payment_method='qris'     THEN o.paid_amount ELSE 0 END) AS qris,
            SUM(CASE WHEN o.payment_method='transfer' THEN o.paid_amount ELSE 0 END) AS trf,
            SUM(CASE WHEN o.payment_method='card'     THEN o.paid_amount ELSE 0 END) AS card
        FROM lumra_config_orders o
        WHERE o.status = 'completed'
        GROUP BY DATE(o.created_at)
        ORDER BY report_date
    """)

    ret_raw = q("""
        SELECT DATE(r.created_at) AS rdate, COUNT(*) AS cnt, COALESCE(SUM(r.total_amount),0) AS val
        FROM lumra_config_returns r
        GROUP BY DATE(r.created_at)
    """)
    ret_map = {r[0]: (r[1], r[2]) for r in ret_raw}

    items_raw = q("""
        SELECT DATE(o.created_at), SUM(oi.quantity)
        FROM lumra_config_orders o
        JOIN lumra_config_orderitems oi ON oi.order_id = o.id
        WHERE o.status='completed'
        GROUP BY DATE(o.created_at)
    """)
    items_map = {r[0]: r[1] for r in items_raw}

    daily_rows = []
    now        = datetime.now()

    for rdate, n_ord, rev, avg, cash, qris, trf, card in daily_raw:
        ret_cnt, ret_val = ret_map.get(rdate, (0, 0))
        items_sold       = items_map.get(rdate, 0) or 0
        net_rev          = Decimal(str(rev)) - Decimal(str(ret_val))
        daily_rows.append((
            rdate, None, int(n_ord),
            Decimal(str(rev)).quantize(Decimal("0.01")),
            int(items_sold),
            Decimal(str(avg)).quantize(Decimal("0.01")),
            int(ret_cnt),
            Decimal(str(ret_val)).quantize(Decimal("0.01")),
            net_rev.quantize(Decimal("0.01")),
            Decimal(str(cash)).quantize(Decimal("0.01")),
            Decimal(str(qris)).quantize(Decimal("0.01")),
            Decimal(str(trf)).quantize(Decimal("0.01")),
            Decimal(str(card)).quantize(Decimal("0.01")),
            0, now
        ))

    log(f"Daily rows: {len(daily_rows):,} ({time.time()-t0:.1f}s)")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(daily_rows)} daily rows")
    else:
        n = bulk_insert(
            "lumra_report_sales_daily",
            ["report_date","location_id","total_orders","total_revenue","total_items_sold",
             "avg_order_value","total_returns","return_value","net_revenue",
             "cash_sales","qris_sales","transfer_sales","card_sales","new_customers","created_at"],
            daily_rows,
            on_conflict="ON CONFLICT (report_date, location_id) DO UPDATE SET "
                        "total_orders=EXCLUDED.total_orders, total_revenue=EXCLUDED.total_revenue, "
                        "net_revenue=EXCLUDED.net_revenue"
        )
        ok(f"Sales daily: {n:,}")

    log("Menghitung sales monthly...")
    monthly_raw = q("""
        SELECT
            EXTRACT(YEAR FROM o.created_at)::int  AS yr,
            EXTRACT(MONTH FROM o.created_at)::int AS mo,
            COUNT(o.id)                           AS total_orders,
            COALESCE(SUM(o.paid_amount),0)        AS total_revenue,
            COALESCE(AVG(o.paid_amount),0)        AS avg_order,
            COUNT(DISTINCT o.customer_id)         AS active_customers
        FROM lumra_config_orders o
        WHERE o.status = 'completed'
        GROUP BY yr, mo
        ORDER BY yr, mo
    """)

    ret_monthly = q("""
        SELECT EXTRACT(YEAR FROM created_at)::int, EXTRACT(MONTH FROM created_at)::int,
               COUNT(*), COALESCE(SUM(total_amount),0)
        FROM lumra_config_returns GROUP BY 1,2
    """)
    ret_m_map = {(r[0],r[1]):(r[2],r[3]) for r in ret_monthly}

    targets    = q("SELECT year, month, target_amount FROM lumra_config_sales_targets")
    target_map = {(r[0],r[1]): r[2] for r in targets}

    monthly_rows = []
    prev_revenue = {}

    for yr, mo, n_ord, rev, avg, active_custs in monthly_raw:
        ret_cnt, ret_val = ret_m_map.get((yr, mo), (0, 0))
        net_rev = Decimal(str(rev)) - Decimal(str(ret_val))
        target  = target_map.get((yr, mo), None) or Decimal("0")
        achieve = (Decimal(str(rev)) / Decimal(str(target)) * 100).quantize(Decimal("0.01")) \
                  if target and Decimal(str(target)) > 0 else Decimal("0")

        prev_mo  = (yr, mo-1) if mo > 1 else (yr-1, 12)
        prev_rev = prev_revenue.get(prev_mo, Decimal("0"))
        mom = ((Decimal(str(rev)) - prev_rev) / prev_rev * 100).quantize(Decimal("0.01")) \
              if prev_rev > 0 else Decimal("0")

        yoy_rev = prev_revenue.get((yr-1, mo), Decimal("0"))
        yoy = ((Decimal(str(rev)) - yoy_rev) / yoy_rev * 100).quantize(Decimal("0.01")) \
              if yoy_rev > 0 else Decimal("0")

        prev_revenue[(yr, mo)] = Decimal(str(rev))

        monthly_rows.append((
            yr, mo, None,
            int(n_ord),
            Decimal(str(rev)).quantize(Decimal("0.01")),
            0,
            Decimal(str(avg)).quantize(Decimal("0.01")),
            int(ret_cnt),
            Decimal(str(ret_val)).quantize(Decimal("0.01")),
            net_rev.quantize(Decimal("0.01")),
            Decimal(str(target)).quantize(Decimal("0.01")),
            achieve, mom, yoy,
            0, int(active_custs),
            datetime.now(), datetime.now()
        ))

    log(f"Monthly rows: {len(monthly_rows):,}")
    if not dry_run:
        n = bulk_insert(
            "lumra_report_sales_monthly",
            ["year","month","location_id","total_orders","total_revenue","total_items_sold",
             "avg_order_value","total_returns","return_value","net_revenue",
             "target_amount","achievement_pct","mom_growth_pct","yoy_growth_pct",
             "new_customers","active_customers","created_at","updated_at"],
            monthly_rows,
            on_conflict="ON CONFLICT (year, month, location_id) DO UPDATE SET "
                        "total_revenue=EXCLUDED.total_revenue, net_revenue=EXCLUDED.net_revenue, "
                        "achievement_pct=EXCLUDED.achievement_pct, updated_at=EXCLUDED.updated_at"
        )
        ok(f"Sales monthly: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 5 — PRODUCT PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_PRODUCT_PERF = """
CREATE TABLE IF NOT EXISTS lumra_report_product_performance (
    id                  BIGSERIAL PRIMARY KEY,
    variant_id          BIGINT NOT NULL UNIQUE REFERENCES lumra_config_productvariants(id),
    total_sold_qty      NUMERIC(15,2) DEFAULT 0,
    total_sold_revenue  NUMERIC(15,2) DEFAULT 0,
    total_sold_cogs     NUMERIC(15,2) DEFAULT 0,
    gross_margin        NUMERIC(15,2) DEFAULT 0,
    margin_pct          NUMERIC(6,2) DEFAULT 0,
    avg_selling_price   NUMERIC(12,2) DEFAULT 0,
    total_orders        INT DEFAULT 0,
    total_returns       INT DEFAULT 0,
    return_rate_pct     NUMERIC(6,2) DEFAULT 0,
    current_stock       NUMERIC(15,2) DEFAULT 0,
    stock_turnover_rate NUMERIC(8,2) DEFAULT 0,
    velocity_label      VARCHAR(20) DEFAULT 'normal',
    last_sold_date      DATE,
    calculated_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_prod_perf_velocity ON lumra_report_product_performance(velocity_label);
CREATE INDEX IF NOT EXISTS idx_prod_perf_margin   ON lumra_report_product_performance(margin_pct DESC);
COMMENT ON TABLE lumra_report_product_performance IS
    'Performa per produk: revenue, margin, turnover, velocity (fast/slow moving).';
"""

def fill_product_perf(dry_run=False):
    head("MODUL 5 — PRODUCT PERFORMANCE")

    if not dry_run:
        execute_sql(CREATE_PRODUCT_PERF, "CREATE lumra_report_product_performance")

    log("Menghitung product performance dari orderitems...")
    t0 = time.time()

    perf_raw = q("""
        SELECT
            oi.variant_id,
            SUM(oi.quantity)                              AS qty_sold,
            SUM(oi.price * oi.quantity)                   AS revenue,
            SUM(COALESCE(oi.cost_price,0) * oi.quantity) AS cogs,
            AVG(oi.price)                                 AS avg_price,
            COUNT(DISTINCT oi.order_id)                   AS n_orders,
            MAX(o.created_at)::date                       AS last_sold
        FROM lumra_config_orderitems oi
        JOIN lumra_config_orders o ON o.id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY oi.variant_id
        LIMIT 50000
    """)

    stock_raw = q("""
        SELECT variant_id, SUM(quantity) AS total_stock
        FROM lumra_config_stock
        GROUP BY variant_id
    """)
    stock_map = {r[0]: Decimal(str(r[1])) for r in stock_raw}

    ret_raw = q("""
        SELECT ri.product_id, COUNT(*)
        FROM lumra_config_returnitems ri
        GROUP BY ri.product_id
    """)
    ret_map = {r[0]: r[1] for r in ret_raw}

    rows = []
    now  = datetime.now()

    all_revenues = sorted([float(r[2] or 0) for r in perf_raw], reverse=True)
    p80 = all_revenues[int(len(all_revenues)*0.2)] if all_revenues else 0
    p20 = all_revenues[int(len(all_revenues)*0.8)] if all_revenues else 0

    for var_id, qty, rev, cogs, avg_price, n_ord, last_sold in perf_raw:
        rev    = Decimal(str(rev or 0))
        cogs   = Decimal(str(cogs or 0))
        qty    = Decimal(str(qty or 0))
        margin = rev - cogs
        margin_pct = (margin/rev*100).quantize(Decimal("0.01")) if rev > 0 else Decimal("0")

        curr_stock = stock_map.get(var_id, Decimal("0"))
        turnover   = (qty / curr_stock).quantize(Decimal("0.01")) if curr_stock > 0 else Decimal("0")

        ret_cnt  = ret_map.get(var_id, 0)
        ret_rate = (Decimal(str(ret_cnt)) / Decimal(str(n_ord)) * 100).quantize(Decimal("0.01")) \
                   if n_ord > 0 else Decimal("0")

        velocity = ("fast_moving" if float(rev) >= p80
                    else "slow_moving" if float(rev) <= p20
                    else "normal")

        rows.append((
            var_id, qty.quantize(Decimal("0.01")),
            rev.quantize(Decimal("0.01")), cogs.quantize(Decimal("0.01")),
            margin.quantize(Decimal("0.01")), margin_pct,
            Decimal(str(avg_price or 0)).quantize(Decimal("0.01")),
            int(n_ord), int(ret_cnt), ret_rate,
            curr_stock.quantize(Decimal("0.01")), turnover,
            velocity, last_sold, now
        ))

    log(f"Product perf rows: {len(rows):,} ({time.time()-t0:.1f}s)")
    if dry_run:
        fast = sum(1 for r in rows if r[12]=="fast_moving")
        slow = sum(1 for r in rows if r[12]=="slow_moving")
        log(f"[DRY RUN] fast={fast:,} normal={len(rows)-fast-slow:,} slow={slow:,}")
        return

    n = bulk_insert(
        "lumra_report_product_performance",
        ["variant_id","total_sold_qty","total_sold_revenue","total_sold_cogs",
         "gross_margin","margin_pct","avg_selling_price","total_orders","total_returns",
         "return_rate_pct","current_stock","stock_turnover_rate","velocity_label",
         "last_sold_date","calculated_at"],
        rows,
        on_conflict="ON CONFLICT (variant_id) DO UPDATE SET "
                    "total_sold_qty=EXCLUDED.total_sold_qty, "
                    "total_sold_revenue=EXCLUDED.total_sold_revenue, "
                    "margin_pct=EXCLUDED.margin_pct, "
                    "velocity_label=EXCLUDED.velocity_label, "
                    "calculated_at=EXCLUDED.calculated_at"
    )
    ok(f"Product performance: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 6 — INVENTORY SNAPSHOT MONTHLY
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_INV_SNAPSHOT = """
CREATE TABLE IF NOT EXISTS lumra_report_inventory_snapshot (
    id              BIGSERIAL PRIMARY KEY,
    snapshot_year   SMALLINT NOT NULL,
    snapshot_month  SMALLINT NOT NULL,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
    qty_opening     NUMERIC(15,2) DEFAULT 0,
    qty_in          NUMERIC(15,2) DEFAULT 0,
    qty_out         NUMERIC(15,2) DEFAULT 0,
    qty_closing     NUMERIC(15,2) DEFAULT 0,
    qty_on_hand     NUMERIC(15,2) DEFAULT 0,
    value_on_hand   NUMERIC(15,2) DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(snapshot_year, snapshot_month, location_id, variant_id)
);
CREATE INDEX IF NOT EXISTS idx_inv_snap_ym ON lumra_report_inventory_snapshot(snapshot_year DESC, snapshot_month DESC);
COMMENT ON TABLE lumra_report_inventory_snapshot IS
    'Snapshot stok akhir bulan — untuk audit akuntansi tanpa re-query seluruh mutasi.';
"""

def fill_inv_snapshot(dry_run=False):
    head("MODUL 6 — INVENTORY SNAPSHOT MONTHLY")

    if not dry_run:
        execute_sql(CREATE_INV_SNAPSHOT, "CREATE lumra_report_inventory_snapshot")

    log("Generating snapshot dari stockmovement per bulan...")
    t0 = time.time()

    # FIX: ILIKE '%in%' dan '%out%' aman di sini karena tidak ada params=[] — driver tidak parse %
    snap_raw = q("""
        SELECT
            EXTRACT(YEAR  FROM created_at)::int AS yr,
            EXTRACT(MONTH FROM created_at)::int AS mo,
            location_id,
            product_id AS variant_id,
            SUM(CASE WHEN movement_type ILIKE '%in%'  THEN quantity ELSE 0 END) AS qty_in,
            SUM(CASE WHEN movement_type ILIKE '%out%' THEN quantity ELSE 0 END) AS qty_out
        FROM lumra_config_stockmovement
        GROUP BY yr, mo, location_id, product_id
        ORDER BY yr, mo
        LIMIT 500000
    """)

    curr_stock = q("""
        SELECT location_id, variant_id, quantity
        FROM lumra_config_stock
        LIMIT 500000
    """)
    stock_map = {(r[0],r[1]): Decimal(str(r[2])) for r in curr_stock}

    rows = []
    now  = datetime.now()

    for yr, mo, loc_id, var_id, qty_in, qty_out in snap_raw:
        qty_in  = Decimal(str(qty_in  or 0))
        qty_out = Decimal(str(qty_out or 0))
        qty_net = qty_in - qty_out
        on_hand = stock_map.get((loc_id, var_id), Decimal("0"))
        opening = on_hand - qty_net
        rows.append((
            int(yr), int(mo), loc_id, var_id,
            opening.quantize(Decimal("0.01")),
            qty_in.quantize(Decimal("0.01")),
            qty_out.quantize(Decimal("0.01")),
            (opening + qty_net).quantize(Decimal("0.01")),
            on_hand.quantize(Decimal("0.01")),
            Decimal("0"),
            now
        ))

    log(f"Snapshot rows: {len(rows):,} ({time.time()-t0:.1f}s)")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(rows):,} snapshot rows")
        return

    n = bulk_insert(
        "lumra_report_inventory_snapshot",
        ["snapshot_year","snapshot_month","location_id","variant_id",
         "qty_opening","qty_in","qty_out","qty_closing","qty_on_hand",
         "value_on_hand","created_at"],
        rows, batch=3000,
        on_conflict="ON CONFLICT (snapshot_year,snapshot_month,location_id,variant_id) DO NOTHING"
    )
    ok(f"Inventory snapshot: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 7 — SHIFTS + SHIFT SALES SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_SHIFTS = """
CREATE TABLE IF NOT EXISTS lumra_ops_shifts (
    id              BIGSERIAL PRIMARY KEY,
    shift_code      VARCHAR(50) UNIQUE NOT NULL,
    location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
    shift_date      DATE NOT NULL,
    shift_type      VARCHAR(20) NOT NULL,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ,
    opened_by_id    BIGINT REFERENCES auth_user(id),
    closed_by_id    BIGINT REFERENCES auth_user(id),
    opening_cash    NUMERIC(12,2) DEFAULT 0,
    closing_cash    NUMERIC(12,2) DEFAULT 0,
    expected_cash   NUMERIC(12,2) DEFAULT 0,
    cash_variance   NUMERIC(12,2) DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'closed',
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_shifts_date ON lumra_ops_shifts(shift_date DESC);
CREATE INDEX IF NOT EXISTS idx_shifts_loc  ON lumra_ops_shifts(location_id);
COMMENT ON TABLE lumra_ops_shifts IS
    'Data shift kerja per outpost. 3 shift: First Light (7-12), Midday (12-18), Twilight (18-close).';
"""

CREATE_SHIFT_SUMMARY = """
CREATE TABLE IF NOT EXISTS lumra_ops_shift_sales_summary (
    id              BIGSERIAL PRIMARY KEY,
    shift_id        BIGINT NOT NULL REFERENCES lumra_ops_shifts(id),
    total_orders    INT DEFAULT 0,
    total_revenue   NUMERIC(15,2) DEFAULT 0,
    cash_received   NUMERIC(12,2) DEFAULT 0,
    qris_received   NUMERIC(12,2) DEFAULT 0,
    other_received  NUMERIC(12,2) DEFAULT 0,
    total_items     INT DEFAULT 0,
    avg_order_value NUMERIC(12,2) DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shift_id)
);
COMMENT ON TABLE lumra_ops_shift_sales_summary IS
    'Ringkasan penjualan per shift. Link ke shift_id dari lumra_ops_shifts.';
"""

def fill_shifts(dry_run=False):
    head("MODUL 7 — SHIFTS & SHIFT SALES SUMMARY")

    if not dry_run:
        execute_sql(CREATE_SHIFTS, "CREATE lumra_ops_shifts")
        execute_sql(CREATE_SHIFT_SUMMARY, "CREATE lumra_ops_shift_sales_summary")

    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    min_date = CTX["order_min_date"] or date(2023, 1, 1)
    max_date = CTX["order_max_date"] or date.today()

    SHIFT_TYPES = [
        ("first_light",      7,  12, "First Light"),
        ("midday_transit",   12, 18, "Midday Transit"),
        ("twilight_bivouac", 18, 23, "Twilight Bivouac"),
    ]

    shift_rows = []
    current    = min_date
    shift_ctr  = 1

    log(f"Generating shifts: {min_date} → {max_date}, {len(location_ids)} lokasi × 3 shift")
    t0         = time.time()
    total_days = (max_date - min_date).days + 1
    day_idx    = 0

    while current <= max_date:
        for loc_id in location_ids:
            opener       = RNG.choice(user_ids) if user_ids else admin_id
            closer       = RNG.choice(user_ids) if user_ids else admin_id
            opening_cash = Decimal(str(RNG.randint(500000, 2000000)))

            for stype, sh, eh, slabel in SHIFT_TYPES:
                code     = f"SHF-{current.strftime('%Y%m%d')}-{loc_id}-{stype[:2].upper()}"
                start_dt = datetime(current.year, current.month, current.day, sh, 0)
                end_dt   = datetime(current.year, current.month, current.day, eh, 0)
                exp_cash = opening_cash + Decimal(str(RNG.randint(100000, 5000000)))
                actual_cash = exp_cash * Decimal(str(RNG.uniform(0.95, 1.05)))
                variance    = actual_cash - exp_cash

                shift_rows.append((
                    code, loc_id, current, stype,
                    start_dt, end_dt,
                    opener, closer,
                    opening_cash.quantize(Decimal("0.01")),
                    actual_cash.quantize(Decimal("0.01")),
                    exp_cash.quantize(Decimal("0.01")),
                    variance.quantize(Decimal("0.01")),
                    "closed", "", current
                ))
                shift_ctr += 1

        if day_idx % 100 == 0:
            progress(day_idx, total_days, t0, "generating shifts")
        current += timedelta(days=1)
        day_idx += 1

    print()
    log(f"Shift rows: {len(shift_rows):,}")

    if dry_run:
        log(f"[DRY RUN] Akan insert {len(shift_rows):,} shifts")
        return

    n = bulk_insert(
        "lumra_ops_shifts",
        ["shift_code","location_id","shift_date","shift_type","start_time","end_time",
         "opened_by_id","closed_by_id","opening_cash","closing_cash","expected_cash",
         "cash_variance","status","notes","created_at"],
        shift_rows, batch=3000,
        on_conflict="ON CONFLICT (shift_code) DO NOTHING"
    )
    ok(f"Shifts inserted: {n:,}")

    log("Generating shift_sales_summary dari orders.shift_id...")
    saved_shifts = q("SELECT id, shift_code FROM lumra_ops_shifts ORDER BY id LIMIT 100000")
    shift_id_map = {r[1]: r[0] for r in saved_shifts}

    order_agg = q("""
        SELECT
            o.shift_id,
            COUNT(o.id)                    AS n_orders,
            COALESCE(SUM(o.paid_amount),0) AS revenue,
            SUM(CASE WHEN o.payment_method='cash' THEN o.paid_amount ELSE 0 END),
            SUM(CASE WHEN o.payment_method='qris' THEN o.paid_amount ELSE 0 END),
            SUM(CASE WHEN o.payment_method NOT IN ('cash','qris') THEN o.paid_amount ELSE 0 END),
            COUNT(DISTINCT oi.id) AS total_items
        FROM lumra_config_orders o
        LEFT JOIN lumra_config_orderitems oi ON oi.order_id = o.id
        WHERE o.status = 'completed' AND o.shift_id IS NOT NULL
        GROUP BY o.shift_id
    """)

    summary_rows = []
    now = datetime.now()
    for shift_str, n_ord, rev, cash, qris, other, items in order_agg:
        shift_db_id = shift_id_map.get(shift_str)
        if not shift_db_id:
            continue
        avg = Decimal(str(rev)) / int(n_ord) if n_ord else Decimal("0")
        summary_rows.append((
            shift_db_id, int(n_ord),
            Decimal(str(rev)).quantize(Decimal("0.01")),
            Decimal(str(cash)).quantize(Decimal("0.01")),
            Decimal(str(qris)).quantize(Decimal("0.01")),
            Decimal(str(other)).quantize(Decimal("0.01")),
            int(items or 0),
            avg.quantize(Decimal("0.01")), now
        ))

    n = bulk_insert(
        "lumra_ops_shift_sales_summary",
        ["shift_id","total_orders","total_revenue","cash_received","qris_received",
         "other_received","total_items","avg_order_value","created_at"],
        summary_rows,
        on_conflict="ON CONFLICT (shift_id) DO NOTHING"
    )
    ok(f"Shift summary: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 8 — DASHBOARD KPI CACHE
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_KPI_CACHE = """
CREATE TABLE IF NOT EXISTS lumra_dashboard_kpi_cache (
    id              BIGSERIAL PRIMARY KEY,
    metric_key      VARCHAR(80) UNIQUE NOT NULL,
    metric_group    VARCHAR(40) NOT NULL,
    metric_label    VARCHAR(120) NOT NULL,
    value_numeric   NUMERIC(20,4),
    value_text      TEXT,
    value_json      JSONB,
    unit            VARCHAR(20) DEFAULT '',
    period_type     VARCHAR(20) DEFAULT 'today',
    period_start    DATE,
    period_end      DATE,
    location_id     BIGINT REFERENCES lumra_config_locations(id),
    trend           VARCHAR(10) DEFAULT 'neutral',
    change_pct      NUMERIC(8,2) DEFAULT 0,
    refreshed_at    TIMESTAMPTZ DEFAULT NOW(),
    next_refresh_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_kpi_group ON lumra_dashboard_kpi_cache(metric_group);
COMMENT ON TABLE lumra_dashboard_kpi_cache IS
    'Cache KPI untuk dashboard. Di-refresh tiap jam via cron.';
"""

def fill_kpi_cache(dry_run=False):
    head("MODUL 8 — DASHBOARD KPI CACHE")

    if not dry_run:
        execute_sql(CREATE_KPI_CACHE, "CREATE lumra_dashboard_kpi_cache")

    now   = datetime.now()
    today = date.today()

    def safe_q1(sql, default=0):
        try: return q1(sql) or default
        except: return default

    # FIX: semua f-string di bawah tidak pakai LIKE/ILIKE jadi aman
    rev_today = safe_q1(f"""
        SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders
        WHERE DATE(created_at)='{today}' AND status='completed'
    """)
    rev_ytd = safe_q1(f"""
        SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders
        WHERE EXTRACT(YEAR FROM created_at)={today.year} AND status='completed'
    """)
    rev_mtd = safe_q1(f"""
        SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders
        WHERE EXTRACT(YEAR FROM created_at)={today.year}
          AND EXTRACT(MONTH FROM created_at)={today.month}
          AND status='completed'
    """)
    ord_today = safe_q1(f"""
        SELECT COUNT(*) FROM lumra_config_orders
        WHERE DATE(created_at)='{today}' AND status='completed'
    """)
    avg_order = safe_q1(f"""
        SELECT COALESCE(AVG(paid_amount),0) FROM lumra_config_orders
        WHERE EXTRACT(YEAR FROM created_at)={today.year} AND status='completed'
    """)
    total_orders  = safe_q1("SELECT COUNT(*) FROM lumra_config_orders WHERE status='completed'")
    total_revenue = safe_q1("SELECT COALESCE(SUM(paid_amount),0) FROM lumra_config_orders WHERE status='completed'")

    total_customers   = safe_q1("SELECT COUNT(*) FROM lumra_config_customers WHERE is_active=true")
    new_customers_mtd = safe_q1(f"""
        SELECT COUNT(*) FROM lumra_config_customers
        WHERE EXTRACT(YEAR FROM created_at)={today.year}
          AND EXTRACT(MONTH FROM created_at)={today.month}
    """)
    champions = safe_q1("SELECT COUNT(*) FROM lumra_crm_rfm_scores WHERE segment='champion'") \
                if table_exists("lumra_crm_rfm_scores") else 0
    at_risk   = safe_q1("SELECT COUNT(*) FROM lumra_crm_rfm_scores WHERE segment='at_risk'") \
                if table_exists("lumra_crm_rfm_scores") else 0

    total_stock_qty = safe_q1("SELECT COALESCE(SUM(quantity),0) FROM lumra_config_stock")
    low_stock = safe_q1("""
        SELECT COUNT(DISTINCT s.variant_id)
        FROM lumra_config_stock s
        JOIN lumra_config_productvariants pv ON pv.id=s.variant_id
        JOIN lumra_config_products p ON p.id=pv.product_id
        WHERE s.quantity < p.min_stock AND p.min_stock > 0
    """)
    expiring_30d = safe_q1(f"""
        SELECT COUNT(*) FROM lumra_config_product_batches
        WHERE expiry_date BETWEEN '{today}' AND '{today + timedelta(days=30)}'
          AND quantity_available > 0
    """)

    total_transfers      = safe_q1("SELECT COUNT(*) FROM lumra_config_transfers WHERE status='received'")
    pending_requisitions = safe_q1("SELECT COUNT(*) FROM lumra_config_requisitions WHERE status='pending'")
    active_production    = safe_q1("SELECT COUNT(*) FROM production_orders WHERE status='in_progress'")
    waste_this_month     = safe_q1(f"""
        SELECT COALESCE(SUM(quantity),0) FROM production_waste_records
        WHERE EXTRACT(YEAR FROM recorded_at)={today.year}
          AND EXTRACT(MONTH FROM recorded_at)={today.month}
    """)

    total_ap = safe_q1("SELECT COALESCE(SUM(total_amount-paid_amount),0) FROM accounting_accounts_payable WHERE status!='paid'")
    total_ar = safe_q1("SELECT COALESCE(SUM(total_amount-paid_amount),0) FROM accounting_accounts_receivable WHERE status!='paid'")

    target_this_month = safe_q1(f"""
        SELECT target_amount FROM lumra_config_sales_targets
        WHERE year={today.year} AND month={today.month}
    """) or 1
    achievement = float(rev_mtd) / float(target_this_month) * 100 if target_this_month else 0

    next_refresh = now + timedelta(hours=1)

    def kpi(key, group, label, num=None, text=None, jval=None,
            unit="", period="today", p_start=None, p_end=None,
            trend="neutral", change=0):
        return (key, group, label, num, text, jval, unit, period,
                p_start or today, p_end or today,
                None, trend, change, now, next_refresh)

    kpis = [
        kpi("revenue_today",       "sales", "Revenue Hari Ini",           float(rev_today),          unit="IDR", trend="up"),
        kpi("revenue_mtd",         "sales", "Revenue MTD",                float(rev_mtd),            unit="IDR", period="month", p_start=today.replace(day=1)),
        kpi("revenue_ytd",         "sales", "Revenue YTD",                float(rev_ytd),            unit="IDR", period="year",  p_start=today.replace(month=1,day=1)),
        kpi("revenue_total",       "sales", "Total Revenue All Time",     float(total_revenue),      unit="IDR"),
        kpi("orders_today",        "sales", "Orders Hari Ini",            float(ord_today),          unit="trx"),
        kpi("orders_total",        "sales", "Total Orders",               float(total_orders),       unit="trx"),
        kpi("avg_order_value",     "sales", "Avg Order Value (YTD)",      float(avg_order),          unit="IDR", period="year"),
        kpi("target_achievement",  "sales", "Pencapaian Target Bulan Ini",achievement,               unit="%",   period="month",
            trend="up" if achievement>=100 else "down", change=achievement-100),

        kpi("customers_total",     "crm", "Total Customer Aktif",         float(total_customers),    unit="customer"),
        kpi("customers_new_mtd",   "crm", "Customer Baru MTD",           float(new_customers_mtd),  unit="customer", period="month"),
        kpi("rfm_champions",       "crm", "Segment Champion",             float(champions),          unit="customer"),
        kpi("rfm_at_risk",         "crm", "Segment At Risk",              float(at_risk),            unit="customer", trend="down"),

        kpi("stock_qty_total",     "inventory", "Total Qty Stok",         float(total_stock_qty),    unit="unit"),
        kpi("stock_low_alert",     "inventory", "Produk Stok Menipis",    float(low_stock),          unit="sku",   trend="down" if low_stock>0 else "neutral"),
        kpi("batch_expiring_30d",  "inventory", "Batch Exp <= 30 hari",   float(expiring_30d),       unit="batch", trend="down" if expiring_30d>0 else "neutral"),

        kpi("transfers_completed", "operations","Transfer Selesai",        float(total_transfers),    unit="trf"),
        kpi("requisitions_pending","operations","Requisisi Pending",       float(pending_requisitions),unit="req"),
        kpi("production_active",   "operations","Production Order Aktif",  float(active_production),  unit="po"),
        kpi("waste_qty_mtd",       "operations","Waste Produksi MTD",      float(waste_this_month),   unit="qty", period="month"),

        kpi("ap_outstanding",      "finance","Hutang Belum Bayar",         float(total_ap),           unit="IDR", trend="down"),
        kpi("ar_outstanding",      "finance","Piutang Belum Terima",       float(total_ar),           unit="IDR"),
    ]

    log(f"KPI metrics: {len(kpis)}")
    if dry_run:
        log("[DRY RUN] Akan insert KPI cache")
        for k in kpis[:5]:
            print(f"      {k[0]:<30} {k[1]:<12} {str(k[3])[:15]}")
        return

    n = bulk_insert(
        "lumra_dashboard_kpi_cache",
        ["metric_key","metric_group","metric_label","value_numeric","value_text",
         "value_json","unit","period_type","period_start","period_end",
         "location_id","trend","change_pct","refreshed_at","next_refresh_at"],
        kpis,
        on_conflict="ON CONFLICT (metric_key) DO UPDATE SET "
                    "value_numeric=EXCLUDED.value_numeric, trend=EXCLUDED.trend, "
                    "change_pct=EXCLUDED.change_pct, refreshed_at=EXCLUDED.refreshed_at, "
                    "next_refresh_at=EXCLUDED.next_refresh_at"
    )
    ok(f"KPI cache: {n} metrics")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 9 — AUDIT TRAILS
# ═══════════════════════════════════════════════════════════════════════════════

CREATE_AUDIT = """
CREATE TABLE IF NOT EXISTS lumra_system_audit_trails (
    id              BIGSERIAL PRIMARY KEY,
    table_name      VARCHAR(80) NOT NULL,
    record_id       BIGINT NOT NULL,
    action          VARCHAR(10) NOT NULL,
    actor_id        BIGINT REFERENCES auth_user(id),
    actor_username  VARCHAR(150),
    old_values      JSONB,
    new_values      JSONB,
    changed_fields  TEXT[],
    ip_address      INET,
    user_agent      TEXT DEFAULT '',
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_table ON lumra_system_audit_trails(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON lumra_system_audit_trails(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_time  ON lumra_system_audit_trails(created_at DESC);
COMMENT ON TABLE lumra_system_audit_trails IS
    'Log audit perubahan data krusial: order, harga, stok adjustment, resep, user.';
"""

def fill_audit(dry_run=False, limit=50000):
    head("MODUL 9 — SYSTEM AUDIT TRAILS")

    if not dry_run:
        execute_sql(CREATE_AUDIT, "CREATE lumra_system_audit_trails")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]
    fake_ips = ["10.0.1."+str(i) for i in range(1, 56)]
    now      = datetime.now()

    audit_rows = []

    orders = q(f"""
        SELECT id, customer_id, paid_amount, status, created_at
        FROM lumra_config_orders
        ORDER BY RANDOM()
        LIMIT {limit // 3}
    """)
    for oid, cid, paid, status, created_at in orders:
        actor = RNG.choice(user_ids) if user_ids else admin_id
        audit_rows.append((
            "lumra_config_orders", oid, "UPDATE",
            actor, None,
            json.dumps({"status": "pending", "paid_amount": str(paid)}),
            json.dumps({"status": status,    "paid_amount": str(paid)}),
            ["status"],
            RNG.choice(fake_ips), "Mozilla/5.0 (Lumra POS)",
            "Order status update", created_at
        ))

    stock_mvs = q(f"""
        SELECT sm.id, sm.location_id, sm.product_id, sm.quantity, sm.movement_type, sm.created_at
        FROM lumra_config_stockmovement sm
        ORDER BY RANDOM()
        LIMIT {limit // 3}
    """)
    for sm_id, loc_id, var_id, qty, mvtype, created_at in stock_mvs:
        actor   = RNG.choice(user_ids) if user_ids else admin_id
        old_qty = int(qty or 0) + RNG.randint(-50, 50)
        audit_rows.append((
            "lumra_config_stock", var_id, "UPDATE",
            actor, None,
            json.dumps({"quantity": old_qty,       "location_id": loc_id}),
            json.dumps({"quantity": int(qty or 0), "location_id": loc_id}),
            ["quantity"],
            RNG.choice(fake_ips), "Lumra Inventory System",
            f"Stock {mvtype}", created_at
        ))

    pos = q(f"""
        SELECT id, code, status, created_at FROM production_orders
        ORDER BY RANDOM() LIMIT {limit // 6}
    """)
    for po_id, code, status, created_at in pos:
        actor = RNG.choice(user_ids) if user_ids else admin_id
        audit_rows.append((
            "production_orders", po_id, "UPDATE",
            actor, None,
            json.dumps({"status": "in_progress", "code": code}),
            json.dumps({"status": status,         "code": code}),
            ["status"],
            RNG.choice(fake_ips), "Lumra Production",
            "Production status update", created_at
        ))

    log(f"Audit trail rows: {len(audit_rows):,}")
    if dry_run:
        log(f"[DRY RUN] Akan insert {len(audit_rows):,} audit rows")
        return

    n = bulk_insert(
        "lumra_system_audit_trails",
        ["table_name","record_id","action","actor_id","actor_username",
         "old_values","new_values","changed_fields","ip_address","user_agent",
         "notes","created_at"],
        audit_rows, batch=2000
    )
    ok(f"Audit trails: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "procurement":  fill_procurement,
    "rfm":          fill_rfm,
    "promotions":   fill_promotions,
    "sales_agg":    fill_sales_agg,
    "product_perf": fill_product_perf,
    "inv_snapshot": fill_inv_snapshot,
    "shifts":       fill_shifts,
    "kpi_cache":    fill_kpi_cache,
    "audit":        fill_audit,
}

ORDER = ["procurement","rfm","promotions","sales_agg","product_perf","inv_snapshot","shifts","kpi_cache","audit"]

def main():
    t_total = time.time()
    print("\n" + "═"*70)
    print("  KAFE NUSANTARA — Database Expansion Script")
    print("  9 modul: Procurement, RFM, Promotions, Sales Agg,")
    print("           Product Perf, Inv Snapshot, Shifts, KPI Cache, Audit")
    print("═"*70)
    print(f"  Mode    : {'DRY RUN' if DRY_RUN else 'EXECUTE'}")
    print(f"  Section : {SECTION}")

    load_context()

    to_run  = ORDER if SECTION == "all" else [SECTION]
    results = {}

    for sec in to_run:
        fn = SECTION_MAP.get(sec)
        if not fn:
            warn(f"Section '{sec}' tidak dikenal. Pilihan: {list(SECTION_MAP.keys())}")
            continue
        try:
            fn(dry_run=DRY_RUN)
            results[sec] = "OK"
        except Exception as e:
            import traceback
            warn(f"ERROR di {sec}: {e}")
            traceback.print_exc()
            results[sec] = f"ERROR: {e}"

    elapsed = time.time() - t_total
    print("\n" + "═"*70)
    print(f"  SELESAI dalam {elapsed:.1f}s")
    print("─"*70)
    for sec, res in results.items():
        icon = "✓" if res == "OK" else "✗"
        print(f"  {icon} {sec:<20} {res}")
    print("═"*70)

    if DRY_RUN:
        print("\n  Jalankan dengan --execute untuk menyimpan ke DB\n")

    new_tables = [
        "lumra_procurement_purchase_orders",
        "lumra_procurement_po_items",
        "lumra_procurement_goods_receipts",
        "lumra_procurement_grn_items",
        "lumra_crm_rfm_scores",
        "lumra_sales_promotions",
        "lumra_sales_promotion_usage",
        "lumra_report_sales_daily",
        "lumra_report_sales_monthly",
        "lumra_report_product_performance",
        "lumra_report_inventory_snapshot",
        "lumra_ops_shifts",
        "lumra_ops_shift_sales_summary",
        "lumra_dashboard_kpi_cache",
        "lumra_system_audit_trails",
    ]
    print("  Tabel yang dibuat/diisi:")
    for t in new_tables:
        cnt     = row_count(t) if not DRY_RUN else "—"
        cnt_str = f"{cnt:,}" if isinstance(cnt, int) else cnt
        print(f"    {t:<45} {cnt_str:>12}")
    print()


try:
    from django.core.management.base import BaseCommand
    class Command(BaseCommand):
        help = "Kafe Nusantara — Database expansion (9 modules)"
        def add_arguments(self, p):
            p.add_argument("--execute", action="store_true", default=False)
            p.add_argument("--section", default="all")
        def handle(self, *args, **opts):
            global DRY_RUN, SECTION
            DRY_RUN = not opts["execute"]
            SECTION = opts["section"]
            main()
except ImportError:
    pass

if __name__ == "__main__":
    main()


seed 2
"""
seed_expansion2.py
==================
KAFE NUSANTARA — World Building Extension
Ekspansi database tahap 2: semua domain bisnis yang belum ter-cover.

MODUL BARU (10 modul tambahan):
  10. hr              — employees, schedules, attendance, payroll, payslip
  11. loyalty         — loyalty_tiers, stamp_cards, stamp_transactions, rewards, redemptions
  12. customer_journey— sessions, touchpoints, feedback, nps_responses
  13. finance_gl      — chart_of_accounts_ext, journal_entries, gl_postings, budgets, budget_actuals
  14. maintenance      — asset_registry, maintenance_schedules, work_orders, spare_parts
  15. supply_chain     — demand_forecast, reorder_alerts, supplier_scorecards, lead_times
  16. notifications    — notification_templates, notification_log, user_notification_prefs
  17. menu_engineering — menu_items_ext, item_modifiers, combos, menu_performance, ab_tests
  18. waste_costing    — waste_categories, waste_logs, waste_cost_summary, root_cause_tags
  19. training         — courses, enrollments, assessments, certifications, skill_matrix

Jalankan:
  python manage.py seed_expansion2 --execute
  python manage.py seed_expansion2 --execute --section=hr
  python manage.py seed_expansion2 --list-sections
"""

import os, sys, random, time, json, math
from decimal import Decimal
from datetime import date, datetime, timedelta, time as dtime

for _s in ("stdout", "stderr"):
    _o = getattr(sys, _s, None)
    if hasattr(_o, "reconfigure"):
        try: _o.reconfigure(encoding="utf-8", errors="replace")
        except: pass

# ── Args ──────────────────────────────────────────────────────────────────────
DRY_RUN = "--execute" not in sys.argv
SECTION = "all"
for i, a in enumerate(sys.argv[1:], 1):
    if a == "--section" and i < len(sys.argv): SECTION = sys.argv[i]
    elif a.startswith("--section="): SECTION = a.split("=",1)[1]

if "--list-sections" in sys.argv:
    print("Sections: hr loyalty customer_journey finance_gl maintenance "
          "supply_chain notifications menu_engineering waste_costing training all")
    sys.exit(0)

RNG = random.Random(99)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
import django; django.setup()
from django.db import connection

# ── Utilities (sama dengan seed_expansion.py) ─────────────────────────────────
def log(msg):  print(f"  {msg}", flush=True)
def ok(msg):   print(f"  ✓ {msg}", flush=True)
def warn(msg): print(f"  ⚠ {msg}", flush=True)
def head(msg):
    print(f"\n{'▓'*60}\n  {msg}\n{'▓'*60}")

def q(sql, params=None):
    with connection.cursor() as cur:
        cur.execute(sql, params) if params else cur.execute(sql)
        return cur.fetchall()

def q1(sql, params=None):
    rows = q(sql, params)
    return rows[0][0] if rows else None

def table_exists(name):
    return q1("SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s", [name]) > 0

def row_count(name):
    try: return q1(f"SELECT COUNT(*) FROM {name}")
    except: return -1

def execute_sql(sql, label=""):
    try:
        with connection.cursor() as cur:
            cur.execute(sql)
        if label: ok(label)
        return True
    except Exception as e:
        warn(f"{label}: {e}")
        return False

def bulk_insert(table, columns, rows, batch=2000, on_conflict="ON CONFLICT DO NOTHING"):
    if not rows: return 0
    cols = ", ".join(columns)
    ph   = ", ".join(["%s"] * len(columns))
    sql  = f"INSERT INTO {table} ({cols}) VALUES ({ph}) {on_conflict}"
    total = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i:i+batch]
        try:
            with connection.cursor() as cur:
                cur.executemany(sql, chunk)
                total += cur.rowcount if cur.rowcount >= 0 else len(chunk)
        except Exception as e:
            warn(f"Batch {i//batch+1} [{table}]: {e}")
            for row in chunk:
                try:
                    with connection.cursor() as cur:
                        cur.execute(sql, row)
                        total += 1
                except: pass
    return total

def progress(done, total, t0, label=""):
    pct = done / max(1, total) * 100
    ela = time.time() - t0
    eta = (ela / max(1, done)) * (total - done) if done < total else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"\r    [{bar}] {pct:5.1f}%  {done:,}/{total:,}  ETA {eta:.0f}s  {label}   ",
          end="", flush=True)

# ── Context ───────────────────────────────────────────────────────────────────
CTX = {}
def load_context():
    log("Loading context...")
    CTX["admin_id"]     = q1("SELECT id FROM auth_user WHERE is_superuser=true ORDER BY id LIMIT 1") \
                          or q1("SELECT id FROM auth_user ORDER BY id LIMIT 1")
    CTX["user_ids"]     = [r[0] for r in q("SELECT id FROM auth_user WHERE is_active=true ORDER BY id LIMIT 200")]
    CTX["location_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_locations ORDER BY id")]
    CTX["vendor_ids"]   = [r[0] for r in q("SELECT id FROM lumra_config_vendors ORDER BY id")]
    CTX["customer_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_customers WHERE is_active=true ORDER BY id LIMIT 5000")]
    CTX["variant_ids"]  = [r[0] for r in q("SELECT id FROM lumra_config_productvariants ORDER BY id LIMIT 2000")]
    CTX["order_ids"]    = [r[0] for r in q("SELECT id FROM lumra_config_orders WHERE status='completed' ORDER BY id LIMIT 50000")]
    CTX["min_date"]     = q1("SELECT MIN(created_at)::date FROM lumra_config_orders") or date(2023, 1, 1)
    CTX["max_date"]     = q1("SELECT MAX(created_at)::date FROM lumra_config_orders") or date.today()
    ok(f"Context: {len(CTX['location_ids'])} locs, {len(CTX['customer_ids'])} customers, "
       f"{len(CTX['order_ids'])} orders, {len(CTX['user_ids'])} users")

today = date.today()

# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 10 — HR: EMPLOYEES, SCHEDULE, ATTENDANCE, PAYROLL
# ═══════════════════════════════════════════════════════════════════════════════

def fill_hr(dry_run=False):
    head("MODUL 10 — HR (Employees, Schedules, Attendance, Payroll)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS hr_employees (
            id              BIGSERIAL PRIMARY KEY,
            employee_number VARCHAR(20) UNIQUE NOT NULL,
            user_id         BIGINT REFERENCES auth_user(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            full_name       VARCHAR(150) NOT NULL,
            nickname        VARCHAR(50) DEFAULT '',
            role            VARCHAR(40) NOT NULL DEFAULT 'barista',
            department      VARCHAR(40) NOT NULL DEFAULT 'operations',
            join_date       DATE NOT NULL,
            end_date        DATE,
            employment_type VARCHAR(20) DEFAULT 'full_time',
            status          VARCHAR(20) DEFAULT 'active',
            base_salary     NUMERIC(12,2) DEFAULT 0,
            allowance       NUMERIC(10,2) DEFAULT 0,
            bank_name       VARCHAR(50) DEFAULT '',
            bank_account    VARCHAR(30) DEFAULT '',
            phone           VARCHAR(20) DEFAULT '',
            emergency_contact VARCHAR(100) DEFAULT '',
            tax_id          VARCHAR(20) DEFAULT '',
            bpjs_health     VARCHAR(20) DEFAULT '',
            bpjs_employment VARCHAR(20) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE hr_employees IS
            'Karyawan Kafe Nusantara per outpost. Role: barista, cashier, supervisor, kitchen, manager.';
        CREATE INDEX IF NOT EXISTS idx_emp_location ON hr_employees(location_id);
        CREATE INDEX IF NOT EXISTS idx_emp_role ON hr_employees(role, status);
        """, "hr_employees"),

        ("""
        CREATE TABLE IF NOT EXISTS hr_work_schedules (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            schedule_date   DATE NOT NULL,
            shift_type      VARCHAR(20) NOT NULL,
            start_time      TIME NOT NULL,
            end_time        TIME NOT NULL,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            status          VARCHAR(20) DEFAULT 'scheduled',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(employee_id, schedule_date, shift_type)
        );
        COMMENT ON TABLE hr_work_schedules IS 'Jadwal kerja mingguan karyawan.';
        CREATE INDEX IF NOT EXISTS idx_sched_date ON hr_work_schedules(schedule_date);
        CREATE INDEX IF NOT EXISTS idx_sched_emp  ON hr_work_schedules(employee_id);
        """, "hr_work_schedules"),

        ("""
        CREATE TABLE IF NOT EXISTS hr_attendance (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            schedule_id     BIGINT REFERENCES hr_work_schedules(id),
            attendance_date DATE NOT NULL,
            clock_in        TIMESTAMPTZ,
            clock_out       TIMESTAMPTZ,
            late_minutes    INT DEFAULT 0,
            early_out_minutes INT DEFAULT 0,
            overtime_minutes  INT DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'present',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE hr_attendance IS
            'Absensi harian. Status: present, absent, sick, leave, holiday.';
        CREATE INDEX IF NOT EXISTS idx_att_date ON hr_attendance(attendance_date DESC);
        CREATE INDEX IF NOT EXISTS idx_att_emp  ON hr_attendance(employee_id);
        """, "hr_attendance"),

        ("""
        CREATE TABLE IF NOT EXISTS hr_payroll (
            id              BIGSERIAL PRIMARY KEY,
            payroll_period  VARCHAR(7) NOT NULL,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            base_salary     NUMERIC(12,2) DEFAULT 0,
            allowance       NUMERIC(10,2) DEFAULT 0,
            overtime_pay    NUMERIC(10,2) DEFAULT 0,
            deduction_late  NUMERIC(10,2) DEFAULT 0,
            deduction_absent NUMERIC(10,2) DEFAULT 0,
            bpjs_health_emp NUMERIC(10,2) DEFAULT 0,
            bpjs_emp_emp    NUMERIC(10,2) DEFAULT 0,
            pph21           NUMERIC(10,2) DEFAULT 0,
            gross_pay       NUMERIC(12,2) DEFAULT 0,
            net_pay         NUMERIC(12,2) DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'draft',
            paid_at         DATE,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(payroll_period, employee_id)
        );
        COMMENT ON TABLE hr_payroll IS
            'Slip gaji bulanan per karyawan. Period format: YYYY-MM.';
        CREATE INDEX IF NOT EXISTS idx_payroll_period ON hr_payroll(payroll_period DESC);
        """, "hr_payroll"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    min_date     = CTX["min_date"]
    max_date     = CTX["max_date"]

    # ── Employees ──────────────────────────────────────────────────────────────
    ROLES = ["barista","barista","barista","cashier","cashier","supervisor","kitchen","kitchen","manager"]
    DEPTS = {"barista":"operations","cashier":"operations","supervisor":"operations",
              "kitchen":"kitchen","manager":"management"}
    EMP_TYPES = ["full_time","full_time","full_time","part_time","contract"]

    FIRST_NAMES = ["Adi","Budi","Citra","Dewi","Eko","Fitri","Galih","Hani","Indra","Joko",
                   "Kartika","Luki","Maya","Nanda","Oki","Putri","Reza","Siti","Toni","Umar",
                   "Vina","Wati","Xandra","Yogi","Zahra","Bagas","Dina","Fajar","Gilang","Hendra"]
    LAST_NAMES  = ["Pratama","Wijaya","Santoso","Kusuma","Setiawan","Rahayu","Putra","Dewi",
                   "Saputra","Nugroho","Hidayat","Permata","Wibowo","Kurniawan","Utama"]

    emp_rows = []
    # ~5-8 karyawan per lokasi
    for loc_id in location_ids:
        n_emp = RNG.randint(5, 8)
        for j in range(n_emp):
            emp_num    = f"EMP-{loc_id:03d}-{j+1:03d}"
            name       = f"{RNG.choice(FIRST_NAMES)} {RNG.choice(LAST_NAMES)}"
            role       = RNG.choice(ROLES)
            dept       = DEPTS[role]
            emp_type   = RNG.choice(EMP_TYPES)
            join_days  = RNG.randint(30, 1200)
            join_date  = today - timedelta(days=join_days)
            base_sal   = Decimal(str({
                "barista": RNG.randint(3000000, 4500000),
                "cashier": RNG.randint(3000000, 4200000),
                "kitchen": RNG.randint(2800000, 4000000),
                "supervisor": RNG.randint(4500000, 6000000),
                "manager": RNG.randint(6000000, 10000000),
            }[role]))
            allowance  = base_sal * Decimal("0.1")
            uid        = RNG.choice(user_ids) if user_ids else None
            emp_rows.append((
                emp_num, uid, loc_id, name,
                name.split()[0], role, dept,
                join_date, None, emp_type, "active",
                base_sal, allowance,
                RNG.choice(["BCA","BNI","Mandiri","BRI"]),
                f"{RNG.randint(1000000000,9999999999)}",
                f"08{RNG.randint(100000000,999999999)}",
                f"{RNG.choice(FIRST_NAMES)} {RNG.choice(LAST_NAMES)} (Saudara)",
                f"{RNG.randint(10,99)}.{RNG.randint(100,999)}.{RNG.randint(100,999)}.{RNG.randint(1,9)}-{RNG.randint(100,999)}.{RNG.randint(100,999)}",
                f"BPJSK{RNG.randint(100000000,999999999)}",
                f"BPJSM{RNG.randint(100000000,999999999)}",
                join_date, join_date
            ))

    log(f"Employees: {len(emp_rows)}")
    if dry_run:
        log(f"[DRY RUN] {len(emp_rows)} employees, schedules, attendance, payroll")
        return

    n = bulk_insert("hr_employees",
        ["employee_number","user_id","location_id","full_name","nickname",
         "role","department","join_date","end_date","employment_type","status",
         "base_salary","allowance","bank_name","bank_account","phone",
         "emergency_contact","tax_id","bpjs_health","bpjs_employment",
         "created_at","updated_at"],
        emp_rows, on_conflict="ON CONFLICT (employee_number) DO NOTHING")
    ok(f"Employees: {n:,}")

    # ── Schedules ──────────────────────────────────────────────────────────────
    employees = q("SELECT id, location_id FROM hr_employees ORDER BY id")
    SHIFT_MAP = [
        ("first_light",      dtime(7,0),  dtime(12,0)),
        ("midday_transit",   dtime(12,0), dtime(18,0)),
        ("twilight_bivouac", dtime(18,0), dtime(23,0)),
    ]

    sched_rows = []
    # 30 hari ke depan + 30 hari ke belakang
    for emp_id, loc_id in employees:
        for d in range(-30, 31):
            sched_date = today + timedelta(days=d)
            # random 1-2 shift per hari, skip 1 hari/minggu (libur)
            if sched_date.weekday() == RNG.randint(0, 6):
                continue
            stype, st, et = RNG.choice(SHIFT_MAP)
            sched_rows.append((
                emp_id, sched_date, stype, st, et, loc_id,
                "completed" if d < 0 else "scheduled",
                "", datetime.now()
            ))

    n = bulk_insert("hr_work_schedules",
        ["employee_id","schedule_date","shift_type","start_time","end_time",
         "location_id","status","notes","created_at"],
        sched_rows, batch=3000,
        on_conflict="ON CONFLICT (employee_id, schedule_date, shift_type) DO NOTHING")
    ok(f"Schedules: {n:,}")

    # ── Attendance ─────────────────────────────────────────────────────────────
    saved_scheds = q("SELECT id, employee_id, schedule_date, start_time, end_time FROM hr_work_schedules WHERE schedule_date < %s ORDER BY id", [today])
    att_rows = []
    for sid, emp_id, sched_date, st, et in saved_scheds:
        status = RNG.choices(
            ["present","present","present","present","absent","sick","leave"],
            weights=[70, 0, 0, 0, 10, 15, 5]
        )[0]
        late = RNG.randint(0, 30) if status == "present" and RNG.random() < 0.2 else 0
        overtime = RNG.randint(0, 90) if status == "present" and RNG.random() < 0.15 else 0
        clock_in  = datetime.combine(sched_date, st) + timedelta(minutes=late) if status == "present" else None
        clock_out = datetime.combine(sched_date, et) + timedelta(minutes=overtime) if status == "present" else None
        att_rows.append((
            emp_id, sid, sched_date,
            clock_in, clock_out,
            late, 0, overtime,
            status, "", datetime.now()
        ))

    n = bulk_insert("hr_attendance",
        ["employee_id","schedule_id","attendance_date","clock_in","clock_out",
         "late_minutes","early_out_minutes","overtime_minutes","status","notes","created_at"],
        att_rows, batch=3000)
    ok(f"Attendance: {n:,}")

    # ── Payroll ────────────────────────────────────────────────────────────────
    emp_detail = q("SELECT id, base_salary, allowance FROM hr_employees")
    payroll_rows = []
    # 12 bulan ke belakang
    for yr_offset in range(12):
        ref = today.replace(day=1) - timedelta(days=yr_offset * 30)
        period = ref.strftime("%Y-%m")
        for emp_id, base_sal, allowance in emp_detail:
            base_sal  = Decimal(str(base_sal or 0))
            allowance = Decimal(str(allowance or 0))
            overtime  = base_sal / 173 * Decimal(str(RNG.randint(0, 20)))
            ded_late  = base_sal / 173 / 60 * Decimal(str(RNG.randint(0, 60)))
            ded_abs   = base_sal / 26 * Decimal(str(RNG.randint(0, 2)))
            bpjs_h    = (base_sal + allowance) * Decimal("0.01")
            bpjs_e    = (base_sal + allowance) * Decimal("0.02")
            gross     = base_sal + allowance + overtime
            pph21     = max(Decimal("0"), (gross * 12 - 54000000) / 12 * Decimal("0.05"))
            net       = gross - ded_late - ded_abs - bpjs_h - bpjs_e - pph21
            payroll_rows.append((
                period, emp_id,
                base_sal.quantize(Decimal("0.01")),
                allowance.quantize(Decimal("0.01")),
                overtime.quantize(Decimal("0.01")),
                ded_late.quantize(Decimal("0.01")),
                ded_abs.quantize(Decimal("0.01")),
                bpjs_h.quantize(Decimal("0.01")),
                bpjs_e.quantize(Decimal("0.01")),
                pph21.quantize(Decimal("0.01")),
                gross.quantize(Decimal("0.01")),
                net.quantize(Decimal("0.01")),
                "paid", ref + timedelta(days=25),
                "", datetime.now()
            ))

    n = bulk_insert("hr_payroll",
        ["payroll_period","employee_id","base_salary","allowance","overtime_pay",
         "deduction_late","deduction_absent","bpjs_health_emp","bpjs_emp_emp",
         "pph21","gross_pay","net_pay","status","paid_at","notes","created_at"],
        payroll_rows,
        on_conflict="ON CONFLICT (payroll_period, employee_id) DO NOTHING")
    ok(f"Payroll: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 11 — LOYALTY PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def fill_loyalty(dry_run=False):
    head("MODUL 11 — LOYALTY (Tiers, Stamp Cards, Transactions, Rewards)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS loyalty_tiers (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(80) NOT NULL,
            description     TEXT DEFAULT '',
            min_points      INT NOT NULL DEFAULT 0,
            max_points      INT,
            discount_pct    NUMERIC(5,2) DEFAULT 0,
            stamp_multiplier NUMERIC(4,2) DEFAULT 1.0,
            perks           JSONB DEFAULT '[]',
            badge_color     VARCHAR(20) DEFAULT '#888888',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_tiers IS
            'Tier loyalty Kafe Nusantara: Expeditor → Field Surveyor → Cartographer → Grand Curator.';
        """, "loyalty_tiers"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_stamp_cards (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT NOT NULL UNIQUE REFERENCES lumra_config_customers(id),
            card_number     VARCHAR(30) UNIQUE NOT NULL,
            tier_id         BIGINT REFERENCES loyalty_tiers(id),
            total_points    INT DEFAULT 0,
            current_stamps  INT DEFAULT 0,
            lifetime_stamps INT DEFAULT 0,
            lifetime_spend  NUMERIC(15,2) DEFAULT 0,
            outposts_visited INT DEFAULT 0,
            last_visit_date DATE,
            member_since    DATE DEFAULT CURRENT_DATE,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_stamp_cards IS
            'Kartu stamp digital per customer. 10 stamps = 1 reward free drink.';
        CREATE INDEX IF NOT EXISTS idx_stamp_tier ON loyalty_stamp_cards(tier_id);
        """, "loyalty_stamp_cards"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_stamp_transactions (
            id              BIGSERIAL PRIMARY KEY,
            card_id         BIGINT NOT NULL REFERENCES loyalty_stamp_cards(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            transaction_type VARCHAR(20) NOT NULL DEFAULT 'earn',
            stamps_delta    INT NOT NULL DEFAULT 0,
            points_delta    INT NOT NULL DEFAULT 0,
            spend_amount    NUMERIC(12,2) DEFAULT 0,
            note            TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_stamp_transactions IS
            'Riwayat earn/redeem stamp dan poin per transaksi.';
        CREATE INDEX IF NOT EXISTS idx_stamp_tx_card ON loyalty_stamp_transactions(card_id);
        CREATE INDEX IF NOT EXISTS idx_stamp_tx_date ON loyalty_stamp_transactions(created_at DESC);
        """, "loyalty_stamp_transactions"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_rewards (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(120) NOT NULL,
            description     TEXT DEFAULT '',
            reward_type     VARCHAR(30) NOT NULL DEFAULT 'free_drink',
            stamps_required INT DEFAULT 10,
            points_required INT DEFAULT 0,
            valid_days      INT DEFAULT 30,
            is_active       BOOLEAN DEFAULT TRUE,
            stock_limit     INT,
            redeemed_count  INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_rewards IS
            'Katalog reward yang bisa diredeem: free drink, pastry, merchandise, diskon.';
        """, "loyalty_rewards"),

        ("""
        CREATE TABLE IF NOT EXISTS loyalty_redemptions (
            id              BIGSERIAL PRIMARY KEY,
            card_id         BIGINT NOT NULL REFERENCES loyalty_stamp_cards(id),
            reward_id       BIGINT NOT NULL REFERENCES loyalty_rewards(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            stamps_used     INT DEFAULT 0,
            points_used     INT DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'redeemed',
            redeemed_at     TIMESTAMPTZ DEFAULT NOW(),
            expires_at      TIMESTAMPTZ,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE loyalty_redemptions IS 'Log redeem reward oleh customer.';
        CREATE INDEX IF NOT EXISTS idx_redemption_card ON loyalty_redemptions(card_id);
        """, "loyalty_redemptions"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # ── Tiers ──────────────────────────────────────────────────────────────────
    tiers_data = [
        ("EXPEDITOR",    "Expeditor",          "Member baru yang baru memulai petualangan.",
         0,     999,  0,   1.0, ["Early bird notification"], "#8B7355"),
        ("FIELD_SURVEYOR","Field Surveyor",    "5+ outpost dikunjungi. Diskon 5% permanent.",
         1000,  4999, 5,   1.2, ["5% discount","Priority queue","Monthly newsletter"], "#4A90A4"),
        ("CARTOGRAPHER", "Senior Cartographer","10+ outpost. Early access menu seasonal.",
         5000,  19999,8,   1.5, ["8% discount","Early access seasonal menu","Free size upgrade 1x/month","Birthday privilege"], "#D4AF37"),
        ("GRAND_CURATOR","Grand Curator",      "Elite member. Akses Grand Reserve menu eksklusif.",
         20000, None, 15,  2.0, ["15% permanent","Grand Reserve access","Free drink monthly","VIP event invite","Personal barista note"], "#1A1A2E"),
    ]
    tier_rows = [(code, name, desc, Decimal(str(minp)), maxp,
                  Decimal(str(disc)), Decimal(str(mult)),
                  json.dumps(perks), color, True, datetime.now())
                 for code, name, desc, minp, maxp, disc, mult, perks, color in tiers_data]

    if not dry_run:
        n = bulk_insert("loyalty_tiers",
            ["code","name","description","min_points","max_points",
             "discount_pct","stamp_multiplier","perks","badge_color","is_active","created_at"],
            tier_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
        ok(f"Loyalty tiers: {n}")

    # ── Rewards catalog ────────────────────────────────────────────────────────
    rewards_data = [
        ("FREE-FILTER",  "Free Filter Coffee",      "1 gelas filter coffee house blend gratis.", "free_drink", 10, 0,   30),
        ("FREE-COLD",    "Free Cold Brew",           "1 gelas cold brew any size.",               "free_drink", 12, 0,   30),
        ("FREE-PASTRY",  "Free Pastry",              "1 pastry pilihan gratis.",                  "free_food",  8,  0,   14),
        ("FREE-GRANOLA", "Free Granola Bowl",        "Granola bowl artisan gratis.",               "free_food",  15, 0,   14),
        ("DISC-20PCT",   "Diskon 20%",               "Diskon 20% untuk satu transaksi.",          "discount",   0,  500, 7),
        ("DISC-50K",     "Voucher Rp 50.000",        "Potongan Rp 50.000 min. transaksi 150rb.",  "voucher",    0,  800, 14),
        ("MERCH-TUMBLER","Kafe Nusantara Tumbler",   "Tumbler edisi terbatas Kafe Nusantara.",    "merchandise",0, 2000, 90),
        ("MERCH-TOTE",   "Expedition Tote Bag",      "Tote bag canvas The Daily Expedition.",     "merchandise",0, 1500, 90),
        ("UPGRADE-SIZE", "Size Upgrade Gratis",      "Upgrade size minuman any size.",             "upgrade",    5,  0,   7),
        ("EARLY-ACCESS", "Early Access Menu Seasonal","Preview menu musim baru 3 hari lebih awal.","experience", 0, 300, 30),
    ]
    reward_rows = [(code, name, desc, rtype, stamps, points, vdays, True, None, 0, datetime.now())
                   for code, name, desc, rtype, stamps, points, vdays in rewards_data]

    if not dry_run:
        n = bulk_insert("loyalty_rewards",
            ["code","name","description","reward_type","stamps_required",
             "points_required","valid_days","is_active","stock_limit","redeemed_count","created_at"],
            reward_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
        ok(f"Rewards: {n}")

    # ── Stamp Cards ────────────────────────────────────────────────────────────
    customer_ids = CTX["customer_ids"]
    tier_ids     = [r[0] for r in q("SELECT id FROM loyalty_tiers ORDER BY min_points")]

    card_rows = []
    for i, cid in enumerate(customer_ids):
        lifetime_stamps = RNG.randint(0, 500)
        lifetime_spend  = Decimal(str(lifetime_stamps * RNG.randint(30000, 80000)))
        current_stamps  = lifetime_stamps % 10
        total_points    = lifetime_stamps * RNG.randint(5, 20)
        # tentukan tier berdasarkan total_points
        tier_id = tier_ids[0]
        for tid, minp in q("SELECT id, min_points FROM loyalty_tiers ORDER BY min_points DESC"):
            if total_points >= minp:
                tier_id = tid
                break
        outposts = min(len(CTX["location_ids"]), RNG.randint(1, 20))
        last_visit = today - timedelta(days=RNG.randint(0, 180))
        card_rows.append((
            cid, f"KN{cid:08d}", tier_id,
            total_points, current_stamps, lifetime_stamps,
            lifetime_spend.quantize(Decimal("0.01")),
            outposts, last_visit,
            today - timedelta(days=RNG.randint(30, 730)),
            True, datetime.now(), datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(card_rows)} stamp cards + transactions + redemptions")
        return

    n = bulk_insert("loyalty_stamp_cards",
        ["customer_id","card_number","tier_id","total_points","current_stamps",
         "lifetime_stamps","lifetime_spend","outposts_visited","last_visit_date",
         "member_since","is_active","created_at","updated_at"],
        card_rows,
        on_conflict="ON CONFLICT (customer_id) DO NOTHING")
    ok(f"Stamp cards: {n:,}")

    # ── Stamp Transactions ─────────────────────────────────────────────────────
    card_data    = q("SELECT id, customer_id FROM loyalty_stamp_cards ORDER BY id LIMIT 3000")
    order_ids    = CTX["order_ids"]
    location_ids = CTX["location_ids"]
    reward_ids   = [r[0] for r in q("SELECT id FROM loyalty_rewards ORDER BY id")]

    stamp_tx_rows   = []
    redemption_rows = []

    for card_id, cust_id in card_data:
        n_tx = RNG.randint(3, 30)
        for _ in range(n_tx):
            tx_type  = RNG.choices(["earn","earn","earn","bonus","redeem"], weights=[60,0,0,20,20])[0]
            stamps   = RNG.randint(1, 3) if tx_type in ("earn","bonus") else -10
            points   = stamps * RNG.randint(5, 15)
            spend    = Decimal(str(RNG.randint(25000, 200000))) if tx_type == "earn" else Decimal("0")
            oid      = RNG.choice(order_ids) if order_ids else None
            lid      = RNG.choice(location_ids)
            tx_date  = datetime.now() - timedelta(days=RNG.randint(0, 365))
            stamp_tx_rows.append((
                card_id, oid, lid, tx_type, stamps, points,
                spend.quantize(Decimal("0.01")), "", tx_date
            ))
            if tx_type == "redeem" and reward_ids:
                rid = RNG.choice(reward_ids)
                redemption_rows.append((
                    card_id, rid, oid, lid, 10, 0,
                    "redeemed", tx_date,
                    tx_date + timedelta(days=30), tx_date
                ))

    n = bulk_insert("loyalty_stamp_transactions",
        ["card_id","order_id","location_id","transaction_type","stamps_delta",
         "points_delta","spend_amount","note","created_at"],
        stamp_tx_rows, batch=3000)
    ok(f"Stamp transactions: {n:,}")

    n = bulk_insert("loyalty_redemptions",
        ["card_id","reward_id","order_id","location_id","stamps_used","points_used",
         "status","redeemed_at","expires_at","created_at"],
        redemption_rows)
    ok(f"Redemptions: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 12 — CUSTOMER JOURNEY (Sessions, Touchpoints, Feedback, NPS)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_customer_journey(dry_run=False):
    head("MODUL 12 — CUSTOMER JOURNEY (Sessions, Touchpoints, Feedback, NPS)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS cj_customer_sessions (
            id              BIGSERIAL PRIMARY KEY,
            session_uuid    UUID DEFAULT gen_random_uuid() UNIQUE,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            channel         VARCHAR(30) DEFAULT 'dine_in',
            session_start   TIMESTAMPTZ NOT NULL,
            session_end     TIMESTAMPTZ,
            duration_minutes INT DEFAULT 0,
            order_count     INT DEFAULT 0,
            total_spend     NUMERIC(12,2) DEFAULT 0,
            device_type     VARCHAR(20) DEFAULT 'unknown',
            referral_source VARCHAR(50) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_customer_sessions IS
            'Sesi kunjungan customer per outpost. Channel: dine_in, takeaway, delivery, online.';
        CREATE INDEX IF NOT EXISTS idx_cj_sess_cust ON cj_customer_sessions(customer_id);
        CREATE INDEX IF NOT EXISTS idx_cj_sess_loc  ON cj_customer_sessions(location_id);
        CREATE INDEX IF NOT EXISTS idx_cj_sess_date ON cj_customer_sessions(session_start DESC);
        """, "cj_customer_sessions"),

        ("""
        CREATE TABLE IF NOT EXISTS cj_touchpoints (
            id              BIGSERIAL PRIMARY KEY,
            session_id      BIGINT REFERENCES cj_customer_sessions(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            touchpoint_type VARCHAR(40) NOT NULL,
            channel         VARCHAR(30) DEFAULT 'dine_in',
            content_ref     VARCHAR(100) DEFAULT '',
            sentiment       VARCHAR(10) DEFAULT 'neutral',
            duration_sec    INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_touchpoints IS
            'Titik interaksi customer: menu_view, order, payment, feedback, loyalty_check, promo_claim.';
        CREATE INDEX IF NOT EXISTS idx_tp_session ON cj_touchpoints(session_id);
        CREATE INDEX IF NOT EXISTS idx_tp_type    ON cj_touchpoints(touchpoint_type);
        """, "cj_touchpoints"),

        ("""
        CREATE TABLE IF NOT EXISTS cj_feedback (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            feedback_type   VARCHAR(30) DEFAULT 'general',
            rating_overall  SMALLINT CHECK(rating_overall BETWEEN 1 AND 5),
            rating_product  SMALLINT CHECK(rating_product BETWEEN 1 AND 5),
            rating_service  SMALLINT CHECK(rating_service BETWEEN 1 AND 5),
            rating_ambiance SMALLINT CHECK(rating_ambiance BETWEEN 1 AND 5),
            comment         TEXT DEFAULT '',
            tags            TEXT[] DEFAULT '{}',
            is_public       BOOLEAN DEFAULT FALSE,
            replied_at      TIMESTAMPTZ,
            reply_text      TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_feedback IS
            'Feedback & rating customer per order/kunjungan. 1-5 bintang multi-dimensi.';
        CREATE INDEX IF NOT EXISTS idx_fb_location ON cj_feedback(location_id);
        CREATE INDEX IF NOT EXISTS idx_fb_rating   ON cj_feedback(rating_overall DESC);
        CREATE INDEX IF NOT EXISTS idx_fb_date     ON cj_feedback(created_at DESC);
        """, "cj_feedback"),

        ("""
        CREATE TABLE IF NOT EXISTS cj_nps_responses (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            survey_period   VARCHAR(7) NOT NULL,
            nps_score       SMALLINT NOT NULL CHECK(nps_score BETWEEN 0 AND 10),
            category        VARCHAR(15) GENERATED ALWAYS AS (
                CASE WHEN nps_score >= 9 THEN 'promoter'
                     WHEN nps_score >= 7 THEN 'passive'
                     ELSE 'detractor' END
            ) STORED,
            reason          TEXT DEFAULT '',
            follow_up_done  BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cj_nps_responses IS
            'Net Promoter Score survey bulanan. 0-6=detractor, 7-8=passive, 9-10=promoter.';
        CREATE INDEX IF NOT EXISTS idx_nps_period ON cj_nps_responses(survey_period);
        CREATE INDEX IF NOT EXISTS idx_nps_score  ON cj_nps_responses(nps_score);
        """, "cj_nps_responses"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    customer_ids = CTX["customer_ids"]
    location_ids = CTX["location_ids"]
    order_ids    = CTX["order_ids"]
    min_date     = CTX["min_date"]
    max_date     = CTX["max_date"]

    CHANNELS      = ["dine_in","dine_in","dine_in","takeaway","delivery"]
    DEVICES       = ["mobile","mobile","desktop","tablet","unknown"]
    REFERRALS     = ["instagram","google","friend","tiktok","walk_in","walk_in","walk_in"]
    TP_TYPES      = ["menu_view","menu_view","order_placed","payment","loyalty_check",
                     "promo_claim","table_service","takeaway_pickup"]
    SENTIMENTS    = ["positive","positive","neutral","neutral","negative"]
    FB_TYPES      = ["general","product","service","ambiance","complaint","compliment"]
    FB_TAGS       = [["kopi_enak","pelayanan_ramah"],["antri_lama"],["tempatnya_nyaman"],
                     ["harga_worth_it"],["barista_friendly"],["ambiance_bagus"],
                     ["cold_brew_top"],["pastry_fresh"]]
    NPS_REASONS   = [
        "Kopi-nya konsisten enak di semua outpost.",
        "Barista-nya ramah dan selalu ingat pesanan saya.",
        "Tempatnya nyaman untuk kerja.",
        "Harga sesuai dengan kualitas.",
        "Kadang antri terlalu lama.",
        "Menu seasonal selalu menarik.",
        "Sudah jadi tempat nongkrong favorit saya.",
        "Loyalty program-nya bikin betah.",
    ]

    # Sessions
    sess_rows = []
    total_days = (max_date - min_date).days
    for cid in RNG.sample(customer_ids, min(2000, len(customer_ids))):
        n_sess = RNG.randint(1, 15)
        for _ in range(n_sess):
            sess_start = datetime.combine(
                min_date + timedelta(days=RNG.randint(0, total_days)),
                dtime(RNG.randint(7, 22), RNG.randint(0, 59))
            )
            duration  = RNG.randint(10, 120)
            sess_end  = sess_start + timedelta(minutes=duration)
            n_orders  = RNG.randint(0, 3)
            spend     = Decimal(str(n_orders * RNG.randint(20000, 100000)))
            sess_rows.append((
                cid, RNG.choice(location_ids),
                RNG.choice(CHANNELS),
                sess_start, sess_end, duration,
                n_orders, spend.quantize(Decimal("0.01")),
                RNG.choice(DEVICES), RNG.choice(REFERRALS),
                sess_start
            ))

    log(f"Sessions: {len(sess_rows)}")
    if dry_run:
        log(f"[DRY RUN] sessions, touchpoints, feedback, NPS")
        return

    n = bulk_insert("cj_customer_sessions",
        ["customer_id","location_id","channel","session_start","session_end",
         "duration_minutes","order_count","total_spend","device_type","referral_source","created_at"],
        sess_rows, batch=3000)
    ok(f"Sessions: {n:,}")

    # Touchpoints
    saved_sessions = q("SELECT id, customer_id FROM cj_customer_sessions ORDER BY id LIMIT 5000")
    tp_rows = []
    for sess_id, cid in saved_sessions:
        for _ in range(RNG.randint(2, 8)):
            tp_rows.append((
                sess_id, cid,
                RNG.choice(TP_TYPES),
                RNG.choice(CHANNELS),
                "", RNG.choice(SENTIMENTS),
                RNG.randint(5, 300),
                datetime.now() - timedelta(days=RNG.randint(0, 365))
            ))

    n = bulk_insert("cj_touchpoints",
        ["session_id","customer_id","touchpoint_type","channel","content_ref",
         "sentiment","duration_sec","created_at"],
        tp_rows, batch=3000)
    ok(f"Touchpoints: {n:,}")

    # Feedback
    fb_rows = []
    for _ in range(min(10000, len(order_ids))):
        oid  = RNG.choice(order_ids)
        cid  = RNG.choice(customer_ids)
        lid  = RNG.choice(location_ids)
        base = RNG.randint(3, 5)
        fb_rows.append((
            cid, oid, lid,
            RNG.choice(FB_TYPES),
            base,
            max(1, base + RNG.randint(-1, 1)),
            max(1, base + RNG.randint(-1, 1)),
            max(1, base + RNG.randint(-1, 1)),
            "",
            json.dumps(RNG.choice(FB_TAGS)),
            RNG.random() < 0.3,
            None, "",
            datetime.now() - timedelta(days=RNG.randint(0, 365))
        ))

    n = bulk_insert("cj_feedback",
        ["customer_id","order_id","location_id","feedback_type",
         "rating_overall","rating_product","rating_service","rating_ambiance",
         "comment","tags","is_public","replied_at","reply_text","created_at"],
        fb_rows, batch=3000)
    ok(f"Feedback: {n:,}")

    # NPS
    nps_rows = []
    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            if date(yr, mo, 1) > today: break
            period    = f"{yr}-{mo:02d}"
            n_resp    = RNG.randint(30, 150)
            respondents = RNG.sample(customer_ids, min(n_resp, len(customer_ids)))
            for cid in respondents:
                # distribusi NPS: ~60% promoter (9-10), ~20% passive (7-8), ~20% detractor (0-6)
                score = RNG.choices(
                    list(range(11)),
                    weights=[2,2,3,3,4,6,10,10,15,20,25]
                )[0]
                nps_rows.append((
                    cid, RNG.choice(location_ids),
                    period, score,
                    RNG.choice(NPS_REASONS),
                    score < 7,
                    datetime.now() - timedelta(days=RNG.randint(0, 30))
                ))

    n = bulk_insert("cj_nps_responses",
        ["customer_id","location_id","survey_period","nps_score",
         "reason","follow_up_done","created_at"],
        nps_rows)
    ok(f"NPS responses: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 13 — FINANCE GL (Journal Entries, Budgets)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_finance_gl(dry_run=False):
    head("MODUL 13 — FINANCE GL (Journal Entries, GL Postings, Budgets)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS finance_journal_entries (
            id              BIGSERIAL PRIMARY KEY,
            entry_number    VARCHAR(30) UNIQUE NOT NULL,
            entry_date      DATE NOT NULL,
            period          VARCHAR(7) NOT NULL,
            entry_type      VARCHAR(30) NOT NULL DEFAULT 'manual',
            description     TEXT NOT NULL DEFAULT '',
            reference_type  VARCHAR(40) DEFAULT '',
            reference_id    BIGINT,
            total_debit     NUMERIC(15,2) DEFAULT 0,
            total_credit    NUMERIC(15,2) DEFAULT 0,
            status          VARCHAR(20) DEFAULT 'posted',
            created_by_id   BIGINT REFERENCES auth_user(id),
            approved_by_id  BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE finance_journal_entries IS
            'Jurnal akuntansi: penjualan, pembelian, biaya, penyesuaian, opening balance.';
        CREATE INDEX IF NOT EXISTS idx_je_date   ON finance_journal_entries(entry_date DESC);
        CREATE INDEX IF NOT EXISTS idx_je_period ON finance_journal_entries(period);
        CREATE INDEX IF NOT EXISTS idx_je_type   ON finance_journal_entries(entry_type);
        """, "finance_journal_entries"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_gl_postings (
            id              BIGSERIAL PRIMARY KEY,
            journal_id      BIGINT NOT NULL REFERENCES finance_journal_entries(id),
            account_id      BIGINT REFERENCES accounting_accounts(id),
            account_code    VARCHAR(20) NOT NULL DEFAULT '',
            account_name    VARCHAR(100) DEFAULT '',
            debit           NUMERIC(15,2) DEFAULT 0,
            credit          NUMERIC(15,2) DEFAULT 0,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            description     TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE finance_gl_postings IS
            'Baris debit/kredit per jurnal. Double-entry bookkeeping.';
        CREATE INDEX IF NOT EXISTS idx_gl_journal  ON finance_gl_postings(journal_id);
        CREATE INDEX IF NOT EXISTS idx_gl_account  ON finance_gl_postings(account_id);
        CREATE INDEX IF NOT EXISTS idx_gl_location ON finance_gl_postings(location_id);
        """, "finance_gl_postings"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_budgets (
            id              BIGSERIAL PRIMARY KEY,
            budget_year     SMALLINT NOT NULL,
            budget_month    SMALLINT,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            category        VARCHAR(50) NOT NULL,
            account_code    VARCHAR(20) DEFAULT '',
            budget_amount   NUMERIC(15,2) NOT NULL DEFAULT 0,
            notes           TEXT DEFAULT '',
            created_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(budget_year, budget_month, location_id, category)
        );
        COMMENT ON TABLE finance_budgets IS
            'Anggaran tahunan/bulanan per kategori dan lokasi.';
        CREATE INDEX IF NOT EXISTS idx_budget_ym ON finance_budgets(budget_year, budget_month);
        """, "finance_budgets"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_budget_actuals (
            id              BIGSERIAL PRIMARY KEY,
            budget_id       BIGINT NOT NULL REFERENCES finance_budgets(id),
            actual_amount   NUMERIC(15,2) DEFAULT 0,
            variance_amount NUMERIC(15,2) DEFAULT 0,
            variance_pct    NUMERIC(6,2) DEFAULT 0,
            as_of_date      DATE NOT NULL,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(budget_id, as_of_date)
        );
        COMMENT ON TABLE finance_budget_actuals IS
            'Realisasi aktual vs anggaran per periode.';
        """, "finance_budget_actuals"),

        ("""
        CREATE TABLE IF NOT EXISTS finance_cost_centers (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            parent_id       BIGINT REFERENCES finance_cost_centers(id),
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE finance_cost_centers IS
            'Cost center per outpost/departemen untuk alokasi biaya.';
        """, "finance_cost_centers"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    admin_id     = CTX["admin_id"]
    user_ids     = CTX["user_ids"]
    min_date     = CTX["min_date"]

    # Cost Centers
    cc_rows = []
    for lid in location_ids:
        for dept in ["operations","kitchen","management","marketing"]:
            cc_rows.append((
                f"CC-{lid:03d}-{dept[:3].upper()}",
                f"Cost Center {dept.title()} - Loc {lid}",
                lid, None, True, datetime.now()
            ))

    if not dry_run:
        n = bulk_insert("finance_cost_centers",
            ["code","name","location_id","parent_id","is_active","created_at"],
            cc_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
        ok(f"Cost centers: {n}")

    # Journal Entries + GL Postings
    JE_TYPES = ["sales_revenue","purchase_expense","payroll_expense","depreciation",
                "accrual","adjustment","opening_balance"]
    accounts = q("SELECT id, code, name FROM accounting_accounts LIMIT 50")
    if not accounts:
        accounts = [(1,"1-1001","Kas Tunai"),(2,"4-1001","Penjualan"),(3,"5-1001","HPP")]

    je_rows = []
    gl_rows = []
    je_ctr  = 1

    # Generate ~2000 jurnal 2 tahun ke belakang
    ref_date = min_date
    days_range = (today - ref_date).days
    for _ in range(2000):
        entry_date = ref_date + timedelta(days=RNG.randint(0, days_range))
        period     = entry_date.strftime("%Y-%m")
        je_type    = RNG.choice(JE_TYPES)
        amount     = Decimal(str(RNG.randint(100000, 50000000)))
        entry_num  = f"JE-{entry_date.year}-{je_ctr:06d}"
        creator    = RNG.choice(user_ids) if user_ids else admin_id

        je_rows.append((
            entry_num, entry_date, period, je_type,
            f"{je_type.replace('_',' ').title()} - {entry_date}",
            je_type, None,
            amount, amount, "posted",
            creator, admin_id, entry_date
        ))
        je_ctr += 1

    if dry_run:
        log(f"[DRY RUN] ~{len(je_rows)} journal entries + GL postings + budgets")
        return

    n = bulk_insert("finance_journal_entries",
        ["entry_number","entry_date","period","entry_type","description",
         "reference_type","reference_id","total_debit","total_credit","status",
         "created_by_id","approved_by_id","created_at"],
        je_rows, on_conflict="ON CONFLICT (entry_number) DO NOTHING")
    ok(f"Journal entries: {n:,}")

    # GL Postings (2 baris per jurnal: debit + kredit)
    saved_jes = q("SELECT id, total_debit FROM finance_journal_entries ORDER BY id")
    for je_id, amount in saved_jes:
        acc_debit  = RNG.choice(accounts)
        acc_credit = RNG.choice(accounts)
        lid        = RNG.choice(location_ids)
        gl_rows.append((je_id, acc_debit[0],  acc_debit[1],  acc_debit[2],  amount, Decimal("0"), lid, "", datetime.now()))
        gl_rows.append((je_id, acc_credit[0], acc_credit[1], acc_credit[2], Decimal("0"), amount, lid, "", datetime.now()))

    n = bulk_insert("finance_gl_postings",
        ["journal_id","account_id","account_code","account_name",
         "debit","credit","location_id","description","created_at"],
        gl_rows, batch=3000)
    ok(f"GL postings: {n:,}")

    # Budgets
    budget_rows = []
    budget_actual_rows = []
    CATEGORIES = ["revenue","cogs","payroll","rent","utilities","marketing",
                  "maintenance","supplies","depreciation","other_opex"]

    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            for lid in location_ids:
                for cat in CATEGORIES:
                    base = Decimal(str({
                        "revenue":   RNG.randint(50000000, 200000000),
                        "cogs":      RNG.randint(15000000, 70000000),
                        "payroll":   RNG.randint(20000000, 50000000),
                        "rent":      RNG.randint(5000000,  20000000),
                        "utilities": RNG.randint(2000000,  8000000),
                        "marketing": RNG.randint(1000000,  5000000),
                        "maintenance":RNG.randint(500000,  3000000),
                        "supplies":  RNG.randint(1000000,  5000000),
                        "depreciation":RNG.randint(500000, 2000000),
                        "other_opex":RNG.randint(500000,  3000000),
                    }[cat]))
                    budget_rows.append((
                        yr, mo, lid, cat, "", base,
                        "", admin_id, datetime.now()
                    ))

    n = bulk_insert("finance_budgets",
        ["budget_year","budget_month","location_id","category","account_code",
         "budget_amount","notes","created_by_id","created_at"],
        budget_rows, batch=3000,
        on_conflict="ON CONFLICT (budget_year, budget_month, location_id, category) DO NOTHING")
    ok(f"Budgets: {n:,}")

    # Budget actuals (realisasi)
    saved_budgets = q("SELECT id, budget_amount FROM finance_budgets ORDER BY id")
    for bid, budget_amt in saved_budgets:
        actual = Decimal(str(budget_amt)) * Decimal(str(round(RNG.uniform(0.7, 1.3), 2)))
        variance = actual - Decimal(str(budget_amt))
        var_pct  = (variance / Decimal(str(budget_amt)) * 100).quantize(Decimal("0.01")) \
                   if budget_amt else Decimal("0")
        budget_actual_rows.append((
            bid, actual.quantize(Decimal("0.01")),
            variance.quantize(Decimal("0.01")),
            var_pct, today
        ))

    n = bulk_insert("finance_budget_actuals",
        ["budget_id","actual_amount","variance_amount","variance_pct","as_of_date"],
        budget_actual_rows, batch=3000,
        on_conflict="ON CONFLICT (budget_id, as_of_date) DO NOTHING")
    ok(f"Budget actuals: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 14 — MAINTENANCE (Asset Registry, Work Orders)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_maintenance(dry_run=False):
    head("MODUL 14 — MAINTENANCE (Assets, Schedules, Work Orders, Spare Parts)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS maint_asset_registry (
            id              BIGSERIAL PRIMARY KEY,
            asset_code      VARCHAR(30) UNIQUE NOT NULL,
            asset_name      VARCHAR(150) NOT NULL,
            category        VARCHAR(40) NOT NULL DEFAULT 'equipment',
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            brand           VARCHAR(80) DEFAULT '',
            model           VARCHAR(80) DEFAULT '',
            serial_number   VARCHAR(80) DEFAULT '',
            purchase_date   DATE,
            purchase_price  NUMERIC(12,2) DEFAULT 0,
            depreciation_rate NUMERIC(5,2) DEFAULT 20.0,
            current_value   NUMERIC(12,2) DEFAULT 0,
            warranty_until  DATE,
            status          VARCHAR(20) DEFAULT 'active',
            last_service_date DATE,
            next_service_date DATE,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE maint_asset_registry IS
            'Inventaris aset per outpost: mesin espresso, grinder, kulkas, POS terminal, dll.';
        CREATE INDEX IF NOT EXISTS idx_asset_loc    ON maint_asset_registry(location_id);
        CREATE INDEX IF NOT EXISTS idx_asset_status ON maint_asset_registry(status);
        """, "maint_asset_registry"),

        ("""
        CREATE TABLE IF NOT EXISTS maint_work_orders (
            id              BIGSERIAL PRIMARY KEY,
            wo_number       VARCHAR(30) UNIQUE NOT NULL,
            asset_id        BIGINT REFERENCES maint_asset_registry(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            wo_type         VARCHAR(30) DEFAULT 'corrective',
            priority        VARCHAR(10) DEFAULT 'normal',
            title           VARCHAR(200) NOT NULL,
            description     TEXT DEFAULT '',
            reported_by_id  BIGINT REFERENCES auth_user(id),
            assigned_to_id  BIGINT REFERENCES auth_user(id),
            status          VARCHAR(20) DEFAULT 'open',
            reported_at     TIMESTAMPTZ DEFAULT NOW(),
            started_at      TIMESTAMPTZ,
            completed_at    TIMESTAMPTZ,
            estimated_hours NUMERIC(5,2) DEFAULT 0,
            actual_hours    NUMERIC(5,2) DEFAULT 0,
            parts_cost      NUMERIC(10,2) DEFAULT 0,
            labor_cost      NUMERIC(10,2) DEFAULT 0,
            total_cost      NUMERIC(12,2) DEFAULT 0,
            root_cause      TEXT DEFAULT '',
            resolution      TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE maint_work_orders IS
            'Work order perawatan/perbaikan. Type: preventive, corrective, emergency.';
        CREATE INDEX IF NOT EXISTS idx_wo_status ON maint_work_orders(status);
        CREATE INDEX IF NOT EXISTS idx_wo_asset  ON maint_work_orders(asset_id);
        CREATE INDEX IF NOT EXISTS idx_wo_loc    ON maint_work_orders(location_id);
        """, "maint_work_orders"),

        ("""
        CREATE TABLE IF NOT EXISTS maint_spare_parts (
            id              BIGSERIAL PRIMARY KEY,
            part_code       VARCHAR(30) UNIQUE NOT NULL,
            part_name       VARCHAR(150) NOT NULL,
            compatible_with TEXT[] DEFAULT '{}',
            unit            VARCHAR(20) DEFAULT 'pcs',
            stock_qty       NUMERIC(10,2) DEFAULT 0,
            min_stock       NUMERIC(10,2) DEFAULT 1,
            unit_cost       NUMERIC(10,2) DEFAULT 0,
            supplier        VARCHAR(100) DEFAULT '',
            lead_time_days  INT DEFAULT 7,
            last_ordered_at DATE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE maint_spare_parts IS
            'Stok suku cadang untuk peralatan kafe: gasket, basket, blade grinder, dll.';
        """, "maint_spare_parts"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    # Assets per lokasi
    ASSETS = [
        ("espresso_machine", "Mesin Espresso",     ["La Marzocca","Synesso","Victoria Arduino"], 25000000, 50000000),
        ("grinder",          "Coffee Grinder",      ["Mahlkonig","Anfim","Eureka"],                5000000,  15000000),
        ("refrigerator",     "Kulkas Display",      ["Sharp","Samsung","Daikin"],                  4000000,  12000000),
        ("pos_terminal",     "POS Terminal",        ["Sunmi","Epson","iMin"],                      3000000,   8000000),
        ("water_purifier",   "Water Purifier",      ["Coway","3M","Panasonic"],                    2000000,   6000000),
        ("blender",          "Commercial Blender",  ["Vitamix","Blendtec"],                        3000000,   8000000),
        ("ice_maker",        "Ice Maker",           ["Hoshizaki","Ice-O-Matic"],                   8000000,  20000000),
        ("air_conditioner",  "AC",                  ["Daikin","Panasonic","Mitsubishi"],            5000000,  15000000),
    ]

    asset_rows = []
    asset_ctr  = 1
    for lid in location_ids:
        for cat, name, brands, min_price, max_price in ASSETS:
            # 1-2 unit per tipe per lokasi
            for unit in range(RNG.randint(1, 2)):
                purchase_date = today - timedelta(days=RNG.randint(30, 1800))
                purchase_price= Decimal(str(RNG.randint(min_price, max_price)))
                age_years     = (today - purchase_date).days / 365
                depr_rate     = Decimal("20.0")  # 20% per tahun
                curr_value    = max(Decimal("0"), purchase_price * (1 - depr_rate/100 * Decimal(str(age_years))))
                last_svc      = today - timedelta(days=RNG.randint(0, 90))
                next_svc      = last_svc + timedelta(days=90)
                asset_rows.append((
                    f"ASSET-{lid:03d}-{asset_ctr:04d}",
                    f"{name} #{unit+1} - Loc {lid}",
                    cat, lid,
                    RNG.choice(brands), f"Model-{RNG.randint(100,999)}",
                    f"SN{RNG.randint(100000000,999999999)}",
                    purchase_date, purchase_price.quantize(Decimal("0.01")),
                    depr_rate, curr_value.quantize(Decimal("0.01")),
                    purchase_date + timedelta(days=365*2),
                    "active", last_svc, next_svc, "",
                    purchase_date, purchase_date
                ))
                asset_ctr += 1

    log(f"Assets: {len(asset_rows)}")
    if dry_run:
        log(f"[DRY RUN] assets, work orders, spare parts")
        return

    n = bulk_insert("maint_asset_registry",
        ["asset_code","asset_name","category","location_id","brand","model",
         "serial_number","purchase_date","purchase_price","depreciation_rate",
         "current_value","warranty_until","status","last_service_date",
         "next_service_date","notes","created_at","updated_at"],
        asset_rows, on_conflict="ON CONFLICT (asset_code) DO NOTHING")
    ok(f"Assets: {n:,}")

    # Work Orders
    asset_ids = [r[0] for r in q("SELECT id, location_id FROM maint_asset_registry")]
    WO_TYPES  = ["preventive","preventive","corrective","corrective","emergency"]
    PRIORITIES= ["low","normal","normal","high","critical"]
    WO_TITLES = [
        "Servis rutin mesin espresso","Kalibrasi grinder","Pembersihan filter air",
        "AC tidak dingin","Mesin espresso bocor","Layar POS mati","Kulkas berembun",
        "Ice maker macet","Lampu display mati","Kebocoran pipa air",
    ]

    wo_rows = []
    wo_ctr  = 1
    for aid in asset_ids:
        n_wo = RNG.randint(1, 5)
        for _ in range(n_wo):
            wo_type    = RNG.choice(WO_TYPES)
            rep_date   = datetime.now() - timedelta(days=RNG.randint(0, 365))
            status     = RNG.choices(["open","in_progress","completed","completed"],
                                     weights=[15,15,35,35])[0]
            started_at = rep_date + timedelta(hours=RNG.randint(1, 24)) if status != "open" else None
            completed_at = started_at + timedelta(hours=RNG.randint(1, 72)) if status == "completed" else None
            est_h      = Decimal(str(RNG.uniform(0.5, 8)))
            act_h      = est_h * Decimal(str(RNG.uniform(0.5, 1.5))) if status == "completed" else Decimal("0")
            parts_cost = Decimal(str(RNG.randint(0, 500000)))
            labor_cost = Decimal(str(RNG.randint(50000, 300000)))
            wo_rows.append((
                f"WO-{today.year}-{wo_ctr:05d}",
                aid,
                RNG.choice(location_ids),
                wo_type, RNG.choice(PRIORITIES),
                RNG.choice(WO_TITLES), "",
                RNG.choice(user_ids) if user_ids else admin_id,
                RNG.choice(user_ids) if user_ids else admin_id,
                status, rep_date, started_at, completed_at,
                est_h.quantize(Decimal("0.01")),
                act_h.quantize(Decimal("0.01")),
                parts_cost, labor_cost,
                (parts_cost + labor_cost).quantize(Decimal("0.01")),
                "", "", rep_date
            ))
            wo_ctr += 1

    n = bulk_insert("maint_work_orders",
        ["wo_number","asset_id","location_id","wo_type","priority","title","description",
         "reported_by_id","assigned_to_id","status","reported_at","started_at","completed_at",
         "estimated_hours","actual_hours","parts_cost","labor_cost","total_cost",
         "root_cause","resolution","created_at"],
        wo_rows, on_conflict="ON CONFLICT (wo_number) DO NOTHING")
    ok(f"Work orders: {n:,}")

    # Spare Parts
    PARTS = [
        ("PART-GASKET-57MM",  "Group Gasket 57mm",    ["espresso_machine"],       "pcs", 20, 5,  15000),
        ("PART-BASKET-20G",   "Portafilter Basket 20g",["espresso_machine"],       "pcs", 10, 3,  45000),
        ("PART-BLADE-BURR",   "Burr Blade Set",        ["grinder"],                "set", 5,  2,  350000),
        ("PART-FILTER-WATER", "Filter Cartridge",      ["water_purifier"],         "pcs", 15, 5,  80000),
        ("PART-PUMP-EP",      "Pump Espresso 15bar",   ["espresso_machine"],       "pcs", 3,  1,  450000),
        ("PART-AC-FILTER",    "AC Filter Mesh",        ["air_conditioner"],        "pcs", 10, 4,  25000),
        ("PART-BLADE-ICE",    "Ice Maker Blade",       ["ice_maker"],              "pcs", 4,  2,  200000),
        ("PART-SCREEN-POS",   "POS Screen Protector",  ["pos_terminal"],           "pcs", 20, 5,  50000),
    ]
    part_rows = [(code, name, json.dumps(compat), unit,
                  RNG.randint(0, 30), min_s,
                  Decimal(str(cost)), "Toko Mesin Jakarta", 7,
                  today - timedelta(days=RNG.randint(10, 90)), datetime.now())
                 for code, name, compat, unit, _, min_s, cost in PARTS]

    n = bulk_insert("maint_spare_parts",
        ["part_code","part_name","compatible_with","unit","stock_qty","min_stock",
         "unit_cost","supplier","lead_time_days","last_ordered_at","created_at"],
        part_rows, on_conflict="ON CONFLICT (part_code) DO NOTHING")
    ok(f"Spare parts: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 15 — SUPPLY CHAIN ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

def fill_supply_chain(dry_run=False):
    head("MODUL 15 — SUPPLY CHAIN (Demand Forecast, Reorder Alerts, Supplier Scorecard)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS sc_demand_forecast (
            id              BIGSERIAL PRIMARY KEY,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            forecast_month  VARCHAR(7) NOT NULL,
            predicted_qty   NUMERIC(12,2) DEFAULT 0,
            actual_qty      NUMERIC(12,2),
            confidence_pct  NUMERIC(5,2) DEFAULT 80.0,
            method          VARCHAR(30) DEFAULT 'moving_average',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(variant_id, location_id, forecast_month)
        );
        COMMENT ON TABLE sc_demand_forecast IS
            'Prediksi kebutuhan bahan/produk per bulan. Method: moving_average, ml_model, manual.';
        CREATE INDEX IF NOT EXISTS idx_forecast_month ON sc_demand_forecast(forecast_month);
        """, "sc_demand_forecast"),

        ("""
        CREATE TABLE IF NOT EXISTS sc_reorder_alerts (
            id              BIGSERIAL PRIMARY KEY,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            current_stock   NUMERIC(12,2) DEFAULT 0,
            reorder_point   NUMERIC(12,2) DEFAULT 0,
            reorder_qty     NUMERIC(12,2) DEFAULT 0,
            days_of_stock   NUMERIC(6,2) DEFAULT 0,
            alert_level     VARCHAR(10) DEFAULT 'normal',
            suggested_po_date DATE,
            preferred_vendor_id BIGINT REFERENCES lumra_config_vendors(id),
            is_resolved     BOOLEAN DEFAULT FALSE,
            resolved_at     TIMESTAMPTZ,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sc_reorder_alerts IS
            'Alert otomatis ketika stok mendekati reorder point. Level: critical, warning, normal.';
        CREATE INDEX IF NOT EXISTS idx_reorder_alert ON sc_reorder_alerts(alert_level, is_resolved);
        """, "sc_reorder_alerts"),

        ("""
        CREATE TABLE IF NOT EXISTS sc_supplier_scorecards (
            id              BIGSERIAL PRIMARY KEY,
            vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
            period          VARCHAR(7) NOT NULL,
            on_time_delivery_pct NUMERIC(5,2) DEFAULT 0,
            quality_acceptance_pct NUMERIC(5,2) DEFAULT 0,
            price_competitiveness NUMERIC(5,2) DEFAULT 0,
            responsiveness_score  NUMERIC(5,2) DEFAULT 0,
            overall_score   NUMERIC(5,2) DEFAULT 0,
            total_orders    INT DEFAULT 0,
            total_value     NUMERIC(15,2) DEFAULT 0,
            issues_count    INT DEFAULT 0,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(vendor_id, period)
        );
        COMMENT ON TABLE sc_supplier_scorecards IS
            'Penilaian performa supplier per bulan: ketepatan delivery, kualitas, harga.';
        CREATE INDEX IF NOT EXISTS idx_scorecard_vendor ON sc_supplier_scorecards(vendor_id);
        CREATE INDEX IF NOT EXISTS idx_scorecard_period ON sc_supplier_scorecards(period DESC);
        """, "sc_supplier_scorecards"),

        ("""
        CREATE TABLE IF NOT EXISTS sc_lead_times (
            id              BIGSERIAL PRIMARY KEY,
            vendor_id       BIGINT NOT NULL REFERENCES lumra_config_vendors(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            avg_lead_days   NUMERIC(5,1) DEFAULT 0,
            min_lead_days   INT DEFAULT 0,
            max_lead_days   INT DEFAULT 0,
            sample_count    INT DEFAULT 0,
            last_updated    DATE DEFAULT CURRENT_DATE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(vendor_id, variant_id)
        );
        COMMENT ON TABLE sc_lead_times IS
            'Lead time rata-rata per vendor × produk. Basis perhitungan reorder point.';
        """, "sc_lead_times"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    variant_ids  = CTX["variant_ids"]
    location_ids = CTX["location_ids"]
    vendor_ids   = CTX["vendor_ids"]

    # Demand Forecast
    fc_rows = []
    for vid in RNG.sample(variant_ids, min(300, len(variant_ids))):
        for lid in location_ids:
            for mo_offset in range(-6, 3):
                ref = today.replace(day=1) + timedelta(days=mo_offset * 31)
                ref = ref.replace(day=1)
                period     = ref.strftime("%Y-%m")
                predicted  = Decimal(str(RNG.randint(50, 500)))
                actual     = Decimal(str(int(predicted * Decimal(str(RNG.uniform(0.7, 1.3)))))) \
                             if mo_offset < 0 else None
                confidence = Decimal(str(round(RNG.uniform(65, 95), 1)))
                method     = RNG.choice(["moving_average","moving_average","ets_model","manual"])
                fc_rows.append((
                    vid, lid, period, predicted,
                    actual, confidence, method, datetime.now()
                ))

    log(f"Demand forecasts: {len(fc_rows)}")
    if dry_run:
        log(f"[DRY RUN] forecasts, reorder alerts, scorecards, lead times")
        return

    n = bulk_insert("sc_demand_forecast",
        ["variant_id","location_id","forecast_month","predicted_qty","actual_qty",
         "confidence_pct","method","created_at"],
        fc_rows, batch=3000,
        on_conflict="ON CONFLICT (variant_id, location_id, forecast_month) DO NOTHING")
    ok(f"Demand forecasts: {n:,}")

    # Reorder Alerts (dari stock yang rendah)
    stock_data = q("""
        SELECT s.variant_id, s.location_id, s.quantity,
               COALESCE(p.min_stock, 10) AS reorder_point
        FROM lumra_config_stock s
        JOIN lumra_config_productvariants pv ON pv.id = s.variant_id
        JOIN lumra_config_products p ON p.id = pv.product_id
        WHERE s.quantity < COALESCE(p.min_stock, 10) * 2
        LIMIT 2000
    """)

    alert_rows = []
    for vid, lid, curr_stock, reorder_pt in stock_data:
        curr = Decimal(str(curr_stock or 0))
        rp   = Decimal(str(reorder_pt or 10))
        days = float(curr) / max(1, RNG.uniform(1, 10))
        level = "critical" if curr <= rp * Decimal("0.5") else \
                "warning"  if curr <= rp else "normal"
        vendor_id = RNG.choice(vendor_ids) if vendor_ids else None
        alert_rows.append((
            vid, lid, curr.quantize(Decimal("0.01")),
            rp.quantize(Decimal("0.01")),
            (rp * 3).quantize(Decimal("0.01")),
            round(days, 1), level,
            today + timedelta(days=max(0, int(days) - 3)),
            vendor_id, False, None, datetime.now()
        ))

    n = bulk_insert("sc_reorder_alerts",
        ["variant_id","location_id","current_stock","reorder_point","reorder_qty",
         "days_of_stock","alert_level","suggested_po_date","preferred_vendor_id",
         "is_resolved","resolved_at","created_at"],
        alert_rows, batch=3000)
    ok(f"Reorder alerts: {n:,}")

    # Supplier Scorecards
    sc_rows = []
    for vid in vendor_ids:
        for mo_offset in range(-12, 0):
            ref = today.replace(day=1) + timedelta(days=mo_offset * 31)
            period = ref.replace(day=1).strftime("%Y-%m")
            otd    = round(RNG.uniform(70, 99), 1)
            qual   = round(RNG.uniform(80, 100), 1)
            price  = round(RNG.uniform(60, 95), 1)
            resp   = round(RNG.uniform(70, 100), 1)
            overall= round((otd * 0.3 + qual * 0.3 + price * 0.2 + resp * 0.2), 1)
            sc_rows.append((
                vid, period, otd, qual, price, resp, overall,
                RNG.randint(5, 50),
                Decimal(str(RNG.randint(5000000, 100000000))),
                RNG.randint(0, 5), "", datetime.now()
            ))

    n = bulk_insert("sc_supplier_scorecards",
        ["vendor_id","period","on_time_delivery_pct","quality_acceptance_pct",
         "price_competitiveness","responsiveness_score","overall_score",
         "total_orders","total_value","issues_count","notes","created_at"],
        sc_rows, on_conflict="ON CONFLICT (vendor_id, period) DO NOTHING")
    ok(f"Supplier scorecards: {n:,}")

    # Lead Times
    lt_rows = []
    for vid in RNG.sample(vendor_ids, min(20, len(vendor_ids))):
        for var_id in RNG.sample(variant_ids, min(30, len(variant_ids))):
            avg_ld = round(RNG.uniform(1, 14), 1)
            lt_rows.append((
                vid, var_id, avg_ld,
                max(1, int(avg_ld - 2)),
                int(avg_ld + 3),
                RNG.randint(3, 20),
                today - timedelta(days=RNG.randint(0, 30)),
                datetime.now()
            ))

    n = bulk_insert("sc_lead_times",
        ["vendor_id","variant_id","avg_lead_days","min_lead_days","max_lead_days",
         "sample_count","last_updated","created_at"],
        lt_rows, on_conflict="ON CONFLICT (vendor_id, variant_id) DO NOTHING")
    ok(f"Lead times: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 16 — NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def fill_notifications(dry_run=False):
    head("MODUL 16 — NOTIFICATIONS (Templates, Logs, Preferences)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS notif_templates (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(40) UNIQUE NOT NULL,
            name            VARCHAR(120) NOT NULL,
            channel         VARCHAR(20) NOT NULL DEFAULT 'push',
            event_trigger   VARCHAR(60) NOT NULL,
            title_template  VARCHAR(200) NOT NULL DEFAULT '',
            body_template   TEXT NOT NULL DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE notif_templates IS
            'Template notifikasi untuk berbagai event. Channel: push, email, sms, whatsapp.';
        """, "notif_templates"),

        ("""
        CREATE TABLE IF NOT EXISTS notif_log (
            id              BIGSERIAL PRIMARY KEY,
            template_id     BIGINT REFERENCES notif_templates(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            user_id         BIGINT REFERENCES auth_user(id),
            channel         VARCHAR(20) NOT NULL DEFAULT 'push',
            recipient       VARCHAR(150) NOT NULL DEFAULT '',
            title           VARCHAR(200) DEFAULT '',
            body            TEXT DEFAULT '',
            status          VARCHAR(20) DEFAULT 'sent',
            sent_at         TIMESTAMPTZ DEFAULT NOW(),
            opened_at       TIMESTAMPTZ,
            clicked_at      TIMESTAMPTZ,
            error_message   TEXT DEFAULT ''
        );
        COMMENT ON TABLE notif_log IS
            'Log pengiriman notifikasi. Status: queued, sent, delivered, opened, failed.';
        CREATE INDEX IF NOT EXISTS idx_notif_log_cust   ON notif_log(customer_id);
        CREATE INDEX IF NOT EXISTS idx_notif_log_status ON notif_log(status);
        CREATE INDEX IF NOT EXISTS idx_notif_log_date   ON notif_log(sent_at DESC);
        """, "notif_log"),

        ("""
        CREATE TABLE IF NOT EXISTS notif_preferences (
            id              BIGSERIAL PRIMARY KEY,
            customer_id     BIGINT NOT NULL UNIQUE REFERENCES lumra_config_customers(id),
            push_enabled    BOOLEAN DEFAULT TRUE,
            email_enabled   BOOLEAN DEFAULT TRUE,
            sms_enabled     BOOLEAN DEFAULT FALSE,
            whatsapp_enabled BOOLEAN DEFAULT TRUE,
            promo_notif     BOOLEAN DEFAULT TRUE,
            order_notif     BOOLEAN DEFAULT TRUE,
            loyalty_notif   BOOLEAN DEFAULT TRUE,
            news_notif      BOOLEAN DEFAULT FALSE,
            quiet_hours_start SMALLINT DEFAULT 22,
            quiet_hours_end   SMALLINT DEFAULT 7,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE notif_preferences IS
            'Preferensi notifikasi per customer. Quiet hours = jam tidak boleh kirim notif.';
        """, "notif_preferences"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Templates
    templates_data = [
        ("ORDER_CONFIRM",   "Order Confirmation",       "push",      "order.completed",
         "Pesanan #{order_id} dikonfirmasi!",
         "Pesananmu di {location_name} sedang disiapkan. Estimasi {eta} menit. ☕"),
        ("STAMP_EARNED",    "Stamp Earned",             "push",      "stamp.earned",
         "Kamu dapat {n} stamp baru! 🎯",
         "Total stampmu sekarang {total_stamps}. Butuh {remaining} lagi untuk reward gratis!"),
        ("REWARD_READY",    "Reward Siap Diredeem",     "push",      "reward.available",
         "Reward-mu sudah bisa diredeem! 🎁",
         "Kamu punya reward '{reward_name}' yang siap digunakan. Berlaku hingga {expires}."),
        ("TIER_UPGRADE",    "Naik Tier!",               "push",      "loyalty.tier_upgrade",
         "Selamat! Kamu naik ke tier {tier_name}! 🏆",
         "Nikmati keuntungan baru: {perks}. Terima kasih sudah setia bersama Kafe Nusantara!"),
        ("BIRTHDAY",        "Happy Birthday!",          "push",      "customer.birthday",
         "Selamat Ulang Tahun! 🎂",
         "Hadiah spesial dari Kafe Nusantara: diskon 20% hari ini. Kunjungi outpost terdekat!"),
        ("PROMO_FLASH",     "Flash Promo",              "push",      "promo.flash",
         "Flash Promo hari ini! ⚡",
         "{promo_name} — hanya {duration} jam! Gunakan kode {code}. Jangan sampai kehabisan!"),
        ("NPS_SURVEY",      "Quick Survey",             "push",      "nps.survey_request",
         "Bagaimana pengalamanmu? 📋",
         "Bantu kami jadi lebih baik. Survey singkat 30 detik untuk kunjunganmu di {location}."),
        ("LOW_STOCK_WARN",  "Low Stock Alert",          "email",     "stock.low",
         "[ALERT] Stok {product_name} menipis di {location}",
         "Stok tersisa: {qty} unit. Reorder point: {reorder_pt}. Segera buat PO."),
        ("PAYROLL_SLIP",    "Slip Gaji",                "email",     "payroll.processed",
         "Slip Gaji {period} sudah tersedia",
         "Slip gaji periode {period} sudah bisa dilihat di sistem. Gaji akan ditransfer pada {pay_date}."),
        ("WO_ASSIGNED",     "Work Order Assigned",      "push",      "wo.assigned",
         "Work Order #{wo_number} ditugaskan",
         "Kamu mendapat tugas WO: {title}. Prioritas: {priority}. Cek detail di aplikasi."),
        ("BIRTHDAY_STAFF",  "Birthday Staff",           "push",      "employee.birthday",
         "Ulang Tahun {name}! 🎂",
         "Jangan lupa ucapkan selamat ulang tahun kepada {name} hari ini!"),
        ("SEASONAL_MENU",   "Menu Seasonal Baru",       "push",      "menu.seasonal_launch",
         "Menu Seasonal Baru Sudah Tersedia! 🍵",
         "Coba '{menu_name}' — racikan terbaru dari barista kami. Terbatas selama {duration}!"),
    ]
    tmpl_rows = [(code, name, channel, trigger, title, body, True, datetime.now())
                 for code, name, channel, trigger, title, body in templates_data]

    if dry_run:
        log(f"[DRY RUN] {len(tmpl_rows)} templates + notification logs + preferences")
        return

    n = bulk_insert("notif_templates",
        ["code","name","channel","event_trigger","title_template",
         "body_template","is_active","created_at"],
        tmpl_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Notification templates: {n}")

    # Notification Log
    tmpl_ids     = [r[0] for r in q("SELECT id, channel FROM notif_templates")]
    customer_ids = CTX["customer_ids"]

    notif_rows = []
    for _ in range(50000):
        tmpl = RNG.choice(tmpl_ids)
        cid  = RNG.choice(customer_ids)
        sent = datetime.now() - timedelta(days=RNG.randint(0, 365),
                                          hours=RNG.randint(0, 23))
        status  = RNG.choices(["sent","delivered","opened","failed"],
                               weights=[20, 40, 35, 5])[0]
        opened  = sent + timedelta(minutes=RNG.randint(1, 120)) \
                  if status in ("opened",) else None
        clicked = opened + timedelta(seconds=RNG.randint(5, 60)) \
                  if opened and RNG.random() < 0.4 else None
        notif_rows.append((
            tmpl, cid, None, "push",
            f"customer_{cid}@example.com",
            "Notifikasi Kafe Nusantara", "",
            status, sent, opened, clicked, ""
        ))

    n = bulk_insert("notif_log",
        ["template_id","customer_id","user_id","channel","recipient",
         "title","body","status","sent_at","opened_at","clicked_at","error_message"],
        notif_rows, batch=3000)
    ok(f"Notification logs: {n:,}")

    # Preferences
    pref_rows = []
    for cid in customer_ids:
        pref_rows.append((
            cid,
            RNG.random() < 0.9, RNG.random() < 0.7,
            RNG.random() < 0.3, RNG.random() < 0.8,
            RNG.random() < 0.8, True, True,
            RNG.random() < 0.4,
            22, 7,
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("notif_preferences",
        ["customer_id","push_enabled","email_enabled","sms_enabled","whatsapp_enabled",
         "promo_notif","order_notif","loyalty_notif","news_notif",
         "quiet_hours_start","quiet_hours_end","created_at","updated_at"],
        pref_rows,
        on_conflict="ON CONFLICT (customer_id) DO NOTHING")
    ok(f"Notification preferences: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 17 — MENU ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════

def fill_menu_engineering(dry_run=False):
    head("MODUL 17 — MENU ENGINEERING (Modifiers, Combos, Performance, A/B Tests)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS menu_modifier_groups (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            selection_type  VARCHAR(20) DEFAULT 'single',
            min_select      INT DEFAULT 0,
            max_select      INT DEFAULT 1,
            is_required     BOOLEAN DEFAULT FALSE,
            is_active       BOOLEAN DEFAULT TRUE,
            sort_order      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_modifier_groups IS
            'Grup modifikasi menu: ukuran, suhu, gula, extra shot, topping, dll.';
        """, "menu_modifier_groups"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_modifiers (
            id              BIGSERIAL PRIMARY KEY,
            group_id        BIGINT NOT NULL REFERENCES menu_modifier_groups(id),
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            price_delta     NUMERIC(10,2) DEFAULT 0,
            is_active       BOOLEAN DEFAULT TRUE,
            sort_order      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_modifiers IS
            'Opsi modifikasi: Small/Medium/Large, Hot/Iced, Less/Normal/Extra Sugar, dll.';
        """, "menu_modifiers"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_combos (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            name            VARCHAR(150) NOT NULL,
            description     TEXT DEFAULT '',
            combo_price     NUMERIC(12,2) NOT NULL,
            regular_price   NUMERIC(12,2) DEFAULT 0,
            discount_amount NUMERIC(10,2) DEFAULT 0,
            is_active       BOOLEAN DEFAULT TRUE,
            valid_from      DATE,
            valid_until     DATE,
            applicable_session VARCHAR(20) DEFAULT 'all',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_combos IS
            'Paket bundle menu: Morning Set, Afternoon Deal, dll.';
        """, "menu_combos"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_combo_items (
            id              BIGSERIAL PRIMARY KEY,
            combo_id        BIGINT NOT NULL REFERENCES menu_combos(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            quantity        INT DEFAULT 1,
            is_swappable    BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_combo_items IS 'Item-item yang masuk dalam satu paket combo.';
        """, "menu_combo_items"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_item_performance (
            id              BIGSERIAL PRIMARY KEY,
            variant_id      BIGINT NOT NULL REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            period          VARCHAR(7) NOT NULL,
            qty_sold        NUMERIC(12,2) DEFAULT 0,
            revenue         NUMERIC(15,2) DEFAULT 0,
            contribution_margin NUMERIC(15,2) DEFAULT 0,
            menu_mix_pct    NUMERIC(6,3) DEFAULT 0,
            category        VARCHAR(20) DEFAULT 'plowhorse',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(variant_id, location_id, period)
        );
        COMMENT ON TABLE menu_item_performance IS
            'Matrix menu engineering per item per bulan. '
            'Category: star (high pop + high margin), plowhorse (high pop + low margin), '
            'puzzle (low pop + high margin), dog (low pop + low margin).';
        CREATE INDEX IF NOT EXISTS idx_menu_perf_period ON menu_item_performance(period DESC);
        CREATE INDEX IF NOT EXISTS idx_menu_perf_cat    ON menu_item_performance(category);
        """, "menu_item_performance"),

        ("""
        CREATE TABLE IF NOT EXISTS menu_ab_tests (
            id              BIGSERIAL PRIMARY KEY,
            test_code       VARCHAR(30) UNIQUE NOT NULL,
            test_name       VARCHAR(150) NOT NULL,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            test_type       VARCHAR(30) DEFAULT 'price',
            control_value   JSONB NOT NULL DEFAULT '{}',
            variant_value   JSONB NOT NULL DEFAULT '{}',
            start_date      DATE NOT NULL,
            end_date        DATE,
            location_ids    BIGINT[] DEFAULT '{}',
            control_orders  INT DEFAULT 0,
            variant_orders  INT DEFAULT 0,
            control_revenue NUMERIC(15,2) DEFAULT 0,
            variant_revenue NUMERIC(15,2) DEFAULT 0,
            winner          VARCHAR(10) DEFAULT 'pending',
            status          VARCHAR(20) DEFAULT 'running',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE menu_ab_tests IS
            'A/B testing harga, nama, deskripsi menu. Winner: control, variant, inconclusive, pending.';
        """, "menu_ab_tests"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    variant_ids  = CTX["variant_ids"]
    location_ids = CTX["location_ids"]

    # Modifier Groups + Modifiers
    modifier_groups = [
        ("SIZE",       "Ukuran",       "single", 1, 1, True,  [
            ("SIZE-S",  "Small",   0),
            ("SIZE-M",  "Medium",  5000),
            ("SIZE-L",  "Large",   10000),
        ]),
        ("TEMP",       "Suhu",         "single", 1, 1, True,  [
            ("TEMP-HOT","Hot",     0),
            ("TEMP-ICE","Iced",    3000),
        ]),
        ("SUGAR",      "Tingkat Gula", "single", 0, 1, False, [
            ("SUGAR-0",  "No Sugar",     0),
            ("SUGAR-50", "Less Sweet",   0),
            ("SUGAR-100","Normal Sweet", 0),
            ("SUGAR-150","Extra Sweet",  0),
        ]),
        ("MILK",       "Jenis Susu",   "single", 0, 1, False, [
            ("MILK-REG", "Regular Milk",  0),
            ("MILK-OAT", "Oat Milk",    8000),
            ("MILK-ALM", "Almond Milk", 8000),
            ("MILK-SOY", "Soy Milk",    5000),
        ]),
        ("EXTRA",      "Tambahan",     "multi",  0, 3, False, [
            ("EXTRA-SHOT","Extra Shot", 8000),
            ("EXTRA-SYR", "Extra Syrup",3000),
            ("EXTRA-COLD","Extra Ice",  0),
            ("EXTRA-CHOC","Choco Drizzle",5000),
        ]),
        ("FOOD-TEMP",  "Kondisi",      "single", 0, 1, False, [
            ("FOOD-WARM","Dihangatkan",  0),
            ("FOOD-ROOM","Room Temp",   0),
        ]),
    ]

    mg_rows  = []
    mod_rows = []
    for code, name, sel_type, mn, mx, req, mods in modifier_groups:
        mg_rows.append((code, name, sel_type, mn, mx, req, True, len(mg_rows), datetime.now()))
        for mcode, mname, delta in mods:
            mod_rows.append((None, mcode, mname, Decimal(str(delta)), True, len(mod_rows), datetime.now()))

    if dry_run:
        log(f"[DRY RUN] modifier groups, combos, menu performance, A/B tests")
        return

    n = bulk_insert("menu_modifier_groups",
        ["code","name","selection_type","min_select","max_select",
         "is_required","is_active","sort_order","created_at"],
        mg_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Modifier groups: {n}")

    # Link modifiers ke groups
    saved_mgs = q("SELECT id, code FROM menu_modifier_groups ORDER BY id")
    mg_code_map = {row[1]: row[0] for row in saved_mgs}
    mod_rows_linked = []
    for code, name, sel_type, mn, mx, req, mods in modifier_groups:
        gid = mg_code_map.get(code)
        if not gid: continue
        for i, (mcode, mname, delta) in enumerate(mods):
            mod_rows_linked.append((gid, mcode, mname, Decimal(str(delta)), True, i, datetime.now()))

    n = bulk_insert("menu_modifiers",
        ["group_id","code","name","price_delta","is_active","sort_order","created_at"],
        mod_rows_linked, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Modifiers: {n}")

    # Combos
    SESSIONS = ["all","first_light","midday_transit","twilight_bivouac"]
    combo_rows = []
    combo_item_rows = []
    for i in range(20):
        code  = f"COMBO-{i+1:03d}"
        price = Decimal(str(RNG.randint(35000, 120000)))
        reg   = price + Decimal(str(RNG.randint(5000, 20000)))
        combo_rows.append((
            code, f"Paket Hemat #{i+1}", "",
            price, reg, reg - price, True,
            today - timedelta(days=RNG.randint(30, 180)),
            today + timedelta(days=RNG.randint(30, 180)),
            RNG.choice(SESSIONS), datetime.now()
        ))

    n = bulk_insert("menu_combos",
        ["code","name","description","combo_price","regular_price","discount_amount",
         "is_active","valid_from","valid_until","applicable_session","created_at"],
        combo_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Combos: {n}")

    # Combo Items
    saved_combos = q("SELECT id FROM menu_combos ORDER BY id")
    for (combo_id,) in saved_combos:
        n_items = RNG.randint(2, 3)
        for var_id in RNG.sample(variant_ids, min(n_items, len(variant_ids))):
            combo_item_rows.append((combo_id, var_id, 1, False, datetime.now()))
    existing_combo_items = set(q("SELECT combo_id, variant_id FROM menu_combo_items"))
    combo_item_rows = [
        row for row in combo_item_rows
        if (row[0], row[1]) not in existing_combo_items
    ]

    n = bulk_insert("menu_combo_items",
        ["combo_id","variant_id","quantity","is_swappable","created_at"],
        combo_item_rows)
    ok(f"Combo items: {n}")

    # Menu Item Performance (matrix engineering)
    me_rows = []
    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            if date(yr, mo, 1) > today: break
            period = f"{yr}-{mo:02d}"
            for vid in RNG.sample(variant_ids, min(50, len(variant_ids))):
                for lid in location_ids:
                    qty     = Decimal(str(RNG.randint(10, 500)))
                    price   = Decimal(str(RNG.randint(20000, 80000)))
                    cogs    = price * Decimal(str(round(RNG.uniform(0.25, 0.50), 2)))
                    rev     = qty * price
                    contrib = qty * (price - cogs)
                    mix_pct = round(RNG.uniform(0.001, 0.15), 3)
                    # Matrix: star/plowhorse/puzzle/dog
                    high_pop = mix_pct > 0.05
                    high_mg  = (price - cogs) / price > Decimal("0.55")
                    cat = ("star" if high_pop and high_mg else
                           "plowhorse" if high_pop else
                           "puzzle" if high_mg else "dog")
                    me_rows.append((
                        vid, lid, period, qty, rev.quantize(Decimal("0.01")),
                        contrib.quantize(Decimal("0.01")), mix_pct, cat, datetime.now()
                    ))

    n = bulk_insert("menu_item_performance",
        ["variant_id","location_id","period","qty_sold","revenue",
         "contribution_margin","menu_mix_pct","category","created_at"],
        me_rows, batch=3000,
        on_conflict="ON CONFLICT (variant_id, location_id, period) DO NOTHING")
    ok(f"Menu performance: {n:,}")

    # A/B Tests
    ab_rows = []
    for i in range(15):
        vid = RNG.choice(variant_ids)
        test_type = RNG.choice(["price","name","description","image"])
        old_price  = RNG.randint(25000, 80000)
        new_price  = old_price + RNG.randint(-5000, 10000)
        start = today - timedelta(days=RNG.randint(14, 90))
        end   = start + timedelta(days=RNG.randint(14, 30))
        status= "completed" if end < today else "running"
        ctrl_ord = RNG.randint(100, 1000)
        var_ord  = RNG.randint(80, 1100)
        winner = ("variant" if var_ord > ctrl_ord * 1.05 else
                  "control" if ctrl_ord > var_ord * 1.05 else
                  "inconclusive") if status == "completed" else "pending"
        ab_rows.append((
            f"AB-{i+1:03d}", f"A/B Test #{i+1} - {test_type.title()}",
            vid, test_type,
            json.dumps({"price": old_price}),
            json.dumps({"price": new_price}),
            start, end,
            [RNG.choice(location_ids) for _ in range(RNG.randint(1, 3))],
            ctrl_ord, var_ord,
            Decimal(str(ctrl_ord * old_price)),
            Decimal(str(var_ord * new_price)),
            winner, status, "", datetime.now()
        ))

    n = bulk_insert("menu_ab_tests",
        ["test_code","test_name","variant_id","test_type","control_value","variant_value",
         "start_date","end_date","location_ids","control_orders","variant_orders",
         "control_revenue","variant_revenue","winner","status","notes","created_at"],
        ab_rows, on_conflict="ON CONFLICT (test_code) DO NOTHING")
    ok(f"A/B Tests: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 18 — WASTE & COSTING
# ═══════════════════════════════════════════════════════════════════════════════

def fill_waste_costing(dry_run=False):
    head("MODUL 18 — WASTE & COSTING (Categories, Logs, Cost Summary, Root Cause)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS waste_categories (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(80) NOT NULL,
            waste_type      VARCHAR(30) DEFAULT 'production',
            description     TEXT DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE waste_categories IS
            'Kategori waste: spoilage, over_production, spill, expired, trim.';
        """, "waste_categories"),

        ("""
        CREATE TABLE IF NOT EXISTS waste_logs (
            id              BIGSERIAL PRIMARY KEY,
            category_id     BIGINT NOT NULL REFERENCES waste_categories(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
            waste_date      DATE NOT NULL,
            shift_type      VARCHAR(20) DEFAULT 'first_light',
            quantity        NUMERIC(10,3) NOT NULL,
            unit            VARCHAR(20) DEFAULT 'gram',
            unit_cost       NUMERIC(10,2) DEFAULT 0,
            total_cost      NUMERIC(12,2) DEFAULT 0,
            root_cause_tag  VARCHAR(50) DEFAULT '',
            description     TEXT DEFAULT '',
            recorded_by_id  BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE waste_logs IS
            'Log waste harian per shift. Diisi oleh supervisor shift.';
        CREATE INDEX IF NOT EXISTS idx_waste_date ON waste_logs(waste_date DESC);
        CREATE INDEX IF NOT EXISTS idx_waste_loc  ON waste_logs(location_id);
        CREATE INDEX IF NOT EXISTS idx_waste_cat  ON waste_logs(category_id);
        """, "waste_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS waste_daily_summary (
            id              BIGSERIAL PRIMARY KEY,
            summary_date    DATE NOT NULL,
            location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
            total_waste_qty NUMERIC(12,3) DEFAULT 0,
            total_waste_cost NUMERIC(12,2) DEFAULT 0,
            waste_pct_of_cogs NUMERIC(6,3) DEFAULT 0,
            top_category    VARCHAR(20) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(summary_date, location_id)
        );
        COMMENT ON TABLE waste_daily_summary IS
            'Ringkasan waste harian per outpost. Benchmark: waste < 3%% dari COGS.';
        CREATE INDEX IF NOT EXISTS idx_waste_sum_date ON waste_daily_summary(summary_date DESC);
        """, "waste_daily_summary"),

        ("""
        CREATE TABLE IF NOT EXISTS waste_root_cause_analysis (
            id              BIGSERIAL PRIMARY KEY,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            period          VARCHAR(7) NOT NULL,
            primary_cause   VARCHAR(80) NOT NULL,
            occurrence_count INT DEFAULT 0,
            total_cost_impact NUMERIC(12,2) DEFAULT 0,
            corrective_action TEXT DEFAULT '',
            status          VARCHAR(20) DEFAULT 'open',
            due_date        DATE,
            closed_at       DATE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE waste_root_cause_analysis IS
            'Analisis akar penyebab waste per periode lokasi. Action plan dan tracking.';
        """, "waste_root_cause_analysis"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    variant_ids  = CTX["variant_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]
    min_date     = CTX["min_date"]

    # Categories
    cat_data = [
        ("SPOILAGE",    "Spoilage/Busuk",      "storage",    "Bahan baku yang busuk sebelum dipakai."),
        ("OVER_PROD",   "Over Production",     "production", "Produksi berlebih yang tidak terjual."),
        ("SPILL",       "Spill/Tumpah",        "handling",   "Minuman/bahan yang tumpah saat penyiapan."),
        ("EXPIRED",     "Expired",             "storage",    "Produk melewati batas kadaluarsa."),
        ("TRIM",        "Trim/Sisa Potong",    "production", "Sisa bahan dari proses portioning."),
        ("RETURN",      "Customer Return",     "service",    "Produk yang dikembalikan customer."),
        ("QC_REJECT",   "QC Reject",           "quality",    "Produk tidak lolos quality check internal."),
        ("TRIAL_BATCH", "Trial/Recipe Test",   "production", "Bahan untuk uji coba resep baru."),
    ]
    cat_rows = [(code, name, wtype, desc, True, datetime.now())
                for code, name, wtype, desc in cat_data]

    if dry_run:
        log(f"[DRY RUN] waste categories, logs, summaries, RCA")
        return

    n = bulk_insert("waste_categories",
        ["code","name","waste_type","description","is_active","created_at"],
        cat_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Waste categories: {n}")

    # Waste Logs
    cat_ids    = [r[0] for r in q("SELECT id FROM waste_categories ORDER BY id")]
    SHIFTS     = ["first_light","midday_transit","twilight_bivouac"]
    ROOT_CAUSES= ["improper_storage","over_ordering","skill_gap","equipment_failure",
                  "expired_ingredient","customer_complaint","recipe_error","spill_accident"]
    UNITS      = ["gram","ml","pcs","liter","kg"]

    waste_rows = []
    days_range = (today - min_date).days
    for _ in range(20000):
        waste_date = min_date + timedelta(days=RNG.randint(0, days_range))
        qty   = Decimal(str(round(RNG.uniform(10, 500), 1)))
        cost  = Decimal(str(RNG.randint(500, 50000)))
        waste_rows.append((
            RNG.choice(cat_ids),
            RNG.choice(variant_ids),
            RNG.choice(location_ids),
            waste_date, RNG.choice(SHIFTS),
            qty, RNG.choice(UNITS),
            cost, qty * cost / 1000,
            RNG.choice(ROOT_CAUSES), "",
            RNG.choice(user_ids) if user_ids else admin_id,
            datetime.combine(waste_date, dtime(RNG.randint(7,22), 0))
        ))

    n = bulk_insert("waste_logs",
        ["category_id","variant_id","location_id","waste_date","shift_type",
         "quantity","unit","unit_cost","total_cost","root_cause_tag","description",
         "recorded_by_id","created_at"],
        waste_rows, batch=3000)
    ok(f"Waste logs: {n:,}")

    # Daily Summary (aggregate dari waste_logs per date × location)
    summary_raw = q("""
        SELECT waste_date, location_id,
               SUM(quantity) AS qty,
               SUM(total_cost) AS cost
        FROM waste_logs
        GROUP BY waste_date, location_id
        ORDER BY waste_date
        LIMIT 50000
    """)

    # COGS dari sales_daily
    cogs_map = {}
    try:
        cogs_raw = q("SELECT report_date, COALESCE(total_revenue * 0.35, 0) FROM lumra_report_sales_daily")
        cogs_map = {r[0]: Decimal(str(r[1])) for r in cogs_raw}
    except: pass

    TOP_CATS = ["SPOILAGE","OVER_PROD","SPILL","EXPIRED"]
    sum_rows = []
    for waste_date, loc_id, qty, cost in summary_raw:
        cogs     = cogs_map.get(waste_date, Decimal("1000000"))
        waste_pct= (Decimal(str(cost)) / cogs * 100).quantize(Decimal("0.001")) \
                   if cogs > 0 else Decimal("0")
        sum_rows.append((
            waste_date, loc_id,
            Decimal(str(qty)).quantize(Decimal("0.001")),
            Decimal(str(cost)).quantize(Decimal("0.01")),
            waste_pct, RNG.choice(TOP_CATS), datetime.now()
        ))

    n = bulk_insert("waste_daily_summary",
        ["summary_date","location_id","total_waste_qty","total_waste_cost",
         "waste_pct_of_cogs","top_category","created_at"],
        sum_rows, batch=3000,
        on_conflict="ON CONFLICT (summary_date, location_id) DO NOTHING")
    ok(f"Waste daily summary: {n:,}")

    # Root Cause Analysis
    rca_rows = []
    ACTIONS = [
        "Review SOP penyimpanan bahan baku.",
        "Implementasi FIFO ketat untuk semua bahan.",
        "Training barista teknik portioning yang benar.",
        "Kalibrasi equipment setiap awal shift.",
        "Review par level dan reduce ordering quantity.",
        "Pasang checklist suhu kulkas harian.",
    ]
    for yr in range(today.year - 1, today.year + 1):
        for mo in range(1, 13):
            if date(yr, mo, 1) > today: break
            period = f"{yr}-{mo:02d}"
            for lid in RNG.sample(location_ids, min(3, len(location_ids))):
                for cause in RNG.sample(ROOT_CAUSES, min(3, len(ROOT_CAUSES))):
                    due = date(yr, mo, 1) + timedelta(days=30)
                    status = "closed" if due < today else "open"
                    rca_rows.append((
                        lid, period, cause,
                        RNG.randint(3, 30),
                        Decimal(str(RNG.randint(50000, 2000000))),
                        RNG.choice(ACTIONS),
                        status, due,
                        due if status == "closed" else None,
                        datetime.now()
                    ))

    n = bulk_insert("waste_root_cause_analysis",
        ["location_id","period","primary_cause","occurrence_count","total_cost_impact",
         "corrective_action","status","due_date","closed_at","created_at"],
        rca_rows)
    ok(f"Root cause analysis: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 19 — TRAINING & CERTIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def fill_training(dry_run=False):
    head("MODUL 19 — TRAINING (Courses, Enrollments, Assessments, Certifications)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS training_courses (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            title           VARCHAR(150) NOT NULL,
            description     TEXT DEFAULT '',
            category        VARCHAR(40) DEFAULT 'operations',
            level           VARCHAR(20) DEFAULT 'beginner',
            duration_hours  NUMERIC(5,1) DEFAULT 0,
            passing_score   SMALLINT DEFAULT 70,
            is_mandatory    BOOLEAN DEFAULT FALSE,
            valid_for_months INT DEFAULT 12,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE training_courses IS
            'Kursus pelatihan karyawan: barista skill, service excellence, food safety, leadership.';
        """, "training_courses"),

        ("""
        CREATE TABLE IF NOT EXISTS training_enrollments (
            id              BIGSERIAL PRIMARY KEY,
            course_id       BIGINT NOT NULL REFERENCES training_courses(id),
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            status          VARCHAR(20) DEFAULT 'enrolled',
            enrolled_at     TIMESTAMPTZ DEFAULT NOW(),
            started_at      TIMESTAMPTZ,
            completed_at    TIMESTAMPTZ,
            score           NUMERIC(5,2),
            passed          BOOLEAN,
            attempt_number  INT DEFAULT 1,
            notes           TEXT DEFAULT '',
            UNIQUE(course_id, employee_id, attempt_number)
        );
        COMMENT ON TABLE training_enrollments IS
            'Enrollment karyawan ke kursus. Bisa multi-attempt jika tidak lulus.';
        CREATE INDEX IF NOT EXISTS idx_enroll_emp    ON training_enrollments(employee_id);
        CREATE INDEX IF NOT EXISTS idx_enroll_status ON training_enrollments(status);
        """, "training_enrollments"),

        ("""
        CREATE TABLE IF NOT EXISTS training_certifications (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            course_id       BIGINT NOT NULL REFERENCES training_courses(id),
            cert_number     VARCHAR(50) UNIQUE NOT NULL,
            issued_date     DATE NOT NULL,
            expiry_date     DATE,
            is_valid        BOOLEAN DEFAULT TRUE,
            issued_by       VARCHAR(100) DEFAULT 'Kafe Nusantara Training Center',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE training_certifications IS
            'Sertifikasi karyawan yang lulus training. Auto-expire sesuai valid_for_months kursus.';
        CREATE INDEX IF NOT EXISTS idx_cert_emp ON training_certifications(employee_id);
        CREATE INDEX IF NOT EXISTS idx_cert_exp ON training_certifications(expiry_date);
        """, "training_certifications"),

        ("""
        CREATE TABLE IF NOT EXISTS training_skill_matrix (
            id              BIGSERIAL PRIMARY KEY,
            employee_id     BIGINT NOT NULL REFERENCES hr_employees(id),
            skill_name      VARCHAR(80) NOT NULL,
            skill_category  VARCHAR(40) DEFAULT 'technical',
            proficiency     SMALLINT DEFAULT 1 CHECK(proficiency BETWEEN 1 AND 5),
            assessed_at     DATE DEFAULT CURRENT_DATE,
            assessed_by_id  BIGINT REFERENCES hr_employees(id),
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(employee_id, skill_name)
        );
        COMMENT ON TABLE training_skill_matrix IS
            'Matriks skill per karyawan. Proficiency 1-5: 1=novice, 3=competent, 5=expert.';
        CREATE INDEX IF NOT EXISTS idx_skill_emp ON training_skill_matrix(employee_id);
        """, "training_skill_matrix"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Courses
    courses_data = [
        ("BARI-101",  "Espresso Fundamentals",           "barista",   "beginner",  8,  70,  True,  12),
        ("BARI-201",  "Manual Brewing Techniques",       "barista",   "intermediate",12,75, False, 12),
        ("BARI-301",  "Latte Art & Coffee Aesthetics",   "barista",   "intermediate",10,75, False, 12),
        ("BARI-401",  "Single Origin & Cupping",         "barista",   "advanced",  16, 80,  False, 24),
        ("SVC-101",   "Customer Service Excellence",     "service",   "beginner",  6,  75,  True,  12),
        ("SVC-201",   "Conflict Resolution",             "service",   "intermediate",4, 70, False, 12),
        ("FOOD-101",  "Food Safety & Hygiene (HACCP)",   "food_safety","beginner",  8,  80,  True,  6),
        ("FOOD-201",  "Allergen Awareness",              "food_safety","beginner",  4,  80,  True,  12),
        ("OPS-101",   "POS System & Cash Handling",      "operations","beginner",  6,  75,  True,  12),
        ("OPS-201",   "Inventory Management",            "operations","intermediate",8,70,  False, 12),
        ("OPS-301",   "Shift Management",                "operations","advanced",  12, 75,  False, 12),
        ("MGMT-101",  "Leadership Essentials",           "management","intermediate",16,75, False, 24),
        ("MGMT-201",  "Financial Literacy for Managers", "management","advanced",  12, 75,  False, 24),
        ("RECIPE-101","Signature Recipe Mastery",        "barista",   "intermediate",8, 80, True,  12),
        ("SAFE-101",  "Fire Safety & Emergency Proc.",   "safety",    "beginner",  4,  80,  True,  12),
    ]
    course_rows = [(code, title, "", cat, lvl,
                    Decimal(str(dur)), passing, mandatory, valid, True, datetime.now())
                   for code, title, cat, lvl, dur, passing, mandatory, valid in courses_data]

    if dry_run:
        log(f"[DRY RUN] courses, enrollments, certifications, skill matrix")
        return

    n = bulk_insert("training_courses",
        ["code","title","description","category","level","duration_hours",
         "passing_score","is_mandatory","valid_for_months","is_active","created_at"],
        course_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Courses: {n}")

    # Enrollments + Certifications
    course_data  = q("SELECT id, passing_score, valid_for_months FROM training_courses ORDER BY id")
    employee_ids = [r[0] for r in q("SELECT id FROM hr_employees ORDER BY id")]

    if not employee_ids or not course_data:
        warn("Tidak ada employee atau course — skip enrollment")
        return

    enroll_rows = []
    cert_rows   = []
    cert_ctr    = 1

    for emp_id in employee_ids:
        # Setiap karyawan ambil 3-8 kursus
        sampled_courses = RNG.sample(course_data, min(RNG.randint(3, 8), len(course_data)))
        for cid, passing_score, valid_months in sampled_courses:
            status = RNG.choices(
                ["completed","completed","in_progress","enrolled","failed"],
                weights=[50, 0, 20, 20, 10]
            )[0]
            enrolled_at  = datetime.now() - timedelta(days=RNG.randint(30, 730))
            started_at   = enrolled_at + timedelta(days=RNG.randint(0, 14)) \
                           if status != "enrolled" else None
            completed_at = started_at + timedelta(days=RNG.randint(1, 30)) \
                           if status in ("completed","failed") else None
            score = Decimal(str(round(RNG.uniform(50, 100), 1))) \
                    if status in ("completed","failed") else None
            passed = bool(score >= passing_score) if score else None

            enroll_rows.append((
                cid, emp_id, status,
                enrolled_at, started_at, completed_at,
                score, passed, 1, "", 
            ))

            if passed:
                issued = completed_at.date() if completed_at else today
                expiry = issued + timedelta(days=valid_months * 30)
                cert_rows.append((
                    emp_id, cid,
                    f"CERT-{emp_id:05d}-{cid:03d}-{cert_ctr:04d}",
                    issued, expiry, expiry >= today,
                    "Kafe Nusantara Training Center",
                    datetime.now()
                ))
                cert_ctr += 1

    n = bulk_insert("training_enrollments",
        ["course_id","employee_id","status","enrolled_at","started_at","completed_at",
         "score","passed","attempt_number","notes"],
        enroll_rows,
        on_conflict="ON CONFLICT (course_id, employee_id, attempt_number) DO NOTHING")
    ok(f"Enrollments: {n:,}")

    n = bulk_insert("training_certifications",
        ["employee_id","course_id","cert_number","issued_date","expiry_date",
         "is_valid","issued_by","created_at"],
        cert_rows, on_conflict="ON CONFLICT (cert_number) DO NOTHING")
    ok(f"Certifications: {n:,}")

    # Skill Matrix
    SKILLS = {
        "technical": ["Espresso Extraction","Milk Steaming","Manual Brewing","Latte Art",
                       "Coffee Cupping","Grinder Calibration","POS Operation","Inventory Count"],
        "service":   ["Customer Greeting","Order Taking","Complaint Handling","Upselling",
                       "Product Knowledge","Table Service"],
        "food_safety":["HACCP","Allergen Awareness","Temperature Control","Personal Hygiene"],
        "leadership":["Shift Briefing","Team Communication","Conflict Resolution","Performance Feedback"],
    }

    skill_rows = []
    for emp_id in employee_ids:
        for cat, skill_list in SKILLS.items():
            for skill in RNG.sample(skill_list, min(RNG.randint(2, 5), len(skill_list))):
                skill_rows.append((
                    emp_id, skill, cat,
                    RNG.randint(1, 5),
                    today - timedelta(days=RNG.randint(0, 365)),
                    None, "", datetime.now()
                ))

    n = bulk_insert("training_skill_matrix",
        ["employee_id","skill_name","skill_category","proficiency","assessed_at",
         "assessed_by_id","notes","created_at"],
        skill_rows,
        on_conflict="ON CONFLICT (employee_id, skill_name) DO UPDATE SET "
                    "proficiency=EXCLUDED.proficiency, assessed_at=EXCLUDED.assessed_at")
    ok(f"Skill matrix: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "hr":               fill_hr,
    "loyalty":          fill_loyalty,
    "customer_journey": fill_customer_journey,
    "finance_gl":       fill_finance_gl,
    "maintenance":      fill_maintenance,
    "supply_chain":     fill_supply_chain,
    "notifications":    fill_notifications,
    "menu_engineering": fill_menu_engineering,
    "waste_costing":    fill_waste_costing,
    "training":         fill_training,
}

ORDER = ["hr","loyalty","customer_journey","finance_gl","maintenance",
         "supply_chain","notifications","menu_engineering","waste_costing","training"]

NEW_TABLES = [
    # HR
    "hr_employees", "hr_work_schedules", "hr_attendance", "hr_payroll",
    # Loyalty
    "loyalty_tiers", "loyalty_stamp_cards", "loyalty_stamp_transactions",
    "loyalty_rewards", "loyalty_redemptions",
    # Customer Journey
    "cj_customer_sessions", "cj_touchpoints", "cj_feedback", "cj_nps_responses",
    # Finance GL
    "finance_journal_entries", "finance_gl_postings", "finance_budgets",
    "finance_budget_actuals", "finance_cost_centers",
    # Maintenance
    "maint_asset_registry", "maint_work_orders", "maint_spare_parts",
    # Supply Chain
    "sc_demand_forecast", "sc_reorder_alerts", "sc_supplier_scorecards", "sc_lead_times",
    # Notifications
    "notif_templates", "notif_log", "notif_preferences",
    # Menu Engineering
    "menu_modifier_groups", "menu_modifiers", "menu_combos", "menu_combo_items",
    "menu_item_performance", "menu_ab_tests",
    # Waste
    "waste_categories", "waste_logs", "waste_daily_summary", "waste_root_cause_analysis",
    # Training
    "training_courses", "training_enrollments", "training_certifications", "training_skill_matrix",
]

def main():
    t_total = time.time()
    print("\n" + "═"*70)
    print("  KAFE NUSANTARA — World Building Extension (seed_expansion2)")
    print("  10 modul baru: HR, Loyalty, CJ, Finance GL, Maintenance,")
    print("  Supply Chain, Notifications, Menu Engineering, Waste, Training")
    print("═"*70)
    print(f"  Mode    : {'DRY RUN' if DRY_RUN else 'EXECUTE'}")
    print(f"  Section : {SECTION}")

    load_context()

    to_run  = ORDER if SECTION == "all" else [SECTION]
    results = {}

    for sec in to_run:
        fn = SECTION_MAP.get(sec)
        if not fn:
            warn(f"Section '{sec}' tidak dikenal.")
            continue
        try:
            fn(dry_run=DRY_RUN)
            results[sec] = "OK"
        except Exception as e:
            import traceback
            warn(f"ERROR di {sec}: {e}")
            traceback.print_exc()
            results[sec] = f"ERROR: {e}"

    elapsed = time.time() - t_total
    print("\n" + "═"*70)
    print(f"  SELESAI dalam {elapsed:.1f}s")
    print("─"*70)
    for sec, res in results.items():
        icon = "✓" if res == "OK" else "✗"
        print(f"  {icon} {sec:<22} {res}")
    print("═"*70)

    if DRY_RUN:
        print("\n  Jalankan dengan --execute untuk menyimpan ke DB\n")

    print(f"\n  {'Tabel':<45} {'Rows':>12}")
    print("─"*60)
    for t in NEW_TABLES:
        cnt     = row_count(t) if not DRY_RUN else "—"
        cnt_str = f"{cnt:,}" if isinstance(cnt, int) and cnt >= 0 else str(cnt)
        print(f"  {t:<45} {cnt_str:>12}")
    print()


try:
    from django.core.management.base import BaseCommand
    class Command(BaseCommand):
        help = "Kafe Nusantara — World Building Extension (10 modul baru)"
        def add_arguments(self, p):
            p.add_argument("--execute", action="store_true", default=False)
            p.add_argument("--section", default="all")
        def handle(self, *args, **opts):
            global DRY_RUN, SECTION
            DRY_RUN = not opts["execute"]
            SECTION = opts["section"]
            main()
except ImportError:
    pass

if __name__ == "__main__":
    main()

seed 3
"""
seed_expansion3.py
==================
KAFE NUSANTARA — World Building Phase 3
Ekspansi database tahap 3: domain yang belum ter-cover dari stack lengkap.

Stack yang di-leverage:
  Celery/Redis  → task_queue, celery_scheduled_jobs, background_job_logs
  Meilisearch   → search_index_config, search_query_logs, search_synonyms
  WeasyPrint    → report_templates, generated_reports, report_schedules
  DRF           → api_keys, api_rate_limits, api_usage_logs, webhooks
  Sentry        → error_tracking_summary, performance_snapshots
  django-axes   → login_attempts (extend), security_events
  Celery Beat   → extended job configs

MODUL BARU (10 modul):
  20. task_queue      — celery tasks, job logs, dead letter queue
  21. search          — Meilisearch index config, query logs, synonyms, analytics
  22. reporting       — report templates, schedules, generated reports, delivery logs
  23. api_gateway     — API keys, rate limits, usage logs, webhook configs
  24. security        — login events, security alerts, ip_whitelist, device_registry
  25. recipe_mgmt     — recipes v2, recipe_versions, costing, yield_tests
  26. events_calendar — events, event_registrations, event_revenue
  27. customer_support— tickets, ticket_messages, sla_configs, escalations
  28. analytics_cube  — pre-aggregated OLAP cubes: hourly, cohort, funnel
  29. config_store    — feature_flags, app_configs, location_configs, changelog

Cara pakai:
  python manage.py seed_expansion3 --execute
  python manage.py seed_expansion3 --execute --section=task_queue
  python manage.py seed_expansion3 --list-sections
"""

import os, sys, random, time, json, hashlib, uuid
from decimal import Decimal
from datetime import date, datetime, timedelta, time as dtime

for _s in ("stdout", "stderr"):
    _o = getattr(sys, _s, None)
    if hasattr(_o, "reconfigure"):
        try: _o.reconfigure(encoding="utf-8", errors="replace")
        except: pass

# ── Args ──────────────────────────────────────────────────────────────────────
DRY_RUN = "--execute" not in sys.argv
SECTION = "all"
for i, a in enumerate(sys.argv[1:], 1):
    if a == "--section" and i < len(sys.argv): SECTION = sys.argv[i]
    elif a.startswith("--section="): SECTION = a.split("=", 1)[1]

if "--list-sections" in sys.argv:
    print("Sections: task_queue search reporting api_gateway security "
          "recipe_mgmt events_calendar customer_support analytics_cube config_store all")
    sys.exit(0)

RNG = random.Random(777)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumra_config.settings")
import django; django.setup()
from django.db import connection

# ── Utilities ─────────────────────────────────────────────────────────────────
def log(msg):  print(f"  {msg}", flush=True)
def ok(msg):   print(f"  ✓ {msg}", flush=True)
def warn(msg): print(f"  ⚠ {msg}", flush=True)
def head(msg):
    print(f"\n{'▓'*60}\n  {msg}\n{'▓'*60}")

def q(sql, params=None):
    with connection.cursor() as cur:
        cur.execute(sql, params) if params else cur.execute(sql)
        return cur.fetchall()

def q1(sql, params=None):
    rows = q(sql, params)
    return rows[0][0] if rows else None

def table_exists(name):
    return q1("SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s", [name]) > 0

def row_count(name):
    try: return q1(f"SELECT COUNT(*) FROM {name}")
    except: return -1

def execute_sql(sql, label=""):
    try:
        with connection.cursor() as cur:
            cur.execute(sql)
        if label: ok(label)
        return True
    except Exception as e:
        warn(f"{label}: {e}")
        return False

def bulk_insert(table, columns, rows, batch=2000, on_conflict="ON CONFLICT DO NOTHING"):
    if not rows: return 0
    cols = ", ".join(columns)
    ph   = ", ".join(["%s"] * len(columns))
    sql  = f"INSERT INTO {table} ({cols}) VALUES ({ph}) {on_conflict}"
    total = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i:i+batch]
        try:
            with connection.cursor() as cur:
                cur.executemany(sql, chunk)
                total += cur.rowcount if cur.rowcount >= 0 else len(chunk)
        except Exception as e:
            warn(f"Batch {i//batch+1} [{table}]: {e}")
            for row in chunk:
                try:
                    with connection.cursor() as cur:
                        cur.execute(sql, row)
                        total += 1
                except: pass
    return total

def rand_hex(n=32):
    return hashlib.sha256(str(RNG.random()).encode()).hexdigest()[:n]

def rand_uuid():
    return str(uuid.UUID(int=RNG.getrandbits(128)))

# ── Context ───────────────────────────────────────────────────────────────────
CTX = {}
def load_context():
    log("Loading context...")
    CTX["admin_id"]     = q1("SELECT id FROM auth_user WHERE is_superuser=true ORDER BY id LIMIT 1") \
                          or q1("SELECT id FROM auth_user ORDER BY id LIMIT 1")
    CTX["user_ids"]     = [r[0] for r in q("SELECT id FROM auth_user WHERE is_active=true ORDER BY id LIMIT 200")]
    CTX["location_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_locations ORDER BY id")]
    CTX["vendor_ids"]   = [r[0] for r in q("SELECT id FROM lumra_config_vendors ORDER BY id")]
    CTX["customer_ids"] = [r[0] for r in q("SELECT id FROM lumra_config_customers WHERE is_active=true ORDER BY id LIMIT 5000")]
    CTX["variant_ids"]  = [r[0] for r in q("SELECT id FROM lumra_config_productvariants ORDER BY id LIMIT 2000")]
    CTX["order_ids"]    = [r[0] for r in q("SELECT id FROM lumra_config_orders WHERE status='completed' ORDER BY id LIMIT 50000")]
    CTX["min_date"]     = q1("SELECT MIN(created_at)::date FROM lumra_config_orders") or date(2023, 1, 1)
    CTX["max_date"]     = q1("SELECT MAX(created_at)::date FROM lumra_config_orders") or date.today()
    # From expansion2 if available
    CTX["employee_ids"] = [r[0] for r in q("SELECT id FROM hr_employees ORDER BY id")] \
                          if table_exists("hr_employees") else []
    CTX["variant_names"]= {r[0]: r[1] for r in q("SELECT id, name FROM lumra_config_productvariants ORDER BY id LIMIT 2000")} \
                          if True else {}
    ok(f"Context: {len(CTX['location_ids'])} locs, {len(CTX['customer_ids'])} customers, "
       f"{len(CTX['order_ids'])} orders, {len(CTX['employee_ids'])} employees")

today = date.today()

# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 20 — TASK QUEUE (Celery + Redis)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_task_queue(dry_run=False):
    head("MODUL 20 — TASK QUEUE (Celery Jobs, Scheduled Tasks, Dead Letter Queue)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS tq_task_definitions (
            id              BIGSERIAL PRIMARY KEY,
            task_name       VARCHAR(120) UNIQUE NOT NULL,
            task_path       VARCHAR(255) NOT NULL,
            description     TEXT DEFAULT '',
            category        VARCHAR(40) DEFAULT 'general',
            default_queue   VARCHAR(50) DEFAULT 'default',
            priority        SMALLINT DEFAULT 5,
            max_retries     SMALLINT DEFAULT 3,
            retry_backoff    INT DEFAULT 60,
            timeout_seconds  INT DEFAULT 300,
            is_scheduled    BOOLEAN DEFAULT FALSE,
            cron_expression VARCHAR(50) DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_task_definitions IS
            'Definisi semua Celery task. Termasuk scheduled tasks (beat).
            Category: reporting, sync, notification, cleanup, analytics, procurement.';
        """, "tq_task_definitions"),

        ("""
        CREATE TABLE IF NOT EXISTS tq_job_logs (
            id              BIGSERIAL PRIMARY KEY,
            task_id         VARCHAR(36) NOT NULL,
            task_name       VARCHAR(120) NOT NULL,
            queue           VARCHAR(50) DEFAULT 'default',
            status          VARCHAR(20) DEFAULT 'pending',
            args_summary    TEXT DEFAULT '',
            kwargs_summary  TEXT DEFAULT '',
            triggered_by    VARCHAR(50) DEFAULT 'schedule',
            triggered_by_id BIGINT,
            worker_name     VARCHAR(100) DEFAULT '',
            started_at      TIMESTAMPTZ,
            completed_at    TIMESTAMPTZ,
            duration_ms     INT,
            result_summary  TEXT DEFAULT '',
            error_message   TEXT DEFAULT '',
            retry_count     SMALLINT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_job_logs IS
            'Log eksekusi setiap Celery task. Untuk monitoring dan debugging.';
        CREATE INDEX IF NOT EXISTS idx_tq_status    ON tq_job_logs(status);
        CREATE INDEX IF NOT EXISTS idx_tq_task_name ON tq_job_logs(task_name);
        CREATE INDEX IF NOT EXISTS idx_tq_created   ON tq_job_logs(created_at DESC);
        """, "tq_job_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS tq_dead_letter_queue (
            id              BIGSERIAL PRIMARY KEY,
            original_task_id VARCHAR(36) NOT NULL,
            task_name       VARCHAR(120) NOT NULL,
            queue           VARCHAR(50) DEFAULT 'default',
            args_payload    JSONB DEFAULT '{}',
            kwargs_payload  JSONB DEFAULT '{}',
            failure_reason  TEXT NOT NULL DEFAULT '',
            failed_at       TIMESTAMPTZ DEFAULT NOW(),
            retry_attempts  SMALLINT DEFAULT 0,
            is_resolved     BOOLEAN DEFAULT FALSE,
            resolved_at     TIMESTAMPTZ,
            resolved_by_id  BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_dead_letter_queue IS
            'Task yang gagal setelah max_retries. Perlu manual intervention.';
        CREATE INDEX IF NOT EXISTS idx_dlq_resolved ON tq_dead_letter_queue(is_resolved);
        """, "tq_dead_letter_queue"),

        ("""
        CREATE TABLE IF NOT EXISTS tq_scheduled_jobs (
            id              BIGSERIAL PRIMARY KEY,
            job_name        VARCHAR(100) UNIQUE NOT NULL,
            task_path       VARCHAR(255) NOT NULL,
            cron_expression VARCHAR(50) NOT NULL,
            description     TEXT DEFAULT '',
            queue           VARCHAR(50) DEFAULT 'default',
            kwargs          JSONB DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            last_run_at     TIMESTAMPTZ,
            next_run_at     TIMESTAMPTZ,
            last_status     VARCHAR(20) DEFAULT 'never_run',
            run_count       INT DEFAULT 0,
            fail_count      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE tq_scheduled_jobs IS
            'Celery Beat scheduled jobs. Sinkron dengan django_celery_beat_periodictask.';
        """, "tq_scheduled_jobs"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Task Definitions
    tasks_data = [
        # (name, path, desc, category, queue, priority, max_retries, timeout, scheduled, cron)
        ("refresh_kpi_cache",        "lumra_config.tasks.refresh_kpi_cache",
         "Refresh semua KPI dashboard cache",                "analytics",     "high",    8,  3,  120, True,  "0 * * * *"),
        ("recalculate_rfm_scores",   "lumra_config.tasks.recalculate_rfm_scores",
         "Hitung ulang RFM score semua customer",            "analytics",     "default", 5,  2,  600, True,  "0 2 * * *"),
        ("generate_sales_daily",     "lumra_config.tasks.generate_sales_daily",
         "Agregasi penjualan harian ke report table",        "reporting",     "default", 6,  3,  300, True,  "5 0 * * *"),
        ("generate_sales_monthly",   "lumra_config.tasks.generate_sales_monthly",
         "Agregasi penjualan bulanan",                       "reporting",     "default", 6,  3,  300, True,  "10 0 1 * *"),
        ("sync_meilisearch_products","lumra_config.tasks.sync_meilisearch_products",
         "Sync produk ke Meilisearch index",                 "sync",          "default", 5,  3,  180, True,  "*/15 * * * *"),
        ("sync_meilisearch_customers","lumra_config.tasks.sync_meilisearch_customers",
         "Sync customer data ke Meilisearch",                "sync",          "default", 4,  3,  300, True,  "0 3 * * *"),
        ("send_promo_notifications", "lumra_config.tasks.send_promo_notifications",
         "Kirim notifikasi promo terjadwal",                 "notification",  "high",    7,  3,  120, True,  "0 9 * * *"),
        ("send_birthday_notifs",     "lumra_config.tasks.send_birthday_notifs",
         "Kirim ucapan ulang tahun ke customer",             "notification",  "default", 7,  3,  60,  True,  "0 7 * * *"),
        ("cleanup_old_job_logs",     "lumra_config.tasks.cleanup_old_job_logs",
         "Hapus job logs lebih dari 90 hari",                "cleanup",       "low",     3,  1,  300, True,  "0 4 * * 0"),
        ("cleanup_expired_tokens",   "lumra_config.tasks.cleanup_expired_tokens",
         "Hapus API tokens yang expired",                    "cleanup",       "low",     3,  1,  60,  True,  "0 4 * * *"),
        ("generate_pdf_report",      "lumra_config.tasks.generate_pdf_report",
         "Generate PDF report on-demand via WeasyPrint",     "reporting",     "default", 5,  2,  120, False, ""),
        ("process_webhook_event",    "lumra_config.tasks.process_webhook_event",
         "Proses outgoing webhook event",                    "webhook",       "high",    8,  5,  30,  False, ""),
        ("send_email_notification",  "lumra_config.tasks.send_email_notification",
         "Kirim email notifikasi",                           "notification",  "default", 6,  3,  30,  False, ""),
        ("update_stock_snapshot",    "lumra_config.tasks.update_stock_snapshot",
         "Update snapshot stok bulanan",                     "sync",          "default", 5,  2,  300, True,  "0 1 1 * *"),
        ("compute_demand_forecast",  "lumra_config.tasks.compute_demand_forecast",
         "Hitung demand forecast dengan moving average",     "analytics",     "default", 4,  2,  600, True,  "0 3 * * 1"),
        ("check_reorder_alerts",     "lumra_config.tasks.check_reorder_alerts",
         "Cek stok dan buat reorder alert jika perlu",       "procurement",   "default", 7,  3,  180, True,  "0 8 * * *"),
        ("send_shift_summary",       "lumra_config.tasks.send_shift_summary",
         "Kirim ringkasan shift ke manager",                 "reporting",     "default", 6,  2,  60,  True,  "0 23 * * *"),
        ("index_search_queries",     "lumra_config.tasks.index_search_queries",
         "Analisis query search untuk improve relevancy",    "analytics",     "low",     3,  1,  300, True,  "0 5 * * *"),
        ("auto_close_tickets",       "lumra_config.tasks.auto_close_tickets",
         "Auto-close ticket yang sudah resolved > 7 hari",  "cleanup",       "low",     3,  1,  120, True,  "0 6 * * *"),
        ("generate_payslips",        "lumra_config.tasks.generate_payslips",
         "Generate slip gaji bulanan PDF",                   "reporting",     "default", 5,  2,  600, True,  "0 10 25 * *"),
    ]
    task_rows = [(name, path, desc, cat, queue, priority, max_ret, timeout,
                  is_sched, cron, True, datetime.now())
                 for name, path, desc, cat, queue, priority, max_ret, timeout, is_sched, cron in tasks_data]

    if dry_run:
        log(f"[DRY RUN] {len(task_rows)} task defs + ~50k job logs + DLQ + scheduled jobs")
        return

    n = bulk_insert("tq_task_definitions",
        ["task_name","task_path","description","category","default_queue","priority",
         "max_retries","retry_backoff","timeout_seconds","is_scheduled","cron_expression",
         "is_active","created_at"],
        task_rows, on_conflict="ON CONFLICT (task_name) DO NOTHING")
    ok(f"Task definitions: {n}")

    # Job Logs (50k entries — 2 tahun ke belakang)
    task_names   = [t[0] for t in tasks_data]
    queue_names  = ["default","high","low","notification","reporting","sync","webhook","procurement"]
    workers      = [f"worker-{i}@lumra-prod" for i in range(1, 9)]
    statuses_w   = ["success","success","success","success","failure","revoked","retry"]
    statuses_wts = [60, 0, 0, 0, 15, 5, 20]

    log("Generating job logs...")
    job_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(50000):
        task_name  = RNG.choice(task_names)
        status     = RNG.choices(statuses_w, weights=statuses_wts)[0]
        created_at = datetime.now() - timedelta(
            days=RNG.randint(0, days_range),
            hours=RNG.randint(0, 23), minutes=RNG.randint(0, 59)
        )
        started_at    = created_at + timedelta(seconds=RNG.randint(0, 30))
        duration_ms   = RNG.randint(50, 30000) if status != "revoked" else 0
        completed_at  = started_at + timedelta(milliseconds=duration_ms) if duration_ms else None
        retry_count   = RNG.randint(0, 3) if status in ("failure","retry") else 0
        error_msg     = RNG.choice([
            "ConnectionError: Redis timeout",
            "OperationalError: DB connection failed",
            "ValueError: Invalid argument",
            "TimeoutError: Task exceeded timeout",
            ""
        ]) if status == "failure" else ""

        job_rows.append((
            rand_uuid(), task_name,
            RNG.choice(queue_names), status,
            f"args: [{RNG.randint(1,100)}]", "{}",
            RNG.choice(["schedule","api","manual","celery_beat"]),
            None, RNG.choice(workers),
            started_at, completed_at, duration_ms if duration_ms else None,
            "OK" if status == "success" else "",
            error_msg, retry_count, created_at
        ))

    n = bulk_insert("tq_job_logs",
        ["task_id","task_name","queue","status","args_summary","kwargs_summary",
         "triggered_by","triggered_by_id","worker_name","started_at","completed_at",
         "duration_ms","result_summary","error_message","retry_count","created_at"],
        job_rows, batch=3000)
    ok(f"Job logs: {n:,}")

    # Dead Letter Queue (failed setelah max retry)
    dlq_rows = []
    for _ in range(500):
        created_at = datetime.now() - timedelta(days=RNG.randint(0, 90))
        resolved   = RNG.random() < 0.4
        dlq_rows.append((
            rand_uuid(), RNG.choice(task_names),
            RNG.choice(queue_names),
            json.dumps({"location_id": RNG.randint(1, 20)}),
            json.dumps({"period": today.strftime("%Y-%m")}),
            RNG.choice(["Max retries exceeded","Task timeout","Unhandled exception"]),
            created_at, RNG.randint(3, 5),
            resolved, created_at + timedelta(days=RNG.randint(1, 7)) if resolved else None,
            CTX["admin_id"] if resolved else None, created_at
        ))

    n = bulk_insert("tq_dead_letter_queue",
        ["original_task_id","task_name","queue","args_payload","kwargs_payload",
         "failure_reason","failed_at","retry_attempts","is_resolved","resolved_at",
         "resolved_by_id","created_at"],
        dlq_rows)
    ok(f"Dead letter queue: {n}")

    # Scheduled Jobs
    scheduled_tasks = [t for t in tasks_data if t[8]]  # is_scheduled == True
    sched_rows = []
    for name, path, desc, cat, queue, priority, _, _, _, cron in scheduled_tasks:
        last_run = datetime.now() - timedelta(hours=RNG.randint(1, 48))
        next_run = last_run + timedelta(hours=1)
        run_count = RNG.randint(50, 2000)
        sched_rows.append((
            f"beat_{name}", path, cron, desc, queue,
            json.dumps({}), True,
            last_run, next_run,
            RNG.choice(["success","success","success","failure"]),
            run_count, int(run_count * RNG.uniform(0, 0.05)),
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("tq_scheduled_jobs",
        ["job_name","task_path","cron_expression","description","queue","kwargs",
         "is_active","last_run_at","next_run_at","last_status","run_count","fail_count",
         "created_at","updated_at"],
        sched_rows, on_conflict="ON CONFLICT (job_name) DO NOTHING")
    ok(f"Scheduled jobs: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 21 — SEARCH (Meilisearch)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_search(dry_run=False):
    head("MODUL 21 — SEARCH (Meilisearch Index Config, Query Logs, Synonyms, Analytics)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS search_index_configs (
            id              BIGSERIAL PRIMARY KEY,
            index_uid       VARCHAR(60) UNIQUE NOT NULL,
            display_name    VARCHAR(100) NOT NULL,
            source_table    VARCHAR(80) NOT NULL,
            primary_key     VARCHAR(30) DEFAULT 'id',
            searchable_attrs JSONB DEFAULT '[]',
            filterable_attrs JSONB DEFAULT '[]',
            sortable_attrs   JSONB DEFAULT '[]',
            displayed_attrs  JSONB DEFAULT '[]',
            ranking_rules    JSONB DEFAULT '["words","typo","proximity","attribute","sort","exactness"]',
            facets           JSONB DEFAULT '[]',
            total_documents INT DEFAULT 0,
            last_synced_at  TIMESTAMPTZ,
            sync_enabled    BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE search_index_configs IS
            'Konfigurasi index Meilisearch per entity. Sinkron otomatis via Celery task.';
        """, "search_index_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS search_query_logs (
            id              BIGSERIAL PRIMARY KEY,
            index_uid       VARCHAR(60) NOT NULL,
            query_text      VARCHAR(500) NOT NULL DEFAULT '',
            user_id         BIGINT REFERENCES auth_user(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            results_count   INT DEFAULT 0,
            clicked_result_id BIGINT,
            response_ms     INT DEFAULT 0,
            filters_applied JSONB DEFAULT '{}',
            session_id      VARCHAR(40) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE search_query_logs IS
            'Log setiap pencarian: kata kunci, jumlah hasil, klik. Untuk search analytics.';
        CREATE INDEX IF NOT EXISTS idx_sq_index   ON search_query_logs(index_uid);
        CREATE INDEX IF NOT EXISTS idx_sq_query   ON search_query_logs(query_text);
        CREATE INDEX IF NOT EXISTS idx_sq_date    ON search_query_logs(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_sq_results ON search_query_logs(results_count);
        """, "search_query_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS search_synonyms (
            id              BIGSERIAL PRIMARY KEY,
            index_uid       VARCHAR(60) NOT NULL,
            word            VARCHAR(100) NOT NULL,
            synonyms        TEXT[] NOT NULL DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(index_uid, word)
        );
        COMMENT ON TABLE search_synonyms IS
            'Sinonim pencarian per index. Contoh: es kopi = iced coffee = cold brew.';
        """, "search_synonyms"),

        ("""
        CREATE TABLE IF NOT EXISTS search_analytics_daily (
            id              BIGSERIAL PRIMARY KEY,
            report_date     DATE NOT NULL,
            index_uid       VARCHAR(60) NOT NULL,
            total_searches  INT DEFAULT 0,
            unique_queries  INT DEFAULT 0,
            zero_result_searches INT DEFAULT 0,
            avg_response_ms NUMERIC(8,2) DEFAULT 0,
            top_queries     JSONB DEFAULT '[]',
            top_zero_results JSONB DEFAULT '[]',
            click_through_rate NUMERIC(5,3) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(report_date, index_uid)
        );
        COMMENT ON TABLE search_analytics_daily IS
            'Statistik pencarian harian. Dasar untuk improve ranking dan synonyms.';
        CREATE INDEX IF NOT EXISTS idx_sa_date ON search_analytics_daily(report_date DESC);
        """, "search_analytics_daily"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Index Configs
    indexes_data = [
        ("products",      "Produk & Menu",       "lumra_config_productvariants",
         ["name","description","category","tags"],
         ["category","is_active","price"],
         ["name","price","popularity"],
         ["id","name","price","category","image_url"],
         ["category","price_range"]),
        ("customers",     "Database Customer",   "lumra_config_customers",
         ["full_name","phone","email","member_id"],
         ["tier","is_active","created_at"],
         ["full_name","created_at","lifetime_spend"],
         ["id","full_name","phone","email","tier"],
         ["tier"]),
        ("orders",        "Riwayat Transaksi",   "lumra_config_orders",
         ["order_number","customer_name","notes"],
         ["status","payment_method","location_id","created_at"],
         ["created_at","paid_amount"],
         ["id","order_number","status","paid_amount","created_at"],
         ["status","payment_method","location_id"]),
        ("locations",     "Outpost Directory",   "lumra_config_locations",
         ["name","address","city","description"],
         ["is_active","city"],
         ["name","city"],
         ["id","name","address","city","latitude","longitude"],
         ["city"]),
        ("vendors",       "Daftar Vendor",       "lumra_config_vendors",
         ["name","contact_name","email","phone","address"],
         ["is_active"],
         ["name"],
         ["id","name","contact_name","email","phone"],
         []),
        ("promotions",    "Promo Aktif",         "lumra_sales_promotions",
         ["name","code","description"],
         ["is_active","promo_type","applicable_session"],
         ["name","discount_value"],
         ["id","code","name","discount_type","discount_value","valid_until"],
         ["promo_type","applicable_session"]),
        ("rfm_segments",  "Customer Segments",   "lumra_crm_rfm_scores",
         ["segment"],
         ["segment","r_score","f_score","m_score"],
         ["rfm_score","monetary_total"],
         ["customer_id","segment","rfm_score","monetary_total"],
         ["segment"]),
        ("assets",        "Asset Registry",      "maint_asset_registry",
         ["asset_name","brand","model","serial_number"],
         ["category","status","location_id"],
         ["asset_name","current_value"],
         ["id","asset_code","asset_name","category","status","location_id"],
         ["category","status"]) if table_exists("maint_asset_registry") else None,
    ]
    indexes_data = [x for x in indexes_data if x is not None]

    idx_rows = [(uid, dname, src, pkey,
                 json.dumps(srch), json.dumps(filt),
                 json.dumps(sort), json.dumps(disp),
                 json.dumps(["words","typo","proximity","attribute","sort","exactness"]),
                 json.dumps(facets),
                 RNG.randint(100, 50000),
                 datetime.now() - timedelta(minutes=RNG.randint(0, 60)),
                 True, datetime.now(), datetime.now())
                for uid, dname, src, srch, filt, sort, disp, facets in [
                    (uid, dn, src, srch, filt, sort, disp, facets)
                    for uid, dn, src, srch, filt, sort, disp, facets in indexes_data
                    # unpack properly
                ]
               ]

    # Rebuild properly
    idx_rows = []
    for row in indexes_data:
        uid, dn, src, srch, filt, sort_, disp, facets = row
        idx_rows.append((
            uid, dn, src, "id",
            json.dumps(srch), json.dumps(filt),
            json.dumps(sort_), json.dumps(disp),
            json.dumps(["words","typo","proximity","attribute","sort","exactness"]),
            json.dumps(facets),
            RNG.randint(100, 50000),
            datetime.now() - timedelta(minutes=RNG.randint(0, 60)),
            True, datetime.now(), datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(idx_rows)} indexes + query logs + synonyms + daily analytics")
        return

    n = bulk_insert("search_index_configs",
        ["index_uid","display_name","source_table","primary_key",
         "searchable_attrs","filterable_attrs","sortable_attrs","displayed_attrs",
         "ranking_rules","facets","total_documents","last_synced_at",
         "sync_enabled","created_at","updated_at"],
        idx_rows, on_conflict="ON CONFLICT (index_uid) DO NOTHING")
    ok(f"Search index configs: {n}")

    # Query Logs
    SAMPLE_QUERIES = [
        "es kopi susu","cold brew","americano","filter coffee","latte",
        "pastry","croissant","granola bowl","matcha","chocolate",
        "promo weekend","voucher","diskon","paket hemat","morning ration",
        "outpost bandung","outpost jakarta","buka jam berapa",
        "menu seasonal","grand reserve","single origin",
        "kopi ethiopia","kenya","flores","gayo","toraja",
        "cemara","kuningan","dago","sudirman","kemang",
    ]
    ZERO_RESULT = ["kopi boba","menu vegan","kopi decaf","delivery order","kopi kopi"]

    index_uids = [row[0] for row in indexes_data]
    customer_ids = CTX["customer_ids"]
    user_ids     = CTX["user_ids"]
    location_ids = CTX["location_ids"]

    ql_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(100000):
        is_zero = RNG.random() < 0.08
        query   = RNG.choice(ZERO_RESULT) if is_zero else RNG.choice(SAMPLE_QUERIES)
        n_results = 0 if is_zero else RNG.randint(1, 50)
        uid     = RNG.choice(index_uids)
        cid     = RNG.choice(customer_ids) if RNG.random() < 0.6 else None
        uid_user= RNG.choice(user_ids) if RNG.random() < 0.3 else None
        created = datetime.now() - timedelta(
            days=RNG.randint(0, days_range),
            hours=RNG.randint(0, 23)
        )
        ql_rows.append((
            uid, query, uid_user, cid,
            RNG.choice(location_ids) if RNG.random() < 0.5 else None,
            n_results,
            RNG.randint(1, 100) if n_results > 0 and RNG.random() < 0.3 else None,
            RNG.randint(2, 150),
            json.dumps({}), rand_hex(8), created
        ))

    n = bulk_insert("search_query_logs",
        ["index_uid","query_text","user_id","customer_id","location_id",
         "results_count","clicked_result_id","response_ms","filters_applied",
         "session_id","created_at"],
        ql_rows, batch=3000)
    ok(f"Search query logs: {n:,}")

    # Synonyms
    synonyms_data = {
        "products": {
            "es kopi susu": ["iced coffee latte","cold coffee milk","kopi susu dingin"],
            "cold brew":    ["kopi dingin","es kopi","cold coffee"],
            "americano":    ["black coffee","kopi hitam","long black"],
            "latte":        ["coffee latte","kopi susu","caffe latte"],
            "croissant":    ["roti tanduk","pastry"],
            "granola":      ["granola bowl","cereal","oatmeal"],
            "matcha":       ["green tea","teh hijau"],
            "single origin":["specialty coffee","kopi specialty","kopi premium"],
        },
        "customers": {
            "member":   ["pelanggan","customer"],
            "loyal":    ["setia","champion","reguler"],
        },
        "locations": {
            "outpost":  ["cabang","gerai","toko","kafe"],
            "bandung":  ["bdg","kota kembang"],
            "jakarta":  ["jkt","ibukota"],
        }
    }
    syn_rows = []
    for idx_uid, syns in synonyms_data.items():
        for word, synonyms in syns.items():
            syn_rows.append((idx_uid, word, synonyms, True, datetime.now()))

    n = bulk_insert("search_synonyms",
        ["index_uid","word","synonyms","is_active","created_at"],
        syn_rows, on_conflict="ON CONFLICT (index_uid, word) DO NOTHING")
    ok(f"Search synonyms: {n}")

    # Daily Analytics
    sa_rows = []
    TOP_QUERIES_SAMPLE = [
        [{"q": "es kopi susu", "count": 120}, {"q": "cold brew", "count": 80}],
        [{"q": "americano", "count": 60}, {"q": "latte", "count": 45}],
    ]
    for d in range(days_range):
        report_date = today - timedelta(days=d)
        for uid in index_uids:
            total  = RNG.randint(50, 2000)
            unique = int(total * RNG.uniform(0.3, 0.7))
            zero   = int(total * RNG.uniform(0.05, 0.15))
            ctr    = round(RNG.uniform(0.1, 0.5), 3)
            sa_rows.append((
                report_date, uid, total, unique, zero,
                round(RNG.uniform(10, 100), 2),
                json.dumps(RNG.choice(TOP_QUERIES_SAMPLE)),
                json.dumps([{"q": q, "count": RNG.randint(1,10)} for q in ZERO_RESULT[:2]]),
                ctr, datetime.now()
            ))

    n = bulk_insert("search_analytics_daily",
        ["report_date","index_uid","total_searches","unique_queries",
         "zero_result_searches","avg_response_ms","top_queries","top_zero_results",
         "click_through_rate","created_at"],
        sa_rows, batch=3000,
        on_conflict="ON CONFLICT (report_date, index_uid) DO NOTHING")
    ok(f"Search analytics daily: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 22 — REPORTING (WeasyPrint PDF Reports)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_reporting(dry_run=False):
    head("MODUL 22 — REPORTING (Templates, Schedules, Generated Reports, Delivery)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS report_templates (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(40) UNIQUE NOT NULL,
            title           VARCHAR(150) NOT NULL,
            description     TEXT DEFAULT '',
            report_type     VARCHAR(30) NOT NULL DEFAULT 'operational',
            template_path   VARCHAR(255) NOT NULL DEFAULT '',
            output_format   VARCHAR(10) DEFAULT 'pdf',
            parameters      JSONB DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            requires_role   VARCHAR(40) DEFAULT 'staff',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_templates IS
            'Template laporan PDF via WeasyPrint. Type: operational, financial, hr, analytics.';
        """, "report_templates"),

        ("""
        CREATE TABLE IF NOT EXISTS report_schedules (
            id              BIGSERIAL PRIMARY KEY,
            template_id     BIGINT NOT NULL REFERENCES report_templates(id),
            schedule_name   VARCHAR(100) NOT NULL,
            cron_expression VARCHAR(50) NOT NULL,
            parameters      JSONB DEFAULT '{}',
            recipients      JSONB DEFAULT '[]',
            delivery_method VARCHAR(20) DEFAULT 'email',
            is_active       BOOLEAN DEFAULT TRUE,
            last_run_at     TIMESTAMPTZ,
            next_run_at     TIMESTAMPTZ,
            run_count       INT DEFAULT 0,
            created_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_schedules IS
            'Jadwal otomatis generate + kirim laporan. Delivery: email, slack, sftp.';
        """, "report_schedules"),

        ("""
        CREATE TABLE IF NOT EXISTS report_generated (
            id              BIGSERIAL PRIMARY KEY,
            template_id     BIGINT REFERENCES report_templates(id),
            schedule_id     BIGINT REFERENCES report_schedules(id),
            report_title    VARCHAR(200) NOT NULL,
            parameters      JSONB DEFAULT '{}',
            file_name       VARCHAR(255) NOT NULL DEFAULT '',
            file_size_kb    INT DEFAULT 0,
            page_count      INT DEFAULT 1,
            status          VARCHAR(20) DEFAULT 'generating',
            generated_by_id BIGINT REFERENCES auth_user(id),
            generation_ms   INT DEFAULT 0,
            error_message   TEXT DEFAULT '',
            expires_at      TIMESTAMPTZ,
            download_count  INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_generated IS
            'Log setiap laporan yang di-generate. File disimpan di storage.';
        CREATE INDEX IF NOT EXISTS idx_rg_template ON report_generated(template_id);
        CREATE INDEX IF NOT EXISTS idx_rg_date     ON report_generated(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_rg_status   ON report_generated(status);
        """, "report_generated"),

        ("""
        CREATE TABLE IF NOT EXISTS report_delivery_log (
            id              BIGSERIAL PRIMARY KEY,
            report_id       BIGINT NOT NULL REFERENCES report_generated(id),
            recipient       VARCHAR(150) NOT NULL,
            delivery_method VARCHAR(20) DEFAULT 'email',
            status          VARCHAR(20) DEFAULT 'sent',
            sent_at         TIMESTAMPTZ DEFAULT NOW(),
            opened_at       TIMESTAMPTZ,
            error_message   TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE report_delivery_log IS 'Log pengiriman laporan ke penerima.';
        CREATE INDEX IF NOT EXISTS idx_rdl_report ON report_delivery_log(report_id);
        """, "report_delivery_log"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # Templates
    templates_data = [
        ("DAILY_SALES",       "Laporan Penjualan Harian",         "operational",
         "reports/daily_sales.html",     "pdf",  {"location_id": None, "date": "today"}),
        ("WEEKLY_SALES",      "Laporan Penjualan Mingguan",       "operational",
         "reports/weekly_sales.html",    "pdf",  {"location_id": None, "week_offset": 0}),
        ("MONTHLY_SALES",     "Laporan Penjualan Bulanan",        "operational",
         "reports/monthly_sales.html",   "pdf",  {"year": None, "month": None}),
        ("PAYSLIP",           "Slip Gaji Karyawan",               "hr",
         "reports/payslip.html",         "pdf",  {"employee_id": None, "period": None}),
        ("PAYROLL_SUMMARY",   "Rekapitulasi Payroll Bulanan",     "hr",
         "reports/payroll_summary.html", "pdf",  {"period": None, "location_id": None}),
        ("INVENTORY_STOCK",   "Laporan Stok Inventaris",          "operational",
         "reports/inventory_stock.html", "pdf",  {"location_id": None, "as_of_date": "today"}),
        ("PO_DOCUMENT",       "Dokumen Purchase Order",           "procurement",
         "reports/purchase_order.html",  "pdf",  {"po_id": None}),
        ("GRN_DOCUMENT",      "Dokumen Good Receipt Note",        "procurement",
         "reports/grn.html",             "pdf",  {"grn_id": None}),
        ("CUSTOMER_STATEMENT","Laporan Transaksi Customer",       "crm",
         "reports/customer_statement.html","pdf",{"customer_id": None, "months": 3}),
        ("RFM_REPORT",        "Analisis RFM Customer",            "analytics",
         "reports/rfm_analysis.html",   "pdf",  {"segment": None}),
        ("WASTE_REPORT",      "Laporan Waste Produksi",           "operational",
         "reports/waste_report.html",    "pdf",  {"location_id": None, "period": None}),
        ("FINANCIAL_SUMMARY", "Ringkasan Keuangan Bulanan",       "financial",
         "reports/financial_summary.html","pdf", {"year": None, "month": None}),
        ("BUDGET_VS_ACTUAL",  "Realisasi vs Anggaran",            "financial",
         "reports/budget_actual.html",  "pdf",  {"year": None, "quarter": None}),
        ("SUPPLIER_SCORECARD","Supplier Scorecard Report",        "procurement",
         "reports/supplier_scorecard.html","pdf",{"vendor_id": None, "period": None}),
        ("SHIFT_SUMMARY",     "Ringkasan Shift Harian",           "operational",
         "reports/shift_summary.html",  "pdf",  {"location_id": None, "date": "today"}),
        ("NPS_DASHBOARD",     "Net Promoter Score Dashboard",     "analytics",
         "reports/nps_dashboard.html",  "pdf",  {"period": None}),
        ("TRAINING_PROGRESS", "Progress Training Karyawan",       "hr",
         "reports/training_progress.html","pdf", {"location_id": None}),
        ("ASSET_REGISTER",    "Daftar Aset Per Lokasi",           "operational",
         "reports/asset_register.html", "pdf",  {"location_id": None}),
        ("MENU_PERFORMANCE",  "Menu Engineering Report",          "analytics",
         "reports/menu_performance.html","pdf",  {"location_id": None, "period": None}),
        ("CONSOLIDATED_P&L",  "Laporan Laba Rugi Konsolidasi",    "financial",
         "reports/pnl_consolidated.html","pdf",  {"year": None, "month": None}),
    ]
    tmpl_rows = [(code, title, "", rtype, tpath, fmt,
                  json.dumps(params), True, "manager", datetime.now())
                 for code, title, rtype, tpath, fmt, params in templates_data]

    if dry_run:
        log(f"[DRY RUN] {len(tmpl_rows)} templates + schedules + generated reports + delivery logs")
        return

    n = bulk_insert("report_templates",
        ["code","title","description","report_type","template_path","output_format",
         "parameters","is_active","requires_role","created_at"],
        tmpl_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Report templates: {n}")

    # Schedules
    tmpl_ids    = [r[0] for r in q("SELECT id FROM report_templates ORDER BY id")]
    admin_id    = CTX["admin_id"]
    user_ids    = CTX["user_ids"]
    sched_rows  = []
    RECIPS      = ["manager@kafenusantara.id","ops@kafenusantara.id","cfo@kafenusantara.id"]
    for tid in tmpl_ids[:10]:
        last_run = datetime.now() - timedelta(hours=RNG.randint(1, 72))
        sched_rows.append((
            tid, f"auto_schedule_{tid}",
            RNG.choice(["0 7 * * *","0 8 * * 1","0 9 1 * *"]),
            json.dumps({"location_id": None}),
            json.dumps(RNG.sample(RECIPS, RNG.randint(1, 3))),
            "email", True,
            last_run, last_run + timedelta(days=1),
            RNG.randint(10, 200),
            RNG.choice(user_ids) if user_ids else admin_id,
            datetime.now()
        ))

    n = bulk_insert("report_schedules",
        ["template_id","schedule_name","cron_expression","parameters","recipients",
         "delivery_method","is_active","last_run_at","next_run_at","run_count",
         "created_by_id","created_at"],
        sched_rows)
    ok(f"Report schedules: {n}")

    # Generated Reports
    sched_ids  = [r[0] for r in q("SELECT id FROM report_schedules ORDER BY id")]
    gen_rows   = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(5000):
        tid      = RNG.choice(tmpl_ids)
        sid      = RNG.choice(sched_ids) if sched_ids else None
        status   = RNG.choices(["completed","completed","failed","generating"],
                               weights=[85, 0, 10, 5])[0]
        gen_ms   = RNG.randint(500, 15000) if status == "completed" else 0
        created  = datetime.now() - timedelta(days=RNG.randint(0, days_range))
        gen_rows.append((
            tid, sid,
            f"Laporan #{RNG.randint(1000,9999)} - {created.strftime('%Y-%m-%d')}",
            json.dumps({"period": created.strftime("%Y-%m")}),
            f"report_{rand_hex(8)}.pdf",
            RNG.randint(50, 5000),
            RNG.randint(1, 50),
            status,
            RNG.choice(user_ids) if user_ids else admin_id,
            gen_ms, "",
            created + timedelta(days=30),
            RNG.randint(0, 20), created
        ))

    n = bulk_insert("report_generated",
        ["template_id","schedule_id","report_title","parameters","file_name",
         "file_size_kb","page_count","status","generated_by_id","generation_ms",
         "error_message","expires_at","download_count","created_at"],
        gen_rows, batch=3000)
    ok(f"Generated reports: {n:,}")

    # Delivery Logs
    rpt_ids    = [r[0] for r in q("SELECT id FROM report_generated WHERE status='completed' ORDER BY id LIMIT 3000")]
    dlv_rows   = []
    for rid in rpt_ids:
        n_recip = RNG.randint(1, 3)
        for recip in RNG.sample(RECIPS, min(n_recip, len(RECIPS))):
            sent  = datetime.now() - timedelta(days=RNG.randint(0, 90))
            status= RNG.choices(["sent","delivered","opened","failed"],
                                weights=[15, 40, 40, 5])[0]
            dlv_rows.append((
                rid, recip, "email", status, sent,
                sent + timedelta(minutes=RNG.randint(1, 60)) if status == "opened" else None,
                "", sent
            ))

    n = bulk_insert("report_delivery_log",
        ["report_id","recipient","delivery_method","status","sent_at",
         "opened_at","error_message","created_at"],
        dlv_rows, batch=3000)
    ok(f"Report delivery logs: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 23 — API GATEWAY (DRF — API Keys, Rate Limits, Webhooks)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_api_gateway(dry_run=False):
    head("MODUL 23 — API GATEWAY (API Keys, Rate Limits, Usage Logs, Webhooks)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id              BIGSERIAL PRIMARY KEY,
            key_id          VARCHAR(20) UNIQUE NOT NULL,
            key_hash        VARCHAR(64) NOT NULL,
            name            VARCHAR(100) NOT NULL,
            owner_id        BIGINT REFERENCES auth_user(id),
            scopes          TEXT[] DEFAULT '{}',
            allowed_ips     TEXT[] DEFAULT '{}',
            rate_limit_tier VARCHAR(20) DEFAULT 'standard',
            is_active       BOOLEAN DEFAULT TRUE,
            expires_at      TIMESTAMPTZ,
            last_used_at    TIMESTAMPTZ,
            total_requests  BIGINT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_keys IS
            'API Keys untuk akses DRF endpoints. Scopes: read, write, admin, webhook.';
        CREATE INDEX IF NOT EXISTS idx_api_key_owner ON api_keys(owner_id);
        """, "api_keys"),

        ("""
        CREATE TABLE IF NOT EXISTS api_rate_limit_tiers (
            id              BIGSERIAL PRIMARY KEY,
            tier_name       VARCHAR(20) UNIQUE NOT NULL,
            requests_per_minute INT DEFAULT 60,
            requests_per_hour   INT DEFAULT 1000,
            requests_per_day    INT DEFAULT 10000,
            burst_limit         INT DEFAULT 100,
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_rate_limit_tiers IS
            'Tier rate limiting untuk API keys. Tier: free, standard, premium, internal.';
        """, "api_rate_limit_tiers"),

        ("""
        CREATE TABLE IF NOT EXISTS api_usage_logs (
            id              BIGSERIAL PRIMARY KEY,
            api_key_id      BIGINT REFERENCES api_keys(id),
            endpoint        VARCHAR(200) NOT NULL,
            method          VARCHAR(10) NOT NULL DEFAULT 'GET',
            status_code     SMALLINT NOT NULL DEFAULT 200,
            response_ms     INT DEFAULT 0,
            request_size_b  INT DEFAULT 0,
            response_size_b INT DEFAULT 0,
            ip_address      INET,
            user_agent      VARCHAR(200) DEFAULT '',
            error_code      VARCHAR(30) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_usage_logs IS
            'Log setiap API request. Untuk billing, analytics, debugging.';
        CREATE INDEX IF NOT EXISTS idx_api_usage_key    ON api_usage_logs(api_key_id);
        CREATE INDEX IF NOT EXISTS idx_api_usage_date   ON api_usage_logs(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage_logs(endpoint);
        CREATE INDEX IF NOT EXISTS idx_api_usage_status ON api_usage_logs(status_code);
        """, "api_usage_logs"),

        ("""
        CREATE TABLE IF NOT EXISTS api_webhooks (
            id              BIGSERIAL PRIMARY KEY,
            webhook_id      VARCHAR(20) UNIQUE NOT NULL,
            name            VARCHAR(100) NOT NULL,
            owner_id        BIGINT REFERENCES auth_user(id),
            target_url      VARCHAR(500) NOT NULL,
            secret_key      VARCHAR(64) NOT NULL DEFAULT '',
            events          TEXT[] NOT NULL DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            failure_count   INT DEFAULT 0,
            last_triggered_at TIMESTAMPTZ,
            last_status     VARCHAR(20) DEFAULT 'never',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_webhooks IS
            'Webhook endpoints untuk event push. Events: order.completed, stock.low, payroll.processed.';
        """, "api_webhooks"),

        ("""
        CREATE TABLE IF NOT EXISTS api_webhook_deliveries (
            id              BIGSERIAL PRIMARY KEY,
            webhook_id      BIGINT NOT NULL REFERENCES api_webhooks(id),
            event_type      VARCHAR(60) NOT NULL,
            payload         JSONB NOT NULL DEFAULT '{}',
            response_code   SMALLINT,
            response_body   TEXT DEFAULT '',
            duration_ms     INT DEFAULT 0,
            attempt_number  SMALLINT DEFAULT 1,
            status          VARCHAR(20) DEFAULT 'pending',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE api_webhook_deliveries IS
            'Log pengiriman webhook. Retry otomatis 3x dengan exponential backoff.';
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_webhook ON api_webhook_deliveries(webhook_id);
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_status  ON api_webhook_deliveries(status);
        CREATE INDEX IF NOT EXISTS idx_wh_delivery_date    ON api_webhook_deliveries(created_at DESC);
        """, "api_webhook_deliveries"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]

    # Rate Limit Tiers
    tier_rows = [
        ("free",      30,   500,    5000,   50),
        ("standard",  60,   1000,   10000,  100),
        ("premium",   300,  10000,  100000, 500),
        ("internal",  1000, 100000, 1000000,2000),
    ]
    if not dry_run:
        n = bulk_insert("api_rate_limit_tiers",
            ["tier_name","requests_per_minute","requests_per_hour","requests_per_day","burst_limit","is_active","created_at"],
            [(t, rpm, rph, rpd, burst, True, datetime.now()) for t, rpm, rph, rpd, burst in tier_rows],
            on_conflict="ON CONFLICT (tier_name) DO NOTHING")
        ok(f"Rate limit tiers: {n}")

    # API Keys
    SCOPES_SETS = [
        ["read"],
        ["read","write"],
        ["read","write","webhook"],
        ["read","write","admin","webhook"],
        ["read","analytics"],
    ]
    APP_NAMES = [
        "Lumra POS Mobile","Lumra Dashboard Web","Lumra Manager App",
        "Inventory Scanner","Third Party Integration","Analytics Platform",
        "WhatsApp Bot","Instagram Integration","Delivery Partner API",
    ]
    key_rows = []
    for i in range(50):
        uid    = RNG.choice(user_ids) if user_ids else admin_id
        kid    = f"KN{rand_hex(6).upper()}"
        khash  = rand_hex(64)
        created = datetime.now() - timedelta(days=RNG.randint(0, 365))
        key_rows.append((
            kid, khash,
            RNG.choice(APP_NAMES),
            uid,
            RNG.choice(SCOPES_SETS),
            [],
            RNG.choice(["standard","standard","premium","internal","free"]),
            RNG.random() > 0.1,
            created + timedelta(days=365) if RNG.random() < 0.3 else None,
            datetime.now() - timedelta(hours=RNG.randint(0, 720)),
            RNG.randint(100, 1000000),
            created, created
        ))

    if dry_run:
        log(f"[DRY RUN] 50 API keys + usage logs + webhooks + deliveries")
        return

    n = bulk_insert("api_keys",
        ["key_id","key_hash","name","owner_id","scopes","allowed_ips",
         "rate_limit_tier","is_active","expires_at","last_used_at",
         "total_requests","created_at","updated_at"],
        key_rows, on_conflict="ON CONFLICT (key_id) DO NOTHING")
    ok(f"API keys: {n}")

    # Usage Logs (100k entries)
    key_ids   = [r[0] for r in q("SELECT id FROM api_keys ORDER BY id")]
    ENDPOINTS = [
        "/api/v1/orders/","/api/v1/orders/{id}/","/api/v1/products/",
        "/api/v1/customers/","/api/v1/customers/{id}/","/api/v1/inventory/stock/",
        "/api/v1/reports/sales-daily/","/api/v1/promotions/","/api/v1/locations/",
        "/api/v1/rfm/segments/","/api/v1/kpi/dashboard/","/api/v1/auth/token/",
        "/api/v1/search/","/api/v1/webhooks/","/api/v1/notifications/",
    ]
    METHODS   = ["GET","GET","GET","POST","PUT","PATCH","DELETE"]
    STATUSES  = [200,200,200,201,400,401,403,404,429,500]
    STAT_WTS  = [60,0,0,15,8,5,3,5,2,2]
    IPS       = [f"10.{RNG.randint(0,5)}.{RNG.randint(0,255)}.{RNG.randint(1,254)}" for _ in range(20)]

    usage_rows = []
    days_range = (today - CTX["min_date"]).days
    for _ in range(100000):
        created = datetime.now() - timedelta(
            days=RNG.randint(0, days_range), hours=RNG.randint(0, 23)
        )
        status = RNG.choices(STATUSES, weights=STAT_WTS)[0]
        usage_rows.append((
            RNG.choice(key_ids) if key_ids else None,
            RNG.choice(ENDPOINTS),
            RNG.choice(METHODS),
            status,
            RNG.randint(5, 2000),
            RNG.randint(100, 5000),
            RNG.randint(200, 50000),
            RNG.choice(IPS),
            "LumraClient/1.0",
            "" if status < 400 else RNG.choice(["RATE_LIMIT","NOT_FOUND","AUTH_FAILED","VALIDATION"]),
            created
        ))

    n = bulk_insert("api_usage_logs",
        ["api_key_id","endpoint","method","status_code","response_ms",
         "request_size_b","response_size_b","ip_address","user_agent",
         "error_code","created_at"],
        usage_rows, batch=3000)
    ok(f"API usage logs: {n:,}")

    # Webhooks
    EVENTS_SETS = [
        ["order.completed","order.cancelled"],
        ["stock.low","stock.out"],
        ["payroll.processed"],
        ["customer.registered","customer.tier_upgrade"],
        ["report.generated"],
    ]
    wh_rows = []
    for i in range(20):
        uid = RNG.choice(user_ids) if user_ids else admin_id
        wh_rows.append((
            f"WH{rand_hex(8).upper()}", f"Webhook #{i+1}",
            uid, f"https://hooks.example{i}.com/lumra",
            rand_hex(32), RNG.choice(EVENTS_SETS), True,
            RNG.randint(0, 10),
            datetime.now() - timedelta(hours=RNG.randint(0, 720)),
            RNG.choice(["success","success","failed"]),
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("api_webhooks",
        ["webhook_id","name","owner_id","target_url","secret_key","events",
         "is_active","failure_count","last_triggered_at","last_status","created_at","updated_at"],
        wh_rows, on_conflict="ON CONFLICT (webhook_id) DO NOTHING")
    ok(f"Webhooks: {n}")

    # Webhook Deliveries
    wh_ids   = [r[0] for r in q("SELECT id FROM api_webhooks ORDER BY id")]
    WH_EVENTS= ["order.completed","stock.low","customer.registered","report.generated","payroll.processed"]
    wdlv_rows= []
    for _ in range(10000):
        wid    = RNG.choice(wh_ids) if wh_ids else 1
        status = RNG.choices(["delivered","delivered","failed","pending"],
                             weights=[75, 0, 20, 5])[0]
        created= datetime.now() - timedelta(days=RNG.randint(0, 90))
        wdlv_rows.append((
            wid, RNG.choice(WH_EVENTS),
            json.dumps({"event": "test", "data": {"id": RNG.randint(1,1000)}}),
            200 if status == "delivered" else RNG.choice([400, 500, None]),
            "{}" if status == "delivered" else "Connection refused",
            RNG.randint(50, 3000),
            RNG.randint(1, 3),
            status, created
        ))

    n = bulk_insert("api_webhook_deliveries",
        ["webhook_id","event_type","payload","response_code","response_body",
         "duration_ms","attempt_number","status","created_at"],
        wdlv_rows, batch=3000)
    ok(f"Webhook deliveries: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 24 — SECURITY (Login Events, Alerts, IP Whitelist)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_security(dry_run=False):
    head("MODUL 24 — SECURITY (Login Events, Security Alerts, Device Registry)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS sec_login_events (
            id              BIGSERIAL PRIMARY KEY,
            user_id         BIGINT REFERENCES auth_user(id),
            username_attempt VARCHAR(150) NOT NULL DEFAULT '',
            event_type      VARCHAR(20) NOT NULL DEFAULT 'login_success',
            ip_address      INET NOT NULL,
            user_agent      TEXT DEFAULT '',
            device_fingerprint VARCHAR(64) DEFAULT '',
            location_hint   VARCHAR(100) DEFAULT '',
            is_suspicious   BOOLEAN DEFAULT FALSE,
            failure_reason  VARCHAR(50) DEFAULT '',
            session_id      VARCHAR(40) DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_login_events IS
            'Log semua login attempt. Event: login_success, login_failed, logout, password_reset.
            Terintegrasi dengan django-axes.';
        CREATE INDEX IF NOT EXISTS idx_login_user ON sec_login_events(user_id);
        CREATE INDEX IF NOT EXISTS idx_login_ip   ON sec_login_events(ip_address);
        CREATE INDEX IF NOT EXISTS idx_login_date ON sec_login_events(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_login_susp ON sec_login_events(is_suspicious) WHERE is_suspicious=TRUE;
        """, "sec_login_events"),

        ("""
        CREATE TABLE IF NOT EXISTS sec_security_alerts (
            id              BIGSERIAL PRIMARY KEY,
            alert_type      VARCHAR(40) NOT NULL,
            severity        VARCHAR(10) NOT NULL DEFAULT 'medium',
            title           VARCHAR(200) NOT NULL,
            description     TEXT DEFAULT '',
            affected_user_id BIGINT REFERENCES auth_user(id),
            ip_address      INET,
            related_data    JSONB DEFAULT '{}',
            status          VARCHAR(20) DEFAULT 'open',
            acknowledged_by_id BIGINT REFERENCES auth_user(id),
            acknowledged_at TIMESTAMPTZ,
            resolved_at     TIMESTAMPTZ,
            auto_blocked    BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_security_alerts IS
            'Alert keamanan: brute force, unusual location, mass download, privilege escalation.';
        CREATE INDEX IF NOT EXISTS idx_sec_alert_type ON sec_security_alerts(alert_type);
        CREATE INDEX IF NOT EXISTS idx_sec_alert_sev  ON sec_security_alerts(severity);
        CREATE INDEX IF NOT EXISTS idx_sec_alert_date ON sec_security_alerts(created_at DESC);
        """, "sec_security_alerts"),

        ("""
        CREATE TABLE IF NOT EXISTS sec_ip_whitelist (
            id              BIGSERIAL PRIMARY KEY,
            ip_address      INET NOT NULL,
            ip_range        VARCHAR(20) DEFAULT '',
            label           VARCHAR(100) NOT NULL DEFAULT '',
            is_active       BOOLEAN DEFAULT TRUE,
            added_by_id     BIGINT REFERENCES auth_user(id),
            expires_at      DATE,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_ip_whitelist IS
            'IP yang di-whitelist untuk akses admin/API tanpa rate limit.';
        """, "sec_ip_whitelist"),

        ("""
        CREATE TABLE IF NOT EXISTS sec_device_registry (
            id              BIGSERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL REFERENCES auth_user(id),
            device_id       VARCHAR(64) UNIQUE NOT NULL,
            device_name     VARCHAR(100) DEFAULT '',
            device_type     VARCHAR(20) DEFAULT 'mobile',
            os              VARCHAR(30) DEFAULT '',
            browser         VARCHAR(30) DEFAULT '',
            is_trusted      BOOLEAN DEFAULT FALSE,
            is_active       BOOLEAN DEFAULT TRUE,
            first_seen_at   TIMESTAMPTZ DEFAULT NOW(),
            last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
            last_ip         INET,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE sec_device_registry IS
            'Device yang pernah dipakai login per user. Basis MFA dan suspicious login detection.';
        CREATE INDEX IF NOT EXISTS idx_device_user ON sec_device_registry(user_id);
        """, "sec_device_registry"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    user_ids = CTX["user_ids"]
    admin_id = CTX["admin_id"]
    days_range = (today - CTX["min_date"]).days

    IPS = [f"{RNG.randint(1,223)}.{RNG.randint(0,255)}.{RNG.randint(0,255)}.{RNG.randint(1,254)}"
           for _ in range(100)]
    INTERNAL_IPS = [f"10.0.{RNG.randint(0,5)}.{RNG.randint(1,254)}" for _ in range(20)]
    UAS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit LumraPOS/3.2",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
        "LumraManager/2.1 (Android 14; Samsung Galaxy)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14) Safari/17",
        "LumraInventory/1.5 (Sunmi T2 Pro)",
    ]

    # Login Events
    login_rows = []
    for _ in range(30000):
        uid    = RNG.choice(user_ids) if user_ids else admin_id
        etype  = RNG.choices(
            ["login_success","login_success","login_success","login_failed","logout","password_reset"],
            weights=[60, 0, 0, 20, 15, 5]
        )[0]
        is_sus = etype == "login_failed" and RNG.random() < 0.3
        created= datetime.now() - timedelta(
            days=RNG.randint(0, days_range), hours=RNG.randint(0, 23)
        )
        login_rows.append((
            uid if etype != "login_failed" else None,
            f"user_{uid}" if uid else "unknown",
            etype,
            RNG.choice(IPS + INTERNAL_IPS),
            RNG.choice(UAS),
            rand_hex(16),
            RNG.choice(["Bandung, ID","Jakarta, ID","Unknown","Surabaya, ID",""]),
            is_sus,
            "" if etype != "login_failed" else RNG.choice(["wrong_password","account_locked","ip_blocked"]),
            rand_hex(8), created
        ))

    if dry_run:
        log(f"[DRY RUN] login events, security alerts, IP whitelist, device registry")
        return

    n = bulk_insert("sec_login_events",
        ["user_id","username_attempt","event_type","ip_address","user_agent",
         "device_fingerprint","location_hint","is_suspicious","failure_reason",
         "session_id","created_at"],
        login_rows, batch=3000)
    ok(f"Login events: {n:,}")

    # Security Alerts
    ALERT_TYPES = ["brute_force","unusual_location","mass_data_export",
                   "privilege_escalation","api_abuse","account_takeover"]
    SEVERITIES  = ["low","medium","high","critical"]
    alert_rows  = []
    for _ in range(200):
        atype   = RNG.choice(ALERT_TYPES)
        sev     = RNG.choices(SEVERITIES, weights=[30,40,20,10])[0]
        created = datetime.now() - timedelta(days=RNG.randint(0, 90))
        status  = RNG.choices(["open","acknowledged","resolved"],weights=[30,30,40])[0]
        uid     = RNG.choice(user_ids) if user_ids else admin_id
        alert_rows.append((
            atype, sev,
            f"[{sev.upper()}] {atype.replace('_',' ').title()} detected",
            f"Suspicious activity detected from IP {RNG.choice(IPS)}",
            uid,
            RNG.choice(IPS),
            json.dumps({"attempts": RNG.randint(5, 50), "ip": RNG.choice(IPS)}),
            status,
            admin_id if status != "open" else None,
            created + timedelta(hours=2) if status != "open" else None,
            created + timedelta(hours=24) if status == "resolved" else None,
            sev == "critical" and RNG.random() < 0.5,
            created
        ))

    n = bulk_insert("sec_security_alerts",
        ["alert_type","severity","title","description","affected_user_id","ip_address",
         "related_data","status","acknowledged_by_id","acknowledged_at","resolved_at",
         "auto_blocked","created_at"],
        alert_rows)
    ok(f"Security alerts: {n}")

    # IP Whitelist
    wl_rows = [(ip, "", f"Internal Network {i}", True, admin_id, None, "", datetime.now())
               for i, ip in enumerate(INTERNAL_IPS)]
    n = bulk_insert("sec_ip_whitelist",
        ["ip_address","ip_range","label","is_active","added_by_id","expires_at","notes","created_at"],
        wl_rows)
    ok(f"IP whitelist: {n}")

    # Device Registry
    dev_rows = []
    DEVICES   = ["mobile","mobile","tablet","desktop","pos_terminal"]
    OS_LIST   = ["iOS 17","Android 14","Android 13","Windows 11","macOS 14","HarmonyOS 4"]
    BROWSERS  = ["LumraPOS","Chrome","Safari","Firefox","LumraManager"]
    for uid in user_ids:
        for _ in range(RNG.randint(1, 4)):
            dev_rows.append((
                uid, rand_hex(16),
                RNG.choice(["iPhone 15","Samsung S24","Sunmi T2","MacBook Pro","iPad Air"]),
                RNG.choice(DEVICES),
                RNG.choice(OS_LIST), RNG.choice(BROWSERS),
                RNG.random() < 0.7, True,
                datetime.now() - timedelta(days=RNG.randint(30, 365)),
                datetime.now() - timedelta(hours=RNG.randint(0, 72)),
                RNG.choice(INTERNAL_IPS),
                datetime.now() - timedelta(days=RNG.randint(30, 365))
            ))

    n = bulk_insert("sec_device_registry",
        ["user_id","device_id","device_name","device_type","os","browser",
         "is_trusted","is_active","first_seen_at","last_seen_at","last_ip","created_at"],
        dev_rows, on_conflict="ON CONFLICT (device_id) DO NOTHING")
    ok(f"Device registry: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 25 — RECIPE MANAGEMENT V2
# ═══════════════════════════════════════════════════════════════════════════════

def fill_recipe_mgmt(dry_run=False):
    head("MODUL 25 — RECIPE MANAGEMENT V2 (Versions, Costing, Yield Tests)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS recipe_v2 (
            id              BIGSERIAL PRIMARY KEY,
            code            VARCHAR(30) UNIQUE NOT NULL,
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            name            VARCHAR(150) NOT NULL,
            version         SMALLINT DEFAULT 1,
            category        VARCHAR(40) DEFAULT 'beverage',
            serving_size    NUMERIC(8,2) DEFAULT 1,
            serving_unit    VARCHAR(20) DEFAULT 'cup',
            preparation_time_min INT DEFAULT 5,
            is_current      BOOLEAN DEFAULT TRUE,
            is_active       BOOLEAN DEFAULT TRUE,
            approved_by_id  BIGINT REFERENCES auth_user(id),
            approved_at     TIMESTAMPTZ,
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_v2 IS
            'Resep produk dengan versioning. is_current=True = versi aktif dipakai barista.';
        CREATE INDEX IF NOT EXISTS idx_recipe_variant ON recipe_v2(variant_id);
        CREATE INDEX IF NOT EXISTS idx_recipe_current ON recipe_v2(is_current) WHERE is_current=TRUE;
        """, "recipe_v2"),

        ("""
        CREATE TABLE IF NOT EXISTS recipe_v2_ingredients (
            id              BIGSERIAL PRIMARY KEY,
            recipe_id       BIGINT NOT NULL REFERENCES recipe_v2(id),
            variant_id      BIGINT REFERENCES lumra_config_productvariants(id),
            ingredient_name VARCHAR(100) NOT NULL DEFAULT '',
            quantity        NUMERIC(10,3) NOT NULL,
            unit            VARCHAR(20) NOT NULL DEFAULT 'gram',
            preparation     VARCHAR(50) DEFAULT '',
            is_optional     BOOLEAN DEFAULT FALSE,
            sort_order      INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_v2_ingredients IS
            'Bahan-bahan per resep dengan kuantitas spesifik.';
        CREATE INDEX IF NOT EXISTS idx_ri_recipe ON recipe_v2_ingredients(recipe_id);
        """, "recipe_v2_ingredients"),

        ("""
        CREATE TABLE IF NOT EXISTS recipe_costing (
            id              BIGSERIAL PRIMARY KEY,
            recipe_id       BIGINT NOT NULL UNIQUE REFERENCES recipe_v2(id),
            total_ingredient_cost NUMERIC(12,2) DEFAULT 0,
            packaging_cost  NUMERIC(10,2) DEFAULT 0,
            labor_cost_allocation NUMERIC(10,2) DEFAULT 0,
            overhead_allocation   NUMERIC(10,2) DEFAULT 0,
            total_cogs      NUMERIC(12,2) DEFAULT 0,
            selling_price   NUMERIC(12,2) DEFAULT 0,
            gross_margin    NUMERIC(12,2) DEFAULT 0,
            margin_pct      NUMERIC(6,2) DEFAULT 0,
            break_even_qty  INT DEFAULT 0,
            costed_at       TIMESTAMPTZ DEFAULT NOW(),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_costing IS
            'Kalkulasi COGS per resep. Dasar penetapan harga jual.';
        """, "recipe_costing"),

        ("""
        CREATE TABLE IF NOT EXISTS recipe_yield_tests (
            id              BIGSERIAL PRIMARY KEY,
            recipe_id       BIGINT NOT NULL REFERENCES recipe_v2(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            tester_id       BIGINT REFERENCES auth_user(id),
            test_date       DATE NOT NULL,
            batch_size      INT DEFAULT 1,
            expected_output NUMERIC(10,3) DEFAULT 0,
            actual_output   NUMERIC(10,3) DEFAULT 0,
            yield_pct       NUMERIC(5,2) DEFAULT 0,
            quality_score   SMALLINT DEFAULT 5 CHECK(quality_score BETWEEN 1 AND 10),
            taste_notes     TEXT DEFAULT '',
            visual_notes    TEXT DEFAULT '',
            adjustments     TEXT DEFAULT '',
            passed          BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE recipe_yield_tests IS
            'Uji yield/konsistensi resep. Dilakukan saat recipe baru atau ada update bahan.';
        """, "recipe_yield_tests"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    variant_ids  = CTX["variant_ids"]
    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    CATEGORIES   = ["beverage_hot","beverage_cold","beverage_specialty","food_pastry","food_savory","food_dessert"]
    SERVING_UNITS= ["cup","glass","bowl","plate","piece","portion"]
    INGREDIENTS_POOL = [
        ("Espresso Shot",   "ml",  20,  40),
        ("Whole Milk",      "ml",  100, 250),
        ("Oat Milk",        "ml",  100, 250),
        ("Simple Syrup",    "ml",  10,  30),
        ("Ice",             "gram",100, 250),
        ("Coffee Beans",    "gram",18,  22),
        ("Chocolate Powder","gram",15,  25),
        ("Vanilla Extract", "ml",  2,   5),
        ("Caramel Sauce",   "ml",  10,  20),
        ("Whipped Cream",   "gram",20,  40),
        ("Cold Brew",       "ml",  150, 200),
        ("Matcha Powder",   "gram",3,   6),
        ("Sugar",           "gram",5,   15),
        ("Salt",            "gram",0.5, 1),
        ("Flour",           "gram",100, 200),
        ("Butter",          "gram",50,  100),
        ("Eggs",            "pcs", 1,   3),
        ("Heavy Cream",     "ml",  50,  100),
    ]

    recipe_rows = []
    recipe_ctr  = 1
    for i, vid in enumerate(RNG.sample(variant_ids, min(100, len(variant_ids)))):
        cat = RNG.choice(CATEGORIES)
        version = RNG.randint(1, 3)
        for v in range(1, version + 1):
            is_current = (v == version)
            recipe_rows.append((
                f"RCP-{recipe_ctr:04d}", vid,
                f"Recipe #{recipe_ctr} v{v}",
                v, cat,
                Decimal(str(RNG.choice([1, 2]))),
                RNG.choice(SERVING_UNITS),
                RNG.randint(3, 15),
                is_current, True,
                admin_id,
                datetime.now() - timedelta(days=RNG.randint(0, 180)),
                "", datetime.now(), datetime.now()
            ))
            recipe_ctr += 1

    if dry_run:
        log(f"[DRY RUN] {len(recipe_rows)} recipes + ingredients + costing + yield tests")
        return

    n = bulk_insert("recipe_v2",
        ["code","variant_id","name","version","category","serving_size","serving_unit",
         "preparation_time_min","is_current","is_active","approved_by_id","approved_at",
         "notes","created_at","updated_at"],
        recipe_rows, on_conflict="ON CONFLICT (code) DO NOTHING")
    ok(f"Recipes v2: {n:,}")

    # Ingredients
    rcp_ids   = [r[0] for r in q("SELECT id FROM recipe_v2 ORDER BY id")]
    ingr_rows = []
    for rid in rcp_ids:
        n_ingr = RNG.randint(3, 8)
        for i, (iname, unit, qmin, qmax) in enumerate(RNG.sample(INGREDIENTS_POOL, min(n_ingr, len(INGREDIENTS_POOL)))):
            qty = Decimal(str(round(RNG.uniform(qmin, qmax), 1)))
            ingr_rows.append((
                rid, None, iname, qty, unit,
                RNG.choice(["","freshly brewed","chilled","heated","steamed"]),
                RNG.random() < 0.1, i, datetime.now()
            ))

    n = bulk_insert("recipe_v2_ingredients",
        ["recipe_id","variant_id","ingredient_name","quantity","unit",
         "preparation","is_optional","sort_order","created_at"],
        ingr_rows, batch=3000)
    ok(f"Recipe ingredients: {n:,}")

    # Costing
    cost_rows = []
    for rid in rcp_ids:
        ingr_cost  = Decimal(str(RNG.randint(3000, 25000)))
        pkg_cost   = Decimal(str(RNG.randint(500, 3000)))
        labor      = Decimal(str(RNG.randint(500, 2000)))
        overhead   = Decimal(str(RNG.randint(500, 3000)))
        total_cogs = ingr_cost + pkg_cost + labor + overhead
        sell_price = total_cogs * Decimal(str(round(RNG.uniform(2.5, 4.5), 1)))
        margin     = sell_price - total_cogs
        margin_pct = (margin / sell_price * 100).quantize(Decimal("0.01")) if sell_price > 0 else Decimal("0")
        bep        = int(1000000 / float(margin)) if float(margin) > 0 else 999
        cost_rows.append((
            rid, ingr_cost, pkg_cost, labor, overhead,
            total_cogs, sell_price.quantize(Decimal("0.01")),
            margin.quantize(Decimal("0.01")), margin_pct, bep,
            datetime.now(), datetime.now()
        ))

    n = bulk_insert("recipe_costing",
        ["recipe_id","total_ingredient_cost","packaging_cost","labor_cost_allocation",
         "overhead_allocation","total_cogs","selling_price","gross_margin","margin_pct",
         "break_even_qty","costed_at","created_at"],
        cost_rows, on_conflict="ON CONFLICT (recipe_id) DO NOTHING")
    ok(f"Recipe costing: {n:,}")

    # Yield Tests
    yt_rows = []
    for rid in RNG.sample(rcp_ids, min(len(rcp_ids), 200)):
        for _ in range(RNG.randint(1, 5)):
            expected = Decimal(str(RNG.randint(200, 400)))
            actual   = expected * Decimal(str(round(RNG.uniform(0.88, 1.02), 2)))
            yld_pct  = (actual / expected * 100).quantize(Decimal("0.01"))
            yt_rows.append((
                rid, RNG.choice(location_ids),
                RNG.choice(user_ids) if user_ids else admin_id,
                today - timedelta(days=RNG.randint(0, 180)),
                RNG.randint(3, 20),
                expected, actual.quantize(Decimal("0.001")),
                yld_pct,
                RNG.randint(6, 10),
                RNG.choice(["Balance baik","Perlu sedikit adjustment","Rasa konsisten",""]),
                "","",
                float(yld_pct) >= 90,
                datetime.now()
            ))

    n = bulk_insert("recipe_yield_tests",
        ["recipe_id","location_id","tester_id","test_date","batch_size",
         "expected_output","actual_output","yield_pct","quality_score",
         "taste_notes","visual_notes","adjustments","passed","created_at"],
        yt_rows)
    ok(f"Yield tests: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 26 — EVENTS CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

def fill_events_calendar(dry_run=False):
    head("MODUL 26 — EVENTS CALENDAR (Events, Registrations, Revenue)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS events_calendar (
            id              BIGSERIAL PRIMARY KEY,
            event_code      VARCHAR(30) UNIQUE NOT NULL,
            title           VARCHAR(200) NOT NULL,
            description     TEXT DEFAULT '',
            event_type      VARCHAR(30) DEFAULT 'tasting',
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            start_datetime  TIMESTAMPTZ NOT NULL,
            end_datetime    TIMESTAMPTZ NOT NULL,
            capacity        INT DEFAULT 0,
            registered_count INT DEFAULT 0,
            ticket_price    NUMERIC(10,2) DEFAULT 0,
            is_free         BOOLEAN DEFAULT FALSE,
            status          VARCHAR(20) DEFAULT 'upcoming',
            host_name       VARCHAR(100) DEFAULT '',
            banner_url      VARCHAR(500) DEFAULT '',
            is_published    BOOLEAN DEFAULT FALSE,
            created_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE events_calendar IS
            'Event Kafe Nusantara: cupping session, live music, workshop barista, launching menu.';
        CREATE INDEX IF NOT EXISTS idx_evt_location ON events_calendar(location_id);
        CREATE INDEX IF NOT EXISTS idx_evt_date     ON events_calendar(start_datetime);
        CREATE INDEX IF NOT EXISTS idx_evt_status   ON events_calendar(status);
        """, "events_calendar"),

        ("""
        CREATE TABLE IF NOT EXISTS event_registrations (
            id              BIGSERIAL PRIMARY KEY,
            event_id        BIGINT NOT NULL REFERENCES events_calendar(id),
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            registrant_name VARCHAR(100) NOT NULL DEFAULT '',
            registrant_phone VARCHAR(20) DEFAULT '',
            registrant_email VARCHAR(100) DEFAULT '',
            ticket_qty      INT DEFAULT 1,
            total_paid      NUMERIC(10,2) DEFAULT 0,
            payment_method  VARCHAR(20) DEFAULT 'transfer',
            payment_status  VARCHAR(20) DEFAULT 'paid',
            attendance_status VARCHAR(20) DEFAULT 'registered',
            check_in_at     TIMESTAMPTZ,
            qr_code         VARCHAR(40) DEFAULT '',
            notes           TEXT DEFAULT '',
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE event_registrations IS
            'Pendaftaran peserta event. QR code untuk check-in di pintu masuk.';
        CREATE INDEX IF NOT EXISTS idx_evtreg_event ON event_registrations(event_id);
        CREATE INDEX IF NOT EXISTS idx_evtreg_cust  ON event_registrations(customer_id);
        """, "event_registrations"),

        ("""
        CREATE TABLE IF NOT EXISTS event_revenue_summary (
            id              BIGSERIAL PRIMARY KEY,
            event_id        BIGINT NOT NULL UNIQUE REFERENCES events_calendar(id),
            total_registered INT DEFAULT 0,
            total_attended  INT DEFAULT 0,
            gross_revenue   NUMERIC(12,2) DEFAULT 0,
            refund_amount   NUMERIC(10,2) DEFAULT 0,
            net_revenue     NUMERIC(12,2) DEFAULT 0,
            avg_ticket_price NUMERIC(10,2) DEFAULT 0,
            venue_cost      NUMERIC(10,2) DEFAULT 0,
            host_fee        NUMERIC(10,2) DEFAULT 0,
            marketing_cost  NUMERIC(10,2) DEFAULT 0,
            net_profit      NUMERIC(12,2) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE event_revenue_summary IS 'Ringkasan pendapatan dan biaya per event.';
        """, "event_revenue_summary"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    customer_ids = CTX["customer_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]

    EVENT_TYPES  = ["cupping_session","barista_workshop","live_music","menu_launching",
                    "coffee_talk","latte_art_class","seasonal_launch","community_gathering"]
    HOSTS        = ["Rizky - Head Barista","Dimas - Coffee Educator","Tia - Barista Champion",
                    "Andi - Coffee Roaster","Sari - Culinary Director","Guest: World Barista Champion"]

    evt_rows = []
    days_range = (today - CTX["min_date"]).days
    for i in range(120):
        start_date  = CTX["min_date"] + timedelta(days=RNG.randint(0, days_range + 60))
        start_dt    = datetime.combine(start_date, dtime(RNG.randint(9, 19), 0))
        end_dt      = start_dt + timedelta(hours=RNG.randint(2, 4))
        status      = ("completed" if end_dt < datetime.now() else
                       "ongoing"   if start_dt <= datetime.now() <= end_dt else
                       "upcoming")
        is_free     = RNG.random() < 0.2
        ticket_price= Decimal("0") if is_free else Decimal(str(RNG.randint(50000, 350000)))
        capacity    = RNG.randint(10, 60)
        registered  = RNG.randint(0, capacity) if status in ("completed","ongoing") else RNG.randint(0, capacity)
        evt_rows.append((
            f"EVT-{i+1:04d}",
            f"{RNG.choice(EVENT_TYPES).replace('_',' ').title()} #{i+1}",
            "Bergabunglah dalam pengalaman kopi yang tak terlupakan.",
            RNG.choice(EVENT_TYPES),
            RNG.choice(location_ids),
            start_dt, end_dt,
            capacity, registered,
            ticket_price, is_free, status,
            RNG.choice(HOSTS), "", True,
            RNG.choice(user_ids) if user_ids else admin_id,
            datetime.now(), datetime.now()
        ))

    if dry_run:
        log(f"[DRY RUN] {len(evt_rows)} events + registrations + revenue summary")
        return

    n = bulk_insert("events_calendar",
        ["event_code","title","description","event_type","location_id",
         "start_datetime","end_datetime","capacity","registered_count","ticket_price",
         "is_free","status","host_name","banner_url","is_published","created_by_id",
         "created_at","updated_at"],
        evt_rows, on_conflict="ON CONFLICT (event_code) DO NOTHING")
    ok(f"Events: {n}")

    # Registrations
    evt_data  = q("SELECT id, capacity, ticket_price, is_free, registered_count FROM events_calendar ORDER BY id")
    reg_rows  = []
    for eid, cap, ticket_price, is_free, registered in evt_data:
        n_reg = registered if registered else RNG.randint(0, min(cap, 30))
        for _ in range(n_reg):
            cid = RNG.choice(customer_ids) if RNG.random() < 0.7 else None
            qty = RNG.randint(1, 2)
            paid = Decimal("0") if is_free else Decimal(str(ticket_price or 0)) * qty
            attended = RNG.random() < 0.85
            reg_rows.append((
                eid, cid,
                f"Peserta {RNG.randint(1000,9999)}",
                f"08{RNG.randint(100000000,999999999)}",
                f"peserta{RNG.randint(1000,9999)}@email.com",
                qty, paid.quantize(Decimal("0.01")),
                RNG.choice(["transfer","qris","cash"]),
                "paid", "attended" if attended else "registered",
                datetime.now() - timedelta(hours=RNG.randint(1, 48)) if attended else None,
                rand_hex(8), "", datetime.now()
            ))

    n = bulk_insert("event_registrations",
        ["event_id","customer_id","registrant_name","registrant_phone","registrant_email",
         "ticket_qty","total_paid","payment_method","payment_status","attendance_status",
         "check_in_at","qr_code","notes","created_at"],
        reg_rows, batch=3000)
    ok(f"Event registrations: {n:,}")

    # Revenue Summary
    rev_rows = []
    for eid, cap, ticket_price, is_free, registered in evt_data:
        n_attended = int((registered or 0) * RNG.uniform(0.7, 0.95))
        gross      = Decimal(str(ticket_price or 0)) * registered if not is_free else Decimal("0")
        refund     = gross * Decimal("0.05") if RNG.random() < 0.1 else Decimal("0")
        net_rev    = gross - refund
        venue      = Decimal(str(RNG.randint(500000, 3000000)))
        host_fee   = Decimal(str(RNG.randint(200000, 1500000)))
        marketing  = Decimal(str(RNG.randint(100000, 500000)))
        net_profit = net_rev - venue - host_fee - marketing
        rev_rows.append((
            eid, registered or 0, n_attended,
            gross.quantize(Decimal("0.01")),
            refund.quantize(Decimal("0.01")),
            net_rev.quantize(Decimal("0.01")),
            Decimal(str(ticket_price or 0)),
            venue, host_fee, marketing,
            net_profit.quantize(Decimal("0.01")),
            datetime.now()
        ))

    n = bulk_insert("event_revenue_summary",
        ["event_id","total_registered","total_attended","gross_revenue","refund_amount",
         "net_revenue","avg_ticket_price","venue_cost","host_fee","marketing_cost",
         "net_profit","created_at"],
        rev_rows, on_conflict="ON CONFLICT (event_id) DO NOTHING")
    ok(f"Event revenue summary: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 27 — CUSTOMER SUPPORT (Tickets, SLA, Escalations)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_customer_support(dry_run=False):
    head("MODUL 27 — CUSTOMER SUPPORT (Tickets, Messages, SLA, Escalations)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS cs_sla_configs (
            id              BIGSERIAL PRIMARY KEY,
            priority        VARCHAR(10) UNIQUE NOT NULL,
            first_response_hours  INT NOT NULL DEFAULT 24,
            resolution_hours      INT NOT NULL DEFAULT 72,
            escalation_hours      INT NOT NULL DEFAULT 48,
            applies_to_categories TEXT[] DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_sla_configs IS 'Konfigurasi SLA per prioritas ticket.';
        """, "cs_sla_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS cs_tickets (
            id              BIGSERIAL PRIMARY KEY,
            ticket_number   VARCHAR(20) UNIQUE NOT NULL,
            customer_id     BIGINT REFERENCES lumra_config_customers(id),
            order_id        BIGINT REFERENCES lumra_config_orders(id),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            channel         VARCHAR(20) DEFAULT 'app',
            category        VARCHAR(30) NOT NULL DEFAULT 'general',
            subcategory     VARCHAR(50) DEFAULT '',
            priority        VARCHAR(10) DEFAULT 'normal',
            status          VARCHAR(20) DEFAULT 'open',
            subject         VARCHAR(200) NOT NULL,
            description     TEXT NOT NULL DEFAULT '',
            assigned_to_id  BIGINT REFERENCES auth_user(id),
            first_response_at TIMESTAMPTZ,
            resolved_at     TIMESTAMPTZ,
            closed_at       TIMESTAMPTZ,
            sla_breached    BOOLEAN DEFAULT FALSE,
            satisfaction_score SMALLINT CHECK(satisfaction_score BETWEEN 1 AND 5),
            tags            TEXT[] DEFAULT '{}',
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_tickets IS
            'Tiket support customer. Channel: app, whatsapp, email, walk_in, social_media.
            Category: product_quality, order_issue, payment, loyalty, complaint, suggestion.';
        CREATE INDEX IF NOT EXISTS idx_ticket_status   ON cs_tickets(status);
        CREATE INDEX IF NOT EXISTS idx_ticket_customer ON cs_tickets(customer_id);
        CREATE INDEX IF NOT EXISTS idx_ticket_priority ON cs_tickets(priority);
        CREATE INDEX IF NOT EXISTS idx_ticket_date     ON cs_tickets(created_at DESC);
        """, "cs_tickets"),

        ("""
        CREATE TABLE IF NOT EXISTS cs_ticket_messages (
            id              BIGSERIAL PRIMARY KEY,
            ticket_id       BIGINT NOT NULL REFERENCES cs_tickets(id),
            sender_type     VARCHAR(10) NOT NULL DEFAULT 'customer',
            sender_id       BIGINT REFERENCES auth_user(id),
            message         TEXT NOT NULL,
            attachments     JSONB DEFAULT '[]',
            is_internal     BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_ticket_messages IS
            'Pesan dalam tiket. sender_type: customer, agent, system. is_internal=True = catatan internal agent.';
        CREATE INDEX IF NOT EXISTS idx_tm_ticket ON cs_ticket_messages(ticket_id);
        CREATE INDEX IF NOT EXISTS idx_tm_date   ON cs_ticket_messages(created_at);
        """, "cs_ticket_messages"),

        ("""
        CREATE TABLE IF NOT EXISTS cs_escalations (
            id              BIGSERIAL PRIMARY KEY,
            ticket_id       BIGINT NOT NULL REFERENCES cs_tickets(id),
            from_agent_id   BIGINT REFERENCES auth_user(id),
            to_agent_id     BIGINT REFERENCES auth_user(id),
            escalation_type VARCHAR(20) DEFAULT 'priority',
            reason          TEXT NOT NULL DEFAULT '',
            new_priority    VARCHAR(10),
            resolved        BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cs_escalations IS 'Log eskalasi tiket ke agent atau supervisor yang lebih senior.';
        """, "cs_escalations"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    # SLA Configs
    sla_data = [
        ("critical", 1,   4,   2),
        ("high",     4,   24,  12),
        ("normal",   8,   48,  24),
        ("low",      24,  120, 72),
    ]
    sla_rows = [(p, fr, res, esc, [], True, datetime.now()) for p, fr, res, esc in sla_data]

    if dry_run:
        log(f"[DRY RUN] SLA configs + tickets + messages + escalations")
        return

    n = bulk_insert("cs_sla_configs",
        ["priority","first_response_hours","resolution_hours","escalation_hours",
         "applies_to_categories","is_active","created_at"],
        sla_rows, on_conflict="ON CONFLICT (priority) DO NOTHING")
    ok(f"SLA configs: {n}")

    customer_ids = CTX["customer_ids"]
    order_ids    = CTX["order_ids"]
    location_ids = CTX["location_ids"]
    user_ids     = CTX["user_ids"]
    admin_id     = CTX["admin_id"]
    days_range   = (today - CTX["min_date"]).days

    CATEGORIES = ["product_quality","order_issue","payment","loyalty","complaint","suggestion","other"]
    CHANNELS   = ["app","whatsapp","email","walk_in","social_media"]
    PRIORITIES = ["low","normal","normal","normal","high","critical"]
    SUBJECTS   = [
        "Pesanan saya salah","Kopi terasa pahit","Promo tidak berfungsi",
        "Stamp tidak bertambah","Refund request","Keluhan kebersihan",
        "Saran menu baru","Barista tidak ramah","Harga tidak sesuai",
        "Aplikasi error","Wi-Fi tidak ada","Tempat duduk kurang",
        "Compliment untuk barista","Request khusus untuk event",
    ]

    ticket_rows = []
    for i in range(5000):
        created = datetime.now() - timedelta(
            days=RNG.randint(0, days_range), hours=RNG.randint(0, 23)
        )
        priority = RNG.choice(PRIORITIES)
        status   = RNG.choices(["open","in_progress","resolved","closed","pending_customer"],
                               weights=[15, 25, 30, 25, 5])[0]
        resolved_at = created + timedelta(hours=RNG.randint(2, 96)) \
                      if status in ("resolved","closed") else None
        sla_breached= resolved_at and (resolved_at - created).total_seconds() > 48*3600
        ticket_rows.append((
            f"TKT-{i+1:06d}",
            RNG.choice(customer_ids),
            RNG.choice(order_ids) if RNG.random() < 0.4 and order_ids else None,
            RNG.choice(location_ids),
            RNG.choice(CHANNELS),
            RNG.choice(CATEGORIES), "",
            priority, status,
            RNG.choice(SUBJECTS),
            "Detail keluhan dari customer.",
            RNG.choice(user_ids) if user_ids else admin_id,
            created + timedelta(hours=RNG.randint(0, 4)) if status != "open" else None,
            resolved_at, resolved_at,
            bool(sla_breached),
            RNG.randint(3, 5) if status == "closed" else None,
            json.dumps([]),
            created, created
        ))

    n = bulk_insert("cs_tickets",
        ["ticket_number","customer_id","order_id","location_id","channel",
         "category","subcategory","priority","status","subject","description",
         "assigned_to_id","first_response_at","resolved_at","closed_at",
         "sla_breached","satisfaction_score","tags","created_at","updated_at"],
        ticket_rows, batch=3000,
        on_conflict="ON CONFLICT (ticket_number) DO NOTHING")
    ok(f"Tickets: {n:,}")

    # Messages
    ticket_ids = [r[0] for r in q("SELECT id FROM cs_tickets ORDER BY id")]
    msg_rows   = []
    CUST_MSGS  = [
        "Saya ingin melaporkan pesanan yang tidak sesuai.",
        "Kopi saya terasa berbeda dari biasanya.",
        "Stamp saya tidak bertambah setelah transaksi.",
        "Apakah promo ini masih berlaku?",
        "Terima kasih atas penanganannya!",
    ]
    AGENT_MSGS = [
        "Halo, terima kasih sudah menghubungi Kafe Nusantara. Kami sedang meninjau laporan Anda.",
        "Kami mohon maaf atas ketidaknyamanan ini. Tim kami sedang menyelidiki masalah tersebut.",
        "Stamp Anda sudah kami tambahkan secara manual. Mohon maaf atas ketidaknyamanan ini.",
        "Promo tersebut masih berlaku hingga akhir bulan. Ada yang bisa kami bantu lagi?",
        "Masalah sudah berhasil diselesaikan. Terima kasih atas kesabaran Anda!",
    ]

    for tid in ticket_ids:
        n_msg = RNG.randint(2, 8)
        for j in range(n_msg):
            is_agent = j % 2 == 1
            msg_rows.append((
                tid,
                "agent" if is_agent else "customer",
                RNG.choice(user_ids) if is_agent and user_ids else None,
                RNG.choice(AGENT_MSGS if is_agent else CUST_MSGS),
                json.dumps([]),
                RNG.random() < 0.1 and is_agent,
                datetime.now() - timedelta(days=RNG.randint(0, 30))
            ))

    n = bulk_insert("cs_ticket_messages",
        ["ticket_id","sender_type","sender_id","message","attachments","is_internal","created_at"],
        msg_rows, batch=3000)
    ok(f"Ticket messages: {n:,}")

    # Escalations
    esc_rows = []
    for tid in RNG.sample(ticket_ids, min(300, len(ticket_ids))):
        if RNG.random() < 0.3:
            esc_rows.append((
                tid,
                RNG.choice(user_ids) if user_ids else admin_id,
                admin_id,
                RNG.choice(["priority","department","manager"]),
                "SLA terancam breach. Perlu penanganan segera.",
                "high", RNG.random() < 0.6,
                datetime.now() - timedelta(days=RNG.randint(0, 30))
            ))

    n = bulk_insert("cs_escalations",
        ["ticket_id","from_agent_id","to_agent_id","escalation_type","reason",
         "new_priority","resolved","created_at"],
        esc_rows)
    ok(f"Escalations: {n}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 28 — ANALYTICS CUBE (Pre-aggregated OLAP)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_analytics_cube(dry_run=False):
    head("MODUL 28 — ANALYTICS CUBE (Hourly, Cohort, Funnel, Retention)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS analytics_hourly_sales (
            id              BIGSERIAL PRIMARY KEY,
            sale_date       DATE NOT NULL,
            sale_hour       SMALLINT NOT NULL CHECK(sale_hour BETWEEN 0 AND 23),
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            shift_type      VARCHAR(20) DEFAULT '',
            total_orders    INT DEFAULT 0,
            total_revenue   NUMERIC(15,2) DEFAULT 0,
            avg_order_value NUMERIC(12,2) DEFAULT 0,
            new_customers   INT DEFAULT 0,
            promo_orders    INT DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(sale_date, sale_hour, location_id)
        );
        COMMENT ON TABLE analytics_hourly_sales IS
            'Agregasi penjualan per jam per outpost. Untuk heatmap dan peak hour analysis.';
        CREATE INDEX IF NOT EXISTS idx_hs_date ON analytics_hourly_sales(sale_date DESC);
        CREATE INDEX IF NOT EXISTS idx_hs_hour ON analytics_hourly_sales(sale_hour);
        """, "analytics_hourly_sales"),

        ("""
        CREATE TABLE IF NOT EXISTS analytics_customer_cohorts (
            id              BIGSERIAL PRIMARY KEY,
            cohort_month    VARCHAR(7) NOT NULL,
            period_offset   SMALLINT NOT NULL DEFAULT 0,
            cohort_size     INT DEFAULT 0,
            retained_customers INT DEFAULT 0,
            retention_rate  NUMERIC(6,3) DEFAULT 0,
            avg_orders      NUMERIC(8,3) DEFAULT 0,
            avg_revenue     NUMERIC(12,2) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(cohort_month, period_offset)
        );
        COMMENT ON TABLE analytics_customer_cohorts IS
            'Cohort retention analysis. cohort_month = bulan pertama customer order.
            period_offset = 0 (bulan pertama), 1 (1 bulan kemudian), dst.
            retention_rate = % customer yang masih aktif di periode tersebut.';
        CREATE INDEX IF NOT EXISTS idx_cohort_month ON analytics_customer_cohorts(cohort_month);
        """, "analytics_customer_cohorts"),

        ("""
        CREATE TABLE IF NOT EXISTS analytics_conversion_funnel (
            id              BIGSERIAL PRIMARY KEY,
            funnel_date     DATE NOT NULL,
            location_id     BIGINT REFERENCES lumra_config_locations(id),
            channel         VARCHAR(20) DEFAULT 'all',
            stage           VARCHAR(30) NOT NULL,
            stage_order     SMALLINT NOT NULL,
            users_count     INT DEFAULT 0,
            conversion_rate NUMERIC(6,3) DEFAULT 0,
            drop_off_rate   NUMERIC(6,3) DEFAULT 0,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(funnel_date, location_id, channel, stage)
        );
        COMMENT ON TABLE analytics_conversion_funnel IS
            'Funnel konversi: visit → browse_menu → add_to_cart → checkout → order → repeat.';
        """, "analytics_conversion_funnel"),

        ("""
        CREATE TABLE IF NOT EXISTS analytics_product_affinity (
            id              BIGSERIAL PRIMARY KEY,
            variant_a_id    BIGINT REFERENCES lumra_config_productvariants(id),
            variant_b_id    BIGINT REFERENCES lumra_config_productvariants(id),
            co_purchase_count INT DEFAULT 0,
            support_pct     NUMERIC(6,3) DEFAULT 0,
            confidence_pct  NUMERIC(6,3) DEFAULT 0,
            lift_score      NUMERIC(8,4) DEFAULT 0,
            period          VARCHAR(7) NOT NULL,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(variant_a_id, variant_b_id, period)
        );
        COMMENT ON TABLE analytics_product_affinity IS
            'Market basket analysis: produk yang sering dibeli bersama.
            Basis untuk cross-sell recommendation.';
        CREATE INDEX IF NOT EXISTS idx_affinity_lift ON analytics_product_affinity(lift_score DESC);
        CREATE INDEX IF NOT EXISTS idx_affinity_a    ON analytics_product_affinity(variant_a_id);
        """, "analytics_product_affinity"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    location_ids = CTX["location_ids"]
    variant_ids  = CTX["variant_ids"]
    min_date     = CTX["min_date"]
    days_range   = (today - min_date).days

    # Hourly Sales (simulasi dari distribusi traffic kafe)
    # Peak: 8-10 (morning), 12-14 (lunch), 17-19 (after office)
    HOUR_WEIGHTS = [0,0,0,0,0,0,1,5,15,18,12,8,12,14,10,8,10,14,12,8,5,3,2,1]
    SHIFT_MAP_H  = {h: ("first_light" if 7 <= h < 12 else
                        "midday_transit" if 12 <= h < 18 else
                        "twilight_bivouac") for h in range(24)}

    log("Generating hourly sales...")
    hs_rows = []
    for d in range(min(days_range, 730)):
        sale_date = today - timedelta(days=d)
        for lid in location_ids:
            daily_revenue = Decimal(str(RNG.randint(2000000, 20000000)))
            for hour in range(7, 23):
                weight    = HOUR_WEIGHTS[hour]
                pct       = weight / sum(HOUR_WEIGHTS[7:23])
                h_revenue = daily_revenue * Decimal(str(round(pct * RNG.uniform(0.7, 1.3), 4)))
                h_orders  = max(0, int(h_revenue / Decimal(str(RNG.randint(30000, 60000)))))
                aov       = h_revenue / h_orders if h_orders > 0 else Decimal("0")
                hs_rows.append((
                    sale_date, hour, lid,
                    SHIFT_MAP_H[hour],
                    h_orders,
                    h_revenue.quantize(Decimal("0.01")),
                    aov.quantize(Decimal("0.01")),
                    RNG.randint(0, max(1, h_orders // 10)),
                    RNG.randint(0, max(1, h_orders // 5)),
                    datetime.now()
                ))

    if dry_run:
        log(f"[DRY RUN] {len(hs_rows)} hourly rows + cohorts + funnel + affinity")
        return

    n = bulk_insert("analytics_hourly_sales",
        ["sale_date","sale_hour","location_id","shift_type","total_orders",
         "total_revenue","avg_order_value","new_customers","promo_orders","created_at"],
        hs_rows, batch=3000,
        on_conflict="ON CONFLICT (sale_date, sale_hour, location_id) DO NOTHING")
    ok(f"Hourly sales: {n:,}")

    # Cohort Analysis
    cohort_rows = []
    for mo_offset in range(24):  # 24 bulan cohort
        cohort_ref = today.replace(day=1) - timedelta(days=mo_offset * 30)
        cohort_month = cohort_ref.replace(day=1).strftime("%Y-%m")
        cohort_size  = RNG.randint(50, 500)
        for period in range(min(13, 24 - mo_offset)):  # max 12 bulan follow-up
            if period == 0:
                retained = cohort_size
                ret_rate = Decimal("100.0")
            else:
                # Retention curve: menurun dengan waktu
                base_retention = 0.7 * (0.85 ** period)
                retained = int(cohort_size * RNG.uniform(base_retention * 0.8, base_retention * 1.2))
                ret_rate = Decimal(str(round(retained / cohort_size * 100, 3)))

            cohort_rows.append((
                cohort_month, period, cohort_size, retained,
                ret_rate,
                Decimal(str(round(RNG.uniform(1.5, 4.0), 3))),
                Decimal(str(RNG.randint(50000, 250000))),
                datetime.now()
            ))

    n = bulk_insert("analytics_customer_cohorts",
        ["cohort_month","period_offset","cohort_size","retained_customers",
         "retention_rate","avg_orders","avg_revenue","created_at"],
        cohort_rows,
        on_conflict="ON CONFLICT (cohort_month, period_offset) DO NOTHING")
    ok(f"Cohort analysis: {n:,}")

    # Conversion Funnel
    FUNNEL_STAGES = [
        ("visit",        1),
        ("browse_menu",  2),
        ("add_to_cart",  3),
        ("checkout",     4),
        ("order_placed", 5),
        ("repeat_order", 6),
    ]
    CHANNELS = ["dine_in","takeaway","app"]
    fnl_rows = []
    for d in range(min(days_range, 90)):
        fdate = today - timedelta(days=d)
        for lid in location_ids:
            for channel in CHANNELS:
                base_visits = RNG.randint(50, 500)
                prev_count  = base_visits
                for stage, sorder in FUNNEL_STAGES:
                    drop = RNG.uniform(0.6, 0.95) if stage != "visit" else 1.0
                    current = int(prev_count * drop)
                    conv_rate = round(current / base_visits * 100, 3) if base_visits > 0 else 0
                    drop_rate = round((prev_count - current) / prev_count * 100, 3) if prev_count > 0 else 0
                    fnl_rows.append((
                        fdate, lid, channel, stage, sorder,
                        current, conv_rate, drop_rate, datetime.now()
                    ))
                    prev_count = current

    n = bulk_insert("analytics_conversion_funnel",
        ["funnel_date","location_id","channel","stage","stage_order",
         "users_count","conversion_rate","drop_off_rate","created_at"],
        fnl_rows, batch=3000,
        on_conflict="ON CONFLICT (funnel_date, location_id, channel, stage) DO NOTHING")
    ok(f"Conversion funnel: {n:,}")

    # Product Affinity (Market Basket)
    aff_rows = []
    sample_variants = RNG.sample(variant_ids, min(80, len(variant_ids)))
    for period_offset in range(6):
        period = (today.replace(day=1) - timedelta(days=period_offset * 30)).replace(day=1).strftime("%Y-%m")
        for i in range(len(sample_variants)):
            for j in range(i+1, min(i+10, len(sample_variants))):
                va = sample_variants[i]
                vb = sample_variants[j]
                co_count   = RNG.randint(5, 200)
                support    = round(co_count / 10000 * 100, 3)
                confidence = round(RNG.uniform(0.1, 0.8), 3)
                lift       = round(confidence / RNG.uniform(0.05, 0.3), 4)
                aff_rows.append((va, vb, co_count, support, confidence, lift, period, datetime.now()))

    n = bulk_insert("analytics_product_affinity",
        ["variant_a_id","variant_b_id","co_purchase_count","support_pct",
         "confidence_pct","lift_score","period","created_at"],
        aff_rows, batch=3000,
        on_conflict="ON CONFLICT (variant_a_id, variant_b_id, period) DO NOTHING")
    ok(f"Product affinity: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODUL 29 — CONFIG STORE (Feature Flags, App Configs, Changelog)
# ═══════════════════════════════════════════════════════════════════════════════

def fill_config_store(dry_run=False):
    head("MODUL 29 — CONFIG STORE (Feature Flags, App Configs, Location Configs, Changelog)")

    sqls = [
        ("""
        CREATE TABLE IF NOT EXISTS cfg_feature_flags (
            id              BIGSERIAL PRIMARY KEY,
            flag_key        VARCHAR(80) UNIQUE NOT NULL,
            display_name    VARCHAR(120) NOT NULL,
            description     TEXT DEFAULT '',
            flag_type       VARCHAR(20) DEFAULT 'boolean',
            default_value   JSONB NOT NULL DEFAULT 'false',
            current_value   JSONB NOT NULL DEFAULT 'false',
            rollout_pct     SMALLINT DEFAULT 100 CHECK(rollout_pct BETWEEN 0 AND 100),
            applies_to      VARCHAR(20) DEFAULT 'all',
            allowed_locations BIGINT[] DEFAULT '{}',
            allowed_tiers   TEXT[] DEFAULT '{}',
            is_active       BOOLEAN DEFAULT TRUE,
            changed_by_id   BIGINT REFERENCES auth_user(id),
            changed_at      TIMESTAMPTZ DEFAULT NOW(),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_feature_flags IS
            'Feature flags untuk A/B testing dan gradual rollout fitur baru.
            flag_type: boolean, percentage, string, json.
            applies_to: all, location, customer_tier, employee_role.';
        """, "cfg_feature_flags"),

        ("""
        CREATE TABLE IF NOT EXISTS cfg_app_configs (
            id              BIGSERIAL PRIMARY KEY,
            config_key      VARCHAR(80) UNIQUE NOT NULL,
            config_group    VARCHAR(40) NOT NULL DEFAULT 'general',
            display_name    VARCHAR(120) NOT NULL,
            value_type      VARCHAR(20) DEFAULT 'string',
            value           JSONB NOT NULL DEFAULT 'null',
            default_value   JSONB NOT NULL DEFAULT 'null',
            description     TEXT DEFAULT '',
            is_sensitive    BOOLEAN DEFAULT FALSE,
            requires_restart BOOLEAN DEFAULT FALSE,
            changed_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_app_configs IS
            'Konfigurasi aplikasi yang bisa diubah tanpa deploy. Group: general, payment, notification, loyalty, reporting.';
        CREATE INDEX IF NOT EXISTS idx_cfg_group ON cfg_app_configs(config_group);
        """, "cfg_app_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS cfg_location_configs (
            id              BIGSERIAL PRIMARY KEY,
            location_id     BIGINT NOT NULL REFERENCES lumra_config_locations(id),
            config_key      VARCHAR(80) NOT NULL,
            value           JSONB NOT NULL DEFAULT 'null',
            override_reason TEXT DEFAULT '',
            changed_by_id   BIGINT REFERENCES auth_user(id),
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(location_id, config_key)
        );
        COMMENT ON TABLE cfg_location_configs IS
            'Override konfigurasi per lokasi spesifik (contoh: jam buka, menu khusus, price list).';
        CREATE INDEX IF NOT EXISTS idx_lc_location ON cfg_location_configs(location_id);
        """, "cfg_location_configs"),

        ("""
        CREATE TABLE IF NOT EXISTS cfg_changelog (
            id              BIGSERIAL PRIMARY KEY,
            change_type     VARCHAR(30) NOT NULL,
            entity_type     VARCHAR(40) NOT NULL,
            entity_id       BIGINT,
            change_summary  VARCHAR(200) NOT NULL,
            old_value       JSONB DEFAULT '{}',
            new_value       JSONB DEFAULT '{}',
            changed_by_id   BIGINT REFERENCES auth_user(id),
            reason          TEXT DEFAULT '',
            ip_address      INET,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
        COMMENT ON TABLE cfg_changelog IS
            'Log semua perubahan konfigurasi. Immutable audit trail untuk compliance.';
        CREATE INDEX IF NOT EXISTS idx_chg_type  ON cfg_changelog(change_type);
        CREATE INDEX IF NOT EXISTS idx_chg_entity ON cfg_changelog(entity_type, entity_id);
        CREATE INDEX IF NOT EXISTS idx_chg_date  ON cfg_changelog(created_at DESC);
        """, "cfg_changelog"),
    ]

    if not dry_run:
        for sql, label in sqls:
            execute_sql(sql, f"CREATE {label}")

    admin_id     = CTX["admin_id"]
    user_ids     = CTX["user_ids"]
    location_ids = CTX["location_ids"]

    # Feature Flags
    flags_data = [
        ("loyalty_v2_enabled",         "Loyalty Program V2",           "boolean", True,   True,  100, "all"),
        ("meilisearch_enabled",         "Meilisearch Search",           "boolean", True,   True,  100, "all"),
        ("ai_recommendations",          "AI Product Recommendations",   "boolean", False,  False, 20,  "all"),
        ("new_pos_ui",                  "New POS Interface",            "boolean", False,  True,  50,  "location"),
        ("digital_receipt",             "Digital Receipt Only",         "boolean", False,  False, 0,   "all"),
        ("qris_split_payment",          "QRIS Split Payment",           "boolean", False,  True,  100, "all"),
        ("real_time_stock_sync",        "Real-time Stock Sync",         "boolean", True,   True,  100, "all"),
        ("whatsapp_notifications",      "WhatsApp Notifications",       "boolean", True,   True,  100, "all"),
        ("seasonal_menu_preview",       "Early Access Seasonal Menu",   "boolean", False,  True,  0,   "customer_tier"),
        ("advanced_analytics_dashboard","Advanced Analytics Dashboard", "boolean", False,  True,  100, "employee_role"),
        ("auto_reorder",                "Automatic Reorder PO",         "boolean", False,  False, 0,   "all"),
        ("customer_facing_kiosk",       "Self-Order Kiosk Mode",        "boolean", False,  True,  30,  "location"),
        ("loyalty_points_expiry",       "Loyalty Points Expiry",        "boolean", False,  False, 0,   "all"),
        ("pdf_receipts",                "PDF Receipt Generation",       "boolean", True,   True,  100, "all"),
        ("multi_currency",              "Multi-currency Support",       "boolean", False,  False, 0,   "all"),
        ("dark_mode_pos",               "Dark Mode POS",                "boolean", False,  True,  100, "all"),
        ("stamp_card_nfc",              "NFC Stamp Card",               "boolean", False,  False, 10,  "location"),
        ("waste_tracking",              "Waste Tracking Module",        "boolean", True,   True,  100, "all"),
        ("training_portal",             "Employee Training Portal",     "boolean", True,   True,  100, "all"),
        ("event_booking",               "Event Booking System",         "boolean", True,   True,  100, "all"),
    ]

    flag_rows = [(key, name, "", "boolean",
                  json.dumps(default), json.dumps(current),
                  rollout, applies, json.dumps([]), json.dumps([]),
                  True, admin_id, datetime.now(), datetime.now())
                 for key, name, ftype, default, current, rollout, applies in flags_data]

    if dry_run:
        log(f"[DRY RUN] {len(flag_rows)} feature flags + app configs + location configs + changelog")
        return

    n = bulk_insert("cfg_feature_flags",
        ["flag_key","display_name","description","flag_type","default_value","current_value",
         "rollout_pct","applies_to","allowed_locations","allowed_tiers","is_active",
         "changed_by_id","changed_at","created_at"],
        flag_rows, on_conflict="ON CONFLICT (flag_key) DO NOTHING")
    ok(f"Feature flags: {n}")

    # App Configs
    app_configs = [
        ("loyalty.stamp_per_order",         "loyalty", "Stamps per Order",              "integer",  1,          1),
        ("loyalty.min_spend_for_stamp",      "loyalty", "Minimum Spend untuk Stamp",     "integer",  25000,      25000),
        ("loyalty.points_per_stamp",         "loyalty", "Poin per Stamp",               "integer",  10,         10),
        ("loyalty.stamp_validity_days",      "loyalty", "Masa berlaku stamp (hari)",    "integer",  365,        365),
        ("payment.qris_surcharge_pct",       "payment", "QRIS Surcharge (%)",           "float",    0.0,        0.0),
        ("payment.cash_rounding",            "payment", "Cash Rounding (nearest Rp)",   "integer",  500,        500),
        ("notification.push_batch_size",     "notification","Push Notif Batch Size",    "integer",  1000,       1000),
        ("notification.email_from",          "notification","Email From Address",        "string",   "noreply@kafenusantara.id","noreply@kafenusantara.id"),
        ("reporting.auto_send_daily",        "reporting","Auto-kirim Laporan Harian",   "boolean",  True,       True),
        ("reporting.retention_days",         "reporting","Simpan laporan (hari)",       "integer",  90,         90),
        ("search.min_query_length",          "search",  "Panjang minimum query",        "integer",  2,          2),
        ("search.results_per_page",          "search",  "Hasil per halaman",            "integer",  20,         20),
        ("pos.session_timeout_minutes",      "pos",     "Timeout sesi POS (menit)",     "integer",  30,         30),
        ("pos.receipt_footer_text",          "pos",     "Teks footer struk",            "string",   "Terima kasih sudah singgah!","Terima kasih sudah singgah!"),
        ("pos.enable_split_payment",         "pos",     "Aktifkan Split Payment",       "boolean",  True,       True),
        ("stock.low_stock_alert_threshold",  "stock",   "Threshold alert stok menipis", "float",    1.5,        1.5),
        ("stock.auto_reorder_enabled",       "stock",   "Auto Reorder aktif",           "boolean",  False,      False),
        ("hr.overtime_multiplier",           "hr",      "Multiplier lembur",            "float",    1.5,        1.5),
        ("hr.late_deduction_per_minute",     "hr",      "Potongan per menit terlambat", "integer",  2000,       2000),
        ("general.timezone",                 "general", "Timezone aplikasi",            "string",   "Asia/Jakarta","Asia/Jakarta"),
        ("general.currency",                 "general", "Mata uang",                    "string",   "IDR",      "IDR"),
        ("general.date_format",              "general", "Format tanggal",               "string",   "DD/MM/YYYY","DD/MM/YYYY"),
    ]
    cfg_rows = [(key, group, name, vtype,
                 json.dumps(val), json.dumps(default),
                 "", False, False, admin_id,
                 datetime.now(), datetime.now())
                for key, group, name, vtype, default, val in app_configs]

    n = bulk_insert("cfg_app_configs",
        ["config_key","config_group","display_name","value_type","value","default_value",
         "description","is_sensitive","requires_restart","changed_by_id","created_at","updated_at"],
        cfg_rows, on_conflict="ON CONFLICT (config_key) DO NOTHING")
    ok(f"App configs: {n}")

    # Location Configs (override per lokasi)
    loc_cfg_rows = []
    LOC_OVERRIDES = [
        ("pos.receipt_footer_text",    lambda: f"Terima kasih! Outpost #{RNG.randint(1,56)}"),
        ("loyalty.stamp_per_order",    lambda: str(RNG.choice([1, 2]))),
        ("pos.session_timeout_minutes",lambda: str(RNG.choice([20, 30, 45, 60]))),
        ("stock.low_stock_alert_threshold", lambda: str(round(RNG.uniform(1.0, 2.5), 1))),
    ]
    for lid in location_ids:
        for key, val_fn in RNG.sample(LOC_OVERRIDES, RNG.randint(1, 3)):
            loc_cfg_rows.append((
                lid, key, json.dumps(val_fn()), "",
                admin_id, datetime.now(), datetime.now()
            ))

    n = bulk_insert("cfg_location_configs",
        ["location_id","config_key","value","override_reason","changed_by_id","created_at","updated_at"],
        loc_cfg_rows,
        on_conflict="ON CONFLICT (location_id, config_key) DO NOTHING")
    ok(f"Location configs: {n}")

    # Changelog
    chg_rows = []
    CHANGE_TYPES = ["config_update","flag_toggle","price_change","recipe_update",
                    "permission_change","menu_update","sla_update"]
    ENTITY_TYPES = ["cfg_feature_flags","cfg_app_configs","menu_item","recipe_v2",
                    "loyalty_tiers","cs_sla_configs"]
    IPS = [f"10.0.0.{i}" for i in range(1, 20)]

    days_range = (today - CTX["min_date"]).days
    for _ in range(2000):
        created = datetime.now() - timedelta(days=RNG.randint(0, days_range))
        chg_rows.append((
            RNG.choice(CHANGE_TYPES),
            RNG.choice(ENTITY_TYPES),
            RNG.randint(1, 100),
            f"Updated config via admin panel",
            json.dumps({"value": RNG.choice([True, False, 10, 25000])}),
            json.dumps({"value": RNG.choice([True, False, 15, 30000])}),
            RNG.choice(user_ids) if user_ids else admin_id,
            "Operational requirement",
            RNG.choice(IPS), created
        ))

    n = bulk_insert("cfg_changelog",
        ["change_type","entity_type","entity_id","change_summary",
         "old_value","new_value","changed_by_id","reason","ip_address","created_at"],
        chg_rows, batch=3000)
    ok(f"Changelog entries: {n:,}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

SECTION_MAP = {
    "task_queue":       fill_task_queue,
    "search":           fill_search,
    "reporting":        fill_reporting,
    "api_gateway":      fill_api_gateway,
    "security":         fill_security,
    "recipe_mgmt":      fill_recipe_mgmt,
    "events_calendar":  fill_events_calendar,
    "customer_support": fill_customer_support,
    "analytics_cube":   fill_analytics_cube,
    "config_store":     fill_config_store,
}

ORDER = ["task_queue","search","reporting","api_gateway","security",
         "recipe_mgmt","events_calendar","customer_support","analytics_cube","config_store"]

NEW_TABLES = [
    # Task Queue
    "tq_task_definitions","tq_job_logs","tq_dead_letter_queue","tq_scheduled_jobs",
    # Search
    "search_index_configs","search_query_logs","search_synonyms","search_analytics_daily",
    # Reporting
    "report_templates","report_schedules","report_generated","report_delivery_log",
    # API Gateway
    "api_keys","api_rate_limit_tiers","api_usage_logs","api_webhooks","api_webhook_deliveries",
    # Security
    "sec_login_events","sec_security_alerts","sec_ip_whitelist","sec_device_registry",
    # Recipe
    "recipe_v2","recipe_v2_ingredients","recipe_costing","recipe_yield_tests",
    # Events
    "events_calendar","event_registrations","event_revenue_summary",
    # Customer Support
    "cs_sla_configs","cs_tickets","cs_ticket_messages","cs_escalations",
    # Analytics Cube
    "analytics_hourly_sales","analytics_customer_cohorts",
    "analytics_conversion_funnel","analytics_product_affinity",
    # Config Store
    "cfg_feature_flags","cfg_app_configs","cfg_location_configs","cfg_changelog",
]

def main():
    t_total = time.time()
    print("\n" + "═"*70)
    print("  KAFE NUSANTARA — World Building Phase 3 (seed_expansion3)")
    print("  10 modul baru: TaskQueue, Search, Reporting, API Gateway,")
    print("  Security, Recipe V2, Events, CS, Analytics Cube, Config Store")
    print(f"  Stack: Celery+Redis · Meilisearch · WeasyPrint · DRF · django-axes")
    print("═"*70)
    print(f"  Mode    : {'DRY RUN' if DRY_RUN else 'EXECUTE'}")
    print(f"  Section : {SECTION}")

    load_context()

    to_run  = ORDER if SECTION == "all" else [SECTION]
    results = {}

    for sec in to_run:
        fn = SECTION_MAP.get(sec)
        if not fn:
            warn(f"Section '{sec}' tidak dikenal.")
            continue
        try:
            fn(dry_run=DRY_RUN)
            results[sec] = "OK"
        except Exception as e:
            import traceback
            warn(f"ERROR di {sec}: {e}")
            traceback.print_exc()
            results[sec] = f"ERROR: {e}"

    elapsed = time.time() - t_total
    print("\n" + "═"*70)
    print(f"  SELESAI dalam {elapsed:.1f}s")
    print("─"*70)
    for sec, res in results.items():
        icon = "✓" if res == "OK" else "✗"
        print(f"  {icon} {sec:<25} {res}")
    print("═"*70)

    if DRY_RUN:
        print("\n  Jalankan dengan --execute untuk menyimpan ke DB\n")

    print(f"\n  {'Tabel Baru':<48} {'Rows':>12}")
    print("─"*63)
    for t in NEW_TABLES:
        cnt     = row_count(t) if not DRY_RUN else "—"
        cnt_str = f"{cnt:,}" if isinstance(cnt, int) and cnt >= 0 else str(cnt)
        print(f"  {t:<48} {cnt_str:>12}")
    print(f"\n  Total tabel baru: {len(NEW_TABLES)}")
    print(f"  Grand total tabel (seed 1+2+3): ~{15 + 40 + len(NEW_TABLES)} tabel\n")


try:
    from django.core.management.base import BaseCommand
    class Command(BaseCommand):
        help = "Kafe Nusantara — World Building Phase 3 (10 modul baru)"
        def add_arguments(self, p):
            p.add_argument("--execute", action="store_true", default=False)
            p.add_argument("--section", default="all")
        def handle(self, *args, **opts):
            global DRY_RUN, SECTION
            DRY_RUN = not opts["execute"]
            SECTION = opts["section"]
            main()
except ImportError:
    pass

if __name__ == "__main__":
    main()



jadi sekarang total databasenya bertambah banyak dari sebelumnya
Django settings loaded successfully | Environment: development | Debug: True
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountingAccounts(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=150)
    account_type = models.CharField(max_length=20)
    level = models.SmallIntegerField()
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField()
    allow_posting = models.BooleanField()
    is_cash_account = models.BooleanField()
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounting_accounts'


class AccountingAccountsPayable(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey('LumraConfigVendors', models.DO_NOTHING)
    invoice_number = models.CharField(unique=True, max_length=50)
    invoice_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20)
    memo = models.CharField(max_length=255, blank=True, null=True)
    journal_entry = models.ForeignKey('AccountingJournalEntries', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounting_accounts_payable'


class AccountingAccountsReceivable(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey('LumraConfigCustomers', models.DO_NOTHING)
    invoice_number = models.CharField(unique=True, max_length=50)
    invoice_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20)
    memo = models.CharField(max_length=255, blank=True, null=True)
    journal_entry = models.ForeignKey('AccountingJournalEntries', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounting_accounts_receivable'


class AccountingJournalEntries(models.Model):
    id = models.BigAutoField(primary_key=True)
    number = models.CharField(unique=True, max_length=30)
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    source = models.CharField(max_length=30)
    created_by = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)
    posted_by = models.ForeignKey('AuthUser', models.DO_NOTHING, related_name='accountingjournalentries_posted_by_set', blank=True, null=True)
    posted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounting_journal_entries'


class AccountingJournalEntryLines(models.Model):
    id = models.BigAutoField(primary_key=True)
    journal_entry = models.ForeignKey(AccountingJournalEntries, models.DO_NOTHING)
    account = models.ForeignKey(AccountingAccounts, models.DO_NOTHING)
    description = models.CharField(max_length=255, blank=True, null=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2)
    credit = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounting_journal_entry_lines'


class AccountingPaymentVoucherAllocations(models.Model):
    id = models.BigAutoField(primary_key=True)
    voucher = models.ForeignKey('AccountingPaymentVouchers', models.DO_NOTHING)
    payable_entry = models.ForeignKey(AccountingAccountsPayable, models.DO_NOTHING)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'accounting_payment_voucher_allocations'


class AccountingPaymentVouchers(models.Model):
    id = models.BigAutoField(primary_key=True)
    number = models.CharField(unique=True, max_length=30)
    date = models.DateField()
    vendor = models.ForeignKey('LumraConfigVendors', models.DO_NOTHING)
    cash_account = models.ForeignKey(AccountingAccounts, models.DO_NOTHING)
    method = models.CharField(max_length=20)
    memo = models.CharField(max_length=255, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    created_by = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)
    journal_entry = models.ForeignKey(AccountingJournalEntries, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounting_payment_vouchers'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AxesAccessattempt(models.Model):
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    http_accept = models.CharField(max_length=1025)
    path_info = models.CharField(max_length=255)
    attempt_time = models.DateTimeField()
    get_data = models.TextField()
    post_data = models.TextField()
    failures_since_start = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'axes_accessattempt'
        unique_together = (('username', 'ip_address', 'user_agent'),)


class AxesAccessattemptexpiration(models.Model):
    access_attempt = models.OneToOneField(AxesAccessattempt, models.DO_NOTHING, primary_key=True)
    expires_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'axes_accessattemptexpiration'


class AxesAccessfailurelog(models.Model):
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    http_accept = models.CharField(max_length=1025)
    path_info = models.CharField(max_length=255)
    attempt_time = models.DateTimeField()
    locked_out = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'axes_accessfailurelog'


class AxesAccesslog(models.Model):
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    http_accept = models.CharField(max_length=1025)
    path_info = models.CharField(max_length=255)
    attempt_time = models.DateTimeField()
    logout_time = models.DateTimeField(blank=True, null=True)
    session_hash = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'axes_accesslog'


class CjCustomerSessions(models.Model):
    id = models.BigAutoField(primary_key=True)
    session_uuid = models.UUIDField(unique=True, blank=True, null=True)
    customer = models.ForeignKey('LumraConfigCustomers', models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    channel = models.CharField(max_length=30, blank=True, null=True)
    session_start = models.DateTimeField()
    session_end = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    order_count = models.IntegerField(blank=True, null=True)
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    device_type = models.CharField(max_length=20, blank=True, null=True)
    referral_source = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cj_customer_sessions'
        db_table_comment = 'Sesi kunjungan customer per outpost. Channel: dine_in, takeaway, delivery, online.'


class CjFeedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey('LumraConfigCustomers', models.DO_NOTHING, blank=True, null=True)
    order = models.ForeignKey('LumraConfigOrders', models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    feedback_type = models.CharField(max_length=30, blank=True, null=True)
    rating_overall = models.SmallIntegerField(blank=True, null=True)
    rating_product = models.SmallIntegerField(blank=True, null=True)
    rating_service = models.SmallIntegerField(blank=True, null=True)
    rating_ambiance = models.SmallIntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)  # This field type is a guess.
    is_public = models.BooleanField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    reply_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cj_feedback'
        db_table_comment = 'Feedback & rating customer per order/kunjungan. 1-5 bintang multi-dimensi.'


class CjNpsResponses(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey('LumraConfigCustomers', models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    survey_period = models.CharField(max_length=7)
    nps_score = models.SmallIntegerField()
    category = models.CharField(max_length=15, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    follow_up_done = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cj_nps_responses'
        db_table_comment = 'Net Promoter Score survey bulanan. 0-6=detractor, 7-8=passive, 9-10=promoter.'


class CjTouchpoints(models.Model):
    id = models.BigAutoField(primary_key=True)
    session = models.ForeignKey(CjCustomerSessions, models.DO_NOTHING, blank=True, null=True)
    customer = models.ForeignKey('LumraConfigCustomers', models.DO_NOTHING, blank=True, null=True)
    touchpoint_type = models.CharField(max_length=40)
    channel = models.CharField(max_length=30, blank=True, null=True)
    content_ref = models.CharField(max_length=100, blank=True, null=True)
    sentiment = models.CharField(max_length=10, blank=True, null=True)
    duration_sec = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cj_touchpoints'
        db_table_comment = 'Titik interaksi customer: menu_view, order, payment, feedback, loyalty_check, promo_claim.'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoCeleryBeatClockedschedule(models.Model):
    clocked_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_clockedschedule'


class DjangoCeleryBeatCrontabschedule(models.Model):
    minute = models.CharField(max_length=240)
    hour = models.CharField(max_length=96)
    day_of_week = models.CharField(max_length=64)
    day_of_month = models.CharField(max_length=124)
    month_of_year = models.CharField(max_length=64)
    timezone = models.CharField(max_length=63)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_crontabschedule'


class DjangoCeleryBeatIntervalschedule(models.Model):
    every = models.IntegerField()
    period = models.CharField(max_length=24)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_intervalschedule'


class DjangoCeleryBeatPeriodictask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField()
    kwargs = models.TextField()
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField()
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.IntegerField()
    date_changed = models.DateTimeField()
    description = models.TextField()
    crontab = models.ForeignKey(DjangoCeleryBeatCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjangoCeleryBeatIntervalschedule, models.DO_NOTHING, blank=True, null=True)
    solar = models.ForeignKey('DjangoCeleryBeatSolarschedule', models.DO_NOTHING, blank=True, null=True)
    one_off = models.BooleanField()
    start_time = models.DateTimeField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    headers = models.TextField()
    clocked = models.ForeignKey(DjangoCeleryBeatClockedschedule, models.DO_NOTHING, blank=True, null=True)
    expire_seconds = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictask'


class DjangoCeleryBeatPeriodictasks(models.Model):
    ident = models.SmallIntegerField(primary_key=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictasks'


class DjangoCeleryBeatSolarschedule(models.Model):
    event = models.CharField(max_length=24)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_solarschedule'
        unique_together = (('event', 'latitude', 'longitude'),)


class DjangoCeleryResultsChordcounter(models.Model):
    group_id = models.CharField(unique=True, max_length=255)
    sub_tasks = models.TextField()
    count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_celery_results_chordcounter'


class DjangoCeleryResultsGroupresult(models.Model):
    group_id = models.CharField(unique=True, max_length=255)
    date_created = models.DateTimeField()
    date_done = models.DateTimeField()
    content_type = models.CharField(max_length=128)
    content_encoding = models.CharField(max_length=64)
    result = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_celery_results_groupresult'


class DjangoCeleryResultsTaskresult(models.Model):
    task_id = models.CharField(unique=True, max_length=255)
    status = models.CharField(max_length=50)
    content_type = models.CharField(max_length=128)
    content_encoding = models.CharField(max_length=64)
    result = models.TextField(blank=True, null=True)
    date_done = models.DateTimeField()
    traceback = models.TextField(blank=True, null=True)
    meta = models.TextField(blank=True, null=True)
    task_args = models.TextField(blank=True, null=True)
    task_kwargs = models.TextField(blank=True, null=True)
    task_name = models.CharField(max_length=255, blank=True, null=True)
    worker = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.DateTimeField()
    periodic_task_name = models.CharField(max_length=255, blank=True, null=True)
    date_started = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_celery_results_taskresult'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class FinanceBudgetActuals(models.Model):
    id = models.BigAutoField(primary_key=True)
    budget = models.ForeignKey('FinanceBudgets', models.DO_NOTHING)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    variance_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    variance_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    as_of_date = models.DateField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_budget_actuals'
        unique_together = (('budget', 'as_of_date'),)
        db_table_comment = 'Realisasi aktual vs anggaran per periode.'


class FinanceBudgets(models.Model):
    id = models.BigAutoField(primary_key=True)
    budget_year = models.SmallIntegerField()
    budget_month = models.SmallIntegerField(blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=50)
    account_code = models.CharField(max_length=20, blank=True, null=True)
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_budgets'
        unique_together = (('budget_year', 'budget_month', 'location', 'category'),)
        db_table_comment = 'Anggaran tahunan/bulanan per kategori dan lokasi.'


class FinanceCostCenters(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_cost_centers'
        db_table_comment = 'Cost center per outpost/departemen untuk alokasi biaya.'


class FinanceGlPostings(models.Model):
    id = models.BigAutoField(primary_key=True)
    journal = models.ForeignKey('FinanceJournalEntries', models.DO_NOTHING)
    account = models.ForeignKey(AccountingAccounts, models.DO_NOTHING, blank=True, null=True)
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_gl_postings'
        db_table_comment = 'Baris debit/kredit per jurnal. Double-entry bookkeeping.'


class FinanceJournalEntries(models.Model):
    id = models.BigAutoField(primary_key=True)
    entry_number = models.CharField(unique=True, max_length=30)
    entry_date = models.DateField()
    period = models.CharField(max_length=7)
    entry_type = models.CharField(max_length=30)
    description = models.TextField()
    reference_type = models.CharField(max_length=40, blank=True, null=True)
    reference_id = models.BigIntegerField(blank=True, null=True)
    total_debit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    approved_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='financejournalentries_approved_by_set', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_journal_entries'
        db_table_comment = 'Jurnal akuntansi: penjualan, pembelian, biaya, penyesuaian, opening balance.'


class HrAttendance(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey('HrEmployees', models.DO_NOTHING)
    schedule = models.ForeignKey('HrWorkSchedules', models.DO_NOTHING, blank=True, null=True)
    attendance_date = models.DateField()
    clock_in = models.DateTimeField(blank=True, null=True)
    clock_out = models.DateTimeField(blank=True, null=True)
    late_minutes = models.IntegerField(blank=True, null=True)
    early_out_minutes = models.IntegerField(blank=True, null=True)
    overtime_minutes = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hr_attendance'
        db_table_comment = 'Absensi harian. Status: present, absent, sick, leave, holiday.'


class HrEmployees(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee_number = models.CharField(unique=True, max_length=20)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    full_name = models.CharField(max_length=150)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=40)
    department = models.CharField(max_length=40)
    join_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    employment_type = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    bank_account = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=20, blank=True, null=True)
    bpjs_health = models.CharField(max_length=20, blank=True, null=True)
    bpjs_employment = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hr_employees'
        db_table_comment = 'Karyawan Kafe Nusantara per outpost. Role: barista, cashier, supervisor, kitchen, manager.'


class HrPayroll(models.Model):
    id = models.BigAutoField(primary_key=True)
    payroll_period = models.CharField(max_length=7)
    employee = models.ForeignKey(HrEmployees, models.DO_NOTHING)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deduction_late = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deduction_absent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bpjs_health_emp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bpjs_emp_emp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pph21 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    paid_at = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hr_payroll'
        unique_together = (('payroll_period', 'employee'),)
        db_table_comment = 'Slip gaji bulanan per karyawan. Period format: YYYY-MM.'


class HrWorkSchedules(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(HrEmployees, models.DO_NOTHING)
    schedule_date = models.DateField()
    shift_type = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hr_work_schedules'
        unique_together = (('employee', 'schedule_date', 'shift_type'),)
        db_table_comment = 'Jadwal kerja mingguan karyawan.'


class LoyaltyRedemptions(models.Model):
    id = models.BigAutoField(primary_key=True)
    card = models.ForeignKey('LoyaltyStampCards', models.DO_NOTHING)
    reward = models.ForeignKey('LoyaltyRewards', models.DO_NOTHING)
    order = models.ForeignKey('LumraConfigOrders', models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    stamps_used = models.IntegerField(blank=True, null=True)
    points_used = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    redeemed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loyalty_redemptions'
        db_table_comment = 'Log redeem reward oleh customer.'


class LoyaltyRewards(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=30)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    reward_type = models.CharField(max_length=30)
    stamps_required = models.IntegerField(blank=True, null=True)
    points_required = models.IntegerField(blank=True, null=True)
    valid_days = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    stock_limit = models.IntegerField(blank=True, null=True)
    redeemed_count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loyalty_rewards'
        db_table_comment = 'Katalog reward yang bisa diredeem: free drink, pastry, merchandise, diskon.'


class LoyaltyStampCards(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.OneToOneField('LumraConfigCustomers', models.DO_NOTHING)
    card_number = models.CharField(unique=True, max_length=30)
    tier = models.ForeignKey('LoyaltyTiers', models.DO_NOTHING, blank=True, null=True)
    total_points = models.IntegerField(blank=True, null=True)
    current_stamps = models.IntegerField(blank=True, null=True)
    lifetime_stamps = models.IntegerField(blank=True, null=True)
    lifetime_spend = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    outposts_visited = models.IntegerField(blank=True, null=True)
    last_visit_date = models.DateField(blank=True, null=True)
    member_since = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loyalty_stamp_cards'
        db_table_comment = 'Kartu stamp digital per customer. 10 stamps = 1 reward free drink.'


class LoyaltyStampTransactions(models.Model):
    id = models.BigAutoField(primary_key=True)
    card = models.ForeignKey(LoyaltyStampCards, models.DO_NOTHING)
    order = models.ForeignKey('LumraConfigOrders', models.DO_NOTHING, blank=True, null=True)
    location = models.ForeignKey('LumraConfigLocations', models.DO_NOTHING, blank=True, null=True)
    transaction_type = models.CharField(max_length=20)
    stamps_delta = models.IntegerField()
    points_delta = models.IntegerField()
    spend_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loyalty_stamp_transactions'
        db_table_comment = 'Riwayat earn/redeem stamp dan poin per transaksi.'


class LoyaltyTiers(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)
    min_points = models.IntegerField()
    max_points = models.IntegerField(blank=True, null=True)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    stamp_multiplier = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    perks = models.JSONField(blank=True, null=True)
    badge_color = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loyalty_tiers'

dan teknologi yang ditambahkan juga bertambah karena masuk beast mode
pip list                                 
Package               Version                                              
--------------------- -----------
amqp                  5.3.1
annotated-types       0.7.0
asgiref               3.11.1
beautifulsoup4        4.14.3
billiard              4.2.4
brotli                1.2.0
build                 1.5.0
camel-converter       5.1.0
celery                5.6.3
certifi               2026.4.22
cffi                  2.0.0
charset-normalizer    3.4.7
click                 8.3.3
click-didyoumean      0.3.1
click-plugins         1.1.1.2
click-repl            0.3.0
colorama              0.4.6
crispy-tailwind       1.0.3
cron-descriptor       1.4.5
cssselect2            0.9.0
Django                6.0.4
django-axes           8.3.1
django-browser-reload 1.21.0
django-cacheops       7.2
django-celery-beat    2.9.0
django_celery_results 2.6.0
django-crispy-forms   2.6
django-debug-toolbar  6.3.0
django-environ        0.13.0
django-extensions     4.1
django-filter         25.2
django-htmx           1.27.0
django-queryset-csv   1.1.0
django-silk           5.5.0
django-tables2        3.0.0
django-tailwind       4.4.2
django-timezone-field 7.2.1
django-unfold         0.92.0
django-widget-tweaks  1.5.1
djangorestframework   3.17.1
et_xmlfile            2.0.0
fonttools             4.62.1
funcy                 2.0
gprof2dot             2025.4.14
idna                  3.13
kombu                 5.6.2
meilisearch           0.41.0
openpyxl              3.1.5
packaging             26.2
pillow                12.2.0
pip                   26.1.1
pip-review            1.3.0
pip-tools             7.5.3
prompt_toolkit        3.0.52
psycopg               3.3.4
psycopg-binary        3.3.4
psycopg2-binary       2.9.12
pycparser             3.0
pydantic              2.13.3
pydantic_core         2.46.3
pydyf                 0.12.1
pyphen                0.17.2
pyproject_hooks       1.2.0
pytailwindcss         0.3.0
python-crontab        3.3.0
python-dateutil       2.9.0.post0
redis                 6.4.0
requests              2.33.1
sentry-sdk            2.59.0
setuptools            82.0.1
six                   1.17.0
soupsieve             2.8.3
sqlparse              0.5.5
tinycss2              1.5.1
tinyhtml5             2.1.0
typing_extensions     4.15.0
typing-inspection     0.4.2
tzdata                2026.2
tzlocal               5.3.1
unicodecsv            0.14.1
urllib3               2.6.3
vine                  5.1.0
wcwidth               0.7.0
weasyprint            68.1
webencodings          0.5.1
wheel                 0.47.0
zopfli                0.4.1