LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

LUMRA ERP
Emerald Odyssey
Blueprint Arsitektur, Desain & Legacy
"You use other ERPs to run a business.
You use Lumra when you are building an empire."
Versi 3.0 · 2026 · Konfidensial
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 01

Manifesto & Filosofi
Sebelum satu baris kode ditulis, sebelum satu warna dipilih — ada keyakinan yang

harus dikunci. Ini bukan dokumen teknis biasa. Ini adalah konstitusi dari sebuah

produk yang lahir untuk memimpin.

Pernyataan Identitas
Lumra ERP bukan sebuah software manajemen. Ia adalah infrastruktur bagi mereka

yang sedang membangun sesuatu yang lebih besar dari diri mereka sendiri. ERP lain

dibangun untuk membuat bisnis berjalan. Lumra dibangun untuk memastikan empire

berkembang — dengan kecepatan, kejelasan, dan keindahan yang tidak bisa

ditemukan di tempat lain.

“You use other ERPs to run a business. You use Lumra when
you are building an empire.”
Seperti Lamborghini yang tidak pernah bersaing dengan Ferrari berdasarkan

spesifikasi mesin — melainkan berdasarkan identitas dan status — Lumra tidak

bersaing dengan SAP atau Odoo berdasarkan jumlah fitur. Lumra bersaing

berdasarkan rasa, estetika, dan filosofi yang tertanam di setiap pixel-nya.

Empat Pilar Pembangun
PILAR 01
Steve Jobs ·
Perfeksionisme
Kemewahan bukan
tentang apa yang
terlihat, tapi tentang
apa yang tidak
terlihat. Setiap
elemen — dari
spacing 8px hingga
shadow 4 lapis —
harus sempurna,
bahkan jika
PILAR 02
Lamborghini ·
Arogansi Elegan
Bukan sombong
tanpa substansi —
tapi keyakinan
penuh bahwa produk
ini memang
berbeda.
Tampilannya yang
berkelas bukan
pencitraan. Ia adalah
cerminan standar
PILAR 03
Meta ·
Ekosistem Masif
Semua modul Lumra
harus mengalir satu
sama lain. Data
bergerak, bukan
disinkronisasi.
Konteks selalu ada,
tanpa perpindahan
halaman.
PILAR 04
Legacy ·
Warisan Abadi
Produk yang
dibangun dengan
standar ini tidak
akan usang dalam
lima tahun. Ia akan
menjadi referensi —
titik perbandingan
yang digunakan
orang lain ketika
membangun sistem
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

pengguna tidak
menyadarinya.
Terutama karena
pengguna tidak
menyadarinya.
yang tidak pernah
dikompromikan sejak
hari pertama.
serupa.
The Lumra Statement
KEPADA PERNYATAAN
Pengguna
Aplikasi lain membuat Anda bekerja untuk sistem. Lumra
membuat sistem bekerja untuk kejayaan Anda.
Investor Ini bukan SaaS biasa. Ini infrastruktur untuk generasi pengusaha
berikutnya.
Kompetitor Kami tidak bersaing di fitur. Kami bersaing di standar.
Tim Produk Jika ada satu pixel yang salah, itu belum selesai.
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 02

Emerald Odyssey Design System
Sistem desain bukan kumpulan warna dan font. Ia adalah bahasa visual yang

digunakan seluruh tim untuk berkomunikasi tanpa ambiguitas. Setiap keputusan di

sini bukan preferensi — ia adalah standar.

Fondasi Warna — Emerald Odyssey Palette
Lima warna ini bukan dipilih secara estetis semata. Masing-masing memiliki peran

fungsional yang tidak boleh dilanggar. Konsistensi palette adalah yang membedakan

produk premium dari produk generik.

PERAN HEX NAMA
PENGGUNAAN
UTAMA
HINDARI
Primary #00674F
Base
Emerald
Sidebar, branding,
border utama,
identity mark
Teks body panjang
Secondary #00A86B Jade Accent
Tombol sukses,
badge aktif, chart
fill, nav highlight
Background area
besar
Accent #EFBF04 Odyssey
Gold
Rating, border
premium, KPI
highlight, Tier Gold
Teks panjang
(kontras rendah)
Neutral #FDFBD4 Ivory Cream
Zebra row odd, off-
white background
alternatif
Tombol atau elemen
dark
Contrast #000080 Deep Navy
Heading berat, Tier
Platinum, elemen
authority
Area luas tanpa
opacity
Warna Semantik — Aligned to Odyssey

Status warna harus selalu selaras dengan palette Emerald. Merah biasa tidak pernah

muncul sendiri — ia selalu digabung dengan Navy untuk mempertahankan karakter

Odyssey.

STATUS IMPLEMENTASI CSS VARIABLE CATATAN
Sukses rgba(0,168,107,.15) --color-secondary- Stok aman, approval
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

+ border jade a15 diterima, order selesai
Warning
rgba(239,191,4,.15)
+ border gold --color-accent-a
Review diperlukan, stok
menengah, draft
Kritis/
Danger
gradient(#A32D2D
→ #000080)
--color-danger-
odyssey
JANGAN pakai merah polos
— harus ke navy
Info rgba(0,0,128,.08) +
border navy
--color-contrast-a10 Draft status, informasi
netral
The Glass Protocol
Setiap komponen card dan panel di Lumra menggunakan Glass Protocol — kombinasi

frosted edge, natural shadow berlapis, dan backdrop blur yang menciptakan kesan

material premium. Glass Protocol adalah identitas visual yang tidak bisa disingkat

atau disederhanakan. Tidak ada versi setengah.

ELEMEN NILAI CSS ALASAN DESAIN
Frosted
Edge
border: 0.5px solid
rgba(255,255,255,0.10)
border-top: rgba(255,255,255,0.25)
border-left: rgba(255,255,255,0.20)
Mensimulasikan pantulan cahaya
dari atas dan kiri. Tanpa ini, card
terasa seperti kotak biasa, bukan
material kaca premium.
Natural
Shadow
0 1px 3px rgba(0,0,0,.08)
0 4px 12px rgba(0,0,0,.06)
0 8px 24px rgba(0,0,0,.04)
0 16px 48px rgba(0,0,0,.03)
4 lapis bayangan makin memudar.
Satu shadow = murah. Empat
shadow = premium. Tidak bisa
dikurangi.
Backdrop
Blur
backdrop-filter: blur(12px)
/* max panel utama: blur(20px) */
Min 12px untuk efek frosted glass
yang terasa. Di bawah 12px tidak
ada efeknya secara visual.
Backgroun
d Tint
background: rgba(0,103,79,.08)
/* emerald glass tint */
Tint tipis sesuai warna parent.
Tidak pernah solid putih polos — itu
membunuh karakter Odyssey.
Kelas CSS Wajib — .kpi-glass

.kpi-glass {
background: rgba(0,103,79,.08);
border: 0.5px solid rgba(255,255,255,0.10);
border-top-color: rgba(255,255,255,0.25);
border-left-color: rgba(255,255,255,0.20);
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

backdrop-filter: blur(12px);
box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.06),
0 8px 24px rgba(0,0,0,.04), 0 16px 48px rgba(0,0,0,.03);
border-radius: 14px; padding: 16px;
transition: transform 200ms ease, box-shadow 200ms ease;
}
.kpi-glass:hover {
transform: translateY(-2px);
box-shadow: 0 4px 16px rgba(0,103,79,.20), 0 8px 24px rgba(0,0,0,.06);
}
Tipografi & Hierarki
Plus Jakarta Sans dipilih karena karakternya yang geometris-modern — terasa

profesional tanpa steril. Semua angka menggunakan font-variant: tabular-nums

sehingga kolom tabel selalu sejajar sempurna secara vertikal.

LEVEL UKURAN WEIGHT PENGGUNAAN
H1 / Page Title 28px 600
Judul halaman utama (dashboard, stock
overview)
H2 / Section Title 22px 600 Sub-judul section dalam halaman
H3 / Card Title 16px 500 Judul KPI card, panel, widget
Body / Description 14px 400 Teks deskripsi, keterangan, body
paragraph
Table / Form 13px 400 Sel tabel, input form, meta info
Label / Badge 11px 500 Badge status, label field, tag uppercase
KPI Number 28–36px 600
Angka metrik besar di dashboard —
tabular-nums wajib
Code / Monospace 13px 400
SKU, ID, nilai teknis — JetBrains Mono
atau Fira Code
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 03

Arsitektur Sistem
Lumra ERP dibangun di atas Django dengan arsitektur modular yang bersih. Total

115 URL aktif, 25 model database, 102 template — semua harus beroperasi sebagai

