# lumra_config/views/inventory_views.py
# Auto-generated oleh lumra_sync.py dari core/views/inventory_views.py
# JANGAN EDIT MANUAL — edit core/views/inventory_views.py lalu jalankan lumra_sync.py lagi

import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import (
    Avg, Count, ExpressionWrapper, F, FloatField, OuterRef,
    Prefetch, Q, Subquery, Sum,
)
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime

from lumra_config.models import (
    Location,
    Category,
    Product,
    ProductVariant,
    Requisition,
    Stock,
)
from .helpers import check_queryset_empty, create_empty_context

# additional imports needed by import/export functionality
import csv
import io
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction, IntegrityError


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def _net_stock_subquery(variant_field="pk"):
    """
    Return a Subquery that calculates the NET stock for a single variant.

    Stock is a ledger table — each row is a transaction. Net stock is the
    sum of all 'in'/'transfer_received'/'adjustment' quantities minus
    'out'/'transfer_sent' quantities.

    Using a subquery (instead of a flat Sum on joined rows) avoids
    double-counting when multiple Stock rows exist per variant.
    """
    positive = ("in", "transfer_received", "adjustment")
    negative = ("out", "transfer_sent")

    inbound = (
        Stock.objects.filter(variant=OuterRef(variant_field), transaction_type__in=positive)
        .values("variant")
        .annotate(s=Sum("quantity"))
        .values("s")
    )
    outbound = (
        Stock.objects.filter(variant=OuterRef(variant_field), transaction_type__in=negative)
        .values("variant")
        .annotate(s=Sum("quantity"))
        .values("s")
    )
    return inbound, outbound


# ============================================================================
# IMPORT / EXPORT helpers and endpoints for products CSV
# ============================================================================

@login_required
@require_GET
# TODO[C3-LONG]: 'products_import_template' = 46 baris (max 30). Pecah: products_import_template_validate(), products_import_template_query(), products_import_template_render()
def products_import_template(request):
    """
    Kirim file CSV kosong berisi header + 1 baris contoh.
    Filosofi: User tidak boleh menebak. Beri mereka 'cockpit' yang jelas.
    """

    # ── Kolom yang akan ditampilkan di template ──
    # Diurutkan: identitas → kategori → harga → stok → opsional
    HEADERS = [
        'sku',
        'product_name',
        'category_name',      # human-readable; backend akan resolve ke category_id
        'unit_name',          # misal: Pcs, Kg, Liter, Pack
        'cost_price',         # harga modal (angka, tanpa Rp / titik / koma)
        'selling_price',      # harga jual
        'minimum_stock',      # batas stok rendah (low_stock_threshold)
        'initial_stock',      # stok awal saat import
        'is_active',          # TRUE / FALSE
        'description',        # opsional
    ]

    # ── 1 baris contoh agar user tahu format ──
    EXAMPLE_ROW = [
        'COFFEE-001',
        'Aceh Gayo Arutala 250g',
        'Coffee Beans',
        'Pcs',
        '85000',              # angka murni, tanpa Rp atau separator ribuan
        '125000',
        '10',
        '50',
        'TRUE',
        'High quality single origin arabica dari Gayo, Aceh.',
    ]

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="lumra_import_template.csv"'

    # BOM agar Excel (Windows) langsung mengenali encoding UTF-8
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(HEADERS)
    writer.writerow(EXAMPLE_ROW)

    return response


