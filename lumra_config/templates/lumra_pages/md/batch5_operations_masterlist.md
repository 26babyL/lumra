# BATCH 5 — MODUL PRODUCTION OPERATIONS + MASTER CHECKLIST
**File yang dicakup:** `material_consumption.html` · `production_waste.html` · `finished_goods_receipt.html` · `production_costing.html`
**Plus:** Master checklist prioritas seluruh sistem

---

## 5A. `material_consumption.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tidak ada form untuk INPUT konsumsi baru — halaman ini hanya list/read-only**

```html
<table class="min-w-full text-sm">
  <thead>...</thead>
  <tbody>
    <template x-for="item in filteredItems">...</template>
  </tbody>
</table>
```
Halaman ini hanya menampilkan daftar konsumsi yang sudah ada. Tidak ada form, tombol, atau modal untuk mencatat konsumsi bahan baru. Namun di `production_order_detail.html`, setelah produksi selesai ada link "Catat Pemakaian Bahan" yang mengarah ke halaman ini.

Artinya user diarahkan ke halaman kosong yang tidak bisa diisi apapun. **Alur produksi tersumbat di sini.**

**Perbaikan wajib — tambahkan form input konsumsi:**
Minimal tambahkan tombol/modal untuk mencatat konsumsi per PO:
```html
<!-- Tombol di header: -->
<button @click="openForm()" class="bg-slate-800 text-white px-4 py-2 rounded-xl text-sm font-semibold">
  + Catat Konsumsi
</button>

<!-- Modal form: -->
<div x-show="showForm" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
  <div class="bg-white rounded-2xl p-6 w-full max-w-lg">
    <h3 class="font-bold text-slate-800 mb-4">Catat Pemakaian Bahan</h3>
    <div class="space-y-3">
      <select x-model="newConsumption.po_id">
        <option value="">Pilih PO...</option>
        <template x-for="po in activePOs" :key="po.id">
          <option :value="po.id" x-text="po.code + ' — ' + po.product"></option>
        </template>
      </select>
      <!-- ... dst untuk setiap bahan dari BOM -->
    </div>
    <button @click="saveConsumption()">Simpan</button>
  </div>
</div>
```

---

**🔴 KRITIS-2: Tidak ada validasi apakah PO sudah berstatus `completed` sebelum konsumsi dicatat**

Konsumsi material seharusnya hanya bisa dicatat untuk PO yang sudah selesai (status `completed`). Tidak ada guard ini di UI maupun (berpotensi) di backend.

**Tambahkan filter di dropdown PO:**
```javascript
get completedPOs() {
  return this.allPOs.filter(po => po.status === 'completed' && !po.consumption_recorded);
},
```

---

**🔴 KRITIS-3: Tidak ada indikator apakah konsumsi untuk suatu PO sudah dicatat atau belum**

List konsumsi tidak dikelompokkan per PO dan tidak ada flag "sudah dicatat". Tim tidak bisa tahu PO mana yang masih outstanding (sudah selesai produksi tapi belum catat konsumsi).

**Tambahkan kolom status atau filter:**
```html
<select x-model="statusFilter" @change="applyFilter()">
  <option value="">Semua PO</option>
  <option value="pending_consumption">Belum dicatat</option>
  <option value="recorded">Sudah dicatat</option>
</select>
```

---

**🟠 PENTING-4: Filter `poFilter` menggunakan exact match string tapi data `po_code` mungkin tidak konsisten**

```javascript
const matchesPO = !this.poFilter || item.po_code === this.poFilter;
```
Jika `po_code` di satu record adalah `"PO-2024-001"` dan di record lain `"po-2024-001"` (lowercase), filter tidak akan bekerja dengan benar. 

**Perbaikan:**
```javascript
const matchesPO = !this.poFilter || 
  (item.po_code || '').toLowerCase() === this.poFilter.toLowerCase();
```

---

**🟠 PENTING-5: Tidak ada perbandingan antara konsumsi aktual vs konsumsi standar BOM**

