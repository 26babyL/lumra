# Claude Handoff: accounting

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 13
Jumlah view terkait: 13

## Template Scope

### lumra_pages/accounting/accounts_payable.html
- File: `lumra_config/templates/lumra_pages/accounting/accounts_payable.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=17, interactive=2, issues=2, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Keuangan / Hutang Usaha (AP)
  - HEADING (H1): Accounts Payable
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Total Hutang
  - CARD: Jatuh Tempo (0-30 Hari)
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-xs font-bold text-slate-500 hover:text-emeral'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/accounts_receivable.html
- File: `lumra_config/templates/lumra_pages/accounting/accounts_receivable.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=17, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Keuangan / Piutang Usaha (AR)
  - HEADING (H1): Accounts Receivable
  - BUTTON: Kirim Pengingat: Kirim Pengingat
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Total Piutang
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/balance_sheet.html
- File: `lumra_config/templates/lumra_pages/accounting/balance_sheet.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=16, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Neraca (Balance Sheet)
  - CARD: Per
  - INPUT [date] asOfDate: asOfDate
  - BUTTON: [icon]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Aset
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/cash_flow.html
- File: `lumra_config/templates/lumra_pages/accounting/cash_flow.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=9, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Laporan Arus Kas (Cash Flow)
  - CARD: Periode
  - INPUT [month] period: period
  - BUTTON: [icon]: 
  - CARD: Cash Flow untuk Periode Berakhir Aktivitas Operasional Arus Kas Bersih dari Akti…
  - HEADING (H2): Cash Flow untuk Periode Berakhir
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/chart_of_accounts.html
- File: `lumra_config/templates/lumra_pages/accounting/chart_of_accounts.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=18, interactive=7, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Keuangan / Chart of Accounts
  - HEADING (H1): Buku Besar Pembantu (COA)
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: Semua Asset Liability Equity Pendapatan Beban
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Semua: Semua
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/general_ledger.html
- File: `lumra_config/templates/lumra_pages/accounting/general_ledger.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=11, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: Buku Besar (General Ledger) Akun {% for account in accounts %} {{ account.code }…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): Buku Besar (General Ledger)
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [select] account: account
  - INPUT [month] period: period
  - CARD: {{ account_name }} Saldo Awal Tanggal Ref Keterangan Debit Kredit Saldo Saldo Aw…

### lumra_pages/accounting/journal_entry_list.html
- File: `lumra_config/templates/lumra_pages/accounting/journal_entry_list.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=18, interactive=5, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Keuangan / Jurnal Umum
  - HEADING (H1): Journal Entry List
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Semua: Semua
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/profit_loss_statement.html
- File: `lumra_config/templates/lumra_pages/accounting/profit_loss_statement.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=15, interactive=1, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Laporan Laba Rugi
  - CARD: Periode
  - INPUT [month] period: period
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Total Pendapatan
  - CARD: Total Beban
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/trial_balance.html
- File: `lumra_config/templates/lumra_pages/accounting/trial_balance.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=17, interactive=4, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Neraca Percobaan (Trial Balance)
  - CARD: Periode
  - INPUT [month] period: period
  - BUTTON: [icon]: 
  - BUTTON: [icon]: 
  - CARD: Total Debit = Total Kredit Selisih
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/chart_of_accounts_form.html
- File: `lumra_config/templates/lumra_pages/accounting/chart_of_accounts_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=14, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: Buat Akun Baru Menambahkan struktur ke Chart of Accounts. {% csrf_token %} Kode…
  - HEADING (H1): Buat Akun Baru
  - [ FORM ]: {% csrf_token %} Kode Akun Cek Ketersediaan Nama Akun Tipe Akun Asset (Aset) Lia…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT FIELD: 
  - BUTTON: Cek Ketersediaan: Cek Ketersediaan
  - INPUT FIELD: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/journal_entry_detail.html
