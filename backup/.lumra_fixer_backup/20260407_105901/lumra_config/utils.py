"""
lumra_config/utils.py
=====================
Standar render helper untuk semua views di Lumra ERP.

Masalah yang diselesaikan:
  - render(request, 'lumra_pages/sales/sales_insight.html') tersebar di mana-mana
  - Kalau template dipindah/direname → harus update banyak file views.py
  - Tidak ada satu titik kendali untuk struktur template

Solusi:
  - Semua views pakai render_page() / render_module()
  - Kalau nama/lokasi template berubah → cukup update TEMPLATE_REGISTRY di sini
  - Auto-fallback mencari template di lokasi alternatif sebelum raise error

─────────────────────────────────────────────────────────
CARA PAKAI DI VIEWS:
─────────────────────────────────────────────────────────

  from lumra_config.utils import render_page

  # Cara 1 — pakai alias (direkomendasikan)
  def sales_history_view(request):
      return render_page(request, 'sales_history', context)

  # Cara 2 — pakai modul + nama file (tanpa .html)
  def dashboard_view(request):
      return render_page(request, 'dashboard', context, module='sales')

  # Cara 3 — path eksplisit (fallback manual, hindari kalau bisa)
  def legacy_view(request):
      return render_page(request, 'lumra_pages/sales/dashboard.html', context)

─────────────────────────────────────────────────────────
CARA UPDATE KALAU TEMPLATE DIPINDAH/DIRENAME:
─────────────────────────────────────────────────────────

  Cukup update TEMPLATE_REGISTRY di bawah.
  Tidak perlu menyentuh views.py sama sekali.

  Contoh: sales_insight.html direname jadi sales_intelligence.html
  SEBELUM: 'sales_history' : 'lumra_pages/sales/sales_insight.html',
  SESUDAH: 'sales_history' : 'lumra_pages/sales/sales_intelligence.html',
"""