satu organisme yang kohesif.

Stack Teknologi
KOMPONEN TEKNOLOGI CATATAN
Framework Django (Python)
Arsitektur MVT, lazy_view() untuk
menghindari circular import
Database PostgreSQL 25 model aktif, app label: lumra_config
Frontend Tailwind CSS +
HTML
Django Template Engine, Plus Jakarta Sans,
Chart.js
CSS Engine lumra_design_syste
m.css
Single source of styling truth — tidak ada
inline CSS di template
Auth Django Auth +
Middleware
EnsureUserProfileMiddleware — setiap user
punya profil
Templates 102 file HTML 81 punya inline CSS — target: pindah
semua ke design system
25 Model Database Utama
MODEL TABEL DATABASE FUNGSI UTAMA
Category _categories Kategori produk
Vendor _vendors Data pemasok/vendor
Product lumra_config_products Master produk dengan FK ke
Category, Vendor, Tax, Unit
ProductVariant lumra_config_productvarian
ts
SKU, harga beli/jual per varian
Stock lumra_config_stock Stok per varian per lokasi
Location lumra_config_locations Lokasi / outlet / gudang
Customer lumra_config_customers
Pelanggan dengan tier & loyalty
points
Order lumra_config_orders Order transaksi
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

OrderItem lumra_config_orderitems Item dalam order
UserProfile lumra_config_userprofile Profil user + FK ke Location
StockOpnameSes
sion
lumra_config_stockopname_
session Sesi stock opname
Recipe production_recipes Resep produksi — SHARED tabel
(fake-initial)
SupplierPrice lumra_config_supplier_price
s
Harga supplier per produk
SalesTarget lumra_config_sales_targets Target penjualan per periode
Distribusi URL per Modul (115 URL Aktif)
MODUL JUMLAH URL CAKUPAN FUNGSIONAL
Sales & POS ~18 URL
Dashboard, POS, Sales Intelligence,
Performance
Inventory ~22 URL
Produk, Stok, Stock Opname, Transfer,
Requisition
Master Data ~20 URL Customer, Vendor, Lokasi, Kategori, Unit
Production ~8 URL Recipe list, form, detail, delete
Marketing ~12 URL Campaign, Discount, Loyalty Members
Reports & Insights ~14 URL Financial, Market, Trends, Activity Log
Settings & Users ~12 URL Profile, Business, System Status, Roles
Authentication ~3 URL Login, Logout, Register
Internal API ~6 URL Products import, Purchase submit, Transfer
confirm
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 04

Komponen & UI Standards
Komponen adalah atom penyusun setiap halaman. Standar ini memastikan bahwa

KPI card di dashboard terlihat identik dengan KPI card di inventory — karena

keduanya menggunakan resep yang sama. Tidak ada pengecualian.

Sidebar & Navbar — Glass Protocol
ELEMEN KELAS CSS SPESIFIKASI
Sidebar container .sidebar-glass
background: rgba(0,103,79,.08), backdrop-
filter: blur(16px), width: 240px, collapsed:
64px
Nav item aktif .nav-item.active background: rgba(0,168,107,.15), border-
left: 3px solid #00A86B, color: #00674F
Nav item hover .nav-item:hover background: rgba(0,103,79,.08), transition:
200ms ease, TIDAK ADA border kiri
Sidebar collapse .sidebar-
glass.collapsed
width: 64px, transition: width 300ms ease,
hanya icon yang terlihat
Navbar .nav-glass
background: rgba(255,255,255,.85),
backdrop-filter: blur(12px), border-bottom:
0.5px rgba(0,103,79,.1)
Command input .cmd-input Rounded full, emerald focus ring: 0 0 0 3px
rgba(0,168,107,.2)
Tabel & Data Grid — Odyssey Standard
Tabel adalah jantung ERP. Di Lumra, tabel bukan sekadar baris data — ia adalah

pernyataan bahwa kita menghargai kejelasan dan kemewahan secara bersamaan.

Setiap tabel harus menggunakan kelas .tbl-odyssey.

ELEMEN SPESIFIKASI CSS ALASAN
Header row
.tbl-head { background:
#00674F; color: white; font-
size: 10px; letter-spacing:
0.08em; }
Emerald header memberi
otoritas visual yang tidak bisa
dikompromikan
Zebra odd tr:nth-child(odd) td
{ background:
Tint emerald sangat tipis —
bukan abu-abu biasa
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

rgba(0,103,79,.035); }
Zebra even
tr:nth-child(even) td
{ background: white; }
Kontras bersih terhadap zebra
odd
Row hover
tr:hover td { background:
rgba(0,103,79,.055); transition:
150ms; }
Lebih gelap dari zebra odd,
feedback hover yang clear
Stok kritis
.badge-critical { background:
linear-gradient(135deg,
rgba(163,45,45,.12),
rgba(0,0,128,.08)); }
JANGAN merah biasa —
gradient ke navy sesuai palette
Status & Badge System
BADGE BACKGROUND TEKS BORDER PENGGUNAAN
Aktif /
Sukses
rgba(0,168,107,.15) #00674F rgba(0,168,
07,.3)
Stok aman, order
selesai, user aktif
Perlu
Review
rgba(239,191,4,.15) #635200 rgba(239,
1,4,.4)
Stok menengah,
draft, pending
approval
Kritis gradient red→navy #A32D2D
rgba(163,45,
45,.2)
Stok kritis, error
sistem, overdue
Info rgba(0,0,128,.08) #
rgba(0,0,
,.2)
Draft campaign, info
netral
Tier
Platinum
#000080 solid #EFBF04 none
Customer tier
tertinggi — gold on
navy
Tier Gold #EFBF04 solid #000000 none
Customer tier kedua
— black on gold
Tier Silver #888888 solid #FFFFFF none Customer tier ketiga^
— white on gray
Verified #00674F solid #FDFBD4 none Vendor verified —
cream on emerald
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 05

The Invisible Grid — Sistem 8px
Jobs tidak berkompromi dengan satu pixel pun. Grid 8px adalah bahasa diam yang

otak manusia baca secara instinktif — ketika spacing konsisten, produk terasa bersih

dan berkelas. Ketika tidak, ia terasa amatir, bahkan jika desainnya indah.

Mengapa 8px — Bukan 7px atau 10px
8px adalah kelipatan dari sebagian besar ukuran layar modern (360, 375, 390, 412,

768, 1024, 1280, 1440px). Ini berarti elemen yang mengikuti grid 8px akan selalu

jatuh di pixel boundary yang bersih — tidak ada sub-pixel rendering yang membuat

elemen terlihat blur atau tidak tajam.

Selain itu, mata manusia memproses ukuran dalam rasio — bukan nilai absolut. Jarak

8px, 16px, 24px, 32px terasa proporsional secara alami karena mengikuti pola yang

otak kita kenali dari objek fisik di dunia nyata.

Aturan Grid per Komponen
KOMPONEN TINGGI
PADDING
H
PADDING V
GAP
INTERNAL
CATATAN
Tombol kecil 32px (4×8) 16px (2×8) 8px (1×8) 8px
Min touch
target
32px
Tombol normal 40px (5×8) 24px (3×8) 8px (1×8) 8px
Default
button
height
Tombol besar 48px (6×8) 32px (4×8) 12px 8px
CTA,
primary
action
Input field 40px (5×8) 16px (2×8) 8px (1×8) — Form input^
standar
Badge / pill 20px 12px 4px 6px
Boleh non-
8 karena
kompak
KPI Card min 96px 16px (2×8) 16px (2×8) 8px
Glass
Protocol
required
Sidebar item 40px (5×8) 16px (2×8) 8px (1×8) 8px Konsisten
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

semua nav
item
Tabel row 40px (5×8) 12px 8px (1×8) —
Tidak
boleh di
bawah
40px
Modal padding auto 24px (3×8) 24px (3×8) 16px
Breathing
room di
dalam
modal
Navbar height 56px (7×8) 24px (3×8) — 16px
Konsisten
di semua
halaman
Sidebar width 240px
(30×8)
— — 8px Collapsed:
64px (8×8)
Cara Audit Grid — Checklist Harian
Sebelum commit setiap file template, lakukan checklist ini. Jika ada nilai yang bukan

kelipatan 4px dan tidak ada alasan kuat, ia harus diperbaiki.

