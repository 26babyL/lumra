from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lumra_config", "0018_update_master_table_names_state"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS system_notification_settings (
                id bigserial PRIMARY KEY,
                key varchar(50) NOT NULL UNIQUE,
                label varchar(120) NOT NULL,
                email_enabled boolean NOT NULL DEFAULT false,
                app_enabled boolean NOT NULL DEFAULT false,
                whatsapp_enabled boolean NOT NULL DEFAULT false,
                is_active boolean NOT NULL DEFAULT true,
                updated_by_id integer NULL REFERENCES auth_user(id) ON DELETE SET NULL,
                updated_at timestamp with time zone NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS system_notification_settings_key_idx
                ON system_notification_settings(key);

            CREATE TABLE IF NOT EXISTS lumra_config_stock_adjustment_reasons (
                id bigserial PRIMARY KEY,
                code varchar(30) NOT NULL UNIQUE,
                name varchar(120) NOT NULL,
                description text NOT NULL DEFAULT '',
                is_active boolean NOT NULL DEFAULT true,
                created_at timestamp with time zone NOT NULL DEFAULT now(),
                updated_at timestamp with time zone NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS production_bom_items (
                id bigserial PRIMARY KEY,
                bom_id bigint NOT NULL REFERENCES production_bill_of_materials(id) ON DELETE CASCADE,
                component_id bigint NOT NULL REFERENCES lumra_config_productvariants(id) ON DELETE RESTRICT,
                quantity numeric(12, 2) NOT NULL,
                unit_id bigint NULL REFERENCES lumra_config_units(id) ON DELETE SET NULL,
                notes text NOT NULL DEFAULT '',
                UNIQUE (bom_id, component_id)
            );
            CREATE INDEX IF NOT EXISTS production_bom_items_bom_id_idx
                ON production_bom_items(bom_id);
            CREATE INDEX IF NOT EXISTS production_bom_items_component_id_idx
                ON production_bom_items(component_id);
            CREATE INDEX IF NOT EXISTS production_bom_items_unit_id_idx
                ON production_bom_items(unit_id);

            CREATE OR REPLACE VIEW product_details_view AS
            SELECT
                pv.sku::varchar(50) AS sku,
                left(p.name, 100)::varchar(100) AS name,
                pv.price_buy AS price_buy,
                pv.price_sell AS price_sell,
                attrs.bean_type::varchar(100) AS bean_type,
                attrs.tag::varchar(100) AS tag,
                attrs.roast_level::varchar(100) AS roast_level,
                attrs.processing::varchar(100) AS processing,
                c.name::varchar(100) AS category,
                p.description AS description
            FROM lumra_config_productvariants pv
            JOIN lumra_config_products p ON p.id = pv.product_id
            LEFT JOIN lumra_config_categories c ON c.id = p.category_id
            LEFT JOIN (
                SELECT
                    variant_id,
                    max(attr_value) FILTER (WHERE lower(attr_name) IN ('bean_type', 'bean type', 'jenis biji')) AS bean_type,
                    max(attr_value) FILTER (WHERE lower(attr_name) IN ('tag', 'tags')) AS tag,
                    max(attr_value) FILTER (WHERE lower(attr_name) IN ('roast_level', 'roast level', 'level roasting')) AS roast_level,
                    max(attr_value) FILTER (WHERE lower(attr_name) IN ('processing', 'process', 'proses')) AS processing
                FROM lumra_config_productattribute_items
                GROUP BY variant_id
            ) attrs ON attrs.variant_id = pv.id;
            """,
            reverse_sql="""
            DROP VIEW IF EXISTS product_details_view;
            DROP TABLE IF EXISTS production_bom_items;
            DROP TABLE IF EXISTS lumra_config_stock_adjustment_reasons;
            DROP TABLE IF EXISTS system_notification_settings;
            """,
        ),
    ]
