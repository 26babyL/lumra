# lumra_config/views/master_data_extended_views.py
# Master Data Extended Views - Stubs untuk rendering template yang belum tercakup

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse

from .helpers import check_queryset_empty, create_empty_context
from lumra_config.models import Tax


def _simple_master_context(title, description, rows=None, columns=None, add_url_name=None):
    return {
        "page_title": title,
        "page_description": description,
        "breadcrumb": [
            {"label": "Master Data", "url": "#"},
            {"label": title, "url": ""},
        ],
        "columns": columns or [],
        "items": rows or [],
        "add_button_url": reverse(add_url_name) if add_url_name else "",
    }


# ===== BANK ACCOUNTS =====

@login_required
def bank_accounts(request):
    """List all bank accounts."""
    context = _simple_master_context(
        "Bank Accounts",
        "Data rekening bank belum memiliki model database khusus.",
    )
    return render(request, 'lumra_pages/master_data/bank_accounts.html', context)


@login_required
def bank_account_form(request, pk=None):
    """Create/Edit bank account."""
    context = _simple_master_context("Bank Account Form", "Form rekening bank.")
    return render(request, 'lumra_pages/master_data/bank_account_form.html', context)


# ===== PAYMENT TERMS =====

@login_required
def payment_terms_list(request):
    """List all payment terms."""
    context = _simple_master_context(
        "Payment Terms",
        "Data termin pembayaran belum memiliki model database khusus.",
    )
    return render(request, 'lumra_pages/master_data/payment_terms_list.html', context)


@login_required
def payment_terms_form(request, pk=None):
    """Create/Edit payment terms."""
    context = _simple_master_context("Payment Terms Form", "Form termin pembayaran.")
    return render(request, 'lumra_pages/master_data/payment_terms_form.html', context)


# ===== TAX =====

@login_required
def tax_list(request):
    """List all tax rates."""
    taxes = Tax.objects.order_by("name")
    rows = [
        {
            "name": tax.name,
            "rate": tax.rate,
            "description": tax.description,
            "is_active": tax.is_active,
            "edit_url": reverse("tax_edit", args=[tax.pk]),
        }
        for tax in taxes
    ]
    context = _simple_master_context(
        "Taxes",
        "Tarif pajak dari database.",
        rows=rows,
        columns=[
            {"key": "name", "label": "Name"},
            {"key": "rate", "label": "Rate"},
            {"key": "description", "label": "Description"},
            {"key": "is_active", "label": "Active"},
        ],
        add_url_name="tax_form",
    )
    return render(request, 'lumra_pages/master_data/tax_list.html', context)


@login_required
def tax_form(request, pk=None):
    """Create/Edit tax rate."""
    context = {
        "page_title": "Tax Form",
        "tax": get_object_or_404(Tax, pk=pk) if pk else None,
    }
    return render(request, 'lumra_pages/master_data/tax_form.html', context)


# ===== REASON CODES =====

@login_required
def reason_codes(request):
    """List all reason codes."""
    context = _simple_master_context("Reason Codes", "Data reason code belum memiliki model database khusus.")
    return render(request, 'lumra_pages/master_data/reason_codes.html', context)


# ===== TAGS =====

@login_required
def tags_list(request):
    """List all tags."""
    context = _simple_master_context("Tags", "Data tag belum memiliki model database khusus.")
    return render(request, 'lumra_pages/master_data/tags_list.html', context)


# ===== LOCATIONS =====

@login_required
def locations(request):
    """List all warehouse locations."""
    context = {}
    return render(request, 'lumra_pages/master_data/locations.html', context)


@login_required
def location_list(request):
    """Alternative endpoint for locations."""
    context = {}
    return render(request, 'lumra_pages/master_data/location_list.html', context)


# ===== CUSTOMERS (Master Data) =====

@login_required
def customers(request):
    """List all customers."""
    context = {}
    return render(request, 'lumra_pages/master_data/customers.html', context)


@login_required
def customers_list(request):
    """Alternative endpoint for customers list."""
    context = {}
    return render(request, 'lumra_pages/master_data/customers_list.html', context)


@login_required
def customer(request, pk=None):
    """Alternative endpoint for customer."""
    context = {}
    return render(request, 'lumra_pages/master_data/customer.html', context)


@login_required
def customer_detail(request, pk):
    """View customer detail."""
    context = {}
    return render(request, 'lumra_pages/master_data/customer_detail.html', context)


@login_required
def customer_form(request, pk=None):
    """Create/Edit customer."""
    context = {}
    return render(request, 'lumra_pages/master_data/customer_form.html', context)


# ===== STOCK OPNAME (Master Data) =====

@login_required
def stock_opname(request):
    """Stock opname management."""
    context = {}
    return render(request, 'lumra_pages/master_data/stock_opname.html', context)


@login_required
def stock_opname_session_detail(request, pk):
    """View stock opname session detail."""
    context = {}
    return render(request, 'lumra_pages/master_data/stock_opname_session_detail.html', context)
