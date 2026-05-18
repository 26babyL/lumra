# 📋 LUMRA ERP — Master Integration Checklist
> Rekap lengkap: MVC flow, skenario per modul, status integrasi, dan urutan pengerjaan.

---

## 🗂️ STRUKTUR FOLDER FINAL

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
│       ├── empty_state.html       
│       ├── pagination.html        
│       ├── data_table.html        
│       ├── breadcrumb.html        
│       ├── confirm_modal.html     
│       ├── tabs.html              
│       ├── badge.html             
│       ├── stepper.html           
│       └── print_base.html        
│
└── lumra_pages/
    ├── auth/
    ├── onboarding/
    ├── inventory/
    ├── sales/
    ├── sales_insight/
    ├── production/
    ├── marketing/
    ├── master_data/
    ├── accounting/
    ├── print/
    ├── messages/
    ├── reports/
    ├── settings/
    └── etc/
```

---

## 🧹 FASE 0 — CLEANUP DULU (Sebelum Apapun)

> Hapus file duplikat ini. Jangan skip, ini technical debt.

| HAPUS | ALASAN | GANTI DENGAN |
|-------|--------|-------------|
| `customer.html` | Duplikat | `customer_detail.html` |
| `vendor_list.html` | Duplikat (beda 's') | `vendors_list.html` |
| `product_list.html` | Duplikat | `products.html` |
| `campaign_list.html` | Duplikat | `campaign.html` |
| `location_list.html` | Duplikat | `locations.html` |
| `add_stock_movement.html` | Duplikat | `stock_movement_form.html` |
| `sales_report_after.html` | Naming tidak jelas | `sales_report.html` |
| `stock_opname_locations.html` (duplikat) | Muncul 2x | Pertahankan di `inventory/` saja |
| `stock_overview.html` (di `reports/`) | Duplikat dari `inventory/` | Hapus di `reports/`, buat alias view |
| `financial_reports.html` (di `reports/`) | Duplikat dari `sales_insight/` | Hapus di `reports/` |
| `dashboard.html` (di `sales_insight/`) | Salah tempat | Rename → `sales_dashboard.html` |
| `pos.html` (di `sales_insight/`) | Salah folder | Pindah → `sales/pos.html` |

**Setelah cleanup: 81 file tersisa (dari 102).**

---

---

## 📦 MODUL 1 — BASE COMPONENTS

### File yang Harus Ada
| File | Fungsi | Dipakai Oleh |
|------|--------|-------------|
| `empty_state.html` | Tampilan halaman kosong (icon + pesan + CTA) | Semua list page saat data kosong |
| `pagination.html` | Navigasi halaman standar | Semua list page |
| `data_table.html` | Wrapper tabel (sort, search, per-page) | Semua halaman tabel |
| `breadcrumb.html` | Navigasi breadcrumb | Semua halaman dalam |
| `confirm_modal.html` | Dialog konfirmasi generik (ya/tidak) | Semua aksi hapus/batal |
| `tabs.html` | Komponen tab horizontal | Halaman detail multi-tab |
| `badge.html` | Badge status (success/warning/danger) | Semua list & detail |
| `stepper.html` | Step wizard (1→2→3→4) | Onboarding, form multi-step |
| `print_base.html` | Layout cetak tanpa navbar/sidebar | Semua print template |

### ✅ Checklist MVC
- [ ] `base.html` meload navbar, sidebar, footer dengan `{% include %}`
- [ ] Semua halaman extends `base.html` dan mengisi block `content`
- [ ] `empty_state.html` menerima context variable `empty_icon`, `empty_title`, `empty_message`, `empty_cta_url`, `empty_cta_label`
- [ ] `pagination.html` menerima object `page_obj` dari Django Paginator
- [ ] `confirm_modal.html` menerima `action_url` dan `csrf_token`

---

## 🔐 MODUL 2 — AUTHENTICATION

### Skenario Alur
```
Baru pertama buka → login.html
Lupa password → forgot_password.html → (cek email) → verify_email.html → reset_password.html → login.html
Login berhasil + 2FA aktif → two_factor.html → dashboard
Layar kunci (idle) → lock_screen.html → (input PIN) → halaman sebelumnya
Sesi habis → session_expired.html → login.html
```

### File & Koneksi MVC
| File HTML | View | Model/Auth |
|-----------|------|-----------|
| `login.html` | `LoginView` (Django built-in) | `auth_user` |
| `register.html` | `RegisterView` | `auth_user` + `lumra_config_userprofile` |
| `forgot_password.html` | `PasswordResetView` | `auth_user.email` |
| `verify_email.html` | — (static page) | — |
| `reset_password.html` | `PasswordResetConfirmView` | `auth_user` |
| `two_factor.html` | `TwoFactorVerifyView` | `lumra_config_userprofile.otp_secret` |
| `lock_screen.html` | `LockScreenView` | `auth_user` session |
| `session_expired.html` | — (static/error page) | — |

### ✅ Checklist MVC
- [ ] `login.html` → POST ke `/auth/login/` → redirect ke `dashboard` atau `two_factor`
- [ ] `forgot_password.html` → POST ke `/auth/password-reset/` → kirim email
- [ ] `reset_password.html` → POST ke `/auth/password-reset/confirm/<uidb64>/<token>/`
- [ ] `two_factor.html` → POST ke `/auth/2fa/verify/` dengan kode OTP
- [ ] `lock_screen.html` → POST PIN ke `/auth/unlock/`, verifikasi session user yang sama
- [ ] `session_expired.html` → tidak perlu view, cukup template statis dengan countdown JS

---

## 🧭 MODUL 3 — ONBOARDING / SETUP WIZARD

### Skenario Alur
```
User baru register → welcome.html
→ step_business.html (isi nama bisnis, logo, industri)
→ step_location.html (tambah outlet/cabang pertama)
→ step_category.html (tambah kategori produk pertama)
→ step_complete.html ("Selesai!") → dashboard
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `welcome.html` | `OnboardingWelcomeView` | `lumra_config_userprofile.onboarding_step` |
| `step_business.html` | `OnboardingBusinessView` | `lumra_config_businessprofile` |
| `step_location.html` | `OnboardingLocationView` | `lumra_config_locations` |
| `step_category.html` | `OnboardingCategoryView` | `lumra_config_categories` |
| `step_complete.html` | `OnboardingCompleteView` | `lumra_config_userprofile.onboarding_done = True` |

