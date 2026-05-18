# Laporan Audit UI/UX — Reverse Engineering
**Dibuat:** 27 April 2026 09:43
**Total file dianalisis:** 223

---

## Ringkasan Eksekutif

| Metrik | Nilai |
|--------|-------|
| File HTML dianalisis | 223 |
| Total komponen terdeteksi | 6533 |
| Total isu ditemukan | 215 |
| ⚠ Warnings | 65 |
| Scroll nesting | 0 |

---

## 📄 activity_drawer
**File:** `activity_drawer.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| modal | 13 |
| layout | 12 |
| timeline | 2 |
| alpine-root | 1 |
| heading | 1 |
| button | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 3
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-reject'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-approve'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-secondary w-full'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-secondary'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-approve'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-secondary'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-approve'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-secondary w-full'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='drawer-btn-secondary w-full'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 alert
**File:** `alert.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|

- **Total komponen:** 0
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 alert_inner
**File:** `alert_inner.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |
| heading | 1 |
| button | 1 |

- **Total komponen:** 7
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 approval_modal
**File:** `approval_modal.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| modal | 6 |
| heading | 2 |
| button | 2 |
| alpine-root | 1 |
| card | 1 |
| badge | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='modal-btn-reject'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='modal-btn-reject'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% block title %}Dashboard{% endblock %}
**File:** `base.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| main | 1 |

- **Total komponen:** 3
- **Elemen interaktif:** 0
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

---

## 📄 footer
**File:** `footer.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| footer | 5 |
| layout | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 kpi_card
**File:** `kpi_card.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| card | 7 |
| layout | 2 |
| metric | 1 |

- **Total komponen:** 10
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 kpi_card_inner
**File:** `kpi_card_inner.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 6 |
| metric | 1 |

- **Total komponen:** 7
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 kpi_card_white
**File:** `kpi_card_white.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 6 |
| article | 1 |

- **Total komponen:** 7
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 navbar
**File:** `navbar.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| badge | 8 |
| search | 8 |
| button | 7 |
| footer | 3 |
| layout | 2 |
| header | 1 |
| filter | 1 |
| image | 1 |

- **Total komponen:** 31
- **Elemen interaktif:** 13
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 badge
**File:** `badge.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |

- **Total komponen:** 5
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 bg_blob
**File:** `bg_blob.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|

- **Total komponen:** 0
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 breadcrumb
**File:** `breadcrumb.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| nav | 1 |
| ol | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 confirm_modal
**File:** `confirm_modal.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| button | 2 |
| heading | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 data_table
**File:** `data_table.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| button | 2 |
| table | 1 |
| layout | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 empty_state
**File:** `empty_state.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 1 |
| heading | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 form_field
**File:** `form_field.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 3 |

- **Total komponen:** 3
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 pagination
**File:** `pagination.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| nav | 1 |

- **Total komponen:** 3
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ title|default:"Dokumen LUMRA" }}
**File:** `print_base.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| footer | 1 |

- **Total komponen:** 1
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 stepper
**File:** `stepper.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 7 |

- **Total komponen:** 7
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 tabs
**File:** `tabs.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| alpine-root | 1 |
| layout | 1 |
| button | 1 |
| filter | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 2
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 sidebar
**File:** `sidebar.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| button | 12 |
| footer | 2 |
| aside | 1 |
| nav | 1 |
| badge | 1 |
| image | 1 |
| modal | 1 |

- **Total komponen:** 19
- **Elemen interaktif:** 13
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 sidebar_item
**File:** `sidebar_item.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 3 |

- **Total komponen:** 3
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 sidebar_right
**File:** `sidebar_right.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 12 |
| button | 4 |
| filter | 4 |
| aside | 1 |
| badge | 1 |

- **Total komponen:** 22
- **Elemen interaktif:** 4
- **Container dengan scroll:** 2
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 rounded-lg transition-all'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='ml-auto flex-shrink-0 text-[10px] font-bold px-2 p'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full mt-2 py-2.5 text-xs font-semibold text-emer'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 content_section
**File:** `content_section.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| button | 3 |
| heading | 1 |
| footer | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 greeting_section
**File:** `greeting_section.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| alpine-root | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 3
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 metric_card
**File:** `metric_card.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| card | 1 |
| badge | 1 |
| progressbar | 1 |

- **Total komponen:** 3
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 dashboard_layout
**File:** `dashboard_layout.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| card | 3 |
| section | 2 |
| heading | 2 |
| badge | 2 |
| progressbar | 1 |
| sidebar | 1 |

- **Total komponen:** 11
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Accounts Payable
**File:** `accounts_payable.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 6 |
| card | 5 |
| heading | 2 |
| button | 2 |
| nav | 1 |
| table | 1 |

- **Total komponen:** 17
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-slate-500 hover:text-emeral'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Accounts Receivable
**File:** `accounts_receivable.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 7 |
| card | 4 |
| heading | 2 |
| nav | 1 |
| button | 1 |
| input | 1 |
| table | 1 |

- **Total komponen:** 17
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Neraca (Balance Sheet)
**File:** `balance_sheet.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |
| card | 4 |
| heading | 3 |
| table | 2 |
| input | 1 |
| button | 1 |

- **Total komponen:** 16
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Laporan Arus Kas (Cash Flow)
**File:** `cash_flow.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 2 |
| card | 2 |
| input | 1 |
| button | 1 |
| table | 1 |

- **Total komponen:** 9
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Buku Besar Pembantu (COA)
**File:** `chart_of_accounts.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| button | 6 |
| layout | 4 |
| card | 2 |
| nav | 1 |
| heading | 1 |
| input | 1 |
| search | 1 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 18
- **Elemen interaktif:** 7
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Buat Akun Baru
**File:** `chart_of_accounts_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 5 |
| layout | 4 |
| button | 2 |
| card | 1 |
| heading | 1 |
| form | 1 |

- **Total komponen:** 14
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Buku Besar (General Ledger)
**File:** `general_ledger.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 4 |
| card | 2 |
| heading | 2 |
| input | 2 |
| table | 1 |

- **Total komponen:** 11
- **Elemen interaktif:** 2
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

---

## 📄 
**File:** `journal_entry_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 4 |
| alpine-root | 1 |
| card | 1 |
| heading | 1 |
| hero | 1 |
| table | 1 |
| form | 1 |
| input | 1 |
| button | 1 |

