# lumra_config/views/sales_views.py

import json
from decimal import Decimal
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.db.models import F, Sum
from django.views.decorators.http import require_POST
from django.utils import timezone

from .helpers import check_queryset_empty, create_empty_context
from lumra_config.models import (
    Category,
    Customer,
    Order,
    Payments,
    ProductVariant,
    Returns,
    AccountsReceivableEntry,
)


def _money(value):
    return float(value or 0)


def _order_total_expr():
    return Sum(F("items__quantity") * F("items__price"))


def _serialize_order(order, prefix="SO", status=None):
    created = timezone.localtime(order.created_at)
    total = getattr(order, "total_amount", None)
    if total is None:
        total = getattr(order, "total_price", 0)
    return {
        "id": f"{prefix}-{order.id:05d}",
        "pk": order.id,
        "date": created.strftime("%Y-%m-%d"),
        "customer": order.customer.name if order.customer else order.customer_name,
        "dining_option": order.get_dining_option_display() if order.dining_option else "-",
        "total": _money(total),
        "payment_status": order.payment_status,
        "status": status or order.status,
    }


def _orders_queryset(order_types=None):
    qs = Order.objects.select_related("customer")
    if order_types:
        qs = qs.filter(order_type__in=order_types)
    return (
        qs
        .annotate(total_amount=_order_total_expr())
        .order_by("-created_at")
    )


def _sales_reference_context(order_type, json_key, prefix, status=None):
    rows = [_serialize_order(order, prefix=prefix, status=status) for order in _orders_queryset(order_type)]
    return {json_key: json.dumps(rows, cls=DjangoJSONEncoder)}


# ===== POS (Point of Sale) =====

@login_required
def pos_view(request):
    """Point of Sale interface - main POS page with cart and products."""
    variants = (
        ProductVariant.objects.select_related("product", "product__category")
        .filter(product__is_active=True)
        .order_by("product__name", "sku")
    )
    products = [
        {
            "id": variant.id,
            "sku": variant.sku,
            "name": variant.product.name,
            "category": variant.product.category.name if variant.product.category else "",
            "price": _money(variant.price_sell),
            "stock": _money(variant.total_stock),
        }
        for variant in variants
    ]
    categories = list(Category.objects.filter(is_active=True).order_by("name").values("id", "name"))
    customers = list(
        Customer.objects.filter(is_active=True)
        .order_by("name")
        .values("id", "name", "email", "phone", "tier", "loyalty_points")
    )
    payment_methods_json = json.dumps([
        {'code': code, 'name': label}
        for code, label in Order.PAYMENT_METHOD_CHOICES
    ], cls=DjangoJSONEncoder)

    context = {
        'products_json': json.dumps(products, cls=DjangoJSONEncoder),
        'categories_json': json.dumps(categories, cls=DjangoJSONEncoder),
        'customers_json': json.dumps(customers, cls=DjangoJSONEncoder),
        'discounts_json': json.dumps([], cls=DjangoJSONEncoder),
        'payment_methods_json': payment_methods_json,
    }
    return render(request, 'lumra_pages/sales_insight/pos.html', context)


@login_required
@require_POST
def pos_create_order(request):
    """Create a new POS order (legacy endpoint, may be deprecated)."""
    return JsonResponse({'status': 'ok', 'message': 'Use pos_process instead'})


