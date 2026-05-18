from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Menampilkan daftar tabel beserta jumlah baris datanya"

    def handle(self, *args, **options):
        all_models = apps.get_models()
        with connection.cursor() as cursor:
            existing_tables = {
                table.name for table in connection.introspection.get_table_list(cursor)
            }

        self.stdout.write(f"{'Table Name':<40} | {'Row Count':<15}")
        self.stdout.write("-" * 60)

        stats = []
        for model in all_models:
            table_name = model._meta.db_table

            if table_name not in existing_tables:
                stats.append((table_name, None))
                self.stdout.write(self.style.ERROR(f"{table_name:<40} | {'MISSING':<15}"))
                continue

            with connection.cursor() as cursor:
                quoted_table_name = connection.ops.quote_name(table_name)
                cursor.execute(f"SELECT COUNT(*) FROM {quoted_table_name}")
                row_count = cursor.fetchone()[0]

            stats.append((table_name, row_count))
            color_func = self.style.SUCCESS if row_count > 0 else self.style.WARNING
            self.stdout.write(color_func(f"{table_name:<40} | {row_count:<15}"))

        with open("daftar_tabel_isi.md", "w", encoding="utf-8") as f:
            f.write("# Ringkasan Data Tabel Lumra\n\n")
            f.write("| Nama Tabel | Jumlah Baris | Status |\n")
            f.write("| :--- | :--- | :--- |\n")
            for table, count in stats:
                if count is None:
                    f.write(f"| {table} | - | Missing |\n")
                    continue

                status = "Terisi" if count > 0 else "Kosong"
                f.write(f"| {table} | {count:,} | {status} |\n")
