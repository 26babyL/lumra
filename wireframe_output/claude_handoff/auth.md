# Claude Handoff: auth

Tujuan:
Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.

Aturan kerja untuk Claude:
- Kerjakan hanya dalam lingkup modul ini.
- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.
- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.
- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.
- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.

Jumlah template: 8
Jumlah view terkait: 8

## Template Scope

### lumra_pages/auth/forgot_password.html
- File: `lumra_config/templates/lumra_pages/auth/forgot_password.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=5, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Lupa Password?
  - [ FORM ]: {% csrf_token %} {% if messages %} {% for message in messages %} {{ message }} {…
  - INPUT [email] nama@email.com: nama@email.com
  - BUTTON: Kirim Link Reset: Kirim Link Reset

### lumra_pages/auth/lock_screen.html
- File: `lumra_config/templates/lumra_pages/auth/lock_screen.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=2, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): {{ request.user.get_full_name }}
  - [ FORM ]: {% csrf_token %} Masukkan password untuk membuka kunci {% if error %} {{ error }…
  - INPUT [password] ••••••••: ••••••••
  - BUTTON: Buka Kunci: Buka Kunci

### lumra_pages/auth/login.html
- File: `lumra_config/templates/lumra_pages/auth/login.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 1
- Reverse stats: components=16, interactive=6, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H2): Selamat Datang Kembali
  - [ FORM ]: {% csrf_token %} {% if error %} {{ error }} {% endif %} Username Password Ingat…
  - LAYOUT CONTAINER [FLEX (row)]: 
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] Masukkan username: Masukkan username
  - LAYOUT CONTAINER [FLEX (row)]: 

### lumra_pages/auth/register.html
- File: `lumra_config/templates/lumra_pages/auth/register.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=0, interactive=0, issues=0, scroll_nesting=0

### lumra_pages/auth/reset_password.html
- File: `lumra_config/templates/lumra_pages/auth/reset_password.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=6, interactive=3, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Reset Password
  - [ FORM ]: {% csrf_token %} {% if error %} {{ error }} {% endif %} Password Baru Konfirmasi…
  - INPUT [password] ••••••••: ••••••••
  - INPUT [password] ••••••••: ••••••••
  - BUTTON: Reset Password: Reset Password

### lumra_pages/auth/session_expired.html
- File: `lumra_config/templates/lumra_pages/auth/session_expired.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=2, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Sesi Expired

### lumra_pages/auth/two_factor.html
- File: `lumra_config/templates/lumra_pages/auth/two_factor.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=8, interactive=3, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): 2FA Setup
  - [ FORM ]: {% csrf_token %} Scan dengan authenticator app: {% if qr_code %} {% else %} {% e…
  - IMAGE [QR Code]: QR Code
  - LAYOUT CONTAINER [FLEX (row)]: 
  - INPUT [text] : 
  - INPUT [text] 000000: 000000
  - BUTTON: Aktifkan 2FA: Aktifkan 2FA

### lumra_pages/auth/verify_email.html
- File: `lumra_config/templates/lumra_pages/auth/verify_email.html`
- Batch: `batch_1_static`
- Alasan batch: Static page or light context, aman untuk mulai round-trip.
- Complexity: 0
- Reverse stats: components=2, interactive=0, issues=0, scroll_nesting=0
- Komponen utama:
  - LAYOUT CONTAINER [FLEX (row)]: 
  - HEADING (H1): Verifikasi Email

## View Scope

### login_view
- File: `lumra_config/views/auth_views.py`:31
- Context keys eksplisit: `error`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def login_view(request):
    """
    Login page untuk user Lumra.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")
        else:
            return render(
                request,
                "lumra_pages/auth/login.html",
                {"error": "Username atau password salah"}
            )

    return render(request, "lumra_pages/auth/login.html")
```

### login_view
- File: `lumra_config/views/auth_views.py`:37
- Signals: GET=False, POST=False, query_model=False, json=False, branching=True

```python
def login_view(request):
    """
    Login page untuk user Lumra.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")
        else:
            return render(
                request,
                "lumra_pages/auth/login.html",
                {"error": "Username atau password salah"}
            )

    return render(request, "lumra_pages/auth/login.html")
```

### forgot_password
- File: `lumra_config/views/auth_views.py`:94
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def forgot_password(request):
    """
    Forgot password request page.
    """
    context = {}
    return render(request, 'lumra_pages/auth/forgot_password.html', context)
```

### reset_password
- File: `lumra_config/views/auth_views.py`:106
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def reset_password(request, token=None):
    """
    Reset password with token.
    """
    context = {'token': token}
    return render(request, 'lumra_pages/auth/reset_password.html', context)
```

### two_factor_setup
- File: `lumra_config/views/auth_views.py`:119
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def two_factor_setup(request):
    """
    Two Factor Authentication setup page.
    """
    context = {}
    return render(request, 'lumra_pages/auth/two_factor.html', context)
```

### verify_email
- File: `lumra_config/views/auth_views.py`:131
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def verify_email(request, token=None):
    """
    Email verification page.
    """
    context = {'token': token}
    return render(request, 'lumra_pages/auth/verify_email.html', context)
```

### lock_screen
- File: `lumra_config/views/auth_views.py`:144
- Decorators: `login_required`
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def lock_screen(request):
    """
    Lock screen (session lock, requires re-auth).
    """
    context = {}
    return render(request, 'lumra_pages/auth/lock_screen.html', context)
```

### session_expired
- File: `lumra_config/views/auth_views.py`:156
- Signals: GET=False, POST=False, query_model=False, json=False, branching=False

```python
def session_expired(request):
    """
    Session expired page.
    """
    context = {}
    return render(request, 'lumra_pages/auth/session_expired.html', context)
```

## Tugas Claude

1. Review hubungan antar template dan view di modul ini.
2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.
3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.
4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.
