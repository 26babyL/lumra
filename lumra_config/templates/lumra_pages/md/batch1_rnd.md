# Catatan Peningkatan per File — Alur R&D → Produksi
**Sistem: CoffeeShop / Lumra ERP**

Dokumen ini dibagi dalam **5 batch** agar setiap batch dapat dikerjakan secara fokus dan mandiri sebelum lanjut ke batch berikutnya.

---

# PANDUAN BACA

Setiap catatan menggunakan kode prioritas:

| Kode | Arti |
|------|------|
| 🔴 **KRITIS** | Alur rusak / data tidak konsisten / dapat menyebabkan bug produksi |
| 🟠 **PENTING** | Fitur belum lengkap, logika bisnis kurang, akan terasa di operasional |
| 🟡 **DISARANKAN** | UX lebih baik, konsistensi antar halaman, efisiensi kerja |
| 🟢 **OPSIONAL** | Nice-to-have, peningkatan jangka panjang |

---

# BATCH 1 — MODUL R&D
**File yang dicakup:** `rnd_list.html` · `rnd_form.html` · `rnd_detail.html`

---

## 1A. `rnd_list.html`

### Masalah & Catatan

**🔴 KRITIS-1: `statusMeta` memanggil ulang `rndListApp()` di dalam getter objek**

Pada blok `init()`, setiap item di array `this.rnds` memiliki getter:
```javascript
get statusMeta() { return rndListApp().statusConfig[this.status] || ... }
get probColor()  { return rndListApp().probColor(this.success_probability); }
get probHex()    { return rndListApp().probHex(this.success_probability); }
```
Masalah: `rndListApp()` dipanggil ulang setiap kali getter diakses, artinya sebuah instance Alpine baru dibuat berulang kali. Ini menyebabkan memory leak dan performa buruk saat jumlah kartu banyak.

**Perbaikan yang benar:** Pindahkan `statusConfig`, `probColor`, dan `probHex` sebagai method/property di level root Alpine, lalu akses via closure atau simpan nilai hasil kalkulasi saat `init()`.

```javascript
// GANTI ini di dalam init() saat mapping:
this.rnds = raw.map(r => {
  const cfg = this.statusConfig[r.status] || this.statusConfig['idea'];
  const pct = Number(r.success_probability || 0);
  return {
    id: r.id,
    name: r.name || r.code,
    status: r.status || 'idea',
    trial_count: '#' + (r.trial_count || 1),
    created_by: r.created_by || '—',
    ingredient_count: r.ingredient_count || 0,
    success_probability: pct,
    estimated_cost: Number(r.estimated_cost || 0),
    statusMeta: cfg,
    probColor: pct >= 70 ? 'text-emerald-600' : pct >= 40 ? 'text-amber-600' : 'text-rose-500',
    probHex:   pct >= 70 ? '#10b981'          : pct >= 40 ? '#f59e0b'         : '#f43f5e',
  };
});
```

---

**🟠 PENTING-2: Tidak ada tombol "Ubah Status" cepat dari list**

Saat ini dari halaman list, satu-satunya aksi adalah "Detail" dan "Edit". Dalam operasional R&D yang sibuk, sangat umum kebutuhan untuk mengubah status langsung dari list (misalnya: approve beberapa formula sekaligus). 

**Tambahkan:** Dropdown atau tombol kecil di hover card untuk ubah status cepat, terutama untuk transisi `review → approved`.

---

**🟠 PENTING-3: Filter tidak mencakup field `created_by`**

`filteredRnDs` hanya memfilter berdasarkan `r.name`. Dalam tim R&D yang terdiri dari beberapa chef/peneliti, filter berdasarkan pembuat formula sangat berguna.

```javascript
// TAMBAHKAN di filteredRnDs getter:
const matchSearch = r.name.toLowerCase().includes(this.search.toLowerCase())
  || r.created_by.toLowerCase().includes(this.search.toLowerCase());
```

---

**🟡 DISARANKAN-4: Stats card tidak reaktif terhadap filter aktif**

`stats` computed property menghitung dari `this.rnds` (seluruh data), bukan dari `this.filteredRnDs`. Sehingga angka di stat card tidak berubah saat filter diaktifkan, membingungkan pengguna.

```javascript
// GANTI referensi di getter stats:
get stats() {
  const src = this.filter === 'all' ? this.rnds : this.filteredRnDs;
  return [
    { label: 'Total Formula',   value: src.length },
    { label: 'In Trial',        value: src.filter(r => r.status === 'in_trial').length },
    { label: 'Menunggu Review', value: src.filter(r => r.status === 'review').length },
    { label: 'Approved',        value: src.filter(r => r.status === 'approved').length },
  ];
},
```

