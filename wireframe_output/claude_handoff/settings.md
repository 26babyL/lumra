# Claude Handoff: settings

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 21
Jumlah view terkait: 32

## Template Scope

### lumra_pages/settings/about.html
- File: `lumra_config/templates/lumra_pages/settings/about.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=73, interactive=3, issues=0, scroll_nesting=0
- Komponen utama:
  - HERO / BANNER: Lumra ERP · Emerald Odyssey Bukan Sekadar Software. Ini Legacy. ERP lain dibuat…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HERO / BANNER: Lumra ERP · Emerald Odyssey
  - HERO / BANNER: Bukan Sekadar Software. Ini Legacy.
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HERO / BANNER: PostgreSQL Native
  - HERO / BANNER: Multi-Tenant Secure
  - HERO / BANNER: 118k+ SKU Tested

### lumra_pages/settings/business_feature_matrix.html
- File: `lumra_config/templates/lumra_pages/settings/business_feature_matrix.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=17, interactive=3, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {% if not can_access_settings %} Anda tidak memiliki izin…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): V-Series Engine
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Batalkan: Batalkan
  - BUTTON: [icon]: 
  - HERO / BANNER: Terkunci di paket ini: + lainnya Upgrade
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/business_profile.html
- File: `lumra_config/templates/lumra_pages/settings/business_profile.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=42, interactive=25, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {{ company_json|json_script:"company-data" }} {{ perms_js…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Profil Perusahaan
  - BADGE / STATUS: Belum disimpan
  - CARD: Identitas Perusahaan * Wajib diisi Nama Perusahaan / Brand * Nama ini tampil di…
  - CARD: Identitas Perusahaan * Wajib diisi
  - INPUT [text] PT. Retail Nusantara / CoffeeShop Paradise: PT. Retail Nusantara / CoffeeShop Paradise
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/business_settings.html
- File: `lumra_config/templates/lumra_pages/settings/business_settings.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=57, interactive=20, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {{ settings_json|json_script:"settings-data" }} {{ audit_…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HERO / BANNER: Current Subscription Active until: SKU Limit / Used Cabang Aktif / Upgrade Plan…
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H2): 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BADGE / STATUS: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/contact.html
- File: `lumra_config/templates/lumra_pages/settings/contact.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=26, interactive=11, issues=0, scroll_nesting=0
- Komponen utama:
  - HEADING (H1): 📞 Contact Us
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - HEADING (H2): Send Message
  - [ FORM ]: {% csrf_token %} Name * Email * Subject * Message * Send Message
  - INPUT [text] Your name: Your name
  - INPUT [email] Your email: Your email
  - INPUT [text] Subject: Subject
  - INPUT [textarea] Your message: Your message

### lumra_pages/settings/search.html
- File: `lumra_config/templates/lumra_pages/settings/search.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=38, interactive=9, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (column)]: 
  - HEADING (H1): 🔍 Search Results
  - [ FORM ]: Search
  - INPUT [text] Search products, customers, orders...: Search products, customers, orders...
  - BUTTON: Search: Search
  - SEARCH BAR: 
  - HEADING (H2): Filter Results
  - LAYOUT CONTAINER [FLEX (column)]: 

### lumra_pages/settings/settings.html
- File: `lumra_config/templates/lumra_pages/settings/settings.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=24, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Pusat Pengaturan
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: Users & Roles Kelola user aktif dan peran akses tim. Permission Matrix Tinjau ha…
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H2): Users & Roles

### lumra_pages/settings/system_status.html
- File: `lumra_config/templates/lumra_pages/settings/system_status.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=21, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): System Status
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: CPU Usage %
  - CARD: Memory Usage %
  - CARD: Disk Usage %
  - CARD: Database

