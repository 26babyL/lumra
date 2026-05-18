# lumra_config/views/production_views.py
# Auto-generated oleh lumra_sync.py dari core/views/production_views.py
# JANGAN EDIT MANUAL — edit core/views/production_views.py lalu jalankan lumra_sync.py lagi

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timezone import localtime

from lumra_config.models import ProductVariant, Recipe, RecipeCategory, Unit
from lumra_config.forms import RecipeForm, RecipeIngredientFormSet
from .helpers import check_queryset_empty, create_empty_context


def _serialize_recipes(queryset):
    """
    Serialize a Recipe queryset to a list of plain dicts for use in
    the recipe_list template via `json_script`. This avoids DOM scraping
    in the frontend and keeps data accurate (e.g. category_id for filtering).
    """
    result = []
    for r in queryset:
        result.append({
            "id":                r.id,
            "name":              r.name,
            "category":          r.category.name if r.category else None,
            "category_id":       r.category_id,
            "ingredients_count": r.ingredients.count(),
            "yield_quantity":    float(r.yield_quantity or 0),
            "yield_unit":        r.yield_unit.symbol if r.yield_unit else "",
            "total_cost":        float(r.total_cost or 0),
            "cost_per_unit":     float(r.cost_per_unit or 0),
            "created_at":        localtime(r.created_at).strftime("%Y-%m-%d %H:%M"),
        })
    return result


# =====================================================
# RECIPE LIST
# =====================================================

@login_required
# TODO[C3-LONG]: 'recipe_list' = 66 baris (max 30). Pecah: recipe_list_validate(), recipe_list_query(), recipe_list_render()
# TODO[C3-LONG]: 'recipe_list' terlalu panjang (66 baris). Pecah: recipe_list_validate(), recipe_list_build_context(), recipe_list_render()
# TODO[C3-LONG]: 'recipe_list' = 73 baris (maks 30). Pecah: recipe_list_validate(), recipe_list_process(), recipe_list_respond()
def recipe_list(request):
    """
    Display all non-archived recipes with search + category filter.
    """
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()

    recipes = Recipe.objects.select_related("category").prefetch_related(
        "ingredients"
    ).filter(is_archived=False)

    if query:
        recipes = recipes.filter(name__icontains=query)

    if category_filter:
        recipes = recipes.filter(category_id=category_filter)

    recipes = recipes.order_by("name")

    # Check if recipes is empty
    if not recipes.exists():
        categories = RecipeCategory.objects.all().order_by("name")
        context = create_empty_context("Recipe List", "Data resep tidak ditemukan. Silahkan tambah resep terlebih dahulu.")
        context.update({
            "categories": categories,
            "query": query,
            "category_filter": category_filter,
        })
        return render(request, "lumra_pages/production/recipe_list.html", context)

    paginator = Paginator(recipes, 20)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    categories = RecipeCategory.objects.all().order_by("name")

    # Serialize ALL filtered recipes so the frontend can handle
    # client-side pagination, search and sorting without DOM scraping.
    recipes_json = _serialize_recipes(recipes)

    table_columns = [
        ("id",                "ID"),
        ("name",              "Name"),
        ("category",          "Category"),
        ("ingredients_count", "Ingredients"),
        ("created_at",        "Created At"),
    ]

    context = {
        "recipes": page_obj,
        "recipes_json": recipes_json,
        "table_columns": table_columns,
        "query": query,
        "category_filter": category_filter,
        "categories": categories,
        "total_recipes": Recipe.objects.filter(is_archived=False).count(),
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "report_title": "Recipe List",
        "is_empty": False,
    }

    return render(
        request,
        "lumra_pages/production/recipe_list.html",
        context,
    )


# =====================================================
# RECIPE FORM (CREATE / EDIT)
# =====================================================

