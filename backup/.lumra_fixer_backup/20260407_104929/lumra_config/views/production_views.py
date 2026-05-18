# lumra_config/views/production_views.py
# Auto-generated oleh lumra_sync.py dari core/views/production_views.py
# JANGAN EDIT MANUAL — edit core/views/production_views.py lalu jalankan lumra_sync.py lagi

import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timezone import localtime

from lumra_config.models import Recipe, RecipeCategory, Unit
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
            "created_at":        localtime(r.created_at).strftime("%Y-%m-%d %H:%M"),
        })
    return result


# =====================================================
# RECIPE LIST
# =====================================================

@login_required
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
    recipes_json = json.dumps(_serialize_recipes(recipes))

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

@login_required
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

    context = {
        "form": form,
        "formset": formset,
        "is_edit": is_edit,
        "recipe": recipe,
        "categories": categories,
        "units": units,
        "report_title": "Edit Recipe" if is_edit else "Add Recipe",
    }

    return render(
        request,
        "lumra_pages/production/recipe_form.html",
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
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = recipe.ingredients.select_related("variant", "unit")

    context = {
        "recipe": recipe,
        "ingredients": ingredients,
        "report_title": f"Recipe Detail - {recipe.name}",
    }

    return render(
        request,
        "lumra_pages/production/recipe_detail.html",
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
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
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