# Alur Scheduling R&D ke Produksi - Rekap Penyesuaian
**Sistem: CoffeeShop / Lumra ERP**
**Disusun berdasarkan konsolidasi catatan:** `batch1_rnd.md`, `batch2_bom.md`, `batch3_recipe.md`, `batch4_production_order.md`, `batch5_operations_masterlist.md`

Dokumen ini merangkum alur **R&D -> BOM -> Recipe -> Production Order -> Operasional Produksi** dalam format yang lebih selaras dengan dokumen batch: bukan hanya narasi proses, tetapi juga **titik kontrol, gap sistem, prioritas perbaikan, dan urutan implementasi**.

---

# TUJUAN DOKUMEN

Dokumen ini dipakai sebagai:

1. **Rekap alur bisnis end-to-end** dari ide formula sampai barang jadi masuk stok.
2. **Peta titik rawan** yang saat ini berpotensi menimbulkan data tidak sinkron, alur tersumbat, atau kesalahan operasional.
3. **Panduan prioritas pengerjaan** agar penyesuaian antar modul tetap konsisten.

---

# GAMBARAN BESAR ALUR

Secara bisnis, sistem ini terbagi menjadi dua zona besar:

- **Zona fleksibel: R&D**
  Fokus pada eksperimen formula, trial berulang, evaluasi rasa, dan keputusan apakah formula layak dilanjutkan.
- **Zona tetap: Produksi**
  Fokus pada standar material, instruksi teknis, pembuatan SPK, penjadwalan, eksekusi, konsumsi bahan, waste, receipt, dan costing.

Titik transisi resmi di antara keduanya adalah:

**R&D Approved -> Promote ke BOM**

Tanpa status `approved`, formula tidak boleh masuk ke standar produksi.

---

# RINGKASAN ALUR IDEAL

```text
[1] R&D Formula
    idea -> in_trial -> review -> approved
        |
        v
[2] Promote ke BOM
    trial terbaik dikonversi menjadi BOM resmi
        |
        v
[3] BOM
    verifikasi material, struktur biaya, versi, dan kesiapan stok
        |
        v
[4] Recipe
    lengkapi instruksi teknis, preparation time, yield, dan hubungan ke BOM
        |
        v
[5] Production Order / SPK
    pilih BOM, tentukan qty, line, tanggal, prioritas, operator
        |
        v
[6] Production Scheduling
    order tampil di kalender dan dipantau per tanggal
        |
        v
[7] Production Execution
    start -> in_progress -> completed
        |
        v
[8] Material Consumption
    catat bahan aktual terpakai dan bandingkan vs standar BOM
        |
        +--> [8b] Production Waste
        |
        v
[9] Finished Goods Receipt
    barang jadi diterima ke stok/lokasi
        |
        v
[10] Production Costing
     analisis biaya aktual vs standar, completion rate, dan variance
```

---

# PETA ALUR DAN TITIK KONTROL

## 1. R&D

**Status utama:** `idea`, `in_trial`, `review`, `approved`

**Tujuan fase:**
- Membuat formula awal
- Menjalankan trial berulang
- Membandingkan hipotesis vs hasil aktual
- Menentukan trial terbaik
- Menyelesaikan gate approval

**Titik kontrol yang harus benar:**
- Status yang disimpan harus valid
- Trial minimal harus punya bahan yang layak
- Perubahan status harus aman, terutama setelah formula dipromote
- Tautan aksi penting tidak boleh hardcoded

**Catatan penyesuaian utama dari Batch 1:**
- `saveRnD('draft')` perlu disejajarkan ke status valid sistem
- Tombol aksi di form R&D harus disederhanakan agar tidak membingungkan
- Status formula yang sudah dipromote perlu diberi penanda visual
- Halaman detail perlu lebih aman terhadap downgrade status setelah promote

---

## 2. Gate Transisi: Promote ke BOM

**Trigger resmi:** hanya saat formula `approved`

**Tujuan fase:**
- Mengambil komposisi trial terbaik
- Membentuk BOM resmi produksi
- Menautkan entitas R&D dengan BOM hasil promote

