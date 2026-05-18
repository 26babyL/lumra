bantu saya merekap agar mana dulu yang harus diselesaikan github copilot, supaya lebih cepat dan terarah. jadi tidak menghabiskan banyak token

ProgrammingError at /inventory/batch/
relation "lumra_config_inventory_batches" does not exist
LINE 1: ...type", "lumra_config_locations"."created_at" FROM "lumra_con

ProgrammingError at /production/bom/
relation "production_boms" does not exist
LINE 1: ...ed_at", "lumra_config_products"."updated_at" FROM "productio

ProgrammingError at /production/order/
relation "production_orders" does not exist
LINE 1: ... "_units"."is_active", "_units"."created_at" FROM "productio

ProgrammingError at /production/scheduling/
relation "production_orders" does not exist
LINE 1: ...ed_at", "lumra_config_products"."updated_at" FROM "productio

ProgrammingError at /production/consumption/
relation "production_material_consumptions" does not exist
LINE 1: ... "_units"."is_active", "_units"."created_at" FROM "productio

ProgrammingError at /production/finished/
relation "production_finished_goods_receipts" does not exist
LINE 1: ...type", "lumra_config_locations"."created_at" FROM "productio

ProgrammingError at /accounting/coa/
relation "accounting_accounts" does not exist
LINE 1: ...T2."notes", T2."created_at", T2."updated_at" FROM "accountin

ProgrammingError at /accounting/ledger/
relation "accounting_accounts" does not exist
LINE 1: ...ated_at", "accounting_accounts"."updated_at" FROM "accountin

ProgrammingError at /accounting/journal/
relation "accounting_journal_entries" does not exist
LINE 1: ...", "accounting_journal_entries"."updated_at" FROM "accountin

ProgrammingError at /accounting/voucher/
relation "accounting_accounts" does not exist
LINE 1: ...ated_at", "accounting_accounts"."updated_at" FROM "accountin

ProgrammingError at /accounting/voucher/
relation "accounting_accounts" does not exist
LINE 1: ...ated_at", "accounting_accounts"."updated_at" FROM "accountin

ProgrammingError at /accounting/trial-balance/
relation "accounting_accounts" does not exist
LINE 1: ...ated_at", "accounting_accounts"."updated_at" FROM "accountin

ProgrammingError at /accounting/balance-sheet/
relation "accounting_accounts" does not exist
LINE 1: ...ated_at", "accounting_accounts"."updated_at" FROM "accountin

ProgrammingError at /accounting/income-statement/
relation "accounting_accounts" does not exist
LINE 1: ...ated_at", "accounting_accounts"."updated_at" FROM "accountin

ProgrammingError at /accounting/cash-flow/
relation "accounting_accounts" does not exist
LINE 1: ...ated_at", "accounting_accounts"."updated_at" FROM "accountin

ProgrammingError at /accounting/ar/
relation "accounting_accounts_receivable" does not exist
LINE 1: ..., "lumra_config_customers"."last_order_date" FROM "accountin

ProgrammingError at /warehouse/zones/
relation "lumra_config_warehouse_zones" does not exist
LINE 1: ...type", "lumra_config_locations"."created_at" FROM "lumra_con

NameError at /master/vendors/
name 'q' is not defined

NameError at /master/categories/
name 'q' is not defined

NameError at /master/units/
name 'q' is not defined

ProgrammingError at /reports/expiry/
relation "lumra_config_inventory_batches" does not exist
LINE 1: ...type", "lumra_config_locations"."created_at" FROM "lumra_con

ProgrammingError at /reports/inventory-age/
relation "lumra_config_inventory_batches" does not exist
LINE 1: ...type", "lumra_config_locations"."created_at" FROM "lumra_con

ProgrammingError at /reports/production/
relation "production_orders" does not exist
LINE 1: ...ed_at", "lumra_config_products"."updated_at" FROM "productio