- **Total komponen:** 12
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Input Jurnal Umum
**File:** `journal_entry_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| input | 7 |
| button | 3 |
| alpine-root | 1 |
| heading | 1 |
| card | 1 |
| footer | 1 |

- **Total komponen:** 22
- **Elemen interaktif:** 5
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Journal Entry List
**File:** `journal_entry_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 9 |
| button | 4 |
| heading | 2 |
| nav | 1 |
| input | 1 |
| card | 1 |

- **Total komponen:** 18
- **Elemen interaktif:** 5
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Payment Voucher (PV)
**File:** `payment_voucher_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 12 |
| layout | 9 |
| alpine-root | 1 |
| heading | 1 |
| card | 1 |
| button | 1 |

- **Total komponen:** 25
- **Elemen interaktif:** 9
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Laporan Laba Rugi
**File:** `profit_loss_statement.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| card | 5 |
| layout | 4 |
| table | 3 |
| heading | 2 |
| input | 1 |

- **Total komponen:** 15
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Neraca Percobaan (Trial Balance)
**File:** `trial_balance.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 6 |
| heading | 3 |
| card | 3 |
| input | 2 |
| button | 2 |
| table | 1 |

- **Total komponen:** 17
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Lupa Password?
**File:** `forgot_password.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 1 |
| heading | 1 |
| form | 1 |
| input | 1 |
| button | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ request.user.get_full_name }}
**File:** `lock_screen.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| form | 1 |
| input | 1 |
| button | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 login
**File:** `login.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| input | 4 |
| button | 2 |
| heading | 1 |
| form | 1 |

- **Total komponen:** 16
- **Elemen interaktif:** 6
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 register
**File:** `register.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|

- **Total komponen:** 0
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Reset Password
**File:** `reset_password.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 2 |
| layout | 1 |
| heading | 1 |
| form | 1 |
| button | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Sesi Expired
**File:** `session_expired.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 1 |
| heading | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 2FA Setup
**File:** `two_factor.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| input | 2 |
| heading | 1 |
| form | 1 |
| image | 1 |
| button | 1 |

- **Total komponen:** 8
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Verifikasi Email
**File:** `verify_email.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 1 |
| heading | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 403
**File:** `error_403.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 1 |
| heading | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Page Not Found - Lumra ERP
**File:** `error_404.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| search | 1 |
| heading | 1 |
| form | 1 |
| input | 1 |
| button | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Internal Server Error - Lumra ERP
**File:** `error_500.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |

- **Total komponen:** 1
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Pemeliharaan Sistem — CoffeeShop
**File:** `error_maintenance.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| button | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Sesi Berakhir — CoffeeShop
**File:** `error_session_expired.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| card | 1 |
| heading | 1 |
| form | 1 |
| button-primary | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Record
**File:** `add_stock_movement.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 16 |
| input | 7 |
| badge | 6 |
| card | 3 |
| heading | 2 |
| search | 2 |
| hero | 1 |
| button | 1 |

- **Total komponen:** 38
- **Elemen interaktif:** 9
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Master Data Alasan Koreksi
**File:** `adjustment_reasons.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| button | 5 |
| input | 5 |
| layout | 4 |
| heading | 2 |
| card | 1 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 19
- **Elemen interaktif:** 10
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 
**File:** `batch_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| card | 7 |
| heading | 4 |
| button | 3 |
| alpine-root | 1 |
| timeline | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Input Batch Baru
**File:** `batch_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 7 |
| layout | 6 |
| button | 2 |
| card | 1 |
| heading | 1 |
| form | 1 |

- **Total komponen:** 18
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Batch & Lot Tracking
**File:** `batch_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 13 |
| card | 4 |
| filter | 4 |
| heading | 2 |
| nav | 1 |
| input | 1 |

- **Total komponen:** 25
- **Elemen interaktif:** 1
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Dashboard Kedaluwarsa
**File:** `expiry_tracking.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 12 |
| button | 6 |
| heading | 3 |
| nav | 1 |
| card | 1 |

- **Total komponen:** 23
- **Elemen interaktif:** 6
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='flex-1 py-2 bg-slate-50 text-slate-600 rounded-lg '
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='flex-1 py-2 bg-white border border-slate-200 text-'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ product.name }}
**File:** `product_details.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 13 |
| heading | 3 |
| button | 3 |
| alpine-root | 1 |
| nav | 1 |
| ol | 1 |
| image | 1 |
| section | 1 |
| table | 1 |
| modal | 1 |
| alert | 1 |

- **Total komponen:** 27
- **Elemen interaktif:** 4
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 DaftarProduk
**File:** `product_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 40 |
| input | 26 |
| button | 25 |
| button-primary | 4 |
| card | 4 |
| modal | 4 |
| badge | 3 |
| form | 3 |
| image | 2 |
| metric | 1 |
| heading | 1 |
| search | 1 |
| table | 1 |

- **Total komponen:** 115
- **Elemen interaktif:** 52
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Produk
**File:** `products.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 32 |
| button | 23 |
| layout | 17 |
| modal | 8 |
| button-primary | 7 |
| card | 6 |
| heading | 5 |
| form | 5 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 105
- **Elemen interaktif:** 56
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 
**File:** `requisition_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 6 |
| heading | 5 |
| button | 5 |
| timeline | 2 |
| alpine-root | 1 |
| badge | 1 |
| table | 1 |

