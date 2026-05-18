# Claude Handoff: production

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 17
Jumlah view terkait: 20

## Template Scope

### lumra_pages/production/rnd_list.html
- File: `lumra_config/templates/lumra_pages/production/rnd_list.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=28, interactive=3, issues=3, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Produksi / Lab RnD
  - HEADING (H1): Lab Riset & Pengembangan
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - FILTER / TAB: Semua
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-white text-slate-700 rounded-lg tex'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-slate-800 text-white rounded-lg tex'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/bom_list.html
- File: `lumra_config/templates/lumra_pages/production/bom_list.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=26, interactive=4, issues=3, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Produksi / Resep & BOM
  - HEADING (H1): Daftar Resep (Bill of Materials)
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - FILTER / TAB: Semua BOM
  - FILTER / TAB: Aktif
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-white text-slate-700 rounded-lg tex'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='px-3 py-1.5 bg-slate-800 text-white rounded-lg tex'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/finished_goods_receipt.html
- File: `lumra_config/templates/lumra_pages/production/finished_goods_receipt.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=30, interactive=10, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [receiptApp()]: Production / Finished Goods Finished Goods Receipt Verifikas…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Production / Finished Goods
  - HEADING (H1): Finished Goods Receipt
  - BUTTON: + Catat Receipt: + Catat Receipt
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Receipts
  - CARD: Qty Diterima
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/material_consumption.html
- File: `lumra_config/templates/lumra_pages/production/material_consumption.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=30, interactive=10, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [consumptionApp()]: Production / Material Consumption Material Consumption Bandi…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Production / Material Consumption
  - HEADING (H1): Material Consumption
  - BUTTON: + Catat Konsumsi: + Catat Konsumsi
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Records
  - CARD: PO Selesai
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/production_costing.html
- File: `lumra_config/templates/lumra_pages/production/production_costing.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=19, interactive=4, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [costingApp()]: Production / Costing Production Costing Ringkasan biaya stan…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Production / Costing
  - HEADING (H1): Production Costing
  - BUTTON: Export CSV: Export CSV
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Orders
  - CARD: Biaya Standar
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/production_order_list.html
- File: `lumra_config/templates/lumra_pages/production/production_order_list.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=27, interactive=6, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Produksi / Surat Perintah Kerja (SPK)
  - HEADING (H1): Production Orders
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total PO
  - CARD: Pending
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/production_scheduling.html
- File: `lumra_config/templates/lumra_pages/production/production_scheduling.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=19, interactive=3, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [scheduleApp()]: Production / Scheduling Production Scheduling Kalender order…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Production / Scheduling
  - HEADING (H1): Production Scheduling
  - CARD: Prev Next
  - BUTTON: Prev: Prev
  - BUTTON: Next: Next
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/production_waste.html
- File: `lumra_config/templates/lumra_pages/production/production_waste.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=38, interactive=15, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [wasteApp()]: Production / Waste Production Waste Catatan scrap, spoilage,…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Production / Waste
  - HEADING (H1): Production Waste
  - BUTTON: + Catat Waste: + Catat Waste
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Records
  - CARD: Jenis Waste
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/recipe_list.html
- File: `lumra_config/templates/lumra_pages/production/recipe_list.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=31, interactive=10, issues=2, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [recipesListApp()]: Dashboard / Recipe Daftar Recipe Kelola recipe produksi bese…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Dashboard / Recipe
  - HEADING (H1): Daftar Recipe
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total Recipe
  - CARD: Tampil
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-rose-600 hover:text-rose-800'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/rnd_detail.html
- File: `lumra_config/templates/lumra_pages/production/rnd_detail.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=27, interactive=9, issues=3, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [rndDetailApp()]: Lab RnD / Dibuat oleh • Trial dari Edit Formula Tambah Trial…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Lab RnD /
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BADGE / STATUS: 
  - HEADING (H1): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Tambah Trial: Tambah Trial
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='trial-tab'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/bom_detail.html
- File: `lumra_config/templates/lumra_pages/production/bom_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=24, interactive=4, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [bomDetailApp()]: Dari R&D SKU • Versi Edit Resep Duplikat Struktur Biaya Baha…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Duplikat: Duplikat
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Struktur Biaya Bahan Lima komponen terbesar ditampilkan terpisah, sisanya digabu…
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/bom_form.html
- File: `lumra_config/templates/lumra_pages/production/bom_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=30, interactive=13, issues=2, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [bomFormApp()]: BOM / {% if is_edit %}Edit{% else %}Form Baru{% endif %} {%…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: BOM / {% if is_edit %}Edit{% else %}Form Baru{% endif %}
  - HEADING (H1): {% if is_edit %}Edit BOM{% else %}Buat BOM Baru{% endif %}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Nama BOM SKU Produk Jadi * Pilih SKU produk jadi... Mode Revisi Koreksi minor, t…
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-rose-600 hover:text-rose-800'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/production_order_detail.html
- File: `lumra_config/templates/lumra_pages/production/production_order_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=17, interactive=4, issues=6, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [poDetailApp()]: Status Saat Ini Selesai / Waktu Mulai Scheduled Date Catatan…
  - CARD: Status Saat Ini Selesai / Waktu Mulai Scheduled Date Catatan Operator Bahan yang…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - PROGRESS GAUGE: Selesai /
  - LAYOUT CONTAINER [GRID 2 cols]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='control-btn btn-start col-span-2'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='h-14 rounded-xl bg-slate-100 text-slate-600 font-b'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='h-14 rounded-xl bg-slate-100 text-slate-600 font-b'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='control-btn btn-stop'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='control-btn btn-complete disabled:opacity-50'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/production_order_form.html
- File: `lumra_config/templates/lumra_pages/production/production_order_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=26, interactive=11, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [poFormApp()]: Production Order / {% if is_edit %}Edit{% else %}Form Baru{%…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Production Order / {% if is_edit %}Edit{% else %}Form Baru{% endif %}
  - HEADING (H1): {% if is_edit %}Edit SPK{% else %}Buat SPK{% endif %}
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: BOM Aktif * Pilih BOM... Kode PO Target Kuantitas Line Produksi Rencana Mulai Pr…
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - INPUT [select] form.bomId: form.bomId
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/recipe_detail.html
- File: `lumra_config/templates/lumra_pages/production/recipe_detail.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 4
- Reverse stats: components=26, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [recipeDetailApp()]: Production / Recipe Detail • Back to List Edit Recipe Yield…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Production / Recipe Detail
  - HEADING (H1): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Yield
  - CARD: Preparation minutes
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/recipe_form.html
- File: `lumra_config/templates/lumra_pages/production/recipe_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=27, interactive=14, issues=2, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [recipeFormApp()]: Recipe / {% if is_edit %}Edit{% else %}Form Baru{% endif %}…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - [ NAVIGATION BAR ]: Recipe / {% if is_edit %}Edit{% else %}Form Baru{% endif %}
  - HEADING (H1): {% if is_edit %}Edit Recipe{% else %}Buat Recipe Baru{% endif %}
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: {% csrf_token %} Nama Recipe * Kategori * Pilih kategori {% for category in cate…
  - [ FORM ]: {% csrf_token %} Nama Recipe * Kategori * Pilih kategori {% for category in cate…
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='w-full rounded-xl border border-slate-200 px-3 py-'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/production/rnd_form.html
- File: `lumra_config/templates/lumra_pages/production/rnd_form.html`
- Batch: `batch_4_complex`
- Alasan batch: Report/print/logic-heavy page, cocok setelah fondasi stabil.
- Complexity: 6
- Reverse stats: components=52, interactive=16, issues=2, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [rndFormApp()]: Lab RnD / Mulai Trial Identitas Formula Nama Formula Target…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Lab RnD /
  - HEADING (H1): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
  - BUTTON: Mulai Trial: Mulai Trial
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='text-violet-400 hover:text-violet-700 leading-none'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### bom_list
- File: `lumra_config/views/production_ops_views.py`:183
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def bom_list(request):
    query = request.GET.get("q", "").strip()
    qs = (
        BillOfMaterial.objects
        .select_related("finished_variant", "finished_variant__product")
        .prefetch_related("items__component")
        .all()
    )
    if query:
        qs = qs.filter(
            Q(code__icontains=query)
            | Q(finished_variant__sku__icontains=query)
            | Q(finished_variant__product__name__icontains=query)
        )
    qs = qs.order_by("-updated_at")

    rows = []
    for b in qs[:500]:
        items = list(b.items.all())
        rows.append({
            "id": b.id,
            "code": b.code,
            "name": b.name or (b.finished_variant.product.name if b.finished_variant.product else b.finished_variant.sku),
            "sku": b.finished_variant.sku,
            "version": b.version,
            "is_active": b.is_active,
            "ingredients_count": len(items),
            "estimated_cost": float(sum((it.quantity or 0) * (it.component.price_buy or 0) for it in items)),
            "updated_at": localtime(b.updated_at).strftime("%Y-%m-%d"),
        })
    context = {"boms_data": rows, "report_title": "BOM List"}
    return render(request, "lumra_pages/production/bom_list.html", context)
```

### bom_form
- File: `lumra_config/views/production_ops_views.py`:274
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def bom_form(request, pk=None):
    bom = get_object_or_404(BillOfMaterial, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["finished_variant_id", "code", "version", "items"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        finished_variant = get_object_or_404(ProductVariant, pk=payload["finished_variant_id"])
        items = payload.get("items") or []
        if not isinstance(items, list) or len(items) == 0:
            return JsonResponse({"success": False, "error": "Items must be a non-empty list."}, status=400)

        with transaction.atomic():
            obj = bom or BillOfMaterial(created_by=request.user)
            obj.finished_variant = finished_variant
            obj.code = str(payload["code"]).strip()
            obj.version = int(payload.get("version") or 1)
            obj.name = str(payload.get("name", "")).strip()
            obj.notes = str(payload.get("notes", "")).strip()
            obj.is_active = bool(payload.get("is_active", True))
            obj.save()

            BillOfMaterialItem.objects.filter(bom=obj).delete()
            item_objs = []
            for it in items:
                comp_id = it.get("component_variant_id")
                qty = it.get("quantity")
                if not comp_id or qty is None:
                    continue
                component = get_object_or_404(ProductVariant, pk=comp_id)
                unit = None
                if it.get("unit_id"):
                    unit = get_object_or_404(Unit, pk=it["unit_id"])
                item_objs.append(BillOfMaterialItem(
                    bom=obj,
                    component=component,
                    quantity=qty,
                    unit=unit,
                    notes=str(it.get("notes", "")).strip(),
                ))
            if not item_objs:
                return JsonResponse({"success": False, "error": "No valid BOM items provided."}, status=400)
            BillOfMaterialItem.objects.bulk_create(item_objs)

        return JsonResponse({"success": True, "id": obj.id})

    variants = ProductVariant.objects.select_related("product").order_by("sku")[:3000]
    units = Unit.objects.order_by("symbol")
    context = {
        "is_edit": bool(bom),
        "bom_id": bom.id if bom else None,
        "variants_data": [
            {"id": v.id, "sku": v.sku, "name": v.product.name if v.product else v.sku, "price_buy": float(v.price_buy or 0)}
            for v in variants
        ],
        "units_data": [{"id": u.id, "symbol": u.symbol, "name": u.name} for u in units],
        "bom_data": {
            "id": bom.id,
            "code": bom.code,
            "version": bom.version,
            "name": bom.name or "",
            "finished_sku": bom.finished_variant.sku,
            "notes": bom.notes or "",
            "is_active": bom.is_active,
            "items": [
                {
                    "id": item.id,
                    "sku": item.component.sku,
                    "name": item.component.product.name if item.component.product else item.component.sku,
                    "quantity": float(item.quantity or 0),
                    "unit": item.unit.symbol if item.unit else "",
                    "unit_price": float(item.component.price_buy or 0),
                }
                for item in bom.items.select_related("component", "component__product", "unit").all()
            ],
        } if bom else {},
        "submit_url": request.path,
        "list_url": "/production/bom/",
        "report_title": "BOM Form",
    }
    return render(request, "lumra_pages/production/bom_form.html", context)
```

### bom_detail
- File: `lumra_config/views/production_ops_views.py`:322
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def bom_detail(request, pk):
    bom = get_object_or_404(
        BillOfMaterial.objects.select_related("finished_variant", "finished_variant__product")
        .prefetch_related("items__component", "items__component__product", "items__component__stock_entries", "items__unit"),
        pk=pk,
    )
    items = []
    for it in bom.items.all():
        items.append({
            "id": it.id,
            "sku": it.component.sku,
            "name": it.component.product.name if it.component.product else it.component.sku,
            "quantity": float(it.quantity),
            "unit": it.unit.symbol if it.unit else "",
            "unit_price": float(it.component.price_buy or 0),
            "total": float((it.quantity or 0) * (it.component.price_buy or 0)),
            "stock": float(it.component.total_stock or 0),
        })
    data = {
        "id": bom.id,
        "code": bom.code,
        "name": bom.name or (bom.finished_variant.product.name if bom.finished_variant.product else bom.finished_variant.sku),
        "finished_sku": bom.finished_variant.sku,
        "version": bom.version,
        "is_active": bom.is_active,
        "notes": bom.notes,
        "rnd_id": getattr(bom, "rnd_id", None),
        "estimated_cost": float(sum((it.quantity or 0) * (it.component.price_buy or 0) for it in bom.items.all())),
        "items": items,
        "updated_at": localtime(bom.updated_at).strftime("%Y-%m-%d %H:%M"),
        "versions": [
            {
                "id": sibling.id,
                "version": sibling.version,
                "is_active": sibling.is_active,
                "created_at": localtime(sibling.created_at).strftime("%Y-%m-%d %H:%M"),
                "created_by": sibling.created_by.get_username() if sibling.created_by else "System",
            }
            for sibling in BillOfMaterial.objects.select_related("created_by")
            .filter(finished_variant=bom.finished_variant)
            .order_by("-version", "-created_at")[:10]
        ],
    }
    context = {"bom_data": data, "report_title": f"BOM Detail - {bom.code}"}
    return render(request, "lumra_pages/production/bom_detail.html", context)
```

### production_order_list
- File: `lumra_config/views/production_ops_views.py`:362
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def production_order_list(request):
    query = request.GET.get("q", "").strip()
    qs = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .order_by("-created_at")
    )
    if query:
        qs = qs.filter(
            Q(code__icontains=query)
            | Q(bom__code__icontains=query)
            | Q(bom__finished_variant__sku__icontains=query)
            | Q(bom__finished_variant__product__name__icontains=query)
        )

    rows = []
    for po in qs[:500]:
        product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
        rows.append({
            "id": po.id,
            "code": po.code,
            "product": product_name,
            "target_qty": float(po.target_quantity),
            "produced_qty": float(po.produced_quantity),
            "uom": po.unit.symbol if po.unit else "",
            "status": po.status,
            "line": po.line or "-",
            "start_date": po.scheduled_date.strftime("%d %b") if po.scheduled_date else "",
            "priority": po.priority or "Normal",
        })

    context = {"pos_data": rows, "report_title": "Production Orders"}
    return render(request, "lumra_pages/production/production_order_list.html", context)
```

### production_order_form
- File: `lumra_config/views/production_ops_views.py`:457
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def production_order_form(request, pk=None):
    po = get_object_or_404(ProductionOrder, pk=pk) if pk else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["code", "bom_id", "target_quantity"]
        missing = [k for k in required if k not in payload]
        if missing:
            return JsonResponse({"success": False, "error": f"Missing fields: {', '.join(missing)}."}, status=400)

        bom = get_object_or_404(BillOfMaterial, pk=payload["bom_id"])
        unit = None
        if payload.get("unit_id"):
            unit = get_object_or_404(Unit, pk=payload["unit_id"])

        obj = po or ProductionOrder(created_by=request.user)
        obj.code = str(payload["code"]).strip()
        obj.bom = bom
        obj.target_quantity = payload.get("target_quantity") or 0
        obj.unit = unit
        obj.priority = str(payload.get("priority", "Normal")).strip() or "Normal"
        obj.line = str(payload.get("line", "")).strip()
        obj.status = str(payload.get("status", obj.status)).strip() or obj.status
        obj.notes = str(payload.get("notes", "")).strip()
        obj.scheduled_date = _parse_iso_date(payload.get("scheduled_date"))
        obj.save()

        return JsonResponse({"success": True, "id": obj.id})

    boms = (
        BillOfMaterial.objects
        .select_related("finished_variant", "finished_variant__product")
        .filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "items",
                queryset=BillOfMaterialItem.objects.select_related(
                    "component",
                    "component__product",
                    "unit",
                ).prefetch_related("component__stock_entries"),
            )
        )
        .order_by("-updated_at")[:1000]
    )
    units = Unit.objects.order_by("symbol")
    context = {
        "is_edit": bool(po),
        "po_id": po.id if po else None,
        "boms_data": [
            {
                "id": b.id,
                "code": b.code,
                "name": b.name or (b.finished_variant.product.name if b.finished_variant.product else b.finished_variant.sku),
                "sku": b.finished_variant.sku,
                "items": [
                    {
                        "id": item.id,
                        "sku": item.component.sku,
                        "name": item.component.product.name if item.component.product else item.component.sku,
                        "quantity": float(item.quantity or 0),
                        "unit": item.unit.symbol if item.unit else "",
                        "unit_price": float(item.component.price_buy or 0),
                        "stock": float(item.component.total_stock or 0),
                    }
                    for item in b.items.all()
                ],
            }
            for b in boms
        ],
        "units_data": [{"id": u.id, "symbol": u.symbol} for u in units],
        "po_data": {
            "id": po.id,
            "code": po.code,
            "bom_id": po.bom_id,
            "target_quantity": float(po.target_quantity or 0),
            "line": po.line or "",
            "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
            "priority": po.priority or "Normal",
            "notes": po.notes or "",
            "unit_id": po.unit_id,
        } if po else {},
        "suggested_po_code": po.code if po else _suggest_po_code(),
        "submit_url": request.path,
        "list_url": "/production/order/",
        "report_title": "Production Order Form",
    }
    return render(request, "lumra_pages/production/production_order_form.html", context)
```

### production_order_detail
- File: `lumra_config/views/production_ops_views.py`:486
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def production_order_detail(request, pk):
    po = get_object_or_404(
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit"),
        pk=pk,
    )
    product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
    data = {
        "id": po.id,
        "code": po.code,
        "product": product_name,
        "bom_code": po.bom.code,
        "status": po.status,
        "target_qty": float(po.target_quantity),
        "produced_qty": float(po.produced_quantity),
        "uom": po.unit.symbol if po.unit else "",
        "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
        "started_at": localtime(po.started_at).strftime("%Y-%m-%d %H:%M") if po.started_at else "",
        "completed_at": localtime(po.completed_at).strftime("%Y-%m-%d %H:%M") if po.completed_at else "",
        "priority": po.priority,
        "line": po.line,
        "notes": po.notes,
        "created_at": localtime(po.created_at).strftime("%Y-%m-%d %H:%M"),
    }
    context = {"po_data": data, "report_title": f"Production Order - {po.code}"}
    return render(request, "lumra_pages/production/production_order_detail.html", context)
```

### production_scheduling
- File: `lumra_config/views/production_ops_views.py`:507
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def production_scheduling(request):
    qs = ProductionOrder.objects.select_related("bom", "bom__finished_variant", "bom__finished_variant__product").order_by("scheduled_date")[:500]
    rows = []
    for po in qs:
        product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
        rows.append({
            "id": po.id,
            "code": po.code,
            "product": product_name,
            "status": po.status,
            "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
        })
    context = {"orders_data": rows, "report_title": "Production Scheduling"}
    return render(request, "lumra_pages/production/production_scheduling.html", context)
```

### material_consumption
- File: `lumra_config/views/production_ops_views.py`:560
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def material_consumption(request):
    qs = (
        ProductionMaterialConsumption.objects
        .select_related("production_order", "component", "component__product", "unit")
        .order_by("-consumed_at")[:500]
    )
    rows = []
    for c in qs:
        rows.append({
            "id": c.id,
            "po_code": c.production_order.code,
            "sku": c.component.sku,
            "name": c.component.product.name if c.component.product else c.component.sku,
            "quantity": float(c.quantity),
            "unit": c.unit.symbol if c.unit else "",
            "consumed_at": localtime(c.consumed_at).strftime("%Y-%m-%d %H:%M"),
        })
    completed_orders = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .prefetch_related("bom__items__component", "bom__items__component__product", "bom__items__unit", "consumptions")
        .filter(status="completed")
        .order_by("-completed_at", "-created_at")[:200]
    )
    context = {
        "consumptions_data": rows,
        "completed_orders_data": [
            {
                "id": po.id,
                "code": po.code,
                "product": po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku,
                "status": po.status,
                "produced_qty": float(po.produced_quantity or 0),
                "uom": po.unit.symbol if po.unit else "",
                "consumption_recorded": po.consumptions.exists(),
                "standard_items": [
                    {
                        "sku": item.component.sku,
                        "name": item.component.product.name if item.component.product else item.component.sku,
                        "standard_qty": float(item.quantity or 0) * float(po.produced_quantity or 0),
                        "unit": item.unit.symbol if item.unit else "",
                    }
                    for item in po.bom.items.all()
                ],
            }
            for po in completed_orders
        ],
        "report_title": "Material Consumption",
    }
    return render(request, "lumra_pages/production/material_consumption.html", context)
```

### finished_goods_receipt
- File: `lumra_config/views/production_ops_views.py`:607
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def finished_goods_receipt(request):
    qs = (
        FinishedGoodsReceipt.objects
        .select_related("production_order", "finished_variant", "finished_variant__product", "location")
        .order_by("-received_at")[:500]
    )
    rows = []
    for r in qs:
        rows.append({
            "id": r.id,
            "po_code": r.production_order.code,
            "sku": r.finished_variant.sku,
            "product": r.finished_variant.product.name if r.finished_variant.product else r.finished_variant.sku,
            "location": r.location.name,
            "quantity": float(r.quantity_received),
            "received_at": localtime(r.received_at).strftime("%Y-%m-%d %H:%M"),
        })
    completed_orders = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .prefetch_related("receipts")
        .filter(status="completed")
        .order_by("-completed_at", "-created_at")[:200]
    )
    locations = Location.objects.order_by("name")[:500]
    context = {
        "receipts_data": rows,
        "completed_orders_data": [
            {
                "id": po.id,
                "code": po.code,
                "product": po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku,
                "sku": po.bom.finished_variant.sku,
                "target_qty": float(po.target_quantity or 0),
                "produced_qty": float(po.produced_quantity or 0),
                "uom": po.unit.symbol if po.unit else "",
                "receipt_recorded": po.receipts.exists(),
            }
            for po in completed_orders
        ],
        "locations_data": [{"id": location.id, "name": location.name} for location in locations],
        "report_title": "Finished Goods Receipt",
    }
    return render(request, "lumra_pages/production/finished_goods_receipt.html", context)
```

### production_waste
- File: `lumra_config/views/production_ops_views.py`:661
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def production_waste(request):
    qs = (
        ProductionWasteRecord.objects
        .select_related("production_order", "component", "component__product", "unit")
        .order_by("-recorded_at")[:500]
    )
    rows = []
    for w in qs:
        rows.append({
            "id": w.id,
            "po_code": w.production_order.code,
            "waste_type": w.waste_type,
            "sku": w.component.sku if w.component else "",
            "name": w.component.product.name if (w.component and w.component.product) else (w.component.sku if w.component else ""),
            "quantity": float(w.quantity),
            "unit": w.unit.symbol if w.unit else "",
            "recorded_at": localtime(w.recorded_at).strftime("%Y-%m-%d %H:%M"),
        })
    completed_orders = (
        ProductionOrder.objects
        .select_related("bom", "bom__finished_variant", "bom__finished_variant__product", "unit")
        .filter(status="completed")
        .order_by("-completed_at", "-created_at")[:200]
    )
    variants = ProductVariant.objects.select_related("product").order_by("sku")[:3000]
    units = Unit.objects.order_by("symbol")
    context = {
        "waste_data": rows,
        "completed_orders_data": [
            {
                "id": po.id,
                "code": po.code,
                "product": po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku,
                "produced_qty": float(po.produced_quantity or 0),
                "uom": po.unit.symbol if po.unit else "",
            }
            for po in completed_orders
        ],
        "variants_data": [
            {
                "id": variant.id,
                "sku": variant.sku,
                "name": variant.product.name if variant.product else variant.sku,
                "price_buy": float(variant.price_buy or 0),
            }
            for variant in variants
        ],
        "units_data": [{"id": unit.id, "symbol": unit.symbol} for unit in units],
        "report_title": "Production Waste",
    }
    return render(request, "lumra_pages/production/production_waste.html", context)
```

### production_costing
- File: `lumra_config/views/production_ops_views.py`:698
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def production_costing(request):
    """
    Placeholder costing page. Real costing should aggregate:
    - consumption * latest cost
    - waste
    - overhead allocations
    """
    qs = ProductionOrder.objects.select_related("bom", "bom__finished_variant", "bom__finished_variant__product").order_by("-created_at")[:200]
    rows = []
    for po in qs:
        product_name = po.bom.finished_variant.product.name if po.bom.finished_variant.product else po.bom.finished_variant.sku
        standard_material_cost = float(sum((item.quantity or 0) * (item.component.price_buy or 0) for item in po.bom.items.all())) * float(po.target_quantity or 0)
        actual_material_cost = float(sum((consumption.quantity or 0) * (consumption.component.price_buy or 0) for consumption in po.consumptions.select_related("component").all()))
        waste_value = float(sum((waste.quantity or 0) * (waste.component.price_buy or 0) for waste in po.wastes.select_related("component").all() if waste.component))
        target_qty = float(po.target_quantity or 0)
        produced_qty = float(po.produced_quantity or 0)
        rows.append({
            "id": po.id,
            "code": po.code,
            "product": product_name,
            "status": po.status,
            "target_qty": target_qty,
            "produced_qty": produced_qty,
            "standard_material_cost": standard_material_cost,
            "actual_material_cost": actual_material_cost,
            "waste_value": waste_value,
            "variance": actual_material_cost - standard_material_cost,
            "scheduled_date": po.scheduled_date.isoformat() if po.scheduled_date else "",
            "completed_at": localtime(po.completed_at).strftime("%Y-%m-%d %H:%M") if po.completed_at else "",
            "completion_pct": min(round((produced_qty / target_qty) * 100), 100) if target_qty > 0 else 0,
            "is_overproduced": produced_qty > target_qty if target_qty > 0 else False,
        })
    context = {"orders_data": rows, "report_title": "Production Costing"}
    return render(request, "lumra_pages/production/production_costing.html", context)
```

### rnd_list
- File: `lumra_config/views/production_ops_views.py`:724
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def rnd_list(request):
    records = _load_rnd_records(request)
    rows = []
    for record in records:
        items = record.get("items") or []
        trials = record.get("trials") or []
        rows.append({
            "id": record["id"],
            "name": record.get("name") or record.get("code") or f"RND-{record['id']}",
            "code": record.get("code") or f"RND-{record['id']}",
            "status": record.get("status") or "idea",
            "created_by": record.get("created_by") or "-",
            "trial_count": len(trials),
            "ingredient_count": len(items),
            "success_probability": float(record.get("success_probability") or 0),
            "estimated_cost": float(sum(float(item.get("estimated_cost") or 0) for item in items)),
        })
    context = {"rnds_data": rows, "report_title": "Lab RnD"}
    return render(request, "lumra_pages/production/rnd_list.html", context)
```

### rnd_form
- File: `lumra_config/views/production_ops_views.py`:796
- Decorators: `login_required`, `require_http_methods`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def rnd_form(request):
    records = _load_rnd_records(request)
    edit_id = request.GET.get("edit")
    rnd = _find_rnd_record(records, edit_id) if edit_id else None

    if request.method == "POST":
        payload, err = _parse_json_body(request)
        if err:
            return err

        items = payload.get("items") or []
        if not isinstance(items, list):
            return JsonResponse({"success": False, "error": "Items harus berupa list."}, status=400)

        next_id = max([int(r["id"]) for r in records] + [0]) + 1
        obj = rnd or {"id": next_id, "created_at": localtime().strftime("%Y-%m-%d %H:%M"), "bom_id": None, "trials": []}
        obj["name"] = str(payload.get("name", "")).strip()
        obj["code"] = obj.get("code") or f"RND-{obj['id']:03d}"
        obj["target_sku"] = payload.get("target_sku") or ""
        obj["category"] = payload.get("category") or "other"
        obj["created_by"] = str(payload.get("created_by") or request.user.get_username()).strip()
        obj["description"] = str(payload.get("description") or "").strip()
        obj["tags"] = payload.get("tags") or []
        obj["based_on"] = payload.get("based_on") or ""
        obj["planned_trials"] = int(payload.get("planned_trials") or 1)
        obj["notes"] = str(payload.get("notes") or "").strip()
        obj["hypothesis_notes"] = str(payload.get("hypothesis_notes") or "").strip()
        obj["hypothesis"] = payload.get("hypothesis") or {}
        obj["success_probability"] = float(payload.get("success_probability") or 0)
        obj["probability_reason"] = str(payload.get("probability_reason") or "").strip()
        obj["status"] = payload.get("status") or obj.get("status") or "idea"
        obj["items"] = [
            {
                "name": str(item.get("name") or item.get("sku") or "").strip(),
                "sku": str(item.get("sku") or item.get("name") or "").strip(),
                "component_variant_id": item.get("component_variant_id"),
                "quantity": float(item.get("quantity") or 0),
                "unit": next((u.symbol for u in Unit.objects.filter(pk=item.get("unit_id"))[:1]), "") if item.get("unit_id") else "",
                "estimated_cost": float(item.get("estimated_cost") or 0),
            }
            for item in items
            if item.get("name") or item.get("sku")
        ]

        if rnd:
            for idx, record in enumerate(records):
                if int(record["id"]) == int(obj["id"]):
                    records[idx] = obj
                    break
        else:
            records.append(obj)

        _save_rnd_records(request, records)
        return JsonResponse({"success": True, "id": obj["id"]})

    variants = ProductVariant.objects.select_related("product").order_by("sku")[:3000]
    units = Unit.objects.order_by("symbol")
    context = {
        "variants_data": [
            {"id": v.id, "sku": v.sku, "name": v.product.name if v.product else v.sku, "price_buy": float(v.price_buy or 0)}
            for v in variants
        ],
        "units_data": [{"id": u.id, "symbol": u.symbol, "name": u.name} for u in units],
        "rnd_data": rnd or {},
        "submit_url": request.path + (f"?edit={edit_id}" if edit_id else ""),
        "report_title": "RnD Form",
    }
    return render(request, "lumra_pages/production/rnd_form.html", context)
```

### rnd_detail
- File: `lumra_config/views/production_ops_views.py`:804
- Decorators: `login_required`
- Context keys eksplisit: `report_title`, `rnd_data`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def rnd_detail(request, pk):
    records = _load_rnd_records(request)
    rnd = _find_rnd_record(records, pk)
    if not rnd:
        return render(request, "lumra_pages/production/rnd_detail.html", {"rnd_data": {}, "report_title": "RnD Detail"})
    context = {"rnd_data": rnd, "report_title": f"RnD Detail - {rnd.get('name') or rnd.get('code')}"}
    return render(request, "lumra_pages/production/rnd_detail.html", context)
```

### rnd_detail
- File: `lumra_config/views/production_ops_views.py`:806
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def rnd_detail(request, pk):
    records = _load_rnd_records(request)
    rnd = _find_rnd_record(records, pk)
    if not rnd:
        return render(request, "lumra_pages/production/rnd_detail.html", {"rnd_data": {}, "report_title": "RnD Detail"})
    context = {"rnd_data": rnd, "report_title": f"RnD Detail - {rnd.get('name') or rnd.get('code')}"}
    return render(request, "lumra_pages/production/rnd_detail.html", context)
```

### rnd_trial_new
- File: `lumra_config/views/production_ops_views.py`:838
- Decorators: `login_required`
- Context keys eksplisit: `report_title`, `rnd_data`, `submit_url`, `units_data`, `variants_data`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def rnd_trial_new(request, pk):
    return render(request, "lumra_pages/production/rnd_form.html", {
        "variants_data": [],
        "units_data": [],
        "rnd_data": {},
        "submit_url": "/rnd/form/",
        "report_title": f"Trial Baru RnD {pk}",
    })
```

### recipe_list
- File: `lumra_config/views/production_views.py`:77
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### recipe_list
- File: `lumra_config/views/production_views.py`:110
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### recipe_form
- File: `lumra_config/views/production_views.py`:210
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
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
```

### recipe_detail
- File: `lumra_config/views/production_views.py`:269
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
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
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
