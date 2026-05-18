from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lumra_config", "0017_rename_production_b_finished_3f2b9d_idx_production__finishe_9b629f_idx_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterModelTable(
                    name="category",
                    table="lumra_config_categories",
                ),
                migrations.AlterModelTable(
                    name="tax",
                    table="lumra_config_taxes",
                ),
                migrations.AlterModelTable(
                    name="unit",
                    table="lumra_config_units",
                ),
                migrations.AlterModelTable(
                    name="vendor",
                    table="lumra_config_vendors",
                ),
            ],
        ),
    ]