### ✅ Checklist MVC
- [ ] Semua step gunakan `stepper.html` partial dengan step aktif yang di-pass via context
- [ ] Setiap step simpan progress ke session atau `userprofile.onboarding_step`
- [ ] Middleware redirect user baru (onboarding belum selesai) ke `welcome.html`
- [ ] `step_complete.html` set `userprofile.onboarding_done = True` dan redirect ke `dashboard`

---

## 📦 MODUL 4 — INVENTORY MANAGEMENT

### Skenario Alur
```
Buat Permintaan Stok (Requisition):
requisition_list.html → [Buat Baru] → requisition_form.html
→ (submit) → requisition_detail.html → [Approve/Reject] → update status

Cek Batch & Expiry:
batch_list.html → [Buat Batch] → batch_form.html → batch_detail.html
expiry_tracking.html → (lihat produk mendekati expired, filter 7/14/30 hari)

Stock Opname:
stock_opname_locations.html → [Pilih Lokasi] → stock_opname_form.html
→ [Submit] → stock_opname_approvals.html → [Approve] → stock_opname_approval_detail.html

Transfer Stok Antar Cabang:
transfer_list.html → [Buat Transfer] → transfer_form.html → transfer_detail.html

Stock Overview:
stock_overview.html → (lihat semua stok per lokasi)
stock_movement.html → (audit trail semua pergerakan stok)
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `stock_overview.html` | `StockOverviewView` | `lumra_config_stock` + `lumra_config_locations` |
| `stock_movement.html` | `StockMovementListView` | `lumra_config_stockmovement` 🆕 |
| `stock_movement_form.html` | `StockMovementCreateView` | `lumra_config_stockmovement` 🆕 |
| `stock_planning.html` | `StockPlanningView` | `lumra_config_stock` + `lumra_config_sales_targets` |
| `stock_opname_locations.html` | `StockOpnameLocationView` | `lumra_config_locations` |
| `stock_opname_form.html` | `StockOpnameFormView` | `lumra_config_stockopname_item` |
| `stock_opname_approvals.html` | `StockOpnameApprovalListView` | `lumra_config_stockopname_session` |
| `stock_opname_approval_detail.html` | `StockOpnameApprovalDetailView` | `lumra_config_stockopname_session` + `lumra_config_stockopname_item` |
| `stock_opname_session_detail.html` | `StockOpnameSessionDetailView` | `lumra_config_stockopname_session` |
| `requisition_list.html` | `RequisitionListView` | `lumra_config_requisitions` |
| `requisition_form.html` | `RequisitionCreateView` | `lumra_config_requisitions` + `lumra_config_requisitionitem` |
| `requisition_detail.html` | `RequisitionDetailView` | `lumra_config_requisitions` |
| `batch_list.html` | `BatchListView` | `lumra_config_productbatches` 🆕 |
| `batch_form.html` | `BatchCreateView` | `lumra_config_productbatches` 🆕 |
| `batch_detail.html` | `BatchDetailView` | `lumra_config_productbatches` 🆕 |
| `expiry_tracking.html` | `ExpiryTrackingView` | `lumra_config_productbatches.expiry_date` 🆕 |
| `warehouse_zones.html` | `WarehouseZoneListView` | ⚠️ Tabel belum ada |
| `warehouse_zone_form.html` | `WarehouseZoneFormView` | ⚠️ Tabel belum ada |
| `adjustment_reasons.html` | `AdjustmentReasonListView` | `lumra_config_adjustmentreasons` 🆕 |
| `supplier_evaluation.html` | `SupplierEvaluationView` | Agregasi dari `lumra_config_stockmovement` + `lumra_config_vendors` |

### ✅ Checklist MVC
- [ ] `stock_overview.html` menampilkan qty per produk per lokasi (JOIN `stock` + `locations` + `products`)
- [ ] `expiry_tracking.html` query: `WHERE expiry_date <= NOW() + INTERVAL X DAY AND is_active = TRUE`
- [ ] `stock_opname_form.html` mengirim formset item (multiple rows sekaligus)
- [ ] Setelah approve opname → otomatis UPDATE `lumra_config_stock.quantity` + INSERT ke `lumra_config_stockmovement`
- [ ] `requisition_detail.html` tombol Approve/Reject hanya muncul jika user punya permission `inventory.approve_requisition`
- [ ] `batch_list.html` + `expiry_tracking.html` membutuhkan tabel `lumra_config_productbatches` sudah ada di DB

---

## 💰 MODUL 5 — SALES & POS

### Skenario Alur
```
Transaksi POS:
pos.html → (scan/cari produk, tambah ke cart) → (pilih customer opsional)
→ (pilih metode bayar) → (proses) → print_receipt.html → pos.html (reset)