**Titik kontrol yang harus benar:**
- Tombol promote hanya aktif saat status tepat
- URL action tidak boleh hardcoded
- Hasil promote harus bisa ditelusuri balik ke formula asal

**Catatan penyesuaian utama:**
- Relasi `R&D <-> BOM` harus terlihat jelas di UI
- Setelah promote, pengguna idealnya diarahkan ke detail BOM atau detail formula dengan status terbaru

---

## 3. BOM

**Tujuan fase:**
- Menetapkan standar bahan
- Menentukan struktur biaya material
- Menyediakan dasar perhitungan SPK
- Menjaga versi BOM tetap terkontrol

**Titik kontrol yang harus benar:**
- BOM hasil promote harus dibedakan dari BOM manual
- Edit BOM tidak boleh menghilangkan histori versi
- SKU bahan yang invalid tidak boleh dibuang diam-diam
- Yield dan UOM harus tersimpan penuh

**Catatan penyesuaian utama dari Batch 2:**
- Form BOM perlu mode edit yang jelas
- Versioning wajib dipikirkan saat komposisi berubah
- Auto-sync harga per SKU perlu ada agar biaya material tidak selalu nol
- Detail BOM perlu aksi header yang benar-benar berfungsi

---

## 4. Recipe

**Tujuan fase:**
- Menyimpan panduan teknis pembuatan
- Menambahkan instruksi langkah kerja
- Menyimpan preparation time dan yield
- Menjadi jembatan operasional teknis ke produksi

**Titik kontrol yang harus benar:**
- Template harus valid secara Django
- Instruksi pembuatan harus bisa diinput
- Yield dan preparation time harus tersedia
- Relasi recipe ke BOM harus eksplisit

**Catatan penyesuaian utama dari Batch 3:**
- File recipe saat ini masih punya masalah template dasar yang fatal
- Form recipe belum menampung field teknis inti
- Detail recipe perlu fallback data yang aman dan tautan ke BOM terkait

---

## 5. Production Order / SPK

**Tujuan fase:**
- Menentukan order produksi resmi
- Mengikat BOM ke target qty, line, tanggal, dan prioritas
- Menjadi titik awal scheduling dan shop floor control

**Titik kontrol yang harus benar:**
- Data PO harus dimapping eksplisit dari server
- Kode PO tidak boleh dibentuk secara acak di client
- Tombol submit harus aman dari double submission
- Material shortage harus benar-benar berbasis stok aktual

**Catatan penyesuaian utama dari Batch 4:**
- `Math.random()` untuk kode PO harus dihilangkan
- Form SPK perlu loading state dan default line yang aman
- List PO perlu guard terhadap progress `NaN%`
- Filter status perlu mencakup `on_hold`

---

## 6. Production Scheduling

**Tujuan fase:**
- Memvisualisasikan order terjadwal
- Memudahkan planner membaca beban kerja per tanggal

**Titik kontrol yang harus benar:**
- `scheduled_date` harus dinormalisasi
- Statistik harus menghitung bulan aktif, bukan seluruh data
- Hari ini dan qty target perlu terlihat jelas di kalender

**Catatan penyesuaian utama:**
- Scheduling saat ini berisiko kosong jika format tanggal dari server tidak cocok
- Kalender perlu lebih informatif untuk keputusan operasional harian

---

## 7. Production Execution

**Tujuan fase:**
- Mengontrol proses mulai, pause, update qty, dan selesai
- Menyimpan waktu aktual dan output produksi

**Titik kontrol yang harus benar:**
- Semua aksi harus tersimpan ke server
- Completion harus punya konfirmasi final
- Operator harus melihat daftar bahan yang dibutuhkan
- Data waktu aktual tidak boleh hanya berupa jam tanpa tanggal

**Catatan penyesuaian utama dari Batch 4:**
- Ini adalah titik paling kritis karena kontrol produksi saat ini baru mengubah state lokal
- Tanpa persist ke server, seluruh kontrol shop floor belum bisa dianggap siap pakai

---

## 8. Material Consumption

**Tujuan fase:**
- Mencatat bahan aktual yang terpakai
- Membandingkan aktual vs standar BOM
- Menjadi dasar costing material aktual