---

**🟡 DISARANKAN-5: Tidak ada indikator visual untuk formula yang sudah di-promote ke BOM**

Formula yang `bom_id !== null` seharusnya ditandai secara visual (misal: badge "Promoted" atau ikon link) agar tim tahu formula mana yang sudah live di produksi dan mana yang belum.

---

**🟢 OPSIONAL-6: Tidak ada sort/urutan kartu**

Semua kartu tampil sesuai urutan dari server. Tambahkan opsi sort: terbaru, tertua, probabilitas tertinggi, biaya terendah.

---

## 1B. `rnd_form.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tombol "Simpan Draft" memanggil `saveRnD('draft')` tapi `draft` bukan status valid**

Di `saveRnD()`, payload mengirimkan `status: statusOverride || 'idea'`. Jika dipanggil dengan `'draft'`, backend akan menerima status `'draft'` yang tidak ada di enum status sistem (`idea`, `in_trial`, `review`, `approved`). Ini akan menyebabkan error atau data tidak konsisten.

**Perbaikan:** Ubah tombol header menjadi:
```javascript
// Header button:
@click="saveRnD('idea')"   // → Simpan Draft = simpan sebagai 'idea'

// Sidebar button sudah benar:
@click="saveRnD('in_trial')"  // → Mulai Trial
@click="saveRnD('idea')"      // → Simpan sebagai Idea
```
Hapus pemanggilan `saveRnD('draft')` sepenuhnya, atau mapping `'draft'` → `'idea'` di awal fungsi.

---

**🔴 KRITIS-2: Duplikasi tombol aksi dengan perilaku berbeda**

Ada 2 set tombol yang melakukan hal berbeda namun membingungkan:
- Header: "Simpan Draft" (`saveRnD('draft')`) dan "Mulai Trial" (`saveRnD('idea')`)  
- Sidebar: "Mulai Trial Sekarang" (`saveRnD('in_trial')`) dan "Simpan sebagai Idea" (`saveRnD('idea')`)

Label "Mulai Trial" di header mengirim status `'idea'`, sedangkan "Mulai Trial Sekarang" di sidebar mengirim `'in_trial'`. Ini kontradiktif dan berpotensi menyesatkan pengguna.

**Perbaikan yang direkomendasikan — sederhanakan menjadi 2 aksi jelas:**
```
[Simpan Idea]   → saveRnD('idea')      // draft, belum mulai trial
[Mulai Trial]   → saveRnD('in_trial')  // langsung masuk antrian trial
```

---

**🟠 PENTING-3: `syncIngredientCost()` tidak otomatis mengisi nama bahan**

Fungsi `syncIngredientCost(index)` sudah benar dalam logika, namun hanya berjalan saat event `@input` di kolom SKU. Jika user mengetik nama bahan dulu baru SKU (atau paste), sinkronisasi tidak terpicu.

**Tambahkan juga** `@blur="syncIngredientCost(index)"` agar sinkronisasi juga terjadi saat user berpindah dari field SKU.

---

**🟠 PENTING-4: Tidak ada validasi bahan minimal sebelum submit ke status `in_trial`**

Saat `saveRnD('in_trial')`, sistem hanya memvalidasi nama formula. Namun formula tanpa bahan apapun bisa disubmit sebagai `in_trial`. Formula tanpa komposisi bahan tidak dapat dijalankan sebagai trial yang bermakna.

**Tambahkan validasi:**
```javascript
const validItems = this.form.ingredients.filter(i => (i.name || i.sku) && i.qty > 0);
if (statusOverride === 'in_trial' && validItems.length === 0) {
  alert('Mohon isi minimal 1 bahan untuk memulai trial.');
  return;
}
```

---

**🟠 PENTING-5: Field `created_by` adalah input teks bebas — rentan salah eja**

Dalam sistem multi-user, `created_by` seharusnya diisi otomatis dari sesi pengguna yang sedang login (Django `request.user`), bukan diketik manual. Nama yang salah eja akan menyebabkan data author tidak konsisten.

**Rekomendasi:** Di template Django, inject user saat ini sebagai default:
```html
<!-- Di view Django, kirim: -->
{{ current_user|json_script:"current-user-data" }}

<!-- Di init(): -->
const uEl = document.getElementById('current-user-data');
if (uEl) this.form.created_by = JSON.parse(uEl.textContent)?.name || '';
```
Jadikan field ini `readonly` atau sembunyikan jika user sudah login.

---

**🟠 PENTING-6: Biaya simulasi tidak termasuk `planned_trials` secara unit**

