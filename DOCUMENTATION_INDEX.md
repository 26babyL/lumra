# 📚 LUMRA ERP - Documentation Index
**Quick Navigation Guide for All 102 HTML Templates**  
*Generated: April 10, 2026*

---

## 🎯 Start Here

**Baru pertama kali?** Baca dalam urutan ini:
1. **MODULE_ARCHITECTURE.md** - Pahami struktur sistem & 10 modul utama
2. **TEMPLATE_CATALOG.md** - Lihat daftar lengkap 102 template
3. **FEATURE_FILE_MAPPING.md** - Cari fitur → template mana yang support?
4. **COMPONENT_ARCHITECTURE.md** - Pahami cara template terhubung

---

## 📖 Dokumentasi Lengkap

### 1. 📋 TEMPLATE_CATALOG.md
**Apa:** Inventaris lengkap 102 HTML file dengan deskripsi detail  
**Gunakan ketika:** Cari template tertentu atau mau tahu fungsi file

**Isi:**
- ✅ 102 template di-list per kategori
- ✅ Deskripsi & features setiap template
- ✅ Siapa yang menggunakan file tersebut
- ✅ Component hierarchy diagram
- ✅ File yang saling terhubung

**Contoh Pencarian:**
```
Cari: "Berapa template untuk inventory?"
Jawab: 16 template di folder inventory/ (page 3)

Cari: "File apa untuk approval workflow?"
Jawab: base/approval_modal.html (page 2)

Cari: "Template buat laporan sales?"
Jawab: 20 template di reports/ folder (page 8-9)
```

---

### 2. 🔗 FEATURE_FILE_MAPPING.md
**Apa:** Map lengkap fitur bisnis ke template yang mendukungnya  
**Gunakan ketika:** Mau implement fitur → cari template & file pendukung

**Isi:**
- ✅ Setiap fitur bisnis → template & file pendukung
- ✅ Data flow & workflow
- ✅ Dependensi antar file
- ✅ User journey examples
- ✅ Feature-to-file relationships

**Contoh Pencarian:**
```
Cari: "Fitur POS pakai template apa?"
Jawab: sales_insight/pos.html + interaksi dengan 5 file lain (page 4)

Cari: "Proses stock opname ada berapa template?"
Jawab: 5 template dalam workflow step-by-step (page 6-7)

Cari: "Customer loyalty pakai file mana?"
Jawab: marketing/loyalty_members.html + master_data/customer_detail.html (page 9)
```

---

### 3. 🏗️ COMPONENT_ARCHITECTURE.md
**Apa:** Arsitektur, inheritance, dan cara template terhubung  
**Gunakan ketika:** Mau understand teknisnya template saling link & share

**Isi:**
- ✅ Template inheritance hierarchy
- ✅ Shared components (navbar, sidebar, kpi_card, dll)
- ✅ Partial components (form_field.html, bg_blob.html)
- ✅ Navigation flow between templates
- ✅ Data flow examples
- ✅ Alpine.js integration points
- ✅ Tailwind CSS usage

**Contoh Pencarian:**
```
Cari: "Form di semua template pakai component apa?"
Jawab: base/partials/form_field.html (page 3)

Cari: "Bagaimana cara stock opname approval?-nya bekerja?"
Jawab: approval_modal.html + Alpine.js integration (page 4, 5)

Cari: "Navbar di semua halaman sama?"
Jawab: Ya, base/navbar.html included di semua page (page 2)
```

---

### 4. 🎯 MODULE_ARCHITECTURE.md
**Apa:** High-level system architecture & 10 modul bisnis  
**Gunakan ketika:** Mau understand struktur sistem & modul dependencies

**Isi:**
- ✅ Three-layer architecture diagram
- ✅ Deskripsi 10 modul bisnis (Auth, Inventory, Sales, dll)
- ✅ Module dependencies graph
- ✅ Data relationships model
- ✅ User role access matrix
- ✅ Process workflows (5 major)
- ✅ Implementation guide

**Contoh Pencarian:**
```
Cari: "Modul apa yang depend ke Master Data?"
Jawab: Sales, Inventory, Marketing, Production (page 6)

Cari: "Staff role bisa akses apa?"
Jawab: POS, limited inventory, view reports (page 8)

Cari: "Workflow stock opname detail?"
Jawab: 5 step dari planning hingga finalize (page 10)
```

---

## 📂 File Organization di Sistem

```
lumra_config/templates/
├── base/                    [14 files - Shared components]
│   ├── base.html                    ← ROOT template
│   ├── navbar.html
│   ├── sidebar.html
│   ├── approval_modal.html
│   ├── kpi_card*.html
│   └── partials/
│       ├── form_field.html
│       └── bg_blob.html
│
└── lumra_pages/             [88 files - Features]
    ├── auth/                [2 files]
    ├── inventory/           [16 files]
    ├── sales_insight/       [7 files]
    ├── production/          [3 files]
    ├── marketing/           [5 files]
    ├── master_data/         [13 files]
    ├── messages/            [2 files]
    ├── reports/             [20 files]
    ├── settings/            [10 files]
    └── etc/                 [3 error pages]

TOTAL: 102 template files
```

---

## 🎨 Theme & Technology

- **Theme:** Emerald Odyssey (Glassmorphism)
- **CSS Framework:** Tailwind CSS
- **Front-end:** Alpine.js for reactive components
- **Icons:** Font Awesome 6.4
- **Typography:** Plus Jakarta Sans (Google Fonts)
- **Backend:** Django (Python)

---

## 🔍 Quick Search Guide

