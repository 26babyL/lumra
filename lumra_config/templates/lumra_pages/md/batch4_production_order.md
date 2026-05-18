# BATCH 4 — MODUL PRODUCTION ORDER
**File yang dicakup:** `production_order_list.html` · `production_order_form.html` · `production_order_detail.html` · `production_scheduling.html`

> Modul ini adalah inti eksekusi produksi. Kesalahan di sini berdampak langsung ke lantai kerja,
> ketersediaan stok, dan akurasi laporan biaya.

---

## 4A. `production_order_list.html`

### Masalah & Catatan

**🔴 KRITIS-1: Data `pos` tidak di-map dengan benar — field langsung dipakai mentah dari server**

```javascript
init(){
  const el = document.getElementById('pos-data');
  if (el && el.textContent) {
    try { this.pos = JSON.parse(el.textContent) || []; } catch(e) { this.pos = []; }
  }
}
```
Data dari server langsung diassign ke `this.pos` tanpa mapping. Artinya template mengasumsikan server mengirim field `product`, `code`, `status`, `target_qty`, `uom`, `line`, `start_date`, `priority`, `produced_qty` dengan nama persis seperti itu. Jika backend mengirim `scheduled_date` bukan `start_date`, atau `quantity` bukan `target_qty`, semua card akan tampil kosong/undefined.

**Perbaikan — tambahkan explicit mapping seperti di modul lain:**
```javascript
this.pos = raw.map(p => ({
  id: p.id,
  code: p.code || '',
  product: p.product || p.bom_name || '',
  status: p.status || 'pending',
  target_qty: Number(p.target_qty || p.target_quantity || 0),
  produced_qty: Number(p.produced_qty || 0),
  uom: p.uom || 'pcs',
  line: p.line || '—',
  start_date: p.scheduled_date || p.start_date || '—',
  priority: p.priority || 'Normal',
}));
```

---

**🔴 KRITIS-2: Progress bar akan error (`NaN%`) jika `target_qty = 0`**

```html
:style="`width: ${(po.produced_qty / po.target_qty) * 100}%`"
```
Jika `target_qty = 0` (data belum lengkap atau PO baru), perhitungan menghasilkan `NaN` atau `Infinity`, yang akan menyebabkan style `width: NaN%` — tidak ada error visible tapi bar tidak tampil dan bisa mempengaruhi layout.

**Perbaikan:**
```javascript
// Tambahkan getter atau computed inline:
progressPct(po) {
  if (!po.target_qty) return 0;
  return Math.min(Math.round((po.produced_qty / po.target_qty) * 100), 100);
},
```
```html
:style="`width: ${progressPct(po)}%`"
x-text="progressPct(po) + '%'"
```

---

**🔴 KRITIS-3: Filter `on_hold` tidak ada di toolbar tapi ada di `statusClass` map**

```javascript
statusClass(s) {
  const map = { pending: 'st-pending', in_progress: 'st-process', completed: 'st-completed', on_hold: 'st-hold' };
}
```
Status `on_hold` dikenali di `statusClass` tapi tidak ada tombol filter untuk melihat PO yang sedang di-hold. PO dengan status `on_hold` hanya tampil di filter "Semua" dan tidak bisa diisolasi.

**Tambahkan tombol filter:**
```html
<button @click="filter='on_hold'" class="px-4 py-2 rounded-lg text-xs font-bold transition"
        :class="filter==='on_hold' ? 'bg-rose-100 text-rose-700' : 'text-slate-600 hover:bg-slate-100'">
  Di-hold
</button>
```

---

**🟠 PENTING-4: Tidak ada indikator PO yang sudah melewati `scheduled_date` (overdue)**

Tidak ada penanda visual untuk PO yang `start_date`-nya sudah lewat tapi statusnya masih `pending`. Dalam operasi produksi, PO overdue harus langsung terlihat.