**Titik kontrol yang harus benar:**
- Harus ada form input, bukan hanya list
- Hanya PO `completed` yang boleh dicatat
- Harus ada indikator PO mana yang sudah dan belum dicatat

**Catatan penyesuaian utama dari Batch 5:**
- Alur pasca produksi saat ini tersumbat karena halaman ini belum menyediakan mekanisme input baru

---

## 9. Production Waste

**Tujuan fase:**
- Mencatat bahan terbuang, scrap, spoilage, rework, dan kerugian proses

**Titik kontrol yang harus benar:**
- Harus ada form input waste
- Tipe waste harus distandardisasi
- Nilai kerugian perlu dihitung

**Catatan penyesuaian utama dari Batch 5:**
- Waste belum bisa dicatat secara nyata
- Tanpa nilai kerugian, management kehilangan data penting untuk evaluasi efisiensi

---

## 10. Finished Goods Receipt

**Tujuan fase:**
- Menerima barang jadi ke stok/lokasi penyimpanan
- Menutup loop produksi secara inventory

**Titik kontrol yang harus benar:**
- Harus ada form input receipt
- Hanya PO selesai yang boleh diterima
- Variance antara produced vs received harus terlihat

**Catatan penyesuaian utama dari Batch 5:**
- Saat ini barang jadi belum punya jalur input formal ke stok, sehingga alur produksi belum benar-benar selesai

---

## 11. Production Costing

**Tujuan fase:**
- Menghitung biaya aktual produksi
- Membandingkan biaya standar vs aktual
- Menampilkan variance dan completion yang bermakna

**Titik kontrol yang harus benar:**
- Halaman costing harus benar-benar memuat data biaya
- Completion rate harus dibaca dengan definisi yang tepat
- Tanggal dan export data perlu tersedia

**Catatan penyesuaian utama dari Batch 5:**
- Halaman ini masih berupa overview ringan, belum costing sesungguhnya

---

# TEMUAN PRIORITAS PER ALUR

## `KRITIS` - Wajib dibereskan agar alur end-to-end bisa dipakai

1. **Kontrol produksi belum persist ke server**
   `production_order_detail` saat ini hanya mengubah state lokal untuk start, pause, complete, dan update qty.

2. **Tiga modul pasca-produksi masih read-only**
   `material_consumption`, `production_waste`, dan `finished_goods_receipt` belum punya form input baru.

3. **Halaman costing belum melakukan costing**
   `production_costing` belum menampilkan biaya aktual maupun variance.

4. **Beberapa template recipe masih bermasalah di level struktur**
   `recipe_list` dan `recipe_form` masih mengandung masalah `extends` dan atribut HTML rusak.

5. **Beberapa aksi utama masih memakai URL hardcoded**
   Terutama pada detail R&D dan titik-titik yang sensitif terhadap perubahan route.

6. **Identitas dokumen transaksi produksi belum aman**
   Kode PO masih berbasis random client-side dan berisiko duplikat.

---

## `PENTING` - Harus masuk sprint stabilisasi pertama

1. BOM perlu mode edit, versioning, validasi SKU, dan payload yield yang lengkap.
2. R&D form perlu konsistensi tombol aksi dan validasi bahan minimal untuk `in_trial`.
3. Recipe form perlu field instruksi, yield, dan preparation time.
4. PO list dan scheduling perlu normalisasi data agar aman dibaca planner.
5. Material consumption perlu perbandingan aktual vs standar BOM.
6. Waste perlu enum tipe yang baku dan kalkulasi nilai kerugian.
7. Finished goods receipt perlu pembacaan variance produced vs received.

---

## `DISARANKAN` - Backlog peningkatan kualitas operasional

1. Tambah penanda visual formula/BOM yang sudah promoted.
2. Tambah indikator overdue di daftar PO.
3. Tambah pagination dan filter line pada list PO.
4. Tambah tautan silang antar modul: R&D -> BOM -> Recipe -> PO.
5. Tambah export CSV/Excel pada costing dan laporan operasional.
6. Rapikan bahasa UI agar konsisten Bahasa Indonesia.

---

# TABEL REKAP ALUR VS STATUS KESIAPAN