- File: `lumra_config/templates/lumra_pages/accounting/journal_entry_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=12, interactive=3, issues=0, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [journalDetailApp()]: Tanggal: Deskripsi Akun Debit Kredit Total Dibuat pada {{ en…
  - CARD: Tanggal: Deskripsi Akun Debit Kredit Total Dibuat pada {{ entry.created_at|date:…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): 
  - HERO / BANNER: 
  - [ TABLE ]: Akun Debit Kredit Total
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/accounting/journal_entry_form.html
- File: `lumra_config/templates/lumra_pages/accounting/journal_entry_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=22, interactive=5, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [journalFormApp()]: Input Jurnal Umum Pastikan Debit dan Kredit seimbang. Batal…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Input Jurnal Umum
  - CARD: {% csrf_token %} Tanggal Transaksi No. Referensi Deskripsi Transaksi Akun Debit…
  - INPUT [hidden] lines_json: lines_json
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - INPUT FIELD: 
  - INPUT FIELD: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/accounting/payment_voucher_form.html
- File: `lumra_config/templates/lumra_pages/accounting/payment_voucher_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=25, interactive=9, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [paymentVoucherApp()]: Payment Voucher (PV) Dokumen bukti pengeluaran kas / bank. B…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Payment Voucher (PV)
  - CARD: {% csrf_token %} No. Bukti Tanggal Bayar Dibayar Kepada (Supplier) -- Pilih Supp…
  - INPUT [hidden] number: number
  - INPUT [hidden] selected_invoice_ids: selected_invoice_ids
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - INPUT FIELD: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### chart_of_accounts
- File: `lumra_config/views/accounting_views.py`:131
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def chart_of_accounts(request):
    accounts = Account.objects.select_related("parent").all()
    context = {
        "accounts": accounts,
        "accounts_json": json.dumps(_serialize_accounts(accounts)),
    }
    return render(request, "lumra_pages/accounting/chart_of_accounts.html", context)
```

### chart_of_accounts_form
- File: `lumra_config/views/accounting_views.py`:184
- Decorators: `login_required`, `atomic`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def chart_of_accounts_form(request, pk=None):
    account = get_object_or_404(Account, pk=pk) if pk else None

    if request.method == "POST":
        parent = None
        parent_id = request.POST.get("parent_id")
        if parent_id:
            parent = get_object_or_404(Account, pk=parent_id)

        payload = {
            "code": request.POST.get("code", "").strip(),
            "name": request.POST.get("name", "").strip(),
            "account_type": request.POST.get("type", "asset"),
            "level": int(request.POST.get("level", "2") or 2),
            "parent": parent,
            "notes": request.POST.get("notes", "").strip(),
            "allow_posting": request.POST.get("level", "2") != "1",
        }

        if account:
            for key, value in payload.items():
                setattr(account, key, value)
        else:
            account = Account(**payload)

        try:
            account.full_clean()
            account.save()
            messages.success(request, "Akun berhasil disimpan.")
            return redirect("chart_of_accounts")
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))

    parent_accounts = Account.objects.filter(level=1, is_active=True).order_by("code")
    form_data = {
        "code": getattr(account, "code", ""),
        "name": getattr(account, "name", ""),
        "type": getattr(account, "account_type", "asset"),
        "level": getattr(account, "level", 2),
        "parent_id": getattr(account, "parent_id", "") or "",
    }
    context = {
        "account": account,
        "form_data": form_data,
        "generated_code": getattr(account, "code", ""),
        "parent_accounts": parent_accounts,
        "parent_accounts_json": json.dumps(_serialize_accounts(parent_accounts)),
    }
    return render(request, "lumra_pages/accounting/chart_of_accounts_form.html", context)