- **Total komponen:** 21
- **Elemen interaktif:** 6
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-emerald-500 hover:bg-emerald-600 te'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-white border border-rose-200 text-r'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-blue-500 hover:bg-blue-600 text-whi'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full py-3 bg-slate-800 hover:bg-slate-700 text-w'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Buat Permintaan Stok
**File:** `requisition_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 7 |
| layout | 3 |
| button | 3 |
| heading | 2 |
| alpine-root | 1 |
| card | 1 |
| table | 1 |

- **Total komponen:** 18
- **Elemen interaktif:** 7
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Permintaan Stok (Requisition)
**File:** `requisition_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| card | 4 |
| filter | 4 |
| search | 2 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 StockMovementControl Tower
**File:** `stock_movement.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 29 |
| button | 9 |
| search | 7 |
| card | 4 |
| nav | 2 |
| metric | 1 |
| heading | 1 |
| alpine-root | 1 |
| button-primary | 1 |
| form | 1 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 58
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='flex-1 flex items-center justify-center gap-2 py-3'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='flex-1 flex items-center justify-center gap-2 py-3'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Record
**File:** `stock_movement_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 16 |
| input | 7 |
| badge | 6 |
| card | 3 |
| heading | 2 |
| search | 2 |
| hero | 1 |
| button | 1 |

- **Total komponen:** 38
- **Elemen interaktif:** 9
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Session Detail —{{ session.location.name }}
**File:** `stock_opname_approval_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| button | 6 |
| heading | 5 |
| layout | 3 |
| table | 2 |
| metric | 1 |
| alpine-root | 1 |
| nav | 1 |
| ol | 1 |
| section | 1 |
| input | 1 |

- **Total komponen:** 22
- **Elemen interaktif:** 8
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Stock Opname Approvals
**File:** `stock_opname_approvals.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 9 |
| button | 7 |
| heading | 4 |
| nav | 2 |
| input | 2 |
| metric | 1 |
| alpine-root | 1 |
| ol | 1 |
| filter | 1 |
| search | 1 |
| section | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='inline-flex items-center gap-1 text-xs font-medium'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='inline-flex items-center gap-1 text-xs font-medium'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Stock Opname —{{ selected_location.name }}
**File:** `stock_opname_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 12 |
| button | 6 |
| input | 4 |
| heading | 3 |
| nav | 2 |
| form | 2 |
| search | 2 |
| alpine-root | 1 |
| ol | 1 |
| section | 1 |
| table | 1 |

- **Total komponen:** 35
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Stock Opname
**File:** `stock_opname_locations.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 14 |
| button | 8 |
| heading | 6 |
| input | 6 |
| metric | 1 |
| alpine-root | 1 |
| nav | 1 |
| ol | 1 |
| search | 1 |
| section | 1 |
| article | 1 |
| form | 1 |

- **Total komponen:** 42
- **Elemen interaktif:** 15
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Inventory Planner
**File:** `stock_overview.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 29 |
| button | 17 |
| input | 14 |
| heading | 6 |
| modal | 4 |
| table | 2 |
| form | 2 |
| metric | 1 |
| alpine-root | 1 |
| nav | 1 |
| ol | 1 |
| search | 1 |
| section | 1 |
| alert | 1 |

- **Total komponen:** 81
- **Elemen interaktif:** 32
- **Container dengan scroll:** 4
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:text-blue-600 hover:bg-'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:style='
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:text-purple-600 hover:b'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 StockPlanning
**File:** `stock_planning.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 42 |
| button | 12 |
| search | 5 |
| card | 4 |
| nav | 2 |
| metric | 1 |
| heading | 1 |
| form | 1 |
| modal | 1 |
| input | 1 |

- **Total komponen:** 70
- **Elemen interaktif:** 13
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-[11px] font-bold text-indigo-500 hover:text-i'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='btn-submit mt-4 disabled:opacity-40'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full mt-2 py-1.5 rounded-lg text-[10px] font-bol'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 PurchasingManagement
**File:** `stock_purchasing.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 42 |
| button | 12 |
| search | 5 |
| card | 4 |
| nav | 2 |
| metric | 1 |
| heading | 1 |
| form | 1 |
| modal | 1 |
| input | 1 |

- **Total komponen:** 70
- **Elemen interaktif:** 13
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-[11px] font-bold text-indigo-500 hover:text-i'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='btn-submit mt-4 disabled:opacity-40'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full mt-2 py-1.5 rounded-lg text-[10px] font-bol'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Evaluasi Performa Supplier
**File:** `supplier_evaluation.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 9 |
| card | 5 |
| heading | 4 |
| button | 2 |
| badge | 1 |

- **Total komponen:** 21
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-slate-600 hover:text-emeral'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Supplier Price List
**File:** `supplier_price_confirm_delete.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 16 |
| button | 10 |
| input | 6 |
| heading | 4 |
| nav | 2 |
| form | 2 |
| search | 2 |
| metric | 1 |
| alpine-root | 1 |
| ol | 1 |
| section | 1 |
| table | 1 |

- **Total komponen:** 47
- **Elemen interaktif:** 17
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% if is_edit %}Edit Supplier Price{% else %}Tambah Supplier Price{% endif %}
**File:** `supplier_price_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| alpine-root | 1 |
| nav | 1 |
| ol | 1 |
| heading | 1 |
| form | 1 |
| button | 1 |

- **Total komponen:** 8
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Supplier Price List
**File:** `supplier_price_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 16 |
| button | 10 |
| input | 6 |
| heading | 4 |
| nav | 2 |
| form | 2 |
| search | 2 |
| metric | 1 |
| alpine-root | 1 |
| ol | 1 |
| section | 1 |
| table | 1 |

- **Total komponen:** 47
- **Elemen interaktif:** 17
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Tambah Zona Baru
**File:** `warehouse_zone_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 6 |
| layout | 5 |
| card | 4 |
| button | 2 |
| heading | 1 |
| form | 1 |

- **Total komponen:** 19
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Zona Gudang
**File:** `warehouse_zones.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 15 |
| card | 5 |
| filter | 4 |
| heading | 2 |
| nav | 1 |
| input | 1 |
| badge | 1 |
| progressbar | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% if campaign %}EditCampaign{% else %}CampaignBaru{% endif %}
**File:** `add_campaign.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 33 |
| layout | 27 |
| card | 10 |
| badge | 6 |
| button | 6 |
| nav | 1 |
| heading | 1 |
| form | 1 |

