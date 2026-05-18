# Generated migration — tambahkan ke:
# lumra_config/migrations/0001_add_sales_target.py
# (atau sesuaikan nomor dengan migration terakhir di project)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lumra_config', '0001_initial'),   # ← ganti sesuai migration terakhir
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesTarget',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year',          models.IntegerField(verbose_name='Tahun')),
                ('month',         models.IntegerField(choices=[(1,'Januari'),(2,'Februari'),(3,'Maret'),(4,'April'),(5,'Mei'),(6,'Juni'),(7,'Juli'),(8,'Agustus'),(9,'September'),(10,'Oktober'),(11,'November'),(12,'Desember')], verbose_name='Bulan')),
                ('target_amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Target Revenue (Rp)')),
                ('notes',         models.TextField(blank=True, verbose_name='Catatan')),
                ('created_at',    models.DateTimeField(auto_now_add=True)),
                ('updated_at',    models.DateTimeField(auto_now=True)),
                ('created_by',    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_targets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name' : 'Sales Target',
                'db_table'     : 'lumra_config_sales_targets',
                'ordering'     : ['-year', '-month'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='salestarget',
            unique_together={('year', 'month')},
        ),
    ]