### lumra_pages/settings/api_keys.html
- File: `lumra_config/templates/lumra_pages/settings/api_keys.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=16, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: System / Integrations
  - HEADING (H1): API Keys
  - BUTTON: Generate New Key: Generate New Key
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/backup_restore.html
- File: `lumra_config/templates/lumra_pages/settings/backup_restore.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=19, interactive=5, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Backup Otomatis Frekuensi Harian Mingguan Bulanan Jadwal Berikutnya Backup Sekar…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H3): Backup Otomatis
  - INPUT [checkbox] autoBackup.enabled: autoBackup.enabled
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [select] autoBackup.frequency: autoBackup.frequency
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/business_form_general.html
- File: `lumra_config/templates/lumra_pages/settings/business_form_general.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=50, interactive=24, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} {{ company_json|json_script:"company-data" }} {# permissi…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Profil Perusahaan
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/email_settings.html
- File: `lumra_config/templates/lumra_pages/settings/email_settings.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=24, interactive=3, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - CARD: Konfigurasi SMTP Status Server: SMTP Host Port Encryption TLS (Recommended) SSL…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Konfigurasi SMTP
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ FORM ]: SMTP Host Port Encryption TLS (Recommended) SSL None Username Password Pengirim…
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/notification_settings.html
- File: `lumra_config/templates/lumra_pages/settings/notification_settings.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=27, interactive=8, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Pengaturan Notifikasi
  - BUTTON: Simpan Preferensi: Simpan Preferensi
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Inventory Stok Menipis Stok di bawah minimum order. Produk Kedaluwarsa Masa paka…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/numbering_settings.html
- File: `lumra_config/templates/lumra_pages/settings/numbering_settings.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=30, interactive=8, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Pengaturan Nomor Otomatis
  - BUTTON: Simpan Perubahan: Simpan Perubahan
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Konfigurasi Umum Faktur (Invoice) Prefix Digit Purchase Order (PO) Prefix Digit…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H2): Konfigurasi Umum
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/permission_matrix.html
- File: `lumra_config/templates/lumra_pages/settings/permission_matrix.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=12, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Permission Matrix
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: Filter Modul: Filter Modul
  - BUTTON: Cetak: Cetak
  - CARD: Role / Modul Dashboard Inventory Purchasing Production Sales (POS) Finance HR &…
  - [ TABLE ]: Role / Modul Dashboard Inventory Purchasing Production Sales (POS) Finance HR &…
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/profile.html
- File: `lumra_config/templates/lumra_pages/settings/profile.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=76, interactive=23, issues=1, scroll_nesting=0
- Komponen utama:
  - METRIC CARD: #} {% block content %} Administrator Profile Personal Identity Kelola akun, pref…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Personal Identity
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - LAYOUT CONTAINER [FLEX (column)]: 
  - IMAGE [Avatar]: Avatar
  - LAYOUT CONTAINER [FLEX (row)]: 
  - BUTTON: [icon]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/roles.html
- File: `lumra_config/templates/lumra_pages/settings/roles.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=14, interactive=2, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - [ NAVIGATION BAR ]: System / Roles & Access
  - HEADING (H1): Manajemen Roles
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: 
  - LAYOUT CONTAINER [FLEX (row)]: 
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/user_list.html
- File: `lumra_config/templates/lumra_pages/settings/user_list.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 2
- Reverse stats: components=0, interactive=0, issues=0, scroll_nesting=0

### lumra_pages/settings/user_roles_permissions.html
- File: `lumra_config/templates/lumra_pages/settings/user_roles_permissions.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=61, interactive=9, issues=1, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [GRID 2 cols]: 
  - METRIC CARD: Total Role {{ total_roles|default:5 }} Terdefinisi
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Total Permission {{ total_permissions|default:34 }} Konfigurasi akses
  - LAYOUT CONTAINER [FLEX (row)]: 
  - METRIC CARD: 
  - METRIC CARD: Sensitive Modules 3 🔒 Restricted
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

### lumra_pages/settings/users.html
- File: `lumra_config/templates/lumra_pages/settings/users.html`
- Batch: `batch_2_listing`
- Alasan batch: Listing atau dashboard ringan dengan context sederhana.
- Complexity: 3
- Reverse stats: components=14, interactive=1, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Users & Roles
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [GRID 1 cols]: 
  - CARD: Total User {{ total_users|default:0 }}
  - CARD: Aktif {{ online_count|default:0 }}
  - CARD: Admin Role {{ admin_count|default:0 }}

### lumra_pages/settings/role_form.html
- File: `lumra_config/templates/lumra_pages/settings/role_form.html`
- Batch: `batch_3_forms`
- Alasan batch: Form atau halaman detail dengan context/logika menengah.
- Complexity: 5
- Reverse stats: components=26, interactive=8, issues=1, scroll_nesting=0
- Komponen utama:
  - ALPINE COMPONENT [roleFormApp()]: Konfigurasi Role Tentukan izin akses untuk jabatan ini. Bata…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Konfigurasi Role
  - CARD: Nama Role Kode Role Deskripsi Simpan Role Inventory Buat / Edit Produk Hapus Pro…
  - INPUT FIELD: 
  - INPUT FIELD: 
  - INPUT FIELD: 
  - BUTTON: Simpan Role: Simpan Role
- Temuan reverse:
  - [info] alpine_xcloak: x-cloak ditemukan — pastikan CSS [x-cloak]{display:none} ada di base template

## View Scope

### profile_view
- File: `lumra_config/views/auth_views.py`:69
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def profile_view(request):
    """
    Halaman profile user.
    """

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        "user_profile": profile,
        "report_title": "My Profile",
    }

    return render(request, "lumra_pages/settings/profile.html", context)
```

