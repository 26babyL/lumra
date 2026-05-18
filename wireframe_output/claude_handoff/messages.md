# Claude Handoff: messages

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 6
Jumlah view terkait: 7

## Template Scope

### lumra_pages/messages/broadcast.html
- File: `lumra_config/templates/lumra_pages/messages/broadcast.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): {{ form_title }}
  - [ FORM ]: {% csrf_token %} {% if form_errors %} {{ form_errors }} {% endif %} {% for field…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Simpan: Simpan

### lumra_pages/messages/compose.html
- File: `lumra_config/templates/lumra_pages/messages/compose.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=23, interactive=3, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Pesan Pribadi / Tulis Pesan
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Tulis Pesan Baru
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: {# ── LEFT: Form Fields ── #} {# Penerima ── #} Kepada {# Chip selector — lebih…
  - [ FORM ]: {# ── LEFT: Form Fields ── #} {# Penerima ── #} Kepada {# Chip selector — lebih…
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/messages/inbox.html
- File: `lumra_config/templates/lumra_pages/messages/inbox.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=30, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Pesan Pribadi
  - HEADING (H1): Pesan Pribadi
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - CARD: Total
  - CARD: Belum Dibaca
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/messages/message_templates.html
- File: `lumra_config/templates/lumra_pages/messages/message_templates.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ page_title }}
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Cari...: Cari...
  - BUTTON: [icon]: 
  - SEARCH BAR: 

### lumra_pages/messages/notification.html
- File: `lumra_config/templates/lumra_pages/messages/notification.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=71, interactive=25, issues=4, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Inbox
  - HEADING (H1): Inbox
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
  - BUTTON: [icon]: 
  - BUTTON: [icon]: 
- Temuan reverse:
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='icon-btn'
  - [warning] empty_button: Tombol tanpa teks/aria-label: <button> id='' class='icon-btn'
  - [info] input_no_label: Input tanpa label/placeholder: <input> id='' class='mt-1 w-3.5 h-3.5 accent-emerald-500 rounded cursor'
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/messages/message_detail.html
- File: `lumra_config/templates/lumra_pages/messages/message_detail.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=16, interactive=3, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: Dashboard / Pesan Pribadi /
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H2): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
  - CALENDAR: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### notification_view
- File: `lumra_config/views/dashboard_views.py`:490
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def notification_view(request):
    notifications = []

    context = {
        "notifications": notifications,
        "notifications_json": json.dumps(
            [
                {
                    "id":           n.get("id", ""),
                    "type":         n.get("type", "system"),
                    "title":        n.get("title", ""),
                    "message":      n.get("message", ""),
                    "full_message": n.get("full_message", ""),
                    "action_url":   n.get("action_url", ""),
                    "timestamp":    n.get("timestamp", timezone.now().isoformat()),
                    "isRead":       n.get("isRead", False),
                }
                for n in notifications
            ],
            cls=DjangoJSONEncoder,
        ),
    }
    return render(request, "lumra_pages/messages/notification.html", context)
```

### inbox
- File: `lumra_config/views/messages_views.py`:20
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def inbox(request):
    """User message inbox."""
    context = {}
    return render(request, 'lumra_pages/messages/inbox.html', context)
```

### message_detail
- File: `lumra_config/views/messages_views.py`:29
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def message_detail(request, pk):
    """View individual message."""
    context = {}
    return render(request, 'lumra_pages/messages/message_detail.html', context)
```

### compose_message
- File: `lumra_config/views/messages_views.py`:38
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def compose_message(request):
    """Compose new message."""
    context = {}
    return render(request, 'lumra_pages/messages/compose.html', context)
```

### notification_center
- File: `lumra_config/views/messages_views.py`:47
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def notification_center(request):
    """Notification center."""
    context = {}
    return render(request, 'lumra_pages/messages/notification.html', context)
```

### broadcast_message
- File: `lumra_config/views/messages_views.py`:56
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def broadcast_message(request):
    """Send broadcast message (admin only)."""
    context = {}
    return render(request, 'lumra_pages/messages/broadcast.html', context)
```

### message_templates
- File: `lumra_config/views/messages_views.py`:65
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def message_templates(request):
    """Message templates management."""
    context = {}
    return render(request, 'lumra_pages/messages/message_templates.html', context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