@login_required
# TODO[C3-LONG]: 'products_import' = 180 baris (max 30). Pecah: products_import_validate(), products_import_query(), products_import_render()
@require_POST
def products_import(request):
    """
    Upload + proses CSV. Prinsip Lamborghini: cepat, presisi, tidak crash.
    """

    csv_file = request.FILES.get('file')

    # ── Guard: file harus ada ──
    if not csv_file:
        return JsonResponse({'success': False, 'error': 'File CSV tidak ditemukan.'}, status=400)

    # ── Guard: ekstensi ──
    if not csv_file.name.lower().endswith('.csv'):
        return JsonResponse({'success': False, 'error': 'Hanya file .csv yang diizinkan.'}, status=400)

    # ── Guard: ukuran (maks 5 MB) ──
    MAX_SIZE_MB = 5
    if csv_file.size > MAX_SIZE_MB * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'error': f'File terlalu besar. Maksimal {MAX_SIZE_MB} MB.'
        }, status=400)

    # ── Baca file; handle encoding UTF-8 dengan/tanpa BOM ──
    try:
        raw = csv_file.read().decode('utf-8-sig')   # utf-8-sig otomatis strip BOM
    except UnicodeDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Encoding file tidak valid. Simpan CSV dalam format UTF-8.'
        }, status=400)

    reader = csv.DictReader(io.StringIO(raw))

    # ── Validasi header wajib ada ──
    REQUIRED_HEADERS = {'sku', 'product_name', 'selling_price'}
    actual_headers   = set(reader.fieldnames or [])
    missing          = REQUIRED_HEADERS - actual_headers

    if missing:
        return JsonResponse({
            'success': False,
            'error': f'Kolom wajib tidak ditemukan: {", ".join(sorted(missing))}'
        }, status=400)

    # ── Pre-load data referensi (category cache) ──
    # Menghindari N+1 query saat memproses ribuan baris
    category_cache: dict[str, Category] = {
        c.name.lower(): c for c in Category.objects.all()
    }

    # ── State akumulasi ──
    # we'll create ProductVariant records; products will be auto-created as needed
    to_create   : list[ProductVariant] = []
    to_skip     : list[dict]    = []    # baris yang diabaikan + alasan
    existing_skus: set[str]     = set(
        ProductVariant.objects.values_list('sku', flat=True)
    )
    seen_skus_in_file: set[str] = set()  # deteksi duplikat dalam file itu sendiri

    # cache products by lower‑cased name so we can reuse them
    product_cache: dict[str, Product] = {
        p.name.lower(): p for p in Product.objects.all()
    }

    # ── Iterasi baris ──
    for line_num, row in enumerate(reader, start=2):   # baris 1 = header

        sku          = _clean_str(row.get('sku', ''))
        product_name = _clean_str(row.get('product_name', ''))

        # ── Validasi field wajib ──
        if not sku:
            to_skip.append({'row': line_num, 'sku': '(kosong)', 'reason': 'SKU tidak boleh kosong'})
            continue
        if not product_name:
            to_skip.append({'row': line_num, 'sku': sku, 'reason': 'product_name tidak boleh kosong'})
            continue

        # ── Cek duplikat SKU di DB ──
        if sku in existing_skus:
            to_skip.append({'row': line_num, 'sku': sku, 'reason': 'SKU sudah ada di database (dilewati)'})
            continue

        # ── Cek duplikat SKU dalam file ini sendiri ──
        if sku in seen_skus_in_file:
            to_skip.append({'row': line_num, 'sku': sku, 'reason': 'SKU duplikat dalam file CSV'})
            continue
        seen_skus_in_file.add(sku)

        # ── Parse harga ──
        selling_price = _parse_decimal(row.get('selling_price', ''))
        if selling_price is None:
            to_skip.append({'row': line_num, 'sku': sku, 'reason': 'selling_price bukan angka valid'})
            continue

        cost_price = _parse_decimal(row.get('cost_price', ''))  # boleh None

        # ── Parse stok ── (ignored for now; stock tracked separately)
        #initial_stock    = _parse_int(row.get('initial_stock', '0'), default=0)
        #minimum_stock    = _parse_int(row.get('minimum_stock', '10'), default=10)

        # ── Resolve category (get_or_create dengan cache) ──
        cat_name = _clean_str(row.get('category_name', ''))
        category = None
        if cat_name:
            cat_key = cat_name.lower()
            if cat_key not in category_cache:
                # Buat kategori baru jika belum ada
                new_cat, _ = Category.objects.get_or_create(
                    name__iexact=cat_name,
                    defaults={'name': cat_name}
                )
                category_cache[cat_key] = new_cat
            category = category_cache[cat_key]

        # ── Parse is_active ──
        raw_active = _clean_str(row.get('is_active', 'TRUE')).upper()
        is_active  = raw_active not in ('FALSE', '0', 'NO', 'TIDAK', 'NONAKTIF')

        # ── ensure product exists
        prod_key = product_name.lower()
        product = product_cache.get(prod_key)
        if not product:
            product = Product.objects.create(
                name=product_name,
                category=category,
            )
            product_cache[prod_key] = product

        # ── build ProductVariant (unsaved) ──
        to_create.append(ProductVariant(
            product=product,
            sku=sku,
            price_sell=selling_price or 0,
            price_buy=cost_price or 0,
        ))

        # Update set agar duplikat berikutnya terdeteksi
        existing_skus.add(sku)

    # ── Tulis ke DB dalam satu transaksi ──
    imported_count = 0
    db_error       = None

    if to_create:
        try:
            with transaction.atomic():
                # ignore_conflicts=False -> sudah filter duplikat manual di loop
                # batch_size=500 -> optimal untuk PostgreSQL, cegah memory spike
                ProductVariant.objects.bulk_create(to_create, batch_size=500)
                imported_count = len(to_create)
        except IntegrityError as e:
            db_error = f'Database integrity error: {str(e)}'
        except Exception as e:
            db_error = f'Unexpected error saat menyimpan: {str(e)}'

    if db_error:
        return JsonResponse({
            'success' : False,
            'error'   : db_error,
            'imported': 0,
            'skipped' : len(to_skip),
        }, status=500)

    # ── Bangun respons ──
    response_data = {
        'success'  : True,
        'imported' : imported_count,
        'skipped'  : len(to_skip),
        'total_rows': imported_count + len(to_skip),
    }

    # Sertakan detail baris yang diskip (maks 50 baris untuk keamanan payload)
    if to_skip:
        response_data['skip_details'] = to_skip[:50]
        if len(to_skip) > 50:
            response_data['skip_details_truncated'] = True

    return JsonResponse(response_data)