DevTools → Elements → Computed → periksa padding, margin, height, width, gap
— semua harus kelipatan 4px
Border-radius wajib konsisten: 4px (xs), 6px (sm), 8px (md), 10px (lg), 14px (xl),
100px (pill)
Line-height: selalu kelipatan font-size — 14px body = line-height 20px atau 24px
Jika spacing terasa tidak pas — percayai instink, lalu ukur. Pasti ada yang keliru.
Gunakan outline: 1px solid red pada elemen untuk melihat batas box
sesungguhnya
Min touch target 40px untuk semua elemen interaktif yang bisa diklik atau
disentuh
Pelanggaran Grid yang Sering Terjadi
PELANGGARAN KODE SALAH KODE BENAR DAMPAK
Padding tidak rata
padding: 10px
15px
padding: 8px
16px
Elemen tidak sejajar
dengan
tetangganya
Gap antar card gap: 14px gap: 16px (2×8)
Grid terasa tidak
berirama
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

Tinggi tombol height: 38px
height: 40px
(5×8)
Tombol terasa
gemuk atau tipis
Font tanpa line-height font-size: 14px font-size:14px;
lh:20px
Teks terlalu rapat
atau renggang
Margin section
margin-bottom:
20px
margin-bottom:
24px
Pemisahan section
tidak konsisten
Border-radius custom border-radius:
7px
var(--radius-md)
= 8px
Sudut tidak selaras
dengan komponen
lain
ATURAN EMAS
Jika spacing terasa sedikit aneh tapi sulit dijelaskan — itu adalah grid violation.
Kemewahan sejati adalah ketika tidak ada yang bisa menunjuk sesuatu yang salah,
tapi semua orang merasakan sesuatu yang benar.
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 06

Shimmer & Loading States
Pengguna tidak mengukur kecepatan dalam milidetik. Mereka mengukurnya dalam

perasaan. Shimmer yang dirancang dengan benar mengubah "menunggu" menjadi

"sedang diproses" — perbedaan psikologis yang sangat besar dan tidak bisa

diremehkan.

Tiga Tipe Loading State di Lumra
TIPE KAPAN DIGUNAKAN IMPLEMENTASI DURASI ANIMASI
Shimmer Card
Saat KPI card atau
list card sedang
fetch data dari API
CSS @keyframes
pada background-
position dengan
warna emerald +
gold glint
1.5s infinite —
cukup lambat untuk
tidak mengganggu
Skeleton Screen
Saat halaman
pertama kali dimuat
— sebelum konten
apapun tersedia
Placeholder abu-abu
berbentuk konten
asli (bukan spinner)
Tidak ada animasi
— placeholder statis
sudah cukup
Inline Spinner
Saat tombol diklik
dan menunggu
respons server
(submit form)
Spinner 16px
menggantikan ikon
atau label tombol
0.6s rotate infinite
— lebih cepat untuk
feedback segera
Progress Bar
Saat upload file atau
operasi batch yang
butuh waktu lama
Bar emerald di
bagian atas
halaman (top-loader
style)
Width dari 0% ke
100% dengan ease-
out
Kode CSS Lengkap — Shimmer Emerald dengan Gold
Glint
@keyframes lumra-shimmer {
0% { background-position: -200% center; }
100% { background-position: 200% center; }
}
.shimmer {
background: linear-gradient(
90deg,
rgba(0,103,79,.06) 0%,
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

rgba(0,168,107,.14) 40%, /* emerald peak */
rgba(239,191,4,.08) 60%, /* gold glint — karakter Odyssey */
rgba(0,103,79,.06) 100%
);
background-size: 200% auto;
animation: lumra-shimmer 1.5s ease-in-out infinite;
border-radius: var(--radius-md);
}
/* KPI Card dalam state loading */
.kpi-glass.is-loading .kpi-value,
.kpi-glass.is-loading .kpi-label {
color: transparent; pointer-events: none;
}
.kpi-glass.is-loading::after {
content: ""; position: absolute; inset: 0;
border-radius: inherit;
/* extend .shimmer — tambahkan class secara JS */
}
/* Skeleton baris tabel */
.skeleton-row td { padding: 10px 12px; }
.skeleton-cell { height: 12px; border-radius: var(--radius-sm); }
/* tambahkan class .shimmer pada .skeleton-cell */
/* Inline button spinner */
@keyframes lumra-spin { to { transform: rotate(360deg); } }
.btn-loading .btn-icon {
width: 14px; height: 14px;
border: 2px solid rgba(255,255,255,.3);
border-top-color: white; border-radius: 50%;
animation: lumra-spin 0.6s linear infinite;
}
Implementasi Django Template — Pola KPI Card
Saat halaman pertama kali dirender, tampilkan shimmer. JavaScript kemudian fetch

data via API dan replace shimmer dengan nilai asli. Ini adalah pola wajib untuk semua

KPI card di dashboard.

LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

