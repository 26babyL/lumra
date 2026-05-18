# BATCH 2 — MODUL BOM (Bill of Materials)
**File yang dicakup:** `bom_list.html` · `bom_form.html` · `bom_detail.html`

> Modul BOM adalah jembatan antara R&D dan Produksi. BOM yang buruk = produksi yang kacau.
> Semua masalah di sini berdampak langsung ke akurasi SPK dan HPP.

---

## 2A. `bom_list.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tidak ada indikator apakah BOM berasal dari R&D atau dibuat manual**

Saat ini semua BOM tampil sama di list tanpa membedakan asal-usulnya. BOM yang dipromote dari R&D (`rnd_id`) seharusnya ditandai berbeda dari BOM yang dibuat manual, karena memiliki konteks trial dan hipotesis yang bisa dirujuk.

**Tambahkan:** Badge atau ikon kecil "dari RnD" dengan tautan ke detail formula R&D asal.

---

**🔴 KRITIS-2: Filter hanya `active` dan `draft` — tidak ada filter `versi terbaru`**

Satu produk bisa memiliki banyak versi BOM (v1.0, v1.1, v1.2). Di list saat ini, semua versi bisa tampil bersamaan jika backend mengembalikan semua. Tidak ada penanda mana yang `is_active` per produk (hanya ada satu BOM aktif per SKU pada satu waktu).

**Tambahkan filter:** "Hanya versi aktif" (satu per SKU) vs "Semua versi termasuk arsip".

---

**🟠 PENTING-3: Hover action "Edit" pada list card tidak mencegah klik card**

```html
<button class="..." @click.stop="window.location.href=...">Edit</button>
```
Tombol "Edit" di hover overlay sudah menggunakan `@click.stop`? Cek ulang — di versi file yang dianalisis, tombol Edit pada hover card **tidak memiliki** `@click.stop`, sehingga klik Edit akan sekaligus memicu navigasi ke halaman detail (karena event bubble ke wrapper `@click`).

**Perbaikan:**
```html
<button @click.stop="window.location.href='{% url 'bom_form' %}?edit=' + bom.id"
        class="px-3 py-1.5 bg-slate-800 text-white ...">Edit</button>
```

---

**🟠 PENTING-4: Tidak ada fitur bulk action**

Dalam operasi produksi aktif, manager perlu bisa mengaktifkan/menonaktifkan beberapa BOM sekaligus (misalnya saat pergantian musim menu). Tidak ada checkbox atau mode multi-select.

---

**🟡 DISARANKAN-5: Kartu tidak menampilkan tanggal terakhir diperbarui**

Informasi `updated_at` penting untuk mengetahui BOM mana yang sudah lama tidak direvisi dan mungkin sudah tidak relevan dengan harga bahan terkini.

---

**🟡 DISARANKAN-6: Search tidak mencakup nama bahan di dalam BOM**

`filteredBOMs` hanya mencari di `b.name` dan `b.sku`. Tim produksi sering mencari "BOM mana yang menggunakan bahan X?" — ini tidak bisa dilakukan dari list saat ini.

---

## 2B. `bom_form.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tidak ada mode Edit — form selalu membuat BOM baru**

`bom_form.html` tidak memiliki mekanisme edit mode (tidak ada `isEdit` flag, tidak ada prefill dari data existing, tidak ada `rnd_data` atau `bom_data` JSON). Artinya setiap kali user ingin merevisi BOM, form ini selalu membuat entry baru dari nol, bukan mengupdate yang ada.

**Tambahkan:**
```javascript
// Tambahkan ke data:
isEdit: false,
editId: null,

// Di init():
const bEl = document.getElementById('bom-data');
if (bEl && bEl.textContent) {
  try {
    const b = JSON.parse(bEl.textContent);
    if (b && b.id) {
      this.isEdit = true;
      this.editId = b.id;
      this.form.name = b.name || '';
      this.form.finished_sku = b.finished_sku || '';
      // ... dst
    }
  } catch(e) {}
}

// Di saveBOM(), ubah method dan URL:
method: this.isEdit ? 'PUT' : 'POST',
// URL: isEdit ? `/bom/${this.editId}/` : '{{ submit_url }}'
```

