# BATCH 3 — MODUL RECIPE
**File yang dicakup:** `recipe_list.html` · `recipe_form.html` · `recipe_detail.html`

> Recipe berbeda dari BOM. BOM = standar material & biaya. Recipe = panduan teknis pembuatan
> (instruksi langkah, preparation time, yield). Keduanya harus terhubung tapi tetap terpisah.

---

## 3A. `recipe_list.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tag `<style>` muncul SEBELUM `{% extends %}` — template Django tidak valid**

```html
<style>
  .modal-overlay { ... }
  .panel-glass { ... }
</style>
{% extends 'base/base.html' %}
```
`{% extends %}` **harus menjadi tag pertama** di file template Django (sebelum whitespace apapun). CSS yang diletakkan sebelumnya akan menyebabkan Django melempar `TemplateSyntaxError: 'extends' tag is not the first tag`.

**Perbaikan:** Pindahkan seluruh blok `<style>` ke dalam `{% block extra_css %}`:
```html
{% extends 'base/base.html' %}
{% block extra_css %}
<style>
  .modal-overlay { ... }
  .panel-glass { ... }
</style>
{% endblock %}
```

---

**🔴 KRITIS-2: Sintaks `style=""` inline bertabrakan dengan Tailwind class di elemen yang sama**

Banyak elemen memiliki kombinasi aneh seperti:
```html
class="style="background-color: var(--em);" hover:style="..." text-white font-medium ..."
```
Ini bukan HTML valid. Tanda kutip yang tidak di-escape menyebabkan atribut `class` terpotong di `style=`, dan sisanya menjadi atribut HTML yang tidak dikenal. Render di browser akan kacau.

Ini tampaknya hasil dari script otomatis yang salah mengkonversi CSS variable ke inline style. Seluruh file perlu dibersihkan dari pola ini.

**Perbaikan contoh:**
```html
<!-- SEBELUM (rusak): -->
<a class="style="background-color: var(--em);" text-white font-medium ...">

<!-- SESUDAH (benar): -->
<a class="bg-emerald-600 text-white font-medium ..."
   style="background-color: var(--em);">
<!-- ATAU hapus inline style jika sudah ada Tailwind class -->
```

---

**🔴 KRITIS-3: Filter kategori menggunakan Django template tag `{% for category in categories %}` tapi data Alpine dari JSON**

```html
<select x-model="categoryFilter" @change="filterRecipes()">
  <option value="">All Categories</option>
  {% for category in categories %}
  <option value="{{ category.id }}">{{ category.name }}</option>
  {% endfor %}
</select>
```
Opsi kategori dirender oleh Django (server-side), namun data recipe difilter client-side oleh Alpine dengan `categoryFilter`. Recipe dari JSON harus memiliki field `category_id` yang cocok dengan `category.id` yang dirender Django.

Jika `recipe.category` di JSON adalah nama string (bukan ID), filter tidak akan pernah cocok.

**Perbaikan:** Pastikan JSON recipe memiliki field `category_id` integer, dan filter menggunakannya:
```javascript
filterRecipes() {
  this.filteredRecipes = this.allRecipes.filter(r => {
    const matchCat = !this.categoryFilter || String(r.category_id) === String(this.categoryFilter);
    const matchSearch = !this.searchQuery || r.name.toLowerCase().includes(this.searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });
}
```

---

**🟠 PENTING-4: Tidak ada tombol "Lihat Detail" — hanya ada Edit dan Delete**

```html
<div class="flex gap-3">
  <a :href="...">Edit</a>
  <button @click="confirmDelete(recipe)">Delete</button>
</div>
```
Kolom aksi di tabel tidak memiliki tautan ke halaman detail recipe. Pengguna tidak bisa membaca instruksi lengkap dari list.

**Tambahkan:**
```html
<a :href="`{% url 'recipe_detail' 0 %}`.replace('/0/', `/${recipe.id}/`)"
   class="text-slate-600 hover:text-slate-800">
  <i class="fas fa-eye"></i> Detail
</a>
```

---

