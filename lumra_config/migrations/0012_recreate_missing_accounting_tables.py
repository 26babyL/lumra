# Recreate all missing accounting tables

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumra_config', '0011_rename_production_wastes_to_waste_records'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create accounting_accounts table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS accounting_accounts (id bigserial PRIMARY KEY, code varchar(20) NOT NULL UNIQUE, name varchar(150) NOT NULL, account_type varchar(20) NOT NULL, level smallint NOT NULL DEFAULT 2, parent_id bigint, is_active boolean NOT NULL DEFAULT true, allow_posting boolean NOT NULL DEFAULT true, is_cash_account boolean NOT NULL DEFAULT false, opening_balance numeric(15, 2) NOT NULL DEFAULT 0, notes text NOT NULL DEFAULT '', created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(parent_id) REFERENCES accounting_accounts(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS accounting_accounts_code ON accounting_accounts(code); CREATE INDEX IF NOT EXISTS accounting_accounts_account_type ON accounting_accounts(account_type); CREATE INDEX IF NOT EXISTS accounting_accounts_parent_id ON accounting_accounts(parent_id);",
            "DROP TABLE IF EXISTS accounting_accounts CASCADE;"
        ),

        # Create accounting_journal_entries table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS accounting_journal_entries (id bigserial PRIMARY KEY, number varchar(30) NOT NULL UNIQUE, date date NOT NULL, reference varchar(100), description varchar(255) NOT NULL, status varchar(20) NOT NULL DEFAULT 'draft', source varchar(30) NOT NULL DEFAULT 'manual', created_by_id bigint, posted_by_id bigint, posted_at timestamp with time zone, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL, FOREIGN KEY(posted_by_id) REFERENCES auth_user(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS accounting_journal_entries_number ON accounting_journal_entries(number); CREATE INDEX IF NOT EXISTS accounting_journal_entries_date ON accounting_journal_entries(date); CREATE INDEX IF NOT EXISTS accounting_journal_entries_status ON accounting_journal_entries(status);",
            "DROP TABLE IF EXISTS accounting_journal_entries CASCADE;"
        ),

        # Create accounting_journal_entry_lines table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS accounting_journal_entry_lines (id bigserial PRIMARY KEY, journal_entry_id bigint NOT NULL, account_id bigint NOT NULL, description varchar(255), debit numeric(15, 2) NOT NULL DEFAULT 0, credit numeric(15, 2) NOT NULL DEFAULT 0, created_at timestamp with time zone NOT NULL, FOREIGN KEY(journal_entry_id) REFERENCES accounting_journal_entries(id) ON DELETE CASCADE, FOREIGN KEY(account_id) REFERENCES accounting_accounts(id) ON DELETE RESTRICT); CREATE INDEX IF NOT EXISTS accounting_journal_entry_lines_journal_entry_id ON accounting_journal_entry_lines(journal_entry_id);",
            "DROP TABLE IF EXISTS accounting_journal_entry_lines CASCADE;"
        ),

        # Create accounting_accounts_payable table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS accounting_accounts_payable (id bigserial PRIMARY KEY, vendor_id bigint NOT NULL, invoice_number varchar(50) NOT NULL UNIQUE, invoice_date date NOT NULL, due_date date NOT NULL, total_amount numeric(15, 2) NOT NULL, paid_amount numeric(15, 2) NOT NULL DEFAULT 0, status varchar(20) NOT NULL DEFAULT 'open', memo varchar(255), journal_entry_id bigint, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(vendor_id) REFERENCES _vendors(id) ON DELETE RESTRICT, FOREIGN KEY(journal_entry_id) REFERENCES accounting_journal_entries(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS accounting_accounts_payable_invoice_number ON accounting_accounts_payable(invoice_number); CREATE INDEX IF NOT EXISTS accounting_accounts_payable_due_date ON accounting_accounts_payable(due_date); CREATE INDEX IF NOT EXISTS accounting_accounts_payable_status ON accounting_accounts_payable(status);",
            "DROP TABLE IF EXISTS accounting_accounts_payable CASCADE;"
        ),

        # Create accounting_accounts_receivable table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS accounting_accounts_receivable (id bigserial PRIMARY KEY, customer_id bigint NOT NULL, invoice_number varchar(50) NOT NULL UNIQUE, invoice_date date NOT NULL, due_date date NOT NULL, total_amount numeric(15, 2) NOT NULL, paid_amount numeric(15, 2) NOT NULL DEFAULT 0, status varchar(20) NOT NULL DEFAULT 'open', memo varchar(255), journal_entry_id bigint, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(customer_id) REFERENCES lumra_config_customers(id) ON DELETE RESTRICT, FOREIGN KEY(journal_entry_id) REFERENCES accounting_journal_entries(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS accounting_accounts_receivable_invoice_number ON accounting_accounts_receivable(invoice_number); CREATE INDEX IF NOT EXISTS accounting_accounts_receivable_due_date ON accounting_accounts_receivable(due_date); CREATE INDEX IF NOT EXISTS accounting_accounts_receivable_status ON accounting_accounts_receivable(status);",
            "DROP TABLE IF EXISTS accounting_accounts_receivable CASCADE;"
        ),

        # Create accounting_payment_vouchers table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS accounting_payment_vouchers (id bigserial PRIMARY KEY, number varchar(30) NOT NULL UNIQUE, date date NOT NULL, vendor_id bigint NOT NULL, cash_account_id bigint NOT NULL, method varchar(20) NOT NULL DEFAULT 'transfer', memo varchar(255), amount_paid numeric(15, 2) NOT NULL DEFAULT 0, created_by_id bigint, journal_entry_id bigint, created_at timestamp with time zone NOT NULL, updated_at timestamp with time zone NOT NULL, FOREIGN KEY(vendor_id) REFERENCES _vendors(id) ON DELETE RESTRICT, FOREIGN KEY(cash_account_id) REFERENCES accounting_accounts(id) ON DELETE RESTRICT, FOREIGN KEY(created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL, FOREIGN KEY(journal_entry_id) REFERENCES accounting_journal_entries(id) ON DELETE SET NULL); CREATE INDEX IF NOT EXISTS accounting_payment_vouchers_number ON accounting_payment_vouchers(number); CREATE INDEX IF NOT EXISTS accounting_payment_vouchers_date ON accounting_payment_vouchers(date);",
            "DROP TABLE IF EXISTS accounting_payment_vouchers CASCADE;"
        ),

        # Create accounting_payment_voucher_allocations table
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS accounting_payment_voucher_allocations (id bigserial PRIMARY KEY, voucher_id bigint NOT NULL, payable_entry_id bigint NOT NULL, amount numeric(15, 2) NOT NULL, FOREIGN KEY(voucher_id) REFERENCES accounting_payment_vouchers(id) ON DELETE CASCADE, FOREIGN KEY(payable_entry_id) REFERENCES accounting_accounts_payable(id) ON DELETE RESTRICT); CREATE INDEX IF NOT EXISTS accounting_payment_voucher_allocations_voucher_id ON accounting_payment_voucher_allocations(voucher_id);",
            "DROP TABLE IF EXISTS accounting_payment_voucher_allocations CASCADE;"
        ),
    ]