---

**🔴 KRITIS-2: `totalMaterialCost` selalu 0 karena `estimated_cost` tidak pernah terisi otomatis**

```javascript
get totalMaterialCost() {
  return this.form.ingredients.reduce((acc, curr) => acc + (curr.estimated_cost || 0), 0);
}
```
Kolom "Est. Harga" di tabel bahan tidak memiliki mekanisme auto-fill berdasarkan SKU yang diketik. Tidak ada `@input` atau `syncIngredientCost()` seperti yang ada di `rnd_form.html`. Akibatnya sidebar "Ringkasan Biaya" selalu menampilkan Rp 0 meski bahan sudah diisi.

**Perbaikan:** Tambahkan fungsi sync harga seperti di rnd_form:
```javascript
syncIngredientCost(index) {
  const ing = this.form.ingredients[index];
  if (!ing || !ing.sku) return;
  const found = this.variants.find(v => 
    String(v.sku).toLowerCase() === String(ing.sku).toLowerCase()
  );
  if (found && !ing.estimated_cost) {
    ing.estimated_cost = Number(found.price_buy || 0);
  }
},
```
Dan tambahkan `@input="syncIngredientCost(index)"` di kolom SKU pada tabel bahan.

---

**🔴 KRITIS-3: Tidak ada mekanisme versioning saat edit BOM**

BOM di sistem ini memiliki field `version`. Namun form tidak memiliki logika untuk auto-increment version saat BOM yang sudah aktif diubah. Tanpa versioning yang benar, riwayat BOM hilang dan tidak bisa dilacak.

**Rekomendasi alur yang benar:**
- Edit minor (typo, harga) → update in-place, version tetap
- Edit major (ubah komposisi bahan) → buat versi baru, version increment, versi lama diarsip

Tambahkan pilihan ini saat mode edit:
```html
<div x-show="isEdit" class="bg-amber-50 border border-amber-200 rounded-xl p-3">
  <p class="text-xs font-bold text-amber-700 mb-2">Tipe Perubahan</p>
  <label class="flex items-center gap-2 text-xs text-amber-700 cursor-pointer">
    <input type="radio" x-model="changeType" value="minor"> Koreksi minor (tetap versi {{ bom.version }})
  </label>
  <label class="flex items-center gap-2 text-xs text-amber-700 cursor-pointer mt-1">
    <input type="radio" x-model="changeType" value="major"> Revisi komposisi (buat v{{ bom.version + 0.1 }})
  </label>
</div>
```

---

**🟠 PENTING-4: Validasi SKU bahan hanya terbatas pada SKU yang ada di variants**

```javascript
const items = this.form.ingredients
  .filter(i => i && i.sku && i.qty)
  .map(i => {
    const comp = variantBySku.get(String(i.sku).toLowerCase());
    if (!comp) return null;  // ← dibuang jika tidak ada di variants
    ...
  })
  .filter(Boolean);
```

Bahan yang SKU-nya tidak ditemukan di variants langsung dibuang tanpa pemberitahuan ke user. Akibatnya user bisa mengisi 5 bahan, tapi hanya 3 yang masuk ke payload tanpa ada peringatan.

**Perbaikan:**
```javascript
const invalidItems = this.form.ingredients
  .filter(i => i.sku && i.qty)
  .filter(i => !variantBySku.has(String(i.sku).toLowerCase()));

if (invalidItems.length > 0) {
  alert(`SKU berikut tidak ditemukan di sistem: ${invalidItems.map(i => i.sku).join(', ')}`);
  return;
}
```

---

**🟠 PENTING-5: `yield_qty` dan `yield_uom` diisi di form tapi tidak dikirim di payload**