# ═══════════════════════════════════════════════════════════════════════
#  3. PRIVATE HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _clean_str(value: str | None) -> str:
    """Strip whitespace, kembalikan string kosong jika None."""
    return (value or '').strip()


def _parse_decimal(value: str | None) -> Decimal | None:
    """
    Konversi string harga ke Decimal.
    Toleran terhadap: '125.000', '125,000', 'Rp 125000', '125_000'
    """
    if not value:
        return None
    cleaned = (
        _clean_str(value)
        .replace('Rp', '').replace('rp', '')
        .replace('.', '').replace(',', '')   # hapus separator ribuan gaya Indonesia
        .replace('_', '').replace(' ', '')
    )
    try:
        query_result = Decimal(cleaned)
        if result < 0:
            return None
        return result
    except InvalidOperation:
        return None


def _parse_int(value: str | None, default: int = 0) -> int:
    """Konversi string ke int; kembalikan default jika gagal."""
    try:
        return max(0, int(_clean_str(value)))
    except (ValueError, TypeError):
        return default


# ------------------------------------------------------------------
# INVENTORY → PRODUCTS LIST
# ------------------------------------------------------------------
 # TODO[C3-LONG]: 'products_view' = 166 baris (max 30). Pecah: products_view_validate(), products_view_query(), products_view_render()