import logging
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.template.loader import select_template
from django.template import TemplateDoesNotExist
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger('lumra.views')

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE REGISTRY
# Sumber tunggal kebenaran: alias → path template canonical
#
# Format key  : nama pendek yang dipakai di views (bebas, tapi konsisten)
# Format value: path relatif terhadap TEMPLATES dir
#
# Konvensi    : 'lumra_pages/[modul]/[nama_file].html'
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATE_REGISTRY: dict[str, str] = {

    # ── Sales ──────────────────────────────────────────────────────────────
    'dashboard'               : 'lumra_pages/sales/dashboard.html',
    'pos'                     : 'lumra_pages/sales/pos.html',
    'notification'            : 'lumra_pages/sales/notification.html',
    'purchasing'              : 'lumra_pages/sales/purchasing.html',
    'sales_history'           : 'lumra_pages/sales/sales_intelligence.html',
    'sales_intelligence'      : 'lumra_pages/sales/sales_intelligence.html',

    # ── Master Data ────────────────────────────────────────────────────────
    'products'                : 'lumra_pages/inventory/product_list.html',
    'product_list'            : 'lumra_pages/inventory/product_list.html',
    'product_detail'          : 'lumra_pages/inventory/product_details.html',
    'categories'              : 'lumra_pages/master_data/categories_list.html',
    'category_form'           : 'lumra_pages/master_data/category_form.html',
    'units'                   : 'lumra_pages/master_data/units_list.html',
    'unit_form'               : 'lumra_pages/master_data/unit_form.html',
    'vendors'                 : 'lumra_pages/master_data/vendors_list.html',
    'vendor_list'             : 'lumra_pages/master_data/vendor_list.html',
    'vendor_form'             : 'lumra_pages/master_data/vendor_form.html',
    'customers'               : 'lumra_pages/master_data/customers_list.html',
    'customer_list'           : 'lumra_pages/master_data/customers_list.html',
    'customer_detail'         : 'lumra_pages/master_data/customer_detail.html',
    'customer_form'           : 'lumra_pages/master_data/customer_form.html',
    'locations'               : 'lumra_pages/master_data/location_list.html',
    'location_list'           : 'lumra_pages/master_data/location_list.html',
    'stock_opname'            : 'lumra_pages/master_data/stock_opname.html',
    'stock_opname_session'    : 'lumra_pages/master_data/stock_opname_session_detail.html',

    # ── Inventory ──────────────────────────────────────────────────────────
    'inventory'               : 'lumra_pages/inventory/stock_overview.html',
    'stock_overview'          : 'lumra_pages/inventory/stock_overview.html',
    'stock_movement'          : 'lumra_pages/inventory/stock_movement.html',
    'stock_movement_form'     : 'lumra_pages/inventory/stock_movement_form.html',
    'stock_planning'          : 'lumra_pages/inventory/stock_planning.html',
    'stock_opname_locations'  : 'lumra_pages/inventory/stock_opname_locations.html',
    'stock_opname_form'       : 'lumra_pages/inventory/stock_opname_form.html',
    'stock_opname_approvals'  : 'lumra_pages/inventory/stock_opname_approvals.html',
    'stock_opname_approval_detail': 'lumra_pages/inventory/stock_opname_approval_detail.html',
    'supplier_price_list'     : 'lumra_pages/inventory/supplier_price_list.html',
    'supplier_price_form'     : 'lumra_pages/inventory/supplier_price_form.html',
    'supplier_price_delete'   : 'lumra_pages/inventory/supplier_price_confirm_delete.html',

    # ── Marketing ──────────────────────────────────────────────────────────
    'campaign_list'           : 'lumra_pages/marketing/campaign_list.html',
    'campaign_form'           : 'lumra_pages/marketing/add_campaign.html',
    'campaign_detail'         : 'lumra_pages/marketing/campaign.html',
    'discount'                : 'lumra_pages/marketing/discount.html',
    'loyalty_members'         : 'lumra_pages/marketing/loyalty_members.html',

    # ── Reports ────────────────────────────────────────────────────────────
    'reporting'               : 'lumra_pages/reports/reporting.html',
    'financial_reports'       : 'lumra_pages/reports/financial_reports.html',
    'sales_report'            : 'lumra_pages/reports/sales_report.html',
    'sales_performance'       : 'lumra_pages/reports/sales_performance.html',
    'sales_history_report'    : 'lumra_pages/reports/sales_history.html',
    'sales_history_product'   : 'lumra_pages/reports/sales_history_product.html',
    'market_insights'         : 'lumra_pages/reports/market_insights.html',
    'trends_analysis'         : 'lumra_pages/reports/trends_analysis.html',
    'activity_log'            : 'lumra_pages/reports/report_activity_log.html',
    'report_activity_log'     : 'lumra_pages/reports/report_activity_log.html',
    'transaction_summary'     : 'lumra_pages/reports/transaction_summary.html',
    'transfer_report'         : 'lumra_pages/reports/transfer_report.html',
    'requisition_report'      : 'lumra_pages/reports/requisition_report.html',
    'purchasing_report'       : 'lumra_pages/reports/purchasing_report.html',
    'profit_loss'             : 'lumra_pages/reports/report_profit_loss_detail.html',
    'report_inventory_log'    : 'lumra_pages/reports/report_inventory_log.html',
    'report_inventory_low'    : 'lumra_pages/reports/report_inventory_low.html',
    'report_inventory_stock'  : 'lumra_pages/reports/report_inventory_stock.html',
    'report_sales_summary'    : 'lumra_pages/reports/report_sales_summary.html',
    'report_sales_by_outlet'  : 'lumra_pages/reports/report_sales_by_outlet.html',
    'report_sales_by_payment' : 'lumra_pages/reports/report_sales_by_payment.html',
    'report_sales_by_product' : 'lumra_pages/reports/report_sales_by_product.html',

    # ── Production ─────────────────────────────────────────────────────────
    'recipe_list'             : 'lumra_pages/production/recipe_list.html',
    'recipe_form'             : 'lumra_pages/production/recipe_form.html',
    'recipe_detail'           : 'lumra_pages/production/recipe_detail.html',

    # ── Settings ───────────────────────────────────────────────────────────
    'settings'                : 'lumra_pages/settings/settings.html',
    'profile'                 : 'lumra_pages/settings/profile.html',
    'business_settings'       : 'lumra_pages/settings/business_settings.html',
    'business_profile'        : 'lumra_pages/settings/business_profile.html',
    'business_feature_matrix' : 'lumra_pages/settings/business_feature_matrix.html',
    'system_status'           : 'lumra_pages/settings/system_status.html',
    'user_list'               : 'lumra_pages/settings/user_list.html',
    'users'                   : 'lumra_pages/settings/user_list.html',
    'user_roles'              : 'lumra_pages/settings/user_roles_permissions.html',
    'search'                  : 'lumra_pages/settings/search.html',
    'about'                   : 'lumra_pages/settings/about.html',
    'contact'                 : 'lumra_pages/settings/contact.html',

    # ── Auth ───────────────────────────────────────────────────────────────
    'login'                   : 'lumra_pages/auth/login.html',
    'register'                : 'lumra_pages/auth/register.html',

    # ── Error Pages ────────────────────────────────────────────────────────
    'error_403'               : 'lumra_pages/error_403.html',
    'error_404'               : 'base/error_404.html',
    'error_500'               : 'base/error_500.html',
}