```

### general_ledger
- File: `lumra_config/views/accounting_views.py`:230
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def general_ledger(request):
    period = request.GET.get("period") or timezone.localdate().strftime("%Y-%m")
    start_date, end_date = _month_window(period)
    accounts = Account.objects.filter(allow_posting=True, is_active=True).order_by("code")
    selected_account = accounts.filter(pk=request.GET.get("account")).first() or accounts.first()

    ledger_rows = []
    opening_balance = Decimal("0")
    account_name = "-"

    if selected_account:
        account_name = f"{selected_account.code} {selected_account.name}"
        opening_balance = _account_balance(selected_account, start_date - timedelta(days=1))
        running_balance = opening_balance
        lines = JournalEntryLine.objects.filter(
            account=selected_account,
            journal_entry__status="posted",
            journal_entry__date__range=(start_date, end_date),
        ).select_related("journal_entry").order_by("journal_entry__date", "id")

        for line in lines:
            running_balance += _account_delta(selected_account, line.debit, line.credit)
            ledger_rows.append(
                {
                    "id": line.id,
                    "date": line.journal_entry.date.isoformat(),
                    "ref": line.journal_entry.number,
                    "desc": line.description or line.journal_entry.description,
                    "debit": float(line.debit),
                    "credit": float(line.credit),
                    "balance": float(running_balance),
                }
            )

    context = {
        "accounts": accounts,
        "selected_account_id": str(selected_account.id) if selected_account else "",
        "period": period,
        "account_name": account_name,
        "opening_balance": float(opening_balance),
        "transactions_json": json.dumps(ledger_rows),
    }
    return render(request, "lumra_pages/accounting/general_ledger.html", context)
```

### journal_entry_list
- File: `lumra_config/views/accounting_views.py`:240
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def journal_entry_list(request):
    journals = JournalEntry.objects.prefetch_related("lines").all()
    context = {
        "journals": journals,
        "journals_json": json.dumps([_serialize_journal(entry) for entry in journals]),
    }
    return render(request, "lumra_pages/accounting/journal_entry_list.html", context)
```

### journal_entry_form
- File: `lumra_config/views/accounting_views.py`:313
- Decorators: `login_required`, `atomic`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def journal_entry_form(request, pk=None):
    entry = get_object_or_404(JournalEntry.objects.prefetch_related("lines"), pk=pk) if pk else None

    if request.method == "POST":
        lines_raw = request.POST.get("lines_json", "[]")
        description = request.POST.get("description", "").strip()
        try:
            lines_payload = json.loads(lines_raw)
        except json.JSONDecodeError:
            lines_payload = []

        total_debit = Decimal("0")
        total_credit = Decimal("0")
        validated_lines = []
        for item in lines_payload:
            account_id = item.get("account_id")
            if not account_id:
                continue
            line = JournalEntryLine(
                account=get_object_or_404(Account, pk=account_id, allow_posting=True),
                debit=_decimal(item.get("debit")),
                credit=_decimal(item.get("credit")),
            )
            line.full_clean(exclude=["journal_entry"])
            validated_lines.append(line)
            total_debit += line.debit
            total_credit += line.credit

        if not description:
            messages.error(request, "Deskripsi jurnal wajib diisi.")
        elif total_debit <= 0 or total_debit != total_credit:
            messages.error(request, "Debit dan kredit harus seimbang.")
        else:
            if not entry:
                entry = JournalEntry(number=_generate_number("JE", JournalEntry), created_by=request.user)
            entry.date = _parse_date(request.POST.get("date"))
            entry.description = description
            entry.reference = request.POST.get("reference", "").strip()
            entry.source = "manual"
            entry.status = "draft"
            entry.save()
            entry.lines.all().delete()
            for line in validated_lines:
                line.journal_entry = entry
                line.save()
            messages.success(request, "Jurnal berhasil disimpan sebagai draft.")
            return redirect("journal_entry_detail", pk=entry.pk)

    posting_accounts = Account.objects.filter(allow_posting=True, is_active=True).order_by("code")
    initial_lines = []
    if entry:
        initial_lines = [
            {
                "account_id": line.account_id,
                "debit": float(line.debit),
                "credit": float(line.credit),
            }
            for line in entry.lines.select_related("account").all()
        ]
    if not initial_lines:
        initial_lines = [{"account_id": "", "debit": 0, "credit": 0}, {"account_id": "", "debit": 0, "credit": 0}]

    context = {
        "entry": entry,
        "generated_number": entry.number if entry else _generate_number("JE", JournalEntry),
        "posting_accounts_json": json.dumps(_serialize_accounts(posting_accounts)),
        "initial_lines_json": json.dumps(initial_lines),
    }
    return render(request, "lumra_pages/accounting/journal_entry_form.html", context)
```

