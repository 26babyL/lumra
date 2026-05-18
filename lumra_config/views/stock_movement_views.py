# lumra_config/views/stock_movement_views.py
# Auto-generated oleh lumra_sync.py dari core/views/stock_movement_views.py
# JANGAN EDIT MANUAL — edit core/views/stock_movement_views.py lalu jalankan lumra_sync.py lagi

# Views related to generic inventory stock movement / log

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F, Case, When, IntegerField
from django.utils.dateparse import parse_date
from django.utils import timezone

from lumra_config.models import Stock, ProductVariant, Location
from .helpers import check_queryset_empty, create_empty_context

# =====================================================
# CONSTANTS
# =====================================================

TXN_IN  = "in"
TXN_OUT = "out"
VALID_TXN_TYPES = {TXN_IN, TXN_OUT, "opname", "adjustment"}
PAGE_SIZE = 15


# =====================================================
# STOCK MOVEMENT LIST
# =====================================================

@login_required
# TODO[C3-LONG]: 'stock_movement_view' = 87 baris (max 30). Pecah: stock_movement_view_validate(), stock_movement_view_query(), stock_movement_view_render()
# TODO[C3-LONG]: 'stock_movement_view' terlalu panjang (87 baris). Pecah: stock_movement_view_validate(), stock_movement_view_build_context(), stock_movement_view_render()
# TODO[C3-LONG]: 'stock_movement_view' = 93 baris (maks 30). Pecah: stock_movement_view_validate(), stock_movement_view_process(), stock_movement_view_respond()
def stock_movement_view(request):
    """List stock movement entries with filters for search, type, and date."""

    qs = Stock.objects.select_related(
        "variant__product", "location"
    ).order_by("-created_at")

    # ── Filters ──────────────────────────────────────
    q            = request.GET.get("q", "").strip()
    type_filter  = request.GET.get("type", "").strip()
    start_date   = request.GET.get("start_date", "").strip()
    end_date     = request.GET.get("end_date", "").strip()

    if q:
        qs = qs.filter(
            Q(variant__sku__icontains=q)           |  # FIX: tambah SKU search
            Q(variant__product__name__icontains=q) |
            Q(notes__icontains=q)
        )

    # FIX: whitelist tipe transaksi — cegah filter injection
    if type_filter and type_filter in VALID_TXN_TYPES:
        qs = qs.filter(transaction_type=type_filter)

    # FIX: validasi format tanggal sebelum dipakai ke ORM
    if start_date and parse_date(start_date):
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date and parse_date(end_date):
        qs = qs.filter(created_at__date__lte=end_date)

    # Check if stock movements is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_movement.html",
            create_empty_context("Stock Movement", "Data pergerakan stok tidak ditemukan.")
        )

    # ── Metrics (dihitung dari qs sebelum paginate) ──
    # FIX: gabungkan 3 query count + 1 aggregate → 1 query
    aggregated = qs.aggregate(
        stock_in_qty=Sum(
            Case(When(transaction_type=TXN_IN, then=F("quantity")),
                 default=0, output_field=IntegerField())
        ),
        stock_out_qty=Sum(
            Case(When(transaction_type=TXN_OUT, then=F("quantity")),
                 default=0, output_field=IntegerField())
        ),
        net=Sum(
            Case(
                When(transaction_type=TXN_IN,  then=F("quantity")),
                When(transaction_type=TXN_OUT, then=-F("quantity")),
                default=0,
                output_field=IntegerField(),
            )
        ),
    )
    total_movements  = qs.count()
    stock_in_count   = aggregated["stock_in_qty"]  or 0
    stock_out_count  = aggregated["stock_out_qty"] or 0
    net_change       = aggregated["net"]           or 0

    # ── Pagination ───────────────────────────────────
    paginator  = Paginator(qs, PAGE_SIZE)
    page_obj   = paginator.get_page(request.GET.get("page"))

    # FIX: hapus loop rebuild dict — kirim queryset langsung ke template
    # Template tinggal pakai: movement.variant.product.name, movement.created_at, dst.

    context = {
        "movements":      page_obj,          # langsung queryset, bukan list dict
        "page_obj":       page_obj,
        "is_paginated":   page_obj.has_other_pages(),
        "total_movements": total_movements,
        "stock_in_count":  stock_in_count,
        "stock_out_count": stock_out_count,
        "net_change":      net_change,
        "query":           q,
        "type":            type_filter,
        "start_date":      start_date,
        "end_date":        end_date,
        "valid_txn_types": sorted(VALID_TXN_TYPES),  # untuk dropdown template
        "report_title":    "Stock Movement",
        "is_empty": False,
    }
    return render(request, "lumra_pages/inventory/stock_movement.html", context)