Pipeline Sales:
quotation_list.html → [Buat Quotation] → quotation_form.html → quotation_detail.html
→ [Konversi ke SO] → sales_order_detail.html → [Buat Invoice] → invoice_detail.html
→ [Catat Pembayaran] → payment_form.html → invoice lunas

Retur:
order_list.html / invoice_detail.html → [Ajukan Retur] → retur_form.html
→ retur_detail.html → [Approve] → (stok kembali + refund/credit note)
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `pos.html` | `POSView` | `lumra_config_orders` + `lumra_config_orderitems` + `lumra_config_customers` |
| `order_list.html` | `OrderListView` | `lumra_config_orders` |
| `order_detail.html` | `OrderDetailView` | `lumra_config_orders` + `lumra_config_orderitems` |
| `sales_order_list.html` | `SalesOrderListView` | `lumra_config_orders` (filter `order_type='sales_order'`) |
| `sales_order_form.html` | `SalesOrderCreateView` | `lumra_config_orders` + `lumra_config_orderitems` |
| `sales_order_detail.html` | `SalesOrderDetailView` | `lumra_config_orders` |
| `quotation_list.html` | `QuotationListView` | `lumra_config_orders` (filter `order_type='draft'`) |
| `quotation_form.html` | `QuotationCreateView` | `lumra_config_orders` |
| `quotation_detail.html` | `QuotationDetailView` | `lumra_config_orders` |
| `invoice_list.html` | `InvoiceListView` | `lumra_config_orders` (filter `order_type='invoiced'`) |
| `invoice_form.html` | `InvoiceCreateView` | `lumra_config_orders` |
| `invoice_detail.html` | `InvoiceDetailView` | `lumra_config_orders` + `lumra_config_payments` 🆕 |
| `payment_list.html` | `PaymentListView` | `lumra_config_payments` 🆕 |
| `payment_form.html` | `PaymentCreateView` | `lumra_config_payments` 🆕 |
| `retur_list.html` | `ReturListView` | `lumra_config_returns` 🆕 |
| `retur_form.html` | `ReturCreateView` | `lumra_config_returns` + `lumra_config_returnitems` 🆕 |
| `retur_detail.html` | `ReturDetailView` | `lumra_config_returns` + `lumra_config_returnitems` 🆕 |

### ✅ Checklist MVC
- [ ] `pos.html` — cart dikelola Alpine.js, submit ke `/api/orders/create/` via fetch/HTMX
- [ ] `pos.html` — setelah transaksi selesai: INSERT `orders`, INSERT `orderitems`, UPDATE `stock`, INSERT `stockmovement`, INSERT `payments`
- [ ] POS harus handle split payment (cash + QRIS sekaligus) → `lumra_config_payments` bisa multi-row per order
- [ ] Konversi Quotation → SO: update `order_type` field dari `draft` ke `sales_order`
- [ ] Konversi SO → Invoice: update `order_type` ke `invoiced`, set `due_date`
- [ ] Retur approved → INSERT `stockmovement` dengan `movement_type='retur'`, UPDATE `stock.quantity`
- [ ] `payment_form.html` otomatis update `orders.payment_status` → `partial` atau `paid`