- **Total komponen:** 85
- **Elemen interaktif:** 40
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-7 h-7 rounded-lg bg-rose-50 text-rose-400 hover:'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 MarketingCampaigns
**File:** `campaign.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 36 |
| metric | 8 |
| badge | 5 |
| button | 4 |
| input | 3 |
| nav | 2 |
| heading | 1 |
| form | 1 |
| search | 1 |
| card | 1 |
| table | 1 |
| modal | 1 |

- **Total komponen:** 64
- **Elemen interaktif:** 7
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 MarketingCampaigns
**File:** `campaign_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 36 |
| metric | 8 |
| badge | 5 |
| button | 4 |
| input | 3 |
| nav | 2 |
| heading | 1 |
| form | 1 |
| search | 1 |
| card | 1 |
| table | 1 |
| modal | 1 |

- **Total komponen:** 64
- **Elemen interaktif:** 7
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ form_title }}
**File:** `customer_segment_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ page_title }}
**File:** `customer_segment_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 💸 Discounts
**File:** `discount.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 17 |
| input | 2 |
| heading | 1 |
| form | 1 |
| search | 1 |
| button | 1 |
| nav | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 🏆 Loyalty Program Members
**File:** `loyalty_members.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 17 |
| input | 2 |
| heading | 1 |
| form | 1 |
| search | 1 |
| button | 1 |
| nav | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Kalender Promo
**File:** `promotion_calendar.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 31 |
| button | 8 |
| heading | 4 |
| card | 4 |
| badge | 4 |
| calendar | 3 |
| nav | 1 |
| alert | 1 |
| modal | 1 |

- **Total komponen:** 57
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ page_title }}
**File:** `voucher_claim_log.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 
**File:** `voucher_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 16 |
| input | 13 |
| button | 9 |
| heading | 7 |
| calendar | 2 |
| badge | 2 |
| nav | 1 |
| card | 1 |
| form | 1 |
| button-primary | 1 |

- **Total komponen:** 53
- **Elemen interaktif:** 22
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Voucher & Promo
**File:** `voucher_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 26 |
| button | 9 |
| card | 8 |
| filter | 5 |
| heading | 3 |
| calendar | 2 |
| search | 2 |
| badge | 2 |
| nav | 1 |
| input | 1 |
| modal | 1 |

- **Total komponen:** 60
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='' class='mt-1 w-3.5 h-3.5 accent-emerald-500 rounded cursor'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ form_title }}
**File:** `bank_account_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ page_title }}
**File:** `bank_accounts.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 ProductCategories
**File:** `categories_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 24 |
| button | 7 |
| nav | 2 |
| search | 2 |
| metric | 1 |
| heading | 1 |
| button-primary | 1 |
| form | 1 |
| input | 1 |
| table | 1 |
| badge | 1 |
| modal | 1 |

- **Total komponen:** 43
- **Elemen interaktif:** 9
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% if is_edit %}Edit{% else %}Tambah{% endif %}Kategori
**File:** `category_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| input | 6 |
| nav | 1 |
| heading | 1 |
| card | 1 |
| badge | 1 |
| form | 1 |
| button | 1 |
| button-primary | 1 |

- **Total komponen:** 21
- **Elemen interaktif:** 8
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 customer
**File:** `customer.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|

- **Total komponen:** 0
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ customer.name }}
**File:** `customer_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 35 |
| metric | 10 |
| button | 5 |
| card | 3 |
| filter | 3 |
| heading | 2 |
| input | 2 |
| nav | 1 |
| badge | 1 |
| progressbar | 1 |
| table | 1 |
| dialog | 1 |
| form | 1 |

- **Total komponen:** 66
- **Elemen interaktif:** 7
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% if form.instance.pk %}Edit Pelanggan{% else %}Tambah Pelanggan Baru{% endif %}
**File:** `customer_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 10 |
| layout | 9 |
| button | 2 |
| alpine-root | 1 |
| nav | 1 |
| heading | 1 |
| form | 1 |
| card | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 13
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Direktori Pelanggan
**File:** `customers.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 29 |
| metric | 10 |
| button | 10 |
| input | 3 |
| nav | 2 |
| search | 2 |
| filter | 2 |
| heading | 1 |
| alpine-root | 1 |
| form | 1 |
| card | 1 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 64
- **Elemen interaktif:** 14
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Direktori Pelanggan
**File:** `customers_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 29 |
| metric | 10 |
| button | 10 |
| input | 3 |
| nav | 2 |
| search | 2 |
| filter | 2 |
| heading | 1 |
| alpine-root | 1 |
| form | 1 |
| card | 1 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 64
- **Elemen interaktif:** 14
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% trans "Locations" %}
**File:** `location_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 34 |
| button | 15 |
| input | 10 |
| metric | 8 |
| heading | 3 |
| modal | 3 |
| nav | 2 |
| search | 2 |
| card | 2 |
| image | 1 |
| badge | 1 |
| form | 1 |
| alert | 1 |

- **Total komponen:** 83
- **Elemen interaktif:** 18
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% trans "Locations" %}
**File:** `locations.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 34 |
| button | 15 |
| input | 10 |
| metric | 8 |
| heading | 3 |
| modal | 3 |
| nav | 2 |
| search | 2 |
| card | 2 |
| image | 1 |
| badge | 1 |
| form | 1 |
| alert | 1 |

- **Total komponen:** 83
- **Elemen interaktif:** 18
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ form_title }}
**File:** `payment_terms_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ page_title }}
**File:** `payment_terms_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ page_title }}
**File:** `reason_codes.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Stock Opname
**File:** `stock_opname.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 19 |
| button | 12 |
| heading | 10 |
| section | 4 |
| input | 4 |
| nav | 2 |
| form | 2 |
| search | 2 |
| metric | 1 |
| alpine-root | 1 |
| ol | 1 |
| table | 1 |

- **Total komponen:** 59
- **Elemen interaktif:** 18
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Approval Detail —{{ approval.location.name }}
**File:** `stock_opname_session_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| heading | 5 |
| button | 5 |
| metric | 1 |
| alpine-root | 1 |
| nav | 1 |
| ol | 1 |
| section | 1 |
| table | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 6
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ page_title }}
**File:** `tags_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ form_title }}
**File:** `tax_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ page_title }}
**File:** `tax_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {% if is_edit %}Edit{% else %}Tambah{% endif %}Satuan
**File:** `unit_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 24 |
| input | 5 |
| card | 4 |
| nav | 1 |
| heading | 1 |
| form | 1 |
| badge | 1 |
| button | 1 |
| alert | 1 |

