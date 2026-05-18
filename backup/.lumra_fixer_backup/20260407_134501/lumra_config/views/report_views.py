# lumra_config/views/report_views.py
# Auto-generated oleh lumra_sync.py dari core/views/report_views.py
# JANGAN EDIT MANUAL — edit core/views/report_views.py lalu jalankan lumra_sync.py lagi

# Report Views - Tambahan di core/views.py

from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, F, Count, Q
from lumra_config.models import Order, OrderItem, Transfer, TransferItem, Requisition, RequisitionItem, Product, Location
from .helpers import check_queryset_empty, create_empty_context, parse_date_aware
import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# ==================== REPORT VIEWS ====================


@login_required
# TODO[C3-LONG]: 'sales_report' = 85 baris (max 30). Pecah: sales_report_validate(), sales_report_query(), sales_report_render()
# TODO[C3-LONG]: 'sales_report' terlalu panjang (85 baris). Pecah: sales_report_validate(), sales_report_build_context(), sales_report_render()
def sales_report(request):
    """
    Laporan Penjualan Detail
    Menampilkan semua transaksi penjualan per item
    """
    # Get date range from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default: last 30 days
    if not date_from or not date_to:
        date_to = timezone.now()
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    # Query sales detail
    sales = OrderItem.objects.filter(
        order__created_at__range=[date_from, date_to],
        order__status='completed'
    ).select_related('order', 'variant', 'variant__product').order_by('-order__created_at')
    
    # Check if sales is empty
    if not sales.exists():
        context = create_empty_context("Sales Report", "Data penjualan tidak ditemukan untuk periode yang dipilih.")
        # ensure dates are strings for template
        def _fmt(d):
            return d.strftime('%Y-%m-%d') if isinstance(d, datetime) else d
        context.update({
            'date_from': _fmt(date_from),
            'date_to': _fmt(date_to),
        })
        return render(request, 'lumra_pages/reports/sales_report.html', context)
    
    # Calculate totals
    total_qty = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_amount = sales.aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0

    # additional metrics for linking pages
    transfer_count = Transfer.objects.filter(
        created_at__range=[date_from, date_to]
    ).count()
    requisition_count = Requisition.objects.filter(
        created_at__range=[date_from, date_to]
    ).count()
    
    # Pagination
    paginator = Paginator(sales, 50)
    page_number = request.GET.get('page', 1)
    sales_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Date', 'SKU', 'Product', 'Qty', 'Price', 'Total'])
        for item in sales:
            writer.writerow([
                item.order.id,
                item.order.customer_name,
                item.order.created_at.strftime('%Y-%m-%d %H:%M'),
                item.variant.sku,
                item.variant.product.name,
                item.quantity,
                item.price,
                item.quantity * item.price
            ])
        return response
    
    context = {
        'sales': sales_page,
        'total_qty': total_qty,
        'total_amount': total_amount,
        'transfer_count': transfer_count,
        'requisition_count': requisition_count,
        'date_from': date_from.strftime('%Y-%m-%d') if hasattr(date_from, 'strftime') else date_from,
        'date_to': date_to.strftime('%Y-%m-%d') if hasattr(date_to, 'strftime') else date_to,
        'report_title': 'Sales Report',
        'is_empty': False,
    }
    return render(request, 'lumra_pages/reports/sales_report.html', context)