**Tambahkan computed dan badge:**
```javascript
isOverdue(po) {
  if (po.status !== 'pending' || !po.start_date || po.start_date === '—') return false;
  return new Date(po.start_date) < new Date();
},
```
```html
<span x-show="isOverdue(po)" class="text-[9px] font-bold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded">
  OVERDUE
</span>
```

---

**🟠 PENTING-5: Tidak ada pagination atau lazy load**

Jika production order berjumlah ratusan, semua card dirender sekaligus. Ini memperlambat browser dan tidak terasa profesional.

**Tambahkan pagination sederhana:**
```javascript
pageSize: 20,
currentPage: 1,
get paginatedPOs() {
  const start = (this.currentPage - 1) * this.pageSize;
  return this.filteredPOs.slice(start, start + this.pageSize);
},
get totalPages() { return Math.ceil(this.filteredPOs.length / this.pageSize); },
```

---

**🟠 PENTING-6: Search hanya mencakup `product` dan `code` — tidak mencakup `line`**

Tim produksi di Dapur A ingin lihat semua PO untuk line mereka. Saat ini tidak bisa filter berdasarkan `line`.

**Tambahkan filter line:**
```html
<select x-model="lineFilter" @change="..." class="...">
  <option value="">Semua Line</option>
  <template x-for="line in lineOptions" :key="line">
    <option :value="line" x-text="line"></option>
  </template>
</select>
```

---

**🟡 DISARANKAN-7: Tidak ada summary stats di atas list**

Tidak ada angka ringkasan: berapa PO pending, berapa in_progress, berapa yang selesai hari ini. Modul lain (RnD, production_scheduling) memiliki stats card. Tambahkan untuk konsistensi.

---

**🟡 DISARANKAN-8: Hover action "Kontrol Produksi" muncul untuk semua status termasuk `completed`**

PO yang sudah `completed` tidak perlu tombol "Kontrol Produksi" lagi. Lebih tepat menampilkan "Lihat Detail" saja untuk PO completed.

---

## 4B. `production_order_form.html`

### Masalah & Catatan

**🔴 KRITIS-1: `boms_data` JSON yang dikirim harus menyertakan field `items` dengan `stock` — tapi ini tidak dijamin**

```javascript
this.bomIngredients = (bom.items || []).map(item => ({
  sku: item.sku || '',
  name: item.name || item.sku || '-',
  quantity: Number(item.quantity || 0),
  uom: item.unit || '',
  stock: Number(item.stock || 0),
  unit_price: Number(item.unit_price || 0),
}));
```
Fitur "Prakiraan Kebutuhan Bahan" sepenuhnya bergantung pada `bom.items[].stock` yang disertakan dalam JSON. Jika view Django tidak melakukan join dengan tabel stok saat menyiapkan `boms_data`, semua nilai `stock` akan 0 dan `hasMaterialShortage` akan selalu `false` — fitur pengecekan stok tidak berfungsi.

**Tambahkan di dokumentasi/view Django:**
```python
# View wajib melakukan annotate stock saat menyiapkan boms_data:
bom_items_with_stock = BOMItem.objects.filter(bom=bom).annotate(
    current_stock=Subquery(
        StockLedger.objects.filter(variant=OuterRef('component_variant'))
        .order_by('-created_at').values('balance')[:1]
    )
)
```

---

**🔴 KRITIS-2: `generatedPO` menggunakan `Math.random()` — bisa menghasilkan duplikat**

```javascript
this.generatedPO = 'PO-' + new Date().getFullYear() + '-' + 
                   String(Math.floor(Math.random() * 1000)).padStart(3,'0');
```
Kode PO dibuat client-side dengan random number. Dua user yang membuka form pada waktu bersamaan bisa menghasilkan kode identik, menyebabkan duplikasi di database.

**Perbaikan:** Biarkan server yang generate kode PO (di Django view atau model `save()`), lalu inject ke template:
```python
# Di view Django:
context['suggested_po_code'] = generate_po_code()  # sequential dari DB
```
```html
{{ suggested_po_code|json_script:"po-code-data" }}
```
```javascript
const pcEl = document.getElementById('po-code-data');
this.generatedPO = pcEl ? JSON.parse(pcEl.textContent) : 'PO-DRAFT';
```

