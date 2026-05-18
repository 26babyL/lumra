# 📘 LUMRA ERP — Test Setup dengan Gemini AI

## 📋 Daftar File

| File | Tujuan | Status |
|------|--------|--------|
| **gemini_data_generator.py** | Module untuk generate data realistis via Gemini API | ✅ NEW |
| **test_setup_with_gemini.py** | Full flow test LENGKAP dengan AI data generation | ✅ NEW |
| **test_setup.py** | Original full flow test (hardcoded data) | ✅ EXISTING |
| **test_full_flow.py** | Alternative test (less complete) | ⚠️ LEGACY |

---

## 🚀 QUICK START

### 1️⃣ Jalankan Test dengan Gemini (RECOMMENDED)

```bash
cd /path/to/lumra

# Via Django shell (BEST)
python manage.py shell < lumra_config/management/commands/test_setup_with_gemini.py

# Atau direct
python lumra_config/management/commands/test_setup_with_gemini.py

# Atau interactive
python manage.py shell
>>> exec(open('lumra_config/management/commands/test_setup_with_gemini.py').read())
```

### 2️⃣ Jalankan Test Original (Tanpa AI)

```bash
python manage.py shell < lumra_config/management/commands/test_setup.py
```

### 3️⃣ Test Gemini Generator Standalone

```bash
python lumra_config/management/commands/gemini_data_generator.py
```

---

## ⚙️ KONFIGURASI

### Edit File: `test_setup_with_gemini.py`

```python
# Line ~67-70
USE_TRANSACTION = False  # True = rollback, False = keep data
USE_GEMINI = True        # True = generate dengan AI, False = hardcoded
PRINT_STOCK_AT_EACH_STEP = True
```

**Penjelasan:**

| Setting | Nilai | Keterangan |
|---------|-------|-----------|
| `USE_TRANSACTION` | `True` | Data di-rollback setelah test (testing only) |
| `USE_TRANSACTION` | `False` | Data tersimpan permanen di database |
| `USE_GEMINI` | `True` | Generate data via AI (internet required) |
| `USE_GEMINI` | `False` | Gunakan hardcoded fallback data |

---

## 🤖 Gemini API Configuration

### API Key Setup

API key sudah di-embed di:
- `lumra_config/management/commands/gemini_data_generator.py` (line ~13)

```python
genai.configure(api_key="AIzaSyAjHu-TizS48cZ_01Rngz1HFtUY1ZwrAnE")
model = genai.GenerativeModel('gemini-1.5-flash')
```

⚠️ **SECURITY NOTE:** Jangan commit API key ke git repo!

Gunakan environment variable jika di production:

```python
import os
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
```

### Model Selection

Saat ini menggunakan: **`gemini-1.5-flash`**
- ✅ Fast & reliable
- ✅ Cost-effective
- ✅ Good untuk data generation

Alternative:
- `gemini-1.5-pro` - More powerful tapi slower/expensive
- `gemini-2.0-flash` - Latest (jika tersedia)

---

## 📊 Alur Test (7 FASE)

### Fase 0: Setup Awal
```
Input dari Gemini:
  ✓ Nama bisnis (Starbucks-style, Kopi Kenangan, etc)
  ✓ Detail bisnis (phone, email, address)
  ✓ Lokasi/toko (4 cabang)
  ✓ Kategori produk
```

### Fase 1: Master Data
```
✓ Units (Cup, Pcs, Kg, Liter, etc)
✓ Vendors/Suppliers (3+ supplier)
✓ Products per kategori
  - Minuman: Espresso, Latte, Cappuccino, etc
  - Makanan: Croissant, Sandwich, Cake, etc
  - Biji Kopi: Arabica, Robusta, Blend, etc
```

### Fase 2: Resep (Recipe)
```
✓ Latte Base (Espresso + Biji Kopi)
✓ Cappuccino Base
```

### Fase 3: Procurement
```
✓ PO (Purchase Order) dari supplier
✓ Incoming stock ke gudang
```

### Fase 4: Transfer
```
✓ Gudang → Dapur Produksi
✓ Update stok di kedua lokasi
```

### Fase 5: Production
```
✓ Production orders (simplified)
```