- **Total komponen:** 39
- **Elemen interaktif:** 6
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Units —Satuan Ukur
**File:** `units_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 30 |
| button | 14 |
| card | 7 |
| filter | 6 |
| input | 3 |
| nav | 2 |
| heading | 2 |
| search | 2 |
| table | 1 |
| badge | 1 |
| modal | 1 |
| alert | 1 |

- **Total komponen:** 70
- **Elemen interaktif:** 20
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class=''
- ℹ input_no_label: Input tanpa label/placeholder: <input> id='' class='w-3.5 h-3.5 accent-emerald-500 rounded cursor-poin'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ vendor.name }}
**File:** `vendor_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 48 |
| button | 4 |
| filter | 3 |
| badge | 2 |
| input | 2 |
| nav | 1 |
| hero | 1 |
| heading | 1 |
| table | 1 |
| timeline | 1 |

- **Total komponen:** 64
- **Elemen interaktif:** 6
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 PartnerVendors
**File:** `vendor_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 37 |
| badge | 11 |
| button | 9 |
| nav | 2 |
| search | 2 |
| input | 2 |
| metric | 1 |
| heading | 1 |
| form | 1 |
| card | 1 |
| table | 1 |
| modal | 1 |

- **Total komponen:** 69
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 PartnerVendors
**File:** `vendors_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 37 |
| badge | 11 |
| button | 9 |
| nav | 2 |
| search | 2 |
| input | 2 |
| metric | 1 |
| heading | 1 |
| form | 1 |
| card | 1 |
| table | 1 |
| modal | 1 |

- **Total komponen:** 69
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ form_title }}
**File:** `broadcast.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Tulis Pesan Baru
**File:** `compose.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 12 |
| card | 2 |
| badge | 2 |
| button | 2 |
| nav | 1 |
| heading | 1 |
| form | 1 |
| input | 1 |
| button-primary | 1 |

- **Total komponen:** 23
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Pesan Pribadi
**File:** `inbox.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 16 |
| card | 6 |
| filter | 3 |
| search | 2 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 message_detail
**File:** `message_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| button | 2 |
| nav | 1 |
| heading | 1 |
| calendar | 1 |
| badge | 1 |
| form | 1 |
| input | 1 |

- **Total komponen:** 16
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ page_title }}
**File:** `message_templates.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 2 |
| heading | 1 |
| input | 1 |
| button | 1 |
| search | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Inbox
**File:** `notification.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 26 |
| button | 21 |
| card | 6 |
| filter | 6 |
| search | 3 |
| nav | 2 |
| heading | 2 |
| input | 2 |
| badge | 1 |
| modal | 1 |
| alert | 1 |

- **Total komponen:** 71
- **Elemen interaktif:** 25
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='icon-btn'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='icon-btn'
- ℹ input_no_label: Input tanpa label/placeholder: <input> id='' class='mt-1 w-3.5 h-3.5 accent-emerald-500 rounded cursor'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ form_title }}
**File:** `step_business.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ form_title }}
**File:** `step_category.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ dashboard_title }}
**File:** `step_complete.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| layout | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ form_title }}
**File:** `step_location.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ dashboard_title }}
**File:** `welcome.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| layout | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Cetak Dokumen — CoffeeShop
**File:** `print_base.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|

- **Total komponen:** 0
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ dashboard_title }}
**File:** `print_credit_note.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| layout | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 print_delivery_note
**File:** `print_delivery_note.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| table | 1 |

- **Total komponen:** 1
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Invoice — CoffeeShop
**File:** `print_invoice.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| heading | 2 |
| table | 1 |

- **Total komponen:** 11
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 print_packing_slip
**File:** `print_packing_slip.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| table | 1 |

- **Total komponen:** 1
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Payment Receipt — CoffeeShop
**File:** `print_payment_receipt.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| heading | 2 |

- **Total komponen:** 10
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 print_production_order
**File:** `print_production_order.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| table | 1 |

- **Total komponen:** 1
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 print_purchase_order
**File:** `print_purchase_order.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| table | 2 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ table_no_header: Tabel tanpa <th>/<thead>: <table> id='' class='table-w-full'

---

## 📄 Quotation — CoffeeShop
**File:** `print_quotation.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |
| heading | 1 |
| table | 1 |

- **Total komponen:** 7
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Print Receipt
**File:** `print_receipt.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |
| heading | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Print Order — CoffeeShop
**File:** `print_sales_order.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|

- **Total komponen:** 0
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ dashboard_title }}
**File:** `print_stock_opname.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| layout | 1 |

- **Total komponen:** 2
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 
**File:** `bom_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| heading | 4 |
| card | 4 |
| input | 2 |
| alpine-root | 1 |
| button | 1 |
| progressbar | 1 |
| table | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% if is_edit %}Edit BOM{% else %}Buat BOM Baru{% endif %}
**File:** `bom_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 9 |
| input | 9 |
| card | 4 |
| button | 3 |
| heading | 2 |
| alpine-root | 1 |
| nav | 1 |
| table | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 13
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-rose-600 hover:text-rose-800'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Daftar Resep (Bill of Materials)
**File:** `bom_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 12 |
| filter | 4 |
| heading | 2 |
| badge | 2 |
| button | 2 |
| nav | 1 |
| input | 1 |
| search | 1 |
| card | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 4
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-white text-slate-700 rounded-lg tex'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-slate-800 text-white rounded-lg tex'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Finished Goods Receipt
**File:** `finished_goods_receipt.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| card | 7 |
| input | 5 |
| button | 4 |
| heading | 3 |
| alpine-root | 1 |
| nav | 1 |
| table | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 10
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Material Consumption
**File:** `material_consumption.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| card | 7 |
| input | 5 |
| button | 4 |
| heading | 3 |
| alpine-root | 1 |
| nav | 1 |
| table | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 10
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Production Costing
**File:** `production_costing.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| card | 7 |
| layout | 4 |
| heading | 2 |
| input | 2 |
| alpine-root | 1 |
| nav | 1 |
| button | 1 |
| table | 1 |

- **Total komponen:** 19
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 
**File:** `production_order_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 7 |
| button-primary | 3 |
| button | 2 |
| alpine-root | 1 |
| card | 1 |
| heading | 1 |
| gauge | 1 |
| input | 1 |