Ini adalah fungsi terpenting dari material consumption — membandingkan berapa yang seharusnya dipakai (dari BOM × qty produksi) vs berapa yang benar-benar dipakai (aktual). Tanpa perbandingan ini, tidak ada analisis efisiensi material.

**Tambahkan kolom:**

| Material | Standar BOM | Aktual Terpakai | Selisih | Status |
|----------|-------------|-----------------|---------|--------|
| Espresso | 200g | 210g | +10g | ⚠️ Lebih |
| Susu | 1500ml | 1480ml | -20ml | ✅ Efisien |

---

**🟡 DISARANKAN-6: Stats "Filtered Qty" menjumlahkan qty dari unit berbeda**

```javascript
get totalQuantity() {
  return this.filteredItems.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
},
```
Jika ada bahan dalam gram dan ml, total qty tidak bermakna karena menjumlahkan satuan yang berbeda. Stats ini sebaiknya dihapus atau diganti dengan "Total Item Tercatat".

---

## 5B. `production_waste.html`

### Masalah & Catatan

**🔴 KRITIS-1: Sama dengan `material_consumption.html` — tidak ada form input waste baru**

Halaman hanya menampilkan list waste yang sudah ada. Tidak ada cara untuk mencatat waste baru dari halaman ini. Padahal `production_order_detail.html` setelah produksi selesai tidak ada link ke waste recording.

**Perbaikan:** Tambahkan form/modal input waste dengan field:
- PO referensi (dropdown PO completed)
- Jenis waste (`waste_type`): Scrap / Spoilage / Rework / Other
- Material yang terbuang (SKU + nama)
- Kuantitas dan satuan
- Catatan penyebab

---

**🔴 KRITIS-2: Tidak ada kalkulasi nilai kerugian dari waste**

Waste dicatat dalam qty tapi tidak ada konversi ke nilai rupiah. Management tidak bisa melihat berapa rupiah kerugian dari waste per periode.

**Tambahkan field dan computed:**
```javascript
// Di init() saat mapping:
waste_value: Number(item.quantity || 0) * Number(item.unit_price || 0),

// Stats card baru:
get totalWasteValue() {
  return this.filteredItems.reduce((sum, i) => sum + (i.waste_value || 0), 0);
},
```
```html
<div class="glass-card px-4 py-3">
  <p class="text-xs uppercase tracking-wide text-slate-400">Nilai Kerugian</p>
  <p class="text-2xl font-bold text-rose-600 mt-1" x-text="formatCurrency(totalWasteValue)"></p>
</div>
```

---

**🟠 PENTING-3: `waste_type` filter menggunakan data dinamis tapi tidak ada standarisasi tipe**

```javascript
this.typeOptions = [...new Set(this.allItems.map(item => item.waste_type).filter(Boolean))];
```
Tipe waste diambil dari data yang sudah ada. Jika user satu menulis "Scrap" dan user lain menulis "scrap" atau "SCRAP", ketiganya menjadi opsi filter berbeda. Tidak ada enum standar.

**Perbaikan:** Hardcode tipe waste yang valid:
```javascript
wasteTypes: ['Scrap', 'Spoilage', 'Rework', 'Overproduction', 'Lainnya'],
```
Dan gunakan ini sebagai opsi di form input, bukan dari data dinamis.

---

**🟠 PENTING-4: Tidak ada grouping waste per PO untuk melihat total waste per order**

List menampilkan setiap record waste satu per satu. Tidak ada cara untuk melihat: "PO-2024-001 total waste berapa?"

**Tambahkan toggle tampilan grouped:**
```javascript
get groupedByPO() {
  const groups = {};
  this.filteredItems.forEach(item => {
    if (!groups[item.po_code]) groups[item.po_code] = { po_code: item.po_code, items: [], totalQty: 0 };
    groups[item.po_code].items.push(item);
    groups[item.po_code].totalQty += Number(item.quantity || 0);
  });
  return Object.values(groups);
},
```

---

**🟡 DISARANKAN-5: Tidak ada trend analisis waste per periode**

