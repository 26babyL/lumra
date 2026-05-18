# Fix waste table name mismatch

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumra_config', '0010_recreate_missing_production_inventory_tables'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS production_wastes RENAME TO production_waste_records;",
            "ALTER TABLE IF EXISTS production_waste_records RENAME TO production_wastes;"
        ),
    ]