- **Total komponen:** 17
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='control-btn btn-start col-span-2'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='h-14 rounded-xl bg-slate-100 text-slate-600 font-b'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='h-14 rounded-xl bg-slate-100 text-slate-600 font-b'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='control-btn btn-stop'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='control-btn btn-complete disabled:opacity-50'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% if is_edit %}Edit SPK{% else %}Buat SPK{% endif %}
**File:** `production_order_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| input | 9 |
| heading | 2 |
| card | 2 |
| alpine-root | 1 |
| nav | 1 |
| button | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Production Orders
**File:** `production_order_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| card | 5 |
| button | 5 |
| heading | 2 |
| nav | 1 |
| input | 1 |
| badge | 1 |
| progressbar | 1 |

- **Total komponen:** 27
- **Elemen interaktif:** 6
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Production Scheduling
**File:** `production_scheduling.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| card | 6 |
| layout | 4 |
| calendar | 3 |
| button | 2 |
| alpine-root | 1 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 19
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Production Waste
**File:** `production_waste.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| card | 8 |
| input | 7 |
| button | 5 |
| heading | 4 |
| alpine-root | 1 |
| nav | 1 |
| table | 1 |
| section | 1 |

- **Total komponen:** 38
- **Elemen interaktif:** 15
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 
**File:** `recipe_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| card | 8 |
| heading | 5 |
| alpine-root | 1 |
| nav | 1 |
| input | 1 |
| table | 1 |
| section | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {% if is_edit %}Edit Recipe{% else %}Buat Recipe Baru{% endif %}
**File:** `recipe_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 10 |
| layout | 5 |
| card | 4 |
| button | 3 |
| heading | 2 |
| alpine-root | 1 |
| nav | 1 |
| form | 1 |

- **Total komponen:** 27
- **Elemen interaktif:** 14
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full rounded-xl border border-slate-200 px-3 py-'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Daftar Recipe
**File:** `recipe_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 9 |
| card | 7 |
| button | 7 |
| heading | 3 |
| input | 2 |
| alpine-root | 1 |
| nav | 1 |
| table | 1 |

- **Total komponen:** 31
- **Elemen interaktif:** 10
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-rose-600 hover:text-rose-800'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 
**File:** `rnd_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| button | 7 |
| card | 4 |
| alpine-root | 1 |
| nav | 1 |
| badge | 1 |
| heading | 1 |
| filter | 1 |
| compare | 1 |

- **Total komponen:** 27
- **Elemen interaktif:** 9
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='trial-tab'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 
**File:** `rnd_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 18 |
| layout | 14 |
| button | 7 |
| card | 7 |
| table-row | 2 |
| alpine-root | 1 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 52
- **Elemen interaktif:** 16
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-violet-400 hover:text-violet-700 leading-none'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Lab Riset & Pengembangan
**File:** `rnd_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 13 |
| filter | 5 |
| heading | 2 |
| progressbar | 2 |
| button | 2 |
| nav | 1 |
| input | 1 |
| search | 1 |
| card | 1 |

- **Total komponen:** 28
- **Elemen interaktif:** 3
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-white text-slate-700 rounded-lg tex'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-slate-800 text-white rounded-lg tex'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 📋 Activity Log
**File:** `activity_log.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 15 |
| input | 4 |
| button | 3 |
| heading | 2 |
| search | 1 |
| nav | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 7
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 📊 {{ report_title }}
**File:** `base_report.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 13 |
| button | 5 |
| heading | 2 |
| input | 2 |
| alpine-root | 1 |
| form | 1 |
| nav | 1 |

- **Total komponen:** 25
- **Elemen interaktif:** 8
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Sales Report
**File:** `purchasing_report.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 34 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 89
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 📋 Activity Log
**File:** `report_activity_log.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 15 |
| input | 4 |
| button | 3 |
| heading | 2 |
| search | 1 |
| nav | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 7
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Laporan Customer Lifetime Value
**File:** `report_customer_lifetime.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| heading | 5 |
| card | 2 |
| button | 1 |
| calendar | 1 |
| badge | 1 |

- **Total komponen:** 20
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Laporan Kedaluwarsa (Expiry)
**File:** `report_expiry.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| heading | 3 |
| card | 3 |
| button | 2 |
| input | 1 |

- **Total komponen:** 17
- **Elemen interaktif:** 5
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-emerald-600 hover:bg-emeral'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-white bg-rose-600 hover:bg-'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Inventory Aging Report
**File:** `report_inventory_age.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |
| card | 5 |
| button | 4 |
| heading | 1 |
| table | 1 |

- **Total komponen:** 16
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-rose-600 hover:text-rose-80'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-amber-600 hover:text-amber-'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_inventory_log.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_inventory_low.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_inventory_stock.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Laporan Produksi
**File:** `report_production.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |
| card | 5 |
| heading | 2 |
| input | 1 |
| metric | 1 |
| progressbar | 1 |
| table | 1 |

- **Total komponen:** 16
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_profit_loss_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_sales_by_outlet.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_sales_by_payment.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_sales_by_product.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `report_sales_summary.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Laporan Kinerja Karyawan
**File:** `report_staff_performance.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| heading | 2 |
| input | 1 |
| card | 1 |
| button | 1 |