# TODO[C3-LONG]: 'transaction_summary' = 60 baris (max 30). Pecah: transaction_summary_validate(), transaction_summary_query(), transaction_summary_render()
@login_required
# TODO[C3-LONG]: 'transaction_summary' terlalu panjang (64 baris). Pecah: transaction_summary_validate(), transaction_summary_build_context(), transaction_summary_render()
def transaction_summary(request):
    """
    Laporan Transaksi (Summary Header)
    Menampilkan ringkasan per transaksi/order
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    # Query transactions with aggregation
    transactions = Order.objects.filter(
        created_at__range=[date_from, date_to],
        status='completed'
    ).annotate(
        total_items=Count('items'),
        total_qty=Sum('items__quantity'),
        total_amount=Sum(F('items__quantity') * F('items__price'))
    ).order_by('-created_at')
    
    # Summary stats
    total_transactions = transactions.count()
    total_revenue = transactions.aggregate(Sum('items__quantity') * Sum('items__price'))['items__quantity__sum'] or 0
    
    paginator = Paginator(transactions, 50)
    page_number = request.GET.get('page', 1)
    transactions_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transaction_summary.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Date', 'Items', 'Total Qty', 'Total Amount', 'Status'])
        for trans in transactions:
            writer.writerow([
                trans.id,
                trans.customer_name,
                trans.created_at.strftime('%Y-%m-%d %H:%M'),
                trans.total_items,
                trans.total_qty,
                trans.total_amount,
                trans.status
            ])
        return response
    
    context = {
        'transactions': transactions_page,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'report_title': 'Transaction Summary'
    # TODO[C3-LONG]: 'transfer_report' = 54 baris (max 30). Pecah: transfer_report_validate(), transfer_report_query(), transfer_report_render()
    }
    return render(request, 'lumra_pages/reports/transaction_summary.html', context)


@login_required
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C3-LONG]: 'transfer_report' terlalu panjang (55 baris). Pecah: transfer_report_validate(), transfer_report_build_context(), transfer_report_render()
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
def transfer_report(request):
    """
    Laporan Transfer (Stock Movement Detail)
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    transfers = TransferItem.objects.filter(
        transfer__created_at__range=[date_from, date_to]
    ).select_related('transfer', 'variant', 'variant__product', 'transfer__source_location', 'transfer__destination_location').order_by('-transfer__created_at')
    
    total_items = transfers.count()
    total_qty_sent = transfers.aggregate(Sum('quantity_sent'))['quantity_sent__sum'] or 0
    
    paginator = Paginator(transfers, 50)
    page_number = request.GET.get('page', 1)
    transfers_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transfer_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Transfer ID', 'From', 'To', 'Date', 'SKU', 'Product', 'Qty Sent', 'Qty Received', 'Status'])
        for item in transfers:
            writer.writerow([
                item.transfer.id,
                item.transfer.source_location.name,
                item.transfer.destination_location.name,
                item.transfer.created_at.strftime('%Y-%m-%d %H:%M'),
                item.variant.sku,
                item.variant.product.name,
                item.quantity_sent,
                item.quantity_received or '-',
                item.transfer.status
            ])
        return response
     # TODO[C3-LONG]: 'requisition_report' = 60 baris (max 30). Pecah: requisition_report_validate(), requisition_report_query(), requisition_report_render()
    
    context = {
        'transfers': transfers_page,
        'total_items': total_items,
        'total_qty_sent': total_qty_sent,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'report_title': 'Transfer Report'
    }
    # TODO[C3-LONG]: 'requisition_report' terlalu panjang (65 baris). Pecah: requisition_report_validate(), requisition_report_build_context(), requisition_report_render()
    return render(request, 'lumra_pages/reports/transfer_report.html', context)


# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
@login_required
def requisition_report(request):
    """
    Laporan Requisition (Permintaan Barang)
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status_filter = request.GET.get('status')
     # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    requisitions = RequisitionItem.objects.filter(
        requisition__created_at__range=[date_from, date_to]
    ).select_related('requisition', 'variant', 'variant__product', 'requisition__from_location', 'requisition__to_location').order_by('-requisition__created_at')
    
    if status_filter:
        requisitions = requisitions.filter(requisition__status=status_filter)
    
    total_items = requisitions.count()
    total_qty = requisitions.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    paginator = Paginator(requisitions, 50)
    page_number = request.GET.get('page', 1)
    requisitions_page = paginator.get_page(page_number)
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="requisition_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Req ID', 'From', 'To', 'Date', 'SKU', 'Product', 'Qty', 'Status', 'Requested By'])
        for item in requisitions:
            writer.writerow([
                item.requisition.id,
                item.requisition.from_location.name,
                item.requisition.to_location.name,
                item.requisition.created_at.strftime('%Y-%m-%d %H:%M'),
                item.variant.sku,
                item.variant.product.name,
                item.quantity,
                item.requisition.status,
                item.requisition.requested_by.username
            ])
        # TODO[C3-LONG]: 'purchasing_report' = 73 baris (max 30). Pecah: purchasing_report_validate(), purchasing_report_query(), purchasing_report_render()
        return response
    
    context = {
        'requisitions': requisitions_page,
        'total_items': total_items,
        'total_qty': total_qty,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'status_filter': status_filter,
        'status_choices': Requisition.STATUS_CHOICES,
        # TODO[C3-LONG]: 'purchasing_report' terlalu panjang (75 baris). Pecah: purchasing_report_validate(), purchasing_report_build_context(), purchasing_report_render()
        'report_title': 'Requisition Report'
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    }
    return render(request, 'lumra_pages/reports/requisition_report.html', context)


@login_required
def purchasing_report(request):
    """
    Laporan Purchasing (Pembelian dari Vendor)
    """
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    vendor_filter = request.GET.get('vendor')
     # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_to = timezone.now()
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    
    purchasing = RequisitionItem.objects.filter(
        requisition__created_at__range=[date_from, date_to],
        requisition__status__in=['approved', 'completed']
    ).select_related('requisition', 'variant', 'variant__product').order_by('-requisition__created_at')
    
    if vendor_filter:
        purchasing = purchasing.filter(variant__product__vendor_id=vendor_filter)
    
    # Calculate costs
    purchasing = purchasing.annotate(
        total_cost=F('quantity') * F('variant__price_buy')
    )
    
    total_items = purchasing.count()
    total_qty = purchasing.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_cost = purchasing.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    paginator = Paginator(purchasing, 50)
    page_number = request.GET.get('page', 1)
    purchasing_page = paginator.get_page(page_number)
    
    # Get vendor list for filter
    from .models import Vendor
    vendors = Vendor.objects.filter(is_active=True).order_by('name')
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="purchasing_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Req ID', 'Date', 'Vendor', 'SKU', 'Product', 'Qty', 'Price', 'Total Cost', 'Status'])
        for item in purchasing:
            vendor_name = item.variant.product.vendor.name if item.variant.product.vendor else '-'
            writer.writerow([
                item.requisition.id,
                item.requisition.created_at.strftime('%Y-%m-%d %H:%M'),
                vendor_name,
                item.variant.sku,
                item.variant.product.name,
                item.quantity,
                item.variant.price_buy,
                item.quantity * item.variant.price_buy,
                item.requisition.status
            ])
        return response
    
    context = {
        'purchasing': purchasing_page,
        'total_items': total_items,
        'total_qty': total_qty,
        'total_cost': total_cost,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'vendor_filter': vendor_filter,
        'vendors': vendors,
        'report_title': 'Purchasing Report'
    }
    return render(request, 'lumra_pages/reports/purchasing_report.html', context)


# ------------------------------------------------------------------
# NEW REPORT STUBS (templated from sales_report)
# ------------------------------------------------------------------

def _parse_dates(req):
    date_from = req.GET.get('date_from')
    date_to = req.GET.get('date_to')
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not date_from or not date_to:
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        date_to = timezone.now()
        date_from = date_to - timedelta(days=30)
    else:
        date_from = parse_date_aware(date_from, 'start')
        date_to = parse_date_aware(date_to, 'end')
    # return as strings for context as well
    fmt = lambda d: d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else d
    return date_from, date_to, fmt(date_from), fmt(date_to)


@login_required

def report_inventory_log(request):
    """Riwayat keluar masuk barang per SKU."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Inventory Log",
                               "Belum ada data masuk/keluar untuk periode tersebut.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_inventory_log.html', ctx)


@login_required

def report_inventory_low(request):
    """Daftar barang yang harus segera fulfillment."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Low Stock Items",
                               "Tidak ada barang yang perlu dipenuhi saat ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_inventory_low.html', ctx)


@login_required

def report_inventory_stock(request):
    """Posisi stok terakhir dan nilai rupiah aset yang ada di gudang."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Inventory Stock",
                               "Data stok tidak tersedia.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_inventory_stock.html', ctx)


@login_required

def report_profit_loss_detail(request):
    """Detail laba/rugi."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Profit & Loss Detail",
                               "Belum ada data laba/rugi untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_profit_loss_detail.html', ctx)


@login_required

def report_sales_by_outlet(request):
    """Membandingkan performa antar cabang."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales by Outlet",
                               "Tidak ada penjualan per outlet untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_by_outlet.html', ctx)


@login_required

def report_sales_by_payment(request):
    """Detail transaksi via QRIS, Cash, atau Transfer."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales by Payment",
                               "Tidak ada transaksi pembayaran untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_by_payment.html', ctx)


@login_required

def report_sales_by_product(request):
    """Produk mana yang paling laris."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales by Product",
                               "Tidak ada data penjualan produk untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_by_product.html', ctx)


@login_required

def report_sales_summary(request):
    """Ringkasan total penjualan, pajak, dan diskon."""
    date_from, date_to, df_str, dt_str = _parse_dates(request)
    ctx = create_empty_context("Sales Summary",
                               "Tidak ada ringkasan penjualan untuk periode ini.")
    ctx.update({'date_from': df_str, 'date_to': dt_str})
    return render(request, 'lumra_pages/reports/report_sales_summary.html', ctx)