ProgrammingError at /settings/users/
relation "system_user_roles" does not exist
LINE 1: ...r_id", "system_roles"."name" AS "role__name" FROM "system_us

ProgrammingError at /settings/permissions/
relation "system_role_permissions" does not exist
LINE 1: SELECT 1 AS "a" FROM "system_role_permissions" LIMIT 1

ProgrammingError at /settings/email/
relation "system_email_settings" does not exist
LINE 1: ...by_id", "system_email_settings"."updated_at" FROM "system_em

ProgrammingError at /settings/numbering/
relation "system_numbering_sequences" does not exist
LINE 1: ...", "system_numbering_sequences"."updated_at" FROM "system_nu

ProgrammingError at /settings/backup/
relation "system_backup_records" does not exist
LINE 1: SELECT 1 AS "a" FROM "system_backup_records" LIMIT 1

ProgrammingError at /settings/api-keys/
relation "system_api_keys" does not exist
LINE 1: SELECT 1 AS "a" FROM "system_api_keys" LIMIT 1

# 🎯 REKAP & PRIORITAS FIX

## Diagnosa Cepat

Ada **2 jenis masalah**, bukan sekadar "tabel belum ada":

```
JENIS A — Nama tabel beda (views pakai nama X, DB pakai nama Y)
JENIS B — Tabel memang belum ada sama sekali (model belum dibuat)
JENIS C — Bug kode sederhana (bukan DB)
```

---

## PETA KESALAHAN

| # | Error | Jenis | Root Cause | Fix |
|---|-------|-------|------------|-----|
| 1 | `lumra_config_inventory_batches` | **A** | Views pakai nama ini, tapi DB ada `lumra_config_productbatches` | Rename db_table ATAU fix views |
| 2 | `lumra_config_warehouse_zones` | **B** | Model belum ada | Buat model + migrate |
| 3 | `production_boms` | **A** | Views pakai ini, DB ada `production_recipes` | Rename db_table ATAU fix views |
| 4 | `production_orders` | **B** | Model belum ada | Buat model + migrate |
| 5 | `production_material_consumptions` | **B** | Model belum ada | Buat model + migrate |
| 6 | `production_finished_goods_receipts` | **B** | Model belum ada | Buat model + migrate |
| 7 | `accounting_accounts` | **B** | Model belum ada | Buat model + migrate |
| 8 | `accounting_journal_entries` | **B** | Model belum ada | Buat model + migrate |
| 9 | `accounting_accounts_receivable` | **B** | Model belum ada | Buat model + migrate |
| 10 | `system_user_roles` | **B** | Model belum ada | Buat model + migrate |
| 11 | `system_role_permissions` | **B** | Model belum ada | Buat model + migrate |
| 12 | `system_email_settings` | **B** | Model belum ada | Buat model + migrate |
| 13 | `system_numbering_sequences` | **B** | Model belum ada | Buat model + migrate |
| 14 | `system_backup_records` | **B** | Model belum ada | Buat model + migrate |
| 15 | `system_api_keys` | **B** | Model belum ada | Buat model + migrate |
| 16 | `name 'q' is not defined` ×3 | **C** | Bug di views | Tambah `q = request.GET.get('q', '')` |

**Total: 2 rename + 13 tabel baru + 3 bug kode**

---

## URUTAN KERJA (hemat token maksimal)

### ⚡ STEP 0 — Fix Bug Kode (30 detik, 0 token Copilot)

Langsung edit manual, jangan pakai Copilot:

```python
# Di file views yang error (vendors, categories, units),
# tambahkan baris ini di awal fungsi GET:

q = request.GET.get('q', '')
```

Cari file: `masterdata_views.py`, cari fungsi yang handle `/master/vendors/`, `/master/categories/`, `/master/units/`. Di setiap fungsi, pastikan ada baris `q = request.GET.get('q', '')` sebelum `q` dipakai di `.filter()`.

---

