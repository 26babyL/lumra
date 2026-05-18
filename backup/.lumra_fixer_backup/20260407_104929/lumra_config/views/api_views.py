# lumra_config/views/api_views.py
# Auto-generated oleh lumra_sync.py dari core/views/api_views.py
# JANGAN EDIT MANUAL — edit core/views/api_views.py lalu jalankan lumra_sync.py lagi

import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from lumra_config.models import (
    Location,
    ProductVariant,
    Requisition,
    RequisitionItem,
    Stock,
    Transfer,
    TransferItem,
    UserProfile,
)


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def _parse_json(request):
    """
    Parse request body as JSON.
    Returns (payload, None) on success or (None, JsonResponse) on failure.
    """
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, JsonResponse({"error": "Invalid JSON body."}, status=400)


def _net_stock(variant, location):
    """
    Return the net stock quantity for a variant at a location.

    Stock is a ledger — net = inbound totals − outbound totals.
    Uses select_for_update() so callers inside a transaction hold a row lock.
    """
    INBOUND  = ("in", "transfer_received", "adjustment")
    OUTBOUND = ("out", "transfer_sent")

    rows = (
        Stock.objects
        .select_for_update()
        .filter(variant=variant, location=location)
        .aggregate(
            inbound=Sum(
                "quantity",
                filter=Q(transaction_type__in=INBOUND),
            ),
            outbound=Sum(
                "quantity",
                filter=Q(transaction_type__in=OUTBOUND),
            ),
        )
    )
    return (rows["inbound"] or 0) - (rows["outbound"] or 0)


def _net_stock_all_locations(variant):
    """
    Return a dict of {location_id: net_stock} for a variant across all locations.
    No row lock — read-only summary.
    """
    INBOUND  = ("in", "transfer_received", "adjustment")
    OUTBOUND = ("out", "transfer_sent")

    inbound_qs = (
        Stock.objects
        .filter(variant=variant, transaction_type__in=INBOUND)
        .values("location_id")
        .annotate(total=Sum("quantity"))
    )
    outbound_qs = (
        Stock.objects
        .filter(variant=variant, transaction_type__in=OUTBOUND)
        .values("location_id")
        .annotate(total=Sum("quantity"))
    )

    result = {}
    for row in inbound_qs:
        result[row["location_id"]] = row["total"] or 0
    for row in outbound_qs:
        result[row["location_id"]] = result.get(row["location_id"], 0) - (row["total"] or 0)
    return result


# ------------------------------------------------------------------
# API: SUBMIT REQUISITION
# ------------------------------------------------------------------

@login_required
@require_POST
def submit_requisition(request):
    """
    User requests stock from a source location to their own location.

    Expected JSON body:
    {
        "from_location": <int location_id>,   # source / warehouse
        "items": [
            {"sku": "SKU001", "quantity": 5},
            ...
        ]
    }

    FIX: from_location is the SOURCE (warehouse), to_location is the
    requesting user's location. Original code had these swapped.
    """
    payload, err = _parse_json(request)
    if err:
        return err

    # Validate required fields
    if "from_location" not in payload or "items" not in payload:
        return JsonResponse(
            {"error": "Missing required fields: 'from_location' and 'items'."},
            status=400,
        )

    items = payload["items"]
    if not isinstance(items, list) or len(items) == 0:
        return JsonResponse({"error": "'items' must be a non-empty list."}, status=400)

    # UserProfile must exist — we do not silently create one
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if not user_profile.location:
        return JsonResponse({"error": "Your user account has no location assigned."}, status=400)

    from_location = get_object_or_404(Location, id=payload["from_location"])

    if from_location == user_profile.location:
        return JsonResponse(
            {"error": "Source and destination location cannot be the same."},
            status=400,
        )

    with transaction.atomic():
        requisition = Requisition.objects.create(
            from_location=from_location,        # source: warehouse/supplier location
            to_location=user_profile.location,  # destination: requesting user's location
            requested_by=request.user,
            status="waiting",
        )

        for item in items:
            sku      = item.get("sku", "").strip()
            quantity = item.get("quantity")

            if not sku:
                raise ValueError("Each item must have a 'sku'.")
            if not isinstance(quantity, (int, float)) or quantity <= 0:
                raise ValueError(f"Item '{sku}' has an invalid quantity: {quantity!r}.")

            variant = get_object_or_404(ProductVariant, sku=sku)

            RequisitionItem.objects.create(
                requisition=requisition,
                variant=variant,
                quantity=int(quantity),
            )

    return JsonResponse({"success": True, "requisition_id": requisition.id}, status=201)