**🟠 PENTING-5: `confirmDelete()` dipanggil tapi tidak terdefinisi di script yang tersedia**

Fungsi `confirmDelete(recipe)` ada di template namun tidak ada implementasinya di script Alpine yang terlihat di file. Ini akan menyebabkan `ReferenceError` di browser.

**Tambahkan minimal:**
```javascript
confirmDelete(recipe) {
  if (!confirm(`Hapus recipe "${recipe.name}"? Tindakan ini tidak dapat dibatalkan.`)) return;
  fetch(`/recipe/${recipe.id}/delete/`, {
    method: 'DELETE',
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  })
  .then(r => r.json())
  .then(j => {
    if (j.success) {
      this.allRecipes = this.allRecipes.filter(r => r.id !== recipe.id);
      this.filterRecipes();
    } else alert(j.error || 'Gagal menghapus recipe');
  });
},
```

---

**🟡 DISARANKAN-6: Bahasa campuran — judul "Recipes List" tapi konten sebagian Bahasa Indonesia**

Header halaman: "🍽️ Recipes List", "Manage and view all drink and food recipes"
Tapi pesan kosong: "No recipes found. Add one now."
Tombol: "Reset", "Add Recipe"

Sedangkan modul lain (BOM, RnD, Production) konsisten berbahasa Indonesia. Seragamkan bahasa di seluruh modul.

---

**🟡 DISARANKAN-7: Tidak ada kolom "HPP / Biaya" di tabel list**

`recipe_list` tidak menampilkan biaya sama sekali. Padahal `recipe_detail` memiliki `total_cost` dan `cost_per_unit`. Tambahkan kolom biaya ringkas di list untuk memudahkan perbandingan cepat.

---

**🟢 OPSIONAL-8: Tidak ada tautan ke BOM terkait dari list recipe**

Jika recipe sudah memiliki BOM yang terhubung, seharusnya ada indikator dan tautan ke BOM tersebut langsung dari list.

---

## 3B. `recipe_form.html`

### Masalah & Catatan

**🔴 KRITIS-1: Sama dengan recipe_list — `<style>` muncul sebelum `{% extends %}`**

Masalah identik dengan `recipe_list.html`. File ini juga memiliki blok `<style>` sebelum `{% extends 'base/base.html' %}`. Wajib diperbaiki dengan cara yang sama.

---

**🔴 KRITIS-2: Sintaks `style=""` bertabrakan dengan class Tailwind — sama dengan recipe_list**

Seluruh file mengandung pola `class="style="color: var(--em);" ..."` yang rusak. Perlu pembersihan menyeluruh.

---

**🟠 PENTING-3: Form menggunakan Django Formset (`formset.management_form`) bukan Alpine state**

```html
{{ formset.management_form }}
<form @submit.prevent="submitForm()" ...>
  {% csrf_token %}
```
Form ini adalah hybrid: Django Formset untuk ingredient rows + Alpine JS untuk logika UI. Ini menyebabkan dua sumber kebenaran untuk data yang sama. Jika `submitForm()` di Alpine mengirim via fetch (JSON), maka `formset.management_form` tidak diperlukan dan hanya menambah kebingungan. Jika submit lewat form HTML biasa, maka `@submit.prevent` dan Alpine state tidak diperlukan.

**Rekomendasi:** Pilih satu pendekatan:
- **Pendekatan A (Alpine/Fetch):** Hapus formset Django, kirim semua data via JSON fetch seperti `bom_form.html`
- **Pendekatan B (Django Form):** Hapus Alpine state, gunakan full Django form + formset rendering, hapus `@submit.prevent`

Pendekatan A lebih konsisten dengan file lain di sistem ini.

---

**🟠 PENTING-4: Tidak ada field untuk `preparation_time`, `yield_quantity`, `yield_unit`**

`recipe_detail.html` menampilkan `preparation_time`, `yield_quantity`, dan `yield_unit` sebagai metric card penting. Namun `recipe_form.html` tidak memiliki input untuk ketiga field ini. Data ini tidak akan pernah terisi dari form.