### journal_entry_detail
- File: `lumra_config/views/accounting_views.py`:349
- Decorators: `login_required`, `atomic`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def journal_entry_detail(request, pk):
    entry = get_object_or_404(JournalEntry.objects.prefetch_related("lines__account"), pk=pk)

    if request.method == "POST" and request.POST.get("action") == "post":
        if not entry.is_balanced:
            messages.error(request, "Jurnal tidak seimbang, posting dibatalkan.")
        elif entry.status == "posted":
            messages.info(request, "Jurnal sudah berstatus posted.")
        else:
            entry.status = "posted"
            entry.posted_by = request.user
            entry.posted_at = timezone.now()
            entry.save(update_fields=["status", "posted_by", "posted_at", "updated_at"])
            messages.success(request, "Jurnal berhasil di-posting.")
        return redirect("journal_entry_detail", pk=entry.pk)

    lines_json = [
        {
            "id": line.id,
            "account_code": line.account.code,
            "account_name": line.account.name,
            "debit": float(line.debit),
            "credit": float(line.credit),
        }
        for line in entry.lines.all()
    ]
    context = {
        "entry": entry,
        "lines_json": json.dumps(lines_json),
        "total_amount": float(entry.total_amount),
    }
    return render(request, "lumra_pages/accounting/journal_entry_detail.html", context)
```

### payment_voucher_form
- File: `lumra_config/views/accounting_views.py`:458
- Decorators: `login_required`, `atomic`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def payment_voucher_form(request, pk=None):
    voucher = get_object_or_404(PaymentVoucher.objects.prefetch_related("allocations"), pk=pk) if pk else None
    vendors = Vendor.objects.filter(is_active=True).order_by("name")
    cash_accounts = Account.objects.filter(allow_posting=True, is_cash_account=True, is_active=True).order_by("code")
    ap_account = _resolve_ap_account()

    if request.method == "POST":
        selected_ids_raw = request.POST.get("selected_invoice_ids", "[]")
        try:
            selected_ids = json.loads(selected_ids_raw)
        except json.JSONDecodeError:
            selected_ids = []

        invoice_map = {
            invoice.id: invoice
            for invoice in AccountsPayableEntry.objects.select_related("vendor").filter(pk__in=selected_ids)
        }
        allocations = []
        allocation_total = Decimal("0")
        for invoice_id in selected_ids:
            invoice = invoice_map.get(invoice_id)
            if invoice and invoice.balance > 0:
                allocations.append((invoice, invoice.balance))
                allocation_total += invoice.balance

        amount_paid = _decimal(request.POST.get("amount_paid"))
        vendor = get_object_or_404(Vendor, pk=request.POST.get("supplier_id"))
        cash_account = get_object_or_404(Account, pk=request.POST.get("bank_id"), allow_posting=True)

        if not allocations:
            messages.error(request, "Pilih minimal satu invoice hutang.")
        elif amount_paid != allocation_total:
            messages.error(request, "Jumlah dibayar harus sama dengan total invoice terpilih.")
        elif ap_account is None:
            messages.error(request, "Belum ada akun hutang usaha yang bisa dipakai posting.")
        else:
            journal = JournalEntry.objects.create(
                number=_generate_number("JE", JournalEntry),
                date=_parse_date(request.POST.get("date")),
                reference=request.POST.get("number") or _generate_number("PV", PaymentVoucher),
                description=request.POST.get("memo", "").strip() or f"Payment voucher {vendor.name}",
                status="posted",
                source="payment_voucher",
                created_by=request.user,
                posted_by=request.user,
                posted_at=timezone.now(),
            )
            JournalEntryLine.objects.create(
                journal_entry=journal,
                account=ap_account,
                debit=amount_paid,
                credit=Decimal("0"),
                description=f"Pelunasan hutang {vendor.name}",
            )
            JournalEntryLine.objects.create(
                journal_entry=journal,
                account=cash_account,
                debit=Decimal("0"),
                credit=amount_paid,
                description=f"Pembayaran dari {cash_account.name}",
            )

            voucher = PaymentVoucher.objects.create(
                number=request.POST.get("number") or _generate_number("PV", PaymentVoucher),
                date=_parse_date(request.POST.get("date")),
                vendor=vendor,
                cash_account=cash_account,
                method=request.POST.get("method", "transfer"),
                memo=request.POST.get("memo", "").strip(),
                amount_paid=amount_paid,
                created_by=request.user,
                journal_entry=journal,
            )

            for invoice, amount in allocations:
                PaymentVoucherAllocation.objects.create(voucher=voucher, payable_entry=invoice, amount=amount)
                invoice.paid_amount += amount
                invoice.status = "paid" if invoice.paid_amount >= invoice.total_amount else "partial"
                invoice.save(update_fields=["paid_amount", "status", "updated_at"])

            messages.success(request, "Payment voucher berhasil diproses.")
            return redirect("accounts_payable")

    payables = AccountsPayableEntry.objects.select_related("vendor").filter(status__in=["open", "partial"]).order_by("due_date")
    payables_by_vendor = {}
    for payable in payables:
        payables_by_vendor.setdefault(payable.vendor_id, []).append(
            {
                "id": payable.id,
                "number": payable.invoice_number,
                "total": float(payable.total_amount),
                "balance": float(payable.balance),
                "due_date": payable.due_date.isoformat(),
            }
        )

    context = {
        "voucher": voucher,
        "generated_number": voucher.number if voucher else _generate_number("PV", PaymentVoucher),
        "vendors": vendors,
        "cash_accounts": cash_accounts,
        "selected_vendor_id": request.GET.get("vendor", ""),
        "payables_json": json.dumps(payables_by_vendor),
    }
    return render(request, "lumra_pages/accounting/payment_voucher_form.html", context)
```