### settings_view
- File: `lumra_config/views/auth_views.py`:82
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def settings_view(request):
    """
    Halaman settings utama.
    """

    return render(request, "lumra_pages/settings/settings.html")
```

### users_view
- File: `lumra_config/views/misc_views.py`:1522
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

### profile_view
- File: `lumra_config/views/misc_views.py`:1531
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def profile_view(request):
    """User profile page."""
    # FIX: get_or_create untuk menghindari RelatedObjectDoesNotExist jika profile belum ada
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    context = {"user_profile": profile}
    return render(request, "lumra_pages/settings/profile.html", context)
```

### settings_view
- File: `lumra_config/views/misc_views.py`:1536
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def settings_view(request):
    return render(request, "lumra_pages/settings/settings.html")
```

### system_status_view
- File: `lumra_config/views/misc_views.py`:1542
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def system_status_view(request):
    context = {"status": {}}
    return render(request, "lumra_pages/settings/system_status.html", context)
```

### business_settings_view
- File: `lumra_config/views/misc_views.py`:1562
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def business_settings_view(request):
    # the template expects several JSON blobs for Alpine;
    # provide empty defaults so the page still loads even if no data yet
    context = {
        "settings": {},
        "settings_json": "{}",
        "audit_json": "{}",
        "outlets_json": "[]",
    }

    # attach permissions so the template and its JS know whether the
    # current user is allowed to access / modify anything on this page.
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)

    return render(request, "lumra_pages/settings/business_settings.html", context)
```

### business_feature_matrix_view
- File: `lumra_config/views/misc_views.py`:1581
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def business_feature_matrix_view(request):
    """Blank endpoint for the feature‑matrix page.

    The ability to view or edit the feature matrix is controlled by the same
    ``sys_config`` permission used by the main settings screen.  Passing the
    permissions object into the template allows the frontend to make
    decisions such as disabling the save button or hiding the upgrade banner
    entirely for unauthorized users.
    """
    context = {"features_json": "[]"}
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)
    return render(request, "lumra_pages/settings/business_feature_matrix.html", context)
```

### business_form_general_view
- File: `lumra_config/views/misc_views.py`:1596
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def business_form_general_view(request):
    """Company profile form page.

    Access restricted by ``sys_config`` permission; unauthorized users will
    see a simple notice instead of the editable form.  We still send a
    minimal JSON payload so the Alpine component is safe to initialize.
    """
    context = {"profile_json": "{}"}
    perms = get_user_permissions(request.user)
    context["perms_json"] = json.dumps(perms)
    context["can_access_settings"] = perms.get("sys_config", False)
    return render(request, "lumra_pages/settings/business_form_general.html", context)
```

### user_roles_permissions_view
- File: `lumra_config/views/misc_views.py`:1603
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def user_roles_permissions_view(request):
    """Simple placeholder for roles & permissions screen."""
    context = {"roles_json": "[]", "perms_json": "[]"}
    return render(request, "lumra_pages/settings/user_roles_permissions.html", context)
```

### about_view
- File: `lumra_config/views/misc_views.py`:1640
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def about_view(request):
    context = {
        "founded_year": 2024,
        "clients_count": 100,
    }
    return render(request, "lumra_pages/settings/about.html", context)
```

### contact_view
- File: `lumra_config/views/misc_views.py`:1644
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def contact_view(request):
    return render(request, "lumra_pages/settings/contact.html", {})
```

### search_view
- File: `lumra_config/views/misc_views.py`:1650
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def search_view(request):
    query = request.GET.get("q", "").strip()
    context = {"query": query}
    return render(request, "lumra_pages/settings/search.html", context)
```

### users_list
- File: `lumra_config/views/settings_views.py`:311
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def users_list(request):
    users = User.objects.order_by("username")
    users_json = _serialize_users(users)
    context = {"users": users, "users_json": json.dumps(users_json), **_user_summary(users)}
    return render(request, "lumra_pages/settings/users.html", context)
```

### user_list
- File: `lumra_config/views/settings_views.py`:319
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def user_list(request):
    users = User.objects.order_by("username")
    users_json = _serialize_users(users)
    context = {"users": users, "users_json": json.dumps(users_json), **_user_summary(users)}
    return render(request, "lumra_pages/settings/user_list.html", context)
```

### roles
- File: `lumra_config/views/settings_views.py`:330
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def roles(request):
    _seed_role_overview()
    role_qs = Role.objects.annotate(user_count=Count("user_assignments")).order_by("name")
    context = {
        "roles": role_qs,
        "total_roles": role_qs.count(),
    }
    return render(request, "lumra_pages/settings/roles.html", context)
```

### role_form
- File: `lumra_config/views/settings_views.py`:355
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=True