# ------------------------------------------------------------------
# API: SUBMIT PURCHASES (BASIC STUB)
# ------------------------------------------------------------------

@login_required
@require_POST
def submit_purchases(request):
    """
    Endpoint used by the purchasing page JavaScript.  The payload has the
    form {"purchases": [...]} where each item contains at least a
    SKU and an array of vendor/quantity pairs.  For now the view is a
    simple stub that validates JSON and returns success; future
    enhancements may create Order/OrderItem records.
    """
    payload, err = _parse_json(request)
    if err:
        return err

    # basic validation so client gets a 400 if structure is wrong
    if "purchases" not in payload or not isinstance(payload["purchases"], list):
        return JsonResponse({"error": "Missing or invalid 'purchases' list."}, status=400)

    # TODO: insert business logic here (create orders, adjust stock, etc.)
    # for now just acknowledge receipt
    return JsonResponse({"success": True}, status=201)


# ------------------------------------------------------------------
# API: APPROVE REQUISITION (STAFF ONLY)
# ------------------------------------------------------------------

@login_required
@require_POST
def approve_requisition(request, requisition_id):
    """
    Staff approves a waiting requisition and creates a Transfer.

    FIX: Removed the double-save (approved → in_transit). The
    requisition moves directly to 'in_transit' in a single save().
    """
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized — staff only."}, status=403)

    requisition = get_object_or_404(Requisition, id=requisition_id)

    if requisition.status != "waiting":
        return JsonResponse(
            {"error": f"Cannot approve a requisition with status '{requisition.status}'."},
            status=400,
        )

    with transaction.atomic():
        # Move directly to in_transit — no need for an intermediate 'approved' save
        requisition.status      = "in_transit"
        requisition.approved_by = request.user
        requisition.approved_at = timezone.now()
        requisition.save()

        transfer = Transfer.objects.create(
            requisition=requisition,
            source_location=requisition.from_location,
            destination_location=requisition.to_location,
            created_by=request.user,
            status="in_transit",
        )

        TransferItem.objects.bulk_create([
            TransferItem(
                transfer=transfer,
                variant=item.variant,
                quantity_sent=item.quantity,
            )
            for item in requisition.items.select_related("variant").all()
        ])

    return JsonResponse({"success": True, "transfer_id": transfer.id})


# ------------------------------------------------------------------
# API: CONFIRM RECEIPT OF TRANSFER
# ------------------------------------------------------------------

@login_required
@require_POST
def confirm_receipt(request, transfer_id):
    """
    Destination user confirms goods received.

    FIX 1 — Ledger correctness:
        Stock is a LEDGER. We never mutate existing rows.
        Each movement creates two new rows:
          • transaction_type='transfer_sent'     at source  (negative quantity)
          • transaction_type='transfer_received' at destination (positive quantity)

    FIX 2 — Race condition:
        _net_stock() uses select_for_update() inside the transaction,
        so concurrent requests cannot both pass the sufficiency check.

    FIX 3 — Authorization:
        User must belong to the destination location of the transfer.
    """
    transfer = get_object_or_404(
        Transfer.objects.select_related(
            "source_location", "destination_location", "requisition"
        ),
        id=transfer_id,
    )

    user_profile = get_object_or_404(UserProfile, user=request.user)

    if not user_profile.location or transfer.destination_location != user_profile.location:
        return JsonResponse(
            {"error": "You are not authorised to confirm this transfer."},
            status=403,
        )

    if transfer.status != "in_transit":
        return JsonResponse(
            {"error": f"Transfer is not in transit (current status: '{transfer.status}')."},
            status=400,
        )

    with transaction.atomic():
        items = list(
            transfer.items.select_related("variant").all()
        )

        # ── Sufficiency check (inside transaction, row-locked) ──────
        for item in items:
            available = _net_stock(item.variant, transfer.source_location)
            if available < item.quantity_sent:
                return JsonResponse(
                    {
                        "error": (
                            f"Insufficient stock for '{item.variant.sku}' "
                            f"at source location. "
                            f"Available: {available}, required: {item.quantity_sent}."
                        )
                    },
                    status=400,
                )

        # ── Write ledger rows ────────────────────────────────────────
        ledger_rows = []
        for item in items:
            # Debit source
            ledger_rows.append(Stock(
                variant=item.variant,
                location=transfer.source_location,
                quantity=item.quantity_sent,
                transaction_type="transfer_sent",
                notes=f"Transfer #{transfer.id} sent",
            ))
            # Credit destination
            ledger_rows.append(Stock(
                variant=item.variant,
                location=transfer.destination_location,
                quantity=item.quantity_sent,
                transaction_type="transfer_received",
                notes=f"Transfer #{transfer.id} received",
            ))

        Stock.objects.bulk_create(ledger_rows)

        # ── Update TransferItems ────────────────────────────────────
        for item in items:
            item.quantity_received = item.quantity_sent
        TransferItem.objects.bulk_update(items, ["quantity_received"])

        # ── Close out Transfer & Requisition ────────────────────────
        transfer.status      = "received"
        transfer.received_at = timezone.now()
        transfer.save(update_fields=["status", "received_at"])

        if transfer.requisition:
            transfer.requisition.status = "completed"
            transfer.requisition.save(update_fields=["status"])

    return JsonResponse({"success": True})


