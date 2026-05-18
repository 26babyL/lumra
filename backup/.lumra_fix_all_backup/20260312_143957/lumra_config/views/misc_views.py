# lumra_config/views/misc_views.py
# Auto-generated oleh lumra_sync.py dari core/views/misc_views.py
# JANGAN EDIT MANUAL — edit core/views/misc_views.py lalu jalankan lumra_sync.py lagi

# Miscellaneous views yang tidak fit dalam kategori khusus

import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, DecimalField, F, Q, Sum
from django.db.models.functions import TruncDate
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from lumra_config.models import (
    Location,
    Order,
    OrderItem,
    Product,
    ProductVariant,
    UserProfile,
)
from .helpers import check_queryset_empty, create_empty_context


# ------------------------------------------------------------------
# Role‑based access support
#
# The RBAC engine is defined in the frontend (`user_roles_permissions.html`)
# and includes a big default matrix of permissions keyed by role names.  In
# order for the various business‑settings templates to behave correctly they
# need to know which permissions the *current* user has.  We reproduce a
# small subset of the JS defaults here and expose them via the view context
# so the templates can render accordingly (show/hide buttons, display an
# "access denied" message, etc.).  This keeps the Python and JS sides in
# sync and avoids sprinkling hard‑coded role checks through the markup.

DEFAULT_ROLE_PERMS = {
    'superadmin': {
        # full‑access shortcut; every key is True
        # in practice the frontend computes this with ``_allTrue()`` but
        # replicating the full dictionary is easiest for testing.
        **{k: True for k in [
            # small sample, the template will ignore extras
            'sys_config', 'sys_status', 'sys_logs', 'sys_backup',
            'sku_view', 'pos_access', 'sales_view',
        ]},
    },
    'admin': {
        'sys_config': False,  # admins are not automatically granted shop
                             # configuration rights in the default matrix
        'sys_status': True,
        'sys_logs': True,
        'sys_backup': False,
        'sku_view': True,
        'pos_access': True,
        'sales_view': True,
    },
    'manager': {
        'sys_config': False,
        'sys_status': False,
        'sys_logs': False,
        'sys_backup': False,
        'sku_view': True,
        'pos_access': True,
        'sales_view': True,
    },
    'staff': {
        'sys_config': False,
        'sys_status': False,
        'sys_logs': False,
        'sys_backup': False,
        'sku_view': True,
        'pos_access': True,
        'sales_view': False,
    },
    'viewer': {
        'sys_config': False,
        'sys_status': False,
        'sys_logs': False,
        'sys_backup': False,
        'sku_view': True,
        'pos_access': False,
        'sales_view': True,
    },
}


def get_user_permissions(user):
    """Return a permissions dict for the given user.

    The returned object mirrors the shape that the frontend expects for
    ``perms-data``.  Currently we only care about a handful of keys –
    ``sys_config`` is the one used by the business‑settings pages – but we
    keep the printed dictionary small so the JSON payload is light.
    """
    role = getattr(getattr(user, 'profile', None), 'role', '') or ''
    role_key = role.lower()
    return DEFAULT_ROLE_PERMS.get(role_key, DEFAULT_ROLE_PERMS['viewer'])



# =====================================================
# SALES & POS VIEWS
# =====================================================

@login_required
def pos_view(request):
    """Point of Sale (POS) untuk transaksi penjualan.

    The template expects `products` to be a JSON string (consumed via
    `json_script`) rather than a raw queryset.  Previously we were
    passing a queryset directly which triggered the
    ``Object of type QuerySet is not JSON serializable`` error.

    We also supply a ``categories`` value so the tab bar loop in the
    template has something to iterate over.
    """

    # queryset of variants with related product and category for later
    # serialization; ordering mimics original behaviour
    variants = (
        ProductVariant.objects
        .select_related("product__category")
        .order_by("sku")
    )

    # convert to plain Python objects suitable for json.dumps()
    products_data = []
    for v in variants:
        prod = v.product
        products_data.append({
            "id": v.id,
            "name": prod.name,
            "sku": v.sku,
            "price": float(v.price_sell),
            "stock": int(v.total_stock),
            "image_url": prod.image.url if getattr(prod, "image", None) else "",
            "category_id": str(prod.category_id) if prod.category_id else "",
            "category": prod.category.name if prod.category else "",
        })

    products_json = json.dumps(products_data)

    # categories for the tabs; use Category model so IDs are available
    from lumra_config.models import Category
    categories = Category.objects.filter(is_active=True).order_by("name")

    # minimal extras so template can always call json_script safely
    context = {
        "products": products_json,
        "categories": categories,
        "discount_presets": json.dumps([]),   # will be replaced with real data later
        "payment_methods": json.dumps([]),
        "held_orders": json.dumps([]),
        "tax_rate": 0,
    }
    return render(request, "lumra_pages/sales/pos.html", context)


