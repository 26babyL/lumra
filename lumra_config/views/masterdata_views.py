# lumra_config/views/masterdata_views.py
# Auto-generated oleh lumra_sync.py dari core/views/masterdata_views.py
# JANGAN EDIT MANUAL — edit core/views/masterdata_views.py lalu jalankan lumra_sync.py lagi

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from lumra_config.models import Category, Unit, Vendor
from lumra_config.forms import CategoryForm, UnitForm, VendorForm
from .helpers import check_queryset_empty, create_empty_context


# ------------------------------------------------------------------
# HELPER
# ------------------------------------------------------------------

def _wants_json(request) -> bool:
    """True if the client expects a JSON response (AJAX/Alpine.js delete)."""
    return (
        request.headers.get("Accept") == "application/json"
        or request.POST.get("_ajax") == "1"
    )


# ------------------------------------------------------------------
# CATEGORY CRUD
# ------------------------------------------------------------------

@login_required
def categories_list(request):
    q = request.GET.get("q", "").strip()
    qs = Category.objects.order_by("name")

    if q:
        qs = qs.filter(name__icontains=q)

    # Check if categories is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/categories_list.html",
            create_empty_context("Categories", "Data kategori tidak ditemukan. Silahkan tambah kategori terlebih dahulu.")
        )

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "categories":  page_obj.object_list,
        "page_obj":    page_obj,
        "query":       q,
        "report_title": "Categories",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/categories_list.html", context)


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Category '{model_instance.name}' created successfully.")
            return redirect("categories_list")
    else:
        form = CategoryForm()

    return render(
        request,
        "lumra_pages/master_data/category_form.html",
        {"form": form, "is_edit": False, "report_title": "Add Category"},
    )


@login_required
def category_update(request, pk):
    model_instance = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=model_instance)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Category '{model_instance.name}' updated successfully.")
            return redirect("categories_list")
    else:
        form = CategoryForm(instance=model_instance)

    return render(
        request,
        "lumra_pages/master_data/category_form.html",
        {"form": form, "is_edit": True, "report_title": "Edit Category"},
    )


@login_required
@require_POST
# TODO[C3-LONG]: 'category_delete' = 32 baris (maks 30). Pecah: category_delete_validate(), category_delete_process(), category_delete_respond()
def category_delete(request, pk):
    model_instance = get_object_or_404(Category, pk=pk)

    # Count related objects that will be affected (SET_NULL in model)
    affected_products = model_instance.product_set.count()
    affected_recipes  = model_instance.recipes.count() if hasattr(model_instance, "recipes") else 0

    name = model_instance.name
    model_instance.delete()

    if _wants_json(request):
        return JsonResponse({
            "success": True,
            "message": f"Category '{name}' deleted.",
            "affected": {
                "products": affected_products,
                "recipes":  affected_recipes,
            },
        })

    messages.success(
        request,
        f"Category '{name}' deleted."
        + (f" {affected_products} product(s) now have no category." if affected_products else ""),
    )
    return redirect("categories_list")


# ------------------------------------------------------------------
# UNIT CRUD
# ------------------------------------------------------------------

@login_required
# TODO[C3-LONG]: 'units_list' terlalu panjang (32 baris). Pecah: units_list_validate(), units_list_build_context(), units_list_render()
# TODO[C3-LONG]: 'units_list' = 37 baris (maks 30). Pecah: units_list_validate(), units_list_process(), units_list_respond()
def units_list(request):
    q = request.GET.get("q", "").strip()
    qs = Unit.objects.order_by("name")

    if q:
        # FIX: was Q(short_name__icontains=q) — field renamed to 'symbol' in refactored model
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(symbol__icontains=q)
        )

    # Check if units is empty
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/units_list.html",
            create_empty_context("Units", "Data satuan tidak ditemukan. Silahkan tambah satuan terlebih dahulu.")
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        )
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "units":        page_obj.object_list,
        "page_obj":     page_obj,
        "query":        q,
        "report_title": "Units",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/units_list.html", context)


@login_required
def unit_create(request):
    if request.method == "POST":
        form = UnitForm(request.POST)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Unit '{model_instance.name}' created successfully.")
            return redirect("units_list")
    else:
        form = UnitForm()

    return render(
        request,
        "lumra_pages/master_data/unit_form.html",
        {"form": form, "is_edit": False, "report_title": "Add Unit"},
    )