---

## 🏭 MODUL 6 — PRODUCTION / RECIPES

### Skenario Alur
```
Setup Resep:
recipe_list.html → [Buat Resep] → recipe_form.html (nama, bahan, qty, unit)
→ recipe_detail.html (lihat detail + bahan baku)

Jalankan Produksi:
production_order_list.html → [Buat PO] → production_order_form.html
→ production_order_detail.html → [Mulai Produksi]
→ material_consumption.html (catat bahan terpakai vs teoritis)
→ production_waste.html (catat waste/scrap)
→ finished_goods_receipt.html (masukkan hasil ke stok)
→ production_order_detail.html (status: completed)

Analisis:
production_costing.html (cost per unit, actual vs standar, variance)
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `recipe_list.html` | `RecipeListView` | `production_recipes` + `production_recipe_categories` |
| `recipe_form.html` | `RecipeCreateView` | `production_recipes` + `production_recipe_ingredients` |
| `recipe_detail.html` | `RecipeDetailView` | `production_recipes` + `production_recipe_ingredients` |
| `production_order_list.html` | `ProductionOrderListView` | ⚠️ Tabel belum ada |
| `production_order_form.html` | `ProductionOrderCreateView` | ⚠️ Tabel belum ada |
| `production_order_detail.html` | `ProductionOrderDetailView` | ⚠️ Tabel belum ada |
| `bom_list.html` | `BOMListView` | `production_recipes` (BOM = recipe dalam konteks ini) |
| `bom_form.html` | `BOMCreateView` | `production_recipes` |
| `bom_detail.html` | `BOMDetailView` | `production_recipes` |
| `production_scheduling.html` | `ProductionSchedulingView` | ⚠️ Tabel belum ada |
| `material_consumption.html` | `MaterialConsumptionView` | ⚠️ Tabel belum ada |
| `finished_goods_receipt.html` | `FinishedGoodsReceiptView` | `lumra_config_stock` + `lumra_config_stockmovement` |
| `production_waste.html` | `ProductionWasteView` | ⚠️ Tabel belum ada |
| `production_costing.html` | `ProductionCostingView` | Agregasi dari tabel consumption + produk |

### ✅ Checklist MVC
- [ ] `recipe_form.html` gunakan Django inline formset untuk bahan-bahan (dynamic add/remove baris via Alpine)
- [ ] `finished_goods_receipt.html` → INSERT `lumra_config_stockmovement` dengan `movement_type='production_in'`
- [ ] Material consumption → INSERT `lumra_config_stockmovement` dengan `movement_type='production_out'`
- [ ] ⚠️ **Tabel production order, scheduling, consumption, waste BELUM ADA** — buat dulu sebelum halaman ini dibuat

---

## 📣 MODUL 7 — MARKETING MANAGEMENT

### Skenario Alur
```
Buat Promo:
campaign.html (daftar semua kampanye) → [Buat Kampanye] → (form buat kampanye)
→ campaign_detail.html → (lihat performa: impressi, klik, konversi, revenue)

Buat Voucher:
voucher_list.html → [Buat Voucher] → voucher_form.html
(isi: kode, tipe diskon %/nominal, min. pembelian, kuota, periode, produk berlaku)
→ voucher_claim_log.html (lihat siapa yang pakai)

Segmentasi Pelanggan:
customer_segment_list.html → [Buat Segmen] → customer_segment_form.html
(rules: total belanja, frekuensi beli, lokasi, kategori produk favorit)
→ (gunakan segmen ini untuk kirim broadcast di Modul Messages)

Kalender Promosi:
promotion_calendar.html → (lihat semua promo aktif/mendatang, deteksi overlap)
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `campaign.html` | `CampaignListView` | ⚠️ Tabel belum ada (ada di roadmap) |
| `voucher_list.html` | `VoucherListView` | ⚠️ Tabel belum ada |
| `voucher_form.html` | `VoucherCreateView` | ⚠️ Tabel belum ada |
| `voucher_claim_log.html` | `VoucherClaimLogView` | ⚠️ Tabel belum ada |
| `customer_segment_list.html` | `CustomerSegmentListView` | ⚠️ Tabel belum ada |
| `customer_segment_form.html` | `CustomerSegmentCreateView` | ⚠️ Tabel belum ada |
| `promotion_calendar.html` | `PromotionCalendarView` | Agregasi dari tabel campaign/voucher |