---

**🔴 KRITIS-3: Tombol "Buat SPK" tidak di-disable saat fetch sedang berjalan**

```html
<button @click="createPO()" :disabled="!form.bomId" class="...">Buat SPK</button>
```
Tombol hanya di-disable jika `!form.bomId`. Saat fetch sedang berjalan (server lambat), user bisa klik lagi → double submission → dua SPK dengan kode yang sama dibuat.

**Perbaikan:**
```javascript
isCreating: false,

createPO() {
  if (this.isCreating) return;
  this.isCreating = true;
  // ... fetch ...
  .finally(() => { this.isCreating = false; });
}
```
```html
:disabled="!form.bomId || isCreating"
x-text="isCreating ? 'Membuat SPK...' : 'Buat SPK'"
```

---

**🟠 PENTING-4: `estimatedTime` dihitung dengan rumus tidak jelas tanpa basis data aktual**

```javascript
get estimatedTime() {
  const qty = Number(this.form.qty || 0);
  const ingredientFactor = this.materialRows.length ? Math.max(this.materialRows.length / 4, 1) : 1;
  return Math.max(1, Math.ceil((qty / 10) * ingredientFactor));
},
```
Rumus ini murni imajinasi — tidak berdasarkan data historis produksi maupun parameter BOM manapun. Menampilkan estimasi yang tidak akurat lebih menyesatkan daripada tidak menampilkan sama sekali.

**Rekomendasi:** Ganti dengan field input manual:
```html
<div>
  <label>Estimasi Durasi Produksi (jam)</label>
  <input type="number" x-model.number="form.estimated_hours" min="0.5" step="0.5" placeholder="cth: 2">
</div>
```
Atau ambil dari field `standard_time` di BOM jika tersedia.

---

**🟠 PENTING-5: Tidak ada field `assigned_to` (penugasan operator/chef)**

SPK yang dibuat tidak memiliki field untuk menugaskan operator atau chef yang bertanggung jawab. Di `production_order_detail.html` juga tidak ada field ini. Akibatnya tidak ada akuntabilitas siapa yang mengerjakan produksi.

**Tambahkan:**
```html
<div>
  <label>Ditugaskan ke</label>
  <select x-model="form.assigned_to">
    <option value="">Pilih Operator...</option>
    <template x-for="op in operators" :key="op.id">
      <option :value="op.id" x-text="op.name"></option>
    </template>
  </select>
</div>
```

---

**🟠 PENTING-6: Field `form.line` tidak memiliki default value**

```javascript
form: { bomId: '', qty: 10, line: '', startDate: '', priority: 'Normal', notes: '' },
```
`line` diinisialisasi sebagai string kosong. Saat user tidak memilih line, payload dikirim dengan `line: ''`. Backend harus menangani string kosong ini atau akan menyimpan data tidak valid.

**Perbaikan:**
```javascript
// Di init(), set default dari opsi pertama yang tersedia:
this.form.line = this.lineOptions[0] || '';
```

---

**🟡 DISARANKAN-7: Preview BOM tidak menampilkan total HPP per unit**

Panel "Prakiraan Kebutuhan Bahan" menampilkan total biaya bahan (`estimatedCost`) tapi tidak menghitung HPP per unit (biaya ÷ qty target). Ini informasi penting untuk keputusan produksi.

**Tambahkan:**
```javascript
get costPerUnit() {
  return this.form.qty > 0 ? this.estimatedCost / this.form.qty : 0;
},
```
```html
<div class="flex justify-between items-center">
  <span class="text-xs font-bold text-slate-500">HPP per Unit</span>
  <span class="text-sm font-bold text-slate-800" x-text="formatCurrency(costPerUnit)"></span>
</div>
```

---

## 4C. `production_order_detail.html`

### Masalah & Catatan