{# Template: saat data belum tersedia, tambahkan class is-loading #}
<div class="kpi-glass {% if not value %}is-loading{% endif %}"
data-kpi="{{ kpi_id }}">
<p class="kpi-label">{{ label }}</p>
<h2 class="kpi-value">
{% if value %}{{ value|currency }}{% endif %}
</h2>
{% if trend %}<span class="badge-{{ trend_type }}">{{ trend }}</span>{% endif %}
</div>
// JavaScript: fetch dan update
document.querySelectorAll('[data-kpi]').forEach(async card => {
const id = card.dataset.kpi;
const data = await fetch(`/api/kpi/${id}/`).then(r => r.json());
card.querySelector('.kpi-value').textContent = data.value;
card.classList.remove('is-loading'); // hapus shimmer
card.classList.add('is-loaded'); // trigger fade-in
});
Psikologi Loading State — Lima Prinsip
PRINSIP PENJELASAN IMPLEMENTASI DI LUMRA
Berikan bentuk,
bukan
kekosongan
Otak lebih tenang melihat
placeholder berbentuk konten
daripada area kosong atau
spinner di tengah layar.
Skeleton screen berbentuk
layout card asli — bukan blok
abu-abu random
Gerak = aktivitas
Animasi shimmer memberi
sinyal "sedang bekerja" tanpa
mengganggu. Spinner solid
terasa lebih menegangkan.
Shimmer emerald lembut —
bukan spinner merah berputar
cepat
Jangan tunjukkan
progres palsu
Progress bar yang melambat di
90% lebih frustasi dari tidak
ada progress bar sama sekali.
Hanya gunakan progress bar
untuk operasi yang bisa diukur
(upload file)
Konsistensi
animasi
Semua elemen yang loading
harus beranimasi dengan
kecepatan yang sama.
Semua shimmer menggunakan
duration 1.5s — satu nilai,
berlaku global
Beri kontrol
kepada user
Jika loading lebih dari 5 detik,
tunjukkan opsi "Coba lagi" atau
estimasi waktu tunggu.
Error state dengan tombol retry
emerald — bukan halaman
kosong
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 07

Prinsip UX & Micro-interactions
Produk yang indah tapi lambat terasa murah. Produk yang cepat tapi jelek terasa

tidak profesional. Lumra harus keduanya — dan micro-interactions adalah yang

menjembatani persepsi kecepatan dengan keindahan.

Standar Transisi per Komponen
KOMPONEN PROPERTI
DURA
TION
EASING TRIGGER
Sidebar collapse width 300m
s
ease
Toggle
button /
hover
Modal masuk opacity + scale 250m
s
ease-out Tombol open
Modal keluar opacity + scale
200m
s ease-in
Close /
backdrop
click
Card hover translateY(-2px)
+ shadow
200m
s
ease Mouse enter
Button active scale(0.98) 150m
s
ease Mouse
down / touch
Nav item hover background-color 150m
s
ease Mouse enter
Drawer panel
transform:
translateX
300m
s
cubic-
bezier(.4,0,.2,1)
Activity
button
Toast / Alert
opacity +
translateY
250m
s ease-out Event trigger
Badge pulse opacity 2s ease-in-out infinite Status kritis
Progressive Reveal — Pola Wajib
Konten tidak boleh muncul semua sekaligus. Gunakan animation-delay bertahap

untuk memandu mata pengguna secara natural dari elemen terpenting ke elemen

pendukung.

LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

.reveal-item {
opacity: 0;
transform: translateY(8px);
animation: reveal 300ms ease forwards;
}
@keyframes reveal {
to { opacity: 1; transform: translateY(0); }
}
.reveal-item:nth-child(1) { animation-delay: 0ms; }
.reveal-item:nth-child(2) { animation-delay: 50ms; }
.reveal-item:nth-child(3) { animation-delay: 100ms; }
.reveal-item:nth-child(4) { animation-delay: 150ms; }
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 08

The Meta Ecosystem — Integrasi Tanpa
Batas
Meta tidak membangun Facebook, Instagram, dan WhatsApp secara terpisah. Mereka

membangun satu infrastruktur identitas dan data, lalu membangun pengalaman

berbeda di atasnya. Lumra mengadopsi filosofi yang sama: satu sumber data, banyak

modul, satu organisme.

Tiga Hukum Ekosistem
HUKUM 1 — Satu Definisi
Setiap entitas — produk, customer, lokasi, vendor — hanya didefinisikan di satu
tempat. Tidak pernah ada "produk di inventory" yang berbeda dengan "produk di
POS". Satu record, diakses dari manapun.
HUKUM 2 — Data Mengalir, Tidak Disinkronisasi
Sinkronisasi manual adalah tanda arsitektur yang buruk. Ketika stok berubah di
inventory, dashboard otomatis memperbarui. Ketika order dibuat di POS, stok
berkurang seketika. Zero lag, zero sync button.
HUKUM 3 — Konteks Selalu Hadir
User tidak pernah kehilangan konteks saat berpindah modul. Sidebar kanan
menampilkan aktivitas real-time. Approval modal bisa dipanggil dari halaman
manapun. Notifikasi muncul di navbar — bukan email.
Peta Ekosistem — Aliran Data Antar Modul
Semua modul membaca dari satu sumber — tidak ada duplikasi data. Master Data

adalah pusat gravitasi sistem. Setiap modul punya koneksi langsung ke pusat, dan

mengembalikan hasilnya ke sana.

TRIGGER MODUL ASAL DAMPAK OTOMATIS KE MODUL LAIN
Customer
checkout, bayar Sales / POS
Inventory: stok berkurang via signals.py |
Reports: revenue update | Customer:
total_spent bertambah, loyalty points
dihitung
Form di
master_data/prod
Master Data Inventory: produk muncul di stock list |
POS: produk bisa ditambah ke order |
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

ucts Reports: produk muncul di filter dropdown
Approval di
stock_opname
Inventory
Stock: quantity diperbarui | Reports:
inventory log tercatat | Dashboard: KPI stok
refresh
Status campaign
= active
Marketing
POS: diskon otomatis teraplikasi saat
checkout | Reports: campaign performance
tracking dimulai
Register +
UserProfile dibuat Auth / Settings
EnsureUserProfileMiddleware: profil
otomatis dibuat | Semua halaman:
user.profile.location tersedia sebagai filter
Contextual Intelligence — UI Level
Di level UI, ekosistem berarti pengguna tidak perlu berpindah halaman untuk

mengakses fungsi yang relevan. Tiga mekanisme utama yang harus ada di semua

halaman Lumra:

MEKANISME IMPLEMENTASI TEKNIS NILAI BAGI PENGGUNA
Sidebar Kanan
Real-time
sidebar_right.html dengan
activity_item — fetch via HTMX
atau polling setiap 30 detik
Selalu tahu apa yang terjadi di
sistem tanpa buka halaman lain
Approval Modal
Universal
approval_modal.html di-include
di base.html — trigger via data-
modal-trigger dari halaman
manapun
Approve transaksi dari halaman
inventory tanpa navigasi ke
halaman approval
Activity Drawer
activity_drawer.html slide dari
kanan — trigger dengan tombol
di navbar
Log aktivitas real-time tersedia
di semua halaman tanpa
navigasi
Command Bar
cmd-input dengan token:
product, location, stock —
search global yang memahami
konteks
Cari produk dari mana saja dan
langsung lompat ke detail
Contextual KPI
KPI card di dashboard
menggunakan data yang sama
dengan reports — satu query,
banyak tampilan
Angka di dashboard selalu
konsisten dengan laporan detail
Roadmap Integrasi — Lapisan Selanjutnya
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

INTEGRASI PRIORITAS NILAI BISNIS DEPENDENSI TEKNIS
REST API Publik Tinggi Partner bisa membangun^
aplikasi di atas Lumra
Django REST Framework
+ token auth sudah ada
di api/views.py
Webhook System Tinggi
Push notifikasi ke sistem
eksternal saat event
terjadi (order, stok kritis)
Model tambahan:
WebhookSubscription +
celery untuk async
delivery
Marketplace Sync
(Tokopedia/Shope
e)
Menengah
Stok dan pesanan dari
marketplace otomatis
masuk ke Lumra
API masing-masing
marketplace + mapping
SKU
AI Forecasting Menengah
Prediksi stok habis
sebelum terjadi,
rekomendasi reorder
Historical data sudah
ada di Stock model —
butuh ML layer
Mobile App (PWA) Rendah
Stock opname dan
approval via smartphone
di lapangan
Django sudah serve
HTML — tambahkan
service worker +
manifest
Multi-tenant Rendah
Satu Lumra, banyak
perusahaan — white
label untuk enterprise
Schema separation per
tenant atau row-level
tenancy
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 09

Roadmap 3 Gelombang
Eksekusi dilakukan dalam tiga gelombang berurutan. Gelombang 1 harus selesai dan

divalidasi sebelum Gelombang 2 dimulai. Satu file yang salah di Gelombang 1 akan

merusak 99 file lainnya. Urutan ini bukan saran — ia adalah hukum eksekusi.

Gelombang 1 — The Master Shell
Tiga file yang mengendalikan layout global. Jika ini salah, semua 102 halaman

terlihat berantakan.

FILE
PRIORIT
AS
TUGAS
base/base.html
CRITICA
L
Injeksi :root CSS variables, import font Plus
Jakarta Sans, setup layout shell. Semua 102
halaman extend file ini — perbaikan di sini
langsung berdampak ke semua.
base/sidebar.html
CRITICA
L
Standarisasi ke sidebar2.html dengan glass
protocol penuh. Nav item aktif harus emerald,
collapse transition 300ms ease.
base/navbar.html HIGH
nav-glass dengan backdrop-blur 12px, cmd-
input dengan emerald focus ring, token pills
untuk product/location/stock.
Gelombang 2 — The Core Components
Komponen kecil yang muncul di banyak halaman. Perbaiki sekali, semua halaman

ikut berkelas.

KOMPONEN
PRIORIT
AS
TUGAS
base/kpi_card.html
CRITICA
L
Konversi ke .kpi-glass — glass bg, frosted edge,
shadow 4 lapis. Gold highlight untuk metric
tertinggi. Tabular-nums untuk semua angka.
base/approval_modal.html HIGH
Modal overlay dengan stripe-new (emerald)
dan stripe-critical (red→navy). Animasi fade +
scale(0.97→1), duration 250ms.
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

base/activity_drawer.html HIGH
Drawer panel dengan backdrop blur, activity
dot warna konsisten (emerald=new,
amber=transit, red=critical). Transition slide
300ms.
base/alert.html MEDIUM
Alert inner dengan semantic color aligned —
gunakan versi Odyssey bukan warna Bootstrap
default.
Gelombang 3 — The Data Powerhouse
Halaman dengan data padat. Implementasi tema pada konten yang paling sering

dilihat user.

MODUL
PRIORIT
AS
TUGAS
lumra_pages/inventory/* HIGH
Tabel zebra emerald, badge stok kritis
red→navy, sortable header, stat-card glass,
amber-pulse untuk stok kritis. 8 file prioritas.
lumra_pages/sales_insight/* HIGH
Chart.js palette: #00A86B primer, #00674F
sekunder, #EFBF04 aksen. KPI card glass, perf-
strip emerald.
lumra_pages/master_data/* MEDIUM
Form card glass, tier badge system
platinum/gold/silver, customer profile section-
card, vendor badge verified/preferred/pending.
lumra_pages/reports/* MEDIUM
base_report.html sebagai fondasi — date-pill
emerald, filter bar glass. Semua 14+ report file
extend base ini.
lumra_pages/auth/* MEDIUM
auth-page-bg dengan blob emerald animated,
auth-card glass dengan frosted edge. Login
screen adalah kesan pertama — harus
sempurna.
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 10

CSS Token Reference
Ini adalah satu-satunya dokumen yang dibutuhkan developer saat mengerjakan

setiap file template. Copy bagian :root ini ke lumra_design_system.css sebagai baris

pertama, sebelum semua rule lainnya. Tidak ada token di luar dokumen ini yang

boleh digunakan tanpa persetujuan.

Master CSS Variables — :root Lengkap
:root {
/* ■ EMERALD ODYSSEY PALETTE */
--color-primary: #00674F; /* Base Emerald */
--color-secondary: #00A86B; /* Jade Accent */
--color-accent: #EFBF04; /* Odyssey Gold */
--color-neutral: #FDFBD4; /* Ivory Cream */
--color-contrast: #000080; /* Deep Navy */
/* ■ ALPHA VARIANTS */
--color-primary-a08: rgba(0,103,79,.08);
--color-primary-a10: rgba(0,103,79,.10);
--color-primary-a12: rgba(0,103,79,.12);
--color-primary-a15: rgba(0,103,79,.15);
--color-secondary-a12: rgba(0,168,107,.12);
--color-secondary-a15: rgba(0,168,107,.15);
--color-accent-a15: rgba(239,191,4,.15);
--color-contrast-a08: rgba(0,0,128,.08);
--color-contrast-a10: rgba(0,0,128,.10);
/* ■ GLASS PROTOCOL */
--glass-bg-emerald: rgba(0,103,79,.08);
--glass-bg-gold: rgba(239,191,4,.07);
--glass-bg-navy: rgba(0,0,128,.06);
--glass-border: 0.5px solid rgba(255,255,255,0.10);
--glass-border-top: rgba(255,255,255,0.25);
--glass-border-left: rgba(255,255,255,0.20);
--glass-blur: blur(12px);
--glass-blur-heavy: blur(20px);
--glass-blur-light: blur(8px);
/* ■ SHADOW SYSTEM */
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

--shadow-natural: 0 1px 3px rgba(0,0,0,.08),
0 4px 12px rgba(0,0,0,.06),
0 8px 24px rgba(0,0,0,.04),
0 16px 48px rgba(0,0,0,.03);
--shadow-hover: 0 4px 16px rgba(0,103,79,.16),
0 8px 24px rgba(0,0,0,.06);
--shadow-focus: 0 0 0 3px rgba(0,168,107,.25);
/* ■ SPACING — kelipatan 4px */
--sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px;
--sp-5: 20px; --sp-6: 24px; --sp-8: 32px; --sp-10: 40px;
--sp-12: 48px; --sp-16: 64px;
/* ■ BORDER RADIUS */
--radius-xs: 4px; --radius-sm: 6px;
--radius-md: 8px; --radius-lg: 10px;
--radius-xl: 14px; --radius-2xl: 20px;
--radius-pill: 100px;
/* ■ TYPOGRAPHY */
--font-heading: 'Plus Jakarta Sans', -apple-system, sans-serif;
--font-body: 'Plus Jakarta Sans', -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
/* ■ TRANSITIONS */
--transition-fast: 150ms ease;
--transition-base: 200ms ease;
--transition-slow: 300ms ease;
--transition-modal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-drawer: 300ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-sidebar: 300ms ease;
}
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 11

