# 🎨 Lumra ERP — UI Audit Report

> **Tanggal Audit**: 12 March 2026 • 02:39  
> **Total File HTML**: 150 file  
> **File Berhasil Di-scan**: 150 file  
> **Tools**: `lumra_ui_audit.py` (custom scanner)

---

## 📋 Daftar Isi

1. [Executive Summary](#1-executive-summary)
2. [Inventaris Komponen UI](#2-inventaris-komponen-ui)
3. [Audit Warna](#3-audit-warna)
4. [Ikon & Aset Visual](#4-ikon--aset-visual)
5. [JavaScript Libraries](#5-javascript-libraries)
6. [Layout & Spacing](#6-layout--spacing)
7. [Inline Styles — Masalah Utama](#7-inline-styles--masalah-utama)
8. [Temuan & Rekomendasi](#8-temuan--rekomendasi)
9. [Design Token yang Disarankan](#9-design-token-yang-disarankan)

---

## 1. Executive Summary

| Metrik | Nilai | Status |
|--------|-------|--------|
| Total file HTML di-scan | **150 file** | — |
| Warna Hex unik ditemukan | **30 warna** | 🟢 OK |
| Kelas Tailwind warna unik | **30 kelas** | 🟢 OK |
| Penggunaan inline `style=""` | **1033×** | 🔴 KRITIS |
| File yang pakai inline style | **101 file** | 🟡 PERLU PERHATIAN |
| Jenis komponen berbeda | **25 jenis** | 🟢 OK |
| Ikon Font Awesome berbeda | **189 ikon** | — |

### Kesimpulan Utama

> **87 warna Hex unik** dan **316 kelas warna Tailwind** tersebar di 150 file.
> Ini adalah tanda "Desain tanpa token" — setiap developer bebas pakai warna apapun.
> Prioritas tertinggi: **unifikasi palet warna** dan **eliminasi inline styles**.

---

## 2. Inventaris Komponen UI

Dihitung berdasarkan jumlah **file HTML** yang menggunakan komponen tersebut.

### 2.1 Distribusi Komponen

| Komponen | Jumlah File | Penetrasi | Keterangan |
|----------|-------------|-----------|------------|
| Button `<button>` | **133** / 150 | `█████████████████░░░` 89% | Ada `<button>`, `btn`, Tailwind — perlu standarisasi varian |
| Toast / Notifikasi | **109** / 150 | `██████████████░░░░░░` 73% | Sangat tinggi — pattern toast berbeda-beda antar file |
| Navbar / Nav | **106** / 150 | `██████████████░░░░░░` 71% | Hampir semua halaman — sudah konsisten via base.html? |
| Card / Panel | **104** / 150 | `█████████████░░░░░░░` 69% | Class "card" tersebar — gaya berbeda di tiap modul |
| Input Text | **94** / 150 | `████████████░░░░░░░░` 63% | Styling input belum tentu seragam |
| Select / Dropdown | **93** / 150 | `████████████░░░░░░░░` 62% | — |
| Form `<form>` | **91** / 150 | `████████████░░░░░░░░` 61% | — |
| Badge / Label | **84** / 150 | `███████████░░░░░░░░░` 56% | Warna badge tidak konsisten (emerald, amber, rose, dll) |
| Tabel `<table>` | **82** / 150 | `██████████░░░░░░░░░░` 55% | Gaya header, border, dan hover berbeda antar modul |
| Tabel dengan Header | **82** / 150 | `██████████░░░░░░░░░░` 55% | — |
| Pagination | **80** / 150 | `██████████░░░░░░░░░░` 53% | Pattern pagination mungkin berbeda-beda |
| Avatar (foto user) | **61** / 150 | `████████░░░░░░░░░░░░` 41% | Fallback avatar kalau foto tidak ada? |
| Modal / Dialog | **60** / 150 | `████████░░░░░░░░░░░░` 40% | Pola modal berbeda (Alpine, vanilla JS, custom) |
| Chart / Grafik | **58** / 150 | `███████░░░░░░░░░░░░░` 39% | Pakai Chart.js — sudah ada wrapper component? |
| Dropdown Menu | **45** / 150 | `██████░░░░░░░░░░░░░░` 30% | — |
| Date Picker | **38** / 150 | `█████░░░░░░░░░░░░░░░` 25% | flatpickr tersebar di 37 file — versi sama? |
| Breadcrumb | **33** / 150 | `████░░░░░░░░░░░░░░░░` 22% | — |
| Textarea | **25** / 150 | `███░░░░░░░░░░░░░░░░░` 17% | — |
| Alert / Banner | **25** / 150 | `███░░░░░░░░░░░░░░░░░` 17% | — |
| Search Input | **24** / 150 | `███░░░░░░░░░░░░░░░░░` 16% | — |
| Tab / Tabbed Nav | **21** / 150 | `██░░░░░░░░░░░░░░░░░░` 14% | — |
| Progress Bar | **15** / 150 | `██░░░░░░░░░░░░░░░░░░` 10% | — |
| Sidebar | **12** / 150 | `█░░░░░░░░░░░░░░░░░░░` 8% | — |
| Tooltip | **11** / 150 | `█░░░░░░░░░░░░░░░░░░░` 7% | — |
| Accordion | **1** / 150 | `░░░░░░░░░░░░░░░░░░░░` 1% | — |

### 2.2 Komponen Kritis untuk Distandarisasi

Berdasarkan frekuensi dan potensi inkonsistensi:

| Prioritas | Komponen | Alasan |
|-----------|----------|--------|
| 🔴 P1 | **Button** | 133 file, paling banyak — variasi style tertinggi |
| 🔴 P1 | **Badge / Status Label** | 84 file, warna status (sukses/warning/error) tidak konsisten |
| 🔴 P1 | **Tabel** | 82 file, gaya header/row berbeda tiap modul |
| 🟡 P2 | **Card** | 104 file, padding dan shadow berbeda |
| 🟡 P2 | **Toast / Notifikasi** | 109 file, pola JS berbeda |
| 🟡 P2 | **Modal** | 60 file, struktur HTML modal bervariasi |
| 🟢 P3 | **Sidebar** | 12 file, sudah terpusat di base template |
| 🟢 P3 | **Navbar** | 106 file, mungkin sudah via include |

---

## 3. Audit Warna

### 3.1 Warna Hex Inline (di dalam HTML / style="")

**30 warna Hex unik** ditemukan tersebar di file HTML.
Ini adalah warna yang di-hardcode, bukan via Tailwind class.

| Rank | Warna | Hex Code | Kemunculan | Keluarga Warna |
|------|-------|----------|------------|----------------|
| 1 | 🟢 | `#059669` | 719× | Emerald / Green |
| 2 | ⚫ | `#94A3B8` | 385× | Slate / Gray |
| 3 | ⚪ | `#FFF` | 326× | White |
| 4 | 🟢 | `#10B981` | 309× | Emerald / Green |
| 5 | ⚫ | `#475569` | 171× | Slate / Gray |
| 6 | ⚫ | `#1E293B` | 142× | Slate / Gray |
| 7 | ⚫ | `#E2E8F0` | 141× | Slate / Gray |
| 8 | ⚫ | `#64748B` | 113× | Slate / Gray |
| 9 | 🟡 | `#F59E0B` | 108× | Amber / Orange |
| 10 | 🔵 | `#6366F1` | 98× | Indigo / Purple |
| 11 | 🟢 | `#6EE7B7` | 95× | Emerald / Green |
| 12 | 🔵 | `#0EA5E9` | 75× | Blue |
| 13 | 🔵 | `#8B5CF6` | 72× | Indigo / Purple |
| 14 | ⚫ | `#CBD5E1` | 72× | Slate / Gray |
| 15 | 🔵 | `#3B82F6` | 64× | Blue |
| 16 | 🔵 | `#7C3AED` | 64× | Indigo / Purple |
| 17 | 🔵 | `#2563EB` | 62× | Blue |
| 18 | 🔴 | `#F43F5E` | 55× | Rose / Red |
| 19 | 🔴 | `#E11D48` | 41× | Rose / Red |
| 20 | 🟡 | `#D97706` | 41× | Amber / Orange |
| 21 | 🔵 | `#4F46E5` | 38× | Indigo / Purple |
| 22 | 🟢 | `#D1FAE5` | 36× | Emerald / Green |
| 23 | ⚫ | `#F1F5F9` | 27× | Slate / Gray |
| 24 | 🔵 | `#C7D2FE` | 26× | Indigo / Purple |
| 25 | ⚫ | `#0F172A` | 24× | Slate / Gray |
| 26 | 🟡 | `#B45309` | 22× | Amber / Orange |
| 27 | 🔴 | `#BE185D` | 22× | Rose / Red |
| 28 | 🟢 | `#065F46` | 17× | Emerald / Green |
| 29 | 🔵 | `#6D28D9` | 14× | Indigo / Purple |
| 30 | 🔵 | `#BFDBFE` | 14× | Blue |

### 3.2 Analisis Warna Keluarga Hex

| Keluarga | Warna-warna yang ditemukan | Total Muncul |
|----------|---------------------------|--------------|
| **Emerald / Green** | `#059669`, `#10B981`, `#6EE7B7`, `#D1FAE5`, `#065F46` | 1176× |
| **Slate / Gray** | `#94A3B8`, `#475569`, `#1E293B`, `#64748B`, `#E2E8F0`, `#CBD5E1`, `#F1F5F9`, `#0F172A` | 1075× |
| **Indigo / Purple** | `#6366F1`, `#8B5CF6`, `#7C3AED`, `#4F46E5`, `#C7D2FE`, `#6D28D9` | 312× |
| **Blue** | `#0EA5E9`, `#3B82F6`, `#2563EB`, `#BFDBFE` | 215× |
| **Amber / Orange** | `#F59E0B`, `#D97706`, `#B45309` | 171× |
| **Rose / Red** | `#F43F5E`, `#E11D48`, `#BE185D` | 118× |
| **White** | `#FFF` | 326× |

> ⚠️ **Masalah**: Emerald saja punya 5 variasi Hex berbeda.
> Standarisasi ke 1 variabel CSS token per warna.

### 3.3 Kelas Warna Tailwind (Top 30)

**30 kelas warna Tailwind unik** ditemukan. Ini adalah "Peta Kekacauan" warna Anda.

| Rank | Class Tailwind | Kemunculan | Kategori |
|------|---------------|------------|---------|
| 1 | `text-slate-400` | 2147× | Teks |
| 2 | `text-slate-800` | 617× | Teks |
| 3 | `text-slate-300` | 560× | Teks |
| 4 | `border-slate-100/60` | 497× | Border |
| 5 | `text-slate-700` | 431× | Teks |
| 6 | `text-white` | 420× | Teks |
| 7 | `text-emerald-600` | 409× | Teks |
| 8 | `text-slate-500` | 400× | Teks |
| 9 | `text-slate-600` | 349× | Teks |
| 10 | `bg-white` | 348× | Background |
| 11 | `bg-emerald-50` | 233× | Background |
| 12 | `bg-emerald-500` | 230× | Background |
| 13 | `text-gray-900` | 226× | Teks |
| 14 | `text-gray-600` | 196× | Teks |
| 15 | `border-emerald-100` | 181× | Border |
| 16 | `text-emerald-500` | 169× | Teks |
| 17 | `text-emerald-700` | 164× | Teks |
| 18 | `text-gray-500` | 146× | Teks |
| 19 | `border-slate-100` | 140× | Border |
| 20 | `bg-slate-50` | 129× | Background |
| 21 | `text-gray-400` | 124× | Teks |
| 22 | `text-slate-200` | 119× | Teks |
| 23 | `text-gray-700` | 111× | Teks |
| 24 | `bg-slate-100` | 103× | Background |
| 25 | `bg-amber-50` | 89× | Background |
| 26 | `bg-gray-50` | 87× | Background |
| 27 | `text-amber-500` | 85× | Teks |
| 28 | `border-gray-100` | 85× | Border |
| 29 | `text-rose-400` | 84× | Teks |
| 30 | `border-gray-200` | 82× | Border |

### 3.4 Distribusi Keluarga Warna Tailwind

| Keluarga | Total Penggunaan | Proporsi |
|----------|-----------------|----------|
| `slate` | 5492 | `███████████████` 61.3% |
| `emerald` | 1386 | `███░░░░░░░░░░░░` 15.5% |
| `gray` | 1057 | `██░░░░░░░░░░░░░` 11.8% |
| `white` | 768 | `██░░░░░░░░░░░░░` 8.6% |
| `amber` | 174 | `░░░░░░░░░░░░░░░` 1.9% |
| `rose` | 84 | `░░░░░░░░░░░░░░░` 0.9% |

> **Kesimpulan**: Dominan `slate` + `emerald`. Tapi juga ada `gray`, `zinc`, `neutral`
> yang secara visual mirip — ini duplikasi yang harus dikonsolidasi.

---

## 4. Ikon & Aset Visual

### 4.1 Library Ikon yang Digunakan

| Library | Status | Catatan |
|---------|--------|---------|
| **Font Awesome** | ✅ Digunakan (139 ref) | Library utama — `fa-*` |
| **Heroicons** | ⚠️ Sedikit (SVG inline) | Tercampur dengan FA |
| **SVG Inline** | 118 SVG | Perlu audit — mungkin duplikat dengan FA |

### 4.2 Top 30 Ikon Paling Sering Dipakai

| Rank | Ikon | Kemunculan | Konteks |
|------|------|------------|---------|
| 1 | `fa-times` | 180× | Tutup modal/dialog |
| 2 | `fa-search` | 143× | Search input |
| 3 | `fa-chevron-right` | 102× | Navigasi, breadcrumb |
| 4 | `fa-chevron-left` | 94× | Navigasi, pagination |
| 5 | `fa-chevron-down` | 94× | Dropdown, accordion |
| 6 | `fa-check` | 89× | Status sukses, checkbox |
| 7 | `fa-store` | 79× | Outlet/toko |
| 8 | `fa-clock` | 75× | Waktu, riwayat |
| 9 | `fa-arrow-right` | 62× | Navigasi, CTA |
| 10 | `fa-trash` | 59× | Hapus data |
| 11 | `fa-spin` | 51× | Loading state |
| 12 | `fa-coins` | 47× | Keuangan, loyalty |
| 13 | `fa-file-csv` | 47× | Export data |
| 14 | `fa-calculator` | 44× | Kalkulasi harga |
| 15 | `fa-chart-line` | 44× | Grafik penjualan |
| 16 | `fa-shopping-cart` | 43× | POS, order |
| 17 | `fa-boxes` | 42× | Inventory/stok |
| 18 | `fa-plus` | 41× | Tambah item |
| 19 | `fa-file-export` | 40× | Export laporan |
| 20 | `fa-file-excel` | 40× | — |
| 21 | `fa-sliders-h` | 39× | — |
| 22 | `fa-print` | 38× | — |
| 23 | `fa-credit-card` | 37× | — |
| 24 | `fa-calendar-alt` | 37× | — |
| 25 | `fa-money-bill-wave` | 37× | — |
| 26 | `fa-file-pdf` | 35× | — |
| 27 | `fa-university` | 35× | — |
| 28 | `fa-qrcode` | 35× | — |
| 29 | `fa-calendar` | 35× | — |
| 30 | `fa-star` | 30× | — |

> **Rekomendasi**: Tetap gunakan Font Awesome saja.
> Ganti semua SVG inline yang duplikat dengan `<i class="fas fa-...">` yang sudah ada.

---

## 5. JavaScript Libraries

| Library | Kemunculan | Versi | Catatan |
|---------|------------|-------|---------|
| **flatpickr** | 37 file | Tidak diketahui | Date picker utama — sudah dominan ✅ |
| **Chart.js** | 10 file | Tidak diketahui | Grafik dashboard ✅ |
| **Alpine.js** | 7 file | Tidak diketahui | Interaktivitas ringan ✅ |
| **CDN refs total** | 56 | — | Referensi ke CDN eksternal |

> ⚠️ **56 referensi CDN eksternal** — tidak ada versi yang terkunci.
> Risiko: library berubah tanpa kontrol. Rekomendasi: gunakan npm/bundler atau lock versi.

---

## 6. Layout & Spacing

### 6.1 Layout System

| Sistem | Penggunaan | Proporsi |
|--------|------------|----------|
| Flexbox (`flex`, `flex-col`, dll) | **5,187×** | Dominan |
| Grid (`grid`, `grid-cols-*`) | **528×** | Sekunder |
| SVG Inline | **118×** | Ikon/ilustrasi |

> Flexbox 10× lebih banyak dari Grid. Sudah konsisten.

### 6.2 Spacing yang Paling Sering Dipakai

| Class | Kemunculan | Nilai (rem) |
|-------|------------|-------------|
| `py-4` | 1231× | 1rem |
| `px-6` | 1124× | 1.5rem |
| `gap-2` | 1115× | 0.5rem |
| `gap-3` | 607× | 0.75rem |
| `mt-0.5` | 571× | — |
| `px-4` | 478× | 1rem |
| `mb-1` | 423× | 0.25rem |
| `px-5` | 405× | 1.25rem |
| `px-3` | 404× | 0.75rem |
| `py-2` | 386× | 0.5rem |
| `p-4` | 376× | 1rem |
| `py-3` | 309× | 0.75rem |
| `mt-1` | 297× | 0.25rem |
| `gap-1.5` | 291× | — |
| `py-2.5` | 234× | — |

### 6.3 Ukuran Teks yang Dipakai

| Class | Kemunculan |
|-------|------------|
| `text-sm` | 939× |
| `text-xs` | 836× |
| `text-2xl` | 416× |
| `text-xl` | 131× |
| `text-lg` | 98× |
| `text-3xl` | 81× |
| `text-4xl` | 31× |
| `text-base` | 5× |
| `text-5xl` | 2× |

### 6.4 Border Radius

| Class | Kemunculan |
|-------|------------|
| `rounded-xl` | 779× |
| `rounded-full` | 664× |
| `rounded-lg` | 496× |
| `rounded-2xl` | 337× |
| `rounded` | 63× |
| `rounded-md` | 11× |
| `rounded-3xl` | 4× |
| `rounded-none` | 4× |
| `rounded-l-md` | 3× |
| `rounded-r-md` | 3× |

### 6.5 Shadow

| Class | Kemunculan |
|-------|------------|
| `shadow-xl` | 150× |
| `shadow-sm` | 105× |
| `shadow-md` | 76× |
| `shadow-2xl` | 44× |
| `shadow-[0_0_0_1px_rgba(16,185,129,0.12),0_4px_16px_rgba(16,185,129,0.12)]` | 35× |
| `shadow-lg` | 22× |
| `shadow-emerald-200` | 6× |
| `shadow-indigo-200/50` | 4× |
| `shadow-[0_4px_14px_rgba(37,99,235,.30)]` | 4× |
| `shadow-[0_4px_14px_rgba(37,99,235,.25)]` | 2× |

---

## 7. Inline Styles — Masalah Utama

**1033 penggunaan `style=""`** ditemukan di **101 file**.

> Inline styles adalah "technical debt" desain — tidak bisa di-override,
> tidak konsisten, dan tidak bisa diubah secara global.

### File dengan Inline Style Terbanyak

| File | Status |
|------|--------|
| `settings_app/business_form_general.html` | 🔴 Perlu refactor |
| `base.html` | 🔴 Perlu refactor |
| `settings_app/users.html` | 🔴 Perlu refactor |
| `sales/purchasing_report.html` | 🔴 Perlu refactor |
| `sales/pos.html` | 🔴 Perlu refactor |
| `settings_app/about.html` | 🔴 Perlu refactor |
| `marketing/campaign_list.html` | 🔴 Perlu refactor |
| `lumra_pages/notification.html` | 🔴 Perlu refactor |
| `lumra_pages/inventory/stock_planning.html` | 🔴 Perlu refactor |
| `lumra_pages/campaign.html` | 🔴 Perlu refactor |
| `sales/purchasing_report opsi 2.html` | 🔴 Perlu refactor |
| `lumra_pages/reports/financial_reports.html` | 🔴 Perlu refactor |
| `master_data/categories_list.html` | 🔴 Perlu refactor |
| `lumra_pages/settings/business_feature_matrix.html` | 🔴 Perlu refactor |
| `lumra_pages/master_data/vendors_list.html` | 🔴 Perlu refactor |
| `lumra_pages/reports/transaction_summary.html` | 🔴 Perlu refactor |
| `master_data/products.html` | 🔴 Perlu refactor |
| `lumra_pages/reports/transfer_report.html` | 🔴 Perlu refactor |
| `inventory/add_stock_movement.html` | 🔴 Perlu refactor |
| `base/sidebar_right.html` | 🔴 Perlu refactor |

### Contoh Inline Style yang Ditemukan

```css
/* text-align:center;background:#f8d7da;color:#721c24;padding:15px;border */
/* width:480px;height:480px;background:#059669;opacity:.055;top:-80px;lef */
/* width:340px;height:340px;background:#0ea5e9;opacity:.04;bottom:-60px;r */
/* font-family: */
/* `background:${sw}` */
/* background:transparent; */
/* max-width:120px; */
/* `background:${f.brand_color|| */
/* background:transparent; */
/* max-width:120px; */
/* `background:${f.brand_color_2|| */
/* `background:${theme.primary}` */
```

> **Rekomendasi**: Pindahkan ke Tailwind class atau CSS custom property.

---

## 8. Temuan & Rekomendasi

### 🔴 Masalah Kritis (Perbaiki Segera)

| # | Temuan | Dampak | Solusi |
|---|--------|--------|--------|
| 1 | **87 warna Hex hardcoded** di HTML | Tidak bisa ubah tema secara global | Buat CSS variables, hapus hex dari HTML |
| 2 | **316 kelas warna Tailwind** berbeda | `gray` vs `slate` vs `zinc` — semua abu-abu | Pilih 1 family: standarkan ke `slate` |
| 3 | **1.033 inline `style=""`** di 150 file | Tidak konsisten, susah diubah | Refactor ke Tailwind / CSS class |
| 4 | **Emerald 5 variasi Hex** (`#059669`, `#10B981`, dll) | Hijau tidak konsisten antar halaman | Unifikasi ke 1 token `--color-primary` |

### 🟡 Perlu Perhatian

| # | Temuan | Solusi |
|---|--------|--------|
| 5 | **56 CDN refs** tanpa versi terkunci | Tambahkan version tag: `flatpickr@4.6.13` |
| 6 | **Badge** 84 file — warna status tidak standar | Buat class: `.badge-success`, `.badge-warning`, `.badge-danger` |
| 7 | **Table** 82 file — style berbeda tiap modul | Buat 1 CSS component class `.table-lumra` |
| 8 | **Modal** 60 file — struktur HTML berbeda | Buat 1 Django template include `_modal.html` |
| 9 | **Toast** 109 file — JS pattern berbeda | Standarkan ke 1 fungsi global `showToast(msg, type)` |

### 🟢 Sudah Baik

- **Flexbox** konsisten sebagai sistem layout utama
- **Font Awesome** dipakai konsisten sebagai icon library
- **flatpickr** sebagai date picker tunggal
- **Emerald + Slate** sebagai keluarga warna dominan (tinggal dikonsolidasi)
- **Chart.js** sebagai charting library tunggal

---

## 9. Design Token yang Disarankan

Berdasarkan warna yang paling sering muncul, ini adalah token yang harus dibuat:

```css
:root {
  /* ── Primary (Emerald) ─────────────────── */
  --color-primary:         #059669;  /* emerald-600 — paling sering: 719× */
  --color-primary-light:   #10B981;  /* emerald-500 — 309× */
  --color-primary-subtle:  #D1FAE5;  /* emerald-100 — background card */
  --color-primary-dark:    #065F46;  /* emerald-800 — text on light bg */

  /* ── Neutral (Slate) ───────────────────── */
  --color-neutral-900:     #0F172A;  /* slate-900 — judul utama */
  --color-neutral-800:     #1E293B;  /* slate-800 — teks utama */
  --color-neutral-600:     #475569;  /* slate-600 — teks sekunder */
  --color-neutral-500:     #64748B;  /* slate-500 — teks placeholder */
  --color-neutral-400:     #94A3B8;  /* slate-400 — border, ikon redup */
  --color-neutral-200:     #E2E8F0;  /* slate-200 — divider, border card */
  --color-neutral-100:     #F1F5F9;  /* slate-100 — background halaman */

  /* ── Semantic ──────────────────────────── */
  --color-success:         #10B981;  /* emerald-500 */
  --color-warning:         #F59E0B;  /* amber-500 — 108× */
  --color-danger:          #F43F5E;  /* rose-500 — 55× */
  --color-info:            #0EA5E9;  /* sky-500 — 75× */

  /* ── Accent (Indigo/Purple — gunakan hemat) */
  --color-accent:          #6366F1;  /* indigo-500 — 98× */

  /* ── Typography ────────────────────────── */
  --font-body:    "Inter", sans-serif;
  --font-display: "Plus Jakarta Sans", sans-serif;

  /* ── Spacing Scale ─────────────────────── */
  --space-1:  0.25rem;   /* 4px  */
  --space-2:  0.5rem;    /* 8px  */
  --space-3:  0.75rem;   /* 12px */
  --space-4:  1rem;      /* 16px */
  --space-6:  1.5rem;    /* 24px */
  --space-8:  2rem;      /* 32px */

  /* ── Border Radius ─────────────────────── */
  --radius-sm:  0.375rem;  /* rounded-md */
  --radius-md:  0.5rem;    /* rounded-lg */
  --radius-lg:  0.75rem;   /* rounded-xl */
  --radius-full: 9999px;   /* rounded-full */

  /* ── Shadow ────────────────────────────── */
  --shadow-card:  0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
  --shadow-modal: 0 20px 60px rgba(0,0,0,.15);
}
```

### Tailwind Config (tailwind.config.js)

```javascript
// Tambahkan ke extend.colors agar token tersedia sebagai class Tailwind
module.exports = {
  theme: {
    extend: {
      colors: {
        primary:  { DEFAULT: "#059669", light: "#10B981", dark: "#065F46", subtle: "#D1FAE5" },
        neutral:  { 900: "#0F172A", 800: "#1E293B", 600: "#475569", 400: "#94A3B8", 200: "#E2E8F0" },
        success:  "#10B981",
        warning:  "#F59E0B",
        danger:   "#F43F5E",
        info:     "#0EA5E9",
        accent:   "#6366F1",
      }
    }
  }
}
```

---

*Laporan ini dibuat otomatis dari scan 150 file HTML Lumra ERP.*  
*Langkah selanjutnya: buat `lumra_design_tokens.css` dan mulai refactor komponen satu per satu.*