Form memiliki input `form.yield_qty` dan `form.yield_uom`, namun di fungsi `saveBOM()` kedua field ini tidak ada dalam object `payload` yang dikirim ke server.

**Tambahkan ke payload:**
```javascript
const payload = {
  ...
  yield_qty: this.form.yield_qty || 1,
  yield_uom: this.form.yield_uom || 'cup',
};
```

---

**🟠 PENTING-6: Tidak ada navigasi kembali ke halaman asal jika user datang dari R&D promote**

Saat BOM dibuat via "Promote ke BOM" dari R&D, setelah form selesai user diarahkan ke `bom_list`. Lebih baik arahkan ke detail BOM yang baru dibuat, atau kembali ke detail formula R&D dengan status terupdate.

---

**🟡 DISARANKAN-7: `suggestedPrice` mengasumsikan margin 60% hardcoded**

```javascript
get suggestedPrice() {
  return this.costPerUnit / 0.4; // 60% margin
}
```
Persentase margin ini hardcoded. Seharusnya bisa dikonfigurasi oleh user, karena margin berbeda untuk kategori produk berbeda (minuman vs makanan vs raw material).

---

## 2C. `bom_detail.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tombol "Edit Resep" tidak mengarah ke URL yang benar**

```html
<button class="...">Edit Resep</button>
```
Tombol ini tidak memiliki `@click` handler maupun `href`. Tombolnya ada tapi tidak berfungsi.

**Perbaikan:**
```html
<a href="{% url 'bom_form' %}?edit={{ bom_id }}" 
   class="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm font-bold shadow hover:bg-slate-700">
  Edit Resep
</a>
```

---

**🔴 KRITIS-2: Tombol "Duplikat" tidak memiliki handler**

Sama seperti "Edit Resep" — tombol "Duplikat" ada di header tapi tidak memiliki `@click` handler apapun. Fitur ini tidak berfungsi.

---

**🟠 PENTING-3: `costCategories` computed property menggunakan data hardcoded**

```javascript
get costCategories() {
  const total = Number(this.bom.total_cost || 0);
  const palette = ['#0f766e', '#2563eb', '#d97706', '#7c3aed', '#dc2626'];
  if (!total) return [];
  return this.bom.ingredients
    .slice()
    .sort((a, b) => b.total - a.total)
    .slice(0, 5)
    ...
}
```
Ini sudah lebih baik dari versi sebelumnya (menggunakan data aktual bahan, bukan nilai hardcoded). Namun batas 5 bahan teratas saja ditampilkan. Jika BOM memiliki 10+ bahan, sisa bahan tidak terwakili di chart dan total persentase tidak mencapai 100%.

**Perbaikan:** Tampilkan semua bahan, atau tambahkan kategori "Lainnya" untuk sisa bahan:
```javascript
const topFive = sorted.slice(0, 5);
const otherAmount = sorted.slice(5).reduce((s, i) => s + i.amount, 0);
if (otherAmount > 0) {
  topFive.push({ name: 'Lainnya', amount: otherAmount, color: '#94a3b8', 
                 pct: Math.round((otherAmount / total) * 100) });
}
return topFive;
```

---

**🟠 PENTING-4: Simulasi qty produksi tidak memiliki batas bawah validasi**

`productionQty` dapat diset ke 0 atau negatif (field `type="number"` tanpa `min` attribute di HTML). Nilai 0 menyebabkan `requiredQty = 0` untuk semua bahan, yang tidak bermakna.

**Tambahkan di template:**
```html
<input type="number" min="1" step="any" x-model.number="productionQty" ...>
```
Dan tambahkan watcher:
```javascript
$watch('productionQty', v => { if (v < 1) this.productionQty = 1; })
```

---

**🟠 PENTING-5: Riwayat Versi di sidebar adalah data statis (hardcoded)**