**Tambahkan input:**
```html
<div class="grid grid-cols-3 gap-4">
  <div>
    <label>Waktu Persiapan (menit)</label>
    <input type="number" x-model.number="formData.preparation_time" min="0">
  </div>
  <div>
    <label>Yield Quantity</label>
    <input type="number" x-model.number="formData.yield_quantity" min="0" step="any">
  </div>
  <div>
    <label>Yield Unit</label>
    <input type="text" x-model="formData.yield_unit" placeholder="cup, pax, kg...">
  </div>
</div>
```

---

**🟠 PENTING-5: Tidak ada field untuk `instructions` (langkah-langkah pembuatan)**

`recipe_detail.html` menampilkan `recipe.instructions` sebagai konten utama di panel kanan. Namun form tidak memiliki textarea untuk mengisi instruksi ini. Recipe tanpa instruksi tidak berguna sebagai panduan produksi.

**Tambahkan:**
```html
<div>
  <label class="block text-sm font-medium text-slate-700 mb-2">
    Instruksi Pembuatan <span class="text-red-500">*</span>
  </label>
  <textarea x-model="formData.instructions" rows="8"
            class="w-full px-4 py-3 border border-slate-300 rounded-lg ..."
            placeholder="Tuliskan langkah-langkah pembuatan secara urut..."></textarea>
</div>
```

---

**🟠 PENTING-6: `validateField()` dan `validateIngredient()` dipanggil tapi implementasinya tidak terlihat**

Fungsi `validateField('name')`, `validateField('category')`, dan `validateIngredient(index)` ada di template namun tidak terdefinisi di script Alpine yang tersedia di file. Browser akan error saat field di-blur.

---

**🟡 DISARANKAN-7: Tidak ada hubungan eksplisit ke BOM**

Form recipe tidak memiliki field untuk menghubungkan recipe dengan BOM yang ada. Tanpa link ini, recipe dan BOM menjadi dua entitas yang tidak saling mengenal di sistem.

**Tambahkan (opsional):**
```html
<div>
  <label>Tautkan ke BOM (opsional)</label>
  <select x-model="formData.bom_id">
    <option value="">Tidak ditautkan</option>
    <template x-for="b in boms" :key="b.id">
      <option :value="b.id" x-text="b.code + ' — ' + b.name"></option>
    </template>
  </select>
</div>
```

---

## 3C. `recipe_detail.html`

### Masalah & Catatan

**🔴 KRITIS-1: Tombol "Edit Recipe" mengarah ke `{% url 'recipe_form' recipe.id %}` tapi `recipe.id` belum tentu tersedia di template context**

```html
<a href="{% url 'recipe_form' recipe.id %}">Edit Recipe</a>
```
`recipe.id` di sini adalah variable Django template, bukan Alpine. Jika view tidak mengirimkan `recipe` sebagai context variable (hanya mengirim `recipe_data` sebagai JSON), tag ini akan gagal dengan `VariableDoesNotExist`.

**Perbaikan:** Gunakan Alpine untuk mengisi href setelah data tersedia, atau inject ID secara terpisah di context:
```python
# Di view Django:
context = {
  'recipe_data': recipe_json,
  'recipe_id': recipe.id,  # inject langsung
}
```
```html
<a href="{% url 'recipe_form' recipe_id %}">Edit Recipe</a>
```

---

**🟠 PENTING-2: `recipe.cost_per_unit` tidak dihitung client-side — harus datang dari server**

Halaman menampilkan `recipe.cost_per_unit` sebagai metric card, namun tidak ada computed property di Alpine yang menghitungnya. Jika backend tidak mengirim field ini, metric card akan tampil kosong atau 0.

**Tambahkan fallback computed:**
```javascript
get costPerUnit() {
  if (this.recipe.cost_per_unit) return this.recipe.cost_per_unit;
  const yieldQty = Number(this.recipe.yield_quantity || 1);
  return this.recipe.total_cost / yieldQty;
},
```

---

**🟠 PENTING-3: Panel "Instructions" menggunakan `whitespace-pre-line` tapi tidak ada sanitasi**