Sidebar menampilkan "Est. Total Spend = totalMaterialCost × planned_trials", namun ini berasumsi setiap trial menggunakan komposisi yang persis sama. Dalam praktik R&D, komposisi berubah per trial. Tambahkan catatan disclaimer di UI:

```html
<p class="text-[10px] text-slate-500 mt-1">
  * Estimasi kasar, asumsi komposisi sama tiap trial
</p>
```

---

**🟡 DISARANKAN-7: Tidak ada feedback visual saat proses simpan berlangsung**

`saveRnD()` melakukan fetch async tanpa indikator loading. Jika server lambat, user bisa klik tombol berkali-kali → multiple submission.

**Tambahkan state loading:**
```javascript
// Di data:
isSaving: false,

// Di saveRnD():
if (this.isSaving) return;
this.isSaving = true;
// ... fetch ...
.finally(() => { this.isSaving = false; });

// Di template:
:disabled="isSaving"
x-text="isSaving ? 'Menyimpan...' : 'Mulai Trial'"
```

---

**🟡 DISARANKAN-8: `suggestedPrice` muncul meski `totalMaterialCost = 0`**

Jika belum ada bahan yang diisi, sidebar menampilkan "Target Harga Jual: Rp 0" yang tidak informatif dan bisa mengundang kebingungan.

```javascript
// Tambahkan x-show:
<div class="p-3 bg-emerald-900/40..." x-show="totalMaterialCost > 0">
```

---

**🟢 OPSIONAL-9: Tidak ada mode "duplicate dari formula lain"**

Field `based_on` hanya menyimpan teks referensi nama formula. Idealnya ini adalah FK ke formula R&D lain, dan saat dipilih, sistem otomatis mengimpor komposisi bahan dari formula asal sebagai titik awal. Ini akan mempercepat iterasi R&D signifikan.

---

## 1C. `rnd_detail.html`

### Masalah & Catatan

**🔴 KRITIS-1: `addTrial()` hanya melakukan `window.location.href` ke URL hardcoded**

```javascript
addTrial() {
  window.location.href = `/rnd/${this.rnd.id}/trial/new/`;
},
```
URL ini hardcoded tanpa menggunakan `{% url %}` tag Django, sehingga jika URL pattern berubah, link akan putus secara diam-diam tanpa error template.

**Perbaikan:**
```html
<!-- Di template, inject URL base: -->
<div ... x-data="rndDetailApp()" data-trial-url="{% url 'rnd_trial_new' 0 %}">

<!-- Di JS: -->
addTrial() {
  const base = this.$el.dataset.trialUrl;
  window.location.href = base.replace('/0/', `/${this.rnd.id}/`);
},
```

---

**🔴 KRITIS-2: `updateStatus()` dan `promoteToBOM()` menggunakan URL hardcoded**

Sama dengan masalah di atas, URL `/rnd/${this.rnd.id}/status/` dan `/rnd/${this.rnd.id}/promote/` hardcoded. Gunakan `data-*` attribute dari template Django untuk inject URL yang benar.

---

**🟠 PENTING-3: Tidak ada konfirmasi atau pencegahan saat status diturunkan (downgrade)**

Panel "Ubah Status Formula" memungkinkan user mengubah status dari `approved` kembali ke `idea` tanpa konfirmasi apapun. Jika formula sudah di-promote ke BOM, downgrade status R&D-nya seharusnya diblokir atau minimal membutuhkan konfirmasi eksplisit dengan peringatan.

**Tambahkan guard:**
```javascript
updateStatus(newStatus) {
  if (this.rnd.bom_id && newStatus !== 'approved') {
    if (!confirm('Formula ini sudah dipromote ke BOM. Menurunkan status dapat menyebabkan inkonsistensi data. Lanjutkan?')) return;
  }
  // ... lanjut fetch
},
```

---

**🟠 PENTING-4: Panel "Hipotesis vs Aktual Terbaik" muncul tapi kosong jika trial belum punya `is_best`**

`getBestActual(key)` mencari trial dengan `is_best = true`. Jika tidak ada yang ditandai `is_best`, ia fallback ke trial terakhir. Namun jika trial terakhir belum memiliki tasting notes (baru dibuat, belum diisi), semua bar akan kosong dan panel terlihat broken.

**Tambahkan guard:**
```javascript
getBestActual(key) {
  const best = this.rnd.trials.find(t => t.is_best)
    || this.rnd.trials.filter(t => t.tasting && Object.keys(t.tasting).length > 0).slice(-1)[0];
  return best && best.tasting ? best.tasting[key] : undefined;
},
```