```html
<div class="...">
  <p class="text-sm font-bold text-slate-800">v1.2 (Aktif)</p>
  <p class="text-[10px] text-slate-500">25 Okt 2023 • oleh Admin</p>
</div>
```
Data riwayat versi ini adalah HTML statis, bukan dari backend. Seharusnya di-render dari data `bom.versions` yang dikirim server.

**Perbaikan di JS `init()`:**
```javascript
this.bom.versions = (b.versions || []).map(v => ({
  version: v.version,
  label: 'v' + v.version + (v.is_active ? ' (Aktif)' : ''),
  date: v.created_at,
  by: v.created_by,
  is_active: v.is_active,
}));
```
Dan render dengan `x-for` di template.

---

**🟠 PENTING-6: HPP Card — input "Biaya Tenaga/Packing" tidak terhubung ke state Alpine**

```html
<input type="number" class="w-24 bg-slate-700 ...">
<span class="text-sm font-bold text-emerald-400">Rp 2.000</span>
```
Input ini tidak terhubung ke `x-model` apapun. Angka "Rp 2.000" di sebelah kanan adalah hardcoded dan tidak berubah meski user mengisi input. HPP yang ditampilkan (`scaledMaterialCost + 2000`) juga menggunakan nilai hardcoded 2000.

**Perbaikan:**
```javascript
// Di data:
laborCost: 2000,

// Di template:
<input type="number" x-model.number="laborCost" class="...">
<span x-text="formatCurrency(laborCost)"></span>

// Di computed:
get totalHPP() { return this.scaledMaterialCost + this.laborCost; }
```

---

**🟡 DISARANKAN-7: Tidak ada tautan ke detail R&D formula asal**

Jika BOM ini dipromote dari R&D (memiliki `rnd_id`), seharusnya ada tautan "Lihat Formula R&D Asal →" di detail BOM untuk traceability.

---

**🟡 DISARANKAN-8: Tabel bahan tidak memiliki kolom subtotal share (persentase per bahan)**

Pengguna tidak bisa langsung melihat kontribusi persentase setiap bahan dari tabel detail. Harus melihat chart di atas. Tambahkan kolom "% Biaya" di tabel.

---

## RINGKASAN BATCH 2

| # | File | Kode | Deskripsi Singkat |
|---|------|------|-------------------|
| 1 | bom_list | 🔴 | Tidak ada penanda BOM dari RnD vs manual |
| 2 | bom_list | 🔴 | Tidak ada filter versi aktif per SKU |
| 3 | bom_list | 🟠 | Tombol Edit di hover card tidak ada `@click.stop` |
| 4 | bom_form | 🔴 | Tidak ada mode Edit — selalu buat BOM baru |
| 5 | bom_form | 🔴 | `totalMaterialCost` selalu 0, tidak ada auto-sync harga dari SKU |
| 6 | bom_form | 🔴 | Tidak ada logic versioning saat BOM diubah |
| 7 | bom_form | 🟠 | Bahan dengan SKU tidak valid dibuang diam-diam tanpa peringatan |
| 8 | bom_form | 🟠 | `yield_qty` dan `yield_uom` tidak dikirim di payload |
| 9 | bom_form | 🟡 | Margin 60% hardcoded, tidak bisa dikonfigurasi |
| 10 | bom_detail | 🔴 | Tombol "Edit Resep" tidak memiliki handler/href |
| 11 | bom_detail | 🔴 | Tombol "Duplikat" tidak memiliki handler |
| 12 | bom_detail | 🟠 | Chart biaya memotong bahan ke-6+ tanpa kategori "Lainnya" |
| 13 | bom_detail | 🟠 | Qty produksi bisa diset ke 0/negatif tanpa validasi |
| 14 | bom_detail | 🟠 | Riwayat versi adalah data HTML statis, bukan dari backend |
| 15 | bom_detail | 🟠 | Input "Biaya Tenaga/Packing" tidak terhubung ke state Alpine |
| 16 | bom_detail | 🟡 | Tidak ada tautan ke formula R&D asal jika BOM dipromote |