Audit Checklist — Sebelum Setiap Commit
Sebelum merge setiap file template, developer wajib menjalankan checklist ini. Tidak

ada pengecualian, tidak peduli seberapa kecil perubahannya.

Checklist Visual — Semua Harus Hijau
ITEM STATUS CARA VERIFIKASI
Semua spacing adalah kelipatan 4px
(idealnya 8px)
Wajib
DevTools → Computed →
periksa semua padding,
margin, gap
Border-radius hanya dari token --
radius-* Wajib
Search di file untuk border-
radius — tidak boleh ada
nilai custom
Warna hanya dari Odyssey palette
atau alpha variant-nya
Wajib
Search untuk hex color di
luar #00674F, #00A86B,
#EFBF04, #FDFBD4,
#000080
KPI card menggunakan .kpi-glass
dengan glass protocol penuh Wajib
Inspect element — pastikan
backdrop-filter, border
frosted, shadow 4 lapis ada
Tabel menggunakan .tbl-odyssey
(header emerald, zebra tint) Wajib
Visual check — header
harus #00674F, zebra harus
rgba(0,103,79,.035)
Shimmer muncul saat loading (bukan
blank atau spinner polos) Wajib
Throttle network di
DevTools, reload halaman
— shimmer harus terlihat
Semua angka menggunakan tabular-
nums
Wajib
Inspect element angka di
tabel atau KPI — pastikan
font-variant set
Transition sudah sesuai standar per
komponen
Wajib
Hover card — harus
translateY(-2px) dalam
200ms
Tidak ada inline style yang override
design system
Dianjurkan
Search "style=" di file HTML
— setiap temuan harus ada
justifikasi
Screen layak ditunjukkan ke investor Wajib
Screenshot dan tanya diri
sendiri: bangga atau malu
menunjukkan ini?
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

“Jika ada satu pixel yang salah, itu belum selesai. Deploy
adalah pernyataan bahwa ini siap dinilai dunia.”
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 12

Narasi & Positioning
Produk terbaik pun gagal tanpa narasi yang tepat. Bab ini berisi positioning

statement, cara Lumra berbicara kepada dunia, dan visi jangka panjang yang

menjadi kompas setiap keputusan.

Lumra vs Kompetitor — Bukan Soal Fitur
Perbandingan ini bukan daftar fitur. Ini adalah perbandingan pengalaman, filosofi,

dan perasaan yang ditinggalkan setelah menggunakan produk.

KOMPETITOR TERASA SEPERTI LUMRA MEMBERIKAN
SAP / Oracle ERP
Spreadsheet raksasa dari tahun
Powerful tapi dingin,
kaku, dan intimidating.
Cockpit F1 milik Anda — data
sama, pengalaman berbeda
kelas.
Odoo
Swiss army knife dengan terlalu
banyak tombol. Bisa segalanya
tapi tidak ada yang terasa
premium.
Fokus vertikal tajam — setiap
fitur dirancang untuk konteks
retail & F&B Indonesia.
ERP Lokal Generic
Form pemerintahan. Warna biru
tua, font Times New Roman,
grid Excel.
Emerald Odyssey — desain
yang membuat pengguna
bangga menampilkannya ke
investor.
Google Sheets /
Excel
Kekuatan manual yang tidak
skalabel. Setiap laporan dibuat
ulang dari nol.
Insight otomatis — dashboard
yang menjawab sebelum
pertanyaan diajukan.
Tool Import CSV
Pekerjaan, bukan power. Data
masuk tapi tidak pernah
menjadi keputusan.
Single Source of Truth — satu
input, puluhan view, zero
duplikasi.
Visi Jangka Panjang — The Lumra Ecosystem
FASE FOKUS & TARGET
Fase 1 · Sekarang
ERP Core sempurna — Inventory, Sales, Master Data, Reports.
Pengguna pertama yang loyal dan menjadi referensi pasar.
Fase 2 · Ekspansi
API publik — integrasi marketplace (Tokopedia, Shopee), payment
gateway, logistik. Ekosistem partner yang menggunakan Lumra
sebagai backbone.
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

Fase 3 ·
Intelligence
AI-powered forecasting — prediksi stok, rekomendasi harga,
customer churn prediction. Dari ERP reaktif menjadi ERP prediktif.
Fase 4 · Platform
White-label dan multi-tenant — Lumra sebagai infrastruktur untuk
SaaS vertikal lainnya. Dari produk menjadi platform — dari tool
menjadi standar industri.
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

BAB 13

Konstitusi Lumra — Sepuluh Hukum
Konstitusi bukan sekadar panduan. Ia adalah garis batas antara keputusan yang

benar dan yang salah — bahkan sebelum pertanyaan diajukan. Setiap developer,

designer, dan product manager yang menyentuh Lumra harus hafal sepuluh hukum

ini.

I — Tidak ada pixel yang dikompromikan
Jika sebuah elemen terlihat hampir benar, ia salah. Sempurna bukan pilihan — ia
adalah minimum. Ini bukan perfeksionisme yang berlebihan. Ini adalah standar
Lumra.
II — Grid 8px adalah hukum, bukan saran
Setiap spacing, padding, margin, dan dimensi harus kelipatan 4px — idealnya 8px.
Tidak ada pengecualian tanpa persetujuan eksplisit dari lead design.
III — Glass Protocol tidak bisa disingkat
Frosted edge, natural shadow 4 lapis, backdrop blur — ketiganya harus hadir
bersama. Tidak ada versi sederhana dari glass. Versi sederhana adalah versi yang
salah.
IV — Warna Odyssey tidak boleh dilanggar
Tidak ada warna baru tanpa alasan yang kuat dan dokumentasi yang jelas. Palette
5 warna beserta alpha variannya adalah batas absolut. Merah kritis selalu ke navy.
V — Data bergerak, tidak disinkronisasi
Jika ada tombol Sync atau proses duplikasi data manual — itu adalah bug
arsitektur, bukan fitur. Semua modul membaca dari satu sumber.
VI — Setiap screen layak dipresentasikan
Jika ada satu halaman yang malu ditunjukkan ke investor — halaman itu belum
selesai dan tidak boleh di-deploy. Tidak ada bedanya halaman jarang dibuka.
VII — Loading bukan alasan untuk jelek
Shimmer emerald selalu menggantikan area kosong. Tidak ada blank screen, tidak
ada spinner polos. Loading state adalah bagian dari produk, bukan
pengecualiannya.
LUMRA ERP · EMERALD ODYSSEY Blueprint v3.0 · Konfidensial