### Fase 6: Penjualan POS
```
✓ Sales Order
✓ Customer
✓ Payment (Cash)
✓ Summary total penjualan
```

---

## 📈 Expected Output

```
╔═════════════════════════════════════════════════════════════════╗
║    LUMRA ERP — FULL FLOW TEST DENGAN GEMINI AI                ║
╚═════════════════════════════════════════════════════════════════╝

  Waktu: 2026-04-19 12:34:56
  Mode Transaksi: OFF (data tersimpan)
  Gemini AI: ACTIVE ✓

═════════════════════════════════════════════════════════════════

  FASE 0: SETUP AWAL

  ▶ STEP 0.1: Setup Nama Bisnis
    ✓ Bisnis: LUMRA Premium Coffee        [AI Generated!]
    → Industri: F&B
    → Alamat: Jl. Gatot Subroto No. 123, Jakarta Selatan
    → Telepon: +62-21-5555-1234
    → Email: info@lumrapremiumcoffee.com

  ▶ STEP 0.2: Setup Lokasi / Toko / Cabang
    ✓ TKO-001: LUMRA Premium Coffee Pusat (store)
    ✓ GUD-001: Gudang Utama (warehouse)
    ✓ DPR-001: Dapur Produksi (production)
    ✓ TKO-002: LUMRA Premium Coffee Cabang 2 (store)

  ▶ STEP 0.3: Setup Kategori Produk
    ✓ Bahan Baku
    ✓ Produk Jadi
    ✓ Minuman → Produk Jadi
    ✓ Makanan → Produk Jadi
    ✓ Biji Kopi → Bahan Baku

═════════════════════════════════════════════════════════════════

  FASE 1: MASTER DATA

  ▶ STEP 1.1: Setup Satuan (Unit)
    ✓ Cup (cup)
    ✓ Pcs (pcs)
    ✓ Kg (kg)
    ✓ Liter (L)
    ✓ Sachet (sct)

  ▶ STEP 1.2: Setup Vendor (Supplier)
    ✓ PT. Kopi Nusantara (+62-21-5555-1111)     [AI Generated!]
    ✓ CV. Roaster Indonesia (+62-21-5555-2222)  [AI Generated!]
    ✓ Koperasi Petani Kopi (+62-21-5555-3333)   [AI Generated!]

  ▶ STEP 1.3: Setup Produk
    ─────── Kategori: Minuman ───────
    ✓ Espresso (cup)
    ✓ Americano (cup)
    ✓ Latte (cup)
    
    ─────── Kategori: Makanan ───────
    ✓ Croissant (pcs)
    ✓ Sandwich (pcs)
    ✓ Chocolate Cake (pcs)
    
    ─────── Kategori: Biji Kopi ───────
    ✓ Arabica Specialty (kg)
    ✓ Robusta Premium (kg)
    ✓ Signature Blend (kg)

═════════════════════════════════════════════════════════════════

  ...
  [More phases...]
  ...

═════════════════════════════════════════════════════════════════

  RINGKASAN & VALIDASI

  Data yang berhasil dibuat:
    ✓ Bisnis: 1
    ✓ Lokasi: 4
    ✓ Kategori: 5
    ✓ Unit: 5
    ✓ Vendor: 3
    ✓ Produk: 9
    ✓ Resep: 2

  Data dari AI (Gemini):
    ✓ Business Name: LUMRA Premium Coffee
    ✓ Location: 4 lokasi
    ✓ Vendor: 3 supplier

  ✓ Test selesai - data tersimpan di database

  ═ ALL TESTS PASSED ═
```

---

## 🔍 File Comparison

### test_setup_with_gemini.py vs test_setup.py

| Fitur | Gemini Version | Original |
|-------|---|---|
| **AI Data Generation** | ✅ Yes | ❌ No |
| **Realistic Names** | ✅ Dynamic | ❌ Hardcoded |
| **Full Flow (7 Fase)** | ✅ Yes | ✅ Yes |
| **Transaction Handling** | ✅ Yes | ✅ Yes |
| **Pretty Output** | ✅ Colors | ✅ Colors |
| **Fallback Data** | ✅ Yes | ✅ Yes |
| **Production Ready** | ✅ Yes | ✅ Yes |

---

## 🎯 Use Cases