### ✅ Checklist MVC
- [ ] ⚠️ **Semua tabel marketing BELUM ADA** — ini Fase 2
- [ ] Voucher applied di POS: `pos.html` kirim `voucher_code` → backend validasi → hitung diskon → tampilkan di cart
- [ ] Customer segment rules dieksekusi via Django ORM query builder atau JSON rules engine
- [ ] `promotion_calendar.html` bisa pakai FullCalendar.js untuk timeline view
- [ ] Setelah segmen dibuat → bisa dipakai di `broadcast.html` (Modul Messages) sebagai target penerima

---

## 📊 MODUL 8 — MASTER DATA & CONFIGURATION

### Skenario Alur
```
Setup Awal:
categories_list.html → [Tambah Kategori] → category_form.html
units_list.html → [Tambah Satuan] → unit_form.html
tax_list.html → [Tambah Pajak] → tax_form.html
bank_accounts.html → [Tambah Rekening] → bank_account_form.html

Data Pelanggan:
customers.html → [Lihat Detail] → customer_detail.html
customer_detail.html → (tab: info, histori transaksi, poin loyalty)
→ [Edit] → customer_form.html

Data Supplier:
vendors_list.html → [Lihat Detail] → vendor_detail.html
vendor_detail.html → (tab: info, harga produk, evaluasi performa)
supplier_evaluation.html → (skor delivery on-time, quality, harga)
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `categories_list.html` | `CategoryListView` | `lumra_config_categories` |
| `category_form.html` | `CategoryCreateView` | `lumra_config_categories` |
| `units_list.html` | `UnitListView` | `lumra_config_units` |
| `unit_form.html` | `UnitCreateView` | `lumra_config_units` |
| `vendors_list.html` | `VendorListView` | `lumra_config_vendors` |
| `vendor_form.html` | `VendorCreateView` | `lumra_config_vendors` |
| `customers.html` | `CustomerListView` | `lumra_config_customers` |
| `customer_detail.html` | `CustomerDetailView` | `lumra_config_customers` + `lumra_config_orders` |
| `customer_form.html` | `CustomerCreateView` | `lumra_config_customers` |
| `locations.html` | `LocationListView` | `lumra_config_locations` |
| `products.html` | `ProductListView` | `lumra_config_products` |
| `product_details.html` | `ProductDetailView` | `lumra_config_products` + `lumra_config_productvariants` + `lumra_config_stock` |
| `tax_list.html` | `TaxListView` | ⚠️ Tabel belum ada |
| `tax_form.html` | `TaxCreateView` | ⚠️ Tabel belum ada |
| `bank_accounts.html` | `BankAccountListView` | ⚠️ Tabel belum ada |
| `bank_account_form.html` | `BankAccountCreateView` | ⚠️ Tabel belum ada |
| `payment_terms_list.html` | `PaymentTermsListView` | ⚠️ Tabel belum ada |
| `tags_list.html` | `TagListView` | ⚠️ Tabel belum ada |
| `reason_codes.html` | `ReasonCodeListView` | `lumra_config_adjustmentreasons` 🆕 |

### ✅ Checklist MVC
- [ ] `product_details.html` → gunakan tab: Info Umum | Varian | Stok per Lokasi | Harga Supplier | Batch
- [ ] `customer_detail.html` → tab: Profil | Histori Transaksi | Poin Loyalty | Segmen
- [ ] `customer_detail.html` → query `lumra_config_orders WHERE customer_id = X ORDER BY created_at DESC`
- [ ] `products.html` → toggle grid view / table view via Alpine.js (simpan preference ke localStorage)
- [ ] `supplier_evaluation.html` → agregasi dari data transaksi pembelian, bukan tabel terpisah

---

## 🧾 MODUL 9 — ACCOUNTING

### Skenario Alur
```
Setup COA:
chart_of_accounts.html → [Tambah Akun] → chart_of_accounts_form.html

Catat Jurnal:
journal_entry_list.html → [Buat Jurnal] → journal_entry_form.html
(tanggal, referensi, baris debit/kredit)
→ journal_entry_detail.html → [Post] → status: posted

Laporan Keuangan:
trial_balance.html (semua akun, total debit, kredit)
→ balance_sheet.html (neraca: aset, kewajiban, ekuitas)
→ cash_flow.html (arus kas: operasional, investasi, pendanaan)