Tidak ada grafik atau visualisasi yang menunjukkan tren waste dari waktu ke waktu. Ini penting untuk monitoring apakah waste meningkat atau menurun setelah perbaikan proses.

---

## 5C. `finished_goods_receipt.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tidak ada form input penerimaan barang jadi baru**

Sama dengan masalah di modul sebelumnya — halaman hanya menampilkan list receipt yang sudah ada. Tidak ada cara untuk mencatat penerimaan barang jadi baru.

Alur yang benar seharusnya:
1. Produksi selesai → operator klik "Selesaikan" di `production_order_detail`
2. Sistem otomatis membuat draft Finished Goods Receipt
3. Staf gudang membuka halaman ini, verifikasi kuantitas, dan konfirmasi penerimaan

Tanpa form ini, barang jadi tidak pernah "resmi" masuk ke stok.

---

**🔴 KRITIS-2: Tidak ada validasi bahwa PO yang di-receipt sudah berstatus `completed`**

Sama seperti material consumption, receipt seharusnya hanya bisa dicatat untuk PO yang sudah selesai. Tidak ada guard ini.

---

**🟠 PENTING-3: Kolom "Qty" di tabel tidak menampilkan satuan (UOM)**

```html
<td class="px-6 py-4 text-right font-semibold text-slate-800" x-text="formatQty(item.quantity)"></td>
```
Angka kuantitas ditampilkan tanpa satuan. Tidak jelas apakah 100 itu cup, kg, atau pcs.

**Perbaikan:**
```html
<td class="px-6 py-4 text-right font-semibold text-slate-800">
  <span x-text="formatQty(item.quantity)"></span>
  <span class="text-slate-400 text-xs ml-1" x-text="item.uom || ''"></span>
</td>
```

---

**🟠 PENTING-4: Tidak ada perbandingan antara qty yang diproduksi vs qty yang diterima**

PO target 100 cup, produksi melaporkan 98 cup, tapi receipt mencatat 95 cup. Selisih 3 cup ini tidak terlihat dimanapun. Ini adalah **variance penerimaan** yang penting untuk inventory accuracy.

**Tambahkan kolom:**
```html
<th>PO Target</th>
<th>Produced</th>
<th>Received</th>
<th>Variance</th>
```

---

**🟡 DISARANKAN-5: Stats "Locations" hanya menghitung unique location dari filtered items**

```javascript
get locationCount() {
  return new Set(this.filteredItems.map(item => item.location).filter(Boolean)).size;
},
```
Stats ini kurang bermakna sebagai KPI. Lebih berguna menampilkan total nilai barang yang diterima (qty × harga) atau jumlah PO yang sudah di-receipt hari ini.

---

**🟡 DISARANKAN-6: Search menggunakan `po_code`, `product`, `sku` tapi tidak `location`**

Tim gudang sering ingin filter: "barang apa saja yang masuk ke lokasi RAK-A3?" Search saat ini tidak mendukung ini.

---

## 5D. `production_costing.html`

### Masalah & Catatan

**🔴 KRITIS-1: Halaman ini hanya menampilkan snapshot order produksi — bukan analisis costing sesungguhnya**

```html
<h1>Production Costing</h1>
<p>Ringkasan order produksi berbasis data aktual yang tersedia saat ini.</p>
<!-- Note card: -->
<p>Halaman ini ringan dan mengambil order dari database. Cost detail akan mengikuti data costing yang nanti tersedia.</p>
```
Halaman "Production Costing" tidak menampilkan biaya apapun. Tidak ada:
- Biaya bahan aktual (dari material consumption)
- Biaya tenaga kerja
- Biaya overhead
- HPP aktual vs HPP standar BOM
- Variance analisis

Ini adalah **halaman placeholder** yang dinamai Costing tapi tidak melakukan costing. Sangat menyesatkan.

