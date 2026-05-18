import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods

from lumra_config.models import (
    InventoryBatch,
    Location,
    ProductVariant,
    Requisition,
    RequisitionItem,
    StockAdjustmentReason,
    SupplierPrice,
    Vendor,
    WarehouseZone,
)
from .helpers import create_empty_context


def _parse_json_body(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, JsonResponse({"success": False, "error": "Invalid JSON body."}, status=400)

def _parse_iso_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


# ------------------------------------------------------------------
# BATCH (Lot Tracking)
# ------------------------------------------------------------------

@login_required
def batch_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()  # fresh|warning|expired

    batches = InventoryBatch.objects.select_related("variant", "variant__product", "location").all()
    if query:
        batches = batches.filter(
            Q(code__icontains=query)
            | Q(variant__sku__icontains=query)
            | Q(variant__product__name__icontains=query)
        )

    today = date.today()
    warning_threshold = today + timedelta(days=30)

    def _status_for(expiry_date):
        if not expiry_date:
            return "fresh"
        if expiry_date < today:
            return "expired"
        if expiry_date <= warning_threshold:
            return "warning"
        return "fresh"

    batch_rows = []
    for b in batches.order_by("-created_at")[:500]:
        batch_rows.append({
            "id": b.id,
            "code": b.code,
            "product": b.variant.product.name if b.variant and b.variant.product else b.variant.sku,
            "sku": b.variant.sku,
            "qty": b.quantity_on_hand,
            "prod_date": b.production_date.isoformat() if b.production_date else "",
            "exp_date": b.expiry_date.isoformat() if b.expiry_date else "",
            "status": _status_for(b.expiry_date),
            "location": b.location.name,
        })

    if status_filter in {"fresh", "warning", "expired"}:
        batch_rows = [r for r in batch_rows if r["status"] == status_filter]

    context = {"batches_data": batch_rows, "report_title": "Batch & Lot Tracking"}
    return render(request, "lumra_pages/inventory/batch_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def batch_form(request, pk=None):
    batch = get_object_or_404(InventoryBatch, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["variant_id", "location_id", "code", "quantity_on_hand"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        variant = get_object_or_404(ProductVariant, pk=payload["variant_id"])
        location = get_object_or_404(Location, pk=payload["location_id"])
        zone = None
        if payload.get("zone_id"):
            zone = get_object_or_404(WarehouseZone, pk=payload["zone_id"])

        if batch:
            obj = batch
        else:
            obj = InventoryBatch(created_by=request.user)

        obj.variant = variant
        obj.location = location
        obj.zone = zone
        obj.code = str(payload["code"]).strip()
        obj.quantity_on_hand = int(payload["quantity_on_hand"] or 0)
        obj.production_date = _parse_iso_date(payload.get("production_date"))
        obj.expiry_date = _parse_iso_date(payload.get("expiry_date"))
        obj.notes = payload.get("notes", "").strip()
        obj.save()

        return JsonResponse({"success": True, "id": obj.id})

    variants = ProductVariant.objects.select_related("product").order_by("sku")[:1000]
    locations = Location.objects.order_by("name")
    zones = WarehouseZone.objects.select_related("location").filter(is_active=True).order_by("location__name", "code")

    context = {
        "is_edit": bool(batch),
        "batch_id": batch.id if batch else None,
        "variants_data": [
            {"id": v.id, "sku": v.sku, "product": v.product.name if v.product else v.sku}
            for v in variants
        ],
        "locations_data": [{"id": l.id, "name": l.name} for l in locations],
        "zones_data": [
            {"id": z.id, "location_id": z.location_id, "code": z.code, "name": z.name}
            for z in zones
        ],
        "submit_url": request.path,
        "list_url": "/inventory/batch/",
        "report_title": "Input Batch",
    }
    return render(request, "lumra_pages/inventory/batch_form.html", context)


@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(
        InventoryBatch.objects.select_related("variant", "variant__product", "location", "zone"),
        pk=pk,
    )
    data = {
        "id": batch.id,
        "code": batch.code,
        "sku": batch.variant.sku,
        "product": batch.variant.product.name if batch.variant.product else batch.variant.sku,
        "qty": batch.quantity_on_hand,
        "location": batch.location.name,
        "zone": batch.zone.code if batch.zone else "",
        "production_date": batch.production_date.isoformat() if batch.production_date else "",
        "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else "",
        "created_at": localtime(batch.created_at).strftime("%Y-%m-%d %H:%M"),
        "notes": batch.notes,
    }
    context = {"batch_data": data, "report_title": f"Batch Detail - {batch.code}"}
    return render(request, "lumra_pages/inventory/batch_detail.html", context)


@login_required
def expiry_tracking(request):
    today = date.today()
    horizon = today + timedelta(days=90)

    batches = (
        InventoryBatch.objects
        .select_related("variant", "variant__product", "location")
        .filter(expiry_date__isnull=False, expiry_date__lte=horizon)
        .order_by("expiry_date")
    )
    rows = [{
        "id": b.id,
        "code": b.code,
        "sku": b.variant.sku,
        "product": b.variant.product.name if b.variant.product else b.variant.sku,
        "location": b.location.name,
        "qty": b.quantity_on_hand,
        "expiry_date": b.expiry_date.isoformat() if b.expiry_date else "",
    } for b in batches[:1000]]

    context = {"batches_data": rows, "report_title": "Expiry Tracking"}
    return render(request, "lumra_pages/inventory/expiry_tracking.html", context)


# ------------------------------------------------------------------
# REQUISITION (UI)
# ------------------------------------------------------------------

@login_required
def requisition_list(request):
    query = request.GET.get("q", "").strip()

    qs = (
        Requisition.objects
        .select_related("from_location", "to_location", "requested_by", "approved_by")
        .order_by("-created_at")
    )
    if query:
        qs = qs.filter(
            Q(id__icontains=query)
            | Q(from_location__name__icontains=query)
            | Q(to_location__name__icontains=query)
        )

    rows = []
    for r in qs[:500]:
        rows.append({
            "pk": r.pk,
            "code": f"REQ-{r.pk:06d}",
            "from": r.from_location.name,
            "to": r.to_location.name,
            "status": r.status,
            "date": localtime(r.created_at).strftime("%Y-%m-%d"),
        })

    context = {"requisitions_data": rows, "report_title": "Requisitions"}
    return render(request, "lumra_pages/inventory/requisition_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def requisition_form(request, pk=None):
    requisition = get_object_or_404(Requisition, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["from_location_id", "to_location_id", "items"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        from_location = get_object_or_404(Location, pk=payload["from_location_id"])
        to_location = get_object_or_404(Location, pk=payload["to_location_id"])
        items = payload["items"]
        if not isinstance(items, list) or len(items) == 0:
            return JsonResponse({"success": False, "error": "Items must be a non-empty list."}, status=400)

        with transaction.atomic():
            if requisition:
                req_obj = requisition
                req_obj.from_location = from_location
                req_obj.to_location = to_location
            else:
                req_obj = Requisition.objects.create(
                    from_location=from_location,
                    to_location=to_location,
                    requested_by=request.user,
                    status="waiting",
                )

            req_obj.save()

            if requisition:
                req_obj.items.all().delete()

            item_objs = []
            for it in items:
                variant_id = it.get("variant_id")
                qty = it.get("quantity")
                if not variant_id or not qty:
                    continue
                variant = get_object_or_404(ProductVariant, pk=variant_id)
                item_objs.append(RequisitionItem(
                    requisition=req_obj,
                    variant=variant,
                    quantity=int(qty),
                ))

            if not item_objs:
                return JsonResponse({"success": False, "error": "No valid items provided."}, status=400)

            RequisitionItem.objects.bulk_create(item_objs)

        return JsonResponse({"success": True, "pk": req_obj.pk})

    locations = Location.objects.order_by("name")
    variants = ProductVariant.objects.select_related("product").order_by("sku")[:2000]

    context = {
        "is_edit": bool(requisition),
        "requisition_pk": requisition.pk if requisition else None,
        "locations_data": [{"id": l.id, "name": l.name} for l in locations],
        "variants_data": [
            {"id": v.id, "sku": v.sku, "name": v.product.name if v.product else v.sku}
            for v in variants
        ],
        "submit_url": request.path,
        "list_url": "/inventory/requisitions/",
        "report_title": "Requisition Form",
    }
    return render(request, "lumra_pages/inventory/requisition_form.html", context)


@login_required
def requisition_detail(request, pk):
    r = get_object_or_404(
        Requisition.objects
        .select_related("from_location", "to_location", "requested_by", "approved_by")
        .prefetch_related("items__variant", "items__variant__product"),
        pk=pk,
    )
    items = []
    for it in r.items.all():
        items.append({
            "sku": it.variant.sku,
            "name": it.variant.product.name if it.variant.product else it.variant.sku,
            "qty": it.quantity,
        })
    data = {
        "pk": r.pk,
        "code": f"REQ-{r.pk:06d}",
        "status": r.status,
        "from": r.from_location.name,
        "to": r.to_location.name,
        "created_at": localtime(r.created_at).strftime("%Y-%m-%d %H:%M"),
        "notes": "",
        "items": items,
    }
    context = {"requisition_data": data, "report_title": f"Requisition Detail - {data['code']}"}
    return render(request, "lumra_pages/inventory/requisition_detail.html", context)


# ------------------------------------------------------------------
# WAREHOUSE ZONES
# ------------------------------------------------------------------

@login_required
def warehouse_zones(request):
    # Lazy loading: hanya ambil 1000 data pertama
    page = int(request.GET.get('page', 1))
    per_page = 1000
    
    zones = WarehouseZone.objects.select_related("location").order_by("location__name", "code")
    
    # Pagination
    paginator = Paginator(zones, per_page)
    page_obj = paginator.get_page(page)
    
    # Total count untuk UI
    total_count = zones.count()
    has_more = total_count > (page * per_page)
    
    # Prepare data for template
    rows = [{
        "id": z.id,
        "location": z.location.name,
        "location_id": z.location_id,
        "code": z.code,
        "name": z.name,
        "zone_type": z.zone_type,
        "capacity": z.capacity,
        "occupied": z.occupied if hasattr(z, 'occupied') else 0,
        "available": z.available if hasattr(z, 'available') else (z.capacity - (z.occupied if hasattr(z, 'occupied') else 0)),
        "utilization": round((z.occupied if hasattr(z, 'occupied') else 0) / z.capacity * 100, 1) if z.capacity > 0 else 0,
        "utilization_color": "success" if (z.occupied if hasattr(z, 'occupied') else 0) / z.capacity < 0.5 else "warning" if (z.occupied if hasattr(z, 'occupied') else 0) / z.capacity < 0.8 else "error",
        "temperature": z.temperature if hasattr(z, 'temperature') else None,
        "is_active": z.is_active,
    } for z in page_obj]
    
    context = {
        "zones": page_obj,
        "zones_json": json.dumps(rows),
        "total_count": total_count,
        "current_page": page,
        "per_page": per_page,
        "has_more": has_more,
        "is_loading_more": False,
    }
    return render(request, "lumra_pages/warehouse/warehouse_zones.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def warehouse_zone_form(request, pk=None):
    zone = get_object_or_404(WarehouseZone, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["location_id", "code", "name", "zone_type", "capacity"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        location = get_object_or_404(Location, pk=payload["location_id"])
        obj = zone or WarehouseZone()
        obj.location = location
        obj.code = str(payload["code"]).strip()
        obj.name = str(payload["name"]).strip()
        obj.zone_type = str(payload["zone_type"]).strip() or "rack"
        obj.capacity = int(payload["capacity"] or 0)
        obj.is_active = bool(payload.get("is_active", True))
        obj.notes = str(payload.get("notes", "")).strip()
        obj.save()
        return JsonResponse({"success": True, "id": obj.id})

    locations = Location.objects.order_by("name")
    context = {
        "is_edit": bool(zone),
        "zone_id": zone.id if zone else None,
        "locations_data": [{"id": l.id, "name": l.name} for l in locations],
        "zone_types_data": [{"id": k, "label": v} for k, v in WarehouseZone.ZONE_TYPES],
        "submit_url": request.path,
        "list_url": "/warehouse/zones/",
        "report_title": "Warehouse Zone Form",
    }
    return render(request, "lumra_pages/inventory/warehouse_zone_form.html", context)


# ------------------------------------------------------------------
# ADMIN / ANALYTICS PAGES
# ------------------------------------------------------------------

@login_required
def adjustment_reasons(request):
    reasons = StockAdjustmentReason.objects.order_by("code")
    rows = [{
        "id": r.id,
        "code": r.code,
        "name": r.name,
        "description": r.description,
        "is_active": r.is_active,
    } for r in reasons[:2000]]
    context = {"reasons_data": rows, "report_title": "Adjustment Reasons"}
    return render(request, "lumra_pages/inventory/adjustment_reasons.html", context)


@login_required
def supplier_evaluation(request):
    """
    Lightweight vendor performance snapshot using data currently available
    (SupplierPrice). Replace with PO/GRN-based metrics when purchasing module exists.
    """
    vendors = Vendor.objects.filter(is_active=True).order_by("name")
    # Aggregate supplier prices per vendor as a proxy
    price_stats = (
        SupplierPrice.objects.filter(is_active=True)
        .values("vendor_id")
        .annotate(
            variants_count=Count("variant_id", distinct=True),
            avg_price=Avg("unit_price"),
            preferred_count=Count("id", filter=Q(is_preferred=True)),
        )
    )
    stats_by_vendor = {row["vendor_id"]: row for row in price_stats}

    rows = []
    for v in vendors:
        s = stats_by_vendor.get(v.id, {})
        rows.append({
            "id": v.id,
            "name": v.name,
            "variants_count": int(s.get("variants_count") or 0),
            "preferred_count": int(s.get("preferred_count") or 0),
            "avg_price": float(s.get("avg_price") or 0),
        })

    context = {"vendors_data": rows, "report_title": "Supplier Evaluation"}
    return render(request, "lumra_pages/inventory/supplier_evaluation.html", context)
