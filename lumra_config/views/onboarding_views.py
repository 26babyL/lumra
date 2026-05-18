# lumra_config/views/onboarding_views.py
# Onboarding Module Views - Stubs untuk rendering template

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .helpers import create_empty_context


# ===== ONBOARDING FLOW =====

@login_required
def onboarding_welcome(request):
    """Onboarding step: Welcome screen."""
    context = {}
    return render(request, 'lumra_pages/onboarding/welcome.html', context)


@login_required
def onboarding_step_business(request):
    """Onboarding step: Business Information."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_business.html', context)


@login_required
def onboarding_step_location(request):
    """Onboarding step: Location/Warehouse setup."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_location.html', context)


@login_required
def onboarding_step_category(request):
    """Onboarding step: Product Categories."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_category.html', context)


@login_required
def onboarding_step_complete(request):
    """Onboarding step: Completion/Success screen."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_complete.html', context)


@login_required
@require_POST
def onboarding_save_step(request, step):
    """AJAX endpoint to save onboarding step data."""
    return JsonResponse({'status': 'ok', 'message': 'Step saved'})
