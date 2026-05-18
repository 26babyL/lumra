import json
from datetime import date

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods

from lumra_config.models import (
    BillOfMaterial,
    BillOfMaterialItem,
    FinishedGoodsReceipt,
    Location,
    ProductVariant,
    ProductionMaterialConsumption,
    ProductionOrder,
    ProductionWasteRecord,
    Unit,
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


def _suggest_po_code():
    current_year = localtime().year
    prefix = f"PO-{current_year}-"
    latest = (
        ProductionOrder.objects
        .filter(code__startswith=prefix)
        .order_by("-code")
        .values_list("code", flat=True)
        .first()
    )
    next_number = 1
    if latest:
        try:
            next_number = int(str(latest).split("-")[-1]) + 1
        except (TypeError, ValueError):
            next_number = ProductionOrder.objects.filter(code__startswith=prefix).count() + 1
    return f"{prefix}{str(next_number).zfill(4)}"


def _rnd_session_key():
    return "production_rnd_records"


def _default_rnd_records():
    return [
        {
            "id": 1,
            "name": "Dark Roast Honey Blend",
            "code": "RND-001",
            "target_sku": "",
            "category": "beverage_hot",
            "created_by": "Tim RnD",
            "description": "Eksperimen minuman baru dengan karakter bold dan sweet finish.",
            "tags": ["new-product", "coffee"],
            "based_on": "",
            "planned_trials": 3,
            "notes": "",
            "hypothesis_notes": "Target body medium-high dengan aftertaste manis.",
            "probability_reason": "Bahan utama sudah stabil, tinggal tuning rasio.",
            "success_probability": 70,
            "status": "in_trial",
            "bom_id": None,
            "created_at": localtime().strftime("%Y-%m-%d %H:%M"),
            "hypothesis": {
                "acidity": 4,
                "body": 7,
                "sweetness": 6,
                "bitterness": 5,
                "aftertaste": 7,
                "aroma": 8,
            },
            "items": [
                {"name": "Espresso Blend", "sku": "BEAN-ESP", "quantity": 18, "unit": "gr", "estimated_cost": 3500},
                {"name": "Honey Syrup", "sku": "SYR-HNY", "quantity": 12, "unit": "ml", "estimated_cost": 2000},
                {"name": "Fresh Milk", "sku": "MLK-FRS", "quantity": 150, "unit": "ml", "estimated_cost": 2800},
            ],
            "trials": [
                {
                    "id": 101,
                    "number": 1,
                    "is_active": True,
                    "is_best": False,
                    "date": localtime().strftime("%Y-%m-%d"),
                    "note_short": "Masih terlalu manis",
                    "notes": "Body sudah cukup baik, tapi sweetness perlu diturunkan sedikit.",
                    "success_probability": 68,
                    "tasting": {
                        "acidity": 4,
                        "body": 7,
                        "sweetness": 8,
                        "bitterness": 4,
                        "aftertaste": 6,
                        "aroma": 7,
                    },
                    "items": [
                        {"name": "Espresso Blend", "sku": "BEAN-ESP", "quantity": 18, "unit": "gr", "estimated_cost": 3500},
                        {"name": "Honey Syrup", "sku": "SYR-HNY", "quantity": 12, "unit": "ml", "estimated_cost": 2000},
                        {"name": "Fresh Milk", "sku": "MLK-FRS", "quantity": 150, "unit": "ml", "estimated_cost": 2800},
                    ],
                }
            ],
        }
    ]


def _load_rnd_records(request):
    records = request.session.get(_rnd_session_key())
    if records is None:
        records = _default_rnd_records()
        request.session[_rnd_session_key()] = records
    return records


def _save_rnd_records(request, records):
    request.session[_rnd_session_key()] = records
    request.session.modified = True


def _find_rnd_record(records, rnd_id):
    return next((record for record in records if int(record["id"]) == int(rnd_id)), None)


# ------------------------------------------------------------------
# BOM
# ------------------------------------------------------------------

@login_required
def bom_list(request):
    query = request.GET.get("q", "").strip()
    qs = (
        BillOfMaterial.objects
        .select_related("finished_variant", "finished_variant__product")
        .prefetch_related("items__component")
        .all()
    )
    if query:
        qs = qs.filter(
            Q(code__icontains=query)
            | Q(finished_variant__sku__icontains=query)
            | Q(finished_variant__product__name__icontains=query)
        )
    qs = qs.order_by("-updated_at")

    rows = []
    for b in qs[:500]:
        items = list(b.items.all())
        rows.append({
            "id": b.id,
            "code": b.code,
            "name": b.name or (b.finished_variant.product.name if b.finished_variant.product else b.finished_variant.sku),
            "sku": b.finished_variant.sku,
            "version": b.version,
            "is_active": b.is_active,
            "ingredients_count": len(items),
            "estimated_cost": float(sum((it.quantity or 0) * (it.component.price_buy or 0) for it in items)),
            "updated_at": localtime(b.updated_at).strftime("%Y-%m-%d"),
        })
    context = {"boms_data": rows, "report_title": "BOM List"}
    return render(request, "lumra_pages/production/bom_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def bom_form(request, pk=None):
    bom = get_object_or_404(BillOfMaterial, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["finished_variant_id", "code", "version", "items"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        finished_variant = get_object_or_404(ProductVariant, pk=payload["finished_variant_id"])
        items = payload.get("items") or []
        if not isinstance(items, list) or len(items) == 0:
            return JsonResponse({"success": False, "error": "Items must be a non-empty list."}, status=400)

        with transaction.atomic():
            obj = bom or BillOfMaterial(created_by=request.user)
            obj.finished_variant = finished_variant
            obj.code = str(payload["code"]).strip()
            obj.version = int(payload.get("version") or 1)
            obj.name = str(payload.get("name", "")).strip()
            obj.notes = str(payload.get("notes", "")).strip()
            obj.is_active = bool(payload.get("is_active", True))
            obj.save()

            BillOfMaterialItem.objects.filter(bom=obj).delete()
            item_objs = []
            for it in items:
                comp_id = it.get("component_variant_id")
                qty = it.get("quantity")
                if not comp_id or qty is None:
                    continue
                component = get_object_or_404(ProductVariant, pk=comp_id)
                unit = None
                if it.get("unit_id"):
                    unit = get_object_or_404(Unit, pk=it["unit_id"])
                item_objs.append(BillOfMaterialItem(
                    bom=obj,
                    component=component,
                    quantity=qty,
                    unit=unit,
                    notes=str(it.get("notes", "")).strip(),
                ))
            if not item_objs:
                return JsonResponse({"success": False, "error": "No valid BOM items provided."}, status=400)
            BillOfMaterialItem.objects.bulk_create(item_objs)

        return JsonResponse({"success": True, "id": obj.id})

    variants = ProductVariant.objects.select_related("product").order_by("sku")[:3000]
    units = Unit.objects.order_by("symbol")
    context = {
        "is_edit": bool(bom),
        "bom_id": bom.id if bom else None,
        "variants_data": [
            {"id": v.id, "sku": v.sku, "name": v.product.name if v.product else v.sku, "price_buy": float(v.price_buy or 0)}
            for v in variants
        ],
        "units_data": [{"id": u.id, "symbol": u.symbol, "name": u.name} for u in units],
        "bom_data": {
            "id": bom.id,
            "code": bom.code,
            "version": bom.version,
            "name": bom.name or "",
            "finished_sku": bom.finished_variant.sku,
            "notes": bom.notes or "",
            "is_active": bom.is_active,
            "items": [
                {
                    "id": item.id,
                    "sku": item.component.sku,
                    "name": item.component.product.name if item.component.product else item.component.sku,
                    "quantity": float(item.quantity or 0),
                    "unit": item.unit.symbol if item.unit else "",
                    "unit_price": float(item.component.price_buy or 0),
                }
                for item in bom.items.select_related("component", "component__product", "unit").all()
            ],
        } if bom else {},
        "submit_url": request.path,
        "list_url": "/production/bom/",
        "report_title": "BOM Form",
    }
    return render(request, "lumra_pages/production/bom_form.html", context)


@login_required
def bom_detail(request, pk):
    bom = get_object_or_404(
        BillOfMaterial.objects.select_related("finished_variant", "finished_variant__product")
        .prefetch_related("items__component", "items__component__product", "items__component__stock_entries", "items__unit"),
        pk=pk,
    )
    items = []
    for it in bom.items.all():
        items.append({
            "id": it.id,
            "sku": it.component.sku,
            "name": it.component.product.name if it.component.product else it.component.sku,
            "quantity": float(it.quantity),
            "unit": it.unit.symbol if it.unit else "",
            "unit_price": float(it.component.price_buy or 0),
            "total": float((it.quantity or 0) * (it.component.price_buy or 0)),
            "stock": float(it.component.total_stock or 0),
        })
    data = {
        "id": bom.id,
        "code": bom.code,
        "name": bom.name or (bom.finished_variant.product.name if bom.finished_variant.product else bom.finished_variant.sku),
        "finished_sku": bom.finished_variant.sku,
        "version": bom.version,
        "is_active": bom.is_active,
        "notes": bom.notes,
        "rnd_id": getattr(bom, "rnd_id", None),
        "estimated_cost": float(sum((it.quantity or 0) * (it.component.price_buy or 0) for it in bom.items.all())),
        "items": items,
        "updated_at": localtime(bom.updated_at).strftime("%Y-%m-%d %H:%M"),
        "versions": [
            {
                "id": sibling.id,
                "version": sibling.version,
                "is_active": sibling.is_active,
                "created_at": localtime(sibling.created_at).strftime("%Y-%m-%d %H:%M"),
                "created_by": sibling.created_by.get_username() if sibling.created_by else "System",
            }
            for sibling in BillOfMaterial.objects.select_related("created_by")
            .filter(finished_variant=bom.finished_variant)
            .order_by("-version", "-created_at")[:10]
        ],
    }
    context = {"bom_data": data, "report_title": f"BOM Detail - {bom.code}"}
    return render(request, "lumra_pages/production/bom_detail.html", context)


# ------------------------------------------------------------------
# PRODUCTION ORDERS
# ------------------------------------------------------------------

@login_required
def production_order_list(request):
    query = request.GET.get("q", "").strip()
    qs = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .order_by("-created_at")
    )
    if query:
        qs = qs.filter(
            Q(code__icontains=query)
            | Q(bom__code__icontains=query)
            | Q(bom__finished_variant__sku__icontains=query)
            | Q(bom__finished_variant__product__name__icontains=query)
        )

    rows = []
    for po in qs[:500]:
        product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
        rows.append({
            "id": po.id,
            "code": po.code,
            "product": product_name,
            "target_qty": float(po.target_quantity),
            "produced_qty": float(po.produced_quantity),
            "uom": po.unit.symbol if po.unit else "",
            "status": po.status,
            "line": po.line or "-",
            "start_date": po.scheduled_date.strftime("%d %b") if po.scheduled_date else "",
            "priority": po.priority or "Normal",
        })

    context = {"pos_data": rows, "report_title": "Production Orders"}
    return render(request, "lumra_pages/production/production_order_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def production_order_form(request, pk=None):
    po = get_object_or_404(ProductionOrder, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["code", "bom_id", "target_quantity"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        bom = get_object_or_404(BillOfMaterial, pk=payload["bom_id"])
        unit = None
        if payload.get("unit_id"):
            unit = get_object_or_404(Unit, pk=payload["unit_id"])

        obj = po or ProductionOrder(created_by=request.user)
        obj.code = str(payload["code"]).strip()
        obj.bom = bom
        obj.target_quantity = payload.get("target_quantity") or 0
        obj.unit = unit
        obj.priority = str(payload.get("priority", "Normal")).strip() or "Normal"
        obj.line = str(payload.get("line", "")).strip()
        obj.status = str(payload.get("status", obj.status)).strip() or obj.status
        obj.notes = str(payload.get("notes", "")).strip()
        obj.scheduled_date = _parse_iso_date(payload.get("scheduled_date"))
        obj.save()

        return JsonResponse({"success": True, "id": obj.id})

    boms = (
        BillOfMaterial.objects
        .select_related("finished_variant", "finished_variant__product")
        .filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "items",
                queryset=BillOfMaterialItem.objects.select_related(
                    "component",
                    "component__product",
                    "unit",
                ).prefetch_related("component__stock_entries"),
            )
        )
        .order_by("-updated_at")[:1000]
    )
    units = Unit.objects.order_by("symbol")
    context = {
        "is_edit": bool(po),
        "po_id": po.id if po else None,
        "boms_data": [
            {
                "id": b.id,
                "code": b.code,
                "name": b.name or (b.finished_variant.product.name if b.finished_variant.product else b.finished_variant.sku),
                "sku": b.finished_variant.sku,
                "items": [
                    {
                        "id": item.id,
                        "sku": item.component.sku,
                        "name": item.component.product.name if item.component.product else item.component.sku,
                        "quantity": float(item.quantity or 0),
                        "unit": item.unit.symbol if item.unit else "",
                        "unit_price": float(item.component.price_buy or 0),
                        "stock": float(item.component.total_stock or 0),
                    }
                    for item in b.items.all()
                ],
            }
            for b in boms
        ],
        "units_data": [{"id": u.id, "symbol": u.symbol} for u in units],
        "po_data": {
            "id": po.id,
            "code": po.code,
            "bom_id": po.bom_id,
            "target_quantity": float(po.target_quantity or 0),
            "line": po.line or "",
            "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
            "priority": po.priority or "Normal",
            "notes": po.notes or "",
            "unit_id": po.unit_id,
        } if po else {},
        "suggested_po_code": po.code if po else _suggest_po_code(),
        "submit_url": request.path,
        "list_url": "/production/order/",
        "report_title": "Production Order Form",
    }
    return render(request, "lumra_pages/production/production_order_form.html", context)


@login_required
def production_order_detail(request, pk):
    po = get_object_or_404(
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit"),
        pk=pk,
    )
    product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
    data = {
        "id": po.id,
        "code": po.code,
        "product": product_name,
        "bom_code": po.bom.code,
        "status": po.status,
        "target_qty": float(po.target_quantity),
        "produced_qty": float(po.produced_quantity),
        "uom": po.unit.symbol if po.unit else "",
        "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
        "started_at": localtime(po.started_at).strftime("%Y-%m-%d %H:%M") if po.started_at else "",
        "completed_at": localtime(po.completed_at).strftime("%Y-%m-%d %H:%M") if po.completed_at else "",
        "priority": po.priority,
        "line": po.line,
        "notes": po.notes,
        "created_at": localtime(po.created_at).strftime("%Y-%m-%d %H:%M"),
    }
    context = {"po_data": data, "report_title": f"Production Order - {po.code}"}
    return render(request, "lumra_pages/production/production_order_detail.html", context)


# ------------------------------------------------------------------
# SCHEDULING / EXECUTION PAGES (Lightweight placeholders)
# ------------------------------------------------------------------

@login_required
def production_scheduling(request):
    qs = ProductionOrder.objects.select_related("bom", "bom__finished_variant", "bom__finished_variant__product").order_by("scheduled_date")[:500]
    rows = []
    for po in qs:
        product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
        rows.append({
            "id": po.id,
            "code": po.code,
            "product": product_name,
            "status": po.status,
            "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
        })
    context = {"orders_data": rows, "report_title": "Production Scheduling"}
    return render(request, "lumra_pages/production/production_scheduling.html", context)


@login_required
def material_consumption(request):
    qs = (
        ProductionMaterialConsumption.objects
        .select_related("production_order", "component", "component__product", "unit")
        .order_by("-consumed_at")[:500]
    )
    rows = []
    for c in qs:
        rows.append({
            "id": c.id,
            "po_code": c.production_order.code,
            "sku": c.component.sku,
            "name": c.component.product.name if c.component.product else c.component.sku,
            "quantity": float(c.quantity),
            "unit": c.unit.symbol if c.unit else "",
            "consumed_at": localtime(c.consumed_at).strftime("%Y-%m-%d %H:%M"),
        })
    completed_orders = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .prefetch_related("bom__items__component", "bom__items__component__product", "bom__items__unit", "consumptions")
        .filter(status="completed")
        .order_by("-completed_at", "-created_at")[:200]
    )
    context = {
        "consumptions_data": rows,
        "completed_orders_data": [
            {
                "id": po.id,
                "code": po.code,
                "product": po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku,
                "status": po.status,
                "produced_qty": float(po.produced_quantity or 0),
                "uom": po.unit.symbol if po.unit else "",
                "consumption_recorded": po.consumptions.exists(),
                "standard_items": [
                    {
                        "sku": item.component.sku,
                        "name": item.component.product.name if item.component.product else item.component.sku,
                        "standard_qty": float(item.quantity or 0) * float(po.produced_quantity or 0),
                        "unit": item.unit.symbol if item.unit else "",
                    }
                    for item in po.bom.items.all()
                ],
            }
            for po in completed_orders
        ],
        "report_title": "Material Consumption",
    }
    return render(request, "lumra_pages/production/material_consumption.html", context)


@login_required
def finished_goods_receipt(request):
    qs = (
        FinishedGoodsReceipt.objects
        .select_related("production_order", "finished_variant", "finished_variant__product", "location")
        .order_by("-received_at")[:500]
    )
    rows = []
    for r in qs:
        rows.append({
            "id": r.id,
            "po_code": r.production_order.code,
            "sku": r.finished_variant.sku,
            "product": r.finished_variant.product.name if r.finished_variant.product else r.finished_variant.sku,
            "location": r.location.name,
            "quantity": float(r.quantity_received),
            "received_at": localtime(r.received_at).strftime("%Y-%m-%d %H:%M"),
        })
    completed_orders = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .prefetch_related("receipts")
        .filter(status="completed")
        .order_by("-completed_at", "-created_at")[:200]
    )
    locations = Location.objects.order_by("name")[:500]
    context = {
        "receipts_data": rows,
        "completed_orders_data": [
            {
                "id": po.id,
                "code": po.code,
                "product": po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku,
                "sku": po.bom.finished_variant.sku,
                "target_qty": float(po.target_quantity or 0),
                "produced_qty": float(po.produced_quantity or 0),
                "uom": po.unit.symbol if po.unit else "",
                "receipt_recorded": po.receipts.exists(),
            }
            for po in completed_orders
        ],
        "locations_data": [{"id": location.id, "name": location.name} for location in locations],
        "report_title": "Finished Goods Receipt",
    }
    return render(request, "lumra_pages/production/finished_goods_receipt.html", context)


@login_required
def production_waste(request):
    qs = (
        ProductionWasteRecord.objects
        .select_related("production_order", "component", "component__product", "unit")
        .order_by("-recorded_at")[:500]
    )
    rows = []
    for w in qs:
        rows.append({
            "id": w.id,
            "po_code": w.production_order.code,
            "waste_type": w.waste_type,
            "sku": w.component.sku if w.component else "",
            "name": w.component.product.name if (w.component and w.component.product) else (w.component.sku if w.component else ""),
            "quantity": float(w.quantity),
            "unit": w.unit.symbol if w.unit else "",
            "recorded_at": localtime(w.recorded_at).strftime("%Y-%m-%d %H:%M"),
        })
    completed_orders = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .filter(status="completed")
        .order_by("-completed_at", "-created_at")[:200]
    )
    variants = ProductVariant.objects.select_related("product").order_by("sku")[:3000]
    units = Unit.objects.order_by("symbol")
    context = {
        "waste_data": rows,
        "completed_orders_data": [
            {
                "id": po.id,
                "code": po.code,
                "product": po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku,
                "produced_qty": float(po.produced_quantity or 0),
                "uom": po.unit.symbol if po.unit else "",
            }
            for po in completed_orders
        ],
        "variants_data": [
            {
                "id": variant.id,
                "sku": variant.sku,
                "name": variant.product.name if variant.product else variant.sku,
                "price_buy": float(variant.price_buy or 0),
            }
            for variant in variants
        ],
        "units_data": [{"id": unit.id, "symbol": unit.symbol} for unit in units],
        "report_title": "Production Waste",
    }
    return render(request, "lumra_pages/production/production_waste.html", context)


@login_required
def production_costing(request):
    """
    Placeholder costing page. Real costing should aggregate:
    - consumption * latest cost
    - waste
    - overhead allocations
    """
    qs = ProductionOrder.objects.select_related("bom", "bom__finished_variant", "bom__finished_variant__product").order_by("-created_at")[:200]
    rows = []
    for po in qs:
        product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
        standard_material_cost = float(sum((item.quantity or 0) * (item.component.price_buy or 0) for item in po.bom.items.all())) * float(po.target_quantity or 0)
        actual_material_cost = float(sum((consumption.quantity or 0) * (consumption.component.price_buy or 0) for consumption in po.consumptions.select_related("component").all()))
        waste_value = float(sum((waste.quantity or 0) * (waste.component.price_buy or 0) for waste in po.wastes.select_related("component").all() if waste.component))
        target_qty = float(po.target_quantity or 0)
        produced_qty = float(po.produced_quantity or 0)
        rows.append({
            "id": po.id,
            "code": po.code,
            "product": product_name,
            "status": po.status,
            "target_qty": target_qty,
            "produced_qty": produced_qty,
            "standard_material_cost": standard_material_cost,
            "actual_material_cost": actual_material_cost,
            "waste_value": waste_value,
            "variance": actual_material_cost - standard_material_cost,
            "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
            "completed_at": localtime(po.completed_at).strftime("%Y-%m-%d %H:%M") if po.completed_at else "",
            "completion_pct": min(round((produced_qty / target_qty) * 100), 100) if target_qty > 0 else 0,
            "is_overproduced": produced_qty > target_qty if target_qty > 0 else False,
        })
    context = {"orders_data": rows, "report_title": "Production Costing"}
    return render(request, "lumra_pages/production/production_costing.html", context)


# ------------------------------------------------------------------
# RND (session-backed lightweight prototype)
# ------------------------------------------------------------------

@login_required
def rnd_list(request):
    records = _load_rnd_records(request)
    rows = []
    for record in records:
        items = record.get("items") or []
        trials = record.get("trials") or []
        rows.append({
            "id": record["id"],
            "name": record.get("name") or record.get("code") or f"RND-{record['id']}",
            "code": record.get("code") or f"RND-{record['id']}",
            "status": record.get("status") or "idea",
            "created_by": record.get("created_by") or "-",
            "trial_count": len(trials),
            "ingredient_count": len(items),
            "success_probability": float(record.get("success_probability") or 0),
            "estimated_cost": float(sum(float(item.get("estimated_cost") or 0) for item in items)),
        })
    context = {"rnds_data": rows, "report_title": "Lab RnD"}
    return render(request, "lumra_pages/production/rnd_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def rnd_form(request):
    records = _load_rnd_records(request)
    edit_id = request.GET.get("edit")
    rnd = _find_rnd_record(records, edit_id) if edit_id else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        items = payload.get("items") or []
        if not isinstance(items, list):
            return JsonResponse({"success": False, "error": "Items harus berupa list."}, status=400)

        next_id = max([int(r["id"]) for r in records] + [0]) + 1
        obj = rnd or {"id": next_id, "created_at": localtime().strftime("%Y-%m-%d %H:%M"), "bom_id": None, "trials": []}
        obj["name"] = str(payload.get("name", "")).strip()
        obj["code"] = obj.get("code") or f"RND-{obj['id']:03d}"
        obj["target_sku"] = payload.get("target_sku") or ""
        obj["category"] = payload.get("category") or "other"
        obj["created_by"] = str(payload.get("created_by") or request.user.get_username()).strip()
        obj["description"] = str(payload.get("description") or "").strip()
        obj["tags"] = payload.get("tags") or []
        obj["based_on"] = payload.get("based_on") or ""
        obj["planned_trials"] = int(payload.get("planned_trials") or 1)
        obj["notes"] = str(payload.get("notes") or "").strip()
        obj["hypothesis_notes"] = str(payload.get("hypothesis_notes") or "").strip()
        obj["hypothesis"] = payload.get("hypothesis") or {}
        obj["success_probability"] = float(payload.get("success_probability") or 0)
        obj["probability_reason"] = str(payload.get("probability_reason") or "").strip()
        obj["status"] = payload.get("status") or obj.get("status") or "idea"
        obj["items"] = [
            {
                "name": str(item.get("name") or item.get("sku") or "").strip(),
                "sku": str(item.get("sku") or item.get("name") or "").strip(),
                "component_variant_id": item.get("component_variant_id"),
                "quantity": float(item.get("quantity") or 0),
                "unit": next((u.symbol for u in Unit.objects.filter(pk=item.get("unit_id"))[:1]), "") if item.get("unit_id") else "",
                "estimated_cost": float(item.get("estimated_cost") or 0),
            }
            for item in items
            if item.get("name") or item.get("sku")
        ]

        if rnd:
            for idx, record in enumerate(records):
                if int(record["id"]) == int(obj["id"]):
                    records[idx] = obj
                    break
        else:
            records.append(obj)

        _save_rnd_records(request, records)
        return JsonResponse({"success": True, "id": obj["id"]})

    variants = ProductVariant.objects.select_related("product").order_by("sku")[:3000]
    units = Unit.objects.order_by("symbol")
    context = {
        "variants_data": [
            {"id": v.id, "sku": v.sku, "name": v.product.name if v.product else v.sku, "price_buy": float(v.price_buy or 0)}
            for v in variants
        ],
        "units_data": [{"id": u.id, "symbol": u.symbol, "name": u.name} for u in units],
        "rnd_data": rnd or {},
        "submit_url": request.path + (f"?edit={edit_id}" if edit_id else ""),
        "report_title": "RnD Form",
    }
    return render(request, "lumra_pages/production/rnd_form.html", context)


@login_required
def rnd_detail(request, pk):
    records = _load_rnd_records(request)
    rnd = _find_rnd_record(records, pk)
    if not rnd:
        return render(request, "lumra_pages/production/rnd_detail.html", {"rnd_data": {}, "report_title": "RnD Detail"})
    context = {"rnd_data": rnd, "report_title": f"RnD Detail - {rnd.get('name') or rnd.get('code')}"}
    return render(request, "lumra_pages/production/rnd_detail.html", context)


@login_required
@require_http_methods(["POST"])
def rnd_status_update(request, pk):
    records = _load_rnd_records(request)
    rnd = _find_rnd_record(records, pk)
    if not rnd:
        return JsonResponse({"success": False, "error": "Formula tidak ditemukan."}, status=404)
    payload, err = _parse_json_body(request)
    if err:
        return err
    rnd["status"] = str(payload.get("status") or rnd.get("status") or "idea")
    _save_rnd_records(request, records)
    return JsonResponse({"success": True})


@login_required
@require_http_methods(["POST"])
def rnd_promote(request, pk):
    records = _load_rnd_records(request)
    rnd = _find_rnd_record(records, pk)
    if not rnd:
        return JsonResponse({"success": False, "error": "Formula tidak ditemukan."}, status=404)
    if rnd.get("bom_id"):
        return JsonResponse({"success": True, "bom_id": rnd["bom_id"]})
    return JsonResponse({"success": False, "error": "Promote ke BOM backend final belum dibuat. Data RnD sudah bisa diakses dari menu."}, status=400)


@login_required
def rnd_trial_new(request, pk):
    return render(request, "lumra_pages/production/rnd_form.html", {
        "variants_data": [],
        "units_data": [],
        "rnd_data": {},
        "submit_url": "/rnd/form/",
        "report_title": f"Trial Baru RnD {pk}",
    })