@login_required
def products_view(request):
    """
    Product list with summary stats.

    Optimisations vs. original:
    - Annotate net_stock on variants in a single query (no per-product loop)
    - low_stock_count uses a single annotated query instead of two
    - total_stock_value computed correctly from net stock × price_buy
    - All stats derived from annotated querysets, not Python loops
    """

    # make absolutely sure the ``user.profile`` attribute is present;
    # several of the downstream templates (navbar/sidebar/products) access
    # ``user.profile`` without guarding.  the middleware normally handles
    # this, but we double‑check here so the view is safe even when invoked
    # in isolation during tests.
    from lumra_config.models import UserProfile
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        setattr(request.user, "profile", profile)

        # mimic the middleware defaults for standalone invocation
        defaults = {
            "role": "User",
            "phone": "",
            "address": "",
            "two_factor_enabled": False,
            "language": "id",
            "email_notifications": False,
            "push_notifications": False,
            "marketing_emails": False,
            "theme": "light",
        }
        for attr, val in defaults.items():
            if not hasattr(profile, attr):
                setattr(profile, attr, val)
        if not hasattr(profile, "avatar") or profile.avatar is None:
            from types import SimpleNamespace
            setattr(profile, "avatar", SimpleNamespace(url="/static/img/default-avatar.png"))
        if not hasattr(profile, "stores"):
            class _DummyManager:
                def all(self):
                    return []
            setattr(profile, "stores", _DummyManager())

    # Check if products table is empty
    total_products = Product.objects.count()
    if total_products == 0:
        # no product rows – we still have to hand the JS something or the
        # Alpine component will crash (x-cloak stays active and the page
        # appears completely blank).  create_empty_context returns only a
        # handful of keys, so supply all of the template variables that are
        # referenced later.  the values here mirror what the normal code
        # would provide so the template can render without checks.
        ctx = create_empty_context(
            "Products",
            "Data produk tidak ditemukan. Silahkan tambah produk terlebih dahulu."
        )
        ctx.update({
            "categories": [],
            "products_json": json.dumps([]),
            "total_products": 0,
            "low_stock_count": 0,
            "total_stock_value": 0,
            "average_price": 0,
            "page_obj": Paginator([], 10).get_page(1),
            "low_stock_threshold": 10,
        })
        return render(request, "lumra_pages/inventory/products.html", ctx)

    # Net stock per variant (single aggregation pass)
    variants_with_stock = ProductVariant.objects.annotate(
        inbound=Sum(
            "stock_entries__quantity",
            filter=Q(stock_entries__transaction_type__in=("in", "transfer_received", "adjustment")),
        ),
        outbound=Sum(
            "stock_entries__quantity",
            filter=Q(stock_entries__transaction_type__in=("out", "transfer_sent")),
        ),
    ).annotate(
        net_stock=ExpressionWrapper(
            (F("inbound") or 0) - (F("outbound") or 0),
            output_field=FloatField(),
        )
    )

    low_stock_threshold = 10

    # Count distinct products that have at least one low-stock variant
    low_stock_count = (
        Product.objects.filter(
            variants__in=variants_with_stock.filter(net_stock__lt=low_stock_threshold)
        )
        .distinct()
        .count()
    )

    # Total stock value = Σ(net_stock × price_buy) per variant
    # Done in Python after a single queryset fetch to keep the expression readable;
    # a pure-SQL approach would require a lateral join which Django doesn't support natively.
    stock_value_qs = variants_with_stock.values("net_stock", "price_buy")
    total_stock_value = sum(
        (row["net_stock"] or 0) * float(row["price_buy"])
        for row in stock_value_qs
    )

    average_price = ProductVariant.objects.aggregate(avg=Avg("price_sell"))["avg"] or 0

    # ── Product list (paginated) ──────────────────────────────
    # Annotate net_stock on first variant via prefetch so the template
    # can render stock without extra queries.
    variants_prefetch = Prefetch(
        "variants",
        queryset=variants_with_stock.order_by("sku"),
        to_attr="variants_with_stock",
    )

    products = (
        Product.objects
        .select_related("category", "vendor")
        .prefetch_related(variants_prefetch)
        .order_by("name")
    )

    paginator = Paginator(products, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))

    # build JSON payload for client‑side manager (same fields used in
    # the Alpine productManager).  keeping the data small reduces the
    # amount of JS parsing work on every navigation.
    def _serialize(prod):
        # rely on variants_with_stock prefetched earlier; take first
        # entry so that the table page doesn't have to loop again.
        variant = prod.variants_with_stock[0] if prod.variants_with_stock else None
        return {
            "id": prod.id,
            "name": prod.name,
            "category": prod.category.name if prod.category else "",
            "stock": variant.net_stock if variant else 0,
            "price": float(variant.price_sell) if variant else 0,
            "description": prod.description or "",
            "image_url": prod.image.url if getattr(prod, "image", None) else "",
        }

    products_json = json.dumps([_serialize(p) for p in page_obj])
    # categories are used by the template filter dropdown; including them
    # avoids an undefined-variable situation.
    categories = list(
        Product.objects.values_list("category__name", flat=True).distinct()
    )

    context = {
        "total_products":    total_products,
        "low_stock_count":   low_stock_count,
        "total_stock_value": round(total_stock_value, 2),
        "average_price":     average_price,
        "page_obj":          page_obj,
        "low_stock_threshold": low_stock_threshold,
        "report_title":      "Products",
        "is_empty": False,
        "products_json": products_json,
        "categories": categories,
    }

    return render(request, "lumra_pages/inventory/products.html", context)


# ------------------------------------------------------------------
# INVENTORY → PRODUCT DETAIL
# TODO[C3-LONG]: 'product_detail_view' = 50 baris (max 30). Pecah: product_detail_view_validate(), product_detail_view_query(), product_detail_view_render()
# ------------------------------------------------------------------

@login_required
def product_detail_view(request, product_id):
    """
    Product detail with per-variant net stock.

    Optimisations vs. original:
    - Stock aggregated in a single bulk query (dict lookup), not N loops
    - Net stock calculated correctly (inbound − outbound)
    """

    product = get_object_or_404(
        Product.objects.select_related("category", "vendor", "tax", "unit")
                       .prefetch_related("variants__attributes"),
        id=product_id,
    )

    # Single bulk aggregate for all variants of this product
    variant_ids = list(product.variants.values_list("id", flat=True))

    inbound_qs = (
        Stock.objects
        .filter(
            variant_id__in=variant_ids,
            transaction_type__in=("in", "transfer_received", "adjustment"),
        )
        .values("variant_id")
        .annotate(total=Sum("quantity"))
    )
    outbound_qs = (
        Stock.objects
        .filter(
            variant_id__in=variant_ids,
            transaction_type__in=("out", "transfer_sent"),
        )
        .values("variant_id")
        .annotate(total=Sum("quantity"))
    )

    inbound_map  = {row["variant_id"]: row["total"] for row in inbound_qs}
    outbound_map = {row["variant_id"]: row["total"] for row in outbound_qs}

    for variant in product.variants.all():
        net = (inbound_map.get(variant.id) or 0) - (outbound_map.get(variant.id) or 0)
        variant._cached_total_stock = net

    context = {
        "product":      product,
        "report_title": f"Product Detail - {product.name}",
    }

    return render(request, "lumra_pages/inventory/product_details.html", context)


