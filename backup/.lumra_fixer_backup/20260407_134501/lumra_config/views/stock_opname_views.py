# lumra_config/views/stock_opname_views.py
# Auto-generated oleh lumra_sync.py dari core/views/stock_opname_views.py
# JANGAN EDIT MANUAL — edit core/views/stock_opname_views.py lalu jalankan lumra_sync.py lagi

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Prefetch, OuterRef, Subquery
from django.contrib import messages
import csv
import io

from lumra_config.models import (
    Location,
    ProductVariant,
    Stock,
    StockOpnameSession,
    StockOpnameItem,
)
from lumra_config.forms import StockOpnameCSVImportForm
from .helpers import check_queryset_empty, create_empty_context

# =====================================================
# CONSTANTS
# =====================================================

STATUS_IN_PROGRESS = "in_progress"
STATUS_SUBMITTED   = "submitted"
STATUS_APPROVED    = "approved"
STATUS_REJECTED    = "rejected"


def is_manager(user):
    """Permission check: hanya manager/admin yang bisa approve."""
    return user.is_staff or user.groups.filter(name="Manager").exists()


# =====================================================
# STOCK OPNAME STEP 1 — SELECT LOCATION
# =====================================================

@login_required
def stock_opname_locations(request):
    """Step 1: User memilih lokasi untuk opname."""

    locations = Location.objects.all().order_by("name")

    # Check if locations is empty
    if not locations.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_opname_locations.html",
            create_empty_context("Stock Opname", "Data lokasi tidak ditemukan. Silahkan tambah lokasi terlebih dahulu.")
        )

    context = {
        "locations": locations,
        "report_title": "Select Location for Stock Opname",
        "is_empty": False,
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_locations.html",
        context,
    )


# =====================================================
# STOCK OPNAME STEP 2 — INPUT FORM + CSV IMPORT
# =====================================================

@login_required
# TODO[C3-LONG]: 'stock_opname_form' = 173 baris (max 30). Pecah: stock_opname_form_validate(), stock_opname_form_query(), stock_opname_form_render()
# TODO[C3-LONG]: 'stock_opname_form' terlalu panjang (176 baris). Pecah: stock_opname_form_validate(), stock_opname_form_build_context(), stock_opname_form_render()
def stock_opname_form(request, location_id):
    """Step 2: Input opname manual atau import CSV."""

    location = get_object_or_404(Location, pk=location_id)

    # FIX: Gunakan select_for_update-safe pattern — cari dulu, baru create
    session = (
        StockOpnameSession.objects
        .filter(location=location, created_by=request.user, status=STATUS_IN_PROGRESS)
        .first()
    )
    if not session:
        session = StockOpnameSession.objects.create(
            location=location,
            created_by=request.user,
            status=STATUS_IN_PROGRESS,
        )

    # ============================
    # HANDLE CSV IMPORT
    # ============================
    if request.method == "POST" and "import_csv" in request.POST:

        form = StockOpnameCSVImportForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            stream = io.TextIOWrapper(csv_file.file, encoding="utf-8")
            reader = csv.DictReader(stream)

            # Pre-fetch semua SKU yang relevan sekali query
            sku_list = []
            rows = list(reader)
            for row in rows:
                sku = row.get("sku", "").strip()
                if sku:
                    sku_list.append(sku)

            variants_by_sku = {
                v.sku: v
                for v in ProductVariant.objects.filter(sku__in=sku_list)
            }

            # Pre-fetch current stocks sekali query
            stocks_by_variant_id = {
                s["variant_id"]: s["total"]
                for s in Stock.objects.filter(
                    variant__sku__in=sku_list,
                    location=location,
                ).values("variant_id").annotate(total=Sum("quantity"))
            }

            opname_items_to_upsert = []
            for row in rows:
                sku        = row.get("sku", "").strip()
                notes      = row.get("notes", "").strip()

                # FIX: Safe int conversion
                try:
                    counted_qty = int(row.get("counted_qty", 0))
                except (ValueError, TypeError):
                    counted_qty = 0

                variant = variants_by_sku.get(sku)
                if not variant:
                    continue

                current_stock = stocks_by_variant_id.get(variant.id, 0)

                StockOpnameItem.objects.update_or_create(
                    session=session,
                    variant=variant,
                    defaults={
                        "current_stock": current_stock,
                        "counted_qty": counted_qty,
                        "notes": notes,
                    },
                )

            messages.success(request, "CSV berhasil diimport.")
        else:
            messages.error(request, "File CSV tidak valid.")

        return redirect("stock_opname_form", location_id=location.id)

    # ============================
    # HANDLE SUBMIT OPNAME
    # ============================
    if request.method == "POST" and "submit_opname" in request.POST:

        for key, value in request.POST.items():
            if key.startswith("counted_qty_"):
                item_id = key.replace("counted_qty_", "")

    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.
                # TODO[C5-N1]: Pindahkan query ini ke atas loop.
                # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')
                try:
                    record_item = StockOpnameItem.objects.get(id=item_id, session=session)
                    item.counted_qty = int(value) if value else 0
                    item.notes = request.POST.get(f"notes_{item_id}", "")
                    item.save()
                except (StockOpnameItem.DoesNotExist, ValueError):
                    continue

        session.status = STATUS_SUBMITTED
        session.submitted_at = timezone.now()
        session.save()

        messages.success(request, "Opname berhasil disubmit, menunggu approval.")
        return redirect("stock_opname_approvals")

    # ============================
    # GET — build products_data dengan efisien (FIX N+1)
    # ============================

    q = request.GET.get("q", "").strip()

    # Filter variants sebelum pagination
    variants_qs = (
        ProductVariant.objects
        .select_related("product")
        .order_by("sku")
    )
    if q:
        variants_qs = variants_qs.filter(
            models_Q(sku__icontains=q) | models_Q(product__name__icontains=q)
        )

    # Ambil semua stock & opname items dalam 2 query, bukan N query
    all_variant_ids = list(variants_qs.values_list("id", flat=True))

    stock_map = {
        s["variant_id"]: s["total"]
        for s in Stock.objects.filter(
            variant_id__in=all_variant_ids,
            location=location,
        ).values("variant_id").annotate(total=Sum("quantity"))
    }

    item_map = {
        i.variant_id: i
        for i in StockOpnameItem.objects.filter(
            session=session,
            variant_id__in=all_variant_ids,
        )
    }

    products_data = [
        {
            "variant": var,
            "current_stock": stock_map.get(var.id, 0),
            "item": item_map.get(var.id),
        }
        for var in variants_qs
    ]

    # Pagination (search sudah diterapkan sebelum ini — FIX bug lama)
    paginator = Paginator(products_data, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "selected_location": location,
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "query": q,
        "form": StockOpnameCSVImportForm(),
        "report_title": f"Stock Opname - {location.name}",
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_form.html",
        context,
    )