# ------------------------------------------------------------------
# API: SUBMIT STOCK ALLOCATION (Planning)
# ------------------------------------------------------------------

@login_required
@require_POST
def submit_stock_allocation(request):
    """
    Create requisitions from the Stock Planning UI.

    FIX: 'from_location' must be provided explicitly in each requisition
    object — we no longer silently fall back to Location.objects.first()
    which is non-deterministic.

    Expected JSON body:
    {
        "requisitions": [
            {
                "sku":           "SKU001",
                "from_location": <int location_id>,
                "quantity":      10
            },
            ...
        ]
    }
    """
    payload, err = _parse_json(request)
    if err:
        return err

    requisitions_data = payload.get("requisitions", [])
    if not isinstance(requisitions_data, list) or not requisitions_data:
        return JsonResponse(
            {"error": "'requisitions' must be a non-empty list."},
            status=400,
        )

    # UserProfile must already exist
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if not user_profile.location:
        return JsonResponse(
            {"error": "Your user account has no location assigned."},
            status=400,
        )

    created = []

    try:
        with transaction.atomic():
            for req_data in requisitions_data:
                sku           = req_data.get("sku", "").strip()
                quantity      = req_data.get("quantity")
                from_loc_id   = req_data.get("from_location")

                if not sku:
                    raise ValueError("Each requisition must include a 'sku'.")
                if not isinstance(quantity, (int, float)) or quantity <= 0:
                    raise ValueError(f"Invalid quantity for '{sku}': {quantity!r}.")
                if not from_loc_id:
                    raise ValueError(f"Missing 'from_location' for '{sku}'.")

                variant       = get_object_or_404(ProductVariant.objects.select_related("product"), sku=sku)
                from_location = get_object_or_404(Location, id=from_loc_id)

                if from_location == user_profile.location:
                    raise ValueError(
                        f"Source and destination location cannot be the same for '{sku}'."
                    )

                requisition = Requisition.objects.create(
                    from_location=from_location,
                    to_location=user_profile.location,
                    requested_by=request.user,
                    status="waiting",
                    notes=f"Stock allocation for {variant.product.name}",
                )

                RequisitionItem.objects.create(
                    requisition=requisition,
                    variant=variant,
                    quantity=int(quantity),
                )

                created.append({
                    "id":       requisition.id,
                    "sku":      variant.sku,
                    "product":  variant.product.name,
                    "quantity": int(quantity),
                })

    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({
        "success": True,
        "message": f"{len(created)} requisition(s) created.",
        "requisitions": created,
    }, status=201)


# ------------------------------------------------------------------
# API: GET STOCK PER LOCATION  (read-only, GET allowed)
# ------------------------------------------------------------------

@login_required
def get_location_stock(request, product_sku):
    """
    Return net stock for a variant across all locations.

    FIX: Stock is a ledger — we must aggregate (Sum) per location,
    not return individual transaction rows. Net = inbound − outbound.
    """
    variant = get_object_or_404(
        ProductVariant.objects.select_related("product"),
        sku=product_sku,
    )

    net_by_location = _net_stock_all_locations(variant)

    # Enrich with location names
    locations = Location.objects.filter(id__in=net_by_location.keys())
    location_map = {loc.id: loc.name for loc in locations}

    location_data = [
        {
            "id":        loc_id,
            "name":      location_map.get(loc_id, "—"),
            "net_stock": net_qty,
        }
        for loc_id, net_qty in sorted(net_by_location.items(), key=lambda x: x[0])
    ]

    return JsonResponse({
        "success":   True,
        "sku":       variant.sku,
        "product":   variant.product.name,
        "locations": location_data,
    })