### Cari File Berdasarkan Fungsi

| Fungsi | File | Lokasi |
|--------|------|--------|
| Login | login.html | auth/ |
| Produk | products.html | inventory/ |
| POS | pos.html | sales_insight/ |
| Dashboard | dashboard.html | sales_insight/ |
| Stock Opname | stock_opname_*.html | inventory/ (5 files) |
| Customer | customers.html | master_data/ |
| Reports | sales_report.html | reports/ (20 files) |
| Settings | settings.html | settings/ |
| Form | form_field.html | base/partials/ |
| Modal | approval_modal.html | base/ |

### Cari Modul Berdasarkan Tugas

| Tugas | Modul | Base Template |
|------|-------|----------------|
| Jual produk | Sales/POS | pos.html |
| Kelola stok | Inventory | products.html → stock_overview.html |
| Hitung stok fisik | Inventory | stock_opname_form.html |
| Laporan penjualan | Reports | sales_report.html |
| Kelola customer | Master Data | customers.html |
| Buat resep | Production | recipe_form.html |
| Kampanye marketing | Marketing | campaign.html |
| User management | Settings | users.html |

---

## 📋 10 Modul Bisnis & Template Count

| # | Modul | Template | Keterangan |
|---|-------|----------|-----------|
| 1 | **Auth & Users** | 2 | Login, Register, User mgmt |
| 2 | **Inventory** | 16 | Produk, stock, purchasing, opname |
| 3 | **Sales & POS** | 7 | POS, dashboard, analytics |
| 4 | **Production** | 3 | Recipe management |
| 5 | **Marketing** | 5 | Campaign, discount, loyalty |
| 6 | **Master Data** | 13 | Categories, units, vendor, customer |
| 7 | **Reports** | 20 | Sales, inventory, financial |
| 8 | **Messages** | 2 | Inbox, notifications |
| 9 | **Settings** | 10 | Business config, system status |
| 10 | **Error Pages** | 3 | 403, 404, 500 errors |
| - | **Base Components** | 14 | Navbar, sidebar, modals, KPI cards |
| **TOTAL** | **103 files** | ✅ Complete |

---

## 🔗 Common Connections

### Most Used Connections
```
inventory/products.html 
  ↓ (select product)
sales_insight/pos.html
  ↓ (transaction created)
reports/sales_history.html
reports/transaction_summary.html
reports/report_sales_by_product.html

inventory/stock_overview.html
  ↓ (low stock alert)
inventory/add_stock_movement.html
  ↓ (or)
inventory/stock_purchasing.html
  ↓
reports/report_inventory_low.html

master_data/customers.html
  ↓ (create/lookup)
sales_insight/pos.html
  ↓ (transaction)
master_data/customer_detail.html
marketing/loyalty_members.html
```

---

## 👥 By User Role

### Admin
**Akses:** Semua file & feature  
**Main Pages:** 
- settings/users.html
- settings/business_settings.html
- reports/ (semua report)

### Manager
**Akses:** Sales, Inventory, Reports  
**Main Pages:**
- sales_insight/dashboard.html
- inventory/stock_overview.html
- inventory/stock_opname_approvals.html
- reports/sales_report.html

### Staff (Cashier/Inventory)
**Akses:** POS, limited inventory  
**Main Pages:**
- sales_insight/pos.html
- inventory/stock_movement.html
- master_data/customers.html

### Viewer (Read-only)
**Akses:** Reports only  
**Main Pages:**
- reports/ (semua laporan)
- sales_insight/dashboard.html

---

## 📝 Implementation Checklist

Ketika membuat sambungan file baru:

- [ ] Baca MODULE_ARCHITECTURE dulu (pahami flow)
- [ ] Identify parent template (usually base.html)
- [ ] Check COMPONENT_ARCHITECTURE untuk component yang dipakai
- [ ] Reference TEMPLATE_CATALOG untuk lihat template sejenis
- [ ] Use FEATURE_FILE_MAPPING untuk lihat data flow
- [ ] Extend dari base.html atau template yang sesuai
- [ ] Include navbar.html, sidebar.html jika diperlukan
- [ ] Use base/partials/form_field.html untuk form
- [ ] Link antar template dengan {% url %} tag
- [ ] Test semua connections & data flow

---

## 🚀 Useful Links

Untuk dokumentasi lebih detail, baca:
1. **Mulai dari:** MODULE_ARCHITECTURE.md (overview)
2. **Cari template:** TEMPLATE_CATALOG.md (inventory)
3. **Cari feature:** FEATURE_FILE_MAPPING.md (how-to)
4. **Technical details:** COMPONENT_ARCHITECTURE.md (implementation)

---

## 💡 Tips

1. **Untuk developer baru:** Mulai dari MODULE_ARCHITECTURE.md
2. **Untuk QA/tester:** Gunakan FEATURE_FILE_MAPPING.md
3. **Untuk designer:** Reference COMPONENT_ARCHITECTURE.md
4. **Untuk DevOps:** Baca MODULE_ARCHITECTURE.md untuk dependencies
5. **Untuk documentation:** Combine all 4 docs untuk complete picture

---

**Generated:** April 10, 2026  
**Total Templates Documented:** 102 files  
**Total Documentation Pages:** 4 files + 1 index  
**Status:** ✅ Complete

---

**File-file dokumentasi ini akan memudahkan Anda untuk:**
- ✅ Understand struktur lengkap sistem
- ✅ Find template untuk fitur tertentu
- ✅ Implement sambungan antar file
- ✅ Maintain & extend sistem
- ✅ Onboard developer baru