# TODO[C3-LONG]: 'recipe_form' = 80 baris (max 30). Pecah: recipe_form_validate(), recipe_form_query(), recipe_form_render()
@login_required
# TODO[C3-LONG]: 'recipe_form' terlalu panjang (81 baris). Pecah: recipe_form_validate(), recipe_form_build_context(), recipe_form_render()
# TODO[C3-LONG]: 'recipe_form' = 89 baris (maks 30). Pecah: recipe_form_validate(), recipe_form_process(), recipe_form_respond()
def recipe_form(request, recipe_id=None):
    """
    Create or edit a recipe + ingredient formset.
    Handles both standard POST and AJAX (JSON response).
    """
    if recipe_id:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_edit = True
    else:
        recipe = None
        is_edit = False

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or \
              request.content_type == "application/x-www-form-urlencoded" and \
              request.GET.get("ajax") == "1"

    # Detect AJAX by checking Accept header or custom flag
    wants_json = (
        request.headers.get("Accept") == "application/json"
        or request.POST.get("_ajax") == "1"
    )

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)

        if form.is_valid() and formset.is_valid():
            recipe_obj = form.save()
            formset.instance = recipe_obj
            formset.save()

            if wants_json:
                return JsonResponse({
                    "success": True,
                    "message": f"Recipe '{recipe_obj.name}' saved successfully!",
                    "recipe_id": recipe_obj.id,
                })

            messages.success(
                request,
                f"Recipe '{recipe_obj.name}' saved successfully!",
            )
            return redirect("recipe_list")

        # Form has errors
        if wants_json:
            errors = {}
            for field, errs in form.errors.items():
                errors[field] = [str(e) for e in errs]
            for i, fs_form in enumerate(formset.forms):
                for field, errs in fs_form.errors.items():
                    errors[f"ingredient_{i}_{field}"] = [str(e) for e in errs]
            return JsonResponse({
                "success": False,
                "errors": errors,
                "message": "Please fix the errors below.",
            }, status=400)

    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)

    categories = RecipeCategory.objects.all().order_by("name")
    units = Unit.objects.all().order_by("symbol")
    variants = ProductVariant.objects.select_related("product").order_by("sku")[:3000]

    context = {
        "form": form,
        "formset": formset,
        "is_edit": is_edit,
        "recipe": recipe,
        "categories": categories,
        "units": units,
        "variants_data": [
            {
                "id": variant.id,
                "sku": variant.sku,
                "name": variant.product.name if variant.product else variant.sku,
                "price_buy": float(variant.price_buy or 0),
            }
            for variant in variants
        ],
        "report_title": "Edit Recipe" if is_edit else "Add Recipe",
    }

    return render(
        request,
        "lumra_pages/production/recipe_form.html",
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        context,
    )


# =====================================================
# RECIPE DETAIL
# =====================================================

@login_required
def recipe_detail(request, recipe_id):
    """
    Show recipe detail + ingredients list.
    """
    recipe = get_object_or_404(
        Recipe.objects.select_related("category", "yield_unit"),
        id=recipe_id,
    )
    ingredients = recipe.ingredients.select_related("variant", "variant__product", "unit")
    recipe_data = {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "category": recipe.category.name if recipe.category else "",
        "yield_quantity": float(recipe.yield_quantity or 0),
        "yield_unit": recipe.yield_unit.symbol if recipe.yield_unit else "",
        "preparation_time": recipe.preparation_time,
        "total_cost": float(recipe.total_cost or 0),
        "cost_per_unit": float(recipe.cost_per_unit or 0),
        "created_at": localtime(recipe.created_at).strftime("%Y-%m-%d %H:%M"),
        "updated_at": localtime(recipe.updated_at).strftime("%Y-%m-%d %H:%M"),
        "ingredients": [
            {
                "id": ingredient.id,
                "sku": ingredient.variant.sku,
                "name": ingredient.variant.product.name if ingredient.variant.product else ingredient.variant.sku,
                "quantity": float(ingredient.quantity or 0),
                "unit": ingredient.unit.symbol if ingredient.unit else "",
                "unit_cost": float(ingredient.unit_cost or 0),
                "subtotal_cost": float(ingredient.subtotal_cost or 0),
                "notes": ingredient.notes,
            }
            for ingredient in ingredients
        ],
    }

    context = {
        "recipe": recipe,
        "ingredients": ingredients,
        "recipe_data": recipe_data,
        "report_title": f"Recipe Detail - {recipe.name}",
    }

    return render(
        request,
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        "lumra_pages/production/recipe_detail.html",
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
        context,
    )


# =====================================================
# RECIPE DELETE
# =====================================================

@login_required
@require_POST
def recipe_delete(request, recipe_id):
    """
    Delete a recipe. Returns JSON for AJAX requests,
    redirects for standard form submissions.
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    wants_json = (
        request.headers.get("Accept") == "application/json"
        or request.POST.get("_ajax") == "1"
    )

    recipe_name = recipe.name
    recipe.delete()

    if wants_json:
        return JsonResponse({
            "success": True,
            "message": f"Recipe '{recipe_name}' deleted successfully!",
        })

    messages.success(request, f"Recipe '{recipe_name}' deleted successfully!")
    return redirect("recipe_list")
