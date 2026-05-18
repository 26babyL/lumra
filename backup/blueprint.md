# Lumra ERP — Blueprint & Route Map
> Versi: 3.0.0 · Generated: 2026-03-23 · Total template: 103 file

---

## Daftar Isi

1. [Struktur Proyek](#1-struktur-proyek)
2. [Design System — Color Tokens](#2-design-system--color-tokens)
3. [Design System — Glass & Surface](#3-design-system--glass--surface)
4. [Design System — Typography](#4-design-system--typography)
5. [Komponen Base](#5-komponen-base)
6. [Route Map — Semua Halaman](#6-route-map--semua-halaman)
   - [Auth](#61-auth)
   - [Dashboard](#62-dashboard)
   - [Inventory](#63-inventory)
   - [Master Data](#64-master-data)
   - [Sales & Insight](#65-sales--insight)
   - [Marketing](#66-marketing)
   - [Production](#67-production)
   - [Reports](#68-reports)
   - [Messages](#69-messages)
   - [Settings](#610-settings)
   - [Error Pages](#611-error-pages)
7. [Matriks Fitur per Modul](#7-matriks-fitur-per-modul)
8. [Checklist Review & QA](#8-checklist-review--qa)
9. [Known Issues & Todo](#9-known-issues--todo)

---

## 1. Struktur Proyek

```
lumra/
└── lumra_config/
    └── templates/
        ├── base/                          # Komponen global
        │   ├── base.html                  # Layout utama (extends semua page)
        │   ├── navbar.html                # Top navigation bar
        │   ├── sidebar.html               # Left sidebar navigation
        │   ├── sidebar1.html              # Sidebar variant
        │   ├── sidebar_item.html          # Sidebar nav item partial
        │   ├── sidebar_right.html         # Right panel sidebar
        │   ├── footer.html                # Footer
        │   ├── kpi_card.html              # KPI card komponen
        │   ├── kpi_card_inner.html        # KPI card inner layout
        │   ├── kpi_card_white.html        # KPI card varian putih
        │   ├── activity_drawer.html       # Side drawer aktivitas
        │   ├── alert.html                 # Alert/notifikasi global
        │   ├── alert_inner.html           # Alert inner content
        │   ├── approval_modal.html        # Modal approval workflow
        │   └── partials/
        │       ├── bg_blob.html           # Ambient background blobs
        │       └── form_field.html        # Form field reusable
        │
        └── lumra_pages/
            ├── auth/                      # 2 halaman
            ├── etc/                       # 3 halaman (error)
            ├── inventory/                 # 14 halaman
            ├── marketing/                 # 5 halaman
            ├── master_data/               # 16 halaman
            ├── messages/                  # 2 halaman
            ├── production/                # 3 halaman
            ├── reports/                   # 20 halaman
            ├── sales_insight/             # 7 halaman
            └── settings/                 # 13 halaman
```

**Total: 103 template aktif** (tidak termasuk backup folder)

---

## 2. Design System — Color Tokens

### Brand Primary — Emerald Jewel Tone

| Token | Hex | Penggunaan |
|---|---|---|
| `--color-emerald-50` | `#E6F2EE` | Background subtle, hover state |
| `--color-emerald-100` | `#C0DFCF` | Border halus, divider |
| `--color-emerald-200` | `#90C4AC` | Icon background |
| `--color-emerald-300` | `#5DA88A` | Accent glow, gradient stop |
| `--color-emerald-400` | `#2E8C69` | Primary light, hover |
| `--color-emerald-500` | `#00674F` | **Brand primary — warna utama** |
| `--color-emerald-600` | `#005A44` | Primary dark hover |
| `--color-emerald-700` | `#004D39` | Strong press state |
| `--color-emerald-800` | `#003D2C` | Text on light bg |
| `--color-emerald-900` | `#002D1F` | Deep dark |
| `--color-emerald-950` | `#001A12` | Darkest, almost black |

**Alias yang dipakai di CSS:**
```css
--color-primary        : #00674F   /* emerald-500 */
--color-primary-light  : #2E8C69   /* emerald-400 */
--color-primary-subtle : #E6F2EE   /* emerald-50  */
--color-primary-dark   : #003D2C   /* emerald-800 */
--color-primary-glow   : #5DA88A   /* emerald-300 */
```

### Neutral Scale — Slate

| Token | Hex | Penggunaan |
|---|---|---|
| `--color-slate-50` | `#F8FAFC` | Page background alternatif |
| `--color-slate-100` | `#F1F5F9` | Surface subtle, skeleton |
| `--color-slate-200` | `#E2E8F0` | Border default, divider |
| `--color-slate-300` | `#CBD5E1` | Scrollbar thumb, placeholder |
| `--color-slate-400` | `#94A3B8` | Text subtle, icon disabled |
| `--color-slate-500` | `#64748B` | Text muted, label |
| `--color-slate-600` | `#475569` | Text secondary |
| `--color-slate-700` | `#334155` | Text strong |
| `--color-slate-800` | `#1E293B` | Text heading |
| `--color-slate-900` | `#0F172A` | Text primary / body |
| `--color-slate-950` | `#020617` | Near-black |

### Semantic Colors

| Token | Hex | Penggunaan |
|---|---|---|
| `--color-success` | `#00674F` | Sama dengan brand primary |
| `--color-success-bg` | `rgba(230,242,238,0.80)` | Badge/alert background |
| `--color-success-border` | `rgba(93,168,138,0.40)` | Badge border |
| `--color-success-text` | `#003D2C` | Badge text |
| `--color-warning` | `#D97706` | Warning state |
| `--color-warning-bg` | `rgba(254,243,199,0.80)` | |
| `--color-warning-border` | `rgba(251,191,36,0.40)` | |
| `--color-warning-text` | `#92400E` | |
| `--color-danger` | `#E11D48` | Error, delete action |
| `--color-danger-bg` | `rgba(255,228,230,0.80)` | |
| `--color-danger-border` | `rgba(251,113,133,0.40)` | |
| `--color-danger-text` | `#9F1239` | |
| `--color-info` | `#0284C7` | Informasi, link |
| `--color-info-bg` | `rgba(224,242,254,0.80)` | |
| `--color-info-border` | `rgba(125,211,252,0.40)` | |
| `--color-info-text` | `#075985` | |
| `--color-accent` | `#4F46E5` | Indigo accent, highlight |
| `--color-accent-bg` | `rgba(238,242,255,0.80)` | |
| `--color-accent-border` | `rgba(165,180,252,0.40)` | |
| `--color-accent-text` | `#3730A3` | |

### KPI Card Accent Colors

Setiap KPI card punya corner accent berbeda sesuai konteks:

| Class | Warna | Dipakai untuk |
|---|---|---|
| `.kpi-card.em` | `#059669` | Revenue, profit, target tercapai |
| `.kpi-card.blue` | `#3b82f6` | Volume, count, transaksi |
| `.kpi-card.vio` | `#8b5cf6` | Loyalty, membership |
| `.kpi-card.rose` | `#f43f5e` | Alert, stock kritis, refund |
| `.kpi-card.amber` | `#f59e0b` | Pending, warning, purchase |

### Page Background

```css
--color-bg: #F5F8F7   /* Emerald-tinted off-white — bukan pure white */
```

---

## 3. Design System — Glass & Surface

### Glass Tokens (SSOT di lumra.config.json)

| Token | Nilai | Keterangan |
|---|---|---|
| `--glass-bg` | `rgba(255,255,255,0.82)` | Surface utama semua card |
| `--glass-bg-strong` | `rgba(255,255,255,0.96)` | Modal, dialog (lebih opaque) |
| `--glass-bg-subtle` | `rgba(255,255,255,0.48)` | Hover overlay, subtle surface |
| `--glass-border` | `rgba(255,255,255,0.20)` | Border glass — untuk konteks gelap/berwarna |
| `--glass-border-em` | `rgba(0,103,79,0.12)` | Border dengan tint emerald |
| `--glass-blur` | `blur(14px) saturate(180%)` | Backdrop filter utama |
| `--glass-blur-sm` | `blur(8px) saturate(160%)` | Blur ringan (tooltip, kecil) |
| `--glass-blur-lg` | `blur(28px) saturate(200%)` | Blur kuat (modal overlay) |
| `--glass-shadow` | `0 2px 12px rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.04)` | Shadow card standar |
| `--glass-shadow-lg` | `0 8px 32px rgba(0,0,0,0.10), 0 0 0 0.5px rgba(0,0,0,0.04)` | Shadow hover |
| `--glass-shadow-glow` | `0 8px 32px rgba(0,0,0,0.08), 0 0 28px rgba(0,103,79,0.12)` | Shadow dengan emerald glow |
| `--glass-dark-bg` | `rgba(15,23,42,0.82)` | Modal overlay backdrop |
| `--glass-dark-blur` | `blur(6px)` | Backdrop modal |
| `--glass-dark-border` | `rgba(255,255,255,0.06)` | Border dark mode |

### ⚠️ Penting: Dua Jenis Border

Ini adalah sumber konflik utama yang menyebabkan border hilang:

| Situasi | Token yang benar | Alasan |
|---|---|---|
| Card/panel glass di atas background berwarna | `--glass-border` `rgba(255,255,255,0.20)` | Kontras terhadap background emerald |
| Table, form, divider di atas **background putih** | `--color-border` `rgba(203,213,225,0.70)` | Slate — terlihat di atas putih |
| Input focus | `--color-border-focus` `#00674F` | Brand color |
| Shadow separator | `--shadow-focus` | 3px emerald glow ring |

### Shadow Scale

```css
--shadow-xs  : 0 1px 2px rgba(0,0,0,0.04)
--shadow-sm  : 0 1px 4px rgba(0,0,0,0.05), 0 0 0 0.5px rgba(0,0,0,0.03)
--shadow-md  : 0 2px 12px rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.03)  ← card default
--shadow-lg  : 0 4px 24px rgba(0,0,0,0.08), 0 0 0 0.5px rgba(0,0,0,0.03)  ← hover
--shadow-xl  : 0 8px 40px rgba(0,0,0,0.10), 0 0 0 0.5px rgba(0,0,0,0.03)  ← dropdown
--shadow-2xl : 0 20px 60px rgba(0,0,0,0.14), 0 0 0 0.5px rgba(0,0,0,0.02) ← modal
```

---

## 4. Design System — Typography

### Font Stack

| Token | Font | Dipakai untuk |
|---|---|---|
| `--font-sans` | `Inter, system-ui` | Body, UI, label, button |
| `--font-display` | `DM Sans, Inter` | Heading, page title, KPI label |
| `--font-mono` | `JetBrains Mono, Fira Code` | Angka KPI, kode, data numerik |

### Scale

| Token | Ukuran | Contoh penggunaan |
|---|---|---|
| `--text-xs` | `0.6875rem` (11px) | Label overline, tag kecil |
| `--text-sm` | `0.8125rem` (13px) | Table cell, form help text |
| `--text-base` | `0.9375rem` (15px) | Body default |
| `--text-md` | `1rem` (16px) | Card title, button |
| `--text-lg` | `1.125rem` (18px) | Section title |
| `--text-xl` | `1.25rem` (20px) | Card heading besar |
| `--text-2xl` | `1.5rem` (24px) | KPI value |
| `--text-3xl` | `1.875rem` (30px) | Page title mobile |
| `--text-4xl` | `2.25rem` (36px) | Page title desktop |

### Aturan Tipografi

- **Heading** → `font-family: var(--font-display)`, `font-weight: 600`, `letter-spacing: -0.02em`
- **Angka/KPI** → `font-family: var(--font-mono)`, `font-variant-numeric: tabular-nums`
- **Label uppercase** → `font-size: var(--text-xs)`, `letter-spacing: 0.12em`, `text-transform: uppercase`
- **Body** → `font-family: var(--font-sans)`, `font-weight: 400`, `line-height: 1.6`

---

## 5. Komponen Base

### `base.html` — Layout Induk

Semua page extends file ini. Menyediakan:
- `{% block extra_css %}` — CSS spesifik halaman
- `{% block content %}` — Konten utama
- `{% block extra_js %}` — JS spesifik halaman
- Include otomatis: navbar, sidebar, footer, bg_blob

### `navbar.html`

| Elemen | Deskripsi |
|---|---|
| Logo + nama bisnis | Kiri, link ke dashboard |
| Store switcher | Dropdown pilih toko/outlet |
| Search bar | Global search produk, lokasi, stok |
| Keyboard shortcut | `/` untuk fokus search |
| Notification bell | Badge jumlah notifikasi baru |
| User avatar + name | Dropdown profil, logout |

### `sidebar.html`

Navigasi kiri dengan struktur:

```
OPERATIONS
  ├── Dashboard
  └── Point of Sale

LOGISTICS
  ├── Inventory  (collapsible)
  └── Locations

PROCUREMENT
  └── Procurement (collapsible)

ANALYTICS
  ├── Customers
  └── Sales & Insight (collapsible)

[bottom]
  ├── User avatar + name
  └── Logout
```

### `kpi_card.html`

KPI card dengan varian:
- `.kpi-card.em` — emerald accent
- `.kpi-card.blue` — blue accent
- `.kpi-card.vio` — violet accent
- `.kpi-card.rose` — rose accent
- `.kpi-card.amber` — amber accent

Anatomy card:
```
┌─────────────────────────────┐ ← frosted top edge (::before)
│ [icon] LABEL OVERLINE       │ ← kpi-label, font-mono kecil
│ 12,345                      │ ← kpi-val, font-mono besar
│ ↑ +12.5% vs kemarin         │ ← delta badge
└─────────────────────────────┘ ← corner accent (::after)
```

### `approval_modal.html`

Modal untuk workflow approval:
- Approve / Reject action
- Comment field
- Status badge current

### `activity_drawer.html`

Side panel aktivitas terkini:
- Timeline event list
- Filter by type
- Timestamp relative

### `form_field.html` (partial)

Reusable form field:
- Label + required indicator
- Input / Select / Textarea
- Help text
- Error message state

---

## 6. Route Map — Semua Halaman

---

### 6.1 Auth

#### `auth/login.html`
- **Route:** `/login/`
- **Layout:** Standalone (tidak extends base.html)
- **Fitur:**
  - Form email + password
  - Remember me checkbox
  - Link "Lupa password"
  - Business branding (logo, nama)
  - Background dengan blob ambient
- **Warna dominan:** Emerald primary, background `#F5F8F7`

#### `auth/register.html`
- **Route:** `/register/`
- **Layout:** Standalone
- **Fitur:**
  - Form registrasi bisnis baru
  - Nama bisnis, email, password, konfirmasi
  - Terms & conditions checkbox
- **Warna dominan:** Sama dengan login

---

### 6.2 Dashboard

#### `sales_insight/dashboard.html`
- **Route:** `/dashboard/`
- **Sidebar aktif:** Dashboard
- **Fitur:**
  - KPI row: Revenue hari ini, Transaksi, AOV, Profit
  - Grafik penjualan (line chart, 7/30 hari)
  - Top 5 produk terlaris
  - Recent transactions list
  - Stock alert widget (stok mendekati habis)
  - Store switcher context
- **Komponen:** `kpi_card.html` ×4, chart area, table recent tx
- **Warna KPI:** `.em` revenue · `.blue` transaksi · `.amber` AOV · `.vio` profit

---

### 6.3 Inventory

#### `inventory/products.html`
- **Route:** `/inventory/products/`
- **Fitur:**
  - Grid/list view toggle
  - Filter: kategori, supplier, status stok
  - Search produk
  - Card produk: foto, nama, SKU, harga, stok
  - Quick action: edit, hapus, lihat detail
  - Pagination

#### `inventory/product_list.html`
- **Route:** `/inventory/product-list/`
- **Fitur:**
  - Table view produk (alternatif dari products.html)
  - Sort by: nama, stok, harga, kategori
  - Bulk select + bulk action
  - Export CSV/Excel
  - Filter panel collapsible

#### `inventory/product_details.html`
- **Route:** `/inventory/products/<id>/`
- **Fitur:**
  - Header: foto produk, nama, SKU, status
  - Tab: Info Umum · Stok · Harga Supplier · Riwayat Mutasi
  - Info umum: kategori, unit, deskripsi, barcode
  - Stok per lokasi (tabel)
  - Grafik pergerakan stok (30 hari)
  - Supplier price list
  - Tombol: Edit Produk, Tambah Stok, Stock Opname

#### `inventory/stock_overview.html`
- **Route:** `/inventory/stock-overview/`
- **Fitur:**
  - KPI: Total SKU, Total Value, Low Stock, Out of Stock
  - Tabel stok semua produk dengan color-coded status
  - Filter lokasi, kategori
  - Export

#### `inventory/stock_movement.html`
- **Route:** `/inventory/stock-movement/`
- **Fitur:**
  - Timeline/log semua mutasi stok
  - Filter: tanggal, tipe (in/out/transfer), produk, lokasi
  - Detail tiap mutasi: qty, dari/ke, alasan, user, timestamp
  - Export

#### `inventory/stock_movement_form.html`
- **Route:** `/inventory/stock-movement/new/`
- **Fitur:**
  - Form tambah mutasi stok manual
  - Pilih produk (autocomplete)
  - Tipe: Masuk / Keluar / Transfer
  - Qty, lokasi asal/tujuan, catatan
  - Validasi stok tersedia

#### `inventory/add_stock_movement.html`
- **Route:** `/inventory/add-stock-movement/`
- **Fitur:** Serupa stock_movement_form — kemungkinan halaman terpisah untuk flow "tambah stok" cepat dari dashboard

#### `inventory/stock_planning.html`
- **Route:** `/inventory/stock-planning/`
- **Fitur:**
  - Rekomendasi reorder berdasarkan rata-rata penjualan
  - Par level setting per produk per lokasi
  - Alert stok di bawah par level
  - Tabel: produk · stok sekarang · par level · rekomendasi order · supplier

#### `inventory/stock_purchasing.html`
- **Route:** `/inventory/stock-purchasing/`
- **Fitur:**
  - Daftar purchase order
  - Status: Draft · Dikirim · Diterima sebagian · Selesai
  - Filter vendor, tanggal, status
  - Tombol buat PO baru

#### `inventory/stock_opname_locations.html`
- **Route:** `/inventory/stock-opname/locations/`
- **Fitur:**
  - Pilih lokasi untuk memulai sesi stock opname
  - Status opname per lokasi: Belum · Sedang berjalan · Selesai

#### `inventory/stock_opname_form.html`
- **Route:** `/inventory/stock-opname/<session_id>/`
- **Fitur:**
  - Form entry hasil hitung fisik per produk
  - Sistem stok (ekspektasi) vs fisik (input user)
  - Selisih otomatis dihitung
  - Simpan draft / Submit untuk approval

#### `inventory/stock_opname_approvals.html`
- **Route:** `/inventory/stock-opname/approvals/`
- **Fitur:**
  - Daftar sesi opname yang menunggu approval
  - Filter status: Pending · Approved · Rejected
  - Bulk approve

#### `inventory/stock_opname_approval_detail.html`
- **Route:** `/inventory/stock-opname/approvals/<id>/`
- **Fitur:**
  - Detail sesi opname
  - Tabel: produk · sistem · fisik · selisih · nilai selisih
  - Tombol Approve / Reject dengan comment
  - Menggunakan `approval_modal.html`

#### `inventory/supplier_price_list.html`
- **Route:** `/inventory/supplier-prices/`
- **Fitur:**
  - Daftar harga beli per produk per supplier
  - Filter produk, supplier
  - Tabel: produk · supplier · harga · tanggal update · min order

#### `inventory/supplier_price_form.html`
- **Route:** `/inventory/supplier-prices/new/` atau `/<id>/edit/`
- **Fitur:**
  - Form harga supplier: produk, supplier, harga, min qty, berlaku mulai

#### `inventory/supplier_price_confirm_delete.html`
- **Route:** `/inventory/supplier-prices/<id>/delete/`
- **Fitur:**
  - Konfirmasi hapus harga supplier
  - Tampilkan detail yang akan dihapus

---

### 6.4 Master Data

#### `master_data/customers.html` & `customers_list.html`
- **Route:** `/customers/` · `/customers/list/`
- **Sidebar aktif:** Customers
- **Fitur:**
  - KPI: Total pelanggan, Member aktif, Churn rate, Avg spend
  - Table: nama, kontak, tier (Regular/Silver/Gold/Platinum/VIP), poin, lifetime value, kunjungan terakhir
  - Filter tier, sort
  - Pagination (12,359+ pelanggan dari screenshot)
  - Export
  - Tombol "Pelanggan Baru"

#### `master_data/customer.html`
- **Route:** `/customers/<id>/`
- **Fitur:** Redirect atau alias ke customer_detail

#### `master_data/customer_detail.html`
- **Route:** `/customers/<id>/detail/`
- **Fitur:**
  - Header: avatar, nama, tier badge, poin
  - Tab: Profil · Riwayat Transaksi · Loyalty · Aktivitas
  - Profil: email, HP, alamat, tanggal daftar
  - Riwayat transaksi: tabel + chart spending
  - Loyalty: poin history, rewards yang ditukar
  - Tombol: Edit, Tambah Poin Manual

#### `master_data/customer_form.html`
- **Route:** `/customers/new/` · `/customers/<id>/edit/`
- **Fitur:**
  - Form pelanggan: nama, email, HP, tanggal lahir, alamat
  - Assign tier manual (opsional)

#### `master_data/locations.html`
- **Route:** `/locations/`
- **Sidebar aktif:** Locations
- **Fitur:**
  - Grid card lokasi/outlet
  - Map view toggle
  - Card: nama toko, alamat, status (Aktif/Nonaktif), jumlah produk
  - Filter status
  - Tombol tambah lokasi

#### `master_data/location_list.html`
- **Route:** `/locations/list/`
- **Fitur:** Table view alternatif untuk locations

#### `master_data/categories_list.html`
- **Route:** `/master-data/categories/`
- **Fitur:**
  - Daftar kategori produk
  - Hierarki (parent/child)
  - Jumlah produk per kategori
  - CRUD actions

#### `master_data/category_form.html`
- **Route:** `/master-data/categories/new/` · `/<id>/edit/`
- **Fitur:** Form kategori: nama, parent, deskripsi, ikon

#### `master_data/units_list.html`
- **Route:** `/master-data/units/`
- **Fitur:**
  - Daftar satuan (pcs, kg, liter, lusin, dll)
  - Konversi antar satuan
  - CRUD

#### `master_data/unit_form.html`
- **Route:** `/master-data/units/new/` · `/<id>/edit/`
- **Fitur:** Form satuan: nama, singkatan, konversi

#### `master_data/vendors_list.html` & `vendor_list.html`
- **Route:** `/master-data/vendors/`
- **Fitur:**
  - Daftar supplier/vendor
  - Info: nama, kontak, kategori produk supplied
  - Filter, search
  - CRUD

#### `master_data/vendor_form.html`
- **Route:** `/master-data/vendors/new/` · `/<id>/edit/`
- **Fitur:** Form vendor: nama, kontak, alamat, payment terms

#### `master_data/stock_opname.html`
- **Route:** `/master-data/stock-opname/`
- **Fitur:**
  - Daftar semua sesi stock opname historis
  - Filter lokasi, tanggal, status
  - Link ke detail sesi

#### `master_data/stock_opname_session_detail.html`
- **Route:** `/master-data/stock-opname/<session_id>/`
- **Fitur:**
  - Detail lengkap satu sesi opname
  - Summary: total SKU, selisih, nilai
  - Tabel per-produk lengkap

---

### 6.5 Sales & Insight

#### `sales_insight/financial_reports.html`
- **Route:** `/sales-insight/financial/`
- **Sidebar aktif:** Sales & Insight
- **Fitur:**
  - KPI: Revenue, COGS, Gross Profit, Net Profit, Margin %
  - Date range picker (preset: hari ini, minggu, bulan, custom)
  - Tab: P&L · Arus Kas · Balance
  - Chart: Revenue vs COGS trend
  - Tabel breakdown per kategori
  - Export PDF/Excel

#### `sales_insight/sales_performance.html`
- **Route:** `/sales-insight/performance/`
- **Fitur:**
  - KPI: Total sales, target achievement %, growth vs periode lalu
  - Grafik perbandingan outlet
  - Leaderboard produk
  - Heatmap jam penjualan
  - Filter outlet, range tanggal

#### `sales_insight/sales_intelligence.html`
- **Route:** `/sales-insight/intelligence/`
- **Fitur:**
  - AI-powered insights
  - Anomali deteksi (penurunan tiba-tiba, spike)
  - Produk berisiko discontinue
  - Rekomendasi aksi

#### `sales_insight/market_insights.html`
- **Route:** `/sales-insight/market/`
- **Fitur:**
  - Tren kategori produk
  - Analisis kompetitor (jika ada data)
  - Musiman pattern
  - Chart perbandingan periode

#### `sales_insight/trends_analysis.html`
- **Route:** `/sales-insight/trends/`
- **Fitur:**
  - Tren jangka panjang (3-12 bulan)
  - Forecast penjualan
  - Korelasi event/promo dengan penjualan
  - Export data

#### `sales_insight/pos.html`
- **Route:** `/pos/`
- **Sidebar aktif:** Point of Sale
- **Fitur:**
  - Interface kasir
  - Grid produk + search
  - Keranjang belanja
  - Hitung kembalian
  - Pilih metode bayar
  - Print struk
  - Diskon/voucher apply

---

### 6.6 Marketing

#### `marketing/campaign_list.html`
- **Route:** `/marketing/campaigns/`
- **Fitur:**
  - Daftar kampanye marketing
  - Status: Draft · Aktif · Selesai · Dijadwalkan
  - Filter status, tanggal
  - KPI ringkas: total campaign, aktif, reach

#### `marketing/campaign.html`
- **Route:** `/marketing/campaigns/<id>/`
- **Fitur:**
  - Detail satu campaign
  - Performa: reach, conversion, revenue attributed
  - Audience: segmen yang ditarget
  - Timeline campaign

#### `marketing/add_campaign.html`
- **Route:** `/marketing/campaigns/new/`
- **Fitur:**
  - Form buat campaign baru
  - Nama, tipe (promo/loyalty/event), segmen target
  - Tanggal mulai-selesai
  - Budget, reward/diskon

#### `marketing/discount.html`
- **Route:** `/marketing/discounts/`
- **Fitur:**
  - Daftar diskon aktif
  - Tipe: persentase, nominal, BOGO, bundle
  - Kondisi: minimum transaksi, produk tertentu, hari/jam tertentu
  - Toggle aktif/nonaktif

#### `marketing/loyalty_members.html`
- **Route:** `/marketing/loyalty/`
- **Fitur:**
  - Statistik loyalty program
  - Distribusi tier member
  - Poin yang beredar
  - Aktivitas redemption terbaru
  - Setting tier (threshold poin)

---

### 6.7 Production

#### `production/recipe_list.html`
- **Route:** `/production/recipes/`
- **Fitur:**
  - Daftar resep/BOM (Bill of Materials)
  - Card: nama produk, jumlah bahan, COGS estimasi
  - Filter kategori

#### `production/recipe_detail.html`
- **Route:** `/production/recipes/<id>/`
- **Fitur:**
  - Detail resep: bahan-bahan + qty + satuan
  - COGS breakdown
  - Yield (berapa porsi per batch)
  - Riwayat perubahan

#### `production/recipe_form.html`
- **Route:** `/production/recipes/new/` · `/<id>/edit/`
- **Fitur:**
  - Form resep
  - Dynamic row bahan (tambah/hapus baris)
  - Autocomplete bahan dari produk inventory
  - COGS auto-kalkulasi

---

### 6.8 Reports

#### `reports/reporting.html`
- **Route:** `/reports/`
- **Fitur:** Hub semua laporan — grid link ke sub-report

#### `reports/sales_report.html` & `sales_report_after.html`
- **Route:** `/reports/sales/`
- **Fitur:**
  - Laporan penjualan harian/mingguan/bulanan
  - Filter outlet, kasir, metode bayar
  - Tabel transaksi + summary
  - Chart revenue

#### `reports/sales_history.html` & `sales_history_product.html`
- **Route:** `/reports/sales-history/`
- **Fitur:**
  - Riwayat penjualan lengkap
  - Filter tanggal, produk, outlet
  - Drill-down ke transaksi individual

#### `reports/report_sales_summary.html`
- **Route:** `/reports/sales-summary/`
- **Fitur:**
  - Ringkasan penjualan — 1 halaman printable
  - Total revenue, qty terjual, avg transaksi
  - Per-outlet breakdown

#### `reports/report_sales_by_product.html`
- **Route:** `/reports/sales-by-product/`
- **Fitur:**
  - Revenue per produk, ranking
  - Qty terjual, margin per produk
  - Chart pareto

#### `reports/report_sales_by_outlet.html`
- **Route:** `/reports/sales-by-outlet/`
- **Fitur:** Perbandingan revenue antar outlet/lokasi

#### `reports/report_sales_by_payment.html`
- **Route:** `/reports/sales-by-payment/`
- **Fitur:** Breakdown revenue per metode pembayaran (cash, QRIS, kartu, dll)

#### `reports/report_profit_loss_detail.html`
- **Route:** `/reports/profit-loss/`
- **Fitur:**
  - P&L detail per periode
  - Revenue, COGS, gross profit, opex, net profit
  - Tabel + chart waterfall

#### `reports/report_inventory_stock.html`
- **Route:** `/reports/inventory-stock/`
- **Fitur:** Snapshot stok semua produk pada tanggal tertentu

#### `reports/report_inventory_log.html`
- **Route:** `/reports/inventory-log/`
- **Fitur:** Log semua perubahan stok (audit trail)

#### `reports/report_inventory_low.html`
- **Route:** `/reports/inventory-low/`
- **Fitur:** Daftar produk dengan stok di bawah par level

#### `reports/transaction_summary.html`
- **Route:** `/reports/transactions/`
- **Fitur:** Summary semua transaksi dengan filter lengkap

#### `reports/purchasing_report.html`
- **Route:** `/reports/purchasing/`
- **Fitur:** Laporan pembelian ke supplier, total spend per vendor

#### `reports/requisition_report.html`
- **Route:** `/reports/requisitions/`
- **Fitur:** Laporan permintaan stok/purchase requisition

#### `reports/transfer_report.html`
- **Route:** `/reports/transfers/`
- **Fitur:** Laporan transfer stok antar lokasi

#### `reports/activity_log.html` & `report_activity_log.html`
- **Route:** `/reports/activity-log/`
- **Fitur:**
  - Log semua aktivitas user di sistem
  - Filter: user, modul, tanggal, tipe aksi
  - Audit trail lengkap

#### `reports/sales_history.html`
- **Route:** `/reports/sales-history/`
- **Fitur:** Riwayat penjualan historis

#### `reports/base_report.html`
- **Tipe:** Base template untuk semua laporan
- **Menyediakan:** Header laporan, filter area, export button, print button

---

### 6.9 Messages

#### `messages/inbox.html`
- **Route:** `/messages/inbox/`
- **Fitur:**
  - Daftar pesan/komunikasi internal
  - Filter: belum dibaca, semua
  - Thread view

#### `messages/notification.html`
- **Route:** `/messages/notifications/`
- **Fitur:**
  - Semua notifikasi sistem
  - Kategori: stok, approval, transaksi, sistem
  - Mark as read / mark all read

---

### 6.10 Settings

#### `settings/settings.html`
- **Route:** `/settings/`
- **Fitur:** Hub settings — grid navigasi ke sub-settings

#### `settings/business_profile.html`
- **Route:** `/settings/business/profile/`
- **Fitur:**
  - Nama bisnis, logo, tagline
  - Alamat lengkap
  - Kontak (telp, email, website)
  - Upload logo

#### `settings/business_form_general.html`
- **Route:** `/settings/business/general/`
- **Fitur:**
  - Zona waktu, bahasa, mata uang
  - Format tanggal/angka
  - Pengaturan pajak (PPN %)
  - Rounding rules

#### `settings/business_settings.html`
- **Route:** `/settings/business/settings/`
- **Fitur:**
  - Pengaturan operasional
  - Jam operasional per outlet
  - Kebijakan retur
  - Receipt/struk settings

#### `settings/business_feature_matrix.html`
- **Route:** `/settings/business/features/`
- **Fitur:**
  - Toggle fitur aktif/nonaktif per plan
  - Matriks fitur vs outlet
  - Upgrade plan CTA

#### `settings/user_list.html`
- **Route:** `/settings/users/`
- **Fitur:**
  - Daftar semua user sistem
  - Role badge tiap user
  - Status aktif/nonaktif
  - Tombol undang user baru

#### `settings/users.html`
- **Route:** `/settings/users/manage/`
- **Fitur:**
  - Manage user detail
  - Assign outlet/lokasi akses

#### `settings/user_roles_permissions.html`
- **Route:** `/settings/roles/`
- **Fitur:**
  - Daftar role (Admin, Manager, Kasir, Gudang, dll)
  - Matrix permission per role per modul
  - CRUD role custom

#### `settings/profile.html`
- **Route:** `/settings/profile/`
- **Fitur:**
  - Edit profil user yang login
  - Foto profil, nama, email
  - Ganti password
  - Preferensi notifikasi

#### `settings/search.html`
- **Route:** `/settings/search/`
- **Fitur:**
  - Global search settings dan konten
  - Quick navigation

#### `settings/system_status.html`
- **Route:** `/settings/system-status/`
- **Fitur:**
  - Status komponen sistem (DB, cache, queue, storage)
  - Uptime, latency
  - Recent error log
  - Version info

#### `settings/about.html`
- **Route:** `/settings/about/`
- **Fitur:**
  - Info versi aplikasi
  - Changelog
  - License

#### `settings/contact.html`
- **Route:** `/settings/contact/`
- **Fitur:**
  - Form kontak support
  - Info kontak Lumra

---

### 6.11 Error Pages

#### `etc/error_403.html`
- **Layout:** Standalone (tidak extends base)
- **Fitur:** Pesan akses ditolak, link kembali ke dashboard

#### `etc/error_404.html`
- **Layout:** Standalone
- **Fitur:** Halaman tidak ditemukan, link kembali, search

#### `etc/error_500.html`
- **Layout:** Standalone
- **Fitur:** Server error, pesan user-friendly, link lapor masalah

---

## 7. Matriks Fitur per Modul

| Fitur | Dashboard | Inventory | Master Data | Sales Insight | Marketing | Production | Reports | Settings |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| KPI Cards | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| Table + Sort | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Search/Filter | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export CSV/Excel | — | ✅ | ✅ | ✅ | — | — | ✅ | — |
| Export PDF | — | — | — | ✅ | — | — | ✅ | — |
| Charts/Grafik | ✅ | ✅ | — | ✅ | ✅ | — | ✅ | — |
| Form CRUD | — | ✅ | ✅ | — | ✅ | ✅ | — | ✅ |
| Approval Workflow | — | ✅ | — | — | — | — | — | — |
| Pagination | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bulk Action | — | ✅ | ✅ | — | — | — | — | — |
| Print View | — | — | — | ✅ | — | — | ✅ | — |
| Date Range Picker | ✅ | ✅ | — | ✅ | ✅ | — | ✅ | — |
| Store Switcher | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| Role-based Access | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Glassmorphism UI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 8. Checklist Review & QA

### Design System Consistency

- [ ] Semua page extends `base.html`
- [ ] Font import hanya via `lumra_design_system.css` (tidak ada `@import Syne` di template)
- [ ] Tidak ada warna hardcoded di luar `:root` (jalankan `validate.py`)
- [ ] Semua border tabel pakai `--color-border` bukan `--glass-border`
- [ ] Semua border glass pakai `--glass-border`
- [ ] KPI nilai pakai `font-family: var(--font-mono)`
- [ ] Heading pakai `font-family: var(--font-display)`
- [ ] `--color-bg: #F5F8F7` sebagai background (bukan `#fff` atau `bg-white`)

### Komponen

- [ ] `kpi_card.html` dipakai konsisten (bukan definisi ulang per halaman)
- [ ] `form_field.html` dipakai untuk semua form input
- [ ] `bg_blob.html` ada di setiap halaman (via base.html)
- [ ] `approval_modal.html` dipakai untuk semua approval flow
- [ ] Toast notification konsisten

### Tier Badge Warna

- [ ] `Regular` → `.chip-neutral` abu-abu
- [ ] `Silver` → `.chip-info` biru muda
- [ ] `Gold` → `.chip-amber` kuning
- [ ] `Platinum` → `.chip-accent` indigo
- [ ] `VIP` → `.chip-rose` merah muda

### Tabel

- [ ] Semua tabel pakai `.lumra-table`
- [ ] `thead` background `rgba(0,0,0,0.02)`
- [ ] `th` font: uppercase, `0.12em` letter-spacing, slate-400
- [ ] Border row: `--color-border` (bukan `--glass-border`)
- [ ] Hover row: `var(--color-primary-a05)`

### KPI Cards

- [ ] Setiap KPI card punya accent class (.em/.blue/.vio/.rose/.amber)
- [ ] Label pakai `kpi-label` (font-mono kecil uppercase)
- [ ] Value pakai `kpi-val` (font-mono besar)
- [ ] Delta/trend pakai `.delta.up` / `.delta.down` / `.delta.flat`

### Form

- [ ] Input focus: `border-color: var(--color-border-focus)` + `box-shadow: var(--shadow-focus)`
- [ ] Error state: `border-color: var(--color-danger)`
- [ ] Label: `color: var(--color-text-muted)`, `font-weight: 500`
- [ ] Placeholder: `color: var(--color-text-subtle)`

### Glassmorphism

- [ ] Semua card: `background: var(--glass-bg)` + `backdrop-filter: var(--glass-blur)`
- [ ] Card hover: `translateY(-2px)` + `box-shadow: var(--glass-shadow-lg)`
- [ ] Modal: `background: var(--glass-bg-strong)` + overlay `var(--glass-dark-bg)`
- [ ] Tidak ada `backdrop-filter` dengan blur < 10px

---

## 9. Known Issues & Todo

### Issues Aktif (dari sesi ini)

| # | Issue | Lokasi | Status |
|---|---|---|---|
| 1 | Border tabel tidak kelihatan | Customers page, kemungkinan global | 🔴 Perlu fix |
| 2 | Tier badge kehilangan border/background | Customers page | 🔴 Perlu fix |
| 3 | `@import Syne` masih ada di 11 template aktif | inventory, master_data, settings | 🟡 Fix tersedia (`validate.py --fix-fonts`) |
| 4 | `--glass-border` dipakai untuk tabel (seharusnya `--color-border`) | lumra_components.css | 🔴 Root cause border hilang |
| 5 | `dashboard.html.backup` ada di root templates | `templates/` | 🟡 Cleanup |

### Todo Backlog

| # | Todo | Prioritas |
|---|---|---|
| 1 | Fix border tabel: ganti `--glass-border` → `--color-border` di lumra_components.css | 🔴 High |
| 2 | Fix tier badge: audit `.status-chip` di components.css | 🔴 High |
| 3 | Hapus `@import Syne` dari 11 template | 🟡 Medium |
| 4 | Bersihkan `dashboard.html.backup` dan file `.backup` lain | 🟢 Low |
| 5 | Verifikasi `products.html` vs `product_list.html` — apakah duplikasi? | 🟡 Medium |
| 6 | Verifikasi `vendors_list.html` vs `vendor_list.html` — apakah duplikasi? | 🟡 Medium |
| 7 | Tambah `--color-border` dan `--border-table` sebagai token terpisah di config | 🟡 Medium |
| 8 | Run `strip_duplicates.py` setelah border fix | 🟢 Low |

### Fix Segera untuk Border Issue

Tambahkan ini ke `lumra_components.css` atau `lumra_design_system.css`:

```css
/* Fix: border untuk elemen di atas background putih */
--color-border       : rgba(203, 213, 225, 0.70);  /* slate-300 semi-transparent */
--color-border-subtle: rgba(0, 0, 0, 0.05);

/* Tabel wajib pakai ini, BUKAN --glass-border */
.lumra-table th,
.lumra-table td {
  border-bottom: 1px solid var(--color-border);
}

/* Status chip harus eksplisit */
.status-chip,
.lumra-badge {
  border: 1px solid transparent;  /* jangan inherit, set eksplisit */
}
```

---

*Blueprint ini di-generate berdasarkan 103 template aktif Lumra ERP.*
*Update blueprint setiap kali ada penambahan halaman baru.*