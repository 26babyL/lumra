# lumra_config/views/auth_views.py

import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone

from lumra_config.models import UserProfile

logger = logging.getLogger(__name__)
User = get_user_model()


# =====================================================
# LOGIN VIEW
# =====================================================

def login_view(request):
    """
    Login page untuk user Lumra.
    Supports username or email authentication.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me")

        if not username or not password:
            return render(
                request,
                "lumra_pages/auth/login.html",
                {"error": "Username dan password wajib diisi."},
            )

        # Allow login with email
        if "@" in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                return render(
                    request,
                    "lumra_pages/auth/login.html",
                    {"error": "Akun Anda sudah dinonaktifkan. Hubungi administrator."},
                )
            auth_login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            logger.info("User '%s' logged in successfully.", user.username)
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            logger.warning("Failed login attempt for '%s'.", username)
            return render(
                request,
                "lumra_pages/auth/login.html",
                {"error": "Username atau password salah."},
            )

    return render(request, "lumra_pages/auth/login.html")


# =====================================================
# LOGOUT VIEW
# =====================================================

def logout_view(request):
    """
    Logout user dan kembali ke login page.
    """
    if request.user.is_authenticated:
        logger.info("User '%s' logged out.", request.user.username)
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

    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()

        profile.phone = request.POST.get("phone", profile.phone)
        profile.save()

        messages.success(request, "Profil berhasil diperbarui.")
        return redirect("profile")

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
    Forgot password — send reset link via email.
    GET: tampilkan form input email.
    POST: kirim email reset password jika user ditemukan.
    """
    context = {"success": False}

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            context["error"] = "Email wajib diisi."
            return render(request, "lumra_pages/auth/forgot_password.html", context)

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            user = None

        if user:
            token = uuid.uuid4().hex
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.reset_token = token
            profile.reset_token_expires = timezone.now() + timedelta(hours=1)
            profile.save()

            reset_url = request.build_absolute_uri(f"/auth/reset-password/{token}/")
            try:
                send_mail(
                    subject="Lumra — Reset Password",
                    message=f"Klik link berikut untuk reset password Anda:\n{reset_url}\n\nLink berlaku selama 1 jam.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                logger.info("Password reset email sent to '%s'.", email)
            except Exception:
                logger.exception("Failed to send password reset email to '%s'.", email)

        # Always show success to prevent email enumeration
        context["success"] = True
        context["message"] = "Jika email terdaftar, link reset password sudah dikirim."

    return render(request, "lumra_pages/auth/forgot_password.html", context)


# =====================================================
# RESET PASSWORD
# =====================================================

def reset_password(request, token=None):
    """
    Reset password with token.
    GET: tampilkan form new password.
    POST: validate token & update password.
    """
    context = {"token": token, "valid_token": False}

    if not token:
        context["error"] = "Token reset tidak ditemukan."
        return render(request, "lumra_pages/auth/reset_password.html", context)

    try:
        profile = UserProfile.objects.select_related("user").get(
            reset_token=token,
            reset_token_expires__gt=timezone.now(),
        )
        context["valid_token"] = True
    except UserProfile.DoesNotExist:
        context["error"] = "Token sudah kadaluarsa atau tidak valid."
        return render(request, "lumra_pages/auth/reset_password.html", context)

    if request.method == "POST":
        password1 = request.POST.get("password", "")
        password2 = request.POST.get("password_confirm", "")

        if not password1 or len(password1) < 8:
            context["error"] = "Password minimal 8 karakter."
            return render(request, "lumra_pages/auth/reset_password.html", context)

        if password1 != password2:
            context["error"] = "Konfirmasi password tidak sama."
            return render(request, "lumra_pages/auth/reset_password.html", context)

        user = profile.user
        user.password = make_password(password1)
        user.save()

        # Invalidate token
        profile.reset_token = None
        profile.reset_token_expires = None
        profile.save()

        logger.info("Password reset completed for user '%s'.", user.username)
        messages.success(request, "Password berhasil direset. Silakan login.")
        return redirect("login")

    return render(request, "lumra_pages/auth/reset_password.html", context)


# =====================================================
# REGISTER VIEW
# =====================================================

def register_view(request):
    """
    Registration page for new users.
    GET: tampilkan form registrasi.
    POST: buat akun baru.
    """
    context = {}

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password", "")
        password2 = request.POST.get("password_confirm", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        errors = []
        if not username:
            errors.append("Username wajib diisi.")
        if not email:
            errors.append("Email wajib diisi.")
        if not password1 or len(password1) < 8:
            errors.append("Password minimal 8 karakter.")
        if password1 != password2:
            errors.append("Konfirmasi password tidak sama.")
        if User.objects.filter(username=username).exists():
            errors.append("Username sudah digunakan.")
        if User.objects.filter(email=email).exists():
            errors.append("Email sudah terdaftar.")

        if errors:
            context["errors"] = errors
            context["form_data"] = {
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            }
            return render(request, "lumra_pages/auth/register.html", context)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.get_or_create(user=user)
        logger.info("New user registered: '%s'.", username)
        messages.success(request, "Registrasi berhasil! Silakan login.")
        return redirect("login")

    return render(request, "lumra_pages/auth/register.html", context)


# =====================================================
# TWO FACTOR AUTHENTICATION
# =====================================================

@login_required
def two_factor_setup(request):
    """
    Two Factor Authentication setup page.
    """
    context = {
        "is_enabled": False,
    }
    return render(request, "lumra_pages/auth/two_factor.html", context)


# =====================================================
# VERIFY EMAIL
# =====================================================

def verify_email(request, token=None):
    """
    Email verification page.
    """
    context = {"token": token, "verified": False}

    if token:
        try:
            profile = UserProfile.objects.select_related("user").get(
                email_verification_token=token,
            )
            user = profile.user
            user.is_active = True
            user.save()
            profile.email_verified = True
            profile.email_verification_token = None
            profile.save()
            context["verified"] = True
            context["message"] = "Email berhasil diverifikasi. Silakan login."
            logger.info("Email verified for user '%s'.", user.username)
        except UserProfile.DoesNotExist:
            context["error"] = "Token verifikasi tidak valid."

    return render(request, "lumra_pages/auth/verify_email.html", context)


# =====================================================
# LOCK SCREEN
# =====================================================

@login_required
def lock_screen(request):
    """
    Lock screen — requires re-authentication to continue.
    """
    context = {"username": request.user.username}

    if request.method == "POST":
        password = request.POST.get("password", "")
        user = authenticate(
            request, username=request.user.username, password=password
        )
        if user is not None:
            return redirect("dashboard")
        else:
            context["error"] = "Password salah."

    return render(request, "lumra_pages/auth/lock_screen.html", context)


# =====================================================
# SESSION EXPIRED
# =====================================================

def session_expired(request):
    """
    Session expired page.
    """
    context = {}
    return render(request, "lumra_pages/auth/session_expired.html", context)