VIII — Typography adalah otoritas
Plus Jakarta Sans, hierarki ketat (28/22/16/14/13/11px), tabular-nums untuk semua
angka. Tidak ada font lain tanpa keputusan produk yang terdokumentasi.
IX — Komponen dipakai, tidak diduplikasi
Jika ada dua KPI card dengan CSS berbeda — salah satu harus dihapus. Satu resep,
berlaku global, tanpa pengecualian.
X — Legacy dibangun hari ini, bukan nanti
Setiap baris kode yang ditulis hari ini adalah fondasi dari sesuatu yang akan ada
dalam sepuluh tahun. Tulis seperti itu. Setiap hari.
“Legacy bukan dibangun dari fitur. Legacy dibangun dari
standar yang tidak mau dikompromikan.”
Lumra ERP · Emerald Odyssey Blueprint v3.0 · 2026
Dokumen ini adalah konstitusi hidup Lumra ERP. Ia akan diperbarui seiring produk berkembang —
tapi filosofinya tidak akan pernah berubah. Setiap keputusan produk yang bertentangan dengan
dokumen ini harus dipertanyakan, bukan dokumen ini yang diubah.
LUMRA ERP

Emerald Odyssey
Blueprint v3.1
BAB 14

Code Quality Constitution
Kode yang tidak bisa dibaca adalah kode yang belum selesai. Kode yang baik berbicara tentang
niatnya — bukan tentang mekanismenya.

Versi 3.1 · 2026 · Konfidensial

LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

BAB 14
Code Quality Constitution
Desain yang indah di frontend tidak ada artinya jika backend yang menopangnya adalah labirin kode yang
tidak bisa dibaca, tidak bisa diuji, dan tidak bisa diubah tanpa merusak hal lain. Bab ini adalah konstitusi
kode — aturan yang memastikan bahwa kecepatan hari ini tidak menjadi utang teknis bulan depan.
Lima anti-pattern rules ini bukan tentang gaya penulisan. Ini tentang kelangsungan hidup sistem. Setiap
rule yang dilanggar adalah waktu yang akan dibayar developer berikutnya — mungkin kamu sendiri, tiga
bulan dari sekarang.
Ringkasan Lima Aturan
# Nama Aturan Prinsip Utama Dampak jika Dilanggar
0
1
Anti-God
Class
Satu class = satu tanggung
jawab, maks 300 baris
Class yang tidak bisa dipahami
dalam 5 menit tidak bisa
di-maintain
0
2
Anti-Duplicate
Code
DRY — setiap pengetahuan
punya satu representasi resmi
Bug di satu tempat muncul lagi di
4 tempat lain yang lupa diupdate
0
3
Anti-Long
Method
Maks 30 baris per function,
satu fungsi = satu tugas
Function yang tidak bisa dibaca
dalam satu layar tidak bisa
di-debug
0
4
Naming as Do
cumentation
Nama = kontrak — variable
noun, function verb, boolean
is_/has_
tmp, data, flag adalah variable
yang membutuhkan komentar
untuk dibaca
0
5
Architecture
Prudence
YAGNI — jangan build untuk
kebutuhan yang belum ada
Over-engineering membunuh
kecepatan iterasi di tahap awal
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

01
Anti-God Class Rule
Satu class = satu tanggung jawab. Maksimal 300 baris per class. Jika lebih — split.
Definisi God Class
God Class adalah class yang tahu terlalu banyak dan melakukan terlalu banyak. Ia menjadi satu-satunya
titik referensi seluruh sistem — dan satu-satunya titik kegagalan. Di Django, God Class paling sering
muncul di views.py yang menangani validasi, bisnis logic, notifikasi, PDF, dan upload sekaligus dalam
satu method.
Tanda-tanda God Class yang Harus Segera Di-split:
Class memiliki lebih dari 300 baris
Nama class mengandung kata "Manager", "Handler", "Controller", "Helper" tanpa spesifikasi
Method dalam class memerlukan penjelasan komentar blok untuk dipahami
Mengubah satu method membutuhkan testing menyeluruh karena semua saling terkait
Developer baru perlu lebih dari satu jam untuk memahami satu class
Sebelum vs Sesudah — Django OrderView
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