# Alias Q untuk menghindari konflik nama
from django.db.models import Q as models_Q


# =====================================================
# STOCK OPNAME STEP 3 — APPROVAL LIST
# =====================================================

@login_required
# TODO[C3-LONG]: 'stock_opname_approvals' terlalu panjang (31 baris). Pecah: stock_opname_approvals_validate(), stock_opname_approvals_build_context(), stock_opname_approvals_render()
def stock_opname_approvals(request):
    """Step 3: Manager/Admin melihat session opname pending."""

    status_filter = request.GET.get("status", "pending")

    if status_filter == "pending":
        sessions = StockOpnameSession.objects.filter(
            status__in=[STATUS_SUBMITTED, STATUS_IN_PROGRESS]
        )
    else:
        sessions = StockOpnameSession.objects.filter(status=status_filter)

    sessions = sessions.select_related("location", "created_by").order_by("-created_at")

    paginator = Paginator(sessions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "approvals": page_obj.object_list,
        "page_obj": page_obj,
        "status": status_filter,
        "report_title": "Stock Opname Approvals",
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_approvals.html",
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        context,
    )


# =====================================================
# STOCK OPNAME STEP 4 — APPROVAL DETAIL
# =====================================================

# TODO[C3-LONG]: 'stock_opname_approval_detail' = 64 baris (max 30). Pecah: stock_opname_approval_detail_validate(), stock_opname_approval_detail_query(), stock_opname_approval_detail_render()
@login_required
# TODO[C3-LONG]: 'stock_opname_approval_detail' terlalu panjang (64 baris). Pecah: stock_opname_approval_detail_validate(), stock_opname_approval_detail_build_context(), stock_opname_approval_detail_render()
@user_passes_test(is_manager, login_url="/unauthorized/")  # FIX: permission guard
def stock_opname_approval_detail(request, session_id):
    """Step 4: Approve / Reject opname session."""

    session = get_object_or_404(StockOpnameSession, pk=session_id)
    opname_items = session.items.select_related("variant", "variant__product")

    if request.method == "POST":
        decision = request.POST.get("decision")

        # ============================
        # APPROVE
        # ============================
        if decision == "approve":
            with transaction.atomic():
 # TODO[C5-N1]: Pindahkan query ini ke atas loop.
 # Gunakan queryset = Model.objects.select_related('...').prefetch_related('...')

                for item in opname_items:
                    # FIX: Hapus semua stock lama, replace dengan satu entry bersih
                    Stock.objects.filter(
                        variant=item.variant,
                        location=session.location,
                    ).delete()

                    Stock.objects.create(
                        variant=item.variant,
                        location=session.location,
                        quantity=item.counted_qty,
                        transaction_type="opname",
                        notes=f"Approved Opname Session #{session.id}",
                        last_updated=timezone.now(),
                    )

                session.status = STATUS_APPROVED
                session.approved_at = timezone.now()
                session.approved_by = request.user
                session.save()

            messages.success(request, f"Session #{session.id} berhasil di-approve.")
            return redirect("stock_opname_approvals")

        # ============================
        # REJECT
        # ============================
        elif decision == "reject":
            reason = request.POST.get("reason", "").strip()
            if not reason:
                messages.error(request, "Alasan penolakan wajib diisi.")
            else:
                session.status = STATUS_REJECTED
                session.notes = reason
                session.save()
                messages.warning(request, f"Session #{session.id} ditolak.")
                return redirect("stock_opname_approvals")

    context = {
        "session": session,
        "opname_data": opname_items,
        "report_title": f"Approval Detail - {session.location.name}",
    }

    return render(
        request,
        "lumra_pages/inventory/stock_opname_approval_detail.html",
        context,
    )