Utang Piutang:
accounts_payable.html (aging hutang ke supplier: 0-30, 31-60, 61-90, 90+ hari)
accounts_receivable.html (aging piutang dari customer)
→ payment_voucher_form.html (bayar hutang ke supplier)
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `chart_of_accounts.html` | `COAListView` | ⚠️ Tabel belum ada |
| `chart_of_accounts_form.html` | `COACreateView` | ⚠️ Tabel belum ada |
| `journal_entry_list.html` | `JournalEntryListView` | ⚠️ Tabel belum ada |
| `journal_entry_form.html` | `JournalEntryCreateView` | ⚠️ Tabel belum ada |
| `journal_entry_detail.html` | `JournalEntryDetailView` | ⚠️ Tabel belum ada |
| `general_ledger.html` | `GeneralLedgerView` | ⚠️ Tabel belum ada |
| `trial_balance.html` | `TrialBalanceView` | ⚠️ Tabel belum ada |
| `balance_sheet.html` | `BalanceSheetView` | ⚠️ Tabel belum ada |
| `cash_flow.html` | `CashFlowView` | ⚠️ Tabel belum ada |
| `accounts_payable.html` | `APAgingView` | ⚠️ Tabel belum ada |
| `accounts_receivable.html` | `ARAgingView` | ⚠️ Tabel belum ada |
| `payment_voucher_form.html` | `PaymentVoucherView` | ⚠️ Tabel belum ada |

### ✅ Checklist MVC
- [ ] ⚠️ **Seluruh modul accounting bergantung pada tabel COA + Jurnal yang belum ada** — ini Fase 3
- [ ] Setiap transaksi (POS, pembelian, retur) idealnya auto-generate jurnal → butuh accounting engine di views
- [ ] `journal_entry_form.html` gunakan inline formset untuk baris debit/kredit (pastikan balance sebelum submit)
- [ ] `general_ledger.html` filter by akun + date range → query aggregasi dari journal entries

---

## 🖨️ MODUL 10 — PRINT TEMPLATES

### Skenario Alur
```
Dari POS → setelah transaksi → tombol "Cetak Struk" → print_receipt.html (58mm thermal)
Dari invoice_detail.html → tombol "Cetak Invoice" → print_invoice.html (A4)
Dari quotation_detail.html → tombol "Cetak Quotation" → print_quotation.html (A4)
Dari sales_order_detail.html → tombol "Cetak SO" → print_sales_order.html (A4)
Dari requisition_detail.html → tombol "Cetak PO Pembelian" → print_purchase_order.html (A4)
Dari transfer_detail.html → tombol "Cetak Surat Jalan" → print_delivery_note.html (A4)
Dari stock_opname_form.html → tombol "Cetak Lembar Opname" → print_stock_opname.html (A4 landscape)
Dari retur_detail.html → tombol "Cetak Credit Note" → print_credit_note.html (A4)
```

### File & Koneksi MVC
| File HTML | View | Data Source |
|-----------|------|-------------|
| `print_receipt.html` | `PrintReceiptView` | `lumra_config_orders` + `lumra_config_orderitems` + `lumra_config_payments` |
| `print_invoice.html` | `PrintInvoiceView` | `lumra_config_orders` + `lumra_config_orderitems` |
| `print_quotation.html` | `PrintQuotationView` | `lumra_config_orders` |
| `print_sales_order.html` | `PrintSalesOrderView` | `lumra_config_orders` + `lumra_config_orderitems` |
| `print_purchase_order.html` | `PrintPurchaseOrderView` | `lumra_config_requisitions` + `lumra_config_requisitionitem` |
| `print_delivery_note.html` | `PrintDeliveryNoteView` | `lumra_config_transfers` |
| `print_packing_slip.html` | `PrintPackingSlipView` | `lumra_config_transfers` |
| `print_credit_note.html` | `PrintCreditNoteView` | `lumra_config_returns` + `lumra_config_returnitems` |
| `print_payment_receipt.html` | `PrintPaymentReceiptView` | `lumra_config_payments` |
| `print_stock_opname.html` | `PrintStockOpnameView` | `lumra_config_stockopname_session` + `lumra_config_stockopname_item` |
| `print_production_order.html` | `PrintProductionOrderView` | Tabel production order (belum ada) |

### ✅ Checklist MVC
- [ ] Semua print template extends `print_base.html` (layout tanpa navbar/sidebar)
- [ ] `print_base.html` memiliki `@media print { ... }` CSS yang hide semua non-print elements
- [ ] Setiap print view → `return render(request, 'print/...html', context)` dengan `Content-Type` normal (bukan PDF)
- [ ] Tombol print di halaman source memanggil `window.open('/print/receipt/<order_id>/')` di new tab → user langsung Ctrl+P
- [ ] `print_receipt.html` → CSS max-width: 58mm, font-size kecil, minimal grafis

---

## 💬 MODUL 11 — MESSAGES & NOTIFICATIONS

### Skenario Alur
```
Kirim Pesan Internal:
notifications.html (daftar semua notif) → [Tulis Pesan] → compose.html
→ (pilih penerima: user/role) → kirim → penerima dapat notif bell icon di navbar

Broadcast ke Segmen:
broadcast.html → (pilih target: semua/role/segmen pelanggan)
→ (isi subject + body) → preview → kirim → log masuk di notification list

Template Pesan:
message_templates.html → [Buat Template] → (nama, subject, body dengan placeholder {customer_name} dll)
→ Template bisa dipilih saat compose/broadcast
```

