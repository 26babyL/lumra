# lumra_config/views/print_views.py

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from lumra_config.models import (
    Order,
    PaymentVoucher,
    ProductionOrder,
    StockOpnameSession,
    Vendor,
)


def _build_order_lines(order):
    lines = []
    subtotal = Decimal("0")
    for item in order.items.select_related("variant", "variant__product"):
        line_total = Decimal(item.quantity) * item.price
        subtotal += line_total
        lines.append(
            {
                "sku": item.variant.sku,
                "name": item.variant.product.name,
                "description": item.variant.size_weight or item.variant.product.description or "-",
                "unit": getattr(item.variant.product.unit, "symbol", "-") if item.variant.product.unit_id else "-",
                "quantity": item.quantity,
                "unit_price": item.price,
                "total": line_total,
            }
        )
    return lines, subtotal


def _build_order_print_context(order):
    lines, subtotal = _build_order_lines(order)
    return {
        "document_number": f"ORD-{order.id:05d}",
        "document_date": order.created_at,
        "customer_name": order.customer.name if order.customer_id else order.customer_name,
        "customer_address": getattr(order.customer, "address", "") if order.customer_id else "",
        "items": lines,
        "subtotal": subtotal,
        "total": subtotal,
        "notes": "",
        "reference_number": f"INV-{order.id:05d}",
    }


def _build_purchase_order_context(vendor):
    variants = list(vendor.product_set.prefetch_related("variants", "unit").order_by("name")[:6])
    items = []
    subtotal = Decimal("0")
    for index, product in enumerate(variants, start=1):
        variant = product.variants.first()
        if not variant:
            continue
        qty = index * 5
        total = Decimal(qty) * variant.price_buy
        subtotal += total
        items.append(
            {
                "name": product.name,
                "description": product.description or "-",
                "unit": getattr(product.unit, "symbol", "-") if product.unit_id else "-",
                "quantity": qty,
                "unit_price": variant.price_buy,
                "total": total,
            }
        )
    tax_amount = subtotal * Decimal("0.11")
    return {
        "document_number": f"PO-{vendor.id:05d}",
        "document_date": timezone.localdate(),
        "vendor": vendor,
        "items": items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total": subtotal + tax_amount,
        "status": "Sent",
        "delivery_address": vendor.address,
    }


@login_required
@require_http_methods(["GET"])
def print_invoice(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context["object"] = order
    return render(request, "lumra_pages/print/print_invoice.html", context)


@login_required
@require_http_methods(["GET"])
def print_sales_order(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context["object"] = order
    return render(request, "lumra_pages/print/print_sales_order.html", context)


@login_required
@require_http_methods(["GET"])
def print_quotation(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context["object"] = order
    return render(request, "lumra_pages/print/print_quotation.html", context)


@login_required
@require_http_methods(["GET"])
def print_purchase_order(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    context = _build_purchase_order_context(vendor)
    return render(request, "lumra_pages/print/print_purchase_order.html", context)


@login_required
@require_http_methods(["GET"])
def print_delivery_note(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context.update(
        {
            "document_number": f"DN-{order.id:05d}",
            "source_name": "Gudang Pusat",
            "source_address": "Lokasi operasional utama",
        }
    )
    return render(request, "lumra_pages/print/print_delivery_note.html", context)


@login_required
@require_http_methods(["GET"])
def print_packing_slip(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    context.update(
        {
            "document_number": f"PK-{order.id:05d}",
            "package_count": max(1, order.items.count()),
        }
    )
    return render(request, "lumra_pages/print/print_packing_slip.html", context)


@login_required
@require_http_methods(["GET"])
def print_payment_receipt(request, pk):
    voucher = get_object_or_404(PaymentVoucher.objects.select_related("vendor"), pk=pk)
    context = {
        "voucher": voucher,
        "document_number": voucher.number,
    }
    return render(request, "lumra_pages/print/print_payment_receipt.html", context)


@login_required
@require_http_methods(["GET"])
def print_receipt(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    return render(request, "lumra_pages/print/print_receipt.html", context)


@login_required
@require_http_methods(["GET"])
def print_production_order(request, pk):
    production_order = get_object_or_404(
        ProductionOrder.objects.select_related(
            "bom",
            "bom__finished_variant",
            "bom__finished_variant__product",
            "unit",
        ).prefetch_related("bom__items__component__product"),
        pk=pk,
    )
    context = {
        "production_order": production_order,
        "document_number": production_order.code,
        "document_date": production_order.created_at,
        "product_name": production_order.bom.finished_variant.product.name,
        "product_sku": production_order.bom.finished_variant.sku,
        "target_quantity": production_order.target_quantity,
        "produced_quantity": production_order.produced_quantity,
        "unit_name": production_order.unit.symbol if production_order.unit_id else "-",
        "bom_items": production_order.bom.items.all(),
        "notes": production_order.notes,
    }
    return render(request, "lumra_pages/print/print_production_order.html", context)


@login_required
@require_http_methods(["GET"])
def print_credit_note(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__variant__product"), pk=pk)
    context = _build_order_print_context(order)
    return render(request, "lumra_pages/print/print_credit_note.html", context)


@login_required
@require_http_methods(["GET"])
def print_stock_opname(request, pk):
    session = get_object_or_404(
        StockOpnameSession.objects.select_related("location", "created_by").prefetch_related("items__variant__product"),
        pk=pk,
    )
    context = {
        "session": session,
        "document_number": f"SO-{session.id:05d}",
    }
    return render(request, "lumra_pages/print/print_stock_opname.html", context)