@login_required
@require_POST
def pos_process_transaction(request):
    """Process POS transaction - handles cart checkout and payment.
    
    Expected POST payload (JSON):
    {
        'customer_id': int or null,
        'items': [{'product_id': int, 'qty': int, 'price': float}, ...],
        'discount_id': int or null,
        'redeem_points': bool,
        'payment_method': 'cash|card|transfer',
        'amount_paid': float
    }
    """
    import json
    from datetime import datetime
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    # Extract payload
    customer_id = data.get('customer_id')
    items = data.get('items', [])
    discount_id = data.get('discount_id')
    redeem_points = data.get('redeem_points', False)
    payment_method = data.get('payment_method', 'cash')
    amount_paid = float(data.get('amount_paid', 0))
    
    # Validation
    if not items:
        return JsonResponse({'success': False, 'error': 'Keranjang kosong'}, status=400)
    
    # Generate transaction number
    now = datetime.now()
    transaction_no = now.strftime('%y%m%d%H%M%S')
    
    # TODO: In production, this should:
    # 1. Create SalesOrder record
    # 2. Create SalesOrderItem records
    # 3. Deduct inventory stock
    # 4. Apply discount if any
    # 5. Redeem loyalty points if enabled
    # 6. Record payment
    # 7. Update ledger entries for accounting
    
    # For now, return success with transaction number
    response = {
        'success': True,
        'transaction_no': transaction_no,
        'customer_id': customer_id,
        'items_count': len(items),
        'payment_method': payment_method,
        'amount_paid': amount_paid,
        'message': 'Transaksi berhasil diproses'
    }
    
    return JsonResponse(response)


# ===== SALES ORDER & QUOTATION =====

@login_required
def sales_order_list(request):
    """List all Sales Orders."""
    rows = [_serialize_order(order, prefix="SO") for order in _orders_queryset(["sales_order", "pos", "completed"])]
    context = {"orders_json": json.dumps(rows, cls=DjangoJSONEncoder)}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/sales_order_list.html', context)


@login_required
def sales_order_form(request, pk=None):
    """Create/Edit Sales Order."""
    context = {
        "order": get_object_or_404(Order, pk=pk, order_type="sales_order") if pk else None,
        "customers": Customer.objects.filter(is_active=True).order_by("name"),
        "variants": ProductVariant.objects.select_related("product").order_by("product__name", "sku"),
    }
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/sales_order_form.html', context)


@login_required
def sales_order_detail(request, pk):
    """View Sales Order detail."""
    order = get_object_or_404(
        Order.objects.select_related("customer").prefetch_related("items__variant__product"),
        pk=pk,
        order_type="sales_order",
    )
    context = {"order": order, "items": order.items.all()}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/sales_order_detail.html', context)


@login_required
def quotation_list(request):
    """List all Quotations."""
    quotes = []
    today = timezone.localdate()
    for order in _orders_queryset(["draft"]):
        created = timezone.localtime(order.created_at).date()
        valid_until = created + timedelta(days=7)
        item = _serialize_order(order, prefix="QT", status="draft")
        item["valid_until"] = valid_until.strftime("%Y-%m-%d")
        item["isExpired"] = valid_until < today
        quotes.append(item)
    context = {"quotations_json": json.dumps(quotes, cls=DjangoJSONEncoder)}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/quotation_list.html', context)


@login_required
def quotation_form(request, pk=None):
    """Create/Edit Quotation."""
    context = {
        "order": get_object_or_404(Order, pk=pk, order_type="draft") if pk else None,
        "customers": Customer.objects.filter(is_active=True).order_by("name"),
        "variants": ProductVariant.objects.select_related("product").order_by("product__name", "sku"),
    }
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/quotation_form.html', context)


@login_required
def quotation_detail(request, pk):
    """View Quotation detail."""
    order = get_object_or_404(
        Order.objects.select_related("customer").prefetch_related("items__variant__product"),
        pk=pk,
        order_type="draft",
    )
    context = {"order": order, "items": order.items.all()}
    return render(request, 'lumra_pages/sales/salesorder_and_quotation/quotation_detail.html', context)


# ===== INVOICE & BILLING =====

@login_required
def invoice_list(request):
    """List all Invoices."""
    invoices = []
    ar_entries = AccountsReceivableEntry.objects.select_related("customer").order_by("-invoice_date", "-id")[:1000]
    for entry in ar_entries:
        invoices.append({
            "id": entry.invoice_number,
            "pk": entry.id,
            "date": entry.invoice_date.strftime("%Y-%m-%d"),
            "customer": entry.customer.name,
            "due_date": entry.due_date.strftime("%Y-%m-%d"),
            "total": _money(entry.total_amount),
            "status": "paid" if entry.status == "paid" else ("partial" if entry.status == "partial" else "unpaid"),
        })
    context = {"invoices_json": json.dumps(invoices, cls=DjangoJSONEncoder)}
    return render(request, 'lumra_pages/sales/invoice_and_billing/invoice_list.html', context)


