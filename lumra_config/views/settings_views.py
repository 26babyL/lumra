# lumra_config/views/settings_views.py

import json
from hashlib import sha256

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from lumra_config.models import (
    APIKey,
    BackupRecord,
    EmailSetting,
    NotificationSetting,
    NumberingSequence,
    Role,
    RolePermission,
    UserRole,
    UserProfile,
)


DEFAULT_MODULES = [
    ("dashboard", "Dashboard"),
    ("inventory", "Inventory"),
    ("purchasing", "Purchasing"),
    ("production", "Production"),
    ("sales", "Sales (POS)"),
    ("finance", "Finance"),
    ("hr", "HR & Payroll"),
    ("admin", "System Admin"),
]


def _seed_role_overview():
    fallback_roles = [
        {
            "name": "Super Admin",
            "code": "SUPER_ADMIN",
            "description": "Akses penuh ke seluruh sistem termasuk pengaturan.",
            "role_type": "admin",
            "user_count": 1,
        },
        {
            "name": "Finance Manager",
            "code": "FINANCE_MANAGER",
            "description": "Akses laporan keuangan, AR/AP, dan approval pembayaran.",
            "role_type": "staff",
            "user_count": 2,
        },
        {
            "name": "Warehouse Staff",
            "code": "WAREHOUSE_STAFF",
            "description": "Mengelola stok, batch, transfer, dan expiry monitoring.",
            "role_type": "staff",
            "user_count": 3,
        },
    ]
    for item in fallback_roles:
        Role.objects.get_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "role_type": item["role_type"],
                "is_system": True,
            },
        )


def _seed_permissions():
    if RolePermission.objects.exists():
        return
    _seed_role_overview()
    role_access = {
        "SUPER_ADMIN": {module[0]: "full" for module in DEFAULT_MODULES},
        "FINANCE_MANAGER": {
            "dashboard": "view",
            "inventory": "view",
            "purchasing": "view",
            "production": "none",
            "sales": "view",
            "finance": "full",
            "hr": "none",
            "admin": "none",
        },
        "WAREHOUSE_STAFF": {
            "dashboard": "view",
            "inventory": "full",
            "purchasing": "view",
            "production": "view",
            "sales": "none",
            "finance": "none",
            "hr": "none",
            "admin": "none",
        },
    }
    for role in Role.objects.all():
        access_map = role_access.get(role.code, {})
        for module_key, module_name in DEFAULT_MODULES:
            access_level = access_map.get(module_key, "none")
            RolePermission.objects.get_or_create(
                role=role,
                module_key=module_key,
                defaults={
                    "module_name": module_name,
                    "access_level": access_level,
                    "can_create": access_level == "full",
                    "can_update": access_level == "full",
                    "can_delete": role.code == "SUPER_ADMIN" and access_level == "full",
                    "can_approve": module_key in {"purchasing", "finance", "admin"} and access_level == "full",
                },
            )


def _seed_numbering_sequences():
    defaults = [
        {"key": "invoice", "name": "Faktur", "prefix": "INV", "digits": 4, "current_value": 14},
        {"key": "po", "name": "Purchase Order", "prefix": "PO", "digits": 4, "current_value": 7},
        {"key": "return", "name": "Retur", "prefix": "RTN", "digits": 4, "current_value": 1},
    ]
    for item in defaults:
        NumberingSequence.objects.get_or_create(key=item["key"], defaults=item)


def _seed_notification_settings():
    defaults = [
        {"key": "inv_low_stock", "label": "Stok Menipis", "email_enabled": True, "app_enabled": True},
        {"key": "inv_expiry", "label": "Produk Kedaluwarsa", "email_enabled": True, "whatsapp_enabled": False},
        {"key": "requisition", "label": "Permintaan Stok", "email_enabled": True, "app_enabled": True},
        {"key": "system_backup", "label": "Backup Database", "app_enabled": True},
    ]
    for item in defaults:
        NotificationSetting.objects.get_or_create(key=item["key"], defaults=item)


def _seed_api_keys():
    if APIKey.objects.exists():
        return
    samples = [
        ("Mobile POS App", "sk_live_", "mobile-pos-app", 30),
        ("Supplier Portal", "sk_live_", "supplier-portal", -30),
    ]
    for name, prefix, raw, offset_days in samples:
        hashed = sha256(raw.encode("utf-8")).hexdigest()
        APIKey.objects.get_or_create(
            hashed_key=hashed,
            defaults={
                "name": name,
                "key_prefix": prefix,
                "last_four": hashed[-4:],
                "status": "active" if offset_days > 0 else "expired",
                "expires_at": timezone.now() + timezone.timedelta(days=offset_days),
            },
        )