### File & Koneksi MVC
| File HTML | View | Model |
|-----------|------|-------|
| `notifications.html` | `NotificationListView` | `lumra_config_notifications` (existing) |
| `compose.html` | `ComposeMessageView` | `lumra_config_messages` |
| `message_detail.html` | `MessageDetailView` | `lumra_config_messages` |
| `broadcast.html` | `BroadcastView` | `lumra_config_messages` + `lumra_config_customers` |
| `message_templates.html` | `MessageTemplateListView` | `lumra_config_message_templates` |

### ✅ Checklist MVC
- [ ] Navbar bell icon `notifCount` → diisi via context processor atau API endpoint `/api/notif/count/`
- [ ] Setelah operasi penting (approve opname, invoice jatuh tempo dll) → auto-create notifikasi via Django signals
- [ ] `broadcast.html` → bulk INSERT ke `lumra_config_notifications` untuk semua user target
- [ ] `message_templates.html` → template dengan placeholder `{customer_name}`, `{amount}`, dll → replace saat kirim

---

## 📈 MODUL 12 — REPORTS & ANALYTICS

### Skenario Alur
```
Dashboard Analytics:
sales_dashboard.html (KPI: revenue hari ini, transaksi, avg order, best seller)
sales_intelligence.html (trend, analisis produk, margin, ABC analysis)
sales_performance.html (target vs aktual per sales/lokasi)
market_insights.html (segmen pasar, customer behavior)
trends_analysis.html (tren waktu, seasonal, forecast)

Laporan Operasional:
reports/ → (list semua laporan yang tersedia)
sales_report.html → filter tanggal → export Excel/PDF
inventory_report.html → stok, pergerakan, aging
financial_reports.html → P&L, arus kas
operational_report.html → efisiensi operasional

Laporan Baru (Prioritas):
report_production.html (output vs target, waste %, cost/unit)
report_expiry.html (produk mendekati expired per lokasi)
report_customer_lifetime.html (CLV, frekuensi, avg order)
report_staff_performance.html (transaksi kasir, total nilai, jam kerja)
report_inventory_age.html (umur stok, qty, nilai, risk level)
```

### ✅ Checklist MVC
- [ ] Semua laporan menggunakan Django ORM aggregasi (`Count`, `Sum`, `Avg`) — hindari raw SQL kecuali terpaksa
- [ ] Filter tanggal semua laporan: `?date_from=2025-01-01&date_to=2025-12-31` via GET params
- [ ] Export Excel: gunakan `openpyxl` atau `xlwt` di view, return `HttpResponse` dengan `Content-Type: application/vnd.ms-excel`
- [ ] Export PDF: gunakan `weasyprint` atau `reportlab` — atau buka print template via JavaScript
- [ ] `report_expiry.html` bergantung pada `lumra_config_productbatches` (tabel 🆕 — harus ada dulu)
- [ ] `report_staff_performance.html` bergantung pada `orders.cashier_id` (field 🆕 yang perlu ditambah ke `orders`)
- [ ] `report_inventory_age.html` bergantung pada `stockmovement.created_at` untuk tanggal masuk pertama

---

## ⚙️ MODUL 13 — SETTINGS & SYSTEM

### Skenario Alur
```
Role & Permission:
roles.html → [Tambah Role] → role_form.html (checklist permission per modul)
permission_matrix.html (lihat semua kombinasi role × modul × aksi)

Pengaturan Dokumen:
numbering_settings.html (format nomor: INV-001, SO-2024-001, prefix custom, reset per tahun/bulan)
email_settings.html (SMTP, test kirim email)
notification_settings.html (aturan trigger notif, channel: in-app/email/push)

Backup & API:
backup_restore.html (download backup, upload restore, jadwal otomatis)
api_keys.html (kelola API key untuk integrasi eksternal)
```

### ✅ Checklist MVC
- [ ] `permission_matrix.html` → render tabel dari `django.contrib.auth` permissions, bukan hardcode
- [ ] `role_form.html` → simpan ke `django.contrib.auth.Group` + custom permission mapping
- [ ] Semua view sensitif (hapus, approve, export) harus dicek `request.user.has_perm('app.action_model')`
- [ ] `numbering_settings.html` → setting disimpan di `lumra_config_systemsettings` (key-value store)
- [ ] `email_settings.html` → tombol "Test Email" POST ke `/settings/email/test/` → kirim email ke user yang login
- [ ] `backup_restore.html` → backup via `manage.py dumpdata` (atau `pg_dump`) dijadikan file download

---

## 🗄️ DATABASE — TABEL BARU YANG HARUS DIBUAT

### 🔴 WAJIB (Bisnis tidak bisa jalan tanpa ini)

