# Generated migration to recreate missing tables
# This migration creates ALL missing tables because migrations 0003-0008
# were marked as applied but tables were never actually created in the database

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumra_config', '0008_fix_table_name_conflicts'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create production_bill_of_materials table FIRST (from 0003, but missing)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_bill_of_materials (id bigserial PRIMARY KEY, finished_variant_id bigint NOT NULL, code varchar(50) NOT NULL UNIQUE, version integer NOT NULL DEFAULT 1, name varchar(255), is_active boolean NOT NULL DEFAULT true, notes text NOT NULL DEFAULT '', created_by_id bigint, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(finished_variant_id) REFERENCES lumra_config_productvariants(id), FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS production_bill_of_materials_code ON production_bill_of_materials(code);",
            "DROP TABLE IF EXISTS production_bill_of_materials CASCADE;"
        ),
        
        # Create WarehouseZone table (from 0003, but missing)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS lumra_config_warehouse_zones (id bigserial PRIMARY KEY, location_id bigint NOT NULL, code varchar(30) NOT NULL, name varchar(120) NOT NULL, zone_type varchar(20) NOT NULL DEFAULT 'rack', capacity integer NOT NULL DEFAULT 0, is_active boolean NOT NULL DEFAULT true, notes text NOT NULL DEFAULT '', created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, UNIQUE(location_id, code), FOREIGN KEY(location_id) REFERENCES lumra_config_locations(id) ON DELETE CASCADE); CREATE INDEX IF NOT EXISTS lumra_config_warehouse_zones_location_id ON lumra_config_warehouse_zones(location_id);",
            "DROP TABLE IF EXISTS lumra_config_warehouse_zones CASCADE;"
        ),
        
        # Create InventoryBatch table (from 0003, but missing)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS lumra_config_inventory_batches (id bigserial PRIMARY KEY, variant_id bigint NOT NULL, location_id bigint NOT NULL, zone_id bigint, code varchar(50) NOT NULL, quantity_on_hand integer NOT NULL DEFAULT 0, production_date date, expiry_date date, notes text NOT NULL DEFAULT '', created_by_id bigint, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, UNIQUE(location_id, code), FOREIGN KEY(variant_id) REFERENCES lumra_config_productvariants(id), FOREIGN KEY(location_id) REFERENCES lumra_config_locations(id) ON DELETE CASCADE, FOREIGN KEY(zone_id) REFERENCES lumra_config_warehouse_zones(id) ON DELETE SET NULL, FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS lumra_config_inventory_batches_code ON lumra_config_inventory_batches(code); CREATE INDEX IF NOT EXISTS lumra_config_inventory_batches_expiry_date ON lumra_config_inventory_batches(expiry_date);",
            "DROP TABLE IF EXISTS lumra_config_inventory_batches CASCADE;"
        ),
        
        # Create ProductionOrder table (from 0003, but missing)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_orders (id bigserial PRIMARY KEY, code varchar(50) NOT NULL UNIQUE, bom_id bigint NOT NULL, status varchar(20) NOT NULL DEFAULT 'pending', target_quantity numeric(12, 2) NOT NULL DEFAULT 0, produced_quantity numeric(12, 2) NOT NULL DEFAULT 0, unit_id bigint, location_id bigint, scheduled_start_date date, scheduled_end_date date, actual_start_date date, actual_end_date date, notes text NOT NULL DEFAULT '', created_by_id bigint, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(bom_id) REFERENCES production_bill_of_materials(id), FOREIGN KEY(unit_id) REFERENCES _units(id) ON DELETE SET NULL, FOREIGN KEY(location_id) REFERENCES lumra_config_locations(id) ON DELETE SET NULL, FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS production_orders_code ON production_orders(code); CREATE INDEX IF NOT EXISTS production_orders_status ON production_orders(status); CREATE INDEX IF NOT EXISTS production_orders_bom_id ON production_orders(bom_id);",
            "DROP TABLE IF EXISTS production_orders CASCADE;"
        ),
        
        # Create ProductionMaterialConsumption table (from 0003, but missing)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_material_consumptions (id bigserial PRIMARY KEY, production_order_id bigint NOT NULL, component_id bigint NOT NULL, quantity_planned numeric(12, 2) NOT NULL DEFAULT 0, quantity_actual numeric(12, 2), unit_id bigint, notes text NOT NULL DEFAULT '', created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE, FOREIGN KEY(component_id) REFERENCES lumra_config_productvariants(id), FOREIGN KEY(unit_id) REFERENCES _units(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS production_material_consumptions_production_order_id ON production_material_consumptions(production_order_id);",
            "DROP TABLE IF EXISTS production_material_consumptions CASCADE;"
        ),
        
        # Create ProductionFinishedGoodsReceipt table (from 0003, but missing)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_finished_goods_receipts (id bigserial PRIMARY KEY, production_order_id bigint NOT NULL, finished_goods_variant_id bigint NOT NULL, quantity_received numeric(12, 2) NOT NULL DEFAULT 0, batch_number varchar(100) DEFAULT NULL, location_id bigint, unit_id bigint, notes text NOT NULL DEFAULT '', received_by_id bigint, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE, FOREIGN KEY(finished_goods_variant_id) REFERENCES lumra_config_productvariants(id), FOREIGN KEY(location_id) REFERENCES lumra_config_locations(id) ON DELETE SET NULL, FOREIGN KEY(unit_id) REFERENCES _units(id) ON DELETE SET NULL, FOREIGN KEY(received_by_id) REFERENCES auth_user(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS production_finished_goods_receipts_production_order_id ON production_finished_goods_receipts(production_order_id);",
            "DROP TABLE IF EXISTS production_finished_goods_receipts CASCADE;"
        ),
        
        # Create ProductionWaste table (from 0003, but missing)
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS production_wastes (id bigserial PRIMARY KEY, production_order_id bigint NOT NULL, waste_variant_id bigint NOT NULL, quantity_waste numeric(12, 2) NOT NULL DEFAULT 0, unit_id bigint, notes text NOT NULL DEFAULT '', created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE, FOREIGN KEY(waste_variant_id) REFERENCES lumra_config_productvariants(id), FOREIGN KEY(unit_id) REFERENCES _units(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS production_wastes_production_order_id ON production_wastes(production_order_id);",
            "DROP TABLE IF EXISTS production_wastes CASCADE;"
        ),
    ]