**🔴 KRITIS-1: `startPO()`, `pausePO()`, `completePO()`, `updateQty()` hanya mengubah state lokal — tidak ada sync ke server**

```javascript
startPO() {
  if(confirm('Mulai produksi sekarang?')) {
    this.po.status = 'in_progress';
    this.po.actual_start = new Date().toLocaleTimeString(...);
  }
},
```
Semua fungsi kontrol produksi hanya mengubah state Alpine di browser. Jika user refresh halaman, semua perubahan hilang. Tidak ada fetch ke server sama sekali.

**Ini masalah fundamental** — halaman kontrol produksi yang paling kritis di seluruh sistem justru tidak menyimpan apapun ke database.

**Perbaikan wajib — setiap aksi harus di-persist:**
```javascript
async startPO() {
  if (!confirm('Mulai produksi sekarang?')) return;
  const res = await fetch(`/production/${this.po.id}/start/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  });
  const j = await res.json();
  if (j.success) {
    this.po.status = 'in_progress';
    this.po.actual_start = j.started_at;
  } else alert(j.error || 'Gagal memulai produksi');
},

async updateQty(delta) {
  const newQty = this.po.produced_qty + delta;
  if (newQty < 0 || newQty > this.po.target_qty + 10) return;
  const res = await fetch(`/production/${this.po.id}/update-qty/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify({ produced_qty: newQty })
  });
  const j = await res.json();
  if (j.success) this.po.produced_qty = newQty;
},
```

---

**🔴 KRITIS-2: `progress-circle` menggunakan CSS `conic-gradient` dengan CSS variable `--pct` tapi tidak di-set**

```html
<div class="progress-circle" :style="`--pct: ${(po.produced_qty / po.target_qty) * 100}%`">
```
CSS di style block:
```css
.progress-circle {
  background: conic-gradient(#0f172a var(--pct), #e2e8f0 0);
}
```
Pendekatan `--pct` via inline style Alpine harusnya bekerja, namun jika `target_qty = 0` akan menghasilkan `Infinity%` atau `NaN%` yang merusak tampilan circle.

**Perbaikan:**
```html
:style="`--pct: ${po.target_qty > 0 ? Math.min((po.produced_qty / po.target_qty) * 100, 100).toFixed(1) : 0}%`"
```

---

**🔴 KRITIS-3: Tombol `completePO()` di-disable hanya jika `produced_qty < target_qty` — tidak ada konfirmasi final**

```html
<button @click="completePO()" :disabled="po.produced_qty < po.target_qty">SELESAIKAN</button>
```
Jika `produced_qty === target_qty`, tombol langsung aktif dan bisa diklik tanpa konfirmasi apapun. Menyelesaikan produksi adalah aksi yang tidak bisa di-undo — harus ada konfirmasi yang jelas dan mencatat siapa yang menyelesaikan.

**Perbaikan:**
```javascript
async completePO() {
  if (!confirm(`Selesaikan produksi ini? Total ${this.po.produced_qty} unit akan dicatat sebagai output.`)) return;
  const res = await fetch(`/production/${this.po.id}/complete/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  });
  const j = await res.json();
  if (j.success) {
    this.po.status = 'completed';
    this.po.completed_at = j.completed_at;
  } else alert(j.error);
},
```

---

**🟠 PENTING-4: Tidak ada tampilan daftar bahan yang harus digunakan (dari BOM)**

Halaman kontrol produksi hanya menampilkan progress circle dan tombol aksi. Operator tidak bisa melihat daftar bahan yang seharusnya digunakan dari BOM langsung di halaman ini. Mereka harus buka BOM secara terpisah.

**Tambahkan panel ringkas:**
```html
<div class="bg-slate-50 rounded-xl p-4">
  <p class="text-xs font-bold text-slate-400 uppercase mb-3">Bahan yang Dibutuhkan</p>
  <template x-for="item in po.bom_items" :key="item.sku">
    <div class="flex justify-between text-sm py-1 border-b border-slate-100">
      <span x-text="item.name"></span>
      <span class="font-mono" x-text="item.required_qty + ' ' + item.uom"></span>
    </div>
  </template>