# ─────────────────────────────────────────────────────────────────────────────
# FALLBACK CHAINS
# Kalau template tidak ditemukan di path canonical,
# coba lokasi-lokasi alternatif ini secara berurutan.
#
# Berguna masa transisi saat file belum selesai dipindah/direname.
# ─────────────────────────────────────────────────────────────────────────────

# Modul yang dikenal — untuk auto-construct fallback path
_KNOWN_MODULES = [
    'sales', 'master_data', 'inventory', 'marketing',
    'reports', 'production', 'settings', 'auth',
]

# TODO[C3-LONG]: '_build_fallback_chain' = 34 baris (max 30). Pecah: _build_fallback_chain_validate(), _build_fallback_chain_query(), _build_fallback_chain_render()
def _build_fallback_chain(template_name: str, module: str | None = None) -> list[str]:
    """
    Bangun daftar path alternatif yang akan dicoba jika path canonical gagal.

    Urutan prioritas:
    1. Path canonical dari registry (sudah dicoba duluan di render_page)
    2. lumra_pages/[module]/[name].html  (jika module diberikan)
    3. lumra_pages/[module]/[name].html  (coba semua modul yang dikenal)
    4. [name].html saja                  (root templates — legacy)
    """
    # Normalisasi: pastikan punya .html
    if not template_name.endswith('.html'):
        name_html = f'{template_name}.html'
    else:
        name_html = template_name

    basename = name_html.split('/')[-1]  # ambil nama file saja
    chain    = []

    # Kalau module eksplisit diberikan
    if module:
        chain.append(f'lumra_pages/{module}/{basename}')

    # Coba semua modul yang dikenal
    for mod in _KNOWN_MODULES:
        candidate = f'lumra_pages/{mod}/{basename}'
        if candidate not in chain:
            chain.append(candidate)

    # Legacy: tanpa subfolder
    chain.append(f'lumra_pages/{basename}')
    chain.append(basename)

    return chain


# ─────────────────────────────────────────────────────────────────────────────
# CORE: resolve_template()
# ─────────────────────────────────────────────────────────────────────────────
 # TODO[C3-LONG]: 'resolve_template' = 74 baris (max 30). Pecah: resolve_template_validate(), resolve_template_query(), resolve_template_render()

def resolve_template(name: str, module: str | None = None) -> str:
    """
    Resolve nama/alias template menjadi path yang benar.

    Urutan lookup:
    1. TEMPLATE_REGISTRY[name]           → path canonical
    2. Jika name sudah berbentuk path/x.html → pakai langsung
    3. Auto-fallback: coba semua kandidat lewat Django select_template()
    4. Raise TemplateDoesNotExist dengan pesan yang informatif

    Args:
        name   : alias ('sales_history'), path ('lumra_pages/sales/x.html'),
                 atau nama file ('dashboard.html')
        module : hint modul untuk mempercepat fallback ('sales', 'inventory', dll)

    Returns:
        Path template yang valid (string)

    Raises:
        TemplateDoesNotExist jika tidak ditemukan di manapun
    """
    # ── 1. Coba registry ────────────────────────────────────────────────────
    if name in TEMPLATE_REGISTRY:
        canonical = TEMPLATE_REGISTRY[name]
        try:
            select_template([canonical])
            return canonical
        except TemplateDoesNotExist:
            logger.warning(
                'lumra.utils: registry entry "%s" → "%s" tidak ditemukan di disk. '
                'Mencoba fallback...', name, canonical
            )

    # ── 2. Jika sudah berupa path lengkap, coba langsung ────────────────────
    if '/' in name or name.endswith('.html'):
        try:
            select_template([name])
            return name
        except TemplateDoesNotExist:
            pass  # lanjut ke fallback

    # ── 3. Auto-fallback chain ───────────────────────────────────────────────
    #  Normalisasi nama: tanpa ekstensi untuk konstruksi path
    base = name.replace('.html', '')
    if '/' in base:
        # Sudah berupa path — ambil basename-nya
        base = base.split('/')[-1]

    candidates = _build_fallback_chain(f'{base}.html', module)

    for candidate in candidates:
        try:
            select_template([candidate])
            logger.info(
                'lumra.utils: "%s" tidak di registry, ditemukan via fallback: "%s"',
                name, candidate
            )
            return candidate
        except TemplateDoesNotExist:
            continue

    # ── 4. Tidak ditemukan sama sekali ──────────────────────────────────────
    tried = [TEMPLATE_REGISTRY.get(name, name)] + candidates
    raise TemplateDoesNotExist(
        f'\n\n'
        f'  Template tidak ditemukan: "{name}"\n'
        f'  Sudah dicoba:\n' +
        '\n'.join(f'    - {t}' for t in dict.fromkeys(tried)) +
        f'\n\n'
        f'  Solusi:\n'
        f'  1. Pastikan file .html ada di lumra_config/templates/\n'
        f'  2. Daftarkan alias di TEMPLATE_REGISTRY di lumra_config/utils.py\n'
        f'     Contoh: \'{name}\' : \'lumra_pages/[modul]/{base}.html\'\n'
    )


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API — fungsi yang dipakai di views
# TODO[C3-LONG]: 'render_page' = 31 baris (max 30). Pecah: render_page_validate(), render_page_query(), render_page_render()
# ─────────────────────────────────────────────────────────────────────────────

