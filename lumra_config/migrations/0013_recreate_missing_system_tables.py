# Generated migration to create missing system configuration tables
# Creates system tables without complex FK dependencies to avoid reference errors

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumra_config', '0012_recreate_missing_accounting_tables'),
    ]

    operations = [
        # Create system_roles table (standalone, no external FKs)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS system_roles (id bigserial PRIMARY KEY, name varchar(100) NOT NULL UNIQUE, code varchar(50) NOT NULL UNIQUE, description text NOT NULL, role_type varchar(20) NOT NULL DEFAULT 'staff', is_active boolean NOT NULL DEFAULT true, is_system boolean NOT NULL DEFAULT false, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL);",
            "DROP TABLE IF EXISTS system_roles CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_roles_name ON system_roles(name);",
            "DROP INDEX IF EXISTS system_roles_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_roles_code ON system_roles(code);",
            "DROP INDEX IF EXISTS system_roles_code;"
        ),

        # Create system_user_roles table (refs auth_user which always exists)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS system_user_roles (id bigserial PRIMARY KEY, user_id integer NOT NULL, role_id bigint NOT NULL, assigned_by_id integer, assigned_at timestamp with time zone NOT NULL, UNIQUE(user_id, role_id), FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE, FOREIGN KEY(role_id) REFERENCES system_roles(id) ON DELETE CASCADE, FOREIGN KEY(assigned_by_id) REFERENCES auth_user(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS system_user_roles CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_user_roles_user_id ON system_user_roles(user_id);",
            "DROP INDEX IF EXISTS system_user_roles_user_id;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_user_roles_role_id ON system_user_roles(role_id);",
            "DROP INDEX IF EXISTS system_user_roles_role_id;"
        ),

        # Create system_role_permissions table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS system_role_permissions (id bigserial PRIMARY KEY, role_id bigint NOT NULL, module_key varchar(50) NOT NULL, module_name varchar(100) NOT NULL, access_level varchar(20) NOT NULL DEFAULT 'none', can_create boolean NOT NULL DEFAULT false, can_update boolean NOT NULL DEFAULT false, can_delete boolean NOT NULL DEFAULT false, can_approve boolean NOT NULL DEFAULT false, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, UNIQUE(role_id, module_key), FOREIGN KEY(role_id) REFERENCES system_roles(id) ON DELETE CASCADE);",
            "DROP TABLE IF EXISTS system_role_permissions CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_role_permissions_module_key ON system_role_permissions(module_key);",
            "DROP INDEX IF EXISTS system_role_permissions_module_key;"
        ),

        # Create system_api_keys table (refs auth_user which always exists)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS system_api_keys (id bigserial PRIMARY KEY, name varchar(120) NOT NULL, key_prefix varchar(20) NOT NULL, hashed_key varchar(128) NOT NULL UNIQUE, last_four varchar(4) NOT NULL, status varchar(20) NOT NULL DEFAULT 'active', expires_at timestamp with time zone, last_used_at timestamp with time zone, created_by_id integer, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS system_api_keys CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_api_keys_key_prefix ON system_api_keys(key_prefix);",
            "DROP INDEX IF EXISTS system_api_keys_key_prefix;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_api_keys_status ON system_api_keys(status);",
            "DROP INDEX IF EXISTS system_api_keys_status;"
        ),

        # Create system_numbering_sequences table (standalone)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS system_numbering_sequences (id bigserial PRIMARY KEY, key varchar(50) NOT NULL UNIQUE, name varchar(120) NOT NULL, prefix varchar(30) NOT NULL, digits smallint NOT NULL DEFAULT 4, current_value integer NOT NULL DEFAULT 0, reset_period varchar(20) NOT NULL DEFAULT 'never', use_date_prefix boolean NOT NULL DEFAULT false, is_active boolean NOT NULL DEFAULT true, updated_at timestamp with time zone NOT NULL);",
            "DROP TABLE IF EXISTS system_numbering_sequences CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_numbering_sequences_key ON system_numbering_sequences(key);",
            "DROP INDEX IF EXISTS system_numbering_sequences_key;"
        ),

        # Create system_email_settings table (refs auth_user)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS system_email_settings (id bigserial PRIMARY KEY, encryption varchar(20) NOT NULL DEFAULT 'tls', host varchar(255) NOT NULL, port integer NOT NULL DEFAULT 587, username varchar(255) NOT NULL, password varchar(255) NOT NULL, from_name varchar(120) NOT NULL, from_email varchar(254) NOT NULL, enabled boolean NOT NULL DEFAULT false, test_recipient varchar(254) NOT NULL, updated_by_id integer, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(updated_by_id) REFERENCES auth_user(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS system_email_settings CASCADE;"
        ),

        # Create system_backup_records table (refs auth_user)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS system_backup_records (id bigserial PRIMARY KEY, name varchar(255) NOT NULL, backup_type varchar(30) NOT NULL DEFAULT 'manual', file_path varchar(255) NOT NULL, file_size_bytes bigint NOT NULL DEFAULT 0, status varchar(20) NOT NULL DEFAULT 'ready', notes text NOT NULL, created_by_id integer, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS system_backup_records CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_backup_records_status ON system_backup_records(status);",
            "DROP INDEX IF EXISTS system_backup_records_status;"
        ),
    ]