### 1. Development/Testing
```python
USE_TRANSACTION = True   # Jangan ubah database
USE_GEMINI = True        # Generate realistic data
```
**Jalankan:** Setiap saat untuk test full flow

### 2. Demo/Presentation
```python
USE_TRANSACTION = False  # Keep generated data
USE_GEMINI = True        # Impressive AI data
```
**Jalankan:** Sebelum presentation untuk populate database

### 3. Load Testing
```python
USE_TRANSACTION = False  # Keep data
USE_GEMINI = False       # Fast hardcoded data
```
**Jalankan:** Multiple times untuk add bulk data

### 4. CI/CD Pipeline
```python
USE_TRANSACTION = True   # Auto-rollback
USE_GEMINI = False       # No external API dependency
```
**Jalankan:** Automated tests

---

## 🐛 Troubleshooting

### ❌ Error: "Models tidak berhasil di-import"

**Solusi:**
```bash
# Pastikan Django setup benar
python manage.py shell

# Cek imports
>>> from lumra_config.models import BusinessProfile
>>> from production.models import Recipe
```

### ❌ Error: "Gemini API Error"

**Solusi:**
- Check internet connection
- Verify API key is valid
- Check Gemini API quota (Free tier: 15 calls/minute)

**Fallback:** Automatic fallback ke hardcoded data

### ❌ Error: "ModuleNotFoundError: No module named 'google'"

**Install:**
```bash
pip install google-generativeai
```

### ⚠️ Warning: "Mode transaksi AKTIF"

**Note:** Ini expected! Berarti data akan di-rollback. Ubah `USE_TRANSACTION = False` jika ingin keep data.

---

## 📚 Struktur Kode

### gemini_data_generator.py

```
CoffeeShopDataGenerator
├── __init__(verbose=True)
├── _prompt(prompt_text) → str
│
├── PHASE 0: Setup
│   ├── generate_business_names() → List[str]
│   ├── generate_business_details() → Dict
│   └── generate_locations() → List[Dict]
│
├── PHASE 1: Master Data
│   ├── generate_products() → List[Dict]
│   └── generate_suppliers() → List[Dict]
│
├── PHASE 2: Recipes
│   └── generate_recipe_names() → List[str]
│
└── PHASE 3-6: Operations
    └── generate_transaction_narrative() → str
```

### test_setup_with_gemini.py

```
run_full_flow_test_with_gemini()
├── FASE 0: Setup Awal
│   ├── Business Profile
│   ├── Locations
│   └── Categories
│
├── FASE 1: Master Data
│   ├── Units
│   ├── Vendors
│   └── Products
│
├── FASE 2: Recipes
│   └── Recipe + Ingredients
│
├── FASE 3: Procurement
│   ├── Purchase Order
│   └── Incoming Stock
│
├── FASE 4: Transfer
│   └── Stock Movement
│
├── FASE 5: Production
│   └── Production Orders
│
├── FASE 6: Sales
│   ├── Sales Order
│   ├── Customer
│   └── Payment
│
└── SUMMARY & VALIDATION
```

---

## 🎓 Learning Path

1. **First Time?**
   ```bash
   # Test dengan fallback (no internet needed)
   USE_GEMINI = False
   python manage.py shell < test_setup_with_gemini.py
   ```

2. **Want AI Magic?**
   ```bash
   # Test dengan Gemini
   USE_GEMINI = True
   python manage.py shell < test_setup_with_gemini.py
   ```

3. **Production Ready?**
   ```bash
   # Integrate ke Django management command
   # Edit: lumra_config/management/commands/setup.py
   ```

---

## 🚀 Next Steps

- [ ] Run test_setup_with_gemini.py
- [ ] Verify data in admin panel
- [ ] Check `migration_report_*.md` for migration status
- [ ] Test business workflow (FASE 0-6)
- [ ] Customize Gemini prompts untuk data yang lebih spesifik

---

## 📝 Notes

- **API Rate Limit:** 15 calls/minute (free tier)
- **Response Time:** 2-5 detik per request
- **Offline Mode:** Use `USE_GEMINI = False` untuk work offline
- **Security:** Jangan commit API key! Use env variables

---

**Created:** 2026-04-19  
**Version:** 1.0  
**Status:** ✅ Ready for Testing