| Tahap | Fungsi Bisnis | Kondisi Saat Ini | Status |
|---|---|---|---|
| R&D Formula | Eksperimen dan approval formula | Sudah terbentuk, tapi masih ada inkonsistensi aksi/status | `Perlu penyesuaian` |
| Promote ke BOM | Gate resmi ke produksi | Sudah ada, perlu penguatan traceability dan route | `Cukup siap` |
| BOM | Standar bahan dan biaya | Struktur sudah ada, edit/versioning belum matang | `Perlu penyesuaian` |
| Recipe | Instruksi teknis produksi | Masih ada gap template dan field inti | `Belum stabil` |
| Production Order | Pembuatan SPK | Sudah ada, tapi masih ada risiko kode dan submit ganda | `Perlu penyesuaian` |
| Scheduling | Kalender produksi | Sudah ada, perlu normalisasi tanggal dan perbaikan statistik | `Perlu penyesuaian` |
| Execution | Kontrol lantai produksi | Aksi inti belum tersimpan ke server | `Kritis` |
| Material Consumption | Catat bahan aktual | Belum ada mekanisme input | `Kritis` |
| Production Waste | Catat waste produksi | Belum ada mekanisme input | `Kritis` |
| Finished Goods Receipt | Barang jadi masuk stok | Belum ada mekanisme input | `Kritis` |
| Production Costing | Analisis biaya produksi | Masih placeholder | `Kritis` |

---

# URUTAN PENGERJAAN YANG DISARANKAN

## Tahap 1 - Membuka jalur transaksi inti

1. Perbaiki `production_order_detail` agar semua aksi sync ke server.
2. Tambahkan form input pada:
   - `material_consumption`
   - `production_waste`
   - `finished_goods_receipt`
3. Ubah `production_costing` minimal menjadi analisis yang benar, atau turunkan dulu menjadi overview jika costing belum siap.

## Tahap 2 - Menstabilkan hulu ke tengah

1. Rapikan `rnd_form` dan `rnd_detail`.
2. Perkuat relasi dan traceability `R&D -> BOM`.
3. Tambahkan mode edit, versioning, dan validasi kuat pada `bom_form`.
4. Perbaiki file recipe yang masih bermasalah secara template dan field.

## Tahap 3 - Menstabilkan perencanaan produksi

1. Perbaiki `production_order_form`:
   - kode PO dari server
   - loading state
   - line default
   - operator assignment
2. Perbaiki `production_order_list`:
   - mapping data eksplisit
   - guard progress
   - filter `on_hold`
   - indikator overdue
3. Perbaiki `production_scheduling`:
   - normalisasi tanggal
   - stats bulan aktif
   - highlight hari ini

## Tahap 4 - Penyempurnaan UX dan auditability

1. Tambah penanda status visual lintas modul.
2. Tambah tautan silang antar dokumen terkait.
3. Tambah export laporan.
4. Tambah riwayat perubahan status / audit log di titik penting.

---

# KESIMPULAN

Setelah diselaraskan dengan dokumen `batch1` sampai `batch5`, terlihat bahwa alur **R&D ke Produksi di Lumra sudah punya bentuk bisnis yang jelas**, tetapi **belum seluruhnya siap secara operasional** karena masih ada beberapa titik kritis:

- transaksi lantai produksi belum tersimpan ke server,
- tiga modul pasca-produksi belum bisa menerima input,
- costing belum benar-benar berjalan,
- dan beberapa modul hulu masih membutuhkan penguatan struktur data serta konsistensi UI.

Dengan kata lain:

- **alur bisnisnya sudah terbaca,**
- **alur sistemnya sudah setengah terbentuk,**
- tetapi **alur transaksinya belum utuh sampai inventory dan costing.**

Dokumen ini sebaiknya dipakai sebagai **rekap induk**, sementara rincian teknis tetap mengacu ke:

- `batch1_rnd.md`
- `batch2_bom.md`
- `batch3_recipe.md`
- `batch4_production_order.md`
- `batch5_operations_masterlist.md`

---

*Dokumen ini adalah versi rekap yang sudah diselaraskan dengan format catatan batch: lebih fokus pada titik kontrol, gap sistem, prioritas, dan urutan pengerjaan dibanding narasi deskriptif panjang.*