</div>
```

---

**🟠 PENTING-5: Tombol `+` dan `-` tidak ada batasan minimum qty**

```javascript
updateQty(delta) {
  const newQty = this.po.produced_qty + delta;
  if(newQty >= 0 && newQty <= this.po.target_qty + 10) {
    this.po.produced_qty = newQty;
  }
},
```
Qty bisa dikurangi sampai 0 tanpa konfirmasi. Jika operator tidak sengaja tekan `-` berkali-kali, angka produksi bisa menjadi 0.

**Perbaikan:** Tambahkan konfirmasi saat qty turun signifikan (lebih dari 10% dari target).

---

**🟠 PENTING-6: `po.actual_start` diisi dengan `toLocaleTimeString` — hanya waktu, tanpa tanggal**

```javascript
this.po.actual_start = new Date().toLocaleTimeString('id-ID', {hour: '2-digit', minute:'2-digit'});
```
Ini hanya menyimpan jam dan menit (misal: "09:45"), tanpa tanggal. Jika produksi melewati tengah malam, data ini tidak bermakna.

**Perbaikan:**
```javascript
this.po.actual_start = new Date().toLocaleString('id-ID', {
  day: '2-digit', month: 'short', year: 'numeric',
  hour: '2-digit', minute: '2-digit'
});
```

---

**🟡 DISARANKAN-7: Tidak ada field input qty manual (selain tombol +/-)**

Untuk target qty yang besar (misal: 500 unit), operator harus klik tombol `+` berkali-kali. Tambahkan input angka langsung di samping tombol +/-:

```html
<input type="number" x-model.number="po.produced_qty"
       :min="0" :max="po.target_qty + 10"
       @change="updateQty(0)"
       class="w-20 text-center border rounded-lg px-2 py-1 text-lg font-bold">
```

---

**🟡 DISARANKAN-8: Tidak ada log history tindakan operator**

Tidak ada catatan kapan PO dimulai, kapan di-pause, berapa kali di-pause, dan siapa operatornya. Ini penting untuk audit dan analisis efisiensi lantai kerja.

---

## 4D. `production_scheduling.html`

### Masalah & Catatan

**🔴 KRITIS-1: `dateToLocalISO()` menggunakan local timezone tapi `scheduled_date` dari server mungkin UTC**

```javascript
dateToLocalISO(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
},
```
Filter kalender menggunakan `item.scheduled_date === dateStr` (exact string match). Jika `scheduled_date` dari server adalah `"2024-01-15T00:00:00+07:00"` bukan `"2024-01-15"`, tidak akan ada yang cocok dan semua sel kalender akan kosong.

**Perbaikan:** Normalisasi `scheduled_date` saat init:
```javascript
this.scheduledOrders = (JSON.parse(el.textContent) || [])
  .filter(item => item.scheduled_date)
  .map(item => ({
    ...item,
    scheduled_date: item.scheduled_date.substring(0, 10) // ambil YYYY-MM-DD saja
  }));