# ------------------------------------------------------------------
# SALES / POS API
# ------------------------------------------------------------------

# we import json here with alias to avoid shadowing earlier 'json'
import json as _json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # template uses fetch with csrftoken header


@login_required
@csrf_exempt
def pos_create_order(request):
    """Endpoint called by the POS front end (``confirmPayment()``).

    This stub mirrors the example from the user’s description; it
    simply validates the request payload and returns a success flag
    until you wire it up to your actual Order/OrderItem models.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = _json.loads(request.body)
    except _json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    # TODO: implement order creation logic (see earlier comment in
    # conversation for a reference snippet)

    # placeholder response
    return JsonResponse({"success": True, "order_id": 0})


@login_required
def purchasing_view(request):
    """Halaman untuk manajemen pembelian."""
    # FIX: annotate langsung, tidak perlu loop manual set _cached_total_stock
    products = (
        ProductVariant.objects
        .select_related("product")
        .annotate(total_stock=Sum("stock_entries__quantity"))
        .order_by("sku")
    )

    # Check if products/variants is empty
    if not products.exists():
        return render(
            request,
            "lumra_pages/sales/purchasing.html",
            create_empty_context("Purchasing", "Data varian produk tidak ditemukan. Silahkan tambah produk terlebih dahulu.")
        )

    paginator = Paginator(products, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))

    # prepare simple JSON list of locations for the Alpine component
    locations = list(Location.objects.order_by("name").values("id","name"))

    context = {
        "page_obj":          page_obj,
        "locations":         Location.objects.order_by("name"),
        "locations_json":    json.dumps(locations),
        "requisition_count": 0,
        "is_empty": False,
    }
    return render(request, "lumra_pages/sales/purchasing.html", context)


@login_required
def sales_history_view(request):
    """Menampilkan riwayat penjualan."""
    context = {"sales": []}
    return render(request, "lumra_pages/reports/sales_history.html", context)


# FIX: tambah @login_required yang sebelumnya hilang
@login_required
def sales_history_products_view(request):
    """Sales history per produk dengan detail — N+1 diperbaiki."""

    products = Product.objects.select_related("category").all()

    # Check if products is empty
    if not products.exists():
        return render(
            request,
            "lumra_pages/reports/sales_history_product.html",
            create_empty_context("Sales History - Products", "Data produk tidak ditemukan.")
        )

    thirty_days_ago = timezone.now() - timedelta(days=30)

    # FIX: ganti loop + per-product query → 2 bulk query
    # Query 1: total units & revenue per product (all-time)
    totals_by_product = {
        row["variant__product_id"]: row
        for row in OrderItem.objects.values("variant__product_id").annotate(
            units_sold=Sum("quantity"),
            revenue=Sum(F("quantity") * F("price"), output_field=DecimalField()),
        )
    }

    # Query 2: daily sales per product (30 hari terakhir)
    recent_qs = (
        OrderItem.objects
        .filter(order__created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate("order__created_at"))
        .values("variant__product_id", "date")
        .annotate(
            units=Sum("quantity"),
            revenue=Sum(F("quantity") * F("price"), output_field=DecimalField()),
        )
        .order_by("variant__product_id", "-date")
    )

    # Group recent sales by product id
    recent_by_product: dict[int, list] = {}
    for row in recent_qs:
        pid = row["variant__product_id"]
        recent_by_product.setdefault(pid, []).append({
            "date":    str(row["date"]),
            "units":   row["units"],
            "revenue": float(row["revenue"] or 0),
        })

    product_sales = []
    for product in products:
        totals = totals_by_product.get(product.id, {})
        product_sales.append({
            "id":           product.id,
            "name":         product.name,
            "description":  product.description,
            "category":     product.category.name if product.category else None,
            "unitsSold":    totals.get("units_sold") or 0,
            "revenue":      float(totals.get("revenue") or 0),
            "salesHistory": recent_by_product.get(product.id, []),
        })

    context = {
        "products": json.dumps(product_sales, default=str),
        "is_empty": False,
    }
    return render(request, "lumra_pages/reports/sales_history_product.html", context)


@login_required
def sales_performance_view(request):
    """Menampilkan performa penjualan."""
    context = {"performance_data": {}}
    return render(request, "lumra_pages/reports/sales_performance.html", context)


# =====================================================
# CUSTOMER MANAGEMENT
# =====================================================

@login_required
def customers_view(request):
    context = {"customers": []}
    return render(request, "lumra_pages/customers.html", context)


@login_required
def add_customer_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/customers.html", context)


@login_required
def view_customer_view(request, customer_id):
    context = {"customer_id": customer_id}
    return render(request, "lumra_pages/customers.html", context)


@login_required
def edit_customer_view(request, customer_id):
    context = {"customer_id": customer_id, "action": "edit"}
    return render(request, "lumra_pages/customers.html", context)


@login_required
def delete_customer_view(request, customer_id):
    # FIX: stub views untuk destructive actions sebaiknya POST-only
    if request.method != "POST":
        return render(request, "lumra_pages/customers.html", {"customer_id": customer_id})
    # TODO: implement actual delete logic
    messages.warning(request, "Delete customer belum diimplementasi.")
    return redirect("customers")


# =====================================================
# CAMPAIGN MANAGEMENT
# =====================================================

@login_required
def campaign_list_view(request):
    context = {
        "total_campaigns":     0,
        "active_campaigns":    0,
        "completed_campaigns": 0,
        "campaigns":           [],
    }
    return render(request, "lumra_pages/campaign.html", context)


@login_required
def add_campaign_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/campaign.html", context)


@login_required
def edit_campaign_view(request, campaign_id):
    context = {"campaign_id": campaign_id, "action": "edit"}
    return render(request, "lumra_pages/campaign.html", context)


@login_required
def delete_campaign_view(request, campaign_id):
    if request.method != "POST":
        return render(request, "lumra_pages/campaign.html", {"campaign_id": campaign_id})
    messages.warning(request, "Delete campaign belum diimplementasi.")
    return redirect("campaign_list")


# =====================================================
# DISCOUNT MANAGEMENT
# =====================================================

@login_required
def discount_list_view(request):
    context = {
        "total_discounts":  0,
        "active_discounts": 0,
        "discounts":        [],
    }
    return render(request, "lumra_pages/discount.html", context)


@login_required
def add_discount_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/discount.html", context)


@login_required
def edit_discount_view(request, discount_id):
    context = {"discount_id": discount_id, "action": "edit"}
    return render(request, "lumra_pages/discount.html", context)


@login_required
def delete_discount_view(request, discount_id):
    if request.method != "POST":
        return render(request, "lumra_pages/discount.html", {"discount_id": discount_id})
    messages.warning(request, "Delete discount belum diimplementasi.")
    return redirect("discount_list")


# =====================================================
# LOYALTY PROGRAM MANAGEMENT
# =====================================================

@login_required
def loyalty_members_view(request):
    context = {
        "total_members":  0,
        "active_members": 0,
        "members":        [],
    }
    return render(request, "lumra_pages/loyalty_members.html", context)


@login_required
def add_loyalty_member_view(request):
    context = {"action": "add"}
    return render(request, "lumra_pages/loyalty_members.html", context)


@login_required
def edit_loyalty_member_view(request, member_id):
    context = {"member_id": member_id, "action": "edit"}
    return render(request, "lumra_pages/loyalty_members.html", context)


@login_required
def delete_loyalty_member_view(request, member_id):
    if request.method != "POST":
        return render(request, "lumra_pages/loyalty_members.html", {"member_id": member_id})
    messages.warning(request, "Delete loyalty member belum diimplementasi.")
    return redirect("loyalty_members")


# =====================================================
# INSIGHTS & ANALYTICS
# =====================================================

@login_required
def financial_reports_view(request):
    context = {"reports": {}}
    return render(request, "lumra_pages/reports/financial_reports.html", context)


@login_required
def market_insights_view(request):
    context = {"insights": {}}
    return render(request, "lumra_pages/market_insights.html", context)


@login_required
def trends_analysis_view(request):
    context = {"trends": {}}
    return render(request, "lumra_pages/trends_analysis.html", context)


@login_required
def activity_log_view(request):
    context = {"activities": []}
    return render(request, "lumra_pages/activity_log.html", context)


# =====================================================
# SYSTEM & SETTINGS
# =====================================================

@login_required
def users_view(request):
    """Manajemen pengguna — staff/admin only."""
    # FIX: gunakan redirect ke 403 page, bukan render langsung (status code tetap 200 di versi lama)
    if not request.user.is_staff:
        return render(request, "lumra_pages/error_403.html", status=403)

    # FIX: pindahkan import ke atas file — import di dalam fungsi hanya untuk menghindari circular import
    users = User.objects.select_related("userprofile").order_by("username")
    context = {"users": users}
    return render(request, "lumra_pages/users.html", context)


@login_required
def profile_view(request):
    """User profile page."""
    # FIX: get_or_create untuk menghindari RelatedObjectDoesNotExist jika profile belum ada
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    context = {"user_profile": profile}
    return render(request, "lumra_pages/profile.html", context)


@login_required
def settings_view(request):
    return render(request, "lumra_pages/settings/settings.html")


@login_required
def system_status_view(request):
    context = {"status": {}}
    return render(request, "lumra_pages/settings/system_status.html", context)


@login_required
def business_settings_view(request):
    # the template expects several JSON blobs for Alpine;
    # provide empty defaults so the page still loads even if no data yet
    context = {
        "settings": {},
        "settings_json": "{}",
        "audit_json": "{}",
        "outlets_json": "[]",
    }

    # attach permissions so the template and its JS know whether the
    # current user is allowed to access / modify anything on this page.
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)

    return render(request, "lumra_pages/settings/business_settings.html", context)


# ---  Business sub‑pages -------------------------------------------------

@login_required
def business_feature_matrix_view(request):
    """Blank endpoint for the feature‑matrix page.

    The ability to view or edit the feature matrix is controlled by the same
    ``sys_config`` permission used by the main settings screen.  Passing the
    permissions object into the template allows the frontend to make
    decisions such as disabling the save button or hiding the upgrade banner
    entirely for unauthorized users.
    """
    context = {"features_json": "[]"}
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)
    return render(request, "lumra_pages/settings/business_feature_matrix.html", context)


@login_required
def business_form_general_view(request):
    """Company profile form page.

    Access restricted by ``sys_config`` permission; unauthorized users will
    see a simple notice instead of the editable form.  We still send a
    minimal JSON payload so the Alpine component is safe to initialize.
    """
    context = {"profile_json": "{}"}
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)
    return render(request, "lumra_pages/settings/business_form_general.html", context)


@login_required
def user_roles_permissions_view(request):
    """Simple placeholder for roles & permissions screen."""
    context = {"roles_json": "[]", "perms_json": "[]"}
    return render(request, "lumra_pages/user_roles_permissions.html", context)

# =====================================================
# EXPORT & DOWNLOAD
# =====================================================

VALID_REPORT_TYPES = {"sales", "inventory", "financial", "movement"}
VALID_TREND_TYPES  = {"weekly", "monthly", "quarterly", "yearly"}


@login_required
def download_report_view(request, report_type):
    # FIX: validasi report_type — sebelumnya semua string diterima dan dirender begitu saja
    if report_type not in VALID_REPORT_TYPES:
        raise Http404(f"Report type '{report_type}' tidak dikenal.")
    context = {"report_type": report_type}
    return render(request, "lumra_pages/market_insights.html", context)


@login_required
def export_trends_view(request, trend_type):
    # FIX: validasi trend_type
    if trend_type not in VALID_TREND_TYPES:
        raise Http404(f"Trend type '{trend_type}' tidak dikenal.")
    context = {"trend_type": trend_type}
    return render(request, "lumra_pages/trends_analysis.html", context)


# =====================================================
# PUBLIC PAGES
# =====================================================

def about_view(request):
    context = {
        "founded_year": 2024,
        "clients_count": 100,
    }
    return render(request, "lumra_pages/about.html", context)


def contact_view(request):
    return render(request, "lumra_pages/contact.html", {})


def search_view(request):
    query = request.GET.get("q", "").strip()
    context = {"query": query}
    return render(request, "lumra_pages/search.html", context)