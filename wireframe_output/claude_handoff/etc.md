# Claude Handoff: etc

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 5
Jumlah view terkait: 1

## Template Scope

### lumra_pages/etc/error_404.html
- File: `lumra_config/templates/lumra_pages/etc/error_404.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=5, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - SEARCH BAR: 
  - HEADING (H1): Page Not Found
  - [ FORM ]: 🔍
  - INPUT [text] Search...: Search...
  - BUTTON: 🔍: 🔍

### lumra_pages/etc/error_500.html
- File: `lumra_config/templates/lumra_pages/etc/error_500.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=1, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): Oops! Something went wrong

### lumra_pages/etc/error_maintenance.html
- File: `lumra_config/templates/lumra_pages/etc/error_maintenance.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=2, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): Maaf, Kami Sedang Bermasalah
  - BUTTON: Kembali ke Beranda: Kembali ke Beranda

### lumra_pages/etc/error_session_expired.html
- File: `lumra_config/templates/lumra_pages/etc/error_session_expired.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=4, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - CARD: Sesi Anda Berakhir Demi alasan keamanan, sesi login Anda telah berakhir. Silakan…
  - HEADING (H2): Sesi Anda Berakhir
  - [ FORM ]: Login Kembali
  - BUTTON (Primary): Login Kembali

### lumra_pages/etc/error_403.html
- File: `lumra_config/templates/lumra_pages/etc/error_403.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=2, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): 403

## View Scope

### users_view
- File: `lumra_config/views/misc_views.py`:1517
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def users_view(request):
    """Manajemen pengguna — staff/admin only."""
    # FIX: gunakan redirect ke 403 page, bukan render langsung (status code tetap 200 di versi lama)
    if not request.user.is_staff:
        return render(request, "lumra_pages/etc/error_403.html", status=403)

    # FIX: pindahkan import ke atas file — import di dalam fungsi hanya untuk menghindari circular import
    users = User.objects.select_related("userprofile").order_by("username")
    context = {"users": users}
    return render(request, "lumra_pages/settings/users.html", context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