- **Total komponen:** 16
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-4 py-2 bg-slate-50 text-slate-600 rounded-lg te'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Reporting Dashboard
**File:** `reporting.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 19 |
| button | 11 |
| heading | 5 |
| nav | 2 |
| input | 2 |
| alpine-root | 1 |
| ol | 1 |
| search | 1 |
| table | 1 |

- **Total komponen:** 43
- **Elemen interaktif:** 14
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='p-1.5 text-slate-400 hover:style='
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `requisition_report.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `sales_history.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 35 |
| button | 18 |
| metric | 12 |
| input | 11 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 96
- **Elemen interaktif:** 29
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `sales_history_product.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `sales_report.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 35 |
| button | 18 |
| metric | 12 |
| input | 11 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 96
- **Elemen interaktif:** 29
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 sales_report_after
**File:** `sales_report_after.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| metric | 1 |
| card | 1 |
| heading | 1 |
| button | 1 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 6
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Sales Report
**File:** `transaction_summary.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Report
**File:** `transfer_report.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| button | 16 |
| input | 11 |
| metric | 8 |
| badge | 4 |
| filter | 4 |
| card | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| heading | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 88
- **Elemen interaktif:** 27
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ input_no_label: Input tanpa label/placeholder: <input> id='searchInput' class='bar-input flex-1'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ detail_title }}
**File:** `invoice_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 3 |
| heading | 1 |
| button | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ form_title }}
**File:** `invoice_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Daftar Faktur
**File:** `invoice_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 12 |
| button | 4 |
| card | 4 |
| filter | 4 |
| search | 2 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 29
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-emerald-50 text-emerald-600 hover:b'
- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs text-emerald-600 font-bold px-2 flex items'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ form_title }}
**File:** `payment_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Riwayat Pembayaran
**File:** `payment_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| card | 4 |
| filter | 4 |
| button | 3 |
| search | 2 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-emerald-50 text-emerald-600 hover:b'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ detail_title }}
**File:** `retur_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 3 |
| heading | 1 |
| button | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ form_title }}
**File:** `retur_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Retur Penjualan
**File:** `retur_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| button | 4 |
| card | 4 |
| filter | 4 |
| search | 2 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 28
- **Elemen interaktif:** 4
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='text-xs text-slate-400 hover:text-slate-600 px-2'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ detail_title }}
**File:** `quotation_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 3 |
| heading | 1 |
| button | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ form_title }}
**File:** `quotation_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Daftar Penawaran
**File:** `quotation_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| card | 4 |
| filter | 4 |
| button | 3 |
| search | 2 |
| nav | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 27
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ⚠ **empty_button:** Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-emerald-50 text-emerald-600 hover:b'
- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 {{ detail_title }}
**File:** `sales_order_detail.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 3 |
| heading | 1 |
| button | 1 |

- **Total komponen:** 5
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 {{ form_title }}
**File:** `sales_order_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 1 |
| form | 1 |
| layout | 1 |
| button | 1 |

- **Total komponen:** 4
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Daftar Sales Order
**File:** `sales_order_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| card | 4 |
| filter | 4 |
| button | 2 |
| search | 2 |
| badge | 2 |
| nav | 1 |
| heading | 1 |

- **Total komponen:** 27
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 DASHBOARD
**File:** `dashboard.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 49 |
| button | 11 |
| section | 6 |
| heading | 4 |
| article | 4 |
| card | 4 |
| breadcrumb | 3 |
| input | 3 |
| alpine-root | 2 |
| header | 1 |
| search | 1 |
| ul | 1 |
| alert | 1 |

- **Total komponen:** 90
- **Elemen interaktif:** 16
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Financial Reports
**File:** `financial_reports.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 42 |
| metric | 15 |
| card | 12 |
| progressbar | 6 |
| badge | 5 |
| filter | 5 |
| button | 3 |
| input | 3 |
| nav | 1 |
| heading | 1 |
| form | 1 |
| calendar | 1 |

- **Total komponen:** 95
- **Elemen interaktif:** 6
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Market Insights
**File:** `market_insights.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 33 |
| metric | 26 |
| card | 18 |
| empty | 7 |
| calendar | 3 |
| input | 3 |
| filter | 3 |
| badge | 2 |
| button | 2 |
| nav | 1 |
| heading | 1 |
| form | 1 |

- **Total komponen:** 100
- **Elemen interaktif:** 5
- **Container dengan scroll:** 1
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Point of Sale
**File:** `pos.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 39 |
| button | 13 |
| input | 5 |
| search | 3 |
| filter | 3 |
| card | 3 |
| heading | 2 |
| image | 2 |
| badge | 2 |
| header | 1 |
| section | 1 |
| aside | 1 |
| alert | 1 |
| modal | 1 |

- **Total komponen:** 77
- **Elemen interaktif:** 21
- **Container dengan scroll:** 3
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales History
**File:** `sales_intelligence.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 31 |
| button | 12 |
| input | 8 |
| badge | 5 |
| filter | 3 |
| nav | 2 |
| search | 2 |
| calendar | 2 |
| card | 2 |
| heading | 1 |
| modal | 1 |
| form | 1 |
| table | 1 |

- **Total komponen:** 71
- **Elemen interaktif:** 21
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Sales Performance
**File:** `sales_performance.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 34 |
| button | 11 |
| card | 9 |
| metric | 8 |
| input | 8 |
| badge | 3 |
| filter | 3 |
| heading | 2 |
| form | 2 |
| progressbar | 2 |
| modal | 2 |
| hero | 1 |
| nav | 1 |
| calendar | 1 |

- **Total komponen:** 87
- **Elemen interaktif:** 20
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 📈 Trends Analysis
**File:** `trends_analysis.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 18 |
| heading | 8 |
| input | 2 |
| form | 1 |
| button | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Bukan SekadarSoftware.IniLegacy.
**File:** `about.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 17 |
| card | 17 |
| badge | 11 |
| layout | 10 |
| hero | 8 |
| section | 7 |
| button | 3 |

- **Total komponen:** 73
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 API Keys
**File:** `api_keys.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| heading | 2 |
| button | 2 |
| nav | 1 |
| card | 1 |

- **Total komponen:** 16
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 backup_restore
**File:** `backup_restore.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 8 |
| card | 3 |
| heading | 3 |
| input | 3 |
| button | 2 |

- **Total komponen:** 19
- **Elemen interaktif:** 5
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 V-SeriesEngine
**File:** `business_feature_matrix.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| hero | 4 |
| layout | 3 |
| heading | 2 |
| button | 2 |
| badge | 2 |
| filter | 2 |
| metric | 1 |
| card | 1 |

- **Total komponen:** 17
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 ProfilPerusahaan
**File:** `business_form_general.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 22 |
| input | 22 |
| image | 2 |
| button | 2 |
| metric | 1 |
| heading | 1 |