**Perbaikan minimum:** Ubah nama halaman menjadi "Production Overview" sampai data costing tersedia, atau implementasikan minimal:
```javascript
// Setelah join dengan data material_consumption:
actualMaterialCost: Number(order.actual_material_cost || 0),
standardMaterialCost: Number(order.standard_material_cost || 0), // dari BOM × qty
variance: actualMaterialCost - standardMaterialCost,
variancePct: standardMaterialCost > 0 
  ? ((actualMaterialCost - standardMaterialCost) / standardMaterialCost * 100).toFixed(1) 
  : 0,
```

---

**🟠 PENTING-2: `completion_pct` bisa melebihi 100% jika ada overproduction**

```javascript
const completionPct = targetQty > 0 ? Math.round((producedQty / targetQty) * 100) : 0;
```
Jika produksi menghasilkan lebih dari target (misalnya target 100, hasil 105), `completionPct = 105`. Tampilan tabel tidak membatasi ini dan akan menampilkan "105%" yang terlihat aneh.

**Perbaikan:**
```javascript
const completionPct = targetQty > 0 
  ? Math.round((producedQty / targetQty) * 100) 
  : 0;
// Tambahkan flag overproduction:
const isOverproduced = producedQty > targetQty;
```

---

**🟠 PENTING-3: Stats "Completion Rate" menggunakan total qty semua order — bukan rata-rata per order**

```javascript
get completionRate() {
  if (!this.totalTargetQty) return '0%';
  return `${Math.round((this.totalProducedQty / this.totalTargetQty) * 100)}%`;
},
```
Ini mengagregasi semua qty. Jika ada 1 PO besar dengan 1000 unit selesai dan 5 PO kecil masing-masing 10 unit tidak selesai, completion rate akan terlihat tinggi padahal banyak PO yang failed.

**Lebih bermakna:** Hitung persentase PO yang completed:
```javascript
get completedOrderRate() {
  if (!this.filteredItems.length) return '0%';
  const completed = this.filteredItems.filter(i => i.status === 'completed').length;
  return `${Math.round((completed / this.filteredItems.length) * 100)}%`;
},
```

---

**🟡 DISARANKAN-4: Tidak ada kolom tanggal di tabel**

Tabel tidak menampilkan `scheduled_date` atau `completed_at`. Tidak bisa melihat distribusi order berdasarkan waktu tanpa klik detail satu per satu.

---

**🟡 DISARANKAN-5: Tidak ada export ke Excel/CSV**

Data costing ini sangat sering dibutuhkan untuk laporan keuangan dan manajemen. Tambahkan tombol export:
```javascript
exportCSV() {
  const headers = ['Order', 'Product', 'Status', 'Target', 'Produced', 'Completion %'];
  const rows = this.filteredItems.map(i => [i.code, i.product, i.status, i.target_qty, i.produced_qty, i.completion_pct + '%']);
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'production_costing.csv'; a.click();
},
```

---

## RINGKASAN BATCH 5

| # | File | Kode | Deskripsi Singkat |
|---|------|------|-------------------|
| 1 | material_consumption | 🔴 | Tidak ada form input konsumsi baru — alur produksi tersumbat |
| 2 | material_consumption | 🔴 | Tidak ada validasi PO harus `completed` sebelum catat konsumsi |
| 3 | material_consumption | 🔴 | Tidak ada flag PO mana yang sudah/belum dicatat konsumsinya |
| 4 | material_consumption | 🟠 | Tidak ada perbandingan konsumsi aktual vs standar BOM |
| 5 | material_consumption | 🟡 | Stats qty menjumlahkan satuan berbeda — tidak bermakna |
| 6 | production_waste | 🔴 | Tidak ada form input waste baru |
| 7 | production_waste | 🔴 | Tidak ada kalkulasi nilai kerugian (qty × harga) |
| 8 | production_waste | 🟠 | `waste_type` tidak distandardisasi — filter jadi inkonsisten |
| 9 | production_waste | 🟠 | Tidak ada grouping waste per PO |
| 10 | finished_goods_receipt | 🔴 | Tidak ada form input receipt baru — stok tidak pernah bertambah |
| 11 | finished_goods_receipt | 🔴 | Tidak ada validasi PO harus `completed` |
| 12 | finished_goods_receipt | 🟠 | Kolom qty tidak menampilkan satuan |
| 13 | finished_goods_receipt | 🟠 | Tidak ada perbandingan produced qty vs received qty (variance) |
| 14 | production_costing | 🔴 | Halaman tidak menampilkan biaya apapun — bukan costing sesungguhnya |
| 15 | production_costing | 🟠 | `completion_pct` bisa >100% tanpa flag overproduction |
| 16 | production_costing | 🟠 | `completionRate` stats menyesatkan — agregat qty bukan agregat PO |
| 17 | production_costing | 🟡 | Tidak ada kolom tanggal di tabel |
| 18 | production_costing | 🟡 | Tidak ada export CSV/Excel |