7 SEBELUM — JANGAN
# views.py — GOD CLASS (450 baris)
class OrderView(View):
def post(self, request):
# ---- VALIDASI (60 baris) ----
if not request.POST.get("customer_id")
:
return JsonResponse({"error": "...
"})
customer = Customer.objects.get(...)
if not customer.is_active:
...
# ---- KALKULASI (80 baris) ----
subtotal = 0
for item in items:
subtotal += item.price * item.qty
tax = subtotal * 0.11
discount = self._calc_discount(custome
r)
total = subtotal + tax - discount
# ---- SIMPAN ORDER (40 baris) ----
order = Order.objects.create(...)
for item in items:
OrderItem.objects.create(...)
# ---- EMAIL (50 baris) ----
send_mail(subject=..., body=...)
# ---- PDF (60 baris) ----
pdf = generate_pdf(order)
# ---- UPLOAD (40 baris) ----
upload_to_s3(pdf)
return redirect("order_success")
3 SESUDAH — LAKUKAN
# views.py — CLEAN (< 30 baris)
class OrderView(View):
def post(self, request):
form = OrderForm(request.POST)
if not form.is_valid():
return self._form_error(form)
order = OrderService.create(
data=form.cleaned_data,
user=request.user
)
NotificationService\
.send_confirmation(order)
DocumentService\
.generate_and_upload(order)
return redirect("order_success")
# services.py — OrderService
class OrderService:
@staticmethod
def create(data, user):
order = Order.objects.create(...)
PricingService.apply(order, data)
return order
# services.py — NotificationService
class NotificationService:
@staticmethod
def send_confirmation(order):
EmailService.send_order_email(order)
Struktur File Django yang Benar
File Tanggung Jawab Tidak Boleh Berisi
views.py Terima request, delegasi ke service,
return response
Bisnis logic, query komplex,
email, PDF
services.py Bisnis logic — kalkulasi, rules, workflow HTTP request/response,
template rendering
forms.py Validasi input, clean data, field
definition
Database query, bisnis kalkulasi
selectors.p
y
Query database — ReadOnly,
optimized
Data mutation, bisnis logic
signals.py Side effect post-save/post-create yang
ringan
Heavy computation, external
API call sync
tasks.py Celery tasks — async, background jobs Synchronous logic yang butuh
response time
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

02
Anti-Duplicate Code Rule
DRY — Don't Repeat Yourself. Setiap pengetahuan harus punya satu representasi resmi.
Mengapa Duplikasi Berbahaya
Duplikasi bukan hanya masalah estetika. Setiap kali kamu copy-paste sebuah block kode, kamu
menciptakan dua sumber kebenaran yang akan diverge. Ketika bisnis rules berubah — dan selalu
berubah — kamu harus mengingat semua tempat yang perlu diupdate. Developer berikutnya tidak akan
tahu.
Tiga Jenis Duplikasi di Lumra
Duplikasi Template HTML
7 SEBELUM — JANGAN
{# Di dashboard.html #}

Revenue


{{ total_revenue }}</h
2>
+12%

{# Di inventory.html — copy paste #}

Stok Total


{{ total_stock }}

Menipis

{# Di reports.html — copy paste lagi #}

...
3 SESUDAH — LAKUKAN
{# components/kpi_card.html — SATU definisi #}
<div class="kpi-glass">
<p class="kpi-label">{{ label }}</p>
<h2 class="kpi-value">{{ value }}</h2>
{% if badge %}
<span class="badge-{{ badge_type }}">
{{ badge }}
</span>
{% endif %}
</div>
{# dashboard.html — pakai include #}
{% include "components/kpi_card.html"
with label="Revenue"
value=total_revenue
badge="+12%"
badge_type="success" %}
{# inventory.html — sama, beda data #}
{% include "components/kpi_card.html"
with label="Stok Total"
value=total_stock
badge="Menipis"
badge_type="warning" %}
Duplikasi Python Logic
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

7 SEBELUM — JANGAN
# Di order_views.py
def checkout(request):
subtotal = sum(i.price * i.qty for i in it
ems)
tax = subtotal * 0.11
total = subtotal + tax
# Di report_views.py — duplikat!
def revenue_report(request):
subtotal = sum(i.price * i.qty for i in it
ems)
tax = subtotal * 0.11
total = subtotal + tax # bug di sini?
# Di api_views.py — duplikat lagi!
def order_api(request):
subtotal = sum(i.price * i.qty for i in it
ems)
tax = subtotal * 0.11 # rate berubah?
total = subtotal + tax
3 SESUDAH — LAKUKAN
# pricing_service.py — SATU sumber
class PricingService:
TAX_RATE = Decimal("0.11")
@classmethod
def calculate(cls, items):
subtotal = sum(
item.price * item.qty
for item in items
)
tax = subtotal * cls.TAX_RATE
return {
"subtotal": subtotal,
"tax": tax,
"total": subtotal + tax,
}
# Pakai di mana saja:
pricing = PricingService.calculate(items)
# Tax rate berubah? Update 1 tempat.
Duplikasi CSS / Styling
7 SEBELUM — JANGAN
{# Di 8 file berbeda #}

...

{# File lain — sedikit beda, inconsistent #}

...
3 SESUDAH — LAKUKAN
{# lumra_design_system.css — SATU definisi #}
.kpi-glass {
background: var(--glass-bg-emerald);
border: var(--glass-border);
border-top-color: var(--glass-border-top);
backdrop-filter: var(--glass-blur);
border-radius: var(--radius-xl);
padding: var(--sp-4);
}
{# Di semua template — konsisten #}
<div class="kpi-glass">
...
</div>
{# Design berubah? Update 1 class. #}
{# Semua halaman ikut otomatis. #}
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

03
Anti-Long Method Rule
Maksimal 30 baris per function. Satu function = satu tugas. Jika perlu komentar blok — extract
method.
Prinsip Dasar
Sebuah function yang membutuhkan komentar seperti # -- KALKULASI -- atau # -- KIRIM EMAIL --
untuk membagi seksinya adalah function yang seharusnya dipecah. Komentar itu sudah menjadi nama
function-nya.
Aturan Praktis:
Maksimal 30 baris per function — termasuk blank lines dan komentar
Jika function membutuhkan komentar blok untuk menjelaskan satu seksi → extract jadi function baru
Satu function harus bisa dijelaskan dengan satu kalimat aktif tanpa kata "dan"
Nama function yang baik membuat komentar tidak diperlukan
Jika function menerima lebih dari 4 parameter → pertimbangkan pakai dataclass atau dict
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

7 SEBELUM — JANGAN
def process_order(request):
# ---- VALIDASI INPUT ----
if not request.POST.get("customer"):
return error("customer required")
customer = Customer.objects.filter(
id=request.POST["customer"],
is_active=True
).first()
if not customer:
return error("invalid customer")
items = json.loads(request.POST["items"])
if not items:
return error("no items")
# ---- KALKULASI ----
subtotal = 0
for item in items:
product = Product.objects.get(id=item[
"id"])
subtotal += product.price * item["qty"
]
tax = subtotal * Decimal("0.11")
discount = 0
if customer.tier == "GOLD":
discount = subtotal * Decimal("0.05")
total = subtotal + tax - discount
# ---- SIMPAN ----
order = Order.objects.create(
customer=customer, total=total)
for item in items:
OrderItem.objects.create(
order=order, ...)
# ---- NOTIFIKASI ----
send_mail(...)
send_whatsapp(...)
# ---- RETURN ----
return JsonResponse({"id": order.id})
3 SESUDAH — LAKUKAN
def process_order(request):
"""Proses order baru dari checkout."""
customer, items = validate_order_input(
request.POST
)
pricing = PricingService.calculate(
items, customer
)
order = create_order(
customer, items, pricing
)
notify_order_created(order)
return JsonResponse({"id": order.id})
def validate_order_input(post_data):
"""Validasi dan return (customer, items)."
""
customer = get_active_customer(
post_data.get("customer")
)
items = parse_order_items(
post_data.get("items")
)
return customer, items
def notify_order_created(order):
"""Kirim semua notifikasi order baru."""
EmailService.send_confirmation(order)
WhatsAppService.send_receipt(order)
Ukuran Ideal per Jenis Method
Jenis Method Maks Baris Tanda Terlalu Panjang
View method (get/post) 15–20 baris Ada query langsung, ada if-else bisnis logic,
ada email
Service method 20–30 baris Melakukan lebih dari satu langkah bisnis yang
berbeda
Utility / helper 10–20 baris Melakukan transformasi data DAN validasi
sekaligus
Signal handler 5–15 baris Melakukan lebih dari trigger-and-delegate
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

Jenis Method Maks Baris Tanda Terlalu Panjang
Model method 10–20 baris Mengandung bisnis logic yang seharusnya di
service
Template tag / filter 5–10 baris Lebih dari satu transformasi data
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

04
Naming as Documentation
Nama yang baik membuat komentar tidak diperlukan. Nama yang buruk membutuhkan komentar
untuk menjelaskan nama itu sendiri.
Filosofi Penamaan di Lumra
Nama bukan label — nama adalah kontrak. Ketika kamu menulis calculate_order_total(), kamu
berjanji bahwa function itu akan menghitung total order, dan hanya itu. Ketika kamu menulis process(),
kamu tidak berjanji apa-apa.
Konvensi Penamaan Wajib
Kategori Konvensi Contoh BENAR Contoh
SALAH
Variable Noun — apa yang
disimpan
order_list,
active_customers,
pending_amount
data, items,
x, tmp, res
Function /
Method
Verb — apa yang
dilakukan
calculate_total(),
send_email(),
get_active_orders()
process(),
handle(),
do_stuff()
Boolean is_ / has_ / can_
prefix
is_active,
has_permission,
can_checkout
active,
permission,
flag, check
Class PascalCase Noun —
entitas
OrderService,
PricingEngine,
CustomerRepository
OrderManager
, Handler,
Utils
Constant UPPER_SNAKE —
nilai tetap
TAX_RATE,
MAX_RETRY_COUNT,
DEFAULT_PAGE_SIZE
taxrate,
Tax, max_r
Django URL
name
module:action format orders:list,
orders:create,
inventory:stock_detail
order_list,
view1, page
Template
variable
Noun, snake_case,
deskriptif
total_revenue,
active_orders,
low_stock_products
data, val,
items, stuff
Before vs After — Naming yang Bicara Sendiri
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

7 SEBELUM — JANGAN
# Apa ini?
def proc(r, d, f=False):
tmp = []
for x in d:
if x["s"] == 1 or f:
val = x["p"] * x["q"]
if val > 0:
tmp.append(x)
res = calc(tmp)
return res
# Kamu perlu baca seluruh function
# untuk paham apa yang dilakukan.
# Developer baru butuh 20 menit.
flag = True
data = get(1)
if data:
x = proc(request, data, flag)
3 SESUDAH — LAKUKAN
def calculate_eligible_order_total(
request,
order_items,
include_inactive=False
):
eligible_items = [
item for item in order_items
if item["status"] == ACTIVE
or include_inactive
if item["price"] * item["qty"] > 0
]
return PricingService.sum(eligible_items)
# Nama sudah menjelaskan intent.
# Developer baru paham dalam 30 detik.
include_archived = True
customer = get_customer_by_id(customer_id)
if customer:
total = calculate_eligible_order_total(
request, order_items, include_archived
)
Kata-kata yang DILARANG sebagai Nama Variable atau Function
Kata Terlarang Mengapa Buruk Ganti Dengan
data, info Terlalu general — semua
adalah data
order_data, customer_info,
stock_payload
tmp, temp Sinyal bahwa niat belum jelas Beri nama sesuai isi:
pending_items,
filtered_orders
x, y, z, i, j Hanya boleh di loop index yang
trivial
order, item, product — nama
entitas yang jelas
flag, check Tidak menjelaskan kondisi apa is_valid, has_discount,
should_notify
val, value Nilai apa? Tipe apa? total_price,
discount_amount, tax_rate
process(),
handle()
Tidak ada komitmen tentang
aksi
calculate_tax(),
send_confirmation(),
save_order()
Manager,
Helper, Utils
Kata keranjang yang berarti
semua dan tidak ada
OrderService, PricingEngine,
EmailSender
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

05
Architecture Prudence — YAGNI
You Aren't Gonna Need It. Jangan build untuk kebutuhan yang belum ada. Kompleksitas yang
tidak dibutuhkan adalah utang teknis tanpa bunga yang tiba-tiba jatuh tempo.
Filosofi YAGNI untuk Lumra
Over-engineering adalah kebalikan dari perfeksionisme Jobs. Jobs tidak menambahkan fitur yang tidak
ada usernya — ia menghapus fitur yang tidak diperlukan. Arsitektur yang terlalu kompleks di awal
membunuh kecepatan iterasi dan membuat developer baru tidak bisa produktif dalam minggu pertama.
Tiga Tingkat Arsitektur — Pilih yang Tepat untuk Fase Saat Ini
Fase Arsitektur Kapan Digunakan Tanda Harus Upgrade
Fase 1 ·
Sekarang
Layered (MVC/MVT)
views → services →
models
Project awal, tim kecil (<5), fitur
belum stabil, pivot masih mungkin
Service layer mulai punya
lebih dari 20 method yang
tidak related
Fase 2 ·
Berkembang
Layered + Domain
Services Domain
objects mulai
terbentuk
Tim mulai besar (5-15), domain
sudah stabil, ada modul yang
kompleks
Circular dependency antar
service, testing butuh banyak
mock
Fase 3 ·
Enterprise
Hexagonal / CQRS
Port & Adapters,
Command/Query
Tim besar (15+), multi-platform,
perlu testability tinggi, performa
kritis
Ini bukan untuk Lumra saat ini.
Build Fase 1 dengan
sempurna dulu.
Anti-Pattern Over-Engineering yang Sering Terjadi
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

7 SEBELUM — JANGAN
# Membuat abstraction layer untuk
# sesuatu yang hanya punya 1 implementasi
class AbstractEmailProvider(ABC):
@abstractmethod
def send(self, to, subject, body): ...
class SMTPEmailProvider(AbstractEmailProvider)
:
def send(self, to, subject, body):
# implementasi smtp
class EmailProviderFactory:
@staticmethod
def create(provider_type):
if provider_type == "smtp":
return SMTPEmailProvider()
# padahal hanya ada SMTP
# Membuat event bus untuk 2 event
class EventBus:
def publish(self, event): ...
def subscribe(self, handler): ...
# Padahal signals Django sudah cukup
3 SESUDAH — LAKUKAN
# Simple service yang langsung pakai
# Django email utilities
class EmailService:
@staticmethod
def send_order_confirmation(order):
send_mail(
subject=f"Order #{order.id} Confir
med",
message=render_email(order),
from_email=settings.DEFAULT_FROM,
recipient_list=[order.customer.ema
il],
)
@staticmethod
def send_low_stock_alert(product):
send_mail(
subject=f"Stok {product.name} Krit
is",
...
)
# Kalau besok perlu provider lain?
# Refactor saat itu tiba — bukan sekarang.
# YAGNI.
Checklist YAGNI — Tanya Sebelum Membangun
Pertanyaan Jika
Jawaban
"Tidak"
Tindakan
Apakah ada user story konkret yang
membutuhkan ini SEKARANG?
Tidak Jangan build. Catat di
backlog.
Apakah ini akan digunakan dalam sprint ini
atau berikutnya?
Tidak Defer. Build yang paling
sederhana dulu.
Apakah tanpa ini sistem tidak bisa berfungsi
dengan benar?
Tidak Nice-to-have bukan
must-have. Skip.
Apakah kompleksitas ini bisa dijelaskan ke
developer baru dalam 10 menit?
Tidak Terlalu kompleks untuk
kebutuhan saat ini.
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

Code Smell Checklist — Untuk Code Review
Gunakan checklist ini setiap kali melakukan code review. Setiap item yang ter-check adalah technical debt
yang perlu segera diselesaikan atau dijadwalkan.
Code Smell Indikator Rule
yang Dil
anggar
Solusi
God Class Class > 300 baris atau punya
method yang tidak saling terkait
Rule 01 Split berdasarkan
tanggung jawab ke
services.py
Copy-paste
Block
Block kode yang sama muncul di
lebih dari 1 tempat
Rule 02 Extract ke function
atau template
partial
Long Method Function > 30 baris atau butuh
komentar blok
Rule 03 Extract method
untuk setiap seksi
yang diberi
komentar
Mystery Name Variable x, tmp, data, flag atau
function process(), handle()
Rule 04 Rename dengan
noun untuk
variable, verb untuk
function
Premature
Abstraction
Interface/abstract class dengan
hanya 1 implementasi
Rule 05 Delete abstraction,
pakai concrete
class langsung
Magic Number Angka hardcoded: 0.11, 5, 300
tanpa nama atau penjelasan
Rule 04 Extract ke constant:
TAX_RATE,
MAX_ITEMS,
MIN_STOCK
Deep Nesting If dalam if dalam if — lebih dari 3
level indentasi
Rule 03 Early return / guard
clause atau extract
ke function
Comment as
Code
Komentar yang menjelaskan APA
yang dilakukan (bukan MENGAPA)
Rule 04 Kode yang baik
menjelaskan
dirinya sendiri
Inline CSS
Override
style="" di template yang
mengoverride design system token
Rule 02 Gunakan kelas dari
lumra_design_syst
em.css
Fat View View method yang berisi query,
kalkulasi, dan notifikasi sekaligus
Rule 01 Delegate ke service
— view hanya
orchestrate
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

Django-Specific Best Practices untuk Lumra
Aturan umum di atas diimplementasikan secara spesifik di Django dengan pola-pola berikut. Ini adalah
standar wajib yang harus diikuti di semua 115 URL dan 102 template Lumra.
Struktur Folder yang Benar
lumra_app/
nnn views.py # Thin views — hanya orchestrate, < 20 baris per method
nnn services.py # Business logic — di sinilah "otak" aplikasi
nnn selectors.py # Read-only queries — QuerySet yang teroptimasi
nnn forms.py # Validasi & clean data — tidak ada bisnis logic
nnn models.py # Data model — property sederhana, bukan bisnis logic
nnn signals.py # Post-save hooks — thin, hanya trigger service
nnn tasks.py # Celery async tasks — untuk operasi berat
nnn serializers.py # API serialization — hanya transformasi data
nnn admin.py # Django admin config
nnn tests/
nnn test_services.py # Unit test bisnis logic
nnn test_views.py # Integration test endpoint
nnn test_selectors.py # Test query correctness
Query Optimization — N+1 Problem
7 SEBELUM — JANGAN
# views.py — menghasilkan N+1 query!
def order_list(request):
orders = Order.objects.all()
# Setiap iterasi = 1 query ke DB!
for order in orders:
print(order.customer.name)
# Ini 1 query per order!
for item in order.items.all():
print(item.product.name)
# Ini 1 query per item!
# 100 orders × 10 items =
# 1 + 100 + 1000 = 1101 queries!
3 SESUDAH — LAKUKAN
# selectors.py — efficient query
class OrderSelector:
@staticmethod
def get_orders_with_details():
return Order.objects.select_related(
"customer",
"customer__tier",
).prefetch_related(
"items",
"items__product",
"items__product__category",
).filter(
is_active=True
).order_by("-created_at")
# views.py menggunakan selector
def order_list(request):
orders = OrderSelector\
.get_orders_with_details()
# Hanya 3 query total.
Model Property vs Service Method
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

Yang Boleh di Model Yang TIDAK Boleh di Model Taruh di Mana
Property sederhana:
full_name,
display_price
Kalkulasi yang melibatkan model
lain
services.py
__str__ method Send email atau notifikasi NotificationServi
ce
Validasi field di
clean()
Query ke tabel lain yang tidak
langsung related
selectors.py
get_absolute_url() Bisnis rules (diskon, tier, loyalty) PricingService,
TierService
LUMRA ERP · EMERALD ODYSSEY BAB 14 — Code Quality Constitution · v3.1 · Konfidensial

Konstitusi Kode — Lima Hukum
01 — Satu Class, Satu Tanggung Jawab
Class yang melakukan banyak hal tidak bisa ditest, tidak bisa di-maintain, dan tidak bisa dipahami.
Pisahkan sebelum menjadi masalah, bukan setelah.
02 — Satu Sumber Kebenaran
Setiap pengetahuan harus punya satu representasi resmi. Copy-paste adalah cara tercepat untuk
menciptakan bug yang tidak bisa dilacak.
03 — Satu Function, Satu Tugas
Jika function membutuhkan komentar untuk menjelaskan seksinya — itu sudah harus jadi beberapa
function. Nama function yang baik adalah dokumentasinya sendiri.
04 — Nama adalah Kontrak
Variable, function, dan class dengan nama yang jelas membuat code review lebih cepat, bug lebih
mudah ditemukan, dan developer baru produktif lebih awal.
05 — Build yang Dibutuhkan, Bukan yang Mungkin Dibutuhkan
Over-engineering membunuh momentum. Build yang paling sederhana yang bisa bekerja. Refactor
ketika kebutuhan nyata itu tiba.
"Kode yang tidak bisa dibaca adalah kode yang belum selesai. Kode yang baik
berbicara tentang niatnya — bukan tentang mekanismenya."