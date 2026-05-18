# Generated migration to create inventory and production tables

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumra_config', '0013_recreate_missing_system_tables'),
    ]

    operations = [
        # Create lumra_config_inventory_batches table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS lumra_config_inventory_batches CASCADE;",
            "SELECT 1;"
        ),
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS lumra_config_inventory_batches (id bigserial PRIMARY KEY, variant_id bigint NOT NULL, location_id bigint NOT NULL, zone_id bigint, code varchar(50) NOT NULL, quantity_on_hand integer NOT NULL DEFAULT 0, production_date date, expiry_date date, notes text NOT NULL, created_by_id integer, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, UNIQUE(location_id, code), FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS lumra_config_inventory_batches CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS lumra_config_inventory_batches_expiry_date ON lumra_config_inventory_batches(expiry_date);",
            "DROP INDEX IF EXISTS lumra_config_inventory_batches_expiry_date;"
        ),

        # Create production_orders table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS production_orders CASCADE;",
            "SELECT 1;"
        ),
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_orders (id bigserial PRIMARY KEY, code varchar(50) NOT NULL UNIQUE, bom_id bigint NOT NULL, status varchar(20) NOT NULL DEFAULT 'pending', target_quantity numeric(12, 2) NOT NULL DEFAULT 0, produced_quantity numeric(12, 2) NOT NULL DEFAULT 0, unit_id bigint, scheduled_date date, started_at timestamp with time zone, completed_at timestamp with time zone, priority varchar(20) NOT NULL DEFAULT 'Normal', line varchar(80) NOT NULL, notes text NOT NULL, created_by_id integer, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS production_orders CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_orders_code ON production_orders(code);",
            "DROP INDEX IF EXISTS production_orders_code;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_orders_scheduled_date ON production_orders(scheduled_date);",
            "DROP INDEX IF EXISTS production_orders_scheduled_date;"
        ),
    ]