---

---

# MASTER CHECKLIST SELURUH SISTEM

## 🔴 KRITIS — Wajib diperbaiki sebelum go-live

### Masalah Alur Bisnis (Data Tidak Tersimpan / Alur Tersumbat)

| # | File | Masalah |
|---|------|---------|
| 1 | `production_order_detail` | Semua aksi start/pause/complete/updateQty **tidak sync ke server** |
| 2 | `material_consumption` | **Tidak ada form input** — alur post-produksi tersumbat |
| 3 | `production_waste` | **Tidak ada form input** — waste tidak bisa dicatat |
| 4 | `finished_goods_receipt` | **Tidak ada form input** — barang jadi tidak pernah masuk stok |
| 5 | `production_costing` | Halaman tidak menampilkan data biaya apapun |

### Masalah Teknis (Bug / Error di Browser)

| # | File | Masalah |
|---|------|---------|
| 6 | `recipe_list` | `<style>` sebelum `{% extends %}` — TemplateSyntaxError Django |
| 7 | `recipe_form` | `<style>` sebelum `{% extends %}` — TemplateSyntaxError Django |
| 8 | `recipe_list` | Sintaks `class="style=..."` rusak — render browser kacau |
| 9 | `recipe_form` | Sintaks `class="style=..."` rusak — render browser kacau |
| 10 | `rnd_list` | `statusMeta` getter memanggil `rndListApp()` berulang — memory leak |
| 11 | `rnd_form` | `saveRnD('draft')` mengirim status tidak valid ke backend |
| 12 | `rnd_detail` | URL `addTrial`, `updateStatus`, `promoteToBOM` hardcoded |
| 13 | `bom_form` | Tidak ada mode Edit — selalu buat BOM baru |
| 14 | `bom_detail` | Tombol "Edit Resep" dan "Duplikat" tidak berfungsi |
| 15 | `po_list` | Progress bar crash `NaN%` jika `target_qty = 0` |
| 16 | `po_form` | Kode PO pakai `Math.random()` — bisa duplikat |
| 17 | `po_form` | Double submission mungkin terjadi — tidak ada loading state |
| 18 | `po_detail` | Progress circle crash jika `target_qty = 0` |
| 19 | `scheduling` | `scheduled_date` tidak dinormalisasi — kalender bisa kosong semua |
| 20 | `recipe_detail` | `{% url 'recipe_form' recipe.id %}` — `recipe.id` mungkin tidak ada di context |

---

## 🟠 PENTING — Selesaikan dalam sprint pertama setelah go-live

