# Generated migration to create missing production tables

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumra_config', '0014_recreate_inventory_production_tables'),
    ]

    operations = [
        # Create production_material_consumptions table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS production_material_consumptions CASCADE;",
            "SELECT 1;"
        ),
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_material_consumptions (id bigserial PRIMARY KEY, production_order_id bigint NOT NULL, component_id bigint NOT NULL, quantity numeric(12, 2) NOT NULL, unit_id bigint, consumed_at timestamp with time zone NOT NULL, notes text NOT NULL DEFAULT '', FOREIGN KEY(production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE, FOREIGN KEY(component_id) REFERENCES lumra_config_productvariants(id) ON DELETE RESTRICT, FOREIGN KEY(unit_id) REFERENCES _units(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS production_material_consumptions CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_material_consumptions_consumed_at ON production_material_consumptions(consumed_at DESC);",
            "DROP INDEX IF EXISTS production_material_consumptions_consumed_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_material_consumptions_production_order ON production_material_consumptions(production_order_id);",
            "DROP INDEX IF EXISTS production_material_consumptions_production_order;"
        ),

        # Create production_finished_goods_receipts table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS production_finished_goods_receipts CASCADE;",
            "SELECT 1;"
        ),
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_finished_goods_receipts (id bigserial PRIMARY KEY, production_order_id bigint NOT NULL, finished_variant_id bigint NOT NULL, location_id bigint NOT NULL, quantity_received numeric(12, 2) NOT NULL, received_at timestamp with time zone NOT NULL, notes text NOT NULL DEFAULT '', FOREIGN KEY(production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE, FOREIGN KEY(finished_variant_id) REFERENCES lumra_config_productvariants(id) ON DELETE RESTRICT, FOREIGN KEY(location_id) REFERENCES lumra_config_locations(id) ON DELETE RESTRICT);",
            "DROP TABLE IF EXISTS production_finished_goods_receipts CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_finished_goods_receipts_received_at ON production_finished_goods_receipts(received_at DESC);",
            "DROP INDEX IF EXISTS production_finished_goods_receipts_received_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_finished_goods_receipts_production_order ON production_finished_goods_receipts(production_order_id);",
            "DROP INDEX IF EXISTS production_finished_goods_receipts_production_order;"
        ),

        # Create production_waste_records table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS production_waste_records CASCADE;",
            "SELECT 1;"
        ),
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_waste_records (id bigserial PRIMARY KEY, production_order_id bigint NOT NULL, component_id bigint, waste_type varchar(20) NOT NULL DEFAULT 'scrap', quantity numeric(12, 2) NOT NULL DEFAULT 0, unit_id bigint, recorded_at timestamp with time zone NOT NULL, notes text NOT NULL DEFAULT '', FOREIGN KEY(production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE, FOREIGN KEY(component_id) REFERENCES lumra_config_productvariants(id) ON DELETE RESTRICT, FOREIGN KEY(unit_id) REFERENCES _units(id) ON DELETE SET NULL);",
            "DROP TABLE IF EXISTS production_waste_records CASCADE;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_waste_records_recorded_at ON production_waste_records(recorded_at DESC);",
            "DROP INDEX IF EXISTS production_waste_records_recorded_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS production_waste_records_production_order ON production_waste_records(production_order_id);",
            "DROP INDEX IF EXISTS production_waste_records_production_order;"
        ),
    ]