# =====================================================
# EXPORT
# =====================================================

@login_required
def export_stock_movement(request):
    """Stub endpoint for exporting stock movement data.

    The front‑end links here with ``?format=csv`` or ``?format=excel``.
    This view currently performs basic validation and returns a placeholder
    response; replace with real CSV/Excel generation logic as needed.
    """
    fmt = request.GET.get("format", "csv").lower()
    if fmt not in ("csv", "excel"):
        return render(request, "lumra_pages/inventory/stock_movement.html", {
            "error": f"Format ekspor tidak dikenal: {fmt}",
        })

    # TODO: query the same filters as ``stock_movement_view`` and emit a file
    return render(request, "lumra_pages/inventory/stock_movement.html", {
        "info": f"Ekspor '{fmt}' belum diimplementasi."
    })


# =====================================================
# ADD STOCK MOVEMENT
# =====================================================

# TODO[C3-LONG]: 'add_stock_movement_view' = 66 baris (max 30). Pecah: add_stock_movement_view_validate(), add_stock_movement_view_query(), add_stock_movement_view_render()
@login_required
# TODO[C3-LONG]: 'add_stock_movement_view' terlalu panjang (69 baris). Pecah: add_stock_movement_view_validate(), add_stock_movement_view_build_context(), add_stock_movement_view_render()
# TODO[C3-LONG]: 'add_stock_movement_view' = 77 baris (maks 30). Pecah: add_stock_movement_view_validate(), add_stock_movement_view_process(), add_stock_movement_view_respond()
def add_stock_movement_view(request):
    """Form untuk membuat stock entry baru."""

    if request.method == "POST":
        variant_id  = request.POST.get("variant")
        location_id = request.POST.get("location")
        raw_qty     = request.POST.get("quantity", "").strip()
        txn_type    = request.POST.get("transaction_type", "").strip()
        notes       = request.POST.get("notes", "").strip()

        # ── Validasi ─────────────────────────────────
        errors = []

        if not variant_id:
            errors.append("Variant wajib dipilih.")
        if not location_id:
            errors.append("Lokasi wajib dipilih.")
        if not raw_qty or not raw_qty.lstrip("-").isdigit():
            errors.append("Quantity harus berupa angka.")
        elif int(raw_qty) <= 0:
            errors.append("Quantity harus lebih dari 0.")
        if txn_type not in VALID_TXN_TYPES:
            errors.append(f"Tipe transaksi tidak valid: {txn_type!r}")

        if errors:
            for err in errors:
                messages.error(request, err)
    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
            # Kembalikan form dengan input yang sudah diisi (tidak hilang)
            return render(request, "lumra_pages/inventory/add_stock_movement.html", {
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # Gunakan Model.objects.select_related('...').prefetch_related('...')
                # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
                "variants":        ProductVariant.objects.select_related("product").all(),
                "locations":       Location.objects.all(),
                "valid_txn_types": sorted(VALID_TXN_TYPES),
                "prev":            request.POST,   # repopulate form di template
            })

        # ── Simpan ───────────────────────────────────
        try:
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan Model.objects.select_related('...').prefetch_related('...')
            # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
            variant  = ProductVariant.objects.get(id=variant_id)
            # TODO[C5-N1]: Pindahkan query ini ke atas loop.
            # Gunakan Model.objects.select_related('...').prefetch_related('...')
            location = Location.objects.get(id=location_id)
        # TODO[C5-N1]: Pindahkan query ini ke atas loop.
        # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
        except (ProductVariant.DoesNotExist, Location.DoesNotExist):
            messages.error(request, "Variant atau lokasi tidak ditemukan.")
            return redirect("add_stock_movement")

        Stock.objects.create(
            variant=variant,
            location=location,
            quantity=int(raw_qty),
            transaction_type=txn_type,
            notes=notes,
            # FIX: simpan user yang melakukan transaksi jika field tersedia
            # created_by=request.user,
        )

        messages.success(
            request,
            f"Stock movement ({txn_type}) untuk {variant} berhasil disimpan."
        )
        return redirect("stock_movement")

    # ── GET ───────────────────────────────────────────
    context = {
        "variants":        ProductVariant.objects.select_related("product").order_by("sku"),
        "locations":       Location.objects.order_by("name"),
        "valid_txn_types": sorted(VALID_TXN_TYPES),
    }
    return render(request, "lumra_pages/inventory/add_stock_movement.html", context)