### 🔧 STEP 1 — Fix 2 Rename (1 prompt Copilot)

Salin prompt ini ke Copilot:

```
Di models.py saya, ada model ProductBatches dengan db_table='lumra_config_productbatches'
dan model Recipes dengan db_table='production_recipes'.

Tapi views saya memakai nama 'lumra_config_inventory_batches' dan 'production_boms'.

Saya ingin mengubah db_table di models.py menjadi:
- ProductBatches → db_table = 'lumra_config_inventory_batches'
- Recipes → db_table = 'production_boms'

Lalu jalankan makemigrations dan migrate. Jangan ubah nama model class-nya,
hanya db_table saja. Berikan juga perintah SQL ALTER TABLE jika perlu
karena tabel sudah ada di DB dengan nama lama.
```

---

### 🏭 STEP 2 — Buat 4 Tabel Production (1 prompt Copilot)

```
Buat 4 model baru di file models.py (app lumra_config atau app terpisah 
jika production itu app sendiri). Cek dulu apakah production itu app 
terpisah atau bagian dari lumra_config dengan inspeksi struktur folder.

Tabel yang dibutuhkan:

1. production_orders
   - id (BigAutoField PK)
   - order_number (CharField unique, max_length=50) 
   - recipe (FK ke production_recipes/BOM, on_delete=PROTECT)
   - status (CharField max_length=20, choices: draft/planned/in_progress/completed/cancelled)
   - planned_quantity (DecimalField 12,2)
   - actual_quantity (DecimalField 12,2, null blank)
   - planned_start_date (DateField)
   - planned_end_date (DateField, null blank)
   - actual_start_date (DateField, null blank)
   - actual_end_date (DateField, null blank)
   - assigned_to (FK to auth_user, null blank, on_delete=SET_NULL)
   - location (FK ke lumra_config_locations, on_delete=PROTECT)
   - notes (TextField blank)
   - waste_percentage (DecimalField 5,2, null blank, default=0)
   - created_by (FK to auth_user, on_delete=SET_NULL, null blank)
   - created_at, updated_at (DateTimeField auto)
   Meta: db_table = 'production_orders'

2. production_material_consumptions
   - id (BigAutoField PK)
   - production_order (FK ke production_orders, on_delete=CASCADE)
   - variant (FK ke lumra_config_productvariants, on_delete=PROTECT)
   - planned_quantity (DecimalField 12,2)
   - actual_quantity (DecimalField 12,2, null blank)
   - unit (FK ke _units, null blank, on_delete=SET_NULL)
   - unit_cost (DecimalField 12,2, null blank)
   - total_cost (DecimalField 12,2, null blank)
   - variance (DecimalField 12,2, null blank)  # actual - planned
   - notes (TextField blank)
   - created_at (DateTimeField auto)
   - unique_together = (production_order, variant)
   Meta: db_table = 'production_material_consumptions'

3. production_finished_goods_receipts
   - id (BigAutoField PK)
   - production_order (FK ke production_orders, on_delete=CASCADE, unique=True)
   - received_quantity (DecimalField 12,2)
   - received_by (FK to auth_user, null blank, on_delete=SET_NULL)
   - location (FK ke lumra_config_locations, on_delete=PROTECT)
   - variant (FK ke lumra_config_productvariants, null blank, on_delete=SET_NULL)
   - quality_status (CharField max_length=20, choices: pending/accepted/rejected)
   - notes (TextField blank)
   - received_at (DateTimeField null blank)
   - created_at (DateTimeField auto)
   Meta: db_table = 'production_finished_goods_receipts'

4. lumra_config_warehouse_zones
   - id (BigAutoField PK)
   - name (CharField max_length=100)
   - location (FK ke lumra_config_locations, on_delete=CASCADE)
   - zone_type (CharField max_length=20, choices: dry/cold/frozen/hazardous/general)
   - capacity (DecimalField 12,2, null blank)
   - current_usage (DecimalField 12,2, default=0)
   - description (TextField blank)
   - is_active (BooleanField default=True)
   - created_at, updated_at (DateTimeField auto)
   - unique_together = (name, location)
   Meta: db_table = 'lumra_config_warehouse_zones'

Setelah buat model, generate dan apply migration.
```