@login_required
def unit_update(request, pk):
    model_instance = get_object_or_404(Unit, pk=pk)

    if request.method == "POST":
        form = UnitForm(request.POST, instance=model_instance)
        if form.is_valid():
            model_instance = form.save()
            messages.success(request, f"Unit '{model_instance.name}' updated successfully.")
            return redirect("units_list")
    else:
        form = UnitForm(instance=model_instance)

    return render(
        request,
        "lumra_pages/master_data/unit_form.html",
        {"form": form, "is_edit": True, "report_title": "Edit Unit"},
    )


@login_required
@require_POST
# TODO[C3-LONG]: 'unit_delete' = 36 baris (maks 30). Pecah: unit_delete_validate(), unit_delete_process(), unit_delete_respond()
def unit_delete(request, pk):
    model_instance = get_object_or_404(Unit, pk=pk)

    # Units may be referenced by Products, Recipes, RecipeIngredients
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    affected_products    = model_instance.product_set.count()
    affected_ingredients = model_instance.recipeingredient_set.count() if hasattr(model_instance, "recipeingredient_set") else 0
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah

    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    name = model_instance.name
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    model_instance.delete()

    if _wants_json(request):
        return JsonResponse({
            "success": True,
            "message": f"Unit '{name}' deleted.",
            "affected": {
                "products":    affected_products,
                "ingredients": affected_ingredients,
            },
        })

    messages.success(request, f"Unit '{name}' deleted.")
    return redirect("units_list")


# TODO[C3-LONG]: 'vendors_list' terlalu panjang (32 baris). Pecah: vendors_list_validate(), vendors_list_build_context(), vendors_list_render()
# ------------------------------------------------------------------
# VENDOR CRUD
# ------------------------------------------------------------------

@login_required
# TODO[C3-LONG]: 'vendors_list' = 40 baris (maks 30). Pecah: vendors_list_validate(), vendors_list_process(), vendors_list_respond()
def vendors_list(request):
    q = request.GET.get("q", "").strip()
    qs = Vendor.objects.order_by("name")

    if q:
        # FIX: was Q(contact_name__icontains=q) — field is 'contact_person' in model
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(contact_person__icontains=q)
        )

    # Check if vendors is empty
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    if not qs.exists():
        return render(
            request,
            "lumra_pages/master_data/vendors_list.html",
            create_empty_context("Vendors", "Data vendor tidak ditemukan. Silahkan tambah vendor terlebih dahulu.")
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        )
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get("page"))

    context = {
        "vendors":      page_obj.object_list,
        "page_obj":     page_obj,
        "query":        q,
        "report_title": "Vendors",
        "is_empty": False,
    }
    return render(request, "lumra_pages/master_data/vendors_list.html", context)


@login_required
def vendor_create(request):
    if request.method == "POST":
        form = VendorForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Vendor '{obj.name}' created successfully.")
            return redirect("vendors_list")
    else:
        form = VendorForm()

    return render(
        request,
        "lumra_pages/master_data/vendor_form.html",
        {"form": form, "is_edit": False, "report_title": "Add Vendor"},
    )


@login_required
def vendor_update(request, pk):
    model_instance = get_object_or_404(Vendor, pk=pk)

    if request.method == "POST":
        form = VendorForm(request.POST, instance=model_instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Vendor '{obj.name}' updated successfully.")
            return redirect("vendors_list")
    else:
        form = VendorForm(instance=model_instance)

    return render(
        request,
        "lumra_pages/master_data/vendor_form.html",
        {"form": form, "is_edit": True, "report_title": "Edit Vendor"},
    )


@login_required
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
# TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
@require_POST
# TODO[C3-LONG]: 'vendor_delete' = 35 baris (maks 30). Pecah: vendor_delete_validate(), vendor_delete_process(), vendor_delete_respond()
def vendor_delete(request, pk):
    obj = get_object_or_404(Vendor, pk=pk)

    # Vendors may be referenced by Products (SET_NULL) and SupplierPrices (CASCADE)
    affected_products        = obj.product_set.count()
    affected_supplier_prices = obj.supplier_prices.count()
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
 # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
 # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial

    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    name = obj.name
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    obj.delete()

    if _wants_json(request):
        return JsonResponse({
            "success": True,
            "message": f"Vendor '{name}' deleted.",
            "affected": {
                "products":        affected_products,
                "supplier_prices": affected_supplier_prices,
            },
        })

    messages.success(
        request,
        f"Vendor '{name}' deleted."
        + (f" {affected_supplier_prices} supplier price(s) also removed." if affected_supplier_prices else ""),
    )
    return redirect("vendors_list")