@login_required
def invoice_form(request, pk=None):
    """Create/Edit Invoice."""
    context = {
        "order": get_object_or_404(Order, pk=pk, order_type="invoiced") if pk else None,
        "customers": Customer.objects.filter(is_active=True).order_by("name"),
        "variants": ProductVariant.objects.select_related("product").order_by("product__name", "sku"),
    }
    return render(request, 'lumra_pages/sales/invoice_and_billing/invoice_form.html', context)


@login_required
def invoice_detail(request, pk):
    """View Invoice detail."""
    order = get_object_or_404(
        Order.objects.select_related("customer").prefetch_related("items__variant__product"),
        pk=pk,
        order_type="invoiced",
    )
    context = {"order": order, "items": order.items.all()}
    return render(request, 'lumra_pages/sales/invoice_and_billing/invoice_detail.html', context)


@login_required
def payment_list(request):
    """List all Payments."""
    payment_rows = []
    payments = Payments.objects.select_related("order", "order__customer").order_by("-payment_date", "-created_at")
    for payment in payments:
        order = payment.order
        method = "transfer" if payment.payment_method == "bank_transfer" else payment.payment_method
        status = "verified" if payment.status == "approved" else payment.status
        payment_rows.append(
            {
                "id": payment.payment_number or f"PAY-{payment.id:05d}",
                "pk": payment.id,
                "invoice": f"INV-{order.id:05d}",
                "customer": order.customer.name if order.customer else order.customer_name,
                "method": method,
                "amount": _money(payment.amount),
                "date": payment.payment_date.strftime("%Y-%m-%d"),
                "status": status,
            }
        )
    context = {"payments_json": json.dumps(payment_rows, cls=DjangoJSONEncoder)}
    return render(request, 'lumra_pages/sales/invoice_and_billing/payment_list.html', context)


@login_required
def payment_form(request, pk=None):
    """Create/Edit Payment."""
    context = {
        "payment": get_object_or_404(Payments, pk=pk) if pk else None,
        "orders": Order.objects.select_related("customer").exclude(payment_status="paid").order_by("-created_at"),
        "payment_methods": Payments.PAYMENT_METHODS,
    }
    return render(request, 'lumra_pages/sales/invoice_and_billing/payment_form.html', context)


# ===== RETURN & REFUND =====

@login_required
def retur_list(request):
    """List all Returns/Refunds."""
    return_rows = []
    returns = Returns.objects.select_related("customer", "order").order_by("-retur_date", "-created_at")
    for item in returns:
        return_rows.append(
            {
                "id": item.retur_number or f"RTN-{item.id:05d}",
                "pk": item.id,
                "date": item.retur_date.strftime("%Y-%m-%d"),
                "customer": item.customer.name,
                "reason": item.reason,
                "amount": _money(item.total_amount),
                "status": item.status,
            }
        )
    context = {"returns_json": json.dumps(return_rows, cls=DjangoJSONEncoder)}
    return render(request, 'lumra_pages/sales/retur_and_refund/retur_list.html', context)


@login_required
def retur_form(request, pk=None):
    """Create/Edit Return/Refund."""
    context = {
        "return": get_object_or_404(Returns, pk=pk) if pk else None,
        "orders": Order.objects.select_related("customer").order_by("-created_at"),
    }
    return render(request, 'lumra_pages/sales/retur_and_refund/retur_form.html', context)


@login_required
def retur_detail(request, pk):
    """View Return/Refund detail."""
    retur = get_object_or_404(Returns.objects.select_related("customer", "order").prefetch_related("items__product__product"), pk=pk)
    context = {"return": retur, "items": retur.items.all()}
    return render(request, 'lumra_pages/sales/retur_and_refund/retur_detail.html', context)
