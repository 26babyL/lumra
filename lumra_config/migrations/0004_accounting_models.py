from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("lumra_config", "0003_warehouse_batch_production_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(db_index=True, max_length=20, unique=True)),
                ("name", models.CharField(max_length=150)),
                ("account_type", models.CharField(choices=[("asset", "Asset"), ("liability", "Liability"), ("equity", "Equity"), ("revenue", "Revenue"), ("expense", "Expense")], db_index=True, max_length=20)),
                ("level", models.PositiveSmallIntegerField(default=2)),
                ("is_active", models.BooleanField(default=True)),
                ("allow_posting", models.BooleanField(default=True)),
                ("is_cash_account", models.BooleanField(default=False)),
                ("opening_balance", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="children", to="lumra_config.account")),
            ],
            options={
                "db_table": "accounting_accounts",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="JournalEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(db_index=True, max_length=30, unique=True)),
                ("date", models.DateField(db_index=True, default=django.utils.timezone.localdate)),
                ("reference", models.CharField(blank=True, max_length=100)),
                ("description", models.CharField(max_length=255)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("posted", "Posted")], db_index=True, default="draft", max_length=20)),
                ("source", models.CharField(choices=[("manual", "Manual"), ("payment_voucher", "Payment Voucher"), ("system", "System")], default="manual", max_length=30)),
                ("posted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_journal_entries", to=settings.AUTH_USER_MODEL)),
                ("posted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="posted_journal_entries", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "accounting_journal_entries",
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="AccountsPayableEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(db_index=True, max_length=50, unique=True)),
                ("invoice_date", models.DateField(db_index=True)),
                ("due_date", models.DateField(db_index=True)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("paid_amount", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("status", models.CharField(choices=[("open", "Open"), ("partial", "Partial"), ("paid", "Paid")], db_index=True, default="open", max_length=20)),
                ("memo", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("journal_entry", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ap_entries", to="lumra_config.journalentry")),
                ("vendor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payables", to="lumra_config.vendor")),
            ],
            options={
                "db_table": "accounting_accounts_payable",
                "ordering": ["due_date", "vendor__name"],
            },
        ),
        migrations.CreateModel(
            name="AccountsReceivableEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(db_index=True, max_length=50, unique=True)),
                ("invoice_date", models.DateField(db_index=True)),
                ("due_date", models.DateField(db_index=True)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("paid_amount", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("status", models.CharField(choices=[("open", "Open"), ("partial", "Partial"), ("paid", "Paid")], db_index=True, default="open", max_length=20)),
                ("memo", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="receivables", to="lumra_config.customer")),
                ("journal_entry", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ar_entries", to="lumra_config.journalentry")),
            ],
            options={
                "db_table": "accounting_accounts_receivable",
                "ordering": ["due_date", "customer__name"],
            },
        ),
        migrations.CreateModel(
            name="JournalEntryLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(blank=True, max_length=255)),
                ("debit", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("credit", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="journal_lines", to="lumra_config.account")),
                ("journal_entry", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lines", to="lumra_config.journalentry")),
            ],
            options={
                "db_table": "accounting_journal_entry_lines",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="PaymentVoucher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(db_index=True, max_length=30, unique=True)),
                ("date", models.DateField(db_index=True, default=django.utils.timezone.localdate)),
                ("method", models.CharField(choices=[("transfer", "Transfer"), ("check", "Cek/Giro"), ("cash", "Tunai")], default="transfer", max_length=20)),
                ("memo", models.CharField(blank=True, max_length=255)),
                ("amount_paid", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("cash_account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payment_vouchers", to="lumra_config.account")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payment_vouchers", to=settings.AUTH_USER_MODEL)),
                ("journal_entry", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payment_voucher", to="lumra_config.journalentry")),
                ("vendor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payment_vouchers", to="lumra_config.vendor")),
            ],
            options={
                "db_table": "accounting_payment_vouchers",
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="PaymentVoucherAllocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("payable_entry", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="voucher_allocations", to="lumra_config.accountspayableentry")),
                ("voucher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="allocations", to="lumra_config.paymentvoucher")),
            ],
            options={
                "db_table": "accounting_payment_voucher_allocations",
                "ordering": ["id"],
            },
        ),
    ]