```python
def role_form(request, pk=None):
    _seed_permissions()
    role = Role.objects.filter(pk=pk).first() if pk else None
    permission_map = {}
    if role:
        permission_map = {item.module_key: item for item in role.permissions.all()}
    modules = []
    for module_key, module_name in DEFAULT_MODULES:
        permission = permission_map.get(module_key)
        modules.append(
            {
                "key": module_key,
                "name": module_name,
                "permission": permission,
            }
        )
    context = {
        "role": role,
        "modules": modules,
        "is_edit": bool(role),
    }
    return render(request, "lumra_pages/settings/role_form.html", context)
```

### user_roles_permissions
- File: `lumra_config/views/settings_views.py`:366
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def user_roles_permissions(request):
    _seed_role_overview()
    role_assignments = UserRole.objects.select_related("user", "role").order_by("user__username", "role__name")
    context = {
        "role_assignments": role_assignments,
        "roles": Role.objects.order_by("name"),
    }
    return render(request, "lumra_pages/settings/user_roles_permissions.html", context)
```

### permission_matrix
- File: `lumra_config/views/settings_views.py`:382
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def permission_matrix(request):
    _seed_permissions()
    roles_qs = Role.objects.prefetch_related("permissions").order_by("name")
    matrix_rows = []
    for role in roles_qs:
        permissions = {perm.module_key: perm.access_level for perm in role.permissions.all()}
        matrix_rows.append({"role": role, "permissions": permissions})
    context = {
        "modules": DEFAULT_MODULES,
        "matrix_rows": matrix_rows,
        "roles": roles_qs,
    }
    return render(request, "lumra_pages/settings/permission_matrix.html", context)
```

### business_profile
- File: `lumra_config/views/settings_views.py`:387
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def business_profile(request):
    return render(request, "lumra_pages/settings/business_profile.html", _business_context(request))
```

### business_settings
- File: `lumra_config/views/settings_views.py`:392
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def business_settings(request):
    return render(request, "lumra_pages/settings/business_settings.html", _business_context(request))
```

### business_form_general
- File: `lumra_config/views/settings_views.py`:397
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def business_form_general(request):
    return render(request, "lumra_pages/settings/business_form_general.html", _business_context(request))
```

### business_feature_matrix
- File: `lumra_config/views/settings_views.py`:402
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def business_feature_matrix(request):
    return render(request, "lumra_pages/settings/business_feature_matrix.html", _business_context(request))
```

### system_status
- File: `lumra_config/views/settings_views.py`:407
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def system_status(request):
    return render(request, "lumra_pages/settings/system_status.html", _system_status_context())
```

### email_settings
- File: `lumra_config/views/settings_views.py`:416
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def email_settings(request):
    setting = EmailSetting.objects.order_by("-updated_at").first()
    context = {
        "email_setting": setting,
    }
    return render(request, "lumra_pages/settings/email_settings.html", context)
```

### notification_settings
- File: `lumra_config/views/settings_views.py`:426
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def notification_settings(request):
    _seed_notification_settings()
    settings_qs = NotificationSetting.objects.order_by("label")
    context = {
        "notification_settings": settings_qs,
    }
    return render(request, "lumra_pages/settings/notification_settings.html", context)
```

### numbering_settings
- File: `lumra_config/views/settings_views.py`:437
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def numbering_settings(request):
    _seed_numbering_sequences()
    sequences = NumberingSequence.objects.order_by("name")
    context = {
        "numbering_sequences": sequences,
        "numbering_preview": {sequence.key: _numbering_preview(sequence) for sequence in sequences},
    }
    return render(request, "lumra_pages/settings/numbering_settings.html", context)
```

### backup_restore
- File: `lumra_config/views/settings_views.py`:448
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def backup_restore(request):
    _seed_backups()
    backups = BackupRecord.objects.order_by("-created_at")
    context = {
        "backups": backups,
        "latest_backup": backups.first(),
    }
    return render(request, "lumra_pages/settings/backup_restore.html", context)
```

### api_keys
- File: `lumra_config/views/settings_views.py`:458
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=True, json=False, branching=False

```python
def api_keys(request):
    _seed_api_keys()
    keys = APIKey.objects.order_by("-created_at")
    context = {
        "api_keys": keys,
    }
    return render(request, "lumra_pages/settings/api_keys.html", context)
```

### about
- File: `lumra_config/views/settings_views.py`:463
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def about(request):
    return render(request, "lumra_pages/settings/about.html", {})
```

### contact
- File: `lumra_config/views/settings_views.py`:468
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def contact(request):
    return render(request, "lumra_pages/settings/contact.html", {})
```

### search
- File: `lumra_config/views/settings_views.py`:475
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def search(request):
    query = request.GET.get("q", "")
    context = {"query": query}
    return render(request, "lumra_pages/settings/search.html", context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
