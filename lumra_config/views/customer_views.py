# lumra_config/views/customer_views.py
# Auto-generated oleh lumra_sync.py dari core/views/customer_views.py
# JANGAN EDIT MANUAL — edit core/views/customer_views.py lalu jalankan lumra_sync.py lagi

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from lumra_config.models import Customer, OrderItem
from lumra_config.forms import CustomerForm

import csv
from django.utils import timezone


# ---------- helper ------------------------------------------------

def _augment_customer(cust: Customer) -> Customer:
    """Attach dynamically-calculated attributes so templates can rely on them.

    We normalise a couple of fields and push some computed values into the
    instance ``__dict__`` rather than assigning directly to properties (which
    would raise ``AttributeError``).
    """
    # tier normalization
    if cust.tier == 'bronze':
        cust.tier = 'regular'

    # copy a few read-only properties into the instance dict so that the
    # template engine / serialization helpers can see them as attributes.
    for attr in ('whatsapp', 'points', 'lifetime_value', 'last_visit', 'points_expiry', 'iseller_id'):
        if attr not in cust.__dict__:
            try:
                cust.__dict__[attr] = getattr(cust, attr)
            except Exception:
                cust.__dict__[attr] = None
    return cust


def _tier_choices():
    # explicit list used by templates; keeps styling consistent even if model
    # choices lag behind.
    return [
        ('regular', 'Regular'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('vip', 'VIP'),
    ]


# ---------- LIST --------------------------------------------------

@login_required
# TODO[C3-LONG]: 'customer_list' = 70 baris (max 30). Pecah: customer_list_validate(), customer_list_query(), customer_list_render()
# TODO[C3-LONG]: 'customer_list' terlalu panjang (70 baris). Pecah: customer_list_validate(), customer_list_build_context(), customer_list_render()
# TODO[C3-LONG]: 'customer_list' = 74 baris (maks 30). Pecah: customer_list_validate(), customer_list_process(), customer_list_respond()
def customer_list(request):
    q = request.GET.get('search', '').strip()
    tier = request.GET.get('tier')
    sort_by = request.GET.get('sort_by', 'created_at')
    order = request.GET.get('order', 'desc')

    qs = Customer.objects.order_by('-created_at')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    if tier:
        if tier == 'regular':
            qs = qs.exclude(tier__in=['silver', 'gold', 'platinum', 'vip'])
        else:
            qs = qs.filter(tier=tier)

    # sort mapping for a few custom keys
    if sort_by in ('points', 'lifetime_value', 'name', 'last_visit', 'created_at'):
        mapping = {
            'points': 'loyalty_points',
            'lifetime_value': 'total_spent',
            'last_visit': 'last_order_date',
        }
        field = mapping.get(sort_by, sort_by)
        if order == 'desc':
            field = '-' + field
        qs = qs.order_by(field)

    # summary stats used by the KPI cards
    total_customers = qs.count()
    gold_count = qs.filter(tier='gold').count()
    vip_count = qs.filter(tier='vip').count()
    total_points = qs.aggregate(Sum('loyalty_points'))['loyalty_points__sum'] or 0
    birthday_this_month = 0  # model has no birth_date yet

    # handle export (csv only for now)
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'WhatsApp/Phone', 'Tier', 'Points'])
        for c in qs:
            writer.writerow([c.name, c.email, c.phone or '', c.tier, c.loyalty_points])
        return response

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    customers = list(page_obj.object_list)
    for c in customers:
        _augment_customer(c)

    context = {
        'customers': customers,
        'page_obj': page_obj,
        'query': q,
        'report_title': 'Customers',
        'is_empty': False,
        'tier_choices': _tier_choices(),
        'total_customers': total_customers,
        'gold_count': gold_count,
        'vip_count': vip_count,
        'total_points': total_points,
        'birthday_this_month': birthday_this_month,
    }
    return render(request, 'lumra_pages/master_data/customers_list.html', context)


# ---------- DETAIL ------------------------------------------------

@login_required
def customer_detail(request, pk):
    cust = get_object_or_404(Customer, pk=pk)
    _augment_customer(cust)

    # transactions from OrderItem similar to sales_report
    transactions = OrderItem.objects.filter(order__customer=cust).select_related(
        'order', 'variant', 'variant__product'
    )

    total_earned_points = sum(getattr(tx, 'points_earned', 0) or 0 for tx in transactions)

    # no persistent log table yet; return empty list
    point_logs = []

    context = {
        'customer': cust,
        'transactions': transactions,
        'total_earned_points': total_earned_points,
        'point_logs': point_logs,
        'report_title': 'Customer Detail',
        'is_empty': False,
        'tier_choices': _tier_choices(),
    }
    return render(request, 'lumra_pages/master_data/customer_detail.html', context)


# ---------- FORM (create/edit) ------------------------------------

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.phone = form.cleaned_data.get('whatsapp', '')
            c.loyalty_points = form.cleaned_data.get('initial_points') or 0
            c.save()
            messages.success(request, f"Customer '{c.name}' dibuat.")
            return redirect('customer_detail', c.pk)
    else:
        form = CustomerForm()
    return render(request, 'lumra_pages/master_data/customer_form.html', {
        'form': form,
        'tier_choices': _tier_choices(),
    })


@login_required
def customer_update(request, pk):
    c = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=c)
        if form.is_valid():
            c = form.save(commit=False)
            c.phone = form.cleaned_data.get('whatsapp', '')
            c.save()
            messages.success(request, f"Customer '{c.name}' diperbarui.")
            return redirect('customer_detail', c.pk)
    else:
        initial = {'whatsapp': c.phone}
        form = CustomerForm(instance=c, initial=initial)
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    return render(request, 'lumra_pages/master_data/customer_form.html', {
        'form': form,
        'tier_choices': _tier_choices(),
    })


@login_required
@require_POST
def customer_delete(request, pk):
    c = get_object_or_404(Customer, pk=pk)
    name = c.name
    c.delete()
    messages.success(request, f"Customer '{name}' dihapus.")
    return redirect('customer_list')


@login_required
@require_POST
def customer_redeem_points(request, pk):
    c = get_object_or_404(Customer, pk=pk)
    try:
        pts = int(request.POST.get('redeem_points', '0'))
    except ValueError:
        pts = 0
    if pts > 0 and pts <= c.loyalty_points:
        c.loyalty_points -= pts
        c.save()
        messages.success(request, f"{pts} poin berhasil diredeem.")
    else:
        messages.error(request, "Jumlah poin tidak valid atau melebihi saldo.")
    return redirect('customer_detail', c.pk)
