# LUMRA ERP — Skenario Lengkap: Setup → Produksi → Penjualan

---

## Daftar Isi

1. [Fase 0 — Setup Awal](#fase-0-setup-awal)
2. [Fase 1 — Master Data](#fase-1-master-data)
3. [Fase 2 — Resep / Recipe](#fase-2-resep--recipe)
4. [Fase 3 — Barang Mentah Datang (Procurement)](#fase-3-barang-mentah-datang-procurement)
5. [Fase 4 — Transfer Gudang → Dapur](#fase-4-transfer-gudang--dapur-produksi)
6. [Fase 5 — Proses Produksi](#fase-5-proses-produksi)
7. [Fase 6 — Penjualan di POS](#fase-6-penjualan-di-pos)
8. [Mapping Tabel Database](#mapping-tabel-database)
9. [DDL Tabel yang Harus Dibuat](#ddl-tabel-yang-harus-dibuat)
10. [Urutan Prioritas Template](#urutan-prioritas-template)

---

## Fase 0: Setup Awal

Ditampilkan saat pertama kali login (onboarding wizard).

### 0.1 — Nama Bisnis

**Template:** `onboarding/step_business.html`

```
┌─────────────────────────────────────────────────────────────┐
│  Nama Bisnis  : [____________________________]             │
│  Logo         : [Upload Logo]                               │
│  Industri     : [▼ F&B / Retail / Jasa / Lainnya]          │
│  Alamat       : [____________________________]             │
│  Telepon      : [____________________________]             │
│  Email        : [____________________________]             │
│                                                 [Lanjut →] │
└─────────────────────────────────────────────────────────────┘
```

**Tabel:** `lumra_config_businessprofile`
- `business_name`, `logo`, `industry`, `address`, `phone`, `email`, `is_setup_completed`

---

### 0.2 — Lokasi / Toko / Cabang

**Template:** `onboarding/step_location.html`

```
┌─────────────────────────────────────────────────────────────┐
│  Nama Toko/Cabang : [____________________________]         │
│  Kode Lokasi      : [TKO-001]  ← auto-generate             │
│  Tipe             : [▼ Toko / Gudang / Dapur Produksi]     │
│  Alamat           : [____________________________]         │
│                                                 [Lanjut →] │
└─────────────────────────────────────────────────────────────┘
```

**Contoh data hasil:**

| ID | Nama Toko            | Kode     | Tipe            |
|----|----------------------|----------|-----------------|
|  1 | LUMRA Cafe Pusat     | TKO-001  | Toko            |
|  2 | Gudang Utama         | GUD-001  | Gudang          |
|  3 | Dapur Produksi       | DPR-001  | Dapur Produksi  |
|  4 | LUMRA Cafe Cabang 2  | TKO-002  | Toko            |

**Tabel:** `lumra_config_locations` — `id`, `name`, `code`, `type`, `address`

---

### 0.3 — Kategori Produk

**Template:** `onboarding/step_category.html`

Buat kategori dengan dukungan hierarki (parent → child).

**Contoh:**
- Bahan Baku *(root)*
- Produk Jadi *(root)*
  - Roti *(child dari Produk Jadi)*
  - Minuman *(child dari Produk Jadi)*
  - Kue *(child dari Produk Jadi)*

**Tabel:** `lumra_config_categories` — `id`, `name`, `parent_id`

---

### 0.4 — Setup Selesai

**Template:** `onboarding/step_complete.html`

```
✅  Setup Selesai!
    Bisnis    : LUMRA Cafe
    Lokasi    : 4 lokasi terdaftar
    Kategori  : 5 kategori

    Apa selanjutnya?
    → Tambah Produk & Supplier
    → Buat Resep
    → Undang Tim
    → Lihat Dashboard
```

---

## Fase 1: Master Data

### 1A — Satuan

**Template:** `units_list.html` → `unit_form.html`

| ID | Nama         | Simbol |
|----|--------------|--------|
|  1 | Kilogram     | kg     |
|  2 | Gram         | g      |
|  3 | Liter        | L      |
|  4 | Mililiter    | ml     |
|  5 | Pcs          | pcs    |
|  6 | Butir        | btr    |
|  7 | Sendok Makan | sdm    |

**Tabel:** `lumra_config_units` — `id`, `name`, `symbol`

---

### 1B — Supplier

**Template:** `vendors_list.html` → `vendor_form.html`

| ID | Nama Supplier          | Kontak        | Telepon      |
|----|------------------------|---------------|--------------|
|  1 | PT Bogasari Flour Mills | Budi Santoso  | 021-1234567  |
|  2 | CV Segar Jaya          | Siti Aminah   | 081-23456789 |
|  3 | UD Susu Makmur         | Pak Hadi      | 081-98765432 |

**Tabel:** `lumra_config_vendors` — `id`, `name`, `contact_person`, `phone`, `email`, `address`

---

### 1C — Produk Bahan Baku

**Template:** `products.html` → `product_details.html`

| SKU  | Nama Produk   | Kategori   | Satuan | Harga Beli |
|------|---------------|------------|--------|------------|
| BB01 | Tepung Terigu | Bahan Baku | kg     | 12.000     |
| BB02 | Gula Pasir    | Bahan Baku | kg     | 15.000     |
| BB03 | Telur Ayam    | Bahan Baku | btr    | 2.500      |
| BB04 | Margarin      | Bahan Baku | kg     | 25.000     |
| BB05 | Susu UHT      | Bahan Baku | L      | 18.000     |
| BB06 | Ragi Instan   | Bahan Baku | sdm    | 500        |
| BB07 | Garam         | Bahan Baku | kg     | 10.000     |
| BB08 | Coklat Bubuk  | Bahan Baku | kg     | 45.000     |

**Tabel:** `lumra_config_products`
- `sku_code`, `name`, `category_id`, `unit_id`, `cost_price`, `sell_price`
- `product_type`: `raw_material` untuk bahan baku, `finished_goods` untuk produk jadi

---

### 1D — Harga Supplier per Produk

**Template:** `supplier_price_list.html` → `supplier_price_form.html`

| Supplier              | Produk        | Harga Beli | Min. Order |
|-----------------------|---------------|------------|------------|
| PT Bogasari           | Tepung Terigu | 12.000     | 25 kg      |
| PT Bogasari           | Gula Pasir    | 14.000     | 10 kg      |
| CV Segar Jaya         | Telur Ayam    | 2.500      | 100 btr    |
| CV Segar Jaya         | Margarin      | 24.000     | 5 kg       |
| UD Susu Makmur        | Susu UHT      | 17.500     | 10 L       |
| CV Segar Jaya         | Ragi Instan   | 450        | 50 sdm     |
| CV Segar Jaya         | Garam         | 9.500      | 5 kg       |
| CV Segar Jaya         | Coklat Bubuk  | 43.000     | 1 kg       |

**Tabel:** `lumra_config_supplier_prices` — `vendor_id`, `product_id`, `price`, `min_order_qty`

---

### 1E — User / Pengguna

**Template:** `users.html` → form inline / modal

| Username | Email             | Role             | Lokasi Default      |
|----------|-------------------|------------------|---------------------|
| admin    | admin@lumra.com   | Super Admin      | LUMRA Cafe Pusat    |
| siti     | siti@lumra.com    | Manager Gudang   | Gudang Utama        |
| budi     | budi@lumra.com    | Kepala Produksi  | Dapur Produksi      |
| dewi     | dewi@lumra.com    | Kasir            | LUMRA Cafe Pusat    |
| rina     | rina@lumra.com    | Kasir            | LUMRA Cafe Cabang 2 |

**Tabel:** `auth_user` + `lumra_config_userprofile`
- `user_id`, `role`, `default_location_id`

---

## Fase 2: Resep / Recipe

### 2.1 — Buat Resep Roti Coklat

**Template:** `recipe_list.html` → `recipe_form.html`

```
┌─────────────────────────────────────────────────────────────┐
│  Nama Resep     : [Roti Coklat]                            │
│  Kategori       : [▼ Roti]                                 │
│  Deskripsi      : [Roti isi coklat lembut]                 │
│  Yield          : [10] pcs                                 │
│  Waktu Produksi : [120] menit                              │
│  Harga Jual     : [15.000] / pcs                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 — Bahan Baku Resep (Bill of Materials)

*(Untuk yield 10 pcs)*

| # | Bahan         | Qty  | Satuan | Subtotal Biaya |
|---|---------------|------|--------|----------------|
| 1 | Tepung Terigu | 1.0  | kg     | Rp 12.000      |
| 2 | Gula Pasir    | 0.2  | kg     | Rp 3.000       |
| 3 | Telur Ayam    | 4    | btr    | Rp 10.000      |
| 4 | Margarin      | 0.15 | kg     | Rp 3.750       |
| 5 | Susu UHT      | 0.3  | L      | Rp 5.400       |
| 6 | Ragi Instan   | 2    | sdm    | Rp 1.000       |
| 7 | Garam         | 0.01 | kg     | Rp 100         |
| 8 | Coklat Bubuk  | 0.1  | kg     | Rp 4.500       |

**Total Biaya Bahan:** Rp 23.800 untuk 10 pcs → **Rp 2.380 / pcs**
**Harga Jual:** Rp 15.000 / pcs → **Margin ±84%**

**Tabel:** `production_recipes`, `production_recipe_ingredients`

---

## Fase 3: Barang Mentah Datang (Procurement)

### 3.1 — Input Purchase Order

**Template:** `stock_purchasing.html`

```
┌─────────────────────────────────────────────────────────────┐
│  No. Pembelian : [PO-202401-0001]  ← auto                  │
│  Tanggal       : [15/01/2024]                               │
│  Supplier      : [▼ PT Bogasari]                            │
│  Lokasi Tujuan : [▼ Gudang Utama]                           │
└─────────────────────────────────────────────────────────────┘
```

| # | Produk        | Qty | Satuan | Harga  | Subtotal   |
|---|---------------|-----|--------|--------|------------|
| 1 | Tepung Terigu | 50  | kg     | 12.000 | 600.000    |
| 2 | Gula Pasir    | 20  | kg     | 14.000 | 280.000    |
| 3 | Telur Ayam    | 100 | btr    | 2.500  | 250.000    |
| 4 | Margarin      | 10  | kg     | 24.000 | 240.000    |
| 5 | Susu UHT      | 20  | L      | 17.500 | 350.000    |
| 6 | Ragi Instan   | 100 | sdm    | 450    | 45.000     |
| 7 | Garam         | 5   | kg     | 9.500  | 47.500     |
| 8 | Coklat Bubuk  | 5   | kg     | 43.000 | 215.000    |

Subtotal: Rp 2.027.500 · PPN 11%: Rp 223.025 · **Total: Rp 2.250.525**

### 3.2 — Yang Terjadi Saat Klik "Simpan & Terima Barang"

```
1. INSERT  lumra_config_orders           → PO-202401-0001, status: completed
2. INSERT  lumra_config_orderitems       → 8 baris item
3. UPDATE  lumra_config_stock            → stok tiap produk di Gudang +qty
4. INSERT  lumra_config_stockmovement    → movement_type: "purchase", qty positif
```

---

## Fase 4: Transfer Gudang → Dapur Produksi

### 4.1 — Kepala Produksi Buat Requisition

**Template:** `requisition_list.html` → `requisition_form.html`

```
┌─────────────────────────────────────────────────────────────┐
│  No. Permintaan : [REQ-202401-0001]                        │
│  Diminta oleh   : Budi (Kepala Produksi)                   │
│  Dari Lokasi    : [▼ Gudang Utama]                         │
│  Ke Lokasi      : [▼ Dapur Produksi]                       │
│  Keterangan     : Produksi Roti Coklat 50 pcs              │
└─────────────────────────────────────────────────────────────┘
```

*(Qty diminta = 5× resep, untuk target 50 pcs)*

| # | Bahan         | Diminta | Stok Gudang |
|---|---------------|---------|-------------|
| 1 | Tepung Terigu | 5.0 kg  | 50 kg  ✅   |
| 2 | Gula Pasir    | 1.0 kg  | 20 kg  ✅   |
| 3 | Telur Ayam    | 20 btr  | 100 btr ✅  |
| 4 | Margarin      | 0.75 kg | 10 kg  ✅   |
| 5 | Susu UHT      | 1.5 L   | 20 L   ✅   |
| 6 | Ragi Instan   | 10 sdm  | 100 sdm ✅  |
| 7 | Garam         | 0.05 kg | 5 kg   ✅   |
| 8 | Coklat Bubuk  | 0.5 kg  | 5 kg   ✅   |

### 4.2 — Approval oleh Manager Gudang

Manager Gudang (Siti) review dan approve requisition.
- Status berubah: `pending` → `approved`
- Dicatat: `approved_by`, `approved_at`

### 4.3 — Eksekusi Transfer

**Template:** `transfer_form.html`

```
┌─────────────────────────────────────────────────────────────┐
│  No. Transfer : [TRF-202401-0001]                          │
│  Referensi    : [REQ-202401-0001]                          │
│  Dari         : Gudang Utama                               │
│  Ke           : Dapur Produksi                             │
└─────────────────────────────────────────────────────────────┘
```

**Yang terjadi saat "Konfirmasi Transfer":**

```
1. INSERT  lumra_config_transfers        → TRF-202401-0001, status: completed
2. INSERT  lumra_config_transferitem     → 8 baris
3. UPDATE  lumra_config_stock            → Gudang berkurang, Dapur bertambah
4. INSERT  lumra_config_stockmovement    → "transfer_out" (Gudang) + "transfer_in" (Dapur)
5. UPDATE  lumra_config_requisitions     → status: "fulfilled"
```

**Contoh perubahan stok Tepung Terigu:**

| Lokasi        | Sebelum | Sesudah |
|---------------|---------|---------|
| Gudang Utama  | 50 kg   | 45 kg   |
| Dapur Produksi| 0 kg    | 5 kg    |

---

## Fase 5: Proses Produksi

### 5.1 — Buat Production Order

**Template:** `production_order_form.html`

```
┌─────────────────────────────────────────────────────────────┐
│  No. Produksi    : [PRD-202401-0001]                       │
│  Resep           : [▼ Roti Coklat]                         │
│  Lokasi Produksi : [▼ Dapur Produksi]                      │
│  Ditugaskan ke   : [▼ Budi Prasetya]                       │
│  Target Output   : [50] pcs                                │
│  Lokasi Output   : [▼ LUMRA Cafe Pusat]                    │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 — Kebutuhan Bahan (Otomatis dari Resep × Ratio)

Ratio = Target (50) ÷ Yield Resep (10) = **5×**

| # | Bahan         | Qty Dibutuhkan | Tersedia | Status |
|---|---------------|----------------|----------|--------|
| 1 | Tepung Terigu | 5.0 kg         | 5.0 kg   | ✅     |
| 2 | Gula Pasir    | 1.0 kg         | 1.0 kg   | ✅     |
| 3 | Telur Ayam    | 20 btr         | 20 btr   | ✅     |
| 4 | Margarin      | 0.75 kg        | 0.75 kg  | ✅     |
| 5 | Susu UHT      | 1.5 L          | 1.5 L    | ✅     |
| 6 | Ragi Instan   | 10 sdm         | 10 sdm   | ✅     |
| 7 | Garam         | 0.05 kg        | 0.05 kg  | ✅     |
| 8 | Coklat Bubuk  | 0.5 kg         | 0.5 kg   | ✅     |

**Estimasi Biaya:** Rp 119.000 untuk 50 pcs → **Rp 2.380 / pcs**

### 5.3 — Saat "Mulai Produksi" Diklik

```
1. UPDATE  lumra_config_production_orders  → status: "in_progress", started_at: now()
2. UPDATE  lumra_config_stock              → stok bahan baku di Dapur berkurang
3. INSERT  lumra_config_stockmovement      → movement_type: "production_out" (qty negatif)
4. INSERT  lumra_config_production_order_materials → catat qty tiap bahan yang dipakai
```

### 5.4 — Saat "Selesai Produksi" Diklik

Input aktual hasil (bisa berbeda dari target karena waste):

```
Target   : 50 pcs
Aktual   : 48 pcs  ← input manual
Waste    : 2 pcs   → "2 pcs gosong, tidak bisa dijual"
```

```
1. UPDATE  lumra_config_production_orders  → status: "completed", actual_qty: 48, waste_qty: 2
2. UPDATE  lumra_config_stock              → stok Roti Coklat di LUMRA Cafe Pusat +48 pcs
3. INSERT  lumra_config_stockmovement      → movement_type: "production_in" di Toko Pusat
```

**Biaya aktual/pcs:** Rp 119.000 ÷ 48 = **Rp 2.479 / pcs** *(lebih mahal karena waste)*

---

## Fase 6: Penjualan di POS

### 6.1 — Tampilan POS

**Template:** `pos.html`

```
┌──────────────────────────────────────────────────────────────┐
│  LUMRA Cafe Pusat  │  Kasir: Dewi  │  17/01/2024            │
│  🔍 Cari produk...                                           │
│  [Semua] [Roti] [Kue] [Minuman]                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  🍞           │  │  🥐           │  │  🍰           │       │
│  │  Roti Coklat │  │  Croissant   │  │  Brownies    │       │
│  │  Rp 15.000   │  │  Rp 18.000   │  │  Rp 20.000   │       │
│  │  Stok: 48    │  │  Stok: 15    │  │  Stok: 8     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 — Contoh Transaksi 1 (Tunai)

| Item         | Qty | Harga  | Subtotal |
|--------------|-----|--------|----------|
| Roti Coklat  | 2   | 15.000 | 30.000   |

Subtotal: Rp 30.000 · PPN 11%: Rp 3.300 · **Total: Rp 33.300**
Bayar: Rp 50.000 · Kembalian: **Rp 16.700**

### 6.3 — Yang Terjadi Saat "BAYAR" Diklik

```
1. INSERT  lumra_config_orders         → SO-202401-0001, order_type: "sales", status: "completed"
2. INSERT  lumra_config_orderitems     → Roti Coklat × 2
3. UPDATE  lumra_config_stock          → stok Roti Coklat di Toko berkurang -2
4. INSERT  lumra_config_stockmovement  → movement_type: "sale", qty: -2
5. INSERT  lumra_config_payments       → payment_method: "cash", amount: 33.300
```

### 6.4 — Struk Thermal (58mm)

```
╔══════════════════════════════════════╗
║        LUMRA CAFE PUSAT              ║
║    Jl. Merdeka No. 1, Jakarta        ║
║    Telp: 021-1234567                 ║
╠══════════════════════════════════════╣
║ 17/01/2024  10:30  │  Kasir: Dewi   ║
║ No: SO-202401-0001                   ║
╠══════════════════════════════════════╣
║ Roti Coklat  2 ×  15.000 =  30.000  ║
╠══════════════════════════════════════╣
║ Subtotal              Rp  30.000     ║
║ PPN 11%               Rp   3.300     ║
║ TOTAL                 Rp  33.300     ║
║ Tunai                 Rp  50.000     ║
║ Kembalian             Rp  16.700     ║
╠══════════════════════════════════════╣
║      Terima kasih atas kunjungan!    ║
╚══════════════════════════════════════╝
```

**Template:** `print/print_receipt.html`

### 6.5 — Proses Retur

Jika pelanggan mengembalikan produk:

```
1. INSERT  lumra_config_returns        → return_code: RET-202401-0001
2. INSERT  lumra_config_returnitems    → Roti Coklat × 1
3. UPDATE  lumra_config_stock          → stok Roti Coklat +1 (kembali ke toko)
4. INSERT  lumra_config_stockmovement  → movement_type: "return_in", qty: +1
```

---

## Mapping Tabel Database

| Fase              | Tabel                                    | Status        |
|-------------------|------------------------------------------|---------------|
| Setup Awal        | `lumra_config_locations`                 | ✅ Ada        |
|                   | `lumra_config_categories`                | ✅ Ada        |
|                   | `lumra_config_businessprofile`           | ✅ Ada        |
| Master Data       | `lumra_config_units`                     | ✅ Ada        |
|                   | `lumra_config_vendors`                   | ✅ Ada        |
|                   | `lumra_config_products`                  | ✅ Ada        |
|                   | `lumra_config_supplier_prices`           | ✅ Ada        |
|                   | `auth_user` + `lumra_config_userprofile` | ✅ Ada        |
| Resep             | `production_recipe_categories`           | ✅ Ada        |
|                   | `production_recipes`                     | ✅ Ada        |
|                   | `production_recipe_ingredients`          | ✅ Ada        |
| Procurement       | `lumra_config_orders`                    | ✅ Ada        |
|                   | `lumra_config_orderitems`                | ✅ Ada        |
|                   | `lumra_config_stock`                     | ✅ Ada        |
|                   | `lumra_config_stockmovement`             | ❌ Harus buat |
| Transfer          | `lumra_config_requisitions`              | ✅ Ada        |
|                   | `lumra_config_requisitionitems`          | ✅ Ada        |
|                   | `lumra_config_transfers`                 | ✅ Ada        |
|                   | `lumra_config_transferitems`             | ✅ Ada        |
| Produksi          | `lumra_config_production_orders`         | ❌ Harus buat |
|                   | `lumra_config_production_order_materials`| ❌ Harus buat |
| POS Penjualan     | `lumra_config_orders`                    | ✅ Ada        |
|                   | `lumra_config_orderitems`                | ✅ Ada        |
|                   | `lumra_config_stockmovement`             | ❌ Harus buat |
|                   | `lumra_config_payments`                  | ❌ Harus buat |
| Retur             | `lumra_config_returns`                   | ❌ Harus buat |
|                   | `lumra_config_returnitems`               | ❌ Harus buat |

---

## DDL Tabel yang Harus Dibuat

### 1. Stock Movement Log *(Paling Kritis)*

```sql
CREATE TABLE lumra_config_stockmovement (
    id             BIGINT       PRIMARY KEY AUTO_INCREMENT,
    product_id     BIGINT       NOT NULL,      -- FK → products
    location_id    BIGINT       NOT NULL,      -- FK → locations
    quantity       DECIMAL(15,4) NOT NULL,     -- + masuk, - keluar
    movement_type  VARCHAR(30)  NOT NULL,
        -- purchase | sale | adjustment | opname
        -- transfer_in | transfer_out
        -- production_in | production_out
        -- return_in
    reference_code VARCHAR(50)  NULL,          -- PO-xxx, SO-xxx, PRD-xxx
    reference_type VARCHAR(30)  NULL,          -- order | transfer | production_order | return
    notes          TEXT         NULL,
    created_by     BIGINT       NOT NULL,      -- FK → auth_user
    created_at     DATETIME     NOT NULL DEFAULT NOW(),

    INDEX idx_product_location (product_id, location_id),
    INDEX idx_movement_type    (movement_type),
    INDEX idx_reference        (reference_code),
    INDEX idx_created_at       (created_at)
);
```

### 2. Payments

```sql
CREATE TABLE lumra_config_payments (
    id             BIGINT       PRIMARY KEY AUTO_INCREMENT,
    payment_code   VARCHAR(50)  NOT NULL UNIQUE,
    order_id       BIGINT       NOT NULL,      -- FK → orders
    payment_method VARCHAR(30)  NOT NULL,      -- cash | card | qris | transfer
    amount         DECIMAL(15,2) NOT NULL,
    reference_no   VARCHAR(100) NULL,          -- nomor referensi EDC / QRIS
    paid_at        DATETIME     NOT NULL,
    created_by     BIGINT       NOT NULL,
    created_at     DATETIME     NOT NULL DEFAULT NOW(),

    INDEX idx_order         (order_id),
    INDEX idx_payment_method(payment_method),
    INDEX idx_paid_at       (paid_at)
);
```

### 3. Production Orders

```sql
CREATE TABLE lumra_config_production_orders (
    id                  BIGINT       PRIMARY KEY AUTO_INCREMENT,
    po_code             VARCHAR(50)  NOT NULL UNIQUE,
    recipe_id           BIGINT       NOT NULL,  -- FK → production_recipes
    location_id         BIGINT       NOT NULL,  -- FK → locations (dapur)
    output_location_id  BIGINT       NULL,       -- FK → locations (toko tujuan)
    assigned_to         BIGINT       NULL,       -- FK → auth_user
    target_qty          DECIMAL(15,4) NOT NULL,
    actual_qty          DECIMAL(15,4) NULL,
    waste_qty           DECIMAL(15,4) NULL DEFAULT 0,
    waste_reason        TEXT         NULL,
    total_material_cost DECIMAL(15,2) NULL,
    status              VARCHAR(20)  NOT NULL DEFAULT 'draft',
        -- draft | in_progress | completed | cancelled
    started_at          DATETIME     NULL,
    completed_at        DATETIME     NULL,
    notes               TEXT         NULL,
    created_by          BIGINT       NOT NULL,
    created_at          DATETIME     NOT NULL DEFAULT NOW(),
    updated_at          DATETIME     NOT NULL DEFAULT NOW() ON UPDATE NOW(),

    INDEX idx_recipe    (recipe_id),
    INDEX idx_location  (location_id),
    INDEX idx_status    (status),
    INDEX idx_created_at(created_at)
);
```

### 4. Production Order Materials

```sql
CREATE TABLE lumra_config_production_order_materials (
    id                   BIGINT        PRIMARY KEY AUTO_INCREMENT,
    production_order_id  BIGINT        NOT NULL,  -- FK → production_orders
    product_id           BIGINT        NOT NULL,  -- FK → products (bahan baku)
    unit_id              BIGINT        NOT NULL,  -- FK → units
    quantity_required    DECIMAL(15,4) NOT NULL,  -- dari resep × ratio
    quantity_used        DECIMAL(15,4) NULL,      -- aktual dipakai
    cost_price           DECIMAL(15,2) NULL,      -- harga saat dipakai

    INDEX idx_po     (production_order_id),
    INDEX idx_product(product_id)
);
```

### 5. Returns & Return Items

```sql
CREATE TABLE lumra_config_returns (
    id           BIGINT        PRIMARY KEY AUTO_INCREMENT,
    return_code  VARCHAR(50)   NOT NULL UNIQUE,
    order_id     BIGINT        NOT NULL,   -- FK → orders
    customer_id  BIGINT        NULL,
    return_date  DATETIME      NOT NULL,
    subtotal     DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_amount   DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    status       VARCHAR(20)   NOT NULL DEFAULT 'pending',
        -- pending | approved | completed | cancelled
    reason       TEXT          NULL,
    notes        TEXT          NULL,
    created_by   BIGINT        NOT NULL,
    created_at   DATETIME      NOT NULL DEFAULT NOW(),

    INDEX idx_order (order_id),
    INDEX idx_status(status)
);

CREATE TABLE lumra_config_returnitems (
    id            BIGINT        PRIMARY KEY AUTO_INCREMENT,
    return_id     BIGINT        NOT NULL,  -- FK → returns
    product_id    BIGINT        NOT NULL,  -- FK → products
    quantity      DECIMAL(15,4) NOT NULL,
    unit_price    DECIMAL(15,2) NOT NULL,
    subtotal      DECIMAL(15,2) NOT NULL,
    reason        VARCHAR(255)  NULL,

    INDEX idx_return (return_id),
    INDEX idx_product(product_id)
);
```

---

## Urutan Prioritas Template

| Prioritas | Template                                      | Kebutuhan Tabel              |
|-----------|-----------------------------------------------|------------------------------|
| 1️⃣        | `onboarding/welcome.html`                     | —                            |
| 1️⃣        | `onboarding/step_business.html`               | businessprofile              |
| 1️⃣        | `onboarding/step_location.html`               | locations                    |
| 1️⃣        | `onboarding/step_category.html`               | categories                   |
| 1️⃣        | `onboarding/step_complete.html`               | —                            |
| 2️⃣        | `inventory/transfer_list.html`                | transfers                    |
| 2️⃣        | `inventory/transfer_form.html`                | transfers + transferitems    |
| 2️⃣        | `inventory/transfer_detail.html`              | transfers + transferitems    |
| 3️⃣        | `production/production_order_form.html`       | recipes + stock              |
| 3️⃣        | `production/production_order_detail.html`     | production_orders            |
| 3️⃣        | `production/material_consumption.html`        | production_order_materials   |
| 4️⃣        | `sales/order_list.html`                       | orders                       |
| 4️⃣        | `sales/order_detail.html`                     | orders + orderitems          |
| 5️⃣        | `print/print_receipt.html`                    | orders + orderitems          |
| 5️⃣        | `print/print_purchase_order.html`             | orders + orderitems          |
| 5️⃣        | `print/print_production_order.html`           | production_orders            |
| 6️⃣        | `partials/print_base.html`                    | —                            |
| 7️⃣        | `sales/retur_list.html`                       | returns                      |
| 7️⃣        | `sales/retur_form.html`                       | returns + returnitems        |
| 7️⃣        | `sales/retur_detail.html`                     | returns + returnitems        |

---

*Dokumen ini sinkron dengan `test_full_flow.py` — jalankan script tersebut untuk memvalidasi seluruh alur secara otomatis.*