### trial_balance
- File: `lumra_config/views/accounting_views.py`:501
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def trial_balance(request):
    period = request.GET.get("period") or timezone.localdate().strftime("%Y-%m")
    _, end_date = _month_window(period)
    groups = []
    grand_debit = Decimal("0")
    grand_credit = Decimal("0")

    for account_type, label in Account.ACCOUNT_TYPES:
        accounts = []
        for account in Account.objects.filter(account_type=account_type, is_active=True).order_by("code"):
            balance = _account_balance(account, end_date)
            debit, credit = _balance_to_columns(account, balance)
            accounts.append(
                {
                    "code": account.code,
                    "name": account.name,
                    "debit": float(debit),
                    "credit": float(credit),
                }
            )
        total_debit = sum(Decimal(str(item["debit"])) for item in accounts)
        total_credit = sum(Decimal(str(item["credit"])) for item in accounts)
        grand_debit += total_debit
        grand_credit += total_credit
        groups.append(
            {
                "name": label.upper(),
                "accounts": accounts,
                "totalDebit": float(total_debit),
                "totalCredit": float(total_credit),
            }
        )

    context = {
        "period": period,
        "account_groups_json": json.dumps(groups),
        "grand_total_debit": float(grand_debit),
        "grand_total_credit": float(grand_credit),
    }
    return render(request, "lumra_pages/accounting/trial_balance.html", context)
