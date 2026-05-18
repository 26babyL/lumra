# Claude Handoff: onboarding

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 5
Jumlah view terkait: 5

## Template Scope

### lumra_pages/onboarding/step_business.html
- File: `lumra_config/templates/lumra_pages/onboarding/step_business.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/onboarding/step_category.html
- File: `lumra_config/templates/lumra_pages/onboarding/step_category.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/onboarding/step_complete.html
- File: `lumra_config/templates/lumra_pages/onboarding/step_complete.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=2, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ dashboard_title }}
  - LAYOUT CONTAINER [GRID 1 cols]: 

### lumra_pages/onboarding/step_location.html
- File: `lumra_config/templates/lumra_pages/onboarding/step_location.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/onboarding/welcome.html
- File: `lumra_config/templates/lumra_pages/onboarding/welcome.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=2, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ dashboard_title }}
  - LAYOUT CONTAINER [GRID 1 cols]: 

## View Scope

### onboarding_welcome
- File: `lumra_config/views/onboarding_views.py`:18
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def onboarding_welcome(request):
    """Onboarding step: Welcome screen."""
    context = {}
    return render(request, 'lumra_pages/onboarding/welcome.html', context)
```

### onboarding_step_business
- File: `lumra_config/views/onboarding_views.py`:25
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def onboarding_step_business(request):
    """Onboarding step: Business Information."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_business.html', context)
```

### onboarding_step_location
- File: `lumra_config/views/onboarding_views.py`:32
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def onboarding_step_location(request):
    """Onboarding step: Location/Warehouse setup."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_location.html', context)
```

### onboarding_step_category
- File: `lumra_config/views/onboarding_views.py`:39
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def onboarding_step_category(request):
    """Onboarding step: Product Categories."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_category.html', context)
```

### onboarding_step_complete
- File: `lumra_config/views/onboarding_views.py`:46
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def onboarding_step_complete(request):
    """Onboarding step: Completion/Success screen."""
    context = {}
    return render(request, 'lumra_pages/onboarding/step_complete.html', context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