---

### 💰 STEP 3 — Buat 3 Tabel Accounting (1 prompt Copilot)

```
Buat 3 model accounting baru. Cek dulu apakah ada app 'accounting' 
terpisah atau gabung di lumra_config. Letakkan di app yang sesuai.

1. accounting_accounts
   - id (BigAutoField PK)
   - code (CharField max_length=20, unique)  # ex: 1-1000, 1-1100
   - name (CharField max_length=255)
   - account_type (CharField max_length=20, choices: asset/liability/equity/revenue/expense)
   - parent (FK to self, null blank, on_delete=SET_NULL)
   - description (TextField blank)
   - is_active (BooleanField default=True)
   - is_header (BooleanField default=False)  # True = grup header, bukan akun transaksi
   - normal_balance (CharField max_length=10, choices: debit/credit)
   - currency (CharField max_length=3, default='IDR')
   - created_at, updated_at (DateTimeField auto)
   Meta: db_table = 'accounting_accounts'

2. accounting_journal_entries  
   - id (BigAutoField PK)
   - entry_number (CharField max_length=50, unique)
   - entry_date (DateField)
   - description (TextField)
   - status (CharField max_length=20, choices: draft/posted/cancelled)
   - reference_type (CharField max_length=50, null blank)  # order, payment, retur, etc
   - reference_id (IntegerField null blank)
   - total_debit (DecimalField 15,2, default=0)
   - total_credit (DecimalField 15,2, default=0)
   - posted_by (FK to auth_user, null blank, on_delete=SET_NULL)
   - posted_at (DateTimeField null blank)
   - created_by (FK to auth_user, null blank, on_delete=SET_NULL)
   - created_at, updated_at (DateTimeField auto)
   Meta: db_table = 'accounting_journal_entries'

3. accounting_accounts_receivable
   - id (BigAutoField PK)
   - customer (FK ke lumra_config_customers, on_delete=PROTECT)
   - order (FK ke lumra_config_orders, null blank, on_delete=SET_NULL)
   - invoice_number (CharField max_length=50, null blank)
   - amount (DecimalField 15,2)
   - amount_paid (DecimalField 15,2, default=0)
   - amount_outstanding (DecimalField 15,2)  # amount - amount_paid
   - due_date (DateField)
   - status (CharField max_length=20, choices: open/partially_paid/fully_paid/overdue/write_off)
   - aging_days (IntegerField default=0)  # computed: today - due_date
   - notes (TextField blank)
   - created_at, updated_at (DateTimeField auto)
   Meta: db_table = 'accounting_accounts_receivable'

Generate dan apply migration.
```

---

### ⚙️ STEP 4 — Buat 6 Tabel System Settings (1 prompt Copilot)