---

**🟠 PENTING-5: Tidak ada form input tasting notes langsung di halaman detail**

Saat ini halaman detail hanya menampilkan data trial yang sudah ada. Untuk menambah trial baru atau mengisi tasting notes, user harus navigasi ke halaman lain (`/rnd/{id}/trial/new/`). Dalam praktik lab yang cepat, ini mengganggu flow.

**Rekomendasi:** Tambahkan inline form untuk mengisi tasting notes trial aktif langsung di halaman detail, tanpa berpindah halaman. Minimal sediakan modal/drawer untuk input tasting.

---

**🟠 PENTING-6: Persentase `success_probability` di sidebar tidak bisa diupdate dari detail**

Nilai probabilitas diambil dari `rnd.success_probability` yang bersifat read-only di halaman ini. Setelah setiap trial, tim mungkin ingin memperbarui probabilitas. Saat ini harus kembali ke form edit.

**Tambahkan:** Input kecil atau slider inline di panel probabilitas untuk update langsung, dengan auto-save via PATCH request.

---

**🟡 DISARANKAN-7: Compare panel tidak responsif di mobile**

Panel perbandingan trial menggunakan `min-w-max` dan `flex gap-3` yang akan overflow di layar kecil. Tidak ada mekanisme scroll horizontal yang ditandai dengan jelas.

**Tambahkan:**
```html
<div class="overflow-x-auto -mx-6 px-6">  <!-- negative margin untuk full-bleed scroll -->
  <div class="flex gap-3 min-w-max pb-3">
    <!-- kolom-kolom -->
  </div>
</div>
<p class="text-[10px] text-slate-400 mt-1 text-center">← Geser untuk lihat semua trial →</p>
```

---

**🟡 DISARANKAN-8: Timeline di sidebar tidak menampilkan tanggal trial secara konsisten**

`trial.date` ditampilkan di timeline, namun jika `trial.date` kosong string, tampilan menjadi "undefined · " dengan trailing titik. 

```javascript
// Perbaikan di template:
x-text="[trial.date, trial.note_short].filter(Boolean).join(' · ')"
```

---

**🟢 OPSIONAL-9: Tidak ada fitur export/cetak detail formula**

Sebelum meeting review dengan manajemen, tim R&D akan sangat terbantu oleh tombol "Export ke PDF" atau "Cetak Ringkasan" yang merangkum semua trial dan perbandingannya dalam satu dokumen.

---

**🟢 OPSIONAL-10: Tidak ada history log perubahan status**

Setiap kali status formula berubah (siapa yang mengubah, kapan, dari status apa ke status apa) tidak direkam di UI. Tambahkan audit trail sederhana di bawah timeline alur.

---

## RINGKASAN BATCH 1

| # | File | Kode | Deskripsi Singkat |
|---|------|------|-------------------|
| 1 | rnd_list | 🔴 | `statusMeta` getter memanggil ulang `rndListApp()` setiap render |
| 2 | rnd_list | 🟠 | Filter tidak mencakup field `created_by` |
| 3 | rnd_list | 🟡 | Stats card tidak reaktif terhadap filter aktif |
| 4 | rnd_list | 🟡 | Formula yang sudah promote ke BOM tidak ditandai |
| 5 | rnd_form | 🔴 | `saveRnD('draft')` mengirim status tidak valid ke backend |
| 6 | rnd_form | 🔴 | Dua set tombol dengan label "Mulai Trial" mengirim status berbeda |
| 7 | rnd_form | 🟠 | `syncIngredientCost` tidak terpicu saat `@blur` |
| 8 | rnd_form | 🟠 | Tidak ada validasi minimal bahan saat submit `in_trial` |
| 9 | rnd_form | 🟠 | `created_by` field teks bebas, rentan salah eja |
| 10 | rnd_form | 🟡 | Tidak ada loading state saat menyimpan |
| 11 | rnd_detail | 🔴 | URL `addTrial`, `updateStatus`, `promoteToBOM` hardcoded tanpa `{% url %}` |
| 12 | rnd_detail | 🟠 | Tidak ada konfirmasi saat downgrade status formula yang sudah promoted |
| 13 | rnd_detail | 🟠 | Panel Hipotesis vs Aktual broken jika tasting notes kosong |
| 14 | rnd_detail | 🟠 | Tidak ada form tasting notes inline di halaman detail |
| 15 | rnd_detail | 🟠 | Probabilitas tidak bisa diupdate dari halaman detail |
| 16 | rnd_detail | 🟡 | Compare panel overflow di mobile tanpa panduan scroll |