def _seed_backups():
    if BackupRecord.objects.exists():
        return
    today = timezone.now()
    BackupRecord.objects.get_or_create(
        name=f"Manual_Backup_{today:%Y%m%d}.sql",
        defaults={
            "backup_type": "manual",
            "file_size_bytes": 2_400_000,
            "status": "ready",
        },
    )
    BackupRecord.objects.get_or_create(
        name=f"Auto_Backup_{(today - timezone.timedelta(days=1)):%Y%m%d}.sql",
        defaults={
            "backup_type": "automatic",
            "file_size_bytes": 2_300_000,
            "status": "ready",
        },
    )


def _numbering_preview(sequence):
    next_number = sequence.current_value + 1
    if sequence.use_date_prefix:
        period_prefix = timezone.localdate().strftime("%y%m")
        prefix = f"{sequence.prefix}-{period_prefix}"
    else:
        prefix = sequence.prefix
    return f"{prefix}-{str(next_number).zfill(sequence.digits)}"


def _serialize_users(users):
    role_map = {
        item["user_id"]: item["role__name"]
        for item in UserRole.objects.select_related("role").values("user_id", "role__name")
    }
    profile_map = {
        profile.user_id: profile
        for profile in UserProfile.objects.select_related("location", "user").filter(user__in=users)
    }
    payload = []
    for user in users:
        profile = profile_map.get(user.id)
        role_name = role_map.get(user.id, "Viewer")
        status = "online" if user.is_active else "offline"
        payload.append(
            {
                "id": user.id,
                "uid": f"USR-{user.id:03d}",
                "name": user.get_full_name() or user.username,
                "email": user.email,
                "role": role_name.lower().replace(" ", "_"),
                "role_label": role_name,
                "status": status,
                "location": profile.location.name if profile and profile.location else "",
                "store": profile.location.name if profile and profile.location else "",
                "twofa": False,
                "last_login": timezone.localtime(user.last_login).strftime("%d %b %Y %H:%M") if user.last_login else "",
                "permissions": [],
            }
        )
    return payload


def _user_summary(users):
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    admin_users = UserRole.objects.filter(role__role_type="admin").values("user_id").distinct().count()
    return {
        "total_users": total_users,
        "online_count": active_users,
        "admin_count": admin_users,
        "twofa_count": 0,
    }


def _business_context(request):
    can_access = request.user.is_superuser or request.user.is_staff
    company = {
        "company_name": "Lumra ERP",
        "legal_name": "PT Lumra Digital Nusantara",
        "npwp": "",
        "nib": "",
        "pkp": "",
        "address": "",
        "city": "",
        "province": "",
        "phone": "",
        "email": request.user.email or "",
        "website": "",
        "brand_color": "#10b981",
        "brand_color_2": "#0f172a",
        "report_theme": "emerald",
        "ppn_rate": 11,
        "invoice_format": "INV-{YYYY}-{MM}-{SEQ}",
        "payment_terms": 30,
        "currency": "IDR",
        "invoice_footer": "Dokumen diterbitkan otomatis oleh Lumra ERP.",
    }
    perms = {"sys_config": can_access}
    return {
        "company_json": json.dumps(company),
        "settings_json": json.dumps(company),
        "audit_json": json.dumps([]),
        "outlets_json": json.dumps([]),
        "features_json": json.dumps([]),
        "perms_json": json.dumps(perms),
        "can_access_settings": can_access,
    }


def _system_status_context():
    metrics = {
        "uptime": "99.9%",
        "db_status": "ok",
        "total_sku": 0,
        "db_connections": 0,
        "db_size": "0 MB",
        "query_avg_ms": 0,
        "disk_pct": 0,
        "disk_used": "0 GB",
        "disk_total": "1 TB",
        "disk_partitions": [],
        "last_sync": timezone.localtime().strftime("%d %b %Y %H:%M"),
        "synced_sku": 0,
        "sync_ok": True,
        "active_tenants": 1,
        "cpu_pct": 0,
        "cpu_cores": 0,
        "cpu_per_core": [],
        "mem_pct": 0,
        "mem_used": "0 GB",
        "mem_total": "0 GB",
        "cpu_history": [0] * 30,
        "mem_history": [0] * 30,
        "perf_labels": [f"T-{idx}" for idx in range(30, 0, -1)],
    }
    return {
        "metrics_json": json.dumps(metrics),
        "components_json": json.dumps([]),
        "logs_json": json.dumps([]),
        "alerts_json": json.dumps([]),
    }


