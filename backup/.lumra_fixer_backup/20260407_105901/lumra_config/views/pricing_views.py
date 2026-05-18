# lumra_config/views/pricing_views.py
# Auto-generated oleh lumra_sync.py dari core/views/pricing_views.py
# JANGAN EDIT MANUAL — edit core/views/pricing_views.py lalu jalankan lumra_sync.py lagi

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from lumra_config.models import SupplierPrice, Vendor, Product
from lumra_config.forms import SupplierPriceForm
from .helpers import check_queryset_empty, create_empty_context


# =====================================================
# SUPPLIER PRICE LIST
# =====================================================

@login_required
# TODO[C3-LONG]: 'supplier_price_list' = 70 baris (max 30). Pecah: supplier_price_list_validate(), supplier_price_list_query(), supplier_price_list_render()
def supplier_price_list(request):
    """
    Menampilkan daftar harga supplier dengan filter vendor dan produk.
    """

    vendor_filter = request.GET.get("vendor")
    product_filter = request.GET.get("product")
    query = request.GET.get("q", "")

    prices = SupplierPrice.objects.select_related(
        "vendor",
        "variant",
        "variant__product"
    ).filter(is_active=True)

    # Filter vendor
    if vendor_filter:
        prices = prices.filter(vendor_id=vendor_filter)

    # Filter product
    if product_filter:
        prices = prices.filter(variant__product_id=product_filter)

    # Search query
    if query:
        prices = prices.filter(
            Q(vendor__name__icontains=query) |
            Q(variant__sku__icontains=query) |
            Q(variant__product__name__icontains=query)
        )

    prices = prices.order_by("-is_preferred", "unit_price")

    # Check if prices is empty
    if not prices.exists():
        vendors = Vendor.objects.filter(is_active=True).order_by("name")
        products = Product.objects.order_by("name")
        context = create_empty_context("Supplier Pricing", "Data harga supplier tidak ditemukan.")
        context.update({
            "vendors": vendors,
            "products": products,
            "vendor_filter": vendor_filter,
            "product_filter": product_filter,
            "query": query,
        })
        return render(request, "lumra_pages/inventory/supplier_price_list.html", context)

    paginator = Paginator(prices, 30)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    vendors = Vendor.objects.filter(is_active=True).order_by("name")
    products = Product.objects.order_by("name")

    context = {
        "prices": page_obj,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        "vendors": vendors,
        "products": products,
        "vendor_filter": vendor_filter,
        "product_filter": product_filter,
        "query": query,
        "total_prices": SupplierPrice.objects.filter(is_active=True).count(),
        "report_title": "Supplier Pricing",
        "is_empty": False,
    }

    return render(
        request,
        "lumra_pages/inventory/supplier_price_list.html",
        context
    )


# =====================================================
# SUPPLIER PRICE FORM (CREATE / EDIT)
# =====================================================
 # TODO[C3-LONG]: 'supplier_price_form' = 40 baris (max 30). Pecah: supplier_price_form_validate(), supplier_price_form_query(), supplier_price_form_render()

@login_required
def supplier_price_form(request):
    """
    Tambah atau edit supplier pricing.
    """

    price_id = request.GET.get("id")

    if price_id:
        supplier_price = get_object_or_404(SupplierPrice, id=price_id)
        is_edit = True
    else:
        supplier_price = None
        is_edit = False

    if request.method == "POST":
        form = SupplierPriceForm(request.POST, instance=supplier_price)

        if form.is_valid():
            model_instance = form.save(commit=False)
            obj.last_updated_by = request.user
            obj.save()

            messages.success(request, "Supplier price saved successfully!")
            return redirect("supplier_price_list")

    else:
        form = SupplierPriceForm(instance=supplier_price)

    context = {
        "form": form,
        "is_edit": is_edit,
        "supplier_price": supplier_price,
        "report_title": "Edit Supplier Price" if is_edit else "Add Supplier Price",
    }

    return render(
        request,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        "lumra_pages/inventory/supplier_price_form.html",
        context
    )


# =====================================================
# SUPPLIER PRICE DELETE
# =====================================================

@login_required
def supplier_price_delete(request, price_id):
    """
    Delete supplier pricing.
    """

    supplier_price = get_object_or_404(SupplierPrice, id=price_id)

    if request.method == "POST":
        supplier_price.delete()
        messages.success(request, "Supplier price deleted successfully!")
        return redirect("supplier_price_list")

    context = {
        "supplier_price": supplier_price,
        "report_title": "Delete Supplier Price",
    }

    return render(
        request,
        "lumra_pages/inventory/supplier_price_confirm_delete.html",
        context
    )