```

### balance_sheet
- File: `lumra_config/views/accounting_views.py`:538
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def balance_sheet(request):
    as_of_date = _parse_date(request.GET.get("as_of_date"), timezone.localdate())

    def collect(account_type):
        items = []
        total = Decimal("0")
        for account in Account.objects.filter(account_type=account_type, allow_posting=True, is_active=True).order_by("code"):
            balance = _account_balance(account, as_of_date)
            if balance:
                items.append({"name": f"{account.code} {account.name}", "amount": float(balance)})
                total += balance
        return items, total

    asset_items, total_assets = collect("asset")
    liability_items, total_liabilities = collect("liability")
    equity_items, total_equity = collect("equity")
    revenue_items, total_revenue = collect("revenue")
    expense_items, total_expense = collect("expense")
    current_earnings = total_revenue - total_expense
    if current_earnings:
        equity_items.append({"name": "Laba Tahun Berjalan", "amount": float(current_earnings)})
        total_equity += current_earnings

    context = {
        "as_of_date": as_of_date.isoformat(),
        "assets_current_json": json.dumps(asset_items),
        "assets_fixed_json": json.dumps([]),
        "liabilities_json": json.dumps(liability_items),
        "equity_json": json.dumps(equity_items),
        "total_assets": float(total_assets),
        "total_liabilities": float(total_liabilities),
        "total_equity": float(total_equity),
    }
    return render(request, "lumra_pages/accounting/balance_sheet.html", context)
```

### profit_loss_statement
- File: `lumra_config/views/accounting_views.py`:589
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def profit_loss_statement(request):
    period = request.GET.get("period") or timezone.localdate().strftime("%Y-%m")
    start_date, end_date = _month_window(period)

    def collect(account_type):
        items = []
        total = Decimal("0")
        accounts = Account.objects.filter(
            account_type=account_type,
            allow_posting=True,
            is_active=True,
        ).order_by("code")
        for account in accounts:
            lines = JournalEntryLine.objects.filter(
                account=account,
                journal_entry__status="posted",
                journal_entry__date__range=(start_date, end_date),
            )
            totals = lines.aggregate(debit=Sum("debit"), credit=Sum("credit"))
            debit = totals["debit"] or Decimal("0")
            credit = totals["credit"] or Decimal("0")
            amount = credit - debit if account_type == "revenue" else debit - credit
            if amount:
                items.append(
                    {
                        "code": account.code,
                        "name": account.name,
                        "amount": float(amount),
                    }
                )
                total += amount
        return items, total

    revenue_items, total_revenue = collect("revenue")
    expense_items, total_expense = collect("expense")
    gross_profit = total_revenue
    net_profit = total_revenue - total_expense

    context = {
        "period": period,
        "revenue_json": json.dumps(revenue_items),
        "expense_json": json.dumps(expense_items),
        "total_revenue": float(total_revenue),
        "total_expense": float(total_expense),
        "gross_profit": float(gross_profit),
        "net_profit": float(net_profit),
    }
    return render(request, "lumra_pages/accounting/profit_loss_statement.html", context)
```

### cash_flow_statement
- File: `lumra_config/views/accounting_views.py`:638
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def cash_flow_statement(request):
    period = request.GET.get("period") or timezone.localdate().strftime("%Y-%m")
    start_date, end_date = _month_window(period)
    beginning_balance = Decimal("0")
    ending_balance = Decimal("0")
    cash_accounts = list(Account.objects.filter(is_cash_account=True, allow_posting=True, is_active=True))

    for account in cash_accounts:
        beginning_balance += _account_balance(account, start_date - timedelta(days=1))
        ending_balance += _account_balance(account, end_date)

    sections = {"operating": {}, "investing": {}, "financing": {}}
    entries = JournalEntry.objects.filter(status="posted", date__range=(start_date, end_date)).prefetch_related(
        Prefetch("lines", queryset=JournalEntryLine.objects.select_related("account"))
    )

    for entry in entries:
        lines = list(entry.lines.all())
        cash_lines = [line for line in lines if line.account.is_cash_account]
        if not cash_lines:
            continue
        other_types = {line.account.account_type for line in lines if not line.account.is_cash_account}
        if other_types & {"revenue", "expense"} or other_types & {"asset"} and any(line.account.name.lower().find("piutang") >= 0 for line in lines):
            section = "operating"
        elif other_types & {"asset"}:
            section = "investing"
        else:
            section = "financing"

        for line in cash_lines:
            amount = _account_delta(line.account, line.debit, line.credit)
            sections[section][line.account.name] = sections[section].get(line.account.name, Decimal("0")) + amount

    operating = [{"name": name, "amount": float(amount)} for name, amount in sections["operating"].items()]
    investing = [{"name": name, "amount": float(amount)} for name, amount in sections["investing"].items()]
    financing = [{"name": name, "amount": float(amount)} for name, amount in sections["financing"].items()]

    context = {
        "period": period,
        "beginning_balance": float(beginning_balance),
        "operating_json": json.dumps(operating),
        "investing_json": json.dumps(investing),
        "financing_json": json.dumps(financing),
        "ending_balance": float(ending_balance),
    }
    return render(request, "lumra_pages/accounting/cash_flow.html", context)
```