@login_required
def users_list(request):
    users = User.objects.order_by("username")
    users_json = _serialize_users(users)
    context = {"users": users, "users_json": json.dumps(users_json), **_user_summary(users)}
    return render(request, "lumra_pages/settings/users.html", context)


@login_required
def user_list(request):
    users = User.objects.order_by("username")
    users_json = _serialize_users(users)
    context = {"users": users, "users_json": json.dumps(users_json), **_user_summary(users)}
    return render(request, "lumra_pages/settings/user_list.html", context)


@login_required
def roles(request):
    role_qs = Role.objects.annotate(user_count=Count("user_assignments")).order_by("name")
    context = {
        "roles": role_qs,
        "total_roles": role_qs.count(),
    }
    return render(request, "lumra_pages/settings/roles.html", context)


@login_required
def role_form(request, pk=None):
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


@login_required
def user_roles_permissions(request):
    role_assignments = UserRole.objects.select_related("user", "role").order_by("user__username", "role__name")
    context = {
        "role_assignments": role_assignments,
        "roles": Role.objects.order_by("name"),
    }
    return render(request, "lumra_pages/settings/user_roles_permissions.html", context)


@login_required
def permission_matrix(request):
    roles_qs = Role.objects.prefetch_related("permissions").order_by("name")
    matrix_rows = []
    roles_json = []
    for role in roles_qs:
        permissions = {perm.module_key: perm.access_level for perm in role.permissions.all()}
        matrix_rows.append({"role": role, "permissions": permissions})
        roles_json.append({
            "id": role.id,
            "name": role.name,
            "access": [module for module, level in permissions.items() if level != "none"],
            "access_levels": permissions,
        })
    context = {
        "modules": DEFAULT_MODULES,
        "matrix_rows": matrix_rows,
        "roles": roles_qs,
        "roles_json": json.dumps(roles_json),
    }
    return render(request, "lumra_pages/settings/permission_matrix.html", context)


@login_required
def business_profile(request):
    return render(request, "lumra_pages/settings/business_profile.html", _business_context(request))


@login_required
def business_settings(request):
    return render(request, "lumra_pages/settings/business_settings.html", _business_context(request))


@login_required
def business_form_general(request):
    return render(request, "lumra_pages/settings/business_form_general.html", _business_context(request))


@login_required
def business_feature_matrix(request):
    return render(request, "lumra_pages/settings/business_feature_matrix.html", _business_context(request))


@login_required
def system_status(request):
    return render(request, "lumra_pages/settings/system_status.html", _system_status_context())


@login_required
def email_settings(request):
    setting = EmailSetting.objects.order_by("-updated_at").first()
    context = {
        "email_setting": setting,
    }
    return render(request, "lumra_pages/settings/email_settings.html", context)


@login_required
def notification_settings(request):
    settings_qs = NotificationSetting.objects.order_by("label")
    context = {
        "notification_settings": settings_qs,
    }
    return render(request, "lumra_pages/settings/notification_settings.html", context)


@login_required
def numbering_settings(request):
    sequences = NumberingSequence.objects.order_by("name")
    context = {
        "numbering_sequences": sequences,
        "numbering_preview": {sequence.key: _numbering_preview(sequence) for sequence in sequences},
    }
    return render(request, "lumra_pages/settings/numbering_settings.html", context)


@login_required
def backup_restore(request):
    backups = BackupRecord.objects.order_by("-created_at")
    context = {
        "backups": backups,
        "latest_backup": backups.first(),
    }
    return render(request, "lumra_pages/settings/backup_restore.html", context)


@login_required
def api_keys(request):
    keys = APIKey.objects.order_by("-created_at")
    context = {
        "api_keys": keys,
    }
    return render(request, "lumra_pages/settings/api_keys.html", context)


@login_required
def about(request):
    return render(request, "lumra_pages/settings/about.html", {})


@login_required
def contact(request):
    return render(request, "lumra_pages/settings/contact.html", {})


@login_required
def search(request):
    query = request.GET.get("q", "")
    context = {"query": query}
    return render(request, "lumra_pages/settings/search.html", context)