```html
<p class="text-sm leading-6 whitespace-pre-line text-slate-600"
   x-text="recipe.instructions || 'Belum ada instruksi.'"></p>
```
`x-text` aman dari XSS. Namun `whitespace-pre-line` tanpa batas tinggi bisa menyebabkan layout jelek jika instruksi sangat panjang. Tambahkan scroll container.

---

**🟠 PENTING-4: Tidak ada tautan ke BOM terkait**

`recipe_detail.html` tidak menampilkan apakah recipe ini sudah memiliki BOM yang terhubung. Tanpa informasi ini, tim produksi tidak tahu apakah recipe sudah siap untuk dijadikan SPK atau belum.

**Tambahkan di panel Metadata:**
```html
<div class="flex justify-between gap-4">
  <span class="text-slate-500">BOM Terkait</span>
  <a x-show="recipe.bom_id"
     :href="'{% url 'bom_detail' 0 %}'.replace('/0/', '/' + recipe.bom_id + '/')"
     class="font-medium text-emerald-600 hover:underline">
    Lihat BOM →
  </a>
  <span x-show="!recipe.bom_id" class="text-slate-400">Belum ada BOM</span>
</div>
```

---

**🟡 DISARANKAN-5: Search ingredient di detail tidak ada debounce**

```html
<input type="search" x-model="searchQuery" @input="applyFilter()" ...>
```
`@input` terpicu setiap keystroke. Untuk daftar ingredient yang panjang, ini menyebabkan re-filter terlalu sering. Tambahkan debounce:
```html
@input.debounce.200ms="applyFilter()"
```

---

**🟡 DISARANKAN-6: Metric card "Cost / Unit" tidak menampilkan satuan**

Kartu menampilkan nilai Rp X.XXX tapi tidak disebutkan "per cup" atau "per pax". Tambahkan `yield_unit` di bawah angka:
```html
<p class="text-sm text-slate-500 mt-1" x-text="'per ' + (recipe.yield_unit || 'unit')"></p>
```

---

## RINGKASAN BATCH 3

| # | File | Kode | Deskripsi Singkat |
|---|------|------|-------------------|
| 1 | recipe_list | 🔴 | `<style>` sebelum `{% extends %}` — template tidak valid |
| 2 | recipe_list | 🔴 | Sintaks `class="style=..."` rusak di seluruh file |
| 3 | recipe_list | 🔴 | Filter kategori: ID vs string tidak cocok dengan Alpine state |
| 4 | recipe_list | 🟠 | Tidak ada tombol "Lihat Detail" di tabel aksi |
| 5 | recipe_list | 🟠 | `confirmDelete()` dipanggil tapi tidak terdefinisi |
| 6 | recipe_list | 🟡 | Bahasa campuran English/Indonesia |
| 7 | recipe_form | 🔴 | `<style>` sebelum `{% extends %}` — template tidak valid |
| 8 | recipe_form | 🔴 | Sintaks `class="style=..."` rusak di seluruh file |
| 9 | recipe_form | 🟠 | Hybrid Django Formset + Alpine — dua sumber kebenaran |
| 10 | recipe_form | 🟠 | Tidak ada input `preparation_time`, `yield_quantity`, `yield_unit` |
| 11 | recipe_form | 🟠 | Tidak ada input `instructions` (langkah pembuatan) |
| 12 | recipe_form | 🟠 | `validateField()` dan `validateIngredient()` tidak terdefinisi |
| 13 | recipe_detail | 🔴 | `{% url 'recipe_form' recipe.id %}` — `recipe.id` mungkin tidak ada di context |
| 14 | recipe_detail | 🟠 | `cost_per_unit` tidak ada fallback computed jika server tidak kirim |
| 15 | recipe_detail | 🟠 | Tidak ada tautan ke BOM terkait |
| 16 | recipe_detail | 🟡 | Search ingredient tidak ada debounce |
| 17 | recipe_detail | 🟡 | Metric "Cost/Unit" tidak menampilkan satuan yield |