```
Buat 6 model system settings baru. Cek apakah ada app 'system' 
terpisah atau gabung di lumra_config.

1. system_user_roles
   - id (BigAutoField PK)
   - user (FK to auth_user, on_delete=CASCADE)
   - role (FK ke 'system_roles', on_delete=PROTECT)  
   - assigned_by (FK to auth_user, null blank, on_delete=SET_NULL)
   - assigned_at (DateTimeField auto)
   - unique_together = (user, role)
   Meta: db_table = 'system_user_roles'

   Note: Jika system_roles belum ada, buat juga:
   system_roles:
   - id, name (unique), description, is_active, created_at, updated_at
   Meta: db_table = 'system_roles'

2. system_role_permissions
   - id (BigAutoField PK)
   - role (FK to system_roles, on_delete=CASCADE)
   - permission (FK to auth_permission, on_delete=CASCADE)
   - unique_together = (role, permission)
   Meta: db_table = 'system_role_permissions'

3. system_email_settings
   - id (BigAutoField PK)
   - smtp_host (CharField max_length=255)
   - smtp_port (IntegerField default=587)
   - smtp_username (CharField max_length=255)
   - smtp_password (CharField max_length=255)
   - use_tls (BooleanField default=True)
   - from_email (CharField max_length=255)
   - from_name (CharField max_length=100)
   - is_active (BooleanField default=False)
   - last_test_at (DateTimeField null blank)
   - last_test_status (CharField max_length=20, null blank)
   - updated_by (FK to auth_user, null blank, on_delete=SET_NULL)
   - created_at, updated_at (DateTimeField auto)
   Meta: db_table = 'system_email_settings'

4. system_numbering_sequences
   - id (BigAutoField PK)
   - document_type (CharField max_length=50, unique)  # INV, SO, PO, RET, PAY, etc
   - prefix (CharField max_length=20, default='')  # INV-
   - format_pattern (CharField max_length=100, default='{prefix}{year}{month}-{seq:04d}')
   - current_sequence (IntegerField default=0)
   - reset_period (CharField max_length=20, choices: never/monthly/yearly)
   - last_generated (DateTimeField null blank)
   - updated_by (FK to auth_user, null blank, on_delete=SET_NULL)
   - created_at, updated_at (DateTimeField auto)
   Meta: db_table = 'system_numbering_sequences'

5. system_backup_records
   - id (BigAutoField PK)
   - filename (CharField max_length=255)
   - file_path (CharField max_length=500)
   - file_size (BigIntegerField default=0)
   - backup_type (CharField max_length=20, choices: manual/auto/scheduled)
   - status (CharField max_length=20, choices: pending/in_progress/completed/failed)
   - notes (TextField blank)
   - created_by (FK to auth_user, null blank, on_delete=SET_NULL)
   - created_at (DateTimeField auto)
   Meta: db_table = 'system_backup_records'

6. system_api_keys
   - id (BigAutoField PK)
   - name (CharField max_length=100)
   - key_hash (CharField max_length=255)  # hashed, bukan plain text
   - key_prefix (CharField max_length=8)  # 4-8 char prefix untuk identifikasi, ex "lumr_xK3m..."
   - is_active (BooleanField default=True)
   - last_used_at (DateTimeField null blank)
   - expires_at (DateTimeField null blank)
   - allowed_ips (TextField blank)  # comma separated
   - permissions (TextField blank)  # JSON list of permissions
   - created_by (FK to auth_user, on_delete=SET_NULL, null blank)
   - created_at, updated_at (DateTimeField auto)
   Meta: db_table = 'system_api_keys'

Generate dan apply migration.
```

---

## 📋 CHEAT SHEET

```
STEP 0 → Manual edit        → 3 bug 'q'                    → 30 detik
STEP 1 → 1 prompt Copilot   → 2 rename db_table             → 2 menit
STEP 2 → 1 prompt Copilot   → 4 tabel production + 1 gudang → 3 menit
STEP 3 → 1 prompt Copilot   → 3 tabel accounting            → 2 menit
STEP 4 → 1 prompt Copilot   → 6 tabel system + 1 roles      → 3 menit
                                                            
TOTAL:   4 prompt Copilot   → 16 tabel + 3 bug fix          → ~12 menit
```

**Urutan ini penting** karena:
- Step 1 harus duluan (rename) karena production BOM reference-nya berubah
- Step 2 sebelum Step 3 karena production_orders tidak depend ke accounting
- Step 4 paling akhir karena paling tidak kritis (settings, bukan core business)

---

## ⚠️ SETELAH SETIAP STEP, CEK:

```bash
python manage.py makemigrations
python manage.py migrate
```

Lalu refresh halaman yang error. Kalau masih error, **cek nama tabel** di error message vs nama di model — mungkin ada typo atau app label yang salah.