# ------------------------------------------------------------------
# TODO[C3-LONG]: 'stock_planning_view' = 66 baris (max 30). Pecah: stock_planning_view_validate(), stock_planning_view_query(), stock_planning_view_render()
# INVENTORY → STOCK PLANNING
# ------------------------------------------------------------------

@login_required
def stock_planning_view(request):
    """
    Stock planning / allocation view.

    Optimisations vs. original:
    - annotated_total_stock assigned directly to _cached_total_stock
      without a second per-object query
    - Net stock annotation (inbound − outbound) instead of raw Sum
    """

    q = request.GET.get("q", "").strip()

    variants = (
        ProductVariant.objects
        .select_related("product")
        .annotate(
            inbound=Sum(
                "stock_entries__quantity",
                filter=Q(stock_entries__transaction_type__in=(
                    "in", "transfer_received", "adjustment"
                )),
            ),
            outbound=Sum(
                "stock_entries__quantity",
                filter=Q(stock_entries__transaction_type__in=(
                    "out", "transfer_sent"
                )),
            ),
        )
        .order_by("sku")
    )

    if q:
        variants = variants.filter(
            Q(sku__icontains=q) | Q(product__name__icontains=q)
        )

    # Check if variants is empty
    if not variants.exists():
        return render(
            request,
            "lumra_pages/inventory/stock_planning.html",
            create_empty_context("Stock Planning", "Data varian produk tidak ditemukan. Silahkan tambah produk dan varian terlebih dahulu.")
        )

    paginator = Paginator(variants, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))
    # TODO[C5-N1]: Query di dalam loop → pindahkan ke atas loop.
    # Gunakan: queryset = Model.objects.select_related(...).prefetch_related(...)
    # lalu iterasi queryset di luar, TANPA query tambahan di dalam loop.

    # Cache net stock — no extra queries
    for v in page_obj.object_list:
        v._cached_total_stock = (v.inbound or 0) - (v.outbound or 0)

    requisition_count = Requisition.objects.filter(
        requested_by=request.user
    ).count()

    context = {
        "page_obj":          page_obj,
        "locations":         Location.objects.all().order_by("name"),
        "requisition_count": requisition_count,
        "query":             q,
        "report_title":      "Stock Planning",
        "is_empty": False,
    }

    return render(request, "lumra_pages/inventory/stock_planning.html", context)


# TODO[C3-LONG]: 'locations_view' = 39 baris (max 30). Pecah: locations_view_validate(), locations_view_query(), locations_view_render()
# ------------------------------------------------------------------
# LOCATIONS MANAGEMENT
# ------------------------------------------------------------------

@login_required
def locations_view(request):
    """
    Location list with JSON payload for Alpine.js front-end.

    Uses json_script-safe serialisation (consistent with recipe_list pattern).
    Fields not present in the model (city, phone, etc.) are NOT fabricated
    here — the front-end should handle missing keys gracefully instead.
    """

    locations_qs = Location.objects.all().order_by("name")

    # Check if locations is empty
    if not locations_qs.exists():
        return render(
            request,
            "lumra_pages/master_data/locations.html",
            create_empty_context("Locations Management", "Data lokasi tidak ditemukan. Silahkan tambah lokasi terlebih dahulu.")
        )

    # Serialise only fields that actually exist on the model
    locations_data = [
        {
            "id":            loc.id,
            "name":          loc.name,
            "address":       loc.address,
            "location_type": loc.location_type,
            "created_at":    localtime(loc.created_at).strftime("%Y-%m-%d"),
        }
        for loc in locations_qs
    ]

    context = {
        "locations":      locations_qs,          # for server-side rendering fallback
        "locations_json": json.dumps(locations_data),  # for Alpine.js
        "report_title":   "Locations Management",
        "is_empty": False,
    }

    return render(request, "lumra_pages/master_data/locations.html", context)