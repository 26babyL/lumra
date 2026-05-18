# lumra_config/views/accounting_views.py

import json
from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from lumra_config.models import (
    Account,
    AccountsPayableEntry,
    AccountsReceivableEntry,
    JournalEntry,
    JournalEntryLine,
    PaymentVoucher,
    PaymentVoucherAllocation,
    Vendor,
)


def _decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def _parse_date(value, fallback=None):
    if fallback is None:
        fallback = timezone.localdate()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return fallback


def _month_window(period_value):
    today = timezone.localdate()
    try:
        year, month = [int(part) for part in period_value.split("-")]
        start = date(year, month, 1)
    except (AttributeError, TypeError, ValueError):
        start = today.replace(day=1)
    end = start.replace(day=monthrange(start.year, start.month)[1])
    return start, end


def _generate_number(prefix, model):
    today = timezone.localdate()
    base = f"{prefix}-{today.strftime('%y%m')}"
    last = model.objects.filter(number__startswith=base).order_by("-number").first()
    seq = 1
    if last:
        try:
            seq = int(last.number.split("-")[-1]) + 1
        except (TypeError, ValueError, IndexError):
            seq = model.objects.count() + 1
    return f"{base}-{seq:03d}"


def _account_delta(account, debit, credit):
    if account.account_type in {"asset", "expense"}:
        return debit - credit
    return credit - debit


def _balance_to_columns(account, balance):
    if account.account_type in {"asset", "expense"}:
        return (max(balance, Decimal("0")), max(-balance, Decimal("0")))
    return (max(-balance, Decimal("0")), max(balance, Decimal("0")))


def _account_balance(account, as_of_date):
    lines = JournalEntryLine.objects.filter(
        account=account,
        journal_entry__status="posted",
        journal_entry__date__lte=as_of_date,
    )
    totals = lines.aggregate(debit=Sum("debit"), credit=Sum("credit"))
    debit = totals["debit"] or Decimal("0")
    credit = totals["credit"] or Decimal("0")
    return account.opening_balance + _account_delta(account, debit, credit)


def _serialize_accounts(accounts):
    return [
        {
            "id": account.id,
            "code": account.code,
            "name": account.name,
            "type": account.account_type,
            "level": account.level,
            "parent_id": account.parent_id or "",
            "can_post": account.allow_posting,
        }
        for account in accounts
    ]


def _resolve_ap_account():
    account = Account.objects.filter(account_type="liability", allow_posting=True, name__icontains="utang").first()
    return account or Account.objects.filter(account_type="liability", allow_posting=True).first()


def _serialize_journal(entry):
    return {
        "id": entry.id,
        "number": entry.number,
        "date": entry.date.isoformat(),
        "description": entry.description,
        "reference": entry.reference,
        "status": entry.status,
        "total": float(entry.total_amount),
    }


@login_required
def chart_of_accounts(request):
    accounts = Account.objects.select_related("parent").all()
    context = {
        "accounts": accounts,
        "accounts_json": json.dumps(_serialize_accounts(accounts)),
    }
    return render(request, "lumra_pages/accounting/chart_of_accounts.html", context)


@login_required
@transaction.atomic
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


@login_required
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


@login_required
def journal_entry_list(request):
    # Lazy loading: hanya ambil 1000 data pertama
    page = int(request.GET.get('page', 1))
    per_page = 1000
    
    journals = JournalEntry.objects.prefetch_related("lines").all()
    
    # Pagination
    paginator = Paginator(journals, per_page)
    page_obj = paginator.get_page(page)
    
    # Total count untuk UI
    total_count = journals.count()
    has_more = total_count > (page * per_page)
    
    context = {
        "journals": page_obj,
        "journals_json": json.dumps([_serialize_journal(entry) for entry in page_obj]),
        "total_count": total_count,
        "current_page": page,
        "per_page": per_page,
        "has_more": has_more,
        "is_loading_more": False,
    }
    return render(request, "lumra_pages/accounting/journal_entry_list.html", context)


@login_required
@transaction.atomic
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


@login_required
@transaction.atomic
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


@login_required
@transaction.atomic
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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
