# 🗺️ LUMRA ERP — MASTER BLUEPRINT
**Panduan Utama Developer: Arsitektur, Template, Database & Workflow**
*Compiled: April 11, 2026 | Status: Complete*

---

## DAFTAR ISI

1. [Gambaran Sistem](#1-gambaran-sistem)
2. [Stack Teknologi](#2-stack-teknologi)
3. [Struktur File & Folder](#3-struktur-file--folder)
4. [Template Inheritance & Component](#4-template-inheritance--component)
5. [10 Modul Bisnis](#5-10-modul-bisnis)
6. [Database Schema Ringkas](#6-database-schema-ringkas)
7. [Relasi Antar Model](#7-relasi-antar-model)
8. [Hak Akses Per Role](#8-hak-akses-per-role)
9. [Workflow Utama](#9-workflow-utama)
10. [Petunjuk Membuat Fitur Baru](#10-petunjuk-membuat-fitur-baru)
11. [Quick Reference Commands](#11-quick-reference-commands)
12. [Koneksi Penting Antar Template](#12-koneksi-penting-antar-template)

---

## 1. GAMBARAN SISTEM

LUMRA ERP adalah sistem manajemen bisnis berbasis Django dengan 102 HTML template yang mencakup 10 modul bisnis utama. Sistem ini dirancang dengan arsitektur tiga lapis:

```
[PRESENTATION]  102 HTML Templates (Tailwind + Alpine.js)
      ↓
[APPLICATION]   Django Views (business logic & data)
      ↓
[DATA]          Django ORM → 32 Models / 32+ Tables
```

**Angka Penting Sistem:**

| Komponen | Jumlah |
|----------|--------|
| Total Templates | 102 files |
| Base Components | 14 files |
| Business Modules | 10 modul |
| Database Models | 32 models |
| Foreign Keys | 50+ relasi |
| URL Routes | 150+ |
| User Roles | 4 (Admin, Manager, Staff, Viewer) |
| Report Types | 20 template laporan |

---

## 2. STACK TEKNOLOGI

| Layer | Teknologi | Keterangan |
|-------|-----------|-----------|
| Backend | Django (Python) | Framework utama |
| Frontend CSS | Tailwind CSS | Utility-first styling |
| Frontend JS | Alpine.js | Reactive UI (no full SPA) |
| Icons | Font Awesome 6.4 | Icon library |
| Typography | Plus Jakarta Sans | Google Fonts |
| Theme | Emerald Odyssey | Glassmorphism style |
| Database | PostgreSQL / MySQL / SQLite | Via Django ORM |
| Template Engine | Django Template Language | Jinja-like syntax |

---

## 3. STRUKTUR FILE & FOLDER

```
lumra_config/
└── templates/
    ├── base/                          ← [14 files] Shared Components
    │   ├── base.html                  ← ROOT — semua template extends dari sini
    │   ├── navbar.html                ← Top navigation (semua halaman)
    │   ├── sidebar.html               ← Left menu (semua halaman)
    │   ├── sidebar_item.html          ← Komponen tiap menu item
    │   ├── sidebar_right.html         ← Panel kanan (opsional)
    │   ├── footer.html                ← Footer (auth & error pages)
    │   ├── alert.html                 ← Alert container
    │   ├── alert_inner.html           ← Alert message content
    │   ├── approval_modal.html        ← Modal approval workflow
    │   ├── kpi_card.html              ← KPI card (dark theme)
    │   ├── kpi_card_inner.html        ← KPI inner content
    │   ├── kpi_card_white.html        ← KPI card (light theme)
    │   └── partials/
    │       ├── form_field.html        ← ⭐ Reusable form input
    │       └── bg_blob.html           ← SVG background decoration
    │
    └── lumra_pages/                   ← [88 files] Feature Pages
        ├── auth/            [2]       login.html, register.html
        ├── inventory/       [16]      products, stock, purchasing, opname
        ├── sales_insight/   [7]       pos, dashboard, analytics
        ├── production/      [3]       recipe_list, recipe_form, recipe_detail
        ├── marketing/       [5]       campaign, discount, loyalty
        ├── master_data/     [13]      categories, units, vendors, customers
        ├── messages/        [2]       inbox.html, notification.html
        ├── reports/         [20]      sales, inventory, financial reports
        ├── settings/        [10]      users, business config, system
        └── etc/             [3]       error_403, error_404, error_500
```

---

## 4. TEMPLATE INHERITANCE & COMPONENT

### Hierarki Inheritance

```
base/base.html  ← ROOT (semua extend ke sini)
│
├── {% block title %}      ← Judul halaman
├── {% block extra_head %} ← Meta/links tambahan
├── {% block extra_css %}  ← CSS page-specific
├── {% block chart_scripts %} ← Chart library
└── {% block content %}    ← SEMUA konten halaman masuk sini
```

### Template Tipikal — Skeleton Wajib

```html
{% extends 'base/base.html' %}

{% block title %}Nama Halaman - LUMRA{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}

  <div class="main-content">
    <!-- konten halaman di sini -->
  </div>

  <!-- Jika ada approval workflow: -->
  {% include 'base/approval_modal.html' %}
{% endblock %}
```

### Shared Components — Cara Pakai

**Form Field (gunakan di semua form):**
```html
{% include 'base/partials/form_field.html' with
  field_type='text'       {# text | email | number | select | textarea | date #}
  label='Nama Produk'
  name='product_name'
  value=product.name      {# untuk edit mode #}
  required=True
  options=categories      {# untuk field_type='select' #}
%}
```

**KPI Card (untuk dashboard):**
```html
{% include 'base/kpi_card.html' with
  kpi_title='Total Penjualan Hari Ini'
  kpi_value=total_sales
  kpi_trend=percent_change
%}
```

**Approval Modal (untuk workflow persetujuan):**
```html
<!-- Trigger button: -->
<button @click="approvalModal = true">Approve</button>

<!-- Include modal: -->
{% include 'base/approval_modal.html' %}
```

### URL Linking Pattern

```html
<!-- Selalu gunakan named URL, JANGAN hardcode path: -->
<a href="{% url 'inventory:products' %}">Products</a>
<a href="{% url 'sales:pos' %}">POS</a>
<a href="{% url 'master_data:customers' %}">Customers</a>
<a href="{% url 'reports:sales_report' %}">Sales Report</a>
```

---

## 5. 10 MODUL BISNIS

### Ringkasan Modul

| # | Modul | Folder | Template | Views File |
|---|-------|--------|----------|------------|
| 1 | Auth & Users | auth/ + settings/ | 2 + 10 | auth_views.py |
| 2 | Inventory | inventory/ | 16 | inventory_views.py, stock_opname_views.py |
| 3 | Sales & POS | sales_insight/ | 7 | sales_views.py, pos_views.py |
| 4 | Production | production/ | 3 | production_views.py |
| 5 | Marketing | marketing/ | 5 | misc_views.py |
| 6 | Master Data | master_data/ | 13 | masterdata_views.py |
| 7 | Reports | reports/ | 20 | report_views.py |
| 8 | Messages | messages/ | 2 | notification_views.py |
| 9 | Settings | settings/ | 10 | settings_views.py |
| 10 | Error Pages | etc/ | 3 | Django default |

### Detail File Per Modul

**INVENTORY (16 files):**
```
inventory/
├── products.html                    ← Daftar produk
├── product_list.html                ← Alternatif list view
├── product_details.html             ← Detail produk
├── stock_overview.html              ← Dashboard stok + low stock alert
├── stock_movement.html              ← Log semua pergerakan stok
├── add_stock_movement.html          ← Form tambah pergerakan stok
├── stock_planning.html              ← Alokasi stok per lokasi
├── stock_opname_locations.html      ← Pilih lokasi untuk opname
├── stock_opname_form.html           ← Form hitung fisik stok
├── stock_opname_approvals.html      ← List opname menunggu approval
├── stock_opname_approval_detail.html← Detail approval + aksi
├── stock_purchasing.html            ← Purchase order
├── supplier_price_list.html         ← Harga dari vendor
├── supplier_price_form.html         ← Form tambah/edit harga vendor
└── supplier_price_confirm_delete.html← Konfirmasi hapus harga
```

**SALES & POS (7 files):**
```
sales_insight/
├── pos.html                         ← ⭐ POS utama (kasir)
├── dashboard.html                   ← Dashboard KPI penjualan
├── sales_intelligence.html          ← Analitik penjualan
├── sales_performance.html           ← Metrik performa
├── financial_reports.html           ← Ringkasan keuangan
├── market_insights.html             ← Analisis pasar
└── trends_analysis.html             ← Analisis tren historis
```

**MASTER DATA (13 files):**
```
master_data/
├── categories_list.html / category_form.html
├── units_list.html / unit_form.html
├── vendors_list.html / vendor_list.html / vendor_form.html
├── customers.html / customers_list.html / customer_detail.html / customer_form.html
├── locations.html / location_list.html
└── stock_opname_session_detail.html ← Riwayat session opname
```

**REPORTS (20 files):**
```
reports/
├── reporting.html                   ← Hub semua laporan
├── base_report.html                 ← Template dasar report
├── sales_report.html / sales_history.html / sales_history_product.html
├── report_sales_by_outlet.html / report_sales_by_payment.html
├── report_sales_by_product.html / report_sales_summary.html
├── report_inventory_stock.html / report_inventory_log.html / report_inventory_low.html
├── report_profit_loss_detail.html   ← Laporan Laba Rugi
├── requisition_report.html / purchasing_report.html / transfer_report.html
├── transaction_summary.html / activity_log.html
└── sales_report_after.html / report_sales_after.html
```

---

## 6. DATABASE SCHEMA RINGKAS

### 32 Model & Tabel Utama

| Kategori | Model | Tabel |
|----------|-------|-------|
| **Master Data** | Category | `_categories` |
| | Unit | `_units` |
| | Vendor | `_vendors` |
| | Tax | `_taxes` |
| | Location | `lumra_config_locations` |
| | Customer | `lumra_config_customers` |
| **Produk** | Product | `lumra_config_products` |
| | ProductVariant | `lumra_config_productvariants` |
| | ProductAttribute | `lumra_config_productattribute_items` |
| **Stok** | Stock | `lumra_config_stock` |
| | StockOpnameSession | `lumra_config_stockopname_session` |
| | StockOpnameItem | `lumra_config_stockopname_item` |
| | SupplierPrice | `lumra_config_supplier_prices` |
| **Workflow Stok** | Requisition | `lumra_config_requisitions` |
| | RequisitionItem | `lumra_config_requisitionitem` |
| | Transfer | `lumra_config_transfers` |
| | TransferItem | `lumra_config_transferitem` |
| **Transaksi** | Order | `lumra_config_orders` |
| | OrderItem | `lumra_config_orderitems` |
| **Produksi** | RecipeCategory | `production_recipe_categories` |
| | Recipe | `production_recipes` |
| | RecipeIngredient | `production_recipe_ingredients` |
| **User** | User | `auth_user` (Django built-in) |
| | UserProfile | `lumra_config_userprofile` |
| **Target** | SalesTarget | `lumra_config_sales_targets` |
| **View** | ProductDetail | `product_details_view` (DB view) |

### Schema Ringkas Model Utama

**Product:**
```
Product (lumra_config_products)
├── id, name (UNIQUE), sku (UNIQUE, INDEX)
├── category_id → Category (FK PROTECT)
├── vendor_id   → Vendor   (FK PROTECT)
├── unit_id     → Unit     (FK PROTECT)
├── tax_id      → Tax      (FK PROTECT)
├── description, is_active, image
└── created_at, updated_at
```

**ProductVariant:**
```
ProductVariant (lumra_config_productvariants)
├── id, sku (UNIQUE)
├── product_id  → Product  (FK CASCADE)
├── price_buy, price_sell, weight
└── is_active
```

**Stock:**
```
Stock (lumra_config_stock)
├── id, quantity, transaction_type ('in'/'out'/'adjustment')
├── variant_id  → ProductVariant (FK CASCADE)
├── location_id → Location (FK CASCADE)
└── created_at
```

**Order:**
```
Order (lumra_config_orders)
├── id, status ('pending'/'completed'/'cancelled')
├── customer_id → Customer (FK, NULLABLE)
├── customer_name (snapshot for backward compat)
├── location_id → Location
└── OrderItem → variant_id, quantity, price (snapshot)
```

---

## 7. RELASI ANTAR MODEL

```
Category ──< Product ──< ProductVariant ──< Stock
                │               │               └── Location
                │               ├──< ProductAttribute
                │               ├──< SupplierPrice >── Vendor
                │               ├──< RequisitionItem >── Requisition
                │               ├──< TransferItem >── Transfer
                │               ├──< StockOpnameItem >── StockOpnameSession
                │               ├──< RecipeIngredient >── Recipe
                │               └──< OrderItem >── Order
                │
                └── Unit, Vendor, Tax (FK)

Customer ──< Order ──< OrderItem ──> ProductVariant
Location ──< Stock, Requisition, Transfer, StockOpnameSession
User ──> UserProfile ──> Location
```

**Aturan Cascade:**
- Hapus Product → CASCADE hapus ProductVariant, Stock
- Hapus Category → PROTECT (tidak bisa hapus kalau masih ada Product)
- Hapus Customer → OrderItems TETAP ada (customer_id menjadi NULL)
- Hapus Location → PROTECT (tidak bisa hapus kalau masih ada Stock)

---

## 8. HAK AKSES PER ROLE

| Modul | Admin | Manager | Staff | Viewer |
|-------|-------|---------|-------|--------|
| Auth & User | Full CRUD | View | Profil sendiri | Profil sendiri |
| Inventory | Full CRUD | Full CRUD | View + Terbatas | View |
| Sales & POS | Full CRUD | Full CRUD | POS saja | View |
| Marketing | Full CRUD | Full CRUD | — | View |
| Master Data | Full CRUD | View + Edit | View | View |
| Production | Full CRUD | View + Edit | View | View |
| Reports | Full + Export | Full + Export | Terbatas | View |
| Settings | Full CRUD | Terbatas | — | — |
| Messages | Full | Full | Full | Terbatas |

**Halaman Utama Per Role:**

| Role | Halaman Utama |
|------|---------------|
| Admin | settings/users.html, settings/business_settings.html, semua reports |
| Manager | sales_insight/dashboard.html, inventory/stock_overview.html, stock_opname_approvals.html |
| Staff | sales_insight/pos.html, inventory/stock_movement.html, master_data/customers.html |
| Viewer | reports/ (semua), sales_insight/dashboard.html |

---

## 9. WORKFLOW UTAMA

### Workflow 1: Transaksi POS (Harian)

```
[LOGIN] auth/login.html
    ↓
[DASHBOARD] sales_insight/dashboard.html — lihat KPI hari ini
    ↓
[POS] sales_insight/pos.html
    ├── Cari produk (dari inventory)
    ├── Lookup customer → master_data/customers.html
    ├── Apply diskon → marketing/discount data
    ├── Pilih metode pembayaran
    └── Proses transaksi
    ↓
[LAPORAN] reports/transaction_summary.html
         reports/sales_history.html
         sales_insight/dashboard.html (KPI terupdate)
```

### Workflow 2: Stock Opname (Hitung Fisik)

```
[PILIH LOKASI] inventory/stock_opname_locations.html
    ↓
[HITUNG FISIK] inventory/stock_opname_form.html
    (list produk + qty sistem → input qty fisik → submit)
    ↓
[REVIEW] inventory/stock_opname_approvals.html
    ↓
[APPROVAL DETAIL] inventory/stock_opname_approval_detail.html
    (cek variance → klik Approve → approval_modal.html)
    ↓
[FINALIZE] inventory/stock_movement.html (adjustment dibuat otomatis)
           inventory/stock_overview.html (stok terupdate)
           master_data/stock_opname_session_detail.html (riwayat)
```

### Workflow 3: Purchase Order

```
[CEK STOK RENDAH] reports/report_inventory_low.html
    ↓
[BUAT PO] inventory/stock_purchasing.html
    ├── Pilih vendor → master_data/vendors_list.html
    └── Pilih produk + qty
    ↓
[APPROVAL] base/approval_modal.html (jika diperlukan)
    ↓
[TERIMA BARANG] inventory/add_stock_movement.html
    (movement type: "Receive PO" → link ke PO)
    ↓
[LAPORAN] reports/purchasing_report.html
          reports/report_inventory_log.html
```

### Workflow 4: Customer Loyalty

```
[BUAT/CARI CUSTOMER] master_data/customer_form.html
    ↓
[TRANSAKSI POS] sales_insight/pos.html
    (poin loyalty ditambahkan otomatis per transaksi)
    ↓
[LIHAT PROFIL] master_data/customer_detail.html
    (saldo poin, riwayat transaksi)
    ↓
[REDEEM] sales_insight/pos.html → "Redeem Points"
    ↓
[KELOLA PROGRAM] marketing/loyalty_members.html
```

### Workflow 5: Campaign & Diskon

```
[BUAT CAMPAIGN] marketing/add_campaign.html
    ↓
[BUAT DISKON] marketing/discount.html
    (tipe, nominal/%, periode berlaku, produk target)
    ↓
[OTOMATIS AKTIF] sales_insight/pos.html
    (diskon muncul & bisa dipilih kasir)
    ↓
[ANALISIS HASIL] marketing/campaign.html
                 reports/report_sales_by_outlet.html
```

---

## 10. PETUNJUK MEMBUAT FITUR BARU

### Langkah Wajib (Urutan Harus Diikuti)

**Step 1 — Buat Django Model**
```python
# lumra_config/models.py
class NamaModel(models.Model):
    name = models.CharField(max_length=100)
    # field lainnya...

    class Meta:
        db_table = 'lumra_config_namamodel'
```

**Step 2 — Buat View**
```python
# lumra_config/views/nama_views.py
def list_view(request):
    items = NamaModel.objects.all()
    return render(request, 'lumra_pages/modul/list.html', {'items': items})
```

**Step 3 — Buat Template**
```html
<!-- lumra_pages/modul/list.html -->
{% extends 'base/base.html' %}

{% block title %}Nama Fitur - LUMRA{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}

  <div class="main-content">
    {% for item in items %}
      <!-- tampilkan data -->
    {% endfor %}
  </div>
{% endblock %}
```

**Step 4 — Buat URL**
```python
# lumra_config/urls/namamodul_urls.py
urlpatterns = [
    path('', list_view, name='list'),
    path('create/', create_view, name='create'),
    path('<int:pk>/edit/', edit_view, name='edit'),
    path('<int:pk>/delete/', delete_view, name='delete'),
]
```

**Step 5 — Daftarkan di Sidebar**
```html
<!-- base/sidebar.html — tambahkan menu item -->
<a href="{% url 'namamodul:list' %}" class="menu-item">
  <i class="fas fa-icon"></i>
  Nama Fitur
</a>
```

**Step 6 — Buat Migrasi & Apply**
```bash
python manage.py makemigrations lumra_config
python manage.py migrate lumra_config
```

### Checklist Koneksi Antar Template

Sebelum menghubungkan file baru ke sistem yang ada:

- [ ] Extend dari `base/base.html`
- [ ] Include `navbar.html` dan `sidebar.html`
- [ ] Gunakan `form_field.html` untuk semua input form
- [ ] Gunakan `approval_modal.html` untuk workflow persetujuan
- [ ] Link antar halaman dengan `{% url 'app:view_name' %}`
- [ ] Kirim data dari view ke template via context dict
- [ ] Gunakan Alpine.js `x-data`, `x-show`, `@click` untuk interaktivitas
- [ ] Test semua koneksi dan data flow

---

## 11. QUICK REFERENCE COMMANDS

```bash
# === DEVELOPMENT ===
python manage.py runserver               # Jalankan dev server
python manage.py shell                   # Django shell interaktif
python manage.py dbshell                 # Shell database langsung

# === MIGRASI ===
python manage.py makemigrations lumra_config   # Buat file migrasi baru
python manage.py migrate lumra_config          # Apply migrasi
python manage.py showmigrations lumra_config   # Cek status migrasi
python manage.py migrate lumra_config zero     # ⚠️ RESET semua migrasi

# === ADMIN ===
python manage.py createsuperuser         # Buat user admin
python manage.py check                   # Cek error konfigurasi

# === DJANGO SHELL — CONTOH ORM ===
from lumra_config.models import *

# Buat data master
Category.objects.create(name='Beverages', code='BEV')
Vendor.objects.create(name='Supplier A', code='SUP001')
Unit.objects.create(name='Kilogram', symbol='kg')
Location.objects.create(name='Gudang Utama', code='GDG01')

# Buat produk
product = Product.objects.create(
    name='Kopi Arabika', sku='COFFEE-001',
    category=category, vendor=vendor,
    unit=unit, tax=tax
)

# Query umum
Product.objects.filter(category=category)
ProductVariant.objects.filter(price_sell__gt=50000)
Stock.objects.filter(location=location).aggregate(Sum('quantity'))

# Cek relasi
product.variants.all()
variant.product.name
stock.variant.product.category.name
```

---

## 12. KONEKSI PENTING ANTAR TEMPLATE

### Flow Penjualan (Sales Chain)
```
inventory/products.html
    ↓ (pilih produk)
sales_insight/pos.html
    ↓ (transaksi selesai)
reports/sales_history.html
reports/transaction_summary.html
reports/report_sales_by_product.html
sales_insight/dashboard.html (KPI update)
```

### Flow Stok (Inventory Chain)
```
inventory/stock_overview.html
    ↓ (low stock alert)
inventory/add_stock_movement.html  ← atau →  inventory/stock_purchasing.html
    ↓                                               ↓
inventory/stock_movement.html            reports/purchasing_report.html
    ↓
reports/report_inventory_low.html
reports/report_inventory_log.html
```

### Flow Customer
```
master_data/customers.html
    ↓ (buat/cari customer)
sales_insight/pos.html
    ↓ (setelah transaksi)
master_data/customer_detail.html
marketing/loyalty_members.html
```

### Flow Master Data → Semua Modul
```
master_data/categories_list.html  ──→  inventory/products.html
master_data/units_list.html       ──→  inventory/products.html
master_data/vendors_list.html     ──→  inventory/stock_purchasing.html
master_data/locations.html        ──→  inventory/stock_opname_locations.html
                                  ──→  inventory/add_stock_movement.html
                                  ──→  reports/report_sales_by_outlet.html
```

### Dependensi Modul (Siapa Butuh Siapa)
```
REPORTS  ← membutuhkan data dari SALES + INVENTORY + MASTER DATA
SALES    ← membutuhkan INVENTORY (produk) + MASTER DATA (customer)
           + MARKETING (diskon)
INVENTORY← membutuhkan MASTER DATA (produk, kategori, vendor, lokasi)
           + PRODUCTION (untuk COGS)
MARKETING← membutuhkan MASTER DATA (customer)
SETTINGS ← mengontrol akses ke SEMUA modul
AUTH     ← gate/pintu masuk untuk SEMUA modul
```

---

## CATATAN PENTING UNTUK DEVELOPER

**Jangan lakukan ini:**
- Jangan hardcode URL di template — selalu pakai `{% url %}`
- Jangan bypass base.html — selalu `{% extends 'base/base.html' %}`
- Jangan buat form input manual — pakai `form_field.html`
- Jangan hapus Location/Category yang masih punya data terkait (PROTECT FK)

**Selalu lakukan ini:**
- Cek `FEATURE_FILE_MAPPING.md` sebelum mulai fitur baru
- Cek `DATABASE_SCHEMA_MAPPING.md` sebelum buat/ubah model
- Test semua role akses (Admin, Manager, Staff, Viewer) setelah buat fitur
- Tambahkan migrasi ke version control

---

*Dokumen ini adalah ringkasan dari: MODULE_ARCHITECTURE.md, COMPONENT_ARCHITECTURE.md, FEATURE_FILE_MAPPING.md, DATABASE_SCHEMA_MAPPING.md, DATABASE_QUICK_REFERENCE.md, TEMPLATE_CATALOG.md, dan DOCUMENTATION_INDEX.md*

**Generated:** April 11, 2026 | **Version:** 1.0 | **Total Templates:** 102