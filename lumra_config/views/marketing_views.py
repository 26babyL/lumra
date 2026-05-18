import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .helpers import check_queryset_empty, create_empty_context
from lumra_config.models import Category, Customer, PaymentVoucher, ProductVariant


def _empty_promotions_context():
    vouchers = []
    for voucher in PaymentVoucher.objects.select_related("vendor").order_by("-date", "-id")[:1000]:
        vouchers.append({
            "id": voucher.id,
            "name": voucher.memo or f"Payment Voucher {voucher.number}",
            "code": voucher.number,
            "type": "fixed",
            "value": float(voucher.amount_paid or 0),
            "max_discount": None,
            "min_purchase": 0,
            "valid_from": voucher.date.isoformat(),
            "valid_to": voucher.date.isoformat(),
            "usage_limit": 1,
            "used_count": 1,
            "is_active": True,
            "validity_label": voucher.date.strftime("%d %b %Y"),
        })
    return {
        "vouchers_json": json.dumps(vouchers, cls=DjangoJSONEncoder),
        "total_vouchers": PaymentVoucher.objects.count(),
        "active_vouchers": len(vouchers),
        "expired_vouchers": 0,
        "total_claims": len(vouchers),
    }


# ===== CAMPAIGN =====

@login_required
def campaign_list(request):
    """List all Campaigns."""
    context = {
        "campaigns": [],
        "total_campaigns": 0,
        "active_campaigns": 0,
        "total_budget": 0,
        "query": request.GET.get("q", ""),
    }
    return render(request, 'lumra_pages/marketing/campaign_list.html', context)


@login_required
def campaign_form(request, pk=None):
    """Create/Edit Campaign."""
    context = {"campaign": None, "products": ProductVariant.objects.select_related("product").order_by("product__name", "sku")}
    return render(request, 'lumra_pages/marketing/add_campaign.html' if not pk else 'lumra_pages/marketing/campaign.html', context)


@login_required
def campaign_detail(request, pk):
    """View Campaign detail."""
    context = {"campaign": None}
    return render(request, 'lumra_pages/marketing/campaign.html', context)


# ===== DISCOUNT =====

@login_required
def discount_list(request):
    """List all Discounts."""
    context = {
        "discounts": [],
        "total_discounts": 0,
        "active_discounts": 0,
        "total_usage": 0,
        "avg_discount": 0,
        "query": request.GET.get("q", ""),
    }
    return render(request, 'lumra_pages/marketing/discount.html', context)


@login_required
def discount_form(request, pk=None):
    """Create/Edit Discount."""
    context = {
        "discount": None,
        "categories": Category.objects.filter(is_active=True).order_by("name"),
        "products": ProductVariant.objects.select_related("product").order_by("product__name", "sku"),
    }
    return render(request, 'lumra_pages/marketing/discount.html', context)


# ===== VOUCHER =====

@login_required
def voucher_list(request):
    """List all Vouchers."""
    context = _empty_promotions_context()
    return render(request, 'lumra_pages/marketing/voucher_list.html', context)


@login_required
def voucher_form(request, pk=None):
    """Create/Edit Voucher."""
    categories = Category.objects.filter(is_active=True).order_by("name").values("id", "name")
    products = ProductVariant.objects.select_related("product").order_by("product__name", "sku")
    products_payload = [
        {
            "id": variant.id,
            "name": f"{variant.product.name} ({variant.sku})",
            "category_id": variant.product.category_id,
        }
        for variant in products
    ]
    context = {
        "voucher": None,
        "categories_json": json.dumps(list(categories), cls=DjangoJSONEncoder),
        "products_json": json.dumps(products_payload, cls=DjangoJSONEncoder),
    }
    return render(request, 'lumra_pages/marketing/voucher_form.html', context)


@login_required
def voucher_claim_log(request):
    """View Voucher Claim Log."""
    context = {"claims": [], "total_claims": 0}
    return render(request, 'lumra_pages/marketing/voucher_claim_log.html', context)


# ===== LOYALTY PROGRAM =====

@login_required
def loyalty_members(request):
    """List all Loyalty Members."""
    query = request.GET.get("q", "").strip()
    tier = request.GET.get("tier", "").strip()
    members = Customer.objects.filter(is_active=True).order_by("-loyalty_points", "name")
    if query:
        members = members.filter(name__icontains=query) | members.filter(email__icontains=query)
    if tier:
        members = members.filter(tier=tier)

    paginator = Paginator(members, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    member_rows = [
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "points": customer.loyalty_points,
            "tier": customer.tier,
            "join_date": customer.created_at,
            "status": "active" if customer.is_active else "inactive",
        }
        for customer in page_obj.object_list
    ]
    all_members = Customer.objects.all()
    context = {
        "members": member_rows,
        "total_members": all_members.count(),
        "active_members": all_members.filter(is_active=True).count(),
        "total_points_redeemed": 0,
        "avg_points": int(all_members.aggregate(avg=Avg("loyalty_points"))["avg"] or 0),
        "query": query,
        "tier": tier,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
    }
    return render(request, 'lumra_pages/marketing/loyalty_members.html', context)


@login_required
def loyalty_member_form(request, pk=None):
    """Create/Edit Loyalty Member."""
    context = {"member": get_object_or_404(Customer, pk=pk) if pk else None}
    return render(request, 'lumra_pages/marketing/loyalty_members.html', context)


# ===== CUSTOMER SEGMENTATION =====

@login_required
def customer_segment_list(request):
    """List all Customer Segments."""
    segments = [
        {"name": label, "code": value, "customer_count": Customer.objects.filter(customer_type=value).count()}
        for value, label in Customer.CUSTOMER_TYPE_CHOICES
    ]
    context = {"segments": segments, "total_segments": len(segments)}
    return render(request, 'lumra_pages/marketing/customer_segment_list.html', context)


@login_required
def customer_segment_form(request, pk=None):
    """Create/Edit Customer Segment."""
    context = {"customer_types": Customer.CUSTOMER_TYPE_CHOICES}
    return render(request, 'lumra_pages/marketing/customer_segment_form.html', context)


# ===== PROMOTION CALENDAR =====

@login_required
def promotion_calendar(request):
    """View Promotion Calendar."""
    context = _empty_promotions_context()
    return render(request, 'lumra_pages/marketing/promotion_calendar.html', context)