| # | File | Masalah |
|---|------|---------|
| 21 | `rnd_form` | Dua tombol "Mulai Trial" mengirim status berbeda |
| 22 | `rnd_form` | `created_by` seharusnya dari session user, bukan input manual |
| 23 | `rnd_detail` | Tidak ada form inline tasting notes |
| 24 | `rnd_detail` | Tidak ada konfirmasi saat downgrade status formula yang sudah promoted |
| 25 | `bom_form` | `totalMaterialCost` selalu 0 — tidak ada auto-sync harga dari SKU |
| 26 | `bom_form` | `yield_qty` dan `yield_uom` tidak dikirim di payload |
| 27 | `bom_form` | Bahan dengan SKU tidak valid dibuang diam-diam |
| 28 | `bom_detail` | Riwayat versi adalah HTML statis |
| 29 | `bom_detail` | Input "Biaya Tenaga" tidak terhubung ke Alpine state |
| 30 | `recipe_form` | Tidak ada input `preparation_time`, `yield_quantity`, `yield_unit` |
| 31 | `recipe_form` | Tidak ada input `instructions` (langkah pembuatan) |
| 32 | `recipe_form` | `validateField()` tidak terdefinisi — error saat blur |
| 33 | `po_list` | Tidak ada filter `on_hold` |
| 34 | `po_list` | Tidak ada indikator PO overdue |
| 35 | `po_form` | Tidak ada field `assigned_to` untuk operator |
| 36 | `po_detail` | Tidak ada daftar bahan BOM yang harus digunakan |
| 37 | `material_consumption` | Tidak ada perbandingan aktual vs standar BOM |
| 38 | `production_waste` | `waste_type` tidak distandardisasi |
| 39 | `production_waste` | Tidak ada kalkulasi nilai kerugian |
| 40 | `finished_goods_receipt` | Tidak ada perbandingan produced vs received qty |

---

## 🟡 DISARANKAN — Backlog sprint berikutnya

| # | File | Masalah |
|---|------|---------|
| 41 | `rnd_list` | Stats card tidak reaktif terhadap filter |
| 42 | `rnd_list` | Tidak ada penanda formula yang sudah promoted |
| 43 | `rnd_form` | Tidak ada loading state saat simpan |
| 44 | `rnd_detail` | Compare panel overflow di mobile |
| 45 | `bom_form` | Margin 60% hardcoded |
| 46 | `bom_detail` | Tidak ada tautan ke formula RnD asal |
| 47 | `recipe_list` | Bahasa campuran English/Indonesia |
| 48 | `recipe_detail` | Search tidak ada debounce |
| 49 | `po_list` | Tidak ada pagination |
| 50 | `po_form` | `estimatedTime` pakai rumus tidak berdasar data |
| 51 | `po_detail` | Tidak ada input qty manual (harus klik +/- banyak kali) |
| 52 | `scheduling` | Tidak ada penanda hari ini di kalender |
| 53 | `scheduling` | Stats card menghitung semua bulan bukan bulan aktif |
| 54 | `production_costing` | Tidak ada export CSV/Excel |

---

## URUTAN PENGERJAAN YANG DISARANKAN

```
MINGGU 1 — Perbaikan Fatal (Sistem tidak bisa dipakai tanpa ini)
├── Fix template Django: recipe_list, recipe_form (extends + style)
├── Fix production_order_detail: semua aksi sync ke server
├── Tambah form input: material_consumption, production_waste, finished_goods_receipt
└── Fix URL hardcoded di rnd_detail

MINGGU 2 — Perbaikan Alur Bisnis
├── Fix bom_form: mode edit + auto-sync harga + yield payload
├── Fix rnd_form: status 'draft' + tombol aksi konsisten
├── Fix po_form: kode PO dari server + loading state
└── Fix po_list: mapping data + progress bar NaN guard

MINGGU 3 — Peningkatan Fungsionalitas
├── Tambah field recipe_form: instructions + preparation_time + yield
├── Tambah assigned_to di po_form + po_detail
├── Standarisasi waste_type di production_waste
├── Tambah perbandingan aktual vs BOM di material_consumption
└── Implementasi production_costing yang sesungguhnya

MINGGU 4 — Polish & UX
├── Tambah overdue indicator di po_list
├── Tambah inline tasting form di rnd_detail
├── Normalisasi bahasa ke Bahasa Indonesia
├── Tambah pagination di list panjang
└── Tambah export CSV di production_costing
```

---

*Dokumen ini disusun berdasarkan analisis struktural 17 file template Django/Alpine.js.*
*Total masalah ditemukan: 20 Kritis · 20 Penting · 14 Disarankan = **54 catatan**.*
