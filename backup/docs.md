# 📖 Lumra ERP — Buku Dokumentasi Teknis

> Dibuat otomatis dari source code pada 11 March 2026 05:02

---

## 📋 Daftar Isi

1. [Arsitektur Project](#1-arsitektur-project)
2. [Database & Model](#2-database--model)
3. [URL → View → Template](#3-url--view--template)
   - [🛒 Sales & POS](#sales--pos)
   - [📦 Master Data](#master-data)
   - [🏭 Inventory](#inventory)
   - [⚗️  Production](#production)
   - [📣 Marketing](#marketing)
   - [📊 Reports & Insights](#reports--insights)
   - [⚙️  Settings & Users](#settings--users)
   - [🔐 Authentication](#authentication)
   - [🔌 Internal API](#internal-api)
4. [Settings & Konfigurasi](#4-settings--konfigurasi)
5. [Troubleshooting Migration](#5-troubleshooting-migration)

---

## 1. Arsitektur Project

```
lumra/
├── manage.py
├── lumra_system/              ← konfigurasi Django
│   ├── settings.py            ← database, middleware, templates
│   ├── urls.py                ← router utama (101 URL)
│   ├── wsgi.py
│   └── asgi.py
└── lumra_config/              ← aplikasi utama
    ├── models.py              ← 24 model, PostgreSQL
    ├── views/                 ← 103 view functions
    │   ├── __init__.py        ← central exports
    │   ├── dashboard_views.py
    │   ├── auth_views.py
    │   ├── inventory_views.py
    │   ├── masterdata_views.py
    │   ├── customer_views.py
    │   ├── stock_movement_views.py
    │   ├── stock_opname_views.py
    │   ├── production_views.py
    │   ├── pricing_views.py
    │   ├── report_views.py
    │   ├── misc_views.py
    │   ├── api_views.py
    │   └── helpers.py
    ├── sales/views.py         ← stub → lumra_config.views
    ├── master_data/views.py   ← stub → lumra_config.views
    ├── inventory/views.py     ← stub → lumra_config.views
    ├── production/views.py    ← stub → lumra_config.views
    ├── marketing/views.py     ← stub → lumra_config.views
    ├── reports/views.py       ← stub → lumra_config.views
    ├── settings_app/views.py  ← stub → lumra_config.views
    ├── auth_app/views.py      ← stub → lumra_config.views
    ├── api/views.py           ← stub → lumra_config.views
    ├── middleware.py          ← EnsureUserProfileMiddleware
    ├── context_processors.py  ← app_version di semua template
    ├── signals.py             ← auto stock deduction
    ├── admin.py               ← Django admin registrations
    ├── apps.py                ← AppConfig + signals ready()
    ├── migrations/            ← database migrations
    └── templates/             ← HTML templates
        └── lumra_pages/       ← halaman utama
```

### Pola URL → View

Semua URL menggunakan `lazy_view()` untuk menghindari circular import:

```python
# lumra_system/urls.py
path('/', lazy_view('lumra_config.sales.views.dashboard_view'), name='dashboard')
#          └── lumra_config/sales/views.py (stub)
#                └── from lumra_config.views import dashboard_view
#                       └── lumra_config/views/dashboard_views.py
```

---

## 2. Database & Model

**Database**: PostgreSQL  
**App label**: `lumra_config`  
**Total model**: 24

| Model | Tabel PostgreSQL | Keterangan |
|-------|-----------------|------------|
| `Category` | `_categories` | Kategori produk |
| `Vendor` | `_vendors` | Supplier/vendor |
| `Tax` | `_taxes` | Konfigurasi pajak |
| `Unit` | `_units` | Satuan ukuran (pcs, kg, dll) |
| `Location` | `lumra_config_locations` | Lokasi/outlet/gudang |
| `Product` | `lumra_config_products` | Produk master |
| `ProductVariant` | `lumra_config_productvariants` | Varian produk (SKU, harga) |
| `ProductAttribute` | `lumra_config_productattribute_items` | Atribut tambahan varian |
| `Stock` | `lumra_config_stock` | Stok per lokasi per varian |
| `Requisition` | `lumra_config_requisitions` | Permintaan transfer stok |
| `RequisitionItem` | `lumra_config_requisitionitem` | Item dalam requisition |
| `Transfer` | `lumra_config_transfers` | Transfer stok antar lokasi |
| `TransferItem` | `lumra_config_transferitem` | Item dalam transfer |
| `UserProfile` | `lumra_config_userprofile` | Profil user + lokasi |
| `Customer` | `lumra_config_customers` | Data pelanggan + loyalty points |
| `Order` | `lumra_config_orders` | Order/transaksi penjualan |
| `OrderItem` | `lumra_config_orderitems` | Item dalam order |
| `ProductDetail` | `product_details_view` | View database (read-only) |
| `StockOpnameSession` | `lumra_config_stockopname_session` | Sesi penghitungan stok fisik |
| `StockOpnameItem` | `lumra_config_stockopname_item` | Item dalam stock opname |
| `RecipeCategory` | `production_recipe_categories` | Kategori resep produksi ⚠️ *shared dengan core* |
| `Recipe` | `production_recipes` | Resep/BOM produksi ⚠️ *shared dengan core* |
| `RecipeIngredient` | `production_recipe_ingredients` | Bahan dalam resep ⚠️ *shared dengan core* |
| `SupplierPrice` | `lumra_config_supplier_prices` | Harga beli per supplier |

> ⚠️ **Tabel shared** (`production_*`) namanya sama antara `core` dan `lumra`.
> Saat migrate gunakan `--fake-initial` agar tidak error DuplicateTable.

### Detail Field Model Utama

#### `UserProfile` → tabel `lumra_config_userprofile`
| Field | Tipe |
|-------|------|
| `user` | `OneToOneField` |
| `location` | `ForeignKey` |

#### `Product` → tabel `lumra_config_products`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `description` | `TextField` |
| `category` | `ForeignKey` |
| `vendor` | `ForeignKey` |
| `tax` | `ForeignKey` |
| `unit` | `ForeignKey` |
| `created_at` | `DateTimeField` |
| `updated_at` | `DateTimeField` |

#### `ProductVariant` → tabel `lumra_config_productvariants`
| Field | Tipe |
|-------|------|
| `product` | `ForeignKey` |
| `sku` | `CharField` |
| `size_weight` | `CharField` |
| `price_buy` | `DecimalField` |
| `price_sell` | `DecimalField` |
| `updated_at` | `DateTimeField` |

#### `Stock` → tabel `lumra_config_stock`
| Field | Tipe |
|-------|------|
| `variant` | `ForeignKey` |
| `location` | `ForeignKey` |
| `quantity` | `IntegerField` |
| `transaction_type` | `CharField` |
| `notes` | `TextField` |
| `last_updated` | `DateTimeField` |
| `created_at` | `DateTimeField` |

#### `Order` → tabel `lumra_config_orders`
| Field | Tipe |
|-------|------|
| `customer` | `ForeignKey` |
| `customer_name` | `CharField` |
| `status` | `CharField` |
| `created_at` | `DateTimeField` |

#### `Customer` → tabel `lumra_config_customers`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `email` | `EmailField` |
| `phone` | `CharField` |
| `address` | `TextField` |
| `city` | `CharField` |
| `tier` | `CharField` |
| `loyalty_points` | `IntegerField` |
| `total_spent` | `DecimalField` |
| `total_orders` | `IntegerField` |
| `is_active` | `BooleanField` |
| `created_at` | `DateTimeField` |
| `updated_at` | `DateTimeField` |
| *...1 field lainnya* | |

#### `Recipe` → tabel `production_recipes`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `description` | `TextField` |
| `instructions` | `TextField` |
| `category` | `ForeignKey` |
| `yield_quantity` | `DecimalField` |
| `yield_unit` | `ForeignKey` |
| `preparation_time` | `IntegerField` |
| `total_cost` | `DecimalField` |
| `cost_per_unit` | `DecimalField` |
| `is_archived` | `BooleanField` |
| `created_at` | `DateTimeField` |
| `updated_at` | `DateTimeField` |

---

## 3. URL → View → Template

Total: **101 URL** aktif

### 🛒 Sales & POS

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/` | GET | `dashboard_view` | `dashboard.html` | 🌐 |
| `/notification/` | GET | `notification_view` | `notification.html` | 🌐 |
| `/sales/pos/` | GET | `pos_view` | `pos.html` | 🌐 |
| `/sales/pos/create-order/` | GET | `pos_create_order` | `—` | 🌐 |
| `/sales/history/` | GET | `sales_history_view` | `sales_history.html` | 🔒 |
| `/sales/history/products/` | GET | `sales_history_products_view` | `sales_history_product.html` | 🌐 |
| `/sales/performance/` | GET | `sales_performance_view` | `sales_performance.html` | 🌐 |
| `/purchasing/` | GET | `purchasing_view` | `purchasing.html` | 🌐 |
| `/reports/purchasing/` | GET | `purchasing_report` | `purchasing_report.html` | 🌐 |

### 📦 Master Data

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/locations/` | GET | `locations_view` | `locations.html` | 🌐 |
| `/master/products/` | GET | `products_view` | `products.html` | 🌐 |
| `/master/products/<int:product_id>/` | GET | `product_detail_view` | `product_details.html` | 🌐 |
| `/master/categories/` | GET | `categories_list` | `categories_list.html` | 🌐 |
| `/master/categories/add/` | GET, POST | `category_create` | `category_form.html` | 🌐 |
| `/master/categories/<int:pk>/edit/` | GET, POST | `category_update` | `category_form.html` | 🌐 |
| `/master/categories/<int:pk>/delete/` | GET | `category_delete` | `—` | 🌐 |
| `/master/units/` | GET | `units_list` | `units_list.html` | 🌐 |
| `/master/units/add/` | GET, POST | `unit_create` | `unit_form.html` | 🌐 |
| `/master/units/<int:pk>/edit/` | GET, POST | `unit_update` | `unit_form.html` | 🌐 |
| `/master/units/<int:pk>/delete/` | GET | `unit_delete` | `—` | 🌐 |
| `/master/vendors/` | GET | `vendors_list` | `vendors_list.html` | 🌐 |
| `/master/vendors/add/` | GET, POST | `vendor_create` | `vendor_form.html` | 🌐 |
| `/master/vendors/<int:pk>/edit/` | GET, POST | `vendor_update` | `vendor_form.html` | 🌐 |
| `/master/vendors/<int:pk>/delete/` | GET | `vendor_delete` | `—` | 🌐 |
| `/master/customers/` | GET | `customer_list` | `customers_list.html` | 🌐 |
| `/master/customers/add/` | GET, POST | `customer_create` | `customer_form.html` | 🌐 |
| `/master/customers/<int:pk>/` | GET | `customer_detail` | `customer_detail.html` | 🌐 |
| `/master/customers/<int:pk>/edit/` | GET, POST | `customer_update` | `customer_form.html` | 🌐 |
| `/master/customers/<int:pk>/delete/` | GET | `customer_delete` | `—` | 🌐 |
| `/master/customers/<int:pk>/redeem/` | GET, POST | `customer_redeem_points` | `—` | 🌐 |
| `/master/stock-opname/` | GET | `stock_opname_locations` | `stock_opname_locations.html` | 🌐 |
| `/master/stock-opname/<int:location_id>/form/` | GET, POST | `stock_opname_form` | `stock_opname_form.html` | 🌐 |
| `/master/stock-opname/approvals/` | GET | `stock_opname_approvals` | `stock_opname_approvals.html` | 🌐 |
| `/master/stock-opname/approvals/<int:session_id>/` | GET, POST | `stock_opname_approval_detail` | `stock_opname_approval_detail.html` | 🌐 |
| `/reports/sales-by-product/` | GET | `report_sales_by_product` | `report_sales_by_product.html` | 🌐 |

### 🏭 Inventory

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/master/products/import-template/` | GET | `products_import_template` | `—` | 🌐 |
| `/inventory/planning/` | GET | `stock_planning_view` | `stock_planning.html` | 🌐 |
| `/inventory/movement/` | GET | `stock_movement_view` | `stock_movement.html` | 🌐 |
| `/inventory/movement/add/` | GET, POST | `add_stock_movement_view` | `add_stock_movement.html` | 🌐 |
| `/inventory/movement/export/` | GET | `export_stock_movement` | `stock_movement.html` | 🌐 |
| `/inventory/supplier-prices/` | GET | `supplier_price_list` | `supplier_price_list.html` | 🌐 |
| `/inventory/supplier-prices/form/` | GET, POST | `supplier_price_form` | `supplier_price_form.html` | 🌐 |
| `/inventory/supplier-prices/<int:price_id>/delete/` | GET | `supplier_price_delete` | `supplier_price_confirm_delete.html` | 🌐 |
| `/api/requisition/<int:requisition_id>/approve/` | GET | `approve_requisition` | `—` | 🌐 |
| `/api/submit-stock-allocation/` | GET | `submit_stock_allocation` | `—` | 🌐 |
| `/api/products/import/` | GET | `products_import` | `—` | 🌐 |

### ⚗️  Production

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/production/recipes/` | GET | `recipe_list` | `recipe_list.html` | 🌐 |
| `/production/recipes/form/` | GET, POST | `recipe_form` | `recipe_form.html` | 🌐 |
| `/production/recipes/<int:recipe_id>/` | GET | `recipe_detail` | `recipe_detail.html` | 🌐 |
| `/production/recipes/<int:recipe_id>/edit/` | GET, POST | `recipe_form` | `recipe_form.html` | 🌐 |
| `/production/recipes/<int:recipe_id>/delete/` | GET, POST | `recipe_delete` | `—` | 🌐 |
| `/production/recipes/<int:recipe_id>/delete-legacy/` | GET, POST | `recipe_delete` | `—` | 🌐 |

### 📣 Marketing

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/marketing/campaigns/` | GET | `campaign_list_view` | `campaign.html` | 🌐 |
| `/marketing/campaigns/add/` | GET | `add_campaign_view` | `campaign.html` | 🌐 |
| `/marketing/campaigns/<int:campaign_id>/edit/` | GET | `edit_campaign_view` | `campaign.html` | 🌐 |
| `/marketing/campaigns/<int:campaign_id>/delete/` | GET | `delete_campaign_view` | `campaign.html` | 🌐 |
| `/marketing/discounts/` | GET | `discount_list_view` | `discount.html` | 🌐 |
| `/marketing/discounts/add/` | GET | `add_discount_view` | `discount.html` | 🌐 |
| `/marketing/discounts/<int:discount_id>/edit/` | GET | `edit_discount_view` | `discount.html` | 🌐 |
| `/marketing/discounts/<int:discount_id>/delete/` | GET | `delete_discount_view` | `discount.html` | 🌐 |
| `/marketing/loyalty/` | GET | `loyalty_members_view` | `loyalty_members.html` | 🌐 |
| `/marketing/loyalty/add/` | GET | `add_loyalty_member_view` | `loyalty_members.html` | 🌐 |
| `/marketing/loyalty/<int:member_id>/edit/` | GET | `edit_loyalty_member_view` | `loyalty_members.html` | 🌐 |
| `/marketing/loyalty/<int:member_id>/delete/` | GET | `delete_loyalty_member_view` | `loyalty_members.html` | 🌐 |

### 📊 Reports & Insights

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/insights/financial/` | GET | `financial_reports_view` | `financial_reports.html` | 🌐 |
| `/insights/market/` | GET | `market_insights_view` | `market_insights.html` | 🌐 |
| `/insights/trends/` | GET | `trends_analysis_view` | `trends_analysis.html` | 🌐 |
| `/insights/activity/` | GET | `activity_log_view` | `activity_log.html` | 🌐 |
| `/insights/download-report/<str:report_type>/` | GET | `download_report_view` | `market_insights.html` | 🌐 |
| `/insights/export-trends/<str:trend_type>/` | GET | `export_trends_view` | `trends_analysis.html` | 🌐 |
| `/reports/sales/` | GET | `sales_report` | `sales_report.html` | 🌐 |
| `/reports/transactions/` | GET | `transaction_summary` | `transaction_summary.html` | 🌐 |
| `/reports/transfers/` | GET | `transfer_report` | `transfer_report.html` | 🌐 |
| `/reports/requisitions/` | GET | `requisition_report` | `requisition_report.html` | 🌐 |
| `/reports/inventory-log/` | GET | `report_inventory_log` | `report_inventory_log.html` | 🌐 |
| `/reports/inventory-low/` | GET | `report_inventory_low` | `report_inventory_low.html` | 🌐 |
| `/reports/inventory-stock/` | GET | `report_inventory_stock` | `report_inventory_stock.html` | 🌐 |
| `/reports/profit-loss-detail/` | GET | `report_profit_loss_detail` | `report_profit_loss_detail.html` | 🌐 |
| `/reports/sales-by-outlet/` | GET | `report_sales_by_outlet` | `report_sales_by_outlet.html` | 🌐 |
| `/reports/sales-by-payment/` | GET | `report_sales_by_payment` | `report_sales_by_payment.html` | 🌐 |
| `/reports/sales-summary/` | GET | `report_sales_summary` | `report_sales_summary.html` | 🌐 |

### ⚙️  Settings & Users

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/users/` | GET | `users_view` | `error_403.html` | 🌐 |
| `/profile/` | GET | `profile_view` | `profile.html` | 🌐 |
| `/settings/` | GET | `settings_view` | `settings.html` | 🌐 |
| `/settings/system/` | GET | `system_status_view` | `system_status.html` | 🌐 |
| `/settings/business/` | GET | `business_settings_view` | `business_settings.html` | 🌐 |
| `/settings/business/general/` | GET | `business_form_general_view` | `business_form_general.html` | 🌐 |
| `/settings/business/feature-matrix/` | GET | `business_feature_matrix_view` | `business_feature_matrix.html` | 🌐 |
| `/settings/business/roles/` | GET | `user_roles_permissions_view` | `user_roles_permissions.html` | 🌐 |
| `/about/` | GET | `about_view` | `about.html` | 🌐 |
| `/contact/` | GET | `contact_view` | `contact.html` | 🌐 |
| `/pricing/` | GET | `pricing_view` | `—` | 🌐 |
| `/search/` | GET | `search_view` | `search.html` | 🌐 |

### 🔐 Authentication

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/auth/login/` | GET, POST | `login_view` | `login.html` | 🌐 |
| `/auth/logout/` | GET | `logout_view` | `—` | 🌐 |

### 🔌 Internal API

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/api/dashboard/data/` | GET | `api_dashboard_data` | `—` | 🌐 |
| `/api/dashboard/chart-data/` | GET | `api_dashboard_chart_data` | `—` | 🌐 |
| `/api/requisition/submit/` | GET | `submit_requisition` | `—` | 🌐 |
| `/api/transfer/<int:transfer_id>/confirm/` | GET | `confirm_receipt` | `—` | 🌐 |
| `/api/purchases/submit/` | GET | `submit_purchases` | `—` | 🌐 |
| `/api/location-stock/<str:product_sku>/` | GET | `get_location_stock` | `—` | 🌐 |

> 🔒 = Login required &nbsp;&nbsp; 🌐 = Public

---

## 4. Settings & Konfigurasi

File: `lumra_system/settings.py`

### Database
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lumra_set_allegra',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Middleware (urutan penting!)
```python
MIDDLEWARE = [
    'django_browser_reload.middleware.BrowserReloadMiddleware',  # Hot reload
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'lumra_config.middleware.EnsureUserProfileMiddleware',  # ← WAJIB: user.profile di template
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Templates
```python
TEMPLATES = [{
    'DIRS': [BASE_DIR / 'lumra_config/templates'],  # ← folder templates
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'lumra_config.context_processors.app_settings',  # ← app_version
        ],
    },
}]
```

### INSTALLED_APPS
```python
INSTALLED_APPS = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'tailwind',
    'theme',
    'django_browser_reload',
    # Project
    'lumra_config',
]
```

---

## 5. Troubleshooting Migration

### Error: `relation already exists`

**Penyebab**: Tabel `production_*` sudah ada di database (dari project `core` lama).

**Solusi cepat:**
```bash
python manage.py makemigrations lumra_config
python manage.py migrate --fake-initial
```

`--fake-initial` = Django skip `CREATE TABLE` untuk tabel yang sudah ada,
tapi tetap buat tabel yang belum ada.

**Atau gunakan skrip otomatis:**
```bash
python lumra_migrate_fix.py
```

### Error: `relation does not exist`

**Penyebab**: Tabel belum dibuat sama sekali.

```bash
python manage.py makemigrations lumra_config
python manage.py migrate
```

### Error: `column does not exist`

**Penyebab**: Model diubah tapi migration belum dijalankan.

```bash
python manage.py makemigrations lumra_config
python manage.py migrate lumra_config
```

### Tabel Shared antara Core & Lumra

Tabel berikut namanya SAMA di kedua project (tidak bisa diubah tanpa migrasi data):

| Tabel | Model di Core | Model di Lumra |
|-------|--------------|----------------|
| `production_recipe_categories` | `RecipeCategory` | `RecipeCategory` |
| `production_recipes` | `Recipe` | `Recipe` |
| `production_recipe_ingredients` | `RecipeIngredient` | `RecipeIngredient` |

Tabel ini dipakai bersama — jangan di-drop!

### Cek Status Migration
```bash
python manage.py showmigrations          # lihat semua
python manage.py showmigrations lumra_config  # hanya lumra
python manage.py sqlmigrate lumra_config 0001  # lihat SQL yang akan dijalankan
```

---

*Dokumentasi ini dibuat otomatis dari source code lumra ERP.*