def render_page(
    request  : HttpRequest,
    template : str,
    context  : dict | None = None,
    *,
    module   : str | None = None,
    status   : int = 200,
    **extra_context,
) -> HttpResponse:
    """
    Drop-in replacement untuk render() dengan template resolution otomatis.

    Args:
        request  : HttpRequest dari Django
        template : alias, path lengkap, atau nama file template
        context  : dict context (opsional)
        module   : hint modul untuk mempercepat fallback ('sales', 'inventory', dll)
        status   : HTTP status code (default 200)
        **extra_context: context tambahan yang di-merge ke context utama

    Contoh:
        return render_page(request, 'sales_history', {'data': qs})
        return render_page(request, 'dashboard', module='sales')
        return render_page(request, 'product_list', ctx, status=200)

    Raise:
        TemplateDoesNotExist dengan pesan lengkap + solusi jika tidak ditemukan
    """
    ctx = {**(context or {}), **extra_context}
    resolved = resolve_template(template, module=module)
    return render(request, resolved, ctx, status=status)


def template_response(
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    request  : HttpRequest,
    template : str,
    context  : dict | None = None,
    *,
    module   : str | None = None,
    status   : int = 200,
    content_type: str = 'text/html',
) -> TemplateResponse:
    """
    Versi TemplateResponse dari render_page().
    Berguna untuk class-based views atau response yang belum di-render.
    """
    ctx      = context or {}
    resolved = resolve_template(template, module=module)
    return TemplateResponse(request, resolved, ctx,
                            status=status, content_type=content_type)


def get_template_path(alias: str) -> str:
    """
    Kembalikan path template dari alias tanpa melakukan render.
    Berguna untuk debugging atau email templates.

    Contoh:
        path = get_template_path('dashboard')
        # → 'lumra_pages/sales/dashboard.html'
    """
    return TEMPLATE_REGISTRY.get(alias, alias)


def list_templates(module: str | None = None) -> dict[str, str]:
    """
    Kembalikan semua entry di TEMPLATE_REGISTRY.
    Kalau module diberikan, filter hanya yang mengandung module tersebut.

    Berguna untuk debugging: python manage.py shell → from lumra_config.utils import list_templates
    """
    if module:
        return {k: v for k, v in TEMPLATE_REGISTRY.items() if f'/{module}/' in v}
    return dict(TEMPLATE_REGISTRY)


# ─────────────────────────────────────────────────────────────────────────────
# MIGRATION HELPER — bantu update views lama secara bertahap
# ─────────────────────────────────────────────────────────────────────────────

def render_compat(
    request  : HttpRequest,
    template : str,
    context  : dict | None = None,
    **kwargs,
) -> HttpResponse:
    """
    Kompatibilitas mundur — identik dengan render_page() tapi
    juga menerima path lama (misalnya 'lumra_pages/sales/sales_insight.html')
    dan otomatis memetakan ke path baru lewat registry.

    Pakai ini di views yang belum sempat dimigrate ke render_page().
    Tidak perlu ubah argumen — cukup ganti:

        from django.shortcuts import render
        →
        from lumra_config.utils import render_compat as render
    """
    return render_page(request, template, context, **kwargs)