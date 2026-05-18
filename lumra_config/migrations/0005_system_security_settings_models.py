from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("lumra_config", "0004_accounting_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_index=True, max_length=100, unique=True)),
                ("code", models.CharField(db_index=True, max_length=50, unique=True)),
                ("description", models.TextField(blank=True)),
                ("role_type", models.CharField(choices=[("admin", "Admin"), ("staff", "Staff"), ("service", "Service")], default="staff", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("is_system", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "system_roles", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="APIKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("key_prefix", models.CharField(db_index=True, max_length=20)),
                ("hashed_key", models.CharField(max_length=128, unique=True)),
                ("last_four", models.CharField(blank=True, max_length=4)),
                ("status", models.CharField(choices=[("active", "Active"), ("revoked", "Revoked"), ("expired", "Expired")], db_index=True, default="active", max_length=20)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_api_keys", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "system_api_keys", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BackupRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("backup_type", models.CharField(default="manual", max_length=30)),
                ("file_path", models.CharField(blank=True, max_length=255)),
                ("file_size_bytes", models.PositiveBigIntegerField(default=0)),
                ("status", models.CharField(choices=[("ready", "Ready"), ("processing", "Processing"), ("failed", "Failed"), ("restored", "Restored")], db_index=True, default="ready", max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_backup_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "system_backup_records", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="EmailSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("encryption", models.CharField(default="tls", max_length=20)),
                ("host", models.CharField(blank=True, max_length=255)),
                ("port", models.PositiveIntegerField(default=587)),
                ("username", models.CharField(blank=True, max_length=255)),
                ("password", models.CharField(blank=True, max_length=255)),
                ("from_name", models.CharField(blank=True, max_length=120)),
                ("from_email", models.EmailField(blank=True, max_length=254)),
                ("enabled", models.BooleanField(default=False)),
                ("test_recipient", models.EmailField(blank=True, max_length=254)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_email_settings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "system_email_settings", "ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="NotificationSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(db_index=True, max_length=50, unique=True)),
                ("label", models.CharField(max_length=120)),
                ("email_enabled", models.BooleanField(default=False)),
                ("app_enabled", models.BooleanField(default=False)),
                ("whatsapp_enabled", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_notification_settings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "system_notification_settings", "ordering": ["label"]},
        ),
        migrations.CreateModel(
            name="NumberingSequence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(db_index=True, max_length=50, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("prefix", models.CharField(max_length=30)),
                ("digits", models.PositiveSmallIntegerField(default=4)),
                ("current_value", models.PositiveIntegerField(default=0)),
                ("reset_period", models.CharField(default="never", max_length=20)),
                ("use_date_prefix", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "system_numbering_sequences", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="RolePermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module_key", models.CharField(db_index=True, max_length=50)),
                ("module_name", models.CharField(max_length=100)),
                ("access_level", models.CharField(choices=[("none", "None"), ("view", "View"), ("full", "Full")], default="none", max_length=20)),
                ("can_create", models.BooleanField(default=False)),
                ("can_update", models.BooleanField(default=False)),
                ("can_delete", models.BooleanField(default=False)),
                ("can_approve", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="permissions", to="lumra_config.role")),
            ],
            options={"db_table": "system_role_permissions", "ordering": ["role__name", "module_name"], "unique_together": {("role", "module_key")}},
        ),
        migrations.CreateModel(
            name="UserRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                ("assigned_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_roles", to=settings.AUTH_USER_MODEL)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_assignments", to="lumra_config.role")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lumra_role_assignments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "system_user_roles", "ordering": ["user__username", "role__name"], "unique_together": {("user", "role")}},
        ),
    ]