| Tabel Baru | Untuk |
|------------|-------|
| `lumra_config_stockmovement` | Audit trail semua perubahan stok |
| `lumra_config_returns` | Header retur/refund |
| `lumra_config_returnitems` | Detail item yang diretur |
| `lumra_config_payments` | Pencatatan pembayaran per order |
| `lumra_config_productbatches` | Tracking batch + expiry date |

### 🟡 SANGAT DISARANKAN

| Tabel Baru | Untuk |
|------------|-------|
| `lumra_config_unitconversions` | Konversi satuan (kg↔gram, liter↔ml) |
| `lumra_config_cashiershifts` | Buka/tutup shift kasir |
| `lumra_config_adjustmentreasons` | Kode alasan penyesuaian stok |

### Field Tambahan ke Tabel Existing

| Tabel | Field Baru |
|-------|-----------|
| `lumra_config_products` | `sell_price`, `barcode`, `min_stock`, `max_stock`, `is_active`, `track_batch`, `has_expiry` |
| `lumra_config_orders` | `order_type`, `payment_status`, `payment_method`, `paid_amount`, `change_amount`, `cashier_id`, `shift_id`, `table_number`, `dining_option` |
| `lumra_config_orderitems` | `cost_price`, `discount_amount`, `discount_percent`, `batch_id`, `notes` |
| `lumra_config_customers` | `customer_type`, `points_balance`, `total_purchases`, `visit_count`, `last_purchase_at`, `is_active` |
| `lumra_config_userprofile` | `role`, `default_location_id`, `is_active` |
| `lumra_config_stock` | `reserved_quantity`, `available_quantity` (generated column) |

---

## 🗓️ URUTAN PENGERJAAN YANG DISARANKAN

### MINGGU 1 — Fondasi
```
1. Cleanup 11 file duplikat
2. Buat tabel: stockmovement + tambah field orders + orderitems
3. Buat base partials: empty_state, pagination, confirm_modal, print_base
4. Fix views untuk stock_overview, stock_movement
```

### MINGGU 2 — Transaksi Inti
```
5. Buat tabel: payments + productbatches
6. POS → pastikan INSERT ke orders, orderitems, payments, stockmovement semuanya atomic (transaction)
7. Buat print_receipt.html (struk POS)
8. Buat batch_list, batch_form, expiry_tracking
```

### MINGGU 3 — Retur & Auth
```
9. Buat tabel: returns + returnitems
10. Buat retur_list, retur_form, retur_detail
11. Buat auth: forgot_password, reset_password, lock_screen
12. Buat print_invoice.html, print_purchase_order.html
```

### MINGGU 4 — Operasional Lengkap
```
13. Buat tabel: unitconversions + cashiershifts + adjustmentreasons
14. Buat invoice_list, invoice_form, invoice_detail, payment_list, payment_form
15. Onboarding wizard (welcome → step_business → step_location → step_category → complete)
16. Settings: roles, role_form, permission_matrix, numbering_settings
```

### MINGGU 5-8 — Field & Tambahan
```
17. Tambah field ke products, customers, userprofile, stock
18. Sales order & quotation flow lengkap
19. Production order (buat tabel dulu)
20. Marketing: campaign, voucher (buat tabel dulu)
21. Accounting dasar: COA, journal entry (Fase 3)
```

---

## 🚦 STATUS RINGKASAN PER MODUL

| Modul | Score Sekarang | Target | Blocker Utama |
|-------|---------------|--------|--------------|
| Base Components | 6/10 | 10/10 | Buat 9 partial baru |
| Authentication | 5/10 | 10/10 | Buat 6 halaman auth |
| Onboarding | 0/10 | 10/10 | Buat 5 halaman + logic |
| Inventory | 8/10 | 10/10 | Tabel batch + stockmovement |
| Sales & POS | 6/10 | 10/10 | Tabel payments + returns |
| Production | 2/10 | 10/10 | Tabel production order |
| Marketing | 4/10 | 10/10 | Semua tabel belum ada |
| Master Data | 7/10 | 10/10 | Tabel tax, bank, tags |
| Accounting | 0/10 | 8/10 | Semua tabel belum ada (Fase 3) |
| Print Templates | 0/10 | 10/10 | Template belum ada |
| Messages | 2/10 | 10/10 | Buat 4 halaman |
| Reports | 9/10 | 10/10 | 5 laporan baru + tabel expiry |
| Settings | 7/10 | 10/10 | Roles, permission matrix |
| Error Pages | 8/10 | 10/10 | 2 halaman baru |

---

*Dokumen ini dibuat berdasarkan Review LUMRA ERP Template Catalog. Update checklist ini setiap kali sebuah file selesai dibuat dan diintegrasikan.*