- **Total komponen:** 50
- **Elemen interaktif:** 24
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 ProfilPerusahaan
**File:** `business_profile.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| input | 22 |
| card | 11 |
| layout | 2 |
| image | 2 |
| button | 2 |
| metric | 1 |
| heading | 1 |
| badge | 1 |

- **Total komponen:** 42
- **Elemen interaktif:** 25
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 business_settings
**File:** `business_settings.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 28 |
| button | 10 |
| input | 8 |
| badge | 5 |
| card | 2 |
| metric | 1 |
| hero | 1 |
| heading | 1 |
| modal | 1 |

- **Total komponen:** 57
- **Elemen interaktif:** 20
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 📞 Contact Us
**File:** `contact.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| heading | 10 |
| button | 6 |
| input | 5 |
| layout | 3 |
| form | 2 |

- **Total komponen:** 26
- **Elemen interaktif:** 11
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Konfigurasi SMTP
**File:** `email_settings.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| input | 8 |
| heading | 2 |
| button | 2 |
| card | 1 |
| form | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 3
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Pengaturan Notifikasi
**File:** `notification_settings.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 12 |
| input | 7 |
| heading | 4 |
| card | 3 |
| button | 1 |

- **Total komponen:** 27
- **Elemen interaktif:** 8
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Pengaturan Nomor Otomatis
**File:** `numbering_settings.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 16 |
| input | 7 |
| heading | 4 |
| card | 2 |
| button | 1 |

- **Total komponen:** 30
- **Elemen interaktif:** 8
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Permission Matrix
**File:** `permission_matrix.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 7 |
| button | 2 |
| heading | 1 |
| card | 1 |
| table | 1 |

- **Total komponen:** 12
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 PersonalIdentity
**File:** `profile.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 32 |
| input | 14 |
| button | 9 |
| button-primary | 5 |
| form | 4 |
| filter | 3 |
| modal | 3 |
| heading | 2 |
| image | 2 |
| metric | 1 |
| card | 1 |

- **Total komponen:** 76
- **Elemen interaktif:** 23
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Konfigurasi Role
**File:** `role_form.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 10 |
| input | 9 |
| heading | 4 |
| alpine-root | 1 |
| card | 1 |
| button | 1 |

- **Total komponen:** 26
- **Elemen interaktif:** 8
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Manajemen Roles
**File:** `roles.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 7 |
| heading | 2 |
| button | 2 |
| nav | 1 |
| card | 1 |
| badge | 1 |

- **Total komponen:** 14
- **Elemen interaktif:** 2
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 🔍 Search Results
**File:** `search.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 11 |
| heading | 10 |
| filter | 8 |
| input | 3 |
| button | 2 |
| nav | 2 |
| form | 1 |
| search | 1 |

- **Total komponen:** 38
- **Elemen interaktif:** 9
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Pusat Pengaturan
**File:** `settings.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 13 |
| heading | 10 |
| card | 1 |

- **Total komponen:** 24
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 System Status
**File:** `system_status.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 9 |
| card | 7 |
| heading | 4 |
| table | 1 |

- **Total komponen:** 21
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 user_list
**File:** `user_list.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|

- **Total komponen:** 0
- **Elemen interaktif:** 0
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## 📄 Roles &Permissions
**File:** `user_roles_permissions.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 34 |
| metric | 9 |
| button | 5 |
| input | 4 |
| badge | 3 |
| heading | 2 |
| nav | 1 |
| filter | 1 |
| table | 1 |
| modal | 1 |

- **Total komponen:** 61
- **Elemen interaktif:** 9
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

### Isu & Temuan

- ℹ alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

---

## 📄 Users & Roles
**File:** `users.html`

### Statistik Komponen

| Tipe | Jumlah |
|------|--------|
| layout | 5 |
| card | 5 |
| heading | 1 |
| input | 1 |
| table | 1 |
| badge | 1 |

- **Total komponen:** 14
- **Elemen interaktif:** 1
- **Container dengan scroll:** 0
- **Scroll nesting:** 0

---

## Pola Lintas File

### Komponen Paling Banyak Digunakan

| Tipe | Total (semua file) |
|------|-------------------|
| layout | 2628 |
| button | 911 |
| input | 720 |
| card | 440 |
| heading | 401 |
| metric | 272 |
| badge | 215 |
| filter | 170 |
| nav | 134 |
| search | 132 |

### File dengan Isu Terbanyak

- **activity_drawer** (`activity_drawer.html`): 10 isu
- **** (`production_order_detail.html`): 6 isu
- **** (`requisition_detail.html`): 5 isu
- **sidebar_right** (`sidebar_right.html`): 4 isu
- **Inventory Planner** (`stock_overview.html`): 4 isu

## Rekomendasi Perbaikan

### 🟢 Info — Alpine Xcloak
**Ditemukan di:** ``, `API Keys`, `Accounts Payable` dan 99 lainnya
**Rekomendasi:** Pastikan CSS `[x-cloak] { display: none !important; }` ada di base template untuk mencegah flash of unstyled content.

### 🟠 Penting — Empty Button
**Ditemukan di:** ``, `Accounts Payable`, `Daftar Faktur` dan 25 lainnya
**Rekomendasi:** Semua tombol harus memiliki teks label atau `aria-label` untuk aksesibilitas screen reader.

### 🟡 Disarankan — Input No Label
**Ditemukan di:** `Inbox`, `Sales Report`, `Units —Satuan Ukur` dan 1 lainnya
**Rekomendasi:** Setiap input form sebaiknya memiliki `<label>` yang terhubung via `for` attribute, atau minimal `aria-label` / `placeholder` yang deskriptif.

### 🟡 Disarankan — Table No Header
**Ditemukan di:** `print_purchase_order`
**Rekomendasi:** Tabel data sebaiknya selalu memiliki baris header `<th>` dalam `<thead>` untuk aksesibilitas dan readability.

---

*Laporan ini dibuat otomatis oleh UI Reverse Engineer.*
*Generated: 27 April 2026 09:43*