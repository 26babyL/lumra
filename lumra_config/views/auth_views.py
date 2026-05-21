# lumra_config/views/auth_views.py
# Auto-generated oleh lumra_sync.py dari core/views/auth_views.py
# JANGAN EDIT MANUAL — edit core/views/auth_views.py lalu jalankan lumra_sync.py lagi

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from lumra_config.models import UserProfile


# =====================================================
# LOGIN VIEW
# =====================================================

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


# =====================================================
# LOGOUT VIEW
# =====================================================

def logout_view(request):
    """
    Logout user dan kembali ke login page.
    """
    auth_logout(request)
    return redirect("login")


# =====================================================
# PROFILE VIEW
# =====================================================

@login_required
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


# =====================================================
# SETTINGS VIEW
# =====================================================

@login_required
def settings_view(request):
    """
    Halaman settings utama.
    """

    return render(request, "lumra_pages/settings/settings.html")


# =====================================================
# FORGOT PASSWORD
# =====================================================

def forgot_password(request):
    """
    Forgot password request page.
    """
    context = {}
    return render(request, 'lumra_pages/auth/forgot_password.html', context)


# =====================================================
# RESET PASSWORD
# =====================================================

def reset_password(request, token=None):
    """
    Reset password with token.
    """
    context = {'token': token}
    return render(request, 'lumra_pages/auth/reset_password.html', context)


# =====================================================
# TWO FACTOR AUTHENTICATION
# =====================================================

@login_required
def two_factor_setup(request):
    """
    Two Factor Authentication setup page.
    """
    context = {}
    return render(request, 'lumra_pages/auth/two_factor.html', context)


# =====================================================
# VERIFY EMAIL
# =====================================================

def verify_email(request, token=None):
    """
    Email verification page.
    """
    context = {'token': token}
    return render(request, 'lumra_pages/auth/verify_email.html', context)


# =====================================================
# LOCK SCREEN
# =====================================================

@login_required
def lock_screen(request):
    """
    Lock screen (session lock, requires re-auth).
    """
    context = {}
    return render(request, 'lumra_pages/auth/lock_screen.html', context)


# =====================================================
# SESSION EXPIRED
# =====================================================

def session_expired(request):
    """
    Session expired page.
    """
    context = {}
    return render(request, 'lumra_pages/auth/session_expired.html', context)


# =====================================================
# REGISTER VIEW
# =====================================================

def register_view(request):
    """
    Registration page for new users.
    """
    context = {}
    return render(request, 'lumra_pages/auth/register.html', context)