### accounts_receivable
- File: `lumra_config/views/accounting_views.py`:680
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def accounts_receivable(request):
    today = timezone.localdate()
    entries = AccountsReceivableEntry.objects.select_related("customer").filter(status__in=["open", "partial"]).order_by("due_date")
    rows = []
    total_ar = Decimal("0")
    due_today = Decimal("0")
    overdue = Decimal("0")

    for item in entries:
        balance = item.balance
        age_days = (today - item.due_date).days
        status = "Overdue" if age_days > 0 else "Due Today" if age_days == 0 else "Unpaid"
        rows.append(
            {
                "id": item.id,
                "customer": item.customer.name,
                "number": item.invoice_number,
                "date": item.invoice_date.isoformat(),
                "due_date": item.due_date.isoformat(),
                "total": float(item.total_amount),
                "balance": float(balance),
                "status": status,
                "age_days": age_days,
            }
        )
        total_ar += balance
        if age_days == 0:
            due_today += balance
        if age_days > 30:
            overdue += balance

    context = {
        "invoices_json": json.dumps(rows),
        "total_ar": float(total_ar),
        "due_today": float(due_today),
        "overdue": float(overdue),
        "today": today.isoformat(),
    }
    return render(request, "lumra_pages/accounting/accounts_receivable.html", context)
```

### accounts_payable
- File: `lumra_config/views/accounting_views.py`:736
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def accounts_payable(request):
    today = timezone.localdate()
    payables = AccountsPayableEntry.objects.select_related("vendor").filter(status__in=["open", "partial"]).order_by("vendor__name", "due_date")
    vendor_rows = {}

    for item in payables:
        vendor_data = vendor_rows.setdefault(
            item.vendor_id,
            {
                "id": item.vendor_id,
                "name": item.vendor.name,
                "invoices_count": 0,
                "total": Decimal("0"),
                "aging": {"current": Decimal("0"), "m1_30": Decimal("0"), "m31_60": Decimal("0"), "m60": Decimal("0")},
            },
        )
        balance = item.balance
        vendor_data["invoices_count"] += 1
        vendor_data["total"] += balance

        age = (today - item.due_date).days
        if age <= 30:
            vendor_data["aging"]["current"] += balance
        elif age <= 60:
            vendor_data["aging"]["m1_30"] += balance
        elif age <= 90:
            vendor_data["aging"]["m31_60"] += balance
        else:
            vendor_data["aging"]["m60"] += balance

    suppliers = []
    totals = {"current": Decimal("0"), "m1_30": Decimal("0"), "m31_60": Decimal("0"), "m60": Decimal("0")}
    total_ap = Decimal("0")
    for item in vendor_rows.values():
        total_ap += item["total"]
        for key in totals:
            totals[key] += item["aging"][key]
        suppliers.append(
            {
                "id": item["id"],
                "name": item["name"],
                "invoices_count": item["invoices_count"],
                "total": float(item["total"]),
                "aging": {key: float(value) for key, value in item["aging"].items()},
            }
        )

    context = {
        "suppliers_json": json.dumps(suppliers),
        "total_ap": float(total_ap),
        "aging_json": json.dumps({key: float(value) for key, value in totals.items()}),
    }
    return render(request, "lumra_pages/accounting/accounts_payable.html", context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