```

---

**🟠 PENTING-2: Tidak ada indikator hari ini di kalender**

Kalender tidak menandai hari ini dengan visual berbeda. User tidak tahu tanggal mana yang sekarang.

**Tambahkan:**
```javascript
get todayStr() {
  return this.dateToLocalISO(new Date());
},
```
```html
<div class="day-cell" :class="{
  'empty': day.type === 'padding',
  'ring-2 ring-slate-800 bg-white': day.dateStr === todayStr
}">
```

---

**🟠 PENTING-3: Pill task di kalender tidak menampilkan qty target**

```html
<div class="font-semibold" x-text="task.code"></div>
<div class="truncate text-[10px]" x-text="task.product"></div>
```
Informasi qty target tidak tampil. Planner tidak bisa menilai beban kerja per hari hanya dari nama PO.

**Tambahkan:**
```html
<div class="text-[9px] opacity-70" x-text="task.target_qty + ' ' + (task.uom || 'pcs')"></div>
```

---

**🟠 PENTING-4: Tidak ada view mingguan atau tampilan Gantt**

Kalender bulanan dengan sel `min-height: 150px` terlalu padat jika ada 5+ PO per hari. Tidak ada cara untuk melihat distribusi beban kerja per jam atau per line dalam satu hari.

**Minimal tambahkan:** Toggle antara tampilan bulanan dan mingguan.

---

**🟡 DISARANKAN-5: Stats "Scheduled Orders" menghitung semua orders termasuk bulan lain**

```javascript
get scheduledOrders() {
  // ini adalah semua orders dari seluruh waktu, bukan hanya bulan aktif
}
```
`scheduledOrders.length` di stats card menghitung semua PO yang punya scheduled_date (dari semua bulan), bukan hanya yang ada di bulan yang sedang ditampilkan. Ini membingungkan karena stats card berdampingan dengan kalender bulan tertentu.

**Perbaikan:**
```javascript
get currentMonthOrders() {
  const prefix = `${this.currentDate.getFullYear()}-${String(this.currentDate.getMonth() + 1).padStart(2, '0')}`;
  return this.scheduledOrders.filter(o => (o.scheduled_date || '').startsWith(prefix));
},
```
Gunakan `currentMonthOrders` untuk semua stats card.

---

**🟡 DISARANKAN-6: Tidak ada fitur drag-and-drop untuk reschedule**

Planner seharusnya bisa menggeser pill task dari satu tanggal ke tanggal lain untuk reschedule. Saat ini harus membuka detail PO dan edit form secara terpisah.

---

## RINGKASAN BATCH 4

| # | File | Kode | Deskripsi Singkat |
|---|------|------|-------------------|
| 1 | po_list | 🔴 | Data `pos` tidak di-map — field diasumsikan sama persis dengan server |
| 2 | po_list | 🔴 | Progress bar `NaN%` jika `target_qty = 0` |
| 3 | po_list | 🔴 | Filter `on_hold` tidak ada di toolbar |
| 4 | po_list | 🟠 | Tidak ada indikator PO overdue |
| 5 | po_list | 🟠 | Search tidak mencakup filter berdasarkan `line` |
| 6 | po_form | 🔴 | `boms_data` harus menyertakan `stock` per item — tidak dijamin dari view |
| 7 | po_form | 🔴 | Kode PO pakai `Math.random()` — bisa duplikat jika 2 user buka bersamaan |
| 8 | po_form | 🔴 | Tombol "Buat SPK" tidak di-disable saat fetch berjalan — double submission |
| 9 | po_form | 🟠 | `estimatedTime` dihitung dengan rumus tidak berdasar data aktual |
| 10 | po_form | 🟠 | Tidak ada field `assigned_to` — tidak ada akuntabilitas operator |
| 11 | po_detail | 🔴 | SEMUA aksi (start, pause, complete, updateQty) tidak sync ke server |
| 12 | po_detail | 🔴 | Progress circle crash jika `target_qty = 0` |
| 13 | po_detail | 🔴 | `completePO()` aktif tanpa konfirmasi final saat qty terpenuhi |
| 14 | po_detail | 🟠 | Tidak ada daftar bahan BOM yang harus digunakan |
| 15 | po_detail | 🟠 | `actual_start` hanya menyimpan jam-menit, tanpa tanggal |
| 16 | po_detail | 🟡 | Tidak ada input qty manual — harus klik +/- berkali-kali |
| 17 | scheduling | 🔴 | `scheduled_date` tidak dinormalisasi — bisa gagal match jika format ISO datetime |
| 18 | scheduling | 🟠 | Tidak ada penanda hari ini di kalender |
| 19 | scheduling | 🟠 | Stats card menghitung semua bulan bukan bulan aktif |
| 20 | scheduling | 🟠 | Pill task tidak menampilkan qty target |
